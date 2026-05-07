<#
.SYNOPSIS
    Extracts and compares test instances from test programs via the TestInstanceComparison tool.

.DESCRIPTION
    Wrapper script for the ApiSamples.TestInstanceComparison tool.
    Supports three invocation strategies (in priority order):
      1. Published .exe in Skills\TestInstanceComparison\ (fastest)
      2. dotnet run via UNC path to SmartTP-Class repository
      3. dotnet run via relative path fallback

    Modes:
      - Single : Extract test instances from a single test program
      - Compare: Compare test instances between two test programs
      - MCP    : Run as MCP server for AI assistant integration

.PARAMETER Mode
    One of: single (default), compare, mcp.

.PARAMETER StplPath
    Path to the SubTestPlan.stpl file for the first (or only) test program.

.PARAMETER TplPath
    Path to the BaseTestPlan.tpl file for the first (or only) test program.

.PARAMETER ModuleName
    Module name pattern to search for (e.g. ARR_ATN_CDIE). Case-insensitive substring match.

.PARAMETER OutputCsvPath
    Path for the output CSV report file.

.PARAMETER StplPath2
    (Compare mode only) Path to the SubTestPlan.stpl file for the second test program.

.PARAMETER TplPath2
    (Compare mode only) Path to the BaseTestPlan.tpl file for the second test program.

.EXAMPLE
    .\compare_test_instances.ps1 -StplPath "\\path\to\SubTestPlan.stpl" -TplPath "\\path\to\BaseTestPlan.tpl" -ModuleName "ARR_ATN_CDIE" -OutputCsvPath "C:\output\results.csv"

.EXAMPLE
    .\compare_test_instances.ps1 -Mode compare -StplPath "\\tp1\SubTestPlan.stpl" -TplPath "\\tp1\BaseTestPlan.tpl" -StplPath2 "\\tp2\SubTestPlan.stpl" -TplPath2 "\\tp2\BaseTestPlan.tpl" -ModuleName "ARR_ATN_CDIE" -OutputCsvPath "C:\output\comparison.csv"

.EXAMPLE
    .\compare_test_instances.ps1 -Mode mcp
#>
param(
    [ValidateSet("single", "compare", "mcp")]
    [string]$Mode = "single",

    [string]$StplPath = "",

    [string]$TplPath = "",

    [string]$ModuleName = "",

    [string]$OutputCsvPath = "",

    [string]$StplPath2 = "",
    [string]$TplPath2 = "",
    [switch]$NoFeedback
)

. "$PSScriptRoot\_common.ps1"
$env:HTTP_PROXY = ""; $env:HTTPS_PROXY = ""

$exeLocations = @(
    (Join-Path $PSScriptRoot "TestInstanceComparison" "ApiSamples.TestInstanceComparison.exe"),
    "I:\engineering\dev\user_links\yrakotch\LLM\CODE\TestInstanceComparison\ApiSamples.TestInstanceComparison.exe"
)
$exePath = $exeLocations | Where-Object { Test-Path $_ } | Select-Object -First 1
$useExe = $null -ne $exePath

$projectPath = ""
if (-not $useExe) {
    $projectPath = "\\ger.corp.intel.com\ec\proj\mdl\ha\intel\engineering\dev\sctp\SmartTP-Class\common\Tools\ApiSamples.TestInstanceComparison"

    if (-not (Test-Path $projectPath)) {
        $projectPath = Join-Path $PSScriptRoot ".." "SmartTP-Class" "common" "Tools" "ApiSamples.TestInstanceComparison"
        $projectPath = (Resolve-Path $projectPath -ErrorAction SilentlyContinue).Path

        if (-not $projectPath -or -not (Test-Path $projectPath)) {
            Write-Error "ERROR: Cannot locate the ApiSamples.TestInstanceComparison project or published .exe. Checked:`n  1. $($exeLocations -join "`n  2. ")`n  3. UNC SmartTP-Class`n  4. Relative path"
            exit 1
        }
    }
}

Write-Host "=== TestInstanceComparison Skill ===" -ForegroundColor Cyan
if ($useExe) {
    Write-Host "  Executable : $exePath"
} else {
    Write-Host "  Project    : $projectPath"
}
Write-Host "  Mode       : $Mode"

if ($Mode -ne "mcp") {
    Write-Host "  STPL       : $StplPath"
    Write-Host "  TPL        : $TplPath"
    Write-Host "  Module     : $ModuleName"
    Write-Host "  Output     : $OutputCsvPath"
    if ($Mode -eq "compare") {
        Write-Host "  STPL2      : $StplPath2"
        Write-Host "  TPL2       : $TplPath2"
    }
}
Write-Host ""

switch ($Mode) {
    "single" {
        if (-not $StplPath -or -not $TplPath -or -not $ModuleName -or -not $OutputCsvPath) {
            Write-Error "ERROR: Single mode requires -StplPath, -TplPath, -ModuleName, and -OutputCsvPath parameters."
            exit 1
        }
        $toolArgs = @($StplPath, $TplPath, $ModuleName, $OutputCsvPath)
    }
    "compare" {
        if (-not $StplPath -or -not $TplPath -or -not $StplPath2 -or -not $TplPath2 -or -not $ModuleName -or -not $OutputCsvPath) {
            Write-Error "ERROR: Compare mode requires -StplPath, -TplPath, -StplPath2, -TplPath2, -ModuleName, and -OutputCsvPath parameters."
            exit 1
        }
        $toolArgs = @($StplPath, $TplPath, $StplPath2, $TplPath2, $ModuleName, $OutputCsvPath)
    }
    "mcp" {
        $toolArgs = @("--mcp")
    }
}

if ($useExe) {
    Write-Host "Running: `"$exePath`" $($toolArgs -join ' ')" -ForegroundColor DarkGray
    Write-Host ""
    $start = Get-Date
    & $exePath @toolArgs
} else {
    Write-Host "Running: dotnet run --project `"$projectPath`" -- $($toolArgs -join ' ')" -ForegroundColor DarkGray
    Write-Host ""
    $start = Get-Date
    & dotnet run --project "$projectPath" -- @toolArgs
}

$exitCode = $LASTEXITCODE
$dur = ((Get-Date) - $start).TotalSeconds
Write-Host ""
Write-Host "=== TestInstanceComparison finished with exit code: $exitCode ===" -ForegroundColor $(if ($exitCode -eq 0) { "Green" } else { "Red" })

Write-UsageLog -SkillName "TestInstanceComparison" -Lot "" -Operation "" -Socket "" -ExitCode $exitCode -DurationSec $dur
Request-Feedback -SkillName "TestInstanceComparison" -Skip:$NoFeedback
exit $exitCode
