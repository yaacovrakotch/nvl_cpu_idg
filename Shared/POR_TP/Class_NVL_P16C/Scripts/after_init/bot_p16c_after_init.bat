ECHO off
SET SSCEXEPATH=%HDMTTOS%\Runtime\Release
REM Make it work on the Cart/HDE

%SSCEXEPATH%\SingleScriptCmd.exe setInstanceParam "TPI_DFF_XXX::DFFX_X_PRIMEULT_K_STARTPREPRL1_X_X_X_X_DUMMYULT" "BypassPort" 1
REM %SSCEXEPATH%\SingleScriptCmd.exe setInstanceParam "TPI_MIXDETCT_XXX::CTRL_X_MIXDET_K_STARTPREPRL1_X_X_X_X_DLCPMIXDET" "BypassPort" 1

%SSCEXEPATH%\SingleScriptCmd.exe setInstanceParam "TPI_DFF_XXX::DFFX_X_DFFREAD_K_STARTPREPRL1_X_X_X_X_DFFREAD" "EnabledModules" "NONKILL"
%SSCEXEPATH%\SingleScriptCmd.exe setInstanceParam "TPI_DFF_XXX::DFFX_X_DFFENDFLOW_K_FINAL_X_X_X_X_DFFVAL" "BypassPort" 1
%SSCEXEPATH%\SingleScriptCmd.exe setInstanceParam "PTH_CEP_HKPKGS7::CEP_X_SCREEN_E_BEGINHUBPKG_X_X_X_X_CEP_EVENT0_CALC" "BypassPort" 1