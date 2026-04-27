<#
.SYNOPSIS
    Expands a BluePrint (.mtpl.bp) by replacing symbols with one concrete value.

.DESCRIPTION
    Reads a .mtpl.bp file and its corresponding symbols.json, replaces every
    \SYMBOL\ placeholder with the first (or specified) value from each symbol's
    value list, producing a valid .mtpl file.

    Also handles derived symbol variants:
      - Lowercase: \freq_corner\ -> lowercase of chosen value (e.g. "f1")
      - _NUM suffix: \MODULE_INDEX_NUM\ -> numeric part of value (e.g. M0 -> 0)

    Outputs:
      1. <module>.mtpl.bp.val  in the BluePrint directory
      2. <module>.mtpl_orig    backup of the original .mtpl (in module directory)
      3. <module>.mtpl         overwritten with the .bp.val content

.PARAMETER InputBp
    Path to the .mtpl.bp file.

.PARAMETER SymbolsFile
    Path to symbols.json. Defaults to symbols.json next to the BP file.

.PARAMETER ValueIndex
    Zero-based index into each symbol's values array. Default 0 (first value).

.EXAMPLE
    .\Expand-BluePrint.ps1 -InputBp "..\ARR\ARR_ATOM_CXX\BluePrint\ARR_ATOM_CXX.mtpl.bp"
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$InputBp,

    [string]$SymbolsFile,

    [int]$ValueIndex = 0
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

#region ── paths ──────────────────────────────────────────────────────────────
$InputBp = (Resolve-Path $InputBp).Path
$bpDir   = Split-Path $InputBp

if (-not $SymbolsFile) {
    $SymbolsFile = Join-Path $bpDir 'symbols.json'
}
$SymbolsFile = (Resolve-Path $SymbolsFile).Path

# Derive module name: ARR_ATOM_CXX.mtpl.bp -> ARR_ATOM_CXX
$bpFileName = [IO.Path]::GetFileName($InputBp)
if ($bpFileName -notmatch '^(.+)\.mtpl\.bp$') {
    throw "Input file must end with .mtpl.bp, got: $bpFileName"
}
$moduleName = $Matches[1]

# Module directory is parent of BluePrint/
$moduleDir = Split-Path $bpDir

$valFile   = Join-Path $bpDir "$moduleName.mtpl.bp.val"
$origMtpl  = Join-Path $moduleDir "$moduleName.mtpl"
$backupMtpl = Join-Path $moduleDir "$moduleName.mtpl_orig"

Write-Host "=== BluePrint Expander ==="
Write-Host "Module    : $moduleName"
Write-Host "Input BP  : $InputBp"
Write-Host "Symbols   : $SymbolsFile"
Write-Host "Value idx : $ValueIndex"
Write-Host "Output val: $valFile"
Write-Host "Backup    : $backupMtpl"
#endregion

#region ── load symbols ───────────────────────────────────────────────────────
$config  = Get-Content -Raw $SymbolsFile | ConvertFrom-Json
$symbols = $config.symbols

# Build replacement map: symbol placeholder -> concrete value (case-sensitive!)
$replacements = [System.Collections.Generic.List[System.Collections.Generic.KeyValuePair[string,string]]]::new()

foreach ($prop in $symbols.PSObject.Properties) {
    $name   = $prop.Name
    $values = @($prop.Value.values)

    # Clean parenthetical notes from values: "M0 (no suffix)" -> "M0"
    $cleanValues = $values | ForEach-Object { ($_ -replace '\s*\(.*\)', '').Trim() }

    $idx = [math]::Min($ValueIndex, $cleanValues.Count - 1)
    $chosenValue = $cleanValues[$idx]

    # Uppercase symbol: \FREQ_CORNER\ -> F1
    $replacements.Add([System.Collections.Generic.KeyValuePair[string,string]]::new('\' + $name + '\', $chosenValue))

    # Lowercase symbol: \freq_corner\ -> f1
    $lowerName = $name.ToLower()
    $replacements.Add([System.Collections.Generic.KeyValuePair[string,string]]::new('\' + $lowerName + '\', $chosenValue.ToLower()))

    # _NUM variant: \MODULE_INDEX_NUM\ -> extract digits from value (M0 -> 0)
    $numMatch = [regex]::Match($chosenValue, '\d+')
    if ($numMatch.Success) {
        $replacements.Add([System.Collections.Generic.KeyValuePair[string,string]]::new('\' + $name + '_NUM\', $numMatch.Value))
        $replacements.Add([System.Collections.Generic.KeyValuePair[string,string]]::new('\' + $lowerName + '_num\', $numMatch.Value))
    }
}

Write-Host ""
Write-Host "Symbol replacements:"
foreach ($r in $replacements) {
    Write-Host "  $($r.Key) -> $($r.Value)"
}
#endregion

#region ── expand BP ──────────────────────────────────────────────────────────
$content = [IO.File]::ReadAllText($InputBp)

foreach ($r in $replacements) {
    $content = $content.Replace($r.Key, $r.Value)
}

# Check for any remaining unresolved symbols
$remaining = [regex]::Matches($content, '\\[A-Za-z_]+\\')
if ($remaining.Count -gt 0) {
    $unresolved = ($remaining | ForEach-Object { $_.Value } | Sort-Object -Unique) -join ', '
    Write-Warning "Unresolved symbols remaining: $unresolved"
}

# Write .bp.val
[IO.File]::WriteAllText($valFile, $content)
$valLines = [IO.File]::ReadAllLines($valFile).Count
Write-Host ""
Write-Host "Written: $valFile ($valLines lines)"
#endregion

#region ── backup & replace original .mtpl ────────────────────────────────────
if (Test-Path $origMtpl) {
    Copy-Item -Path $origMtpl -Destination $backupMtpl -Force
    Write-Host "Backup:  $backupMtpl"
} else {
    Write-Warning "Original .mtpl not found at $origMtpl - skipping backup"
}

Copy-Item -Path $valFile -Destination $origMtpl -Force
Write-Host "Updated: $origMtpl"
#endregion

Write-Host ""
Write-Host "=== Done ==="
