#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Unittest for shell.py
"""
from setenv_unittest import ROOT_ENV, UT_DIR     # must be first import for unittests
from gadget.shell import *
from io import StringIO
from gadget.gizmo import Elapsed, MockVar, with_
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.disk import mkdirs, Chdir, Allfiles
from gadget.files import TempDir, File
from gadget.strmore import str_isword
from gadget.helperclass import CaptureStdoutLog
import gadget.shell as shell
from gadget.tvpv import TvpvEnv
from os.path import exists
import os.path as op
from unittest.mock import Mock, patch, MagicMock
from pprint import pformat


class SystemCall_tests(TestCase):

    def test_timeout(self):
        # timeout case
        e, sout, serr = SystemCall('sleep 10').run_sout_serr(1)
        self.assertEqual(e, 1)
        self.assertEqual(sout, '')
        self.assertEqual(serr, 'TIMEOUT at 1 secs')

        # no timeout case
        e, sout, serr = SystemCall('ls sure_not_found_aqwe').run_sout_serr(2)
        self.assertEqual(e, 2)
        self.assertEqual(sout, '')
        self.assertIn('cannot access', serr)

    def test_sout_serr(self):
        code = r"""#!{exe} -u
import sys
for ii in range(3):
    sys.stdout.write("stdout %s\n" % ii)
    sys.stderr.write("stderr %s\n" % ii)

""".format(exe=sys.executable)

        with TempName(name=True) as tname:
            File(tname).touch(code).chmod("0775")

            # interleaved()
            call = SystemCall(tname, exe=True)
            ecode, result = call.run_outtxt()
            self.assertEqual(call.return_ecode(), 0)
            self.assertEqual(ecode, 0)
            expect = ['stdout 0',
                      'stderr 0',
                      'stdout 1',
                      'stderr 1',
                      'stdout 2',
                      'stderr 2']
            self.assertEqual(result.split('\n'), expect)
            result = call.run_outonly()
            self.assertEqual(result.split('\n'), expect)
            ecode, result = call.run_outtxt(False)
            expect2 = '''stdout 0
stdout 1
stdout 2
stderr 0
stderr 1
stderr 2'''
            self.assertTextEqual(result, expect2)
            _, result = SystemCall('echo abc').run_outtxt(False)
            self.assertEqual(result, 'abc')

            # interleaved_outfile()
            with TempName(name=True) as tname2:
                call = SystemCall(tname, exe=True)
                ecode = call.run_outfile(tname2)
                self.assertEqual(ecode, 0)
                self.assertEqual(call.return_ecode(), 0)
                result = File(tname2).read()
                self.assertEqual(result.split('\n'), expect + [''])

            # sout_serr()
            call = SystemCall(tname, exe=True)
            ecode, sout, serr = call.run_sout_serr()
            self.assertEqual(ecode, 0)
            self.assertEqual(call.return_ecode(), 0)
            self.assertEqual(sout.split('\n'), ['stdout 0', 'stdout 1', 'stdout 2'])
            self.assertEqual(serr.split('\n'), ['stderr 0', 'stderr 1', 'stderr 2'])

            # run_stream() - basic and passing case
            call = SystemCall(tname, exe=True)
            res = list(call.run_stream())
            self.assertEqual(res, expect)
            self.assertEqual(call.return_ecode(), 0)
            self.assertEqual(call.return_ecode(), 0)   # yes, run 2nd time

    @unittest.skipIf(IS_WIN, 'unix only due to plain command call')
    def test_nonexe(self):
        # run_stream() - basic and passing case
        call = SystemCall(f'ls -ltr {ROOT_ENV}')
        _, res = call.run_outtxt()
        self.assertIn('README.md', res)

    def test_basic(self):
        codepass = r"""#!{exe} -u
import sys
print("txtout")
sys.stderr.write("txterr\n")
open(sys.argv[1], "w").write("Success %s" % sys.argv[2])
""".format(exe=sys.executable)

        codefail = r"""#!{exe} -u
import sys
print("txtout")
sys.stderr.write("txterr\n")
raise Exception('Errored')
""".format(exe=sys.executable)

        with TempDir(name=True) as tdir:
            filepass = File(join(tdir, "pass")).touch(codepass).chmod("0775").get_name()
            filefail = File(join(tdir, "fail")).touch(codefail).chmod("0775").get_name()

            # pass case - string
            call = SystemCall('%s %s "4 5" 46' % (filepass, join(tdir, 'out')), exe=True)
            ecode = call.run()
            self.assertEqual(ecode, 0)
            self.assertEqual(call.return_ecode(), 0)
            self.assertEqual(File(join(tdir, 'out')).read(), 'Success 4 5')

            # fail case
            call = SystemCall(filefail, exe=True)
            ecode = call.run()
            self.assertEqual(ecode, 1)
            self.assertEqual(call.return_ecode(), 1)

            # pass case - list
            ecode = SystemCall([filepass, join(tdir, 'out'), '45 46'], exe=True).run()
            self.assertEqual(ecode, 0)
            self.assertEqual(File(join(tdir, 'out')).read(), 'Success 45 46')

            # shlex should not be called
            SystemCall([filepass, join(tdir, 'out'), '4 "5 4" 6'], exe=True).run()
            self.assertEqual(File(join(tdir, 'out')).read(), 'Success 4 "5 4" 6')

            # exitout = message
            with self.assertRaisesRegex(Exception, "oops"):
                SystemCall(filefail, exe=True).run(exitout='oops')
            with self.assertRaisesRegex(Exception, "It should be exitout"):
                SystemCall(filefail, exe=True).run(exitout=True)

            # incorrect usage
            call = SystemCall(filefail, exe=True)
            with self.assertRaisesRegex(Exception, "but actual system call execute was not called"):
                call.return_ecode()

            with self.assertRaisesRegex(OSError, "notfound_abc"):
                SystemCall("/notfound_abc").run()

            # run_stream() - error code check
            call = SystemCall(filefail, exe=True)
            res = list(call.run_stream())
            self.assertIn('txtout', res)
            self.assertIn('txterr', res)
            self.assertIn('Exception: Errored', res)
            self.assertEqual(call.return_ecode(), 1)
            self.assertEqual(call.return_ecode(), 1)   # yes, run second time

    def test_is_popen_false(self):

        # with both stdout and stderr
        code = r"""#!{exe} -u
import sys
print("txtout")
sys.stderr.write("txterr\n")
exit(1)
""".format(exe=sys.executable)
        with TempDir(name=True) as tdir:
            filecmd = File(join(tdir, "fail1")).touch(code).chmod("0775").get_name()

            with open(f'{tdir}/outf', 'w') as fh:
                sc = SystemCall(filecmd, exe=True)
                ecode = sc._subprocess_call(sc.cmd, fh, fh, is_popen=False)
                self.assertEqual(ecode, 1)
            expect = '''txtout
txterr
'''
            self.assertTextEqual(File(f'{tdir}/outf').read(), expect)

    def test_disp(self):

        # with both stdout and stderr - run_outtxt
        code = r"""#!{exe} -u
import sys
print("txtout")
sys.stderr.write("txterr\n")
exit(1)
""".format(exe=sys.executable)
        with TempDir(name=True) as tdir:
            filecmd = File(join(tdir, "fail1")).touch(code).chmod("0775").get_name()

            with CaptureStdoutLog() as p:
                call = SystemCall(filecmd, exe=True, disp=True)
                call.run_outtxt()
            self.assertEqual(call.return_ecode(), 1)
            expect = '''CMD: %s
===== Stdout+Stderr:
txtout
txterr
===end of stdout+stderr===
''' % filecmd
            self.assertTextEqual(p.getvalue(), expect)

        # with both stdout and stderr - run_sout_serr()
        code = r"""#!{exe} -u
import sys
print("txtout")
sys.stderr.write("txterr\n")
exit(1)
""".format(exe=sys.executable)
        with TempDir(name=True) as tdir:
            filecmd = File(join(tdir, "fail1")).touch(code).chmod("0775").get_name()

            with CaptureStdoutLog() as p:
                call = SystemCall(filecmd, exe=True, disp=True)
                call.run_sout_serr()
            self.assertEqual(call.return_ecode(), 1)
            expect = '''CMD: %s
===== Stdout:
txtout
===== Stderr:
txterr
===end of stdout or stderr===
''' % filecmd
            self.assertTextEqual(p.getvalue(), expect)

        # no stdout and stderr - run_sout_serr
        code = r"""#!{exe} -u
import sys
exit(1)
""".format(exe=sys.executable)
        with TempDir(name=True) as tdir:
            filecmd = File(join(tdir, "fail1")).touch(code).chmod("0775").get_name()

            with CaptureStdoutLog() as p:
                call = SystemCall(filecmd, exe=True, disp=True)
                call.run_sout_serr()
            self.assertEqual(call.return_ecode(), 1)
            expect = '''CMD: %s
===== Stdout:
===end of stdout or stderr===
''' % filecmd
            self.assertTextEqual(p.getvalue(), expect)

        # no stdout and stderr - run_outtxt
        code = r"""#!{exe} -u
import sys
exit(1)
""".format(exe=sys.executable)
        with TempDir(name=True) as tdir:
            filecmd = File(join(tdir, "fail1")).touch(code).chmod("0775").get_name()

            with CaptureStdoutLog() as p:
                call = SystemCall(filecmd, exe=True, disp=True)
                call.run_outtxt()
            self.assertEqual(call.return_ecode(), 1)
            expect = '''CMD: %s
===== Stdout+Stderr:
===end of stdout+stderr===
''' % filecmd
            self.assertTextEqual(p.getvalue(), expect)

    def test_run_disp(self):

        # with both stdout and stderr
        code = r"""#!{exe} -u
import sys
print("txtout")
sys.stderr.write("txterr\n")
exit(1)
""".format(exe=sys.executable)
        with TempDir(name=True) as tdir:
            filecmd = File(join(tdir, "fail1")).touch(code).chmod("0775").get_name()

            with CaptureStdoutLog() as p:
                call = SystemCall(filecmd, exe=True)
                call.run(disp=True)
            self.assertEqual(call.return_ecode(), 1)
            self.assertIn('txtout', p.getvalue())
            self.assertIn('txterr', p.getvalue())

        # no stdout and stderr
        code = r"""#!{exe} -u
import sys
exit(1)
""".format(exe=sys.executable)
        with TempDir(name=True) as tdir:
            filecmd = File(join(tdir, "fail1")).touch(code).chmod("0775").get_name()
            with CaptureStdoutLog() as p:
                call = SystemCall([filecmd, '1 2'], exe=True)
                call.run(disp=True)
            self.assertEqual(call.return_ecode(), 1)
            self.assertIn("fail1 '1 2'", p.getvalue())   # check on the command
            self.assertIn('===end of', p.getvalue())

        # pass case
        code = r"""#!{exe} -u
