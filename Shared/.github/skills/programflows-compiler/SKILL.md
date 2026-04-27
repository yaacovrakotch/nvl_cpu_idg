---
name: programflows-compiler
description: 'Full workflow for updating and compiling ProgramFlows in the NVL test program. Use when asked to update program flows, regenerate programflows mtpl, add a subflow to program flows, modify flow routing, update programflows for a BOM, or compile IPH_FLOWS/IPC_FLOWS/IPP_FLOWS/IPG_FLOWS/ProgramFlowsHUB/ProgramFlowsGCD/ProgramFlowsCPU/ProgramFlowsPCD. Handles dielet-level and package-level flows, Torch fixer execution, .stpl guard, and git commit scoping.'
user-invocable: true
---

# ProgramFlows Compiler

> ## âš ï¸ IMPORTANT â€” nvl.common Cannot Compile ProgramFlows Directly
>
> **ProgramFlows compilation is NOT done from the `nvl.common` repository.**
>
> `nvl.common` is a shared submodule. The ProgramFlows `.py` source files in this repo
> (`POR_TP/<BOM>/ProgramFlowsTestPlan/ProgramFlows.py`, `ProgramFlowsSharedPKG.py`) depend on
> dielet-specific files (`ProgramFlowsCPU.py`, `ProgramFlowsGCD.py`, `ProgramFlowsHUB.py`,
> `ProgramFlowsPCD.py`) that only exist in the dielet repos.
>
> **To compile or regenerate ProgramFlows, you must work from the appropriate dielet repo:**
>
> | Dielet | Repo |
> |--------|------|
> | CPU | `nvl.cpu` |
> | GCD | `nvl.gcd` |
> | HUB | `nvl.hub` |
> | PCD | `nvl.pcd` |
>
> In each dielet repo, `nvl.common` is included as `Shared/`. The ProgramFlows compilation
> commands reference this submodule path automatically.
>
> **If you are currently working in `nvl.common`**, redirect your work to the correct dielet
> repo and re-invoke this skill from there.

---

## What ProgramFlows Files Live in nvl.common

These files in nvl.common are **data/source** files only â€” they are NOT compiled directly from nvl.common:

| File | Role |
|------|------|
| `POR_TP/<BOM>/ProgramFlowsTestPlan/ProgramFlows.py` | Shared flow compilation entry point (requires dielet ProgramFlows<Die>.py imports) |
| `POR_TP/<BOM>/ProgramFlowsTestPlan/ProgramFlowsSharedPKG.py` | Shared package-level flow data (imported by ProgramFlows.py) |

Editing these files in nvl.common is fine â€” but compilation must happen from the dielet repo after the submodule is updated.

---

## Quick Reference â€” Dielet Repo ProgramFlows Compilation

When working from a dielet repo (e.g. `nvl.hub`), the compilation commands are:

```powershell
# Navigate to the ProgramFlowsTestPlan folder for the target BOM
cd POR_TP\<BOM>\ProgramFlowsTestPlan

# Command 1: Compile the dielet IP flow (e.g. IPH_FLOWS.py for HUB)
python ..\..\..\Shared\BaseInputs\pytpd\main\pymtpl.py <IP_FLOWS>.py -env ..\EnvironmentFile.env

# Command 2: Compile the shared package flow
# Set DIE_LIST to one or more dielets: CPU, GCD, HUB, PCD (comma-separated)
# Default (all dielets): "CPU,GCD,HUB,PCD"
$env:DIE_LIST = "<DIE>"
python ..\..\..\Shared\BaseInputs\pytpd\main\pymtpl.py ..\..\..\Shared\POR_TP\<BOM>\ProgramFlowsTestPlan\ProgramFlows.py -env ..\EnvironmentFile.env
```

| Dielet | IP flow file | DIE_LIST value |
|--------|-------------|----------------|
| CPU | `IPC_FLOWS.py` | `CPU` |
| GCD | `IPG_FLOWS.py` | `GCD` |
| HUB | `IPH_FLOWS.py` | `HUB` |
| PCD | `IPP_FLOWS.py` | `PCD` |
| All | (not applicable) | `CPU,GCD,HUB,PCD` |

> **Legacy manual Torch command** (for reference — use `run_torch_fixer.py` script instead):
> ```powershell
> & "$env:TorchAPIExecPath\Torch.exe" fix-tp --sln-config Class_NVL_S28C -s NVL_Common.sln -p POR_TP/Class_NVL_S28C/Class_NVL_S28C.tpproj
> ```

For the full step-by-step compilation workflow, the Torch fixer, `.stpl` guard, and commit guidance, open the corresponding skill from the **dielet repo** (e.g. `nvl.hub/.github/skills/programflows-compiler/SKILL.md`).

```

| Dielet | IP flow file | DIE_LIST value |
|--------|-------------|----------------|
| CPU | `IPC_FLOWS.py` | `CPU` |
| GCD | `IPG_FLOWS.py` | `GCD` |
| HUB | `IPH_FLOWS.py` | `HUB` |
| PCD | `IPP_FLOWS.py` | `PCD` |
| All | (not applicable) | `CPU,GCD,HUB,PCD` |

> **Legacy manual Torch command** (for reference â€” use `run_torch_fixer.py` script instead):
> ```powershell
> & "$env:TorchAPIExecPath\Torch.exe" fix-tp --sln-config Class_NVL_S28C -s NVL_Common.sln -p POR_TP/Class_NVL_S28C/Class_NVL_S28C.tpproj
> ```

For the full step-by-step compilation workflow, the Torch fixer, `.stpl` guard, and commit guidance, open the corresponding skill from the **dielet repo** (e.g. `nvl.hub/.github/skills/programflows-compiler/SKILL.md`).

