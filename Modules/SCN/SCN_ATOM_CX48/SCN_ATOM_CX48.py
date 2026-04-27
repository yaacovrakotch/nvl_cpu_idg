#from turtle import pos
from pymtpl.por_methods import VminTC,DDGShmooTC, PrimeHvqkTestMethod, MbistVminTC, AuxiliaryTC, ScreenTC,PrimeVirtualFuseExportToSharedStorageTestMethod,PrimePatConfigTestMethod,PrimeSampleRateTestMethod,MbistRasterRepairTC,PrimeScanHRYSSNTestMethod,PrimeScanSPOFITestMethod, RunCallback, ApexTC, PrimeShmooTestMethod, PrimeApplyTestConditionTestMethod
from pymtpl.core import Flow, Fitem, pPass, pFail, Initialize, NativeMultiTrial, AUTO, MTLdefault, InitializeNVLClass, Import, TrialParamSpec, Spec, MConfig

########################################################################

# frequency decode for single static test
STATIC_FREQUENCY_CORNERS = {
    "F1" : "400",
    "F2" : "800",
    "F3" : "1100",
    "F4" : "1400",
    "F5" : "1600",
    "F6" : "2100"
    }
# Voltage targets for each module
voltage_targets = {
    "M0": "HC04_02_0P85_VCCATOM0",
    "M1": "HC03_02_0P85_VCCATOM1",
    "M2": "HC02_02_0P85_VCCATOM2",
    "M3": "HC01_02_0P85_VCCATOM3"
}
# initialmaskbit for each module
INITIALMASKBIT = {
    "M0": "1110",
    "M1": "1101",
    "M2": "1011",
    "M3": "0111"
}
N2P48_INITIALMASKBIT = {
    "M0": "10",
    "M1": "01",
}
# Define ATOM_MODULES based on MODULE #
MODULE = "SCN_ATOM_CX48"  # You can change this as needed
VOLTAGE_DOMAIN = "AT"

if MODULE == "SCN_ATOM_CX816":
    ATOM_MODULES = ["M0", "M1", "M2", "M3"]
elif MODULE == "SCN_ATOM_CX48":
    ATOM_MODULES = ["M0", "M1"]
else:
    ATOM_MODULES = []  # Default case if MODULE doesn't match any known value

########################################################################
# INITIALIZE LAYOUT
########################################################################

output = InitializeNVLClass(
    outfile = MODULE,
    module_name = MODULE,
    tosversion = "tos4",
    binrange = [(4120,4133), (4220, 4233), (4720, 4733)],
    ctrrangeforbins=(2778, 2888),
    #CH_ATOM_BR = (4120, 4133) , #4717-4733, do not use 4719, 4119, 4219(reset bin)
    #SA_ATOM_BR = (4220, 4233),
    #AS_ATOM_BR = (4720, 4733),
    basenumrange=(13333,13665),
    defaultthermalbin=[(97472778, 97472888), (97422778,97422888), (97412778,97412888), (97942778,97942888)], #9097HB17
    defaultresetbin=[(47192778, 47192888), (42192778,42192888), (41192778,41192888), (94192778,94192888)], #90HB1917/90HB1918
    defaultrm2bin = [(99472778, 99472888), (99422778, 99422888), (99412778, 99412888), (99942778, 99942888)],
    defaultrm1bin = [(98472778, 98472888), (98422778, 98422888), (98412778, 98412888), (98942778, 98942888)]
    #LTTCPORT4 = 9497
    #LTTCPORT5 = 9419
)
lttcbin= (9447, 9447)

########################################################################
# IMPORT REQUIRED FILES
########################################################################

# Add the necessary files to import in your mtpl
Import("SCN_ATOM_CX48_Specs.usrv")
Import("SCN_ATOM_CX48_Levels.tcg")
Import("SCN_ATOM_CX48_Timing.tcg")
#Import("VminTC.xml")
#Import("PrimeScanHRYTestMethod.xml")
#Import("ScanHRYOCC.xml")
#Import("PrimeHvqkTestMethod.xml")
#Import("RunCallback.xml")
#Import("PrimePatConfigTestMethod.xml")
#Import("DDGShmooTC.xml")
#Import("PrimeSampleRateTestMethod.xml")
#Import("PrimeScanSPOFITestMethod.xml")
#Import("SCN_ATOM_CX48_Timing.tcg")

#################################################################################################
# SCREENTC TESTS LAYOUT
######################################################################################################
    
def get_test_list_screentc(
    flow,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_screentc = []	
    sample_test_screentc = \
        ScreenTC(name=f"CTRL_X_SCREEN_K_{flow}_X_X_X_X_RESET_GSDS",
               ScreenTestSet = "",
               ScreenTestsFile = "",
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -41, goto="NEXT"),
               r1=pPass(goto="NEXT"),
               r2=pFail(setbin = -41, goto="NEXT")))
    test_listt_screentc.append(sample_test_screentc)
    
    return test_listt_screentc

#######################################################################################
# PATCONFIG TESTS LAYOUT
######################################################################################################
    
def get_test_list_patconfig(
    flow,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_patconfig = []	
    sample_test_patconfig = \
        PrimePatConfigTestMethod(name=f"CTRL_X_PATMOD_K_{flow}_X_X_X_X_RESET_FREQUENCY",
               ConfigurationFile = "",
               SetPoint = "",
               #SetPointsPlistMode = "Global",
               #SetPointsPreInstance = "",
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -41, goto="NEXT"),
               r1=pPass(goto="NEXT")))
    test_listt_patconfig.append(sample_test_patconfig)
    
    return test_listt_patconfig
       
################################################################################################## 
# SPOFI TESTS OCC LAYOUT
##################################################################################################
   
def get_test_list_stuckat_spofi_occ(
    flow,
    corner,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_stuckat_spofi_occ = []
    sample_test_stuckat_spofi_occ = \
        PrimeScanSPOFITestMethod(name=f"STUCKAT_ATOM_SPOFI_K_{flow}_X_X_NOM_OCC",
               Patlist = f'scn_arw_x_vccia_static_{flow.lower()}_hptp1600_4r4t_edt_stuckat_occ_classedc_list',
               TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48")'),
               LevelsTc = 'SCN_ATOM_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNATOM_OVERRIDE_nom',
               PerPatternFailCaptureCount = 1000,
               TotalFailCaptureCount = 5000,
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin=-42, goto="NEXT"),
               r1=pPass(ret=1),
               r2=pFail(setbin=-42, ret=0)))

    test_listt_stuckat_spofi_occ.append(sample_test_stuckat_spofi_occ)
    
    return test_listt_stuckat_spofi_occ

def get_test_list_atspeed_spofi_occ(
    flow,
    corner,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_atspeed_spofi_occ = []
    sample_test_atspeed_spofi_occ = \
        PrimeScanSPOFITestMethod(name=f"ATSPEED_ATOM_SPOFI_K_{flow}_X_X_NOM_OCC",
               Patlist = f'scn_arw_x_vccia_static_{flow.lower()}_hptp1600_4r4t_edt_stuckat_occ_classedc_list',
               TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48")'),
               LevelsTc = 'SCN_ATOM_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNATOM_OVERRIDE_nom',
               PerPatternFailCaptureCount = 1000,
               TotalFailCaptureCount = 5000,
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin=-47, ret=0),
               r1=pPass(ret=1),
               r2=pFail(setbin=-47, ret=0)))

    test_listt_atspeed_spofi_occ.append(sample_test_atspeed_spofi_occ)
    
    return test_listt_atspeed_spofi_occ

def get_test_list_chain_spofi_occ(
    flow,
    corner,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_chain_spofi_occ = []
    sample_test_chain_spofi_occ = \
        PrimeScanSPOFITestMethod(name=f"CHAIN_ATOM_SPOFI_K_{flow}_X_X_NOM_OCC",
               Patlist = f'scn_arw_x_vccia_chain_hptp1600_4r4t_edt_chain_occ_classedc_list',
               TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts800_tstprtclk400_tck50_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts800_tstprtclk400_tck50_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts800_tstprtclk400_tck50_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts800_tstprtclk400_tck50_SCNATOM48")'),
               LevelsTc = 'SCN_ATOM_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNATOM_OVERRIDE_nom',
               PerPatternFailCaptureCount = 1000,
               TotalFailCaptureCount = 5000,
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin=-41, goto=f"PROXY_ATOM_SPOFI_K_{flow}_X_X_NOM_OCC"),
               r1=pPass(ret=1),
               r2=pFail(setbin=-41, goto=f"PROXY_ATOM_SPOFI_K_{flow}_X_X_NOM_OCC")))

    test_listt_chain_spofi_occ.append(sample_test_chain_spofi_occ)
    
    return test_listt_chain_spofi_occ

############################################################################################
# SPOFI TESTS IO LAYOUT
############################################################################################
   
def get_test_list_stuckat_spofi(
    flow,
    corner,
    atom,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_stuckat_spofi = []
    sample_test_stuckat_spofi = \
        PrimeScanSPOFITestMethod(name=f"STUCKAT_ATOM_SPOFI_K_{flow}_X_X_NOM_{corner}_M{atom}",
               _comment=["NOCLEAN", "PATLIST_NOCLEAN : Due to needing this plist for PO shmoo", "TCG_NOCLEAN : Due to needing it"],
               Patlist = f'scn_arw_{flow.lower()}_hptp1600_4r4t_edt_stuckat_m{atom}_classhvm_list',
               LevelsTc = 'SCN_ATOM_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNATOM_OVERRIDE_nom',
               TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48")'),
               PerPatternFailCaptureCount = 100000,
               TotalFailCaptureCount = 100000,
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin=-42, ret=0),
               r1=pPass(ret=0),
               r2=pFail(setbin=-42, ret=0)))

    test_listt_stuckat_spofi.append(sample_test_stuckat_spofi)
    
    return test_listt_stuckat_spofi

def get_test_list_atspeed_spofi(
    flow,
    corner,
    atom,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_atspeed_spofi = []
    sample_test_atspeed_spofi = \
        PrimeScanSPOFITestMethod(name=f"ATSPEED_ATOM_SPOFI_K_{flow}_X_X_NOM_{corner}_M{atom}",
               Patlist = f'scn_arw_x_vccia_{corner.lower()}_{flow.lower()}_hptp1600_4r4t_edt_atspeed_m{atom}_classhvm_list',
               LevelsTc = 'SCN_ATOM_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNATOM_OVERRIDE_nom',
               TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48")'),
               PerPatternFailCaptureCount = 100000,
               TotalFailCaptureCount = 100000,
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin=-47, goto="NEXT"),
               r1=pPass(ret=0),
               r2=pFail(setbin=-47, goto="NEXT")))

    test_listt_atspeed_spofi.append(sample_test_atspeed_spofi)
    
    return test_listt_atspeed_spofi

def get_test_list_chain_spofi(
    flow,
    corner,
    atom,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_chain_spofi = []
    sample_test_chain_spofi = \
        PrimeScanSPOFITestMethod(name=f"CHAIN_ATOM_SPOFI_K_{flow}_X_X_NOM_{corner}_M{atom}",
               Patlist = f'scn_arw_chain_hptp1600_4r4t_edt_chain_m{atom}_classhvm_list',
               LevelsTc = 'SCN_ATOM_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNATOM_OVERRIDE_nom',
               TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts800_tstprtclk400_tck50_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts800_tstprtclk400_tck50_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts800_tstprtclk400_tck50_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts800_tstprtclk400_tck50_SCNATOM48")'),
               PerPatternFailCaptureCount = 100000,
               TotalFailCaptureCount = 100000,
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin=-41, ret=0),
               r1=pPass(ret=0),
               r2=pFail(setbin=-41, ret=0)))

    test_listt_chain_spofi.append(sample_test_chain_spofi)
    
    return test_listt_chain_spofi

################################################################################################## 
# SHMOO TESTS OCC LAYOUT
##################################################################################################

