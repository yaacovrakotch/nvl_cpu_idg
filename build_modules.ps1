param(
    [string]$torchExe = "I:\tpapps\TORCH\Prod22\CLI\torch.exe",
    [string]$solution = "NVL_CPU.sln",

    # Examples:
    #   .\build_modules.ps1 -Classes All                                                   # Build all classes
    #   .\build_modules.ps1 -Classes Class_NVL_HX28C                                       # Build one class
    #   .\build_modules.ps1 -Classes Class_NVL_HX28C, Class_NVL_S28C                       # Build multiple classes
    #   .\build_modules.ps1 -Modules DRV_RESET_CKX -Class Class_NVL_H16C                   # Build one module
    #   .\build_modules.ps1 -Modules DRV_RESET_CKX, ARR_ATOM_CXX -Class Class_NVL_H16C     # Build multiple modules
    [string[]]$Classes = @(),
    [string[]]$Modules = @(),
    [string]$Class = "",
    [switch]$InstallTorch = $false,

    # Directory for build log files. Each build produces a log file that can be used by a workflow to diagnose and fix errors.
    [string]$LogDir = "BuildLogs"
)

$ErrorActionPreference = "Stop"

# Ensure log directory exists
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

function Invoke-TorchBuild {
    param(
        [string]$Label,
        [string[]]$TorchArgs,
        [string]$LogFile
    )

    Write-Host ""
    Write-Host "=== Building $Label ===" -ForegroundColor Cyan
    Write-Host "  Log: $LogFile"

    # Run torch and capture output to both console and log file
    $output = & $torchExe @TorchArgs 2>&1
    $output | Out-File -FilePath $LogFile -Encoding UTF8

    # Also display to console
    $output | ForEach-Object { Write-Host $_ }

    # Extract error/warning summary from output
    $errors = ($output | Select-String -Pattern "(\d+) Error\(s\)" | ForEach-Object { $_.Matches[0].Groups[1].Value }) | Select-Object -Last 1
    $warnings = ($output | Select-String -Pattern "(\d+) Warning\(s\)" | ForEach-Object { $_.Matches[0].Groups[1].Value }) | Select-Object -Last 1

    # Append summary to log
    "" | Out-File -FilePath $LogFile -Append -Encoding UTF8
    "--- BUILD SUMMARY ---" | Out-File -FilePath $LogFile -Append -Encoding UTF8
    "Label: $Label" | Out-File -FilePath $LogFile -Append -Encoding UTF8
    "ExitCode: $LASTEXITCODE" | Out-File -FilePath $LogFile -Append -Encoding UTF8
    "Errors: $errors" | Out-File -FilePath $LogFile -Append -Encoding UTF8
    "Warnings: $warnings" | Out-File -FilePath $LogFile -Append -Encoding UTF8
    "Result: $(if ($LASTEXITCODE -eq 0) { 'PASS' } else { 'FAIL' })" | Out-File -FilePath $LogFile -Append -Encoding UTF8

    return $LASTEXITCODE
}

if ($InstallTorch) {
    Write-Host "=== Torch install ===" -ForegroundColor Cyan
    & $torchExe install
    if ($LASTEXITCODE -ne 0) { Write-Error "Torch install failed with exit code $LASTEXITCODE"; exit $LASTEXITCODE }
}

$failed = @()
$succeeded = @()
$logFiles = @()

