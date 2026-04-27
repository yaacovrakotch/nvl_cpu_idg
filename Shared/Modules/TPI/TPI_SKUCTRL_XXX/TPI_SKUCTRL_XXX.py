# PKG Sku Manager Module pymtpl source code.
# Output for prime13 and TOS4.
from pymtpl.por_methods import BaseMethod, required, optional, AuxiliaryTC
from pymtpl.core import Flow, Fitem, pPass, pFail, Initialize, AUTO, InitializeNVLClass, Import, TrialParamSpec, Spec

class SkuDataInit(BaseMethod):
    def __init__(self,
                 name,
                 SkuInputFile=required,  # <param>=required|optional,
                 _comment=None,                 # required, do not omit
                 _fitem=None,                   # required, do not omit
                 **kwargs                       # required, do not omit
                 ):
        self._init(name, locals())

class SkuManager(BaseMethod):
    def __init__(self,
                 name,
                 BypassPort=optional,
                 CurrentOptype=required,
                 ClassHotProcessOptype=required,
                 Domain=optional,
                 MidFreqValue=optional,
                 Mode=required,
                 PreInstance=optional,
                 _comment=None,                 # required, do not omit
                 _fitem=None,                   # required, do not omit
                 **kwargs                       # required, do not omit
                 ):
        self._init(name, locals())

class VminForwardInit(BaseMethod):
    def __init__(self,
                 name,
                 UpdateLimitCheck=required,  # <param>=required|optional,
                 UpdateFLWD=required,
                 PrintToItuff=required,
                 VminGB=optional,
                 Domains = optional,
                 DFFPrefix=required,
                 IgnoredCornerList=optional,
                 ReadDffOptype=optional,
                 ReadDffDieID=optional,
                 BypassPort=optional,
                 PreInstance=optional,
                 _comment=None,                 # required, do not omit
                 _fitem=None,                   # required, do not omit
                 **kwargs                       # required, do not omit
                 ):
        self._init(name, locals())

# Initialize the module by defining the output mtpl path and the module name
InitializeNVLClass('TPI_SKUCTRL_XXX', 'TPI_SKUCTRL_XXX', binrange = (9360, 9360),
                   defaultrm2bin=(99934500, 99934999),
                   defaultrm1bin=(98934500, 98934999))

Import("TPI_SKUCTRL_XXX.usrv")

skudatainit_test = SkuDataInit(
    name = "CTRL_X_X_K_INIT_X_X_X_X_SKUDATAINIT",
    SkuInputFile = Spec('GetEnvironmentVariable("~HDMT_TP_BASE_DIR")' + ' + 'f'__shared__::TpRule.If_CLASS_NVL_S52C("./Shared/Modules/TPI/TPI_SKUCTRL_XXX/InputFiles/SKUmanagerFreqConfig_52C.json", __shared__::TpRule.If_CLASS_NVL_HX28C("./Shared/Modules/TPI/TPI_SKUCTRL_XXX/InputFiles/SKUmanagerFreqConfig_HX.json", __shared__::TpRule.If_CLASS_NVL_S28C("./Shared/Modules/TPI/TPI_SKUCTRL_XXX/InputFiles/SKUmanagerFreqConfig.json", __shared__::TpRule.If_CLASS_NVL_P16C("./Shared/Modules/TPI/TPI_SKUCTRL_XXX/InputFiles/SKUmanagerFreqConfig_P16C.json", __shared__::TpRule.If_CLASS_NVL_S16C("./Shared/Modules/TPI/TPI_SKUCTRL_XXX/InputFiles/SKUmanagerFreqConfig_S16C.json", __shared__::TpRule.If_CLASS_DNL_S28C("./Shared/Modules/TPI/TPI_SKUCTRL_XXX/InputFiles/SKUmanagerFreqConfig_S28C_DNL.json", __shared__::TpRule.If_CLASS_NVL_U8C("./Shared/Modules/TPI/TPI_SKUCTRL_XXX/InputFiles/SKUmanagerFreqConfig_U8C.json", __shared__::TpRule.If_CLASS_NVL_H16C("./Shared/Modules/TPI/TPI_SKUCTRL_XXX/InputFiles/SKUmanagerFreqConfig_H16C.json", "./Shared/Modules/TPI/TPI_SKUCTRL_XXX/InputFiles/SKUmanagerFreqConfig.json"))))))))'),
    _fitem = Fitem(r0=pFail(ret=0))
)

AHMT_FOLK = AuxiliaryTC(
    name = "AFORK_X_SCREEN_K_STARTPREPRL1_X_X_X_X_X",
    BypassPort = Spec('__shared__::FlwSkpCollect.if_ahmt(2,1)'),
    DataType = "Integer",
    Expression = "1",
	ResultPort = "1",
    _fitem = Fitem(r0=pFail(setbin=9360, ret=0), r2=pPass(ret = 1))
)

skumanagerpredictor_test = SkuManager(
    name = "CTRL_X_X_K_STARTPREPRL1_X_X_X_X_SKUMANAGER",
    CurrentOptype = "__shared__::DFFVars.WRITE_OPTYPE",
    ClassHotProcessOptype = Spec('TPI_SKUCTRL_XXX_Rules.PredictorMode_ClassHotProcessOptype("CLASSHOT:RC_S1", "CLASSHOT:PBIC_DAB")'),
    Mode = "Predictor",
    PreInstance = "SetCurrentDieId(PKG)",
    _fitem = Fitem(r0=pFail(setbin=9360, ret=0))
)

