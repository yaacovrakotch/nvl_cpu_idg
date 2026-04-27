---
applyTo: "**/TPI_DIERCVRY_CXX/**"
---

# TPI_DIERCVRY_CXX — Die Recovery Module

## Module Overview

`TPI_DIERCVRY_CXX` manages CPU die recovery operations across three subflows. It initializes die recovery trackers, restores core recovery DFF values at the start of the CPU test, and finalizes recovery data at package end.

> **Note:** The Pymtpl source file uses a non-standard `_SOURCE` suffix: `TPI_DIERCVRY_CXX_SOURCE.py`.

---

## Editing Rules

- **Pymtpl-based module** — `TPI_DIERCVRY_CXX_SOURCE.py` is the **source of truth**.
- **Never edit `.mtpl` directly** — it is fully regenerated on compilation.
- After any change to `_SOURCE.py`, run the Pymtpl compiler targeting `TPI_DIERCVRY_CXX_SOURCE.py`.
- The `.usrv` file (`TPI_DIERCVRY_CXX.usrv`) contains UserVar definitions imported via `Import(...)` — edit separately if UserVars change.

---

## Module Initialization

```python
InitializeNVLClass('TPI_DIERCVRY_CXX', 'TPI_DIERCVRY_CXX',
    binrange=(9310, 9310),
    defaultrm2bin=(99932000, 99933999),
    defaultrm1bin=(98932000, 98933999))

Import("TPI_DIERCVRY_CXX.usrv")
```

Fail bins increment from 9310 upward — one explicit bin number per test instance.

---

## Subflow List

```python
subflow = ["INIT", "BEGINCPU", "ENDCPUPKG"]
# Index:      0        1            2
```

---

## Flow Sequence Overview

| Subflow | Purpose |
|---------|---------|
| `INIT` | Initializes die recovery tracker from JSON rules and SKU files |
| `BEGINCPU` | Restores core recovery tracker from DFF/GSDS at the start of the CPU test; supports 1-die and 2-die (S52C) |
| `ENDCPUPKG` | Finalizes die recovery data at end of the CPU package test |

---

## Test Types Used

### DieRecoveryBase

Initializes recovery trackers from JSON rules and SKU files (INIT subflow):

```python
DieRecoveryBase(
    name=f"CTRL_X_PRIMEDIERECOVERY_K_{subflow[0]}_X_X_X_X_X",
    LogLevel="Disabled",
    EnablePreTestCheck="False",
    RulesFile=Spec('__shared__::TpRule.If_S28_S52_HX28_P16C_S16C_DS28C(...)'),
    SKUFile=Spec('__shared__::TpRule.If_S28_S52_HX28_P16C_S16C_DS28C(...)'),
    TrackerFile=Spec('__shared__::TpRule.If_48(...)'),
    AllowDefeatures=Spec('TPI_DIERCVRY_CXX_Rules.RecoveryBypass(...)'),
    SaveHistory="True",
    _fitem=Fitem('SAME', r0=pFail(ret=0), r1=pPass(ret=1))
)
```

### ScreenTC

Used to check DFF revert conditions and route flow (BEGINCPU subflow):

```python
ScreenTC(
    name=f"DIERCVRY_X_FUNC_K_{subflow[1]}_X_X_X_X_REVERSEDFF",
    BypassPort=Spec('__shared__::TpRule.If_48(1,-1)'),
    ScreenTestSet="SetDFF2GSDS",
    ScreenTestsFile="./InputFiles/TPI_DIERCVRY_CXX_ScreenTest.txt",
    PostInstance="PrintToItuff(--body_type strgval --body_data G.I.S.REVERTCOREREC)",
    _fitem=Fitem('SAME',
        r0=pFail(setbin=DIERCVRY_Bin, ret=0),
        r1=pPass(goto="..._CORE0TOTRACKER"),
        r2=pPass(goto="..._CORE0TOTRACKERGSDS"),
        r3=pFail(setbin=DIERCVRY_Bin, ret=0))
)
```

