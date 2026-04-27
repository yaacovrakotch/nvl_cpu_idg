---
name: pymtpl-compiler
description: Compile Pymtpl Python modules (.py) to generate test plan files (.mtpl, .sbdefs, .flw). Use when compiling modules, regenerating test files after edits, or validating module compilation. Handles path detection and GitHub runner compatibility.
argument-hint: "ModuleName"
user-invokable: true
---

# Compile Pymtpl Module

This skill provides guidance on compiling Pymtpl Python modules using the existing `pymtpl.py` script to generate test plan files (.mtpl, .sbdefs, .flw).

## What This Skill Does

This skill helps you:

1. **Locate pymtpl.py** - Find the script in the repository (typically `<repo_root>/Shared/BaseInputs/pytpd/main/pymtpl.py`)
2. **Navigate correctly** - Change to the module directory before running
3. **Use correct paths** - Provide relative paths to EnvironmentFile.env and BinDefinitions.bdefs
4. **Handle platforms** - Know when to use `-skip_path_updater` flag (GitHub runners)
5. **Validate output** - Check generated files (.mtpl, .sbdefs, .flw)
6. **Run bin validation** - Optionally execute bin-name-override after compilation

## When to Use This Skill

Use this skill when:
- Compiling a Pymtpl module after editing the .py file
- Regenerating .mtpl, .sbdefs, .flw files
- Validating module compilation before commit
- Running compilation in CI/CD pipelines
- Troubleshooting compilation errors

## Prerequisites

- Module `.py` file exists in `Modules/<MODULE_NAME>/`
- Ensure you clone the repo using git submodule update --init --recursive - This will ensure the pytpd library is also cloned.
- `pymtpl.py` script exists (typically `Shared/BaseInputs/pytpd/main/pymtpl.py`)
- Environment file exists (typically `POR_TP/Class_NVL_S28C/EnvironmentFile.env` - **filename may vary by repository**)


⚠️ **Note**: The exact filenames for the environment may differ between repositories. Use the search commands below to locate them. Use grep to find the files. If you find multiple .env files, use from Class_NVL_S28C or the one that is most relevant to your module.


## Usage

### Quick Start - Local Machine

```powershell
# Navigate to the module directory
cd Modules\PTH_DTS

# Run pymtpl.py with relative paths
# Note: Adjust .env and .bdefs filenames if they differ in your repository
python <repo_root>\Shared\BaseInputs\pytpd\main\pymtpl.py "moduleName.py" -env <repo_root>\POR_TP\Class_NVL_S28C\EnvironmentFile.env
```

### GitHub Runner / CI Pipeline

⚠️ **CRITICAL**: Add `-skip_path_updater` flag when running on GitHub runners to avoid Python path issues.

```powershell
# Navigate to the module directory
cd Modules\PTH_DTS

# Run with -skip_path_updater flag
# Note: Adjust .env and .bdefs filenames if they differ in your repository
python <repo_root>\Shared\BaseInputs\pytpd\main\pymtpl.py "moduleName.py" -env <repo_root>\POR_TP\Class_NVL_S28C\EnvironmentFile.env -skip_path_updater
    ```

### Bash / Linux

```bash
# Navigate to the module directory
cd Modules/PTH_DTS

# Run pymtpl.py with relative paths
# Note: Adjust .env and .bdefs filenames if they differ in your repository
python <repo_root>\Shared\BaseInputs\pytpd\main\pymtpl.py "moduleName.py" -env <repo_root>\POR_TP\Class_NVL_S28C\EnvironmentFile.env
```

## Compilation Workflow

### Standard Compilation Steps

1. **Locate pymtpl.py** - Find script in repository (typically `Shared/BaseInputs/pytpd/main/pymtpl.py`)
2. **Navigate to module directory** - `cd Modules/<MODULE_NAME>/`
3. **Calculate relative paths** - Determine paths from module directory to pymtpl.py, EnvironmentFile.env
4. **Execute pymtpl.py** - Run with correct syntax and flags
5. **Validate output** - Check generated files exist (.mtpl, .sbdefs, .flw)

## Command Syntax

### Required Arguments

```bash
python <path-to-pymtpl.py> <MODULE>.py -env <path-to-env-file>
```

⚠️ **Note**: The environment filenames may vary by repository (e.g., `EnvironmentFile.env`, `Product.env`, etc.). Use the search commands in "Finding File Locations" to locate the correct files.

### Optional Flags

- `-skip_path_updater` - Use on GitHub runners to avoid Python path issues

### Path Requirements

⚠️ **CRITICAL**: All paths must be relative to the module directory where you run the command. This is bevause Pymtpl output paths are relative to the Module directory. So the output mtpl generated may be somewhere else if you are not in the module directory when you run the command.

