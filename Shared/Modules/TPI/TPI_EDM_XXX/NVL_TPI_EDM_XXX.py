# ENG TP Path: I:\engineering\dev\sctp\tptorrent\hdmxprogs\arl\EDM_PYMTPL_DEBUG
# Import the necessary classes from Pymtpl
from pymtpl.por_methods import PrimeDcTestMethod, IVCurve, ULTLoggerTC, ScreenTC
from pymtpl.core import Flow, Fitem, pPass, pFail, Initialize, MultiTrial, AUTO, MTLdefault, InitializeMTL, InitializeNVLClass, Import, TrialParamSpec, Spec

##############################################################################################
# UPDATED by Skorlam on 12/30/2025 - To help with move to new Sort like binning at class.
##############################################################################################

# Initialize the module by defining the output mtpl path and module name
InitializeNVLClass('TPI_EDM_XXX', 'TPI_EDM_XXX', binrange=[(1080, 1086), (1090, 1096), (1590, 1596)],
                   defaultrm2bin = [(99152000, 99153999), (99102000, 99103999)],
                   defaultrm1bin = [(98152000, 98153999), (98102000, 98103999)])

# Add the necessary files to import in your mtpl
Import("TPI_EDM_XXX.usrv")
Import("TPI_EDM_XKPKGMB.usrv")
Import ("LevelsSequences_EDM.lvl")
Import ("BaseLevels_EDM.tcg")

#List of pins and relays based on composite block
EDM_pin_list = ["BASE_EDM", "CPU_EDM", "CPU1_EDM", "GCD_EDM", "HUB_EDM", "GND_EDM", "PCD_TMUX_07"]
EDM_diode_pin_list = ["BASE_EDM", "CPU_EDM", "CPU1_EDM", "GCD_EDM", "HUB_EDM", "GND_EDM", "PCD_TMUX_07"]
#EDM_diode_pin_list = ["CPU_EDM", "CPU1_EDM", "GCD_EDM", "HUB_EDM", "PCD_TMUX_07"]

#Created an empty test list that will be appended by each test created in the loop
EDM_START_test_list = []

EDM_DCFF_test_list = []

EDM_DCFF_diode_test_list = []

#Dictionary for shared pins or pins with unique IPs that we can't include in instance name
EDM_Pin_dict = {
                    "BASE_EDM": "BASE_EDM",
                    "CPU_EDM": "CPU_EDM",
                    "CPU1_EDM": "CPU1_EDM",
                    "GCD_EDM": "GCD_EDM",
                    "HUB_EDM": "HUB_EDM",
                    "GND_EDM": "PCD_EDM",  #### using this pin to create PCD test for H product 
                    "PCD_TMUX_07": "PCD_TMUX_07",
                }

#Dictionary for test instance naming 
Vir_name_dict = {
                    "BASE_EDM": "BASE_EDM",
                    "CPU_EDM": "CPU_EDM",
                    "CPU1_EDM": "CPU1_EDM",
                    "GCD_EDM": "GCD_EDM",
                    "HUB_EDM": "HUB_EDM",
                    "GND_EDM": "PCD_EDM",  #### using this pin to create PCD test for H product 
                    "PCD_TMUX_07": "PCD_TMUX_07",
                }

#Dictionary for LevelsTc

EDM_Levels_dict = {
                "Default": "TPI_EDM_XXX::all_tpi_edm_x_vsim_pkg_level_cat0" 
                #"BASE_EDM": "BASE::Power_dwn_PKG_xxx_pwrd_zerzer",
                #"CPU_EDM": "BASE::Power_dwn_PKG_xxx_pwrd_zerzer",
                #"CPU1_EDM": "BASE::Power_dwn_PKG_xxx_pwrd_zerzer",
                #"GCD_EDM": "BASE::Power_dwn_PKG_xxx_pwrd_zerzer",
                #"HUB_EDM": "BASE::Power_dwn_PKG_xxx_pwrd_zerzer",
                #"GND_EDM": "BASE::Power_dwn_PKG_xxx_pwrd_zerzer"
              }

EDM_Diode_Levels_dict = {
                        "Default": "TPI_EDM_XXX::all_tpi_edm_x_isvm_pkg_level_cat0" 
                        #"BASE_EDM": "BASE::Power_dwn_PKG_xxx_pwrd_zerzer",
                        #"CPU_EDM": "BASE::Power_dwn_PKG_xxx_pwrd_zerzer",
                        #"CPU1_EDM": "BASE::Power_dwn_PKG_xxx_pwrd_zerzer",
                        #"GCD_EDM": "BASE::Power_dwn_PKG_xxx_pwrd_zerzer",
                        #"HUB_EDM": "BASE::Power_dwn_PKG_xxx_pwrd_zerzer",
                        #"GND_EDM": "BASE::Power_dwn_PKG_xxx_pwrd_zerzer"
              }

