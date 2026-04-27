# Owner: samrenji
# Import the necessary classes from Pymtpl
from pymtpl.por_methods import CtvDecoderSpm, PrimeFunctionalTestMethod, AuxiliaryTC
from pymtpl.core import Flow, Fitem, pPass, pFail, Initialize, NativeMultiTrial, AUTO, MTLdefault, InitializeMTL, Import, TrialParamSpec, Spec, ModuleFlow, InitializeNVLClass

# Initialize the module by defining the output mtpl path and module name
InitializeNVLClass('./TPI_DAS_CXX', 'TPI_DAS_CXX', tosversion="tos4", binrange=(710, 779))

# Add the necessary files to import in your mtpl
Import("TPI_DAS_CXX_LevelsSequences.lvl")
Import("TPI_DAS_CXX_Levels.tcg")

# Define test names and level modes
TestName = ["FORCE_0550MV", "FORCE_0650MV", "FORCE_0750MV", "FORCE_0850MV", "FORCE_0950MV", "FORCE_1050MV"]
LevelMode = {
    "FORCE_0550MV": "IPC::TPI_DAS_CXX::DAS_VCCIA_0P55V_MIN",
    "FORCE_0650MV": "IPC::TPI_DAS_CXX::DAS_VCCIA_0P65V_MIN",
    "FORCE_0750MV": "IPC::TPI_DAS_CXX::DAS_VCCIA_0P75V_MIN",
    "FORCE_0850MV": "IPC::TPI_DAS_CXX::DAS_VCCIA_0P85V_MIN",
    "FORCE_0950MV": "IPC::TPI_DAS_CXX::DAS_VCCIA_0P95V_MIN",
    "FORCE_1050MV": "IPC::TPI_DAS_CXX::DAS_VCCIA_1P05V_MIN"
}

# Define modes
Modes = ["TDC0", "TDC1", "FALL", "RISE"]
mode_to_patlist = {
    "TDC0": "RO_MODE_TDC_0",
    "TDC1": "RO_MODE_TDC_1",
    "FALL": "MEAS_MODE_FALL",
    "RISE": "MEAS_MODE_RISE"
}

# Map modes to configuration files
mode_to_config_file = {
    "TDC0": Spec('__shared__::TpRule.If_48("./InputFiles/das_ro_mode_tdc0_48_A0.csv","./InputFiles/das_ro_mode_tdc0_A0.csv")'),
    "TDC1": Spec('__shared__::TpRule.If_48("./InputFiles/das_ro_mode_tdc1_48_A0.csv","./InputFiles/das_ro_mode_tdc1_A0.csv")'),
    "FALL": Spec('__shared__::TpRule.If_48("./InputFiles/das_meas_mode_fall_48_A0.csv","./InputFiles/das_meas_mode_fall_A0.csv")'),
    "RISE": Spec('__shared__::TpRule.If_48("./InputFiles/das_meas_mode_rise_48_A0.csv","./InputFiles/das_meas_mode_rise_A0.csv")')
}

# Define the DAS_BYPASS Test
DAS_BYPASS = AuxiliaryTC(
    name='DAS_X_AUX_K_BEGINCPU_X_X_X_X_QNR_FORK',
    DataType='String',
    Datalog='Enabled',
    Expression="[SCVars.SC_ENGID]",
    ResultPort="([R]=='QE'||[R]=='QQ'||[R]=='QZ')?1:2"
)

# Create Test Flow
def create_test_flows():
    test_list = []
    test_names = set()  # To track unique test names
    for param in TestName:
        for mode in Modes:
            patname = mode_to_patlist[mode]  # Get the corresponding patlist mode
            config_file = mode_to_config_file[mode]  # Get the corresponding configuration file
            test_name = f"DAS_X_CTVDECODER_K_BEGINCPU_X_X_X_X_{param}_{mode}"
            if test_name in test_names:
                print(f"Duplicate test name found: {test_name}")
            else:
                test_names.add(test_name)
            patlist_name = f"nvl_full_das_ip_{patname.lower()}"

            # Set PreInstance and PostInstance as needed
            pre_instance = None
            post_instance = None
            if param == "FORCE_0950MV":
                pre_instance = Spec('__shared__::TpRule.If_48("VoltageConverter(--dlvrpins VCCIA --fivrcondition NOM_CCF_CORE --overrides CORE1:0.95,CORE0:0.95 --expressions CCF_CORE)","VoltageConverter(--dlvrpins VCCIA --fivrcondition NOM_CCF_CORE --overrides CORE3:0.95,CORE2:0.95,CORE1:0.95,CORE0:0.95 --expressions CCF_CORE)")')
                post_instance = "VoltageConverter(--dlvrpins VCCIA --fivrcondition NOM_CCF_CORE --expressions CCF_CORE)"
            elif param == "FORCE_1050MV":
                pre_instance = Spec('__shared__::TpRule.If_48("VoltageConverter(--dlvrpins VCCIA --fivrcondition NOM_CCF_CORE --overrides CORE1:1.05,CORE0:1.05 --expressions CCF_CORE)","VoltageConverter(--dlvrpins VCCIA --fivrcondition NOM_CCF_CORE --overrides CORE3:1.05,CORE2:1.05,CORE1:1.05,CORE0:1.05 --expressions CCF_CORE)")')
                post_instance = "VoltageConverter(--dlvrpins VCCIA --fivrcondition NOM_CCF_CORE --expressions CCF_CORE)"

            # Build kwargs for CtvDecoderSpm
            kwargs = dict(
                name=test_name,
                ConfigurationFile=config_file,
                LevelsTc=LevelMode[param],
                TimingsTc="IPC::CPU_IP_BASE::cpu_fun_timing_mts100_tstprtclk50_tck100",
                PrePlist="SetPinAttributes(--settings=CPU_VLOADMUXCBIT3:LogicalValue:0)",
                CtvCapturePins="IPC::CPU_TDO",
                Patlist=patlist_name,
                _fitem=Fitem('SAME', r0=pFail(setbin=AUTO, ret=0), r2=pFail(setbin=90990700, ret=2)),
            )
            if pre_instance:
                kwargs["PreInstance"] = pre_instance
            if post_instance:
                kwargs["PostInstance"] = post_instance

            flow_test = CtvDecoderSpm(**kwargs)
            test_list.append(flow_test)
    return test_list

