---
applyTo: "**/TPI_PWRCTRL_XXX/**"
---

# TPI_PWRCTRL_XXX — Power Rail Control Module

## Module Overview

`TPI_PWRCTRL_XXX` manages shared power rail sequencing for the NVL test program. For each subflow that requires a specific voltage rail setting (min, max, or nom), it applies the appropriate test condition using `PrimeApplyTestConditionTestMethod`. Additional `PowerSequenceHandler` tests handle power-down/power-up at key points (START and LTTCCOMMON flows).

---

## Editing Rules

- **Pymtpl-based module** — `TPI_PWRCTRL_XXX.py` is the **source of truth**.
- **Never edit `.mtpl` directly** — it is fully regenerated on compilation.
- After any change to `.py`, run the Pymtpl compiler to regenerate `.mtpl`.

---

## Module Initialization

```python
InitializeNVLClass('TPI_PWRCTRL_XXX', 'TPI_PWRCTRL_XXX', tosversion="tos4",
    binrange=(9315, 9316),
    defaultrm2bin=(99933000, 99933999),
    defaultrm1bin=(98933000, 98933999))
```

Counter: `PWRCTRLCTR = 72500000`

---

## Subflow Lists

| List | Subflows |
|------|---------|
| `subflw_list_min` | `STARTSHAREDRAILSMIN1`, `HVBISHAREDRAILSMIN`, `BEGINSHAREDRAILSMIN`, `SPEEDSHAREDRAILSMIN`, `ENDSHAREDRAILSMIN`, `LTTCSHAREDRAILSMIN1`, `STARTPREPRL2` |
| `subflw_list_max` | `BEGINSHAREDRAILSMAX`, `ENDSHAREDRAILSMAX`, `LTTCSHAREDRAILSMAX` |
| `subflw_list_nom` | `STARTSHAREDRAILSNOM`, `BEGINSHAREDRAILSNOM`, `ENDSHAREDRAILSNOM`, `FACTSHAREDRAILSNOM` |

---

## Test Types Used

### PrimeApplyTestConditionTestMethod — SETSRAIL test

Generated for every subflow in all three lists. Sets the shared rail voltages to the appropriate level then writes `SharedRailsIPFollower` user vars via `PostInstance`:

```python
PrimeApplyTestConditionTestMethod(
    name=f'CTRL_X_PWR_K_{subflw}_X_X_X_X_SETSRAIL',
    TestConditionCategory="LEVELS_SETUP",
    TestConditionName="srails_set_x_x_pkg_lvl_<min|max|nom>",
    PostInstance="Call(WriteUserVar(--uservar __shared__::SharedRailsIPFollower.v1p8 --value __shared__::PowerSpec.v1p8_<level> --type Double) | ...)",
    _fitem=Fitem('SAME', r0=pFail(setbin=AUTO, ret=0))
)
```

Test condition names by level:

| Level | TestConditionName |
|-------|------------------|
| min | `srails_set_x_x_pkg_lvl_min` |
| max | `srails_set_x_x_pkg_lvl_max` |
| nom | `srails_set_x_x_pkg_lvl_nom` |

### PowerSequenceHandler — START and LTTCCOMMON flows

`PowerSequenceHandler` tests at `START` and `LTTCCOMMON` handle power-down/power-up sequencing:

```python
PowerSequenceHandler(
    name="CTRL_X_PWR_K_START_X_X_X_X_PWRCTRLTCDC",
    ApplyPowerDown="Always",
    ApplyPowerOn="Always",
    PowerDownTc="BASE::Power_dwn_PKG_xxx_pwrd_zerzer",
    PowerOnTc="BASE::Power_Up_TC_DC_PKG_force_0V_lvl",
    _fitem=Fitem('SAME', r0=pFail(setbin=9315, ret=0))
)
```

Variants at `START`:  `PWRCTRLTCDC` (DC) and `PWRCTRLTCPKG` (PKG)  
Variants at `LTTCCOMMON`: `PWRCTRLTCDC`, `SETRAIL`, `PWRCTRLTCPKG`

---

## Flow Structure

Each subflow in the three lists generates a single flow containing its SETSRAIL test:

```
TPI_PWRCTRL_XXX_<SUBFLOW>   → contains CTRL_X_PWR_K_<SUBFLOW>_X_X_X_X_SETSRAIL
```

The `START` and `LTTCCOMMON` flows contain `PowerSequenceHandler` tests.

---

## Adding or Removing a Subflow — Checklist

1. Add or remove the subflow name from the appropriate list (`subflw_list_min`, `subflw_list_max`, or `subflw_list_nom`) in `TPI_PWRCTRL_XXX.py`.
2. Run the Pymtpl compiler to regenerate `.mtpl`.
3. Verify the new or removed flow entry appears/disappears in the generated `.mtpl`.

