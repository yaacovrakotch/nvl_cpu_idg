---
applyTo: "**/TPI_SHOPS_XKP*/**"
---

# TPI_SHOPS_XKPKGDT / TPI_SHOPS_XKPKGMB — Package Shorts/Opens Module

## Module Overview

`TPI_SHOPS_XKPKGDT` and `TPI_SHOPS_XKPKGMB` implement package-level shorts and opens (SHOPS) screening for the NVL package (DT and MB variants respectively). Both modules share a single Pymtpl source file.

---

## Editing Rules

- **Pymtpl-based module** — `TPI_SHOPS_XKX.py` is the **shared source of truth** for both `TPI_SHOPS_XKPKGDT` and `TPI_SHOPS_XKPKGMB`.
- Both modules' directories contain a copy of `TPI_SHOPS_XKX.py`.
- **Never edit `.mtpl` directly** — it is fully regenerated on compilation.
- After any change to `.py`, run the Pymtpl compiler for **both** modules.

---

## Bin Definitions

| Bin constant | Value | Description |
|-------------|-------|-------------|
| `UPPER_OVERFLOW_BIN` | 1042 | Upper diode overflow |
| `UPPER_SHORTS_BIN` | 1062 | Upper diode shorts |
| `UPPER_OPENS_BIN` | 1562 | Upper diode opens |

---

## Test Types Used

All tests use `IVCurve` test method.

| Function | Purpose |
|----------|---------|
| `get_upper_diode_test()` | Generates upper diode IV curve test |
| `get_lower_diode_test()` | Generates lower diode IV curve test |
| `dc_composite()` | DC composite test |
| `shops_flow()` | Generates the SHOPS flow |

---

## TMUX Configurations

Eight TMUX configurations are defined for PCD. Each configuration targets a subset of package pins and uses a unique TMUX setup. These are parameterized loops in `TPI_SHOPS_XKX.py`.

---

## Editing Checklist

1. Modify `TPI_SHOPS_XKX.py` in the appropriate module directory.
2. Run the Pymtpl compiler on both `TPI_SHOPS_XKPKGDT` and `TPI_SHOPS_XKPKGMB` if the change applies to both.
3. Verify the generated `.mtpl` reflects the updated tests and flows for the correct variant.
