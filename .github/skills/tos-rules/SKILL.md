---
name: tos-rules
description: 'Comprehensive guide for TOS (OTPL) SelectorRules in the NVL test program repository. This is the authoritative reference — any AI Agent must read this skill before answering questions or performing tasks related to TOS rules, including adding rules, modifying rules, understanding rule syntax, or referencing rules in Pymtpl modules.'
---

# TOS Rules Skill

This skill teaches an AI Agent everything needed to read, understand, and add new `SelectorRule` entries to the TOS Rules file in this repository.

## When to Use This Skill

- Adding a new BOM-based rule (e.g., a new package/BOM group needs a dedicated rule)
- Adding a new location-based rule (e.g., a new location set needs a rule)
- Understanding how an existing rule works or how it is used in a module
- Referencing a rule from a Pymtpl module (e.g., setting `BypassPort`)
- Troubleshooting rule load errors or runtime errors

---

## Background: What Are TOS Rules?

Rules are an **OTPL feature** (`hdmtOS 3.7.0.0+`) that allow a single named variable (the **outcome**) to be selected at test program **load time** based on the first matching condition in a list. Once loaded, rules are re-evaluated any time relevant UserVar values change.

Key terminology:

| Term | Meaning |
|------|---------|
| `SelectorRuleCollection` | A named group of `SelectorRule` blocks |
| `SelectorRule` | A single rule that evaluates conditions to pick one outcome |
| Outcome | A named result chosen if its condition is true |
| Fallback outcome | An outcome with **no condition** — always matches, acts like `default` |

**Critical rule**: If no condition matches and there is no fallback outcome, the test program will throw a **load error** or **runtime error**. Always include a fallback outcome (e.g., `no;` or `default;`).

---

## File Location

TOS Rules are defined at multiple places in the codebase. Ask the user. For NVL Repo specifically, TOS Rules are defined in:

```
BaseInputs/Common/Common_Files/TOSRules.usrv
```

This file is declared in a `Shared { }` block, making all rules available across all BOMs using the `__shared__::` namespace prefix.

---

## OTPL Syntax

```otpl
Version 1.0;

Shared
{
    SelectorRuleCollection <CollectionName>
    {
        ### <Comment describing the rule> || Requester: <Name> || Usage: <example usage>
        SelectorRule <RuleName>(<Outcome1>, <Outcome2>, ..., <FallbackOutcome>)
        {
            <Outcome1> => <condition_expression>;
            <Outcome2> => <condition_expression>;
            <FallbackOutcome>;   # No condition = always matches (fallback)
        }
    }
}
```

### Condition Expression Operators

| Operator / Function | Description | Example |
|---|---|---|
| `==` | String equality | `SCVars.SC_STEP == "A"` |
| `!=` | String inequality | `SCVars.SC_STEP != "A"` |
| `\|\|` | Logical OR | `expr1 \|\| expr2` |
| `&&` | Logical AND | `expr1 && expr2` |
| `contains(str, substr)` | Substring match | `contains(SCVars.SC_FACILITYID, "GDL")` |
| `GetEnvironmentVariable("VAR")` | Read an environment variable | `GetEnvironmentVariable("BOMGROUP")` |

### Referencing UserVars

- **Shared UserVars** (defined in `Shared { }`): referenced as `SCVars.SC_LOCN` or `__shared__::SCVars.SC_LOCN`
- **Local UserVars** (defined in a specific BOM): referenced with the `__main__::` prefix

---

## The Two SelectorRuleCollections in This Repo

### 1. `TpRule` — General Test Program Rules

The primary collection. Contains all BOM-based and location-based rules.

**Namespace for module usage:** `__shared__::TpRule.<RuleName>(...)`

### 2. `DieIndic` — Dielet Indicator Rules

A collection of child rules (`if_cpu`, `if_gcd`, `if_hub`, `if_pcd`) and a parent composite rule (`DieCombo`) for driving behavior based on which dielets are present in the package. Child rules can be called **from within other rules** using the `RuleCollection.RuleName(TrueOutcome, FalseOutcome)` syntax.

