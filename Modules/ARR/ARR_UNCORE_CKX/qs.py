from pyqs import PortInject, ManualInject, SetModule, ctvData, portData, pinData, thermalData, userVar, triggerData, patternData

SetModule('IPC::ARR_UNCORE_CKX')

test_names = [
        "ALL_UNCORE_SB_K_BEGINCPUPKG_X_VNNAON_MIN_X_F1",
        "ALL_UNCORE_HRY_E_BEGINCPUPKG_TAP_VNNAON_X_X_X_ALL_PRESCREEN",
        "ALL_UNCORE_VFDM_K_BEGINCPUPKG_X_X_X_X_X_REPAIR_FUSE",
        "ALL_UNCORE_FUSECONFIG_K_BEGINCPUPKG_X_X_X_X_X_NOM",
        "ALL_UNCORE_HRY_K_BEGINCPUPKG_TAP_VNNAON_X_X_X_ALL_POSTSCREEN",
        "ALL_UNCORE_AUX_E_BEGINCPUPKG_X_X_X_X_X_SETBIN2_BIRA_BISR",
        "SSA_UNCORE_HRY_E_BEGINCPUPKG_TAP_VNNAON_X_X_REPAIR_PRESCREEN_BIRA_BISR_DMU",
        "SSA_UNCORE_AUX_E_BEGINCPUPKG_X_X_X_X_X_SETBIN2_BIRA_BISR1_DMU",
        "ALL_UNCORE_AUX_E_BEGINCPUPKG_X_X_X_X_X_NOM_CHECK_BIN",
        "ALL_UNCORE_AUX_E_BEGINCPUPKG_X_X_X_X_X_NOM_SETBIN2",
        "ALL_UNCORE_X_E_BEGINCPUPKG_X_X_X_X_X_X_MBIST_DFF_WRITE_NOM",
        "ALL_UNCORE_SB_K_BEGINCPUPKG_X_VNNAON_MIN_X_DUMMY",
        "ALL_UNCORE_SB_K_BEGINCPUPKG_X_VNNAON_MAX_X_F1",
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

