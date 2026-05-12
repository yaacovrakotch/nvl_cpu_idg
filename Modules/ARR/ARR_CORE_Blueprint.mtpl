Version 1.0;

ProgramStyle = Modular;

TestPlan ARR_\Module\_CXX;

Import "ARR_\Module\_CXX.usrv";
Import "ARR_\Module\_CXX_Timing.tcg";
Import "ARR_\Module\_CXX_Level.tcg";

# Test Counter Definition

MultiTrialTest \IP\_\Module\_\Type\_\RunMode\_\SF\_X_\Domain\A_\CORNER\_MTT
{
    TrialVariable CPU_TRIALS::FlowDomain.CORE;
    TrialVariableExitAction "Continue";
	CSharpTrialTest VminTC "\IP\_\Module\_\Type\_\RunMode\_\SF\_X_\Domain\A_\CORNER\_" + __shared__::CustomFlowMatrixSpecs.CR_\CORNER\_FREQ_MHz + "_ALL"
    {
        CornerIdentifiers = "CR3@\CORNER\,CR2@\CORNER\,CR1@\CORNER\,CR0@\CORNER\";
        Patlist = \Plist\   
        LevelsTc = "IPC::ARR_\Module\_CXX::arr_cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_ARR_MBIST_min_lvl";
        TimingsTc = "IPC::ARR_\Module\_CXX::cpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800";
        BaseNumbers = \BaseNumber\ ## numbers going up.
        BypassPort = -1;
        EndVoltageLimits = \EndVoltageLimits\
        ExecutionMode = "SearchWithScoreboard";
        FailCaptureCount = toInteger(1);
        FeatureSwitchSettings = ARR_\Module\_CXX_Specs.FeatureSwitchMTT;
        FivrCondition = ARR_\Module\_CXX_Specs.FivrConditionNom;
        FivrConditionPlistParamName = "Patlist";
        TrialParam FlowIndex = __shared__::FlowMatrixSingular.FlowIndex;
        ForwardingMode = ARR_\Module\_CXX_Specs.ForwardingMode_Kill;
        LimitGuardband = toString(__shared__::GBVars.LimitGuardband);
        MaxFailsNum = toInteger(20);
        PatternNameCounterIndexes = ARR_\Module\_CXX_Specs.PatternMap;
        PinMap = ARR_\Module\_CXX_Specs.Recovery_PinMap;
        RecoveryMode = ARR_\Module\_CXX_Specs.Recovery_Mode_Speedflow;
        RecoveryOptions = __shared__::Recovery_Single.F1F4_recovery_opt_CR;
        RecoveryTrackingIncoming = ARR_\Module\_CXX_Specs.RecoveryTracker_Incoming;
        RecoveryTrackingOutgoing = ARR_\Module\_CXX_Specs.RecoveryTracker_Outgoing_Speedflow;
        SetPointsPlistParamName = "Patlist";
        SetPointsPostInstance = PSPOST.\Domain\_\CORNER\;
        SetPointsPreInstance = PSPRE.\Domain\_\CORNER\+","+"MCdrv:"+ARR_\Module\_CXX_Specs.corefreq+":"+ __shared__::FlowMatrixSingular.CR_\CORNER\_FREQ+"GHz,MCdrv:"+ARR_\Module\_CXX_Specs.ringfreq+":"+ __shared__::FlowMatrixSingular.CCF_\CORNER\_FREQ+"GHz";
        StartVoltages = __shared__::FlowMatrixSingular.\Domain\_LOW_SEARCH_VALUE;
        StartVoltagesForRetry = __shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "");
        StartVoltagesOffset = __shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "");
        StepSize = toDouble(__shared__::FlowMatrixSingular.\Domain\_SEARCH_RESOLUTION);
        TestMode = "MultiVmin";
        VoltageConverter = ARR_\Module\_CXX_Specs.VoltageConverter_rail + DROPOUT.\Domain\_\CORNER\;
        VoltageTargets = ARR_\Module\_CXX_Specs.CORE_NonPMUCS_VoltageTarget;
        VminResult = "ARR_DCM3_\CORNER\_VMIN,ARR_DCM2_\CORNER\_VMIN,ARR_DCM1_\CORNER\_VMIN,ARR_DCM0_\CORNER\_VMIN";
        TrialResult -2
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -1;
        }
        TrialResult 0
        {
            PassFail Fail;
            TrialAction __shared__::TpRule.MTT_Rule("Next","Exit");
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
            Return 1;
        }
        TrialResult 2
        {
            PassFail Fail;
            TrialAction __shared__::TpRule.MTT_Rule("Next","Exit");
            Return 2;
        }
        TrialResult 3
        {
            PassFail Pass;
            TrialAction __shared__::TpRule.MTT_Rule("Next","Exit");
            Return 3;
        }
        TrialResult 4
        {
            PassFail Fail;
            TrialAction __shared__::TpRule.MTT_Rule("Next","Exit");
            Return 4;
        }
        TrialResult 5
        {
            PassFail Fail;
            TrialAction __shared__::TpRule.MTT_Rule("Next","Exit");
            Return 5;
        }
    }
}

MultiTrialTest \IP\_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_\CORNERTOP\_MTT
{
    TrialVariable CPU_TRIALS::FlowDomain.CORE_TOP;
    TrialVariableExitAction "Continue";
	CSharpTrialTest VminTC "\IP\_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_\CORNERTOP\_" + __shared__::CORNERs.\Domain\_\FlowMatrixTOP\ + "_ALL"
    {

        Patlist = \Plist\    
        LevelsTc = "IPC::ARR_\Module\_CXX::arr_cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_ARR_MBIST_min_lvl";
        TimingsTc = "IPC::ARR_\Module\_CXX::cpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800";
        BaseNumbers = \BaseNumber\
        BypassPort = -1;
        TrialParam CornerIdentifiers = __shared__::CornerIdentifiers.\Domain\_\FlowMatrixTOP\;
        DtsConfiguration = ARR_\Module\_Rules.QA_HOT_Default("","nvl_cpu_all_ctv","");
        EndVoltageLimits = \EndVoltageLimits\
        ExecutionMode = "Search";
        FailCaptureCount = toInteger(1);
        FeatureSwitchSettings = ARR_\Module\_CXX_Specs.FeatureSwitchMTT;
        FivrCondition = ARR_\Module\_CXX_Specs.FivrConditionNom;
        FivrConditionPlistParamName = "Patlist";
        FlowIndex = __shared__::FlowMatrixSingular.FlowIndex;
        ForwardingMode = ARR_\Module\_CXX_Specs.ForwardingMode_Kill;
        LimitGuardband = toString(__shared__::GBVars.LimitGuardband);
        PatternNameCounterIndexes = ARR_\Module\_CXX_Specs.PatternMap;
        PinMap = ARR_\Module\_CXX_Specs.Recovery_PinMap;
        RecoveryMode = ARR_\Module\_CXX_Specs.Recovery_Mode_Speedflow;
        TrialParam RecoveryOptions = __shared__::Recovery.MTT_recovery_opt_CR;
        RecoveryTrackingIncoming = ARR_\Module\_CXX_Specs.RecoveryTracker_Incoming;
        RecoveryTrackingOutgoing = ARR_\Module\_CXX_Specs.RecoveryTracker_Outgoing_Speedflow;
        SetPointsPlistParamName = "Patlist";
        SetPointsPostInstance = PSPOST.\Domain\_\CORNERTOP\;
        TrialParam SetPointsPreInstance = PSPRE.\Domain\_\CORNERTOP\+","+"MCdrv:"+ARR_\Module\_CXX_Specs.corefreq+":"+ __shared__::FreqValues.\Domain\_\FlowMatrixTOP\+"GHz,MCdrv:"+ARR_\Module\_CXX_Specs.ringfreq+":"+ __shared__::FreqValues.CCF_C5+"GHz";
        StartVoltages = __shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE;
        StartVoltagesForRetry = __shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "");
        StartVoltagesOffset = __shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "");
        StepSize = toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION);
        TestMode = "MultiVmin";
        VoltageConverter = ARR_\Module\_CXX_Specs.VoltageConverter_rail + DROPOUT.\Domain\_\CORNERTOP\;
        VoltageTargets = ARR_\Module\_CXX_Specs.CORE_NonPMUCS_VoltageTarget;
        TrialResult -2
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -1;
        }
        TrialResult 0
        {
            PassFail Fail;
            TrialAction __shared__::TpRule.MTT_Rule("Next","Exit");
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
            Return 1;
        }
        TrialResult 2
        {
            PassFail Fail;
            TrialAction __shared__::TpRule.MTT_Rule("Next","Exit");
            Return 0;
        }
        TrialResult 3
        {
            PassFail Fail;
            TrialAction "Exit";
            Return 4;
        }
        TrialResult 4
        {
            PassFail Fail;
            TrialAction __shared__::TpRule.MTT_Rule("Next","Exit");
            Return 4;
        }
        TrialResult 5
        {
            PassFail Fail;
            TrialAction __shared__::TpRule.MTT_Rule("Next","Exit");
            Return 5;
        }
    }
}


