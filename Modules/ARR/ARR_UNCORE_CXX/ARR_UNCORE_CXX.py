from pymtpl.por_methods import VminTC,DDGShmooTC, PrimeHvqkTestMethod, PrimeMbistTestMethod, AuxiliaryTC, ScreenTC,PrimeVirtualFuseExportToSharedStorageTestMethod,PrimePatConfigTestMethod,PrimeSampleRateTestMethod,MbistRasterRepairTC,PrimeScanHRYSSNTestMethod,PrimeScanSPOFITestMethod, RunCallback, ApexTC
from pymtpl.core import Flow, Fitem, pPass, pFail, Initialize, NativeMultiTrial, AUTO, MTLdefault, InitializeNVLClass, Import, TrialParamSpec, Spec, MConfig, os
from pymtpl.binctr import NVLClass8dig

MODULE = "ARR_UNCORE_CXX"
VOLTAGE_DOMAIN = "VCCC"
product = "ARR_UNCORE"
MODULEPATH = 'GetEnvironmentVariable("~HDMT_TP_BASE_DIR")'

product_skus = ["CX816"]
 
for sku in product_skus:
    mtplname = f"{product}_{sku}"
    InitializeNVLClass(
        outfile=mtplname,
        module_name=mtplname,
        binrange=[(6100, 6114), (2105, 2114)],
        basenumrange=(2252, 2499),
        defaultthermalbin=90972400,  # Updated to start with 9097 as required by Mar'25 Pymtpl
        defaultresetbin=90221930,
        mttbinstrategy=NVLClass8dig
    )

Import("ARR_UNCORE_CXX.usrv")
Import("ARR_UNCORE_CXX_Timing.tcg")

#Uncore Nom
def get_test_list_uncore_vnnaon_f1_nom(
    flow,
    corner,
    testinput
):
    test_list_begincpunom = []
    uncore_vnnaon_f1_nom = VminTC(
        name=f"ALL_UNCORE_SB_K_{flow}_X_VNNAON_X_X_F1_NOM",
        BypassPort=testinput.get("Bypassport", -1),
        Patlist='resetplb_8axx080808_phase2_all_MCarr_CA2P_hdmt2_hvm_list',
        LevelsTc="CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom",
        TimingsTc='ARR_UNCORE_CXXcpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800',
        BaseNumbers = None if "SCR" in flow else AUTO,
        EndVoltageLimits=Spec(f'ARR_UNCORE_{sku}_Specs.Search_VNNAON_HighSearch'),
        ExecutionMode="SearchWithScoreboard",
        #FailCaptureCount=Spec(f'ARR_UNCORE_{sku}_Specs.Search_CaptureCount'),
        FeatureSwitchSettings=Spec(f'ARR_UNCORE_{sku}_Specs.FeatureSwitch'),
        MaxRepetitionCount=1,
        PatternNameCounterIndexes=Spec(f'ARR_UNCORE_{sku}_Specs.PatternMap'),
        #ScoreboardEdgeTicks=Spec(f'ARR_UNCORE_{sku}_Specs.Search_ScoreboardEdgeTicks'),
        #MaxFailsNum=Spec(f'ARR_UNCORE_{sku}_Specs.Search_MaxFailNum'),
        SetPointsPlistParamName='Patlist',
        StartVoltages=Spec(f'ARR_UNCORE_{sku}_Specs.Search_VNNAON_LowSearch'),
        StartVoltagesForRetry=Spec(f'ARR_UNCORE_{sku}_Specs.Search_VNNAON_LowSearch'),
        FivrCondition = Spec(f'ARR_UNCORE_{sku}_Specs.UNCORE_FivrCondition'),
        StepSize=0.02,
        TestMode='Scoreboard',
        VoltageTargets=Spec(f'ARR_UNCORE_{sku}_Specs.VNNAON_Voltagetargets'),
        SetPointsPreInstance=Spec(f'ARR_UNCORE_{sku}_Specs.Search_SetPointsPreInstance'),
        _fitem=Fitem(
            'SAME',
            edc=testinput.get("ISEDC"),
            r0=pFail(setbin=-21, goto="NEXT"),
            r1=pPass(goto="NEXT"),
            r2=pFail(setbin=-21, goto="NEXT"),
            r3=pFail(setbin=-21, goto="NEXT"),
            r4=pFail(setbin=-21, goto="NEXT"),
            r5=pFail(setbin=-21, goto="NEXT")
        )
    )
    test_list_begincpunom.append(uncore_vnnaon_f1_nom)
    return test_list_begincpunom

