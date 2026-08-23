# Builds a gig's .archive from JSON-authored resources in source\wkit\raw.
# Usage: .\tools\build-archive.ps1 gig-01
param(
    [Parameter(Mandatory = $true)][string]$Mod,
    [string]$Cli = "$env:LOCALAPPDATA\Programs\WolvenKit.CLI\WolvenKit.CLI.exe"
)

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
$modDir = Get-ChildItem (Join-Path $repo "mods") -Directory | Where-Object { $_.Name -like "$Mod*" }
if (-not $modDir -or $modDir.Count -gt 1) { throw "Mod '$Mod' not found or ambiguous under mods\" }

$raw = Join-Path $modDir.FullName "source\wkit\raw"
$packed = Join-Path $modDir.FullName "source\wkit\packed"
$archiveName = ((Get-ChildItem $raw -Filter "*.archive.xl" | Select-Object -First 1).Name) -replace "\.archive\.xl$", ""
if (-not $archiveName) { throw "No .archive.xl found in $raw (needed to derive archive name)" }

# 0) STALENESS GUARD, before any work is done.
#    gen_voice.py failed once - it could not read the 32-bit float WAVs torchaudio
#    writes - and this script carried straight on and packed the PREVIOUS run's
#    audio. The result was a mod that had just been "successfully built" and
#    contained the wrong voices, which nothing downstream can detect. So: if any
#    source .wav is newer than its .wem, the .wem was not regenerated.
#    Find the .wem by NAME anywhere under the raw tree, rather than at a fixed
#    path. This used to hardcode mod\negative_balance\audio\vo, which is gig 01's
#    folder, so a second gig with its own audio folder saw every .wem as missing
#    and could never build. The rest of this script derives everything from the
#    mod argument; this one line did not.
$audioSrc = Join-Path $modDir.FullName "source\audio"
if (Test-Path $audioSrc) {
    $wems = @{}
    foreach ($w in Get-ChildItem $raw -Recurse -Filter *.wem -File) { $wems[$w.BaseName] = $w }
    $stale = @()
    foreach ($wav in Get-ChildItem $audioSrc -Filter *.wav -File) {
        $wem = $wems[$wav.BaseName]
        if (-not $wem) { $stale += "$($wav.Name) -> no .wem at all"; continue }
        if ($wem.LastWriteTime -lt $wav.LastWriteTime) {
            $stale += "$($wav.Name) is newer than its .wem"
        }
    }
    if ($stale.Count -gt 0) {
        throw ("Audio is stale - run tools\gig01\gen_voice.py first:`n  " + ($stale -join "`n  "))
    }
}

# Staging dir named after the archive; CLI pack uses the folder name.
$staging = Join-Path $env:TEMP "cc-build\$archiveName"
Remove-Item (Split-Path $staging) -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force $staging | Out-Null

# 1) Convert every *.json authored resource (files named <resource>.json where
#    <resource> has its own extension, e.g. gig01.journal.json -> gig01.journal)
$jsonSources = Get-ChildItem $raw -Recurse -Filter "*.json" | Where-Object { $_.Name -match "\.[a-z0-9]+\.json$" -and $_.Name -notmatch "\.archive\.xl$" }
foreach ($src in $jsonSources) {
    & $Cli convert deserialize $src.FullName | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "convert deserialize failed for $($src.Name)" }
    $resource = $src.FullName -replace "\.json$", ""
    if (-not (Test-Path $resource)) { throw "expected output missing: $resource" }
    # Mirror path relative to raw\ into staging
    $rel = $resource.Substring($raw.Length + 1)
    $dst = Join-Path $staging $rel
    New-Item -ItemType Directory -Force (Split-Path $dst) | Out-Null
    Move-Item $resource $dst -Force
    Write-Host "  built $rel"
}

# 1b) Copy through resources that are ALREADY compiled binaries and have no JSON
#     form. Only .wem so far (Wwise audio, written by tools\gig01\gen_voice.py) - a
#     whitelist rather than "everything that is not .json", so a stray file in
#     raw\ can never end up shipped by accident.
$binaryExts = @(".wem")
$binaries = Get-ChildItem $raw -Recurse -File | Where-Object { $binaryExts -contains $_.Extension.ToLower() }
foreach ($src in $binaries) {
    $rel = $src.FullName.Substring($raw.Length + 1)
    $dst = Join-Path $staging $rel
    New-Item -ItemType Directory -Force (Split-Path $dst) | Out-Null
    Copy-Item $src.FullName $dst -Force
    Write-Host "  copied $rel"
}

# 2) Pack staging into .archive
New-Item -ItemType Directory -Force $packed | Out-Null
& $Cli pack $staging -o $packed
if ($LASTEXITCODE -ne 0) { throw "pack failed" }

# 3) Copy the .archive.xl next to the packed archive
Copy-Item (Join-Path $raw "$archiveName.archive.xl") $packed -Force

# 4) Record WHAT went in, so deploy-dev can tell a stale archive from a
#    re-run of a generator that produced the same bytes.
#
#    The first version of that guard compared TIMESTAMPS and cried wolf the
#    first time it mattered: an audit pass re-ran every generator, every output
#    was byte-identical, and 22 files came back "newer than the archive". A
#    guard that is wrong when you are busy is a guard that gets bypassed with
#    a flag, and then it is not a guard.
$manifest = Get-ChildItem $raw -Recurse -File | Sort-Object FullName | ForEach-Object {
    $rel = $_.FullName.Substring($raw.Length).TrimStart([char]92)
    "$rel $((Get-FileHash $_.FullName -Algorithm SHA256).Hash)"
}
$sha = [System.Security.Cryptography.SHA256]::Create()
$bytes = [System.Text.Encoding]::UTF8.GetBytes(($manifest -join "`n"))
$digest = ($sha.ComputeHash($bytes) | ForEach-Object { $_.ToString('x2') }) -join ''
Set-Content -Path (Join-Path $packed 'raw.sha256') -Value $digest -Encoding ascii

Get-ChildItem $packed | ForEach-Object { Write-Host "  packed: $($_.Name) ($([math]::Round($_.Length/1KB,1)) KB)" }
Write-Host "Build complete. Deploy with tools\deploy-dev.ps1 $Mod"