CSharpTest ApexTC XSA_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_X_X_ALL_APEX_FMAX
{
    Patlist = "IPC::arr_cdie_\sftop\_mbist_core_all_all_all_limiter_\cornertop\_class_hptp_list_master";    
    LevelsTc = "IPC::ARR_\Module\_CXX::arr_cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_ARR_MBIST_min_lvl";
    TimingsTc = "IPC::ARR_\Module\_CXX::cpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800";
    BypassPort = 1;
    End = __shared__::FlowMatrixSingular.APEX_\Module\_MIN;
    ExportTokens = "FXCRC3,FXCRC2,FXCRC1,FXCRC0";
    FivrCondition = ARR_\Module\_CXX_Specs.FivrConditionNom;
    FivrConditionPlistParamName = "Patlist";
    ForwardingMode = ARR_\Module\_CXX_Specs.ForwardingMode_EDC;
    PatternNameCounterIndexes = ARR_\Module\_CXX_Specs.PatternMap;
    PinMap = ARR_\Module\_CXX_Specs.Recovery_PinMap;
    RecoveryOptions = ARR_\Module\_CXX_Specs.Recovery_Options_Speedflow;
    RecoveryTracking = ARR_\Module\_CXX_Specs.RecoveryTracker_Incoming;
    SetPointsPostInstance = PSPOST.\Domain\_\CORNERTOP\+",CORE:nblctrl_core_l2:nblon";
    SetPointsPreInstance = PSPRE.\Domain\_\CORNERTOP\+","+"MCdrv:"+ARR_\Module\_CXX_Specs.corefreq+":"+ __shared__::FlowMatrixSingular.CR_\CORNER\_FREQ+"GHz,MCdrv:"+ARR_\Module\_CXX_Specs.ringfreq+":"+ __shared__::FlowMatrixSingular.CCF_\CORNER\_FREQ+"GHz,CORE:nblctrl_core_l2:nbloff";
    Start = __shared__::FlowMatrixSingular.APEX_\Module\_MAX;
    StepSize = toInteger(1);
    Targets = "ACORE3,ACORE2,ACORE1,ACORE0";
    VoltageConverter = ARR_\Module\_CXX_Specs.VoltageConverter_rail + DROPOUT.\Domain\_\CORNERTOP\ + " --overrides CORE3:"+__shared__::FlowMatrixSingular.CR_VMAX_VALUE+",CORE2:"+__shared__::FlowMatrixSingular.CR_VMAX_VALUE+",CORE1:"+__shared__::FlowMatrixSingular.CR_VMAX_VALUE+",CORE0:"+__shared__::FlowMatrixSingular.CR_VMAX_VALUE;
}

MultiTrialTest XSA_\Module\_\Type\_\RunMode\_F5XCR_X_\Domain\A_\CORNERTOP\_\SPLITCORE\_MTT
{
    TrialVariable CPU_TRIALS::FlowDomain.CORE_TOP;
	TrialVariableExitAction "Continue";
	CSharpTrialTest VminTC "XSA_\Module\_\Type\_\RunMode\_F5XCR_X_\Domain\_" + __shared__::CORNERs.\Domain\_\FlowMatrixTOP\+ "_" + __shared__::FreqInMHZ.\Domain\_\FlowMatrixTOP\ + "_\SPLITCORE\"
    {
        Patlist = "IPC::arr_cdie_f5xcr_mbist_core_all_all_all_limiter_\CORNERTOP\_class_hptp_list_master";    
        LevelsTc = "IPC::ARR_\Module\_CXX::arr_cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_ARR_MBIST_min_lvl";
        TimingsTc = "IPC::ARR_\Module\_CXX::cpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800";
        BaseNumbers = \BaseNumber\
        BypassPort = 1;
        TrialParam CornerIdentifiers = __shared__::CornerIdentifiers.\Domain\_\FlowMatrixTOP\;
        DtsConfiguration = ARR_\Module\_Rules.QA_HOT_Default("","nvl_cpu_all_ctv","");
        EndVoltageLimits = \EndVoltageLimits\
        ExecutionMode = "SearchWithScoreboard";
        FailCaptureCount = toInteger(1);
        FeatureSwitchSettings = ARR_\Module\_CXX_Specs.FeatureSwitchMTT;
        InitialMaskBits = "1100";
        MaskPins = \MaskPins\
        FivrCondition = ARR_\Module\_CXX_Specs.FivrConditionNom;
        FivrConditionPlistParamName = "Patlist";
        FlowIndex = __shared__::FlowMatrixSingular.FlowIndex;
        ForwardingMode = ARR_\Module\_CXX_Specs.ForwardingMode_Kill;
        LimitGuardband = toString(__shared__::GBVars.LimitGuardband);
        PatternNameCounterIndexes = ARR_\Module\_CXX_Specs.PatternMap;
        PinMap = ARR_\Module\_CXX_Specs.Recovery_PinMap;
        RecoveryMode = ARR_\Module\_CXX_Specs.Recovery_Mode_Speedflow;
        TrialParam RecoveryOptions = __shared__::Recovery.MTT_recovery_opt_CR;
        RecoveryTrackingIncoming = ARR_\Module\_CXX_Specs.RecoveryTracker_Incoming;
        RecoveryTrackingOutgoing = ARR_\Module\_CXX_Specs.RecoveryTracker_Outgoing_Speedflow;
        SetPointsPlistParamName = "Patlist";
        SetPointsPostInstance = PSPOST.\Domain\_\CORNERTOP\;
        TrialParam SetPointsPreInstance = PSPRE.\Domain\_\CORNERTOP\+","+"MCdrv:corefreq3:"+"0.8GHz,"+"MCdrv:corefreq2:"+"0.8GHz,"+"MCdrv:corefreq1:"+ __shared__::FreqValues.\Domain\_\FlowMatrixTOP\+"GHz,"+"MCdrv:corefreq0:"+ __shared__::FreqValues.\Domain\_\FlowMatrixTOP\+"GHz,MCdrv:"+ARR_\Module\_CXX_Specs.ringfreq+":"+ __shared__::FreqValues.CCF_C5+"GHz";
        StartVoltages = __shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE;
        StartVoltagesForRetry = __shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "");
        StartVoltagesOffset = __shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "");
        StepSize = toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION);
        TestMode = "MultiVmin";
        VoltageConverter = ARR_\Module\_CXX_Specs.VoltageConverter_rail + DROPOUT.\Domain\_\CORNERTOP\;
        VoltageTargets = ARR_\Module\_CXX_Specs.CORE_NonPMUCS_VoltageTarget;
        TrialResult -2
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -1;
        }
        TrialResult 0
        {
            PassFail Fail;
            TrialAction __shared__::TpRule.MTT_Rule("Next","Exit");
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
            Return 1;
        }
        TrialResult 2
        {
            PassFail Fail;
            TrialAction __shared__::TpRule.MTT_Rule("Next","Exit");
            Return 2;
        }
        TrialResult 3
        {
            PassFail Fail;
            TrialAction __shared__::TpRule.MTT_Rule("Next","Exit");
            Return 3;
        }
        TrialResult 4
        {
            PassFail Fail;
            TrialAction __shared__::TpRule.MTT_Rule("Next","Exit");
            Return 4;
        }
        TrialResult 5
        {
            PassFail Fail;
            TrialAction __shared__::TpRule.MTT_Rule("Next","Exit");
            Return 5;
        }
    }
}

MultiTrialTest XSA_\Module\_SB_\RunMode\_FMINXCR_X_\Domain\A_FMIN_MTT
{
    TrialVariable CPU_TRIALS::FlowDomain.CORE;
    TrialVariableExitAction "Continue";
	CSharpTrialTest VminTC "XSA_\Module\_SB_\RunMode\_FMINXCR_X_\Domain\A_FMIN_" + __shared__::CustomFlowMatrixSpecs.CR_FMIN_MHz + "_ALL"
    {
    CornerIdentifiers = "CR3@F1,CR2@F1,CR1@F1,CR0@F1";    
    Patlist = "IPC::arr_cdie_fminxcr_mbist_core_all_all_all_limiter_fmin_class_hptp_list_master";    
    LevelsTc = "IPC::ARR_\Module\_CXX::arr_cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_ARR_MBIST_min_lvl";
    TimingsTc = "IPC::ARR_\Module\_CXX::cpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800";
    BaseNumbers = \BaseNumber\
    BypassPort = -1;
    EndVoltageLimits = \EndVoltageLimits\
    #LimitGuardband = toString(__shared__::GBVars.FminLimitGuardband);
    LimitGuardband = toString(__shared__::TpRule.If_QRE("",toString(__shared__::GBVars.FminLimitGuardband)));
    ExecutionMode = "SearchWithScoreboard";
    FailCaptureCount = toInteger(1);
    FivrCondition = ARR_\Module\_CXX_Specs.FivrConditionNom;
    FeatureSwitchSettings = ARR_\Module\_CXX_Specs.FeatureSwitchNonMTT;
    FivrConditionPlistParamName = "Patlist";
    TrialParam FlowIndex = __shared__::FlowMatrixSingular.FlowIndex;
    ForwardingMode = ARR_\Module\_CXX_Specs.ForwardingMode_Kill;
    PatternNameCounterIndexes = ARR_\Module\_CXX_Specs.PatternMap;
    PinMap = ARR_\Module\_CXX_Specs.Recovery_PinMap;
    RecoveryMode = "NoRecovery";
    RecoveryTrackingIncoming = ARR_\Module\_CXX_Specs.RecoveryTracker_Incoming;
    RecoveryTrackingOutgoing = ARR_\Module\_CXX_Specs.RecoveryTracker_Outgoing_Speedflow;
    RecoveryOptions = ARR_\Module\_CXX_Specs.Recovery_Options;
    SetPointsPlistParamName = "Patlist";
    SetPointsPostInstance = PSPOST.CR_FMIN;
    SetPointsPreInstance = PSPRE.CR_FMIN+","+"MCdrv:"+ARR_\Module\_CXX_Specs.corefreq+":"+ __shared__::FlowMatrixSingular.CR_FMIN+"GHz,MCdrv:"+ARR_\Module\_CXX_Specs.ringfreq+":"+ __shared__::FlowMatrixSingular.CCF_FMIN+"GHz";
    StartVoltages = __shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE;
    StartVoltagesForRetry = __shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesForRetry , "");
    StartVoltagesOffset = __shared__::QNRTpRuleShared.If_PseudoVminForwarding(__shared__::QNRUsrvShared.StartVoltagesOffset , "");
    StepSize = toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION);
    TestMode = "MultiVmin";
    VoltageConverter = ARR_\Module\_CXX_Specs.VoltageConverter_rail + DROPOUT.CR_FMIN;
    VoltageTargets = ARR_\Module\_CXX_Specs.CORE_NonPMUCS_VoltageTarget;
    TrialResult -2
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -1;
        }
        TrialResult 0
        {
            PassFail Fail;
            TrialAction "Next";
            Return 1;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
            Return 1;
        }
        TrialResult 2
        {
            PassFail Fail;
            TrialAction "Next";
            Return 1;
        }
        TrialResult 3
        {
            PassFail Fail;
            TrialAction "Next";
            Return 1;
        }
        TrialResult 4
        {
            PassFail Fail;
            TrialAction "Next";
            Return 1;
        }
        TrialResult 5
        {
            PassFail Fail;
            TrialAction "Next";
            Return 1;
        }
    }
}

