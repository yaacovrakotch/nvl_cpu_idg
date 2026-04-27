---
applyTo: "**/TPI_EDM_XXX/**"
---

# TPI_EDM_XXX — Electrical Die Mark (EDM) Module

## Module Overview

`TPI_EDM_XXX` runs IV curve tests to perform electrical die marking (EDM) for opens/shorts detection across all dies (CPU, GCD, HUB, PCD) and package-level pins. Tests are organized by die/pin group and failure mode (open, short, open-FF, short-FF, diode).

---

## Editing Rules

- **Pymtpl-based module** — `NVL_TPI_EDM_XXX.py` is the **source of truth** (note: filename is `NVL_TPI_EDM_XXX.py`, not `TPI_EDM_XXX.py`).
- **Never edit `.mtpl` directly** — it is fully regenerated on compilation.
- After any change to `.py`, run the Pymtpl compiler.

---

## Module Initialization

```python
InitializeNVLClass('TPI_EDM_XXX', 'TPI_EDM_XXX',
    binrange=[(1080, 1086), (1090, 1096), (1590, 1596)])
```

---

## Subflows

| Subflow | Purpose |
|---------|---------|
| `START` | Initial EDM IV curve tests |
| `DCFF` | DC FF-mode EDM IV curve tests |

---

## Pin Lists

| Pin group | Description |
|-----------|-------------|
| `BASE_EDM` | Base EDM pins |
| `CPU_EDM` | CPU die EDM pins |
| `CPU1_EDM` | CPU1 die EDM pins (S52C) |
| `GCD_EDM` | GCD die EDM pins |
| `HUB_EDM` | HUB die EDM pins |
| `GND_EDM` | Ground reference EDM pins |
| `PCD_TMUX_07` | PCD TMUX pins |

---

## Bin Dictionaries

| Dictionary | Bins |
|------------|------|
| `Bin_OPEN_dict` | Opens failures by pin/die |
| `Bin_SHORT_dict` | Shorts failures by pin/die |
| `Bin_OPEN_FF_dict` | FF-mode opens failures |
| `Bin_SHORT_FF_dict` | FF-mode shorts failures |
| `Diode_Bin_OPEN_dict` | Diode opens failures |

All bins fall within binrange `[(1080, 1086), (1090, 1096), (1590, 1596)]`.

---

## Test Type

All tests use `IVCurve` with per-pin/die parameterization. Each test corresponds to a specific pin group and failure mode.

---

## Editing Checklist

1. Modify `NVL_TPI_EDM_XXX.py` — add/remove pin groups, update bin assignments, or change IV curve parameters.
2. Run the Pymtpl compiler.
3. Verify the generated `.mtpl` reflects the changed tests and flows.
