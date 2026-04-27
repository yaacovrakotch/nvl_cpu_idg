#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
import os
import re
import xml.etree.ElementTree as ET
import datetime
from gadget.errors import confirm
from gadget.helperclass import IS_UT
import subprocess
import time
import json
from gadget.pylog import log
import platform


class TorchExtractTestMethodInfo:
    """
    This class decompiles a DLL using a C# tool and extracts test method information.
    """
    # csharp tool path - supports both Windows and Unix
    @staticmethod
    def get_csharp_tools_path():
        """
        Returns the appropriate csharp tools path based on the operating system.

        Windows: UNC path \\amr\\ec\\...
        Unix/Linux: Converted path using //amr/ec/... pattern, then to /intel/...
        """
        confirm(platform.system() == 'Windows', "gen_methods is only supported on Windows systems.", "Please call this tool from Windows")
        return r'\\amr\ec\proj\mdl\jf\intel\tpvalidation\engtools\tptools\mtl\tools\pytpd-csharp-tools\latest\pytpd-csharp-tools.exe'

    def __init__(self):
        self.csharp_tools_path = self.get_csharp_tools_path()

    def decompile_dll_to_json(self, dll_paths):
        """
        Runs the C# tool and parses its output as JSON.
        Returns the parsed JSON object if successful, else raises an exception.
        """
        cmd = [self.csharp_tools_path, 'extract']
        cmd.extend(dll_paths)

        confirm(os.path.exists(self.csharp_tools_path), f"Cannot access dll extractor at {self.csharp_tools_path}", "Ensure you have access to the AMR network share.")

        for dll_path in dll_paths:
            log.info(f"-I- DLL Path exists: {os.path.exists(dll_path)}: {dll_path}")

        log.info(f'-I- Running Command: {" ".join(cmd)}')

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"C# tool failed with exit code {result.returncode}: {result.stderr}")
        json_object = None
        try:
            json_object = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON output: {e}\nOutput: {result.stdout}")

        return json_object