CSharpTest VminTC XSA_\Module\_SB_\RunMode\_VMAXXCR_X_\Domain\A_MAX_X_ALL
{
    Patlist = "IPC::arr_cdie_vmaxxcr_mbist_core_all_all_all_ks_vmax_lfm_x_class_hptp_list";    
    LevelsTc = "IPC::ARR_\Module\_CXX::arr_cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_ARR_MBIST_max_lvl";
    TimingsTc = "IPC::ARR_\Module\_CXX::cpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800";
    #BaseNumbers = \BaseNumber\
    BypassPort = -1;
    DtsConfiguration = ARR_\Module\_Rules.QA_HOT_Default("","nvl_cpu_all_ctv","");
    EndVoltageLimits = __shared__::FlowMatrixSingular.CR_VMAX_VALUE;
    ExecutionMode = "Search";
    FailCaptureCount = toInteger(1);
    FivrCondition = ARR_\Module\_CXX_Specs.FivrConditionNom;
    FeatureSwitchSettings = ARR_\Module\_CXX_Specs.FeatureSwitchMTT;
    FivrConditionPlistParamName = "Patlist";
    ForwardingMode = ARR_\Module\_CXX_Specs.ForwardingMode_Kill;
    LimitGuardband = toString(__shared__::GBVars.LimitGuardband);
    PatternNameCounterIndexes = ARR_\Module\_CXX_Specs.PatternMap;
    PinMap = ARR_\Module\_CXX_Specs.Recovery_PinMap;
    RecoveryMode = ARR_\Module\_CXX_Specs.CORE_RecoveryMode_VMAX;
    RecoveryOptions = ARR_\Module\_CXX_Specs.Recovery_Options;
    RecoveryTrackingIncoming = ARR_\Module\_CXX_Specs.RecoveryTracker_Incoming;
    RecoveryTrackingOutgoing = ARR_\Module\_CXX_Specs.RecoveryTracker_Outgoing;
    SetPointsPlistParamName = "Patlist";
    SetPointsPostInstance = PSPOST.CR_F1 + "," + ARR_\Module\_CXX_Specs.nbl_on;
    SetPointsPreInstance = PSPRE.CR_F1+","+"MCdrv:"+ARR_\Module\_CXX_Specs.corefreq+":"+ __shared__::FlowMatrixSingular.CR_\CORNER\_FREQ+"GHz,MCdrv:"+ARR_\Module\_CXX_Specs.ringfreq+":"+ __shared__::FlowMatrixSingular.CCF_\CORNER\_FREQ+"GHz,"+ARR_\Module\_CXX_Specs.nbl_off;
    StartVoltages = __shared__::FlowMatrixSingular.CR_VMAX_VALUE;
    StepSize = toDouble(0.01);
    TestMode = "Functional";
    VoltageConverter = "--overrides CORE3:"+__shared__::FlowMatrixSingular.CR_VMAX_VALUE+",CORE2:"+__shared__::FlowMatrixSingular.CR_VMAX_VALUE+",CORE1:"+__shared__::FlowMatrixSingular.CR_VMAX_VALUE+",CORE0:"+__shared__::FlowMatrixSingular.CR_VMAX_VALUE+ " --dlvrpins VCCIA --expressions " + DROPOUT.CR_F1;
    VoltageTargets = ARR_\Module\_CXX_Specs.CORE_NonPMUCS_VoltageTarget;
}

CSharpTest DDGShmooTC ARR_\Module\_SHMOO_E_BEGINCPUNOM_X_X_X_X_SHMOO_FOR_DEDC_1
{
    Patlist = "IPC::arr_cdie_\sf\_mbist_core_all_all_all_limiter_\corner\_class_hptp_list_master";    
    LevelsTc = "IPC::ARR_CCF_CXX::arr_cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_ARR_MBIST_nom_lvl";
    TimingsTc = "IPC::ARR_\Module\_CXX::cpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800";
    BypassPort = 1;
    LogLevel = "Enabled";
    PrintFormat = "ShmooHub";
    SetPointsPlistParamName = "Patlist";
    SetPointsPreInstance = "";
    VoltageConverter = "--dlvrpins VCCIA --expressions CORE --fivrcondition NOM_CCF_CORE";
    XAxisType = "SpecSetVariable";
    XAxisParam = "p_all_mts";
    XAxisParamType = "UserDefined";
    XAxisRange = "700e6:50e6:6";
    YAxisParam = "CORE3,CORE2,CORE1,CORE0";
    YAxisParamType = "UserDefined";
    YAxisRange = "0.9:-0.05:12";
    YAxisType = "FIVR";
}



CSharpTest VminTC SSA_\Module\_SB_\RunMode\_ENDCPUNOM_X_\Domain\A_X_X_C6S_RETENTION_ALL
{
    Patlist = "IPC::arr_cdie_endcpunom_mbist_core_pnc_mlcc6s_all_ssa_vccmlc_retention_x_class_hptp_list";    
    LevelsTc = "IPC::ARR_\Module\_CXX::arr_cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_ARR_MBIST_nom_lvl";
    TimingsTc = "IPC::ARR_\Module\_CXX::cpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800";
    BaseNumbers = \BaseNumber\
    BypassPort = -1;
    EndVoltageLimits = "0.825";
    ExecutionMode = "SearchWithScoreboard";
    FivrCondition = ARR_\Module\_CXX_Specs.FivrConditionNom;
    FailCaptureCount = toInteger(1);
    FeatureSwitchSettings = ARR_\Module\_CXX_Specs.FeatureSwitchNonMTT;
    ForwardingMode = ARR_\Module\_CXX_Specs.ForwardingMode_EDC;
    MaxFailsNum = toInteger(20);
    MaxRepetitionCount = 1;
    PatternNameCounterIndexes = ARR_\Module\_CXX_Specs.PatternMap;
    PinMap = ARR_\Module\_CXX_Specs.Recovery_PinMap;
    RecoveryMode = ARR_\Module\_CXX_Specs.Recovery_Mode;
    RecoveryOptions = ARR_\Module\_CXX_Specs.Recovery_Options;
    RecoveryTrackingIncoming = ARR_\Module\_CXX_Specs.RecoveryTracker_Incoming;
    RecoveryTrackingOutgoing = ARR_\Module\_CXX_Specs.RecoveryTracker_Outgoing;
    ScoreboardEdgeTicks = toInteger(0);
    SetPointsPlistParamName = "Patlist";
    SetPointsPostInstance = PSPOST.CR_F1;
    SetPointsPreInstance = PSPRE.CR_F1+","+"MCdrv:"+ARR_\Module\_CXX_Specs.corefreq+":"+ __shared__::FlowMatrixSingular.CR_\CORNER\_FREQ+"GHz,MCdrv:"+ARR_\Module\_CXX_Specs.ringfreq+":"+ __shared__::FlowMatrixSingular.CCF_\CORNER\_FREQ+"GHz," + ARR_\Module\_CXX_Specs.nbl_on;
    StartVoltages = "0.825";
    StepSize = toDouble(0.01);
    TestMode = "Scoreboard";
    VoltageTargets = ARR_\Module\_CXX_Specs.CORE_NonPMUCS_VoltageTarget;
}

