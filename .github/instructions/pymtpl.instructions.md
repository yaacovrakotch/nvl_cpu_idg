---
applyTo: "**/Modules/**/*.py"
---

# Pymtpl Framework Instructions

## Overview

Pymtpl is a Python-based DSL (Domain-Specific Language) that generates OTPL/MTPL code for Intel semiconductor test programs. This guide provides comprehensive framework documentation for working with Pymtpl code.

## Code Generation Guidelines

- NEVER delete tests from user input unless explicitly requested
- Only modify what the user specifically asks to change
- Follow PEP8 conventions and prioritize code readability
- Generate complete, working code without placeholders
- When asked questions about Pymtpl files, evaluate the entire file (expand loops, conditionals) before answering

## Pymtpl File Structure

A typical Pymtpl file has three sections:
1. **Imports and Initialization** - Import classes, define Initialize calls, set variables
2. **Test Definitions** - Define test methods and helper functions
3. **Flow Definitions** - Define test flows and subflows

## `Initialize` Class

Sets up configuration at the start of a Pymtpl script. Initializes output paths, binning strategies, and other global settings.

### Common Parameters:

- **outfile** (str): Path to output mtpl file without .mtpl extension
- **module_name** (str): Module name
- **binrange** (list): Range of bins - `[]` or `[(start, end), ...]`
- **basenumrange** (list): Range of base numbers - `[]` or `[(start, end)]`
- **tosversion** (str): TOS version - `'tos3'` or `'tos4'` (default: `'tos3'`)
- **defaultrm1bin** (str): Default softwarebin in format `-HB`
- **defaultrm2bin** (str): Default clampbin in format `-HB`

### Additional Parameters:
- **nonmttbinstrategy**, **mttbinstrategy**: Binning classes for non-MTT/MTT tests
- **nonmttctrstrategy**, **mttctrstrategy**: Counter classes for non-MTT/MTT tests
- **basenumberstrategy**: Strategy for base numbers
- **paramorder**: Order of test method output parameters
- **defaultthermalbin**, **defaultresetbin**: Default bins in format `90HBSBXX`
- **edcportctrbinrange**: Bin range for EDC/pass port counters
- **forceflwfilegen** (bool): Force flow file generation (default: `False`)

### Partial Functions

- **InitializeMTL**: Uses `MTLdefault` for default values
- **InitializeNVLClass**: Uses NVL class strategies (`NVLClass8dig`, `MTTNVLClass8dig`, etc.), `tosversion="tos4"`
- **InitializeNVLSort**: Uses NVL sort strategies (`Sort8dig`, `CtrSort8dig`), `tosversion="tos4"`

### Special Values

- **AUTO**: Used in BasePort `setbin` parameter. Equals `-1` and tells Pymtpl to auto-assign bins.

```python
from pymtpl.core import AUTO
Fitem("SAME", r0=pFail(setbin=AUTO, goto="NEXT"), r1=pPass(goto="NEXT"))
```

## `BaseMethod` Class

Parent class for test methods (also called test instances or test templates). Provides structure for defining and managing test methods with unique names and initialized parameters.

### Key Attributes:
- **names**: Dictionary tracking all registered test names to ensure uniqueness

### Parameters:
- **name**: The name of the test instance
- **vars_dictionary**: Dictionary containing test parameters and values (mostly strings; exceptions like `BypassPort` which is int)
  - `BypassPort = 1`: Test is bypassed (disabled)
  - `BypassPort = -1`: Test is enabled (will execute)
- **_fitem**: Optional Fitem object defining flow routing

### Parameter Formats:
- **String**: Regular string value (output enclosed in quotes)
- **Spec**: Direct output without quotes
  - Input: `param = Spec('value')` → Output: `param = value;`
- **TrialParamSpec**: For SpeedFlow expansion support
  - Input: `param = TrialParamSpec('val')` → Output: `TrialParam param = val;`

## `MultiTrial` Class

Manages configuration and execution of MTT (MultiTrial) tests for speed flow testing. Has its own name and baseports.

