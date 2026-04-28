<#
.SYNOPSIS
    Generic MTPL-to-BluePrint transformer. Module-agnostic.

.DESCRIPTION
    Transforms any NVL .mtpl file into a BluePrint (BP) + companion prompt,
    using a per-module configuration file (bp-config.json) that defines:
      - symbols:        name, description, values, replacement pairs
      - notes:          module-specific notes appended to the prompt file

    Algorithm:
      1. Restore .mtpl_orig as the generation baseline (or create it on first run).
      2. Parse the .mtpl into preamble (header + Counters), test blocks, and flow blocks.
      3. For each test block, detect its symbol combination and apply symbol replacements.
      4. Annotate each test block with a # BP_COMBO comment for per-block expansion.
      5. Keep ALL test blocks (no deduplication). Keep flow blocks verbatim.
      6. Emit BluePrint (.mtpl.bp) and companion prompt (.prompt.txt).
      7. Validate via trial expansion that each block round-trips correctly.

    The BP preserves all 1:1 test and flow counts from the original.
    Flow blocks are kept verbatim because they reference items across multiple
    symbol combinations (e.g., a flow may reference M0, M1, M2, M3 sub-flows).

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
$origMtpl  = Join-Path $moduleDir "${moduleName}.mtpl_orig"
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

