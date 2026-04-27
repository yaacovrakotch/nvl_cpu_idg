#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for check_pattern_lock.py
"""
import sys
try:
    from setenv_unittest import UT_DIR, UT_DIR_REPO, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR, UT_DIR_REPO, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests

from qgates.check_pattern_lock import *
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from pprint import pprint
from gadget.gizmo import with_
from tp.testprogram import Env
from unittest.mock import Mock


class TestCheckLock(TestCase):

    @with_(TempDir, chdir=True, delete=True)
    def test_error_lock_check(self):
        # default
        self.assertEqual(CheckLock.error_lock_check([]), True)
        # all match
        File('POR_TP/class/InputFiles/allow_unlocked.txt').touch('Mdrv\nMfus', mkdir=True, newfile=True)
        self.assertEqual(CheckLock.error_lock_check(['/path/Mdrv', '/path/Mfus']), False)
        File('POR_TP/class/InputFiles/allow_unlocked.txt').touch('M', mkdir=True, newfile=True)
        self.assertEqual(CheckLock.error_lock_check(['/path/Mdrv', '/path/Mfus']), False)
        # partial match
        File('POR_TP/class/InputFiles/allow_unlocked.txt').touch('Mdrv', mkdir=True, newfile=True)
        self.assertEqual(CheckLock.error_lock_check(['/path/Mdrv', '/path/Mfus']), True)
        # partial match
        File('POR_TP/class/InputFiles/allow_unlocked.txt').touch('xxx', mkdir=True, newfile=True)
        self.assertEqual(CheckLock.error_lock_check(['/path/Mdrv', '/path/Mfus']), True)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_get_pat_patch_unlocked_real(self):
        obj = CheckLock(f'{UT_DIR}/mtt_tp/POR_TP/Class_MTL_P68/EnvironmentFile.env')
        result = obj.get_pat_patch_unlocked()
        self.assertEqual(len(list(result)), 0)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_get_pat_patch_unlocked(self):
        obj = CheckLock(f'{UT_DIR}/mtt_tp/POR_TP/Class_MTL_P68/EnvironmentFile.env')
        with TempDir(name=True) as tdir:
            File(f'{tdir}/Mtpidrng/RevTCSxMA0.0/p0/plb/a.plb').touch(mkdir=True)
            File(f'{tdir}/Mtpidrng/RevTCSxMA0.0/p0/locked').touch(mkdir=True)
            File(f'{tdir}/Mtpi/RevTCSxMA0.0/p0/plb/a.plb').touch(mkdir=True)
            File(f'{tdir}/Mtpidrng/RevTCSxMA0.0/p0/plb/slim/a.plb').touch(mkdir=True)
            paths = [f'{tdir}/Mtpidrng/RevTCSxMA0.0/p0/plb',
                     f'{tdir}/Mtpi/RevTCSxMA0.0/p0/plb',
                     f'{tdir}/Mtpidrng/RevTCSxMA0.0/p0/plb/slim',       # slim
                     f'{tdir}/MtpidrngSORT/RevTCSxMA0.0/p0/plb',        # sort
                     f'{tdir}'                                          # random
                     ]
            with MockVar(Env, 'get_plist_paths', Mock(return_value=paths)):
                self.assertEqual(list(obj.get_pat_patch_unlocked()),
                                 [f'{tdir}/Mtpi/RevTCSxMA0.0/p0'])

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_main(self):
        # no check of eng_tp
        mvtp = f'{UT_DIR}/torch_mvtp/ENG_TP/Class_MTL_P68_DEBUG/EnvironmentFile.env'
        self.assertEqual(CheckLock(mvtp).main(), 1)

        # with day_code
        portp = f'{UT_DIR}/mtt_tp/POR_TP/Class_MTL_P68/EnvironmentFile.env'
        with MockVar(sys, 'argv', f'a.py {day_code()}'):
            self.assertEqual(CheckLock(portp).main(), 2)

        # pass case
        CheckLock(portp).main()

        # fail case
        with MockVar(CheckLock, 'get_pat_patch_unlocked', Mock(return_value=['/a'])):
            with self.assertRaisesRegex(ErrorUser, 'Unlocked pattern patch'):
                CheckLock(portp).main()

        # allow_unlocked.txt
        with TempDir(chdir=True):
            File('POR_TP/class/InputFiles/allow_unlocked.txt').touch('abc', mkdir=True, newfile=True)
            with MockVar(CheckLock, 'get_pat_patch_unlocked', Mock(return_value=['/abc'])):
                CheckLock(portp).main()

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(MockVar, os.environ, 'VEP2_ROOT', '/p')
    def test_lockit(self):
        portp = f'{UT_DIR}/mtt_tp/POR_TP/Class_MTL_P68/EnvironmentFile.env'
        unlocked_path = ['/intel/hdmxpats/mtl/MaaaCdrv/RevTCCXXA4.0/p4']
        with MockVar(CheckLock, 'get_pat_patch_unlocked', Mock(return_value=unlocked_path)), \
                MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, 'ci_plist running. ok'))):
            result = CheckLock(portp).lock_it()
            self.assertEqual(result, 'ci_plist.py -module MaaaCdrv -rev RevTCCXXA4.0p4 -lock -dev -comment Lock_for_tp_integration')


class TestQgatePatternLock(TestCase):

    def test_basic(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6tos4/POR_TP/TGLH81/EnvironmentFile.env')
        obj = QgatePatternLock(tpobj)

        # case: not from a PR
        self.assertEqual(obj.main(), 1)

        # pass case
        with MockVar(os.environ, 'FROM_PR', 'True'):
            obj.main()
        self.assertEqual(obj.result, [])
        self.assertEqual(obj.passed, {(249, 'BASE'): 1})

        # fail case

        def fake(slf):
            raise ErrorUser('blaherror', 'blahsuggestion')

        with MockVar(os.environ, 'FROM_PR', 'True'), \
                MockVar(CheckLock, 'main', fake):
            obj.main()
        pprint(obj.result)
        self.assertEqual(obj.result, [{'id': 249, 'message': 'blaherror', 'module': 'BASE'}])


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
