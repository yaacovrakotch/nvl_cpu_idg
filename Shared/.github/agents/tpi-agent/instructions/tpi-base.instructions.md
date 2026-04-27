---
applyTo: "**/TPI_BASE_XXX/**"
---

# TPI_BASE_XXX — Program Initialization Module

## Module Overview

`TPI_BASE_XXX` handles program-level initialization, lot start/end, VMIN forwarding, and test-plan-level sequencing. It runs at the very start and end of the test flow.

---

## Editing Rules

- **Pymtpl-based module** — `TPI_BASE_XXX.py` is the **source of truth**.
- **Never edit `.mtpl` directly** — it is fully regenerated on compilation.
- After any change to `.py`, run the Pymtpl compiler.

---

## Module Initialization

```python
InitializeNVLClass('TPI_BASE_XXX', 'TPI_BASE_XXX', binrange=(9302, 9302))
```

---

## Subflows

| Subflow | Purpose |
|---------|---------|
| `INIT` | Program entry — library and Simba init, device begin datalog |
| `LOTSTARTFLOW` | Lot start callback |
| `LOTENDFLOW` | Lot end callback |
| `TESTPLANSTARTFLOW` | Test plan start — registers callbacks |
| `TESTPLANENDFLOW` | Test plan end cleanup |
| `START` | Main start-of-test-sequence init tests |
| `STARTPOST` | Post-start operations |
| `STARTPREPRL1` | Pre-PRL1 setup |
| `BEGIN` | Begin-of-lot operations |
| `FINAL` | End-of-sequence finalization |
| `FACT` | Factory-specific setup |

---

## Test Types Used

| Test class | Usage |
|-----------|-------|
| `PrimeInitializeLibraryTestMethod` | Library initialization (`INIT` flow) |
| `PrimeSimbaInitTestMethod` | Simba framework init (`INIT` flow) |
| `VminForwardingBase` | VMIN forwarding setup |
| `ScreenTC` | Various screen tests |
| `AuxiliaryTC` | Auxiliary control tests |
| `RunCallback` | Callback execution |

---

## Adding a New Test — Checklist

1. Add the test instance to `TPI_BASE_XXX.py` using the appropriate test class.
2. Name the test following: `CTRL_X_<TESTTYPE>_K_<SUBFLOW>_X_X_X_X_<SUFFIX>`
3. Place it in the correct `Flow(...)` for the target subflow.
4. Run the Pymtpl compiler to regenerate `.mtpl`.
5. Verify the new test and flow item appear correctly in the generated `.mtpl`.
