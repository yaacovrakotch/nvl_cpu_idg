---
applyTo: "**/pymtpl/mtpl2py.py"
---
# MTPL to Python Converter (mtpl2py.py)

## Purpose
Reverse engineers existing MTPL files back into Python pymtpl code. Useful for converting legacy MTPL or understanding existing test programs.

## Key Class: GenPy

### Initialization
```python
from pymtpl.mtpl2py import GenPy

converter = GenPy('/path/to/file.mtpl')
```

**Constructor Parameters**:
- `mtplfile`: Path to MTPL file to convert

**Automatic Detection**:
- Finds TP directory (3 levels up from MTPL)
- Locates env file automatically
- Can override with `OPT.env`

### Configuration

#### Product-Specific Defaults

**BaseDefault** (Manual):
```python
config = {
    'initialize': 'Initialize',
    'autosetbins': False,         # Keep original bins
    'autosetcounters': False,     # Keep original counters
    'autogeneratestandardports': False,  # Write all ports
    'importbinlimits': False      # Don't import bin limits
}
```

**DMRClassDefault**:
```python
config = {
    'initialize': 'InitializeDMRClass',
    'autosetbins': True,          # Convert to auto-binning
    'autosetcounters': True,      # Remove counters
    'autogeneratestandardports': True,  # Skip standard ports
    'importbinlimits': True       # Import bin limits from JSON
}
```

**CBRClassDefault**: Same as DMRClassDefault but uses `InitializeCBRClass`

**Setting Product**:
```python
# Via command line
python mtpl2py.py input.mtpl -product dmrclass

# Or set OPT.product in code
OPT.product = 'dmrclass'
```

### Main Workflow

```python
converter = GenPy('input.mtpl')
converter.main()  # Generates input.py
```

**Steps**:
1. Parse MTPL using TP's MTPL reader
2. Extract DUTFlow map and test instances
3. Generate Initialize statement
4. Generate Import statements
5. Generate test method definitions
6. Generate Fitem definitions with ports
7. Generate Flow definitions
8. Write to .py file

## Key Methods

### get_dutflow_dict_and_modulename()
Reads MTPL and creates internal data structures.

**Creates**:
- `self.df`: DUTFlow map (all flows and items)
- `self.df_edckill`: EDC/Kill status map
- `self.modulename`: Extracted module name
- `self.commentdict`: ##EDC## comment locations

### write_initialize_line()
Generates Initialize statement with imports.

**Output Example**:
```python
from pymtpl.por_methods import TestMethod1, TestMethod2
from pymtpl.core import Flow, Fitem, pPass, pFail, InitializeDMRClass, ...

InitializeDMRClass('Test_MyModule', 'MyModule', binrange=bin_limits, ...)
```

**With Bin Limits** (DMR/CBR):
```python
from pymtpl.helpers import get_bin_limits_from_json

bin_limits = get_bin_limits_from_json('MyModule')
InitializeDMRClass('Test_MyModule', 'MyModule', binrange=bin_limits, ...)
```

### write_import_lines()
Extracts Import statements from MTPL that aren't test methods.

**Example Output**:
```python
Import('MyUserVars.usrv')
Import('PatternConfig.xml')
```

### write_testmethod_info_lines()
Generates test method definition.

**For Regular Tests**:
```python
TestMethod(name='MyTest',
    Patlist='pattern.plist',
    LevelsTc='levels.tpl',
    TimingsTc='timings.tpl',
    SomeParam=Spec('UserVars.MyVar')
)
```

**For MTT Tests**:
```python
NativeMultiTrial(name='MTT_Test',
    trialvar='IP_CPU_BASE::FlowDomain.GT',
    exitaction="Continue",
    template=TestMethod(name='MTT_Test',
        Patlist='pattern.plist',
        SomeParam=TrialParamSpec('Trial.Param')
    ),
    # Port definitions follow
)
```

**Parameter Handling**:
- **Literals** (strings): Wrapped in quotes
- **Expressions**: Wrapped in `Spec()`
- **Trial Parameters**: Wrapped in `TrialParamSpec()`
- **Numbers**: Written as-is
- **Paths**: Backslashes escaped

### write_portinfo_lines()
Generates port definitions for Fitem.

**For Regular Tests**:
```python
    _fitem=Fitem(
        r0=pFail(setbin=90440101, ctr=44010001, ret=0),
        r1=pPass(goto='NEXT'),
        rm1=pFail(ret=-1),
        rm2=pFail(ret=-2)
    )
)
```

**For MTT Tests**:
```python
    r0=pFail(setbin=4401, ctr=4401, trialaction='Exit', ret=-1),
    r1=pPass(trialaction='Next')
)
```

**Port Optimization** (when `autogeneratestandardports=True`):
- Skips r1 if it's default pass port going to NEXT
- Skips rm1 if it's standard -1 return
- Skips rm2 if it's standard -2 return
- Reduces generated code for standard patterns

### Bin Extraction

#### get_bin()
Extracts bin from SetBin string.

**For Non-MTT** (8-digit):
```python
# Input: "SoftBins.b90440101_fail_Module_Test"
# Output: 90440101 (or -44 if autosetbins=True)
```

**For MTT** (4-digit):
```python
# Input: '"b" + FlowMatrix.bin + "4401_fail_..."'
# Output: 4401
```

**Auto-Binning Conversion**:
When `autosetbins=True`, converts 8-digit to hardbin:
```python
90440101 → -44  # Extracts HB from positions 2-3
```

### Counter Extraction

#### get_counter()
Extracts counter from IncrementCounters string.

