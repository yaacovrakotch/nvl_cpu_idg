---
name: pattern-patch-update
description: Automated tool to update pattern patch versions across multiple module .mconfig files. Use when updating test pattern versions (e.g., update all PTH modules to p4).
argument-hint: "ModulePattern PatchVersion"
user-invokable: true
---

# Updating Pattern Patches in .mconfig Files

## Overview

Pattern patches specify which version of pattern files (test patterns) should be used for a module. These are defined in `.mconfig` XML files in `/Modules/*/` directories.

**IMPORTANT:** The configuration file is named `.mconfig` (a hidden file starting with a dot), NOT `*.mconfig` or `something.mconfig`. When searching or updating, use the exact filename `.mconfig`.

### .mconfig File Structure
- Standard Indentation

```xml
<?xml version="1.0" encoding="utf-8" ?>
<ModuleConfiguration>
    <Patterns>
        <PORRoot Path="\\amr\ec\proj\mdl\sc\intel\hdmxpats\cbr\Mpth" Rev="RevTC0.0" Patch="p2" >
            <PlistFiles>
                <PlistFile>vm_class.plist</PlistFile>
            </PlistFiles>
        </PORRoot>
    </Patterns>
</ModuleConfiguration>
```

## Update Methodology

When a user requests a patch update for a set of modules (e.g., "PTH modules" or "CLK modules"), update ALL `.mconfig` files in the matching module folders.

### Module Pattern Matching

Common module patterns:
- **PTH modules**: `/Modules/PTH*/.mconfig` (PTH_SOT, PTH_DTS, PTH_PMC, PTH_VM, PTH_PWR, PTH_PRESOAK, PTH_THRSOAK)
- **CLK modules**: `/Modules/CLK*/.mconfig` (CLK_PLL, etc.)
- **ARR modules**: `/Modules/ARR*/.mconfig` (ARR_MBIST, ARR_HBM)
- **SIO modules**: `/Modules/SIO*/.mconfig` (SIO_SERDES, SIO_PCIE)
- **EIO modules**: `/Modules/EIO*/.mconfig` (EIO_D2D)
- **FUS modules**: `/Modules/FUS*/.mconfig` (FUS_FUSEREAD, FUS_FUSEBURN)
- **SCN modules**: `/Modules/SCN*/.mconfig` (SCN_CORE)
- **TPI modules**: `/Modules/TPI*/.mconfig` (TPI_BASE, TPI_DC, TPI_RECOVERY)

### Patch Version Format

Patch values follow the format `Patch="p<number>"`:
- `p0` - Initial patch
- `p1` - Patch 1
- `p2` - Patch 2
- `p4` - Patch 4
- `p5` - Patch 5
- etc.

When updating, replace the entire patch value regardless of the previous value.

### Step-by-Step Workflow

#### Step 1: Identify Target Modules

Based on user request, identify the module pattern:
- "Update PTH modules to p4" → Target: `/Modules/PTH*/.mconfig`
- "Update CLK patch to p1" → Target: `/Modules/CLK*/.mconfig`

#### Step 2: Find All Matching Files

**PowerShell (Windows):**
```powershell
# Find all .mconfig files in PTH modules
Get-ChildItem -Path "Modules\PTH*" -Filter ".mconfig" -Recurse

# Find all .mconfig files in CLK modules
Get-ChildItem -Path "Modules\CLK*" -Filter ".mconfig" -Recurse
```

**Bash/Linux:**
```bash
# Find all .mconfig files in PTH modules (exact filename match)
find Modules/PTH* -name ".mconfig" -type f

# Find all .mconfig files in CLK modules (exact filename match)
find Modules/CLK* -name ".mconfig" -type f
```

#### Step 3: Update Patch Values

**PowerShell (Windows):**
```powershell
# Update all PTH modules to p4
Get-ChildItem -Path "Modules\PTH*" -Filter ".mconfig" -Recurse | ForEach-Object {
    (Get-Content $_.FullName) -replace 'Patch="p\d+"', 'Patch="p4"' | Set-Content $_.FullName
}

# Update all CLK modules to p6
Get-ChildItem -Path "Modules\CLK*" -Filter ".mconfig" -Recurse | ForEach-Object {
    (Get-Content $_.FullName) -replace 'Patch="p\d+"', 'Patch="p6"' | Set-Content $_.FullName
}
```

**Bash/Linux:**
```bash
# Update all PTH modules to p4
find Modules/PTH* -name ".mconfig" -type f -exec sed -i 's/Patch="p[0-9]\+"/Patch="p4"/' {} \;

# Update all CLK modules to p6
find Modules/CLK* -name ".mconfig" -type f -exec sed -i 's/Patch="p[0-9]\+"/Patch="p6"/' {} \;
```

#### Step 4: Verify Changes

