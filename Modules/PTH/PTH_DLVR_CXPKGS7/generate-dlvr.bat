@echo off
setlocal enabledelayedexpansion

REM =========================================================
REM Root = 3 levels up from CXPKGS7
REM =========================================================
set "root=%~dp0..\..\.."
for %%i in ("%root%") do set "root=%%~fi"

set "base=%root%\Modules\PTH"

REM =========================================================
REM Step 1: Already inside CXPKGS7
REM =========================================================
cd /d "%~dp0"
echo RUNNING: PTH_DLVR_CXPKGS7

python "%root%\Shared\BaseInputs\pytpd\main\pymtpl.py" ^
  -env "%root%\POR_TP\Class_NVL_S28C\EnvironmentFile.env" ^
  "%base%\PTH_DLVR_CXPKGS7\PTH_DLVR_pymtpl.py"

REM =========================================================
REM Step 2: Move generated files
REM =========================================================
for %%F in (PTH_DLVR_*.mtpl PTH_DLVR_*.flw PTH_DLVR_*_SubBinDefinitions.sbdefs) do (

    set "filename=%%~nF"
    set "module=!filename!"

    REM Remove suffix for sbdefs
    if "!module:~-18!"=="_SubBinDefinitions" (
        set "module=!module:~0,-18!"
    )

    set "destDir=%base%\!module!"

    if not exist "!destDir!" (
        mkdir "!destDir!"
        echo CREATED: !destDir!
    )

    move /Y "%%F" "!destDir!\%%~nxF" >nul
    echo MOVED: %%~nxF ^> !destDir!
)

endlocal
pause