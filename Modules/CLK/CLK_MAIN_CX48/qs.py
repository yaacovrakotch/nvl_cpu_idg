from pyqs import PortInject, ManualInject, SetModule, ctvData, portData, pinData, thermalData, userVar, cycleData, triggerData, patternData
SetModule('IPC::CLK_MAIN_CXXX')
ManualInject("FUSECHECK_X_CMEM_K_BEGINCPU_TAP_X_MIN_X_40_BBS",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("LOCK_X_CMEM_K_BEGINCPU_TAP_X_MIN_X_40_HVM",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("LOCK_X_CMEM_K_BEGINCPU_TAP_X_MIN_X_38_HVM",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("SETUP_X_SCREEN_K_BEGINCPU_X_X_MIN_X_X_X",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("FORK_X_SAMPLE_K_BEGINCPU_X_X_MIN_X_X_BBS ",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("FORK_X_SAMPLE_K_BEGINCPU_X_X_MIN_X_X_HVM",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("FORK_X_SAMPLE_K_BEGINCPU_X_X_MIN_X_X_SDC",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("LOCK_X_CMEM_K_BEGINCPUNOM_TAP_X_NOM_X_40_HVM",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("LOCK_X_CMEM_K_BEGINCPUNOM_TAP_X_NOM_X_38_HVM",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("FVCURVE_PLL_CMEM_E_BEGINCPUNOM_TAP_X_NOM_X_40_SDC",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("OPENLOOP_FLL_CMEM_E_BEGINCPUNOM_TAP_X_NOM_X_40_SDC",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("SETUP_X_SCREEN_K_BEGINCPUNOM_X_X_NOM_X_X_X",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("FORK_X_SAMPLE_K_BEGINCPUNOM_X_X_NOM_X_X_BBS",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("FORK_X_SAMPLE_K_BEGINCPUNOM_X_X_NOM_X_X_HVM",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("FORK_X_SAMPLE_K_BEGINCPUNOM_X_X_NOM_X_X_SDC",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("LOCK_X_CMEM_K_BEGINCPUMAX_TAP_X_MAX_X_40_HVM",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("LOCK_X_CMEM_K_BEGINCPUMAX_TAP_X_MAX_X_38_HVM",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("SETUP_X_SCREEN_K_BEGINCPUMAX_X_X_MAX_X_X_X",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("FORK_X_SAMPLE_K_BEGINCPUMAX_X_X_MAX_X_X_BBS",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("FORK_X_SAMPLE_K_BEGINCPUMAX_X_X_MAX_X_X_HVM",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("FORK_X_SAMPLE_K_BEGINCPUMAX_X_X_MAX_X_X_SDC",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
  