r"""
Document title : TestMethod Classes definition file
Summary: This document contains the testmethod information necessary for pymtpl to generate an mtpl output.
Date Generated: 2025-01-16
Generated from: \\amr\ec\proj\mdl\jf\intel\engineering\dev\PQV\dtv\scan\skorlam\Scripts\pymtpl_development\applications.manufacturing.ate-test.tp-tools.pytpd\pymtpl
Tool used: gen_methods.py
"""
from pymtpl.core import BaseMethod
from pymtpl.core import required, optional


# Beginning of PrimeApplySerialCaptureGroupMapTestMethod class definition
class PrimeApplySerialCaptureGroupMapTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 CaptureGroupMapName=required,  # Gets or sets the capture group map name to apply.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeApplySerialCaptureGroupMapTestMethod class definition


# Beginning of PrimeApplyTestConditionTestMethod class definition
class PrimeApplyTestConditionTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 AlarmPortRedirect=optional,        # Disable or enable alarm port redirect.
                 TestConditionCategory=optional,    # Test Condition category.
                 TestConditionName=required,        # Name of an existing Test Condition.
                 BypassPort=optional,               # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,      # Enable for current instance's test time and memory information
                 LogLevel=optional,                 # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,           # Enable for record detailed test time information
                 SetPointsPlistMode=optional,       # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,  # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,    # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,     # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,           # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,              # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,             # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FlowIndex=optional,                # Parameter to specify the instance flow index on Dynamic Flows.
                 FlowIndexCallbackName=optional,    # Flow Index callback function name. in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeApplyTestConditionTestMethod class definition


# Beginning of PrimeArrayFusingTestMethod class definition
class PrimeArrayFusingTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 DffUploadMode=optional,                # Gets or sets FuseToDFFWritingMode.
                 FuseResourceFile=required,             # Gets or sets FuseResourceFile input file.
                 FusingMode=optional,                   # Gets or sets FusingMode.
                 Patlist=required,                      # Gets or sets Patlist name for setting up the fuse handles.
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PrePlist=optional,                     # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeArrayFusingTestMethod class definition


# Beginning of PrimeArrayHryTestMethod class definition
class PrimeArrayHryTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ApplyEndSequence=optional,             # Gets or sets the ApplyEndSequence at the end of the test.
                 ConfigFile=required,                   # Gets or sets the Configuration File.
                 LevelsTc=required,                     # Gets or sets LevelsTc for plist execution.
                 MaskPins=optional,                     # Gets or sets comma separated pins for mask.
                 Patlist=required,                      # Gets or sets Patlist to execute.
                 PrePlist=optional,                     # Gets or sets the PrePlist callback to plist execution.
                 RawStringForwardingMode=optional,      # Gets or sets the Raw String forwarding mode.
                 SharedStorageKey=optional,             # Gets or sets the Key to be used with Raw STring Forwarding mode. If empty the mode is disabled.
                 TimingsTc=required,                    # Gets or sets TimingsTc for plist execution.
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeArrayHryTestMethod class definition


# Beginning of PrimeArrayRepairTestMethod class definition
class PrimeArrayRepairTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ApplyEndSequence=optional,             # Gets or sets the ApplyEndSequence at the end of the test.
                 ArrayName=required,                    # Gets or sets ArrayName to plist execution.
                 BaseNumber=required,                   # Gets or sets BaseNumber for R-file printing.
                 CtvPinNames=required,                  # Gets or sets CtvPinNames to capture.
                 IfeObject=optional,                    # Gets or sets The IFE object of type IArrayRepairExtensions.
                 LevelsTc=required,                     # Gets or sets LevelsTc to plist execution.
                 MaskPins=optional,                     # Gets or sets comma separated pins for mask.
                 Patlist=required,                      # Gets or sets Patlist to execute.
                 PrePlist=optional,                     # Gets or sets the PrePlist callback to plist execution.
                 RasterConfigFile=optional,             # Gets or sets RasterConfigFile input file.
                 ResourcesFile=required,                # Gets or sets ResourcesFile input file.
                 TimingsTc=required,                    # Gets or sets TimingsTc for plist execution.
                 TotalFailCaptureCount=optional,        # Gets or sets number of Patlist execution failures to capture per plist.
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeArrayRepairTestMethod class definition


# Beginning of PrimeBinSetterTestMethod class definition
class PrimeBinSetterTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 NumberOfFailingPath=optional,   # Gets or sets parameter of Number of Failing BinSet path.
                 ReadDirectionSetting=optional,  # Gets or sets parameter of Read Direction of the instances run.
                 BypassPort=optional,            # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,   # Enable for current instance's test time and memory information
                 LogLevel=optional,              # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,        # Enable for record detailed test time information
                 PreInstance=optional,           # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,          # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeBinSetterTestMethod class definition


# Beginning of PrimeCallbacksRegistrarTestMethod class definition
class PrimeCallbacksRegistrarTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 IfeObject=optional,            # Gets or Sets **not in use will be removed later with the refactoring of the IfeObject**.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeCallbacksRegistrarTestMethod class definition


# Beginning of PrimeCapturePacketsTestMethod class definition
class PrimeCapturePacketsTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ApplyEndSequence=optional,             # Gets or sets whether to apply the end sequence for this test execution.
                 DataPins=required,                     # Pins to used to collect data for packet generation.
                 FunctionalDataToUse=required,          #  Gets or sets the type of functional test data that will be used to generate packets.
                 IdPins=required,                       # Pins to used to id incoming cycles.
                 InvalidPacketTolerance=optional,       # The maximum allowed invalid cycles when assembling packets.
                 KeyForSharedStorage=required,          # Gets or sets the key to use when inserting the final binary string into shared storage.
                 LevelsTc=required,                     # Gets or sets levels test condition to use for functional test execution.
                 MaskPins=optional,                     # Gets or sets the pins to mask for functional test execution.
                 PacketSize=required,                   # The expected size of complete packets.
                 Patlist=required,                      # Gets or sets plist to use for functional test execution.
                 PrePlist=optional,                     # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 ReversePacketOutput=optional,          # If true, reverses the bits of the output packets before placing them into SharedStorage
                 Sequence=required,                     # Gets or sets a sequence of integer values that will be used to sequence packets in 'Wave'. These values will be checked against the id value of each packet.
                 Timeout=optional,                      # The maximum allowed time to innerExecute this instance before exiting out port 0.
                 TimingsTc=required,                    # Gets or sets timing test condition to use for functional test execution.
                 TotalCaptureCount=optional,            # Gets or sets the total amount of failures allowed if using PerCycleFails to generate packets. Ignored otherwise.
                 ValidPins=required,                    # Pins to used to determine if cycle is valid.
                 ValidValues=required,                  # The values each valid pin should display for an incoming cycle to be considered valid.
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeCapturePacketsTestMethod class definition


# Beginning of PrimeCaptureVectorsTestMethod class definition
class PrimeCaptureVectorsTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ApplyEndSequence=optional,             # Gets or sets whether to apply the end sequence for this test execution.
                 FunctionalDataToUse=required,          # Gets or sets the type of functional test data that will be used to generate vectors.
                 KeyForSharedStorage=required,          # Gets or sets the key to use when inserting the final binary string into shared storage.
                 LevelsTc=required,                     # Gets or sets levels test condition to use for functional test execution.
                 MaskPins=optional,                     # Gets or sets the pins to mask for functional test execution.
                 Mode=required,                         # Gets or sets the decoding mode for this test method.
                 Patlist=required,                      # Gets or sets plist to use for functional test execution.
                 Pins=required,                         # Gets or sets all pins used for capture of vectors.
                 PrePlist=optional,                     # Gets or sets the PrePlist callback to plist execution.
                 ReverseVectorOutput=optional,          # If true, reverses the bits of the output vectors before placing them into SharedStorage
                 Timeout=optional,                      # How long this test method should take to execute (in ms) before exiting out of port 0.
                 TimingsTc=required,                    # Gets or sets timing test condition to use for functional test execution.
                 TotalCaptureCount=optional,            # Gets or sets the total amount of failures allowed if using PerCycleFails to generate vectors. Ignored otherwise.
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeCaptureVectorsTestMethod class definition


# Beginning of PrimeContactResistanceTestMethod class definition
class PrimeContactResistanceTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ApplyEndSequence=optional,        # ApplyEndSequence at the end of the test.
                 LevelsTc=required,                # Name of the levels file.
                 SetupFilePath=required,           # The path of the Setup file.
                 BypassPort=optional,              # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,     # Enable for current instance's test time and memory information
                 LogLevel=optional,                # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,          # Enable for record detailed test time information
                 PreInstance=optional,             # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,            # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 RelayTestConditionName=optional,  # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeContactResistanceTestMethod class definition


# Beginning of PrimeCtvDecoderTestMethod class definition
class PrimeCtvDecoderTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ApplyEndSequence=optional,              # Gets or sets the ApplyEndSequence at the end of the test.
                 ConfigurationFile=required,             # Gets or sets ConfigFile with dataStructure parameters.
                 CtvCapturePins=optional,                # Gets or sets comma separated pins for CTV capture.
                 DatalogLevel=optional,                  # Gets or sets datalog level(ALL, FAIL_ONLY, COMPRESS, PINMAP_COMPRESS)
                 DieIdRename=optional,                   # Gets or sets the DieIdRename.
                 HighLimits=optional,                    # Gets or sets comma seperated high limits for the measure pins.
                 IfeObject=optional,                     # Gets or sets the IFE object of type ITriggeredDcExtensions.
                 LevelsTc=required,                      # Gets or sets LevelsTc to plist execution.
                 LowLimits=optional,                     # Gets or sets comma separated low limits for the measure pins.
                 MaskPins=optional,                      # Gets or sets comma separated pins for mask.
                 MeasurementTypes=optional,              #  Gets or sets comma separated measurement types (Current, Voltage) or (C, V).
                 Patlist=required,                       # Gets or sets Pat-list to execute.
                 PerDieBinning=optional,                 # Gets or sets the PerDieBinning.
                 Pins=optional,                          #  Gets or sets comma separated pins to get DC results for.
                 PrePlist=optional,                      # Gets or sets the PrePlist callback to plist execution.
                 SamplingCount=optional,                 #  Gets or sets sampling count per pin.
                 SoftwareTriggerConfiguration=optional,  # Gets or sets the configuration file for the software trigger event.
                 TimingsTc=required,                     # Gets or sets TimingsTc for plist execution.
                 TriggerMapName=optional,                # Gets or sets comma seperated high limits for the measure pins.
                 BypassPort=optional,                    # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,           # Enable for current instance's test time and memory information
                 LogLevel=optional,                      # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                # Enable for record detailed test time information
                 PreInstance=optional,                   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,            # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,       # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,         # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,          # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,                # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,             # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,   # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,       # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,        # The RelayTestCondition to apply.
                 PostPlist=optional,                     # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeCtvDecoderTestMethod class definition


# Beginning of PrimeCurrentDieIdManagerTestMethod class definition
class PrimeCurrentDieIdManagerTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 DieIdValue=optional,           # Gets or sets of the value to the current dieID.
                 OperationHandler=optional,     # Gets or sets of the Operation on handling the Current Die Id.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeCurrentDieIdManagerTestMethod class definition


# Beginning of PrimeDcLeakageTestMethod class definition
class PrimeDcLeakageTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 Configuration=optional,           # Gets or sets ConfigurationSet name from Json to be used during testing.
                 ConfigurationFile=optional,       # Gets or sets the json file which contains DcLeakage configurations.
                 DeviceType=optional,              # Gets or sets pre-conditioning pattern execution type. Static executes the pre-conditioning pattern only once for the first pin/pingroup. Dynamic executes for every pin/pingroup.
                 ExecutionMode=required,           # Gets or sets Execution mode (PerPin, PerGroup, PerConfig).
                 IfeObject=optional,               # Gets or sets The IFE object of type IDcLeakageExtension.
                 LeakageHighPatlist=optional,      # Gets or sets Patlist for leakage high test.
                 LeakageLowPatlist=optional,       # Gets or sets Patlist for leakage low test.
                 LevelsTc=optional,                # Gets or sets LevelsTc to plist execution.
                 PrePause=optional,                # Gets or sets delay time between DC measurements in seconds.
                 TestType=optional,                # Gets or sets the leakage test to execute (VCC for Low Leakage, VSS for High, Both for both).
                 TimingsTc=optional,               # Gets or sets TimingsTc for plist execution.
                 BypassPort=optional,              # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,     # Enable for current instance's test time and memory information
                 LogLevel=optional,                # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,          # Enable for record detailed test time information
                 PreInstance=optional,             # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,            # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 RelayTestConditionName=optional,  # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeDcLeakageTestMethod class definition


# Beginning of PrimeDcTestMethod class definition
class PrimeDcTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 AlarmPortRedirect=optional,       # The alarm port redirect disabled or enabled.
                 ApplyEndSequence=optional,        # The ApplyEndSequence at the end of the test.
                 DatalogLevel=optional,            # Datalog level(ALL, FAIL_ONLY, COMPRESS, PINMAP_COMPRESS\").
                 EnableFlushSmartTc=optional,      # Flag to enable flushing Levels Smart TC.
                 HighLimits=optional,              # Comma separated high limits for the measure Pins.
                 IfeObject=optional,               # Gets or sets the IFE object of type IDcExtensions.
                 LevelsTc=required,                # The alarm port redirect disabled or enabled.
                 LowLimits=optional,               # Comma separated low limits for the measure Pins.
                 MeasurementTypes=optional,        # comma separated measurement type(Current, Voltage\").
                 Pins=required,                    # Comma separated Pins to get DC results for.
                 SamplingCount=optional,           # Sampling count per pin. Optional field , Required when measuring the same pin few times.
                 BypassPort=optional,              # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,     # Enable for current instance's test time and memory information
                 LogLevel=optional,                # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,          # Enable for record detailed test time information
                 PreInstance=optional,             # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,            # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 RelayTestConditionName=optional,  # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeDcTestMethod class definition


# Beginning of PrimeDefeatureReportTestMethod class definition
class PrimeDefeatureReportTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 InputFilePath=required,        # Gets or sets the input file path for defeature report.
                 ReadConfigFromFile=optional,   # 
                 SubFlow=required,              # Gets or sets the subflow to execute.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeDefeatureReportTestMethod class definition


# Beginning of PrimeDeviceEndDatalogTestMethod class definition
class PrimeDeviceEndDatalogTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 IfeObject=optional,            # Ife object
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeDeviceEndDatalogTestMethod class definition


# Beginning of PrimeDeviceEndFinalizeTestMethod class definition
class PrimeDeviceEndFinalizeTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 IfeObject=optional,            # Ife object
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeDeviceEndFinalizeTestMethod class definition


# Beginning of PrimeDeviceStartPackageDatalogTestMethod class definition
class PrimeDeviceStartPackageDatalogTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 IfeObject=optional,            # Gets or sets extended functions.
                 VisualIdCheck=optional,        # Gets or sets the type of visual Id check. Default value is 'IGNORE_CAMERA'
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeDeviceStartPackageDatalogTestMethod class definition


# Beginning of PrimeDeviceStartSetupTestMethod class definition
class PrimeDeviceStartSetupTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 SmartTc=optional,              # Gets or sets whether or not smartTC will be enabled for the current DUT.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeDeviceStartSetupTestMethod class definition


# Beginning of PrimeDeviceStartSingleDieDatalogTestMethod class definition
class PrimeDeviceStartSingleDieDatalogTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 IfeObject=optional,            # Gets or sets extended functions.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeDeviceStartSingleDieDatalogTestMethod class definition


# Beginning of PrimeDeviceStartWaferDatalogTestMethod class definition
class PrimeDeviceStartWaferDatalogTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 IfeObject=optional,            # Gets or sets extended functions.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeDeviceStartWaferDatalogTestMethod class definition


# Beginning of PrimeDffEndOfFlowValidationTestMethod class definition
class PrimeDffEndOfFlowValidationTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 EnableFailingPortForDefaultValue=optional,  # Enable or disable failing port (port 2) for dff tokens that wasn't updated during Main Flow execution. This will take priorities over failing port (port 0) for token check failure.
                 BypassPort=optional,                        # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,               # Enable for current instance's test time and memory information
                 LogLevel=optional,                          # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                    # Enable for record detailed test time information
                 PreInstance=optional,                       # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                      # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeDffEndOfFlowValidationTestMethod class definition


# Beginning of PrimeDffReadTestMethod class definition
class PrimeDffReadTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 EnabledModules=optional,       # The IFE object of type IUltDecoderExtensions.
                 IsInlineDff=optional,          # InlineDFF flag to enabling or Disabling Inline DFF feature.
                 LogIndividualTokens=optional,  # The setting for DFF Tokens to be logged individually in iTuff for ARIES consumption.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeDffReadTestMethod class definition


# Beginning of PrimeElectricalZAlignmentTestMethod class definition
class PrimeElectricalZAlignmentTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ApplyEndSequence=optional,         # ApplyEndSequence at the end of the test.
                 ItuffDataloggingEnabled=optional,  # Whether or not the Test Method will do the Ituff Datalogging.
                 LevelsTc=required,                 # Name of the levels file.
                 SetupFilePath=required,            # The path of the Setup file.
                 BypassPort=optional,               # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,      # Enable for current instance's test time and memory information
                 LogLevel=optional,                 # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,           # Enable for record detailed test time information
                 PreInstance=optional,              # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,             # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 RelayTestConditionName=optional,   # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeElectricalZAlignmentTestMethod class definition


# Beginning of PrimeEyeDiagramTestMethod class definition
class PrimeEyeDiagramTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ConfigurationInputFile=optional,       # Configuration input file.
                 CtvCapturePins=optional,               # Comma separated pins for CTV capture.
                 CtvDataSharedStorageKey=optional,      # Ctv Data Shared Storage Key.
                 CtvLogic=optional,                     # CtvLogic.
                 DieIdRename=optional,                  # DieId to be used to replace the pin name on ituff printing and to add the corresponding tssid.
                 IfeObject=optional,                    # IFE object of type IFuncCaptureExtensions.
                 LevelsTc=optional,                     # LevelsTc to plist execution.
                 Mode=optional,                         # Mode.
                 Patlist=optional,                      # Patlist to execute.
                 PrePlist=optional,                     # PrePlist callback to plist execution.
                 PrintPlots=optional,                   # PrintPlots.
                 TimingsTc=optional,                    # TimingsTc for plist execution.
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeEyeDiagramTestMethod class definition


# Beginning of PrimeFastRasterTestMethod class definition
class PrimeFastRasterTestMethod(BaseMethod):
    def __init__(self,
                 name,
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
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeFastRasterTestMethod class definition


# Beginning of PrimeFlowControlEndTestMethod class definition
class PrimeFlowControlEndTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 Datalog=optional,              # Value indicating whether data logging is enabled.
                 DffTokenName=optional,         # DffTokenName to set with flow value.
                 DomainName=required,           # Domain name.
                 SharedStorageKey=optional,     # Shared storage token to set with flow value.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeFlowControlEndTestMethod class definition


# Beginning of PrimeFlowControlForkTestMethod class definition
class PrimeFlowControlForkTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 DomainName=required,           # Domain name.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeFlowControlForkTestMethod class definition


# Beginning of PrimeFlowControlSetTestMethod class definition
class PrimeFlowControlSetTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 DomainName=required,           # Domain name.
                 DomainValue=required,          # Domain Value.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeFlowControlSetTestMethod class definition


# Beginning of PrimeFlowControlStartTestMethod class definition
class PrimeFlowControlStartTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 DefaultValue=required,         # Domain Value.
                 DffTokenName=required,         # DFF Token Name to be used as source of domain flow number.
                 DomainName=required,           # Domain name.
                 UseDffToken=optional,          # DFF Token Override.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeFlowControlStartTestMethod class definition


# Beginning of PrimeFlowLoopControlTestMethod class definition
class PrimeFlowLoopControlTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 InputJsonConfigFile=required,  # DummyParam1 (this comment will be used on the pre-header file).
                 SetConfig=optional,            # Configname to selectively execute a set to modify Flow Loop Control.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeFlowLoopControlTestMethod class definition


# Beginning of PrimeFlowLoopExitTestMethod class definition
class PrimeFlowLoopExitTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 FlowItemName=required,         # flow item name.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeFlowLoopExitTestMethod class definition


# Beginning of PrimeForkTestMethod class definition
class PrimeForkTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 IsRegex=optional,              # Value indicating whether the provided \"LocationCodeToMatch\" parameter is a RegEx, or the exact name of the location code to match to.
                 LocationCodeToMatch=optional,  # Configname to selectively execute a set to modify Flow Loop Control.
                 Mode=required,                 # Value that will determine how this FORK will determine its exit port.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeForkTestMethod class definition


# Beginning of PrimeFuncDcCtvTestMethod class definition
class PrimeFuncDcCtvTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 AlarmPortRedirect=optional,            # Gets or sets the alarm port redirect disabled or enabled.
                 ApplyEndSequence=optional,             # Gets or sets the ApplyEndSequence at the end of the test.
                 CtvPins=required,                      #  Gets or sets comma seperated pins to capture results for.
                 DatalogLevel=optional,                 # Gets or sets datalog level(ALL, FAIL_ONLY, COMPRESS, PINMAP_COMPRESS)
                 DcLevels=required,                     # Gets or sets LevelsTc to plist execution.
                 HighLimits=required,                   # Gets or sets comma separated high limits for the measure pins.
                 IfeObject=optional,                    # Gets or sets the IFE object of type IDcExtensions.
                 LevelsTc=required,                     # Gets or sets LevelsTc for plist execution.
                 LowLimits=required,                    # Gets or sets comma separated low limits for the measure pins.
                 MaskPins=optional,                     # Gets or sets  comma separated pins for mask.
                 MeasurementTypes=optional,             # Gets or sets comma separated measurement type(Current, Voltage)
                 Patlist=required,                      # Gets or sets Patlist to execute.
                 Pins=required,                         # Gets or sets comma seperated pins to get DC results for.
                 PrePlist=optional,                     # Gets or sets the PrePlist callback to plist execution.
                 SamplingCount=optional,                # Gets or sets  comma separated pins for mask.
                 TimingsTc=required,                    # Gets or sets TimingsTc for plist execution.
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeFuncDcCtvTestMethod class definition


# Beginning of PrimeFuncDcTestMethod class definition
class PrimeFuncDcTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 AlarmPortRedirect=optional,            # Gets or sets the alarm port redirect disabled or enabled.
                 ApplyEndSequence=optional,             # Gets or sets the ApplyEndSequence at the end of the test.
                 DatalogLevel=optional,                 # Gets or sets datalog level(ALL, FAIL_ONLY, COMPRESS, PINMAP_COMPRESS)
                 DcLevels=required,                     # Gets or sets levels with the Dc test. This level TC would be the one with the `StartMeasurement` block.
                 HighLimits=required,                   # Gets or sets comma separated high limits for the measure pins.
                 IfeObject=optional,                    # Gets or sets the IFE object of type IDcExtensions.
                 LevelsTc=required,                     # Gets or sets LevelsTc for plist execution.
                 LowLimits=required,                    # Gets or sets comma separated low limits for the measure pins.
                 MaskPins=optional,                     # Gets or sets comma separated pins for mask.
                 MeasurementTypes=optional,             # Gets or sets comma separated measurement type(Current, Voltage)
                 Patlist=required,                      # Gets or sets Patlist to execute.
                 Pins=required,                         #  Gets or sets comma separated pins to get DC results for.
                 PrePlist=optional,                     # Gets or sets the PrePlist callback to plist execution.
                 SamplingCount=optional,                # Gets or sets sampling count per pin.
                 TimingsTc=required,                    # Gets or sets TimingsTc for plist execution.
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeFuncDcTestMethod class definition


# Beginning of PrimeFunctionalTestMethod class definition
class PrimeFunctionalTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 AlarmPortRedirect=optional,             # The alarm port redirect disabled or enabled.
                 ApplyEndSequence=optional,              # The ApplyEndSequence at the end of the test.
                 CtvCapturePerCycleMode=optional,        # CTV capture mode. If DISABLED (default), CTV capture will be per pin. If ENABLED it will be per cycle.
                 CtvCapturePins=optional,                # Comma separated pins for CTV capture.
                 DtsConfigurationName=optional,          # Configuration in case DTS processing is wanted.
                 FailuresToCapturePerPattern=optional,   # Int for number of failures per pattern to capture. If 0 (default), per pattern capture is disabled.
                 FailuresToCaptureTotal=optional,        # Int for the number of global failures to capture. If 0 (default), it means failure capture is disabled.
                 IfeObject=optional,                     #  Gets or sets the IFE object of type IFuncCaptureExtensions.
                 LevelsTc=required,                      # LevelsTc to plist execution.
                 MaskPins=optional,                      # Comma separated pins for mask.
                 MaxFailuresPerPatternToItuff=optional,  # Int for number of failures per pattern to print to ituff. If 0 (default), per pattern failure count defaults to MaxFailuresToItuff.
                 MaxFailuresToItuff=optional,            # int for the number of global failures to print to ituff. If 0 (default), it means failure prints are disabled.
                 Patlist=required,                       # Patlist to execute.
                 PrePlist=optional,                      # PrePlist callback to plist execution.
                 TimingsTc=required,                     # TimingsTc for plist execution.
                 BypassPort=optional,                    # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,           # Enable for current instance's test time and memory information
                 LogLevel=optional,                      # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                # Enable for record detailed test time information
                 SetPointsPlistMode=optional,            # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,       # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,         # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,          # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,                # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,             # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,   # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 RelayTestConditionName=optional,        # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,       # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PostPlist=optional,                     # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeFunctionalTestMethod class definition


# Beginning of PrimeFuseAtClassTestMethod class definition
class PrimeFuseAtClassTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 FactMode=required,                       # Fact mode.
                 FactRulesFilePath=required,              # FRF file path or a user var that contains it.
                 LotReservationFilePath=required,         # LRF file path or a user var that contains it.
                 MrvUserVar=optional,                     # Name of the user var that contains the Mrv against which to check the mrv value in the LRF file.
                 OpTypeUserVar=optional,                  # Name of the user var that contains the OpType against which to check the current OpType value.
                 SspecBinsMappingObjectContext=required,  # Shared storage context in which the SspecBinsMapping object is stored.
                 SspecBinsMappingObjectKey=required,      # Key of the SspecBinMapping to be used on the shared storage.
                 VersionMatch=optional,                   # Name of the user var that contains the Mrv against which to check the mrv value in the LRF file.
                 VersionOffset=optional,                  # Offset non matching version can have if VersionMatch is OFFSET.
                 BypassPort=optional,                     # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,            # Enable for current instance's test time and memory information
                 LogLevel=optional,                       # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                 # Enable for record detailed test time information
                 PreInstance=optional,                    # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                   # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeFuseAtClassTestMethod class definition


# Beginning of PrimeFuseBurnMaskTestMethod class definition
class PrimeFuseBurnMaskTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ApplyEndSequence=optional,             # ApplyEndSequence at the end of the test.
                 ConfigName=required,                   # Configuration name for the input file. Can only define single name.
                 ConfigurationFile=required,            # ConfigurationFile. ~HDMT_TPL_DIR/Modules/FuseBurn/FuseBurn/InputFiles/fuseBurnScenario1.json\". other using type String.
                 IfeObject=optional,                    # IFE object of type IFuseReadMaskExtensions.
                 LevelsTc=optional,                     # LevelsTc for plist execution.
                 MaskNames=required,                    # Name of masks to select within the register. By default the test method only allow define single mask name, but user can use it as CommaSeparatedString to run multiple mask with CustomExecute.
                 MaskPins=optional,                     # Comma separated pins for mask.
                 MaxNumberOfFails=optional,             # Maximum number of failure to capture.
                 Patlist=optional,                      # Patlist to execute.
                 PrePatlist=optional,                   # Pre Patlist to execute.
                 RegisterNames=required,                # Name of registers to select within the configuration. Can define single or multiple name with comma delimiter.
                 SkipPatternExecute=optional,           # Execute Pattern aka Run Functional Test. Set DISABLED for execute pattern (functional test).
                 TimingsTc=optional,                    # TimingsTc for plist execution.
                 VoltageFile=optional,                  # VoltageFile. ~HDMT_TPL_DIR/Modules/FuseBurn/FuseBurn/InputFiles/fuseBurnVoltage.json\". other using type String.
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PrePlist=optional,                     # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeFuseBurnMaskTestMethod class definition


# Beginning of PrimeFuseBurnSspecTestMethod class definition
class PrimeFuseBurnSspecTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ConfigName=required,                   # Configuration name for the input file. Can only define single name.
                 ConfigurationFile=required,            # ConfigurationFile. ~HDMT_TPL_DIR/Modules/FuseBurn/FuseBurn/InputFiles/fuseBurnScenario1.json. other using type String.
                 IfeObject=optional,                    # IFE object of type IFuseReadMaskExtensions.
                 LevelsTc=optional,                     # LevelsTc for plist execution.
                 MaskPins=optional,                     # Comma separated pins for mask.
                 MaxNumberOfFails=optional,             # Maximum number of failure to capture.
                 Patlist=optional,                      # Patlist to execute.
                 PrePatlist=optional,                   # Pre Patlist to execute.
                 RegisterNames=required,                # Name of registers to select within the configuration. Can define single or multiple name with comma delimiter.
                 SkipPatternExecute=optional,           # Execute Pattern aka Run Functional Test.
                 TimingsTc=optional,                    # TimingsTc for plist execution.
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PrePlist=optional,                     # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeFuseBurnSspecTestMethod class definition


# Beginning of PrimeFuseReadMarginSweepTestMethod class definition
class PrimeFuseReadMarginSweepTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ApplyEndSequence=optional,                # ApplyEndSequence at the end of the test.
                 ConfigName=required,                      # Configuration name for the input file. Can only define single name.
                 ConfigurationFile=required,               # ConfigurationFile. ~HDMT_TPL_DIR/Modules/FuseRead/FuseRead/InputFiles/fuseReadScenario1.json. other using type String.
                 EnableCaptureFunctionalFailure=optional,  # A value indicating whether to enable CreateCaptureFailureAndCtvPerPinTest(true) or CreateCaptureCtvPerPinTest(false)
                 FuseGroupToDatalog=optional,              # Name of fuse group to datalog. When this parameter is defined (enabled) with valid fuse group name, the fuse string of the fuse group name will be datalog to ituff.
                 IfeObject=optional,                       # IFE object of type IMarginSweepExtensions.
                 IsSimulationEnabled=optional,             # A value indicating whether gets or sets IsSimulationEnable.
                 LevelsTc=required,                        # Level.
                 MaskPins=optional,                        # Comma separated pins for mask.
                 Patlist=required,                         # Patlist.
                 PrePlist=optional,                        # Preplist.
                 RegisterName=required,                    # Name of registers to select within the configuration. Can define single name.
                 TimingsTc=required,                       # Timing.
                 VoltageFile=optional,                     # VoltageFile. ~HDMT_TPL_DIR/Modules/FuseRead/FuseRead/InputFiles/fuseReadVoltage.json. other using type String.
                 BypassPort=optional,                      # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,             # Enable for current instance's test time and memory information
                 LogLevel=optional,                        # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                  # Enable for record detailed test time information
                 PreInstance=optional,                     # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                    # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,              # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,         # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,           # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,            # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,                  # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,               # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,     # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,         # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,          # The RelayTestCondition to apply.
                 PostPlist=optional,                       # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeFuseReadMarginSweepTestMethod class definition


# Beginning of PrimeFuseReadMaskTestMethod class definition
class PrimeFuseReadMaskTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ApplyEndSequence=optional,                # ApplyEndSequence at the end of the test.
                 ConfigName=required,                      # Configuration name for the input file. Can only define single name.
                 ConfigurationFile=required,               # ConfigurationFile. ~HDMT_TPL_DIR/Modules/FuseRead/FuseRead/InputFiles/fuseReadScenario1.json. other using type String.
                 EnableCaptureFunctionalFailure=optional,  # A value whether to enable CreateCaptureFailureAndCtvPerPinTest(true) or CreateCaptureCtvPerPinTest(false).
                 FailingMaskName=optional,                 # Failing mask names. Can define single or multiple name with comma delimiter.
                 FuseGroupToDatalog=optional,              # Name of fuse group to datalog. When this parameter is defined (enabled) with valid fuse group name, the fuse string of the fuse group name will be datalog to ituff.
                 IfeObject=optional,                       # IFE object of type IFuseReadMaskExtensions.
                 LevelsTc=optional,                        # LevelsTc for plist execution.
                 MaskPins=optional,                        # Comma separated pins for mask.
                 PassingMaskName=optional,                 # Passing mask names. Can define single or multiple name with comma delimiter.
                 Patlist=optional,                         # Patlist to execute.
                 PrePlist=optional,                        # Pre Patlist to execute.
                 RegisterName=required,                    # Name of registers to select within the configuration. Can define single or multiple name with comma delimiter.
                 SimulationMode=optional,                  # Simulation mode. Indicating whether fuse string value is set with SimulationString (True) or CtvData (False).
                 TimingsTc=optional,                       # TimingsTc for plist execution.
                 VoltageFile=optional,                     # VoltageFile. ~HDMT_TPL_DIR/Modules/FuseRead/FuseRead/InputFiles/fuseReadVoltage.json. other using type String.
                 BypassPort=optional,                      # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,             # Enable for current instance's test time and memory information
                 LogLevel=optional,                        # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                  # Enable for record detailed test time information
                 PreInstance=optional,                     # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                    # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,              # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,         # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,           # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,            # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,                  # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,               # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,     # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,         # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,          # The RelayTestCondition to apply.
                 PostPlist=optional,                       # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeFuseReadMaskTestMethod class definition


# Beginning of PrimeFuseReadMaskUltDecodeTestMethod class definition
class PrimeFuseReadMaskUltDecodeTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ApplyEndSequence=optional,                # The ApplyEndSequence at the end of the test.
                 ConfigName=required,                      # The configuration name for the input file. Can only define single name.
                 ConfigurationFile=required,               # ConfigurationFile.
                 DieIdNames=required,                      # The Name Die Id name.
                 EnableCaptureFunctionalFailure=optional,  # To enable CreateCaptureFailureAndCtvPerPinTest(enabled) or CreateCaptureCtvPerPinTest(disabled).
                 FailingMaskName=optional,                 # The failing mask names. Can define single or multiple name with comma delimiter.
                 FuseGroupToDatalog=optional,              # The name of fuse group to datalog. When this parameter is defined (enabled) with valid fuse group name, the fuse string of the fuse group name will be datalog to ituff.
                 IfeObject=optional,                       # The IFE object of type IFuseReadMaskExtensions.
                 LevelsTc=optional,                        # LevelsTc for plist execution.
                 MaskPins=optional,                        # Comma separated pins for mask.
                 PackageEfuse=optional,                    # DieId Name to print ituff as PackageEfuse. DieId ULT info will print under trlot, trwafer, trxloc, tryloc.
                 PassingMaskName=optional,                 # The passing mask names. Can define single or multiple name with comma delimiter.
                 Patlist=optional,                         # Patlist to execute.
                 PostUltExecuteMaskName=optional,          # Gets or sets the name of masks to select within the register. By default the test method only allow define single mask name, but user can use it as CommaSeparatedString to run multiple mask with CustomExecute.
                 PrePlist=optional,                        # Pre Patlist to execute.
                 PrintUltDataPerDieIdToItuff=optional,     # The current instance has to print the ult data per die id to the ituff.
                 RegisterName=required,                    # The name of registers to select within the configuration. Can define single or multiple name with comma delimiter.
                 SimulationMode=optional,                  # Simulation mode. Indicating whether fuse string value is set with SimulationString (enabled) or CtvData (disabled).
                 TimingsTc=optional,                       # TimingsTc for plist execution.
                 UltOffset=optional,                       # List of offsets to start ctvs decoding. If one value is given it will be use as offsets for all Ctvs. Default is 0 (zero).
                 VoltageFile=optional,                     # VoltageFile.
                 BypassPort=optional,                      # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,             # Enable for current instance's test time and memory information
                 LogLevel=optional,                        # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                  # Enable for record detailed test time information
                 PreInstance=optional,                     # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                    # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,              # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,         # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,           # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,            # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,                  # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,               # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,     # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,         # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,          # The RelayTestCondition to apply.
                 PostPlist=optional,                       # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeFuseReadMaskUltDecodeTestMethod class definition


# Beginning of PrimeFuseReadSspecTestMethod class definition
class PrimeFuseReadSspecTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ApplyEndSequence=optional,                # The ApplyEndSequence at the end of the test.
                 ConfigName=required,                      # The configuration name for the input file. Can only define single name.
                 ConfigurationFile=required,               # ConfigurationFile.
                 EnableCaptureFunctionalFailure=optional,  # Whether to enable CreateCaptureFailureAndCtvPerPinTest(true) or CreateCaptureCtvPerPinTest(false).
                 FuseGroupToDatalog=optional,              # The name of fuse group to datalog. When this parameter is defined (enabled) with valid fuse group name, the fuse string of the fuse group name will be datalog to ituff.
                 IfeObject=optional,                       # The IFE object of type IFuseReadMaskExtensions.
                 LevelsTc=optional,                        # LevelsTc for plist execution.
                 MaskPins=optional,                        # Comma separated pins for mask.
                 Patlist=optional,                         # Patlist to execute.
                 PrePlist=optional,                        # Pre Patlist to execute.
                 RegisterName=required,                    # The name of registers to select within the configuration. Can define single or multiple name with comma delimiter.
                 SimulationMode=optional,                  # Simulation mode. Indicating whether fuse string value is set with SimulationString (True) or CtvData (False).
                 TimingsTc=optional,                       # TimingsTc for plist execution.
                 VoltageFile=optional,                     # VoltageFile.
                 BypassPort=optional,                      # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,             # Enable for current instance's test time and memory information
                 LogLevel=optional,                        # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                  # Enable for record detailed test time information
                 PreInstance=optional,                     # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                    # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,              # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,         # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,           # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,            # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,                  # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,               # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,     # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,         # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,          # The RelayTestCondition to apply.
                 PostPlist=optional,                       # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeFuseReadSspecTestMethod class definition


# Beginning of PrimeGetDffTestMethod class definition
class PrimeGetDffTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 DieId=optional,                # DieId for the token we would like to pull from. Only single die id is allowed. Value is optional. If left empty, it will grab from the currently set die id.
                 ForceGetFromUBE=optional,      # ForceGetFromUBE, to decide whether to forcefully get Dff directly from UBE file.
                 OpType=optional,               # Optype on the optype we would like to pull dff from. Only single optype is allowed. Value is optional. If left empty, it use the DFFVars.Read_Optype as the optype.
                 Storage=optional,              # For where to keep the data. Accept uservar or sharedstorage. Example On UserVar: UserVarCollection.UserVarName (\".\" is important). Example On SharedStorage: Any string value as long as it's not delimited by \".
                 TokenName=optional,            # TokenName for the token we would like to get. By Field Name Example: TokA.F1
                 Vid=optional,                  # For Vid we would like to pull dff data from. Only single vid is allowed. Value is optional. If left empty, it would not find dff based on vid. If defined, user will also need to define die id and optype.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeGetDffTestMethod class definition


# Beginning of PrimeGetRepairDffTestMethod class definition
class PrimeGetRepairDffTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 RepairDffFile=required,        # Path to the input file containing the information to be obtained from the DFF.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeGetRepairDffTestMethod class definition


# Beginning of PrimeGfxAddTagByUserDefinitionTestMethod class definition
class PrimeGfxAddTagByUserDefinitionTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 Area=required,                 # The Area.
                 Content=required,              # The Content.
                 HryFailSymbol=optional,        # The HryFailSymbol.
                 HryPassSymbol=optional,        # The HryPassSymbol.
                 Tag=required,                  # The Tag.
                 UserInput=required,            # Source input to read EIDs statuses from, for creating the new tag.
                 UserInputType=required,        # The type of the 'UserInput' parameter.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeGfxAddTagByUserDefinitionTestMethod class definition


# Beginning of PrimeGfxEvaluateTestMethod class definition
class PrimeGfxEvaluateTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 Area=required,                       # The Area for Gfx test method.
                 Content=required,                    # Content
                 EndSku=optional,                     # The end sku for Gfx test method.
                 FailRecoveryGroupsKey=optional,      # FailRecoveryGroupsKey
                 HryRawStringDatalog=optional,        # The Hry raw string datalog for GfxScoreboard TM.
                 HryTreeLevelDatalog=optional,        # The Hry tree level datalog for GfxScoreboard TM.
                 OptionalTagsForEvaluation=optional,  # OptionalTags
                 RequiredTagsForEvaluation=optional,  # RequiredTags
                 ResultSkuKey=optional,               # ResultSkuKey
                 StartSku=optional,                   # The start sku for Gfx test method.
                 Tag=optional,                        # The tag for GfxScoreboard TM.
                 BypassPort=optional,                 # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,        # Enable for current instance's test time and memory information
                 LogLevel=optional,                   # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,             # Enable for record detailed test time information
                 PreInstance=optional,                # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,               # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeGfxEvaluateTestMethod class definition


# Beginning of PrimeGfxPacketMonitorTestMethod class definition
class PrimeGfxPacketMonitorTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ApplyEndSequence=optional,             # The ApplyEndSequence at the end of the test.
                 Area=optional,                         # The Area for Gfx test method.
                 ArrayName=optional,                    # The ArrayName.
                 ConfigFile=required,                   # ConfigFile input file.
                 Content=optional,                      # The Content for GfxScoreboard TM.
                 EndSku=optional,                       # The end sku for Gfx test method.
                 EngineeringOutputFilePath=optional,    # EngineeringOutputFilePath file.
                 FailEidsKey=optional,                  # FailEidsKey
                 FailRecoveryGroupsKey=optional,        # FailRecoveryGroupsKey
                 GfxAggregationMode=optional,           # GfxAggregation mode.
                 HryFailSymbol=optional,                # The HryFailSymbol.
                 HryPassSymbol=optional,                # The HryPassSymbol.
                 HryRawStringDatalog=optional,          # The Hry raw string datalog for GfxScoreboard TM.
                 HryTreeLevelDatalog=optional,          # The Hry tree level datalog for GfxScoreboard TM.
                 LevelsTc=required,                     # LevelsTc to plist execution.
                 MaskPins=optional,                     # Comma separated pins for mask.
                 MaximumFailuresPerPattern=optional,    # MaximumFailuresPerPattern
                 MaximumTotalFailures=optional,         # MaximumTotalFailures
                 PacketDatalogMode=optional,            # PacketDatalogMode mode.
                 Patlist=required,                      # Patlist to execute.
                 PrePlist=optional,                     # The PrePlist callback to plist execution.
                 ResultSkuKey=optional,                 # The result sku for GfxScoreboard TM.
                 StartSku=optional,                     # The start sku for Gfx test method.
                 Tag=optional,                          # The tag for GfxScoreboard TM.
                 TimingsTc=required,                    # TimingsTc for plist execution.
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeGfxPacketMonitorTestMethod class definition


# Beginning of PrimeGfxScoreBoardTestMethod class definition
class PrimeGfxScoreBoardTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ApplyEndSequence=optional,             # The ApplyEndSequence at the end of the test.
                 Area=required,                         # The Area for Gfx test method.
                 BaseNumbers=optional,                  # An integer number value to prefix the generated scoreboard fail counters. This parameter supports multiple base numbers.
                 ConfigFile=required,                   # ConfigFile input file.
                 Content=required,                      # The Content for GfxScoreboard TM.
                 CtvPinName=required,                   # CtvPinNames to capture.
                 DOAPinNames=optional,                  # DOAPinNames to capture.
                 EidDecodeMethod=optional,              # eidDecodeMethod
                 EndSku=optional,                       # The end sku for Gfx test method.
                 FailEidsKey=optional,                  # FailEidsKey
                 FailRecoveryGroupsKey=optional,        # FailRecoveryGroupsKey
                 HryPerPattern=optional,                # hryPerPattern
                 HryRawStringDatalog=optional,          # The Hry raw string datalog for GfxScoreboard TM.
                 HryTreeLevelDatalog=optional,          # The Hry tree level datalog for GfxScoreboard TM.
                 IfeObject=optional,                    # The IFE object of type IFuseReadMaskExtensions.
                 LevelsTc=required,                     # LevelsTc to plist execution.
                 MaskPins=optional,                     # Comma separated pins for mask.
                 MaxFailsNum=optional,                  # The maximum number of fails that can be processed for scoreboard counters. This parameter is zero by default. If no other positive value is passed, then the maximum possible integer value will be used.
                 PassEidsKey=optional,                  # PassEidsKey
                 Patlist=required,                      # Patlist to execute.
                 PatternNameCounterIndexes=optional,    # A comma separated string of integers which map characters in the pattern name to produce a scoreboard counter. Positive indexes, starting at 0, map characters at the start of the pattern name. Negative indexes, starting at -1, map characters at the end of the pattern name.
                 PrePlist=optional,                     # The PrePlist callback to plist execution.
                 ResultSkuKey=optional,                 # The result sku for GfxScoreboard TM.
                 StartSku=optional,                     # The start sku for Gfx test method.
                 Tag=optional,                          # The tag for GfxScoreboard TM.
                 TimingsTc=required,                    # TimingsTc for plist execution.
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeGfxScoreBoardTestMethod class definition


# Beginning of PrimeGfxSsnScoreBoardTestMethod class definition
class PrimeGfxSsnScoreBoardTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 Area=required,                       # The Area for Gfx test method.
                 BaseNumbers=required,                # An integer number value to prefix the generated scoreboard fail counters. This parameter supports multiple base numbers.
                 Content=required,                    # Content
                 CtvCapturePin=required,              # Single pin name for CTV capture.
                 CtvPinName=required,                 # Pin name for which CTV data should be captured.
                 ConfigFile=required,                 # Path to .json input file that describes the CTV mapping to partitions (eids).
                 EndSku=optional,                     # The end sku for Gfx test method.
                 FailRecoveryGroupsKey=optional,      # FailRecoveryGroupsKey
                 HryRawStringDatalog=optional,        # The Hry raw string datalog for GfxScoreboard TM.
                 HryTreeLevelDatalog=optional,        # The Hry tree level datalog for GfxScoreboard TM.
                 InputFile=required,                  # Input file.
                 LevelsTc=required,                   # LevelsTc to plist execution.
                 MaxFailsNum=required,                # The maximum number of fails that can be processed for scoreboard counters. This parameter is zero by default. If no other positive value is passed, then the maximum possible integer value will be used.
                 MaskPins=optional,                   # Comma separated list of pins for which the fail data capture will be skipped.
                 Patlist=required,                    # Patlist to execute.
                 PatternNameCounterIndexes=required,  # A comma separated string of integers which map characters in the pattern name to produce a scoreboard counter. Positive indexes, starting at 0, map characters at the start of the pattern name. Negative indexes, starting at -1, map characters at the end of the pattern name.
                 PatternsToIgnore=required,           # Comma separated patterns regexes to ignore when decoding failures. Note that those won't be disabled on plist level.
                 PrePlist=optional,                   # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 ResultSkuKey=optional,               # ResultSkuKey
                 StartSku=optional,                   # The start sku for Gfx test method.
                 Tag=optional,                        # The tag for GfxScoreboard TM.
                 TimingsTc=required,                  # TimingsTc for plist execution.
                 BypassPort=optional,                 # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,        # Enable for current instance's test time and memory information
                 LogLevel=optional,                   # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,             # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeGfxSsnScoreBoardTestMethod class definition


# Beginning of PrimeGfxStartOfDeviceTestMethod class definition
class PrimeGfxStartOfDeviceTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 Area=required,                 # The Area for Gfx test method.
                 Content=optional,              # The Content for GfxScoreboard TM.
                 EndSku=optional,               # The end sku for Gfx test method.
                 StartSku=optional,             # The start sku for Gfx test method.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeGfxStartOfDeviceTestMethod class definition


# Beginning of PrimeHvqkManagerTestMethod class definition
class PrimeHvqkManagerTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 HvqkMode=optional,             # HvqkMode
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeHvqkManagerTestMethod class definition


# Beginning of PrimeHvqkTestMethod class definition
class PrimeHvqkTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 AlarmHandleDelay=optional,             # Alarm Handle Delay time in millisecond.
                 ApplyEndSequence=optional,             # The ApplyEndSequence at the end of the test.
                 DtsConfigurationName=optional,         # Configuration in case DTS processing is wanted.
                 IfeObject=optional,                    # The IFE object of type IFuseReadMaskExtensions.
                 LevelsTc=required,                     # LevelsTc for plist execution.
                 Patlist=required,                      # The Patlist to execute.
                 PowerDownLevel=optional,               # Custom PowerDown Level for post execution flow.
                 PowerUpLevel=optional,                 # Custom PowerUp Level for post execution flow.
                 TimingsTc=required,                    # TimingsTc for plist execution.
                 VoltageStepConfigFile=required,        # The directory of the HvqkConfigJson file.
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PrePlist=optional,                     # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeHvqkTestMethod class definition


# Beginning of PrimeIVCurveTestMethod class definition
class PrimeIVCurveTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 AlarmPortRedirect=optional,             # Gets or sets the alarm port redirect disabled or enabled.
                 DatalogLevel=optional,                  # Gets or sets datalog level(ALL, FAIL_ONLY, COMPRESS, PINMAP_COMPRESS)
                 FlushSmartTcLevels=optional,            # Gets or sets flag to enable flushing Levels Smart TC.
                 ForceSetPoint=required,                 # ForceSetPoint
                 ForceStartValue=optional,               # ForceStartValue
                 ForceStepSize=optional,                 # ForceStepSize
                 ForceStopValue=optional,                # ForceStopValue
                 HighLimits=optional,                    # High Limits
                 IfeObject=optional,                     # IFE
                 LevelsTc=required,                      # LevelsTC
                 LowLimits=optional,                     # LowLimits
                 MeasurementTypes=optional,              # MeasurementTypes.
                 PerformCharacterizationSweep=optional,  # Execution mode to run sweep or not.
                 Pins=required,                          # Pins
                 BypassPort=optional,                    # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,           # Enable for current instance's test time and memory information
                 LogLevel=optional,                      # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                # Enable for record detailed test time information
                 PreInstance=optional,                   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 RelayTestConditionName=optional,        # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeIVCurveTestMethod class definition


# Beginning of PrimeIdskTestMethod class definition
class PrimeIdskTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 BitLogic=optional,             # Kill for zscore AND/OR vmin_delta. AND by default.
                 OutlierVector=required,        # Outgoing tracking structure GSDS to be used later by DieRecovery.
                 StdDevCeiling=required,        # Maximum standard deviation allowed.
                 StdDevFloor=required,          # Minimum standard deviation allowed.
                 VminDelta=required,            # Maximum vmin difference allowed.
                 VminInput=required,            # Incoming VMIN string.
                 ZscoreLimit=required,          # Sigma kill limit.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeIdskTestMethod class definition


# Beginning of PrimeIdvTestMethod class definition
class PrimeIdvTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ApplyEndSequence=optional,             # The ApplyEndSequence at the end of the test.
                 CalculationsTableFile=required,        # CalculationsTableFile file name.
                 IdvStructureFile=required,             # Idv Structure configuration file name.
                 IfeObject=optional,                    # Gets or sets the IFE object of type IDcExtensions.
                 LevelsTc=required,                     # LevelsTc to plist execution.
                 MaskPins=optional,                     # Comma separated pins for mask.
                 Patlist=required,                      # Patlist to execute.
                 PrePlist=optional,                     # The PrePlist callback to plist execution.
                 RawDataLogging=optional,               # The raw data is logged into ITUFF or not.
                 TapFrequency=required,                 # Tap Frequency value.
                 TimingsTc=required,                    # TimingsTc for plist execution.
                 TriggerMapName=required,               # Comma seperated high limits for the measure pins.
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeIdvTestMethod class definition


# Beginning of PrimeInitializeInstancesTestMethod class definition
class PrimeInitializeInstancesTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 EngineeringDebug=optional,        # EngineeringDebug mode. If true the check of force re-verify conditions (CheckIfForceReVerifyNeeded) are skip returning true.
                 PrintPatternMemory=optional,      # Pattern memory printing.
                 PriorityInstanceVerify=optional,  # List of instances that must be verified prior the verify all instances.
                 VerifyAll=optional,               # VerifyAll mode.
                 BypassPort=optional,              # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,     # Enable for current instance's test time and memory information
                 LogLevel=optional,                # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,          # Enable for record detailed test time information
                 PreInstance=optional,             # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,            # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeInitializeInstancesTestMethod class definition


# Beginning of PrimeInitializeLibraryTestMethod class definition
class PrimeInitializeLibraryTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ForceFullInit=optional,                 # Indicating whether to force full init and skip any 2nd init or InitOffline optimizations. When set to false (i.e. do not force full init), each test method will have the option to force it's own verify by overriding the default ForceReVerify API. This is a debug feature to allow modifying input files, for production TP this is expected to always be False.
                 GlobalTelemetryLevel=optional,          # Sets the Performance telemetry level
                 PerformanceCounterLogLevel=optional,    # Sets the Performance Counter level
                 PerformanceCounterSampleRate=optional,  # Sets the Performance telemetry level
                 BypassPort=optional,                    # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,           # Enable for current instance's test time and memory information
                 LogLevel=optional,                      # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                # Enable for record detailed test time information
                 PreInstance=optional,                   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeInitializeLibraryTestMethod class definition


# Beginning of PrimeInitializeServicesTestMethod class definition
class PrimeInitializeServicesTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ForceAleph=optional,               # Value to enable/disable aleph optimization to skip already parsed service configuration files.
                 ForceValidateAlephFiles=optional,  # Value to enable/disable Json schema validation for service configuration files.
                 BypassPort=optional,               # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,      # Enable for current instance's test time and memory information
                 LogLevel=optional,                 # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,           # Enable for record detailed test time information
                 PreInstance=optional,              # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,             # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeInitializeServicesTestMethod class definition


# Beginning of PrimeInlineGetDffTestMethod class definition
class PrimeInlineGetDffTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 TimeOut=optional,              # TimeOut (this comment will be used on the pre-header file).
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeInlineGetDffTestMethod class definition


# Beginning of PrimeLSARasterTestMethod class definition
class PrimeLSARasterTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ApplyEndSequence=optional,             # The ApplyEndSequence at the end of the test.
                 ExecutionMode=optional,                # Which mode to use for this instance of PrimeLSARasterTestMethod.
                 HryMapPath=optional,                   # Filepath to HryMap. Required when in Prescreen and PrescreenPrintMode is set to CTV_Mode.
                 LevelsTc=required,                     # LevelsTc for plist execution.
                 MaskPins=optional,                     # Comma separated pins for mask.
                 MetadataConfigPath=required,           # Filepath to MetadataConfig. Required for all TM instances.
                 OutputTag=optional,                    # Tag to output info for repair during Rastermode. Required for Raster is passing defects to iCRepair.
                 Patlist=optional,                      # Patlist to execute.
                 PinMappingSetName=required,            # PinMappingSet to use during execution; this is a name defined in MetadataConfig.
                 PrePlist=optional,                     # PrePlist callback to plist execution.
                 PrescreenHryFlowToken=required,        # HRY flow token for Prescreen. Used for ituff printing.
                 PrescreenHryFrequencyToken=required,   # HRY frequency token for Prescreen. Used for ituff printing.
                 PrescreenMafLimit=optional,            # Maximum number of failing arrays to print to Ituff. By default, this is set to 0, or unlimited.
                 PrescreenMapName=optional,             # Key used to store failing arrays in shared storage to be accessed later. Prescreen instance submits DB to this key, Raster instance uses this as the key to fetch from DB.
                 PrescreenPrintMode=optional,           # print mode for Prescreen. By default this is set to FAILMODE.
                 RasterConfigPath=optional,             # Filepath to RasterConfig. Required for Raster.
                 RasterMapSimulation=optional,          # A string which will simulate the internal RasterMap for this TM instance. Eliminates the need to run Prescreen by faking locations which need to be rastered..
                 ReductionConfigSetName=optional,       # ReductionConfigSet to use during Raster execution; optional if user needs to reduce internalDB.
                 TfileRasterPrint=optional,             # Whether to print to raster tfile.
                 TimingsTc=required,                    # TimingsTc for plist execution.
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeLSARasterTestMethod class definition


# Beginning of PrimeLogPcsTokensTestMethod class definition
class PrimeLogPcsTokensTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ForceAries=optional,           # ForceAries. Forces all ituff output to ARIES even if MIDAS is enabled
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeLogPcsTokensTestMethod class definition


# Beginning of PrimeLotEndDatalogTestMethod class definition
class PrimeLotEndDatalogTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 IfeObject=optional,            # Gets or sets ExtendedFunctions.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeLotEndDatalogTestMethod class definition


# Beginning of PrimeLotEndFinalizeTestMethod class definition
class PrimeLotEndFinalizeTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeLotEndFinalizeTestMethod class definition


# Beginning of PrimeLotStartDatalogTestMethod class definition
class PrimeLotStartDatalogTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 IfeObject=optional,            #  Gets or sets ExtendedFunctions.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 StreamDestination=optional,    # Stream destination for the data log file
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeLotStartDatalogTestMethod class definition


# Beginning of PrimeLotStartSetupTestMethod class definition
class PrimeLotStartSetupTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeLotStartSetupTestMethod class definition


# Beginning of PrimeLsaRasterRepairTestMethod class definition
class PrimeLsaRasterRepairTestMethod(BaseMethod):
    def __init__(self,
                 name,
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
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeLsaRasterRepairTestMethod class definition


# Beginning of NVLLsaRasterExtension class definition
class NVLLsaRasterExtension(BaseMethod):
    def __init__(self,
                 name,
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
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of NVLLsaRasterExtension class definition

# Beginning of PrimeLyaTestMethod class definition
class PrimeLyaTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 BaseNumber=optional,              # Array Base Number to be used with raster data (FA/FI). Changing numbers directly controls the RASTER HEADER.
                 BitLineBarPin=required,           # Name of the pin which acts as Bit Line Bar.
                 BitLinePin=required,              # Name of the pin which acts as Bit Line.
                 ExecutionMode=optional,           # LYA execution mode.
                 IfeObject=optional,               # IFE object of type ILyaExtensions.
                 LevelsTc=required,                # LevelsTc for plist execution.
                 LyaConfigFile=required,           # LYA configuration file full path.
                 MaxLyaCount=optional,             # Maximum LYA Tests Per instance (max. cells to test).
                 PrePause=optional,                # Gets or sets Pre-Measurement delay specified in Seconds.
                 StorageTag=required,              # Specific tag to obtain the unique shared storage name associated to the corresponding repair instance.
                 TargetArray=required,             # JSON configuration set name.
                 TimingsTc=required,               # TimingsTc for plist execution.
                 VccMaxLevel=optional,             # Max value to set the high force level on.
                 VccPin=required,                  # VCC pin to base the high force level on.
                 BypassPort=optional,              # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,     # Enable for current instance's test time and memory information
                 LogLevel=optional,                # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,          # Enable for record detailed test time information
                 PreInstance=optional,             # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,            # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 RelayTestConditionName=optional,  # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeLyaTestMethod class definition


# Beginning of PrimeMbistRasterRepairTestMethod class definition
class PrimeMbistRasterRepairTestMethod(BaseMethod):
    def __init__(self,
                 name,
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
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeMbistRasterRepairTestMethod class definition

# Beginning of PrimeMbistTestMethod class definition
class PrimeMbistTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ApplyEndSequence=optional,              # ApplyEndSequence at the end of the test.
                 BisrMode=optional,                      # Mode used to store BISR data in TP. Possible values are 'compress', 'patmod', 'birabuild', 'uncompress', 'padbisr', and 'skipcompresscheck'.
                 ClearVariables=optional,                # The ClearVariables indicate which values set by the current test method will be cleared. Possible values are: 'hry', 'bisr', 'recovery' and 'all'.
                 DffOperation=optional,                  # The Dff Operation indicates the cases in which the write to Dff should be used. Possible values are 'write', 'read', 'bisr' and 'rec'. The way it works is that it checks the 'read' and 'write' for the cases of 'bisr' and 'rec' (recovery).
                 DffSocket=optional,                     # Dff socket type.
                 FailCaptureCount=optional,              # FailCaptureCount. Setting this value to 1 will set stop-on-first-fail. Any value greater than 1 will run full plist unless used in combination with ReturnOn plist options.
                 IgnoreResetFail=optional,               # To ignore state.
                 ItuffNameExtenstion=optional,           # The ItuffNameExtenstion parameter is added to the hry tag when printing to the ituff.
                 LevelsTc=required,                      # Symbol of the levels file.
                 LookupTableConfigurationFile=optional,  # Hry LookupTableConfigurationFile.
                 MappingConfigurationFile=required,      # Mapping configuration file.
                 MaskPins=optional,                      # Comma separated pins for mask.
                 MbistTestMode=optional,                 # This parameter indicates the Mbist Test mode. Possible values are: 'Hry', 'PostRepair', 'KitchenSink', 'RepairShareBira' and 'Initialize'.
                 Patlist=required,                       # Patlist to execute.
                 PrePlist=optional,                      # PrePlist callback to plist execution.
                 PrintToItuff=optional,                  # The PrintToItuff parameter indicates which values should be printed to the ituff. Possible values are: 'hry' and 'bisrcompfail'.
                 RecoveryConfigurationFile=optional,     # RecoveryConfigurationFile.
                 RecoveryModeDownbin=optional,           # Set the recovery mode of the test instance.
                 TimingsTc=required,                     # TimingsTc for plist execution.
                 VfdmConfigurationFile=optional,         # Vfdm configuration file.
                 BypassPort=optional,                    # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,           # Enable for current instance's test time and memory information
                 LogLevel=optional,                      # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeMbistTestMethod class definition

# Beginning of PrimeMbistVminSearchTestMethod class definition
class PrimeMbistVminSearchTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 AdvancedDebug=optional,                 # Whether to collect per pattern debug.  Per controller per pattern result information.
                 ApplyEndSequence=optional,              # The ApplyEndSequence at the end of the test.
                 BisrMode=optional,                      # Mode used to store BISR data in TP.
                 ClearVariables=optional,                # Mode for clearing or not global HRY string.
                 CtvPins=optional,                       # CTV capture pins.
                 DffOperation=optional,                  # Dff Operation.
                 EndVoltageLimits=required,              # EndVoltageLimits.
                 ExecutionMode=optional,                 # Execution mode, default behaviour is Search without scoreboard. In order to enable ScoreBoard : executionMode = SearchWithScoreboard and ScoreBoardBaseNum > 0.
                 FailCaptureCount=optional,              # FailCaptureCount. Default 1 will set stop-on-first-fail. Any value greater than 1 will run full plist unless used in combination with ReturnOn plist options.
                 FeatureSwitchSettings=optional,         # FeatureSwitchSettings.
                 FivrCondition=optional,                 # FivrCondition name.
                 ForceConfigFileParseState=optional,     # The state to force parsing of a new config file for debug scenarios.
                 IfeObject=optional,                     # Gets or sets the IFE object of type IDcExtensions.
                 IgnorePrePstFail=optional,              # To ignore state.
                 ItuffNameExtenstion=optional,           # For running multiple fuse values with different ITUFF prints.
                 LevelsTc=required,                      # Level test condition to load.
                 LookupTableConfigurationFile=optional,  # LookupTableConfigurationFile.
                 MappingConfig=optional,                 # Mapping config.
                 MaskPins=optional,                      # Comma separated pins for mask.
                 MaxRepetitionCount=optional,            # The maximum number of times a search can be repeated for recovering purposes. This parameter is zero by default. Meaning, no repetition will be executed for any search.
                 MbistTestMode=optional,                 # Enables default or post repair flows.
                 MultiPassMasks=optional,                # A list containing the mask bit arrays needed for multi pass capability. Example: \"1100,0101\" indicates that two multi pass will be executed. Where elements corresponding to \"1\" mean that target will be masked or ignored for the corresponding search.
                 Patlist=required,                       # Patlist to execute.
                 PatternNameMap=optional,                # A comma separated string of integers which map characters in the pattern name to produce a scoreboard counter. Positive indexes, starting at 0, map characters at the start of the string. Negative indexes, starting at -1, map characters at the end of the string.
                 PrePlist=optional,                      # The PrePlist callback to plist execution.
                 PrintToItuff=optional,                  # Mode for printing hry string to the ituff.
                 RecoveryConfigurationFile=optional,     # RecoveryConfigurationFile.
                 RecoveryModeDownbin=optional,           # Set the recovery mode of the instancMbistTestMode.
                 ScoreboardBaseNumbers=optional,         # An integer number value to prefix the generated scoreboard fail counters.
                 ScoreboardEdgeTicks=optional,           # The number of resolution ticks to step down when scoreboard mode is enabled.
                 ScoreboardMaxFails=optional,            # The maximum number of fails that can be processed for scoreboard counters. This parameter is zero by default. If no other positive value is passed, then the maximum possible integer value will be used.
                 StartVoltages=required,                 # StartVoltageValues.
                 StartVoltagesForRetry=optional,         # LowerStartVoltages for overshoot.
                 StepSize=required,                      # StepSize.
                 TestMode=optional,                      # Enables default or post repair flows. 
                 TimingsTc=required,                     # Timing test condition to load.
                 VFDMconfig=optional,                    # VFDM config.
                 VoltageTargets=required,                # Targets.
                 BypassPort=optional,                    # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,           # Enable for current instance's test time and memory information
                 LogLevel=optional,                      # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                # Enable for record detailed test time information
                 PreInstance=optional,                   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,            # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,       # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,         # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,          # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,                # A Regular Expression to minimize the patterns in the configurations.
                 SoftwareTriggerCallBack=optional,       # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,        # The RelayTestCondition to apply.
                 PostPlist=optional,                     # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeMbistVminSearchTestMethod class definition


# Beginning of PrimeMixingDetectionTestMethod class definition
class PrimeMixingDetectionTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ConfigurationFilePath=required,  # Configuration file path.
                 BypassPort=optional,             # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,    # Enable for current instance's test time and memory information
                 LogLevel=optional,               # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,         # Enable for record detailed test time information
                 PreInstance=optional,            # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,           # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeMixingDetectionTestMethod class definition


# Beginning of PrimeOdeseBinConverterTestMethod class definition
class PrimeOdeseBinConverterTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 IfeObject=optional,            # IFE object of type IOdeseBinConverterExtensions.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeOdeseBinConverterTestMethod class definition


# Beginning of PrimePUPTestMethod class definition
class PrimePUPTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 EFuseUserFormat=optional,      # The current EFuse user format.
                 IfeObject=optional,            # IfeObject.
                 Mode=optional,                 # Operation mode.
                 MonitorLoopNum=optional,       # Monitor Loop number.
                 PatternsFilePath=optional,     # The path of the patterns file.
                 PupDebugMode=optional,         # Debug mode.
                 PupMatchMode=optional,         # The desired PUP match mode which defined how the per unit nodes in PUP.json will be matched.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimePUPTestMethod class definition


# Beginning of PrimeParticipatingDutLoggerTestMethod class definition
class PrimeParticipatingDutLoggerTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeParticipatingDutLoggerTestMethod class definition


# Beginning of PrimePassBinToSspecAndFuseAtClassBinConverterTestMethod class definition
class PrimePassBinToSspecAndFuseAtClassBinConverterTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 FactBinKey=required,                     # Shared storage key where the Fuse At Class bin should be stored.
                 PassBinKey=required,                     # Shared storage key where the PassBin is stored.
                 SspecBinsMappingObjectContext=required,  # Shared storage context in which the SspecBinsMapping object is stored.
                 SspecBinsMappingObjectKey=required,      # FRF file path or a user var that contains it.
                 SspecKey=required,                       # Shared storage key where the Sspec should be stored.
                 BypassPort=optional,                     # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,            # Enable for current instance's test time and memory information
                 LogLevel=optional,                       # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                 # Enable for record detailed test time information
                 PreInstance=optional,                    # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                   # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimePassBinToSspecAndFuseAtClassBinConverterTestMethod class definition


# Beginning of PrimePatConfigEngineeringTestMethod class definition
class PrimePatConfigEngineeringTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 EngineeringConfigurationFile=optional,  # EngineeringConfigurationFile name.
                 BypassPort=optional,                    # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,           # Enable for current instance's test time and memory information
                 LogLevel=optional,                      # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                # Enable for record detailed test time information
                 PreInstance=optional,                   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimePatConfigEngineeringTestMethod class definition


# Beginning of PrimePatConfigReApplyTestMethod class definition
class PrimePatConfigReApplyTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimePatConfigReApplyTestMethod class definition


# Beginning of PrimePatConfigTestMethod class definition
class PrimePatConfigTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ConfigurationFile=required,    # Configuration file name
                 Plist=optional,                # Pattern list name.
                 RegEx=optional,                # Pattern regex.
                 SetPoint=required,             # Set point names
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimePatConfigTestMethod class definition


# Beginning of PrimePauseTestMethod class definition
class PrimePauseTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ExitPort=optional,                 # return Port after Sleep Time. Range from 0 to 5. (Default=1)
                 SleepTime=required,                # the sleep time in milliseconds
                 BypassPort=optional,               # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,      # Enable for current instance's test time and memory information
                 LogLevel=optional,                 # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,           # Enable for record detailed test time information
                 SetPointsPlistMode=optional,       # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,  # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,    # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,     # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,           # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,              # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,             # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FlowIndex=optional,                # Parameter to specify the instance flow index on Dynamic Flows.
                 FlowIndexCallbackName=optional,    # Flow Index callback function name. in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimePauseTestMethod class definition


# Beginning of PrimePerformanceProfileTestMethod class definition
class PrimePerformanceProfileTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 GlobalInstanceSummaryMode=optional,  # Global instance summary mode.
                 MemorySummary=optional,              # Memory summary mode.
                 BypassPort=optional,                 # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,        # Enable for current instance's test time and memory information
                 LogLevel=optional,                   # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,             # Enable for record detailed test time information
                 PreInstance=optional,                # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,               # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimePerformanceProfileTestMethod class definition


# Beginning of PrimePinMonitorTestMethod class definition
class PrimePinMonitorTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ConfigurationName=optional,    # The Configuration Name.
                 DumpMode=optional,             # The Dump mode.
                 Mode=required,                 # The Monitor modes.
                 SamplingInterval=optional,     # Sampling interval in milliseconds.
                 TagName=optional,              # The suffix Tag Name for ituff purpose only.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimePinMonitorTestMethod class definition


# Beginning of PrimePinProfilerTestMethod class definition
class PrimePinProfilerTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 CallbackName=optional,         # Name of the callback to be triggered for ech tag.
                 Mode=optional,                 # Mode parameter of the test method.
                 PinNames=optional,             # List of pin names as comma separated. These can be HDDPS or TDAU pins.
                 SamplingInterval=optional,     # Sampling rate of the profile in ms. Valid only for Start mode.
                 Tag=required,                  # Name of the profile to start or stop by this test method.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimePinProfilerTestMethod class definition


# Beginning of PrimePlatformPatternCachingTestMethod class definition
class PrimePlatformPatternCachingTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 CachingBehavior=required,      # The alarm port redirect disabled or enabled.
                 EntryCapacity=required,        # The entry capacity of the pattern memory cache.
                 MaxVectorEntrySize=required,   # The maximum size of an entry to be accepted into the cache.
                 VectorCapacity=required,       # The maximum amount of vectors in the pattern memory cache.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimePlatformPatternCachingTestMethod class definition


# Beginning of PrimePowerPremonitionResponseDeviceStartTestMethod class definition
class PrimePowerPremonitionResponseDeviceStartTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 IsProfileModeEnabled=optional,  # Profile mode
                 ThermalController=optional,     # Value indicating whether to use DTC or TCC
                 BypassPort=optional,            # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,   # Enable for current instance's test time and memory information
                 LogLevel=optional,              # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,        # Enable for record detailed test time information
                 PreInstance=optional,           # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,          # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimePowerPremonitionResponseDeviceStartTestMethod class definition


# Beginning of PrimePowerPremonitionResponseInitTestMethod class definition
class PrimePowerPremonitionResponseInitTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 MinimumPercentageOfValidDTSData=optional,  # Minimum percentage of valid DTS data. Default percentage is 50%
                 ProfileInstanceFilePath=optional,          # Path to the file with the info of the instances to profile.
                 SerialCaptureDtsProfile=optional,          # value indicating whether to capture DTS data or not.
                 ThermalController=optional,                # Value indicating whether to use DTC or TCC
                 BypassPort=optional,                       # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,              # Enable for current instance's test time and memory information
                 LogLevel=optional,                         # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                   # Enable for record detailed test time information
                 PreInstance=optional,                      # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                     # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimePowerPremonitionResponseInitTestMethod class definition


# Beginning of PrimeRasterTestMethod class definition
class PrimeRasterTestMethod(BaseMethod):
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
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeRasterTestMethod class definition


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
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of NVLRasterExtension class definition

# Beginning of PrimeRepairTestMethod class definition
class PrimeRepairTestMethod(BaseMethod):
    def __init__(self,
                 name,
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
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeRepairTestMethod class definition


# Beginning of PrimeRepairToFuseTestMethod class definition
class PrimeRepairToFuseTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 EnableFuseReset=optional,       # Flag to indicate whether to reset all R2F fuses contained in the FuseManager service. Default is set to True.
                 FuseNamespace=required,         # Fuse namespace to be used to create the VirtualFuseHandler for FuseManager service.
                 IfeObject=optional,             # IFE object of type IRepairToFuseExtensions.
                 RepairToFuseFilePath=required,  # File with the repair to fuse configuration.
                 ResourcesFilePath=required,     # File with the resources configuration.
                 BypassPort=optional,            # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,   # Enable for current instance's test time and memory information
                 LogLevel=optional,              # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,        # Enable for record detailed test time information
                 PreInstance=optional,           # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,          # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeRepairToFuseTestMethod class definition


# Beginning of PrimeRvCallbacksRegistrarTestMethod class definition
class PrimeRvCallbacksRegistrarTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 IfeObject=optional,            # Gets or Sets **not in use will be removed later with the refactoring of the IfeObject**.
                 Mode=required,                 #  Gets or sets the registration mode of the RV callbacks in this instance." 
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeRvCallbacksRegistrarTestMethod class definition


# Beginning of PrimeSampleRateTestMethod class definition
class PrimeSampleRateTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 GlobalSampleRate=optional,      # Global sample rate.
                 PrintItuffExitPort=optional,    # PrintItuffExitport, DUT Sampling is based on this number.
                 SampleOption=optional,          # Wafer Sample Form.
                 SamplingRateValue=required,     # SamplingRateValue, DUT Sampling is based on this number.
                 ShouldFirstBeSampled=optional,  # Wafer Sample Form.
                 WaferSampleList=optional,       # WaferSampleList, DUT Sampling is based on this wafer list.
                 WaferSampleRateValue=optional,  # WaferSampleRateValue, Wafer Sampling is based on this number.
                 BypassPort=optional,            # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,   # Enable for current instance's test time and memory information
                 LogLevel=optional,              # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,        # Enable for record detailed test time information
                 PreInstance=optional,           # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,          # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeSampleRateTestMethod class definition


# Beginning of PrimeScanHRYSSNTestMethod class definition
class PrimeScanHRYSSNTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ApplyEndSequence=optional,                 # ApplyEndSequence at the end of the test.
                 ExpectedPartitionsStatuses=optional,       # ExpectedPartitionsStatuses.Comma-separated values of \"PartitionName=0/1/8/9/X\" (X - don't care.)\nExample: \"EXE=1, FID=X, OOO=0\
                 HRYInputFile=required,                     # HRY generation rules input file.
                 IfeObject=optional,                        # The IFE object of type IScanHRYExtensions.
                 LevelsTc=required,                         # LevelsTc for plist execution.
                 MaskPins=optional,                         # Comma separated pins for mask.
                 PartitionsToIgnore=optional,               # PartitionsToIgnore. When one of the failing partition matches one of this paritions, the test method will print 9 on the HRY string.
                 Patlist=required,                          # Patlist to execute.
                 PatternsRegexesForKill=optional,           # PatternsRegexesForKill. When one of the failing patterns, matching one of the regexes, test method will exit from dedicated port 4.\nExample: \".*pre.*, Pattern.*\
                 PerPatFailCaptureCount=optional,           # Number of Patlist execution failures to capture per pattern. The minimal number is 1.
                 PinMappingFile=required,                   # Pin mapping input file
                 PrePlist=optional,                         #  PrePlist callback to plist execution.
                 SetUnassignedToUntestedPatterns=optional,  # SetUnassignedToUntestedPatterns. If TRUE the HRY will be overriden with UNASSIGNED for those partitions that not reported failures.
                 SharedStorageHRYExportKey=optional,        # The SharedStorageHRYExportKey. This key will be used to export the HRY to shared storage under IP scope.\nThe key will be reset in all cases at beginning of execution with empty string. In case of failure, nothing will be written afterwards.
                 TimingsTc=required,                        # TimingsTc for plist execution.
                 TotalFailCaptureCount=optional,            # Number of Patlist execution failures to capture per plist.
                 BypassPort=optional,                       # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,              # Enable for current instance's test time and memory information
                 LogLevel=optional,                         # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                   # Enable for record detailed test time information
                 PreInstance=optional,                      # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                     # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,               # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,          # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,            # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,             # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,                   # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,                # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,      # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,          # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,           # The RelayTestCondition to apply.
                 PostPlist=optional,                        # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeScanHRYSSNTestMethod class definition


# Beginning of PrimeScanHRYStfTestMethod class definition
class PrimeScanHRYStfTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ApplyEndSequence=optional,               # ApplyEndSequence at the end of the test.
                 CompressedMode=optional,                 # Indicates whether CompressedMode is On or Off.
                 HryMappingDescriptorInputFile=required,  # HRY mapping descriptor file. This file contents should define the way we map a specific failure to an actual HRY index.\nThis file should be auto-generated by SPF-TOOL.
                 HryMappingInputFile=required,            # HRY mapping file. This should be a binary file, that contains mapping information that will be accessed in run-time,to determine for a specific failure, the HRY partition index.\nThis file should be auto-generated by SPF-TOOL.
                 IfeObject=optional,                      # The IFE object of type IScanHRYStfExtensions.
                 LevelsTc=required,                       # LevelsTc for plist execution.
                 MaskPins=optional,                       # Comma separated pins for mask.
                 Patlist=required,                        # Patlist to execute.
                 PatternsNotToProcessForHRY=optional,     # Comma-separated string of patterns regexes to exclude when processing failures for HRY.\nThose patterns will still be executed if they appear in plist, but their failures will not be processed.
                 PatternsRegexesForKill=optional,         # PatternsRegexesForKill. When one of the failing patterns, matching one of the regexes, test method will exit from dedicated port 3.\nExample: \".*pre.*, Pattern.*\
                 PerPatternFailCaptureCount=required,     # Number of Patlist execution failures to capture per pattern.
                 PrePlist=optional,                       #  PrePlist callback to plist execution.
                 SanityCheckInputFile=optional,           # Sanity check input file. This parameter is optional. But when not, test method will run in special mode.
                 TimingsTc=required,                      # TimingsTc for plist execution.
                 TotalFailCaptureCount=required,          # Number of Patlist execution failures to capture per plist.
                 BypassPort=optional,                     # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,            # Enable for current instance's test time and memory information
                 LogLevel=optional,                       # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                 # Enable for record detailed test time information
                 SetPointsPlistMode=optional,             # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,        # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,          # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,           # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,                 # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                    # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                   # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,              # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,    # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 RelayTestConditionName=optional,         # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,        # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PostPlist=optional,                      # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeScanHRYStfTestMethod class definition


# Beginning of PrimeScanHRYTestMethod class definition
class PrimeScanHRYTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ApplyEndSequence=optional,             # ApplyEndSequence at the end of the test.
                 ExpectedPartitionsStatuses=optional,   # ExpectedPartitionsStatuses. Comma-separated values of \"PartitionName=0/1/8/9/X\" (X - don't care.)\nExample: \"EXE=1, FID=X, OOO=0\".
                 FirstFailDataItuffPrint=optional,      # If ENABLED test method will print first fail data per pattern to ituff.
                 HRYInputFile=required,                 # HRY generation rules input file.
                 IfeObject=optional,                    # The IFE object of type IScanHRYExtensions.
                 LevelsTc=required,                     # LevelsTc for plist execution.
                 MaskPins=optional,                     # Comma separated pins for mask.
                 Patlist=required,                      # Patlist to execute.
                 PatternsRegexesForKill=optional,       # PatternsRegexForKill. When one of the failing patterns, matching one of the regexes, test method will exit from dedicated port 4.\nExample: \".*pre.*, Pattern.*\
                 PerPatFailCaptureCount=optional,       # Number of Patlist execution failures to capture per pattern. The minimal number is 1.
                 PrePlist=optional,                     #  PrePlist callback to plist execution.
                 SharedStorageHRYExportKey=optional,    # The SharedStorageHRYExportKey. This key will be used to export the HRY to shared storage under IP scope.\nThe key will be reset in all cases at beginning of execution with empty string. In case of failure, nothing will be written afterwards.
                 TimingsTc=required,                    # TimingsTc for plist execution.
                 TotalFailCaptureCount=required,        # Number of Patlist execution failures to capture per plist.
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeScanHRYTestMethod class definition


# Beginning of PrimeScanSPOFITestMethod class definition
class PrimeScanSPOFITestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ApplyEndSequence=optional,                  # ApplyEndSequence at the end of the test.
                 EngineeringSpofiOutputFolderPath=optional,  # EngineeringSpofiOutputFolderPath. Default value is empty string which will make SPOFI prints go to scan datalog file.\nIf value is not empty, a new file will be created in this folder with the unit id (vid) name 
                 IfeObject=optional,                         # The IFE object of type IScanSPOFIExtensions.
                 LevelsTc=required,                          # LevelsTc for plist execution.
                 MaskPins=optional,                          # Comma separated pins for mask.
                 Patlist=required,                           # Patlist to execute.
                 PatternsRegexesForKill=optional,            # PatternsRegexForKill. When one of the failing patterns, matching one of the regexes, test method will exit from dedicated port 2.\nExample: \".*pre.*, Pattern.*\
                 PerPatternFailCaptureCount=required,        # Number of Patlist execution failures to capture per pattern.
                 PrePlist=optional,                          #  PrePlist callback to plist execution.
                 TimingsTc=required,                         # TimingsTc for plist execution.
                 TotalFailCaptureCount=required,             # Number of Patlist execution failures to capture per plist.
                 BypassPort=optional,                        # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,               # Enable for current instance's test time and memory information
                 LogLevel=optional,                          # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                    # Enable for record detailed test time information
                 SetPointsPlistMode=optional,                # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,           # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,             # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,              # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,                    # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                       # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                      # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,                 # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,       # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 RelayTestConditionName=optional,            # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,           # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PostPlist=optional,                         # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeScanSPOFITestMethod class definition


# Beginning of PrimeScoreboardTestMethod class definition
class PrimeScoreboardTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ApplyEndSequence=optional,             # ApplyEndSequence at the end of the test.
                 BaseNumbers=optional,                  # Comma Separated string of base numbers.
                 CtvCapturePerCycleMode=optional,       # CTV capture mode. If DISABLED (default), CTV capture will be per pin. If ENABLED it will be per cycle.
                 CtvCapturePins=optional,               # Comma separated pins for CTV capture.
                 IfeObject=optional,                    # The IFE object of type IFuncCaptureExtensions.
                 LevelsTc=required,                     # LevelsTc for plist execution.
                 MaskPins=optional,                     # Comma separated pins for mask.
                 MaxFailsNum=optional,                  # The maximum fails number.
                 Patlist=required,                      # Patlist to execute.
                 PatternNameCounterIndexes=optional,    # The name of the Pattern Counter Indexes.
                 PrePlist=optional,                     #  PrePlist callback to plist execution.
                 TimingsTc=required,                    # TimingsTc for plist execution.
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeScoreboardTestMethod class definition


# Beginning of PrimeSetDffTestMethod class definition
class PrimeSetDffTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 DieId=optional,                # Die Id for the token to be set to. " 
                 TokenName=optional,            # DFF Token Name to be set. Single Token Example: TokA. " 
                 TokenValue=optional,           # DFF Value to set to the token name defined in TokenName parameter. " 
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeSetDffTestMethod class definition


# Beginning of PrimeSetIpEndSequenceTestConditionTestMethod class definition
class PrimeSetIpEndSequenceTestConditionTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 TestConditionName=required,    # Name of an existing Test Condition.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeSetIpEndSequenceTestConditionTestMethod class definition


# Beginning of PrimeSetRepairDffTestMethod class definition
class PrimeSetRepairDffTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 RepairDffFile=required,        # Path to the input file containing the information to be set to the DFF.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeSetRepairDffTestMethod class definition


# Beginning of PrimeSharedStorageInserterTestMethod class definition
class PrimeSharedStorageInserterTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 Path=required,                 # The config file path
                 Scope=optional,                # ShareStorage scope.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeSharedStorageInserterTestMethod class definition


# Beginning of PrimeShmooTestMethod class definition
class PrimeShmooTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ApplyEndSequence=optional,             # ApplyEndSequence at the end of the test.
                 ExecutionMode=optional,                # ExecutionMode. AllPin by Default.
                 IfeObject=optional,                    # The IFE object of type ExtendedFunctions.
                 LevelsTc=required,                     # LevelsTc for plist execution.
                 MaskPins=optional,                     # Comma separated pins for mask.
                 Patlist=required,                      # Patlist to execute.
                 PlotMode=optional,                     # PlotMode.
                 PowerDownBetweenPoints=optional,       # Power down between point. This will trigger EndSequence before ApplyTestCondition in PrePointExecute.
                 PrePlist=optional,                     #  PrePlist callback to plist execution.
                 PrintFormat=optional,                  # The print format for shmoo ituffs.
                 RegionalKillLimits=optional,           # The RegionalKillLimits. Format is: \"XMin, XMax, YMin, YMax\".
                 ShmooPins=optional,                    # Comma separated shmoo pins for PerPin mode.
                 TimingsTc=required,                    # TimingsTc for plist execution.
                 XAxisDatalogName=optional,             # The name used during datalog prints for X axis. Uses XAxisParam by default.
                 XAxisDatalogPrefix=optional,           # The unit prefix for scaling the X axis. (Base, Milli, Micro, Nano).
                 XAxisParam=optional,                   # XAxis Parameter.
                 XAxisParamType=optional,               # XAxis parameter type. None by Default.
                 XAxisRange=optional,                   # The  XAxisRange. Default format: \"Start: Resolution: NumberOfPoints\".
                 YAxisDatalogName=optional,             # The name used during datalog prints for Y Axis. Uses YAxisParam by default.
                 YAxisDatalogPrefix=optional,           # The prefix for scaling the Y axis. (Base, Milli, Micro, Nano).
                 YAxisParam=optional,                   # The YAxisParameter. Empty by default.
                 YAxisParamType=optional,               # XAxis parameter type. None by Default.
                 YAxisRange=optional,                   # The YAxisRange. Default format: \"Start: Resolution: NumberOfPoints\".
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeShmooTestMethod class definition


# Beginning of PrimeShopsTestMethod class definition
class PrimeShopsTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 AlarmPortRedirect=optional,     # Gets or sets the alarm port redirect disabled or enabled.
                 DatalogLevel=optional,          #  Gets or sets selects data log mode : FAIL_DATA, ALL_DATA, ALL_DATA_COMPRESS, ALL_DATA_PINMAP_COMPRESS, NONE(default).
                 DcLevelsTc=optional,            # Gets or sets LevelsTc for lower and upper Dc test.
                 EnableFlushSmartTc=optional,    # Gets or sets flag to enable flushing Levels Smart TC.
                 IfeObject=optional,             # 
                 LowerDiodeForceValue=optional,  # Gets or sets Pin Attributes for lower Dc test.
                 LowerDiodeLimitHigh=optional,   #  Gets or sets high limit to process dc results for lower diode test.
                 LowerDiodeLimitLow=optional,    # Gets or sets low limit to process dc results for lower diode test.
                 LowerLevelsTc=optional,         # Gets or sets LowerLevelsTc for functional test execution.
                 MeasureSequence=optional,       # Gets or sets MeasureSequence.
                 PatList=optional,               # Gets or sets PatList to execute.
                 Pins=optional,                  # Gets or sets comma separated pins to measure in dc test.
                 PrePause=optional,              # Gets or sets Pre-Measurement delay specified in Seconds.
                 ShopsTestType=optional,         #  Gets or sets shops test type: LOWER_SHORTS, LOWER_SHORTS_AND_OPENS, UPPER_SHORTS, UPPER_SHORTS_AND_OPENS, ALL(default).
                 TemplateMode=optional,          # Gets or sets shops test mode: DC_ONLY, FUNC_ONLY, DC_AND_FUNC(default).
                 TimingsTc=optional,             # Gets or sets TimingsTc for plist execution.
                 UpperDiodeForceValue=optional,  # Gets or sets Pin Attributes for upper Dc test.
                 UpperDiodeLimitHigh=optional,   #  Gets or sets high limit to process dc results for upper diode test.
                 UpperDiodeLimitLow=optional,    # Gets or sets low limit to process dc results for upper diode test.
                 UpperLevelsTc=optional,         # Gets or sets UpperLevelsTc for functional test execution.
                 BypassPort=optional,            # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,   # Enable for current instance's test time and memory information
                 LogLevel=optional,              # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,        # Enable for record detailed test time information
                 PreInstance=optional,           # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,          # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeShopsTestMethod class definition


# Beginning of PrimeSignalFileTestMethod class definition
class PrimeSignalFileTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ProcessGenericSignalFilesPath=required,   # Path for process generic signal files.
                 ProductSpecificSignalFilesPath=required,  # Path for product specific signal files.
                 BypassPort=optional,                      # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,             # Enable for current instance's test time and memory information
                 LogLevel=optional,                        # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                  # Enable for record detailed test time information
                 PreInstance=optional,                     # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                    # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeSignalFileTestMethod class definition


# Beginning of PrimeSimbaInitTestMethod class definition
class PrimeSimbaInitTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 SsidKeyForUltData=optional,         # The SSID key to access ULT/eFuse data.
                 UlatEnableMode=optional,            # The ULAT enable mode (OFF/PROD).
                 UlatFilePath=optional,              # The path to the ulat file. If it's empty, Simba will take the ulat file from the SCVars.SC_ULAT_FILE user variable.
                 UlatFileType=optional,              # The ULAT input file format (LOT/UNIT).
                 UnitIdentificationMethod=optional,  # The unit identification Method (VID/ULT/VID_AND_ULT).
                 BypassPort=optional,                # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,       # Enable for current instance's test time and memory information
                 LogLevel=optional,                  # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,            # Enable for record detailed test time information
                 PreInstance=optional,               # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,              # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeSimbaInitTestMethod class definition


# Beginning of PrimeSimpleSearchTestMethod class definition
class PrimeSimpleSearchTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 IfeObject=optional,                    # IFE object of type ISimpleSearchExtension.
                 LevelsTc=required,                     # LevelsTc for plist execution.
                 Patlist=required,                      # Patlist to execute.
                 SearchDirection=optional,              # Search direction. Example: Pass_to_fail, fail_to_pass.
                 SearchMethod=optional,                 # Search method. Example: Linear, Binary.
                 SearchParam=required,                  # Levels or timings specSet.
                 SearchType=optional,                   # Search type. Example: VMIN, VMAX.
                 SkipEdgeCheck=optional,                # Skip edge check.
                 TimingsTc=required,                    # TimingsTc for plist execution.
                 ValuesExpression=required,             # Point Expression. Expected input format as lowValue,highValue,resolution.
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PrePlist=optional,                     # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeSimpleSearchTestMethod class definition


# Beginning of PrimeSmartTcTestMethod class definition
class PrimeSmartTcTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 Action=optional,               # SmartTc Action. can be (DisableSmartTc, EnableSmartTc)
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeSmartTcTestMethod class definition


# Beginning of PrimeSortBinTraceTestMethod class definition
class PrimeSortBinTraceTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 BinTraceMode=required,         # The TM mode. The modes available are On and Off.
                 BinTraceName=optional,         # Bin Trace Name to turn on or off..
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeSortBinTraceTestMethod class definition


# Beginning of PrimeSortCheckBinTestMethod class definition
class PrimeSortCheckBinTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 BinStorageKeyPrefix=optional,  # The BinStorageKeyPrefix
                 ConfigurationFile=required,    # Configuration file
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeSortCheckBinTestMethod class definition


# Beginning of PrimeSortCheckpointTestMethod class definition
class PrimeSortCheckpointTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 BinTracesToCheck=required,     # List of BinTracesToCheck.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeSortCheckpointTestMethod class definition


# Beginning of PrimeSortSetBinTestMethod class definition
class PrimeSortSetBinTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 BinStorageKeyPrefix=optional,  # The BinStorageKeyPrefix
                 ConfigurationFile=required,    # Configuration file.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeSortSetBinTestMethod class definition


# Beginning of PrimeSortTBinTestMethod class definition
class PrimeSortTBinTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 BinInputs=required,              # Comma separated list of Bin Inputs to process.
                 CostKill=optional,               # Indicates whether CostKill is On or Off.
                 DesignKill=optional,             # Indicates whether DesignKill is On or Off.
                 ExpectedNumberOfFlows=required,  # Expected Number Of Flows.
                 QualityKill=optional,            # Indicates whether QualityKill is On or Off.
                 BypassPort=optional,             # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,    # Enable for current instance's test time and memory information
                 LogLevel=optional,               # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,         # Enable for record detailed test time information
                 PreInstance=optional,            # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,           # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeSortTBinTestMethod class definition


# Beginning of PrimeSspecToFuseAtClassBinConverterTestMethod class definition
class PrimeSspecToFuseAtClassBinConverterTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 FactBinKey=required,                     # Shared storage key where the Result should be stored.
                 SspecBinsMappingObjectContext=required,  # Sshared storage context in which the SspecBinsMapping object is stored.
                 SspecBinsMappingObjectKey=required,      # Shared storage key where the SspecBinsMapping object, which is a comma delimited string of passBin:sspec:factBin, is stored.
                 SspecKey=required,                       # Shared storage key where the Sspec is stored.
                 BypassPort=optional,                     # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,            # Enable for current instance's test time and memory information
                 LogLevel=optional,                       # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                 # Enable for record detailed test time information
                 PreInstance=optional,                    # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                   # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeSspecToFuseAtClassBinConverterTestMethod class definition


# Beginning of PrimeTdauParametricDataLoggerTestMethod class definition
class PrimeTdauParametricDataLoggerTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 DffTokens=optional,            # Dff tokens to be used.
                 PinNames=required,             # Comma separated pins to be used.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeTdauParametricDataLoggerTestMethod class definition


# Beginning of PrimeTdrCalibrationTestMethod class definition
class PrimeTdrCalibrationTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 AlwaysExecute=optional,        # AlwaysExecute to do TDR calibration.
                 IgnoredPins=optional,          # Comma separated IgnoredPins to exclude from TDR calibration.
                 LoadDataFromFile=optional,     # Calibration files for each PinGroups to be calibrated.
                 PinGroups=required,            # Comma separated PinGroups to do TDR calibration.
                 TdrHiLimit=optional,           # High limit of the calibration value.
                 TdrLoLimit=optional,           # Low limit of the calibration value.
                 TdrOverrides=optional,         # An input file for manually overrides TDR calibration values.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeTdrCalibrationTestMethod class definition


# Beginning of PrimeTesterMesIdCheckerTestMethod class definition
class PrimeTesterMesIdCheckerTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 IfeObject=optional,              # ExtendedFunctions
                 ValidTesterMesIdRegex=required,  # TesterMesId Regexes in comma separated list.
                 BypassPort=optional,             # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,    # Enable for current instance's test time and memory information
                 LogLevel=optional,               # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,         # Enable for record detailed test time information
                 PreInstance=optional,            # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,           # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeTesterMesIdCheckerTestMethod class definition


# Beginning of PrimeThermalControlSetInitTestMethod class definition
class PrimeThermalControlSetInitTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 TemperatureSetName=required,   # The name of the TemperatureSet to apply.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeThermalControlSetInitTestMethod class definition


# Beginning of PrimeThermalControlSetTestMethod class definition
class PrimeThermalControlSetTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ControlSet=optional,           # The name that matches desired index to choose values from.
                 UeiPinName=required,           # The name of the pin to apply a control set change.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeThermalControlSetTestMethod class definition


# Beginning of PrimeThermalEndOfTestTestMethod class definition
class PrimeThermalEndOfTestTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ContinuousReadSampleRate=optional,  # The sample rate time in milliseconds in which the continuous read will be performed.
                 IntegrityHighLimit=optional,        # The high temperature limit of a measurement integrity check.
                 IntegrityLowLimit=optional,         # The low temperature limit of a measurement integrity check.
                 LowerTolerance=required,            # The minimum tolerance value to calculate the low limits of the measurement.
                 PcsDatalogSelector=optional,        # Datalog selectors to use for each Pin.
                 PinNames=required,                  # Pins to be used.
                 UpperTolerance=required,            # The maximum tolerance value to calculate the high limits of the measurement.
                 BypassPort=optional,                # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,       # Enable for current instance's test time and memory information
                 LogLevel=optional,                  # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,            # Enable for record detailed test time information
                 PreInstance=optional,               # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,              # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeThermalEndOfTestTestMethod class definition


# Beginning of PrimeThermalRampTestMethod class definition
class PrimeThermalRampTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ApplyEndSequence=optional,             # The applySequence for the end of the test.
                 IfeObject=optional,                    # IFE object of type IThermalRampExtensions.
                 IntegrityHighLimit=optional,           # High temperature limit of a measurement integrity check.
                 IntegrityLowLimit=optional,            # Low temperature limit of a measurement integrity check.
                 LevelsTc=optional,                     # levels Test Condition used with pattern.
                 LogPinToken=optional,                  # Datalog selectors to use for each Pin when printing to ituff.
                 LowerTolerance=required,               # List of tolerance values to calculate the low limits of the measurement.
                 MaskPins=optional,                     # Pins to mask.
                 Patlist=optional,                      # optional pattern run during soak.
                 PinNames=required,                     # TDAU pins names to check.
                 PrePlist=optional,                     # PrePlist callback to plist execution
                 RampMode=required,                     # Ramp mode. changes print format.
                 SetPoints=required,                    # Set points, use one for all or one per pin.
                 Timeout=required,                      # Timeout in miliseconds
                 TimingsTc=optional,                    # Timing test Condition that used with the pattern.
                 UpperTolerance=required,               # List of tolerance values to calculate the high limits of the measurement.
                 UseAverage=optional,                   # A flag indicating whether all the pins should be averaged together before checking against the limits.
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeThermalRampTestMethod class definition


# Beginning of PrimeThermalSingleMeasurementTestMethod class definition
class PrimeThermalSingleMeasurementTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ContinuousRead=optional,            # ContinuousRead profile. can be ENABLED or DISABLED
                 ContinuousReadSampleRate=optional,  # Sample rate time in milliseconds in which the continuous read will be performed.
                 DffTokens=optional,                 # Dff tokens.
                 IntegrityHighLimit=optional,        # High temperature limit of a measurement integrity check.
                 IntegrityLowLimit=optional,         # Low temperature limit of a measurement integrity check.
                 LowerTolerance=required,            # List of tolerance values to calculate the low limits of the measurement.
                 MeasurementType=optional,           # Type of measurement
                 PinNames=required,                  # Pins names.
                 PinNamesExcluded=optional,          # Pins names to exclude
                 PreMeasurementLevelName=optional,   # Name of the Level test Condition to be applied before the measurement.
                 StorageTag=optional,                # Additional storage tag.
                 UpperTolerance=required,            # List of tolerance values to calculate the high limits of the measurement.
                 UserVarStoreNames=optional,         # List of uservar names in which the measurements for every pin will be stored.
                 BypassPort=optional,                # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,       # Enable for current instance's test time and memory information
                 LogLevel=optional,                  # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,            # Enable for record detailed test time information
                 PreInstance=optional,               # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,              # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeThermalSingleMeasurementTestMethod class definition


# Beginning of PrimeThermalUeiStreamTestMethod class definition
class PrimeThermalUeiStreamTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ActionType=required,           # Type of action. can be start or stop
                 CollectPins=required,          # Tdau pins to perform actions on.
                 DtsMode=optional,              # Dts mode for the UEI streaming.
                 UeiSlaveType=required,         # Type of Slave
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeThermalUeiStreamTestMethod class definition


# Beginning of PrimeTimeUnderStressControlTestMethod class definition
class PrimeTimeUnderStressControlTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 CustomDffToken=optional,       # Custom DFF token to save the stress time accordingly.
                 DatalogUserBin=optional,       # Reports User Bin to be reported in the Footer Section for DPC ituff.
                 DieName=optional,              # Die name to save the stress time accordingly.
                 FlowItemName=optional,         # Flow item name to be used for getting the Loop duration for Stress time.
                 FlushTimeSpan=optional,        # Flush time span, to execute FLUSH api call.
                 MaxFlowLoopTime=optional,      # Maximum time in seconds for flowLoopDuration.
                 Mode=required,                 # Logger modes.
                 SamplingInterval=optional,     # Reports sampling interval in milliseconds for stress monitoring.
                 StressTime=optional,           # Desired Stress time in seconds. Required for AutoStressDetect mode.
                 VoltageSupplies=optional,      # Comma separated list of voltage supplies to monitor for stress.
                 VoltageThreshold=optional,     # Comma separated voltage threshold per pin to be considered 'Under Stress'.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeTimeUnderStressControlTestMethod class definition


# Beginning of PrimeTiuIdentityTestMethod class definition
class PrimeTiuIdentityTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 IfeObject=optional,            # Ife object
                 ValidTiuRegex=required,        # TIU Regexes in comma separated list.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeTiuIdentityTestMethod class definition


# Beginning of PrimeTiuPowerSupplyContinuityTestMethod class definition
class PrimeTiuPowerSupplyContinuityTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ApplyEndSequence=optional,        # ApplyEndSequence at the end of the test.
                 HighLimit=optional,               # Comma separated upper limits for the measured pins.
                 LevelsTc=required,                # Levels test condition.
                 LowLimit=optional,                # Comma separated lower limits for the measured pins.
                 Pins=required,                    # Comma separated pins to get DC Results for.
                 BypassPort=optional,              # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,     # Enable for current instance's test time and memory information
                 LogLevel=optional,                # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,          # Enable for record detailed test time information
                 PreInstance=optional,             # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,            # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 RelayTestConditionName=optional,  # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeTiuPowerSupplyContinuityTestMethod class definition


# Beginning of PrimeTiuResistanceTestMethod class definition
class PrimeTiuResistanceTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ApplyEndSequence=optional,        # ApplyEndSequence at the end of the test.
                 HighLimits=optional,              # Comma separated high limits for the measured pins.
                 LevelsTc=required,                # Levels test condition.
                 LowLimits=optional,               # Comma separated low limits for the measured pins.
                 Pins=required,                    # Comma separated pins to get DC Results for. The value must be in Ohm.
                 BypassPort=optional,              # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,     # Enable for current instance's test time and memory information
                 LogLevel=optional,                # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,          # Enable for record detailed test time information
                 PreInstance=optional,             # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,            # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 RelayTestConditionName=optional,  # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeTiuResistanceTestMethod class definition


# Beginning of PrimeTiuSignalPinLeakageTestMethod class definition
class PrimeTiuSignalPinLeakageTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ApplyEndSequence=optional,        # ApplyEndSequence at the end of the test.
                 HighLimit=optional,               # Comma separated upper limits for the measured pins.
                 LevelsTc=required,                # Levels test condition.
                 LowLimit=optional,                # Comma separated lower limits for the measured pins.
                 Pins=required,                    # Comma separated pins to get DC Results for.
                 BypassPort=optional,              # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,     # Enable for current instance's test time and memory information
                 LogLevel=optional,                # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,          # Enable for record detailed test time information
                 PreInstance=optional,             # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,            # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 RelayTestConditionName=optional,  # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeTiuSignalPinLeakageTestMethod class definition


# Beginning of PrimeTriggeredDcTestMethod class definition
class PrimeTriggeredDcTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 AlarmPortRedirect=optional,             # Gets or sets the alarm port redirect disabled or enabled.
                 ApplyEndSequence=optional,              # The ApplyEndSequence at the end of the test.
                 CtvPins=optional,                       # Gets or sets comma separated pins to get CTV from the plist execution.
                 DatalogLevel=optional,                  # Gets or sets datalog level(ALL, FAIL_ONLY, COMPRESS, PINMAP_COMPRESS)
                 HighLimits=required,                    # Gets or sets comma seperated high limits for the measure pins.
                 IfeObject=optional,                     # Gets or sets the IFE object of type ITriggeredDcExtensions.
                 LevelsTc=required,                      # Gets or sets LevelsTc to use.
                 LowLimits=required,                     # Gets or sets comma separated low limits for the measure pins.
                 MaskPins=optional,                      # Gets or sets comma separated pins for mask.
                 MeasurementTypes=optional,              # Gets or sets comma separated measurement types (Current, Voltage) or (C, V).
                 Patlist=required,                       # Gets or sets PatList to use.
                 PcatMode=optional,                      # Gets or sets datalog level(All, FailOnly)
                 Pins=required,                          # Gets or sets comma separated pins to get DC results for.
                 PrePlist=optional,                      # Gets or sets the PrePlist callback to plist execution.
                 SamplingCount=optional,                 # Gets or sets sampling count per pin.
                 SoftwareTriggerConfiguration=optional,  # Gets or sets the configuration file for the software trigger event.
                 TimingsTc=required,                     # Gets or sets TimingsTc to use.
                 TriggerMapName=optional,                # Gets or sets comma seperated high limits for the measure pins.
                 BypassPort=optional,                    # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,           # Enable for current instance's test time and memory information
                 LogLevel=optional,                      # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                # Enable for record detailed test time information
                 SetPointsPlistMode=optional,            # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,       # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,         # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,          # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,                # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,             # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,   # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 RelayTestConditionName=optional,        # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,       # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PostPlist=optional,                     # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeTriggeredDcTestMethod class definition


# Beginning of PrimeTsmcUltDecoderTestMethod class definition
class PrimeTsmcUltDecoderTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 CTVOrder=optional,             # CTVs order for decoding.
                 DieIdNames=required,           # Comma separated Die Id names.
                 Offset=optional,               # Comma separated list of offsets to start ctvs decoding.
                 ULTStart=optional,             # Fab Id.
                 UserVarsList=optional,         # List of comma separated userVarNames in the format of collection.userVarName variables.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeTsmcUltDecoderTestMethod class definition


# Beginning of PrimeUltDecoderTestMethod class definition
class PrimeUltDecoderTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ApplyEndSequence=optional,             # ApplyEndSequence at the end of the test.
                 CapturePins=optional,                  # Pins name for CTV capture comma separated.
                 CtvOrder=optional,                     # CTVs order for decoding.
                 DieIdNames=required,                   # Comma separated Die Id names.
                 ExpectedBitCount=required,             # Expected total bit count.
                 IfeObject=optional,                    # IFE object of type IUltDecoderExtensions.
                 LevelsTc=optional,                     # LevelsTc to plist execution.
                 MaskPins=optional,                     # Comma separated pins for mask.
                 Offset=optional,                       # Comma separated list of offsets to start ctvs decoding.
                 PackageEfuse=optional,                 # DieId Name to print ituff as PackageEfuse.
                 Patlist=optional,                      # Patlist to execute.
                 PrePlist=optional,                     # PrePlist callback to plist execution.
                 PrintUltDataPerDieIdToItuff=optional,  # Defines if current instance has to print the ult data per die id to the ituff.
                 TimingsTc=optional,                    # TimingsTc for plist execution.
                 UserVarsList=optional,                 # List of comma separated userVarNames in the format of collection.userVarName variables.
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeUltDecoderTestMethod class definition


# Beginning of PrimeUltEncoderTestMethod class definition
class PrimeUltEncoderTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 BitCount=required,               # Expected bit count.
                 CtvOrder=optional,               # CTVs order for decoding.
                 DieIdName=optional,              # Name Die Id name, use when data are taken from share storage.
                 TargetUserVar=required,          # User var name for save the result.
                 UserVarForLotName=optional,      # User var name for lot number.
                 UserVarForWafer=optional,        # User var name for wafer.
                 UserVarForXCoordinate=optional,  # User var name for x coordinate.
                 UserVarForYCoordinate=optional,  # User var name for x coordinate.
                 BypassPort=optional,             # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,    # Enable for current instance's test time and memory information
                 LogLevel=optional,               # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,         # Enable for record detailed test time information
                 PreInstance=optional,            # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,           # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeUltEncoderTestMethod class definition


# Beginning of PrimeVMeasureLoopTestMethod class definition
class PrimeVMeasureLoopTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 CapturePins=optional,          # Gets or sets comma-separated pins for CTV capture results.
                 ConfigFile=required,           # Gets or sets the configuration file name.
                 DatalogLevel=optional,         # Gets or sets datalog level(ALL, FAIL_ONLY, COMPRESS, PINMAP_COMPRESS)
                 IfeObject=optional,            # Gets or sets The IFE object of type IFuncDcCtvExtensions.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeVMeasureLoopTestMethod class definition


# Beginning of PrimeVadtlOverallResultsToItuffTestMethod class definition
class PrimeVadtlOverallResultsToItuffTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeVadtlOverallResultsToItuffTestMethod class definition


# Beginning of PrimeVadtlTestMethod class definition
class PrimeVadtlTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ConfigurationFile=required,    # Configuration file path.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeVadtlTestMethod class definition


# Beginning of PrimeVirtualFuseExportToDffTestMethod class definition
class PrimeVirtualFuseExportToDffTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 DffToken=required,             # DffToken that will be used to export fuses data.
                 Namespace=required,            # Fuses namespace.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeVirtualFuseExportToDffTestMethod class definition


# Beginning of PrimeVirtualFuseExportToSharedStorageTestMethod class definition
class PrimeVirtualFuseExportToSharedStorageTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 EnableLatch=optional,              # Enable/Disable the fuse storage latching mechanism.
                 FdsSharedStorageKey=required,      # FDSSharedStorageKey to use for writing FDS.
                 FuseDataGap=required,              # The virtual fuse data gap fuse name.
                 FuseDescriptorGap=required,        # The virtual fuse descriptor gap fuse name.
                 GenerateFuseDataMapFile=optional,  # Enable/Disable the fuse data map file generation.
                 HcsSharedStorageKey=required,      # HCSSharedStorageKey to use for writing HCS.
                 Namespace=required,                # Fuses namespace to export.
                 Tags=required,                     # Comma separated tags to use within namespace.
                 Threshold=optional,                # Fuse capacity threshold. This threshold will determine exit port and latching logic.
                 BypassPort=optional,               # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,      # Enable for current instance's test time and memory information
                 LogLevel=optional,                 # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,           # Enable for record detailed test time information
                 PreInstance=optional,              # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,             # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeVirtualFuseExportToSharedStorageTestMethod class definition


# Beginning of PrimeVirtualFuseImportFromDffTestMethod class definition
class PrimeVirtualFuseImportFromDffTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 DffToken=required,             # Dff token to read fuses data from.
                 Namespace=required,            # Fuses namespace to update from DFF.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeVirtualFuseImportFromDffTestMethod class definition


# Beginning of PrimeVirtualFuseResetTestMethod class definition
class PrimeVirtualFuseResetTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 Namespace=required,            # Fuses namespace to export.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeVirtualFuseResetTestMethod class definition


# Beginning of PrimeVixVoxTestMethod class definition
class PrimeVixVoxTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ApplyEndSequence=optional,             # The ApplyEndSequence at the end of the test.
                 CatastrophicFailLimit=optional,        # Gets or sets catastrophic fail limit.
                 DvMode=optional,                       # Gets or sets DvMode options.
                 ExecuteMode=optional,                  # Gets or sets Test Method Execution Mode: Search Vix, Search Vox, One Pass.
                 HryLoggingMode=optional,               # Gets or sets HRY logging mode.
                 LevelsTc=required,                     # Gets or sets LevelsTc to use.
                 MaskPins=optional,                     # Gets or sets comma separated pins for mask.
                 OnePassHryPins=optional,               # Gets or sets HRY pins of interest.
                 Patlist=required,                      # Gets or sets PatList to use.
                 PrePlist=optional,                     # Gets or sets the PrePlist callback to plist execution.
                 TdoPinName=required,                   # Gets or sets TDO Pin Name.
                 TimingsTc=required,                    # Gets or sets TimingsTc to use.
                 VihVohSearchParams=optional,           # Gets or sets vih/voh search parameters.
                 VilVolSearchParams=optional,           # Gets or sets vih/voh search parameters.
                 VixPinsMask=optional,                  # Gets or sets Vix Pins to mask.
                 VoxPinsMask=optional,                  # Gets or sets Vox Pins to mask.
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeVixVoxTestMethod class definition


# Beginning of PrimeVminForwardingExportTestMethod class definition
class PrimeVminForwardingExportTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 AllFlowExpansion=optional,                          # Indicates if all flows values will be printed into the export token with frequency id.
                 AllowBypassCorners=optional,                        # Indicates if a bypass corner is allowed. If true print -9.999 if false will throw exception.
                 ExportDataLog=optional,                             # Indicates if Search and Check data will be export as the interpolator results.
                 ExportKeys=optional,                                # Export comma separated keys available to export the data.
                 ExportType=optional,                                # Export type.
                 FrequencyPrintMultiplier=optional,                  # Multiplier to be applied to the frequency values printed into the export token with frequency values.
                 IfeObject=optional,                                 # IFE object of type IVminForwardingExportExtensions.
                 IncludeDisabledCornerAtExport=optional,             # Indicates whether the Export procedure should check if the corner was disabled in one point.
                 MaxFlowNumber=optional,                             # Maximum expected flow number to export data.
                 OperationMode=required,                             # TM operation mode.
                 PreProcessInput=optional,                           # Preprocess data (ie: interpolation objects string token) input.
                 PreProcessMode=optional,                            # The data processing mode mechanism.
                 PrintOnlyPassingFlowAtFrequencyNameToken=optional,  # Indicates whether the Export token for all flows with frequency name includes only the passing flow onwards data, leaving the lower failed flows with empty data, but with the flow separator.
                 SnapshotKey=required,                               # Shared storage's key used to save the snapshot data.
                 BypassPort=optional,                                # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,                       # Enable for current instance's test time and memory information
                 LogLevel=optional,                                  # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                            # Enable for record detailed test time information
                 PreInstance=optional,                               # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                              # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeVminForwardingExportTestMethod class definition


# Beginning of PrimeVminSearchTestMethod class definition
class PrimeVminSearchTestMethod(BaseMethod):
    def __init__(self,
                 name,
                 ApplyEndSequence=optional,           # ApplyEndSequence at the end of the test.
                 BaseNumbers=optional,                # Comma separated list of numbers  to prefix the scoreboard counters.
                 EndVoltageLimits=required,           # End voltage limits.
                 ExecutionMode=optional,              # Execution mode, default behaviour is Search without scoreboard.
                 FeatureSwitchSettings=optional,      # Feature switch settings.
                 FivrCondition=optional,              # FIVR condition name.
                 IfeObject=optional,                  # IFE object of type IVminSearchExtensions.
                 LevelsTc=required,                   # Level test condition to load.
                 MaskPins=optional,                   # Comma separated string indicating which pins to mask.
                 MaxFailsNum=optional,                # Maximum number of fails that can be processed for scoreboard counters.
                 MaxRepetitionCount=optional,         # Maximum number of times a search can be repeated for recovering purposes.
                 MultiPassMasks=optional,             # Comma separated list of mask bit strings needed for multi pass capability.
                 Patlist=required,                    # Patlist to execute.
                 PatternNameCounterIndexes=optional,  # Comma separated string of integers which map characters in the pattern name to produce a scoreboard counter.
                 PrePlist=optional,                   # PrePlist callback to plist execution.
                 PrintPatternsOccurrences=optional,   # Print failing patterns occurrences to ituff.
                 ScoreboardEdgeTicks=optional,        # Number of resolution ticks to step down when scoreboard mode is enabled.
                 StartVoltages=required,              # Start voltage values.
                 StartVoltagesForRetry=optional,      # Lower start voltages for overshoot.
                 StepSize=required,                   # Search step size in Volts.
                 TimingsTc=required,                  # Timing test condition to load.
                 VoltageTargets=required,             # Voltage targets.
                 BypassPort=optional,                 # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,        # Enable for current instance's test time and memory information
                 LogLevel=optional,                   # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,             # Enable for record detailed test time information
                 PreInstance=optional,                # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,               # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,         # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,    # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,      # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,       # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,             # A Regular Expression to minimize the patterns in the configurations.
                 RelayTestConditionName=optional,     # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,    # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PostPlist=optional,                  # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeVminSearchTestMethod class definition


# Beginning of TestMethodBase class definition
class TestMethodBase(BaseMethod):
    def __init__(self,
                 name,
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of TestMethodBase class definition


# Beginning of ADMRecovery class definition
class ADMRecovery(BaseMethod):
    def __init__(self,
                 name,
                 CounterCompare=optional,                # Gets or sets mode for calculate 'POST-PRE' counter differences for each counter value in each DB column.
                 CounterGSDSUpload=optional,             # Gets or sets mode for Gsds raw counter values per fail counter type per datablock column.
                 HRYString=optional,                     # Gets or sets mode for summarize the pass/fail result on each datablock column by half channel level Write to ituff Eg: 6 bit HRY string.
                 LookupTableConfigurationFile=optional,  # Gets or sets LookupTableConfigurationFile.
                 PrimaryTracker=optional,                # Gets or sets mode for first or primary stage to upload tracker as GSDS.
                 TestResultSummary=optional,             # Gets or sets mode.
                 AlarmPortRedirect=optional,             # The alarm port redirect disabled or enabled.
                 ApplyEndSequence=optional,              # The ApplyEndSequence at the end of the test.
                 CtvCapturePerCycleMode=optional,        # CTV capture mode. If DISABLED (default), CTV capture will be per pin. If ENABLED it will be per cycle.
                 CtvCapturePins=optional,                # Comma separated pins for CTV capture.
                 DtsConfigurationName=optional,          # Configuration in case DTS processing is wanted.
                 FailuresToCapturePerPattern=optional,   # Int for number of failures per pattern to capture. If 0 (default), per pattern capture is disabled.
                 FailuresToCaptureTotal=optional,        # Int for the number of global failures to capture. If 0 (default), it means failure capture is disabled.
                 IfeObject=optional,                     #  Gets or sets the IFE object of type IFuncCaptureExtensions.
                 LevelsTc=required,                      # LevelsTc to plist execution.
                 MaskPins=optional,                      # Comma separated pins for mask.
                 MaxFailuresPerPatternToItuff=optional,  # Int for number of failures per pattern to print to ituff. If 0 (default), per pattern failure count defaults to MaxFailuresToItuff.
                 MaxFailuresToItuff=optional,            # int for the number of global failures to print to ituff. If 0 (default), it means failure prints are disabled.
                 Patlist=required,                       # Patlist to execute.
                 PrePlist=optional,                      # PrePlist callback to plist execution.
                 TimingsTc=required,                     # TimingsTc for plist execution.
                 BypassPort=optional,                    # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,           # Enable for current instance's test time and memory information
                 LogLevel=optional,                      # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                # Enable for record detailed test time information
                 SetPointsPlistMode=optional,            # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,       # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,         # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,          # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,                # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,             # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,   # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 RelayTestConditionName=optional,        # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,       # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PostPlist=optional,                     # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 FlowIndex=optional,                     # Parameter to specify the instance flow index on Dynamic Flows.
                 FlowIndexCallbackName=optional,         # Flow Index callback function name. in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of ADMRecovery class definition


# Beginning of ADMRecoveryCommonParams class definition
class ADMRecoveryCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FlowIndex=optional,                    # Parameter to specify the instance flow index on Dynamic Flows.
                 FlowIndexCallbackName=optional,        # Flow Index callback function name. in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of ADMRecoveryCommonParams class definition


# Beginning of ARLLsaRasterExtension class definition
class ARLLsaRasterExtension(BaseMethod):
    def __init__(self,
                 name,
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
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of ARLLsaRasterExtension class definition


# Beginning of ARLLsaRasterExtensionCommonParams class definition
class ARLLsaRasterExtensionCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of ARLLsaRasterExtensionCommonParams class definition


# Beginning of ARLLyaExtension class definition
class ARLLyaExtension(BaseMethod):
    def __init__(self,
                 name,
                 BaseNumber=optional,              # Array Base Number to be used with raster data (FA/FI). Changing numbers directly controls the RASTER HEADER.
                 BitLineBarPin=required,           # Name of the pin which acts as Bit Line Bar.
                 BitLinePin=required,              # Name of the pin which acts as Bit Line.
                 ExecutionMode=optional,           # LYA execution mode.
                 IfeObject=optional,               # IFE object of type ILyaExtensions.
                 LevelsTc=required,                # LevelsTc for plist execution.
                 LyaConfigFile=required,           # LYA configuration file full path.
                 MaxLyaCount=optional,             # Maximum LYA Tests Per instance (max. cells to test).
                 PrePause=optional,                # Gets or sets Pre-Measurement delay specified in Seconds.
                 StorageTag=required,              # Specific tag to obtain the unique shared storage name associated to the corresponding repair instance.
                 TargetArray=required,             # JSON configuration set name.
                 TimingsTc=required,               # TimingsTc for plist execution.
                 VccMaxLevel=optional,             # Max value to set the high force level on.
                 VccPin=required,                  # VCC pin to base the high force level on.
                 BypassPort=optional,              # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,     # Enable for current instance's test time and memory information
                 LogLevel=optional,                # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,          # Enable for record detailed test time information
                 PreInstance=optional,             # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,            # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 RelayTestConditionName=optional,  # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of ARLLyaExtension class definition


# Beginning of ARLLyaExtensionCommonParams class definition
class ARLLyaExtensionCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,             # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,            # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 RelayTestConditionName=optional,  # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of ARLLyaExtensionCommonParams class definition


# Beginning of ARLRasterExtension class definition
class ARLRasterExtension(BaseMethod):
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
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of ARLRasterExtension class definition


# Beginning of ARLRasterExtensionCommonParams class definition
class ARLRasterExtensionCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of ARLRasterExtensionCommonParams class definition


# Beginning of AnalogDcTC class definition
class AnalogDcTC(BaseMethod):
    def __init__(self,
                 name,
                 DataBaseFile=required,                  # Gets or sets the data base for the instance with all rxPairs and rcomp settings.
                 ExpectedBits=optional,                  # Gets or sets the amount of bits expected to be captured by the captured pin name.
                 FlushLevels=optional,                   # Gets or sets LEVELS_SETUP flushing after test.
                 ParallelCtvProcessing=optional,         # Gets or sets a flag to enable/disable parallel CTV processing.
                 UseSPM=optional,                        # Gets or sets SPM ITUFF format printing.
                 AlarmPortRedirect=optional,             # Gets or sets the alarm port redirect disabled or enabled.
                 ApplyEndSequence=optional,              # The ApplyEndSequence at the end of the test.
                 CtvPins=optional,                       # Gets or sets comma separated pins to get CTV from the plist execution.
                 DatalogLevel=optional,                  # Gets or sets datalog level(ALL, FAIL_ONLY, COMPRESS, PINMAP_COMPRESS)
                 HighLimits=required,                    # Gets or sets comma seperated high limits for the measure pins.
                 IfeObject=optional,                     # Gets or sets the IFE object of type ITriggeredDcExtensions.
                 LevelsTc=required,                      # Gets or sets LevelsTc to use.
                 LowLimits=required,                     # Gets or sets comma separated low limits for the measure pins.
                 MaskPins=optional,                      # Gets or sets comma separated pins for mask.
                 MeasurementTypes=optional,              # Gets or sets comma separated measurement types (Current, Voltage) or (C, V).
                 Patlist=required,                       # Gets or sets PatList to use.
                 PcatMode=optional,                      # Gets or sets datalog level(All, FailOnly)
                 Pins=required,                          # Gets or sets comma separated pins to get DC results for.
                 PrePlist=optional,                      # Gets or sets the PrePlist callback to plist execution.
                 SamplingCount=optional,                 # Gets or sets sampling count per pin.
                 SoftwareTriggerConfiguration=optional,  # Gets or sets the configuration file for the software trigger event.
                 TimingsTc=required,                     # Gets or sets TimingsTc to use.
                 TriggerMapName=optional,                # Gets or sets comma seperated high limits for the measure pins.
                 BypassPort=optional,                    # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,           # Enable for current instance's test time and memory information
                 LogLevel=optional,                      # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                # Enable for record detailed test time information
                 SetPointsPlistMode=optional,            # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,       # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,         # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,          # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,                # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,             # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,   # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 RelayTestConditionName=optional,        # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,       # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PostPlist=optional,                     # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of AnalogDcTC class definition


# Beginning of AnalogDcTCCommonParams class definition
class AnalogDcTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of AnalogDcTCCommonParams class definition


# Beginning of AnalogOutlierKill class definition
class AnalogOutlierKill(BaseMethod):
    def __init__(self,
                 name,
                 IQRMultiplier=optional,        # Multiplier to IQR method to calculate outliers.
                 Percentile=optional,           # P (percentile) value to be used on UXPY method to calculate outliers.
                 U=optional,                    # U value to be used on UXPY method to calculate outliers.
                 ZScoreLimit=optional,          # Z-Score Limit to be used to calculate outliers.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of AnalogOutlierKill class definition


# Beginning of AnalogOutlierKillCommonParams class definition
class AnalogOutlierKillCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of AnalogOutlierKillCommonParams class definition


# Beginning of ArrayHRY class definition
class ArrayHRY(BaseMethod):
    def __init__(self,
                 name,
                 ConfigFile=required,                   # Gets or sets the Configuration File.
                 LevelsTc=required,                     # Gets or sets LevelsTc for plist execution.
                 MaskPins=optional,                     # Gets or sets comma separated pins for mask.
                 Patlist=required,                      # Gets or sets Patlist to execute.
                 RawStringForwardingMode=optional,      # Gets or sets the Raw String forwarding mode.
                 SharedStorageKey=optional,             # Gets or sets the Key to be used with Raw STring Forwarding mode. If empty the mode is disabled.
                 TimingsTc=required,                    # Gets or sets TimingsTc for plist execution.
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PrePlist=optional,                     # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of ArrayHRY class definition


# Beginning of ArrayHRYCommonParams class definition
class ArrayHRYCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PrePlist=optional,                     # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of ArrayHRYCommonParams class definition


# Beginning of ArrayRepair_EDRAM class definition
class ArrayRepair_EDRAM(BaseMethod):
    def __init__(self,
                 name,
                 EnableRaster=optional,                 # Gets or sets Raster mode.
                 EnableRepair=optional,                 # Gets or sets Repair mode.
                 IoFixThreshold=optional,               # Gets or sets Defect Threshold for IO Fix.
                 MaxDefectsToProcess=optional,          # Gets or sets Max Number of Defects to Process Per DB.
                 PatconfigAGUSMAX=optional,             # Gets or sets Patmod configuration for label AGU_S_MAX.
                 PatconfigAGUSMIN=optional,             # Gets or sets Patmod configuration for label AGU_S_MIN.
                 RepairAlgo=optional,                   # Gets or sets Repair mode.
                 RowMustFixThreshold=optional,          # Gets or sets Defect Threshold for Must Fix.
                 RowNonMustFixThreshold=optional,       # Gets or sets Defect Threshold for Non-Must Fix.
                 SimFile=optional,                      # Gets or sets simulation input file. When it's empty data will be taken normally from defects parser and resources file. But when it's populated, it will be parsed and repair algorithm will take the data from it. Note that these things will be affected when using SimFile: ArrayLoopCallback(), DefectParserCallback() and RepairCallback().
                 ApplyEndSequence=optional,             # Gets or sets the ApplyEndSequence at the end of the test.
                 ArrayName=required,                    # Gets or sets ArrayName to plist execution.
                 BaseNumber=required,                   # Gets or sets BaseNumber for R-file printing.
                 CtvPinNames=required,                  # Gets or sets CtvPinNames to capture.
                 IfeObject=optional,                    # Gets or sets The IFE object of type IArrayRepairExtensions.
                 LevelsTc=required,                     # Gets or sets LevelsTc to plist execution.
                 MaskPins=optional,                     # Gets or sets comma separated pins for mask.
                 Patlist=required,                      # Gets or sets Patlist to execute.
                 PrePlist=optional,                     # Gets or sets the PrePlist callback to plist execution.
                 RasterConfigFile=optional,             # Gets or sets RasterConfigFile input file.
                 ResourcesFile=required,                # Gets or sets ResourcesFile input file.
                 TimingsTc=required,                    # Gets or sets TimingsTc for plist execution.
                 TotalFailCaptureCount=optional,        # Gets or sets number of Patlist execution failures to capture per plist.
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of ArrayRepair_EDRAM class definition


# Beginning of ArrayRepair_EDRAMCommonParams class definition
class ArrayRepair_EDRAMCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of ArrayRepair_EDRAMCommonParams class definition


# Beginning of AssertTC class definition
class AssertTC(BaseMethod):
    def __init__(self,
                 name,
                 Bench=optional,                # Enables bench validation.
                 InputFile=required,            # Input file name.
                 Offline=optional,              # Enables offline validation.
                 Production=optional,           # Enables production validation.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of AssertTC class definition


# Beginning of AssertTCCommonParams class definition
class AssertTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of AssertTCCommonParams class definition


# Beginning of AuxiliaryTC class definition
class AuxiliaryTC(BaseMethod):
    def __init__(self,
                 name,
                 DataType=optional,             # Type of the expression result.
                 Datalog=optional,              # Specifies whether to enable/disable the Datalogging to Ituff.
                 Expression=required,           # Ncalc Expression to evaluate.
                 ResultPort=optional,           # Specifies when to log the CTV.
                 ResultToken=optional,          # Specifies the name of the Token to store the results.
                 Storage=optional,              # Specifies where to store the result..
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of AuxiliaryTC class definition


# Beginning of AuxiliaryTCCommonParams class definition
class AuxiliaryTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of AuxiliaryTCCommonParams class definition


# Beginning of BackgroundPatConfig class definition
class BackgroundPatConfig(BaseMethod):
    def __init__(self,
                 name,
                 FuseConfigFile=optional,         # Gets or sets the file which defines the FuseConfigs to execute.
                 Mode=optional,                   # Gets or sets Mode of the template.
                 PatConfigSetpointList=optional,  # Gets or sets the list of PatConfigSetpoints to execute.
                 WaitTimeout=optional,            # Gets or sets the Timeout in milliseconds for Wait mode.
                 BypassPort=optional,             # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,    # Enable for current instance's test time and memory information
                 LogLevel=optional,               # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,         # Enable for record detailed test time information
                 PreInstance=optional,            # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,           # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of BackgroundPatConfig class definition


# Beginning of BackgroundPatConfigCommonParams class definition
class BackgroundPatConfigCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of BackgroundPatConfigCommonParams class definition


# Beginning of BinRulesTC class definition
class BinRulesTC(BaseMethod):
    def __init__(self,
                 name,
                 InputFile=required,            # Gets or sets the name of the input file.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of BinRulesTC class definition


# Beginning of BinRulesTCCommonParams class definition
class BinRulesTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of BinRulesTCCommonParams class definition


# Beginning of BisrRepairCheckTC class definition
class BisrRepairCheckTC(BaseMethod):
    def __init__(self,
                 name,
                 AllowRefuse=optional,                   # Gets or sets enables Refusing of parts.
                 LookupTableConfigurationFile=required,  # Gets or sets LookupTableConfigurationFile.
                 MappingConfig=required,                 # Gets or sets  Mapping Config.
                 RepairCheckBisrName=optional,           # Gets or sets  Mapping Config.
                 AlarmPortRedirect=optional,             # The alarm port redirect disabled or enabled.
                 ApplyEndSequence=optional,              # The ApplyEndSequence at the end of the test.
                 CtvCapturePerCycleMode=optional,        # CTV capture mode. If DISABLED (default), CTV capture will be per pin. If ENABLED it will be per cycle.
                 CtvCapturePins=optional,                # Comma separated pins for CTV capture.
                 DtsConfigurationName=optional,          # Configuration in case DTS processing is wanted.
                 FailuresToCapturePerPattern=optional,   # Int for number of failures per pattern to capture. If 0 (default), per pattern capture is disabled.
                 FailuresToCaptureTotal=optional,        # Int for the number of global failures to capture. If 0 (default), it means failure capture is disabled.
                 IfeObject=optional,                     #  Gets or sets the IFE object of type IFuncCaptureExtensions.
                 LevelsTc=required,                      # LevelsTc to plist execution.
                 MaskPins=optional,                      # Comma separated pins for mask.
                 MaxFailuresPerPatternToItuff=optional,  # Int for number of failures per pattern to print to ituff. If 0 (default), per pattern failure count defaults to MaxFailuresToItuff.
                 MaxFailuresToItuff=optional,            # int for the number of global failures to print to ituff. If 0 (default), it means failure prints are disabled.
                 Patlist=required,                       # Patlist to execute.
                 PrePlist=optional,                      # PrePlist callback to plist execution.
                 TimingsTc=required,                     # TimingsTc for plist execution.
                 BypassPort=optional,                    # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,           # Enable for current instance's test time and memory information
                 LogLevel=optional,                      # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                # Enable for record detailed test time information
                 SetPointsPlistMode=optional,            # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,       # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,         # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,          # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,                # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,             # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,   # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 RelayTestConditionName=optional,        # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,       # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PostPlist=optional,                     # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of BisrRepairCheckTC class definition


# Beginning of BisrRepairCheckTCCommonParams class definition
class BisrRepairCheckTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of BisrRepairCheckTCCommonParams class definition


# Beginning of CallbacksManager class definition
class CallbacksManager(BaseMethod):
    def __init__(self,
                 name,
                 IfeObject=optional,            # Gets or Sets **not in use will be removed later with the refactoring of the IfeObject**.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of CallbacksManager class definition


# Beginning of CallbacksManagerCommonParams class definition
class CallbacksManagerCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of CallbacksManagerCommonParams class definition


# Beginning of ConcurrentPlistTracer class definition
class ConcurrentPlistTracer(BaseMethod):
    def __init__(self,
                 name,
                 PatConfigForCtv=required,               # Gets or sets the name of the Prime PatConfig used to add/remove CTV data for tracing.
                 AlarmPortRedirect=optional,             # The alarm port redirect disabled or enabled.
                 ApplyEndSequence=optional,              # The ApplyEndSequence at the end of the test.
                 CtvCapturePerCycleMode=optional,        # CTV capture mode. If DISABLED (default), CTV capture will be per pin. If ENABLED it will be per cycle.
                 CtvCapturePins=optional,                # Comma separated pins for CTV capture.
                 DtsConfigurationName=optional,          # Configuration in case DTS processing is wanted.
                 FailuresToCapturePerPattern=optional,   # Int for number of failures per pattern to capture. If 0 (default), per pattern capture is disabled.
                 FailuresToCaptureTotal=optional,        # Int for the number of global failures to capture. If 0 (default), it means failure capture is disabled.
                 IfeObject=optional,                     #  Gets or sets the IFE object of type IFuncCaptureExtensions.
                 LevelsTc=required,                      # LevelsTc to plist execution.
                 MaskPins=optional,                      # Comma separated pins for mask.
                 MaxFailuresPerPatternToItuff=optional,  # Int for number of failures per pattern to print to ituff. If 0 (default), per pattern failure count defaults to MaxFailuresToItuff.
                 MaxFailuresToItuff=optional,            # int for the number of global failures to print to ituff. If 0 (default), it means failure prints are disabled.
                 Patlist=required,                       # Patlist to execute.
                 PrePlist=optional,                      # PrePlist callback to plist execution.
                 TimingsTc=required,                     # TimingsTc for plist execution.
                 BypassPort=optional,                    # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,           # Enable for current instance's test time and memory information
                 LogLevel=optional,                      # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                # Enable for record detailed test time information
                 SetPointsPlistMode=optional,            # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,       # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,         # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,          # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,                # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,             # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,   # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 RelayTestConditionName=optional,        # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,       # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PostPlist=optional,                     # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of ConcurrentPlistTracer class definition


# Beginning of ConcurrentPlistTracerCommonParams class definition
class ConcurrentPlistTracerCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of ConcurrentPlistTracerCommonParams class definition


# Beginning of ConcurrentTracesVminTC class definition
class ConcurrentTracesVminTC(BaseMethod):
    def __init__(self,
                 name,
                 BundleSearchSpec=required,           # Gets or sets the BundleSearchSpec configuration file.
                 ContentSpec=required,                # Gets or sets the ContentSpec configuration file.
                 ForwardingMode=optional,             # Gets or sets forwarding mode for the VminForwarding Table.
                 LimitGuardband=optional,             # Gets or sets LimitGuardband to be used with VminForwarding SearchGuardbandEnabled option.
                 PinMap=optional,                     # Gets or sets recovery map name. User can enter Json stream or input file.
                 RecoveryGroupSize=optional,          # Gets or sets a comma-separated list of values of how many pinmaps/recoverytokens bits to use for each voltage target.
                 RecoveryTrackingIncoming=optional,   # Gets or sets an recovery tracking name to be sourced.
                 StartVoltagesOffset=optional,        # Gets or sets an offset to the calculated start voltage.
                 TestProgramSpec=required,            # Gets or sets the TestProgramSpec configuration file.
                 VminResult=optional,                 # Gets or sets Shared Storage Token names to store vmin results to. Use only the token names (no G.U.D. prefix), it automatically stores value in DUT/Double tables.
                 VoltageConverter=optional,           # Gets or sets the VoltageConverter parameters for DLVR.
                 VoltagesOffset=optional,             # Gets or sets an offset to applied voltage.
                 ApplyEndSequence=optional,           # ApplyEndSequence at the end of the test.
                 BaseNumbers=optional,                # Comma separated list of numbers  to prefix the scoreboard counters.
                 EndVoltageLimits=required,           # End voltage limits.
                 ExecutionMode=optional,              # Execution mode, default behaviour is Search without scoreboard.
                 FeatureSwitchSettings=optional,      # Feature switch settings.
                 FivrCondition=optional,              # FIVR condition name.
                 IfeObject=optional,                  # IFE object of type IVminSearchExtensions.
                 LevelsTc=required,                   # Level test condition to load.
                 MaskPins=optional,                   # Comma separated string indicating which pins to mask.
                 MaxFailsNum=optional,                # Maximum number of fails that can be processed for scoreboard counters.
                 MaxRepetitionCount=optional,         # Maximum number of times a search can be repeated for recovering purposes.
                 MultiPassMasks=optional,             # Comma separated list of mask bit strings needed for multi pass capability.
                 Patlist=required,                    # Patlist to execute.
                 PatternNameCounterIndexes=optional,  # Comma separated string of integers which map characters in the pattern name to produce a scoreboard counter.
                 PrePlist=optional,                   # PrePlist callback to plist execution.
                 PrintPatternsOccurrences=optional,   # Print failing patterns occurrences to ituff.
                 ScoreboardEdgeTicks=optional,        # Number of resolution ticks to step down when scoreboard mode is enabled.
                 StartVoltages=required,              # Start voltage values.
                 StartVoltagesForRetry=optional,      # Lower start voltages for overshoot.
                 StepSize=required,                   # Search step size in Volts.
                 TimingsTc=required,                  # Timing test condition to load.
                 VoltageTargets=required,             # Voltage targets.
                 BypassPort=optional,                 # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,        # Enable for current instance's test time and memory information
                 LogLevel=optional,                   # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,             # Enable for record detailed test time information
                 PreInstance=optional,                # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,               # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,         # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,    # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,      # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,       # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,             # A Regular Expression to minimize the patterns in the configurations.
                 RelayTestConditionName=optional,     # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,    # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PostPlist=optional,                  # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of ConcurrentTracesVminTC class definition


# Beginning of ConcurrentTracesVminTCCommonParams class definition
class ConcurrentTracesVminTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,              # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,             # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,       # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,  # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,    # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,     # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,           # A Regular Expression to minimize the patterns in the configurations.
                 SoftwareTriggerCallBack=optional,  # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,   # The RelayTestCondition to apply.
                 PostPlist=optional,                # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of ConcurrentTracesVminTCCommonParams class definition


# Beginning of CsioCmemTC class definition
class CsioCmemTC(BaseMethod):
    def __init__(self,
                 name,
                 ApplyEndSequence=optional,             # Gets or sets ApplyEndSequence.
                 CtvCapturePins=required,               # Gets or sets CtvCapturePins.
                 EdcEnable=optional,                    # Gets or sets Enable flag for additional EDC datalog.
                 FunctionCall=required,                 # Gets or sets Config_set.
                 IpConfigurationFile=required,          # Gets or sets ConfigurationFile.
                 KillDecode=optional,                   # Gets or sets KillDecode feature.
                 LevelsTc=required,                     # Levels TestCondition to use.
                 LimitsConfigurationFile=required,      # Gets or sets ConfigurationFile.
                 MaskPins=optional,                     # Gets or sets MaskPins.
                 Patlist=required,                      # PatternList to execute.
                 PlistConfigSet=required,               # Gets or sets which Plist block to use from IpMap.
                 PlistConfigurationFile=required,       # Gets or sets ConfigurationFile.
                 PrePlist=optional,                     # Gets or sets PrePlist.
                 TimingsTc=required,                    # Timing TestCondition to use.
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of CsioCmemTC class definition


# Beginning of CsioCmemTCCommonParams class definition
class CsioCmemTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of CsioCmemTCCommonParams class definition


# Beginning of CtvDecoderSpm class definition
class CtvDecoderSpm(BaseMethod):
    def __init__(self,
                 name,
                 ApplyEndSequence=optional,             # Gets or sets the ApplyEndSequence at the end of the test.
                 CapturePatternFailures=optional,       # Gets or sets the CapturePatternFailures.
                 ConfigurationFile=required,            # Gets or sets ConfigFile with dataStructure parameters.
                 CsvOutput=optional,                    # Gets or sets output CSV file.
                 CtvCapturePins=optional,               # Gets or sets comma separated pins for CTV capture.
                 Defeature=optional,                    # Gets or sets Defeature.
                 DieIdDisable=optional,                 # Gets or sets comma separated list of SSIDs to be disabled (ignored) during CTV processing.
                 DieIdRename=optional,                  # Gets or sets the DieIdRename.
                 ItuffHRYFailurePrint=optional,         # Gets or sets the ituff mode.
                 ItuffMode=optional,                    # Gets or sets the ituff mode..
                 ItuffSampleRate=optional,              # Gets or sets the ituff mode..
                 LevelsTc=required,                     # Gets or sets LevelsTc to plist execution.
                 MaskPins=optional,                     # Gets or sets comma separated pins for mask.
                 Patlist=required,                      # Gets or sets Pat-list to execute.
                 PatternFailuresToCapture=optional,     # Gets or sets the PatternFailuresToCapture.
                 PerDieBinning=optional,                # Gets or sets the PerDieBinning.
                 PrePlist=optional,                     # Gets or sets PrePlist.
                 TimingsTc=required,                    # Gets or sets TimingsTc for plist execution.
                 TriggerMapName=optional,               # Gets or sets trigger map.
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of CtvDecoderSpm class definition


# Beginning of CtvDecoderSpmCommonParams class definition
class CtvDecoderSpmCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of CtvDecoderSpmCommonParams class definition


# Beginning of CtvTokensTC class definition
class CtvTokensTC(BaseMethod):
    def __init__(self,
                 name,
                 ConfigurationFile=required,             # Gets or sets the configuration file.
                 ExpectedBits=required,                  # Gets or sets the amount of bits expected to be captured by the captured pin name.
                 LogMode=optional,                       # Gets or sets the datalog mode.
                 Set=required,                           # Gets or sets the configuration set to run.
                 TriggerMap=optional,                    # Gets or sets the TriggerMap name from the .ptm file to use for pattern based Vbump with an EXTTrigger.
                 AlarmPortRedirect=optional,             # The alarm port redirect disabled or enabled.
                 ApplyEndSequence=optional,              # The ApplyEndSequence at the end of the test.
                 CtvCapturePerCycleMode=optional,        # CTV capture mode. If DISABLED (default), CTV capture will be per pin. If ENABLED it will be per cycle.
                 CtvCapturePins=optional,                # Comma separated pins for CTV capture.
                 DtsConfigurationName=optional,          # Configuration in case DTS processing is wanted.
                 FailuresToCapturePerPattern=optional,   # Int for number of failures per pattern to capture. If 0 (default), per pattern capture is disabled.
                 FailuresToCaptureTotal=optional,        # Int for the number of global failures to capture. If 0 (default), it means failure capture is disabled.
                 IfeObject=optional,                     #  Gets or sets the IFE object of type IFuncCaptureExtensions.
                 LevelsTc=required,                      # LevelsTc to plist execution.
                 MaskPins=optional,                      # Comma separated pins for mask.
                 MaxFailuresPerPatternToItuff=optional,  # Int for number of failures per pattern to print to ituff. If 0 (default), per pattern failure count defaults to MaxFailuresToItuff.
                 MaxFailuresToItuff=optional,            # int for the number of global failures to print to ituff. If 0 (default), it means failure prints are disabled.
                 Patlist=required,                       # Patlist to execute.
                 PrePlist=optional,                      # PrePlist callback to plist execution.
                 TimingsTc=required,                     # TimingsTc for plist execution.
                 BypassPort=optional,                    # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,           # Enable for current instance's test time and memory information
                 LogLevel=optional,                      # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                # Enable for record detailed test time information
                 SetPointsPlistMode=optional,            # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,       # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,         # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,          # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,                # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,             # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,   # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 RelayTestConditionName=optional,        # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,       # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PostPlist=optional,                     # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of CtvTokensTC class definition


# Beginning of CtvTokensTCCommonParams class definition
class CtvTokensTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of CtvTokensTCCommonParams class definition


# Beginning of DDGCapturePacketsTC class definition
class DDGCapturePacketsTC(BaseMethod):
    def __init__(self,
                 name,
                 DataPins=required,                     # Gets or sets comma separated pins for CTV capture.
                 ExecutionMode=optional,                # Gets or sets the GSDS tokens where the decoded packets will be saved.
                 LevelsTc=required,                     # Gets or sets LevelsTc for plist execution.
                 MaskPins=optional,                     # Gets or sets  comma separated pins for mask.
                 OutputGsds=required,                   # Gets or sets the GSDS tokens where the decoded packets will be saved.
                 Patlist=required,                      # Gets or sets Patlist to execute.
                 TimingsTc=required,                    # Gets or sets TimingsTc for plist execution.
                 TotalSize=optional,                    # Gets or sets the length of all the valid data captured. If this amount mismatches the length of the valid captured data, the instance fails. This parameter is optional; if empty, the size is not checked.
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PrePlist=optional,                     # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of DDGCapturePacketsTC class definition


# Beginning of DDGCapturePacketsTCCommonParams class definition
class DDGCapturePacketsTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PrePlist=optional,                     # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of DDGCapturePacketsTCCommonParams class definition


# Beginning of DDGFunctionalTC class definition
class DDGFunctionalTC(BaseMethod):
    def __init__(self,
                 name,
                 AlarmPortRedirect=optional,             # Gets or sets the alarm port redirect disabled or enabled.
                 ApplyEndSequence=optional,              # Gets or sets the ApplyEndSequence at the end of the test.
                 CapturedDataTokens=optional,            # Gets or sets a list of comma-separated SharedStorage tokens to store captured data per pin.
                 CtvCapturePerCycleMode=optional,        # Gets or sets CTV capture mode. If DISABLED (default), CTV capture will be per pin. If ENABLED it will be per cycle.
                 CtvCapturePins=optional,                # Gets or sets comma separated pins for CTV capture.
                 DtsConfigurationName=optional,          # Gets or sets the configuration in case DTS processing is wanted.
                 FailuresToCapturePerPattern=optional,   # Gets or sets int for number of failures per pattern to capture. If 0 (default), per pattern capture is disabled.
                 FailuresToCaptureTotal=optional,        # Gets or sets int for the number of global failures to capture. If 0 (default), it means failure capture is disabled.
                 IfeObject=optional,                     # Gets or sets the IFE object of type IFuncCaptureExtensions.
                 LevelsTc=optional,                      # Gets or sets LevelsTc for plist execution.
                 MaskPins=optional,                      # Gets or sets  comma separated pins for mask.
                 MaxFailuresPerPatternToItuff=optional,  # Gets or sets int for number of failures per pattern to print to ituff. If 0 (default), per pattern failure count defaults to MaxFailuresToItuff.
                 MaxFailuresToItuff=optional,            # Gets or sets int for the number of global failures to print to ituff. If 0 (default), it means failure prints are disabled.
                 Patlist=optional,                       # Gets or sets Patlist to execute.
                 PrintPreviousLabel=optional,            # Gets or sets a option to print previous label.
                 TimingsTc=optional,                     # Gets or sets TimingsTc for plist execution.
                 BypassPort=optional,                    # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,           # Enable for current instance's test time and memory information
                 LogLevel=optional,                      # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                # Enable for record detailed test time information
                 PreInstance=optional,                   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,            # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,       # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,         # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,          # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,                # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,             # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,   # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,       # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,        # The RelayTestCondition to apply.
                 PrePlist=optional,                      # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                     # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of DDGFunctionalTC class definition


# Beginning of DDGFunctionalTCCommonParams class definition
class DDGFunctionalTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PrePlist=optional,                     # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of DDGFunctionalTCCommonParams class definition


# Beginning of DDGShmooTC class definition
class DDGShmooTC(BaseMethod):
    def __init__(self,
                 name,
                 ApplyEndSequence=optional,             # Gets or sets the ApplyEndSequence at the end of the test.
                 ExecutionMode=optional,                # Gets or sets the ExecutionMode. None by AllPin.
                 IfeObject=optional,                    # Gets or sets ExtendedFunctions.
                 LevelsTc=required,                     # Gets or sets LevelsTc to plist execution.
                 MaskPins=optional,                     # Gets or sets comma separated pins for mask.
                 Patlist=required,                      # Gets or sets Patlist to execute.
                 PlotMode=optional,                     # Gets or sets PlotMode.
                 PowerDownBetweenPoints=optional,       # Gets or sets power_down_between_point. This will trigger EndSequence before ApplyTestCondition in PrePointExecute.
                 PrePointExecMode=optional,             # Gets or sets the PrePointExec Mode.
                 PrePointExecTest=optional,             # Gets or sets the test to run when PrePointExec mode is enabled.
                 PrintFormat=optional,                  # Gets or sets the print format for shmoo ituffs.
                 RegionalKillLimits=optional,           # Gets or sets the RegionalKillLimits. Format is: "XMin, XMax, YMin, YMax".
                 ShmooPins=optional,                    # Gets or sets comma separated shmoo pins for PerPin mode.
                 TimingsTc=required,                    # Gets or sets TimingsTc for plist execution.
                 VoltageConverter=optional,             # Gets or sets a list of voltage overrides.
                 XAxisDatalogName=optional,             # Gets or sets the name used during datalog prints for X axis. Uses XAxisParam by default.
                 XAxisDatalogPrefix=optional,           # Gets or sets the unit prefix for scaling the X axis. (Base, Milli, Micro, Nano).
                 XAxisParam=optional,                   # Gets or sets the XAxisParameter. Empty by default.
                 XAxisParamType=optional,               # Use YAxisType. Set this to UserDefined or None if XAxisType is also None.
                 XAxisRange=optional,                   # Gets or sets the XAxisRange. Default format: "Start: Resolution: NumberOfPoints".
                 XAxisType=optional,                    # Gets or sets the XAxisType parameter.
                 YAxisDatalogName=optional,             # Gets or sets the name used during datalog prints for Y Axis. Uses YAxisParam by default.
                 YAxisDatalogPrefix=optional,           # Gets or sets the unit prefix for scaling the Y axis. (Base, Milli, Micro, Nano).
                 YAxisParam=optional,                   # Gets or sets the YAxisParameter. Empty by default.
                 YAxisParamType=optional,               # Use YAxisType. Set this to UserDefined or None if YAxisType is also None.
                 YAxisRange=optional,                   # Gets or sets the YAxisRange. Default format: "Start: Resolution: NumberOfPoints".
                 YAxisType=optional,                    # Gets or sets the YAxisType parameter.
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PrePlist=optional,                     # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of DDGShmooTC class definition


# Beginning of DDGShmooTCCommonParams class definition
class DDGShmooTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PrePlist=optional,                     # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of DDGShmooTCCommonParams class definition


# Beginning of DTSBase class definition
class DTSBase(BaseMethod):
    def __init__(self,
                 name,
                 ConfigurationFile=required,     # Gets or sets the voltage converter ActiveConfiguration file.
                 VoltageTargetMapping=optional,  # Gets or sets the voltage targets to sensors mapping.
                 BypassPort=optional,            # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,   # Enable for current instance's test time and memory information
                 LogLevel=optional,              # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,        # Enable for record detailed test time information
                 PreInstance=optional,           # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,          # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of DTSBase class definition


# Beginning of DTSBaseCommonParams class definition
class DTSBaseCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of DTSBaseCommonParams class definition


# Beginning of DUSTI_Configure class definition
class DUSTI_Configure(BaseMethod):
    def __init__(self,
                 name,
                 AckWaitTime=required,          # Gets or sets  the wait time between writing an I2C command to reading a completion value.
                 AttemptCount=required,         # Gets or sets  the count of attempts we try to execute the I2C command.
                 ForceFlow=required,            # Gets or sets  the flow to pass, no failures.
                 FpgaWaitTime=required,         # Gets or sets  the wait time to get the FPGA value.
                 LevelsOption=required,         # Gets or Sets Levels Load option.  Not required.
                 McuReset=required,             # Gets or sets  Reset of the MCU.  True or False.
                 PinName=required,              # Gets or Sets Levels Load option.  Not required.
                 PlistOption=required,          # Gets or Sets PLIST Load option.  Not required.
                 TimingsOption=required,        # Gets or Sets Timings Load option.  Not required.
                 XMLInputFile=required,         # Gets or sets the XML Input file.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of DUSTI_Configure class definition


# Beginning of DUSTI_ConfigureCommonParams class definition
class DUSTI_ConfigureCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of DUSTI_ConfigureCommonParams class definition


# Beginning of DUSTI_StartLogging class definition
class DUSTI_StartLogging(BaseMethod):
    def __init__(self,
                 name,
                 AckWaitTime=required,          # Gets or sets  the wait time between writing an I2C command to reading a completion value.
                 AttemptCount=required,         # Gets or sets  the count of attempts we try to execute the I2C command.
                 ForceFlow=required,            # Gets or sets  the flow to pass, no failures.
                 FpgaWaitTime=required,         # Gets or sets  the wait time to get the FPGA value.
                 LevelsOption=required,         # Gets or Sets Levels Load option.  Not required.
                 PinName=required,              # Gets or Sets Levels Load option.  Not required.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of DUSTI_StartLogging class definition


# Beginning of DUSTI_StartLoggingCommonParams class definition
class DUSTI_StartLoggingCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of DUSTI_StartLoggingCommonParams class definition


# Beginning of DUSTI_StopLogging class definition
class DUSTI_StopLogging(BaseMethod):
    def __init__(self,
                 name,
                 AckWaitTime=required,          # Gets or sets  the wait time between writing an I2C command to reading a completion value.
                 AttemptCount=required,         # Gets or sets  the count of attempts we try to execute the I2C command.
                 ForceFlow=required,            # Gets or sets  the flow to pass, no failures.
                 FpgaWaitTime=required,         # Gets or sets  the wait time to get the FPGA value.
                 LevelsOption=required,         # Gets or Sets Levels Load option.  Not required.
                 PinName=required,              # Gets or Sets Levels Load option.  Not required.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of DUSTI_StopLogging class definition


# Beginning of DUSTI_StopLoggingCommonParams class definition
class DUSTI_StopLoggingCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of DUSTI_StopLoggingCommonParams class definition


# Beginning of DcPrint class definition
class DcPrint(BaseMethod):
    def __init__(self,
                 name,
                 SharedStorageEveryMeasurement=optional,  # Gets or sets the value indicating to print every measurement to shared storage (_Measurement#) and ituff (piped values).
                 SharedStoragePrefix=optional,            # Gets or sets a prefix for storing the results in shared storage.  If not set result(s) will not be stored.
                 AlarmPortRedirect=optional,              # The alarm port redirect disabled or enabled.
                 ApplyEndSequence=optional,               # The ApplyEndSequence at the end of the test.
                 DatalogLevel=optional,                   # Datalog level(ALL, FAIL_ONLY, COMPRESS, PINMAP_COMPRESS\").
                 EnableFlushSmartTc=optional,             # Flag to enable flushing Levels Smart TC.
                 HighLimits=optional,                     # Comma separated high limits for the measure Pins.
                 IfeObject=optional,                      # Gets or sets the IFE object of type IDcExtensions.
                 LevelsTc=required,                       # The alarm port redirect disabled or enabled.
                 LowLimits=optional,                      # Comma separated low limits for the measure Pins.
                 MeasurementTypes=optional,               # comma separated measurement type(Current, Voltage\").
                 Pins=required,                           # Comma separated Pins to get DC results for.
                 SamplingCount=optional,                  # Sampling count per pin. Optional field , Required when measuring the same pin few times.
                 BypassPort=optional,                     # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,            # Enable for current instance's test time and memory information
                 LogLevel=optional,                       # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                 # Enable for record detailed test time information
                 PreInstance=optional,                    # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                   # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 RelayTestConditionName=optional,         # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of DcPrint class definition


# Beginning of DcPrintCommonParams class definition
class DcPrintCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,             # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,            # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 RelayTestConditionName=optional,  # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of DcPrintCommonParams class definition


# Beginning of DcSingleDiffMeasureTC class definition
class DcSingleDiffMeasureTC(BaseMethod):
    def __init__(self,
                 name,
                 DiffHighLimit=required,           # Sets high limit for differential measurement.
                 DiffLowLimit=required,            # Sets low limit for differential measurement.
                 AlarmPortRedirect=optional,       # The alarm port redirect disabled or enabled.
                 ApplyEndSequence=optional,        # The ApplyEndSequence at the end of the test.
                 DatalogLevel=optional,            # Datalog level(ALL, FAIL_ONLY, COMPRESS, PINMAP_COMPRESS\").
                 EnableFlushSmartTc=optional,      # Flag to enable flushing Levels Smart TC.
                 HighLimits=optional,              # Comma separated high limits for the measure Pins.
                 IfeObject=optional,               # Gets or sets the IFE object of type IDcExtensions.
                 LevelsTc=required,                # The alarm port redirect disabled or enabled.
                 LowLimits=optional,               # Comma separated low limits for the measure Pins.
                 MeasurementTypes=optional,        # comma separated measurement type(Current, Voltage\").
                 Pins=required,                    # Comma separated Pins to get DC results for.
                 SamplingCount=optional,           # Sampling count per pin. Optional field , Required when measuring the same pin few times.
                 BypassPort=optional,              # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,     # Enable for current instance's test time and memory information
                 LogLevel=optional,                # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,          # Enable for record detailed test time information
                 PreInstance=optional,             # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,            # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 RelayTestConditionName=optional,  # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of DcSingleDiffMeasureTC class definition


# Beginning of DcSingleDiffMeasureTCCommonParams class definition
class DcSingleDiffMeasureTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,             # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,            # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 RelayTestConditionName=optional,  # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of DcSingleDiffMeasureTCCommonParams class definition


# Beginning of DedcLoadConfigTC class definition
class DedcLoadConfigTC(BaseMethod):
    def __init__(self,
                 name,
                 ConfigFile=required,           # Gets or sets Path to the file to be store.
                 CoreAware=optional,            # Gets or sets if core deafeaturing/multipasss should be used. Empty indiates disabled.
                 Mode=optional,                 # Gets or sets whether to enable or disable this configuration.
                 Modules=optional,              # Gets or sets the list of modules to run this config on in (If in local mode).
                 Scope=optional,                # Gets or sets whether to enable or disable this configuration.
                 ValidationMode=optional,       # Gets or sets Path to the file to be store.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of DedcLoadConfigTC class definition


# Beginning of DedcLoadConfigTCCommonParams class definition
class DedcLoadConfigTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of DedcLoadConfigTCCommonParams class definition


# Beginning of DedcRVCallbackTC class definition
class DedcRVCallbackTC(BaseMethod):
    def __init__(self,
                 name,
                 ForceFlow=optional,            # Gets or sets whether to enable or disable this configuration.
                 TestTimeSoftCap=optional,      # Gets or sets Max Test time to disable aditional data collection. FF will finish. Defaut value is 0 to indicate infinite test time is allowed.
                 IfeObject=optional,            # Gets or Sets **not in use will be removed later with the refactoring of the IfeObject**.
                 Mode=required,                 #  Gets or sets the registration mode of the RV callbacks in this instance." 
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of DedcRVCallbackTC class definition


# Beginning of DedcRVCallbackTCCommonParams class definition
class DedcRVCallbackTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of DedcRVCallbackTCCommonParams class definition


# Beginning of DfxTimingTuner class definition
class DfxTimingTuner(BaseMethod):
    def __init__(self,
                 name,
                 AdaptiveEnd=optional,                  # Gets or sets the ending value of the search (as an offset from the current value).
                 AdaptiveResolution=optional,           # Gets or sets the resolution of the search steps.
                 AdaptiveStart=optional,                # Gets or sets the starting value of the search (as an offset from the current value).
                 ConfigFile=required,                   # Gets or sets the name of the Configuration file to load.
                 ConfigSet=required,                    # Gets or sets the name of the Configuration set to use.
                 Datalog=optional,                      # Gets or sets whether or not to Datalog all pins on a successful search.
                 DisablePatternLoop=optional,           # Gets or sets whether or not to disable the pattern loop.
                 LevelsTc=required,                     # Gets or sets LevelsTc to plist execution.
                 MaskPins=optional,                     # Gets or sets comma separated mask pins for Patlist execution.
                 Patlist=required,                      # Gets or sets Patlist to execute for the Search.
                 SearchEnd=required,                    # Gets or sets the ending value of the search.
                 SearchResolution=required,             # Gets or sets the resolution of the search steps.
                 SearchStart=required,                  # Gets or sets the starting value of the search.
                 TimingsTc=required,                    # Gets or sets TimingsTc for plist execution.
                 UpdateTC=optional,                     # Gets or sets which TestConditions to Resolve on a successfull search.
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PrePlist=optional,                     # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of DfxTimingTuner class definition


# Beginning of DfxTimingTunerCommonParams class definition
class DfxTimingTunerCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PrePlist=optional,                     # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of DfxTimingTunerCommonParams class definition


# Beginning of DieRecoveryBase class definition
class DieRecoveryBase(BaseMethod):
    def __init__(self,
                 name,
                 AllowDefeatures=optional,      # Gets or sets the value indicating whether or not DownBins are valid. If false, the Trackers can only be written once and will fail if their value is every changed.
                 EnablePreTestCheck=optional,   # Gets or sets the value indicating whether VminTC should run the dierecovery rules before executing the search. If this is set to True and the pre-test check fails, VminTC exit port will depend only on the results of the test, any non-tested trackers will be ignored.
                 Mode=optional,                 # Gets or sets the Templates Execution Mode (Only Configure is valid for a production test program).
                 RulesFile=required,            # Gets or sets the DieRecovery Rules file.
                 SKUFile=required,              # Gets or sets the DieRecovery SKU Definition file.
                 SaveHistory=optional,          # Gets or sets the value indicating whether or not to save the name of every test that updates a DieRecovery Tracker.
                 TrackerFile=required,          # Gets or sets the DieRecovery Tracker configuration file.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of DieRecoveryBase class definition


# Beginning of DieRecoveryBaseCommonParams class definition
class DieRecoveryBaseCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of DieRecoveryBaseCommonParams class definition


# Beginning of DlvrDACCal class definition
class DlvrDACCal(BaseMethod):
    def __init__(self,
                 name,
                 ConfigFile=required,                    # Gets or sets the configuration file to load.
                 CtvConfigurationFile=optional,          # Gets or sets the CSV file to be used with CtvServicesSpm.
                 Defeature=optional,                     # Gets or sets Defeature.
                 DieIdDisable=optional,                  # Gets or sets comma separated list of SSIDs to be disabled (ignored) during CTV processing
                 DieIdRename=optional,                   # Gets or sets the DieIdRename to be used with CtvServicesSpm.
                 Domains=required,                       # Gets or sets the list of domains to run.
                 RecoveryRule=optional,                  # Gets or sets the DieRecovery Rules to run when the tracker is updated.
                 RecoveryTracking=optional,              # Gets or sets the DieRecovery Token to update on failure.
                 RunEquationsOnFail=optional,            # Gets or sets a value indicating whether the Equations should be run even on a failure (can be used to assign default values).
                 AlarmPortRedirect=optional,             # Gets or sets the alarm port redirect disabled or enabled.
                 ApplyEndSequence=optional,              # The ApplyEndSequence at the end of the test.
                 CtvPins=optional,                       # Gets or sets comma separated pins to get CTV from the plist execution.
                 DatalogLevel=optional,                  # Gets or sets datalog level(ALL, FAIL_ONLY, COMPRESS, PINMAP_COMPRESS)
                 HighLimits=required,                    # Gets or sets comma seperated high limits for the measure pins.
                 IfeObject=optional,                     # Gets or sets the IFE object of type ITriggeredDcExtensions.
                 LevelsTc=required,                      # Gets or sets LevelsTc to use.
                 LowLimits=required,                     # Gets or sets comma separated low limits for the measure pins.
                 MaskPins=optional,                      # Gets or sets comma separated pins for mask.
                 MeasurementTypes=optional,              # Gets or sets comma separated measurement types (Current, Voltage) or (C, V).
                 Patlist=required,                       # Gets or sets PatList to use.
                 PcatMode=optional,                      # Gets or sets datalog level(All, FailOnly)
                 Pins=required,                          # Gets or sets comma separated pins to get DC results for.
                 PrePlist=optional,                      # Gets or sets the PrePlist callback to plist execution.
                 SamplingCount=optional,                 # Gets or sets sampling count per pin.
                 SoftwareTriggerConfiguration=optional,  # Gets or sets the configuration file for the software trigger event.
                 TimingsTc=required,                     # Gets or sets TimingsTc to use.
                 TriggerMapName=optional,                # Gets or sets comma seperated high limits for the measure pins.
                 BypassPort=optional,                    # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,           # Enable for current instance's test time and memory information
                 LogLevel=optional,                      # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                # Enable for record detailed test time information
                 SetPointsPlistMode=optional,            # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,       # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,         # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,          # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,                # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,             # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,   # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 RelayTestConditionName=optional,        # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,       # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PostPlist=optional,                     # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of DlvrDACCal class definition


# Beginning of DlvrDACCalCommonParams class definition
class DlvrDACCalCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of DlvrDACCalCommonParams class definition


# Beginning of DlvrTrimCalc class definition
class DlvrTrimCalc(BaseMethod):
    def __init__(self,
                 name,
                 ConfigFile=required,           # Gets or sets the configuration file to load.
                 ConfigSet=required,            # Gets or sets the configuration set to execute.
                 Mode=required,                 # Gets or sets the calculation mode.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of DlvrTrimCalc class definition


# Beginning of DlvrTrimCalcCommonParams class definition
class DlvrTrimCalcCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of DlvrTrimCalcCommonParams class definition


# Beginning of DrngTC class definition
class DrngTC(BaseMethod):
    def __init__(self,
                 name,
                 CollisionDataSize=optional,             # Gets or sets the register size for collision data chunks. Example: 128 vs 256bits; split in 4 chunks.
                 CollisionStart=optional,                # The index of the first CTV bit to use for Collision data.
                 ExpectedCtvSize=required,               # The expected number of CTV to capture. Instance will fail if the actual number of CTV does not match. Set to -1 to disable the check.
                 HealthCountLimits=optional,             # Gets or sets the comma-separated health count limits. dnoxor_lo,dnoxor_hi,dxor_lo,dxor_hi.
                 HealthCountStart=optional,              # The index of the first CTV bit to use for Health Count data.
                 MetricsStart=optional,                  # The index of the first CTV bit to use for Metrics data.
                 Mode=optional,                          # Gets or sets the execution mode.
                 AlarmPortRedirect=optional,             # The alarm port redirect disabled or enabled.
                 ApplyEndSequence=optional,              # The ApplyEndSequence at the end of the test.
                 CtvCapturePerCycleMode=optional,        # CTV capture mode. If DISABLED (default), CTV capture will be per pin. If ENABLED it will be per cycle.
                 CtvCapturePins=optional,                # Comma separated pins for CTV capture.
                 DtsConfigurationName=optional,          # Configuration in case DTS processing is wanted.
                 FailuresToCapturePerPattern=optional,   # Int for number of failures per pattern to capture. If 0 (default), per pattern capture is disabled.
                 FailuresToCaptureTotal=optional,        # Int for the number of global failures to capture. If 0 (default), it means failure capture is disabled.
                 IfeObject=optional,                     #  Gets or sets the IFE object of type IFuncCaptureExtensions.
                 LevelsTc=required,                      # LevelsTc to plist execution.
                 MaskPins=optional,                      # Comma separated pins for mask.
                 MaxFailuresPerPatternToItuff=optional,  # Int for number of failures per pattern to print to ituff. If 0 (default), per pattern failure count defaults to MaxFailuresToItuff.
                 MaxFailuresToItuff=optional,            # int for the number of global failures to print to ituff. If 0 (default), it means failure prints are disabled.
                 Patlist=required,                       # Patlist to execute.
                 PrePlist=optional,                      # PrePlist callback to plist execution.
                 TimingsTc=required,                     # TimingsTc for plist execution.
                 BypassPort=optional,                    # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,           # Enable for current instance's test time and memory information
                 LogLevel=optional,                      # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                # Enable for record detailed test time information
                 SetPointsPlistMode=optional,            # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,       # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,         # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,          # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,                # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,             # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,   # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 RelayTestConditionName=optional,        # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,       # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PostPlist=optional,                     # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of DrngTC class definition


# Beginning of DrngTCCommonParams class definition
class DrngTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of DrngTCCommonParams class definition


# Beginning of DynamicFuncRestoreTC class definition
class DynamicFuncRestoreTC(BaseMethod):
    def __init__(self,
                 name,
                 CleanRestoreVariables=optional,  # Gets or sets desired plist modification type.
                 RestoreMode=optional,            # Gets or sets desired plist modification type.
                 TestTypeMappingFile=optional,    # Gets or sets name of input test mapping configuration file.
                 BypassPort=optional,             # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,    # Enable for current instance's test time and memory information
                 LogLevel=optional,               # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,         # Enable for record detailed test time information
                 PreInstance=optional,            # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,           # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of DynamicFuncRestoreTC class definition


# Beginning of DynamicFuncRestoreTCCommonParams class definition
class DynamicFuncRestoreTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of DynamicFuncRestoreTCCommonParams class definition


# Beginning of DynamicFuncTC class definition
class DynamicFuncTC(BaseMethod):
    def __init__(self,
                 name,
                 FailPatternLogSubString=optional,      # Gets or sets fail pattern positions from pattern name for dataLog.
                 LevelsTc=required,                     # Gets or sets LevelsTc to plist execution.
                 MaskPins=optional,                     # Gets or sets comma separated mask pins for Patlist execution.
                 MaxNumberOfFails=optional,             # Gets or sets max number of patternNames to process.
                 Patlist=required,                      # Gets or sets Patlist to execute.
                 TestIdSubStringFilter=optional,        # Gets or sets test id positions from pattern name to match in target plist instead of full pattern name.
                 TestTypeMappingFile=optional,          # Gets or sets name of input test mapping configuration file.
                 TimingsTc=required,                    # Gets or sets TimingsTc for plist execution.
                 UnhandledCaseAction=optional,          # Gets or sets unhandled case selection, port 2 or enable all.
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PrePlist=optional,                     # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of DynamicFuncTC class definition


# Beginning of DynamicFuncTCCommonParams class definition
class DynamicFuncTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PrePlist=optional,                     # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of DynamicFuncTCCommonParams class definition


# Beginning of EyeDiagram class definition
class EyeDiagram(BaseMethod):
    def __init__(self,
                 name,
                 ConfigurationInputFile=optional,       # Configuration input file.
                 CtvCapturePins=optional,               # Comma separated pins for CTV capture.
                 CtvDataSharedStorageKey=optional,      # Ctv Data Shared Storage Key.
                 CtvLogic=optional,                     # CtvLogic.
                 DieIdRename=optional,                  # DieId to be used to replace the pin name on ituff printing and to add the corresponding tssid.
                 IfeObject=optional,                    # IFE object of type IFuncCaptureExtensions.
                 LevelsTc=optional,                     # LevelsTc to plist execution.
                 Mode=optional,                         # Mode.
                 Patlist=optional,                      # Patlist to execute.
                 PrePlist=optional,                     # PrePlist callback to plist execution.
                 PrintPlots=optional,                   # PrintPlots.
                 TimingsTc=optional,                    # TimingsTc for plist execution.
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of EyeDiagram class definition


# Beginning of EyeDiagramCommonParams class definition
class EyeDiagramCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of EyeDiagramCommonParams class definition


# Beginning of FUSEBURN_Check_FacilityID_TpFuseEnable class definition
class FUSEBURN_Check_FacilityID_TpFuseEnable(BaseMethod):
    def __init__(self,
                 name,
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FUSEBURN_Check_FacilityID_TpFuseEnable class definition


# Beginning of FUSEBURN_ECC_Check class definition
class FUSEBURN_ECC_Check(BaseMethod):
    def __init__(self,
                 name,
                 AlarmPortRedirect=optional,             # The alarm port redirect disabled or enabled.
                 ApplyEndSequence=optional,              # The ApplyEndSequence at the end of the test.
                 CtvCapturePerCycleMode=optional,        # CTV capture mode. If DISABLED (default), CTV capture will be per pin. If ENABLED it will be per cycle.
                 CtvCapturePins=optional,                # Comma separated pins for CTV capture.
                 DtsConfigurationName=optional,          # Configuration in case DTS processing is wanted.
                 FailuresToCapturePerPattern=optional,   # Int for number of failures per pattern to capture. If 0 (default), per pattern capture is disabled.
                 FailuresToCaptureTotal=optional,        # Int for the number of global failures to capture. If 0 (default), it means failure capture is disabled.
                 IfeObject=optional,                     #  Gets or sets the IFE object of type IFuncCaptureExtensions.
                 LevelsTc=required,                      # LevelsTc to plist execution.
                 MaskPins=optional,                      # Comma separated pins for mask.
                 MaxFailuresPerPatternToItuff=optional,  # Int for number of failures per pattern to print to ituff. If 0 (default), per pattern failure count defaults to MaxFailuresToItuff.
                 MaxFailuresToItuff=optional,            # int for the number of global failures to print to ituff. If 0 (default), it means failure prints are disabled.
                 Patlist=required,                       # Patlist to execute.
                 PrePlist=optional,                      # PrePlist callback to plist execution.
                 TimingsTc=required,                     # TimingsTc for plist execution.
                 BypassPort=optional,                    # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,           # Enable for current instance's test time and memory information
                 LogLevel=optional,                      # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                # Enable for record detailed test time information
                 SetPointsPlistMode=optional,            # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,       # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,         # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,          # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,                # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,             # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,   # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 RelayTestConditionName=optional,        # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,       # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PostPlist=optional,                     # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FUSEBURN_ECC_Check class definition


# Beginning of FUSEBURN_FuseReadMask class definition
class FUSEBURN_FuseReadMask(BaseMethod):
    def __init__(self,
                 name,
                 ExceptionPort=required,                   # Gets or sets the expected port if the mask compare returns true. Last value should always set to exception port. Can define single or multiple name with comma delimiter.
                 Expectedport=required,                    # Gets or sets the expected port if the mask compare returns true. Last value should always set to exception port. Can define single or multiple name with comma delimiter.
                 FuseReadGlobal=required,                  # Gets or sets the input parameter as UserVar for FLE to consume.
                 MaskName=required,                        # Gets or sets fuse string mask(s). Can define single or multiple name with comma delimiter.
                 UserVarCollection=required,               # Gets or sets the input parameter as UserVar Collection.
                 ApplyEndSequence=optional,                # ApplyEndSequence at the end of the test.
                 ConfigName=required,                      # Configuration name for the input file. Can only define single name.
                 ConfigurationFile=required,               # ConfigurationFile. ~HDMT_TPL_DIR/Modules/FuseRead/FuseRead/InputFiles/fuseReadScenario1.json. other using type String.
                 EnableCaptureFunctionalFailure=optional,  # A value whether to enable CreateCaptureFailureAndCtvPerPinTest(true) or CreateCaptureCtvPerPinTest(false).
                 FailingMaskName=optional,                 # Failing mask names. Can define single or multiple name with comma delimiter.
                 FuseGroupToDatalog=optional,              # Name of fuse group to datalog. When this parameter is defined (enabled) with valid fuse group name, the fuse string of the fuse group name will be datalog to ituff.
                 IfeObject=optional,                       # IFE object of type IFuseReadMaskExtensions.
                 LevelsTc=optional,                        # LevelsTc for plist execution.
                 MaskPins=optional,                        # Comma separated pins for mask.
                 PassingMaskName=optional,                 # Passing mask names. Can define single or multiple name with comma delimiter.
                 Patlist=optional,                         # Patlist to execute.
                 PrePlist=optional,                        # Pre Patlist to execute.
                 RegisterName=required,                    # Name of registers to select within the configuration. Can define single or multiple name with comma delimiter.
                 SimulationMode=optional,                  # Simulation mode. Indicating whether fuse string value is set with SimulationString (True) or CtvData (False).
                 TimingsTc=optional,                       # TimingsTc for plist execution.
                 VoltageFile=optional,                     # VoltageFile. ~HDMT_TPL_DIR/Modules/FuseRead/FuseRead/InputFiles/fuseReadVoltage.json. other using type String.
                 BypassPort=optional,                      # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,             # Enable for current instance's test time and memory information
                 LogLevel=optional,                        # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                  # Enable for record detailed test time information
                 PreInstance=optional,                     # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                    # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,              # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,         # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,           # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,            # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,                  # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,               # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,     # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,         # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,          # The RelayTestCondition to apply.
                 PostPlist=optional,                       # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FUSEBURN_FuseReadMask class definition


# Beginning of FUSEBURN_Val_Fork_Test class definition
class FUSEBURN_Val_Fork_Test(BaseMethod):
    def __init__(self,
                 name,
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FUSEBURN_Val_Fork_Test class definition


# Beginning of FaCTBegin class definition
class FaCTBegin(BaseMethod):
    def __init__(self,
                 name,
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FaCTBegin class definition


# Beginning of FaCTExecute class definition
class FaCTExecute(BaseMethod):
    def __init__(self,
                 name,
                 Key=required,                  # Gets or sets the Mapping Object Key for the shared storage.
                 KeyContext=required,           # Gets or sets the Context value for the Key.
                 WritingContext=required,       # Gets or sets the Context value for writing the data to shared storage.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FaCTExecute class definition


# Beginning of FaCTExitController class definition
class FaCTExitController(BaseMethod):
    def __init__(self,
                 name,
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FaCTExitController class definition


# Beginning of FaCTInit class definition
class FaCTInit(BaseMethod):
    def __init__(self,
                 name,
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FaCTInit class definition


# Beginning of FindUltOrVidTC class definition
class FindUltOrVidTC(BaseMethod):
    def __init__(self,
                 name,
                 DieIds=optional,               # Gets or sets the matching dieId.
                 InputFile=required,            # Gets or sets the name of the configuration file.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FindUltOrVidTC class definition


# Beginning of FindUltOrVidTCCommonParams class definition
class FindUltOrVidTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FindUltOrVidTCCommonParams class definition


# Beginning of FleCheckFullChipArraySignature class definition
class FleCheckFullChipArraySignature(BaseMethod):
    def __init__(self,
                 name,
                 FuseReadTokenName=required,         # Gets or sets the mandatory parameter of FuseReadTokenName. It can be uservar token or sharedstorage token.
                 OutputFuseStringLocation=required,  # Gets or sets the OutputFuseStringLocation Paramter.
                 Register=required,                  # Gets or sets the mandatory parameter of Fuse Register.
                 BypassPort=optional,                # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,       # Enable for current instance's test time and memory information
                 LogLevel=optional,                  # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,            # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FleCheckFullChipArraySignature class definition


# Beginning of FleCheckFuseStringStatus class definition
class FleCheckFuseStringStatus(BaseMethod):
    def __init__(self,
                 name,
                 FuseReadTokenName=required,         # Gets or sets the mandatory parameter of FuseReadTokenName.
                 LockoutBitGroup=optional,           # Gets or sets the LockoutBitGroup parameter.
                 OutputFuseStringLocation=optional,  # Gets or sets the OutputFuseStringLocation Paramter.
                 Register=required,                  # Gets or sets the mandatory parameter of Fuse Register.
                 SkipShortTest=optional,             # Gets or sets the SkipShortTest Paramter.
                 BypassPort=optional,                # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,       # Enable for current instance's test time and memory information
                 LogLevel=optional,                  # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,            # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FleCheckFuseStringStatus class definition


# Beginning of FleCheckFusedSspecFusing class definition
class FleCheckFusedSspecFusing(BaseMethod):
    def __init__(self,
                 name,
                 FuseReadTokenName=required,         # Gets or sets the mandatory parameter of FuseReadTokenName.
                 OutputFuseStringLocation=optional,  # Gets or sets the OutputFuseStringLocation Paramter.
                 Register=required,                  # Gets or sets the mandatory parameter of Fuse Register.
                 SspecFuseGroupName=required,        # Gets or sets the LockoutBitGroup parameter.
                 BypassPort=optional,                # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,       # Enable for current instance's test time and memory information
                 LogLevel=optional,                  # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,            # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FleCheckFusedSspecFusing class definition


# Beginning of FleCompareFuseString class definition
class FleCompareFuseString(BaseMethod):
    def __init__(self,
                 name,
                 Category=required,                  # Gets or sets the mandatory Category Paramter.
                 FuseReadTokenName=required,         # Gets or sets the mandatory parameter of FuseReadTokenName. It can be uservar token or sharedstorage token.
                 OutputFuseStringLocation=required,  # Gets or sets the OutputFuseStringLocation Paramter.
                 Register=required,                  # Gets or sets the mandatory parameter of Fuse Register.
                 BypassPort=optional,                # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,       # Enable for current instance's test time and memory information
                 LogLevel=optional,                  # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,            # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FleCompareFuseString class definition


# Beginning of FleComputeFullChipArraySignature class definition
class FleComputeFullChipArraySignature(BaseMethod):
    def __init__(self,
                 name,
                 FuseReadTokenName=required,         # Gets or sets the mandatory parameter of FuseReadTokenName. It can be uservar token or sharedstorage token.
                 OutputFuseStringLocation=required,  # Gets or sets the OutputFuseStringLocation Paramter.
                 Register=required,                  # Gets or sets the mandatory parameter of Fuse Register.
                 BypassPort=optional,                # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,       # Enable for current instance's test time and memory information
                 LogLevel=optional,                  # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,            # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FleComputeFullChipArraySignature class definition


# Beginning of FleComputeFuseHashSignature class definition
class FleComputeFuseHashSignature(BaseMethod):
    def __init__(self,
                 name,
                 FuseReadTokenName=required,         # Gets or sets the mandatory parameter of FuseReadTokenName. It can be uservar token or sharedstorage token.
                 OutputFuseStringLocation=required,  # Gets or sets the OutputFuseStringLocation Paramter.
                 Register=required,                  # Gets or sets the mandatory parameter of Fuse Register.
                 BypassPort=optional,                # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,       # Enable for current instance's test time and memory information
                 LogLevel=optional,                  # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,            # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FleComputeFuseHashSignature class definition


# Beginning of FleGenerateFuseRepairString class definition
class FleGenerateFuseRepairString(BaseMethod):
    def __init__(self,
                 name,
                 CalculateEcc=optional,              # Gets or sets the CalculateEcc parameter.
                 DataLog=optional,                   # Gets or sets the PrintToiTuff parameter. Print to iTuff failing bits info.
                 FuseChassis=required,               # Gets or sets the mandatory FuseChassis parameter. e.g.:CH3= Chassis 3.0, CH21 = Fuse Chassis 2.1, CH4 = Fuse Chassis 4.0.
                 FuseReadTokenName=required,         # Gets or sets the mandatory parameter of FuseReadTokenName.
                 NumOfColInArray=optional,           # Gets or sets the numOfColInArray parameter. Specify the number of columns  in 1K array.
                 NumOfRowInArray=optional,           # Gets or sets the NumOfRowInArray parameter. Specify the number of rows in 1K array.
                 OutputFuseStringLocation=optional,  # Gets or sets the OutputFuseStringLocation Parameter.
                 Process=required,                   # Gets or sets the mandatory Process parameter. e.g.:10NM = Intel 10nm process , N3 = TSMC N3 process, 5NM = Intel 5nm process.
                 Register=required,                  # Gets or sets the mandatory parameter of Fuse Register.
                 SplitSpecialRows=optional,          # Gets or sets the SplitSpecialRows parameter. YES means the final repair string will be split to data and configuration areas.
                 BypassPort=optional,                # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,       # Enable for current instance's test time and memory information
                 LogLevel=optional,                  # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,            # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FleGenerateFuseRepairString class definition


# Beginning of FleGenerateFuseRepairStringWithSpecialRow class definition
class FleGenerateFuseRepairStringWithSpecialRow(BaseMethod):
    def __init__(self,
                 name,
                 CalculateEcc=optional,               # Gets or sets the CalculateEcc parameter.
                 DataLog=optional,                    # Gets or sets the PrintToiTuff parameter. Print to iTuff failing bits info.
                 FuseChassis=required,                # Gets or sets the mandatory FuseChassis parameter. e.g.:CH3= Chassis 3.0, CH21 = Fuse Chassis 2.1, CH4 = Fuse Chassis 4.0.
                 FuseReadTokenName=required,          # Gets or sets the mandatory parameter of FuseReadTokenName.
                 NumOfColInArray=optional,            # Gets or sets the numOfColInArray parameter. Specify the number of columns  in 1K array.
                 NumOfRowInArray=optional,            # Gets or sets the NumOfRowInArray parameter. Specify the number of rows in 1K array.
                 OutputFuseStringLocation=optional,   # Gets or sets the OutputFuseStringLocation Parameter.
                 OutputSpecialRowsLocation=optional,  # Gets or sets the OutputFuseStringLocation Paramter.
                 Process=required,                    # Gets or sets the mandatory Process parameter. e.g.:10NM = Intel 10nm process , N3 = TSMC N3 process, 5NM = Intel 5nm process.
                 Register=required,                   # Gets or sets the mandatory parameter of Fuse Register.
                 SpecialRowTokenName=required,        # Gets or sets the mandatory parameter of FuseReadTokenName.
                 SplitSpecialRows=optional,           # Gets or sets the SplitSpecialRows parameter. YES means the final repair string will be split to data and configuration areas.
                 BypassPort=optional,                 # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,        # Enable for current instance's test time and memory information
                 LogLevel=optional,                   # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,             # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FleGenerateFuseRepairStringWithSpecialRow class definition


# Beginning of FleGenerateLockoutBitsFuseString class definition
class FleGenerateLockoutBitsFuseString(BaseMethod):
    def __init__(self,
                 name,
                 Register=required,             # Gets or sets the mandatory parameter of Fuse Register.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FleGenerateLockoutBitsFuseString class definition


# Beginning of FleGenerateLockoutBitsFuseStringByName class definition
class FleGenerateLockoutBitsFuseStringByName(BaseMethod):
    def __init__(self,
                 name,
                 Name=required,                 # Gets or sets the mandatory parameter of Name.
                 Register=required,             # Gets or sets the mandatory parameter of Fuse Register.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FleGenerateLockoutBitsFuseStringByName class definition


# Beginning of FleGeneratePerDieFuseString class definition
class FleGeneratePerDieFuseString(BaseMethod):
    def __init__(self,
                 name,
                 DataLog=optional,              # Gets or sets the mandatory parameter of data log.
                 Register=required,             # Gets or sets the mandatory parameter of Fuse Register.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FleGeneratePerDieFuseString class definition


# Beginning of FleGeneratePerDieFuseStringIgnoreSecurityKeys class definition
class FleGeneratePerDieFuseStringIgnoreSecurityKeys(BaseMethod):
    def __init__(self,
                 name,
                 DataLog=optional,              # Gets or sets the mandatory parameter of data log.
                 Register=required,             # Gets or sets the mandatory parameter of Fuse Register.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FleGeneratePerDieFuseStringIgnoreSecurityKeys class definition


# Beginning of FleGetDieStatus class definition
class FleGetDieStatus(BaseMethod):
    def __init__(self,
                 name,
                 FuseStateUservar=required,     # Gets or sets the mandatory parameter of Fuse Register.
                 Register=required,             # Gets or sets the mandatory parameter of Fuse Register.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FleGetDieStatus class definition


# Beginning of FleISeedCapturePartId class definition
class FleISeedCapturePartId(BaseMethod):
    def __init__(self,
                 name,
                 ItuffBinary=optional,                   # Gets or sets print to ituff in rawbinary_msbF format.
                 ItuffFuseId=optional,                   # Gets or sets print to ituff in strgval format.
                 ItuffHex=optional,                      # Gets or sets print to ituff in rawnhex_msbF format.
                 AlarmPortRedirect=optional,             # The alarm port redirect disabled or enabled.
                 ApplyEndSequence=optional,              # The ApplyEndSequence at the end of the test.
                 CtvCapturePerCycleMode=optional,        # CTV capture mode. If DISABLED (default), CTV capture will be per pin. If ENABLED it will be per cycle.
                 CtvCapturePins=optional,                # Comma separated pins for CTV capture.
                 DtsConfigurationName=optional,          # Configuration in case DTS processing is wanted.
                 FailuresToCapturePerPattern=optional,   # Int for number of failures per pattern to capture. If 0 (default), per pattern capture is disabled.
                 FailuresToCaptureTotal=optional,        # Int for the number of global failures to capture. If 0 (default), it means failure capture is disabled.
                 IfeObject=optional,                     #  Gets or sets the IFE object of type IFuncCaptureExtensions.
                 LevelsTc=required,                      # LevelsTc to plist execution.
                 MaskPins=optional,                      # Comma separated pins for mask.
                 MaxFailuresPerPatternToItuff=optional,  # Int for number of failures per pattern to print to ituff. If 0 (default), per pattern failure count defaults to MaxFailuresToItuff.
                 MaxFailuresToItuff=optional,            # int for the number of global failures to print to ituff. If 0 (default), it means failure prints are disabled.
                 Patlist=required,                       # Patlist to execute.
                 PrePlist=optional,                      # PrePlist callback to plist execution.
                 TimingsTc=required,                     # TimingsTc for plist execution.
                 BypassPort=optional,                    # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,           # Enable for current instance's test time and memory information
                 LogLevel=optional,                      # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                # Enable for record detailed test time information
                 SetPointsPlistMode=optional,            # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,       # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,         # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,          # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,                # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,             # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,   # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 RelayTestConditionName=optional,        # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,       # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PostPlist=optional,                     # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FleISeedCapturePartId class definition


# Beginning of FleISeedGenerateCA class definition
class FleISeedGenerateCA(BaseMethod):
    def __init__(self,
                 name,
                 DieId=required,                # Gets or sets the mandatory parameter of unit identifier in case of Async keys generation.
                 KeysTypeId=required,           # Gets or sets the KeysTypeId.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FleISeedGenerateCA class definition


# Beginning of FleISeedGenerateKeys class definition
class FleISeedGenerateKeys(BaseMethod):
    def __init__(self,
                 name,
                 DieId=optional,                # Gets or sets the mandatory parameter of unit identifier in case of Async keys generation.
                 KeyGenerationMode=optional,    # Gets or sets the generate keys sync or async.
                 KeysAlgorithm=required,        # Gets or sets the Key KeysAlgorithm.
                 KeysCount=required,            # Gets or sets the KeysCount.
                 KeysLength=required,           # Gets or sets the KeysLength.
                 KeysTypeId=required,           # Gets or sets the KeysTypeId.
                 PartId=optional,               # Gets or sets the PartId.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FleISeedGenerateKeys class definition


# Beginning of FleISeedGetLotKeys class definition
class FleISeedGetLotKeys(BaseMethod):
    def __init__(self,
                 name,
                 KeysTypeId=required,           # Gets or sets the KeysTypeId.
                 MaxQueryAttempts=optional,     # Gets or sets the max number of query attempts before failure.
                 QueryMode=optional,            # Gets or sets the query mode for this operation.
                 ReQuerySleep=optional,         # Gets or sets the number of seconds to wait for re-query attempt.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FleISeedGetLotKeys class definition


# Beginning of FleISeedGetUnitKeys class definition
class FleISeedGetUnitKeys(BaseMethod):
    def __init__(self,
                 name,
                 DieId=required,                # Gets or sets the mandatory parameter of unit identifier in case of Async keys generation.
                 KeysTypeId=required,           # Gets or sets the KeysTypeId.
                 QueryMode=optional,            # Gets or sets the query mode for this operation.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FleISeedGetUnitKeys class definition


# Beginning of FleISeedKeyGenFork class definition
class FleISeedKeyGenFork(BaseMethod):
    def __init__(self,
                 name,
                 KeyName=required,              # Gets or sets the mandatory parameter of KeyName.
                 Register=required,             # Gets or sets the mandatory parameter of Fuse Register.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FleISeedKeyGenFork class definition


# Beginning of FleISeedSetUnitKeys class definition
class FleISeedSetUnitKeys(BaseMethod):
    def __init__(self,
                 name,
                 DieIds=required,               # Gets or sets the mandatory parameter of unit identifier in case of Async keys generation.
                 KeysAlgorithm=optional,        # Gets or sets the Key KeysAlgorithm.
                 KeysTypeId=required,           # Gets or sets the KeysTypeId.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FleISeedSetUnitKeys class definition


# Beginning of FlePrintSSPECToItuff class definition
class FlePrintSSPECToItuff(BaseMethod):
    def __init__(self,
                 name,
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FlePrintSSPECToItuff class definition


# Beginning of FleUpdateSocCrc16InFuseString class definition
class FleUpdateSocCrc16InFuseString(BaseMethod):
    def __init__(self,
                 name,
                 FuncName=required,             # Gets or sets the mandatory Category Paramter.
                 Register=required,             # Gets or sets the mandatory parameter of Fuse Register.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FleUpdateSocCrc16InFuseString class definition


# Beginning of FleUpdateSpecialAlgInFuseString class definition
class FleUpdateSpecialAlgInFuseString(BaseMethod):
    def __init__(self,
                 name,
                 AlgorithmName=required,        # Gets or sets the mandatory AlgorithmName Paramter.
                 Register=required,             # Gets or sets the mandatory parameter of Fuse Register.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FleUpdateSpecialAlgInFuseString class definition


# Beginning of FlowControlBase class definition
class FlowControlBase(BaseMethod):
    def __init__(self,
                 name,
                 AllowDownbins=optional,        # Gets or sets the flag to indicate if Flow Downbins are allowed.
                 UseMTT=optional,               # Gets or sets the flag to indicate if flow control will use MTT.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FlowControlBase class definition


# Beginning of FlowControlBaseCommonParams class definition
class FlowControlBaseCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FlowControlBaseCommonParams class definition


# Beginning of FlowControlTC class definition
class FlowControlTC(BaseMethod):
    def __init__(self,
                 name,
                 DefaultValues=optional,        # Gets or sets the list of start values.
                 Domains=optional,              # Gets or sets the list of flow domains and/or MTT variables.
                 ExportDff=optional,            # Gets or sets the list of DFF tokens to set current flow number.
                 ExportSharedStorage=optional,  # Gets or sets the list of variables to export current flow number.
                 FlexBOMIndex=optional,         # Gets or sets range/index to slice/substring entered FlexBOMVar.
                 FlexBOMVar=optional,           # Gets or sets the name of FlexBOM user var to use for decoding.
                 OperationMode=optional,        # Gets or sets the operation mode.
                 OutputMode=optional,           # Gets or sets the flow control output type.
                 PredictEquation=optional,      # Expression to predict start flow using simple equation.For multiple domains, use semicolon-separated values.
                 SourceMode=optional,           # Gets or sets the source mode.
                 StartValues=optional,          # Gets or sets the list of start values.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FlowControlTC class definition


# Beginning of FlowControlTCCommonParams class definition
class FlowControlTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FlowControlTCCommonParams class definition


# Beginning of FlowHooksFileGeneratorTC class definition
class FlowHooksFileGeneratorTC(BaseMethod):
    def __init__(self,
                 name,
                 Mode=required,                 # Gets or sets the RV mode. set to Disabled as default.
                 TargetHookTest=required,       # Gets or sets Name of the test to update the file path for.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FlowHooksFileGeneratorTC class definition


# Beginning of FlowHooksFileGeneratorTCCommonParams class definition
class FlowHooksFileGeneratorTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FlowHooksFileGeneratorTCCommonParams class definition


# Beginning of FmaxTC class definition
class FmaxTC(BaseMethod):
    def __init__(self,
                 name,
                 FrequencyMultiplier=optional,          # Gets or sets a frequency multiplier to calculate final measurement. It will calculate FrequencyMultiplier/SpecSet.
                 LevelsTc=required,                     # Gets or sets the Levels TestCondition for plist execution.
                 MaskPins=optional,                     # Gets or sets a comma separated list of pins to mask for Patlist execution.
                 Patlist=required,                      # Gets or sets Patlist to execute for the Search.
                 PerPattern=optional,                   # Gets or sets an option to enable/disable per pattern data collection.
                 SearchEnd=required,                    # Gets or sets the ending value for the search.
                 SearchParameter=required,              # Gets or sets the name of the TimingTC Parameter to search.
                 SearchStart=required,                  # Gets or sets the starting value for the search.
                 SearchStep=required,                   # Gets or sets the search resolution or step size.
                 TimingsTc=required,                    # Gets or sets the Timing TestCondition for plist execution.
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PrePlist=optional,                     # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FmaxTC class definition


# Beginning of FmaxTCCommonParams class definition
class FmaxTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PrePlist=optional,                     # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FmaxTCCommonParams class definition


# Beginning of FunctionalShopsTC class definition
class FunctionalShopsTC(BaseMethod):
    def __init__(self,
                 name,
                 PinConfigFile=required,                 # Gets or Sets the PinConfig file name.
                 SchemaFile=required,                    # Gets or Sets the Schema file name.
                 TestMode=optional,                      # Gets or sets test mode. Default mode is 'Production'.
                 VOXOption=optional,                     # Gets or sets test mode. Default mode is 'Production'.
                 AlarmPortRedirect=optional,             # The alarm port redirect disabled or enabled.
                 ApplyEndSequence=optional,              # The ApplyEndSequence at the end of the test.
                 CtvCapturePerCycleMode=optional,        # CTV capture mode. If DISABLED (default), CTV capture will be per pin. If ENABLED it will be per cycle.
                 CtvCapturePins=optional,                # Comma separated pins for CTV capture.
                 DtsConfigurationName=optional,          # Configuration in case DTS processing is wanted.
                 FailuresToCapturePerPattern=optional,   # Int for number of failures per pattern to capture. If 0 (default), per pattern capture is disabled.
                 FailuresToCaptureTotal=optional,        # Int for the number of global failures to capture. If 0 (default), it means failure capture is disabled.
                 IfeObject=optional,                     #  Gets or sets the IFE object of type IFuncCaptureExtensions.
                 LevelsTc=required,                      # LevelsTc to plist execution.
                 MaskPins=optional,                      # Comma separated pins for mask.
                 MaxFailuresPerPatternToItuff=optional,  # Int for number of failures per pattern to print to ituff. If 0 (default), per pattern failure count defaults to MaxFailuresToItuff.
                 MaxFailuresToItuff=optional,            # int for the number of global failures to print to ituff. If 0 (default), it means failure prints are disabled.
                 Patlist=required,                       # Patlist to execute.
                 PrePlist=optional,                      # PrePlist callback to plist execution.
                 TimingsTc=required,                     # TimingsTc for plist execution.
                 BypassPort=optional,                    # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,           # Enable for current instance's test time and memory information
                 LogLevel=optional,                      # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                # Enable for record detailed test time information
                 SetPointsPlistMode=optional,            # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,       # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,         # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,          # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,                # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,             # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,   # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 RelayTestConditionName=optional,        # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,       # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PostPlist=optional,                     # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FunctionalShopsTC class definition


# Beginning of FunctionalShopsTCCommonParams class definition
class FunctionalShopsTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FunctionalShopsTCCommonParams class definition


# Beginning of FuseLogicEngineInit class definition
class FuseLogicEngineInit(BaseMethod):
    def __init__(self,
                 name,
                 FleInputFile=required,         # Gets or sets FLE session configuration file.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of FuseLogicEngineInit class definition


# Beginning of Fuse_Code class definition
class Fuse_Code(BaseMethod):
    def __init__(self,
                 name,
                 DummyParam1=required,          # Gets or sets the DummyParam1 (this comment will be used on the pre-header file).
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of Fuse_Code class definition


# Beginning of HPTPEyeDiagram class definition
class HPTPEyeDiagram(BaseMethod):
    def __init__(self,
                 name,
                 EyeTestPins=required,               # Gets or sets the pins that will be used to do the EyeTest, (need to be strobe pins).
                 FailCount=optional,                 # Gets or sets the maximum amount of failures allowed per pattern execution.
                 LevelsTC=required,                  # Gets or sets LevelsTc to plist execution.
                 MaskPins=optional,                  # Gets or sets the pin results that will be excluded during pattern execution.
                 ParameterDriveRange=required,       # Gets or sets the range of the Parameter Drive START:STEP:NUMBEROFSTEPS.
                 ParameterNameDrive=required,        # Gets or sets the Drive param of the shmoo.
                 ParameterNameStrobe=required,       # Gets or sets the Strobe param of the shmoo.
                 ParameterNameVOX=required,          # Gets or sets the parameter to shmoo on the Eye.
                 ParameterNameVREF=required,         # Gets or sets the parameter to shmoo on the Eye.
                 ParameterStrobeRange=required,      # Gets or sets the range of the Parameter Strobe START:STEP:NUMBEROFSTEPS.
                 ParameterVOXRange=required,         # Gets or sets the range of the Parameter VOX START:STEP:NUMBEROFSTEPS.
                 ParameterVREFRange=required,        # Gets or sets the range of the Parameter VREF START:STEP:NUMBEROFSTEPS.
                 PerPinDriveOffsetParams=required,   # Gets or sets the parameters for drive offset per pin for each one of the EyeTestPins.
                 PerPinStrobeOffsetParams=required,  # Gets or sets the parameters for strobe offset per pin for each one of the EyeTestPins.
                 Plist=required,                     # Gets or sets the Plist for eye width part of the test.
                 PrePlist=optional,                  # Gets or sets the Plist for eye width part of the test.
                 TestMode=optional,                  # Gets or sets the mode for the test execution , RX, TX or RX and TX.
                 TimingShmooRangeDrive=required,     # Gets or sets the step size of the initial timing shmoo Y.
                 TimingShmooRangeStrobe=required,    # Gets or sets the step size of the initial timing shmoo X.
                 TimingsTC=required,                 # Gets or sets TimingsTc for plist execution.
                 BypassPort=optional,                # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,       # Enable for current instance's test time and memory information
                 LogLevel=optional,                  # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,            # Enable for record detailed test time information
                 PreInstance=optional,               # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,              # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of HPTPEyeDiagram class definition


# Beginning of HPTPEyeDiagramCommonParams class definition
class HPTPEyeDiagramCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of HPTPEyeDiagramCommonParams class definition


# Beginning of HPTPImpedance class definition
class HPTPImpedance(BaseMethod):
    def __init__(self,
                 name,
                 CapturePinName=optional,               # Gets or sets the CTV pin name.
                 DCLevel=optional,                      # Gets or sets dc levels to be applied after the plist execution to setup and trigger DC measurements.
                 FuncLevel=required,                    # Gets or sets func levels to be apply prior to pattern execution(this will contain all the preconditioning setup e.g pwr sequencing etc).
                 MaskPins=optional,                     # Gets or sets the mask pin names.
                 MeasConfigFile=optional,               # Gets or sets the json file which contains PinMeasurement configurations.
                 MeasConfigSet=optional,                # Gets or sets the config set.
                 PatConfigName=optional,                # Gets or sets the patconfigName.
                 Patlist=required,                      # Gets or sets Patlist.
                 PerPinRstray=optional,                 # Gets or sets the per pin rstray.
                 PinMapping=optional,                   # Gets or sets the pin mapping.
                 TargetResistance=optional,             # Gets or sets target resistance to achieve.
                 TestMode=optional,                     # Gets or sets ImpedanceMode(CALIBRATION_FUNC_CTV, CALIBRATION_PMU or CHARACTERIZATION_PMU).
                 TestType=optional,                     # Gets or sets the impedance test to execute (PD for RX and TX PD, PU for TXPU, PUPD for both).
                 TimingsTc=required,                    # Gets or sets TimingsTc for plist execution.
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 PrePlist=optional,                     # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of HPTPImpedance class definition


# Beginning of HPTPImpedanceCommonParams class definition
class HPTPImpedanceCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 PrePlist=optional,                     # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of HPTPImpedanceCommonParams class definition


# Beginning of HPTPSetupScan class definition
class HPTPSetupScan(BaseMethod):
    def __init__(self,
                 name,
                 ExecutionMode=optional,               # Gets or sets ExeMode(TERMSHIFTCODE_PATMOD, TIMING_OVERRIDE or ALL).
                 PDDeemphasisCode=optional,            # Gets or sets the value for the deemphasis pull down code that will be shifted on the calibration test, can be a number or a GlobalStorage variable.
                 PDResistorCode=optional,              # Gets or sets the value for the resistor pull down code that will be shifted on the calibration test, can be a number or a GlobalStorage variable.
                 PUDeemphasisCode=optional,            # Gets or sets the value for the deemphasis pull up code that will be shifted on the calibration test, can be a number or a GlobalStorage variable.
                 PUResistorCode=optional,              # Gets or sets the value for the resistor pull up code that will be shifted on the calibration test, can be a number or a GlobalStorage variable.
                 PatmodConfiguration=optional,         # Gets or sets the configuration to patch the termination codes in the timing calibration pattern.
                 RtermResistorCode=optional,           # Gets or sets the value for the resistor rx termination code that will be shifted on the calibration test, can be a number or a GlobalStorage variable.
                 TimingOverrideDriveParam=optional,    # Gets or sets the name of the global drive offset parameter.
                 TimingOverrideDriveValue=optional,    # Gets or sets the value for the global drive offset param, can be a number or a GlobalStorage variable, either SharedstorageToken or hardcoded.
                 TimingOverrideStrobeParams=optional,  # Gets or sets comma separated params of the name of the per-pin strobe offset parameter.
                 TimingOverrideStrobeValues=optional,  # Gets or sets comma separated values for the name of the per-pin strobe offset param, can be a number or a GlobalStorage variable, either SharedstorageToken or hardcoded.
                 TimingsTc=optional,                   # Gets or sets TimingsTc for plist execution.
                 BypassPort=optional,                  # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,         # Enable for current instance's test time and memory information
                 LogLevel=optional,                    # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,              # Enable for record detailed test time information
                 PreInstance=optional,                 # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of HPTPSetupScan class definition


# Beginning of HPTPSetupScanCommonParams class definition
class HPTPSetupScanCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of HPTPSetupScanCommonParams class definition


# Beginning of IVCurve class definition
class IVCurve(BaseMethod):
    def __init__(self,
                 name,
                 AlarmMode=optional,                    # Gets or sets AlarmMode; when is enabled alarms will be routed to different port.
                 AlarmModeDelay=optional,               # Gets or sets AlarmMode delay time in uS.
                 DatalogLevel=optional,                 # Gets or sets datalog level(ALL, FAIL_ONLY, COMPRESS, PINMAP_COMPRESS, DC_PRINT).
                 EnableFlushSmartTc=optional,           # Gets or sets flag to enable flushing Levels Smart TC.
                 ForceSetPoint=optional,                # Gets or sets force set point value for production mode.
                 ForceStartValue=optional,              # Gets or sets force start value for characterization mode.
                 ForceStepSize=optional,                # Gets or sets force step size for characterization mode.
                 ForceStopValue=optional,               # Gets or sets force stop value for characterization mode.
                 FreeDriveCurrentHi=optional,           # Gets or sets FreeDriveCurrentHi values. Required for VLC pins while using VSIM.
                 FreeDriveCurrentLo=optional,           # Gets or sets FreeDriveCurrentLo values. Required for VLC pins while using VSIM.
                 FreeDriveTime=optional,                # Gets or sets FreeDriveTime values. Required for all pins while using  VSIM.
                 HighLimits=required,                   # Gets or sets comma separated high limits for the measure Pins.
                 IClampHi=optional,                     # Gets or sets IClampHi values. Required for all pins while using VSIM.
                 IClampLo=optional,                     # Gets or sets IClampLo values. Required for all pins while using VSIM.
                 IRange=optional,                       # Gets or sets IRange values. Required for all pins.
                 LevelsTc=required,                     # Gets or sets LevelsTc to use.
                 LowLimits=required,                    # Gets or sets comma separated low limits for the measure Pins.
                 MaskPins=optional,                     # Gets or sets comma separated pins for mask.
                 Mode=optional,                         # Gets or sets execution mode.
                 OverVoltageLimit=optional,             # Gets or sets OverVoltageLimit values. Required for LC. HC, HV pins while using ISVM.
                 Patlist=optional,                      # Gets or sets the optional patlist name.
                 Pins=required,                         # Gets or sets comma separated Pins to get DC results for.
                 PowerOnTc=optional,                    # Gets or sets Power-on TC.
                 PreMeasurementDelay=optional,          # Gets or sets PreMeasurementDelay values. Required for all pins.
                 SamplingCount=optional,                # Gets or sets SamplingCount values. Required for all pins.
                 SamplingRatio=optional,                # Gets or sets SamplingRatio values. Required for all pins.
                 SharedStorageTokens=optional,          # Gets or sets a list of comma separated names for SharedStorage tokens to store measurement results.
                 TimingsTc=optional,                    # Gets or sets the optional timings test condition.
                 Type=required,                         # Gets or sets measurement type(Current, Voltage)
                 UnderVoltageLimit=optional,            # Gets or sets UnderVoltageLimit values. Required for LC. HC, HV pins while using ISVM.
                 VClamp=optional,                       # Gets or sets VClamp values. Required for VLC pins while using ISVM.
                 VClampHi=optional,                     # Gets or sets VClampHi values. Required for DPin pins while using ISVM.
                 VClampLo=optional,                     # Gets or sets VClampLo values. Required for DPin pins while using ISVM.
                 VRange=optional,                       # Gets or sets VRange values. Required for HV pins.
                 VSlewStepRatio=optional,               # Gets or sets VSlewStepRatio values. Required for HV pins while using VSIM characterization mode.
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PrePlist=optional,                     # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of IVCurve class definition


# Beginning of IVCurveCommonParams class definition
class IVCurveCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PrePlist=optional,                     # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of IVCurveCommonParams class definition


# Beginning of ImpactStudiesVmin class definition
class ImpactStudiesVmin(BaseMethod):
    def __init__(self,
                 name,
                 AltInstanceName=optional,          # Gets or sets an alternative test name to use for ituff logging.
                 ConfigurationFile=required,        # Gets or sets the name of the Configuration File.
                 ForwardFailingVmins=optional,      # Gets or sets a value which specifies whether a failing vmin should be forwarded to the next step.
                 SingleIpMode=optional,             # Gets or sets a value which specifies whether to split the results by IP or not.
                 VminForwardOffset=optional,        # Gets or sets the value to subtract from the Vmin Result before forwarding to the next test.
                 BypassPort=optional,               # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,      # Enable for current instance's test time and memory information
                 LogLevel=optional,                 # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,           # Enable for record detailed test time information
                 SetPointsPlistMode=optional,       # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,  # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,    # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,     # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,           # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,              # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,             # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FlowIndex=optional,                # Parameter to specify the instance flow index on Dynamic Flows.
                 FlowIndexCallbackName=optional,    # Flow Index callback function name. in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of ImpactStudiesVmin class definition


# Beginning of ImpactStudiesVminCommonParams class definition
class ImpactStudiesVminCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 SetPointsPlistMode=optional,       # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,  # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,    # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,     # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,           # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,              # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,             # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FlowIndex=optional,                # Parameter to specify the instance flow index on Dynamic Flows.
                 FlowIndexCallbackName=optional,    # Flow Index callback function name. in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of ImpactStudiesVminCommonParams class definition


# Beginning of InitVariablesTC class definition
class InitVariablesTC(BaseMethod):
    def __init__(self,
                 name,
                 ConfigurationFile=required,    # Gets or sets the configuration file, which should be in a .csv format.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of InitVariablesTC class definition


# Beginning of InitVariablesTCCommonParams class definition
class InitVariablesTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of InitVariablesTCCommonParams class definition


# Beginning of InterleavePatModShmoo class definition
class InterleavePatModShmoo(BaseMethod):
    def __init__(self,
                 name,
                 ConfigList=required,                   # Gets or Sets ConfigList in format of Module:Group.
                 ConfigSetPoints=required,              # Gets or Sets ConfigSetPoints to execute in format setpoint1,setpoint2,setpoint n...
                 IfeObject=optional,                    # Gets or sets ExtendedFunctions.
                 LevelsTc=required,                     # Gets or sets LevelsTc to plist execution.
                 Patlist=required,                      # Gets or sets Patlist to execute.
                 TimingsTc=required,                    # Gets or sets TimingsTc for plist execution.
                 XAxisParam=required,                   # Gets or sets the XAxisParameter. By default only TC specs are supported (levels/timings).
                 XAxisRange=required,                   # Gets or sets the XAxisRange. Default format: 'Start: Resolution: NumberOfPoints'.
                 YAxisParam=required,                   # Gets or sets the YAxisParameter. By default only TC specs are supported (levels/timings).
                 YAxisRange=required,                   # Gets or sets the YAxisRange. Default format: 'Start: Resolution: NumberOfPoints'.
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PrePlist=optional,                     # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of InterleavePatModShmoo class definition


# Beginning of InterleavePatModShmooCommonParams class definition
class InterleavePatModShmooCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PrePlist=optional,                     # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of InterleavePatModShmooCommonParams class definition


# Beginning of JsonRunTC class definition
class JsonRunTC(BaseMethod):
    def __init__(self,
                 name,
                 IfeObject=optional,            # Gets or Sets **not in use will be removed later with the refactoring of the IfeObject**.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of JsonRunTC class definition


# Beginning of JsonRunTCCommonParams class definition
class JsonRunTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of JsonRunTCCommonParams class definition


# Beginning of MbistRasterRepairTC class definition
class MbistRasterRepairTC(BaseMethod):
    def __init__(self,
                 name,
                 EnableFAFI=optional,                    # Gets or sets EnableFAFI flag.
                 EnableRepair=optional,                  # Gets or sets EnableRepair flag.
                 FuseFunctionality=optional,             # Gets or sets comma separated setting FuseFuncionality for prime fuses.
                 LYASharedStorage=optional,              # Gets or sets LYA SharedStorage Value.
                 PlistLimit=optional,                    # Gets or sets Raster off HRY.
                 RasterInputFile=required,               # Gets or sets the name of the Raster JSON configuration file.
                 RasterOffHry=optional,                  # Gets or sets Raster off HRY.
                 RepairInputFile=optional,               # Gets or sets the name of the Repair JSON configuration file.
                 SkipPriority=optional,                  # Gets or sets Raster off HRY.
                 AlarmPortRedirect=optional,             # The alarm port redirect disabled or enabled.
                 ApplyEndSequence=optional,              # The ApplyEndSequence at the end of the test.
                 CtvCapturePerCycleMode=optional,        # CTV capture mode. If DISABLED (default), CTV capture will be per pin. If ENABLED it will be per cycle.
                 CtvCapturePins=optional,                # Comma separated pins for CTV capture.
                 DtsConfigurationName=optional,          # Configuration in case DTS processing is wanted.
                 FailuresToCapturePerPattern=optional,   # Int for number of failures per pattern to capture. If 0 (default), per pattern capture is disabled.
                 FailuresToCaptureTotal=optional,        # Int for the number of global failures to capture. If 0 (default), it means failure capture is disabled.
                 IfeObject=optional,                     #  Gets or sets the IFE object of type IFuncCaptureExtensions.
                 LevelsTc=required,                      # LevelsTc to plist execution.
                 MaskPins=optional,                      # Comma separated pins for mask.
                 MaxFailuresPerPatternToItuff=optional,  # Int for number of failures per pattern to print to ituff. If 0 (default), per pattern failure count defaults to MaxFailuresToItuff.
                 MaxFailuresToItuff=optional,            # int for the number of global failures to print to ituff. If 0 (default), it means failure prints are disabled.
                 Patlist=required,                       # Patlist to execute.
                 PrePlist=optional,                      # PrePlist callback to plist execution.
                 TimingsTc=required,                     # TimingsTc for plist execution.
                 BypassPort=optional,                    # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,           # Enable for current instance's test time and memory information
                 LogLevel=optional,                      # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                # Enable for record detailed test time information
                 SetPointsPlistMode=optional,            # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,       # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,         # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,          # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,                # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,             # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,   # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 RelayTestConditionName=optional,        # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,       # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PostPlist=optional,                     # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of MbistRasterRepairTC class definition


# Beginning of MbistRasterRepairTCCommonParams class definition
class MbistRasterRepairTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of MbistRasterRepairTCCommonParams class definition


# Beginning of MbistVminTC class definition
class MbistVminTC(BaseMethod):
    def __init__(self,
                 name,
                 AdvancedDebug=optional,                 # Gets or sets whether to collect per pattern debug.  Per controller per pattern result information.
                 BisrMode=optional,                      # Gets or sets  Mode used to store BISR data in TP.
                 ClearVariables=optional,                # Gets or sets mode for clearing or not global HRY string.
                 CornerIdentifiers=optional,             # Gets or sets comma separated corner identifiers.
                 CornerPatConfigSetPoints=optional,      # Gets or sets shared storage key for a pre-populated list of PatConfigSetPoints by CornerIdentification.
                 CtvPins=optional,                       # Gets or sets CTV capture pins.
                 DffOperation=optional,                  # Gets or sets  Mode used to store BISR data in TP.
                 DtsConfiguration=optional,              # Gets or sets DTS configuration name. Empty configuration name means DTS capture move is disabled.
                 FailCaptureCount=optional,              # Gets or sets FailCaptureCount. Default 1 will set stop-on-first-fail. Any value greater than 1 will run full plist unless used in combination with ReturnOn plist options.
                 FlowIndex=optional,                     # Gets or sets the current FlowIndex.
                 FlowIndexCallbackName=optional,         # Gets or sets the current FlowIndexCallbackName.
                 ForceConfigFileParseState=optional,     # Gets or sets the state to force parsing of a new config file for debug scenarios.
                 ForwardingMode=optional,                # Gets or sets forwarding mode.
                 IgnorePrePstFail=optional,              # Gets or sets to ignore state.
                 InitialMaskBits=optional,               # Gets or sets forwarding mode.
                 ItuffNameExtenstion=optional,           # Gets or sets For running multiple fuse values with different ITUFF prints.
                 LimitGuardband=optional,                # Gets or sets LimitGuardband to be used with VminForwarding SearchGuardbandEnabled option.
                 LookupTableConfigurationFile=optional,  # Gets or sets LookupTableConfigurationFile.
                 MappingConfig=optional,                 # Gets or sets  Mapping Config.
                 MbistTestMode=optional,                 # Gets or sets enables default or post repair flows.
                 PostInstancePlist=optional,             # Gets or sets PostInstancePlist execution.
                 PrimeNonBisrconfig=optional,            # Gets or sets  Prime VFDM config.
                 PrintToItuff=optional,                  # Gets or sets mode for printing hry string to the ituff.
                 RecoveryConfigurationFile=optional,     # Gets or sets RecoveryConfigurationFile.
                 RecoveryModeDownbin=optional,           # Gets or sets set the recovery mode of the instancMbistTestModee.
                 ScoreboardBaseNumberMbist=optional,     # Gets or sets base# used only by MBIST tools since no otherway to bypass flow.
                 TestMode=optional,                      # Gets or sets enables default or post repair flows.
                 TriggerLevelsCondition=optional,        # Gets or sets trigger levels test condition name.
                 TriggerMap=optional,                    # Gets or sets trigger map.
                 VFDMconfig=optional,                    # Gets or sets  VFDM config.
                 VminResult=optional,                    # Gets or sets vmin result. Stores value in SharedStorage using comma-separated key names with Context.DUT.
                 VoltageConverter=optional,              # Gets or sets a list of voltage overrides from VminForwarding.
                 VoltagesOffset=optional,                # Gets or sets an offset to applied voltage.
                 ApplyEndSequence=optional,              # ApplyEndSequence at the end of the test.
                 BaseNumbers=optional,                   # Comma separated list of numbers  to prefix the scoreboard counters.
                 EndVoltageLimits=required,              # End voltage limits.
                 ExecutionMode=optional,                 # Execution mode, default behaviour is Search without scoreboard.
                 FeatureSwitchSettings=optional,         # Feature switch settings.
                 FivrCondition=optional,                 # FIVR condition name.
                 IfeObject=optional,                     # IFE object of type IVminSearchExtensions.
                 LevelsTc=required,                      # Level test condition to load.
                 MaskPins=optional,                      # Comma separated string indicating which pins to mask.
                 MaxFailsNum=optional,                   # Maximum number of fails that can be processed for scoreboard counters.
                 MaxRepetitionCount=optional,            # Maximum number of times a search can be repeated for recovering purposes.
                 MultiPassMasks=optional,                # Comma separated list of mask bit strings needed for multi pass capability.
                 Patlist=required,                       # Patlist to execute.
                 PatternNameCounterIndexes=optional,     # Comma separated string of integers which map characters in the pattern name to produce a scoreboard counter.
                 PrePlist=optional,                      # PrePlist callback to plist execution.
                 PrintPatternsOccurrences=optional,      # Print failing patterns occurrences to ituff.
                 ScoreboardEdgeTicks=optional,           # Number of resolution ticks to step down when scoreboard mode is enabled.
                 StartVoltages=required,                 # Start voltage values.
                 StartVoltagesForRetry=optional,         # Lower start voltages for overshoot.
                 StepSize=required,                      # Search step size in Volts.
                 TimingsTc=required,                     # Timing test condition to load.
                 VoltageTargets=required,                # Voltage targets.
                 BypassPort=optional,                    # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,           # Enable for current instance's test time and memory information
                 LogLevel=optional,                      # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                # Enable for record detailed test time information
                 PreInstance=optional,                   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,            # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,       # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,         # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,          # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,                # A Regular Expression to minimize the patterns in the configurations.
                 RelayTestConditionName=optional,        # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,       # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PostPlist=optional,                     # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,             # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,   # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of MbistVminTC class definition


# Beginning of MbistVminTCCommonParams class definition
class MbistVminTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of MbistVminTCCommonParams class definition


# Beginning of PGMCallbacksManager class definition
class PGMCallbacksManager(BaseMethod):
    def __init__(self,
                 name,
                 IfeObject=optional,            # Gets or Sets **not in use will be removed later with the refactoring of the IfeObject**.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PGMCallbacksManager class definition


# Beginning of PGMFuseDecodeTC class definition
class PGMFuseDecodeTC(BaseMethod):
    def __init__(self,
                 name,
                 DatalogFormat=optional,           # Gets or sets Datalog parameter.
                 DieId=optional,                   # Gets or sets die id for datalogging.
                 SharedStorageBinaryUlt=optional,  # Gets or sets the SharedStorageBinaryUlt.
                 BypassPort=optional,              # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,     # Enable for current instance's test time and memory information
                 LogLevel=optional,                # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,          # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PGMFuseDecodeTC class definition


# Beginning of PGMFuseEncodeTC class definition
class PGMFuseEncodeTC(BaseMethod):
    def __init__(self,
                 name,
                 DatalogFormat=optional,              # Gets or sets Datalog parameter.
                 DieId=optional,                      # Gets or sets die id for datalogging.
                 Foundry=optional,                    # Gets or sets Foundry parameter.
                 Lot=optional,                        # Gets or sets Fab Lot.
                 SetSharedStorageBinaryUlt=optional,  # Gets or sets the SetSharedStorageBinaryUlt.
                 Wafer=optional,                      # Gets or sets Wafer Id.
                 X=optional,                          # Gets or sets X-coordinate location.
                 Y=optional,                          # Gets or sets Y-coordinate location.
                 BypassPort=optional,                 # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,        # Enable for current instance's test time and memory information
                 LogLevel=optional,                   # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,             # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PGMFuseEncodeTC class definition


# Beginning of PGMScreenTC class definition
class PGMScreenTC(BaseMethod):
    def __init__(self,
                 name,
                 ScreenTestName=required,       # Gets or sets the ScreenTestName to execute.
                 ScreenTestsFile=required,      # Gets or sets Name of the screen tests file.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PGMScreenTC class definition


# Beginning of PTHGetSetGsdsDffTC class definition
class PTHGetSetGsdsDffTC(BaseMethod):
    def __init__(self,
                 name,
                 ConfigurationFile=required,        # Gets or sets the voltage converter ActiveConfiguration file.
                 OPType=required,                   # Gets or sets the GSDS2DFF or DFF2GSDS OPType.
                 BypassPort=optional,               # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,      # Enable for current instance's test time and memory information
                 LogLevel=optional,                 # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,           # Enable for record detailed test time information
                 SetPointsPlistMode=optional,       # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,  # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,    # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,     # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,           # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,              # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,             # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PTHGetSetGsdsDffTC class definition


# Beginning of PTHGetSetGsdsDffTCCommonParams class definition
class PTHGetSetGsdsDffTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 SetPointsPlistMode=optional,       # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,  # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,    # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,     # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,           # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,              # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,             # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PTHGetSetGsdsDffTCCommonParams class definition


# Beginning of PValTC class definition
class PValTC(BaseMethod):
    def __init__(self,
                 name,
                 LevelsTc=required,                     # Gets or sets LevelsTc to plist execution.
                 MaskPins=optional,                     # Gets or sets comma separated mask pins for Patlist execution.
                 Patlist=required,                      # Gets or sets Patlist to execute.
                 SkipBurstOff=optional,                 # Gets or sets an option to skip burst off execution.
                 SkipTime0=optional,                    # Gets or sets an option to skip time0 execution.
                 TimingsTc=required,                    # Gets or sets TimingsTc for plist execution.
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PrePlist=optional,                     # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PValTC class definition


# Beginning of PValTCCommonParams class definition
class PValTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PrePlist=optional,                     # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PValTCCommonParams class definition


# Beginning of PatConfigTC class definition
class PatConfigTC(BaseMethod):
    def __init__(self,
                 name,
                 InputFile=required,            # Gets or sets the input file with all tags.
                 PlistRegEx=optional,           # Gets or sets the optional plist regular expression.
                 Tags=required,                 # Gets or sets the list of tags to apply during pattern(s) modifications.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PatConfigTC class definition


# Beginning of PatConfigTCCommonParams class definition
class PatConfigTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PatConfigTCCommonParams class definition


# Beginning of PatternDelayOptimizer class definition
class PatternDelayOptimizer(BaseMethod):
    def __init__(self,
                 name,
                 GuardbandMultiplier=optional,          # Gets or sets a guardband for the final value. The saved value will be multiplied by (1 
                 LevelsTc=required,                     # Gets or sets LevelsTc to plist execution.
                 MaskPins=optional,                     # Gets or sets comma separated mask pins for Patlist execution.
                 MaxTestpoints=optional,                # Gets or sets the maximum number of wait times to check.
                 OverwriteOutput=optional,              # Gets or sets a value indicating whether the output files should overwrite any existing files or update the file name so it is unique.
                 Patlist=required,                      # Gets or sets Patlist to execute.
                 PatmodConfig=required,                 # Gets or sets the name of the PatConfig Name (must exist in PatmodInputFile).
                 PatmodInputFile=required,              # Gets or sets the name of the input/base Prime .patmod.json file.
                 PatmodOutputFile=required,             # Gets or sets the name of the output Prime .patmod.json file.
                 PerRunPatternLimit=optional,           # Gets or sets a limit of how many patterns to run at a time. 0 means run all patterns.
                 ReloadPatConfig=optional,              # Gets or sets a value indicating whether the ALEPH/PatConfig should be reloaded before running (might fail if Prime Ticket 23312 hasn't been fixed).
                 RestorePatterns=optional,              # Gets or sets a value indicating whether the patterns should be restored to their original state when the intance finishes.
                 SearchMethod=optional,                 # Gets or sets the Type of search to do. Either Binary, LinearLowToHigh or LinearHighToLow.
                 SearchValueMax=optional,               # Gets or sets the Maximum wait value to use. If less-than-or-equal-to 0, the existing wait time in the pattern is used.
                 SearchValueMin=optional,               # Gets or sets the Minimum wait value to use.
                 SearchValueResolution=optional,        # Gets or sets the Resolution of the Search.
                 SummaryOutputFile=required,            # Gets or sets the name of the output json file which summarizes the results including the list of invalid patterns.
                 TimingsTc=required,                    # Gets or sets TimingsTc for plist execution.
                 UnitIdUserVar=optional,                # Gets or sets a user variable which contains the unit id.
                 WriteThroughSysC=optional,             # Gets or sets a value indicating whether the output files should be written using the SysC.
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PrePlist=optional,                     # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PatternDelayOptimizer class definition


# Beginning of PatternDelayOptimizerCommonParams class definition
class PatternDelayOptimizerCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PrePlist=optional,                     # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PatternDelayOptimizerCommonParams class definition


# Beginning of PatternTrimmer class definition
class PatternTrimmer(BaseMethod):
    def __init__(self,
                 name,
                 DomainRatios=required,                 # Gets or sets the list of domains with respective ratios.
                 Executions=optional,                   # Gets or sets the number of plist executions per pattern modification.
                 GuardBand=optional,                    # Gets or sets a wait time guard band to avoid marginal results.
                 LevelsTc=required,                     # Gets or sets LevelsTc to plist execution.
                 MaskPins=optional,                     # Gets or sets comma separated mask pins for Patlist execution.
                 MinRPT=optional,                       # Gets or sets the min RPT size to process.
                 Patlist=required,                      # Gets or sets Patlist to execute.
                 TargetPattern=required,                # Gets or sets a regular expression with target patterns to trim.
                 TimingsTc=required,                    # Gets or sets TimingsTc for plist execution.
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PrePlist=optional,                     # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PatternTrimmer class definition


# Beginning of PatternTrimmerCommonParams class definition
class PatternTrimmerCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PrePlist=optional,                     # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PatternTrimmerCommonParams class definition


# Beginning of PlistConfigTC class definition
class PlistConfigTC(BaseMethod):
    def __init__(self,
                 name,
                 Command=required,                      # Gets or sets command line.
                 Patlist=required,                      # Gets or sets the patlist to modify. It supports regex.
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PrePlist=optional,                     # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PlistConfigTC class definition


# Beginning of PlistConfigTCCommonParams class definition
class PlistConfigTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PrePlist=optional,                     # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PlistConfigTCCommonParams class definition


# Beginning of PlistModificationsBase class definition
class PlistModificationsBase(BaseMethod):
    def __init__(self,
                 name,
                 OperationMode=optional,        # Gets or sets the operation mode.
                 Patlists=optional,             # Gets or sets the list of patlists to restore.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PlistModificationsBase class definition


# Beginning of PlistModificationsBaseCommonParams class definition
class PlistModificationsBaseCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PlistModificationsBaseCommonParams class definition


# Beginning of PllVidWalkTC class definition
class PllVidWalkTC(BaseMethod):
    def __init__(self,
                 name,
                 FmaxKillGBMult=optional,       # Gets or sets the Scaling factor for the upper range of valid frequencies.
                 FminKillGBMult=optional,       # Gets or sets the Scaling factor for the lower range of valid frequencies.
                 FuseCfgTest=optional,          # Gets or sets the name of the EVG UF test to use to set the fuses.
                 InputFile=required,            # Gets or sets the Input file name.
                 MaxVoltage=required,           # Gets or sets the Maximum Voltage.
                 MinVoltage=required,           # Gets or sets the Minimum Voltage.
                 PllName=required,              # Gets or sets the PLL name.
                 SubFlow=optional,              # Gets or sets the name of the subflow attached to the hanging instances.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PllVidWalkTC class definition


# Beginning of PllVidWalkTCCommonParams class definition
class PllVidWalkTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PllVidWalkTCCommonParams class definition


# Beginning of PowerSequenceHandler class definition
class PowerSequenceHandler(BaseMethod):
    def __init__(self,
                 name,
                 AlarmMode=optional,            # Gets or sets AlarmMode; when is enabled alarms will be routed to different port.
                 ApplyPowerDown=optional,       # Gets or sets ApplyPowerDown while setting a new Power-On TC.
                 ApplyPowerOn=optional,         # Gets or sets ApplyPowerOn.
                 PowerDownTc=optional,          # Gets or sets Power-down TC.
                 PowerOnTc=optional,            # Gets or sets Power-on TC.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PowerSequenceHandler class definition


# Beginning of PowerSequenceHandlerCommonParams class definition
class PowerSequenceHandlerCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PowerSequenceHandlerCommonParams class definition


# Beginning of PrimeApplySerialCaptureGroupMapTestMethodCommonParams class definition
class PrimeApplySerialCaptureGroupMapTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeApplySerialCaptureGroupMapTestMethodCommonParams class definition


# Beginning of PrimeApplyTestConditionTestMethodCommonParams class definition
class PrimeApplyTestConditionTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 SetPointsPlistMode=optional,       # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,  # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,    # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,     # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,           # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,              # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,             # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FlowIndex=optional,                # Parameter to specify the instance flow index on Dynamic Flows.
                 FlowIndexCallbackName=optional,    # Flow Index callback function name. in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeApplyTestConditionTestMethodCommonParams class definition


# Beginning of PrimeArrayFusingTestMethodCommonParams class definition
class PrimeArrayFusingTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeArrayFusingTestMethodCommonParams class definition


# Beginning of PrimeArrayHryTestMethodCommonParams class definition
class PrimeArrayHryTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeArrayHryTestMethodCommonParams class definition


# Beginning of PrimeArrayRepairTestMethodCommonParams class definition
class PrimeArrayRepairTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeArrayRepairTestMethodCommonParams class definition


# Beginning of PrimeBinSetterTestMethodCommonParams class definition
class PrimeBinSetterTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeBinSetterTestMethodCommonParams class definition


# Beginning of PrimeCallbacksRegistrarTestMethodCommonParams class definition
class PrimeCallbacksRegistrarTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeCallbacksRegistrarTestMethodCommonParams class definition


# Beginning of PrimeCapturePacketsTestMethodCommonParams class definition
class PrimeCapturePacketsTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PrePlist=optional,                     # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeCapturePacketsTestMethodCommonParams class definition


# Beginning of PrimeCaptureVectorsTestMethodCommonParams class definition
class PrimeCaptureVectorsTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeCaptureVectorsTestMethodCommonParams class definition


# Beginning of PrimeContactResistanceTestMethodCommonParams class definition
class PrimeContactResistanceTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,             # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,            # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 RelayTestConditionName=optional,  # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeContactResistanceTestMethodCommonParams class definition


# Beginning of PrimeCtvDecoderTestMethodCommonParams class definition
class PrimeCtvDecoderTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeCtvDecoderTestMethodCommonParams class definition


# Beginning of PrimeCurrentDieIdManagerTestMethodCommonParams class definition
class PrimeCurrentDieIdManagerTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeCurrentDieIdManagerTestMethodCommonParams class definition


# Beginning of PrimeDcLeakageTestMethodCommonParams class definition
class PrimeDcLeakageTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,             # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,            # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 RelayTestConditionName=optional,  # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeDcLeakageTestMethodCommonParams class definition


# Beginning of PrimeDcTestMethodCommonParams class definition
class PrimeDcTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,             # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,            # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 RelayTestConditionName=optional,  # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeDcTestMethodCommonParams class definition


# Beginning of PrimeDefeatureReportTestMethodCommonParams class definition
class PrimeDefeatureReportTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeDefeatureReportTestMethodCommonParams class definition


# Beginning of PrimeDeviceEndDatalogTestMethodCommonParams class definition
class PrimeDeviceEndDatalogTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeDeviceEndDatalogTestMethodCommonParams class definition


# Beginning of PrimeDeviceEndFinalizeTestMethodCommonParams class definition
class PrimeDeviceEndFinalizeTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeDeviceEndFinalizeTestMethodCommonParams class definition


# Beginning of PrimeDeviceEndTestMethodCommonParams class definition
class PrimeDeviceEndTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeDeviceEndTestMethodCommonParams class definition


# Beginning of PrimeDeviceStartInitTestMethodCommonParams class definition
class PrimeDeviceStartInitTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeDeviceStartInitTestMethodCommonParams class definition


# Beginning of PrimeDeviceStartPackageDatalogTestMethodCommonParams class definition
class PrimeDeviceStartPackageDatalogTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeDeviceStartPackageDatalogTestMethodCommonParams class definition


# Beginning of PrimeDeviceStartSetupTestMethodCommonParams class definition
class PrimeDeviceStartSetupTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeDeviceStartSetupTestMethodCommonParams class definition


# Beginning of PrimeDeviceStartSingleDieDatalogTestMethodCommonParams class definition
class PrimeDeviceStartSingleDieDatalogTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeDeviceStartSingleDieDatalogTestMethodCommonParams class definition


# Beginning of PrimeDeviceStartTestMethodCommonParams class definition
class PrimeDeviceStartTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeDeviceStartTestMethodCommonParams class definition


# Beginning of PrimeDeviceStartWaferDatalogTestMethodCommonParams class definition
class PrimeDeviceStartWaferDatalogTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeDeviceStartWaferDatalogTestMethodCommonParams class definition


# Beginning of PrimeDffEndOfFlowValidationTestMethodCommonParams class definition
class PrimeDffEndOfFlowValidationTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeDffEndOfFlowValidationTestMethodCommonParams class definition


# Beginning of PrimeDffReadTestMethodCommonParams class definition
class PrimeDffReadTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeDffReadTestMethodCommonParams class definition


# Beginning of PrimeDynamicFuncRestoreTestMethodCommonParams class definition
class PrimeDynamicFuncRestoreTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeDynamicFuncRestoreTestMethodCommonParams class definition


# Beginning of PrimeDynamicFuncTestMethodCommonParams class definition
class PrimeDynamicFuncTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeDynamicFuncTestMethodCommonParams class definition


# Beginning of PrimeElectricalZAlignmentTestMethodCommonParams class definition
class PrimeElectricalZAlignmentTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,             # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,            # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 RelayTestConditionName=optional,  # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeElectricalZAlignmentTestMethodCommonParams class definition


# Beginning of PrimeEyeDiagramTestMethodCommonParams class definition
class PrimeEyeDiagramTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeEyeDiagramTestMethodCommonParams class definition


# Beginning of PrimeFastRasterTestMethodCommonParams class definition
class PrimeFastRasterTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeFastRasterTestMethodCommonParams class definition


# Beginning of PrimeFlowControlEndTestMethodCommonParams class definition
class PrimeFlowControlEndTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeFlowControlEndTestMethodCommonParams class definition


# Beginning of PrimeFlowControlForkTestMethodCommonParams class definition
class PrimeFlowControlForkTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeFlowControlForkTestMethodCommonParams class definition


# Beginning of PrimeFlowControlSetTestMethodCommonParams class definition
class PrimeFlowControlSetTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeFlowControlSetTestMethodCommonParams class definition


# Beginning of PrimeFlowControlStartTestMethodCommonParams class definition
class PrimeFlowControlStartTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeFlowControlStartTestMethodCommonParams class definition


# Beginning of PrimeFlowLoopControlTestMethodCommonParams class definition
class PrimeFlowLoopControlTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeFlowLoopControlTestMethodCommonParams class definition


# Beginning of PrimeFlowLoopExitTestMethodCommonParams class definition
class PrimeFlowLoopExitTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeFlowLoopExitTestMethodCommonParams class definition


# Beginning of PrimeForkTestMethodCommonParams class definition
class PrimeForkTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeForkTestMethodCommonParams class definition


# Beginning of PrimeFuncCaptureCtvTestMethodCommonParams class definition
class PrimeFuncCaptureCtvTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 SetPointsPlistMode=optional,       # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,  # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,    # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,     # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,           # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,              # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,             # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeFuncCaptureCtvTestMethodCommonParams class definition


# Beginning of PrimeFuncCaptureFailuresTestMethodCommonParams class definition
class PrimeFuncCaptureFailuresTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 SetPointsPlistMode=optional,       # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,  # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,    # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,     # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,           # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,              # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,             # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeFuncCaptureFailuresTestMethodCommonParams class definition


# Beginning of PrimeFuncCaptureScoreboardTestMethodCommonParams class definition
class PrimeFuncCaptureScoreboardTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 SetPointsPlistMode=optional,       # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,  # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,    # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,     # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,           # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,              # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,             # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeFuncCaptureScoreboardTestMethodCommonParams class definition


# Beginning of PrimeFuncDcCtvTestMethodCommonParams class definition
class PrimeFuncDcCtvTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeFuncDcCtvTestMethodCommonParams class definition


# Beginning of PrimeFuncDcTestMethodCommonParams class definition
class PrimeFuncDcTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeFuncDcTestMethodCommonParams class definition


# Beginning of PrimeFuncNoCaptureTestMethodCommonParams class definition
class PrimeFuncNoCaptureTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 SetPointsPlistMode=optional,       # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,  # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,    # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,     # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,           # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,              # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,             # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeFuncNoCaptureTestMethodCommonParams class definition


# Beginning of PrimeFunctionalTestMethodCommonParams class definition
class PrimeFunctionalTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeFunctionalTestMethodCommonParams class definition


# Beginning of PrimeFuseAtClassTestMethodCommonParams class definition
class PrimeFuseAtClassTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeFuseAtClassTestMethodCommonParams class definition


# Beginning of PrimeFuseBurnMaskTestMethodCommonParams class definition
class PrimeFuseBurnMaskTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeFuseBurnMaskTestMethodCommonParams class definition


# Beginning of PrimeFuseBurnSspecTestMethodCommonParams class definition
class PrimeFuseBurnSspecTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeFuseBurnSspecTestMethodCommonParams class definition


# Beginning of PrimeFuseReadMarginSweepTestMethodCommonParams class definition
class PrimeFuseReadMarginSweepTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeFuseReadMarginSweepTestMethodCommonParams class definition


# Beginning of PrimeFuseReadMaskTestMethodCommonParams class definition
class PrimeFuseReadMaskTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeFuseReadMaskTestMethodCommonParams class definition


# Beginning of PrimeFuseReadMaskUltDecodeTestMethodCommonParams class definition
class PrimeFuseReadMaskUltDecodeTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeFuseReadMaskUltDecodeTestMethodCommonParams class definition


# Beginning of PrimeFuseReadSspecTestMethodCommonParams class definition
class PrimeFuseReadSspecTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeFuseReadSspecTestMethodCommonParams class definition


# Beginning of PrimeGetDffTestMethodCommonParams class definition
class PrimeGetDffTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeGetDffTestMethodCommonParams class definition


# Beginning of PrimeGetRepairDffTestMethodCommonParams class definition
class PrimeGetRepairDffTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeGetRepairDffTestMethodCommonParams class definition


# Beginning of PrimeGfxAddTagBySkuNameTestMethodCommonParams class definition
class PrimeGfxAddTagBySkuNameTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeGfxAddTagBySkuNameTestMethodCommonParams class definition


# Beginning of PrimeGfxAddTagByUserDefinitionTestMethodCommonParams class definition
class PrimeGfxAddTagByUserDefinitionTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeGfxAddTagByUserDefinitionTestMethodCommonParams class definition


# Beginning of PrimeGfxEvaluateTestMethodCommonParams class definition
class PrimeGfxEvaluateTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeGfxEvaluateTestMethodCommonParams class definition


# Beginning of PrimeGfxPacketMonitorTestMethodCommonParams class definition
class PrimeGfxPacketMonitorTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeGfxPacketMonitorTestMethodCommonParams class definition


# Beginning of PrimeGfxScoreBoardTestMethodCommonParams class definition
class PrimeGfxScoreBoardTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeGfxScoreBoardTestMethodCommonParams class definition


# Beginning of PrimeGfxStartOfDeviceTestMethodCommonParams class definition
class PrimeGfxStartOfDeviceTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeGfxStartOfDeviceTestMethodCommonParams class definition


# Beginning of PrimeGfxStartTestMethodCommonParams class definition
class PrimeGfxStartTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeGfxStartTestMethodCommonParams class definition


# Beginning of PrimeHvqkManagerTestMethodCommonParams class definition
class PrimeHvqkManagerTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeHvqkManagerTestMethodCommonParams class definition


# Beginning of PrimeHvqkTestMethodCommonParams class definition
class PrimeHvqkTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeHvqkTestMethodCommonParams class definition


# Beginning of PrimeIVCurveTestMethodCommonParams class definition
class PrimeIVCurveTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,             # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,            # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 RelayTestConditionName=optional,  # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeIVCurveTestMethodCommonParams class definition


# Beginning of PrimeIdskTestMethodCommonParams class definition
class PrimeIdskTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeIdskTestMethodCommonParams class definition


# Beginning of PrimeIdvTestMethodCommonParams class definition
class PrimeIdvTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeIdvTestMethodCommonParams class definition


# Beginning of PrimeInitTestMethodCommonParams class definition
class PrimeInitTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeInitTestMethodCommonParams class definition


# Beginning of PrimeInitializeInstancesTestMethodCommonParams class definition
class PrimeInitializeInstancesTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeInitializeInstancesTestMethodCommonParams class definition


# Beginning of PrimeInitializeLibraryTestMethodCommonParams class definition
class PrimeInitializeLibraryTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeInitializeLibraryTestMethodCommonParams class definition


# Beginning of PrimeInitializeServicesTestMethodCommonParams class definition
class PrimeInitializeServicesTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeInitializeServicesTestMethodCommonParams class definition


# Beginning of PrimeInlineGetDffTestMethodCommonParams class definition
class PrimeInlineGetDffTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeInlineGetDffTestMethodCommonParams class definition


# Beginning of PrimeLSARasterTestMethodCommonParams class definition
class PrimeLSARasterTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeLSARasterTestMethodCommonParams class definition


# Beginning of PrimeLogPcsTokensTestMethodCommonParams class definition
class PrimeLogPcsTokensTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeLogPcsTokensTestMethodCommonParams class definition


# Beginning of PrimeLotEndDatalogTestMethodCommonParams class definition
class PrimeLotEndDatalogTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeLotEndDatalogTestMethodCommonParams class definition


# Beginning of PrimeLotEndFinalizeTestMethodCommonParams class definition
class PrimeLotEndFinalizeTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeLotEndFinalizeTestMethodCommonParams class definition


# Beginning of PrimeLotEndTestMethodCommonParams class definition
class PrimeLotEndTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeLotEndTestMethodCommonParams class definition


# Beginning of PrimeLotStartDatalogTestMethodCommonParams class definition
class PrimeLotStartDatalogTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeLotStartDatalogTestMethodCommonParams class definition


# Beginning of PrimeLotStartInitTestMethodCommonParams class definition
class PrimeLotStartInitTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeLotStartInitTestMethodCommonParams class definition


# Beginning of PrimeLotStartSetupTestMethodCommonParams class definition
class PrimeLotStartSetupTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeLotStartSetupTestMethodCommonParams class definition


# Beginning of PrimeLotStartTestMethodCommonParams class definition
class PrimeLotStartTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeLotStartTestMethodCommonParams class definition


# Beginning of PrimeLsaRasterRepairTestMethodCommonParams class definition
class PrimeLsaRasterRepairTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeLsaRasterRepairTestMethodCommonParams class definition


# Beginning of PrimeLyaTestMethodCommonParams class definition
class PrimeLyaTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,             # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,            # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 RelayTestConditionName=optional,  # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeLyaTestMethodCommonParams class definition


# Beginning of PrimeMbistRasterRepairTestMethodCommonParams class definition
class PrimeMbistRasterRepairTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeMbistRasterRepairTestMethodCommonParams class definition


# Beginning of PrimeMbistVminSearchTestMethodCommonParams class definition
class PrimeMbistVminSearchTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,              # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,             # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,       # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,  # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,    # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,     # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,           # A Regular Expression to minimize the patterns in the configurations.
                 SoftwareTriggerCallBack=optional,  # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,   # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeMbistVminSearchTestMethodCommonParams class definition


# Beginning of PrimeMixingDetectionTestMethodCommonParams class definition
class PrimeMixingDetectionTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeMixingDetectionTestMethodCommonParams class definition


# Beginning of PrimeOdeseBinConverterTestMethodCommonParams class definition
class PrimeOdeseBinConverterTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeOdeseBinConverterTestMethodCommonParams class definition


# Beginning of PrimePUPTestMethodCommonParams class definition
class PrimePUPTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimePUPTestMethodCommonParams class definition


# Beginning of PrimePackageHeaderTestMethodCommonParams class definition
class PrimePackageHeaderTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimePackageHeaderTestMethodCommonParams class definition


# Beginning of PrimePacketMonitorTestMethodCommonParams class definition
class PrimePacketMonitorTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimePacketMonitorTestMethodCommonParams class definition


# Beginning of PrimePacketRepairTestMethodCommonParams class definition
class PrimePacketRepairTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimePacketRepairTestMethodCommonParams class definition


# Beginning of PrimeParticipatingDutLoggerTestMethodCommonParams class definition
class PrimeParticipatingDutLoggerTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeParticipatingDutLoggerTestMethodCommonParams class definition


# Beginning of PrimePassBinToSspecAndFuseAtClassBinConverterTestMethodCommonParams class definition
class PrimePassBinToSspecAndFuseAtClassBinConverterTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimePassBinToSspecAndFuseAtClassBinConverterTestMethodCommonParams class definition


# Beginning of PrimePatConfigEngineeringTestMethodCommonParams class definition
class PrimePatConfigEngineeringTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimePatConfigEngineeringTestMethodCommonParams class definition


# Beginning of PrimePatConfigReApplyTestMethodCommonParams class definition
class PrimePatConfigReApplyTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimePatConfigReApplyTestMethodCommonParams class definition


# Beginning of PrimePatConfigTestMethodCommonParams class definition
class PrimePatConfigTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimePatConfigTestMethodCommonParams class definition


# Beginning of PrimePauseTestMethodCommonParams class definition
class PrimePauseTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 SetPointsPlistMode=optional,       # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,  # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,    # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,     # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,           # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,              # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,             # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FlowIndex=optional,                # Parameter to specify the instance flow index on Dynamic Flows.
                 FlowIndexCallbackName=optional,    # Flow Index callback function name. in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimePauseTestMethodCommonParams class definition


# Beginning of PrimePerformanceProfileTestMethodCommonParams class definition
class PrimePerformanceProfileTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimePerformanceProfileTestMethodCommonParams class definition


# Beginning of PrimePinMonitorTestMethodCommonParams class definition
class PrimePinMonitorTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimePinMonitorTestMethodCommonParams class definition


# Beginning of PrimePinProfilerTestMethodCommonParams class definition
class PrimePinProfilerTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimePinProfilerTestMethodCommonParams class definition


# Beginning of PrimePlatformPatternCachingTestMethodCommonParams class definition
class PrimePlatformPatternCachingTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimePlatformPatternCachingTestMethodCommonParams class definition


# Beginning of PrimePowerPremonitionResponseDeviceStartTestMethodCommonParams class definition
class PrimePowerPremonitionResponseDeviceStartTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimePowerPremonitionResponseDeviceStartTestMethodCommonParams class definition


# Beginning of PrimePowerPremonitionResponseInitTestMethodCommonParams class definition
class PrimePowerPremonitionResponseInitTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimePowerPremonitionResponseInitTestMethodCommonParams class definition


# Beginning of PrimeRasterTestMethodCommonParams class definition
class PrimeRasterTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeRasterTestMethodCommonParams class definition


# Beginning of PrimeRepairTestMethodCommonParams class definition
class PrimeRepairTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeRepairTestMethodCommonParams class definition


# Beginning of PrimeRepairToFuseTestMethodCommonParams class definition
class PrimeRepairToFuseTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeRepairToFuseTestMethodCommonParams class definition


# Beginning of PrimeRvCallbacksRegistrarTestMethodCommonParams class definition
class PrimeRvCallbacksRegistrarTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeRvCallbacksRegistrarTestMethodCommonParams class definition


# Beginning of PrimeSampleRateTestMethodCommonParams class definition
class PrimeSampleRateTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeSampleRateTestMethodCommonParams class definition


# Beginning of PrimeScanHRYSSNTestMethodCommonParams class definition
class PrimeScanHRYSSNTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeScanHRYSSNTestMethodCommonParams class definition


# Beginning of PrimeScanHRYStfTestMethodCommonParams class definition
class PrimeScanHRYStfTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeScanHRYStfTestMethodCommonParams class definition


# Beginning of PrimeScanHRYTestMethodCommonParams class definition
class PrimeScanHRYTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeScanHRYTestMethodCommonParams class definition


# Beginning of PrimeScanSPOFITestMethodCommonParams class definition
class PrimeScanSPOFITestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeScanSPOFITestMethodCommonParams class definition


# Beginning of PrimeScoreboardTestMethodCommonParams class definition
class PrimeScoreboardTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeScoreboardTestMethodCommonParams class definition


# Beginning of PrimeSetDffTestMethodCommonParams class definition
class PrimeSetDffTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeSetDffTestMethodCommonParams class definition


# Beginning of PrimeSetIpEndSequenceTestConditionTestMethodCommonParams class definition
class PrimeSetIpEndSequenceTestConditionTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeSetIpEndSequenceTestConditionTestMethodCommonParams class definition


# Beginning of PrimeSetRepairDffTestMethodCommonParams class definition
class PrimeSetRepairDffTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeSetRepairDffTestMethodCommonParams class definition


# Beginning of PrimeSharedStorageInserterTestMethodCommonParams class definition
class PrimeSharedStorageInserterTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeSharedStorageInserterTestMethodCommonParams class definition


# Beginning of PrimeShmooTestMethodCommonParams class definition
class PrimeShmooTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeShmooTestMethodCommonParams class definition


# Beginning of PrimeShopsTestMethodCommonParams class definition
class PrimeShopsTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeShopsTestMethodCommonParams class definition


# Beginning of PrimeSignalFileTestMethodCommonParams class definition
class PrimeSignalFileTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeSignalFileTestMethodCommonParams class definition


# Beginning of PrimeSimbaInitTestMethodCommonParams class definition
class PrimeSimbaInitTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeSimbaInitTestMethodCommonParams class definition


# Beginning of PrimeSimpleSearchTestMethodCommonParams class definition
class PrimeSimpleSearchTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PrePlist=optional,                     # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeSimpleSearchTestMethodCommonParams class definition


# Beginning of PrimeSingleDieHeaderTestMethodCommonParams class definition
class PrimeSingleDieHeaderTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeSingleDieHeaderTestMethodCommonParams class definition


# Beginning of PrimeSmartTcTestMethodCommonParams class definition
class PrimeSmartTcTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeSmartTcTestMethodCommonParams class definition


# Beginning of PrimeSortBinTraceTestMethodCommonParams class definition
class PrimeSortBinTraceTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeSortBinTraceTestMethodCommonParams class definition


# Beginning of PrimeSortCheckBinTestMethodCommonParams class definition
class PrimeSortCheckBinTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeSortCheckBinTestMethodCommonParams class definition


# Beginning of PrimeSortCheckpointTestMethodCommonParams class definition
class PrimeSortCheckpointTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeSortCheckpointTestMethodCommonParams class definition


# Beginning of PrimeSortSetBinTestMethodCommonParams class definition
class PrimeSortSetBinTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeSortSetBinTestMethodCommonParams class definition


# Beginning of PrimeSortTBinTestMethodCommonParams class definition
class PrimeSortTBinTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeSortTBinTestMethodCommonParams class definition


# Beginning of PrimeSspecToFuseAtClassBinConverterTestMethodCommonParams class definition
class PrimeSspecToFuseAtClassBinConverterTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeSspecToFuseAtClassBinConverterTestMethodCommonParams class definition


# Beginning of PrimeTdauParametricDataLoggerTestMethodCommonParams class definition
class PrimeTdauParametricDataLoggerTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeTdauParametricDataLoggerTestMethodCommonParams class definition


# Beginning of PrimeTdrCalibrationTestMethodCommonParams class definition
class PrimeTdrCalibrationTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeTdrCalibrationTestMethodCommonParams class definition


# Beginning of PrimeTesterMesIdCheckerTestMethodCommonParams class definition
class PrimeTesterMesIdCheckerTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeTesterMesIdCheckerTestMethodCommonParams class definition


# Beginning of PrimeThermalControlSetInitTestMethodCommonParams class definition
class PrimeThermalControlSetInitTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeThermalControlSetInitTestMethodCommonParams class definition


# Beginning of PrimeThermalControlSetTestMethodCommonParams class definition
class PrimeThermalControlSetTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeThermalControlSetTestMethodCommonParams class definition


# Beginning of PrimeThermalEndOfTestTestMethodCommonParams class definition
class PrimeThermalEndOfTestTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeThermalEndOfTestTestMethodCommonParams class definition


# Beginning of PrimeThermalRampTestMethodCommonParams class definition
class PrimeThermalRampTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeThermalRampTestMethodCommonParams class definition


# Beginning of PrimeThermalSingleMeasurementTestMethodCommonParams class definition
class PrimeThermalSingleMeasurementTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeThermalSingleMeasurementTestMethodCommonParams class definition


# Beginning of PrimeThermalUeiStreamTestMethodCommonParams class definition
class PrimeThermalUeiStreamTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeThermalUeiStreamTestMethodCommonParams class definition


# Beginning of PrimeTimeUnderStressControlTestMethodCommonParams class definition
class PrimeTimeUnderStressControlTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeTimeUnderStressControlTestMethodCommonParams class definition


# Beginning of PrimeTiuIdentityTestMethodCommonParams class definition
class PrimeTiuIdentityTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeTiuIdentityTestMethodCommonParams class definition


# Beginning of PrimeTiuPowerSupplyContinuityTestMethodCommonParams class definition
class PrimeTiuPowerSupplyContinuityTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,             # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,            # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 RelayTestConditionName=optional,  # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeTiuPowerSupplyContinuityTestMethodCommonParams class definition


# Beginning of PrimeTiuResistanceTestMethodCommonParams class definition
class PrimeTiuResistanceTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,             # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,            # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 RelayTestConditionName=optional,  # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeTiuResistanceTestMethodCommonParams class definition


# Beginning of PrimeTiuSignalPinLeakageTestMethodCommonParams class definition
class PrimeTiuSignalPinLeakageTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,             # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,            # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 RelayTestConditionName=optional,  # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeTiuSignalPinLeakageTestMethodCommonParams class definition


# Beginning of PrimeTriggeredDcTestMethodCommonParams class definition
class PrimeTriggeredDcTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeTriggeredDcTestMethodCommonParams class definition


# Beginning of PrimeTsmcUltDecoderTestMethodCommonParams class definition
class PrimeTsmcUltDecoderTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeTsmcUltDecoderTestMethodCommonParams class definition


# Beginning of PrimeUltDecoderTestMethodCommonParams class definition
class PrimeUltDecoderTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeUltDecoderTestMethodCommonParams class definition


# Beginning of PrimeUltEncoderTestMethodCommonParams class definition
class PrimeUltEncoderTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeUltEncoderTestMethodCommonParams class definition


# Beginning of PrimeVMeasureLoopTestMethodCommonParams class definition
class PrimeVMeasureLoopTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeVMeasureLoopTestMethodCommonParams class definition


# Beginning of PrimeVadtlOverallResultsToItuffTestMethodCommonParams class definition
class PrimeVadtlOverallResultsToItuffTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeVadtlOverallResultsToItuffTestMethodCommonParams class definition


# Beginning of PrimeVadtlTestMethodCommonParams class definition
class PrimeVadtlTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeVadtlTestMethodCommonParams class definition


# Beginning of PrimeVirtualFuseExportToDFFTestMethodCommonParams class definition
class PrimeVirtualFuseExportToDFFTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeVirtualFuseExportToDFFTestMethodCommonParams class definition


# Beginning of PrimeVirtualFuseExportToSharedStorageTestMethodCommonParams class definition
class PrimeVirtualFuseExportToSharedStorageTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeVirtualFuseExportToSharedStorageTestMethodCommonParams class definition


# Beginning of PrimeVirtualFuseImportFromDFFTestMethodCommonParams class definition
class PrimeVirtualFuseImportFromDFFTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeVirtualFuseImportFromDFFTestMethodCommonParams class definition


# Beginning of PrimeVirtualFuseResetTestMethodCommonParams class definition
class PrimeVirtualFuseResetTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeVirtualFuseResetTestMethodCommonParams class definition


# Beginning of PrimeVixVoxTestMethodCommonParams class definition
class PrimeVixVoxTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeVixVoxTestMethodCommonParams class definition


# Beginning of PrimeVminForwardingExportTestMethodCommonParams class definition
class PrimeVminForwardingExportTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeVminForwardingExportTestMethodCommonParams class definition


# Beginning of PrimeVminSearchTestMethodCommonParams class definition
class PrimeVminSearchTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,              # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,             # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,       # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,  # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,    # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,     # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,           # A Regular Expression to minimize the patterns in the configurations.
                 RelayTestConditionName=optional,   # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,  # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeVminSearchTestMethodCommonParams class definition


# Beginning of PrimeWaferHeaderTestMethodCommonParams class definition
class PrimeWaferHeaderTestMethodCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PrimeWaferHeaderTestMethodCommonParams class definition


# Beginning of PstateTest class definition
class PstateTest(BaseMethod):
    def __init__(self,
                 name,
                 CapDataDef=required,                   # Gets or sets the CapData input file (this comment will be used on the pre-header file).
                 CapturePins=required,                  # Gets or sets comma-separated list of pins to capture.
                 FailCount=required,                    # Gets or sets the FailCount number.
                 FuncVminGsdsToken=required,            # Gets or sets the FuncVminGsdsToken name.
                 InputFile=required,                    # Gets or sets the InputFile (this comment will be used on the pre-header file).
                 LevelsTc=required,                     # Gets or sets the LevelsTc name.
                 MaskPins=required,                     # Gets or sets comma-separated list of pins to mask.
                 Patlist=required,                      # Gets or sets the Patlist name.
                 TimingsTc=required,                    # Gets or sets the TimingsTc name.
                 VidDomain=required,                    # Gets or sets the VidDomain (this comment will be used on the pre-header file).
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PrePlist=optional,                     # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PstateTest class definition


# Beginning of PstateTestCommonParams class definition
class PstateTestCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PrePlist=optional,                     # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of PstateTestCommonParams class definition


# Beginning of QNRELTTC class definition
class QNRELTTC(BaseMethod):
    def __init__(self,
                 name,
                 EnablePerPatternLogging=optional,  # Gets or sets EnablePerPatternLogging featrue. Default is empty string (disable). Set to any other string to enable.
                 PauseTime=optional,                # Gets or sets PauseTime. Sets how many milliseconds to wait between vmin search test execution. A value less than 1 indicates the feature is disabled.
                 RunRegex=optional,                 # Gets or sets regular expression to filter what test names to consider.
                 SearchTestClassName=required,      # Gets or sets vminTC for MTL, but can be different based on product.
                 IfeObject=optional,                # Gets or Sets **not in use will be removed later with the refactoring of the IfeObject**.
                 Mode=required,                     #  Gets or sets the registration mode of the RV callbacks in this instance." 
                 BypassPort=optional,               # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,      # Enable for current instance's test time and memory information
                 LogLevel=optional,                 # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,           # Enable for record detailed test time information
                 PreInstance=optional,              # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,             # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of QNRELTTC class definition


# Beginning of QNRELTTCCommonParams class definition
class QNRELTTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of QNRELTTCCommonParams class definition


# Beginning of QNRRVCallbackTC class definition
class QNRRVCallbackTC(BaseMethod):
    def __init__(self,
                 name,
                 ConfigFile=required,           # Gets or sets Path to the file to be store.
                 EnableCoreAware=optional,      # Gets or sets if core deafaturing/multipasss should be used. Empty indiates disabled.
                 TestTimeSoftCap=optional,      # Gets or sets Max Test time to disable aditional data collection. FF will finish. Defaut value is 0 to indicate infinite test time is allowed.
                 ValidationMode=optional,       # Gets or sets Path to the file to be store.
                 IfeObject=optional,            # Gets or Sets **not in use will be removed later with the refactoring of the IfeObject**.
                 Mode=required,                 #  Gets or sets the registration mode of the RV callbacks in this instance." 
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of QNRRVCallbackTC class definition


# Beginning of QNRRVCallbackTCCommonParams class definition
class QNRRVCallbackTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of QNRRVCallbackTCCommonParams class definition


# Beginning of QNRRVCustomCodeTC class definition
class QNRRVCustomCodeTC(BaseMethod):
    def __init__(self,
                 name,
                 IfeObject=optional,            # Gets or Sets **not in use will be removed later with the refactoring of the IfeObject**.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of QNRRVCustomCodeTC class definition


# Beginning of QNRRVCustomCodeTCCommonParams class definition
class QNRRVCustomCodeTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of QNRRVCustomCodeTCCommonParams class definition


# Beginning of RenameTp class definition
class RenameTp(BaseMethod):
    def __init__(self,
                 name,
                 DebugUserVar=optional,         # Full collection.name of the user variable to write the last modified file/time for debug purposes.
                 FileCountLimit=optional,       # Maximum number of files to check. Will exit port -1 if this is exceeded.
                 IgnoreFiles=optional,          # Comma separate list of file names to ignore (just the file name, no path).
                 SocPathOffset=optional,        # Relative path adjustment to get from the .soc file to the main TP directory.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of RenameTp class definition


# Beginning of RenameTpCommonParams class definition
class RenameTpCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of RenameTpCommonParams class definition


# Beginning of RunCallback class definition
class RunCallback(BaseMethod):
    def __init__(self,
                 name,
                 Callback=required,             # Gets or sets the name of the callback to execute.
                 Parameters=optional,           # Gets or sets the parameters to send to the callback.
                 ResultPort=optional,           # Gets or sets an expression to set exit port based on the callback return value.
                 ResultToken=optional,          # Gets or sets the GSDS token (of the form G.U.S.TokenName) to write the callbacks return value to.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of RunCallback class definition


# Beginning of RunCallbackCommonParams class definition
class RunCallbackCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of RunCallbackCommonParams class definition


# Beginning of SFMCheckEccStatisticsStatus class definition
class SFMCheckEccStatisticsStatus(BaseMethod):
    def __init__(self,
                 name,
                 NumberOfCorrectableError=required,      # Gets or sets the No Correctable Error.
                 SetPoint=required,                      # Gets or sets the Fab Process.
                 AlarmPortRedirect=optional,             # The alarm port redirect disabled or enabled.
                 ApplyEndSequence=optional,              # The ApplyEndSequence at the end of the test.
                 CtvCapturePerCycleMode=optional,        # CTV capture mode. If DISABLED (default), CTV capture will be per pin. If ENABLED it will be per cycle.
                 CtvCapturePins=optional,                # Comma separated pins for CTV capture.
                 DtsConfigurationName=optional,          # Configuration in case DTS processing is wanted.
                 FailuresToCapturePerPattern=optional,   # Int for number of failures per pattern to capture. If 0 (default), per pattern capture is disabled.
                 FailuresToCaptureTotal=optional,        # Int for the number of global failures to capture. If 0 (default), it means failure capture is disabled.
                 IfeObject=optional,                     #  Gets or sets the IFE object of type IFuncCaptureExtensions.
                 LevelsTc=required,                      # LevelsTc to plist execution.
                 MaskPins=optional,                      # Comma separated pins for mask.
                 MaxFailuresPerPatternToItuff=optional,  # Int for number of failures per pattern to print to ituff. If 0 (default), per pattern failure count defaults to MaxFailuresToItuff.
                 MaxFailuresToItuff=optional,            # int for the number of global failures to print to ituff. If 0 (default), it means failure prints are disabled.
                 Patlist=required,                       # Patlist to execute.
                 PrePlist=optional,                      # PrePlist callback to plist execution.
                 TimingsTc=required,                     # TimingsTc for plist execution.
                 BypassPort=optional,                    # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,           # Enable for current instance's test time and memory information
                 LogLevel=optional,                      # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                # Enable for record detailed test time information
                 SetPointsPlistMode=optional,            # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,       # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,         # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,          # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,                # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,             # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,   # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 RelayTestConditionName=optional,        # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,       # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PostPlist=optional,                     # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of SFMCheckEccStatisticsStatus class definition


# Beginning of SFMDffEfuseCheck class definition
class SFMDffEfuseCheck(BaseMethod):
    def __init__(self,
                 name,
                 DffFormat=required,            # Gets or sets the FoverousProduct from user.
                 DieIdName=required,            # Gets or sets the DieIdName from user. PKG/U1/U2.
                 UserVarCollection=required,    # Gets or sets the UserVar Collection from user.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of SFMDffEfuseCheck class definition


# Beginning of SFMFUSEBURNFuseReadMask class definition
class SFMFUSEBURNFuseReadMask(BaseMethod):
    def __init__(self,
                 name,
                 ExceptionPort=required,                   # Gets or sets the expected port if all mask(s) compare returns false. Can define single or multiple name with comma delimiter.
                 ExpectedPort=required,                    # Gets or sets the expected port if the mask compare returns true. Can define single or multiple name with comma delimiter.
                 FuseMaskName=required,                    # Gets or sets fuse string mask(s). Can define single or multiple name with comma delimiter.
                 FuseReadGlobal=optional,                  # Gets or sets the input parameter as UserVar for FLE to consume.
                 ApplyEndSequence=optional,                # ApplyEndSequence at the end of the test.
                 ConfigName=required,                      # Configuration name for the input file. Can only define single name.
                 ConfigurationFile=required,               # ConfigurationFile. ~HDMT_TPL_DIR/Modules/FuseRead/FuseRead/InputFiles/fuseReadScenario1.json. other using type String.
                 EnableCaptureFunctionalFailure=optional,  # A value whether to enable CreateCaptureFailureAndCtvPerPinTest(true) or CreateCaptureCtvPerPinTest(false).
                 FailingMaskName=optional,                 # Failing mask names. Can define single or multiple name with comma delimiter.
                 FuseGroupToDatalog=optional,              # Name of fuse group to datalog. When this parameter is defined (enabled) with valid fuse group name, the fuse string of the fuse group name will be datalog to ituff.
                 IfeObject=optional,                       # IFE object of type IFuseReadMaskExtensions.
                 LevelsTc=optional,                        # LevelsTc for plist execution.
                 MaskPins=optional,                        # Comma separated pins for mask.
                 PassingMaskName=optional,                 # Passing mask names. Can define single or multiple name with comma delimiter.
                 Patlist=optional,                         # Patlist to execute.
                 PrePlist=optional,                        # Pre Patlist to execute.
                 RegisterName=required,                    # Name of registers to select within the configuration. Can define single or multiple name with comma delimiter.
                 SimulationMode=optional,                  # Simulation mode. Indicating whether fuse string value is set with SimulationString (True) or CtvData (False).
                 TimingsTc=optional,                       # TimingsTc for plist execution.
                 VoltageFile=optional,                     # VoltageFile. ~HDMT_TPL_DIR/Modules/FuseRead/FuseRead/InputFiles/fuseReadVoltage.json. other using type String.
                 BypassPort=optional,                      # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,             # Enable for current instance's test time and memory information
                 LogLevel=optional,                        # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                  # Enable for record detailed test time information
                 PreInstance=optional,                     # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                    # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,              # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,         # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,           # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,            # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,                  # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,               # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,     # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,         # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,          # The RelayTestCondition to apply.
                 PostPlist=optional,                       # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of SFMFUSEBURNFuseReadMask class definition


# Beginning of SFMFUSEBURNValForkTest class definition
class SFMFUSEBURNValForkTest(BaseMethod):
    def __init__(self,
                 name,
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of SFMFUSEBURNValForkTest class definition


# Beginning of SFMFaCTBegin class definition
class SFMFaCTBegin(BaseMethod):
    def __init__(self,
                 name,
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of SFMFaCTBegin class definition


# Beginning of SFMFaCTExecute class definition
class SFMFaCTExecute(BaseMethod):
    def __init__(self,
                 name,
                 Key=required,                  # Gets or sets the Mapping Object Key for the shared storage.
                 KeyContext=required,           # Gets or sets the Context value for the Key.
                 WritingContext=required,       # Gets or sets the Context value for writing the data to shared storage.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of SFMFaCTExecute class definition


# Beginning of SFMFaCTExitController class definition
class SFMFaCTExitController(BaseMethod):
    def __init__(self,
                 name,
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of SFMFaCTExitController class definition


# Beginning of SFMFaCTInit class definition
class SFMFaCTInit(BaseMethod):
    def __init__(self,
                 name,
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of SFMFaCTInit class definition


# Beginning of SFMFuseCaptureCSRScreenTest class definition
class SFMFuseCaptureCSRScreenTest(BaseMethod):
    def __init__(self,
                 name,
                 PICVersion=required,                    # Gets or sets PIC version.
                 SetFlow=required,                       # Gets or sets Flow.
                 AlarmPortRedirect=optional,             # The alarm port redirect disabled or enabled.
                 ApplyEndSequence=optional,              # The ApplyEndSequence at the end of the test.
                 CtvCapturePerCycleMode=optional,        # CTV capture mode. If DISABLED (default), CTV capture will be per pin. If ENABLED it will be per cycle.
                 CtvCapturePins=optional,                # Comma separated pins for CTV capture.
                 DtsConfigurationName=optional,          # Configuration in case DTS processing is wanted.
                 FailuresToCapturePerPattern=optional,   # Int for number of failures per pattern to capture. If 0 (default), per pattern capture is disabled.
                 FailuresToCaptureTotal=optional,        # Int for the number of global failures to capture. If 0 (default), it means failure capture is disabled.
                 IfeObject=optional,                     #  Gets or sets the IFE object of type IFuncCaptureExtensions.
                 LevelsTc=required,                      # LevelsTc to plist execution.
                 MaskPins=optional,                      # Comma separated pins for mask.
                 MaxFailuresPerPatternToItuff=optional,  # Int for number of failures per pattern to print to ituff. If 0 (default), per pattern failure count defaults to MaxFailuresToItuff.
                 MaxFailuresToItuff=optional,            # int for the number of global failures to print to ituff. If 0 (default), it means failure prints are disabled.
                 Patlist=required,                       # Patlist to execute.
                 PrePlist=optional,                      # PrePlist callback to plist execution.
                 TimingsTc=required,                     # TimingsTc for plist execution.
                 BypassPort=optional,                    # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,           # Enable for current instance's test time and memory information
                 LogLevel=optional,                      # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                # Enable for record detailed test time information
                 SetPointsPlistMode=optional,            # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,       # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,         # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,          # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,                # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,             # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,   # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 RelayTestConditionName=optional,        # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,       # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PostPlist=optional,                     # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of SFMFuseCaptureCSRScreenTest class definition


# Beginning of SFMFuseReadMask class definition
class SFMFuseReadMask(BaseMethod):
    def __init__(self,
                 name,
                 ExceptionPort=required,                   # Gets or sets the expected port if all mask(s) compare returns false. Can define single or multiple name with comma delimiter.
                 ExpectedPort=required,                    # Gets or sets the expected port if the mask compare returns true. Can define single or multiple name with comma delimiter.
                 FuseMaskName=required,                    # Gets or sets fuse string mask(s). Can define single or multiple name with comma delimiter.
                 FuseReadGlobal=optional,                  # Gets or sets the input parameter as UserVar for FLE to consume.
                 ApplyEndSequence=optional,                # ApplyEndSequence at the end of the test.
                 ConfigName=required,                      # Configuration name for the input file. Can only define single name.
                 ConfigurationFile=required,               # ConfigurationFile. ~HDMT_TPL_DIR/Modules/FuseRead/FuseRead/InputFiles/fuseReadScenario1.json. other using type String.
                 EnableCaptureFunctionalFailure=optional,  # A value whether to enable CreateCaptureFailureAndCtvPerPinTest(true) or CreateCaptureCtvPerPinTest(false).
                 FailingMaskName=optional,                 # Failing mask names. Can define single or multiple name with comma delimiter.
                 FuseGroupToDatalog=optional,              # Name of fuse group to datalog. When this parameter is defined (enabled) with valid fuse group name, the fuse string of the fuse group name will be datalog to ituff.
                 IfeObject=optional,                       # IFE object of type IFuseReadMaskExtensions.
                 LevelsTc=optional,                        # LevelsTc for plist execution.
                 MaskPins=optional,                        # Comma separated pins for mask.
                 PassingMaskName=optional,                 # Passing mask names. Can define single or multiple name with comma delimiter.
                 Patlist=optional,                         # Patlist to execute.
                 PrePlist=optional,                        # Pre Patlist to execute.
                 RegisterName=required,                    # Name of registers to select within the configuration. Can define single or multiple name with comma delimiter.
                 SimulationMode=optional,                  # Simulation mode. Indicating whether fuse string value is set with SimulationString (True) or CtvData (False).
                 TimingsTc=optional,                       # TimingsTc for plist execution.
                 VoltageFile=optional,                     # VoltageFile. ~HDMT_TPL_DIR/Modules/FuseRead/FuseRead/InputFiles/fuseReadVoltage.json. other using type String.
                 BypassPort=optional,                      # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,             # Enable for current instance's test time and memory information
                 LogLevel=optional,                        # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                  # Enable for record detailed test time information
                 PreInstance=optional,                     # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                    # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,              # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,         # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,           # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,            # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,                  # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,               # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,     # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,         # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,          # The RelayTestCondition to apply.
                 PostPlist=optional,                       # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of SFMFuseReadMask class definition


# Beginning of SFMIFPFLOWFORK class definition
class SFMIFPFLOWFORK(BaseMethod):
    def __init__(self,
                 name,
                 Operation=required,            # Gets or sets the Operation. eg.PHMHOT/CLASSCOLD/FACR (this comment will be used on the pre-header file).
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of SFMIFPFLOWFORK class definition


# Beginning of SFMIFPINITIALREAD class definition
class SFMIFPINITIALREAD(BaseMethod):
    def __init__(self,
                 name,
                 ContextToStore=optional,                  # Gets or sets the ContextToStore.
                 NegativeTestMask=optional,                # Gets or sets the mask name(s) for negative testing purpose such as open_socket. Can define single or multiple name with comma delimiter.Optional.
                 ProgrammedMask=required,                  # Gets or sets the mask name(s) for programmed unit. Can define single or multiple name with comma delimiter.
                 RetestFlagStorageName=required,           # Gets or sets the shared storage name to store "0" for retest flag purpose. Can define single or multiple name with comma delimiter.Optional.
                 UnprogrammedMask=required,                # Gets or sets the mask name(s) for unprogrammed unit. Can define single or multiple name with comma delimiter.
                 ApplyEndSequence=optional,                # ApplyEndSequence at the end of the test.
                 ConfigName=required,                      # Configuration name for the input file. Can only define single name.
                 ConfigurationFile=required,               # ConfigurationFile. ~HDMT_TPL_DIR/Modules/FuseRead/FuseRead/InputFiles/fuseReadScenario1.json. other using type String.
                 EnableCaptureFunctionalFailure=optional,  # A value whether to enable CreateCaptureFailureAndCtvPerPinTest(true) or CreateCaptureCtvPerPinTest(false).
                 FailingMaskName=optional,                 # Failing mask names. Can define single or multiple name with comma delimiter.
                 FuseGroupToDatalog=optional,              # Name of fuse group to datalog. When this parameter is defined (enabled) with valid fuse group name, the fuse string of the fuse group name will be datalog to ituff.
                 IfeObject=optional,                       # IFE object of type IFuseReadMaskExtensions.
                 LevelsTc=optional,                        # LevelsTc for plist execution.
                 MaskPins=optional,                        # Comma separated pins for mask.
                 PassingMaskName=optional,                 # Passing mask names. Can define single or multiple name with comma delimiter.
                 Patlist=optional,                         # Patlist to execute.
                 PrePlist=optional,                        # Pre Patlist to execute.
                 RegisterName=required,                    # Name of registers to select within the configuration. Can define single or multiple name with comma delimiter.
                 SimulationMode=optional,                  # Simulation mode. Indicating whether fuse string value is set with SimulationString (True) or CtvData (False).
                 TimingsTc=optional,                       # TimingsTc for plist execution.
                 VoltageFile=optional,                     # VoltageFile. ~HDMT_TPL_DIR/Modules/FuseRead/FuseRead/InputFiles/fuseReadVoltage.json. other using type String.
                 BypassPort=optional,                      # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,             # Enable for current instance's test time and memory information
                 LogLevel=optional,                        # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                  # Enable for record detailed test time information
                 PreInstance=optional,                     # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                    # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,              # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,         # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,           # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,            # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,                  # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,               # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,     # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,         # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,          # The RelayTestCondition to apply.
                 PostPlist=optional,                       # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of SFMIFPINITIALREAD class definition


# Beginning of SFMIFPRAPQRE class definition
class SFMIFPRAPQRE(BaseMethod):
    def __init__(self,
                 name,
                 VmaxMask=optional,                        # Gets or sets Mask Name for Vmax condition. Can define single or multiple name with comma delimiter.
                 VminMask=optional,                        # Gets or sets Mask Name for Vmax condition. Can define single or multiple name with comma delimiter.
                 VnomMask=optional,                        # Gets or sets Mask Name for Vnom condition. Can define single or multiple name with comma delimiter.
                 ApplyEndSequence=optional,                # ApplyEndSequence at the end of the test.
                 ConfigName=required,                      # Configuration name for the input file. Can only define single name.
                 ConfigurationFile=required,               # ConfigurationFile. ~HDMT_TPL_DIR/Modules/FuseRead/FuseRead/InputFiles/fuseReadScenario1.json. other using type String.
                 EnableCaptureFunctionalFailure=optional,  # A value whether to enable CreateCaptureFailureAndCtvPerPinTest(true) or CreateCaptureCtvPerPinTest(false).
                 FailingMaskName=optional,                 # Failing mask names. Can define single or multiple name with comma delimiter.
                 FuseGroupToDatalog=optional,              # Name of fuse group to datalog. When this parameter is defined (enabled) with valid fuse group name, the fuse string of the fuse group name will be datalog to ituff.
                 IfeObject=optional,                       # IFE object of type IFuseReadMaskExtensions.
                 LevelsTc=optional,                        # LevelsTc for plist execution.
                 MaskPins=optional,                        # Comma separated pins for mask.
                 PassingMaskName=optional,                 # Passing mask names. Can define single or multiple name with comma delimiter.
                 Patlist=optional,                         # Patlist to execute.
                 PrePlist=optional,                        # Pre Patlist to execute.
                 RegisterName=required,                    # Name of registers to select within the configuration. Can define single or multiple name with comma delimiter.
                 SimulationMode=optional,                  # Simulation mode. Indicating whether fuse string value is set with SimulationString (True) or CtvData (False).
                 TimingsTc=optional,                       # TimingsTc for plist execution.
                 VoltageFile=optional,                     # VoltageFile. ~HDMT_TPL_DIR/Modules/FuseRead/FuseRead/InputFiles/fuseReadVoltage.json. other using type String.
                 BypassPort=optional,                      # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,             # Enable for current instance's test time and memory information
                 LogLevel=optional,                        # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                  # Enable for record detailed test time information
                 PreInstance=optional,                     # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                    # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,              # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,         # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,           # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,            # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,                  # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,               # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,     # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,         # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,          # The RelayTestCondition to apply.
                 PostPlist=optional,                       # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of SFMIFPRAPQRE class definition


# Beginning of SFMPUFFuseReadMask class definition
class SFMPUFFuseReadMask(BaseMethod):
    def __init__(self,
                 name,
                 ExceptionPort=required,                   # Gets or sets the expected port if all mask(s) compare returns false. Can define single or multiple name with comma delimiter.
                 ExpectedPort=required,                    # Gets or sets the expected port if the mask compare returns true. Can define single or multiple name with comma delimiter.
                 FuseMaskName=required,                    # Gets or sets fuse string mask(s). Can define single or multiple name with comma delimiter.
                 FuseReadGlobal=optional,                  # Gets or sets the input parameter as UserVar for FLE to consume.
                 ApplyEndSequence=optional,                # ApplyEndSequence at the end of the test.
                 ConfigName=required,                      # Configuration name for the input file. Can only define single name.
                 ConfigurationFile=required,               # ConfigurationFile. ~HDMT_TPL_DIR/Modules/FuseRead/FuseRead/InputFiles/fuseReadScenario1.json. other using type String.
                 EnableCaptureFunctionalFailure=optional,  # A value whether to enable CreateCaptureFailureAndCtvPerPinTest(true) or CreateCaptureCtvPerPinTest(false).
                 FailingMaskName=optional,                 # Failing mask names. Can define single or multiple name with comma delimiter.
                 FuseGroupToDatalog=optional,              # Name of fuse group to datalog. When this parameter is defined (enabled) with valid fuse group name, the fuse string of the fuse group name will be datalog to ituff.
                 IfeObject=optional,                       # IFE object of type IFuseReadMaskExtensions.
                 LevelsTc=optional,                        # LevelsTc for plist execution.
                 MaskPins=optional,                        # Comma separated pins for mask.
                 PassingMaskName=optional,                 # Passing mask names. Can define single or multiple name with comma delimiter.
                 Patlist=optional,                         # Patlist to execute.
                 PrePlist=optional,                        # Pre Patlist to execute.
                 RegisterName=required,                    # Name of registers to select within the configuration. Can define single or multiple name with comma delimiter.
                 SimulationMode=optional,                  # Simulation mode. Indicating whether fuse string value is set with SimulationString (True) or CtvData (False).
                 TimingsTc=optional,                       # TimingsTc for plist execution.
                 VoltageFile=optional,                     # VoltageFile. ~HDMT_TPL_DIR/Modules/FuseRead/FuseRead/InputFiles/fuseReadVoltage.json. other using type String.
                 BypassPort=optional,                      # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,             # Enable for current instance's test time and memory information
                 LogLevel=optional,                        # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                  # Enable for record detailed test time information
                 PreInstance=optional,                     # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                    # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,              # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,         # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,           # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,            # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,                  # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,               # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,     # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,         # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,          # The RelayTestCondition to apply.
                 PostPlist=optional,                       # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of SFMPUFFuseReadMask class definition


# Beginning of SFMPostProcessIseedKey class definition
class SFMPostProcessIseedKey(BaseMethod):
    def __init__(self,
                 name,
                 KeyTypeId=required,              # Gets or sets KeyTypeId.
                 KeyTypeIdBinaryLength=required,  # Gets or sets KeyTypeIdBinaryLength.
                 BypassPort=optional,             # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,    # Enable for current instance's test time and memory information
                 LogLevel=optional,               # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,         # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of SFMPostProcessIseedKey class definition


# Beginning of SIOEDCLogTC class definition
class SIOEDCLogTC(BaseMethod):
    def __init__(self,
                 name,
                 ReuseCaptMemGlobal=optional,            # Gets or sets the ReuseCaptMemGlobal. If set, the plist will not be executed, instead the capture memory will be read from this global. The global can be GSDS, UserVar or SharedStorage. Formats for Globals: UserVar:collection.uservar GSDS:G.[UL].S.token 
                 UserFile=required,                      # Gets or sets the User File name.
                 UserToken=required,                     # Gets or sets the User Token.
                 AlarmPortRedirect=optional,             # The alarm port redirect disabled or enabled.
                 ApplyEndSequence=optional,              # The ApplyEndSequence at the end of the test.
                 CtvCapturePerCycleMode=optional,        # CTV capture mode. If DISABLED (default), CTV capture will be per pin. If ENABLED it will be per cycle.
                 CtvCapturePins=optional,                # Comma separated pins for CTV capture.
                 DtsConfigurationName=optional,          # Configuration in case DTS processing is wanted.
                 FailuresToCapturePerPattern=optional,   # Int for number of failures per pattern to capture. If 0 (default), per pattern capture is disabled.
                 FailuresToCaptureTotal=optional,        # Int for the number of global failures to capture. If 0 (default), it means failure capture is disabled.
                 IfeObject=optional,                     #  Gets or sets the IFE object of type IFuncCaptureExtensions.
                 LevelsTc=required,                      # LevelsTc to plist execution.
                 MaskPins=optional,                      # Comma separated pins for mask.
                 MaxFailuresPerPatternToItuff=optional,  # Int for number of failures per pattern to print to ituff. If 0 (default), per pattern failure count defaults to MaxFailuresToItuff.
                 MaxFailuresToItuff=optional,            # int for the number of global failures to print to ituff. If 0 (default), it means failure prints are disabled.
                 Patlist=required,                       # Patlist to execute.
                 PrePlist=optional,                      # PrePlist callback to plist execution.
                 TimingsTc=required,                     # TimingsTc for plist execution.
                 BypassPort=optional,                    # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,           # Enable for current instance's test time and memory information
                 LogLevel=optional,                      # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                # Enable for record detailed test time information
                 SetPointsPlistMode=optional,            # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,       # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,         # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,          # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,                # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,             # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,   # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 RelayTestConditionName=optional,        # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,       # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PostPlist=optional,                     # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of SIOEDCLogTC class definition


# Beginning of SIOEDCLogTCCommonParams class definition
class SIOEDCLogTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of SIOEDCLogTCCommonParams class definition


# Beginning of SIOEDCMainTC class definition
class SIOEDCMainTC(BaseMethod):
    def __init__(self,
                 name,
                 EDCLogEnabled=optional,        # Gets or sets a value indicating wheter EDC Logging is enabled.
                 EDCShmooEnabled=optional,      # Gets or sets a value indicating wheter EDC Shmoo Mode is enabled.
                 PostTestTokens=optional,       # Gets or sets comma separated list of tokens to run after the main test.
                 PreTestTokens=optional,        # Gets or sets comma separated list of tokens to run before the main test.
                 UserFile=required,             # Gets or sets the User File name.
                 UserToken=required,            # Gets or sets the User Token.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of SIOEDCMainTC class definition


# Beginning of SIOEDCMainTCCommonParams class definition
class SIOEDCMainTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of SIOEDCMainTCCommonParams class definition


# Beginning of SIOShmooTC class definition
class SIOShmooTC(BaseMethod):
    def __init__(self,
                 name,
                 PostTestTokens=optional,       # Gets or sets comma separated list of tokens to run after the main test.
                 PreTestTokens=optional,        # Gets or sets comma separated list of tokens to run before the main test.
                 UserFile=required,             # Gets or sets the User File name.
                 UserToken=required,            # Gets or sets the User Token.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of SIOShmooTC class definition


# Beginning of SIOShmooTCCommonParams class definition
class SIOShmooTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of SIOShmooTCCommonParams class definition


# Beginning of ScanHRYOCC class definition
class ScanHRYOCC(BaseMethod):
    def __init__(self,
                 name,
                 HRYInputFile=required,                 # Gets or sets HRY generation rules input file.
                 LevelsTc=required,                     # Gets or sets LevelsTc to plist execution.
                 MaskPins=optional,                     # Gets or sets comma separated pins for mask.
                 Patlist=required,                      # Gets or sets Patlist to execute.
                 PerPartitionLogging=optional,          # Gets or sets the controls for when to do the Per-Partition Logging.
                 PerPatFailCaptureCount=optional,       # Gets or sets number of Patlist execution failures to capture per pattern. The minimal number is 1.
                 TimingsTc=required,                    # Gets or sets TimingsTc for plist execution.
                 TotalFailCaptureCount=optional,        # Gets or sets number of Patlist execution failures to capture per plist.
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PrePlist=optional,                     # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of ScanHRYOCC class definition


# Beginning of ScanHRYOCCCommonParams class definition
class ScanHRYOCCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PrePlist=optional,                     # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of ScanHRYOCCCommonParams class definition


# Beginning of ScreenTC class definition
class ScreenTC(BaseMethod):
    def __init__(self,
                 name,
                 ScreenTestSet=required,        # Gets or sets the name of the Set to execute.
                 ScreenTestsFile=required,      # Gets or sets Name of the screen tests file.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of ScreenTC class definition


# Beginning of ScreenTCCommonParams class definition
class ScreenTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of ScreenTCCommonParams class definition


# Beginning of SimpleCtvTC class definition
class SimpleCtvTC(BaseMethod):
    def __init__(self,
                 name,
                 Limits=optional,                        # Gets or sets registers limits for selected registers. Format: --high reg1:11 --low reg2:1.
                 Print=optional,                         # Gets or sets registers to print to ituff. Format: --registers reg1 reg2.
                 Registers=required,                     # Gets or sets registers to decode from CTV. Format: --registers reg1:11-0 reg2:13,12.
                 Save=optional,                          # Gets or sets registers to save in shared storage and user vars.
                 AlarmPortRedirect=optional,             # The alarm port redirect disabled or enabled.
                 ApplyEndSequence=optional,              # The ApplyEndSequence at the end of the test.
                 CtvCapturePerCycleMode=optional,        # CTV capture mode. If DISABLED (default), CTV capture will be per pin. If ENABLED it will be per cycle.
                 CtvCapturePins=optional,                # Comma separated pins for CTV capture.
                 DtsConfigurationName=optional,          # Configuration in case DTS processing is wanted.
                 FailuresToCapturePerPattern=optional,   # Int for number of failures per pattern to capture. If 0 (default), per pattern capture is disabled.
                 FailuresToCaptureTotal=optional,        # Int for the number of global failures to capture. If 0 (default), it means failure capture is disabled.
                 IfeObject=optional,                     #  Gets or sets the IFE object of type IFuncCaptureExtensions.
                 LevelsTc=required,                      # LevelsTc to plist execution.
                 MaskPins=optional,                      # Comma separated pins for mask.
                 MaxFailuresPerPatternToItuff=optional,  # Int for number of failures per pattern to print to ituff. If 0 (default), per pattern failure count defaults to MaxFailuresToItuff.
                 MaxFailuresToItuff=optional,            # int for the number of global failures to print to ituff. If 0 (default), it means failure prints are disabled.
                 Patlist=required,                       # Patlist to execute.
                 PrePlist=optional,                      # PrePlist callback to plist execution.
                 TimingsTc=required,                     # TimingsTc for plist execution.
                 BypassPort=optional,                    # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,           # Enable for current instance's test time and memory information
                 LogLevel=optional,                      # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                # Enable for record detailed test time information
                 SetPointsPlistMode=optional,            # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,       # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,         # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,          # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,                # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,             # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,   # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 RelayTestConditionName=optional,        # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,       # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PostPlist=optional,                     # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of SimpleCtvTC class definition


# Beginning of SimpleCtvTCCommonParams class definition
class SimpleCtvTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of SimpleCtvTCCommonParams class definition


# Beginning of SocRecovery class definition
class SocRecovery(BaseMethod):
    def __init__(self,
                 name,
                 RecoveryMode=optional,         # Gets or sets recovery tracking name.
                 SerialModeLength=optional,     # Number of characters required for Serial mode recovery string
                 TokenNames=optional,           # Gets or sets list of recovery tokens delimited with | or spaces.
                 ValueList=optional,            # Gets or sets list of recovery values to set tokens with, number of values must match number of tokens.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of SocRecovery class definition


# Beginning of SocRecoveryCommonParams class definition
class SocRecoveryCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of SocRecoveryCommonParams class definition


# Beginning of SsidBinnerTC class definition
class SsidBinnerTC(BaseMethod):
    def __init__(self,
                 name,
                 Port=required,                 # Gets or sets the name of the callback to execute.
                 Ssid=optional,                 # Gets or sets the ssid.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of SsidBinnerTC class definition


# Beginning of SsidBinnerTCCommonParams class definition
class SsidBinnerTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of SsidBinnerTCCommonParams class definition


# Beginning of StaControlSetInitTC class definition
class StaControlSetInitTC(BaseMethod):
    def __init__(self,
                 name,
                 HandlerRecipe=optional,        # Gets or sets the path to handler recipe.
                 IntecApp=optional,             # Gets or sets the path to Intec path.
                 IntecJson=optional,            # Gets or sets the path to Intec json.
                 PolarisApp=optional,           # Gets or sets the path to Polaris path.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of StaControlSetInitTC class definition


# Beginning of StaControlSetInitTCCommonParams class definition
class StaControlSetInitTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of StaControlSetInitTCCommonParams class definition


# Beginning of StaControlSetTC class definition
class StaControlSetTC(BaseMethod):
    def __init__(self,
                 name,
                 ControlSet=required,           # Gets or sets the name that matches desired index to choose values from.
                 GuardBand=optional,            # Gets or sets polaris guardband in C.
                 PostRamp=optional,             # Gets or sets post-ramp sleep time in seconds.
                 TimeOut=optional,              # Gets or sets polaris instance time-out in seconds.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of StaControlSetTC class definition


# Beginning of StaControlSetTCCommonParams class definition
class StaControlSetTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of StaControlSetTCCommonParams class definition


# Beginning of TdrLoggerTC class definition
class TdrLoggerTC(BaseMethod):
    def __init__(self,
                 name,
                 Pins=optional,                 # Gets or sets the list of pins to log. It supports regx: if no pin name is entered all pins are logged.
                 TdrFile=required,              # Gets or sets TDR file to log. It supports wild card: in case of multiple matches it will pull last modified file.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of TdrLoggerTC class definition


# Beginning of TdrLoggerTCCommonParams class definition
class TdrLoggerTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of TdrLoggerTCCommonParams class definition


# Beginning of TesterScreenTC class definition
class TesterScreenTC(BaseMethod):
    def __init__(self,
                 name,
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of TesterScreenTC class definition


# Beginning of TesterScreenTCCommonParams class definition
class TesterScreenTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of TesterScreenTCCommonParams class definition


# Beginning of TimeTracker class definition
class TimeTracker(BaseMethod):
    def __init__(self,
                 name,
                 Argument=optional,             # Gets or sets the Argument for time tracker.
                 TestMode=optional,             # Gets or sets the TestMode.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of TimeTracker class definition


# Beginning of TimeTrackerCommonParams class definition
class TimeTrackerCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of TimeTrackerCommonParams class definition


# Beginning of TriggeredDcCtv class definition
class TriggeredDcCtv(BaseMethod):
    def __init__(self,
                 name,
                 AddPinNamePostfix=optional,             # Gets or sets the AddPinNamePostfix.
                 CheckDcLimits=optional,                 # Gets or sets the Check DC Limits value.
                 CheckFunctionalResult=optional,         # Gets or sets the CheckFunctionalResult.
                 ConfigurationFile=optional,             # Gets or sets JSON file with data structure parameters.
                 ConfigurationName=optional,             # Gets or sets CSV file with dataStructure parameters.
                 CsvOutput=optional,                     # Gets or sets the CsvOutput.
                 CtvConfigurationFile=optional,          # Gets or sets CSV file with ctv services data tructure parameters.
                 CtvFunctionality=optional,              # Gets or sets the CtvFunctionality.
                 Defeature=optional,                     # Gets or sets Defeature.
                 DieIdDisable=optional,                  # Gets or sets comma separated list of SSIDs to be disabled (ignored) during CTV processing.
                 DieIdRename=optional,                   # Gets or sets the DieIdRename.
                 EOTPowerDown=optional,                  # Gets or sets the EOTPowerDown.
                 ItuffCompression=optional,              # Gets or sets the ItuffCompression.
                 PerDieBinning=optional,                 # Gets or sets the PerDieBinning.
                 PinRenamePostfix=optional,              # Gets or sets the PinRenamePostfix.
                 PostProcessingAction=optional,          # Gets or sets the PostProcessingAction.
                 RequiredSampleCount=optional,           # Gets or sets the RequiredSampleCount.
                 AlarmPortRedirect=optional,             # Gets or sets the alarm port redirect disabled or enabled.
                 ApplyEndSequence=optional,              # The ApplyEndSequence at the end of the test.
                 CtvPins=optional,                       # Gets or sets comma separated pins to get CTV from the plist execution.
                 DatalogLevel=optional,                  # Gets or sets datalog level(ALL, FAIL_ONLY, COMPRESS, PINMAP_COMPRESS)
                 HighLimits=required,                    # Gets or sets comma seperated high limits for the measure pins.
                 IfeObject=optional,                     # Gets or sets the IFE object of type ITriggeredDcExtensions.
                 LevelsTc=required,                      # Gets or sets LevelsTc to use.
                 LowLimits=required,                     # Gets or sets comma separated low limits for the measure pins.
                 MaskPins=optional,                      # Gets or sets comma separated pins for mask.
                 MeasurementTypes=optional,              # Gets or sets comma separated measurement types (Current, Voltage) or (C, V).
                 Patlist=required,                       # Gets or sets PatList to use.
                 PcatMode=optional,                      # Gets or sets datalog level(All, FailOnly)
                 Pins=required,                          # Gets or sets comma separated pins to get DC results for.
                 PrePlist=optional,                      # Gets or sets the PrePlist callback to plist execution.
                 SamplingCount=optional,                 # Gets or sets sampling count per pin.
                 SoftwareTriggerConfiguration=optional,  # Gets or sets the configuration file for the software trigger event.
                 TimingsTc=required,                     # Gets or sets TimingsTc to use.
                 TriggerMapName=optional,                # Gets or sets comma seperated high limits for the measure pins.
                 BypassPort=optional,                    # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,           # Enable for current instance's test time and memory information
                 LogLevel=optional,                      # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,                # Enable for record detailed test time information
                 SetPointsPlistMode=optional,            # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,       # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,         # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,          # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,                # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,                   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 FivrConditionName=optional,             # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,   # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 RelayTestConditionName=optional,        # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,       # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PostPlist=optional,                     # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of TriggeredDcCtv class definition


# Beginning of TriggeredDcCtvCommonParams class definition
class TriggeredDcCtvCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 PostPlist=optional,                    # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of TriggeredDcCtvCommonParams class definition


# Beginning of ULTLoggerTC class definition
class ULTLoggerTC(BaseMethod):
    def __init__(self,
                 name,
                 DieId=required,                        # Gets or sets the DieID (for example: U1).
                 IsInlineDff=optional,                  # Gets or sets InlineDFF flag to enable or disable Inline DFF feature.
                 PrintUlt=optional,                     # Gets or sets PrintUlt flag to print ult to datalog.
                 SetUltDataPerDieId=optional,           # Gets or sets SetUltDataPerDieId flag to enable or disable DFF ult per die id.
                 ValueExpression=required,              # Gets or sets the a regular expression to match in the fuse DFF data (for example: TPREV=MTBHOP).
                 BypassPort=optional,                   # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,          # Enable for current instance's test time and memory information
                 LogLevel=optional,                     # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,               # Enable for record detailed test time information
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of ULTLoggerTC class definition


# Beginning of ULTLoggerTCCommonParams class definition
class ULTLoggerTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,                  # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,                 # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,           # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,      # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,        # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,         # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,               # A Regular Expression to minimize the patterns in the configurations.
                 FivrConditionName=optional,            # The Fivr Condition to apply.
                 FivrConditionPlistParamName=optional,  # The name of the parameter in the current instance that holds the plist name. If a FivrCondition is specified, this field must not be empty.
                 SoftwareTriggerCallBack=optional,      # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,       # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of ULTLoggerTCCommonParams class definition


# Beginning of UserCodeTC class definition
class UserCodeTC(BaseMethod):
    def __init__(self,
                 name,
                 Arguments=optional,            # Gets or sets the method arguments.
                 InputFile=required,            # Gets or sets the input file.
                 Method=required,               # Gets or sets the method name to run.
                 NamespaceClass=required,       # Gets or sets the namespace.class name where the method to run is.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of UserCodeTC class definition


# Beginning of UserCodeTCCommonParams class definition
class UserCodeTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of UserCodeTCCommonParams class definition


# Beginning of VminAggregatorTC class definition
class VminAggregatorTC(BaseMethod):
    def __init__(self,
                 name,
                 InputFile=required,            # Gets or sets the input file.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of VminAggregatorTC class definition


# Beginning of VminAggregatorTCCommonParams class definition
class VminAggregatorTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of VminAggregatorTCCommonParams class definition


# Beginning of VminForwardingBase class definition
class VminForwardingBase(BaseMethod):
    def __init__(self,
                 name,
                 AllowDownbins=optional,           # Gets or sets the flag to indicate if Flow Downbins are allowed.
                 DffMappingFile=optional,          # Gets or sets the name of the DFF-to-GSDS mapping file.
                 DffMappingOptype=optional,        # Gets or sets the location to read the DFF data from.
                 DffMappingSet=optional,           # Gets or sets the name of the Set within the DffMappingFile to use.
                 Mode=optional,                    # Gets or sets the Templates Execution mode (Either Configure or DumpTables).
                 SearchGuardbandEnable=optional,   # Gets or sets the operation mode to enable VminTC SearchGuardband mode.
                 StoreVoltages=optional,           # Gets or sets the operation mode flag OperationModeFlag.StoreVoltages.
                 StoreVoltagesDoubleTap=optional,  # Gets or sets an offset to add to stored vmin when delta is greater than the entered offset.
                 UseDffAsSource=optional,          # Gets or sets the operation mode flag OperationModeFlag.UseLimitCheckAsSource.
                 UseLimitCheck=optional,           # Gets or sets the operation mode flag OperationModeFlag.UseLimitCheck.
                 UseVoltagesSources=optional,      # Gets or sets the operation mode flag OperationModeFlag.UseVoltagesSources.
                 VminSinglePointMode=optional,     # Gets or sets the operation mode to force VminTC to only run a single test point.
                 BypassPort=optional,              # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,     # Enable for current instance's test time and memory information
                 LogLevel=optional,                # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,          # Enable for record detailed test time information
                 PreInstance=optional,             # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,            # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of VminForwardingBase class definition


# Beginning of VminForwardingBaseCommonParams class definition
class VminForwardingBaseCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of VminForwardingBaseCommonParams class definition


# Beginning of VminForwardingSaveAsUpsGsdsTC class definition
class VminForwardingSaveAsUpsGsdsTC(BaseMethod):
    def __init__(self,
                 name,
                 FastCornersGsds=optional,       # Gets or sets the name of the GSDS token to hold the full vmin results of all FAST corners.
                 FastStcGsds=optional,           # Gets or sets the name of the GSDS token to hold the full vmin results of all FAST corners (FAST_STC_V).
                 MergeWithEvgData=optional,      # Gets or sets the Mode. True means to read the EVG FAST tokens and modify them. False means to ignore any existing EVG data.
                 PassingFlowInputGsds=optional,  # Gets or sets the GSDS Token containing the current/passing flow.
                 UpsVfGsds=optional,             # Gets or sets the name of the GSDS token to hold the vmin results for the 1st tested flow.
                 UpsVfPassinFlowGsds=optional,   # Gets or sets the name of the GSDS token to hold the vmin results for the passing flow.
                 BypassPort=optional,            # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,   # Enable for current instance's test time and memory information
                 LogLevel=optional,              # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,        # Enable for record detailed test time information
                 PreInstance=optional,           # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,          # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of VminForwardingSaveAsUpsGsdsTC class definition


# Beginning of VminForwardingSaveAsUpsGsdsTCCommonParams class definition
class VminForwardingSaveAsUpsGsdsTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of VminForwardingSaveAsUpsGsdsTCCommonParams class definition


# Beginning of VminForwardingSaveFakeDataTC class definition
class VminForwardingSaveFakeDataTC(BaseMethod):
    def __init__(self,
                 name,
                 Domains=required,              # Gets or sets the List of Domains.
                 FlowDomain=optional,           # Gets or sets the Flow Domain to read the flow from.
                 FlowId=optional,               # Gets or sets the Flow ID.
                 FrequencyCorner=required,      # Gets or sets the Frequency Corner.
                 VminResults=required,          # Gets or sets the List of Vmin Results.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of VminForwardingSaveFakeDataTC class definition


# Beginning of VminForwardingSaveFakeDataTCCommonParams class definition
class VminForwardingSaveFakeDataTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of VminForwardingSaveFakeDataTCCommonParams class definition


# Beginning of VminPass2FailTC class definition
class VminPass2FailTC(BaseMethod):
    def __init__(self,
                 name,
                 CtvCapturePins=optional,           # Comma separated pins for CTV capture.
                 CtvDatalog=optional,               # Specifies when to log the CTV.
                 EndVoltage=required,               # End voltage limits.
                 FivrCondition=required,            # FivrCondtion Name to use.
                 LevelsTc=required,                 # Level test condition to load.
                 MaskPins=optional,                 # Comma separated string indicating which pins to mask.
                 Patlist=required,                  # Patlist to execute.
                 StartVoltage=required,             # Start voltage values.
                 StepSize=required,                 # Search step size in Volts.
                 TimingsTc=required,                # Timing test condition to load.
                 VminResult=optional,               # SharedStorage token name to store the Vmin result.
                 VoltageConverter=optional,         # Additional arguments for voltage converter.
                 VoltageTargets=required,           # Voltage targets.
                 BypassPort=optional,               # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,      # Enable for current instance's test time and memory information
                 LogLevel=optional,                 # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,           # Enable for record detailed test time information
                 PreInstance=optional,              # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,             # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,       # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,  # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,    # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,     # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,           # A Regular Expression to minimize the patterns in the configurations.
                 PrePlist=optional,                 # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 SoftwareTriggerCallBack=optional,  # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,   # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of VminPass2FailTC class definition


# Beginning of VminPass2FailTCCommonParams class definition
class VminPass2FailTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,              # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,             # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,       # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,  # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,    # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,     # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,           # A Regular Expression to minimize the patterns in the configurations.
                 PrePlist=optional,                 # The pre-plist callback in the format of CALLBACKNAME(ARGS).
                 PostPlist=optional,                # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 SoftwareTriggerCallBack=optional,  # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 RelayTestConditionName=optional,   # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of VminPass2FailTCCommonParams class definition


# Beginning of VminPredict class definition
class VminPredict(BaseMethod):
    def __init__(self,
                 name,
                 ClearCache=optional,           # Indicates whether the VminPrediction Cache should be cleared before executing.
                 DomainIdentifier=required,     # The domain identifier (i.e. 'IA', 'AVX2' 'AVX3', 'AMX').
                 ExecutionMode=required,        # test method's execution mode.
                 Frequency=required,            # The domain identifier (e.g. 'F3')..
                 ModelFile=required,            # The path to the model file.
                 ModelName=required,            # The name of the model.
                 MultiFlows=optional,           # Lists multiple flows (e.g. FLOW1|FLOW2|FLOW3|FLOW4) for prediction storage.
                 Offset=optional,               # An adjustment (
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of VminPredict class definition


# Beginning of VminPredictCommonParams class definition
class VminPredictCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 PreInstance=optional,   # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,  # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of VminPredictCommonParams class definition


# Beginning of VminTC class definition
class VminTC(BaseMethod):
    def __init__(self,
                 name,
                 CornerIdentifiers=optional,          # Gets or sets comma separated corner identifiers.
                 CtvPins=optional,                    # Gets or sets CTV capture pins.
                 DtsConfiguration=optional,           # Gets or sets DTS configuration name. Empty configuration name means DTS capture move is disabled.
                 FailCaptureCount=optional,           # Gets or sets FailCaptureCount. Default 1 will set stop-on-first-fail. Any value greater than 1 will run full plist unless used in combination with ReturnOn plist options.
                 FlowIndex=optional,                  # Gets or sets the current FlowIndex.
                 FlowIndexCallbackName=optional,      # Gets or sets the current FlowIndexCallbackName.
                 ForwardingMode=optional,             # Gets or sets forwarding mode.
                 InitialMaskBits=optional,            # Gets or sets forwarding mode.
                 LimitGuardband=optional,             # Gets or sets LimitGuardband to be used with VminForwarding SearchGuardbandEnabled option.
                 PinMap=optional,                     # Gets or sets recovery map name. User can enter Json stream or input file.
                 PostInstancePlist=optional,          # Gets or sets PostInstancePlist execution.
                 RecoveryMode=optional,               # Gets or sets DieRecovery update mode.
                 RecoveryOptions=optional,            # Gets or sets DieRecoveryOutgoing_ rule.
                 RecoveryTimingsTc=optional,          # Gets or sets a new timings for RecoveryTimingRetest.
                 RecoveryTrackingIncoming=optional,   # Gets or sets an recovery tracking name to be sourced.
                 RecoveryTrackingOutgoing=optional,   # Gets or sets recovery tracking name to be updated.
                 ScoreboardPerPatternFails=optional,  # Gets or sets scoreboard per pattern capture fails limit. Default is 1.
                 StartVoltagesOffset=optional,        # Gets or sets an offset to the calculated start voltage.
                 TestMode=required,                   # Gets or sets test mode.
                 TriggerLevelsCondition=optional,     # Gets or sets trigger levels test condition name.
                 TriggerMap=optional,                 # Gets or sets trigger map.
                 VminResult=optional,                 # Gets or sets vmin result. Stores value in SharedStorage using comma-separated key names with Context.DUT.
                 VoltageConverter=optional,           # Gets or sets a list of voltage overrides from VminForwarding.
                 VoltagesOffset=optional,             # Gets or sets an offset to applied voltage.
                 ApplyEndSequence=optional,           # ApplyEndSequence at the end of the test.
                 BaseNumbers=optional,                # Comma separated list of numbers  to prefix the scoreboard counters.
                 EndVoltageLimits=required,           # End voltage limits.
                 ExecutionMode=optional,              # Execution mode, default behaviour is Search without scoreboard.
                 FeatureSwitchSettings=optional,      # Feature switch settings.
                 FivrCondition=optional,              # FIVR condition name.
                 IfeObject=optional,                  # IFE object of type IVminSearchExtensions.
                 LevelsTc=required,                   # Level test condition to load.
                 MaskPins=optional,                   # Comma separated string indicating which pins to mask.
                 MaxFailsNum=optional,                # Maximum number of fails that can be processed for scoreboard counters.
                 MaxRepetitionCount=optional,         # Maximum number of times a search can be repeated for recovering purposes.
                 MultiPassMasks=optional,             # Comma separated list of mask bit strings needed for multi pass capability.
                 Patlist=required,                    # Patlist to execute.
                 PatternNameCounterIndexes=optional,  # Comma separated string of integers which map characters in the pattern name to produce a scoreboard counter.
                 PrePlist=optional,                   # PrePlist callback to plist execution.
                 PrintPatternsOccurrences=optional,   # Print failing patterns occurrences to ituff.
                 ScoreboardEdgeTicks=optional,        # Number of resolution ticks to step down when scoreboard mode is enabled.
                 StartVoltages=required,              # Start voltage values.
                 StartVoltagesForRetry=optional,      # Lower start voltages for overshoot.
                 StepSize=required,                   # Search step size in Volts.
                 TimingsTc=required,                  # Timing test condition to load.
                 VoltageTargets=required,             # Voltage targets.
                 BypassPort=optional,                 # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,        # Enable for current instance's test time and memory information
                 LogLevel=optional,                   # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,             # Enable for record detailed test time information
                 PreInstance=optional,                # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,               # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 SetPointsPlistMode=optional,         # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,    # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,      # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,       # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,             # A Regular Expression to minimize the patterns in the configurations.
                 RelayTestConditionName=optional,     # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,    # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PostPlist=optional,                  # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of VminTC class definition


# Beginning of VminTCCommonParams class definition
class VminTCCommonParams(BaseMethod):
    def __init__(self,
                 name,
                 SetPointsPlistMode=optional,       # Plist Mode Global/Local.
                 SetPointsPlistParamName=optional,  # A name of a param at current instance that hold plist name.If empty setpoints will be applied on all patterns defined in configurations.
                 SetPointsPostInstance=optional,    # A list of Group names and Set point value to apply after test execution.
                 SetPointsPreInstance=optional,     # A list of Group names and Set point value to apply before test execution.
                 SetPointsRegEx=optional,           # A Regular Expression to minimize the patterns in the configurations.
                 PreInstance=optional,              # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,             # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 RelayTestConditionName=optional,   # The RelayTestCondition to apply.
                 SoftwareTriggerCallBack=optional,  # Callback name without argument, argument is the payload of TOSTrigger instruction in pattern.
                 PostPlist=optional,                # The post-plist callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of VminTCCommonParams class definition


# Beginning of DcBinning class definition
class DcBinning(BaseMethod):
    def __init__(self,
                 name,
                 AlarmPortRedirect=optional,       # The alarm port redirect disabled or enabled.
                 ApplyEndSequence=optional,        # The ApplyEndSequence at the end of the test.
                 DatalogLevel=optional,            # Datalog level(ALL, FAIL_ONLY, COMPRESS, PINMAP_COMPRESS\").
                 EnableFlushSmartTc=optional,      # Flag to enable flushing Levels Smart TC.
                 HighLimits=optional,              # Comma separated high limits for the measure Pins.
                 IfeObject=optional,               # Gets or sets the IFE object of type IDcExtensions.
                 LevelsTc=required,                # The alarm port redirect disabled or enabled.
                 LowLimits=optional,               # Comma separated low limits for the measure Pins.
                 MeasurementTypes=optional,        # comma separated measurement type(Current, Voltage\").
                 Pins=required,                    # Comma separated Pins to get DC results for.
                 SamplingCount=optional,           # Sampling count per pin. Optional field , Required when measuring the same pin few times.
                 BypassPort=optional,              # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,     # Enable for current instance's test time and memory information
                 LogLevel=optional,                # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,          # Enable for record detailed test time information
                 PreInstance=optional,             # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,            # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 RelayTestConditionName=optional,  # The RelayTestCondition to apply.
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of DcBinning class definition


# Beginning of SclkCalcFreq class definition
class SclkCalcFreq(BaseMethod):
    def __init__(self,
                 name,
                 IfeObject=optional,            # Gets or Sets **not in use will be removed later with the refactoring of the IfeObject**.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of SclkCalcFreq class definition
class SclkGenlockParser(BaseMethod):
    def __init__(self,
                 name,
                 IfeObject=optional,            # Gets or Sets **not in use will be removed later with the refactoring of the IfeObject**.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 PreInstance=optional,          # The pre-instane callback in the format of CALLBACKNAME(ARGS).
                 PostInstance=optional,         # The post-instane callback in the format of CALLBACKNAME(ARGS).
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())


# Beginning of UpsEngineExecuteEnd class definition
class UpsEngineExecuteEnd(BaseMethod):
    def __init__(self,
                 name,
                 EXECUTION_MODE=required,       # Gets or sets the EXECUTION_MODE.
                 TIMEOUT_SEC=required,          # Gets or sets the timeout in msec. If timeout is exceeded then the Execute function returns port 0.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of UpsEngineExecuteEnd class definition


# Beginning of UpsEngineExecuteStart class definition
class UpsEngineExecuteStart(BaseMethod):
    def __init__(self,
                 name,
                 DUMMY_UNIT=required,           # Gets or sets the vid of a dummy unit to read from a csv file. Format is filename::vid.
                 EXECUTION_MODE=required,       # Gets or sets the EXECUTION_MODE.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of UpsEngineExecuteStart class definition


# Beginning of UpsEngineInitEnd class definition
class UpsEngineInitEnd(BaseMethod):
    def __init__(self,
                 name,
                 EXECUTION_MODE=required,       # Gets or sets the EXECUTION_MODE.
                 TIMEOUT_SEC=required,          # Gets or sets the timeout in msec. If timeout is exceeded then the Execute function returns port 0.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of UpsEngineInitEnd class definition


# Beginning of UpsEngineInitStart class definition
class UpsEngineInitStart(BaseMethod):
    def __init__(self,
                 name,
                 DEVICE=required,               # Gets or sets the Device - usually comes from SCVars.SC_DEVICE.
                 EXECUTION_MODE=required,       # Gets or sets the EXECUTION_MODE.
                 FILE_PATH_MAP=required,        # Gets or sets the DummyParam1 FILE_PATH_MAP.
                 FLEX_BOM=required,             # Gets or sets the DummyParam1 FLEX_BOM.
                 LOG_LEVEL=required,            # Gets or sets the LOG_LEVEL.
                 PACKAGE=required,              # Gets or sets the Package - usually comes from SCVars.SC_PACKAGE.
                 PRODUCT_LOG_PATH=required,     # Gets or sets the PRODUCT_LOG_PATH.
                 PRODUCT_PATH=required,         # Gets or sets the PATH in which the Liport xml resides.
                 REVISION=required,             # Gets or sets the Revision - usually comes from SCVars.SC_REV.
                 STEP=required,                 # Gets or sets the Step - usually comes from SCVars.SC_STEP.
                 STRUCTURE_XML_PATH=required,   # Gets or sets the STRUCTURE_XML_PATH.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of UpsEngineInitStart class definition


# Beginning of UpsEngineRunner class definition
class UpsEngineRunner(BaseMethod):
    def __init__(self,
                 name,
                 DEVICE=required,               # Gets or sets the Device - usually comes from SCVars.SC_DEVICE.
                 DUMMY_UNIT=required,           # Gets or sets the UPS_VERSION.
                 EXECUTION_MODE=required,       # Gets or sets the EXECUTION_MODE.
                 FILE_PATH_MAP=required,        # Gets or sets the DummyParam1 FILE_PATH_MAP.
                 FLEX_BOM=required,             # Gets or sets the DummyParam1 FLEX_BOM.
                 LOG_LEVEL=required,            # Gets or sets the LOG_LEVEL.
                 PACKAGE=required,              # Gets or sets the Package - usually comes from SCVars.SC_PACKAGE.
                 PRODUCT_LOG_PATH=required,     # Gets or sets the PRODUCT_LOG_PATH.
                 PRODUCT_PATH=required,         # Gets or sets the PATH in which the Liport xml resides.
                 REVISION=required,             # Gets or sets the Revision - usually comes from SCVars.SC_REV.
                 STEP=required,                 # Gets or sets the Step - usually comes from SCVars.SC_STEP.
                 STRUCTURE_XML_PATH=required,   # Gets or sets the STRUCTURE_XML_PATH.
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of UpsEngineRunner class definition


# Beginning of UpsHotDffUpload class definition
class UpsHotDffUpload(BaseMethod):
    def __init__(self,
                 name,
                 BypassPort=optional,           # Port number, provided literally to bypass execution. Use nonnegative to bypass
                 InstanceSummaryMode=optional,  # Enable for current instance's test time and memory information
                 LogLevel=optional,             # Verbosity for console printing of information from code execution
                 TelemetryLevel=optional,       # Enable for record detailed test time information
                 _comment=None,
                 _fitem=None,
                 **kwargs
                 ):
        self._init(name, locals())
# End of UpsHotDffUpload class definition

