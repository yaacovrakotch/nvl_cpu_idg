---
applyTo: "**/pymtpl/binctr.py"
---
# Binning and Counter Module (binctr.py)

## Purpose
Manages automatic bin and counter assignment strategies for different products and test types. Provides sticky bins/counters through JSON files and supports reading from MTPL.

## Key Concepts

### Bin Formats

**4-Digit Bins** (HBSB):
- Format: `HBSB` where HB=HardBin, SB=SoftBin
- Example: `4401` (HB=44, SB=01)
- Used in: MTL products, MTT tests

**8-Digit Bins** (90HBSBXX):
- Format: `90HBSBXX` where HB=HardBin, SB=SoftBin, XX=unique identifier
- Example: `90440101` (HB=44, SB=01, XX=01)
- Used in: NVL, DMR, Sort products

**Counter Format** (8-Digit):
- Format: `HBSBXXXX` or similar product-specific format
- Example: `44010001`
- Pass counters may use different prefix (e.g., 99XXXXXX for DMR)

### Bin Assignment Methods

1. **Manual Binning**: Specify exact bin value
   ```python
   pFail(setbin=90440101)  # 8-digit
   pFail(setbin=4401)      # 4-digit
   ```

2. **Auto-Binning with Hardbin**: Specify hardbin, auto-assign softbin
   ```python
   pFail(setbin=-44)  # Auto-assign in HB 44 range
   ```

3. **Fully Automatic**: Let pymtpl choose everything
   ```python
   pFail(setbin=AUTO)  # or setbin=-1
   ```

## Binning Strategies

### BaseBin
**Parent class** for all binning strategies.

**Key Attributes**:
- `bin_registry`: Dict mapping bins to names
- `all_4digit`: Set of used 4-digit bins
- `all_8digit`: Set of used 8-digit bins
- `autobindict`: Sticky bin assignments
- `sbdef_dict`: Sub-bin definition dictionary

**Key Methods**:
- `set_bin_range()`: Set available bin ranges
- `load_autobinfile()`: Load sticky bins from JSON
- `load_autobininfo_from_mtpl()`: Read bins from existing MTPL
- `write_sbdef_file()`: Generate .sbdefs file
- `populate_internal_bin_trackers()`: Track user-defined bins

### BinSSB (MTL)
**Format**: 4-digit HBSB, converts to 8-digit as `90HBHBSB`

**Ignore List**: `['rm1', 'rm2', 'r1', 'r4', 'r5']`
- These ports don't participate in auto-binning
- rm1/rm2 use default system/clamp bins
- r4/r5 use thermal/reset bins
- r1 is pass port (typically no bin)

**Bin Conversion**:
```python
# 4-digit to 8-digit
4401 → 90444401
```

**Special Bins**:
- **Thermal** (r4): `97HBXX` format
- **Reset** (r5): `HB19XX` format

**Example**:
```python
Initialize(
    'output', 'Module',
    binrange=(4400, 4450),
    nonmttbinstrategy=BinSSB
)
```

### MTTBinSSB (MTL MTT)
**Format**: 4-digit bins with FlowMatrix variable

**Bin String Output**:
```python
"SoftBins.b" + FlowMatrix.bin + "4401_fail_Module_TestName"
```

**Ignore List**: `['rm1', 'rm2', 'r1']`

### NVLClass8dig
**Format**: 8-digit `90HBSBXX` with unique XX per HBSB

**Bin Conversion**:
```python
# 4-digit HBSB input → unique 8-digit
4401 → 90440100, 90440101, 90440102, ... (incrementing XX)
```

**Ignore List**: `['rm1', 'rm2', 'r1', 'r5']`

**Special Features**:
- Tracks bin counter per HBSB combination
- Supports custom thermal/reset bins via Initialize parameters
- Validates input bins must be 7-8 digits

**Thermal/Reset Handling**:
```python
# Default thermal bin (if not specified)
defaultthermalbin=90974401  # Format: 9097HBXX

# Default reset bin
defaultresetbin=90441901    # Format: 90HB19XX
```

**Example**:
```python
Initialize(
    'output', 'Module',
    binrange=(4400, 4450),
    nonmttbinstrategy=NVLClass8dig,
    defaultthermalbin=90974401,
    defaultresetbin=90441901
)
```

### MTTNVLClass8dig
MTT variant of NVLClass8dig, similar 4-digit counter logic.

### Sort8dig
**Format**: Full 8-digit bins used as-is

**Key Difference**: No bin conversion, uses full 8-digit as bin and counter

