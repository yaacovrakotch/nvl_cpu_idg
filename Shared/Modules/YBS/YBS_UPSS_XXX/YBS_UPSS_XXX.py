# PKG TPI Evmin Module pymtpl source code.
# Output for prime13 and TOS4.
from pymtpl.por_methods import ScreenTC, VminForwardingSaveFakeDataTC,PrimeVminForwardingExportTestMethod, AuxiliaryTC, PrimeSetDffTestMethod, ScreenTC
from pymtpl.core import Flow,  Fitem,  pPass,  pFail,  Initialize,  NativeMultiTrial,  AUTO,  MTLdefault,  InitializeNVLClass,  Import,  TrialParamSpec,  Spec,  ModuleFlow
from pymtpl.por_methods import BaseMethod, required, optional
 

class UpsEngineRunner(BaseMethod):
    def __init__(self,
                 name,
                 PACKAGE = required,              # Gets or sets the Package - usually comes from SCVars.SC_PACKAGE.
                 DEVICE = required,               # Gets or sets the Device - usually comes from SCVars.SC_DEVICE.
                 REVISION = required,             # Gets or sets the Revision - usually comes from SCVars.SC_REV.
                 STEP = required,                 # Gets or sets the Step - usually comes from SCVars.SC_STEP.
                 RECIPE_PATH = required,          # Gets or sets the PATH in which the recipe json resides.                                
                 FLEX_BOM = required,             # Gets or sets the DummyParam1 FLEX_BOM.
                 DUMMY_UNIT = required,           # Gets or sets the UPS_VERSION.               
                 PreInstance = optional,          # Run before the test
                 BypassPort = optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode = optional,  # Enable for current instance's test time and memory information
                 LogLevel = optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel = optional,                   
                 _comment=None,                 # required, do not omit
                 _fitem=None,                   # required, do not omit
                 **kwargs                       # required, do not omit
                 ):
        self._init(name, locals())
class VminCalculate(BaseMethod):
    def __init__(self,
                 name,
                 LogLevel = optional,
				 BypassPort = optional,
	             ExportKeys = required,       #"UPSVFPASSFLOW,CORNER_VMIN_SOURCE,FAST_STC_V";
				 IgnoredCornerList = optional, # "GT,GTVPG,SAAT,SAC,SACD,SAIOC,SAQ,SAME,SAN,SAPS,SAVPU";
				 InstanceMode = optional, #defalut "CalculationAndExport"
                 UploadVminDFF =  optional,       #defalut "FALSE"; 
				 UploadFLWDDFF = optional, # default "FALSE"
                 UploadSkuDFF = optional,
                 PrintToItuff = optional,     #defalut "FALSE";
				 FrequencyPrintMultiplier = required,  # 0.000000001;
				 AllowBypassCorners = required,  #"TRUE";
                 DieId = optional, #default "" 
				 PreInstance = optional,               
				 PostInstance = optional,               
                 _comment=None,                 # required, do not omit
                 _fitem=None,                   # required, do not omit
                 **kwargs                       # required, do not omit
                 ):
        self._init(name, locals())

# Initialize the module by defining the output mtpl path and the module name
InitializeNVLClass('./YBS_UPSS_XXX',  'YBS_UPSS_XXX', tosversion="tos4", binrange=[(1402, 1489), (790, 799)], 
                   defaultrm2bin = [(99140000,99141999), (99070000, 99071999)],
                   defaultrm1bin = [(98140000, 98141999), (98070000, 98071999)]
)
Import("YBS_UPSS_XXX.usrv")
subflw = "END"