#Dictionary for EDM bin assignments by die 
Bin_OPEN_dict = {
                "CPU_EDM": 1590,
                "CPU1_EDM": 1591,
                "GCD_EDM": 1593,
                "HUB_EDM": 1594,
                "GND_EDM": 1595,
                "BASE_EDM": 1596,
                "PCD_TMUX_07": 1595
              }
Bin_SHORT_dict = {
                "CPU_EDM": 1090,
                "CPU1_EDM": 1091,
                "GCD_EDM": 1093,
                "HUB_EDM": 1094,
                "GND_EDM": 1095,
                "BASE_EDM": 1096,
                "PCD_TMUX_07": 1095
              }   

Bin_OPEN_FF_dict = {
                "CPU_EDM": 1590,
                "CPU1_EDM": 1591,
                "GCD_EDM": 1593,
                "HUB_EDM": 1594,
                "GND_EDM": 1595,
                "BASE_EDM": 1596,
                "PCD_TMUX_07": 1595
              }
Bin_SHORT_FF_dict = {
                "CPU_EDM": 1090,
                "CPU1_EDM": 1091,
                "GCD_EDM": 1093,
                "HUB_EDM": 1094,
                "GND_EDM": 1095,
                "BASE_EDM": 1096,
                "PCD_TMUX_07": 1095
              } 
              
Diode_Bin_OPEN_dict = {
                "CPU_EDM": 1080,
                "CPU1_EDM": 1081,
                "GCD_EDM": 1083,
                "HUB_EDM": 1084,
                "PCD_TMUX_07": 1085,
                "BASE_EDM": 1086
              }
              
              
#Dictionary for BypassPort

BypassPort_dict = {
                    "Default": -1,
                    "CPU1_EDM": Spec('__shared__::TpRule.If_DS0_DS1_M(1,-1,1,1)'),
                    "GND_EDM": Spec('__shared__::TpRule.If_DS0_DS1_M(1,1,-1,1)'),
                    "PCD_TMUX_07": Spec('__shared__::TpRule.If_DS0_DS1_M(-1,-1,1,-1)'),
                  }

#Dictionary for PreInstance

Pre_Instance_dict = {
                    "Default": "",
                    "PCD_TMUX_07": "SetPinAttributes(--settings=PCD_TMUXCBIT2:LogicalValue:0 PCD_TMUXCBIT1:LogicalValue:0 PCD_TMUXCBIT0:LogicalValue:1)"
                    }

#Dictionary for PostInstance

Post_Instance_dict = {
                    "Default": "",
                    "PCD_TMUX_07": "SetPinAttributes(--settings=pcd_tmux_all:LogicalValue:0)"
                    }

#Dictionary for IRANGE

IR_dict = {                
                    "Default": Spec('TPI_EDM_XXX_Rules.EDM_Limit_HOT_COLD("IR100uA", "IR100uA", "IR100uA")'),
                    "BASE_EDM": Spec('TPI_EDM_XXX_Rules.EDM_Limit_HOT_COLD("IR1mA", "IR1mA", "IR1mA")')
           }
 
