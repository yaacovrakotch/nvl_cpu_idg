---
name: add-new-bom
description: >
  Add a new BOM (Bill of Materials / bomgroup) to the NVL test program repository.
  Use when the user says "add a new BOM", "enable a new BOM", "create a new bomgroup",
  "bring up a new BOM", or "new BOM enablement". Works in BOTH nvl.common AND dielet repos
  (nvl.cpu, nvl.gcd, nvl.hub, nvl.pcd). Auto-detects the repo type and presents a
  scoped plan for approval before making any changes.
user-invokable: true
argument-hint: "NewBOMFullName SourceBOMToCopyFrom"
---

# Add New BOM — Common and Dielet Repos

This skill guides the TPI Agent through all steps required to register a new BOM in either
the **nvl.common** shared repository or a **dielet repository** (`nvl.cpu`, `nvl.gcd`,
`nvl.hub`, `nvl.pcd`). The skill auto-detects which repo type is active, asks for all
required inputs, presents a complete plan, **waits for explicit user approval**, and only
then executes.

> ⛔ **CRITICAL**: The agent MUST NOT modify any file until the user approves the plan.
> Every session follows: **Detect → Gather Inputs → Present Plan → Await Approval → Execute**.

---

## When to Use This Skill

- User says "add a new BOM", "enable BOM", "new BOM bring-up", "new bomgroup", etc.
- A new silicon product variant needs to be registered in the test program
- Running in either `nvl.common` or a dielet repo (`nvl.cpu`, `nvl.gcd`, `nvl.hub`, `nvl.pcd`)

---

## Phase 0 — Detect Repo Type

Before asking any questions, examine the workspace to determine which repo is active.

### Auto-Detection Rules

Use `file_search` or `grep_search` to check for these markers:

| Marker to check | If found → Repo Type |
|----------------|---------------------|
| `NVL_Common.sln` exists at workspace root | **nvl.common** |
| `BaseInputs/Common/Common_Files/SCVars.usrv` exists at workspace root | **nvl.common** |
| `Shared/` directory exists at workspace root (submodule) | **dielet repo** |
| `.sln` filename matches `nvl_cpu.sln`, `nvl_gcd.sln`, `nvl_hub.sln`, `nvl_pcd.sln` | **dielet repo** (and which dielet) |

### If auto-detection is ambiguous

If the markers above do not give a clear answer, ask using `vscode_askQuestions`:

```json
[
  {
    "header": "RepoType",
    "question": "Which repository are you working in?",
    "options": [
      { "label": "nvl.common", "description": "Shared common repo — updates SCVars, TOSRules, DFF_Screen, shared BaseInputs", "recommended": true },
      { "label": "nvl.cpu", "description": "CPU dielet repo" },
      { "label": "nvl.gcd", "description": "GCD dielet repo" },
      { "label": "nvl.hub", "description": "HUB dielet repo" },
      { "label": "nvl.pcd", "description": "PCD dielet repo" }
    ],
    "allowFreeformInput": false
  }
]
```

Store the result as `REPO_TYPE` (values: `nvl.common`, `nvl.cpu`, `nvl.gcd`, `nvl.hub`, `nvl.pcd`).

---

## Phase 1 — Gather Required Inputs

Call `vscode_askQuestions` to collect all inputs **before touching any file**.
Ask in **two rounds** to avoid overwhelming the user. Some Round 2 questions are only
relevant for specific repo types — skip questions that do not apply.

### Round 1 — Identity (always ask, both repo types)