#dielet_dic = {"U1PU5": ["CPU",  "UPSVFPASSFLOW_U1PU5,CORNER_VMIN_SOURCE,FAST_STC_V_U1PU5", "GT,GTVPG,SAAT,SAC,SACD,SAIOC,SAQ,SAME,SAN,SAPS,SAVPU,SADPU", "__shared__::DieIndic.if_cpu(YBS_UPSS_XXX_Rules.QA_S1_bypass(1, -1), 1)"],
#              "U1PU6": ["CPU1", "UPSVFPASSFLOW_U1PU6,CORNER_VMIN_SOURCE,FAST_STC_V_U1PU6", "GT,GTVPG,SAAT,SAC,SACD,SAIOC,SAQ,SAME,SAN,SAPS,SAVPU,SADPU", "__shared__::DieIndic.if_cpu(YBS_UPSS_XXX_Rules.QA_S1_bypass(1, -1), 1)"],
#              "U1PU4": ["GPU",  "UPSVFPASSFLOW_U1PU4,CORNER_VMIN_SOURCE,FAST_STC_V_U1PU4", "CR,AT,CCF,SAAT,SAC,SACD,SAIOC,SAQ,SAME,SAN,SAPS,SAVPU,SADPU", "__shared__::DieIndic.if_gcd(YBS_UPSS_XXX_Rules.QA_S1_bypass(1, -1), 1)"],
#              "U1PU2": ["HUB",  "UPSVFPASSFLOW_U1PU2,CORNER_VMIN_SOURCE,FAST_STC_V_U1PU2", "CR,AT,CCF,GT,GTVPG", "__shared__::DieIndic.if_hub(YBS_UPSS_XXX_Rules.QA_S1_bypass(1, -1), 1)"]             
#    }

dielet_dic = {"U1PU5": ["CPU",  "UPSVFPASSFLOW_U1PU5,CORNER_VMIN_SOURCE,FAST_STC_V_U1PU5", "CRFCT", "__shared__::DieIndic.if_cpu(YBS_UPSS_XXX_Rules.QA_S1_bypass(1, -1), 1)", "U1.U5"],
              "U1PU6": ["CPU1", "UPSVFPASSFLOW_U1PU6,CORNER_VMIN_SOURCE,FAST_STC_V_U1PU6", "CRFCT", "__shared__::DieIndic.if_cpu(YBS_UPSS_XXX_Rules.QA_S1_bypass(1, -1), 1)","U1.U6"],
              #"U1PU2": ["HUB",  "UPSVFPASSFLOW_U1PU2,CORNER_VMIN_SOURCE,FAST_STC_V_U1PU2", "", "__shared__::DieIndic.if_hub(YBS_UPSS_XXX_Rules.QA_S1_bypass(1, -1), 1)","U1.U2"]             
    }
dielet_dic_FCT = {"U1PU5": ["CPU",  "UPSVFPASSFLOW_U1PU5,CORNER_VMIN_SOURCE,FAST_STC_V_U1PU5", "", "__shared__::DieIndic.if_cpu(YBS_UPSS_XXX_Rules.QA_S1_bypass(1, -1), 1)", "U1.U5"],
                  "U1PU6": ["CPU1", "UPSVFPASSFLOW_U1PU6,CORNER_VMIN_SOURCE,FAST_STC_V_U1PU6", "", "__shared__::DieIndic.if_cpu(YBS_UPSS_XXX_Rules.QA_S1_bypass(1, -1), 1)","U1.U6"]
    }
dielet_dic_gt = {"U1PU4": ["GPU",  "UPSVFPASSFLOW_U1PU4,CORNER_VMIN_SOURCE,FAST_STC_V_U1PU4", "CR,AT,CCF,SAAT,SAC,SACD,SAIOC,SAQ,SAME,SAN,SAPS,SAVPU,SADPU", "__shared__::DieIndic.if_gcd(YBS_UPSS_XXX_Rules.QA_S1_bypass(1, -1), 1)","U1.U4"]             
    }

vmincalculate_list = []  # empty list that will contain the VminCalculate tests
vmincalculate_FCT = []
downstream_list = []
FMAX_CHECK_TEST = ScreenTC (
    name="UPSS_X_VMINFWDEXP_K_ENDPREPRL0_X_X_X_X_CORE_FMAXCHECK",
    BypassPort= -1,
    ScreenTestSet = "CHECK_FCT",
    ScreenTestsFile = './InputFiles/settingGSDS.txt',    
    _fitem=Fitem('SAME',
                 r0=pFail(setbin = 1402,ret=0),
                 r1= pPass(goto="UPSS_X_VMINFWDEXP_K_ENDPREPRL0_X_X_X_X_INTERPOST_U1PU5_FCT"),
                 r2= pPass(goto = "UPSS_X_VMINFWDEXP_K_ENDPREPRL0_X_X_X_X_INTERPOST_U1PU5"))
    )
