from pymtpl.por_methods import VminTC, PrimePatConfigTestMethod, PrimeThermalSingleMeasurementTestMethod, DedcRVCallbackTC, ScreenTC, FmaxTC, RunCallback, DDGShmooTC, DedcLoadConfigTC, ApexTC, PrimeVirtualFuseExportToSharedStorageTestMethod,PrimePatConfigTestMethod,PrimeArrayHryTestMethod,PrimeLSARasterTestMethod,PrimeCapturePacketsTestMethod,PrimeCaptureVectorsTestMethod,PrimeRepairToFuseTestMethod #,NVLRasterExtension,NVLLsaRasterExtension
from pymtpl.core import Flow, Fitem, pPass, pFail, Initialize, NativeMultiTrial, AUTO, MTLdefault, InitializeMTL, Spec, TrialParamSpec, Import, InitializeNVLClass, MConfig

from pymtpl.por_methods import BaseMethod, required, optional
# Beginning of NVLRasterExtension class definition
class NVLRasterExtension(BaseMethod):
    def __init__(self,
                 name,
                 MaxDefectCount=optional,       # Max number of defects that will be processed by the repair instance
                 AlgorithmPriority=optional,    # Prioritization of the repair algorithm criteria.
                 ArrayFile=required,            # Path to the Array input file.
                 BaseNumber=optional,           # BaseNumber for R-file printing.
                 DataLog=optional,              # Selects the output type in which to log the instance results.
                 DecoderMatchLabel=required,    # Label from which to obtain the decoding parameters to be used from the array file.
                 DeleteInputStorage=optional,   # Defines whether to delete input stored data if input is provided through a storage key.
                 IfeObject=optional,            # IFE object of type IRepairExtensions.
                 InputForDebug=optional,        # Input data for testing.
                 InputStorageKey=optional,      # SharedStorage input key in DUT context to be grabbed from list of strings table.
                 LyaCellSelection=optional,     # LYA cell select algorithm.
                 LyaStorageTag=optional,        # Specific tag to create a unique shared storage name for the current repair instance. This will later be used to share repair data with the corresponding LYA test instance.
                 OperationMode=optional,        # Operation mode.
                 ResourceFile=optional,         # Path to the Resource input file.
                 TargetArray=required,          # Array name that the instance will use for data processing.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None
                 ):
        self._init(name, locals())
# End of NVLRasterExtension class definition

module = "ARR_ATOM_CX"
mtpl_naming = "ARR_ATOM_CX"

socket = "CLASS"
def ifEmpty (param):
	if param: 
		return param
	else:
		return None

def get_ApexTC_fmax(testname,content,subflow,freqcorner): 
	bypass = content['bypass']
	kill = content['kill']
	template = content['template']
	flowmatrix = content['flowmatrix']
	voltageDomain = content['flowmatrix'].split('_')[0]
	hermes = "master" if 'hermes' in content else "list"

	# supply override handling
	supply = content['supply']
	voltage_target = supply

	#recovery handling
	forwardingmode = 'None' if 'recovery' in content else "Input"
	pinmap = POR_PinMap if 'recovery' not in content else None
	recoverymode = 'NoRecovery' if 'recovery' in content else None
	recoveryoptions = POR_RecoveryOptions if 'recovery' in content else None
	incomingtrackers = POR_RecoveryTrackingIncoming if 'recovery' in content else None
	outgoingtrackers = POR_RecoveryTrackingOutgoing if 'recovery' in content else None
	featureswitchsettings = POR_FeatureSwitchSettings if 'recovery' in content else None

	#Voltage converter handling
	voltageconverter = '--overrides ' + content['voltageoverride'] if 'voltageoverride' in content else ''
	if 'powermux' in content:
		voltageconverter = content['powermux'] if voltageconverter=='' else (voltageconverter + ' ' + content['powermux'])

	if 'plist' in content:
		plist_name = f"IPC::arr_{dielet.lower()}_{subflow.lower()}_{dft.lower()}_{IP.lower()}_{content['plist'][0].lower()}_{content['plist'][1].lower()}_{supply.lower()}_{content['plist'][2].lower()}_{testname.lower()}_{freqcorner.lower()}_{socket.lower()}_{hermes}"

	return ApexTC(
			name=f'ARR_{IP}_FMAX_K_{subflow}_HITO_VCCIA_X_X_{testname.upper()}' if kill==1 else f'ARR_{IP}_VMIN_E_{subflow}_HITO_VCCIA_X_X_{testname.upper()}',
			BypassPort = bypass,			
			Targets = f'{voltage_target}',
			ForwardingMode = "Input",
			PinMap = pinmap,
			InitialMaskBits='',
			DtsConfiguration='',
			RecoveryOptions='',
			RecoveryTracking='',
			#SetPointsPreInstance = Spec(gen_SetPointsPreInstance(freqcorner,template)),
			#SetPointsPostInstance = "MCdrv:R1_SET";
			LevelsTc = f'{level}',
			Patlist = f'{plist_name}',
			SetPointsPlistParamName = "Patlist",
			PatternNameCounterIndexes = "9,10,11,12,13,14,15",
			TimingsTc = f'{timing}',
            End=Spec(f'__shared__::FlowMatrixSingular.APEX_ATOM_MIN'),
            Start=Spec(f'__shared__::FlowMatrixSingular.APEX_ATOM_MAX'),
			StepSize = 1,
			FivrCondition="NOM",
			VoltageConverter='--dlvrpins VCCIA',
			)
			#BaseNumbers = AUTO,
			#VoltageConverter = voltageconverter if voltageconverter else None)
			
			#EndVoltageLimits = Spec(f'__shared__::FlowMatrixSingular.AT_LOW_SEARCH_VALUE'),
			#ScoreboardEdgeTicks = 0,
			#MaxFailsNum = 0,						
			#StartVoltages = Spec(f'__shared__::FlowMatrixSingular.AT_LOW_SEARCH_VALUE'),
			#StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.AT_SEARCH_RESOLUTION)'),
			#TestMode = 'MultiVmin',			
			

def get_VminTC_vmin(testname,content,subflow,freqcorner): 
	bypass = content['bypass']
	kill = content['kill']
	template = content['template']
	flowmatrix = content['flowmatrix']	
	voltageDomain = content['flowmatrix'].split('_')[0]
	
	if 'hermes' not in content:
		hermes = 'list'
	else:
		hermes = "master" if content['hermes'] == "1" else "long__1"

	#recovery handling
	#forwardingmode = 'None' if 'recovery' in content else "Input"
	pinmap = POR_PinMap if 'recovery' not in content else None
	recoverymode = POR_RecoverMode if 'recovery' not in content else None
	#recoveryoptions = POR_RecoveryOptions if 'recovery' in content else None
	#incomingtrackers = POR_RecoveryTrackingIncoming if 'recovery' in content else None
	#outgoingtrackers = POR_RecoveryTrackingOutgoing if 'recovery' in content else None
	#featureswitchsettings = POR_FeatureSwitchSettings if 'recovery' in content else None

	#Voltage converter handling
	voltageconverter = '--overrides ' + content['voltageoverride'] if 'voltageoverride' in content else ''
	if 'powermux' in content:
		voltageconverter = content['powermux'] if voltageconverter=='' else (voltageconverter + ' ' + content['powermux'])

	if 'plist' in content and testname == "COMBINED":
		supply = 'VCCATOM'
		plist_testname = 'ALL'
		plist_name = f"IPC::arr_{dielet.lower()}_{subflow.lower()}_{dft.lower()}_{IP.lower()}_{content['plist'][0].lower()}_{content['plist'][1].lower()}_{supply.lower()}_{content['plist'][2].lower()}_{plist_testname.lower()}_{freqcorner.lower()}_hptp800_{socket.lower()}_{hermes}"
	elif 'plist' in content and testname == "SSA":
		supply = 'VCCATOM'
		plist_testname = 'L2'
		plist_name = f"IPC::arr_{dielet.lower()}_{subflow.lower()}_{dft.lower()}_{IP.lower()}_{content['plist'][0].lower()}_{content['plist'][1].lower()}_{supply.lower()}_{content['plist'][2].lower()}_{plist_testname.lower()}_{freqcorner.lower()}_hptp800_{socket.lower()}_{hermes}"
	else: 
		'plist' in content and testname == "SSA_l2tag"
		supply = 'VCCATOM'
		plist_testname = 'L2'
		plist_name = f"IPC::arr_{dielet.lower()}_{subflow.lower()}_{dft.lower()}_{IP.lower()}_{content['plist'][0].lower()}_{content['plist'][1].lower()}_{supply.lower()}_{content['plist'][2].lower()}_{plist_testname.lower()}_{freqcorner.lower()}_hptp800_{socket.lower()}_{hermes}"
	
	# supply override handling
	supply = content['supply']
	voltage_target = supply
	CornerIdentifiers = ''
	
	if 'CDIE_' not in flowmatrix and 'FMIN' not in flowmatrix:				
		for i,item in enumerate(corner_id):
			CornerIdentifiers += item + '@' + freq_corner			
			if i<len(corner_id)-1:
				CornerIdentifiers += ','
	

	
	ExecutionMode = 'SearchWithScoreboard'
	ForwardingMode = 'InputOutput' if kill==1 else "Input"
	LimitGuardband = 'GBVars.FminLimitGuardband'
	ScoreboardEdgeTicks = 'toInteger(__shared__::Specs.CHK_EDGE_TICK)'
	MaxFailsNum = 'toInteger(__shared__::Specs.CHK_MAX_FAILS)'
	TestMode = 'SingleVmin'
	VoltagesOffset = ''
	CornerIdentifiers = ''

	
	return VminTC(
			name=f'ARR_{IP}_VMIN_K_{subflow}_HITO_VCCIA_{freqcorner}_X_{testname.upper()}' if kill==1 else f'ARR_{IP}_VMIN_E_{subflow}_HITO_VCCIA_{freqcorner}_X_{testname.upper()}',
			BypassPort = bypass,
			EndVoltageLimits = Spec(f'__shared__::FlowMatrixSingular.AT_HIGH_SEARCH_VALUE'),
			LevelsTc = f'{level}',
			Patlist = f'{plist_name}',
			PatternNameCounterIndexes = "9,10,11,12,13,14,15",
			BaseNumbers = AUTO,
			ScoreboardEdgeTicks = Spec(f'{ScoreboardEdgeTicks}'),
			MaxFailsNum = Spec(f'{MaxFailsNum}'),
			SetPointsPlistParamName = "Patlist",
			#SetPointsPreInstance = Spec(gen_SetPointsPreInstance(freqcorner,template)),
			StartVoltages = Spec(f'__shared__::FlowMatrixSingular.AT_LOW_SEARCH_VALUE'),
			StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.AT_SEARCH_RESOLUTION)'),
			TestMode = ifEmpty(f'{TestMode}'), 
			TimingsTc = f'{timing}',
			VoltageTargets = f'{voltage_target}',
			VoltageConverter = voltageconverter if voltageconverter else None,
			ExecutionMode = ifEmpty(f'{ExecutionMode}'),
			CornerIdentifiers = ifEmpty(f'{CornerIdentifiers}'),	
			ForwardingMode = ifEmpty(f'{ForwardingMode}'),
			LimitGuardband = ifEmpty(f'{LimitGuardband}'),
			VoltagesOffset = ifEmpty(f'{VoltagesOffset}'),
			PinMap = ifEmpty(f'{pinmap}'),
			StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
			StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
			RecoveryMode = recoverymode)
			#RecoveryOptions = recoveryoptions,
			#RecoveryTrackingIncoming = incomingtrackers,
			#RecoveryTrackingOutgoing = outgoingtrackers,
			#FeatureSwitchSettings = featureswitchsettings)


def get_VminTC_pt(testname, content, subflow, freqcorner): 
    bypass = content['bypass']
    kill = content['kill']
    template = content['template']
    flowmatrix = content['flowmatrix']
    voltageDomain = content['flowmatrix'].split('_')[0]
    if 'hermes' not in content:
        hermes = 'list'
    else:
        hermes = "master" if content['hermes'] == "1" else "long__1"

    # supply override handling
    supply = content['supply']
    voltage_target = supply

    # recovery handling
    # forwardingmode = 'None' if 'recovery' in content else "Input"
    pinmap = POR_PinMap if 'recovery' not in content else None
    recoverymode = POR_RecoverMode if 'recovery' not in content else None
    ForwardingMode = 'InputOutput' if kill == 1 else "Input"
    # recoveryoptions = POR_RecoveryOptions if 'recovery' in content else None
    # incomingtrackers = POR_RecoveryTrackingIncoming if 'recovery' in content else None
    # outgoingtrackers = POR_RecoveryTrackingOutgoing if 'recovery' in content else None
    # featureswitchsettings = POR_FeatureSwitchSettings if 'recovery' in content else None

    # Voltage converter handling
    voltageconverter = '--overrides ' + content['voltageoverride'] if 'voltageoverride' in content else ''
    if 'powermux' in content:
        voltageconverter = content['powermux'] if voltageconverter == '' else (voltageconverter + ' ' + content['powermux'])

    # Ensure level is always defined
    if 'level' in content:
        level = f'CPU_IP_BASE::CDIE_all_bf_x_x_IPC_lvl_{content["level"]}'
    else:
        level = globals().get('level', "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min")

    if 'plist' in content and testname == "COMBINED":
        supply = 'VCCATOM'
        plist_testname = 'ALL'
        plist_name = f"IPC::arr_{dielet.lower()}_{subflow.lower()}_{dft.lower()}_{IP.lower()}_{content['plist'][0].lower()}_{content['plist'][1].lower()}_{supply.lower()}_{content['plist'][2].lower()}_{plist_testname.lower()}_{freqcorner.lower()}_hptp800_{socket.lower()}_{hermes}"
    elif 'plist' in content and testname == "SSA":
        supply = 'VCCATOM'
        plist_testname = 'L2'
        plist_name = f"IPC::arr_{dielet.lower()}_{subflow.lower()}_{dft.lower()}_{IP.lower()}_{content['plist'][0].lower()}_{content['plist'][1].lower()}_{supply.lower()}_{content['plist'][2].lower()}_{plist_testname.lower()}_{freqcorner.lower()}_hptp800_{socket.lower()}_{hermes}"
    else:
        'plist' in content and testname == "SSA_l2c6"
        supply = 'VCCATOM'
        plist_testname = 'L2'
        plist_name = f"IPC::arr_{dielet.lower()}_{subflow.lower()}_{dft.lower()}_{IP.lower()}_{content['plist'][0].lower()}_{content['plist'][1].lower()}_{supply.lower()}_{content['plist'][2].lower()}_{plist_testname.lower()}_{freqcorner.lower()}_hptp800_{socket.lower()}_{hermes}"

    return VminTC(
        name=f'ARR_{IP}_SB_K_{subflow}_HITO_VCCIA_{freqcorner}_X_{testname.upper()}' if kill == 1 else f'ARR_{IP}_VMIN_E_{subflow}_HITO_VCCIA_{freqcorner}_X_{testname.upper()}',
        BypassPort=bypass,
        EndVoltageLimits=Spec(f'__shared__::FlowMatrixSingular.AT_LOW_SEARCH_VALUE'),
		PreInstance = ifEmpty(f"{content['PreInstance']}") if 'PreInstance' in content else None,
        ForwardingMode=ifEmpty(f'{ForwardingMode}'),
        LevelsTc=f'{level}',
        Patlist=f'{plist_name}',
        PatternNameCounterIndexes="9,10,11,12,13,14,15",
        BaseNumbers=AUTO,
        ScoreboardEdgeTicks=0,
        MaxFailsNum=0,
        SetPointsPlistParamName="Patlist",
        SetPointsPreInstance=Spec(f'"MCdrv:atomfreq_0:"+' + Spec(f"__shared__::FlowMatrixSingular.{flowmatrix}+") + '"GHz,MCdrv:corefreq:"+' + Spec(f"__shared__::FlowMatrixSingular.{flowmatrix}+") + '"GHz,MCdrv:ringfreq_0:"+' + Spec(f"__shared__::FlowMatrixSingular.{flowmatrix}+") + '"GHz,MCAarr:ratio_modify:"+' + Spec(f"__shared__::FlowMatrixSingular.{flowmatrix}+") + '"GHz"'),
        StartVoltages=Spec(f'__shared__::FlowMatrixSingular.AT_LOW_SEARCH_VALUE'),
        StepSize=Spec(f'toDouble(__shared__::FlowMatrixSingular.AT_SEARCH_RESOLUTION)'),
        TestMode='Scoreboard',
        TimingsTc=f'{timing}',
        VoltageTargets=f'{voltage_target}',
        # VoltageConverter = voltageconverter if voltageconverter else None,
        VoltageConverter=Spec(f'"--railconfigurations CDIE_ATOM_POWERMUXM0 CDIE_ATOM_POWERMUXM1 CDIE_ATOM_POWERMUXM2 CDIE_ATOM_POWERMUXM3 CDIE_L2_NBLCTRL0 CDIE_L2_NBLCTRL1 CDIE_L2_NBLCTRL2 CDIE_L2_NBLCTRL3 --dlvrpins VCCIA --expressions "' + f' + DROPOUT.AT_{freqcorner}'),
        PinMap=ifEmpty(f'{pinmap}'),
        RecoveryMode=recoverymode,
        RecoveryOptions='CLASS_NVL_S28C_8A',
        FivrCondition='NOM',
        RecoveryTrackingIncoming='ACRM3,ACRM2,ACRM1,ACRM0',
        RecoveryTrackingOutgoing='ACRM3,ACRM2,ACRM1,ACRM0',
        FeatureSwitchSettings= 'recovery_update_always,disable_masked_targets,fivr_mode_on,print_per_target_increments,print_scoreboard_counters'
    )

