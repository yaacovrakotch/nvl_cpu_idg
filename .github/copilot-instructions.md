# NVL CPU Test Program Repository

## Overview

This is an Intel semiconductor ATE (Automated Test Equipment) test program repository for Silicon testing. The repository contains test programs written in **OTPL (OpenStart Test Programming Language)**, which is used to generate test programs that run on Intel proprietary HDMX semiconductor testers.

## Nova Lake Repository Structure

The Nova Lake (NVL) test program is split across **5 separate repositories**, one for each dielet and a shared common repo:

| Repository | Description |
|------------|-------------|
| `nvl.cpu`    | CPU dielet test program |
| `nvl.gcd`    | GCD dielet test program |
| `nvl.hub`    | HUB dielet test program |
| `nvl.pcd`    | PCD dielet test program |
| `nvl.common` | Shared common content used by all dielets |

The **`nvl.common`** repository is included as a **Git submodule** in each of the four dielet repos (`nvl.cpu`, `nvl.gcd`, `nvl.hub`, `nvl.pcd`). It contains shared modules, base inputs, and configuration that are reused across all dielets. Changes intended for all dielets should be made in `nvl.common`, while dielet-specific changes belong in the respective dielet repo.

## About OTPL and Pymtpl

**OTPL** is a flat, declarative test programming language that lacks the expressive features of modern programming languages. To address this limitation, we use **Pymtpl** - a Python-based Domain-Specific Language (DSL) that generates OTPL/MTPL code.

**Pymtpl** allows us to:
- Write test programs using Python's programming constructs (loops, functions, conditionals)
- Generate complex OTPL test flows programmatically
- Maintain code readability and reusability
- Follow software engineering best practices (PEP8, DRY principles)

## Working with Pymtpl

For detailed information about the Pymtpl framework, classes, methods, and best practices, please refer to:
- **[Pymtpl Instructions](instructions/pymtpl.instructions.md)** - Comprehensive Pymtpl framework documentation

The Pymtpl instructions apply specifically to Python files in the `Modules/` directory and contain:
- Pymtpl class definitions (Initialize, BaseMethod, MultiTrial, Fitem, Flow, BasePort)
- Code generation guidelines
- Design patterns and best practices
- Complete examples

## Working with Program Flows

For modifying or creating Pymtpl files in the **ProgramFlowsTestPlan** directories (located in `POR_TP/*/ProgramFlowsTestPlan/`), please refer to:
- **[Program Flows Instructions](instructions/programflows.instructions.md)** - Specialized guidance for program flows

The Program Flows instructions provide:
- Specific patterns and conventions for ProgramFlowsTestPlan Pymtpl files
- Flow structure and organization guidelines
- Integration with test plan configurations
- Examples specific to program flow implementations

**Important**: Do not use general Pymtpl guidelines for ProgramFlowsTestPlan files. Always consult the programflows.instructions.md file for these specific files.

## Test Execution Concepts

### Bypassing Tests
Bypassing a test means that during ATE (Automated Test Equipment) testing, the test is not executed. This is a common practice for disabling tests without removing them from the test flow.
- **BypassPort = 1**: Test is bypassed (disabled, will not execute)
- **BypassPort = -1**: Test is enabled (not bypassed, will execute normally)

### EDC - Engineering Data Collection
EDC stands for Engineering Data Collection. When a test is in EDC mode, if the test fails, no bin is assigned. This means the failure is recorded for engineering analysis purposes only, and does not result in the device being binned as a failure.
- **edc = True**: Test is in EDC mode. Failures will not assign bins, only collect engineering data.
- **edc = False**: Test is in kill mode (normal mode). Failures will assign bins as configured.

Users may refer to:
- **"Move a test to kill"**: This means setting `edc = False` (normal failure binning)
- **"Move a test to EDC"**: This means setting `edc = True` (engineering data collection only)

## Binning Methodology Migration

If the user asks for help with migrating to the new binning methodology (also referred to as "class binning", "HBSBXXXX binning", or "sort-like binning at class"), please refer to:
- **[HBSBXXXX_AI_Agent.instructions.md](instructions/HBSBXXXX_AI_Agent.instructions.md)** - Comprehensive migration guide for the new binning methodology

This file contains detailed instructions and best practices for transitioning from the legacy binning approach to the new HBSBXXXX binning methodology.

## Code Review Guidelines

When reviewing code changes in this repository, follow these special instructions:

### ProgramFlowsTestPlan Folder Changes

**CRITICAL**: When changes are detected in files within `ProgramFlowsTestPlan` folders:

1. **Check for direct mtpl edits**: If `.mtpl` files have been modified, verify that the corresponding `.py` (Pymtpl) files in the same folder were also edited.

2. **Flag violations**: Leave a comment if:
   - `.mtpl` files were changed directly, BUT
   - The corresponding Pymtpl `.py` file was NOT modified
   
3. **Why this matters**: 
   - `.mtpl` files are **generated** from Pymtpl `.py` files
   - Direct edits to `.mtpl` files will be **overwritten** when the Pymtpl code is regenerated
   - All changes must be made in the source Pymtpl `.py` files to persist

4. **Expected pattern**:
   - ✅ CORRECT: Both `module_name.py` and generated `module_name.mtpl` are modified
   - ❌ INCORRECT: Only `module_name.mtpl` is modified (direct edit without updating source)

**Example review comment for violations**:
```
⚠️ Warning: `.mtpl` file was edited directly without modifying the corresponding Pymtpl `.py` file. 
These changes will be lost when the Pymtpl code is regenerated. 
Please make changes in the `.py` file instead and regenerate the `.mtpl` file.
```
## Pull Request Guidelines

### PR Description Template

All pull requests must include the following required information:

#### Basic Information
- **Why is this PR needed?** - Concise summary of the motivation. Agent to make a best guess to fill this in based on the PR description, but the user must review and edit as needed.
- **What type of PR is this?** - New feature (planned/unplanned), sighting response, fix, or other
- **Source of the PR change** - Planned item, sighting, QE event, feedback, or other

#### Impact Assessment
- **Common PR/Die affected** - Which die is affected (CPU, GCD, HUB, PCD)
- **Bins affected** - Specific bins or many bins
- **Socket(s) affected** - HOT, COLD, PHM, or other
- **Package(s) affected** - Which Novalake packages are impacted

#### Validation Requirements
- **Validation performed** - Type of validation (load/init, standing die, VPO, MBOT)
- **Validation temperature** - Temperature conditions used for validation
- **Other details** - Any additional context or special considerations (optional)

**CRITICAL**: All sections must be completed. Use checkboxes with 'X' (no spaces) to indicate selections.

For the complete template, see `.github/pull_request_template.md`.



### Module File Types

Each module in `repo_root/Modules/<MODULE_NAME>/` may contain:

- **`.py`** - Pymtpl Python source file (if present, this is the source of truth) - **Excludes `qs.py` files**
- **`qs.py`** - QuickSim configuration file (ignore for Pymtpl editing purposes)
- **`.mtpl`** - Generated test plan file (generated from `.py` or manually maintained)
- **`.sbdefs`** - Bin definitions file (generated from `.py` or manually maintained)
- **`.flw`** - Flow file (generated from `.py` or manually maintained)
- **`.mconfig`** - Pattern patch configuration (see mconfig instructions)

## Automation Integration

The `build_modules.ps1` script is intended to be integrated into a larger automated workflow. Ensure that this script is designed to work seamlessly within the overall automation framework, facilitating efficient module building and deployment processes.