```json
[
  {
    "header": "NewBOMFullName",
    "question": "What is the full bomgroup name for the new BOM? (e.g. CLASS_NVL_X28C or CLASS_DNL_Y28C)",
    "allowFreeformInput": true
  },
  {
    "header": "SourceBOM",
    "question": "Which existing BOM should be used as the copy source?",
    "options": [
      { "label": "CLASS_NVL_S28C", "recommended": true },
      { "label": "CLASS_NVL_S52C" },
      { "label": "CLASS_NVL_HX28C" },
      { "label": "CLASS_NVL_P16C" },
      { "label": "CLASS_NVL_S16C" },
      { "label": "CLASS_NVL_H16C" },
      { "label": "CLASS_NVL_U8C" },
      { "label": "CLASS_DNL_S28C" }
    ],
    "allowFreeformInput": true
  },
  {
    "header": "GCDConfig",
    "question": "What is the GCD EU configuration for this BOM? (used to update TOS rules — nvl.common only, but helps plan validation)",
    "options": [
      { "label": "32EU", "description": "S28C, S52C, HX28C, S16C, DNL_S28C", "recommended": true },
      { "label": "64EU", "description": "H16C, U8C" },
      { "label": "192EU", "description": "P16C" }
    ],
    "allowFreeformInput": false
  }
]
```

### Round 2 — Details

**For nvl.common** — ask all five questions below:

```json
[
  {
    "header": "PackageCode",
    "question": "What is the SC_PACKAGE code for this BOM in DFF_Screen.txt? (e.g. 63, 56, 59, 69, 67, 66, 68)",
    "allowFreeformInput": true
  },
  {
    "header": "DeviceCode",
    "question": "What is the SC_DEVICE suffix code for this BOM in DFF_Screen.txt? (e.g. AAA, AAB, AAC)",
    "options": [
      { "label": "AAA", "recommended": true },
      { "label": "AAB" },
      { "label": "AAC" }
    ],
    "allowFreeformInput": true
  },
  {
    "header": "LocationCodes",
    "question": "What location codes (SC_LOCN) apply to this BOM for DFF_Screen.txt? (comma-separated, e.g. 6163,5163,6167,5167)",
    "allowFreeformInput": true
  },
  {
    "header": "BOMString",
    "question": "What is the BOM string for Bomgroup.usrv? (e.g. 634AAA2VC — the 'bom' field)",
    "allowFreeformInput": true
  },
  {
    "header": "PerBomTPName1",
    "question": "What is the PerBomTPName1 (ituff name) for this BOM? (e.g. NVLS763C0H03A0ZS619)",
    "allowFreeformInput": true
  }
]
```

**For dielet repos** — ask only these two questions:

```json
[
  {
    "header": "BOMString",
    "question": "What is the BOM string for Bomgroup.usrv? (e.g. 634AAA2VC — the 'bom' field)",
    "allowFreeformInput": true
  },
  {
    "header": "PerBomTPName1",
    "question": "What is the PerBomTPName1 (ituff name) for this BOM? (e.g. NVLS763C0H03A0ZS619)",
    "allowFreeformInput": true
  }
]
```

---

## Phase 2 — Derive Variables from Inputs

From `NewBOMFullName` (e.g., `CLASS_NVL_X28C`), derive these variables used throughout the steps:

| Variable | Example | How to derive |
|----------|---------|--------------|
| `SHORT_BOM` | `X28C` | Strip `CLASS_NVL_` or `CLASS_DNL_` prefix |
| `NEW_COMMON_FOLDER` | `Common_Class_NVL_X28C` | `Common_` + title-cased full name |
| `NEW_POR_TP_FOLDER` | `Class_NVL_X28C` | Title-case full name |
| `SOURCE_SHORT_BOM` | `S28C` | Strip prefix from `SourceBOM` |
| `SOURCE_COMMON_FOLDER` | `Common_Class_NVL_S28C` | Derived from `SourceBOM` |
| `SOURCE_POR_TP_FOLDER` | `Class_NVL_S28C` | Derived from `SourceBOM` |
| `DFF_SHORT` | `NVL_X28C` | `NVL_` + `SHORT_BOM`; for DNL BOMs: `NVL_DNL<SHORT_BOM>` |

Folder name rules:
- `CLASS_NVL_X28C` → `Common_Class_NVL_X28C` and `Class_NVL_X28C`
- `CLASS_DNL_S28C` → `Common_Class_DNL_S28C` and `Class_DNL_S28C`

---

## Phase 3 — Present Plan and Await Approval

> ⛔ **DO NOT MODIFY ANY FILES BEFORE THIS STEP IS COMPLETE.**

