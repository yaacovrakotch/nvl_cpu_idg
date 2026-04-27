---
applyTo: "**/pymtpl/core.py"
---
# Core Module (core.py)

## Purpose
Contains the fundamental classes for creating and managing test flows in pymtpl. This is the heart of the pymtpl framework.

## Key Classes

### Initialize
**Purpose**: Sets up module configuration and clears/initializes global state.

**Required Parameters**:
- `outfile`: Path to output MTPL file
- `module_name`: Name of the test module (TestPlan name)

**All Parameters** (with defaults):
- `binrange=[]`: Bin range(s) as tuple(s), e.g., `(4400, 4500)` or `[(4400, 4500), (8001, 8100)]`
- `nonmttbinstrategy=None`: Binning strategy class for non-MTT tests (e.g., BinSSB, NVLClass8dig, ServerClass8dig)
- `mttbinstrategy=None`: Binning strategy class for MTT tests (e.g., MTTBinSSB, MTTNVLClass8dig)
- `ctrstrategy=None`: **DEPRECATED** - Use nonmttctrstrategy and mttctrstrategy instead
- `nonmttctrstrategy=None`: Counter strategy class for non-MTT tests (e.g., CtrHBSB, CtrNVLClass8dig)
- `mttctrstrategy=None`: Counter strategy class for MTT tests (e.g., MTTCtrHBSB, MTTCtrNVLClass8dig)
- `defaults=BaseDefault`: Default class for port/param behaviors (BaseDefault, MTLdefault, NVLdefault, DMRdefault, CBRdefault, Sortdefault)
- `basenumrange=[]`: Range(s) for auto-basenumbering, e.g., `(1000, 2000)` or `[(1000, 1500), (2000, 2500)]`
- `forceflwfilegen=False`: Force generation of .flw file even if it exists
- `basenumberstrategy=None`: Strategy class for basenumber assignment (typically use default BaseNumber)
- `paramorder=None`: List of parameter names to prioritize in output order, e.g., `['Patlist', 'LevelsTc', 'TimingsTc']`
- `tosversion='tos3'`: TOS version - 'tos3' or 'tos4'
- `defaultthermalbin=None`: Default thermal bin (r4 port) as int or tuple: `90974401` or `(90974401, 90974501)`
- `defaultresetbin=None`: Default reset bin (r5 port) as int or tuple: `90441901` or `(90441901, 90451901)`
- `defaultrm1bin=None`: Default software/system bin (rm1 port) as `-HB`, 8-digit int, or string bin name
- `defaultrm2bin=None`: Default clamp/DPS bin (rm2 port) as `-HB`, 8-digit int, or string bin name
- `edcportctrbinrange=[]`: Counter range(s) for EDC and pass ports, e.g., `[(4400, 4450)]`
- `autobinignorelist=None`: List of bins to skip during auto-binning, e.g., `[4401, 4402, 90440101]`
- `deprecation_warning=False`: Show deprecation warnings for old Initialize variants
- `bom=None`: BOM identifier string for env file auto-detection
- `bindefovrd=None`: Dictionary to override bin name definitions, e.g., `{'98': 'b98_CUSTOM_NAME'}`
- `writehardbinstosbdef=None`: Whether to write hardbins to .sbdefs file (None=use default class setting)
- `writesoftbinstosbdef=None`: Whether to write softbins to .sbdefs file (None=use default class setting)
- `usebinctrfrommtpl=False`: Read bins/counters from existing MTPL instead of JSON files

**Example**:
```python
Initialize(
    'output/MyModule', 
    'MyModule',
    binrange=(4400, 4500),
    tosversion='tos4',
    nonmttbinstrategy=NVLClass8dig,
    nonmttctrstrategy=CtrNVLClass8dig,
    defaultrm1bin=-98,
    defaultrm2bin=-99,
    edcportctrbinrange=[(4400, 4450)],
    defaultthermalbin=90974401,
    defaultresetbin=90441901,
    paramorder=['Patlist', 'LevelsTc', 'TimingsTc']
)
```

