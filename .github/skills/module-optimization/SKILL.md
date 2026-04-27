---
name: module-optimization
description: Optimize Pymtpl module code by applying refactoring patterns (UserVars, templates, loops) with validation at each step. Use when reducing redundancy and improving maintainability.
argument-hint: "Module.py"
user-invokable: true
---

# Optimize Pymtpl Module

This skill describes the workflow to optimize Pymtpl module Python code by applying refactoring patterns while ensuring the generated `.mtpl` output remains functionally equivalent.

## Workflow Overview

1. **Create optimization plan** - Document proposed changes in a markdown file
2. **Apply optimizations incrementally** - One at a time, in order
3. **Compile and compare** - Validate `.mtpl` output after each change
4. **Verify equivalence** - Ensure functionality is preserved
5. **Document changes** - Add comments explaining patterns used
6. **Report results** - Summary of optimizations applied

## When to Use

Use when reducing code duplication, standardizing parameters, or improving module maintainability after `.mtpl` to `.py` conversion.

## Code Organization

Every Pymtpl module `.py` file must be split into **three clearly labeled sections** in this order:

### Section 1 – Setup / Initialization
Contains all imports, UserVars declarations, constants, and any shared configuration objects.

```python
# =============================================================================
# SECTION 1: SETUP / INITIALIZATION
# =============================================================================
from pymtpl import Initialize, BaseMethod, Flow, Fitem, MultiTrial
from pymtpl.usrvars import UserVars

MODULE_NAME = "PTH_EXAMPLE"

usrv = UserVars()
usrv.InputFilePath = (f'GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "/Modules/{MODULE_NAME}/InputFiles/"', str)
```

### Section 2 – Test Definitions
Contains the **shared test generator function(s)** that produce test instances.  A generator function accepts the parameters that vary between SubFlows (flow name, corner, FlowMatrix, content list) and returns a list of test instances.  The loop inside the generator iterates over **test types within a SubFlow** — this is acceptable because the SubFlows themselves are never looped over.

```python
# =============================================================================
# SECTION 2: TEST DEFINITIONS
# =============================================================================

def get_vmintc(inputs):
    """Helper function to create VminTC instances based on input parameters."""
    return VminTC(inputs)

def get_screentests(inputs):
    """Helper function to create screen test instances."""
    return ScreenTC(inputs)
```

### Section 3 – Flows
Contains all SubFlow definitions.  Each SubFlow **must** be its own explicitly written block — **never iterate over SubFlows in a loop**.  Readability is the top priority.  Each block follows the same pattern:
1. Banner header
2. UPPERCASE variables for flow name, corner, FlowMatrix
3. `content_list` dictionary (test types → Bypass + IS_EDC)
4. Call the generator to build the test list
5. Create the `Flow(...)` object

```python
# =============================================================================
# SECTION 3: FLOWS
# =============================================================================

################# START MTPL FLOW DEFINITION #####################

#################################################################
#
#                       SAMPLE SUBFLOW
#
#################################################################
VAR1 = "INPUT1"         # Variables defined at the beginning
VAR2 = "INPUT2"            # Variables defined at the beginning


# USe dictionaries for the tests in the subflow to make it easy to update params.
# Common params can go into the test definition function, unique params can be set here in the content_list
Subflow_content_list = {
    "TESTA": {"Bypass": -1, "IS_EDC": False},
    "TESTB": {"Bypass": -1, "IS_EDC": False},
}

Sample_Test1   = get_vmintc(Subflow_content_list["TESTA"])
Sample_Test2   = get_screentests(Subflow_content_list["TESTB"])
Sample_Subflow = Flow("MY_MODULE_SUBFLOW", [Sample_Test1, Sample_Test2])

#################################################################
#
#                       SAMPLE2 SUBFLOW
#
#################################################################
# REPEAT SAME STRUCTURE FOR NEXT SUBFLOW
```

> Each additional SubFlow follows the **exact same structure** — copy the block, update the UPPERCASE variables and `content_list`, done.

## Prerequisites

- Module `.py` file exists and compiles successfully
- `pymtpl.py` accessible for compilation (see [pymtpl-compiler skill](../pymtpl-compiler/SKILL.md))
- `.BinLimits.json` and required files present

## CRITICAL Rules

- **Never add or remove tests** unless user explicitly asks
- **All test names, bins, counters, and flow routing must remain identical**
- Apply optimizations in strict order: Phase 1 (UserVars) then Phase 2 (DRY)
- Validate `.mtpl` output after each optimization before proceeding

## Success Criteria
- Must see NO UPDATE messages to the mtpl or the SBDef.
- Changes to pymtpl.pth is allowed.
- -i- NO UPDATE: No changes to Module_Name.mtpl
- -i- NO UPDATE: No changes to .\Module_Name_SubBinDefinitions.sbdefs

## Optimization Patterns (Apply in Order)

### Phase 1: UserVars Optimizations (Changes .mtpl output)

#### 1. Input File Path Standardization
Converts hardcoded paths to UserVar with environment variable:

**Before:**
```python
test1 = PrimeFunctionalTestMethod(
    ConfigurationFile="./Modules/PTH_DTS/InputFiles/config.txt"
)
```

**After:**
```python
usrv.InputFilePath = (f'GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "/Modules/{MODULE_NAME}/InputFiles/"', str)
InputFilePathOptions.InputFilePathFromUserVar(usrv.InputFilePath)

test1 = PrimeFunctionalTestMethod(
    ConfigurationFile=inputfile("config.txt")
)
```

