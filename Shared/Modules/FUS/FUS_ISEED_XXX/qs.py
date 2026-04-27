from pyqs import PortInject, ManualInject, SetModule, ctvData, portData, pinData, thermalData, userVar, triggerData, patternData
SetModule('FUS_ISEED_XXX')
ManualInject("FUSE_X_CTVDECODER_K_STARTSHAREDRAILSNOM_X_X_X_X_TAP_STATUS",
    plist="IPP::pcd_dfxagg_read_hvm_status_csr",
    plistResult={},
    actions=[
        ctvData(burst="0", pin="PCD_TDO", value="1001000000000000101111000000000011110000101000010000001011100110"),
    ])
ManualInject("FUSE_X_SCREEN_K_STARTSHAREDRAILSNOM_X_X_X_X_UNIT_INFO_DECODE",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="3", status="Pass"),
    ])
ManualInject("FUSE_X_CTVDECODER_K_STARTSHAREDRAILSNOM_X_X_X_X_TAP_STATUS_PCDH",
    plist="IPP::pcd_dfxagg_read_hvm_status_csr",
    plistResult={},
    actions=[
        ctvData(burst="0", pin="PCD_TDO", value="1001000000000000101111000000000011110000101000010000001011100110"),
    ])
ManualInject("FUSE_X_SCREEN_K_STARTSHAREDRAILSNOM_X_X_X_X_UNIT_INFO_DECODE_PCDH",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="3", status="Pass"),
    ])
ManualInject("FUSE_X_CTVDECODER_K_FACT_X_X_X_X_TAP_STATUS_PCDH",
    plist="IPP::pcd_dfxagg_read_hvm_status_csr",
    plistResult={},
    actions=[
        ctvData(burst="0", pin="PCD_TDO", value="1001000000000000101111000000000011110000101000010000001011100110"),
    ])
ManualInject("FUSE_X_SCREEN_K_FACT_X_X_X_X_UNIT_INFO_DECODE_PCDH",
    flowResult={},
    occurrence={'default': 'true'},
    actions=[
        portData(port="3", status="Pass"),
    ])