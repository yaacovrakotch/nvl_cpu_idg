"""
mtpl to py generator

"""
from gadget.vepargs import Args, TA_StoreTrue, TA_All, TA_AppendSC
from gadget.gizmo import Elapsed
from gadget.pylog import log
from gadget.errors import confirm, ErrorUser, ErrorInput, Check
from gadget.files import File
from gadget.disk import mkdirs
from gadget.helperclass import OPT
from gadget.strmore import sha1, to_list
from gadget.dictmore import reverse_keyval
from os.path import isdir, dirname, exists
from importlib.machinery import SourceFileLoader
from itertools import chain
from functools import partial
import re
import os
from pathlib import Path
import json
from tp.testprogram import Env
from tp.testprogram import TestProgram


"""
Psuedo code -

1) Inout path to mtpl
2) Extract the module name/module dir and get env file from there.
3) Iterate over all the Fitems for each flow according to the "ORDER" key so that we preserve the order of tests.
4) For each Fitem, extract the test and mtt params.
5) Write the test method
6) Write the fitem/port info
"""


class BaseDefault:
    """Base class for defaults
    Important: All attributes in this class should be lower case so that -set_defaults can work properly
    """

    initialize = 'Initialize'
    autosetbins = False
    autosetcounters = False
    autogeneratestandardports = False
    importbinlimits = False
    omit_binrange_params = False
    tos = 4
    use_first_two_digits_for_hardbin = False  # used in conjunction with autosetbins for sort-style binning with HBSBxxxx

    @classmethod
    def trialtesttype(cls):
        """Returns the trial test type based on TOS version"""
        return 'TrialTest' if cls.tos == 3 else 'CSharpTrialTest'

    @classmethod
    def mtttemplate(cls):
        """Returns the MTT template type based on TOS version"""
        return 'MultiTrial' if cls.tos == 3 else 'NativeMultiTrial'


class CWFClassDefault(BaseDefault):
    """Class for CWFspecific defaults"""

    initialize = 'InitializeCWFClass'
    autosetbins = True
    autosetcounters = True
    autogeneratestandardports = True
    importbinlimits = True
    omit_binrange_params = False
    tos = 3


class DMRClassDefault(BaseDefault):
    """Class for DMR specific defaults"""

    initialize = 'InitializeDMRClass'
    autosetbins = True
    autosetcounters = True
    autogeneratestandardports = True
    importbinlimits = True
    omit_binrange_params = False
    tos = 4


class JGSClassDefault(BaseDefault):
    """Class for JGS (Jaguar Shores) specific defaults"""

    initialize = 'InitializeJGSClass'
    autosetbins = True
    autosetcounters = True
    autogeneratestandardports = True
    importbinlimits = True
    omit_binrange_params = False
    tos = 4
    use_first_two_digits_for_hardbin = True


class CBRClassDefault(BaseDefault):
    """Class for CBR specific defaults"""

    initialize = 'InitializeCBRClass'
    autosetbins = True
    autosetcounters = True
    autogeneratestandardports = True
    importbinlimits = True
    omit_binrange_params = False
    tos = 4


class TestChipDefault(BaseDefault):
    """Configuration for Test Chip MTPL to Python conversion.

    Simplified defaults for Test Chip: converts bins to -HB format, removes explicit counters,
    omits binrange parameters, and uses HBSBXXXX-style format (first two digits for hardbin).

    :cvar initialize: Initialize function name ('InitializeTestChip')
    :cvar importbinlimits: Skip importing bin limits from JSON (False)
    :cvar omit_binrange_params: Omit binrange from Initialize call (True)
    """

    initialize = 'InitializeTestChip'
    autosetbins = True
    autosetcounters = True
    autogeneratestandardports = True
    importbinlimits = False
    omit_binrange_params = True
    tos = 4
    use_first_two_digits_for_hardbin = True


class NVLClassDefault(BaseDefault):
    """Class for NVL specific defaults"""

    initialize = 'InitializeNVLClass'
    autosetbins = False
    autosetcounters = False
    autogeneratestandardports = False
    importbinlimits = False
    omit_binrange_params = False
    tos = 4


