#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
unittests for ut.py
"""
from setenv_unittest import ROOT_ENV, UT_DIR_REPO, EXIST_PDX_I_DRIVE     # must be first import for unittests
import time
import re
import os
import gadget.ut
from gadget.ut import *
from gadget.ut import _TestPEP8
from io import StringIO
from gadget.files import TempName, TempDir
from os.path import isdir, exists
from gadget.disk import mkdirs
from contextlib import nullcontext
from unittest.mock import patch
from types import SimpleNamespace


class CheckTmpDir_tests(TestCase):

    @unittest.skipIf(*is_ut_option("OPTIONAL", message="Flaky"))
    def test_basic(self):
        obj = CheckTmpDir()   # yes, instantiate again, it's ok to have duplicate message for test_ut.py
        with MockVar(sys, "stderr", StringIO()) as p:
            obj.close()
        self.assertEqual(p.getvalue(), "")

        with TempDir(name=True) as t:
            with MockVar(sys, "stderr", StringIO()) as p:
                obj.close()
        print(p.getvalue())
        self.assertTrue(p.getvalue().startswith("==="), "Should have the warning message")

    @unittest.skipIf(is_cov(), 'No need for coverage since it fails')
    def test_integration(self):
        tdir = tmpdir()
        fname = f'{tdir}/pytpd_must_not_exist_CheckTmpDir_unittest'
        assert not exists(fname)
        assert exists('gadget'), 'This test must be run from pytpd root'

        cmd = f'''{sys.executable} -c 'import gadget.ut; open("{fname}", "w").close()' '''
        _, out = SystemCall(cmd).run_outtxt()
        File(fname).unlink()
        self.assertTrue(out.startswith("==="), out)

    def intentional(self):    # execute this manually and visually inspect output of unittest
        with TempDir(delete=False, name=True) as tdir:
            print(f'TempDir created: {tdir}')

    def test_close(self):
        with TempDir(name=True) as fake_tmpdir, \
                MockVar(gadget.ut, "tmpdir", Mock(return_value=fake_tmpdir)), \
                MockVar(gadget.ut.atexit, "register", Mock()):
            obj = CheckTmpDir()

            with MockVar(sys, "stderr", StringIO()) as buf:
                obj.close()
            self.assertEqual(buf.getvalue(), "")

            leaked_file = os.path.join(fake_tmpdir, "leaked.tmp")
            with open(leaked_file, "w", encoding="utf-8") as f:
                f.write("leaked content")

            ignore_file = os.path.join(fake_tmpdir, "eclogin-errors.log")
            with open(ignore_file, "w", encoding="utf-8") as f:
                f.write("ignore me")

            broken_file = os.path.join(fake_tmpdir, "broken.tmp")
            with open(broken_file, "w", encoding="utf-8") as f:
                f.write("broken content")

            def fake_stat(path):
                if path == broken_file:
                    raise OSError("stat failure")
                return SimpleNamespace(st_uid=obj.uid)

            obj.stat = fake_stat

            with MockVar(sys, "stderr", StringIO()) as buf:
                obj.close()
            self.assertIn("tmp file created but not removed", buf.getvalue())
            self.assertIn(leaked_file, buf.getvalue())
            self.assertNotIn(ignore_file, buf.getvalue())
            self.assertNotIn(broken_file, buf.getvalue())


def code1_mixed():
    """Returns a unittest code - mixed SLOW and OPTIONAL"""

    return '''
from gadget.ut import unittest, is_ut_option
import os


class MiniTest(unittest.TestCase):
    def test_passfunc(self):
        self.assertTrue(True, "pass")

    def foo(self):
        self.assertTrue(True, "pass")

    def test_failfunc(self):
        self.assertTrue(False, "fail")


class Normalclass:
    def test_passfunc(self):
        self.assertTrue(True, "pass")


class MiniTest2(unittest.TestCase):
    @unittest.skipIf(*is_ut_option('SLOW', message="Slowtest"))
    def test_passfunc(self):
        self.assertTrue(True, "pass")

    def foo(self):
        self.assertTrue(True, "pass")

    @unittest.skipIf(*is_ut_option('OPTIONAL', message="Optional"))
    def test_failfunc(self):
        self.assertTrue(False, "fail")


unittest.main()'''


class Unittest_args(TestCase):
    """
    These tests checks the command arguments are working ok
    """

    def test_normal(self):
        with MockVar(os.environ, 'PYTHONPATH', ROOT_ENV),\
                TempName(exe=code1_mixed()) as t:
            ecode, sout, serr = SystemCall([t.name(), "-v", "-b"], exe=True).run_sout_serr()
            self.assertIn("FAILED (failures=1, skipped=2)", serr)

    def test_s(self):
        with MockVar(os.environ, 'PYTHONPATH', ROOT_ENV),\
                TempName(exe=code1_mixed()) as t:
            ecode, sout, serr = SystemCall([t.name(), "-v", "-b", "-s"], exe=True).run_sout_serr()
            self.assertIn("FAILED (failures=1, skipped=1)", serr)

    def test_o(self):
        with MockVar(os.environ, 'PYTHONPATH', ROOT_ENV),\
                TempName(exe=code1_mixed()) as t:
            ecode, sout, serr = SystemCall([t.name(), "-v", "-b", "-o"], exe=True).run_sout_serr()
            self.assertIn("FAILED (failures=2, skipped=1)", serr)

    @unittest.skipIf(is_cov(), 'No need for coverage since it fails from pipeline')
    def test_s_and_o(self):
        with MockVar(os.environ, 'PYTHONPATH', ROOT_ENV),\
                TempName(exe=code1_mixed()) as t:
            ecode, sout, serr = SystemCall([t.name(), "-v", "-b", "-o", "-s"], exe=True).run_sout_serr()
            self.assertIn("FAILED (failures=2)", serr)

    def test_print(self):
        self.assertRaises(SystemExit, print_help)

        with MockVar(os.environ, 'PYTHONPATH', ROOT_ENV):
            res = SystemCall([sys.argv[0], '-h'], exe=True).run_outonly()
        self.assertIn('notmpcheck', res)

    def test_printlast5failed(self):
        code = '''
from gadget.ut import unittest, is_ut_option
import os


class MiniTest(unittest.TestCase):

    def test_passfunc(self):
        print('passfunc')
        self.assertTrue(True, "pass")

    def foo(self):
        print('foo')
        self.assertTrue(True, "pass")

    def test_failfunc(self):
        print('failfunc')
        self.assertTrue(False, "fail")

    def test_errfunc(self):
        print('errfunc')
        raise ValueError("This is an error")


unittest.main()'''

        with MockVar(os.environ, 'PYTHONPATH', ROOT_ENV),\
                TempName(exe=code) as t:

            # unbuffered
            ecode, sout, serr = SystemCall([t.name(), "-v"], exe=True).run_sout_serr()
            expect = """