##Dictionary for LimitHi
#Limit_Hi_dict = {              
#                "Default": Spec('TPI_EDM_XXX_Rules.EDM_Limit_HOT_COLD("0.0003A", "0.0001A", "0.0001A")'),
#                "BASE_EDM": Spec('TPI_EDM_XXX_Rules.EDM_Limit_HOT_COLD("0.0027A", "0.0009A", "0.0009A")'),
#                "CPU_EDM": Spec('TPI_EDM_XXX_Rules.EDM_Limit_HOT_COLD("0.00009A", "0.00003A", "0.00003A")'),
#                "CPU1_EDM": Spec('TPI_EDM_XXX_Rules.EDM_Limit_HOT_COLD("0.00009A", "0.00003A", "0.00003A")'),
#                "GCD_EDM": Spec('TPI_EDM_XXX_Rules.EDM_Limit_HOT_COLD("0.00006A", "0.00002A", "0.00002A")'),
#                "HUB_EDM": Spec('TPI_EDM_XXX_Rules.EDM_Limit_HOT_COLD("0.00006A", "0.00002A", "0.00002A")'),
#                "GND_EDM": Spec('TPI_EDM_XXX_Rules.EDM_Limit_HOT_COLD("0.00006A", "0.00002A", "0.00002A")'),
#                "PCD_TMUX_07": Spec('TPI_EDM_XXX_Rules.EDM_Limit_HOT_COLD("0.00006A", "0.00003A", "0.00003A")')
#                }
##Dictionary for LimitLo
################## Enable first set of limits for PO TP. Second set of limits only for offine Bin1 #################
#Limit_Lo_dict = {                             
#                "Default": Spec('TPI_EDM_XXX_Rules.EDM_Limit_HOT_COLD("0.000003A", "0.000001A", "0.000001A")'),                
#                "BASE_EDM": Spec('TPI_EDM_XXX_Rules.EDM_Limit_HOT_COLD("0.000003A", "0.000001A", "0.000001A")'),
#                "CPU_EDM": Spec('TPI_EDM_XXX_Rules.EDM_Limit_HOT_COLD("0.000003A", "0.000001A", "0.000001A")'),
#                "CPU1_EDM": Spec('TPI_EDM_XXX_Rules.EDM_Limit_HOT_COLD("0.000003A", "0.000001A", "0.000001A")'),
#                "GCD_EDM": Spec('TPI_EDM_XXX_Rules.EDM_Limit_HOT_COLD("0.000003A", "0.000001A", "0.000001A")'),
#                "HUB_EDM": Spec('TPI_EDM_XXX_Rules.EDM_Limit_HOT_COLD("0.000003A", "0.000001A", "0.000001A")'),
#                "GND_EDM": Spec('TPI_EDM_XXX_Rules.EDM_Limit_HOT_COLD("0.000003A", "0.000001A", "0.000001A")'),
#                "PCD_TMUX_07": Spec('TPI_EDM_XXX_Rules.EDM_Limit_HOT_COLD("0.000003A", "0.000001A", "0.000001A")')
#                }

#Dictionary for LimitHi
Limit_Hi_dict = {   
                 "Default": Spec('__shared__::TpRule.If_PACKAGE(TPI_EDM_XXX_Desktop_Limit.TPI_EDM_XXX_High_Default,TPI_EDM_XKPKGMB_Mobile_Limit.TPI_EDM_XKPKGMB_High_Default)'),
                 "BASE_EDM": Spec('__shared__::TpRule.If_PACKAGE(TPI_EDM_XXX_Desktop_Limit.TPI_EDM_XXX_High_BASE,TPI_EDM_XKPKGMB_Mobile_Limit.TPI_EDM_XKPKGMB_High_BASE)'),
                 "CPU_EDM": Spec('__shared__::TpRule.If_PACKAGE(TPI_EDM_XXX_Desktop_Limit.TPI_EDM_XXX_High_CPU,TPI_EDM_XKPKGMB_Mobile_Limit.TPI_EDM_XKPKGMB_High_CPU)'),
                 "CPU1_EDM": Spec('__shared__::TpRule.If_PACKAGE(TPI_EDM_XXX_Desktop_Limit.TPI_EDM_XXX_High_CPU1,TPI_EDM_XKPKGMB_Mobile_Limit.TPI_EDM_XKPKGMB_High_CPU1)'),
                 "GCD_EDM": Spec('__shared__::TpRule.If_PACKAGE(TPI_EDM_XXX_Desktop_Limit.TPI_EDM_XXX_High_GCD,TPI_EDM_XKPKGMB_Mobile_Limit.TPI_EDM_XKPKGMB_High_GCD)'),
                 "HUB_EDM": Spec('__shared__::TpRule.If_PACKAGE(TPI_EDM_XXX_Desktop_Limit.TPI_EDM_XXX_High_HUB,TPI_EDM_XKPKGMB_Mobile_Limit.TPI_EDM_XKPKGMB_High_HUB)'),
                 "GND_EDM": Spec('__shared__::TpRule.If_PACKAGE(TPI_EDM_XXX_Desktop_Limit.TPI_EDM_XXX_High_GND,TPI_EDM_XKPKGMB_Mobile_Limit.TPI_EDM_XKPKGMB_High_GND)'),
                 "PCD_TMUX_07": Spec('__shared__::TpRule.If_PACKAGE(TPI_EDM_XXX_Desktop_Limit.TPI_EDM_XXX_High_PCD,TPI_EDM_XKPKGMB_Mobile_Limit.TPI_EDM_XKPKGMB_High_PCD)'),
                }
				
