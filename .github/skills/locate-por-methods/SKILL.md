---
name: locate-por-methods
description: Locate the correct por_methods.py file in the test program repository. Use when you need to reference test method definitions or parameter types.
argument-hint: "WorkspaceRoot"
user-invokable: true
---

# Locate por_methods.py File

This skill helps locate the correct `por_methods.py` file in a test program repository.

## Purpose

The `por_methods.py` file contains all available test method class definitions with their parameters. Finding the correct file is critical for:
- Determining available test methods
- Validating parameter names and types
- Checking parameter requirements (required vs optional)

## ⚠️ CRITICAL: File Location Rules

**DO NOT USE:** `Scripts/pytpd/pymtpl/por_methods.py` ❌ **WRONG FILE**

**CORRECT LOCATIONS (search in priority order):**
1. `Scripts/pymtpl/pymtpl/por_methods.py` ✅
2. `Shared/BaseInputs/Scripts/por_methods.py` ✅
3. `UserCode/pymtpl/por_methods.py` ✅
4. `Shared/BaseInputs/Scripts/pymtpl/por_methods.py` ✅

**Key Distinctions:**
- ✅ CORRECT: `Scripts/pymtpl/pymtpl/por_methods.py` 
- ❌ WRONG: `Scripts/pytpd/pymtpl/por_methods.py` (pytpd vs pymtpl)

**Important Notes:**
- The por_methods.py file is NOT included in the solution
- Must be located using file_search or grep_search tools
- Different test programs may have the file in different locations
- Always verify the path contains `pymtpl` not `pytpd`

## Search Strategy

1. **Start with file_search** using pattern: `**/por_methods.py`
2. **Filter results** to exclude `pytpd` paths
3. **Prioritize paths** matching the order above
4. **Validate** by reading the first few lines to confirm it contains `BaseMethod` class definitions

## Validation

Once located, verify the file by checking for:
- Import of `BaseMethod` class
- Test method class definitions (e.g., `PrimeFunctionalTestMethod`)
- Parameter decorators like `@required` and `@optional`

## Example Search

```python
# Use file_search
file_search("**/por_methods.py")

# Expected valid result:
# workspace_root/Scripts/pymtpl/pymtpl/por_methods.py

# Invalid result (should be rejected):
# workspace_root/Scripts/pytpd/pymtpl/por_methods.py
```

## Related Documentation

- [10-por-methods-reference.instructions.md](../../instructions/pymtpl/10-por-methods-reference.instructions.md) - Using por_methods.py for type inference
