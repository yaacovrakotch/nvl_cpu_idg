#Import the necessary classes from Pymtpl
from turtle import goto
from pymtpl.por_methods import PrimeScanSPOFITestMethod, PrimePauseTestMethod, VminTC, DDGFunctionalTC, DDGShmooTC, DedcLoadConfigTC, DedcRVCallbackTC
from pymtpl.core import Flow, Fitem, pPass, pFail, Initialize, MultiTrial, AUTO, MTLdefault, InitializeNVLClass, Import, TrialParamSpec, Spec, BaseMethod, required, optional, MConfig     

# Beginning of QNRELTTC class definition
class QNRELTTC(BaseMethod):
    def __init__(self,
                 name,
                 FloatingTestName=optional,         # Gets or sets FloatingTestName featrue. Default is empty string (disable). Set to any other string to enable.
                 EnablePerPatternLogging=optional,  # Gets or sets EnablePerPatternLogging featrue. Default is empty string (disable). Set to any other string to enable.
                 PauseTime=optional,                # Gets or sets PauseTime. Sets how many milliseconds to wait between vmin search test execution. A value less than 1 indicates the feature is disabled.
                 RunRegex=optional,                 # Gets or sets regular expression to filter what test names to consider.
                 SearchTestClassName=required,      # Gets or sets vminTC for MTL, but can be different based on product.
                 IfeObject=optional,                # Gets or Sets **not in use will be removed later with the refactoring of the IfeObject**.
                 Mode=required,                     #  Gets or sets the registration mode of the RV callbacks in this instance." 
                 BypassPort=optional,               # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,      # Enable for current instance's test time and memory information
                 LogLevel=optional,                 # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,           # Enable for record detailed test time information
                 PreInstance=optional,              # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,             # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of QNRELTTC class definition
MODULE_NAME =  'QNR_CARV_CKX'

# Initialize the module by defining the output mtpl path and the module name
InitializeNVLClass(MODULE_NAME, MODULE_NAME)
Import(f"{MODULE_NAME}.usrv")

# Define the Mconfig file configuration.
mconfig = MConfig(
)

# Init flow
dedcLoadConfig = DedcLoadConfigTC(
    name = "CTRL_X_CALLBACK_K_INIT_X_X_X_X_CONTROL_ARV",
    CoreAware = "DISABLE",
    Scope = "GLOBAL",
    Mode = Spec('QNR_CARV_CKX_Rules.CTRL_X_CALLBACK_K_INIT_X_X_X_X_CONTROL_ARV_Mode("ENABLE", "DISABLE")'),
    ConfigFile = f"./InputFiles/NVL_ARV_CPU.json",
    _fitem = Fitem(r0=pFail(ret=0))
    ) 

elt = QNRELTTC(
    name = "CTRL_X_CALLBACK_K_INIT_X_X_X_X_CONTROL_ELT",
    RunRegex = "IP[CHPG]::.*_F[567]_",
    SearchTestClassName  = "VminTC",
    Mode = Spec('QNR_CARV_CKX_Rules.CTRL_X_CALLBACK_K_INIT_X_X_X_X_CONTROL_ELT("REGISTER", "UNREGISTER")'),
    PauseTime = 100,
    FloatingTestName  = "IPC::QNR_CARV_CXX::CTRL_X_EAP_X_CPUIPFF_X_X_X_X_EAP,IPG::QNR_CARV_GXX::CTRL_X_EAP_X_GCDIPFF_X_X_X_X_EAP,IPH::QNR_CARV_HXX::CTRL_X_EAP_X_HUBIPFF_X_X_X_X_EAP,IPP::QNR_CARV_PXX::CTRL_X_EAP_X_PCDIPFF_X_X_X_X_EAP",
    _fitem = Fitem(r0=pFail(ret=0))
    ) 

# DEDC flow
prime_pause = PrimePauseTestMethod(
    name = "CTRL_X_PAUSE_X_CPUPKGFF_X_X_X_X_PAUSE",
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
    name = "CTRL_X_SCANFI_X_CPUPKGFF_X_X_X_X_SPOFI",
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
    name = "CTRL_X_EAP_X_CPUPKGFF_X_X_X_X_EAP",
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
    name = "CTRL_X_FUNC_X_CPUPKGFF_X_X_X_X_FUNC",
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
    name = "CTRL_X_SHMOO_X_CPUPKGFF_X_X_X_X_SHMOO",
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

CPUPKGFF_SubFlow = Flow(f'{MODULE_NAME}_CPUPKGFF',prime_pause, prime_spofi, vmin, func, shmoo)

INITCPUPKG_SubFlow = Flow(f'{MODULE_NAME}_INIT',dedcLoadConfig, elt)