### Parameters:
- **name**: The name of the test
- **template**: Template object (must be a `BaseMethod` instance)
- **trialvar**: Trial variable (default: `'IP_CPU_BASE::FlowDomain.Default'`)
- **exitaction**: Action on exit (default: `'Continue'`)
- **edcexitaction**: Action on EDC exit (default: `'Restore'`)
- **_comment**: Optional comment
- **_fitem**: Optional Fitem
- **r0, r1, r2, r3, r4, r5, rm1, rm2**: Return values (MTT-specific ports)

### Example

Regular non-MTT test:
```python
SCLRF1_TEST_1 = VminTC(name="TEST_1", BypassPort=-1, TestMode="MultiVmin", 
                       _fitem=Fitem("SAME", r0=pFail(setbin=4500, ret=0)))
```

Same test as MTT:
```python
SCLRF1_TEST_1 = MultiTrial(
    name="MTTtname", 
    trialvar="trialvar_value",
    template=VminTC(name="TEST_1", BypassPort=-1, TestMode="MultiVmin", 
                    _fitem=Fitem("SAME", r0=pFail(setbin=4500, ret=0))),
    r0=pFail(setbin=4500, ret=0, trialaction="Exit"),
    r2=pFail(setbin=4500, ret=2, trialaction="Exit")
)
```

**NativeMultiTrial**: Subclass for native MTT tests specific to TOS4.

## `Fitem` Class

Represents a FlowItem object that defines and manages flow items in a test flow. Handles BasePorts and EDC settings.

### Parameters:
- **name**: Flow item name (default: `'SAME'`)
- **ti**: Associated `Flow` or `BaseMethod` object (optional, can be set later)
- **edc**: Enable EDC mode (default: `False`)
- **r0, r1, r2, r3, r4, r5, rm1, rm2**: BasePorts (additional ports like r6, r7 supported via kwargs)

### Usage Examples

**Combined with BaseMethod:**
```python
SCLRF1_TEST_1 = VminTC(name="TEST_1", BypassPort=-1, TestMode="MultiVmin", 
                       _fitem=Fitem("SAME", edc=False, r0=pFail(setbin=4500, ret=0)))
```

**Defined separately:**
```python
SCLRF1_TEST_1 = VminTC(name="TEST_1", BypassPort=-1, TestMode="MultiVmin")
SCLRF1_TEST_1_Fitem = Fitem("SAME", SCLRF1_TEST_1, edc=False, r0=pFail(setbin=4500, ret=0))
```

## Bypassing a Test

### Overview
Bypassing a test means that during ATE (Automated Test Equipment) testing, the test is not executed. This is a common practice for disabling tests without removing them from the test flow.

### Implementation
- **BypassPort = 1**: Test is bypassed (disabled, will not execute)
- **BypassPort = -1**: Test is enabled (not bypassed, will execute normally)

### Example
```python
# Bypassed test - will not execute on ATE
BYPASSED_TEST = VminTC(name="TEST_DISABLED", BypassPort=1, TestMode="MultiVmin")

# Enabled test - will execute on ATE
ENABLED_TEST = VminTC(name="TEST_ENABLED", BypassPort=-1, TestMode="MultiVmin")
```

## EDC - Engineering Data Collection

### Overview
EDC stands for Engineering Data Collection. When a test is in EDC mode, if the test fails, no bin is assigned. This means the failure is recorded for engineering analysis purposes only, and does not result in the device being binned as a failure.

### Implementation
- **edc = True**: Test is in EDC mode. Failures will not assign bins, only collect engineering data.
- **edc = False**: Test is in kill mode (normal mode). Failures will assign bins as configured.

### Terminology
Users may refer to:
- **"Move a test to kill"**: This means setting `edc = False` in the Fitem
- **"Move a test to EDC"**: This means setting `edc = True` in the Fitem

