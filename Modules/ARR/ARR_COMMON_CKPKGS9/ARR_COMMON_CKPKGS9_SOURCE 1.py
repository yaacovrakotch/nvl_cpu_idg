from re import M
from pymtpl.por_methods import VminTC,DDGShmooTC, PrimeHvqkTestMethod, MbistVminTC, PrimeMbistTestMethod, AuxiliaryTC, ScreenTC,PrimeVirtualFuseExportToSharedStorageTestMethod,PrimePatConfigTestMethod,PrimeSampleRateTestMethod,MbistRasterRepairTC,PrimeScanHRYSSNTestMethod,PrimeScanSPOFITestMethod, RunCallback,PrimeRepairToFuseTestMethod
from pymtpl.core import Flow, Fitem, pPass, pFail, Initialize, NativeMultiTrial, AUTO, MTLdefault, InitializeNVLClass, Import, TrialParamSpec, Spec, MConfig

MODULE = "ARR_COMMON_CK816"

########################################################################
# INITIALIZE
########################################################################

output = InitializeNVLClass(
    outfile = MODULE,
    module_name = MODULE,
    tosversion = "tos4",
    binrange = [(6040,6049), (2141,2149)],
    #basenumrange=(2750, 2999),
    defaultthermalbin=(90976040, 90972149), #9097HB17
    defaultresetbin=(90601925, 90211949), #90HB1917/90HB1918
)

########################################################################
# IMPORT REQUIRED FILES
########################################################################

Import("ARR_COMMON_CK816.usrv")


########################
#   STARTCPUPATMODSPKGS   #
########################

def get_test_list_vfdm(
    flow,
    testinput
    ):
	
    test_list_vfdm = []	
    sample_test_vfdm = \
        PrimeVirtualFuseExportToSharedStorageTestMethod(name=f"ALL_X_VFDM_E_{flow}_X_X_X_X_VFDM_REBUILD",
               FdsSharedStorageKey = "CPU0_FUSE_EMB_VFDM_FDS_BINARY",
               FuseDataGap = "CPU0.VF_Heap_Data_Gap.VF_Heap_Data_Gap",
               FuseDescriptorGap = "CPU0.VF_Heap_Descriptor_Gap.VF_Heap_Descriptor_Gap",
               HcsSharedStorageKey = "CPU0_FUSE_EMB_VFDM_HCS_BINARY",
               Namespace = "CPU0",
               Tags = "",
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -60, goto="NEXT"),
               r1=pPass(goto="NEXT")))
    test_list_vfdm.append(sample_test_vfdm)
    
    return test_list_vfdm
    
def get_test_list_patconfig(
    flow,
    testinput
    ):
	
    test_list_patconfig = []	
    sample_test_patconfig = \
        PrimePatConfigTestMethod(name=f"ALL_CORE_X_E_{flow}_X_X_X_X_MBIST_DFF_READ",
               ConfigurationFile = "",
               SetPoint = "",
               SetPointsPlistMode = "Global",
               SetPointsPreInstance = "",
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -60, goto="NEXT"),
               r1=pPass(goto="NEXT")))
    test_list_patconfig.append(sample_test_patconfig)
    
    return test_list_patconfig

def get_test_list_pmtm_mbist_hry(
    flow,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_list_pmtm_mbist_hry = []	
    sample_test_pmtm_mbist_hry = \
        PrimeMbistTestMethod(name=f"ALL_X_HRY_E_{flow}_X_X_X_X_MBIST_HRY_INIT",
               Patlist='resetplb_1xbbxxxxxx_phase2_ccf_MCtpi_CA2P_hdmt2_ippkg_hvm_list',
               TimingsTc='CPU_IP_BASE::cpu_fun_timing_mts800_tstprtclk400_tck100',
               LevelsTc='CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min',
               BisrMode = 'uncompress',
               ClearVariables = 'all',
               FailCaptureCount = 10000000,
               LookupTableConfigurationFile = Spec("ARR_COMMON_Specs.HRY_LIST"),
               MappingConfigurationFile = Spec(f'GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "/Modules/ARR_COMMON/InputFiles/SharedStorageDFFMap.json"'),
               MbistTestMode = 'Initialize',
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -60, goto="NEXT"),
               r1=pPass(goto="NEXT"),
               r2=pFail(setbin = -60, goto="NEXT")))
    test_list_pmtm_mbist_hry.append(sample_test_pmtm_mbist_hry)
    
    return test_list_pmtm_mbist_hry

