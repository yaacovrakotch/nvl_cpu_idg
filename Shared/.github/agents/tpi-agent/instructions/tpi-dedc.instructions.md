---
applyTo: "**/TPI_DEDC_XXX/**"
---

# TPI_DEDC_XXX — Dynamic EDC/Recovery Callback Module

## Module Overview

`TPI_DEDC_XXX` implements the dynamic EDC (Engineering Data Collection) and recovery callback mechanism. It contains a single `DedcRVCallbackTC` test that controls EDC mode and recovery flow behavior at runtime.

---

## Editing Rules

- **Pymtpl-based module** — `TPI_DEDC_XXX.py` is the **source of truth**.
- **Never edit `.mtpl` directly** — it is fully regenerated on compilation.
- After any change to `.py`, run the Pymtpl compiler.

---

## Module Initialization

```python
InitializeNVLClass('TPI_DEDC_XXX', 'TPI_DEDC_XXX', binrange=(9300, 9300),
    defaultrm2bin=(99937500, 99937999),
    defaultrm1bin=(98937500, 98937999))
```

---

## Counter

```python
DEDCCTR = 93005480
```

---

## Subflow

| Subflow | Purpose |
|---------|---------|
| `INIT` | Entry point — executes the DEDC callback |

---

## Test Type

The module uses a single `DedcRVCallbackTC` test with parameters:

| Parameter | Description |
|-----------|-------------|
| `Mode` | Operating mode for the callback |
| `ForceFlow` | Whether to force a flow change on certain results |
| `TestTimeSoftCap` | Soft cap on test execution time |
| `UseLegacyBinning` | Whether to use legacy or new binning |

---

## Editing Checklist

1. Modify the `DedcRVCallbackTC` parameters in `TPI_DEDC_XXX.py`.
2. Run the Pymtpl compiler.
3. Verify the generated `.mtpl` reflects the parameter changes.