**PowerShell (Windows):**
```powershell
# Verify all PTH modules now have the correct patch
Get-ChildItem -Path "Modules\PTH*" -Filter ".mconfig" -Recurse | Select-String "Patch="

# Verify all CLK modules now have the correct patch
Get-ChildItem -Path "Modules\CLK*" -Filter ".mconfig" -Recurse | Select-String "Patch="
```

**Bash/Linux:**
```bash
# Verify all PTH modules now have the correct patch
grep "Patch=" Modules/PTH*/.mconfig

# Verify all CLK modules now have the correct patch
grep "Patch=" Modules/CLK*/.mconfig
```

## Example Workflows

### Example 1: Update PTH Modules to Patch 4

**PowerShell (Windows):**
```powershell
# Find all PTH module .mconfig files
Get-ChildItem -Path "Modules\PTH*" -Filter ".mconfig" -Recurse

# Update all to p4
Get-ChildItem -Path "Modules\PTH*" -Filter ".mconfig" -Recurse | ForEach-Object {
    (Get-Content $_.FullName) -replace 'Patch="p\d+"', 'Patch="p4"' | Set-Content $_.FullName
}

# Verify
Get-ChildItem -Path "Modules\PTH*" -Filter ".mconfig" -Recurse | Select-String "Patch="
```

**Bash/Linux:**
```bash
# Find all PTH module .mconfig files
find Modules/PTH* -name ".mconfig" -type f

# Update all to p4
find Modules/PTH* -name ".mconfig" -type f -exec sed -i 's/Patch="p[0-9]\+"/Patch="p4"/' {} \;

# Verify
grep "Patch=" Modules/PTH*/.mconfig
```

### Example 2: Update CLK Modules to Patch 6

**PowerShell (Windows):**
```powershell
# Find all CLK module .mconfig files
Get-ChildItem -Path "Modules\CLK*" -Filter ".mconfig" -Recurse

# Update all to p6
Get-ChildItem -Path "Modules\CLK*" -Filter ".mconfig" -Recurse | ForEach-Object {
    (Get-Content $_.FullName) -replace 'Patch="p\d+"', 'Patch="p6"' | Set-Content $_.FullName
}

# Verify
Get-ChildItem -Path "Modules\CLK*" -Filter ".mconfig" -Recurse | Select-String "Patch="
```

**Bash/Linux:**
```bash
# Find all CLK module .mconfig files
find Modules/CLK* -name ".mconfig" -type f

# Update all to p6
find Modules/CLK* -name ".mconfig" -type f -exec sed -i 's/Patch="p[0-9]\+"/Patch="p6"/' {} \;

# Verify
grep "Patch=" Modules/CLK*/.mconfig
```

### Example 3: Update Multiple Module Types

**PowerShell (Windows):**
```powershell
# Update all ARR and SIO modules to p2
Get-ChildItem -Path "Modules\ARR*","Modules\SIO*" -Filter ".mconfig" -Recurse | ForEach-Object {
    (Get-Content $_.FullName) -replace 'Patch="p\d+"', 'Patch="p2"' | Set-Content $_.FullName
}

# Verify
Get-ChildItem -Path "Modules\ARR*","Modules\SIO*" -Filter ".mconfig" -Recurse | Select-String "Patch="
```

**Bash/Linux:**
```bash
# Update all ARR and SIO modules to p2
find Modules/ARR* Modules/SIO* -name ".mconfig" -type f -exec sed -i 's/Patch="p[0-9]\+"/Patch="p2"/' {} \;

# Verify
grep "Patch=" Modules/ARR*/.mconfig Modules/SIO*/.mconfig
```

## Key Points

- **Exact Filename:** The file is named `.mconfig` (hidden file with dot prefix), not `*.mconfig` or any other pattern
- **Module-Based Updates:** Target modules by folder pattern (e.g., `PTH*`, `CLK*`)
- **Version-Agnostic:** Updates replace any previous patch value (p0, p1, p2, etc.)
- **Simple Workflow:** No need to match by Path attribute, just update all files in matching module folders
- **Batch Updates:** Multiple modules' mconfigs can be updated in a single operation
- **Patch Format:** Always use format `Patch="p<number>"` (e.g., `Patch="p1"`, `Patch="p4"`)

## User Request Examples

- "Update PTH modules to pattern patch 4" → Update all `/Modules/PTH*/.mconfig` files to `Patch="p4"`
- "Set CLK patch to p6" → Update all `/Modules/CLK*/.mconfig` files to `Patch="p6"`
- "Update ARR mconfig to p2" → Update all `/Modules/ARR*/.mconfig` files to `Patch="p2"`
- "Change FUS modules to patch 5" → Update all `/Modules/FUS*/.mconfig` files to `Patch="p5"`
