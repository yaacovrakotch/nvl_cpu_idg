#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for pobj_cache.py
"""
from setenv_unittest import UT_DIR, UT_DIR_REPO, EXIST_PDX_I_DRIVE    # must be first import for unittests
from main.pobj_cache import *
from gadget.ut import TestCase, unittest, is_ut_option, Mock
from gadget.gizmo import MockVar
from gadget.files import TempDir, File
from gadget.shell import IS_UNIX
from gadget.helperclass import CaptureStdoutLog
from tp.testprogram import TestProgram
from pprint import pprint


class TestPC(TestCase):

    def test_basic(self):
        # main() Start to finish, with duplicate delete, 3 missing pobj, ignore commonfiles
        with TempDir(name=True, delete=True) as tdir:
            with MockVar(PobjCopy, 'TPFIXPATH', f'{tdir}/tpfixpath'), \
                    MockVar(PobjCopy, 'get_lpath', Mock(return_value=f'{tdir}/dest_beefc0')):

                res = []

                def fake(item, ldrive):
                    res.append((item, ldrive))

                # put the files
                File(f'{tdir}/tpfixpath/abcdd/a.pobj').touch(mkdir=True)
                File(f'{tdir}/tpfixpath/abcdd/b.pobj').touch(mkdir=True)
                File(f'{tdir}/tpfixpath/abcdd/mtl_com_abc.pobj').touch(mkdir=True)
                File(f'{tdir}/tpfixpath/abcdd/dup.pobj').touch(mkdir=True)
                File(f'{tdir}/tpfixpath/abcde/c.pobj').touch(mkdir=True)
                File(f'{tdir}/tpfixpath/abcde/d.pobj').touch(mkdir=True)
                File(f'{tdir}/tpfixpath/abcde/dup.pobj').touch(mkdir=True)
                File(f'{tdir}/tpfixpath/ff').touch()     # file - should be ignored
                File(f'{tdir}/dest_beefc0/c.pobj').touch(mkdir=True)

                tpobj = TestProgram(f'{UT_DIR_REPO}/Simple3/POR_TP/TGLH81/EnvironmentFile.env')
                obj = PobjCopy(tpobj)
                with MockVar(obj, 'robocopy', fake):
                    obj.main_postload()

                self.assertEqual(len(obj.missing), 3)
                self.assertEqual(res, [(f'{tdir}/tpfixpath/abcdd', f'{tdir}/dest_beefc0'),
                                       (f'{tdir}/tpfixpath/abcde', f'{tdir}/dest_beefc0')])

                self.assertEqual(sorted(os.listdir(f'{tdir}/tpfixpath/abcde')), ['c.pobj', 'd.pobj'])

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic_preload(self):
        # main() Start to finish, with duplicate delete, 3 missing pobj, ignore commonfiles
        with TempDir(name=True, delete=True) as tdir:
            with MockVar(PobjCopy, 'TPFIXPATH', f'{tdir}/tpfixpath'), \
                    MockVar(PobjCopy, 'get_lpath', Mock(return_value=f'{tdir}/dest_ee679c')), \
                    MockVar(PobjCopy, 'get_dpath', Mock(return_value=f'{tdir}/dest2_ee679c')):

                res = []

                def fake(item, ldrive):
                    res.append((item, ldrive))

                # Put files in tpfixpath - should be deleted
                File(f'{tdir}/tpfixpath/subdir/a.pobj').touch(mkdir=True)

                tpobj = TestProgram(f'{UT_DIR}/Integ_2A_2/ENG_TP/Class_MTL_P68/EnvironmentFile.env')
                obj = PobjCopy(tpobj)
                with MockVar(obj, 'robocopy', fake):
                    result = obj.main_preload()

                # should complete start to finish
                self.assertEqual(result, None)
                # should do robocopy
                self.assertEqual(res, [(f'{tdir}/dest_ee679c', f'{tdir}/dest2_ee679c')])
                # should write the marker
                self.assertEqual(File(f'{tdir}/sha_tpfixpath.txt').read(), 'ee679c')   # code is written
                # should empty
                self.assertEqual(os.listdir(f'{tdir}/tpfixpath'), [])

                # run again
                File(f'{tdir}/tpfixpath/subdir2/a.pobj').touch(mkdir=True)
                with MockVar(obj, 'robocopy', fake):
                    result = obj.main_preload()
                self.assertEqual(result, None)
                self.assertEqual(os.listdir(f'{tdir}/tpfixpath'), ['subdir2'])   # should not delete

                # no d drive
                with MockVar(PobjCopy, 'get_dpath', Mock(return_value=f'{tdir}/dest2')):
                    self.assertEqual(obj.main_preload(), 2)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_get_lpath(self):
        # no cache
        tpobj = TestProgram(f'{UT_DIR}/Simple3/POR_TP/TGLH81/EnvironmentFile.env')
        obj = PobjCopy(tpobj)
        self.assertEqual(obj.get_lpath(), '')
        self.assertEqual(obj.get_dpath(), '')
        self.assertEqual(obj.main_postload(), 11)
        self.assertEqual(obj.main_preload(), 1)

        # with cache
        tpobj = TestProgram(f'{UT_DIR}/Integ_2A_2/ENG_TP/Class_MTL_P68/EnvironmentFile.env')
        obj = PobjCopy(tpobj)
        self.assertEqual(obj.get_lpath(), 'L:\\cachepatterns\\OutputPobj_MTLP6C0A_beefc0')
        self.assertEqual(obj.get_dpath(), 'D:\\OutputPobj_MTLP6C0A_beefc0')

        # TPFIX path not found and L:\ drive not found in unix
        if IS_UNIX:
            self.assertEqual(obj.main_postload(), None)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_main(self):
        env = f'{UT_DIR}/Simple3/POR_TP/TGLH81/EnvironmentFile.env'

        # Invalid
        with MockVar(sys, 'argv', ['.py', 'unknown', env]):
            with self.assertRaisesRegex(ErrorUser, 'is invalid'):
                PobjCopy.main()

        # preload
        with MockVar(sys, 'argv', ['.py', 'preload', env]):
            self.assertEqual(PobjCopy.main(), 1)

        # postload
        with MockVar(sys, 'argv', ['.py', 'postload', env]):
            with MockVar(PobjCopy, 'get_lpath', lambda x: 'LPATH'):
                with CaptureStdoutLog() as p:
                    self.assertEqual(PobjCopy.main(), 11)
        expect = '''
-i- PobjCopy postload: using LPATH
-i- PobjCopy() is ignored since L:/cachepatterns path [LPATH] does not follow convention.
'''
        self.assertTextEqual(p.getvalue(), expect)

        # postload_donly
        with MockVar(sys, 'argv', ['.py', 'postload_donly', env]):
            with MockVar(PobjCopy, 'get_dpath', lambda x: 'DPATH'):
                with CaptureStdoutLog() as p:
                    self.assertEqual(PobjCopy.main(), 11)
        expect = '''
-i- PobjCopy postload: using DPATH
-i- PobjCopy() is ignored since L:/cachepatterns path [DPATH] does not follow convention.
'''
        self.assertTextEqual(p.getvalue(), expect)

        # sha
        with MockVar(sys, 'argv', ['.py', 'sha', f'{UT_DIR}/Integ_2A_2/ENG_TP/Class_MTL_P68/EnvironmentFile.env']):
            with CaptureStdoutLog() as p:
                self.assertEqual(PobjCopy.main(), 5)
            self.assertEqual(p.getvalue().strip(), 'ee679c')


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
