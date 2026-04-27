---
name: blueprint
description: 'Read, query, and update the NVL Blueprint status Excel file (NVL_Blueprint.xlsx). Use when asked about blueprint status, NVL subflow, test program subflows for CPU, GCD, HUB, or PCD dielets, color-coded status, or when the user wants to update a status value, WW (workweek), owner, or any cell in the blueprint tracker. Triggers: blueprint, subflow status, WW update, blueprint Excel, NVL schedule, dielet subflows.'
user-invocable: true
---

# NVL Blueprint Excel Skill

This skill reads and updates the NVL Blueprint status Excel file:

```
Shared/BaseInputs/Common/Common_Files/NVL_Blueprint.xlsx
```

The file tracks top-level and sub-level test program subflows across 4 dielets — **CPU, GCD, HUB, PCD** — and is color-coded to indicate structure. This skill drives a Python CLI script (`blueprint.py`) that outputs structured JSON for comprehension and writes updates back to the file in-place.

For blueprint edits, prefer the high-level slot workflow over raw cell edits. The user will usually describe changes using `SimplerBPView`, and the script will infer the required `FullBP` companion rows.

The script is intentionally limited to these two sheets:
- `SimplerBPView`
- `FullBP`

All other workbook sheets are ignored.

The script also supports a ProgramFlows sync workflow that reads blueprint topology from `FullBP` and updates the managed `ProgramFlows*.py` source files for one or more BOMs. This workflow is source-only: it edits `.py` files and does not regenerate `.mtpl` output.

When the user requests a ProgramFlows subflow-topology change, this skill should treat the blueprint as a separate but related surface of record:
- Ask whether the blueprint should also be updated for any subflow add/remove/reorder/reroute request
- Do not ask that question for module-only edits inside an existing subflow
- If a new subflow is being added and the user does not request module content, default the ProgramFlows source update to a placeholder scaffold containing only the appropriate leading `TPI_FLWFLGS` entry plus the file-family default ports

For human change requests, the primary anchor is:
- `FLOWDEF:ALL:Flow`

That row defines the blueprint slot sequence in `SimplerBPView`. The script now exposes a `slot_view` model keyed on each `FLOWDEF:ALL:Flow` cell, with the corresponding CPU/GCD/HUB/PCD flows attached.

`FullBP` is treated as the authoritative source for `FLOWDEF:ALL:FlowType` (`SubFlow` vs `SubParFlow`). When reading `SimplerBPView`, the script resolves matching `FLOWDEF:ALL:Flow` names back to `FullBP` and includes the matched `FlowType` when available.

For insert planning, the script now accounts for every non-empty row label in `FullBP` column A, not just the `FLOWDEF:*` subset. That includes top-level rows such as:
- `TOS_EXEC_FLOW`
- `TP_EXEC_FLOW`
- `TOP_FLOW:Flow`
- `TOP_FLOW:FlowType`
- `TOP_FLOW:PortRange`
- `TOP_FLOW:DieletType`

Unknown future row labels in `FullBP` are discovered dynamically from column A and are planned by template copy or reported as ambiguous if equally good templates disagree.

For `insert-slot` planning, the script also uses the requested subflow name as a metadata hint. If the name clearly indicates a dielet such as `CPU`, `GCD`, `HUB`, or `PCD`, or a scope family such as `PKG` or `IP*`, the planner narrows the `FLOWDEF:ALL:DieletType`, `FLOWDEF:ALL:Scope`, and `FLOWDEF:ALL:PortRange` inference onto workbook siblings that already match that hint. Explicit CLI overrides still win, and conflicting overrides are reported as blocking issues instead of being silently applied.

## Session Start — Required Clarification

At the very beginning of every blueprint session, before reading or modifying any data, ask the user:

> **Which BOM are you working with?** (e.g., `Class_NVL_S28C`, `Class_NVL_S52C`, `Class_NVL_H16C`, etc.)

Do not proceed with any query, update, or sync operation until the BOM is confirmed. All subsequent `--bom` arguments must use the value the user provides here.

If the user's request already contains an explicit BOM name, confirm it back to the user before proceeding rather than asking again.

---

## When to Use This Skill

- User asks about the NVL blueprint, subflow change
- User mentions: blueprint, subflow, dielet subflows

## Prerequisites

- `openpyxl` Python package must be installed:
  ```powershell
  pip install openpyxl
  ```
- All commands must be run from the **repo root** directory

## Script Location

```
.github/skills/blueprint/script/blueprint.py
```

