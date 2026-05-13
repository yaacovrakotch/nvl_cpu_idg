# Build all unique modules from 18 CXX + 5 non-CXX picks; write summary table to file.
$tf = Join-Path $PSScriptRoot '_build_summary.md'
Remove-Item $tf -ErrorAction SilentlyContinue

# Module -> first referencing class (pre-discovered)
$moduleClass = [ordered]@{
    'ARR_ATOM_CXX'     = 'Class_DNL_S28C'
    'ARR_CCF_CXX'      = 'Class_DNL_S28C'
    'ARR_CORE_CXX'     = 'Class_DNL_S28C'
    'ARR_HBM_CXX'      = 'Class_DNL_S28C'
    'ARR_RING_CXX'     = 'Class_DNL_S28C'
    'ARR_UNCORE_CXX'   = 'Class_DNL_S28C'
    'CLK_BASE_CS40'    = 'Class_DNL_S28C'
    'DRV_RESET_CXX'    = 'Class_DNL_S28C'
    'DRV_TAP_CXX'      = 'Class_DNL_S28C'
    'FUN_ATOM_CX48'    = 'Class_NVL_H16C'
    'FUS_FSG_CXX'      = 'Class_DNL_S28C'
    'FUS_FUSEBURN_CXX' = 'Class_DNL_S28C'
    'MIO_HPTP_CXPKGHX' = 'Class_NVL_H16C'
    'PTH_BGR_CJ816P'   = 'Class_DNL_S28C'
    'PTH_PVT_CXX'      = 'Class_DNL_S28C'
    'PTH_VDAC_CXX'     = 'Class_DNL_S28C'
    'PTH_VID_CXX'      = 'Class_DNL_S28C'
    'PTH_VMIN_CXX'     = 'Class_DNL_S28C'
    'QNR_CARV_CXX'     = 'Class_DNL_S28C'
    'SCN_ATOM_CX48'    = 'Class_NVL_H16C'
    'SCN_CONFIG_CXX'   = 'Class_DNL_S28C'
    'SCN_CORE_CXX'     = 'Class_DNL_S28C'
    'SCN_RING_CXX'     = 'Class_DNL_S28C'
    'SCN_UNCORE_CXX'   = 'Class_DNL_S28C'
    'TPI_DAS_CXX'      = 'Class_NVL_H16C'
    'TPI_LJ_CXX'       = 'Class_DNL_S28C'
}

$rows = @()
$idx = 0
$total = $moduleClass.Count
foreach ($m in $moduleClass.Keys) {
    $idx++
    $cls = $moduleClass[$m]
    Write-Host ""
    Write-Host "[$idx/$total] Building $m ($cls)..." -ForegroundColor Cyan

    $out = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'build_modules.ps1') -Modules $m -Class $cls 2>&1 | Out-String

    # Parse last "N Error(s)" / "N Warning(s)"
    $errMatches = [regex]::Matches($out, '(\d+)\s+Error\(s\)')
    $warMatches = [regex]::Matches($out, '(\d+)\s+Warning\(s\)')
    $errors   = if ($errMatches.Count -gt 0) { $errMatches[$errMatches.Count - 1].Groups[1].Value } else { '?' }
    $warnings = if ($warMatches.Count -gt 0) { $warMatches[$warMatches.Count - 1].Groups[1].Value } else { '?' }
    $result = if ($out -match '(?m)^\s*SUCCESS\s*$' -or $out -match 'All builds passed') { 'PASS' }
              elseif ($out -match 'FAILED \(exit code') { 'FAIL' }
              else { 'UNKNOWN' }

    $rows += [PSCustomObject]@{
        Module   = $m
        Class    = $cls
        Errors   = $errors
        Warnings = $warnings
        Result   = $result
    }

    Write-Host "  -> $result (errors=$errors warnings=$warnings)" -ForegroundColor (@{PASS='Green';FAIL='Red'}[$result])
}

# Write summary
$md = @()
$md += "# BluePrint module build summary"
$md += ""
$md += "Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
$md += ""
$md += "Modules built: $($rows.Count) (18 CXX + 5 non-CXX picks from one-per-group cycle)"
$md += ""
$md += "| # | Module | Class | Errors | Warnings | Build |"
$md += "|---:|---|---|---:|---:|---|"
$i = 0
foreach ($r in $rows) {
    $i++
    $md += "| $i | **$($r.Module)** | $($r.Class) | $($r.Errors) | $($r.Warnings) | $($r.Result) |"
}
$md += ""
$pass = ($rows | Where-Object Result -eq 'PASS').Count
$fail = ($rows | Where-Object Result -eq 'FAIL').Count
$unk  = ($rows | Where-Object Result -eq 'UNKNOWN').Count
$md += "## Totals"
$md += "- PASS: $pass"
$md += "- FAIL: $fail"
$md += "- UNKNOWN: $unk"
$md += ""
$md += "Per-build torch logs are under ``BuildLogs/``."
$md -join "`n" | Set-Content -Path $tf -Encoding UTF8

Write-Host ""
Write-Host "Build summary written to: $tf" -ForegroundColor Yellow
$rows | Format-Table -AutoSize
