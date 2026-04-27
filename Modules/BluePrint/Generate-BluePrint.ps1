<#
.SYNOPSIS
    Generic MTPL-to-BluePrint transformer. Module-agnostic.

.DESCRIPTION
    Transforms any NVL .mtpl file into a BluePrint (BP) + companion prompt,
    using a per-module configuration file (bp-config.json) that defines:
      - symbols:        name, description, values, replacement pairs
      - normalization:  regex patterns applied before dedup comparison
      - notes:          module-specific notes appended to the prompt file

    Algorithm:
      1. Restore _orig.mtpl as the generation baseline (or create it on first run).
      2. Parse the .mtpl into preamble (header + Counters), test blocks, and flow blocks.
      3. Apply symbol replacements (literal find/replace from config).
      4. Normalise blocks (BaseNumbers, SetBin, IncrementCounters + config-defined patterns) for dedup.
      5. Group identical normalised blocks; keep one representative per group.
      6. Emit BluePrint (.mtpl.bp) and companion prompt (.prompt.txt).
      7. Report duplicate test/flow names that indicate incomplete symbolization.

.PARAMETER InputMtpl
    Path to the source .mtpl file.

.PARAMETER ConfigFile
    Path to the bp-config.json for this module.

.PARAMETER OutputDir
    Directory for output files.  Defaults to .\BluePrint next to the input.

