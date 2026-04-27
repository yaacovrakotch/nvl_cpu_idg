---
applyTo: "**/TPI_PUP_XXX/**"
---

# TPI_PUP_XXX — Power-Up Sequencing Module

## Module Overview

`TPI_PUP_XXX` manages power-up (PUP) sequencing setup. It registers callbacks, configures plist modifications, sets up PUP test conditions, and handles test-plan-end power-down cleanup.

---

## Editing Rules

- **Pymtpl-based module** — `TPI_PUP_XXX.py` is the **source of truth**.
- **Never edit `.mtpl` directly** — it is fully regenerated on compilation.
- After any change to `.py`, run the Pymtpl compiler.

---

## Module Initialization

```python
InitializeNVLClass('TPI_PUP_XXX', 'TPI_PUP_XXX', binrange=(9312, 9312))
```

---

## Subflows

| Subflow | Purpose |
|---------|---------|
| `INIT` | Register callbacks and set up plist modifications |
| `TESTPLANENDFLOW` | Power-down cleanup at test plan end |

---

## Test Types Used

| Test class | Usage |
|-----------|-------|
| `PrimeCallbacksRegistrarTestMethod` | Registers runtime callbacks |
| `PlistModificationsBase` | Configures plist modifications |
| `PlistConfigTC` | Applies plist configuration |
| `PrimePUPTestMethod` | Executes PUP test sequence |

---

## Common Test Names

| Test name | Purpose |
|-----------|---------|
| `RESTORE` | Restore from power-down state |
| `PUP_Setup` | Power-up test setup |
| `SKIP_SHORT` / `SKIP_LONG` | Short/long skip configurations |
| `PRINTITUFF` | Print PUP results to ituff |

---

## Editing Checklist

1. Modify `TPI_PUP_XXX.py` — add/remove tests, change parameters, update plist configuration.
2. Run the Pymtpl compiler.
3. Verify the generated `.mtpl` reflects the updated tests and flow.