CSharpTest VminTC SSA_\Module\_SB_\RunMode\_ENDCPUMAX_X_\Domain\A_MAX_X_PMUCS_ALL
{
    Patlist = "IPC::arr_cdie_endcpumax_mbist_core_pnc_pm_all_ssa_vccinf_ks_x_class_hptp_list";    
    LevelsTc = "IPC::ARR_\Module\_CXX::arr_cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_ARR_MBIST_max_lvl";
    TimingsTc = "IPC::ARR_\Module\_CXX::cpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800";
    BaseNumbers = \BaseNumber\
    BypassPort = 1;
    EndVoltageLimits = "0.825";
    ExecutionMode = "SearchWithScoreboard";
    FivrCondition = ARR_\Module\_CXX_Specs.FivrConditionNom;
    FailCaptureCount = toInteger(1);
    FeatureSwitchSettings = ARR_\Module\_CXX_Specs.FeatureSwitchNonMTT;
    ForwardingMode = ARR_\Module\_CXX_Specs.ForwardingMode_EDC;
    MaxFailsNum = toInteger(20);
    MaxRepetitionCount = 1;
    PatternNameCounterIndexes = ARR_\Module\_CXX_Specs.PatternMap;
    PinMap = ARR_\Module\_CXX_Specs.Recovery_PinMap;
    RecoveryMode = "NoRecovery";
    RecoveryOptions = "";
    RecoveryTrackingIncoming = ARR_\Module\_CXX_Specs.RecoveryTracker_Incoming;
    RecoveryTrackingOutgoing = "";
    ScoreboardEdgeTicks = toInteger(0);
    SetPointsPlistParamName = "Patlist";
    SetPointsPostInstance = PSPOST.\Domain\_\CORNERTOP\ + "," + ARR_\Module\_CXX_Specs.nbl_on;
    SetPointsPreInstance = PSPRE.CR_F1+","+"MCdrv:"+ARR_\Module\_CXX_Specs.corefreq+":"+ __shared__::FlowMatrixSingular.CR_\CORNER\_FREQ+"GHz,MCdrv:"+ARR_\Module\_CXX_Specs.ringfreq+":"+ __shared__::FlowMatrixSingular.CCF_\CORNER\_FREQ+"GHz," + ARR_\Module\_CXX_Specs.nbl_off;
    StartVoltages = "0.825";
    StepSize = toDouble(0.01);
    TestMode = "Scoreboard";
    VoltageTargets = ARR_\Module\_CXX_Specs.CORE_PMUCS_VoltageTarget;
}


CSharpTest VminTC \NOMIP\_\Module\_SB_\RunMode\_BEGINCPUNOM_X_\Domain\A_NOM_X_ALL
{
    Patlist = \NOMPlist\    
    LevelsTc = "IPC::ARR_\Module\_CXX::arr_cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_ARR_MBIST_nom_lvl";
    TimingsTc = "IPC::ARR_\Module\_CXX::cpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800";
    BaseNumbers = \BaseNumber\
    BypassPort = -1;
    EndVoltageLimits = "0.825";
    ExecutionMode = "SearchWithScoreboard";
    FivrCondition = ARR_\Module\_CXX_Specs.FivrConditionNom;
    FailCaptureCount = toInteger(1);
    FeatureSwitchSettings = ARR_\Module\_CXX_Specs.FeatureSwitchNonMTT;
    ForwardingMode = ARR_\Module\_CXX_Specs.ForwardingMode_Kill;
    MaxFailsNum = toInteger(20);
    MaxRepetitionCount = 1;
    PatternNameCounterIndexes = ARR_\Module\_CXX_Specs.PatternMap;
    PinMap = ARR_\Module\_CXX_Specs.Recovery_PinMap;
    RecoveryMode = ARR_\Module\_CXX_Specs.Recovery_Mode;
    RecoveryOptions = ARR_\Module\_CXX_Specs.Recovery_Options;
    RecoveryTrackingIncoming = ARR_\Module\_CXX_Specs.RecoveryTracker_Incoming;
    RecoveryTrackingOutgoing = ARR_\Module\_CXX_Specs.RecoveryTracker_Outgoing;
    ScoreboardEdgeTicks = toInteger(0);
    SetPointsPlistParamName = "Patlist";
    SetPointsPostInstance = PSPOST.CR_F1;
    SetPointsPreInstance = PSPRE.CR_F1+","+"MCdrv:"+ARR_\Module\_CXX_Specs.corefreq+":"+ __shared__::FlowMatrixSingular.CR_F2_FREQ+"GHz,MCdrv:"+ARR_\Module\_CXX_Specs.ringfreq+":"+ __shared__::FlowMatrixSingular.CCF_F2_FREQ+"GHz," + ARR_\Module\_CXX_Specs.nbl_on;
    StartVoltages = "0.825";
    StepSize = toDouble(0.01);
    TestMode = "Scoreboard";
    VoltageTargets = ARR_\Module\_CXX_Specs.CORE_NonPMUCS_VoltageTarget;
}


CSharpTest PrimePatConfigTestMethod ALL_\Module\_PATMOD_\RunMode\_FMINXCR_X_X_X_X_RATIO4_DISABLE_FMIN
{
	BypassPort = -1;
	ConfigurationFile = GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "/Modules/ARR/ARR_\Module\_CXX/InputFiles/fmin_resetovr.setpoints.json";
	SetPoint = "enable_fmin_400_throttle_done_detected_core";
}

CSharpTest PrimePatConfigTestMethod ALL_\Module\_PATMOD_\RunMode\_FMINXCR_X_X_X_X_RATIO4_ENABLE_FMIN
{
	BypassPort = -1;
	ConfigurationFile = GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "/Modules/ARR/ARR_\Module\_CXX/InputFiles/fmin_resetovr.setpoints.json";
	SetPoint = "disable_fmin_400_throttle_done_detected_core";

}



MultiTrialTest XSA_\Module\_VMAX_\RunMode\_VMAXXCR_X_\Domain\A_\CORNERTOP\_X_FREQ_\SPLITCORE\_MTT
{
    TrialVariable CPU_TRIALS::FlowDomain.CORE_TOP;
	TrialVariableExitAction "Continue";
	CSharpTrialTest VminTC "XSA_\Module\_VMAX_\RunMode\_VMAXXCR_X_\Domain\A_" + __shared__::CORNERs.\Domain\_\FlowMatrixTOP\ + "_X_\SPLITCORE\"
    {
         Patlist = "IPC::arr_cdie_vmaxxcr_mbist_core_all_all_all_ks_vmax_tfm_x_class_hptp_list";
         LevelsTc = "IPC::ARR_\Module\_CXX::arr_cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_ARR_MBIST_max_lvl";
         TimingsTc = "IPC::ARR_\Module\_CXX::cpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800";
         #BaseNumbers = \BaseNumber\
         BypassPort = -1;
         DtsConfiguration = ARR_\Module\_Rules.QA_HOT_Default("","nvl_cpu_all_ctv","");
         EndVoltageLimits = __shared__::FlowMatrixSingular.CR_VMAX_VALUE;
         FailCaptureCount = toInteger(1);
         FeatureSwitchSettings = ARR_\Module\_CXX_Specs.FeatureSwitchMTT;
         FivrCondition = ARR_\Module\_CXX_Specs.FivrConditionNom;
         FivrConditionPlistParamName = "Patlist";
         FlowIndex = __shared__::FlowMatrixSingular.FlowIndex;
         ForwardingMode = ARR_\Module\_CXX_Specs.ForwardingMode_Kill;
         LimitGuardband = toString(__shared__::GBVars.LimitGuardband);
         InitialMaskBits = "1100";
         MaskPins = \MaskPins\
         PatternNameCounterIndexes = ARR_\Module\_CXX_Specs.PatternMap;
         PinMap = ARR_\Module\_CXX_Specs.Recovery_PinMap;
         PrintPatternsOccurrences = "No";
         RecoveryMode = "NoRecovery";
         RecoveryOptions = "";
         RecoveryTrackingIncoming = ARR_\Module\_CXX_Specs.RecoveryTracker_Incoming;
         RecoveryTrackingOutgoing = "";
         SetPointsPlistParamName = "Patlist";
         ScoreboardEdgeTicks = 0;
         ScoreboardPerPatternFails = 1;
         SetPointsPostInstance = PSPOST.\Domain\_\CORNERTOP\;
         TrialParam SetPointsPreInstance = PSPRE.\Domain\_\CORNERTOP\+","+"MCdrv:corefreq2:"+"0.8GHz,"+"MCdrv:corefreq3:"+"0.8GHz,"+"MCdrv:corefreq1:"+ __shared__::FreqValues.\Domain\_\FlowMatrixTOP\+"GHz,"+"MCdrv:corefreq0:"+ __shared__::FreqValues.\Domain\_\FlowMatrixTOP\+"GHz,MCdrv:"+ARR_\Module\_CXX_Specs.ringfreq+":"+ __shared__::FreqValues.CCF_C5+"GHz,"+ARR_\Module\_CXX_Specs.nbl_off;
         StartVoltages = __shared__::FlowMatrixSingular.CR_VMAX_VALUE;
         StepSize = toDouble(__shared__::FlowMatrixSingular.CR_SEARCH_RESOLUTION);
         TestMode = "Functional";
         ExecutionMode = "Search";
         MaxFailsNum = 0;
         MaxRepetitionCount = 0;
         EnableScoreboardOnMonitorOnly = "False";   
         VoltageConverter = "--overrides CORE3:"+__shared__::FlowMatrixSingular.CR_VMAX_VALUE+",CORE2:"+__shared__::FlowMatrixSingular.CR_VMAX_VALUE+",CORE1:"+__shared__::FlowMatrixSingular.CR_VMAX_VALUE+",CORE0:"+__shared__::FlowMatrixSingular.CR_VMAX_VALUE+ " --dlvrpins VCCIA --expressions " + DROPOUT.\Domain\_\CORNERTOP\;
         VoltageTargets = ARR_\Module\_CXX_Specs.CORE_NonPMUCS_VoltageTarget;
       TrialResult -2
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction "Exit";
            Return -1;
        }
        TrialResult 0
        {
            PassFail Fail;
            TrialAction "Exit";
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction "Exit";
            Return 1;
        }
        TrialResult 2
        {
            PassFail Fail;
            TrialAction "Exit";
            Return 0;
        }
        TrialResult 3
        {
            PassFail Fail;
            TrialAction "Exit";
            Return 0;
        }
        TrialResult 4
        {
            PassFail Fail;
            TrialAction "Exit";
            Return 0;
        }
        TrialResult 5
        {
            PassFail Fail;
            TrialAction "Exit";
            Return 0;
        }
    }
}






