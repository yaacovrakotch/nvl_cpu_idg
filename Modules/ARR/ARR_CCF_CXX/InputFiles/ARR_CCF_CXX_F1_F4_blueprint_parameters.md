# ARR_CCF_CXX Blueprint Parameter Mappings (F1-F4)

## Overview
This file defines the input parameters and expansion rules for the ARR_CCF_CXX F1-F4 blueprint.

## Input Parameters

### Corner Definitions
```yaml
CORNERS:
  - F1
  - F2
  - F3
  - F4
```

### Frequency Mappings
```yaml
FREQ_MAP:
  F1: 1200  # MHz
  F2: 1500  # MHz
  F3: 2200  # MHz
  F4: 3000  # MHz
```

### Base Numbers Mappings
```yaml
BASE_NUMBERS:
  F1:
    SSA_LLCSRAM: 12334
    LSA_CBOA: 12335
    LSA_LLCRF: 12336
  F2:
    SSA_LLCSRAM: 12337
    LSA_CBOA: 12338
    LSA_LLCRF: 12340
  F3:
    SSA_LLCSRAM: 12341
    LSA_CBOA: 12342
    LSA_LLCRF: 12343
  F4:
    SSA_LLCSRAM: 12753  # Note: Different range!
    LSA_CBOA: 12755
    LSA_LLCRF: 12754
```

### VminResult Mappings
```yaml
VMIN_RESULT:
  F1:
    SSA_LLCSRAM: "ARR_CCF_LLCSRAM_F1_VMIN"
    LSA_CBOA: "ARR_CCF_CBOA_F1_VMIN"
    LSA_LLCRF: "ARR_CCF_LLCRF_F1_VMIN"
  F2:
    SSA_LLCSRAM: "ARR_CCF_LLCSRAM_F2_VMIN"
    LSA_CBOA: "ARR_CCF_CBOA_F2_VMIN"
    LSA_LLCRF: "ARR_CCF_LLCRF_F2_VMIN"
  F3:
    SSA_LLCSRAM: "ARR_CCF_LLCSRAM_F3_VMIN"
    LSA_CBOA: "ARR_CCF_CBOA_F3_VMIN"
    LSA_LLCRF: "ARR_CCF_LLCRF_F3_VMIN"
  F4:
    SSA_LLCSRAM: "ARR_CCF_LLCSRAM_F4_VMIN"
    LSA_CBOA: "ARR_CCF_CBOA_F4_VMIN"
    LSA_LLCRF: "ARR_CCF_LLCRF_F4_VMIN"
```

## Substitution Rules

### Flow Name Pattern
```
ARR_CCF_CXX_F<corner>XCCF
```
**Example**:
- F1 → ARR_CCF_CXX_F1XCCF
- F2 → ARR_CCF_CXX_F2XCCF
- F3 → ARR_CCF_CXX_F3XCCF
- F4 → ARR_CCF_CXX_F4XCCF

### Test Instance Name Patterns
```
SSA_CCF_VMIN_K_F<corner>XCCF_X_X_F<corner>_<freq>_LLCSRAM_MTT
LSA_CCF_VMIN_K_F<corner>XCCF_X_X_F<corner>_<freq>_CBOA_MTT
LSA_CCF_VMIN_K_F<corner>XCCF_X_X_F<corner>_<freq>_LLCRF_MTT
```

### Parameter Substitution Patterns