The Excel file path is **fixed** inside the script (relative to repo root):
```
Shared/BaseInputs/Common/Common_Files/NVL_Blueprint.xlsx
```

For safe validation on a temporary workbook copy, you can override the target workbook with the `BLUEPRINT_EXCEL_PATH` environment variable:

```powershell
$env:BLUEPRINT_EXCEL_PATH = (Resolve-Path ".github\skills\blueprint\tmp\validation_blueprint.xlsx").Path
python .github\skills\blueprint\script\blueprint.py --read
```

When the override is unset, the script falls back to the default workbook under `Shared`.

---

## Workflow

### Step 1 — Understand the File Structure

Always start with `--read` to discover sheet names and column layout before querying or updating. This is the comprehension step.

**PowerShell (Windows):**
```powershell
python .github\skills\blueprint\script\blueprint.py --read
```

**Bash (Linux/Mac):**
```bash
python .github/skills/blueprint/script/blueprint.py --read
```

The JSON output contains:
- `all_sheets` — list of all sheet names in the workbook
- `allowed_sheets` — the subset this skill will operate on (`SimplerBPView`, `FullBP`)
- `sheets` — for each allowed sheet: every row with row number, column letter, cell value, and background `color` (ARGB hex or `null`)
- `slot_view` — structured blueprint slots anchored on `FLOWDEF:ALL:Flow`; each slot includes `all_flow`, `all_flow_type`, and dielet flows (`cpu_flow`, `gcd_flow`, `hub_flow`, `pcd_flow`)
- when `SimplerBPView` is read, matched `FullBP` top-level metadata is also exposed through `resolved_from_fullbp` when available

To limit output to one sheet:
```powershell
python .github\skills\blueprint\script\blueprint.py --read --sheet "SimplerBPView"
```

> **Tip**: For change requests like "add a subflow after X", use `slot_view` and anchor on `all_flow.value` first. Do not anchor on dielet rows first.

---

### Step 2 — Locate a Specific Row

Before updating, use `--query` to find the exact row and confirm the column layout:

```powershell
python .github\skills\blueprint\script\blueprint.py --query "STARTPCDPATMODSPKG"
```

```powershell
python .github\skills\blueprint\script\blueprint.py --query "VStartPCDPost" --sheet "SimplerBPView"
```

- Search is **case-insensitive** and matches any cell in the row
- Returns matching rows with row numbers, column letters, values, and colors
- Also returns `slot_matches`, which is the preferred result for blueprint-aware reasoning
- Use `slot_matches` to identify the slot anchor (`all_flow`) before editing cells directly

---

### Step 3 — Apply the Update

#### ⚠️ Mandatory Pattern Check — Required Before Any Slot Insert

Before constructing any `--insert-slot` or `--report-ambiguities` command, always run `--query` on the **anchor flow** (or the nearest sibling) and inspect its `slot_matches` result. This step is **not optional** and **not skippable**.

```powershell
python .github\skills\blueprint\script\blueprint.py --query "<anchor_flow>"
```

In the `slot_matches` result, check `cpu_flow`, `gcd_flow`, `hub_flow`, `pcd_flow` for the sibling slot:

**Pattern B — Solo slots (each dielet name IS its own `FLOWDEF:ALL:Flow` entry)**
- `cpu_flow: null`, `gcd_flow: null`, `hub_flow: null`, `pcd_flow: null`
- Real examples from this workbook: `ENDCPUPKG`, `ENDGCDPKG`, `ENDHUBPKG`, `ENDPCDPKG`
- ✅ Each new slot must be inserted individually, one `--insert-slot` call per slot
- ❌ Do **NOT** use `--dielet-flow` for any of these inserts
- ⚠️ A dielet prefix in the name (`ENDCPUVMAXPKG`) does **not** mean it is a child — the prefixed name IS the `FLOWDEF:ALL:Flow` value itself

**Pattern A — Parent-child slots (neutral shared name with per-dielet children)**
- `cpu_flow: "ENDCPUPKG"`, `gcd_flow: "ENDGCDPKG"`, etc. — one or more non-null
- Real examples: `ENDPKG`, `STARTPKG`, `BEGIN` — the `FLOWDEF:ALL:Flow` is a neutral alias
- ✅ Use a single `--insert-slot` with `--dielet-flow CPU=... --explicit-dielet-subflows`

**Name signal (supplementary hint — never the sole determiner):**
- New flow name **contains** a dielet identifier (`CPU`, `GCD`, `HUB`, `PCD`) → strong indicator of Pattern B
- New flow name is neutral (no dielet identifier) → defer entirely to the sibling `slot_matches` result