CSharpTest ApexTC XSA_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_X_X_\SPLITCORE\_APEX_FMAX
{
    Patlist = "IPC::arr_cdie_\sftop\_mbist_core_all_all_all_limiter_\cornertop\_class_hptp_list_master";    
    LevelsTc = "IPC::ARR_\Module\_CXX::arr_cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_ARR_MBIST_min_lvl";
    TimingsTc = "IPC::ARR_\Module\_CXX::cpu_fun_timing_mts800_tstprtclk400_tck100_pncarrmts800";
    BypassPort = 1;
    End = __shared__::FlowMatrixSingular.APEX_\Module\_MIN;
    ExportTokens = "FXCRC3,FXCRC2,FXCRC1,FXCRC0";
    FivrCondition = ARR_\Module\_CXX_Specs.FivrConditionNom;
    FivrConditionPlistParamName = "Patlist";
    ForwardingMode = ARR_\Module\_CXX_Specs.ForwardingMode_EDC;
    InitialMaskBits = "1100";
    MaskPins = \MaskPins\
    PatternNameCounterIndexes = ARR_\Module\_CXX_Specs.PatternMap;
    PinMap = ARR_\Module\_CXX_Specs.Recovery_PinMap;
    RecoveryOptions = ARR_\Module\_CXX_Specs.Recovery_Options_Speedflow;
    RecoveryTracking = ARR_\Module\_CXX_Specs.RecoveryTracker_Incoming;
    SetPointsPostInstance = PSPOST.\Domain\_\CORNERTOP\+",CORE:nblctrl_core_l2:nblon";
    SetPointsPreInstance = PSPRE.\Domain\_\CORNERTOP\+","+"MCdrv:"+ARR_\Module\_CXX_Specs.corefreq+":"+ __shared__::FlowMatrixSingular.CR_\CORNER\_FREQ+"GHz,MCdrv:"+ARR_\Module\_CXX_Specs.ringfreq+":"+ __shared__::FlowMatrixSingular.CCF_\CORNER\_FREQ+"GHz,CORE:nblctrl_core_l2:nbloff";
    Start = __shared__::FlowMatrixSingular.APEX_\Module\_MAX;
    StepSize = toInteger(1);
    Targets = "ACORE3,ACORE2,ACORE1,ACORE0";
    VoltageConverter = "--overrides CORE1:"+__shared__::FlowMatrixSingular.CR_VMAX_VALUE+",CORE0:"+__shared__::FlowMatrixSingular.CR_VMAX_VALUE+ " --dlvrpins VCCIA --expressions " + DROPOUT.\Domain\_\CORNERTOP\;
}


CSharpTest RunCallback XSA_\Module\_RUNCALLBACK_\RunMode\_INIT_X_X_X_X_APEXTC
{
    BypassPort = -1;
    Callback = "ReadFrequencyPatConfigFile";
    Parameters = GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "./Modules/ARR/ARR_\Module\_CXX/InputFiles/ApexTC_Input_Config.json";
} # End of Test Counter Definition

############






CSharpTest VminTC SSA_\Module\_\Type\_\RunMode\_BEGINCPUNOM_X_\Domain\A_MIN_X_DUMMY
{
    Patlist = "IPC::resetplb_8axx080808_phase2_all_MCarr_CA2P_hdmt2_hvm_list";
    LevelsTc = "IPC::CPU_IP_BASE::cpu_all_bf_x_x_ipc_lvl_nom";
    TimingsTc = "IPC::CPU_IP_BASE::cpu_fun_timing_mts800_tstprtclk400_tck100";
    BaseNumbers = \BaseNumber\
    BypassPort = -1;
    EndVoltageLimits = "0.825";
    ExecutionMode = "SearchWithScoreboard";
    FivrCondition = ARR_\Module\_CXX_Specs.FivrConditionNom;
    FailCaptureCount = toInteger(1);
    FeatureSwitchSettings = ARR_\Module\_CXX_Specs.FeatureSwitchNonMTT;
    ForwardingMode = ARR_\Module\_CXX_Specs.ForwardingMode_EDC;
    MaxFailsNum = toInteger(20);
    MaxRepetitionCount = 1;
    PatternNameCounterIndexes = ARR_\Module\_CXX_Specs.PatternMap;
    PinMap = "";
    RecoveryMode = "NoRecovery";
    RecoveryOptions = "";
    RecoveryTrackingIncoming = "";
    RecoveryTrackingOutgoing = "";
    ScoreboardEdgeTicks = toInteger(0);
    SetPointsPlistParamName = "Patlist";
    SetPointsPreInstance = "MCdrv:"+ARR_\Module\_CXX_Specs.corefreq+":"+ __shared__::FlowMatrixSingular.CR_F2_FREQ+"GHz,MCdrv:"+ARR_\Module\_CXX_Specs.ringfreq+":"+ __shared__::FlowMatrixSingular.CCF_F2_FREQ+"GHz," + ARR_\Module\_CXX_Specs.nbl_off;
    StartVoltages = "0.825";
    StepSize = toDouble(0.01);
    TestMode = "Scoreboard";
    VoltageTargets = ARR_\Module\_CXX_Specs.CORE_PMUCS_VoltageTarget;
}

CSharpTest PrimePatConfigTestMethod ALL_\Module\_PATMOD_\RunMode\_BEGINCPUNOM_X_X_X_X_RATIO4_ENABLE_FMIN
{
	BypassPort = -1;
	ConfigurationFile = GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "/Modules/ARR/ARR_\Module\_CXX/InputFiles/fmin_resetovr.setpoints.json";
	SetPoint = "disable_fmin_400_throttle_done_detected_core";

}

##### Flow #####
Flow ARR_\Module\_CXX_INIT 
{

    FlowItem XSA_\Module\_RUNCALLBACK_\RunMode\_INIT_X_X_X_X_APEXTC XSA_\Module\_RUNCALLBACK_\RunMode\_INIT_X_X_X_X_APEXTC
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90601700_fail_ARR_\Module\_CXX_XSA_\Module\_RUNCALLBACK_\RunMode\_INIT_X_X_X_X_APEXTC;
            
            Return 0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }
}

Flow ARR_\Module\_CXX_\SF\ @\SF\_SubFlow
{
    FlowItem XSA_\Module\_\Type\_\RunMode\_\SF\_X_\Domain\A_\CORNER\_MTT XSA_\Module\_\Type\_\RunMode\_\SF\_X_\Domain\A_\CORNER\_MTT
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90601000_fail_ARR_\Module\_CXX_XSA_\Module\_\Type\_\RunMode\_\SF\_X_\Domain\A_\CORNER\_MTT;
            
			Return 0;
        }
        Result 1
        {
            Property PassFail = "Pass";
			GoTo ROM_\Module\_\Type\_\RunMode\_\SF\_X_\Domain\A_\CORNER\_MTT;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90601000_fail_ARR_\Module\_CXX_XSA_\Module\_\Type\_\RunMode\_\SF\_X_\Domain\A_\CORNER\_MTT;
            
            Return 0;
        }
        Result 3
        {
            Property PassFail = "Pass";
            #SetBin b90601000_fail_ARR_\Module\_CXX_XSA_\Module\_\Type\_\RunMode\_\SF\_X_\Domain\A_\CORNER\_MTT;
            
			GoTo ROM_\Module\_\Type\_\RunMode\_\SF\_X_\Domain\A_\CORNER\_MTT;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b90976018_fail_PTH_DTS_XXX_ARR_\Module\_CXX_THERMAL_PORT4_SHARED_BIN;
            
            Return 0;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b90611920_fail_ARR_\Module\_CXX_RESET_PORT5_SHARED_BIN;
            
            Return 0;
        }
    }
    FlowItem ROM_\Module\_\Type\_\RunMode\_\SF\_X_\Domain\A_\CORNER\_MTT ROM_\Module\_\Type\_\RunMode\_\SF\_X_\Domain\A_\CORNER\_MTT @EDC
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90601000_fail_ARR_\Module\_CXX_XSA_\Module\_\Type\_\RunMode\_\SF\_X_\Domain\A_\CORNER\_MTT;
            
			Return 1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90601000_fail_ARR_\Module\_CXX_XSA_\Module\_\Type\_\RunMode\_\SF\_X_\Domain\A_\CORNER\_MTT;
            
            Return 1;
        }
        Result 3
        {
            Property PassFail = "Pass";
            #SetBin b90601000_fail_ARR_\Module\_CXX_XSA_\Module\_\Type\_\RunMode\_\SF\_X_\Domain\A_\CORNER\_MTT;
            
            Return 1;
        }
        Result 4
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90976018_fail_PTH_DTS_XXX_ARR_\Module\_CXX_THERMAL_PORT4_SHARED_BIN;
            
            Return 1;
        }
        Result 5
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90611920_fail_ARR_\Module\_CXX_RESET_PORT5_SHARED_BIN;
            
            Return 1;
        }
    }  
}