dielet_dict = {"CPU" : [["CORE", "RING", "ATOM"], ["GT", "SAAT", "SAC", "SADPU", "SAME", "SAN", "SAQ", "SAVPU"], "cpu"],
               "GPU" : [["GT"], ["CORE", "RING", "ATOM", "SAAT", "SAC", "SADPU", "SAME", "SAN", "SAQ", "SAVPU"], "gcd"],
               # "HUB" : [["SAAT", "SAC", "SADPU", "SAME", "SAN", "SAQ", "SAVPU"], ["CORE", "RING", "ATOM", "GT"], "hub"]
}
desktop_only = ["SADPU", "SAME", "SAN", "SAVPU"]

vminforwardinit_list = []

for dielet in dielet_dict.keys():
    vminforwardinit_test = VminForwardInit(
        name = "CTRL_" + dielet.upper() + "_DOWNSTREAMFLOWCONTROL_K_STARTPREPRL1_X_X_X_X",
        BypassPort = Spec("__shared__::DieIndic.if_" + dielet_dict[dielet][2] + "(TPI_SKUCTRL_XXX_Rules.VminForwardInit_BypassPort(1, 1, -1), 1)"),
        DFFPrefix = Spec('TPI_SKUCTRL_XXX_Rules.VminForwardInit_DFFPrefix("R", "H", "C", "E")'),
        UpdateFLWD = "TRUE",
        UpdateLimitCheck = "FALSE",
        PrintToItuff = "TRUE",
        ReadDffOptype = Spec('TPI_SKUCTRL_XXX_Rules.VminForwardInit_ReadDffOptype("RC_S1", "PBIC_DAB")'),
        ReadDffDieID = Spec("__shared__::DFFVars.DIEID_" + dielet),
        Domains = ",".join(dielet_dict[dielet][0]),
        # IgnoredCornerList = ",".join(dielet_dict[dielet][1]),
        _fitem = Fitem(r0=pFail(setbin=9360, ret=0))
    )
    vminforwardinit_list.append(vminforwardinit_test)
vminforwardinit_test_hub = VminForwardInit(
    name = "CTRL_HUB_DOWNSTREAMFLOWCONTROL_K_STARTPREPRL1_X_X_X_X",
    BypassPort = Spec("__shared__::DieIndic.if_hub(TPI_SKUCTRL_XXX_Rules.VminForwardInit_BypassPort(1, 1, -1), 1)"),
    DFFPrefix = Spec('TPI_SKUCTRL_XXX_Rules.VminForwardInit_DFFPrefix("R", "H", "C", "E")'),
    UpdateFLWD = "TRUE",
    UpdateLimitCheck = "FALSE",
    PrintToItuff = "TRUE",
    ReadDffOptype = Spec('TPI_SKUCTRL_XXX_Rules.VminForwardInit_ReadDffOptype("RC_S1", "PBIC_DAB")'),
    ReadDffDieID = Spec("__shared__::DFFVars.DIEID_HUB"),
    Domains = Spec('__shared__::TpRule.If_S_PKGs("SAAT,SAC,SAQ","SAAT,SAC,SAQ")'),
    # IgnoredCornerList = ",".join(dielet_dict[dielet][1]),
    _fitem = Fitem(r0=pFail(setbin=9360, ret=0))
)
vminforwardinit_list.append(vminforwardinit_test_hub)

        
initfreq_test = SkuManager(
    name = "CTRL_X_GETINITIALFREQ_K_STARTPREPRL1_X_X_X_X",
    Domain = Spec('__shared__::TpRule.If_S_PKGs("CORE,RING,ATOM,GT,SAAT,SAC,SAQ","CORE,RING,ATOM,GT,SAAT,SAC,SAQ")'),
    Mode = "GetInitialFreq",
    _fitem = Fitem(r0=pFail(setbin=AUTO, ret=0), r2=pPass(ret=1))
)

vminforwardinit_test = VminForwardInit(
    name = "CTRL_CPU1_DOWNSTREAMFLOWCONTROL_K_STARTPREPRL1_X_X_X_X",
    BypassPort = Spec("__shared__::DieIndic.if_cpu(__shared__::TpRule.If_CLASS_NVL_S52C(__shared__::TpRule.If_CHOT(1, __shared__::TpRule.If_RCHOT(1, -1)), 1), 1)"),
    DFFPrefix = Spec('TPI_SKUCTRL_XXX_Rules.VminForwardInit_DFFPrefix("R", "H", "C", "E")'),
    UpdateFLWD = "TRUE",
    UpdateLimitCheck = "FALSE",
    PrintToItuff = "TRUE",
    ReadDffOptype = Spec('TPI_SKUCTRL_XXX_Rules.VminForwardInit_ReadDffOptype("RC_S1", "PBIC_DAB")'),
    ReadDffDieID = Spec("__shared__::DFFVars.DIEID_CPU1"),
    Domains = "CORE,RING,ATOM",
    #IgnoredCornerList = "GT, GTVPG, SAAT, SAC, SADPU, SAME, SAN, SAQ, SAVPU",
    _fitem = Fitem(r0=pFail(setbin=9360, ret=0))
)
vminforwardinit_list.append(vminforwardinit_test)

Flow("TPI_SKUCTRL_XXX_INIT", skudatainit_test)
Flow("TPI_SKUCTRL_XXX_STARTPREPRL1", AHMT_FOLK,skumanagerpredictor_test, initfreq_test, vminforwardinit_list)
