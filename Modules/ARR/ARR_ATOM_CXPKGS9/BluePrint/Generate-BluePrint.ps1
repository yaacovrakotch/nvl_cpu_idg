<#
.SYNOPSIS
    Transforms an NVL .mtpl file into a BluePrint (BP) file + corresponding prompt.

.DESCRIPTION
    IDG-aligned blueprint generator.  The PPT (ww16 2026) defines a blueprint as:
      "a minimized, symbolized version of the full module MTPL file"
    with symbols enclosed in backslashes \SYMBOL\.

    Algorithm:
      1. Parse the .mtpl into a preamble (header + Counters) and test blocks.
      2. Apply symbol replacements — literal find/replace of all known symbol values.
      3. Normalise blocks so that only-cosmetic diffs (BaseNumbers) vanish.
      4. Group identical normalised blocks; keep one representative per group.
      5. Emit the BluePrint (.mtpl.bp) and a companion prompt (.prompt.txt).

.PARAMETER InputMtpl
    Path to the source .mtpl file.

.PARAMETER OutputDir
    Directory for the output files.  Defaults to .\BluePrint next to the input.

.EXAMPLE
    .\Generate-BluePrint.ps1 -InputMtpl "..\ARR_ATOM_CXPKGS9.mtpl"
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$InputMtpl,
    [string]$OutputDir
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

#region ── paths ──────────────────────────────────────────────────────────────
$InputMtpl  = (Resolve-Path $InputMtpl).Path
$moduleName = [IO.Path]::GetFileNameWithoutExtension($InputMtpl)
if (-not $OutputDir) { $OutputDir = Join-Path (Split-Path $InputMtpl) 'BluePrint' }
if (-not (Test-Path $OutputDir)) { New-Item -ItemType Directory $OutputDir -Force | Out-Null }

$bpFile     = Join-Path $OutputDir "$moduleName.mtpl.bp"
$promptFile = Join-Path $OutputDir "$moduleName.prompt.txt"
Write-Host "Input : $InputMtpl"
Write-Host "Output: $OutputDir"
#endregion

#region ── read file ──────────────────────────────────────────────────────────
$rawLines = [IO.File]::ReadAllLines($InputMtpl)
Write-Host "  Lines: $($rawLines.Count)"
#endregion

#region ── symbol replacement table ───────────────────────────────────────────
# Each entry: ordered list of [find, replace] pairs.
# Replacements are applied in order, so put longer / more-specific patterns first.
# The PPT dictates backslash-delimited symbols: \corner\, \FlowType\ etc.

$symbolDefs = [ordered]@{}   # symbol name -> @{ Description; Values }

# Helper to register a symbol and return its replacement pairs
function New-Symbol {
    param(
        [string]$Name,
        [string]$Description,
        [string[]]$Values,
        [hashtable[]]$Pairs      # @{ Find='...'; Replace='...' }
    )
    $script:symbolDefs[$Name] = @{ Description = $Description; Values = $Values }
    return $Pairs
}

$allReplacements = @()

