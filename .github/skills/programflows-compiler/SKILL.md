---
name: programflows-compiler
description: 'Full workflow for updating and compiling ProgramFlows in the NVL test program. Use when asked to update program flows, regenerate programflows mtpl, add a subflow to program flows, modify flow routing, update programflows for a BOM, or compile IPH_FLOWS/IPC_FLOWS/IPP_FLOWS/IPG_FLOWS/ProgramFlowsHUB/ProgramFlowsGCD/ProgramFlowsCPU/ProgramFlowsPCD. Handles dielet-level and package-level flows, Torch fixer execution, .stpl guard, and git commit scoping.'
user-invocable: true
---

# ProgramFlows Compiler

Full end-to-end workflow for editing and regenerating ProgramFlows `.mtpl` output files from their Pymtpl `.py` sources in the NVL test program repository.

## When to Use This Skill

- Adding a new subflow or module to a program flow
- Changing port routing between subflows
- Enabling or disabling a flow item
- Updating a flow for one or more BOMs (Class_NVL_S28C, Class_NVL_S52C, etc.)

## Session Start — Required Clarifications

At the very beginning of every ProgramFlows session, before reading any files or classifying the request, ask the user the following two questions:

**1. What type of update is this?**

| Option | Meaning |
|--------|---------|
| **Blueprint subflow update** | Only the blueprint Excel needs to change (new slot, reorder, delete) |
| **Module flow update** | Only the ProgramFlows `.py`/`.mtpl` files need to change (module-level edits inside an existing subflow) |
| **Both** | Blueprint topology change AND ProgramFlows source changes are required |

**2. Which BOM are you working with?** (e.g., `Class_NVL_S28C`, `Class_NVL_S52C`, `Class_NVL_H16C`, etc.)

If the user's request already contains explicit answers to both questions, confirm them back before proceeding rather than asking again.

### Execution order when Blueprint is involved

If the user selects **Blueprint subflow update** or **Both**:
1. **Execute the blueprint skill first** — follow `.github/skills/blueprint/SKILL.md` completely before touching any ProgramFlows `.py` file
2. Only after the blueprint update is confirmed (or the user elects to skip it) proceed with ProgramFlows edits

If the user selects **Module flow update** only, skip the blueprint skill entirely and proceed directly to the workflow steps below.

---

## Workflow Gate — Topology vs Module-Only

After the session-start clarification, classify the request more precisely:

Treat these as **subflow-topology changes** (Blueprint + ProgramFlows both affected):
- Adding a subflow
- Deleting a subflow
- Reordering subflows

Do **not** treat these as topology changes (ProgramFlows only):
- Adding, removing, or reordering modules within the subflow body
- Changing ports or `GoTo` routing on existing flow items
- Enabling or disabling an existing flow item without changing the surrounding subflow topology

If the session-start answer already resolved this classification, skip re-asking. If the classification contradicts the session-start choice, surface the conflict to the user before proceeding.

## Prerequisites

### Clone the common submodule (dielet repos only)

> ⚠️ **Only required when working in a dielet repo** (`nvl.hub`, `nvl.cpu`, `nvl.gcd`, `nvl.pcd`).  
> If you are working in `nvl.common` directly, skip this step — there is no submodule.

```powershell
git submodule update --init --recursive --force
```

This clones `nvl.common` into the `Shared/` folder. If `Shared/` is empty or missing files, this command was not run.

---

## Step 1 — Identify the Target .py File

The change scope determines which `.py` to edit. All source files are in:

```
POR_TP/<BOM>/ProgramFlowsTestPlan/
```

### Dielet-level flows (IP scope)

| Die | Source file |
|-----|------------|
| HUB | `IPH_FLOWS.py` |
| CPU | `IPC_FLOWS.py` |
| PCD | `IPP_FLOWS.py` |
| GCD | `IPG_FLOWS.py` |

Use these when the change is specific to one IP die's flow sequence within the package test.

### Package-level flows

| Die repo | Source file | Location |
|----------|------------|----------|
| HUB      | `ProgramFlowsHUB.py` | `POR_TP/<BOM>/ProgramFlowsTestPlan/` |
| GCD      | `ProgramFlowsGCD.py` | `POR_TP/<BOM>/ProgramFlowsTestPlan/` |
| CPU      | `ProgramFlowsCPU.py` | `POR_TP/<BOM>/ProgramFlowsTestPlan/` |
| PCD      | `ProgramFlowsPCD.py` | `POR_TP/<BOM>/ProgramFlowsTestPlan/` |