import sys
print("txtout")
sys.stderr.write("txterr\n")
""".format(exe=sys.executable)
        with TempDir(name=True) as tdir:
            filecmd = File(join(tdir, "fail1")).touch(code).chmod("0775").get_name()
            with CaptureStdoutLog() as p:
                call = SystemCall(filecmd, exe=True, disp=True)
                call.run(disp=True)
            self.assertEqual(call.return_ecode(), 0)
            self.assertEqual(len(p.getvalue().split('\n')), 7)

    @unittest.skipIf(IS_WIN, 'unix only due to sha of newlines changing')
    def test_universal_newlines(self):
        # These tests make sures universal_newlines have no effect on different types of files
        with TempDir(name=True) as tdir:
            outfile = join(tdir, "file1")

            # normal unix file - text
            testfile = '/p/pde/tvpv/pylib3a/test_files/unix.txt'
            SystemCall('cat %s' % testfile).run_outfile(outfile)
            self.assertEqual(File(outfile).sha1(binary=True), '3b31471cc1bfaf2dd2f3cc7ef7a45ddec6c7e3fa')

            # unicode file
            testfile = '/p/pde/tvpv/pylib3a/test_files/unicode.html'
            SystemCall('cat %s' % testfile).run_outfile(outfile)
            self.assertEqual(File(outfile).sha1(binary=True), '8c55864a172b77c9f5c38f5cf505faa0b19db2a7')

            # windows file
            testfile = '/p/pde/tvpv/pylib3a/test_files/dos.txt'
            SystemCall('cat %s' % testfile).run_outfile(outfile)
            self.assertEqual(File(outfile).sha1(binary=True), '84c5a4fc8e4586a2c77217bda6215e5e4b2bf78a')

            # binary file
            testfile = '/p/pde/tvpv/pylib3a/test_files/binary.so'
            SystemCall('cat %s' % testfile).run_outfile(outfile)
            self.assertEqual(File(outfile).sha1(binary=True), '6d2af4489e705287a3a15d18513be921bafa2a64')

    def test_exe(self):
        with TempDir(name=True) as tdir:
            ff = File(f'{tdir}/aa').touch('print("hello py")')
            _, res = SystemCall(ff.get_name(), exe=True).run_outtxt()
            self.assertEqual(res, 'hello py')


class BgCmd_tests(TestCase):

    def test_basic(self, optional=False):
        bg = BgCmd(ncpu=2)
        code = "import sys; import time; print(sys.argv[1]);"
        with TempName(exe=code, name=True) as tmp:
            bg.send("%s cmd111" % tmp)
            bg.send(tmp, "cmd222")
            bg.send(tmp, ["cmd333"], name="333")

            self.assertEqual(bg.get("r1").name, "r1")
            self.assertEqual(bg.get("r2").cmd, [tmp, "cmd222"])
            self.assertEqual(bg.get("333").seqid, 3)
            self.assertRaises(Exception, bg.get, "444")   # not existing job
            self.assertEqual(set([j.name for j in bg.queue(wait=True)]), {"r1", "r2", "333"})
            self.assertEqual(set([j.name for j in bg.queue(wip=True)]), set())
            self.assertEqual(set([j.name for j in bg.queue(done=True)]), set())

            bg.run()

            if optional:
                # These are flaky test, so run only during optional
                print("Executing optional tests")
                self.assertEqual(len(bg.runninglist), 2)   # there are only 2 cpu's
                self.assertTrue(bg.is_running("%s cmd111" % tmp))
                self.assertTrue(bg.is_running("%s cmd222" % tmp))

            self.assertTrue(bg.is_job_exist("333"))

            # let bg.run() finish
            for _ in range(300):   # max of 30 loops
                if bg.run():
                    time.sleep(0.1)
                else:
                    break
            else:
                self.fail("bg.run() failed to complete")

            # let bg.count() finish
            for _ in range(300):   # max of 300 loops (30 secs)
                if bg.count() > 0:
                    time.sleep(0.1)
                else:
                    break
            else:
                self.fail("bg.count() failed to complete")

            self.assertEqual(set([j.name for j in bg.queue(done=True)]), {"r1", "r2", "333"})
            self.assertEqual(set([j.name for j in bg.queue(wait=True)]), set())
            self.assertEqual(list(bg.launchlist), ["r1", "r2", "333"])
            self.assertEqual(len(bg.runninglist), 0)
            self.assertFalse(bg.is_running("%s cmd111" % tmp))

            # Check the outputs
            self.assertEqual(File(bg.get("r1").sout).read(), "cmd111\n")
            self.assertEqual(File(bg.get("r2").sout).read(), "cmd222\n")
            self.assertEqual(File(bg.get("333").sout).read(), "cmd333\n")
            self.assertEqual(bg.get("333").ecode, 0)

            # Check purge
            job = bg.get("333")
            self.assertTrue(exists(job.sout))
            self.assertTrue(exists(job.serr))
            bg.purge("333")
            self.assertFalse(exists(job.sout))
            self.assertFalse(exists(job.serr))
            self.assertFalse(bg.is_job_exist("333"))
            self.assertEqual(set([j.name for j in bg.queue(done=True)]), {"r1", "r2"})
            self.assertRaises(Exception, bg.purge, "333")   # not existing job
            bg.jobs['r2'].status = bg.STATUS.WIP
            self.assertRaises(Exception, bg.purge, "r2")   # cannot purge wip job

            # name check
            self.assertRaises(Exception, bg.send, tmp, "cmd222", name='r1')   # duplicate name
            self.assertRaises(Exception, bg.send, tmp, "cmd222", name='r 1')  # invalid name

        bg.close()

    @unittest.skipIf(*is_ut_option('SKIP_NIGHTLY_BUILD', message="Flaky test during continuous integration", neg=False))
    @unittest.skipIf(*is_ut_option('SLOW', message="slowtest"))
    @with_(MockVar, os, 'getloadavg', Mock(return_value=[0.0, 0.0, 0.0]))
    @with_(MockVar, multiprocessing, 'cpu_count', Mock(return_value=4))
    def test_basic_full(self):
        self.test_basic(optional=True)

    def test_sout_serr(self):
        bg = BgCmd(ncpu=2)
        code1 = "import sys; import time; print(sys.argv[1]);"
        code2 = "import sys; import time; print(sys.argv[1]);raise Exception;"
        with TempName(exe=code1, name=True) as tmp1, \
                TempName(exe=code2, name=True) as tmp2:
            bg.send(tmp1, "cmd111")
            bg.send(tmp2, "cmd222")

            self.assertEqual(bg.get("r1").ecode, -1)
            bg.run()

            # let bg.run() finish
            for _ in range(300):   # max of 30 loops
                if bg.run():
                    time.sleep(0.1)
                else:
                    break
            else:
                self.fail("bg.run() failed to complete")

            # let bg.count() finish
            for _ in range(300):   # max of 300 loops (30 secs)
                if bg.count() > 0:
                    time.sleep(0.1)
                else:
                    break
            else:
                self.fail("bg.count() failed to complete")

            # Check the outputs

            self.assertEqual(File(bg.get("r1").sout).read(), "cmd111\n")
            self.assertEqual(File(bg.get("r1").serr).read(), "")
            self.assertEqual(bg.get("r1").ecode, 0)

            self.assertEqual(File(bg.get("r2").sout).read(), "cmd222\n")
            self.assertIn('Traceback', File(bg.get("r2").serr).read())
            self.assertEqual(bg.get("r2").ecode, 1)

        bg.close()

    def test_count(self):
        """
        Test the count function
        """
        class PollTrue:
            returncode = 0

            def poll(self):
                return True

            def terminate(self):
                pass

        class PollNone:
            returncode = 1

            def poll(self):
                return None

            def terminate(self):
                pass

        bg = BgCmd(ncpu=100)
        bg.send("cmd111")
        bg.send("cmd222")
        bg.send("cmd333")
        bg.send("cmd444")
        bg.send("cmd555")
        bg.jobs['r1'].pr = PollTrue()
        bg.jobs['r2'].pr = PollTrue()
        bg.jobs['r3'].pr = PollTrue()
        bg.jobs['r4'].pr = PollNone()   # means wip
        bg.jobs['r5'].pr = PollNone()   # means wip
        self.assertEqual(bg.count(), 0)

        for job in "r1 r2 r3 r4 r5".split():
            bg.jobs[job].status = bg.STATUS.WIP
        self.assertEqual(bg.count(), 2)

        for job in "r1 r2 r3 r4 r5".split():
            bg.jobs[job].status = bg.STATUS.WIP
        bg.jobs['r3'].pr = PollNone()  # means wip
        bg.jobs['r3'].elapsed = time.time()
        self.assertEqual(bg.count(), 3)

    @unittest.skipIf(*is_ut_option('SLOW', message="Slowtest"))
    @with_(MockVar, os, 'getloadavg', Mock(return_value=[0.0, 0.0, 0.0]))
    @with_(MockVar, multiprocessing, 'cpu_count', Mock(return_value=4))
    def test_comprehensive(self):
        bg = BgCmd(ncpu=2)
        code = "import sys; import time; time.sleep(2); print(sys.argv[1]);"
        with TempName(exe=code, name=True) as tmp:
            bg.send(tmp, "cmd111", seqid=10)
            bg.send(tmp, "cmd222")
            bg.send(tmp, "cmd333")
            bg.send(tmp, "cmd444")
            bg.send(tmp, "cmd555")

            bg.run()
            self.assertEqual(len([j.name for j in bg.queue(wip=True)]), 2)   # There must be two wip

            # let bg.run() finish
            for i in range(200):   # max of 20 seconds
                if bg.run():
                    time.sleep(0.1)
                else:
                    break
            else:
                self.fail("bg.run() failed to complete")

            # let bg.count() finish
            for i in range(100):   # max of 10 loops
                if bg.count() > 0:
                    time.sleep(0.1)
                else:
                    break
            else:
                self.fail("bg.count() failed to complete")

            # Check the outputs
            self.assertEqual(File(bg.get("r1").sout).read(), "cmd111\n")
            self.assertEqual(File(bg.get("r2").sout).read(), "cmd222\n")
            self.assertEqual(File(bg.get("r3").sout).read(), "cmd333\n")
            self.assertEqual(File(bg.get("r4").sout).read(), "cmd444\n")
            self.assertEqual(File(bg.get("r5").sout).read(), "cmd555\n")

            self.assertEqual(list(bg.launchlist), ["r2", "r3", "r4", "r5", "r1"])

    @with_(MockVar, os, 'getloadavg', Mock(return_value=[0.0, 0.0, 0.0]))
    @with_(MockVar, multiprocessing, 'cpu_count', Mock(return_value=4))
    @unittest.skipIf(*is_ut_option('SKIP_NIGHTLY_BUILD', message="flaky test. see failrepo.", neg=False))
    @unittest.skipIf(*is_ut_option('SLOW', message="slowtest"))
    def test_timeout(self):
        bg = BgCmd(ncpu=4, timeout=1)
        code = "from __future__ import print_function; import sys; import time; time.sleep(100); print(sys.argv[1]);"
        with TempName(exe=code, name=True) as tmp:
            bg.send(tmp, "cmd111")
            bg.send(tmp, "cmd222", timeout=1.5)
            bg.send(tmp, "cmd333", timeout=2)

            bg.run()
            self.assertEqual(len([j.name for j in bg.queue(wip=True)]), 3)   # There must be three

            # check all pid is present
            procs = set()
            for j in bg.queue(wip=True):
                procs.add(j.pr)
            for pr in procs:
                self.assertIsNone(pr.poll())

            # let bg.count() finish
            for i in range(50):   # max of 5 secs
                if bg.count() > 0:
                    time.sleep(0.1)
                else:
                    break
            else:
                self.fail("timeout did not happen (waited for 5 seconds, timeout at 1 sec)")

            # at this time the process should be killed!
            self.assertEqual(len([j.name for j in bg.queue(wip=True)]), 0)
            for i in range(200):   # max of 20 seconds for process to be killed
                isdone = True
                for pr in procs:
                    if pr.poll() is None:
                        isdone = False
                if isdone:
                    break

                time.sleep(0.1)
            else:
                self.fail("process was not killed after 20 seconds of wait")

            # Check the outputs
            self.assertEqual(File(bg.get("r1").sout).read(), "")
            self.assertEqual(File(bg.get("r2").sout).read(), "")
            self.assertEqual(File(bg.get("r3").sout).read(), "")
            self.assertIn('TIMEOUT', File(bg.get("r3").serr).read())
            self.assertAlmostEqual(bg.get("r1").elapsed, 1, delta=0.2)
            self.assertAlmostEqual(bg.get("r2").elapsed, 1.5, delta=0.2)
            self.assertAlmostEqual(bg.get("r3").elapsed, 2, delta=0.2)

            self.assertEqual(list(bg.launchlist), ["r1", "r2", "r3"])

    def test_load(self):
        m_pass = Mock()
        ins = m_pass.return_value
        ins.poll.return_value = None    # it is running
        with MockVar(subprocess, "Popen", m_pass):

            # normal case - low load
            with MockVar(os, 'getloadavg', Mock(return_value=[1.0, 0, 0])):
                bg = BgCmd(ncpu=2)
                bg._cpu_count = 10
                bg.send("/notexist", "cmd111")
                bg.send("/notexist", "cmd112")
                self.assertFalse(bg.run())
                self.assertEqual(bg.count(), 2)

                bg.send("/notexist", "cmd113")
                self.assertTrue(bg.run())
                self.assertEqual(bg.count(), 2)

            # overload case
            bg = BgCmd(ncpu=3)
            bg._cpu_count = 10
            bg.send("/notexist", "cmd111")
            bg.send("/notexist", "cmd112")
            with MockVar(os, 'getloadavg', Mock(return_value=[11.0, 0, 0])):
                self.assertTrue(bg.run())
                self.assertEqual(bg.count(), 1)  # one is run

                self.assertTrue(bg.run())
                self.assertEqual(bg.count(), 1)  # no additional run

            with MockVar(os, 'getloadavg', Mock(return_value=[7.0, 0, 0])):
                self.assertFalse(bg.run())
                self.assertEqual(bg.count(), 2)

            # partial load case
            bg = BgCmd(ncpu=3)
            bg._cpu_count = 10
            bg.send("/notexist", "cmd111")
            bg.send("/notexist", "cmd112")
            bg.send("/notexist", "cmd113")
            bg.send("/notexist", "cmd114")
            with MockVar(os, 'getloadavg', Mock(return_value=[8.0, 0, 0])):
                self.assertTrue(bg.run())
                self.assertEqual(bg.count(), 1)   # one is run

                self.assertTrue(bg.run())
                self.assertEqual(bg.count(), 2)   # additional one run

            with MockVar(os, 'getloadavg', Mock(return_value=[11.0, 0, 0])):
                self.assertTrue(bg.run())
                self.assertEqual(bg.count(), 2)   # no additional runs

            with MockVar(os, 'getloadavg', Mock(return_value=[9.1, 0, 0])):
                self.assertTrue(bg.run())
                self.assertEqual(bg.count(), 2)   # no additional runs

            with MockVar(os, 'getloadavg', Mock(return_value=[8.9, 0, 0])):
                self.assertTrue(bg.run())
                self.assertEqual(bg.count(), 3)   # one additional
                self.assertTrue(bg.run())
                self.assertEqual(bg.count(), 3)   # no additional bec of max cpu

    @unittest.skipIf(*is_ut_option('OPTIONAL', message="robustness test only"))
    def test_robust(self):
        for i in range(200):     # 200-loop check
            print("testing loop#%s. Test will stop if there is failure." % i, end=' ')
            bg = BgCmd(ncpu=2)
            code = "import sys; import time; print(sys.argv[1]);"
            with TempName(exe=code, name=True) as tmp:
                bg.send(tmp, "cmd111")
                bg.send(tmp, "cmd222")
                bg.send(tmp, "cmd333")
                bg.send(tmp, "cmd444")
                bg.send(tmp, "cmd555")

                bg.run()
                # self.assertEqual(set([j.name for j in bg.queue(wip=True)]), {"r1","r2"})
                if set([j.name for j in bg.queue(wip=True)]) != {"r1", "r2"}:
                    print("<<<<<<<", [j.name for j in bg.queue(wip=True)])
                    for job in bg.queue(done=True):
                        print("Output: %r %r" % (job.name, File(job.sout).read()))
                else:
                    print()

                # let bg.run() finish
                for i in range(30):   # max of 30 loops
                    if bg.run():
                        time.sleep(0.1)
                    else:
                        break
                else:
                    self.fail("bg.run() failed to complete")

                # let bg.count() finish
                for i in range(30):   # max of 30 loops
                    if bg.count() > 0:
                        time.sleep(0.1)
                    else:
                        break
                else:
                    self.fail("bg.count() failed to complete")

                self.assertEqual(list(bg.launchlist), ["r1", "r2", "r3", "r4", "r5"])

                # Check the outputs
                self.assertEqual(File(bg.get("r1").sout).read(), "cmd111\n")
                self.assertEqual(File(bg.get("r2").sout).read(), "cmd222\n")
                self.assertEqual(File(bg.get("r3").sout).read(), "cmd333\n")
                self.assertEqual(File(bg.get("r4").sout).read(), "cmd444\n")
                self.assertEqual(File(bg.get("r5").sout).read(), "cmd555\n")

            bg.close()


class MaxVMsize_tests(TestCase):
    def test_basic(self):
        aa = MaxVMsize()
        self.assertRaises(Exception, aa.get_maxvmsize)    # context manager not used
        with MaxVMsize(sleepn=0.1) as aa:
            time.sleep(0.5)
            self.assertGreater(aa.get_maxvmsize(), 5000)
            tn = aa.tname
        self.assertFalse(os.path.exists(tn), "Temp file must not exist since object is closed")


class FromSysArgv_tests(TestCase):
    def test_single(self):
        with MockVar(sys, "argv", []):
            self.assertEqual(FromSysArgv.single("-serev"), '')
        with MockVar(sys, "argv", "arg.py -serev 24 -vrev vrevA".split()):
            self.assertEqual(FromSysArgv.single("-serev"), '24')
        with MockVar(sys, "argv", "arg.py -serev".split()):
            self.assertEqual(FromSysArgv.single("-serev"), '')
        with MockVar(sys, "argv", "arg.py -vrev vrevA".split()):
            self.assertEqual(FromSysArgv.single("-serev"), '')

    def test_multi(self):
        with MockVar(sys, "argv", []):
            self.assertEqual(FromSysArgv.multi("-serev"), [])
        with MockVar(sys, "argv", "arg.py -serev 24 -vrev vrevA".split()):
            self.assertEqual(FromSysArgv.multi("-serev"), ['24'])
        with MockVar(sys, "argv", "arg.py -serev".split()):
            self.assertEqual(FromSysArgv.multi("-serev"), [''])
        with MockVar(sys, "argv", "arg.py -vrev vrevA".split()):
            self.assertEqual(FromSysArgv.multi("-serev"), [])
        with MockVar(sys, "argv", "arg.py -serev 24 -vrev vrevA -serev 25".split()):
            self.assertEqual(FromSysArgv.multi("-serev"), ['24', '25'])


class Various_tests(TestCase):

    def test_taradd1(self):
        with TempDir(name=True, chdir=True) as tdir, \
                TempDir(name=True) as tdir2, \
                TempDir(name=True) as tdir3:
            File('a.file').touch()
            File('.git/abc').touch(mkdir=True)
            File('dir1/abc').touch(mkdir=True)
            TarAdd(f'{tdir2}/a.tar.gz', '.')
            untar(f'{tdir2}/a.tar.gz', tdir3)
            expect = '''
./.git/abc
./a.file
./dir1/abc
'''
            with Chdir(tdir3):
                self.assertTextEqual('\n'.join(sorted(Allfiles('.'))), expect)

    def test_taradd2(self):
        with TempDir(name=True, chdir=True) as tdir, \
                TempDir(name=True) as tdir2, \
                TempDir(name=True) as tdir3:
            File('a.file').touch()
            File('.git/abc').touch(mkdir=True)
            File('dir1/abc').touch(mkdir=True)
            File('temp/abc').touch(mkdir=True)
            TarAdd(f'{tdir2}/a.tar.gz', '.', exclude=['.git', 'temp'])
            untar(f'{tdir2}/a.tar.gz', tdir3)
            expect = '''
./a.file
./dir1/abc
'''
            with Chdir(tdir3):
                self.assertTextEqual('\n'.join(sorted(Allfiles('.'))), expect)

    def test_untar(self):
        with TempDir(name=True) as tdir:
            untar(f'{UT_DIR}/misc_files/job_dummy.tar.gz', tdir)
            self.assertEqual(set(os.listdir(tdir)), {'POR_TP'})

    def test_taradd_integration(self):
        # Integration test for TarAdd excluding both files and directories
        with TempDir(name=True, chdir=True) as tdir, \
                TempDir(name=True) as tdir2, \
                TempDir(name=True) as tdir3:
            # Create test structure with various files and directories
            File('keep_this.txt').touch('important data')
            File('complete_tp.tar.gz').touch('fake tar file content')
            File('another_exclude.zip').touch('another excluded file')
            File('.git/config').touch(mkdir=True)
            File('.git/HEAD').touch()
            File('.github/workflows/test.yml').touch(mkdir=True)
            File('Shared/.github/config').touch(mkdir=True)
            File('astra/data.txt').touch(mkdir=True)
            File('TPConfig/settings.ini').touch(mkdir=True)
            File('UserCode/test.py').touch(mkdir=True)
            File('Shared/TPConfig/more.ini').touch(mkdir=True)
            File('temp/cache.dat').touch(mkdir=True)
            File('valid_dir/keep.txt').touch(mkdir=True)
            File('InputFiles/data1.txt').touch(mkdir=True)
            File('InputFiles/data2.txt').touch()

            # Create tar with exclusions (matching mtplencode.py pattern)
            exclude_list = [
                '.git',
                '.github',
                'Shared/.github',
                'astra',
                'TPConfig',
                'UserCode',
                'Shared/TPConfig',
                'temp',
                'complete_tp.tar.gz',
                'another_exclude.zip',
                'InputFiles'
            ]
            TarAdd(f'{tdir2}/result.tar.gz', '.', exclude=exclude_list)

            # Extract to verify
            untar(f'{tdir2}/result.tar.gz', tdir3)

            # Expected files that should be included
            with Chdir(tdir3):
                all_files = sorted(Allfiles('.'))
                self.assertEqual(all_files, ['./keep_this.txt', './valid_dir/keep.txt'])

    def test_vmsize(self):
        num, unit = vmsize().split()
        self.assertTrue(int(num) > 30000, "vmsize check")
        self.assertEqual(unit, "kB")

    def test_which(self):
        # foundcase
        self.assertEqual(which('cdislookup'), '/usr/intel/bin/cdislookup')
        # not found case
        self.assertIs(which('cdislookupnotfound'), None)
        # direct specify
        self.assertEqual(which('/usr/intel/bin/cdislookup'), '/usr/intel/bin/cdislookup')

    def test_vmdata(self):
        num1, unit = vmsize("VmData").split()
        num2, unit = vmsize("VmSize").split()
        self.assertGreater(int(num1), 5000, "vmdata check")
        self.assertGreater(int(num2), int(num1), "vmsize greater than vmdata check")
        self.assertEqual(unit, "kB")
        self.assertRaises(Exception, vmsize, "VMX")   # unknown type

    def test_fullcmdline(self):
        with MockVar(sys, "argv", ['cmd.py', 'a', 'b', 'c']):
            self.assertEqual(fullcmdline(), "a b c")     # basic
        with MockVar(sys, "argv", ['cmd.py', 'a', 'b', 'c d']):
            self.assertEqual(fullcmdline(), "a b 'c d'")  # with space
        with MockVar(sys, "argv", ['cmd.py', '-a', 'b a', 'c d']):
            self.assertEqual(fullcmdline(), "-a 'b a' 'c d'")  # two space
        with MockVar(sys, "argv", ['cmd.py', '-a', "b'a", 'c"d']):
            self.assertEqual(fullcmdline(), """-a "b'a" 'c"d'""")  # special char
        with MockVar(sys, "argv", ['cmd.py', '-a', "b' a", 'c "d']):
            self.assertEqual(fullcmdline(), """-a "b' a" 'c "d'""")  # special char w/ space
        with MockVar(sys, "argv", ['cmd.py', '-a', """b'\"a""", 'c "d']):
            self.assertEqual(fullcmdline(), """-a b'\"a 'c \"d'""")  # both '"
        with MockVar(sys, "argv", ['cmd.py', '-a']):
            self.assertEqual(fullcmdline(True), CALLERBIN + " -a")

    def test_username_hostname(self):
        self.assertEqual(type(USERNAME), str)
        self.assertEqual(type(HOSTNAME), str)
        self.assertGreater(len(USERNAME), 2, "username length must be greater than 2 (exist)")
        self.assertGreater(len(HOSTNAME), 2, "hostname length must be greater than 2 (exist)")
        self.assertTrue(op.isdir(LAUNCH_CWD))
        self.assertEqual(USERNAME, os.environ['USER'])  # gross check

        # Validate IDSIDs
        self.assertFalse(is_idsid_valid('mfazlian'))
        self.assertTrue(is_idsid_valid(USERNAME))

    def test_is_exe(self):
        self.assertTrue(is_exe("python"), "is_exe() must return True. python is an executable")
        self.assertFalse(is_exe("pythonXX"), "is_exe() must return False. pythonXX is not an executable")

    def test_getcaller(self):
        self.assertEqual(os.path.basename(CALLERBIN), "test_shell.py")
        self.assertEqual(CALLERBIN[0], "/")   # must be absolute path
        self.assertTrue(os.path.exists(CALLERBIN), "CALLERBIN must exist")

    def test_pjoin(self):
        self.assertEqual(pjoin("a", "b c"), join("a", "b", "c"))
        self.assertEqual(pjoin("a"), join("a"))
        self.assertEqual(pjoin("a", "b"), join("a", "b"))
        self.assertEqual(pjoin("a", "b c d", "e f"), join("a", "b", "c", "d", "e", "f"))

    def test_tmpdir(self):   # this test works on windows and unix
        if IS_UNIX:
            self.assertEqual(tmpdir(), "/tmp")
        else:
            self.assertNotEqual(tmpdir(), "/tmp")

    def test_getuid(self):
        if IS_UNIX:
            self.assertIs(type(getuid()), int)
        else:
            self.assertIs(type(getuid()), str)

    def test_iseclipse(self):
        self.assertFalse(iseclipse_ut())    # This will fail on eclipse

    def test_groups(self):
        import grp
        allgrp = ''.join(group_names())
        self.assertFalse(allgrp.isdigit(), allgrp)
        self.assertTrue(str_isword(allgrp, ".-"), allgrp)

        # Some exception occurred
        def myfoo(id, func=grp.getgrgid, cnt=[0]):
            res = func(id)
            cnt[0] += 1
            if cnt[0] >= 2:    # error out on 2nd group
                raise Exception("Error")
            return res

        with MockVar(grp, "getgrgid", myfoo):
            self.assertEqual(len(group_names()), 1)

    @unittest.skipIf(*is_ut_option('OPTIONAL', message="cdislookup is not so robust"))
    def test_cdis_info_real(self):
        # pass case
        self.assertEqual(cdis('jqdelosr'), 'john.q.delos.reyes@intel.com')

    def test_cdis_info_ut(self):
        # pass case
        sout = 'somekey = somevalue\nDomainAddress = someemail@intel.com\n'

        with MockVar(SystemCall, "run_sout_serr", Mock(return_value=(0, sout, ''))):
            self.assertEqual(cdis('jqdelosr'), 'someemail@intel.com')

            # invalid key
            self.assertEqual(cdis('jqdelosr', key='Unknown'), '')

        # something wrong happened
        with self.assertRaisesRegex(Exception, "Error executing"):
            cdis('jqdelosrxx -q')

    def test_homedir(self):
        self.assertTrue(exists(homedir()))
        self.assertTrue(exists(homedir(USERNAME)))

    @unittest.skipIf(*is_ut_option('SKIP_NIGHTLY_BUILD', message="Flaky test during continuous integration", neg=False))
    def test_is_machine_up(self):
        # case 1 : machine is down
        with MockVar(SystemCall, "run_outonly", Mock(return_value=("100% packet loss"))):
            self.assertFalse(shell.is_machine_up("server1"))

        # case 2 : machine is up
        with MockVar(SystemCall, "run_outonly", Mock(return_value=("0% packet loss"))):
            self.assertTrue(shell.is_machine_up("server1"))
            self.assertFalse(shell.is_machine_up("server1", sshok=True))

            # Exception occurred
            with MockVar(shell, "Timeout", Mock(side_effect=Exception)):
                self.assertFalse(shell.is_machine_up("server1", sshok=True))

        # case 2 : machine is up
        with MockVar(SystemCall, "run_outonly", Mock(return_value=("unknown host"))):
            self.assertFalse(shell.is_machine_up("server1"))

        # real test
        self.assertTrue(is_machine_up(HOSTNAME))
        self.assertTrue(is_machine_up(HOSTNAME, sshok=True))
        self.assertFalse(is_machine_up(HOSTNAME + "ek"))

    @unittest.skipIf(*is_ut_option('SLOW', message="slowtest"))
    def test_ping_host(self):
        # case 1 : garbled text from ping command, no regex match
        with MockVar(SystemCall, "run_outonly", Mock(return_value=("this is a garbage string"))):
            self.assertFalse(shell.ping_host("server1"))
        with MockVar(SystemCall, "run_outonly", Mock(return_value=("rtt min/avg/max/mdev = 0.017/0.018/0.019/0.000 ms"))):
            self.assertEqual(shell.ping_host("server1"), '0.018ms')

        # real test
        self.assertTrue(ping_host("127.0.0.1"))
        self.assertTrue(ping_host("127.0.0.1", 1))
        self.assertFalse(ping_host("127.0.0.1foo", 1))
        self.assertFalse(ping_host("127.0.0.1", "bar"))

    def test_check_valid_user(self):
        # invalid user
        with self.assertRaisesRegex(Exception, "is not a valid user"):
            check_valid_user("abcdef")

        # user is not specified
        self.assertEqual(check_valid_user(), 1)

        # valid user
        with MockVar(sys, "stdout", StringIO()):
            check_valid_user(USERNAME)

    @unittest.skipIf(*is_ut_option('SLOW', message="slowtest"))
    @unittest.skipIf(*is_ut_option('SKIP_NIGHTLY_BUILD', message="Flaky test during continuous integration", neg=False))
    def test_is_alive_ssh(self):
        # basic test
        self.assertTrue(is_alive_ssh(HOSTNAME))

        # basic test, freegb=1 should pass
        self.assertTrue(is_alive_ssh(HOSTNAME, freegb=1))

        # basic test, freegb=100000 should fail
        self.assertFalse(is_alive_ssh(HOSTNAME, freegb=100000))

        # bad host should fail
        self.assertFalse(is_alive_ssh('q123'))    # unknown host

    @unittest.skipIf(*is_ut_option('OPTIONAL', message="slowtest"))
    def test_is_alive_ssh_slow(self):

        def fake_run_outtext1(*args, **kwargs):
            time.sleep(20)
            return (0, "")

        def fake_run_outtext2(*args, **kwargs):
            raise Exception("Fake exception raised")

        def fake_run_outtext3(*args, **kwargs):
            time.sleep(20)
            return (1, "Fake error message")

        print("Test timeout function (with Timeout)")
        sw = Elapsed()
        with MockVar(shell, "SystemCall", lambda args, **kwargs: time.sleep(20)):
            self.assertFalse(is_alive_ssh(HOSTNAME, timeout=2))
        print("Elapsed:", sw)

        print("Test timeout function (ssh native)")
        sw = Elapsed()
        with MockVar(SystemCall, "run_outtxt", fake_run_outtext1):
            self.assertFalse(is_alive_ssh(HOSTNAME, native_timeout=True, timeout=3))
        print("Elapsed:", sw)

        print("Test timeout function (ssh native, exception)")
        sw = Elapsed()
        with MockVar(SystemCall, "run_outtxt", fake_run_outtext2):
            self.assertFalse(is_alive_ssh(HOSTNAME, native_timeout=True, timeout=3))
        print("Elapsed:", sw)

        print("Test timeout function (ssh native, error code)")
        sw = Elapsed()

        with MockVar(SystemCall, "run_outtxt", fake_run_outtext3):
            self.assertFalse(is_alive_ssh(HOSTNAME, native_timeout=True, timeout=3))

        print("Elapsed:", sw)

    @unittest.skipIf(*is_ut_option('SKIP_NIGHTLY_BUILD', message="Flaky test during continuous integration", neg=False))
    def test_is_alive_ssh_df_outputs(self):
        def df_out1a(*args, **kwargs):
            msg = 'Filesystem            Size  Used Avail Use% Mounted on\n' \
                  '/dev/sda9             809G   16G  752G   3% /tmp'
            return (0, msg)

        def df_out1b(*args, **kwargs):
            msg = 'Filesystem            Size  Used Avail Use% Mounted on\n' \
                  '/dev/sda9           456809  1645 44236   3% /tmp'
            return (0, msg)

        def df_out2a(*args, **kwargs):
            msg = 'Filesystem      Size  Used Avail Use% Mounted on\n' \
                  '/dev/sda10      674G  104G  537G  17% /tmp'
            return (0, msg)

        def df_out2b(*args, **kwargs):
            msg = 'Filesystem      Size  Used Avail Use% Mounted on\n' \
                  '/dev/sda10      674M  104M  537M  17% /tmp'
            return (0, msg)

        def df_out2c(*args, **kwargs):
            msg = 'Filesystem      Size  Used Avail Use% Mounted on\n' \
                  '/dev/sda10      674K  104K  537K  17% /tmp'
            return (0, msg)

        def df_out3a(*args, **kwargs):
            msg = 'Filesystem            Size  Used Avail Use% Mounted on\n' \
                  '/dev/sda10            751G  3.1G  709G   1% /tmp'
            return (0, msg)

        def df_out4a(*args, **kwargs):
            msg = 'Filesystem            Size  Used Avail Use% Mounted on\n' \
                  '/dev/sda8             2.2T   53G  2.0T   3% /tmp'
            return (0, msg)

        def df_out4b(*args, **kwargs):
            msg = 'Filesystem            Size  Used Avail Use% Mounted on\n' \
                  '/dev/sda8             2.2tB   53gB  2.0tB   3% /tmp'
            return (0, msg)

        with MockVar(SystemCall, "run_outtxt", df_out1a):
            self.assertTrue(is_alive_ssh(HOSTNAME, freegb=2), " df_out1a failed")

        with MockVar(SystemCall, "run_outtxt", df_out1b):
            self.assertFalse(is_alive_ssh(HOSTNAME, freegb=45), " df_out1b failed")

        with MockVar(SystemCall, "run_outtxt", df_out2a):
            self.assertTrue(is_alive_ssh(HOSTNAME, freegb=2), " df_out2a failed")

        with MockVar(SystemCall, "run_outtxt", df_out2b):
            self.assertFalse(is_alive_ssh(HOSTNAME, freegb=10), " df_out2b failed")

        with MockVar(SystemCall, "run_outtxt", df_out2c):
            self.assertFalse(is_alive_ssh(HOSTNAME, freegb=2), " df_out2c failed")

        with MockVar(SystemCall, "run_outtxt", df_out3a):
            self.assertTrue(is_alive_ssh(HOSTNAME, freegb=2), " df_out3a failed")

        with MockVar(SystemCall, "run_outtxt", df_out4a):
            self.assertTrue(is_alive_ssh(HOSTNAME, freegb=2), " df_out4a failed")

        with MockVar(SystemCall, "run_outtxt", df_out4b):
            self.assertTrue(is_alive_ssh(HOSTNAME, freegb=2), " df_out4b failed")

        self.assertTrue(is_alive_ssh(HOSTNAME, dfdir='/p/pde/tvpv'), " Good path failed")

        self.assertFalse(is_alive_ssh(HOSTNAME, dfdir='/p/pde/bad_path'), " Bad path should have failed")

    def test_get_caller_exe(self):
        # use own pid
        with MockVar(os, "getppid", Mock(return_value=os.getpid())):
            self.assertIn(os.path.basename(get_caller_exe()), ('test_shell.py', 'covmain.py'))

        # unittests
        self.assertEqual(get_caller_exe(['python', '-u', 'try.py']), 'try.py')
        self.assertEqual(get_caller_exe(['python', '-u']), '')
        self.assertEqual(get_caller_exe(['-csh', 'abc']), '-csh')
        self.assertEqual(get_caller_exe(['-sh', 'abc']), '-sh')
        self.assertEqual(get_caller_exe(['/somepath/perl', 'abc.pl']), 'abc.pl')
        self.assertEqual(get_caller_exe(['']), '')

        # Real run python
        with MockVar(os.environ, 'PYTHONPATH', ROOT_ENV),\
                TempDir(name=True, delete=True) as tdir:
            tnm = File(join(tdir, "mymodule.py"))
            tnm.touch("#!%s -u\n" % sys.executable)
            tnm.touch("from gadget.shell import get_caller_exe, os\n")
            tnm.touch("print('%s OK' % get_caller_exe())\n")
            tnm.chmod("0775")
            tne = File(join(tdir, "myapp.py"))
            tne.touch("#!%s -u\n" % sys.executable)
            tne.touch("from gadget.shell import SystemCall\n")
            tne.touch("print(SystemCall('%s arg1', exe=True).run_outonly())" % tnm.get_name())
            tne.chmod("0775")
            self.assertEqual(SystemCall(tne.get_name(), exe=True).run_outonly(), '%s OK' % tne.get_name())

    def test_nfs_standard_path(self):

        # /nfs/site paths should remain unchanged.
        self.assertEqual("/nfs/site/disks/ccdo.hdk.models.010/models/soc_sb", nfs_standard_path("/nfs/site/disks/ccdo.hdk.models.010/models/soc_sb"))

        # Valid test cases.
        self.assertEqual("/nfs/site/disks/mdo_bxt_005/models/bxtp_C0", nfs_standard_path("/nfs/pdx/disks/mdo_bxt_005/models/bxtp_C0"))
        self.assertEqual("/p/hdk/rtl/emu_models/dhdk73/bxtp", nfs_standard_path("/p/hdk/rtl/emu_models/dhdk73/bxtp"))
        self.assertEqual("/nfs/site/disks/mdo_bxt_003", nfs_standard_path("/nfs/pdx/disks/mdo_bxt_003"))
        self.assertEqual("/nfs/site/disks/mdo_bxt_003", nfs_standard_path("/nfs/pdx/disks/mdo_bxt_003/"))
        self.assertEqual("/p/pde/tvpv", nfs_standard_path("/p/pde/tvpv", check_exist=True))

        # Check empty input.
        self.assertRaises(Exception, nfs_standard_path, "")

        # Non-existant path with check == True.
        self.assertRaises(Exception, nfs_standard_path, "some_path", True)

    def test_is_netbatch(self):
        my_env = {'MYVAR': 'myval'}
        with MockVar(os, "environ", my_env):
            self.assertFalse(is_netbatch())

        my_env = {'__NB_CLASS': 'pdx_vnc'}
        with MockVar(os, "environ", my_env):
            self.assertFalse(is_netbatch())

        my_env = {'__NB_CLASS': 'pdx_normal', '__NB_QUEUE': 'pdx_interactive'}
        with MockVar(os, "environ", my_env):
            self.assertFalse(is_netbatch())

        my_env = {'__NB_CLASS': 'pdx_normal', '__NB_QUEUE': 'pdx_misc_short_pp', '__NB_POOL': 'pdx_ion'}
        with MockVar(os, "environ", my_env):
            self.assertFalse(is_netbatch())

        my_env = {'__NB_CLASS': 'pdx_normal', '__NB_QUEUE': 'pdx_misc_short_pp', '__NB_POOL': 'pdx_misc',
                  '__NB_INTERACTIVE_SESSIONID': 'pdx_ion.307474872'}
        with MockVar(os, "environ", my_env):
            self.assertFalse(is_netbatch())

        my_env = {'__NB_CLASS': 'pdx_normal', '__NB_QUEUE': 'pdx_misc_short_pp', '__NB_POOL': 'pdx_misc'}
        with MockVar(os, "environ", my_env):
            self.assertTrue(is_netbatch())

    def test_is_vnc_machine(self):
        with MockVar(os.environ, "__NB_CLASS", MockVar.delete):
            self.assertFalse(is_vnc_machine())
        with MockVar(os.environ, "__NB_CLASS", "something"):
            self.assertFalse(is_vnc_machine())
        with MockVar(os.environ, "__NB_CLASS", "a_vnc"):
            self.assertTrue(is_vnc_machine())
        with MockVar(os.environ, "__NB_CLASS", "vnc"):
            self.assertTrue(is_vnc_machine())

    def test_get_calling_stack(self):
        with TempDir(name=True) as tdir:

            # Create proc files needed for testing caller stack info
            mkdirs(join(tdir, '12345'))
            mkdirs(join(tdir, '23456'))
            mkdirs(join(tdir, '34567'))
            mkdirs(join(tdir, '99999'))
            mkdirs(join(tdir, '99998'))
            File(join(tdir, '12345', 'cmdline')).touch("/usr/intel/bin/python\0-w\0/usr/intel/bin/child")
            File(join(tdir, '12345', 'status')).touch("Name:  python\n State: S (sleeping)\n Tgid: 12345\n Pid: 12345\n"
                                                      " PPid:  23456\n  VmPeak:     21345 kB\n VmSize:   21345 kB\n")
            File(join(tdir, '23456', 'cmdline')).touch("/usr/intel/bin/perl5.14.1-threads\0-w\0/p/pde/tvpv/bin/parent "
                                                       "-arg")
            File(join(tdir, '23456', 'status')).touch("Name:  perl\n State: S (sleeping)\n Tgid: 23456\n Pid:   23456\n"
                                                      " PPid:  34567\n  VmPeak:     21345 kB\n VmSize:   21345 kB\n")
            File(join(tdir, '34567', 'cmdline')).touch("/usr/intel/bin/perl\0-w\0/p/pde/tvpv/bin/grandparent -arg1 -a2")
            File(join(tdir, '34567', 'status')).touch("Name:  perl\n State: S (sleeping)\n Tgid:  34567\n Pid: 34567\n"
                                                      " PPid:  99999\n VmPeak:     21345 kB\n VmSize:   21345 kB\n")
            File(join(tdir, '99999', 'cmdline')).touch("tcsh")
            File(join(tdir, '99999', 'status')).touch("Name:  tcsh\n State: S (sleeping)\n Tgid:  3856\n Pid:   3856\n"
                                                      " PPid:  3854\n VmPeak:     21345 kB\n VmSize:   21345 kB\n")
            File(join(tdir, '99998', 'cmdline')).touch("/usr/intel/bin/perl\0-w")  # This should not happen irl, for cov
            File(join(tdir, '99998', 'status')).touch("Name:  tcsh\n State: S (sleeping)\n Tgid:  3856\n Pid:   3856\n"
                                                      " PPid:  3854\n VmPeak:     21345 kB\n VmSize:   21345 kB\n")

            expected = ['child', 'parent', 'grandparent']
            # Parses the cmdline/status files created in SetUp()
            self.assertEqual(get_calling_stack('12345', tdir), expected,
                             "Calling stack recursively parsed /proc/ files")

            # Some extra coverage tests
            mkdirs(join(tdir, '88888'))
            mkdirs(join(tdir, '88889'))
            mkdirs(join(tdir, '88887'))
            File(join(tdir, '88888', 'cmdline')).touch("bash -w")
            File(join(tdir, '88889', 'cmdline')).touch("xterm -x")
            File(join(tdir, '88887', 'cmdline')).touch("nothing_to_see_here")
            self.assertEqual(len(get_calling_stack('88888', tdir)), 0, 'Properly skip shell "bash"')
            self.assertEqual(len(get_calling_stack('88889', tdir)), 0, 'Properly skip "xterm"')
            self.assertEqual(len(get_calling_stack('88887', tdir)), 1, "Doesn't skip straight executables")
            self.assertEqual(len(get_calling_stack('99998', tdir)), 0, "Just Perl doesn't count")
            self.assertEqual(len(get_calling_stack(None, tdir)), 0)

            # Cover blacklist case where we keep searching
            mkdirs(join(tdir, '9'))
            mkdirs(join(tdir, '10'))
            mkdirs(join(tdir, '11'))
            mkdirs(join(tdir, '12'))
            mkdirs(join(tdir, '13'))
            File(join(tdir, '13', 'cmdline')).touch("/usr/intel/bin/python\0-w\0/usr/intel/bin/child\0-a\0-b")
            File(join(tdir, '13', 'status')).touch("Pid:   13\nPPid:  12\n")
            File(join(tdir, '12', 'cmdline')).touch("-usr/intel/bin/sh")  # Should get skipped, but keep looking
            File(join(tdir, '12', 'status')).touch("Pid:   12\nPPid:  11\n")
            File(join(tdir, '11', 'cmdline')).touch("/usr/intel/bin/perl5.14.1-threads\0-w\0/p/pde/tvpv/bin/parent")
            File(join(tdir, '11', 'status')).touch("Pid:   11\nPPid:  10\n")
            File(join(tdir, '10', 'cmdline')).touch("/var/netstar/lib/build_0829_12/nbjobleader.out\0/mdo/tvpv/sles11\0"
                                                    "/nfs/pdx/home/damacleo\0/nfs/pdx/home/damacleo")
            File(join(tdir, '10', 'status')).touch("Pid:   10\nPPid:  9\n")
            # Should have stopped and this one is never reached
            File(join(tdir, '9', 'cmdline')).touch("/usr/intel/bin/python2.7.5\0-w\0/p/pde/tvpv/bin/grandparent")
            File(join(tdir, '9', 'status')).touch("Pid:   9\nPPid:  1\n")

            expected = ['child', 'parent']
            stack = get_calling_stack(13, tdir)
            self.assertEqual(len(stack), 2)
            self.assertEqual(stack, expected)

            # Grab shell script name if it exists
            mkdirs(join(tdir, '21'))
            mkdirs(join(tdir, '22'))
            mkdirs(join(tdir, '23'))
            File(join(tdir, '23', 'cmdline')).touch("/usr/intel/bin/python\0-w\0/usr/intel/bin/child\0-a\0-b")
            File(join(tdir, '23', 'status')).touch("Pid:   23\nPPid:  22\n")
            File(join(tdir, '22', 'cmdline')).touch("-usr/intel/bin/tcsh")  # Should get skipped, but keep looking
            File(join(tdir, '22', 'status')).touch("Pid:   22\nPPid:  21\n")
            File(join(tdir, '21', 'cmdline')).touch("-usr/intel/bin/tcsh parent")
            File(join(tdir, '21', 'status')).touch("Pid:   21\nPPid:  20\n")
            stack = get_calling_stack(23, tdir)
            self.assertEqual(len(stack), 2)
            self.assertEqual(stack, expected)


