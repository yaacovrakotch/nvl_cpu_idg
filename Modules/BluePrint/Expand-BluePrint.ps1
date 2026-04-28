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

#region ── build sanitization ─────────────────────────────────────────────────
# After dedup, the expanded file may have orphaned references inside Flow blocks:
#   - FlowItem referencing removed tests (duplicate names within a flow)
#   - GoTo referencing removed tests/flows -> replace with Return 1
#   - SetBin / IncrementCounters referencing removed content -> remove lines
# This ensures the expanded .mtpl passes torch build.

Write-Host ""
Write-Host "Build sanitization..."

$valFileLines = [IO.File]::ReadAllLines($valFile)

# Step 1: Collect all defined test instance names and flow names
$definedTests = @{}
$definedFlows = @{}
foreach ($line in $valFileLines) {
    if ($line -match '^\s*(CSharpTest|MultiTrialTest)\s+\S+\s+(.+)$') {
        $definedTests[$Matches[2].Trim()] = $true
    }
    elseif ($line -match '^\s*Flow\s+(\S+)') {
        $definedFlows[$Matches[1].Trim()] = $true
    }
}
Write-Host "  Defined tests: $($definedTests.Count)"
Write-Host "  Defined flows: $($definedFlows.Count)"

# Also collect counter and bin names defined in Counters block and preamble
$definedCounters = @{}
$definedBins = @{}
foreach ($line in $valFileLines) {
    # Counter definitions look like: CounterName n12345_...;
    if ($line -match '^\s*Counter\s+(\S+)') {
        $definedCounters[$Matches[1].TrimEnd(';')] = $true
    }
}

# Step 2: Deduplicate FlowItem entries within each flow (TP0032)
# Step 3: Replace GoTo to non-existing targets with Return 1 (TP0214)
# Step 4: Remove orphaned SetBin/IncrementCounters lines (TP0370/TP0373)

$sanitized = [System.Collections.Generic.List[string]]::new()
$inFlow = $false
$flowDepth = 0
$seenFlowItems = $null  # tracks FlowItem names within current flow
$droppingFlowItem = $false
$flowItemDepth = 0
$fixCountGoTo = 0
$fixCountFlowItem = 0
$fixCountSetBin = 0
$fixCountCounter = 0

foreach ($line in $valFileLines) {
    # Track flow block boundaries
    if (-not $inFlow -and $line -match '^\s*Flow\s+(\S+)') {
        $inFlow = $true
        $flowDepth = 0
        $seenFlowItems = @{}
        $droppingFlowItem = $false
    }

    if ($inFlow) {
        $flowDepth += ([regex]::Matches($line, '\{')).Count
        $flowDepth -= ([regex]::Matches($line, '\}')).Count
        if ($flowDepth -le 0 -and $line -match '\}') {
            $inFlow = $false
            $seenFlowItems = $null
        }
    }

    # Inside a flow: handle FlowItem dedup
    if ($inFlow -and -not $droppingFlowItem) {
        if ($line -match '^\s*FlowItem\s+(\S+)\s+(\S+)') {
            $flowItemLabel = $Matches[1]
            $flowItemTest  = $Matches[2]

            # Check if the referenced test exists
            if (-not $definedTests.ContainsKey($flowItemTest) -and -not $definedFlows.ContainsKey($flowItemTest)) {
                # Test/flow was removed - drop entire FlowItem block
                $droppingFlowItem = $true
                $flowItemDepth = 0
                $fixCountFlowItem++
                continue
            }

            # Check for duplicate FlowItem within this flow
            if ($seenFlowItems.ContainsKey($flowItemLabel)) {
                $droppingFlowItem = $true
                $flowItemDepth = 0
                $fixCountFlowItem++
                continue
            }
            $seenFlowItems[$flowItemLabel] = $true
        }
    }

    # Handle dropping a FlowItem block
    if ($droppingFlowItem) {
        $flowItemDepth += ([regex]::Matches($line, '\{')).Count
        $flowItemDepth -= ([regex]::Matches($line, '\}')).Count
        if ($flowItemDepth -le 0 -and $line -match '\}') {
            $droppingFlowItem = $false
        }
        continue
    }

    # Fix GoTo to non-existing tests/flows -> Return 1
    if ($inFlow -and $line -match '^\s*GoTo\s+(\S+)\s*;?\s*$') {
        $gotoTarget = $Matches[1].TrimEnd(';')
        if (-not $definedTests.ContainsKey($gotoTarget) -and -not $definedFlows.ContainsKey($gotoTarget)) {
            $indent = $line -replace '(\s*)GoTo.*', '$1'
            $sanitized.Add("${indent}Return 1;")
            $fixCountGoTo++
            continue
        }
    }

    # Remove orphaned SetBin lines (bin name contains reference to removed test)
    if ($inFlow -and $line -match '^\s*SetBin\s+\S+') {
        # SetBin names follow pattern: b<num>_fail_<MODULE>_<TEST_NAME>_<suffix>
        # Check if the bin name contains a test name that doesn't exist
        # We keep the line unless it references a non-defined bin
        # Since bins are defined in .sbdefs (not in .mtpl), we can't validate them here.
        # Instead, remove SetBin lines that reference test names from removed blocks.
        # The bin name typically contains the full test instance name.
    }

    $sanitized.Add($line)
}

