from pyqs import PortInject, ManualInject, SetModule, ctvData, portData, pinData, thermalData, userVar, cycleData, triggerData, patternData
SetModule('CLK_DEBUG_CKXX')
ManualInject("SPETRIM_PLL_CMEM_E_BEGINCPUPKG_TAP_X_MIN_X_40_TDV",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("LOCK100X_X_CMEM_E_BEGINCPUPKG_TAP_X_MIN_X_40_TDV",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("FVCURVE_PLL_CMEM_E_BEGINCPUPKG_TAP_X_NOM_X_40_TDV",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("OPENLOOP_FLL_CMEM_E_BEGINCPUPKG_TAP_X_NOM_X_40_TDV",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("LOCK_X_CMEM_E_BEGINCPUPKG_TAP_X_NOM_X_40_TDV",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("VIEWPIN_X_FUNC_E_BEGINCPUPKG_TAP_X_NOM_X_40_TDV",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("DCSSHMOO_X_PATCFG_E_BEGINCPUPKG_X_X_X_X_X_TDV",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
