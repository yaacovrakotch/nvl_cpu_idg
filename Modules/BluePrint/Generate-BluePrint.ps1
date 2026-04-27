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
      1. Parse the .mtpl into preamble (header + Counters) and test blocks.
      2. Apply symbol replacements (literal find/replace from config).
      3. Normalise blocks (BaseNumbers + config-defined patterns) for dedup.
      4. Group identical normalised blocks; keep one representative per group.
      5. Emit BluePrint (.mtpl.bp) and companion prompt (.prompt.txt).

.PARAMETER InputMtpl
    Path to the source .mtpl file.

.PARAMETER ConfigFile
    Path to the bp-config.json for this module.

.PARAMETER OutputDir
    Directory for output files.  Defaults to .\BluePrint next to the input.

.EXAMPLE
    # From any directory:
    .\Generate-BluePrint.ps1 -InputMtpl "..\ARR\ARR_ATOM_CXPKGS9\ARR_ATOM_CXPKGS9.mtpl" `
                              -ConfigFile "..\ARR\ARR_ATOM_CXPKGS9\BluePrint\bp-config.json"

    # With explicit output:
    .\Generate-BluePrint.ps1 -InputMtpl "C:\...\ARR_ATOM_CXX.mtpl" `
                              -ConfigFile "C:\...\bp-config.json" `
                              -OutputDir  "C:\...\BluePrint"
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

Write-Host "=== MTPL BluePrint Generator (generic) ==="
Write-Host "Module : $moduleName"
Write-Host "Input  : $InputMtpl"
Write-Host "Config : $ConfigFile"
Write-Host "Output : $OutputDir"
#endregion

#region ── load config ────────────────────────────────────────────────────────
$config = Get-Content -Raw $ConfigFile | ConvertFrom-Json

# Build ordered symbol definitions and flat replacement list from config
$symbolDefs     = [ordered]@{}   # symbol name -> @{ Description; Values }
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
# Split into preamble (header + Counters) and test blocks.

function Find-EndOfCounters {
    param([string[]]$Lines)
    for ($i = 0; $i -lt $Lines.Count; $i++) {
        if ($Lines[$i] -match '^\}\s*#\s*End of Test Counter Definition') {
            return $i
        }
    }
    # fallback: line before first CSharpTest/MultiTrialTest
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

    # Stop at Flow section — only test definitions matter
    if ($line -match '^\s*Flow\s+') { break }

    # CSharpTest or MultiTrialTest header
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
    else {
        $i++
    }
}

Write-Host "  Test blocks:  $($testBlocks.Count)"
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
    # Apply module-specific normalization rules from config
    foreach ($rule in $NormRules) {
        $n = $n -replace $rule.Pattern, $rule.Replacement
    }
    return $n
}

Write-Host "Symbolizing and deduplicating..."

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

#region ── deduplicate ────────────────────────────────────────────────────────
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

$uniqueCount = $groupOrder.Count
$totalBlocks = $testBlocks.Count
$dupRemoved  = $totalBlocks - $uniqueCount

Write-Host "  Total blocks:       $totalBlocks"
Write-Host "  Unique templates:   $uniqueCount"
Write-Host "  Duplicates removed: $dupRemoved"
Write-Host "  Block compression:  $([math]::Round(100.0 * $dupRemoved / [math]::Max(1,$totalBlocks), 1))%"
#endregion

#region ── emit BluePrint file ────────────────────────────────────────────────
$sb = [System.Text.StringBuilder]::new()

# Preamble kept verbatim
[void]$sb.AppendLine(($preambleLines -join "`n"))
[void]$sb.AppendLine("")

$groupIdx = 0
foreach ($key in $groupOrder) {
    $groupIdx++
    $members = $groups[$key]
    $representative = $members[0]

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

$sb.ToString() | Set-Content -Path $bpFile -Encoding UTF8 -NoNewline

$bpLines = [IO.File]::ReadAllLines($bpFile).Count
$origLines = $rawLines.Count
$lineReduction = [math]::Round(100.0 * (1 - $bpLines / [math]::Max(1, $origLines)), 1)

Write-Host "`nBluePrint: $bpFile"
Write-Host "  BP lines:     $bpLines (from $origLines, ${lineReduction}% reduction)"
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
[void]$pr.AppendLine("EXPANSION GROUPS")
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
                $cleanVal = $val -replace '\s*\(.*\)', ''   # strip parenthetical descriptions
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
