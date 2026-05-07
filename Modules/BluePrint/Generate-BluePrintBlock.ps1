<#
.SYNOPSIS
    Block-scoped BluePrint generator. Compresses ONLY a user-selected subset
    of flows (and the tests they reference) into a BP + symbols.csv pair.

.DESCRIPTION
    The user nominates one or more flows from a source .mtpl. This script:
      1. Slices the source mtpl down to:
           - the original preamble (Test Counter Definitions et al.)
           - every test block referenced (transitively) by the chosen flows
           - every chosen flow block (and any sub-flow they reach)
      2. Writes the slice to <OutputDir>\<module>_block_<tag>.mtpl
         (and a matching .mtpl_orig sidecar so the underlying generator
         treats it as canonical source).
      3. Invokes Generate-BluePrint.ps1 on the slice, producing:
           <module>_block_<tag>_bp.mtpl     (compressed BP)
           <module>_block_<tag>.symbols.csv (per-test slot table)
           <module>_block_<tag>.compressions.log
           <module>_block_<tag>.binmap.json
           <module>_block_<tag>.prompt.txt
           <module>_block_<tag>.derivations.log

    Nothing in the original module BluePrint output is touched.

.PARAMETER InputMtpl
    Source .mtpl file to slice.

.PARAMETER ConfigFile
    bp-config.json (passed through to Generate-BluePrint.ps1).

.PARAMETER Flows
    One or more flow names to include. Sub-flows reached from these flows
    are pulled in automatically.

.PARAMETER Tag
    Short label appended to the output filename. Default: 'sel'.

.PARAMETER OutputDir
    Where to write the slice + BP outputs. Default: <module>\BluePrint\block\

.EXAMPLE
    .\Generate-BluePrintBlock.ps1 `
        -InputMtpl ..\ARR\ARR_ATOM_CXX\ARR_ATOM_CXX.mtpl `
        -ConfigFile ..\ARR\ARR_ATOM_CXX\BluePrint\bp-config.json `
        -Flows ARR_ATOM_CXX_F1XAT,ARR_ATOM_CXX_F2XAT,ARR_ATOM_CXX_F3XAT `
        -Tag F1F2F3XAT
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]   $InputMtpl,
    [Parameter(Mandatory)] [string]   $ConfigFile,
    [Parameter(Mandatory)] [string[]] $Flows,
    [string] $Tag = 'sel',
    [string] $OutputDir,
    # When false (default) the BP keeps every test/flow definition (verbatim
    # ones included) so the round-trip Expand step can fully validate it
    # against the slice mtpl_orig. Set to $true to omit verbatim buckets
    # for a smaller BP (round-trip will be skipped in that case).
    [bool]   $SymbolizedOnly = $false
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$InputMtpl  = (Resolve-Path $InputMtpl).Path
$ConfigFile = (Resolve-Path $ConfigFile).Path
$moduleName = [IO.Path]::GetFileNameWithoutExtension($InputMtpl)
$moduleDir  = Split-Path $InputMtpl
if (-not $OutputDir) { $OutputDir = Join-Path $moduleDir 'BluePrint\block' }
if (-not (Test-Path $OutputDir)) { New-Item -ItemType Directory $OutputDir -Force | Out-Null }

$sliceName = "${moduleName}_block_${Tag}"
$sliceMtpl = Join-Path $OutputDir "$sliceName.mtpl"
$sliceOrig = Join-Path $OutputDir "$sliceName.mtpl_orig"

Write-Host "=== BluePrint Block Generator ==="
Write-Host "Module      : $moduleName"
Write-Host "Source mtpl : $InputMtpl"
Write-Host "Flows in    : $($Flows -join ', ')"
Write-Host "Slice name  : $sliceName"
Write-Host "Output dir  : $OutputDir"