def get_shmoo_test_occstuckat(flow, corner, testinput):
    """
    Returns a DDGShmooTC test instance for stuck-at shmoo testing for a given ATOM module.
    """
    return DDGShmooTC(
        name=f"STUCKAT_ATOM_SHMOO_E_{flow}_X_X_NOM_X_OCC",
        _comment=["NOCLEAN", "PATLIST_NOCLEAN : Due to needing this plist for PO shmoo", "TCG_NOCLEAN : Due to needing it"],
        Patlist= f'scn_arw_{flow.lower()}_hptp1600_12r4t_edt_stuckat_occ_classhvm_list',
        LevelsTc = 'SCN_ATOM_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNATOM_OVERRIDE_nom',
        TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48")'),
        SetPointsPlistParamName="Patlist",
        SetPointsPlistMode="Local",
        PrePointExecMode= "Never",
        SetPointsPreInstance= Spec(f'"MCdrv:atomfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.AT_F1_FREQ+")+'"GHz,MCdrv:ringfreq_0:2.4GHz,MCAscn:ratio_modify_OCC:R4_OCC"'),
        VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions ATOM --fivrcondition NOM"'),
        #ExecutionMode="AllPin",
        PrintFormat='ShmooHub',
        XAxisType="SpecSetVariable",
        XAxisDatalogPrefix = 'Nano',
        XAxisParam="all_mts",
        XAxisParamType="UserDefined",
        XAxisRange= "1100e6:100e6:5",
        YAxisType="FIVR",
        YAxisParam= 'ATOM1,ATOM0',
        YAxisParamType="UserDefined",
        YAxisDatalogPrefix = 'Base',
        YAxisRange= "1.2:-0.1:10",
        LogLevel="Enabled",
        PowerDownBetweenPoints="DISABLED",
        #PlotMode= "NORMAL",
        InstanceSummaryMode="Disabled",
        TelemetryLevel="None",
        ApplyEndSequence="DISABLED",
        BypassPort=testinput.get("Bypassport", -1),
        _fitem=Fitem(
            'SAME',
            edc=testinput.get("ISEDC"),
            r0=pFail(goto = "NEXT"),
            r1=pPass(goto = "NEXT"),
            r2=pFail(goto = "NEXT"))
    )

def get_test_list_occchain(flow, corner, testinput, atom_module):
    """
    Returns a DDGShmooTC test instance for stuck-at shmoo testing for a given ATOM module.
    """
    return DDGShmooTC(
        name=f"CHAIN_ATOM_SHMOO_E_{flow}_X_X_NOM_X_OCC",
        Patlist=f'scn_arw_chain_hptp1600_4r4t_edt_chain_m{atom}_classhvm_list',
        LevelsTc = 'SCN_ATOM_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNATOM_OVERRIDE_nom',
        TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts800_tstprtclk400_tck50_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts800_tstprtclk400_tck50_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts800_tstprtclk400_tck50_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts800_tstprtclk400_tck50_SCNATOM48")'),
        SetPointsPlistParamName="Patlist",
        SetPointsPlistMode="Local",
        PrePointExecMode= "Never",
        SetPointsPreInstance=Spec(f'"MCdrv:atomfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.AT_F1_FREQ+")+'"GHz,MCdrv:ringfreq_0:2.4GHz"'),
        VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions ATOM --fivrcondition NOM"'),
        #ExecutionMode="AllPin",
        PrintFormat='ShmooHub',
        XAxisType="SpecSetVariable",
        XAxisDatalogPrefix = 'Nano',
        XAxisParam="all_mts",
        XAxisParamType="UserDefined",
        XAxisRange="600e6:100e6:5",
        YAxisType="FIVR",
        YAxisParam='ATOM1,ATOM0',
        YAxisParamType="UserDefined",
        YAxisDatalogPrefix = 'Base',
        YAxisRange="1.2:-0.1:10",
        LogLevel="Enabled",
        PowerDownBetweenPoints="DISABLED",
        #PlotMode= "NORMAL",
        InstanceSummaryMode="Disabled",
        TelemetryLevel="None",
        ApplyEndSequence="DISABLED",
        BypassPort=testinput.get("Bypassport", -1),
        _fitem=Fitem(
            'SAME',
            edc=testinput.get("ISEDC"),
            r0=pFail(goto = "NEXT"),
            r1=pPass(goto = "NEXT"),
            r2=pFail(goto = "NEXT"))
    )

def get_shmoo_test_f1f4occatspeed(flow, corner, testinput, FlowMatrix):
    """
    Returns a DDGShmooTC test instance for stuck-at shmoo testing for a given ATOM module.
    """
    return DDGShmooTC(
        name=f"ATSPEED_ATOM_SHMOO_E_BEGINCPU_X_X_NOM_X_{flow}_OCC",
        _comment=["NOCLEAN", "PATLIST_NOCLEAN : Due to needing this plist for PO shmoo", "TCG_NOCLEAN : Due to needing it"],
        Patlist= 'scn_arw_vmaxf5xat_hptp1600_12r4t_edt_atspeed_occ_classhvm_list',
        LevelsTc = 'SCN_ATOM_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNATOM_OVERRIDE_nom',
        TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts800_tstprtclk400_tck50_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts800_tstprtclk400_tck50_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts800_tstprtclk400_tck50_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts800_tstprtclk400_tck50_SCNATOM48")') if "FMINXAT" in flow else Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48")'),
        SetPointsPlistParamName="Patlist",
        SetPointsPlistMode="Local",
        #PrePointExecMode= "Never",
        SetPointsPreInstance= testinput.get("setpointpre", Spec(f'"MCdrv:atomfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.{FlowMatrix}+")+'"GHz,MCdrv:ringfreq_0:2.4GHz,MCAscn:ratio_modify_OCC:R8_OCC"')),
        VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions ATOM --fivrcondition NOM"'),
        #ExecutionMode="AllPin",
        PrintFormat='ShmooHub',
        XAxisType="SpecSetVariable",
        XAxisDatalogPrefix = 'Base',
        XAxisParam="all_mts" if "FMINXAT" in flow else "all_mts",
        XAxisParamType="UserDefined",
        XAxisRange="600e6:100e6:5" if "FMINXAT" in flow else "1100e6:100e6:5",
        YAxisType="FIVR",
        YAxisParam='ATOM1,ATOM0',
        YAxisParamType="UserDefined",
        YAxisDatalogPrefix = 'Base',
        YAxisRange="1.2:-0.1:10",
        LogLevel="Enabled",
        PowerDownBetweenPoints="DISABLED",
        #PlotMode= "NORMAL",
        #InstanceSummaryMode="Disabled",
        #TelemetryLevel="None",
        ApplyEndSequence="DISABLED",
        BypassPort=testinput.get("Bypassport", -1),
        _fitem=Fitem(
            'SAME',
            edc=testinput.get("ISEDC"),
            r0=pFail(goto = "NEXT"),
            r1=pPass(goto = "NEXT"),
            r2=pFail(goto = "NEXT"))
    )

def get_shmoo_test_f5occatspeed(flow, corner, testinput, FlowMatrix):
    """
    Returns a DDGShmooTC test instance for stuck-at shmoo testing for a given ATOM module.
    """
    return DDGShmooTC(
        name=f"ATSPEED_ATOM_SHMOO_E_BEGINCPU_X_X_NOM_X_{flow}_OCC",
        _comment=["NOCLEAN", "PATLIST_NOCLEAN : Due to needing this plist for PO shmoo", "TCG_NOCLEAN : Due to needing it"],
        Patlist = 'scn_arw_vmaxf5xat_hptp1600_12r4t_edt_atspeed_occ_classhvm_list',
        LevelsTc = 'SCN_ATOM_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNATOM_OVERRIDE_nom',
        TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48")'),
        SetPointsPlistParamName="Patlist",
        SetPointsPlistMode="Local",
        #PrePointExecMode= "Never",
        SetPointsPreInstance=Spec(f'"MCdrv:atomfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.{FlowMatrix}+")+'"GHz,MCdrv:ringfreq_0:2.4GHz,MCAscn:ratio_modify_OCC:R8_OCC"'),
        VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions ATOM --fivrcondition NOM"'),
        #ExecutionMode="AllPin",
        PrintFormat='ShmooHub',
        XAxisType="SpecSetVariable",
        XAxisDatalogPrefix = 'Base',
        XAxisParam="all_mts",
        XAxisParamType="UserDefined",
        XAxisRange="1100e6:100e6:5",
        YAxisType="FIVR",
        YAxisParam='ATOM1,ATOM0',
        YAxisParamType="UserDefined",
        YAxisDatalogPrefix = 'Base',
        YAxisRange="1.2:-0.1:10",
        LogLevel="Enabled",
        PowerDownBetweenPoints="DISABLED",
        #PlotMode= "NORMAL",
        #InstanceSummaryMode="Disabled",
        #TelemetryLevel="None",
        ApplyEndSequence="DISABLED",
        BypassPort=testinput.get("Bypassport", -1),
        _fitem=Fitem(
            'SAME',
            edc=testinput.get("ISEDC"),
            r0=pFail(goto = "NEXT"),
            r1=pPass(goto = "NEXT"),
            r2=pFail(goto = "NEXT"))
    )

def get_shmoo_test_vmaxoccatspeed(flow, corner, testinput, FlowMatrix):
    """
    Returns a DDGShmooTC test instance for stuck-at shmoo testing for a given ATOM module.
    """
    return DDGShmooTC(
        name=f"ATSPEED_ATOM_SHMOO_E_ENDCPUMAX_X_X_NOM_X_{flow}_OCC",
        Patlist = 'scn_arw_vmaxf5xat_hptp1600_12r4t_edt_atspeed_occ_classhvm_list',
        LevelsTc = 'SCN_ATOM_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNATOM_OVERRIDE_nom',
        TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48")'),
        SetPointsPlistParamName="Patlist",
        SetPointsPlistMode="Local",
        #PrePointExecMode= "Never",
        SetPointsPreInstance=Spec(f'"MCdrv:atomfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.{FlowMatrix}+")+'"GHz,MCdrv:ringfreq_0:2.4GHz,MCAscn:ratio_modify_OCC:R8_OCC"'),
        VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions ATOM --fivrcondition NOM"'),
        #ExecutionMode="AllPin",
        PrintFormat='ShmooHub',
        XAxisType="SpecSetVariable",
        XAxisDatalogPrefix = 'Base',
        XAxisParam="all_mts",
        XAxisParamType="UserDefined",
        XAxisRange="1100e6:100e6:5",
        YAxisType="FIVR",
        YAxisParam='ATOM1,ATOM0',
        YAxisParamType="UserDefined",
        YAxisDatalogPrefix = 'Base',
        YAxisRange="1.2:-0.1:10",
        LogLevel="Enabled",
        PowerDownBetweenPoints="DISABLED",
        #PlotMode= "NORMAL",
        #InstanceSummaryMode="Disabled",
        #TelemetryLevel="None",
        ApplyEndSequence="DISABLED",
        BypassPort=testinput.get("Bypassport", -1),
        _fitem=Fitem(
            'SAME',
            edc=testinput.get("ISEDC"),
            r0=pFail(goto = "NEXT"),
            r1=pPass(goto = "NEXT"),
            r2=pFail(goto = "NEXT"))
    )

############################################################################################
# SHMOO TESTS IO LAYOUT
######################################################################################################
def get_shmoo_test_iostuckat(flow, corner, atom, testinput, atom_module):
    """
    Returns a DDGShmooTC test instance for stuck-at shmoo testing for a given ATOM module.
    """
    return DDGShmooTC(
        name=f"STUCKAT_ATOM_SHMOO_E_{flow}_X_X_NOM_X_M{atom}",
        Patlist=f'scn_arw_{flow.lower()}_hptp1600_4r4t_edt_stuckat_m{atom}_classhvm_list',
        LevelsTc = 'SCN_ATOM_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNATOM_OVERRIDE_nom',
        TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48")'),
        SetPointsPlistParamName="Patlist",
        SetPointsPlistMode="Local",
        PrePointExecMode= "Never",
        SetPointsPreInstance=Spec(f'"MCdrv:atomfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.AT_F1_FREQ+")+'"GHz,MCdrv:ringfreq_0:2.4GHz"'),
        VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions ATOM --fivrcondition NOM"'),
        #ExecutionMode="AllPin",
        PrintFormat='ShmooHub',
        XAxisType="SpecSetVariable",
        XAxisDatalogPrefix = 'Nano',
        XAxisParam="all_mts",
        XAxisParamType="UserDefined",
        XAxisRange="1100e6:100e6:5",
        YAxisType="FIVR",
        YAxisParam=f'ATOM{atom}',
        YAxisParamType="UserDefined",
        YAxisDatalogPrefix = 'Base',
        YAxisRange="1.2:-0.1:10",
        LogLevel="Enabled",
        PowerDownBetweenPoints="DISABLED",
        #PlotMode= "NORMAL",
        InstanceSummaryMode="Disabled",
        TelemetryLevel="None",
        ApplyEndSequence="DISABLED",
        BypassPort=testinput.get("Bypassport", -1),
        _fitem=Fitem(
            'SAME',
            edc=testinput.get("ISEDC"),
            r0=pFail(goto = "NEXT"),
            r1=pPass(goto = "NEXT"),
            r2=pFail(goto = "NEXT"))
    )

def get_test_list_iochain(flow, corner, atom, testinput, atom_module):
    """
    Returns a DDGShmooTC test instance for stuck-at shmoo testing for a given ATOM module.
    """
    return DDGShmooTC(
        name=f"CHAIN_ATOM_SHMOO_E_{flow}_X_X_NOM_X_M{atom}",
        _comment=["NOCLEAN", "PATLIST_NOCLEAN : Due to needing this plist for PO shmoo", "TCG_NOCLEAN : Due to needing it"],
        Patlist = f'scn_arw_chain_hptp1600_4r4t_edt_chain_m{atom}_classhvm_list',
        LevelsTc = 'SCN_ATOM_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNATOM_OVERRIDE_nom',
        TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts800_tstprtclk400_tck50_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts800_tstprtclk400_tck50_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts800_tstprtclk400_tck50_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts800_tstprtclk400_tck50_SCNATOM48")'),
        SetPointsPlistParamName="Patlist",
        SetPointsPlistMode="Local",
        PrePointExecMode= "Never",
        SetPointsPreInstance=Spec(f'"MCdrv:atomfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.AT_F1_FREQ+")+'"GHz,MCdrv:ringfreq_0:2.4GHz,MCAscn:ratio_modify_chain:R8C"'),
        VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions ATOM --fivrcondition NOM"'),
        #ExecutionMode="AllPin",
        PrintFormat='ShmooHub',
        XAxisType="SpecSetVariable",
        XAxisDatalogPrefix = 'Nano',
        XAxisParam="all_mts",
        XAxisParamType="UserDefined",
        XAxisRange= "600e6:100e6:5",
        YAxisType="FIVR",
        YAxisParam=f'ATOM{atom}',
        YAxisParamType="UserDefined",
        YAxisDatalogPrefix = 'Base',
        YAxisRange="1.2:-0.1:10",
        LogLevel="Enabled",
        PowerDownBetweenPoints="DISABLED",
        #PlotMode= "NORMAL",
        InstanceSummaryMode="Disabled",
        TelemetryLevel="None",
        ApplyEndSequence="DISABLED",
        BypassPort=testinput.get("Bypassport", -1),
        _fitem=Fitem(
            'SAME',
            edc=testinput.get("ISEDC"),
            r0=pFail(goto = "NEXT"),
            r1=pPass(goto = "NEXT"),
            r2=pFail(goto = "NEXT"))
    )

def get_shmoo_test_f1f4ioatspeed(flow, corner, atom, testinput, FlowMatrix):
    """
    Returns a DDGShmooTC test instance for stuck-at shmoo testing for a given ATOM module.
    """
    return DDGShmooTC(
        name=f"ATSPEED_ATOM_SHMOO_E_X_X_X_NOM_X_X_{flow}_M{atom}",
        Patlist= f'scn_arw_fminxat_hptp1600_4r4t_edt_atspeed_m{atom}_classhvm_list' if "FMINXAT" in flow else f'scn_arw_{flow.lower()}_hptp1600_4r4t_edt_atspeed_m{atom}_classhvm_list_{corner.lower()}_master',
        LevelsTc = 'SCN_ATOM_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNATOM_OVERRIDE_nom',
        TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts800_tstprtclk400_tck50_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts800_tstprtclk400_tck50_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts800_tstprtclk400_tck50_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts800_tstprtclk400_tck50_SCNATOM48")') if "FMINXAT" in flow else Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48")'),
        SetPointsPlistParamName="Patlist",
        SetPointsPlistMode="Local",
        #PrePointExecMode= "Never",
        SetPointsPreInstance= testinput.get("setpointpre", Spec(f'"MCdrv:atomfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.{FlowMatrix}+")+'"GHz,MCdrv:ringfreq_0:2.4GHz"')),
        VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions ATOM --fivrcondition NOM"'),
        #ExecutionMode="AllPin",
        PrintFormat='ShmooHub',
        XAxisType="SpecSetVariable",
        XAxisDatalogPrefix = 'Base',
        XAxisParam="all_mts" if "FMINXAT" in flow else "all_mts",
        XAxisParamType="UserDefined",
        XAxisRange="600e6:100e6:5" if "FMINXAT" in flow else "1100e6:100e6:5",
        YAxisType="FIVR",
        YAxisParam=f'ATOM{atom}',
        YAxisParamType="UserDefined",
        YAxisDatalogPrefix = 'Base',
        YAxisRange="1.2:-0.1:10",
        LogLevel="Enabled",
        PowerDownBetweenPoints="DISABLED",
        #PlotMode= "NORMAL",
        #InstanceSummaryMode="Disabled",
        #TelemetryLevel="None",
        ApplyEndSequence="DISABLED",
        BypassPort=testinput.get("Bypassport", -1),
        _fitem=Fitem(
            'SAME',
            edc=testinput.get("ISEDC"),
            r0=pFail(goto = "NEXT"),
            r1=pPass(goto = "NEXT"),
            r2=pFail(goto = "NEXT"))
    )

def get_shmoo_test_f5ioatspeed(flow, corner, atom, testinput, FlowMatrix):
    """
    Returns a DDGShmooTC test instance for stuck-at shmoo testing for a given ATOM module.
    """
    return DDGShmooTC(
        name=f"ATSPEED_ATOM_SHMOO_E_X_X_X_NOM_X_X_{flow}_M{atom}",
        Patlist= f'scn_arw_f5xat_hptp1600_4r4t_edt_atspeed_m{atom}_classhvm_list_f5_master',
        LevelsTc = 'SCN_ATOM_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNATOM_OVERRIDE_nom',
        TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48")'),
        SetPointsPlistParamName="Patlist",
        SetPointsPlistMode="Local",
        #PrePointExecMode= "Never",
        SetPointsPreInstance=Spec(f'"MCdrv:atomfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.{FlowMatrix}+")+'"GHz,MCdrv:ringfreq_0:2.4GHz"'),
        VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions ATOM --fivrcondition NOM"'),
        #ExecutionMode="AllPin",
        PrintFormat='ShmooHub',
        XAxisType="SpecSetVariable",
        XAxisDatalogPrefix = 'Base',
        XAxisParam="all_mts",
        XAxisParamType="UserDefined",
        XAxisRange="1100e6:100e6:5",
        YAxisType="FIVR",
        YAxisParam=f'ATOM{atom}',
        YAxisParamType="UserDefined",
        YAxisDatalogPrefix = 'Base',
        YAxisRange="1.2:-0.1:10",
        LogLevel="Enabled",
        PowerDownBetweenPoints="DISABLED",
        #PlotMode= "NORMAL",
        #InstanceSummaryMode="Disabled",
        #TelemetryLevel="None",
        ApplyEndSequence="DISABLED",
        BypassPort=testinput.get("Bypassport", -1),
        _fitem=Fitem(
            'SAME',
            edc=testinput.get("ISEDC"),
            r0=pFail(goto = "NEXT"),
            r1=pPass(goto = "NEXT"),
            r2=pFail(goto = "NEXT"))
    )

def get_test_list_chain_shmoodata_margincheck(
    flow, 
    corner, 
    testtype, 
    testinput 
    ):
    
    # Create an empty list that will contain the final list of the test
    test_listt_chain_shmoo_margincheck = []
    sample_test_chain_shmoo_margincheck = PrimeShmooTestMethod(name = f"CHAIN_ATOM_SHMOO_E_{flow}_X_AT_NOM_X_{corner}_{testtype}_IOSHMOODATA",
                Patlist = 'scn_arw_chain_hptp1600_4r4t_edt_chain_m0_classhvm_list',
                LevelsTc = 'SCN_ATOM_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNATOM_OVERRIDE_nom',
                TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts800_tstprtclk400_tck50_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts800_tstprtclk400_tck50_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts800_tstprtclk400_tck50_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts800_tstprtclk400_tck50_SCNATOM48")'),
                #ApplyEndSequence = 'DISABLED',
                #ExecutionMode = 'Allpin',
                #SetPointsPlistParamName = "Patlist",
                #SetPointsPreInstance = Spec(f'"MCdrv:corefreq:"' +Spec(f"+__shared__::FlowMatrixSingular.CR_{corner}_FREQ+")+'"GHz"'),
                #SetPointsPlistMode = 'Local',
                #VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions CORE --fivrcondition NOM_CCF_CORE"'),
                #PrintFormat = "ShmooHub",
                #PowerDownBetweenPoints = 'DISABLED',
                #PlotMode = 'Normal',
                #XAxisType = "SpecSetVariable",
                XAxisDatalogPrefix = 'Base',
                XAxisParam = testinput.get("xaxisparam", ""),
                XAxisParamType = 'TimingTestCondition',
                XAxisRange = testinput.get("xaxisrange", ""),
                #YAxisType = 'FIVR',
                #YAxisDatalogPrefix = 'Base',
                #YAxisParam = f'CORE{dcm}',
                #YAxisParamType = "UserDefined",
                #YAxisRange = '1.2:-0.1:10',
                #LogLevel = 'Enabled',
                BypassPort = testinput.get("Bypassport", -1),
                _fitem=Fitem('SAME',
                edc=testinput.get("ISEDC"),
                r0=pFail(goto = "NEXT"),
                r1=pPass(goto = "NEXT"),
                r2=pPass(goto = "NEXT")))
               
    test_listt_chain_shmoo_margincheck.append(sample_test_chain_shmoo_margincheck)
    
    return test_listt_chain_shmoo_margincheck
    
######################################################################################################
# INIT - DIERECOVERY & PATMOD LAYOUT
######################################################################################################
def get_test_globalinit_patmod(
    flow,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_initconfig = []	
    sample_test_initconfig = \
        PrimePatConfigTestMethod(name=f"CTRL_X_PATMOD_K_{flow}_X_X_X_X_GLOBAL_INIT",
               ConfigurationFile = "./InputFiles/NVL_SCN_ATOM_INIT.PatConfigSetPoints.json",
               SetPoint = "SCN_ATOM_INIT_DISABLE_LLCPWRMUX",
               BypassPort = testinput.get("Bypassport", -1),
               #Loglevel= "Disabled",
               InstanceSummaryMode= "Disabled",
               TelemetryLevel= "None", 
               #SetPointsPlistMode= "Global",
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -41, goto="NEXT"),
               r1=pPass(goto="NEXT")))
    test_listt_initconfig.append(sample_test_initconfig)
    
    return test_listt_initconfig
    
def get_test_pinmap_parse(
    flow,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_callback = []	
    sample_test_callback = \
        RunCallback(name=f"CTRL_X_UF_E_{flow}_X_X_X_X_PINMAP_SCN_PRIME_DIERECOVERY",
               Callback = "LoadPinMapFile",
               Parameters = "--decoder AnyFailSingleSliceDecoder --file ./Modules/SCN/SCN_ATOM_CX48/InputFiles/N2P48_DieRecoveryPinMaps_IO_NVL_SCNATOM.json",
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -41, goto="NEXT"),
               r1=pPass(goto="NEXT")))
    test_listt_callback.append(sample_test_callback)
    
    return test_listt_callback 


def get_test_pinmap_parse_occ(
    flow,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_callback = []	
    sample_test_callback = \
        RunCallback(name=f"CTRL_X_UF_E_{flow}_X_X_X_X_PINMAP_SCN_PRIME_DIERECOVERY_OCC",
               Callback = "LoadPinMapFile",
               Parameters = "--decoder FailDataDecoder --file ./Modules/SCN/SCN_ATOM_CX48/InputFiles/N2P48_DieRecoveryPinMaps_OCC_NVL_SCANATOM.json",
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -41, goto="NEXT"),
               r1=pPass(goto="NEXT")))
    test_listt_callback.append(sample_test_callback)
    
    return test_listt_callback 

def get_test_apex_parse(
    flow,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_apex_callback = []	
    sample_test_apex_callback = \
        RunCallback(name=f"CTRL_X_UF_E_{flow}_X_X_X_X_SCN_PRIME_APEX",
               Callback = "ReadFrequencyPatConfigFile",
               Parameters = Spec('GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "./Modules/SCN/SCN_ATOM_CX48/InputFiles/N2P48_ApexTC_Input_Config.json"'),
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -41, goto="NEXT"),
               r1=pPass(goto="NEXT")))
    test_listt_apex_callback.append(sample_test_apex_callback)
    
    return test_listt_apex_callback 

########################################################################
# BEGIN OCC TESTS LAYOUT
########################################################################

def get_test_list_stuckat_occ(
    flow,
    corner,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_stuckat_occ = []	
    sample_test_stuckat_occ = \
        VminTC(name=f"STUCKAT_ATOM_SB_K_{flow}_X_AT_NOM_X_F1_OCC", 
               Patlist = f'scn_arw_{flow.lower()}_hptp1600_12r4t_edt_stuckat_occ_classhvm_list',
               LevelsTc = 'SCN_ATOM_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNATOM_OVERRIDE_nom',
               TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48")'),
               StartVoltages = Spec("SCN_ATOM_CX48_Specs.ATPG_StartVoltage"),
               EndVoltageLimits = Spec("SCN_ATOM_CX48_Specs.ATPG_EndVoltage"),
               VoltageTargets = testinput.get("Voltagetarget", "ATOM1,ATOM0"),
               ExecutionMode = 'SearchWithScoreboard',
               TestMode = testinput.get("Testmode", ""),
               VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions "' + f' + DROPOUT.AT_F1'),
               BaseNumbers = AUTO,
               StepSize = Spec("toDouble(0.01)"),
               FeatureSwitchSettings = 'fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters',
               LogLevel = "Disabled",
               SetPointsPlistMode = "Local",
               FivrCondition = 'NOM',
               ForwardingMode = 'InputOutput',
               PatternNameCounterIndexes = '1,2,3,4,5,6,7',
               #FailCaptureCount=72000,
               PinMap = 'NVL_SCN_ATOM',
               RecoveryMode = 'RecoveryPort', #offrec RecoveryMode = 'RecoveryPort',
               RecoveryOptions = Spec(f'__shared__::Recovery_Single.F1F4_recovery_opt_AT'),
               RecoveryTrackingIncoming = 'ACRM1,ACRM0',
               RecoveryTrackingOutgoing = 'ACRM1,ACRM0',
               #ScoreboardBaseNumber = '',
               ScoreboardEdgeTicks = Spec("toInteger(__shared__::Specs.VMX_EDGE_TICK)"),
               #ScoreboardPerPatternFails = 72,
               #ScoreboardMaxFails = '',
               MaxFailsNum = Spec("toInteger(__shared__::Specs.VMX_MAX_FAILS)"),
               SetPointsPlistParamName = 'Patlist',
               SetPointsPreInstance = Spec(f'SCN_ATOM_CX48_Specs.N2P48_PreInst_F1'),
               SetPointsPostInstance= Spec(f'PSPOST.AT_F1'),
               PreInstance = '',
               PostInstance = '',
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -42, goto="NEXT"),
               r1=pPass(ret=1),
               r2=pFail(setbin = -42, goto="NEXT"),
               r3=pPass(ret=1),
               r4=pFail(setbin = -42, goto="NEXT"),
               r5=pFail(setbin = -42, goto="NEXT")))
    test_listt_stuckat_occ.append(sample_test_stuckat_occ)
    
    return test_listt_stuckat_occ
 

########################################################################
# BEGIN IO LAYOUT
########################################################################
def get_test_list_stuckat(
    flow,
    corner,
    atom,
    testinput,
    flowmatrix
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_stuckat = []	
    sample_test_stuckat = \
        VminTC(name=f"STUCKAT_ATOM_SB_K_{flow}_X_AT_NOM_X_F1_M{atom}",
               Patlist = f'scn_arw_{flow.lower()}_hptp1600_4r4t_edt_stuckat_m{atom}_classhvm_list',
               LevelsTc = 'SCN_ATOM_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNATOM_OVERRIDE_nom',
               TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48")'),
               StartVoltages = Spec("SCN_ATOM_CX48_Specs.ATPG_StartVoltage"),
               EndVoltageLimits = Spec("SCN_ATOM_CX48_Specs.ATPG_EndVoltage"),
               VoltageTargets = f'ATOM{atom}', #testinput.get("Voltagetarget", "ATOM1,ATOM0"),
               ExecutionMode = 'SearchWithScoreboard',
               TestMode = testinput.get("Testmode", ""),
               VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions "' + f' + DROPOUT.AT_F1'),
               BaseNumbers = AUTO,
               StepSize = 0.01,
               FeatureSwitchSettings = 'fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters',
               LogLevel = "Disabled",
               SetPointsPlistMode = "Local",
               FivrCondition = 'NOM',
               ForwardingMode = 'InputOutput',
               InitialMaskBits = '0', #testinput.get("initialmaskbit", ""),
               PatternNameCounterIndexes = '1,2,3,4,5,6,7',
               #FailCaptureCount= 72000,
               PinMap = f'ATOM{atom}_SCAN',
               RecoveryMode = 'RecoveryPort', #offrec RecoveryMode = 'RecoveryPort',
               RecoveryOptions = Spec(f'__shared__::Recovery_Single.F1F4_recovery_opt_AT'),
               RecoveryTrackingIncoming = f'ACRM{atom}',
               RecoveryTrackingOutgoing = f'ACRM{atom}',
               #ScoreboardBaseNumber = '',
               ScoreboardEdgeTicks = Spec("toInteger(__shared__::Specs.VMX_EDGE_TICK)"),
               #ScoreboardPerPatternFails = 72,
               #ScoreboardMaxFails = '',
               MaxFailsNum = Spec("toInteger(__shared__::Specs.VMX_MAX_FAILS)"),
               SetPointsPlistParamName = 'Patlist',
               SetPointsPreInstance=Spec(f'PSPRE.AT_F1+' f'","+' f'"MCdrv:atomfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.AT_F1_FREQ+")+'"GHz"'),
               SetPointsPostInstance= Spec(f'PSPOST.AT_F1'),
               PreInstance = '',
               PostInstance = '',
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -42, goto="NEXT"),
               r1=pPass(ret=1),
               r2=pFail(setbin = -42, goto="NEXT"),
               r3=pPass(ret=1),
               r4=pFail(setbin = -42, goto="NEXT"),
               r5=pFail(setbin = -42, goto="NEXT")))
    test_listt_stuckat.append(sample_test_stuckat)
    
    return test_listt_stuckat


def get_test_list_chain(
    flow,
    corner,
    atom,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_chain = []	
    sample_test_chain = \
        VminTC(name=f"CHAIN_ATOM_SB_K_{flow}_X_AT_NOM_X_F1_M{atom}",
               Patlist = f'scn_arw_chain_hptp1600_4r4t_edt_chain_m{atom}_classhvm_list',
               LevelsTc = 'SCN_ATOM_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNATOM_OVERRIDE_nom',
               TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts800_tstprtclk400_tck50_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts800_tstprtclk400_tck50_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts800_tstprtclk400_tck50_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts800_tstprtclk400_tck50_SCNATOM48")'),
               EndVoltageLimits = Spec("SCN_ATOM_CX48_Specs.ATPG_EndVoltage"), 
               ExecutionMode = 'SearchWithScoreboard',
               FailCaptureCount = Spec("toInteger(999)"),
               FeatureSwitchSettings = 'fivr_mode_on,recovery_update_always,disable_masked_targets,print_per_target_increments,print_scoreboard_counters',
               LogLevel = "Disabled",
               SetPointsPlistMode = "Local",
               FivrCondition = 'NOM',
               ForwardingMode = 'InputOutput',
               InitialMaskBits = '0', #testinput.get("initialmaskbit", ""),
               MaskPins = '',
               PinMap = f'ATOM{atom}_SCAN', #'ATOM3_SCAN,ATOM2_SCAN,ATOM1_SCAN,ATOM0_SCAN',
               RecoveryMode =  'NoRecovery', 
               RecoveryOptions = Spec(f'__shared__::Recovery_Single.F1F4_recovery_opt_AT'), 
               RecoveryTrackingIncoming = f'ACRM{atom}',
               RecoveryTrackingOutgoing = f'ACRM{atom}',
               PatternNameCounterIndexes = '1,2,3,4,5,6,7',
               PreInstance = '',
               PostInstance = '',
               BaseNumbers = AUTO,
               ScoreboardEdgeTicks = Spec("toInteger(__shared__::Specs.VMX_EDGE_TICK)"),
               MaxFailsNum = Spec("toInteger(__shared__::Specs.VMX_MAX_FAILS)"),
               SetPointsPlistParamName = 'Patlist',
               SetPointsPreInstance= Spec(f'SCN_ATOM_CX48_Specs.N2P48_PreInst_F1_chain_mts800'),
               SetPointsPostInstance = '',
               StartVoltages = Spec("SCN_ATOM_CX48_Specs.ATPG_StartVoltage"),
               StepSize = 0.01,
               TestMode = testinput.get("Testmode", ""),
               VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions "' + f' + DROPOUT.AT_F1'),
               VoltageTargets = f'ATOM{atom}', #testinput.get("Voltagetarget", "ATOM1,ATOM0"),
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -41, goto="NEXT"),
               r1=pPass(ret=0),
               r2=pFail(setbin = -41, goto="NEXT"),
               r3=pPass(ret=0),
               r4=pFail(setbin = -41, goto="NEXT"),
               r5=pFail(setbin = -41, goto="NEXT")))
    test_listt_chain.append(sample_test_chain)
    
    return test_listt_chain

########################################################################
# F1-F4, MTT OCC vmin search/check test LAYOUT
########################################################################

def get_test_list_atspeed_occ_f1f4_mtt (
    testtype,
    flow, 
    corner, 
    testinput,
    FlowMatrix
    ):
           
    # decode MTT test name
    test_listt_atspeed_occ_f1f4_mtt = []  
    # Get the frequency value from FlowMatrixRule
    frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]
    
    sample_test_atspeed_occ_f1f4_mtt = \
    NativeMultiTrial(name = f"ATSPEED_ATOM_{testtype}_K_{flow.upper()}_X_AT_{corner.upper()}_X_FREQ_OCC",
                exitaction = "Continue",
                _comment = f"KILL ATSPEED {flow.upper()}",
                trialvar = "CPU_TRIALS::FlowDomain.ATOM",
                template = VminTC(name = f'"ATSPEED_ATOM_{testtype}_K_{flow.upper()}_X_AT_{corner.upper()}_" + ' + Spec(f"__shared__::CustomFlowMatrixSpecs.{FlowMatrix}_MHz") + f' + "_OCC"',
                Patlist = f'scn_arw_{flow.lower()}_hptp1600_12r4t_edt_atspeed_occ_classhvm_list_{corner.lower()}_master',
                LevelsTc = 'SCN_ATOM_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNATOM_OVERRIDE_nom',
                TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48")'),
                PreInstance = '',
                PostInstance = '',
                BaseNumbers = AUTO,
                CornerIdentifiers = Spec(f'__shared__::CornerIdentifiers.AT_{corner_id}'),
                DtsConfiguration = "ALL_CDIE_C48_N2P_NONE_CORE" if "F4XAT" in flow else "ALL_CDIE_C48_N2P_NONE_CORE",
                EndVoltageLimits = Spec(f'__shared__::FlowMatrixSingular.AT_LFM_VMIN_RAIN_KILL') if "F1XAT" in flow else Spec(f'__shared__::FlowMatrixSingular.AT_HIGH_SEARCH_VALUE'),
                ExecutionMode = testinput.get("executionmode", "SearchWithScoreboard"),
                FeatureSwitchSettings = 'fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters',
                LogLevel = "Disabled",
				SetPointsPlistMode = "Local",
                FivrCondition = 'NOM',
                FlowIndexCallbackName = '',
                FlowIndex = TrialParamSpec(f"__shared__::FlowMatrix.FlowIndex"),
                ForwardingMode = 'InputOutput', #offrec ForwardingMode = 'Input',
                InitialMaskBits = '',
                LimitGuardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
                MaskPins = '',
                PatternNameCounterIndexes = '1,2,3,4,5,6,7',
                PinMap = 'NVL_SCN_ATOM',
                RecoveryMode = 'RecoveryPort', 
                RecoveryOptions = Spec(f'__shared__::Recovery_Single.F1F4_recovery_opt_AT'),
                RecoveryTrackingIncoming = 'ACRM1,ACRM0',
                RecoveryTrackingOutgoing = 'ACRM1,ACRM0',
                ScoreboardEdgeTicks = Spec("toInteger(__shared__::Specs.CHK_EDGE_TICK)"),
                #ScoreboardPerPatternFails = 72,
                MaxFailsNum = Spec("toInteger(__shared__::Specs.CHK_MAX_FAILS)"),
                SetPointsPlistParamName = 'Patlist',
                SetPointsPreInstance = Spec(f'SCN_ATOM_CX48_Specs.N2P48_PreInst_{corner.upper()}'),
                SetPointsPostInstance= Spec(f'PSPOST.AT_{corner}'),
                StartVoltages = Spec(f'__shared__::FlowMatrixSingular.AT_LOW_SEARCH_VALUE'),
                StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
			    StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
                StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.AT_SEARCH_RESOLUTION)'),
                TestMode = testinput.get("Testmode", ""),
                #VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions "' + f' + DROPOUT.AT_{corner}'),
                VoltageConverter = Spec(f'"--railconfigurations CDIE_L2_NBLCTRL1 CDIE_L2_NBLCTRL0 --dlvrpins VCCIA --expressions "' + f' + DROPOUT.AT_{corner}'),
                VoltagesOffset = 'GBVars.VoltageOffset',
                VoltageTargets = testinput.get("Voltagetarget", "ATOM1,ATOM0"),
                BypassPort = testinput.get("Bypassport", -1),
                ), # The close bracket here indicates that we are done defining VminTC params
                
                r0 = pFail(setbin = -47, ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')), # Start MTT test port definitions.,
                r1 = pPass(ret = 1, trialaction = "Exit"),
                r2 = pFail(setbin= -47, ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r3 = pPass(ret = 1, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r4 = pFail(setbin= -47, ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r5 = pFail(setbin= -47, ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                
                _fitem=Fitem('SAME', edc=testinput.get("ISEDC"),
                            r0 = pFail(setbin = -47, ret= 0),
                            r1 = pPass(ret = 1),
                            r2 = pFail(setbin = -47, ret= 0),
                            r3 = pPass(ret = 1),
                            r4 = pFail(setbin= -47, ret= 0),
                            r5 = pFail(setbin= -47, ret= 0)))
            
    test_listt_atspeed_occ_f1f4_mtt.append(sample_test_atspeed_occ_f1f4_mtt)

    return test_listt_atspeed_occ_f1f4_mtt

########################################################################
# F1-F4, MTT IO vmin search/check test LAYOUT
########################################################################

def get_test_list_atspeed_f1f4_io_mtt(
    testtype,
    flow, 
    corner, 
    corner_id, 
    atom,
    testinput,
    FlowMatrix,
    recoverytestflag=False
    ):
       
    # decode MTT test name
    test_list_atspeed_f1f4_io_mtt = []
    
    # Get the frequency value from FlowMatrixRule
    frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]
      
    sample_test_atspeed_f1f4_io_mtt = \
        NativeMultiTrial(name = f"ATSPEED_ATOM_{testtype}_K_{flow.upper()}_X_AT_{corner.upper()}_X_FREQ_M{atom}",
                exitaction = "Continue",
                _comment = f"KILL ATSPEED {flow.upper()}",
                trialvar = "CPU_TRIALS::FlowDomain.ATOM",
                template = VminTC(name = f'"ATSPEED_ATOM_{testtype}_K_{flow.upper()}_X_AT_{corner.upper()}_" + ' + Spec(f"__shared__::CustomFlowMatrixSpecs.{FlowMatrix}_MHz") + f' + "_M{atom}"',
                Patlist = testinput.get("Patlist", f"scn_arw_{flow.lower()}_hptp1600_4r4t_edt_atspeed_m{atom}_classhvm_list_{corner.lower()}_master"),
                LevelsTc = 'SCN_ATOM_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNATOM_OVERRIDE_nom',
                TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts800_tstprtclk400_tck50_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts800_tstprtclk400_tck50_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts800_tstprtclk400_tck50_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts800_tstprtclk400_tck50_SCNATOM48")') if "FMINXAT" in flow else Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48")'),
                PreInstance = '',
                PostInstance = '',
                BaseNumbers = AUTO,
                CornerIdentifiers = f'AT{atom}@{corner}',
                DtsConfiguration = "ALL_CDIE_C48_N2P_NONE_CORE" if "F4XAT" in flow else "ALL_CDIE_C48_N2P_NONE_CORE",
                EndVoltageLimits = Spec(f'__shared__::FlowMatrixSingular.AT_LFM_VMIN_RAIN_KILL') if "F1XAT" in flow else Spec(f'__shared__::FlowMatrixSingular.AT_HIGH_SEARCH_VALUE'),
                ExecutionMode = testinput.get("executionmode", "SearchWithScoreboard"),
                FeatureSwitchSettings = 'fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters',
                LogLevel = "Disabled",
				SetPointsPlistMode = "Local",
                FivrCondition = 'NOM',
                FlowIndexCallbackName = '',
                FlowIndex = TrialParamSpec(f"__shared__::FlowMatrix.FlowIndex"),
                ForwardingMode = 'Input' if "FMINXAT" in flow else 'InputOutput',
                InitialMaskBits = '0', #testinput.get("initialmaskbit", ""),
                LimitGuardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
                MaskPins = '',
                PatternNameCounterIndexes = '1,2,3,4,5,6,7',
                PinMap = f'ATOM{atom}_SCAN', #'ATOM3_SCAN,ATOM2_SCAN,ATOM1_SCAN,ATOM0_SCAN',
                RecoveryMode = 'RecoveryPort', 
                RecoveryOptions = Spec(f'__shared__::Recovery_Single.F1F4_recovery_opt_AT'), #'CLASS_NVL_S28C_8A', 
                RecoveryTrackingIncoming = f'ACRM{atom}',
                RecoveryTrackingOutgoing = f'ACRM{atom}',
                ScoreboardEdgeTicks = Spec("toInteger(__shared__::Specs.CHK_EDGE_TICK)"),
                #ScoreboardPerPatternFails = 72,
                MaxFailsNum = Spec("toInteger(__shared__::Specs.CHK_MAX_FAILS)"),
                SetPointsPlistParamName = 'Patlist',
                SetPointsPreInstance= Spec(f'PSPRE.AT_{corner}+' f'","+' f'"MCdrv:atomfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.{FlowMatrix}+")+'"GHz"'),
                SetPointsPostInstance= Spec(f'PSPOST.AT_{corner}'),
                StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry{corner.upper()} , "")'),
			    StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset{corner.upper()} , "")'),
                StartVoltages = Spec(f'__shared__::FlowMatrixSingular.AT_LOW_SEARCH_VALUE'),
                StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.AT_SEARCH_RESOLUTION)'),
                TestMode = testinput.get("Testmode", ""),
                #VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions "' + f' + DROPOUT.AT_{corner}'),
                VoltageConverter = Spec(f'"--railconfigurations CDIE_L2_NBLCTRL{atom} --dlvrpins VCCIA --expressions "' + f' + DROPOUT.AT_{corner}'),
                VoltagesOffset = 'GBVars.VoltageOffset',
                VoltageTargets = f'ATOM{atom}', #testinput.get("Voltagetarget", "ATOM1,ATOM0"),
                BypassPort = testinput.get("Bypassport", -1),
                ), # The close bracket here indicates that we are done defining VminTC params     
                r0=pFail(setbin=-47, ret=0, trialaction= Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r1 = pPass(ret = 1, trialaction = "Exit"),
                r2 = pFail(ret = 2, setbin= -47, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r3 = pPass(ret = 3, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r4 = pFail(ret = 4, setbin= -47, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r5 = pFail(ret = 5, setbin= -47, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                
                _fitem=Fitem('SAME', edc=testinput.get("ISEDC"),
                             r0 = pFail(setbin = -47, ret = 0),
                             r1 = pPass(ret = 1),
                             r2 = pFail(setbin= -47, ret = 0),
                             r3 = pPass(ret = 1),
                             r4 = pFail(setbin= -47, ret = 0),
                             r5 = pFail(setbin= -47, ret = 0)))
                             
    test_list_atspeed_f1f4_io_mtt.append(sample_test_atspeed_f1f4_io_mtt)

    return test_list_atspeed_f1f4_io_mtt


########################################################################
# F5-F6, MTT OCC vmin search/check test LAYOUT
########################################################################

def get_test_list_atspeed_occ_f5f6_mtt (
    testtype,
    flow, 
    corner, 
    testinput,
    FlowMatrix,
    corner_id
    ):
           
    # decode MTT test name
    test_listt_atspeed_occ_f5f6_mtt = []  
    # Get the frequency value from FlowMatrixRule
    frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]
    
    sample_test_atspeed_occ_f5f6_mtt = \
    NativeMultiTrial(name = f"ATSPEED_ATOM_{testtype}_K_{flow.upper()}_X_AT_{corner.upper()}_X_FREQ_OCC",
                exitaction = "Continue",
                _comment = f"KILL ATSPEED {flow.upper()}",
                trialvar = "CPU_TRIALS::FlowDomain.ATOM_TOP",
                template = VminTC(name = f'"ATSPEED_ATOM_{testtype}_K_{flow.upper()}_X_AT_" + ' + Spec(f"__shared__::Corners.AT_{corner_id}") + '+ "_" +' + Spec(f"__shared__::FreqInMHZ.AT_{corner_id}") + f' + "_OCC"',
                Patlist = f'scn_arw_{flow.lower()}_hptp1600_12r4t_edt_atspeed_occ_classhvm_list_{corner.lower()}_master',
                LevelsTc = 'SCN_ATOM_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNATOM_OVERRIDE_nom',
                TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48")'),
                #PreInstance = '',
                #PostInstance = '',
                BaseNumbers = AUTO,
                CornerIdentifiers = TrialParamSpec(f"__shared__::CornerIdentifiers.AT_C5"),
                DtsConfiguration = 'ALL_CDIE_C48_N2P_NONE_CORE',
                EndVoltageLimits = Spec(f'__shared__::FlowMatrixSingular.AT_HIGH_SEARCH_VALUE'),
                ExecutionMode = testinput.get("executionmode", "SearchWithScoreboard"),
		        #FailCaptureCount = Spec("SCN_ATOM_CX48_Specs.Fail_Capture_Count"),
                FeatureSwitchSettings = 'fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters',
                LogLevel = "Disabled",
				SetPointsPlistMode = "Local",
                FivrCondition = 'NOM',
                FivrConditionPlistParamName = "Patlist",
                #FlowIndexCallbackName = '',
                FlowIndex = Spec(f"__shared__::FlowMatrixSingular.FlowIndex"),
                ForwardingMode = 'InputOutput',
                InitialMaskBits = '',
                LimitGuardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
                #MaskPins = '',
                PatternNameCounterIndexes = '1,2,3,4,5,6,7',
                PinMap = 'NVL_SCN_ATOM',
                RecoveryMode = 'RecoveryPort', 
                RecoveryOptions = TrialParamSpec(f'__shared__::Recovery.MTT_recovery_opt_AT'), #'CLASS_NVL_S28C_8A',
                RecoveryTrackingIncoming = 'ACRM1,ACRM0',
                RecoveryTrackingOutgoing = 'ACRM1,ACRM0',
                ScoreboardEdgeTicks = Spec("toInteger(__shared__::Specs.CHK_EDGE_TICK)"),
                #ScoreboardPerPatternFails = 72,
                MaxFailsNum = Spec("toInteger(__shared__::Specs.CHK_MAX_FAILS)"),
                SetPointsPlistParamName = 'Patlist',
                SetPointsPreInstance= TrialParamSpec(f'SCN_ATOM_CX48_Specs.N2P48_PreInst_F5'),
                SetPointsPostInstance= Spec(f'PSPOST.AT_F5'),
                StartVoltagesForRetry = TrialParamSpec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetryF5 , ["","",""])'),
			    StartVoltagesOffset = TrialParamSpec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffsetF5 , ["","",""])'),
                StartVoltages = Spec(f'__shared__::FlowMatrixSingular.AT_LOW_SEARCH_VALUE'),
                StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.AT_SEARCH_RESOLUTION)'),
                TestMode = testinput.get("Testmode", ""),
                #VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions "' + f' + DROPOUT.AT_{corner}'),
                VoltageConverter = Spec(f'"--railconfigurations CDIE_L2_NBLCTRL1 CDIE_L2_NBLCTRL0 --dlvrpins VCCIA --expressions "' + f' + DROPOUT.AT_{corner}'),
                VoltagesOffset = 'GBVars.VoltageOffset',
                VoltageTargets = "ATOM1,ATOM0",
                BypassPort = testinput.get("Bypassport", -1),
                ), # The close bracket here indicates that we are done defining VminTC params
                
                r0 = pFail(setbin = -47, ret= 0, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')), # Start MTT test port definitions.,
                r1 = pPass(ret = 1, trialaction = "Exit"),
                r2 = pFail(setbin= -47, ret= 2, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r3 = pPass(ret = 3, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r4 = pFail(setbin= -47, ret= 4, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r5 = pFail(setbin= -47, ret= 5, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                
                _fitem=Fitem('SAME', edc=testinput.get("ISEDC"),
                            r0 = pFail(setbin = -47, ret= 0),
                            r1 = pPass(ret = 1),
                            r2 = pFail(setbin = -47, ret= 0),
                            r3 = pPass(ret = 1),
                            r4 = pFail(setbin= -47, ret= 0),
                            r5 = pFail(setbin= -47, ret= 0)))
            
    test_listt_atspeed_occ_f5f6_mtt.append(sample_test_atspeed_occ_f5f6_mtt)

    return test_listt_atspeed_occ_f5f6_mtt


########################################################################
# F5-F6, MTT IO vmin search/check test LAYOUT
########################################################################

def get_test_list_atspeed_f5f6_io_mtt(
    testtype,
    flow, 
    corner, 
    atom,
    testinput,
    FlowMatrix,
    corner_id,
    recoverytestflag=False
    ):
       
    # decode MTT test name
    test_list_atspeed_f5f6_io_mtt = []
    
    # Get the frequency value from FlowMatrixRule
    frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]
      
    sample_test_atspeed_f5f6_io_mtt = \
        NativeMultiTrial(name = f"ATSPEED_ATOM_{testtype}_K_{flow.upper()}_X_AT_{corner.upper()}_X_FREQ_M{atom}",
                exitaction = "Continue",
                _comment = [f"KILL ATSPEED {flow.upper()}","NOCLEAN", "PATLIST_NOCLEAN : Due to needing this plist", "TCG_NOCLEAN : Due to needing it"],
                trialvar = "CPU_TRIALS::FlowDomain.ATOM_TOP",
                template = VminTC(name = f'"ATSPEED_ATOM_{testtype}_K_{flow.upper()}_X_AT_" + ' + Spec(f"__shared__::Corners.AT_{corner_id}") + '+ "_" +' + Spec(f"__shared__::FreqInMHZ.AT_{corner_id}") + f' + "_M{atom}"',
                Patlist = testinput.get("Patlist", f"scn_arw_{flow.lower()}_hptp1600_4r4t_edt_atspeed_m{atom}_classhvm_list_{corner.lower()}_master"),
                LevelsTc = 'SCN_ATOM_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNATOM_OVERRIDE_nom',
                TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48")'),
                #PreInstance = '',
                #PostInstance = '',
                BaseNumbers = AUTO,
                CornerIdentifiers = TrialParamSpec(f'SCN_ATOM_CX48_corneridentifier.AT_C5_M{atom}'),
                DtsConfiguration = 'ALL_CDIE_C48_N2P_NONE_CORE',
                EndVoltageLimits = Spec(f'__shared__::FlowMatrixSingular.AT_HIGH_SEARCH_VALUE'),
                ExecutionMode = testinput.get("executionmode", "SearchWithScoreboard"),
                #FailCaptureCount = Spec("SCN_ATOM_CX48_Specs.Fail_Capture_Count"),
                FeatureSwitchSettings =  'fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters',
                LogLevel = "Disabled",
				SetPointsPlistMode = "Local",
                FivrCondition = 'NOM',
                FivrConditionPlistParamName = "Patlist",
                #FlowIndexCallbackName = '',
                FlowIndex = Spec(f"__shared__::FlowMatrixSingular.FlowIndex"),
                ForwardingMode = 'InputOutput',
                InitialMaskBits = '0', #testinput.get("initialmaskbit", ""),
                LimitGuardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
                #MaskPins = '',
                PatternNameCounterIndexes = '1,2,3,4,5,6,7',
                PinMap = f'ATOM{atom}_SCAN', #'ATOM3_SCAN,ATOM2_SCAN,ATOM1_SCAN,ATOM0_SCAN',
                RecoveryMode =  'RecoveryPort', 
                RecoveryOptions = TrialParamSpec(f'__shared__::Recovery.MTT_recovery_opt_AT'), #'CLASS_NVL_S28C_8A',
                RecoveryTrackingIncoming = f'ACRM{atom}',
                RecoveryTrackingOutgoing = f'ACRM{atom}',
                ScoreboardEdgeTicks = Spec("toInteger(__shared__::Specs.CHK_EDGE_TICK)"),
                #ScoreboardPerPatternFails = 72,
                MaxFailsNum = Spec("toInteger(__shared__::Specs.CHK_MAX_FAILS)"),
                SetPointsPlistParamName = 'Patlist',
                SetPointsPreInstance= TrialParamSpec(f'PSPRE.AT_{corner}+' f'","+' f'"MCdrv:atomfreq_0:"' +Spec(f"+__shared__::FreqValues.AT_{corner_id}+")+'"GHz"'),
                SetPointsPostInstance= Spec(f'PSPOST.AT_F5'),
                StartVoltagesForRetry = TrialParamSpec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetryF5 , ["","",""])'),
			    StartVoltagesOffset = TrialParamSpec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffsetF5 , ["","",""])'),
                StartVoltages = Spec(f'__shared__::FlowMatrixSingular.AT_LOW_SEARCH_VALUE'),
                StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.AT_SEARCH_RESOLUTION)'),
                TestMode = testinput.get("Testmode", ""),
                #VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions "' + f' + DROPOUT.AT_{corner}'),
                VoltageConverter = Spec(f'"--railconfigurations CDIE_L2_NBLCTRL{atom} --dlvrpins VCCIA --expressions "' + f' + DROPOUT.AT_{corner}'),
                #VoltagesOffset = 'GBVars.VoltageOffset',
                VoltageTargets = f'ATOM{atom}', #testinput.get("Voltagetarget", "ATOM1,ATOM0"),
                BypassPort = testinput.get("Bypassport", -1),
                ), # The close bracket here indicates that we are done defining VminTC params     
                r0=pFail(setbin=-47, ret=0, trialaction= Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r1 = pPass(ret = 1, trialaction = "Exit"),
                r2 = pFail(ret = 2, setbin= -47, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r3 = pPass(ret = 3, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r4 = pFail(ret = 4, setbin= -47, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r5 = pFail(ret = 5, setbin= -47, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),              
                _fitem=Fitem('SAME', edc=testinput.get("ISEDC"),
                             r0 = pFail(setbin = -47, ret = 0),
                             r1 = pPass(ret = 1),
                             r2 = pFail(setbin= -47, ret = 0),
                             r3 = pPass(ret = 1),
                             r4 = pFail(setbin= -47, ret = 0),
                             r5 = pFail(setbin= -47, ret = 0)))
                             
    test_list_atspeed_f5f6_io_mtt.append(sample_test_atspeed_f5f6_io_mtt)

    return test_list_atspeed_f5f6_io_mtt


############################################################################################
# APEXTC OCC LAYOUT
############################################################################################


def get_test_list_atspeed_f5f6_occapex(    
    testtype,
    flow, 
    corner, 
    testinput,
    FlowMatrix,
    corner_id,
    recoverytestflag=False
    ):
       
    # decode MTT test name
    test_list_atspeed_f5f6_occapex = []
    
    # Get the frequency value from FlowMatrixRule
    frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]
      
    sample_test_atspeed_f5f6_occapex = \
        ApexTC(name = f"ATSPEED_ATOM_APEX_K_{flow.upper()}_X_AT_F5_X_APEX_OCC",
                #exitaction = "Restore",
                #_comment = f"KILL ATSPEED {flow.upper()}",
                #trialvar = "CPU_TRIALS::FlowDomain.ATOM_TOP",
                #template=ApexTC(
                         #name=f'"ATSPEED_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_X_" + ' + Spec(f"__shared__::Corners.AT_{corner_id}") + f' + "_APEXM{atom}"',
                Patlist = 'scn_arw_vmaxf5xat_hptp1600_12r4t_edt_atspeed_occ_classhvm_list',
                LevelsTc = 'SCN_ATOM_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNATOM_OVERRIDE_nom',
                TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48")'),
                #InitialMaskBits = '0', 
                DtsConfiguration = 'ALL_CDIE_C48_N2P_NONE_CORE',
                ForwardingMode = 'Input', #'Input',
                PinMap = 'NVL_SCN_ATOM',
    	        RecoveryOptions = '', #offrec RecoveryOptions = 'CLASS_NVL_S28C_8A',
	            RecoveryTracking= 'ACRM1,ACRM0',
                #ScoreboardEdgeTicks = Spec("toInteger(__shared__::Specs.CHK_EDGE_TICK)"),
                #MaxFailsNum = Spec("toInteger(__shared__::Specs.CHK_MAX_FAILS)"),
	            End= Spec('__shared__::FlowMatrixSingular.APEX_ATOM_MIN'),
                Start=Spec('__shared__::FlowMatrixSingular.APEX_ATOM_MAX'),
                SetPointsPreInstance= Spec(f'SCN_ATOM_CX48_Specs.N2P48_PreInst_F5_APEX'),
                #SetPointsPostInstance= '',
                SetPointsPostInstance= f'CDIE_ATOM:nblctrl_cdie_atom_l2:nblon',
                FivrCondition = 'NOM',
	            FivrConditionPlistParamName="Patlist",
	            StepSize = Spec("toInteger(3)"),
                #PatternNameCounterIndexes = '1,2,3,4,5,6,7',
                VoltageConverter = Spec(f'"--overrides ATOM1:"+' +Spec(f"__shared__::FlowMatrixSingular.AT_VMAX_VALUE")+ f'+",ATOM0:"+' +Spec(f"__shared__::FlowMatrixSingular.AT_VMAX_VALUE")+ f'+ " --dlvrpins VCCIA --expressions "' + f' + DROPOUT.AT_F5'),            
                #VoltageConverter = --dlvrpins VCCIA  --expressions " + DROPOUT.CLR_F5 + " --overrides CCF:" + __shared__::FlowMatrixSingular.CCF_VMAX_VALUE;
                ExportTokens=Spec('__shared__::APEX_Tokens.ATToken'),
	            Targets= f'SATOM1,SATOM0',
	            BypassPort = testinput.get("Bypassport", -1),
                #), # The close bracket here indicates that we are done defining VminTC params     
                #  r0=pFail(setbin=-47, ret=0, trialaction=Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                #  r1=pPass(ret=1, trialaction="Next"),
                #  r2=pFail(setbin=-47, ret=0, trialaction="Exit"),
                #  r3=pPass(ret=1, trialaction="Next"),
                #  r4=pFail(setbin=-47, ret=0, trialaction="Exit"),
                #  r5=pFail(setbin=-47, ret=0, trialaction="Exit"),
                  _fitem=Fitem('SAME', edc=testinput.get("ISEDC"),
                            r0 = pFail(setbin = -47, goto="NEXT"),
                            r1 = pPass(goto="NEXT"),
                            r2 = pFail(setbin = -47, goto="NEXT"),
                            r3 = pPass(goto="NEXT"),
                            r4 = pFail(setbin= -47, goto="NEXT"),
                            r5 = pFail(setbin= -47, goto="NEXT")))

                             
    test_list_atspeed_f5f6_occapex.append(sample_test_atspeed_f5f6_occapex)

    return test_list_atspeed_f5f6_occapex


############################################################################################
# APEXTC IO LAYOUT
############################################################################################
def get_test_list_atspeed_f5f6_ioapex(
    flow, 
    corner, 
    atom,
    testinput,
    FlowMatrix,
    corner_id,
    recoverytestflag=False
    ):
       
    # decode MTT test name
    test_list_atspeed_f5f6_ioapex = []
    
    # Get the frequency value from FlowMatrixRule
    frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]
      
    sample_test_atspeed_f5f6_ioapex = \
        ApexTC(name = f"ATSPEED_ATOM_VMIN_K_{flow.upper()}_X_AT_{corner.upper()}_X_FREQ_M{atom}_APEX",
                #exitaction = "Restore",
                #_comment = f"KILL ATSPEED {flow.upper()}",
                #trialvar = "CPU_TRIALS::FlowDomain.ATOM_TOP",
                #template=ApexTC(
                         #name=f'"ATSPEED_VMIN_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_X_" + ' + Spec(f"__shared__::Corners.AT_{corner_id}") + f' + "_APEXM{atom}"',
                Patlist = f"scn_arw_vmaxf5xat_hptp1600_4r4t_edt_atspeed_m{atom}_classhvm_list",
                LevelsTc = 'SCN_ATOM_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNATOM_OVERRIDE_nom',
                TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48")'),
                InitialMaskBits = '0', 
                DtsConfiguration = 'ALL_CDIE_C48_N2P_NONE_CORE',
                ForwardingMode = 'Input', #'Input',
                PinMap = f'ATOM{atom}_SCAN',
    	        RecoveryOptions = '', #offrec RecoveryOptions = 'CLASS_NVL_S28C_8A',
	            RecoveryTracking= f'ACRM{atom}',
                #ScoreboardEdgeTicks = Spec("toInteger(__shared__::Specs.CHK_EDGE_TICK)"),
                #MaxFailsNum = Spec("toInteger(__shared__::Specs.CHK_MAX_FAILS)"),
	            End= Spec('__shared__::FlowMatrixSingular.APEX_ATOM_MIN'),
                Start=Spec('__shared__::FlowMatrixSingular.APEX_ATOM_MAX'),
                SetPointsPreInstance= Spec(f'PSPRE.AT_{corner}+' f'","+' f'"MCdrv:atomfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.AT_F5_FREQ+")+'"GHz"'),
                #SetPointsPreInstance= Spec(f'PSPRE.AT_{corner}+' f'","+' f'"MCdrv:atomfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.AT_F5_FREQ+")+'"GHz,CDIE_ATOM:nblctrl_cdie_atom_l2:nbloff"'),
                #SetPointsPostInstance= '',
                SetPointsPostInstance= f'CDIE_ATOM:nblctrl_cdie_atom_l2:nblon',
                FivrCondition = 'NOM',
	            FivrConditionPlistParamName="Patlist",
	            StepSize = Spec("toInteger(3)"),
                PatternNameCounterIndexes = '1,2,3,4,5,6,7',
                VoltageConverter = Spec(f'"--overrides ATOM{atom}:"+__shared__::FlowMatrixSingular.AT_VMAX_VALUE+' + '" --dlvrpins VCCIA --expressions " + DROPOUT.AT_F5'),            
                #VoltageConverter = --dlvrpins VCCIA  --expressions " + DROPOUT.CLR_F5 + " --overrides CCF:" + __shared__::FlowMatrixSingular.CCF_VMAX_VALUE;
                ExportTokens=Spec('__shared__::APEX_Tokens.ATToken'),
	            Targets=f'SATOM{atom}',
	            BypassPort = testinput.get("Bypassport", 1),
                #), # The close bracket here indicates that we are done defining VminTC params     
                #  r0=pFail(setbin=-47, ret=0, trialaction=Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                #  r1=pPass(ret=1, trialaction="Next"),
                #  r2=pFail(setbin=-47, ret=0, trialaction="Exit"),
                #  r3=pPass(ret=1, trialaction="Next"),
                #  r4=pFail(setbin=-47, ret=0, trialaction="Exit"),
                #  r5=pFail(setbin=-47, ret=0, trialaction="Exit"),
                  _fitem=Fitem('SAME', edc=testinput.get("ISEDC"),
                            r0 = pFail(setbin = -47, goto="NEXT"),
                            r1 = pPass(goto="NEXT"),
                            r2 = pFail(setbin = -47, goto="NEXT"),
                            r3 = pPass(goto="NEXT"),
                            r4 = pFail(setbin= -47, goto="NEXT"),
                            r5 = pFail(setbin= -47, goto="NEXT")))

                             
    test_list_atspeed_f5f6_ioapex.append(sample_test_atspeed_f5f6_ioapex)

    return test_list_atspeed_f5f6_ioapex

########################################################################
# LTTC F5 MTT OCC vmin search/check test LAYOUT
########################################################################

def get_test_list_atspeed_lttcf5_occ_mtt(
    testtype,
    flow, 
    corner, 
    testinput,
    FlowMatrix,
    corner_id
    ):
       
    # decode MTT test name
    test_list_atspeed_lttcf5_occ_mtt = []
    
    # Get the frequency value from FlowMatrixRule
    frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]
      
    sample_test_atspeed_lttcf5_occ_mtt = \
        NativeMultiTrial(name = f"ATSPEED_ATOM_{testtype}_K_{flow.upper()}_X_AT_{corner.upper()}_X_FREQ_OCC",
                exitaction = "Continue",
                _comment = f"KILL ATSPEED {flow.upper()}",
                trialvar = "CPU_TRIALS::FlowDomain.ATOM_TOP",
                template = VminTC(name = f'"ATSPEED_ATOM_{testtype}_K_{flow.upper()}_X_AT_" + ' + Spec(f"__shared__::Corners.AT_{corner_id}") + '+ "_" +' + Spec(f"__shared__::FreqInMHZ.AT_{corner_id}") + f' + "_OCC"',
                Patlist = 'scn_arw_f5lttc_hptp1600_12r4t_edt_atspeed_occ_classhvm_list',
                LevelsTc = 'SCN_ATOM_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNATOM_OVERRIDE_nom',
                TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48")'),
                #PreInstance = '',
                #PostInstance = '',
                BaseNumbers = AUTO,
                CornerIdentifiers = '',
                DtsConfiguration = '',
                EndVoltageLimits = TrialParamSpec(f'"D.R"+__shared__::Corners.AT_C5+"AT"'),
                ExecutionMode = testinput.get("executionmode", "SearchWithScoreboard"),
                #FailCaptureCount = Spec("SCN_ATOM_CX48_Specs.Fail_Capture_Count"),
                FeatureSwitchSettings =  'fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters',
                LogLevel = "Disabled",
				SetPointsPlistMode = "Local",
                FivrCondition = 'NOM',
                FivrConditionPlistParamName = "Patlist",
                #FlowIndexCallbackName = '',
                FlowIndex = Spec(f"__shared__::FlowMatrixSingular.FlowIndex"),
                ForwardingMode = 'Input',
                #InitialMaskBits = '0', #testinput.get("initialmaskbit", ""),
                LimitGuardband = '31mV',
                #MaskPins = '',
                PatternNameCounterIndexes = '1,2,3,4,5,6,7',
                PinMap = 'NVL_SCN_ATOM',
                RecoveryMode =  'NoRecovery', 
                RecoveryOptions = TrialParamSpec(f'__shared__::Recovery.MTT_recovery_opt_AT'), #'CLASS_NVL_S28C_8A',
                RecoveryTrackingIncoming = 'ACRM1,ACRM0',
                RecoveryTrackingOutgoing = 'ACRM1,ACRM0',
                ScoreboardEdgeTicks = Spec("toInteger(__shared__::Specs.CHK_EDGE_TICK)"),
                #ScoreboardPerPatternFails = 72,
                MaxFailsNum = Spec("toInteger(__shared__::Specs.CHK_MAX_FAILS)"),
                SetPointsPlistParamName = 'Patlist',
                SetPointsPreInstance= TrialParamSpec(f'SCN_ATOM_CX48_Specs.N2P48_PreInst_F5'),
                SetPointsPostInstance= Spec(f'PSPOST.AT_F5'),
                StartVoltagesForRetry = TrialParamSpec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetryF5 , ["","",""])'),
			    StartVoltagesOffset = TrialParamSpec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffsetF5 , ["","",""])'),
                StartVoltages = TrialParamSpec(f'"D.R"+__shared__::Corners.AT_C5+"AT"'),
                StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.AT_SEARCH_RESOLUTION)'),
                TestMode = testinput.get("Testmode", ""),
                #VoltageConverter = Spec('"--dlvrpins VCCIA --expressions " + DROPOUT.AT_F5 + " --overrides CCF:"+' + Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")),
                VoltageConverter = Spec('"--railconfigurations CDIE_L2_NBLCTRL1 CDIE_L2_NBLCTRL0 --dlvrpins VCCIA --expressions " + DROPOUT.AT_F5 + " --overrides CCF:"+' + Spec(f"__shared__::FlowMatrixSingular.CCF_VMAX_VALUE")),
                #VoltagesOffset = 'GBVars.VoltageOffset',
                VoltageTargets = "ATOM1,ATOM0",
                BypassPort = testinput.get("Bypassport", -1),
                ), # The close bracket here indicates that we are done defining VminTC params     
                r0=pFail(setbin=-47, ret=0, trialaction = "Exit"),
                r1 = pPass(ret = 1, trialaction = "Exit"),
                r2 = pFail(ret = 2, trialaction = "Exit"),
                r3 = pPass(ret = 3, trialaction = "Exit"),
                r4 = pFail(ret = 4, trialaction = "Exit"),
                r5 = pFail(ret = 5, trialaction = "Exit"),              
                _fitem=Fitem('SAME', edc=testinput.get("ISEDC"),
                             r0 = pFail(setbin=9447, ret = 0),
                             r1 = pPass(ret = 1),
                             r2 = pFail(setbin=9447, ret = 0),
                             r3 = pPass(ret = 1),
                             r4 = pFail(setbin= 9794, ret = 0),
                             r5 = pFail(setbin= 9419, ret = 0)))
                             
    test_list_atspeed_lttcf5_occ_mtt.append(sample_test_atspeed_lttcf5_occ_mtt)

    return test_list_atspeed_lttcf5_occ_mtt
########################################################################
# LTTC F5 MTT IO vmin search/check test LAYOUT
########################################################################

def get_test_list_atspeed_lttcf5_io_mtt(
    testtype,
    flow, 
    corner, 
    atom,
    testinput,
    FlowMatrix,
    corner_id,
    recoverytestflag=False
    ):
       
    # decode MTT test name
    test_list_atspeed_lttcf5_io_mtt = []
    
    # Get the frequency value from FlowMatrixRule
    frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]

    # setbin_value = base_lttc_bin + atom
      
    sample_test_atspeed_lttcf5_io_mtt = \
        NativeMultiTrial(name = f"ATSPEED_ATOM_{testtype}_K_{flow.upper()}_X_AT_{corner.upper()}_X_FREQ_M{atom}",
                exitaction = "Continue",
                _comment = f"KILL ATSPEED {flow.upper()}",
                trialvar = "CPU_TRIALS::FlowDomain.ATOM_TOP",
                template = VminTC(name = f'"ATSPEED_ATOM_{testtype}_K_{flow.upper()}_X_AT_" + ' + Spec(f"__shared__::Corners.AT_{corner_id}") + '+ "_" +' + Spec(f"__shared__::FreqInMHZ.AT_{corner_id}") + f' + "_M{atom}"',
                Patlist = testinput.get("Patlist", f"scn_arw_f5lttc_hptp1600_4r4t_edt_atspeed_m{atom}_classhvm_list"),
                LevelsTc = 'SCN_ATOM_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNATOM_OVERRIDE_nom',
                TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48")'),
                #PreInstance = '',
                #PostInstance = '',
                BaseNumbers = AUTO,
                CornerIdentifiers = '',
                DtsConfiguration = '',
                EndVoltageLimits = TrialParamSpec(f'"D.R"+__shared__::Corners.AT_C5+"AT"'),
                ExecutionMode = testinput.get("executionmode", "SearchWithScoreboard"),
                #FailCaptureCount = Spec("SCN_ATOM_CX48_Specs.Fail_Capture_Count"),
                FeatureSwitchSettings =  'fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters',
                LogLevel = "Disabled",
				SetPointsPlistMode = "Local",
                FivrCondition = 'NOM',
                FivrConditionPlistParamName = "Patlist",
                #FlowIndexCallbackName = '',
                FlowIndex = Spec(f"__shared__::FlowMatrixSingular.FlowIndex"),
                ForwardingMode = 'Input',
                InitialMaskBits = '0', #testinput.get("initialmaskbit", ""),
                LimitGuardband = '31mV',
                #MaskPins = '',
                PatternNameCounterIndexes = '1,2,3,4,5,6,7',
                PinMap = f'ATOM{atom}_SCAN', #'ATOM3_SCAN,ATOM2_SCAN,ATOM1_SCAN,ATOM0_SCAN',
                RecoveryMode =  'RecoveryPort', 
                RecoveryOptions = TrialParamSpec(f'__shared__::Recovery.MTT_recovery_opt_AT'), #'CLASS_NVL_S28C_8A',
                RecoveryTrackingIncoming = f'ACRM{atom}',
                RecoveryTrackingOutgoing = f'ACRM{atom}',
                ScoreboardEdgeTicks = Spec("toInteger(__shared__::Specs.CHK_EDGE_TICK)"),
                #ScoreboardPerPatternFails = 72,
                MaxFailsNum = Spec("toInteger(__shared__::Specs.CHK_MAX_FAILS)"),
                SetPointsPlistParamName = 'Patlist',
                SetPointsPreInstance= TrialParamSpec(f'PSPRE.AT_{corner}+' f'","+' f'"MCdrv:atomfreq_0:"' +Spec(f"+__shared__::FreqValues.AT_{corner_id}+")+'"GHz"'),
                SetPointsPostInstance= Spec(f'PSPOST.AT_F5'),
                StartVoltagesForRetry = TrialParamSpec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetryF5 , ["","",""])'),
			    StartVoltagesOffset = TrialParamSpec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffsetF5 , ["","",""])'),
                StartVoltages = TrialParamSpec(f'"D.R"+__shared__::Corners.AT_C5+"AT"'),
                StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.AT_SEARCH_RESOLUTION)'),
                TestMode = testinput.get("Testmode", ""),
                #VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions "' + f' + DROPOUT.AT_{corner}'),
                VoltageConverter = Spec(f'"--railconfigurations CDIE_L2_NBLCTRL{atom} --dlvrpins VCCIA --expressions "' + f' + DROPOUT.AT_{corner}'),
                #VoltagesOffset = 'GBVars.VoltageOffset',
                VoltageTargets = f'ATOM{atom}', #testinput.get("Voltagetarget", "ATOM1,ATOM0"),
                BypassPort = testinput.get("Bypassport", -1),
                ), # The close bracket here indicates that we are done defining VminTC params     
                r0=pFail(setbin=-47, ret=0, trialaction = "Exit"),
                r1 = pPass(ret = 1, trialaction = "Exit"),
                r2 = pFail(ret = 2, trialaction = "Exit"),
                r3 = pPass(ret = 3, trialaction = "Exit"),
                r4 = pFail(ret = 4, trialaction = "Exit"),
                r5 = pFail(ret = 5, trialaction = "Exit"),              
                _fitem=Fitem('SAME', edc=testinput.get("ISEDC"),
                             r0 = pFail(setbin=9447, ret = 0),
                             r1 = pPass(ret = 1),
                             r2 = pFail(setbin=9447, ret = 0),
                             r3 = pPass(ret = 1),
                             r4 = pFail(setbin= 9794, ret = 0),
                             r5 = pFail(setbin= 9419, ret = 0)))
                             
    test_list_atspeed_lttcf5_io_mtt.append(sample_test_atspeed_lttcf5_io_mtt)

    return test_list_atspeed_lttcf5_io_mtt