### Flow
**Purpose**: Represents a DUTFlow (test sequence) in MTPL.

**Parameters**:
- `name`: Flow name (string)
- `*fitem_list`: Variable number of Fitem objects or lists of Fitem objects
- `dtag`: Optional flow alias (e.g., `dtag='INIT'` creates `@INIT`)

**Key Methods**:
- `get_items()`: Returns list of Fitem objects in the flow
- `write_lines()`: Generates MTPL output for the flow
- `get_registry()`: Class method returning all Flow objects

**Example**:
```python
Flow('MAIN', [
    Fitem(test1, r0=pFail(ret=0), r1=pPass()),
    Fitem(test2, r0=pFail(ret=0), r1=pPass())
], dtag='MAIN')
```

**Special Flow Types**:
- **ModuleFlow**: Used in ProgramFlows for module references
- **Floating**: For floating instances (not in a flow)
- **ConCurrentFlow**: For parallel execution flows

### Fitem (Flow Item)
**Purpose**: Wrapper around a test instance or composite flow with port definitions.

**Parameters**:
- `name`: Fitem name (use 'SAME' to match test instance name)
- `ti`: Test instance (BaseMethod) or Flow object
- `edc`: True for EDC (Error Detection and Correction), False for Kill (default: False)
- `r0`, `r1`, `r2`, `r3`, `r4`, `r5`: Port objects (pPass/pFail)
- `rm1`, `rm2`: Negative port objects
- `goto`: Goto target (string or Fitem/BaseMethod reference)
- `MinLoopDuration`: Loop duration expression
- `LoopCount`: Loop count expression
- `BreakLoopOn`: Break condition expression

**Example**:
```python
Fitem(
    name='MyTest_Item',
    ti=my_test_instance,
    edc=False,
    r0=pFail(setbin=-44, ret=0),
    r1=pPass(goto='NEXT'),
    rm1=pFail(setbin=-98, ret=-1),
    rm2=pFail(setbin=-99, ret=-2)
)
```

**Using _fitem for inline definition**:
```python
SomeTest(
    name='Test1',
    Patlist='pattern.plist',
    _fitem=Fitem(r0=pFail(setbin=-44), r1=pPass())
)
```

### BasePort (pPass and pFail)
**Purpose**: Defines port behavior for test results.

**Common Parameters**:
- `setbin`: Bin number (positive for manual, negative for auto with hardbin)
  - Positive: Direct bin assignment (e.g., `90440101` for 8-digit)
  - Negative: Auto-binning (e.g., `-44` means hardbin 44)
  - `AUTO` or `-1`: Fully automatic binning
- `ctr`: Counter number (8-digit for most strategies)
- `ret`: Return value (-2, -1, 0, 1, 2, etc.)
- `goto`: Goto target ('NEXT', test name, or Fitem/BaseMethod reference)
- `trialaction`: For MTT tests ('Exit', 'Next', or Spec expression)
- `setbinstring`: Direct bin string (overrides setbin)

**pPass** - Used for passing test results:
```python
pPass(ret=1)  # Default: return 1
pPass(goto='NEXT')  # Go to next test
pPass(setbin=90440101, ctr=44010001)  # With bin and counter
```

**pFail** - Used for failing test results:
```python
pFail(setbin=-44, ret=0)  # Auto-bin with HB 44, return 0
pFail(goto='ERROR_HANDLER')  # Go to specific test
pFail(setbin=90440101, ctr=44010001, ret=0)  # Manual bin/counter
```

**Port Naming Convention**:
- `r0`: Port 0 (typically fail port for Kill tests)
- `r1`: Port 1 (typically pass port)
- `r2`, `r3`, `r4`, `r5`: Additional positive ports
- `rm1`: Port -1 (software/system alarm)
- `rm2`: Port -2 (clamp/DPS alarm)