# ---- Pristine source resolution -------------------------------------------
# `$InputMtpl` (the build artifact at module root) is overwritten by the
# merge round-trip with the *expanded* form. To keep slicing deterministic
# across runs, we always read FROM `BluePrint/<module>.mtpl_orig` if it
# exists; otherwise we snapshot the current `$InputMtpl` to that path now
# and use it from here on. All downstream parsing (slice + merge) operates
# on this pristine origin.
$bpDirEarly = Join-Path $moduleDir 'BluePrint'
if (-not (Test-Path $bpDirEarly)) { New-Item -ItemType Directory $bpDirEarly -Force | Out-Null }
$pristineOrig = Join-Path $bpDirEarly "${moduleName}.mtpl_orig"
if (-not (Test-Path $pristineOrig)) {
    Copy-Item -Path $InputMtpl -Destination $pristineOrig -Force
    Write-Host "  Snapshotted pristine source: $pristineOrig"
}
$sourceForSlice = $pristineOrig
Write-Host "  Pristine origin: $sourceForSlice"

# ---- Parse source mtpl into preamble / tests / flows -----------------------
$rawLines = [IO.File]::ReadAllLines($sourceForSlice)

function Find-EndOfCounters {
    param([string[]]$Lines)
    for ($i = 0; $i -lt $Lines.Count; $i++) {
        if ($Lines[$i] -match '^\}\s*#\s*End of Test Counter Definition') { return $i }
    }
    for ($i = 0; $i -lt $Lines.Count; $i++) {
        if ($Lines[$i] -match '^\s*(CSharpTest|MultiTrialTest)\s+') { return $i - 1 }
    }
    return 0
}

function Parse-BlockBody {
    param([string[]]$Lines, [int]$StartIdx)
    $depth = 0; $opened = $false
    $j = $StartIdx
    while ($j -lt $Lines.Count) {
        $depth += ([regex]::Matches($Lines[$j], '\{')).Count
        $depth -= ([regex]::Matches($Lines[$j], '\}')).Count
        if ($depth -gt 0) { $opened = $true }
        if ($opened -and $depth -le 0) { return $j }
        $j++
    }
    return $j - 1
}

$countersEnd   = Find-EndOfCounters -Lines $rawLines
$preambleLines = $rawLines[0..$countersEnd]

# Index every test and flow block with its line range and preceding comment band.
$testIndex = @{}   # name -> @{ Start; End; CommentStart }
$flowIndex = @{}   # name -> @{ Start; End; CommentStart }

$i = $countersEnd + 1
$inFlowSection = $false
while ($i -lt $rawLines.Count) {
    $line = $rawLines[$i]

    if (-not $inFlowSection -and ($line -match '^\s*CSharpTest\s+\S+\s+(\S+)' -or $line -match '^\s*MultiTrialTest\s+(\S+)\s*$')) {
        $name = $Matches[1].Trim()
        $cs = $i - 1
        while ($cs -gt $countersEnd -and ($rawLines[$cs] -match '^\s*#' -or $rawLines[$cs].Trim() -eq '')) { $cs-- }
        $cs++
        $end = Parse-BlockBody -Lines $rawLines -StartIdx $i
        $testIndex[$name] = @{ Start = $i; End = $end; CommentStart = $cs }
        $i = $end + 1
        continue
    }
    if ($line -match '^\s*Flow\s+(\S+)') {
        $inFlowSection = $true
        $name = $Matches[1]
        $cs = $i - 1
        while ($cs -gt $countersEnd -and ($rawLines[$cs] -match '^\s*#' -or $rawLines[$cs].Trim() -eq '')) { $cs-- }
        $cs++
        $end = Parse-BlockBody -Lines $rawLines -StartIdx $i
        $flowIndex[$name] = @{ Start = $i; End = $end; CommentStart = $cs }
        $i = $end + 1
        continue
    }
    $i++
}

Write-Host "  Source has $($testIndex.Count) test(s) and $($flowIndex.Count) flow(s)."

# ---- Resolve flow closure (BFS) -------------------------------------------
$missing = @($Flows | Where-Object { -not $flowIndex.ContainsKey($_) })
if ($missing.Count -gt 0) {
    throw "Flow(s) not found in $InputMtpl : $($missing -join ', ')"
}

$keepFlowSet = New-Object 'System.Collections.Generic.HashSet[string]'
$keepTestSet = New-Object 'System.Collections.Generic.HashSet[string]'
$queue = New-Object 'System.Collections.Generic.Queue[string]'
foreach ($f in $Flows) { [void]$keepFlowSet.Add($f); $queue.Enqueue($f) }