After gathering all inputs, present the full plan using prose or a numbered list, then
call `vscode_askQuestions` with an approval prompt:

```json
[
  {
    "header": "Approval",
    "question": "Review the plan above. Proceed with all changes?",
    "options": [
      { "label": "Proceed — execute all changes", "recommended": true },
      { "label": "Cancel — do not make any changes" }
    ],
    "allowFreeformInput": true
  }
]
```

The plan must include:
- Detected repo type and which dielet (if applicable)
- The full list of files that will be created or modified
- The derived variable values (NewBOMFullName, SHORT_BOM, source BOM, etc.)
- Any known gaps (e.g., missing DFF XML files, manual GitHub steps)

Only proceed to Phase 4 if the user selects **Proceed**.

---

## Phase 4A — Execute: nvl.common Repo Steps

> Apply these steps only when `REPO_TYPE == nvl.common`.

### Step C1 — Copy and Update BaseInputs Folder

#### C1a. Copy folder
```powershell
Copy-Item -Path "BaseInputs\Common\<SOURCE_COMMON_FOLDER>" `
          -Destination "BaseInputs\Common\<NEW_COMMON_FOLDER>" -Recurse
```

#### C1b. Update `Bomgroup.usrv` in the new folder
File: `BaseInputs/Common/<NEW_COMMON_FOLDER>/Bomgroup.usrv`

- Set `locationCode` = first location code from user input (or derive from similar BOM in [bom-inputs-reference.md](references/bom-inputs-reference.md))
- Set `bom` = `<BOMString>` (user input)
- Set `ActiveBomGroup` = `<NewBOMFullName>` (all caps)
- Set `PerBomTPName1` = `<PerBomTPName1>` (user input)

#### C1c. Update `EnvironmentFile_Common.env`
In the copied file, search-and-replace:
- All occurrences of `<SOURCE_SHORT_BOM>` → `<SHORT_BOM>` (case-insensitive)
- All occurrences of `<SOURCE_COMMON_FOLDER>` → `<NEW_COMMON_FOLDER>`

> Note: Most path values (FUSE root, pattern paths) will still reference the source BOM —
> this is expected and intentional. Flag these lines in a note to the user for manual update.

#### C1d. Rename `.ctproj` file inside the new folder
```powershell
Rename-Item "BaseInputs\Common\<NEW_COMMON_FOLDER>\<SOURCE_COMMON_FOLDER>.ctproj" `
            "<NEW_COMMON_FOLDER>.ctproj"
```

#### C1e. Update `Common_BOM.imp`
In `BaseInputs/Common/<NEW_COMMON_FOLDER>/Common_BOM.imp`, replace any reference to
`<SOURCE_COMMON_FOLDER>` with `<NEW_COMMON_FOLDER>`.

---

### Step C2 — Update `SCVars.usrv`

File: `BaseInputs/Common/Common_Files/SCVars.usrv`

#### C2a. Count existing Outcomes first
Before editing, use `grep_search` to count the current number of named Outcomes in
`TpRuleSC.If_BOMname`. The new BOM gets Outcome number = (current count).
The old catch-all (bare `OutcomeN;` with no condition) shifts up by one.

#### C2b. Add new Outcome to `If_BOMname` rule
Insert the new BOM as the second-to-last Outcome (before the catch-all). Example:

```
# Before (8 named + 1 catch-all = 9 total):
SelectorRule If_BOMname(Outcome1, ..., Outcome8, Outcome9)
{
    ...
    Outcome8 => GetEnvironmentVariable("BOMGROUP") == "CLASS_NVL_U8C";
    Outcome9;
}

# After (9 named + 1 catch-all = 10 total):
SelectorRule If_BOMname(Outcome1, ..., Outcome8, Outcome9, Outcome10)
{
    ...
    Outcome8 => GetEnvironmentVariable("BOMGROUP") == "CLASS_NVL_U8C";
    Outcome9 => GetEnvironmentVariable("BOMGROUP") == "<NewBOMFullName>";
    Outcome10;
}
```