**Default Port Behavior** (varies by product):
- **Kill Test**: r0 typically returns 0, r1 goes to next
- **EDC Test**: All ports typically go to next
- **rm1/rm2**: Auto-populated by default classes (product-specific)

### BaseMethod
**Purpose**: Base class for all test instances (test methods).

**Common Pattern**:
```python
class MyTestMethod(BaseMethod):
    def __init__(self, name, Patlist, LevelsTc='lvl', **kwargs):
        vars_dict = locals()
        self._init(name, vars_dict)
```

**Special Parameters**:
- `_fitem`: Fitem object for inline port definition
- `_comment`: Comment(s) to include in MTPL output

**Key Methods**:
- `write_lines()`: Generates MTPL output for test instance
- `get_method_name()`: Returns test class name
- `counter_increment()`: Manages instance counters for reuse

### MultiTrial (MTT)
**Purpose**: Defines Multi-Trial tests that execute across trial variables.

**Parameters**:
- `name`: MTT test name
- `template`: BaseMethod test instance to be run in trial mode
- `trialvar`: Trial variable expression (e.g., 'IP_CPU_BASE::FlowDomain.Default')
- `exitaction`: Exit action on trial completion (default: 'Continue')
- `edcexitaction`: Exit action for EDC mode (default: 'Restore')
- Port definitions: `r0`, `r1`, `r2`, etc. (must match template ports)

**Example**:
```python
test_template = SomeTest(name='BaseTest', Patlist='pat.plist')

mtt_test = MultiTrial(
    name='MTT_Test',
    template=test_template,
    trialvar='IP_CPU_BASE::FlowDomain.GT',
    r0=pFail(trialaction='Exit', ret=-1),
    r1=pPass(trialaction='Next')
)
```

**NativeMultiTrial**: TOS4 variant without bin/counter generation in trial results.

## Important Classes

### Import
**Purpose**: Adds import statements to MTPL header.

**Example**:
```python
Import('MyUserVars.usrv')
Import('PatternFile.xml')
```

### MtplComment
**Purpose**: Adds comments to MTPL header section.

### MConfig
**Purpose**: Generates module.mconfig file for pattern configuration.

**Example**:
```python
MConfig(
    path='/path/to/patterns',
    rev='1.0',
    patch='0',
    plistinfo='pattern.plist',
    ip='IP_CPU'
)
```

### FlowDefs
**Purpose**: Defines flow assignments for ProgramFlows.

**Parameters**:
- `InitFlow`: Initialization flow name
- `MainFlow`: Main flow name
- `LotEndFlow`: Lot end flow name
- Other flow definitions

## Helper Classes

### Spec
**Purpose**: Outputs parameters without quotes (for expressions, uservars).

**Example**:
```python
Spec('TP_KNOB.ActivePins')  # Outputs: TP_KNOB.ActivePins (no quotes)
```

### TrialParamSpec
**Purpose**: Outputs trial parameters for MTT tests without quotes.

## Product-Specific Initialize Functions (Partial Classes)

Pymtpl provides pre-configured Initialize functions for different products using Python's `functools.partial`. These set appropriate defaults, strategies, and TOS versions.

### InitializeMTL
**Purpose**: Initialize for MTL products with legacy defaults.

**Pre-configured Settings**:
- `defaults=MTLdefault`
- `deprecation_warning=True`

**Default Behaviors** (from MTLdefault):
- Auto-populates rm1, rm2 ports with default bins
- Uses BinSSB binning (4-digit → 8-digit conversion)
- rm1 default: `b90989801_fail_FAIL_SYSTEM_SOFTWARE`
- rm2 default: `b90999901_fail_FAIL_DPS_ALARM`

**Usage**:
```python
InitializeMTL(
    'output/Module',
    'ModuleName',
    binrange=(4400, 4500)
    # Other parameters as needed
)
```

**Note**: Shows deprecation warning encouraging migration to product-specific initializers.

---

### InitializeNVL (Deprecated)
**Purpose**: Legacy NVL initialization - **DO NOT USE FOR NEW CODE**.