# Define STRESS_AF_MODE using PrimeFunctionalTestMethod
def create_stress_af_mode():
    stress_af_tests = []
    for param in TestName:
        test_name = f"DAS_X_PRIMEFUNC_K_BEGINCPU_X_X_X_X_{param}_STRESS_AF"
        patlist_name = "nvl_full_das_ip_stress_af_mode"
        
        # Set PreInstance and PostInstance as needed
        pre_instance = None
        post_instance = None
        if param == "FORCE_0950MV":
            pre_instance = "VoltageConverter(--dlvrpins VCCIA --fivrcondition NOM_CCF_CORE --overrides CORE3:0.95,CORE2:0.95,CORE1:0.95,CORE0:0.95 --expressions CCF_CORE)"
            post_instance = "VoltageConverter(--dlvrpins VCCIA --fivrcondition NOM_CCF_CORE --expressions CCF_CORE)"
        elif param == "FORCE_1050MV":
            pre_instance = "VoltageConverter(--dlvrpins VCCIA --fivrcondition NOM_CCF_CORE --overrides CORE3:1.05,CORE2:1.05,CORE1:1.05,CORE0:1.05 --expressions CCF_CORE)"
            post_instance = "VoltageConverter(--dlvrpins VCCIA --fivrcondition NOM_CCF_CORE --expressions CCF_CORE)"

        # Build kwargs for PrimeFunctionalTestMethod
        kwargs = dict(
            name=test_name,
            LevelsTc=LevelMode[param],
            TimingsTc="IPC::CPU_IP_BASE::cpu_fun_timing_mts100_tstprtclk50_tck100",
            PrePlist="SetPinAttributes(--settings=CPU_VLOADMUXCBIT3:LogicalValue:0)",
            Patlist="nvl_full_das_ip_stress_af_mode",
            _comment = "NOCLEAN",
            BypassPort=1,
            _fitem=Fitem('SAME', r0=pFail(setbin=AUTO, ret=0), r2=pFail(setbin=90990700, ret=2))
        )
        if pre_instance:
            kwargs["PreInstance"] = pre_instance
        if post_instance:
            kwargs["PostInstance"] = post_instance

        flow_test = PrimeFunctionalTestMethod(**kwargs)
        stress_af_tests.append(flow_test)
    return Flow("STRESS_AF_MODE", stress_af_tests)

# Create Test Flow for each mode
all_tests = create_test_flows()
# Create STRESS_AF_MODE Flow
STRESS_AF_MODE = create_stress_af_mode()

# Define Composite Test
TDC_0 = Flow("TDC_0", [test for test in all_tests if "TDC0" in test.name])
TDC_1 = Flow("TDC_1", [test for test in all_tests if "TDC1" in test.name])
#CALIB_MODE = Flow("CALIB_MODE", [test for test in all_tests if "CALIB_MODE" in test.name])
FALL_MODE = Flow("FALL_MODE", [test for test in all_tests if "FALL" in test.name])
RISE_MODE = Flow("RISE_MODE", [test for test in all_tests if "RISE" in test.name])



# Call your test in a DUTFlow
BEGINCPU_SubFlow = Flow('TPI_DAS_CXX_BEGINCPU',
                    Fitem("SAME", DAS_BYPASS, r0=pFail(setbin=AUTO, ret=0), r2=pPass(ret=2)),
                    Fitem("SAME", TDC_0, r0=pFail(ret=0), r2=pFail(ret=0), r3=pFail(ret=0)),
                    Fitem("SAME", TDC_1, r0=pFail(ret=0), r2=pFail(ret=0), r3=pFail(ret=0)),
                    #Fitem("SAME", CALIB_MODE, r0=pFail(ret=2), r2=pFail(ret=0), r3=pFail(ret=0)),
                    Fitem("SAME", FALL_MODE, r0=pFail(ret=0), r2=pFail(ret=0), r3=pFail(ret=0)),
                    Fitem("SAME", RISE_MODE, r0=pFail(ret=0), r2=pFail(ret=0), r3=pFail(ret=0)),
                    Fitem("SAME", STRESS_AF_MODE, r0=pFail(ret=0), r2=pFail(ret=0), r3=pFail(ret=0)))
