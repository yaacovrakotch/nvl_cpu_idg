---
name: add-chainby-directives
description: Analyzes a symbolized MTPL blueprint and its expected expanded output to determine where ChainBy and GoTo <NEXT> directives should be added to the blueprint's Flow/FlowItem Result blocks so that the framework produces the correct chaining behavior.
argument-hint: '[path to symbolized blueprint] [path to expected output file]'
metadata:
  version: 1.0.0
  author: Shiri H
---

# Add ChainBy Directives Skill

You are a specialized agent that compares a **symbolized MTPL blueprint** (before expansion) with its **expected expanded output** (after the framework processes it) to identify which FlowItem Result blocks need `ChainBy <PARAM>;` directives added. You then update the blueprint file with the correct directives.


## Goal

Given:
1. A **symbolized blueprint** file (`.mtpl`) located under `Modules/` containing `\SYMBOL\` placeholders in Flow/FlowItem definitions
2. An **expected output** file (`.mtpl`) located under `Modules/` showing the fully expanded result with concrete chaining (GoTo between variants)
3. A **symbol definition** listing all symbols, their values, and dependency maps

Produce:
1. A **new file** named `<original_name>_chained.mtpl` (in the same folder as the original blueprint) containing the blueprint with `ChainBy <PARAM>;` directives added to the correct Result blocks. The original blueprint file is NOT modified.
2. A **summary** of all changes made

**File naming:** If the input blueprint is `blueprints/SCN_HUB_orig_grouped_symbolized.mtpl`, the output file is `blueprints/SCN_HUB_orig_grouped_symbolized_chained.mtpl`.

---

## Background: ChainBy and GoTo <NEXT> Directives

### ChainBy PARAM;

The `ChainBy PARAM;` directive tells the framework to chain expanded variants of the same FlowItem sequentially. It goes INSIDE a Result block, AFTER the `Return` statement.

**Syntax:**
```
Result <code>
{
    Property PassFail = "Pass";
    Return 1;
    ChainBy DOMAIN;
}
```

**Behavior:**
- For **non-last** variants: the framework replaces `Return X;` with `GoTo <next_variant>;`
- For the **last** variant: the `Return` statement is kept as-is (it becomes the exit point)
- Multi-level chaining uses `>` separator: `ChainBy IP>ARRAYTYPE;`

**Critical Rule:** The `Return` statement MUST remain in the Result block alongside the `ChainBy` directive. The Return acts as the fallback for the last variant. The validator requires every Result block to have a `Return` or `GoTo` statement.

### GoTo <NEXT>;

Used in building-block blueprints to chain between different FlowItems within the same flow (not variants of the same item).

**Syntax:**
```
Result 1
{
    Property PassFail = "Pass";
    GoTo <NEXT> or Return 1;
}
```

**Behavior:**
- If there's a subsequent FlowItem in the flow, the framework replaces this with `GoTo <actual_next_item>;`
- If this is the last FlowItem, it falls back to `Return 1;`
- The `or Return X;` part is REQUIRED (validator enforces termination)

### ChainBy Anchoring (Automatic)

When a Flow has a BYPASS/control FlowItem whose `GoTo` points to a symbolized FlowItem that has `ChainBy`, the framework automatically redirects the GoTo to the **first** variant in the chain. No explicit directive needed for this.

---

## Step 1: Parse the Symbolized Blueprint

### 1.1 Identify Flow Blocks with Symbolized FlowItems

Scan the blueprint for all `Flow <name> { ... }` blocks. For each Flow:
1. Extract all `FlowItem <name> <reference>` entries
2. Identify which FlowItems contain symbol placeholders (e.g., `\DOMAIN\`, `\TEST_TYPE\`, `\FREQ\`)
3. Note the symbol comments above each Flow/FlowItem that declare which symbols are used and their values

### 1.2 Categorize Flow Types

Flows fall into these categories:
- **Parent flows with sub-flow calls**: Contain FlowItems that reference child Flows and are expanded by a parameter
- **Leaf flows with test instances**: Contain FlowItems that reference actual test instances
- **Composite flows**: Intermediate flows that chain domain-specific sub-flows

### 1.3 Extract Result Block Structure

For each symbolized FlowItem, record:
- Which Result codes exist (-2, -1, 0, 1, 2, 3, 4, 5)
- What each Result block contains (Return value, GoTo target, PassFail property)
- Whether it already has a `ChainBy` or `GoTo <NEXT>` directive

---

## Step 2: Parse the Expected Output

### 2.1 Find Expanded Flow Variants

For each symbolized Flow in the blueprint, find all corresponding expanded Flows in the expected output. For example:
- Blueprint: `Flow SCN_HUB_HXX_\FREQ\XSN` → Expected: `Flow SCN_HUB_HXX_F1XSN`, `Flow SCN_HUB_HXX_F2XSN`, etc.
- Blueprint: `Flow VMAXXSN_\FREQ\_\TEST_TYPE\_COMPOSITE` → Expected: `Flow VMAXXSN_F1_ATSPEED_COMPOSITE`, etc.

### 2.2 Identify Chaining Patterns

For each parent flow in the expected output that contains multiple FlowItems referencing sub-flows:

1. **Sequential GoTo Pattern**: Check if FlowItems chain to each other via GoTo
   ```
   FlowItem A_NONR: Result 0/1 → GoTo A_IPU
   FlowItem A_IPU:  Result 0/1 → GoTo A_NPU
   FlowItem A_NPU:  Result 0/1 → GoTo A_MEDIA
   FlowItem A_MEDIA: Result 0/1 → GoTo A_DISPLAY
   FlowItem A_DISPLAY: Result 0/1 → Return
   ```

2. **Determine which Result ports are chained**: Not all Results chain. Check each Result code:
   - If non-last variant has `GoTo <next_variant>` → this port is chained
   - If non-last variant has `Return` → this port is NOT chained
   
3. **Determine the chaining parameter**: The parameter whose values differ across the chained FlowItem names (e.g., NONR/IPU/NPU/MEDIA/DISPLAY → DOMAIN parameter)

### 2.3 Record Chaining Requirements

For each symbolized FlowItem that needs ChainBy, record:
- **Flow name** (in blueprint, with symbols)
- **FlowItem name** (in blueprint, with symbols)
- **Parameter to chain by** (e.g., DOMAIN, TEST_TYPE, FREQ)
- **Result codes that need ChainBy** (e.g., [0, 1] or just [1])
- **Return value for the last variant** (preserved from the expected output's last item)

---

## Step 3: Determine ChainBy Placement Rules

### 3.1 Matching Expected to Blueprint

For each Flow in the expected output that shows chaining:

1. **Identify the corresponding blueprint Flow** by matching the flow name pattern (replacing concrete values with symbols)

2. **Identify the chained FlowItem** in the blueprint (the one with the symbol in its name)

3. **Determine which ports get ChainBy:**
   - Look at a non-last variant in the expected output
   - For each Result code: if the expected output shows `GoTo <next_variant>`, that Result needs `ChainBy`
   - If the expected output shows `Return X` (unchanged), that Result does NOT get ChainBy

4. **Determine the Return value for the ChainBy port:**
   - Look at the LAST variant in the expected output
   - The `Return X;` value in the last variant's chained port = the Return value to use in the blueprint
   - This Return value goes before the `ChainBy` directive

### 3.2 Multi-Level ChainBy

If a FlowItem chains across multiple parameters simultaneously (rare), use `>` separator:
```
ChainBy PARAM1>PARAM2;
```

The order determines nesting: PARAM1 is the outer loop, PARAM2 is the inner loop.

### 3.3 Anchor GoTo Adjustment

For BYPASS/control FlowItems that have `GoTo <symbolized_target>`:
- If the target FlowItem has ChainBy, the framework will automatically redirect to the first variant
- The blueprint should keep the **symbolic** GoTo (e.g., `GoTo SCN_HUB_HXX_\FREQ\XSN_\DOMAIN\;`)
- The framework handles anchoring automatically based on ChainBy presence

---

## Step 4: Create the Output File and Apply Changes

### 4.0 Duplicate the Blueprint

Before making any modifications:
1. **Copy** the original blueprint file to a new file in the **same folder**
2. **Name** the new file: `<original_name_without_extension>_chained.mtpl`
   - Example: `SCN_HUB_orig_grouped_symbolized.mtpl` → `SCN_HUB_orig_grouped_symbolized_chained.mtpl`
3. All subsequent modifications are applied to the **new copy only**. The original file must remain untouched.

### 4.1 Add ChainBy Directives

For each FlowItem that needs chaining:

**Before (example):**
```
FlowItem SCN_HUB_HXX_\FREQ\XSN_\DOMAIN\ SCN_HUB_HXX_\FREQ\XSN_\DOMAIN\
{
    Result -2 { Property PassFail = "Fail"; Return -2; }
    Result -1 { Property PassFail = "Fail"; Return -1; }
    Result 0 { Property PassFail = "Pass"; Return 0; }
    Result 1 { Property PassFail = "Pass"; Return 0; }
}
```

**After (ChainBy added to ports 0 and 1):**
```
FlowItem SCN_HUB_HXX_\FREQ\XSN_\DOMAIN\ SCN_HUB_HXX_\FREQ\XSN_\DOMAIN\
{
    Result -2 { Property PassFail = "Fail"; Return -2; }
    Result -1 { Property PassFail = "Fail"; Return -1; }
    Result 0 { Property PassFail = "Pass"; Return 0; ChainBy DOMAIN; }
    Result 1 { Property PassFail = "Pass"; Return 1; ChainBy DOMAIN; }
}
```

**Key Rules:**
1. Add `ChainBy PARAM;` AFTER the `Return` statement in the Result block
2. The Return value should match what the LAST variant has in the expected output
3. For inline Result blocks (single line), keep it inline: `Result 1 { Property PassFail = "Pass"; Return 1; ChainBy DOMAIN; }`
4. For multi-line Result blocks, add on its own line with matching indentation:
   ```
   Result 1
   {
       Property PassFail = "Pass";
       Return 1;
       ChainBy DOMAIN;
   }
   ```
5. Only add ChainBy to Result blocks that show GoTo chaining in the expected output
6. Do NOT add ChainBy to Result blocks that keep their Return value unchanged (e.g., error ports -2, -1)

### 4.2 Adjust Return Values for Last Variant

The Return value in the blueprint's ChainBy port must match what the **last variant** shows in the expected output:
- If last variant shows `Return 1;` in Result 1 → blueprint should have `Return 1; ChainBy DOMAIN;`
- If last variant shows `Return 0;` in Result 0 → blueprint should have `Return 0; ChainBy DOMAIN;`

### 4.3 Do NOT Modify

- **BYPASS/control FlowItems**: Their GoTo targets stay symbolic (framework handles anchoring)
- **Test instance flows** (leaf flows like `SCN_HUB_HXX_\FREQ\XSN_\DOMAIN\`): These already have internal chaining via explicit GoTo
- **Result blocks with GoTo** already: If a Result already has a `GoTo <target>;`, do not add ChainBy
- **Error ports** (-2, -1): These should never chain

---

## Step 5: Verify the Changes

### 5.1 Validation Checks

After updating the blueprint:

1. **Every Result block must have a Return or GoTo**: ChainBy alone is insufficient. Verify each modified Result still has `Return X;` before the `ChainBy`.

2. **Symbol consistency**: The parameter name in `ChainBy PARAM;` must match a symbol that appears in the FlowItem name and has multiple values.

3. **No duplicate ChainBy**: Each Result block should have at most one ChainBy directive.

4. **Correct scope**: ChainBy only applies to FlowItems that are expanded by the specified parameter. The FlowItem name MUST contain `\PARAM\` (the symbol being chained).

### 5.2 Expected Transformation Verification

For each ChainBy added, mentally verify the transformation:
- Non-last variants: `Return X;` gets replaced by `GoTo <next_variant>;`
- Last variant: `Return X;` is kept as-is
- External GoTo targets pointing to the chained FlowItem get redirected to first variant

---

## Step 6: Generate Summary

Produce a summary listing:
1. Each Flow modified
2. Each FlowItem modified within that Flow
3. The ChainBy parameter added
4. Which Result ports were modified
5. The chaining order (e.g., NONR → IPU → NPU → MEDIA → DISPLAY)

---

## Example: SCN_HUB Blueprint

### Symbol Definitions:
```
DOMAIN: [DISPLAY, IPU, MEDIA, NONR, NPU]
TEST_TYPE: [ATSPEED, STUCKAT]
FREQ: [F1, F2, F3, F4, FBAT, FMIN]
  Dependency: {NONR: [F1,F2,F3,F4,FBAT,FMIN], IPU: [F1,F2,F4,FBAT,FMIN], ...}