.EXAMPLE
    .\Generate-BluePrint.ps1 -InputMtpl "..\ARR\ARR_ATOM_CXX\ARR_ATOM_CXX.mtpl" `
                              -ConfigFile "..\ARR\ARR_ATOM_CXX\BluePrint\bp-config.json"
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$InputMtpl,

    [Parameter(Mandatory)]
    [string]$ConfigFile,

    [string]$OutputDir
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

#region ── paths ──────────────────────────────────────────────────────────────
$InputMtpl  = (Resolve-Path $InputMtpl).Path
$ConfigFile = (Resolve-Path $ConfigFile).Path
$moduleName = [IO.Path]::GetFileNameWithoutExtension($InputMtpl)

if (-not $OutputDir) { $OutputDir = Join-Path (Split-Path $InputMtpl) 'BluePrint' }
if (-not (Test-Path $OutputDir)) { New-Item -ItemType Directory $OutputDir -Force | Out-Null }

$bpFile     = Join-Path $OutputDir "$moduleName.mtpl.bp"
$promptFile = Join-Path $OutputDir "$moduleName.prompt.txt"

Write-Host "=== MTPL BluePrint Generator ==="
Write-Host "Module : $moduleName"
Write-Host "Input  : $InputMtpl"
Write-Host "Config : $ConfigFile"
Write-Host "Output : $OutputDir"
#endregion

#region ── restore original mtpl ──────────────────────────────────────────────
$moduleDir = Split-Path $InputMtpl
$origMtpl  = Join-Path $moduleDir "${moduleName}_orig.mtpl"
if (Test-Path $origMtpl) {
    Copy-Item -Path $origMtpl -Destination $InputMtpl -Force
    Write-Host "Restored: $InputMtpl from $origMtpl"
} else {
    # First run: current .mtpl is the original — save it as the baseline
    Copy-Item -Path $InputMtpl -Destination $origMtpl -Force
    Write-Host "First run: saved $origMtpl from current .mtpl"
}
#endregion

#region ── load config ────────────────────────────────────────────────────────
$config = Get-Content -Raw $ConfigFile | ConvertFrom-Json

# Build ordered symbol definitions and flat replacement list from config
$symbolDefs      = [ordered]@{}
$allReplacements = @()

foreach ($sym in $config.symbols) {
    $symbolDefs[$sym.name] = @{
        Description = $sym.description
        Values      = @($sym.values)
    }
    foreach ($pair in $sym.replacements) {
        $allReplacements += @{ Find = $pair.find; Replace = $pair.replace }
    }
}

# Load normalization patterns from config (or use defaults)
$normPatterns = @()
if ($config.PSObject.Properties['normalization']) {
    foreach ($np in $config.normalization) {
        $normPatterns += @{ Pattern = $np.pattern; Replacement = $np.replacement }
    }
}

# Load notes from config (or use defaults)
$moduleNotes = @()
if ($config.PSObject.Properties['notes']) {
    $moduleNotes = @($config.notes)
}

Write-Host "  Symbols:      $($symbolDefs.Count)"
Write-Host "  Replacements: $($allReplacements.Count)"
Write-Host "  Norm rules:   $($normPatterns.Count)"
#endregion

#region ── read file ──────────────────────────────────────────────────────────
$rawLines = [IO.File]::ReadAllLines($InputMtpl)
Write-Host "  Lines:        $($rawLines.Count)"
#endregion

#region ── parse blocks ───────────────────────────────────────────────────────
function Find-EndOfCounters {
    param([string[]]$Lines)
    for ($i = 0; $i -lt $Lines.Count; $i++) {
        if ($Lines[$i] -match '^\}\s*#\s*End of Test Counter Definition') {
            return $i
        }
    }
    for ($i = 0; $i -lt $Lines.Count; $i++) {
        if ($Lines[$i] -match '^\s*(CSharpTest|MultiTrialTest)\s+') {
            return $i - 1
        }
    }
    return 0
}

$countersEnd   = Find-EndOfCounters -Lines $rawLines
$preambleLines = $rawLines[0..$countersEnd]
Write-Host "  Preamble:     lines 0..$countersEnd"

$testBlocks = [System.Collections.Generic.List[PSCustomObject]]::new()

$i = $countersEnd + 1
while ($i -lt $rawLines.Count) {
    $line = $rawLines[$i]

    if ($line -match '^\s*(CSharpTest|MultiTrialTest)\s+(\S+)\s+(.+)$') {
        $testType     = $Matches[1]
        $templateName = $Matches[2]
        $instanceName = $Matches[3].Trim()

        # collect preceding comment lines
        $commentLines = [System.Collections.Generic.List[string]]::new()
        $k = $i - 1
        while ($k -gt $countersEnd -and $rawLines[$k] -match '^\s*(#|$)') {
            if ($rawLines[$k].Trim()) { $commentLines.Insert(0, $rawLines[$k]) }
            $k--
        }

        # collect block lines (header through matching close-brace)
        $depth  = 0
        $opened = $false
        $blockLines = [System.Collections.Generic.List[string]]::new()
        foreach ($cl in $commentLines) { $blockLines.Add($cl) }
        $j = $i
        while ($j -lt $rawLines.Count) {
            $blockLines.Add($rawLines[$j])
            $openCount  = ([regex]::Matches($rawLines[$j], '\{')).Count
            $closeCount = ([regex]::Matches($rawLines[$j], '\}')).Count
            $depth += $openCount - $closeCount
            if ($openCount -gt 0) { $opened = $true }
            if ($opened -and $depth -le 0) { break }
            $j++
        }

        $testBlocks.Add([PSCustomObject]@{
            TestType     = $testType
            TemplateName = $templateName
            InstanceName = $instanceName
            RawText      = ($blockLines -join "`n")
            StartLine    = $i
            EndLine      = $j
        })
        $i = $j + 1
    }
    elseif ($line -match '^\s*Flow\s+') {
        # Start of flow section
        break
    }
    else {
        $i++
    }
}

Write-Host "  Test blocks:  $($testBlocks.Count)"

# Parse flow blocks (same structure as test blocks)
$flowBlocks = [System.Collections.Generic.List[PSCustomObject]]::new()

