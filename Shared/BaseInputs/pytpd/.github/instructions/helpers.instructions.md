---
applyTo: "**/pymtpl/helpers.py"
---
# Helper Functions and Utilities (helpers.py)

## Purpose
Provides utility functions and helper classes for common pymtpl operations, including ProgramFlows generation, input file path handling, and configuration helpers.

## ProgramFlows Class

### Purpose
Creates pymtpl objects for ProgramFlows.mtpl - the top-level flow that orchestrates module execution.

### Configuration Format

**Basic Syntax**:
```python
program_flows = '''
<subflow>  <module>  <port> <port> ...
'''
```

**Example**:
```python
program_flows = '''
START               TPI_FLWFLGS_XXX    r2p
START               TPI_BASE_XXX       r2p:TPI_PRESI_XXX  r3f
SHAREDRAILSNOM      TPI_DFF_XXX        r2p                r3p
'''
```

### Port Syntax

**Format**: `r<N><p/f><return/n><:goto>`

**Components**:
- `r<N>`: Result port (r0, r1, r2, rm1, rm2, etc.)
- `<p/f>`: Pass or Fail
- `<return>`: Return value or 'n' for NEXT
- `:<goto>`: Optional goto target

**Examples**:
```python
r2p              # Result 2, Pass, return 1 (default)
r2p2             # Result 2, Pass, return 2
r2pm1            # Result 2, Pass, return -1
r2pn             # Result 2, Pass, goto NEXT
rm1pn            # Result -1, Pass, goto NEXT
r2f:<mod>        # Result 2, Fail, goto <mod>
r0f0             # Result 0, Fail, return 0
r1px             # Delete r1 port (x = exclude)
```

### Usage

```python
from pymtpl.helpers import ProgramFlows
from pymtpl.core import Initialize

# Initialize for ProgramFlows
Initialize('ProgramFlows', 'ProgramFlowsModule', tosversion='tos4')

# Define configuration
config = '''
MAIN    TPI_FLWFLGS_XXX    r2p
MAIN    TPI_BASE_XXX       r0f0  r2p
MAIN    TPI_END_XXX        r0f0  r1p
'''

# Generate ProgramFlows
pf = ProgramFlows()
pf.main(config, topflow='MAIN', ip=False)
```

**Parameters**:
- `config`: Text configuration string
- `topflow`: Name of top-level flow ('MAIN', 'INIT', etc.)
- `ip`: False for module ProgramFlows, True for IP ProgramFlows

### Special Features

#### DEFAULTS Handling
Define default ports for all modules:
```python
config = '''
START    DEFAULTS    r0f0  rm1fm1  rm2fm2
START    Module1     r2p
START    Module2     r2p
'''
```

#### Module Flow Naming
- **Simple**: `Module` → `IP::Module::FITEM_START`
- **With $**: `$Module` → `Module` (direct reference)
- **With ~**: `~Module` → `Module` (no IP prefix)
- **With ::**: `IP::Module::Flow` → as-is

### TopFlow vs SubFlow
- **TopFlow** (MAIN): Goes directly in MAIN flow
- **SubFlow** (START, END, etc.): Creates `START_SubFlow` composite

## NVLProgramFlows Class

### Purpose
Specialized ProgramFlows for NVL products with multi-die support.

### Key Features

#### Die Combination Handling
Supports CPU, HUB, GCD, PCD combinations:
```python
die_combo = ['CPU', 'GCD']  # Disaggregated TP
die_combo = ['CPU', 'HUB', 'GCD', 'PCD']  # Full TP
```

#### Concurrent Flow Generation
```python
params = NVLProgramFlows.get_flow_params(
    dc=['CPU', 'GCD'],
    templatename='BEGIN%s'
)
# Returns dict for ConCurrentFlow() creation
```

**Output**:
```python
{
    'IPC': 'IPC_FLOWS::BEGINCPU',
    'IPG': 'IPG_FLOWS::BEGINGCD',
    'result': [
        'IPC, IPG, EffectiveIPResult',
        '[-2:-1], *, IPC',
        '0, *, IPC',
        '1, *, IPC',
        ...
    ]
}
```

#### Dielet Stripping
```python
final_code = NVLProgramFlows.strip_dielets(main_code, ['CPU', 'GCD'])
```
Removes flows/modules not needed for specific die combination.

#### Empty Composite Handling
```python
updated_flow = NVLProgramFlows.ignore_emptycomp(comp_name, die_combo)
```
Removes empty composite references marked with `###`.

## Input File Helpers

### inputfile() Function

**Purpose**: Generate paths to module InputFiles directory.