#Dictionary for LimitLo
################# Enable first set of limits for PO TP. Second set of limits only for offine Bin1 #################
Limit_Lo_dict = {  
                 "Default": Spec('__shared__::TpRule.If_PACKAGE(TPI_EDM_XXX_Desktop_Limit.TPI_EDM_XXX_Low_Default,TPI_EDM_XKPKGMB_Mobile_Limit.TPI_EDM_XKPKGMB_Low_Default)'),
                 "BASE_EDM": Spec('__shared__::TpRule.If_PACKAGE(TPI_EDM_XXX_Desktop_Limit.TPI_EDM_XXX_Low_BASE,TPI_EDM_XKPKGMB_Mobile_Limit.TPI_EDM_XKPKGMB_Low_BASE)'),
                 "CPU_EDM": Spec('__shared__::TpRule.If_PACKAGE(TPI_EDM_XXX_Desktop_Limit.TPI_EDM_XXX_Low_CPU,TPI_EDM_XKPKGMB_Mobile_Limit.TPI_EDM_XKPKGMB_Low_CPU)'),
                 "CPU1_EDM": Spec('__shared__::TpRule.If_PACKAGE(TPI_EDM_XXX_Desktop_Limit.TPI_EDM_XXX_Low_CPU1,TPI_EDM_XKPKGMB_Mobile_Limit.TPI_EDM_XKPKGMB_Low_CPU1)'),
                 "GCD_EDM": Spec('__shared__::TpRule.If_PACKAGE(TPI_EDM_XXX_Desktop_Limit.TPI_EDM_XXX_Low_GCD,TPI_EDM_XKPKGMB_Mobile_Limit.TPI_EDM_XKPKGMB_Low_GCD)'),
                 "HUB_EDM": Spec('__shared__::TpRule.If_PACKAGE(TPI_EDM_XXX_Desktop_Limit.TPI_EDM_XXX_Low_HUB,TPI_EDM_XKPKGMB_Mobile_Limit.TPI_EDM_XKPKGMB_Low_HUB)'),
                 "GND_EDM": Spec('__shared__::TpRule.If_PACKAGE(TPI_EDM_XXX_Desktop_Limit.TPI_EDM_XXX_Low_GND,TPI_EDM_XKPKGMB_Mobile_Limit.TPI_EDM_XKPKGMB_Low_GND)'),
                 "PCD_TMUX_07": Spec('__shared__::TpRule.If_PACKAGE(TPI_EDM_XXX_Desktop_Limit.TPI_EDM_XXX_Low_PCD,TPI_EDM_XKPKGMB_Mobile_Limit.TPI_EDM_XKPKGMB_Low_PCD)'),
                }
				
#Dictionary for ClampHi
Clamp_Hi_dict = {              
                "Default": Spec('TPI_EDM_XXX_Rules.EDM_Limit_HOT_COLD("100uA", "100uA", "100uA")'),
                "BASE_EDM": Spec('TPI_EDM_XXX_Rules.EDM_Limit_HOT_COLD("1mA", "1mA", "1mA")'),
                "CPU_EDM": Spec('TPI_EDM_XXX_Rules.EDM_Limit_HOT_COLD("100uA", "100uA", "100uA")'),
                "CPU1_EDM": Spec('TPI_EDM_XXX_Rules.EDM_Limit_HOT_COLD("100uA", "100uA", "100uA")'),
                "GCD_EDM": Spec('TPI_EDM_XXX_Rules.EDM_Limit_HOT_COLD("100uA", "100uA", "100uA")'),
                "HUB_EDM": Spec('TPI_EDM_XXX_Rules.EDM_Limit_HOT_COLD("100uA", "100uA", "100uA")'),
                "GND_EDM": Spec('TPI_EDM_XXX_Rules.EDM_Limit_HOT_COLD("100uA", "100uA", "100uA")'),
                "PCD_TMUX_07": Spec('TPI_EDM_XXX_Rules.EDM_Limit_HOT_COLD("100uA", "100uA", "100uA")')
                }