#DMU Retention
def get_test_list_all_uncore_vnnaon_retention(
    flow,
    corner,
    testinput
):
    test_list_endcpunom = []
    all_uncore_vnnaon_retention = VminTC(
        name=f"ALL_UNCORE_SB_K_{flow}_X_VNNAON_X_X_X_RETENTION",
        BypassPort=testinput.get("Bypassport", -1),
        Patlist='resetplb_8axx080808_phase2_all_MCarr_CA2P_hdmt2_hvm_list',
        LevelsTc="CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom",
        TimingsTc='ARR_UNCORE_CXXcpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800',
        BaseNumbers = None if "SCR" in flow else AUTO,
        EndVoltageLimits=Spec(f'ARR_UNCORE_{sku}_Specs.Search_VNNAON_HighSearch'),
        ExecutionMode="SearchWithScoreboard",
        #FailCaptureCount=Spec(f'ARR_UNCORE_{sku}_Specs.Search_CaptureCount'),
        FeatureSwitchSettings=Spec(f'ARR_UNCORE_{sku}_Specs.FeatureSwitch'),
        MaxRepetitionCount=1,
        PatternNameCounterIndexes=Spec(f'ARR_UNCORE_{sku}_Specs.PatternMap'),
        #ScoreboardEdgeTicks=Spec(f'ARR_UNCORE_{sku}_Specs.Search_ScoreboardEdgeTicks'),
        #MaxFailsNum=Spec(f'ARR_UNCORE_{sku}_Specs.Search_MaxFailNum'),
        SetPointsPlistParamName='Patlist',
        StartVoltages=Spec(f'ARR_UNCORE_{sku}_Specs.Search_VNNAON_LowSearch'),
        StartVoltagesForRetry=Spec(f'ARR_UNCORE_{sku}_Specs.Search_VNNAON_LowSearch'),
        StepSize=0.02,
        TestMode='Scoreboard',
        VoltageTargets=Spec(f'ARR_UNCORE_{sku}_Specs.VNNAON_Voltagetargets'),
        FivrCondition = Spec(f'ARR_UNCORE_{sku}_Specs.UNCORE_FivrCondition'),
        SetPointsPreInstance=Spec(f'ARR_UNCORE_{sku}_Specs.Search_SetPointsPreInstance'),
        _fitem=Fitem( 
            'SAME',
            edc=testinput.get("ISEDC"),
            r0=pFail(setbin=-21, goto="NEXT"),
            r1=pPass(goto="NEXT"),
            r2=pFail(setbin=-21, goto="NEXT"),
            r3=pFail(setbin=-21, goto="NEXT"),
            r4=pFail(setbin=-21, goto="NEXT"),
            r5=pFail(setbin=-21, goto="NEXT")
        )
    )
    test_list_endcpunom.append(all_uncore_vnnaon_retention)
    return test_list_endcpunom