**Ignore List**: `['rm1', 'rm2']`

**Example**:
```python
Initialize(
    'output', 'Module',
    binrange=(44000000, 44999999),  # Full 8-digit range
    nonmttbinstrategy=Sort8dig
)
```

### ServerClass8dig
**Format**: 8-digit bins, special port handling

**Key Features**:
- **All ports get counters** (no ignore list by default)
- Special rm1/rm2 counter matching when using defaultrm1bin/defaultrm2bin
- Supports skip_pass_counters flag

**Port String Format**:
```python
# Uses port number directly (not last digit)
'n1' for rm1, 'n2' for rm2, '4' for r4, '5' for r5
```

**Example**:
```python
Initialize(
    'output', 'Module',
    binrange=(4400, 4450),
    nonmttbinstrategy=ServerClass8dig,
    defaultrm1bin='b90980100_fail_FAIL_SYSTEM_SOFTWARE_n1'
)
```

### CtrServerClass8dig
Counter strategy for ServerClass8dig.

**EDC Counter Range**:
- Fail ports: `90HBXX00` to `90HBXX99`
- Pass ports: `99HBXX00` to `99HBXX99`

### DMRdefault / CtrDMRClass8dig
**Special Features**:
- `skip_pass_counters = True`: No automatic pass counters
- rm1/rm2 counters match bin names (b→n substitution)
- Custom bin naming in sbdef

**Bin Name Format**:
```python
# Example: defaultrm1bin handling
'b90980100_fail_FAIL_SYSTEM_SOFTWARE_n1'
↓ (counter matches)
'n90980100_fail_FAIL_SYSTEM_SOFTWARE_n1'
```

### CBRdefault
Same as DMR but:
- `write_hardbins_to_sbdef = False`
- `write_softbins_to_sbdef = False`

## Counter Strategies

### BaseCounter
**Parent class** for counter strategies.

**Key Attributes**:
- `ctr_registry`: Dict mapping counters to names
- `all_8digit_counter`: Set of used counters
- `autoctrdict`: Sticky counter assignments
- `ctr_headers`: Counter headers for MTPL

**Key Methods**:
- `load_autoctrfile()`: Load sticky counters from JSON
- `get_portctrstring()`: Generate counter string for port
- `get_unique_edc_ctr()`: Get counter for EDC/pass ports

### CtrHBSB (MTL)
**Format**: `HBSBXXXX` (4-digit HBSB + 4-digit counter)

**Counter Generation**:
```python
# Based on bin: 4401
# Counter: 44010001, 44010002, 44010003, ...
```

**Ignore List**: `['rm1', 'rm2', 'r1']`

### MTTCtrHBSB
MTT variant using 4-digit counters with FlowMatrix.

### CtrNVLClass8dig
**Format**: `HBSBXXXX` (4-digit HBSB from bin + 4-digit counter)

**Special Handling**:
- Thermal counters: Random starting point per module
- Reset counters: Random starting point per module
- EDC/Pass counters: From edcportctrbinrange

**Ignore List**: `['rm1', 'rm2']`

**Example**:
```python
Initialize(
    'output', 'Module',
    nonmttctrstrategy=CtrNVLClass8dig,
    edcportctrbinrange=[(4400, 4450)]  # For EDC tests
)
```

### MTTCtrNVLClass8dig
MTT variant with pseudo-random 4-digit counter start:
- ARR modules: 0-2000
- FUN modules: 3001-5000
- SCN modules: 6001-8000
- Others: 9001-9099

### CtrSort8dig
**Format**: Counter equals bin value

**Key Feature**: Bin and counter are identical (full 8-digit)

## JSON Files

### AutoBinner JSON
**Location**: `{module_dir}/PymtplInputFiles/{module}_AutoBinner.json`

**Format**:
```json
{
  "TestName1": {
    "bin": "4401",
    "r0": "90440101",
    "r2": "90440102"
  },
  "TestName2": {
    "bin": "4402",
    "r0": "90440201"
  }
}
```

**Purpose**: Maintains sticky bin assignments across pymtpl runs

### AutoCounter JSON
**Location**: `{module_dir}/PymtplInputFiles/{module}_AutoCounter.json`

**Format**:
```json
{
  "TestName1": {
    "r0": "44010001",
    "r2": "44010002"
  },
  "TestName2": {
    "r0": "44020001"
  }
}
```

**Purpose**: Maintains sticky counter assignments across pymtpl runs

### AutoBasenumber JSON
**Location**: `{module_dir}/PymtplInputFiles/{module}_AutoBasenumber.json`

