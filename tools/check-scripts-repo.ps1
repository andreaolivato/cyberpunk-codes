# Compile the REPO's redscript without deploying anything to the game.
#
# check-scripts.ps1 compiles the DEPLOYED tree and refuses to run when the repo
# differs from it, which is the right guard for "have I tested what I am about
# to play". It is the wrong tool for "is this refactor even valid", because it
# forces you to deploy over a working install first to find out.
#
# This assembles the same temp tree, but takes the mod's scripts from the REPO
# and runs the vendoring step on the way in, so what gets compiled is exactly
# what a deploy WOULD produce. Nothing under the game folder is written.
#
# Usage:  .\tools\check-scripts-repo.ps1 gig-01
param([Parameter(Mandatory = $true)][string]$Mod)

$ErrorActionPreference = "Stop"
$game = "C:\Program Files (x86)\Steam\steamapps\common\Cyberpunk 2077"
$repo = Split-Path -Parent $PSScriptRoot
$root = Join-Path $env:TEMP "cc-repocheck"
$scripts = Join-Path $root "r6\scripts"

$modDir = Get-ChildItem (Join-Path $repo "mods") -Directory |
          Where-Object { $_.Name -like "$Mod*" } | Select-Object -First 1
if (-not $modDir) { Write-Host "no mod matching '$Mod'" -ForegroundColor Red; exit 1 }

Remove-Item $root -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force $scripts | Out-Null
New-Item -ItemType Directory -Force (Join-Path $root "r6\cache") | Out-Null

# The vanilla scripts, plus every plugin's registered scripts. Miss the second
# and you get bogus "unresolved type 'DynamicEntitySpec'" errors.
Copy-Item "$game\r6\scripts\*" $scripts -Recurse -Force
foreach ($plugin in Get-ChildItem "$game\red4ext\plugins" -Directory) {
    $dest = Join-Path $scripts "_$($plugin.Name)"
    $ps = Join-Path $plugin.FullName "Scripts"
    if (Test-Path $ps) { Copy-Item $ps $dest -Recurse -Force }
    $loose = Get-ChildItem $plugin.FullName -Filter *.reds -File -ErrorAction SilentlyContinue
    if ($loose) {
        New-Item -ItemType Directory -Force $dest | Out-Null
        $loose | ForEach-Object { Copy-Item $_.FullName $dest -Force }
    }
}
Copy-Item "$game\r6\cache\final.redscripts" (Join-Path $root "r6\cache\final.redscripts") -Force

# Replace the deployed copy of THIS mod with the repo's, then vendor.
# The deploy folder is the SHIP name, not the mod folder name
# (gig-01-negative-balance -> NegativeBalance), and copying the repo in beside
# an already-deployed copy makes the mod collide with itself.
$shipName = (($modDir.Name -split "-", 3)[2] -split "-" | ForEach-Object {
    $_.Substring(0, 1).ToUpper() + $_.Substring(1)
}) -join ""
$dst = Join-Path $scripts $shipName
Remove-Item $dst -Recurse -Force -ErrorAction SilentlyContinue
Copy-Item (Join-Path $modDir.FullName "source\scripts") $dst -Recurse -Force
Get-ChildItem $dst -Filter *.md -File | Remove-Item -Force
# Derive the gig number from the MOD FOLDER (gig-01-...), not the ship name -
# the ship name has no number in it, so matching against it silently yields
# Gig01 for every gig and hands two mods the same module.
$gig = ($modDir.Name -replace '^gig-(\d+).*$', 'Gig$1')
if ($gig -notmatch '^Gig\d+$') { throw "cannot derive a gig number from '$($modDir.Name)'" }
& (Join-Path $PSScriptRoot "vendor-shared.ps1") -Dst $dst -Gig $gig

$output = & "$game\engine\tools\scc.exe" -compile $scripts 2>&1
$exit = $LASTEXITCODE
$compiled = $output | Select-String -Pattern "Compiling files in" -Quiet
if (-not $compiled) {
    Write-Host "COMPILE CHECK DID NOT RUN - scc compiled nothing (exit $exit)." -ForegroundColor Red
    $output | Select-Object -Last 20
    exit 1
}
$errors = $output | Select-String -Pattern "\[ERROR" -Context 0, 4
if ($exit -ne 0 -or $errors) {
    Write-Host "COMPILE ERRORS (exit $exit):" -ForegroundColor Red
    if ($errors) { $errors | ForEach-Object { $_.Line; $_.Context.PostContext } }
    else { $output | Select-Object -Last 20 }
    exit 1
}
$warnings = $output | Select-String -Pattern "\[WARN" -Context 0, 4
if ($warnings) {
    Write-Host "Warnings:" -ForegroundColor Yellow
    $warnings | ForEach-Object { $_.Line; $_.Context.PostContext }
}
Write-Host "Repo scripts compile cleanly (vendored as CyberpunkCodes.Shared.$gig)." -ForegroundColor Green