**For Non-MTT**:
```python
# Input: "IncrementCounters Module::n44010001_fail_Test_0"
# Output: 44010001
```

**For MTT**:
```python
# Input: '...::p" + FlowMatrix.bin + "4401_pass_...'
# Output: 4401
```

### Flow Generation

#### write_flow_items()
Generates complete Flow definitions.

**Output Structure**:
```python
##############################################################
##################### MAIN 
##############################################################
MAIN = Flow('MAIN', [
    TestMethod1(...),
    TestMethod2(...),
    ...
], dtag='MAIN')
```

**Handles**:
- Multiple flows in order
- DTAGs (@INIT, @EDC, etc.)
- EDC vs Kill test detection
- Composite flows
- Flow item naming
- Next item detection for goto='NEXT'

## Usage Patterns

### Basic Conversion
```python
from pymtpl.mtpl2py import GenPy

# Convert MTPL to Python
converter = GenPy('path/to/module.mtpl')
converter.main()
# Creates path/to/module.py
```

### With Product Specification
```python
from gadget.helperclass import OPT
from pymtpl.mtpl2py import GenPy

OPT.product = 'dmrclass'  # or 'cbrclass'
converter = GenPy('path/to/module.mtpl')
converter.main()
```

### With Custom Env File
```python
from gadget.helperclass import OPT
from pymtpl.mtpl2py import GenPy

OPT.env = '/path/to/EnvironmentFile.env'
converter = GenPy('path/to/module.mtpl')
converter.main()
```

## Generated Code Features

### Spec vs Literals
**Literals** (wrapped in quotes):
```python
Patlist='pattern.plist'
```

**Expressions** (wrapped in Spec):
```python
Patlist=Spec('UserVars.PatternName')
```

**Detection**: Uses TP's ttype info to determine literal vs expression

### Trial Parameters
For MTT tests, trial parameters detected by `_MTT()` wrapper:
```python
# MTPL: SomeParam = _MTT(Trial.Value);
# Python: SomeParam=TrialParamSpec('Trial.Value')
```

### Composite Flow Detection
Automatically detects when test instance is actually a composite:
```python
# If test instance is a flow
Fitem('SAME', SubFlowName, r0=pFail(ret=0), r1=pPass())
```

### EDC Detection
Reads `@EDC` attribute and ##EDC## comments:
```python
# EDC test
Fitem(test, edc=True, r0=pFail(setbin=..., goto='NEXT'))

# ##EDC## bins extracted from comments
```

## Output File Structure

```python
# 1. Imports and Initialize
from pymtpl.por_methods import Test1, Test2
from pymtpl.core import Flow, Fitem, pPass, pFail, Initialize, ...

Initialize('output', 'Module', ...)

# 2. Non-test Imports
Import('file1.usrv')
Import('file2.xml')

# 3. Flow Definitions (one per flow)
##############################################################
##################### INIT 
##############################################################
INIT = Flow('INIT', [
    Test1(...),
    Test2(...),
])

##############################################################
##################### MAIN 
##############################################################
MAIN = Flow('MAIN', [
    Test3(...),
    Test4(...),
])
```

## Advanced Features

### Goto Resolution
Converts MTPL GoTo to Python goto:
```python
# If going to next test
goto='NEXT'

# If going to specific test
goto='TestName'

# Optimizes away redundant gotos
```

### Return Value Optimization
Skips default return values:
```python
# Default pass return (r1=1) - not written
# Default fail return (kill r0=0) - not written
# Non-default returns - explicitly written
ret=2  # Written because not default
```

### Port Parameter Ordering
Consistent parameter order in ports:
1. `ret` (if specified)
2. `setbin` (if specified)
3. `ctr` (if specified)
4. `goto` (if specified)
5. `trialaction` (for MTT)

### Test Template Tracking
Automatically tracks all test templates used:
```python
# Collected during parsing
self.testtemplates = {'TestMethod1', 'TestMethod2', ...}

# Used in import statement
from pymtpl.por_methods import TestMethod1, TestMethod2
```

## Integration with Pymtpl

After conversion, the generated Python file can be run with pymtpl:
```python
# Generated file: module.py
python module.py
# Regenerates module.mtpl
```

Should produce functionally equivalent MTPL (some formatting differences expected).

## Limitations & Notes

1. **Comment Preservation**: Comments in MTPL are not preserved in Python
2. **Formatting**: Generated code may have different formatting than hand-written
3. **Expression Detection**: Relies on TP's ttype information (requires valid stpl)
4. **EDC Comments**: Only ##EDC## SetBin comments are parsed, not other comments
5. **Concurrent Flows**: Special handling for ConCurrentFlow blocks
6. **MTT Ports**: Assumes MTT test and Fitem have matching port definitions

## Best Practices

1. **Verify TP Structure**: Ensure TP has valid stpl before conversion
2. **Check Product**: Set correct product for optimal output
3. **Review Generated Code**: Manual review recommended after conversion
4. **Test Round-Trip**: Run generated Python through pymtpl to verify
5. **Bin Limits**: For DMR/CBR, ensure BinLimits.json exists before conversion

## Common Issues

### Missing Test Templates
**Symptom**: Import errors for test methods
**Solution**: Ensure test templates are in por_methods.py or accessible path

### Expression vs Literal
**Symptom**: Quotes around expressions or missing quotes on literals
**Solution**: Check ttype information in TP's MTPL parser

### Path Escaping
**Symptom**: Invalid escape sequences in paths
**Solution**: Code auto-escapes backslashes (`\` → `\\`)

### Port Mismatch
**Symptom**: MTT and Fitem ports don't match
**Solution**: Review generated MTT definition, may need manual adjustment
