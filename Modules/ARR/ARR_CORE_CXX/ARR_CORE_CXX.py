from pymtpl.por_methods import VminTC,DDGShmooTC, PrimeHvqkTestMethod, MbistVminTC, PrimeMbistTestMethod, AuxiliaryTC, ScreenTC,PrimeVirtualFuseExportToSharedStorageTestMethod,PrimePatConfigTestMethod,PrimeSampleRateTestMethod,MbistRasterRepairTC,PrimeScanHRYSSNTestMethod,PrimeScanSPOFITestMethod, RunCallback, ApexTC
from pymtpl.core import Flow, Fitem, pPass, pFail, Initialize, NativeMultiTrial, AUTO, MTLdefault, InitializeNVLClass, Import, TrialParamSpec, Spec, MConfig
from pymtpl.binctr import NVLClass8dig # type: ignore
#from pymtpl.por_methods import PrimeVminTC, PrimeVminTCWithRecovery, PrimeVminTCWithRecoveryAndScoreboard, PrimeVminTCWithRecoveryAndScoreboardAndRetry, PrimeVminTCWithRecoveryAndScoreboardAndRetryAndFeatureSwitch, PrimeVminTCWithRecoveryAndScoreboardAndRetryAndFeatureSwitchAndSetPointsPreInstance

# Define DCM_MODULES based on MODULE #
#MODULE = "ARR_CORE"
VOLTAGE_DOMAIN = "CRA"
#VOLTAGE_DOMAIN = "VCCC"
product = "ARR_CORE"
MODULEPATH = 'GetEnvironmentVariable("~HDMT_TP_BASE_DIR")'

product_skus = ["_CX816"]
voltage_targets = {
    "DCM0": "CORE0",
    "DCM1": "CORE1",
    "DCM2": "CORE2",
    "DCM3": "CORE3"
}
################# START MTPL FLOW DEFINITON #####################
  
product_skus = ["CX816"]

FlowMatrixRule = {
    "CR_FMIN_MHz"   : "0400",
    "CR_F1_FREQ_MHz": "1200",
    "CR_F2_FREQ_MHz": "1500",
    "CR_F3_FREQ_MHz": "2400",
    "CR_F4_FREQ_MHz": "3500",
    "CR_F5_FREQ_MHz": "3600"

    }

# FlowMatrix Definition
flow_matrix_definitions = {
    "F1": "CR_F1_FREQ",
    "F2": "CR_F2_FREQ",
    "F3": "CR_F3_FREQ",
    "F4": "CR_F4_FREQ",
    "F5": "CR_F5_FREQ"
}
 
for sku in product_skus:
    mtplname = f"{product}_{sku}"
    # Initialize the module by defining the output mtpl path and the module name
    InitializeNVLClass(
        outfile=mtplname,
        module_name=mtplname,
        binrange=[(6000, 6018), (2000, 2018)],
        basenumrange=(2252, 2499),
        defaultthermalbin=(90976018), #90HB1917/90HB1918
        defaultresetbin=(90611920), #90HB1917/90HB1918
        mttbinstrategy=NVLClass8dig

    )

########################################################################
# IMPORT REQUIRED FILES
########################################################################

# Add the necessary files to import in your mtpl
Import("ARR_CORE_CXX.usrv")
Import("ARR_CORE_CXX_Timing.tcg")

###Define VMINTC in BEGCPUNOM subflow##
#PMUCS C0C1 F2 KS Nom
def get_test_list_ssa_core_vnnaon_pmuc_f2_c0c1(
    flow,
    corner,
    testinput
):
    test_listt_begincpunom = []

    frequency_value = FlowMatrixRule["CR_F2_FREQ_MHz"]

    ssa_core_vnnaon_pmucs_c0c1_nom = VminTC(
        name=f"SSA_CORE_SB_K_{flow}_X_{VOLTAGE_DOMAIN.upper()}_NOM_{frequency_value}_PMUCS_C0C1",
        BypassPort=testinput.get("Bypassport", -1),
        Patlist='resetplb_8axx080808_phase2_all_MCarr_CA2P_hdmt2_hvm_list',
        LevelsTc="CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom",
        TimingsTc="ARR_CORE_CXX:cpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800",
        BaseNumbers = None if "SCR" in flow else AUTO,
        EndVoltageLimits=Spec(f'ARR_CORE_{sku}_Specs.Search_VCCC_HighSearch'),
        ExecutionMode="SearchWithScoreboard",
        FailCaptureCount = Spec("toInteger(1)"),
        FeatureSwitchSettings=Spec(f'ARR_CORE_{sku}_Specs.FeatureSwitch'),
        ForwardingMode='Input',
        MaxRepetitionCount=1,
        PatternNameCounterIndexes=Spec(f'ARR_CORE_{sku}_Specs.PatternMap'),
        PinMap=Spec(f'ARR_CORE_{sku}_Specs.Pattern_name_map'),
        RecoveryMode=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery'),
        RecoveryTrackingIncoming=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_DCM'),
        RecoveryTrackingOutgoing=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_Tracker'),
        ScoreboardEdgeTicks = Spec("toInteger(0)"),
        MaxFailsNum = Spec("toInteger(20)"),
        SetPointsPlistParamName='Patlist',
        StartVoltages=Spec(f'ARR_CORE_{sku}_Specs.CORE_HVQK_HighSearch'),
        #StartVoltagesForRetry=Spec(f'ARR_CORE_{sku}_Specs.CORE_HVQK_LowSearch'),
        StepSize=Spec("toDouble(0.01)"),
        TestMode='Scoreboard',
        VoltageTargets = Spec(f'ARR_CORE_{sku}_Specs.voltage_target'),
        SetPointsPreInstance = '',
        RecoveryOptions=Spec(f'ARR_CORE_{sku}_Specs.CORE_RecoveryOptions'),
        _fitem=Fitem(
            'SAME',
            edc=testinput.get("ISEDC"),
            r0=pFail(setbin=-20, ),
            r1=pPass(goto="NEXT"),
            r2=pFail(setbin=-20, goto="NEXT"),
            r3=pPass(goto="NEXT"),
            r4=pFail(setbin=-20, goto="NEXT"),
            r5=pFail(setbin=-20, goto="NEXT")
        )
    )
    test_listt_begincpunom.append(ssa_core_vnnaon_pmucs_c0c1_nom)
    return test_listt_begincpunom

def get_test_list_ssa_core_vnnaon_pmuc_f2_all(
    flow,
    corner,
    testinput
):
    test_listt_begincpunom = []

    frequency_value = FlowMatrixRule["CR_F2_FREQ_MHz"]

    ssa_core_vnnaon_pmucs_all_nom = VminTC(
        name=f"SSA_CORE_SB_K_{flow}_X_{VOLTAGE_DOMAIN.upper()}_NOM_{frequency_value}_PMUCS_ALL",
        BypassPort=testinput.get("Bypassport", -1),
        Patlist='resetplb_8axx080808_phase2_all_MCarr_CA2P_hdmt2_hvm_list',
        LevelsTc="CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom",
        TimingsTc="ARR_CORE_CXX:cpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800",
        BaseNumbers = None if "SCR" in flow else AUTO,
        EndVoltageLimits=Spec(f'ARR_CORE_{sku}_Specs.Search_VCCC_HighSearch'),
        ExecutionMode="SearchWithScoreboard",
        FailCaptureCount = Spec("toInteger(1)"),
        FeatureSwitchSettings=Spec(f'ARR_CORE_{sku}_Specs.FeatureSwitch'),
        ForwardingMode='Input',
        MaxRepetitionCount=1,
        PatternNameCounterIndexes=Spec(f'ARR_CORE_{sku}_Specs.PatternMap'),
        PinMap=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_PinMap'),
        RecoveryMode=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery'),
        RecoveryTrackingIncoming=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_DCM'),
        RecoveryTrackingOutgoing=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_Tracker'),
        ScoreboardEdgeTicks = Spec("toInteger(0)"),
        MaxFailsNum = Spec("toInteger(20)"),
        SetPointsPlistParamName='Patlist',
        StartVoltages=Spec(f'ARR_CORE_{sku}_Specs.CORE_HVQK_HighSearch'),
        #StartVoltagesForRetry=Spec(f'ARR_CORE_{sku}_Specs.CORE_HVQK_LowSearch'),
        StepSize=Spec("toDouble(0.01)"),
        TestMode='Scoreboard',
        VoltageTargets = Spec(f'ARR_CORE_{sku}_Specs.voltage_target'),
        SetPointsPreInstance = '',
        RecoveryOptions=Spec(f'ARR_CORE_{sku}_Specs.CORE_RecoveryOptions'),
        _fitem=Fitem(
            'SAME',
            edc=testinput.get("ISEDC"),
            r0=pFail(setbin=-20, ),
            r1=pPass(goto="NEXT"),
            r2=pFail(setbin=-20, goto="NEXT"),
            r3=pPass(goto="NEXT"),
            r4=pFail(setbin=-20, goto="NEXT"),
            r5=pFail(setbin=-20, goto="NEXT")
        )
    )
    test_listt_begincpunom.append(ssa_core_vnnaon_pmucs_all_nom)
    return test_listt_begincpunom

