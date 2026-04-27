---
applyTo: "**/TPI_DAS_CXX/**"
---

# TPI_DAS_CXX — DAS (Data Acquisition System) Module

## Module Overview

`TPI_DAS_CXX` measures CPU ring oscillator performance using the DAS system. For each voltage level (550mV–1050mV) and measurement mode (TDC0, TDC1, FALL, RISE, STRESS_AF), it executes `CtvDecoderSpm` or `PrimeFunctionalTestMethod` tests and collects data. A fork test routes QE/engineering sessions to bypass the main DAS flow.

---

## Editing Rules

- **Pymtpl-based module** — `TPI_DAS_CXX.py` is the **source of truth**.
- **Never edit `.mtpl` directly** — it is fully regenerated on compilation.
- After any change to `.py`, run the Pymtpl compiler.

---

## Module Initialization

```python
InitializeNVLClass('./TPI_DAS_CXX', 'TPI_DAS_CXX', tosversion="tos4", binrange=(710, 779))
Import("TPI_DAS_CXX_LevelsSequences.lvl")
Import("TPI_DAS_CXX_Levels.tcg")
```

---

## Voltage Levels

```python
TestName = ["FORCE_0550MV", "FORCE_0650MV", "FORCE_0750MV",
            "FORCE_0850MV", "FORCE_0950MV", "FORCE_1050MV"]
```

Levels are defined in `TPI_DAS_CXX_LevelsSequences.lvl` using `IPC::TPI_DAS_CXX::DAS_VCCIA_<LEVEL>_MIN` namespacing.

---

## Measurement Modes

| Mode | Patlist segment | Config file pattern | Test type |
|------|----------------|---------------------|-----------|
| `TDC0` | `RO_MODE_TDC_0` | `das_ro_mode_tdc0[_48]_A0.csv` | `CtvDecoderSpm` |
| `TDC1` | `RO_MODE_TDC_1` | `das_ro_mode_tdc1[_48]_A0.csv` | `CtvDecoderSpm` |
| `FALL` | `MEAS_MODE_FALL` | `das_meas_mode_fall[_48]_A0.csv` | `CtvDecoderSpm` |
| `RISE` | `MEAS_MODE_RISE` | `das_meas_mode_rise[_48]_A0.csv` | `CtvDecoderSpm` |
| `STRESS_AF` | `stress_af_mode` | N/A | `PrimeFunctionalTestMethod` |

Config files are selected using `__shared__::TpRule.If_48(...)` — 48-core variants use `_48` suffixed files.

---

## Test Types Used

### AuxiliaryTC (fork test)

Routes QE/engineering sessions to bypass DAS:

```python
AuxiliaryTC(
    name='DAS_X_AUX_K_BEGINCPU_X_X_X_X_QNR_FORK',
    DataType='String',
    Datalog='Enabled',
    Expression="[SCVars.SC_ENGID]",
    ResultPort="([R]=='QE'||[R]=='QQ'||[R]=='QZ')?1:2"
)
```

- Result 1: QE/engineering session — flow routes to skip DAS tests  
- Result 2: Production — flow continues to DAS tests

### CtvDecoderSpm

Runs ring oscillator capture per voltage/mode combination:

```python
CtvDecoderSpm(
    name=f"DAS_X_CTVDECODER_K_BEGINCPU_X_X_X_X_{param}_{mode}",
    ConfigurationFile=Spec('__shared__::TpRule.If_48("./InputFiles/das_<mode>_48_A0.csv","./InputFiles/das_<mode>_A0.csv")'),
    LevelsTc=f"IPC::TPI_DAS_CXX::DAS_VCCIA_{param}_MIN",
    TimingsTc="IPC::CPU_IP_BASE::cpu_fun_timing_mts100_tstprtclk50_tck100",
    PrePlist="SetPinAttributes(--settings=CPU_VLOADMUXCBIT3:LogicalValue:0)",
    CtvCapturePins="IPC::CPU_TDO",
    Patlist=f"nvl_full_das_ip_{patlist_name.lower()}",
    _fitem=Fitem('SAME', r0=pFail(setbin=AUTO, ret=0), r2=pFail(setbin=90990700, ret=2))
)
```

