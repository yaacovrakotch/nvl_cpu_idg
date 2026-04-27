---
applyTo: "**/TPI_TRIALVAR_???/**"
---

# TPI_TRIALVAR_CXX / GXX / HXX / PXX — IP Trial Variable Definitions

## Module Overview

The `TPI_TRIALVAR_*` modules define IP-level trial variables used by the test program. There is one module per dielet:

| Module | Die | File |
|--------|-----|------|
| `TPI_TRIALVAR_CXX` | CPU | `cpu_ip_trials.mtpl` |
| `TPI_TRIALVAR_GXX` | GCD | `gcd_ip_trials.mtpl` |
| `TPI_TRIALVAR_HXX` | HUB | `hub_ip_trials.mtpl` |
| `TPI_TRIALVAR_PXX` | PCD | `pcd_ip_trials.mtpl` |

---

## Editing Rules

- **No Pymtpl source (`.py`)** — these are **direct-MTPL modules**.
- Edit the respective `.mtpl` file directly.
- Associated `.usrv` (user variable) file may also need updating when variables are added or removed.
- No compilation step needed.
- Do NOT create `.py` files unless the module requires programmatic generation.

---

## File Structure

Each module directory contains:
- `<die>_ip_trials.mtpl` — trial variable definitions
- `<die>_ip_trials.flw` — flow layout file (auto-generated, do not edit manually)
- `<die>_ip_trials.usrv` — user variable definitions

---

## Editing Checklist

1. Open the appropriate `.mtpl` file (`cpu_ip_trials.mtpl`, `gcd_ip_trials.mtpl`, etc.).
2. Add, remove, or modify trial variable definitions directly.
3. If user variables changed, update the corresponding `.usrv` file.
4. No compilation required — changes take effect immediately.