**Pre-configured Settings**:
- `defaults=NVLdefault`
- `tosversion='tos4'`
- `deprecation_warning=True`

**Replacement**: Use `InitializeNVLClass` or `InitializeNVLSort` instead.

**Deprecation Message**: Will raise error directing users to use InitializeNVLClass or InitializeNVLSort.

---

### InitializeNVLClass
**Purpose**: Initialize for NVL Class testing with 8-digit binning.

**Pre-configured Settings**:
- `defaults=NVLdefault`
- `nonmttbinstrategy=NVLClass8dig` - 8-digit bins with unique XX per HBSB
- `mttbinstrategy=MTTNVLClass8dig` - 4-digit counters for MTT
- `nonmttctrstrategy=CtrNVLClass8dig` - 8-digit counters (HBSBXXXX)
- `mttctrstrategy=MTTCtrNVLClass8dig` - 4-digit counters with pseudo-random start
- `tosversion='tos4'`

**Bin Format**: `90HBSBXX` (8-digit with unique XX per HBSB combo)

**Counter Format**: `HBSBXXXX` (4-digit HBSB + 4-digit unique counter)

**Usage**:
```python
InitializeNVLClass(
    'output/Module',
    'ModuleName',
    binrange=[(4400, 4450), (8001, 8100)],
    edcportctrbinrange=[(4400, 4450)],
    defaultthermalbin=90974401,
    defaultresetbin=90441901,
    defaultrm1bin=-98,
    defaultrm2bin=-99
)
```

**Best For**: NVL Class testing requiring unique 8-digit bins per test/port combination.

---

### InitializeNVLSort
**Purpose**: Initialize for NVL Sort testing where bin equals counter.

**Pre-configured Settings**:
- `defaults=Sortdefault`
- `nonmttbinstrategy=Sort8dig` - Full 8-digit bins used as-is
- `nonmttctrstrategy=CtrSort8dig` - Counter equals bin value
- `tosversion='tos4'`

**Bin Format**: Full 8-digit (e.g., `44010001`)

**Counter Format**: Same as bin (bin = counter)

**Port Handling**: rm1, rm2 require explicit definition or use defaultrm1bin/defaultrm2bin

**Usage**:
```python
InitializeNVLSort(
    'output/Module',
    'ModuleName',
    binrange=[(44000000, 44999999)],  # Full 8-digit range
    edcportctrbinrange=[(4400, 4450)],
    defaultrm1bin=90980100,  # Must be 8-digit
    defaultrm2bin=90990100
)
```

**Best For**: Sort testing where simple bin=counter relationship is needed.

---

### InitializeDMRClass
**Purpose**: Initialize for DMR/DCAI Class testing with server-style binning.

**Pre-configured Settings**:
- `defaults=DMRdefault`
- `nonmttbinstrategy=ServerClass8dig` - 8-digit bins for all ports
- `mttbinstrategy=MTTNVLClass8dig` - Standard MTT binning
- `nonmttctrstrategy=CtrDMRClass8dig` - Server counter strategy (no auto pass counters)
- `mttctrstrategy=MTTCtrNVLClass8dig` - Standard MTT counters
- `tosversion='tos4'`
- `usebinctrfrommtpl=True` - Read bins/counters from MTPL

**Special Features** (from DMRdefault):
- `write_hardbins_to_sbdef=True` - Writes hardbins to .sbdefs file
- `write_softbins_to_sbdef=True` - Writes softbins to .sbdefs file
- `skip_pass_counters=True` - No automatic counters for pass ports
- rm1/rm2 counter names match bin names (b→n substitution)
- Custom bin naming: `b98_FAIL_SOFTWARE_ALARM_OR_ZERO_BIN`, `b99_FAIL_HARDWARE_ERROR`

**Bin Format**: `90HBSBXX` (8-digit)

**Counter Format**: `90HBSBXX` for fail ports, `99HBSBXX` for pass ports (EDC range)

