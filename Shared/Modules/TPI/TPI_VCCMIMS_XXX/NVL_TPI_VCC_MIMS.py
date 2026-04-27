# ENG TP Path: I:\engineering\dev\sctp\tptorrent\hdmxprogs\arl\MIMS_PYMTPL_DEBUG
# Import the necessary classes from Pymtpl
from pymtpl.por_methods import ScreenTC, RunCallback
from pymtpl.core import Flow, Fitem, pPass, pFail, Initialize, MultiTrial, AUTO, MTLdefault, InitializeMTL, InitializeNVLClass, Import, TrialParamSpec, Spec

# Initialize the module by defining the output mtpl path and module name
InitializeNVLClass('TPI_VCCMIMS_XXX', 'TPI_VCCMIMS_XXX')

# Add the necessary files to import in your mtpl
Import("TPI_VCCMIMS_XXX.usrv")

# MIMS pin list
MIMS_pin_list = ["VCCIA", "VCCIO", "VCCIO_FLTR", "VCCSA", "VNNAON", "VNNAON_FLTR", "VDD2", "VCCGT", "CPU0_EXT_BGREF_TRIM_ANA", "CPU1_EXT_BGREF_TRIM_ANA", "V1P8", "V1P8_CPU", "V1P8_FLTR", "VCCIO_OUT_SVID", "VCCDFT_PCD", 
                    "V1P8_FLTRA", "V1P8_FLTRB", "GCD_BGR_TRIM_REF", "HUB_EXT_BGREF_TRIM_ANA", "VCCLPECORE", "VDDQ", "HUB_GCD_EXT_BGREF_TRIM_ANA", "VCCIO_FLTR_H", "VNNAON_FLTR_H"]
#ITUFF_pin_list = ["VLOAD_ATOM_0_START", "VLOAD_ATOM_0_LTTC", "VLOAD_ATOM_1_START", "VLOAD_ATOM_1_LTTC", "VLOAD_CORE_0_START", "VLOAD_CORE_0_LTTC", "VLOAD_CORE_1_START", "VLOAD_CORE_1_LTTC", "VLOAD_CORE_2_START", "VLOAD_CORE_2_LTTC", "VLOAD_CORE_3_START", "VLOAD_CORE_3_LTTC", "VLOAD_CORE_4_START", "VLOAD_CORE_4_LTTC", "VLOAD_CORE_5_START", "VLOAD_CORE_5_LTTC", "VLOAD_RING_START", "VLOAD_RING_LTTC", "VNNAON_HC_START", "VNNAON_HC_LTTC", "VCCSA_HC_START", "VCCSA_HC_LTTC", "VCCIO_HC_START", "VCCIO_HC_LTTC", "VCC1P8_LC_START", "VCC1P8_LC_LTTC", "VCC1P8_QUIET_1_LC_START", "VCC1P8_QUIET_1_LC_LTTC", "VCC1P8_CPU_LC_START", "VCC1P8_CPU_LC_LTTC", "VCCGT_HC_START", "VCCGT_HC_LTTC", "VCCFPGM_GCD_LC_START", "VCCFPGM_GCD_LC_LTTC", "VCCIA_HC_START", "VCCIA_HC_LTTC"]

ITUFF_pin_list = ["VCCIA_START", "VCCIO_LTTC", "VCCIO_FLTR_START", "VCCSA_LTTC", "VNNAON_START", "VNNAON_FLTR_LTTC", "VDD2_START", "VCCGT_LTTC", "CPU0_EXT_BGREF_TRIM_ANA_START", 
                "CPU1_EXT_BGREF_TRIM_ANA_LTTC", "V1P8_START", "V1P8_CPU_LTTC", "V1P8_FLTR_START", "VCCIO_OUT_SVID_LTTC", "VCCDFT_PCD_START", "VCCIA_LTTC", "VCCIO_START", "VCCIO_FLTR_LTTC", 
                "VCCSA_START", "VNNAON_LTTC", "VNNAON_FLTR_START", "VDD2_LTTC", "VCCGT_START", "CPU0_EXT_BGREF_TRIM_ANA_LTTC", "CPU1_EXT_BGREF_TRIM_ANA_START", "V1P8_LTTC", 
                "V1P8_CPU_START", "V1P8_FLTR_LTTC", "VCCIO_OUT_SVID_START", "VCCDFT_PCD_LTTC","V1P8_FLTRA_START", "V1P8_FLTRB_START", "GCD_BGR_TRIM_REF_START", "HUB_EXT_BGREF_TRIM_ANA_START", "VCCLPECORE_START",
				"VDDQ_START", "VCCIO_FLTR_H_START", "VNNAON_FLTR_H_START","V1P8_FLTRA_LTTC", "V1P8_FLTRB_LTTC", "GCD_BGR_TRIM_REF_LTTC", "HUB_EXT_BGREF_TRIM_ANA_LTTC",
				"VCCLPECORE_LTTC", "VDDQ_LTTC", "VCCIO_FLTR_H_LTTC", "VNNAON_FLTR_H_LTTC"]
	

