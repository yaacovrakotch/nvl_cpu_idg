from pymtpl.por_methods import VminTC,DDGShmooTC, PrimeHvqkTestMethod, PrimeMbistTestMethod, AuxiliaryTC, ScreenTC,PrimeVirtualFuseExportToSharedStorageTestMethod,PrimePatConfigTestMethod,PrimeSampleRateTestMethod,MbistRasterRepairTC,PrimeScanHRYSSNTestMethod,PrimeScanSPOFITestMethod, RunCallback
from pymtpl.core import Flow, Fitem, pPass, pFail, Initialize, NativeMultiTrial, AUTO, MTLdefault, InitializeNVLClass, Import, TrialParamSpec, Spec, MConfig, os

# Define DCM_MODULES based on MODULE #
MODULE = "ARR_CORE_CKX"
#VOLTAGE_DOMAIN = "CRA"
VOLTAGE_DOMAIN = "VNNAON"
product = "ARR_CORE"

product_skus = ["CK816"]
voltage_targets = {
    "DCM0": "VCCCORE0",
    "DCM1": "VCCCORE1",
    "DCM2": "VCCCORE2",
    "DCM3": "VCCCORE3"
}
########################################################################
# INITIALIZE
########################################################################
# Initialize(MODULE, "ARR_CORE_CXX", "tos4
for sku in product_skus:
    mtplname = f"{product}_{sku}"
    # Initialize the module by defining the output mtpl path and the module name
    InitializeNVLClass(
        outfile=mtplname,
        module_name=mtplname,
        binrange=[(6020, 6024), (2019, 2024)],
        basenumrange=(2291, 2300),
        defaultthermalbin=(),
        defaultresetbin=()
        #defaultthermalbin=90972200, #90HB1917/90HB1918
        #defaultresetbin=90221922 #90HB1917/90HB1918
      
    )
########################################################################
# IMPORT REQUIRED FILES
########################################################################

# Add the necessary files to import in your mtpl
Import("ARR_CORE_CKX.usrv")


###Define VMINTC in BEGCPUPKG subflow##
# Create an empty list that will contain the final list of the test
def get_test_list_ssa_core_vnnaon_pmuc_f1_c0c1_min(
    flow,
    testinput
):
    test_listt_begincpupkg = []
    ssa_core_vnnaon_pmuc_f1_c0c1_min = VminTC(
        name=f"SSA_CORE_VMIN_K_{flow}_X_CRA_MIN_LFM_VNNAON_PMUC_C0C1",
        BypassPort=testinput.get("Bypassport", -1),
        Patlist='resetplb_1xbbxxxxxx_phase2_ccf_MCtpi_CA2P_hdmt2_ippkg_hvm_list',
        LevelsTc="IPC::CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom",
        TimingsTc='ARR_CORE_CXX:cpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800',
        BaseNumbers=AUTO,
        EndVoltageLimits=Spec("ARR_CORE_Specs.CORE_HVQK_LowSearch"),
        ExecutionMode='SearchWithScoreboard',
        #FailCaptureCount=Spec("ARR_CORE_Specs.CORE_BEGIN_FailCaptureCountOverride"),
        FeatureSwitchSettings=Spec(f'ARR_CORE_Specs.FeatureSwitch'),
        ForwardingMode=Spec("ARR_CORE_Specs.CORE_Fowarding_Mode"),
        MaxRepetitionCount=1,
        PatternNameCounterIndexes=Spec("ARR_CORE_Specs.Pattern_name_map"),
        PinMap=Spec("ARR_CORE_Specs.CORE_Recovery_PinMap"),
        RecoveryMode=Spec("ARR_CORE_Specs.CORE_Recovery_Mode"),
        RecoveryTrackingIncoming=Spec("ARR_CORE_Specs.CORE_Recovery_DCM"),
        RecoveryTrackingOutgoing=Spec("ARR_CORE_Specs.CORE_Recovery_Tracker"),
        ScoreboardEdgeTicks = Spec("toInteger(0)"),
        #MaxFailsNum=Spec("toInteger(ARR_CORE_Specs.CORE_HVQK_MaxFailCapture)"),
        SetPointsPlistParamName='Patlist',
        StartVoltages=Spec("ARR_CORE_Specs.CORE_HVQK_HighSearch"),
        StartVoltagesForRetry=Spec("ARR_CORE_Specs.CORE_HVQK_LowSearch"),
        StepSize=0.02,
        TestMode='Scoreboard',
        #Voltagetarget=Spec("ARR_CORE_Specs.CORE_PMUCS_Voltage_Target"),
        SetPointsPreInstance='',
        RecoveryOptions=Spec("ARR_CORE_Specs.CORE_RecoveryOptions"),
        _fitem=Fitem(
            'SAME',
            edc=testinput.get("ISEDC"),
            r0=pFail(setbin=-60, goto="NEXT"),
            r1=pPass(goto="NEXT"),
            r2=pFail(setbin=-60, goto="NEXT"),
            r3=pPass(goto="NEXT"),
            r4=pFail(setbin=-60, goto="NEXT"),
            r5=pFail(setbin=-60, goto="NEXT")
        )
    )
    test_listt_begincpupkg.append(ssa_core_vnnaon_pmuc_f1_c0c1_min)
    return test_listt_begincpupkg

