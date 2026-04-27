ECHO off
SET SSCEXEPATH=%HDMTTOS%\Runtime\Release
REM Make it work on the Cart/HDE


%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_FACTMODE" "LotLevel"
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_FACILITYIID" "JF1"
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_TWOSTEPFACT" "FALSE"
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_FACTPROCESSSTEP" "CLASSHOT"
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_FLEXBOMRECIPE" "FFFFFFF00000"
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_LRFDOWNLOADPATH" "~HDMT_TPL_DIR\Shared\Modules\FUS\FUS_FACT_XXX\fact_offlineval\DUMMYLOT_OneStep_LRF.xml"
%SSCEXEPATH%\SingleScriptCmd.exe setUserVar "SCVars" "SC_FRFPATH" "~HDMT_TPL_DIR\Shared\Modules\FUS\FUS_FACT_XXX\fact_offlineval\fact_rules_sfp.xml"