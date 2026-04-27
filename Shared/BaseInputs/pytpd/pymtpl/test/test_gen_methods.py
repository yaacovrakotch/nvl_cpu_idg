#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
unitest for methods
"""
from setenv_unittest import UT_DIR, ROOT_ENV    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option, Mock
from gadget.gizmo import MockVar, with_
from gadget.helperclass import CaptureStdoutLog
from gadget.files import TempDir, File
from gadget.dictmore import keys_atlevel
from gadget.errors import ErrorUser, ErrorCockpit
from gadget.shell import CALLERBIN
from pymtpl.gen_methods import *
from unittest.mock import patch, MagicMock
from main.pymtpl import PyMtplArgs
from tp.testprogram import Env
import sys
import os
from pprint import pprint


class TestExtractTestMethodInfo(TestCase):
    @patch('pymtpl.gen_methods.datetime')
    @patch('pymtpl.gen_methods.__file__', '/path/to/gen_methods.py')
    def test_get_header_string(self, mock_datetime):
        """Test get_header_string with mocked datetime and __file__"""
        # Mock datetime.now() to return a fixed datetime
        mock_now = Mock()
        mock_now.strftime.return_value = '2025-10-08 12:34:56'
        mock_datetime.datetime.now.return_value = mock_now

        obj = ExtractTestMethodInfo(dll_json={})
        header = obj.get_header_string()

        gen_methods_path = os.path.abspath('/path/to/gen_methods.py').replace("\\", "\\\\")
        # Verify the header contains expected content
        expect = f'''"""