**Format**:
```json
{
  "TestName1": "1000",
  "TestName2": "1001"
}
```

**Purpose**: Auto-assigns and tracks unique basenumbers

## Sub-Bin Definition (.sbdefs) File

Generated by `write_sbdef_file()` method.

**Sections**:
1. **HardBins**: 2-digit hardbins (if enabled)
2. **SoftBins**: 4-digit HBSB bins (if enabled)
3. **DataBins**: Full 8-digit bins with descriptions

**Example Output**:
```
Version 1.0;
SubBinDefs
{
    BinGroup HardBins
    {
        Bin b44_FAIL_XXX    44    : "b44_FAIL_XXX",    Fail;
    }
    
    BinGroup SoftBins
    {
        Bin b4401    4401    : "b4401",    b44_FAIL_XXX;
    }
    
    BinGroup DataBins
    {
        LeafBin b90440101_fail_Module_Test1    90440101    : "...",    b4401;
    }
}
```

## Reading from MTPL

### BaseMtplInfo
**Purpose**: Parses existing MTPL to extract bin/counter information

**Key Methods**:
- `load_mtpl_dutflow_map()`: Read MTPL and populate dutflow map
- `_update_autobin_json()`: Extract bins from port data
- `_update_autoctr_json()`: Extract counters from port data

**Use Case**: When `usebinctrfrommtpl=True` in Initialize

## Best Practices

### Bin Management
1. **Define Adequate Ranges**: Ensure enough bins for all tests
2. **Use Sticky Bins**: Let JSON files maintain consistency
3. **Check Bin Exhaustion**: Monitor when ranges are nearly full
4. **Product-Specific**: Use correct strategy for your product

### Counter Management
1. **Let Auto-Counter Work**: Don't manually specify unless needed
2. **EDC Range**: Define edcportctrbinrange for EDC tests
3. **Check Uniqueness**: Manual counters must not conflict
4. **Pass Counters**: Some strategies skip pass counters (e.g., DMR)

### Shared Bins
When multiple tests use same bin:
- Bin name gets `_SHARED_BIN` suffix
- First test to use bin sets the name
- Useful for common fail bins

### Special Port Bins
- **rm1**: Software/system alarm (typically 98XX)
- **rm2**: Clamp/DPS alarm (typically 99XX)
- **r4**: Thermal bin (97XX or custom)
- **r5**: Reset bin (HB19XX or custom)

## Strategy Selection Guide

| Product | Non-MTT Binning | MTT Binning | Non-MTT Counter | MTT Counter |
|---------|----------------|-------------|-----------------|-------------|
| MTL | BinSSB | MTTBinSSB | CtrHBSB | MTTCtrHBSB |
| NVL Class | NVLClass8dig | MTTNVLClass8dig | CtrNVLClass8dig | MTTCtrNVLClass8dig |
| NVL Sort | Sort8dig | N/A | CtrSort8dig | N/A |
| DMR Class | ServerClass8dig | MTTNVLClass8dig | CtrDMRClass8dig | MTTCtrNVLClass8dig |
| CBR Class | ServerClass8dig | MTTNVLClass8dig | CtrServerClass8dig | MTTCtrNVLClass8dig |

## Common Issues

### Bin Range Exhaustion
**Symptom**: Error about no available bins
**Solution**: Increase bin range or use multiple ranges

### Counter Collisions
**Symptom**: Error about duplicate counter
**Solution**: Use auto-counters or ensure manual counters are unique

### Missing JSON Files
**Symptom**: Tests get new bins every run
**Solution**: Let pymtpl create JSON files (don't delete them)

### Wrong Bin Format
**Symptom**: Validation error on bin format
**Solution**: Use correct digit count for strategy (4 vs 8 digit)

## Advanced Features

### Multiple Bin Ranges
```python
Initialize(
    'output', 'Module',
    binrange=[(4400, 4450), (8001, 8100)],  # Multiple ranges
    nonmttbinstrategy=BinSSB
)
```

### Bin Ignore List
```python
Initialize(
    'output', 'Module',
    binrange=(4400, 4500),
    autobinignorelist=[4401, 4402, 9044]  # Skip these bins
)
```

### Custom Thermal/Reset Bins
```python
Initialize(
    'output', 'Module',
    defaultthermalbin=(90974401, 90974501),  # Multiple HBs
    defaultresetbin=(90441901, 90451901)
)
```

### EDC Port Counters
```python
Initialize(
    'output', 'Module',
    edcportctrbinrange=[(4400, 4450)]  # Counter range for EDC
)
```
