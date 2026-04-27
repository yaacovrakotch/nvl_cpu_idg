---
applyTo: "**/pymtpl/*.py"
---

# Pymtpl Overview

## What is Pymtpl?

Pymtpl is a Python-based test template engine for generating MTPL (Manufacturing Test Plan Language) files used in semiconductor ATE (Automatic Test Equipment) testing. It provides a programmatic way to create and manage test programs for Intel's manufacturing test infrastructure.

## Design Philosophy

### 1. Object-Oriented Architecture with Class Isolation

Pymtpl uses a **class-based architecture** where different products and test strategies are isolated into their own classes:

- **Product-Specific Binning Strategies**: Each product has its own binning class (e.g., `NVLClass8dig`, `DMRClass8dig`, `Sort8dig`, `ServerClass8dig`)
- **Product-Specific Counter Strategies**: Each product has its own counter class (e.g., `CtrNVLClass8dig`, `CtrDMRClass8dig`, `CtrSort8dig`)
- **Product-Specific Defaults**: Each product has its own default configuration class (e.g., `NVLdefault`, `DMRdefault`, `MTLdefault`, `CBRdefault`, `Sortdefault`)

**Critical Principle - Backward Compatibility**: Changes made to one product class (e.g., NVL) **must NOT impact** other product classes (e.g., DMR, MTL, Server). This isolation ensures:
- Legacy test programs continue to work without modification
- New features can be added to specific products without breaking others
- Product teams can evolve their strategies independently

**Inheritance Guidelines**: When using inheritance between classes:
- Subclasses should only override methods that need product-specific behavior
- Avoid modifying parent class behavior that affects other products
- Test thoroughly to ensure changes don't propagate unexpectedly

### 2. Leverage Gadget Utilities

**Always prefer using `gadget` helpers** when implementing new features or fixing issues. The `gadget` library provides battle-tested utilities that maintain consistency across the codebase:

- **`gadget.pylog.log`**: For all logging operations (info, warning, error, debug)
- **`gadget.errors`**: For error handling and validation (`confirm`, `ErrorUser`, `ErrorInput`, `Check`)
- **`gadget.files.File`**: For file read/write operations
- **`gadget.disk.mkdirs`**: For directory creation
- **`gadget.strmore`**: For string utilities (e.g., `sha1`, `to_list`)
- **`gadget.dictmore.DictDot`**: For dictionary operations
- **`gadget.shell.SystemCall`**: For shell command execution
- **`gadget.helperclass`**: For helper utilities (`OPT`, `IS_UT`, `NoneLikeClass`, `is_none`)

Using gadget utilities ensures:
- Consistent error messages and logging formats
- Robust error handling across the codebase
- Easier maintenance and debugging
- Proven reliability from extensive production use

### 3. Strategy Pattern for Product Variants

Pymtpl uses the **Strategy Pattern** to provide different behaviors for different products. Each `Initialize*` function binds specific strategies using Python's `functools.partial`:

```python
# Example: NVL Class uses its own strategies
InitializeNVLClass = partial(Initialize, 
    defaults=NVLdefault, 
    nonmttbinstrategy=NVLClass8dig, 
    mttbinstrategy=MTTNVLClass8dig, 
    nonmttctrstrategy=CtrNVLClass8dig, 
    mttctrstrategy=MTTCtrNVLClass8dig, 
    tosversion="tos4")

# Example: DMR Class uses different strategies
InitializeDMRClass = partial(Initialize, 
    defaults=DMRdefault, 
    nonmttbinstrategy=DMRClass8dig, 
    mttbinstrategy=MTTBinSSB, 
    nonmttctrstrategy=CtrDMRClass8dig, 
    mttctrstrategy=MTTCtrHBSB, 
    tosversion="tos4")
```

This enables:
- Product-specific binning and counter behaviors without modifying core logic
- Easy addition of new product strategies
- Clear separation between products
- Explicit configuration at initialization time

### 4. Registry Pattern for Central Management

Several core classes maintain **global registries** for centralized access and lifecycle management:

- **`Flow.get_registry()`**: Maintains all Flow objects in the current module
- **`Import.get_import_registry()`**: Tracks all import statements needed
- **`MConfig.get_import_registry()`**: Tracks MConfig declarations

Benefits:
- Ensures uniqueness of flow names within a module
- Enables centralized validation and processing
- Simplifies iteration over all flows during MTPL generation
- Provides clean lifecycle management (cleared on each `Initialize.clear_all()`)

### 5. Separation of Concerns

Each file in pymtpl has a **clear, focused responsibility**:

- **`core.py`**: Core classes (Flow, Fitem, BaseMethod, Initialize) and workflow orchestration
- **`binctr.py`**: All binning and counter strategies, isolated by product class
- **`helpers.py`**: Utility functions and helper classes for common operations
- **`mtpl2py.py`**: Reverse engineering (converts MTPL files back to Python)
- **`gen_methods.py`**: Test method generation utilities
- **`autobinctrupdate.py`**: Auto-update bin and counter JSON files

When making changes:
- Keep binning/counter logic in `binctr.py`
- Keep flow/fitem/port logic in `core.py`
- Keep utility functions in `helpers.py`
- Avoid cross-file dependencies where possible

## Key Concepts

### Test Program Structure
- **Flow**: A sequence of test instances organized together (DUTFlow in MTPL)
- **Fitem** (Flow Item): A wrapper around a test instance or composite flow with port definitions
- **Test Instance** (BaseMethod): An individual test method with parameters
- **Ports**: Result handling for test instances (r0, r1, r2, etc., and rm1, rm2 for negative ports)

### Port Types
- **pPass()**: Defines behavior for passing ports
- **pFail()**: Defines behavior for failing ports
- Port parameters: `setbin`, `ctr`, `ret`, `goto`, `trialaction`

### Test Types
- **Normal Tests**: Single execution tests
- **MTT (MultiTrialTest)**: Tests that execute across multiple trial variables
- **Composites**: Flows used as sub-flows within other flows

## File Structure

The main files in pymtpl are:

1. **core.py**: Core classes (Flow, Fitem, BaseMethod, Initialize, etc.)
2. **binctr.py**: Bin and counter management strategies
3. **mtpl2py.py**: MTPL to Python converter (reverse engineering)
4. **helpers.py**: Utility functions and helper classes
5. **gen_methods.py**: Test method generation utilities
6. **autobinctrupdate.py**: Auto-update bin and counter JSON files

## Common Workflow

1. **Initialize** the module with output path and configuration
2. **Define test methods** using BaseMethod subclasses
3. **Create Fitems** with test instances and port definitions
4. **Build Flows** by grouping Fitems together
5. **Run PyMtpl.main()** to generate MTPL file

## Example Basic Structure

```python
from pymtpl.core import Initialize, Flow, Fitem, pPass, pFail
from pymtpl.por_methods import SomeTestMethod

# Initialize module
Initialize('output_path', 'ModuleName', binrange=[(4400, 4500)])

# Create test instance
test1 = SomeTestMethod(name='Test1', Patlist='pattern.plist')

# Create flow items with ports
flow_items = [
    Fitem(test1._fitem, r0=pFail(setbin=-44, ret=0), r1=pPass(goto='NEXT'))
]

# Create flow
Flow('MAIN', flow_items)
```

## TOS Versions

Pymtpl supports two TOS (Test Operating System) versions:
- **TOS3**: Legacy format
- **TOS4**: Current format with different syntax (e.g., CSharp tests)

Set version in Initialize: `Initialize(..., tosversion='tos4')`

## Product-Specific Configurations

Different products have specialized Initialize functions:
- **InitializeMTL**: For MTL products
- **InitializeNVLClass**: For NVL Class testing
- **InitializeNVLSort**: For NVL Sort testing
- **InitializeDMRClass**: For DMR Class testing
- **InitializeCBRClass**: For CBR Class testing (AN TPI team)

Each has product-specific default behaviors for binning, counters, and port handling.

## Auto-Features

### Auto-Binning
Use `setbin=AUTO` or `setbin=-HB` to automatically assign bins based on hardbin ranges.

### Auto-Counters
Counters are automatically generated when `ctr=None` and `setbinstring` exists.

### Auto-Basenumbering
Use negative basenumber values to auto-assign from defined ranges.

## Key Design Patterns

1. **Registry Pattern**: Flow, Import, and MConfig classes maintain registries
2. **Strategy Pattern**: Different binning/counter strategies for different products
3. **Builder Pattern**: Flows are built up from Fitems
4. **Template Pattern**: BaseMethod provides template for test methods

## Common Issues to Avoid

1. **Name Collisions**: Flow item names must be unique within a flow
2. **Port Definitions**: Missing required ports (especially rm1, rm2)
3. **Bin Range Exhaustion**: Define adequate bin ranges
4. **Counter Uniqueness**: Manual counters must be unique
5. **Initialize Before Use**: Always call Initialize() before creating Fitems

## Additional Resources

See individual documentation files for detailed information:
- `core.instructions.md`: Core classes and concepts
- `binctr.instructions.md`: Binning and counter strategies
- `mtpl2py.instructions.md`: MTPL to Python conversion
- `helpers.instructions.md`: Helper functions and utilities
