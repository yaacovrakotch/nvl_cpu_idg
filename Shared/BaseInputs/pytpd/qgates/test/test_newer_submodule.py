#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for newer_submodule.py

no pull requests found for branch "blah"

"""
import sys
try:
    from setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests

from qgates.newer_submodule import *        # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.gizmo import with_
from gadget.files import TempDir, File
from gadget.disk import Chdir
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock


NewerSub.is_unix = False
QGateExecute.repodir = f'{UT_DIR}/MTLXXXXXXX37B0ASXXX'


class TestSB(TestCase):

    # common pr_diff output across unittests: one submodule
    text_pr_diff = '''
diff --git a/Modules/FUN_CCF_C68/FUN_CCF_C68_CLASS_P68G2.mtpl b/Modules/FUN_CCF_C68/FUN_CCF_C68_CLASS_P68G2.mtpl
index 5e53a4154..bdaf53b44 100644
--- a/Modules/FUN_CCF_C68/FUN_CCF_C68_CLASS_P68G2.mtpl
+++ b/Modules/FUN_CCF_C68/FUN_CCF_C68_CLASS_P68G2.mtpl
@@ -1,4 +1,5 @@
diff --git a/Modules/TPI b/Modules/TPI
index a0777d904..c6e035aaa 160000
--- a/Modules/TPI
+++ b/Modules/TPI
@@ -1 +1 @@
-Subproject commit a0777d904af157ad91260ca613467ebb7cb31340
+Subproject commit c6e035aaaa99a36df293fdbce044090112ff1620
'''

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(MockVar, NewerSub, 'not_from_pr', Mock(return_value=False))
    @with_(Chdir, f'{UT_DIR}/MTLXXXXXXX37B0ASXXX')
    def test_passcase(self):
        # mocked system calls

        GitHub.clear()

        def fake_system_call(slf):
            cmd = ' '.join(slf.cmd)
            if 'gh pr diff' in cmd:
                return 0, self.text_pr_diff
            if 'git log' in cmd:
                return 0, '''c6e035aaaa99a36df293fdbce044090112ff1620
a0777d904af157ad91260ca613467ebb7cb31340
884ffb8ffb189039980bf3d0360516ead68c2e75
884ffb8ffb189039980bf3d0360516ead68c2e75
884ffb8ffb189039980bf3d0360516ead68c2e75
884ffb8ffb189039980bf3d0360516ead68c2e75
884ffb8ffb189039980bf3d0360516ead68c2e75
884ffb8ffb189039980bf3d0360516ead68c2e75
884ffb8ffb189039980bf3d0360516ead68c2e75
884ffb8ffb189039980bf3d0360516ead68c2e75
884ffb8ffb189039980bf3d0360516ead68c2e75
884ffb8ffb189039980bf3d0360516ead68c2e75
884ffb8ffb189039980bf3d0360516ead68c2e75
'''     # intentionally long for coverage
            if 'pr view' in cmd:
                return 0, ''    # labels: QQ
            raise Exception(f'Unknown cmd: [{cmd}]')

        tpobj = TestProgram('POR_TP/Class_MTL_P28/EnvironmentFile.env')
        obj = NewerSub(tpobj)
        with MockVar(SystemCall, 'run_outtxt', fake_system_call):
            obj.main()

        self.assertEqual(obj.result, [])   # no error
        self.assertEqual(obj.passed, {(231, 'TPI'): 1})

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(MockVar, NewerSub, 'not_from_pr', Mock(return_value=False))
    @with_(Chdir, f'{UT_DIR}/MTLXXXXXXX37B0ASXXX')
    def test_failcase(self):
        # This is exactly the same as test_passcase with from-sha-a removed in the git log output

        GitHub.clear()

        def fake_system_call(slf):
            cmd = ' '.join(slf.cmd)
            if 'gh pr diff' in cmd:
                return 0, self.text_pr_diff
            if 'git log' in cmd:
                return 0, '''c6e035aaaa99a36df293fdbce044090112ff1620
884ffb8ffb189039980bf3d0360516ead68c2e75
'''
            if 'pr view' in cmd:
                return 0, ''    # labels: QQ
            raise Exception(f'Unknown cmd: [{cmd}]')

        tpobj = TestProgram('POR_TP/Class_MTL_P28/EnvironmentFile.env')
        obj = NewerSub(tpobj)
        with MockVar(SystemCall, 'run_outtxt', fake_system_call):
            obj.main()

        print(obj.result)
        msg = ('Commit sha of Modules/TPI is from older rev. From: a0777d904af157ad91260ca613467ebb7cb31340 to '
               'c6e035aaaa99a36df293fdbce044090112ff1620. Did you mean to revert the submodule? '
               'If so, add [revert_submodule] label in the PR.')
        self.assertEqual(obj.result, [{'message': msg, 'id': 231, 'module': 'TPI'}])
        self.assertEqual(obj.passed, {})

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(Chdir, f'{UT_DIR}/MTLXXXXXXX37B0ASXXX')
    def test_failcase_prlabel(self):
        # This unittest should be exactly the same as test_failcase, but with pr_label

        GitHub.clear()

        def fake_system_call(slf):
            cmd = ' '.join(slf.cmd)
            if 'gh pr diff' in cmd:
                return 0, self.text_pr_diff
            if 'git log' in cmd:
                return 0, '''c6e035aaaa99a36df293fdbce044090112ff1620
884ffb8ffb189039980bf3d0360516ead68c2e75
'''
            if 'pr view' in cmd:
                return 0, 'labels: revert_submodule'
            raise Exception(f'Unknown cmd: [{cmd}]')

        tpobj = TestProgram('POR_TP/Class_MTL_P28/EnvironmentFile.env')
        obj = NewerSub(tpobj)
        with MockVar(SystemCall, 'run_outtxt', fake_system_call):
            obj.main()

        self.assertEqual(obj.result, [])
        self.assertEqual(obj.passed, {})

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(MockVar, NewerSub, 'not_from_pr', Mock(return_value=False))
    @with_(Chdir, f'{UT_DIR}/MTLXXXXXXX37B0ASXXX')
    def test_initial(self):

        GitHub.clear()

        def fake_system_call(slf):
            cmd = ' '.join(slf.cmd)
            if 'gh pr diff' in cmd:
                return 0, '''
diff --git a/.gitmodules b/.gitmodules
index 9c7af890e3..3c7c377f68 100644
--- a/.gitmodules
+++ b/.gitmodules
@@ -37,3 +37,6 @@
 [submodule "Modules/MIO_DDR"]
        path = Modules/MIO_DDR
        url = https://github.com/intel-restricted/applications.manufacturing.ate-test.torch.client.mtl.class.sharedmwio-ddrall.git
+[submodule "Shared/BaseInputs/pytpd"]
+       path = Shared/BaseInputs/pytpd
+       url = https://github.com/intel-innersource/applications.manufacturing.ate-test.tp-tools.pytpd.git
diff --git a/Modules/TPI b/Modules/TPI
new file mode 160000
index 0000000000..07177070ff
--- /dev/null
+++ b/Modules/TPI
@@ -0,0 +1 @@
+Subproject commit 07177070ffd491339b9921665496290a6d654e21
'''
            if 'git log' in cmd:
                return 0, '''07177070ffd491339b9921665496290a6d654e21
a0777d904af157ad91260ca613467ebb7cb31340
'''     # intentionally long for coverage
            if 'pr view' in cmd:
                return 0, ''    # labels: QQ
            raise Exception(f'Unknown cmd: [{cmd}]')

        tpobj = TestProgram('POR_TP/Class_MTL_P28/EnvironmentFile.env')
        obj = NewerSub(tpobj)
        with MockVar(SystemCall, 'run_outtxt', fake_system_call):
            obj.main()

        self.assertEqual(obj.result, [])   # no error
        self.assertEqual(obj.passed, {(231, 'TPI'): 1})

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(MockVar, NewerSub, 'not_from_pr', Mock(return_value=False))
    @with_(Chdir, f'{UT_DIR}/MTLXXXXXXX37B0ASXXX')
    def test_no_gitlog(self):
        # No git log output

        GitHub.clear()

        def fake_system_call(slf):
            cmd = ' '.join(slf.cmd)
            if 'gh pr diff' in cmd:
                return 0, self.text_pr_diff
            if 'git log' in cmd:
                return 0, ''
            if 'pr view' in cmd:
                return 0, ''
            raise Exception(f'Unknown cmd: [{cmd}]')

        tpobj = TestProgram('POR_TP/Class_MTL_P28/EnvironmentFile.env')
        obj = NewerSub(tpobj)
        with MockVar(SystemCall, 'run_outtxt', fake_system_call):
            obj.main()

        self.assertEqual(obj.result, [{'message': ('Output of [git log] seems to be incorrect since first sha is '
                                                   'not found c6e035aaaa99a36df293fdbce044090112ff1620 vs []. '
                                                   'Pls check above output.'),
                                       'id': 231,
                                       'module': 'TPI'}])
        self.assertEqual(obj.passed, {})

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(Chdir, f'{UT_DIR}/MTLXXXXXXX37B0ASXXX')
    def test_basic(self):
        # not from a git folder
        GitHub.clear()
        tpobj = TestProgram('POR_TP/Class_MTL_P28/EnvironmentFile.env')
        obj = NewerSub(tpobj)
        obj.main()

        self.assertEqual(obj.result, [])   # no error
        self.assertEqual(obj.passed, {})   # no passing


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
