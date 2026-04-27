from pyqs import PortInject, ManualInject, SetModule, ctvData, portData, pinData, thermalData, userVar, cycleData, triggerData, patternData
SetModule('PTH_DLVR_CKPKGS7')
# List of test case names to inject
test_cases = [
    "DLVR_X_ANAMEAS_K_ENDCPUPKG_X_X_X_X_POWERLOSS",
    "DLVR_X_FUSECONFIG_K_STARTCPUPATMODSPKG_X_X_X_X_FUSECONFIG_ALL_X1",
    "DLVR_X_FUSECONFIG_K_STARTCPUPATMODSPKG_X_X_X_X_FUSECONFIG_ALL_X2",
    "DLVR_X_FUSECONFIG_K_STARTCPUPATMODSPKG_X_X_X_X_FUSECONFIG_ALL_X4"
]

# Loop through each test case and apply the same manual injection format
for test_case in test_cases:
    ManualInject(
        test_case,
        flowResult={},
        occurrence={'default': 'true'},
        actions=[
            portData(port="1", status="Pass"),
        ]
    )