**Namespace for module usage:** `__shared__::DieIndic.<RuleName>(...)`

---

## The Two Main Rule Patterns

### Pattern 1: BOM-Based Rule (Binary `yes`/`no`)

Used to enable or disable behavior for a specific BOM group. Always uses `GetEnvironmentVariable("BOMGROUP")`.

```otpl
### This rule can be used to apply condition based on BOM || Requester: <Team> || Usage: BypassPort = __shared__::TpRule.If_CLASS_NVL_S28C(-1,1);
SelectorRule If_CLASS_NVL_S28C(yes, no)
{
    yes => GetEnvironmentVariable("BOMGROUP") == "CLASS_NVL_S28C";
    no;
}
```

### Pattern 2: Location-Based Rule (Binary `yes`/`no`)

Used to enable or disable behavior based on the tester location set. Always uses:
```
contains(LocationSets.<SET_NAME>, "[" + SCVars.SC_LOCN + ":" + SCVars.SC_CURRENT_PROCESS_TYPE + "]")
```

```otpl
### This rule can be used to apply condition based on [SC_LOCN]:[SC_CURRENT_PROCESS_TYPE] || Usage: BypassPort = __shared__::TpRule.If_PHM(-1,1);
SelectorRule If_PHM(yes, no)
{
    yes => contains(LocationSets.PHM, "[" + SCVars.SC_LOCN + ":" + SCVars.SC_CURRENT_PROCESS_TYPE + "]");
    no;
}
```

### Pattern 3: Multi-BOM Selector Rule

Used when different BOM groups need distinct values (e.g., different SpecSet values, different bypass behavior across 3+ BOMs). Uses numbered outcomes with a guaranteed fallback.

```otpl
SelectorRule If_S28_S52_HX28(Outcome1, Outcome2, Outcome3, Outcome4)
{
    Outcome1 => GetEnvironmentVariable("BOMGROUP") == "CLASS_NVL_S28C";
    Outcome2 => GetEnvironmentVariable("BOMGROUP") == "CLASS_NVL_S52C";
    Outcome3 => GetEnvironmentVariable("BOMGROUP") == "CLASS_NVL_HX28C";
    Outcome4;   # fallback
}
```

### Pattern 4: Calling a Child Rule from a Parent Rule

A `SelectorRule` can call another rule as a boolean expression using `Collection.RuleName(TrueOutcome, FalseOutcome)`:

```otpl
SelectorRule DieCombo(all, cg, cpu, default)
{
    all => DieIndic.if_cpu(True, False) && DieIndic.if_gcd(True, False);
    cg  => DieIndic.if_cpu(True, False) && DieIndic.if_gcd(True, False);
    cpu => DieIndic.if_cpu(True, False);
    default;
}
```

---

## Known BOM Groups in This Repository

| BOMGROUP Value | Description |
|---|---|
| `CLASS_NVL_S28C` | Novalake S28C (i5/i7 Desktop) |
| `CLASS_NVL_S52C` | Novalake S52C (i9 Desktop) |
| `CLASS_NVL_S28CB` | Novalake S28C BLLC |
| `CLASS_NVL_S52CB` | Novalake S52C BLLC |
| `CLASS_NVL_S16C` | Novalake S16C (i5 Desktop, CDIE-48) |
| `CLASS_NVL_HX28C` | Novalake HX28C (Mobile) |
| `CLASS_NVL_H16C` | Novalake H16C (Mobile, 64EU) |
| `CLASS_NVL_P16C` | Novalake P16C (Mobile, 192EU) |
| `CLASS_NVL_U8C` | Novalake U8C (Ultra Mobile) |
| `CLASS_NVL_UL6C` | Novalake UL6C (Ultra Low Power) |
| `CLASS_NVL_S8C` | Novalake S8C |
| `CLASS_NVL_AX` | Novalake AX |
| `CLASS_NVL_AX16C` | Novalake AX16C |
| `CLASS_NVL_AX28C` | Novalake AX28C |
| `CLASS_NVL_AM` | Novalake AM |
| `CLASS_DNL_S28C` | Denverton Lake S28C |
| `CLASS_DNL_S16C` | Denverton Lake S16C |
| `CLASS_DNL_S8C` | Denverton Lake S8C |
| `CLASS_DNL_S52CB` | Denverton Lake S52C BLLC |

