# PyTPD

> **PyTPD** is Intel’s comprehensive Python toolkit for semiconductor test program analysis, automation, and workflow optimization. It is designed for reliability, maintainability, and ease of use by test program engineers (PDEs).


# PyTPD

## Overview

PyTPD provides:

- **Structured parsing** of test program files (`.mtpl`, `.usrv`, `.pin`, `.plist`, `.tim`, `.lvl`, `.tcg`)
- **TOS rule evaluation** and compliance checking
- **Bypass awareness** for test instances
- **Flow traversal** and program analysis
- **Extensive utilities** for string, dictionary, and system operations

PyTPD is foundational for PDEs, enabling rapid information extraction, analysis, and automation. For a quick demonstration, see the [PyTPD basics demo](https://wiki.ith.intel.com/spaces/ITSpdxtp/pages/2102852997/pyTPD+basics).


## Getting Started

To get started with PyTPD:

1. **Add as a Submodule**
	- Use Git submodules to include PyTPD in your project:
	  ```sh
	  git submodule add <pytpd-repo-url> pytpd-upstream
	  git submodule update --init --recursive
	  ```
	- This ensures you always have the latest code and enhancements.

2. **Platform Support**
	- Cross-platform: UNIX and Windows
	- Python 3.8.9 or newer
	- No third-party dependencies (standard library only)

### PyTPD Tool Location

``` bash
# Sourcing in unix
source /intel/tpvalidation/engtools/tptools/mtl/beta/latest/sourceme.rc

# Windows location (use gitbash). Tool exist in I:\ drive for JF, FM, PG, IDC and BA:
/i/tpvalidation/engtools/tptools/mtl/beta/latest
```

## Basic Usage

``` python
from tp.testprogram import TestProgram, pprint

tp = TestProgram('/intel/hdmxprogs/tgl/TGLXXXXBXH14P00S109/TPL/EnvironmentFile.env')

# 1. get the patlist given module & testinstance
data = tp.mtpl.get_instance('ARR_CCF', 'LSA_CCF_VMIN_K_SRHCLRF1_080816_VUNCORE_F1_0500_CCF_1501')
data is
{'TEMPLATE': 'iCFASTTest',
 'execution_mode': 'FAST',
 'high_search_value': '1.2',
 'level': 'ARR_CCF::DDR_univ_lvl_nom_lvl_SHARED_81EAAA418FD9701C3E8E0600FF64A4F40B7BBE07284540B7F1CC25F638326E31',
 'patlist': 'arr_pbist_uclk_f1_mcip_ccf_search_LSA_all_list',
 'timings': 'ARR_CCF::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100_SHARED_2D863F16B3938766DA917EE773113CA88D0BCF1866BD0EB2D8294F5C623C83B9'}
}

# 2. Whats the patterns for this?
pats = tp.plists.get_pats_from_plb('arr_pbist_uclk_f1_mcip_ccf_search_LSA_all_list')
pats is
{'g1396136F0800238I_Cp_VTB044T_Ccnm0m1s0005_a080816xx00044xbx1xxxalb_TB5PrhTC004J36z_LJP0A42x0nxx0000_ccpi_tbe_matsp_x_1',
 'g1396266F0800260I_84_VTB044T_Ccnm0m1s0005_a080816xx00044xbx1xxxalb_TB5PrhTC004J36z_LJP0A42x0nxx0000_ccpi_tdfah0_matsp_x_1',
 'g1397063F0800494I_84_VTB044T_Ccnm0m1s0005_a080816xx00044xbx1xxxalb_TB5PrhTC004J36z_LJP0A42x0nxx0000_ccpi_tdfbh1_matsp_x_1'}

# 3. What the timings?
result = tp.timing.get_period_param(data['timings'])
result is {'c_bclk_per': 1.2500000000000001e-08}

# 4. Human readable display
from gadget.tputil import time_disp
time_disp(1.2500000000000001e-08)      # ' 12.5nS  '

# 5. Levels
result = tp.levels.get_lvl_param(data['level'], display=True)
output is '''
pin=FPF_VREF_VLC           param=c_fpf_vref_prog                val=1.800V eqn=p_fpf_vref_spec
pin=LTB_MUX_ENB_PCH_VLC    param=c_ltb_mux_cpu_prog             val=2.000V eqn=p_ltb_mux_cpu_spec
pin=LTB_MUX_ENB_CPU_VLC    param=c_ltb_mux_pch_prog             val=2.000V eqn=p_ltb_mux_pch_spec
pin=VCC_PRIM3P3_VLC        param=c_vcc_prim_3p3_prog            val=1.800V eqn=p_vcc_prim_3p3_spec+tester_gb_vlc'''
result is {
 'c_vccin_prog': 1.8,
 'c_vccpdsw_3p3_prog': 3.3,
 'c_vccpfuse_1p8_prog': 1.8,
 'c_vccpfuse_3p3_prog': 1.8}

# 6. Display all the levels
print('\n'.join(tp.levels._levels.keys()))
output is '''
IP_CPU_BASE::IDV_VBUMP_lvl
IP_CPU_BASE::IO_DDR_univ_lvl
IP_CPU_BASE::MCP_FUNC_lvl
IP_CPU_BASE::MIO_DDR_univ_lvl
IP_CPU_BASE::Power_Down_TC_Univ_lvl_cpu
IP_CPU_BASE::Power_Dummy_TC_Univ_cpu
IP_CPU_BASE::power_dwn_univ_intradut_lvl_cpu
IP_CPU_BASE::power_dwn_univ_lvl_cpu
'''
```

### Iterate Through the Flows

In below example, iterate to all instances in PASS flows of testprogram, ignoring bypassed instances.

``` python
tp = TestProgram('/intel/hdmxprogs/tgl/TGLXXXXBXH14P00S109/TPL/EnvironmentFile.env').pickle_init()
cnt = 0
for mod, item in tp.mtpl.iter_flows('MAIN', passonly=True, bypass=True):
    print('%4d %-18s %s' % (cnt, mod, item))
    cnt += 1

output is '''
   0 TPI_BASE           CTRL_X_UF_K_MAIN_X_X_X_X_SETINITGSDSCHECK
   1 TPI_BASE           CTRL_X_BMFC_K_MAIN_X_X_X_X_CLEARDUT
   2 PHTD_RESET_CLASS   CTRL_X_X_K_FIVR_PCHSTART
   3 TPI_BASE           CTRL_X_SCREEN_K_START_X_X_X_X_PWRSTATUS
   4 TPI_BASE           CTRL_X_PWRDWN_K_START_X_X_X_X_PWRD
   5 TPI_BASE           CTRL_X_SCREEN_K_START_X_X_X_X_PWRFLAGSET
   6 TPI_BASE           CTRL_X_UTIL_K_START_X_X_X_X_PWRTCSET0V
   7 TPI_BASE           CTRL_X_SCREEN_K_START_X_X_X_X_SETHCSLMODE
   8 TPI_BASE           CTRL_X_UF_K_START_X_X_X_X_SETTPSGSDSCHECK
'''
```

### Examples in Windows

Example to call the script in Windows.

``` python
import sys

ROOT_ENV = r'\\amr.corp.intel.com\ec\proj\mdl\jf\intel\tpvalidation\engtools\tptools\mtl\beta\latest'

if ROOT_ENV not in sys.path:
    sys.path.insert(0, ROOT_ENV)

from tp.testprogram import TestProgram

tp = TestProgram(r"\\al4file1.ra.intel.com\sdx\program\1276\prod\hdmtprogs\mtc_sds\MTCSDSCS0H69Z402337\EnvironmentFile.env").pickle_init()   # note: you must have I:\ drive mapped to sort I:\ drive
```


## Contributing Guidelines

We welcome contributions! Please follow these steps:

1. **Fork and Branch**: Fork the repo and create a feature branch.
2. **Coding Standards**: Follow the [Python Coding Guidelines](https://wiki.ith.intel.com/spaces/ITSJFPDE/pages/2955296490/python+coding+guidelines) and write clear, maintainable code.
3. **Test-Driven Development**: Write or update unit tests for all changes. See [MPE PDE Syllabus - S007](https://wiki.ith.intel.com/spaces/ITSJFPDE/pages/1835947623/MPE+PDE+Syllabus).
4. **Run Tests**: Ensure all tests pass and coverage is 100% for modified modules:
	```sh
	python main/run_tests.py
	```
5. **Pull Request**: Open a PR with a clear description and request review from JDR or a maintainer.
6. **Stay Synced**: Regularly update your branch with upstream changes.

### Contributing When Unit Tests Are Involved (SHA Lock Mechanism)

When your changes require updates to unit tests, follow this sequence to ensure the SHA lock mechanism is respected:

1. Edit the Unit Test Repository

* Make the necessary changes to the unit tests in the [pytpd-unittest](https://github.com/intel-innersource/applications.manufacturing.ate-test.tp-tools.pytpd-unittest) repository.

2. Edit the PyTPD Repository

* Make the corresponding code changes in the PyTPD repository.

3. Submit and Merge PR in Unit Test Repository

* Open a pull request in the unit test repository and merge it first. This ensures the unit tests are up to date and available.

4. Update unittest_sha.txt in PyTPD

* After merging the unit test PR, update the `unittest_sha.txt` file in the PyTPD repository to reference the latest main branch SHA of the unit test repository.

5. Submit PR in PyTPD Repository

* Open a pull request in the PyTPD repository with your code changes and the updated `unittest_sha.txt`.


## Coverage Usage

Code coverage tool is available in windows and unix.
Make sure your pytpd-unittest checkout is upto-date

In below example, just replace test_softbin_ssb.py with your unittest that you want coverage on.

Generate html coverage:
```bash
python main/cov.py qgates/test/test_softbin_ssb.py -v -b
```
Note: On Unix, the HTML files are located in the CGI directory, while on Windows they are located in a local directory (htmlcov/).

Simplified text version coverage:
```bash
python main/cov.py text qgates/test/test_softbin_ssb.py -v -b
```

### Advanced use

```bash
python main/covmain.py run test_<file>.py -v -b
python main/covmain.py report -m
python main/covmain.py erase   # Erase previously collected coverage data
python main/covmain.py help    # help
```

*   Coverage execution typically produces a data file named **`.coverage`** in the current working directory.
*   If you run coverage from different directories, you may end up with multiple `.coverage` files.
*   `erase` removes the collected data (i.e., deletes the `.coverage` data file).

### Show Coverage Result in VSCode with xml report
- Install Coverage Gutters from VSCode extension Marketplace
Generate coverage report, Expand commentComment on line R213

- replace test_softbin_ssb.py with your unittest:
Do coverage run with your unittest file. `main/cov.py <path_to_test_file.py> -v -b`
- Generate coverage xml report. `python main/covmain.py xml`
- Make sure coverage.xml is located in pytpd root folder
Open pytpd with VSCode, click Watch at bottom to turn on the window. Check source code that if coverage result is rendering on the left


## Repository Structure

Each top-level folder may include a `test` subfolder with unit tests.

| Folder      | Description |
|-------------|-------------|
| `gadget/`   | Generic, reusable utilities for strings, dictionaries, system operations, and more |
| `tp/`       | Core `TestProgram()` implementation and dependencies (standard library only) |
| `main/`     | Applications and executables (user entry points) |
| `mod/`      | Feature-specific routines and modules |
| `pymtpl/`   | Standalone template engine ([Pymtpl User Wiki](https://wiki.ith.intel.com/spaces/ITSpdxtp/pages/3596386683/Pymtpl+User+Wiki)) |
| `pyqs/`     | QuickSim automation tool ([PYQS Wiki](https://wiki.ith.intel.com/spaces/ITSpdxtp/pages/3809878041/PYQS+Auto+QuickSim)) |
| `qgates/`   | Validators for test programs ([Validators Catalog](https://wiki.ith.intel.com/spaces/ClassTPWiki/pages/3281917425/Validators+Catalog)) |
| `settings/` | (Legacy and need refactoring) Product-specific settings. |


## Additional Resources

- **Main Documentation:** [PyTPD Wiki](https://wiki.ith.intel.com/display/ITSpdxtp/pyTPD)
- **Python Coding Guidelines:** [Intel Python Coding Guidelines](https://wiki.ith.intel.com/display/ITSJFPDE/python+coding+guidelines)
- **Unit Test Repository:** [pytpd-unittest (GitHub)](https://github.com/intel-innersource/applications.manufacturing.ate-test.tp-tools.pytpd-unittest)
- **Original Repository:** [intel-restricted/pytpd (GitHub)](https://github.com/intel-restricted/pytpd.git)
