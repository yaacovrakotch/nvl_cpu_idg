# Copilot Instructions for the pytpd repository

## Project Overview
The `pytpd` (Python Test Program Development) repository is a comprehensive toolkit for semiconductor ATE (Automatic Test Equipment) test program development and management. This is a mature codebase for Intel's manufacturing test infrastructure.

### Key Components
- **`pymtpl/`**: Core test template engine for generating test programs from .mtpl templates
- **`gadget/`**: Utility library with common helpers (logging, file operations, shell utilities)
- **`main/`**: Primary executables and automation scripts for test program lifecycle
- **`mod/`**: Modules for specific test operations and integrations
- **`tp/`**: Test program specific utilities and patterns

## General Guidelines
- Use clear, concise, and well-documented code.
- Follow existing code style and structure.
- When adding new features or fixing bugs, always write or update unit tests.
- **NEVER** change line endings from the original file format. Preserve the existing line ending style (LF vs CRLF) of each file.

## Code Reuse
- Before writing new code, look for existing methods or utilities in the codebase that can be reused.
- Prefer calling existing methods as fallbacks rather than duplicating logic (e.g., use an existing `copytp()` method instead of reimplementing file copy logic).
- The `gadget/` library contains many reusable utilities—check there first for common operations like file handling, logging, and shell commands.
- When a new approach fails or is platform-specific, fall back to proven existing methods rather than writing redundant error-handling code.

## How to Run autopep8 for Code Formatting
- Always run autopep8 after editing any Python file using this exact syntax.

To format Python files according to PEP8 standards, use the following command from the pytpd root directory:
```shell
main/easyautopep8.py /path/to/yourfile.py 
```

To format multiple files at once, list each file path separated by spaces:
```shell
main/easyautopep8.py pymtpl/binctr.py pymtpl/core.py pymtpl/test/test_binctr.py pymtpl/test/test_core.py
```

## Function and Method Documentation Style
- Use reStructuredText (Sphinx) style for all function and method docstrings
- Use `:param:`, `:type:`, `:return:`, `:raises:` format
- For code examples in docstrings, use `::` notation followed by indented code blocks

**Correct format:**
```python
def my_function(arg1, arg2):
    """Brief description of the function.
    
    More detailed explanation if needed.
    
    :param arg1: Description of arg1
    :type arg1: str
    :param arg2: Description of arg2
    :type arg2: int
    :return: Description of return value
    :rtype: bool
    :raises ValueError: When arg2 is negative
    
    Usage::
    
        result = my_function("test", 5)
        print(result)
    """
    pass
```

## How to Run Unit Tests
- Critical: If running unit tests, please read .github/instructions/unittest.instructions.md 

## Unit Test Documentation Style
- When writing or modifying unit tests, use inline comments (`#`) instead of docstrings (`"""`) to describe what each test does.
- Format: Place the comment on the line immediately after the `def test_*():` declaration.

## Going Forward
- Use this as the default style for future unit tests in this repo: behavior/output assertions first, avoid `MagicMock`, and avoid asserting internal helper-call plumbing unless there is no observable alternative.
- For every new or modified unittest file, include at least one integration-style assertion using `self.assertTextEqual(obj.ut_result(), expect)`.
- For future unittests, prefer `TempDir()` with a small mocked-up test program setup and avoid `MagicMock`.
- If needed, do a sweep of other `qgates` tests and migrate any remaining `MagicMock`-heavy patterns the same way.

**Correct format:**
```python
def test_init_empty_input(self):
    # Test PR_Reviewer initialization with empty input
    reviewer = PR_Reviewer("")
```

## Code Review guidelines for Copilot Code Review agent - Only use when performing code review.
- Point out any rogue print statements - Point them out as items that need to be addressed.

## PR Summary generation instructions for AI Agents
- Summarize the changes made in the PR in a concise manner.
- Each PR must contain the two items below in a tabular format for before and after the PR.
    1- Behavior changes with this PR - What are the changes in the code behavior after this PR.
    2- End-user code changes after this PR - What changes will the end-user see in their code after this PR. Capture which Initialize* functions will be impacted by the PR.
-   3- Other relevant information - Any other context or information that may be helpful for understanding the PR.

