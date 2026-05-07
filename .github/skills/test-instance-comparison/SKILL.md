---
name: test-instance-comparison
description: Extract and compare test instances and flows between one or two test programs. Parses STPL/TPL files via the Trace API, walks the MainFlow tree in true execution order (DeepSelect), and outputs results to CSV. Use when the user asks to compare test programs, diff TPs, list instances in a flow/module, check flow execution order, or analyze what changed between two TPs (instance presence, ordering, parameters, bypass, EDC).
argument-hint: -StplPath <stpl> -TplPath <tpl> -ModuleName <pattern> -OutputCsvPath <csv> [-Mode single|compare|mcp] [-StplPath2 <stpl2> -TplPath2 <tpl2>]
user-invokable: true
---

# Test Instance & Flow Comparison

This skill extracts and compares test instances from one or two test programs using the `ApiSamples.TestInstanceComparison` tool (.NET 9, built on the Trace API).

> **Why this exists** — STPL module listing order, directory order, and `.mtpl` FlowItem order do **NOT** reflect actual execution order. The only correct way to determine "which instance runs before another" is to walk `testProgram.MainFlow.DeepSelect<TestInstance>()` from the Trace API. This tool already does that for you.

## Files in this skill

- [`compare_test_instances.ps1`](./compare_test_instances.ps1) — PowerShell wrapper
- [`_common.ps1`](./_common.ps1) — shared usage-logging helpers (dot-sourced)

## Tool resolution order

The wrapper picks the first available of:

1. **Local published .exe** (if deployed alongside the skill):  
   `.github/skills/test-instance-comparison/TestInstanceComparison/ApiSamples.TestInstanceComparison.exe`
2. **Authoritative published .exe** on the network share:  
   `I:\engineering\dev\user_links\yrakotch\LLM\CODE\TestInstanceComparison\ApiSamples.TestInstanceComparison.exe`
3. **`dotnet run`** against the source project:  
   `\\ger.corp.intel.com\ec\proj\mdl\ha\intel\engineering\dev\sctp\SmartTP-Class\common\Tools\ApiSamples.TestInstanceComparison`

## Modes

| Mode        | Purpose |
|-------------|---------|
| **single**  | Extract test instances from a single test program (default) |
| **compare** | Compare test instances between two test programs side-by-side |
| **mcp**     | Run as MCP server for AI-assistant integration (JSON-RPC 2.0 over stdio) |

## Parameters

| Parameter        | Required                  | Description |
|------------------|---------------------------|-------------|
| `StplPath`       | ✅ (single & compare)     | Path to the `SubTestPlan.stpl` for TP1 |
| `TplPath`        | ✅ (single & compare)     | Path to the `BaseTestPlan.tpl` for TP1 |
| `ModuleName`     | ✅ (single & compare)     | Module/flow name pattern (case-insensitive substring) |
| `OutputCsvPath`  | ✅ (single & compare)     | Output CSV path |
| `StplPath2`      | Compare mode only         | STPL for TP2 |
| `TplPath2`       | Compare mode only         | TPL for TP2 |
| `Mode`           | Optional (default `single`) | `single` \| `compare` \| `mcp` |
| `NoFeedback`     | Optional                  | Skip the interactive feedback prompt |

## How to invoke

### Single TP — extract instances in a flow/module

```powershell
.\.github\skills\test-instance-comparison\compare_test_instances.ps1 `
    -StplPath "<stpl_path>" `
    -TplPath  "<tpl_path>" `
    -ModuleName "<module_or_flow_substring>" `
    -OutputCsvPath "<csv_path>"
```

### Compare two TPs

```powershell
.\.github\skills\test-instance-comparison\compare_test_instances.ps1 -Mode compare `
    -StplPath  "<stpl1>" -TplPath  "<tpl1>" `
    -StplPath2 "<stpl2>" -TplPath2 "<tpl2>" `
    -ModuleName "<module_or_flow_substring>" `
    -OutputCsvPath "<csv_path>"
```

### MCP server mode

```powershell
.\.github\skills\test-instance-comparison\compare_test_instances.ps1 -Mode mcp
```

### Direct .exe invocation

```powershell
& "I:\engineering\dev\user_links\yrakotch\LLM\CODE\TestInstanceComparison\ApiSamples.TestInstanceComparison.exe" <stpl> <tpl> <module> <csv>
& "I:\engineering\dev\user_links\yrakotch\LLM\CODE\TestInstanceComparison\ApiSamples.TestInstanceComparison.exe" <stpl1> <tpl1> <stpl2> <tpl2> <module> <csv>
& "I:\engineering\dev\user_links\yrakotch\LLM\CODE\TestInstanceComparison\ApiSamples.TestInstanceComparison.exe" --mcp
```

## Test program file locations