#### C2c. Update `SC_PUP_FILE_PATH` UserVar
Add the new path at the Outcome position matching the new number (before the catch-all):
```
"~HDMT_TPL_DIR\\Shared\\BaseInputs\\Common\\<NEW_COMMON_FOLDER>",  ← insert here
"~HDMT_TPL_DIR\\Shared\\BaseInputs\\Common\\Common_Class_NVL_S28C"   ← catch-all stays last
```

#### C2d. Update ALL other `If_BOMname`-consuming UserVars
Search `SCVars.usrv` for all UserVars that call `TpRuleSC.If_BOMname(...)`. Each one must
receive the new argument at the matching position. The catch-all (last argument) stays last.
Also check `common.usrv` in `Common_Files/` for any additional UserVars using this rule.

---

### Step C3 — Update `TOSRules.usrv`

File: `BaseInputs/Common/Common_Files/TOSRules.usrv`

Based on user's GCD EU selection, add `|| GetEnvironmentVariable("BOMGROUP") == "<NewBOMFullName>"`
to the appropriate rule's `yes` condition:

| User selected | Rule to edit |
|--------------|-------------|
| 32EU | `If_32EU` |
| 64EU | `If_64EU` |
| 192EU | `If_192EU` |

Also check:
- **`If_NoGTRecovery`** — If the new BOM is a standard CLASS product (not PHM/CS), add it to the `CLASS` outcome.
- **`Check_BOM`** — Read the existing logic before deciding. Only update if the new BOM warrants it.

---

### Step C4 — Update `DFF_Screen.txt`

File: `Modules/TPI/TPI_BASE_XXX/InputFiles/DFF_Screen.txt`

#### C4a. Find the last TEST label number
Read the existing file. Count the highest `TESTn` label (e.g., `TEST10`). The new entries will use `TEST<n+1>` (e.g., `TEST11`).

#### C4b. Update the last test's terminal branch
The current last test in the chain has `;  2` as its false branch (falls to end-of-screen).
Change that `2` to `TEST<n+1>` so the chain continues to the new BOM.

#### C4c. Find the next available TESTRC pair
Count the highest `TESTRCm` label. New entries use `TESTRC<m+1>` and `TESTRC<m+2>`.

#### C4d. Append new EXEC entries
```
EXEC   ; TEST<n+1> ; STRING ; LITERAL ; True ; == ; EXPRESSION ; Contains([__shared__::SCVars.SC_PACKAGE], '<PackageCode>') && Contains([__shared__::SCVars.SC_DEVICE], '<DeviceCode>') ; - ; TESTRC<m+1>  ;  2
EXEC   ; TESTRC<m+1> ; STRING ; LITERAL ; True ; == ; EXPRESSION ; in([__shared__::SCVars.SC_LOCN], <'LOCN1', 'LOCN2', ...>) ; - ; TESTRC<m+2> ; TEST<n+1>A
EXEC   ; TESTRC<m+2> ; STRING ; GLOBAL     ; __shared__::DFFVars.MTL_FILE_PATH                    ; SET ; LITERAL ; ./Shared/Modules/TPI/TPI_DFF_XXX/InputFiles/<DFF_SHORT>_RAWCLASS.xml ; - ; 1  ; 2
EXEC   ; TEST<n+1>A  ; STRING ; GLOBAL     ; __shared__::DFFVars.MTL_FILE_PATH                    ; SET ; LITERAL ; ./Shared/Modules/TPI/TPI_DFF_XXX/InputFiles/<DFF_SHORT>_CLASS.xml ; - ; 1  ; 2
```

Location codes must be single-quoted and comma-separated: `'6163', '5163', '6167', '5167'`

> ⚠️ If `<DFF_SHORT>_CLASS.xml` and `<DFF_SHORT>_RAWCLASS.xml` do not yet exist in
> `Modules/TPI/TPI_DFF_XXX/InputFiles/`, note this to the user as a manual follow-up.

---

### Step C5 — Copy and Update POR_TP Folder

