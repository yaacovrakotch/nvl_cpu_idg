---
applyTo: "**/TPI_SKUCTRL_XXX/**"
---

# TPI_SKUCTRL_XXX — SKU Manager Control Module

## Module Overview

`TPI_SKUCTRL_XXX` manages SKU-specific frequency settings, SA_VMAXHI voltage token setup, and DFF CHSAVMAX read/write. It branches based on optype to handle initial POR die vs downstream test flows differently.

---

## Editing Rules

- **Pymtpl-based module** — `TPI_SKUCTRL_XXX.py` is the **source of truth**.
- **Never edit `.mtpl` directly** — it is fully regenerated on compilation.
- After any change to `.py`, run the Pymtpl compiler.

---

## Module Initialization

```python
InitializeNVLClass('TPI_SKUCTRL_XXX', 'TPI_SKUCTRL_XXX', tosversion="tos4", binrange=(9360, 9360),
    defaultrm2bin=(99936300, 99936399),
    defaultrm1bin=(98936300, 98936399))
```

---

## Flow Sequence

| Flow | Purpose |
|------|---------|
| `TPI_SKUCTRL_XXX_F5XSN` | SetPassFreq at F5 speed |
| `TPI_SKUCTRL_XXX_BEGINHUBPKG` | SA_VMAXHI token setup with optype branching |
| `TPI_SKUCTRL_XXX_ENDHUBPKG` | Write DFF CHSAVMAX at end of hub |
| `TPI_SKUCTRL_XXX_VMAXXSN` | Print SA_VMAXHI_Voltage value to ituff |
| `TPI_SKUCTRL_XXX_LTTCHUBMAX` | Write DFF CHSAVMAX in LTTC (PBIC_DAB only) |

---

## Test Types Used

### SkuManager (custom BaseMethod class)

Handles frequency/domain configuration:

```python
class SkuManager(BaseMethod):
    # Parameters: BypassPort, CurrentOptype, ClassHotProcessOptype,
    #             Domain, MidFreqValue, Mode, PreInstance
```

Current usage: `Mode = "SetPassFreq"` with per-package domain selection via `__shared__::TpRule.If_S_PKGs(...)`.

### PrimeGetDffTestMethod

Reads a DFF token value into shared storage:

```python
PrimeGetDffTestMethod(
    name=...,
    BypassPort=Spec("__shared__::GlobalRule.primaryoptype(1,1,-1,-1,-1,-1,-1,-1,-1,-1)"),
    DieId=Spec("__shared__::DFFVars.DIEID_HUB"),
    OpType="PBIC_DAB",
    Storage="SA_VMAXHI_String",
    TokenName="CHSAVMAX",
)
```

### PrimeSetDffTestMethod

Writes a value back to DFF from storage:

```python
PrimeSetDffTestMethod(
    name=...,
    BypassPort=Spec("__shared__::GlobalRule.primaryoptype(-1,-1,1,1,1,1,1,1,1,1)"),
    DieId=Spec("__shared__::DFFVars.DIEID_HUB"),
    PreInstance="WriteSharedStorage(--token G.U.S.SA_VMAXHI_String --value G.U.D.SA_VMAXHI_Voltage)",
    TokenName="CHSAVMAX",
    TokenValue="Storage.SA_VMAXHI_String",
)
```

### RunCallback

Used for token writes and ituff logging:

```python
RunCallback(
    name=...,
    Callback="WriteSharedStorage",
    Parameters="--token G.U.D.SA_VMAXHI_Voltage --value ...",
    PostInstance="WriteUserVar(--uservar VMAX_HI_Downstream.SA_VMAX_VALUE --value ... --type String)",
)
```

---

## Optype Branch Pattern (BEGINHUBPKG)

The `BEGINHUBPKG` flow branches based on whether the die is a POR or downstream optype:

```python
Flow("TPI_SKUCTRL_XXX_BEGINHUBPKG",
    Fitem("SAME", vmaxhi_token_test,         r0=pFail(setbin=AUTO, ret=0)),
    Fitem("SAME", downstream_getdff_test,
        r0=pPass(goto="CTRL_X_RUNCALLBACK_X_BEGINHUBPKG_X_X_X_X_SETTOKEN_POR"),
        r1=pPass(goto="CTRL_X_RUNCALLBACK_X_BEGINHUBPKG_X_X_X_X_SETTOKEN_DOWNSTREAM")),
    Fitem("SAME", vmaxhi_token_test_por,      r0=pFail(setbin=AUTO, ret=0), r1=pPass(ret=1)),
    Fitem("SAME", vmaxhi_token_test_downstream, r0=pFail(setbin=AUTO, ret=0), r1=pPass(ret=1)),
)
```

- **Result 0** (PrimeGetDff returns 0 = no DFF data) → go to POR path (use FlowMatrixSingular value)
- **Result 1** (PrimeGetDff returns 1 = DFF data available) → go to downstream path (use DFF string)

---

## Key Storage and Token References

| Reference | Purpose |
|-----------|---------|
| `G.U.D.SA_VMAXHI_Voltage` | Shared storage token — holds final SA VMAX HI voltage |
| `G.U.S.SA_VMAXHI_String` | String storage — intermediate for DFF CHSAVMAX write |
| `VMAX_HI_Downstream.SA_VMAX_VALUE` | UserVar — SA_VMAX value for downstream path |
| `__shared__::FlowMatrixSingular.SA_VMAX_VALUE` | POR-path voltage value from flow matrix |

---

## Adding a New Optype Branch — Checklist

1. Add the new `RunCallback` or `PrimeGetDffTestMethod` test instance in `.py`.
2. Add the new `Fitem` to the relevant `Flow(...)` definition with the correct `r0`/`r1` goto destinations.
3. Update `__shared__::GlobalRule.primaryoptype(...)` bypass arguments if the test is optype-gated.
4. Run the Pymtpl compiler to regenerate `.mtpl`.
5. Verify the new `Result` entries appear in the generated `Flow` block.