# Created an empty test list that will be appended by each test created in the loop
MIMS_test_list = []
ITUFF_test_list = []

# Bypassport dictionary 

BypassPort_dict = {
                    "Default": 1,
                    "CPU1_EXT_BGREF_TRIM_ANA": Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'),
                    "CPU1_EXT_BGREF_TRIM_ANA_START": Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'),
                    "CPU1_EXT_BGREF_TRIM_ANA_LTTC": Spec('__shared__::TpRule.If_CLASS_NVL_S52C(1,1)'),
                    "V1P8_FLTRA": Spec('TPI_VCCMIMS_XXX_Rules.If_M_PKGs(1,1)'), 
					"V1P8_FLTRA_LTTC": Spec('TPI_VCCMIMS_XXX_Rules.If_M_PKGs(1,1)'), 
					"V1P8_FLTRA_START": Spec('TPI_VCCMIMS_XXX_Rules.If_M_PKGs(1,1)'), 
                    "V1P8_FLTRB": Spec('TPI_VCCMIMS_XXX_Rules.If_M_PKGs(1,1)'),
					"V1P8_FLTRB_LTTC": Spec('TPI_VCCMIMS_XXX_Rules.If_M_PKGs(1,1)'),
					"V1P8_FLTRB_START": Spec('TPI_VCCMIMS_XXX_Rules.If_M_PKGs(1,1)'),
                    "GCD_BGR_TRIM_REF": Spec('TPI_VCCMIMS_XXX_Rules.If_M_PKGs(1,1)'),
					"GCD_BGR_TRIM_REF_LTTC": Spec('TPI_VCCMIMS_XXX_Rules.If_M_PKGs(1,1)'),
					"GCD_BGR_TRIM_REF": Spec('TPI_VCCMIMS_XXX_Rules.If_M_PKGs(1,1)'),
                    "HUB_EXT_BGREF_TRIM_ANA": Spec('TPI_VCCMIMS_XXX_Rules.If_M_PKGs(1,1)'),
					"HUB_EXT_BGREF_TRIM_ANA_LTTC": Spec('TPI_VCCMIMS_XXX_Rules.If_M_PKGs(1,1)'),
					"HUB_EXT_BGREF_TRIM_ANA_START": Spec('TPI_VCCMIMS_XXX_Rules.If_M_PKGs(1,1)'),
                    "VCCLPECORE": Spec('TPI_VCCMIMS_XXX_Rules.If_M_PKGs(1,1)'),
					"VCCLPECORE_LTTC": Spec('TPI_VCCMIMS_XXX_Rules.If_M_PKGs(1,1)'),
					"VCCLPECORE_START": Spec('TPI_VCCMIMS_XXX_Rules.If_M_PKGs(1,1)'),
                    "VDDQ": Spec('TPI_VCCMIMS_XXX_Rules.If_M_PKGs(1,1)'), 
					"VDDQ_LTTC": Spec('TPI_VCCMIMS_XXX_Rules.If_M_PKGs(1,1)'), 
					"VDDQ_START": Spec('TPI_VCCMIMS_XXX_Rules.If_M_PKGs(1,1)'), 
                    "VCCIO_FLTR_H": Spec('TPI_VCCMIMS_XXX_Rules.If_M_PKGs(1,1)'),
					"VCCIO_FLTR_H_LTTC": Spec('TPI_VCCMIMS_XXX_Rules.If_M_PKGs(1,1)'),
					"VCCIO_FLTR_H_START": Spec('TPI_VCCMIMS_XXX_Rules.If_M_PKGs(1,1)'),
                    "VNNAON_FLTR_H": Spec('TPI_VCCMIMS_XXX_Rules.If_M_PKGs(1,1)'),
					"VNNAON_FLTR_H_LTTC": Spec('TPI_VCCMIMS_XXX_Rules.If_M_PKGs(1,1)'),
					"VNNAON_FLTR_H_START": Spec('TPI_VCCMIMS_XXX_Rules.If_M_PKGs(1,1)'),
				}