# --- FREQ_CORNER (F1-F4) -------------------------------------------------
$allReplacements += New-Symbol -Name 'FREQ_CORNER' `
    -Description 'Frequency corner for VMIN search tests. F1 is the lowest standard corner, F4 the highest.' `
    -Values @('F1','F2','F3','F4') `
    -Pairs @(
        # test-name level (upper case)
        @{Find='F1XAT'; Replace='\FREQ_CORNER\XAT'},
        @{Find='F2XAT'; Replace='\FREQ_CORNER\XAT'},
        @{Find='F3XAT'; Replace='\FREQ_CORNER\XAT'},
        @{Find='F4XAT'; Replace='\FREQ_CORNER\XAT'},
        @{Find='_VCCIA_F1_'; Replace='_VCCIA_\FREQ_CORNER\_'},
        @{Find='_VCCIA_F2_'; Replace='_VCCIA_\FREQ_CORNER\_'},
        @{Find='_VCCIA_F3_'; Replace='_VCCIA_\FREQ_CORNER\_'},
        @{Find='_VCCIA_F4_'; Replace='_VCCIA_\FREQ_CORNER\_'},
        # FlowMatrix / CustomFlowMatrix references
        @{Find='AT_F1_FREQ_MHz'; Replace='AT_\FREQ_CORNER\_FREQ_MHz'},
        @{Find='AT_F2_FREQ_MHz'; Replace='AT_\FREQ_CORNER\_FREQ_MHz'},
        @{Find='AT_F3_FREQ_MHz'; Replace='AT_\FREQ_CORNER\_FREQ_MHz'},
        @{Find='AT_F4_FREQ_MHz'; Replace='AT_\FREQ_CORNER\_FREQ_MHz'},
        @{Find='AT_F1_FREQ'; Replace='AT_\FREQ_CORNER\_FREQ'},
        @{Find='AT_F2_FREQ'; Replace='AT_\FREQ_CORNER\_FREQ'},
        @{Find='AT_F3_FREQ'; Replace='AT_\FREQ_CORNER\_FREQ'},
        @{Find='AT_F4_FREQ'; Replace='AT_\FREQ_CORNER\_FREQ'},
        # DROPOUT expressions
        @{Find='DROPOUT.AT_F1'; Replace='DROPOUT.AT_\FREQ_CORNER\'},
        @{Find='DROPOUT.AT_F2'; Replace='DROPOUT.AT_\FREQ_CORNER\'},
        @{Find='DROPOUT.AT_F3'; Replace='DROPOUT.AT_\FREQ_CORNER\'},
        @{Find='DROPOUT.AT_F4'; Replace='DROPOUT.AT_\FREQ_CORNER\'},
        # CornerIdentifiers @Fn
        @{Find='@F1'; Replace='@\FREQ_CORNER\'},
        @{Find='@F2'; Replace='@\FREQ_CORNER\'},
        @{Find='@F3'; Replace='@\FREQ_CORNER\'},
        @{Find='@F4'; Replace='@\FREQ_CORNER\'},
        # StartVoltagesForRetry / Offset
        @{Find='ForRetryF1'; Replace='ForRetry\FREQ_CORNER\'},
        @{Find='ForRetryF2'; Replace='ForRetry\FREQ_CORNER\'},
        @{Find='ForRetryF3'; Replace='ForRetry\FREQ_CORNER\'},
        @{Find='ForRetryF4'; Replace='ForRetry\FREQ_CORNER\'},
        @{Find='OffsetF1'; Replace='Offset\FREQ_CORNER\'},
        @{Find='OffsetF2'; Replace='Offset\FREQ_CORNER\'},
        @{Find='OffsetF3'; Replace='Offset\FREQ_CORNER\'},
        @{Find='OffsetF4'; Replace='Offset\FREQ_CORNER\'},
        # VminResult
        @{Find='F1_VMIN'; Replace='\FREQ_CORNER\_VMIN'},
        @{Find='F2_VMIN'; Replace='\FREQ_CORNER\_VMIN'},
        @{Find='F3_VMIN'; Replace='\FREQ_CORNER\_VMIN'},
        @{Find='F4_VMIN'; Replace='\FREQ_CORNER\_VMIN'},
        # patlist lower-case frequency identifiers
        @{Find='f1xat'; Replace='\freq_corner\xat'},
        @{Find='f2xat'; Replace='\freq_corner\xat'},
        @{Find='f3xat'; Replace='\freq_corner\xat'},
        @{Find='f4xat'; Replace='\freq_corner\xat'},
        @{Find='_f1_'; Replace='_\freq_corner\_'},
        @{Find='_f2_'; Replace='_\freq_corner\_'},
        @{Find='_f3_'; Replace='_\freq_corner\_'},
        @{Find='_f4_'; Replace='_\freq_corner\_'}
    )

# --- COVERAGE_TYPE (COMBINED / SSA / SSA_L2DATA / MEC) --------------------
$allReplacements += New-Symbol -Name 'COVERAGE_TYPE' `
    -Description 'Coverage variant for array tests: COMBINED=all arrays, SSA=single-sided only, SSA_L2DATA=L2 data arrays, MEC=maximum error count.' `
    -Values @('COMBINED','SSA','SSA_L2DATA','MEC') `
    -Pairs @(
        # Longer match first to avoid partial replacement
        @{Find='_SSA_L2DATA'; Replace='_\COVERAGE_TYPE\'},
        @{Find='_COMBINED';   Replace='_\COVERAGE_TYPE\'},
        @{Find='_SSA';        Replace='_\COVERAGE_TYPE\'},
        @{Find='_MEC';        Replace='_\COVERAGE_TYPE\'}
    )

# --- MODULE_INDEX (M0-M3 for raster repair pipeline) ---------------------
$allReplacements += New-Symbol -Name 'MODULE_INDEX' `
    -Description 'L2 cache module index (M0-M3). Each physical module is tested independently in the raster repair pipeline.' `
    -Values @('M0','M1','M2','M3') `
    -Pairs @(
        @{Find='_M0_1';  Replace='_\MODULE_INDEX\_1'},
        @{Find='_M1_1';  Replace='_\MODULE_INDEX\_1'},
        @{Find='_M2_1';  Replace='_\MODULE_INDEX\_1'},
        @{Find='_M3_1';  Replace='_\MODULE_INDEX\_1'},
        @{Find='_M0_REP2FUSE'; Replace='_\MODULE_INDEX\_REP2FUSE'},
        @{Find='_M1_REP2FUSE'; Replace='_\MODULE_INDEX\_REP2FUSE'},
        @{Find='_M2_REP2FUSE'; Replace='_\MODULE_INDEX\_REP2FUSE'},
        @{Find='_M3_REP2FUSE'; Replace='_\MODULE_INDEX\_REP2FUSE'},
        @{Find='_M3_CPU1'; Replace='_\MODULE_INDEX\_CPU1'},
        # BypassPort SCBD references
        @{Find='SCBD_0_0_0_0'; Replace='SCBD_\MODULE_INDEX_NUM\_0_0_0'},
        @{Find='SCBD_1_0_0_0'; Replace='SCBD_\MODULE_INDEX_NUM\_0_0_0'},
        @{Find='SCBD_2_0_0_0'; Replace='SCBD_\MODULE_INDEX_NUM\_0_0_0'},
        @{Find='SCBD_3_0_0_0'; Replace='SCBD_\MODULE_INDEX_NUM\_0_0_0'},
        # DecoderMatchLabel
        @{Find='"module0"'; Replace='"\MODULE_INDEX\"'},
        @{Find='"module1"'; Replace='"\MODULE_INDEX\"'},
        @{Find='"module2"'; Replace='"\MODULE_INDEX\"'},
        @{Find='"module3"'; Replace='"\MODULE_INDEX\"'},
        # SharedStorage keys
        @{Find='L2DATAMINM0'; Replace='L2DATA\VOLTAGE_CORNER\\MODULE_INDEX\'},
        @{Find='L2DATAMINM1'; Replace='L2DATA\VOLTAGE_CORNER\\MODULE_INDEX\'},
        @{Find='L2DATAMINM2'; Replace='L2DATA\VOLTAGE_CORNER\\MODULE_INDEX\'},
        @{Find='L2DATAMINM3'; Replace='L2DATA\VOLTAGE_CORNER\\MODULE_INDEX\'},
        @{Find='L2DATAMAXM0'; Replace='L2DATA\VOLTAGE_CORNER\\MODULE_INDEX\'},
        @{Find='L2DATAMAXM1'; Replace='L2DATA\VOLTAGE_CORNER\\MODULE_INDEX\'},
        @{Find='L2DATAMAXM2'; Replace='L2DATA\VOLTAGE_CORNER\\MODULE_INDEX\'},
        @{Find='L2DATAMAXM3'; Replace='L2DATA\VOLTAGE_CORNER\\MODULE_INDEX\'},
        @{Find='L2TAGMINM0';  Replace='L2TAG\VOLTAGE_CORNER\\MODULE_INDEX\'},
        @{Find='L2TAGMINM1';  Replace='L2TAG\VOLTAGE_CORNER\\MODULE_INDEX\'},
        @{Find='L2TAGMINM2';  Replace='L2TAG\VOLTAGE_CORNER\\MODULE_INDEX\'},
        @{Find='L2TAGMINM3';  Replace='L2TAG\VOLTAGE_CORNER\\MODULE_INDEX\'},
        @{Find='L2TAGMAXM0';  Replace='L2TAG\VOLTAGE_CORNER\\MODULE_INDEX\'},
        @{Find='L2TAGMAXM1';  Replace='L2TAG\VOLTAGE_CORNER\\MODULE_INDEX\'},
        @{Find='L2TAGMAXM2';  Replace='L2TAG\VOLTAGE_CORNER\\MODULE_INDEX\'},
        @{Find='L2TAGMAXM3';  Replace='L2TAG\VOLTAGE_CORNER\\MODULE_INDEX\'},
        # patlist module tags
        @{Find='_m0_'; Replace='_\module_index\_'},
        @{Find='_m1_'; Replace='_\module_index\_'},
        @{Find='_m2_'; Replace='_\module_index\_'},
        @{Find='_m3_'; Replace='_\module_index\_'}
    )

# --- CPU_DIE --------------------------------------------------------------
$allReplacements += New-Symbol -Name 'CPU_DIE' `
    -Description 'CPU die selector. Tests are duplicated for the second die with _CPU1 suffix. CPU0=no suffix.' `
    -Values @('CPU0 (no suffix)','CPU1 (_CPU1 suffix)') `
    -Pairs @(
        @{Find='_CPU1'; Replace='_\CPU_DIE\'}
    )

# --- PMUX_INDEX (0-3 for RunCallback freq tests) -------------------------
$allReplacements += New-Symbol -Name 'PMUX_INDEX' `
    -Description 'Power-mux callback index (0-3), one per ATOM compute cluster.' `
    -Values @('0','1','2','3') `
    -Pairs @(
        @{Find='PMUX_CO_FREQ0'; Replace='PMUX_CO_FREQ\PMUX_INDEX\'},
        @{Find='PMUX_CO_FREQ1'; Replace='PMUX_CO_FREQ\PMUX_INDEX\'},
        @{Find='PMUX_CO_FREQ2'; Replace='PMUX_CO_FREQ\PMUX_INDEX\'},
        @{Find='PMUX_CO_FREQ3'; Replace='PMUX_CO_FREQ\PMUX_INDEX\'},
        @{Find='CDIE_ATOM0_FREQ';  Replace='CDIE_ATOM\PMUX_INDEX\_FREQ'},
        @{Find='CDIE_ATOM1_FREQ';  Replace='CDIE_ATOM\PMUX_INDEX\_FREQ'},
        @{Find='CDIE_ATOM2_FREQ';  Replace='CDIE_ATOM\PMUX_INDEX\_FREQ'},
        @{Find='CDIE_ATOM3_FREQ';  Replace='CDIE_ATOM\PMUX_INDEX\_FREQ'},
        @{Find='_CDIEATOM0_CO_FREQ'; Replace='_CDIEATOM\PMUX_INDEX\_CO_FREQ'},
        @{Find='_CDIEATOM1_CO_FREQ'; Replace='_CDIEATOM\PMUX_INDEX\_CO_FREQ'},
        @{Find='_CDIEATOM2_CO_FREQ'; Replace='_CDIEATOM\PMUX_INDEX\_CO_FREQ'},
        @{Find='_CDIEATOM3_CO_FREQ'; Replace='_CDIEATOM\PMUX_INDEX\_CO_FREQ'}
    )

# --- VOLTAGE_CORNER (MIN/MAX for raster tests) ---------------------------
$allReplacements += New-Symbol -Name 'VOLTAGE_CORNER' `
    -Description 'Voltage corner for raster capture/repair tests. MIN=minimum voltage, MAX=maximum voltage.' `
    -Values @('MIN','MAX') `
    -Pairs @(
        @{Find='VCCIA_MIN_X'; Replace='VCCIA_\VOLTAGE_CORNER\_X'},
        @{Find='VCCIA_MAX_X'; Replace='VCCIA_\VOLTAGE_CORNER\_X'}
    )

# --- SSA_ARRAY_TYPE (L2_DATA / L2_TAG in SSA raster) ---------------------
$allReplacements += New-Symbol -Name 'SSA_ARRAY_TYPE' `
    -Description 'SSA array type: L2_DATA covers data arrays, L2_TAG covers tag arrays.' `
    -Values @('L2_DATA','L2_TAG') `
    -Pairs @(
        @{Find='_L2_DATA_'; Replace='_\SSA_ARRAY_TYPE\_'},
        @{Find='_L2_TAG_';  Replace='_\SSA_ARRAY_TYPE\_'},
        @{Find='l2_data';   Replace='\ssa_array_type\'},
        @{Find='l2_tag';    Replace='\ssa_array_type\'}
    )

# --- LSA_ARRAY_TYPE (L2_C6 / L2_LRU / L2_STATE) -------------------------
$allReplacements += New-Symbol -Name 'LSA_ARRAY_TYPE' `
    -Description 'LSA array type: L2_C6 (C6 retention), L2_LRU (least recently used), L2_STATE (state arrays).' `
    -Values @('L2_C6','L2_LRU','L2_STATE') `
    -Pairs @(
        @{Find='_L2_C6_';    Replace='_\LSA_ARRAY_TYPE\_'},
        @{Find='_L2_LRU_';   Replace='_\LSA_ARRAY_TYPE\_'},
        @{Find='_L2_STATE_'; Replace='_\LSA_ARRAY_TYPE\_'},
        @{Find='l2_c6';      Replace='\lsa_array_type\'},
        @{Find='l2_lru';     Replace='\lsa_array_type\'},
        @{Find='l2_state';   Replace='\lsa_array_type\'}
    )

# --- REP_DIRECTION (VMIN/VMAX for repair flag tests) ---------------------
$allReplacements += New-Symbol -Name 'REP_DIRECTION' `
    -Description 'Repair direction: VMIN-side vs VMAX-side repair flag.' `
    -Values @('VMIN','VMAX') `
    -Pairs @(
        @{Find='VMAXREP'; Replace='\REP_DIRECTION\REP'},
        @{Find='VMINREP'; Replace='\REP_DIRECTION\REP'}
    )

# --- L2_ENDCPU_TYPE (TAG/DATA for L2 ENDCPU tests) ----------------------
$allReplacements += New-Symbol -Name 'L2_ENDCPU_TYPE' `
    -Description 'L2 sub-array tested at ENDCPU: TAG or DATA.' `
    -Values @('TAG','DATA') `
    -Pairs @(
        @{Find='_X_L2_TAG';  Replace='_X_L2_\L2_ENDCPU_TYPE\'},
        @{Find='_X_L2_DATA'; Replace='_X_L2_\L2_ENDCPU_TYPE\'}
    )

# --- HRY_PHASE (PRE/POST for HRY array tests) ---------------------------
$allReplacements += New-Symbol -Name 'HRY_PHASE' `
    -Description 'HRY test phase: PRE runs before repair, POST runs after repair.' `
    -Values @('PRE','POST') `
    -Pairs @(
        @{Find='_X_PRE';  Replace='_X_\HRY_PHASE\'},
        @{Find='_X_POST'; Replace='_X_\HRY_PHASE\'}
    )

# --- RASTERLOOP_TYPE -----------------------------------------------------
$allReplacements += New-Symbol -Name 'RASTERLOOP_TYPE' `
    -Description 'PatConfig raster loop type: VMAXRASTERLOOP or VMINRASTERLOOP.' `
    -Values @('VMAXRASTERLOOP','VMINRASTERLOOP') `
    -Pairs @(
        @{Find='VMAXRASTERLOOP'; Replace='\RASTERLOOP_TYPE\'},
        @{Find='VMINRASTERLOOP'; Replace='\RASTERLOOP_TYPE\'}
    )

Write-Host "  Defined $($symbolDefs.Count) symbols with $($allReplacements.Count) replacement pairs"
#endregion

#region ── parse blocks ───────────────────────────────────────────────────────
# Split the file into: preamble (everything up to end of Counters block)
#                       test blocks (CSharpTest / MultiTrialTest)

function Find-EndOfCounters {
    param([string[]]$Lines)
    for ($i = 0; $i -lt $Lines.Count; $i++) {
        if ($Lines[$i] -match '^\}\s*#\s*End of Test Counter Definition') {
            return $i
        }
    }
    # fallback: find first CSharpTest/MultiTrialTest
    for ($i = 0; $i -lt $Lines.Count; $i++) {
        if ($Lines[$i] -match '^\s*(CSharpTest|MultiTrialTest)\s+') {
            return $i - 1
        }
    }
    return 0
}

$countersEnd = Find-EndOfCounters -Lines $rawLines
$preambleLines = $rawLines[0..$countersEnd]
Write-Host "  Preamble: lines 0..$countersEnd"

# Parse test blocks from remaining lines
$testBlocks = [System.Collections.Generic.List[PSCustomObject]]::new()

$i = $countersEnd + 1
while ($i -lt $rawLines.Count) {
    $line = $rawLines[$i]

    # CSharpTest or MultiTrialTest header
    if ($line -match '^\s*(CSharpTest|MultiTrialTest)\s+(\S+)\s+(.+)$') {
        $testType     = $Matches[1]
        $templateName = $Matches[2]
        $instanceName = $Matches[3].Trim()

        # collect preceding comment lines (# ...) that belong to this block
        $commentLines = [System.Collections.Generic.List[string]]::new()
        $k = $i - 1
        while ($k -gt $countersEnd -and $rawLines[$k] -match '^\s*(#|$)') {
            if ($rawLines[$k].Trim()) { $commentLines.Insert(0, $rawLines[$k]) }
            $k--
        }

        # collect from current line to matching close-brace
        $startIdx = $i
        $depth = 0
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
            StartLine    = $startIdx
            EndLine      = $j
        })
        $i = $j + 1
    }
    else {
        $i++
    }
}

Write-Host "  Test blocks: $($testBlocks.Count)"
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
    param([string]$Text)
    # Strip BaseNumbers (unique per test, not a symbol)
    $n = $Text -replace 'BaseNumbers\s*=\s*"[^"]*"', 'BaseNumbers = "\BASE_NUMBER\"'
    # Strip FuseNamespace (varies by CPU die)
    $n = $n -replace 'FuseNamespace\s*=\s*"[^"]*"', 'FuseNamespace = "\FUSE_NAMESPACE\"'
    # Strip PostInstance GSDS key differences (CPU0/CPU1 vary)
    $n = $n -replace 'UnrepairabledSsiKey\w+', 'UnrepairabledSsiKey\CPU_DIE\'
    return $n
}

Write-Host "Symbolizing and deduplicating..."

$processed = foreach ($block in $testBlocks) {
    $symbolized = Apply-Replacements -Text $block.RawText -Pairs $allReplacements
    $normalized = Normalize-ForDedup -Text $symbolized
    [PSCustomObject]@{
        Block          = $block
        SymbolizedText = $symbolized
        NormalizedKey  = $normalized.Trim()
    }
}
#endregion

#region ── deduplicate ────────────────────────────────────────────────────────
$groups = [ordered]@{}
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

Write-Host "  Total blocks:      $totalBlocks"
Write-Host "  Unique templates:  $uniqueCount"
Write-Host "  Duplicates removed: $dupRemoved"
Write-Host "  Compression:       $([math]::Round(100.0 * $dupRemoved / [math]::Max(1,$totalBlocks), 1))%"
#endregion

#region ── emit BluePrint file ────────────────────────────────────────────────
$sb = [System.Text.StringBuilder]::new()

# Preamble (header + counters kept as-is per user request)
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
Write-Host "`nBluePrint: $bpFile"
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

    # Detect which symbols actually vary
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

[void]$pr.AppendLine("")
[void]$pr.AppendLine("-" * 80)
[void]$pr.AppendLine("NOTES")
[void]$pr.AppendLine("-" * 80)
[void]$pr.AppendLine("- Counters section is kept verbatim from the original file.")
[void]$pr.AppendLine("- BaseNumbers are unique per instance; assign sequentially when expanding.")
[void]$pr.AppendLine("- Tests with _CPU1 suffix duplicate the base test for the second compute die.")
[void]$pr.AppendLine("- F5 corner uses a different trial variable (ATOM_TOP) and freq references")
[void]$pr.AppendLine("  (Corners.AT_C5, FreqValues.AT_C5) - kept as a separate template.")
[void]$pr.AppendLine("- FMIN corner uses different timing TC and voltage forwarding from F1 results.")
[void]$pr.AppendLine("- When generating a product-specific MTPL, consult the Test Plan Wiki for")
[void]$pr.AppendLine("  the actual symbol values (frequencies, voltage limits, etc).")

$pr.ToString() | Set-Content -Path $promptFile -Encoding UTF8 -NoNewline
Write-Host "Prompt:    $promptFile"
#endregion

Write-Host ""
Write-Host "=== Done ==="
Write-Host "  Original: $totalBlocks blocks, $($rawLines.Count) lines"
Write-Host "  BluePrint: $uniqueCount blocks ($('{0:N1}' -f (100.0 * $dupRemoved / [math]::Max(1,$totalBlocks)))% reduction)"
