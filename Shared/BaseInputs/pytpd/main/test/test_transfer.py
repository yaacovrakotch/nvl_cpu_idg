#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for transfer.py
"""
from setenv_unittest import UT_DIR, ROOT_ENV, UT_DIR_REPO    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option, MockVar, IS_UNIX, IS_WIN
from gadget.files import TempDir, File
from gadget.disk import Chdir
from gadget.gizmo import with_
from main.transfer import *
from os.path import join, dirname, abspath
from gadget.shell import HOSTNAME
from gadget.helperclass import CaptureStdoutLog
from main.tp_audit import TPInfo
import shutil


class TestTTP(TestCase):

    def test_updatetp(self):
        with TempDir(name=True, chdir=True, startcopy=f'{UT_DIR_REPO}/Simple6') as tdir:
            with MockVar(sys, 'argv', ['transfer.py', 'POR_TP/TGLH81/EnvironmentFile.env']):
                main()
            with CaptureStdoutLog() as p:
                with MockVar(sys, 'argv', ['tpaudit.py', 'POR_TP/TGLH81/EnvironmentFile.env', '-plist']):
                    TPInfo().main()
            expect = f'''
{Env.xpath(tdir)}/plists/Shops.plist
{Env.xpath(tdir)}/plists/fuse.plist
'''
            self.assertTextEqual(p.getvalue(), expect)

            # run again - do nothing
            with MockVar(sys, 'argv', ['transfer.py', 'POR_TP/TGLH81/EnvironmentFile.env']):
                with CaptureStdoutLog() as p:
                    main()
            expect = f'''
-i- Nothing to do - {tdir}/plists already exist
'''
            self.assertTextEqual(p.getvalue(), expect)

    @unittest.skipIf(IS_WIN, 'unix only')
    def test_integ(self):
        with TempDir(name=True, chdir=True, delete=True) as tdir:
            # setup
            mkdirs('src')
            mkdirs('dest')
            mkdirs('tplist')
            shutil.copytree(f'{UT_DIR}/Simple6', 'src/TP1')

            # run it
            res = TTP(HOSTNAME).main(f'{tdir}/src',
                                     '*/POR_TP/*/EnvironmentFile.env',
                                     f'{tdir}/tplist',
                                     f'{tdir}/dest')
            self.assertEqual(res, [f'{tdir}/dest/TP1'])

            # check output
            self.assertEqual(len(os.listdir(f'{tdir}/dest/TP1/plists')), 5)
            env = File(f'{tdir}/dest/TP1/POR_TP/TGLH81/EnvironmentFile.env').read()
            print(env)
            self.assertIn('dest/TP1/plists', env)

    @unittest.skipIf(IS_WIN, 'unix only')
    def test_main(self):
        with TempDir(name=True, chdir=True, delete=True) as tdir:
            # setup
            mkdirs('src')
            mkdirs('dest')
            mkdirs('tplist')
            shutil.copytree(f'{UT_DIR}/Simple6', 'src/TP1')

            # Display the TP
            with MockVar(sys, 'argv', ['a.py', HOSTNAME, f'{tdir}/src', 'POR_TP/*/EnvironmentFile.env']):
                with CaptureStdoutLog() as p:
                    main()
                self.assertEqual(p.getvalue().split('\n')[-2], 'TP1')

            # Copy one TP
            with MockVar(sys, 'argv', ['a.py', HOSTNAME, f'{tdir}/src/TP1', f'{tdir}/dest']):
                main()
                self.assertEqual(os.listdir('dest'), ['TP1'])

            # invalid
            with MockVar(sys, 'argv', ['a.py']):
                with CaptureStdoutLog() as p:
                    main()
                self.assertIn('Display list of TP', p.getvalue())

    @unittest.skipIf(IS_WIN, 'unix only')
    def test_eseu(self):
        obj = TTP(HOSTNAME)
        self.assertEqual(obj.eseu, '')
        obj = TTP(HOSTNAME, eseu=True)
        self.assertEqual(obj.eseu, 'eseu.py')


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
