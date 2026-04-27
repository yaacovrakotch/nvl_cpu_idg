ECHO off
SET SSCEXEPATH=%HDMTTOS%\Runtime\Release
REM Make it work on the Cart/HDE

%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_LOCN" "6248"
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_FACILITYIID" "JF1"
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_FACTMODE" "OFF"
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_FLEXBOMRECIPE" "000000000000"
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_TWOSTEPFACT" "TRUE"
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_LRFDOWNLOADPATH" ""
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_FRFPATH" ""