vmincalculate_FCT.append(FMAX_CHECK_TEST)

for dielet in dielet_dic: 
	# exportkey_group = dielet_dic[dielet][1]
	ignoredcorner_list = dielet_dic[dielet][2]
	vmincalculatetc = VminCalculate(
		name=f"UPSS_X_VMINFWDEXP_K_ENDPREPRL0_X_X_X_X_INTERPOST_{dielet}",
		LogLevel = "Enabled",
		BypassPort = Spec('__shared__::TpRule.If_CLASS_NVL_S52C('+dielet_dic[dielet][3]+', 1)' if dielet == "U1PU6" else (dielet_dic[dielet][3])),
		ExportKeys = "UPSVFPASSFLOW,CORNER_VMIN_SOURCE,FAST_STC_V",
		IgnoredCornerList =  ignoredcorner_list,
        InstanceMode = Spec('YBS_UPSS_XXX_Rules.UPSS_bypass("CalculationAndExport", "ExportOnly")'),
		UploadVminDFF =  "FALSE",
        UploadFLWDDFF =  Spec('YBS_UPSS_XXX_Rules.UPSS_bypass("TRUE", "FALSE")'),
        UploadSkuDFF = "FALSE",
		PrintToItuff = "TRUE",
		FrequencyPrintMultiplier = 0.000000001,
		AllowBypassCorners = "TRUE",
        DieId = dielet_dic[dielet][4],
	    PreInstance = 'SetCurrentDieId("+__shared__::DFFVars.DIEID_' + dielet_dic[dielet][0] + '+")',
		PostInstance = "Call(LogTrackerHistory()|LogVminForwardTableToItuff())",		 
		_fitem = Fitem('SAME', r0=pFail(setbin = 1402, ret=0), r1=pPass(goto='NEXT')) 
    )
	vmincalculate_list.append(vmincalculatetc)


for dielet in dielet_dic_FCT: 
	# exportkey_group = dielet_dic[dielet][1]
	ignoredcorner_list = dielet_dic_FCT[dielet][2]
	FTC_vmincalculatetc = VminCalculate(
		name=f"UPSS_X_VMINFWDEXP_K_ENDPREPRL0_X_X_X_X_INTERPOST_{dielet}_FCT",
		LogLevel = "Enabled",
		BypassPort = Spec('__shared__::TpRule.If_CLASS_NVL_S52C('+dielet_dic_FCT[dielet][3]+', 1)' if dielet == "U1PU6" else (dielet_dic_FCT[dielet][3])),
		ExportKeys = "UPSVFPASSFLOW,CORNER_VMIN_SOURCE,FAST_STC_V",
		IgnoredCornerList =  ignoredcorner_list,
        InstanceMode = Spec('YBS_UPSS_XXX_Rules.UPSS_bypass("CalculationAndExport", "ExportOnly")'),
		UploadVminDFF =  "FALSE",
        UploadFLWDDFF =  Spec('YBS_UPSS_XXX_Rules.UPSS_bypass("TRUE", "FALSE")'),
        UploadSkuDFF = "FALSE",
		PrintToItuff = "TRUE",
		FrequencyPrintMultiplier = 0.000000001,
		AllowBypassCorners = "TRUE",
        DieId = dielet_dic_FCT[dielet][4],
	    PreInstance = 'SetCurrentDieId("+__shared__::DFFVars.DIEID_' + dielet_dic_FCT[dielet][0] + '+")',
		PostInstance = "Call(LogTrackerHistory()|LogVminForwardTableToItuff())",		 
		_fitem = Fitem('SAME', r0=pFail(setbin = 1402, ret=0), r1=pPass(goto='NEXT')) if dielet == "U1PU5" else Fitem('SAME', r0=pFail(setbin = 1402, ret=0), r1=pPass(ret =1)) 
    )
	vmincalculate_FCT.append(FTC_vmincalculatetc)