Use these when the change affects the top-level package program flow (PKG subflows such as `BEGINGCDPKG_SubFlow`, `ENDGCDPKG_SubFlow`, etc.).

> ⚠️ **`ProgramFlowsGCD.py` (and the other `ProgramFlows<Die>.py` files) are data files — they are NOT compiled directly.**  
> They are imported by `Shared/POR_TP/<BOM>/ProgramFlowsTestPlan/ProgramFlows.py`, which is the actual compilation entry point.  
> See Step 4 for the correct two-step compilation sequence.

> For syntax and rules on editing these `.py` files, consult  
> `.github/instructions/programflows.instructions.md`.

> ⚠️ **MANDATORY PRE-READ for PKG-scope subflows**: If the new subflow name contains `PKG`, or the user references a position by TopFlow name (e.g. "after the END subflow"), you MUST read `Shared/POR_TP/<BOM>/ProgramFlowsTestPlan/ProgramFlowsSharedPKG.py` **before** touching any source file or the blueprint:
> 1. Locate the relevant TopFlow (e.g. `END_TopFlow`) and read its **complete entry list in order** to identify the exact anchor row
> 2. **Disambiguate named subflows** — `END_SubFlow` (the neutral shared subflow at the tail of `END_TopFlow`) is a distinct entry from `END*PKG_SubFlow` (the dielet PKG subflows earlier in that same TopFlow); they are not the same anchor
> 3. Confirm whether the new subflow also requires wiring into the TopFlow in `ProgramFlowsSharedPKG.py` — required for all PKG-scope subflows; a dielet `IPG_FLOWS.py` entry alone is not sufficient
> 4. Only after completing this read proceed to blueprint planning and source editing

---

## Step 2 — Edit the .py File

Make the required changes to the target `.py` file identified in Step 1.

> ⚠️ **MANDATORY CHECK — before and after editing:**  
> Every non-MAIN subflow MUST have `TPI_FLWFLGS_<IP>XX` as its **first module**.  
> - New subflow? Add `TPI_FLWFLGS_<IP>XX` as line 1 of the subflow body.  
> - Editing existing subflow? Verify `TPI_FLWFLGS_<IP>XX` is still first.  
> - If missing, add it before any other module — do not proceed to compile without it.  
> Additional modules beyond `TPI_FLWFLGS_<IP>XX` are at the user's discretion.

Key syntax reminder:
```
<SubFlow_Name>    <MODULE_NAME>    <port_defs>
MAIN              <SubFlow_Name>   <port_defs>
```

See `.github/instructions/programflows.instructions.md` for full port syntax and examples.

#### Cross-Surface Pattern Check (required when a blueprint `--insert-slot` is also planned)

If a blueprint update is planned in the same session, **determine the slot pattern type from the `.py` source first**, before touching the blueprint. The two surfaces must match — if they would disagree, stop and ask the user before applying either change.

> ⚠️ **Anchor disambiguation — never infer position from name alone**: When the user says "add after X", the blueprint anchor must be confirmed from the actual TopFlow sequence read from `ProgramFlowsSharedPKG.py` (see mandatory pre-read above). A positional reference like "after the END subflow" is ambiguous — `END_SubFlow` (shared common) and `END*PKG_SubFlow` (dielet PKG) are separate entries in the same `END_TopFlow`. If the TopFlow has not been read yet, **STOP and read it before constructing any `--insert-slot` command**.

How to read the pattern from the `.py` source:

- Look at how the new subflow name appears in `Shared/POR_TP/<BOM>/ProgramFlowsTestPlan/ProgramFlowsSharedPKG.py` (for shared PKG wiring) and the dielet `ProgramFlows<Die>.py`:
  - `END_TopFlow` (or `MAIN`) uses the **full dielet-prefixed name** directly (e.g. `END_TopFlow ENDCPUVMAXPKG_SubFlow …`) → **Pattern B**: each dielet name is its own independent `FLOWDEF:ALL:Flow` slot in the blueprint; do **NOT** use `--dielet-flow`
  - `END_TopFlow` uses a **neutral alias** (e.g. `END_TopFlow ENDPKG_SubFlow …`) and only the dielet file carries per-dielet names → **Pattern A**: neutral alias at `FLOWDEF:ALL`, dielet names as children; use `--dielet-flow --explicit-dielet-subflows`