#Dictionary for ClampLo
Clamp_Lo_dict = {              
                "Default": Spec('TPI_EDM_XXX_Rules.EDM_Limit_HOT_COLD("-100uA", "-100uA", "-100uA")'),
                "BASE_EDM": Spec('TPI_EDM_XXX_Rules.EDM_Limit_HOT_COLD("-1mA", "-1mA", "-1mA")'),
                "CPU_EDM": Spec('TPI_EDM_XXX_Rules.EDM_Limit_HOT_COLD("-100uA", "-100uA", "-100uA")'),
                "CPU1_EDM": Spec('TPI_EDM_XXX_Rules.EDM_Limit_HOT_COLD("-100uA", "-100uA", "-100uA")'),
                "GCD_EDM": Spec('TPI_EDM_XXX_Rules.EDM_Limit_HOT_COLD("-100uA", "-100uA", "-100uA")'),
                "HUB_EDM": Spec('TPI_EDM_XXX_Rules.EDM_Limit_HOT_COLD("-100uA", "-100uA", "-100uA")'),
                "GND_EDM": Spec('TPI_EDM_XXX_Rules.EDM_Limit_HOT_COLD("-100uA", "-100uA", "-100uA")'),
                "PCD_TMUX_07": Spec('TPI_EDM_XXX_Rules.EDM_Limit_HOT_COLD("-100uA", "-100uA", "-100uA")')
                }
#Dictionary for VForce
FSP_EDM_dict = {
                "Default": "0.3V",
                "CPU_EDM": "0.3V",
                "CPU1_EDM": "0.3V",
                "GCD_EDM": "0.3V",
                "HUB_EDM": "0.3V",
                "GND_EDM": "0.3V",
                "BASE_EDM": "0.3V",
                "PCD_TMUX_07": "0.3V"
              }
#Dictionary for PMD
PMD_dict = {
                "Default": "10ms",
                "CPU_EDM": "10ms",
                "CPU1_EDM": "10ms",
                "GCD_EDM": "10ms",
                "HUB_EDM": "10ms",
                "GND_EDM": "10ms",
                "BASE_EDM": "10ms",
                "PCD_TMUX_07": "10ms"
              }
#Dictionary for FDT
FDT_dict = {
                "Default": "2ms",
                "CPU_EDM": "2ms",
                "CPU1_EDM": "2ms",
                "GCD_EDM": "2ms",
                "HUB_EDM": "2ms",
                "GND_EDM": "2ms",
                "BASE_EDM": "2ms",
                "PCD_TMUX_07": "2ms"
              }
### Define test instance loop for each item in the pin_list
## IVCURVE Method EDM Tests

# Start Subflow

for pin in EDM_pin_list:
    OPEN_SHORT_test = IVCurve(
                        name = f"EDM_X_DC_K_START_X_X_X_X_{Vir_name_dict.get(pin)}_OPEN_SHORT_IV",
                        AlarmMode = "Enabled",
                        DatalogLevel = "ALL",
                        #EnableFlushSmartTc = "Disabled",
                        LevelsTc = EDM_Levels_dict.get(pin, EDM_Levels_dict["Default"]),
                        IRange = IR_dict.get(pin, IR_dict["Default"]),
                        HighLimits = Limit_Hi_dict.get(pin, Limit_Hi_dict["Default"]),
                        LowLimits = Limit_Lo_dict.get(pin, Limit_Lo_dict["Default"]),
                        ForceSetPoint = FSP_EDM_dict.get(pin, FSP_EDM_dict["Default"]),
                        ForceStartValue = "0V",
                        ForceStepSize = "0.1V",
                        ForceStopValue = "1V",
                        IClampHi = Clamp_Hi_dict.get(pin, Clamp_Hi_dict["Default"]),
                        IClampLo = Clamp_Lo_dict.get(pin, Clamp_Lo_dict["Default"]),
                        PreMeasurementDelay = PMD_dict.get(pin, PMD_dict["Default"]),
                        FreeDriveTime = FDT_dict.get(pin, FDT_dict["Default"]),
                        PreInstance = Pre_Instance_dict.get(pin, Pre_Instance_dict["Default"]),
                        PostInstance = Post_Instance_dict.get(pin, Post_Instance_dict["Default"]),
                        BypassPort = BypassPort_dict.get(pin, BypassPort_dict["Default"]),
                        SamplingCount = "1",
                        Type = "Current",
                        Pins = EDM_Pin_dict.get(pin, pin),
						Mode = "Levels",
						LogLevel = "Disabled",
                        _fitem = Fitem('SAME', 
										r0 = pFail(setbin = Bin_OPEN_dict.get(pin), ret = 0), 
										r2 = pFail(setbin = 9910, ret = 2),
                                        r3 = pFail(setbin = Bin_OPEN_dict.get(pin), ret = 0),
                                        r4 = pFail(setbin = Bin_SHORT_dict.get(pin), ret = 0)
                                       )
                   )

    EDM_START_test_list.append(OPEN_SHORT_test)
    print(OPEN_SHORT_test.name)  

# THRFF Subflow not supported
    
# DCFF Subflow  
  