**rm1/rm2 Handling**: Can use `-HB`, 8-digit int, or full bin string
- `-98` → `b90980100_fail_FAIL_SYSTEM_SOFTWARE_n1`
- `90980100` → `b90980100_fail_FAIL_SYSTEM_SOFTWARE_n1`
- `'b90980100_fail_FAIL_SYSTEM_SOFTWARE_n1'` → used as-is

**Usage**:
```python
InitializeDMRClass(
    'output/Module',
    'ModuleName',
    binrange=[(4400, 4450)],
    edcportctrbinrange=[(4400, 4450)],
    defaultrm1bin=-98,  # or 90980100 or full string
    defaultrm2bin=-99
)
```

**Best For**: DMR Class testing with specific sbdef and counter requirements.

---

### InitializeCBRClass
**Purpose**: Initialize for CBR/AN TPI Class testing (CBR variant of DMR).

**Pre-configured Settings**:
- `defaults=CBRdefault`
- `nonmttbinstrategy=ServerClass8dig` - Same as DMR
- `mttbinstrategy=MTTNVLClass8dig` - Same as DMR
- `nonmttctrstrategy=CtrServerClass8dig` - Server counter strategy (WITH auto pass counters)
- `mttctrstrategy=MTTCtrNVLClass8dig` - Standard MTT counters
- `tosversion='tos4'`
- `usebinctrfrommtpl=True` - Read bins/counters from MTPL

**Differences from DMR**:
- `write_hardbins_to_sbdef=False` - Does NOT write hardbins to .sbdefs
- `write_softbins_to_sbdef=False` - Does NOT write softbins to .sbdefs
- `skip_pass_counters=False` - DOES generate automatic pass counters (unlike DMR)

**Usage**:
```python
InitializeCBRClass(
    'output/Module',
    'ModuleName',
    binrange=[(4400, 4450)],
    edcportctrbinrange=[(4400, 4450)],
    defaultrm1bin='b90980100_fail_FAIL_SYSTEM_SOFTWARE_n1',
    defaultrm2bin='b90990100_fail_FAIL_DPS_ALARM_n2'
)
```

**Best For**: CBR/AN TPI Class testing that needs similar structure to DMR but without sbdef generation.

---

## Product Initialize Comparison Table

| Product | Initialize Function | Bin Strategy | Counter Strategy | TOS | sbdef | Pass Counters | Bin=Counter |
|---------|-------------------|--------------|------------------|-----|-------|---------------|-------------|
| MTL | InitializeMTL | BinSSB (4→8) | CtrHBSB | tos3 | No | Yes | No |
| NVL Class | InitializeNVLClass | NVLClass8dig | CtrNVLClass8dig | tos4 | No | Yes | No |
| NVL Sort | InitializeNVLSort | Sort8dig | CtrSort8dig | tos4 | No | Yes | Yes |
| DMR Class | InitializeDMRClass | ServerClass8dig | CtrDMRClass8dig | tos4 | Yes | No | No |
| CBR Class | InitializeCBRClass | ServerClass8dig | CtrServerClass8dig | tos4 | No | Yes | No |

**Key**:
- **Bin Strategy**: How bins are formatted and assigned
- **Counter Strategy**: How counters are formatted and assigned
- **sbdef**: Whether .sbdefs file is generated with hardbins/softbins
- **Pass Counters**: Whether pass ports get automatic counters
- **Bin=Counter**: Whether bin value equals counter value

---

## Default Classes (Used by Initialize Functions)

### BaseDefault
Minimal defaults, manual port definition required. Base class for all other defaults.

**Settings**:
- No automatic port population
- No binning strategy
- No counter strategy
- Manual configuration required

### MTLdefault
Defaults for MTL products.

**Port Defaults**:
- rm1: `pFail(setbin=-98, ret=-1)` → `b90989801_fail_FAIL_SYSTEM_SOFTWARE`
- rm2: `pFail(setbin=-99, ret=-2)` → `b90999901_fail_FAIL_DPS_ALARM`