class MachineInfo_tests(TestCase):

    def files(self, f):
        open(f, "w").write('''ABC
DEF
123
456
''')

    def files_2(self, f):
        open(f, "w").write('''ABC
Memory size is 26472
Memory size is 62708
Memory size is 62755
model name    : Intel(R) Xeon(R) CPU           E5450  @ 3.00GHz
model name    : Intel(R) Xeon(R) CPU           E5450  @ 3.00GHz
physical id    : 0
physical id    : 1
physical id    : 0
physical id    : 1
siblings       : 16
siblings       : 16
siblings       : 16
siblings       : 16
MemTotal:     32910156 kB
''')

    def files_3(self, f):
        open(f, "w").write('''ABC
Memory size is 26472
Memory size is 62708
Memory size is 62755
model name    : Intel(R) Xeon(R) CPU           E5450  @ 3.00GHz
model name    : Intel(R) Xeon(R) CPU           E5450  @ 3.00GHz
processor      : 0
processor      : 1
processor      : 2
processor      : 3
MemTotal:     32837120 kB
''')

    def test_machine_type(self):
        with TempDir(name=True) as tdir1:
            mi = MachineInfo()
            res = mi.machine_type()
            self.assertIs(type(res), str)

            fin = op.join(tdir1, "log")
            self.files_2(fin)
            mi = MachineInfo(cpuinfo=fin)
            res = mi.machine_type()
            self.assertEqual(res, "Intel(R) Xeon(R) CPU           E5450  @ 3.00GHz")

            fin = op.join(tdir1, "test")
            self.files(fin)
            self.assertRaises(Exception, mi.machine_type, fin)

    def test_n_physical_cores(self):
        with TempDir(name=True) as tdir1:
            mi = MachineInfo()
            res = mi.n_physical_cores()
            self.assertIs(type(res), int)

            fin = op.join(tdir1, "log")
            self.files_3(fin)
            mi = MachineInfo(cpuinfo=fin)
            res = mi.n_physical_cores()
            self.assertEqual(res, 4)

            fin = op.join(tdir1, "log")
            self.files_2(fin)
            mi = MachineInfo(cpuinfo=fin)
            res = mi.n_physical_cores()
            self.assertEqual(res, 32)

            fin = op.join(tdir1, "test")
            self.files(fin)
            mi = MachineInfo(cpuinfo=fin)
            self.assertRaises(Exception, mi.n_physical_cores)

    def test_n_physical_cpu(self):
        with TempDir(name=True) as tdir1:
            mi = MachineInfo()
            res = mi.n_physical_cpu()
            self.assertIs(type(res), int)

            fin = op.join(tdir1, "log")
            self.files_2(fin)
            mi = MachineInfo(cpuinfo=fin)
            res = mi.n_physical_cpu()
            self.assertEqual(res, 2)

            fin = op.join(tdir1, "test")
            self.files(fin)
            mi = MachineInfo(cpuinfo=fin)
            res = mi.n_physical_cpu()
            self.assertEqual(res, 0)

    def test_n_logical_cores(self):
        mi = MachineInfo()
        res = mi.n_logical_cores()
        self.assertIs(type(res), int)

        with TempDir(name=True) as tdir1:
            fin = op.join(tdir1, "log")
            self.files_2(fin)
            mi = MachineInfo(cpuinfo=fin)
            self.assertRaises(Exception, mi.n_logical_cores)

    def test_uptime_load(self):
        mi = MachineInfo()
        res = mi.uptime_load()
        self.assertIs(type(res), str)

    def test_n_users(self):
        mi = MachineInfo()
        res = mi.n_users()
        self.assertIs(type(res), int)

    def test_machine_memory_gb(self):
        with TempDir(name=True) as tdir1:
            mi = MachineInfo()
            res = mi.machine_memory_gb()
            self.assertIs(type(res), int)

            fin = op.join(tdir1, "log")
            self.files_2(fin)
            mi = MachineInfo(meminfo=fin)
            res = mi.machine_memory_gb()
            self.assertEqual(res, 31)

            fin = op.join(tdir1, "test")
            self.files(fin)
            mi = MachineInfo(meminfo=fin)
            self.assertRaises(Exception, mi.machine_memory_gb)

    def test_total_run_time(self):
        mi = MachineInfo()
        sw = Elapsed()
        res = mi.total_run_time(sw)
        self.assertIs(type(res), float)

    def test_get_history(self):
        mi = MachineInfo()
        res = mi.get_history()
        self.assertEqual(sorted(res.keys()), ['date', 'host', 'timesec', 'user'])

    def test_vmsize(self):
        mi = MachineInfo()
        self.assertIs(type(mi.vmsize_kb()), int)
        with MockVar(shell, "vmsize", Mock(return_value="12 kB")):
            self.assertEqual(mi.vmsize_kb(), 12)

    def test_vmdata(self):
        mi = MachineInfo()
        self.assertIs(type(mi.vmdata_kb()), int)
        with MockVar(shell, "vmsize", Mock(return_value="12 kB")):
            self.assertEqual(mi.vmdata_kb(), 12)

    def test_vpeak(self):
        mi = MachineInfo()
        self.assertIs(type(mi.vpeak_kb()), int)
        with MockVar(shell, "vmsize", Mock(return_value="12 kB")):
            self.assertEqual(mi.vpeak_kb(), 12)

    def test_getkb(self):
        mi = MachineInfo()
        self.assertRaisesRegex(Exception, "Cannot get unit", mi.getkb, '23kb')
        self.assertRaisesRegex(Exception, "Unknown unit", mi.getkb, '23 bb')
        self.assertEqual(mi.getkb("1234"), 1)
        self.assertEqual(mi.getkb("11 kb"), 11)
        self.assertEqual(mi.getkb("12 mb"), 12288)
        self.assertEqual(mi.getkb("13 gb"), 13631488)
        self.assertEqual(mi.getkb("14 tb"), 15032385536)

    def test_sles_version(self):
        mi = MachineInfo()
        # Valid case
        self.assertGreater(mi.sles_version(), 8)
        # Invalid case
        self.assertEqual(mi.sles_version('/notfound'), 0)

    def fake_sles10_stat_read(self):
        sles10_stat = "cpu  83924363 27263 35296908 3924972477 19325737 223697 2302458 0\n" \
                      "cpu0 6527727 4975 2962231 486293439 12348108 26617 96076 0\n" \
                      "cpu1 6713132 1021 3017671 498144659 364522 0 18125 0\n" \
                      "cpu2 8557798 2428 3830760 495383522 460766 0 23847 0\n" \
                      "cpu3 18969770 6969 7248426 481231233 734644 0 68069 0\n" \
                      "cpu4 5881927 1380 2608436 495855177 3896454 0 15728 0\n" \
                      "cpu5 5956921 846 2781858 499165305 336396 0 17767 0\n" \
                      "cpu6 7307241 2340 3563109 496935298 428695 0 22399 0\n" \
                      "cpu7 24009842 7302 9284414 471963841 756149 197079 2040445 0\n" \
                      "ctxt 6969484243\n" \
                      "btime 1523316804\n" \
                      "processes 272184702\n" \
                      "procs_running 1\n" \
                      "procs_blocked 1\n"
        for line in sles10_stat.split('\n'):
            yield line

    def test_sles10_version(self):
        """
        Have to fake SLES10 /proc/stat results to test that case in SystemStatus
        """
        mi = MachineInfo()
        with MockVar(mi, "sysname", Mock(return_value="2.6.16")), \
                MockVar(mi, 'statinfo', Mock(return_value=self.fake_sles10_stat_read())):
            self.assertLess(abs(mi.SystemStatus() - time.time()), 2, " Absolute time delta >2 sec")

    def test_ver2524_version(self):
        """
        Have to fake kernel 2.6.24 version /proc/stat results to test that case in SystemStatus
        """
        mi = MachineInfo()
        with MockVar(mi, "sysname", Mock(return_value="2.6.24")):
            self.assertLess(abs(mi.SystemStatus() - time.time()), 2, " Absolute time delta >2 sec")

    def test_bad_kernel_ver(self):
        """
        Have to fake kernel 2.5.28 version /proc/stat results to test that case in SystemStatus
        """
        mi = MachineInfo()
        with MockVar(mi, "sysname", Mock(return_value="2.5.28")):
            self.assertRaises(Exception, mi.SystemStatus, " Exception for unhandled kernel version not caught")

    @unittest.skipIf(*is_ut_option('SKIP_NIGHTLY_BUILD', message="Flaky test during continuous integration", neg=False))
    def test_native_version(self):
        """
        Have to test native /proc/stat results to test that case in SystemStatus
        """
        mi = MachineInfo()
        self.assertLess(abs(mi.SystemStatus(mytime=2, sleep=1) - time.time()), 2, " Absolute time delta >2 sec")

    def test_sysname(self):
        mi = MachineInfo()
        self.assertIn('linux', mi.sysname())
        self.assertNotIn('Error:', mi.sysname())
        self.assertIn('Error:', mi.sysname('sysnamex'))  # Do not remove/change this unittest, 'Error:' is used in test_location_base.py:Test_VepDirsBase.test_env_header_info

    @unittest.skipIf(*is_ut_option('SLOW', message="slowtest"))
    @unittest.skipIf(*is_ut_option('SKIP_NIGHTLY_BUILD', message="Flaky test during continuous integration", neg=False))
    def test_CalcLoad_no_irq(self):
        """
        Remove a busy value and an idle value from sysstat to test continues
        """
        mi = MachineInfo()
        now1 = mi.SystemStatus()
        self.assertLess((now1 - time.time()), 2, " Absolute time delta >2 sec")
        now2 = mi.SystemStatus(now1, 5)
        mi.sysstat['pre']['irq'] = None
        mi.sysstat['pre']['idle'] = None
        mi.sysstat['post']['steal'] = None
        load = mi.CalcLoad(now2 - now1)
        print("\n CalcLoad %s" % load)
        self.assertIn('System mem: Used', load)