- Pass this determination explicitly when constructing the blueprint `--insert-slot` command so both surfaces are consistent
- If the `.py` evidence and the blueprint pattern implied by the user's request point to different structures, **STOP** and surface the conflict to the user before applying anything

---

## Step 3 — Run the Torch Fixer - MUST ALWAYS RUN BEFORE COMPILING PROGRAMFLOWS PYMTPL TO AVOID ERRORS

From the **repo root**, use the `run_torch_fixer.py` wrapper script. It runs the Torch fixer and **automatically discards all side-effect files** introduced by the fixer (`.env`, `.plist`, `.slimplist`, etc.), preserving only the files that were already dirty before the fixer ran. **`.stpl` files are intentionally kept** and not discarded.

```powershell
cd <repo_root>
python .github/skills/programflows-compiler/Scripts/run_torch_fixer.py <BOM>
```

**Example:**
```powershell
python .github/skills/programflows-compiler/Scripts/run_torch_fixer.py Class_NVL_S28C
```

The script will print a summary of which side-effect files were discarded and which files remain modified (your intended changes).

> **Legacy manual command** (for reference only — use the script above instead):
> ```powershell
> & "$env:TorchAPIExecPath\Torch.exe" fix-tp --sln-config Class_NVL_S28C -s NVL_GCD.sln -p POR_TP/Class_NVL_S28C/Class_NVL_S28C.tpproj
> ```

> ⚠️ **Steps 5 (Guard .stpl) is no longer needed** when using `run_torch_fixer.py` — the script handles all side-effect cleanup automatically. `.stpl` files are intentionally preserved.

The script is located at `.github/skills/programflows-compiler/Scripts/run_torch_fixer.py`.

---

## Step 4 — Compile with Pymtpl

Always run **two** pymtpl compilation commands, regardless of whether you edited `IPG_FLOWS.py` or `ProgramFlowsGCD.py`. This matches the `.runme` script used by the repo and ensures both output MTPLs are kept in sync.

> ⚠️ **You must `cd` into the dielet `ProgramFlowsTestPlan` folder first** — pymtpl resolves output paths relative to the working directory, and the `ProgramFlowsGCD.py` import is resolved from the current directory.

```powershell
# Navigate to the ProgramFlowsTestPlan folder for the target BOM
cd POR_TP\<BOM>\ProgramFlowsTestPlan

# Command 1: Compile the dielet IP flow (always required)
python ..\..\..\Shared\BaseInputs\pytpd\main\pymtpl.py IPG_FLOWS.py -env ..\EnvironmentFile.env

# Command 2: Compile the shared package flow (always required)
# ProgramFlowsGCD.py is imported from the current directory by ProgramFlows.py
$env:DIE_LIST = "GCD"
python ..\..\..\Shared\BaseInputs\pytpd\main\pymtpl.py ..\..\..\Shared\POR_TP\<BOM>\ProgramFlowsTestPlan\ProgramFlows.py -env ..\EnvironmentFile.env
```

**Example** for `Class_NVL_S28C`:
```powershell
cd POR_TP\Class_NVL_S28C\ProgramFlowsTestPlan

# Command 1
python ..\..\..\Shared\BaseInputs\pytpd\main\pymtpl.py IPG_FLOWS.py -env ..\EnvironmentFile.env

# Command 2
$env:DIE_LIST = "GCD"
python ..\..\..\Shared\BaseInputs\pytpd\main\pymtpl.py ..\..\..\Shared\POR_TP\Class_NVL_S28C\ProgramFlowsTestPlan\ProgramFlows.py -env ..\EnvironmentFile.env
```

> For locating `pymtpl.py` and the environment file if these paths differ, see the  
> `pymtpl-compiler` skill.

**Expected outputs** — two regenerated `.mtpl` files in the same folder:
```
POR_TP/<BOM>/ProgramFlowsTestPlan/IPG_FLOWS.mtpl
POR_TP/<BOM>/ProgramFlowsTestPlan/ProgramFlows.mtpl
```

---

## Step 5 — Guard the .stpl File

