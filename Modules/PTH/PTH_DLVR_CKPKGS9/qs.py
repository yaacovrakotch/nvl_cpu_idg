from pyqs import PortInject, ManualInject, SetModule, ctvData, portData, pinData, thermalData, userVar, cycleData, triggerData, patternData
SetModule('PTH_DLVR_CKPKGS9')
ManualInject("DLVR_X_ANAMEAS_K_ENDCPUPKG_X_X_X_X_POWERLOSS",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("DLVR_X_ANAMEAS_K_ENDCPUPKG_X_X_X_X_POWERLOSS_CPU1",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("DLVR_X_FUSECONFIG_K_STARTCPUPATMODSPKG_X_X_X_X_FUSECONFIG_ALL_X1",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("DLVR_X_FUSECONFIG_K_STARTCPUPATMODSPKG_X_X_X_X_FUSECONFIG_ALL_X2",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])
ManualInject("DLVR_X_FUSECONFIG_K_STARTCPUPATMODSPKG_X_X_X_X_FUSECONFIG_ALL_X4",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="1", status="Pass"),
    ])