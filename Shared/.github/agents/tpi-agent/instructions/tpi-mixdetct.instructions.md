---
applyTo: "**/TPI_MIXDETCT_XXX/**"
---

# TPI_MIXDETCT_XXX — Mix/Wrong-Die Detection Module

## Module Overview

`TPI_MIXDETCT_XXX` detects mixed or wrong dies in the package using `PrimeMixingDetectionTestMethod`. It runs at the STARTPREPRL1 subflow and uses a configuration file to define the expected die combinations.

---

## Editing Rules

- **Pymtpl-based module** — `TPI_MIXDETECT_XXX.py` is the **source of truth** (note: filename is `TPI_MIXDETECT_XXX.py`, not `TPI_MIXDETCT_XXX.py`).
- **Never edit `.mtpl` directly** — it is fully regenerated on compilation.
- After any change to `.py`, run the Pymtpl compiler.

---

## Module Initialization

```python
InitializeNVLClass('TPI_MIXDETCT_XXX', 'TPI_MIXDETCT_XXX', binrange=(4900, 4900))
```

---

## Subflow

| Subflow | Purpose |
|---------|---------|
| `STARTPREPRL1` | Mix detection check before PRL1 begins |

---

## Test Type

`PrimeMixingDetectionTestMethod` with a `configurationFile` path pointing to the mix detection configuration.

---

## BypassPort Logic

```python
BypassPort=Spec("__shared__::DieIndic.DieCombo(-1,1,1,...)")
```

The bypass is controlled by `__shared__::DieIndic.DieCombo(...)` which evaluates the actual die combination present. A multi-die package (more than one die populated) is required for the test to run; single-die configurations bypass it.

---

## Editing Checklist

1. Modify `TPI_MIXDETECT_XXX.py` — update the configuration file path, bypass condition, or binrange.
2. Run the Pymtpl compiler.
3. Verify the generated `.mtpl` reflects the updated test definition.
