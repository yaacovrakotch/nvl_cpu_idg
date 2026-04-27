---
applyTo: "**/TPI_XIU_XXX/**"
---

# TPI_XIU_XXX — XIU Identity and Continuity Module

## Module Overview

`TPI_XIU_XXX` performs XIU (eXternal Interface Unit) identity validation, TDR (Time Domain Reflectometry) calibration, power supply continuity, and signal pin leakage tests. It runs at the `INIT` and `PKGFF` subflows.

---

## Editing Rules

- **Pymtpl-based module** — `TPI_XIU_XXX.py` is the **source of truth**.
- **Never edit `.mtpl` directly** — it is fully regenerated on compilation.
- After any change to `.py`, run the Pymtpl compiler.

---

## Module Initialization

```python
InitializeNVLClass('TPI_XIU_XXX', 'TPI_XIU_XXX', tosversion="tos4")
```

No binrange is specified at the module level (bins are assigned inline if needed).

---

## Subflows

| Subflow | Purpose |
|---------|---------|
| `INIT` | XIU identity check + TDR calibration |
| `PKGFF` | Power supply continuity + signal pin leakage |

---

## Test Types Used

| Test class | Usage |
|-----------|-------|
| `PrimeTiuIdentityTestMethod` | Validates XIU identity via regex pattern matching |
| `PrimeTdrCalibrationTestMethod` | TDR calibration |
| `PrimeTiuPowerSupplyContinuityTestMethod` | Power supply pin continuity |
| `PrimeTiuSignalPinLeakageTestMethod` | Signal pin leakage measurement |

---

## XIU Identity Validation

The identity test uses regex patterns to validate the TIU (Test Interface Unit) identity string. Patterns are defined in the `.py` and compiled into the test's `Pattern` parameter.

---

## Editing Checklist

1. Modify `TPI_XIU_XXX.py` — update identity patterns, TDR parameters, or add/remove tests.
2. Run the Pymtpl compiler.
3. Verify the generated `.mtpl` reflects the updated test definitions.