# Dictionary for ScreenTestSet
ScreenTestSet_dict = {
                "Default": "",
				"V1P8": "MIMSHORT_SCREEN_V1P8",
				"V1P8_CPU": "MIMSHORT_SCREEN_V1P8_CPU",
				"V1P8_FLTR": "MIMSHORT_SCREEN_V1P8_FLTR",
				"VCCIO": "MIMSHORT_SCREEN_VCCIO",
				"VCCIO_FLTR": "MIMSHORT_SCREEN_VCCIO_FLTR",
				"VCCIO_FLTR_H": "MIMSHORT_SCREEN_VCCIO_FLTR_H",
				"VCCSA": "MIMSHORT_SCREEN_VCCSA",
				"VNNAON": "MIMSHORT_SCREEN_VNNAON",
				"VNNAON_FLTR": "MIMSHORT_SCREEN_VNNAON_FLTR",
				"VNNAON_FLTR_H": "MIMSHORT_SCREEN_VNNAON_FLTR_H",
				"VCCIO_OUT_SVID": "MIMSHORT_SCREEN_VCCIO_OUT_SVID",
				"VDD2": "MIMSHORT_SCREEN_VDD2",
				"VCCGT": "MIMSHORT_SCREEN_VCCGT",
				"VCCDFT_PCD": "MIMSHORT_SCREEN_VCCDFT_PCD",
				"VCCIA": "MIMSHORT_SCREEN_VCCIA",
				"CPU0_EXT_BGREF_TRIM_ANA": "MIMSHORT_SCREEN_CPU0_EXT_BGREF_TRIM_ANA",
				"CPU1_EXT_BGREF_TRIM_ANA": "MIMSHORT_SCREEN_CPU1_EXT_BGREF_TRIM_ANA",
                "V1P8_FLTRA": "MIMSHORT_SCREEN_V1P8_FLTRA", 
                "V1P8_FLTRB": "MIMSHORT_SCREEN_V1P8_FLTRB", 
                "GCD_BGR_TRIM_REF": "MIMSHORT_SCREEN_GCD_BGR_TRIM_REF",
                "HUB_EXT_BGREF_TRIM_ANA": "MIMSHORT_SCREEN_HUB_EXT_BGREF_TRIM_ANA",
                "VCCLPECORE": "MIMSHORT_SCREEN_VCCLPECORE", 
                "VDDQ": "MIMSHORT_SCREEN_VDDQ", 
                "VCCIO_FLTR_H": "MIMSHORT_SCREEN_VCCIO_FLTR_H", 
                "VNNAON_FLTR_H": "MIMSHORT_SCREEN_VNNAON_FLTR_H",
                "HUB_GCD_EXT_BGREF_TRIM_ANA": "MIMSHORT_SCREEN_HUB_GCD_EXT_BGREF_TRIM_ANA"                
                   }

				   
