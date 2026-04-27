from pyqs import PortInject, ManualInject, SetModule, ctvData, portData, pinData, thermalData, userVar, cycleData, triggerData, patternData
SetModule('PTH_THRSOAK_XXX')
ManualInject("TD_X_APPLYTC_E_START_X_X_X_X",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_APPLYTC_E_START_X_X_X_X_SCOC",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_APPLYTC_E_START_X_X_X_X_PSMSETUP_CPU",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_APPLYTC_E_START_X_X_X_X_PSMSETUP_PCH",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_CS_E_START_X_X_X_X_DIODESOT_CPU",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_CS_E_START_X_X_X_X_DIODESOT_PCH",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_CS_E_START_X_X_X_X_DIODESOT",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_PARDATA_E_START_X_X_X_X",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_SOAK_K_START_X_X_X_X_THRSOAK",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_TDAU_K_START_X_X_X_X_DIEFORCE",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_UEISTREAM_E_START_X_X_X_X_STARTSTREAM",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_PARDATA_E_START_X_X_X_X_IDEALITYCALC",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_APPLYTC_E_LTTCRAMP_X_X_X_X_START_STOPCNV",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_AUX_E_LTTCRAMP_X_X_X_X_START_ENABLE_SOT",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_APPLYTC_E_LTTCRAMP_X_X_X_X_START_SCOCAL",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_TDAU_E_LTTCRAMP_X_X_X_X_START",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_AUX_E_LTTCRAMP_X_X_X_X_START_DISABLE_EOT",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_TDAU_K_LTTCRAMP_X_X_X_X_START_EOT",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_AUX_E_LTTCRAMP_X_X_X_X_START_ENABLE_LTTC",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_CS_E_LTTCRAMP_X_X_X_X_START_LTTC20_CPU",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_CS_E_LTTCRAMP_X_X_X_X_START_LTTC20_PCH",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_SOAK_K_LTTCRAMP_X_X_X_X_START_LTTCSOAK",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_AUX_E_LTTCRAMP_X_X_X_X_START_BENCHTOP_FORK",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_AUX_E_LTTCRAMP_X_X_X_X_START_DISABLE_SOT",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_AUX_E_LTTCRAMP_X_X_X_X_START_ENABLE_EOT",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_TDAU_K_LTTCRAMP_X_X_X_X_START_SOT",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_TDAU_E_LTTCRAMP_X_X_X_X_START_1",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_SCREEN_E_LTTCRAMP_X_X_X_X_PPRCHECK",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_AUX_E_LTTCRAMP_X_X_X_X_PPRCHECK",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_CS_E_LTTCRAMP_X_X_X_X_START_LTTC20",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])