**Basic Usage**:
```python
from pymtpl.helpers import inputfile

# Get InputFiles directory path
base_path = inputfile()  # GetEnvironmentVariable("~HDMT_TP_BASE_DIR")+"/Modules/ModName/InputFiles/"

# Get specific file path
file_path = inputfile('config.csv')  # ...InputFiles/config.csv

# With subdirectory
file_path = inputfile('subfolder/data.txt')  # ...InputFiles/subfolder/data.txt
```

**Returns**: `Spec()` object (unwrapped in MTPL generation)

### InputFilePathOptions Configuration

**Control inputfile() behavior**:
```python
from pymtpl.helpers import InputFilePathOptions

# Use Spec() wrapper (default True)
InputFilePathOptions.USE_SPEC = True

# Override base path
InputFilePathOptions.OVERRIDE_INPUTFILE_PATH = 'MyUserVars.InputFilePath'

# Change joining operator
InputFilePathOptions.JOINING_OPERATOR = ' + "'  # For concatenation
```

**Example with Override**:
```python
# In MTPL header, define uservar:
# String InputFilePath = GetEnvironmentVariable("~HDMT_TP_BASE_DIR")+"/Modules/MyModule/InputFiles/";

from pymtpl.helpers import inputfile, InputFilePathOptions

InputFilePathOptions.OVERRIDE_INPUTFILE_PATH = 'MyUserVars.InputFilePath'

# Now inputfile() uses the uservar
ConfigFile = inputfile('config.csv')
# Result: MyUserVars.InputFilePath/config.csv
```

### inputfile_selector_rule()

**Purpose**: Create selector rule functions for input files.

**Usage with functools.partial**:
```python
from functools import partial
from pymtpl.helpers import inputfile_selector_rule, InputFilePathOptions

InputFilePathOptions.OVERRIDE_INPUTFILE_PATH = 'MyUserVars.InputFilePath'

# Create selector function
FileByChop = partial(
    inputfile_selector_rule,
    selectorrule='TPKnobs.Chop',
    argcount=2
)

# Use it
ConfigFile = FileByChop('xcc.csv', 'lcc.csv')
# Result: MyUserVars.InputFilePath + TPKnobs.Chop("xcc.csv", "lcc.csv")
```

## Bin Limits Helper

### get_bin_limits_from_json()

**Purpose**: Read bin limits from module's BinLimits.json file.

**File Location**: `{module_dir}/{module_name}.BinLimits.json`

**JSON Format**:
```json
{
    "BinLimits": [
        [9825, 9850],
        [900, 999],
        [6800, 6899]
    ],
    "Comment": "Optional comments or other keys"
}
```

**Usage**:
```python
from pymtpl.helpers import get_bin_limits_from_json

bin_limits = get_bin_limits_from_json('MyModule')
# Returns: [(9825, 9850), (900, 999), (6800, 6899)]

# Use in Initialize
Initialize(
    'output', 'MyModule',
    binrange=bin_limits,
    edcportctrbinrange=bin_limits
)
```

**Bin Range Meaning**:
- Middle 4 digits of 8-digit bin
- `[9825, 9850]` → bins `90982500` to `90985099`
- `[900, 999]` → bins `90090000` to `90099999`

## Test Instance Creation Helper

### create_test_instance_with_defaults()

**Purpose**: Create test instances with default parameters.

**Direct Usage**:
```python
from pymtpl.helpers import create_test_instance_with_defaults
from pymtpl.por_methods import MyTestMethod

instance = create_test_instance_with_defaults(
    testmethod=MyTestMethod,
    defaults={'Patlist': 'default.plist', 'LevelsTc': 'default.lvl'},
    name='Test1',
    Patlist='custom.plist'  # Overrides default
)
```

**With functools.partial** (Recommended):
```python
from functools import partial
from pymtpl.helpers import create_test_instance_with_defaults
from pymtpl.por_methods import MyTestMethod

# Create reusable test creator
MyTest = partial(
    create_test_instance_with_defaults,
    testmethod=MyTestMethod,
    defaults={
        'Patlist': 'default.plist',
        'LevelsTc': 'default.lvl',
        'TimingsTc': 'default.tim'
    }
)

# Use it multiple times
test1 = MyTest(name='Test1')  # Uses all defaults
test2 = MyTest(name='Test2', Patlist='special.plist')  # Overrides Patlist
test3 = MyTest(name='Test3', LevelsTc='custom.lvl')  # Overrides LevelsTc
```

**Features**:
- Validates required parameters
- Allows selective override of defaults
- Clean syntax for repeated test creation
- Supports `required` sentinel value

## BOM Configuration Helper

### getvalidboms()

**Purpose**: Get valid BOMs for a category from TP configuration.

**File Location**: `{tpdir}/Shared/BaseInputs/Inputs/bom_to_category.json`

**JSON Format**:
```json
{
    "POR": ["BOM1", "BOM2", "BOM3"],
    "ENG": ["BOM4", "BOM5"],
    "CategoryName": ["BOM_A", "BOM_B"]
}
```

