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
    # When true (default) the BP file omits verbatim (non-symbolized) buckets.
    # In that mode the round-trip Expand step is also skipped (Expand cannot
    # rebuild a partial BP). Set to $false for full BP + parity validation.
    [bool]   $SymbolizedOnly = $true
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

# ---- Parse source mtpl into preamble / tests / flows -----------------------
$rawLines = [IO.File]::ReadAllLines($InputMtpl)

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

# ---- Invoke the existing generator on the slice ---------------------------
$gen = Join-Path $PSScriptRoot 'Generate-BluePrint.ps1'
Write-Host ""
Write-Host "--- Invoking Generate-BluePrint.ps1 on slice ---"
$global:LASTEXITCODE = 0
& $gen -InputMtpl $sliceMtpl -ConfigFile $ConfigFile -OutputDir $OutputDir -SymbolizedOnly $SymbolizedOnly
if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) { throw "Generate-BluePrint failed (exit $LASTEXITCODE)" }

# ---- Expand the BP back to validation .mtpl (round-trip parity check) -----
$bpFile  = Join-Path $OutputDir "${sliceName}_bp.mtpl"
$csvFile = Join-Path $OutputDir "$sliceName.symbols.csv"
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

# ---- Build flat denormalized views (one row per test instance) ------------
# Disabled: the new design keeps only `_bp.mtpl` + `.symbols.csv`. The flat
# builders consumed the old per-bucket symbols.csv format and produce
# additional output files that are not part of the requested two-file output.
$flatBp  = $null
$flatTab = $null

# (flat builder invocations removed; cleanup pass below deletes any stale
#  outputs from prior runs.)

# ---- Cleanup: keep _bp.mtpl, .symbols.csv, .mtpl_orig, .binmap.json,
#               .derivations.log, .compressions.log; delete the rest.
$keep = @(
    "${sliceName}_bp.mtpl"
    "$sliceName.symbols.csv"
    "$sliceName.mtpl_orig"
    "$sliceName.binmap.json"
    "$sliceName.derivations.log"
    "$sliceName.compressions.log"
)
$removed = 0
Get-ChildItem -Path $OutputDir -File -Filter "$sliceName*" | ForEach-Object {
    if ($_.Name -in $keep) { return }
    try { Remove-Item $_.FullName -Force -ErrorAction Stop; $removed++ } catch { }
}
if ($removed -gt 0) {
    Write-Host "  Cleanup: removed $removed extra file(s); kept _bp.mtpl + .symbols.csv + .mtpl_orig + .binmap.json + .derivations.log + .compressions.log"
}

Write-Host ""
Write-Host "=== Block BP generation complete ==="
Write-Host "  BP        : $(Join-Path $OutputDir "${sliceName}_bp.mtpl")"
Write-Host "  symbols   : $(Join-Path $OutputDir "$sliceName.symbols.csv")"