def get_VminTC_multitrial_singlevmin_F5(testname,content,subflow,freqcorner): 
	bypass = content['bypass']
	kill = content['kill']
	template = content['template']
	flowmatrix = content['flowmatrix']
	dts = content['dts'] if 'dts' in content else ''
	if 'hermes' not in content:
		hermes = 'list'
	else:
		hermes = "master" if content['hermes'] == "1" else "long__1"
	if 'CDIE_' not in flowmatrix:
		voltageDomain = content['flowmatrix'].split('_')[0]
	else:
		voltageDomain = "VCCIA"
			
	
	
	#recovery handling
	pinmap = POR_PinMap if 'recovery' not in content else None
	recoverymode = POR_RecoverMode if 'recovery' not in content else None
	recoveryoptions = POR_RecoveryOptions if 'recovery' in content else None
	incomingtrackers = POR_RecoveryTrackingIncoming if 'recovery' in content else None
	outgoingtrackers = POR_RecoveryTrackingOutgoing if 'recovery' in content else None
	featureswitchsettings = POR_FeatureSwitchSettings_MultiVmin if 'recovery' in content else None

	#Voltage converter handling
	voltageconverter = '"--overrides ' + content['voltageoverride'] if 'voltageoverride' in content else ''
	if 'powermux' in content:
		voltageconverter = f'"{content["powermux"]}"' if voltageconverter=='' else (voltageconverter + ' + ' + f'" {content["powermux"]}"')
	
	if 'plist' in content and testname == "COMBINED":
		supply = 'VCCATOM'
		plist_testname = 'ALL'
		plist_name = f"IPC::arr_{dielet.lower()}_{subflow.lower()}_{dft.lower()}_{IP.lower()}_{content['plist'][0].lower()}_{content['plist'][1].lower()}_{supply.lower()}_{content['plist'][2].lower()}_{plist_testname.lower()}_{freqcorner.lower()}_hptp800_{socket.lower()}_{hermes}"
	elif 'plist' in content and testname == "SSA":
		supply = 'VCCATOM'
		plist_testname = 'L2'
		plist_name = f"IPC::arr_{dielet.lower()}_{subflow.lower()}_{dft.lower()}_{IP.lower()}_{content['plist'][0].lower()}_{content['plist'][1].lower()}_{supply.lower()}_{content['plist'][2].lower()}_{plist_testname.lower()}_{freqcorner.lower()}_hptp800_{socket.lower()}_{hermes}"
	
	# supply override handling
	supply = content['supply']
	voltage_target = supply

	if 'CDIE_' not in flowmatrix:		
		CornerIdentifiers = '"'		
		for i,item in enumerate(corner_id):
			CornerIdentifiers += item + '@' + freq_corner			
			if i<len(corner_id)-1:
				CornerIdentifiers += ','				
		CornerIdentifiers += '"'
		prefix_for_flowmatrix = "__shared__::CustomFlowMatrixSpecs"
		#print(f'{CornerIdentifiers}')
	else:
		prefix_for_flowmatrix = "__shared__::Corners"
	
	ExecutionMode = 'SearchWithScoreboard'
	ForwardingMode = 'InputOutput' if kill==1 else "Input"
	LimitGuardband = ''
	ScoreboardEdgeTicks = 'toInteger(__shared__::Specs.CHK_EDGE_TICK)'
	MaxFailsNum = 'toInteger(__shared__::Specs.CHK_MAX_FAILS)'
	TestMode = 'MultiVmin'
	VoltagesOffset = ''
		
	return NativeMultiTrial(
			name=f'ARR_{IP}_VMIN_K_{subflow}_HITO_VCCIA_{freqcorner}_X_{testname.upper()}' if kill==1 else f'ARR_{IP}_VMIN_E_{subflow}_HITO_VCCIA_{freqcorner}_X_{testname.upper()}',
			trialvar='IPC::CPU_TRIALS::FlowDomain.ATOM_TOP',
			exitaction="Continue" if kill==1 else "Restore",
			_comment='Sample VminTC test with MTT',
			template=VminTC(name=f'"ARR_{IP}_VMIN_K_{subflow}_HITO_VCCIA_{freqcorner}_" + __shared__::Corners.AT_C5 + "_{testname.upper()}"' if kill==1 else f'"ARR_{IP}_E_{subflow}_HITO_VCCIA_{freqcorner}_" + "{prefix_for_flowmatrix}.{flowmatrix} + "{testname.upper()}"',
			BypassPort = bypass,
			CornerIdentifiers = TrialParamSpec(f'__shared__::CornerIdentifiers.AT_C5'), #if 'CDIE_' in flowmatrix else TrialParamSpec(f'{CornerIdentifiers}'),
			DtsConfiguration = ifEmpty(f'{dts}'),
			EndVoltageLimits = Spec(f'__shared__::FlowMatrixSingular.AT_HIGH_SEARCH_VALUE'), #+","+__shared__::FlowMatrix.AT_HIGH_SEARCH_VALUE'),
			ExecutionMode = ifEmpty(f'{ExecutionMode}'),
			FlowIndex = Spec("__shared__::FlowMatrixSingular.FlowIndex"),
			#FlowIndexCallbackName = ifEmpty(f'{FlowIndexCallbackName}'),
			ForwardingMode = ifEmpty(f'{ForwardingMode}'),
			LevelsTc = f'{level}',
			LimitGuardband = ifEmpty(f'{LimitGuardband}'),
			Patlist = f'{plist_name}',
			PatternNameCounterIndexes = "9,10,11,12,13,14,15",
			BaseNumbers = AUTO, # if 'srh' not in template else None,
			ScoreboardEdgeTicks = Spec(f'{ScoreboardEdgeTicks}') if ScoreboardEdgeTicks else None,
			MaxFailsNum = Spec(f'{MaxFailsNum}') if MaxFailsNum else None,
			SetPointsPlistParamName = "Patlist",
			SetPointsPreInstance = TrialParamSpec(f'"MCdrv:atomfreq_0:"+'+Spec(f"__shared__::FreqValues.AT_C5+")+'"GHz,MCdrv:corefreq:"+'+Spec(f"__shared__::FlowMatrixSingular.{flowmatrix}+")+'"GHz,MCdrv:ringfreq_0:"+'+Spec(f"__shared__::FreqValues.CCF_C5+")+'"GHz,MCAarr:ratio_modify:"+'+Spec(f"__shared__::FlowMatrixSingular.{flowmatrix}+")+'"GHz"'),
			StartVoltages = Spec(f'__shared__::FlowMatrixSingular.AT_LOW_SEARCH_VALUE'), #'+","+__shared__::FlowMatrix.AT_LOW_SEARCH_VALUE'),
			StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.AT_SEARCH_RESOLUTION)'),
			TestMode = ifEmpty(f'{TestMode}'), 
			TimingsTc = f'{timing}',
			VoltagesOffset = ifEmpty(f'{VoltagesOffset}'),
			VoltageTargets = f'{voltage_target}',
			#VoltageConverter = Spec(voltageconverter) if voltageconverter else None,
			VoltageConverter = Spec(f'"--railconfigurations CDIE_ATOM_POWERMUXM0 CDIE_ATOM_POWERMUXM1 CDIE_ATOM_POWERMUXM2 CDIE_ATOM_POWERMUXM3 CDIE_L2_NBLCTRL0 CDIE_L2_NBLCTRL1 CDIE_L2_NBLCTRL2 CDIE_L2_NBLCTRL3 --dlvrpins VCCIA --expressions "' + f' + DROPOUT.AT_{freqcorner}'),
			PinMap = pinmap,
			RecoveryMode = recoverymode,
			#RecoveryOptions = recoveryoptions,
			RecoveryOptions ='CLASS_NVL_S28C_8A',
			StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
			StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
			FivrCondition = 'NOM',
			RecoveryTrackingIncoming = 'ACRM3,ACRM2,ACRM1,ACRM0',
			RecoveryTrackingOutgoing = 'ACRM3,ACRM2,ACRM1,ACRM0',
			FeatureSwitchSettings = 'recovery_update_always,disable_masked_targets,fivr_mode_on,print_per_target_increments,print_scoreboard_counters',
			#FivrCondition = 'NOM',
			),

			r0=pFail(setbin=AUTO, ret=0, trialaction = Spec(f'__shared__::TpRule.MTT_Rule("Next","Exit")')),
			r1=pPass(setbin=AUTO, ret=1, trialaction = "Exit"),
			r2=pFail(setbin=AUTO, ret=2, trialaction = Spec(f'__shared__::TpRule.MTT_Rule("Next","Exit")')),
			r3=pPass(setbin=AUTO, ret=1, trialaction = "Exit"),
			r4=pFail(setbin=AUTO, ret=4, trialaction = Spec(f'__shared__::TpRule.MTT_Rule("Next","Exit")')),
			r5=pFail(setbin=AUTO, ret=5, trialaction = Spec(f'__shared__::TpRule.MTT_Rule("Next","Exit")')))

def get_VminTC_multitrial_singlevmin(testname,content,subflow,freqcorner): 
	bypass = content['bypass']
	kill = content['kill']
	template = content['template']
	flowmatrix = content['flowmatrix']
	dts = content['dts'] if 'dts' in content else ''
	if 'hermes' not in content:
		hermes = 'list'
	else:
		hermes = "master" if content['hermes'] == "1" else "long__1"
	if 'CDIE_' not in flowmatrix:
		voltageDomain = content['flowmatrix'].split('_')[0]
	else:
		voltageDomain = "VCCIA"
			
	
	
	#recovery handling
	pinmap = POR_PinMap if 'recovery' not in content else None
	recoverymode = POR_RecoverMode if 'recovery' not in content else None
	recoveryoptions = POR_RecoveryOptions if 'recovery' in content else None
	incomingtrackers = POR_RecoveryTrackingIncoming if 'recovery' in content else None
	outgoingtrackers = POR_RecoveryTrackingOutgoing if 'recovery' in content else None
	featureswitchsettings = POR_FeatureSwitchSettings_MultiVmin if 'recovery' in content else None

	#Voltage converter handling
	voltageconverter = '"--overrides ' + content['voltageoverride'] if 'voltageoverride' in content else ''
	if 'powermux' in content:
		voltageconverter = f'"{content["powermux"]}"' if voltageconverter=='' else (voltageconverter + ' + ' + f'" {content["powermux"]}"')
	
	if 'plist' in content and testname == "COMBINED":
		supply = 'VCCATOM'
		plist_testname = 'ALL'
		plist_name = f"IPC::arr_{dielet.lower()}_{subflow.lower()}_{dft.lower()}_{IP.lower()}_{content['plist'][0].lower()}_{content['plist'][1].lower()}_{supply.lower()}_{content['plist'][2].lower()}_{plist_testname.lower()}_{freqcorner.lower()}_hptp800_{socket.lower()}_{hermes}"
	elif 'plist' in content and testname == "SSA":
		supply = 'VCCATOM'
		plist_testname = 'L2'
		plist_name = f"IPC::arr_{dielet.lower()}_{subflow.lower()}_{dft.lower()}_{IP.lower()}_{content['plist'][0].lower()}_{content['plist'][1].lower()}_{supply.lower()}_{content['plist'][2].lower()}_{plist_testname.lower()}_{freqcorner.lower()}_hptp800_{socket.lower()}_{hermes}"
	else: 
		'plist' in content and testname == "SSA_l2tag"
		supply = 'VCCATOM'
		plist_testname = 'L2'
		plist_name = f"IPC::arr_{dielet.lower()}_{subflow.lower()}_{dft.lower()}_{IP.lower()}_{content['plist'][0].lower()}_{content['plist'][1].lower()}_{supply.lower()}_{content['plist'][2].lower()}_{plist_testname.lower()}_{freqcorner.lower()}_hptp800_{socket.lower()}_{hermes}"
	
	# supply override handling
	supply = content['supply']
	voltage_target = supply

	if 'CDIE_' not in flowmatrix:		
		CornerIdentifiers = '"'		
		for i,item in enumerate(corner_id):
			CornerIdentifiers += item + '@' + freq_corner			
			if i<len(corner_id)-1:
				CornerIdentifiers += ','				
		CornerIdentifiers += '"'
		prefix_for_flowmatrix = "__shared__::CustomFlowMatrixSpecs"
		#print(f'{CornerIdentifiers}')
	else:
		prefix_for_flowmatrix = "__shared__::Corners"
	
	ExecutionMode = 'SearchWithScoreboard'
	ForwardingMode = 'InputOutput' if kill==1 else "Input"
	LimitGuardband = ''
	ScoreboardEdgeTicks = 'toInteger(__shared__::Specs.CHK_EDGE_TICK)'
	MaxFailsNum = 'toInteger(__shared__::Specs.CHK_MAX_FAILS)'
	TestMode = 'MultiVmin' #change to multivmin for speedflow test ww27p1 fmohdfai
	VoltagesOffset = ''
		
	return NativeMultiTrial(
			name=f'ARR_{IP}_VMIN_K_{subflow}_HITO_VCCIA_{freqcorner}_X_{testname.upper()}' if kill==1 else f'ARR_{IP}_VMIN_E_{subflow}_HITO_VCCIA_{freqcorner}_X_{testname.upper()}',
			trialvar='IPC::CPU_TRIALS::FlowDomain.ATOM',
			exitaction="Continue" if kill==1 else "Restore",
			_comment='Sample VminTC test with MTT',
			template=VminTC(name=f'"ARR_{IP}_K_{subflow}_HITO_VCCIA_{freqcorner}_" + {prefix_for_flowmatrix}.{flowmatrix}_MHz + "_{testname.upper()}"' if kill==1 else f'"ARR_{IP}_E_{subflow}_HITO_VCCIA_{freqcorner}_" + {prefix_for_flowmatrix}.{flowmatrix} + "_{testname.upper()}"',
			BypassPort = bypass,
			CornerIdentifiers = TrialParamSpec(f'__shared__::CornerIdentifiers.CDIE_C3') if 'CDIE_' in flowmatrix else TrialParamSpec(f'{CornerIdentifiers}'),
			DtsConfiguration = ifEmpty(f'{dts}'),
			EndVoltageLimits = Spec(f'__shared__::FlowMatrixSingular.AT_HIGH_SEARCH_VALUE'), #+","+__shared__::FlowMatrix.AT_HIGH_SEARCH_VALUE'),
			ExecutionMode = ifEmpty(f'{ExecutionMode}'),
			FlowIndex = Spec("__shared__::FlowMatrixSingular.FlowIndex"),
			#FlowIndexCallbackName = ifEmpty(f'{FlowIndexCallbackName}'),
			ForwardingMode = ifEmpty(f'{ForwardingMode}'),
			LevelsTc = f'{level}',
			LimitGuardband = ifEmpty(f'{LimitGuardband}'),
			Patlist = f'{plist_name}',
			PatternNameCounterIndexes = "9,10,11,12,13,14,15",
			BaseNumbers = AUTO, # if 'srh' not in template else None,
			ScoreboardEdgeTicks = Spec(f'{ScoreboardEdgeTicks}') if ScoreboardEdgeTicks else None,
			MaxFailsNum = Spec(f'{MaxFailsNum}') if MaxFailsNum else None,
			SetPointsPlistParamName = "Patlist",
			SetPointsPreInstance = TrialParamSpec(f'"MCdrv:atomfreq_0:"+'+Spec(f"__shared__::FlowMatrixSingular.{flowmatrix}+")+'"GHz,MCdrv:corefreq:"+'+Spec(f"__shared__::FlowMatrixSingular.{flowmatrix}+")+'"GHz,MCdrv:ringfreq_0:"+'+Spec(f"__shared__::FlowMatrixSingular.{flowmatrix}+")+'"GHz,MCAarr:ratio_modify:"+'+Spec(f"__shared__::FlowMatrixSingular.{flowmatrix}+")+'"GHz"'),
			StartVoltages = Spec(f'__shared__::FlowMatrixSingular.AT_LOW_SEARCH_VALUE'), #'+","+__shared__::FlowMatrix.AT_LOW_SEARCH_VALUE'),
			StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.AT_SEARCH_RESOLUTION)'),
			TestMode = ifEmpty(f'{TestMode}'), 
			TimingsTc = f'{timing}',
			VoltagesOffset = ifEmpty(f'{VoltagesOffset}'),
			VoltageTargets = f'{voltage_target}',
			#VoltageConverter = Spec(voltageconverter) if voltageconverter else None,
			VoltageConverter = Spec(f'"--railconfigurations CDIE_ATOM_POWERMUXM0 CDIE_ATOM_POWERMUXM1 CDIE_ATOM_POWERMUXM2 CDIE_ATOM_POWERMUXM3 CDIE_L2_NBLCTRL0 CDIE_L2_NBLCTRL1 CDIE_L2_NBLCTRL2 CDIE_L2_NBLCTRL3 --dlvrpins VCCIA --expressions "' + f' + DROPOUT.AT_{freqcorner}'),
			PinMap = pinmap,
			RecoveryMode = recoverymode,
			#RecoveryOptions = recoveryoptions,
			RecoveryOptions ='CLASS_NVL_S28C_8A',
			StartVoltagesForRetry = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "")'),
			StartVoltagesOffset = Spec(f'__shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "")'),
			FivrCondition = 'NOM',
			RecoveryTrackingIncoming = 'ACRM3,ACRM2,ACRM1,ACRM0',
			RecoveryTrackingOutgoing = 'ACRM3,ACRM2,ACRM1,ACRM0',
			FeatureSwitchSettings ='recovery_update_always,disable_masked_targets,fivr_mode_on,print_per_target_increments,print_scoreboard_counters',
			
			),

			r0=pFail(setbin=AUTO, ret=0, trialaction = Spec(f'__shared__::TpRule.MTT_Rule("Next","Exit")')),
			r1=pPass(setbin=AUTO, ret=1, trialaction = "Exit"),
			r2=pFail(setbin=AUTO, ret=2, trialaction = Spec(f'__shared__::TpRule.MTT_Rule("Next","Exit")')),
			r3=pPass(setbin=AUTO, ret=1, trialaction = "Exit"),
			r4=pFail(setbin=AUTO, ret=4, trialaction = Spec(f'__shared__::TpRule.MTT_Rule("Next","Exit")')),
			r5=pFail(setbin=AUTO, ret=5, trialaction = Spec(f'__shared__::TpRule.MTT_Rule("Next","Exit")')))

def get_VminTC_multitrial_multivmin(testname,content,subflow,freqcorner): 
	bypass = content['bypass']
	kill = content['kill']
	template = content['template']
	flowmatrix = content['flowmatrix']
	dts = content['dts'] if 'dts' in content else ''
	if 'hermes' not in content:
		hermes = 'list'
	else:
		hermes = "master" if content['hermes'] == "1" else "long__1"
	voltageDomain = content['flowmatrix'].split('_')[0]
			
	
	
	#recovery handling
	pinmap = POR_PinMap if 'recovery' not in content else None
	recoverymode = POR_RecoverMode if 'recovery' not in content else None
	recoveryoptions = POR_RecoveryOptions if 'recovery' in content else None
	incomingtrackers = POR_RecoveryTrackingIncoming if 'recovery' in content else None
	outgoingtrackers = POR_RecoveryTrackingOutgoing if 'recovery' in content else None
	featureswitchsettings = POR_FeatureSwitchSettings_MultiVmin if 'recovery' in content else None

	#Voltage converter handling
	voltageconverter = '"--overrides ' + content['voltageoverride'] if 'voltageoverride' in content else ''
	if 'powermux' in content:
		voltageconverter = f'"{content["powermux"]}"' if voltageconverter=='' else (voltageconverter + ' + ' + f'" {content["powermux"]}"')
	
	if 'plist' in content and testname == "COMBINED":
		supply = 'VCCATOM'
		plist_testname = 'ALL'
		plist_name = f"IPC::arr_{dielet.lower()}_{subflow.lower()}_{dft.lower()}_{IP.lower()}_{content['plist'][0].lower()}_{content['plist'][1].lower()}_{supply.lower()}_{content['plist'][2].lower()}_{plist_testname.lower()}_{freqcorner.lower()}_hptp800_{socket.lower()}_{hermes}"
	elif 'plist' in content and testname == "SSA":
		supply = 'VCCATOM'
		plist_testname = 'L2'
		plist_name = f"IPC::arr_{dielet.lower()}_{subflow.lower()}_{dft.lower()}_{IP.lower()}_{content['plist'][0].lower()}_{content['plist'][1].lower()}_{supply.lower()}_{content['plist'][2].lower()}_{plist_testname.lower()}_{freqcorner.lower()}_hptp800_{socket.lower()}_{hermes}"
	
	# supply override handling
	supply = content['supply']

	if 'CDIE_' in flowmatrix:		
		CornerIdentifiers = ''
		voltage_target = ''
		for i,item in enumerate(corner_id):
			CornerIdentifiers += item + '@' + freq_corner
			voltage_target += supply
			if i<len(corner_id)-1:
				CornerIdentifiers += ','
				voltage_target += ','

	#if 'CDIE_' not in flowmatrix:		
	#	CornerIdentifiers = ''
	#	for i,item in enumerate(corner_id):
	#		CornerIdentifiers += item + '@' + freq_corner
	#		if i<len(corner_id)-1:
	#			CornerIdentifiers += ','
	#else:
	#	CornerIdentifiers = ''

	ExecutionMode = 'SearchWithScoreboard'
	ForwardingMode = 'InputOutput' if kill==1 else "Input"
	LimitGuardband = 'GBVars.LimitGuardband'
	ScoreboardEdgeTicks = 'toInteger(__shared__::Specs.CHK_EDGE_TICK)'
	MaxFailsNum = 'toInteger(__shared__::Specs.CHK_MAX_FAILS)'
	TestMode = 'MultiVmin'
	VoltagesOffset = 'GBVars.VoltageOffset'
	#elif 'srh' in template:
	#	#CornerIdentifiers = ''
	#	#for i,item in enumerate(corner_id):
	#	#	CornerIdentifiers += item + '@' + freq_corner
	#	#	if i<len(corner_id)-1:
	#	#		CornerIdentifiers += ','
	#
	#	ExecutionMode = 'Search'
	#	FlowIndexCallbackName = ''
	#	ForwardingMode = 'InputOutput' if kill==1 else "Input"
	#	LimitGuardband = ''
	#	ScoreboardEdgeTicks = ''
	#	MaxFailsNum = ''
	#	TestMode = 'MultiVmin'
	#	VoltagesOffset = ''
	#else: # max		
	#	#CornerIdentifiers = ''
	#	ExecutionMode = ''
	#	#FlowIndexCallbackName = ''
	#	ForwardingMode = 'Input' if 'recovery' in content else "None"
	#	LimitGuardband = ''
	#	ScoreboardEdgeTicks = 'toInteger(Specs.VMX_EDGE_TICK)'
	#	MaxFailsNum = 'toInteger(Specs.VMX_MAX_FAILS)'
	#	TestMode = 'Scoreboard'
	#	VoltagesOffset = ''
	#	
	#	# recovery handling
	#	recoverymode = 'NoRecovery' if 'recovery' in content else None

	
	return NativeMultiTrial(
			name=f'ARR_{IP}_VMIN_K_{subflow}_HITO_{voltageDomain}_{freqcorner}_{flowmatrix}_{testname.upper()}' if kill==1 else f'ARR_{IP}_VMIN_E_{subflow}_HITO_{voltageDomain}_{freqcorner}_{flowmatrix}_{testname.upper()}',
			#trialvar='IP_PCH_BASE::FlowDomain.Default', 
			trialvar='IPC::CPU_TRIALS::FlowDomain.ATOM',
			exitaction="Continue" if kill==1 else "Restore",
			_comment='Sample VminTC test with MTT',
			template=VminTC(name=f'"ARR_{IP}_K_{subflow}_HITO_{voltageDomain}_{freqcorner}_" + __shared__::Corners.{flowmatrix} + "_{testname.upper()}"' if kill==1 else f'"ARR_{IP}_E_{subflow}_HITO_{voltageDomain}_{freqcorner}_" + __shared__::FlowMatrix.{flowmatrix} + "_{testname.upper()}"',
			BypassPort = bypass,
			CornerIdentifiers = TrialParamSpec(f'__shared__::CornerIdentifiers.CDIE_C3') if 'CDIE_' in flowmatrix else ifEmpty(f'{CornerIdentifiers}'),
			DtsConfiguration = ifEmpty(f'{dts}'),
			EndVoltageLimits = Spec(f'__shared__::FlowMatrixSingular.AT_HIGH_SEARCH_VALUE'), #+","+__shared__::FlowMatrix.AT_HIGH_SEARCH_VALUE'),
			ExecutionMode = ifEmpty(f'{ExecutionMode}'),
			FlowIndex = Spec("__shared__::FlowMatrixSingular.FlowIndex"),
			#FlowIndexCallbackName = ifEmpty(f'{FlowIndexCallbackName}'),
			ForwardingMode = ifEmpty(f'{ForwardingMode}'),
			LevelsTc = f'{level}',
			LimitGuardband = ifEmpty(f'{LimitGuardband}'),
			Patlist = f'{plist_name}',
			PatternNameCounterIndexes = "9,10,11,12,13,14,15",
			BaseNumbers = AUTO, # if 'srh' not in template else None,
			ScoreboardEdgeTicks = Spec(f'{ScoreboardEdgeTicks}') if ScoreboardEdgeTicks else None,
			MaxFailsNum = Spec(f'{MaxFailsNum}') if MaxFailsNum else None,
			SetPointsPlistParamName = "Patlist",
			#SetPointsPreInstance = TrialParamSpec(gen_SetPointsPreInstance(freqcorner,template)),
			StartVoltages = Spec(f'__shared__::FlowMatrixSingular.AT_LOW_SEARCH_VALUE'), #'+","+__shared__::FlowMatrix.AT_LOW_SEARCH_VALUE'),
			StepSize = Spec(f'toDouble(__shared__::FlowMatrixSingular.AT_SEARCH_RESOLUTION)'),
			TestMode = ifEmpty(f'{TestMode}'), 
			TimingsTc = f'{timing}',
			VoltagesOffset = ifEmpty(f'{VoltagesOffset}'),
			VoltageTargets = f'{voltage_target}',
			VoltageConverter = Spec(voltageconverter) if voltageconverter else None,
			PinMap = pinmap,
			RecoveryMode = recoverymode,
			RecoveryTrackingIncoming = 'ACRM3,ACRM2,ACRM1,ACRM0',
			RecoveryTrackingOutgoing = 'ACRM3,ACRM2,ACRM1,ACRM0',
			FeatureSwitchSettings = 'recovery_update_always,disable_masked_targets,fivr_mode_on',
			FivrCondition = 'NOM',
			),

			r0=pFail(setbin=AUTO, ret=0, trialaction = Spec(f'__shared__::TpRule.MTT_Rule("Next","Exit")')),
			r1=pPass(setbin=AUTO, ret=1, trialaction = "Exit"),
			r2=pFail(setbin=AUTO, ret=2, trialaction = Spec(f'__shared__::TpRule.MTT_Rule("Next","Exit")')),
			r3=pFail(setbin=AUTO, ret=3, trialaction = Spec(f'__shared__::TpRule.MTT_Rule("Next","Exit")')),
			r4=pFail(setbin=AUTO, ret=4, trialaction = Spec(f'__shared__::TpRule.MTT_Rule("Next","Exit")')),
			r5=pFail(setbin=AUTO, ret=5, trialaction = Spec(f'__shared__::TpRule.MTT_Rule("Next","Exit")')))

