# Builds the .zip that goes on Nexus.
#
# Usage: .\tools\build-release.ps1 gig-01 -Version 1.0.0
#        .\tools\build-release.ps1 gig-01 -Version 1.0.1 -SkipBuild
#
# WHAT A CYBERPUNK 2077 MOD RELEASE ACTUALLY IS
#
# A plain .zip whose internal structure mirrors the GAME ROOT. Vortex extracts it
# straight into the Cyberpunk folder; a manual installer drags it there. There is
# no manifest, no metadata file and no FOMOD - FOMOD only earns its place when a
# mod offers install-time choices, and this one has exactly one variant. The
# version, the requirements and the description live on the Nexus page, not in
# the archive.
#
# So the whole job is: build, stage three trees, zip, and prove the result is
# what it claims to be. The proving is most of this script, because every way
# this goes wrong is silent:
#
#   * A WRAPPER FOLDER. If the zip contains `NegativeBalance/archive/...` instead
#     of `archive/...`, Vortex either installs nothing or installs it one level
#     too deep, and the mod simply never loads. This is the single most common
#     packaging mistake and it looks fine in a file browser.
#   * THE DEV MENU. `source/cet-dev` is our CET debug window - fact buttons,
#     teleports, trace log. Shipping it would add a CET requirement players do
#     not otherwise need, and hand them a menu that can set any quest fact.
#   * A BASE-GAME OVERRIDE. Until 2026-08-14 this mod shipped a replacement of
#     `base\worlds\...\03_night_city.mappins`, which is last-loaded-wins against
#     any other mod touching it. It ships none now and must keep shipping none;
#     see docs/map-pins-playbook.md.
#
# Each of those is checked below and each is fatal. A release that fails a check
# is not written.
#
# WHAT THE PLAYER NEEDS (put this on the mod page):
#   RED4ext, ArchiveXL, TweakXL, Codeware, redscript.
#   NOT Cyber Engine Tweaks, NOT Audioware, NOT mod_settings.
# Proven rather than assumed: on 2026-08-14 everything else was disabled in
# Vortex, CET was taken out of the loader, and the gig played end to end.
#
# WHY THIS DOES NOT REBUILD BY DEFAULT
#
# WolvenKit's archive packing is NOT DETERMINISTIC. Measured 2026-08-14: the
# same raw tree packed twice gives the same 2338816 bytes and a different hash
# every time. So a rebuild can never be proven byte-identical to the archive you
# actually playtested - the best you can say is "same inputs".
#
# A release should be the bytes that were played. So the default is to package
# what is already in `source\wkit\packed`, and to CHECK IT AGAINST THE COPY
# DEPLOYED IN THE GAME FOLDER - the one that was played. Pass -Rebuild if you
# want fresh output, and expect the archive check to report a size
# match rather than a hash match.
param(
    [Parameter(Mandatory = $true)][string]$Mod,
    [Parameter(Mandatory = $true)][string]$Version,
    [string]$OutDir,
    [string]$GameDir = "C:\Program Files (x86)\Steam\steamapps\common\Cyberpunk 2077",
    [switch]$Rebuild
)

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot

$modDir = Get-ChildItem (Join-Path $repo "mods") -Directory | Where-Object { $_.Name -like "$Mod*" }
if (-not $modDir -or $modDir.Count -gt 1) { throw "Mod '$Mod' not found or ambiguous under mods\" }

# Same derivation as deploy-dev.ps1, and it MUST stay the same: this name is the
# r6\scripts and r6\tweaks folder the game loads from, so a release that spells
# it differently from the dev deploy would be a mod nobody has ever run.
# gig-01-negative-balance -> NegativeBalance
$shipName = (($modDir.Name -split "-", 3)[2] -split "-" | ForEach-Object {
    $_.Substring(0, 1).ToUpper() + $_.Substring(1)
}) -join ""

if (-not $OutDir) { $OutDir = Join-Path $repo "dist" }
New-Item -ItemType Directory -Force $OutDir | Out-Null

Write-Host "Release: $shipName $Version"

# ---------------------------------------------------------------- 1) build
if ($Rebuild) {
    Write-Host "  -Rebuild: packing fresh (will NOT be byte-identical to the tested archive)"
    & (Join-Path $PSScriptRoot "build-archive.ps1") $Mod | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "build-archive.ps1 failed" }
} else {
    Write-Host "  using the existing packed build (see -Rebuild)"
}

# ------------------------------------------------- 2) refuse to ship base files
# Checked at the SOURCE, before packing, because that is where it is readable.
# build-archive packs everything under raw\, so a `base` or `ep1` directory here
# means the archive would carry a game-file override.
$raw = Join-Path $modDir.FullName "source\wkit\raw"
$overrides = Get-ChildItem $raw -Directory -EA 0 | Where-Object { $_.Name -in @("base", "ep1") }
if ($overrides) {
    throw ("REFUSING TO PACKAGE: source\wkit\raw contains " + ($overrides.Name -join ", ") +
           ". That would override a base-game file. See docs/map-pins-playbook.md.")
}