if ($Modules.Count -gt 0) {
    # --- Module-level build (torch build with .mtproj + class configuration) ---

    if (-not $Class) {
        Write-Host "ERROR: -Class is required when using -Modules." -ForegroundColor Red
        Write-Host "Example: .\build_modules.ps1 -Modules DRV_RESET_CKX -Class Class_NVL_H16C"
        exit 1
    }

    foreach ($moduleName in $Modules) {
        $mtproj = Get-ChildItem -Path "Modules", "Shared\Modules" -Filter "$moduleName.mtproj" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
        if (-not $mtproj) {
            Write-Host "ERROR: Module '$moduleName' not found (.mtproj not found under Modules/ or Shared/Modules/)" -ForegroundColor Red
            $failed += $moduleName
            continue
        }

        $mtprojRelative = $mtproj.FullName.Replace((Get-Item .).FullName + "\", "")
        $logFile = Join-Path $LogDir "${moduleName}_${Class}_${timestamp}.log"
        $logFiles += $logFile

        Write-Host "  Solution: $solution"
        Write-Host "  Project:  $mtprojRelative"
        Write-Host "  Config:   $Class"

        $exitCode = Invoke-TorchBuild -Label "$moduleName ($Class)" -TorchArgs @("build", "-s", $solution, "-p", $mtprojRelative, "--ms", "/p:Configuration=$Class", "/p:Platform=Any CPU", "-v", "Normal") -LogFile $logFile

        if ($exitCode -ne 0) {
            Write-Host "  FAILED (exit code $exitCode)" -ForegroundColor Red
            $failed += $moduleName
        } else {
            Write-Host "  SUCCESS" -ForegroundColor Green
            $succeeded += $moduleName
        }
    }
} elseif ($Classes.Count -gt 0) {
    # --- Class-level build (torch build with .tpproj) ---

    $allTpprojs = Get-ChildItem -Path "POR_TP" -Filter "*.tpproj" -Recurse
    if ($allTpprojs.Count -eq 0) { Write-Error "No .tpproj files found under POR_TP/"; exit 1 }

    if ($Classes.Count -eq 1 -and $Classes[0] -eq "All") {
        $selectedTpprojs = $allTpprojs
    } else {
        $selectedTpprojs = $allTpprojs | Where-Object { $Classes -contains $_.Directory.Name }
        if ($selectedTpprojs.Count -eq 0) {
            Write-Host "No matching classes found. Available:" -ForegroundColor Red
            $allTpprojs | ForEach-Object { Write-Host "  - $($_.Directory.Name)" }
            exit 1
        }
    }

    foreach ($tpproj in $selectedTpprojs) {
        $className = $tpproj.Directory.Name
        $tpprojRelative = $tpproj.FullName.Replace((Get-Item .).FullName + "\", "")
        $logFile = Join-Path $LogDir "${className}_${timestamp}.log"
        $logFiles += $logFile

        Write-Host "  Solution: $solution"
        Write-Host "  TPProj:   $tpprojRelative"

        $exitCode = Invoke-TorchBuild -Label $className -TorchArgs @("build", "-s", $solution, "-p", $tpprojRelative, "--restore", "--ms", "/property:Configuration=Release", "-v", "Normal") -LogFile $logFile

        if ($exitCode -ne 0) {
            Write-Host "  FAILED (exit code $exitCode)" -ForegroundColor Red
            $failed += $className
        } else {
            Write-Host "  SUCCESS" -ForegroundColor Green
            $succeeded += $className
        }
    }
} else {
    Write-Host "ERROR: Specify either -Classes or -Modules." -ForegroundColor Red
    Write-Host ""
    Write-Host "Usage:"
    Write-Host "  .\build_modules.ps1 -Classes All"
    Write-Host "  .\build_modules.ps1 -Classes Class_NVL_HX28C"
    Write-Host "  .\build_modules.ps1 -Modules DRV_RESET_CKX -Class Class_NVL_H16C"
    exit 1
}

# Summary
Write-Host ""
Write-Host "=== Build Summary ===" -ForegroundColor Cyan
Write-Host "  Succeeded: $($succeeded.Count) - $($succeeded -join ', ')" -ForegroundColor Green
if ($failed.Count -gt 0) {
    Write-Host "  Failed:    $($failed.Count) - $($failed -join ', ')" -ForegroundColor Red
}
Write-Host "  Log files:" -ForegroundColor Yellow
$logFiles | ForEach-Object { Write-Host "    $_" }

if ($failed.Count -gt 0) {
    exit 1
} else {
    Write-Host "  All builds passed!" -ForegroundColor Green
    exit 0
}