def get_test_list_aux_svhcs(
    flow,
    testinput
    ):
	
    test_list_aux_svhcs = []	
    sample_test_aux_svhcs = \
        AuxiliaryTC(name=f"X_CPU_GETDFF_E_{flow}_X_X_X_X_SVHCS",
               DataType = "String",
               Expression = "Bin2Hex([G.U.S.CPU0_FUSE_EMB_VFDM_HCS_BINARY])",
               ResultToken = "SVHCS",
               Storage = "DFF",
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -60, goto="NEXT"),
               r1=pPass(goto="NEXT")))
    test_list_aux_svhcs.append(sample_test_aux_svhcs)
    
    return test_list_aux_svhcs

def get_test_list_aux_svsdf1(
    flow,
    testinput
    ):
	
    test_list_aux_svsdf1 = []	
    sample_test_aux_svsdf1 = \
        AuxiliaryTC(name=f"X_CPU_GETDFF_E_{flow}_X_X_X_X_SVFDS1",
               DataType = "String",
               Expression = "Substring(Bin2Hex([G.U.S.CPU0_FUSE_EMB_VFDM_FDS_BINARY]),0,3800)",
               ResultToken = "SVFDS1",
               Storage = "DFF",
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -60, goto="NEXT"),
               r1=pPass(goto="NEXT")))
    test_list_aux_svsdf1.append(sample_test_aux_svsdf1)
    
    return test_list_aux_svsdf1

def get_test_list_aux_svsdf2(
    flow,
    testinput
    ):
	
    test_list_aux_svsdf2 = []	
    sample_test_aux_svsdf2 = \
        AuxiliaryTC(name=f"X_CPU_GETDFF_E_{flow}_X_X_X_X_SVFDS2",
               DataType = "String",
               Expression = "Substring(Bin2Hex([G.U.S.CPU0_FUSE_EMB_VFDM_FDS_BINARY]),3800,608)",
               ResultToken = "SVFDS2",
               Storage = "DFF",
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -60, goto="NEXT"),
               r1=pPass(goto="NEXT")))
    test_list_aux_svsdf2.append(sample_test_aux_svsdf2)
    
    return test_list_aux_svsdf2

def get_test_list_aux_setfds(
    flow,
    testinput
    ):
	
    test_list_aux_setfds = []	
    sample_test_aux_setfds = \
        AuxiliaryTC(name=f"ALL_X_AUX_E_{flow}_X_X_X_X_SET_FDS",
               DataType = "String",
               Expression = "Substring(Bin2Hex([G.U.S.CPU0_FUSE_EMB_VFDM_FDS_BINARY]),3800,608)",
               ResultToken = "SVFDS2",
               Storage = "DFF",
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -60, goto="NEXT"),
               r1=pPass(goto="NEXT")))
    test_list_aux_setfds.append(sample_test_aux_setfds)
    
    return test_list_aux_setfds

def get_test_list_fuseconfig(
    flow,
    testinput
    ):
	
    test_list_fuseconfig = []	
    sample_test_fuseconfig = \
        PrimePatConfigTestMethod(name=f"ALL_X_FUSECONFIG_K_{flow}_X_X_X_X_MBIST_RWA_PATCONFIG",
               ConfigurationFile = "",
               SetPoint = "MBIST_PER_DIE_RWA",
               SetPointsPlistMode = "Global",
               RegEx = "[gdx].*_longreset_fuseover.*_MC.*(arr|fun|fun.*|scn)",
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -60, goto="NEXT"),
               r1=pPass(goto="NEXT")))
    test_list_fuseconfig.append(sample_test_fuseconfig)
    
    return test_list_fuseconfig

def get_test_list_fuseconfig_rep(
    flow,
    testinput
    ):
	
    test_list_fuseconfig_rep = []	
    sample_test_fuseconfig_rep = \
        PrimePatConfigTestMethod(name=f"ALL_X_FUSECONFIG_K_{flow}_X_X_X_X_REPAIR",
               ConfigurationFile = Spec('GetEnvironmentVariable("FUSE_ROOT_DIR_CPU_INT")+ "/CSP/array_repair_perunit.PatConfigSetpoints.json"'),
               SetPoint = "CPU0_APPLY_VFDM",
               SetPointsPlistMode = "Global",
               RegEx = "[gdx].*_longreset_fuseover.*_MC.*(arr|fun|fun.*|scn)",
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -60, goto="NEXT"),
               r1=pPass(goto="NEXT")))
    test_list_fuseconfig_rep.append(sample_test_fuseconfig_rep)
    
    return test_list_fuseconfig_rep


##########################################
##### added by ARR_ATOM #######
##########################################