ITUFF_Parameters_dict = {				   
				   
					"VCCIA_START": "--body_type strgval --body_data G.U.D.VCCIA_START^IPC::VCCIA --tname_suf _VCCIA_START",
					"VCCIO_LTTC": "--body_type strgval --body_data G.U.D.VCCIO_LTTC^VCCIO --tname_suf _VCCIO_LTTC",
					"VCCIO_FLTR_START": "--body_type strgval --body_data G.U.D.VCCIO_FLTR_START^VCCIO_FLTR --tname_suf _VCCIO_FLTR_START",
					"VCCSA_LTTC": "--body_type strgval --body_data G.U.D.VCCSA_LTTC^IPH::VCCSA --tname_suf _VCCSA_LTTC",
					"VNNAON_START": "--body_type strgval --body_data G.U.D.VNNAON_START^VNNAON --tname_suf _VNNAON_START",
					"VNNAON_FLTR_LTTC": "--body_type strgval --body_data G.U.D.VNNAON_FLTR_LTTC^VNNAON_FLTR --tname_suf _VNNAON_FLTR_LTTC",
					"VDD2_START": "--body_type strgval --body_data G.U.D.VDD2_START^IPH::VDD2 --tname_suf _VDD2_START",
					"VCCGT_LTTC": "--body_type strgval --body_data G.U.D.VCCGT_LTTC^IPG::VCCGT --tname_suf _VCCGT_LTTC",
					"CPU0_EXT_BGREF_TRIM_ANA_START": "--body_type strgval --body_data G.U.D.CPU0_EXT_BGREF_TRIM_ANA_START^IPC::CPU0_EXT_BGREF_TRIM_ANA --tname_suf _CPU0_EXT_BGREF_TRIM_ANA_START",
					"CPU1_EXT_BGREF_TRIM_ANA_LTTC": "--body_type strgval --body_data G.U.D.CPU1_EXT_BGREF_TRIM_ANA_LTTC^IPC::CPU1_EXT_BGREF_TRIM_ANA --tname_suf _CPU1_EXT_BGREF_TRIM_ANA_LTTC",
					"V1P8_START": "--body_type strgval --body_data G.U.D.V1P8_START^V1P8 --tname_suf _V1P8_START",
					"V1P8_CPU_LTTC": "--body_type strgval --body_data G.U.D.V1P8_CPU_LTTC^V1P8_CPU --tname_suf _V1P8_CPU_LTTC",
					"V1P8_FLTR_START": "--body_type strgval --body_data G.U.D.V1P8_FLTR_START^V1P8_FLTR --tname_suf _V1P8_FLTR_START",
					"VCCIO_OUT_SVID_LTTC": "--body_type strgval --body_data G.U.D.VCCIO_OUT_SVID_LTTC^VCCIO_OUT_SVID --tname_suf _VCCIO_OUT_SVID_LTTC",
					"VCCDFT_PCD_START": "--body_type strgval --body_data G.U.D.VCCDFT_PCD_START^IPP::VCCDFT_PCD --tname_suf _VCCDFT_PCD_START",
					"VCCIA_LTTC": "--body_type strgval --body_data G.U.D.VCCIA_LTTC^IPC::VCCIA --tname_suf _VCCIA_LTTC",
					"VCCIO_START": "--body_type strgval --body_data G.U.D.VCCIO_START^VCCIO --tname_suf _VCCIO_START",
					"VCCIO_FLTR_LTTC": "--body_type strgval --body_data G.U.D.VCCIO_FLTR_LTTC^VCCIO_FLTR --tname_suf _VCCIO_FLTR_LTTC",
					"VCCSA_START": "--body_type strgval --body_data G.U.D.VCCSA_START^IPH::VCCSA --tname_suf _VCCSA_START",
					"VNNAON_LTTC": "--body_type strgval --body_data G.U.D.VNNAON_LTTC^VNNAON --tname_suf _VNNAON_LTTC",
					"VNNAON_FLTR_START": "--body_type strgval --body_data G.U.D.VNNAON_FLTR_START^VNNAON_FLTR --tname_suf _VNNAON_FLTR_START",
					"VDD2_LTTC": "--body_type strgval --body_data G.U.D.VDD2_LTTC^IPH::VDD2 --tname_suf _VDD2_LTTC",
					"VCCGT_START": "--body_type strgval --body_data G.U.D.VCCGT_START^IPG::VCCGT --tname_suf _VCCGT_START",
					"CPU0_EXT_BGREF_TRIM_ANA_LTTC": "--body_type strgval --body_data G.U.D.CPU0_EXT_BGREF_TRIM_ANA_LTTC^IPC::CPU0_EXT_BGREF_TRIM_ANA --tname_suf _CPU0_EXT_BGREF_TRIM_ANA_LTTC",
					"CPU1_EXT_BGREF_TRIM_ANA_START": "--body_type strgval --body_data G.U.D.CPU1_EXT_BGREF_TRIM_ANA_START^IPC::CPU1_EXT_BGREF_TRIM_ANA --tname_suf _CPU1_EXT_BGREF_TRIM_ANA_START",
					"V1P8_LTTC": "--body_type strgval --body_data G.U.D.V1P8_LTTC^V1P8 --tname_suf _V1P8_LTTC",
					"V1P8_CPU_START": "--body_type strgval --body_data G.U.D.V1P8_CPU_START^V1P8_CPU --tname_suf _V1P8_CPU_START",
					"V1P8_FLTR_LTTC": "--body_type strgval --body_data G.U.D.V1P8_FLTR_LTTC^V1P8_FLTR --tname_suf _V1P8_FLTR_LTTC",
					"VCCIO_OUT_SVID_START": "--body_type strgval --body_data G.U.D.VCCIO_OUT_SVID_START^VCCIO_OUT_SVID --tname_suf _VCCIO_OUT_SVID_START",
					"VCCDFT_PCD_LTTC": "--body_type strgval --body_data G.U.D.VCCDFT_PCD_LTTC^IPP::VCCDFT_PCD --tname_suf _VCCDFT_PCD_LTTC",                    
                    "V1P8_FLTRA_START": "--body_type strgval --body_data G.U.D.V1P8_FLTRA_START^V1P8_FLTRA --tname_suf _V1P8_FLTRA_START",
					"V1P8_FLTRA_LTTC": "--body_type strgval --body_data G.U.D.V1P8_FLTRA_LTTC^V1P8_FLTRA --tname_suf _V1P8_FLTRA_LTTC",
                    "V1P8_FLTRB_START": "--body_type strgval --body_data G.U.D.V1P8_FLTRB_START^V1P8_FLTRB --tname_suf _V1P8_FLTRB_START",
					"V1P8_FLTRB_LTTC": "--body_type strgval --body_data G.U.D.V1P8_FLTRB_LTTC^V1P8_FLTRB --tname_suf _V1P8_FLTRB_LTTC",
                    "VCCIO_FLTR_H_START": "--body_type strgval --body_data G.U.D.VCCIO_FLTR_H_START^VCCIO_FLTR_H --tname_suf _VCCIO_FLTR_H_START",
					"VCCIO_FLTR_H_LTTC": "--body_type strgval --body_data G.U.D.VCCIO_FLTR_H_LTTC^VCCIO_FLTR_H --tname_suf _VCCIO_FLTR_H_LTTC",
                    "VNNAON_FLTR_H_START": "--body_type strgval --body_data G.U.D.VNNAON_FLTR_H_START^VNNAON_FLTR_H --tname_suf _VNNAON_FLTR_H_START",
					"VNNAON_FLTR_H_LTTC": "--body_type strgval --body_data G.U.D.VNNAON_FLTR_H_LTTC^VNNAON_FLTR_H --tname_suf _VNNAON_FLTR_H_LTTC",
                    "HUB_GCD_EXT_BGREF_TRIM_ANA_START": "--body_type strgval --body_data G.U.D.HUB_GCD_EXT_BGREF_TRIM_ANA_START^HUB_GCD_EXT_BGREF_TRIM_ANA --tname_suf _HUB_GCD_EXT_BGREF_TRIM_ANA_START",
					"HUB_GCD_EXT_BGREF_TRIM_ANA_LTTC": "--body_type strgval --body_data G.U.D.HUB_GCD_EXT_BGREF_TRIM_ANA_LTTC^HUB_GCD_EXT_BGREF_TRIM_ANA --tname_suf _HUB_GCD_EXT_BGREF_TRIM_ANA_LTTC",                     
                    "VDDQ_START": "--body_type strgval --body_data G.U.D.VDDQ_START^IPH::VDDQ --tname_suf _VDDQ_START",
                    "VDDQ_LTTC": "--body_type strgval --body_data G.U.D.VDDQ_LTTC^IPH::VDDQ --tname_suf _VDDQ_LTTC",
                    "VCCLPECORE_START": "--body_type strgval --body_data G.U.D.VCCLPECORE_START^IPH::VCCLPECORE --tname_suf _VCCLPECORE_START",
                    "VCCLPECORE_LTTC": "--body_type strgval --body_data G.U.D.VCCLPECORE_LTTC^IPH::VCCLPECORE --tname_suf _VCCLPECORE_LTTC",
                    "HUB_EXT_BGREF_TRIM_ANA_START": "--body_type strgval --body_data G.U.D.HUB_EXT_BGREF_TRIM_ANA_START^IPH::HUB_EXT_BGREF_TRIM_ANA --tname_suf _HUB_EXT_BGREF_TRIM_ANA_START",
                    "HUB_EXT_BGREF_TRIM_ANA_LTTC": "--body_type strgval --body_data G.U.D.HUB_EXT_BGREF_TRIM_ANA_LTTC^IPH::HUB_EXT_BGREF_TRIM_ANA --tname_suf _HUB_EXT_BGREF_TRIM_ANA_LTTC",
                    "GCD_BGR_TRIM_REF_START": "--body_type strgval --body_data G.U.D.GCD_BGR_TRIM_REF_START^IPG::GCD_BGR_TRIM_REF --tname_suf _GCD_BGR_TRIM_REF_START",
                    "GCD_BGR_TRIM_REF_LTTC": "--body_type strgval --body_data G.U.D.GCD_BGR_TRIM_REF_LTTC^IPG::GCD_BGR_TRIM_REF --tname_suf _GCD_BGR_TRIM_REF_LTTC",                  

				   }

