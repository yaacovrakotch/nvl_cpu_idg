ECHO off
SET SSCEXEPATH=%HDMTTOS%\Runtime\Release
REM Make it work on the Cart/HDE

%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_LOCN" "6197"
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_CURRENT_PROCESS_STEP" "FUSE"
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_CURRENT_PROCESS_TYPE" "FUSE"
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_FACTPROCESSSTEP" "FUSE"
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_FACILITYID" "JF1"
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_FACTMODE" "OFF"
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_FLEXBOMRECIPE" "000000000000"
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_TWOSTEPFACT" "TRUE"
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_LRFDOWNLOADPATH" ""
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_FRFPATH" ""