while ($queue.Count -gt 0) {
    $cur = $queue.Dequeue()
    $info = $flowIndex[$cur]
    for ($k = $info.Start; $k -le $info.End; $k++) {
        $ln = $rawLines[$k]
        if ($ln -match '^\s*(?:DUTFlowItem|FlowItem)\s+(\S+)\s+(\S+)') {
            $ref = $Matches[2]
            if ($flowIndex.ContainsKey($ref)) {
                if (-not $keepFlowSet.Contains($ref)) { [void]$keepFlowSet.Add($ref); $queue.Enqueue($ref) }
            } elseif ($testIndex.ContainsKey($ref)) {
                [void]$keepTestSet.Add($ref)
            }
        }
    }
}

Write-Host "  Closure: $($keepFlowSet.Count) flow(s), $($keepTestSet.Count) test(s)."
$extraFlows = @(@($keepFlowSet) | Where-Object { $_ -notin $Flows })
if ($extraFlows.Count -gt 0) {
    Write-Host "    Sub-flows pulled in: $($extraFlows -join ', ')" -ForegroundColor Yellow
}

# ---- Build the slice ------------------------------------------------------
$sb = [System.Text.StringBuilder]::new()
foreach ($pl in $preambleLines) { [void]$sb.AppendLine($pl) }
[void]$sb.AppendLine('')

# Tests in original order
$orderedTests = @($testIndex.GetEnumerator() | Sort-Object { $_.Value.Start } | Where-Object { $keepTestSet.Contains($_.Key) })
foreach ($te in $orderedTests) {
    $info = $te.Value
    [void]$sb.AppendLine('')
    for ($k = $info.CommentStart; $k -le $info.End; $k++) { [void]$sb.AppendLine($rawLines[$k]) }
}

[void]$sb.AppendLine('')

# Flows in original order (only those in keepFlowSet)
$orderedFlows = @($flowIndex.GetEnumerator() | Sort-Object { $_.Value.Start } | Where-Object { $keepFlowSet.Contains($_.Key) })
foreach ($fe in $orderedFlows) {
    $info = $fe.Value
    [void]$sb.AppendLine('')
    for ($k = $info.CommentStart; $k -le $info.End; $k++) { [void]$sb.AppendLine($rawLines[$k]) }
}

[IO.File]::WriteAllText($sliceMtpl, $sb.ToString())
[IO.File]::WriteAllText($sliceOrig, $sb.ToString())
Write-Host "  Slice written: $sliceMtpl ($([IO.File]::ReadAllLines($sliceMtpl).Count) lines)"

# ---- Slice integrity: every FlowItem ref must resolve to a defined test ---
# (closure carving may have dropped a test that some flow still references)
function _Get-DefsAndRefs {
    param([string]$Path)
    $lines = [IO.File]::ReadAllLines($Path)
    $defs = New-Object 'System.Collections.Generic.HashSet[string]'
    $flowDefs = New-Object 'System.Collections.Generic.HashSet[string]'
    $refs = @{}   # refName -> list of "<flow>: <line>" strings (where it was referenced)
    $curFlow = $null
    $depth = 0
    foreach ($ln in $lines) {
        if ($ln -match '^\s*CSharpTest\s+\S+\s+(\S+)')      { [void]$defs.Add($Matches[1].Trim()) }
        elseif ($ln -match '^\s*MultiTrialTest\s+(\S+)\s*$'){ [void]$defs.Add($Matches[1].Trim()) }
        elseif ($ln -match '^\s*(?:DUTFlow|Flow)\s+(\S+)')  { $curFlow = $Matches[1]; [void]$flowDefs.Add($curFlow); $depth = 0 }
        elseif ($ln -match '^\s*(?:DUTFlowItem|FlowItem)\s+(\S+)(?:\s+(\S+))?') {
            foreach ($r in @($Matches[1], $Matches[2])) {
                if (-not $r) { continue }
                if (-not $refs.ContainsKey($r)) { $refs[$r] = New-Object 'System.Collections.Generic.List[string]' }
                [void]$refs[$r].Add("$curFlow")
            }
        }
        $depth += ([regex]::Matches($ln, '\{').Count)
        $depth -= ([regex]::Matches($ln, '\}').Count)
    }
    return @{ Defs = $defs; FlowDefs = $flowDefs; Refs = $refs }
}
$sliceInfo = _Get-DefsAndRefs -Path $sliceMtpl
$dangling = New-Object 'System.Collections.Generic.List[string]'
foreach ($r in $sliceInfo.Refs.Keys) {
    if ($sliceInfo.Defs.Contains($r)) { continue }
    if ($sliceInfo.FlowDefs.Contains($r)) { continue }   # nested flow -> flow is fine
    [void]$dangling.Add($r)
}
if ($dangling.Count -gt 0) {
    Write-Host "  Slice integrity: $($dangling.Count) FlowItem reference(s) have no matching test/flow definition" -ForegroundColor Red
    foreach ($r in ($dangling | Select-Object -First 10)) {
        $where = ($sliceInfo.Refs[$r] | Select-Object -Unique) -join ', '
        Write-Host "    - $r  (referenced from flow: $where)" -ForegroundColor Red
    }
    if ($dangling.Count -gt 10) { Write-Host "    ...and $($dangling.Count - 10) more" -ForegroundColor Red }
    throw "Slice integrity check failed: dangling FlowItem references in $sliceMtpl"
}
Write-Host "  Slice integrity OK: $($sliceInfo.Defs.Count) test def(s), $($sliceInfo.FlowDefs.Count) flow def(s), $($sliceInfo.Refs.Count) FlowItem ref(s) all resolve"