class RunChild_tests(TestCase):
    def test_basic(self):
        def myfoo(val, pid):
            """child routine"""
            val.value = 123
            pid.value = os.getpid()

        val = multiprocessing.Value('i', 0)   # shared variable
        pid = multiprocessing.Value('i', os.getpid())   # shared variable
        with RunChild(target=myfoo, args=(val, pid)) as p:
            pass
        self.assertEqual(val.value, 123)
        self.assertNotEqual(pid.value, os.getpid())
        self.assertFalse(p.is_force_terminate())

    def test_notimeout(self):
        def myfoo(val):
            """child routine"""
            val.value = 123

        val = multiprocessing.Value('i', 0)   # shared variable
        with RunChild(timeout=0.1, target=myfoo, args=(val,)) as p:
            pass
        self.assertEqual(val.value, 123)
        self.assertFalse(p.is_force_terminate())

    def test_timeout(self):
        def myfoo(val):
            """Very long child routine"""
            val.value = 123
            for i in range(120):
                time.sleep(1)

        val = multiprocessing.Value('i', 0)   # shared variable
        with RunChild(timeout=0.1, target=myfoo, args=(val,)) as p:
            pass
        self.assertEqual(val.value, 123)
        self.assertTrue(p.is_force_terminate())

    def test_terminate(self):
        def myfoo(val):
            """Very long child routine"""
            val.value = 123
            for i in range(120):
                time.sleep(1)

        val = multiprocessing.Value('i', 0)   # shared variable
        with RunChild(target=myfoo, args=(val,)) as p:
            p.terminate()
        self.assertFalse(p.is_alive())
        self.assertFalse(p.is_force_terminate())

    @unittest.skipIf(*is_ut_option('SKIP_NIGHTLY_BUILD', message="flaky test. see failrepo.", neg=False))
    def test_incorrectargs(self):
        def myfoo(val, val2):
            """Very long child routine"""
            val.value = 123
            for i in range(120):
                time.sleep(1)

        val = multiprocessing.Value('i', 0)   # shared variable
        with RunChild(target=myfoo, args=(val,)) as p:
            time.sleep(0.1)
            self.assertFalse(p.is_alive(), "process should not be alive")

    def test_waitready(self):
        def myfoo(val, ready, sleeptime):
            """child process"""
            time.sleep(sleeptime)
            val.value = 123
            ready.value = 1

        val = multiprocessing.Value('i', 0)   # shared variable
        ready = multiprocessing.Value('i', 0)   # shared variable
        with RunChild(target=myfoo, args=(val, ready), kwargs={'sleeptime': 0.2}) as p:
            p.waitready(ready)
            self.assertEqual(val.value, 123)
            self.assertEqual(ready.value, 1)

        # timeout
        val = multiprocessing.Value('i', 0)   # shared variable
        ready = multiprocessing.Value('i', 0)   # shared variable
        with RunChild(target=myfoo, args=(val, ready), kwargs={'sleeptime': 3}) as p:
            self.assertRaises(Exception, p.waitready, ready, timeout=1)
            self.assertEqual(val.value, 0)
            self.assertEqual(ready.value, 0)
            p.terminate()

    def test_exception_in_current_pid(self):
        # This tests when current process raises exception, it should kill child proc immediately
        def myfoo(ready):
            """child process"""
            ready.value = 1
            time.sleep(10)
            ready.value = 2   # this should not be executed

        ready = multiprocessing.Value('i', 0)   # shared variable
        with self.assertRaisesRegex(ValueError, "myerror"):
            with RunChild(target=myfoo, args=(ready,)) as p:
                p.waitready(ready)
                raise ValueError("myerror")     # raise exception. This should kill child process.
        self.assertEqual(ready.value, 1)


