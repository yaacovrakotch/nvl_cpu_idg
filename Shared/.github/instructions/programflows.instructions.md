---
applyTo: "**/POR_TP/**/ProgramFlowsTestPlan/*.py"
---

# ProgramFlows Class Documentation for AI Agents

## Overview

The `ProgramFlows` class is a powerful tool in the pymtpl framework that generates ProgramFlows.mtpl files from a human-readable text configuration. It automatically creates DUTFlow blocks with proper flow item sequencing, port routing, and IP scope handling for semiconductor ATE (Automatic Test Equipment) test programs.

## Key Concepts

### 1. Basic Structure
- **ProgramFlows.mtpl**: The generated output file containing DUTFlow definitions
- **Configuration Text**: Human-readable input format specifying flow relationships
- **SubFlows**: Named sequences of test modules that can be reused
- **MainFlow**: The top-level flow (usually "MAIN") that orchestrates execution

### 2. Core Classes
- `ProgramFlows`: Main class for generating program flows
- `Flow`: Represents a DUTFlow block in the output
- `Fitem`: Individual flow items within a Flow
- `ModuleFlow`: Special flow type for referencing test modules
- `Initialize`: Setup class for output configuration

## Configuration Text Format

### Basic Syntax
```
<subflow_name>    <module_name>    <port_definitions>...
```

### Example Configuration
```python
text = '''
START_SubFlow               TPI_FLWFLGS_XXX           r2p  r3f r4f1
START_SubFlow               TPI_BASE_XXX              r3f6 rm4pm7

SHAREDRAILSNOM_SubFlow      TPI_FLWFLGS_XXX           r2p2

# The order follows MAIN definition
MAIN                        SHAREDRAILSNOM_SubFlow
MAIN                        START_SubFlow
'''
```

## Port Syntax Reference

### Port Format: `r<result><pass/fail><return_value/goto>`

| Syntax | Description | Example |
|--------|-------------|---------|
| `r2p` | Result 2, Pass, Return 1 (default) | Most common pass port |
| `r2p2` | Result 2, Pass, Return 2 | Pass with specific return value |
| `r2f` | Result 2, Fail, Return 0 (default) | Basic fail port |
| `r2f3` | Result 2, Fail, Return 3 | Fail with specific return value |
| `r2pn` | Result 2, Pass, Goto Next | Continue to next flow item |
| `r2fn` | Result 2, Fail, Goto Next | Fail but continue |
| `r2f:<modname>` | Result 2, Fail, Goto module | Jump to specific module |
| `rm1p` | Result -1, Pass, Return 1 | Negative result port |
| `r0x0` | Remove default r0 port | Delete port (Jonathan request) |

### Port Defaults by Flow Type

**SubFlows (non-MAIN):**
```python
defaults = {
    'rm2': pFail(ret=-2),
    'rm1': pFail(ret=-1), 
    'r0': pFail(ret=0)
}
```

**MainFlow:**
```python
defaults = {
    'r0': pFail(ret=0)
}
```

## Usage Patterns

### 1. Basic Usage
```python
from pymtpl.core import Initialize
from pymtpl.helpers import ProgramFlows

# Initialize output
Initialize('./MyProgramFlows', 'MyModule')

# Define flow configuration
program_flows = '''
START_SubFlow       TPI_MODULE_A      r2p r3f
START_SubFlow       TPI_MODULE_B      r2pn

MAIN               START_SubFlow      r2f:ALARM_SubFlow
MAIN               ALARM_SubFlow
'''

# Generate flows
ProgramFlows().main(program_flows, 'MAIN')
```

### 2. IP-Scoped Flows (ip=False, default)
```python
# Automatically adds IP scope (e.g., IP_CPU::)
ProgramFlows().main(text, 'MAIN', ip=False)
```

### 3. ProgramFlows without IP Scope (ip=True)
```python
# No automatic IP scope addition
ProgramFlows().main(text, 'MAIN', ip=True)
```

### 4. Using DEFAULTS
```python
text = '''
# Override default ports for entire subflow
START_SubFlow       DEFAULTS          r0f1
START_SubFlow       TPI_MODULE_A      r2pn
START_SubFlow       TPI_MODULE_B

MAIN               DEFAULTS          rm1f:ALARM_SubFlow
MAIN               START_SubFlow     r0pn r2p:END_SubFlow
'''
```

## Special Module Types

### 1. Direct Module Calls
```python
# Direct module call with :: syntax
MAIN    TPI_XXX::TPI_XXX_MAIN    r2f:ALARM r3f:PRLCPU
```