def get_aux_test(flow, OnSwitch, datatype, exp, storedata, st_type, comment):

    return AuxiliaryTC(
            name = f"ALL_X_AUX_K_{flow}_X_X_X_X_{comment}",
            BypassPort = OnSwitch,
	        DataType = datatype,
	        Expression = exp,
	        ResultToken = storedata,
            Storage = st_type)
#Custom Function For Ports Routing
def assign_callback_ports(edc, custom, name, testinfo, assignBin, port): 

    if edc == "Yes":
        return Fitem(name, testinfo, edc=True,
                     r0=pFail(setbin=assignBin, goto="NEXT"),
                     r1=pPass(goto="NEXT"))
    elif custom == "Yes":
        return Fitem(name, testinfo, edc=False, 
                     r0=pFail(setbin=assignBin, goto=port),
                     r1=pPass(goto=port))
    else:
        return Fitem(name, testinfo, edc=False, 
                     r0=pFail(setbin=assignBin, ret=0), 
                     r1=pPass(goto="NEXT"))


def get_ScreenTC(flow, OnSwitch, file_path, screen_data, comment):
    
    return ScreenTC(
            name = f"ALL_ATOM_SCREENTC_K_{flow}_X_X_X_X_{comment}",
            BypassPort = OnSwitch,
	        ScreenTestsFile = file_path,
            ScreenTestSet = screen_data)

def PatConfigTM(flow, OnSwitch, setupfile, vfdm, pat_regex, comment):

    return PrimePatConfigTestMethod(
            name = f"ALL_ATOM_PATCONFIG_K_{flow}_X_X_X_X_{comment}",
            BypassPort = OnSwitch,
	        ConfigurationFile = setupfile,
            SetPoint = vfdm,
            RegEx = pat_regex)

def create_raster_ext(input_dict):
			target_array_map = {
				"L2_DATA": "l2d",
				"L2_TAG": "l2_tag",
				"L2_STATE": "l2_sta",
				"L2_C6S": "l2_c6s",
				"L2_LRU": "l2_lru",
				"L2_DATA_RAS": "l2d",
				"L2_TAG_RAS": "l2_tag",
	
			}

def create_repairtofuse(flow, OnSwitch, setupfile, setupfile_1, comment):
			sample_test=PrimeRepairToFuseTestMethod(name = f"ALL_X_SCREEN_K_{flow}_X_X_X_X_ATOM_{comment}",
												BypassPort =OnSwitch,
												ResourcesFilePath = resources_file,
												RepairToFuseFilePath = repairtofuse_file,
												#ResourcesFilePath = "~HDMT_TPL_DIR/Modules/ARR_COMMON_CXX/InputFiles/ARL_ArrayMap_resource.json",
												#RepairToFuseFilePath = "~HDMT_TPL_DIR/Modules/ARR_COMMON_CXX/InputFiles/ARL_Repair_to_fuse.json",
												FuseNamespace = "CPU0",
												LogLevel = "Disabled",
												_fitem=Fitem("SAME", 
															edc=True,
															r1 = pPass(ret="1"),
															r0 = pFail(ret="1"),
															r2 = pPass(ret="1"))#,
															#rm1 = pFail(setbin=BIN98_DICT['ALL'], ret=-1), 
															#rm2 = pFail(setbin=BIN99_DICT['ALL'], ret=-2))
												)
			return sample_test


def create_VFDM(flow, OnSwitch, comment):
			sample_test=PrimeVirtualFuseExportToSharedStorageTestMethod(name = f"ALL_X_SCREEN_K_{flow}_X_X_X_X_ATOM_{comment}",
												BypassPort =OnSwitch,
												#ResourcesFilePath = resources_file,
												#RepairToFuseFilePath = repairtofuse_file,
                                                FdsSharedStorageKey = "CPU0_FUSE_EMB_VFDM_FDS_BINARY",
                                                FuseDataGap = "CPU0.VF_Heap_Data_Gap.VF_Heap_Data_Gap",
                                                FuseDescriptorGap = "CPU0.VF_Heap_Descriptor_Gap.VF_Heap_Descriptor_Gap",
                                                HcsSharedStorageKey = "CPU0_FUSE_EMB_VFDM_HCS_BINARY",
                                                Namespace = "CPU0",
                                                Tags = "",
												#ResourcesFilePath = "~HDMT_TPL_DIR/Modules/ARR_COMMON_CXX/InputFiles/ARL_ArrayMap_resource.json",
												#RepairToFuseFilePath = "~HDMT_TPL_DIR/Modules/ARR_COMMON_CXX/InputFiles/ARL_Repair_to_fuse.json",
												#FuseNamespace = "CPU0",
												LogLevel = "Disabled",
												_fitem=Fitem("SAME", 
															edc=True,
															r1 = pPass(ret="1"),
															r0 = pFail(ret="1"),
															r2 = pPass(ret="1"))#,
															#rm1 = pFail(setbin=BIN98_DICT['ALL'], ret=-1), 
															#rm2 = pFail(setbin=BIN99_DICT['ALL'], ret=-2))
												)
			return sample_test