class Stdin_tests(TestCase):

    def test_is_stdin(self):
        # coverage
        Stdin.is_stdin()
        sys.stdin.close()
        self.assertFalse(Stdin.is_stdin())    # exception case

    @unittest.skipIf(*is_ut_option('OPTIONAL', message="real stdin test only, fails using prod_run_fossil"))
    def test_is_stdin_real(self):
        # real test
        code = '''
from gadget.shell import Stdin
print(Stdin.is_stdin())
'''
        with TempName(exe=code, name=True) as tn1:
            # True case
            with TempName(name=True) as tn2:
                File(tn2).touch('#!/usr/intel/bin/tcsh\necho hello|%s\n' % tn1).chmod('0750')
                res = SystemCall(tn2).run_outonly()
                self.assertEqual(res, 'True')

            # False case
            res = SystemCall(tn1).run_outonly()
            self.assertEqual(res, 'False')

    def test_get_fh(self):
        import fileinput

        # normal file
        with TempDir(name=True) as tdir:
            File(join(tdir, 'a1')).touch('abc')
            with MockVar(OPT, 'all', [join(tdir, 'a1')]):
                self.assertEqual(Stdin.get_fh().read(), 'abc')

        # stdin (mocked)
        with MockVar(OPT, 'all', []):
            with MockVar(fileinput, "input", Mock(return_value='abc')):
                self.assertEqual(Stdin.get_fh(), 'abc')

        # real stdin
        code = '''
from gadget.shell import Stdin
for line in Stdin.get_fh():
   print("YAY %s" % line)
'''
        with MockVar(os.environ, 'PYTHONPATH', ROOT_ENV),\
                TempName(exe=code, name=True) as tn1:
            with TempName(name=True) as tn2:
                File(tn2).touch('#!/usr/intel/bin/tcsh\necho hello|%s\n' % tn1).chmod('0750')
                res = SystemCall(tn2).run_outonly()
                self.assertEqual(res, 'YAY hello')