def get_DDGShmooTC_test(testname,content,subflow,freqcorner):
	# example	
	# Test DDGShmooTC SOC_ATOM_SHMOO_K_DEDC_X_VATOM_X_X_SHMOO {
		#LevelsTc = "BASE::soc_all_dft_x_x_pkg_lvl_nom_lvl";
		#LogLevel = "Disabled";
		#MaskPins = "";
		#Patlist = "funsoc_csnf1_nocbist_list";
		#SetPointsPlistParamName = "Patlist";
		#SetPointsPostInstance = "";
		#SetPointsPreInstance = "";
		#TimingsTc = "BASE::soc_hvm_timing_tclk100_xtal100_rtc4_bclk400_tam200_ssnin400_ssnout400";
		#VoltageConverter = "";
		#XAxisParam = "p_mtd_per";
		#XAxisRange = "8e-9:1e-9:5";
		#YAxisParam = "p_VCCATOM_spec";
		#YAxisRange = "0.45:0.01:40";
		#BypassPort = -1;	
	return DDGShmooTC(
				name = f"ARR_{IP}_SHMOO_E_{subflow}_X_X_X_X_{testname.upper()}",
				BypassPort = 1,
				PrintFormat = "ShmooHub",
				LevelsTc = level,
				TimingsTc = timing,
				LogLevel = "Disabled",
				SetPointsPlistMode = "Local",
				Patlist = content['Patlist'],
				SetPointsPlistParamName = "Patlist",
				XAxisDatalogPrefix = "Nano",
				XAxisType = content['XAxisType'] if 'XAxisType' in content else None,
				XAxisParam = content['XAxisParam'] if 'XAxisParam' in content else "p_cpu_per",
				XAxisRange = content['XAxisRange'] if 'XAxisRange' in content else "1.15e-9:0.05e-9:5",
				YAxisType = content['YAxisType'] if 'YAxisType' in content else None,
				YAxisParam = content['YAxisParam'] if 'YAxisParam' in content else 'ATOM0',
				YAxisRange = content['YAxisRange'] if 'YAxisRange' in content else '0.45:0.05:12',
				YAxisParamType = "UserDefined",
				XAxisParamType = "UserDefined",
				SetPointsPreInstance = content['SetPointsPreInstance'] if 'SetPointsPreInstance' in content else None,
				SetPointsPostInstance = content['SetPointsPostInstance'] if 'SetPointsPostInstance' in content else None,
				VoltageConverter = content['VoltageConverter'] if 'VoltageConverter' in content else "--dlvrpins VCCIA --fivrcondition NOM",
				MaskPins = content['MaskPins'] if 'MaskPins' in content else None,								
				
					_fitem=Fitem('SAME', edc = True,
						r0 = pFail(setbin=AUTO),
						r2 = pFail(setbin=AUTO),
						r3 = pFail(setbin=AUTO)))

def get_DedcLoadConfigTC_test():
	return RunCallback(
		name = "CTRL_X_UF_E_INIT_X_X_X_X_PINMAP_ARRATOM",
		BypassPort = 1,
		Parameters = "--decoder FailDataDecoder --file ./Modules/ARR/ARR_ATOM_CXX/InputFiles/DieRecoveryPinMaps_NVL_ARRATOM_28C.json",
		LogLevel = "Disabled",
		Callback = "LoadPinMapFile",
			_fitem=Fitem('SAME', edc = False,
                 r0 = pFail(setbin=-60, ret=0)))

def get_DedcLoadConfigTC_test1():
	return RunCallback(
		name = "ARR_ATOM_RUNCALLBACK_K_INIT_X_X_X_X_APEXTC",
		BypassPort = 1,
		Parameters = "--decoder FailDataDecoder --file ./Modules/ARR/ARR_ATOM_CXX/InputFiles/ApexTC_Input_Config.json",
		LogLevel = "Disabled",
		Callback = "ReadFrequencyPatConfigFile",
			_fitem=Fitem('SAME', edc = False,
                 r0 = pFail(setbin=-60, ret=0)))

def get_thermaltdau_test(subflow, corner):
   return PrimeThermalSingleMeasurementTestMethod(
				name = f"SBFT_X_TDAU_E_{subflow}{corner}_X_VATOM_{corner}_X_POST",
				#IntegrityHighLimit = 200,
				#IntegrityLowLimit = 130,
				LowerTolerance = "30",
				PinNames = "IP_CPU::TDAU_CH_CORE",
				UpperTolerance = "30",
					_fitem=Fitem('SAME', edc = True,
                        r0 = pFail(goto="NEXT"),
                        r1 = pPass(goto="NEXT"),
                        r2 = pFail(goto="NEXT"),
                        r3 = pFail(goto="NEXT"),
                        r4 = pFail(goto="NEXT"),
                        r5 = pFail(goto="NEXT")))

def get_FmaxTC_test(testname,content,subflow,freqcorner):
	# example of ARL CDIE FmaxTC template settup
	#Test FmaxTC SBFT_ATOM_FMAX_E_MAXAT_X_VATOM_F6_3400_L2_DRAGON_IS_FMAX_M0 {
	#		Patlist = "funatom_cdie_maxat_f6_L2_dragon_IS_list";
	#		LevelsTc = "IP_CPU_BASE::cpu_all_bf_x_x_ipcpu_lvl_min_lvl";
	#		SearchEnd = 2.3;
	#		SearchParameter = "p_fmax_freq";
	#		SearchStart = 4.2;
	#		SearchStep = 0.1;
	#		TimingsTc = "IP_CPU::FUN_ATOM_CXX::FUN_ATOM_CXX_FMAX_TC_tdo2ssn_tclk100_sclk400_cclk400";
	#		SetPointsPlistParamName = "Patlist";
	#		SetPointsPreInstance = FUN_ATOM_CXX.ATOMCORE_M0_ENABLE + ",FUNATOM:AtomM0:enabled,FUNATOM:AtomM1:disabled,MCdrv:core_disable:disable_core,MCdrv:atomfreq:3.4GHz,MCdrv:ringfreq:0.8GHz,AtomFun:freq_corners:3.4GHz,MCdrv:pwrmux_sel_atom_l2:vcclogic,MCdrv:R1_SET";
	#		SetPointsPostInstance = "MCdrv:core_disable:enable_core,MCdrv:atomcore_disable:mask_0xc,FUNATOM:AtomM0:enabled,FUNATOM:AtomM1:enabled,MCdrv:R1_SET";
	#		PreInstance = FUN_ATOM_CXX.R1_M0_ENABLE;
	#		PostInstance = FUN_ATOM_CXX.R1_ALL_ENABLE;
	#		PrePlist = "VoltageConverter(--railconfigurations CDIE_ATOM_POWERMUXM0 --dlvrpins IP_CPU::VCCIA_HC --overrides ATOM0:1.10 --fivrcondition NOM)";
	#
	# content_list = {	"L2dragon"	: { "bypass":1, "kill":0,'template':'FmaxTC','Patlist':'filloutpatlistname','TimingsTc':'filloutoverridetiming',
	#                                   'SearchParameter':'filloutSearchParameter','SearchStart':'filloutSearchStart','SearchEnd':'filloutSearchEnd','SearchStep':'filloutSearchStep',
	#                                   'SetPointsPreInstance':'filloutSetPointsPreInstance','SetPointsPostInstance':'filloutSetPointsPostInstance',	# these are optional
	#								    'PreInstance':'filloutPreInstance','PostInstance':'filloutPostInstance','PrePlist':'filloutPrePlist'			# these are optional
	#								  }}
	bypass = content['bypass']
	kill = content['kill']
	return FmaxTC(name = f"FUNC_{IP}_FMAX_K_{subflow}_X_X_X_X_{testname.upper()}" if kill==1 else f"FUNC_{IP}_FMAX_E_{subflow}_X_X_X_X_{testname.upper()}",
				BypassPort = bypass,
				Patlist = content['Patlist'],
				LevelsTc = level,
				TimingsTc = content['TimingsTc'],
				SearchParameter = content['SearchParameter'],
				SearchStart = content['SearchStart'],
				SearchEnd = content['SearchEnd'],
				SearchStep = content['SearchStep'],
				SetPointsPlistParamName = "Patlist",
				SetPointsPreInstance = content['SetPointsPreInstance'] if 'SetPointsPreInstance' in content else None,
				SetPointsPostInstance = content['SetPointsPostInstance'] if 'SetPointsPostInstance' in content else None,
				PreInstance = content['PreInstance'] if 'PreInstance' in content else None,
				PostInstance = content['PostInstance'] if 'PostInstance' in content else None,
				PrePlist = content['PrePlist'] if 'PrePlist' in content else None,
					_fitem=Fitem('SAME', edc = False if (kill==1) else True,
						r0 = pFail(setbin=AUTO, ret=0) if (kill==1) else pFail(setbin=AUTO),
						r2 = pFail(setbin=AUTO, ret=0) if (kill==1) else pFail(setbin=AUTO),
						r3 = pFail(setbin=AUTO, ret=0) if (kill==1) else pFail(setbin=AUTO),
						r4 = pFail(setbin=AUTO, ret=0) if (kill==1) else pFail(setbin=AUTO),
						r5 = pFail(setbin=AUTO, ret=0) if (kill==1) else pFail(setbin=AUTO)))

def get_ScreenTC_test(testname,content,subflow,freqcorner):
	bypass = content['bypass']
	kill = content['kill']
	ScreenTestSet = content['screentestset']	
	ScreenTestsFile = content['screentestfile']	
	PreInstance = content['preinstance'] if 'preinstance' in content else ''
	PostInstance = content['postinstance'] if 'postinstance' in content else ''

	return ScreenTC(
				name = f"CTRL_X_SCREEN_K_{subflow}_X_X_X_X_{testname.upper()}" if kill==1 else f"CTRL_X_SCREEN_E_{subflow}_X_X_X_X_{testname.upper()}",
				BypassPort = bypass,
				ScreenTestSet = ScreenTestSet,
				ScreenTestsFile = ScreenTestsFile,
				PreInstance = ifEmpty(PreInstance),
				PostInstance = ifEmpty(PostInstance),
					_fitem=Fitem('SAME', edc = False if kill==1 else True,
                        r0 = pFail(setbin=AUTO, ret=0) if (kill==1) else pFail(setbin=AUTO)))

def get_RunCallback_test(testname,content,subflow,freqcorner):
	bypass = content['bypass']
	kill = content['kill']
	param = content['param']
	callback = content['callback']
	return RunCallback(
				name = f"CTRL_X_PRIMEDIERECOVERY_K_{subflow}_X_X_X_X_{testname.upper()}" if kill==1 else f"CTRL_X_PRIMEDIERECOVERY_K_{subflow}_X_X_X_X_{testname.upper()}",
				BypassPort = bypass,
				Callback = callback,
				Parameters = param,
					_fitem=Fitem('SAME', edc = False if kill==1 else True,
                        r0 = pFail(setbin=AUTO, ret=0) if (kill==1) else pFail(setbin=AUTO)))
############ RWA BEGINCPUNOM ################

def get_PrimePatConfigTestMethod_test():
	return PrimePatConfigTestMethod(
				name = f"ALL_X_FUSECONFIG_K_BEGINCPUNOM_X_X_X_X_ATOM_RWA_PATCONFIG",
				BypassPort = 1,
				ConfigurationFile = 'GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "/Modules/ARR/ARR_ATOM_CXX/InputFiles/APPLY_ATOM_RWA.FuseConfigSetPoints.json"',
				SetPoint = "ATOM_PER_DIE_RWA",
				RegEx = "[gdx].*_longreset_fuseover.*_MC.*(arr|fun).*",
					_fitem=Fitem('SAME', edc = False,
                        r0 = pFail(setbin=AUTO, ret=0)))


####### ENDCPU TEST TEMPLATE DEFINE #################
def get_RunCallback_endcpu_test(testname,content,subflow,freqcorner):
	bypass = content['bypass']
	kill = content['kill']
	param = content['param']
	callback = content['callback']

	return RunCallback(
				name = f"ARR_{IP}_RUNCALLBACK_K_{subflow}_HITO_X_{freqcorner}_X_{testname.upper()}" if kill==1 else f"ARR_{IP}_RUNCALLBACK_K_{subflow}_HITO_X_{freqcorner}_X_{testname.upper()}",
				BypassPort = bypass,
				Callback = callback,
				Parameters = param,
				PostInstance =  content['postcall'])#'PrintToItuff(--body_type strgval --body_data G.U.S.HUBATOMPMUX --tname_suf _HUMATOMPMUX_FREQ)')
					#_fitem=Fitem('SAME', edc = False if kill==1 else True,
					#	r0 = pFail(setbin=AUTO, ret=0) if (kill==1) else pFail(setbin=AUTO)))


############################################################

def get_mconfig():
	plistinfo	= {}

	for sku in packages:
		for setplist in packages[sku]['plist']:
			mconfigs	= setplist.split("\\")#packages[sku]['plist'].split("\\")
			path		= "\\".join(mconfigs[:-4])
			rev			= mconfigs[-4]
			patch		= mconfigs[-3]
			

			plistinfo[mconfigs[-1]] = packages[sku]['bom']

	alephfiles	= packages[sku]['alephfiles']
	# Define the Mconfig file configuration
	mconfig = MConfig(
		ip = "IPC", #The IPName is used for modules in IntraDut test program to declare the IP it belongs to.  For package level modules do not add the <IPName> element at all
		path=path,
		rev=rev,
		patch=patch,
		plistinfo=plistinfo
	)
	# local aleph files
	mconfig.aleph(alephfiles=alephfiles)

def get_test_list(contentlist,subflow,freqcorner):
	testlist = []
	for test in contentlist:
		if contentlist[test]['template'] == 'PrimePatConfigTestMethod':	
			testlist.append(get_PrimePatConfigTestMethod_test(test,contentlist[test],subflow,freqcorner))


		elif contentlist[test]['template'] == 'RunCallback':	
			testlist.append(get_RunCallback_test())

		elif contentlist[test]['template'] == 'RunCallback1':	
			testlist.append(get_RunCallback_endcpu_test(test,contentlist[test],subflow,freqcorner))

		elif contentlist[test]['template'] == 'ScreenTC':	
			testlist.append(get_ScreenTC_test(test,contentlist[test],subflow,freqcorner))

		elif contentlist[test]['template'] == 'FmaxTC':	
			testlist.append(get_FmaxTC_test(test,contentlist[test],subflow,freqcorner))

		elif contentlist[test]['template'] == 'DDGShmooTC':	
			testlist.append(get_DDGShmooTC_test(test,contentlist[test],subflow,freqcorner))
		
		elif contentlist[test]['template'] == 'VminTC_pt':
			testlist.append(get_VminTC_pt(test,contentlist[test],subflow,freqcorner))

		elif contentlist[test]['template'] == 'VminTC_vmin':
			testlist.append(get_VminTC_vmin(test,contentlist[test],subflow,freqcorner))

		elif contentlist[test]['template'] == 'ApexTC_fmax':
			testlist.append(get_ApexTC_fmax(test,contentlist[test],subflow,freqcorner))

		elif contentlist[test]['template'] == 'VminTC_MTT_singleVmin' or contentlist[test]['template'] == 'VminTC_chk' or contentlist[test]['template'] == 'VminTC_max': # vmin_srh,vmin_chk,vmin_max
			testlist.append(get_VminTC_multitrial_singlevmin(test,contentlist[test],subflow,freqcorner))

		elif contentlist[test]['template'] == 'VminTC_MTT_singleVmin_F5' or contentlist[test]['template'] == 'VminTC_chk' or contentlist[test]['template'] == 'VminTC_max': # vmin_srh,vmin_chk,vmin_max
			testlist.append(get_VminTC_multitrial_singlevmin_F5(test,contentlist[test],subflow,freqcorner))

		elif contentlist[test]['template'] == 'VminTC_MTT_multiVmin' or contentlist[test]['template'] == 'VminTC_MV_chk' or contentlist[test]['template'] == 'VminTC_MT_max': # vmin_srh,vmin_chk,vmin_max
			testlist.append(get_VminTC_multitrial_multivmin(test,contentlist[test],subflow,freqcorner))

		else:
			print(f"Template {contentlist[test]['template']} not found")	
	return testlist

