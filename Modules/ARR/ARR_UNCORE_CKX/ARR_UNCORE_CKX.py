from pymtpl.por_methods import VminTC, DDGShmooTC, PrimeHvqkTestMethod, PrimeMbistTestMethod, AuxiliaryTC, ScreenTC, PrimeVirtualFuseExportToSharedStorageTestMethod, PrimePatConfigTestMethod, PrimeSampleRateTestMethod, MbistRasterRepairTC, PrimeScanHRYSSNTestMethod, PrimeScanSPOFITestMethod, RunCallback, ApexTC
from pymtpl.core import Flow, Fitem, pPass, pFail, Initialize, NativeMultiTrial, AUTO, MTLdefault, InitializeNVLClass, Import, TrialParamSpec, Spec, MConfig, os
from pymtpl.binctr import NVLClass8dig

VOLTAGE_DOMAIN = "VNNAON"
product = "ARR_UNCORE"
MODULEPATH = 'GetEnvironmentVariable("~HDMT_TP_BASE_DIR")'

product_skus = ["CK816"]

for sku in product_skus:
    mtplname = f"{product}_{sku}"
    InitializeNVLClass(
        outfile=mtplname,
        module_name=mtplname,
        binrange=[(6115, 6124), (2115, 2124)],
        basenumrange=(2252, 2499),
        defaultthermalbin=90972410,  # Updated to start with 9097 as required by Mar'25 Pymtpl
        defaultresetbin=90221940,
        mttbinstrategy=NVLClass8dig,
    )

Import("ARR_UNCORE_CKX.usrv")

def get_test_list_uncore_vnnaon_f1_min(flow, corner, testinput):
    """
    Returns a list with the VminTC test for uncore VNNAON F1 min.
    """
    test_list_begcpupkgmin = []

    uncore_vnnaon_f1_min = VminTC(
        name=f"ALL_UNCORE_SB_K_{flow}_X_{VOLTAGE_DOMAIN.upper()}_MIN_X_F1",
        Patlist='resetplb_1xbbxxxxxx_phase2_ccf_MCtpi_CA2P_hdmt2_ippkg_hvm_list',
        TimingsTc='CPU_IP_BASE::cpu_fun_timing_mts800_tstprtclk400_tck100',
        LevelsTc='CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min',
        StartVoltages=Spec(f'ARR_UNCORE_{sku}_Specs.UNCORE_Startvoltage'),
        EndVoltageLimits=Spec(f'ARR_UNCORE_{sku}_Specs.UNCORE_Endvoltage'),
        VoltageTargets=Spec(f'ARR_UNCORE_{sku}_Specs.VNNAON_Voltagetargets'),
        ExecutionMode='SearchWithScoreboard',
        TestMode='Scoreboard',
        BaseNumbers=None if "SCR" in flow else AUTO,
        StepSize=0.02,
        FeatureSwitchSettings=Spec(f'ARR_UNCORE_{sku}_Specs.FeatureSwitch'),
        ForwardingMode='Input',
        PinMap=Spec(f'ARR_UNCORE_{sku}_Specs.Pattern_name_map'),
        ScoreboardEdgeTicks = Spec("toInteger(0)"),
        MaxFailsNum = Spec("toInteger(20)"),
        BypassPort=testinput.get("Bypassport", -1),
        _fitem=Fitem(
            'SAME',
            edc=testinput.get("ISEDC"),
            r0=pFail(setbin=-21, ret=0),
            r1=pPass(ret=1),
            r2=pFail(setbin=-21, ret=0),
            r3=pFail(setbin=-21, ret=0),
            r4=pFail(setbin=-21, ret=0),
            r5=pFail(setbin=-21, ret=0),
        )
    )
    test_list_begcpupkgmin.append(uncore_vnnaon_f1_min)
    return test_list_begcpupkgmin

#################################################################################
#							BEGINCPUPKG SUBFLOW
#
#################################################################################
begcpupkgmin_flow = "BEGINCPUPKG"
begcpupkgmin_corner = "LFM"

begcpupkgmin_uncore_vnnaon_f1_min_tli = {"Bypassport": 1, "Testmode": "Scoreboard", "ISEDC": False}
begcpupkgmin_uncore_vnnaon_f1_min = get_test_list_uncore_vnnaon_f1_min(
    begcpupkgmin_flow, begcpupkgmin_corner, begcpupkgmin_uncore_vnnaon_f1_min_tli
)

# BEGINCPU SUBFLOW
begcpupkgmin = Flow(
    f'ARR_UNCORE_{sku}_BEGINCPUPKG',
    begcpupkgmin_uncore_vnnaon_f1_min
)