> ✅ **Handled automatically** if you used `.github/skills/programflows-compiler/Scripts/run_torch_fixer.py` in Step 3. Skip this step.

If you ran the Torch fixer manually (without the script), check for other fixer side effects and discard them — **but do NOT discard `.stpl`**:

```powershell
# Discard side-effect files (env, plists) — but NOT .stpl
git checkout -- POR_TP/<BOM>/EnvironmentFile.env
git checkout -- POR_TP/<BOM>/PLIST_ALL_CLASS_NVL_S28C.plist.xml
# ... etc for other side-effect files
```

> ⚠️ Also check for `.slimplist.*` and `.ipxml` files under `POR_TP/<BOM>/` — discard those too. Only stage the `.py` and `.mtpl` files.

---

## Step 6 — Validate the .mtpl Output

After compilation, diff **both** generated `.mtpl` files to confirm only the expected changes are present.

```powershell
git diff POR_TP/<BOM>/ProgramFlowsTestPlan/IPG_FLOWS.mtpl
git diff POR_TP/<BOM>/ProgramFlowsTestPlan/ProgramFlows.mtpl
```

**Example:**
```powershell
git diff POR_TP/Class_NVL_S28C/ProgramFlowsTestPlan/IPG_FLOWS.mtpl
git diff POR_TP/Class_NVL_S28C/ProgramFlowsTestPlan/ProgramFlows.mtpl
```

> If you only edited `IPG_FLOWS.py`, `ProgramFlows.mtpl` should be clean (no diff).  
> If you only edited `ProgramFlowsGCD.py`, `IPG_FLOWS.mtpl` should be clean (no diff).  
> Always check both regardless.

**What to check in the changed MTPL:**
- Only `FlowItem` blocks and `GoTo` references corresponding to your change are modified
- The `GoTo` chain is consistent — each `FlowItem`'s pass `GoTo` points to the correct next item
- No other subflows or unrelated sections changed
- The total number of `FlowItem` blocks in the affected subflow is unchanged (reorder only, no additions/deletions)

If the diff contains unexpected changes (wrong subflow, extra sections modified, broken `GoTo` chain), stop and let the user know that the mtpl changes are not as expected and that manual intervention is needed.

#### Blueprint Consistency Check (required when a blueprint `--insert-slot` was also applied in this session)

If a blueprint slot insert was applied in the same session, verify that the `FLOWDEF:ALL:Flow` slot structure written to the blueprint matches what appears in the compiled `.mtpl`.

How to read the pattern from the `.mtpl`:
- Each subflow appears as a top-level `Flow <SUBFLOW_NAME>_SubFlow { … }` block
- Individual dielet-prefixed flows (`Flow ENDCPUVMAXPKG_SubFlow`) confirm Pattern B
- A single neutral-named flow (`Flow ENDPKG_SubFlow`) containing per-dielet routing confirms Pattern A

Consistency rules:

| `.mtpl` evidence | Blueprint state | Verdict |
|---|---|---|
| `Flow ENDCPUVMAXPKG_SubFlow` (individual) | `FLOWDEF:ALL:Flow = ENDCPUVMAXPKG`, `cpu_flow: null` | ✅ Consistent — Pattern B |
| `Flow ENDPKG_SubFlow` (neutral) | `FLOWDEF:ALL:Flow = ENDPKG`, `cpu_flow: "ENDCPUPKG"` | ✅ Consistent — Pattern A |
| `Flow ENDCPUVMAXPKG_SubFlow` (individual) | `FLOWDEF:ALL:Flow = ENDVMAXPKG`, `cpu_flow: "ENDCPUVMAXPKG"` | ❌ **Mismatch** — STOP |
| `Flow ENDPKG_SubFlow` (neutral) | `FLOWDEF:ALL:Flow = ENDCPUPKG` (solo, no neutral parent) | ❌ **Mismatch** — STOP |

On a mismatch: report the inconsistency to the user, identify which surface is wrong, and do not commit until the blueprint is corrected to match the `.mtpl`.

---

## Step 7 — Revert the .stpl File to POR State

Once the `.mtpl` diff is validated, revert the `.stpl` file back to its pre-fixer state:

```powershell
git checkout -- POR_TP/<BOM>/SubTestPlan.stpl
```

**Example:**
```powershell
git checkout -- POR_TP/Class_NVL_S28C/SubTestPlan.stpl
```

