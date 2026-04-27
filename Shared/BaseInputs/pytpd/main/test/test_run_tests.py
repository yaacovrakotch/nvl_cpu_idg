#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for run_tests.py
"""
from setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option
from main.run_tests import *
from setenv_unittest import ROOT_ENV    # must be after run_tests!
from gadget.gizmo import MockVar
from gadget.helperclass import CaptureStdout
from gadget.files import TempDir, File
from gadget.shell import IS_UNIX, IS_WIN
from gadget.disk import mkdirs
from os.path import join
import sys
import os
import main.run_tests as rt


class TestAssert(TestCase):

    def test_proc_py_line(self):
        self.assertEqual(Assertize._proc_py_line(['    assert abc, f"ghi"'], 0),
                         ('    ', 'abc', '(f"ghi")'))
        self.assertEqual(Assertize._proc_py_line(['    oops abc, "ghi"'], 0),
                         (None, None, None))
        self.assertEqual(Assertize._proc_py_line(['    assert type(x, y)'], 0),
                         (None, None, None))
        self.assertEqual(Assertize._proc_py_line(['    assert abc, ("ghi")'], 0),
                         ('    ', 'abc', '("ghi")'))
        self.assertEqual(Assertize._proc_py_line(['    assert instance(a, b), "ghi"'], 0),
                         ('    ', 'instance(a, b)', '("ghi")'))
        self.assertEqual(Assertize._proc_py_line(['    assert "," in a, "ghi"'], 0),
                         ('    ', '"," in a', '("ghi")'))
        self.assertEqual(Assertize._proc_py_line(['    assert "," in a, ("ghi"',
                                                  '   "x"',
                                                  '   "z")'], 0),
                         ('    ', '"," in a', '("ghi"\n   "x"\n   "z")'))

    def test_proc_ternary(self):
        self.assertEqual(Assertize._proc_ternary('    abc = 26 if ut1 else 27', 1),
                         ['    if ut1:    # line#1',
                          '        abc = 26',
                          '    else:',
                          '        abc = 27'])
        self.assertEqual(Assertize._proc_ternary('    abc = 26', 1), [])
        self.assertEqual(Assertize._proc_ternary('    abc= 26 if ut1 else 27', 1), [])
        self.assertEqual(Assertize._proc_ternary('    abc = {26 if ut1 else 27}', 1), [])

    def test_assert_run(self):
        with TempDir(name=True, delete=True) as tdir, \
                TempDir(name=True, delete=True) as tdir_out:
            code = '''
assert True, (f'hello'
              'there')
    assert False, 'hello'
assert isinstance(x, y), 'yeah'
assert isinstance(x, y)
    abc = 'hi' if self.some else 'comp'
'''
            File(join(tdir, 'a.py')).touch(code)
            File(join(tdir, 'a.txt')).touch(code)
            File(join(tdir, '.git/a.txt')).touch(code, mkdir=True)
            File(join(tdir, 'a.pyc')).touch(code)

            cmd = f'run_tests.py -assert {tdir_out}'
            with MockVar(sys, "argv", cmd.split()), \
                    MockVar(rt, "ROOT_ENV", tdir), \
                    self.assertRaises(SystemExit):
                RunTests().main()

            expect = '''
_dum = (f'hello'
              'there')   # line#1
assert True, (f'hello'
              'there')
    _dum = ('hello')   # line#3
    assert False, 'hello'
_dum = ('yeah')   # line#4
assert isinstance(x, y), 'yeah'
assert isinstance(x, y)
    if self.some:    # line#6
        abc = 'hi'
    else:
        abc = 'comp' '''
            self.assertTextEqual(File(f'{tdir_out}/a.py').read(), expect)
            self.assertTextEqual(File(f'{tdir_out}/a.txt').read(), code)
            self.assertEqual(set(os.listdir(tdir_out)), {'a.txt', 'a.py'})


class TestRun(TestCase):

    def test_basic_nt(self):
        with TempDir(name=True, delete=True) as tdir:

            # Passing test
            cmd = ["%s/main/run_tests.py" % tdir, '-f', '-nt']

            with MockVar(sys, "argv", cmd):
                RunTests.root = tdir
                code = '''#!%s
import sys
sys.path.append('%s')
from gadget.ut import TestCase, unittest


class RunTest(TestCase):
    def test_basic(self):
        self.assertEqual(1, 1)


unittest.main()
''' % (sys.executable, ROOT_ENV)
                File(os.path.join(tdir, 'main/test/test_run_test.py')).touch(code, mkdir=True).chmod("02770")
                with CaptureStdout() as p:
                    RunTests().main()
                self.assertIn("Success! no fails.", p.getvalue())

            # Failing test
            cmd = ["%s/main/run_tests.py" % tdir, '-f', '-nt', '-show']
            with MockVar(sys, "argv", cmd):
                code = '''#!%s
import sys
sys.path.append('%s')
from gadget.ut import TestCase, unittest


class RunTest(TestCase):
    def test_basic(self):
        self.fail("fail")


unittest.main()
''' % (sys.executable, ROOT_ENV)
                File(os.path.join(tdir, 'main/test/test_run_test.py')).touch(code, newfile=True).chmod("02770")
                with CaptureStdout() as p, self.assertRaises(SystemExit):
                    RunTests().main()
                print(p.getvalue())
                self.assertIn('Fail tests: 1', p.getvalue())
                self.assertIn('======= test_run_test', p.getvalue())

    @unittest.skipIf(IS_WIN, 'unix only bgcmd')
    def test_basic_parallel(self):
        with TempDir(name=True, delete=True) as tdir:

            # Passing test
            RunTests.root = tdir
            code = '''#!%s
import sys
sys.path.append('%s')
from gadget.ut import TestCase, unittest


class RunTest(TestCase):
    def test_basic(self):
        self.assertEqual(1, 1)


unittest.main()
''' % (sys.executable, ROOT_ENV)
            File(os.path.join(tdir, 'main/test/test_abc1.py')).touch(code, mkdir=True).chmod("02770")

            # Failing test
            code = '''#!%s
import sys
sys.path.append('%s')
from gadget.ut import TestCase, unittest


class RunTest(TestCase):
    def test_basic(self):
        self.fail("fail")


unittest.main()
''' % (sys.executable, ROOT_ENV)
            File(os.path.join(tdir, 'main/test/test_abc2.py')).touch(code, newfile=True).chmod("02770")

            cmd = ["%s/main/run_tests.py" % tdir, '-f']
            with MockVar(sys, "argv", cmd), MockVar(RunTests, 'ncpu', 1):
                with CaptureStdout() as p, self.assertRaises(SystemExit):
                    RunTests().main()
                print(p.getvalue())
                self.assertIn('Fail tests: 1', p.getvalue())
                expect = ['Fail tests: 1 - ',
                          'Starting unittest runs... logdir:',
                          r"main/test/test_abc1.py \s+[23] tests, \S+\s+ Secs, OK",
                          r"main/test/test_abc2.py \s+[23] tests, \S+\s+ Secs, FAILED \(failures=1\)",
                          ]
                output = [x for x in sorted(p.getvalue().split('\n')) if 'Waiting for' not in x and ' is done' not in x and x]
                print('\n'.join(output))
                self.assertRegexpEachList(output, expect)

    @unittest.skipIf(IS_WIN, 'unix only bgcmd')
    def test_1_core(self, cores=1):
        # Needed for coverage
        with TempDir(name=True, delete=True) as tdir:
            RunTests.root = tdir

            # 2 sec test
            code = '''#!%s
import sys
sys.path.append('%s')
from gadget.ut import TestCase, unittest
import time


class RunTest(TestCase):
    def test_basic(self):
        time.sleep(2)
        self.assertEqual(1, 1)


unittest.main()
''' % (sys.executable, ROOT_ENV)
            File(os.path.join(tdir, 'main/test/test_abc2.py')).touch(code, mkdir=True).chmod("02770")

            # 1 sec test
            code = '''#!%s
import sys
sys.path.append('%s')
from gadget.ut import TestCase, unittest
import time


class RunTest(TestCase):
    def test_basic(self):
        time.sleep(1)
        self.assertEqual(1, 1)


unittest.main()
''' % (sys.executable, ROOT_ENV)
            File(os.path.join(tdir, 'main/test/test_abc1.py')).touch(code, mkdir=True).chmod("02770")

            # 0 sec test
            code = '''#!%s
import sys
sys.path.append('%s')
from gadget.ut import TestCase, unittest


class RunTest(TestCase):
    def test_basic(self):
        self.assertEqual(1, 1)


unittest.main()
''' % (sys.executable, ROOT_ENV)
            File(os.path.join(tdir, 'main/test/test_abc0.py')).touch(code, mkdir=True).chmod("02770")

            cmd = ["%s/main/run_tests.py" % tdir, '-f']
            with MockVar(sys, "argv", cmd), MockVar(RunTests, 'ncpu', cores):
                with CaptureStdout() as p:
                    RunTests().main()
                print(p.getvalue())
                self.assertIn("Success! no fails.", p.getvalue())

    @unittest.skipIf(IS_WIN, 'unix only bgcmd')
    def test_9_core(self):
        self.test_1_core(cores=9)   # There are 3 tests, and use all cores

    @unittest.skipIf(*is_ut_option('SKIP_NIGHTLY_BUILD', message='due to mtl env', neg=False))
    def test_basic_cov(self):
        cmd = f"{ROOT_ENV}/main/run_tests.py -c -gadget -ut -nt".split()

        with MockVar(sys, "argv", cmd), MockVar(RunTests, "root", ROOT_ENV):
            with CaptureStdout() as p:
                RunTests().main()

            print(p.getvalue())
            self.assertIn("Coverage: 75%", p.getvalue())
            self.assertIn("Success! no fails.", p.getvalue())

    def test_execute_test(self):
        # test one successful real unittest run
        with MockVar(sys, "argv", ["/run_tests.py"]):
            rts = RunTests()
        root = dirname(dirname(dirname(realpath(sys.argv[0]))))
        with CaptureStdout() as p:
            result = rts.execute_test(os.path.join(root, 'gadget', 'test', 'test_strmore.py'), root)
        self.assertEqual(result, False)
        self.assertIn('tests, OK', p.getvalue())

        result = rts.execute_test(os.path.join(root, 'gadget', 'test', 'test_strmore.py'), root)
        self.assertEqual(result, False)

    def test_parse_ut_info(self):
        out = """