Flow ARR_\Module\_FMAX
{
    FlowItem XSA_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_X_X_ALL_APEX_FMAX XSA_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_X_X_ALL_APEX_FMAX @EDC
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90600400_fail_ARR_\Module\_CXX_XSA_\Module\_\Type\_\RunMode\_\SF\_X_\Domain\A_\CORNER\_3600_ALL_APEX_MTT;
            
			GoTo XSA_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_X_X_C0C1_APEX_FMAX;
        }
        Result 1
        {
            Property PassFail = "Pass";
			GoTo XSA_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_X_X_C0C1_APEX_FMAX;
        }
        Result 2
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90600400_fail_ARR_\Module\_CXX_XSA_\Module\_\Type\_\RunMode\_\SF\_X_\Domain\A_\CORNER\_3600_ALL_APEX_MTT;
            
			GoTo XSA_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_X_X_C0C1_APEX_FMAX;
        }
        Result 3
        {
            Property PassFail = "Pass";
			GoTo XSA_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_X_X_C0C1_APEX_FMAX;
        }
        Result 4
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90976018_fail_PTH_DTS_XXX_ARR_\Module\_CXX_THERMAL_PORT4_SHARED_BIN;
            
			GoTo XSA_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_X_X_C0C1_APEX_FMAX;
        }
        Result 5
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90611920_fail_ARR_\Module\_CXX_RESET_PORT5_SHARED_BIN;
            
			GoTo XSA_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_X_X_C0C1_APEX_FMAX;
        }
    }
    FlowItem XSA_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_X_X_C0C1_APEX_FMAX XSA_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_X_X_C0C1_APEX_FMAX @EDC
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90600400_fail_ARR_\Module\_CXX_XSA_\Module\_\Type\_\RunMode\_\SF\_X_\Domain\A_\CORNER\_3600_ALL_APEX_MTT;
            
			GoTo XSA_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_X_X_C2C3_APEX_FMAX;
        }
        Result 1
        {
            Property PassFail = "Pass";
			GoTo XSA_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_X_X_C2C3_APEX_FMAX;
        }
        Result 2
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90600400_fail_ARR_\Module\_CXX_XSA_\Module\_\Type\_\RunMode\_\SF\_X_\Domain\A_\CORNER\_3600_ALL_APEX_MTT;
            
			GoTo XSA_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_X_X_C2C3_APEX_FMAX;
        }
        Result 3
        {
            Property PassFail = "Pass";
            GoTo XSA_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_X_X_C2C3_APEX_FMAX;
        }
        Result 4
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90976018_fail_PTH_DTS_XXX_ARR_\Module\_CXX_THERMAL_PORT4_SHARED_BIN;
            
			GoTo XSA_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_X_X_C2C3_APEX_FMAX;
        }
        Result 5
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90611920_fail_ARR_\Module\_CXX_RESET_PORT5_SHARED_BIN;
            
			GoTo XSA_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_X_X_C2C3_APEX_FMAX;
        }
    }
    FlowItem XSA_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_X_X_C2C3_APEX_FMAX XSA_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_X_X_C2C3_APEX_FMAX @EDC
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90600400_fail_ARR_\Module\_CXX_XSA_\Module\_\Type\_\RunMode\_\SF\_X_\Domain\A_\CORNER\_3600_ALL_APEX_MTT;
            
			Return 1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90600400_fail_ARR_\Module\_CXX_XSA_\Module\_\Type\_\RunMode\_\SF\_X_\Domain\A_\CORNER\_3600_ALL_APEX_MTT;
            
            Return 1;
        }
        Result 3
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 4
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90976018_fail_PTH_DTS_XXX_ARR_\Module\_CXX_THERMAL_PORT4_SHARED_BIN;
            
            Return 1;
        }
        Result 5
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90611920_fail_ARR_\Module\_CXX_RESET_PORT5_SHARED_BIN;
            
            Return 1;
        }
    }
    
}
Flow ARR_\Module\_CXX_F5XCR @F5XCR_SubFlow
{
    FlowItem ARR_\Module\_FMAX ARR_\Module\_FMAX
    {
        Result -2
        {
            Property PassFail = "Fail";
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            Return 0;
        }
        Result 1
        {
            Property PassFail = "Pass";
			GoTo XSA_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_\CORNERTOP\_C0C1_MTT;
        }
    }
    
    FlowItem XSA_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_\CORNERTOP\_C0C1_MTT XSA_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_\CORNERTOP\_C0C1_MTT
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90601400_fail_ARR_\Module\_CXX_XSA_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_\CORNERTOP\_C0C1_MTT;
            
            Return 0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo XSA_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_\CORNERTOP\_C2C3_MTT;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90601400_fail_ARR_\Module\_CXX_XSA_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_\CORNERTOP\_C0C1_MTT;
            
            Return 0;
        }
        Result 3
        {
            Property PassFail = "Pass";
			GoTo XSA_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_\CORNERTOP\_C2C3_MTT;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b90976018_fail_PTH_DTS_XXX_ARR_\Module\_CXX_THERMAL_PORT4_SHARED_BIN;
            
            Return 0;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b90611920_fail_ARR_\Module\_CXX_RESET_PORT5_SHARED_BIN;
            
            Return 0;
        }
    }
    
    FlowItem XSA_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_\CORNERTOP\_C2C3_MTT XSA_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_\CORNERTOP\_C2C3_MTT
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90601500_fail_ARR_\Module\_CXX_XSA_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_\CORNERTOP\_C2C3_MTT;
            
            Return 0;
        }
        Result 1
        {
            Property PassFail = "Pass";
			GoTo ROM_\Module\_\Type\_\RunMode\_\SF\_X_\Domain\A_\CORNER\_MTT;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90601500_fail_ARR_\Module\_CXX_XSA_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_\CORNERTOP\_C2C3_MTT;
            
            Return 0;
        }
        Result 3
        {
            Property PassFail = "Pass";
			GoTo ROM_\Module\_\Type\_\RunMode\_\SF\_X_\Domain\A_\CORNER\_MTT;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b90976018_fail_PTH_DTS_XXX_ARR_\Module\_CXX_THERMAL_PORT4_SHARED_BIN;
            
            Return 0;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b90611920_fail_ARR_\Module\_CXX_RESET_PORT5_SHARED_BIN;
            
            Return 0;
        }
    }
    
    FlowItem XSA_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_\CORNERTOP\_MTT XSA_\Module\_\Type\_\RunMode\_\SF\_X_\Domain\A_\CORNER\_MTT
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90601600_fail_ARR_\Module\_CXX_XSA_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_\CORNERTOP\_MTT;
            
            Return 0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 0;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90601600_fail_ARR_\Module\_CXX_XSA_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_\CORNERTOP\_MTT;
            
            Return 0;
        }
        Result 3
        {
            Property PassFail = "Fail";
            SetBin b90601600_fail_ARR_\Module\_CXX_XSA_\Module\_\Type\_\RunMode\_\SF\_X_\Domain\A_\CORNER\_MTT;
            
            Return 0;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b90976018_fail_PTH_DTS_XXX_ARR_\Module\_CXX_THERMAL_PORT4_SHARED_BIN;
            
            Return 0;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b90611920_fail_ARR_\Module\_CXX_RESET_PORT5_SHARED_BIN;
            
            Return 0;
        }
    }
    
    FlowItem ROM_\Module\_\Type\_\RunMode\_\SF\_X_\Domain\A_\CORNER\_MTT ROM_\Module\_\Type\_\RunMode\_\SF\_X_\Domain\A_\CORNER\_MTT @EDC
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90601600_fail_ARR_\Module\_CXX_XSA_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_\CORNERTOP\_MTT;
            
            Return 1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90601600_fail_ARR_\Module\_CXX_XSA_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_\CORNERTOP\_MTT;
            
            Return 1;
        }
        Result 3
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90601600_fail_ARR_\Module\_CXX_XSA_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_\CORNERTOP\_MTT;
            
            Return 1;
        }
        Result 4
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90976018_fail_PTH_DTS_XXX_ARR_\Module\_CXX_THERMAL_PORT4_SHARED_BIN;
            
            Return 1;
        }
        Result 5
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90611920_fail_ARR_\Module\_CXX_RESET_PORT5_SHARED_BIN;
            
            Return 1;
        }
    }
    
}

Flow ARR_\Module\_CXX_FMINXCR @FMINXCR_SubFlow
{
    FlowItem ALL_\Module\_PATMOD_\RunMode\_FMINXCR_X_X_X_X_RATIO4_DISABLE_FMIN ALL_\Module\_PATMOD_\RunMode\_FMINXCR_X_X_X_X_RATIO4_DISABLE_FMIN @EDC
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90600600_fail_ARR_\Module\_CXX_XSA_\Module\_\Type\_\RunMode\_FMINXCR_X_\Domain\A_FMIN_0400_ALL;
            
            GoTo XSA_\Module\_SB_\RunMode\_FMINXCR_X_\Domain\A_FMIN_MTT;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo XSA_\Module\_SB_\RunMode\_FMINXCR_X_\Domain\A_FMIN_MTT;
        }
 
    }

    FlowItem XSA_\Module\_SB_\RunMode\_FMINXCR_X_\Domain\A_FMIN_MTT XSA_\Module\_SB_\RunMode\_FMINXCR_X_\Domain\A_FMIN_MTT
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90600600_fail_ARR_\Module\_CXX_XSA_\Module\_\Type\_\RunMode\_FMINXCR_X_\Domain\A_FMIN_0400_ALL;
            
            Return 0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo ALL_\Module\_PATMOD_\RunMode\_FMINXCR_X_X_X_X_RATIO4_ENABLE_FMIN;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90600600_fail_ARR_\Module\_CXX_XSA_\Module\_\Type\_\RunMode\_FMINXCR_X_\Domain\A_FMIN_0400_ALL;
            
			Return 0;
        }
        Result 3
        {
            Property PassFail = "Fail";
            
            Return 0;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b90976018_fail_PTH_DTS_XXX_ARR_\Module\_CXX_THERMAL_PORT4_SHARED_BIN;
            
			Return 0;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b90611920_fail_ARR_\Module\_CXX_RESET_PORT5_SHARED_BIN;
            
			Return 0;
        }
    }
    FlowItem ALL_\Module\_PATMOD_\RunMode\_FMINXCR_X_X_X_X_RATIO4_ENABLE_FMIN ALL_\Module\_PATMOD_\RunMode\_FMINXCR_X_X_X_X_RATIO4_ENABLE_FMIN @EDC
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90600600_fail_ARR_\Module\_CXX_XSA_\Module\_\Type\_\RunMode\_FMINXCR_X_\Domain\A_FMIN_0400_ALL;
            
            Return 1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }
    
}