########################################################################
# F1 vmax, OCC SA test LAYOUT
########################################################################

def get_test_list_sa_f1vmax_occ_mtt(
    testtype,
    flow, 
    corner, 
    testinput,
    FlowMatrix
    ):
       
    # decode MTT test name
    test_list_sa_f1vmax_occ_mtt = []
    
    # Get the frequency value from FlowMatrixRule
    frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]
      
    sample_test_sa_f1vmax_occ_mtt = \
        VminTC(name = f"STUCKAT_ATOM_SB_K_{flow.upper()}_X_AT_MAX_X_F1_OCC",
                #exitaction = "Continue",
                #_comment = f"KILL ATSPEED {flow.upper()}",
                #trialvar = "CPU_TRIALS::FlowDomain.ATOM",
                #template = VminTC(name = f'"ATSPEED_{testtype}_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_" + ' + Spec(f"__shared__::CustomFlowMatrixSpecs.{FlowMatrix}_MHz") + f' + "_M{atom}"',
                Patlist = testinput.get("Patlist", f'scn_arw_vmax{corner.lower()}xat_hptp1600_12r4t_edt_stuckat_occ_classhvm_list'),
                LevelsTc = 'SCN_ATOM_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNATOM_OVERRIDE_nom',
                TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48")'),
                PreInstance = '',
                PostInstance = '',
                BaseNumbers = AUTO,
                CornerIdentifiers = '',
                DtsConfiguration = '',
                EndVoltageLimits = Spec(f'__shared__::FlowMatrixSingular.AT_VMAX_VALUE'),
                ExecutionMode = testinput.get("executionmode", "SearchWithScoreboard"),
				FailCaptureCount = Spec("toInteger(999)"),
                FeatureSwitchSettings = 'fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters',
                LogLevel = "Disabled",
				SetPointsPlistMode = "Local",
                FivrCondition = 'NOM',
                FlowIndexCallbackName = '',
                FlowIndex = Spec(f"__shared__::FlowMatrixSingular.FlowIndex"),
                ForwardingMode = 'Input',
                InitialMaskBits = '', #testinput.get("initialmaskbit", ""),
                #LimitGuardband = 'GBVars.LimitGuardband',
                MaskPins = '',
                PatternNameCounterIndexes = '1,2,3,4,5,6,7',
                PinMap = 'NVL_SCN_ATOM',
                RecoveryMode = 'RecoveryPort', 
                RecoveryOptions = Spec(f'__shared__::Recovery_Single.F1F4_recovery_opt_AT'),
                RecoveryTrackingIncoming = 'ACRM1,ACRM0',
                RecoveryTrackingOutgoing = 'ACRM1,ACRM0',
                ScoreboardEdgeTicks = Spec("toInteger(__shared__::Specs.VMX_EDGE_TICK)"),
                #ScoreboardPerPatternFails = 72,
                MaxFailsNum = Spec("toInteger(__shared__::Specs.VMX_MAX_FAILS)"),
                SetPointsPlistParamName = 'Patlist',
                SetPointsPreInstance= Spec(f'SCN_ATOM_CX48_Specs.N2P48_PreInst_F1_VMAX'),
                #SetPointsPostInstance= Spec(f'PSPOST.AT_{corner}'),
                SetPointsPostInstance= Spec(f'PSPOST.AT_{corner}+' f'","+' f'"CDIE_ATOM:nblctrl_cdie_atom_l2:nblon"'),
                StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetryF1 , "")'),
			    StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffsetF1 , "")'),
                StartVoltages = Spec(f'__shared__::FlowMatrixSingular.AT_VMAX_VALUE'),
                StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.AT_SEARCH_RESOLUTION)'),
                TestMode = testinput.get("Testmode", ""),
                VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions "' + f' + DROPOUT.AT_F1'),
                VoltagesOffset = 'GBVars.VoltageOffset',
                VoltageTargets = "ATOM1,ATOM0",
                BypassPort = testinput.get("Bypassport", -1),
                #), # The close bracket here indicates that we are done defining VminTC params     
                #r0=pFail(setbin=-47, ret=0, trialaction=Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                #r1 = pPass(ret = 1, trialaction = "Exit"),
                #r2 = pFail(ret = 2, setbin= -47, trialaction = "Next"),
                #r3 = pPass(ret = 3, trialaction = "Exit"),
                #r4 = pFail(ret = 4, setbin= -47, trialaction = "Next"),
                #r5 = pFail(ret = 5, setbin= -47, trialaction = "Next"),
                
                _fitem=Fitem('SAME', edc=testinput.get("ISEDC"),
                             r0 = pFail(setbin = -42, ret=0),
                             r1 = pPass(goto="NEXT"),
                             r2 = pFail(setbin= -42, ret=0),
                             r3 = pPass(goto="NEXT"),
                             r4 = pFail(setbin= -42, ret=0),
                             r5 = pFail(setbin= -42, ret=0)))
                             
    test_list_sa_f1vmax_occ_mtt.append(sample_test_sa_f1vmax_occ_mtt)

    return test_list_sa_f1vmax_occ_mtt



