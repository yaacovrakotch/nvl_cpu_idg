@echo off

for %%I in (.) do set CurrDirName=%%~nxI
echo %CurrDirName%

cd ..
cd torch-extinguisher

set MINOR_VERSION=0
for /f %%i in ('py -3 -c "import sys; print(sys.version_info[1])"') do set MINOR_VERSION=%%i

if %MINOR_VERSION% lss 6 (
    echo "python 3.6 or later must be used, please install a new python version"
    py --list
    pause
    exit
)

py -3 --version

py -3 -u "torch_extinguisher.py" -r "../.." -m %CurrDirName% -i "../"

if %ERRORLEVEL% neq 0 (
    pause
)