> The Torch fixer modifies `SubTestPlan.stpl` as a side effect. It must be reverted to the committed (POR) state before committing your changes — it should never be committed.

---

## Step 8 — Commit Only the Correct Files

The files to stage depend on which source `.py` was edited:

| Scenario | Files to commit |
|----------|-----------------|
| Edited `IPG_FLOWS.py` only | `IPG_FLOWS.py` + `IPG_FLOWS.mtpl` |
| Edited `ProgramFlowsGCD.py` only | `ProgramFlowsGCD.py` + `ProgramFlows.mtpl` |
| Edited both | All four files above |

In all cases, **`ProgramFlows.mtpl` only changes when `ProgramFlowsGCD.py` is edited**, and **`IPG_FLOWS.mtpl` only changes when `IPG_FLOWS.py` is edited**. Stage only the files that actually have a diff.

**Do not commit:**
- `SubTestPlan.stpl` (already reverted in Step 7)
- Any unrelated `.mtpl` or generated files
- `.tpproj`, `.sln`, or other project files touched by the Torch fixer

```powershell
# Example: edited ProgramFlowsGCD.py
git add POR_TP/<BOM>/ProgramFlowsTestPlan/ProgramFlowsGCD.py
git add POR_TP/<BOM>/ProgramFlowsTestPlan/ProgramFlows.mtpl
git commit -m "<your commit message>"

# Example: edited IPG_FLOWS.py
git add POR_TP/<BOM>/ProgramFlowsTestPlan/IPG_FLOWS.py
git add POR_TP/<BOM>/ProgramFlowsTestPlan/IPG_FLOWS.mtpl
git commit -m "<your commit message>"
```

---

## Multi-BOM Workflow

If the user requests the same change across multiple BOMs (e.g., `Class_NVL_S28C` and `Class_NVL_S52C`), execute **Steps 1–8 sequentially for each BOM**, one at a time. Do not interleave steps across BOMs.

```
For each BOM in [Class_NVL_S28C, Class_NVL_S52C, ...]:
    Step 1 — Identify target .py for this BOM
    Step 2 — Edit .py
    Step 3 — Run Torch fixer (run_torch_fixer.py)
    Step 4 — Compile
    Step 5 — (manual fixer only) Guard side effects
    Step 6 — Validate .mtpl diff
    Step 7 — Revert .stpl to POR state
    Step 8 — Stage and commit
```

---

## Quick Reference — File Locations

```
<repo_root>/
├── NVL_GCD.sln                                       ← slnfile
├── POR_TP/
│   └── <BOM>/
│       ├── <BOM>.tpproj                              ← tpproj
│       ├── SubTestPlan.stpl                          ← DO NOT COMMIT
│       ├── EnvironmentFile.env
│       └── ProgramFlowsTestPlan/
│           ├── IPG_FLOWS.py                          ← dielet IP flow source → IPG_FLOWS.mtpl
│           ├── ProgramFlowsGCD.py                   ← PKG flow data (imported by Shared ProgramFlows.py)
│           ├── IPG_FLOWS.mtpl                        ← generated from IPG_FLOWS.py
│           └── ProgramFlows.mtpl                    ← generated from Shared ProgramFlows.py
└── Shared/                                           ← nvl.common submodule
    ├── BaseInputs/pytpd/main/pymtpl.py              ← compiler
    └── POR_TP/<BOM>/ProgramFlowsTestPlan/
        └── ProgramFlows.py                          ← compilation entry point for ProgramFlows.mtpl
                                                       (imports ProgramFlowsGCD.py from dielet folder)
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `Shared/` folder is empty | Run `git submodule update --init --recursive --force` |
| pymtpl output goes to wrong folder | Ensure you `cd` into `ProgramFlowsTestPlan/` before running pymtpl |
| `.stpl` shows as modified after Torch fixer | Expected — discard with `git checkout -- <path>` |
| Torch fixer cannot find `.sln` | Run the command from the repo root directory |
| Multiple `.mtpl` files changed | Only stage the one corresponding to the edited `.py` |

> For guidance on interpreting `--plan-programflows-sync` output (non-issues, TopFlow ordering rules, unmanaged subflow checks), see the **blueprint skill**: `.github/skills/blueprint/SKILL.md` — section "Interpreting `--plan-programflows-sync` Output — Known Non-Issues".