def get_test_list_xsa_core_vccc_c0c1_nom(
    flow,
    corner,
    testinput
):
    test_listt_begincpunom = []

    frequency_value = FlowMatrixRule["CR_F2_FREQ_MHz"]
    xsa_core_vccc_c0c1_nom = VminTC(
        name=f"XSA_CORE_SB_K_{flow}_X_{VOLTAGE_DOMAIN.upper()}_NOM_{frequency_value}_PMUCS_C0C1",
        BypassPort=testinput.get("Bypassport", -1),
        Patlist='resetplb_8axx080808_phase2_all_MCarr_CA2P_hdmt2_hvm_list',
        LevelsTc="CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom",
        TimingsTc="ARR_CORE_CXX:cpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800",
        BaseNumbers = None if "SCR" in flow else AUTO,
        EndVoltageLimits=Spec(f'ARR_CORE_{sku}_Specs.Search_VCCC_HighSearch'),
        ExecutionMode='Search',
        FailCaptureCount = Spec("toInteger(1)"),
        FeatureSwitchSettings=Spec(f'ARR_CORE_{sku}_Specs.FeatureSwitch'),
        ForwardingMode='Input',
        MaxRepetitionCount=1,
        PatternNameCounterIndexes=Spec(f'ARR_CORE_{sku}_Specs.PatternMap'),
        PinMap=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_PinMap'),
        RecoveryMode=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery'),
        RecoveryTrackingIncoming = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_DCM'),
        RecoveryTrackingOutgoing=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_Tracker'),
        RecoveryOptions='S816_6C_8A',
        ScoreboardEdgeTicks = Spec("toInteger(0)"),
        MaxFailsNum = Spec("toInteger(20)"),
        SetPointsPlistParamName='Patlist',
        StartVoltages=Spec(f'ARR_CORE_{sku}_Specs.CORE_BEGIN_LowSearch'),
        StepSize=Spec("toDouble(0.01)"),
        TestMode='Scoreboard',
        VoltageTargets = Spec(f'ARR_CORE_{sku}_Specs.voltage_target'),
        SetPointsPreInstance = '',
         _fitem=Fitem(
            'SAME',
            edc=testinput.get("ISEDC"),
            r0=pFail(setbin=-20, goto="NEXT"),
            r1=pPass(goto="NEXT"),
            r2=pFail(setbin=-20, goto="NEXT"),
            r3=pPass(goto="NEXT"),#example port if want to set EDC
            r4=pFail(setbin=-20, goto="NEXT"),
            r5=pFail(setbin=-20, goto="NEXT")
        )
    )
    test_listt_begincpunom.append(xsa_core_vccc_c0c1_nom)
    return test_listt_begincpunom 

def get_test_list_xsa_core_vccc_all_nom(
    flow,
    corner,
    testinput
):
    test_listt_begincpunom = []

    frequency_value = FlowMatrixRule["CR_F2_FREQ_MHz"]
    xsa_core_vccc_all_nom = VminTC(
        name=f"XSA_CORE_SB_K_{flow}_X_{VOLTAGE_DOMAIN.upper()}_NOM_{frequency_value}_PMUCS_ALL",
        BypassPort=testinput.get("Bypassport", -1),
        Patlist='resetplb_8axx080808_phase2_all_MCarr_CA2P_hdmt2_hvm_list',
        LevelsTc="CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom",
        TimingsTc="ARR_CORE_CXX:cpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800",
        BaseNumbers = None if "SCR" in flow else AUTO,
        EndVoltageLimits=Spec(f'ARR_CORE_{sku}_Specs.Search_VCCC_HighSearch'),
        ExecutionMode='Search',
        #FailCaptureCount = Spec("toInteger(1)"),
        FailCaptureCount = Spec("toInteger(1)"),
        FeatureSwitchSettings=Spec(f'ARR_CORE_{sku}_Specs.FeatureSwitch'),
        ForwardingMode='Input',
        MaxRepetitionCount=1,
        PatternNameCounterIndexes=Spec(f'ARR_CORE_{sku}_Specs.PatternMap'),
        PinMap=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_PinMap'),
        RecoveryMode=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery'),
        RecoveryTrackingIncoming = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_DCM'),
        RecoveryTrackingOutgoing=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_Tracker'),
        RecoveryOptions='S816_6C_8A',
        ScoreboardEdgeTicks = Spec("toInteger(0)"),
        MaxFailsNum = Spec("toInteger(20)"),
        SetPointsPlistParamName='Patlist',
        StartVoltages=Spec(f'ARR_CORE_{sku}_Specs.CORE_BEGIN_LowSearch'),
        StepSize=Spec("toDouble(0.01)"),
        TestMode='Scoreboard',
        VoltageTargets = Spec(f'ARR_CORE_{sku}_Specs.voltage_target'),
        SetPointsPreInstance = '',
         _fitem=Fitem(
            'SAME',
            edc=testinput.get("ISEDC"),
            r0=pFail(setbin=-20, goto="NEXT"),
            r1=pPass(goto="NEXT"),
            r2=pFail(setbin=-20, goto="NEXT"),
            r3=pPass(goto="NEXT"),#example port if want to set EDC
            r4=pFail(setbin=-20, goto="NEXT"),
            r5=pFail(setbin=-20, goto="NEXT")
        )
    )
    test_listt_begincpunom.append(xsa_core_vccc_all_nom)
    return test_listt_begincpunom 

def get_test_list_ssa_core_vnnaon_pmuc_f2_c2c3(
    flow,
    corner,
    testinput
):
    test_listt_begincpunom = []

    frequency_value = FlowMatrixRule["CR_F2_FREQ_MHz"]

    ssa_core_vnnaon_pmucs_c2c3_nom = VminTC(
        name=f"SSA_CORE_SB_K_{flow}_X_{VOLTAGE_DOMAIN.upper()}_NOM_{frequency_value}_PMUCS_C2C3",
        BypassPort=testinput.get("Bypassport", -1),
        Patlist='resetplb_8axx080808_phase2_all_MCarr_CA2P_hdmt2_hvm_list',
        LevelsTc="CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom",
        TimingsTc="ARR_CORE_CXX:cpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800",
        BaseNumbers = None if "SCR" in flow else AUTO,
        EndVoltageLimits=Spec(f'ARR_CORE_{sku}_Specs.Search_VCCC_HighSearch'),
        ExecutionMode="SearchWithScoreboard",
        #FailCaptureCount = Spec("toInteger(1)"),
        FailCaptureCount = Spec("toInteger(1)"),
        FeatureSwitchSettings=Spec(f'ARR_CORE_{sku}_Specs.FeatureSwitch'),
        ForwardingMode='Input',
        MaxRepetitionCount=1,
        PatternNameCounterIndexes=Spec(f'ARR_CORE_{sku}_Specs.PatternMap'),
        PinMap=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_PinMap'),
        RecoveryMode=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery'),
        RecoveryTrackingIncoming=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_DCM'),
        RecoveryTrackingOutgoing=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_Tracker'),
        ScoreboardEdgeTicks = Spec("toInteger(0)"),
        MaxFailsNum = Spec("toInteger(20)"),
        SetPointsPlistParamName='Patlist',
        StartVoltages=Spec(f'ARR_CORE_{sku}_Specs.CORE_HVQK_HighSearch'),
        #StartVoltagesForRetry=Spec(f'ARR_CORE_{sku}_Specs.CORE_HVQK_LowSearch'),
        StepSize=Spec("toDouble(0.01)"),
        TestMode='Scoreboard',
        VoltageTargets = Spec(f'ARR_CORE_{sku}_Specs.voltage_target'),
        SetPointsPreInstance = '',
        RecoveryOptions=Spec(f'ARR_CORE_{sku}_Specs.CORE_RecoveryOptions'),
        _fitem=Fitem(
            'SAME',
            edc=testinput.get("ISEDC"),
            r0=pFail(setbin=-20, goto="NEXT"),
            r1=pPass(goto="NEXT"),
            r2=pFail(setbin=-20, goto="NEXT"),
            r3=pPass(goto="NEXT"),#example port if want to set EDC
            r4=pFail(setbin=-20, goto="NEXT"),
            r5=pFail(setbin=-20, goto="NEXT")
        )
    )
    test_listt_begincpunom.append(ssa_core_vnnaon_pmucs_c2c3_nom)
    return test_listt_begincpunom


def get_test_list_xsa_core_vccc_c2c3_nom(
    flow,
    corner,
    testinput
):
    test_listt_begincpunom = []

    frequency_value = FlowMatrixRule["CR_F2_FREQ_MHz"]


    xsa_core_vccc_c2c3_nom = VminTC(
        name=f"XSA_CORE_SB_K_{flow}_X_{VOLTAGE_DOMAIN.upper()}_NOM_{frequency_value}_PMUCS_C2C3",
        BypassPort=testinput.get("Bypassport", -1),
        Patlist='resetplb_8axx080808_phase2_all_MCarr_CA2P_hdmt2_hvm_list',
        LevelsTc="CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom",
        TimingsTc="ARR_CORE_CXX:cpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800",
        BaseNumbers = None if "SCR" in flow else AUTO,
        EndVoltageLimits=Spec(f'ARR_CORE_{sku}_Specs.Search_VCCC_HighSearch'),
        ExecutionMode='Search',
        #FailCaptureCount = Spec("toInteger(1)"),
        FailCaptureCount = Spec("toInteger(1)"),
        FeatureSwitchSettings=Spec(f'ARR_CORE_{sku}_Specs.FeatureSwitch'),
        ForwardingMode=Spec(f'ARR_CORE_{sku}_Specs.Recovery_ForwardingMode'),
        MaxRepetitionCount=1,
        PatternNameCounterIndexes=Spec(f'ARR_CORE_{sku}_Specs.PatternMap'),
        PinMap=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_PinMap'),
        RecoveryMode=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery'),
        RecoveryTrackingIncoming=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_DCM'),
        RecoveryTrackingOutgoing=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_Tracker'),
        RecoveryOptions='S816_6C_8A',
        ScoreboardEdgeTicks = Spec("toInteger(0)"),
        MaxFailsNum = Spec("toInteger(20)"),
        SetPointsPlistParamName='Patlist',
        StartVoltages=Spec(f'ARR_CORE_{sku}_Specs.CORE_BEGIN_LowSearch'),
        StepSize=Spec("toDouble(0.01)"),
        TestMode='Scoreboard',
        VoltageTargets = Spec(f'ARR_CORE_{sku}_Specs.voltage_target'),
        SetPointsPreInstance = '',
        _fitem=Fitem(
            'SAME',
            edc=testinput.get("ISEDC"),
            r0=pFail(setbin=-20, goto="NEXT"),
            r1=pPass(goto="NEXT"),
            r2=pFail(setbin=-20, goto="NEXT"),
            r3=pPass(goto="NEXT"),#example port if want to set EDC
            r4=pFail(setbin=-20, goto="NEXT"),
            r5=pFail(setbin=-20, goto="NEXT")
        )
    )
    test_listt_begincpunom.append(xsa_core_vccc_c2c3_nom)
    return test_listt_begincpunom 

