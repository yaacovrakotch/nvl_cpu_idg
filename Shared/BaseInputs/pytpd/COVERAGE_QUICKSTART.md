# Quick Guide: Coverage in VS Code

## TL;DR - Fastest Way

1. **Run test with coverage** (choose one method):
   ```bash
   # Method 1: Using cov.py (RECOMMENDED - now supports XML!)
   python3 main/cov.py xml main/test/test_pymtpl.py -v
   ```

2. **Install Coverage Gutters** extension in VS Code (if not already installed)

3. **View coverage**: Open any Python file → Click "Watch" in status bar

That's it! You'll see green/red indicators in the gutter showing covered/uncovered code.

## Scripts Available

| Script/Command | Purpose |
|--------|---------|
| `python3 main/cov.py xml <test.py>` | Run test + generate XML (built-in, RECOMMENDED) |

## Using cov.py (RECOMMENDED)

The `cov.py` wrapper now supports XML generation directly:

```bash
# Single test with XML output for VS Code
python3 main/cov.py xml main/test/test_pymtpl.py -v

# Accumulated coverage (run multiple tests)
python3 main/cov.py curdir main/test/test_pymtpl.py -v
python3 main/cov.py curdir pymtpl/test/test_core.py -v
# ... run more tests ...
python3 main/cov.py xml  # Generate XML from accumulated coverage

# Other useful commands
python3 main/cov.py text main/test/test_pymtpl.py -v  # Text report
python3 main/cov.py html  # HTML report (after accumulated coverage)
python3 main/cov.py report  # Text report (after accumulated coverage)

# Run coverage on everything at once (untested)
python3 main/cov.py xml main/run_tests.py -show -gadget
```

## Troubleshooting

**Problem**: `main/cov.py` has import errors
- **Solution**: source sourcemefiles/vscodevepsourceme.rc

**Problem**: Coverage Gutters can't find coverage.xml
- **Solution**: 
  1. Verify .vscode/settings.json includes  "coverage-gutters.coverageFileNames": [ "coverage.xml" ]
  2. Make sure `coverage.xml` is in the workspace root
  3. Reload VS Code window (Ctrl+Shift+P → "Developer: Reload Window")
  4. Try Command Palette: "Coverage Gutters: Display Coverage"
  5. Check VS Code Output panel (View → Output → "Coverage Gutters") for error messages

**Problem**: No coverage showing in VS Code
- **Solution**: 
  1. Check `coverage.xml` exists: `ls -la coverage.xml`
  2. Make sure Coverage Gutters extension is installed
  3. Open a Python source file (not a test file)
  4. Click "Watch" in the status bar (bottom-right)
  5. Look for coverage percentage in status bar
  6. If you see "No coverage" - reload VS Code window