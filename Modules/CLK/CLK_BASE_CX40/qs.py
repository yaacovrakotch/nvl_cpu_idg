from pyqs import PortInject, ManualInject, SetModule, ctvData, portData, pinData, thermalData, userVar, cycleData, triggerData, patternData
SetModule('IPC::CLK_BASE_CXXX')
ManualInject("CLK_X_PATMOD_K_INIT_X_X_X_X_CPU",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("RESETCHECK_X_CMEM_E_STARTANA1CPU_TAP_X_MIN_X_40_BBS",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("CONFIGREAD_X_CMEM_E_STARTANA1CPU_TAP_X_MIN_X_40_BBS",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("STATUSREAD_X_CMEM_E_STARTANA1CPU_TAP_X_MIN_X_40_BBS",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("VREFTRIM_X_CMEM_K_STARTANA1CPU_TAP_X_MIN_X_40_HVM",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("VREFTRIM_X_SCREEN_K_STARTANA1CPU_X_X_X_X_X_HVM",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("VCCPLL_X_CMEM_K_STARTANA1CPU_TAP_X_MIN_X_40_HVM",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("IREFTRIM_X_CMEM_K_STARTANA1CPU_TAP_X_MIN_X_40_HVM",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("IREFTRIM_X_SCREEN_K_STARTANA1CPU_X_X_X_X_X_HVM",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("DCATRIM_X_CMEM_K_STARTANA1CPU_TAP_X_MIN_X_40_HVM",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("DCATRIM_X_SCREEN_K_STARTANA1CPU_X_X_X_X_X_HVM",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("AFSTRIM_X_CMEM_K_STARTANA1CPU_TAP_X_MIN_X_40_HVM",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("AFSTRIM_X_SCREEN_K_STARTANA1CPU_X_X_X_X_X_HVM",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("VREFTRIM_X_CMEM_E_STARTANA1CPU_TAP_X_MIN_X_40_SDC",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("IREFTRIM_X_CMEM_E_STARTANA1CPU_TAP_X_MIN_X_40_SDC",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("DCATRIM_X_CMEM_E_STARTANA1CPU_TAP_X_MIN_X_40_SDC",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("AFSTRIM_X_CMEM_E_STARTANA1CPU_TAP_X_MIN_X_40_SDC",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])