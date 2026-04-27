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

## Prerequisites

- Module `.py` file exists and compiles successfully
- `pymtpl.py` accessible for compilation (see [pymtpl-compiler skill](../pymtpl-compiler/SKILL.md))
- `.BinLimits.json` and required files present

## CRITICAL Rules

- **Never add or remove tests** unless user explicitly asks
- **All test names, bins, counters, and flow routing must remain identical**
- Apply optimizations in strict order: Phase 1 (UserVars) then Phase 2 (DRY)
- Validate `.mtpl` output after each optimization before proceeding

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

#### 3. Test Instance Templates
Creates reusable templates with default parameters:

**Before:**
```python
test1 = PrimeFunctionalTestMethod(
    Patlist="test1.plist",
    LevelsTc="nom_lvl",
    TimingsTc="nom_tim",
    PrePlist="init.plist"
)
test2 = PrimeFunctionalTestMethod(
    Patlist="test2.plist",
    LevelsTc="nom_lvl",
    TimingsTc="nom_tim",
    PrePlist="init.plist"
)
```

**After:**
```python
from functools import partial
from pymtpl.helpers import create_test_instance_with_defaults

MyFuncTest = partial(
    create_test_instance_with_defaults,
    testmethod=PrimeFunctionalTestMethod,
    defaults={
        'LevelsTc': 'nom_lvl',
        'TimingsTc': 'nom_tim',
        'PrePlist': 'init.plist',
    }
)

test1 = MyFuncTest(Patlist="test1.plist")
test2 = MyFuncTest(Patlist="test2.plist")
```

#### 4. Looping Over Test Instances
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

## Validation Strategy

- **Phase 1**: Compiled `.mtpl` may differ in syntax; verify resolved values are equivalent
  - Example: `"./path/file"` → `MODULE.InputFilePath + "file"`
- **Phase 2**: Compiled `.mtpl` must be byte-for-byte identical; revert any differences

## Best Practices

1. Use meaningful variable names
2. Add comments explaining optimization patterns
3. Validate compilation and `.mtpl` equivalence after each change
4. Apply Phase 1 (UserVars) before Phase 2 (DRY)
5. Review and version control optimized modules

## Related Documentation

- [09-uservars.instructions.md](../../instructions/pymtpl/09-uservars.instructions.md) - UserVars usage
- [pymtpl-compiler skill](../pymtpl-compiler/SKILL.md) - Compilation workflow
- [02-initialize-config.instructions.md](../../instructions/pymtpl/02-initialize-config.instructions.md) - Initialize class configuration