########################
#   INIT               #
########################
def get_test_pinmap_parse(
    flow,
    testinput
    ):
	
   # Create an empty list that will contain the final list of the test
    test_list_callback = []	
    sample_test_callback = \
        RunCallback(name=f"ALL_X_UF_K_{flow}_X_X_X_X_PINMAP",
               Callback = "LoadPinMapFile",
               Parameters = "--decoder PinToSliceIndexDecoder --file ./Modules/ARR_COMMON/InputFiles/ARR.PinMap.json",
               BypassPort = testinput.get("Bypassport", -1),
               _fitem=Fitem('SAME',
               edc=testinput.get("ISEDC"),
               r0=pFail(setbin = -60, ret=0),
               r1=pPass(goto="NEXT")))
    test_list_callback.append(sample_test_callback)
    
    return test_list_callback   

#################################################################################
#							INIT SUBFLOW
#
#################################################################################
init_flow = "INIT"

pinmap_parse_tli = {"Bypassport": 1, "ISEDC": True}
pinmap_parse = get_test_pinmap_parse(init_flow, pinmap_parse_tli)

#INIT SUBFLOW
INIT_SUBFLOW = Flow(f'{MODULE}_INIT',
                                pinmap_parse
                              )  

#################################################################################
#							STARTCPUPATMODSPKG SUBFLOW
#
#	- STARTCPUPATMODSPKG flow will test reapir
#
#################################################################################

startcpupatomodspkg_flow = "STARTCPUPATMODSPKG"
startcpupatomodspkg_corner = "LFM"

#bypass_rules = Spec(MODULE+'_Rules.WRITE_DFF('+MODULE+'_Rules.RC_S1("RC_S1","PBIC_DAB"),"WriteDFF", '+MODULE+'_Rules.RC_S1("RC_S1","PBIC_DAB"))')
bypass_rules = "WriteDFF"
patmod_regex = Spec('"g.*_longreset_fuseoverrid.*_MCAarr.*"')
resources_file = Spec('GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "/Modules/ARR/ARR_COMMON_CK816/InputFiles/NVL_ArrayMap_ATOM.json"') #"~HDMT_TPL_DIR/Modules/ARR_COMMON_CXX/InputFiles/ARL_ArrayMap_resource.json",
repairtofuse_file = Spec('GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "/Modules/ARR/ARR_COMMON_CK816/InputFiles/NVL_Repair_to_fuse_ATOM.json"') #"~HDMT_TPL_DIR/Modules/ARR_COMMON_CXX/InputFiles/ARL_Repair_to_fuse.json",
arraydef_file = Spec('GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "/Modules/ARR/ARR_COMMON_CK816/InputFiles/NVL_ArrayDefinition_ATOM.json"')


####### ATOM TESTS ########
hex2bin = get_ScreenTC(startcpupatomodspkg_flow, 1, "./InputFiles/HextoBinTest.txt", bypass_rules, "CONVERT_HEX2BIN_VFDM_DFF")
#per_die_rwa = PatConfigTM(startcpupatomodspkg_flow, 1, "./InputFiles/APPLY_ATOM_RWA.FuseConfigSetPoints.json", "PER_DIE_RWA", patmod_regex, "RWA")
#repair_override = PatConfigTM(startcpupatomodspkg_flow, 1, Spec('GetEnvironmentVariable("FUSE_ROOT_DIR_CPU_INT")+ "/CSP/array_repair_perunit.PatConfigSetpoints.json"'), "CPU0_APPLY_VFDM", patmod_regex, "REPAIR")
repairtofuse_file = create_repairtofuse(startcpupatomodspkg_flow,1, resources_file, repairtofuse_file,"REP2FUSE")
VFDM_build = create_VFDM(startcpupatomodspkg_flow,1,"VFDM_REBUILD")

# PrimeVirtualFuseExportToSharedStorageTestMethod
startcpupatomodspkg_vfdm_tli = {"Bypassport": 1, "ISEDC": True}
startcpupatomodspkg_vfdm = get_test_list_vfdm(startcpupatomodspkg_flow, startcpupatomodspkg_vfdm_tli)