def get_test_list_ssa_core_vccc_c6s_retention_c0c1(
    flow,
    corner,
    testinput
):
    test_listt_endcpunom = []
    ssa_core_vccc_c6s_retention_c0c1 = VminTC(
        name=f"SSA_CORE_SB_K_{flow}_X_{VOLTAGE_DOMAIN.upper()}_X_X_C6S_RETENTION_C0C1",
        BypassPort = testinput.get("Bypassport", -1),
        Patlist = 'resetplb_8axx080808_phase2_all_MCarr_CA2P_hdmt2_hvm_list',
        LevelsTc="CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom",
        TimingsTc="ARR_CORE_CXX:cpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800",
        BaseNumbers = None if "SCR" in flow else AUTO,
        EndVoltageLimits = Spec(f'ARR_CORE_{sku}_Specs.Search_VCCC_HighSearch'),
        ExecutionMode = 'SearchWithScoreboard',
        #FailCaptureCount = Spec("toInteger(1)"),
        FailCaptureCount = Spec("toInteger(1)"),
        FeatureSwitchSettings=Spec(f'ARR_CORE_{sku}_Specs.FeatureSwitch'),
        ForwardingMode = Spec(f'ARR_CORE_{sku}_Specs.CORE_Fowarding_Mode'),
        MaxRepetitionCount = 1,
        PatternNameCounterIndexes=Spec(f'ARR_CORE_{sku}_Specs.PatternMap'),
        PinMap = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_PinMap'),
        RecoveryMode=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery'),
        RecoveryTrackingIncoming = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_DCM'),
        RecoveryTrackingOutgoing = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_Tracker'),
        #ScoreboardPerPatternFails = Spec("toInteger(ARR_CORE_Specs.ScoreBoardPerPatFailure)"),
        ScoreboardEdgeTicks = Spec("toInteger(0)"),
        MaxFailsNum = Spec("toInteger(20)"),
        SetPointsPlistParamName = 'Patlist',
        StartVoltages = Spec(f'ARR_CORE_{sku}_Specs.CORE_HVQK_NomSearch'),
        StepSize=Spec("toDouble(0.01)"),
        TestMode = 'Scoreboard',
        VoltageTargets = Spec(f'ARR_CORE_{sku}_Specs.voltage_target'),
        SetPointsPreInstance = '',
        RecoveryOptions = Spec(f'ARR_CORE_{sku}_Specs.CORE_RecoveryOptions'),
        _fitem=Fitem( 
            'SAME',
            edc=testinput.get("ISEDC"),
            r0=pFail(setbin=-20, goto="NEXT"),
            r1=pPass(goto="NEXT"),
            r2=pFail(setbin=-20, goto="NEXT"),
            r3=pPass(goto="NEXT"),
            r4=pFail(setbin=-20, goto="NEXT"),
            r5=pFail(setbin=-20, goto="NEXT")
        )
    )
    test_listt_endcpunom.append(ssa_core_vccc_c6s_retention_c0c1)
    return test_listt_endcpunom

def get_test_list_ssa_core_vccc_c6s_retention_c2c3(
    flow,
    corner,
    testinput
):
    test_listt_endcpunom = []
    ssa_core_vccc_c6s_retention_c2c3 = VminTC(
        name=f"SSA_CORE_SB_K_{flow}_X_{VOLTAGE_DOMAIN.upper()}_X_X_C6S_RETENTION_C2C3",
        BypassPort = testinput.get("Bypassport", -1),
        Patlist = 'resetplb_8axx080808_phase2_all_MCarr_CA2P_hdmt2_hvm_list',
        LevelsTc="CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom",
        TimingsTc="ARR_CORE_CXX:cpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800",
        BaseNumbers = None if "SCR" in flow else AUTO,
        EndVoltageLimits = Spec(f'ARR_CORE_{sku}_Specs.Search_VCCC_HighSearch'),
        ExecutionMode = 'SearchWithScoreboard',
        FailCaptureCount = Spec("toInteger(1)"),
        ##FailCaptureCount = Spec("toInteger(ARR_CORE_Specs.CORE_BEGIN_FailCaptureCountOverride)"),
        FeatureSwitchSettings=Spec(f'ARR_CORE_{sku}_Specs.FeatureSwitch'),
        ForwardingMode = Spec(f'ARR_CORE_{sku}_Specs.CORE_Fowarding_Mode'),
        MaxRepetitionCount = 1,
        PatternNameCounterIndexes=Spec(f'ARR_CORE_{sku}_Specs.PatternMap'),
        PinMap = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_PinMap'),
        RecoveryMode=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery'),
        RecoveryTrackingIncoming = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_DCM'),
        RecoveryTrackingOutgoing = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_Tracker'),
        #ScoreboardPerPatternFails = Spec("toInteger(ARR_CORE_Specs.ScoreBoardPerPatFailure)"),
        ScoreboardEdgeTicks = Spec("toInteger(0)"),
        MaxFailsNum = Spec("toInteger(20)"),
        SetPointsPlistParamName = 'Patlist',
        StartVoltages = Spec(f'ARR_CORE_{sku}_Specs.CORE_HVQK_NomSearch'),
        StepSize=Spec("toDouble(0.01)"),
        TestMode = 'Scoreboard',
        VoltageTargets = Spec(f'ARR_CORE_{sku}_Specs.voltage_target'),
        SetPointsPreInstance = '',
        RecoveryOptions = Spec(f'ARR_CORE_{sku}_Specs.CORE_RecoveryOptions'),
        _fitem=Fitem( 
            'SAME',
            edc=testinput.get("ISEDC"),
            r0=pFail(setbin=-20, goto="NEXT"),
            r1=pPass(goto="NEXT"),
            r2=pFail(setbin=-20, goto="NEXT"),
            r3=pPass(goto="NEXT"),
            r4=pFail(setbin=-20, goto="NEXT"),
            r5=pFail(setbin=-20, goto="NEXT")
        )
    )
    test_listt_endcpunom.append(ssa_core_vccc_c6s_retention_c2c3)
    return test_listt_endcpunom

def get_test_list_ssa_core_vccc_c6s_retention_all(
    flow,
    corner,
    testinput
):
    test_listt_endcpunom = []
    ssa_core_vccc_c6s_retention_all = VminTC(
        name=f"SSA_CORE_SB_K_{flow}_X_{VOLTAGE_DOMAIN.upper()}_X_X_C6S_RETENTION_ALL",
        BypassPort = testinput.get("Bypassport", -1),
        Patlist = 'resetplb_8axx080808_phase2_all_MCarr_CA2P_hdmt2_hvm_list',
        LevelsTc="CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom",
        TimingsTc="ARR_CORE_CXX:cpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800",
        BaseNumbers = None if "SCR" in flow else AUTO,
        EndVoltageLimits = Spec(f'ARR_CORE_{sku}_Specs.Search_VCCC_HighSearch'),
        ExecutionMode = 'SearchWithScoreboard',
        FailCaptureCount = Spec("toInteger(1)"),
        ##FailCaptureCount = Spec("toInteger(ARR_CORE_Specs.CORE_BEGIN_FailCaptureCountOverride)"),
        FeatureSwitchSettings=Spec(f'ARR_CORE_{sku}_Specs.FeatureSwitch'),
        ForwardingMode = Spec(f'ARR_CORE_{sku}_Specs.CORE_Fowarding_Mode'),
        MaxRepetitionCount = 1,
        PatternNameCounterIndexes=Spec(f'ARR_CORE_{sku}_Specs.PatternMap'),
        PinMap = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_PinMap'),
        RecoveryMode=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery'),
        RecoveryTrackingIncoming = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_DCM'),
        RecoveryTrackingOutgoing = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_Tracker'),
        #ScoreboardPerPatternFails = Spec("toInteger(ARR_CORE_Specs.ScoreBoardPerPatFailure)"),
        ScoreboardEdgeTicks = Spec("toInteger(0)"),
        MaxFailsNum = Spec("toInteger(20)"),
        SetPointsPlistParamName = 'Patlist',
        StartVoltages = Spec(f'ARR_CORE_{sku}_Specs.CORE_HVQK_NomSearch'),
        StepSize=Spec("toDouble(0.01)"),
        TestMode = 'Scoreboard',
        VoltageTargets = Spec(f'ARR_CORE_{sku}_Specs.voltage_target'),
        SetPointsPreInstance = '',
        RecoveryOptions = Spec(f'ARR_CORE_{sku}_Specs.CORE_RecoveryOptions'),
        _fitem=Fitem( 
            'SAME',
            edc=testinput.get("ISEDC"),
            r0=pFail(setbin=-20, goto="NEXT"),
            r1=pPass(goto="NEXT"),
            r2=pFail(setbin=-20, goto="NEXT"),
            r3=pPass(goto="NEXT"),
            r4=pFail(setbin=-20, goto="NEXT"),
            r5=pFail(setbin=-20, goto="NEXT")
        )
    )
    test_listt_endcpunom.append(ssa_core_vccc_c6s_retention_all)
    return test_listt_endcpunom

