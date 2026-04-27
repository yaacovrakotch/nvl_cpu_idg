---
name: bin-name-override
description: Automatically detect and fix bin name mismatches between module .sbdefs files and the main BinDefinitions.bdefs file. Use when working with Pymtpl modules that need bindefovrd parameter corrections, after generating .sbdefs files, or when bin names don't match between module and main definitions.
argument-hint: module.py module.sbdefs BinDefinitions.bdefs
user-invokable: true
---

# Correct bindefovrd Parameter

This skill provides an automated tool to detect and fix bin name mismatches between module `.sbdefs` files and the main `BinDefinitions.bdefs` file.

## What This Skill Does

The [bin_name_override.py](./bin_name_override.py) script automatically:

1. **Parses files** - Reads `.sbdefs` and `.bdefs` files to extract bin definitions
2. **Finds mismatches** - Compares parent bin names between module and main definitions
3. **Generates overrides** - Creates properly formatted `bindefovrd` entries
4. **Updates module** - Modifies the `.py` file with correct bin overrides (smart merge preserves existing entries)
5. **Suggests additions** - Generates entries for missing parent bins in `.bdefs`

## When to Use This Skill

Use this skill when:
- Module `.sbdefs` parent bin names don't match `BinDefinitions.bdefs`
- Adding new `setbin()` calls to a module
- After compiling `.py` to generate `.sbdefs` (via `pymtpl.py`)
- Tests fail due to bin definition mismatches
- Integrating modules into test programs with different bin naming conventions

## Prerequisites

- Module `.py` file exists with `Initialize*` class
- Module `.sbdefs` file has been generated (run `pymtpl.py` first)
- Main `BinDefinitions.bdefs` file is accessible

## Usage

### Quick Start

```powershell
# From the test program root directory
python <path-to-skill>\bin_name_override.py <module.py> <module.sbdefs> <BinDefinitions.bdefs>
```

### Detailed Examples

**Run from repo root:**
```powershell
python ..\applications.manufacturing.ate-test.tp-tools.module-agent\.github\skills\bin-name-override\bin_name_override.py `
    .\Modules\MIO_DDR_COMP\MIO_DDR_COMP.py `
    .\Modules\MIO_DDR_COMP\MIO_DDR_COMP.sbdefs `
    .\Shared\Common\BinDefinitions.bdefs
```

**Preview changes without modifying (dry run):**
```powershell
python bin_name_override.py module.py module.sbdefs BinDefinitions.bdefs --dry-run
```

**Generate softbin names without zero-padding:**
```powershell
python bin_name_override.py module.py module.sbdefs BinDefinitions.bdefs --no-pad-softbin-names
```

### Command Options

- `--dry-run` - Show what would be changed without modifying files
- `--no-pad-softbin-names` - Generate softbin names without zero-padding (e.g., `b900` instead of `b0900`)

## Exit Codes

- **0** - All bin definitions are consistent, no changes needed
- **1** - Mismatches or missing bins were found (even if fixed)


## Related Documentation

- [BinDefinitions.instructions.md](../../instructions/TOS/BinDefinitions.instructions.md) - Bin definitions file format and naming rules
- [BinDefinitions.instructions.md](../../instructions/TOS/BinDefinitions.instructions.md) - Bin definitions file structure and hierarchy
- [02-initialize-config.instructions.md](../../instructions/pymtpl/02-initialize-config.instructions.md) - Initialize class configuration