### RunCallback

Used for tracker writes and GSDS copy operations:

```python
RunCallback(
    name=f"DIERCVRY_X_FUNC_K_{subflow[1]}_X_X_X_X_CORE0TOTRACKER",
    Callback="WriteTracker",
    Parameters=Spec('TPI_DIERCVRY_CXX_Rules.RecoveryRule(...)'),
    ResultPort="[R]=='PASS'?1:0",
    PostInstance="CopyTracker(--tracker ACRM3,ACRM2,ACRM1,ACRM0,CR --gsds G.I.S.CRINIT)",
    _fitem=Fitem('SAME',
        r0=pFail(setbin=DIERCVRY_Bin, ret=0),
        r1=pPass(goto="..."),
        r2=pFail(setbin=DIERCVRY_Bin, ret=0))
)
```

---

## Test Naming Patterns

```
CTRL_X_PRIMEDIERECOVERY_K_INIT_X_X_X_X_X         # DieRecoveryBase (INIT subflow)
DIERCVRY_X_FUNC_K_<SUBFLOW>_X_X_X_X_<SUFFIX>     # ScreenTC and RunCallback
```

---

## Die ID References

| Reference | Purpose |
|-----------|---------|
| `__shared__::DFFVars.DIEID_CPU` | Primary CPU die ID |
| `__shared__::DFFVars.DIEID_CPU1` | Second CPU die ID (S52C 2-die packages only) |

---

## Key Rules References

| Rule | Purpose |
|------|---------|
| `TPI_DIERCVRY_CXX_Rules.RecoveryBypass(...)` | Recovery bypass rule (AllowDefeatures) per package |
| `TPI_DIERCVRY_CXX_Rules.RecoveryRule(...)` | Selects WriteTracker parameters by recovery path |
| `__shared__::TpRule.If_S28_S52_HX28_P16C_S16C_DS28C(...)` | Package-specific parameter selection |
| `__shared__::TpRule.If_48(...)` | Bypass based on 48-core vs other variants |
| `__shared__::TpRule.If_CLASS_NVL_S52C(...)` | S52C-specific routing |

---

## S52C 2-Die Handling

The `BEGINCPU` subflow handles both 1-die and 2-die (S52C) packages:

- Tests `REVERSEDFF2CDIE`, `CORE1TOTRACKER`, `CORE1TOTRACKERGSDS`, `SLICE1TOTRACKER` are **bypassed** on all non-S52C packages via `BypassPort = Spec('__shared__::TpRule.If_S28_S52_HX28_P16C_S16C_DS28C(1,-1,1,1,1,1,1)')`.
- Second die tracker operations use `__shared__::DFFVars.DIEID_CPU1` for DFF lookups.

---

## Bin Increment Pattern

Bins are assigned explicitly and increment monotonically from binrange start:

```python
DIERCVRY_Bin = 9310
# After each test instance: DIERCVRY_Bin += 1
```

`AUTO` is not used — each test instance gets a unique explicit bin number.

---

## Adding a New Recovery Test — Checklist

1. Determine the subflow (`INIT`, `BEGINCPU`, or `ENDCPUPKG`).
2. Add the test instance to `TPI_DIERCVRY_CXX_SOURCE.py` using the next `DIERCVRY_Bin` value; increment `DIERCVRY_Bin` immediately after.
3. Use the correct test type (`DieRecoveryBase`, `ScreenTC`, or `RunCallback`).
4. Follow the naming pattern `DIERCVRY_X_FUNC_K_<SUBFLOW>_X_X_X_X_<SUFFIX>`.
5. For S52C-only tests, add the appropriate `BypassPort` rule from `__shared__::TpRule.If_S28_S52_...`.
6. Run the Pymtpl compiler targeting `TPI_DIERCVRY_CXX_SOURCE.py`.
7. Verify the new test and bin counter appear in the generated `.mtpl`.
