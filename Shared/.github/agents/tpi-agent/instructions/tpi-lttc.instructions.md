---
applyTo: "**/TPI_LTTC_XXX/**"
---

# TPI_LTTC_XXX — Thermal Ramp and Measurement Module

## Module Overview

`TPI_LTTC_XXX` performs thermal control operations: temperature ramping and single-point thermal measurements across all dies (CPU, GCD, HUB, PCD). It runs at LTTC (Low-Temperature Thermal Characterization) subflows.

---

## Editing Rules

- **Pymtpl-based module** — `TPI_LTTC_XXX.py` is the **source of truth**.
- **Never edit `.mtpl` directly** — it is fully regenerated on compilation.
- After any change to `.py`, run the Pymtpl compiler.

---

## Module Initialization

```python
InitializeNVLClass('TPI_LTTC_XXX', 'TPI_LTTC_XXX', binrange=(94939700, 94939799))
```

---

## Subflows

| Subflow | Purpose |
|---------|---------|
| `LTTCRAMP` | Thermal ramp operations |
| `LTTCPOST` | Post-LTTC single-point thermal measurements |

---

## Test Types Used

| Test class | Usage |
|-----------|-------|
| `PrimeThermalRampTestMethod` | Temperature ramping to target |
| `PrimeThermalSingleMeasurementTestMethod` | Single-point temperature measurement |
| `PrimeThermalControlSetTestMethod` | Thermal control set point |

---

## Pin Names (Thermal Sensors)

| Pin name | Die |
|----------|-----|
| `IPC::CPU_TDAU0` | CPU |
| `IPG::GCD_TDAU0` | GCD |
| `IPP::PCD_TDAU0` | PCD |
| `IPH::HUB_TDAU0` | HUB |

---

## Editing Checklist

1. Modify `TPI_LTTC_XXX.py` — add/remove thermal sensor references, update ramp parameters, or add a subflow.
2. Run the Pymtpl compiler.
3. Verify the generated `.mtpl` reflects the updated test definitions and flows.