################# START MTPL FLOW DEFINITON #####################
def gen_SetPointsPreInstance(freqcorner,template):			# adjust based on UPS release
	SetPointsPreInstance = ''
	freq = freqcorner+"_FREQ" if freqcorner != 'FMIN' else freqcorner
	matrix = '__shared__::FlowMatrixSingular' if template == 'vmin_pt' else '__shared__::FlowMatrixSingular'
	
	#SetPointsPreInstance += f'"MHdrv:ddrfreqqclk_0:"+{matrix}.SAQ_{freq}+"MHz"'
	##SetPointsPreInstance += f'+ ",MHdrv:ddrfreqqclk_1:"+{matrix}.SAQ_{freq}+"MHz"'
	#SetPointsPreInstance += f' + ",MHdrv:ddrfreqauxclk_0:"+{matrix}.SAN_{freq}+"MHz"'
	#SetPointsPreInstance += f' + ",MHdrv:ddrfreqgear_1:"+{matrix}.SAN_{freq}+"MHz"'
	#SetPointsPreInstance += f' + ",MHdrv:ddrfreqgear_2:"+{matrix}.SAN_{freq}+"MHz"'
	#SetPointsPreInstance += f' + ",MHdrv:cdclk_freq_0:"+{matrix}.SADPU_{freq}+"MHz"'	
	#SetPointsPreInstance += f' + ",MHdrv:ddrfreqphclk_0:"+{matrix}.SAC_{freq}+"MHz"'
	#SetPointsPreInstance += f' + ",MHdrv:ddrfreqwp2lcpll_0:"+{matrix}.SAPS_{freq}+"MHz"'
	#SetPointsPreInstance += f' + ",MHdrv:h2gfreq_0:"+{matrix}.SADPU_{freq}+"MHz"'
	#SetPointsPreInstance += f' + ",MHdrv:media_freq_0:"+{matrix}.SAME_{freq}+"MHz"'
	#SetPointsPreInstance += f' + ",MHdrv:media_freq_1:"+{matrix}.SAME_{freq}+"MHz"'
	#SetPointsPreInstance += f' + ",MHdrv:media_freq_2:"+{matrix}.SAME_{freq}+"MHz"'
	#SetPointsPreInstance += f' + ",MHdrv:nclk_freq_0:"+{matrix}.SAVPU_{freq}+"MHz"'
	#SetPointsPreInstance +=  x
	return SetPointsPreInstance
	
packages = {'S28C':{'plist':{"I:\\hdmxpats\\nvl_cpu\\MCAarr\\RevTCI8GA0.0\\p2\\plb\\arr_cdie_begincpunom_pbist_atom_ks_ttr_hptp800_class.plist", 
	                          "I:\\hdmxpats\\nvl_cpu\\MCAarr\\RevTCI8GA0.0\\p2\\plb\\arr_cdie_f1xat_pbist_atom_ks_ttr_f1_hptp800_class.plist",
							  "I:\\hdmxpats\\nvl_cpu\\MCAarr\\RevTCI8GA0.0\\p2\\plb\\arr_cdie_f2xat_pbist_atom_ks_ttr_f2_hptp800_class.plist",
							  "I:\\hdmxpats\\nvl_cpu\\MCAarr\\RevTCI8GA0.0\\p2\\plb\\arr_cdie_f3xat_pbist_atom_ks_ttr_f3_hptp800_class.plist",
							  "I:\\hdmxpats\\nvl_cpu\\MCAarr\\RevTCI8GA0.0\\p2\\plb\\arr_cdie_f4xat_pbist_atom_ks_ttr_f4_hptp800_class.plist",
							  "I:\\hdmxpats\\nvl_cpu\\MCAarr\\RevTCI8GA0.0\\p2\\plb\\arr_cdie_f5xat_pbist_atom_ks_ttr_f5_hptp800_class.plist",
							  "I:\\hdmxpats\\nvl_cpu\\MCAarr\\RevTCI8GA0.0\\p2\\plb\\arr_cdie_fminxat_pbist_atom_ks_ttr_fmin_hptp800_class.plist",
							 # "I:\\hdmxpats\\nvl_cpu\\MCAarr\\RevTCI8GA0.0\\p0\\plb\\arr_cdie_fbatxsn_pbist_atom_ks_ttr_fbat_hptp800_class.plist",
							  "I:\\hdmxpats\\nvl_cpu\\MCAarr\\RevTCI8GA0.0\\p2\\plb\\arr_cdie_vmaxxat_pbist_atom_vmaxf1_ttr_hptp800_class.plist",
							  "I:\\hdmxpats\\nvl_cpu\\MCAarr\\RevTCI8GA0.0\\p2\\plb\\arr_cdie_endcpu_pbist_atom_ks_ttr_fx_hptp800_class.plist",
							  "I:\\hdmxpats\\nvl_cpu\\MCAarr\\RevTCI8GA0.0\\p2\\plb\\arr_cdie_endcpunom_pbist_atom_l2_vatom_ret_f1_hptp800_class.plist", 
							  "I:\\hdmxpats\\nvl_cpu\\MCAarr\\RevTCI8GA0.0\\p2\\plb\\arr_cdie_x_pbist_atom_all_vatom_hry_all_f1_tito_class.plist",
							  "I:\\hdmxpats\\nvl_cpu\\MCAarr\\RevTCI8GA0.0\\p2\\plb\\arr_cdie_x_pbist_atom_all_vatom_raster_f1_tito_class.plist",
							  "I:\\hdmxpats\\nvl_cpu\\MCAarr\\RevTCI8GA0.0\\p2\\plb\\arr_cdie_vmaxxat_pbist_atom_vmaxf5_ttr_hptp800_class.plist"},'bom':'CLASS_NVL_S28C','alephfiles': ''}}
#			'S52C':{'plist':  {"I:\\hdmxpats\\nvl_cpu\\MCAarr\\RevTCI8GA0.0\\p1\\plb\\arr_CDIE_beginhubnom_pbist_atom_ks_ttr_hptp800_class_nvl_s52c.plist", 
#	                          "I:\\hdmxpats\\nvl_cpu\\MCAarr\\RevTCI8GA0.0\\p1\\plb\\arr_CDIE_f1xsn_pbist_atom_ks_ttr_f1_hptp800_class_nvl_s52c.plist",
#							  "I:\\hdmxpats\\nvl_cpu\\MCAarr\\RevTCI8GA0.0\\p1\\plb\\arr_CDIE_f2xsn_pbist_atom_ks_ttr_f2_hptp800_class_nvl_s52c.plist",
#							  "I:\\hdmxpats\\nvl_cpu\\MCAarr\\RevTCI8GA0.0\\p1\\plb\\arr_CDIE_f3xsn_pbist_atom_ks_ttr_f3_hptp800_class_nvl_s52c.plist",
#							  "I:\\hdmxpats\\nvl_cpu\\MCAarr\\RevTCI8GA0.0\\p1\\plb\\arr_CDIE_fminxsn_pbist_atom_ks_ttr_fmin_hptp800_class_nvl_s52c.plist",
#							  "I:\\hdmxpats\\nvl_cpu\\MCAarr\\RevTCI8GA0.0\\p1\\plb\\arr_CDIE_fbatxsn_pbist_atom_ks_ttr_fbat_hptp800_class_nvl_s52c.plist",
#							  "I:\\hdmxpats\\nvl_cpu\\MCAarr\\RevTCI8GA0.0\\p1\\plb\\arr_CDIE_vmaxxsn_pbist_atom_vmaxf1_ttr_hptp800_class_nvl_s52c.plist",
#							  "I:\\hdmxpats\\nvl_cpu\\MCAarr\\RevTCI8GA0.0\\p1\\plb\\arr_CDIE_vmaxxsn_pbist_atom_vmaxf3_ttr_hptp800_class_nvl_s52c.plist"},'bom':'CLASS_NVL_S52C','alephfiles': ''}} # ,'alephfiles':["InputFiles/fun_hub.patmod.json"]
			
# 'HX':{'plist':"I:\\hdmxpats\\arl_soc\\MSNfunatom\\RevTCSXSB0.0\\p0\\plb\\funsoc_class_allplist.plist_1",'bom':'CLASS_S68G1_HX','alephfiles':["InputFiles/fun_hub.patmod.json"]},
# 'SK':{'plist':"I:\\hdmxpats\\arl_soc\\MSNfunatom\\RevTCSXSB0.0\\p0\\plb\\funsoc_class_allplist.plist",'bom':'CLASS_S68G1_SK','alephfiles':["InputFiles/fun_hub.patmod.json"]}}
SKU = ''
content = 'ARR'
dielet = 'CPU'
IP = 'ATOM'
dft = 'pbist'
level = "CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_min"
timing = "IPC::ARR_ATOM_CXX::cpu_fun_timing_mts800_tstprtclk400_tck100_arratom"
corner_id = ""		# adjust based on UPS release , 'SACD0', 'SANPU0', 'SAIOC0'     ------ SACD0@F3,SAPS0

POR_dts_ctv = 'nvlcdie_ctv'
POR_dts_noctv = 'nvlcdie_noctv'

LSA_Range = (2075,2098) #ATOM LSA
SSA_ALL_Range = (6075,6098) #ATOM SSA/ALL
RET_Range = (6075,6098) #ATOM Retention
besenum = (12500,12749)
#NonPUP_Range = (2601,2749)

SSABin = -60
LSABin = -20
RETBin = -63
#PUPBN = -25
#NonPUPBN = -26

LSA_Thermal = 90972060
SSA_Thermal = 90976060
LSA_Reset = 90201960
SSA_Reset = 90601960
# With these dictionary definitions:
#LSA_Thermal = {"816": 90972060}
#SSA_Thermal = {"816": 90976060}
#LSA_Reset = {"816": 90201960}
#SSA_Reset = {"816": 90601960}



# define recovery settings here
POR_Pmux = '' #--railconfigurations CDIE_ATOM_POWERMUXM0'
POR_VoltageTarget = 'ATOM3,ATOM2,ATOM1,ATOM0' #CDIE_RST_00
POR_PinMap = 'NVL_ARRATOM' #'ARL_FUNATOM_HUBREC'
POR_RecoverMode = 'RecoveryPort' #No recovery for ATOM
POR_RecoveryOptions = 'CLASS_NVL_S28C_8A'
POR_RecoveryTrackingIncoming = 'ACRM3,ACRM2,ACRM1,ACRM0' # \Modules\TPI\TPI_HUBREC_HXX\InputFiles\HubRecovery_Rules.json
POR_RecoveryTrackingOutgoing = 'ACRM3,ACRM2,ACRM1,ACRM0' # \Modules\TPI\TPI_HUBREC_HXX\InputFiles\HubRecovery_Rules.json
POR_FeatureSwitchSettings = 'recovery_update_always,disable_masked_targets,fivr_mode_on,print_per_target_increments,print_scoreboard_counters' #"disable_masked_targets"
POR_FeatureSwitchSettings_SingleVmin = 'recovery_update_always,disable_masked_targets,fivr_mode_on,print_per_target_increments,print_scoreboard_counters' #"disable_masked_targets,incremental_recovery_loop"
POR_FeatureSwitchSettings_MultiVmin = 'recovery_update_always,disable_masked_targets,fivr_mode_on,print_per_target_increments,print_scoreboard_counters' #"disable_masked_targets,return_on_global_sticky_error"

package_to_mod_mapping = {'816':{'S28C','S52C'}}


# Function to determine the PrePlist value based on the corner and array_type
def get_preplist(corner, array_type):
    if corner == "NOM":
        return ""
    elif corner == "MIN":
        if array_type == "XSA":
            return "VoltageConverter(--overrides=ATOM0:VMIN_ATOM_CACHE_L2_VMINREP,ATOM1:VMIN_ATOM_CACHE_L2_VMINREP,ATOM2:VMIN_ATOM_CACHE_L2_VMINREP,ATOM0:VMIN_ATOM_CACHE_L2_VMINREP --dlvrpins IP_CPU::VCCIA --fivrcondition NOM)"
        elif array_type == "LSA":
            return "VoltageConverter(--overrides=ATOM0:VMIN_ATOM_CACHE_RF_VMINREP,ATOM1:VMIN_ATOM_CACHE_RF_VMINREP,ATOM2:VMIN_ATOM_CACHE_RF_VMINREP,ATOM3:VMIN_ATOM_CACHE_RF_VMINREP --dlvrpins IP_CPU::VCCIA --fivrcondition NOM)"
    elif corner == "RAS":
        if array_type == "XSA":
            return "VoltageConverter(--overrides=ATOM0:VMIN_ATOM_CACHE_L2_VMINREP,ATOM1:VMIN_ATOM_CACHE_L2_VMINREP,ATOM2:VMIN_ATOM_CACHE_L2_VMINREP,ATOM0:VMIN_ATOM_CACHE_L2_VMINREP --dlvrpins IP_CPU::VCCIA --fivrcondition NOM)"
        elif array_type == "SSA":
            return "VoltageConverter(--overrides=ATOM0:VMIN_ATOM_CACHE_L2_VMINREP,ATOM1:VMIN_ATOM_CACHE_L2_VMINREP,ATOM2:VMIN_ATOM_CACHE_L2_VMINREP,ATOM0:VMIN_ATOM_CACHE_L2_VMINREP --dlvrpins IP_CPU::VCCIA --fivrcondition NOM)"
        elif array_type == "LSA":
            return "VoltageConverter(--overrides=ATOM0:VMIN_ATOM_CACHE_RF_VMINREP,ATOM1:VMIN_ATOM_CACHE_RF_VMINREP,ATOM2:VMIN_ATOM_CACHE_RF_VMINREP,ATOM3:VMIN_ATOM_CACHE_RF_VMINREP --dlvrpins IP_CPU::VCCIA --fivrcondition NOM)"
    elif corner == "MAX":
        if array_type == "SSA":
            return "VoltageConverter(--overrides=VCCIA:VMAX_VOLTAGE)"
        elif array_type == "LSA":
            return "VoltageConverter(--overrides=VCCIA:VMAX_VOLTAGE)"
    return ""

