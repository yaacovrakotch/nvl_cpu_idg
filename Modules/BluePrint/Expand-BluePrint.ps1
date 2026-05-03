<#
.SYNOPSIS
    Expands a v2 BluePrint (data-driven, per-bucket-table CSV) into a full .mtpl.

.DESCRIPTION
    Reads <module>_bp.mtpl + <module>.symbols.csv. The CSV is organised as
    one tabular section per bucket:
        # Bucket B1  type=CSharpTest  template=VminTC  tests=4
        InstanceName,SLOT1,SLOT2
        name_a,v1,v2
        name_b,v3,v4
        ...
        <blank line>
        # Bucket F1  type=Flow  flows=2
        FlowName,SLOT1
        ...

    The BP marks compressed sections with:
        # BP_BUCKET: B<id> tests=<n>      (for tests)
        # BP_FLOW_BUCKET: F<id> flows=<n> (for flows)

    For each bucket, the expander emits one block per CSV row, substituting
    \SLOT\ placeholders with that row's slot values.
.PARAMETER InputBp
    Path to <module>_bp.mtpl.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]$InputBp
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

#region paths
$InputBp    = (Resolve-Path $InputBp).Path
$bpDir      = Split-Path $InputBp
$bpFileName = [IO.Path]::GetFileName($InputBp)
if ($bpFileName -match '^(.+)_bp\.mtpl$') {
    $moduleName = $Matches[1]
} elseif ($bpFileName -match '^(.+)_bp\.bp$') {
    # Backwards compatibility with the .bp extension.
    $moduleName = $Matches[1]
} elseif ($bpFileName -match '^(.+)\.mtpl\.bp$') {
    # Backwards compatibility with the legacy name.
    $moduleName = $Matches[1]
} else {
    throw "Input must end with _bp.mtpl (or legacy _bp.bp / .mtpl.bp), got: $bpFileName"
}
$moduleDir   = Split-Path $bpDir
$csvFile     = Join-Path $bpDir "$moduleName.symbols.csv"
$binmapFile  = Join-Path $bpDir "$moduleName.binmap.json"
$valFile     = Join-Path $bpDir "${moduleName}_bp.val.mtpl"
$origMtpl    = Join-Path $moduleDir "$moduleName.mtpl_orig"
$targetMtpl  = Join-Path $moduleDir "$moduleName.mtpl"

Write-Host "=== BluePrint Expander (v2 per-bucket CSV) ==="
Write-Host "BP : $InputBp"
Write-Host "CSV: $csvFile"

# Prefer .symbols.csv.new if it exists and is newer than .csv (the generator
# writes there when something else holds an exclusive lock on the .csv).
$csvNewFile = "$csvFile.new"
if ((Test-Path $csvNewFile) -and (-not (Test-Path $csvFile) -or
     (Get-Item $csvNewFile).LastWriteTime -gt (Get-Item $csvFile).LastWriteTime)) {
    Write-Host "  Using $csvNewFile (newer than .csv)"
    $csvFile = $csvNewFile
}

if (-not (Test-Path $csvFile)) {
    throw "symbols.csv not found at $csvFile - run Generate-BluePrint first."
}
#endregion

