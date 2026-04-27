#Import the necessary classes from Pymtpl
from turtle import goto
from pymtpl.por_methods import PrimeScanSPOFITestMethod, PrimePauseTestMethod, VminTC, DDGFunctionalTC, DDGShmooTC, DedcLoadConfigTC, DedcRVCallbackTC
from pymtpl.core import Flow, Fitem, pPass, pFail, Initialize, MultiTrial, AUTO, MTLdefault, InitializeNVLClass, Import, TrialParamSpec, Spec, BaseMethod, required, optional, MConfig     
        
MODULE_NAME =  'QNR_CARV_CXX'

# Initialize the module by defining the output mtpl path and the module name
InitializeNVLClass(MODULE_NAME, MODULE_NAME)
Import(f"{MODULE_NAME}.usrv")

# Define the Mconfig file configuration.
mconfig = MConfig(
    ip="IPC"
)

# Init flow
dedcLoadConfig = DedcLoadConfigTC(
    name = "CTRL_X_CALLBACK_K_INIT_X_X_X_X_CONTROL_ARV",
    CoreAware = "DISABLE",
    Scope = "GLOBAL",
    Mode = Spec('QNR_CARV_CXX_Rules.CTRL_X_CALLBACK_K_INIT_X_X_X_X_CONTROL_ARV_Mode("ENABLE", "DISABLE")'),
    ConfigFile = f"./InputFiles/NVL_ARV.json",
    _fitem = Fitem(r0=pFail(ret=0))
    ) 

# DEDC flow
prime_pause = PrimePauseTestMethod(
    name = "CTRL_X_PAUSE_X_CPUIPFF_X_X_X_X_PAUSE",
    SleepTime = 1,
    ExitPort = 1,
    BypassPort = 1,
    _fitem = Fitem('SAME', edc = True,
                rm1=pFail(ret=-1, setbin=AUTO),
                rm2=pFail(ret=-2, setbin=AUTO),
                r0=pPass(ret=1),
                r1=pPass(ret=1),
                r2=pPass(ret=1),
                r3=pPass(ret=1),
                r4=pPass(ret=1),
                r5=pPass(ret=1)
                )
    )

prime_spofi = PrimeScanSPOFITestMethod(
    name = "CTRL_X_SCANFI_X_CPUIPFF_X_X_X_X_SPOFI",
    _comment = "NOCLEAN",
    Patlist = "IP_CPU::scn_cdie_begcpupkgf1_nonccf_atspeed_mio200_edt_classhvm_list",
    LevelsTc = "BASE::cpu_all_bf_x_x_pkg_lvl_max_lvl",
    TimingsTc = "IP_CPU::SCN_UNCORE_C68C::cpu_testport_timing_tclk100_sclk200_cclk400",
    PerPatternFailCaptureCount = 25000,
    TotalFailCaptureCount = 50000,
    BypassPort = 1,
    _fitem = Fitem(r0=pFail(), edc=True)
    )

vmin = VminTC(
    name = "CTRL_X_EAP_X_CPUIPFF_X_X_X_X_EAP",
    _comment = "NOCLEAN",
    ExecutionMode = "SearchWithScoreboard",
    Patlist = "IP_PCH_BASE::NotAPlist",
    LevelsTc = "IP_PCH_BASE::gcd_all_bf_x_x_ippch_lvl_max_lvl",
    TimingsTc = "IP_PCH_BASE::gcd_dftring_perpin_timing_tclk100_dclk400_cclk400",
    MaxFailsNum = 1000,
    TestMode = "Scoreboard",
    EndVoltageLimits = "",
    StartVoltages = "",
    StepSize = .01,
    VoltageTargets = "",
    BypassPort = 1,
    _fitem = Fitem(r0=pFail(), edc=True)
    )

func = DDGFunctionalTC(
    name = "CTRL_X_FUNC_X_CPUIPFF_X_X_X_X_FUNC",
    _comment = "NOCLEAN",
    Patlist = "IP_PCH_BASE::NotAPlist",
    LevelsTc = "IP_PCH_BASE::gcd_all_bf_x_x_ippch_lvl_max_lvl",
    TimingsTc = "IP_PCH_BASE::gcd_dftring_perpin_timing_tclk100_dclk400_cclk400",
    FailuresToCapturePerPattern = 2,
    FailuresToCaptureTotal = 1000,
    MaxFailuresPerPatternToItuff = 2,
    MaxFailuresToItuff = 1000,
    BypassPort = 1,
    _fitem = Fitem(r0=pFail(), edc=True)
    )

shmoo = DDGShmooTC(
    name = "CTRL_X_SHMOO_X_CPUIPFF_X_X_X_X_SHMOO",
    _comment = "NOCLEAN",
    Patlist = "IP_PCH_BASE::NotAPlist",
    LevelsTc = "IP_PCH_BASE::gcd_all_bf_x_x_ippch_lvl_max_lvl",
    TimingsTc = "IP_PCH_BASE::gcd_dftring_perpin_timing_tclk100_dclk400_cclk400",
    XAxisParam = "p_mtd_per",
    XAxisParamType = "UserDefined",
    XAxisRange = "9E-9:.5E-9:5",
    XAxisType = "SpecSetVariable",
    YAxisRange = "0.45:0.05:15",
    YAxisParamType = "UserDefined",
    BypassPort = 1,
    _fitem = Fitem(r0=pFail(), edc=True)
    )

CPUIPFF_SubFlow = Flow(f'{MODULE_NAME}_CPUIPFF',prime_pause, prime_spofi, vmin, func, shmoo)

INITCPU_SubFlow = Flow(f'{MODULE_NAME}_INIT',dedcLoadConfig)