#### C5a. Copy folder
```powershell
Copy-Item -Path "POR_TP\<SOURCE_POR_TP_FOLDER>" `
          -Destination "POR_TP\<NEW_POR_TP_FOLDER>" -Recurse
```

#### C5b. Rename files in the new folder
```powershell
Rename-Item "POR_TP\<NEW_POR_TP_FOLDER>\PLIST_ALL_<SourceBOM>.plist.xml" "PLIST_ALL_<NewBOMFullName>.plist.xml"
Rename-Item "POR_TP\<NEW_POR_TP_FOLDER>\<SOURCE_POR_TP_FOLDER>.tpconfig"  "<NEW_POR_TP_FOLDER>.tpconfig"
Rename-Item "POR_TP\<NEW_POR_TP_FOLDER>\<SOURCE_POR_TP_FOLDER>.tpproj"    "<NEW_POR_TP_FOLDER>.tpproj"
```

#### C5c. Update internal references in all files inside the new folder
For each file in the new `POR_TP/<NEW_POR_TP_FOLDER>/` folder, search-and-replace:
- `<SOURCE_SHORT_BOM>` (case-sensitive and upper-case variants) → `<SHORT_BOM>`
- `<SOURCE_POR_TP_FOLDER>` → `<NEW_POR_TP_FOLDER>`
- `<SourceBOM>` (full name) → `<NewBOMFullName>`

Key files to check:

| File | What to update |
|------|---------------|
| `<NEW_POR_TP_FOLDER>.tpconfig` | ProductCodeName, TestProgramDescriptiveName, SOCPath, BomGroup name, FlowMatrixPath, plist reference |
| `EnvironmentFile.env` | Any path referencing the source BOM short name |
| `SubTestPlan.stpl` | BOM name references |
| `PLIST_ALL_<NewBOMFullName>.plist.xml` | Internal BOM name references |

---

### Step C6 — Update Solution File

File: `NVL_Common.sln`

Add the new POR_TP `.tpproj` as a new project entry, following the exact same block format
used for the source BOM's entry. Generate a new unique GUID:
```powershell
[System.Guid]::NewGuid().ToString("B").ToUpper()
```

---

### Step C7 — Recompile Affected TPI Modules

After all file edits in nvl.common, use the [pymtpl-compiler skill](../pymtpl-compiler/SKILL.md)
to recompile any modules whose `.py` or InputFiles were changed:

| Module | Recompile if... |
|--------|----------------|
| `TPI_BASE_XXX` | `DFF_Screen.txt` or `TPI_BASE_XXX_ScreenTest.txt` was changed |
| `TPI_DFF_XXX` | New DFF XML files were added, or `.py` was edited |
| `TPI_FLWFLGS_XXX` | New BOM-specific flow flags are needed |

---

### Validation Checklist — nvl.common

- [ ] `BaseInputs/Common/<NEW_COMMON_FOLDER>/` exists with updated `Bomgroup.usrv`
- [ ] `SCVars.usrv` `If_BOMname` Outcome count matches argument list count
- [ ] All `If_BOMname`-consuming UserVars in `SCVars.usrv` and `common.usrv` have the new argument
- [ ] `TOSRules.usrv` EU rule includes the new BOM
- [ ] `DFF_Screen.txt` — new EXEC entries present; previous last test chains to new test
- [ ] `POR_TP/<NEW_POR_TP_FOLDER>/` exists with all internal references updated
- [ ] No leftover `<SOURCE_SHORT_BOM>` references in the new folder
- [ ] `NVL_Common.sln` includes the new project
- [ ] DFF XML files exist or are flagged as pending manual addition

---

## Phase 4B — Execute: Dielet Repo Steps

> Apply these steps only when `REPO_TYPE` is `nvl.cpu`, `nvl.gcd`, `nvl.hub`, or `nvl.pcd`.
> In dielet repos, nvl.common is mounted as the `Shared/` submodule. Do NOT modify files
> inside `Shared/` — those must be changed in nvl.common separately.

---

### Step D1 — Copy and Update POR_TP Folder

#### D1a. Copy folder
```powershell
Copy-Item -Path "POR_TP\<SOURCE_POR_TP_FOLDER>" `
          -Destination "POR_TP\<NEW_POR_TP_FOLDER>" -Recurse
```

