---
applyTo: "**/TPI_END_XXX/**"
---

# TPI_END_XXX — End-of-Flow Module

## Module Overview

`TPI_END_XXX` performs end-of-test-sequence operations: device end datalog, bin 69 flag check, ODES bin remapping, and factory-end logout.

---

## Editing Rules

- **Pymtpl-based module** — `TPI_END_XXX.py` is the **source of truth**.
- **Never edit `.mtpl` directly** — it is fully regenerated on compilation.
- After any change to `.py`, run the Pymtpl compiler.

---

## Module Initialization

```python
InitializeNVLClass('TPI_END_XXX', 'TPI_END_XXX', binrange=(9307, 9307))
```

---

## Subflows

| Subflow | Purpose |
|---------|---------|
| `INIT` | Instance initialization |
| `FACT` | Factory end operations |
| `END` | Main end-of-flow: device end datalog + bin 69 check |
| `TESTPLANENDFLOW` | Test plan end cleanup |
| `FINAL` | Final logout |

---

## Test Types Used

| Test class | Usage |
|-----------|-------|
| `PrimeInitializeInstancesTestMethod` | Instance init at start |
| `RunCallback` | General callbacks |
| `AuxiliaryTC` | Bin 69 flag check (`Bin69_chk`) |
| `PrimeDeviceEndDatalogTestMethod` | Device end datalog |

---

## Key References

| Reference | Purpose |
|-----------|---------|
| `__shared__::TP_KNOB.Bin69_FLG` | Flag used to check bin 69 condition in `Bin69_chk` test |

---

## Bin 69 Check

The `Bin69_chk` test evaluates `__shared__::TP_KNOB.Bin69_FLG`. If the flag is set (indicating a bin 69 condition), the test fails and assigns the appropriate bin.

---

## Editing Checklist

1. Modify `TPI_END_XXX.py` for the desired change.
2. Run the Pymtpl compiler.
3. Verify the generated `.mtpl` includes the updated test or flow logic.