for pin in EDM_pin_list:
    OPEN_SHORT_test = IVCurve(
                        name = f"EDM_X_DC_K_DCFF_X_X_X_X_{Vir_name_dict.get(pin)}_OPEN_SHORT_IV",
                        AlarmMode = "Enabled",
                        DatalogLevel = "ALL",
                        #EnableFlushSmartTc = "Disabled",
                        LevelsTc = EDM_Levels_dict.get(pin, EDM_Levels_dict["Default"]),
                        IRange = IR_dict.get(pin, IR_dict["Default"]),
                        HighLimits = Limit_Hi_dict.get(pin, Limit_Hi_dict["Default"]),
                        LowLimits = Limit_Lo_dict.get(pin, Limit_Lo_dict["Default"]),
                        ForceSetPoint = FSP_EDM_dict.get(pin, FSP_EDM_dict["Default"]),
                        ForceStartValue = "0V",
                        ForceStepSize = "0.1V",
                        ForceStopValue = "1V",
                        IClampHi = Clamp_Hi_dict.get(pin, Clamp_Hi_dict["Default"]),
                        IClampLo = Clamp_Lo_dict.get(pin, Clamp_Lo_dict["Default"]),
                        PreMeasurementDelay = PMD_dict.get(pin, PMD_dict["Default"]),
                        FreeDriveTime = FDT_dict.get(pin, FDT_dict["Default"]),
                        PreInstance = Pre_Instance_dict.get(pin, Pre_Instance_dict["Default"]),
                        PostInstance = Post_Instance_dict.get(pin, Post_Instance_dict["Default"]),
                        BypassPort = BypassPort_dict.get(pin, BypassPort_dict["Default"]),
                        SamplingCount = "1",
                        Type = "Current",
                        Pins = EDM_Pin_dict.get(pin, pin),
						Mode = "Levels",
						LogLevel = "Disabled",
                        _fitem = Fitem('SAME', 
										r0 = pFail(setbin = Bin_OPEN_FF_dict.get(pin), ret = 0), 
										r2 = pFail(setbin = 9910, ret = 2),
                                        r3 = pFail(setbin = Bin_OPEN_FF_dict.get(pin), ret = 0),
                                        r4 = pFail(setbin = Bin_SHORT_FF_dict.get(pin), ret = 0)
                                       )
                   )

    EDM_DCFF_test_list.append(OPEN_SHORT_test)
    print(OPEN_SHORT_test.name)    


# DCFF Subflow

for pin in EDM_diode_pin_list:
    OPEN_test = IVCurve(
                        name = f"EDM_X_DC_K_DCFF_X_X_X_X_400UA_DIODE_CHECK_{Vir_name_dict.get(pin)}_OPEN_IV",
                        AlarmMode = "Enabled",
                        DatalogLevel = "ALL",
                        #EnableFlushSmartTc = "Disabled",
                        LevelsTc = EDM_Diode_Levels_dict.get(pin, EDM_Diode_Levels_dict["Default"]),
                        IRange = "IR1mA",
                        #HighLimits = "2V",
                        HighLimits = Spec('TPI_EDM_XXX_Rules.EDM_Limit_HOT_COLD("6V", "2V", "2V")'),
                        #LowLimits = "0.1V",
                        LowLimits = Spec('TPI_EDM_XXX_Rules.EDM_Limit_HOT_COLD("0.3V", "0.1V", "0.1V")'),
                        ForceSetPoint = "0.0004A",
                        ForceStartValue = "0A",
                        ForceStepSize = "0.0001A",
                        ForceStopValue = "0.001A",
                        VClampHi = "3.3V",
                        VClampLo = "-0.5V",
                        PreMeasurementDelay = "20ms",
                        FreeDriveTime = "2ms",
                        PreInstance = Pre_Instance_dict.get(pin, Pre_Instance_dict["Default"]),
                        PostInstance = Post_Instance_dict.get(pin, Post_Instance_dict["Default"]),
                        BypassPort = BypassPort_dict.get(pin, BypassPort_dict["Default"]),
                        SamplingCount = "1",
                        Type = "Voltage",
                        Pins = EDM_Pin_dict.get(pin, pin),
						Mode = "Levels",
						LogLevel = "Disabled",
                        _fitem = Fitem('SAME',
                                        edc = True,
										#r0 = pFail(setbin = Diode_Bin_OPEN_dict.get(pin), ret = 0), 
										#r2 = pFail(setbin = 9916, ret = 2),
                                        #r3 = pFail(setbin = Diode_Bin_OPEN_dict.get(pin), ret = 0)
                                        r0 = pFail(goto = "NEXT"), 
										r2 = pFail(goto = "NEXT"),
                                        r3 = pFail(goto = "NEXT"),
                                        r4 = pFail(goto = "NEXT"),
                                       )
                   )

    EDM_DCFF_diode_test_list.append(OPEN_test)
    print(OPEN_test.name) 

