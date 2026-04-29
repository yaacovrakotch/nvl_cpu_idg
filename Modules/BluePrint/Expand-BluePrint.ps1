<#
.SYNOPSIS
    Expands a v2 BluePrint (data-driven, per-bucket-table CSV) into a full .mtpl.

.DESCRIPTION
    Reads <module>.mtpl.bp + <module>.symbols.csv. The CSV is organised as
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
    Path to <module>.mtpl.bp.
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
if ($bpFileName -notmatch '^(.+)\.mtpl\.bp$') {
    throw "Input must end with .mtpl.bp, got: $bpFileName"
}
$moduleName  = $Matches[1]
$moduleDir   = Split-Path $bpDir
$csvFile     = Join-Path $bpDir "$moduleName.symbols.csv"
$binmapFile  = Join-Path $bpDir "$moduleName.binmap.json"
$valFile     = Join-Path $bpDir "$moduleName.mtpl.bp.val"
$origMtpl    = Join-Path $moduleDir "$moduleName.mtpl_orig"
$targetMtpl  = Join-Path $moduleDir "$moduleName.mtpl"

Write-Host "=== BluePrint Expander (v2 per-bucket CSV) ==="
Write-Host "BP : $InputBp"
Write-Host "CSV: $csvFile"

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
if (Test-Path $binmapFile) {
    $bm = Get-Content $binmapFile -Raw | ConvertFrom-Json
    if ($bm.PSObject.Properties.Name -contains 'tests' -and $bm.tests) {
        foreach ($p in $bm.tests.PSObject.Properties) { $binmapTests[$p.Name] = @($p.Value) }
    }
    if ($bm.PSObject.Properties.Name -contains 'flows' -and $bm.flows) {
        foreach ($p in $bm.flows.PSObject.Properties) { $binmapFlows[$p.Name] = @($p.Value) }
    }
    Write-Host "  Binmap loaded: tests=$($binmapTests.Count), flows=$($binmapFlows.Count)"
} else {
    Write-Host "  Binmap: not found (placeholders will remain in output)"
}

function Restore-BinCtrPlaceholders {
    # Walks $bodyLines and replaces __BIN__/__CTR__/__BNUM__ placeholders with
    # the original values stored in $values (in body order).
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