**Decision rules — no guesswork permitted:**

| Sibling pattern | Name signal | Action |
|---|---|---|
| Pattern B (all null) | Matches (dielet in name) | Preview the planned N solo slots to the user, wait for acknowledgement, then apply |
| Pattern A (non-null children) | Matches (neutral name) | Preview the planned parent+children structure to the user, wait for acknowledgement, then apply |
| Any pattern | Conflict (signals disagree) | **STOP** — show the user both signals and the contradiction, ask which is correct, do not apply any write until answered |
| Anchor not found or ambiguous | — | **STOP** — ask the user to confirm the pattern before proceeding |

**Preview format** (required before every write): always describe the exact slots that will be inserted, including whether they have dielet children or not, so the user can catch mismatches before they are written.

---

#### Preferred Option — High-Level Slot Insert

Use this when the user asks for a blueprint change such as adding a subflow before/after an existing `FLOWDEF:ALL:Flow` entry in `SimplerBPView`.

Dry-run first to inspect inferred metadata and ambiguity handling:

```powershell
python .github\skills\blueprint\script\blueprint.py --report-ambiguities --anchor-flow "STARTPCDPATMODSPKG" --position after --new-flow "StartPost" --mode parallel --dielet-flow CPU=VStartCPUPost --dielet-flow PCD=VStartPCDPost --explicit-dielet-subflows
```

If the plan is acceptable, apply it:

```powershell
python .github\skills\blueprint\script\blueprint.py --insert-slot --anchor-flow "STARTPCDPATMODSPKG" --position after --new-flow "StartPost" --mode parallel --dielet-flow CPU=VStartCPUPost --dielet-flow PCD=VStartPCDPost --explicit-dielet-subflows --confirm-owner dielet
```

Behavior:
- Anchor is resolved from `SimplerBPView`
- `FullBP` companion rows are planned for every non-empty label in `FullBP` column A using nearby structural templates
- This includes top-level rows (`TOS_EXEC_FLOW`, `TP_EXEC_FLOW`, `TOP_FLOW:*`), `FLOWDEF:ALL:*` metadata, and participating dielet metadata rows such as `FLOWDEF:CPU:Scope`, `FLOWDEF:CPU:FlowType`, `FLOWDEF:CPU:PortRange` (and corresponding GCD/HUB/PCD rows when those dielets participate)
- If the user only asked to add or reorder a `FLOWDEF:ALL:Flow` slot and did not explicitly specify dielet-specific child subflows, leave `FLOWDEF:CPU:Flow`, `FLOWDEF:GCD:Flow`, `FLOWDEF:HUB:Flow`, and `FLOWDEF:PCD:Flow` empty for that slot
- Do not synthesize `--dielet-flow` arguments from naming conventions, owner classification, or guessed ProgramFlows topology; only use `--dielet-flow` when **both** the mandatory sibling pattern check (above) confirms Pattern A **and** the user has explicitly named those child subflows — the name containing a dielet identifier alone is never sufficient justification for using `--dielet-flow`
- The CLI now enforces this rule: any use of `--dielet-flow` must also include `--explicit-dielet-subflows`
- The requested subflow name is used as an additional workbook-driven hint for `FLOWDEF:ALL:DieletType`, `FLOWDEF:ALL:Scope`, and `FLOWDEF:ALL:PortRange` when the name is unambiguous
- The requested subflow name is also classified as `shared` or `dielet`; if that ownership is not clear enough, the insert is blocked until the user clarifies it
- Applying an insert now requires explicit ownership confirmation via `--confirm-owner` even when the naming convention is an exact match
- Style/color is copied only from a FullBP donor that matches the resolved scope and dielet-type family; if the style donor is missing or mismatched, the insert is blocked
- Dry-run output includes `fullbp_row_plan`, a row-by-row plan marking each `FullBP` label as `explicit`, `inferred`, `copied_from_template`, `blank`, or `ambiguous`
- If some inferred `FullBP` metadata is ambiguous, those rows are reported individually while non-ambiguous rows remain planned
- Dry-run output also includes `owner_classification` and `confirmation_required`
- If the style template itself is ambiguous or incompatible with the resolved metadata, the insert is blocked and the issue is reported

#### High-Level Slot Delete

Use this when the user asks to remove an existing slot identified from `SimplerBPView`.

Dry-run first to confirm the target slot mapping:

```powershell
python .github\skills\blueprint\script\blueprint.py --delete-slot --target-flow "STARTPCDPATMODSPKG" --dry-run
```

If the target is correct, apply it:

```powershell
python .github\skills\blueprint\script\blueprint.py --delete-slot --target-flow "STARTPCDPATMODSPKG"
```

Behavior:
- Target is resolved from `SimplerBPView`
- Matching `FullBP` slot is identified by the same `FLOWDEF:ALL:Flow` value
- If the flow name occurs more than once, use `--occurrence N`
- Dry-run is recommended before any delete

#### Option A — Update by Row + Column Coordinates

Use when you have the exact row number and column from Step 2:

```powershell
python .github\skills\blueprint\script\blueprint.py --update-cell --sheet "SimplerBPView" --row 15 --col E --value "STARTPCDNOM"
```

| Argument | Description |
|----------|-------------|
| `--sheet` | Sheet name (required) |
| `--row`   | 1-based row number |
| `--col`   | Column letter (`A`, `B`, ...) or 1-based integer |
| `--value` | New value (auto-detected as int, float, or string) |

#### Option B — Update by Matching a Column Value

Use when you know a unique identifier (e.g., subflow name) and want to update another column in the same row:

```powershell
python .github\skills\blueprint\script\blueprint.py --update-match --sheet "FullBP" --match-col A --match-val "FLOWDEF:ALL:FlowType" --update-col J --update-val "SubParFlow"
```

| Argument | Description |
|----------|-------------|
| `--sheet`      | Sheet name (required) |
| `--match-col`  | Column containing the identifier to search |
| `--match-val`  | Exact value to match (**case-sensitive**, matches entire cell) |
| `--update-col` | Column to update in the matched row |
| `--update-val` | New value to write |

> **Backup**: Before every write, the script automatically saves a copy to `Shared/BaseInputs/Common/Common_Files/NVL_Blueprint.xlsx.bak`. To restore, rename the `.bak` file back to `.xlsx`.

> **Validation Tip**: When `BLUEPRINT_EXCEL_PATH` is set, the backup is created next to that override workbook instead of next to the default workbook.

---

### Step 4 — Verify the Update

Re-query to confirm the change was applied correctly:

---

## ProgramFlows Sync

Use this when the user wants blueprint topology reflected into ProgramFlows Python source files.

Before applying this workflow, decide whether the request is actually a topology change:
- Topology changes include adding a subflow, deleting a subflow, reordering subflows, changing wrapper routing, or changing which top flow owns a subflow
- Module-only edits inside an existing subflow are not topology changes and should not automatically trigger a blueprint update question

For topology changes:
- Ask whether the blueprint should also be updated if the user did not already specify that intent
- Ask for BOM when it is not mentioned in the request or the session has not yet established a BOM context
- Ask for repo scope (`shared`, `dielet/s` or `both`) when it is not mentioned by the use and ask which dielet if not the root directory

For new subflow additions:
- Default to placeholder-only scaffolding in ProgramFlows source files only when the sync is creating a new missing subflow and the user did not explicitly request module content
- If a matching subflow already exists in ProgramFlows source, preserve it as-is unless the user explicitly requests module content changes
- The placeholder should contain only the required leading `TPI_FLWFLGS_XXX` or `TPI_FLWFLGS_<IP>XX` line and the default port family for that file type
- Shared placeholder placement should follow the authoritative `FullBP` slot order, not nearest-neighbor heuristics in the existing file

Scope rules:
- `Shared/` contains the common ProgramFlows sources reused by every dielet repo
- the active workspace repo contributes the dielet-specific ProgramFlows sources for CPU, GCD, HUB, or PCD
- the sync updates source `.py` files only; it does not compile or regenerate `.mtpl`

Dry-run first:

```powershell
python .github\skills\blueprint\script\blueprint.py --plan-programflows-sync --bom Class_NVL_S28C --repo-scope both
```

Apply after reviewing the JSON plan:

```powershell
python .github\skills\blueprint\script\blueprint.py --apply-programflows-sync --bom Class_NVL_S28C --repo-scope both
```

Useful variants:

```powershell
python .github\skills\blueprint\script\blueprint.py --plan-programflows-sync --bom Class_NVL_S28C --bom Class_NVL_S52C --repo-scope shared
```

```powershell
python .github\skills\blueprint\script\blueprint.py --plan-programflows-sync --bom Class_NVL_S28C --repo-scope dielet
```