class ExtractTestMethodInfo:
    """
    This class is used to extract test method information from decompiled C# files.
    It generates a dictionary containing parameters and their optionality.
    """

    def __init__(self, dll_json):
        self.dll_json = dll_json
        self.testmethodparaminfo = {}  # Changed from list to dictionary

    def extract_all_testmethod_class_info(self):
        """Extracts test method class information from the provided JSON data."""
        # the json is a list of templates
        for value in self.dll_json:
            # skip if not instantiable
            if not value['IsInstantiable']:
                continue
            # get class name, but only take \w characters
            class_name = re.sub(r'\W+', '', value['TemplateName'])
            self.testmethodparaminfo[class_name] = {
                "Parameters": {},
            }
            for param in value['Parameters']:
                self.testmethodparaminfo[class_name]["Parameters"][param['Name']] = {
                    "Required": not param['IsOptional']
                }
                if param.get('Description'):
                    self.testmethodparaminfo[class_name]["Parameters"][param['Name']]['Description'] = param.get('Description')
                if param.get('DefaultValue'):
                    self.testmethodparaminfo[class_name]["Parameters"][param['Name']]['DefaultValue'] = param.get('DefaultValue')
                if param.get('TestProgramType'):
                    self.testmethodparaminfo[class_name]["Parameters"][param['Name']]['Type'] = param.get('TestProgramType')
                if param.get('PossibleValues'):
                    self.testmethodparaminfo[class_name]["Parameters"][param['Name']]['PossibleValues'] = param.get('PossibleValues')

    def get_header_string(self):
        # Get current timestamp
        datetime_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        gen_path = os.path.abspath(__file__).replace("\\", "\\\\")
        header_string = f'''"""
Document title : TestMethod Classes definition file
Summary: This document contains the testmethod information necessary for pymtpl to generate an mtpl output.
Date Generated: {datetime_string}
Generated from: {gen_path}
Tool used: pytpd-csharp-tools.exe extract
"""
from pymtpl.core import BaseMethod
from pymtpl.core import required, optional\n
            '''
        return header_string

    def get_params_comment(self, class_data, param_names, indent=4):
        """Iterator to create a docstring for method parameters."""
        indentation = ' ' * indent
        yield indentation + '"""'
        yield indentation + 'Args:'
        # Write each parameter
        for param_name in param_names:
            param_data = class_data["Parameters"][param_name]

            # Determine if parameter is required or optional
            is_required = param_data.get("Required", False)
            optional_string = "Required" if is_required else "Optional"

            # Get description
            description_string = param_data.get("Description", "No description found").replace('\n', ' ').replace('\r', '').replace('\t', ' ')
            # ensure description_string starts with an uppercase letter and ends with a period
            if description_string and not description_string[0].isupper():
                description_string = description_string[0].upper() + description_string[1:]
            if description_string and not description_string.endswith('.'):
                description_string += '.'

            # Get Type
            type_string = param_data.get("Type", "unknown")
            # concat possible values, if present
            possible_values = param_data.get("PossibleValues", [])
            possible_values_string = ''
            if possible_values:
                possible_values_string += f' Options: {", ".join(possible_values)}.'

            # Get Default value - Assign Not Found if not present
            default_value = param_data.get("DefaultValue", "None").replace('\n', ' ').replace('\r', '').replace('\t', ' ')

            yield f'{indentation}    {param_name} ({optional_string} {type_string}): {description_string} Default: {default_value}.{possible_values_string}'
        yield f'{indentation}"""'

    def generate_methods_py(self, output_path):
        """Generate a methods.py file from the resolved classes."""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        filename = os.path.join(output_path, "new_test_methods.py")

        with open(filename, 'w', encoding='utf-8') as outfile:
            # Write header
            outfile.write(self.get_header_string())

            # Define class template
            class_def_string = '''
# Beginning of %s class definition
class %s(BaseMethod):
    def __init__(self,
                 name,
'''

            # Sort class names alphabetically
            sorted_class_names = sorted(self.testmethodparaminfo.keys())

            # Process each class
            for class_name in sorted_class_names:
                class_data = self.testmethodparaminfo[class_name]
                # Skip classes with empty Parameters dictionary
                if not class_data["Parameters"]:
                    continue
                outfile.write(class_def_string % (class_name, class_name))

                # Get all parameter names
                param_names = sorted([k for k in class_data["Parameters"].keys()])

                # Write each parameter
                for param_name in param_names:
                    param_data = class_data["Parameters"][param_name]

                    # Determine if parameter is required or optional
                    is_required = param_data.get("Required", False)
                    optional_string = "required" if is_required else "optional"

                    outfile.write(f'                 {param_name}={optional_string},\n')

                # Add standard parameters
                outfile.write(f'                 _comment=None,\n')
                outfile.write(f'                 _fitem=None,\n')
                # outfile.write(f'                 **kwargs\n') - Uncomment this line if you want to support params not part of por methods.
                outfile.write(f'                 ):\n')
                # Write parameter docstring
                for line in self.get_params_comment(class_data, param_names, indent=8):
                    outfile.write(line + '\n')
                outfile.write(f'        self._init(name, locals())\n')
                outfile.write(f'# End of {class_name} class definition\n')
                outfile.write('\n')

            log.info(f'-I- Methods file generated: {os.path.abspath(output_path)}')


class GenMethods:
    def __init__(self, pymtplfilepath, dll_paths):
        """
        Accepts an ordered list of DLL paths
        No env file or TestProgram logic is used.
        """
        self.pymtplfilepath = pymtplfilepath
        self.dll_paths = dll_paths
        # Set a default tpdir for output if needed
        self.tpdir = os.path.dirname(os.path.abspath(pymtplfilepath))

    def main(self, outdir=None):
        """
        Main method to process DLLs and extract test method information for tos4.
        Args:
            outdir (str): Directory to output the generated methods.py file. If None, a default location is used.
        """
        if outdir is None:
            outdir = os.path.join(self.tpdir, "pymtpl_generated")
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        log.info(f"-I- Output directory for generated files: {outdir}")

        torch_extract = TorchExtractTestMethodInfo()
        dll_parsed_json = torch_extract.decompile_dll_to_json(self.dll_paths)

        test_info_obj = ExtractTestMethodInfo(dll_parsed_json)
        test_info_obj.extract_all_testmethod_class_info()
        test_info_obj.generate_methods_py(outdir)
        log.info(f"-I- Successfully generated method definitions in {outdir}")
        return outdir