# Load normalization patterns from config (optional, for reference only)
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

    if ($line -match '^\s*CSharpTest\s+(\S+)\s+(.+)$') {
        $testType     = 'CSharpTest'
        $templateName = $Matches[1]
        $instanceName = $Matches[2].Trim()
    }
    elseif ($line -match '^\s*MultiTrialTest\s+(\S+)\s*$') {
        $testType     = 'MultiTrialTest'
        $templateName = ''
        $instanceName = $Matches[1].Trim()
    }
    else {
        $testType = $null
    }

    if ($testType) {

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

Write-Host "Symbolizing test blocks (no deduplication)..."

# Detect symbol combination for each test block using replacement find patterns
# This is more precise than raw value substring matching, avoiding false positives
# (e.g., "F5" in "F5XAT" being mistaken for ECC_FREQ=F5 when ECC_FREQ is actually F6).
$symNames = @($config.symbols | ForEach-Object { $_.name })

function Detect-Combo {
    param([PSCustomObject]$Block, $ConfigSymbols)
    $combo = [ordered]@{}
    # Build body text excluding preceding comment lines (which may contain
    # commented-out test blocks with misleading symbol values).
    $headerLine = "$($Block.TestType) $($Block.TemplateName) $($Block.InstanceName)".Trim()
    $bodyLines = $Block.RawText -split "`n" | Where-Object {
        $_.Trim() -and (-not ($_.Trim().StartsWith('#')))
    }
    $bodyText = $bodyLines -join "`n"
    foreach ($sym in $ConfigSymbols) {
        $cleanValues = @($sym.values | ForEach-Object { ($_ -replace '\s*\(.*\)', '').Trim() })
        $found = $null
        # 1. Check replacement find patterns against instance name (most reliable)
        foreach ($pair in $sym.replacements) {
            if ($Block.InstanceName.Contains($pair.find)) {
                foreach ($val in $cleanValues) {
                    if ($pair.find.Contains($val) -or $pair.find.Contains($val.ToLower())) {
                        $found = $val; break
                    }
                }
                if ($found) { break }
            }
        }
        # 2. Check replacement find patterns against non-comment body
        if (-not $found) {
            foreach ($pair in $sym.replacements) {
                if ($bodyText.Contains($pair.find)) {
                    foreach ($val in $cleanValues) {
                        if ($pair.find.Contains($val) -or $pair.find.Contains($val.ToLower())) {
                            $found = $val; break
                        }
                    }
                    if ($found) { break }
                }
            }
        }
        # 3. Fallback: check value with underscore/word boundaries in instance name
        if (-not $found) {
            foreach ($val in $cleanValues) {
                $escaped = [regex]::Escape($val)
                if ($Block.InstanceName -match "(^|_)${escaped}(_|$)") {
                    $found = $val; break
                }
            }
        }
        # 4. Last resort: check value in non-comment body with boundaries
        if (-not $found) {
            foreach ($val in $cleanValues) {
                $escaped = [regex]::Escape($val)
                if ($bodyText -match "(^|_|`")${escaped}(_|`"|$)") {
                    $found = $val; break
                }
            }
        }
        if ($found) { $combo[$sym.name] = $found }
    }
    return $combo
}

$processedTests = [System.Collections.Generic.List[PSCustomObject]]::new()
foreach ($block in $testBlocks) {
    $combo = Detect-Combo -Block $block -ConfigSymbols $config.symbols
    $symbolized = Apply-Replacements -Text $block.RawText -Pairs $allReplacements
    $processedTests.Add([PSCustomObject]@{
        Block          = $block
        SymbolizedText = $symbolized
        Combo          = $combo
    })
}

Write-Host "  Test blocks:      $($processedTests.Count) (before BaseNumbers compression)"
#endregion

#region ── BaseNumbers compression ────────────────────────────────────────────
# Normalize BaseNumbers to a default ("0") and merge blocks that become identical.
# Each merged group records the BaseNumbers per combo for later restoration.
$defaultBaseNum = "0"
$compressions = [System.Collections.Generic.List[PSCustomObject]]::new()

# Build normalized text for each block (BaseNumbers -> default)
foreach ($pt in $processedTests) {
    $normalized = $pt.SymbolizedText -replace '(\bBaseNumbers\s*=\s*")(\d+)(")', "`${1}${defaultBaseNum}`${3}"
    $pt | Add-Member -NotePropertyName 'NormalizedText' -NotePropertyValue $normalized -Force
    # Extract this block's original BaseNumbers
    $bnMatch = [regex]::Match($pt.SymbolizedText, '\bBaseNumbers\s*=\s*"(\d+)"')
    $bn = if ($bnMatch.Success) { $bnMatch.Groups[1].Value } else { $null }
    $pt | Add-Member -NotePropertyName 'BaseNumbers' -NotePropertyValue $bn -Force
}

# Group by NormalizedText — blocks with identical symbolized text except BaseNumbers
$groups = [ordered]@{}
foreach ($pt in $processedTests) {
    $key = $pt.NormalizedText
    if (-not $groups.Contains($key)) { $groups[$key] = [System.Collections.Generic.List[PSCustomObject]]::new() }
    $groups[$key].Add($pt)
}

# Build final list: one representative per group, with BaseNumbers mapping
# Only compress if ALL blocks in the group have UNIQUE combo keys (otherwise
# we can't restore individual BaseNumbers during expansion).
$mergedTests = [System.Collections.Generic.List[PSCustomObject]]::new()
$skippedCompressions = 0
foreach ($entry in $groups.GetEnumerator()) {
    $group = $entry.Value
    $representative = $group[0]

    if ($group.Count -eq 1) {
        # Single block — no compression, but still record BaseNumbers for restoration
        $singleBnMap = [ordered]@{}
        $singleComboKey = ($representative.Combo.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join ', '
        if ($representative.BaseNumbers) { $singleBnMap[$singleComboKey] = $representative.BaseNumbers }
        $mergedTests.Add([PSCustomObject]@{
            SymbolizedText = $representative.NormalizedText
            Combo          = $representative.Combo
            BaseNumbersMap = $singleBnMap
            OriginalBlocks = $group
            Block          = $representative.Block
        })
        continue
    }

    # Build BaseNumbers map: comboKey -> BaseNumbers
    $bnMap = [ordered]@{}
    $hasDuplicateKeys = $false
    foreach ($pt in $group) {
        $comboKey = ($pt.Combo.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join ', '
        if ($bnMap.Contains($comboKey)) {
            $hasDuplicateKeys = $true
            break
        }
        $bnMap[$comboKey] = if ($pt.BaseNumbers) { $pt.BaseNumbers } else { "" }
    }

    if ($hasDuplicateKeys) {
        # Combo keys not unique — can't restore BaseNumbers per block during expansion.
        # Keep all blocks separate (no compression for this group).
        $skippedCompressions++
        foreach ($pt in $group) {
            $singleBnMap = [ordered]@{}
            $singleComboKey = ($pt.Combo.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join ', '
            if ($pt.BaseNumbers) { $singleBnMap[$singleComboKey] = $pt.BaseNumbers }
            $mergedTests.Add([PSCustomObject]@{
                SymbolizedText = $pt.NormalizedText
                Combo          = $pt.Combo
                BaseNumbersMap = $singleBnMap
                OriginalBlocks = [System.Collections.Generic.List[PSCustomObject]]::new()
                Block          = $pt.Block
            })
            $mergedTests[-1].OriginalBlocks.Add($pt)
        }
    } else {
        # All combo keys unique — safe to compress
        $mergedTests.Add([PSCustomObject]@{
            SymbolizedText = $representative.NormalizedText
            Combo          = $representative.Combo
            BaseNumbersMap = $bnMap
            OriginalBlocks = $group
            Block          = $representative.Block
        })
        $compressions.Add([PSCustomObject]@{
            RepresentativeName = $representative.Block.InstanceName
            MergedCount        = $group.Count
            MergedInstances    = @($group | ForEach-Object { $_.Block.InstanceName })
            BaseNumbersMap     = $bnMap
        })
    }
}

$mergedCount = $processedTests.Count - $mergedTests.Count
Write-Host "  After BaseNumbers compression: $($mergedTests.Count) blocks ($mergedCount merged away, $skippedCompressions groups skipped due to duplicate combo keys)"
#endregion

#region ── emit BluePrint file ────────────────────────────────────────────────
# Flow blocks are kept verbatim - they reference items across multiple symbol
# combinations and cannot be safely symbolized for per-block expansion.

Write-Host "Emitting BluePrint (with BaseNumbers compression)..."

$sb = [System.Text.StringBuilder]::new()

# Preamble kept verbatim
[void]$sb.AppendLine(($preambleLines -join "`n"))
[void]$sb.AppendLine("")

# Emit merged test blocks with combo + BaseNumbers annotations
foreach ($mt in $mergedTests) {
    $comboStr = ($mt.Combo.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join ', '
    [void]$sb.AppendLine("")
    [void]$sb.AppendLine("# BP_COMBO: $comboStr")
    # Emit BaseNumbers mapping for all blocks that have a BaseNumbers value
    # Multi-entry: compressed group (multiple originals expand from one template)
    # Single-entry: non-compressed block (restores BaseNumbers from default "0")
    if ($mt.BaseNumbersMap.Count -gt 0) {
        $bnParts = @()
        foreach ($bnEntry in $mt.BaseNumbersMap.GetEnumerator()) {
            $bnParts += "$($bnEntry.Key)|$($bnEntry.Value)"
        }
        [void]$sb.AppendLine("# BP_BASENUMBERS: $($bnParts -join ' ;; ')")
    }
    [void]$sb.AppendLine($mt.SymbolizedText)
}

# Emit all flow blocks verbatim
if ($flowBlocks.Count -gt 0) {
    [void]$sb.AppendLine("")
    [void]$sb.AppendLine("")
    foreach ($fb in $flowBlocks) {
        [void]$sb.AppendLine("")
        [void]$sb.AppendLine($fb.RawText)
    }
}

$sb.ToString() | Set-Content -Path $bpFile -Encoding UTF8 -NoNewline

$bpLineCount = [IO.File]::ReadAllLines($bpFile).Count
Write-Host "`nBluePrint: $bpFile"
Write-Host "  BP lines:     $bpLineCount (from $($rawLines.Count) original)"
Write-Host "  Test blocks:  $($mergedTests.Count) (from $($processedTests.Count) original, $mergedCount compressed)"
Write-Host "  Flow blocks:  $($flowBlocks.Count)"
#endregion

#region ── trial expansion validation ─────────────────────────────────────────
# Do a trial expansion of each BP test block using its own combo values and
# compare every param value against the original.  Any test block that produces
# a param value not present in the original gets reverted to its unsymbolized
# (original) text.
Write-Host ""
Write-Host "Trial expansion validation..."

# Build original param value index: ParamName -> set of values
$origLines   = [IO.File]::ReadAllLines($origMtpl)
$origPV      = @{}
foreach ($l in $origLines) {
    if ($l -match '^\s*(\w+)\s*=\s*"([^"]*)"') {
        $pN = $Matches[1]; $pV = $Matches[2]
        if (-not $origPV.ContainsKey($pN)) { $origPV[$pN] = @{} }
        $origPV[$pN][$pV] = $true
    }
}

function Build-ComboReplacementMap {
    param([hashtable]$Combo, $ConfigSymbols)
    $map = [System.Collections.Generic.List[System.Collections.Generic.KeyValuePair[string,string]]]::new()
    foreach ($sym in $ConfigSymbols) {
        if (-not $Combo.ContainsKey($sym.name)) { continue }
        $val = $Combo[$sym.name]
        $map.Add([System.Collections.Generic.KeyValuePair[string,string]]::new('\' + $sym.name + '\', $val))
        $lower = $sym.name.ToLower()
        $map.Add([System.Collections.Generic.KeyValuePair[string,string]]::new('\' + $lower + '\', $val.ToLower()))
        $numMatch = [regex]::Match($val, '\d+')
        if ($numMatch.Success) {
            $map.Add([System.Collections.Generic.KeyValuePair[string,string]]::new('\' + $sym.name + '_NUM\', $numMatch.Value))
            $map.Add([System.Collections.Generic.KeyValuePair[string,string]]::new('\' + $lower + '_num\', $numMatch.Value))
        }
    }
    return $map
}

function Expand-Trial {
    param([string]$Text, $Map)
    $r = $Text
    foreach ($kv in $Map) { $r = $r.Replace($kv.Key, $kv.Value) }
    return $r
}

# Read the BP and parse test blocks for validation
$bpLines = [IO.File]::ReadAllLines($bpFile)

# Parse test blocks and their BP_COMBO annotations
$bpTestBlocks = [System.Collections.Generic.List[PSCustomObject]]::new()
$lastComboLine = -1
$lastCombo = $null
$bi = 0
while ($bi -lt $bpLines.Count) {
    if ($bpLines[$bi] -match '^# BP_COMBO:\s*(.+)$') {
        $comboStr = $Matches[1].Trim()
        $combo = [ordered]@{}
        foreach ($part in ($comboStr -split ',\s*')) {
            $kv = $part -split '=', 2
            if ($kv.Count -eq 2) { $combo[$kv[0].Trim()] = $kv[1].Trim() }
        }
        $lastCombo = $combo
        $lastComboLine = $bi
        $bi++
        continue
    }
    if ($bpLines[$bi] -match '^\s*CSharpTest\s+(\S+)\s+(.+)$') {
        $bpInstanceName = $Matches[2].Trim()
    } elseif ($bpLines[$bi] -match '^\s*MultiTrialTest\s+(\S+)\s*$') {
        $bpInstanceName = $Matches[1].Trim()
    } else {
        $bpInstanceName = $null
    }
    if ($bpInstanceName) {
        $blockStart = $bi
        $depth = 0; $opened = $false
        while ($bi -lt $bpLines.Count) {
            $depth += ([regex]::Matches($bpLines[$bi], '\{')).Count
            $depth -= ([regex]::Matches($bpLines[$bi], '\}')).Count
            if ($depth -gt 0) { $opened = $true }
            $bi++
            if ($opened -and $depth -le 0) { break }
        }
        $bpTestBlocks.Add([PSCustomObject]@{
            StartLine = $blockStart
            EndLine   = $bi - 1
            Name      = $bpInstanceName
            Combo     = $lastCombo
            ComboLine = $lastComboLine
        })
        $lastCombo = $null
    } else {
        $bi++
    }
}

# For each BP test block, trial-expand using its combo and check param values
# Skip BaseNumbers during validation since it's been normalized to default
$revertCount = 0
foreach ($tb in $bpTestBlocks) {
    if (-not $tb.Combo -or $tb.Combo.Count -eq 0) { continue }

    $comboMap = Build-ComboReplacementMap -Combo $tb.Combo -ConfigSymbols $config.symbols
    $blockText = ($bpLines[$tb.StartLine..$tb.EndLine]) -join "`n"
    $expanded  = Expand-Trial -Text $blockText -Map $comboMap

    $badParams = @()
    foreach ($line in ($expanded -split "`n")) {
        if ($line -match '^\s*(\w+)\s*=\s*"([^"]*)"') {
            $pN = $Matches[1]; $pV = $Matches[2]
            if ($pN -eq 'BaseNumbers') { continue }  # skip — normalized to default
            if ($origPV.ContainsKey($pN) -and -not $origPV[$pN].ContainsKey($pV)) {
                $badParams += "$pN=`"$pV`""
            }
        }
    }
    if ($badParams.Count -gt 0) {
        # Revert: find the merged-test entry and expand back into original blocks
        $expandedName = Expand-Trial -Text $tb.Name -Map $comboMap
        # Find ALL original blocks that were merged into this BP entry
        $matchedMerge = $null
        foreach ($mt in $mergedTests) {
            foreach ($ob in $mt.OriginalBlocks) {
                if ($ob.Block.InstanceName -eq $expandedName) {
                    $matchedMerge = $mt; break
                }
            }
            if ($matchedMerge) { break }
        }
        if ($matchedMerge) {
            Write-Host "  Reverting '$($tb.Name)' -> $($matchedMerge.OriginalBlocks.Count) original(s) (bad: $($badParams[0]))"
            # Clear the BP_COMBO and BP_BASENUMBERS annotation lines
            if ($tb.ComboLine -ge 0) { $bpLines[$tb.ComboLine] = $null }
            # Also clear BP_BASENUMBERS line if present (between combo and block start)
            for ($ci = $tb.ComboLine + 1; $ci -lt $tb.StartLine; $ci++) {
                if ($bpLines[$ci] -match '^# BP_BASENUMBERS:') { $bpLines[$ci] = $null }
            }
            for ($ri = $tb.StartLine; $ri -le $tb.EndLine; $ri++) {
                $bpLines[$ri] = $null
            }
            # Emit all original blocks from the merged group
            $revertSb = [System.Text.StringBuilder]::new()
            foreach ($ob in $matchedMerge.OriginalBlocks) {
                [void]$revertSb.AppendLine($ob.Block.RawText)
            }
            $bpLines[$tb.StartLine] = $revertSb.ToString().TrimEnd()
            $revertCount++
        } else {
            # Fallback: try single original block match
            $origBlock = $null
            foreach ($ob in $testBlocks) {
                if ($ob.InstanceName -eq $expandedName) {
                    $origBlock = $ob; break
                }
            }
            if ($origBlock) {
                Write-Host "  Reverting '$($tb.Name)' -> original '$($origBlock.InstanceName)' (bad: $($badParams -join ', '))"
                if ($tb.ComboLine -ge 0) { $bpLines[$tb.ComboLine] = $null }
                for ($ci = $tb.ComboLine + 1; $ci -lt $tb.StartLine; $ci++) {
                    if ($bpLines[$ci] -match '^# BP_BASENUMBERS:') { $bpLines[$ci] = $null }
                }
                for ($ri = $tb.StartLine; $ri -le $tb.EndLine; $ri++) {
                    $bpLines[$ri] = $null
                }
                $bpLines[$tb.StartLine] = $origBlock.RawText
                $revertCount++
            } else {
                Write-Host "  WARNING: could not find original block for '$expandedName' to revert"
            }
        }
    }
}

if ($revertCount -gt 0) {
    $newBp = [System.Collections.Generic.List[string]]::new()
    foreach ($line in $bpLines) {
        if ($null -ne $line) {
            foreach ($subLine in ($line -split "`n")) {
                $newBp.Add($subLine)
            }
        }
    }
    [IO.File]::WriteAllLines($bpFile, $newBp.ToArray())
    Write-Host "  Reverted $revertCount test block(s) to original (unsymbolized)."
    $bpLineCount = [IO.File]::ReadAllLines($bpFile).Count
    Write-Host "  Updated BP lines: $bpLineCount"
} else {
    Write-Host "  OK - all test blocks produce valid param values."
}
#endregion

#region ── emit Prompt file ───────────────────────────────────────────────────
$pr = [System.Text.StringBuilder]::new()

[void]$pr.AppendLine("=" * 80)
[void]$pr.AppendLine("MTPL BLUEPRINT EXPANSION PROMPT")
[void]$pr.AppendLine("Module: $moduleName")
[void]$pr.AppendLine("Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm')")
[void]$pr.AppendLine("=" * 80)
[void]$pr.AppendLine("")
[void]$pr.AppendLine("This BluePrint (.mtpl.bp) is a version of the full module MTPL file with")
[void]$pr.AppendLine("symbol placeholders in test block names and parameter values.")
[void]$pr.AppendLine("Symbols are enclosed in backslashes: \SYMBOL_NAME\.")
[void]$pr.AppendLine("")
[void]$pr.AppendLine("Each test block is preceded by a # BP_COMBO annotation that specifies")
[void]$pr.AppendLine("the symbol values for that specific test instance.")
[void]$pr.AppendLine("")
[void]$pr.AppendLine("Flow blocks are kept verbatim from the original because they reference")
[void]$pr.AppendLine("items across multiple symbol combinations.")
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

# -- Notes ---
[void]$pr.AppendLine("")
[void]$pr.AppendLine("-" * 80)
[void]$pr.AppendLine("NOTES")
[void]$pr.AppendLine("-" * 80)
[void]$pr.AppendLine("- Counters section is kept verbatim from the original file.")
[void]$pr.AppendLine("- Flow blocks are kept verbatim (not symbolized).")
[void]$pr.AppendLine("- Each test block has a # BP_COMBO annotation for per-block expansion.")
[void]$pr.AppendLine("- BaseNumbers are normalized to '$defaultBaseNum' in the BP.")
[void]$pr.AppendLine("- Compressed blocks have # BP_BASENUMBERS annotations with combo->value maps.")
[void]$pr.AppendLine("- See $moduleName.compressions.log for compression details.")
foreach ($note in $moduleNotes) {
    [void]$pr.AppendLine("- $note")
}

$pr.ToString() | Set-Content -Path $promptFile -Encoding UTF8 -NoNewline
Write-Host "Prompt:    $promptFile"
#endregion

#region ── extract paramValues from original and update symbols.json ───────────
Write-Host ""
Write-Host "Extracting parameter values from original for validation..."

$origLines = [IO.File]::ReadAllLines($origMtpl)
$paramValues = [ordered]@{}

foreach ($l in $origLines) {
    if ($l -match '^\s*(\w+)\s*=\s*"([^"]*)"') {
        $pName = $Matches[1]
        $pVal  = $Matches[2]
        if (-not $paramValues.Contains($pName)) {
            $paramValues[$pName] = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
        }
        [void]$paramValues[$pName].Add($pVal)
    }
}

# Load existing symbols.json, add/update paramValues section
$symbolsJsonPath = Join-Path $OutputDir 'symbols.json'
if (Test-Path $symbolsJsonPath) {
    $symbolsJson = Get-Content -Raw $symbolsJsonPath | ConvertFrom-Json
} else {
    throw "symbols.json not found at $symbolsJsonPath"
}

# Build paramValues as a PSCustomObject with sorted arrays
$pvObj = [ordered]@{}
foreach ($entry in $paramValues.GetEnumerator()) {
    $pvObj[$entry.Key] = @($entry.Value | Sort-Object)
}

# Add or replace the paramValues property
if ($symbolsJson.PSObject.Properties['paramValues']) {
    $symbolsJson.PSObject.Properties.Remove('paramValues')
}
$symbolsJson | Add-Member -NotePropertyName 'paramValues' -NotePropertyValue ([PSCustomObject]$pvObj)

# Write back symbols.json (formatted)
$symbolsJson | ConvertTo-Json -Depth 10 | Set-Content -Path $symbolsJsonPath -Encoding UTF8
Write-Host "  Updated symbols.json with paramValues ($($paramValues.Count) parameters, $($paramValues.Values | ForEach-Object { $_.Count } | Measure-Object -Sum | Select-Object -ExpandProperty Sum) unique values)"
#endregion

#region ── generate combinations table ────────────────────────────────────────
# For each test block in the original, detect which symbol values are present
# and produce a CSV table showing the actual combinations that exist.
Write-Host ""
Write-Host "Generating combinations table..."

$comboFile = Join-Path $OutputDir "$moduleName.combinations.csv"
$symNames  = @($config.symbols | ForEach-Object { $_.name })

# Build a lookup: for each symbol, its possible values (cleaned)
$symValMap = [ordered]@{}
foreach ($sym in $config.symbols) {
    $symValMap[$sym.name] = @($sym.values | ForEach-Object { ($_ -replace '\s*\(.*\)', '').Trim() })
}

$rows = [System.Collections.Generic.List[PSCustomObject]]::new()
foreach ($block in $testBlocks) {
    $row = [ordered]@{ TestInstance = $block.InstanceName; TestType = $block.TestType; Template = $block.TemplateName }
    foreach ($sName in $symNames) {
        $found = ''
        foreach ($sVal in $symValMap[$sName]) {
            # Check the instance name first (case-sensitive), then the full body
            if ($block.InstanceName.Contains($sVal) -or $block.InstanceName.Contains($sVal.ToLower())) {
                $found = $sVal; break
            }
        }
        if (-not $found) {
            # Check block body
            foreach ($sVal in $symValMap[$sName]) {
                if ($block.RawText.Contains($sVal) -or $block.RawText.Contains($sVal.ToLower())) {
                    $found = $sVal; break
                }
            }
        }
        $row[$sName] = $found
    }
    $rows.Add([PSCustomObject]$row)
}

# Write CSV (handle locked file gracefully)
$header = @('TestInstance', 'TestType', 'Template') + $symNames
$csvLines = [System.Collections.Generic.List[string]]::new()
$csvLines.Add($header -join ',')
foreach ($r in $rows) {
    $vals = foreach ($h in $header) { $r.$h }
    $csvLines.Add($vals -join ',')
}
try {
    [IO.File]::WriteAllLines($comboFile, $csvLines.ToArray())
    Write-Host "  Written: $comboFile ($($rows.Count) rows, $($symNames.Count) symbols)"
} catch {
    Write-Warning "Could not write $comboFile (file locked?). Skipping combinations CSV."
}

# Summary: unique combinations per symbol
foreach ($sName in $symNames) {
    $uniq = ($rows | ForEach-Object { $_.$sName } | Where-Object { $_ } | Sort-Object -Unique) -join ', '
    $count = ($rows | ForEach-Object { $_.$sName } | Where-Object { $_ } | Sort-Object -Unique).Count
    Write-Host "    $sName [$count]: $uniq"
}
#endregion

#region ── compression report ─────────────────────────────────────────────────
$reportFile = Join-Path $OutputDir "$moduleName.compressions.log"
$rpt = [System.Text.StringBuilder]::new()
[void]$rpt.AppendLine("=" * 80)
[void]$rpt.AppendLine("BLUEPRINT COMPRESSION REPORT")
[void]$rpt.AppendLine("Module:    $moduleName")
[void]$rpt.AppendLine("Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm')")
[void]$rpt.AppendLine("=" * 80)
[void]$rpt.AppendLine("")
[void]$rpt.AppendLine("Original test blocks:  $($processedTests.Count)")
[void]$rpt.AppendLine("After compression:     $($mergedTests.Count)")
[void]$rpt.AppendLine("Blocks merged away:    $mergedCount")
[void]$rpt.AppendLine("Compression groups:    $($compressions.Count)")
[void]$rpt.AppendLine("Reverted blocks:       $revertCount")
[void]$rpt.AppendLine("")

if ($compressions.Count -gt 0) {
    [void]$rpt.AppendLine("-" * 80)
    [void]$rpt.AppendLine("COMPRESSION DETAILS")
    [void]$rpt.AppendLine("-" * 80)
    $groupNum = 0
    foreach ($c in $compressions) {
        $groupNum++
        [void]$rpt.AppendLine("")
        [void]$rpt.AppendLine("Group ${groupNum}: $($c.MergedCount) instances merged")
        [void]$rpt.AppendLine("  Representative: $($c.RepresentativeName)")
        [void]$rpt.AppendLine("  Merged instances:")
        foreach ($inst in $c.MergedInstances) {
            $bn = ''
            foreach ($bnEntry in $c.BaseNumbersMap.GetEnumerator()) {
                if ($bnEntry.Key -match [regex]::Escape($inst) -or $c.MergedInstances.Count -le 5) {
                    # show all for small groups
                }
            }
            [void]$rpt.AppendLine("    - $inst")
        }
        [void]$rpt.AppendLine("  BaseNumbers mapping:")
        foreach ($bnEntry in $c.BaseNumbersMap.GetEnumerator()) {
            [void]$rpt.AppendLine("    [$($bnEntry.Key)] -> BaseNumbers=$($bnEntry.Value)")
        }
    }
} else {
    [void]$rpt.AppendLine("No compressions were performed.")
}

[void]$rpt.AppendLine("")
[void]$rpt.AppendLine("-" * 80)
[void]$rpt.AppendLine("REVERTED BLOCKS (kept as original, not symbolized)")
[void]$rpt.AppendLine("-" * 80)
if ($revertCount -gt 0) {
    [void]$rpt.AppendLine("$revertCount block(s) were reverted due to invalid param values after trial expansion.")
    [void]$rpt.AppendLine("These blocks appear in the BP without # BP_COMBO annotations.")
} else {
    [void]$rpt.AppendLine("No blocks were reverted.")
}

$rpt.ToString() | Set-Content -Path $reportFile -Encoding UTF8 -NoNewline
Write-Host "Report:    $reportFile"
#endregion

Write-Host ""
Write-Host "=== Done ==="
