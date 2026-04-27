#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
VEP unittest importer

Purpose: 1. Tagging of slow and optional unittests
         2. Identify tmp files which are not cleaned up - CheckTmpDir()
         3. Independent test execution (via -i) -> IndependentExec()
         4. Improved display for -v (easy cut+paste of 'classname.test_name')
         5. -t option: time each test case

Unittest Usage:
   1. In test_<module>.py file, use the following import. No need to 'import unittest'
        from gadget.ut import unittest, is_ut_option, TestCase

   * The folowing are decorators, add it before the unittest class or function.
   2. Identify slow tests:     [Skipped by default, run by -s. These are executed during nightly build]
        @unittest.skipIf(*is_ut_option('SLOW', message='Slowtest bec large file'))   # change message to right one
   3. Identify optional tests: [Skipped by default, run by -o. These are not run during nightly build]]
        @unittest.skipIf(*is_ut_option('OPTIONAL', message='For new operating system only'))   # change message to right one
   4. Identify non-nightly build tests:        [Skip by -a. These are not run during nightly build]]
        @unittest.skipIf(*is_ut_option('SKIP_NIGHTLY_BUILD', message='manual run only', neg=False))
   5. Identify slow StateEqn integration test: [Skip by -r. These are skipped during update_rel.py -riskrelease]]
        @unittest.skipIf(*is_ut_option('SESLOW', message='slow stateeqn specific test', neg=False))
   6. To skip (always) a unittest class or function:
        @unittest.skip('skipping, pending code completion')
   7. To test in one site only, eg. JF:
        @unittest.skipIf(veppaths.vep_prodsite() != 'JF', "JF only - <reason_why>")

Unittest Execution Usage:
   To run all tests excluding slow-tests and optional-tests (normal run):
        test_<module>.py -v -b
   To run all tests including slow-tests:
        test_<module>.py -v -b -s
   To run all tests including optional tests:
        test_<module>.py -v -b -o
   To run unit tests independently (separate process). [identify unit-test to unit-test dependency]
        test_<module>.py -i
   To run unit tests with tmp file warning disabled:
        test_<module>.py -notmpcheck
   To run unit tests with timeit information:
        test_<module>.py -t -b
   To enable devdebug prints:
        test_<module>.py -d
   To skip PEP8 check (during active development or coverage iterations):
        test_<module>.py -p