Document title : TestMethod Classes definition file
Summary: This document contains the testmethod information necessary for pymtpl to generate an mtpl output.
Date Generated: 2025-10-08 12:34:56
Generated from: {gen_methods_path}
Tool used: pytpd-csharp-tools.exe extract
"""
from pymtpl.core import BaseMethod
from pymtpl.core import required, optional

        '''
        self.assertTextEqual(header, expect)

        # Verify datetime.now().strftime was called with correct format
        mock_now.strftime.assert_called_once_with("%Y-%m-%d %H:%M:%S")

    def test_extract_all_testmethod_class_info_instantiable_required_param(self):
        """Test extract with instantiable template and required parameter"""
        dll_json = [
            {
                'IsInstantiable': True,
                'TemplateName': 'MyTestClass',
                'Parameters': [
                    {
                        'Name': 'Param1',
                        'IsOptional': False
                    }
                ]
            }
        ]
        obj = ExtractTestMethodInfo(dll_json=dll_json)
        obj.extract_all_testmethod_class_info()

        # Verify the extracted info
        self.assertIn('MyTestClass', obj.testmethodparaminfo)
        self.assertIn('Param1', obj.testmethodparaminfo['MyTestClass']['Parameters'])
        self.assertTrue(obj.testmethodparaminfo['MyTestClass']['Parameters']['Param1']['Required'])

    def test_extract_all_testmethod_class_info_non_instantiable_skipped(self):
        """Test extract skips non-instantiable templates"""
        dll_json = [
            {
                'IsInstantiable': False,
                'TemplateName': 'NonInstantiableClass',
                'Parameters': [
                    {
                        'Name': 'Param1',
                        'IsOptional': False
                    }
                ]
            }
        ]
        obj = ExtractTestMethodInfo(dll_json=dll_json)
        obj.extract_all_testmethod_class_info()

        # Verify non-instantiable class was skipped
        self.assertNotIn('NonInstantiableClass', obj.testmethodparaminfo)
        self.assertEqual(len(obj.testmethodparaminfo), 0)

    def test_extract_all_testmethod_class_info_optional_param(self):
        """Test extract with optional parameter (IsOptional=True)"""
        dll_json = [
            {
                'IsInstantiable': True,
                'TemplateName': 'MyTestClass',
                'Parameters': [
                    {
                        'Name': 'OptionalParam',
                        'IsOptional': True
                    }
                ]
            }
        ]
        obj = ExtractTestMethodInfo(dll_json=dll_json)
        obj.extract_all_testmethod_class_info()

        # Verify Required is False for optional parameter
        self.assertFalse(obj.testmethodparaminfo['MyTestClass']['Parameters']['OptionalParam']['Required'])

    def test_extract_all_testmethod_class_info_param_with_description(self):
        """Test extract with parameter that has Description field"""
        dll_json = [
            {
                'IsInstantiable': True,
                'TemplateName': 'MyTestClass',
                'Parameters': [
                    {
                        'Name': 'Param1',
                        'IsOptional': False,
                        'Description': 'This is a test parameter'
                    }
                ]
            }
        ]
        obj = ExtractTestMethodInfo(dll_json=dll_json)
        obj.extract_all_testmethod_class_info()

        # Verify Description was extracted
        self.assertIn('Description', obj.testmethodparaminfo['MyTestClass']['Parameters']['Param1'])
        self.assertEqual(obj.testmethodparaminfo['MyTestClass']['Parameters']['Param1']['Description'],
                         'This is a test parameter')

    def test_extract_all_testmethod_class_info_param_without_description(self):
        """Test extract with parameter that has no Description field"""
        dll_json = [
            {
                'IsInstantiable': True,
                'TemplateName': 'MyTestClass',
                'Parameters': [
                    {
                        'Name': 'Param1',
                        'IsOptional': False
                    }
                ]
            }
        ]
        obj = ExtractTestMethodInfo(dll_json=dll_json)
        obj.extract_all_testmethod_class_info()

        # Verify Description was not added to dict
        self.assertNotIn('Description', obj.testmethodparaminfo['MyTestClass']['Parameters']['Param1'])

    def test_extract_all_testmethod_class_info_param_with_default_value(self):
        """Test extract with parameter that has DefaultValue field"""
        dll_json = [
            {
                'IsInstantiable': True,
                'TemplateName': 'MyTestClass',
                'Parameters': [
                    {
                        'Name': 'Param1',
                        'IsOptional': True,
                        'DefaultValue': '42'
                    }
                ]
            }
        ]
        obj = ExtractTestMethodInfo(dll_json=dll_json)
        obj.extract_all_testmethod_class_info()

        # Verify DefaultValue was extracted
        self.assertIn('DefaultValue', obj.testmethodparaminfo['MyTestClass']['Parameters']['Param1'])
        self.assertEqual(obj.testmethodparaminfo['MyTestClass']['Parameters']['Param1']['DefaultValue'], '42')

    def test_extract_all_testmethod_class_info_param_without_default_value(self):
        """Test extract with parameter that has no DefaultValue field"""
        dll_json = [
            {
                'IsInstantiable': True,
                'TemplateName': 'MyTestClass',
                'Parameters': [
                    {
                        'Name': 'Param1',
                        'IsOptional': False
                    }
                ]
            }
        ]
        obj = ExtractTestMethodInfo(dll_json=dll_json)
        obj.extract_all_testmethod_class_info()

        # Verify DefaultValue was not added to dict
        self.assertNotIn('DefaultValue', obj.testmethodparaminfo['MyTestClass']['Parameters']['Param1'])

    def test_extract_all_testmethod_class_info_template_name_regex_cleanup(self):
        """Test extract with TemplateName containing non-word characters"""
        dll_json = [
            {
                'IsInstantiable': True,
                'TemplateName': 'My-Test.Class_123!@#',
                'Parameters': [
                    {
                        'Name': 'Param1',
                        'IsOptional': False
                    }
                ]
            }
        ]
        obj = ExtractTestMethodInfo(dll_json=dll_json)
        obj.extract_all_testmethod_class_info()

        # Verify TemplateName was cleaned by regex (only word characters remain)
        self.assertIn('MyTestClass_123', obj.testmethodparaminfo)
        self.assertNotIn('My-Test.Class_123!@#', obj.testmethodparaminfo)

    def test_extract_all_testmethod_class_info_multiple_params(self):
        """Test extract with template having multiple parameters"""
        dll_json = [
            {
                'IsInstantiable': True,
                'TemplateName': 'MyTestClass',
                'Parameters': [
                    {
                        'Name': 'Param1',
                        'IsOptional': False,
                        'Description': 'First parameter'
                    },
                    {
                        'Name': 'Param2',
                        'IsOptional': True,
                        'DefaultValue': 'default_value',
                        'Description': 'Second parameter'
                    },
                    {
                        'Name': 'Param3',
                        'IsOptional': False
                    }
                ]
            }
        ]
        obj = ExtractTestMethodInfo(dll_json=dll_json)
        obj.extract_all_testmethod_class_info()

        # Verify all parameters were extracted
        params = obj.testmethodparaminfo['MyTestClass']['Parameters']
        self.assertEqual(len(params), 3)
        self.assertIn('Param1', params)
        self.assertIn('Param2', params)
        self.assertIn('Param3', params)

        # Verify Param1 details
        self.assertTrue(params['Param1']['Required'])
        self.assertEqual(params['Param1']['Description'], 'First parameter')
        self.assertNotIn('DefaultValue', params['Param1'])

        # Verify Param2 details
        self.assertFalse(params['Param2']['Required'])
        self.assertEqual(params['Param2']['Description'], 'Second parameter')
        self.assertEqual(params['Param2']['DefaultValue'], 'default_value')

        # Verify Param3 details
        self.assertTrue(params['Param3']['Required'])
        self.assertNotIn('Description', params['Param3'])
        self.assertNotIn('DefaultValue', params['Param3'])

    def test_extract_all_testmethod_class_info_empty_dll_json(self):
        """Test extract with empty dll_json"""
        dll_json = []
        obj = ExtractTestMethodInfo(dll_json=dll_json)
        obj.extract_all_testmethod_class_info()

        # Verify testmethodparaminfo is empty
        self.assertEqual(len(obj.testmethodparaminfo), 0)

    def test_extract_all_testmethod_class_info_multiple_templates(self):
        """Test extract with multiple template classes"""
        dll_json = [
            {
                'IsInstantiable': True,
                'TemplateName': 'ClassA',
                'Parameters': [
                    {
                        'Name': 'ParamA',
                        'IsOptional': False
                    }
                ]
            },
            {
                'IsInstantiable': True,
                'TemplateName': 'ClassB',
                'Parameters': [
                    {
                        'Name': 'ParamB',
                        'IsOptional': True,
                        'Description': 'Parameter B description'
                    }
                ]
            },
            {
                'IsInstantiable': False,
                'TemplateName': 'ClassC',
                'Parameters': []
            }
        ]
        obj = ExtractTestMethodInfo(dll_json=dll_json)
        obj.extract_all_testmethod_class_info()

        # Verify only instantiable classes were extracted
        self.assertEqual(len(obj.testmethodparaminfo), 2)
        self.assertIn('ClassA', obj.testmethodparaminfo)
        self.assertIn('ClassB', obj.testmethodparaminfo)
        self.assertNotIn('ClassC', obj.testmethodparaminfo)

        # Verify ClassA details
        self.assertTrue(obj.testmethodparaminfo['ClassA']['Parameters']['ParamA']['Required'])

        # Verify ClassB details
        self.assertFalse(obj.testmethodparaminfo['ClassB']['Parameters']['ParamB']['Required'])
        self.assertEqual(obj.testmethodparaminfo['ClassB']['Parameters']['ParamB']['Description'],
                         'Parameter B description')

    def test_extract_all_testmethod_class_info_param_with_type(self):
        # Test extract with parameter that has TestProgramType field
        dll_json = [
            {
                'IsInstantiable': True,
                'TemplateName': 'MyTestClass',
                'Parameters': [
                    {
                        'Name': 'Param1',
                        'IsOptional': True,
                        'TestProgramType': 'String'
                    }
                ]
            }
        ]
        obj = ExtractTestMethodInfo(dll_json=dll_json)
        obj.extract_all_testmethod_class_info()

        # Verify Type was extracted
        self.assertIn('Type', obj.testmethodparaminfo['MyTestClass']['Parameters']['Param1'])
        self.assertEqual(obj.testmethodparaminfo['MyTestClass']['Parameters']['Param1']['Type'], 'String')

    def test_extract_all_testmethod_class_info_param_with_possible_values(self):
        # Test extract with parameter that has PossibleValues field
        dll_json = [
            {
                'IsInstantiable': True,
                'TemplateName': 'MyTestClass',
                'Parameters': [
                    {
                        'Name': 'DataLog',
                        'IsOptional': True,
                        'TestProgramType': 'String',
                        'DefaultValue': 'ENABLED',
                        'PossibleValues': ['DISABLED', 'ENABLED']
                    }
                ]
            }
        ]
        obj = ExtractTestMethodInfo(dll_json=dll_json)
        obj.extract_all_testmethod_class_info()

        # Verify PossibleValues was extracted
        param = obj.testmethodparaminfo['MyTestClass']['Parameters']['DataLog']
        self.assertIn('PossibleValues', param)
        self.assertEqual(param['PossibleValues'], ['DISABLED', 'ENABLED'])
        self.assertEqual(param['Type'], 'String')
        self.assertEqual(param['DefaultValue'], 'ENABLED')

    def test_extract_all_testmethod_class_info_param_without_type(self):
        # Test extract with parameter that has no TestProgramType field
        dll_json = [
            {
                'IsInstantiable': True,
                'TemplateName': 'MyTestClass',
                'Parameters': [
                    {
                        'Name': 'Param1',
                        'IsOptional': False
                    }
                ]
            }
        ]
        obj = ExtractTestMethodInfo(dll_json=dll_json)
        obj.extract_all_testmethod_class_info()

        # Verify Type was not added to dict
        self.assertNotIn('Type', obj.testmethodparaminfo['MyTestClass']['Parameters']['Param1'])

    @patch('pymtpl.gen_methods.ExtractTestMethodInfo.get_header_string', Mock(return_value=''))
    def test_write_output_with_options(self):
        # Test write_output with parameter that has PossibleValues (Options)
        obj = ExtractTestMethodInfo(dll_json={})
        test_dict = {
            'TestClass': {
                'Parameters': {
                    'DataLog': {
                        'Required': False,
                        'Type': 'String',
                        'Description': 'No description found',
                        'DefaultValue': 'ENABLED',
                        'PossibleValues': ['DISABLED', 'ENABLED']
                    }
                }
            }
        }
        obj.testmethodparaminfo = test_dict
        with TempDir(name=True, chdir=True) as tdir:
            obj.generate_methods_py(tdir)
            expect = f'''
# Beginning of TestClass class definition
class TestClass(BaseMethod):
    def __init__(self,
                 name,
                 DataLog=optional,
                 _comment=None,
                 _fitem=None,
                 ):
        """
        Args:
            DataLog (Optional String): No description found. Default: ENABLED. Options: DISABLED, ENABLED.
        """
        self._init(name, locals())
# End of TestClass class definition

'''
            self.assertTextEqual(File(os.path.join(tdir, 'new_test_methods.py')).read(), expect)

    @patch('pymtpl.gen_methods.ExtractTestMethodInfo.get_header_string', Mock(return_value=''))
    def test_write_output_required_with_type(self):
        # Test write_output with required parameter with Type field
        obj = ExtractTestMethodInfo(dll_json={})
        test_dict = {
            'TestClass': {
                'Parameters': {
                    'RequiredParam': {
                        'Required': True,
                        'Type': 'Integer',
                        'Description': 'A required integer parameter'
                    }
                }
            }
        }
        obj.testmethodparaminfo = test_dict
        with TempDir(name=True, chdir=True) as tdir:
            obj.generate_methods_py(tdir)
            expect = f'''
# Beginning of TestClass class definition
class TestClass(BaseMethod):
    def __init__(self,
                 name,
                 RequiredParam=required,
                 _comment=None,
                 _fitem=None,
                 ):
        """
        Args:
            RequiredParam (Required Integer): A required integer parameter. Default: None.
        """
        self._init(name, locals())
# End of TestClass class definition

'''
            self.assertTextEqual(File(os.path.join(tdir, 'new_test_methods.py')).read(), expect)

    @patch('pymtpl.gen_methods.ExtractTestMethodInfo.get_header_string', Mock(return_value=''))
    def test_write_output_mixed_parameters(self):
        # Test write_output with mix of required/optional, with/without types and options
        obj = ExtractTestMethodInfo(dll_json={})
        test_dict = {
            'MixedClass': {
                'Parameters': {
                    'RequiredNoType': {
                        'Required': True,
                        'Description': 'Required parameter without type'
                    },
                    'OptionalWithType': {
                        'Required': False,
                        'Type': 'String',
                        'Description': 'Optional parameter with type',
                        'DefaultValue': 'test'
                    },
                    'OptionalWithOptions': {
                        'Required': False,
                        'Type': 'Boolean',
                        'Description': 'Optional with options',
                        'DefaultValue': 'True',
                        'PossibleValues': ['True', 'False']
                    }
                }
            }
        }
        obj.testmethodparaminfo = test_dict
        with TempDir(name=True, chdir=True) as tdir:
            obj.generate_methods_py(tdir)
            expect = f'''
# Beginning of MixedClass class definition
class MixedClass(BaseMethod):
    def __init__(self,
                 name,
                 OptionalWithOptions=optional,
                 OptionalWithType=optional,
                 RequiredNoType=required,
                 _comment=None,
                 _fitem=None,
                 ):
        """
        Args:
            OptionalWithOptions (Optional Boolean): Optional with options. Default: True. Options: True, False.
            OptionalWithType (Optional String): Optional parameter with type. Default: test.
            RequiredNoType (Required unknown): Required parameter without type. Default: None.
        """
        self._init(name, locals())
# End of MixedClass class definition

'''
            self.assertTextEqual(File(os.path.join(tdir, 'new_test_methods.py')).read(), expect)

    @patch('pymtpl.gen_methods.ExtractTestMethodInfo.get_header_string', Mock(return_value=''))
    def test_write_output(self):
        # Test write_output with new format including Type, Default, and Options
        obj = ExtractTestMethodInfo(dll_json={})
        test_dict = {
            'DTSBase': {
                'Parameters': {
                    'ConfigurationFile': {'Required': False, 'Type': 'String', 'Description': 'Gets or sets the voltage converter ActiveConfiguration file.'},
                    'BypassPort': {'Required': False, 'Type': 'Integer', 'Description': 'Port number, provided literally to bypass execution. Use nonnegative to bypass'},
                    'LogLevel': {'Required': False, 'Type': 'String', 'Description': 'Verbosity for console printing of information from code execution'},
                    'InstanceSummaryMode': {'Required': False, 'Type': 'String', 'Description': "Enable for current instance's test time and memory information"},
                    'TelemetryLevel': {'Required': False, 'Type': 'String', 'Description': 'enable for record detailed test time information'},
                    'PreInstance': {'Required': False, 'Type': 'String', 'Description': 'The pre-instance callback in the format of CALLBACKNAME(ARGS).'},
                    'PostInstance': {'Required': False, 'Type': 'String', 'Description': 'The post-instance callback in the format of CALLBACKNAME(ARGS).'}
                }
            },
            'SkipMe': {'Parameters': {}}
        }
        obj.testmethodparaminfo = test_dict
        with TempDir(name=True, chdir=True) as tdir:
            obj.generate_methods_py(tdir)
            expect = f'''
# Beginning of DTSBase class definition
class DTSBase(BaseMethod):
    def __init__(self,
                 name,
                 BypassPort=optional,
                 ConfigurationFile=optional,
                 InstanceSummaryMode=optional,
                 LogLevel=optional,
                 PostInstance=optional,
                 PreInstance=optional,
                 TelemetryLevel=optional,
                 _comment=None,
                 _fitem=None,
                 ):
        """
        Args:
            BypassPort (Optional Integer): Port number, provided literally to bypass execution. Use nonnegative to bypass. Default: None.
            ConfigurationFile (Optional String): Gets or sets the voltage converter ActiveConfiguration file. Default: None.
            InstanceSummaryMode (Optional String): Enable for current instance's test time and memory information. Default: None.
            LogLevel (Optional String): Verbosity for console printing of information from code execution. Default: None.
            PostInstance (Optional String): The post-instance callback in the format of CALLBACKNAME(ARGS). Default: None.
            PreInstance (Optional String): The pre-instance callback in the format of CALLBACKNAME(ARGS). Default: None.
            TelemetryLevel (Optional String): Enable for record detailed test time information. Default: None.
        """
        self._init(name, locals())
# End of DTSBase class definition

'''
            self.assertTextEqual(File(os.path.join(tdir, 'new_test_methods.py')).read(), expect)


class TestTorchExtractTestMethodInfo(TestCase):
    """Unit tests for TorchExtractTestMethodInfo class"""

    @patch('platform.system')
    def test_csharp_tools_path_windows_format(self, mock_platform):
        """Test that csharp_tools_path uses Windows UNC path format"""
        # Mock platform.system to return Windows
        mock_platform.return_value = 'Windows'

        obj = TorchExtractTestMethodInfo()

        # Verify the path starts with the expected Windows UNC prefix
        self.assertTrue(obj.csharp_tools_path.startswith(r'\\amr\ec\proj\mdl'),
                        f"csharp_tools_path should start with '\\\\amr\\ec\\proj\\mdl', got: {obj.csharp_tools_path}")

        # Verify it's a raw string (contains backslashes, not forward slashes for network path)
        self.assertIn(r'\ec\proj\mdl', obj.csharp_tools_path,
                      f"csharp_tools_path should contain Windows path separators")

        # Verify it ends with the executable name
        self.assertTrue(obj.csharp_tools_path.endswith('.exe'),
                        f"csharp_tools_path should end with .exe, got: {obj.csharp_tools_path}")

        # Verify platform.system was called (though not strictly necessary for this static path)
        mock_platform.assert_called()

    @patch('platform.system')
    def test_csharp_tools_path_linux_error(self, mock_platform):
        """Test that csharp_tools_path throws a UserError if not on Windows"""
        # Mock platform.system to return Linux
        mock_platform.return_value = 'Linux'

        with self.assertRaisesRegex(ErrorUser, "only supported on Windows systems."):
            TorchExtractTestMethodInfo()

        # Verify the path starts with the expected Windows UNC prefix
        mock_platform.assert_called()

    @patch('pymtpl.gen_methods.subprocess.run')
    @patch('pymtpl.gen_methods.os.path.exists')
    @patch('platform.system')
    def test_decompile_dll_to_json_success(self, mock_platform, mock_exists, mock_run):
        """Test successful DLL decompilation to JSON"""
        # Mock platform.system to return Windows
        mock_platform.return_value = 'Windows'
        # Mock os.path.exists to return True for all paths
        mock_exists.return_value = True

        # Mock subprocess.run to return successful result with JSON
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = '[{"IsInstantiable": true, "TemplateName": "TestClass", "Parameters": []}]'
        mock_result.stderr = ''
        mock_run.return_value = mock_result

        obj = TorchExtractTestMethodInfo()
        dll_paths = ['/path/to/test.dll']
        result = obj.decompile_dll_to_json(dll_paths)

        # Verify subprocess.run was called with correct arguments
        expected_cmd = [obj.csharp_tools_path, 'extract', '/path/to/test.dll']
        mock_run.assert_called_once_with(expected_cmd, capture_output=True, text=True)

        # Verify the returned JSON is correct
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0]['IsInstantiable'])
        self.assertEqual(result[0]['TemplateName'], 'TestClass')
        self.assertEqual(result[0]['Parameters'], [])

    @patch('pymtpl.gen_methods.subprocess.run')
    @patch('pymtpl.gen_methods.os.path.exists')
    @patch('platform.system')
    def test_decompile_dll_to_json_multiple_dlls(self, mock_platform, mock_exists, mock_run):
        """Test decompilation with multiple DLL paths"""
        mock_platform.return_value = 'Windows'
        mock_exists.return_value = True

        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = '[{"IsInstantiable": true, "TemplateName": "ClassA", "Parameters": []}, {"IsInstantiable": true, "TemplateName": "ClassB", "Parameters": []}]'
        mock_result.stderr = ''
        mock_run.return_value = mock_result

        obj = TorchExtractTestMethodInfo()
        dll_paths = ['/path/to/test1.dll', '/path/to/test2.dll']
        result = obj.decompile_dll_to_json(dll_paths)

        # Verify subprocess.run was called with all DLL paths
        expected_cmd = [obj.csharp_tools_path, 'extract', '/path/to/test1.dll', '/path/to/test2.dll']
        mock_run.assert_called_once_with(expected_cmd, capture_output=True, text=True)

        # Verify both classes were returned
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['TemplateName'], 'ClassA')
        self.assertEqual(result[1]['TemplateName'], 'ClassB')

    @patch('pymtpl.gen_methods.subprocess.run')
    @patch('pymtpl.gen_methods.os.path.exists')
    @patch('platform.system')
    def test_decompile_dll_to_json_csharp_tool_not_found(self, mock_platform, mock_exists, mock_run):
        """Test error when C# tool path doesn't exist"""
        mock_platform.return_value = 'Windows'
        # Mock os.path.exists to return False for csharp tool

        def exists_side_effect(path):
            return 'csharp-tools.exe' not in path
        mock_exists.side_effect = exists_side_effect

        obj = TorchExtractTestMethodInfo()
        dll_paths = ['/path/to/test.dll']

        # Verify confirm raises ErrorUser when csharp tool doesn't exist
        with self.assertRaises(ErrorUser) as context:
            obj.decompile_dll_to_json(dll_paths)

        self.assertIn('Cannot access dll extractor', str(context.exception))

    @patch('pymtpl.gen_methods.subprocess.run')
    @patch('pymtpl.gen_methods.os.path.exists')
    @patch('platform.system')
    def test_decompile_dll_to_json_subprocess_failure(self, mock_platform, mock_exists, mock_run):
        """Test error handling when subprocess returns non-zero exit code"""
        mock_platform.return_value = 'Windows'
        mock_exists.return_value = True

        # Mock subprocess.run to return failure
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ''
        mock_result.stderr = 'Error: Failed to decompile DLL'
        mock_run.return_value = mock_result

        obj = TorchExtractTestMethodInfo()
        dll_paths = ['/path/to/test.dll']

        # Verify RuntimeError is raised with proper message
        with self.assertRaises(RuntimeError) as context:
            obj.decompile_dll_to_json(dll_paths)

        self.assertIn('C# tool failed with exit code 1', str(context.exception))
        self.assertIn('Error: Failed to decompile DLL', str(context.exception))

    @patch('pymtpl.gen_methods.subprocess.run')
    @patch('pymtpl.gen_methods.os.path.exists')
    @patch('platform.system')
    def test_decompile_dll_to_json_invalid_json(self, mock_platform, mock_exists, mock_run):
        """Test error handling when subprocess returns invalid JSON"""
        mock_platform.return_value = 'Windows'
        mock_exists.return_value = True

        # Mock subprocess.run to return invalid JSON
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = 'This is not valid JSON'
        mock_result.stderr = ''
        mock_run.return_value = mock_result

        obj = TorchExtractTestMethodInfo()
        dll_paths = ['/path/to/test.dll']

        # Verify ValueError is raised with proper message
        with self.assertRaises(ValueError) as context:
            obj.decompile_dll_to_json(dll_paths)

        self.assertIn('Failed to parse JSON output', str(context.exception))
        self.assertIn('This is not valid JSON', str(context.exception))

    @patch('pymtpl.gen_methods.subprocess.run')
    @patch('pymtpl.gen_methods.os.path.exists')
    @patch('platform.system')
    def test_decompile_dll_to_json_empty_json_array(self, mock_platform, mock_exists, mock_run):
        """Test decompilation returns empty array when no classes found"""
        mock_platform.return_value = 'Windows'
        mock_exists.return_value = True

        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = '[]'
        mock_result.stderr = ''
        mock_run.return_value = mock_result

        obj = TorchExtractTestMethodInfo()
        dll_paths = ['/path/to/test.dll']
        result = obj.decompile_dll_to_json(dll_paths)

        # Verify empty array is returned
        self.assertEqual(result, [])
        self.assertEqual(len(result), 0)

    @patch('pymtpl.gen_methods.subprocess.run')
    @patch('pymtpl.gen_methods.os.path.exists')
    @patch('platform.system')
    def test_decompile_dll_to_json_complex_json(self, mock_platform, mock_exists, mock_run):
        """Test decompilation with complex JSON containing parameters"""
        mock_platform.return_value = 'Windows'
        mock_exists.return_value = True

        complex_json = '''[
            {
                "IsInstantiable": true,
                "TemplateName": "ComplexClass",
                "Parameters": [
                    {
                        "Name": "Param1",
                        "IsOptional": false,
                        "Description": "Test parameter"
                    },
                    {
                        "Name": "Param2",
                        "IsOptional": true,
                        "DefaultValue": "default",
                        "Description": "Optional param"
                    }
                ]
            }
        ]'''

        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = complex_json
        mock_result.stderr = ''
        mock_run.return_value = mock_result

        obj = TorchExtractTestMethodInfo()
        dll_paths = ['/path/to/test.dll']
        result = obj.decompile_dll_to_json(dll_paths)

        # Verify complex JSON is parsed correctly
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['TemplateName'], 'ComplexClass')
        self.assertEqual(len(result[0]['Parameters']), 2)
        self.assertEqual(result[0]['Parameters'][0]['Name'], 'Param1')
        self.assertFalse(result[0]['Parameters'][0]['IsOptional'])
        self.assertEqual(result[0]['Parameters'][1]['Name'], 'Param2')
        self.assertTrue(result[0]['Parameters'][1]['IsOptional'])
        self.assertEqual(result[0]['Parameters'][1]['DefaultValue'], 'default')


