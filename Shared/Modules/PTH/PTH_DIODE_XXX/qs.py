from pyqs import PortInject, ManualInject, SetModule, ctvData, portData, pinData, thermalData, userVar, cycleData, triggerData, patternData
SetModule('PTH_DIODE_XXX')
ManualInject("TD_X_APPLYTC_E_INIT_X_X_X_X_TDSETUP",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_APPLYTC_E_TESTPLANENDFLOW_X_X_X_X_PSMSTOP_CPU",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_APPLYTC_E_TESTPLANENDFLOW_X_X_X_X_PSMSTOP_PCH",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_APPLYTC_E_TESTPLANENDFLOW_X_X_X_X_STOPCNV",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_APPLYTC_E_TESTPLANSTARTFLOW_X_X_X_X_SCOCAL",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_AUX_E_FINAL_X_X_X_X_DISABLE_EOT",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_AUX_E_START_X_X_X_X_DISABLE_SOT",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_AUX_E_START_X_X_X_X_ENABLE_EOT",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_AUX_E_TESTPLANENDFLOW_X_X_X_X_DISABLE_EOT",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_AUX_E_TESTPLANSTARTFLOW_X_X_X_X_DISABLE_EOT",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_AUX_E_TESTPLANSTARTFLOW_X_X_X_X_ENABLE_SOT",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_CS_E_TESTPLANENDFLOW_X_X_X_X_DESOAK_CPU",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_CS_E_TESTPLANENDFLOW_X_X_X_X_DESOAK_PCH",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_CS_E_BEGIN_X_X_X_X_TEST_CPU",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_CS_E_BEGIN_X_X_X_X_TEST_PCH",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_CS_E_BEGIN_X_X_X_X_TEST",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("PrimeThermalControlSetInitTestMethod TD_X_CS_E_INIT_X_X_X_X_TCISETUP",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_CS_E_TESTPLANENDFLOW_X_X_X_X_DESOAK",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_SCREEN_E_INIT_X_X_X_X_BTCHECK",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_SCREEN_E_TESTPLANSTARTFLOW_X_X_X_X_BTCHECK_1",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_TDAU_E_FINAL_X_X_X_X_EOT",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_TDAU_E_FINAL_X_X_X_X_EOT_BT",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_TDAU_E_TESTPLANENDFLOW_X_X_X_X_EOT_TPEF",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_TDAU_E_FINAL_X_X_X_X",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_TDAU_E_START_X_X_X_X_SOT_BT",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_TDAU_E_TESTPLANENDFLOW_X_X_X_X",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_TDAU_E_TESTPLANENDFLOW_X_X_X_X_SOT",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_TDAU_K_START_X_X_X_X_SOT",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_UEISTREAM_E_LOTENDFLOW_X_X_X_X_STOP",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_UEISTREAM_E_LOTSTARTFLOW_X_X_X_X_START",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_AUX_E_FINAL_X_X_X_X_LTTC_FORK",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_AUX_E_TESTPLANSTARTFLOW_X_X_X_X_DISABLE_FACT",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_APPLYTC_E_LTTCRAMP_X_X_X_X_SCOCAL_FACT",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_APPLYTC_E_LTTCRAMP_X_X_X_X_STOPCNV_FACT",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_AUX_E_LTTCRAMP_X_X_X_X_ENABLE_SOT",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_TDAU_E_LTTCRAMP_X_X_X_X_FINAL",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_AUX_E_LTTCRAMP_X_X_X_X_FINAL_DISABLE_EOT",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_TDAU_K_LTTCRAMP_X_X_X_X_FINAL_EOT",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_AUX_E_LTTCRAMP_X_X_X_X_FINAL_ENABLE_LTTC",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_CS_E_LTTCRAMP_X_X_X_X_FINAL_FACT_CPU",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_CS_E_LTTCRAMP_X_X_X_X_FINAL_FACT_PCH",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_SOAK_K_LTTCRAMP_X_X_X_X_FINAL_FACTSOAK",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_AUX_E_LTTCRAMP_X_X_X_X_FINAL_BENCHTOP_FORK",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_TDAU_E_TESTPLANENDFLOW_X_X_X_X_EOT_TPEF_LTTC",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_TDAU_E_TESTPLANENDFLOW_X_X_X_X_LTTC",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_AUX_E_TESTPLANENDFLOW_X_X_X_X_LTTC_FORK",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("PTH_DIODE_MEASURE_E_TESTPLANENDFLOW_X_X_X_X_LOGPCSTOKENS",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_PAUSE_E_TESTPLANSTARTFLOW_X_X_X_X_PUC",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_CS_E_LTTCRAMP_X_X_X_X_FINAL_FACT",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("TD_X_SCREEN_E_START_X_X_X_X_IDEALITYCALC",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])