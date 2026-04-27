ECHO off
SET SSCEXEPATH=%HDMTTOS%\Runtime\Release
REM Make it work on the Cart/HDE

%SSCEXEPATH%\SingleScriptCmd.exe setInstanceParam "TPI_MIXDETCT_XXX::CTRL_X_MIXDET_K_STARTPREPRL1_X_X_X_X_DLCPMIXDET" "BypassPort" 1

REM DFF NONKILL
%SSCEXEPATH%\SingleScriptCmd.exe setInstanceParam "TPI_DFF_XXX::DFFX_X_DFFREAD_K_STARTPREPRL1_X_X_X_X_DFFREAD" "EnabledModules" "NONKILL"
%SSCEXEPATH%\SingleScriptCmd.exe setInstanceParam "TPI_DFF_XXX::DFFX_X_DFFENDFLOW_K_FINAL_X_X_X_X_DFFVAL" "BypassPort" 1
%SSCEXEPATH%\SingleScriptCmd.exe setInstanceParam "PTH_CEP_HKPKGS7::CEP_X_SCREEN_E_BEGINHUBPKG_X_X_X_X_CEP_EVENT0_CALC" "BypassPort" 1
%SSCEXEPATH%\SingleScriptCmd.exe setInstanceParam "IPH::PTH_DTS_HXPKGS7::DTS_X_SCREEN_K_LTTCHUB_X_X_X_X_DTSCALC" "BypassPort" 1
%SSCEXEPATH%\SingleScriptCmd.exe setInstanceParam "IPH::PTH_DTS_HXPKGS7::DTS_X_GSDS2DFF_E_LTTCHUB_X_X_X_X_SDTCLASS" "BypassPort" 1

%SSCEXEPATH%\SingleScriptCmd.exe setInstanceParam "IPC::ARR_CCF_CXX::SSA_CCF_SB_K_ENDCPU_X_VNNAON_NOM_1200_LLCSRAM_PMUX" "BypassPort" 1

REM Setup dtscalc gold
REM - Temporarily removing the file below for DTS PR validation.
REM %SSCEXEPATH%\SingleScriptCmd.exe setInstanceParam "IPC::PTH_DTS_CXPKGS7::DTS_X_SCREEN_K_STARTANA0CPU_X_X_X_X_DTSCALC" "ScreenTestsFile" "./InputFiles/N2P_261_dtscalc_gold.txt"
