from pymtpl.por_methods import VminTC,DDGShmooTC, PrimeHvqkTestMethod, PrimeMbistTestMethod, AuxiliaryTC, ScreenTC,PrimeVirtualFuseExportToSharedStorageTestMethod,PrimePatConfigTestMethod,PrimeSampleRateTestMethod,MbistRasterRepairTC,PrimeScanHRYSSNTestMethod,PrimeScanSPOFITestMethod, RunCallback, ApexTC
from pymtpl.core import Flow, Fitem, pPass, pFail, Initialize, NativeMultiTrial, AUTO, MTLdefault, InitializeNVLClass, Import, TrialParamSpec, Spec, MConfig, os
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
    "DCM0": "VCCCORE0",
    "DCM1": "VCCCORE1",
    "DCM2": "VCCCORE2",
    "DCM3": "VCCCORE3"
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

###Define VMINTC in BEGCPUNOM subflow##
# Create an empty list that will contain the final list of the test
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
        LevelsTc='BASE::SBF_nom_lvl',
        TimingsTc='ARR_CORE::cpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800',
        BaseNumbers = None if "SCR" in flow else AUTO,
        EndVoltageLimits=Spec(f'ARR_CORE_{sku}_Specs.CORE_HVQK_LowSearch'),
        ExecutionMode="SearchWithScoreboard",
        #FailCaptureCount=72000,
        FeatureSwitchSettings='disable_masked_targets',
        ForwardingMode='Input',
        MaxRepetitionCount=1,
        PatternNameCounterIndexes=Spec(f'ARR_CORE_{sku}_Specs.PatternMap'),
        PinMap=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_PinMap'),
        RecoveryMode=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_DCM'),
        RecoveryTrackingIncoming=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_Mode'),
        RecoveryTrackingOutgoing=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_Tracker'),
        #ScoreboardEdgeTicks=Spec(f'ARR_CORE_{sku}_Specs.CORE_HVQK_#ScoreboardEdgeTicks'),
        ##MaxFailsNum=Spec("toInteger(ARR_CORE_Specs.CORE_HVQK_MaxFailCapture)'),
        SetPointsPlistParamName='Patlist',
        StartVoltages=Spec(f'ARR_CORE_{sku}_Specs.CORE_HVQK_HighSearch'),
        StartVoltagesForRetry=Spec(f'ARR_CORE_{sku}_Specs.CORE_HVQK_LowSearch'),
        StepSize=0.02,
        TestMode='Scoreboard',
        #Voltagetarget=Spec("ARR_CORE_Specs.CORE_PMUCS_Voltage_Target"),
        SetPointsPreInstance = '',
        RecoveryOptions=Spec(f'ARR_CORE_{sku}_Specs.CORE_RecoveryOptions'),
        _fitem=Fitem(
            'SAME',
            edc=testinput.get("ISEDC"),
            r0=pFail(setbin=-20, ret=0),
            r1=pPass(goto="NEXT"),
            r2=pFail(setbin=-20, ret=0),
            r3=pFail(setbin=-20, ret=0),
            r4=pFail(setbin=-20, ret=0),
            r5=pFail(setbin=-20, ret=0)
        )
    )
    test_listt_begincpunom.append(ssa_core_vnnaon_pmucs_c0c1_nom)
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
        LevelsTc='BASE::SBF_nom_lvl',
        TimingsTc='ARR_CORE::cpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800',
        BaseNumbers = None if "SCR" in flow else AUTO,
        EndVoltageLimits=Spec(f'ARR_CORE_{sku}_Specs.CORE_HVQK_HighSearch'),
        ExecutionMode='Search',
        ##FailCaptureCount=Spec("toInteger(ARR_CORE_Specs.CORE_BEGIN_#FailCaptureCountOverride)"),
        #FeatureSwitchSettings=Spec("toInteger(ARR_CORE_Specs.CORE_Recovery_FeatureSwitchSet)"),
        ForwardingMode='InputOutput',
        MaxRepetitionCount=1,
        PatternNameCounterIndexes=Spec(f'ARR_CORE_{sku}_Specs.PatternMap'),
        PinMap=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_PinMap'),
        RecoveryMode='RecoveryPort',
        RecoveryTrackingIncoming='CR3_M,CR2_M,CR1_M,CR0_M',
        RecoveryTrackingOutgoing='CR3,CR2,CR1,CR0',
        RecoveryOptions='S816_6C_8A',
        ##ScoreboardEdgeTicks=Spec("toInteger(ARR_CORE_Specs.CORE_BEGIN_#ScoreboardEdgeTicks)"),
        ##MaxFailsNum=Spec("toInteger(ARR_CORE_Specs.CORE_BEGIN_MaxFailCapture)"),
        SetPointsPlistParamName='Patlist',
        StartVoltages=Spec(f'ARR_CORE_{sku}_Specs.CORE_BEGIN_LowSearch'),
        StepSize=0.02,
        TestMode='Scoreboard',
        #Voltagetarget=Spec("ARR_CORE_Specs.CORE_VCCC_Voltage_Target"), *need to remove due to vmintc template issue
        SetPointsPreInstance = '',
        _fitem=Fitem(
            'SAME',
            r0=pFail(setbin=-20, ret=0),
            r1=pPass(ret=1),
            r2=pFail(setbin=-20, ret=0),
            r3=pPass(goto="NEXT"),
            r4=pFail(setbin=-20, ret=0),
            r5=pFail(setbin=-20, ret=0)
        )
    )
    test_listt_begincpunom.append(xsa_core_vccc_c0c1_nom)
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
        LevelsTc='BASE::SBF_nom_lvl',
        TimingsTc='ARR_CORE::cpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800',
        BaseNumbers = None if "SCR" in flow else AUTO,
        EndVoltageLimits=Spec(f'ARR_CORE_{sku}_Specs.CORE_HVQK_LowSearch'),
        ExecutionMode="SearchWithScoreboard",
        #FailCaptureCount=72000,
        FeatureSwitchSettings='disable_masked_targets',
        ForwardingMode='Input',
        MaxRepetitionCount=1,
        PatternNameCounterIndexes=Spec(f'ARR_CORE_{sku}_Specs.PatternMap'),
        PinMap=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_PinMap'),
        RecoveryMode=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_DCM'),
        RecoveryTrackingIncoming=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_Mode'),
        RecoveryTrackingOutgoing=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_Tracker'),
        #ScoreboardEdgeTicks=Spec(f'ARR_CORE_{sku}_Specs.CORE_HVQK_#ScoreboardEdgeTicks'),
        ##MaxFailsNum=Spec("toInteger(ARR_CORE_Specs.CORE_HVQK_MaxFailCapture)'),
        SetPointsPlistParamName='Patlist',
        StartVoltages=Spec(f'ARR_CORE_{sku}_Specs.CORE_HVQK_HighSearch'),
        StartVoltagesForRetry=Spec(f'ARR_CORE_{sku}_Specs.CORE_HVQK_LowSearch'),
        StepSize=0.02,
        TestMode='Scoreboard',
        #Voltagetarget=Spec("ARR_CORE_Specs.CORE_PMUCS_Voltage_Target"),
        SetPointsPreInstance = '',
        RecoveryOptions=Spec(f'ARR_CORE_{sku}_Specs.CORE_RecoveryOptions'),
        _fitem=Fitem(
            'SAME',
            edc=testinput.get("ISEDC"),
            r0=pFail(setbin=-20, ret=0),
            r1=pPass(goto="NEXT"),
            r2=pFail(setbin=-20, ret=0),
            r3=pFail(setbin=-20, ret=0),
            #r3=pPass(goto="NEXT"),#example port if want to set EDC
            r4=pFail(setbin=-20, ret=0),
            r5=pFail(setbin=-20, ret=0)
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
        LevelsTc='BASE::SBF_nom_lvl',
        TimingsTc='ARR_CORE::cpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800',
        BaseNumbers = None if "SCR" in flow else AUTO,
        EndVoltageLimits=Spec(f'ARR_CORE_{sku}_Specs.CORE_HVQK_HighSearch'),
        ExecutionMode='Search',
        ##FailCaptureCount=Spec("toInteger(ARR_CORE_Specs.CORE_BEGIN_#FailCaptureCountOverride)"),
        #FeatureSwitchSettings=Spec("toInteger(ARR_CORE_Specs.CORE_Recovery_FeatureSwitchSet)"),
        ForwardingMode='InputOutput',
        MaxRepetitionCount=1,
        PatternNameCounterIndexes=Spec(f'ARR_CORE_{sku}_Specs.PatternMap'),
        PinMap=Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_PinMap'),
        RecoveryMode='RecoveryPort',
        RecoveryTrackingIncoming='CR3_M,CR2_M,CR1_M,CR0_M',
        RecoveryTrackingOutgoing='CR3,CR2,CR1,CR0',
        RecoveryOptions='S816_6C_8A',
        ##ScoreboardEdgeTicks=Spec("toInteger(ARR_CORE_Specs.CORE_BEGIN_#ScoreboardEdgeTicks)"),
        ##MaxFailsNum=Spec("toInteger(ARR_CORE_Specs.CORE_BEGIN_MaxFailCapture)"),
        SetPointsPlistParamName='Patlist',
        StartVoltages=Spec(f'ARR_CORE_{sku}_Specs.CORE_BEGIN_LowSearch'),
        StepSize=0.02,
        TestMode='Scoreboard',
        #Voltagetarget=Spec("ARR_CORE_Specs.CORE_VCCC_Voltage_Target"),
        SetPointsPreInstance = '',
        _fitem=Fitem(
            'SAME',
            r0=pFail(setbin=-20, ret=0),
            r1=pPass(ret=1),
            r2=pFail(setbin=-20, ret=0),
            r3=pFail(setbin=-20, ret=0),
            r4=pFail(setbin=-20, ret=0),
            r5=pFail(setbin=-20, ret=0)
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
        LevelsTc = 'BASE::SBF_nom_lvl',
        TimingsTc = 'ARR_CORE::cpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800',
        BaseNumbers = None if "SCR" in flow else AUTO,
        EndVoltageLimits = Spec(f'ARR_CORE_{sku}_Specs.CORE_HVQK_NomSearch'),
        ExecutionMode = 'SearchWithScoreboard',
        ##FailCaptureCount = Spec("toInteger(ARR_CORE_Specs.CORE_BEGIN_#FailCaptureCountOverride)"),
        FeatureSwitchSettings = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_FeatureSwitchSet'),
        ForwardingMode = Spec(f'ARR_CORE_{sku}_Specs.CORE_Fowarding_Mode'),
        MaxRepetitionCount = 1,
        PatternNameCounterIndexes=Spec(f'ARR_CORE_{sku}_Specs.PatternMap'),
        PinMap = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_PinMap'),
        RecoveryMode = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_Mode'),
        RecoveryTrackingIncoming = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_DCM'),
        RecoveryTrackingOutgoing = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_Tracker'),
        #ScoreboardPerPatternFails = Spec("toInteger(ARR_CORE_Specs.ScoreBoardPerPatFailure)"),
        ##ScoreboardEdgeTicks = Spec("toInteger(ARR_CORE_Specs.CORE_HVQK_#ScoreboardEdgeTicks)"),
        ##MaxFailsNum = Spec("toInteger(ARR_CORE_Specs.CORE_HVQK_MaxFailCapture)"),
        SetPointsPlistParamName = 'Patlist',
        StartVoltages = Spec(f'ARR_CORE_{sku}_Specs.CORE_HVQK_NomSearch'),
        StepSize=0.02,
        TestMode = 'Scoreboard',
        #Voltagetarget = Spec("ARR_CORE_Specs.CORE_VCCC_Voltage_Target"),
        SetPointsPreInstance = '',
        RecoveryOptions = Spec(f'ARR_CORE_{sku}_Specs.CORE_RecoveryOptions'),
        _fitem=Fitem( 
            'SAME',
            edc=testinput.get("ISEDC"),
            r0=pFail(setbin=-20, ret=0),
            r1=pPass(goto="NEXT"),
            r2=pFail(setbin=-20, ret=0),
            r3=pFail(setbin=-20, ret=0),
            r4=pFail(setbin=-20, ret=0),
            r5=pFail(setbin=-20, ret=0)
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
        LevelsTc = 'BASE::SBF_nom_lvl',
        TimingsTc = 'ARR_CORE::cpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800',
        BaseNumbers = None if "SCR" in flow else AUTO,
        EndVoltageLimits = Spec(f'ARR_CORE_{sku}_Specs.CORE_HVQK_NomSearch'),
        ExecutionMode = 'SearchWithScoreboard',
        ##FailCaptureCount = Spec("toInteger(ARR_CORE_Specs.CORE_BEGIN_#FailCaptureCountOverride)"),
        FeatureSwitchSettings = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_FeatureSwitchSet'),
        ForwardingMode = Spec(f'ARR_CORE_{sku}_Specs.CORE_Fowarding_Mode'),
        MaxRepetitionCount = 1,
        PatternNameCounterIndexes=Spec(f'ARR_CORE_{sku}_Specs.PatternMap'),
        PinMap = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_PinMap'),
        RecoveryMode = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_Mode'),
        RecoveryTrackingIncoming = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_DCM'),
        RecoveryTrackingOutgoing = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_Tracker'),
        #ScoreboardPerPatternFails = Spec("toInteger(ARR_CORE_Specs.ScoreBoardPerPatFailure)"),
        ##ScoreboardEdgeTicks = Spec("toInteger(ARR_CORE_Specs.CORE_HVQK_#ScoreboardEdgeTicks)"),
        ##MaxFailsNum = Spec("toInteger(ARR_CORE_Specs.CORE_HVQK_MaxFailCapture)"),
        SetPointsPlistParamName = 'Patlist',
        StartVoltages = Spec(f'ARR_CORE_{sku}_Specs.CORE_HVQK_NomSearch'),
        StepSize=0.02,
        TestMode = 'Scoreboard',
        #Voltagetarget = Spec("ARR_CORE_Specs.CORE_VCCC_Voltage_Target"),
        SetPointsPreInstance = '',
        RecoveryOptions = Spec(f'ARR_CORE_{sku}_Specs.CORE_RecoveryOptions'),
        _fitem=Fitem( 
            'SAME',
            edc=testinput.get("ISEDC"),
            r0=pFail(setbin=-20, ret=0),
            r1=pPass(goto="NEXT"),
            r2=pFail(setbin=-20, ret=0),
            r3=pFail(setbin=-20, ret=0),
            r4=pFail(setbin=-20, ret=0),
            r5=pFail(setbin=-20, ret=0)
        )
    )
    test_listt_endcpunom.append(ssa_core_vccc_c6s_retention_c2c3)
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
        LevelsTc = 'BASE::SBF_nom_lvl',
        TimingsTc = 'ARR_CORE::cpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800',
        BaseNumbers = None if "SCR" in flow else AUTO,
        EndVoltageLimits = Spec(f'ARR_CORE_{sku}_Specs.CORE_HVQK_NomSearch'),
        ExecutionMode = 'SearchWithScoreboard',
        ##FailCaptureCount = Spec("toInteger(ARR_CORE_Specs.CORE_BEGIN_#FailCaptureCountOverride)"),
        FeatureSwitchSettings = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_FeatureSwitchSet'),
        ForwardingMode = Spec(f'ARR_CORE_{sku}_Specs.CORE_Fowarding_Mode'),
        MaxRepetitionCount = 1,
        PatternNameCounterIndexes=Spec(f'ARR_CORE_{sku}_Specs.PatternMap'),
        PinMap = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_PinMap'),
        RecoveryMode = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_Mode'),
        RecoveryTrackingIncoming = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_DCM'),
        RecoveryTrackingOutgoing = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_Tracker'),
        #ScoreboardPerPatternFails = Spec("toInteger(ARR_CORE_Specs.ScoreBoardPerPatFailure)"),
        ##ScoreboardEdgeTicks = Spec("toInteger(ARR_CORE_Specs.CORE_HVQK_#ScoreboardEdgeTicks)"),
        ##MaxFailsNum = Spec("toInteger(ARR_CORE_Specs.CORE_HVQK_MaxFailCapture)"),
        SetPointsPlistParamName = 'Patlist',
        StartVoltages = Spec(f'ARR_CORE_{sku}_Specs.CORE_HVQK_NomSearch'),
        StepSize=0.02,
        TestMode = 'Scoreboard',
        #Voltagetarget = Spec("ARR_CORE_Specs.CORE_VCCC_Voltage_Target"),
        SetPointsPreInstance = '',
        RecoveryOptions = Spec(f'ARR_CORE_{sku}_Specs.CORE_RecoveryOptions'),
        _fitem=Fitem( 
            'SAME',
            edc=testinput.get("ISEDC"),
            r0=pFail(setbin=-20, ret=0),
            r1=pPass(goto="NEXT"),
            r2=pFail(setbin=-20, ret=0),
            r3=pFail(setbin=-20, ret=0),
            r4=pFail(setbin=-20, ret=0),
            r5=pFail(setbin=-20, ret=0)
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
        LevelsTc = 'BASE::SBF_nom_lvl',
        TimingsTc = 'ARR_CORE::cpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800',
        BaseNumbers = None if "SCR" in flow else AUTO,
        EndVoltageLimits = Spec(f'ARR_CORE_{sku}_Specs.CORE_HVQK_NomSearch'),
        ExecutionMode = 'SearchWithScoreboard',
        ##FailCaptureCount = Spec("toInteger(ARR_CORE_Specs.CORE_BEGIN_#FailCaptureCountOverride)"),
        FeatureSwitchSettings = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_FeatureSwitchSet'),
        ForwardingMode = Spec(f'ARR_CORE_{sku}_Specs.CORE_Fowarding_Mode'),
        MaxRepetitionCount = 1,
        PatternNameCounterIndexes=Spec(f'ARR_CORE_{sku}_Specs.PatternMap'),
        PinMap = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_PinMap'),
        RecoveryMode = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_Mode'),
        RecoveryTrackingIncoming = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_DCM'),
        RecoveryTrackingOutgoing = Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_Tracker'),
        #ScoreboardPerPatternFails = Spec("toInteger(ARR_CORE_Specs.ScoreBoardPerPatFailure)"),
        ##ScoreboardEdgeTicks = Spec("toInteger(ARR_CORE_Specs.CORE_HVQK_#ScoreboardEdgeTicks)"),
        ##MaxFailsNum = Spec("toInteger(ARR_CORE_Specs.CORE_HVQK_MaxFailCapture)"),
        SetPointsPlistParamName = 'Patlist',
        StartVoltages = Spec(f'ARR_CORE_{sku}_Specs.CORE_HVQK_NomSearch'),
        StepSize=0.02,
        TestMode = 'Scoreboard',
        #Voltagetarget = Spec("ARR_CORE_Specs.CORE_VCCC_Voltage_Target"),
        SetPointsPreInstance = '',
        RecoveryOptions = Spec(f'ARR_CORE_{sku}_Specs.CORE_RecoveryOptions'),
        _fitem=Fitem( 
            'SAME',
            edc=testinput.get("ISEDC"),
            r0=pFail(setbin=-20, ret=0),
            r1=pPass(goto="NEXT"),
            r2=pFail(setbin=-20, ret=0),
            r3=pFail(setbin=-20, ret=0),
            r4=pFail(setbin=-20, ret=0),
            r5=pFail(setbin=-20, ret=0)
        )  # <-- This closing parenthesis was missing
    )
    test_listt_endcpumax.append(ssa_core_vnnaon_pmuc_f1_c2c3_max)

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
            template=VminTC(name=f'"XSA_CORE_SB_K_{subflow}_X_VCC_{corner}_" + ' + Spec(f"__shared__::CustomFlowMatrixSpecs.{FlowMatrix}_MHz") + f' + "_{test_type}"',
            
            TimingsTc="CPU_IP_BASE::cpu_fun_timing_mts100_tstprtclk50_tck100",
            BaseNumbers=None if "SCR" in flow else AUTO,
            EndVoltageLimits=Spec(f'ARR_CORE_{sku}_Specs.CORE_BEGIN_HighSearch'),
            ExecutionMode="Search" if "XCR" in flow else "SearchWithScoreboard",
            TestMode="MultiVmin",
            #FailCaptureCount=1,
            ##MaxFailsNum=Spec("toInteger(ARR_CORE_Specs.HVQK_VNNAON_MaxFailCapture)"),
            StartVoltages=Spec(f'ARR_CORE_{sku}_Specs.CORE_BEGIN_LowSearch'),
            StartVoltagesForRetry=Spec(f'ARR_CORE_{sku}_Specs.CORE_BEGIN_LowSearch'),
            StepSize=0.02,
            RecoveryMode="NoRecovery",
            BypassPort=test_parms.get("Bypass", -1),
            SetPointsPreInstance = '',
            SetPointsPostInstance='',
            LevelsTc="CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom",
            Patlist = 'resetplb_8axx080808_phase2_all_MCarr_CA2P_hdmt2_hvm_list',
            PatternNameCounterIndexes=Spec(f'ARR_CORE_{sku}_Specs.PatternMap'),
            RecoveryOptions="",
            # Removed 'End' and 'Start' as they are not valid arguments for VminTC
            FivrCondition="NOM",
            FlowIndex = TrialParamSpec(f"__shared__::FlowMatrixSingular.FlowIndex"),  
            FivrConditionPlistParamName="Patlist",
            VoltageConverter='--overrides CORE3:"+' + Spec(f"__shared__::FlowMatrixSingular.AT_VMAX_VALUE") + f'+",CORE2:"+' + Spec(f"__shared__::FlowMatrixSingular.AT_VMAX_VALUE") + f'+",CORE1:"+' + Spec(f"__shared__::FlowMatrixSingular.AT_VMAX_VALUE") + f'+",CORE0:"+' + Spec(f"__shared__::FlowMatrixSingular.AT_VMAX_VALUE") + f'+" --dlvrpins VCCIA',
            ),
            r0=pFail(setbin=-60, ret=0, trialaction=Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
            r1=pPass(setbin=-60, ret=0, trialaction="Exit"),
            r2=pFail(setbin=-60, ret=0, trialaction="Exit"),
            r3=pFail(setbin=-60, ret=0, trialaction="Exit"),
            r4=pFail(setbin=-60, ret=0, trialaction="Exit"),
            r5=pFail(setbin=-60, ret=0, trialaction="Exit"),
            _fitem=Fitem(
                'SAME',
                edc=test_parms["IS_EDC"],
                r0=pFail(setbin=-60, ret=0),
                r1=pPass(setbin=-60, goto="NEXT"),
                r2=pFail(setbin=-60, ret=0),
                r3=pFail(setbin=-60, ret=0),
                r4=pFail(setbin=-60, ret=0),
                r5=pFail(setbin=-60, ret=0)
            )
        ))
    return test_list_arrflow
 ########################################################################################################################
 #APEX_COMP VCC DEFINITION
 ########################################################################################################################
def get_test_apextc(flow, corner, FlowMatrix, subflow, content_list):
    """
    Generate a list of NativeMultiTrial APEXTC tests for the given flow, corner, FlowMatrix, subflow, and content_list.
    Ensures each test name is unique by appending an index.
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
                    DtsConfiguration="",
                    BypassPort=test_parms["Bypass"],
                    Targets="CORE3,CORE2,CORE1,CORE0",
                    ForwardingMode="Input",
                    PinMap=test_parms.get("PinMap", Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_PinMap')),
                    SetPointsPreInstance = '',
                    SetPointsPostInstance='',
                    LevelsTc="CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom",
                    TimingsTc="CPU_IP_BASE::cpu_fun_timing_mts800_tstprtclk400_tck100",
                    Patlist='resetplb_8axx080808_phase2_all_MCarr_CA2P_hdmt2_hvm_list',
                    PatternNameCounterIndexes=Spec(f'ARR_CORE_{sku}_Specs.PatternMap'),
                    RecoveryOptions="",
                    RecoveryTracking="CR",
                    End=Spec(f'__shared__::FlowMatrixSingular.APEX_CORE_MIN'),
                    Start=Spec(f'__shared__::FlowMatrixSingular.APEX_CORE_MAX'),
                    FivrCondition="NOM",
                    FivrConditionPlistParamName="Patlist",
                    VoltageConverter='--overrides CORE3:"+' + Spec(f"__shared__::FlowMatrixSingular.AT_VMAX_VALUE") + f'+",CORE2:"+' + Spec(f"__shared__::FlowMatrixSingular.AT_VMAX_VALUE") + f'+",CORE1:"+' + Spec(f"__shared__::FlowMatrixSingular.AT_VMAX_VALUE") + f'+",CORE0:"+' + Spec(f"__shared__::FlowMatrixSingular.AT_VMAX_VALUE") + f'+" --dlvrpins VCCIA',
                    ExportTokens="FXCRC3,FXCRC2,FXCRC1,FXCRC0",
                ),
                r0=pFail(setbin=-60, ret=0, trialaction="Exit"),
                r1=pPass(setbin=-60, ret=0, trialaction="Exit"),
                r2=pFail(setbin=-60, ret=0, trialaction="Exit"),
                r3=pFail(setbin=-60, ret=0, trialaction="Exit"),
                r4=pFail(setbin=-60, ret=0, trialaction="Exit"),
                r5=pFail(setbin=-60, ret=0, trialaction="Exit"),
                _fitem=Fitem(
                    'SAME',
                    edc=test_parms["IS_EDC"],
                    r0=pFail(setbin=-60, ret=0),
                    r1=pPass(setbin=-60, goto="NEXT"),
                    r2=pFail(setbin=-60, ret=0),
                    r3=pFail(setbin=-60, ret=0),
                    r4=pFail(setbin=-60, ret=0),
                    r5=pFail(setbin=-60, ret=0)
                )
            )
        )
    return test_list_apextcflow

########################################################################################################################
  #FMIN DEFINITION
########################################################################################################################
def get_test_list_fmin(flow, corner, FlowMatrix, subflow, content_list):

    test_list_fminflow = []  # Define an empty list. This will be used to append all the Fitems in the flow

    frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]
    # Loop through the content_list to create multiple tests based on the provided parameters
    for test_type, test_parms in content_list.items():
        test_list_fminflow.append(
            NativeMultiTrial(
                name=f"XSA_CORE_SB_K_{subflow}_X_{VOLTAGE_DOMAIN.upper()}_{corner}_{frequency_value}_{test_type}",
                exitaction="Continue",
                trialvar="CPU_TRIALS::FlowDomain.CORE",
                _comment='SpeedFlow F5XCR APEXTC test with MTT',
                template=VminTC(
                    name=f'"XSA_CORE_SB_K_{subflow}_X_VCCC_{corner}" + ' +
                         Spec(f"__shared__::CustomFlowMatrixSpecs.{FlowMatrix}_MHz") +
                         f' + "_{test_type}"',
                    BypassPort=test_parms["Bypass"],
                    ExecutionMode="Search" if "SCR" in flow else "SearchWithScoreboard",
                    TestMode="MultiVmin",
                    ForwardingMode="Input" if test_parms["IS_EDC"] else "InputOutput",
                    FeatureSwitchSettings='recovery_update_always,disable_masked_targets,print_per_target_increments,print_scoreboard_counters,fivr_mode_on',
                    LevelsTc="CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom",
                    TimingsTc="CPU_IP_BASE::cpu_fun_timing_mts800_tstprtclk400_tck100",
                    Patlist = 'resetplb_8axx080808_phase2_all_MCarr_CA2P_hdmt2_hvm_list',
                    BaseNumbers=None if "SCR" in flow else AUTO,
                    #CornerIdentifiers=TrialParamSpec(Spec(f"__shared__::CornerIdentifiers.CR_{corner_id}")),
                    EndVoltageLimits=Spec(f'ARR_CORE_{sku}_Specs.Search_VCCC_HighSearch'),
                    StartVoltages=Spec(f'ARR_CORE_{sku}_Specs.CORE_BEGIN_LowSearch'),
                    StartVoltagesForRetry = Spec('__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry, "")'),
                    LimitGuardband=Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
                    StepSize=0.02,
                    PinMap=test_parms.get("PinMap", Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_PinMap')),
                    PatternNameCounterIndexes=Spec(f'ARR_CORE_{sku}_Specs.PatternMap'),
                    RecoveryMode="NoRecovery",
                    RecoveryOptions="",
                    RecoveryTrackingOutgoing="",
                    SetPointsPlistParamName="Patlist",
                    FivrCondition="NOM",
                    #FailCaptureCount=Spec(f'ARR_CORE_{sku}_Specs.#FailCaptureCount'),
                    FivrConditionPlistParamName="Patlist",
                    DtsConfiguration="",
                    VoltageConverter='', 
                    SetPointsPreInstance = '',
                    SetPointsPostInstance='',
                ),
                r0=pFail(setbin=-60, ret=0, trialaction=Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r1=pPass(setbin=-60, ret=0, trialaction="Exit"),
                r2=pFail(setbin=-60, ret=0, trialaction="Exit"),
                r3=pFail(setbin=-60, ret=0, trialaction="Exit"),
                r4=pFail(setbin=-60, ret=0, trialaction="Exit"),
                r5=pFail(setbin=-60, ret=0, trialaction="Exit"),
                _fitem=Fitem(
                    'SAME',
                    edc=test_parms["IS_EDC"],
                    r0=pFail(setbin=-60, ret=0),
                    r1=pPass(setbin=-60, goto="NEXT"),
                    r2=pFail(setbin=-60, ret=0),
                    r3=pFail(setbin=-60, ret=0),
                    r4=pFail(setbin=-60, ret=0),
                    r5=pFail(setbin=-60, ret=0)
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
                    name=f'"XSA_CORE_SB_K_{subflow}_X_VCCC_{corner}" + ' +
                         Spec(f"__shared__::CustomFlowMatrixSpecs.{FlowMatrix}_MHz") +
                         f' + "_{test_type}"',
                    BypassPort=test_parms["Bypass"],
                    ExecutionMode="Search" if "SCR" in flow else "SearchWithScoreboard",
                    TestMode="MultiVmin",
                    ForwardingMode="Input" if test_parms["IS_EDC"] else "InputOutput",
                    FeatureSwitchSettings='recovery_update_always,disable_masked_targets,print_per_target_increments,print_scoreboard_counters,fivr_mode_on',
                    LevelsTc="CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom",
                    TimingsTc="CPU_IP_BASE::cpu_fun_timing_mts800_tstprtclk400_tck100",
                    Patlist = 'resetplb_8axx080808_phase2_all_MCarr_CA2P_hdmt2_hvm_list',
                    BaseNumbers=None if "SCR" in flow else AUTO,
                    #CornerIdentifiers=TrialParamSpec(Spec(f"__shared__::CornerIdentifiers.CR_{corner_id}")),
                    EndVoltageLimits=Spec(f"__shared__::FlowMatrixSingular.CR_HIGH_SEARCH_VALUE"),
                    StartVoltages=Spec(f"__shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE"),
                    LimitGuardband=Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
                    StepSize=0.02,
                    PinMap=test_parms.get("PinMap", Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_PinMap')),
                    PatternNameCounterIndexes=Spec(f'ARR_CORE_{sku}_Specs.PatternMap'),
                    RecoveryMode="NoRecovery",
                    RecoveryOptions="",
                    RecoveryTrackingOutgoing="",
                    SetPointsPlistParamName="Patlist",
                    FivrCondition="NOM",
                    #FailCaptureCount=Spec(f'ARR_CORE_{sku}_Specs.#FailCaptureCount'),
                    FivrConditionPlistParamName="Patlist",
                    DtsConfiguration="",
                    VoltageConverter='', 
                    FlowIndex = TrialParamSpec(f"__shared__::FlowMatrixSingular.FlowIndex"), 
                    SetPointsPreInstance = '',
                    SetPointsPostInstance='',
                ),
                r0=pFail(setbin=-60, ret=0, trialaction=Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r1=pPass(setbin=-60, ret=0, trialaction="Exit"),
                r2=pFail(setbin=-60, ret=0, trialaction="Exit"),
                r3=pFail(setbin=-60, ret=0, trialaction="Exit"),
                r4=pFail(setbin=-60, ret=0, trialaction="Exit"),
                r5=pFail(setbin=-60, ret=0, trialaction="Exit"),
                _fitem=Fitem(
                    'SAME',
                    edc=test_parms["IS_EDC"],
                    r0=pFail(setbin=-60, ret=0),
                    r1=pPass(setbin=-60, goto="NEXT"),
                    r2=pFail(setbin=-60, ret=0),
                    r3=pFail(setbin=-60, ret=0),
                    r4=pFail(setbin=-60, ret=0),
                    r5=pFail(setbin=-60, ret=0)
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
         #FeatureSwitchSettings = 'recovery_update_always,disable_masked_targets,print_per_target_increments,print_scoreboard_counters,fivr_mode_on',
         LevelsTc = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom",
         TimingsTc = "CPU_IP_BASE::cpu_fun_timing_mts800_tstprtclk400_tck100",
         Patlist='resetplb_8axx080808_phase2_all_MCarr_CA2P_hdmt2_hvm_list',
         BaseNumbers = None if "SCR" in flow else AUTO,
         EndVoltageLimits = Spec(f"__shared__::FlowMatrixSingular.CR_V{corner}_VALUE"),
         StartVoltages = Spec(f"__shared__::FlowMatrixSingular.CR_V{corner}_VALUE"),
         LimitGuardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
         StepSize=0.02,
         PinMap = test_parms.get("PinMap", Spec(f'ARR_CORE_{sku}_Specs.CORE_Recovery_PinMap')),
         PatternNameCounterIndexes=Spec(f'ARR_CORE_{sku}_Specs.PatternMap'),
         RecoveryMode = "NoRecovery",
         RecoveryOptions = "",
         RecoveryTrackingIncoming = "",
         RecoveryTrackingOutgoing = "",
         SetPointsPlistParamName = "Patlist",
         #VoltageTargets = "CORE3,CORE2,CORE1,CORE0",
         FivrCondition = "NOM",
         #FailCaptureCount = Spec(f'ARR_CORE_{sku}_Specs.#FailCaptureCount'), # This is the number of failures we want to capture before we stop the test.
         FivrConditionPlistParamName = "Patlist",
         DtsConfiguration = "", # This is a placeholder for the DTS configuration. We will use an empty string for now.
         VoltageConverter='', 
         SetPointsPreInstance = '', # This is a placeholder for the SetPointsPreInstance. We will use an empty string for now.
         SetPointsPostInstance='',
         _fitem=Fitem('SAME', edc = test_parms["IS_EDC"], # Define the Fitem info. We define the EDC status as an input param for ease of control in the future.
                        r0 = pFail(setbin=-60, ret=0),
                        r1 = pPass(setbin=-60, goto="NEXT"),
                        r2 = pFail(setbin=-60, ret=0),
                        r3 = pFail(setbin=-60, ret=0),
                        r4 = pFail(setbin=-60, ret=0),
                        r5 = pFail(setbin=-60, ret=0))))
  
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
        "C0C1": {"Bypass": 1, "IS_EDC": False},  # Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
        "C2C3": {"Bypass": 1, "IS_EDC": False}
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
        "C0C1": {"Bypass": 1, "IS_EDC": False},  # Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
        "C2C3": {"Bypass": 1, "IS_EDC": False}
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
        "C0C1": {"Bypass": 1, "IS_EDC": False},  # Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
        "C2C3": {"Bypass": 1, "IS_EDC": False}
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
        "C0C1": {"Bypass": 1, "IS_EDC": False},  # Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
        "C2C3": {"Bypass": 1, "IS_EDC": False}
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
    "C0C1": {"Bypass": 1, "IS_EDC": False},  # Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
    "C2C3": {"Bypass": 1, "IS_EDC": False}
    }

    ApexTC_content_list = {
    "C0C1": {"Bypass": 1, "IS_EDC": False},  # Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
    "C2C3": {"Bypass": 1, "IS_EDC": False}
    }
else:
    {

        }

XCRF5_Tests = get_test_list(XCRF5_Flow, XCRF5_Corner, XCRF5_FlowMatrix, XCRF5_CornerID, XCRF5_Subflow, XCRF5_content_list)

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
#FMIN_Flow = "FMIN"                  # Define the name of your flow
#FMIN_Corner = "FMIN"                        
#FMIN_FlowMatrix = "CR_FMIN"       # Define the FlowMatrix attribute associated with this flow
#FMIN_Subflow = "FMINXCR"
#
## Input
#if sku == "CX816":
#    FMIN_content_list = {
#   "C0C1" : {"Bypass" : 1, "IS_EDC" : False}, # Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
#   "C2C3" : {"Bypass" : 1, "IS_EDC" : False}
#    }
#else:
#    {
#        }
#
#FMIN_Tests = get_test_list_fmin(FMIN_Flow, FMIN_Corner, FMIN_FlowMatrix, FMIN_Subflow, FMIN_content_list)
#
#FMIN_Subflow = Flow(f"ARR_CORE_{sku}_FMINXCR @FMINXCR_SubFlow", FMIN_Tests)

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
   "C0C1" : {"Bypass" : 1, "IS_EDC" : False}, # Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
   "C2C3" : {"Bypass" : 1, "IS_EDC" : False}
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
   "C0C1" : {"Bypass" : 1, "IS_EDC" : False}, # Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
   "C2C3" : {"Bypass" : 1, "IS_EDC" : False}
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

begincpunom_vmintc_ssa_core_vnnaon_pmuc_tli = {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": False}
begcpunom_vmintc_ssa_core_vnnaon_pmuc = get_test_list_ssa_core_vnnaon_pmuc_f2_c0c1(begincpunom_flow, begincpunom_corner, begincpunom_vmintc_ssa_core_vnnaon_pmuc_tli)

begcpunom_vmintc_xsa_core_vccc_c0c1_nom_tli = {"Bypassport": 1, "Testmode": "Scoreboard"}
begcpunom_vmintc_xsa_core_vccc_c0c1_nom = get_test_list_xsa_core_vccc_c0c1_nom(begincpunom_flow, begincpunom_corner, begincpunom_vmintc_ssa_core_vnnaon_pmuc_tli)

begcpunom_vmintc_ssa_core_vnnaon_pmuc_f2_c2c3_tli = {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": False}
begcpunom_vmintc_ssa_core_vnnaon_pmuc_f2_c2c3 = get_test_list_ssa_core_vnnaon_pmuc_f2_c2c3(begincpunom_flow, begincpunom_corner, begcpunom_vmintc_ssa_core_vnnaon_pmuc_f2_c2c3_tli)

begcpunom_vmintc_xsa_core_vccc_c2c3_nom_tli = {"Bypassport": 1, "Testmode": "Scoreboard"}
begcpunom_vmintc_xsa_core_vccc_c2c3_nom = get_test_list_xsa_core_vccc_c2c3_nom(begincpunom_flow, begincpunom_corner, begcpunom_vmintc_xsa_core_vccc_c2c3_nom_tli)


#BEGINCPU SUBFLOW
BEGINCPUNOM = Flow(
    f'ARR_CORE_{sku}_BEGINCPUNOM',
    begcpunom_vmintc_ssa_core_vnnaon_pmuc + begcpunom_vmintc_xsa_core_vccc_c0c1_nom + begcpunom_vmintc_ssa_core_vnnaon_pmuc_f2_c2c3 + begcpunom_vmintc_xsa_core_vccc_c2c3_nom
    )               

#################################################################################
#							ENDCPUNOM SUBFLOW
#
#	-Need retention 
#################################################################################
endcpunom_flow = "ENDCPUNOM"
endcpunom_corner = "VCCC"

# Define the ENDCPU subflow

endcpunom_vmintc_ssa_core_vccc_c6s_retention_c0c1_tli = {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": False}
endcpunom_vmintc_ssa_core_vccc_c6s_retention_c0c1 = get_test_list_ssa_core_vccc_c6s_retention_c0c1(endcpunom_flow, endcpunom_corner, endcpunom_vmintc_ssa_core_vccc_c6s_retention_c0c1_tli)

endcpunom_vmintc_ssa_core_vccc_c6s_retention_c2c3_tli = {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": False}
endcpunom_vmintc_ssa_core_vccc_c6s_retention_c2c3 = get_test_list_ssa_core_vccc_c6s_retention_c2c3(endcpunom_flow, endcpunom_corner, endcpunom_vmintc_ssa_core_vccc_c6s_retention_c2c3_tli)


#ENDCPUNOM SUBFLOW
ENDCPUNOM = Flow(
    f'ARR_CORE_{sku}_ENDCPUNOM',
    endcpunom_vmintc_ssa_core_vccc_c6s_retention_c0c1 + endcpunom_vmintc_ssa_core_vccc_c6s_retention_c2c3
    )               

#################################################################################
#							ENDCPUMAX SUBFLOW
#
#	-Need retention 
#################################################################################
endcpumax_flow = "ENDCPUMAX"
endcpumax_corner = "VNNAON"

# Define the ENDCPUMAX subflow

endcpumax_ssa_core_vnnaon_pmuc_f1_c0c1_max_tli = {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": False}
endcpumax_ssa_core_vnnaon_pmuc_f1_c0c1_max = get_test_list_ssa_core_vnnaon_pmuc_f1_c0c1_max(endcpumax_flow, endcpumax_corner, endcpumax_ssa_core_vnnaon_pmuc_f1_c0c1_max_tli)

endcpumax_ssa_core_vnnaon_pmuc_f1_c2c3_max_tli = {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": False}
endcpumax_ssa_core_vnnaon_pmuc_f1_c2c3_max = get_test_list_ssa_core_vnnaon_pmuc_f1_c2c3_max(endcpumax_flow, endcpumax_corner, endcpumax_ssa_core_vnnaon_pmuc_f1_c2c3_max_tli)

#ENDCPUMAX SUBFLOW
ENDCPUMAX = Flow(
    f'ARR_CORE_{sku}_ENDCPUMAX',
    endcpumax_ssa_core_vnnaon_pmuc_f1_c0c1_max + endcpumax_ssa_core_vnnaon_pmuc_f1_c2c3_max
    )              

 