errfunc
failfunc
passfunc

---> 2 Failing Tests:
MiniTest.test_errfunc(__main__)
MiniTest.test_failfunc(__main__)"""
            result = [x for x in sout.split('\n') if dirname(t.name()) not in x]
            self.assertTextEqual('\n'.join(result), expect)

            # buffered output
            ecode, sout, serr = SystemCall([t.name(), "-v", "-b"], exe=True).run_sout_serr()
            expect = """
Stdout:
errfunc

Stdout:
failfunc

---> 2 Failing Tests:
MiniTest.test_errfunc(__main__)
MiniTest.test_failfunc(__main__)"""
            result = [x for x in sout.split('\n') if dirname(t.name()) not in x]
            self.assertTextEqual('\n'.join(result), expect)

    def test_printfirst5_morethan5(self):
        # Test that prints "First 5 of N Failing Tests" when there are more than 5 failures
        code = '''
from gadget.ut import unittest


class MiniTest(unittest.TestCase):

    def test_fail1(self):
        self.fail("Fail 1")

    def test_fail2(self):
        self.fail("Fail 2")

    def test_fail3(self):
        self.fail("Fail 3")

    def test_fail4(self):
        self.fail("Fail 4")

    def test_fail5(self):
        self.fail("Fail 5")

    def test_fail6(self):
        self.fail("Fail 6")

    def test_fail7(self):
        self.fail("Fail 7")


unittest.main()'''

        with MockVar(os.environ, 'PYTHONPATH', ROOT_ENV),\
                TempName(exe=code) as t:

            # Test with more than 5 failures
            ecode, sout, serr = SystemCall([t.name(), "-v", "-b", "-p"], exe=True).run_sout_serr()
            # Should show "First 5 of 7 Failing Tests"
            self.assertIn("---> First 5 of 7 Failing Tests:", sout)
            # Should list exactly 5 test names
            lines_after_marker = sout.split("---> First 5 of 7 Failing Tests:")[1].split('\n')
            test_lines = [line for line in lines_after_marker if 'MiniTest.test_fail' in line]
            self.assertEqual(len(test_lines), 5, f"Expected 5 test names, but got {len(test_lines)}")

    def test_printfirst5_inline_result(self):
        class DummyTest:
            def __init__(self, name):
                self.name = name

            def __str__(self):
                return self.name

        stream = StringIO()
        result = First5FailResult(stream, descriptions=True, verbosity=1)
        result.errors = []
        result.failures = [(DummyTest(f"Dummy.test_fail{i}"), None) for i in range(7)]

        with MockVar(sys, "stdout", StringIO()) as cap:
            result.printFirst5Failures()

        output = cap.getvalue()
        self.assertIn("---> First 5 of 7 Failing Tests:", output)
        failure_lines = [line for line in output.split('\n') if 'Dummy.test_fail' in line]
        self.assertEqual(len(failure_lines), 5)


class UT_Option_Test(TestCase):

    def test_basic(self):
        with MockVar(sys, "argv", "cmd -x -v -t".split()):
            op = UT_Options({'-x': "SLOW1",
                             '-y': "OPTIONAL1"})

            self.assertEqual(sys.argv, "cmd -v -t".split())
            self.assertEqual(op("SLOW1", message="hi"), (False, "hi. Add -x to test."))
            self.assertEqual(op("OPTIONAL1", message="hi."), (True, "hi. Add -y to test."))   # skip=True
            self.assertEqual(op("OPTIONAL1", message="hi.", neg=False), (False, "hi. Remove -y to test."))   # skip=True
            self.assertRaisesRegex(Exception, "Invalid is_ut_option", op, "OPTIONAL", message="hi")

            op.set_option("OPTIONAL1")
            self.assertEqual(op("OPTIONAL1", message="hi."), (False, "hi. Add -y to test."))
            self.assertRaises(Exception, op.set_option, "OPTIONALX")

    @unittest.skip("skip write to cwd")
    def test_cwd(self):
        with self.assertRaises(Exception):
            File("somefile").touch()

    def test_ut_data_exists(self):
        ctx = patch('setenv_unittest.UT_DIR', new=UT_DIR_REPO) if not EXIST_PDX_I_DRIVE else nullcontext()
        with ctx:
            self.assertTrue(ut_data_exists('Simple1'))
            self.assertFalse(ut_data_exists('surennotfound'))


class IndependentExec_tests(TestCase):

    @unittest.skipIf(*is_ut_option('SKIP_NIGHTLY_BUILD', message='manual run only', neg=False))
    @unittest.skipIf(*is_ut_option('SLOW', message="slowtest"))
    def test_basic(self):
        # Create a unittest script, check parsing algo then execute it and check for output
        self.maxDiff = None
        with MockVar(os.environ, 'PYTHONPATH', ROOT_ENV),\
                TempName(exe=code1_mixed()) as t:
            ie = IndependentExec()
            self.assertEqual(ie.getfuncs(t.name()), set(['MiniTest2.test_passfunc',
                                                         'MiniTest.test_passfunc',
                                                         'MiniTest.test_failfunc',
                                                         'MiniTest2.test_failfunc']))
            with MockVar(sys, "stdout", StringIO()) as p:
                ie.main(t.name(), arg_s=True, arg_o=True)
                self.assertMultiLineEqual(p.getvalue(), 'MiniTest.test_failfunc FAILED (failures=1)\nMiniTest.test_passfunc OK\nMiniTest2.test_failfunc FAILED (failures=1)\nMiniTest2.test_passfunc OK\n\nSummary of Fails: ========\nMiniTest.test_failfunc FAILED (failures=1)\nMiniTest2.test_failfunc FAILED (failures=1)\n')

            with MockVar(sys, "stdout", StringIO()) as p:
                ie.main(t.name(), arg_s=False, arg_o=False)
                self.assertMultiLineEqual(p.getvalue(), 'MiniTest.test_failfunc FAILED (failures=1)\nMiniTest.test_passfunc OK\nMiniTest2.test_failfunc OK (skipped=1)\nMiniTest2.test_passfunc OK (skipped=1)\n\nSummary of Fails: ========\nMiniTest.test_failfunc FAILED (failures=1)\n')

    @unittest.skipIf(*is_ut_option('SKIP_NIGHTLY_BUILD', message='manual run only', neg=False))
    def test_allpass(self):
        # Create a unittest script, check parsing algo then execute it and check for output
        code = '''
from gadget.ut import unittest, is_ut_option
import os

class MiniTest(unittest.TestCase):
    def test_passfunc(self):
        self.assertTrue(True, "pass")

    def foo(self):
        self.assertTrue(True, "pass")

unittest.main()
'''
        self.maxDiff = None
        with MockVar(os.environ, 'PYTHONPATH', ROOT_ENV),\
                TempName(exe=code) as t:
            ie = IndependentExec()
            self.assertEqual(ie.getfuncs(t.name()), set(['MiniTest.test_passfunc']))
            with MockVar(sys, "stdout", StringIO()) as p:
                ie.main(t.name(), arg_s=True, arg_o=True)
                self.assertMultiLineEqual(p.getvalue(), 'MiniTest.test_passfunc OK\n')


class SetMaxRunTime_tests(TestCase):

    @unittest.skipIf(*is_ut_option('SLOW', message="slowtest"))
    def test_set_max_runtime(self):
        def foo():
            time.sleep(60)
        set_max_runtime(1)
        self.assertRaises(Exception, foo)


class TestCaseTest(unittest.TestCase):   # this must be unittest.TestCase

    def test_basic(self):
        # Create a unittest script, check that it runs using TestCase
        code = '''
from gadget.ut import unittest, is_ut_option, TestCase
import os


class MiniTest(TestCase):
    def test_passfunc(self):
        self.assertTrue(True, "pass")

    def test_failfunc(self):
        self.assertFalse(True, "pass")


unittest.main()'''
        self.maxDiff = None
        with MockVar(os.environ, 'PYTHONPATH', ROOT_ENV),\
                TempName(exe=code) as t:
            res = SystemCall([t.name(), "-v", "-b"]).run_outonly()
            print(res)
            self.assertIn('MiniTest.test_failfunc(__main__) ... FAIL', res)
            self.assertIn('MiniTest.test_passfunc(__main__) ... ok', res)
            self.assertIn('TestPEP8.test_PEP8(gadget.ut) ... ok', res)
            self.assertIn('Ran 4 tests', res)
            self.assertIn('FAIL: MiniTest.test_failfunc(__main__)', res)

    @unittest.skipIf(*is_ut_option('SLOW', message="slowtest"))
    def test_buffer_output_log(self):
        # This unittest tests the log.info() and log.debug() under '-v -b' conditions for both pass and fail

        # pass case =====================================================
        code = '''
from gadget.ut import unittest, TestCase
from gadget.pylog import log
import os


class MiniTest(TestCase):
    def test_log(self):
        print("fromprint")
        log.info("INFO_message")
        log.debug("DEBUG_message")


unittest.main()'''
        self.maxDiff = None
        with MockVar(os.environ, 'PYTHONPATH', ROOT_ENV),\
                TempName(exe=code) as t:

            # verbose and buffered
            _, sout, serr = SystemCall([t.name(), "-v", "-b"]).run_sout_serr()
            expect1 = '''
'''
            result = [x for x in sout.split('\n') if 'PEP8 files to check' not in x]
            self.assertTextEqual('\n'.join(result), expect1)
            expect2 = '''
MiniTest.test_log(__main__) ... ok
TestPEP8.test_PEP8(gadget.ut) ... ok
TestPEP8.test_check_unittest_sha(gadget.ut) ... ok

----------------------------------------------------------------------

OK
'''
            result = [x for x in serr.split('\n') if 'Ran 3 tests' not in x]
            result = [x for x in result if dirname(t.name()) not in x]
            self.assertTextEqual('\n'.join(result), expect2)

            # verbose
            _, sout, serr = SystemCall([t.name(), "-v"]).run_sout_serr()
            expect1 = '''
fromprint
INFO_message
DEBUG   : DEBUG_message
'''
            result = [x for x in sout.split('\n') if 'PEP8 files to check' not in x]
            self.assertTextEqual('\n'.join(result), expect1)

            result = []
            for line in serr.split('\n'):
                if 'Ran 3 tests' in line:
                    continue
                if 'ResourceWarning:' in line:
                    continue
                if 'for handler in' in line:
                    continue
                if line.startswith('ok'):
                    continue
                if '/tmp/' in line:
                    continue
                result.append(line)
            expect2 = '''
TestPEP8.test_PEP8(gadget.ut) ... ok
TestPEP8.test_check_unittest_sha(gadget.ut) ... ok

----------------------------------------------------------------------

OK
'''
            self.assertTextEqual('\n'.join(result), expect2)

        # fail case ====================================================
        code = '''
from gadget.ut import unittest, TestCase
from gadget.pylog import log
import os


class MiniTest(TestCase):

    def test_log(self):
        log.info("INFO_message")
        log.debug("DEBUG_message")
        self.fail("error")


unittest.main()'''
        self.maxDiff = None
        with MockVar(os.environ, 'PYTHONPATH', ROOT_ENV),\
                TempName(exe=code) as t:
            _, sout, serr = SystemCall([t.name(), "-v", "-b"]).run_sout_serr()
            expect1 = '''
Stdout:
INFO_message
DEBUG   : DEBUG_message

---> 1 Failing Test:
MiniTest.test_log(__main__)'''
            result = [x for x in sout.split('\n') if 'PEP8 files to check' not in x]
            self.assertTextEqual('\n'.join(result), expect1)
            expect2 = f'''
MiniTest.test_log(__main__) ... FAIL

Stderr:
TestPEP8.test_PEP8(gadget.ut) ... ok
TestPEP8.test_check_unittest_sha(gadget.ut) ... ok

======================================================================
FAIL: MiniTest.test_log(__main__)
----------------------------------------------------------------------
Traceback (most recent call last):
    self.fail("error")
AssertionError: error

Stdout:
INFO_message
DEBUG   : DEBUG_message

Stderr:

----------------------------------------------------------------------

FAILED (failures=1)
'''
            result = []
            for line in serr.split('\n'):
                if 'Ran 3 tests' in line:
                    continue
                if 'ResourceWarning:' in line:
                    continue
                if 'for handler in' in line:
                    continue
                if line.startswith('ok'):
                    continue
                if '/tmp/' in line:
                    continue
                if re.match(r'\s*~+\^+\s*$', line):
                    continue
                result.append(line)
            self.assertTextEqual('\n'.join(result), expect2)


class TestCase_methods(TestCase):

    def test___str__(self):
        # Coverage test for __str__

        # When -t option is assigned, there will be a timing info string in the begining of
        # self.__str__(), take care of this case so that the coverage will always pass.
        self.assertTrue(self.__str__().endswith('TestCase_methods.test___str__(__main__)'))

    def test_RegexpInList(self):
        res = ['abc', 'def', 'ghi']

        # pass case
        self.assertRegexpInList(res, ['de.*', '.*gh'])
        self.assertRegexpInList(res, ['abc', 'ghi'])
        self.assertRegexpInList(res, ['abc'])

        # fail case, check also outputs
        expect = """'ghix' is not found in expected list while keeping the order:
       FOUND : abc
       FOUND : def
   NOT FOUND : ghix"""
        with self.assertRaisesRegex(AssertionError, expect):
            with CaptureStdoutLog() as p:
                self.assertRegexpInList(res, ['abc', 'def', 'ghix'])

        expect = '''
==== Output lines:
FOUND 1: abc
FOUND 2: def
      3: ghi
'''
        self.assertTextEqual(p.getvalue(), expect)

        # last line is not found
        with self.assertRaises(AssertionError):
            self.assertRegexpInList(res, ['ghi', 'more'])

        # incorrect order
        with self.assertRaises(AssertionError):
            self.assertRegexpInList(res, ['def', 'abc'])

        # input list is empty
        with self.assertRaises(AssertionError):
            self.assertRegexpInList([], ['ghi', 'more'])

    def test_assertRegexpInDict(self):
        dict_obj = {'abc': '123', 'def': '456'}
        # passing case
        self.assertRegexpInDict(dict_obj, 'ab.', '12.')
        # failing case (key matches, value does not)
        with self.assertRaisesRegex(AssertionError, 'does not match any'):
            self.assertRegexpInDict(dict_obj, 'def', '12.')

    def test_assertRegexpEachList(self):
        ab = ['abc', 'adef', 'aghi']

        # pass case
        self.assertRegexpEachList(ab, [r'\w', r'\w+', r'a\w+'])
        self.assertRegexpEachList(['abc', 'adef', 'aghi', ''], ['abc', 'adef', r'\w+', ''])

        # length is not the same
        with self.assertRaisesRegex(AssertionError, 'Number of elements does not match'):
            self.assertRegexpEachList(ab, [r'\w', r'\w+'])

        # fail case
        with self.assertRaisesRegex(AssertionError, 'failed regex'):
            self.assertRegexpEachList(ab, [r'\w', r'\w+', r'q\w+'])

    def test_assertItemsEqual(self):
        # passing case: same list, same order
        self.assertItemsEqual(['1', '2', '3'], ['1', '2', '3'])
        # passing case: same list, different order
        self.assertItemsEqual(['1', '2', '3'], ['2', '3', '1'])
        # passing case: list inside the list
        self.assertItemsEqual(['a', ['a'], ['b']], [['a'], ['b'], 'a'])

        # failing case: item in second but not first
        with self.assertRaisesRegex(AssertionError, 'items in second but not first'):
            self.assertItemsEqual(['1', '2'], ['1', '2', '3'])

        # failing case: item in first but not second
        with self.assertRaisesRegex(AssertionError, 'item in first but not second'):
            self.assertItemsEqual(['1', '2', '3'], ['1', '2', '4'])
        # failing case: different content
        with self.assertRaisesRegex(AssertionError, 'List 1 has extra element'):
            self.assertItemsEqual(['1', '2', '2'], ['1', '2', '4'])
        with self.assertRaisesRegex(AssertionError, 'List 1 has extra element'):
            self.assertItemsEqual([1, 1, 1, 2], [2, 2, 1, 1])
        with self.assertRaisesRegex(AssertionError, 'items in second but not first'):
            self.assertItemsEqual([1], [1, 1])
        with self.assertRaisesRegex(AssertionError, 'has extra element: 1'):
            self.assertItemsEqual([1, 1], [1])

    def test_assertGoldEqual(self):
        with TempDir(name=True) as tdir:
            # pass case
            File(f'{tdir}/a').touch('abc')
            File(f'{tdir}/b').touch('abc')
            self.assertGoldEqual(f'{tdir}/a', f'{tdir}/b')

            # fail case
            File(f'{tdir}/c').touch('abc1')
            with self.assertRaisesRegex(AssertionError, 'Check diff and update gold file if needed'):
                self.assertGoldEqual(f'{tdir}/a', f'{tdir}/c')

            # Compare file is created
            self.assertGoldEqual(f'{tdir}/a', f'{tdir}/c.compare')

            # Run again
            with self.assertRaisesRegex(AssertionError, 'Check diff and update gold file if needed'):
                self.assertGoldEqual(f'{tdir}/a', f'{tdir}/c')
            self.assertGoldEqual(f'{tdir}/a', f'{tdir}/c.compare')
            self.assertEqual(set(os.listdir(tdir)), {'b', 'c.compare', 'c', 'a'})

    def test_assertTextEqual(self):
        text1 = "a\nb\nc\n"
        text2 = "a\nb1\nc\n"

        # pass case
        self.assertTextEqual(text1, text1)

        # fail case
        with self.assertRaisesRegex(AssertionError, r'b\s+\|\s+b1'):
            self.assertTextEqual(text1, text2)

        # fail case windows
        with MockVar(gadget.ut, "IS_UNIX", False):
            with self.assertRaisesRegex(AssertionError, r'b\s+\|\s+b1'):
                self.assertTextEqual(text1, text2)

        # with spaces
        text1 = "a\n   \nb   \nc\n"
        text2 = "a\n\nb\nc\n"
        self.assertTextEqual(text1, text2)
        self.assertTextEqual(text1, text1)

        # readability
        expect = '''
line
'''
        self.assertTextEqual('line', expect)
        self.assertTextEqual('line\n', expect)
        self.assertTextEqual('\nline', expect)
        self.assertTextEqual('\nline\n', expect)

    def test_assertPartialText(self):
        text1 = "a\nb\nc\n"

        # pass case
        self.assertPartialText(text1, 'b\nc')

        # fail case
        with self.assertRaisesRegex(AssertionError, 'Expected Text does not exist'):
            self.assertPartialText(text1, 'b\nd')

    def test_assertXpathEqual(self):
        self.assertXpathEqual('/intel', '/intel')
        with self.assertRaisesRegex(AssertionError, " != "):
            self.assertXpathEqual('/intel', '/intelx')

    def test_create_patch1(self):   # must be named patch1
        # patch worked
        a = self.create_patch("os.path.getatime")
        with TempDir(name=True) as tdir:
            self.assertTrue(isinstance(os.path.getatime('argme'), Mock))
        a.assert_called_with('argme')

    def test_create_patch2(self):   # must be named patch2 (same as above, with number 2)
        # patch must not be applied / returned back from patch1
        with TempDir(name=True) as tdir:
            self.assertTrue(isinstance(os.path.getatime(tdir), float))

    def test_create_patch3(self):
        # patch with arg, do not assign to variable
        self.create_patch("os.path.getatime", Mock(return_value="testme"))
        with TempDir(name=True) as tdir:
            self.assertEqual(os.path.getatime(tdir), "testme")

    def test_create_patch4(self):
        # patch must not be applied / returned back from patch3
        with TempDir(name=True) as tdir:
            self.assertTrue(isinstance(os.path.getatime(tdir), float))


class TestTestPEP8(TestCase):

    @unittest.skip("This SHOULD be skipped!")
    def test_skip(self):
        self.fail("ooops")

    @unittest.skipIf(False, "This is not skipped!")
    def test_skipIf(self):
        pass

    @unittest.skipUnless(True, "This is not skipped!")
    def test_skipUnless(self):
        pass

    @unittest.expectedFailure
    def test_expectedFailure(self):
        self.fail("ooops")

    def test_get_files(self):
        self.assertTrue(True)
        with TempDir(name=True) as tdir:
            ufile = os.path.join(tdir, "test_no_library.py")
            File(ufile).touch()
            self.assertEqual(TestPEP8._get_files(ufile), [ufile])

    def test_get_files_skip_list_mock(self):
        fake_file = '/tmp/some/path/test_skip.py'
        with MockVar(gadget.ut.re, "search", Mock(return_value=True)):
            self.assertEqual(TestPEP8._get_files(fake_file), [fake_file])

    def test_do_pep8_checks(self):
        with TempDir(name=True) as tdir:
            mkdirs(os.path.join(tdir, 'library', 'test'))
            ufile = os.path.join(tdir, 'library', 'test', 'test_abc.py')
            File(ufile).touch("""\
