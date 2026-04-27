# PKG Sku Manager Module pymtpl source code.
# Output for prime13 and TOS4.
from pymtpl.por_methods import BaseMethod, required, optional
from pymtpl.core import Flow, Fitem, pPass, pFail, Initialize, AUTO, InitializeNVLClass, Import, TrialParamSpec, Spec

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

# Initialize the module by defining the output mtpl path and the module name
InitializeNVLClass('TPI_SKUCTRL_CXX', 'TPI_SKUCTRL_CXX', binrange = (9361, 9361))

domain_list = ["CORE", "RING", "ATOM"] #, "GT", "SAAT", "SAC", "SACD", "SADPU", "SAME", "SAN", "SAPS", "SAQ", "SAVPU"] #based on keys in FreqConfig.json
freqtest_list = []

for domain in domain_list:
    passfreq_test = SkuManager(
    name = "CTRL_X_X_K_" + domain + "_X_X_X_X_SETPASSFREQ",
    BypassPort = -1,
    Domain = domain,
    Mode = "SetPassFreq",
    CurrentOptype = "__shared__::DFFVars.WRITE_OPTYPE",
    _fitem = Fitem(r0=pFail(setbin=AUTO, ret=0), r2=pPass(ret=1))
    )
    freqtest_list.append(passfreq_test)
    
    # midfreq_test = SkuManager(
    # name = "CTRL_X_X_K_" + domain + "_X_X_X_X_CHECKMIDFREQ",
    # BypassPort = 1,
    # Domain = domain,
    # MidFreqValue="F4",
    # Mode = "CheckMidFreq",
    # _fitem = Fitem(r0=pFail(setbin=AUTO, ret=0), r2=pPass(ret=1))
    # )
    # freqtest_list.append(midfreq_test)

Flow("TPI_SKUCTRL_CXX_F5XCR", freqtest_list)