# Patconfig
startcpupatomodspkg_patconfig_tli = {"Bypassport": 1, "ISEDC": True}
startcpupatomodspkg_patconfig = get_test_list_patconfig(startcpupatomodspkg_flow, startcpupatomodspkg_patconfig_tli)

# PMTM test
startcpupatomodspkg_pmtm_mbist_hry_tli = {"Bypassport": 1, "ISEDC": True}
startcpupatomodspkg_pmtm_mbist_hry = get_test_list_pmtm_mbist_hry(startcpupatomodspkg_flow, startcpupatomodspkg_pmtm_mbist_hry_tli)

# Aux
startcpupatomodspkg_aux_svhcs_tli = {"Bypassport": 1, "ISEDC": True}
startcpupatomodspkg_aux_svhcs = get_test_list_aux_svhcs(startcpupatomodspkg_flow, startcpupatomodspkg_aux_svhcs_tli)

startcpupatomodspkg_aux_svsdf1_tli = {"Bypassport": 1, "ISEDC": True}
startcpupatomodspkg_aux_svsdf1 = get_test_list_aux_svsdf1(startcpupatomodspkg_flow, startcpupatomodspkg_aux_svsdf1_tli)

startcpupatomodspkg_aux_svsdf2_tli = {"Bypassport": 1, "ISEDC": True}
startcpupatomodspkg_aux_svsdf2 = get_test_list_aux_svsdf2(startcpupatomodspkg_flow, startcpupatomodspkg_aux_svsdf2_tli)

startcpupatomodspkg_aux_setfds_tli = {"Bypassport": 1, "ISEDC": True}
startcpupatomodspkg_aux_setfds = get_test_list_aux_setfds(startcpupatomodspkg_flow, startcpupatomodspkg_aux_setfds_tli)

# Fuseconfig
startcpupatomodspkg_fuseconfig_tli = {"Bypassport": 1, "ISEDC": True}
startcpupatomodspkg_fuseconfig = get_test_list_fuseconfig(startcpupatomodspkg_flow, startcpupatomodspkg_fuseconfig_tli)

startcpupatomodspkg_fuseconfig_rep_tli = {"Bypassport": 1, "ISEDC": True}
startcpupatomodspkg_fuseconfig_rep = get_test_list_fuseconfig_rep(startcpupatomodspkg_flow, startcpupatomodspkg_fuseconfig_rep_tli)


# STARTCPUPATMODSPKG SUBFLOW
STARTCPUPATMODSPKG_SUBFLOW = Flow(f'{MODULE}_STARTCPUPATMODSPKG',
                                 startcpupatomodspkg_fuseconfig,
                                 startcpupatomodspkg_pmtm_mbist_hry,
                                 startcpupatomodspkg_patconfig,
                                 assign_callback_ports("No", "No", "SAME", repairtofuse_file, -21, ''),
                                 startcpupatomodspkg_vfdm,
                                 startcpupatomodspkg_aux_svhcs,
                                 startcpupatomodspkg_aux_svsdf1,
                                 startcpupatomodspkg_aux_svsdf2,
                                 startcpupatomodspkg_aux_setfds,
                                 startcpupatomodspkg_fuseconfig_rep,
                                 assign_callback_ports("No", "No", "SAME", hex2bin, -21, ''),
                                 assign_callback_ports("No", "No", "SAME", VFDM_build, -21, '')
                                 
                                
                                 
                                 
                                 )
##############################################################################
#                          
#                          SUBFLOW END
#                                                  
##############################################################################

flow = "ENDCPUPKG"
fds = 'WRITE_CSVFDS'
hcs = 'WRITE_CSVHCS'
bypass_rules = Spec(MODULE+'_Rules.WRITE_DFF(1,1,1)')

write_fds = get_aux_test(flow, bypass_rules, "String", "Bin2Hex([G.U.S.CPU0_FUSE_EMB_VFDM_FDS_BINARY])", "CSVFDS", "DFF", fds)
write_hcs = get_aux_test(flow, bypass_rules, "String", "Bin2Hex([G.U.S.CPU0_FUSE_EMB_VFDM_HCS_BINARY])", "CSVHCS", "DFF", hcs)

ENDSUBFLOW_subflow = Flow(MODULE+"_"+flow,assign_callback_ports("No", "No", "SAME", write_fds, -21, ''),
                                           assign_callback_ports("No", "No", "SAME", write_hcs, -21, ''))                                 