### BOM Group Groupings

| Grouping Rule | BOMs Covered |
|---|---|
| `If_32EU` | S28C, S28CB, S52C, S16C, UL6C, DNL_S28C, HX28C |
| `If_64EU` | H16C, U8C |
| `If_192EU` | P16C |
| `If_M_PKGs` | HX28C, H16C, P16C, U8C, UL6C (Mobile packages) |
| `If_S_PKGs` | S28C, S52C, S28CB, S16C, DNL_S28C (Desktop/S packages) |
| `If_DS0_DS1_M` | DS0=S28C/S28CB/S16C/DNL_S28C, DS1=S52C, M=HX28C/H16C/P16C/U8C/UL6C |

---

## How Rules Are Used in Pymtpl Modules

### Setting `BypassPort`

The most common use. `BypassPort = 1` bypasses the test; `BypassPort = -1` enables it.

```python
# In Pymtpl: bypass test on all BOMs EXCEPT CLASS_NVL_S28C
method.BypassPort = "__shared__::TpRule.If_CLASS_NVL_S28C(-1,1)"

# In Pymtpl: bypass test at all locations EXCEPT PHM
method.BypassPort = "__shared__::TpRule.If_PHM(-1,1)"
```

In MTPL (generated output), it looks like:
```otpl
BypassPort = __shared__::TpRule.If_CLASS_NVL_S28C(-1,1);
```

### Setting a Timing or SpecSet Parameter

When a rule has 3+ outcomes, each outcome maps positionally to the argument list at the call site:

```otpl
# Rule: SelectorRule BomGroupRule(slow, mid, fast)
Timing = TimingSelect.BomGroupRule("10MHz_timing", "100MHz_timing", "200MHz_timing");
# slow => "10MHz_timing", mid => "100MHz_timing", fast => "200MHz_timing"
```

---

## Step-by-Step: How to Add a New TOS Rule

### Step 1: Determine the Rule Type

- **New single-BOM rule** → Use `If_CLASS_<BOMGROUP>(yes, no)` pattern
- **New location-set rule** → Use `If_<LOCATIONSET>(yes, no)` pattern
- **Multi-BOM selector** → Use numbered outcomes `(Outcome1, ..., OutcomeN)` with fallback
- **Dielet-based rule** → Add to `DieIndic` collection; check `DieCombo` first if a combo exists

### Step 2: Check for Existing Rules

Before adding a new rule, verify the rule doesn't already exist. Common rules to reuse:

- Single-BOM checks: `If_CLASS_NVL_<BOM>` rules already exist for most BOMs
- Multi-BOM: Check `If_32EU`, `If_64EU`, `If_192EU`, `If_M_PKGs`, `If_S_PKGs`, `If_DS0_DS1_M`
- Location: `If_PHM`, `If_CHOT`, `If_CCOLD`, `If_RCHOT`, `If_RCCOLD`, `If_PHMHOT`, `If_PHMCOLD`, `If_PHMROOM`, `If_COLD`, `If_RCHOT_CHOT`, `If_RCCOLD_CCOLD`
- Fuse/special: `FuseSpecial`, `FuseRetestBypass`, `If_PHMF`, `If_POSTFUSED`

### Step 3: Write the Rule

Follow the **comment format** before every rule:
```
### <Description of what the rule does> || Requester: <Name/Team> || Usage: <example call>
```

**New BOM rule template:**
```otpl
### This rule can be used to apply condition based on BOM || Requester: <Team> || Usage: BypassPort = __shared__::TpRule.If_CLASS_NVL_XXXX(-1,1);
SelectorRule If_CLASS_NVL_XXXX(yes, no)
{
    yes => GetEnvironmentVariable("BOMGROUP") == "CLASS_NVL_XXXX";
    no;
}
```