################# END MTPL FLOW DEFINITON #####################
for sku in package_to_mod_mapping:

	SKU  = sku


	InitializeNVLClass(f"../../{content}/{module}{sku}/{mtpl_naming}{sku}", f"{module}{sku}", binrange = [LSA_Range, SSA_ALL_Range,RET_Range], basenumrange = (12500,12749), defaultthermalbin = (90972055,90976055), defaultresetbin = (90201955,90601955))
	Import(f'{module}{sku}'".usrv")
	Import(f'{module}{sku}_Specs'".usrv")
	Import(f'{module}{sku}_Timing'".tcg")
	Import(f'{module}{sku}_Levels'".tcg")

	#################################################################
	#          
	#                       INIT SUBFLOW                        
	#
	#################################################################
	sub_flow = "INIT"                       # Define the name of your flow
	freq_corner = ""						# Define the test frequency
 
	# Input
	# Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
	#UNCOMMENT LATER#content_list = {	"matchmode_enable"	: {"bypass":-1, "kill":1,'template':'PrimePatConfigTestMethod','jsonfile':f"./Modules/{module}/InputFiles/fun_hub.patConfigSetPoint.json",'setpoint':'ENABLE_MATCHMODE'}, 
	#UNCOMMENT LATER#					"matchmode_disable"	: {"bypass":-1, "kill":1,'template':'PrimePatConfigTestMethod','jsonfile':'fullpathjsonfile','setpoint':'setpointname'},
	#UNCOMMENT LATER#					"pinmap_recovery"	: {"bypass":-1, "kill":1,'template':'RunCallback','callback':'LoadPinMapFile','param':'--decoder FailDataDecoder --file fullpathjsonfile'},
	#UNCOMMENT LATER#					"dummyscreentest"	: {"bypass":-1, "kill":1,'template':'ScreenTC','screentestset':'givemetoken','screentestfile':'fullpathscreentestfile'}}
	#UNCOMMENT LATER#
	## DedcLoadConfigTC instance is created at the start of the flow by default to enable DEDC
	pinmap = get_DedcLoadConfigTC_test()
	apex = get_DedcLoadConfigTC_test1()
	#RWA  = get_PrimePatConfigTestMethod_test()
	
	#tests = get_test_list(content_list,sub_flow,freq_corner)
	Flow(module+sku+"_"+sub_flow, pinmap,apex) # ,tests

	###################################################################
	###          
	###                       DEDC SUBFLOW                        
	###
	###################################################################
	##sub_flow = "DEDC"                       # Define the name of your flow
	##freq_corner = ""						# Define the test frequency
 	##
	### Input
	### Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
	##content_list = {	'shmoo_for_dedc'	: {"bypass":1, "kill":0,'template':'DDGShmooTC','Patlist':'funsoc_csnf3_hift_list',
	##										   #'XAxisType':'fillout','XAxisParam':'fillout','XAxisRange':'fillout',		# default, cfg overrides if needed
	##										   #'YAxisType':'fillout','YAxisParam':'fillout','YAxisRange':'fillout',		# default, cfg overrides if needed
	##										   #'SetPointsPreInstance':'fillout','SetPointsPostInstance':'fillout',			# default, cfg overrides if needed
	##										   #'VoltageConverter':'fillout','MaskPins':'fillout',							# default, cfg overrides if needed
	##									  }
	##				}
	##
	##tests = get_test_list(content_list,sub_flow,freq_corner)
	##Flow(module+sku+"_"+sub_flow, tests)
 
	#################################################################
	#          
	#                       BEGINHUBNOM SUBFLOW                       
	#
	#################################################################
	sub_flow = "BEGINCPUNOM"                   # Define the name of your flow
	freq_corner = "F3"						# Define the test frequency
	IPCluster = "ALL"
	arraytype = "ALL"
	testtype = "KS"

	# Input
	# Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
	content_list = {	"COMBINED"		: {"bypass":1,"kill":1,'template':'VminTC_pt','supply':POR_VoltageTarget,'flowmatrix':'AT_F3_FREQ', 'voltageoverride':f'{POR_VoltageTarget}'+":0.9", 'plist': [IPCluster,arraytype,testtype], 'level' : 'nom'},
	                    "SSA"           : {"bypass":1,"kill":1,'template':'VminTC_pt','supply':POR_VoltageTarget,'flowmatrix':'AT_F3_FREQ', 'voltageoverride':f'{POR_VoltageTarget}'+":0.9", 'plist': ["directdsdb","ssa",testtype], 'level' : 'nom'}}
					

	tests = get_test_list(content_list,sub_flow,freq_corner)
	
	content_list_shmoo = {	'shmoo_for_dedc'	: {"bypass":-1, "kill":0,'template':'DDGShmooTC','Patlist':'IPC::arr_cdie_begincpunom_pbist_atom_all_all_vatom_ks_all_f3_hptp800_class_list'
											   #'XAxisType':'fillout','XAxisParam':'fillout','XAxisRange':'fillout',		# default, cfg overrides if needed
											   #'YAxisType':'fillout','YAxisParam':'fillout','YAxisRange':'fillout',		# default, cfg overrides if needed
											   #'SetPointsPreInstance':'fillout','SetPointsPostInstance':'fillout',			# default, cfg overrides if needed
											   #'VoltageConverter':'fillout','MaskPins':'fillout',							# default, cfg overrides if needed
										  }
					}
	
	tests.extend(get_test_list(content_list_shmoo,sub_flow,freq_corner))

	resources_file = Spec('GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "/Modules/ARR/ARR_ATOM_CXX/InputFiles/NVL_ArrayMap_ATOM.json"') #"~HDMT_TPL_DIR/Modules/ARR_COMMON_CXX/InputFiles/ARL_ArrayMap_resource.json",
	repairtofuse_file = Spec('GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "/Modules/ARR/ARR_ATOM_CXX/InputFiles/NVL_Repair_to_fuse_ATOM.json"') #"~HDMT_TPL_DIR/Modules/ARR_COMMON_CXX/InputFiles/ARL_Repair_to_fuse.json",
	arraydef_file = Spec('GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "/Modules/ARR/ARR_ATOM_CXX/InputFiles/NVL_ArrayDefinition_ATOM.json"')

	def create_capturevec_test(input_dict):
		preplist = get_preplist(input_dict["corner"], input_dict["array_type"])
		sample_test=PrimeCaptureVectorsTestMethod(name = f"{input_dict['array_type']}_ATOM_CAPPKTS_E_"+sub_flow+f"_TITO_VCCIA_{input_dict['corner']}_X"+f"_{input_dict['testname']}",
											BypassPort=Spec(input_dict["Bypass"]),
											Pins = "CPU_TDO",
											FunctionalDataToUse = "CTV",
											Timeout = Spec("400"),
											ReverseVectorOutput = "True",
											Mode = "PerPin",
											KeyForSharedStorage = (input_dict["key"]),
											LevelsTc = level,
											Patlist = (input_dict['plist']),
											#PreInstance = "ExecutePatConfigSetPoint("+Specs.MCdrv_F1AT_F1CO_F1CC+","+Specs.MCarrAtom_F1AT_x_Global+")",
											PrePlist = preplist,
											TimingsTc = timing,
											_fitem=Fitem("SAME",
														edc=True,
														r0 = pFail(ret="1"),
														r1 = pPass(goto="NEXT"),
														r2 = pPass(ret="1"))#,
														#rm1 = pFail(setbin=BIN98_DICT['ALL'], ret=-1), 
														#rm2 = pFail(setbin=BIN99_DICT['ALL'], ret=-2))											
											)
		return sample_test

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
			target_array = target_array_map.get(input_dict["testname"], input_dict["testname"].lower())
	
			sample_test=NVLRasterExtension(name = f"{input_dict['array_type']}_ATOM_REPAIR_E_"+sub_flow+f"_TITO_VCCIA_{input_dict['corner']}_X"+f"_{input_dict['testname']}",
												BypassPort=Spec(input_dict["Bypass"]),
												ArrayFile = arraydef_file,
												ResourceFile = resources_file,
												LogLevel = "Disabled",
												InputStorageKey = (input_dict["key"]),
												TargetArray = target_array,
												OperationMode = "Repair",
												MaxDefectCount = 5000,
												DecoderMatchLabel = "module0",
												DataLog = "TFile",
												_fitem=Fitem("SAME", 
															edc=True,
															r0 = pFail(ret="1"),
															r1 = pPass(ret="1"),
															r2 = pPass(goto="NEXT"),
															r3 = pPass(ret="1"),
															r4 = pPass(ret="1"),
															r5 = pFail(ret="1"))#,
															#rm1 = pFail(setbin=BIN98_DICT['ALL'], ret=-1), 
															#rm2 = pFail(setbin=BIN99_DICT['ALL'], ret=-2))
												)
			return sample_test
	
	def create_repairtofuse(input_dict):
			sample_test=PrimeRepairToFuseTestMethod(name = f"{input_dict['array_type']}_ATOM_REPAIR_E_"+sub_flow+f"_TITO_VCCIA_{input_dict['corner']}_X"+f"_{input_dict['testname']}_REP2FUSE",
												BypassPort =-1,
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
	
	def create_PATMOD_test(input_dict):
			sample_test=PrimePatConfigTestMethod(name = f"{input_dict['array_type']}_ATOM_PATMOD_E_"+sub_flow+f"_TITO_VCCIA_{input_dict['corner']}_X"+f"_{input_dict['testname']}",
										ConfigurationFile = Spec('GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "/Modules/ARR/ARR_ATOM_CXX/InputFiles/AtomArray.PatConfigSetpoints.json"'),
										SetPoint = f"{input_dict['setpoint']}",
										#RegEx = Spec("FUSEVars.CDIE_Fuse_Pattern_Regex_Ratio1+\"_MCAarr*\""),
										BypassPort=(input_dict["Bypass"]),
										)
			return sample_test
	
	def create_hry_test(input_dict):
			preplist = get_preplist(input_dict["corner"], input_dict["array_type"])
			sample_test=PrimeArrayHryTestMethod(name = f"{input_dict['array_type']}_ATOM_HRY_E_"+sub_flow+f"_TITO_VCCIA_{input_dict['corner']}_X"+f"_{input_dict['testname']}",
												BypassPort=(input_dict["Bypass"]),
												LevelsTc = level,
												Patlist = (input_dict['plist']),
												SetPointsPlistParamName = "Patlist",
												##SetPointsPreInstance = get_setpoints_preinstance(freq_corner,"TITO"),
												TimingsTc ="CPU_IP_BASE::cpu_fun_timing_mts100_tstprtclk50_tck100",
												ConfigFile = Spec('GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "/Modules/ARR/ARR_ATOM_CXX/InputFiles/arr_cdie_x_pbist_atom_direct_all_vatom_hry_all_f1_tito_class_list.xml"'),							
												#ConfigFile = Spec('GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "/Modules/ARR_ATOM_HXX/InputFiles/'+f"{input_dict['xml']}"+'\"'),							
												PrePlist = preplist,
												#PrePlist = "VoltageConverter(--overrides=VCCATOM0_HC:VMIN_ATOM_CACHE_L2_VMINREP)";
												)
			return sample_test

	def get_ScreenTC(sub_flow, OnSwitch, file_path, screen_data, comment):
    
			return ScreenTC(
            name = f"ALL_ATOM_SCREENTC_E_{sub_flow}_X_X_X_X_{comment}",
            BypassPort = OnSwitch,
	        ScreenTestsFile = file_path,
            ScreenTestSet = screen_data)
	
	def create_VFDM(sub_flow, OnSwitch, comment):
			sample_test=PrimeVirtualFuseExportToSharedStorageTestMethod(name = f"ALL_X_SCREEN_K_{sub_flow}_X_X_X_X_ATOM_{comment}",
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

	def create_PatConfigTM(sub_flow, OnSwitch, setupfile, vfdm, pat_regex, comment):

			return PrimePatConfigTestMethod(
            name = f"ALL_ATOM_PATCONFIG_K_{sub_flow}_X_X_X_X_{comment}",
            BypassPort = OnSwitch,
	        ConfigurationFile = setupfile,
            SetPoint = vfdm,
            RegEx = pat_regex)

	######################
	# VMIN REPAIR
	######################
	
	####L2_DATA
	L2_DATA_MIN_Test_Dict = {
			"L2_DATA_CAPTURE_MIN" : {"testname" : "L2_DATA" , "corner":"MIN" , "Bypass" :f'{module}{sku}'".L2_DATA_ALL_SCBD_0_0_0_0", "array_type" : "SSA", "plist" : "arr_cdie_x_pbist_atom_direct_ssa_vatom_raster_l2_data_f1_m0_tito_class_list","key":"L2DATAMINM0"},
			"L2_DATA_RASTER_EXT_MIN" : {"testname" : "L2_DATA" , "corner":"MIN" , "Bypass" : f'{module}{sku}'".L2_DATA_ALL_SCBD_0_0_0_0", "array_type" : "SSA","key":"L2DATAMINM0"},
			"L2_DATA_REPAIR2FUSE_MIN" : {"testname" : "L2_DATA" , "corner":"MIN" , "Bypass" : f'{module}{sku}'".L2_DATA_ALL_SCBD_0_0_0_0", "array_type" : "SSA"}
			}
		
	L2_DATA_CAP_MIN = create_capturevec_test(L2_DATA_MIN_Test_Dict["L2_DATA_CAPTURE_MIN"])
	L2_DATA_RASTER_MIN = create_raster_ext(L2_DATA_MIN_Test_Dict["L2_DATA_RASTER_EXT_MIN"])
	L2_DATA_REP2FUSE_MIN = create_repairtofuse(L2_DATA_MIN_Test_Dict["L2_DATA_REPAIR2FUSE_MIN"])		
		
	L2_DATA_MIN_COMPOSITE = Flow("L2_DATA_MIN", L2_DATA_CAP_MIN, L2_DATA_RASTER_MIN,L2_DATA_REP2FUSE_MIN )
	
	#### L2_TAG #####
	L2_TAG_MIN_Test_Dict = {
			"L2_TAG_CAPTURE_MIN" : {"testname" : "L2_TAG" , "corner":"MIN" , "Bypass" :f'{module}{sku}'".L2_TAG_ALL_SCBD_0_0_0_0", "array_type" : "SSA", "plist" : "arr_cdie_x_pbist_atom_direct_ssa_vatom_raster_l2_tag_f1_m0_tito_class_list","key":"L2TAGMINM0"},
			"L2_TAG_RASTER_EXT_MIN" : {"testname" : "L2_TAG" , "corner":"MIN" , "Bypass" :f'{module}{sku}'".L2_TAG_ALL_SCBD_0_0_0_0", "array_type" : "SSA","key":"L2TAGMINM0"},
			"L2_TAG_REPAIR2FUSE_MIN" : {"testname" : "L2_TAG" , "corner":"MIN" , "Bypass" : f'{module}{sku}'".L2_TAG_ALL_SCBD_0_0_0_0", "array_type" : "SSA"}
			}
		
	L2_TAG_CAP_MIN = create_capturevec_test(L2_TAG_MIN_Test_Dict["L2_TAG_CAPTURE_MIN"])
	L2_TAG_RASTER_MIN = create_raster_ext(L2_TAG_MIN_Test_Dict["L2_TAG_RASTER_EXT_MIN"])
	L2_TAG_REP2FUSE_MIN = create_repairtofuse(L2_TAG_MIN_Test_Dict["L2_TAG_REPAIR2FUSE_MIN"])		
		
	L2_TAG_MIN_COMPOSITE = Flow("L2_TAG_MIN", L2_TAG_CAP_MIN, L2_TAG_RASTER_MIN,L2_TAG_REP2FUSE_MIN)
	
	#### L2_STATE #####
	L2_STATE_MIN_Test_Dict = {
			"L2_STATE_CAPTURE_MIN" : {"testname" : "L2_STATE" , "corner":"MIN" , "Bypass" :f'{module}{sku}'".L2_STATE_ALL_SCBD_0_0_0_0", "array_type" : "LSA", "plist" : "arr_cdie_x_pbist_atom_direct_lsa_vatom_raster_l2_state_f1_m0_tito_class_list","key":"L2STATEMINM0"},
			"L2_STATE_RASTER_EXT_MIN" : {"testname" : "L2_STATE" , "corner":"MIN" , "Bypass" :f'{module}{sku}'".L2_STATE_ALL_SCBD_0_0_0_0", "array_type" : "LSA","key":"L2STATEMINM0"},
			"L2_STATE_REPAIR2FUSE_MIN" : {"testname" : "L2_STATE" , "corner":"MIN" , "Bypass" :f'{module}{sku}'".L2_STATE_ALL_SCBD_0_0_0_0", "array_type" : "LSA"}
			}
		
	L2_STATE_CAP_MIN = create_capturevec_test(L2_STATE_MIN_Test_Dict["L2_STATE_CAPTURE_MIN"])
	L2_STATE_RASTER_MIN = create_raster_ext(L2_STATE_MIN_Test_Dict["L2_STATE_RASTER_EXT_MIN"])
	L2_STATE_REP2FUSE_MIN = create_repairtofuse(L2_STATE_MIN_Test_Dict["L2_STATE_REPAIR2FUSE_MIN"])		
		
	L2_STATE_MIN_COMPOSITE = Flow("L2_STATE_MIN", L2_STATE_CAP_MIN,L2_STATE_RASTER_MIN, L2_STATE_REP2FUSE_MIN)
	
	#### L2_C6 #####
	L2_C6_MIN_Test_Dict = {
			"L2_C6_CAPTURE_MIN" : {"testname" : "L2_C6" , "corner":"MIN" , "Bypass" :f'{module}{sku}'".L2_C6S_ALL_SCBD_0_0_0_0", "array_type" : "LSA", "plist" : "arr_cdie_x_pbist_atom_direct_lsa_vatom_raster_l2_c6s_f1_m0_tito_class_list","key":"L2C6MINM0"},
			"L2_C6_RASTER_EXT_MIN" : {"testname" : "L2_C6" , "corner":"MIN" , "Bypass" :f'{module}{sku}'".L2_C6S_ALL_SCBD_0_0_0_0", "array_type" : "LSA","key":"L2C6MINM0"},
			"L2_C6_REPAIR2FUSE_MIN" : {"testname" : "L2_C6" , "corner":"MIN" , "Bypass" : f'{module}{sku}'".L2_C6S_ALL_SCBD_0_0_0_0", "array_type" : "LSA"}
			}
		
	L2_C6_CAP_MIN = create_capturevec_test(L2_C6_MIN_Test_Dict["L2_C6_CAPTURE_MIN"])
	L2_C6_RASTER_MIN = create_raster_ext(L2_C6_MIN_Test_Dict["L2_C6_RASTER_EXT_MIN"])
	L2_C6_REP2FUSE_MIN = create_repairtofuse(L2_C6_MIN_Test_Dict["L2_C6_REPAIR2FUSE_MIN"])		
		
	L2_C6_MIN_COMPOSITE = Flow("L2_C6_MIN", L2_C6_CAP_MIN, L2_C6_RASTER_MIN,L2_C6_REP2FUSE_MIN )
	
	#### L2_LRU #####
	L2_LRU_MIN_Test_Dict = {
			"L2_LRU_CAPTURE_MIN" : {"testname" : "L2_LRU" , "corner":"MIN" , "Bypass" : f'{module}{sku}'".L2_LRU_ALL_SCBD_0_0_0_0", "array_type" : "LSA", "plist" : "arr_cdie_x_pbist_atom_direct_lsa_vatom_raster_l2_lru_f1_m0_tito_class_list","key":"L2LRUMINM0"},
			"L2_LRU_RASTER_EXT_MIN" : {"testname" : "L2_LRU" , "corner":"MIN" , "Bypass" : f'{module}{sku}'".L2_LRU_ALL_SCBD_0_0_0_0", "array_type" : "LSA","key":"L2LRUMINM0"},
			"L2_LRU_REPAIR2FUSE_MIN" : {"testname" : "L2_LRU" , "corner":"MIN" , "Bypass" : f'{module}{sku}'".L2_LRU_ALL_SCBD_0_0_0_0", "array_type" : "LSA"}
			}
		
	L2_LRU_CAP_MIN = create_capturevec_test(L2_LRU_MIN_Test_Dict["L2_LRU_CAPTURE_MIN"])
	L2_LRU_RASTER_MIN = create_raster_ext(L2_LRU_MIN_Test_Dict["L2_LRU_RASTER_EXT_MIN"])
	L2_LRU_REP2FUSE_MIN = create_repairtofuse(L2_LRU_MIN_Test_Dict["L2_LRU_REPAIR2FUSE_MIN"])		
		
	L2_LRU_MIN_COMPOSITE = Flow("L2_LRU_MIN", L2_LRU_CAP_MIN, L2_LRU_RASTER_MIN,L2_LRU_REP2FUSE_MIN)
	
	L2_MIN_Test_Dict = {
    "DIRECT_PRE_HRY_MIN" : {"testname" : "PRE", "array_type" : "XSA" , "corner":"MIN" , "Bypass" : 1, "plist" : "arr_pbist_tito_hry_atom_class_list","gsds":"VMIN_ATOM_CACHE_L2_VMINREP", "xml":"arr_cdie_x_pbist_atom_direct_all_vatom_hry_all_f1_tito_class_list.xml"},    
    "DIRECT_POST_HRY_MIN" : {"testname" : "POST", "array_type" : "XSA" , "corner":"MIN" , "Bypass" : 1, "plist" : "arr_pbist_tito_hry_atom_class_list","gsds":"VMIN_ATOM_CACHE_L2_VMINREP", "xml":"arr_cdie_x_pbist_atom_direct_all_vatom_hry_all_f1_tito_class_list.xml"},
	"RASTERLOOP_PATCONFIG_MIN" : {"testname" : "VMINRASTERLOOP" , "corner":"MIN" , "array_type" : "XSA", "Bypass" : 1,"setpoint":"VminRasterLoop"}
	#"SCREENTEST_SETLOCALVMIN" : {"OnSwitch": 1, "file_path": Spec('GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "/Modules/ARR_ATOM/InputFiles/arr_atomrr_repair.txt"'),"screen_data": "SET_LOCALVMINL2Repair","comment":"SETLOCAL_L2_VMINREP"}
    }

	VMIN_RASTER_LOOP = create_PATMOD_test(L2_MIN_Test_Dict["RASTERLOOP_PATCONFIG_MIN"])
	DIRECT_PRE_HRY_MIN = create_hry_test(L2_MIN_Test_Dict["DIRECT_PRE_HRY_MIN"])
	SCREENTEST_SETLOCALVMIN= get_ScreenTC( sub_flow, 1, Spec('GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "/Modules/ARR/ARR_ATOM_CXX/InputFiles/arr_atomrr_repair.txt"'),"SET_LOCALVMINL2Repair","SETLOCAL_L2_VMINREP")
	SCREENTEST_SETL2RR_VMIN= get_ScreenTC( sub_flow, 1, Spec('GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "/Modules/ARR/ARR_ATOM_CXX/InputFiles/ScreenTest_L2.txt"'),"SetL2_RasterRepair","SETL2RR_VMINREP")
	TEST_VFDM1= create_VFDM(sub_flow, 1, "MINREPAIR_L2ALL")
	TEST_PATCONFIGTM1 = create_PatConfigTM (sub_flow, 1, Spec('GetEnvironmentVariable("FUSE_ROOT_DIR_CPU_INT") + "/CSP/array_repair_perunit.PatConfigSetpoints.json"'),"CPU0_APPLY_VFDM","[gdx].*_longreset_fuseoverride.*_MCAarr.*","MINREPAIR_L2ALL")
	DIRECT_POST_HRY_MIN = create_hry_test(L2_MIN_Test_Dict["DIRECT_POST_HRY_MIN"])
	SCREENTEST_REVERT_VMINREP= get_ScreenTC( sub_flow, 1, Spec('GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "/Modules/ARR/ARR_ATOM_CXX/InputFiles/arr_atomrr_repair.txt"'),"REVERT_VMINL2Repair","REVERT_L2_VMINREP")
	TEST_PATCONFIGTM1_REVERT = create_PatConfigTM (sub_flow, 1, Spec('GetEnvironmentVariable("FUSE_ROOT_DIR_CPU_INT") + "/CSP/array_repair_perunit.PatConfigSetpoints.json"'),"CPU0_APPLY_VFDM","[gdx].*_longreset_fuseoverride.*_MCAarr.*","REVERT_REPTOFUSE")
	TEST_VFDM1_REVERT= create_VFDM(sub_flow, 1, "L2ALL_REVERT")


	DIRECT_MIN_COMPOSITE = Flow("L2_ALL_MIN_REP",
								Fitem("SAME",VMIN_RASTER_LOOP,edc=True, r0 = pFail(setbin=SSABin,goto = "NEXT"), r1 = pPass(goto = "NEXT"), r2 = pFail(setbin=SSABin,goto = "NEXT")),#, rm1 = pFail(setbin=BIN98_DICT['LSA'], ret=-1), rm2 = pFail(setbin=BIN99_DICT['LSA'], ret=-2)
								Fitem("SAME",SCREENTEST_SETLOCALVMIN,edc=True, r0 = pFail(setbin=SSABin,goto = "NEXT"), r1 = pPass(goto = "NEXT"), r2 = pFail(setbin=SSABin,goto = "NEXT")),
								Fitem("SAME",DIRECT_PRE_HRY_MIN,edc=True, r0 = pFail(setbin=SSABin,goto = "NEXT"), r1 = pPass(ret = "1"), r2 = pFail(setbin=SSABin,goto = "NEXT"), r3 = pFail(setbin=SSABin,ret = "1")), #, rm1 = pFail(setbin=BIN98_DICT['LSA'], ret=-1), rm2 = pFail(setbin=BIN99_DICT['LSA'], ret=-2)
								Fitem("SAME",SCREENTEST_SETL2RR_VMIN,edc=True, r0 = pFail(setbin=SSABin,goto = "NEXT"), r1 = pPass(goto = "NEXT"), r2 = pFail(setbin=SSABin,goto = "NEXT")),
								Fitem("SAME",L2_DATA_MIN_COMPOSITE, r0 = pFail(goto = "NEXT")),
								Fitem("SAME",L2_TAG_MIN_COMPOSITE, r0 = pFail(goto = "NEXT")),
								Fitem("SAME",L2_STATE_MIN_COMPOSITE, r0 = pFail(goto = "NEXT")),
								Fitem("SAME",L2_C6_MIN_COMPOSITE, r0 = pFail(goto = "NEXT")),
								Fitem("SAME",L2_LRU_MIN_COMPOSITE, r0 = pFail(goto = "NEXT")),
								Fitem("SAME",TEST_VFDM1,edc=True, r0 = pFail(setbin=SSABin,goto = "NEXT"), r1 = pPass(goto = "NEXT"), r2 = pPass(setbin=SSABin,goto = "NEXT"), r3=pFail(setbin=SSABin,goto = "SCREENTEST_REVERT_VMINREP")),
								#Fitem("SAME",DIRECT_POST_HRY_MIN,edc=True, r0 = pFail(setbin=SSABin,goto = "TEST_PATCONFIGTM1"), r1 = pPass(ret = "1"), r2 = pPass(setbin=SSABin,ret = "1"), r3 = pFail(setbin=SSABin,ret = "1")),
								Fitem("SAME",TEST_PATCONFIGTM1,edc=True, r0 = pFail(setbin=SSABin,goto = "SCREENTEST_REVERT_VMINREP"), r1 = pPass(goto = "DIRECT_POST_HRY_MIN"),r2 = pPass(ret="1")),
								Fitem("SAME",SCREENTEST_REVERT_VMINREP,edc=True, r0 = pFail(setbin=SSABin,goto = "NEXT"), r1 = pPass(goto = "NEXT"),r2 = pPass(goto = "NEXT")),
								Fitem("SAME",TEST_PATCONFIGTM1_REVERT,edc=True, r0 = pFail(setbin=SSABin,ret = "0"), r1 = pPass(goto = "NEXT")),
								Fitem("SAME",TEST_VFDM1_REVERT,edc=True, r0 = pFail(setbin=SSABin,ret = "0"), r1 = pPass(ret = "1"), r2 = pPass(setbin=SSABin,ret = "1")),
								Fitem("SAME",DIRECT_POST_HRY_MIN,edc=True, r0 = pFail(setbin=SSABin,goto = "TEST_PATCONFIGTM1"), r1 = pPass(ret = "1"), r2 = pPass(setbin=SSABin,ret = "1"), r3 = pFail(setbin=SSABin,ret = "1"))
								)
	
	MINREP_COMPOSITE = Flow("MIN_REPAIR_"+sub_flow,
								Fitem("SAME",DIRECT_MIN_COMPOSITE, r0 = pFail(ret = "1")))
	

	Flow(module+sku+"_"+sub_flow, Fitem("SAME", tuple(tests)[0], edc = False if (content_list["COMBINED"]["kill"]==1) else True,
				r0 = pFail(setbin=LSABin, ret=0) if (content_list["COMBINED"]["kill"]==1) else pFail(setbin=AUTO),
				r1 = pPass(ret = 1),
				r2 = pFail(setbin=LSABin,  ret=0) if (content_list["COMBINED"]["kill"]==1) else pFail(setbin=AUTO),
				r3 = pPass(ret = 1),
				r4 = pFail(setbin=LSA_Thermal, ret=0) if (content_list["COMBINED"]["kill"]==1) else pFail(setbin=AUTO),
				r5 = pFail(setbin=LSA_Reset, ret=0) if (content_list["COMBINED"]["kill"]==1) else pFail(setbin=AUTO)),
				Fitem("SAME", tuple(tests)[1], edc = False if (content_list["SSA"]["kill"]==1) else True,
				r0 = pFail(setbin=SSABin, ret=0) if (content_list["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r1 = pPass(ret = 0),
				r2 = pFail(setbin=SSABin, ret=0) if (content_list["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r3 = pFail(setbin=SSABin, ret=0) if (content_list["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r4 = pFail(setbin=SSA_Thermal, ret=0) if (content_list["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r5 = pFail(setbin=SSA_Reset, ret=0) if (content_list["SSA"]["kill"]==1) else pFail(setbin=AUTO)),				
				Fitem("SAME", tuple(tests)[-1], edc = False if (content_list_shmoo["shmoo_for_dedc"]["kill"]==1) else True,
				r0 = pFail(ret = 1),
				r1 = pPass(ret = 1)#,
				#r2 = pFail(ret=1) if (content_list_shmoo["shmoo_for_dedc"]["kill"]==1) else pFail(ret=1),
				#r3 = pFail(ret=1) if (content_list_shmoo["shmoo_for_dedc"]["kill"]==1) else pFail(ret=1)
				),
				Fitem("SAME",MINREP_COMPOSITE, r0 = pFail(ret = "1")))





	###################################################################
	###          
	###                       VMAXSN SUBFLOW                       
	###
	###################################################################
	##sub_flow = "VMAXSN"                   # Define the name of your flow
	##freq_corner = "X"						# Define the test frequency
	##IPCluster = "ALL"
	##arraytype = "ALL"
	##testtype = "KS"
	##
	### Input
	### Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
	##content_list = {	"COMBINED"		: {"bypass":1,"kill":1,'template':'ApexTC','supply':'VCCATOM','flowmatrix':'SAAT_F2_FREQ', 'voltageoverride':'--overrides VCCATOM_HC:1.3', 'plist': [IPCluster,arraytype,testtype]},
	##                     "SSA"          : {"bypass":1,"kill":1,'template':'ApexTC','supply':'VCCATOM','flowmatrix':'SAAT_F2_FREQ', 'voltageoverride':'--overrides VCCATOM_HC:1.3', 'plist': [IPCluster,arraytype,testtype]}}
	##
	##tests = get_test_list(content_list,sub_flow,freq_corner)
	##print(f'{tests}')
	##Flow(module+sku+"_"+sub_flow, Fitem("SAME", tuple(tests)[0], # edc = False if (content_list["ALL"]["kill"]==1) else True,
	##			r0 = pFail(setbin=LSABin, goto = tuple(tests)[1].name) if (content_list["ALL"]["kill"]==1) else pFail(setbin=AUTO),
	##			r1 = pPass(ret = 1),
	##			r2 = pFail(setbin=LSABin, goto = tuple(tests)[1].name) if (content_list["ALL"]["kill"]==1) else pFail(setbin=AUTO),
	##			r3 = pFail(setbin=LSABin, goto = tuple(tests)[1].name) if (content_list["ALL"]["kill"]==1) else pFail(setbin=AUTO),
	##			r4 = pFail(setbin=LSA_Thermal, goto = tuple(tests)[1].name) if (content_list["ALL"]["kill"]==1) else pFail(setbin=AUTO),
	##			r5 = pFail(setbin=SSA_Reset, goto = tuple(tests)[1].name) if (content_list["ALL"]["kill"]==1) else pFail(setbin=AUTO)),
	##			 Fitem("SAME", tuple(tests)[1],
	##			r0 = pFail(setbin=SSABin, ret=0) if (content_list["ALL"]["kill"]==1) else pFail(setbin=AUTO),
	##			r1 = pPass(ret = 0),
	##			r2 = pFail(setbin=SSABin, ret=0) if (content_list["ALL"]["kill"]==1) else pFail(setbin=AUTO),
	##			r3 = pFail(setbin=SSABin, ret=0) if (content_list["ALL"]["kill"]==1) else pFail(setbin=AUTO),
	##			r4 = pFail(setbin=SSA_Thermal, ret=0) if (content_list["ALL"]["kill"]==1) else pFail(setbin=AUTO),
	##			r5 = pFail(setbin=SSA_Reset, ret=0) if (content_list["ALL"]["kill"]==1) else pFail(setbin=AUTO)))
	
	#################################################################
	#          
	#                    HERMES F1XSN SUBFLOW                       
	#
	#################################################################
	sub_flow = "F1XAT"						# Define the name of your flow
	freq_corner = "F1"						# Define the test frequency
	IPCluster = "ALL"
	arraytype = "ALL"
	testtype = "REDUCEDKS"

	# Input
	# Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
	content_list[SKU] = {	"COMBINED"	: {"bypass":1, "kill":1,'template':'VminTC_MTT_singleVmin','supply':POR_VoltageTarget,'flowmatrix':'AT_F1_FREQ','powermux':POR_Pmux,'plist': [IPCluster,arraytype,testtype], 'hermes' : '1'},
	                        "SSA"       : {"bypass":1, "kill":1,'template':'VminTC_MTT_singleVmin','supply':POR_VoltageTarget,'flowmatrix':'AT_F1_FREQ','powermux':POR_Pmux,'plist': ["directdsdb","ssa",testtype], 'hermes' : '0'},
							"SSA_l2tag": {"bypass":1, "kill":1,'template':'VminTC_MTT_singleVmin','supply':POR_VoltageTarget,'flowmatrix':'AT_F1_FREQ','powermux':POR_Pmux,'plist': ["directdsdb","ssa",testtype], 'hermes' : '0'}}
	#content_list['SX'] = {	"L2dragon"	: {"bypass":1, "kill":1,'template':'VminTC_srh','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F1_FREQ', 'powermux':POR_Pmux}}
	#content_list['SK'] = {	"L2dragon"	: {"bypass":1, "kill":1,'template':'VminTC_srh','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F1_FREQ'}}
	
	tests = get_test_list(content_list[SKU],sub_flow,freq_corner)
	Flow(module+sku+"_"+sub_flow, Fitem("SAME", tuple(tests)[0], # edc = False if (content_list[SKU]["COMBINED"]["kill"]==1) else True,
				r0 = pFail(setbin=LSABin, ret = 0) if (content_list[SKU]["COMBINED"]["kill"]==1) else pFail(setbin=AUTO),
				r1 = pPass(ret = 1),
				r2 = pFail(setbin=LSABin, ret = 0) if (content_list[SKU]["COMBINED"]["kill"]==1) else pFail(setbin=AUTO),
				r3 = pPass(ret = 1),
				r4 = pFail(setbin=LSA_Thermal, ret = 0) if (content_list[SKU]["COMBINED"]["kill"]==1) else pFail(setbin=AUTO),
				r5 = pFail(setbin=LSA_Reset, ret = 0) if (content_list[SKU]["COMBINED"]["kill"]==1) else pFail(setbin=AUTO)),
				 Fitem("SAME", tuple(tests)[1],
				r0 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r1 = pPass(ret = 0),
				r2 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r3 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r4 = pFail(setbin=SSA_Thermal, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r5 = pFail(setbin=SSA_Reset, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO)),
				Fitem("SAME", tuple(tests)[2],
				r0 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r1 = pPass(ret = 1),
				r2 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA_l2tag"]["kill"]==1) else pFail(setbin=AUTO),
				r3 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA_l2tag"]["kill"]==1) else pFail(setbin=AUTO),
				r4 = pFail(setbin=SSA_Thermal, ret=0) if (content_list[SKU]["SSA_l2tag"]["kill"]==1) else pFail(setbin=AUTO),
				r5 = pFail(setbin=SSA_Reset, ret=0) if (content_list[SKU]["SSA_l2tag"]["kill"]==1) else pFail(setbin=AUTO)))

	#################################################################
	#          
	#                    HERMES F2XSN SUBFLOW                       
	#
	#################################################################
	sub_flow = "F2XAT"						# Define the name of your flow
	freq_corner = "F2"						# Define the test frequency
	IPCluster = "ALL"
	arraytype = "ALL"
	testtype = "REDUCEDKS"
	
	# Input
	# Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
	content_list[SKU] = {	"COMBINED"	: {"bypass":1, "kill":1,'template':'VminTC_MTT_singleVmin','supply':POR_VoltageTarget,'flowmatrix':'AT_F2_FREQ','powermux':POR_Pmux,'plist': [IPCluster,arraytype,testtype], 'hermes' : '1'},
	                        "SSA"       : {"bypass":1, "kill":1,'template':'VminTC_MTT_singleVmin','supply':POR_VoltageTarget,'flowmatrix':'AT_F2_FREQ','powermux':POR_Pmux,'plist': ["directdsdb","ssa",testtype], 'hermes' : '0'},
							"SSA_l2tag": {"bypass":1, "kill":1,'template':'VminTC_MTT_singleVmin','supply':POR_VoltageTarget,'flowmatrix':'AT_F2_FREQ','powermux':POR_Pmux,'plist': ["directdsdb","ssa",testtype], 'hermes' : '0'}}
	#content_list['SX'] = {	"L2dragon"	: {"bypass":1, "kill":1,'template':'VminTC_srh','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F2_FREQ', 'powermux':POR_Pmux}}
	#content_list['SK'] = {	"L2dragon"	: {"bypass":1, "kill":1,'template':'VminTC_srh','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F2_FREQ'}}
	
	tests = get_test_list(content_list[SKU],sub_flow,freq_corner)
	Flow(module+sku+"_"+sub_flow, Fitem("SAME", tuple(tests)[0], # edc = False if (content_list[SKU]["COMBINED"]["kill"]==1) else True,
				r0 = pFail(setbin=LSABin, ret=0) if (content_list[SKU]["COMBINED"]["kill"]==1) else pFail(setbin=AUTO),
				r1 = pPass(ret = 1),
				r2 = pFail(setbin=LSABin, ret=0) if (content_list[SKU]["COMBINED"]["kill"]==1) else pFail(setbin=AUTO),
				r3 = pPass(ret = 1),
				r4 = pFail(setbin=LSA_Thermal, ret=0) if (content_list[SKU]["COMBINED"]["kill"]==1) else pFail(setbin=AUTO),
				r5 = pFail(setbin=LSA_Reset, ret=0) if (content_list[SKU]["COMBINED"]["kill"]==1) else pFail(setbin=AUTO)),
				 Fitem("SAME", tuple(tests)[1],
				r0 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r1 = pPass(ret = 0),
				r2 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r3 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r4 = pFail(setbin=SSA_Thermal, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r5 = pFail(setbin=SSA_Reset, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO)),
				 Fitem("SAME", tuple(tests)[2],
				r0 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r1 = pPass(ret = 1),
				r2 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA_l2tag"]["kill"]==1) else pFail(setbin=AUTO),
				r3 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA_l2tag"]["kill"]==1) else pFail(setbin=AUTO),
				r4 = pFail(setbin=SSA_Thermal, ret=0) if (content_list[SKU]["SSA_l2tag"]["kill"]==1) else pFail(setbin=AUTO),
				r5 = pFail(setbin=SSA_Reset, ret=0) if (content_list[SKU]["SSA_l2tag"]["kill"]==1) else pFail(setbin=AUTO)))

	#################################################################
	#          
	#                 HERMES F3XSN SUBFLOW                       
	#
	#################################################################
	sub_flow = "F3XAT"						# Define the name of your flow
	freq_corner = "F3"						# Define the test frequency
	IPCluster = "ALL"
	arraytype = "ALL"
	testtype = "REDUCEDKS"

	# Input
	# Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
	content_list[SKU] = {	"COMBINED"	: {"bypass":1, "kill":1,'template':'VminTC_MTT_singleVmin','supply':POR_VoltageTarget,'flowmatrix':'AT_F3_FREQ','powermux':POR_Pmux,'plist': [IPCluster,arraytype,testtype], 'hermes' : '1'},
							"SSA"	    : {"bypass":1, "kill":1,'template':'VminTC_MTT_singleVmin','supply':POR_VoltageTarget,'flowmatrix':'AT_F3_FREQ','powermux':POR_Pmux,'plist': ["directdsdb","ssa",testtype], 'hermes' : '0'}, # ,'voltageoverride':'VCCATOM_HC:SOC^SAN0@F3'
							"SSA_l2tag": {"bypass":1, "kill":1,'template':'VminTC_MTT_singleVmin','supply':POR_VoltageTarget,'flowmatrix':'AT_F3_FREQ','powermux':POR_Pmux,'plist': ["directdsdb","ssa",testtype], 'hermes' : '0'}}
							#content_list['SX'] = {	"L2dragon"	: {"bypass":1, "kill":1,'template':'VminTC_srh','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F3_FREQ', 'powermux':POR_Pmux}}
	#content_list['SK'] = {	"L2dragon"	: {"bypass":1, "kill":1,'template':'VminTC_srh','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F3_FREQ'}}
	
	tests = get_test_list(content_list[SKU],sub_flow,freq_corner)
	Flow(module+sku+"_"+sub_flow, Fitem('SAME', tuple(tests)[0], edc = False if (content_list[SKU]["COMBINED"]["kill"]==1) else True,
				r0 = pFail(setbin=LSABin, ret=0) if (content_list[SKU]["COMBINED"]["kill"]==1) else pFail(setbin=AUTO),
				r1 = pPass(ret = 1),
				r2 = pFail(setbin=LSABin, ret=0) if (content_list[SKU]["COMBINED"]["kill"]==1) else pFail(setbin=AUTO),
				r3 = pPass(ret = 1),
				r4 = pFail(setbin=LSA_Thermal, ret=0) if (content_list[SKU]["COMBINED"]["kill"]==1) else pFail(setbin=AUTO),
				r5 = pFail(setbin=LSA_Reset, ret=0) if (content_list[SKU]["COMBINED"]["kill"]==1) else pFail(setbin=AUTO)),
				Fitem("SAME", tuple(tests)[1],
				r0 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r1 = pPass(ret = 0),
				r2 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r3 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r4 = pFail(setbin=SSA_Thermal, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r5 = pFail(setbin=SSA_Reset, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO)),
				Fitem("SAME", tuple(tests)[2],
				r0 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r1 = pPass(ret = 1),
				r2 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA_l2tag"]["kill"]==1) else pFail(setbin=AUTO),
				r3 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA_l2tag"]["kill"]==1) else pFail(setbin=AUTO),
				r4 = pFail(setbin=SSA_Thermal, ret=0) if (content_list[SKU]["SSA_l2tag"]["kill"]==1) else pFail(setbin=AUTO),
				r5 = pFail(setbin=SSA_Reset, ret=0) if (content_list[SKU]["SSA_l2tag"]["kill"]==1) else pFail(setbin=AUTO)))

	#################################################################
	#          
	#                 HERMES F4XSN SUBFLOW                       
	#
	#################################################################
	sub_flow = "F4XAT"						# Define the name of your flow
	freq_corner = "F4"						# Define the test frequency
	IPCluster = "ALL"
	arraytype = "ALL"
	testtype = "REDUCEDKS"

	# Input
	# Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
	content_list[SKU] = {	"COMBINED"	: {"bypass":1, "kill":1,'template':'VminTC_MTT_singleVmin','supply':POR_VoltageTarget,'flowmatrix':'AT_F4_FREQ','powermux':POR_Pmux,'plist': [IPCluster,arraytype,testtype], 'hermes' : '1'},
							"SSA"	    : {"bypass":1, "kill":1,'template':'VminTC_MTT_singleVmin','supply':POR_VoltageTarget,'flowmatrix':'AT_F4_FREQ','powermux':POR_Pmux,'plist': ["directdsdb","ssa",testtype], 'hermes' : '0'}, # ,'voltageoverride':'VCCATOM_HC:SOC^SAN0@F3'
							"SSA_l2tag": {"bypass":1, "kill":1,'template':'VminTC_MTT_singleVmin','supply':POR_VoltageTarget,'flowmatrix':'AT_F4_FREQ','powermux':POR_Pmux,'plist': ["directdsdb","ssa",testtype], 'hermes' : '0'}}
	#content_list['SX'] = {	"L2dragon"	: {"bypass":1, "kill":1,'template':'VminTC_srh','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F3_FREQ', 'powermux':POR_Pmux}}
	#content_list['SK'] = {	"L2dragon"	: {"bypass":1, "kill":1,'template':'VminTC_srh','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F3_FREQ'}}
	
	tests = get_test_list(content_list[SKU],sub_flow,freq_corner)
	Flow(module+sku+"_"+sub_flow, Fitem('SAME', tuple(tests)[0], edc = False if (content_list[SKU]["COMBINED"]["kill"]==1) else True,
				r0 = pFail(setbin=LSABin, ret=0) if (content_list[SKU]["COMBINED"]["kill"]==1) else pFail(setbin=AUTO),
				r1 = pPass(ret = 1),
				r2 = pFail(setbin=LSABin, ret=0) if (content_list[SKU]["COMBINED"]["kill"]==1) else pFail(setbin=AUTO),
				r3 = pPass(ret = 1),
				r4 = pFail(setbin=LSA_Thermal, ret=0) if (content_list[SKU]["COMBINED"]["kill"]==1) else pFail(setbin=AUTO),
				r5 = pFail(setbin=LSA_Reset, ret=0) if (content_list[SKU]["COMBINED"]["kill"]==1) else pFail(setbin=AUTO)),
				Fitem("SAME", tuple(tests)[1],
				r0 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r1 = pPass(ret = 0),
				r2 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r3 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r4 = pFail(setbin=SSA_Thermal, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r5 = pFail(setbin=SSA_Reset, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO)),
				Fitem("SAME", tuple(tests)[2],
				r0 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r1 = pPass(ret = 1),
				r2 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA_l2tag"]["kill"]==1) else pFail(setbin=AUTO),
				r3 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA_l2tag"]["kill"]==1) else pFail(setbin=AUTO),
				r4 = pFail(setbin=SSA_Thermal, ret=0) if (content_list[SKU]["SSA_l2tag"]["kill"]==1) else pFail(setbin=AUTO),
				r5 = pFail(setbin=SSA_Reset, ret=0) if (content_list[SKU]["SSA_l2tag"]["kill"]==1) else pFail(setbin=AUTO)))

		#################################################################
	#          
	#                    HERMES F5XSN SUBFLOW                       
	#
	#################################################################
	sub_flow = "F5XAT"						# Define the name of your flow
	freq_corner = "F5"						# Define the test frequency
	IPCluster = "ALL"
	arraytype = "ALL"
	testtype = "REDUCEDKS"

	# Input
	# Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
	content_list[SKU] = {	"COMBINED"	: {"bypass":1, "kill":1,'template':'VminTC_MTT_singleVmin_F5','supply':POR_VoltageTarget,'flowmatrix':'AT_F5_FREQ','powermux':POR_Pmux,'plist': [IPCluster,arraytype,testtype], 'hermes' : '1'},
	                        "SSA"       : {"bypass":1, "kill":1,'template':'VminTC_MTT_singleVmin_F5','supply':POR_VoltageTarget,'flowmatrix':'AT_F5_FREQ','powermux':POR_Pmux,'plist': ["directdsdb","ssa",testtype], 'hermes' : '0'},
							"SSA_l2tag": {"bypass":1, "kill":1,'template':'VminTC_MTT_singleVmin','supply':POR_VoltageTarget,'flowmatrix':'AT_F5_FREQ','powermux':POR_Pmux,'plist': ["directdsdb","ssa",testtype], 'hermes' : '0'},
							"SSA_APEXTC": {"bypass":1, "kill":0,'template':'ApexTC_fmax','supply':POR_VoltageTarget,'flowmatrix':'AT_F5_FREQ','powermux':POR_Pmux,'plist': ["directdsdb","ssa",testtype], 'hermes' : '0'}}
	#content_list['SX'] = {	"L2dragon"	: {"bypass":1, "kill":1,'template':'VminTC_srh','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F1_FREQ', 'powermux':POR_Pmux}}
	#content_list['SK'] = {	"L2dragon"	: {"bypass":1, "kill":1,'template':'VminTC_srh','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F1_FREQ'}}
	
	tests = get_test_list(content_list[SKU],sub_flow,freq_corner)
	Flow(module+sku+"_"+sub_flow, Fitem("SAME", tuple(tests)[0], # edc = False if (content_list[SKU]["COMBINED"]["kill"]==1) else True,
				r0 = pFail(setbin=LSABin, ret=0) if (content_list[SKU]["COMBINED"]["kill"]==1) else pFail(setbin=AUTO),
				r1 = pPass(ret = 1),
				r2 = pFail(setbin=LSABin, ret=0) if (content_list[SKU]["COMBINED"]["kill"]==1) else pFail(setbin=AUTO),
				r3 = pPass(ret = 1),
				r4 = pFail(setbin=LSA_Thermal, ret=0) if (content_list[SKU]["COMBINED"]["kill"]==1) else pFail(setbin=AUTO),
				r5 = pFail(setbin=LSA_Reset, ret=0) if (content_list[SKU]["COMBINED"]["kill"]==1) else pFail(setbin=AUTO)),
				 Fitem("SAME", tuple(tests)[1],
				r0 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r1 = pPass(ret = 0),
				r2 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r3 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r4 = pFail(setbin=SSA_Thermal, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r5 = pFail(setbin=SSA_Reset, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO)),
				 Fitem("SAME", tuple(tests)[2],
				r0 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r1 = pPass(ret = 1),
				r2 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA_l2tag"]["kill"]==1) else pFail(setbin=AUTO),
				r3 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA_l2tag"]["kill"]==1) else pFail(setbin=AUTO),
				r4 = pFail(setbin=SSA_Thermal, ret=0) if (content_list[SKU]["SSA_l2tag"]["kill"]==1) else pFail(setbin=AUTO),
				r5 = pFail(setbin=SSA_Reset, ret=0) if (content_list[SKU]["SSA_l2tag"]["kill"]==1) else pFail(setbin=AUTO)),
				 Fitem("SAME", tuple(tests)[3],
				r0 = pFail(setbin=SSABin, goto = tuple(tests)[0].name) if (content_list[SKU]["SSA_APEXTC"]["kill"]==0) else pFail(setbin=AUTO),
				r1 = pFail(setbin=SSABin,goto = tuple(tests)[0].name) if (content_list[SKU]["SSA_APEXTC"]["kill"]==0) else pFail(setbin=AUTO),
				r2 = pFail(setbin=SSABin,goto = tuple(tests)[0].name) if (content_list[SKU]["SSA_APEXTC"]["kill"]==0) else pFail(setbin=AUTO),
				r3 = pFail(setbin=SSABin, goto = tuple(tests)[0].name) if (content_list[SKU]["SSA_APEXTC"]["kill"]==0) else pFail(setbin=AUTO),
				r4 = pFail(setbin=SSA_Thermal, goto = tuple(tests)[0].name) if (content_list[SKU]["SSA_APEXTC"]["kill"]==0) else pFail(setbin=AUTO),
				r5 = pFail(setbin=SSA_Reset, goto = tuple(tests)[0].name) if (content_list[SKU]["SSA_APEXTC"]["kill"]==0) else pFail(setbin=AUTO)))

	#################################################################
	#          
	#                    FMINXSN SUBFLOW                       
	#
	#################################################################
	sub_flow = "FMINXAT"						# Define the name of your flow
	freq_corner = "FMIN"						# Define the test frequency
	IPCluster = "ALL"
	arraytype = "ALL"
	testtype = "REDUCEDKS"

	# Input
	# Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
	content_list[SKU] = {	"COMBINED"	: {"bypass":1, "kill":1,'template':'VminTC_vmin','supply':POR_VoltageTarget,'flowmatrix':'AT_FMIN','powermux':POR_Pmux,'plist': [IPCluster,arraytype,testtype]},
	                        "SSA"       : {"bypass":1, "kill":1,'template':'VminTC_vmin','supply':POR_VoltageTarget,'flowmatrix':'AT_FMIN','powermux':POR_Pmux,'plist': ["directdsdb","ssa",testtype]},
							"SSA_l2tag"       : {"bypass":1, "kill":1,'template':'VminTC_vmin','supply':POR_VoltageTarget,'flowmatrix':'AT_FMIN','powermux':POR_Pmux,'plist': ["directdsdb","ssa",testtype]}}
	#content_list['SX'] = {	"L2dragon"	: {"bypass":1, "kill":1,'template':'VminTC_srh','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F1_FREQ', 'powermux':POR_Pmux}}
	#content_list['SK'] = {	"L2dragon"	: {"bypass":1, "kill":1,'template':'VminTC_srh','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F1_FREQ'}}
	
	tests = get_test_list(content_list[SKU],sub_flow,freq_corner)
	Flow(module+sku+"_"+sub_flow, Fitem("SAME", tuple(tests)[0], # edc = False if (content_list[SKU]["COMBINED"]["kill"]==1) else True,
				r0 = pFail(setbin=LSABin, ret=0) if (content_list[SKU]["COMBINED"]["kill"]==1) else pFail(setbin=AUTO),
				r1 = pPass(ret = 1),
				r2 = pFail(setbin=LSABin, ret=0) if (content_list[SKU]["COMBINED"]["kill"]==1) else pFail(setbin=AUTO),
				r3 = pPass(ret = 1),
				r4 = pFail(setbin=LSA_Thermal, ret=0) if (content_list[SKU]["COMBINED"]["kill"]==1) else pFail(setbin=AUTO),
				r5 = pFail(setbin=LSA_Reset, ret=0) if (content_list[SKU]["COMBINED"]["kill"]==1) else pFail(setbin=AUTO)),
				 Fitem("SAME", tuple(tests)[1],
				r0 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r1 = pPass(ret = 0),
				r2 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r3 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r4 = pFail(setbin=SSA_Thermal, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r5 = pFail(setbin=SSA_Reset, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO)),
				 Fitem("SAME", tuple(tests)[2],
				r0 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r1 = pPass(ret = 1),
				r2 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA_l2tag"]["kill"]==1) else pFail(setbin=AUTO),
				r3 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA_l2tag"]["kill"]==1) else pFail(setbin=AUTO),
				r4 = pFail(setbin=SSA_Thermal, ret=0) if (content_list[SKU]["SSA_l2tag"]["kill"]==1) else pFail(setbin=AUTO),
				r5 = pFail(setbin=SSA_Reset, ret=0) if (content_list[SKU]["SSA_l2tag"]["kill"]==1) else pFail(setbin=AUTO)))

	#################################################################
	#          
	#                    VMAXXSN SUBFLOW                       
	#
	#################################################################
	sub_flow = "VMAXXAT"						# Define the name of your flow
	freq_corner = "F1"						# Define the test frequency
	IPCluster = "ALL"
	arraytype = "ALL"
	testtype = "VMAX"

	# Input
	# Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
	content_list[SKU] = {	"COMBINED"	: {"bypass":1, "kill":1,'template':'VminTC_pt','supply':POR_VoltageTarget,'flowmatrix':'AT_F1_FREQ', 'voltageoverride':f'{POR_VoltageTarget}'+":1.1", 'plist': [IPCluster,arraytype,testtype], 'level' : 'nom'},
	                        "SSA"       : {"bypass":1, "kill":1,'template':'VminTC_pt','supply':POR_VoltageTarget,'flowmatrix':'AT_F1_FREQ', 'voltageoverride':f'{POR_VoltageTarget}'+":1.1", 'plist': ["directdsdb","ssa",testtype], 'level' : 'nom'}}
	
	#content_list['SX'] = {	"L2dragon"	: {"bypass":1, "kill":1,'template':'VminTC_srh','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F1_FREQ', 'powermux':POR_Pmux}}
	#content_list['SK'] = {	"L2dragon"	: {"bypass":1, "kill":1,'template':'VminTC_srh','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F1_FREQ'}}
	
	tests = get_test_list(content_list[SKU],sub_flow,freq_corner)

	freq_corner = "F5"						# Define the test frequency
	# Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
	content_list[SKU] = {	"COMBINED"	: {"bypass":1, "kill":1,'template':'VminTC_pt','supply':POR_VoltageTarget,'flowmatrix':'AT_F5_FREQ', 'voltageoverride':f'{POR_VoltageTarget}'+":1.1", 'plist': [IPCluster,arraytype,testtype], 'level' : 'nom'},
	                        "SSA"       : {"bypass":1, "kill":1,'template':'VminTC_pt','supply':POR_VoltageTarget,'flowmatrix':'AT_F5_FREQ', 'voltageoverride':f'{POR_VoltageTarget}'+":1.1", 'plist': ["directdsdb","ssa",testtype], 'level' : 'nom'}}
	
	tests.extend(get_test_list(content_list[SKU],sub_flow,freq_corner))
	
	Flow(module+sku+"_"+sub_flow, Fitem("SAME", tuple(tests)[0], # edc = False if (content_list[SKU]["COMBINED"]["kill"]==1) else True,
				r0 = pFail(setbin=LSABin, goto = tuple(tests)[1].name) if (content_list[SKU]["COMBINED"]["kill"]==1) else pFail(setbin=AUTO),
				r1 = pPass(goto = tuple(tests)[2].name),
				r2 = pFail(setbin=LSABin, goto = tuple(tests)[1].name) if (content_list[SKU]["COMBINED"]["kill"]==1) else pFail(setbin=AUTO),
				r3 = pFail(setbin=LSABin, goto = tuple(tests)[1].name) if (content_list[SKU]["COMBINED"]["kill"]==1) else pFail(setbin=AUTO),
				r4 = pFail(setbin=LSA_Thermal, goto = tuple(tests)[1].name) if (content_list[SKU]["COMBINED"]["kill"]==1) else pFail(setbin=AUTO),
				r5 = pFail(setbin=LSA_Reset, goto = tuple(tests)[1].name) if (content_list[SKU]["COMBINED"]["kill"]==1) else pFail(setbin=AUTO)),
				 Fitem("SAME", tuple(tests)[1],
				r0 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r1 = pPass(ret = 0),
				r2 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r3 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r4 = pFail(setbin=SSA_Thermal, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r5 = pFail(setbin=SSA_Reset, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO)),
				Fitem("SAME", tuple(tests)[2], # edc = False if (content_list[SKU]["COMBINED"]["kill"]==1) else True,
				r0 = pFail(setbin=LSABin, goto = tuple(tests)[3].name) if (content_list[SKU]["COMBINED"]["kill"]==1) else pFail(setbin=AUTO),
				r1 = pPass(ret = 1),
				r2 = pFail(setbin=LSABin, goto = tuple(tests)[3].name) if (content_list[SKU]["COMBINED"]["kill"]==1) else pFail(setbin=AUTO),
				r3 = pFail(setbin=LSABin, goto = tuple(tests)[3].name) if (content_list[SKU]["COMBINED"]["kill"]==1) else pFail(setbin=AUTO),
				r4 = pFail(setbin=LSA_Thermal, goto = tuple(tests)[3].name) if (content_list[SKU]["COMBINED"]["kill"]==1) else pFail(setbin=AUTO),
				r5 = pFail(setbin=LSA_Reset, goto = tuple(tests)[3].name) if (content_list[SKU]["COMBINED"]["kill"]==1) else pFail(setbin=AUTO)),
				 Fitem("SAME", tuple(tests)[3],
				r0 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r1 = pPass(ret = 0),
				r2 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r3 = pFail(setbin=SSABin, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r4 = pFail(setbin=SSA_Thermal, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO),
				r5 = pFail(setbin=SSA_Reset, ret=0) if (content_list[SKU]["SSA"]["kill"]==1) else pFail(setbin=AUTO)))

	#
	################################################################
	#          
	#                       CSNF1 SUBFLOW                       
	#
	#################################################################
	##UNCOMMENT LATER##sub_flow = "CSNF1"						# Define the name of your flow
	##UNCOMMENT LATER##freq_corner = "F1"						# Define the test frequency
	##UNCOMMENT LATER##
	##UNCOMMENT LATER### Input
	##UNCOMMENT LATER### Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
	##UNCOMMENT LATER##content_list['HX'] =	{	"L2dragon"	: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCLPCORE','flowmatrix':'SAAT_F1_FREQ','voltageoverride':'VCCATOM_HC:SOC^SAN0@F1','powermux':POR_Pmux},
	##UNCOMMENT LATER##							"bilbo"		: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCLPCORE','flowmatrix':'SAAT_F1_FREQ','voltageoverride':'VCCATOM_HC:SOC^SAN0@F1' },
	##UNCOMMENT LATER##							"trunkdbg"	: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCLPCORE','flowmatrix':'SAAT_F1_FREQ','voltageoverride':'VCCATOM_HC:SOC^SAN0@F1' },
	##UNCOMMENT LATER##							"napbist"	: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F1_FREQ', 'voltageoverride':'VCCATOM_HC:SOC^SAAT0@F1'},
	##UNCOMMENT LATER##							"gfifo"		: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F1_FREQ', 'voltageoverride':'VCCATOM_HC:SOC^SAAT0@F1'}}
	##UNCOMMENT LATER##content_list['SX'] =	{	"L2dragon"	: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F1_FREQ', 'powermux':POR_Pmux},
	##UNCOMMENT LATER##							"bilbo"		: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F1_FREQ' },
	##UNCOMMENT LATER##							"trunkdbg"	: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F1_FREQ' },
	##UNCOMMENT LATER##							"napbist"	: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F1_FREQ' },
	##UNCOMMENT LATER##							"gfifo"		: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F1_FREQ' }}
	##UNCOMMENT LATER##content_list['SK'] =	{	"L2dragon"	: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F1_FREQ' },
	##UNCOMMENT LATER##							"bilbo"		: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F1_FREQ' },
	##UNCOMMENT LATER##							"trunkdbg"	: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F1_FREQ' },
	##UNCOMMENT LATER##							"napbist"	: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F1_FREQ' },
	##UNCOMMENT LATER##							"gfifo"		: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F1_FREQ' }}
	##UNCOMMENT LATER##
	##UNCOMMENT LATER##tests = get_test_list(content_list[SKU],sub_flow,freq_corner)
	##UNCOMMENT LATER##Flow(module+"_"+sub_flow, tests)

	#################################################################
	#          
	#                       CSNF2 SUBFLOW                       
	#
	#################################################################
	##UNCOMMENT LATER##sub_flow = "CSNF2"						# Define the name of your flow
	##UNCOMMENT LATER##freq_corner = "F2"						# Define the test frequency
	##UNCOMMENT LATER##
	##UNCOMMENT LATER### Input
	##UNCOMMENT LATER### Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
	##UNCOMMENT LATER##content_list['HX'] =	{	"L2dragon"	: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCLPCORE','flowmatrix':'SAAT_F2_FREQ','voltageoverride':'VCCATOM_HC:SOC^SAN0@F1','powermux':POR_Pmux},
	##UNCOMMENT LATER##							"bilbo"		: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCLPCORE','flowmatrix':'SAAT_F2_FREQ','voltageoverride':'VCCATOM_HC:SOC^SAN0@F1' },
	##UNCOMMENT LATER##							"trunkdbg"	: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCLPCORE','flowmatrix':'SAAT_F2_FREQ','voltageoverride':'VCCATOM_HC:SOC^SAN0@F1' },
	##UNCOMMENT LATER##							"napbist"	: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F2_FREQ', 'voltageoverride':'VCCATOM_HC:SOC^SAAT0@F1'},
	##UNCOMMENT LATER##							"gfifo"		: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F2_FREQ', 'voltageoverride':'VCCATOM_HC:SOC^SAAT0@F1'}}
	##UNCOMMENT LATER##content_list['SX'] =	{	"L2dragon"	: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F2_FREQ', 'powermux':POR_Pmux},
	##UNCOMMENT LATER##							"bilbo"		: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F2_FREQ' },
	##UNCOMMENT LATER##							"trunkdbg"	: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F2_FREQ' },
	##UNCOMMENT LATER##							"napbist"	: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F2_FREQ' },
	##UNCOMMENT LATER##							"gfifo"		: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F2_FREQ' }}
	##UNCOMMENT LATER##content_list['SK'] =	{	"L2dragon"	: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F2_FREQ' },
	##UNCOMMENT LATER##							"bilbo"		: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F2_FREQ' },
	##UNCOMMENT LATER##							"trunkdbg"	: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F2_FREQ' },
	##UNCOMMENT LATER##							"napbist"	: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F2_FREQ' },
	##UNCOMMENT LATER##							"gfifo"		: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F2_FREQ' }}
	##UNCOMMENT LATER##
	##UNCOMMENT LATER##tests = get_test_list(content_list[SKU],sub_flow,freq_corner)
	##UNCOMMENT LATER##Flow(module+"_"+sub_flow, tests)

	#################################################################
	#          
	#                       CSNF3 SUBFLOW                       
	#
	#################################################################
	##UNCOMMENT LATER##sub_flow = "CSNF3"						# Define the name of your flow
	##UNCOMMENT LATER##freq_corner = "F3"						# Define the test frequency
	##UNCOMMENT LATER##
	##UNCOMMENT LATER### Input
	##UNCOMMENT LATER### Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
	##UNCOMMENT LATER##content_list['HX'] =	{	"L2dragon"	: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCLPCORE','flowmatrix':'SAAT_F3_FREQ','voltageoverride':'VCCATOM_HC:SOC^SAN0@F1','powermux':POR_Pmux,'dts':POR_dts_noctv},
	##UNCOMMENT LATER##							"bilbo"		: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCLPCORE','flowmatrix':'SAAT_F3_FREQ','voltageoverride':'VCCATOM_HC:SOC^SAN0@F1' },
	##UNCOMMENT LATER##							"trunkdbg"	: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCLPCORE','flowmatrix':'SAAT_F3_FREQ','voltageoverride':'VCCATOM_HC:SOC^SAN0@F1' },
	##UNCOMMENT LATER##							"napbist"	: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F3_FREQ', 'voltageoverride':'VCCATOM_HC:SOC^SAAT0@F1'},
	##UNCOMMENT LATER##							"gfifo"		: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F3_FREQ', 'voltageoverride':'VCCATOM_HC:SOC^SAAT0@F1'}}
	##UNCOMMENT LATER##content_list['SX'] =	{	"L2dragon"	: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F3_FREQ', 'powermux':POR_Pmux,'dts':POR_dts_noctv},
	##UNCOMMENT LATER##							"bilbo"		: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F3_FREQ' },
	##UNCOMMENT LATER##							"trunkdbg"	: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F3_FREQ' },
	##UNCOMMENT LATER##							"napbist"	: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F3_FREQ' },
	##UNCOMMENT LATER##							"gfifo"		: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F3_FREQ' }}
	##UNCOMMENT LATER##content_list['SK'] =	{	"L2dragon"	: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F3_FREQ', 'dts':POR_dts_noctv },
	##UNCOMMENT LATER##							"bilbo"		: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F3_FREQ' },
	##UNCOMMENT LATER##							"trunkdbg"	: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F3_FREQ' },
	##UNCOMMENT LATER##							"napbist"	: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F3_FREQ' },
	##UNCOMMENT LATER##							"gfifo"		: {"bypass":1, "kill":1,'template':'VminTC_chk','recovery':1,'supply':'VCCATOM',    'flowmatrix':'SAN_F3_FREQ' }}
	##UNCOMMENT LATER##			 
	##UNCOMMENT LATER##
	##UNCOMMENT LATER##tests = get_test_list(content_list[SKU],sub_flow,freq_corner)
	##UNCOMMENT LATER##Flow(module+"_"+sub_flow, tests)

	#################################################################
	#          
	#                       CSNFMIN SUBFLOW                       
	#
	#################################################################
	##UNCOMMENT LATER##sub_flow = "CSNFMIN"						# Define the name of your flow
	##UNCOMMENT LATER##freq_corner = "FMIN"						# Define the test frequency
	##UNCOMMENT LATER##
	##UNCOMMENT LATER### Input
	##UNCOMMENT LATER### Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
	##UNCOMMENT LATER##content_list['HX'] = {	"L2dragon"	: {"bypass":1, "kill":0,'template':'VminTC_pt','supply':'VCCLPCORE','flowmatrix':'SAAT_FMIN','voltageoverride':'VCCLPCORE_HC:SOC^SAAT0@F1,VCCATOM_HC:SOC^SAN0@F1','recovery':1,'powermux':POR_Pmux},
	##UNCOMMENT LATER##						"bilbo"		: {"bypass":1, "kill":0,'template':'VminTC_pt','supply':'VCCLPCORE','flowmatrix':'SAAT_FMIN','voltageoverride':'VCCLPCORE_HC:SOC^SAAT0@F1,VCCATOM_HC:SOC^SAN0@F1','recovery':1},
	##UNCOMMENT LATER##						"trunkdbg"	: {"bypass":1, "kill":0,'template':'VminTC_pt','supply':'VCCLPCORE','flowmatrix':'SAAT_FMIN','voltageoverride':'VCCLPCORE_HC:SOC^SAAT0@F1,VCCATOM_HC:SOC^SAN0@F1','recovery':1},
	##UNCOMMENT LATER##						"napbist"	: {"bypass":1, "kill":0,'template':'VminTC_pt','supply':'VCCATOM',    'flowmatrix':'SAN_FMIN', 'voltageoverride':'VCCLPCORE_HC:SOC^SAAT0@F1,VCCATOM_HC:SOC^SAN0@F1','recovery':1},
	##UNCOMMENT LATER##						"gfifo"		: {"bypass":1, "kill":0,'template':'VminTC_pt','supply':'VCCATOM',    'flowmatrix':'SAN_FMIN', 'voltageoverride':'VCCLPCORE_HC:SOC^SAAT0@F1,VCCATOM_HC:SOC^SAN0@F1','recovery':1}}
	##UNCOMMENT LATER##content_list['SX'] = {	"L2dragon"	: {"bypass":1, "kill":0,'template':'VminTC_pt','supply':'VCCATOM',    'flowmatrix':'SAN_FMIN', 'voltageoverride':'VCCATOM_HC:SOC^SAN0@F1', 'recovery':1,'powermux':POR_Pmux},
	##UNCOMMENT LATER##						"bilbo"		: {"bypass":1, "kill":0,'template':'VminTC_pt','supply':'VCCATOM',    'flowmatrix':'SAN_FMIN', 'voltageoverride':'VCCATOM_HC:SOC^SAN0@F1', 'recovery':1},
	##UNCOMMENT LATER##						"trunkdbg"	: {"bypass":1, "kill":0,'template':'VminTC_pt','supply':'VCCATOM',    'flowmatrix':'SAN_FMIN', 'voltageoverride':'VCCATOM_HC:SOC^SAN0@F1', 'recovery':1},
	##UNCOMMENT LATER##						"napbist"	: {"bypass":1, "kill":0,'template':'VminTC_pt','supply':'VCCATOM',    'flowmatrix':'SAN_FMIN', 'voltageoverride':'VCCATOM_HC:SOC^SAN0@F1', 'recovery':1},
	##UNCOMMENT LATER##						"gfifo"		: {"bypass":1, "kill":0,'template':'VminTC_pt','supply':'VCCATOM',    'flowmatrix':'SAN_FMIN', 'voltageoverride':'VCCATOM_HC:SOC^SAN0@F1', 'recovery':1}}
	##UNCOMMENT LATER##content_list['SK'] = {	"L2dragon"	: {"bypass":1, "kill":0,'template':'VminTC_pt','supply':'VCCATOM',    'flowmatrix':'SAN_FMIN', 'voltageoverride':'VCCATOM_HC:SOC^SAN0@F1', 'recovery':1},
	##UNCOMMENT LATER##						"bilbo"		: {"bypass":1, "kill":0,'template':'VminTC_pt','supply':'VCCATOM',    'flowmatrix':'SAN_FMIN', 'voltageoverride':'VCCATOM_HC:SOC^SAN0@F1', 'recovery':1},
	##UNCOMMENT LATER##						"trunkdbg"	: {"bypass":1, "kill":0,'template':'VminTC_pt','supply':'VCCATOM',    'flowmatrix':'SAN_FMIN', 'voltageoverride':'VCCATOM_HC:SOC^SAN0@F1', 'recovery':1},
	##UNCOMMENT LATER##						"napbist"	: {"bypass":1, "kill":0,'template':'VminTC_pt','supply':'VCCATOM',    'flowmatrix':'SAN_FMIN', 'voltageoverride':'VCCATOM_HC:SOC^SAN0@F1', 'recovery':1},
	##UNCOMMENT LATER##						"gfifo"		: {"bypass":1, "kill":0,'template':'VminTC_pt','supply':'VCCATOM',    'flowmatrix':'SAN_FMIN', 'voltageoverride':'VCCATOM_HC:SOC^SAN0@F1', 'recovery':1}}
	##UNCOMMENT LATER##
	##UNCOMMENT LATER##tests = get_test_list(content_list[SKU],sub_flow,freq_corner)
	##UNCOMMENT LATER##Flow(module+"_"+sub_flow, tests)

	#################################################################
	#          
	#                       MAXSN SUBFLOW                       
	#
	#################################################################
	#UNCOMMENT LATER#sub_flow = "MAXSN"						# Define the name of your flow
	#UNCOMMENT LATER#flows = []
	#UNCOMMENT LATER#
	#UNCOMMENT LATER##build composite MAXSN_F1,MAXSN_F3
	#UNCOMMENT LATER#for freq_corner in ("F1","F3"):
	#UNCOMMENT LATER#	# Input
	#UNCOMMENT LATER#	# Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
	#UNCOMMENT LATER#	content_list['HX'] = { "L2dragon"	: {"bypass":1, "kill":1,'template':'VminTC_max','supply':'VCCLPCORE','flowmatrix':'SAAT_'+freq_corner+'_FREQ','voltageoverride':'VCCLPCORE_HC:"+FlowMatrix.AT_VMAX_VALUE+",VCCATOM_HC:"+FlowMatrix.SA_VMAX_VALUE','recovery':1,'powermux':POR_Pmux},
	#UNCOMMENT LATER#						   "bilbo"		: {"bypass":1, "kill":1,'template':'VminTC_max','supply':'VCCLPCORE','flowmatrix':'SAAT_'+freq_corner+'_FREQ','voltageoverride':'VCCLPCORE_HC:"+FlowMatrix.AT_VMAX_VALUE+",VCCATOM_HC:"+FlowMatrix.SA_VMAX_VALUE','recovery':1},
	#UNCOMMENT LATER#						   "trunkdbg"	: {"bypass":1, "kill":1,'template':'VminTC_max','supply':'VCCLPCORE','flowmatrix':'SAAT_'+freq_corner+'_FREQ','voltageoverride':'VCCLPCORE_HC:"+FlowMatrix.AT_VMAX_VALUE+",VCCATOM_HC:"+FlowMatrix.SA_VMAX_VALUE','recovery':1},
	#UNCOMMENT LATER#						   "napbist"	: {"bypass":1, "kill":1,'template':'VminTC_max','supply':'VCCATOM',    'flowmatrix':'SAN_'+freq_corner+'_FREQ', 'voltageoverride':'VCCLPCORE_HC:"+FlowMatrix.AT_VMAX_VALUE+",VCCATOM_HC:"+FlowMatrix.SA_VMAX_VALUE','recovery':1},
	#UNCOMMENT LATER#						   "gfifo"		: {"bypass":1, "kill":1,'template':'VminTC_max','supply':'VCCATOM',    'flowmatrix':'SAN_'+freq_corner+'_FREQ', 'voltageoverride':'VCCLPCORE_HC:"+FlowMatrix.AT_VMAX_VALUE+",VCCATOM_HC:"+FlowMatrix.SA_VMAX_VALUE','recovery':1}}
	#UNCOMMENT LATER#	content_list['SX'] = { "L2dragon"	: {"bypass":1, "kill":1,'template':'VminTC_max','supply':'VCCATOM',    'flowmatrix':'SAN_'+freq_corner+'_FREQ', 'voltageoverride':'VCCATOM_HC:"+FlowMatrix.SA_VMAX_VALUE','recovery':1,'powermux':POR_Pmux},
	#UNCOMMENT LATER#						   "bilbo"		: {"bypass":1, "kill":1,'template':'VminTC_max','supply':'VCCATOM',    'flowmatrix':'SAN_'+freq_corner+'_FREQ', 'voltageoverride':'VCCATOM_HC:"+FlowMatrix.SA_VMAX_VALUE','recovery':1},
	#UNCOMMENT LATER#						   "trunkdbg"	: {"bypass":1, "kill":1,'template':'VminTC_max','supply':'VCCATOM',    'flowmatrix':'SAN_'+freq_corner+'_FREQ', 'voltageoverride':'VCCATOM_HC:"+FlowMatrix.SA_VMAX_VALUE','recovery':1},
	#UNCOMMENT LATER#						   "napbist"	: {"bypass":1, "kill":1,'template':'VminTC_max','supply':'VCCATOM',    'flowmatrix':'SAN_'+freq_corner+'_FREQ', 'voltageoverride':'VCCATOM_HC:"+FlowMatrix.SA_VMAX_VALUE','recovery':1},
	#UNCOMMENT LATER#						   "gfifo"		: {"bypass":1, "kill":1,'template':'VminTC_max','supply':'VCCATOM',    'flowmatrix':'SAN_'+freq_corner+'_FREQ', 'voltageoverride':'VCCATOM_HC:"+FlowMatrix.SA_VMAX_VALUE','recovery':1}}
	#UNCOMMENT LATER#	content_list['SK'] = { "L2dragon"	: {"bypass":1, "kill":1,'template':'VminTC_max','supply':'VCCATOM',    'flowmatrix':'SAN_'+freq_corner+'_FREQ', 'voltageoverride':'VCCATOM_HC:"+FlowMatrix.SA_VMAX_VALUE','recovery':1},
	#UNCOMMENT LATER#						   "bilbo"		: {"bypass":1, "kill":1,'template':'VminTC_max','supply':'VCCATOM',    'flowmatrix':'SAN_'+freq_corner+'_FREQ', 'voltageoverride':'VCCATOM_HC:"+FlowMatrix.SA_VMAX_VALUE','recovery':1},
	#UNCOMMENT LATER#						   "trunkdbg"	: {"bypass":1, "kill":1,'template':'VminTC_max','supply':'VCCATOM',    'flowmatrix':'SAN_'+freq_corner+'_FREQ', 'voltageoverride':'VCCATOM_HC:"+FlowMatrix.SA_VMAX_VALUE','recovery':1},
	#UNCOMMENT LATER#						   "napbist"	: {"bypass":1, "kill":1,'template':'VminTC_max','supply':'VCCATOM',    'flowmatrix':'SAN_'+freq_corner+'_FREQ', 'voltageoverride':'VCCATOM_HC:"+FlowMatrix.SA_VMAX_VALUE','recovery':1},
	#UNCOMMENT LATER#						   "gfifo"		: {"bypass":1, "kill":1,'template':'VminTC_max','supply':'VCCATOM',    'flowmatrix':'SAN_'+freq_corner+'_FREQ', 'voltageoverride':'VCCATOM_HC:"+FlowMatrix.SA_VMAX_VALUE','recovery':1}}
	#UNCOMMENT LATER#
	#UNCOMMENT LATER#		
	#UNCOMMENT LATER#	tests = get_test_list(content_list[SKU],sub_flow,freq_corner)
	#UNCOMMENT LATER#	composite = Flow(sub_flow+"_"+freq_corner, tests)
	#UNCOMMENT LATER#	flows.append(Fitem("SAME", composite, r0 = pFail(ret=0)))
	#UNCOMMENT LATER#
	#UNCOMMENT LATER#
	#UNCOMMENT LATER#Flow(module+"_"+sub_flow, flows)
	#################################################################
	#          
	#                    ENDHUBNOM SUBFLOW                       
	#
	#################################################################
	sub_flow = "ENDCPUNOM"						# Define the name of your flow
	freq_corner = "F1"						# Define the test frequency
	IPCluster = "L2"
	arraytype = "LSA"
	testtype = "RET"

	# Input
	# Define the test types we want in this subflow and also define Bypass and EDC definitions separately so that we can change them easily in the future.
	content_list[SKU] = {	"SSA_l2c6"	: {"bypass":1, "kill":1,'template':'VminTC_pt','supply':POR_VoltageTarget,'flowmatrix':'AT_F1_FREQ', 'plist': [IPCluster,arraytype,testtype],'level':'nom'}}
	
	tests = get_test_list(content_list[SKU],sub_flow,freq_corner)
	
	
	Flow(module+sku+"_"+sub_flow, Fitem("SAME", tuple(tests)[0] , edc = False if (content_list[SKU]["SSA_l2c6"]["kill"]==1) else True,
				r0 = pFail(setbin=LSABin, ret=0) if (content_list[SKU]["SSA_l2c6"]["kill"]==1) else pFail(setbin=LSABin),
				r1 = pPass(ret=1),
				r2 = pFail(setbin=LSABin, ret=0) if (content_list[SKU]["SSA_l2c6"]["kill"]==1) else pFail(setbin=LSABin),
				r3 = pFail(setbin=LSABin, ret=0) if (content_list[SKU]["SSA_l2c6"]["kill"]==1) else pFail(setbin=LSABin)))
				#r4 = pFail(setbin=LSA_Thermal[sku], ret=0) if (content_list[SKU]["SSA_l2c6"]["kill"]==1) else pFail(setbin=LSA_Thermal[sku]),
				#r5 = pFail(setbin=LSA_Reset[sku], ret=0) if (content_list[SKU]["SSA_l2c6"]["kill"]==1) else pFail(setbin=LSA_Reset[sku])))


	#################################################################
	#		  
	#					ENDHUB SUBFLOW					   
	#
	#################################################################
	sub_flow = "ENDCPU"						# Define the name of your flow
	freq_corner = "X"						# Define the test frequency
	IPCluster = "ALL"
	arraytype = "ALL"
	testtype = "REDUCEDKS_COFREQ"

	content_list[SKU] = { "PMUX_CO_FREQ0"  : {"bypass" : 1,
											 "kill" : 0, 
											 "template" : 'RunCallback1',
											 "param" : '--target AT0 --voltage 0.715 --flow CPU --expression MCdrv:atomfreq0_0:[FREQ0]GHz,MCdrv:corefreq:0.8GHz,MCdrv:ringfreq_0:0.8GHz,MCAarr:ratio_modify:0.8GHz --token CPUATOM0PMUX', 
											 "callback" : 'CalculateFrequencySwitch', 
											 "postcall" : 'PrintToItuff(--body_type strgval --body_data G.U.S.CPUATOM0PMUX --tname_suf _CPUATOM0_CO_FREQ)'},
					  
						"PMUX_CO_FREQ1" : {"bypass" : 1,
											 "kill" : 0, 
											 "template" : 'RunCallback1',
											 "param" : '--target AT1 --voltage 0.715 --flow CPU --expression MCdrv:atomfreq1_0:[FREQ0]GHz,MCdrv:corefreq:0.8GHz,MCdrv:ringfreq_0:0.8GHz,MCAarr:ratio_modify:0.8GHz --token CPUATOM1PMUX', 
											 "callback" : 'CalculateFrequencySwitch', 
											 "postcall" : 'PrintToItuff(--body_type strgval --body_data G.U.S.CPUATOM1PMUX --tname_suf _CPUATOM1_CO_FREQ)'},

						"PMUX_CO_FREQ2" : {"bypass" : 1,
											 "kill" : 0, 
											 "template" : 'RunCallback1',
											 "param" : '--target AT2 --voltage 0.715 --flow CPU --expression MCdrv:atomfreq2_0:[FREQ0]GHz,MCdrv:corefreq:0.8GHz,MCdrv:ringfreq_0:0.8GHz,MCAarr:ratio_modify:0.8GHz --token CPUATOM2PMUX', 
											 "callback" : 'CalculateFrequencySwitch', 
											 "postcall" : 'PrintToItuff(--body_type strgval --body_data G.U.S.CPUATOM2PMUX --tname_suf _CPUATOM2_CO_FREQ)'},

						"PMUX_CO_FREQ3" : {"bypass" : 1,
											 "kill" : 0, 
											 "template" : 'RunCallback1',
											 "param" : '--target AT3 --voltage 0.715 --flow CPU --expression MCdrv:atomfreq3_0:[FREQ0]GHz,MCdrv:corefreq:0.8GHz,MCdrv:ringfreq_0:0.8GHz,MCAarr:ratio_modify:0.8GHz --token CPUATOM3PMUX', 
											 "callback" : 'CalculateFrequencySwitch', 
											 "postcall" : 'PrintToItuff(--body_type strgval --body_data G.U.S.CPUATOM3PMUX --tname_suf _CPUATOM3_CO_FREQ)'}					  

					  }
	
	tests = get_test_list(content_list[SKU],sub_flow,freq_corner)

	
	content_list_co_freq = 	{ "L2_TAG"		: {"bypass":1, "kill":0,'template':'VminTC_pt','supply':POR_VoltageTarget,'flowmatrix':'SAAT_X', 
												'PreInstance' :'ExecutePatConfigSetPoint(G.U.S.CPUATOM0PMUX)',
												'voltageoverride':f'{POR_VoltageTarget}'+":0.715",'powermux':POR_Pmux,'plist':["directdsdb","ssa",testtype]},
							  "L2_DATA"		: {"bypass":1, "kill":0,'template':'VminTC_pt','supply':POR_VoltageTarget,'flowmatrix':'SAAT_X',
												'PreInstance' :'ExecutePatConfigSetPoint(G.U.S.CPUATOM0PMUX)',
												'voltageoverride':f'{POR_VoltageTarget}'+":0.715",'powermux':POR_Pmux,'plist': ["directdsdb","ssa",testtype]}}
	
	
	tests.extend(get_test_list(content_list_co_freq,sub_flow,freq_corner))

	Flow(module+sku+"_"+sub_flow, Fitem("SAME", tuple(tests)[0], edc = False if (content_list[SKU]["PMUX_CO_FREQ0"]["kill"]==1) else True, r0 = pFail(setbin=SSABin, ret="0")),
								Fitem("SAME", tuple(tests)[1], edc = False if (content_list[SKU]["PMUX_CO_FREQ1"]["kill"]==1) else True, r0 = pFail(setbin=SSABin, ret="0")),
								Fitem("SAME", tuple(tests)[2], edc = False if (content_list[SKU]["PMUX_CO_FREQ2"]["kill"]==1) else True, r0 = pFail(setbin=SSABin, ret="0")),
								Fitem("SAME", tuple(tests)[3], edc = False if (content_list[SKU]["PMUX_CO_FREQ3"]["kill"]==1) else True, r0 = pFail(setbin=SSABin, ret="0")),
								  Fitem("SAME", tuple(tests)[4], edc = False if (content_list_co_freq["L2_TAG"]["kill"]==1) else True, r0 = pFail(setbin=SSABin, ret="0")),
								  Fitem("SAME", tuple(tests)[5], edc = False if (content_list_co_freq["L2_DATA"]["kill"]==1) else True, r0 = pFail(setbin=SSABin, ret="0")))

# generate mconfig file
get_mconfig()