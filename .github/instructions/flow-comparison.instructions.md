---
applyTo: "**/*.mtpl,**/*_bp.mtpl,**/*_bp.flows_compare.csv,**/.tmp_arr_core_compare/**,**/symbolize_*.py,**/compare_flows*.py"
---

# Flow Comparison & Symbolization — Mandatory Rules

When the user asks to **compare flows within a module**, **collapse/symbolize a
module's `.mtpl`**, **diff `F1XAT/F2XAT/F3XAT` (or similar) flows**, or
**generate a `_bp.mtpl`**, the rules below are MANDATORY. Do not write
ad-hoc comparison scripts; do not invent alternative output schemas.

## 1. Required tooling (no substitutes)

1. **Test-instance data source** — use the
   [`test-instance-comparison`](../skills/test-instance-comparison/SKILL.md)
   skill (wraps `ApiSamples.TestInstanceComparison`, built on the Trace API).
   Skill location: `.github/skills/test-instance-comparison/`.
   This is the only sanctioned way to obtain instance/parameter/connectivity
   data. STPL listing / FlowItem order is not acceptable as a substitute (see
   the main `copilot-instructions.md` execution-order section).

2. **Comparison + symbolization pipeline** — use these scripts only:
   - `.tmp_arr_core_compare/symbolize_mtpl.py` — orchestrator (3 phases:
     `compare`, `generate`, `validate`; CLI: `[compare|generate|validate|all]`).
   - `.tmp_arr_core_compare/compare_flows_v3.py` — comparison engine, called by
     the orchestrator.

   Do NOT create new comparison scripts (e.g. `compare_matrix.py`,
   `flow_diff.py`, etc.) with custom schemas. If a different view is needed,
   derive it FROM `*_bp.flows_compare.csv` — never replace it.

## 2. Canonical output — `<MODULE>_bp.flows_compare.csv`

Filename: `Modules/<...>/<MODULE>/<MODULE>_bp.flows_compare.csv`

Exact column order (no additions, no renames, no reordering):

| # | Column                        | Meaning                                                                 |
|---|-------------------------------|-------------------------------------------------------------------------|
| 1 | `Entity`                      | Collapsed entity key — see row-types below                              |
| 2 | `<flowN>` (one per flow)      | The value of the entity in flow N (instance name or param/conn value)   |
| 3 | `DIFF`                        | `OK` if all flow values equal, else describes the diff                  |
| 4 | `<flowN>_line` (one per flow) | Source line number in the originating `.mtpl`                           |
| 5 | `Symbolized`                  | The entity row's value with `<sN>` placeholders where flows differ      |
| 6 | `<flowN>_symbols`             | `s0=value; s1=value; …` mapping per flow                                |

Example flow-column names: `ARR_ATOM_CXX_F1XAT`, `ARR_ATOM_CXX_F2XAT`,
`ARR_ATOM_CXX_F3XAT`.

### Row-types under each `Entity`
- `<entity>` — bare row for the instance name (top-level merged identity)
- `<entity>.param.<ParamName>` — one row per parameter
- `<entity>.connectivity.R<port>` — one row per output port (Return/GoTo/etc.)
- `<entity>.edc` — entity-data-class marker