**New location rule template:**
```otpl
### This rule can be used to apply condition based on [SC_LOCN]:[SC_CURRENT_PROCESS_TYPE] || Requester: <Team> || Usage: BypassPort = __shared__::TpRule.If_NEWLOCN(-1,1);
SelectorRule If_NEWLOCN(yes, no)
{
    yes => contains(LocationSets.NEWLOCN, "[" + SCVars.SC_LOCN + ":" + SCVars.SC_CURRENT_PROCESS_TYPE + "]");
    no;
}
```

### Step 4: Place the Rule in the Correct Collection

- **General rules** (BOM, location, process, step) → inside `SelectorRuleCollection TpRule { }`
- **Dielet indicator rules** → inside `SelectorRuleCollection DieIndic { }`
- Add adjacent to similar rules (e.g., new BOM rule near other BOM rules)

### Step 5: Validate the Rule

Checklist before committing:
- [ ] Every `SelectorRule` has at least one fallback outcome (no condition) OR all possible conditions are guaranteed to match
- [ ] Outcome names declared in the `SelectorRule(...)` header match exactly the outcome names in the body
- [ ] The order of outcomes in the header matches the intended positional mapping
- [ ] The rule name is unique within its `SelectorRuleCollection`
- [ ] The comment follows the `### Description || Requester: X || Usage: Y` format
- [ ] Referenced `LocationSets.<NAME>` variables exist in the LocationSets file
- [ ] Referenced `SCVars.<VAR>` variables exist in the SCVars UserVars block

---

## Critical Rules and Common Mistakes

### ❌ Missing Fallback — WILL CAUSE LOAD ERROR
```otpl
# WRONG: If SC_LOCN is not "6561" or "7721", this rule fails to load
SelectorRule LocnRule(Outcome1, Outcome2)
{
    Outcome1 => SCVars.SC_LOCN == "6561";
    Outcome2 => SCVars.SC_LOCN == "7721";
    # No fallback! Load error if neither matches.
}
```

### ✅ Correct — Always Include a Fallback
```otpl
SelectorRule LocnRule(Outcome1, Outcome2, default)
{
    Outcome1 => SCVars.SC_LOCN == "6561";
    Outcome2 => SCVars.SC_LOCN == "7721";
    default;  # Always matches if neither above is true
}
```

### ❌ Unreachable Outcome — Logic Bug (No Error, But Silently Wrong)
```otpl
SelectorRule LocnRule(Outcome1, Outcome2, Outcome3)
{
    Outcome1 => SCVars.SC_LOCN == "6561";
    Outcome2 => SCVars.SC_LOCN == "7721";
    Outcome3 => SCVars.SC_LOCN == "7721";  # Never reached — Outcome2 always wins first
    default;
}
```

### ❌ Editing `.mtpl` files Instead of Source
Rules referenced in modules live in `TOSRules.usrv` — do NOT edit `.mtpl` files directly to change rule references. Update the Pymtpl `.py` source file and regenerate.

### ❌ Wrong Namespace Prefix
```otpl
# WRONG: Missing __shared__ prefix for rules in the Shared block
BypassPort = TpRule.If_CLASS_NVL_S28C(-1,1);

# CORRECT:
BypassPort = __shared__::TpRule.If_CLASS_NVL_S28C(-1,1);
```

---

## Outcome Ordering — How Positional Arguments Work

The declaration order of outcomes in `SelectorRule <Name>(A, B, C)` determines which positional argument is selected at call sites:

```otpl
SelectorRule If_S28_S52_HX28(Outcome1, Outcome2, Outcome3, Outcome4)
{
    Outcome1 => GetEnvironmentVariable("BOMGROUP") == "CLASS_NVL_S28C";
    Outcome2 => GetEnvironmentVariable("BOMGROUP") == "CLASS_NVL_S52C";
    Outcome3 => GetEnvironmentVariable("BOMGROUP") == "CLASS_NVL_HX28C";
    Outcome4;  # fallback
}
```

