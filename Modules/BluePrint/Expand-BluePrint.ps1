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

    [string]$SymbolsFile
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

Write-Host "=== BluePrint Expander ==="
Write-Host "Module    : $moduleName"
Write-Host "Input BP  : $InputBp"
Write-Host "Symbols   : $SymbolsFile"
Write-Host "Output val: $valFile"
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

    # Always use the first value from the symbol's values list
    $chosenValue = $cleanValues[0]

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

# Auto-fix duplicate test instances (keep first occurrence, drop later ones)
$valFileLines = [IO.File]::ReadAllLines($valFile)
$testNames = $valFileLines | ForEach-Object { if ($_ -match '^\s*(CSharpTest|MultiTrialTest)\s+\S+\s+(.+)$') { $Matches[2].Trim() } } | Where-Object { $_ }
$dups = $testNames | Group-Object | Where-Object { $_.Count -gt 1 }
if ($dups) {
    Write-Host "Auto-fixing $($dups.Count) duplicate test name(s) (keeping first occurrence)..."
    $dupNameSet = @{}
    foreach ($d in $dups) { $dupNameSet[$d.Name] = $true }

    $seenTests = @{}
    $cleanLines = [System.Collections.Generic.List[string]]::new()
    $dropping = $false
    $droppedCount = 0

    foreach ($line in $valFileLines) {
        if ($line -match '^\s*(CSharpTest|MultiTrialTest)\s+\S+\s+(.+)$') {
            $name = $Matches[2].Trim()
            if ($dupNameSet.ContainsKey($name) -and $seenTests.ContainsKey($name)) {
                $dropping = $true
                $droppedCount++
                Write-Host "  Dropped duplicate: $name"
                continue
            }
            $seenTests[$name] = $true
            $dropping = $false
        } elseif ($dropping) {
            # Inside a duplicate block being dropped
            if ($line -match '^\}') { $dropping = $false }
            continue
        }
        $cleanLines.Add($line)
    }
    [IO.File]::WriteAllLines($valFile, $cleanLines.ToArray())
    Write-Host "  Removed $droppedCount duplicate test block(s)."
    $valFileLines = [IO.File]::ReadAllLines($valFile)
}

# Auto-fix duplicate flow names (keep first occurrence, drop later ones)
$flowNames = $valFileLines | ForEach-Object { if ($_ -match '^\s*Flow\s+(\S+)') { $Matches[1].Trim() } } | Where-Object { $_ }
$flowDups = $flowNames | Group-Object | Where-Object { $_.Count -gt 1 }
if ($flowDups) {
    Write-Host "Auto-fixing $($flowDups.Count) duplicate flow name(s) (keeping first occurrence)..."
    $dupFlowSet = @{}
    foreach ($d in $flowDups) { $dupFlowSet[$d.Name] = $true }

    $seenFlows = @{}
    $cleanLines = [System.Collections.Generic.List[string]]::new()
    $dropping = $false
    $depth = 0
    $droppedCount = 0

    foreach ($line in $valFileLines) {
        if (-not $dropping -and $line -match '^\s*Flow\s+(\S+)') {
            $name = $Matches[1].Trim()
            if ($dupFlowSet.ContainsKey($name) -and $seenFlows.ContainsKey($name)) {
                $dropping = $true
                $depth = 0
                $droppedCount++
                Write-Host "  Dropped duplicate flow: $name"
            }
            $seenFlows[$name] = $true
        }
        if ($dropping) {
            $depth += ([regex]::Matches($line, '\{')).Count
            $depth -= ([regex]::Matches($line, '\}')).Count
            if ($depth -le 0 -and $line -match '\}') { $dropping = $false }
            continue
        }
        $cleanLines.Add($line)
    }
    [IO.File]::WriteAllLines($valFile, $cleanLines.ToArray())
    Write-Host "  Removed $droppedCount duplicate flow block(s)."
}
#endregion

#region ── replace original .mtpl ────────────────────────────────────────
Copy-Item -Path $valFile -Destination $origMtpl -Force
Write-Host "Updated: $origMtpl"
#endregion

#region ── copy to sibling modules (copyTargets) ─────────────────────────────
$bpConfigFile = Join-Path $bpDir 'bp-config.json'
if (Test-Path $bpConfigFile) {
    $bpConfig = Get-Content -Raw $bpConfigFile | ConvertFrom-Json
    if ($bpConfig.PSObject.Properties['copyTargets'] -and $bpConfig.copyTargets.Count -gt 0) {
        $arrDir = Split-Path $moduleDir   # parent folder containing sibling modules
        foreach ($target in $bpConfig.copyTargets) {
            $targetMtpl = Join-Path (Join-Path $arrDir $target) "$target.mtpl"
            if (Test-Path (Split-Path $targetMtpl)) {
                Copy-Item -Path $valFile -Destination $targetMtpl -Force
                Write-Host "Copied:  $targetMtpl (copyTarget)"
            } else {
                Write-Warning "copyTarget directory not found: $(Split-Path $targetMtpl) - skipping $target"
            }
        }
    }
}
#endregion

Write-Host ""
Write-Host "=== Done ==="
