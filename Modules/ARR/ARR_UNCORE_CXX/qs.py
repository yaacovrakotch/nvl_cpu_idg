from pyqs import PortInject, ManualInject, SetModule, ctvData, portData, pinData, thermalData, userVar, triggerData, patternData

SetModule('IPC::ARR_UNCORE_CKX')

test_names = [
        "ALL_UNCORE_SB_K_BEGINCPUNOM_X_VNNAON_X_X_F1_NOM",
        "ALL_UNCORE_SB_K_ENDCPUNOM_X_VNNAON_X_X_X_RETENTION",
        "ALL_UNCORE_SB_K_ENDCPUMAX_X_VNNAON_X_X_F1_MAX",
        "ARR_UNCORE_SHMOO_E_BEGINCPUNOM_X_X_X_X_SHMOO_FOR_DEDC",
]

# Populate a ManualInject for each test name
for test_name in test_names:
    ManualInject(test_name,
        flowResult={},
        occurrence={'default': 'true'},
        actions=[
            portData(port="1", status="Pass"),
        ]
    )