### Symbol cell encoding
- Compare-CSV cells: `<sN>` (angle brackets)
- `_bp.mtpl` body:    `\sN\` (backslash-bounded)
- `<flow>_symbols`:   `s0=…; s1=…` (semicolon-separated key=value)

## 3. Source coverage rule

`compare_flows_v3.py` indexes definitions from its `MTPL_TEST_SOURCES` list.
**Every `.mtpl` containing CSharpTest / MultiTrialTest definitions referenced
by the flows under comparison must be in `MTPL_TEST_SOURCES`** — otherwise the
entity will be missing from the compare CSV and won't be symbolized in
`_bp.mtpl`.

## 4. Sibling artifacts (also produced by `symbolize_mtpl.py`)

- `<MODULE>_bp.mtpl` — collapsed BluePrint (uses `\sN\` tokens)
- `<MODULE>_bp.mtpl_symbols.csv` — symbol → per-flow value map (union of flow columns across cycles)
- `<MODULE>_bp.mtpl_expanded` — buildable expansion (substituted form)

Validation contract: `errors(_bp.mtpl_expanded build) ≤ errors(<MODULE>.mtpl_orig build)`.

## 5. Canonical commands — when the user asks for…

These are the **only** commands that may be used. Do not improvise alternative
Python snippets, ad-hoc parsers, or substitute scripts. The orchestrator's
3-phase contract is fixed: `compare` → produces the comparison CSV;
`generate` → produces `_bp.mtpl` + `_bp.mtpl_symbols.csv`; `validate` →
runs structural + consistency + build-error contract.

### "Generate the BP" / "collapse the mtpl" / "create `_bp.mtpl`"
Run phases `compare` + `generate`. The simplest is to run `all` (which also
validates) — never run only `generate` from a stale compare CSV.

```powershell
cd C:\Users\yrakotch\source\repos\nvl_cpu_idg\.tmp_arr_core_compare
& "C:/Users/yrakotch/AppData/Local/Programs/Python/Python314/python.exe" symbolize_mtpl.py all
```

Produces (in `Modules/<...>/<MODULE>/`):
- `<MODULE>_bp.flows_compare.csv`     (canonical — see §2)
- `<MODULE>_bp.mtpl`                  (collapsed BluePrint with `\sN\` tokens)
- `<MODULE>_bp.mtpl_symbols.csv`      (symbol → per-flow value map)
- `<MODULE>_bp.mtpl_expanded`         (buildable substituted form)

### "Run only the comparison" / "regenerate `flows_compare.csv`"
```powershell
& "<py>" symbolize_mtpl.py compare
```

### "Regenerate `_bp.mtpl` from existing compare CSV"
```powershell
& "<py>" symbolize_mtpl.py generate
```

### "Run full validation" / "validate the BP" / "check the build contract"
```powershell
& "<py>" symbolize_mtpl.py validate
```

`validate` performs **all three** checks — none may be skipped or replaced:
1. **Structural validation** — every `\sN\` token in `_bp.mtpl` has a row in
   `_bp.mtpl_symbols.csv`; every symbol row covers every flow column.
2. **Symbol-consistency** — `_load_symbols_from_compare_csv()` round-trip:
   the symbols extracted from the compare CSV must match the on-disk
   `_bp.mtpl_symbols.csv` (cycle-aware: column union allowed).
3. **Build-error contract** — run `torch.exe build -p mtproj --ms /p:BuildProjectReferences=false`
   in the module directory against (a) `<MODULE>.mtpl_orig` and
   (b) `<MODULE>_bp.mtpl_expanded`. The expanded build's error count
   **must be ≤** the orig's. PASS = `errors(expanded) ≤ errors(orig)`.

### Standard "starting from scratch" sequence (cycle 1)
```powershell
$mod = 'C:\Users\yrakotch\source\repos\nvl_cpu_idg\Modules\ARR\ARR_CORE_CXX'
Get-ChildItem $mod -Filter '*_bp.*' -ErrorAction SilentlyContinue | Remove-Item
cd C:\Users\yrakotch\source\repos\nvl_cpu_idg\.tmp_arr_core_compare
& "<py>" symbolize_mtpl.py all
```

Subsequent runs without deleting `_bp.*` artifacts are treated as **cycle 2+**
(cumulative): numbering of new symbols continues from the on-disk max,
existing symbol assignments are preserved, and flow columns are unioned.

## 6. What to do if asked for a different format

Push back. Cite this file. Produce the canonical CSV first, then optionally
post-process it to whatever shape the user wants — but the canonical CSV
must always be (re)generated.