FlagCheck1 = ScreenTC(
                    name = "EDM_X_DC_K_DCFF_X_X_X_X_FLAGCHECK1",
                    ScreenTestSet = "SHOPSBINCHECK1",
                    ScreenTestsFile = "InputFiles/TPI_EDM_XXX_ScreenTest.txt",
                    _fitem = Fitem('SAME', r0 = pFail(setbin = 9010, ret = 0), r1 = pPass(ret = 1), r2 = pPass(goto = "NEXT"), r3 = pPass(goto = "NEXT"), r4 = pFail(setbin = 9010, ret = 0))
                   )
FlagCheck2_PASS = ScreenTC(
                    name = "EDM_X_DC_K_DCFF_X_X_X_X_FLAGCHECK2_PASS",
                    ScreenTestSet = "SHOPSBINCHECK2",
                    ScreenTestsFile = "InputFiles/TPI_EDM_XXX_ScreenTest.txt",
                    _fitem = Fitem('SAME', r0 = pFail(setbin = 9010, ret = 0), r1 = pPass(ret = 1), r2 = pPass(goto = "NEXT"), r3 = pPass(ret = 1))
                   )
#FlagCheck2_FAIL_bin_dict = {"FlagCheck2_FAIL_bin": 1099}

FlagCheck2_FAIL = ScreenTC(
                    name = "EDM_X_DC_K_DCFF_X_X_X_X_FLAGCHECK2_FAIL",
                    ScreenTestSet = "SHOPSBINCHECK2",
                    ScreenTestsFile = "InputFiles/TPI_EDM_XXX_ScreenTest.txt",
                    #_fitem = Fitem('SAME', r0 = pFail(ret = 0), r1 = pFail(ret = 2), r2 = pFail(ret = 0), r3 = pFail(ret = 2))
                    _fitem = Fitem('SAME', r0 = pFail(setbin = 1099, ret = 0), r1 = pFail(setbin = 1099, ret = 2),
                                    r2 = pFail(setbin = 1099, ret = 0), r3 = pFail(setbin = 1099, ret = 2))
                   )

#ULTLogger Instance in DCFF
ULTLOGGER_EDM = ULTLoggerTC(
                                name = "EDM_X_PRIMEULT_K_DCFF_X_X_X_X_ULTLOGGER_EDM",
                                DieId = Spec('__shared__::TpRule.If_CLASS_NVL_S52C((__shared__::DFFVars.DIEID_BASE+","+__shared__::DFFVars.DIEID_CPU+","+__shared__::DFFVars.DIEID_CPU1+","+__shared__::DFFVars.DIEID_GPU+","+__shared__::DFFVars.DIEID_PCD+","+__shared__::DFFVars.DIEID_HUB),(__shared__::DFFVars.DIEID_BASE+","+__shared__::DFFVars.DIEID_CPU+","+__shared__::DFFVars.DIEID_GPU+","+__shared__::DFFVars.DIEID_PCD+","+__shared__::DFFVars.DIEID_HUB))'),
                                LogLevel = "Disabled",
                                SetUltDataPerDieId = "DISABLED",
                                ValueExpression = Spec('__shared__::TpRule.If_CLASS_NVL_S52C((__shared__::DFFVars.DIEID_BAS_IDENTIFIER+","+__shared__::DFFVars.DIEID_CPU_IDENTIFIER+","+__shared__::DFFVars.DIEID_CPU1_IDENTIFIER+","+__shared__::DFFVars.DIEID_GPU_IDENTIFIER+","+__shared__::DFFVars.DIEID_PCD_IDENTIFIER+","+__shared__::DFFVars.DIEID_HUB_IDENTIFIER),(__shared__::DFFVars.DIEID_BAS_IDENTIFIER+","+__shared__::DFFVars.DIEID_CPU_IDENTIFIER+","+__shared__::DFFVars.DIEID_GPU_IDENTIFIER+","+__shared__::DFFVars.DIEID_PCD_IDENTIFIER+","+__shared__::DFFVars.DIEID_HUB_IDENTIFIER))'),
                                BypassPort = Spec('__shared__::TpRule.If_M_PKGs(1,-1)'),
                                _fitem = Fitem('SAME', r0 = pFail(setbin = 5306, ret = 0),  r1 = pPass(ret = 1))
                                )

