from pyqs import PortInject, ManualInject, SetModule, ctvData, portData, pinData, thermalData, userVar, triggerData, patternData
SetModule('FUS_FUSEVLD_CKX')


ManualInject("FUSE_X_FUSEREAD_K_BEGINCPUPKG_X_X_X_X_VLD_UV_03",
    plist="cpu_fuse_hvm_vld_vbump",
    plistResult={},
    actions=[
        #ctvData(captureDirection = "RightToLeft",burst="0", pin="IPC::CPU_TDO", value="00000000000000000000000000001101"), #PASSING
        ctvData(captureDirection = "RightToLeft",burst="0", pin="CPU_TDO", value="0000000000000000000000000000110100000000000000000000000000001101"),
    	])
ManualInject("FUSE_X_FUSEREAD_K_BEGINCPUPKG_X_X_X_X_VLD_OV_09",
    plist="cpu_fuse_hvm_vld_vbump",
    plistResult={},
    actions=[
        #ctvData(captureDirection = "RightToLeft",burst="0", pin="IPC::CPU_TDO", value="00000000000000000000000000001101"), #PASSING
        ctvData(captureDirection = "RightToLeft",burst="0", pin="CPU_TDO", value="0000000000000000000000000000111000000000000000000000000000001110"),
    	])