x=1
y= 2
""")

            self.assertEqual(len(TestPEP8._do_pep8_checks(ufile)), 2)

            # Collects errors from test_abc.py as well as the module file abc.py
            mfile = os.path.join(tdir, 'library', "abc.py")
            File(mfile).touch("""\
a= 3
b = 4
""")
            self.assertEqual(len(TestPEP8._do_pep8_checks(ufile)), 3)

            # Skip no pep8 pragma
            File(mfile).unlink()
            File(mfile).touch(r'''\
def foo(x, y):
    """
    Docstring with a escape \w
    """
    print "x, y"
    z=x+y  # pragma: no pep8
    print z
''')
            self.assertEqual(len(TestPEP8._do_pep8_checks(ufile)), 2)

            # Ensure that pragmas can only skip certain errors
            File(mfile).unlink()
            File(mfile).touch(r'''\
def foo1(x, y):
    """
    Docstring
    """
    print "x, y"
    z=x+y  # pragma: no pep8
    a[1]   = b   # pragma: no pep8 E221
    a[21]  =   c  # pragma: no pep8 E221
    a[3]   =   d  # pragma: no pep8 E221,E222
    print z
''')
            # Should now be clean: a[1]   = b
            # Still has an error:  a[21]  =   c
            # All errors filtered: a[3]   =   d
            errors = TestPEP8._do_pep8_checks(ufile)
            self.assertEqual(len(errors), 3)  # 2 from ufile, 1 after filtering PEP8 codes = 3 violations
            # Clean Test for coverage!
            File(ufile).unlink()
            File(mfile).unlink()
            File(ufile).touch("x = 1\n")
            self.assertEqual(len(TestPEP8._do_pep8_checks(ufile)), 0)

    def test_do_pep8_checks_empty_file_list(self):
        with MockVar(TestPEP8, "_get_files", Mock(return_value=[])):
            result = TestPEP8._do_pep8_checks(__file__)
        self.assertEqual(result, [])

    def test_do_checkenv(self):
        tester = _TestPEP8()
        fake_get_bin = Mock(return_value="/tmp/library/bin/foo.py")
        fake_check_file = Mock(return_value="success99")
        with MockVar(_TestPEP8, "get_bin_module", fake_get_bin), \
                MockVar(_TestPEP8, "check_file", fake_check_file):
            tester.do_checkenv()

        fake_get_bin.assert_called_once_with()
        fake_check_file.assert_called_once_with("/tmp/library/bin/foo.py")

    def test_build_info(self):
        # Test info creation
        pep8_results = []
        expected = "PEP8 Passed!"
        self.assertEqual(TestPEP8._build_info_string(pep8_results), expected)

        pep8_results.append(('path/file.py', 'x =1\n', 1, 3, 'E225', 'missing whitespace around operator'))
        info = TestPEP8._build_info_string(pep8_results)
        self.assertIn('You have 1 PEP8 Violation(s):', info)

    def test_checkenv(self):
        from gadget.ut import _TestPEP8

        # bin file
        with MockVar(_TestPEP8, "_get_files", Mock(return_value=['/tmp/library/bin/abc.py',
                                                                 '/tmp/library/bin/test/test_abc.py'])):
            self.assertEqual(_TestPEP8.get_bin_module(), '/tmp/library/bin/abc.py')

        # not a bin file
        with MockVar(_TestPEP8, "_get_files", Mock(return_value=['/tmp/library/veplib/abc.py',
                                                                 '/tmp/library/veplib/test/test_abc.py'])):
            self.assertEqual(_TestPEP8.get_bin_module(), '')

        with TempDir(name=True) as tdir:
            # checkfile - pass case
            text = """