| Parameter | Pattern | F1 Example | F2 Example |
|-----------|---------|------------|------------|
| CornerIdentifiers | `"CCF0@F<corner>"` | `"CCF0@F1"` | `"CCF0@F2"` |
| BaseNumbers | See BASE_NUMBERS map | `"12334"` | `"12337"` |
| Patlist | `arr_cdie_f<corner>xccf_...` | `arr_cdie_f1xccf_...` | `arr_cdie_f2xccf_...` |
| SetPoints Prefix | `PSPRE.CLR_F<corner>` | `PSPRE.CLR_F1` | `PSPRE.CLR_F2` |
| SetPoints Postfix | `PSPOST.CLR_F<corner>` | `PSPOST.CLR_F1` | `PSPOST.CLR_F2` |
| Ring Frequency | `CCF_F<corner>_FREQ` | `CCF_F1_FREQ` | `CCF_F2_FREQ` |
| Voltage Dropout | `DROPOUT.CLR_F<corner>` | `DROPOUT.CLR_F1` | `DROPOUT.CLR_F2` |
| Start Voltages Retry | `StartVoltagesForRetryF<corner>` | `StartVoltagesForRetryF1` | `StartVoltagesForRetryF2` |
| Start Voltages Offset | `StartVoltagesOffsetF<corner>` | `StartVoltagesOffsetF1` | `StartVoltagesOffsetF2` |
| VminResult | See VMIN_RESULT map | `"ARR_CCF_LLCSRAM_F1_VMIN"` | `"ARR_CCF_LLCSRAM_F2_VMIN"` |

## Special Rules

### Rule 1: EndVoltageLimits (Corner-Specific)
```python
if corner == "F1":
    EndVoltageLimits = ARR_CCF_Rules.QA_HOT_Default(
        __shared__::FlowMatrixSingular.CCF_HIGH_SEARCH_VALUE,
        __shared__::FlowMatrixSingular.CR_LFM_VMIN_RAIN_KILL,
        __shared__::FlowMatrixSingular.CCF_HIGH_SEARCH_VALUE
    )
else:  # F2, F3, F4
    EndVoltageLimits = __shared__::FlowMatrixSingular.CCF_HIGH_SEARCH_VALUE
```

### Rule 2: SetPointsPreInstance (Test-Type Specific)
```python
if test_type == "SSA":
    # Include atomfreq_0
    SetPointsPreInstance = (
        PSPRE.CLR_F<corner> + "," +
        "MCdrv:corefreq:" + __shared__::FlowMatrixSingular.CR_F1_FREQ + "GHz," +
        "MCdrv:ringfreq_0:" + __shared__::FlowMatrixSingular.CCF_F<corner>_FREQ + "GHz," +
        "MCdrv:atomfreq_0:" + __shared__::FlowMatrixSingular.AT_F1_FREQ + "GHz"
    )
else:  # LSA (CBOA, LLCRF)
    # No atomfreq_0
    SetPointsPreInstance = (
        PSPRE.CLR_F<corner> + "," +
        "MCdrv:corefreq:" + __shared__::FlowMatrixSingular.CR_F1_FREQ + "GHz," +
        "MCdrv:ringfreq_0:" + __shared__::FlowMatrixSingular.CCF_F<corner>_FREQ + "GHz"
    )
```

### Rule 3: Flow Structure (Always 3 Tests)
```python
# Each flow contains exactly 3 test instances in this order:
tests = [
    "SSA_CCF_VMIN_K_F{corner}XCCF_X_X_F{corner}_{freq}_LLCSRAM_MTT",  # Position 1
    "LSA_CCF_VMIN_K_F{corner}XCCF_X_X_F{corner}_{freq}_CBOA_MTT",     # Position 2
    "LSA_CCF_VMIN_K_F{corner}XCCF_X_X_F{corner}_{freq}_LLCRF_MTT"     # Position 3
]
```

## Constant Parameters (Identical Across All Corners)

The following parameters remain constant and should NOT be substituted:

```yaml
CONSTANTS:
  BypassPort: -1
  ExecutionMode: "SearchWithScoreboard"
  TestMode: "SingleVmin"
  VoltageTargets: "CCF"
  RecoveryMode: "NoRecovery"
  StepSize: 0.01
  FlowIndex: __shared__::FlowMatrix.FlowIndex  # Note: NOT FlowMatrixSingular
  CoreFrequency: __shared__::FlowMatrixSingular.CR_F1_FREQ  # Constant F1
  AtomFrequency: __shared__::FlowMatrixSingular.AT_F1_FREQ  # Constant F1
  StartVoltages: __shared__::FlowMatrixSingular.CR_LOW_SEARCH_VALUE
  FeatureSwitchSettings: ARR_CCF_CXX_Specs.FeatureSwitchNonMTT
  FivrCondition: ARR_CCF_CXX_Specs.FivrConditionNom
  ForwardingMode: ARR_CCF_CXX_Specs.ForwardingMode_Kill
  LevelsTc: "IPC::ARR_CCF_CXX::arr_cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC_ARR_MBIST_min_lvl"
  TimingsTc: ARR_CCF_CXX_Specs.timings_Rules
  DtsConfiguration: ARR_CCF_CXX_Specs.DTSConfig_Rules
  PatternNameCounterIndexes: ARR_CCF_CXX_Specs.PatternMap
  SetPointsPlistParamName: "Patlist"
  FailCaptureCount: 1
  ScoreboardEdgeTicks: __shared__::Specs.CHK_EDGE_TICK
  MaxFailsNum: __shared__::Specs.CHK_MAX_FAILS
  LimitGuardband: __shared__::GBVars.LimitGuardband
```

## Expansion Algorithm (Pseudocode)

```python
def expand_blueprint(corners=["F1", "F2", "F3", "F4"]):
    flows = []
    
    for corner in corners:
        freq = FREQ_MAP[corner]
        
        # Create flow
        flow = create_flow(f"ARR_CCF_CXX_F{corner}XCCF")
        
        # Create 3 test instances
        for test_type in ["SSA_LLCSRAM", "LSA_CBOA", "LSA_LLCRF"]:
            test = create_test_instance(
                name=f"{test_type.split('_')[0]}_CCF_VMIN_K_F{corner}XCCF_X_X_F{corner}_{freq}_{test_type.split('_')[1]}_MTT",
                corner=corner,
                freq=freq,
                test_type=test_type,
                base_number=BASE_NUMBERS[corner][test_type]
            )
            
            # Apply special rules
            if corner == "F1":
                test.EndVoltageLimits = "ARR_CCF_Rules.QA_HOT_Default(...)"
            else:
                test.EndVoltageLimits = "__shared__::FlowMatrixSingular.CCF_HIGH_SEARCH_VALUE"
            
            if test_type == "SSA_LLCSRAM":
                test.SetPointsPreInstance += ",MCdrv:atomfreq_0:..."
            
            flow.add_test(test)
        
        flows.append(flow)
    
    return flows
```

## Usage Example

To generate a new test program with corners F1, F2, F3:

```python
# Input
corners = ["F1", "F2", "F3"]

# Expand
flows = expand_blueprint(corners)

# Output contains:
# - ARR_CCF_CXX_F1XCCF (3 tests: LLCSRAM, CBOA, LLCRF)
# - ARR_CCF_CXX_F2XCCF (3 tests: LLCSRAM, CBOA, LLCRF)
# - ARR_CCF_CXX_F3XCCF (3 tests: LLCSRAM, CBOA, LLCRF)
# Total: 3 flows × 3 tests = 9 test instances
```

## Notes

1. **F4 Base Numbers**: F4 uses a different base number range (1275x) compared to F1-F3 (1233x-1234x). This is intentional and should be preserved.

2. **FlowIndex**: All F1-F4 flows use `FlowMatrix.FlowIndex` (not `FlowMatrixSingular`). This is different from F5, which uses `FlowMatrixSingular.FlowIndex`.

3. **Core/Atom Frequencies**: These remain constant at `CR_F1_FREQ` and `AT_F1_FREQ` across all corners. Only the ring frequency (`CCF_F<corner>_FREQ`) varies.

4. **Test Order**: The order of tests within each flow is critical and must be maintained: SSA_LLCSRAM → LSA_CBOA → LSA_LLCRF.

5. **F5 Exclusion**: This blueprint covers F1-F4 only. F5 has significant differences (extra ARR_CCF_FMAX subflow, symbolic CornerIdentifiers, array parameters) and should be treated as a separate pattern.