#### D1b. Rename files in the new folder
```powershell
Rename-Item "POR_TP\<NEW_POR_TP_FOLDER>\PLIST_ALL_<SourceBOM>.plist.xml" "PLIST_ALL_<NewBOMFullName>.plist.xml"
Rename-Item "POR_TP\<NEW_POR_TP_FOLDER>\<SOURCE_POR_TP_FOLDER>.tpconfig"  "<NEW_POR_TP_FOLDER>.tpconfig"
Rename-Item "POR_TP\<NEW_POR_TP_FOLDER>\<SOURCE_POR_TP_FOLDER>.tpproj"    "<NEW_POR_TP_FOLDER>.tpproj"
```

#### D1c. Update internal references
For each file in `POR_TP/<NEW_POR_TP_FOLDER>/`, search-and-replace:
- `<SOURCE_SHORT_BOM>` / `<SOURCE_POR_TP_FOLDER>` / `<SourceBOM>` → new BOM equivalents

Key files:

| File | What to update |
|------|---------------|
| `<NEW_POR_TP_FOLDER>.tpconfig` | ProductCodeName, TestProgramDescriptiveName, SOCPath, BomGroup name, plist reference |
| `EnvironmentFile.env` | Any path referencing source BOM short name |
| `SubTestPlan.stpl` | BOM name references |
| `PLIST_ALL_<NewBOMFullName>.plist.xml` | Internal BOM name references |

> **Dynamic BOM note:** For Dynamic BOM repos, the tpconfig `<SupportedBomGroups>` section may
> reference a shared flow matrix. Update only the `name=` and `plist=` attributes for the new BOM.

---

### Step D2 — Copy and Update BaseInputs Folder

Some dielet repos maintain their own `BaseInputs/Common/` BOM folders (mirroring common).
Check whether `BaseInputs/Common/<SOURCE_COMMON_FOLDER>` exists at the dielet repo root.

- **If it exists:** Copy and update the same way as Step C1 above (for the dielet root path).
- **If it does not exist:** Skip this step — the dielet relies entirely on the `Shared/` submodule for BaseInputs.

---

### Step D3 — Update `pf_pymtpl.bat`

File: `POR_TP/<NEW_POR_TP_FOLDER>/Scripts/pf_pymtpl.bat`

This script was copied from the source BOM folder. Update it so it references the new BOM:
- Replace `<SOURCE_SHORT_BOM>` / `<SOURCE_POR_TP_FOLDER>` → new BOM equivalents
- Verify the `--bomgroup` or equivalent argument points to `<NewBOMFullName>`

---

### Step D4 — Add Checker Workflow YAML

File: `.github/workflows/checker_<SHORT_BOM>.yml` (or equivalent naming used in the repo)

Copy an existing checker yml (e.g., for the source BOM) and update:
- Workflow `name:` → reference new BOM
- Any `BOMGROUP` environment variable → `<NewBOMFullName>`
- Job/step names that reference the source BOM name → new BOM name
- The `Run GenProgramFlows Pymtpl <bom>` command element → use `<NewBOMFullName>`

> Ask the user to confirm the exact yml naming convention used in this repo if uncertain.

---

### Step D5 — Update Solution File

File: `nvl_<dielet>.sln` (e.g., `nvl_cpu.sln`, `nvl_gcd.sln`, etc.)

Add the new POR_TP `.tpproj` as a new project entry, following the same block format used
for the source BOM. Generate a new GUID:
```powershell
[System.Guid]::NewGuid().ToString("B").ToUpper()
```

---

### Step D6 — SkipModules Setup

Directory: `POR_TP/<NEW_POR_TP_FOLDER>/SkipModules/`

This directory was copied from the source BOM. Review its contents:
- Keep skip entries for modules that are genuinely not yet validated for the new BOM
- Remove skip entries for modules that should run
- As a starting point, begin with the same skip list as the source BOM and reduce over time