#region parse symbols.csv (per-bucket tables)
$bucketTables = [ordered]@{}
$rawCsv = [IO.File]::ReadAllLines($csvFile)
$ci = 0
try {
while ($ci -lt $rawCsv.Count) {
    $line = $rawCsv[$ci]
    if ($line -match '^\s*#\s*Bucket\s+(\S+)') {
        $bid = $Matches[1]
        $ci++
        if ($ci -ge $rawCsv.Count) { throw "Bucket $bid has no header row" }
        $hdrLine = $rawCsv[$ci]; $ci++
        $hdrCols = $hdrLine.Split(',')
        $slotNames = New-Object System.Collections.Generic.List[string]
        if ($hdrCols.Count -gt 1) {
            for ($h = 1; $h -lt $hdrCols.Count; $h++) { [void]$slotNames.Add($hdrCols[$h]) }
        }
        $rows = [System.Collections.Generic.List[hashtable]]::new()
        # Collect data lines for this bucket then parse them as a CSV chunk
        # so quoted fields containing commas are handled correctly.
        $dataLines = New-Object System.Collections.Generic.List[string]
        while ($ci -lt $rawCsv.Count -and $rawCsv[$ci].Trim() -ne '' -and -not ($rawCsv[$ci] -match '^\s*#\s*Bucket')) {
            [void]$dataLines.Add($rawCsv[$ci])
            $ci++
        }
        if ($dataLines.Count -gt 0) {
            $chunk = @($hdrLine) + $dataLines
            $parsed = $chunk | ConvertFrom-Csv
            foreach ($pr in $parsed) {
                $name = $pr.($hdrCols[0])
                $slots = @{}
                foreach ($sn in $slotNames) { $slots[$sn] = $pr.$sn }
                $rows.Add(@{ Name = $name; Slots = $slots })
            }
        }
        $bucketTables[$bid] = $rows
        continue
    }
    $ci++
}
} catch {
    Write-Host "CSV parse error at line $ci ('$($rawCsv[$ci])'): $_" -ForegroundColor Red
    Write-Host "Stack: $($_.ScriptStackTrace)" -ForegroundColor Red
    throw
}
Write-Host "  Buckets in CSV: $($bucketTables.Count)"
#endregion

#region load binmap (per-instance original bin/ctr/bnum values)
$binmapTests = @{}
$binmapFlows = @{}
$globalDefaultPre  = $null
$globalDefaultPost = $null
if (Test-Path $binmapFile) {
    $bm = Get-Content $binmapFile -Raw | ConvertFrom-Json
    if ($bm.PSObject.Properties.Name -contains 'tests' -and $bm.tests) {
        foreach ($p in $bm.tests.PSObject.Properties) { $binmapTests[$p.Name] = @($p.Value) }
    }
    if ($bm.PSObject.Properties.Name -contains 'flows' -and $bm.flows) {
        foreach ($p in $bm.flows.PSObject.Properties) { $binmapFlows[$p.Name] = @($p.Value) }
    }
    if ($bm.PSObject.Properties.Name -contains 'defaults' -and $bm.defaults) {
        if ($bm.defaults.PSObject.Properties.Name -contains 'SetPointsPreInstance')  { $globalDefaultPre  = [string]$bm.defaults.SetPointsPreInstance }
        if ($bm.defaults.PSObject.Properties.Name -contains 'SetPointsPostInstance') { $globalDefaultPost = [string]$bm.defaults.SetPointsPostInstance }
    }
    Write-Host "  Binmap loaded: tests=$($binmapTests.Count), flows=$($binmapFlows.Count), defaults Pre=$globalDefaultPre Post=$globalDefaultPost"
} else {
    Write-Host "  Binmap: not found (placeholders will remain in output)"
}

function Restore-BinCtrPlaceholders {
    # Walks $bodyLines and restores per-instance values stored in $values
    # (in body order). Restores:
    #   SetBin __BIN__                       -> original bin value
    #   IncrementCounters __CTR__            -> original counter value
    #   BaseNumbers "__BNUM__"               -> original baseNumber value
    #   BypassPort = __BYPASS__              -> original BypassPort value (1 or -1)
    # SetPointsPreInstance / SetPointsPostInstance "DEFAULT" are restored
    # from a single global default applied to every instance in Restore-Defaults.
    param(
        [System.Collections.Generic.List[string]]$BodyLines,
        $Values
    )
    if (-not $Values -or $Values.Count -eq 0) { return $BodyLines }
    $vi = 0
    $out = [System.Collections.Generic.List[string]]::new()
    foreach ($l in $BodyLines) {
        $nl = $l
        if ($nl -match '__BIN__') {
            if ($vi -lt $Values.Count) { $nl = $nl.Replace('__BIN__', [string]$Values[$vi]); $vi++ }
        } elseif ($nl -match '__CTR__') {
            if ($vi -lt $Values.Count) { $nl = $nl.Replace('__CTR__', [string]$Values[$vi]); $vi++ }
        } elseif ($nl -match '__BNUM__') {
            if ($vi -lt $Values.Count) { $nl = $nl.Replace('__BNUM__', [string]$Values[$vi]); $vi++ }
        } elseif ($nl -match '__BYPASS__') {
            if ($vi -lt $Values.Count) { $nl = $nl.Replace('__BYPASS__', [string]$Values[$vi]); $vi++ }
        }
        [void]$out.Add($nl)
    }
    return $out
}