#Define your composite test first

EDM_START_BASE = Flow("EDM_BASE", EDM_START_test_list[0])
EDM_START_CPU = Flow("EDM_CPU", EDM_START_test_list[1])
EDM_START_CPU1 = Flow("EDM_CPU1", EDM_START_test_list[2])
EDM_START_GCD = Flow("EDM_GCD", EDM_START_test_list[3])
EDM_START_HUB = Flow("EDM_HUB", EDM_START_test_list[4])
EDM_START_GND = Flow("EDM_PCD_H", EDM_START_test_list[5])
EDM_START_PCD= Flow("EDM_PCD", EDM_START_test_list[6])

EDM_DCFF_BASE = Flow("EDM_DCFF_BASE", EDM_DCFF_diode_test_list[0], EDM_DCFF_test_list[0])
EDM_DCFF_CPU = Flow("EDM_DCFF_CPU", EDM_DCFF_diode_test_list[1], EDM_DCFF_test_list[1])
EDM_DCFF_CPU1 = Flow("EDM_DCFF_CPU1", EDM_DCFF_diode_test_list[2], EDM_DCFF_test_list[2])
EDM_DCFF_GCD = Flow("EDM_DCFF_GCD", EDM_DCFF_diode_test_list[3], EDM_DCFF_test_list[3])
EDM_DCFF_HUB = Flow("EDM_DCFF_HUB", EDM_DCFF_diode_test_list[4], EDM_DCFF_test_list[4])
EDM_DCFF_GND = Flow("EDM_DCFF_PCD_H",  EDM_DCFF_diode_test_list[5], EDM_DCFF_test_list[5])
EDM_DCFF_PCD = Flow("EDM_DCFF_PCD",  EDM_DCFF_diode_test_list[6], EDM_DCFF_test_list[6])

EDM_DCFF_ALL = Flow("EDM_DCFAILFLOW", Fitem("SAME", EDM_DCFF_BASE, r0 = pFail(ret = 0), r2 = pFail(ret = 2)), 
                                          Fitem("SAME", EDM_DCFF_CPU, r0 = pFail(ret = 0), r2 = pFail(ret = 2)), 
                                          Fitem("SAME", EDM_DCFF_CPU1, r0 = pFail(ret = 0), r2 = pFail(ret = 2)),
                                          Fitem("SAME", EDM_DCFF_GCD, r0 = pFail(ret = 0), r2 = pFail(ret = 2)), 
                                          Fitem("SAME", EDM_DCFF_HUB, r0 = pFail(ret = 0), r2 = pFail(ret = 2)), 
                                          Fitem("SAME", EDM_DCFF_GND, r0 = pFail(ret = 0), r2 = pFail(ret = 2)),
                                           Fitem("SAME", EDM_DCFF_PCD, r0 = pFail(ret = 0), r2 = pFail(ret = 2)))

# Call your test in a DUTFlow

START_Subflow = Flow('TPI_EDM_XXX_START', Fitem("SAME", EDM_START_BASE, r0 = pFail(ret = 0), r2 = pFail(ret = 2)), 
                                          Fitem("SAME", EDM_START_CPU, r0 = pFail(ret = 0), r2 = pFail(ret = 2)),
                                          Fitem("SAME", EDM_START_CPU1, r0 = pFail(ret = 0), r2 = pFail(ret = 2)), 
                                          Fitem("SAME", EDM_START_GCD, r0 = pFail(ret = 0), r2 = pFail(ret = 2)), 
                                          Fitem("SAME", EDM_START_HUB, r0 = pFail(ret = 0), r2 = pFail(ret = 2)), 
                                          Fitem("SAME", EDM_START_GND, r0 = pFail(ret = 0), r2 = pFail(ret = 2)),
                                          Fitem("SAME", EDM_START_PCD, r0 = pFail(ret = 0), r2 = pFail(ret = 2)))

                                          
DCFF_Subflow = Flow('TPI_EDM_XXX_DCFF', FlagCheck1, Fitem("SAME", EDM_DCFF_ALL, r0 = pFail(goto = "EDM_X_DC_K_DCFF_X_X_X_X_FLAGCHECK2_FAIL"), r1 = pPass(goto = "EDM_X_DC_K_DCFF_X_X_X_X_FLAGCHECK2_PASS"), r2 = pFail(ret = 2)), FlagCheck2_FAIL, FlagCheck2_PASS, ULTLOGGER_EDM )