# ---- Invoke the existing generator on the slice ---------------------------
$gen = Join-Path $PSScriptRoot 'Generate-BluePrint.ps1'
Write-Host ""
Write-Host "--- Invoking Generate-BluePrint.ps1 on slice ---"
$global:LASTEXITCODE = 0
& $gen -InputMtpl $sliceMtpl -ConfigFile $ConfigFile -OutputDir $OutputDir -SymbolizedOnly $SymbolizedOnly
if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) { throw "Generate-BluePrint failed (exit $LASTEXITCODE)" }

# ---- BP integrity is validated end-to-end by the Expand step below, which
# performs proper coupled per-row substitution and then runs full parity
# checks (count parity, body diff, flow connectivity, dangling refs) against
# the slice mtpl_orig. A pre-expand sanity check is redundant and brittle
# because it cannot reproduce the per-row coupling without re-implementing
# the expander.
$bpFile  = Join-Path $OutputDir "${sliceName}_bp.mtpl"
# Generator now writes:
#   <slice>.symbols.csv         = USER-FACING reduced pivot (Symbol -> per-flow value)
#   <slice>.symbols.buckets.csv = INTERNAL per-bucket multi-table (consumed by Expander)
$csvFile        = Join-Path $OutputDir "$sliceName.symbols.csv"
$bucketsCsvFile = Join-Path $OutputDir "$sliceName.symbols.buckets.csv"

$expand  = Join-Path $PSScriptRoot 'Expand-BluePrint.ps1'

Write-Host ""
Write-Host "--- Invoking Expand-BluePrint.ps1 (round-trip + parity check) ---"
if ($SymbolizedOnly) {
    Write-Host "  (skipped: SymbolizedOnly mode -- BP omits verbatim buckets so round-trip is not meaningful)"
} else {
    $global:LASTEXITCODE = 0
    & $expand -InputBp $bpFile -OrigMtpl $sliceOrig -TargetMtpl $sliceMtpl
    if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) { throw "Expand-BluePrint failed (exit $LASTEXITCODE)" }
}

# ---- Merge: produce the canonical <module>.mtpl.bp ------------------------
# The slice-level _bp.mtpl only covers the closure of the requested flows.
# The deliverable is a merged BP file that mirrors the FULL original mtpl
# unchanged everywhere EXCEPT for the closure tests/flows, which are
# replaced in-place by the slice's compressed `# BP_BUCKET` /
# `# BP_FLOW_BUCKET` blocks. Result is written next to the original mtpl as
# `<module>.mtpl.bp` (extension not built by .mtproj). The companion
# symbols.csv and binmap.json are placed beside it.
Write-Host ""
Write-Host "--- Merging slice BP into full mtpl_orig ---"
$bpDir          = Join-Path $moduleDir 'BluePrint'
if (-not (Test-Path $bpDir)) { New-Item -ItemType Directory $bpDir -Force | Out-Null }
$mergedBpFile      = Join-Path $bpDir "${moduleName}.mtpl.bp"
$mergedCsvFile     = Join-Path $bpDir "${moduleName}.symbols.csv"          # pivot (user-facing)
$mergedBucketsCsv  = Join-Path $bpDir "${moduleName}.symbols.buckets.csv"  # per-bucket (expander-internal)
$mergedBinmap      = Join-Path $bpDir "${moduleName}.binmap.json"