**Example from `Modules/PTH_DTS/`:**
- pymtpl.py: `../../Shared/BaseInputs/pytpd/main/pymtpl.py`
- Environment file: `../../Shared/Common/EnvironmentFile.env` (filename may vary)
- Bin definitions: `../../Shared/Common/BinDefinitions.bdefs` (filename may vary)

## Finding File Locations

### Find pymtpl.py

```powershell
# PowerShell - Search for pymtpl.py
Get-ChildItem -Path . -Filter "pymtpl.py" -Recurse -ErrorAction SilentlyContinue | Select-Object FullName

# Or find pymtpl.bat which contains the path
Get-ChildItem -Path . -Filter "pymtpl.bat" -Recurse | Select-Object FullName
```

### Find Environment File (.env)

⚠️ **Note**: Filename may vary - could be `EnvironmentFile.env`, `<Product>.env`, or similar.

```powershell

# Or search the entire repository
Get-ChildItem -Path . -Filter "*.env" -Recurse -ErrorAction SilentlyContinue | Select-Object FullName
```

## Generated Files

Compilation produces:

| File | Description |
|------|-------------|
| `<MODULE>.mtpl` | Test plan file with test instances and flows |
| `<MODULE>.sbdefs` | Module-specific bin definitions |
| `<MODULE>.flw` | Flow file with test execution routing |
| `<MODULE>.usrv` | User variables file (if UserVars defined) |

## Example Output

```powershell
PS> cd Modules\PTH_DTS
PS> python <repo_root>\Shared\BaseInputs\pytpd\main\pymtpl.py PTH_DTS.py -env <repo_root>\POR_TP\Class_NVL_S28C\EnvironmentFile.env -bindef ..\..\Shared\Common\BinDefinitions.bdefs

Loading module PTH_DTS.py...
Loading module PTH_DTS.py...
Generating test instances...
Writing PTH_DTS.mtpl...
Writing PTH_DTS.sbdefs...
Writing PTH_DTS.flw...
Compilation complete.

# Verify files were created
PS> ls *.mtpl, *.sbdefs, *.flw

PTH_DTS.mtpl    (12,543 bytes)
PTH_DTS.sbdefs  (3,421 bytes)
PTH_DTS.flw     (8,234 bytes)
```

## Integration with Other Skills

    ### In Module Creation Workflow

Part of [module-creation](../module-creation/SKILL.md) workflow:
1. Create .py file
2. **Compile with pymtpl.py** ← This skill
3. Integrate into solution

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **pymtpl.py not found** | Search for pymtpl.py: `Get-ChildItem -Filter "pymtpl.py" -Recurse` |
| **EnvironmentFile.env not found** | Check Shared/Common/EnvironmentFile.env exists |
| **Module not found error** | Verify running from module directory |
| **Flow name mismatch** | Check goto references match Flow names (see flow composites) |
| **Import errors on GitHub** | Use -skip_path_updater flag when running on GitHub runners |
| **Permission denied** | Check file permissions, ensure not read-only |

## Advanced Usage

### Batch Compilation

Compile multiple modules in sequence:

```powershell
# Compile all PTH modules
Get-ChildItem Modules\PTH*\*.py | ForEach-Object {
    $moduleName = $_.BaseName
    $modulePath = $_.Directory.Name
    Push-Location "Modules\$modulePath"
    python <repo_root>\Shared\BaseInputs\pytpd\main\pymtpl.py "$moduleName.py" -env <repo_root>\POR_TP\Class_NVL_S28C\EnvironmentFile.env
    Pop-Location
}
```

## Repository Structure Reference

### Typical File Locations

```
Test Program Root/
├── Modules/
│   └── <MODULE_NAME>/
│       ├── <MODULE>.py          ← Module source
│       └── .BinLimits.json      ← Bin range limits
├── Shared/BaseInputs/
│   └── pytpd/
│       └── main/
│           └── pymtpl.py        ← Compiler script
└── Shared/
    └── Common/
        ├── EnvironmentFile.env           ← Environment config (filename may vary)
        └── BinDefinitions.bdefs ← Main bin definitions (filename may vary)
```

⚠️ **Note**: The environment and bin definitions filenames shown above are typical examples but may differ in your repository.

## Validation Checklist

### Pre-compilation Checks

- [ ] Module .py file exists and is readable
- [ ] Module directory contains .BinLimits.json
- [ ] pymtpl.py script is accessible (typically at `Scripts/pytpd/main/pymtpl.py`)
- [ ] If not found, let user know they need to clone the submodules with `git submodule update --init --recursive`
- [ ] Environment file exists (typically `*.env` in `Shared/Common/` - filename may vary)
- [ ] Working directory is module directory (`Modules/<MODULE_NAME>/`)

### Post-compilation Checks

- [ ] .mtpl file was generated
- [ ] .sbdefs file was generated
- [ ] .flw file was generated - Optional
- [ ] Generated files are non-empty
- [ ] No compilation errors in output