VCORNER2: [MAX, MIN, NOM]
STAGE: [BEGINHUB, ENDHUB]
```

### Changes Applied:

| Flow | FlowItem | ChainBy | Ports Modified | Chain Order |
|------|----------|---------|----------------|-------------|
| `SCN_HUB_HXX_\FREQ\XSN` | `SCN_HUB_HXX_\FREQ\XSN_\DOMAIN\` | `DOMAIN` | 0, 1 | NONR→IPU→NPU→MEDIA→DISPLAY |
| `VMAXXSN_\FREQ\_\TEST_TYPE\_COMPOSITE` | `VMAXXSN_\FREQ\_\TEST_TYPE\_COMPOSITE_\DOMAIN\` | `DOMAIN` | 0, 1 | NONR→IPU→NPU→MEDIA→DISPLAY |
| `VMAXXSN_\FREQ\_COMPOSITE` | `VMAXXSN_\FREQ\_\TEST_TYPE\_COMPOSITE` | `TEST_TYPE` | 1 | ATSPEED→STUCKAT |
| `SCN_HUB_HXX_\VCORNER\XSN` | `VMAXXSN_\FREQ\_COMPOSITE` | `FREQ` | 1 | F1→F4 (per dependency) |
| `\STAGE\\VCORNER2\_\TEST_TYPE\_COMPOSITE` | `\STAGE\\VCORNER2\_\TEST_TYPE\_COMPOSITE_\DOMAIN\` | `DOMAIN` | 0, 1 | NONR→IPU→NPU→MEDIA→DISPLAY |
| `SCN_HUB_HXX_\STAGE\\VCORNER2\` | `\STAGE\\VCORNER2\_\TEST_TYPE\_COMPOSITE` | `TEST_TYPE` | 1 | ATSPEED→STUCKAT |
| `\STAGE\\VCORNER2\_\TEST_TYPE\_COMPOSITE` (FMIN variant) | `FMINXSN_\FREQ\_\TEST_TYPE\_COMPOSITE_\DOMAIN\` | `DOMAIN` | 0, 1 | (per domain) |

### Detailed Example — Before/After:

**Flow `SCN_HUB_HXX_\FREQ\XSN` — Before:**
```
FlowItem SCN_HUB_HXX_\FREQ\XSN_\DOMAIN\ SCN_HUB_HXX_\FREQ\XSN_\DOMAIN\
{
    Result -2 { Property PassFail = "Fail"; Return -2; }
    Result -1 { Property PassFail = "Fail"; Return -1; }
    Result 0 { Property PassFail = "Pass"; Return 0; }
    Result 1 { Property PassFail = "Pass"; Return 0; }
}
```

**Flow `SCN_HUB_HXX_\FREQ\XSN` — After:**
```
FlowItem SCN_HUB_HXX_\FREQ\XSN_\DOMAIN\ SCN_HUB_HXX_\FREQ\XSN_\DOMAIN\
{
    Result -2 { Property PassFail = "Fail"; Return -2; }
    Result -1 { Property PassFail = "Fail"; Return -1; }
    Result 0 { Property PassFail = "Pass"; Return 0; ChainBy DOMAIN; }
    Result 1 { Property PassFail = "Pass"; Return 1; ChainBy DOMAIN; }
}
```

Note: Result 1's Return value changed from `0` to `1` because in the expected output, the LAST domain variant (DISPLAY) has `Return 1;` in its Result 1 port (the chain exit passes through).

**Flow `VMAXXSN_\FREQ\_COMPOSITE` — Before:**
```
FlowItem VMAXXSN_\FREQ\_\TEST_TYPE\_COMPOSITE VMAXXSN_\FREQ\_\TEST_TYPE\_COMPOSITE
{
    Result -2 { ... Return -2; }
    Result -1 { ... Return -1; }
    Result 0 { Property PassFail = "Pass"; Return 0; }
    Result 1 { Property PassFail = "Pass"; Return 0; }
}
```

**Flow `VMAXXSN_\FREQ\_COMPOSITE` — After:**
```
FlowItem VMAXXSN_\FREQ\_\TEST_TYPE\_COMPOSITE VMAXXSN_\FREQ\_\TEST_TYPE\_COMPOSITE
{
    Result -2 { ... Return -2; }
    Result -1 { ... Return -1; }
    Result 0 { Property PassFail = "Pass"; Return 0; }
    Result 1 { Property PassFail = "Pass"; Return 1; ChainBy TEST_TYPE; }
}
```

Note: Only Result 1 gets ChainBy because in the expected output, Result 0 keeps `Return 0;` (no GoTo) while only Result 1 gets `GoTo <next_test_type>`.

---

## Edge Cases

### 1. Dependency-Filtered Expansion

When a parameter has a dependency map (e.g., FREQ depends on DOMAIN), the chaining only includes the values valid for that specific context. The ChainBy directive still uses the simple form (`ChainBy FREQ;`) — the framework handles the dependency filtering.

### 2. PassFail Determines Chaining Eligibility

A Result block with `Property PassFail = "Fail"` and a Return 0 that chains in the expected output still gets ChainBy. The determination is purely based on whether the expected output shows GoTo for non-last variants.

However, typically:
- Error ports (-2 = DPS alarm, -1 = system software error) NEVER chain
- "Fail" ports (Result 0 with PassFail="Fail") may or may not chain depending on flow design
- "Pass" ports (Result 1 with PassFail="Pass") commonly chain

### 3. Multi-Line vs Single-Line Result Blocks

Preserve the existing formatting style:
- If the blueprint uses single-line Results: `Result 1 { Property PassFail = "Pass"; Return 1; ChainBy DOMAIN; }`
- If the blueprint uses multi-line Results, add ChainBy on its own line

### 4. Multiple Symbols in FlowItem Name

If a FlowItem name contains multiple symbols (e.g., `\TEST_TYPE\_\DOMAIN\_...`), the ChainBy parameter should be the one that creates the sequential chain in the parent flow. Look at the parent Flow's FlowItem list in the expected output to determine which parameter creates the chain.

### 5. Existing GoTo in Result Blocks

If a Result block already has `GoTo <target>;`, do NOT add ChainBy. These are explicit internal flow connections (e.g., VMIN→CHAIN→FFSEARCH→FFSHMOO within a domain sub-flow).

### 6. BYPASS FlowItems and Anchoring

BYPASS FlowItems (like `CTRL_SCAN_AUX_E_\FREQ\XSN_X_X_X_X_BYPASS`) use `GoTo <symbolized_name>;` in their Result 0. The framework's ChainBy anchoring automatically redirects this GoTo to the first variant of the chained FlowItem. **Do not modify BYPASS FlowItems** — just ensure the ChainBy is correctly placed on the target FlowItem.
