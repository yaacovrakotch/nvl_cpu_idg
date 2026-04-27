---
applyTo: "**/TPI_TIMETRK_CXX/**"
---

# TPI_TIMETRK_CXX — Time Tracking Module

## Module Overview

`TPI_TIMETRK_CXX` measures the execution time of parallel subflows across all dielets. For each subflow whose name contains `PRL`, it generates a START timer test at the beginning of the subflow and a STOP timer test at the end.

---

## Editing Rules

- **Pymtpl-based module** — `TPI_TIMETRK_CXX.py` is the **source of truth**.
- **Never edit `.mtpl` directly** — it is fully regenerated on compilation.
- After any change to `.py`, run the Pymtpl compiler.

---

## Module Initialization

```python
InitializeNVLClass(module_name, module_name, tosversion="tos4", binrange=(9370, 9370))
```

---

## Test Type

All tests use `TimeTracker` with either `TestMode = "START"` or `TestMode = "STOP"`.

---

## Test Definition Pattern

### TIMERSTART

```python
TimeTracker(
    name=f"CTRL_X_TIMETRACK_K_{subflw}_X_X_X_X_TIMERSTART",
    TestMode="START",
    Argument=f'{subflw}',
    _fitem=Fitem('SAME', r0=pFail(setbin=AUTO, ret=0, ctr=TIMESTART))
)
```

### TIMERSTOP

```python
TimeTracker(
    name=f"CTRL_X_TIMETRACK_K_{subflw}_X_X_X_X_TIMERSTOP",
    TestMode="STOP",
    Argument=f'{subflw}',
    _fitem=Fitem('SAME', r0=pFail(setbin=AUTO, ret=0, ctr=TIMESTOP))
)
```

The `Argument` value is the subflow name string — this is how the timer identifies which subflow it is measuring.

---

## Subflow Selection Rule

Only subflows containing **`PRL`** in their name are tracked.

The `.py` reads all subflows from `POR_TP/Class_NVL_S28C/ProgramFlowsTestPlan/IP*.py` and filters to only those where `'PRL' in subflw`. Deduplication is applied to prevent duplicate timer entries.

---

## Counter Ranges

| Timer type | Start value | Increments |
|------------|------------|-----------|
| TIMERSTART | **44500000** | +1 per PRL subflow |
| TIMERSTOP  | **54550000** | +1 per PRL subflow |

---

## Generated Flows

Each PRL subflow generates two flows:

```
TPI_TIMETRK_CXX_FIRST_<SUBFLOW>   → contains the TIMERSTART test
TPI_TIMETRK_CXX_LAST_<SUBFLOW>    → contains the TIMERSTOP test
```

Examples for CPU parallel subflows: `TPI_TIMETRK_CXX_FIRST_STARTPRL0CPU`, `TPI_TIMETRK_CXX_LAST_ENDPRL0CPU`.

The FIRST flow is placed at the entry point of the subflow; the LAST flow is placed at the exit point.

---

## Adding a New PRL Subflow Timer — Checklist

1. Confirm the subflow exists in `POR_TP/Class_NVL_S28C/ProgramFlowsTestPlan/IP*.py`.
2. Confirm the subflow name contains `PRL` — only PRL subflows are timed.
3. Run the Pymtpl compiler — the TIMERSTART and TIMERSTOP tests, plus `FIRST_` and `LAST_` flows, are generated automatically.
4. Verify the new counter entries appear in the `Counters` block of the generated `.mtpl`.
5. Wire the new `TPI_TIMETRK_CXX_FIRST_<SUBFLOW>` and `TPI_TIMETRK_CXX_LAST_<SUBFLOW>` flows into the program flow at the correct entry and exit points.
