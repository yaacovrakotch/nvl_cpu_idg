# Tester Selection Configuration Error

ERROR: Tester count does not match BOM count

Current Configuration:
Target BOMs: {BOMLIST}
Tester Input: {TESTERLIST}
BOM Count: {BOMCOUNT}
Tester Count: {TESTERCOUNT}

Valid Input Examples:

Example 1 - Single 'any' (works with any BOM count):
targetbom: 'Class_NVL_S28C,Class_NVL_HX28C,Class_NVL_S16C'
tester: 'any'

Example 2 - Exact match (3 BOMs = 3 testers):
targetbom: 'Class_NVL_S28C,Class_NVL_HX28C,Class_NVL_S16C'
tester: 'PG,JF04TXBT60365A,any'

Example 3 - Single BOM, single tester:
targetbom: 'Class_NVL_S28C'
tester: 'PG07TXBT65251A'

Example 4 - ALL BOMs with 'any':
targetbom: 'ALL'
tester: 'any'

Example 5 - ALL BOMs with specific testers ({TOTALMATRIXCOUNT} testers for {TOTALMATRIXCOUNT} BOMs):
targetbom: 'ALL'
tester: 'PG,JF,any,PG07TXBT65251A,JF04TXBT60365A,IDC,FM'

Example 6 - Mixed sites and specific testers:
targetbom: 'Class_NVL_S28C,Class_NVL_HX28C'
tester: 'PG07TXBT65251A,IDC'

Note: When using 'ALL', you need exactly {TOTALMATRIXCOUNT} testers for the current matrix configuration.

Available BOMs (dynamically loaded from matrix):
{ALLMATRIXBOMS}

Total BOMs in matrix: {TOTALMATRIXCOUNT}

Available Sites/Testers:
Sites: JF, PG, FM, IDC, BA
Special: any (auto-assign based on selected site)
Specific testers: PG07TXBT65251A, JF04TXBT60365A, etc.

Configuration Rules:

1. Use 'any' alone for all BOMs to use default tester assignment
2. For multiple testers, count must exactly match BOM count
3. Testers are mapped by position: BOM1->Tester1, BOM2->Tester2, etc.
4. No partial matching: Either use 'any' for all, or provide exact count of testers

## Single Mode Restrictions (when enabled):

If you see errors about "Single Mode" or "MultiSwitch disabled":
- Only ONE BOM allowed (no comma-separated BOMs, no 'ALL')
- Only ONE tester allowed (no comma-separated testers)
- Valid single mode examples:
  * targetbom: 'Class_NVL_S28C', tester: 'any'
  * targetbom: 'Class_NVL_S52C', tester: 'PG07TXBT65251A'
- To run multiple BOMs, submit separate workflow runs

Troubleshooting:

Check that your comma-separated tester list has the same number of items as your BOM list
Use 'any' if you want all BOMs to use the default tester for the selected site
Ensure no extra spaces or empty entries in your comma-separated lists
The matrix currently contains {TOTALMATRIXCOUNT} BOMs when using 'ALL'
If in Single Mode: Use only one BOM and one tester per workflow run

Common Mistakes:

Count mismatch: Providing 2 testers for 3 BOMs
Extra spaces: 'PG, JF' instead of 'PG,JF'
Wrong BOM names: Using short names instead of full class names
Empty entries: 'PG,,JF' creates an empty middle entry
Single Mode violations: Using multiple BOMs or testers when restricted

Quick Fix Examples:

Problem: 3 BOMs, 2 testers
targetbom: 'Class_NVL_S28C,Class_NVL_HX28C,Class_NVL_S16C'
tester: 'PG,JF04TXBT60365A'  (WRONG - missing 3rd tester)

Solution: Add the missing tester
targetbom: 'Class_NVL_S28C,Class_NVL_HX28C,Class_NVL_S16C'
tester: 'PG,JF04TXBT60365A,any'  (CORRECT - 3 testers for 3 BOMs)

Alternative: Use 'any' for all
targetbom: 'Class_NVL_S28C,Class_NVL_HX28C,Class_NVL_S16C'
tester: 'any'  (CORRECT - single 'any' works for any BOM count)

Single Mode Fix: Use one BOM only
targetbom: 'Class_NVL_S28C'
tester: 'any'  (CORRECT - single BOM and single tester)

For more help, contact the TPD team.
