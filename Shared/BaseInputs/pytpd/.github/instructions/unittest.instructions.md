## How to Run Unit Tests
- YOU MUST RUN UNIT TESTS ONLY AS DEFINED BELOW. ANY OTHER WAY OF RUNNING UNIT TESTS WILL BE MET WITH A PENALTY.
- Do not create a virtual environment.  Use the terminal.
- Some unit tests require being run from the pytpd repository root directory, using the full relative path to the test file. Running tests by changing into subdirectories may cause failures for tests that expect a specific working directory.
- Test files are named `test_*.py` and are located in various `test` directories (e.g., `pymtpl/test`, `gadget/test`).
- Different test classes are defined in different files (e.g., `TestDMRClass8dig` is in `pymtpl/test/test_binctr.py`, `TestGenPy` is in `pymtpl/test/test_mtpl2py.py`, and `BreakAtTest` is in `gadget/test/test_ut.py`).
- To run all tests in a file from the root, use:
  ```shell
  python3 pymtpl/test/test_binctr.py -v -b
  python3 pymtpl/test/test_mtpl2py.py -v -b
  python3 gadget/test/test_ut.py -v -b
  ```
- To run all tests for a specific class, use:
  ```shell
  python3 pymtpl/test/test_binctr.py -v TestDMRClass8dig
  python3 pymtpl/test/test_mtpl2py.py -v TestGenPy
  python3 gadget/test/test_ut.py -v BreakAtTest
  ```
- To run a specific test function, use:
  ```shell
  python3 pymtpl/test/test_binctr.py -v TestDMRClass8dig.test_function_name
  python3 pymtpl/test/test_mtpl2py.py -v TestGenPy.test_function_name
  python3 gadget/test/test_ut.py -v BreakAtTest.test_function_name
  ```

### Creating new unit tests
- When adding new features or fixing bugs, always create or update unit tests in the appropriate `test` directory.
- Follow the existing structure and naming conventions for test files and classes.
- Ensure that unit test functions use comments to describe functionality instead of docstrings.
- For tests that modify global state or class variables, use setUp/tearDown to set and reset state:
  ```python
  def setUp(self):
      # set any global value necessary
      GlobalClass.SOME_VARIABLE = SOME_STATE
  
  def tearDown(self):
      # Restore original state
      GlobalClass.reset()
  ```

### GitHub Pipeline Environment Limitations
- Tests that reference `UT_DIR` (unittest data directory) will not pass in the GitHub pipeline environment because the  directory is not available.  
- When creating new tests, avoid dependencies on `UT_DIR` when possible, or ensure tests gracefully handle its absence.
- For new features, prefer unit tests that don't require external test data files or use in-memory test data instead.
