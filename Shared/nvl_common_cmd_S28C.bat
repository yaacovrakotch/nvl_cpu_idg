ECHO off
SET SSCEXEPATH=%HDMTTOS%\Runtime\Release
REM Make it work on the Cart/HDE

REM bot_s28c_before_init.bat
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_FACILITYID" "%COMPUTERNAME%"
%SSCEXEPATH%\SingleScriptCmd.exe setInstanceParam "TPI_BASE_XXX::CTRL_X_PRIMELOTSTART_K_LOTSTARTFLOW_X_X_X_X_PRIMESTARTLOTDATALOG" "StreamDestination" "OUTPUT_TO_FILE" 
%SSCEXEPATH%\SingleScriptCmd.exe setInstanceParam "TPI_BASE_XXX::CTRL_X_UF_E_TESTPLANSTARTFLOW_X_X_X_X_PINPROFILERSTARTMONITOR" "BypassPort" 1

REM Run XIU normally
REM %SSCEXEPATH%\SingleScriptCmd.exe setInstanceParam "TPI_XIU_XXX::CTRL_X_TDRCAL_K_INIT_X_X_X_X_TDRCLIBRATION" "LoadDataFromFile" "TRUE"
REM %SSCEXEPATH%\SingleScriptCmd.exe setInstanceParam "TPI_XIU_XXX::CTRL_X_XIUPOWERSUPPLY_K_INIT_X_X_X_X_XIUCONTINUITY" "BypassPort" 1
REM %SSCEXEPATH%\SingleScriptCmd.exe setInstanceParam "TPI_XIU_XXX::CTRL_X_XIUPINLEAKGE_K_INIT_X_X_X_X_XIUHVMLEAKAGE" "BypassPort" 1

REM Prompt user for RCC mode
ECHO.
powershell -Command "Write-Host 'Is this activity for RCC on the x10? (Y/N): ' -ForegroundColor Yellow -NoNewline"
SET /P RCC_MODE=
SET SC_BENCHTOP_VALUE=1
IF /I "%RCC_MODE:~0,1%"=="Y" SET SC_BENCHTOP_VALUE=-1
IF /I "%RCC_MODE:~0,1%"=="N" SET SC_BENCHTOP_VALUE=1
powershell -Command "Write-Host 'Setting SC_BENCHTOP to: %SC_BENCHTOP_VALUE%' -ForegroundColor Cyan"

%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_BENCHTOP" "%SC_BENCHTOP_VALUE%"
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_PACKAGE" "63"
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_DEVICE" "4AAA2V"
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_REV" ""
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_STEP" "C"

REM bot_s28c_after_init.bat
%SSCEXEPATH%\SingleScriptCmd.exe setInstanceParam "TPI_MIXDETCT_XXX::CTRL_X_MIXDET_K_STARTPREPRL1_X_X_X_X_DLCPMIXDET" "BypassPort" 1

%SSCEXEPATH%\SingleScriptCmd.exe setInstanceParam "TPI_DFF_XXX::DFFX_X_DFFREAD_K_STARTPREPRL1_X_X_X_X_DFFREAD" "EnabledModules" "NONKILL"
%SSCEXEPATH%\SingleScriptCmd.exe setInstanceParam "TPI_DFF_XXX::DFFX_X_DFFENDFLOW_K_FINAL_X_X_X_X_DFFVAL" "BypassPort" 1
%SSCEXEPATH%\SingleScriptCmd.exe setInstanceParam "PTH_CEP_HKPKGS7::CEP_X_SCREEN_E_BEGINHUBPKG_X_X_X_X_CEP_EVENT0_CALC" "BypassPort" 1
%SSCEXEPATH%\SingleScriptCmd.exe setInstanceParam "IPH::PTH_DTS_HXPKGS7::DTS_X_SCREEN_K_LTTCHUB_X_X_X_X_DTSCALC" "BypassPort" 1
%SSCEXEPATH%\SingleScriptCmd.exe setInstanceParam "IPH::PTH_DTS_HXPKGS7::DTS_X_GSDS2DFF_E_LTTCHUB_X_X_X_X_SDTCLASS" "BypassPort" 1