while ($i -lt $rawLines.Count) {
    $line = $rawLines[$i]

    if ($line -match '^\s*Flow\s+(\S+)') {
        $flowName = $Matches[1]

        $startIdx = $i
        $depth = 0
        $opened = $false
        $blockLines = [System.Collections.Generic.List[string]]::new()
        $j = $i
        while ($j -lt $rawLines.Count) {
            $blockLines.Add($rawLines[$j])
            $openCount  = ([regex]::Matches($rawLines[$j], '\{')).Count
            $closeCount = ([regex]::Matches($rawLines[$j], '\}')).Count
            $depth += $openCount - $closeCount
            if ($openCount -gt 0) { $opened = $true }
            if ($opened -and $depth -le 0) { break }
            $j++
        }

        $flowBlocks.Add([PSCustomObject]@{
            TestType     = 'Flow'
            TemplateName = ''
            InstanceName = $flowName
            RawText      = ($blockLines -join "`n")
            StartLine    = $startIdx
            EndLine      = $j
        })
        $i = $j + 1
    }
    else {
        $i++
    }
}

Write-Host "  Flow blocks:  $($flowBlocks.Count)"
#endregion

#region ── apply symbol replacements ──────────────────────────────────────────
function Apply-Replacements {
    param([string]$Text, [hashtable[]]$Pairs)
    $result = $Text
    foreach ($p in $Pairs) {
        $result = $result.Replace($p.Find, $p.Replace)
    }
    return $result
}

function Normalize-ForDedup {
    param([string]$Text, [hashtable[]]$NormRules)
    # Always normalize BaseNumbers (universal across all modules)
    $n = $Text -replace 'BaseNumbers\s*=\s*"[^"]*"', 'BaseNumbers = "\BASE_NUMBER\"'
    # Strip SetBin names (unique bin numbers per flow item)
    $n = $n -replace 'SetBin\s+\S+', 'SetBin \BIN_NAME\'
    # Strip IncrementCounters references (unique counter names)
    $n = $n -replace 'IncrementCounters\s+\S+', 'IncrementCounters \COUNTER_REF\'
    # Apply module-specific normalization rules from config
    foreach ($rule in $NormRules) {
        $n = $n -replace $rule.Pattern, $rule.Replacement
    }
    return $n
}

Write-Host "Symbolizing and deduplicating tests..."

$processed = foreach ($block in $testBlocks) {
    $symbolized = Apply-Replacements -Text $block.RawText -Pairs $allReplacements
    $normalized = Normalize-ForDedup -Text $symbolized -NormRules $normPatterns
    [PSCustomObject]@{
        Block          = $block
        SymbolizedText = $symbolized
        NormalizedKey  = $normalized.Trim()
    }
}
#endregion

#region ── deduplicate tests ──────────────────────────────────────────────────
$groups     = [ordered]@{}
$groupOrder = [System.Collections.Generic.List[string]]::new()

foreach ($p in $processed) {
    $key = $p.NormalizedKey
    if (-not $groups.Contains($key)) {
        $groups[$key] = [System.Collections.Generic.List[PSCustomObject]]::new()
        $groupOrder.Add($key)
    }
    $groups[$key].Add($p)
}

$bodyUnique = $groupOrder.Count
$totalBlocks = $testBlocks.Count

# Name-based second pass: if multiple body-unique blocks share the same
# symbolized name (incomplete body symbolization), keep only the first.
$seenTestNames    = @{}
$nameDeduped      = [System.Collections.Generic.List[string]]::new()
$nameDropCount    = 0

foreach ($key in $groupOrder) {
    $rep = $groups[$key][0]
    # Extract symbolized instance name from the first line of the representative
    $firstLine = ($rep.SymbolizedText -split "`n")[0]
    if ($firstLine -match '^\s*(?:CSharpTest|MultiTrialTest)\s+\S+\s+(.+)$') {
        $symName = $Matches[1].Trim()
    } else {
        $symName = $key  # fallback
    }
    if ($seenTestNames.ContainsKey($symName)) {
        $nameDropCount++
        Write-Host "  Name dedup: dropping extra body variant of '$symName'"
        continue
    }
    $seenTestNames[$symName] = $true
    $nameDeduped.Add($key)
}
$groupOrder = $nameDeduped

$uniqueCount = $groupOrder.Count
$dupRemoved  = $totalBlocks - $uniqueCount