### PrimeFunctionalTestMethod

Used for the STRESS_AF mode (currently bypassed — `BypassPort=1`):

```python
PrimeFunctionalTestMethod(
    name=f"DAS_X_PRIMEFUNC_K_BEGINCPU_X_X_X_X_{param}_STRESS_AF",
    LevelsTc=f"IPC::TPI_DAS_CXX::DAS_VCCIA_{param}_MIN",
    TimingsTc="IPC::CPU_IP_BASE::cpu_fun_timing_mts100_tstprtclk50_tck100",
    PrePlist="SetPinAttributes(--settings=CPU_VLOADMUXCBIT3:LogicalValue:0)",
    Patlist="nvl_full_das_ip_stress_af_mode",
    BypassPort=1,
    _fitem=Fitem('SAME', r0=pFail(setbin=AUTO, ret=0), r2=pFail(setbin=90990700, ret=2))
)
```

---

## Test Naming Patterns

```
DAS_X_AUX_K_BEGINCPU_X_X_X_X_QNR_FORK                         # fork test
DAS_X_CTVDECODER_K_BEGINCPU_X_X_X_X_<VOLTAGE>_<MODE>          # CtvDecoderSpm
DAS_X_PRIMEFUNC_K_BEGINCPU_X_X_X_X_<VOLTAGE>_STRESS_AF        # STRESS_AF
```

---

## Voltage Override Behavior

For `FORCE_0950MV` and `FORCE_1050MV`, `PreInstance` and `PostInstance` are added to override `VCCIA` voltage:

```python
PreInstance = Spec('__shared__::TpRule.If_48(
    "VoltageConverter(--dlvrpins VCCIA --overrides CORE1:<V>,CORE0:<V> --expressions CCF_CORE)",
    "VoltageConverter(--dlvrpins VCCIA --overrides CORE3:<V>,CORE2:<V>,CORE1:<V>,CORE0:<V> --expressions CCF_CORE)"
)')
PostInstance = "VoltageConverter(--dlvrpins VCCIA --fivrcondition NOM_CCF_CORE --expressions CCF_CORE)"
```

For 48-core variants, only 2 overrides are used (CORE1, CORE0). For all others, 4 overrides are used.

---

## Sub-Flows

| Sub-flow | Contents |
|----------|----------|
| `TDC_0` | All `FORCE_*MV` × `TDC0` tests |
| `TDC_1` | All `FORCE_*MV` × `TDC1` tests |
| `FALL_MODE` | All `FORCE_*MV` × `FALL` tests |
| `RISE_MODE` | All `FORCE_*MV` × `RISE` tests |
| `STRESS_AF_MODE` | All `FORCE_*MV` × `STRESS_AF` tests (currently bypassed) |

---

## Generated Flow

```
TPI_DAS_CXX_BEGINCPU
```

Structure:

```
Fitem: DAS_BYPASS fork  → r2=continue to DAS
Fitem: TDC_0
Fitem: TDC_1
Fitem: FALL_MODE
Fitem: RISE_MODE
Fitem: STRESS_AF_MODE
```

---

## Adding a New Voltage Level — Checklist

1. Add the new level string (e.g. `"FORCE_1150MV"`) to `TestName` in `TPI_DAS_CXX.py`.
2. Add the levels mapping entry in the `LevelMode` dict.
3. Add a `VoltageConverter` pre/post instance block if a non-default voltage override is needed.
4. Add corresponding level definitions to `TPI_DAS_CXX_LevelsSequences.lvl`.
5. Run the Pymtpl compiler.

---

## Adding a New Measurement Mode — Checklist

1. Add the mode string to the `Modes` list in `TPI_DAS_CXX.py`.
2. Add `mode_to_patlist` and `mode_to_config_file` entries.
3. Run the Pymtpl compiler — the new tests are generated automatically via the loop.
4. Define a new `Flow(...)` for the mode (similar to `TDC_0`, `FALL_MODE`, etc.).
5. Add the new flow as a `Fitem` inside `TPI_DAS_CXX_BEGINCPU`.

---

## Contacts

Refer to the `owner.txt` file in the module directory for the current module owner.
