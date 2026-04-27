---
applyTo: "**/TPI_FLWFLGS_XXX/**"
---

# TPI_FLWFLGS_XXX — Flow Flags Module

## Module Overview

`TPI_FLWFLGS_XXX` manages per-subflow skip/enable logic for the entire NVL test program (all dielets: CPU, GCD, HUB, PCD). For each subflow discovered in the program flow, it generates a paired set of tests:

| Test suffix | Purpose |
|-------------|---------|
| `FLWSKP` | Evaluates skip conditions using `FlwSkpCollect.FlwSkpRule(...)` read from the CSV map |
| `FLWFLG` | Records the actual flow execution flag (and sets the die ID context) |

---

## Editing Rules

- **Pymtpl-based module** — `TPI_FLWFLGS_XXX.py` is the **source of truth**.
- **Never edit `.mtpl` directly** — it is fully regenerated each time `.py` is compiled.
- After any change to `.py`, run the Pymtpl compiler to regenerate `.mtpl`.
- The CSV file `InputFiles/Flwflg_Logic_Map.csv` must stay in sync with the program flows.

---

## How Subflows Are Discovered

The `.py` reads four dielet ProgramFlows files via the path `POR_TP/Class_NVL_S28C/ProgramFlowsTestPlan/`:
- `ProgramFlowsCPU.py`
- `ProgramFlowsGCD.py`
- `ProgramFlowsHUB.py`
- `ProgramFlowsPCD.py`

It also scans all `POR_TP/*/ProgramFlowsTestPlan/ProgramFlowsSharedPKG.py` files.

Subflow names are extracted where the **second token on a line starts with `TPI_FLWFLGS`**. The subflow name is the first token, with `_SubFlow` stripped.

> ⚠️ These dielet ProgramFlows files live in the dielet repos (`nvl.cpu`, `nvl.gcd`, `nvl.hub`, `nvl.pcd`). When compiling `TPI_FLWFLGS_XXX`, nvl.common must be cloned as a submodule inside a dielet repo so the files exist at the expected relative paths.

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
    PostInstance=post_instance,       # see PostInstance rule below
    _fitem=Fitem('SAME', r0=pFail(setbin=AUTO, ret=0, ctr=FLWFLGCTR))
)
```

### PreInstance / PostInstance rule for FLWFLG

The die ID context is set based on which dielet's PKG subflow this is:

| Subflow matches | PreInstance | PostInstance |
|-----------------|-------------|--------------|
| CPU PKG subflows (`STARTCPUPATMODSPKG`, `HVBICPUPKG`, `BEGINCPUPKG`, `ENDCPUPKG`, `ENDCPUVMAXPKG`, `LTTCCPUPKG`, `CPUIPFF`, `CPUPKGFF`) | `SetCurrentDieId("+__shared__::DFFVars.DIEID_CPU+")` | `__shared__::TpRule.If_CLASS_NVL_S52C("PrimeSetAdditionalCurrentDieIds("+__shared__::DFFVars.DIEID_CPU1+")","")` (S52C only) |
| GCD PKG subflows (`STARTGCDPATMODSPKG`, `HVBIGCDPKG`, `BEGINGCDPKG`, `ENDGCDPKG`, `ENDGCDVMAXPKG`, `LTTCGCDPKG`, `GCDIPFF`, `GCDPKGFF`) | `SetCurrentDieId("+__shared__::DFFVars.DIEID_GPU+")` | None |
| HUB PKG subflows (`STARTHUBPATMODSPKG`, `HVBIHUBPKG`, `BEGINHUBPKG`, `ENDHUBPKG`, `ENDHUBVMAXPKG`, `LTTCHUBPKG`, `HUBIPFF`, `HUBPKGFF`) | `SetCurrentDieId("+__shared__::DFFVars.DIEID_HUB+")` | None |
| PCD PKG subflows (`STARTPCDPATMODSPKG`, `HVBIPCDPKG`, `BEGINPCDPKG`, `ENDPCDPKG`, `ENDPCDVMAXPKG`, `LTTCPCDPKG`, `PCDIPFF`, `PCDPKGFF`) | `SetCurrentDieId("+__shared__::DFFVars.DIEID_PCD+")` | None |
| All other subflows | `SetCurrentDieId(PKG)` | None |

---

## Counter Ranges

| Test type | Counter start | Increments |
|-----------|--------------|-----------|
| FLWSKP | **44400000** | +1 per subflow |
| FLWFLG | **54400000** | +1 per subflow |

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
TPI_FLWFLGS_XXX_<SUBFLOW>
```

The flow contains both FLWSKP and FLWFLG tests in sequence.

---

## Adding a New Subflow — Checklist

1. Add the subflow to the appropriate dielet ProgramFlows file (`ProgramFlowsCPU.py`, `ProgramFlowsGCD.py`, `ProgramFlowsHUB.py`, or `ProgramFlowsPCD.py`) in the dielet repo, with `TPI_FLWFLGS_XXX` as the second token on the line. (This step happens in the dielet repo, not nvl.common.)
2. Run the Pymtpl compiler — it will detect the CSV is out of date and exit with a message.
3. Open `InputFiles/Flwflg_Logic_Map.csv` and add a new row for the subflow with the correct `FlwSkpRule(...)` parameters.
4. Run the Pymtpl compiler again — the new FLWSKP/FLWFLG pair and flow are generated automatically.
5. Verify the new counter entries appear in the `Counters` block of the generated `.mtpl`.