Write-Host "  Total test blocks:      $totalBlocks"
Write-Host "  Body-unique templates:  $bodyUnique"
Write-Host "  Name collisions fixed:  $nameDropCount"
Write-Host "  Final unique tests:     $uniqueCount"
Write-Host "  Duplicates removed:     $dupRemoved"
Write-Host "  Compression:            $([math]::Round(100.0 * $dupRemoved / [math]::Max(1,$totalBlocks), 1))%"
#endregion

#region ── symbolize and deduplicate flows ────────────────────────────────────
Write-Host "Symbolizing and deduplicating flows..."

$processedFlows = foreach ($block in $flowBlocks) {
    $symbolized = Apply-Replacements -Text $block.RawText -Pairs $allReplacements
    $normalized = Normalize-ForDedup -Text $symbolized -NormRules $normPatterns
    [PSCustomObject]@{
        Block          = $block
        SymbolizedText = $symbolized
        NormalizedKey  = $normalized.Trim()
    }
}

$flowGroups     = [ordered]@{}
$flowGroupOrder = [System.Collections.Generic.List[string]]::new()

foreach ($p in $processedFlows) {
    $key = $p.NormalizedKey
    if (-not $flowGroups.Contains($key)) {
        $flowGroups[$key] = [System.Collections.Generic.List[PSCustomObject]]::new()
        $flowGroupOrder.Add($key)
    }
    $flowGroups[$key].Add($p)
}

$bodyUniqueFlows = $flowGroupOrder.Count
$totalFlows      = $flowBlocks.Count

# Name-based second pass for flows
$seenFlowNames    = @{}
$nameDedupedFlows = [System.Collections.Generic.List[string]]::new()
$flowNameDrops    = 0

foreach ($key in $flowGroupOrder) {
    $rep = $flowGroups[$key][0]
    $firstLine = ($rep.SymbolizedText -split "`n")[0]
    if ($firstLine -match '^\s*Flow\s+(\S+)') {
        $symName = $Matches[1].Trim()
    } else {
        $symName = $key
    }
    if ($seenFlowNames.ContainsKey($symName)) {
        $flowNameDrops++
        Write-Host "  Name dedup: dropping extra body variant of flow '$symName'"
        continue
    }
    $seenFlowNames[$symName] = $true
    $nameDedupedFlows.Add($key)
}
$flowGroupOrder = $nameDedupedFlows

$uniqueFlows    = $flowGroupOrder.Count
$flowDupRemoved = $totalFlows - $uniqueFlows

Write-Host "  Total flow blocks:      $totalFlows"
Write-Host "  Body-unique templates:  $bodyUniqueFlows"
Write-Host "  Name collisions fixed:  $flowNameDrops"
Write-Host "  Final unique flows:     $uniqueFlows"
Write-Host "  Duplicates removed:     $flowDupRemoved"
Write-Host "  Compression:            $([math]::Round(100.0 * $flowDupRemoved / [math]::Max(1,$totalFlows), 1))%"
#endregion

#region ── emit BluePrint file ────────────────────────────────────────────────
$sb = [System.Text.StringBuilder]::new()

# Preamble kept verbatim
[void]$sb.AppendLine(($preambleLines -join "`n"))
[void]$sb.AppendLine("")

$emittedTestNames = @{}
$emitSkipped = 0
$groupIdx = 0
foreach ($key in $groupOrder) {
    $groupIdx++
    $members = $groups[$key]
    $representative = $members[0]

    # Extract symbolized name for final dedup guard
    $firstLine = ($representative.SymbolizedText -split "`n")[0]
    $emitName = $null
    if ($firstLine -match '^\s*(?:CSharpTest|MultiTrialTest)\s+\S+\s+(.+)$') {
        $emitName = $Matches[1].Trim()
    }
    if ($emitName -and $emittedTestNames.ContainsKey($emitName)) {
        $emitSkipped++
        Write-Host "  Emit guard: skipping duplicate name '$emitName'"
        continue
    }
    if ($emitName) { $emittedTestNames[$emitName] = $true }

    if ($members.Count -gt 1) {
        [void]$sb.AppendLine("")
        [void]$sb.AppendLine("# ==== GROUP $groupIdx : $($members.Count) instances (see prompt for expansion) ====")
        $nameList = ($members | ForEach-Object { $_.Block.InstanceName }) -join ', '
        if ($nameList.Length -gt 200) {
            $nameList = (($members | Select-Object -First 3 | ForEach-Object { $_.Block.InstanceName }) -join ', ') + ", ... ($($members.Count) total)"
        }
        [void]$sb.AppendLine("# Instances: $nameList")
    } else {
        [void]$sb.AppendLine("")
    }

    [void]$sb.AppendLine($representative.SymbolizedText)
}
if ($emitSkipped -gt 0) {
    Write-Host "  Emit guard: removed $emitSkipped additional test block(s) with duplicate names."
}