def get_test_list_ssa_core_vnnaon_pmuc_f1_c2c3_min(
    flow,
    testinput
):
    test_listt_begincpupkg = []
    ssa_core_vnnaon_pmuc_f1_c2c3_min = VminTC(
        name=f"SSA_CORE_VMIN_K_{flow}_X_CRA_MIN_LFM_VNNAON_PMUC_C2C3",
        BypassPort=testinput.get("Bypassport", -1),
        Patlist='resetplb_1xbbxxxxxx_phase2_ccf_MCtpi_CA2P_hdmt2_ippkg_hvm_list',
        LevelsTc="IPC::CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom",
        TimingsTc='ARR_CORE_CXX:cpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800',
        BaseNumbers=AUTO,
        EndVoltageLimits=Spec("ARR_CORE_Specs.CORE_HVQK_LowSearch"),
        ExecutionMode='SearchWithScoreboard',
        #FailCaptureCount=Spec("ARR_CORE_Specs.CORE_BEGIN_FailCaptureCountOverride"),
        FeatureSwitchSettings=Spec(f'ARR_CORE_Specs.FeatureSwitch'),
        ForwardingMode=Spec("ARR_CORE_Specs.CORE_Fowarding_Mode"),
        MaxRepetitionCount=1,
        PatternNameCounterIndexes=Spec("ARR_CORE_Specs.Pattern_name_map"),
        PinMap=Spec("ARR_CORE_Specs.CORE_Recovery_PinMap"),
        RecoveryMode=Spec("ARR_CORE_Specs.CORE_Recovery_Mode"),
        RecoveryTrackingIncoming=Spec("ARR_CORE_Specs.CORE_Recovery_DCM"),
        RecoveryTrackingOutgoing=Spec("ARR_CORE_Specs.CORE_Recovery_Tracker"),
        #ScoreboardEdgeTicks=Spec("toInteger(ARR_CORE_Specs.CORE_HVQK_ScoreboardEdgeTicks)"),
        #MaxFailsNum=Spec("toInteger(ARR_CORE_Specs.CORE_HVQK_MaxFailCapture)"),
        SetPointsPlistParamName='Patlist',
        StartVoltages=Spec("ARR_CORE_Specs.CORE_HVQK_HighSearch"),
        StartVoltagesForRetry=Spec("ARR_CORE_Specs.CORE_HVQK_LowSearch"),
        StepSize=0.02,
        TestMode='Scoreboard',
        #Voltagetarget=Spec("ARR_CORE_Specs.CORE_PMUCS_Voltage_Target"),
        SetPointsPreInstance='',
        RecoveryOptions=Spec("ARR_CORE_Specs.CORE_RecoveryOptions"),
        _fitem=Fitem(
            'SAME',
            edc=testinput.get("ISEDC"),
            r0=pFail(setbin=-60, goto="NEXT"),
            r1=pPass(goto="NEXT"),
            r2=pFail(setbin=-60, goto="NEXT"),
            r3=pPass(goto="NEXT"),
            r4=pFail(setbin=-60, goto="NEXT"),
            r5=pFail(setbin=-60, goto="NEXT")
        )
    )
    test_listt_begincpupkg.append(ssa_core_vnnaon_pmuc_f1_c2c3_min)
    return test_listt_begincpupkg