**Usage**:
```python
from pymtpl.helpers import getvalidboms

# Get BOMs for category
valid_boms = getvalidboms('POR')
# Returns: ["BOM1", "BOM2", "BOM3"]

# Use in MConfig
from pymtpl.core import MConfig

for bom in valid_boms:
    MConfig(
        path='/patterns',
        plistinfo={'pattern.plist': bom}
    )
```

**Requires**: `OPT.env` to be set (env file path)

## Validation and Utility Classes

### Compact Class

**Purpose**: Compact MTPL output for unittest assertions.

**Usage**:
```python
from pymtpl.helpers import Compact

# In unittest
result = str(Compact('output.mtpl'))
expected = '''
DUTFlow MAIN {
    DUTFlowItem Test1 Test1 {
        Result 0 { Property PassFail = "Fail"; Return 0; }
    }
}
'''
self.assertEqual(result, expected)
```

**Features**:
- Removes empty lines
- Compacts Result blocks to single line
- Preserves indentation
- Easier to write test assertions

### ValidationMtplConvert Class

**Purpose**: Validate MTPL→Python→MTPL round-trip conversion.

**Usage** (for validation testing):
```python
from pymtpl.helpers import ValidationMtplConvert

validator = ValidationMtplConvert()
validator.main(
    env='/path/to/EnvironmentFile.env',
    mtpl='/path/to/ProgramFlows.mtpl',
    outpy='output/programflows.py'
)
# Converts MTPL to Python and regenerates MTPL for comparison
```

## Best Practices

### Input File Paths
1. **Use inputfile()**: Don't hardcode paths
2. **Set Override**: Use uservar for flexibility
3. **Normalize Paths**: Function handles slashes automatically
4. **Selector Rules**: Use for conditional files

### ProgramFlows
1. **Order Matters**: Define subflows before MAIN
2. **Use DEFAULTS**: Reduce repetition
3. **Test Incrementally**: Add modules gradually
4. **Check Port Logic**: Verify returns and gotos

### Test Creation
1. **Use Defaults**: Reduce code duplication
2. **Partial Functions**: Create reusable test creators
3. **Override Selectively**: Only specify what changes
4. **Document Defaults**: Make them clear for maintenance

### Bin Limits
1. **External File**: Keep in JSON, not hardcoded
2. **Adequate Ranges**: Ensure enough bins
3. **Document Ranges**: Explain bin allocation
4. **Version Control**: Track JSON files

## Common Patterns

### ProgramFlows Template
```python
from pymtpl.helpers import ProgramFlows
from pymtpl.core import Initialize

Initialize('ProgramFlows', 'ProgramFlows', tosversion='tos4')

config = '''
MAIN    Module1    r0f0  r2p
MAIN    Module2    r0f0  r2p
'''

ProgramFlows().main(config, 'MAIN', ip=False)
```

### Test Creator Pattern
```python
from functools import partial
from pymtpl.helpers import create_test_instance_with_defaults

MyTest = partial(
    create_test_instance_with_defaults,
    testmethod=SomeTestMethod,
    defaults={'Patlist': 'default.plist'}
)

tests = [MyTest(name=f'Test{i}') for i in range(10)]
```

### Input File Pattern
```python
from pymtpl.helpers import inputfile, InputFilePathOptions

# In test parameter
ConfigFile = inputfile('configs/test.csv')

# With selector
from functools import partial
FileByBom = partial(
    inputfile_selector_rule,
    selectorrule='TPKnobs.Bom',
    argcount=3
)
ConfigFile = FileByBom('bom1.csv', 'bom2.csv', 'bom3.csv')
```

## Advanced Features

### NVL Concurrent Flow
```python
from pymtpl.helpers import NVLProgramFlows
from pymtpl.core import ConCurrentFlow

params = NVLProgramFlows.get_flow_params(['CPU', 'GCD'], 'BEGIN%s')

ConCurrentFlow('BEGIN_SubFlow', **params)
```

### Dielet Configuration
```python
# Full TP code
main_code = '''...'''

# Strip to dielet
dielet_code = NVLProgramFlows.strip_dielets(main_code, ['CPU'])
```

### Compact Output Validation
```python
# Generate MTPL
from pymtpl.core import PyMtpl
PyMtpl.main()

# Compact for assertion
from pymtpl.helpers import Compact
actual = str(Compact('output.mtpl'))

# Compare
assert actual == expected_compact_output
```

## Migration Helpers

When migrating from old MTPL to pymtpl:
1. Use `mtpl2py.py` to generate initial Python
2. Use `getvalidboms()` to populate BOM lists
3. Use `get_bin_limits_from_json()` for bin ranges
4. Use `ValidationMtplConvert` to verify accuracy