########################################################################
# F1 vmax, IO SA test LAYOUT
########################################################################

def get_test_list_sa_f1vmax_io_mtt(
    testtype,
    flow, 
    corner, 
    atom,
    testinput,
    FlowMatrix,
    recoverytestflag=False
    ):
       
    # decode MTT test name
    test_list_sa_f1vmax_io_mtt = []
    
    # Get the frequency value from FlowMatrixRule
    frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]
      
    sample_test_sa_f1vmax_io_mtt = \
        VminTC(name = f"STUCKAT_ATOM_SB_K_{flow.upper()}_X_AT_MAX_X_F1_M{atom}",
                #exitaction = "Continue",
                #_comment = f"KILL ATSPEED {flow.upper()}",
                #trialvar = "CPU_TRIALS::FlowDomain.ATOM",
                #template = VminTC(name = f'"ATSPEED_{testtype}_K_{flow.upper()}_X_{VOLTAGE_DOMAIN.upper()}_{corner.upper()}_" + ' + Spec(f"__shared__::CustomFlowMatrixSpecs.{FlowMatrix}_MHz") + f' + "_M{atom}"',
                Patlist = testinput.get("Patlist", f"scn_arw_vmax{corner.lower()}xat_hptp1600_4r4t_edt_stuckat_m{atom}_classhvm_list"),
                LevelsTc = 'SCN_ATOM_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNATOM_OVERRIDE_nom',
                TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48")'),
                PreInstance = '',
                PostInstance = '',
                BaseNumbers = AUTO,
                CornerIdentifiers = '',
                DtsConfiguration = '',
                EndVoltageLimits = Spec(f'__shared__::FlowMatrixSingular.AT_VMAX_VALUE'),
                ExecutionMode = testinput.get("executionmode", "SearchWithScoreboard"),
				FailCaptureCount = Spec("toInteger(999)"),
                FeatureSwitchSettings = 'fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters',
                LogLevel = "Disabled",
				SetPointsPlistMode = "Local",
                FivrCondition = 'NOM',
                FlowIndexCallbackName = '',
                FlowIndex = Spec(f"__shared__::FlowMatrixSingular.FlowIndex"),
                ForwardingMode = 'Input',
                InitialMaskBits = '0', #testinput.get("initialmaskbit", ""),
                #LimitGuardband = 'GBVars.LimitGuardband',
                MaskPins = '',
                PatternNameCounterIndexes = '1,2,3,4,5,6,7',
                PinMap = f'ATOM{atom}_SCAN', #'ATOM3_SCAN,ATOM2_SCAN,ATOM1_SCAN,ATOM0_SCAN',
                RecoveryMode = 'RecoveryPort', 
                RecoveryOptions = Spec(f'__shared__::Recovery_Single.F1F4_recovery_opt_AT'),
                RecoveryTrackingIncoming = f'ACRM{atom}',
                RecoveryTrackingOutgoing = f'ACRM{atom}',
                ScoreboardEdgeTicks = Spec("toInteger(__shared__::Specs.VMX_EDGE_TICK)"),
                #ScoreboardPerPatternFails = 72,
                MaxFailsNum = Spec("toInteger(__shared__::Specs.VMX_MAX_FAILS)"),
                SetPointsPlistParamName = 'Patlist',
                #SetPointsPreInstance= Spec(f'PSPRE.AT_{corner}+' f'","+' f'"MCdrv:atomfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.AT_F1_FREQ+")+'"GHz"'),
                SetPointsPreInstance= Spec(f'PSPRE.AT_{corner}+' f'","+' f'"MCdrv:atomfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.AT_F1_FREQ+")+'"GHz,CDIE_ATOM:nblctrl_cdie_atom_l2:nbloff"'),
                #SetPointsPostInstance= Spec(f'PSPOST.AT_{corner}'),
                SetPointsPostInstance= Spec(f'PSPOST.AT_{corner}+' f'","+' f'"CDIE_ATOM:nblctrl_cdie_atom_l2:nblon"'),
                StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetryF1 , "")'),
			    StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffsetF1 , "")'),
                StartVoltages = Spec(f'__shared__::FlowMatrixSingular.AT_VMAX_VALUE'),
                StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.AT_SEARCH_RESOLUTION)'),
                TestMode = testinput.get("Testmode", ""),
                VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions "' + f' + DROPOUT.AT_F1'),
                VoltagesOffset = 'GBVars.VoltageOffset',
                VoltageTargets = f'ATOM{atom}', #testinput.get("Voltagetarget", "ATOM1,ATOM0"),
                BypassPort = testinput.get("Bypassport", -1),
                #), # The close bracket here indicates that we are done defining VminTC params     
                #r0=pFail(setbin=-47, ret=0, trialaction=Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                #r1 = pPass(ret = 1, trialaction = "Exit"),
                #r2 = pFail(ret = 2, setbin= -47, trialaction = "Next"),
                #r3 = pPass(ret = 3, trialaction = "Exit"),
                #r4 = pFail(ret = 4, setbin= -47, trialaction = "Next"),
                #r5 = pFail(ret = 5, setbin= -47, trialaction = "Next"),
                
                _fitem=Fitem('SAME', edc=testinput.get("ISEDC"),
                             r0 = pFail(setbin = -42, goto="NEXT"),
                             r1 = pPass(goto="NEXT"),
                             r2 = pFail(setbin= -42, goto="NEXT"),
                             r3 = pPass(goto="NEXT"),
                             r4 = pFail(setbin= -42, goto="NEXT"),
                             r5 = pFail(setbin= -42, goto="NEXT")))
                             
    test_list_sa_f1vmax_io_mtt.append(sample_test_sa_f1vmax_io_mtt)

    return test_list_sa_f1vmax_io_mtt

