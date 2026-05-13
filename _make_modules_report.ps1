# Aggregate report: for each module with a .mtpl, list test/flow counts in
# the original (.mtpl_orig if present, else current .mtpl) and in the BP
# (compressions.log), plus build status from the latest matching BuildLogs entry.
$tf = Join-Path $PSScriptRoot '_modules_report.md'

function Count-TestsFlows {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return @{ Tests = $null; Flows = $null } }
    $tests = 0; $flows = 0
    foreach ($l in [IO.File]::ReadAllLines($Path)) {
        if ($l -match '^\s*CSharpTest\s+\S+\s+\S+' -or $l -match '^\s*MultiTrialTest\s+\S+\s*$') { $tests++ }
        elseif ($l -match '^\s*Flow\s+\S+') { $flows++ }
    }
    return @{ Tests = $tests; Flows = $flows }
}

# Latest BuildLog status per module (any class)
function Get-BuildStatus {
    param([string]$Module)
    $logs = Get-ChildItem (Join-Path $PSScriptRoot 'BuildLogs') -Filter "${Module}_*" -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending
    if (-not $logs) { return @{ Status = 'NOT BUILT'; Errors = '-'; Warnings = '-'; Class = '-' } }
    $log = $logs[0]
    $cls = if ($log.Name -match "^${Module}_(.+?)_\d{8}_\d{6}\.log$") { $Matches[1] } else { '-' }
    $txt = Get-Content $log.FullName -Raw
    $errs = ([regex]::Matches($txt, '(\d+)\s+Error\(s\)') | Select-Object -Last 1)
    $wars = ([regex]::Matches($txt, '(\d+)\s+Warning\(s\)') | Select-Object -Last 1)
    $errN = if ($errs) { [int]$errs.Groups[1].Value } else { -1 }
    $warN = if ($wars) { [int]$wars.Groups[1].Value } else { -1 }
    $status = if ($txt -match 'Result:\s*PASS' -or ($errN -eq 0 -and $txt -match 'Build Test Program')) { 'PASS' }
              elseif ($errN -gt 0) { 'FAIL' } else { 'UNKNOWN' }
    return @{ Status = $status; Errors = $errN; Warnings = $warN; Class = $cls }
}

# Round-trip status per module: re-run Expand-BluePrint silently and parse result.
function Get-RoundTripStatus {
    param([string]$Module, [string]$BpFile)
    if (-not (Test-Path $BpFile)) { return '-' }
    $out = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'Modules\BluePrint\Expand-BluePrint.ps1') -InputBp $BpFile 2>&1 | Out-String
    if ($out -match 'OK - every test and flow') { return 'OK' }
    if ($out -match '(?s)Tests:.*?diff=(\d+).*?Flows:.*?diff=(\d+)') {
        return "FAIL T:$($Matches[1]) F:$($Matches[2])"
    }
    if ($out -match 'SKIPPED') { return 'NO_ORIG' }
    return 'ERROR'
}

# Discover all modules with a .mtpl
$rows = @()
$mtpls = Get-ChildItem (Join-Path $PSScriptRoot 'Modules') -Recurse -Filter "*.mtpl" -File |
         Where-Object { $_.BaseName -eq $_.Directory.Name }   # only <DIR>/<DIR>.mtpl

foreach ($m in $mtpls | Sort-Object FullName) {
    $name = $m.BaseName
    $group = $m.Directory.Parent.Name
    $orig = Join-Path $m.Directory.FullName "$name.mtpl_orig"
    $useOrig = Test-Path $orig
    $srcPath = if ($useOrig) { $orig } else { $m.FullName }
    $bp     = Join-Path $m.Directory.FullName "BluePrint\${name}_bp.mtpl"

    $oCounts = Count-TestsFlows -Path $srcPath
    $bpCounts = Count-TestsFlows -Path $bp
    $bpExists = Test-Path $bp
    $build = Get-BuildStatus -Module $name
    $rt    = if ($bpExists) { Get-RoundTripStatus -Module $name -BpFile $bp } else { '-' }

    $rows += [PSCustomObject]@{
        Group       = $group
        Module      = $name
        OrigSource  = if ($useOrig) { 'mtpl_orig' } else { 'mtpl' }
        OrigTests   = $oCounts.Tests
        OrigFlows   = $oCounts.Flows
        BpExists    = $bpExists
        BpTests     = if ($bpExists) { $bpCounts.Tests } else { '-' }
        BpFlows     = if ($bpExists) { $bpCounts.Flows } else { '-' }
        RoundTrip   = $rt
        BuildClass  = $build.Class
        BuildStatus = $build.Status
        Errors      = $build.Errors
        Warnings    = $build.Warnings
    }
}

# Write markdown table
$md = @()
$md += "# All-modules BluePrint + build report"
$md += ""
$md += "Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
$md += ""
$md += "Modules with a top-level ``<DIR>/<DIR>.mtpl``: $($rows.Count)"
$md += ""
$md += "Columns:"
$md += "- **Orig src**: ``mtpl_orig`` (BluePrint cycle ran) or ``mtpl`` (no orig snapshot, counts taken from current .mtpl)"
$md += "- **Orig Tests / Orig Flows**: tests / flows in the original source"
$md += "- **BP Tests / BP Flows**: tests / flows in the generated ``_bp.mtpl`` (- means no BP yet)"
$md += "- **Round-trip**: re-running Expand reproduces every test/flow in mtpl_orig (OK / FAIL T:n F:n / NO_ORIG / -)"
$md += "- **Build**: latest result from ``BuildLogs/`` (NOT BUILT = no .mtproj or never invoked)"
$md += ""
$md += "| # | Group | Module | Orig src | Orig Tests | Orig Flows | BP Tests | BP Flows | Round-trip | Build class | Build | Errors | Warnings |"
$md += "|---:|---|---|---|---:|---:|---:|---:|---|---|---|---:|---:|"
$shown = @($rows | Where-Object { $_.BuildStatus -ne 'NOT BUILT' })
$i = 0
foreach ($r in $shown) {
    $i++
    $md += "| $i | $($r.Group) | **$($r.Module)** | $($r.OrigSource) | $($r.OrigTests) | $($r.OrigFlows) | $($r.BpTests) | $($r.BpFlows) | $($r.RoundTrip) | $($r.BuildClass) | $($r.BuildStatus) | $($r.Errors) | $($r.Warnings) |"
}

# Totals
$nPass = ($rows | Where-Object BuildStatus -eq 'PASS').Count
$nFail = ($rows | Where-Object BuildStatus -eq 'FAIL').Count
$nNB   = ($rows | Where-Object BuildStatus -eq 'NOT BUILT').Count
$nBp   = ($rows | Where-Object BpExists -eq $true).Count
$md += ""
$md += "## Totals"
$md += "- Modules total: $($rows.Count)"
$md += "- With BluePrint generated: $nBp"
$md += "- Build PASS: $nPass"
$md += "- Build FAIL: $nFail"
$md += "- Not built (no .mtproj or never invoked): $nNB"

$md -join "`n" | Set-Content -Path $tf -Encoding UTF8
Write-Host "Report written to: $tf"
$rows | Format-Table -AutoSize