vmincalculatepkg = VminCalculate(
	name=f"UPSS_X_VMINFWDEXP_K_ENDPREPRL0_X_X_X_X_INTERPOST_PKG",
	LogLevel = "Enabled",
	BypassPort = Spec('YBS_UPSS_XXX_Rules.QA_S1_bypass(1, -1)'),
	ExportKeys = "UPSVFPASSFLOW,CORNER_VMIN_SOURCE,FAST_STC_V",
	IgnoredCornerList =  "CRFCT,CR,AT,CCF,GT,GTVPG,SAAT,SAC,SACD,SAIOC,SAQ,SAME,SAN,SAPS,SAVPU,SADPU",
	InstanceMode = "CalculationOnly",
    UploadVminDFF =  "FALSE",
	UploadFLWDDFF = "FALSE",
    UploadSkuDFF = "TRUE",
    PrintToItuff = "FALSE",
	FrequencyPrintMultiplier = 0.000000001,
	AllowBypassCorners = "TRUE",
	PreInstance = 'SetCurrentDieId(PKG)',
    PostInstance = "Call(PrintToItuff(--body_type strgval --body_data T.IPH::HUB_TRIALS::FlowDomain.HUB_TOP --tname_suf _HUB_FLOW)|PrintToItuff(--body_type strgval --body_data T.IPG::GCD_TRIALS::FlowDomain.GT_TOP --tname_suf _GT_FLOW)|PrintToItuff(--body_type strgval --body_data T.IPC::CPU_TRIALS::FlowDomain.CORE_TOP --tname_suf _CORE_FLOW)|PrintToItuff(--body_type strgval --body_data T.IPC::CPU_TRIALS::FlowDomain.RING_TOP --tname_suf _RING_FLOW)|PrintToItuff(--body_type strgval --body_data T.IPC::CPU_TRIALS::FlowDomain.ATOM_TOP --tname_suf _ATOM_FLOW))",
	_fitem = Fitem('SAME', r0=pFail(setbin = 1402, ret=0), r1=pPass(goto='NEXT')) 
)
vmincalculate_U1PU2 = VminCalculate(
		name=f"UPSS_X_VMINFWDEXP_K_ENDPREPRL0_X_X_X_X_INTERPOST_U1PU2",
		LogLevel = "Enabled",
		BypassPort = Spec('__shared__::DieIndic.if_hub(YBS_UPSS_XXX_Rules.QA_S1_bypass(1, -1), 1)'),
		ExportKeys = "UPSVFPASSFLOW,CORNER_VMIN_SOURCE,FAST_STC_V",
		IgnoredCornerList =  "",
        InstanceMode = Spec('YBS_UPSS_XXX_Rules.UPSS_bypass("CalculationAndExport", "ExportOnly")'),
		UploadVminDFF =  "FALSE",
        UploadFLWDDFF =  Spec('YBS_UPSS_XXX_Rules.UPSS_bypass("TRUE", "FALSE")'),
        UploadSkuDFF = "FALSE",
		PrintToItuff = "TRUE",
		FrequencyPrintMultiplier = 0.000000001,
		AllowBypassCorners = "TRUE",
        DieId = "U1.U2",
	    PreInstance = 'SetCurrentDieId("+__shared__::DFFVars.DIEID_HUB+")',
		PostInstance = "Call(LogTrackerHistory()|LogVminForwardTableToItuff())",		 
		_fitem = Fitem('SAME', r0=pFail(setbin = 1402, ret=0), r1=pPass(goto='NEXT')) 
    )
PrintT = ScreenTC (    
    name = "UPSS_X_PRINTTRIALVAR_K_ENDPREPRL0_X_X_X_X",
    BypassPort = Spec('YBS_UPSS_XXX_Rules.UPSS_bypass(-1, 1)'),
    ScreenTestSet = "PrintTrialVar",
    ScreenTestsFile = './InputFiles/settingGSDS.txt',
    _fitem = Fitem('SAME', r0=pFail(setbin = 1402, ret=0), r1=pPass(goto='NEXT'))
)