Current sync coverage:
- shared package `MAIN_code` ordering in `ProgramFlowsSharedPKG.py`
- shared parallel wrapper inventory via `prl_dict` in `ProgramFlows.py`
- dielet package subflow ordering in `ProgramFlows<dielet>.py`
- dielet IP wrapper ordering in `IP<dielet>_FLOWS.py`

The dry-run JSON includes:
- active dielet repo detected from the workspace name
- requested BOM list and repo scope
- per-file change status and planned ordering details
- `preserved_placeholder_groups` for existing managed subflows that were already placeholder-only and were kept unchanged
- `preserved_non_placeholder_groups` for existing managed subflows whose bodies contain executable content beyond the default placeholder and were kept unchanged; review these before apply when the user expected only newly scaffolded placeholders

```powershell
python .github\skills\blueprint\script\blueprint.py --query "StartPost" --sheet "SimplerBPView"
```

---

## Complete Command Reference

| Command | Purpose | Required Arguments |
|---------|---------|-------------------|
| `--read` | Dump all sheets as JSON (values + colors) | — |
| `--read --sheet <name>` | Dump one sheet only | `--sheet` |
| `--query <text>` | Find rows containing text (all sheets) | `<text>` |
| `--query <text> --sheet <name>` | Find rows containing text (one sheet) | `<text>`, `--sheet` |
| `--report-ambiguities` | Dry-run an insert-slot request and list inferred values plus unresolved fields | `--anchor-flow`, `--position`, `--new-flow`, `--mode` |
| `--insert-slot` | Insert a slot using `SimplerBPView` as the anchor surface | `--anchor-flow`, `--position`, `--new-flow`, `--mode` |
| `--delete-slot` | Delete a slot using `SimplerBPView` as the anchor surface | `--target-flow` |
| `--update-cell` | Update one cell by coordinates | `--sheet`, `--row`, `--col`, `--value` |
| `--update-match` | Find row by value, update another column | `--sheet`, `--match-col`, `--match-val`, `--update-col`, `--update-val` |

---

## Understanding Color Codes

The Excel file uses background fill colors primarily to show structural grouping, not just status. The `--read` and `--query` output includes a `"color"` field per cell:

- `"color": null` — No fill (default white background)
- `"color": "FF92D050"` — Green (typically complete / on-track)
- `"color": "FFFFC000"` — Orange/amber (typically in-progress / at-risk)
- `"color": "FFFF0000"` — Red (typically blocked / behind)
- `"color": "FF00B0F0"` — Blue (typically planned / future)
- `"color": "theme:X,tint:Y"` — Theme-based color (Excel theme palette entry)

In practice for these blueprint rows:
- `FLOWDEF:ALL:Flow` is the slot anchor row
- CPU/GCD/HUB/PCD flow rows use color mainly as dielet/family grouping
- `FLOWDEF:ALL:FlowType` from `FullBP` tells whether a slot is `SubFlow` or `SubParFlow`

The format is ARGB hex: first two digits are alpha (`FF` = fully opaque), followed by 6-digit RGB.

---

## Examples

**Read entire workbook:**
```powershell
python .github\skills\blueprint\script\blueprint.py --read
```

**Read SimplerBPView only:**
```powershell
python .github\skills\blueprint\script\blueprint.py --read --sheet "SimplerBPView"
```

**Dry-run a parallel slot insertion:**
```powershell
python .github\skills\blueprint\script\blueprint.py --report-ambiguities --anchor-flow "STARTPCDPATMODSPKG" --position after --new-flow "StartPost" --mode parallel --dielet-flow CPU=VStartCPUPost --dielet-flow PCD=VStartPCDPost
```

**Insert the new parallel slot:**
```powershell
python .github\skills\blueprint\script\blueprint.py --insert-slot --anchor-flow "STARTPCDPATMODSPKG" --position after --new-flow "StartPost" --mode parallel --dielet-flow CPU=VStartCPUPost --dielet-flow PCD=VStartPCDPost --confirm-owner dielet
```

**Dry-run deletion of an existing slot:**
```powershell
python .github\skills\blueprint\script\blueprint.py --delete-slot --target-flow "STARTPCDPATMODSPKG" --dry-run
```

**Find all rows mentioning "PTH":**
```powershell
python .github\skills\blueprint\script\blueprint.py --query "PTH"
```

**Find a slot anchor in SimplerBPView:**
```powershell
python .github\skills\blueprint\script\blueprint.py --query "STARTPCDPATMODSPKG" --sheet "SimplerBPView"
```

