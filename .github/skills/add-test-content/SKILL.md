---
name: add-test-content
description: Add test content to an existing Pymtpl module. Use when populating a module with test methods and configuration values.
argument-hint: "ModuleName TestContent"
user-invokable: true
---

# Add Test Content

This skill provides guidance on how to add test content to an existing Pymtpl module. This includes defining flows and composites, creating test instances with the correct parameters, and ensuring the module compiles correctly.

## What this skill covers
- Defining flows and composites based on test requirements
- Creating test instances with correct parameters and naming conventions
- Compiling the module to validate the .py file and generate .mtpl, .sbdefs, and .flw files
- Validating bin names with the `bin-name-override` skill

## When to use this skill
Use this skill when you have an existing Pymtpl module with a .py file and you need to populate it with test methods, flows, and configuration values based on user input.

## Prerequisites
- Existing Pymtpl module with a .py file (created using the `module-creation` skill or manually)
- Test requirements and content provided by the user

## Critical Rules
1. Do not optimize the .py file unless the user requests it. The priority is to create a correct module.

## Workflow
Follow each of these steps in order and complete each step before moving to the next one. Do not skip steps or perform them out of order.
1. Verify that the module pymtpl file has been created at `Modules/<MODULE_NAME>/<MODULE_NAME>.py` and open it.
2. Define flows and composites based on the test requirements for the module, following the patterns in `06-flows-composites.instructions.md`
3. Create test instances: See "Creating the test instances" section below
4. Convert the module from .py to .mtpl using [pymtpl-compiler skill](../pymtpl-compiler/SKILL.md) to validate the .py file is correct and generates the expected output files (.mtpl, .sbdefs, .flw)
5. Run the [`bin-name-override`](../bin-name-override/SKILL.md) skill after the converting to mtpl, to ensure bin names are correct and match BinDefinitions.bdefs.

## Creating the test instances
1. ⚠️ CRITICAL Reference `10-por-methods-reference.instructions.md` for how to locate and read por_methods.py to find the correct test method and expected parameters for each test instance
2. Always define all required test parameters for a test method, even if the user doesn't specify them.
3. Follow the coding guidelines in `07-coding-guidelines.instructions.md` for how to structure the test instances and flows
4. Follow the naming conventions in `12-naming-convention.instructions.md` for naming the test instances 
5. For unspecified bins, reference `TOS/HardBins.instructions.md` to determine the correct hardbin based on the test type
6. Reference the inputfile uservar in the test instances for any input/config file paths:
```python
test1 = SomeTestMethod(
    # ...
    ConfigurationFile=inputfile("my_input_file.txt")
)
```