### Example
```python
# Test in EDC mode - failures collect data but don't bin the part
EDC_TEST = VminTC(
    name="TEST_EDC",
    BypassPort=-1,
    TestMode="MultiVmin",
    _fitem=Fitem("SAME", edc=True, r0=pFail(goto="NEXT"), r1=pPass(goto="NEXT"))
)

# Test in kill mode - failures will bin the part
KILL_TEST = VminTC(
    name="TEST_KILL",
    BypassPort=-1,
    TestMode="MultiVmin",
    _fitem=Fitem("SAME", edc=False, r0=pFail(setbin=4500, ret=0), r1=pPass(goto="NEXT"))
)
```

## Ports Classes - `BasePort` Class

Ports define exit routes of a test method and specify which test executes next when exiting through a particular port.

- **pFail**: Fail ports (test execution failed)
- **pPass**: Pass ports (test execution passed)

### Parameters:
- **ctr**: Counter for the port (default: `None`; `ctr=0` skips counter assignment)
- **setbin**: Bin value (4-digit or 8-digit; negative value = auto-assign)
- **ret**: Return value of the port
- **goto**: Name of the test to route to (use `goto="NEXT"` to route to next Fitem in Flow)
- **trialaction**: Trial action (used in MultiTrial tests)

**Note**: Cannot use both `ret` and `goto` on the same port - a port has only one action.

### Examples

**Combined Fitem and BaseMethod:**
```python
TEST_1 = VminTC(name="TEST_1", BypassPort=-1, TestMode="MultiVmin", 
                _fitem=Fitem("SAME", edc=False, r0=pFail(setbin=4500, ret=0)))
```

**Separate Fitem routing to another test:**
```python
TEST_1 = VminTC(name="TEST_1", BypassPort=-1, TestMode="MultiVmin")
TEST_2 = VminTC(name="TEST_2", BypassPort=-1, TestMode="MultiVmin")
TEST_1_Fitem = Fitem("SAME", TEST_1, edc=False, r0=pFail(setbin=4500, goto=TEST_2.name))
```

**MultiTrial ports (must match Fitem port count):**
```python
MultiTrial(name="MTTName", 
           exitaction="Continue",
           trialvar="something",
           template=VminTC(name='Template_Name', BypassPort=-1),
           r0=pFail(setbin=AUTO, ret=0, trialaction="Next"),
           r1=pPass(setbin=AUTO, ret=1, trialaction="Exit"),
           _fitem=Fitem('SAME', edc=False,
                        r0=pFail(setbin=AUTO, ret=0),
                        r1=pPass(setbin=AUTO, goto='NEXT')))
```

## `Flow` Class

Represents a flow object (also called SubFlow). Required for a flow to appear in final mtpl output. Manages a list of flow items (Fitem objects) processed in order.

### Parameters:
- **name**: The name of the flow
- **fitem_list**: List of `Fitem` or `BaseMethod` objects
- **_orig_name**: Original name (used with `duplicate_flow_obj`, default: `None`)

### Flow Types

**Regular Flow:**
```python
SCLRF1_TEST_1 = VminTC(name="TEST_1", BypassPort=-1, TestMode="MultiVmin", 
                       _fitem=Fitem("SAME", r0=pFail(setbin=4500, ret=0)))
SCLRF1_Flow = Flow("SCLRF1", SCLRF1_TEST_1)
```

**Composite Flow (Flow inside Flow):**
```python
SCLRF1_TEST_1 = VminTC(name="TEST_1", BypassPort=-1, TestMode="MultiVmin", 
                       _fitem=Fitem("SAME", r0=pFail(setbin=4500, ret=0)))
Composite_Flow = Flow("SCLRF1", SCLRF1_TEST_1)
SCLRF1_Flow = Flow('SCLRF1', Fitem("SAME", Composite_Flow, 
                                    r0=pFail(ret=0), r2=pFail(ret=2), r1=pPass(ret=1)))
```

**Note**: Avoid nesting more than 2 levels of flows for readability.

### Test Routing

Routing uses `goto` or `ret`:
- **ret**: Return value - exits through a port
- **goto**: Routes to another test by name