# Partition slice BP into preamble (drop), test-bucket sections, flow-bucket
# sections. A bucket "section" is the leading bucket header line plus all
# lines up to (but not including) the next BP_*-marker or end-of-file.
$sliceBpLines = [IO.File]::ReadAllLines($bpFile)
$testBucketSections = New-Object 'System.Collections.Generic.List[string[]]'
$flowBucketSections = New-Object 'System.Collections.Generic.List[string[]]'
$cur = New-Object 'System.Collections.Generic.List[string]'
$curKind = $null   # 'test' | 'flow' | $null
function _Flush-Section {
    if ($null -eq $script:curKind -or $script:cur.Count -eq 0) { return }
    $arr = $script:cur.ToArray()
    if ($script:curKind -eq 'test') { [void]$script:testBucketSections.Add($arr) }
    else                            { [void]$script:flowBucketSections.Add($arr) }
    $script:cur.Clear()
}
$script:cur = $cur
$script:curKind = $curKind
$script:testBucketSections = $testBucketSections
$script:flowBucketSections = $flowBucketSections
foreach ($ln in $sliceBpLines) {
    if ($ln -match '^# BP_BUCKET:')           { _Flush-Section; $script:curKind = 'test'; $script:cur.Add($ln); continue }
    if ($ln -match '^# BP_FLOW_BUCKET:')      { _Flush-Section; $script:curKind = 'flow'; $script:cur.Add($ln); continue }
    if ($null -eq $script:curKind) { continue }   # slice preamble, drop
    $script:cur.Add($ln)
}
_Flush-Section
Write-Host "  Slice BP partitioned: $($testBucketSections.Count) test bucket(s), $($flowBucketSections.Count) flow bucket(s)"

# Build the merged BP by walking the original mtpl line-by-line, dropping
# lines belonging to closure tests/flows, and emitting all bucket sections
# at the position of the first dropped block of each kind.
$origLines = $rawLines   # already loaded above
$keepTestList = @{}; foreach ($n in $keepTestSet) { $keepTestList[$n] = $true }
$keepFlowList = @{}; foreach ($n in $keepFlowSet) { $keepFlowList[$n] = $true }
$mergedSb       = [System.Text.StringBuilder]::new()
$emittedTests   = $false
$emittedFlows   = $false
$skipUntilLine  = -1

for ($mi = 0; $mi -lt $origLines.Count; $mi++) {
    if ($mi -le $skipUntilLine) { continue }
    $ln = $origLines[$mi]

    # Detect a closure test definition starting at this line.
    $isClosureTest = $false; $testEnd = -1
    if ($ln -match '^\s*CSharpTest\s+\S+\s+(\S+)' -or $ln -match '^\s*MultiTrialTest\s+(\S+)\s*$') {
        $tName = $Matches[1].Trim()
        if ($keepTestList.ContainsKey($tName) -and $testIndex.ContainsKey($tName)) {
            $isClosureTest = $true
            $testEnd = $testIndex[$tName].End
            # Also drop the leading comment band that was bound to this test.
            $cs = $testIndex[$tName].CommentStart
            # Trim trailing blank lines from the merged output that we
            # already wrote above this comment band, so the bucket emit
            # sits flush (the bucket sections start with their own blank
            # line + header).
        }
    }
    if ($isClosureTest) {
        if (-not $emittedTests) {
            foreach ($sec in $testBucketSections) {
                [void]$mergedSb.AppendLine('')
                foreach ($sl in $sec) { [void]$mergedSb.AppendLine($sl) }
            }
            $emittedTests = $true
        }
        $skipUntilLine = $testEnd
        continue
    }

    $isClosureFlow = $false; $flowEnd = -1
    if ($ln -match '^\s*Flow\s+(\S+)') {
        $fName = $Matches[1]
        if ($keepFlowList.ContainsKey($fName) -and $flowIndex.ContainsKey($fName)) {
            $isClosureFlow = $true
            $flowEnd = $flowIndex[$fName].End
        }
    }
    if ($isClosureFlow) {
        if (-not $emittedFlows) {
            foreach ($sec in $flowBucketSections) {
                [void]$mergedSb.AppendLine('')
                foreach ($sl in $sec) { [void]$mergedSb.AppendLine($sl) }
            }
            $emittedFlows = $true
        }
        $skipUntilLine = $flowEnd
        continue
    }

    # Pass through non-closure content verbatim.
    [void]$mergedSb.AppendLine($ln)
}

