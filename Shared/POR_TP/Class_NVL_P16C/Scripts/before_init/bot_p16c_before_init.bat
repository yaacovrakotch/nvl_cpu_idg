@ECHO off
SET SSCEXEPATH=%HDMTTOS%\Runtime\Release
REM Make it work on the Cart/HDE

%SSCEXEPATH%\SingleScriptCmd.exe setInstanceParam "TPI_BASE_XXX::CTRL_X_PRIMELOTSTART_K_LOTSTARTFLOW_X_X_X_X_PRIMESTARTLOTDATALOG" "StreamDestination" "OUTPUT_TO_FILE" 
%SSCEXEPATH%\SingleScriptCmd.exe setInstanceParam "TPI_BASE_XXX::CTRL_X_UF_E_TESTPLANSTARTFLOW_X_X_X_X_PINPROFILERSTARTMONITOR" "BypassPort" 1

%SSCEXEPATH%\SingleScriptCmd.exe setInstanceParam "TPI_XIU_XXX::CTRL_X_TDRCAL_K_INIT_X_X_X_X_TDRCLIBRATION" "LoadDataFromFile" "TRUE"
%SSCEXEPATH%\SingleScriptCmd.exe setInstanceParam "TPI_XIU_XXX::CTRL_X_XIUPOWERSUPPLY_K_INIT_X_X_X_X_XIUCONTINUITY" "BypassPort" 1
%SSCEXEPATH%\SingleScriptCmd.exe setInstanceParam "TPI_XIU_XXX::CTRL_X_XIUPINLEAKGE_K_INIT_X_X_X_X_XIUHVMLEAKAGE" "BypassPort" 1
%SSCEXEPATH%\SingleScriptCmd.exe setInstanceParam "TPI_XIU_XXX::CTRL_X_XIUIDENTITY_K_INIT_X_X_X_X_XIUNAME" "ValidTiuRegex" "^BB2T4H1P[0-9]+:NVL[H|P][X|Z|B][a-zA-Z0-9]+[T|F][0-9]+$"

%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_BENCHTOP" "1"
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_PACKAGE" "69"
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_DEVICE" "4AAA2V"
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_STEP" "A"
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_REV" ""
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_TEMPERATURE" "100"