Flow ARR_\Module\_CXX_VMAXXCR @VMAXXCR_SubFlow
{
    
    FlowItem XSA_\Module\_SB_\RunMode\_VMAXXCR_X_\Domain\A_MAX_X_ALL XSA_\Module\_SB_\RunMode\_VMAXXCR_X_\Domain\A_MAX_X_ALL
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90600800_fail_ARR_\Module\_CXX_XSA_\Module\_SB_\RunMode\_VMAXXCR_X_\Domain\A_MAX_X_ALL;
            
            Return 0;
        }
        Result 1
        {
            Property PassFail = "Pass";
			GoTo XSA_\Module\_VMAX_\RunMode\_VMAXXCR_X_\Domain\A_\CORNER\_X_FREQ_C0C1_MTT;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90600800_fail_ARR_\Module\_CXX_XSA_\Module\_SB_\RunMode\_VMAXXCR_X_\Domain\A_MAX_X_ALL;
            
            Return 0;
        }
        Result 3
        {
            Property PassFail = "Pass";
			GoTo XSA_\Module\_VMAX_\RunMode\_VMAXXCR_X_\Domain\A_\CORNER\_X_FREQ_C0C1_MTT;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b90976018_fail_PTH_DTS_XXX_ARR_\Module\_CXX_THERMAL_PORT4_SHARED_BIN;
            
            Return 0;
        }

        Result 5
        {
            Property PassFail = "Fail";
            SetBin b90611920_fail_ARR_\Module\_CXX_RESET_PORT5_SHARED_BIN;
            
            Return 0;
        }
    }
    

    FlowItem XSA_\Module\_VMAX_\RunMode\_VMAXXCR_X_\Domain\A_\CORNER\_X_FREQ_C0C1_MTT XSA_\Module\_VMAX_\RunMode\_VMAXXCR_X_\Domain\A_\CORNER\_X_FREQ_C0C1_MTT
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90601800_fail_ARR_\Module\_CXX_XSA_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_\CORNERTOP\_C0C1_MTT;
            
            Return 0;
			
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo XSA_\Module\_VMAX_\RunMode\_VMAXXCR_X_\Domain\A_\CORNER\_X_FREQ_C2C3_MTT;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90601800_fail_ARR_\Module\_CXX_XSA_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_\CORNERTOP\_C0C1_MTT;
            
            Return 0;
			
        }
        Result 3
        {
            Property PassFail = "Fail";
            SetBin b90601800_fail_ARR_\Module\_CXX_XSA_\Module\_\Type\_\RunMode\_\SFTOP\_X_\Domain\A_\CORNERTOP\_C0C1_MTT;
            
            Return 0;
			
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b90976018_fail_PTH_DTS_XXX_ARR_\Module\_CXX_THERMAL_PORT4_SHARED_BIN;
            
            Return 0;
			
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b90611920_fail_ARR_\Module\_CXX_RESET_PORT5_SHARED_BIN;
            
            Return 0;
			
        }
    }
    
    FlowItem XSA_\Module\_VMAX_\RunMode\_VMAXXCR_X_\Domain\A_\CORNER\_X_FREQ_C2C3_MTT XSA_\Module\_VMAX_\RunMode\_VMAXXCR_X_\Domain\A_\CORNER\_X_FREQ_C2C3_MTT
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90602000_fail_ARR_\Module\_CXX_XSA_\Module\_VMAX_\RunMode\_VMAXXCR_X_\Domain\A_\CORNER\_X_FREQ_C2C3_MTT;
            
            Return 0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90602000_fail_ARR_\Module\_CXX_XSA_\Module\_VMAX_\RunMode\_VMAXXCR_X_\Domain\A_\CORNER\_X_FREQ_C2C3_MTT;
            
            Return 0;
        }
        Result 3
        {
            Property PassFail = "Fail";
            SetBin b90602000_fail_ARR_\Module\_CXX_XSA_\Module\_VMAX_\RunMode\_VMAXXCR_X_\Domain\A_\CORNER\_X_FREQ_C2C3_MTT;
            
            Return 0;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b90976018_fail_PTH_DTS_XXX_ARR_\Module\_CXX_THERMAL_PORT4_SHARED_BIN;
            
            Return 0;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b90611920_fail_ARR_\Module\_CXX_RESET_PORT5_SHARED_BIN;
            
            Return 0;
        }
    }
    
}


