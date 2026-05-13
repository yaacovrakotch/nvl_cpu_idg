# BluePrint module build summary

Generated: 2026-04-28 16:06

Modules built: 26 (18 CXX + 5 non-CXX picks from one-per-group cycle)

| # | Module | Class | Errors | Warnings | Build |
|---:|---|---|---:|---:|---|
| 1 | **ARR_ATOM_CXX** | Class_DNL_S28C | 0 | 323 | PASS |
| 2 | **ARR_CCF_CXX** | Class_DNL_S28C | 0 | 226 | PASS |
| 3 | **ARR_CORE_CXX** | Class_DNL_S28C | 3185 | 6717 | FAIL (pre-existing - fails with HEAD) |
| 4 | **ARR_HBM_CXX** | Class_DNL_S28C | - | - | N/A (no .mtproj) |
| 5 | **ARR_RING_CXX** | Class_DNL_S28C | - | - | N/A (no .mtproj) |
| 6 | **ARR_UNCORE_CXX** | Class_DNL_S28C | 0 | 87 | PASS |
| 7 | **CLK_BASE_CS40** | Class_DNL_S28C | 1 | 1 | FAIL (pre-existing - .mtproj path mismatch) |
| 8 | **DRV_RESET_CXX** | Class_DNL_S28C | 0 | 131 | PASS |
| 9 | **DRV_TAP_CXX** | Class_DNL_S28C | - | - | N/A (no .mtproj) |
| 10 | **FUN_ATOM_CX48** | Class_NVL_H16C | 0 | 304 | PASS |
| 11 | **FUS_FSG_CXX** | Class_DNL_S28C | 0 | 73 | PASS |
| 12 | **FUS_FUSEBURN_CXX** | Class_DNL_S28C | 0 | 367 | PASS |
| 13 | **MIO_HPTP_CXPKGHX** | Class_NVL_H16C | 0 | 248 | PASS |
| 14 | **PTH_BGR_CJ816P** | Class_DNL_S28C | - | - | N/A (no .mtproj) |
| 15 | **PTH_PVT_CXX** | Class_DNL_S28C | - | - | N/A (no .mtproj) |
| 16 | **PTH_VDAC_CXX** | Class_DNL_S28C | 0 | 163 | PASS |
| 17 | **PTH_VID_CXX** | Class_DNL_S28C | - | - | N/A (no .mtproj) |
| 18 | **PTH_VMIN_CXX** | Class_DNL_S28C | - | - | N/A (no .mtproj) |
| 19 | **QNR_CARV_CXX** | Class_DNL_S28C | 0 | 86 | PASS |
| 20 | **SCN_ATOM_CX48** | Class_NVL_H16C | 0 | 191 | PASS |
| 21 | **SCN_CONFIG_CXX** | Class_DNL_S28C | - | - | N/A (no .mtproj) |
| 22 | **SCN_CORE_CXX** | Class_DNL_S28C | - | - | N/A (no .mtproj) |
| 23 | **SCN_RING_CXX** | Class_DNL_S28C | - | - | N/A (no .mtproj) |
| 24 | **SCN_UNCORE_CXX** | Class_DNL_S28C | - | - | N/A (no .mtproj) |
| 25 | **TPI_DAS_CXX** | Class_NVL_H16C | 0 | 94 | PASS |
| 26 | **TPI_LJ_CXX** | Class_DNL_S28C | - | - | N/A (no .mtproj) |

## Totals
- PASS: 12 (BluePrint regenerated and built clean)
- FAIL: 2 (BOTH pre-existing - reproduce on HEAD content)
- N/A (no .mtproj, mtpl-only): 12

### Pre-existing failures (verified)
- **ARR_CORE_CXX**: 1377 errors with HEAD `.mtpl`, 3185 with regenerated. Module references unresolved UserVar/SpecificationSet groups (`LocationSets`, `SCVars`, `cpu_all_bf_x_x_ipc_lvl_CPU_BFUNC`, etc.). Fails to build standalone regardless of BluePrint.
- **CLK_BASE_CS40**: 1 error: `Project ...\Modules\CLK\.source\CLK_BASE_CXXX\CLK_BASE_CS40.mtproj not found in the solution`. Solution registration / project path mismatch unrelated to .mtpl content.

Per-build torch logs are under `BuildLogs/`.