port_list = list(range(1405,1490))+list(range(790,800))
d_items = {f'r{x}': pFail(setbin=int(f'{str(x).zfill(4)}'), ret=0) for x in port_list}

upsrunner  =  UpsEngineRunner( 
    name = "UPSS_X_UPSENGINERUNNER_K_LTTCPOST_X_X_X_X_UPSS",
    PACKAGE = Spec('__shared__::SCVars.SC_PACKAGE'),
    DEVICE = Spec('__shared__::SCVars.SC_DEVICE'),
    REVISION = Spec('__shared__::SCVars.SC_REV'),
    STEP = Spec('__shared__::SCVars.SC_STEP'),
    RECIPE_PATH = Spec('__shared__::TpRule.If_CLASS_NVL_S28C("./Shared/Modules/YBS/YBS_UPSS_XXX/InputFiles_JF/model_recipe_NVL_S28C.json", __shared__::TpRule.If_CLASS_NVL_S52C("./Shared/Modules/YBS/YBS_UPSS_XXX/InputFiles_JF/model_recipe_NVL_S52C.json", __shared__::TpRule.If_CLASS_NVL_HX28C("./Shared/Modules/YBS/YBS_UPSS_XXX/InputFiles_PG/MB/model_recipe_HX.json", __shared__::TpRule.If_CLASS_NVL_P16C("./Shared/Modules/YBS/YBS_UPSS_XXX/InputFiles_BA/model_recipe_P16C.json", __shared__::TpRule.If_CLASS_NVL_S16C("./Shared/Modules/YBS/YBS_UPSS_XXX/InputFiles_PG/DT/model_recipe_S16C.json", __shared__::TpRule.If_CLASS_DNL_S28C("./Shared/Modules/YBS/YBS_UPSS_XXX/InputFiles_PG/DT/model_recipe_DS28C.json", __shared__::TpRule.If_CLASS_NVL_H16C("./Shared/Modules/YBS/YBS_UPSS_XXX/InputFiles_IDC/NVL_H16C/model_recipe_H.json", "unknown")))))))'),
    FLEX_BOM = Spec('__shared__::SCVars.SC_FLEXBOMRECIPE'),
    DUMMY_UNIT = "",
    BypassPort = Spec('YBS_UPSS_XXX_Rules.IfPackage(YBS_UPSS_XXX_Rules.UPSS_bypass(-1, 1), 1)'),
    PreInstance = 'SetCurrentDieId(PKG)',
    _fitem = Fitem('SAME', r1=pPass(goto='NEXT'), **d_items)
)
for dielet in dielet_dic_gt: 
	exportkey_group = dielet_dic_gt[dielet][1]
	ignoredcorner_list = dielet_dic_gt[dielet][2]
	vmincalculatetc_gt = VminCalculate(
		name=f"UPSS_X_VMINFWDEXP_K_END_X_X_X_X_INTERPOST_{dielet}",
		LogLevel = "Enabled",
		BypassPort = Spec('__shared__::TpRule.If_CLASS_NVL_S52C('+dielet_dic_gt[dielet][3]+', 1)' if dielet == "U1PU6" else (dielet_dic_gt[dielet][3])),
		ExportKeys = "UPSVFPASSFLOW,CORNER_VMIN_SOURCE,FAST_STC_V",
		# IgnoredCornerList =  ignoredcorner_list,
        InstanceMode = Spec('YBS_UPSS_XXX_Rules.UPSS_bypass("CalculationAndExport", "ExportOnly")'),
		UploadVminDFF =  "FALSE",
        UploadFLWDDFF =  Spec('YBS_UPSS_XXX_Rules.UPSS_bypass("TRUE", "FALSE")'),
        UploadSkuDFF = "FALSE",
		PrintToItuff = "TRUE",
		FrequencyPrintMultiplier = 0.000000001,
		AllowBypassCorners = "TRUE",
        DieId = dielet_dic_gt[dielet][4],
	    PreInstance = 'SetCurrentDieId("+__shared__::DFFVars.DIEID_' + dielet_dic_gt[dielet][0] + '+")',
		PostInstance = "Call(LogTrackerHistory()|LogVminForwardTableToItuff())",		 
		_fitem = Fitem('SAME', r0=pFail(setbin = 1402, ret=0), r1=pPass(goto='NEXT')) 
    )