**Update a specific cell directly in SimplerBPView:**
```powershell
python .github\skills\blueprint\script\blueprint.py --update-cell --sheet "SimplerBPView" --row 15 --col E --value "STARTPCDNOM"
```

**Update the FullBP flow type row for a specific slot column:**
```powershell
python .github\skills\blueprint\script\blueprint.py --update-match --sheet "FullBP" --match-col A --match-val "FLOWDEF:ALL:FlowType" --update-col J --update-val "SubParFlow"
```

---

## Troubleshooting

| Error Message | Cause | Fix |
|---------------|-------|-----|
| `openpyxl is not installed` | Missing Python package | `pip install openpyxl` |
| `Excel file not found: ...` | Wrong working directory | Run from the repo root |
| `Sheet 'X' is not supported` | Sheet is outside the supported blueprint views | Use only `SimplerBPView` or `FullBP` |
| `Sheet 'X' not found` | Wrong sheet name | Run `--read` first to see `all_sheets` |
| `No row found where column...` | Exact match failed | Use `--query` to find the exact string; `--match-val` is case-sensitive and must match the full cell value |
| `Row N is out of range` | Row number too high | Check max row from `--read` output |
| `Invalid column: 'X'` | Bad column argument | Use a letter (`A`, `B`) or a 1-based integer (`1`, `2`) |

---

## Interpreting `--plan-programflows-sync` Output — Known Non-Issues

When running `--plan-programflows-sync` to compare the blueprint against existing `.py` files, the tool reports `definition_order`, `extra_unmanaged`, and `TopFlow` diffs. Apply the following rules before flagging anything as an issue.

### Rule 1 — TopFlow refs are authoritative for execution order; `definition_order` is not

The `definition_order` section reports the sequence in which subflow groups appear in the `MAIN_code` text block of the `.py` file. This is **not** the execution sequence. Actual execution order is determined by each `*_TopFlow` routing block (e.g., `LTTC_TopFlow`, `SPEED_TopFlow`).

**Correct check**: compare `existing_refs == desired_refs` inside each `*_TopFlow` entry.
- If they match → execution order is ✅ correct regardless of `definition_order` position.
- Only flag `definition_order` mismatches if there is **no corresponding TopFlow** that overrides the sequence.

Do **not** flag LTTC, SPEED, BEGIN, END, HVBI, FACT, or START subflow ordering based on `definition_order` alone.

### Rule 2 — `extra_unmanaged` entries in `IP*_FLOWS.py` must be verified, not assumed

The blueprint topology tracks **PRL wrapper subflows** (e.g., `STARTPRL0GCD_SubFlow`, `BEGINPRL0GCD_SubFlow`). Subflows inside those wrappers (the test content) are not blueprint-managed and will appear as `extra_unmanaged`. However, not every `extra_unmanaged` entry is automatically a PRL inner subflow — each one must be verified.

**Verification**: for each `extra_unmanaged` entry, check whether it appears as the inner payload of a PRL wrapper using the `r40f40` port pattern:

```
STARTPRL0GCD_SubFlow      STARTGCDNOM_SubFlow        rm2fm2 rm1fm1 r0f40 r40f40
```

- If confirmed as a PRL inner subflow → ✅ expected, do not flag
- If it is **not** called by any PRL wrapper → ⚠️ confirm with user whether it is intentional

This applies to all dielet IP flow files (`IPH_FLOWS.py`, `IPC_FLOWS.py`, `IPG_FLOWS.py`, `IPP_FLOWS.py`).

### Rule 3 — `extra_unmanaged` in `ProgramFlowsGCD.py` (or other dielet-pkg files) requires user confirmation

Unmanaged entries in `ProgramFlowsGCD.py` do not have a predictable PRL-inner-subflow pattern. Always confirm with the user whether the entry is intentional before dismissing it.

### Summary decision table

| File | `extra_unmanaged` | Action |
|------|-------------------|---------|
| Any `IP*_FLOWS.py` | Confirmed as inner payload of a PRL wrapper (`r40f40`) | ✅ Expected — do not flag |
| Any `IP*_FLOWS.py` | Not called by any PRL wrapper | ⚠️ Confirm with user |
| `ProgramFlowsGCD.py` / `ProgramFlowsSharedPKG.py` | Any unrecognized entry | ⚠️ Confirm with user |
| Any file | `missing_managed` entries | ❌ Real gap — must be fixed |
| Any file | `TopFlow.existing_refs != desired_refs` | ❌ Real ordering mismatch — must be fixed |
| Any file | `definition_order` mismatch only, TopFlow matches | ✅ Non-issue — do not flag |