---

### Step D7 — Note Manual GitHub Steps

These steps **cannot be automated** and must be done manually in the GitHub UI:

| Task | Notes |
|------|-------|
| Add label `tprobot_<NewBOMFullName>` | GitHub repo Labels settings |
| Add label `PASSED_<NewBOMFullName>` | GitHub repo Labels settings |
| Add label `FAILED_<NewBOMFullName>` | GitHub repo Labels settings |
| Enable branch protection for new checker | Repo Settings → Branches → Edit rule → add new checker to required status checks |
| Enable TPbot load/init for new BOM | After load and init pass |
| Enable TPbot B1 (after PO) | After standing silicon available |

Present these to the user as a checklist after completing the automated steps.

---

### Validation Checklist — Dielet Repo

- [ ] `POR_TP/<NEW_POR_TP_FOLDER>/` exists with all internal references updated
- [ ] `pf_pymtpl.bat` references the new BOM
- [ ] Checker workflow yml exists and references the new BOM name correctly
- [ ] Solution file includes the new tpproj
- [ ] SkipModules reviewed and set appropriately
- [ ] No leftover `<SOURCE_SHORT_BOM>` references in the new POR_TP folder
- [ ] Manual GitHub steps listed to user (labels, branch protection, TPbot)

---

## Affected Files Summary

### nvl.common

| File | Change type |
|------|------------|
| `BaseInputs/Common/<NEW_COMMON_FOLDER>/Bomgroup.usrv` | Created (copy + edit) |
| `BaseInputs/Common/<NEW_COMMON_FOLDER>/EnvironmentFile_Common.env` | Created (copy + edit) |
| `BaseInputs/Common/<NEW_COMMON_FOLDER>/<NEW_COMMON_FOLDER>.ctproj` | Created (renamed copy) |
| `BaseInputs/Common/Common_Files/SCVars.usrv` | Edit — add Outcome + UserVar argument |
| `BaseInputs/Common/Common_Files/TOSRules.usrv` | Edit — add BOM to EU rule |
| `Modules/TPI/TPI_BASE_XXX/InputFiles/DFF_Screen.txt` | Edit — add EXEC entries |
| `Modules/TPI/TPI_DFF_XXX/InputFiles/<DFF_SHORT>_CLASS.xml` | Add (if available) |
| `Modules/TPI/TPI_DFF_XXX/InputFiles/<DFF_SHORT>_RAWCLASS.xml` | Add (if available) |
| `POR_TP/<NEW_POR_TP_FOLDER>/` | Created (copy + all files updated) |
| `NVL_Common.sln` | Edit — add new project entry |

### Dielet Repo

| File | Change type |
|------|------------|
| `POR_TP/<NEW_POR_TP_FOLDER>/` | Created (copy + all files updated) |
| `POR_TP/<NEW_POR_TP_FOLDER>/Scripts/pf_pymtpl.bat` | Edit — update BOM references |
| `BaseInputs/Common/<NEW_COMMON_FOLDER>/` | Created if dielet has its own BaseInputs copy |
| `.github/workflows/checker_<SHORT_BOM>.yml` | Created (copy + edit) |
| `nvl_<dielet>.sln` | Edit — add new project entry |

---

## References

- [NEW_BOM_Creation.txt](../../NEW_BOM_Creation.txt) — Full BOM bring-up wiki (used to build this skill)
- [references/bom-inputs-reference.md](references/bom-inputs-reference.md) — Known BOM parameters table
- [SCVars.usrv](../../BaseInputs/Common/Common_Files/SCVars.usrv) — `If_BOMname` rule (nvl.common)
- [TOSRules.usrv](../../BaseInputs/Common/Common_Files/TOSRules.usrv) — EU config rules (nvl.common)
- [DFF_Screen.txt](../../Modules/TPI/TPI_BASE_XXX/InputFiles/DFF_Screen.txt) — DFF screen test (nvl.common)
- [programflows-compiler skill](../programflows-compiler/SKILL.md) — ProgramFlows regeneration (dielet repo, after BOM changes)
