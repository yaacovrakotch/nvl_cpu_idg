---
applyTo: "**/TPI_DFF_XXX/**"
---

# TPI_DFF_XXX — DFF End-of-Flow Validation Module

## Module Overview

`TPI_DFF_XXX` performs DFF (Device Failure File) end-of-flow validation and logs die identifier data using `ULTLoggerTC`. It runs at two key points: pre-PRL1 (reading die IDs) and final (validating DFF state).

---

## Editing Rules

- **Pymtpl-based module** — `TPI_DFF_XXX.py` is the **source of truth**.
- **Never edit `.mtpl` directly** — it is fully regenerated on compilation.
- After any change to `.py`, run the Pymtpl compiler.

---

## Module Initialization

```python
InitializeNVLClass('TPI_DFF_XXX', 'TPI_DFF_XXX', binrange=[(5300, 5310), (9401, 9410)])
```

---

## Subflows

| Subflow | Purpose |
|---------|---------|
| `STARTPREPRL1` | Reads die identifier DFF tokens into shared storage |
| `FINAL` | Validates DFF end-of-flow state; logs die IDs to ituff |

---

## Test Types Used

| Test class | Usage |
|-----------|-------|
| `PrimeDffEndOfFlowValidationTestMethod` | Validates DFF state at end of flow |
| `PrimeDffReadTestMethod` | Reads a DFF token into shared storage |
| `ULTLoggerTC` | Logs data to ituff output |
| `AuxiliaryTC` | Dummy/gate tests |

---

## Key DFF References

| Reference | Purpose |
|-----------|---------|
| `__shared__::DFFVars.DIEID_CPU` | CPU die ID DFF token |
| `__shared__::DFFVars.DIEID_GPU` | GCD die ID DFF token |
| `__shared__::DFFVars.DIEID_HUB` | HUB die ID DFF token |
| `__shared__::DFFVars.DIEID_PCD` | PCD die ID DFF token |
| `__shared__::DFFVars.IDENTIFIER_*` | Die identifier tokens for each die |

---

## Editing Checklist

1. Modify `TPI_DFF_XXX.py` for the desired change (add/remove die ID, change validation logic).
2. Run the Pymtpl compiler.
3. Verify the generated `.mtpl` reflects the changes correctly in both subflows.
