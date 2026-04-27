from pyqs import PortInject, ManualInject, SetModule, ctvData, portData, pinData, thermalData, userVar, triggerData, patternData

SetModule('IPC::FUN_CCF_CX816')

test_names = [
    "SBFT_CCF_VMIN_K_F5XCCF_X_X_F5_X_FC_DRG",
    "SBFT_CCF_VMIN_K_F5XCCF_X_X_F5_X_FC_DRG_C0",
    "SBFT_CCF_VMIN_K_F5XCCF_X_X_F5_X_FC_DRG_C1",
    "SBFT_CCF_VMIN_K_F5XCCF_X_X_F5_X_FC_DRG_C2",
    "SBFT_CCF_VMIN_K_F5XCCF_X_X_F5_X_FC_DRG_C3",
    "SBFT_CCF_VMIN_K_F6XCCF_X_X_F6_X_FC_DRG",
    "SBFT_CCF_VMIN_K_F6XCCF_X_X_F6_X_FC_DRG_C0",
    "SBFT_CCF_VMIN_K_F6XCCF_X_X_F6_X_FC_DRG_C1",
    "SBFT_CCF_VMIN_K_F6XCCF_X_X_F6_X_FC_DRG_C2",
    "SBFT_CCF_VMIN_K_F6XCCF_X_X_F6_X_FC_DRG_C3",
    "SBFT_CCF_VMIN_K_F7XCCF_X_X_F7_X_FC_DRG",
    "SBFT_CCF_VMIN_K_F7XCCF_X_X_F7_X_FC_DRG_C0",
    "SBFT_CCF_VMIN_K_F7XCCF_X_X_F7_X_FC_DRG_C1",
    "SBFT_CCF_VMIN_K_F7XCCF_X_X_F7_X_FC_DRG_C2",
    "SBFT_CCF_VMIN_K_F7XCCF_X_X_F7_X_FC_DRG_C3",
    "SBFT_CCF_VMIN_K_FMINXCCF_X_X_FMIN_X_FC_DRG",
    "SBFT_CCF_VMIN_K_FMINXCCF_X_X_FMIN_X_FC_DRG_C0",
    "SBFT_CCF_VMIN_K_FMINXCCF_X_X_FMIN_X_FC_DRG_C1",
    "SBFT_CCF_VMIN_K_FMINXCCF_X_X_FMIN_X_FC_DRG_C2",
    "SBFT_CCF_VMIN_K_FMINXCCF_X_X_FMIN_X_FC_DRG_C3",
    "SBFT_CCF_VMIN_K_F1XCCF_X_X_F1_X_FC_DRG",
    "SBFT_CCF_VMIN_K_F1XCCF_X_X_F1_X_FC_DRG_C0",
    "SBFT_CCF_VMIN_K_F1XCCF_X_X_F1_X_FC_DRG_C1",
    "SBFT_CCF_VMIN_K_F1XCCF_X_X_F1_X_FC_DRG_C2",
    "SBFT_CCF_VMIN_K_F1XCCF_X_X_F1_X_FC_DRG_C3",
    "SBFT_CCF_VMIN_K_F2XCCF_X_X_F2_X_FC_DRG",
    "SBFT_CCF_VMIN_K_F2XCCF_X_X_F2_X_FC_DRG_C0",
    "SBFT_CCF_VMIN_K_F2XCCF_X_X_F2_X_FC_DRG_C1",
    "SBFT_CCF_VMIN_K_F2XCCF_X_X_F2_X_FC_DRG_C2",
    "SBFT_CCF_VMIN_K_F2XCCF_X_X_F2_X_FC_DRG_C3",
    "SBFT_CCF_VMIN_K_F3XCCF_X_X_F3_X_FC_DRG",
    "SBFT_CCF_VMIN_K_F3XCCF_X_X_F3_X_FC_DRG_C0",
    "SBFT_CCF_VMIN_K_F3XCCF_X_X_F3_X_FC_DRG_C1",
    "SBFT_CCF_VMIN_K_F3XCCF_X_X_F3_X_FC_DRG_C2",
    "SBFT_CCF_VMIN_K_F3XCCF_X_X_F3_X_FC_DRG_C3",
    "SBFT_CCF_VMIN_K_F4XCCF_X_X_F4_X_FC_DRG",
    "SBFT_CCF_VMIN_K_F4XCCF_X_X_F4_X_FC_DRG_C0",
    "SBFT_CCF_VMIN_K_F4XCCF_X_X_F4_X_FC_DRG_C1",
    "SBFT_CCF_VMIN_K_F4XCCF_X_X_F4_X_FC_DRG_C2",
    "SBFT_CCF_VMIN_K_F4XCCF_X_X_F4_X_FC_DRG_C3",
    "SBFT_CCF_VMIN_E_ENDCPU_X_X_VNOM_X_CCF_CCFBIST",
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

drng_test_names = [
    "DRNG_CCF_FUNC_K_ENDCPU_TAP_X_VNOM_X_CCF_DRNGTC_DRNG",
    "DRNG_CCF_FUNC_K_ENDCPU_TAP_X_VNOM_X_CCF_DRNGTC_FUSE_DRNG",
]
	
for test_name in drng_test_names:
    ManualInject(test_name,
        flowResult={},
        occurrence={'default': 'true'},
        actions=[
            portData(port="1", status="Pass"),
        ]
    )	
