<#
.SYNOPSIS
    Expands a BluePrint (.mtpl.bp) by replacing symbols with per-block combo values.

.DESCRIPTION
    Reads a .mtpl.bp file and its corresponding symbols.json.  Each test block
    in the BP has a # BP_COMBO annotation specifying the symbol values for that
    specific instance.  The expander uses those per-block values to replace
    symbol placeholders, producing a valid .mtpl file with ALL original tests
    and flows preserved.

    Flow blocks are kept verbatim (they were not symbolized during generation
    because they reference items across multiple symbol combinations).

    Also handles derived symbol variants:
      - Lowercase: \freq_corner\ -> lowercase of chosen value (e.g. "f1")
      - _NUM suffix: \MODULE_INDEX_NUM\ -> numeric part of value (e.g. M0 -> 0)

    Outputs:
      1. <module>.mtpl.bp.val  in the BluePrint directory
      2. <module>.mtpl         overwritten with the expanded content

.PARAMETER InputBp
    Path to the .mtpl.bp file.

.PARAMETER SymbolsFile
    Path to symbols.json. Defaults to symbols.json next to the BP file.

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

#region â”€â”€ paths â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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

#region â”€â”€ load symbols â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$config  = Get-Content -Raw $SymbolsFile | ConvertFrom-Json
$symbols = $config.symbols

# Collect symbol names for replacement map building
$symbolNames = [System.Collections.Generic.List[string]]::new()
foreach ($prop in $symbols.PSObject.Properties) {
    $symbolNames.Add($prop.Name)
}

Write-Host ""
Write-Host "Symbols: $($symbolNames -join ', ')"
#endregion