downstreamdffs  =  UpsEngineRunner(
      name = "UPSS_X_UPSDOWNSTREAMDFF_K_END_X_X_X_X_UPSS",
      PACKAGE = "",
      DEVICE = "",
      REVISION = "AUTO",
      STEP = "",
	  RECIPE_PATH = './Shared/Modules/YBS/YBS_UPSS_XXX/InputFiles/model_recipe_DFFs.json',
      FLEX_BOM = "000000000000",
	  DUMMY_UNIT = "",
	  BypassPort = Spec('YBS_UPSS_XXX_Rules.UPSS_bypass(-1, 1)'),
      _fitem = Fitem('SAME', edc = True, r1405=pFail(setbin = None,  goto='NEXT'), r1=pPass(goto='NEXT'), r2 = pPass(ret="1"))
)
downstreamdffsAfter  =  UpsEngineRunner(
      name = "UPSS_X_UPSDOWNSTREAMDFF_K_LTTCHUBPKG_X_X_X_X_UPSS",
      PACKAGE = "",
      DEVICE = "",
      REVISION = "AUTO",
      STEP = "",
	  RECIPE_PATH = './Shared/Modules/YBS/YBS_UPSS_XXX/InputFiles/model_recipe_DFFs.json',
      FLEX_BOM = "000000000000",
	  DUMMY_UNIT = "",
	  BypassPort = Spec('__shared__::TpRule.If_S_PKGs(1, 1)'),
      _fitem = Fitem('SAME', edc = True, r1405=pFail(setbin = None,  goto='NEXT'), r1=pPass(goto='NEXT'), r2 = pPass(ret="1"))
)
AHMT_FORK = AuxiliaryTC(
    name = "AFORK_X_SCREEN_K_END_X_X_X_X_X",
    BypassPort = Spec('__shared__::FlwSkpCollect.if_ahmt(2, __shared__::TpRule.If_QRE(2, YBS_UPSS_XXX_Rules.Bypass6233(2, __shared__::TpRule.If_REBI(2, 1))))'),
    DataType = "Integer",
    Expression = "1",
	ResultPort = "1",
    _fitem = Fitem(r0=pFail(setbin= 1404, ret=0), r2=pPass(ret = 1))
)
AHMT_FORK_ENDPRE = AuxiliaryTC(
    name = "AFORK_X_SCREEN_K_ENDPREPRL0_X_X_X_X_X",
    BypassPort = Spec('__shared__::FlwSkpCollect.if_ahmt(2, __shared__::TpRule.If_QRE(2, YBS_UPSS_XXX_Rules.Bypass6233(2, __shared__::TpRule.If_REBI(2, 1))))'),
    DataType = "Integer",
    Expression = "1",
	ResultPort = "1",
    _fitem = Fitem(r0=pFail(setbin= 1404, ret=0), r2=pPass(ret = 1))
)
SetGSDSInit = ScreenTC (    
    name = "UPSS_X_SETAGGITDGSDS_K_END_X_X_X_X_UPSS",
    BypassPort = Spec('YBS_UPSS_XXX_Rules.UPSS_bypass(1, 1)'),
    ScreenTestSet = "INITGSDS",
    ScreenTestsFile =  './InputFiles/settingGSDS.txt',
     _fitem = Fitem('SAME', r0=pFail(setbin = 1402, ret=0), r1=pPass(goto='NEXT'))
)

SetGSDSAfter = ScreenTC (
    name = "UPSS_X_SETAGGITDGSDS_K_LTTCHUBPKG_X_X_X_X_UPSS",
	BypassPort = Spec('__shared__::TpRule.If_S_PKGs(1, 1)'),
    ScreenTestSet = "AFTERGSDS",
    ScreenTestsFile =  './InputFiles/settingGSDS.txt',
    _fitem = Fitem('SAME', r0=pFail(setbin = 1402, ret=0), r1=pPass(goto='NEXT')) 
)