########################################################################
# F5 vmax, OCC vmin search/check test LAYOUT
########################################################################

def get_test_list_atspeed_f5vmax_occ_mtt(
    testtype,
    flow, 
    corner, 
    testinput,
    FlowMatrix,
    corner_id
    ):
       
    # decode MTT test name
    test_list_atspeed_f5vmax_occ_mtt = []
    
    # Get the frequency value from FlowMatrixRule
    frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]
      
    sample_test_atspeed_f5vmax_occ_mtt = \
        NativeMultiTrial(name = f"ATSPEED_ATOM_{testtype}_K_{flow.upper()}_X_AT_MAX_X_F5_FREQ_OCC",
                exitaction = "Continue",
                _comment = f"KILL ATSPEED {flow.upper()}",
                trialvar = "CPU_TRIALS::FlowDomain.ATOM_TOP",
                template = VminTC(name = f'"ATSPEED_ATOM_{testtype}_K_{flow.upper()}_X_AT_MAX_" + ' + Spec(f"__shared__::Corners.AT_{corner_id}") + '+ "_" +' + Spec(f"__shared__::FreqInMHZ.AT_{corner_id}") + f' + "_OCC"',
                Patlist = testinput.get("Patlist", f'scn_arw_vmax{corner.lower()}xat_hptp1600_12r4t_edt_atspeed_occ_classhvm_list'),
                LevelsTc = 'SCN_ATOM_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNATOM_OVERRIDE_nom',
                TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48")'),
                #PostInstance = '',
                BaseNumbers = AUTO,
                CornerIdentifiers = "", #TrialParamSpec(f'SCN_ATOM_CX48_corneridentifier.AT_C5_M{atom}'),
                DtsConfiguration = 'ALL_CDIE_C48_N2P_NONE_CORE',
                EndVoltageLimits = Spec(f'__shared__::FlowMatrixSingular.AT_VMAX_VALUE'),
                ExecutionMode = testinput.get("executionmode", "SearchWithScoreboard"),
                #FailCaptureCount = Spec("toInteger(999)"),
                FeatureSwitchSettings =  'fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters',
                LogLevel = "Disabled",
				SetPointsPlistMode = "Local",
                FivrCondition = 'NOM',
                FivrConditionPlistParamName = "Patlist",
                #FlowIndexCallbackName = '',
                FlowIndex = Spec(f"__shared__::FlowMatrixSingular.FlowIndex"),
                ForwardingMode = 'Input',
                InitialMaskBits = '', #testinput.get("initialmaskbit", ""),
                LimitGuardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
                #MaskPins = '',
                PatternNameCounterIndexes = '1,2,3,4,5,6,7',
                PinMap = 'NVL_SCN_ATOM',
                RecoveryMode =  'NoRecovery', 
                RecoveryOptions = TrialParamSpec(f'__shared__::Recovery.MTT_recovery_opt_AT'), #'CLASS_NVL_S28C_8A', 
                RecoveryTrackingIncoming = 'ACRM1,ACRM0',
                RecoveryTrackingOutgoing = 'ACRM1,ACRM0',
                ScoreboardEdgeTicks = Spec("toInteger(__shared__::Specs.VMX_EDGE_TICK)"),
                #ScoreboardPerPatternFails = 72,
                MaxFailsNum = Spec("toInteger(__shared__::Specs.VMX_MAX_FAILS)"),
                SetPointsPlistParamName = 'Patlist',
                SetPointsPreInstance= TrialParamSpec(f'SCN_ATOM_CX48_Specs.N2P48_PreInst_F5_VMAX'),
                SetPointsPostInstance= "CDIE_ATOM:nblctrl_cdie_atom_l2:nblon",
                #SetPointsPostInstance= '',
                #StartVoltagesForRetry = TrialParamSpec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetryF5 , ["","",""])'),
			    #StartVoltagesOffset = TrialParamSpec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffsetF5 , ["","",""])'),
                StartVoltages = Spec(f'__shared__::FlowMatrixSingular.AT_VMAX_VALUE'),
                StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.AT_SEARCH_RESOLUTION)'),
                TestMode = testinput.get("Testmode", ""),
                VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions "' + f' + DROPOUT.AT_F5'),
                #VoltagesOffset = 'GBVars.VoltageOffset',
                VoltageTargets = "ATOM1,ATOM0",
                BypassPort = testinput.get("Bypassport", -1),
                ), # The close bracket here indicates that we are done defining VminTC params     
                r0=pFail(setbin=-47, ret=0, trialaction= "Exit"),
                r1 = pPass(ret = 1, trialaction = "Exit"),
                r2 = pFail(ret = 2, setbin= -47, trialaction = "Exit"),
                r3 = pPass(ret = 3, trialaction = "Exit"),
                r4 = pFail(ret = 4, setbin= -47, trialaction = "Exit"),
                r5 = pFail(ret = 5, setbin= -47, trialaction = "Exit"),             
                _fitem=Fitem('SAME', edc=testinput.get("ISEDC"),
                             r0 = pFail(setbin = -47, ret=0),
                             r1 = pPass(goto="NEXT"),
                             r2 = pFail(setbin= -47, ret=0),
                             r3 = pPass(goto="NEXT"),
                             r4 = pFail(setbin= -47, ret=0),
                             r5 = pFail(setbin= -47, ret=0)))
                             
    test_list_atspeed_f5vmax_occ_mtt.append(sample_test_atspeed_f5vmax_occ_mtt)

    return test_list_atspeed_f5vmax_occ_mtt

########################################################################
# F5 vmax, IO vmin search/check test LAYOUT
########################################################################