#region â”€â”€ build per-block replacement map function â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function Build-ReplacementMap {
    param([hashtable]$Combo, [System.Collections.Generic.List[string]]$AllSymbolNames)
    $map = [System.Collections.Generic.List[System.Collections.Generic.KeyValuePair[string,string]]]::new()
    foreach ($name in $AllSymbolNames) {
        if (-not $Combo.ContainsKey($name)) { continue }
        $val = $Combo[$name]
        # Uppercase symbol: \FREQ_CORNER\ -> F1
        $map.Add([System.Collections.Generic.KeyValuePair[string,string]]::new('\' + $name + '\', $val))
        # Lowercase symbol: \freq_corner\ -> f1
        $lower = $name.ToLower()
        $map.Add([System.Collections.Generic.KeyValuePair[string,string]]::new('\' + $lower + '\', $val.ToLower()))
        # _NUM variant: \MODULE_INDEX_NUM\ -> extract digits from value (M0 -> 0)
        $numMatch = [regex]::Match($val, '\d+')
        if ($numMatch.Success) {
            $map.Add([System.Collections.Generic.KeyValuePair[string,string]]::new('\' + $name + '_NUM\', $numMatch.Value))
            $map.Add([System.Collections.Generic.KeyValuePair[string,string]]::new('\' + $lower + '_num\', $numMatch.Value))
        }
    }
    return $map
}

function Apply-ReplacementMap {
    param([string]$Text, $Map)
    $r = $Text
    foreach ($kv in $Map) { $r = $r.Replace($kv.Key, $kv.Value) }
    return $r
}
#endregion

#region â”€â”€ expand BP per-block â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$bpLines = [IO.File]::ReadAllLines($InputBp)
$output  = [System.Collections.Generic.List[string]]::new()

$currentCombo = $null
$testCount  = 0
$flowCount  = 0
$comboCount = 0

$i = 0
while ($i -lt $bpLines.Count) {
    $line = $bpLines[$i]

    # Check for BP_COMBO annotation
    if ($line -match '^# BP_COMBO:\s*(.+)$') {
        $comboStr = $Matches[1].Trim()
        $combo = @{}
        foreach ($part in ($comboStr -split ',\s*')) {
            $kv = $part -split '=', 2
            if ($kv.Count -eq 2) { $combo[$kv[0].Trim()] = $kv[1].Trim() }
        }
        $currentCombo = $combo
        $comboCount++
        # Don't emit the BP_COMBO comment to the output
        $i++
        continue
    }

    # Check for test block start
    if ($line -match '^\s*(CSharpTest|MultiTrialTest)\s+') {
        # Collect the entire test block
        $blockLines = [System.Collections.Generic.List[string]]::new()
        $depth = 0; $opened = $false
        while ($i -lt $bpLines.Count) {
            $blockLines.Add($bpLines[$i])
            $depth += ([regex]::Matches($bpLines[$i], '\{')).Count
            $depth -= ([regex]::Matches($bpLines[$i], '\}')).Count
            if ($depth -gt 0) { $opened = $true }
            $i++
            if ($opened -and $depth -le 0) { break }
        }

        $blockText = $blockLines -join "`n"

        # If we have a combo, apply per-block replacement
        if ($currentCombo -and $currentCombo.Count -gt 0) {
            $map = Build-ReplacementMap -Combo $currentCombo -AllSymbolNames $symbolNames
            $blockText = Apply-ReplacementMap -Text $blockText -Map $map
        }

        # Check for remaining unresolved symbols in this block
        $remaining = [regex]::Matches($blockText, '\\[A-Za-z_]+\\')
        if ($remaining.Count -gt 0) {
            $unresolved = ($remaining | ForEach-Object { $_.Value } | Sort-Object -Unique) -join ', '
            Write-Warning "Unresolved symbols in test block: $unresolved"
        }

        foreach ($bl in ($blockText -split "`n")) {
            $output.Add($bl)
        }
        $currentCombo = $null
        $testCount++
        continue
    }

    # Check for flow block (kept verbatim)
    if ($line -match '^\s*Flow\s+') {
        $depth = 0; $opened = $false
        while ($i -lt $bpLines.Count) {
            $output.Add($bpLines[$i])
            $depth += ([regex]::Matches($bpLines[$i], '\{')).Count
            $depth -= ([regex]::Matches($bpLines[$i], '\}')).Count
            if ($depth -gt 0) { $opened = $true }
            $i++
            if ($opened -and $depth -le 0) { break }
        }
        $flowCount++
        continue
    }

    # All other lines (preamble, comments, blank lines) pass through
    # Skip group/instance comments from old format
    if ($line -match '^# ==== (GROUP|FLOW GROUP)') { $i++; continue }
    if ($line -match '^# (Instances|Flows):') { $i++; continue }

    $output.Add($line)
    $i++
}

# Write .bp.val
[IO.File]::WriteAllLines($valFile, $output.ToArray())
Write-Host ""
Write-Host "Written: $valFile ($($output.Count) lines)"
Write-Host "  Test blocks:  $testCount"
Write-Host "  Flow blocks:  $flowCount"
Write-Host "  Combos used:  $comboCount"
#endregion

#region â”€â”€ validate parameter values against original â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
$symbolsData = Get-Content -Raw $SymbolsFile | ConvertFrom-Json
if ($symbolsData.PSObject.Properties['paramValues']) {
    Write-Host ""
    Write-Host "Param value validation (vs original)..."
    $pvRef = $symbolsData.paramValues
    $expandedLines = [IO.File]::ReadAllLines($valFile)
    $violations = [System.Collections.Generic.List[string]]::new()

    foreach ($eline in $expandedLines) {
        if ($eline -match '^\s*(\w+)\s*=\s*"([^"]*)"') {
            $pName = $Matches[1]
            $pVal  = $Matches[2]
            if ($pvRef.PSObject.Properties[$pName]) {
                $allowed = @($pvRef.$pName)
                if ($pVal -notin $allowed) {
                    $violations.Add("  $pName = `"$pVal`"")
                }
            }
        }
    }

    if ($violations.Count -gt 0) {
        $uniqueViolations = $violations | Sort-Object -Unique
        Write-Host "  VIOLATIONS: $($uniqueViolations.Count) param values not found in original:" -ForegroundColor Red
        foreach ($v in $uniqueViolations) { Write-Host $v -ForegroundColor Red }
        throw "Param value validation failed: $($uniqueViolations.Count) new value(s) not in original."
    } else {
        Write-Host "  OK - all param values match the original."
    }
} else {
    Write-Host ""
    Write-Host "Param value validation: SKIPPED (no paramValues in symbols.json; re-run Generate first)"
}
#endregion

#region â”€â”€ replace module .mtpl â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
Copy-Item -Path $valFile -Destination $origMtpl -Force
Write-Host "Updated: $origMtpl"
#endregion

#region â”€â”€ copy to sibling modules (copyTargets) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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
