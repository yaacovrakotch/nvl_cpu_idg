from pyqs import PortInject, ManualInject, SetModule, ctvData, portData, pinData, thermalData, userVar, triggerData, patternData
SetModule('TPI_DFF_XXX')
ManualInject("DFFX_X_DFFENDFLOW_K_FINAL_X_X_X_X_DFFVAL",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])