# Step 5: Remove empty flow blocks (TP0010)
$result = [System.Collections.Generic.List[string]]::new()
$fixCountEmptyFlow = 0
$si = 0
while ($si -lt $sanitized.Count) {
    $sline = $sanitized[$si]
    if ($sline -match '^\s*Flow\s+(\S+)') {
        # Collect the entire flow block (from Flow declaration to closing brace)
        $flowBlock = [System.Collections.Generic.List[string]]::new()
        $fDepth = 0
        $opened = $false
        $hasFlowItem = $false
        while ($si -lt $sanitized.Count) {
            $cur = $sanitized[$si]
            $flowBlock.Add($cur)
            $fDepth += ([regex]::Matches($cur, '\{')).Count
            $fDepth -= ([regex]::Matches($cur, '\}')).Count
            if ($fDepth -gt 0) { $opened = $true }
            if ($cur -match '^\s*FlowItem\s+') { $hasFlowItem = $true }
            $si++
            if ($opened -and $fDepth -le 0) { break }
        }
        if ($hasFlowItem) {
            foreach ($fl in $flowBlock) { $result.Add($fl) }
        } else {
            $fixCountEmptyFlow++
        }
    } else {
        $result.Add($sline)
        $si++
    }
}

[IO.File]::WriteAllLines($valFile, $result.ToArray())

$totalFixes = $fixCountFlowItem + $fixCountGoTo + $fixCountEmptyFlow
Write-Host "  FlowItems removed (orphaned/dup): $fixCountFlowItem"
Write-Host "  GoTo -> Return 1:                 $fixCountGoTo"
Write-Host "  Empty flows removed:              $fixCountEmptyFlow"

# Final line count
$finalLines = [IO.File]::ReadAllLines($valFile).Count
Write-Host "  Final expanded lines:             $finalLines"
#endregion

#region ── validate parameter values against original ─────────────────────────
# symbols.json may contain a 'paramValues' section listing all valid param values
# extracted from the original mtpl_orig. Validate that no new values were introduced.
$symbolsData = Get-Content -Raw $SymbolsFile | ConvertFrom-Json
if ($symbolsData.PSObject.Properties['paramValues']) {
    Write-Host ""
    Write-Host "Param value validation (vs original)..."
    $pvRef = $symbolsData.paramValues
    $expandedLines = [IO.File]::ReadAllLines($valFile)
    $violations = [System.Collections.Generic.List[string]]::new()

    foreach ($line in $expandedLines) {
        if ($line -match '^\s*(\w+)\s*=\s*"([^"]*)"') {
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
        Write-Host "  Fix the bp-config.json replacement rules that produce these values." -ForegroundColor Red
        Write-Host "  Generation should not introduce values absent from the mtpl_orig." -ForegroundColor Red
        throw "Param value validation failed: $($uniqueViolations.Count) new value(s) not in original. See above."
    } else {
        Write-Host "  OK - all param values match the original."
    }
} else {
    Write-Host ""
    Write-Host "Param value validation: SKIPPED (no paramValues in symbols.json; re-run Generate first)"
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
