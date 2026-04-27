---
applyTo: "**/TPI_VCC_XXX/**"
---

# TPI_VCC_XXX — VCC IV Curve Tests Module

## Module Overview

`TPI_VCC_XXX` performs VCC IV curve tests across all dies (HUB, CPU, GCD, PCD) and package-level pins, including DLVR (Distributed Local Voltage Regulator) and LTTC variants. Tests are extensively parameterized by pin group, die, test condition, and bypass condition.

---

## Editing Rules

- **Pymtpl-based module** — `NVL_TPI_VCC_XXX.py` is the **source of truth** (note: filename is `NVL_TPI_VCC_XXX.py`).
- **Never edit `.mtpl` directly** — it is fully regenerated on compilation.
- After any change to `.py`, run the Pymtpl compiler.

---

## Module Initialization

```python
InitializeNVLClass('TPI_VCC_XXX', 'TPI_VCC_XXX', binrange=(800, 899))
```

---

## Pin Lists by Die

| Die / Group | Pin count |
|-------------|-----------|
| HUB | 13 pins |
| CPU | 12 pins |
| GCD | 3 pins |
| PCD | 5 pins |
| PKG | 1 pin |
| DLVR | 18 pins |
| LTTC | 24 pins |

---

## Configuration Dictionaries

| Dictionary | Purpose |
|------------|---------|
| `BypassPort_dict` | Per-die/pin bypass conditions |
| `FSP_dict` | Fast-speed-path test parameters |
| `FSP_START_dict` | Start-of-flow FSP parameters |
| `FSP_LTTC_dict` | LTTC FSP parameters |
| `NFSP_dict` | Non-FSP test parameters |

All bins fall within binrange `(800, 899)`.

---

## Test Types Used

All tests use `IVCurve` with per-pin/die parameterization organized via the configuration dictionaries.

---

## Editing Checklist

1. Modify `NVL_TPI_VCC_XXX.py` — update pin lists, bypass conditions, bin assignments, or IV curve parameters.
2. Run the Pymtpl compiler.
3. Verify the generated `.mtpl` reflects the updated tests and flows.
4. Confirm all bin assignments remain within `(800, 899)`.
