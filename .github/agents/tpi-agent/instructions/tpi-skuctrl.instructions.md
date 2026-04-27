---
applyTo: "**/TPI_SKUCTRL_CXX/**"
---

# TPI_SKUCTRL_CXX — SKU Frequency Control Module

## Module Overview

`TPI_SKUCTRL_CXX` sets the pass frequency for CPU clock domains (CORE, RING, ATOM) using the `SkuManager` test method. It operates using the `SetPassFreq` mode driven by the `WRITE_OPTYPE` DFF variable.

---

## Editing Rules

- **Pymtpl-based module** — `TPI_SKUCTRL_CXX.py` is the **source of truth**.
- **Never edit `.mtpl` directly** — it is fully regenerated on compilation.
- After any change to `.py`, run the Pymtpl compiler.

---

## Module Initialization

```python
InitializeNVLClass('TPI_SKUCTRL_CXX', 'TPI_SKUCTRL_CXX', binrange=(9361, 9361))
```

---

## Domain List

```python
domain_list = ["CORE", "RING", "ATOM"]
```

Each domain generates one `SetPassFreq` test instance in the flow.

---

## Test Type Used

### SkuManager (custom BaseMethod class)

Handles per-domain frequency configuration:

```python
class SkuManager(BaseMethod):
    # Parameters: BypassPort, CurrentOptype, ClassHotProcessOptype,
    #             Domain, MidFreqValue, Mode, PreInstance
```

Usage pattern:

```python
SkuManager(
    name="CTRL_X_X_K_" + domain + "_X_X_X_X_SETPASSFREQ",
    BypassPort=-1,
    Domain=domain,
    Mode="SetPassFreq",
    CurrentOptype="__shared__::DFFVars.WRITE_OPTYPE",
    _fitem=Fitem(r0=pFail(setbin=AUTO, ret=0), r2=pPass(ret=1))
)
```

---

## Generated Flow

```
TPI_SKUCTRL_CXX_F5XCR
```

Contains one `SkuManager` test per domain in `domain_list` (CORE, RING, ATOM).

---

## Test Naming Pattern

```
CTRL_X_X_K_<DOMAIN>_X_X_X_X_SETPASSFREQ
```

---

## Adding a New Domain — Checklist

1. Add the domain string to `domain_list` in `TPI_SKUCTRL_CXX.py`.
2. Run the Pymtpl compiler — the new `SetPassFreq` test is generated automatically.
3. Verify the new test instance appears in the generated `.mtpl`.

---

## Adding a New Flow (e.g., CheckMidFreq) — Checklist

A commented-out `CheckMidFreq` template exists in the `.py` for each domain. To activate:

1. Uncomment the `midfreq_test` block in `TPI_SKUCTRL_CXX.py`.
2. Set the desired `MidFreqValue` (e.g., `"F4"`).
3. Add the test to `freqtest_list` (already done in the commented template).
4. Define a separate `Flow(...)` if a dedicated mid-freq flow is needed.
5. Run the Pymtpl compiler.

---

## Contacts

Refer to the `owner.txt` file in the module directory for the current module owner.