# Append deduplicated flow blocks
if ($flowGroupOrder.Count -gt 0) {
    [void]$sb.AppendLine("")
    [void]$sb.AppendLine("")

    $emittedFlowNames = @{}
    $flowEmitSkipped = 0
    $flowGroupIdx = 0
    foreach ($key in $flowGroupOrder) {
        $flowGroupIdx++
        $members = $flowGroups[$key]
        $representative = $members[0]

        # Extract symbolized flow name for final dedup guard
        $firstLine = ($representative.SymbolizedText -split "`n")[0]
        $emitName = $null
        if ($firstLine -match '^\s*Flow\s+(\S+)') {
            $emitName = $Matches[1].Trim()
        }
        if ($emitName -and $emittedFlowNames.ContainsKey($emitName)) {
            $flowEmitSkipped++
            Write-Host "  Emit guard: skipping duplicate flow '$emitName'"
            continue
        }
        if ($emitName) { $emittedFlowNames[$emitName] = $true }

        if ($members.Count -gt 1) {
            [void]$sb.AppendLine("")
            [void]$sb.AppendLine("# ==== FLOW GROUP $flowGroupIdx : $($members.Count) instances (see prompt for expansion) ====")
            $nameList = ($members | ForEach-Object { $_.Block.InstanceName }) -join ', '
            if ($nameList.Length -gt 200) {
                $nameList = (($members | Select-Object -First 3 | ForEach-Object { $_.Block.InstanceName }) -join ', ') + ", ... ($($members.Count) total)"
            }
            [void]$sb.AppendLine("# Flows: $nameList")
        } else {
            [void]$sb.AppendLine("")
        }

        [void]$sb.AppendLine($representative.SymbolizedText)
    }
    if ($flowEmitSkipped -gt 0) {
        Write-Host "  Emit guard: removed $flowEmitSkipped additional flow block(s) with duplicate names."
    }
}

$sb.ToString() | Set-Content -Path $bpFile -Encoding UTF8 -NoNewline

$bpLineCount = [IO.File]::ReadAllLines($bpFile).Count
$lineReduction = [math]::Round(100.0 * (1 - $bpLineCount / [math]::Max(1, $rawLines.Count)), 1)

Write-Host "`nBluePrint: $bpFile"
Write-Host "  BP lines:     $bpLineCount (from $($rawLines.Count), ${lineReduction}% reduction)"

# Post-emit auto-fix: remove any remaining duplicate test blocks from the file
$bpLines = [IO.File]::ReadAllLines($bpFile)
$bpTestNames = $bpLines | ForEach-Object { if ($_ -match '^\s*(CSharpTest|MultiTrialTest)\s+\S+\s+(.+)$') { $Matches[2].Trim() } } | Where-Object { $_ }
$bpDups = $bpTestNames | Group-Object | Where-Object { $_.Count -gt 1 }
if ($bpDups) {
    Write-Host "Auto-fixing $($bpDups.Count) duplicate test name(s) in emitted file..."
    $dupNameSet = @{}
    foreach ($d in $bpDups) { $dupNameSet[$d.Name] = $true }

    $seenTests = @{}
    $cleanLines = [System.Collections.Generic.List[string]]::new()
    $dropping = $false
    $droppedCount = 0

    foreach ($line in $bpLines) {
        if ($line -match '^\s*(CSharpTest|MultiTrialTest)\s+\S+\s+(.+)$') {
            $name = $Matches[2].Trim()
            if ($dupNameSet.ContainsKey($name) -and $seenTests.ContainsKey($name)) {
                $dropping = $true
                $droppedCount++
                Write-Host "  Dropped duplicate test: $name"
                continue
            }
            $seenTests[$name] = $true
            $dropping = $false
        } elseif ($dropping) {
            if ($line -match '^\}') { $dropping = $false }
            continue
        }
        $cleanLines.Add($line)
    }
    [IO.File]::WriteAllLines($bpFile, $cleanLines.ToArray())
    Write-Host "  Removed $droppedCount duplicate test block(s)."
    $bpLines = [IO.File]::ReadAllLines($bpFile)
} else {
    Write-Host "Duplicate check: OK - no duplicate test instance names."
}