function Restore-Defaults {
    # Replaces literal SetPointsPreInstance / SetPointsPostInstance "DEFAULT"
    # values with the single global default value for the module.
    param(
        [System.Collections.Generic.List[string]]$BodyLines,
        [string]$PreVal,
        [string]$PostVal
    )
    $out = [System.Collections.Generic.List[string]]::new()
    foreach ($l in $BodyLines) {
        $nl = $l
        if ($PreVal -ne $null -and $nl -match '^(\s*SetPointsPreInstance\s*=\s*)"DEFAULT"(\s*;\s*)$') {
            $nl = $Matches[1] + '"' + $PreVal + '"' + $Matches[2]
        } elseif ($PostVal -ne $null -and $nl -match '^(\s*SetPointsPostInstance\s*=\s*)"DEFAULT"(\s*;\s*)$') {
            $nl = $Matches[1] + '"' + $PostVal + '"' + $Matches[2]
        }
        [void]$out.Add($nl)
    }
    return $out
}
#endregion

#region read BP and expand
$bpLines = [IO.File]::ReadAllLines($InputBp)
$out = [System.Collections.Generic.List[string]]::new()

$testCount = 0; $flowCount = 0; $bucketCount = 0; $flowBucketCount = 0
$i = 0
while ($i -lt $bpLines.Count) {
    $line = $bpLines[$i]

    $marker = $null; $bid = $null
    if ($line -match '^# BP_BUCKET:\s*(B\d+)')           { $marker = 'test'; $bid = $Matches[1] }
    elseif ($line -match '^# BP_FLOW_BUCKET:\s*(F\d+)')  { $marker = 'flow'; $bid = $Matches[1] }

    if ($marker) {
        if ($marker -eq 'test') { $bucketCount++ } else { $flowBucketCount++ }
        $i++
        $blockCmts = [System.Collections.Generic.List[string]]::new()
        while ($i -lt $bpLines.Count) {
            $ln = $bpLines[$i]
            if ($ln -match '^# BP_(BUCKET|FLOW_BUCKET):') { break }
            if ($ln -match '^\s*(CSharpTest|MultiTrialTest|Flow)\s+') { break }
            if ($ln.Trim() -eq '') { $i++; continue }
            $blockCmts.Add($ln); $i++
        }
        if ($i -ge $bpLines.Count) { throw "Bucket $bid has no body" }
        $body = [System.Collections.Generic.List[string]]::new()
        $depth = 0; $opened = $false
        while ($i -lt $bpLines.Count) {
            $body.Add($bpLines[$i])
            $depth += ([regex]::Matches($bpLines[$i], '\{')).Count
            $depth -= ([regex]::Matches($bpLines[$i], '\}')).Count
            if ($depth -gt 0) { $opened = $true }
            $i++
            if ($opened -and $depth -le 0) { break }
        }

        if (-not $bucketTables.Contains($bid)) {
            throw "Bucket $bid referenced in BP but not in CSV"
        }
        foreach ($row in $bucketTables[$bid]) {
            foreach ($c in $blockCmts) { $out.Add($c) }
            # Build expanded body for this instance, then restore real
            # bin/counter/baseNumber values from the binmap so the emitted
            # .mtpl is build-valid.
            $expandedBody = [System.Collections.Generic.List[string]]::new()
            foreach ($bl in $body) {
                $expanded = $bl
                foreach ($k in $row.Slots.Keys) {
                    $expanded = $expanded.Replace("\$k\", $row.Slots[$k])
                }
                [void]$expandedBody.Add($expanded)
            }
            $valMap = if ($marker -eq 'test') { $binmapTests } else { $binmapFlows }
            if ($valMap.ContainsKey($row.Name)) {
                $expandedBody = Restore-BinCtrPlaceholders -BodyLines $expandedBody -Values $valMap[$row.Name]
            }
            $expandedBody = Restore-Defaults -BodyLines $expandedBody -PreVal $globalDefaultPre -PostVal $globalDefaultPost
            foreach ($el in $expandedBody) { $out.Add($el) }
            $out.Add('')
            if ($marker -eq 'test') { $testCount++ } else { $flowCount++ }
        }
        continue
    }

    # Non-bucketed Flow block (verbatim) — kept for safety
    if ($line -match '^\s*Flow\s+\S') {
        $depth = 0; $opened = $false
        while ($i -lt $bpLines.Count) {
            $out.Add($bpLines[$i])
            $depth += ([regex]::Matches($bpLines[$i], '\{')).Count
            $depth -= ([regex]::Matches($bpLines[$i], '\}')).Count
            if ($depth -gt 0) { $opened = $true }
            $i++
            if ($opened -and $depth -le 0) { break }
        }
        $flowCount++
        continue
    }

    $out.Add($line)
    $i++
}

[IO.File]::WriteAllLines($valFile, $out.ToArray())
Write-Host "  Tests expanded: $testCount from $bucketCount test buckets"
Write-Host "  Flows expanded: $flowCount from $flowBucketCount flow buckets"
Write-Host "  Val written: $valFile"

# Write the fully expanded .mtpl for build (same content as val, just placed
# at the module's .mtpl path so torch picks it up for compilation).
[IO.File]::WriteAllLines($targetMtpl, $out.ToArray())
Write-Host "  Build .mtpl written: $targetMtpl  (tests=$testCount, flows=$flowCount)"
#endregion
#endregion

#region round-trip identity check vs mtpl_orig
function Get-Blocks {
    param([string]$Path)
    $lines = [IO.File]::ReadAllLines($Path)
    $tests = @{}; $flows = @{}
    $i = 0
    while ($i -lt $lines.Count) {
        $ln = $lines[$i]
        $kind = $null; $name = $null
        if ($ln -match '^\s*CSharpTest\s+\S+\s+(\S+)')      { $kind = 'test'; $name = $Matches[1].Trim() }
        elseif ($ln -match '^\s*MultiTrialTest\s+(\S+)\s*$'){ $kind = 'test'; $name = $Matches[1].Trim() }
        elseif ($ln -match '^\s*Flow\s+(\S+)')              { $kind = 'flow'; $name = $Matches[1].Trim() }
        if ($kind) {
            $depth = 0; $opened = $false
            $body = [System.Text.StringBuilder]::new()
            while ($i -lt $lines.Count) {
                $bl = $lines[$i]
                [void]$body.AppendLine($bl)
                $depth += ([regex]::Matches($lines[$i], '\{')).Count
                $depth -= ([regex]::Matches($lines[$i], '\}')).Count
                if ($depth -gt 0) { $opened = $true }
                $i++
                if ($opened -and $depth -le 0) { break }
            }
            $bs = $body.ToString()
            $bs = ($bs -split "`n" |
                   Where-Object { $_ -notmatch '^\s*#\s*BP_' } |
                   ForEach-Object { ($_.Trim()) }) -join "`n"
            $bs = $bs -replace '\s+', ' '
            if ($kind -eq 'test') { $tests[$name] = $bs } else { $flows[$name] = $bs }
            continue
        }
        $i++
    }
    return @{ Tests = $tests; Flows = $flows }
}

if (Test-Path $origMtpl) {
    Write-Host ""
    Write-Host "Round-trip identity check vs mtpl_orig..."
    $o = Get-Blocks -Path $origMtpl
    $v = Get-Blocks -Path $valFile
    #region BP-vs-MTPL count parity + flow connectivity (new checks)
    function Get-FlowConnectivity {
        param([string]$Path)
        # Parse flows + per-flow body so we can do reachability from roots.
        $lines = [IO.File]::ReadAllLines($Path)
        $flowDefs = New-Object 'System.Collections.Generic.List[string]'
        $flowSet  = New-Object 'System.Collections.Generic.HashSet[string]'
        $bodyMap  = @{}   # name -> list of body lines
        $i = 0
        while ($i -lt $lines.Count) {
            $ln = $lines[$i]
            if ($ln -match '^\s*(?:DUTFlow|Flow)\s+(\S+)') {
                $name = $Matches[1]
                [void]$flowDefs.Add($name); [void]$flowSet.Add($name)
                $body = New-Object 'System.Collections.Generic.List[string]'
                # Find opening brace (may be same line or next non-blank)
                $j = $i + 1
                while ($j -lt $lines.Count -and $lines[$j].Trim() -eq '') { $j++ }
                if ($j -lt $lines.Count -and $lines[$j].Trim().StartsWith('{')) {
                    $depth = 1; $j++
                    while ($j -lt $lines.Count -and $depth -gt 0) {
                        $bl = $lines[$j]
                        $depth += ([regex]::Matches($bl, '\{').Count)
                        $depth -= ([regex]::Matches($bl, '\}').Count)
                        if ($depth -gt 0) { [void]$body.Add($bl) }
                        $j++
                    }
                }
                $bodyMap[$name] = $body
                $i = $j; continue
            }
            $i++
        }
        # Per-flow outgoing FlowItem refs (only to other defined flows).
        $edges = @{}
        $referenced = New-Object 'System.Collections.Generic.HashSet[string]'
        foreach ($name in $flowDefs) {
            $outs = New-Object 'System.Collections.Generic.HashSet[string]'
            foreach ($bl in $bodyMap[$name]) {
                if ($bl -match '^\s*(?:DUTFlowItem|FlowItem)\s+(\S+)(?:\s+(\S+))?') {
                    foreach ($t in @($Matches[1], $Matches[2])) {
                        if ($t -and $flowSet.Contains($t) -and $t -ne $name) {
                            [void]$outs.Add($t); [void]$referenced.Add($t)
                        }
                    }
                }
            }
            $edges[$name] = $outs
        }
        # Roots = flows not referenced by anything (entry points).
        $roots = New-Object 'System.Collections.Generic.List[string]'
        foreach ($name in $flowDefs) {
            if (-not $referenced.Contains($name)) { [void]$roots.Add($name) }
        }
        if ($flowDefs.Count -gt 0 -and -not $roots.Contains($flowDefs[0])) {
            [void]$roots.Add($flowDefs[0])
        }
        # BFS reachability.
        $reach = New-Object 'System.Collections.Generic.HashSet[string]'
        $q = New-Object 'System.Collections.Generic.Queue[string]'
        foreach ($r in $roots) { [void]$reach.Add($r); $q.Enqueue($r) }
        while ($q.Count -gt 0) {
            $c = $q.Dequeue()
            foreach ($n in $edges[$c]) {
                if (-not $reach.Contains($n)) { [void]$reach.Add($n); $q.Enqueue($n) }
            }
        }
        return @{ Flows = $flowDefs; Refs = $referenced; Roots = $roots; Reachable = $reach; BodyMap = $bodyMap }
    }

    function Get-TestFlowCoverage {
        # Returns test names that appear as CSharpTest/MultiTrialTest but are
        # never referenced by any FlowItem/DUTFlowItem in any flow body.
        param([string]$Path)
        $lines = [IO.File]::ReadAllLines($Path)
        $testNames = New-Object 'System.Collections.Generic.HashSet[string]'
        $fiRefs    = New-Object 'System.Collections.Generic.HashSet[string]'
        foreach ($ln in $lines) {
            if ($ln -match '^\s*CSharpTest\s+\S+\s+(\S+)')       { [void]$testNames.Add($Matches[1].Trim()) }
            elseif ($ln -match '^\s*MultiTrialTest\s+(\S+)\s*$') { [void]$testNames.Add($Matches[1].Trim()) }
            elseif ($ln -match '^\s*(?:DUTFlowItem|FlowItem)\s+(\S+)(?:\s+(\S+))?') {
                [void]$fiRefs.Add($Matches[1])
                if ($Matches[2]) { [void]$fiRefs.Add($Matches[2]) }
            }
        }
        $uncovered = New-Object 'System.Collections.Generic.List[string]'
        foreach ($t in $testNames) {
            if (-not $fiRefs.Contains($t)) { [void]$uncovered.Add($t) }
        }
        return @{ Total = $testNames.Count; Covered = ($testNames.Count - $uncovered.Count); Uncovered = $uncovered }
    }
    function Get-BpLogicalCounts {
        param([string]$Path)
        $tCount = 0; $fCount = 0
        foreach ($ln in [IO.File]::ReadAllLines($Path)) {
            if ($ln -match '^\s*#\s*BP_BUCKET\s*:\s*\S+\s+tests=(\d+)')      { $tCount += [int]$Matches[1] }
            elseif ($ln -match '^\s*#\s*BP_FLOW_BUCKET\s*:\s*\S+\s+flows=(\d+)') { $fCount += [int]$Matches[1] }
        }
        return @{ Tests = $tCount; Flows = $fCount }
    }
    $bpCounts = Get-BpLogicalCounts -Path $InputBp
    $valTests = $v.Tests.Count
    $valFlows = $v.Flows.Count
    Write-Host "  Count parity: BP-logical tests=$($bpCounts.Tests) val=$valTests | BP-logical flows=$($bpCounts.Flows) val=$valFlows"
    $parityFail = $false
    if ($bpCounts.Tests -ne $valTests) {
        Write-Host "    Test count mismatch ($($bpCounts.Tests) vs $valTests)" -ForegroundColor Red; $parityFail = $true
    }
    if ($bpCounts.Flows -ne $valFlows) {
        Write-Host "    Flow count mismatch ($($bpCounts.Flows) vs $valFlows)" -ForegroundColor Red; $parityFail = $true
    }

    $valConn = Get-FlowConnectivity -Path $valFile
    $orphans = New-Object 'System.Collections.Generic.List[string]'
    foreach ($fn in $valConn.Flows) {
        if (-not $valConn.Reachable.Contains($fn)) { [void]$orphans.Add($fn) }
    }
    Write-Host "  Flow connectivity: defined=$($valConn.Flows.Count) roots=$($valConn.Roots.Count) reachable=$($valConn.Reachable.Count) orphan=$($orphans.Count)"
    if ($orphans.Count -gt 0) {
        foreach ($o2 in ($orphans | Select-Object -First 20)) { Write-Host "    orphan flow: $o2" -ForegroundColor Yellow }
        if ($orphans.Count -gt 20) { Write-Host "    ...and $($orphans.Count - 20) more" -ForegroundColor Yellow }
    }

    # Check 2: every test must be referenced by at least one FlowItem.
    $bpCov = Get-TestFlowCoverage -Path $InputBp
    $valCov = Get-TestFlowCoverage -Path $valFile
    Write-Host "  Test-flow coverage (bp):  total=$($bpCov.Total) covered=$($bpCov.Covered) uncovered=$($bpCov.Uncovered.Count)"
    Write-Host "  Test-flow coverage (val): total=$($valCov.Total) covered=$($valCov.Covered) uncovered=$($valCov.Uncovered.Count)"
    if ($bpCov.Uncovered.Count -gt 0) {
        foreach ($t in ($bpCov.Uncovered | Select-Object -First 20)) { Write-Host "    bp uncovered test: $t" -ForegroundColor Yellow }
        if ($bpCov.Uncovered.Count -gt 20) { Write-Host "    ...and $($bpCov.Uncovered.Count - 20) more" -ForegroundColor Yellow }
    }
    if ($valCov.Uncovered.Count -gt 0) {
        foreach ($t in ($valCov.Uncovered | Select-Object -First 20)) { Write-Host "    val uncovered test: $t" -ForegroundColor Yellow }
        if ($valCov.Uncovered.Count -gt 20) { Write-Host "    ...and $($valCov.Uncovered.Count - 20) more" -ForegroundColor Yellow }
    }
    if ($parityFail) { Write-Host "    [parity check WARNING - non-fatal]" -ForegroundColor Yellow }
    #endregion
    $missingT = @($o.Tests.Keys | Where-Object { -not $v.Tests.ContainsKey($_) })
    $diffT    = @($o.Tests.Keys | Where-Object { $v.Tests.ContainsKey($_) -and $v.Tests[$_] -ne $o.Tests[$_] })
    $extraT   = @($v.Tests.Keys | Where-Object { -not $o.Tests.ContainsKey($_) })
    $missingF = @($o.Flows.Keys | Where-Object { -not $v.Flows.ContainsKey($_) })
    $diffF    = @($o.Flows.Keys | Where-Object { $v.Flows.ContainsKey($_) -and $v.Flows[$_] -ne $o.Flows[$_] })
    $extraF   = @($v.Flows.Keys | Where-Object { -not $o.Flows.ContainsKey($_) })

    Write-Host "  Tests: orig=$($o.Tests.Count), val=$($v.Tests.Count), missing=$($missingT.Count), diff=$($diffT.Count), extra=$($extraT.Count)"
    Write-Host "  Flows: orig=$($o.Flows.Count), val=$($v.Flows.Count), missing=$($missingF.Count), diff=$($diffF.Count), extra=$($extraF.Count)"

    $issue = ($missingT.Count + $diffT.Count + $extraT.Count + $missingF.Count + $diffF.Count + $extraF.Count) -gt 0
    if ($issue) {
        if ($missingT.Count -gt 0) { Write-Host "  Missing tests:" -ForegroundColor Red; foreach ($t in ($missingT | Select-Object -First 20)) { Write-Host "    - $t" -ForegroundColor Red }; if ($missingT.Count -gt 20) { Write-Host "    ...and $($missingT.Count - 20) more" -ForegroundColor Red } }
        if ($diffT.Count    -gt 0) { Write-Host "  Body-diff tests:" -ForegroundColor Red; foreach ($t in ($diffT    | Select-Object -First 20)) { Write-Host "    - $t" -ForegroundColor Red }; if ($diffT.Count    -gt 20) { Write-Host "    ...and $($diffT.Count - 20) more" -ForegroundColor Red } }
        if ($extraT.Count   -gt 0) { Write-Host "  Extra tests:"   -ForegroundColor Yellow; foreach ($t in ($extraT  | Select-Object -First 20)) { Write-Host "    - $t" -ForegroundColor Yellow }; if ($extraT.Count   -gt 20) { Write-Host "    ...and $($extraT.Count - 20) more" -ForegroundColor Yellow } }
        if ($missingF.Count -gt 0) { Write-Host "  Missing flows:" -ForegroundColor Red; foreach ($f in $missingF) { Write-Host "    - $f" -ForegroundColor Red } }
        if ($diffF.Count    -gt 0) { Write-Host "  Body-diff flows:" -ForegroundColor Red; foreach ($f in $diffF) { Write-Host "    - $f" -ForegroundColor Red } }
        if ($extraF.Count   -gt 0) { Write-Host "  Extra flows:"   -ForegroundColor Yellow; foreach ($f in $extraF) { Write-Host "    - $f" -ForegroundColor Yellow } }
        throw "Round-trip identity check failed."
    } else {
        Write-Host "  OK - every test and flow in mtpl_orig is reproduced by the BP."
    }
} else {
    Write-Host "Round-trip check: SKIPPED (no $moduleName.mtpl_orig found)"
}
#endregion

#region replace mtpl
Copy-Item -Path $valFile -Destination $targetMtpl -Force
Write-Host "Updated: $targetMtpl"
#endregion

#region copy to sibling modules (copyTargets)
$bpConfigFile = Join-Path $bpDir 'bp-config.json'
if (Test-Path $bpConfigFile) {
    $bpConfig = Get-Content -Raw $bpConfigFile | ConvertFrom-Json
    if ($bpConfig.PSObject.Properties['copyTargets'] -and $bpConfig.copyTargets.Count -gt 0) {
        $arrDir = Split-Path $moduleDir
        foreach ($target in $bpConfig.copyTargets) {
            $tDir = Join-Path $arrDir $target
            if (Test-Path $tDir) {
                Copy-Item -Path $valFile -Destination (Join-Path $tDir "$target.mtpl") -Force
                Write-Host "Copied:  $target.mtpl (copyTarget)"
            } else {
                Write-Warning "copyTarget directory not found: $tDir - skipping $target"
            }
        }
    }
}
#endregion

Write-Host ""
Write-Host "=== Done ==="