**MTT Port Defaults**:
- rm1: `pFail(trialaction='Exit', ret=-1)`
- rm2: `pFail(trialaction='Exit', ret=-2)`

### NVLdefault
Defaults for NVL products.

**Port Defaults** (for test instances):
- rm1: `pFail(setbin=-98, ret=-1)`
- rm2: `pFail(setbin=-99, ret=-2)`

**Port Defaults** (for composites):
- rm1: `pFail(ret=-1)` - No setbin
- rm2: `pFail(ret=-2)` - No setbin

**MTT Port Defaults**:
- rm1: `pFail(trialaction='Exit', ret=-1)`
- rm2: `pFail(trialaction='Exit', ret=-2)`

### DMRdefault
Defaults for DMR/DCAI products.

**Special Features**:
- `write_hardbins_to_sbdef=True`
- `write_softbins_to_sbdef=True`
- Custom bin name overrides via `bindefdefaults` dict
- Flexible rm1/rm2 bin handling (-HB, 8-digit, or string)

**Bin Name Overrides**:
- HB 98: `b98_FAIL_SOFTWARE_ALARM_OR_ZERO_BIN`
- HB 99: `b99_FAIL_HARDWARE_ERROR`
- SB 9801: `9801_FAIL_TESTCLASS_EXCEPTION_ERROR`

**Port Defaults** (test instances):
- rm1/rm2: Set based on `defaultrm1bin`/`defaultrm2bin` Initialize parameters

**Port Defaults** (composites):
- rm1: `pFail(ret=-1)` - No setbin
- rm2: `pFail(ret=-2)` - No setbin

### CBRdefault
Defaults for CBR/AN TPI products - similar to DMR but different sbdef handling.

**Differences from DMR**:
- `write_hardbins_to_sbdef=False`
- `write_softbins_to_sbdef=False`

**Otherwise**: Same as DMRdefault

### Sortdefault
Defaults for Sort testing.

**Port Defaults** (test instances):
- rm1/rm2: Set based on `defaultrm1bin`/`defaultrm2bin` or r0 setbin

**Logic**: If `defaultrm1bin`/`defaultrm2bin` not specified, derives from r0 setbin

**Port Defaults** (composites):
- rm1: `pFail(ret=-1)` - No setbin
- rm2: `pFail(ret=-2)` - No setbin

## Special Variables

- `required`: Sentinel value indicating parameter is required
- `optional`: Sentinel value indicating parameter is optional
- `AUTO`: Alias for `-1` for auto-binning

## Best Practices

1. **Always Initialize First**: Call Initialize() before creating any Fitems
2. **Unique Names**: Ensure DUTFlowItem names are unique
3. **Port Coverage**: Define all necessary ports (check product defaults)
4. **EDC vs Kill**: Be explicit about edc=True/False
5. **Bin Ranges**: Provide adequate bin ranges for auto-binning
6. **MTT Port Matching**: MTT ports must match template ports
7. **Use _fitem**: For cleaner inline test definitions
8. **Counter Uniqueness**: Manually specified counters must be unique

## Common Patterns

### Simple Test Flow
```python
Initialize('output', 'Module', binrange=(4400, 4500))

test1 = TestMethod(name='T1', Patlist='p1.plist', _fitem=Fitem(
    r0=pFail(setbin=-44), r1=pPass()
))

test2 = TestMethod(name='T2', Patlist='p2.plist', _fitem=Fitem(
    r0=pFail(setbin=-44), r1=pPass()
))

Flow('MAIN', [test1, test2])
```

### Composite Flow
```python
subflow_items = [test1, test2, test3]
subflow = Flow('SUBFLOW', subflow_items)

main_items = [
    Fitem('SubflowCall', subflow, r0=pFail(ret=0), r1=pPass())
]
Flow('MAIN', main_items)
```

### Loop with Break Condition
```python
Fitem(
    test,
    LoopCount='10',
    BreakLoopOn='result == 0',
    r0=pFail(ret=0),
    r1=pPass()
)
```
