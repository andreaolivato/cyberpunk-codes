# Copy shared\scripts into one mod's script folder, under a PER-GIG module name.
#
# WHY THE RENAME IS MANDATORY, tested against scc on 2026-08-16 rather than
# assumed:
#
#   two files, SAME module, same class name       -> [SYM_REDEFINITION]
#   two files, DIFFERENT module, same class name  -> compiles clean
#
# and a SYM_REDEFINITION breaks more than our gig: redscript compiles the
# whole bundle, so it takes down every redscript mod the player has installed.
# Two of our gigs shipping an un-renamed shared file would do that.
#
# Class names therefore need no per-gig prefix. Only the `module` line in the
# shared files, and the matching `import` in the gig's own scripts, are touched.
#
# Usage:  .\tools\vendor-shared.ps1 -Dst <script folder> -Gig Gig01
param(
    [Parameter(Mandatory = $true)][string]$Dst,
    [Parameter(Mandatory = $true)][string]$Gig
)

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
$shared = Join-Path $repo "shared\scripts"

if (-not (Test-Path $shared)) { return }
$files = Get-ChildItem $shared -Filter *.reds -File
if (-not $files) { return }

New-Item -ItemType Directory -Force $Dst | Out-Null
# BOM-less UTF-8: redscript rejects a BOM with "syntax error, expected one of
# @, EOF, a top-level definition" on line 1, and Set-Content -Encoding utf8
# writes one on Windows PowerShell 5.1.
$enc = New-Object System.Text.UTF8Encoding($false)

foreach ($f in $files) {
    $text = [System.IO.File]::ReadAllText($f.FullName)
    $text = $text -replace '(?m)^module CyberpunkCodes\.Shared$', "module CyberpunkCodes.Shared.$Gig"
    [System.IO.File]::WriteAllText((Join-Path $Dst $f.Name), $text, $enc)
}

# ...and point the gig's own scripts at the renamed module.
foreach ($f in Get-ChildItem $Dst -Filter *.reds -File) {
    if ($f.Name -like "CCShared_*") { continue }
    $text = [System.IO.File]::ReadAllText($f.FullName)
    if ($text -match '(?m)^import CyberpunkCodes\.Shared\.\*$') {
        $text = $text -replace '(?m)^import CyberpunkCodes\.Shared\.\*$', "import CyberpunkCodes.Shared.$Gig.*"
        [System.IO.File]::WriteAllText($f.FullName, $text, $enc)
    }
}

Write-Host "  vendored $($files.Count) shared script(s) as CyberpunkCodes.Shared.$Gig"
