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
#
# THIS SCRIPT DOES NOT BUILD THE ARCHIVE. It copies whatever build-archive.ps1
# last produced. Run that FIRST whenever any resource under source\wkit\raw has
# changed, or the game gets last build's quest graph, scenes and journal with
# this build's redscript, which looks exactly like a change that did not work.
# There is a guard below, and it exists because that happened on 2026-08-23:
# a whole playthrough was spent testing the previous build.
param(
    [Parameter(Mandatory = $true)][string]$Mod,
    [string]$GameDir = "C:\Program Files (x86)\Steam\steamapps\common\Cyberpunk 2077",
    [switch]$NoDevMenu,
    [switch]$AllowStaleArchive
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

# STALENESS GUARD, and it is the same guard build-archive.ps1 puts on audio,
# for the same reason: a build that is silently one revision behind cannot be
# detected downstream, and every symptom points at the change under test.
#
# 2026-08-23: gen_questphase.py, gen_scenes.py and the rest were re-run, this
# script was run without build-archive.ps1 first, and it faithfully copied an
# archive an hour old. The redscript WAS current, so the game ran new script
# against an old quest graph and both of the beats being tested took their old
# path. The report was "nothing we did was applied at all", which was correct.
#
# IT COMPARES CONTENT, NOT TIMESTAMPS, and the difference is the whole value.
# The first version compared mtimes and cried wolf within the hour: an audit
# re-ran every generator, every output was byte-identical, and 22 files came
# back "newer than the archive". A guard that is wrong when you are busy gets
# bypassed with a flag, and then it is not a guard. build-archive.ps1 writes
# raw.sha256 next to the archive; this recomputes it.
$packedDir = Join-Path $modDir.FullName "source\wkit\packed"
$rawDir = Join-Path $modDir.FullName "source\wkit\raw"
$packedArchive = Get-ChildItem $packedDir -Filter "*.archive" -File -ErrorAction SilentlyContinue |
    Select-Object -First 1
if ($packedArchive -and (Test-Path $rawDir)) {
    $manifest = Get-ChildItem $rawDir -Recurse -File | Sort-Object FullName | ForEach-Object {
        $rel = $_.FullName.Substring($rawDir.Length).TrimStart([char]92)
        "$rel $((Get-FileHash $_.FullName -Algorithm SHA256).Hash)"
    }
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $bytes = [System.Text.Encoding]::UTF8.GetBytes(($manifest -join "`n"))
    $now = ($sha.ComputeHash($bytes) | ForEach-Object { $_.ToString('x2') }) -join ''
    $stampFile = Join-Path $packedDir 'raw.sha256'
    $stale = $false
    $why = ''
    if (Test-Path $stampFile) {
        $was = (Get-Content $stampFile -Raw).Trim()
        if ($was -ne $now) {
            $stale = $true
            $why = "the resources under source\wkit\raw have CHANGED since it was packed"
        }
    } else {
        # No stamp: an archive from before this guard existed. Fall back to the
        # old timestamp test rather than passing silently, and say which it is.
        $newer = Get-ChildItem $rawDir -Recurse -File |
            Where-Object { $_.LastWriteTime -gt $packedArchive.LastWriteTime }
        if ($newer) {
            $stale = $true
            $why = ("no raw.sha256 beside the archive, and {0} file(s) are NEWER than it. " -f $newer.Count) +
                   "That may only be a re-run; rebuild once to get a content stamp and this stops guessing"
        }
    }
    if ($stale) {
        $msg = "STALE ARCHIVE: $why.`n`n" +
               "Run  .\tools\build-archive.ps1 $Mod  first, then deploy again.`n" +
               "-AllowStaleArchive deploys anyway, and you will be testing the old build."
        if ($AllowStaleArchive) { Write-Warning $msg } else { throw $msg }
    }
}

# Packed archive (built via WolvenKit GUI into source\wkit\packed for now)
$src = $packedDir
if (Test-Path $src) {
    Get-ChildItem $src -Filter "*.archive*" | ForEach-Object {
        Copy-Item $_.FullName (Join-Path $GameDir "archive\pc\mod") -Force
        Write-Host "  archive -> archive\pc\mod\$($_.Name)"
    }
}

Write-Host "Done. Launch the game and check red4ext\logs for [CC.Gig01]."
