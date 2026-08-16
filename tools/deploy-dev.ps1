# Deploys a gig's current sources into the game folder for testing.
# Usage: .\tools\deploy-dev.ps1 gig-01   (accepts any unique prefix of the mod folder name)
#        .\tools\deploy-dev.ps1 gig-01 -NoDevMenu   (deploy exactly what a player gets)
#
# -NoDevMenu deploys the three things a RELEASE contains - archive, redscript,
# tweaks - and skips the CET dev menu. It also DELETES an already-deployed dev
# menu, which is the point: without that, a plain re-deploy silently puts the
# menu back and a "clean user" test stops being one. Found the hard way on
# 2026-08-14, when playtesting removed the CET mods by hand to test as a new user and
# the next deploy would have reinstalled ours.
#
# The mod itself has NO CET dependency to break - see the note by that block
# below - so this flag changes what is on disk, not how the gig behaves.
param(
    [Parameter(Mandatory = $true)][string]$Mod,
    [string]$GameDir = "C:\Program Files (x86)\Steam\steamapps\common\Cyberpunk 2077",
    [switch]$NoDevMenu
)

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
$modDir = Get-ChildItem (Join-Path $repo "mods") -Directory | Where-Object { $_.Name -like "$Mod*" }
if (-not $modDir -or $modDir.Count -gt 1) { throw "Mod '$Mod' not found or ambiguous under mods\" }

# Ship name: gig-01-negative-balance -> NegativeBalance
$shipName = (($modDir.Name -split "-", 3)[2] -split "-" | ForEach-Object {
    $_.Substring(0, 1).ToUpper() + $_.Substring(1)
}) -join ""

Write-Host "Deploying $($modDir.Name) as '$shipName' -> $GameDir"

# redscript
$src = Join-Path $modDir.FullName "source\scripts"
if (Test-Path $src) {
    $dst = Join-Path $GameDir "r6\scripts\$shipName"
    Remove-Item $dst -Recurse -Force -ErrorAction SilentlyContinue
    Copy-Item $src $dst -Recurse
    Get-ChildItem $dst -Filter *.md -File | Remove-Item -Force
    # Shared helpers, vendored under a per-gig module so two of our gigs can be
    # installed together. See tools/vendor-shared.ps1 for why that is mandatory.
    $gig = ($modDir.Name -replace '^gig-(\d+).*$', 'Gig$1')
    if ($gig -notmatch '^Gig\d+$') { throw "cannot derive a gig number from '$($modDir.Name)'" }
    & (Join-Path $PSScriptRoot "vendor-shared.ps1") -Dst $dst -Gig $gig
    Write-Host "  scripts -> r6\scripts\$shipName"
}

# TweakXL yaml
$src = Join-Path $modDir.FullName "source\tweaks"
if ((Test-Path $src) -and (Get-ChildItem $src -Filter *.yaml -ErrorAction SilentlyContinue)) {
    $dst = Join-Path $GameDir "r6\tweaks\$shipName"
    Remove-Item $dst -Recurse -Force -ErrorAction SilentlyContinue
    Copy-Item $src $dst -Recurse
    Write-Host "  tweaks  -> r6\tweaks\$shipName"
}

# CET dev tools (dev-only, excluded from releases).
#
# NOTHING THE MOD SHIPS DEPENDS ON THIS, by construction rather than
# by care: CET is a separate Lua VM that redscript cannot call into at all. The
# only coupling runs the other way - the menu writes quest facts that the mod
# reads - and an unset fact reads as 0, which is every gate's "no" and every
# bisect switch's "behave normally". Audited fact by fact on 2026-08-14: of the
# 40 facts the shipped scripts read, the only one no quest phase or script of
# ours ever writes is `cc_g01_no_scene`, whose 0 is the normal path.
#
# So removing CET cannot break the gig. It costs the fact buttons, the
# teleports, FULL PIN DIAGNOSIS and call_trace.log - diagnosis, not gameplay.
$src = Join-Path $modDir.FullName "source\cet-dev"
$cetName = ($shipName -creplace "([a-z])([A-Z])", '$1_$2').ToLower() + "_dev"
$cetDst = Join-Path $GameDir "bin\x64\plugins\cyber_engine_tweaks\mods\$cetName"
if ($NoDevMenu) {
    if (Test-Path $cetDst) {
        Remove-Item $cetDst -Recurse -Force
        Write-Host "  cet-dev <- REMOVED $cetName (release layout)"
    } else {
        Write-Host "  cet-dev    skipped (release layout)"
    }
} elseif (Test-Path $src) {
    New-Item -ItemType Directory -Force $cetDst | Out-Null
    Copy-Item "$src\*" $cetDst -Recurse -Force
    Write-Host "  cet-dev -> bin\x64\...\cyber_engine_tweaks\mods\$cetName"
}

# Packed archive (built via WolvenKit GUI into source\wkit\packed for now)
$src = Join-Path $modDir.FullName "source\wkit\packed"
if (Test-Path $src) {
    Get-ChildItem $src -Filter "*.archive*" | ForEach-Object {
        Copy-Item $_.FullName (Join-Path $GameDir "archive\pc\mod") -Force
        Write-Host "  archive -> archive\pc\mod\$($_.Name)"
    }
}

Write-Host "Done. Launch the game and check red4ext\logs for [CC.Gig01]."