def get_test_list_ssa_core_vnnaon_pmuc_f1_c0c1_max(
    flow,
    corner,
    testinput
):
    test_listt_endcpumax = []

    frequency_value = FlowMatrixRule["CR_F1_FREQ_MHz"]
    ssa_core_vnnaon_pmuc_f1_c0c1_max = VminTC(
        name=f"SSA_CORE_SB_K_{flow}_X_{VOLTAGE_DOMAIN.upper()}_MAX_{frequency_value}_PMUCS_C0C1",
        BypassPort = testinput.get("Bypassport", -1),
        Patlist = 'resetplb_8axx080808_phase2_all_MCarr_CA2P_hdmt2_hvm_list',
        LevelsTc="CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom",
        TimingsTc="ARR_CORE_CXX:cpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800",
        BaseNumbers = None if "SCR" in flow else AUTO,
        EndVoltageLimits = Spec(f'ARR_CORE_{sku}_Specs.Search_VCCC_HighSearch'),
        ExecutionMode = 'SearchWithScoreboard',
        FailCaptureCount = Spec("toInteger(1)"),
        ##FailCaptureCount = Spec("toInteger(ARR_CORE_Specs.CORE_BEGIN_FailCaptureCountOverride)"),
        FeatureSwitchSettings=Spec(f'ARR_CORE_{sku}_Specs.FeatureSwitch'),
        ForwardingMode = Spec(f'ARR_CORE_{sku}_Specs.CORE_Fowarding_Mode'),
        MaxRepetitionCount = 1,
        PatternNameCounterIndexes=Spec(f'ARR_CORE_{sku}_Specs.PatternMap'),
        PinMap = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_PinMap'),
        RecoveryMode=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery'),
        RecoveryTrackingIncoming = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_DCM'),
        RecoveryTrackingOutgoing = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_Tracker'),
        #ScoreboardPerPatternFails = Spec("toInteger(ARR_CORE_Specs.ScoreBoardPerPatFailure)"),
        ScoreboardEdgeTicks = Spec("toInteger(0)"),
        MaxFailsNum = Spec("toInteger(20)"),
        SetPointsPlistParamName = 'Patlist',
        StartVoltages = Spec(f'ARR_CORE_{sku}_Specs.CORE_HVQK_NomSearch'),
        StepSize=Spec("toDouble(0.01)"),
        TestMode = 'Scoreboard',
        VoltageTargets = Spec(f'ARR_CORE_{sku}_Specs.voltage_target'),
        SetPointsPreInstance = '',
        RecoveryOptions = Spec(f'ARR_CORE_{sku}_Specs.CORE_RecoveryOptions'),
        _fitem=Fitem( 
            'SAME',
            edc=testinput.get("ISEDC"),
            r0=pFail(setbin=-20, goto="NEXT"),
            r1=pPass(goto="NEXT"),
            r2=pFail(setbin=-20, goto="NEXT"),
            r3=pPass(goto="NEXT"),
            r4=pFail(setbin=-20, goto="NEXT"),
            r5=pFail(setbin=-20, goto="NEXT")
        )
    )
    test_listt_endcpumax.append(ssa_core_vnnaon_pmuc_f1_c0c1_max)
    return test_listt_endcpumax


def get_test_list_ssa_core_vnnaon_pmuc_f1_c2c3_max(
    flow,
    corner,
    testinput
):
    test_listt_endcpumax = []

    frequency_value = FlowMatrixRule["CR_F1_FREQ_MHz"]

    ssa_core_vnnaon_pmuc_f1_c2c3_max = VminTC(
        name=f"SSA_CORE_SB_K_{flow}_X_{VOLTAGE_DOMAIN.upper()}_MAX_{frequency_value}_PMUCS_C2C3",
        BypassPort = testinput.get("Bypassport", -1),
        Patlist = 'resetplb_8axx080808_phase2_all_MCarr_CA2P_hdmt2_hvm_list',
        LevelsTc="CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom",
        TimingsTc="ARR_CORE_CXX:cpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800",
        BaseNumbers = None if "SCR" in flow else AUTO,
        EndVoltageLimits = Spec(f'ARR_CORE_{sku}_Specs.Search_VCCC_HighSearch'),
        ExecutionMode = 'SearchWithScoreboard',
        FailCaptureCount = Spec("toInteger(1)"),
        ##FailCaptureCount = Spec("toInteger(ARR_CORE_Specs.CORE_BEGIN_#FailCaptureCountOverride)"),
        FeatureSwitchSettings=Spec(f'ARR_CORE_{sku}_Specs.FeatureSwitch'),
        ForwardingMode = Spec(f'ARR_CORE_{sku}_Specs.CORE_Fowarding_Mode'),
        MaxRepetitionCount = 1,
        PatternNameCounterIndexes=Spec(f'ARR_CORE_{sku}_Specs.PatternMap'),
        PinMap = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_PinMap'),
        RecoveryMode=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery'),
        RecoveryTrackingIncoming = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_DCM'),
        RecoveryTrackingOutgoing = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_Tracker'),
        #ScoreboardPerPatternFails = Spec("toInteger(ARR_CORE_Specs.ScoreBoardPerPatFailure)"),
        ScoreboardEdgeTicks = Spec("toInteger(0)"),
        MaxFailsNum = Spec("toInteger(20)"),
        SetPointsPlistParamName = 'Patlist',
        StartVoltages = Spec(f'ARR_CORE_{sku}_Specs.CORE_HVQK_NomSearch'),
        StepSize=Spec("toDouble(0.01)"),
        TestMode = 'Scoreboard',
        VoltageTargets = Spec(f'ARR_CORE_{sku}_Specs.voltage_target'),
        SetPointsPreInstance = '',
        RecoveryOptions = Spec(f'ARR_CORE_{sku}_Specs.CORE_RecoveryOptions'),
        _fitem=Fitem( 
            'SAME',
            edc=testinput.get("ISEDC"),
            r0=pFail(setbin=-20, goto="NEXT"),
            r1=pPass(goto="NEXT"),
            r2=pFail(setbin=-20, goto="NEXT"),
            r3=pPass(goto="NEXT"),
            r4=pFail(setbin=-20, goto="NEXT"),
            r5=pFail(setbin=-20, goto="NEXT")
        )  
    )
    test_listt_endcpumax.append(ssa_core_vnnaon_pmuc_f1_c2c3_max)

    return test_listt_endcpumax

def get_test_list_ssa_core_vnnaon_pmuc_f1_all_max(
    flow,
    corner,
    testinput
):
    test_listt_endcpumax = []

    frequency_value = FlowMatrixRule["CR_F1_FREQ_MHz"]

    ssa_core_vnnaon_pmuc_f1_all_max = VminTC(
        name=f"SSA_CORE_SB_K_{flow}_X_{VOLTAGE_DOMAIN.upper()}_MAX_{frequency_value}_PMUCS_ALL",
        BypassPort = testinput.get("Bypassport", -1),
        Patlist = 'resetplb_8axx080808_phase2_all_MCarr_CA2P_hdmt2_hvm_list',
        LevelsTc="CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom",
        TimingsTc="ARR_CORE_CXX:cpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800",
        BaseNumbers = None if "SCR" in flow else AUTO,
        EndVoltageLimits = Spec(f'ARR_CORE_{sku}_Specs.Search_VCCC_HighSearch'),
        ExecutionMode = 'SearchWithScoreboard',
        FailCaptureCount = Spec("toInteger(1)"),
        ##FailCaptureCount = Spec("toInteger(ARR_CORE_Specs.CORE_BEGIN_#FailCaptureCountOverride)"),
        FeatureSwitchSettings=Spec(f'ARR_CORE_{sku}_Specs.FeatureSwitch'),
        ForwardingMode = Spec(f'ARR_CORE_{sku}_Specs.CORE_Fowarding_Mode'),
        MaxRepetitionCount = 1,
        PatternNameCounterIndexes=Spec(f'ARR_CORE_{sku}_Specs.PatternMap'),
        PinMap = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_PinMap'),
        RecoveryMode=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery'),
        RecoveryTrackingIncoming = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_DCM'),
        RecoveryTrackingOutgoing = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_Tracker'),
        #ScoreboardPerPatternFails = Spec("toInteger(ARR_CORE_Specs.ScoreBoardPerPatFailure)"),
        ScoreboardEdgeTicks = Spec("toInteger(0)"),
        MaxFailsNum = Spec("toInteger(20)"),
        SetPointsPlistParamName = 'Patlist',
        StartVoltages = Spec(f'ARR_CORE_{sku}_Specs.CORE_HVQK_NomSearch'),
        StepSize=Spec("toDouble(0.01)"),
        TestMode = 'Scoreboard',
        VoltageTargets = Spec(f'ARR_CORE_{sku}_Specs.voltage_target'),
        SetPointsPreInstance = '',
        RecoveryOptions = Spec(f'ARR_CORE_{sku}_Specs.CORE_RecoveryOptions'),
        _fitem=Fitem( 
            'SAME',
            edc=testinput.get("ISEDC"),
            r0=pFail(setbin=-20, goto="NEXT"),
            r1=pPass(goto="NEXT"),
            r2=pFail(setbin=-20, goto="NEXT"),
            r3=pPass(goto="NEXT"),
            r4=pFail(setbin=-20, goto="NEXT"),
            r5=pFail(setbin=-20, goto="NEXT")
        )  
    )
    test_listt_endcpumax.append(ssa_core_vnnaon_pmuc_f1_all_max)

    return test_listt_endcpumax
 ########################################################################################################################
 #F1F4 VCC DEFINITION
 ########################################################################################################################