class TestGenMethods(TestCase):
    """Unit tests for GenMethods class"""

    # this integration test doesn't work on unix because it's a windows only tool
    # @with_(TempDir, startcopy=f'{UT_DIR}/sudheer_unit_test/torch_p6828_fixer_1', chdir=True)
    # def test_integration(self):
    #    output_path = '.'
    #    dll_paths = [
    #        r"Shared\BaseInputs\Supersedes\code",
    #        r'UserCode\dlls'
    #    ]
    #    cmd = f'pymtpl.py -genmethods {dll_paths} -genmethodsoutdir {output_path}'.split()
    #    with MockVar(sys, "argv", cmd):
    #        self.assertEqual(PyMtplArgs().main(), 1)
    #    self.assertGoldEqual('new_test_methods.py', f'{UT_DIR}/sudheer_unit_test/methods1.gold')

    def test_init_single_dll(self):
        """Test GenMethods initialization with single DLL path"""
        pymtpl_file = '/path/to/test.mtpl'
        dll_paths = ['/path/to/test.dll']

        obj = GenMethods(pymtpl_file, dll_paths)

        # Verify initialization
        self.assertEqual(obj.pymtplfilepath, pymtpl_file)
        self.assertEqual(obj.dll_paths, dll_paths)
        self.assertEqual(obj.tpdir, os.path.abspath('/path/to'))

    def test_init_multiple_dlls(self):
        """Test GenMethods initialization with multiple DLL paths"""
        pymtpl_file = '/path/to/project/test.mtpl'
        dll_paths = ['/path/to/dll1.dll', '/path/to/dll2.dll', '/path/to/dll3.dll']

        obj = GenMethods(pymtpl_file, dll_paths)

        # Verify initialization
        self.assertEqual(obj.pymtplfilepath, pymtpl_file)
        self.assertEqual(obj.dll_paths, dll_paths)
        self.assertEqual(len(obj.dll_paths), 3)
        self.assertEqual(obj.tpdir, os.path.abspath('/path/to/project'))

    def test_init_nested_path(self):
        """Test GenMethods initialization with nested file path"""
        pymtpl_file = '/deep/nested/path/to/project/test.mtpl'
        dll_paths = ['/path/to/test.dll']

        obj = GenMethods(pymtpl_file, dll_paths)

        # Verify tpdir is correctly extracted
        self.assertEqual(obj.tpdir, os.path.abspath('/deep/nested/path/to/project'))

    @patch('pymtpl.gen_methods.TorchExtractTestMethodInfo')
    @patch('pymtpl.gen_methods.ExtractTestMethodInfo')
    @patch('pymtpl.gen_methods.os.makedirs')
    @patch('pymtpl.gen_methods.os.path.exists')
    def test_main_default_outdir(self, mock_exists, mock_makedirs, mock_extract_class, mock_torch_class):
        """Test main method with default output directory"""
        # Setup mocks
        mock_exists.return_value = False

        # Mock TorchExtractTestMethodInfo
        mock_torch_instance = Mock()
        mock_torch_instance.decompile_dll_to_json.return_value = [
            {'IsInstantiable': True, 'TemplateName': 'TestClass', 'Parameters': []}
        ]
        mock_torch_class.return_value = mock_torch_instance

        # Mock ExtractTestMethodInfo
        mock_extract_instance = Mock()
        mock_extract_class.return_value = mock_extract_instance

        # Create GenMethods object
        pymtpl_file = '/path/to/test.mtpl'
        dll_paths = ['/path/to/test.dll']
        obj = GenMethods(pymtpl_file, dll_paths)

        # Call main without outdir
        result = obj.main()

        # Verify default outdir was used
        expected_outdir = os.path.abspath('/path/to/pymtpl_generated')
        self.assertEqual(result, expected_outdir)

        # Verify makedirs was called for default outdir
        mock_makedirs.assert_called_once_with(expected_outdir)

        # Verify TorchExtractTestMethodInfo.decompile_dll_to_json was called
        mock_torch_instance.decompile_dll_to_json.assert_called_once_with(dll_paths)

        # Verify ExtractTestMethodInfo methods were called
        mock_extract_instance.extract_all_testmethod_class_info.assert_called_once()
        mock_extract_instance.generate_methods_py.assert_called_once_with(expected_outdir)

    @patch('pymtpl.gen_methods.TorchExtractTestMethodInfo')
    @patch('pymtpl.gen_methods.ExtractTestMethodInfo')
    @patch('pymtpl.gen_methods.os.makedirs')
    @patch('pymtpl.gen_methods.os.path.exists')
    def test_main_custom_outdir(self, mock_exists, mock_makedirs, mock_extract_class, mock_torch_class):
        """Test main method with custom output directory"""
        # Setup mocks
        mock_exists.return_value = False

        # Mock TorchExtractTestMethodInfo
        mock_torch_instance = Mock()
        mock_torch_instance.decompile_dll_to_json.return_value = [
            {'IsInstantiable': True, 'TemplateName': 'TestClass', 'Parameters': []}
        ]
        mock_torch_class.return_value = mock_torch_instance

        # Mock ExtractTestMethodInfo
        mock_extract_instance = Mock()
        mock_extract_class.return_value = mock_extract_instance

        # Create GenMethods object
        pymtpl_file = '/path/to/test.mtpl'
        dll_paths = ['/path/to/test.dll']
        obj = GenMethods(pymtpl_file, dll_paths)

        # Call main with custom outdir
        custom_outdir = '/custom/output/path'
        result = obj.main(outdir=custom_outdir)

        # Verify custom outdir was used
        self.assertEqual(result, custom_outdir)

        # Verify makedirs was called for custom outdir
        mock_makedirs.assert_called_once_with(custom_outdir)

        # Verify ExtractTestMethodInfo.generate_methods_py was called with custom outdir
        mock_extract_instance.generate_methods_py.assert_called_once_with(custom_outdir)

    @patch('pymtpl.gen_methods.TorchExtractTestMethodInfo')
    @patch('pymtpl.gen_methods.ExtractTestMethodInfo')
    @patch('pymtpl.gen_methods.os.makedirs')
    @patch('pymtpl.gen_methods.os.path.exists')
    def test_main_outdir_already_exists(self, mock_exists, mock_makedirs, mock_extract_class, mock_torch_class):
        """Test main method when output directory already exists"""
        # Setup mocks - outdir exists
        mock_exists.return_value = True

        # Mock TorchExtractTestMethodInfo
        mock_torch_instance = Mock()
        mock_torch_instance.decompile_dll_to_json.return_value = []
        mock_torch_class.return_value = mock_torch_instance

        # Mock ExtractTestMethodInfo
        mock_extract_instance = Mock()
        mock_extract_class.return_value = mock_extract_instance

        # Create GenMethods object
        pymtpl_file = '/path/to/test.mtpl'
        dll_paths = ['/path/to/test.dll']
        obj = GenMethods(pymtpl_file, dll_paths)

        # Call main
        result = obj.main()

        # Verify makedirs was NOT called since directory exists
        mock_makedirs.assert_not_called()

        # Verify other methods were still called
        mock_torch_instance.decompile_dll_to_json.assert_called_once()
        mock_extract_instance.extract_all_testmethod_class_info.assert_called_once()
        mock_extract_instance.generate_methods_py.assert_called_once()

    @patch('pymtpl.gen_methods.TorchExtractTestMethodInfo')
    @patch('pymtpl.gen_methods.ExtractTestMethodInfo')
    @patch('pymtpl.gen_methods.os.makedirs')
    @patch('pymtpl.gen_methods.os.path.exists')
    def test_main_with_multiple_dlls(self, mock_exists, mock_makedirs, mock_extract_class, mock_torch_class):
        """Test main method with multiple DLL paths"""
        # Setup mocks
        mock_exists.return_value = False

        # Mock TorchExtractTestMethodInfo to return multiple classes
        mock_torch_instance = Mock()
        mock_torch_instance.decompile_dll_to_json.return_value = [
            {'IsInstantiable': True, 'TemplateName': 'ClassA', 'Parameters': []},
            {'IsInstantiable': True, 'TemplateName': 'ClassB', 'Parameters': []},
            {'IsInstantiable': False, 'TemplateName': 'ClassC', 'Parameters': []}
        ]
        mock_torch_class.return_value = mock_torch_instance

        # Mock ExtractTestMethodInfo
        mock_extract_instance = Mock()
        mock_extract_class.return_value = mock_extract_instance

        # Create GenMethods object with multiple DLLs
        pymtpl_file = '/path/to/test.mtpl'
        dll_paths = ['/path/to/dll1.dll', '/path/to/dll2.dll']
        obj = GenMethods(pymtpl_file, dll_paths)

        # Call main
        result = obj.main()

        # Verify decompile_dll_to_json was called with all DLL paths
        mock_torch_instance.decompile_dll_to_json.assert_called_once_with(dll_paths)

        # Verify ExtractTestMethodInfo was initialized with the JSON result
        mock_extract_class.assert_called_once()
        call_args = mock_extract_class.call_args[0]
        self.assertEqual(len(call_args[0]), 3)  # Should have 3 classes from JSON

    @patch('pymtpl.gen_methods.TorchExtractTestMethodInfo')
    @patch('pymtpl.gen_methods.ExtractTestMethodInfo')
    @patch('pymtpl.gen_methods.os.makedirs')
    @patch('pymtpl.gen_methods.os.path.exists')
    def test_main_returns_outdir(self, mock_exists, mock_makedirs, mock_extract_class, mock_torch_class):
        """Test that main method returns the output directory path"""
        # Setup mocks
        mock_exists.return_value = True

        # Mock TorchExtractTestMethodInfo
        mock_torch_instance = Mock()
        mock_torch_instance.decompile_dll_to_json.return_value = []
        mock_torch_class.return_value = mock_torch_instance

        # Mock ExtractTestMethodInfo
        mock_extract_instance = Mock()
        mock_extract_class.return_value = mock_extract_instance

        # Create GenMethods object
        pymtpl_file = '/path/to/test.mtpl'
        dll_paths = ['/path/to/test.dll']
        obj = GenMethods(pymtpl_file, dll_paths)

        # Test with default outdir
        result1 = obj.main()
        self.assertEqual(result1, os.path.abspath('/path/to/pymtpl_generated'))

        # Test with custom outdir
        result2 = obj.main(outdir='/custom/path')
        self.assertEqual(result2, '/custom/path')


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