def get_test_list_atspeed_f5vmax_io_mtt(
    testtype,
    flow, 
    corner, 
    atom,
    testinput,
    FlowMatrix,
    corner_id,
    recoverytestflag=False
    ):
       
    # decode MTT test name
    test_list_atspeed_f5vmax_io_mtt = []
    
    # Get the frequency value from FlowMatrixRule
    frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]
      
    sample_test_atspeed_f5vmax_io_mtt = \
        NativeMultiTrial(name = f"ATSPEED_ATOM_{testtype}_K_{flow.upper()}_X_AT_MAX_X_F5_FREQ_M{atom}",
                exitaction = "Continue",
                _comment = f"KILL ATSPEED {flow.upper()}",
                trialvar = "CPU_TRIALS::FlowDomain.ATOM_TOP",
                template = VminTC(name = f'"ATSPEED_ATOM_{testtype}_K_{flow.upper()}_X_AT_MAX_" + ' + Spec(f"__shared__::Corners.AT_{corner_id}") + '+ "_" +' + Spec(f"__shared__::FreqInMHZ.AT_{corner_id}") + f' + "_M{atom}"',
                Patlist = testinput.get("Patlist", f"scn_arw_vmax{corner.lower()}xat_hptp1600_4r4t_edt_atspeed_m{atom}_classhvm_list"),
                LevelsTc = 'SCN_ATOM_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNATOM_OVERRIDE_nom',
                TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48")'),
                #PreInstance = '',
                #PostInstance = '',
                BaseNumbers = AUTO,
                CornerIdentifiers = "", #TrialParamSpec(f'SCN_ATOM_CX48_corneridentifier.AT_C5_M{atom}'),
                DtsConfiguration = 'ALL_CDIE_C48_N2P_NONE_CORE',
                EndVoltageLimits = Spec(f'__shared__::FlowMatrixSingular.AT_VMAX_VALUE'),
                ExecutionMode = testinput.get("executionmode", "SearchWithScoreboard"),
                #FailCaptureCount = Spec("toInteger(999)"),
                FeatureSwitchSettings =  'fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters',
                LogLevel = "Disabled",
				SetPointsPlistMode = "Local",
                FivrCondition = 'NOM',
                FivrConditionPlistParamName = "Patlist",
                #FlowIndexCallbackName = '',
                FlowIndex = Spec(f"__shared__::FlowMatrixSingular.FlowIndex"),
                ForwardingMode = 'Input',
                InitialMaskBits = '0', #testinput.get("initialmaskbit", ""),
                LimitGuardband = Spec(f'toString(__shared__::GBVars.LimitGuardband)'),
                #MaskPins = '',
                PatternNameCounterIndexes = '1,2,3,4,5,6,7',
                PinMap = f'ATOM{atom}_SCAN', #'ATOM3_SCAN,ATOM2_SCAN,ATOM1_SCAN,ATOM0_SCAN',
                RecoveryMode =  'NoRecovery', 
                RecoveryOptions = TrialParamSpec(f'__shared__::Recovery.MTT_recovery_opt_AT'), #'CLASS_NVL_S28C_8A', 
                RecoveryTrackingIncoming = f'ACRM{atom}',
                RecoveryTrackingOutgoing = f'ACRM{atom}',
                ScoreboardEdgeTicks = Spec("toInteger(__shared__::Specs.VMX_EDGE_TICK)"),
                #ScoreboardPerPatternFails = 72,
                MaxFailsNum = Spec("toInteger(__shared__::Specs.VMX_MAX_FAILS)"),
                SetPointsPlistParamName = 'Patlist',
                #SetPointsPreInstance= TrialParamSpec(f'PSPRE.AT_{corner}+' f'","+' f'"MCdrv:atomfreq_0:"' +Spec(f"+__shared__::FreqValues.AT_{corner_id}+")+'"GHz"'),
                SetPointsPreInstance= TrialParamSpec(f'PSPRE.AT_{corner}+' f'","+' f'"MCdrv:atomfreq_0:"' +Spec(f"+__shared__::FreqValues.AT_{corner_id}+")+'"GHz,CDIE_ATOM:nblctrl_cdie_atom_l2:nbloff"'),
                #SetPointsPostInstance= '',
                SetPointsPostInstance= "CDIE_ATOM:nblctrl_cdie_atom_l2:nblon",
                StartVoltagesForRetry = TrialParamSpec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetryF5 , ["","",""])'),
			    StartVoltagesOffset = TrialParamSpec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffsetF5 , ["","",""])'),
                StartVoltages = Spec(f'__shared__::FlowMatrixSingular.AT_VMAX_VALUE'),
                StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.AT_SEARCH_RESOLUTION)'),
                TestMode = testinput.get("Testmode", ""),
                VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions "' + f' + DROPOUT.AT_F5'),
                #VoltagesOffset = 'GBVars.VoltageOffset',
                VoltageTargets = f'ATOM{atom}', #testinput.get("Voltagetarget", "ATOM1,ATOM0"),
                BypassPort = testinput.get("Bypassport", -1),
                ), # The close bracket here indicates that we are done defining VminTC params     
                r0=pFail(setbin=-47, ret=0, trialaction= Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r1 = pPass(ret = 1, trialaction = "Exit"),
                r2 = pFail(ret = 2, setbin= -47, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r3 = pPass(ret = 3, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r4 = pFail(ret = 4, setbin= -47, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r5 = pFail(ret = 5, setbin= -47, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),              
                _fitem=Fitem('SAME', edc=testinput.get("ISEDC"),
                             r0 = pFail(setbin = -47, goto="NEXT"),
                             r1 = pPass(goto="NEXT"),
                             r2 = pFail(setbin= -47, goto="NEXT"),
                             r3 = pPass(goto="NEXT"),
                             r4 = pFail(setbin= -47, goto="NEXT"),
                             r5 = pFail(setbin= -47, goto="NEXT")))
                             
    test_list_atspeed_f5vmax_io_mtt.append(sample_test_atspeed_f5vmax_io_mtt)

    return test_list_atspeed_f5vmax_io_mtt


########################################################################
# FMIN MTT/FF OCC vmin search/check test LAYOUT
########################################################################

def get_test_list_atspeed_fmin_occ_mtt(
    testtype,
    flow, 
    corner, 
    testinput,
    FlowMatrix
    ):
       
    # decode MTT test name
    test_list_atspeed_fmin_occ_mtt = []
    
    # Get the frequency value from FlowMatrixRule
    frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]
      
    sample_test_atspeed_fmin_occ_mtt = \
        NativeMultiTrial(name = f"ATSPEED_ATOM_{testtype}_K_{flow.upper()}_X_AT_{corner.upper()}_X_FREQ_OCC",
                exitaction = "Continue",
                _comment = f"KILL ATSPEED {flow.upper()}",
                trialvar = "CPU_TRIALS::FlowDomain.ATOM",
                template = VminTC(name = f'"ATSPEED_ATOM_{testtype}_K_{flow.upper()}_X_AT_{corner.upper()}_" + ' + Spec(f"__shared__::CustomFlowMatrixSpecs.{FlowMatrix}_MHz") + f' + "_OCC"',
                Patlist = f'scn_arw_{flow.lower()}_hptp1600_12r4t_edt_atspeed_occ_classhvm_list',
                LevelsTc = 'SCN_ATOM_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNATOM_OVERRIDE_nom',
                TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts800_tstprtclk400_tck50_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts800_tstprtclk400_tck50_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts800_tstprtclk400_tck50_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts800_tstprtclk400_tck50_SCNATOM48")') if "FMINXAT" in flow else Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48")'),
                PreInstance = '',
                PostInstance = '',
                BaseNumbers = AUTO,
                CornerIdentifiers = 'AT1@F1,AT0@F1',
                DtsConfiguration = 'ALL_CDIE_C48_N2P_NONE_CORE',
                EndVoltageLimits = Spec(f'__shared__::FlowMatrixSingular.AT_LFM_VMIN_RAIN_KILL'),
                ExecutionMode = testinput.get("executionmode", "SearchWithScoreboard"),
                FeatureSwitchSettings = 'fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters',
                LogLevel = "Disabled",
				SetPointsPlistMode = "Local",
                FivrCondition = 'NOM',
                FlowIndexCallbackName = '',
                FlowIndex = TrialParamSpec(f"__shared__::FlowMatrix.FlowIndex"),
                ForwardingMode = 'Input',
                InitialMaskBits = '', #testinput.get("initialmaskbit", ""),
                LimitGuardband = Spec(f'toString(__shared__::GBVars.FminLimitGuardband)'),
                MaskPins = '',
                PatternNameCounterIndexes = '1,2,3,4,5,6,7',
                PinMap = 'NVL_SCN_ATOM', #'ATOM3_SCAN,ATOM2_SCAN,ATOM1_SCAN,ATOM0_SCAN',
                RecoveryMode = 'NoRecovery', 
                RecoveryOptions = '', #Spec(f'__shared__::Recovery_Single.F1F4_recovery_opt_AT'),
                RecoveryTrackingIncoming = 'ACRM1,ACRM0',
                RecoveryTrackingOutgoing = '', #f'ACRM{atom}',
                ScoreboardEdgeTicks = Spec("toInteger(__shared__::Specs.CHK_EDGE_TICK)"),
                #ScoreboardPerPatternFails = 72,
                MaxFailsNum = Spec("toInteger(__shared__::Specs.CHK_MAX_FAILS)"),
                SetPointsPlistParamName = 'Patlist',
                SetPointsPreInstance= Spec(f'SCN_ATOM_CX48_Specs.N2P48_PreInst_FMIN'),
                SetPointsPostInstance= Spec(f'PSPOST.AT_{corner}'),
                StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
			    StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
                StartVoltages = Spec(f'__shared__::FlowMatrixSingular.AT_LOW_SEARCH_VALUE'),
                StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.AT_SEARCH_RESOLUTION)'),
                TestMode = testinput.get("Testmode", "MultiVmin"),
                #VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions "' + f' + DROPOUT.AT_{corner}'),
                VoltageConverter = Spec(f'"--railconfigurations CDIE_L2_NBLCTRL1 CDIE_L2_NBLCTRL0 --dlvrpins VCCIA --expressions "' + f' + DROPOUT.AT_{corner}'),
                VoltagesOffset = 'GBVars.VoltageOffset',
                VoltageTargets = "ATOM1,ATOM0",
                BypassPort = testinput.get("Bypassport", -1),
                ), # The close bracket here indicates that we are done defining VminTC params     
                r0=pFail(setbin=-47, ret=0, trialaction= Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r1 = pPass(ret = 1, trialaction = "Exit"),
                r2 = pFail(ret = 2, setbin= -47, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r3 = pPass(ret = 3, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r4 = pFail(ret = 4, setbin= -47, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r5 = pFail(ret = 5, setbin= -47, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                
                _fitem=Fitem('SAME', edc= testinput.get("ISEDC"),
                             r0 = pFail(setbin = -47, goto="NEXT"),
                             r1 = pPass(ret = 1),
                             r2 = pFail(setbin= -47, goto="NEXT"),
                             r3 = pPass(ret = 1),
                             r4 = pFail(setbin= -47, goto="NEXT"),
                             r5 = pFail(setbin= -47, goto="NEXT")))
                             
    test_list_atspeed_fmin_occ_mtt.append(sample_test_atspeed_fmin_occ_mtt)

    return test_list_atspeed_fmin_occ_mtt

def get_test_list_fminffocc(
    testtype,
    flow, 
    corner, 
    atom,
    testinput,
    recoverytestflag=False
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_fminffocc = []	
    sample_test_fminffocc = \
        VminTC(name=f"ATSPEED_ATOM_SB_K_{flow}_X_AT_NOM_X_OCC_FF_SEARCH",
               Patlist = f'scn_arw_{flow.lower()}_hptp1600_12r4t_edt_atspeed_occ_classhvm_list',
               LevelsTc = 'SCN_ATOM_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNATOM_OVERRIDE_nom',
               TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts800_tstprtclk400_tck50_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts800_tstprtclk400_tck50_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts800_tstprtclk400_tck50_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts800_tstprtclk400_tck50_SCNATOM48")') if "FMINXAT" in flow else Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48")'),
               PreInstance = '',
               PostInstance = '',
               BaseNumbers = AUTO,
               CornerIdentifiers = '',
               DtsConfiguration = 'ALL_CDIE_C48_N2P_NONE_CORE',
               EndVoltageLimits = Spec(f'__shared__::FlowMatrixSingular.AT_LFM_VMIN_RAIN_KILL'),
               ExecutionMode = "SearchWithScoreboard",
               FeatureSwitchSettings = 'fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters',
               LogLevel = "Disabled",
			   SetPointsPlistMode = "Local",
               FivrCondition = 'NOM',
               FlowIndexCallbackName = '',
               FlowIndex = Spec(f"__shared__::FlowMatrixSingular.FlowIndex"),
               ForwardingMode = 'Input',
               InitialMaskBits = '',
               #LimitGuardband = 'GBVars.FminLimitGuardband',
               MaskPins = '',
               PatternNameCounterIndexes = '1,2,3,4,5,6,7',
               PinMap = 'NVL_SCN_ATOM',
               RecoveryMode = 'NoRecovery', 
               RecoveryOptions = '', #Spec(f'__shared__::Recovery_Single.F1F4_recovery_opt_AT'),
               RecoveryTrackingIncoming = 'ACRM1,ACRM0',
               RecoveryTrackingOutgoing = '', #f'ACRM{atom}',
               ScoreboardEdgeTicks = Spec("toInteger(__shared__::Specs.CHK_EDGE_TICK)"),
               #ScoreboardPerPatternFails = 72,
               MaxFailsNum = Spec("toInteger(__shared__::Specs.CHK_MAX_FAILS)"),
               SetPointsPlistParamName = 'Patlist',
               SetPointsPreInstance= Spec(f'SCN_ATOM_CX48_Specs.N2P48_PreInst_FMIN'),
               SetPointsPostInstance= Spec(f'PSPOST.AT_{corner}'),
               StartVoltages = Spec(f'__shared__::FlowMatrixSingular.AT_LOW_SEARCH_VALUE'),
               StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
               StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
               StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.AT_SEARCH_RESOLUTION)'),
               TestMode = "MultiVmin",
               #VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions "' + f' + DROPOUT.AT_{corner}'),
               VoltageConverter = Spec(f'"--railconfigurations CDIE_L2_NBLCTRL1 CDIE_L2_NBLCTRL0 --dlvrpins VCCIA --expressions "' + f' + DROPOUT.AT_{corner}'),
               VoltagesOffset = 'GBVars.VoltageOffset',
               VoltageTargets = "ATOM1,ATOM0",
               BypassPort = -1,
               _fitem=Fitem('SAME',
               edc= True,
               r0=pFail(setbin = -47, ret=0),
               r1=pPass(ret=0),
               r2=pFail(setbin = -47, ret=0),
               r3=pPass(ret=0),
               r4=pFail(setbin = -47, ret=0),
               r5=pFail(setbin = -47, ret=0)))

    test_listt_fminffocc.append(sample_test_fminffocc)
    
    return test_listt_fminffocc

########################################################################
# FMIN MTT IO vmin search/check test LAYOUT
########################################################################

def get_test_list_atspeed_fmin_io_mtt(
    testtype,
    flow, 
    corner, 
    atom,
    testinput,
    FlowMatrix,
    recoverytestflag=False
    ):
       
    # decode MTT test name
    test_list_atspeed_fmin_io_mtt = []
    
    # Get the frequency value from FlowMatrixRule
    frequency_value = FlowMatrixRule[f"{FlowMatrix}_MHz"]
      
    sample_test_atspeed_fmin_io_mtt = \
        NativeMultiTrial(name = f"ATSPEED_ATOM_{testtype}_K_{flow.upper()}_X_AT_{corner.upper()}_X_FREQ_M{atom}",
                exitaction = "Continue",
                _comment = f"KILL ATSPEED {flow.upper()}",
                trialvar = "CPU_TRIALS::FlowDomain.ATOM",
                template = VminTC(name = f'"ATSPEED_ATOM_{testtype}_K_{flow.upper()}_X_AT_{corner.upper()}_" + ' + Spec(f"__shared__::CustomFlowMatrixSpecs.{FlowMatrix}_MHz") + f' + "_M{atom}"',
                Patlist = testinput.get("Patlist", f"scn_arw_{flow.lower()}_hptp1600_4r4t_edt_atspeed_m{atom}_classhvm_list"),
                LevelsTc = 'SCN_ATOM_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNATOM_OVERRIDE_nom',
                TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts800_tstprtclk400_tck50_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts800_tstprtclk400_tck50_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts800_tstprtclk400_tck50_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts800_tstprtclk400_tck50_SCNATOM48")') if "FMINXAT" in flow else Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48")'),
                PreInstance = '',
                PostInstance = '',
                BaseNumbers = AUTO,
                CornerIdentifiers = f'AT{atom}@F1',
                DtsConfiguration = 'ALL_CDIE_C48_N2P_NONE_CORE',
                EndVoltageLimits = Spec(f'__shared__::FlowMatrixSingular.AT_LFM_VMIN_RAIN_KILL'),
                ExecutionMode = testinput.get("executionmode", "SearchWithScoreboard"),
                FeatureSwitchSettings = 'fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters',
                LogLevel = "Disabled",
				SetPointsPlistMode = "Local",
                FivrCondition = 'NOM',
                FlowIndexCallbackName = '',
                FlowIndex = TrialParamSpec(f"__shared__::FlowMatrix.FlowIndex"),
                ForwardingMode = 'Input',
                InitialMaskBits = '0', #testinput.get("initialmaskbit", ""),
                LimitGuardband = Spec(f'toString(__shared__::GBVars.FminLimitGuardband)'),
                MaskPins = '',
                PatternNameCounterIndexes = '1,2,3,4,5,6,7',
                PinMap = f'ATOM{atom}_SCAN', #'ATOM3_SCAN,ATOM2_SCAN,ATOM1_SCAN,ATOM0_SCAN',
                RecoveryMode = 'NoRecovery', 
                RecoveryOptions = '', #Spec(f'__shared__::Recovery_Single.F1F4_recovery_opt_AT'),
                RecoveryTrackingIncoming = f'ACRM{atom}',
                RecoveryTrackingOutgoing = '', #f'ACRM{atom}',
                ScoreboardEdgeTicks = Spec("toInteger(__shared__::Specs.CHK_EDGE_TICK)"),
                #ScoreboardPerPatternFails = 72,
                MaxFailsNum = Spec("toInteger(__shared__::Specs.CHK_MAX_FAILS)"),
                SetPointsPlistParamName = 'Patlist',
                SetPointsPreInstance= Spec(f'PSPRE.AT_{corner}+' f'","+' f'"MCdrv:atomfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.{FlowMatrix}+")+'"GHz"'),
                SetPointsPostInstance= Spec(f'PSPOST.AT_{corner}'),
                StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
			    StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
                StartVoltages = Spec(f'__shared__::FlowMatrixSingular.AT_LOW_SEARCH_VALUE'),
                StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.AT_SEARCH_RESOLUTION)'),
                TestMode = testinput.get("Testmode", ""),
                #VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions "' + f' + DROPOUT.AT_{corner}'),
                VoltageConverter = Spec(f'"--railconfigurations CDIE_L2_NBLCTRL{atom} --dlvrpins VCCIA --expressions "' + f' + DROPOUT.AT_{corner}'),
                VoltagesOffset = 'GBVars.VoltageOffset',
                VoltageTargets = f'ATOM{atom}', #testinput.get("Voltagetarget", "ATOM1,ATOM0"),
                BypassPort = testinput.get("Bypassport", -1),
                ), # The close bracket here indicates that we are done defining VminTC params     
                r0=pFail(setbin=-47, ret=0, trialaction= Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r1 = pPass(ret = 1, trialaction = "Exit"),
                r2 = pFail(ret = 2, setbin= -47, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r3 = pPass(ret = 3, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r4 = pFail(ret = 4, setbin= -47, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                r5 = pFail(ret = 5, setbin= -47, trialaction = Spec('__shared__::TpRule.MTT_Rule("Next","Exit")')),
                
                _fitem=Fitem('SAME', edc=testinput.get("ISEDC"),
                             r0 = pFail(setbin = -47, goto="NEXT"),
                             r1 = pPass(ret = 1),
                             r2 = pFail(setbin= -47, goto="NEXT"),
                             r3 = pPass(ret = 1),
                             r4 = pFail(setbin= -47, goto="NEXT"),
                             r5 = pFail(setbin= -47, goto="NEXT")))
                             
    test_list_atspeed_fmin_io_mtt.append(sample_test_atspeed_fmin_io_mtt)

    return test_list_atspeed_fmin_io_mtt

def get_test_list_fminffio(
    testtype,
    flow, 
    corner, 
    atom,
    testinput,
    recoverytestflag=False
    ):
	
   # Create an empty list that will contain the final list of the test
    test_listt_fminffio = []	
    sample_test_fminffio = \
        VminTC(name=f"ATSPEED_ATOM_SB_K_{flow}_X_AT_NOM_X_M{atom}_FF_SEARCH",
               Patlist = f"scn_arw_{flow.lower()}_hptp1600_4r4t_edt_atspeed_m{atom}_classhvm_list",
               LevelsTc = 'SCN_ATOM_CX48::cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_SCNATOM_OVERRIDE_nom',
               TimingsTc = Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts800_tstprtclk400_tck50_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts800_tstprtclk400_tck50_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts800_tstprtclk400_tck50_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts800_tstprtclk400_tck50_SCNATOM48")') if "FMINXAT" in flow else Spec(f'__shared__::TpRule.If_C48_DS_AX_M("SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48DS","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48","SCN_ATOM_CX48::cpu_hvm_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48M","SCN_ATOM_CX48::cpu_fun_timing_mts1500_tstprtclk750_tck93p75_SCNATOM48")'),
               PreInstance = '',
               PostInstance = '',
               BaseNumbers = AUTO,
               CornerIdentifiers = '',
               DtsConfiguration = 'ALL_CDIE_C48_N2P_NONE_CORE',
               EndVoltageLimits = Spec(f'__shared__::FlowMatrixSingular.AT_LFM_VMIN_RAIN_KILL'),
               ExecutionMode = "SearchWithScoreboard",
               FeatureSwitchSettings = 'fivr_mode_on,disable_masked_targets,print_per_target_increments,print_scoreboard_counters',
               LogLevel = "Disabled",
			   SetPointsPlistMode = "Local",
               FivrCondition = 'NOM',
               FlowIndexCallbackName = '',
               FlowIndex = Spec(f"__shared__::FlowMatrixSingular.FlowIndex"),
               ForwardingMode = 'Input',
               InitialMaskBits = '0',
               #LimitGuardband = 'GBVars.FminLimitGuardband',
               MaskPins = '',
               PatternNameCounterIndexes = '1,2,3,4,5,6,7',
               PinMap = f'ATOM{atom}_SCAN',
               RecoveryMode = 'NoRecovery', 
               RecoveryOptions = '', #Spec(f'__shared__::Recovery_Single.F1F4_recovery_opt_AT'),
               RecoveryTrackingIncoming = f'ACRM{atom}',
               RecoveryTrackingOutgoing = '', #f'ACRM{atom}',
               ScoreboardEdgeTicks = Spec("toInteger(__shared__::Specs.CHK_EDGE_TICK)"),
               #ScoreboardPerPatternFails = 72,
               MaxFailsNum = Spec("toInteger(__shared__::Specs.CHK_MAX_FAILS)"),
               SetPointsPlistParamName = 'Patlist',
               SetPointsPreInstance= Spec(f'PSPRE.AT_{corner}+' f'","+' f'"MCdrv:atomfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.AT_FMIN+")+'"GHz"'),
               SetPointsPostInstance= Spec(f'PSPOST.AT_{corner}'),
               StartVoltages = Spec(f'__shared__::FlowMatrixSingular.AT_LOW_SEARCH_VALUE'),
               StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
               StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
               StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.AT_SEARCH_RESOLUTION)'),
               TestMode = "SingleVmin",
               VoltageConverter = Spec(f'"--dlvrpins VCCIA --expressions "' + f' + DROPOUT.AT_{corner}'),
               VoltagesOffset = 'GBVars.VoltageOffset',
               VoltageTargets = f'ATOM{atom}',
               BypassPort = 1,
               _fitem=Fitem('SAME',
               edc= True,
               r0=pFail(setbin = -47, goto="NEXT"),
               r1=pPass(ret=1),
               r2=pFail(setbin = -47, goto="NEXT"),
               r3=pPass(ret=1),
               r4=pFail(setbin = -47, goto="NEXT"),
               r5=pFail(setbin = -47, goto="NEXT")))

    test_listt_fminffio.append(sample_test_fminffio)
    
    return test_listt_fminffio




    
#################################################################################
#							INIT SUBFLOWX LAYOUT
#
#	- INIT flow will have pinmap & dierecovery related tests in 
#
#################################################################################
INIT_FLOW = "INIT"

INIT_PATMOD_TLI = {"Bypassport": -1, "ISEDC": True}
INIT_PATMOD = get_test_globalinit_patmod(INIT_FLOW, INIT_PATMOD_TLI)

PINMAP_PARSE_TLI = {"Bypassport": -1, "ISEDC": True}
PINMAP_PARSE = get_test_pinmap_parse(INIT_FLOW, INIT_PATMOD_TLI)

PINMAP_PARSE_OCC_TLI = {"Bypassport": -1, "ISEDC": True}
PINMAP_PARSE_OCC = get_test_pinmap_parse_occ(INIT_FLOW, INIT_PATMOD_TLI)

APEX_TLI = {"Bypassport": -1, "ISEDC": True}
APEX_PARSE = get_test_apex_parse(INIT_FLOW, INIT_PATMOD_TLI)


INIT_SUBFLOW = Flow(f'{MODULE}_INIT',
                                INIT_PATMOD,
                                PINMAP_PARSE_OCC,
                                PINMAP_PARSE,
                                APEX_PARSE,
                              )    

#################################################################################
#							BEGINCPU/SHMOO SUBFLOWX LAYOUT
#
#	- BEGINCPU flow will test 10% STUCKAT content 
#	- Fail flow will include CHAIN, & SPOFI 
#
#################################################################################

BEGINCPU_FLOW = "BEGINCPU"
BEGINCPU_CORNER = "LFM"
DROPOUT1 = "F1"
DROPOUT2 = "F2"
DROPOUT3 = "F3"
DROPOUT4 = "F4"
DROPOUT5 = "F5"
DROPOUT6 = "F6"
DROPOUT7 = "F7"
FMIN_FLOW = "FMINXAT"    
VMAX_FLOW = "VMAXXAT"


flowmatrix = "AT_F1_FREQ"
flowmatrix2 = "AT_F2_FREQ"
flowmatrix3 = "AT_F3_FREQ"
flowmatrix4 = "AT_F4_FREQ"
flowmatrix5 = "AT_F5_FREQ"
flowmatrix6 = "AT_F6_FREQ"
flowmatrix7 = "AT_F7_FREQ"
flowmatrixfmin = "AT_FMIN"


# OCC COMPOSITE TEST LIST
BEGINCPU_VMINTC_STUCKAT_OCC_TLI = {"Bypassport": -1, "Testmode": "MultiVmin", "ISEDC": False}
BEGINCPU_VMINTC_STUCKAT_OCC = get_test_list_stuckat_occ(BEGINCPU_FLOW, BEGINCPU_CORNER, BEGINCPU_VMINTC_STUCKAT_OCC_TLI)
#BEGINCPU_OCC = Flow("BEGINCPU_OCC", BEGINCPU_VMINTC_STUCKAT_OCC)

# ScreenTC
BEGINCPU_SCREENTC_TLI = {"Bypassport": 1, "ISEDC": True}
BEGINCPU_SCREENTC = get_test_list_screentc(BEGINCPU_FLOW, BEGINCPU_SCREENTC_TLI)

# Patconfig
BEGINCPU_PATCONFIG_TLI = {"Bypassport": 1, "ISEDC": True}
BEGINCPU_PATCONFIG = get_test_list_patconfig(BEGINCPU_FLOW, BEGINCPU_PATCONFIG_TLI)

#Shmoo margin check
begin_cpu_testype = "MARGIN_CHECK_1P5_DRV"
begin_cpushmoo_drv_tli = {"Bypassport": 1, "ISEDC": True, "xaxisparam": Spec(f'__shared__::TpRule.If_DS0_DS1_M("cpu_tstprt_i_drv_mul","p_cpu_tstprt_i_drv_mul","p_cpu_tstprt_i_drv_mul","p_cpu_tstprt_i_drv_mul")'), "xaxisrange": "0:0.1:21"}
begincpu_shmoo_drv_margin = get_test_list_chain_shmoodata_margincheck(BEGINCPU_FLOW, BEGINCPU_CORNER, begin_cpu_testype, begin_cpushmoo_drv_tli)

begin_cpu_testype = "MARGIN_CHECK_1P5_STB"
begin_cpushmoo_stb_tli = {"Bypassport": 1, "ISEDC": True, "xaxisparam": Spec(f'__shared__::TpRule.If_DS0_DS1_M("cpu_tstprt_o_stb_mul","p_cpu_tstprt_o_stb_mul","p_cpu_tstprt_o_stb_mul","p_cpu_tstprt_o_stb_mul")'), "xaxisrange": "0:0.1:21"}
begincpu_shmoo_stb_margin = get_test_list_chain_shmoodata_margincheck(BEGINCPU_FLOW, BEGINCPU_CORNER, begin_cpu_testype, begin_cpushmoo_stb_tli)

# Function to create test lists and flows for each module
def create_module_flow(module_index, module_name, flowmatrix):
   # Define TLI settings for each module
    vmintc_stuckat_tli = {
        "Bypassport": -1,
        "Testmode": "Scoreboard",
        #"Voltagetarget": VOLTAGE_TARGETS[module_name],
        "initialmaskbit": N2P48_INITIALMASKBIT[module_name],
        "ISEDC": False,
        #"Preinstance": f"MCdrv:corefreq_VAL_0_8GHz,MCdrv:core0_disable_0:{'enable_core' if module_index == 0 else 'disable_core'},MCdrv:core1_disable_0:{'enable_core' if module_index == 1 else 'disable_core'},MCdrv:core2_disable_0:{'enable_core' if module_index == 2 else 'disable_core'},MCdrv:core3_disable_0:{'enable_core' if module_index == 3 else 'disable_core'}"
    }
    
    vmintc_stuckat = get_test_list_stuckat(BEGINCPU_FLOW, BEGINCPU_CORNER, module_index, vmintc_stuckat_tli, flowmatrix)

    vmintc_chain = get_test_list_chain(BEGINCPU_FLOW, BEGINCPU_CORNER, module_index, vmintc_stuckat_tli)

    spofi_stuckat_tli = {"Bypassport": 1, "ISEDC": True}
    spofi_stuckat = get_test_list_stuckat_spofi(BEGINCPU_FLOW, BEGINCPU_CORNER, module_index, spofi_stuckat_tli)
 
    spofi_chain_tli = {"Bypassport": 1, "ISEDC": True}
    spofi_chain = get_test_list_chain_spofi(BEGINCPU_FLOW, BEGINCPU_CORNER, module_index, spofi_chain_tli)
 
  #  spofi_proxy_tli = {"Bypassport": 1, "ISEDC": True}
  #  spofi_proxy = get_test_list_proxy_spofi(BEGINCPU_FLOW, BEGINCPU_CORNER, module_index, spofi_proxy_tli)

    return Flow(f"BEGINCPU_{module_name}",  vmintc_chain, spofi_stuckat)

    #return Flow(f"BEGINCPU_{module_name}", vmintc_stuckat)

# Create flows for each module
module_flows = [create_module_flow(i, module, flowmatrix) for i, module in enumerate(ATOM_MODULES)]


# Define SHMOO IO tests for each ATOM module (M0 to M3)

#SHMOO_STUCKAT_TLI = {"Bypassport": 1, "ISEDC": True}
#SHMOO_STUCKAT_IO = [
#    get_shmoo_test_iostuckat(BEGINCPU_FLOW, BEGINCPU_CORNER, atom, SHMOO_STUCKAT_TLI, f"M{atom}")
#    for atom in range(2)
#]
#STUCKAT_SHMOO = Flow("STUCKAT_SHMOO", *SHMOO_STUCKAT_IO)
#
SHMOO_CHAIN_TLI = {"Bypassport": 1, "ISEDC": True}
SHMOO_CHAIN_IO = [
    get_test_list_iochain(BEGINCPU_FLOW, BEGINCPU_CORNER, atom, SHMOO_CHAIN_TLI, f"M{atom}")
    for atom in range (2)
 ]
CHAIN_SHMOO = Flow("CHAIN_SHMOO", *SHMOO_CHAIN_IO)
#
#fminxat_flow = "FMINXAT"
#SHMOO_ATSPEED_TLI = {"Bypassport": 1, "ISEDC": True, "timingstc": "cpu_fun_timing_mts400_tstprtclk200_tck50_OVERRIDE", "setpointpre": Spec(f'PSPRE.AT_FMIN+' f'","+' f'"MCdrv:atomfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.AT_FMIN+")+'"GHz"'),}
#atspeed_shmoo = [
#    get_shmoo_test_f1f4ioatspeed(fminxat_flow, DROPOUT1, atom, SHMOO_ATSPEED_TLI, flowmatrix)
#    for atom in range (2)
# ]
#ATSPEED_FMIN = Flow("FMIN_SHMOO", *atspeed_shmoo)
#
#f1xat_flow = "F1XAT"
#SHMOO_ATSPEED_TLI = {"Bypassport": 1, "ISEDC": True}
#atspeed_shmoo = [
#    get_shmoo_test_f1f4ioatspeed(f1xat_flow, DROPOUT1, atom, SHMOO_ATSPEED_TLI, flowmatrix)
#    for atom in range (2)
# ]
#ATSPEED_F1 = Flow("F1_SHMOO", *atspeed_shmoo)
#
#f2xat_flow = "F2XAT"
#SHMOO_ATSPEED_TLI = {"Bypassport": 1, "ISEDC": True}
#atspeed_shmoo = [
#    get_shmoo_test_f1f4ioatspeed(f2xat_flow, DROPOUT2, atom, SHMOO_ATSPEED_TLI, flowmatrix2)
#    for atom in range (2)
# ]
#ATSPEED_F2 = Flow("F2_SHMOO", *atspeed_shmoo)
#
#f3xat_flow = "F3XAT"
#SHMOO_ATSPEED_TLI = {"Bypassport": 1, "ISEDC": True}
#atspeed_shmoo = [
#    get_shmoo_test_f1f4ioatspeed(f3xat_flow, DROPOUT3, atom, SHMOO_ATSPEED_TLI, flowmatrix3)
#    for atom in range (2)
# ]
#ATSPEED_F3 = Flow("F3_SHMOO", *atspeed_shmoo)
#
#f4xat_flow = "F4XAT"
#SHMOO_ATSPEED_TLI = {"Bypassport": 1, "ISEDC": True}
#atspeed_shmoo = [
#    get_shmoo_test_f1f4ioatspeed(f4xat_flow, DROPOUT4, atom, SHMOO_ATSPEED_TLI, flowmatrix4)
#    for atom in range (2)
# ]
#ATSPEED_F4 = Flow("F4_SHMOO", *atspeed_shmoo)
#
#f5xat_flow = "F5XAT"
#SHMOO_ATSPEED_TLI = {"Bypassport": -1, "ISEDC": True}
#atspeed_shmoo = [
#    get_shmoo_test_f5ioatspeed(f5xat_flow, DROPOUT5, atom, SHMOO_ATSPEED_TLI, flowmatrix5)
#    for atom in range (2)
# ]
#ATSPEED_F5 = Flow("F5_SHMOO", *atspeed_shmoo)
#
#f6xat_flow = "F6XAT"
#SHMOO_ATSPEED_TLI = {"Bypassport": 1, "ISEDC": True}
#atspeed_shmoo = [
#    get_shmoo_test_f5ioatspeed(f6xat_flow, DROPOUT6, atom, SHMOO_ATSPEED_TLI, flowmatrix6)
#    for atom in range (2)
# ]
#ATSPEED_F6 = Flow("F6_SHMOO", *atspeed_shmoo)
#
#f7xat_flow = "F7XAT"
#SHMOO_ATSPEED_TLI = {"Bypassport": 1, "ISEDC": True}
#atspeed_shmoo = [
#    get_shmoo_test_f5ioatspeed(f7xat_flow, DROPOUT7, atom, SHMOO_ATSPEED_TLI, flowmatrix7)
#    for atom in range (2)
# ]
#ATSPEED_F7 = Flow("F7_SHMOO", *atspeed_shmoo)
#
#VMAX_SHMOO_TLI = {"Bypassport": 1, "ISEDC": True}
#VMAX_SHMOO_IO = [
#    get_shmoo_test_iostuckat(VMAX_FLOW, BEGINCPU_CORNER, atom, VMAX_SHMOO_TLI, f"M{atom}")
#    for atom in range(2)
#]
#VMAX_SHMOO = Flow("VMAX_SHMOO", *VMAX_SHMOO_IO)
#
#SHMOO_COMPOSITE = Flow("SHMOO", 
#                       Fitem("SAME", STUCKAT_SHMOO, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
#                       Fitem("SAME", CHAIN_SHMOO, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
#                       Fitem("SAME", ATSPEED_F1, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
#                       Fitem("SAME", ATSPEED_FMIN, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
#                       Fitem("SAME", ATSPEED_F2, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
#                       Fitem("SAME", ATSPEED_F3, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
#                       Fitem("SAME", ATSPEED_F4, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
#                       Fitem("SAME", ATSPEED_F5, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
#                       Fitem("SAME", ATSPEED_F6, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
#                       Fitem("SAME", ATSPEED_F7, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
#                       Fitem("SAME", VMAX_SHMOO, r0=pFail(ret=0), r1=pPass(goto="NEXT")))

# Define SHMOO OCC tests for each ATOM module


SHMOO_STUCKAT_TLI = {"Bypassport": 1, "ISEDC": True}
STUCKAT_SHMOO_OCC = get_shmoo_test_occstuckat(BEGINCPU_FLOW, BEGINCPU_CORNER, SHMOO_STUCKAT_TLI)

fminxat_flow = "FMINXAT"
SHMOO_ATSPEED_TLI = {"Bypassport": 1, "ISEDC": True, "setpointpre": Spec(f'PSPRE.AT_FMIN+' f'","+' f'"MCdrv:atomfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.AT_FMIN+")+'"GHz,MCdrv:ringfreq_0:2.4GHz,MCAscn:ratio_modify_OCC:R4_OCC"'),}
ATSPEED_FMIN_OCC = get_shmoo_test_f1f4occatspeed(fminxat_flow, DROPOUT1, SHMOO_ATSPEED_TLI, flowmatrix)

f1xat_flow = "F1XAT"
SHMOO_ATSPEED_TLI = {"Bypassport": 1, "ISEDC": True, "setpointpre": Spec(f'"MCdrv:atomfreq_0:"' +Spec(f"+__shared__::FlowMatrixSingular.AT_F1_FREQ+")+'"GHz,MCdrv:ringfreq_0:2.4GHz,MCAscn:ratio_modify_OCC:R4_OCC"'),}
ATSPEED_F1_OCC = get_shmoo_test_f1f4occatspeed(f1xat_flow, DROPOUT1, SHMOO_ATSPEED_TLI, flowmatrix)

f2xat_flow = "F2XAT"
SHMOO_ATSPEED_TLI = {"Bypassport": 1, "ISEDC": True}
ATSPEED_F2_OCC = get_shmoo_test_f1f4occatspeed(f2xat_flow, DROPOUT2, SHMOO_ATSPEED_TLI, flowmatrix2)

f3xat_flow = "F3XAT"
SHMOO_ATSPEED_TLI = {"Bypassport": 1, "ISEDC": True}
ATSPEED_F3_OCC = get_shmoo_test_f1f4occatspeed(f3xat_flow, DROPOUT3, SHMOO_ATSPEED_TLI, flowmatrix3)

f4xat_flow = "F4XAT"
SHMOO_ATSPEED_TLI = {"Bypassport": 1, "ISEDC": True}
ATSPEED_F4_OCC = get_shmoo_test_f1f4occatspeed(f4xat_flow, DROPOUT4, SHMOO_ATSPEED_TLI, flowmatrix4)


f5xat_flow = "F5XAT"
SHMOO_ATSPEED_TLI = {"Bypassport": 1, "ISEDC": True}
ATSPEED_F5_OCC = get_shmoo_test_f5occatspeed(f5xat_flow, DROPOUT5, SHMOO_ATSPEED_TLI, flowmatrix5)


f6xat_flow = "F6XAT"
SHMOO_ATSPEED_TLI = {"Bypassport": 1, "ISEDC": True}
ATSPEED_F6_OCC = get_shmoo_test_f5occatspeed(f6xat_flow, DROPOUT6, SHMOO_ATSPEED_TLI, flowmatrix6)


f7xat_flow = "F7XAT"
SHMOO_ATSPEED_TLI = {"Bypassport": 1, "ISEDC": True}
ATSPEED_F7_OCC = get_shmoo_test_f5occatspeed(f7xat_flow, DROPOUT7, SHMOO_ATSPEED_TLI, flowmatrix7)


SHMOO_COMPOSITE = Flow("SHMOO", 
                       STUCKAT_SHMOO_OCC,
                       Fitem("SAME", CHAIN_SHMOO, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                       ATSPEED_F1_OCC,
                       ATSPEED_FMIN_OCC,
                       ATSPEED_F2_OCC,
                       ATSPEED_F3_OCC,
                       ATSPEED_F4_OCC,
                       ATSPEED_F5_OCC,
                       ATSPEED_F6_OCC,
                       ATSPEED_F7_OCC)


# BEGINCPU SUBFLOW
BEGINCPU_SUBFLOW = Flow(f'{MODULE}_BEGINCPU',
                     BEGINCPU_VMINTC_STUCKAT_OCC,
                     *[Fitem("SAME", module_flow, r0=pFail(ret=0), r1=pPass(goto="NEXT")) for module_flow in module_flows[:-1]],
                     Fitem("SAME", module_flows[-1], r0=pFail(ret=0), r1=pPass(ret=1)),
                     Fitem("SAME", SHMOO_COMPOSITE, r0=pFail(ret=0), r1=pPass(ret=1)))
                     
                     
                    
##################################################################################
##                         F1-F4 IO/OCC SEARCH SUBFLOWX LAYOUT
##
##   - CHECK flow will test 80% ATSPEED content 
##
##################################################################################

# FlowMatrixRule Definition
FlowMatrixRule = {
    "AT_FMIN_MHz"   : "0400",
    "AT_F1_FREQ_MHz": "1200",
    "AT_F2_FREQ_MHz": "1500",
    "AT_F3_FREQ_MHz": "2400",
    "AT_F4_FREQ_MHz": "3500"

    }

# FlowMatrix Definition
flow_matrix_definitions = {
    "F1": "AT_F1_FREQ",
    "F2": "AT_F2_FREQ",
    "F3": "AT_F3_FREQ",
    "F4": "AT_F4_FREQ"
}

corner_id_definitions = {
    "F1": "C1",
    "F2": "C2",
    "F3": "C3",
    "F4": "C4",
}

# Function to create test lists and flows for each module
def create_module_flow(testtype, flow_name, corner, corner_id, module_index, module_name, flow_matrix):
    # Define TLI settings for each module
    vmintc_atspeed_tli = {
        "Bypassport": 1,
        "Testmode": "SingleVmin",
        #"Voltagetarget": voltage_targets[module_name],
        "initialmaskbit": N2P48_INITIALMASKBIT[module_name],
        "ISEDC": False,
        "Recovery": "NoRecovery",
        #"Preinstance": f"MCdrv:corefreq_VAL_0_8GHz,MCdrv:core0_disable_0:{'enable_core' if module_index == 0 else 'disable_core'},MCdrv:core1_disable_0:{'enable_core' if module_index == 1 else 'disable_core'},MCdrv:core2_disable_0:{'enable_core' if module_index == 2 else 'disable_core'},MCdrv:core3_disable_0:{'enable_core' if module_index == 3 else 'disable_core'}"
    }
    
    vmintc_atspeed = get_test_list_atspeed_f1f4_io_mtt(testtype, flow_name, corner, corner_id, module_index, vmintc_atspeed_tli, flow_matrix)
    #
    #shmoo_atspeed_tli = {"Bypassport": 1, "ISEDC": True}
    #shmoo_atspeed = get_test_list_stuckat_shmoo(flow_name, corner, module_index, shmoo_atspeed_tli) # Here as placeholder, add in Flow if/when needed, 
    #                                                                                                # but be aware, adding these in will cause some conflicts in sbindef file, not enough bins to cater for all. 
    #
    spofi_atspeed_tli = {"Bypassport": 1, "ISEDC": True} 
    spofi_atspeed = get_test_list_atspeed_spofi(flow_name, corner, module_index, spofi_atspeed_tli) # Here as placeholder, add in Flow if/when needed, 
                                                                                                    # but be aware, adding these in will cause some conflicts in sbindef file, not enough bins to cater for all.

    spofi_stuckat_tli = {"Bypassport": 1, "ISEDC": True} 
    spofi_stuckat = get_test_list_stuckat_spofi(flow_name, corner, module_index, spofi_stuckat_tli) # Here as placeholder, add in Flow if/when needed, 
                                                                                                    # but be aware, adding these in will cause some conflicts in sbindef file, not enough bins to cater for all.
	
    return Flow(f"{flow_name}_{module_name}", vmintc_atspeed)

# Function to create subflows
def create_subflow(flow_name, corner, module_name, flow_matrix, corner_id):
    
    # OCC COMPOSITE TEST LIST
    testtype = "VMIN"
    vmintc_atspeed_occ_tli = {"Bypassport": -1, "Testmode": "MultiVmin", "ISEDC": False}
    vmintc_atspeed_occ = get_test_list_atspeed_occ_f1f4_mtt(testtype, flow_name, corner, vmintc_atspeed_occ_tli, flow_matrix)
    #occ = Flow(f"{flow_name}_OCC", vmintc_atspeed_occ)
                    
    # ScreenTC
    #screentc_tli = {"Bypassport": 1, "ISEDC": True}
    #screentc = get_test_list_screentc(flow_name, screentc_tli)

    # Patconfig
    #patconfig_tli = {"Bypassport": 1, "ISEDC": True}
    #patconfig = get_test_list_patconfig(flow_name, patconfig_tli)

    # Create flows for each module
    module_flows = [create_module_flow(testtype, flow_name, corner, corner_id, i, module, flow_matrix) for i, module in enumerate(ATOM_MODULES)]

    # Create the subflow
    subflow = Flow(f'{module_name}_{flow_name}',
                   vmintc_atspeed_occ,
                   #screentc,
                   #patconfig,
                   *[Fitem("SAME", module_flow, r0=pFail(ret=0), r1=pPass(goto="NEXT")) for module_flow in module_flows[:-1]],
                   Fitem("SAME", module_flows[-1], r0=pFail(ret=0), r1=pPass(ret=1)))
    
    return subflow

# Define the subflows
subflows = []
for i in range(1, 4):
    flow_name = f"F{i}XAT"
    corner = f"F{i}"
    flow_matrix = flow_matrix_definitions[corner]
    corner_id = corner_id_definitions[corner]
    subflows.append(create_subflow(flow_name, corner, MODULE, flow_matrix, corner_id))


#################################################################################
#                           F5-F6 IO/OCC SUBFLOWX LAYOUT
#
#   - Consists of F5 & F6 corners flow which will test 100% ATSPEED content in TOP subflow 
#
#################################################################################

# FlowMatrixRule Definition
FlowMatrixRule = {
    "AT_F5_FREQ_MHz": "3600",
    "AT_F6_FREQ_MHz": "4000",
    "AT_F7_FREQ_MHz": "4300"
}
# FlowMatrix Definition
flow_matrix_definitions = {
    "F5": "AT_F5_FREQ",
    "F6": "AT_F6_FREQ",
}
corner_id_definitions = {
    "F5": "C5",
    "F6": "C6",
}
# Function to create test lists and flows for each module
def create_module_flow(testtype, flow_name, corner, module_index, module_name, flow_matrix, corner_id):
    # Define TLI settings for each module
    vmintc_atspeed_tli = {
        "Bypassport": 1,
        "Testmode": "SingleVmin",
        #"executionmode": "Search",
        #"Voltagetarget": voltage_targets[module_name],
        "initialmaskbit": N2P48_INITIALMASKBIT[module_name],
        "ISEDC": False,
        "Recovery": "RecoveryPort",
        #"Preinstance": f"MCdrv:corefreq_VAL_0_8GHz,MCdrv:core0_disable_0:{'enable_core' if module_index == 0 else 'disable_core'},MCdrv:core1_disable_0:{'enable_core' if module_index == 1 else 'disable_core'},MCdrv:core2_disable_0:{'enable_core' if module_index == 2 else 'disable_core'},MCdrv:core3_disable_0:{'enable_core' if module_index == 3 else 'disable_core'}"
    }

    vmintc_atspeed = get_test_list_atspeed_f5f6_io_mtt(testtype, flow_name, corner, module_index, vmintc_atspeed_tli, flow_matrix, corner_id)
    #
    #shmoo_atspeed_tli = {"Bypassport": 1, "ISEDC": True}
    #shmoo_atspeed = get_test_list_stuckat_shmoo(flow_name, corner, module_index, shmoo_atspeed_tli) # Here as placeholder, add in Flow if/when needed, 
    #                                                                                                # but be aware, adding these in will cause some conflicts in sbindef file, not enough bins to cater for all. 
    #

    apextc_tli = {"Bypassport": 1, "initialmaskbit": N2P48_INITIALMASKBIT[module_name], "ISEDC": True}
    apextc = get_test_list_atspeed_f5f6_ioapex(flow_name, corner, module_index, apextc_tli, flow_matrix, corner_id)

    spofi_atspeed_tli = {"Bypassport": 1, "ISEDC": True} 
    spofi_atspeed = get_test_list_atspeed_spofi(flow_name, corner, module_index, spofi_atspeed_tli) # Here as placeholder, add in Flow if/when needed, 
                                                                                                    # but be aware, adding these in will cause some conflicts in sbindef file, not enough bins to cater for all.

    spofi_stuckat_tli = {"Bypassport": 1, "ISEDC": True} 
    spofi_stuckat = get_test_list_stuckat_spofi(flow_name, corner, module_index, spofi_stuckat_tli) # Here as placeholder, add in Flow if/when needed, 
                                                                                                    # but be aware, adding these in will cause some conflicts in sbindef file, not enough bins to cater for all.
	
    return Flow(f"{flow_name}_{module_name}", apextc, vmintc_atspeed)

# Function to create subflows
def create_subflow(testtype, flow_name, corner, module_name, flow_matrix, corner_id):
    
    # OCC COMPOSITE TEST LIST
    testtype = "VMIN"
    vmintc_atspeed_occ_tli = {"Bypassport": -1, "Testmode": "MultiVmin", "ISEDC": False}
    vmintc_atspeed_occ = get_test_list_atspeed_occ_f5f6_mtt(testtype, flow_name, corner, vmintc_atspeed_occ_tli, flow_matrix, corner_id)
    #occ = Flow(f"{flow_name}_OCC", vmintc_atspeed_occ)

    # APEX OCC COMPOSITE TEST LIST
    testtype = "VMIN"
    vmintc_apexatspeed_occ_tli = {"Bypassport": 1, "Testmode": "MultiVmin", "ISEDC": True}
    vmintc_apexatspeed_occ = get_test_list_atspeed_f5f6_occapex(testtype, flow_name, corner, vmintc_apexatspeed_occ_tli, flow_matrix, corner_id)
    #occ = Flow(f"{flow_name}_OCC", vmintc_apexatspeed_occ)
                    
    # Create flows for each module
    #module_flows = [create_module_flow(testtype, flow_name, corner, i, module, flow_matrix, corner_id) for i, module in enumerate(ATOM_MODULES)]

    # Create the subflow
    #subflow = Flow(f'{module_name}_{flow_name}',
    #               vmintc_apexatspeed_occ,
    #               vmintc_atspeed_occ,
    #               
    #               *[Fitem("SAME", module_flow, r0=pFail(ret = 0), r1=pPass(goto="NEXT")) for module_flow in module_flows[:-1]],
    #               Fitem("SAME", module_flows[-1], r0=pFail(ret = 0), r1=pPass(ret=1)))
    #
    #return subflow

# Define the subflows for F5 and F6, only F5 enabled for now
subflows = []
for corner in ["F5"]:
    flow_name = f"{corner}XAT"
    flow_matrix = flow_matrix_definitions[corner]
    corner_id = corner_id_definitions[corner]
    testtype = "VMIN"
    subflows.append(create_subflow(testtype, flow_name, corner, MODULE, flow_matrix, corner_id))


#################################################################################
#                           LTTC F5 IO/OCC SUBFLOWX LAYOUT
#
#   - Subflow for LTTCCPU, F5 corner, ATOM modules M0-M3
#
#################################################################################

flow_name = "LTTCCPUMAX"

# FlowMatrixRule Definition
FlowMatrixRule = {
    "AT_F5_FREQ_MHz": "3600",
}

# FlowMatrix Definition
flow_matrix_definitions = {
    "F5": "AT_F5_FREQ",
}

corner_id_definitions = {
    "F5": "C5",
}

# OCC COMPOSITE TEST LIST
vmintc_atspeed_occ_tli = {"Bypassport": 1, "Testmode": "MultiVmin", "ISEDC": False}
vmintc_atspeed_occ = get_test_list_atspeed_lttcf5_occ_mtt(testtype, flow_name, corner, vmintc_atspeed_occ_tli, flow_matrix, corner_id)
#occ = Flow(f"{flow_name}_OCC", vmintc_atspeed_occ)

def create_module_flow(testtype, flow_name, corner, module_index, module_name, flow_matrix, corner_id):
    """
    Create a Flow for a given module/atom for LTTCCPU subflow.
    """
    vmintc_atspeed_tli = {
        "Bypassport": 1,
        "Testmode": "SingleVmin",
        "initialmaskbit": N2P48_INITIALMASKBIT[module_name],
        "ISEDC": False,
        "Recovery": "RecoveryPort",
    }
    vmintc_atspeed = get_test_list_atspeed_lttcf5_io_mtt(
        testtype, flow_name, corner, module_index, vmintc_atspeed_tli, flow_matrix, corner_id
    )
    return Flow(f"{flow_name}_{module_name}", vmintc_atspeed)

def create_subflow(testtype, flow_name, corner, module_name, flow_matrix, corner_id):
    """
    Create the LTTCCPU subflow for all ATOM_MODULES, without OCC test.
    """
    module_flows = [
        create_module_flow(testtype, flow_name, corner, i, module, flow_matrix, corner_id)
        for i, module in enumerate(ATOM_MODULES)
    ]

    subflow = Flow(
        f"{module_name}_{flow_name}",
        vmintc_atspeed_occ,
        *[
            Fitem("SAME", module_flow, r0=pFail(ret=0), r1=pPass(goto="NEXT"))
            for module_flow in module_flows[:-1]
        ],
        Fitem("SAME", module_flows[-1], r0=pFail(ret=0), r1=pPass(ret=1))
    )
    return subflow

# Define the LTTCCPU subflow
flow_name = "LTTCCPUMAX"
corner = "F5"
testtype = "VMIN"
flow_matrix = flow_matrix_definitions[corner]
corner_id = corner_id_definitions[corner]
LTTCCPU_SUBFLOW = create_subflow(testtype, flow_name, corner, MODULE, flow_matrix, corner_id)

#################################################################################
#							F4XATLO SUBFLOWX LAYOUT
#
#
#################################################################################
# FlowMatrixRule Definition
FlowMatrixRule = {
    "AT_F4_FREQ_MHz": "3500",
    }
# FlowMatrix Definition
flow_matrix_definitions = {
    "F4": "AT_F4_FREQ",
}
corner_id_definitions = {
    "F4": "C4",
}

# Function to create test lists and flows for each module
def create_module_flow(testtype, flow_name, corner, corner_id, module_index, module_name, flow_matrix):
    # Define TLI settings for each module
    vmintc_atspeed_tli = {
        "Bypassport": 1,
        "Testmode": "SingleVmin",
        #"Voltagetarget": voltage_targets[module_name],
        "initialmaskbit": N2P48_INITIALMASKBIT[module_name],
        "ISEDC": False,
        "Recovery": "NoRecovery",
        #"Preinstance": f"MCdrv:corefreq_VAL_0_8GHz,MCdrv:core0_disable_0:{'enable_core' if module_index == 0 else 'disable_core'},MCdrv:core1_disable_0:{'enable_core' if module_index == 1 else 'disable_core'},MCdrv:core2_disable_0:{'enable_core' if module_index == 2 else 'disable_core'},MCdrv:core3_disable_0:{'enable_core' if module_index == 3 else 'disable_core'}"
    }
    
    vmintc_atspeed = get_test_list_atspeed_f1f4_io_mtt(testtype, flow_name, corner, corner_id, module_index, vmintc_atspeed_tli, flow_matrix)
    #
    #shmoo_atspeed_tli = {"Bypassport": 1, "ISEDC": True}
    #shmoo_atspeed = get_test_list_stuckat_shmoo(flow_name, corner, module_index, shmoo_atspeed_tli) # Here as placeholder, add in Flow if/when needed, 
    #                                                                                                # but be aware, adding these in will cause some conflicts in sbindef file, not enough bins to cater for all. 
    #
    spofi_atspeed_tli = {"Bypassport": 1, "ISEDC": True} 
    spofi_atspeed = get_test_list_atspeed_spofi(flow_name, corner, module_index, spofi_atspeed_tli) # Here as placeholder, add in Flow if/when needed, 
                                                                                                    # but be aware, adding these in will cause some conflicts in sbindef file, not enough bins to cater for all.

    spofi_stuckat_tli = {"Bypassport": 1, "ISEDC": True} 
    spofi_stuckat = get_test_list_stuckat_spofi(flow_name, corner, module_index, spofi_stuckat_tli) # Here as placeholder, add in Flow if/when needed, 
                                                                                                    # but be aware, adding these in will cause some conflicts in sbindef file, not enough bins to cater for all.
	
    return Flow(f"{flow_name}_{module_name}", vmintc_atspeed)

# Function to create subflows
def create_subflow(flow_name, corner, module_name, flow_matrix, corner_id):
    
    # OCC COMPOSITE TEST LIST
    testtype = "VMIN"
    vmintc_atspeed_occ_tli = {"Bypassport": -1, "Testmode": "MultiVmin", "ISEDC": False}
    vmintc_atspeed_occ = get_test_list_atspeed_occ_f1f4_mtt(testtype, flow_name, corner, vmintc_atspeed_occ_tli, flow_matrix)
    #occ = Flow(f"{flow_name}_OCC", vmintc_atspeed_occ)
                    
    # ScreenTC
    #screentc_tli = {"Bypassport": 1, "ISEDC": True}
    #screentc = get_test_list_screentc(flow_name, screentc_tli)

    # Patconfig
    #patconfig_tli = {"Bypassport": 1, "ISEDC": True}
    #patconfig = get_test_list_patconfig(flow_name, patconfig_tli)

    # Create flows for each module
    module_flows = [create_module_flow(testtype, flow_name, corner, corner_id, i, module, flow_matrix) for i, module in enumerate(ATOM_MODULES)]

    # Create the subflow
    subflow = Flow(f'{module_name}_{flow_name}',
                   vmintc_atspeed_occ,
                   #screentc,
                   #patconfig,
                   *[Fitem("SAME", module_flow, r0=pFail(ret=0), r1=pPass(goto="NEXT")) for module_flow in module_flows[:-1]],
                   Fitem("SAME", module_flows[-1], r0=pFail(ret=0), r1=pPass(ret=1)))
    
    return subflow

# Define the subflow for F4XATLO
flow_name = "F4XATLO"
corner = "F4"
testtype = "VMIN"
flow_matrix = flow_matrix_definitions[corner]
corner_id = corner_id_definitions[corner]
subflows = [create_subflow(flow_name, corner, MODULE, flow_matrix, corner_id)]

#################################################################################
#							F5XATLO SUBFLOWX LAYOUT
#
#
#################################################################################
# FlowMatrixRule Definition
FlowMatrixRule = {
    "AT_F5_FREQ_MHz": "3600",
    "AT_F6_FREQ_MHz": "4000",
    "AT_F7_FREQ_MHz": "4300"
}
# FlowMatrix Definition
flow_matrix_definitions = {
    "F5": "AT_F5_FREQ",
    "F6": "AT_F6_FREQ",
}
corner_id_definitions = {
    "F5": "C5",
    "F6": "C6",
}
# Function to create test lists and flows for each module
def create_module_flow(testtype, flow_name, corner, module_index, module_name, flow_matrix, corner_id):
    # Define TLI settings for each module
    vmintc_atspeed_tli = {
        "Bypassport": 1,
        "Testmode": "SingleVmin",
        #"executionmode": "Search",
        #"Voltagetarget": voltage_targets[module_name],
        "initialmaskbit": N2P48_INITIALMASKBIT[module_name],
        "ISEDC": False,
        "Recovery": "RecoveryPort",
        #"Preinstance": f"MCdrv:corefreq_VAL_0_8GHz,MCdrv:core0_disable_0:{'enable_core' if module_index == 0 else 'disable_core'},MCdrv:core1_disable_0:{'enable_core' if module_index == 1 else 'disable_core'},MCdrv:core2_disable_0:{'enable_core' if module_index == 2 else 'disable_core'},MCdrv:core3_disable_0:{'enable_core' if module_index == 3 else 'disable_core'}"
    }

    vmintc_atspeed = get_test_list_atspeed_f5f6_io_mtt(testtype, flow_name, corner, module_index, vmintc_atspeed_tli, flow_matrix, corner_id)
    #
    #shmoo_atspeed_tli = {"Bypassport": 1, "ISEDC": True}
    #shmoo_atspeed = get_test_list_stuckat_shmoo(flow_name, corner, module_index, shmoo_atspeed_tli) # Here as placeholder, add in Flow if/when needed, 
    #                                                                                                # but be aware, adding these in will cause some conflicts in sbindef file, not enough bins to cater for all. 
    #

    apextc_tli = {"Bypassport": 1, "initialmaskbit": N2P48_INITIALMASKBIT[module_name], "ISEDC": True}
    apextc = get_test_list_atspeed_f5f6_ioapex(flow_name, corner, module_index, apextc_tli, flow_matrix, corner_id)

    spofi_atspeed_tli = {"Bypassport": 1, "ISEDC": True} 
    spofi_atspeed = get_test_list_atspeed_spofi(flow_name, corner, module_index, spofi_atspeed_tli) # Here as placeholder, add in Flow if/when needed, 
                                                                                                    # but be aware, adding these in will cause some conflicts in sbindef file, not enough bins to cater for all.

    spofi_stuckat_tli = {"Bypassport": 1, "ISEDC": True} 
    spofi_stuckat = get_test_list_stuckat_spofi(flow_name, corner, module_index, spofi_stuckat_tli) # Here as placeholder, add in Flow if/when needed, 
                                                                                                    # but be aware, adding these in will cause some conflicts in sbindef file, not enough bins to cater for all.
	
    return Flow(f"{flow_name}_{module_name}", apextc, vmintc_atspeed)

# Function to create subflows
def create_subflow(testtype, flow_name, corner, module_name, flow_matrix, corner_id):
    
    # OCC COMPOSITE TEST LIST
    testtype = "VMIN"
    vmintc_atspeed_occ_tli = {"Bypassport": -1, "Testmode": "MultiVmin", "ISEDC": False}
    vmintc_atspeed_occ = get_test_list_atspeed_occ_f5f6_mtt(testtype, flow_name, corner, vmintc_atspeed_occ_tli, flow_matrix, corner_id)
    #occ = Flow(f"{flow_name}_OCC", vmintc_atspeed_occ)

    # APEX OCC COMPOSITE TEST LIST
    testtype = "VMIN"
    vmintc_apexatspeed_occ_tli = {"Bypassport": 1, "Testmode": "MultiVmin", "ISEDC": True}
    vmintc_apexatspeed_occ = get_test_list_atspeed_f5f6_occapex(testtype, flow_name, corner, vmintc_apexatspeed_occ_tli, flow_matrix, corner_id)
    #occ = Flow(f"{flow_name}_OCC", vmintc_apexatspeed_occ)
                    
    # Create flows for each module
    module_flows = [create_module_flow(testtype, flow_name, corner, i, module, flow_matrix, corner_id) for i, module in enumerate(ATOM_MODULES)]

    # Create the subflow
    subflow = Flow(f'{module_name}_{flow_name}',
                   vmintc_apexatspeed_occ,
                   vmintc_atspeed_occ,
                   
                   *[Fitem("SAME", module_flow, r0=pFail(ret = 0), r1=pPass(goto="NEXT")) for module_flow in module_flows[:-1]],
                   Fitem("SAME", module_flows[-1], r0=pFail(ret = 0), r1=pPass(ret=1)))
    
    return subflow

# Define the subflow for F5XATLO
flow_name = "F5XATLO"
corner = "F5"
testtype = "VMIN"
flow_matrix = flow_matrix_definitions[corner]
corner_id = corner_id_definitions[corner]
subflows = [create_subflow(testtype, flow_name, corner, MODULE, flow_matrix, corner_id)]

#################################################################################
#							VMAXXAT SUBFLOWX LAYOUT
#
#
#################################################################################
atom0 = 0
atom1 = 1
#atom2 = 2
#atom3 = 3
testtype = "SB"
flow_name = "VMAXXAT" 
cornerf1 = "F1" 
cornerf5 = "F5"

# FlowMatrixRule Definition
FlowMatrixRule = {
    "AT_F1_FREQ_MHz": "1200",
    "AT_F5_FREQ_MHz": "3600"
    }

# FlowMatrix Definition
flow_matrix_definitions = {
    "F1": "AT_F1_FREQ",
    "F5": "AT_F5_FREQ",
}

corner_id_definitions = {
    "F5": "C5",
}

#SA_F1 test list
vmaxxat_vmintc_sa_occ_tli = {"Bypassport": -1, "Testmode": "MultiVmin", "ISEDC": False, "Patlist": "scn_arw_vmaxf1xat_hptp1600_12r4t_edt_stuckat_occ_classhvm_list",}
vmaxxat_vmintc_sa_occ = get_test_list_sa_f1vmax_occ_mtt(testtype, flow_name, cornerf1, vmaxxat_vmintc_sa_occ_tli, flow_matrix)
vmintc_sa_tli_0 = {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": True, "initialmaskbit": "10", "Patlist": "scn_arw_vmaxf1xat_hptp1600_4r4t_edt_stuckat_m0_classhvm_list",}
vmintc_sa_0 = get_test_list_sa_f1vmax_io_mtt(testtype, flow_name, cornerf1, atom0, vmintc_sa_tli_0, flow_matrix)
vmintc_sa_tli_1 = {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": True, "initialmaskbit": "01", "Patlist": "scn_arw_vmaxf1xat_hptp1600_4r4t_edt_stuckat_m1_classhvm_list",}
vmintc_sa_1 = get_test_list_sa_f1vmax_io_mtt(testtype, flow_name, cornerf1, atom1, vmintc_sa_tli_1, flow_matrix)
# vmintc_sa_tli_2 = {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": True, "initialmaskbit": "1011", "Patlist": "scn_arw_vmaxf1xat_hptp1600_4r4t_edt_stuckat_m2_classhvm_list",}
# vmintc_sa_2 = get_test_list_sa_f1vmax_io_mtt(testtype, flow_name, cornerf1, atom2, vmintc_sa_tli_2, flow_matrix)
# vmintc_sa_tli_3 = {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": True, "initialmaskbit": "0111", "Patlist": "scn_arw_vmaxf1xat_hptp1600_4r4t_edt_stuckat_m3_classhvm_list",}
# vmintc_sa_3 = get_test_list_sa_f1vmax_io_mtt(testtype, flow_name, cornerf1, atom3, vmintc_sa_tli_3, flow_matrix)


vmaxxat_f1 = Flow("VMAXXAT_F1", vmaxxat_vmintc_sa_occ)

#ATSPEED_F5 test list
vmaxxat_vmintc_atspeed_occ_tli = {"Bypassport": -1, "Testmode": "MultiVmin", "ISEDC": False, "Patlist": "scn_arw_vmaxf5xat_hptp1600_12r4t_edt_atspeed_occ_classhvm_list",}
vmaxxat_vmintc_atspeed_occ = get_test_list_atspeed_f5vmax_occ_mtt(testtype, flow_name, cornerf5, vmaxxat_vmintc_atspeed_occ_tli, flow_matrix, corner_id)
vmintc_atspeed_tli_0 = {"Bypassport": 1, "Testmode": "SingleVmin", "ISEDC": True, "initialmaskbit": "10", "Patlist": "scn_arw_vmaxf5xat_hptp1600_4r4t_edt_atspeed_m0_classhvm_list",}
vmintc_atspeed_0 = get_test_list_atspeed_f5vmax_io_mtt(testtype, flow_name, cornerf5, atom0, vmintc_atspeed_tli_0, flow_matrix, corner_id)
vmintc_atspeed_tli_1 = {"Bypassport": 1, "Testmode": "SingleVmin", "ISEDC": True, "initialmaskbit": "01", "Patlist": "scn_arw_vmaxf5xat_hptp1600_4r4t_edt_atspeed_m1_classhvm_list",}
vmintc_atspeed_1 = get_test_list_atspeed_f5vmax_io_mtt(testtype, flow_name, cornerf5, atom1, vmintc_atspeed_tli_1, flow_matrix, corner_id)
# vmintc_atspeed_tli_2 = {"Bypassport": 1, "Testmode": "SingleVmin", "ISEDC": True, "initialmaskbit": "1011", "Patlist": "scn_arw_vmaxf5xat_hptp1600_4r4t_edt_atspeed_m2_classhvm_list",}
# vmintc_atspeed_2 = get_test_list_atspeed_f5vmax_io_mtt(testtype, flow_name, cornerf5, atom2, vmintc_atspeed_tli_2, flow_matrix, corner_id)
# vmintc_atspeed_tli_3 = {"Bypassport": 1, "Testmode": "SingleVmin", "ISEDC": True, "initialmaskbit": "0111", "Patlist": "scn_arw_vmaxf5xat_hptp1600_4r4t_edt_atspeed_m3_classhvm_list",}
# vmintc_atspeed_3 = get_test_list_atspeed_f5vmax_io_mtt(testtype, flow_name, cornerf5, atom3, vmintc_atspeed_tli_3, flow_matrix, corner_id)

vmaxxat_f5 = Flow("VMAXXAT_F5", vmaxxat_vmintc_atspeed_occ)

# vmaxxat SUBFLOW
vmaxxat_SUBFLOW = Flow(f'{MODULE}_VMAXXAT',
                     Fitem("SAME", vmaxxat_f1, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                     Fitem("SAME", vmaxxat_f5, r0=pFail(ret=0), r1=pPass(ret=1)),
)

#################################################################################
#							ENDCPUMAX SUBFLOWX LAYOUT
#
#
#################################################################################
atom0 = 0
atom1 = 1
atom2 = 2
atom3 = 3
testtype = "SB"
flow_name = "ENDCPUMAX"
cornerf1 = "F1" 
cornerf5 = "F5"

# FlowMatrixRule Definition
FlowMatrixRule = {
    "AT_F1_FREQ_MHz": "1200",
    "AT_F5_FREQ_MHz": "3600"
    }

# FlowMatrix Definition
flow_matrix_definitions = {
    "F1": "AT_F1_FREQ",
    "F5": "AT_F5_FREQ",
}

corner_id_definitions = {
    "F5": "C5",
}

#SA_F1 test list
vmaxxat_vmintc_sa_occ_tli = {"Bypassport": 1, "Testmode": "MultiVmin", "ISEDC": False, "Patlist": "scn_arw_vmaxf1xat_hptp1600_12r4t_edt_stuckat_occ_classhvm_list",}
vmaxxat_vmintc_sa_occ = get_test_list_sa_f1vmax_occ_mtt(testtype, flow_name, cornerf1, vmaxxat_vmintc_sa_occ_tli, flow_matrix)
vmintc_sa_tli_0 = {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": True, "initialmaskbit": "10", "Patlist": "scn_arw_vmaxf1xat_hptp1600_4r4t_edt_stuckat_m0_classhvm_list",}
vmintc_sa_0 = get_test_list_sa_f1vmax_io_mtt(testtype, flow_name, cornerf1, atom0, vmintc_sa_tli_0, flow_matrix)
vmintc_sa_tli_1 = {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": True, "initialmaskbit": "01", "Patlist": "scn_arw_vmaxf1xat_hptp1600_4r4t_edt_stuckat_m1_classhvm_list",}
vmintc_sa_1 = get_test_list_sa_f1vmax_io_mtt(testtype, flow_name, cornerf1, atom1, vmintc_sa_tli_1, flow_matrix)
# vmintc_sa_tli_2 = {"Bypassport": -1, "Testmode": "Scoreboard", "ISEDC": True, "initialmaskbit": "1011", "Patlist": "scn_arw_vmaxf1xat_hptp1600_4r4t_edt_stuckat_m2_classhvm_list",}
# vmintc_sa_2 = get_test_list_sa_f1vmax_io_mtt(testtype, flow_name, cornerf1, atom2, vmintc_sa_tli_2, flow_matrix)
# vmintc_sa_tli_3 = {"Bypassport": -1, "Testmode": "Scoreboard", "ISEDC": True, "initialmaskbit": "0111", "Patlist": "scn_arw_vmaxf1xat_hptp1600_4r4t_edt_stuckat_m3_classhvm_list",}
# vmintc_sa_3 = get_test_list_sa_f1vmax_io_mtt(testtype, flow_name, cornerf1, atom3, vmintc_sa_tli_3, flow_matrix)


#endcpumax_f1 = Flow("ENDCPUMAX_F1", vmaxxat_vmintc_sa_occ)

#ATSPEED_F5 test list
vmaxxat_vmintc_atspeed_occ_tli = {"Bypassport": 1, "Testmode": "MultiVmin", "ISEDC": False, "Patlist": "scn_arw_vmaxf5xat_hptp1600_12r4t_edt_atspeed_occ_classhvm_list",}
vmaxxat_vmintc_atspeed_occ = get_test_list_atspeed_f5vmax_occ_mtt(testtype, flow_name, cornerf5, vmaxxat_vmintc_atspeed_occ_tli, flow_matrix, corner_id)
vmintc_atspeed_tli_0 = {"Bypassport": 1, "Testmode": "SingleVmin", "ISEDC": True, "initialmaskbit": "10", "Patlist": "scn_arw_vmaxf5xat_hptp1600_4r4t_edt_atspeed_m0_classhvm_list",}
vmintc_atspeed_0 = get_test_list_atspeed_f5vmax_io_mtt(testtype, flow_name, cornerf5, atom0, vmintc_atspeed_tli_0, flow_matrix, corner_id)
vmintc_atspeed_tli_1 = {"Bypassport": 1, "Testmode": "SingleVmin", "ISEDC": True, "initialmaskbit": "01", "Patlist": "scn_arw_vmaxf5xat_hptp1600_4r4t_edt_atspeed_m1_classhvm_list",}
vmintc_atspeed_1 = get_test_list_atspeed_f5vmax_io_mtt(testtype, flow_name, cornerf5, atom1, vmintc_atspeed_tli_1, flow_matrix, corner_id)
# vmintc_atspeed_tli_2 = {"Bypassport": -1, "Testmode": "SingleVmin", "ISEDC": True, "initialmaskbit": "1011", "Patlist": "scn_arw_vmaxf5xat_hptp1600_4r4t_edt_atspeed_m2_classhvm_list",}
# vmintc_atspeed_2 = get_test_list_atspeed_f5vmax_io_mtt(testtype, flow_name, cornerf5, atom2, vmintc_atspeed_tli_2, flow_matrix, corner_id)
# vmintc_atspeed_tli_3 = {"Bypassport": -1, "Testmode": "SingleVmin", "ISEDC": True, "initialmaskbit": "0111", "Patlist": "scn_arw_vmaxf5xat_hptp1600_4r4t_edt_atspeed_m3_classhvm_list",}
# vmintc_atspeed_3 = get_test_list_atspeed_f5vmax_io_mtt(testtype, flow_name, cornerf5, atom3, vmintc_atspeed_tli_3, flow_matrix, corner_id)

#endcpumax_f5 = Flow("ENDCPUMAX_F5", vmaxxat_vmintc_atspeed_occ)

VMAX_SHMOO_TLI = {"Bypassport": 1, "ISEDC": True}
#VMAX_SHMOO_OCC = get_shmoo_test_vmaxoccatspeed(VMAX_FLOW, DROPOUT5, SHMOO_ATSPEED_TLI, flowmatrix5)

# vmaxxat SUBFLOW
#endcpumax_SUBFLOW = Flow(f'{MODULE}_ENDCPUMAX',      
#                     Fitem("SAME", endcpumax_f1, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
#                     Fitem("SAME", endcpumax_f5, r0=pFail(ret=0), r1=pPass(ret=1)),
#                     VMAX_SHMOO_OCC
#)

#################################################################################
#							VMAXXATLO SUBFLOWX LAYOUT
#
#
#################################################################################
atom0 = 0
atom1 = 1
#atom2 = 2
#atom3 = 3
testtype = "SB"
flow_name = "VMAXXATLO" 
cornerf1 = "F1" 
cornerf5 = "F5"

# FlowMatrixRule Definition
FlowMatrixRule = {
    "AT_F1_FREQ_MHz": "1200",
    "AT_F5_FREQ_MHz": "3600"
    }

# FlowMatrix Definition
flow_matrix_definitions = {
    "F1": "AT_F1_FREQ",
    "F5": "AT_F5_FREQ",
}

corner_id_definitions = {
    "F5": "C5",
}

#SA_F1 test list
vmaxxat_vmintc_sa_occ_tli = {"Bypassport": -1, "Testmode": "MultiVmin", "ISEDC": False, "Patlist": "scn_arw_vmaxf1xatlo_hptp1600_12r4t_edt_stuckat_occ_classhvm_list",}
vmaxxat_vmintc_sa_occ = get_test_list_sa_f1vmax_occ_mtt(testtype, flow_name, cornerf1, vmaxxat_vmintc_sa_occ_tli, flow_matrix)
vmintc_sa_tli_0 = {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": True, "initialmaskbit": "10", "Patlist": "scn_arw_vmaxf1xatlo_hptp1600_4r4t_edt_stuckat_m0_classhvm_list",}
vmintc_sa_0 = get_test_list_sa_f1vmax_io_mtt(testtype, flow_name, cornerf1, atom0, vmintc_sa_tli_0, flow_matrix)
vmintc_sa_tli_1 = {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": True, "initialmaskbit": "01", "Patlist": "scn_arw_vmaxf1xatlo_hptp1600_4r4t_edt_stuckat_m1_classhvm_list",}
vmintc_sa_1 = get_test_list_sa_f1vmax_io_mtt(testtype, flow_name, cornerf1, atom1, vmintc_sa_tli_1, flow_matrix)
# vmintc_sa_tli_2 = {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": True, "initialmaskbit": "1011", "Patlist": "scn_arw_vmaxf1xatlo_hptp1600_4r4t_edt_stuckat_m2_classhvm_list",}
# vmintc_sa_2 = get_test_list_sa_f1vmax_io_mtt(testtype, flow_name, cornerf1, atom2, vmintc_sa_tli_2, flow_matrix)
# vmintc_sa_tli_3 = {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": True, "initialmaskbit": "0111", "Patlist": "scn_arw_vmaxf1xatlo_hptp1600_4r4t_edt_stuckat_m3_classhvm_list",}
# vmintc_sa_3 = get_test_list_sa_f1vmax_io_mtt(testtype, flow_name, cornerf1, atom3, vmintc_sa_tli_3, flow_matrix)


vmaxxatlo_f1 = Flow("VMAXXATLO_F1", vmaxxat_vmintc_sa_occ)

#ATSPEED_F5 test list
vmaxxat_vmintc_atspeed_occ_tli = {"Bypassport": -1, "Testmode": "MultiVmin", "ISEDC": False, "Patlist": "scn_arw_vmaxf5xatlo_hptp1600_12r4t_edt_atspeed_occ_classhvm_list",}
vmaxxat_vmintc_atspeed_occ = get_test_list_atspeed_f5vmax_occ_mtt(testtype, flow_name, cornerf5, vmaxxat_vmintc_atspeed_occ_tli, flow_matrix, corner_id)
vmintc_atspeed_tli_0 = {"Bypassport": 1, "Testmode": "SingleVmin", "ISEDC": True, "initialmaskbit": "10", "Patlist": "scn_arw_vmaxf5xatlo_hptp1600_4r4t_edt_atspeed_m0_classhvm_list",}
vmintc_atspeed_0 = get_test_list_atspeed_f5vmax_io_mtt(testtype, flow_name, cornerf5, atom0, vmintc_atspeed_tli_0, flow_matrix, corner_id)
vmintc_atspeed_tli_1 = {"Bypassport": 1, "Testmode": "SingleVmin", "ISEDC": True, "initialmaskbit": "01", "Patlist": "scn_arw_vmaxf5xatlo_hptp1600_4r4t_edt_atspeed_m1_classhvm_list",}
vmintc_atspeed_1 = get_test_list_atspeed_f5vmax_io_mtt(testtype, flow_name, cornerf5, atom1, vmintc_atspeed_tli_1, flow_matrix, corner_id)
# vmintc_atspeed_tli_2 = {"Bypassport": 1, "Testmode": "SingleVmin", "ISEDC": True, "initialmaskbit": "1011", "Patlist": "scn_arw_vmaxf5xatlo_hptp1600_4r4t_edt_atspeed_m2_classhvm_list",}
# vmintc_atspeed_2 = get_test_list_atspeed_f5vmax_io_mtt(testtype, flow_name, cornerf5, atom2, vmintc_atspeed_tli_2, flow_matrix, corner_id)
# vmintc_atspeed_tli_3 = {"Bypassport": 1, "Testmode": "SingleVmin", "ISEDC": True, "initialmaskbit": "0111", "Patlist": "scn_arw_vmaxf5xatlo_hptp1600_4r4t_edt_atspeed_m3_classhvm_list",}
# vmintc_atspeed_3 = get_test_list_atspeed_f5vmax_io_mtt(testtype, flow_name, cornerf5, atom3, vmintc_atspeed_tli_3, flow_matrix, corner_id)

vmaxxatlo_f5 = Flow("VMAXXATLO_F5", vmaxxat_vmintc_atspeed_occ)

# vmaxxat SUBFLOW
vmaxxat_SUBFLOW = Flow(f'{MODULE}_VMAXXATLO',
                     Fitem("SAME", vmaxxatlo_f1, r0=pFail(ret=0), r1=pPass(goto="NEXT")),
                     Fitem("SAME", vmaxxatlo_f5, r0=pFail(ret=0), r1=pPass(ret=1)),
)

#################################################################################
#							FMIN SUBFLOWX LAYOUT
#
#
#################################################################################

# FlowMatrixRule Definition
FlowMatrixRule = {
    "AT_FMIN_MHz": "0400"
}
# FlowMatrix Definition
flow_matrix_definitions = {
    "FMIN": "AT_FMIN",
}
# Function to create test lists and flows for each module
def create_module_flow(testtype, flow_name, corner, atom, flow_matrix):
    """
    Create a Flow for a given module/atom for FMIN subflow.
    """
    module_name = f"M{atom}"
    vmintc_atspeed_tli = {
        "Bypassport": 1,
        "Testmode": "SingleVmin",
        "initialmaskbit": N2P48_INITIALMASKBIT[module_name],
        "ISEDC": True,
        "Recovery": "RecoveryPort",
        "Patlist": f"scn_arw_fminxat_hptp1600_4r4t_edt_atspeed_m{atom}_classhvm_list",
        "executionmode": "SearchWithScoreboard",    
    }
    
    vmintc_atspeed = get_test_list_atspeed_fmin_io_mtt(        
    		testtype, flow_name, corner, atom, vmintc_atspeed_tli, flow_matrix
    	)

    vmintc_atspeed_ff = get_test_list_fminffio(        
    		testtype, flow_name, corner, atom, flow_matrix
    	)
	
    return Flow(f"{flow_name}_M{atom}", vmintc_atspeed)

# Function to create subflows
def create_subflow(testtype, flow_name, corner, module_name, flow_matrix):
    
    # OCC COMPOSITE TEST LIST
    vmintc_atspeed_occ_tli = {"Bypassport": -1, "Testmode": "MultiVmin", "ISEDC": False}
    vmintc_atspeed_occ = get_test_list_atspeed_fmin_occ_mtt(testtype, flow_name, corner, vmintc_atspeed_occ_tli, flow_matrix)
    fminffocc = get_test_list_fminffocc(testtype, flow_name, corner, 0, vmintc_atspeed_occ_tli)
    occ = Flow(f"{flow_name}_OCC", vmintc_atspeed_occ, fminffocc)
                    


    # Create flows for each module
    module_flows = [
        create_module_flow(testtype, flow_name, corner, i, flow_matrix)
        for i in range(len(ATOM_MODULES))
    ]

    subflow = Flow(
        f"{module_name}_{flow_name}",
        Fitem("SAME", occ, r0=pFail(ret=0), r1=pPass(ret=1)),
        *[
            Fitem("SAME", module_flow, r0=pFail(goto="NEXT"), r1=pPass(goto="NEXT"))
            for module_flow in module_flows[:-1]
        ],
        Fitem("SAME", module_flows[-1], r0=pFail(ret=1), r1=pPass(ret=1))
    )
    return subflow

# Define the subflows

flow_name = "FMINXAT"
corner = "FMIN"
testtype = "VMIN"
flow_matrix = flow_matrix_definitions[corner]
subflows = [create_subflow(testtype, flow_name, corner, MODULE, flow_matrix)]