### 2. Parallel Flows
```python
# Parallel flow with $ prefix
MAIN    $PRLCPU    r2f3
```

### 3. SubFlow References
```python
# Reference to another subflow
MAIN    START_SubFlow    r2f:END_SubFlow
```

## Generated Output Structure

### Example Input:
```python
text = '''
START_SubFlow       TPI_FLWFLGS_XXX    r2p r3f
START_SubFlow       TPI_BASE_XXX       r2pn

MAIN               START_SubFlow       r2f2
'''
```

### Generated Output:
```mtpl
DUTFlow START_SubFlow {
 DUTFlowItem TPI_FLWFLGS_XXX_START IP_CPU::TPI_FLWFLGS_XXX::TPI_FLWFLGS_XXX_START {
  Result -2 { Property PassFail = "Fail"; Return -2; }
  Result -1 { Property PassFail = "Fail"; Return -1; }
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; GoTo TPI_BASE_XXX_START; }
  Result 2 { Property PassFail = "Pass"; Return 1; }
  Result 3 { Property PassFail = "Fail"; Return 0; }
 }
 DUTFlowItem TPI_BASE_XXX_START TPI_BASE_XXX::TPI_BASE_XXX_START {
  Result -2 { Property PassFail = "Fail"; Return -2; }
  Result -1 { Property PassFail = "Fail"; Return -1; }
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; Return 1; }
  Result 2 { Property PassFail = "Pass"; GoTo NEXT; }
 }
}
DUTFlow MAIN {
 DUTFlowItem START_SubFlow START_SubFlow {
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; Return 1; }
  Result 2 { Property PassFail = "Fail"; Return 2; }
 }
}
```

## Common Modification Patterns

### 1. Adding New Module to Existing SubFlow
```python
# Before:
START_SubFlow       TPI_MODULE_A      r2p

# After:
START_SubFlow       TPI_MODULE_A      r2p
START_SubFlow       TPI_MODULE_B      r2pn  # Add new module
```

### 2. Changing Port Routing
```python
# Before:
MAIN    START_SubFlow    r2f

# After:  
MAIN    START_SubFlow    r2f:ALARM_SubFlow  # Route to specific subflow
```

### 3. Adding New SubFlow
```python
# Add new subflow definition
NEW_SubFlow         TPI_NEW_MODULE    r2p r3f

# Reference in MAIN
MAIN               NEW_SubFlow        r2f:END_SubFlow
```

### 4. Removing Ports
```python
# Remove default r0 port
START_SubFlow       TPI_MODULE_A      r2p r0x0
```

## Error Handling and Validation

### Common Errors to Avoid:
1. **Invalid Port Syntax**: Ensure ports match regex `r\d+|rm\d+[pfx](n|m\d+|\d+)?(:\S+)?`
2. **Duplicate DUTFlowItem Names**: Each flow item name must be unique
3. **Missing TopFlow**: Always define the top-level flow (MAIN/INIT)
4. **Circular References**: Avoid goto loops between subflows

### Validation Example:
```python
# Good:
START_SubFlow       TPI_MODULE_A      r2p r3f
MAIN               START_SubFlow      r2f

# Bad - Invalid port syntax:
START_SubFlow       TPI_MODULE_A      r2invalid  # Error!

# Bad - Missing MAIN:
START_SubFlow       TPI_MODULE_A      r2p  # Error - no top flow!
```

## Advanced Features

### 1. FlowDefs Integration
```python
from pymtpl.core import FlowDefs

# Define flow mappings
FlowDefs(InitFlow='INIT', MainFlow='MAIN')
```

### 2. Multi-IP Support
```python
# Different IP scopes automatically applied based on module mapping
START_SubFlow       CPU_MODULE        r2p    # -> IP_CPU::
START_SubFlow       PCH_MODULE        r2p    # -> IP_PCH::
```

### 3. Complex Port Routing
```python
text = '''
MAIN    START_SubFlow    r1p:SUCCESS_SubFlow r2f:RETRY_SubFlow r0f:FAIL_SubFlow
MAIN    SUCCESS_SubFlow  r1p
MAIN    RETRY_SubFlow    r1p:START_SubFlow r0f:FAIL_SubFlow  
MAIN    FAIL_SubFlow     
'''
```

## Debugging and Testing

### 1. Use Compact Class for Testing
```python
from pymtpl.helpers import Compact

# Generate and compare output
expect = '''
DUTFlow MAIN {
 DUTFlowItem START_SubFlow START_SubFlow {
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; Return 1; }
 }
}
'''
assert str(Compact('output.mtpl')) == expect
```