# Post-emit auto-fix: remove any remaining duplicate flow blocks from the file
$bpFlowNames = $bpLines | ForEach-Object { if ($_ -match '^\s*Flow\s+(\S+)') { $Matches[1].Trim() } } | Where-Object { $_ }
$bpFlowDups = $bpFlowNames | Group-Object | Where-Object { $_.Count -gt 1 }
if ($bpFlowDups) {
    Write-Host "Auto-fixing $($bpFlowDups.Count) duplicate flow name(s) in emitted file..."
    $dupFlowSet = @{}
    foreach ($d in $bpFlowDups) { $dupFlowSet[$d.Name] = $true }

    $seenFlows = @{}
    $cleanLines = [System.Collections.Generic.List[string]]::new()
    $dropping = $false
    $depth = 0
    $droppedCount = 0

    foreach ($line in $bpLines) {
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
    [IO.File]::WriteAllLines($bpFile, $cleanLines.ToArray())
    Write-Host "  Removed $droppedCount duplicate flow block(s)."
} else {
    Write-Host "Duplicate check: OK - no duplicate flow names."
}

$bpLineCount = [IO.File]::ReadAllLines($bpFile).Count
Write-Host "  Final BP lines: $bpLineCount"
#endregion

#region ── emit Prompt file ───────────────────────────────────────────────────
$pr = [System.Text.StringBuilder]::new()

[void]$pr.AppendLine("=" * 80)
[void]$pr.AppendLine("MTPL BLUEPRINT EXPANSION PROMPT")
[void]$pr.AppendLine("Module: $moduleName")
[void]$pr.AppendLine("Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm')")
[void]$pr.AppendLine("=" * 80)
[void]$pr.AppendLine("")
[void]$pr.AppendLine("This BluePrint (.mtpl.bp) is a minimized, symbolized version of the full")
[void]$pr.AppendLine("module MTPL file.  Symbols are enclosed in backslashes: \SYMBOL_NAME\.")
[void]$pr.AppendLine("To regenerate the full MTPL, expand each symbol placeholder with every")
[void]$pr.AppendLine("value listed below, creating one test instance per combination.")
[void]$pr.AppendLine("")

# -- Symbol definitions ---
[void]$pr.AppendLine("-" * 80)
[void]$pr.AppendLine("SYMBOL DEFINITIONS")
[void]$pr.AppendLine("-" * 80)

foreach ($sym in $symbolDefs.GetEnumerator()) {
    [void]$pr.AppendLine("")
    [void]$pr.AppendLine("  Symbol:      \$($sym.Key)\")
    [void]$pr.AppendLine("  Description: $($sym.Value.Description)")
    [void]$pr.AppendLine("  Values:      $($sym.Value.Values -join ', ')")
}

[void]$pr.AppendLine("")
[void]$pr.AppendLine("-" * 80)
[void]$pr.AppendLine("EXPANSION GROUPS (Tests)")
[void]$pr.AppendLine("-" * 80)

$groupIdx = 0
foreach ($key in $groupOrder) {
    $groupIdx++
    $members = $groups[$key]
    if ($members.Count -le 1) { continue }

    $rep = $members[0]
    [void]$pr.AppendLine("")
    [void]$pr.AppendLine("GROUP $groupIdx  ($($members.Count) instances)")
    [void]$pr.AppendLine("  Test type: $($rep.Block.TestType) $($rep.Block.TemplateName)")
    [void]$pr.AppendLine("  Original instances:")
    foreach ($m in $members) {
        [void]$pr.AppendLine("    - $($m.Block.InstanceName)")
    }

    # Detect which symbols actually vary in this group
    $varying = [ordered]@{}
    foreach ($sym in $symbolDefs.GetEnumerator()) {
        $found = [System.Collections.Generic.HashSet[string]]::new()
        foreach ($m in $members) {
            foreach ($val in $sym.Value.Values) {
                $cleanVal = $val -replace '\s*\(.*\)', ''
                if ($m.Block.InstanceName.Contains($cleanVal) -or $m.Block.RawText.Contains($cleanVal)) {
                    [void]$found.Add($cleanVal)
                }
            }
        }
        if ($found.Count -gt 1) {
            $varying[$sym.Key] = ($found | Sort-Object) -join ', '
        }
    }
    if ($varying.Count -gt 0) {
        [void]$pr.AppendLine("  Varying symbols:")
        foreach ($v in $varying.GetEnumerator()) {
            [void]$pr.AppendLine("    \$($v.Key)\ = [$($v.Value)]")
        }
    }
    [void]$pr.AppendLine("  -> Expand: create one instance for each combination of the above symbol values.")
}

# -- Flow expansion groups ---
if ($flowGroupOrder.Count -gt 0) {
    [void]$pr.AppendLine("")
    [void]$pr.AppendLine("-" * 80)
    [void]$pr.AppendLine("EXPANSION GROUPS (Flows)")
    [void]$pr.AppendLine("-" * 80)

    $flowGroupIdx = 0
    foreach ($key in $flowGroupOrder) {
        $flowGroupIdx++
        $members = $flowGroups[$key]
        if ($members.Count -le 1) { continue }

        $rep = $members[0]
        [void]$pr.AppendLine("")
        [void]$pr.AppendLine("FLOW GROUP $flowGroupIdx  ($($members.Count) instances)")
        [void]$pr.AppendLine("  Original flows:")
        foreach ($m in $members) {
            [void]$pr.AppendLine("    - $($m.Block.InstanceName)")
        }

        $varying = [ordered]@{}
        foreach ($sym in $symbolDefs.GetEnumerator()) {
            $found = [System.Collections.Generic.HashSet[string]]::new()
            foreach ($m in $members) {
                foreach ($val in $sym.Value.Values) {
                    $cleanVal = $val -replace '\s*\(.*\)', ''
                    if ($m.Block.InstanceName.Contains($cleanVal) -or $m.Block.RawText.Contains($cleanVal)) {
                        [void]$found.Add($cleanVal)
                    }
                }
            }
            if ($found.Count -gt 1) {
                $varying[$sym.Key] = ($found | Sort-Object) -join ', '
            }
        }
        if ($varying.Count -gt 0) {
            [void]$pr.AppendLine("  Varying symbols:")
            foreach ($v in $varying.GetEnumerator()) {
                [void]$pr.AppendLine("    \$($v.Key)\ = [$($v.Value)]")
            }
        }
        [void]$pr.AppendLine("  -> Expand: create one flow for each combination of the above symbol values.")
    }
}

# -- Notes ---
[void]$pr.AppendLine("")
[void]$pr.AppendLine("-" * 80)
[void]$pr.AppendLine("NOTES")
[void]$pr.AppendLine("-" * 80)
[void]$pr.AppendLine("- Counters section is kept verbatim from the original file.")
[void]$pr.AppendLine("- BaseNumbers are unique per instance; assign sequentially when expanding.")
foreach ($note in $moduleNotes) {
    [void]$pr.AppendLine("- $note")
}

$pr.ToString() | Set-Content -Path $promptFile -Encoding UTF8 -NoNewline
Write-Host "Prompt:    $promptFile"
#endregion

Write-Host ""
Write-Host "=== Done ==="
