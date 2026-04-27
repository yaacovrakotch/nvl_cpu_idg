---
name: module-creation
description: Create a blank Pymtpl module from scratch with all required files, directory structure, and solution integration. Use when creating a blank test module.
argument-hint: "ModuleName"
user-invokable: true
---

# Create New Module

This skill automates creation of a blank Pymtpl module from scratch using the [create_module.py](create_module.py) script. It creates all required files, directory structure, and integrates with solution files.

The module is created with the correct Initialize class configured automatically.

## What This Skill Creates

**Automatically created:**
1. **Directory structure** - `Modules/<MODULE_NAME>/` with `InputFiles/` subdirectory
2. **Configuration files** - `.mconfig`, `.BinLimits.json`, `.tpmodule`, `.mtproj`
3. **Python source** - `.py` file from template with MODULE_NAME configured
4. **Solution integration** - Updates to `.sln`, `.imp`, `.stpl`, `.tpproj`

**Post-creation steps:**
5. **Compile module** - Use [pymtpl-compiler skill](../pymtpl-compiler/SKILL.md) to generate `.mtpl`, `.sbdefs`, `.flw`
6. **Verify solution integration** - Validate that the updates to the solution files are correct.

## Prerequisites

- Test program repository structure exists
- Module name doesn't already exist
- Product-specific Initialize class defined (see [product-config.instructions.md](../../instructions/product-config.instructions.md))

## Workflow

### Step 1: Obtain Required Information from User

Ask user for:
- **Module name** (e.g., "PTH_NEW", "PTH_DTS")
- **Initialize class name** (e.g., "InitializeMTL", "InitializeLNL") - See [product-config.instructions.md](../../instructions/product-config.instructions.md)

### Step 2: Locate Solution Files

Find these files using file_search:
- **`.imp` file** - Usually `TestProgram/TestProgram.imp` or `POR_TP/TestProgram/TestProgram.imp`
- **`.stpl` file** - Usually same directory as `.imp`
- **`.tpproj` file** - Usually same directory as `.imp`
- **`.sln` file** - Auto-detected in workspace root (or can specify manually)

**Example search:**
```python
file_search("**/*.imp")
file_search("**/*.stpl") 
file_search("**/TestProgram.tpproj")
```

### Step 3: Run create_module.py Script

**Command:**
```bash
python .github/skills/module-creation/create_module.py PTH_NEW \
  --initialize InitializeMTL \
  --imp TestProgram/TestProgram.imp \
  --stpl TestProgram/TestProgram.stpl \
  --tpproj TestProgram/TestProgram.tpproj
```

**Script parameters:**
- `module_name` (required) - Name of module to create
- `--initialize` (required) - Initialize class name (e.g., InitializeMTL, InitializeLNL)
- `--imp` (required) - Path to .imp file for solution integration
- `--stpl` (required) - Path to .stpl file for solution integration
- `--tpproj` (required) - Path to .tpproj file for solution integration
- `--workspace-root` - Workspace directory (default: current directory)
- `--template` - Path to module_template.py (default: auto-detect)
- `--sln` - Path to .sln file (default: auto-detect in workspace root)
- `--project-type-guid` - Project type GUID for .sln (default: auto-detect from existing .mtproj projects)

### Step 4: Verify Creation

Check that all files were created:
- `Modules/<MODULE_NAME>/<MODULE_NAME>.py`
- `Modules/<MODULE_NAME>/<MODULE_NAME>.mtproj`
- `Modules/<MODULE_NAME>/.mconfig`
- `Modules/<MODULE_NAME>/<MODULE_NAME>.BinLimits.json`
- `Modules/<MODULE_NAME>/.tpmodule`
- `Modules/<MODULE_NAME>/InputFiles/` (directory)

### Step 5: Post-Creation Configuration

**Compile module** using [pymtpl-compiler skill](../pymtpl-compiler/SKILL.md)

### Step 6: Verify Solution Integration

Check that the updates to the `.sln`, `.imp`, `.stpl`, and `.tpproj` files are correct.

## Related Documentation

- [create_module.py](create_module.py) - Module creation script
- [module_template.py](../../instructions/pymtpl/templates/module_template.py) - Python template
- [product-config.instructions.md](../../instructions/product-config.instructions.md) - Initialize class configuration
- [pymtpl-compiler skill](../pymtpl-compiler/SKILL.md) - Compilation guide

## Common Issues

| Issue | Solution |
|-------|----------|
| **Module already exists** | Cancel workflow and prompt user to choose a different module name |
| **Template not found** | Use `--template` parameter to specify path to module_template.py |
| **Python not found** | Ensure Python 3.6+ is installed and in PATH |
| **Solution files not found** | Verify file paths using file_search; check for TestProgram/ vs POR_TP/TestProgram/ |
| **Initialize class name wrong** | Check product-config.instructions.md for correct class name |
| **Solution doesn't load in Visual Studio** | Project type GUID may be wrong; script auto-detects from existing .mtproj projects, or use `--project-type-guid` to specify manually |
| **Solution files not updated** | Verify file paths are correct; check script output for warnings |
| **Compilation failed after creation** | Review Initialize class configuration (see product-config.instructions.md) |