### 2. Enable Logging
```python
from gadget.pylog import log
log.info('Flow generation completed')
```

## Complete Working Example

```python
from pymtpl.core import Initialize
from pymtpl.helpers import ProgramFlows 

# Initialize output file
Initialize('IPC_FLOWS', 'IPC_FLOWS', tosversion="tos4")

# Define standard port configurations
ipc_stdports = 'rm2fm2 rm1fm1 r0f20'
ipcflwflgs_stdports = 'rm2fm2 rm1fm1 r0f20 r2p1'

# Define program flows configuration
MAIN_code = f'''
# Startup flows
STARTCPUNOM_SubFlow       TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
STARTCPUNOM_SubFlow       FUS_FUSECFG_CXX      {ipc_stdports}
STARTCPUNOM_SubFlow       TPI_PWRCTRL_CXX      rm2fm2 rm1fm1 r0f20 r2p1
STARTCPUNOM_SubFlow       IPC::DRV_RESET_CXX::DRV_BASIC_CXX_STARTCPUNOM        {ipc_stdports}

# Begin flows
BEGINCPU_SubFlow          TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
BEGINCPU_SubFlow          TPI_DIERCVRY_CXX     {ipc_stdports}
BEGINCPU_SubFlow          CLK_MAIN_CXXX        {ipc_stdports}
BEGINCPU_SubFlow          SCN_CORE_CX816       rm2fm2 rm1fm1 r0f20 r2p1

# Functional test flows  
F1XCCF_SubFlow            TPI_FLWFLGS_CXX      {ipcflwflgs_stdports}
F1XCCF_SubFlow            ARR_CCF_CXX          rm2fm2 rm1fm1 r0f20 r2p1
F1XCCF_SubFlow            SCN_UNCORE_CX816     rm2fm2 rm1fm1 r0f20 r2p1
F1XCCF_SubFlow            FUN_CCF_CX816        rm2fm2 rm1fm1 r0f20 r2p1

# Parallel execution flows
STARTPRL0CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_FIRST_STARTPRL0CPU        rm2fm2 rm1fm1 r0f20
STARTPRL0CPU_SubFlow      STARTCPUNOM_SubFlow        rm2fm2 rm1fm1 r0f20 r20f20
STARTPRL0CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_LAST_STARTPRL0CPU        rm2fm2 rm1fm1 r0f20

BEGINPRL0CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_FIRST_BEGINPRL0CPU        rm2fm2 rm1fm1 r0f20
BEGINPRL0CPU_SubFlow      BEGINCPU_SubFlow     rm2fm2 rm1fm1 r0f20 r20f20
BEGINPRL0CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_LAST_BEGINPRL0CPU        rm2fm2 rm1fm1 r0f20

SPEEDPRL0CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_FIRST_SPEEDPRL0CPU        rm2fm2 rm1fm1 r0f20
SPEEDPRL0CPU_SubFlow      F1XCCF_SubFlow        rm2fm2 rm1fm1 r0f20 r20f20
SPEEDPRL0CPU_SubFlow      IPC::TPI_TIMETRK_CXX::TPI_TIMETRK_CXX_LAST_SPEEDPRL0CPU        rm2fm2 rm1fm1 r0f20
'''

# Generate the flows (note: topflow is 'CPU_ProgramFlows', ip=False for auto IP scoping)
ProgramFlows().main(MAIN_code, 'CPU_ProgramFlows', ip=False)
```

This will generate `IPC_FLOWS.mtpl` with properly formatted DUTFlow blocks ready for use in ATE test programs.

## Best Practices for AI Agents

1. **Always validate port syntax** before generation
2. **Use descriptive subflow names** that indicate their purpose
3. **Define error handling flows** (ALARM_SubFlow, FAIL_SubFlow)
4. **Group related modules** into logical subflows
5. **Test with simple configurations** before complex ones
6. **Use DEFAULTS** strategically to reduce repetition
7. **Document complex port routing** with comments
8. **Maintain consistent naming conventions** across flows

## Integration with Existing Test Programs

When modifying existing ProgramFlows:

1. **Analyze current flow structure** before making changes
2. **Preserve existing port relationships** unless specifically changing them
3. **Test incremental changes** rather than wholesale replacements
4. **Validate against existing test patterns** in the codebase
5. **Consider downstream dependencies** when changing flow names or ports

This documentation provides the foundation for AI agents to effectively use the ProgramFlows class to generate and modify program flow configurations in the pymtpl framework.