def get_test_list_ssa_core_vnnaon_pmuc_f1_all_min(
    flow,
    testinput
):
    test_listt_begincpupkg = []
    ssa_core_vnnaon_pmuc_f1_all_min = VminTC(
        name=f"SSA_CORE_VMIN_K_{flow}_X_CRA_MIN_LFM_VNNAON_PMUC_ALL",
        BypassPort=testinput.get("Bypassport", -1),
        Patlist='resetplb_1xbbxxxxxx_phase2_ccf_MCtpi_CA2P_hdmt2_ippkg_hvm_list',
        LevelsTc="IPC::CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom",
        TimingsTc='ARR_CORE_CXX:cpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800',
        BaseNumbers=AUTO,
        EndVoltageLimits=Spec("ARR_CORE_Specs.CORE_HVQK_LowSearch"),
        ExecutionMode='SearchWithScoreboard',
        #FailCaptureCount=Spec("ARR_CORE_Specs.CORE_BEGIN_FailCaptureCountOverride"),
        FeatureSwitchSettings=Spec(f'ARR_CORE_Specs.FeatureSwitch'),
        ForwardingMode=Spec("ARR_CORE_Specs.CORE_Fowarding_Mode"),
        MaxRepetitionCount=1,
        PatternNameCounterIndexes=Spec("ARR_CORE_Specs.Pattern_name_map"),
        PinMap=Spec("ARR_CORE_Specs.CORE_Recovery_PinMap"),
        RecoveryMode=Spec("ARR_CORE_Specs.CORE_Recovery_Mode"),
        RecoveryTrackingIncoming=Spec("ARR_CORE_Specs.CORE_Recovery_DCM"),
        RecoveryTrackingOutgoing=Spec("ARR_CORE_Specs.CORE_Recovery_Tracker"),
        #ScoreboardEdgeTicks=Spec("toInteger(ARR_CORE_Specs.CORE_HVQK_ScoreboardEdgeTicks)"),
        #MaxFailsNum=Spec("toInteger(ARR_CORE_Specs.CORE_HVQK_MaxFailCapture)"),
        SetPointsPlistParamName='Patlist',
        StartVoltages=Spec("ARR_CORE_Specs.CORE_HVQK_HighSearch"),
        StartVoltagesForRetry=Spec("ARR_CORE_Specs.CORE_HVQK_LowSearch"),
        StepSize=0.02,
        TestMode='Scoreboard',
        #Voltagetarget=Spec("ARR_CORE_Specs.CORE_PMUCS_Voltage_Target"),
        SetPointsPreInstance='',
        RecoveryOptions=Spec("ARR_CORE_Specs.CORE_RecoveryOptions"),
        _fitem=Fitem(
            'SAME',
            edc=testinput.get("ISEDC"),
            r0=pFail(setbin=-60, goto="NEXT"),
            r1=pPass(goto="NEXT"),
            r2=pFail(setbin=-60, goto="NEXT"),
            r3=pPass(goto="NEXT"),
            r4=pFail(setbin=-60, goto="NEXT"),
            r5=pFail(setbin=-60, goto="NEXT")
        )
    )
    test_listt_begincpupkg.append(ssa_core_vnnaon_pmuc_f1_all_min)
    return test_listt_begincpupkg


#################################################################################
#							BEGINCPUPKG MIN SUBFLOW
#
#################################################################################
begincpunom_flow = "BEGINCPUPKG"

# Define the BEGINCPUPKG subflow

begcpupkg_vmintc_ssa_core_pmuc_c0c1_tli = {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": True}
begcpupkg_vmintc_ssa_core_pmuc_c0c1 = get_test_list_ssa_core_vnnaon_pmuc_f1_c0c1_min(begincpunom_flow, begcpupkg_vmintc_ssa_core_pmuc_c0c1_tli)

begcpupkg_vmintc_ssa_core_pmuc_c2c3_tli = {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": True}
begcpupkg_vmintc_ssa_core_pmuc_c2c3 = get_test_list_ssa_core_vnnaon_pmuc_f1_c2c3_min(begincpunom_flow, begcpupkg_vmintc_ssa_core_pmuc_c2c3_tli)

begcpupkg_vmintc_ssa_core_pmuc_all_tli = {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": True}
begcpupkg_vmintc_ssa_core_pmuc_all = get_test_list_ssa_core_vnnaon_pmuc_f1_all_min(begincpunom_flow, begcpupkg_vmintc_ssa_core_pmuc_all_tli)

#BEGINCPUPKG SUBFLOW
#BEGINCPUPKG = Flow(
#    f'{MODULE}_BEGINCPUPKG',
#    begcpupkg_vmintc_ssa_core_pmuc_c0c1 + begcpupkg_vmintc_ssa_core_pmuc_c2c3
#    )  
#   
BEGINCPUPKG = Flow(
    f'{MODULE}_BEGINCPUPKG',
     begcpupkg_vmintc_ssa_core_pmuc_all
    )               


    