# MTPL BluePrint Generator

## What is a BluePrint?

A BluePrint (BP) is a **compressed, minimized, symbolized version** of a full module `.mtpl` test program file.

If we have the same test appearing twice (or more) in an `.mtpl` where the only change between tests is a parameter indicating the frequency, then the BP includes only **one test** with a corresponding prompt saying: "do this test in frequency1 and frequency2."

The repetitive parts are called **symbols** (e.g., the frequency string is a symbol), while **symbol values** are: frequency1, frequency2, etc.

In the BP, symbols are enclosed in backslashes: `\FREQ_CORNER\`, `\VOLTAGE_CORNER\`, etc.

There can be more than one parameter differentiating between tests — the BP collapses all dimensions simultaneously.

## Origin

Based on the IDG PPT presentation (ww16 2026).  
Reference slides are stored in [`ppt_slides/`](ppt_slides/) (slides 14–24).

## Algorithm

1. **Get Input**: NVL module `.mtpl` file + per-module `bp-config.json`.
2. **Identify symbols**: The values that have different "modes" in the file (e.g., Corner, flow name, voltage, module index, array type, etc.).
3. **Identify symbol values**: For each symbol, list possible values (e.g., `FREQ_CORNER = [F1, F2, F3, F4]`).
4. **If several entities (test/flow) are differentiated only by symbol values**:
   - The symbols are characterized in the prompt file by plain English descriptions.
   - Replace each symbol value with its corresponding `\SYMBOL\` placeholder.
   - Delete duplications (keep only one representative entity per group).
5. **Output**: The BluePrint file (`.mtpl.bp`) + companion prompt (`.prompt.txt`).

**Note**: The Counters section at the top of each `.mtpl` is kept verbatim — it is not symbolized.

## File Structure

```
Modules/
  BluePrint/                          ← Generic engine (this directory)
    Generate-BluePrint.ps1            ← Module-agnostic BP generator
    ppt_slides/                       ← Reference PPT slides (14–24)
    README.md                         ← This file

  ARR/ARR_ATOM_CXPKGS9/BluePrint/    ← CXPKGS9-specific
    bp-config.json                    ← Symbol definitions + replacement pairs
    symbols.json                      ← Human-readable symbol reference
    ARR_ATOM_CXPKGS9.mtpl.bp         ← Generated BluePrint output
    ARR_ATOM_CXPKGS9.prompt.txt      ← Generated expansion prompt

  ARR/ARR_ATOM_CXX/BluePrint/        ← CXX-specific
    bp-config.json                    ← Symbol definitions + replacement pairs
    symbols.json                      ← Human-readable symbol reference
    ARR_ATOM_CXX.mtpl.bp             ← Generated BluePrint output
    ARR_ATOM_CXX.prompt.txt          ← Generated expansion prompt
```

## Usage

```powershell
# From Modules/BluePrint/:
.\Generate-BluePrint.ps1 -InputMtpl "..\ARR\ARR_ATOM_CXPKGS9\ARR_ATOM_CXPKGS9.mtpl" `
                          -ConfigFile "..\ARR\ARR_ATOM_CXPKGS9\BluePrint\bp-config.json"

# With explicit output directory:
.\Generate-BluePrint.ps1 -InputMtpl "C:\...\ARR_ATOM_CXX.mtpl" `
                          -ConfigFile "C:\...\bp-config.json" `
                          -OutputDir  "C:\...\BluePrint"
```

When `-OutputDir` is omitted, output goes to a `BluePrint/` folder next to the input `.mtpl`.

## Adding a New Module

1. Analyze the module's `.mtpl` to identify repeating test blocks and the dimensions that vary between them (symbols).
2. Create a `bp-config.json` in the module's `BluePrint/` directory following the schema below.
3. Run `Generate-BluePrint.ps1` with the new config.

### bp-config.json Schema

```json
{
  "module": "MODULE_NAME",
  "description": "One-line module description",

  "symbols": [
    {
      "name": "SYMBOL_NAME",
      "description": "Plain English description of this symbol",
      "values": ["VALUE1", "VALUE2", "VALUE3"],
      "replacements": [
        {"find": "literal_text_to_find", "replace": "text_with_\\SYMBOL\\"}
      ]
    }
  ],

  "normalization": [
    {"pattern": "regex_pattern", "replacement": "replacement_text"}
  ],

  "notes": [
    "Module-specific note for the prompt file."
  ]
}
```

**Key points**:
- **Symbol order matters**: Symbols are processed in array order. Place more-specific symbols first (e.g., `ECC_FREQ` with F5/F6/F7 before `FREQ_CORNER` with F1–F4) to avoid partial matches.
- **Replacements are literal**: `find`/`replace` use exact string matching (not regex).
- **Normalization rules** are regex patterns applied before dedup comparison (e.g., normalizing `BypassPort` TPRules or `FuseNamespace` values).
- **BaseNumbers** are always normalized automatically — no need to add them to config.

## Results

| Module | Input Lines | Input Blocks | Unique Templates | Block Compression | Line Reduction |
|--------|-------------|-------------|------------------|-------------------|----------------|
| CXPKGS9 | 24,629 | 363 | 261 | 28.1% | 82.7% |
| CXX | 25,732 | 360 | 228 | 36.7% | 82.5% |

## Symbols Summary

### Common symbols (both modules):
| Symbol | Values | Description |
|--------|--------|-------------|
| `\FREQ_CORNER\` | F1, F2, F3, F4 | Frequency corner for VMIN search tests |
| `\COVERAGE_TYPE\` | COMBINED, SSA_L2DATA, ... | Array coverage variant |
| `\MODULE_INDEX\` | M0, M1, M2, M3 | L2 cache module index |
| `\VOLTAGE_CORNER\` | MIN, MAX | Voltage corner for raster tests |
| `\SSA_ARRAY_TYPE\` | L2_DATA, L2_TAG | SSA array type |
| `\LSA_ARRAY_TYPE\` | L2_C6, L2_LRU, L2_STATE | LSA array type |
| `\REP_DIRECTION\` | VMIN, VMAX | Repair direction flag |
| `\L2_ENDCPU_TYPE\` | TAG, DATA | L2 sub-array at ENDCPU |
| `\HRY_PHASE\` | PRE, POST | HRY test phase |
| `\RASTERLOOP_TYPE\` | VMAXRASTERLOOP, VMINRASTERLOOP | PatConfig raster loop |
| `\PMUX_INDEX\` | 0, 1, 2, 3 | Power-mux callback index |

### CXPKGS9 only:
| Symbol | Values | Description |
|--------|--------|-------------|
| `\CPU_DIE\` | CPU0, CPU1 | Dual-die selector (_CPU1 suffix) |

### CXX only:
| Symbol | Values | Description |
|--------|--------|-------------|
| `\ECC_FREQ\` | F5, F6, F7 | ECC frequency corner (ECCON/ECCSBFDV) |
| `\ECC_MODULE\` | M0, M1, M2, M3 | ECCSBFDV CtvTokensTC module index |

## GitHub Repository

Public repo: https://github.com/yaacovrakotch/nvl_cpu_idg
