@ECHO off
SET SSCEXEPATH=%HDMTTOS%\Runtime\Release
REM Make it work on the Cart/HDE

%SSCEXEPATH%\SingleScriptCmd.exe setInstanceParam "TPI_BASE_XXX::CTRL_X_PRIMELOTSTART_K_LOTSTARTFLOW_X_X_X_X_PRIMESTARTLOTDATALOG" "StreamDestination" "OUTPUT_TO_FILE" 
%SSCEXEPATH%\SingleScriptCmd.exe setInstanceParam "TPI_BASE_XXX::CTRL_X_UF_E_TESTPLANSTARTFLOW_X_X_X_X_PINPROFILERSTARTMONITOR" "BypassPort" 1

%SSCEXEPATH%\SingleScriptCmd.exe setInstanceParam "TPI_XIU_XXX::CTRL_X_TDRCAL_K_INIT_X_X_X_X_TDRCLIBRATION" "LoadDataFromFile" "TRUE"
%SSCEXEPATH%\SingleScriptCmd.exe setInstanceParam "TPI_XIU_XXX::CTRL_X_XIUPOWERSUPPLY_K_INIT_X_X_X_X_XIUCONTINUITY" "BypassPort" 1
%SSCEXEPATH%\SingleScriptCmd.exe setInstanceParam "TPI_XIU_XXX::CTRL_X_XIUPINLEAKGE_K_INIT_X_X_X_X_XIUHVMLEAKAGE" "BypassPort" 1

%SSCEXEPATH%\SingleScriptCmd.exe setInstanceParam "IPC::PTH_DTS_CXPKGS7::DTS_X_PATMOD_E_LTTCCPU_X_X_X_X" "BypassPort" 1
%SSCEXEPATH%\SingleScriptCmd.exe setInstanceParam "IPC::PTH_DTS_CXPKGS7::DTS_X_PATMOD_E_LTTCCPU_X_X_X_X_DLVR_RESET_VOLTAGE" "BypassPort" 1
%SSCEXEPATH%\SingleScriptCmd.exe setInstanceParam "IPC::PTH_DTS_CXPKGS7::DTS_X_PATMOD_E_STARTANA0CPU_X_X_X_X" "BypassPort" 1
%SSCEXEPATH%\SingleScriptCmd.exe setInstanceParam "IPC::PTH_DTS_CXPKGS7::DTS_X_PATMOD_E_STARTANA0CPU_X_X_X_X_DLVR_RESET_VOLTAGE" "BypassPort" 1
%SSCEXEPATH%\SingleScriptCmd.exe setInstanceParam "YBS_UPSS_XXX::UPSS_X_UPSENGINERUNNER_K_LTTCPOST_X_X_X_X_UPSS" "BypassPort" 1

%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_BENCHTOP" "1"
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_PACKAGE" "66"
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_DEVICE" "4AAB2V"
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_REV" ""
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_STEP" "B"
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_TEMPERATURE" "70"
