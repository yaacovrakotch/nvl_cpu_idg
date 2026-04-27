ECHO off
SET SSCEXEPATH=%HDMTTOS%\Runtime\Release
REM Make it work on the Cart/HDE

REM setting SC uservars
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_TEMPERATURE" "25"
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_LOCN" "6248"
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_CURRENT_PROCESS_STEP" "PHMROOM"
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_CURRENT_PROCESS_TYPE" "PHMROOM"
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_BENCHTOP" "1"



ECHO DONE with SCRIPT..