At the call site in a module:
```otpl
Level = __shared__::TpRule.If_S28_S52_HX28("LevelS28", "LevelS52", "LevelHX28", "LevelDefault");
# CLASS_NVL_S28C  → "LevelS28"   (position 1)
# CLASS_NVL_S52C  → "LevelS52"   (position 2)
# CLASS_NVL_HX28C → "LevelHX28"  (position 3)
# anything else  → "LevelDefault" (position 4, fallback)
```

---

## Complete Reference: All Rules in `TpRule` Collection

### BOM-Based Binary Rules (`yes`/`no`)

| Rule Name | `yes` Condition |
|---|---|
| `If_CLASS_NVL_S28C` | BOMGROUP == "CLASS_NVL_S28C" |
| `If_CLASS_NVL_S52C` | BOMGROUP == "CLASS_NVL_S52C" |
| `If_CLASS_NVL_S28CB` | BOMGROUP == "CLASS_NVL_S28CB" |
| `If_CLASS_NVL_S16C` | BOMGROUP == "CLASS_NVL_S16C" |
| `If_CLASS_NVL_HX28C` | BOMGROUP == "CLASS_NVL_HX28C" |
| `If_CLASS_NVL_H16C` | BOMGROUP == "CLASS_NVL_H16C" |
| `If_CLASS_NVL_P16C` | BOMGROUP == "CLASS_NVL_P16C" |
| `If_CLASS_NVL_UL6C` | BOMGROUP == "CLASS_NVL_UL6C" |
| `If_SS_NVL_U8C` | BOMGROUP == "CLASS_NVL_U8C" |
| `If_CLASS_NVL_AX28C` | BOMGROUP == "CLASS_NVL_AX28C" |
| `If_CLASS_NVL_AX16C` | BOMGROUP == "CLASS_NVL_AX16C" |
| `If_CLASS_DNL_S28C` | BOMGROUP == "CLASS_DNL_S28C" |
| `If_CLASS_NVL_DNL_S28C` | BOMGROUP == S28C OR DNL_S28C |
| `If_32EU` | S28C, S28CB, S52C, S16C, UL6C, DNL_S28C, HX28C |
| `If_64EU` | H16C, U8C |
| `If_192EU` | P16C |
| `If_M_PKGs` | HX28C, H16C, P16C, U8C, UL6C |
| `If_S_PKGs` | S28C, S52C, S28CB, S16C, DNL_S28C |
| `IF_S52` *(2 outcomes: Outcome1, Outcome2)* | Outcome1=S52C; Outcome2=fallback |
| `If_48` | H16C, P16C, S16C |
| `If_18AP` | Int process BOMs at step A |
| `If_BENCHTOP` | SC_BENCHTOP == 1 |
| `PO_Z_step_bypass` | SC_STEP contains "Z" |

### Location-Based Binary Rules (`yes`/`no`)

| Rule Name | `yes` Condition (LocationSet matched) |
|---|---|
| `If_PHM` | LocationSets.PHM |
| `If_CHOT` | LocationSets.CHOT |
| `If_CCOLD` | LocationSets.CCOLD |
| `If_RCHOT` | LocationSets.RCHOT |
| `If_RCCOLD` | LocationSets.RCCOLD |
| `If_PHMHOT` | LocationSets.PHMHOT |
| `If_PHMCOLD` | LocationSets.PHMCOLD |
| `If_PHMROOM` | LocationSets.PHMROOM |
| `If_COLD` | LocationSets.COLD |
| `If_PHMF` | LocationSets.PHMF |
| `If_RCHOT_CHOT` | LocationSets.RCHOT OR CHOT |
| `If_RCCOLD_CCOLD` | LocationSets.RCCOLD OR CCOLD |
| `If_RV` | LocationSets.RV |
| `If_QRE` | CH_QUAL, CC_QUAL, CH_QUAL_RV, CC_QUAL_RV |
| `If_REBI` | LocationSets.INLINE_REBI_RV |
| `If_FacilityID_GDL` | SC_FACILITYID contains "GDL" |
| `If_POSTFUSED` | PHMF, QA_S1, CH_QUAL, CC_QUAL, FC_ENG, FH_ENG, CH_QUAL_RV, CC_QUAL_RV, or SC_LOCN contains "6234" |
| `MTT_Rule` | CH_CHVM, RCHOT, CH_CRV, or SC_ENGID == "QE"/"QZ" |