# For this example we will be focusing on generating mutiple speed flow tests. We will be using the below MTT Test Template to generate our output.
def get_test_list_f1_f4(flow, corner, FlowMatrix, subflow, content_list):
    test_list_arrflow = []  # Define an empty list. This will be used to append all the Fitems in the flow
    frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]
    # Loop through the content_list to create multiple tests based on the provided parameters
    for test_type, test_parms in content_list.items():
        test_list_arrflow.append(NativeMultiTrial(
            name=f"XSA_CORE_SB_K_{subflow}_X_{VOLTAGE_DOMAIN.upper()}_{corner}_{frequency_value}_{test_type}",
            exitaction="Continue",
            trialvar="CPU_TRIALS::FlowDomain.CORE",
            _comment='Sample VminTC test with MTT',
            template=VminTC(
                name=f'"XSA_CORE_SB_K_{subflow}_X_VCC_{corner}_" + ' + Spec(f"__shared__::CustomFlowMatrixSpecs.{FlowMatrix}_MHz") + f' + "_{test_type}"',
                TimingsTc="ARR_CORE_CXX:cpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800",
                LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
                BaseNumbers=None if "SCR" in flow else AUTO,
                PinMap = test_parms.get("PinMap", Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_PinMap')),
                PatternNameCounterIndexes = Spec(f'ARR_CORE_{sku}_Specs.PatternMap'),
                EndVoltageLimits=Spec(f'__shared__::FlowMatrixSingular.CR_HIGH_SEARCH_VALUE'),
                ExecutionMode="Search" if "XCR" in flow else "SearchWithScoreboard",
                TestMode="MultiVmin",
                ForwardingMode = "Input" if test_parms["IS_EDC"] else "InputOutput",
                FeatureSwitchSettings = 'recovery_update_always,disable_masked_targets,print_per_target_increments,print_scoreboard_counters,fivr_mode_on',
                FailCaptureCount = Spec("toInteger(1)"),
                #DtsConfiguration = Spec(f'ARR_CORE_{sku}_Specs.dtsconfig'),
                FivrConditionPlistParamName = "Patlist",
                MaxFailsNum=Spec("toInteger(20)"),
                StartVoltages=Spec(f'__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE'),
                StartVoltagesForRetry=Spec('__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
                StartVoltagesOffset=Spec('__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
                StepSize=Spec(f'toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)'),
                LimitGuardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
                RecoveryMode="NoRecovery",
                RecoveryOptions = "CLASS_NVL_S28C_8A",
                RecoveryTrackingIncoming = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_DCM'),
                RecoveryTrackingOutgoing = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_Tracker'),
                SetPointsPlistParamName = "Patlist",
                VoltageTargets = Spec(f'ARR_CORE_{sku}_Specs.voltage_target'),
                FivrCondition = "NOM_CCF_CORE",
                BypassPort=test_parms.get("Bypass", -1),
                VoltageConverter=test_parms.get("VoltageConverter", Spec(f'"--dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_{corner}')),
                FlowIndex=TrialParamSpec(f"__shared__::FlowMatrixSingular.FlowIndex"),
                SetPointsPreInstance=Spec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:"+'+Spec(f'ARR_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'ARR_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{corner}_FREQ")+f'+"GHz"'),
                SetPointsPostInstance=Spec(f'PSPOST.CR_{corner}'),
            ),  # Close the braces for the MTT Template
            r0=pFail(setbin=-60, ret=0, trialaction=Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
            r1=pPass(ret=1, trialaction="Exit"),
            r2=pFail(setbin=-60, ret=0, trialaction="Exit"),
            r3=pPass(ret=1, trialaction="Exit"),
            r4=pFail(setbin=-60, ret=0, trialaction="Exit"),
            r5=pFail(setbin=-60, ret=0, trialaction="Exit"),
            _fitem=Fitem(
                'SAME',
                edc=test_parms["IS_EDC"],
                r0=pFail(setbin=-60, goto="NEXT"),
                r1=pPass(goto="NEXT"),
                r2=pFail(setbin=-60, goto="NEXT"),
                r3=pPass(goto="NEXT"),
                r4=pFail(setbin=-60, goto="NEXT"),
                r5=pFail(setbin=-60, goto="NEXT")
            )
        ))
    return test_list_arrflow
 ########################################################################################################################
 #APEX_COMP VCC DEFINITION
 ########################################################################################################################
def get_test_apextc(flow, corner, FlowMatrix, subflow, content_list):
    """
    Generate a list of NativeMultiTrial APEXTC tests for the given flow, corner, FlowMatrix, subflow, and content_list.
    """
    test_list_apextcflow = []

    frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]
    # Loop through the content_list to create multiple tests based on the provided parameters
    for test_type, test_parms in content_list.items():
        test_list_apextcflow.append(
            NativeMultiTrial(
                name=f"XSA_CORE_SB_K_{subflow}_X_{VOLTAGE_DOMAIN.upper()}_{corner}_{frequency_value}_{test_type}_APEX_MTT",
                exitaction="Restore", #Restore is EDC test
                trialvar="CPU_TRIALS::FlowDomain.CORE",
                _comment='SpeedFlow F5XCR APEXTC test with MTT',
                template=ApexTC(
                    name=f'"XSA_CORE_SB_K_{subflow}_X_VCCC_{corner}_" + ' +
                         Spec(f"ARR_CORE_{sku}::ARR_CORE_{sku}_Specs.Apex_Multipass") +
                         f' + "_{test_type}_APEX_MTT"',
                    InitialMaskBits=TrialParamSpec(f'ARR_CORE_{sku}_Specs.Apex_Multipass'),
                    #DtsConfiguration = Spec(f'ARR_CORE_{sku}_Specs.dtsconfig'),
                    BypassPort=test_parms["Bypass"],
                    Targets="CORE3,CORE2,CORE1,CORE0",
                    StepSize = Spec("toInteger(1)"),
                    ForwardingMode="Input",
                    PinMap=test_parms.get("PinMap", Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_PinMap')),
                    SetPointsPreInstance = Spec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:"+'+Spec(f'ARR_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'ARR_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{corner}_FREQ")+f'+"GHz"'),
                    SetPointsPostInstance = Spec(f'PSPOST.CR_{corner}'),
                    LevelsTc="CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom",
                    TimingsTc="ARR_CORE_CXX:cpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800",
                    Patlist='resetplb_8axx080808_phase2_all_MCarr_CA2P_hdmt2_hvm_list',
                    PatternNameCounterIndexes=Spec(f'ARR_CORE_{sku}_Specs.PatternMap'),
                    RecoveryOptions=Spec(f'ARR_CORE_{sku}_Specs.CORE_RecoveryOptions'),
                    RecoveryTracking="CR",
                    End=Spec(f'__shared__::FlowMatrixSingular.APEX_CORE_MIN'),
                    Start=Spec(f'__shared__::FlowMatrixSingular.APEX_CORE_MAX'),
                    FivrCondition = "NOM_CCF_CORE",
                    FivrConditionPlistParamName="Patlist",
                    VoltageConverter = '--overrides CORE3:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE2:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE1:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+",CORE0:"+' +Spec(f"__shared__::FlowMatrixSingular.CR_VMAX_VALUE")+ f'+" --dlvrpins VCCIA',
                    ExportTokens="FXCRC3,FXCRC2,FXCRC1,FXCRC0",
                ),
            r0=pFail(setbin=-60, ret= 0, trialaction=Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
            r1=pPass(ret = 1, trialaction = "Next"),
            r2=pFail(setbin=-60, ret= 0, trialaction="Exit"),
            r3=pPass(ret = 1, trialaction = "Next"),
            r4=pFail(setbin=-60, ret= 0, trialaction="Exit"),
            r5=pFail(setbin=-60, ret= 0, trialaction="Exit"),
            _fitem=Fitem(
                'SAME',
                edc=test_parms["IS_EDC"],
                r0=pFail(setbin=-60, goto="NEXT"),
                r1=pPass(goto= "NEXT"),
                r2=pFail(setbin=-60, goto="NEXT"),
                r3=pPass(goto= "NEXT"),
                r4=pFail(setbin=-60, goto="NEXT"),
                r5=pFail(setbin=-60, goto="NEXT")
            )
        ))
    return test_list_apextcflow

########################################################################################################################
  #FMIN DEFINITION
########################################################################################################################
def get_test_list_fmin(flow, testinput, corner, FlowMatrix, subflow, content_list):

    test_list_fminflow = []  # Define an empty list. This will be used to append all the Fitems in the flow

    frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]
    # Loop through the content_list to create multiple tests based on the provided parameters
    for test_type, test_parms in content_list.items():
        test_list_fminflow.append(
            VminTC(
                name=f"XSA_CORE_SB_K_{subflow}_X_{VOLTAGE_DOMAIN.upper()}_{corner}_{frequency_value}_{test_type}",
                    BypassPort = testinput.get("Bypassport", 1),
                    ExecutionMode="Search" if "SCR" in flow else "SearchWithScoreboard",
                    TestMode="SingleVmin",
                    ForwardingMode="Input" if test_parms["IS_EDC"] else "InputOutput",
                    FeatureSwitchSettings=Spec(f'ARR_CORE_{sku}_Specs.FeatureSwitch'),
                    LevelsTc="CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
                    TimingsTc="ARR_CORE_CXX:cpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800",
                    Patlist = 'resetplb_8axx080808_phase2_all_MCarr_CA2P_hdmt2_hvm_list',
                    BaseNumbers=None if "SCR" in flow else AUTO,
                    CornerIdentifiers = f"CR3@F1,CR2@F1,CR1@F1,CR0@F1",
                    EndVoltageLimits = Spec(f'__shared__::FlowMatrixSingular.CR_HIGH_SEARCH_VALUE'),
                    StartVoltages = Spec(f'__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE'),
                    StartVoltagesForRetry = Spec('__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
                    StartVoltagesOffset = Spec('__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
                    StepSize=Spec("toDouble(0.01)"),
                    LimitGuardband=Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
                    PinMap=test_parms.get("PinMap", Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_PinMap')),
                    PatternNameCounterIndexes=Spec(f'ARR_CORE_{sku}_Specs.PatternMap'),
                    RecoveryMode=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery'),
                    RecoveryOptions=Spec(f'ARR_CORE_{sku}_Specs.CORE_RecoveryOptions'),
                    RecoveryTrackingIncoming = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_DCM'),
                    RecoveryTrackingOutgoing=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_Tracker'),
                    SetPointsPlistParamName="Patlist",
                    VoltageTargets = Spec(f'ARR_CORE_{sku}_Specs.voltage_target'),
                    FivrCondition = "NOM_CCF_CORE",
                    FailCaptureCount = Spec("toInteger(1)"),
                    FivrConditionPlistParamName="Patlist",
                    #DtsConfiguration = Spec(f'ARR_CORE_{sku}_Specs.dtsconfig'),
                    VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_{corner}'),
                    #FlowIndex = TrialParamSpec(f"__shared__::FlowMatrixSingular.FlowIndex"),
                    SetPointsPreInstance = Spec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:"+'+Spec(f'ARR_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{FlowMatrix}+")+'"GHz,MCdrv:"+'+Spec(f'ARR_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_{corner}")+f'+"GHz"'),
                    SetPointsPostInstance = Spec(f'PSPOST.CR_{corner}'),
                
                    _fitem=Fitem(
                    'SAME',
                    edc=test_parms["IS_EDC"],
                    r0=pFail(setbin=-60, goto="NEXT"),
                    r1=pPass(goto="NEXT"),
                    r2=pFail(setbin=-60, goto="NEXT"),
                    r3=pPass(goto="NEXT"),
                    r4=pFail(setbin=-60, goto="NEXT"),
                    r5=pFail(setbin=-60, goto="NEXT")
                )
            )
        )

    return test_list_fminflow

########################################################################################################################
  #F5XCR DEFINITION
########################################################################################################################

def get_test_list(flow, corner, FlowMatrix, corner_id, subflow, content_list):
    test_list = []  # Define an empty list. This will be used to append all the Fitems in the flow

    frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]

    for test_type, test_parms in content_list.items():
        test_list.append(
            NativeMultiTrial(
                name=f"XSA_CORE_SB_K_{subflow}_X_{VOLTAGE_DOMAIN.upper()}_{corner}_{frequency_value}_{test_type}",
                exitaction="Continue",
                trialvar="CPU_TRIALS::FlowDomain.CORE",
                _comment='SpeedFlow F5XCR MTT Test',
                template=VminTC(
                    name=f'"SBFT_CORE_VMIN_K_{subflow}_X_CRA_" + ' + Spec(f"__shared__::Corners.CR_{corner_id}") + f' + "_X_{test_type}"',
                    BypassPort=test_parms["Bypass"],
                    CornerIdentifiers = TrialParamSpec(Spec(f"__shared__::CornerIdentifiers.CR_{corner_id}")),
                    ExecutionMode="Search" if "SCR" in flow else "SearchWithScoreboard",
                    TestMode="MultiVmin",
                    ForwardingMode="Input" if test_parms["IS_EDC"] else "InputOutput",
                    FeatureSwitchSettings=Spec(f'ARR_CORE_{sku}_Specs.FeatureSwitch'),
                    LevelsTc="CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min",
                    TimingsTc="ARR_CORE_CXX:cpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800",
                    EndVoltageLimits = Spec(f'__shared__::FlowMatrixSingular.CR_HIGH_SEARCH_VALUE'),
                    Patlist = 'resetplb_8axx080808_phase2_all_MCarr_CA2P_hdmt2_hvm_list',
                    BaseNumbers=None if "SCR" in flow else AUTO,
                    StartVoltages=Spec(f"__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE"),
                    StartVoltagesForRetry = Spec('__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
                    StartVoltagesOffset = Spec('__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
                    StepSize=Spec(f'toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION)'),
                    LimitGuardband=Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
                    PinMap=test_parms.get("PinMap", Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_PinMap')),
                    PatternNameCounterIndexes=Spec(f'ARR_CORE_{sku}_Specs.PatternMap'),
                    RecoveryMode=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery'),
                    RecoveryOptions=Spec(f'ARR_CORE_{sku}_Specs.CORE_RecoveryOptions'),
                    RecoveryTrackingIncoming = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_DCM'),
                    RecoveryTrackingOutgoing=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_Tracker'),
                    SetPointsPlistParamName="Patlist",
                    FivrCondition = "NOM_CCF_CORE",
                    FailCaptureCount = Spec("toInteger(1)"),
                    FivrConditionPlistParamName="Patlist",
                    #DtsConfiguration = Spec(f'ARR_CORE_{sku}_Specs.dtsconfig'),
                    VoltageConverter = test_parms.get("VoltageConverter", Spec(f'"--dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_{corner}')),
                    FlowIndex = TrialParamSpec(f"__shared__::FlowMatrixSingular.FlowIndex"), 
                    SetPointsPreInstance = TrialParamSpec(f'PSPRE.CR_{corner}+' f'","+' f'"MCdrv:"+'+Spec(f'ARR_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FreqValues.CR_{corner_id}+")+'"GHz,MCdrv:"+'+Spec(f'ARR_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FreqValues.CCF_{corner_id}")+f'+"GHz"'),
                    SetPointsPostInstance = Spec(f'PSPOST.CR_{corner}'),
                ),
                r0=pFail(setbin=-60, ret= 0, trialaction=Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r1=pPass(ret = 1, trialaction = "NEXT"),
                r2=pFail(setbin=-60, ret= 0, trialaction="Exit"),
                r3=pFail(setbin=-60, ret= 0, trialaction="Exit"),
                r4=pFail(setbin=-60, ret= 0, trialaction="Exit"),
                r5=pFail(setbin=-60, ret= 0, trialaction="Exit"),
                _fitem=Fitem(
                    'SAME',
                    edc=test_parms["IS_EDC"],
                    r0=pFail(setbin=-60, goto="NEXT"),
                    r1=pPass(goto= "NEXT"),
                    r2=pFail(setbin=-60, goto="NEXT"),
                    r3=pPass(goto= "NEXT"),
                    r4=pFail(setbin=-60, goto="NEXT"),
                    r5=pFail(setbin=-60, goto="NEXT")
                )
            )
        )

    return test_list

#################################################################################
#VMAX DEFINITION
#################################################################################

def get_test_vmax(flow, corner, FlowMatrix, subflow, content_list):
     
   test_list_vmaxflow = [] # Define an empty list. This will be used to append all the Fitems in the flow
  
   for test_type, test_parms in content_list.items():
      test_list_vmaxflow.append(VminTC(name=f'XSA_CORE_SB_K_{subflow}_X_{VOLTAGE_DOMAIN.upper()}_{corner}_X_{test_type}',
         BypassPort = test_parms["Bypass"],
         ExecutionMode = "Search" if "SCR" in flow else "SearchWithScoreboard", # Use a conditional to control out execution mode based on which flow we are defining the test in.
         TestMode = "Functional",
         ForwardingMode = "None",
         FeatureSwitchSettings=Spec(f'ARR_CORE_{sku}_Specs.FeatureSwitch'),
         LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_max",
         TimingsTc="ARR_CORE_CXX:cpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800",
         Patlist='resetplb_8axx080808_phase2_all_MCarr_CA2P_hdmt2_hvm_list',
         BaseNumbers = None if "SCR" in flow else AUTO,
         EndVoltageLimits = Spec(f"__shared__::FlowMatrixSingular.CR_V{corner}_VALUE"),
         StartVoltages = Spec(f"__shared__::FlowMatrixSingular.CR_V{corner}_VALUE"),
         LimitGuardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
         StepSize=Spec("toDouble(0.01)"),
         PinMap = test_parms.get("PinMap", Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_PinMap')),
         PatternNameCounterIndexes=Spec(f'ARR_CORE_{sku}_Specs.PatternMap'),
         RecoveryMode=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery'),
         RecoveryOptions = "",
         RecoveryTrackingIncoming = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_DCM'),
         RecoveryTrackingOutgoing=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_Tracker'),
         SetPointsPlistParamName = "Patlist",
         VoltageTargets = Spec(f'ARR_CORE_{sku}_Specs.voltage_target'),
         FivrCondition = "NOM_CCF_CORE",
         FailCaptureCount = Spec("toInteger(1)"),
         FivrConditionPlistParamName = "Patlist",
         #DtsConfiguration = Spec(f'ARR_CORE_{sku}_Specs.dtsconfig'),
         VoltageConverter = test_parms.get("VoltageConverter", Spec(f'"--dlvrpins VCCIA --expressions "' + f' + DROPOUT.CR_F5')),
         SetPointsPreInstance = Spec(f'PSPRE.CR_F5+' f'","+' f'"MCdrv:"+'+Spec(f'ARR_CORE_{sku}_Specs.corefreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.{FlowMatrix}_FREQ+")+'"GHz,MCdrv:"+'+Spec(f'ARR_CORE_{sku}_Specs.ringfreq+''":"')+Spec(f"+ __shared__::FlowMatrixSingular.CCF_F5_FREQ")+f'+"GHz"'),
         SetPointsPostInstance = Spec(f'PSPOST.CR_F5'),
         _fitem=Fitem('SAME', edc = test_parms["IS_EDC"], # Define the Fitem info. We define the EDC status as an input param for ease of control in the future.
                        r0 = pFail(setbin=-60, goto="NEXT"),
                        r1 = pPass(goto="NEXT"),
                        r2 = pFail(setbin=-60, goto="NEXT"),
                        r3 = pPass(goto="NEXT"),
                        r4 = pFail(setbin=-60, goto="NEXT"),
                        r5 = pFail(setbin=-60, goto="NEXT"))))
  
   return test_list_vmaxflow
   
#################################################################################
#							INIT SUBFLOW
#
#	- Need to have pinmap decoder
#
#################################################################################
#init_flow = "INIT"
#
##INIT SUBFLOW
#INIT_SUBFLOW = Flow(f'ARR_CORE_{sku}_INIT')    

#################################################################
#                       XCRF1 SUBFLOW
#
#################################################################
XCRF1_Flow = "XCRF1"                  # Define the name of your flow
XCRF1_Corner = "F1"
XCRF1_FlowMatrix = "CR_F1_FREQ"       # Define the FlowMatrix attribute associated with this flow
XCRF1_Subflow = "F1XCR"


# Input
if sku == "CX816":
    XCRF1_content_list = {
        #"C0C1": {"Bypass": 1, "IS_EDC": True},  # Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
        #"C2C3": {"Bypass": 1, "IS_EDC": True},
        "ALL": {"Bypass": 1, "IS_EDC": True}
    }
else:
    XCRF1_content_list = {}

XCRF1_Tests = get_test_list_f1_f4(XCRF1_Flow, XCRF1_Corner, XCRF1_FlowMatrix, XCRF1_Subflow, XCRF1_content_list)

XCRF1_Subflow = Flow(f"ARR_CORE_{sku}_F1XCR @F1XCR_SubFlow", XCRF1_Tests)
#################################################################
#                       XCRF2 SUBFLOW
#
#################################################################
XCRF2_Flow = "XCRF2"                  # Define the name of your flow
XCRF2_Corner = "F2"
XCRF2_FlowMatrix = "CR_F2_FREQ"       # Define the FlowMatrix attribute associated with this flow
XCRF2_Subflow = "F2XCR"

# Input
if sku == "CX816":
    XCRF2_content_list = {
        #"C0C1": {"Bypass": 1, "IS_EDC": True},  # Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
        #"C2C3": {"Bypass": 1, "IS_EDC": True},
        "ALL": {"Bypass": 1, "IS_EDC": True}
    }
else:
    XCRF2_content_list = {}

XCRF2_Tests = get_test_list_f1_f4(XCRF2_Flow, XCRF2_Corner, XCRF2_FlowMatrix, XCRF2_Subflow, XCRF2_content_list)

XCRF2_Subflow = Flow(f"ARR_CORE_{sku}_F2XCR @F2XCR_SubFlow", XCRF2_Tests)

#################################################################
#                       XCRF3 SUBFLOW
#
#################################################################
XCRF3_Flow = "XCRF3"                  # Define the name of your flow
XCRF3_Corner = "F3"
XCRF3_FlowMatrix = "CR_F3_FREQ"       # Define the FlowMatrix attribute associated with this flow
XCRF3_Subflow = "F3XCR"

# Input
if sku == "CX816":
    XCRF3_content_list = {
        #"C0C1": {"Bypass": 1, "IS_EDC": True},  # Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
        #"C2C3": {"Bypass": 1, "IS_EDC": True},
        "ALL": {"Bypass": 1, "IS_EDC": True}
    }
else:
    XCRF3_content_list = {}

XCRF3_Tests = get_test_list_f1_f4(XCRF3_Flow, XCRF3_Corner, XCRF3_FlowMatrix, XCRF3_Subflow, XCRF3_content_list)

XCRF3_Subflow = Flow(f"ARR_CORE_{sku}_F3XCR @F3XCR_SubFlow", XCRF3_Tests)

#################################################################
#                       XCRF4 SUBFLOW
#
#################################################################
# FlowMatrixRule Definition


XCRF4_Flow = "XCRF4"                  # Define the name of your flow
XCRF4_Corner = "F4"
XCRF4_FlowMatrix = "CR_F4_FREQ"       # Define the FlowMatrix attribute associated with this flow
XCRF4_Subflow = "F4XCR"

# Input
if sku == "CX816":
    XCRF4_content_list = {
        #"C0C1": {"Bypass": 1, "IS_EDC": True},  # Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
        #"C2C3": {"Bypass": 1, "IS_EDC": True},
        "ALL": {"Bypass": 1, "IS_EDC": True}
    }
else:
    XCRF4_content_list = {}

XCRF4_Tests = get_test_list_f1_f4(XCRF4_Flow, XCRF4_Corner, XCRF4_FlowMatrix, XCRF4_Subflow, XCRF4_content_list)

XCRF4_Subflow = Flow(f"ARR_CORE_{sku}_F4XCR @F4XCR_SubFlow", XCRF4_Tests)


#################################################################
#                       XCRF5 SUBFLOW
#
#################################################################
XCRF5_Flow = "XCRF5"                  # Define the name of your flow
XCRF5_Corner = "F5"			   
XCRF5_FlowMatrix = "CR_F5_FREQ"    
XCRF5_CornerID = "C5"		# Define the FlowMatrix attribute associated with this flow
XCRF5_Subflow = "F5XCR"

APEX_Flow = "XCRF5"                  # Define the name of your flow
APEX_Corner = "F5"                        
APEX_FlowMatrix = "CR_F5_FREQ"       # Define the FlowMatrix attribute associated with this flow

# Input
if sku == "CX816":
    XCRF5_content_list = {
    #"C0C1": {"Bypass": 1, "IS_EDC": True},  # Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
    #"C2C3": {"Bypass": 1, "IS_EDC": True},
    "ALL": {"Bypass": 1, "IS_EDC": True}
    }

    ApexTC_content_list = {
    #"C0C1": {"Bypass": 1, "IS_EDC": True},  # Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
    #"C2C3": {"Bypass": 1, "IS_EDC": True},
    "ALL": {"Bypass": 1, "IS_EDC": True}
    }
else:
    {

        }

XCRF5_Tests = get_test_list(XCRF5_Flow, XCRF5_Corner, XCRF5_FlowMatrix, XCRF5_CornerID, XCRF5_Subflow, XCRF5_content_list)


#XCRF5_Subflow = Flow(f"ARR_CORE_{sku}_F5XCR @F5XCR_SubFlow", XCRF5_Tests)*enable when disable apextc


APEX_Tests = get_test_apextc(APEX_Flow, APEX_Corner, APEX_FlowMatrix, XCRF5_Subflow, ApexTC_content_list)
APEX_COMP = Flow("ARR_CORE_FMAX", APEX_Tests)
  
XCRF5_Subflow = Flow(f"ARR_CORE_{sku}_F5XCR @F5XCR_SubFlow", 
                     Fitem ('SAME', APEX_COMP, r0=pFail(ret=0 ), r1=pPass(goto="NEXT")),
                     XCRF5_Tests)





#################################################################
    #         
    #                       FMIN SUBFLOW                      
    #
#################################################################
FMIN_Flow = "FMIN"                  # Define the name of your flow
FMIN_Corner = "FMIN"                        
FMIN_FlowMatrix = "CR_FMIN"       # Define the FlowMatrix attribute associated with this flow
FMIN_Subflow = "FMINXCR"

testinput = {}# This is a placeholder for the test input. We will use an empty dictionary for now.

# Input
if sku == "CX816":
    FMIN_content_list = {
   #"C0C1" : {"Bypass" : 1, "IS_EDC" : True}, # Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
   #"C2C3" : {"Bypass" : 1, "IS_EDC" : True},
   "ALL" : {"Bypass" : 1, "IS_EDC" : True}
    }
else:
    FMIN_content_list = {}

FMIN_Tests = get_test_list_fmin(FMIN_Flow, testinput, FMIN_Corner, FMIN_FlowMatrix, FMIN_Subflow, FMIN_content_list)

FMIN_Subflow = Flow(f"ARR_CORE_{sku}_FMINXCR @FMINXCR_SubFlow", FMIN_Tests)

#################################################################
    #         
    #                       VMAX SUBFLOW                      
    #
#################################################################
VMAX_Flow = "VMAX"                  # Define the name of your flow
VMAX_Corner = "MAX"                        
VMAX_FlowMatrix = "CR_F5"       # Define the FlowMatrix attribute associated with this flow
VMAX_Subflow = "VMAXXCR"

if sku == "CX816":
    VMAX_content_list = {
   #"C0C1" : {"Bypass" : 1, "IS_EDC" : True}, # Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
   #"C2C3" : {"Bypass" : 1, "IS_EDC" : True},
   "ALL" : {"Bypass" : 1, "IS_EDC" : True}
    }
else:
   {
       }

VMAX_Tests = get_test_vmax(VMAX_Flow, VMAX_Corner, VMAX_FlowMatrix, VMAX_Subflow, VMAX_content_list)

VMAX_Subflow = Flow(f"ARR_CORE_{sku}_VMAXXCR @VMAXXCR_SubFlow", VMAX_Tests)

#################################################################
#         
#                       VMAXXCRLO SUBFLOW                      
#
#################################################################
VMAXXCRLO_Flow = "VMAX"                  # Define the name of your flow
VMAXXCRLO_Corner = "MAX"                        
VMAXXCRLO_FlowMatrix = "CR_F5"       # Define the FlowMatrix attribute associated with this flow
VMAXXCRLO_Subflow = "VMAXXCRLO"

if sku == "CX816":
    VMAXXCRLO_content_list = {
   #"C0C1" : {"Bypass" : 1, "IS_EDC" : True}, # Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
   #"C2C3" : {"Bypass" : 1, "IS_EDC" : True},
   "ALL" : {"Bypass" : 1, "IS_EDC" : True}
    }
else:
   {
       }

VMAXXCRLO_Tests = get_test_vmax(VMAXXCRLO_Flow, VMAXXCRLO_Corner, VMAXXCRLO_FlowMatrix, VMAXXCRLO_Subflow, VMAXXCRLO_content_list)

VMAXXCRLO_Subflow = Flow(f"ARR_CORE_{sku}_VMAXXCRLO @VMAXXCRLO_SubFlow", VMAXXCRLO_Tests)


#################################################################################
#							BEGINCPUNOM SUBFLOW
#
#	- Need to have VFDM apply
#	- Need to have RWA apply
#	- Placeholder for VFDM rebuild_
#	- PMUCS NOM 
#
#################################################################################
begincpunom_flow = "BEGINCPUNOM"
begincpunom_corner = "LFM"

# Define the BEGINCPU subflow

#begcpunom_vmintc_ssa_core_vnnaon_pmuc_f2_c0c1_tli = {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": True}
#begcpunom_vmintc_ssa_core_vnnaon_pmuc_f2_c0c1 = get_test_list_ssa_core_vnnaon_pmuc_f2_c0c1(begincpunom_flow, begincpunom_corner, begcpunom_vmintc_ssa_core_vnnaon_pmuc_f2_c0c1_tli)

begcpunom_vmintc_ssa_core_vnnaon_pmuc_f2_all_tli = {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": True}
begcpunom_vmintc_ssa_core_vnnaon_pmuc_f2_all = get_test_list_ssa_core_vnnaon_pmuc_f2_all(begincpunom_flow, begincpunom_corner, begcpunom_vmintc_ssa_core_vnnaon_pmuc_f2_all_tli)


#begcpunom_vmintc_xsa_core_vccc_c0c1_nom_tli = {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": True}
#begcpunom_vmintc_xsa_core_vccc_c0c1_nom = get_test_list_xsa_core_vccc_c0c1_nom(begincpunom_flow, begincpunom_corner, begcpunom_vmintc_xsa_core_vccc_c0c1_nom_tli)

begcpunom_vmintc_xsa_core_vccc_all_nom_tli = {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": True}
begcpunom_vmintc_xsa_core_vccc_all_nom = get_test_list_xsa_core_vccc_all_nom(begincpunom_flow, begincpunom_corner, begcpunom_vmintc_xsa_core_vccc_all_nom_tli)

#begcpunom_vmintc_ssa_core_vnnaon_pmuc_f2_c2c3_tli = {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": True}
#begcpunom_vmintc_ssa_core_vnnaon_pmuc_f2_c2c3 = get_test_list_ssa_core_vnnaon_pmuc_f2_c2c3(begincpunom_flow, begincpunom_corner, begcpunom_vmintc_ssa_core_vnnaon_pmuc_f2_c2c3_tli)

#begcpunom_vmintc_xsa_core_vccc_c2c3_nom_tli = {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": True}
#begcpunom_vmintc_xsa_core_vccc_c2c3_nom = get_test_list_xsa_core_vccc_c2c3_nom(begincpunom_flow, begincpunom_corner, begcpunom_vmintc_xsa_core_vccc_c2c3_nom_tli)


#BEGINCPU SUBFLOW
#BEGINCPUNOM = Flow(
#    f'ARR_CORE_{sku}_BEGINCPUNOM',
#    begcpunom_vmintc_ssa_core_vnnaon_pmuc_f2_c0c1 + begcpunom_vmintc_xsa_core_vccc_c0c1_nom + begcpunom_vmintc_ssa_core_vnnaon_pmuc_f2_c2c3 + begcpunom_vmintc_xsa_core_vccc_c2c3_nom + begcpunom_vmintc_ssa_core_vnnaon_pmuc_f2_all + begcpunom_vmintc_xsa_core_vccc_all_nom
#    )              

BEGINCPUNOM = Flow(
    f'ARR_CORE_{sku}_BEGINCPUNOM',
      begcpunom_vmintc_xsa_core_vccc_all_nom + begcpunom_vmintc_ssa_core_vnnaon_pmuc_f2_all 
    )  
#################################################################################
#							ENDCPUNOM SUBFLOW
#
#	-Need retention 
#################################################################################
endcpunom_flow = "ENDCPUNOM"
endcpunom_corner = "VCCC"

# Define the ENDCPU subflow

#endcpunom_vmintc_ssa_core_vccc_c6s_retention_c0c1_tli = {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": True}
#endcpunom_vmintc_ssa_core_vccc_c6s_retention_c0c1 = get_test_list_ssa_core_vccc_c6s_retention_c0c1(endcpunom_flow, endcpunom_corner, endcpunom_vmintc_ssa_core_vccc_c6s_retention_c0c1_tli)

#endcpunom_vmintc_ssa_core_vccc_c6s_retention_c2c3_tli = {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": True}
#endcpunom_vmintc_ssa_core_vccc_c6s_retention_c2c3 = get_test_list_ssa_core_vccc_c6s_retention_c2c3(endcpunom_flow, endcpunom_corner, endcpunom_vmintc_ssa_core_vccc_c6s_retention_c2c3_tli)

endcpunom_vmintc_ssa_core_vccc_c6s_retention_all_tli = {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": True}
endcpunom_vmintc_ssa_core_vccc_c6s_retention_all = get_test_list_ssa_core_vccc_c6s_retention_all(endcpunom_flow, endcpunom_corner, endcpunom_vmintc_ssa_core_vccc_c6s_retention_all_tli)


#ENDCPUNOM SUBFLOW
#ENDCPUNOM = Flow(
#    f'ARR_CORE_{sku}_ENDCPUNOM',
#    endcpunom_vmintc_ssa_core_vccc_c6s_retention_c0c1 + endcpunom_vmintc_ssa_core_vccc_c6s_retention_c2c3 + endcpunom_vmintc_ssa_core_vccc_c6s_retention_all
#    )               

ENDCPUNOM = Flow(
    f'ARR_CORE_{sku}_ENDCPUNOM',
    endcpunom_vmintc_ssa_core_vccc_c6s_retention_all
    )   
#################################################################################
#							ENDCPUMAX SUBFLOW
#
#	-Need retention 
#################################################################################
endcpumax_flow = "ENDCPUMAX"
endcpumax_corner = "VNNAON"

# Define the ENDCPUMAX subflow

#endcpumax_ssa_core_vnnaon_pmuc_f1_c0c1_max_tli = {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": True}
#endcpumax_ssa_core_vnnaon_pmuc_f1_c0c1_max = get_test_list_ssa_core_vnnaon_pmuc_f1_c0c1_max(endcpumax_flow, endcpumax_corner, endcpumax_ssa_core_vnnaon_pmuc_f1_c0c1_max_tli)

#endcpumax_ssa_core_vnnaon_pmuc_f1_c2c3_max_tli = {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": True}
#endcpumax_ssa_core_vnnaon_pmuc_f1_c2c3_max = get_test_list_ssa_core_vnnaon_pmuc_f1_c2c3_max(endcpumax_flow, endcpumax_corner, endcpumax_ssa_core_vnnaon_pmuc_f1_c2c3_max_tli)

endcpumax_ssa_core_vnnaon_pmuc_f1_all_max_tli = {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": True}
endcpumax_ssa_core_vnnaon_pmuc_f1_all_max = get_test_list_ssa_core_vnnaon_pmuc_f1_all_max(endcpumax_flow, endcpumax_corner, endcpumax_ssa_core_vnnaon_pmuc_f1_all_max_tli)

#ENDCPUMAX SUBFLOW
#ENDCPUMAX = Flow(
#    f'ARR_CORE_{sku}_ENDCPUMAX',
#    endcpumax_ssa_core_vnnaon_pmuc_f1_c0c1_max + endcpumax_ssa_core_vnnaon_pmuc_f1_c2c3_max + endcpumax_ssa_core_vnnaon_pmuc_f1_all_max
#    )    

ENDCPUMAX = Flow(
    f'ARR_CORE_{sku}_ENDCPUMAX',
    endcpumax_ssa_core_vnnaon_pmuc_f1_all_max
    )   

 