import sys      # special file
    import time # non-indent zero
# import time   # commented

import checkenv
import os
            """
            File(join(tdir, 'a.py')).touch(text, newfile=True)
            # the imports in this example should fail in py3 (import time is the first seen, no exception)
            self.assertIn('as the first import', TestPEP8.check_file(join(tdir, 'a.py')))

            # checkfile - fail case
            text = """
import os
import checkenv
            """
            File(join(tdir, 'a.py')).touch(text, newfile=True)
            self.assertIn('as the first import', TestPEP8.check_file(join(tdir, 'a.py')))

            # checkfile - fail case
            text = """
from os import path
import checkenv
            """
            File(join(tdir, 'a.py')).touch(text, newfile=True)
            self.assertIn('as the first import', TestPEP8.check_file(join(tdir, 'a.py')))

            # checkfile - ignore file
            File(join(tdir, 'getimports.py')).touch(text, newfile=True)
            self.assertEqual(TestPEP8.check_file(join(tdir, 'getimports.py')), 'success1')

            # checkfile - pass case - no imports
            text = """
# just a comment
            """
            File(join(tdir, 'a.py')).touch(text, newfile=True)
            self.assertEqual(TestPEP8.check_file(join(tdir, 'a.py')), 'success3')

            # checkfile - pass case - empty
            text = """
