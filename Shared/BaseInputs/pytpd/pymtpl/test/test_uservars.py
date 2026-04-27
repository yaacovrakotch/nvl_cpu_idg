#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
unittest for uservars.py
"""
from setenv_unittest import UT_DIR_REPO, ROOT_ENV
from gadget.ut import TestCase, unittest
from gadget.files import TempDir
from pymtpl.uservars import UserVars
from pymtpl.core import Initialize, Spec, InitializeMTL, Import
from gadget.errors import ErrorUser
import os


class TestUserVars(TestCase):

    def setUp(self):
        # Clear registries before each test
        UserVars.clear_registry()
        Import.clear_registry()
        Initialize.clear_all()

    def tearDown(self):
        # Clean up after each test
        UserVars.clear_registry()
        Import.clear_registry()

    def test_init_basic(self):
        # Test UserVars initialization with filename only (setname defaults to filename)
        usrv = UserVars('test_module')
        self.assertEqual(usrv._filename, 'test_module')
        self.assertEqual(usrv._setname, 'test_module')
        self.assertEqual(len(UserVars._uservar_registry), 1)

    def test_init_with_setname(self):
        # Test UserVars initialization with both filename and setname
        usrv = UserVars('test_module', 'CustomSet')
        self.assertEqual(usrv._filename, 'test_module')
        self.assertEqual(usrv._setname, 'CustomSet')

    def test_init_duplicate_setname(self):
        # Test error when duplicate setname is used
        UserVars('test_module', 'Set1')
        with self.assertRaisesRegex(ErrorUser, 'already exists'):
            UserVars('test_module2', 'Set1')

    def test_clear_registry(self):
        # Test clearing the registry
        UserVars('test1')
        UserVars('test2')
        self.assertEqual(len(UserVars._uservar_registry), 2)
        UserVars.clear_registry()
        self.assertEqual(len(UserVars._uservar_registry), 0)

    def test_int_variable(self):
        # Test adding integer variable
        usrv = UserVars('test_module')
        usrv.DummyInt = 25
        self.assertEqual(len(usrv._variables), 1)
        var_type, var_name, value, is_spec, is_array = usrv._variables[0]
        self.assertEqual(var_type, 'Integer')
        self.assertEqual(var_name, 'DummyInt')
        self.assertEqual(value, 25)
        self.assertFalse(is_spec)
        self.assertFalse(is_array)

    def test_float_variable(self):
        # Test adding float variable
        usrv = UserVars('test_module')
        usrv.DummyDouble = 25.0
        var_type, var_name, value, is_spec, is_array = usrv._variables[0]
        self.assertEqual(var_type, 'Double')
        self.assertEqual(value, 25.0)

    def test_string_variable(self):
        # Test adding string variable
        usrv = UserVars('test_module')
        usrv.DummyString = "TestString"
        var_type, var_name, value, is_spec, is_array = usrv._variables[0]
        self.assertEqual(var_type, 'String')
        self.assertEqual(value, "TestString")

    def test_bool_variable(self):
        # Test adding boolean variable
        usrv = UserVars('test_module')
        usrv.DummyBool = False
        var_type, var_name, value, is_spec, is_array = usrv._variables[0]
        self.assertEqual(var_type, 'Boolean')
        self.assertEqual(value, False)

    def test_int_spec(self):
        # Test integer spec expression
        usrv = UserVars('test_module')
        usrv.IntSpec = ('PTH_PRESOAK.DummyInt + 20', int)
        var_type, var_name, value, is_spec, is_array = usrv._variables[0]
        self.assertEqual(var_type, 'Integer')
        self.assertEqual(value, 'PTH_PRESOAK.DummyInt + 20')
        self.assertTrue(is_spec)

    def test_float_spec(self):
        # Test float spec expression
        usrv = UserVars('test_module')
        usrv.DoubleSpec = ('PTH_PRESOAK.DummyDouble + 10.5', float)
        var_type, var_name, value, is_spec, is_array = usrv._variables[0]
        self.assertEqual(var_type, 'Double')
        self.assertTrue(is_spec)

    def test_string_spec(self):
        # Test string spec expression
        usrv = UserVars('test_module')
        usrv.StringSpec = ('GetEnvironmentVariable("~HDMT_TP_BASE_DIR")', str)
        var_type, var_name, value, is_spec, is_array = usrv._variables[0]
        self.assertEqual(var_type, 'String')
        self.assertTrue(is_spec)

    def test_bool_spec(self):
        # Test boolean spec expression
        usrv = UserVars('test_module')
        usrv.BoolSpec = ('PTH_PRESOAK.DummyInt > 20', bool)
        var_type, var_name, value, is_spec, is_array = usrv._variables[0]
        self.assertEqual(var_type, 'Boolean')
        self.assertTrue(is_spec)

    def test_array_int(self):
        # Test integer array
        usrv = UserVars('test_module')
        usrv.ArrayInt = [1, 2, 3, 4, 5]
        var_type, var_name, value, is_spec, is_array = usrv._variables[0]
        self.assertEqual(var_type, 'Integer')
        self.assertTrue(is_array)
        self.assertEqual(value, [1, 2, 3, 4, 5])

    def test_array_float(self):
        # Test float array
        usrv = UserVars('test_module')
        usrv.ArrayDouble = [1.1, 2.2, 3.3]
        var_type, var_name, value, is_spec, is_array = usrv._variables[0]
        self.assertEqual(var_type, 'Double')
        self.assertTrue(is_array)

    def test_array_string(self):
        # Test string array
        usrv = UserVars('test_module')
        usrv.ArrayString = ["TestString", "AnotherString"]
        var_type, var_name, value, is_spec, is_array = usrv._variables[0]
        self.assertEqual(var_type, 'String')
        self.assertTrue(is_array)

    def test_array_bool(self):
        # Test boolean array
        usrv = UserVars('test_module')
        usrv.ArrayBool = [True, False, True]
        var_type, var_name, value, is_spec, is_array = usrv._variables[0]
        self.assertEqual(var_type, 'Boolean')
        self.assertTrue(is_array)

    def test_array_empty(self):
        # Test empty array raises error
        usrv = UserVars('test_module')
        with self.assertRaisesRegex(ErrorUser, 'cannot be empty'):
            usrv.EmptyArray = []

    def test_array_mixed_types(self):
        # Test mixed type array raises error
        usrv = UserVars('test_module')
        with self.assertRaisesRegex(ErrorUser, 'same type'):
            usrv.MixedArray = [1, 2.5, 3]

    def test_array_int_spec(self):
        # Test integer array spec
        usrv = UserVars('test_module')
        usrv.ArrayIntSpec = ('[1,2,3,4,PTH_PRESOAK.DummyInt]', [int])
        var_type, var_name, value, is_spec, is_array = usrv._variables[0]
        self.assertEqual(var_type, 'Integer')
        self.assertTrue(is_spec)
        self.assertTrue(is_array)

    def test_array_float_spec(self):
        # Test float array spec
        usrv = UserVars('test_module')
        usrv.ArrayDoubleSpec = ('[1.5,2.5,PTH_PRESOAK.DummyDouble]', [float])
        var_type, var_name, value, is_spec, is_array = usrv._variables[0]
        self.assertEqual(var_type, 'Double')
        self.assertTrue(is_spec)
        self.assertTrue(is_array)

    def test_array_string_spec(self):
        # Test string array spec
        usrv = UserVars('test_module')
        usrv.ArrayStringSpec = ('["String1","String2"]', [str])
        var_type, var_name, value, is_spec, is_array = usrv._variables[0]
        self.assertEqual(var_type, 'String')
        self.assertTrue(is_spec)
        self.assertTrue(is_array)

    def test_array_bool_spec(self):
        # Test boolean array spec
        usrv = UserVars('test_module')
        usrv.ArrayBoolSpec = ('[True,False,PTH_PRESOAK.DummyBool]', [bool])
        var_type, var_name, value, is_spec, is_array = usrv._variables[0]
        self.assertEqual(var_type, 'Boolean')
        self.assertTrue(is_spec)
        self.assertTrue(is_array)

    def test_get_uservar_as_spec(self):
        # Test accessing uservar returns Spec
        usrv = UserVars('PTH_PRESOAK')
        usrv.DummyInt = 25
        spec_obj = usrv.DummyInt
        self.assertIsInstance(spec_obj, Spec)
        self.assertEqual(str(spec_obj), 'PTH_PRESOAK.DummyInt')

    def test_get_undefined_uservar(self):
        # Test accessing undefined uservar raises error
        usrv = UserVars('PTH_PRESOAK')
        usrv.DummyInt = 25
        with self.assertRaisesRegex(ErrorUser, 'not found'):
            _ = usrv.UndefinedVar

    def test_get_method(self):
        # Test accessing method works normally (line 74: callable check)
        usrv = UserVars('test_module')
        # Access the method without calling it
        method = usrv._write_variables
        self.assertTrue(callable(method))
        # Also test a class method
        self.assertTrue(callable(usrv.write_all_uservars))
        # also test an internal variable
        self.assertEqual(usrv._filename, 'test_module')

    def test_get_noncallable_attribute_not_in_variables(self):
        # Test accessing a non-callable attribute (line 74 is False) that's not in _variables
        usrv = UserVars('test_module')
        # Directly set a non-callable attribute to the instance __dict__ (bypassing __setattr__)
        object.__setattr__(usrv, 'some_value', 42)
        # Now try to access it - should fail at the confirm on line 78
        # because it's not in _variables even though it exists and is not callable
        with self.assertRaisesRegex(ErrorUser, 'not found'):
            _ = usrv.some_value

    def test_write_single_file_single_set(self):
        # Test writing one file with one set
        with TempDir(chdir=True):
            InitializeMTL('test_module', 'test_module')
            usrv = UserVars('test_module')
            usrv.DummyInt = 25
            usrv.DummyString = "TestString"

            UserVars.write_all_uservars('test_module')

            self.assertTrue(os.path.exists('test_module.usrv'))
            with open('test_module.usrv', 'r') as f:
                content = f.read()
            self.assertIn('Version 1.0;', content)
            self.assertIn('UserVars test_module', content)
            self.assertIn('Integer DummyInt = 25;', content)
            self.assertIn('String DummyString = "TestString";', content)

    def test_write_single_file_multiple_sets(self):
        # Test multiple UserVars with same filename write to one file
        with TempDir(chdir=True):
            InitializeMTL('test_module', 'test_module')
            usrv1 = UserVars('test_module')
            usrv1.Var1 = 10

            usrv2 = UserVars('test_module', 'Set2')
            usrv2.Var2 = 20

            UserVars.write_all_uservars('test_module')

            self.assertTrue(os.path.exists('test_module.usrv'))
            with open('test_module.usrv', 'r') as f:
                content = f.read()
            self.assertIn('UserVars test_module', content)
            self.assertIn('UserVars Set2', content)
            self.assertIn('Integer Var1 = 10;', content)
            self.assertIn('Integer Var2 = 20;', content)

    def test_write_multiple_files(self):
        # Test multiple filenames create multiple files
        with TempDir(chdir=True):
            InitializeMTL('test_module', 'test_module')
            usrv1 = UserVars('test_module')
            usrv1.Var1 = 10

            usrv2 = UserVars('separate_file', 'Set3')
            usrv2.Var2 = 20

            UserVars.write_all_uservars('test_module')

            self.assertTrue(os.path.exists('test_module.usrv'))
            self.assertTrue(os.path.exists('separate_file.usrv'))

    def test_empty_uservar_not_written(self):
        # Test empty UserVars should not write
        with TempDir(chdir=True):
            InitializeMTL('test_module', 'test_module')
            usrv1 = UserVars('test_module')
            usrv1.Var1 = 10

            usrv2 = UserVars('test_module', 'emptyset')  # no variables added
            usrv3 = UserVars('separate_file_2', 'empty')  # no variables added

            UserVars.write_all_uservars('test_module')

            # test_module.usrv should exist with only first set
            self.assertTrue(os.path.exists('test_module.usrv'))
            with open('test_module.usrv', 'r') as f:
                content = f.read()
            self.assertIn('UserVars test_module', content)
            self.assertNotIn('UserVars emptyset', content)

            # separate_file_2.usrv should not exist
            self.assertFalse(os.path.exists('separate_file_2.usrv'))

    def test_output_format_integer(self):
        # Test integer output format
        with TempDir(chdir=True):
            InitializeMTL('test_module', 'test_module')
            usrv = UserVars('test_module')
            usrv.DummyInt = 25

            UserVars.write_all_uservars('test_module')

            with open('test_module.usrv', 'r') as f:
                content = f.read()
            self.assertIn('Integer DummyInt = 25;', content)

    def test_output_format_double(self):
        # Test double output format
        with TempDir(chdir=True):
            InitializeMTL('test_module', 'test_module')
            usrv = UserVars('test_module')
            usrv.DummyDouble = 25.5

            UserVars.write_all_uservars('test_module')

            with open('test_module.usrv', 'r') as f:
                content = f.read()
            self.assertIn('Double DummyDouble = 25.5;', content)

    def test_output_format_string(self):
        # Test string output format with quotes
        with TempDir(chdir=True):
            InitializeMTL('test_module', 'test_module')
            usrv = UserVars('test_module')
            usrv.DummyString = "TestString"

            UserVars.write_all_uservars('test_module')

            with open('test_module.usrv', 'r') as f:
                content = f.read()
            self.assertIn('String DummyString = "TestString";', content)

    def test_output_format_boolean(self):
        # Test boolean output format (lowercase)
        with TempDir(chdir=True):
            InitializeMTL('test_module', 'test_module')
            usrv = UserVars('test_module')
            usrv.DummyBool = False

            UserVars.write_all_uservars('test_module')

            with open('test_module.usrv', 'r') as f:
                content = f.read()
            self.assertIn('Boolean DummyBool = False;', content)

    def test_output_format_array_int(self):
        # Test integer array output format
        with TempDir(chdir=True):
            InitializeMTL('test_module', 'test_module')
            usrv = UserVars('test_module')
            usrv.ArrayInt = [1, 2, 3, 4, 5]

            UserVars.write_all_uservars('test_module')

            with open('test_module.usrv', 'r') as f:
                content = f.read()
            self.assertIn('Array<Integer> ArrayInt = [1,2,3,4,5];', content)

    def test_output_format_array_string(self):
        # Test string array output format with double quotes
        with TempDir(chdir=True):
            InitializeMTL('test_module', 'test_module')
            usrv = UserVars('test_module')
            usrv.ArrayString = ["TestString", "AnotherString"]

            UserVars.write_all_uservars('test_module')

            with open('test_module.usrv', 'r') as f:
                content = f.read()
            self.assertIn('Array<String> ArrayString = ["TestString","AnotherString"];', content)

    def test_output_format_spec(self):
        # Test spec expressions have no quotes
        with TempDir(chdir=True):
            InitializeMTL('test_module', 'test_module')
            usrv = UserVars('test_module')
            usrv.IntSpec = ('PTH_PRESOAK.DummyInt+20', int)

            UserVars.write_all_uservars('test_module')

            with open('test_module.usrv', 'r') as f:
                content = f.read()
            self.assertIn('Integer IntSpec = PTH_PRESOAK.DummyInt+20;', content)
            self.assertNotIn('"PTH_PRESOAK.DummyInt+20"', content)

    def test_error_none_value(self):
        # Test setting variable to None raises error
        usrv = UserVars('test_module')
        with self.assertRaisesRegex(ErrorUser, 'Value is required'):
            usrv.InvalidVar = None

    def test_error_invalid_tuple_length(self):
        # Test tuple with wrong length raises error
        usrv = UserVars('test_module')
        with self.assertRaisesRegex(ErrorUser, 'must be of length 2'):
            usrv.InvalidVar = ('expr', int, 'extra')

    def test_error_tuple_non_string_expr(self):
        # Test tuple with non-string expression raises error
        usrv = UserVars('test_module')
        with self.assertRaisesRegex(ErrorUser, 'first element must be a string'):
            usrv.InvalidVar = (123, int)

    def test_error_invalid_type_in_tuple(self):
        # Test invalid type in tuple raises error
        usrv = UserVars('test_module')
        with self.assertRaisesRegex(TypeError, 'second element must be a type'):
            usrv.InvalidVar = ('expr', 'not_a_type')

    def test_error_invalid_array_type(self):
        # Test array type specifier must be [type] format
        usrv = UserVars('test_module')
        with self.assertRaisesRegex(ErrorUser, 'must be .type. with length of 1'):
            usrv.InvalidVar = ('expr', [int, float])

    def test_import_registry(self):
        # Test .usrv files are added to Import registry
        UserVars('test_module')
        self.assertIn('test_module.usrv', Import._import_registry_name)

        # Should not duplicate
        UserVars('test_module', 'Set2')
        import_count = Import._import_registry_name.count('test_module.usrv')
        self.assertEqual(import_count, 1)

    def test_comprehensive_example(self):
        # Test comprehensive example similar to PTH_PRESOAK.py
        with TempDir(chdir=True):
            InitializeMTL('PTH_PRESOAK', 'PTH_PRESOAK')

            # Create first set with all types
            usrv = UserVars('PTH_PRESOAK')
            usrv.DummyInt = 25
            usrv.IntSpec = ('PTH_PRESOAK.DummyInt+20', int)
            usrv.ArrayInt = [1, 2, 3, 4, 5]
            usrv.ArrayIntSpec = ('[1,2,3,4,PTH_PRESOAK.DummyInt]', [int])

            usrv.DummyBool = False
            usrv.BoolSpec = ('PTH_PRESOAK.DummyInt>20', bool)
            usrv.ArrayBool = [True, False, True]
            usrv.ArrayBoolSpec = ('[True,False,PTH_PRESOAK.DummyBool]', [bool])

            usrv.DummyString = "TestString"
            usrv.StringSpec = ('GetEnvironmentVariable("~HDMT_TP_BASE_DIR")+"/Modules/PTH_DTS/InputFiles/"', str)
            usrv.ArrayString = ["TestString", "AnotherString"]
            usrv.ArrayStringSpec = ('["String1","String2",PTH_PRESOAK.DummyString]', [str])

            usrv.DummyDouble = 25.0
            usrv.DoubleSpec = ('PTH_PRESOAK.DummyDouble+10.5', float)
            usrv.ArrayDouble = [1.1, 2.2, 3.3]
            usrv.ArrayDoubleSpec = ('[1.5,2.5,PTH_PRESOAK.DummyDouble]', [float])

            # Create second set in same file
            usrv2 = UserVars('PTH_PRESOAK', 'Set2')
            usrv2.DummyInt2 = 11

            # Create separate file
            usrv3 = UserVars('separate_file', 'Set3')
            usrv3.DummyInt3 = 15

            # Create empty sets (should not be written)
            usrv4 = UserVars('separate_file_2', 'empty')
            usrv5 = UserVars('PTH_PRESOAK', 'emptyset2')

            UserVars.write_all_uservars('PTH_PRESOAK')

            # Verify PTH_PRESOAK.usrv
            self.assertTrue(os.path.exists('PTH_PRESOAK.usrv'))
            expected_pth_presoak = '''Version 1.0;

UserVars PTH_PRESOAK
{
    Integer DummyInt = 25;
    Integer IntSpec = PTH_PRESOAK.DummyInt+20;
    Array<Integer> ArrayInt = [1,2,3,4,5];
    Array<Integer> ArrayIntSpec = [1,2,3,4,PTH_PRESOAK.DummyInt];
    Boolean DummyBool = False;
    Boolean BoolSpec = PTH_PRESOAK.DummyInt>20;
    Array<Boolean> ArrayBool = [True,False,True];
    Array<Boolean> ArrayBoolSpec = [True,False,PTH_PRESOAK.DummyBool];
    String DummyString = "TestString";
    String StringSpec = GetEnvironmentVariable("~HDMT_TP_BASE_DIR")+"/Modules/PTH_DTS/InputFiles/";
    Array<String> ArrayString = ["TestString","AnotherString"];
    Array<String> ArrayStringSpec = ["String1","String2",PTH_PRESOAK.DummyString];
    Double DummyDouble = 25.0;
    Double DoubleSpec = PTH_PRESOAK.DummyDouble+10.5;
    Array<Double> ArrayDouble = [1.1,2.2,3.3];
    Array<Double> ArrayDoubleSpec = [1.5,2.5,PTH_PRESOAK.DummyDouble];
}

UserVars Set2
{
    Integer DummyInt2 = 11;
}
'''
            with open('PTH_PRESOAK.usrv', 'r') as f:
                content = f.read()
            self.assertTextEqual(content, expected_pth_presoak)

            # Verify separate_file.usrv
            self.assertTrue(os.path.exists('separate_file.usrv'))
            expected_separate_file = '''Version 1.0;

UserVars Set3
{
    Integer DummyInt3 = 15;
}
'''
            with open('separate_file.usrv', 'r') as f:
                content = f.read()
            self.assertTextEqual(content, expected_separate_file)

            # Verify empty file not created
            self.assertFalse(os.path.exists('separate_file_2.usrv'))

    def test_error_invalid_type_object(self):
        # Test TypeError when invalid type object is used (line 155)
        usrv = UserVars('test_module')
        with self.assertRaisesRegex(TypeError, 'must be int, float, str, or bool'):
            usrv.InvalidVar = ('some_expression', list)

    def test_repeated_write_no_updates(self):
        # Test that repeated writes with no changes don't rewrite files
        with TempDir(chdir=True):
            InitializeMTL('test_module', 'test_module')
            usrv = UserVars('test_module')
            usrv.DummyInt = 25
            usrv.DummyString = "TestString"

            # First write should create the file
            UserVars.write_all_uservars('test_module')
            self.assertTrue(os.path.exists('test_module.usrv'))

            # Get the modification time
            mtime1 = os.path.getmtime('test_module.usrv')

            # Second write with no changes - should log "NO UPDATE"
            import time
            time.sleep(0.01)  # Small delay to ensure time difference if file is rewritten
            UserVars.write_all_uservars('test_module')

            # Modification time should be the same (file not rewritten)
            mtime2 = os.path.getmtime('test_module.usrv')
            self.assertEqual(mtime1, mtime2)


if __name__ == '__main__':
    unittest.main()
