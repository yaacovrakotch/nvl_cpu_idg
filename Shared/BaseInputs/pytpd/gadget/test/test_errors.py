#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unittest for errors class
"""
from setenv_unittest import ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests
from gadget.errors import *
from os.path import dirname
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.dictmore import TVPVConfigDict
from gadget.shell import tmpdir, HOSTNAME, SystemCall, MachineInfo
from gadget.gizmo import MockVar, IS_UNIX, IS_WIN
from gadget.files import TempName, File, TempDir
from gadget.disk import mkdirs
from unittest.mock import Mock, patch
from os.path import basename, join
import os
import sys


def some_fail():
    """Used in traceback unittest"""
    raise ErrorVep("something went wrong")


def foo_traceback():
    Func(12)


def Func(var):
    Check.is_str('arg1', var)


class CheckTest(TestCase):

    def test_basic(self):
        # check line number
        with self.assertRaisesRegex(ErrorUser, 'Pls fix value of arg1 in line# 26'):
            foo_traceback()

        # check message
        with self.assertRaisesRegex(ErrorUser, 'On arg1=None, arg1 is expecting string'):
            Check.is_str('arg1', None)

        # specific line number
        with self.assertRaisesRegex(ErrorUser, 'Pls fix value of arg1 in line# 5'):
            Check.is_str('arg1', None, lno=5)

        # oknone=True should be ignored
        self.assertEqual(Check.is_str('arg1', 'abc', oknone=True), 'abc')

    def test_min_python_version(self):
        # Test case: Check for system version is 3, 13 or higher
        with self.assertRaisesRegex(Exception, 'Python 4.10 or higher is required'):
            Check.min_python_version(4, 10, _ver=(3, 12))

        with self.assertRaisesRegex(Exception, 'Python 3.13 or higher is required'):
            Check.min_python_version(3, 13, _ver=(3, 12))

        with self.assertRaisesRegex(Exception, 'Python 4.13 or higher is required'):
            Check.min_python_version(4, 13, _ver=(3, 12))

        # Passing cases
        Check.min_python_version(1, 1, _ver=(3, 12))
        Check.min_python_version(1, 13, _ver=(3, 12))
        Check.min_python_version(3, 11, _ver=(3, 12))
        Check.min_python_version(3, 12, _ver=(3, 12))

    def test_types(self):
        # is_str
        self.assertEqual(Check.is_str('arg1', None, oknone=True), None)
        self.assertEqual(Check.is_str('arg1', 'abc'), 'abc')
        with self.assertRaisesRegex(ErrorUser, 'On arg1=1, arg1 is expecting string'):
            Check.is_str('arg1', 1)

        # is_int
        self.assertEqual(Check.is_int('arg1', None, oknone=True), None)
        self.assertEqual(Check.is_int('arg1', 5), 5)
        with self.assertRaisesRegex(ErrorUser, "On arg1='1', arg1 is expecting int"):
            Check.is_int('arg1', '1')

        # is_bool
        self.assertEqual(Check.is_bool('arg1', None, oknone=True), None)
        self.assertEqual(Check.is_bool('arg1', True), True)
        with self.assertRaisesRegex(ErrorUser, "On arg1=1, arg1 is expecting bool"):
            Check.is_bool('arg1', 1)

        # any object
        self.assertEqual(Check.is_obj('arg1', None, int, oknone=True), None)
        self.assertEqual(Check.is_obj('arg1', 5, int), 5)
        self.assertEqual(Check.is_obj('arg1', 5, (int, str)), 5)
        self.assertEqual(Check.is_obj('arg1', 'abc', (int, str)), 'abc')
        with self.assertRaisesRegex(ErrorUser, "On arg1=1.1, arg1 is expecting.*int.*str"):
            Check.is_obj('arg1', 1.1, (int, str))

    def test_check_get_caller_lno(self):
        Check.check_get_caller_lno()    # make sure it pass


class Prod_AllClassesTest(TestCase):

    def test_required_classes(self):
        for cls in (ErrorVep, ErrorInput, ErrorConfig, ErrorEnv, ErrorExpect, ErrorCockpit):
            with self.assertRaisesRegex(cls, "error-message"):
                raise cls("error-message")
            with self.assertRaisesRegex(cls, "error-message"):
                raise cls("error-message", "suggestion")

    def test_exit1(self):
        with self.assertRaises(SystemExit):
            exit1("some error")

        # make sure traceback and exitcode is correct
        code = f"""