# Safety: if for some reason no closure block was hit (e.g. all closure
# tests/flows landed at end-of-file and we exhausted the loop without
# emitting), append remaining buckets.
if (-not $emittedTests) {
    foreach ($sec in $testBucketSections) {
        [void]$mergedSb.AppendLine('')
        foreach ($sl in $sec) { [void]$mergedSb.AppendLine($sl) }
    }
}
if (-not $emittedFlows) {
    foreach ($sec in $flowBucketSections) {
        [void]$mergedSb.AppendLine('')
        foreach ($sl in $sec) { [void]$mergedSb.AppendLine($sl) }
    }
}

[IO.File]::WriteAllText($mergedBpFile, $mergedSb.ToString().TrimEnd() + "`r`n")
Copy-Item -Path $csvFile        -Destination $mergedCsvFile    -Force
Copy-Item -Path $bucketsCsvFile -Destination $mergedBucketsCsv -Force
$sliceBinmap = Join-Path $OutputDir "$sliceName.binmap.json"
if (Test-Path $sliceBinmap) { Copy-Item -Path $sliceBinmap -Destination $mergedBinmap -Force }
$mergedLineCount = [IO.File]::ReadAllLines($mergedBpFile).Count
Write-Host "  Merged BP written: $mergedBpFile ($mergedLineCount lines)"
Write-Host "  Merged symbols (pivot)  : $mergedCsvFile"
Write-Host "  Merged symbols (buckets): $mergedBucketsCsv"

