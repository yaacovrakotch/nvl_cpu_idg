---
applyTo: "**/TPI_FLWFLGS_CXX/**"
---

# TPI_FLWFLGS_CXX — Flow Flags Module

## Module Overview

`TPI_FLWFLGS_CXX` manages per-subflow skip/enable logic for the entire CPU test program. For each subflow discovered in the program flow, it generates a paired set of tests:

| Test suffix | Purpose |
|-------------|---------|
| `FLWSKP` | Evaluates skip conditions using `FlwSkpCollect.FlwSkpRule(...)` read from the CSV map |
| `FLWFLG` | Records the actual flow execution flag (and sets the die ID context) |

---

## Editing Rules

- **Pymtpl-based module** — `TPI_FLWFLGS_CXX.py` is the **source of truth**.
- **Never edit `.mtpl` directly** — it is fully regenerated each time `.py` is compiled.
- After any change to `.py`, run the Pymtpl compiler to regenerate `.mtpl`.
- The CSV file `InputFiles/Flwflg_Logic_Map.csv` must stay in sync with the program flows.

---

## How Subflows Are Discovered

The `.py` reads `POR_TP/Class_NVL_S28C/ProgramFlowsTestPlan/IP*.py` and extracts subflow names where the **second token on a line starts with `TPI_FLWFLGS`**. The subflow name is the first token, with `_SubFlow` stripped.

---

## Generated Test Pair Per Subflow

### FLWSKP test

```python
AuxiliaryTC(
    name=f"CTRL_X_AUX_K_{subflw}_X_X_X_X_FLWSKP",
    DataType="Integer",
    Expression="1",
    ResultPort="1",
    BypassPort=Spec(f"__shared__::FlwSkpCollect.FlwSkpRule({convert_str})"),
    _fitem=Fitem('SAME', r0=pFail(setbin=AUTO, ret=0, ctr=FLWSKPCTR), r2=pPass(ret=2))
)
```

### FLWFLG test

```python
AuxiliaryTC(
    name=f"CTRL_X_AUX_K_{subflw}_X_X_X_X_FLWFLG",
    DataType="Integer",
    Expression="1",
    ResultPort="1",
    PreInstance=pre_instance_value,   # see PreInstance rule below
    _fitem=Fitem('SAME', r0=pFail(setbin=AUTO, ret=0, ctr=FLWFLGCTR))
)
```

### PreInstance rule for FLWFLG

| Subflow | PreInstance value |
|---------|------------------|
| `STARTCPUNOM` | `''` (empty string — no pre-instance) |
| All other subflows | `'SetCurrentDieId("+__shared__::DFFVars.DIEID_CPU+")'` |

### PostInstance rule for FLWFLG

| Condition | PostInstance value |
|-----------|-------------------|
| S52C (NVL_S52C) | `Spec('__shared__::TpRule.If_CLASS_NVL_S52C("PrimeSetAdditionalCurrentDieIds("+__shared__::DFFVars.DIEID_CPU1+")","")')` |
| All other packages | `None` (no PostInstance) |

---

## Counter Ranges

| Test type | Counter start | Increments |
|-----------|--------------|-----------|
| FLWSKP | **44500000** | +1 per subflow |
| FLWFLG | **54550000** | +1 per subflow |

---

## CSV Logic Map

`InputFiles/Flwflg_Logic_Map.csv`:
- **Column A** — subflow name
- **Columns B+** — parameters passed to `FlwSkpCollect.FlwSkpRule(...)`

The Pymtpl reads this CSV to build the `BypassPort` expression for each FLWSKP test. The CSV **must be manually updated** when new subflows are added.

If the CSV does not contain an entry for a subflow found in the program flows, the Pymtpl will detect the mismatch on compilation and exit with an update message.

---

## Generated Flow Per Subflow

Each subflow pair generates one named flow:

```
TPI_FLWFLGS_CXX_<SUBFLOW>
```

The flow contains both FLWSKP and FLWFLG tests in sequence.

---

## Adding a New Subflow — Checklist

1. Add the subflow to the program flow file (`POR_TP/Class_NVL_S28C/ProgramFlowsTestPlan/IP*.py`) with `TPI_FLWFLGS_CXX` as the second token on the line.
2. Run the Pymtpl compiler — it will detect the CSV is out of date and exit with a message.
3. Open `InputFiles/Flwflg_Logic_Map.csv` and add a new row for the subflow with the correct `FlwSkpRule(...)` parameters.
4. Run the Pymtpl compiler again — the new FLWSKP/FLWFLG pair and flow are generated automatically.
5. Verify the new counter entries appear in the `Counters` block of the generated `.mtpl`.