import sys
sys.path.insert(0, r'{ROOT_ENV}')
from gadget.errors import exit1
def foo():
    exit1("missing trace", "some suggestion")
foo()
"""
        with TempName(name=True) as tname:
            File(tname).touch(code).chmod("0775")
            ecode, result = SystemCall(tname, exe=True).run_outtxt()
        expect = '''==================================================
Error:      missing trace
Suggestion: some suggestion
=================================================='''
        self.assertTextEqual(result, expect)  # Make sure traceback is correct
        self.assertEqual(ecode, 1)


class RequiredTest(TestCase):

    def test_confirm(self):
        # pass case
        confirm(True, 'Hi', 'Do this')

        # fail case
        with self.assertRaisesRegex(ErrorUser, 'test_errors.py:test_confirm'):   # it should show correct traceback
            confirm(False, 'pls check blah', 'This should always fail')

        # fail case
        with self.assertRaisesRegex(NameError, 'var_not_found'):
            confirm(True, 'pls check blah', f'This {var_not_found}')

    def test_assertraises(self):
        # ErrorConfig
        with self.assertRaisesRegex(ErrorConfig, "myerrormessage"):
            raise ErrorConfig("hello myerrormessage")
        with self.assertRaisesRegex(Exception, "myerrormessage"):
            raise ErrorConfig("hello myerrormessage")
        with self.assertRaisesRegex(ErrorVepNoTB, "myerrormessage"):
            raise ErrorConfig("hello myerrormessage")
        with self.assertRaisesRegex(ErrorVepBase, "myerrormessage"):
            raise ErrorConfig("hello myerrormessage")

        # ErrorCockpit
        with self.assertRaisesRegex(ErrorCockpit, "myerrormessage"):
            raise ErrorCockpit("hello myerrormessage")
        with self.assertRaisesRegex(Exception, "myerrormessage"):
            raise ErrorCockpit("hello myerrormessage")
        with self.assertRaisesRegex(ErrorVep, "myerrormessage"):
            raise ErrorCockpit("hello myerrormessage")

    def test_try_ErrorConfig(self):
        def foo1():
            try:
                raise ErrorConfig("Error! Exception should have been caught")
            except ErrorConfig:
                return

        def foo2():
            try:
                raise ErrorConfig("Error! Exception should have been caught")
            except Exception:
                return

        def foo3():
            try:
                raise ErrorConfig("Error! Exception should have been caught")
            except ErrorVepBase:
                return

        def foo4():
            try:
                raise ErrorConfig("Error! Exception should have been caught")
            except ErrorVepNoTB:
                return

        foo1()
        foo2()
        foo3()
        foo4()

    def test_try_ErrorCockpit(self):
        def foo1():
            try:
                raise ErrorCockpit("Error! Exception should have been caught")
            except ErrorCockpit:
                return

        def foo2():
            try:
                raise ErrorCockpit("Error! Exception should have been caught")
            except Exception:
                return

        def foo4():
            try:
                raise ErrorCockpit("Error! Exception should have been caught")
            except ErrorVep:
                return

        foo1()
        foo2()
        foo4()

    def test_traceback1(self):
        # no traceback
        code = f'''
import sys
sys.path.insert(0, r'{ROOT_ENV}')
from gadget.errors import ErrorConfig
raise ErrorConfig('hello')
print('shouldnotprint')
'''
        with TempName(exe=code, name=True) as name:
            ecode, sout, serr = SystemCall(name, exe=True).run_sout_serr()
            self.assertEqual(sout, '')
            print(serr)
            self.assertRegexpEachList(serr.split('\n'),
                                      ['Error Type',
                                       '=+',
                                       'Error:      hello',
                                       'Suggestion: .*',
                                       'ErrorSig:   .*lno#6$',
                                       'Rundir:     .*',
                                       '=+'])

    def test_traceback2(self):
        # with traceback
        code = f'''
import sys
sys.path.insert(0, r'{ROOT_ENV}')
from gadget.errors import ErrorCockpit
raise ErrorCockpit('hello')
print('shouldnotprint')
'''
        with TempName(exe=code, name=True, delete=True) as name:
            ecode, sout, serr = SystemCall(name, exe=True).run_sout_serr()
            print("$$$$$$$$$")
            print(sout)
            print("$$$$$$$$$")
            print(serr)
            self.assertEqual(sout, '')
            self.assertEqual(len(serr.split('\n')), 10)
            self.assertIn('lno#6\n', serr)
            self.assertTrue('Error Type' in serr)

        print(serr)


class BaseClassTest(TestCase):

    def test_heirarchy(self):
        def foo1():
            raise ErrorCockpit("Invalid Config")

        def foo2():
            raise ErrorCockpit("Invalid Config", "Pls ask for help")

        self.assertRaises(Exception, foo1)   # parent class
        self.assertRaises(ErrorVep, foo1)    # parent class
        self.assertRaises(ErrorCockpit, foo1)
        self.assertRaises(ErrorCockpit, foo2)

    def test_message_displayed(self):
        def foo1():
            raise ErrorVep("myerrormessage")

        def foo_suggestion():
            raise ErrorVep("myerrormessage", "fix-this")

        self.assertRaisesRegex(ErrorVep, "myerrormessage", foo1)      # errormessage
        self.assertRaisesRegex(ErrorVep, "Pls read error message and do basic debug first", foo1)   # suggestion
        self.assertRaisesRegex(ErrorVep, HOSTNAME, foo1)              # errorsig
        self.assertRaisesRegex(ErrorVep, basename(__file__), foo1)    # rundir

        self.assertRaisesRegex(ErrorVep, "myerrormessage", foo_suggestion)      # errormessage
        self.assertRaisesRegex(ErrorVep, "fix-this", foo_suggestion)    # suggestion

    def test_get_main_error(self):
        # Normal exception - VEP
        try:
            raise ErrorInput("This is: error[text] message")
        except Exception as e:
            self.assertEqual(ErrorVep.get_main_error(e), "This is: error[text] message")

        # Normal exception - python
        try:
            raise ValueError("This [text]")
        except Exception as e:
            self.assertIn("This [text]", ErrorVep.get_main_error(e))

        # Normal text
        self.assertEqual(ErrorVep.get_main_error("some [text]"), "some [text]")

    def test_args(self):
        self.assertEqual(ErrorInput.args("errormsg"), ["errormsg"])
        self.assertEqual(ErrorInput.args(("errormsg", "suggestion")), ("errormsg", "suggestion"))


class OldCheckTest(TestCase):

    def test_check_required_valid(self):
        # Pass case - list
        check.required_valid({"aa": 1, "bb": 2, "cc": 3}.keys(),
                             required="aa bb".split(),
                             valid="aa bb cc".split(),
                             message="Hello")

        # Pass case - str
        check.required_valid(set("aa bb cc".split()),
                             required="aa bb",
                             message="Hello")

        # Pass case - set
        check.required_valid(set("aa bb cc".split()),
                             valid=set("aa bb cc".split()),
                             message="Hello")

        # Missing required
        self.assertRaisesRegex(ErrorConfig, "Hello.*does not exist", check.required_valid,
                               {"aa": 1, "bb": 2, "cc": 3}.keys(),
                               required="aa bb dd".split(),
                               valid="aa bb cc".split(),
                               message="Hello")

        # Unknown
        self.assertRaisesRegex(ErrorConfig, "Hello.*not a valid", check.required_valid,
                               set("aa bb cc".split()),
                               required="aa bb",
                               valid="aa bb dd",
                               message="Hello")

    def test_is_dir_empty_writable(self):
        # case1 - non-exist, fail case
        if IS_UNIX:  # Permissions of the root dir on Unix
            with self.assertRaisesRegex(ErrorUser, 'Pls make sure'):
                check.is_dir_empty_writeable('/empty_guaranteed_not_exist')

        # case2 - exist, empty, pass
        with TempDir(name=True) as tdir:
            check.is_dir_empty_writeable(tdir)
            self.assertFalse(isdir(tdir))

        # case3 - non-exist, pass case
        with TempDir(name=True) as tdir:
            check.is_dir_empty_writeable(f'{tdir}/empty')

            # case4 - exist, with files
            File(f'{tdir}/a').touch()
            with self.assertRaisesRegex(ErrorUser, 'Make sure destination dir is empty'):
                check.is_dir_empty_writeable(tdir)

            # case5 - user specified a file
            with self.assertRaisesRegex(ErrorUser, 'Pls specify a destination directory, or delete the file'):
                check.is_dir_empty_writeable(f'{tdir}/a')

            # case6 - exist, empty, fail, cannot rmdir
            mkdirs(f'{tdir}/empty2')
            with self.assertRaisesRegex(ErrorUser, 'cannot be removed'), \
                    MockVar(os, 'rmdir', Mock(side_effect=Exception)):
                check.is_dir_empty_writeable(f'{tdir}/empty2')

    def test_is_list(self):
        # pass case
        inp = ['a', 'b']
        self.assertIs(check.is_list(inp), inp)

        # fail case
        expected_msg = "class.*int"
        self.assertRaisesRegex(ErrorConfig, expected_msg, check.is_list, 12)

    def test_is_set(self):
        # pass case
        inp = {'a', 'b'}
        self.assertIs(check.is_set(inp), inp)

        # fail case
        expected_msg = "class.*int"
        self.assertRaisesRegex(ErrorConfig, expected_msg, check.is_set, 12)

    def test_is_list_or_set(self):
        # pass case
        inp = {'a', 'b'}
        self.assertIs(check.is_list_or_set(inp), inp)
        check.is_list_or_set(['a', 'b'])

        # fail case
        expected_msg = "class.*int"
        self.assertRaisesRegex(ErrorConfig, expected_msg, check.is_list_or_set, 12)

    def test_is_string(self):
        # pass case
        inp = "abc"
        self.assertIs(check.is_string(inp), inp)

        # fail case
        expected_msg = "class.*int"
        self.assertRaisesRegex(ErrorConfig, expected_msg, check.is_string, 12)

    def test_is_int(self):
        # pass case
        self.assertEqual(check.is_int(12), 12)
        self.assertEqual(check.is_int(0), 0)

        # fail case
        expected_msg = "class.*str"
        self.assertRaisesRegex(ErrorConfig, expected_msg, check.is_int, "abc")

    def test_is_callable(self):
        # pass case
        self.assertEqual(check.is_callable(dict), dict)

        # fail case
        self.assertRaisesRegex(ErrorConfig, "callable", check.is_callable, 1)

    def test_is_dict(self):
        # pass case
        aa = TVPVConfigDict()
        aa.top.child.key1 = 567
        self.assertIs(check.is_dict(aa), aa)
        res = check.is_dict(aa, make_copy=True)
        self.assertIsNot(res, aa)
        self.assertEqual(res, aa)

        # fail case
        expected_msg = "class.*str"
        self.assertRaisesRegex(ErrorConfig, expected_msg, check.is_dict, "abc")

    def test_is_dir(self):
        # pass case
        inp = dirname(sys.executable)
        self.assertIs(check.is_dir(inp), inp)

        # fail case
        self.assertRaisesRegex(ErrorConfig, "/tmp/surenotexist", check.is_dir, "/tmp/surenotexist")

    @unittest.skipIf(IS_WIN, 'unix only - cannot create broken link in windows')
    def test_is_broken_link(self):
        with TempDir(name=True) as tdir:
            # pass case
            self.assertIs(check.is_broken_link(tdir), tdir)
            # fail case
            os.symlink(join(tdir, 'missing'), join(tdir, 'new'))
            self.assertRaisesRegex(ErrorEnv, 'is a broken', check.is_broken_link, join(tdir, 'new'))

    def test_is_exist(self):
        # pass case
        inp = dirname(sys.executable)
        self.assertIs(check.is_exist(inp), inp)

        # fail case
        self.assertRaisesRegex(ErrorConfig, "/tmp/surenotexist", check.is_exist, "/tmp/surenotexist")

        # pass case list
        inp = [dirname(sys.executable),
               dirname(sys.executable),
               dirname(sys.executable)]
        self.assertIs(check.is_exist(inp), inp)

        # fail case list
        self.assertRaisesRegex(ErrorConfig, "/tmp/surenotexist", check.is_exist,
                               [dirname(sys.executable),
                                "/tmp/surenotexist",
                                dirname(sys.executable)])

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_is_dir_writable(self):
        # pass case
        inp = tmpdir()
        self.assertIs(check.is_dir_writable(inp), inp)

        # fail case
        if IS_UNIX:
            path = '/'
        else:
            path = 'i:\\'
        self.assertRaisesRegex(ErrorConfig, "not writable", check.is_dir_writable, path)

        # empty case
        with self.assertRaisesRegex(ErrorConfig, "Specified directory is empty"):
            check.is_dir_writable('')

        # not exist
        with self.assertRaisesRegex(ErrorConfig, "Directory does not exist"):
            check.is_dir_writable('/notexist')

    @unittest.skipIf(IS_WIN, 'unix only due chmod stuff')
    def test_is_modifiable(self):
        # pass case
        with TempName(name=True) as tn:
            File(tn).touch('abc')
            self.assertIs(check.is_modifiable(tn), tn)

            # fail case - no permission
            File(tn).chmod("0440")
            self.assertRaisesRegex(ErrorEnv, "cannot be modified", check.is_modifiable, tn)

        # another fail case
        self.assertRaisesRegex(ErrorEnv, "cannot be modified", check.is_modifiable,
                               sys.executable)

        # Directory modifiable
        with TempDir(name=True) as tdir:
            check.is_modifiable(tdir)

        # Directory not modifiable
        self.assertRaisesRegex(ErrorEnv, "cannot be modified", check.is_modifiable,
                               dirname(sys.executable))

    def test_is_auto_off(self):
        # pass case
        dd = TVPVConfigDict()
        dd.AUTO_OFF()
        self.assertIs(check.is_auto_off(dd), dd)

        # fail case
        dd = TVPVConfigDict()
        self.assertRaisesRegex(ErrorConfig, "dictionary has autovivification", check.is_auto_off, dd)
        self.assertRaisesRegex(ErrorVep, "dictionary has autovivification", check.is_auto_off, dd, errorclass=ErrorVep)

        # fail case, wrong class
        self.assertRaisesRegex(Exception, "must be VEP", check.is_auto_off, dd, errorclass=Exception)

    @unittest.skipIf(IS_WIN, 'unix only')
    def test_no_sles10(self):
        """
        Functional test for no_sles10
        :return:
        """
        # case: sles10 machine, catch exception
        with MockVar(MachineInfo, 'sles_version', Mock(return_value=10)):
            self.assertRaisesRegex(ErrorUser, 'Sles10 not supported', check.no_sles10)

        # case: sles11, expect True
        with MockVar(MachineInfo, 'sles_version', Mock(return_value=11)):
            self.assertTrue(check.no_sles10())

    def test_exc_source(self):
        result = ""
        try:
            some_fail()
        except ErrorVep:
            result = exc_source()
        self.assertIn('test_errors.py, line 22, in some_fail()', result)   # This must have correct line number since we are testing traceback

    def test_get_defaultclass(self):
        # pass case - default
        self.assertIs(check._get_defaultclass(None), ErrorConfig)
        self.assertIs(check._get_defaultclass(ErrorCockpit), ErrorCockpit)
        self.assertIs(check._get_defaultclass(None, ErrorCockpit), ErrorCockpit)
        self.assertIs(check._get_defaultclass(ErrorEnv, ErrorCockpit), ErrorEnv)

        # invalid input
        self.assertRaisesRegex(Exception, 'must be VEP', check._get_defaultclass, IOError)
        self.assertRaisesRegex(Exception, 'must be VEP', check._get_defaultclass, None, IOError)

    @patch.dict('os.environ', {'__NB_CLASS': ''})
    def test_is_ion_machine_pass(self):
        # mock_env.return_value = "vnc"
        self.assertTrue(check.is_ion_machine())

    @patch.dict('os.environ', {'__NB_CLASS': 'vnc'})
    def test_is_ion_machine_fail(self):
        with self.assertRaisesRegex(ErrorEnv, "cannot run"):
            check.is_ion_machine()


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