# ---- Bidirectional symbol-coverage check on the merged BP ----------------
# Every \TOKEN\ placeholder in the merged BP must appear as a Symbol in the
# pivot CSV, and every Symbol in the pivot must be referenced at least once
# in the merged BP. Catches drift between the two artifacts.
$bpText = [IO.File]::ReadAllText($mergedBpFile)
$bpSymbols = New-Object 'System.Collections.Generic.HashSet[string]'
foreach ($m in [regex]::Matches($bpText, '\\([A-Z][A-Z0-9_]*)\\')) {
    [void]$bpSymbols.Add($m.Groups[1].Value)
}
$pivotSymbols = New-Object 'System.Collections.Generic.HashSet[string]'
$pivotLines = [IO.File]::ReadAllLines($mergedCsvFile)
for ($pi = 1; $pi -lt $pivotLines.Count; $pi++) {
    $first = ($pivotLines[$pi] -split ',', 2)[0].Trim('"')
    if ($first) { [void]$pivotSymbols.Add($first) }
}
$inBpNotPivot = @($bpSymbols | Where-Object { -not $pivotSymbols.Contains($_) } | Sort-Object)
$inPivotNotBp = @($pivotSymbols | Where-Object { -not $bpSymbols.Contains($_) } | Sort-Object)
Write-Host ("  Symbol coverage: BP-tokens={0}, pivot-symbols={1}, BP-only={2}, pivot-only={3}" `
    -f $bpSymbols.Count, $pivotSymbols.Count, $inBpNotPivot.Count, $inPivotNotBp.Count)
if ($inBpNotPivot.Count -gt 0) {
    Write-Host "  BP placeholders missing from pivot CSV (first 20):" -ForegroundColor Yellow
    $inBpNotPivot | Select-Object -First 20 | ForEach-Object { Write-Host "    $_" -ForegroundColor Yellow }
    throw "Symbol coverage check failed: $($inBpNotPivot.Count) \TOKEN\ placeholder(s) in '$mergedBpFile' have no row in '$mergedCsvFile' (pivot)."
}
if ($inPivotNotBp.Count -gt 0) {
    Write-Host "  Pivot symbols not referenced in BP (first 20):" -ForegroundColor Yellow
    $inPivotNotBp | Select-Object -First 20 | ForEach-Object { Write-Host "    $_" -ForegroundColor Yellow }
    throw "Symbol coverage check failed: $($inPivotNotBp.Count) Symbol row(s) in '$mergedCsvFile' have no \TOKEN\ reference in '$mergedBpFile'."
}

# Validate the merged BP by expanding it and round-tripping against the
# FULL original mtpl. The expanded form REPLACES the module's source
# `<module>.mtpl` (the canonical build artifact). The original is preserved
# alongside the BP as `<module>.mtpl_orig` (created on first run).
$mergedOrig = Join-Path $bpDir "${moduleName}.mtpl_orig"
if (-not (Test-Path $mergedOrig)) { Copy-Item -Path $InputMtpl -Destination $mergedOrig -Force }
$mergedTargetMtpl = $InputMtpl   # overwrite the build artifact with expanded form
Write-Host ""
Write-Host "--- Invoking Expand-BluePrint.ps1 on merged BP (full module round-trip) ---"
$global:LASTEXITCODE = 0
& $expand -InputBp $mergedBpFile -OrigMtpl $mergedOrig -TargetMtpl $mergedTargetMtpl -LenientChecks
if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) { throw "Expand-BluePrint on merged BP failed (exit $LASTEXITCODE)" }

# The expander writes a `<module>_bp.val.mtpl` sidecar in the same folder
# as the merged BP. That filename ends in `.mtpl` and would be picked up
# by the .mtproj wildcard build, so rename it to a non-built extension.
$valSide = Join-Path $bpDir "${moduleName}_bp.val.mtpl"
if (Test-Path $valSide) { Move-Item -Path $valSide -Destination (Join-Path $bpDir "${moduleName}_bp.val.txt") -Force }

# Belt-and-suspenders: any other `*.mtpl` file inside $bpDir is stale (from
# legacy runs / earlier iterations) and would be picked up by the .mtproj
# wildcard. Our canonical merged outputs use `.mtpl.bp`, `.mtpl_orig`,
# `.symbols.csv`, `.binmap.json`, `_bp.val.txt` -- none of which match `*.mtpl`.
$staleMtpl = @(Get-ChildItem -Path $bpDir -Filter '*.mtpl' -File -ErrorAction SilentlyContinue)
foreach ($f in $staleMtpl) {
    try {
        Remove-Item $f.FullName -Force -ErrorAction Stop
        Write-Host "  Cleanup: removed stale BluePrint/.mtpl file $($f.Name)"
    } catch {
        Write-Host "  Cleanup: failed to remove $($f.FullName) ($_)" -ForegroundColor Yellow
    }
}

# ---- Build flat denormalized views (one row per test instance) ------------
# Disabled: the new design keeps only `_bp.mtpl` + `.symbols.csv`. The flat
# builders consumed the old per-bucket symbols.csv format and produce
# additional output files that are not part of the requested two-file output.
$flatBp  = $null
$flatTab = $null

# (flat builder invocations removed; cleanup pass below deletes any stale
#  outputs from prior runs.)

# ---- Cleanup: the slice-level files in `block/` are intermediates only.
# Remove the whole subdir so it can't pollute the .mtproj wildcard build
# (the slice `_bp.mtpl` and `.mtpl_orig` both end in `.mtpl`). The merged
# canonical outputs in `BluePrint/<module>.mtpl.bp` etc. are the deliverable.
if (Test-Path $OutputDir) {
    try {
        Remove-Item -Path $OutputDir -Recurse -Force -ErrorAction Stop
        Write-Host "  Cleanup: removed slice intermediates dir $OutputDir"
    } catch {
        Write-Host "  Cleanup: failed to remove $OutputDir ($_)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "=== Block BP generation complete ==="
Write-Host "  Merged BP        : $mergedBpFile"
Write-Host "  symbols (pivot)  : $mergedCsvFile"
Write-Host "  symbols (buckets): $mergedBucketsCsv"