"""

import os
import sys
import signal
import re
import unittest as orig_unittest     # module usage is "from gadget.ut import unittest"
import atexit
import shutil
from .files import File, TempDir
from .strmore import regex, group, indent
from .shell import getuid, tmpdir, iseclipse_ut, LAUNCH_CWD, SystemCall
from .gizmo import MockVar, Elapsed, IS_UNIX, IS_WIN
from .helperclass import OPT, CaptureStdout, CaptureStdoutLog, is_cov
from .tputil import SDiff
from os.path import join, dirname, realpath, basename
import __main__  # Needed to determine what the top calling file is in all cases

# these are here for easy import on test files
from unittest.mock import patch, MagicMock, Mock


class CheckTmpDir:
    """Class to check if there are extra tmp files not deleted after a unittest"""

    def __init__(self):
        """Get all files in /tmp that is owned by user"""

        self.uid = getuid()      # userid number of owner
        self.files = set()    # These contain the /tmp files owned by user at start of execution

        # get all the files in tmp that is owned by user
        for f in os.listdir(tmpdir()):
            name = os.path.join(tmpdir(), f)  # Need to check existence because of broken links (file exist but pointing to nothing). os.stat() will fail on broken links
            try:
                if os.path.exists(name) and os.stat(os.path.join(tmpdir(), f)).st_uid == self.uid:
                    self.files.add(f)
            except FileNotFoundError:    # pragma: no cover   - race condition during threaded runs
                pass

        # store the functions for use in delete. It's a BKM to store them here bec of GC.
        self.join = os.path.join
        self.stat = os.stat
        self.listdir = os.listdir
        self.exists = os.path.exists
        self.tmpdir = tmpdir()
        atexit.register(self.close)

    def close(self):
        """
        Check added files in /tmp since import time.
        """
        # Note: atexit.register() is called FIRST than __del__ destructor.  (This is good)
        for f in self.listdir(self.tmpdir):
            if 'eclogin-errors' in f:
                continue
            name = self.join(self.tmpdir, f)

            try:
                st_uid = self.stat(name).st_uid
            except BaseException:
                st_uid = 0

            if st_uid == self.uid:
                if f not in self.files:
                    sys.stderr.write("=========== WARNING! tmp file created but not "
                                     "removed: %s\n" % name)
                    # Cannot use raise SystemExit above since it will be ugly "Exception SystemExit()... ignored"


class UT_Options:
    """
    Determine the additional arguments for unittests (e.g. -s,-o)
    Instantiated Singleton design
    Used with @unittest.skipIf
    Example:
       @unittest.skipIf(*is_ut_option('SLOW', message='Slowtest bec large file'))
    """

    def __init__(self, dd):
        """Get all the options specified in dd dictionary"""
        self.options = {}     # dictionary of options
        self.dash = {}     # option name to dash-arg mapping
        for op in dd:
            self.options[dd[op]] = False
            self.dash[dd[op]] = op
            if op in sys.argv:
                sys.argv.remove(op)    # remove this option, so that unittest will not fail
                self.options[dd[op]] = True

    def set_option(self, option, value=True):
        """
        Set the option to value
        Example:
            is_ut_option.set_option('SLOW')    # set SLOW to True, same as adding '-s' argument
        """
        if option not in self.options:
            raise Exception("Invalid is_ut_option(%r) specified." % option)

        self.options[option] = value

    def __call__(self, option, message, andexpr=True, neg=True):
        """Returns existence of this option"""
        # check validity first
        if option not in self.options:
            raise Exception("Invalid is_ut_option(%r) specified." % option)

        # Add a period for pretty printout
        if not message.endswith("."):
            message += "."

        # Return a tuple: (True/False, message).
        # Since SkipIf is a negative expression, then return the not value.
        if neg:
            # Default
            return (not (self.options[option] and andexpr),
                    message + " Add %s to test." % self.dash[option])
        else:
            # example: SKIP_NIGHTLY_BUILD
            return ((self.options[option] and andexpr),
                    message + " Remove %s to test." % self.dash[option])


class IndependentExec:
    """
    Execute the unittests independently to see which tests that are dependent from each other.
    It is ideal that tests should not affect each other
    """

    def getfuncs(self, f):
        """
        Return a set of classname.funcname for unittests
        Algo here is to parse the caller script. Decision to do this rather than getting
        the func names dynamically is because need to reimport (which is circular import)
        and need to find the methods to get the name.
        """
        tests = set()
        classname = None
        for line in File(f).chomp():
            if regex(r'^class\s+(\w+)', line):
                classname = group(1)
                if 'unittest.TestCase' not in line:
                    classname = None
            if regex(r'^    def\s+(test\w+)', line):
                if classname is not None:
                    tests.add(classname + "." + group(1))
        return tests

    def runtest(self, f, tests, arg_s, arg_o):
        """Run the tests independently"""
        faillist = []

        # Additional args
        addargs = ""
        if arg_s:
            addargs += "-s "
        if arg_o:
            addargs += "-o "

        for t in sorted(tests):
            ecode, sout, serr = SystemCall("%s -v -b %s %s" % (f, t, addargs)).run_sout_serr()
            line = serr.split('\n')[-1]  # get last line
            print(t, line)
            if ecode:
                faillist.append("%s %s" % (t, line))

        # display all faillist
        if len(faillist) > 0:
            print()
            print("Summary of Fails: ========")
            for line in faillist:
                print(line)

    def main(self, f, arg_s, arg_o):
        """Main routine, run the tests"""
        self.runtest(f, self.getfuncs(f), arg_s, arg_o)


def set_max_runtime(timeout=60):
    """
    Set unittest max execution time to timeout (in seconds)
    """
    def handler(signum, frame):
        raise Exception("Unittest exceeded maximum time: %s" % timeout)

    signal.signal(signal.SIGALRM, handler)
    signal.alarm(timeout)


class TimeTheTest:
    """
    Internal use by TestCase to display the time per test
    Enable with -t option
    """

    def __init__(self):
        self.ut_timer = Elapsed()
        self.ut_timer_prev = "Bootup"
        self.ut_timer_log = []
        self.is_timer_enabled = bool('-t' in sys.argv)   # cannot use is_ut_option() at this point, is_ut_option() not defined yet
        self.check_args()
        atexit.register(self.timer_print)     # execute timer_print upon exit

    def check_args(self):
        """Add the -v if user did not specify it"""
        if self.is_timer_enabled and '-v' not in sys.argv:
            sys.argv.insert(1, '-v')

    def timer_string(self, name):
        """Save the time of this particular test name"""
        tim = self.ut_timer.elapsed()
        if self.is_timer_enabled:
            res = "[%s]: Timeit: %s\n" % (self.ut_timer.elapsed(reset=True, pretty=True),
                                          self.ut_timer_prev)
        else:
            res = ""
        self.ut_timer_prev = name
        self.ut_timer_log.append((tim, res))
        return res

    def timer_print(self):
        """
        Print the timer log. Called by atexit
        """
        if not self.is_timer_enabled:
            return   # do nothing

        self.timer_string("")   # last test
        print()
        print("Timeit log per test (sorted):")
        for tim, line in sorted(self.ut_timer_log, key=lambda x: x[0]):
            print(line, end=' ')


time_the_test = TimeTheTest()


class TestCase(orig_unittest.TestCase):
    """
    Inherited testcase, with better printout so you can cut and paste the test
    Added assert and more functionality
    """

    def setUp(self):
        # So that custom message is appended after the expect vs actual results. (Thanks DavidM)
        # https://docs.python.org/2/library/unittest.html#unittest.TestCase.longMessage
        self.longMessage = True

        # one-time-per-class setup for logging
        if not hasattr(self, "_onetimesetup_log"):
            from .pylog import log    # to support py3 imports
            self.__class__._onetimesetup_log = True       # Do not remove this
            log.stdout('DEBUG')   # so that -v -b will buffer log.debug() and log.info()

    def __str__(self):
        testname = "%s.%s" % (self.__class__.__name__, self._testMethodName)
        timerstring = time_the_test.timer_string(testname)
        return "%s%s(%s)" % (timerstring,
                             testname,
                             self.__class__.__module__)

    def assertRegexpInList(self, list_output, list_in_expect):
        """
        Given a output list of strings, check elements of list_in_expect is in there
        Order is checked
        list_in_expect can be partial

        :param list_output: list of output_strings
        :param list_in_expect: list of regex string (expect)
        :return:
        """
        rolist = [re.compile(x) for x in list_in_expect]
        idx = 0
        msg = [f"NOT TESTED: {x}" for x in list_in_expect]
        lastfound = 0
        for lno, item in enumerate(list_output):
            if rolist[idx].search(item):
                lastfound = lno
                msg[idx] = msg[idx].replace('NOT TESTED:', '    FOUND :')
                idx += 1
                if idx == len(rolist):
                    return     # success pass

        # replace first "NOT TESTED" to "NOT FOUND"
        first = True
        for idx in range(len(msg)):
            if 'NOT TESTED:' in msg[idx] and first:
                msg[idx] = msg[idx].replace('NOT TESTED:', 'NOT FOUND :')
                first = False

        # Print the output lines for easy debug
        print('==== Output lines:')
        for lno, line in enumerate(list_output):
            ok = 'FOUND' if lastfound >= lno else '     '
            print(f'{ok} {lno+1}: {line}')

        self.fail("%r is not found in expected list while keeping the order:\n%s"
                  "" % (rolist[idx].pattern, indent(3, msg)))

    def assertRegexpInDict(self, dict_obj, key_regex, val_regex):
        """Given a dict_obj, check for at least one key/value pair match"""
        key_re = re.compile(key_regex)
        val_re = re.compile(val_regex)
        for key in dict_obj:
            if key_re.search(key) and val_re.search(dict_obj[key]):
                return
        self.fail("%s/%s does not match any key/value in %s" % (key_regex, val_regex, dict_obj))

    def assertRegexpEachList(self, list_obj, list_regex):
        """
        Given a list_obj, list_regex, perform the regex in each element of list_obj.
        Each element in list_obj should correspond to each element in list_regex, 1:1
        """
        if len(list_obj) != len(list_regex):
            self.fail('Number of elements does not match: %d vs %d. Reference: %r'
                      '' % (len(list_obj), len(list_regex), list_obj))

        for comp, reg in zip(list_obj, list_regex):
            if comp == reg:
                continue
            if not re.search(reg, comp):
                self.fail("Element %r failed regex '%s'" % (comp, reg))

    def assertXpathEqual(self, path1, path2):
        """
        Check two paths are equal for both unix and windows
        """
        from tp.testprogram import Env
        if Env.xpath(path1) != Env.xpath(path2):
            self.fail(f"'{Env.xpath(path1)}' != '{Env.xpath(path2)}'")

    def assertItemsEqual(self, list1, list2):
        """
        Check that two lists have the same content (order does not matter)
        :param list1:
        :param list2:
        :return: None
        """
        # create copies of the lists to keep track of duplicate items, ensure count is the same
        copy_of_2 = list(list2)

        for item in list1:
            if item not in list2:
                self.fail('Lists are different, item in first but not second: %s' % item)
            if item not in copy_of_2:
                self.fail('List 1 has extra element: %s' % item)
            copy_of_2.remove(item)

        if copy_of_2:   # must be empty
            self.fail('Lists are different, items in second but not first: %s' % copy_of_2)

    def assertGoldEqual(self, targfile, goldfile):
        """
        Compares Test file with Gold file, then copies the Test file into <goldfile>.compare for diffing
        Normally, Test file is in tmp, so it does not exist

        :param targfile: Test file
        :param goldfile: Expect file
        :return:
        """
        if File(targfile).read().rstrip() == File(goldfile).read().rstrip():
            return     # passing case

        dest = f'{goldfile}.compare'
        File(dest).unlink()
        shutil.copy2(targfile, dest)    # cannot use File().copy() here due to a wierd corner case on naming
        self.fail(f'Contents of expect file differ. Check diff and update gold file if needed: '
                  f'tkdiff {dest} {goldfile};')

    def assertTextEqual(self, result_text, expected_text):
        """
        Compare a multi-line-string (result_text) with expected_text
        with output using sdiff for easy compare.
        trailing spaces are removed.

        :param result_text: multi-line result text
        :param expected_text: multi-line expected text
        :return: None
        """
        # remove trailing spaces
        result_text = '%s\n' % '\n'.join(x.rstrip() for x in result_text.split('\n'))
        expected_text = '%s\n' % '\n'.join(x.rstrip() for x in expected_text.split('\n'))

        if result_text == expected_text:
            return   # passing case
        if f'\n{result_text}\n' == expected_text:     # for readability on triple quoted string
            return   # passing case
        if f'\n{result_text}' == expected_text:       # for readability on triple quoted string
            return   # passing case
        if f'{result_text}\n' == expected_text:       # for readability on triple quoted string
            return   # passing case

        # Display the resulting text for easy cut+paste
        message = ["Text does not match expect. Details below:"]
        message.append("===== start of result text")
        message.append(result_text)
        message.append("===== end of result text. sdiff below:")

        # Display the sdiff
        if IS_UNIX:
            with TempDir(name=True) as tdir:
                f1 = File(join(tdir, 'f1')).touch(result_text).get_name()
                f2 = File(join(tdir, 'f2')).touch(expected_text).get_name()
                _, out = SystemCall('sdiff %s %s --strip-trailing-cr' % (f1, f2)).run_outtxt()
                message.append(out)
        else:
            f1 = [x.rstrip() for x in result_text.split('\n')]
            f2 = [x.rstrip() for x in expected_text.split('\n')]
            with CaptureStdoutLog(disp=False) as p:
                SDiff().simple(f1, f2, col=80, diffonly=False)
            message.append(p.getvalue())

        self.fail('\n'.join(message))

    def assertPartialText(self, result_text, expected_text):
        """
        Check if expected_text is inside multi-line-string (result_text)
        with output using sdiff for easy compare.
        trailing spaces are removed. Similar to assertTextEqual

        :param result_text: multi-line result text
        :param expected_text: multi-line expected text
        :return: None
        """
        # remove trailing spaces
        result_text = '%s\n' % '\n'.join(x.rstrip() for x in result_text.split('\n'))
        expected_text = '%s\n' % '\n'.join(x.rstrip() for x in expected_text.split('\n'))

        if expected_text in result_text:
            return   # passing case

        # Display the resulting text for easy cut+paste
        message = ["Expected Text does not exist. Details below:"]
        message.append("===== start of result text")
        message.append(result_text)
        message.append("===== end of result text. sdiff below:")

        # Display the sdiff
        with TempDir(name=True) as tdir:
            f1 = File(join(tdir, 'f1')).touch(result_text).get_name()
            f2 = File(join(tdir, 'f2')).touch(expected_text).get_name()
            _, out = SystemCall('sdiff %s %s' % (f1, f2)).run_outtxt()
            message.append(out)

        self.fail('\n'.join(message))

    def create_patch(self, name, mock=None):
        """
        Non-indent version of patch()+Mock()
        Useful if you don't want nested indents for so many patches.
        The patch will apply to end of test function.
        For partial code patching, then use 'with patch() context manager' - indent version.

        Usage1:
        def test_first(self):
            a = self.create_patch('os.system')
            <somecode, os.system() is used>
            a.assert_called_with(cmd)

        Usage equivalence:
            with patch('os.system', Mock(return_value='result') as a:
                <somecode>
        above is equivalent to:
            a = self.create_patch('os.system', Mock(return_value='result')
            <somecode>

        VEP2 suggested usage for patch:
        1. decorator: @patch()    # Only if you don't need the mock object for asserts
                                  # Good for test level or class level
        2. decorator: @with_(MockVar, <args>
                                  # Only if you don't need the mock object for asserts
                                  # Good for test level only
        2. with MockVar():        # Specific code block mocking, mock object can be returned
        3. m=self.create_patch()  # non-indent solution for patching and mock object is returned
        """
        if mock is None:
            mock = Mock()
        patcher = patch(name, mock)
        thing = patcher.start()
        self.addCleanup(patcher.stop)
        return thing


class _TestPEP8(TestCase):
    """
    A TestCase that will be added to every unit test execution to ensure that PEP8 compliance checks
    are being followed.
    """
    # See code list: https://github.com/hhatto/autopep8
    ignore_codes = ['E402',  # E402 - Fix module level import not at top of file
                    'E501',  # E501 - Try to make lines fit within --max-line-length characters.
                    'W503',  # W503 - Fix line break before binary operator.
                    'W504',  # W504 - Fix line break after binary operator.
                    'W605',  # Fix invalid escape sequence 'x'.
                    'E712']  # E712 - Fix comparison with boolean.  (Breaks Numpy)

    def do_PEP8(self):
        os.chdir(LAUNCH_CWD)  # Some test files are changing CWD dirs during execution. Getting original.
        pep8_results = self._do_pep8_checks(realpath(__main__.__file__))
        info = self._build_info_string(pep8_results)
        self.assertEqual(len(pep8_results), 0, info)

    @staticmethod
    def _do_pep8_checks(ut_file):
        """
        Scan the current unit test file and the corresponding module.py file for PEP8 violations. Skip
        violations that have autopep8 cleanup bugs or that have a no pep8 pragma attached to the line
        :param ut_file: Unit Test file being run. Example: library/utils/test/test_strmore.py
        :return: a list of filtered PEP8 violations
        """
        if IS_WIN:
            return []   # pragma: no cover

        from main.pycodestyle import StyleGuide
        style = StyleGuide(ignore=TestPEP8.ignore_codes)
        files_to_check = TestPEP8._get_files(ut_file)
        print(f"-i- PEP8 files to check: {files_to_check}")

        filtered = []
        if not len(files_to_check):
            return []

        # Must run the check on each file individually b/c the pycodestyle report class
        # only stores the results of the last file run.
        for tfile in files_to_check:
            # Style checker prints a lot of stuff to the screen that we don't need to bother
            # the devlopers with
            with CaptureStdout() as p:
                result = style.check_files([tfile])

            # VEP will skip some PEP8 checks that autopep8 won't clean up
            if result.get_count() > 0:
                count = 0
                for r in result._deferred_print:
                    (line_num, offset, pep_type) = r[:3]
                    full_line = result.lines[line_num - 1].strip('\n')

                    # Ignore any line that contains the no pep8 pragma
                    #  Allow the users to skip specific PEP codes as well
                    # Example:
                    #    a[1]=b  # pragma: no pep8
                    #    a[2]   = b # pragma: no pep8 E221
                    #    a[3]   =   b  #pragma: no pep8 E221,E222
                    m = re.search(r'#\s+pragma:\s*no\s+pep8([\s,0-9EW]+)?', full_line)
                    if m:
                        skip_codes = m.group(1)
                        if skip_codes:
                            skip_list = skip_codes.replace(',', ' ').split()
                            if pep_type in skip_list:
                                continue
                        else:
                            continue       # pragma: no cover   - peephole optimization

                    filtered.append((tfile, full_line) + r)
                    count += 1

                if count:
                    print("***** Found %s pep8 errors in %s" % (count, tfile))

        return filtered

    @classmethod
    def _get_files(cls, ut_file):   # using staticmethod will cause unittest to fail because of Mock
        """
        :param ut_file: fullpath to the unittest file
        :return: list of files
        """
        files = [ut_file]
        if re.search(r'/(skip_list_here)/', ut_file):
            return files

        module_filename = basename(ut_file).replace('test_', '')
        module_dir = dirname(dirname(ut_file))
        module_file = os.path.join(module_dir, module_filename)
        if os.path.exists(module_file):
            files.append(module_file)

        return files

    @staticmethod
    def _build_info_string(pep8_violations):
        info = 'PEP8 Passed!'
        result_str = ''
        cwd = realpath(os.getcwd())
        if len(pep8_violations) > 0:
            found = {}
            for pep in pep8_violations:
                (ufile, full_line, line_num, offset, pep_type, pep_desc) = pep[:6]
                found[ufile.replace(cwd, '.')] = 1
                result_str += "%s:%s:%s %s %s\n" % (ufile, line_num, offset, pep_type, pep_desc)
                result_str += full_line + '\n'
                result_str += ' ' * offset + '^\n'

            info = """***PEP8 failures detected!***

In order to pass unit tests, you need to ensure both your test.py file and module.py file are PEP8 clean.
You have several options to identify and fix the PEP8 violations:
  * Use Intellij/PyCharm: These IDEs will underline and autofix (Code->Reformat Code) PEP8 violations
  * Run autopep8 script to clean files:
        main/easyautopep8.py {files}

  * Just report the failures:
        main/pycodestyle.py {files} --ignore={ignore} --show-source --statistics
            (You can add --show-pep8 as well to get hints if you aren't sure how to fix)

  * You can ONLY exclude individual lines if you have a GOOD reason they aren't PEP8 compliant. Optionally, you
    can add a list of error codes that should be skipped, other violations will still be detected.
        Example:
            config[abc]    = 1  # pragma: no pep8              <-- Skips all PEP8 errors (not recommended)
            config[x]      = 1  # pragma: no pep8 E221,E222    <-- Only skips specified PEP8 codes

You have {count} PEP8 Violation(s):
""".format(count=len(pep8_violations), ignore=','.join(TestPEP8.ignore_codes), files=' '.join(list(found.keys())))

        return info + result_str

    def do_checkenv(self):
        message = self.check_file(self.get_bin_module())
        self.assertTrue(message.startswith("success"), message)

    @classmethod
    def get_bin_module(cls):
        for bin_file in cls._get_files(realpath(__main__.__file__)):
            if '/test/' in bin_file:
                continue   # skip unittests
            if 'library/bin/' in bin_file:
                return bin_file
        return ''   # not a bin file

    @classmethod
    def check_file(cls, bin_file):     # using staticmethod will cause unittest to fail because of Mock
        """
        :param bin_file: Input file
        :return: success.* for success, other message for failure
        """
        if not bin_file:
            return 'success0'

        # skip these special files
        if basename(bin_file) in ('tracer.py',        # not a vep2 specific tool
                                  'getimports.py',    # must not import anything else
                                  'tkdiff.py',        # has special imports
                                  'checkenv.py',      # cannot import itself
                                  'config_env_sites.py',  # Non executable required config
                                  'compas_query.py',  # this file is released in tools/ area, no checkenv
                                  'tailer.py',        # copied from web
                                  'attach_debug.py',  # standard imports only
                                  'dir_diff.py',      # special usage, tst rel area is used during release
                                  'vcf.py',           # try/except added to support Python3
                                  'run_all_tests.py'  # Needs to do special imports to support coverage calcs
                                  ):
            return 'success1'

        print("checkenv test: %s" % bin_file)
        with File(bin_file) as ff:
            for lno, line in enumerate(ff.chomp()):
                # ignore this special import
                if line.startswith(('import sys', '#')):
                    continue

                # check for py3, look for checkenv in a try/except (line starts with space unlike py2 case below)
                # instead of the py2 case (import checkenv), py3 looks like this:
                # try:
                #   from bin import checkenv
                # except BaseException:
                #   import checkenv
                if 'import ' in line:
                    message = ("library/bin/%s does not have 'import checkenv' as the first import. Line #%s. "
                               "This is required so auto-source will work for bin/ files." % (basename(bin_file), lno))
                    if re.search(r'^\s*from bin import [^#]*checkenv', line) or \
                            re.search(r'^\s*import [^#]*checkenv', line):
                        return "success2_py3"
                    return message

                # py2/original check: find the first import that does NOT start with a space/tab
                # e.g. 'import checkenv'
                if 'import ' in line and (not line.startswith(' ')):    # pragma: no cover  - python2 is no longer supported
                    message = ("library/bin/%s does not have 'import checkenv' as the first import. Line #%s. "
                               "This is required so auto-source will work for bin/ files." % (basename(bin_file), lno))
                    if 'import checkenv' in line:
                        return "success2"
                    return message

        return 'success3'


class unittest:
    """
    In order to enforce PEP8 standards, the unit test main function is being intercepted so that we can
    guarentee the PEP8 checks are being run for every unit test.  All other functions of unittest that
    we are using in the code also need to be specified so that live unittest.* references will not break.
    """
    # Intercepting the unittest.TestCase calls to force the VEP version to be used.  This line is saying that:
    #    unittest.TestCase = (local ut.py) TestCase class.
    #  Example test_abc.py entry:
    #    class MyTests(unittest.TestCase)  -->  Now points to VEP version of TestCase
    #    class MyTests(TestCase)           --> Also points to VEP version of TestCase
    # This will fix mismatched printing cases where the built-in & VEP versions were being mixed together
    # The following line looks weird ... but it really does need to be this way.
    TestCase = TestCase

    @classmethod
    def main(cls, *args, **kwargs):
        """
        This function will force PEP8 compliance checks to be run by automatically adding an additional TestCase
        to every unittest file being run by VEP.  The procedure will be as follows:
            1) Unit Test file and corresponding module .py file will be checked for PEP8 compliance
                Example: test/test_abc.py executed -- ./abc.py is also checked
            2) Only library/, TST/, and REF/ files are checked.  Product specific code is not checked
                because we are not forcing compliance on configs or module State Equations
            3) Concise summary of failures will be provided. Devs informed of how to auto-correct failures
        :param args: Args to pass to the builtin unittest.mail()
        :param kwargs: Number of arguments being passed
        :return:
        """
        # Add our own custom module to the list of unitest.TestCases to be executed
        frame = sys._getframe(1)
        module = frame.f_locals
        module['TestPEP8'] = TestPEP8   # We force PEP8 class into this module
        kwargs['testRunner'] = First5FailRunner
        return orig_unittest.main(*args, **kwargs)

    @classmethod
    def skip(cls, *args, **kwargs):
        return orig_unittest.skip(*args, **kwargs)

    @classmethod
    def skipIf(cls, *args, **kwargs):
        return orig_unittest.skipIf(*args, **kwargs)

    @classmethod
    def skipUnless(cls, *args, **kwargs):
        return orig_unittest.skipUnless(*args, **kwargs)

    @classmethod
    def expectedFailure(cls, *args, **kwargs):
        return orig_unittest.expectedFailure(*args, **kwargs)


class First5FailResult(orig_unittest.TextTestResult):

    def printFirst5Failures(self):
        all_failed = [test for (test, _) in self.errors + self.failures]
        if all_failed:
            total_failures = len(all_failed)
            shown_failures = min(5, total_failures)

            if total_failures <= 5:
                # Show "M Failing Tests" when M <= 5
                print(f"\n---> {total_failures} Failing Test{'s' if total_failures > 1 else ''}:")
            else:
                # Show "First N of M Failing Tests" when M > 5
                print(f"\n---> First {shown_failures} of {total_failures} Failing Tests:")

            for i, (test) in enumerate(all_failed, 1):
                if i <= 5:
                    print(test)


class First5FailRunner(orig_unittest.TextTestRunner):
    resultclass = First5FailResult

    def run(self, test):
        result = super().run(test)
        result.printFirst5Failures()
        return result


class BreakPoint(Exception):
    """BreakPoint exception class, used with BreakAt()"""
    pass


class BreakAt(MockVar):
    """
    Class to trigger breakpoint at any function (before the func call or after the func call)
    for testing purposes.

    See below for usage:

    def test_break_at_a_function(self):
        import patternheader

        with BreakAt(patternheader.PinHeader, 'getHeaderString', count=0) as bp:   # getHeaderString is the method name for breakpoint
            with self.assertRaises(BreakPoint):       # This is needed to trap the breakpoint. The breakpoint will happen as a 'raise BreakPoint'
                pat = PatternBase.mini_mkpat('249', module='Mft')    # setup
            # Do checks here or unittest here. Code should be at this indent level.
            # Breakpoint happened before getHeaderString() is called


    def test_break_after_a_function(self):
        import patternheader

        with BreakAt(patternheader.PinHeader, 'getHeaderString', count=1) as bp:
            with self.assertRaises(BreakPoint):
                pat = PatternBase.mini_mkpat('249', module='Mft')    # setup
            # Breakpoint happened after getHeaderString() is called
            # more test code here
            self.assertEqual(bp.result, 'SomeValue')   # The result of 'getHeaderString' is in bp.result
    """

    def __init__(self, obj, method, count=1):
        """
        obj is the source object
        method is the method name
        count is the counter before BreakPoint is raised.
        zero means before the function is called.
        1 means after one function call
        2 means after two function calls, etc
        """
        self._obj = obj
        self._attr = method
        self._isdict = False
        self._orig = None    # populated in _assign_dict(), _assign_attr()
        self._count = count
        self._cnt = 0
        self.result = "Method not executed"
        self._mockif = None
        self._fakeit()

    def _fakeit(self):
        """Fake the method call"""
        if not hasattr(self._obj, self._attr):
            raise Exception("%s does not have %s() method" % (self._obj, self._attr))
        func = getattr(self._obj, self._attr)

        def func_closure(*args, **kwargs):
            if self._count == 0:
                raise BreakPoint
            self.result = func(*args, **kwargs)
            self._cnt += 1
            if self._cnt == self._count:
                raise BreakPoint
            return self.result    # return the result of the function

        self._value = func_closure

    def __enter__(self):
        """Do the mocking"""
        self._assign_attr()

        return(self)     # Do not return Mock object. Return the value, for use with stdout Mocks.


class CronDir:
    """
    Create unittest cron temp dir

    Usage:
    # @patch('veplib.prod.location.veppaths.crondir', Mock(return_value=crondir()))
    """

    def __call__(self):
        self.tdir = TempDir()   # Create a new instance everytime it is called
        return self.tdir.name()


crondir = CronDir()


def mock_all_methods(cls, value):
    """
    Return a MagicMock object, with all (normal) methods of cls mocked with given value

    # Example 1 - Mock a class:
       with MockVar(obj, 'MyClass', mock_all_methods(MyClass, True)):
           # Code that instantiates MyClass()

    # Example 2 - Mock an instantiated object methods:
       myobj = MyClass()
       with MockVar(obj, 'myobj', mock_all_methods(myobj, True)):
           # Code that uses myobj
    """
    allmethods = {"%s.return_value" % x: value for x in dir(cls) if not x.startswith('__')}
    m = MagicMock()
    if isinstance(cls, type):
        ins = m.return_value
        ins.configure_mock(**allmethods)
    else:
        m.configure_mock(**allmethods)
    return m


def ut_data_exists(path):
    """
    Helper function to check if test data exists

    Used as a decorator: @unittest.skipUnless(ut_data_exists("TGLXXXXBXH14P00S109/TPL/EnvironmentFile.env"), "Test data not available")

    :param path: path in unittest folder
    :return:
    """
    from setenv_unittest import UT_DIR
    return os.path.exists(os.path.join(UT_DIR, path))


def print_help():
    """
    Display the help message - need to add additional options
    """

    print('''
Usage: {name} [options] [test] [...]

Options:
  -h, --help       Show this message
  -v, --verbose    Verbose output
  -q, --quiet      Minimal output
  -f, --failfast   Stop on first failure
  -c, --catch      Catch control-C and display results
  -b, --buffer     Buffer stdout and stderr during test runs
  -s               Include slow tests (slow tests are skipped by default)
  -a               Automated test, will skip SKIP_NIGHTLY_BUILD
  -r               Skip SESLOW tests
  -o               Include optional tests (optional tests are skipped by default)
  -t               Display the time consumed per test
  -i               Run the tests independently
  -d               Set log.dev() to be displayed: OPT.devdebug=True
  -p               Skip pep8 check
  -notmpcheck      Do not perform undeleted tmp file check
  -co              Update pytpd-unittest repo to expected sha

Examples:
  {name} -v -b             - run default set of tests, suppressing stdout
  {name} -v MyTests        - run all tests in class MyTests
  {name} -v MyTests.test1  - run specific test MyTests.test1
  {name} -v -b -t          - Display the time consumed per test
  {name} -v -b -s          - include slow tests

'''.format(name=os.path.basename(sys.argv[0])))

    exit(0)

#################################################
# Assign module variables
#################################################


is_ut_option = UT_Options({'-s': "SLOW",
                           '-o': "OPTIONAL",
                           '-t': "TIMEIT",
                           '-a': "SKIP_NIGHTLY_BUILD",
                           '-r': "SESLOW",
                           '-d': "DEV_DEBUG",
                           '-p': "NO_PEP8",
                           '-notmpcheck': "NOTMPCHECK"})


class TestPEP8(_TestPEP8):

    @orig_unittest.skipIf(*is_ut_option('NO_PEP8', message='skipped because of -p option', neg=False))
    @orig_unittest.skipIf(IS_WIN, 'unix only because of pycodestyle')
    @orig_unittest.skipIf(is_cov(), 'No pep8 on coverage (slow)')
    def test_PEP8(self):    # pragma: no cover
        self.do_PEP8()
        # self.do_checkenv()
        result = self.do_duplicate_testname(realpath(__main__.__file__))
        self.assertIsNone(result, f'Duplicate [def {result}]! This is quality problem as it masks the test')

    def test_check_unittest_sha(self):
        # This test will check if sha of unittest_sha.txt match actual sha of unittest repo
        from gadget.getgit import GetGit
        from main.test.setenv_unittest import ROOT_ENV, UT_DIR_REPO
        from gadget.disk import Chdir
        with Chdir(UT_DIR_REPO):
            actual_sha = GetGit().get_currentsha()    # actual sha of repo
        expected_sha = File(f"{ROOT_ENV}/unittest_sha.txt").read().strip()
        self.assertTrue(actual_sha == expected_sha,
                        (f"Incorrect pytpd-unittest repo sha. Read below:\n"
                         f"   Expecting sha: {expected_sha} (specified in unittest_sha.txt).\n"
                         f"   Checkout sha:  {actual_sha}\n"
                         f"   Pls update your ../pytpd-unittest repo, or add -co in the unittest command to auto-update"))

    @staticmethod
    def do_duplicate_testname(utfile):
        """
        Check if there is a duplicate definition of a test
        Since python does not error out and the test is mask if developer copy+paste the test
        and forget to change the def name
        """
        found = set()
        robj = re.compile(r'^\s*def (test\w+)')
        for line in File(utfile):
            if line.strip().startswith('#'):
                continue
            if line.startswith('class '):
                found = set()   # reset
            res = robj.search(line)
            if res:
                name = res.group(1)
                if name in found:
                    return name
                found.add(res.group(1))
        return None


def trim_traceback_without_code(traceback: str):
    """
    Remove source code lines and their caret (^) indicator lines from a traceback.

    In some Python traceback formats, exception output may include
    the offending source line and a subsequent line consisting of one or more '^'
    characters that point to the error location. This function strips those lines
    to produce a cleaner traceback that contains only the stack and error message.

    :param traceback: the original traceback string.
    :return: list of the filtered traceback lines.
    """
    lines = traceback.split('\n')
    out = []

    skip_caret = False
    for line in lines:
        # Skip the ^^^^ indicator line that follows the code line.
        if skip_caret and re.match(r"^\s*\^+", line):
            skip_caret = False
            continue
        skip_caret = False

        # Skip the code line (typically indented by four spaces and not a File ... line).
        if line.startswith("    ") and "File " not in line:
            skip_caret = True
            continue

        # Also skip any ^^^^ indicator lines that appear on their own.
        if re.match(r"^\s*\^+", line):
            continue

        out.append(line)

    return out


# force chdir to a read-only directory. This will force unit test writers to make their test not to write in cwd.
# commented below: it will not work for __file__ use. long term: uncomment this, fix test that use __file__ and
# provide method for realpath of __file__ os.chdir(os.path.dirname(sys.executable))

if iseclipse_ut():  # pragma: no cover   # set slowtest to True always for Eclipse, since Eclipse can control it
    is_ut_option.set_option("SLOW", True)

# Instantiate class if NOTMPCHECK not existing
if is_ut_option("NOTMPCHECK", message="")[0]:
    checktmpdir = CheckTmpDir()

if '-h' in sys.argv:  # pragma: no cover    # tested separately
    print_help()

if '-co' in sys.argv:   # pragma: no cover    # tested manually (two cases: sha already correct and sha is incorrect)
    sys.argv.remove('-co')     # So it will proceed
    from gadget.getgit import GetGit
    from main.test.setenv_unittest import ROOT_ENV, UT_DIR_REPO
    from gadget.disk import Chdir

    expected_sha = File(f"{ROOT_ENV}/unittest_sha.txt").read().strip()
    with Chdir(UT_DIR_REPO):
        previous_sha = GetGit().get_currentsha()    # actual sha of repo
        if expected_sha == previous_sha:
            print("[-co]: Nothing to do. Current sha is correct/expected.")
        else:
            print('[-co]: Updating ../pytpd-unittest checkout:')
            SystemCall(f'git fetch').run(disp=True)
            SystemCall(f'git checkout {expected_sha}').run(disp=True)
            current_sha = GetGit().get_currentsha()    # actual sha of repo
            print()
            print(f'Previous sha: {previous_sha}')
            print(f'Expected sha: {expected_sha}')
            print(f'Current  sha: {current_sha}')
            print()
            assert current_sha == expected_sha, 'Something went wrong with checkout. Check above log from git.'

if not is_ut_option("DEV_DEBUG", message="")[0]:  # pragma: no cover - manual test   # is_ut_option() is negative logic
    OPT.devdebug = True

if '-i' in sys.argv:  # pragma: no cover    # Execute the tests independently
    IndependentExec().main(sys.argv[0],      # Cannot be run in eclipse, need -i option anyway
                           arg_s='-s' in sys.argv,
                           arg_o='-o' in sys.argv)
    exit(0)   # do not proceed
