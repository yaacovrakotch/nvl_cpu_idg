<#
.SYNOPSIS
  Build a "flat-style" BluePrint pair from a module's per-bucket symbols CSV:
    <MODULE>_bp_flat.mtpl     - one skeleton block per (TestType, Template)
    <MODULE>_symbols_flat.csv - one row per test instance with all slot values

  Inspired by the VMAX_TESTS.csv approach: a single denormalized table of
  tests, with a small MTPL-shaped skeleton that uses \COLUMN\ placeholders
  for varying values and inlines constants where the column is the same for
  every test of that template.

.DESCRIPTION
  Inputs:
    <module>.symbols.csv  (per-bucket sections written by Generate-BluePrint.ps1)

  Outputs (next to the input by default):
    <module>_bp_flat.mtpl
    <module>_symbols_flat.csv

  The skeleton MTPL groups every test bucket by (TestType, Template). Each
  group produces one block; for each slot column in the union over the
  group's buckets:
    - if all rows in the group share the same value -> emit literal
    - otherwise                                     -> emit "\COLUMN\"
  The InstanceName itself becomes a \Name\ placeholder.

  Flow buckets are skipped (this view is for tests).
#>
param(
    [Parameter(Mandatory)] [string]$InputCsv,
    [string]$OutputMtpl,
    [string]$OutputCsv
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$InputCsv = (Resolve-Path $InputCsv).Path
$inputDir = Split-Path $InputCsv
$leaf     = [IO.Path]::GetFileNameWithoutExtension($InputCsv)
if ($leaf -match '^(.+)\.symbols$') { $module = $Matches[1] } else { $module = $leaf }
if (-not $OutputMtpl) { $OutputMtpl = Join-Path $inputDir "${module}_bp_flat.mtpl" }
if (-not $OutputCsv ) { $OutputCsv  = Join-Path $inputDir "${module}_symbols_flat.csv" }

Write-Host "=== Flat BluePrint Builder ==="
Write-Host "In  : $InputCsv"
Write-Host "BP  : $OutputMtpl"
Write-Host "CSV : $OutputCsv"

#region helpers
function Split-CsvLine {
    param([string]$Line)
    $out = New-Object 'System.Collections.Generic.List[string]'
    $sb  = New-Object System.Text.StringBuilder
    $inQ = $false
    for ($i = 0; $i -lt $Line.Length; $i++) {
        $ch = $Line[$i]
        if ($inQ) {
            if ($ch -eq '"') {
                if ($i + 1 -lt $Line.Length -and $Line[$i + 1] -eq '"') { [void]$sb.Append('"'); $i++ }
                else { $inQ = $false }
            } else { [void]$sb.Append($ch) }
        } else {
            if     ($ch -eq ',') { $out.Add($sb.ToString()); [void]$sb.Clear() }
            elseif ($ch -eq '"') { $inQ = $true }
            else                 { [void]$sb.Append($ch) }
        }
    }
    $out.Add($sb.ToString())
    return $out.ToArray()
}

function Csv-Escape {
    param([string]$s)
    if ($null -eq $s) { return '' }
    if ($s -match '[",\r\n]') { return '"' + ($s -replace '"','""') + '"' }
    return $s
}
#endregion

#region parse per-bucket csv
$lines = [IO.File]::ReadAllLines($InputCsv)
$buckets = New-Object 'System.Collections.Generic.List[hashtable]'
$i = 0
while ($i -lt $lines.Length) {
    $ln = $lines[$i]
    if ($ln -match '^#\s*Bucket\s+(\S+)\s+type=(\S+)(?:\s+template=(\S*))?(?:\s+(?:tests|flows)=(\d+))?') {
        $bId   = $Matches[1]
        $bType = $Matches[2]
        $bTmpl = if ($Matches.Count -gt 3) { $Matches[3] } else { '' }
        $i++
        while ($i -lt $lines.Length -and ($lines[$i].Trim() -eq '' -or $lines[$i].StartsWith('#'))) { $i++ }
        if ($i -ge $lines.Length) { break }
        $hdr = Split-CsvLine -Line $lines[$i]
        $i++
        $rows = New-Object 'System.Collections.Generic.List[string[]]'
        while ($i -lt $lines.Length -and $lines[$i].Trim() -ne '' -and -not $lines[$i].StartsWith('#')) {
            $rows.Add((Split-CsvLine -Line $lines[$i]))
            $i++
        }
        $buckets.Add(@{ Id = $bId; Type = $bType; Template = $bTmpl; Header = $hdr; Rows = $rows })
        continue
    }
    $i++
}
$testBuckets = @($buckets | Where-Object { $_.Type -ne 'Flow' })
Write-Host ("  Test buckets parsed: {0}" -f $testBuckets.Count)
#endregion

#region group by (TestType, Template) and build flat rows
# Each "test record" -> @{ TestType; Template; BucketId; Name; Cells = ordered hashtable slot->value }
$records = New-Object 'System.Collections.Generic.List[hashtable]'
foreach ($b in $testBuckets) {
    foreach ($r in $b.Rows) {
        $cells = [ordered]@{}
        for ($k = 1; $k -lt $b.Header.Length; $k++) {
            if ($k -lt $r.Length) { $cells[$b.Header[$k]] = $r[$k] }
        }
        $records.Add(@{
            TestType = $b.Type
            Template = $b.Template
            BucketId = $b.Id
            Name     = $r[0]
            Cells    = $cells
        })
    }
}
Write-Host ("  Total tests        : {0}" -f $records.Count)

# Group records
$groups = @{}
$groupOrder = New-Object 'System.Collections.Generic.List[string]'
foreach ($rec in $records) {
    $gk = "$($rec.TestType)|$($rec.Template)"
    if (-not $groups.ContainsKey($gk)) {
        $groups[$gk] = @{
            TestType = $rec.TestType
            Template = $rec.Template
            Records  = New-Object 'System.Collections.Generic.List[hashtable]'
        }
        [void]$groupOrder.Add($gk)
    }
    [void]$groups[$gk].Records.Add($rec)
}
Write-Host ("  Skeleton groups    : {0}" -f $groups.Count)
#endregion

#region emit symbols_flat.csv (one table per group, each with its own header)
# Format mirrors the per-bucket symbols.csv style but groups by
# (TestType, Template) instead of by bucket id, and uses a meaningful
# table name like  TESTS_<TEMPLATE>_<TESTTYPE>  (similar to VMAX_TESTS).
$csvSb = New-Object System.Text.StringBuilder
[void]$csvSb.AppendLine("# Flat symbols table for $module")
[void]$csvSb.AppendLine("# One section per (TestType, Template) group; columns are the union of")
[void]$csvSb.AppendLine("# slot names across that group's buckets.")
[void]$csvSb.AppendLine('')
foreach ($gk in $groupOrder) {
    $g = $groups[$gk]
    # Per-group slot union, ordered.
    $gSlotSet = New-Object 'System.Collections.Generic.HashSet[string]'
    foreach ($rec in $g.Records) { foreach ($k in $rec.Cells.Keys) { [void]$gSlotSet.Add($k) } }
    $gSlots = @($gSlotSet | Sort-Object)
    # Drop slots that are constant across the whole group (their value is in
    # the corresponding skeleton block) so the table only carries varying
    # columns -- much more like VMAX_TESTS in shape.
    $varSlots = @()
    foreach ($s in $gSlots) {
        $vals = New-Object 'System.Collections.Generic.HashSet[string]'
        foreach ($rec in $g.Records) {
            $v = if ($rec.Cells.Contains($s)) { [string]$rec.Cells[$s] } else { '' }
            [void]$vals.Add($v)
        }
        if ($vals.Count -gt 1) { $varSlots += $s }
    }
    $tmpl = if ($g.Template) { $g.Template } else { 'NoTemplate' }
    $tblName = ("{0}_{1}" -f $tmpl.ToUpper(), $g.TestType.ToUpper())
    [void]$csvSb.AppendLine("# Table: $tblName  TestType=$($g.TestType)  Template=$($g.Template)  tests=$($g.Records.Count)")
    $hdr = @('SYMBOL') + $varSlots
    [void]$csvSb.AppendLine((($hdr | ForEach-Object { Csv-Escape $_ }) -join ','))
    foreach ($rec in $g.Records) {
        $cells = New-Object 'System.Collections.Generic.List[string]'
        [void]$cells.Add($rec.Name)
        foreach ($s in $varSlots) {
            if ($rec.Cells.Contains($s)) { [void]$cells.Add([string]$rec.Cells[$s]) } else { [void]$cells.Add('') }
        }
        [void]$csvSb.AppendLine((($cells | ForEach-Object { Csv-Escape $_ }) -join ','))
    }
    [void]$csvSb.AppendLine('')
}
[IO.File]::WriteAllText($OutputCsv, $csvSb.ToString())
Write-Host ("  Symbols rows       : {0}" -f $records.Count)
#endregion

#region emit bp_flat.mtpl (one skeleton block per group)
$mtplSb = New-Object System.Text.StringBuilder
[void]$mtplSb.AppendLine("# Flat BluePrint for $module")
[void]$mtplSb.AppendLine("# One block per (TestType, Template). Constants are inlined; varying")
[void]$mtplSb.AppendLine("# values appear as \COLUMN\ placeholders; \Name\ is the InstanceName.")
[void]$mtplSb.AppendLine("# Companion: ${module}_symbols_flat.csv")
[void]$mtplSb.AppendLine('')

$skeletonStats = New-Object 'System.Collections.Generic.List[string]'
foreach ($gk in $groupOrder) {
    $g = $groups[$gk]
    # Union of slots present in this group
    $gSlotSet = New-Object 'System.Collections.Generic.HashSet[string]'
    foreach ($rec in $g.Records) { foreach ($k in $rec.Cells.Keys) { [void]$gSlotSet.Add($k) } }
    $gSlots = @($gSlotSet | Sort-Object)
    # Determine constant vs varying per slot
    $constSlots = @()
    $varSlots   = @()
    foreach ($s in $gSlots) {
        $vals = New-Object 'System.Collections.Generic.HashSet[string]'
        foreach ($rec in $g.Records) {
            $v = if ($rec.Cells.Contains($s)) { [string]$rec.Cells[$s] } else { '' }
            [void]$vals.Add($v)
        }
        if ($vals.Count -eq 1) { $constSlots += @{ Name = $s; Value = (@($vals)[0]) } }
        else                   { $varSlots   += $s }
    }
    [void]$skeletonStats.Add(("  {0,-40} tests={1,-4} constant={2,-3} varying={3}" -f $gk, $g.Records.Count, $constSlots.Count, $varSlots.Count))

    # Emit skeleton
    $tt = $g.TestType
    $tmpl = $g.Template
    $tmplLbl = if ($tmpl) { $tmpl } else { 'NoTemplate' }
    $tblName = ("{0}_{1}" -f $tmplLbl.ToUpper(), $tt.ToUpper())
    $hdrLine = if ($tmpl) { "$tt $tmpl \Name\" } else { "$tt \Name\" }
    [void]$mtplSb.AppendLine("# Table: $tblName  tests=$($g.Records.Count)  (companion CSV section: $tblName)")
    [void]$mtplSb.AppendLine($hdrLine)
    [void]$mtplSb.AppendLine('{')
    foreach ($c in $constSlots) {
        $val = $c.Value
        if ($val -eq '') { continue }   # don't emit empty constants
        # Quote if value contains characters that look like a string param.
        if ($val -match '\s|[":=]' -or $c.Name -match '^(Patlist|HryMapPath|StartVoltagesForRetry|ResourcesFilePath|PrescreenMapName|ScreenTestSet|InputStorageKey|TargetArray|DecoderMatchLabel|SetPoints)') {
            [void]$mtplSb.AppendLine("    $($c.Name) = `"$val`";")
        } else {
            [void]$mtplSb.AppendLine("    $($c.Name) = $val;")
        }
    }
    foreach ($s in $varSlots) {
        [void]$mtplSb.AppendLine("    $s = `"\$s\`";")
    }
    [void]$mtplSb.AppendLine('}')
    [void]$mtplSb.AppendLine('')
}
[IO.File]::WriteAllText($OutputMtpl, $mtplSb.ToString())
Write-Host "  Skeleton group stats:"
foreach ($l in $skeletonStats) { Write-Host $l }
Write-Host ("  BP written         : {0}" -f $OutputMtpl)
Write-Host ("  CSV written        : {0}" -f $OutputCsv)
#endregion
