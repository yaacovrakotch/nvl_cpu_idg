# Known NVL BOM Parameters Reference

This table documents the parameter values for all existing NVL BOMs.
Use it when adding a new BOM to infer likely values for similar products.

## Existing BOM Registry

| BOM Full Name | Short Name | Package Code | Device Code | GCD EU Config | Common Folder | Outcome# in If_BOMname |
|--------------|-----------|-------------|------------|--------------|---------------|------------------------|
| CLASS_NVL_S28C  | S28C  | 63 | AAA | 32EU | Common_Class_NVL_S28C  | Outcome1 |
| CLASS_NVL_S52C  | S52C  | 56 | AAB | 32EU | Common_Class_NVL_S52C  | Outcome2 |
| CLASS_NVL_HX28C | HX28C | 59 | AAA | 32EU | Common_Class_NVL_HX28C | Outcome3 |
| CLASS_NVL_P16C  | P16C  | 69 | AAA | 192EU | Common_Class_NVL_P16C | Outcome4 |
| CLASS_NVL_S16C  | S16C  | 67 | AAA | 32EU | Common_Class_NVL_S16C  | Outcome5 |
| CLASS_DNL_S28C  | S28C  | 63 | AAC | 32EU | Common_Class_DNL_S28C  | Outcome6 |
| CLASS_NVL_H16C  | H16C  | 66 | AAA | 64EU | Common_Class_NVL_H16C  | Outcome7 |
| CLASS_NVL_U8C   | U8C   | 68 | AAA | 64EU | Common_Class_NVL_U8C   | Outcome8 |

> Catch-all: `Outcome9` (no condition — default)

## Location Codes by BOM Type

| BOM | Typical Location Codes (SC_LOCN) |
|-----|----------------------------------|
| S28C, S52C, HX28C, DNL_S28C | 6163, 5163, 6167, 5167, 6168, 5168 |
| P16C, S16C, H16C | 6163, 5163, 6167, 5167 |
| U8C | 6163, 5163, 6167, 5167 |

## DFF XML File Naming Convention

DFF input XML files live in `Modules/TPI/TPI_DFF_XXX/InputFiles/`.

| BOM | CLASS xml | RAWCLASS xml | OLF xml |
|-----|----------|-------------|---------|
| S28C  | NVL_S28C_CLASS.xml  | NVL_S28C_RAWCLASS.xml  | NVL_S28C_OLF.xml  |
| S52C  | NVL_S52C_CLASS.xml  | NVL_S52C_RAWCLASS.xml  | NVL_S52C_OLF.xml  |
| HX28C | NVL_HX28C_CLASS.xml | NVL_HX28C_RAWCLASS.xml | NVL_HX28C_OLF.xml |
| P16C  | NVL_P16C_CLASS.xml  | NVL_P16C_RAWCLASS.xml  | NVL_P16C_OLF.xml  |
| S16C  | NVL_S16C_CLASS.xml  | NVL_S16C_RAWCLASS.xml  | NVL_S16C_OLF.xml  |
| DNL_S28C | NVL_DNLS28C_CLASS.xml | NVL_DNLS28C_RAWCLASS.xml | NVL_DNLS28C_OLF.xml |
| H16C  | NVL_H16C_CLASS.xml  | NVL_H16C_RAWCLASS.xml  | NVL_H16C_OLF.xml  |
| U8C   | NVL_U8C_CLASS.xml   | NVL_U8C_RAWCLASS.xml   | NVL_U8C_OLF.xml   |

**Naming rule for new BOMs:**
- Standard NVL: `NVL_<SHORT_BOM>_CLASS.xml`  (e.g., `NVL_X28C_CLASS.xml`)
- DNL variant: `NVL_DNL<SHORT_BOM>_CLASS.xml`  (e.g., `NVL_DNLX28C_CLASS.xml`)

## TOS Rules EU Mapping

### `If_32EU` (yes condition) — add new 32EU BOMs here
```
yes => GetEnvironmentVariable("BOMGROUP") == "CLASS_NVL_S28C"
    || GetEnvironmentVariable("BOMGROUP") == "CLASS_NVL_S28CB"
    || GetEnvironmentVariable("BOMGROUP") == "CLASS_NVL_S52C"
    || GetEnvironmentVariable("BOMGROUP") == "CLASS_NVL_S16C"
    || GetEnvironmentVariable("BOMGROUP") == "CLASS_NVL_UL6C"
    || GetEnvironmentVariable("BOMGROUP") == "CLASS_DNL_S28C"
    || GetEnvironmentVariable("BOMGROUP") == "CLASS_NVL_HX28C";
```

### `If_64EU` (yes condition) — add new 64EU BOMs here
```
yes => GetEnvironmentVariable("BOMGROUP") == "CLASS_NVL_H16C"
    || GetEnvironmentVariable("BOMGROUP") == "CLASS_NVL_U8C";
```

### `If_192EU` (yes condition) — add new 192EU BOMs here
```
yes => GetEnvironmentVariable("BOMGROUP") == "CLASS_NVL_P16C";
```

## Bomgroup.usrv Template

```
Version 1.0;

Shared
{
    UserVars TorchRulesVars
    {
        String locationCode = "<LOCATION_CODE>";
        String bom = "<BOM_STRING>";
    }

    UserVars GlobalBomGroupName
    {
        String ActiveBomGroup = "<NewBOMFullName>";
    }

    UserVars PerBomTPNameVars
    {
        Const String PerBomTPName1 = "<PerBomTPName1>";    # Ituffname
    }
}
```

## DFF_Screen.txt Entry Template

```
EXEC   ; TEST<n> ; STRING ; LITERAL ; True ; == ; EXPRESSION ; Contains([__shared__::SCVars.SC_PACKAGE], '<PackageCode>') && Contains([__shared__::SCVars.SC_DEVICE], '<DeviceCode>') ; - ; TESTRC<m>  ;  <NextTestLabel or 2>
EXEC   ; TESTRC<m> ; STRING ; LITERAL ; True ; == ; EXPRESSION ; in([__shared__::SCVars.SC_LOCN], <'LOCN1', 'LOCN2', ...>) ; - ; TESTRC<m+1> ; TEST<n>A
EXEC   ; TESTRC<m+1> ; STRING ; GLOBAL     ; __shared__::DFFVars.MTL_FILE_PATH                    ; SET ; LITERAL ; ./Shared/Modules/TPI/TPI_DFF_XXX/InputFiles/<DFF_SHORT>_RAWCLASS.xml ; - ; 1  ; 2
EXEC   ; TEST<n>A  ; STRING ; GLOBAL     ; __shared__::DFFVars.MTL_FILE_PATH                    ; SET ; LITERAL ; ./Shared/Modules/TPI/TPI_DFF_XXX/InputFiles/<DFF_SHORT>_CLASS.xml ; - ; 1  ; 2
```

**Counting rule:** Existing BOMs use TEST1–TEST10 and TESTRC1–TESTRC20 (2 TRC per BOM).
A new 9th BOM would use TEST11 and TESTRC21/TESTRC22.