class GenPy:
    def __init__(self, mtplfile):
        self.mtplfile = mtplfile
        # Extract TP Dir from input mtpl file.
        # Mtpls are usually 3 folders deep in the TP dir structure.
        # TODO : Change this so that when we run it in the TP Repo, we pass in the Env file directly.
        tpdir = mtplfile
        for _ in range(3):
            tpdir = os.path.dirname(tpdir)
        self.tpdir = tpdir
        if OPT.env:
            # If user specified env file in the input variable, use that
            self.envfile = OPT.env
        else:
            self.envfile = Env.get_envfile(self.tpdir)
        self.defaults = BaseDefault
        if OPT.product and OPT.product.lower() == 'dmrclass':
            self.defaults = DMRClassDefault
        if OPT.product and OPT.product.lower() == 'cwfclass':
            self.defaults = CWFClassDefault
        if OPT.product and OPT.product.lower() == 'cbrclass':
            self.defaults = CBRClassDefault
        if OPT.product and OPT.product.lower() == 'jgsclass':
            self.defaults = JGSClassDefault
        if OPT.product and OPT.product.lower() == 'testchip':
            self.defaults = TestChipDefault
        if OPT.product and OPT.product.lower() == 'nvlclass':
            self.defaults = NVLClassDefault
        if OPT.set_defaults:
            overrides = {}
            valid_keys = sorted(k for k in dir(self.defaults) if not k.startswith('_') and not callable(getattr(self.defaults, k)))
            for key, val in OPT.set_defaults.items():
                if key not in valid_keys:
                    raise ErrorUser(f'-set_defaults key "{key}" is not a recognized defaults attribute.',
                                    f'Valid keys are: {valid_keys}')
                existing = getattr(self.defaults, key)
                if isinstance(existing, bool):
                    if not isinstance(val, str) or val.lower() not in ('true', 'false'):
                        raise ErrorUser(f'-set_defaults value for "{key}" must be "true" or "false", got {type(val).__name__}.',
                                        f'Use -set_defaults {key}=true or -set_defaults {key}=false')
                    val = val.lower() == 'true'
                elif isinstance(existing, int):
                    try:
                        val = int(val)
                    except (ValueError, TypeError):
                        raise ErrorUser(f'-set_defaults value for "{key}" must be an integer, got "{val}".',
                                        f'Use -set_defaults {key}=<integer>')
                overrides[key] = val
            self.defaults = type(self.defaults.__name__, (self.defaults,), overrides)
        self.tpobj = TestProgram(self.envfile)
        self.moduledir = os.path.dirname(mtplfile)
        self.outputpyfilepath = mtplfile.strip(".mtpl")
        self.testtemplates = set()

    def main(self):
        """Main Entry point to write the output"""

        # Call the function that helps generate the dataframe with all the dutflow info
        self.get_dutflow_dict_and_modulename()
        self.get_sourcefile_path()
        all_lines = []
        initialize_lines = []
        flow_lines = []
        import_lines = []
        uservars_lines = []
        flow_lines.extend(self.write_flow_items())
        initialize_lines.extend(self.write_initialize_line())
        import_lines.extend(self.write_import_lines())
        uservars_lines.extend(self.write_uservars_lines())
        all_lines = chain(initialize_lines, import_lines, uservars_lines, flow_lines)

        if not File(self.sourcefile).rewrite('\n'.join(all_lines), 'Mtpl2Py.main(mtpl)'):
            log.info(f'-i- NO UPDATE: No changes were detected so {self.sourcefile} was not updated')

    def get_sourcefile_path(self):
        confirm('.mtpl' in self.mtplfile, f"Input file {self.mtplfile} is not an .mtpl file", "Please provide an .mtpl file")
        self.sourcefile = self.mtplfile.replace('.mtpl', '.py')

    def get_dutflow_dict_and_modulename(self):
        """Function that returns a dictionary containing all the DUTFlow Item info"""
        self.tpobj.mtpl.read_mtpl_specific([self.mtplfile], True)
        self.df = self.tpobj.mtpl.get_dutflow_map()
        # Get EDC Kill dict
        self.df_edckill = self.tpobj.mtpl.get_dutflow_map(at=True)
        # Get the name of the module
        fname2mod = reverse_keyval(self.tpobj.mtpl.get_mod2fname())
        self.modulename = fname2mod[self.mtplfile]
        # Get comment dictionary for ##EDC## bins
        self.commentdict, self.eoldict = self.tpobj.mtpl.read_dutflow_comments(self.mtplfile)
        # Extract UserVars from .usrv files
        self.extract_uservars_from_usrv_files()
        # Identify and collect all tests in INIT flows
        self.init_flow_tests = self._collect_init_flow_tests()

    def _identify_init_flows(self):
        """Identify all flows with @INIT dtag.

        :return: Set of flow names that have @INIT dtag
        :rtype: set
        """
        init_flows = set()
        for flow_key in self.df.keys():
            # Check if this flow has @INIT dtag
            if (flow_key, None) in self.df_edckill:
                dtag_val = self.df_edckill[(flow_key, None)]
                if dtag_val == '@INIT':
                    init_flows.add(flow_key)
        return init_flows

    def _get_flow_data(self, flow_name):
        """Get flow data for a flow given its name.

        Handles cases where flow_name might be just the flow name or include :: prefix.

        :param flow_name: The flow name (may or may not include :: prefix)
        :type flow_name: str
        :return: The flow data dict, or None if not found
        :rtype: dict or None
        """
        # First try exact match
        if flow_name in self.df:
            return self.df[flow_name]

        # Adding module name to flow name to get full key name
        key = f"{self.modulename}::{flow_name}"
        confirm(key in self.df, f"Flow {flow_name} not found in module {self.modulename}", "Please check the MTPL structure")
        return self.df[key]

    def _collect_init_flow_tests(self):
        """Collect all test names in INIT flows and their nested child flows.

        Recursively traverses INIT flows and any composite flows (child flows) within them
        to build a complete set of all tests that should have no bins/counters.

        :return: Set of test names that are in INIT flows or nested child flows
        :rtype: set
        """
        init_flows = self._identify_init_flows()
        init_tests = set()

        def collect_tests_from_flow(flow_name):
            """Recursively collect tests from a flow and its child flows."""
            flow_data = self._get_flow_data(flow_name)
            confirm(flow_data is not None, f"Flow data for {flow_name} not found", "Please check the MTPL structure")
            for fitemname in flow_data.get('_ORDER', []):
                # Add this test to the set
                init_tests.add(fitemname)
                flowablename = flow_data[fitemname].get(999)

                # Check if this is a composite (child flow)
                try:
                    testmethod_info = self.tpobj.mtpl.get_instance(self.modulename, fitemname, evaluated=False, mtt=False)
                    mtt_info = self.tpobj.mtpl.get_instance(self.modulename, fitemname, evaluated=False, mtt=True)
                except AssertionError:
                    # Assertion error is when it is not a test method which means it is a composite.
                    # This is a composite, recursively collect tests from child flow
                    collect_tests_from_flow(flowablename)

        # Collect tests from all INIT flows
        for init_flow in init_flows:
            collect_tests_from_flow(init_flow)

        return init_tests

    def extract_uservars_from_usrv_files(self):
        """Function that extracts UserVars from .usrv files in the same directory as the MTPL.

        Finds all .usrv files in the same directory as the MTPL file, parses UserVars blocks
        from each file, and stores them in a structured format for later conversion to pymtpl
        UserVars objects.

        :return: None (stores results in self.uservars_data)
        """

        self.uservars_data = []

        # Get the directory containing the MTPL file
        mtpl_dir = os.path.dirname(self.mtplfile)
        confirm(isdir(mtpl_dir), f"Directory {mtpl_dir} does not exist or is not a directory", "Please provide a valid MTPL file path")

        # Find all .usrv files in the same directory
        usrv_files = [f for f in os.listdir(mtpl_dir) if f.endswith('.usrv')]

        # Parse each .usrv file
        for usrv_filename in usrv_files:
            usrv_path = os.path.join(mtpl_dir, usrv_filename)
            self._parse_usrv_file(usrv_path)

    def _parse_usrv_file(self, usrv_filepath):
        """Parse a single .usrv file and extract UserVars.

        :param usrv_filepath: Path to the .usrv file
        :return: None (appends to self.uservars_data)
        :throws: if file cannot be read
        """
        usrv_content = File(usrv_filepath).read()

        # Find all UserVars blocks using regex
        # Pattern: UserVars <setname> { <variables> }
        uservars_pattern = r'UserVars\s+(\w+)\s*\{([^}]+)\}'
        uservars_matches = re.findall(uservars_pattern, usrv_content, re.DOTALL)

        for setname, block_content in uservars_matches:
            # Parse individual variables within the block
            # Pattern: <type> <name> = <value>;
            # Type can be: Integer, Double, String, Boolean, Array<Type>
            var_pattern = r'(Array<\w+>|\w+)\s+(\w+)\s*=\s*([^;]+);'
            var_matches = re.findall(var_pattern, block_content)

            variables = []
            for var_type, var_name, var_value in var_matches:
                # Clean up whitespace
                var_value = var_value.strip()
                # remove all spaces
                var_value = re.sub(r'\s+', '', var_value)

                # Determine if this is an array type
                is_array = var_type.startswith('Array<')
                if is_array:
                    # Extract base type from Array<Type>
                    base_type = re.search(r'Array<(\w+)>', var_type).group(1)
                else:
                    base_type = var_type

                # Determine if value needs Spec wrapper
                needs_spec = self._detect_if_needs_spec(base_type, var_value, is_array)

                variables.append({
                    'type': base_type,
                    'name': var_name,
                    'value': var_value,
                    'is_array': is_array,
                    'needs_spec': needs_spec
                })

            if variables:  # Only store if there are variables
                self.uservars_data.append({
                    'setname': setname,
                    'variables': variables,
                    'source_file': os.path.basename(usrv_filepath)
                })

    def _detect_if_needs_spec(self, base_type, var_value, is_array):
        """Detect if a uservar value needs to be wrapped in Spec().

        Guidelines from requirements:
        - If the uservar has any special variable in it (usually denoted by USERVARSET.VARNAME)
        - If there are no quotes in what looks like a string

        :param base_type: Base type of the variable (Integer, Double, String, Boolean)
        :param var_value: Value string from MTPL
        :param is_array: Whether this is an array variable
        :return: True if needs Spec wrapper, False otherwise
        """

        # For arrays
        if is_array:
            # If value doesn't start with [, it's an expression
            if not var_value.startswith('['):
                return True
            # Check if array content has module references (expressions)
            # Look for patterns like "Module.Var" (letters on both sides of dot) or "Function()"
            # But NOT floating point numbers like "1.1" (digits on both sides)
            if re.search(r'[a-zA-Z_]\w*\.[a-zA-Z_]\w*|\w+\(', var_value):
                return True
            # Array literals without expressions don't need spec
            return False

        # For String type - check this BEFORE module reference check
        if base_type == 'String':
            # If not in quotes, it needs Spec
            if not (var_value.startswith('"') and var_value.endswith('"')):
                return True
            # Quoted strings don't need Spec, even if they contain dots
            return False

        # For numeric and boolean types - check literals BEFORE module references
        if base_type in ('Integer', 'Double'):
            # Check if it's a literal number (handles both integers and floats)
            # Pattern: optional minus, digits, optional (decimal point followed by at least one digit)
            if re.match(r'^-?\d+(?:\.\d+)?$', var_value):
                return False
            # Otherwise it's an expression (fall through to module reference check)

        if base_type == 'Boolean':
            # Check if it's a literal boolean
            if var_value in ('True', 'False', 'true', 'false'):
                return False
            # Otherwise it's an expression (fall through to module reference check)

        # Check for module/uservar references (pattern: Word.Word) or function calls
        if ('.' in var_value and re.search(r'[a-zA-Z_]\w*\.[a-zA-Z_]\w*', var_value)) or '(' in var_value:
            return True

        # For non-literals that aren't module refs or function calls, assume expression
        # This handles cases like arithmetic expressions without module refs (e.g., "10 + 20")
        if base_type in ('Integer', 'Double', 'Boolean'):
            # If we get here for numeric/boolean types, it's an unrecognized expression
            return True

        # Default: no spec needed (should not reach here for well-formed input)
        return False

    def write_initialize_line(self):
        """Function that writes the initialize line back to the .py file"""
        testtemplate_import_string = ', '.join(sorted(self.testtemplates))

        yield f"from pymtpl.por_methods import {testtemplate_import_string}"

        # Check if we have uservars to add UserVars import
        has_uservars = hasattr(self, 'uservars_data') and self.uservars_data
        if has_uservars:
            yield f"from pymtpl.core import Flow, Fitem, pPass, pFail, {self.defaults.initialize}, {self.defaults.mtttemplate()}, AUTO, Import, TrialParamSpec, Spec"
            yield f"from pymtpl.uservars import UserVars"
        else:
            yield f"from pymtpl.core import Flow, Fitem, pPass, pFail, {self.defaults.initialize}, {self.defaults.mtttemplate()}, AUTO, Import, TrialParamSpec, Spec"

        # If the user has specified to import bin limits, we import them here.
        bin_limits_string = ''
        if not self.defaults.omit_binrange_params:
            if self.defaults.importbinlimits:
                yield "from pymtpl.helpers import get_bin_limits_from_json\n"
                yield f"# Importing bin limits from json file for {self.modulename}"
                yield f"bin_limits = get_bin_limits_from_json('{self.modulename}')"
                bin_limits_string = f", binrange=bin_limits, edcportctrbinrange=bin_limits"

        yield f"\n{self.defaults.initialize}('Test_{self.modulename}', '{self.modulename}'{bin_limits_string})\n"

    def write_import_lines(self):
        """Function that writes the import lines to the mtpl file.
            Users import uservars, tcg files etc and also testtemplates not being used
            This function helps import those into the .py file"""
        testtemplates = self.testtemplates
        # self.tpobj.mtpl._import is a dict with key = module name and values = List of all the import statements in the mtpl
        count_imports = 0
        for importitemraw in self.tpobj.mtpl._import[self.modulename]:
            importitemraw = importitemraw.replace(";", "")
            importitemraw = importitemraw.replace("Import ", "")
            importitemraw = importitemraw.replace("\"", "")
            importitemraw = importitemraw.replace("\'", "")
            # Switching to importitem from importitemraw to carry forward .xml in the import name
            importitem = importitemraw.replace(".xml", "")
            if importitem not in testtemplates:
                yield f"Import('{importitemraw}')"
                count_imports += 1
        if count_imports > 0:
            yield ""  # adds extra new line if there are imports

    def write_uservars_lines(self):
        """Function that generates UserVars Python code from parsed MTPL uservars.

        Generates pymtpl UserVars objects with proper variable assignments.
        Handles different types (Integer, Double, String, Boolean, Arrays) and
        detects when to use Spec() wrapper for expressions.

        :return: Generator yielding lines of Python code
        """
        if not hasattr(self, 'uservars_data') or not self.uservars_data:
            return  # No uservars to write

        yield from self.write_section_header('UserVars')

        for uservars_set in self.uservars_data:
            setname = uservars_set['setname']
            variables = uservars_set['variables']

            # Generate UserVars instance
            # Check if setname matches module name (default case)
            if setname == self.modulename:
                var_name_prefix = 'usrv'
                yield f"usrv = UserVars('{setname}')"
            else:
                # Sanitize setname for use as Python variable name
                # Replace non-identifier characters with underscore
                safe_setname = re.sub(r'[^a-zA-Z0-9_]', '_', setname)
                # Ensure it doesn't start with a digit
                if safe_setname[0].isdigit():
                    safe_setname = 'usrv_' + safe_setname
                var_name_prefix = f'usrv_{safe_setname}'
                yield f"{var_name_prefix} = UserVars('{self.modulename}', setname='{setname}')"

            # Generate variable assignments
            for var in variables:
                var_name = var['name']
                var_value = var['value']
                var_type = var['type']
                is_array = var['is_array']
                needs_spec = var['needs_spec']

                # Determine the Python type for Spec tuple syntax
                python_type_map = {
                    'Integer': 'int',
                    'Double': 'float',
                    'String': 'str',
                    'Boolean': 'bool'
                }
                python_type = python_type_map.get(var_type, 'str')

                # Use the variable name prefix we defined earlier
                if needs_spec:
                    # Value needs Spec wrapper (expression)
                    if is_array:
                        # Array Spec: ("expression", [type])
                        yield f"{var_name_prefix}.{var_name} = ('{var_value}', [{python_type}])"
                    else:
                        # Regular Spec: ("expression", type)
                        yield f"{var_name_prefix}.{var_name} = ('{var_value}', {python_type})"
                else:
                    # Literal value - no Spec needed
                    if is_array:
                        # Array literal
                        yield f"{var_name_prefix}.{var_name} = {var_value}"
                    elif var_type == 'String':
                        # String literal - already has quotes
                        yield f"{var_name_prefix}.{var_name} = {var_value}"
                    elif var_type == 'Boolean':
                        # Boolean literal - capitalize for Python
                        py_bool = var_value.capitalize()
                        yield f"{var_name_prefix}.{var_name} = {py_bool}"
                    else:
                        # Numeric literal
                        yield f"{var_name_prefix}.{var_name} = {var_value}"
        yield from self.write_section_footer('UserVars')

    def get_bin(self, setbinstring, ismtt=False):
        """Helps extract the SetBin value when given a setbin string"""
        if ismtt:
            # TODO: Add support for 8 digit bin definitions on MTT tests.
            pattern = r"\b\d{4}"
        else:
            pattern = r"b(\d{8})"
        matches = re.findall(pattern, setbinstring)
        setbin = matches[0]
        if self.defaults.autosetbins and not ismtt:
            if self.defaults.use_first_two_digits_for_hardbin:
                # Extract hardbin from first two digits (positions 1-2)
                hardbin = re.findall(r"b(\d{2})", setbinstring)[0]
            else:
                # Extract hardbin from second two digits (positions 3-4)
                hardbin = re.findall(r"b\d{2}(\d{2})", setbinstring)[0]
            setbin = -1 * int(hardbin)
        return int(setbin)

    def get_counter(self, counterstring, ismtt=False):

        if ismtt:
            pattern = r'"(\d{4})'
        else:
            pattern = r"[np](\d{8})"
            # Find all matches
        matches = re.findall(pattern, counterstring)
        try:
            counter = matches[0]
        except IndexError:
            raise ErrorUser(f"Please verify the validity of the counter {counterstring}",
                            f"Counters should follow the following convention - nXXXXXXXX or pXXXXXXXX")

        return int(counter)

    def get_bin_from_counter(self, setbinstring, ismtt=False):
        """Helps extract the SetBin value when given a setcounter string"""
        pattern = r"[np](\d{8})"
        matches = re.findall(pattern, setbinstring)
        setbin = matches[0]
        if self.defaults.use_first_two_digits_for_hardbin:
            # Extract hardbin from first two digits (positions 1-2)
            hardbin = re.findall(r"[np](\d{2})", setbinstring)[0]
        else:
            # Extract hardbin from second two digits (positions 3-4)
            hardbin = re.findall(r"[np]\d{2}(\d{2})", setbinstring)[0]
        setbin = -1 * int(hardbin)
        return int(setbin)

    def write_portinfo_lines(self, portdatadict, edc=False, ismtt=False, nextfitem=None):

        skip_counter = self.defaults.autosetcounters

        if ismtt:
            for port, portdata in portdatadict.items():
                # Set default values for all the BasePort arguments
                setbin = None
                counter = None
                ret_string = None
                goto_string = None

                if port != 999:
                    if port < 0:
                        port = str(port).replace('-', 'm')
                    for k, v in portdata.items():
                        if "SetBin" in k:
                            setbin = self.get_bin(v, ismtt=True)
                        if "Return" in k:
                            ret_string = v
                        if "GoTo" in k:
                            goto_string = v
                        if "TrialAction" in k:
                            trial_action = v
                        if "Counter" in k and not skip_counter:
                            counter = self.get_counter(v, ismtt=True)

                    # determine which params to write
                    params = []
                    if ret_string is not None:
                        params.append(f'ret={ret_string.strip()}')
                    if self._is_init_flow_test:
                        params.append('setbin=None')
                    elif setbin is not None:
                        params.append(f'setbin={setbin}')
                    if self._is_init_flow_test:
                        params.append('ctr=0')
                    elif counter is not None:
                        params.append(f'ctr={counter}')
                    if goto_string is not None and ret_string is None:  # port cannot have both GoTo and Ret together.
                        params.append(f"goto='{goto_string}'")

                    # always append trialaction
                    if trial_action not in ['"Exit"', '"Next"']:  # if trial_action is a basic literal
                        params.append(f"trialaction=Spec('{trial_action}')")
                    else:
                        params.append(f"trialaction={trial_action}")

                    # write the params
                    yield from self.write_port_line(port, portdata['PassFail'], params, tabs=2)
        else:  # Not MTT
            for port, portdata in portdatadict.items():
                # Set default values for all the BasePort arguments
                setbin = None
                counter = None
                ret_string = None
                goto_string = None

                if port != 999:
                    if port < 0:
                        port = str(port).replace('-', 'm')
                    for k, v in portdata.items():
                        if "SetBin" in k:
                            setbin = self.get_bin(v)
                        if "Counter" in k and not skip_counter:
                            counter = self.get_counter(v)
                        if "Counter" in k and skip_counter and setbin is None and portdata['PassFail'] == 'Pass':
                            # this means we need to use the counter as a setbin, for a pass port
                            setbin = self.get_bin_from_counter(v)
                        if "Return" in k:
                            ret_string = v
                        if "GoTo" in k:
                            goto_string = v
                            if (nextfitem and goto_string == nextfitem):
                                goto_string = 'NEXT'

                    # AutoGenerate Standard Ports: If ports are going where we expect, we do not generate a port for it.
                    # autogeneratestandardports overrides autosetbins/autosetcounters for standard ports.
                    # BUT: For INIT flow tests, we must write ALL ports explicitly
                    if not self._is_init_flow_test and self.defaults.autogeneratestandardports and port in ['m2', 'm1', 1]:
                        # If port is 1 and going where we expect, we do not generate a port for it.
                        if (port == 1 and portdata['PassFail'] == 'Pass' and setbin is None and
                            (
                                (goto_string == 'NEXT' and ret_string is None) or  # we're in a sequence and we're just going to the next item
                                (ret_string == '1' and goto_string is None and nextfitem is None)  # we're at the end of a sequence and just need to return 1
                        )
                        ):
                            continue
                        # If port is -1 or -2 is the standard fail port, don't generate it
                        if (port == 'm1' and goto_string is None and portdata['PassFail'] == 'Fail' and ret_string == '-1'):
                            continue
                        if (port == 'm2' and goto_string is None and portdata['PassFail'] == 'Fail' and ret_string == '-2'):
                            continue

                    # determine which params to write
                    params = []
                    if ret_string is not None:
                        if not self._is_init_flow_test:
                            if portdata['PassFail'] == 'Pass' and nextfitem is None and ret_string == '1':
                                # default return value for pass port is 1 (if nextfitem is None)
                                pass
                            elif portdata['PassFail'] == 'Fail' and edc and nextfitem is None and ret_string == '1':
                                # default return value for edc fail port is 1 (if nextfitem is None)
                                pass
                            elif portdata['PassFail'] == 'Fail' and not edc and ret_string == '0':
                                # default return value for kill fail port is 0
                                pass
                            else:
                                params.append(f'ret={ret_string}')
                        else:
                            # For INIT flow tests, always write ret
                            params.append(f'ret={ret_string}')
                    if self._is_init_flow_test:
                        params.append('setbin=None')
                    elif setbin is not None:
                        params.append(f'setbin={setbin}')
                    if self._is_init_flow_test:
                        params.append('ctr=0')
                    elif counter is not None:
                        params.append(f'ctr={counter}')
                    if goto_string is not None and ret_string is None:  # port cannot have both GoTo and Ret together.
                        if portdata['PassFail'] == 'Pass' and (nextfitem == goto_string or goto_string == 'NEXT'):
                            # default goto value for pass port is next fitem
                            pass
                        elif portdata['PassFail'] == 'Fail' and edc and (nextfitem == goto_string or goto_string == 'NEXT'):
                            # default goto value for edc fail port is next fitem
                            pass
                        else:
                            params.append(f"goto='{goto_string}'")

                    # write the params
                    yield from self.write_port_line(port, portdata['PassFail'], params)
            if not self._iscomposite:
                yield "        )"
            yield "    ),"

    def write_port_line(self, port, passFail, params, tabs=3):
        """Function that writes the port definition line to the mtpl file"""
        param_string = ', '.join(params)  # combine into one string
        yield f"{' ' * 4 * tabs}r{port}=p{passFail}({param_string}),"

    def write_testmethod_info_lines(self, fitemname):
        """Function that writes the test parameter info to pymtpl"""
        self._iscomposite = False
        self._ismtt = False
        # Set whether this test is in INIT flow
        self._is_init_flow_test = fitemname in self.init_flow_tests

        try:
            testmethod_info = self.tpobj.mtpl.get_instance(self.modulename, fitemname, evaluated=False, mtt=False)
            mtt_info = self.tpobj.mtpl.get_instance(self.modulename, fitemname, evaluated=False, mtt=True)

            if mtt_info:

                self._ismtt = True
                yield f"    {self.defaults.mtttemplate()}(name = '{fitemname}',"
                for k, v in mtt_info.items():
                    if k == "TrialVariable":
                        yield f"        trialvar = '{v.strip(';')}',"
                    if "ExitAction" in k:
                        # expecting something like "Continue" or "Restore"
                        if self.defaults.tos == 3:
                            yield f"        exitaction = Spec('{v.strip(';')}'),"
                        else:
                            yield f"        exitaction = {v.strip(';')},"

                mtt_search_pattern = r"_MTT\((.*?)\)"

                self.testtemplates.add(testmethod_info['TEMPLATE'])

                yield f"        template = {testmethod_info['TEMPLATE']}(name = '{mtt_info[self.defaults.trialtesttype()].strip(';')}',"
                for k, v in testmethod_info.items():
                    # Ensure that there are no mixed use of " and ' in the mtpl.
                    # If a user is using them interchangably, replace them with " so that it is uniform.
                    v = v.replace("'", '"')
                    if k != "TEMPLATE":
                        if "patlist" in k.lower():
                            key2use = "Patlist"
                        else:
                            key2use = k

                        # Make sure that paths are escaped properly
                        if '\\' in v:
                            v = v.replace("\\", "\\\\")

                        if "_MTT" in v:
                            trialparam = re.sub(mtt_search_pattern, lambda match: match.group(1), v)
                            # MTT params are enclosed in braces in pytpd.
                            # Below lines of code help remove the leading and trailing braces so that we do not write them to the mtpl.
                            trialparam = trialparam.lstrip('(')
                            trialparam = trialparam[:-1] if trialparam.endswith(')') else trialparam
                            trialparam = "('" + trialparam + "')"

                            yield f"            {key2use} = TrialParamSpec{trialparam},"
                        elif self.tpobj.mtpl.ttype[self.modulename][fitemname][k]:  # key is literal
                            yield f"            {key2use} = '{v}',"
                        else:
                            # if v is int or float, we want to write it as is
                            if re.search(r"^-?\d+(\.\d+)?$", v):
                                yield f"            {key2use} = {v},"
                            else:
                                yield f"            {key2use} = Spec(\'{v}\'),"
                yield "        ),"
                yield from self.write_portinfo_lines(mtt_info['TrialResult'], ismtt=True)
            else:
                self.testtemplates.add(testmethod_info['TEMPLATE'])
                yield f"    {testmethod_info['TEMPLATE']}(name = '{fitemname}',"
                for k, v in testmethod_info.items():

                    # we can't replace ' with " because users might need both for regexes

                    if k != "TEMPLATE":
                        if "patlist" in k.lower():
                            key2use = "Patlist"
                        else:
                            key2use = k

                        # Make sure that paths are escaped properly
                        if '\\' in v:
                            v = v.replace("\\", "\\\\")
                        if '\'' in v:
                            v = v.replace("\'", "\\\'")

                        if self.tpobj.mtpl.ttype[self.modulename][fitemname][k]:  # key is literal
                            yield f"        {key2use} = '{v}',"
                        else:
                            # if v is int or float, we want to write it as is
                            if re.search(r"^-?\d+(\.\d+)?$", v):
                                yield f"        {key2use} = {v},"
                            else:
                                yield f"        {key2use} = Spec(\'{v}\'),"
        except AssertionError:
            # Assertion error is when it is not a test method which means it is a composite.
            # TODO: Check with JDR: Assertion error is also raised when the test plan does not match the stpl. So we cannot put in a ErrorUser
            self._iscomposite = True

    def _get_port_info(self, setbininfo):
        identifier = None
        id_match = re.search(r'_([n]?)(\d+);', setbininfo)
        if id_match:
            prefix = id_match.group(1)
            number = id_match.group(2)

            # Process the identifier
            if prefix == 'n':
                identifier = -int(number)  # Convert to negative
            else:
                identifier = int(number)  # Keep as positive
        return identifier

    def write_section_header(self, section_name):
        """Function that writes the comment header for a section

        :param section_name: Name of the section to display in the header
        :type section_name: str
        """
        yield "##############################################################"
        yield f"# {section_name}"
        yield f"# region"
        yield "##############################################################"

    def write_section_footer(self, section_name):
        """Function that writes the comment footer for a section"""
        yield "##############################################################"
        yield f"# endregion {section_name}"
        yield "##############################################################\n"

    def write_flow_items(self):
        for Flow, Fitem in self.df.items():
            flow_name = Flow.split("::")[-1]
            dtag_string = ''
            # for DUTFlow objects, the @DTAG is stored in the df_edckill dict
            if (Flow, None) in self.df_edckill:
                dtag_val = self.df_edckill[(Flow, None)]
                dtag_val = dtag_val[1:]  # remove the @ since we're looking at the at_map
                dtag_string = f", dtag='{dtag_val}'"
            yield from self.write_section_header(flow_name)
            yield f"{flow_name} = Flow('{flow_name}', ["
            for idx in range(len(Fitem['_ORDER'])):
                fitemname = Fitem['_ORDER'][idx]
                flowablename = Fitem[fitemname][999]

                # get next flow item name if we can
                if idx == len(Fitem['_ORDER']) - 1:
                    nextfitem = None
                else:
                    nextfitem = Fitem['_ORDER'][idx + 1]

                try:
                    edc = self.df_edckill[(Flow, fitemname)] == '@EDC'
                except KeyError:
                    edc = False

                if edc:
                    # set this instance to edc
                    edcstring = 'edc=True,'
                    # figure out EDC setbins from comments
                    comment_bin_info = self.commentdict[fitemname]
                    for comment in comment_bin_info:
                        if '##EDC##' in comment:
                            clean_bininfo = comment.replace('##EDC##', '').strip()
                            port = self._get_port_info(clean_bininfo)
                            if port is not None and 'SetBin' not in Fitem[fitemname][port]:
                                Fitem[fitemname][port]['SetBin'] = clean_bininfo

                else:
                    edcstring = ''

                # Write the test method info lines
                if fitemname == flowablename:
                    yield from self.write_testmethod_info_lines(fitemname)
                else:
                    yield from self.write_testmethod_info_lines(flowablename)

                if not self._iscomposite:
                    if fitemname == flowablename:
                        # If flow item name and test name are the same
                        yield f"        _fitem = Fitem({edcstring}"
                    else:
                        # If Flow item is different from test name
                        yield f"        _fitem = Fitem('{fitemname}', {edcstring}"
                else:  # Composite
                    if fitemname == flowablename:
                        # If flow item name and test name are the same
                        yield f"    Fitem('SAME', {fitemname}, {edcstring}"
                    else:
                        # If Flow item is different from test name
                        yield f"    Fitem('{fitemname}', '{flowablename}', {edcstring}"

                # Set current fitemname for write_portinfo_lines to access
                self._current_fitemname = fitemname
                yield from self.write_portinfo_lines(Fitem[fitemname], edc=edc, nextfitem=nextfitem)

            yield f"]{dtag_string})"
            yield from self.write_section_footer(flow_name)