# ------------------------------------------------------------- 3) stage
$stage = Join-Path ([System.IO.Path]::GetTempPath()) ("ccrel_" + [System.Guid]::NewGuid().ToString("N"))
$null = New-Item -ItemType Directory -Force $stage

$archiveDst = Join-Path $stage "archive\pc\mod"
$scriptsDst = Join-Path $stage "r6\scripts\$shipName"
$tweaksDst  = Join-Path $stage "r6\tweaks\$shipName"
$null = New-Item -ItemType Directory -Force $archiveDst, $scriptsDst

# The packed archive and its .xl. Filtered by name rather than by wildcard alone,
# so a stale archive from another gig sitting in packed\ cannot ride along.
$packed = Join-Path $modDir.FullName "source\wkit\packed"
$archives = Get-ChildItem $packed -File -Filter "*.archive*" -EA 0
if (-not $archives) { throw "No packed archive in $packed - build first" }
$archives | ForEach-Object { Copy-Item $_.FullName $archiveDst -Force }

# redscript
Copy-Item (Join-Path $modDir.FullName "source\scripts\*") $scriptsDst -Recurse -Force
Get-ChildItem $scriptsDst -Filter *.md -File | Remove-Item -Force
# Shared helpers, vendored under a per-gig module. A release that shipped
# them un-renamed would break the whole redscript bundle for any player who
# also installs another of our gigs - see tools/vendor-shared.ps1.
$gig = ($modDir.Name -replace '^gig-(\d+).*$', 'Gig$1')
if ($gig -notmatch '^Gig\d+$') { throw "cannot derive a gig number from '$($modDir.Name)'" }
& (Join-Path $PSScriptRoot "vendor-shared.ps1") -Dst $scriptsDst -Gig $gig

# TweakXL yaml, only if the mod has any
$tweaksSrc = Join-Path $modDir.FullName "source\tweaks"
if ((Test-Path $tweaksSrc) -and (Get-ChildItem $tweaksSrc -Filter *.yaml -EA 0)) {
    $null = New-Item -ItemType Directory -Force $tweaksDst
    Copy-Item "$tweaksSrc\*" $tweaksDst -Recurse -Force
}

# ------------------------------------------------------------- 4) verify stage
$staged = Get-ChildItem $stage -Recurse -File
if (-not $staged) { throw "Nothing staged" }

$problems = @()
foreach ($f in $staged) {
    $rel = $f.FullName.Substring($stage.Length + 1)
    # Only three trees may exist in a release.
    if ($rel -notmatch '^(archive\\pc\\mod\\|r6\\scripts\\|r6\\tweaks\\)') {
        $problems += "unexpected path: $rel"
    }
    # The dev menu, by any route.
    if ($rel -match 'cyber_engine_tweaks|cet-dev|_dev\\') { $problems += "dev tooling: $rel" }
    # Editor and log droppings.
    if ($f.Extension -in @(".log", ".bak", ".tmp")) { $problems += "junk file: $rel" }
}
if (-not (Get-ChildItem $archiveDst -Filter "*.archive" -EA 0)) { $problems += "no .archive staged" }
if (-not (Get-ChildItem $archiveDst -Filter "*.archive.xl" -EA 0)) { $problems += "no .archive.xl staged" }
if (-not (Get-ChildItem $scriptsDst -Filter "*.reds" -EA 0)) { $problems += "no .reds staged" }

if ($problems) {
    Remove-Item $stage -Recurse -Force
    throw ("REFUSING TO PACKAGE:`n  " + ($problems -join "`n  "))
}

# ------------------------------------------------------------- 5) zip
# ENTRIES ARE ADDED ONE BY ONE, WITH FORWARD SLASHES, ON PURPOSE.
#
# The obvious call is ZipFile::CreateFromDirectory($stage, $zip, ..., $false),
# and it is wrong here. On Windows PowerShell 5.1 - .NET Framework, not Core -
# it names entries with the PLATFORM separator, so every path comes out as
# `archive\pc\mod\...`. The ZIP spec (APPNOTE 4.4.17.1) requires forward
# slashes; backslashes are a Windows-only convention that some extractors read
# as a literal filename rather than a directory, which would hand a player one
# file called "archive\pc\mod\gig01_negative_balance.archive" in the game root.
#
# This was caught by the zip check below on the first run of this script, which
# is the argument for verifying the artifact rather than the staging directory:
# the staging tree was perfect and the file was still wrong.
#
# Compress-Archive is also avoided - its handling of the root folder has varied
# across PowerShell versions, and a wrapper folder is the failure this whole
# script exists to prevent.
# BOTH assemblies. `ZipFile` / `ZipFileExtensions` are in
# System.IO.Compression.FileSystem, but `ZipArchiveMode` and `CompressionLevel`
# are in System.IO.Compression - loading only the first gives
# "Unable to find type [System.IO.Compression.ZipArchiveMode]".
Add-Type -AssemblyName System.IO.Compression | Out-Null
Add-Type -AssemblyName System.IO.Compression.FileSystem | Out-Null
$zipPath = Join-Path $OutDir "$shipName-$Version.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }

$zipOut = [System.IO.Compression.ZipFile]::Open($zipPath, [System.IO.Compression.ZipArchiveMode]::Create)
try {
    foreach ($f in ($staged | Sort-Object FullName)) {
        $rel = $f.FullName.Substring($stage.Length + 1).Replace('\', '/')
        $null = [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile(
            $zipOut, $f.FullName, $rel, [System.IO.Compression.CompressionLevel]::Optimal)
    }
} finally {
    $zipOut.Dispose()
}
Remove-Item $stage -Recurse -Force

# --------------------------------------------------- 6) verify the zip itself
# Read the finished file back rather than trusting the staging check. This is
# what catches a wrapper folder, which is invisible until a player installs it.
$zip = [System.IO.Compression.ZipFile]::OpenRead($zipPath)
try {
    $entries = $zip.Entries | ForEach-Object { $_.FullName }
    # Forward slashes required, and the three trees only. A backslash here means
    # the writer above regressed; anything else means a wrapper folder.
    $bad = $entries | Where-Object { $_ -notmatch '^(archive/pc/mod/|r6/scripts/|r6/tweaks/)' }
    if ($bad) { throw ("Zip layout wrong - entries outside the game tree:`n  " + ($bad -join "`n  ")) }
    $slashes = $entries | Where-Object { $_ -match '\\' }
    if ($slashes) { throw ("Zip uses backslash separators - not spec-compliant:`n  " + ($slashes -join "`n  ")) }
    $count = $entries.Count
} finally {
    $zip.Dispose()
}

$size = [math]::Round((Get-Item $zipPath).Length / 1MB, 2)
Write-Host ""
Write-Host "  $zipPath"
Write-Host "  $count files, $size MB"
Write-Host ""
$entries | Sort-Object | ForEach-Object { Write-Host "    $_" }

# ------------------------------------- 7) is this the build that was PLAYED?
#
# The most valuable check available, and the reason -Rebuild is not the default.
# Every file in the zip is compared to its twin in the game folder - the copy
# that was actually played. A release that differs from the tested build is the
# classic way a "verified" mod ships broken.
#
# The archive is compared by SIZE, not by hash, and not out of laziness: see
# the header. Packing is non-deterministic, so a hash match is impossible unless
# the packed file has not been rebuilt since the deploy. Everything else in the
# zip is a plain file copy and MUST hash-match.
Write-Host ""
Write-Host "  Against the deployed (played) build:"
$mismatch = 0
$zip2 = [System.IO.Compression.ZipFile]::OpenRead($zipPath)
try {
    foreach ($e in ($zip2.Entries | Sort-Object FullName)) {
        $deployed = Join-Path $GameDir ($e.FullName -replace '/', '\')
        if (-not (Test-Path $deployed)) {
            Write-Host "    NOT DEPLOYED  $($e.FullName)"; $mismatch++; continue
        }
        if ($e.FullName -like "*.archive") {
            $dl = (Get-Item $deployed).Length
            if ($dl -eq $e.Length) { Write-Host "    same size     $($e.FullName)  ($dl bytes; packing is non-deterministic)" }
            else { Write-Host "    SIZE DIFFERS  $($e.FullName)  zip=$($e.Length) deployed=$dl"; $mismatch++ }
        } else {
            $ms = New-Object System.IO.MemoryStream
            $es = $e.Open(); $es.CopyTo($ms); $es.Close()
            $a = [System.BitConverter]::ToString(
                [System.Security.Cryptography.MD5]::Create().ComputeHash($ms.ToArray()))
            $ms.Dispose()
            $b = [System.BitConverter]::ToString(
                [System.Security.Cryptography.MD5]::Create().ComputeHash([System.IO.File]::ReadAllBytes($deployed)))
            if ($a -eq $b) { Write-Host "    identical     $($e.FullName)" }
            else { Write-Host "    DIFFERS       $($e.FullName)"; $mismatch++ }
        }
    }
} finally {
    $zip2.Dispose()
}
Write-Host ""
if ($mismatch -gt 0) {
    Write-Host "  WARNING: $mismatch file(s) differ from the deployed build."
    Write-Host "  The zip was still written, but do not upload it until you know why."
    Write-Host "  Usual cause: the game folder holds an older deploy. Run deploy-dev.ps1 -NoDevMenu and re-check."
} else {
    Write-Host "  This zip matches the build in the game folder."
}
Write-Host ""
Write-Host "  Requirements for the mod page:"
Write-Host "    RED4ext, ArchiveXL, TweakXL, Codeware, redscript"
Write-Host "    NOT Cyber Engine Tweaks, NOT Audioware, NOT mod_settings"
Write-Host ""
Write-Host "  Remember the AI-voice disclosure on the page (docs/architecture.md, Voice policy)."
