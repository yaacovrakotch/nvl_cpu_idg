#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Unittests for pylog
"""
from setenv_unittest import ROOT_ENV     # must be first import for unittests
import sys
import os
import re
import time
from os.path import join, exists
from io import StringIO
from gadget.helperclass import OPT, CaptureStdoutLog
from gadget.files import TempName, File, TempDir
from gadget.shell import SystemCall
from gadget.gizmo import MockVar, count_iter
from gadget.ut import TestCase, unittest, is_ut_option
from gadget import pylog
from gadget.pylog import log, VepLog, LOGLEVELS, logging
from unittest.mock import Mock


def simple_line_count(out):
    """
    Windows will mark the position of abnormal lines,
    which will cause the output line count to differ when calculated.
    This interface will remove the marked line for easier calculation.
    """
    _out = re.sub(r'^\s*\^+\s*$', '', out, flags=re.MULTILINE)
    lines = [line for line in _out.split('\n') if line.strip()]
    return len(lines)


class AA_log_tests(TestCase):
    """This test must be first"""

    def test_first_test(self):
        self.assertFalse(log.is_file_set_once)
        with TempDir(name=True) as tdir:
            log.file(join(tdir, "f1"), usetmp=False)
            log.info("Text1")
            log.info("Text2")
            self.assertTrue(exists(join(tdir, "f1")))
            self.assertTrue(log.is_file_set_once)
            self.assertTrue(VepLog.is_file_set_once)

            # another file
            log.file(join(tdir, "f3"), usetmp=False)
            log.info("Text5")
            log.info("Text6")
            self.assertTrue(exists(join(tdir, "f3")))

            self.assertIn('Text1', File(join(tdir, "f1.gz")).fh().read())
            self.assertIn('Text2', File(join(tdir, "f1.gz")).fh().read())
            self.assertIn('Text5', File(join(tdir, "f3")).fh().read())
            self.assertIn('Text6', File(join(tdir, "f3")).fh().read())


class Veplog_tests(TestCase):

    def setUp(self):
        self.tmpdir = TempDir()
        self.tmp = join(self.tmpdir.name(), 'tmp.name')
        self.app = join(self.tmpdir.name(), 'tmp.app')

    def tearDown(self):
        self.tmpdir.close()

    def test_default_fmt(self):
        """
        Testing default behaviour of log straight after import. Currently: stdout('DEBUG')
        """
        code = '''#!%(exec)s
import sys
from gadget.pylog import log
log.dev("dev")
log.debug("debug")
log.info("info")
log.warning("warn")
log.critical("crit")
log.error("err")
''' % {'exec': sys.executable}

        # print(code)
        open(self.tmp, "w").write(code)
        os.chmod(self.tmp, 0o750)
        res = SystemCall(self.tmp, exe=True).run_outonly()
        # print res
        self.assertRegex(res, r"\s*DEBUG\s*: debug\n")
        self.assertRegex(res, r"\n\s*info\n")
        self.assertRegex(res, r"\n\s*WARNING\s*: warn\n")
        self.assertRegex(res, r"\n\s*CRITICAL\s*: crit\n")
        self.assertRegex(res, r"\n\s*ERROR\s*: err")

    def test_basicfile(self):
        """
        test: Basic test, logger to a file
        """
        # Basic test
        log.file(self.app)
        log.info("info1")
        log.debug("debug2")
        log.close()
        res = File(self.app + ".gz").fh().read()
        self.assertIn('info1', res)
        self.assertIn('debug2\n', res)

        # initialize again
        with TempDir(name=True) as tdir:
            log.file(join(tdir, "f1"), usetmp=False)
            log.info("Text1")
            log.info("Text2")
            logpath = log.get_logpath()
            self.assertTrue(exists(join(tdir, "f1")))
            self.assertEqual(logpath, join(tdir, "f1"))
            # Note: there is no close here
            self.assertIn('Text1', File(join(tdir, "f1")).fh().read())
            self.assertIn('Text2', File(join(tdir, "f1")).fh().read())

    def test_loglong(self):
        """
        test: loglong
        """
        # Note that logger is a global module, so it does not re-initialize when it is already initialized

        vlog = VepLog()
        self.assertNotEqual(vlog.fmt_file, vlog.fmt_stdout)
        with MockVar(OPT, "loglong", True):
            vlog.file(self.app)
        self.assertNotEqual(vlog.fmt_file, vlog.fmt_stdout)
        vlog.close()

        vlog = VepLog()
        self.assertNotEqual(vlog.fmt_file, vlog.fmt_stdout)
        vlog.file(self.app)
        self.assertEqual(vlog.fmt_file, vlog.fmt_stdout)
        vlog.close()

    def test_dev(self):
        """
        test: dev use
        """
        # No OPT
        with MockVar(OPT, "devdebug", False):
            log.file(self.app)
            log.dev("info1")
            log.dev("debug2")
        log.close()
        res = File(self.app + ".gz").fh().read()
        self.assertEqual(res, '')

        # with Opt
        with MockVar(OPT, "devdebug", True):
            log.file(self.app)
            log.dev("info1")
            log.dev("debug2")
        log.close()
        res = File(self.app + ".gz").fh().read()
        self.assertIn('info1', res)
        self.assertIn('debug2', res)

    def test_devdebug_level(self):
        """
        Test: dev use should print a new levelname (DEVDEBUG) when levelname is in fmt_stdout
        """
        # Devdebug true, log.file()
        with MockVar(OPT, "devdebug", True):
            # log.fmt_file will take the same value upon log.file() - no loglong given
            log.fmt_stdout = "%(levelname)8s: %(message)s"
            # sets log.fmt_file = log.fmt_stdout
            log.file(self.app)
            log.dev("debug1")
            log.fmt_stdout = "%(message)s"
            log.dev("debug2")
        log.close()
        # Only now will the self.app+".gz" logfile be created!
        res = File(self.app + ".gz").fh().read()
        self.assertRegex(res, r"DEVDEBUG\s*: debug1\n")
        self.assertRegex(res, r"DEVDEBUG\s*: debug2\n")

        with MockVar(OPT, "devdebug", True):
            log.fmt_stdout = "%(message)s"
            log.file(self.app)
            log.dev("debug3")
        log.close()
        # Only now will the self.app+".gz" logfile be created!
        res = File(self.app + ".gz").fh().read()
        self.assertRegex(res, r"\n*\s*debug3\n")
        self.assertNotRegexpMatches(res, "\nDEVDEBUG: debug3\n")

    def test_devdebug_print(self):
        """
        Test devdebug in stdout vs print mode
        """
        # Devdebug in stdout mode
        with MockVar(OPT, "devdebug", True), MockVar(sys, "stdout", StringIO()) as p:
            log.fmt_stdout = "%(levelname)8s: %(message)s"
            # Making sure switching file->stdout doesn't muck it up
            log.file(self.app)
            log.stdout("DEBUG")
            log.dev("stdout_dev")
            log.set_log_methods_to_print()
            log.dev("print_dev")
            log.debug("debug")
        # print p.getvalue()
        self.assertRegex(p.getvalue(), "DEVDEBUG: stdout_dev\n")
        self.assertRegex(p.getvalue(), r"\n\s*print_dev\n")
        self.assertNotRegexpMatches(p.getvalue(), r"\n\s*DEVDEBUG: print_dev\n")
        self.assertRegex(p.getvalue(), r"\n\s*debug\n")
        self.assertNotRegexpMatches(p.getvalue(), r"\n\s*DEBUG: debug\n")

    def test_withstdout(self):
        """
        Test: File (do not use tmp) with stdout
        """
        vlog = VepLog()
        # Just to hide the stdout output
        with MockVar(sys, "stdout", StringIO()) as p:
            vlog.filestdout(self.app, string_level="DEBUG", usetmp=False)
            self.assertRaises(Exception, vlog.file, string_level="INVALIDTEXT")
            vlog.info("info1")
            vlog.debug("debug2")
            vlog.close()
        res = File(self.app + ".gz").fh().read()
        # print res
        self.assertIn("info1", res)
        self.assertIn("debug2", res)
        self.assertEqual(len(res.split('\n')), 3)

    def test_errorcheck(self):
        # test: Various Exception cases
        vlog = VepLog()
        vlog.stdout()

        self.assertRaisesRegex(Exception, "Provided log", vlog._get_level, "UNKNOWNLEVEL")

        self.assertRaises(Exception, pylog.log.info, "abc", "def")

    def test_set_verbosity_stdout(self):
        """
        Testing default behaviour of setting verbosity on the fly
        """
        with MockVar(sys, "stdout", StringIO()) as p:
            # Log INFO and up
            log.stdout("INFO")
            log.dev("dev1")
            log.debug("debug1")
            log.info("info1")
            log.warning("warn1")
            log.error("err1")
            log.critical("crit1")
            # Log ERROR and up
            log.set_verbosity("ERROR")
            log.dev("dev2")
            log.debug("debug2")
            log.info("info2")
            log.warning("warn2")
            log.error("err2")
            log.critical("crit2")
            # Prints - log everything regardless of level
            log.set_log_methods_to_print()
            self.assertEqual(log.set_verbosity("CRITICAL"), "ERROR")   # previous verbosity
            log.dev("dev3")
            log.debug("debug3")
            log.info("info3")
            log.warning("warn3")
            log.error("err3")
            log.critical("crit3")

            res = p.getvalue()

        # print res
        # We test for verbosity level change - and not format here...
        self.assertNotIn("dev1", res)
        self.assertNotIn("debug1", res)
        self.assertIn("info1", res)
        self.assertIn("warn1", res)
        self.assertIn("err1", res)
        self.assertIn("crit1", res)
        self.assertNotIn("dev2", res)
        self.assertNotIn("debug2", res)
        self.assertNotIn("info2", res)
        self.assertNotIn("warn2", res)
        self.assertIn("err2", res)
        self.assertIn("crit2", res)

    def test_set_verbosity_error(self):
        """
        Testing default setting an illegal verbosity (logging) level
        """

        with MockVar(sys, "stdout", StringIO()) as p:
            # Log INFO and up
            log.stdout("INFO")
            log.info("info1")
            self.assertRaises(Exception, log.set_verbosity, "NOTALEVEL")
            log.info("info2")
        res = p.getvalue()
        # print res
        self.assertIn("info1", res)
        self.assertIn("info2", res)

    def test_libcall(self):
        # test: run executable and import a library that imports utils.veplog and calls log.info
        tmp2 = join(self.tmpdir.name(), 'tmp2')
        self.main = tmp2 + "_main.py"
        self.lib = tmp2 + "_lib"
        libname = os.path.basename(self.lib)
        self.lib += ".py"

        # Main executable
        code = '#!%s\n' \
               'import sys\n' \
               'import %s as mylib\n' \
               'from gadget.pylog import log\n' \
               'log.fmt_stdout_info = "HEADER %s"\n' \
               'log.stdout(string_level="INFO")\n' \
               'log.info("info1")\n' \
               'mylib.foo()\n' % (sys.executable, libname, "%(message)s")

        print("\n# main FileName: ", self.main)
        print(code)
        with open(self.main, "w") as fh:
            fh.write(code)
        os.chmod(self.main, 0o750)

        # Library
        code = '#!%s\n'\
               'import sys\n'\
               'from gadget.pylog import log\n'\
               'def foo():\n'\
               '   log.info("in lib")\n' % sys.executable

        print("# lib FileName: ", self.lib)
        print(code)
        with open(self.lib, "w") as fh:
            fh.write(code)
        os.chmod(self.lib, 0o750)
        if 'PYTHONDONTWRITEBYTECODE' in os.environ:
            del os.environ['PYTHONDONTWRITEBYTECODE']
        code, stdouterr = SystemCall(self.main, exe=True).run_outtxt()
        time.sleep(1)
        print(" cmd %s: self.lib %s, self.main %s, code %s,\n stdouterr %s" % (self.main, self.lib, self.main, code, stdouterr))
        os.unlink(self.main)
        os.unlink(self.lib)
        if exists(self.lib + "c"):  # Not being created in Python 3
            os.unlink(self.lib + "c")
        self.assertEqual(stdouterr, 'HEADER info1\nHEADER in lib')

    def test_file_changeformat(self):
        """
        Making sure file() mode takes formatting from fmt_stdout, and sets info()
        formatting to be the same as everything else
        """
        # test: log.file(), run from a script
        with TempDir(name=True) as tdir:
            code = '''#!{exe}
import sys
from gadget.pylog import log
log.fmt_stdout = "SOMEPREFIX: %(asctime)s %(message)s"
log.file(r'{tdir}/log1')
log.info("info1")
log.debug("debug1")
log.critical("critical1")
'''.format(exe=sys.executable,
                tdir=tdir)

            # print(code)
            open(self.tmp, "w").write(code)
            os.chmod(self.tmp, 0o750)
            code, res, err = SystemCall(self.tmp, exe=True).run_sout_serr()

            self.assertFalse(code)
            self.assertEqual(res, '')
            self.assertEqual(err, '')

            logfile = File(join(tdir, 'log1'), autofind=True).read()
            # print "====== OUTPUT start"
            # print logfile
            # print "====== OUTPUT end"

            self.assertIn('info1', logfile)
            self.assertIn('debug1', logfile)
            self.assertIn('critical1', logfile)
            self.assertIn('SOMEPREFIX', logfile)

    def test_file(self):
        # test: log.file(), run from a script
        with TempDir(name=True) as tdir:
            code = '''#!{exe}
import sys
from gadget.pylog import log
log.file(r'{tdir}/log1')
log.info("info1")
log.debug("debug1")
log.critical("critical1")
'''.format(exe=sys.executable,
                tdir=tdir)

            # print(code)
            open(self.tmp, "w").write(code)
            os.chmod(self.tmp, 0o750)
            code, res, err = SystemCall(self.tmp, exe=True).run_sout_serr()

            # print "======\nOUTPUT:\n", res
            self.assertFalse(code)
            self.assertEqual(res, '')
            self.assertEqual(err, '')

            logfile = File(join(tdir, 'log1'), autofind=True).read()
            self.assertIn('info1', logfile)
            self.assertIn('debug1', logfile)
            self.assertIn('critical1', logfile)

    def test_file_exception2(self):
        with TempDir(name=True) as tdir:
            code = '''#!{exe}
import sys
from gadget.pylog import log
from gadget.files import File
def raisef(*args):
    raise OSError("some_error_compress")
File.compress = raisef
log.file(r'{tdir}/log1')
log.info("info1")
log.debug("debug1")
log.critical("critical1")
'''.format(exe=sys.executable,
                tdir=tdir)

            # print(code)
            open(self.tmp, "w").write(code)
            os.chmod(self.tmp, 0o750)
            code, res, err = SystemCall(self.tmp, exe=True).run_sout_serr()

            # print "======\nOUTPUT:\n", res
            self.assertFalse(code)
            self.assertEqual(res, '-i- Warning: Rename+compress failed: some_error_compress')
            self.assertEqual(err, '')

            logfile = File(join(tdir, 'log1'), autofind=True).read()
            self.assertIn('info1', logfile)
            self.assertIn('debug1', logfile)
            self.assertIn('critical1', logfile)

    def test_stdout(self):
        # test: stdout check, run from a script
        code = '''#!{exe}
import sys
from gadget.pylog import log
log.fmt_stdout = "%(levelname)8s: %(message)s"
log.stdout(string_level="INFO")
log.info("info1")
log.debug("debug1")
log.critical("critical1")
'''.format(exe=sys.executable)

        # print(code)
        open(self.tmp, "w").write(code)
        os.chmod(self.tmp, 0o750)
        res = SystemCall(self.tmp, exe=True).run_outonly()
        # print "======\nOUTPUT:\n", res
        self.assertIn('info1', res)
        self.assertIn('critical1', res)

    @unittest.skipIf(*is_ut_option('OPTIONAL', message="This test must be run by itself"))
    def test_stdoutfirst(self):
        # This test must be run by itself.
        # This tests stdout as the first setup
        with MockVar(sys, "stdout", StringIO()) as p:
            log.stdout()
            log.info("line1")
            log.debug("line2d")
            self.assertIn('line1\n', p.getvalue())
            self.assertIn('DEBUG: line2d\n', p.getvalue())

    def test_copy(self):
        # This also tests log.file(None) usage
        with TempDir(name=True) as tdir:
            log.file(None)     # This is intentional
            log.info("line1")
            log.debug("line2d")
            log.copy(join(tdir, "f1copy"))
            log.copy(join(tdir, "f2copy"))
            self.assertTrue(exists(log.tmpname))
            log.close()
            self.assertFalse(exists(log.tmpname))

            self.assertIn('line1', File(join(tdir, "f1copy")).fh().read())
            self.assertIn('line2d', File(join(tdir, "f1copy")).fh().read())
            self.assertIn('line1', File(join(tdir, "f2copy")).fh().read())
            self.assertIn('line2d', File(join(tdir, "f2copy")).fh().read())

    def test_stdout_exception(self):
        """
        test: stdout with exception, run from a script
        """
        code = '''#!%(exec)s
import sys
from gadget.pylog import log
log.stdout()
log.info("info1")
if abc>1: pass
log.debug("debug1")
''' % {'exec': sys.executable}

        # print(code)
        open(self.tmp, "w").write(code)
        os.chmod(self.tmp, 0o750)
        code, res, err = SystemCall(self.tmp, exe=True).run_sout_serr()
        # print "===== err message"
        # print res
        self.assertIn("info1", res)
        self.assertIn("NameError:", res)
        self.assertEqual(simple_line_count(res), 6)
        self.assertEqual(simple_line_count(err), 4)

    def test_file_exception(self):
        # test: file with exception check, no stdout output, run from a script
        code = '''#!%(exec)s
import sys
from gadget.pylog import log
log.file(r"%(app)s",usetmp=False)
log.info("info1")
if abc>1: pass
log.debug("debug1")
''' % {
            'exec': sys.executable,
            'app': self.app}

        # print(code)
        open(self.tmp, "w").write(code)
        os.chmod(self.tmp, 0o750)
        code, res, err = SystemCall(self.tmp, exe=True).run_sout_serr()
        self.assertEqual(res, '')    # there should be no stdout output
        self.assertEqual(simple_line_count(err), 4)
        res = File(self.app + ".gz").fh().read()
        self.assertRegex(res, 'NameError:.*is not defined')
        self.assertEqual(simple_line_count(res), 6)

    def test_file_stdout(self):
        # test: file and stdout together
        code = '''#!%(exec)s
import sys
from gadget.pylog import log
log.filestdout(r"%(app)s",usetmp=False)
log.info("i1")
log.info("i2")
log.debug("debug1")
''' % {
            'exec': sys.executable,
            'app': self.app
        }

        # print(code)
        open(self.tmp, "w").write(code)
        os.chmod(self.tmp, 0o750)
        res = SystemCall(self.tmp, exe=True).run_outonly()
        self.assertIn('i1', res)
        self.assertIn('i2', res)
        self.assertIn('debug1', res)
        res = File(self.app + ".gz").fh().read()
        # print "Result text:==========="
        # print res
        self.assertIn('i1', res)
        self.assertIn('i2', res)
        self.assertIn('debug1', res)

    def test_file_stdout_loglong(self):
        # test: file and stdout together
        code = '''#!%(exec)s
import sys
from gadget.pylog import log
from gadget.helperclass import OPT
OPT.loglong = True
log.filestdout(r"%(app)s",usetmp=False)
log.info("i1")
log.info("i2")
log.debug("debug1")
''' % {
            'exec': sys.executable,
            'app': self.app}

        # print(code)
        open(self.tmp, "w").write(code)
        os.chmod(self.tmp, 0o750)
        res = SystemCall(self.tmp, exe=True).run_outonly()
        self.assertIn('i1', res)
        self.assertIn('i2', res)
        self.assertIn('debug1', res)
        res = File(self.app + ".gz").fh().read()
        # print "Result text:==========="
        # print res
        self.assertNotEqual(res, 'i1\ni2\ndebug1\n')
        self.assertEqual(len(res.split('\n')), 4)

    def test_filestdout(self):
        with TempDir(name=True) as tmp_log_filename, MockVar(sys, "stdout", StringIO()) as p:
            log.filestdout(filename=join(tmp_log_filename, "f1"), usetmp=False)
            log.info("line1")
            log.warning("line2")
            fd = open(join(tmp_log_filename, "f1"), "r")
            fileout = fd.read()
            stdout = p.getvalue()
        self.assertEqual(fileout, stdout)
        self.assertIn("line1", fileout)
        self.assertIn("line2", fileout)

    def test_filemixed(self):
        """
        Test: test filemixed mode (info/dev -> both, rest to file only) no devdebug in OPT
        """
        # Note that logger is a global module, so it does not re-initialize when it is already initialized
        vlog = VepLog()
        with MockVar(sys, "stdout", StringIO()) as p,\
                MockVar(OPT, "devdebug", True):
            vlog.filemixed(self.app)
            vlog.info("info1")
            vlog.info("info2")
            vlog.dev("dev")
            vlog.debug("debug")
            vlog.warning("warn")
            vlog.error("err")
            vlog.critical("crit")
            vlog.close()
        res_stdout = p.getvalue()
        # print res_stdout
        self.assertIn('info1', res_stdout)
        self.assertIn('info2', res_stdout)
        self.assertIn('dev', res_stdout)
        self.assertNotIn('debug', res_stdout)
        self.assertNotIn('warn', res_stdout)
        self.assertNotIn('err', res_stdout)
        self.assertIn('crit', res_stdout)
        res_file = File(self.app + ".gz").fh().read()
        # print res_file
        self.assertIn('info1', res_file)
        self.assertIn('info2', res_file)
        self.assertIn('dev', res_file)
        self.assertIn('debug', res_file)
        self.assertIn('warn', res_file)
        self.assertIn('err', res_file)
        self.assertIn('crit', res_file)

    def test_filemixed_code(self):
        """
        Test: file mixed via cmd_safe execution, without devdebug
        """
        code = '''#!%(exec)s
import sys
from gadget.pylog import log
log.filemixed(r"%(app)s")
log.info("i1")
log.dev("dev1")
log.info("i2")
log.debug("debug1")
''' % {
            'exec': sys.executable,
            'app': self.app}

        # print(code)
        open(self.tmp, "w").write(code)
        os.chmod(self.tmp, 0o750)
        res_stdout = SystemCall(self.tmp, exe=True).run_outonly()
        # print res_stdout
        self.assertIn('i1', res_stdout)
        self.assertIn('i2', res_stdout)
        self.assertNotIn('dev1', res_stdout)
        self.assertNotIn('debug1', res_stdout)
        res_file = File(self.app, autofind=True).fh().read()
        self.assertIn('i1', res_file)
        self.assertIn('i2', res_file)
        self.assertNotIn('dev1', res_file)
        self.assertIn('debug1', res_file)
        # print res_file
        self.assertEqual(len(res_file.split('\n')), 4)

    def test_file_stdout2(self):
        # test: file and stdout together: two files
        with TempName() as tn:
            t1 = tn.fname()
            t2 = tn.fname()
            code = '''#!%(exec)s
import sys
from gadget.pylog import log
log.filestdout(r"%(t1)s")
log.info("File1")
log.close()
log.filestdout(r"%(t2)s")
log.info("File2")
log.close()
    ''' % {
                'exec': sys.executable,
                't1': t1,
                't2': t2
            }

            # print(code)
            open(self.tmp, "w").write(code)
            os.chmod(self.tmp, 0o750)
            res = SystemCall(self.tmp, exe=True).run_outonly()
            self.assertIn('File1', res)
            self.assertIn('File2', res)
            self.assertIn('File1', File(t1, autofind=True).fh().read())
            self.assertIn('File2', File(t2, autofind=True).fh().read())
            self.assertEqual(count_iter(File(t1, autofind=True)), 1)
            self.assertEqual(count_iter(File(t2, autofind=True)), 1)

    def test_normal_print(self):
        vlog = VepLog()
        vlog.close()
        with MockVar(sys, "stdout", StringIO()) as p:
            vlog.info("line1")
            vlog.debug("line2d")
            vlog.flush("line3")
            self.assertEqual(p.getvalue(), 'line1\nline2d\nline3\n')

    def test_close(self):
        vlog = VepLog()
        vlog.tmpname = None
        vlog.close()    # should run ok

        vlog.tmpname = "/tmp/sure_not_exist_12_8_7_1"
        vlog.close()    # should run ok

        with TempDir(chdir=True, name=True) as td:
            File("abc").touch("aa1")
            vlog.tmpname = "abc"
            vlog.input_file = join(td, "newfile")
            vlog.s_setup = True
            vlog.close()
            self.assertEqual(File("newfile.gz").fh().read(), "aa1")
            self.assertRaises(IOError, File, "abc", autofind=True)

        # double close
        vlog.close()
        vlog.close()

    def test_postproc_XPRIV(self):
        vlog = VepLog()
        vlog.funclen = 15
        with TempDir(chdir=True, name=True) as td:
            File("abc").touch('''
2013-12-05 19:10:57,102 foo             This is debug
2013-12-05 19:10:57,102 foo             This is info
2013-12-05 18:55:32,187 _infoXPRIV      12345678901234 This is info1
2013-12-05 18:55:32,187 _infoXPRIV      123456789012345 This is info1
2013-12-05 18:55:32,187 _infoXPRIV      12345678901234567 This is info1
2013-12-05 18:55:32,187 _infoXPRIV      f1 This is info2
''')
            vlog._postproc_XPRIV("abc")
            self.assertMultiLineEqual(File("abc").fh().read(), '''
2013-12-05 19:10:57,102 foo             This is debug
2013-12-05 19:10:57,102 foo             This is info
2013-12-05 18:55:32,187 12345678901234  This is info1
2013-12-05 18:55:32,187 123456789012345 This is info1
2013-12-05 18:55:32,187 12345678901234567 This is info1
2013-12-05 18:55:32,187 f1              This is info2
''')
            self.assertFalse(exists("abc.orig"), "file should not exist")

    def test_infoXPRIV(self):
        vlog = VepLog()
        vlog.set_log_methods_to_print()
        # Just prints once
        with MockVar(sys, "stdout", StringIO()) as p:
            # without OPT.long
            vlog._infoXPRIV("INF")
            self.assertEqual(p.getvalue(), "INF\n")
        vlog.stdout()
        vlog._vep_info = vlog._normal_print
        with MockVar(sys, "stdout", StringIO()) as p:
            # without OPT.long
            vlog._infoXPRIV("HELLO")
            self.assertEqual(p.getvalue(), "HELLO\nHELLO\n")

        with MockVar(sys, "stdout", StringIO()) as p:
            # with OPT.long
            with MockVar(OPT, "loglong", True):
                vlog._infoXPRIV("HELLO")
                self.assertEqual(p.getvalue(), 'HELLO\ntest_infoXPRIV HELLO\n')

    def test_devXPRIV(self):
        """
        Testing log._devXPRIV functionality, similar to _infoXPRIV
        """
        vlog = VepLog()
        vlog.set_log_methods_to_print()
        # No devdebug - nothing:
        with MockVar(sys, "stdout", StringIO()) as p,\
                MockVar(OPT, "devdebug", False):
            # without OPT.long
            vlog._devXPRIV("HELLO")
            self.assertEqual(p.getvalue(), "")
        # With devdebug
        with MockVar(sys, "stdout", StringIO()) as p,\
                MockVar(OPT, "devdebug", True):
            # without OPT.long
            vlog._devXPRIV("HELLO")
            self.assertEqual(p.getvalue(), "HELLO\nHELLO\n")

        with MockVar(sys, "stdout", StringIO()) as p:
            # with OPT.long
            with MockVar(OPT, "loglong", True), MockVar(OPT, "devdebug", True):
                vlog._devXPRIV("HELLO")
                self.assertEqual(p.getvalue(), 'HELLO\ntest_devXPRIV HELLO\n')

    def test_errcritXPRIV(self):
        """
        Testing log._errorXPRIV / log._critical functionality
        Currently if no self.log defined it will give only 1 output
        """
        vlog = VepLog()
        vlog.set_log_methods_to_print()
        # Just prints once
        with MockVar(sys, "stdout", StringIO()) as p:
            # without OPT.long
            vlog._errorXPRIV("ERR")
            vlog._criticalXPRIV("CRIT")
            self.assertEqual(p.getvalue(), "ERR\nCRIT\n")
        # Just prints once, again
        with MockVar(sys, "stdout", StringIO()) as p:
            # with OPT.long
            with MockVar(OPT, "loglong", True):
                vlog._errorXPRIV("ERR")
                vlog._criticalXPRIV("CRIT")
                self.assertEqual(p.getvalue(), 'ERR\nCRIT\n')

        with TempName() as tfile:
            vlog.filemixed(tfile.name(), usetmp=False)
            with MockVar(sys, "stdout", StringIO()) as p:
                # without OPT.long
                vlog._errorXPRIV("ERR1")
                vlog._criticalXPRIV("CRIT1")
            fileout = open(tfile.name()).read()
            self.assertIn("ERR1\n", p.getvalue())
            self.assertIn("CRIT1\n", fileout)
            # print fileout

            with MockVar(sys, "stdout", StringIO()) as p:
                # with OPT.long
                with MockVar(OPT, "loglong", True):
                    vlog._errorXPRIV("ERR2")
                    vlog._criticalXPRIV("CRIT2")
                fileout = open(tfile.name()).read()
                self.assertIn("ERR2\n", p.getvalue())
                self.assertIn("CRIT2\n", p.getvalue())
                self.assertIn("test_errcritXPRIV ERR2\n", fileout)
                self.assertIn("test_errcritXPRIV CRIT2\n", fileout)
            # print fileout
            vlog.close()
            os.unlink(tfile.name() + ".gz")

    def test_profileXPRIV(self):
        """
        Testing log._profileXPRIV functionality
        """
        vlog = VepLog()
        vlog.set_log_methods_to_print()
        # with OPT.print_profile is False
        with MockVar(sys, "stdout", StringIO()) as p:
            with MockVar(OPT, "print_profile", False):
                vlog._profileXPRIV("TEST_PROFILE", 0.2, 0.1)
            vlog.close()
            self.assertNotIn("TEST_PROFILE\n", p.getvalue())

        # with OPT.print_profile is True
        with MockVar(sys, "stdout", StringIO()) as p:
            with MockVar(OPT, "print_profile", True):
                vlog._profileXPRIV("TEST_PROFILE", 0.2, 0.1)
            vlog.close()
            self.assertIn("TEST_PROFILE\n", p.getvalue())

        # with OPT.loglong
        with MockVar(sys, "stdout", StringIO()) as p:
            # with OPT.long
            with MockVar(OPT, "loglong", True), MockVar(OPT, "print_profile", True):
                vlog._profileXPRIV("TEST_PROFILE", 0.2, 0.1)
                vlog.close()
                self.assertIn('TEST_PROFILE\n', p.getvalue())

    def test_profile(self):
        vlog = VepLog()
        vlog.set_log_methods_to_print()
        # with OPT.print_profile is False
        with MockVar(OPT, "print_profile", False), MockVar(sys, "stdout", StringIO()) as p:
            vlog.stdout("INFO")
            vlog.profile("info1", time=0.2, threshold=0.1)
            vlog.profile("debug2", time=0.1, threshold=0.2)
            vlog.close()
            self.assertNotIn('PROFILE : info1', p.getvalue())
            self.assertNotIn('debug2', p.getvalue())

        # with OPT.print_profile is True
        with MockVar(OPT, "print_profile", True), MockVar(sys, "stdout", StringIO()) as p:
            vlog.stdout("INFO")
            vlog.profile("info1", time=0.2, threshold=0.1)
            vlog.profile("debug2", time=0.1, threshold=0.2)
            vlog.close()
            self.assertIn('PROFILE : info1', p.getvalue())
            self.assertNotIn('debug2', p.getvalue())

        with MockVar(OPT, "print_profile", True), MockVar(sys, "stdout", StringIO()) as p:
            vlog.filestdout(self.app, usetmp=False)
            vlog._vep_profile("info1", time=0.2, threshold=0.1)
            vlog._vep_profile("debug2", time=0.1, threshold=0.2)
            vlog.close()
            res_file = File(self.app + ".gz").fh().read()
            # print res_file
            self.assertIn('info1', res_file)
            self.assertNotIn('debug2', res_file)

    def test_profile_filemixed(self):
        vlog = VepLog()
        vlog.loglevel = "PROFILE"
        with MockVar(OPT, "print_profile", True), \
                MockVar(vlog, "_str_to_record", Mock(return_value=vlog._str_to_record("profile1"))):
            vlog.filemixed(self.app, usetmp=False)
            vlog.profile("profile1", time=0.2, threshold=0.1)
            vlog.close()
            res_file = File(self.app + ".gz").fh().read()
            self.assertIn('profile1', res_file)

        with MockVar(OPT, "print_profile", True), MockVar(OPT, "loglong", True), \
                MockVar(vlog, "_str_to_record", Mock(return_value=vlog._str_to_record("profile1"))):
            vlog.filemixed(self.app, usetmp=False)
            vlog.profile("profile1", time=0.2, threshold=0.1)
            vlog.close()
            res_file = File(self.app + ".gz").fh().read()
            self.assertIn('test_profile_filemixed profile1', res_file)

    def test_change_file(self):
        with TempDir(name=True) as tdir:
            log.file(join(tdir, "f1"))
            log.info("Text1")
            log.info("Text2")
            self.assertFalse(exists(join(tdir, "f1")))

            log.file(join(tdir, "f3"), usetmp=False)
            log.info("Text5")
            log.info("Text6")
            self.assertTrue(exists(join(tdir, "f3")))

            log.file(join(tdir, "f2"))
            log.info("Text3")
            log.info("Text4")
            self.assertFalse(exists(join(tdir, "f2")))

            log.file(join(tdir, "f4"), usetmp=False)
            log.info("Text7")
            log.info("Text8")
            self.assertTrue(exists(join(tdir, "f4")))
            log.close()

            self.assertIn('Text1', File(join(tdir, "f1.gz")).fh().read())
            self.assertIn('Text2', File(join(tdir, "f1.gz")).fh().read())

            self.assertIn('Text3', File(join(tdir, "f2.gz")).fh().read())
            self.assertIn('Text4', File(join(tdir, "f2.gz")).fh().read())

            self.assertIn('Text5', File(join(tdir, "f3.gz")).fh().read())
            self.assertIn('Text6', File(join(tdir, "f3.gz")).fh().read())

            self.assertIn('Text7', File(join(tdir, "f4.gz")).fh().read())
            self.assertIn('Text8', File(join(tdir, "f4.gz")).fh().read())

    def test_change_filestdout(self):
        with MockVar(sys, "stdout", StringIO()) as p, TempDir(name=True) as tdir:
            log.filestdout(join(tdir, "f1"))
            log.info("Text1")
            log.info("Text2")
            self.assertFalse(exists(join(tdir, "f1")))

            log.filestdout(join(tdir, "f3"), usetmp=False)
            log.info("Text5")
            log.info("Text6")
            self.assertTrue(exists(join(tdir, "f3")))

            log.filestdout(join(tdir, "f2"))
            log.info("Text3")
            log.info("Text4")
            self.assertFalse(exists(join(tdir, "f2")))

            log.filestdout(join(tdir, "f4"), usetmp=False)
            log.info("Text7")
            log.info("Text8")
            self.assertTrue(exists(join(tdir, "f4")))
            log.close()

            self.assertIn('Text1', File(join(tdir, "f1.gz")).fh().read())
            self.assertIn('Text2', File(join(tdir, "f1.gz")).fh().read())

            self.assertIn('Text3', File(join(tdir, "f2.gz")).fh().read())
            self.assertIn('Text4', File(join(tdir, "f2.gz")).fh().read())

            self.assertIn('Text5', File(join(tdir, "f3.gz")).fh().read())
            self.assertIn('Text6', File(join(tdir, "f3.gz")).fh().read())

            self.assertIn('Text7', File(join(tdir, "f4.gz")).fh().read())
            self.assertIn('Text8', File(join(tdir, "f4.gz")).fh().read())

    def test_change_filemixed(self):
        with MockVar(sys, "stdout", StringIO()) as p,\
                TempDir(name=True) as tdir:
            log.filemixed(join(tdir, "f1"))
            log.info("Text1")
            log.debug("Text2")
            self.assertFalse(exists(join(tdir, "f1")))

            log.filemixed(join(tdir, "f3"), usetmp=False)
            log.info("Text5")
            log.debug("Text6")
            self.assertTrue(exists(join(tdir, "f3")))

            log.filemixed(join(tdir, "f2"))
            log.debug("Text3")
            log.info("Text4")
            self.assertFalse(exists(join(tdir, "f2")))

            log.filemixed(join(tdir, "f4"), usetmp=False)
            log.debug("Text7")
            log.debug("Text8")
            self.assertTrue(exists(join(tdir, "f4")))
            log.close()

            self.assertIn('Text1', File(join(tdir, "f1.gz")).fh().read())
            self.assertIn('Text2', File(join(tdir, "f1.gz")).fh().read())

            self.assertIn('Text3', File(join(tdir, "f2.gz")).fh().read())
            self.assertIn('Text4', File(join(tdir, "f2.gz")).fh().read())

            self.assertIn('Text5', File(join(tdir, "f3.gz")).fh().read())
            self.assertIn('Text6', File(join(tdir, "f3.gz")).fh().read())

            self.assertIn('Text7', File(join(tdir, "f4.gz")).fh().read())
            self.assertIn('Text8', File(join(tdir, "f4.gz")).fh().read())

            self.assertEqual(p.getvalue().split('\n'), ['Text1',
                                                        'Text5',
                                                        'Text4',
                                                        ''])

    def test_change_combination(self):
        with MockVar(sys, "stdout", StringIO()) as p,\
                TempDir(name=True) as tdir:
            log.fmt_stdout = "%(message)s"
            log.fmt_file = "%(message)s"
            log.file(join(tdir, "f1"))
            log.info("Text1")
            log.info("Text2")
            self.assertFalse(exists(join(tdir, "f1")))

            log.filemixed(join(tdir, "f3"), usetmp=False)
            log.info("Text5")
            log.info("Text6")
            self.assertTrue(exists(join(tdir, "f3")))

            log.filestdout(join(tdir, "f2"))
            log.info("Text3")
            log.info("Text4")
            self.assertFalse(exists(join(tdir, "f2")))

            log.filemixed(join(tdir, "f4"), usetmp=False)
            log.info("Text7")
            log.info("Text8")
            self.assertTrue(exists(join(tdir, "f4")))
            log.close()

            self.assertIn('Text1', File(join(tdir, "f1.gz")).fh().read())
            self.assertIn('Text2', File(join(tdir, "f1.gz")).fh().read())

            self.assertIn('Text3', File(join(tdir, "f2.gz")).fh().read())
            self.assertIn('Text4', File(join(tdir, "f2.gz")).fh().read())

            self.assertIn('Text5', File(join(tdir, "f3.gz")).fh().read())
            self.assertIn('Text6', File(join(tdir, "f3.gz")).fh().read())

            self.assertIn('Text7', File(join(tdir, "f4.gz")).fh().read())
            self.assertIn('Text8', File(join(tdir, "f4.gz")).fh().read())

            self.assertEqual(['Text5',
                              'Text6',
                              'Text3',
                              'Text4',
                              'Text7',
                              'Text8',
                              ''], p.getvalue().split('\n'))

    def test_change_comball(self):
        # Test all combinations of setup:
        #    file filemixed filestdout stdout
        #     1      1
        #     2                2
        #     3                           3
        #            4         4
        #            5                    5
        #                      6          6

        with MockVar(sys, "stdout", StringIO()) as p, TempDir(name=True) as tdir:
            log.fmt_stdout = "%(message)s"
            # case1  (look at next two cases)
            log.file(join(tdir, "f1"), usetmp=False)
            log.info("Text1")
            log.debug("Text2")

            # case1r (look at next two cases)
            log.filemixed(join(tdir, "f2"), usetmp=False)
            log.info("Text3")
            log.debug("Text4")

            # case3
            log.file(join(tdir, "f3"), usetmp=False)
            log.info("Text5")
            log.debug("Text6")

            # case3r
            log.stdout()
            log.info("Text7")
            log.debug("Text8")

            # case2
            log.file(join(tdir, "f4"), usetmp=False)
            log.info("Text9")
            log.debug("Text10")

            # case 4r
            log.filestdout(join(tdir, "f5"), usetmp=False)
            log.info("Text11")
            log.debug("Text12")

            # case 4
            log.filemixed(join(tdir, "f6"), usetmp=False)
            log.info("Text13")
            log.debug("Text14")

            # case 6
            log.filestdout(join(tdir, "f7"), usetmp=False)
            log.info("Text15")
            log.debug("Text16")

            # case 5r
            log.stdout()
            log.info("Text17")
            log.debug("Text18")

            # case 5
            log.filemixed(join(tdir, "f8"), usetmp=False)
            log.info("Text19")
            log.debug("Text20")

            # case 6r
            log.stdout()
            log.info("Text21")
            log.debug("Text22")

            log.filestdout(join(tdir, "f9"), usetmp=False)
            log.info("Text23")
            log.debug("Text24")

            self.assertIn('Text1', File(join(tdir, "f1.gz")).fh().read())
            self.assertIn('Text2', File(join(tdir, "f1.gz")).fh().read())

            self.assertIn('Text3', File(join(tdir, "f2.gz")).fh().read())
            self.assertIn('Text4\n', File(join(tdir, "f2.gz")).fh().read())

            self.assertIn('Text5', File(join(tdir, "f3.gz")).fh().read())
            self.assertIn('Text6', File(join(tdir, "f3.gz")).fh().read())

            self.assertIn('Text9', File(join(tdir, "f4.gz")).fh().read())
            self.assertIn('Text10', File(join(tdir, "f4.gz")).fh().read())

            self.assertIn('Text11', File(join(tdir, "f5.gz")).fh().read())
            self.assertIn('Text12', File(join(tdir, "f5.gz")).fh().read())

            self.assertIn('Text13', File(join(tdir, "f6.gz")).fh().read())
            self.assertIn('Text14', File(join(tdir, "f6.gz")).fh().read())

            self.assertIn('Text15', File(join(tdir, "f7.gz")).fh().read())
            self.assertIn('Text16', File(join(tdir, "f7.gz")).fh().read())

            self.assertIn('Text19', File(join(tdir, "f8.gz")).fh().read())
            self.assertIn('Text20', File(join(tdir, "f8.gz")).fh().read())

            self.assertIn('Text23', File(join(tdir, "f9")).fh().read())
            self.assertIn('Text24', File(join(tdir, "f9")).fh().read())

            self.assertEqual(p.getvalue().split('\n'), ['Text3',
                                                        'Text7',
                                                        'Text8',
                                                        'Text11',
                                                        'Text12',
                                                        'Text13',
                                                        'Text15',
                                                        'Text16',
                                                        'Text17',
                                                        'Text18',
                                                        'Text19',
                                                        'Text21',
                                                        'Text22',
                                                        'Text23',
                                                        'Text24',
                                                        ''])

    def test_change_filemixed_secondary_and_back(self):
        """
        Test functionality of secondary logger arg. Meaning:
        a. write to logfile a
        b. change to logfile b without closing loggfile a
        c. write to logfile b
        d. change back to logfile a, NOT closing logfile b
        e. close logfile a
        ENDSTATE: 2 logs, only a is gzipped.
        REMINDER: debug prints go to file only in "filemixed mode"
        """
        with MockVar(sys, "stdout", StringIO()) as p, TempDir(name=True) as tdir:
            log.fmt_stdout = "%(message)s"
            # Default is: secondary_logger=False
            log.filemixed(join(tdir, "log_a"), string_level="DEBUG", usetmp=False)
            log.info("log_a_info")
            log.debug("log_a_debug")
            log.filemixed(join(tdir, "log_b"), string_level="DEBUG", secondary_logger=True, usetmp=False)
            log.info("log_b_info")
            log.debug("log_b_debug")
            # Default is: secondary_logger=False, this will close log_b
            log.filemixed(join(tdir, "log_a"), string_level="DEBUG", usetmp=False)
            log.info("log_a_info2")
            log.debug("log_a_debug2")
            log.close()

            # print os.listdir(tdir)
        # print p.getvalue()
            self.assertEqual(['log_a_info',
                              'log_b_info',
                              'log_a_info2',
                              ''], p.getvalue().split('\n'))
            self.assertFalse(exists(join(tdir, "log_a")))
            self.assertFalse(exists(join(tdir, "log_b.gz")))

            self.assertTrue(exists(join(tdir, "log_a.gz")))
            self.assertTrue(exists(join(tdir, "log_b")))

            self.assertIn('log_a_info', File(join(tdir, "log_a.gz")).read())
            self.assertIn('log_a_debug', File(join(tdir, "log_a.gz")).read())
            self.assertIn('log_a_info2', File(join(tdir, "log_a.gz")).read())
            self.assertIn('log_a_debug2', File(join(tdir, "log_a.gz")).read())
            self.assertIn('log_b_info', File(join(tdir, "log_b")).read())
            self.assertIn('log_b_debug', File(join(tdir, "log_b")).read())
            self.assertNotIn('log_b_info', File(join(tdir, "log_a.gz")).read())
            self.assertNotIn('log_b_debug', File(join(tdir, "log_a.gz")).read())
            self.assertNotIn('log_a_info2', File(join(tdir, "log_b")).read())
            self.assertNotIn('log_a_debug2', File(join(tdir, "log_b")).read())

    def test_str_to_record(self):
        """
        Test conversion of string to LogRecord
        """
        rec = log._str_to_record("test1")
        from logging import LogRecord
        self.assertIsInstance(rec, LogRecord)
        self.assertEqual(rec.getMessage(), "test1")

    def test_subs_formatters(self):
        """
        Test substitution of substring in format
        """
        with MockVar(sys, "stdout", StringIO()) as p:
            log.fmt_stdout = "ABCD %(message)s"
            log.stdout("DEBUG")
            # Get formats, don't do anything:
            fmt_old = log._VepLog__subs_formatters("ABCD", "1234")
            log.debug("logging...")
        res = p.getvalue()
        # print res
        self.assertIn("1234 logging...", res)
        self.assertNotIn("ABCD", res)

    def test_set_formatters(self, new_fmt=None):
        """
        Test formatter setting
        """
        with MockVar(sys, "stdout", StringIO()) as p:
            log.fmt_stdout = "%(levelname)8s: %(message)s"
            log.stdout("DEBUG")
            log.debug("test1")
            # Should do nothing
            log._VepLog__set_formatters(None)
            log.debug("test2")
            log._VepLog__set_formatters("%(message)s")
            log.debug("test3")
            log._VepLog__set_formatters("%(levelname)8s: %(message)s")
            log.debug("test4")
            log._VepLog__set_formatters(["%(message)s"] * len(log.log.parent.handlers))
            log.debug("test5")
        res = p.getvalue()
        # print res
        self.assertEqual(res, "   DEBUG: test1\n   DEBUG: test2\ntest3\n   DEBUG: test4\ntest5\n")

    def test_get_default_loglevel(self):
        # default
        self.assertEqual(log._get_default_loglevel(None), "DEBUG")

        # specified
        self.assertEqual(log._get_default_loglevel('INFO'), "INFO")

        # OPT.verbose
        with MockVar(OPT, 'verbosity_level', 'CRITICAL'):
            self.assertEqual(log._get_default_loglevel(None), "CRITICAL")
            self.assertEqual(log._get_default_loglevel('INFO'), "CRITICAL")

    def test_dec_log_wrap_more(self):
        """
        Testing log_wrap_more decorator [main logic, rest of dec's wrap it]
        """
        # Providing method name
        log.__init__()  # reset formatters
        log.stdout("DEBUG")

        @log.log_wrap_more(log_method="debug")
        def my_func(param1, param2="abc"):
            print("This is my_func")
            return param1 + param2

        expected = "DEBUG   : method my_func, args: ('a',),{} - Starting...\nThis is my_func\nDEBUG   : method my_func, return_value=aabc - Done!"
        with CaptureStdoutLog() as p:
            res = my_func("a")
        log.debug("my_func wrapping provided:\n{}".format(p.getvalue()))
        self.assertEqual(res, "aabc")
        self.assertIn(expected, p.getvalue())

        # Providing method name, none verbose
        @log.log_wrap_more(log_method="info", verbose=False)
        def my_func2(param1, param2="abc"):
            print("This is my_func2")
            return param1 + param2

        expected = "method my_func2 - Starting...\nThis is my_func2\nmethod my_func2 - Done!"
        with CaptureStdoutLog() as p:
            res = my_func2("a", "bcd")
        log.debug("my_func2 wrapping provided:\n{}".format(p.getvalue()))
        self.assertEqual(res, "abcd")
        self.assertIn(expected, p.getvalue())

        # Providing method obj
        @log.log_wrap_more(log_method=log.warning)
        def my_func3(param1, param2="abc"):
            print("This is my_func3")
            return param1 + param2

        expected = "WARNING : method my_func3, args: ('a',),{'param2': 'b'} - Starting...\nThis is my_func3\nWARNING : method my_func3, return_value=ab - Done!"
        with CaptureStdoutLog() as p:
            res = my_func3("a", param2="b")
        log.debug("my_func3 wrapping provided:\n{}".format(p.getvalue()))
        self.assertEqual(res, "ab")
        self.assertIn(expected, p.getvalue())

        # Providing bad method obj
        @log.log_wrap_more(log_method=log.__init__)
        def my_func4(param1, param2="abc"):
            print("This is my_func4")
            return param1 + param2

        expected = "DEBUG   : method my_func4, args: (),{'param2': 'a', 'param1': 'b'} - Starting...\nThis is my_func4\nDEBUG   : method my_func4, return_value=ba - Done!\n"
        with CaptureStdoutLog() as p:
            res = my_func4(param2="a", param1="b")
        log.debug("my_func4 wrapping provided:\n{}".format(p.getvalue()))
        self.assertEqual(res, "ba")
        self.assertIn(expected, p.getvalue())

        # benchmarking and verbose
        @log.log_wrap_more(timer=True, verbose=True)
        def my_func5(param1, param2="abc"):
            time.sleep(0.5)
            print("This is my_func5")
            return param1 + param2

        expected_re = r"DEBUG   : method my_func5, args: \(\),{'param2': 'a', 'param1': 'b'} - Starting\.\.\.\nThis is my_func5\nDEBUG   : method my_func5, return_value=ba, Elapsed in ([\.\d]+) secs - Done!"
        with CaptureStdoutLog() as p:
            res = my_func5(param2="a", param1="b")
        log.debug("my_func5 wrapping provided:\n{}".format(p.getvalue()))
        self.assertEqual(res, "ba")
        self.assertRegex(p.getvalue(), expected_re)

    def test_dec_wrappers(self):
        """
        Testing log_wrap_more wrappers:
        log_wrap()
        debug_wrap()
        debug_wrap_more()

        benchmark_wrap()
        debug_benchmark_wrap()
        benchmark_wrap_more()

        """
        def my_func(param1, param2="abc"):
            print("This is my_func")
            return param1 + param2

        # NOTE: my_func not wrapped, my_func\d are wrapped!

        # log_wrap <-> log_wrap_more
        @log.log_wrap_more(log_method="debug", verbose=False)
        def my_func1(*args, **kwargs):
            return my_func(*args, **kwargs)

        @log.log_wrap(log_method="debug")
        def my_func2(*args, **kwargs):
            return my_func(*args, **kwargs)

        with CaptureStdoutLog() as p1:
            res1 = my_func1("foo", 'bar')
        with CaptureStdoutLog() as p2:
            res2 = my_func2("foo", "bar")
        self.assertEqual(res1, res2)
        self.assertEqual(p1.getvalue().replace("my_func1", "my_funcW"), p2.getvalue().replace("my_func2", "my_funcW"))

        # debug_wrap <-> log_more
        @log.debug_wrap()
        def my_func3(*args, **kwargs):
            return my_func(*args, **kwargs)

        with CaptureStdoutLog() as p3:
            res3 = my_func3("foo", "bar")
        self.assertEqual(res2, res3)
        self.assertEqual(p2.getvalue().replace("my_func2", "my_funcW"), p3.getvalue().replace("my_func3", "my_funcW"))

        # debug_wrap_more <-> log_wrap_more
        @log.log_wrap_more(log_method="debug")
        def my_func4(*args, **kwargs):
            return my_func(*args, **kwargs)

        @log.debug_wrap_more()
        def my_func5(*args, **kwargs):
            return my_func(*args, **kwargs)

        with CaptureStdoutLog() as p4:
            res4 = my_func4("foo", "bar")
        with CaptureStdoutLog() as p5:
            res5 = my_func5("foo", "bar")
        self.assertEqual(res4, res5)
        self.assertEqual(p4.getvalue().replace("my_func4", "my_funcW"), p5.getvalue().replace("my_func5", "my_funcW"))

        # benchmark_wrap <-> log_wrap_more [log method given in 2 different ways]
        @log.log_wrap_more(log_method="info", verbose=False, timer=True)
        def my_func6(*args, **kwargs):
            return my_func(*args, **kwargs)

        @log.benchmark_wrap(log_method=log.info)
        def my_func7(*args, **kwargs):
            return my_func(*args, **kwargs)

        with CaptureStdoutLog() as p6:
            res6 = my_func6("foo", "bar")
        with CaptureStdoutLog() as p7:
            res7 = my_func7("foo", "bar")
        self.assertEqual(res6, res7)
        self.assertEqual(p6.getvalue().replace("my_func6", "my_funcW"), p7.getvalue().replace("my_func7", "my_funcW"))

        # debug_benchmark_wrap <-> log_wrap_more
        @log.log_wrap_more(log_method="debug", timer=True, verbose=False)
        def my_func8(*args, **kwargs):
            return my_func(*args, **kwargs)

        @log.debug_benchmark_wrap()
        def my_func9(*args, **kwargs):
            return my_func(*args, **kwargs)

        with CaptureStdoutLog() as p8:
            res8 = my_func8("foo", "bar")
        with CaptureStdoutLog() as p9:
            res9 = my_func9("foo", "bar")
        # log.debug(p8.getvalue())
        # log.debug(p9.getvalue())
        self.assertEqual(res8, res9)
        self.assertEqual(p8.getvalue().replace("my_func8", "my_funcW"), p9.getvalue().replace("my_func9", "my_funcW"))

        # benchmark_wrap_more <-> log_wrap_more
        @log.log_wrap_more(log_method="warning", timer=True, verbose=True)
        def my_func10(*args, **kwargs):
            return my_func(*args, **kwargs)

        @log.benchmark_wrap_more(log_method="warning")
        def my_func11(*args, **kwargs):
            return my_func(*args, **kwargs)

        with CaptureStdoutLog() as p10:
            res10 = my_func10("foo", "bar")
        with CaptureStdoutLog() as p11:
            res11 = my_func11("foo", "bar")
        self.assertEqual(res10, res11)
        self.assertEqual(p10.getvalue().replace("my_func10", "my_funcW"), p11.getvalue().replace("my_func11", "my_funcW"))

    def test_loglevels(self):
        # Confirm that the loglevel values are correct
        for level in LOGLEVELS:
            self.assertEqual(LOGLEVELS[level], vars(logging)[level])

    def test_lognocommit(self):
        with CaptureStdoutLog() as p:
            log.nocommit("hello")
        self.assertIn('hello', p.getvalue())


class Logline_tests(TestCase):

    def test_logline(self):
        with TempName() as t:
            tmp = t.name()
            open(tmp, "w").close()
            pylog.logline(tmp, "Hello1")
            pylog.logline(tmp, "Hello2")
            pylog.logline(tmp, "Hello3")
            res = open(tmp).read()

            # print res
            self.assertEqual(len(res.split('\n')), 4)
            self.assertIn('Hello1', res)
            self.assertIn('Hello3', res)

            # log file does not exist
            self.assertRaises(Exception, pylog.logline, "/tmp/surefilenotexist_12_8", "sometext")

        # text output
        self.assertRegex(pylog.logline(None, "sometext1"), "sometext1")


if __name__ == '__main__':
    os.environ['PYTHONPATH'] = '%s%s%s' % (os.environ.get('PYTHONPATH', ''), os.pathsep, ROOT_ENV)
    unittest.main()