### Multi-Outcome Location Rules

| Rule Name | Outcomes |
|---|---|
| `FuseSpecial` | fuse, pbic, rv, fh_eng, fc_eng, default |
| `FuseRetestBypass` | Outcome1–Outcome11, default |
| `If_NoGTRecovery` | CLASS, CH_CHVM, RCHOT, CH_QUAL, default |
| `Is_Dieslct` | no (SC_DIESLCT contains "NA"), yes |

### Multi-BOM Selector Rules

| Rule Name | Outcomes |
|---|---|
| `Check_BOM` | Outcome1=S52C, Outcome2=S28C, Outcome3=fallback |
| `If_S28_S52_HX28` | S28C, S52C, HX28C, fallback |
| `If_S28_S52_HX28_P16C` | S28C, S52C, HX28C, P16C, fallback |
| `If_S28_S52_HX28_P16C_H16C` | S28C, S52C, HX28C, P16C, H16C, fallback |
| `If_S28_S52_HX28_P16C_DS28C` | S28C, S52C, HX28C, P16C, DNL_S28C, fallback |
| `If_S28_S52_HX28_P16C_S16C_DS28C` | S28C, S52C, HX28C, P16C, S16C, DNL_S28C, fallback |
| `If_S28_S52_HX28_P16C_H16C_S16C_DS28C` | S28C, S52C, HX28C, P16C, H16C, S16C, DNL_S28C, fallback |
| `If_DS0_DS1_M` | DS0 (S28C/S28CB/S16C/DNL), DS1 (S52C), M (Mobile), fallback |
| `If_C48_DS_AX_M` | DS (S16C/DNL_S16C), AX (AX16C), M (H16C/P16C), fallback |
| `If_HX28C_P16C` | HX28C, P16C, fallback |
| `If_HX28C_P16C_H16C` | HX28C, P16C, H16C, OTHER |
| `If_PACKAGE` | YES (S-PKGs), NO (M-PKGs) — **no fallback, all BOMs must match one** |
| `If_ProcessType` | int, ext, bllc, no |
| `If_18AP` | yes (Intel 18A process at step A), no |
| `If_52_S52CB_DNL52CB` | S52C, S52CB, DNL_S52CB, fallback |
| `If_MICP` | Outcome1 (S52C/S52CB/DNL_S52CB), Outcome2=fallback |
| `If_If_Dielet` | all_die, cpu_gcd_hub, cpu_gcd, cpu_hub, gcd_hub, cpu, gcd, hub, default |
| `If_S28_S52_HX28_P16C_S16C_H16C_U8C_UL6C_S8C_AX_AM_...` | All 17 BOMs + fallback |

### `DieIndic` Collection Rules

| Rule Name | Purpose |
|---|---|
| `if_cpu` | `DIELET_INDICATOR` contains "CPU" |
| `if_gcd` | `DIELET_INDICATOR` contains "GCD" |
| `if_hub` | `DIELET_INDICATOR` contains "HUB" |
| `if_pcd` | `DIELET_INDICATOR` contains "PCD" |
| `if_primech` | Location is CH_HVM or RCH_HVM |
| `DieCombo` | Full 16-outcome combo of dielet presence |
| `AllDie` | all dielets + primary socket; `default` fallback |
| `If_DummyData` | Dielet combo restricted to primary sockets |

---

## Source File Reference

- **TOSRules file:** [BaseInputs/Common/Common_Files/TOSRules.usrv](../../../../BaseInputs/Common/Common_Files/TOSRules.usrv)
- **Pymtpl instructions:** [.github/instructions/pymtpl.instructions.md](../../instructions/pymtpl.instructions.md)
- **Program flows instructions:** [.github/instructions/programflows.instructions.md](../../instructions/programflows.instructions.md)