Flow ARR_\Module\_CXX_BEGINCPUNOM
{
    FlowItem ALL_\Module\_PATMOD_\RunMode\_BEGINCPUNOM_X_X_X_X_RATIO4_ENABLE_FMIN ALL_\Module\_PATMOD_\RunMode\_BEGINCPUNOM_X_X_X_X_RATIO4_ENABLE_FMIN @EDC
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90600600_fail_ARR_\Module\_CXX_XSA_\Module\_\Type\_\RunMode\_FMINXCR_X_\Domain\A_FMIN_0400_ALL;
            
			GoTo SSA_\Module\_\Type\_\RunMode\_BEGINCPUNOM_X_\Domain\A_MIN_X_DUMMY;
        }
        Result 1
        {
            Property PassFail = "Pass";
			GoTo SSA_\Module\_\Type\_\RunMode\_BEGINCPUNOM_X_\Domain\A_MIN_X_DUMMY;
        }
    }

    FlowItem SSA_\Module\_\Type\_\RunMode\_BEGINCPUNOM_X_\Domain\A_MIN_X_DUMMY SSA_\Module\_\Type\_\RunMode\_BEGINCPUNOM_X_\Domain\A_MIN_X_DUMMY @EDC
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            
			GoTo VMAX_REPAIR;
        }
        Result 1
        {
            Property PassFail = "Pass";
			GoTo VMAX_REPAIR;
        }
        Result 2
        {
            Property PassFail = "Fail";
            
			GoTo VMAX_REPAIR;
        }
        Result 3
        {
            Property PassFail = "Fail";
            
			GoTo VMAX_REPAIR;
        }
        Result 4
        {
            Property PassFail = "Fail";
            
			GoTo VMAX_REPAIR;
        }
        Result 5
        {
            Property PassFail = "Fail";
            
			GoTo VMAX_REPAIR;
        }
    }
    FlowItem ARR_\Module\_SHMOO_E_BEGINCPUNOM_X_X_X_X_SHMOO_FOR_DEDC_1 ARR_\Module\_SHMOO_E_BEGINCPUNOM_X_X_X_X_SHMOO_FOR_DEDC_1 @EDC
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            Return 1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }
    FlowItem ROM_\Module\_SB_\RunMode\_BEGINCPUNOM_X_\Domain\A_NOM_X_ALL ROM_\Module\_SB_\RunMode\_BEGINCPUNOM_X_\Domain\A_NOM_X_ALL
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90200100_fail_ARR_\Module\_CXX_SSA_ROM_\Module\_SB_\RunMode\_BEGINCPUNOM_X_\Domain\A_NOM_X_ALL;
            
			Return 0;
        }
        Result 1
        {
            Property PassFail = "Pass";
			GoTo LSA_\Module\_SB_\RunMode\_BEGINCPUNOM_X_\Domain\A_NOM_X_MEURSINT;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90200100_fail_ARR_\Module\_CXX_SSA_ROM_\Module\_SB_\RunMode\_BEGINCPUNOM_X_\Domain\A_NOM_X_ALL;
            
			Return 0;
        }
        Result 3
        {
            Property PassFail = "Pass";
			GoTo LSA_\Module\_SB_\RunMode\_BEGINCPUNOM_X_\Domain\A_NOM_X_MEURSINT;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b90976018_fail_PTH_DTS_XXX_ARR_\Module\_CXX_THERMAL_PORT4_SHARED_BIN;
            
			Return 0;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b90611920_fail_ARR_\Module\_CXX_RESET_PORT5_SHARED_BIN;
            
			Return 0;
        }
    }
    FlowItem LSA_\Module\_SB_\RunMode\_BEGINCPUNOM_X_\Domain\A_NOM_X_MEURSINT LSA_\Module\_SB_\RunMode\_BEGINCPUNOM_X_\Domain\A_NOM_X_MEURSINT @EDC
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            
            Return 1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            
            Return 1;
        }
        Result 3
        {
            Property PassFail = "Fail";
            
            Return 1;
        }
        Result 4
        {
            Property PassFail = "Fail";
            
            Return 1;
        }
        Result 5
        {
            Property PassFail = "Fail";
            
            Return 1;
        }
    }
    FlowItem XSA_\Module\_SB_\RunMode\_BEGINCPUNOM_X_\Domain\A_NOM_X_ALL XSA_\Module\_SB_\RunMode\_BEGINCPUNOM_X_\Domain\A_NOM_X_ALL
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90200500_fail_ARR_\Module\_CXX_XSA_\Module\_SB_\RunMode\_BEGINCPUNOM_X_\Domain\A_NOM_X_ALL;
            
            Return 0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo ROM_\Module\_SB_\RunMode\_BEGINCPUNOM_X_\Domain\A_NOM_X_ALL;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90200500_fail_ARR_\Module\_CXX_XSA_\Module\_SB_\RunMode\_BEGINCPUNOM_X_\Domain\A_NOM_X_ALL;
            
            Return 0;
        }
        Result 3
        {
            Property PassFail = "Pass";
            #SetBin b90200500_fail_ARR_\Module\_CXX_XSA_\Module\_SB_\RunMode\_BEGINCPUNOM_X_\Domain\A_NOM_X_ALL;
            #
            GoTo ROM_\Module\_SB_\RunMode\_BEGINCPUNOM_X_\Domain\A_NOM_X_ALL;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b90976018_fail_PTH_DTS_XXX_ARR_\Module\_CXX_THERMAL_PORT4_SHARED_BIN;
            
            Return 0;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b90611920_fail_ARR_\Module\_CXX_RESET_PORT5_SHARED_BIN;
            
            Return 0;
        }
    }
    
	FlowItem ALL_\Module\_X_E_BEGINCPUNOM_X_X_X_X_X_X_MBIST_DFF_WRITE_VMIN ALL_\Module\_X_E_BEGINCPUNOM_X_X_X_X_X_X_MBIST_DFF_WRITE_VMIN @EDC
	{
		Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
		Result 0
		{
			Property PassFail = "Fail";
			
			GoTo NOM_REPAIR;
		}
		Result 1
		{
			Property PassFail = "Pass";
			GoTo NOM_REPAIR;
		}
		Result 2
		{
			Property PassFail = "Pass";
			GoTo NOM_REPAIR;
		}
        Result 3
		{
			Property PassFail = "Pass";
			GoTo NOM_REPAIR;
		}
        Result 4
		{
			Property PassFail = "Pass";
			GoTo NOM_REPAIR;
		}
        Result 5
		{
			Property PassFail = "Fail";
			
			GoTo NOM_REPAIR;
		}
        Result 6
		{
			Property PassFail = "Fail";
			
			GoTo NOM_REPAIR;
		}
        Result 7
		{
			Property PassFail = "Fail";
			
			GoTo NOM_REPAIR;

		}
        Result 8
		{
			Property PassFail = "Fail";
			
			GoTo NOM_REPAIR;
		}
        Result 9
		{
			Property PassFail = "Fail";
			
			GoTo NOM_REPAIR;
		}

	}
    
	FlowItem ALL_\Module\_X_E_BEGINCPUNOM_X_X_X_X_X_X_MBIST_DFF_WRITE_VMAX ALL_\Module\_X_E_BEGINCPUNOM_X_X_X_X_X_X_MBIST_DFF_WRITE_VMAX @EDC
	{
		Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
		Result 0
		{
			Property PassFail = "Fail";
			
			GoTo XSA_\Module\_SB_\RunMode\_BEGINCPUNOM_X_\Domain\A_NOM_X_ALL;
		}
		Result 1
		{
			Property PassFail = "Pass";
			GoTo XSA_\Module\_SB_\RunMode\_BEGINCPUNOM_X_\Domain\A_NOM_X_ALL;
		}
		Result 2
		{
			Property PassFail = "Pass";
			GoTo XSA_\Module\_SB_\RunMode\_BEGINCPUNOM_X_\Domain\A_NOM_X_ALL;
		}
        Result 3
		{
			Property PassFail = "Pass";
			GoTo XSA_\Module\_SB_\RunMode\_BEGINCPUNOM_X_\Domain\A_NOM_X_ALL;
		}
        Result 4
		{
			Property PassFail = "Pass";
			GoTo XSA_\Module\_SB_\RunMode\_BEGINCPUNOM_X_\Domain\A_NOM_X_ALL;
		}
        Result 5
		{
			Property PassFail = "Fail";
			
			GoTo XSA_\Module\_SB_\RunMode\_BEGINCPUNOM_X_\Domain\A_NOM_X_ALL;
		}
        Result 6
		{
			Property PassFail = "Fail";
			
			GoTo XSA_\Module\_SB_\RunMode\_BEGINCPUNOM_X_\Domain\A_NOM_X_ALL;
		}
        Result 7
		{
			Property PassFail = "Fail";
			
			GoTo XSA_\Module\_SB_\RunMode\_BEGINCPUNOM_X_\Domain\A_NOM_X_ALL;
		}
        Result 8
		{
			Property PassFail = "Fail";
			
			GoTo XSA_\Module\_SB_\RunMode\_BEGINCPUNOM_X_\Domain\A_NOM_X_ALL;
		}
        Result 9
		{
			Property PassFail = "Fail";
			
			GoTo XSA_\Module\_SB_\RunMode\_BEGINCPUNOM_X_\Domain\A_NOM_X_ALL;
		}

	}
    
   FlowItem VMAX_REPAIR VMAX_REPAIR
	{
		Result -2 
		{
			Property PassFail = "Fail";
			Return -2; 
		}
		Result -1 
		{ 
			Property PassFail = "Fail";
			Return -1; 
		}
		Result 0 
		{ 
			Property PassFail = "Fail";
			GoTo ALL_\Module\_X_E_BEGINCPUNOM_X_X_X_X_X_X_MBIST_DFF_WRITE_VMAX; 
		}
		Result 1
		{ 
			Property PassFail = "Pass";
			GoTo ALL_\Module\_X_E_BEGINCPUNOM_X_X_X_X_X_X_MBIST_DFF_WRITE_VMAX; 
		}
	}
    
	FlowItem ALL_\Module\_X_E_BEGINCPUNOM_X_X_X_X_X_X_MBIST_DFF_WRITE_NOM ALL_\Module\_X_E_BEGINCPUNOM_X_X_X_X_X_X_MBIST_DFF_WRITE_NOM @EDC
	{
		Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
		Result 0
		{
			Property PassFail = "Fail";
			
			GoTo SSA_\Module\_\Type\_\RunMode\_BEGINCPUNOM_X_\Domain\A_MIN_X_DUMMY;
		}
		Result 1
		{
			Property PassFail = "Pass";
			GoTo SSA_\Module\_\Type\_\RunMode\_BEGINCPUNOM_X_\Domain\A_MIN_X_DUMMY;
		}
		Result 2
		{
			Property PassFail = "Pass";
			GoTo SSA_\Module\_\Type\_\RunMode\_BEGINCPUNOM_X_\Domain\A_MIN_X_DUMMY;
		}
        Result 3
		{
			Property PassFail = "Pass";
			GoTo SSA_\Module\_\Type\_\RunMode\_BEGINCPUNOM_X_\Domain\A_MIN_X_DUMMY;
		}
        Result 4
		{
			Property PassFail = "Pass";
			GoTo SSA_\Module\_\Type\_\RunMode\_BEGINCPUNOM_X_\Domain\A_MIN_X_DUMMY;
		}
        Result 5
		{
			Property PassFail = "Fail";
			
			GoTo SSA_\Module\_\Type\_\RunMode\_BEGINCPUNOM_X_\Domain\A_MIN_X_DUMMY;
		}
        Result 6
		{
			Property PassFail = "Fail";
			
			GoTo SSA_\Module\_\Type\_\RunMode\_BEGINCPUNOM_X_\Domain\A_MIN_X_DUMMY;
		}
        Result 7
		{
			Property PassFail = "Fail";
			
			GoTo SSA_\Module\_\Type\_\RunMode\_BEGINCPUNOM_X_\Domain\A_MIN_X_DUMMY;
		}
        Result 8
		{
			Property PassFail = "Fail";
			
			GoTo SSA_\Module\_\Type\_\RunMode\_BEGINCPUNOM_X_\Domain\A_MIN_X_DUMMY;
		}
        Result 9
		{
			Property PassFail = "Fail";
			
			GoTo SSA_\Module\_\Type\_\RunMode\_BEGINCPUNOM_X_\Domain\A_MIN_X_DUMMY;
		}

	}

 
Flow ARR_\Module\_CXX_ENDCPUNOM
{
    FlowItem SSA_\Module\_SB_\RunMode\_ENDCPUNOM_X_\Domain\A_X_X_C6S_RETENTION_ALL SSA_\Module\_SB_\RunMode\_ENDCPUNOM_X_\Domain\A_X_X_C6S_RETENTION_ALL @EDC
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90600200_fail_ARR_\Module\_CXX_SSA_\Module\_SB_\RunMode\_ENDCPUNOM_X_\Domain\A_X_X_C6S_RETENTION_ALL;
            
            Return 1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90600200_fail_ARR_\Module\_CXX_SSA_\Module\_SB_\RunMode\_ENDCPUNOM_X_\Domain\A_X_X_C6S_RETENTION_ALL;
            
            Return 1;
        }
        Result 3
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 4
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90976018_fail_PTH_DTS_XXX_ARR_\Module\_CXX_THERMAL_PORT4_SHARED_BIN;
            
            Return 1;
        }
        Result 5
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90611920_fail_ARR_\Module\_CXX_RESET_PORT5_SHARED_BIN;
            
            Return 1;
        }
    }
    
}

Flow ARR_\Module\_CXX_ENDCPUMAX
{
    FlowItem SSA_\Module\_SB_\RunMode\_ENDCPUMAX_X_\Domain\A_MAX_X_PMUCS_ALL SSA_\Module\_SB_\RunMode\_ENDCPUMAX_X_\Domain\A_MAX_X_PMUCS_ALL @EDC
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90600300_fail_ARR_\Module\_CXX_SSA_\Module\_SB_\RunMode\_ENDCPUMAX_X_\Domain\A_MAX_X_PMUCS_ALL;
            
            Return 1;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90600300_fail_ARR_\Module\_CXX_SSA_\Module\_SB_\RunMode\_ENDCPUMAX_X_\Domain\A_MAX_X_PMUCS_ALL;
            
            Return 1;
        }
        Result 3
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 4
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90976018_fail_PTH_DTS_XXX_ARR_\Module\_CXX_THERMAL_PORT4_SHARED_BIN;
            
            Return 1;
        }
        Result 5
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b90611920_fail_ARR_\Module\_CXX_RESET_PORT5_SHARED_BIN;
            
            Return 1;
        }
    }
}