- **STPL**: `SubTestPlan_<CLASS>.stpl` in the TP root
- **TPL**:  `BaseTestPlan_<CLASS>.tpl`  in the TP root

For NVL the in-repo POR TP files typically live under:

```
POR_TP\<package>\SubTestPlan_<...>.stpl
POR_TP\<package>\BaseTestPlan_<...>.tpl
```

## Module/flow name patterns

The `ModuleName` parameter is a case-insensitive substring match against flow and module names in the test program. Examples: `ARR_ATN_CDIE`, `SCN_SA`, `ARR_CCF`, `VMIN`, `LFM`.

### Resolving module-level flows that return 0 instances

Module-level flows defined inside `Modules/.../<MODULE>.mtpl` (e.g. `ARR_ATOM_CXX_F1XAT`) are usually **not** directly reachable from `MainFlow.DeepSelect<TestInstance>()`. Querying the skill with the bare flow name returns 0 instances. They are wired in via wrapper sub-flows in `POR_TP/<product>/ProgramFlowsTestPlan/IPC_FLOWS.mtpl`:

```
Flow F1XAT_SubFlow
    FlowItem ARR_ATOM_CXX_F1XAT IPC::ARR_ATOM_CXX::ARR_ATOM_CXX_F1XAT
```

That `<FLOW>_SubFlow` is then called from a `SPEEDPRL<N>CPU_SubFlow`. At runtime the Trace API renames each leaf instance with the wrapper scope prefix, e.g.:

```
F1XAT_SubFlow_SPEEDPRL0CPU::ARR_ATOM_VMIN_E_F1XAT_HITO_VCCIA_F1_X_SSA_L2DATA
F2XAT_SubFlow_SPEEDPRL2CPU::ARR_ATOM_VMIN_E_F2XAT_HITO_VCCIA_F2_X_SSA_L2DATA
F3XAT_SubFlow_SPEEDPRL2CPU::ARR_ATOM_VMIN_E_F3XAT_HITO_VCCIA_F3_X_SSA_L2DATA
```

**Recipe** when the skill returns 0 for `<FLOW>`:

1. Re-run the skill with a wide filter (e.g. `"_"`) to dump every reachable instance:
   ```powershell
   & $exe $stpl $tpl "_" $allCsv
   ```
2. Find the wrapper scope prefix in the resulting CSV by searching `Test Instance Name` for `<FLOW>_SubFlow_*::`:
   ```powershell
   Import-Csv $allCsv |
     Where-Object { $_.'Test Instance Name' -match "<FLOW>_SubFlow_\w+::" } |
     Select-Object -ExpandProperty 'Test Instance Name' -First 1
   ```
3. Strip the `<FLOW>_SubFlow_<SPEEDPRLn>CPU::` prefix to recover the bare instance name; use that prefix to filter the CSV for the flow's leaf instances in true MainFlow execution order.

## Output

- **Console summary** — extracted instances with template, parent flow, parameters, MTT status.
- **CSV** — columns: `Test Program, Module, Test Instance Name, Parent Flow, Test Template, Test Parameters, Is MTT`.
- In **compare** mode, instances are matched by name across the two TPs and differences are highlighted.

## MCP tools (when run with `-Mode mcp`)

| Tool                        | Description |
|-----------------------------|-------------|
| `extract_test_instances`    | Extract instances from a single TP (`stplPath`, `tplPath`, `moduleName`) |
| `compare_test_instances`    | Compare instances between two TPs (`stplPath1`, `tplPath1`, `stplPath2`, `tplPath2`, `moduleName`) |

## Parsing rules

1. STPL → TPL references are resolved automatically.
2. The tool searches flows and modules whose names contain the `ModuleName` substring (case-insensitive).
3. For each match, it walks `MainFlow.DeepSelect<TestInstance>()` so the result reflects **true execution order**, not file order.
4. In `compare` mode, instances are matched by name across TPs; presence, ordering, parameters, EDC and bypass differences are highlighted.

## Prerequisites

- .NET 9 runtime installed on the machine.
- Network access to `I:\engineering\dev\user_links\yrakotch\LLM\CODE\` (for the published .exe) **or** to `\\ger.corp.intel.com\ec\proj\mdl\ha\intel\engineering\dev\sctp\SmartTP-Class\` (for the `dotnet run` fallback).

## Build (if you need to rebuild the .exe)

```powershell
dotnet publish `
    "\\ger.corp.intel.com\ec\proj\mdl\ha\intel\engineering\dev\sctp\SmartTP-Class\common\Tools\ApiSamples.TestInstanceComparison\ApiSamples.TestInstanceComparison.csproj" `
    -c Release -r win-x64 --self-contained false `
    -o ".github\skills\test-instance-comparison\TestInstanceComparison\"
```
