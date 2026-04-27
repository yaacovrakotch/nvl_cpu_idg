---
applyTo: "**/TPI_MOTEST_XXX/**"
---

# TPI_MOTEST_XXX — Module-Only Test Placeholder

## Module Overview

`TPI_MOTEST_XXX` is a placeholder module for module-only tests (tests that run only during module-only test mode, bypassed during normal production flow).

---

## Editing Rules

- **No Pymtpl source (`.py`)** — this is a **direct-MTPL module**.
- Edit `TPI_MOTEST_XXX.mtpl` directly.
- No compilation step needed.
- Do NOT create a `.py` file unless the module grows to require programmatic generation (5+ repeated test patterns or complex logic).

---

## Adding Content

Follow these conventions when adding content:

1. Define all test instances in `.mtpl` before any `Flow` blocks.
2. Name tests using the standard TPI convention:
   ```
   CTRL_X_<TESTTYPE>_K_<SUBFLOW>_X_X_X_X_<SUFFIX>
   ```
3. Add a `TPI_MOTEST_XXX_SubBinDefinitions.sbdefs` file if any failing bins are needed.
4. Place new flows after all test instance definitions.
5. Use the standard `module.mconfig` file for pattern patch configuration — do not add it inline to `.mtpl`.