# just a comment
            """
            File(join(tdir, 'a.py')).touch(text, newfile=True)
            self.assertEqual(TestPEP8.check_file(''), 'success0')

            # checks the only apply in py3
            # py3 passing case: import checkenv is encased in a try/except
            text = """
try:
    from bin import checkenv
except BaseException:
    import checkenv    # for no PYTHONPATH
"""
            File(join(tdir, 'a.py')).touch(text, newfile=True)
            self.assertEqual(TestPEP8.check_file(join(tdir, 'a.py')), 'success2_py3')

            # py3 failing case: import checkenv is after import
            text = """
try:
    import gadget.strmore
    from bin import checkenv
except BaseException:
    import checkenv    # for no PYTHONPATH
"""
            File(join(tdir, 'a.py')).touch(text, newfile=True)
            self.assertIn('as the first', TestPEP8.check_file(join(tdir, 'a.py')))

    def test_dupname(self):
        # case1 - fail case
        with TempDir(chdir=True):
            File('a.py').touch('''
class AA:
    def %s(a):
         pass
    def %s(b):
         pass
''' % ('test_foo1', 'test_foo1'))
            self.assertEqual(TestPEP8.do_duplicate_testname('a.py'), 'test_foo1')

            # case2 - fail case with embedded class
            File('c.py').touch('''
class AA:
    def %s(a):
        class CC:
             pass
    def %s(b):
         pass
''' % ('test_foo1', 'test_foo1'))
            self.assertEqual(TestPEP8.do_duplicate_testname('c.py'), 'test_foo1')

            # case3 - pass case
            File('b.py').touch('''
class AA:
    def %s(a):
         pass
class BB:
    def %s(b):
         pass
''' % ('foo1', 'foo1'))
            self.assertEqual(TestPEP8.do_duplicate_testname('b.py'), None)

            # case4 - comment lines are ignored by the parser
            File('d.py').touch('''
# def test_shadow():
class AA:
    def test_unique(self):
        pass
''')
            self.assertIsNone(TestPEP8.do_duplicate_testname('d.py'))


class Mock_all_method_test(TestCase):
    def test_class(self):
        with MockVar(gadget.ut, "UT_Options", mock_all_methods(UT_Options, 12344)):
            a = gadget.ut.UT_Options()
            self.assertEqual(a.set_option(), 12344)

    def test_instantiated(self):
        with MockVar(gadget.ut, "is_ut_option", mock_all_methods(is_ut_option, 12355)):
            self.assertEqual(gadget.ut.is_ut_option.set_option(), 12355)


class exe1:
    """test class for BreakAt"""

    def __init__(self):
        self.var = 0
        print("I am init")
        self.foores = self.foo(1)

    def foo(self, cnt):
        self.var += cnt
        print("I am foo", self.var)
        return self.var


class BreakAtTest(TestCase):

    def test_count_0(self):
        with BreakAt(exe1, "foo", count=0) as v:
            with self.assertRaises(BreakPoint):
                var = True
                exe1()
                var = False    # should not be reached
            self.assertEqual(v.result, "Method not executed")
            self.assertTrue(var)

        # confirm that original is back
        self.assertEqual(exe1().foo(1), 2)

    def test_count_1_default(self):
        with BreakAt(exe1, "foo") as v:     # default
            with self.assertRaises(BreakPoint):
                var = True
                exe1()
                var = False    # should not be reached
            self.assertEqual(v.result, 1)
            self.assertTrue(var)

    def test_count_2(self):
        with BreakAt(exe1, "foo", count=2) as v:     # default
            with self.assertRaises(BreakPoint):
                obj = exe1()
                var = True
                obj.foo(5)
                var = False    # should not be reached
            self.assertEqual(v.result, 6)
            self.assertEqual(obj.foores, 1)
            self.assertTrue(var)

    def test_count_3(self):
        with BreakAt(exe1, "foo", count=3) as v:     # default
            with self.assertRaises(BreakPoint):
                exe1()
                exe1()
                var = True
                exe1()
                var = False    # should not be reached
            self.assertEqual(v.result, 1)
            self.assertTrue(var)

    def test_no_attribute(self):
        with self.assertRaisesRegex(Exception, "does not have"):
            with BreakAt(exe1, "foo1", count=3) as v:     # default
                pass


class CronDirTest(TestCase):
    def test_basic(self):
        res1 = crondir()
        res2 = crondir()
        self.assertNotEqual(res1, res2)
        self.assertTrue(isdir(res1))
        self.assertTrue(isdir(res2))


class TimeItTest(TestCase):
    def test_basic_no_display(self):
        ut1 = time_the_test.__class__()

        ut1.is_timer_enabled = False
        self.assertEqual(ut1.timer_string("somename"), "")
        with MockVar(sys, "stdout", StringIO()) as p:
            ut1.timer_print()
        self.assertEqual(p.getvalue(), "")  # empty

    def test_basic(self):
        ut1 = time_the_test.__class__()

        ut1.is_timer_enabled = True
        self.assertRegex(ut1.timer_string("somename"), 'Timeit: Bootup')
        with MockVar(sys, "stdout", StringIO()) as p:
            ut1.timer_print()
        self.assertRegexpEachList(p.getvalue().split('\n'),
                                  ['',
                                   'Timeit log per test',
                                   r'\[[\d\.]+ Secs\]: Timeit:',
                                   r'\[[\d\.]+ Secs\]: Timeit:',
                                   ''])
        ut1.is_timer_enabled = False     # Do not display summary

    def test_check_args(self):
        with MockVar(time_the_test, "is_timer_enabled", True):
            # no args
            with MockVar(sys, "argv", "test.py".split()):
                time_the_test.check_args()
                self.assertEqual(sys.argv, ['test.py', '-v'])

            # with -v
            with MockVar(sys, "argv", "test.py -v".split()):
                time_the_test.check_args()
                self.assertEqual(sys.argv, ['test.py', '-v'])

            # with -t -v
            with MockVar(sys, "argv", "test.py -t -v".split()):
                time_the_test.check_args()
                self.assertEqual(sys.argv, ['test.py', '-t', '-v'])

            # with -t
            with MockVar(sys, "argv", "test.py -t".split()):
                time_the_test.check_args()
                self.assertEqual(sys.argv, ['test.py', '-v', '-t'])

            # with -t
            with MockVar(sys, "argv", "test.py -t testme".split()):
                time_the_test.check_args()
                self.assertEqual(sys.argv, ['test.py', '-v', '-t', 'testme'])

        with MockVar(time_the_test, "is_timer_enabled", False):
            # no args
            with MockVar(sys, "argv", "test.py".split()):
                time_the_test.check_args()
                self.assertEqual(sys.argv, ['test.py'])

            # with -t
            with MockVar(sys, "argv", "test.py -t".split()):
                time_the_test.check_args()
                self.assertEqual(sys.argv, ['test.py', '-t'])


class Trim_traceback_without_code_test(TestCase):
    def test_remove_single_code_and_caret_line(self):
        tb = """