**Example:**
```python
sample_test = VminTC(
    name="SBFT_CCF_FUNC_K_ENDCPU_X_VCCR_F1_X",
    EndVoltageLimits="0.9",
    _fitem=Fitem('SAME', r0=pFail(setbin=4500, goto="SBFT_CCF_FUNC_K_ENDCPU_X_VCCR_F1_X_3"))
)
sample_test_2 = VminTC(
    name="SBFT_CCF_FUNC_K_ENDCPU_X_VCCR_F1_X_2",
    EndVoltageLimits="0.9",
    _fitem=Fitem('SAME', r0=pFail(setbin=4501, ret=0))
)
sample_test_3 = VminTC(
    name="SBFT_CCF_FUNC_K_ENDCPU_X_VCCR_F1_X_3",
    EndVoltageLimits="0.9",
    _fitem=Fitem('SAME', r0=pFail(setbin=4501, ret=2))
)
SCLRF1_Subflow = Flow('SCLRF1', sample_test, sample_test_2, sample_test_3)
```

## Pymtpl Code Design Guidelines

Code readability is the defining factor for Pymtpl code design. Follow these rules:

### File Structure

1. **Split file into 3 sections:**
   - Setup/Initialization (Initialize call, imports, variables)
   - Test Definition (test methods and functions)
   - Flow Definition (all flows)

2. **Define each subflow as its own section** - Users should be able to edit each subflow independently

**Avoid:**
```python
subflows = ["CCRF4", "MAXCRF6"]
for subflow in subflows:
    # do something
```

**Prefer:**
```python
#################################################################
#                       CCRF4 SUBFLOW                        
#################################################################
CCR_F4_Flow = "CCRF4"
F4_Corner = "F4"
F4_FlowMatrix = "CR_F4_FREQ"
F4_content_list = {"MLC_DRG": -1, "SLC_DRG": -1, "MLC": -1, "SLC": -1}

CCRF4_Tests = get_test_list(CCR_F4_Flow, F4_Corner, F4_FlowMatrix, F4_content_list)
CCRF4_Subflow = Flow("FUN_CORE_C68_CCRF4", CCRF4_Tests)

#################################################################
#                       MAXCRF6 SUBFLOW                        
#################################################################
MAXCR_F6_Flow = "MAXCR"
F6_Corner = "F6"
F6_FlowMatrix = "CR_F6_FREQ"
F6_content_list = {"MLC_DRG": -1, "SLC_DRG": -1, "MLC": -1, "SLC": 1}

MAXCRF6_Tests = get_test_list(MAXCR_F6_Flow, F6_Corner, F6_FlowMatrix, F6_content_list)
MAXCRF6_Subflow = Flow("FUN_CORE_C68_MAXCR", MAXCRF6_Tests)
```

### Best Practices

3. Use **dictionaries** to control test params (BypassPort, EDC flag, etc.)
4. Use **UPPER_CASE** for variables
5. **Avoid nested loops** - reduces readability
6. **Don't call functions inside functions** - reduces readability and flexibility
7. Add **docstrings** to each function
8. Add **comments** wherever needed

### Example of a Pymtpl File That Follows All the Rules Above:

```python
# Import the necessary classes from Pymtpl
from pymtpl.por_methods import VminTC, AuxiliaryTC, PrimeScanHRYSSNTestMethod, PrimeScanHRYTestMethod, RunCallback, PrimeScanSPOFITestMethod, ScreenTC
from pymtpl.core import Flow, Fitem, pPass, pFail, AUTO, InitializeNVLSort, Import, Spec

CH_ATOM_BR = (4175, 4199)
SA_ATOM_BR = (4275, 4299)
AS_ATOM_BR = (4775, 4799)

# Initialize the module by defining the output mtpl path and the module name
InitializeNVLSort('EXAMPLE_MTPL', 'EXAMPLE_MODULE', binrange = [CH_ATOM_BR, SA_ATOM_BR, AS_ATOM_BR], basenumrange = (3451,3499), defaultrm1bin = -42, defaultrm2bin = -42)

# Add the necessary files to import in your mtpl
Import("SCN_ATOM_C68.usrv")
Import("AuxiliaryTC.xml")
Import("ScreenTC.xml")
Import("VminTC.xml")

# Define any globally used variables
ATOM_timings = "SCN_ATOM_C68::cpu_ssn_timing_PARAMS_tclk100_sclk400_cclk400_ATOM_PO_timing_adjust"
EXVF_LVL = "BASE::bf_exvf_lvl_nom_lvl"
NOM_LVL = "BASE::bf_lvl_nom_lvl"

def get_screentc(testinput, flow, reset_flavor=None):
    """Generate ScreenTC test instances based on test input configuration."""
    test_output = ""
    for testtype, test_info in testinput.items():
        scantype = testtype.split('_')[0]
        test_output = ScreenTC(
            name=f"CTRL_ATOM_SCREEN_E_{flow}_X_X_X_X{test_info.get('extra', '')}",
            BypassPort=test_info.get("BypassPort", ""),
            ScreenTestSet=test_info.get("ScreenTestSet", ""),
            ScreenTestsFile=test_info.get("ScreenTestsFile", "")
        )
    return test_output

def get_auxtc(testinput, flow, reset_flavor=None):
    """Generate AuxiliaryTC test instances based on test input configuration."""
    test_output = ""
    for testtype, test_info in testinput.items():
        scantype = testtype.split('_')[0]
        modtype = testtype.split('_')[1]
        test_output = AuxiliaryTC(
            name=f"{scantype}_{modtype}_AUX_E_{flow}_X_X_X_X{test_info.get('extra', '')}",
            BypassPort=test_info.get("BypassPort", ""),
            Expression=test_info.get("Expression", ""),
            ResultToken=test_info.get("ResultToken", ""),
            DataType=test_info.get("DataType", ""),
            Storage=test_info.get("Storage", ""),
            ResultPort=test_info.get("ResultPort", ""),
            PreInstance=test_info.get("PreInstance", "")
        )
    return test_output

#################################################################################
#             BEGIN FLOW
#
# - BEGIN flow will test 80% STUCKAT content 
# - Fail flow will include CHAIN, SPOFI, and HRY tests 
#
#################################################################################

############################## SCREEN TESTS #####################################

BEGIN_FLOW = "BEGIN"

BEGIN_VAR_INIT = {"VAR_INIT": {"BypassPort": -1, "ScreenTestSet": "VAR_INIT", "ScreenTestsFile": "./Modules/SCN_ATOM_C68/InputFiles/scn_atom_screentest.txt", "extra": "_VAR_INIT"}}
BEGIN_VAR_INIT_TEST = get_screentc(BEGIN_VAR_INIT, BEGIN_FLOW)

BEGIN_VMIN_INIT = {"VMIN_INIT": {"BypassPort": -1, "ScreenTestSet": "VMIN_INIT", "ScreenTestsFile": "./Modules/SCN_ATOM_C68/InputFiles/scn_atom_DFFset.txt", "extra": "_VMIN_INIT"}}
BEGIN_VMIN_INIT_TEST = get_screentc(BEGIN_VMIN_INIT, BEGIN_FLOW)

BEGIN_AUX_PREAMBLE = {"BEGIN_CTRL_X": {"extra": "_PREAMBLE", "BypassPort": -1, "DataType": "String", "Expression": "0", "ResultPort":"[R]=='1'?1:1"}}
BEGIN_AUX_PREAMBLE_TEST = get_auxtc(BEGIN_AUX_PREAMBLE, BEGIN_FLOW)

########################### BEGIN DUT FLOW ######################################

BEGIN_SUBFLOW = Flow("SCN_ATOM_C68_BEGIN", 
    Fitem("SAME", BEGIN_VAR_INIT_TEST,
        r1=pPass(goto= BEGIN_VMIN_INIT_TEST.name), 
        r0=pFail(ret=1),
        r2=pFail(ret=1)), 
    Fitem("SAME", BEGIN_VMIN_INIT_TEST,
        r1=pPass(goto="NEXT"),
        r0=pFail(ret=1),
        r2=pFail(ret=1)),
    Fitem("SAME", BEGIN_AUX_PREAMBLE_TEST, 
        r1=pPass(ret=1),
        r0=pFail(ret=1))
)
```

That should give you a good understanding of what Pymtpl is.

```