class RsyncerBaseTest(TestCase):

    # from config.config_release_sites_common import sitecfg_common
    @patch("gadget.config_release_sites_common.sitecfg_common", {"JF": None, TvpvEnv.get_site().upper(): None})
    def test_init(self):
        # Bad site:
        with self.assertRaisesRegex(IOError, "Bad site given"):
            rsync = RsyncerBase("site")

        # Normal init, override exe
        rsync = RsyncerBase(site="PDX", rsync_exe="rsync", allow_local_cp=True)
        self.assertEqual(rsync.rsync_exe, "rsync")
        self.assertEqual(rsync.allow_local_cp, True)

        # Normal init, check members
        rsync = RsyncerBase("PDX")
        self.assertEqual(rsync.site, "JF")
        self.assertEqual(rsync.pipes, "/usr/intel/common/pkgs/pipes/1.47/bin/pipes")
        self.assertTrue("rsync_exe" in rsync.__dict__)
        self.assertEqual(rsync.allow_local_cp, False)

    @patch("gadget.shell.RsyncerBase.get_remote_machines")
    def test_do_rsync(self, mock_remote_mach):

        with MockVar(shell, "SystemCall", MagicMock()) as mock_syscall:
            mock_instance = mock_syscall.return_value
            mock_instance.run_sout_serr.return_value = 0, "success", ""

            rsync = RsyncerBase(TvpvEnv.get_site())
            self.assertEqual(rsync.allow_local_cp, False)

            # Bad direction (not push/pull)
            self.assertRaisesRegex(IOError, "Invalid value for rsync direction",
                                   rsync.do_rsync, ["src1", "src2"], "dest", "pullsh")

            # Push - successful, src dir list
            opts = "--recursive -avz --partial"
            mock_remote_mach.return_value = "remote_mach"
            mock_instance.run_sout_serr.return_value = (0, "out", None)
            ret = rsync.do_rsync(["src1", "src2"], "dest", "push", use_stage=False)
            mock_syscall.assert_called_with("{rsync} {opts} --timeout=60 --rsync-path={rsync} --rsh={pipes} {src} {dest}"
                                            .format(rsync=rsync.rsync_exe,
                                                    opts=opts,
                                                    pipes=rsync.pipes,
                                                    src="src1 src2",
                                                    dest="remote_mach:dest"), disp=True)
            self.assertTrue(ret)

            # Push - successful, src dir string
            mock_remote_mach.return_value = "remote_mach"
            mock_instance.run_sout_serr.return_value = (0, "out", None)
            ret = rsync.do_rsync("src1", "dest", "push", use_stage=False)
            mock_syscall.assert_called_with("{rsync} {opts} --timeout=60 --rsync-path={rsync} --rsh={pipes} {src} {dest}"
                                            .format(rsync=rsync.rsync_exe,
                                                    opts=opts,
                                                    pipes=rsync.pipes,
                                                    src="src1",
                                                    dest="remote_mach:dest"), disp=True)
            self.assertTrue(ret)

            # Pull - successfull, src dir string
            mock_remote_mach.return_value = "remote_mach"
            mock_instance.run_sout_serr.return_value = (0, "out", None)
            ret = rsync.do_rsync("src1", "dest", "pull", use_stage=False)
            mock_syscall.assert_called_with("{rsync} {opts} --timeout=60 --rsync-path={rsync} --rsh={pipes} {src} {dest}"
                                            .format(rsync=rsync.rsync_exe,
                                                    opts=opts,
                                                    pipes=rsync.pipes,
                                                    src="remote_mach:src1",
                                                    dest="dest"), disp=True)
            self.assertTrue(ret)

            # Validate post/preprocessing: Pull - successfull, src dir string,
            mock_remote_mach.return_value = "remote_mach"
            mock_instance.run_sout_serr.return_value = (0, "out", None)
            with patch("gadget.shell.RsyncerBase._rsync_preprocessing") as pre_mock, \
                    patch("gadget.shell.RsyncerBase._rsync_postprocessing") as post_mock:
                post_mock.return_value = "SUCESS"
                ret = rsync.do_rsync("src1", "dest", "pull", use_stage=False)
                pre_mock.assert_called_once_with()
                post_mock.assert_called_once_with()
                self.assertEqual(ret, "SUCESS")

            # Validate postprocessing on failure: Pull - unsuccessfull, src dir string,
            mock_remote_mach.return_value = "remote_mach"
            mock_instance.run_sout_serr.return_value = (1, "out", None)
            with patch("gadget.shell.RsyncerBase._rsync_preprocessing") as pre_mock, \
                    patch("gadget.shell.RsyncerBase._rsync_postprocessing") as post_mock:
                post_mock.return_value = "AFTER FAILURE"
                ret = rsync.do_rsync("src1", "dest", "pull", use_stage=False, postprocess_on_fail=True)
                pre_mock.assert_called_once_with()
                post_mock.assert_called_once_with()
                self.assertEqual(ret, "AFTER FAILURE")

            # Pull - Failure
            with CaptureStdoutLog() as p:
                mock_remote_mach.return_value = "remote_mach"
                mock_instance.run_sout_serr.return_value = (1, "out", "Oh no")
                ret = rsync.do_rsync(["src1"], "dest", "pull", use_stage=False)
                mock_syscall.assert_called_with("{rsync} {opts} --timeout=60 --rsync-path={rsync} --rsh={pipes} {src} {dest}"
                                                .format(rsync=rsync.rsync_exe,
                                                        opts=opts,
                                                        pipes=rsync.pipes,
                                                        src="remote_mach:src1",
                                                        dest="dest"), disp=True)
            log.debug(p.getvalue())
            self.assertIn("RSYNC failed", p.getvalue())
            self.assertFalse(ret)

            # Test local pull functionality with dirs that actually exist
            rsync_local = RsyncerBase(TvpvEnv.get_site(), allow_local_cp=True)
            self.assertEqual(rsync_local.allow_local_cp, True)

            with TempDir(chdir=False, name=True, delete=True) as tdir:
                # Put some src and dest dirs in the temp dir
                src_dir = join(tdir, "src")
                dest_dir = join(tdir, "dest")
                os.mkdir(src_dir)
                os.mkdir(dest_dir)

                # Files don't exist (not verified local) with local enabled: should use rsync
                mock_remote_mach.return_value = "remote_mach"
                mock_instance.run_sout_serr.return_value = (0, "out", None)
                ret = rsync_local.do_rsync("src1", "dest", "pull", use_stage=False)
                mock_syscall.assert_called_with("{rsync} {opts} --timeout=60 --rsync-path={rsync} --rsh={pipes} {src} {dest}"
                                                .format(rsync=rsync_local.rsync_exe,
                                                        opts=opts,
                                                        pipes=rsync_local.pipes,
                                                        src="remote_mach:src1",
                                                        dest="dest"), disp=True)
                self.assertTrue(ret)

                # Files exist with local disabled: should use rsync
                mock_remote_mach.return_value = "remote_mach"
                mock_instance.run_sout_serr.return_value = (0, "out", None)
                ret = rsync_local.do_rsync(src_dir, dest_dir, "pull", use_stage=False)
                mock_syscall.assert_called_with("{rsync} {opts} --timeout=60 --rsync-path={rsync} --rsh={pipes} {src} {dest}"
                                                .format(rsync=rsync.rsync_exe,
                                                        opts=opts,
                                                        pipes=rsync.pipes,
                                                        src=src_dir,
                                                        dest=dest_dir), disp=True)
                self.assertTrue(ret)

                # source dir doesn't exist, should clear local flag:
                src_dirs = join(src_dir, 'notthere')
                mock_remote_mach.return_value = "remote_mach"
                mock_instance.run_sout_serr.return_value = (0, "out", None)
                ret = rsync_local.do_rsync(src_dirs, dest_dir, "pull", use_stage=False)
                mock_syscall.assert_called_with("{rsync} {opts} --timeout=60 --rsync-path={rsync} --rsh={pipes} {src} {dest}"
                                                .format(rsync=rsync.rsync_exe,
                                                        opts=opts,
                                                        pipes=rsync.pipes,
                                                        src="remote_mach:" + src_dirs,
                                                        dest=dest_dir), disp=True)
                self.assertTrue(ret)

                # source dir exists, but specifies source host for push:
                src_dirs = "remote_host1:" + src_dir
                mock_remote_mach.return_value = "remote_mach"
                mock_instance.run_sout_serr.return_value = (0, "out", None)
                ret = rsync_local.do_rsync(src_dirs, dest_dir, "push", use_stage=False)
                self.assertFalse(ret)

                # source dir exists, but specifies source host for push:
                src_dirs = []
                src_dirs.append("remote_host1:" + src_dir)
                mock_remote_mach.return_value = "remote_mach"
                mock_instance.run_sout_serr.return_value = (0, "out", None)
                ret = rsync_local.do_rsync(src_dirs, dest_dir, "push", use_stage=False)
                self.assertFalse(ret)

                # source dir exists, but destination specifies host for push:
                dest_dirs = "remote_host2:" + dest_dir
                mock_remote_mach.return_value = "remote_mach"
                mock_instance.run_sout_serr.return_value = (0, "out", None)
                ret = rsync_local.do_rsync(src_dir, dest_dirs, "push", use_stage=False)
                self.assertFalse(ret)

                src_dirs = []
                src_dirs.append(src_dir)
                src_dirs.append(join(src_dir, 'notthere'))

                # one source dir doesn't exist, should clear local flag:
                mock_remote_mach.return_value = "remote_mach"
                mock_instance.run_sout_serr.return_value = (0, "out", None)
                ret = rsync_local.do_rsync(src_dirs, dest_dir, "push", use_stage=False)
                self.assertTrue(ret)

                # one source dir doesn't exist, should clear local flag:
                mock_remote_mach.return_value = "remote_mach"
                mock_instance.run_sout_serr.return_value = (0, "out", None)
                ret = rsync_local.do_rsync(src_dirs, dest_dir, "push", use_stage=False)
                mock_syscall.assert_called_with("{rsync} {opts} --timeout=60 --rsync-path={rsync} --rsh={pipes} {src} {dest}"
                                                .format(rsync=rsync.rsync_exe,
                                                        opts=opts,
                                                        pipes=rsync.pipes,
                                                        src=' '.join(src_dirs),
                                                        dest="remote_mach:" + dest_dir), disp=True)
                self.assertTrue(ret)

                # list of src_dirs and list_file given, should fail
                ret = rsync_local.do_rsync(src_dirs, dest_dir, "push", list_file='/non/file')
                self.assertFalse(ret)

                # try list_file with pull (not allowed)
                ret = rsync_local.do_rsync(src_dir, dest_dir, "pull", list_file='/non/file')
                self.assertFalse(ret)

                # list file does not exist, should fail
                ret = rsync_local.do_rsync(src_dir, dest_dir, "push", list_file='/non/file')
                self.assertFalse(ret)

                # valid test for list file - also guarantee only 1 space when use_pipes=False
                list_file = join(tdir, 'list_file.txt')
                File(list_file).touch('# list of files/dirs to sync would go here')
                ret = rsync_local.do_rsync(src_dir, dest_dir, "push", use_stage=False, list_file=list_file,
                                           use_pipes=False)
                mock_syscall.assert_called_with("{rsync} {opts} --timeout=60 --rsync-path={rsync} {src} {dest}"
                                                .format(rsync=rsync.rsync_exe,
                                                        opts=opts + " -avr --no-R --files-from=%s" % list_file,
                                                        src=src_dir,
                                                        dest=dest_dir), disp=True)
                self.assertTrue(ret)

            # Testcase when the path is exists in current and remote sites cause the local still in True
            rsync = RsyncerBase(TvpvEnv.get_site(), allow_local_cp=True)
            opts = "--recursive -avz --partial"
            mock_remote_mach.return_value = "remote_mach"
            mock_instance.run_sout_serr.return_value = (0, "out", None)
            rsync.site = "abc"
            ret = rsync.do_rsync(["/p/pde/tvpv"], "/p/pde/tvpv", "push", use_stage=False)
            mock_syscall.assert_called_with("{rsync} {opts} --timeout=60 --rsync-path={rsync} --rsh={pipes} {src} {dest}"
                                            .format(rsync=rsync.rsync_exe,
                                                    opts=opts,
                                                    pipes=rsync.pipes,
                                                    src="/p/pde/tvpv",
                                                    dest="remote_mach:/p/pde/tvpv"), disp=True)
            self.assertTrue(ret)
            rsync.site = TvpvEnv.get_site()

    def test__remote_chmod(self):
        """
        Test RsyncerBase._remote_chmod() private method.
        """
        with MockVar(shell, "SystemCall", MagicMock()) as mock_syscall:
            sync = RsyncerBase(TvpvEnv.get_site())
            # Success
            with TempDir(name=True, delete=True) as tdir, CaptureStdoutLog() as p:
                instance = mock_syscall.return_value
                instance.run_sout_serr.return_value = 0, "sout", "no_err"
                ret = sync._remote_chmod(host="host_mach", dest_dir=tdir, ch_str="testmod")
                mock_syscall.assert_called_with("ssh host_mach chmod testmod {}".format(tdir), disp=True)
            log.debug(p.getvalue())
            self.assertEqual(ret, True)
            self.assertIn("sout", p.getvalue())
            self.assertNotIn("no_err", p.getvalue())

            # Fail
            with TempDir(name=True, delete=True) as tdir, CaptureStdoutLog() as p:
                instance = mock_syscall.return_value
                instance.run_sout_serr.return_value = 1, "sout", "serr"
                ret = sync._remote_chmod(host="host_mach", dest_dir=tdir, ch_str="testmod")
                mock_syscall.assert_called_with("ssh host_mach chmod testmod {}".format(tdir), disp=True)
            log.debug(p.getvalue())
            self.assertEqual(ret, False)
            self.assertIn("ecode: 1", p.getvalue())
            self.assertIn("sout: sout", p.getvalue())
            self.assertIn("serr: serr", p.getvalue())

    def test__get_remote_machines(self):

        # with MockVar(shell, "cmd_safe", Mock(return_value=(0, "success", ""))):
        with MockVar(shell, "SystemCall", MagicMock()) as mock_syscall, \
                MockVar(shell, "is_alive_ssh", Mock(return_value=True)):
            from gadget.config_release_sites_common import sitecfg_common
            rsync = RsyncerBase(TvpvEnv.get_site())
            mock_instance = mock_syscall.return_value
            mock_instance.run_sout_serr.return_value = 0, "success", ""

            ret1 = rsync.get_remote_machines(TvpvEnv.get_site())
            log.info(" test__get_remote_machines: ret1 %s, all %s" % (ret1, sitecfg_common[TvpvEnv.get_site()]["hosts"]))
            self.assertTrue(ret1 in sitecfg_common[TvpvEnv.get_site()]["hosts"])

            rsync.previous_machine = "plxc001.pdx.intel.com"
            ret2 = rsync.get_remote_machines(TvpvEnv.get_site(), 10)
            log.info(" test__get_remote_machines: ret2 %s, rsync.previous_machine %s" % (ret2, rsync.previous_machine))
            self.assertEqual(ret2, "plxc001.pdx.intel.com")  # fake machine to test forced rsync.previous_machine

            # Implied site
            rsync = RsyncerBase(TvpvEnv.get_site())
            rsync.site = TvpvEnv.get_site()
            rsync.previous_machine = None
            ret3 = rsync.get_remote_machines(None, 2000)
            self.assertTrue(ret3 in sitecfg_common[TvpvEnv.get_site()]["hosts"])

        # no valid machines
        # with MockVar(shell, "cmd_safe", Mock(return_value=(1, "Failure!", "Could not connect!"))):
        with MockVar(shell, "SystemCall", MagicMock()) as mock_syscall:
            mock_instance = mock_syscall.return_value
            mock_instance.run_sout_serr.return_value = 1, "Failure!", "Could not connect!"

            local_site = TvpvEnv.get_site().upper()
            with patch("gadget.config_release_sites_common.sitecfg_common", {"JF": {'access': [],
                                                                                    'hosts': ['host1', 'host2'],
                                                                                    'limit': 90},
                                                                             local_site: {'access': [],
                                                                                          'hosts': [
                                                                                              'host1',
                                                                                              'host2'],
                                                                                          'limit': 90}}):
                rsync2 = RsyncerBase(TvpvEnv.get_site())
                remote_host = rsync2.get_remote_machines(TvpvEnv.get_site())
                self.assertFalse(remote_host, "Unexpectly found remote machine %s" % remote_host)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