#Uncore Max
def get_test_list_uncore_vnnaon_f1_max(
    flow,
    corner,
    testinput
):
    test_list_endcpumax = []
    uncore_vnnaon_f1_max = VminTC(
        name=f"ALL_UNCORE_SB_K_{flow}_X_VNNAON_X_X_F1_MAX",
        BypassPort=testinput.get("Bypassport", -1),
        Patlist='resetplb_8axx080808_phase2_all_MCarr_CA2P_hdmt2_hvm_list',
        LevelsTc="CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom",
        TimingsTc="ARR_UNCORE_CXXcpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800",
        BaseNumbers = None if "SCR" in flow else AUTO,
        EndVoltageLimits=Spec(f'ARR_UNCORE_{sku}_Specs.Search_VNNAON_HighSearch'),
        ExecutionMode="SearchWithScoreboard",
        #FailCaptureCount=Spec(f'ARR_UNCORE_{sku}_Specs.Search_CaptureCount'),
        FeatureSwitchSettings=Spec(f'ARR_UNCORE_{sku}_Specs.FeatureSwitch'),
        MaxRepetitionCount=1,
        PatternNameCounterIndexes=Spec(f'ARR_UNCORE_{sku}_Specs.PatternMap'),
        #ScoreboardEdgeTicks=Spec(f'ARR_UNCORE_{sku}_Specs.Search_ScoreboardEdgeTicks'),
        #MaxFailsNum=Spec(f'ARR_UNCORE_{sku}_Specs.Search_MaxFailNum'),
        SetPointsPlistParamName='Patlist',
        StartVoltages=Spec(f'ARR_UNCORE_{sku}_Specs.Search_VNNAON_LowSearch'),
        StartVoltagesForRetry=Spec(f'ARR_UNCORE_{sku}_Specs.Search_VNNAON_LowSearch'),
        StepSize=0.02,
        TestMode='Scoreboard',
        VoltageTargets=Spec(f'ARR_UNCORE_{sku}_Specs.VNNAON_Voltagetargets'),
        SetPointsPreInstance=Spec(f'ARR_UNCORE_{sku}_Specs.Search_SetPointsPreInstance'),
        _fitem=Fitem(
            'SAME',
            edc=testinput.get("ISEDC"),
            r0=pFail(setbin=-21, goto="NEXT"),
            r1=pPass(goto="NEXT"),
            r2=pFail(setbin=-21, goto="NEXT"),
            r3=pFail(setbin=-21, goto="NEXT"),
            r4=pFail(setbin=-21, goto="NEXT"),
            r5=pFail(setbin=-21, goto="NEXT")
        )
    )
    test_list_endcpumax.append(uncore_vnnaon_f1_max)
    return test_list_endcpumax


#################################################################################
#							BEGINCPUNOM SUBFLOW
#
#################################################################################
begincpunom_flow = "BEGINCPUNOM"
begincpunom_corner = "LFM"

begincpunom_vmintc_uncore_vnnaon_f1_nom_tli = {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": True}
begincpunom_vmintc_uncore_vnnaon_f1_nom = get_test_list_uncore_vnnaon_f1_nom(begincpunom_flow, begincpunom_corner, begincpunom_vmintc_uncore_vnnaon_f1_nom_tli)


#BEGINCPU SUBFLOW
BEGINCPUNOM = Flow(
    f'ARR_UNCORE_{sku}_BEGINCPUNOM',
    begincpunom_vmintc_uncore_vnnaon_f1_nom 
)  


#################################################################################
#							ENDCPUNOM SUBFLOW
#
#	-Need retention 
#################################################################################
endcpunom_flow = "ENDCPUNOM"
endcpunom_corner = "VNNAON"

endcpunom_vmintc_all_uncore_vnnaon_retention_tli = {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": True}
endcpunom_vmintc_all_uncore_vnnaon_retention_c0c1 = get_test_list_all_uncore_vnnaon_retention(endcpunom_flow, endcpunom_corner, endcpunom_vmintc_all_uncore_vnnaon_retention_tli)

#ENDCPUNOM SUBFLOW
ENDCPUNOM = Flow(
    f'ARR_UNCORE_{sku}_ENDCPUNOM',
    endcpunom_vmintc_all_uncore_vnnaon_retention_c0c1 
    )               


#################################################################################
#							ENDCPUMAX SUBFLOW
#
#	-Need retention 
#################################################################################
endcpumax_flow = "ENDCPUMAX"
endcpumax_corner = "VNNAON"

endcpumax_vmintc_uncore_vnnaon_f1_max_tli = {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": True}
endcpumax_vmintc_uncore_vnnaon_f1_max = get_test_list_uncore_vnnaon_f1_max(endcpumax_flow, endcpumax_corner, endcpumax_vmintc_uncore_vnnaon_f1_max_tli)

#ENDCPUMAX SUBFLOW
ENDCPUMAX = Flow(
    f'ARR_UNCORE_{sku}_ENDCPUMAX',
   endcpumax_vmintc_uncore_vnnaon_f1_max 
    )              