#### 2. Common Test Parameters as UserVars
Extracts repeated parameters into UserVars:

**Before:**
```python
test1 = Method1(CtvCapturePins="JTAG_TDO_PAD,JTAG_TDO_DIE1")
test2 = Method2(CtvCapturePins="JTAG_TDO_PAD,JTAG_TDO_DIE1")
test3 = Method3(CtvCapturePins="JTAG_TDO_PAD,JTAG_TDO_DIE1")
```

**After:**
```python
usrv.CtvCapturePins = "JTAG_TDO_PAD,JTAG_TDO_DIE1"

test1 = Method1(CtvCapturePins=usrv.CtvCapturePins)
test2 = Method2(CtvCapturePins=usrv.CtvCapturePins)
test3 = Method3(CtvCapturePins=usrv.CtvCapturePins)
```

**Parameters NOT converted to UserVars:**
- Levels or Timings parameters (use Python variables instead)
- Fitem parameters
- Parameters used only once

### Phase 2: DRY Optimizations (No .mtpl changes)

#### 3. Looping Over Test Instances
Converts repeated patterns into loops:

**Before:**
```python
test_vdd_0p75 = VminTC(Target="VDD", TargetVoltage=0.75)
test_vdd_0p80 = VminTC(Target="VDD", TargetVoltage=0.80)
test_vdd_0p85 = VminTC(Target="VDD", TargetVoltage=0.85)
test_vdd_0p90 = VminTC(Target="VDD", TargetVoltage=0.90)
```

**After:**
```python
vdd_tests = {}
for voltage in [0.75, 0.80, 0.85, 0.90]:
    test_name = f"test_vdd_{voltage:.2f}".replace(".", "p")
    vdd_tests[test_name] = VminTC(Target="VDD", TargetVoltage=voltage)
```
#### 4. Dictionaries for Common Test Parameters
Use dictionaries to control shared test parameters (e.g., `BypassPort`, `edc`).  This makes it trivial to change the state of a test without hunting through the file.

**Why:** Avoids index-coupled arrays, keeps related data together, and allows targeted overrides.

**Before (index-coupled arrays — avoid this):**
```python
TEST_NAMES    = ["test_scan_a", "test_scan_b", "test_scan_c"]
BYPASS_VALUES = [1, -1, 1]          # fragile: order must match TEST_NAMES
EDC_VALUES    = [True, False, False]
```

**After (dictionary — preferred):**
```python
# Settings are self-documenting and order-independent
TEST_SETTINGS = {
    #  test name        bypass  edc
    "test_scan_a":  {"bypass": 1,  "edc": True},
    "test_scan_b":  {"bypass": -1, "edc": False},
    "test_scan_c":  {"bypass": 1,  "edc": False},
}

for NAME, CFG in TEST_SETTINGS.items():
    fitem = Fitem(NAME, BypassPort=CFG["bypass"], edc=CFG["edc"])
```

Use **UPPER_CASE** for all dictionary and variable names that hold configuration data.

### Recommendations
- If the file is too big like more than 400 lines of code, consider optimizing one subflow at a time instead of the whole file to reduce risk and make validation easier.
- Search for patterns of code like Flow("FLOW_NAME", Fitems) to identify all the subflows in the file.
- **Readability over brevity for SubFlows**: never collapse multiple SubFlows into a loop just to save lines.  Write each SubFlow out explicitly with a banner header so any engineer can jump straight to it.
- Use the following banner style for every SubFlow and Flow section header:
```python
#####################################################
############### SUBFLOW NAME ########################
#####################################################
```

## Validation Strategy

- **Phase 1**: Compiled `.mtpl` may differ in syntax; verify resolved values are equivalent
  - Example: `"./path/file"` → `MODULE.InputFilePath + "file"`
- **Phase 2**: Compiled `.mtpl` must be byte-for-byte identical; revert any differences

## Code Style Rules

These rules must be followed whenever writing or optimizing Pymtpl code:

| Rule | Guidance |
|------|----------|
| **UPPERCASE variables** | All configuration variables, dictionaries, and constants must use UPPER_CASE names (e.g., `TEST_SETTINGS`, `MODULE_NAME`, `INPUT_PATH`). |
| **Docstrings on every function** | Every `def` must have a concise triple-quoted docstring immediately after the signature.  One to three lines is enough — describe what the SubFlow does and any key constraints.  Do **not** write long paragraphs; keep docstrings short so they are actually read. |
| **No functions inside functions** | Do not call a helper function from inside another function that builds test instances.  Evaluate all values before passing them to the constructor. |
| **No nested loops** | Refactor nested loops into a single loop over a flat dictionary or list of tuples.  Nested loops hurt readability and make parameter changes error-prone. |
| **Never loop over SubFlows** | Each SubFlow must be written out as its own explicit block of code.  **Never** generate SubFlow code inside a loop.  Readability is more important than brevity here. |
| **No index-coupled arrays** | Never maintain two or more parallel lists whose items are linked by index position.  Use a dictionary or list of tuples instead. |
| **Comment generously** | Add section headers (`# ---`), inline comments, and docstrings.  Aim for at least one comment per logical block. |
| **Set default parameters** | Define default values once (via `partial` / template or a shared dictionary) and only override what differs per test. |
| **Descriptive names** | Prefer explicit names (`SCAN_NOM_BYPASS`) over terse abbreviations.  You are compressing thousands of MTPL lines into hundreds of Python lines — use the space. |

## Related Documentation

- [pymtpl-compiler skill](../pymtpl-compiler/SKILL.md) - Compilation workflow