#LTTC_pin_list = ["VCCIA", "VCCIO", "VCCIO_FLTR", "VCCSA", "VNNAON", "VNNAON_FLTR", "VDD2", "VCCGT", "CPU0_EXT_BGREF_TRIM_ANA", "CPU1_EXT_BGREF_TRIM_ANA", "V1P8", "V1P8_CPU", "V1P8_FLTR", "VCCIO_OUT_SVID", "VCCDFT_PCD", 
#                   "V1P8_FLTRA", "V1P8_FLTRB", "GCD_BGR_TRIM_REF", "HUB_EXT_BGREF_TRIM_ANA", "VCCLPECORE", "VDDQ", "HUB_GCD_EXT_BGREF_TRIM_ANA", "VCCIO_FLTR_H", "VNNAON_FLTR_H"]
				   
###Define test instance loop for each item in the pin_list
# VCC MIMs Screen Tests
for pin in MIMS_pin_list:
    screen_test = ScreenTC(
                        name = f"CONT_X_SCREEN_K_LTTCCOMMON_X_X_X_X_MIMS_{pin}",
                        ScreenTestSet = ScreenTestSet_dict.get(pin),
                        ScreenTestsFile = "./InputFiles/VCC_MIMS_Screentest.txt",
						BypassPort = BypassPort_dict.get(pin, BypassPort_dict["Default"]),
                        _fitem = Fitem('SAME', r0 = pFail(setbin = 90910800, ret = 0), r2 = pFail(setbin = 90910800, ret = 0))
                   )
    MIMS_test_list.append(screen_test)

# Print to ituff instances to print START and LTTC measurements
for pin in ITUFF_pin_list:
    pin_test = RunCallback(
                        name = f"CTRL_X_RUNCALLBACK_K_LTTCCOMMON_X_X_X_X_PRINTTOITUFF_{pin}",
                        Callback = "PrintToItuff",
                        Parameters = ITUFF_Parameters_dict.get(pin),
						BypassPort = BypassPort_dict.get(pin, BypassPort_dict["Default"]),
                        _fitem = Fitem('SAME', edc = True, r0 = pFail(setbin = 90910800))
                   )
    ITUFF_test_list.append(pin_test)

# Define your composite test first
PrintToITUFF = Flow("PrintToITUFF", ITUFF_test_list)
                           
# Call your test in a DUTFlow
LTTCCOMMON_SubFlow = Flow('TPI_VCCMIMS_XXX_LTTCCOMMON', Fitem("SAME", PrintToITUFF, edc = True, r0 = pFail(goto = "NEXT")), MIMS_test_list)