Traceback (most recent call last):
  File "t.py", line 3, in <module>
    1/0
    ^
ZeroDivisionError: division by zero
"""
        expected = """
Traceback (most recent call last):
  File "t.py", line 3, in <module>
ZeroDivisionError: division by zero
"""
        self.assertTextEqual('\n'.join(trim_traceback_without_code(tb)), expected)

    def test_remove_standalone_caret_line(self):
        tb = """
Traceback (most recent call last):
    ^^^^^
  File "t.py", line 1, in <module>
ValueError: bad
"""
        expected = """
Traceback (most recent call last):
  File "t.py", line 1, in <module>
ValueError: bad
"""
        self.assertTextEqual('\n'.join(trim_traceback_without_code(tb)), expected)

    def test_multiple_frames_and_caret_pairs(self):
        tb = """
Traceback (most recent call last):
  File "a.py", line 10, in <module>
    main()
    ^^^^^^
  File "a.py", line 6, in main
    1/0
      ^
ZeroDivisionError: division by zero
"""
        expected = """
Traceback (most recent call last):
  File "a.py", line 10, in <module>
  File "a.py", line 6, in main
ZeroDivisionError: division by zero
"""
        self.assertTextEqual('\n'.join(trim_traceback_without_code(tb)), expected)

    def test_no_code_no_caret_should_remain_same(self):
        tb = """
Traceback (most recent call last):
  File "x.py", line 1, in <module>
RuntimeError: boom
"""
        self.assertTextEqual('\n'.join(trim_traceback_without_code(tb)), tb)

    def test_cover_standalone_caret_continue_branch(self):
        tb = """
Traceback (most recent call last):
some header line
  ^^^^^^^
ValueError: boom
"""
        expected = """
Traceback (most recent call last):
some header line
ValueError: boom
"""
        self.assertTextEqual('\n'.join(trim_traceback_without_code(tb)), expected)


if __name__ == "__main__":
    unittest.main()
