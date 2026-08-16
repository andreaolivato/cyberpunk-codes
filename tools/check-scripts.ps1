# Offline redscript compile check - catches script errors without launching the game.
#
# Keep this file pure ASCII: Windows PowerShell 5.1 reads a BOM-less .ps1 as
# Windows-1252, so a UTF-8 em dash turns into a stray double quote and the
# script stops parsing.
#
# RED4ext compiles r6\scripts PLUS the script folders its plugins register
# (Codeware's especially). A plain compile of r6\scripts therefore reports bogus
# "unresolved type 'DynamicEntitySpec'" errors. This script assembles a temp tree
# with everything, including the vanilla script cache scc needs.
#
# IMPORTANT - the invocation is fussy (this cost us a broken bundle once):
# scc derives the game root by walking UP from the scripts directory it is given
# and expects the <root>\r6\scripts + <root>\r6\cache\final.redscripts layout.
# Handed a path that is not shaped like that, it silently compiles NOTHING,
# prints "Compilation complete" and exits 0. The previous version of this script
# passed a flat temp dir plus an explicit cache path and so always passed - even
# on files that were not valid redscript at all. Verified 2026-08-11:
#   scc -compile <flat dir> <cache>   -> "Compilation complete", exit 0, no-op
#   scc -compile <nonexistent dir>    -> "Compilation complete", exit 0, no-op
#   scc -compile <root>\r6\scripts    -> really compiles, exit 1 on error
# If you change this, re-run the self-test: .\tools\check-scripts.ps1 -SelfTest
#
# Usage: .\tools\check-scripts.ps1 [-SelfTest]

param([switch]$SelfTest)

$ErrorActionPreference = "Stop"
$game = "C:\Program Files (x86)\Steam\steamapps\common\Cyberpunk 2077"
$root = Join-Path $env:TEMP "cc-scriptcheck"
$scripts = Join-Path $root "r6\scripts"

# STALENESS GUARD - this checker compiles the DEPLOYED scripts in the game
# folder, not the repo. Run it before deploy-dev.ps1 and it faithfully compiles
# the PREVIOUS version and reports success, which is worse than useless: it is a
# green light on code you have not tested. That happened on 2026-08-12 and the
# game caught the syntax error the checker had just passed.
#
# So: compare every .reds in the repo against its deployed twin, and refuse to
# run if they differ. Correct order is always deploy, THEN check.
if (-not $SelfTest) {
    $repo = Split-Path -Parent $PSScriptRoot
    $stale = @()
    foreach ($src in Get-ChildItem (Join-Path $repo "mods") -Recurse -Filter *.reds -File) {
        if ($src.FullName -like "*\scripts-disabled\*") { continue }
        $dst = Get-ChildItem "$game\r6\scripts" -Recurse -Filter $src.Name -File -ErrorAction SilentlyContinue |
               Select-Object -First 1
        if (-not $dst) {
            $stale += "$($src.Name) - not deployed at all"
        } else {
            # A deployed gig script is legitimately NOT byte-equal to its source:
            # deploy-dev vendors the shared helpers under a per-gig module and
            # rewrites the matching import line (tools\vendor-shared.ps1). Apply
            # the same rewrite before comparing, or this guard calls every script
            # stale the moment a gig uses shared code - which is a refusal to run
            # the compile check at all, i.e. exactly the blind spot it exists to
            # close.
            $gig = "Gig01"
            if ($src.FullName -match "\\mods\\gig-(\d+)-") { $gig = "Gig$($Matches[1])" }
            $want = [System.IO.File]::ReadAllText($src.FullName) -replace
                    "(?m)^import CyberpunkCodes\.Shared\.\*$", "import CyberpunkCodes.Shared.$gig.*"
            $have = [System.IO.File]::ReadAllText($dst.FullName)
            if ($want -ne $have) {
                $stale += "$($src.Name) - deployed copy differs from source"
            }
        }
    }
    if ($stale) {
        Write-Host "REFUSING TO RUN - the deployed scripts are not what is in the repo:" -ForegroundColor Red
        $stale | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
        Write-Host "This checker compiles the DEPLOYED tree, so it would be checking stale code." -ForegroundColor Red
        Write-Host "Run .\tools\deploy-dev.ps1 <mod> first, then re-run this." -ForegroundColor Yellow
        exit 1
    }
}

Remove-Item $root -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force $scripts | Out-Null
New-Item -ItemType Directory -Force (Join-Path $root "r6\cache") | Out-Null

Copy-Item "$game\r6\scripts\*" $scripts -Recurse -Force
# Plugins register scripts two different ways: most use a Scripts subfolder
# (ArchiveXL, Codeware, TweakXL), but mod_settings drops packed.reds/module.reds
# straight in its plugin folder. Miss the second kind and every mod that depends
# on it fails with bogus "unresolved reference 'ModSettings'" errors.
foreach ($plugin in Get-ChildItem "$game\red4ext\plugins" -Directory) {
    $dest = Join-Path $scripts "_$($plugin.Name)"
    $pluginScripts = Join-Path $plugin.FullName "Scripts"
    if (Test-Path $pluginScripts) {
        Copy-Item $pluginScripts $dest -Recurse -Force
    }
    $loose = Get-ChildItem $plugin.FullName -Filter *.reds -File -ErrorAction SilentlyContinue
    if ($loose) {
        New-Item -ItemType Directory -Force $dest | Out-Null
        $loose | ForEach-Object { Copy-Item $_.FullName $dest -Force }
    }
}
Copy-Item "$game\r6\cache\final.redscripts" (Join-Path $root "r6\cache\final.redscripts") -Force

if ($SelfTest) {
    # Prove the checker can still fail: plant a file that cannot compile.
    Set-Content (Join-Path $scripts "_ccSelfTest.reds") "this is not valid redscript @@@" -Encoding utf8
}

$output = & "$game\engine\tools\scc.exe" -compile $scripts 2>&1
$exit = $LASTEXITCODE

# scc only lists the source files it compiled when it really ran. No list means
# it no-opped, which must never be reported as success.
$compiled = $output | Select-String -Pattern "Compiling files in" -Quiet

if ($SelfTest) {
    if ($exit -ne 0) {
        Write-Host "Self-test OK: the checker detects broken scripts." -ForegroundColor Green
        exit 0
    }
    Write-Host "SELF-TEST FAILED: broken scripts were reported as clean." -ForegroundColor Red
    exit 1
}

if (-not $compiled) {
    Write-Host "COMPILE CHECK DID NOT RUN - scc compiled nothing (exit $exit)." -ForegroundColor Red
    Write-Host "The temp tree layout is probably wrong; see the notes at the top." -ForegroundColor Red
    $output | Select-Object -Last 25
    exit 1
}

$errors = $output | Select-String -Pattern "\[ERROR" -Context 0, 4

if ($exit -ne 0 -or $errors) {
    Write-Host "COMPILE ERRORS (exit $exit):" -ForegroundColor Red
    if ($errors) { $errors | ForEach-Object { $_.Line; $_.Context.PostContext } }
    else { $output | Select-Object -Last 25 }
    exit 1
}

$warnings = $output | Select-String -Pattern "\[WARN" -Context 0, 4
if ($warnings) {
    Write-Host "Warnings:" -ForegroundColor Yellow
    $warnings | ForEach-Object { $_.Line; $_.Context.PostContext }
}

Write-Host "Scripts compile cleanly." -ForegroundColor Green