SetDffInit = PrimeSetDffTestMethod (
    name = "UPSS_X_SETAGGITDDFF_K_END_X_X_X_X_UPSS",
	BypassPort = Spec('YBS_UPSS_XXX_Rules.UPSS_bypass(1, 1)'),
    DieId = Spec('__shared__::DFFVars.DIEID_HUB'),
    TokenValue = "0",
    TokenName = "SAAGGITD",
    _fitem = Fitem('SAME', r0=pFail(setbin = 1402, ret=0), r1=pPass(goto='NEXT')) 
)

SetDffAfter = PrimeSetDffTestMethod (
    name = "UPSS_X_SETAGGITDDFF_K_LTTCHUBPKG_X_X_X_X_UPSS",
	BypassPort = Spec('__shared__::TpRule.If_S_PKGs(1, 1)'),
    DieId = Spec('__shared__::DFFVars.DIEID_HUB'),
    TokenValue = "1",
    TokenName = "SAAGGITD",
    _fitem = Fitem('SAME', r0=pFail(setbin = 1402, ret=0), r1=pPass(goto='NEXT')) 
)

SetMBLDTGSDS = ScreenTC (    
    name = "UPSS_X_SETPKGGSDS_K_ENDPREPRL0_X_X_X_X",
    BypassPort = Spec('YBS_UPSS_XXX_Rules.UPSS_bypass(-1, 1)'),
    ScreenTestSet = Spec('__shared__::TpRule.If_M_PKGs("SETMOBILEGSDS", __shared__::TpRule.If_S_PKGs("SETDESKTOPGSDS", ""))'),
    ScreenTestsFile = './InputFiles/settingGSDS.txt',
    _fitem = Fitem('SAME', r0=pFail(setbin = 1402, ret=0), r1=pPass(goto='NEXT'))
)

SetITDMODELGSDS = ScreenTC (    
    name = "UPSS_X_SETITDMODELGSDS_K_ENDPREPRL0_X_X_X_X",
    BypassPort = Spec('YBS_UPSS_XXX_Rules.UPSS_bypass(-1, 1)'),
    ScreenTestSet = "SETUPITDMODEL",
    ScreenTestsFile = Spec('__shared__::TpRule.If_CLASS_NVL_S28C("./InputFiles_JF/setITDGSDS_NVL_S28C.txt", __shared__::TpRule.If_CLASS_NVL_S52C("./InputFiles_JF/setITDGSDS_NVL_S52C.txt", __shared__::TpRule.If_CLASS_NVL_HX28C("./InputFiles_PG/MB/setITDGSDS_HX.txt", __shared__::TpRule.If_CLASS_NVL_P16C("./InputFiles_BA/setITDGSDS_P16C.txt", __shared__::TpRule.If_CLASS_NVL_S16C("./InputFiles_PG/DT/setITDGSDS_S16C.txt", __shared__::TpRule.If_CLASS_DNL_S28C("./InputFiles_PG/DT/setITDGSDS_DS28C.txt", __shared__::TpRule.If_CLASS_NVL_H16C("./InputFiles_IDC/setITDGSDS_H16C.txt", "./InputFiles/DummyInputFile.txt")))))))'),
    _fitem = Fitem('SAME', r0=pFail(setbin = 1402, ret=0), r1=pPass(goto='NEXT'))
)


ENDPREPRL0_Subflow = Flow('YBS_UPSS_XXX_ENDPREPRL0', AHMT_FORK_ENDPRE, SetITDMODELGSDS, SetMBLDTGSDS,vmincalculatepkg,vmincalculate_U1PU2, vmincalculate_FCT,vmincalculate_list)
END_Subflow = Flow('YBS_UPSS_XXX_END',AHMT_FORK, vmincalculatetc_gt,SetGSDSInit, downstreamdffs)
LTTCPOST_Subflow = Flow('YBS_UPSS_XXX_LTTCPOST', upsrunner)
LTTCHUBPKG_SubFlow = Flow('YBS_UPSS_XXX_LTTCHUBPKG',SetGSDSAfter, downstreamdffsAfter)