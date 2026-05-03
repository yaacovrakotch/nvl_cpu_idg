<#
.SYNOPSIS
  Build a flat, denormalized "all-tests" table from a module's BluePrint
  per-bucket symbols.csv. Inspired by the VMAX_TESTS.csv style: one row per
  test, columns are the union of slot names across all test buckets.

.DESCRIPTION
  Reads <module>.symbols.csv (which has one CSV section per bucket).
  Emits <module>_bp_flat.csv with one row per test instance:
    Bucket, TestType, Template, InstanceName, <slot1>, <slot2>, ...
  Slot columns are the alphabetically-sorted union across all TEST buckets
  (Flow buckets are skipped). Cells are empty when the slot isn't defined
  for that test's bucket.

  Use this for cross-bucket pattern hunting / spreadsheet pivoting.

.PARAMETER InputCsv
  Path to <module>.symbols.csv produced by Generate-BluePrint.ps1.

.PARAMETER OutputCsv
  Optional. Defaults to <InputDir>\<module>_bp_flat.csv next to the input.

.PARAMETER IncludeFlowBuckets
  When set, also emit rows for flow buckets (FlowName instead of InstanceName).
#>
param(
    [Parameter(Mandatory)] [string]$InputCsv,
    [string]$OutputCsv,
    [switch]$IncludeFlowBuckets
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$InputCsv = (Resolve-Path $InputCsv).Path
$inputDir = Split-Path $InputCsv
$leaf     = [IO.Path]::GetFileNameWithoutExtension($InputCsv)
if ($leaf -match '^(.+)\.symbols$') { $module = $Matches[1] } else { $module = $leaf }
if (-not $OutputCsv) { $OutputCsv = Join-Path $inputDir "${module}_bp_flat.csv" }

Write-Host "=== BluePrint Flat Table Builder ==="
Write-Host "In : $InputCsv"
Write-Host "Out: $OutputCsv"

# Parse the per-bucket CSV. A bucket starts with `# Bucket B<n> ...` (test) or
# `# Bucket F<n> ...` (flow). The next non-comment line is the header row,
# followed by data rows until a blank line / next `# Bucket` header.
$lines = [IO.File]::ReadAllLines($InputCsv)

function Split-CsvLine {
    # Minimal CSV split honouring double-quoted fields with embedded commas.
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

$buckets = New-Object 'System.Collections.Generic.List[hashtable]'
$i = 0
while ($i -lt $lines.Length) {
    $ln = $lines[$i]
    if ($ln -match '^#\s*Bucket\s+(\S+)\s+type=(\S+)(?:\s+template=(\S*))?(?:\s+(?:tests|flows)=(\d+))?') {
        $bId   = $Matches[1]
        $bType = $Matches[2]
        $bTmpl = if ($Matches.Count -gt 3) { $Matches[3] } else { '' }
        $i++
        # Skip blank/comment lines until header
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
Write-Host ("  Parsed {0} bucket section(s)" -f $buckets.Count)

# Collect union of slot column names across the in-scope buckets.
$inScope = if ($IncludeFlowBuckets) { $buckets } else { @($buckets | Where-Object { $_.Type -ne 'Flow' }) }
Write-Host ("  In-scope buckets   : {0}" -f $inScope.Count)
$slotNames = New-Object 'System.Collections.Generic.HashSet[string]'
foreach ($b in $inScope) {
    for ($k = 1; $k -lt $b.Header.Length; $k++) { [void]$slotNames.Add($b.Header[$k]) }
}
$slotCols = @($slotNames | Sort-Object)
Write-Host ("  Distinct slot cols : {0}" -f $slotCols.Count)

# Emit flat CSV
$sb = New-Object System.Text.StringBuilder
$leadCols = @('Bucket','BucketType','Template','Name')
$header   = $leadCols + $slotCols
[void]$sb.AppendLine((($header | ForEach-Object { Csv-Escape $_ }) -join ','))

$rowCount = 0
foreach ($b in $inScope) {
    $colIdx = @{}
    for ($k = 1; $k -lt $b.Header.Length; $k++) { $colIdx[$b.Header[$k]] = $k }
    foreach ($r in $b.Rows) {
        $name = $r[0]
        $cells = New-Object 'System.Collections.Generic.List[string]'
        [void]$cells.Add($b.Id)
        [void]$cells.Add($b.Type)
        [void]$cells.Add($b.Template)
        [void]$cells.Add($name)
        foreach ($s in $slotCols) {
            if ($colIdx.ContainsKey($s)) {
                $idx = $colIdx[$s]
                if ($idx -lt $r.Length) { [void]$cells.Add($r[$idx]) } else { [void]$cells.Add('') }
            } else {
                [void]$cells.Add('')
            }
        }
        [void]$sb.AppendLine((($cells | ForEach-Object { Csv-Escape $_ }) -join ','))
        $rowCount++
    }
}

[IO.File]::WriteAllText($OutputCsv, $sb.ToString())
Write-Host ("  Rows written       : {0}" -f $rowCount)
Write-Host ("  Output             : {0}" -f $OutputCsv)
