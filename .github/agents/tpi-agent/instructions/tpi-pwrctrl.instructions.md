---
applyTo: "**/TPI_PWRCTRL_CXX/**"
---

# TPI_PWRCTRL_CXX — Power Control Module

## Module Overview

`TPI_PWRCTRL_CXX` handles the IPC CPU power-up sequence for the `STARTCPUNOM` subflow. It uses `PowerSequenceHandler` to apply the IPC power-down and power-up timing configurations.

---

## Editing Rules

- **Pymtpl-based module** — `TPI_PWRCTRL_CXX.py` is the **source of truth**.
- **Never edit `.mtpl` directly** — it is fully regenerated on compilation.
- After any change to `.py`, run the Pymtpl compiler.

---

## Module Initialization

```python
InitializeNVLClass(module_name, module_name, tosversion="tos4")
```

No binrange is defined — this module does not assign fail bins.

---

## Test Type Used

### PowerSequenceHandler

Applies a named power-down and power-up timing configuration:

```python
PowerSequenceHandler(
    name="CTRL_X_PWR_K_STARTCPUNOM_X_X_X_X_PWRUPTCIPCPU",
    ApplyPowerDown="Always",
    ApplyPowerOn="Always",
    PowerDownTc="CPU_IP_BASE::Power_dwn_IPC_xxx_pwrd_zerzer",
    PowerOnTc="CPU_IP_BASE::Power_Up_TC_IPC_nom",
    _fitem=Fitem('SAME', r0=pFail(setbin=90931100, ret=0))
)
```

---

## Generated Flow

```
TPI_PWRCTRL_CXX_STARTCPUNOM
```

Contains the single `CTRL_X_PWR_K_STARTCPUNOM_X_X_X_X_PWRUPTCIPCPU` test instance.

---

## Test Naming Pattern

```
CTRL_X_PWR_K_<SUBFLOW>_X_X_X_X_<SUFFIX>
```

---

## Adding Content

If additional power sequencing tests are needed in future subflows:

1. Define additional `PowerSequenceHandler` instances in `TPI_PWRCTRL_CXX.py`.
2. Name tests using the `CTRL_X_PWR_K_<SUBFLOW>_X_X_X_X_<SUFFIX>` convention.
3. Define a new `Flow(...)` for the subflow.
4. Run the Pymtpl compiler to regenerate `.mtpl`.

---

## Contacts

Refer to the `owner.txt` file in the module directory for the current module owner.