Unittest_args.test_print(__main__) ... ok
Unittest_args.test_s(__main__) ... ok
Unittest_args.test_s_and_o(__main__) ... ok

----------------------------------------------------------------------
Ran 46 tests in 7.382s

OK (skipped=2, expected failures=1)
"""
        result = RunTests._parse_ut_info(out)
        self.assertEqual(result, (46, 7.382, False, 'OK (skipped=2, expected failures=1)'))

        out = """
TestPEP8.test_PEP8(gadget.ut) ... ok
TestPatternHeader.test_CreatePinHeader(__main__) ... ok
TestPatternHeader.test_getHeaderString(__main__) ... ok

======================================================================
FAIL: StrTests.test_nsplit(__main__)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "gadget/test/test_strmore.py", line 35, in test_nsplit
    self.fail('abc')
AssertionError: abc

----------------------------------------------------------------------
Ran 60 tests in 0.428s

FAILED (failures=1)
"""
        result = RunTests._parse_ut_info(out)
        self.assertEqual(result, (60, 0.428, True, 'FAILED (failures=1) '))

    def test_files_to_test(self):
        inp = ['/path/mod/test/test_a.py',
               '/path/gadget/test/test_tputil.py',
               '/path/gadget/test/test_shell.py',
               '/path/tp/test/test_tp.py',
               '/path/main/test/test_simple_ut.py',
               ]
        exp = ['/path/mod/test/test_a.py',
               '/path/gadget/test/test_tputil.py',
               '/path/tp/test/test_tp.py',
               '/path/main/test/test_simple_ut.py',
               ]

        with MockVar(OPT, 'gadget', False):
            self.assertEqual(list(RunTests.files_to_test(inp)), exp)
        with MockVar(OPT, 'gadget', True):
            self.assertEqual(list(RunTests.files_to_test(inp)), inp)
        with MockVar(OPT, 'ut', True):
            self.assertEqual(list(RunTests.files_to_test(inp)), ['/path/main/test/test_simple_ut.py'])

    def test_cmd(self):
        # default
        with MockVar(sys, "argv", 'script.py'.split()):
            rts = RunTests()
            self.assertEqual(rts.get_cmd('a.py').split()[1:], 'a.py -v -b -a -s'.split())

        # fast
        with MockVar(sys, "argv", 'script.py -f'.split()):
            rts = RunTests()
            self.assertEqual(rts.get_cmd('a.py').split()[1:], 'a.py -v -b -a'.split())

        # coverage
        with MockVar(sys, "argv", 'script.py -c'.split()):
            rts = RunTests()
            self.assertEqual(rts.get_cmd('a.py').split()[1:], 'text a.py -v -b'.split())

        with MockVar(sys, "argv", 'script.py'.split()), MockVar(rt, 'EXIST_PDX_I_DRIVE', True):
            rts = RunTests()
            cmd = rts.get_cmd('test_sort_class_tp_diff.py')
            self.assertEqual(cmd.split(), 'test_sort_class_tp_diff.py -v -b -a -s'.split())

    def test_get_pr_modified_files(self):
        """Tests getting a list of the files modified in a PR"""
        with MockVar(sys, "argv", 'script.py'.split()):
            rts = RunTests()

        # Mock GitHub.get_modfiles() to return sample modified files
        mock_files = [
            'pymtpl/binctr.py',
            'gadget/strmore.py',
            'main/run_tests.py',
            'README.md',  # Non-Python file
            'tp/testprogram.py'
        ]

        with MockVar(GitHub, 'get_modfiles', lambda self: mock_files):
            result = rts.get_pr_modified_files()

        # Should only return Python files
        expected = {
            'pymtpl/binctr.py',
            'gadget/strmore.py',
            'main/run_tests.py',
            'tp/testprogram.py'
        }
        self.assertEqual(result, expected)

    def test_derive_mainpy(self):
        with TempDir(name=True, delete=True) as tdir, \
                MockVar(sys, "argv", 'script.py'.split()):

            RunTests.root = tdir
            rts = RunTests()

            binctr_source = join(tdir, 'pymtpl/binctr.py')
            binctr_test = join(tdir, 'pymtpl/test/test_binctr.py')

            # Create directory structure and test files
            File(binctr_source).touch('# source', mkdir=True)
            File(binctr_test).touch('# test', mkdir=True)

            # Test 1: Valid test file
            result = rts._derive_mainpy(binctr_test)
            self.assertEqual(result, os.path.normpath(binctr_source))

            # Test 2: File not starting with test_
            result = rts._derive_mainpy('pymtpl/tests/tests_binctr.py')
            self.assertEqual(result, None)

            # Test 3: test file not starting with test_
            result = rts._derive_mainpy('pymtpl/test/test_binctr/binctr.py')
            self.assertEqual(result, None)

    def test_get_pr_modified_files_error(self):
        """
        Tests getting a list of the files modified in a PR
        But throw an error as no matches found
        """
        with MockVar(sys, "argv", 'script.py'.split()):
            rts = RunTests()

        # Mock GitHub.get_modfiles() to return sample modified files
        mock_files = [
            'pymtpl/binctr.',
        ]

        def mock_raise_error(self):
            raise Exception("API Error")

        with MockVar(GitHub, 'get_modfiles', mock_raise_error):
            with CaptureStdout() as p:
                result = rts.get_pr_modified_files()

        self.assertIn('Warning: Could not get PR modified files', p.getvalue())

    def test_get_tests_for_modified_files(self):
        """Test mapping modified files to test files"""
        with TempDir(name=True, delete=True) as tdir, \
                MockVar(sys, "argv", 'script.py'.split()):

            RunTests.root = tdir
            rts = RunTests()

            # Create directory structure and test files
            File(join(tdir, 'pymtpl/binctr.py')).touch('# source', mkdir=True)
            File(join(tdir, 'pymtpl/test/test_binctr.py')).touch('# test', mkdir=True)

            File(join(tdir, 'gadget/strmore.py')).touch('# source', mkdir=True)
            File(join(tdir, 'gadget/test/test_strmore.py')).touch('# test', mkdir=True)
            File(join(tdir, 'gadget/test/test_files.py')).touch('# test', mkdir=True)

            File(join(tdir, 'main/newfile.py')).touch('# source', mkdir=True)
            # No corresponding test file for newfile.py

            File(join(tdir, 'tp/test/test_direct.py')).touch('# test', mkdir=True)

            # Test 1: Direct test file
            modified = ['tp/test/test_direct.py']
            result = rts.get_tests_for_modified_files(modified)
            self.assertEqual(result, [join(tdir, 'tp/test/test_direct.py')])

            # Test 2: Source file with corresponding test
            modified = ['pymtpl/binctr.py']
            result = rts.get_tests_for_modified_files(modified)
            self.assertEqual(result, [join(tdir, 'pymtpl', 'test', 'test_binctr.py')])

            # Test 3: Source file without direct test (should add all tests in dir)
            modified = ['gadget/strmore.py']
            with CaptureStdout() as p:
                result = rts.get_tests_for_modified_files(modified)
            self.assertEqual(set(result), {
                join(tdir, 'gadget', 'test', 'test_strmore.py')
            })

            # Test 4: Multiple modified files
            modified = ['pymtpl/binctr.py', 'gadget/strmore.py']
            result = rts.get_tests_for_modified_files(modified)
            self.assertEqual(set(result), {
                join(tdir, 'pymtpl', 'test', 'test_binctr.py'),
                join(tdir, 'gadget', 'test', 'test_strmore.py')
            })

            # Test 5: File with no test directory (fallback)
            modified = ['main/newfile.py']
            result = rts.get_tests_for_modified_files(modified)
            self.assertEqual(result, [])

    def test_run_pr_coverage_with_failures(self):
        # Test coverage run with test failures
        with TempDir(name=True, delete=True) as tdir, \
                TempDir(name=True, delete=True) as logdir, \
                MockVar(sys, "argv", 'script.py -coverage'.split()):

            RunTests.root = tdir
            RunTests.log_dir = logdir
            rts = RunTests()

            # Create a failing test
            test_code = f'''#!{sys.executable}
    import sys
    sys.path.append('{ROOT_ENV}')
    from gadget.ut import TestCase, unittest


    class TestSample(TestCase):
        def test_fail(self):
            self.fail("Intentional failure")


    unittest.main()
    '''

            source_code = '''
    def sample_function():
        return 42
    '''

            File(join(tdir, 'pymtpl/sample.py')).touch(source_code, mkdir=True)
            File(join(tdir, 'pymtpl/test/test_sample.py')).touch(test_code, mkdir=True).chmod('02770')

            test_files = [join(tdir, 'pymtpl/test/test_sample.py')]
            modified_files = ['pymtpl/sample.py']

            # Mock SystemCall.run_outtxt to return failing test output
            def mock_run_outtxt(self):
                # Return mock output that looks like a failed test run
                mock_output = '''test_fail (__main__.TestSample) ... FAIL

======================================================================
FAIL: test_fail (__main__.TestSample)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/test_sample.py", line 8, in test_fail
    self.fail("Intentional failure")
AssertionError: Intentional failure

----------------------------------------------------------------------
Ran 1 test in 0.123s

FAILED (failures=1)

Coverage: 80% - 3 lines
Missing: 1
BrMiss: 0
'''
                return 0, mock_output

            # Mock gh pr view to return sample PR body
            def mock_gh_view(self):
                mock_body = '''### Why is this PR needed?
Test PR

<!-- COVERAGE_REPORT_START -->
### Coverage Report for Modified Files
_Coverage details will be automatically updated here by the CI workflow_
<!-- COVERAGE_REPORT_END -->
'''
                return 0, mock_body, ''

            # Mock gh pr edit command
            def mock_gh_edit(self):
                return 0, '', ''

            # Track which commands were called
            call_tracker = {'view_called': False, 'edit_called': False}

            def mock_run_sout_serr(self):
                # Check if 'pr' and 'view'/'edit' are in the command list
                if 'pr' in self.cmd and 'view' in self.cmd:
                    call_tracker['view_called'] = True
                    return mock_gh_view(self)
                elif 'pr' in self.cmd and 'edit' in self.cmd:
                    call_tracker['edit_called'] = True
                    return mock_gh_edit(self)
                return 0, '', ''

            with MockVar(SystemCall, 'run_outtxt', mock_run_outtxt), \
                    MockVar(SystemCall, 'run_sout_serr', mock_run_sout_serr), \
                    MockVar(GetCmd, 'gh_final', 'gh'), \
                    self.assertRaises(SystemExit) as cm:
                rts.run_pr_coverage(test_files, modified_files)

            # Should exit with code 1 due to test failure
            self.assertEqual(cm.exception.code, 1)

            # Verify PR description update was called
            self.assertTrue(call_tracker['view_called'], 'gh pr view should be called')
            self.assertTrue(call_tracker['edit_called'], 'gh pr edit should be called')

            # Check that PR description file was created
            pr_desc_file = join(logdir, 'pr_description.txt')
            self.assertTrue(os.path.exists(pr_desc_file))

            content = File(pr_desc_file).read()
            self.assertIn('Coverage Report for Modified Files', content)
            self.assertIn('<!-- COVERAGE_REPORT_START -->', content)
            self.assertIn('<!-- COVERAGE_REPORT_END -->', content)

    def test_run_pr_coverage_success(self):
        # Test successful coverage run with passing tests
        with TempDir(name=True, delete=True) as tdir, \
                TempDir(name=True, delete=True) as logdir, \
                MockVar(sys, "argv", 'script.py -coverage'.split()):

            RunTests.root = tdir
            RunTests.log_dir = logdir
            rts = RunTests()

            # Create a passing test
            test_code = f'''#!{sys.executable}
    import sys
    sys.path.append('{ROOT_ENV}')
    from gadget.ut import TestCase, unittest


    class TestSample(TestCase):
        def test_pass(self):
            self.assertEqual(1, 1)


    unittest.main()
    '''

            source_code = '''
    def sample_function():
        return 42
    '''

            File(join(tdir, 'gadget/simple.py')).touch(source_code, mkdir=True)
            File(join(tdir, 'gadget/test/test_simple.py')).touch(test_code, mkdir=True).chmod('02770')

            test_files = [join(tdir, 'gadget/test/test_simple.py')]
            modified_files = [os.path.normpath('gadget/simple.py')]

            # Mock SystemCall.run_outtxt to return successful test output
            original_run_outtxt = SystemCall.run_outtxt

            def mock_run_outtxt(self):
                # Return mock output that looks like a successful test run
                mock_output = '''test_pass (__main__.TestSample) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.123s

OK

Coverage: 100% - 3 lines
Missing: 0
BrMiss: 0
'''
                return 0, mock_output

            # Mock gh pr view to return sample PR body
            def mock_gh_view(self):
                mock_body = '''### Why is this PR needed?
Test PR

<!-- COVERAGE_REPORT_START -->
### Coverage Report for Modified Files
_Coverage details will be automatically updated here by the CI workflow_
<!-- COVERAGE_REPORT_END -->
'''
                return 0, mock_body, ''

            # Mock gh pr edit command
            def mock_gh_edit(self):
                return 0, '', ''

            def mock_run_sout_serr(self):
                if 'pr' in self.cmd and 'view' in self.cmd:
                    return mock_gh_view(self)
                elif 'pr' in self.cmd and 'edit' in self.cmd:
                    return mock_gh_edit(self)
                return 0, '', ''

            with MockVar(SystemCall, 'run_outtxt', mock_run_outtxt), \
                    MockVar(SystemCall, 'run_sout_serr', mock_run_sout_serr), \
                    CaptureStdout() as p:
                # Should NOT raise SystemExit for successful tests
                rts.run_pr_coverage(test_files, modified_files)

            output = p.getvalue()
            self.assertIn('Success! All tests passed', output)
            self.assertIn(os.path.normpath('gadget/simple.py'), output)

            # Check PR description file was created
            pr_desc_file = join(logdir, 'pr_description.txt')
            self.assertTrue(os.path.exists(pr_desc_file))
            content = File(pr_desc_file).read()
            self.assertIn('Coverage Report for Modified Files', content)
            self.assertIn('100%', content)

    def test_run_pr_coverage_with_invalid_coverage(self):
        with TempDir(name=True, delete=True) as tdir, \
                TempDir(name=True, delete=True) as logdir, \
                MockVar(sys, "argv", 'script.py -coverage'.split()):

            RunTests.root = tdir
            RunTests.log_dir = logdir
            rts = RunTests()

            test_code = f'''#!{sys.executable}
    import sys
    sys.path.append('{ROOT_ENV}')
    from gadget.ut import TestCase, unittest


    class TestSample(TestCase):
        def test_pass2(self):
            self.assertEqual(1, 1)


    unittest.main()
    '''

            source_code = '''
    def sample_function():
        return 42
    '''

            File(join(tdir, 'gadget/simple.py')).touch(source_code, mkdir=True)
            File(join(tdir, 'gadget/test/simple.py')).touch(test_code, mkdir=True).chmod('02770')

            test_files = [join(tdir, 'gadget/test/simple.py')]
            modified_files = [os.path.normpath('gadget/simple.py')]

            def mock_run_outtxt(self):
                # Return mock output that looks like a successful test run
                mock_output = '''test_pass2 (__main__.TestSample) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.123s

OK

Timeit log per test (sorted):
0.123 Secs: Timeit: TestSample.test_pass2
Missing Lines: 3-4
Missing: 0
BrMiss: 0
Coverage: abc - 3 lines

            '''
                return 0, mock_output

            def mock_gh_view(self):
                mock_body = '''### Why is this PR needed?
Test PR

<!-- COVERAGE_REPORT_START -->
### Coverage Report for Modified Files
_Coverage details will be automatically updated here by the CI workflow_
<!-- COVERAGE_REPORT_END -->
            '''
                return 0, mock_body, ''

            def mock_gh_edit(self):
                return 0, '', ''

            def mock_run_sout_serr(self):
                if 'pr' in self.cmd and 'view' in self.cmd:
                    return mock_gh_view(self)
                elif 'pr' in self.cmd and 'edit' in self.cmd:
                    return mock_gh_edit(self)
                return 0, '', ''

            with MockVar(SystemCall, 'run_outtxt', mock_run_outtxt), \
                    MockVar(SystemCall, 'run_sout_serr', mock_run_sout_serr), \
                    CaptureStdout() as p:
                # Should NOT raise SystemExit for successful tests
                rts.run_pr_coverage(test_files, modified_files)
            output = p.getvalue()
            self.assertIn('Success! All tests passed', output)
            self.assertIn(os.path.normpath('gadget/simple.py'), output)

            # Check PR description file was created
            pr_desc_file = join(logdir, 'pr_description.txt')
            self.assertTrue(os.path.exists(pr_desc_file))
            content = File(pr_desc_file).read()
            self.assertIn('No coverage data available', content)

    def test_run_pr_coverage_with_invalid_commit_sha(self):
        with TempDir(name=True, delete=True) as tdir, \
                TempDir(name=True, delete=True) as logdir, \
                MockVar(sys, "argv", 'script.py -coverage'.split()):

            RunTests.root = tdir
            RunTests.log_dir = logdir
            rts = RunTests()

            test_code = f'''#!{sys.executable}
    import sys
    sys.path.append('{ROOT_ENV}')
    from gadget.ut import TestCase, unittest


    class TestSample(TestCase):
        def test_pass3(self):
            self.assertEqual(1, 1)


    unittest.main()
    '''

            source_code = '''
    def sample_function():
        return 42
    '''

            File(join(tdir, 'gadget/simple.py')).touch(source_code, mkdir=True)
            File(join(tdir, 'gadget/test/simple.py')).touch(test_code, mkdir=True).chmod('02770')

            test_files = [join(tdir, 'gadget/test/simple.py')]
            modified_files = [os.path.normpath('gadget/simple.py')]

            def mock_run_outtxt(self):
                # Return mock output that looks like a successful test run
                mock_output = '''test_pass3 (__main__.TestSample) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.123s

OK

Timeit log per test (sorted):
0.123 Secs: Timeit: TestSample.test_pass3
Missing Lines: 3-8
Missing: 0
BrMiss: 0
Coverage: 90% - 3 lines

            '''
                return 0, mock_output

            def mock_run_sout_serr(self):
                return 1, '', ''

            with MockVar(SystemCall, 'run_outtxt', mock_run_outtxt), \
                    MockVar(SystemCall, 'run_sout_serr', mock_run_sout_serr), \
                    CaptureStdout() as p:
                # Should NOT raise SystemExit for successful tests
                rts.run_pr_coverage(test_files, modified_files)
            output = p.getvalue()
            self.assertIn('Success! All tests passed', output)
            self.assertIn(os.path.normpath('gadget/simple.py'), output)

            # Check PR description file cannot be created
            pr_desc_file = join(logdir, 'pr_description.txt')
            self.assertFalse(os.path.exists(pr_desc_file))
            self.assertIn("Could not fetch PR description. Coverage report not updated.", output)

    def test_run_pr_coverage_no_matching_source(self):
        # Test coverage when test file has no corresponding source file
        with TempDir(name=True, delete=True) as tdir, \
                TempDir(name=True, delete=True) as logdir, \
                MockVar(sys, "argv", 'script.py -coverage'.split()):

            RunTests.root = tdir
            RunTests.log_dir = logdir
            rts = RunTests()

            # Create test without corresponding source file
            test_code = f'''#!{sys.executable}
    import sys
    sys.path.append('{ROOT_ENV}')
    from gadget.ut import TestCase, unittest


    class TestOrphan(TestCase):
        def test_pass1(self):
            self.assertEqual(1, 1)


    unittest.main()
    '''

            File(join(tdir, 'mod/test/test_orphan.py')).touch(test_code, mkdir=True).chmod('02770')

            test_files = [join(tdir, 'mod/test/test_orphan.py')]
            modified_files = ['mod/different.py']  # This doesn't match the test file

            # Mock successful test run
            def mock_run_outtxt(self):
                return 0, '''Ran 1 test in 0.1s

OK

Coverage: 80% - 10 lines
Missing: 2
BrMiss: 0
'''

            # Mock gh pr view to return sample PR body
            def mock_gh_view(self):
                mock_body = '''### Why is this PR needed?
Test PR

<!-- COVERAGE_REPORT_START -->
### Coverage Report for Modified Files
_Coverage details will be automatically updated here by the CI workflow_
<!-- COVERAGE_REPORT_END -->
'''
                return 0, mock_body, ''

            def mock_run_sout_serr(self):
                if 'pr' in self.cmd and 'view' in self.cmd:
                    return mock_gh_view(self)
                elif 'pr' in self.cmd and 'edit' in self.cmd:
                    return 0, '', ''
                return 0, '', ''

            with MockVar(SystemCall, 'run_outtxt', mock_run_outtxt), \
                    MockVar(SystemCall, 'run_sout_serr', mock_run_sout_serr), \
                    CaptureStdout() as p:
                rts.run_pr_coverage(test_files, modified_files)

            output = p.getvalue()
            # Should warn about no source file found
            self.assertIn('Warning: No source file found', output)
            self.assertIn('Success! All tests passed', output)

    def test_main_coverage_mode_no_modified_files(self):
        """Test coverage mode when no modified Python files are found"""
        with TempDir(name=True, delete=True) as tdir, \
                MockVar(sys, "argv", 'script.py -coverage'.split()):

            RunTests.root = tdir
            rts = RunTests()

            # Mock get_pr_modified_files to return empty list (no Python files)
            def mock_get_pr_modified_files(self):
                return []

            with MockVar(RunTests, 'get_pr_modified_files', mock_get_pr_modified_files), \
                    CaptureStdout() as p:
                result = rts.main()

            output = p.getvalue()
            # Should print message and exit early
            self.assertIn('No modified Python files found in PR. Exiting.', output)
            self.assertIsNone(result)  # main() should return None (early exit)

    def test_main_coverage_mode_no_test_files(self):
        """Test coverage mode when modified files exist but no corresponding tests found"""
        with TempDir(name=True, delete=True) as tdir, \
                MockVar(sys, "argv", 'script.py -coverage'.split()):

            RunTests.root = tdir
            rts = RunTests()

            # Mock get_pr_modified_files to return some files
            def mock_get_pr_modified_files(self):
                return ['pymtpl/newfile.py', 'gadget/newutil.py']

            # Mock get_tests_for_modified_files to return empty list (no tests found)
            def mock_get_tests_for_modified_files(self, modified_files):
                return []

            with MockVar(RunTests, 'get_pr_modified_files', mock_get_pr_modified_files), \
                    MockVar(RunTests, 'get_tests_for_modified_files', mock_get_tests_for_modified_files), \
                    CaptureStdout() as p:
                result = rts.main()

            output = p.getvalue()
            # Should print message and exit early
            self.assertIn('No corresponding test files found for modified files. Exiting.', output)
            self.assertIsNone(result)

    def test_get_tests_for_modified_files_fallback(self):
        """Test fallback behavior when no direct test file exists - searches for any test_modified_file and adds that if exists."""
        with TempDir(name=True, delete=True) as tdir, \
                MockVar(sys, "argv", 'script.py'.split()):

            RunTests.root = tdir
            rts = RunTests()

            # Create directory structure
            # Source file without a direct test_<name>.py
            File(join(tdir, 'pymtpl/complex_module.py')).touch('# source', mkdir=True)
            # Multiple test files in the test directory
            File(join(tdir, 'somewhere/test/test_complex_module.py')).touch('# test 1', mkdir=True)
            # Modified file that doesn't have test_complex_module.py
            modified_1 = ['pymtpl/nonexistenttest.py']
            with CaptureStdout() as p:
                result = rts.get_tests_for_modified_files(modified_1)
            output_1 = p.getvalue()
            self.assertIn('No test file found for modified file', output_1)
            # Fallback case - Test exists somewhere in the repo.
            modified_2 = ['pymtpl/complex_module.py']
            with CaptureStdout() as p:
                result_2 = rts.get_tests_for_modified_files(modified_2)
            output_2 = p.getvalue()
            # Should return all test files in the directory
            expected_tests = {
                join(tdir, 'somewhere', 'test', 'test_complex_module.py')
            }
            self.assertEqual(set(result_2), expected_tests)
            # Check that all test files are mentioned in output
            self.assertIn('test_complex_module.py', output_2)

    def test_get_tests_fallback_with_direct_test_exists(self):
        """Test that fallback is NOT used when direct test file exists"""
        with TempDir(name=True, delete=True) as tdir, \
                MockVar(sys, "argv", 'script.py'.split()):

            RunTests.root = tdir
            rts = RunTests()

            # Create source file with matching test file
            File(join(tdir, 'gadget/strmore.py')).touch('# source', mkdir=True)
            File(join(tdir, 'gadget/test/test_strmore.py')).touch('# direct test', mkdir=True)

            # Also create other test files that should NOT be included
            File(join(tdir, 'gadget/test/test_other.py')).touch('# other test', mkdir=True)
            File(join(tdir, 'gadget/test/test_another.py')).touch('# another test', mkdir=True)

            modified = ['gadget/strmore.py']

            with CaptureStdout() as p:
                result = rts.get_tests_for_modified_files(modified)

            output = p.getvalue()

            # Should NOT see fallback message
            self.assertNotIn('[Fallback]', output)

            # Should only return the direct test file
            expected = [join(tdir, 'gadget', 'test', 'test_strmore.py')]
            self.assertEqual(result, expected)

    def test_main_coverage_mode_success_flow(self):
        # Test complete coverage mode flow with valid test files and modified files
        with TempDir(name=True, delete=True) as tdir, \
                TempDir(name=True, delete=True) as logdir, \
                MockVar(sys, "argv", 'script.py -coverage'.split()):

            RunTests.root = tdir
            RunTests.log_dir = logdir
            rts = RunTests()

            # Create actual test structure
            File(join(tdir, 'pymtpl/sample.py')).touch('# source', mkdir=True)
            File(join(tdir, 'pymtpl/test/test_sample.py')).touch('# test', mkdir=True)

            # Mock get_pr_modified_files to return files
            def mock_get_pr_modified_files(self):
                return ['pymtpl/sample.py']

            # Mock get_tests_for_modified_files to return test files
            def mock_get_tests_for_modified_files(self, modified_files):
                return [join(tdir, 'pymtpl/test/test_sample.py')]

            # Mock the actual test execution
            def mock_run_outtxt(self):
                mock_output = '''test_sample (__main__.TestSample) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.123s

OK

Coverage: 95% - 20 lines
Missing: 1
BrMiss: 0
'''
                return 0, mock_output

            # Mock gh pr view to return sample PR body
            def mock_gh_view(self):
                mock_body = '''### Why is this PR needed?
Test PR

<!-- COVERAGE_REPORT_START -->
### Coverage Report for Modified Files
_Coverage details will be automatically updated here by the CI workflow_
<!-- COVERAGE_REPORT_END -->
'''
                return 0, mock_body, ''

            def mock_run_sout_serr(self):
                if len(self.cmd) >= 3 and self.cmd[:3] == ['gh', 'pr', 'view']:
                    return mock_gh_view(self)
                elif len(self.cmd) >= 3 and self.cmd[:3] == ['gh', 'pr', 'edit']:
                    return 0, '', ''
                return 0, '', ''

            with MockVar(RunTests, 'get_pr_modified_files', mock_get_pr_modified_files), \
                    MockVar(RunTests, 'get_tests_for_modified_files', mock_get_tests_for_modified_files), \
                    MockVar(SystemCall, 'run_outtxt', mock_run_outtxt), \
                    MockVar(SystemCall, 'run_sout_serr', mock_run_sout_serr), \
                    CaptureStdout() as p:
                result = rts.main()

            output = p.getvalue()
            # Should show it's running coverage
            self.assertIn('Running coverage for 1 test files', output)
            self.assertIn('Success! All tests passed', output)
            self.assertIsNone(result)  # main() returns None after coverage

    def test_get_pr_modified_files_with_test_files_only(self):
        """Test that modifying only test files returns their corresponding source files"""
        with MockVar(sys, "argv", 'script.py'.split()):
            rts = RunTests()

        # Create temporary directory structure
        with TempDir(name=True, delete=True) as tdir:
            RunTests.root = tdir

            # Create source and test files
            File(join(tdir, 'pymtpl/binctr.py')).touch('# source', mkdir=True)
            File(join(tdir, 'pymtpl/test/test_binctr.py')).touch('# test', mkdir=True)

            File(join(tdir, 'gadget/strmore.py')).touch('# source', mkdir=True)
            File(join(tdir, 'gadget/test/test_strmore.py')).touch('# test', mkdir=True)

            # Mock GitHub.get_modfiles() to return ONLY test files
            mock_files = [
                'pymtpl/test/test_binctr.py',
                'gadget/test/test_strmore.py',
            ]

            with MockVar(GitHub, 'get_modfiles', lambda self: mock_files), \
                    CaptureStdout() as p:
                result = rts.get_pr_modified_files()

            # Should return the corresponding source files
            expected = [
                os.path.normpath('pymtpl/binctr.py'),
                os.path.normpath('gadget/strmore.py')
            ]
            self.assertEqual(sorted(result), sorted(expected))

            # Check output messages
            output = p.getvalue()
            self.assertIn(f"Added source file {os.path.normpath('pymtpl/binctr.py')}", output)
            self.assertIn(f"Added source file {os.path.normpath('gadget/strmore.py')}", output)

    def test_get_pr_modified_files_with_relative_paths(self):
        """Test handling of test files with leading ./ in paths"""
        with MockVar(sys, "argv", 'script.py'.split()):
            rts = RunTests()

        with TempDir(name=True, delete=True) as tdir:
            RunTests.root = tdir

            # Create source and test files
            File(join(tdir, 'tp/testprogram.py')).touch('# source', mkdir=True)
            File(join(tdir, 'tp/test/test_testprogram.py')).touch('# test', mkdir=True)

            # Mock with ./ prefix (some git systems return paths this way)
            mock_files = [
                './tp/test/test_testprogram.py',
            ]

            with MockVar(GitHub, 'get_modfiles', lambda self: mock_files), \
                    CaptureStdout() as p:
                result = rts.get_pr_modified_files()

            # Should handle ./ prefix correctly and return source file
            expected = {os.path.normpath('tp/testprogram.py')}
            self.assertEqual(result, expected)

            output = p.getvalue()
            self.assertIn(f"Added source file {os.path.normpath('tp/testprogram.py')}", output)

    def test_get_pr_modified_files_test_without_source(self):
        """Test that test files without corresponding source files are ignored"""
        with MockVar(sys, "argv", 'script.py'.split()):
            rts = RunTests()

        with TempDir(name=True, delete=True) as tdir:
            RunTests.root = tdir

            # Create only test file, NO source file
            File(join(tdir, 'mod/test/test_orphan.py')).touch('# test', mkdir=True)

            # Mock with test file that has no source
            mock_files = [
                'mod/test/test_orphan.py',
            ]

            with MockVar(GitHub, 'get_modfiles', lambda self: mock_files), \
                    CaptureStdout() as p:
                result = rts.get_pr_modified_files()

            # Should return empty list (no source file exists)
            self.assertEqual(result, set())

            output = p.getvalue()
            # Should NOT have "Added source file" message
            self.assertNotIn('Added source file mod/orphan.py', output)


if __name__ == '__main__':  # pragma: no cover
    RunTests.log_dir = f'{UT_DIR_REPO}/trash_logs/mirror_logs'       # So that it won't clobber with real run_tests.py logs
    unittest.main()
