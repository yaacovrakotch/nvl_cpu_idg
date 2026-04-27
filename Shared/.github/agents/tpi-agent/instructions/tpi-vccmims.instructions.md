---
applyTo: "**/TPI_VCCMIMS_XXX/**"
---

# TPI_VCCMIMS_XXX — VCC MIMS Screen Tests Module

## Module Overview

`TPI_VCCMIMS_XXX` performs VCC MIMS (Metal-Insulator-Metal-Stack) screen tests and logs the results to ituff using `PrintToItuff` callbacks. It runs at the `LTTCCOMMON` subflow.

---

## Editing Rules

- **Pymtpl-based module** — `NVL_TPI_VCC_MIMS.py` is the **source of truth** (note: filename is `NVL_TPI_VCC_MIMS.py`).
- **Never edit `.mtpl` directly** — it is fully regenerated on compilation.
- After any change to `.py`, run the Pymtpl compiler.

---

## Module Initialization

```python
InitializeNVLClass('TPI_VCCMIMS_XXX', 'TPI_VCCMIMS_XXX')
```

No binrange is specified (no failing bins defined in this module).

---

## Subflow

| Subflow | Purpose |
|---------|---------|
| `LTTCCOMMON` | MIMS screen tests + ituff logging |

---

## Pin Lists

| List | Description |
|------|-------------|
| `MIMS_pin_list` | 24 MIMS measurement pins |
| `ITUFF_pin_list` | 40+ pins for ituff logging output |

---

## Test Types Used

| Test class | Usage |
|-----------|-------|
| `ScreenTC` | MIMS screen tests, parameterized per pin group |
| `RunCallback` | `PrintToItuff` callback for logging results |

---

## Configuration Dictionaries

| Dictionary | Purpose |
|------------|---------|
| `BypassPort_dict` | Per-test bypass conditions |
| `ScreenTestSet_dict` | Screen test set names per pin/condition |
| `ITUFF_Parameters_dict` | Parameters passed to PrintToItuff per pin group |

---

## Editing Checklist

1. Modify `NVL_TPI_VCC_MIMS.py` — update pin lists, bypass conditions, screen test sets, or ituff parameters.
2. Run the Pymtpl compiler.
3. Verify the generated `.mtpl` reflects the updated tests and flow.
