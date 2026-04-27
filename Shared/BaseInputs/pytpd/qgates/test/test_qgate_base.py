#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for qgate/qgate_base.py
"""
from setenv_unittest import UT_DIR_REPO, ROOT_ENV     # must be first import for unittests
from qgates.qgate_base import *
from gadget.ut import TestCase, unittest, is_ut_option, MockVar, Mock
from gadget.files import TempDir, File
from os.path import basename
from tp.testprogram import TestProgram
from gadget.gizmo import with_
from gadget.helperclass import CaptureStdoutLog
from gadget.tputil import trimut
from gadget.shell import TarAdd
import glob
import re


class TestUniqueID(TestCase):

    def test_check_all(self):
        # Make sure that all qgates.py has unique id

        # get all qgate .py in qgates/ folder
        allqgate = glob.glob(f'{ROOT_ENV}/qgates/*.py')
        robj = re.compile(r"self\.(add_error|add_pass)\((\d+)")
        found = {}
        for fname in allqgate:
            # This is a special file used in unittest, so we can't change this
            if basename(fname) == 'missing_ports.py':
                continue

            text = File(fname).read()
            for code, idno in robj.findall(text):
                if found.get(idno, fname) != fname:
                    self.fail(f'Duplicate qgate {idno} in:\n   {fname} vs\n   {found[idno]}')
                found[idno] = fname    # register it


class TestBaseClass(TestCase):

    def test_basic_with_error(self):
        env = f'{UT_DIR_REPO}/Simple3_missingports/POR_TP/TGLH81/EnvironmentFile.env'

        class Checker1(QGateBase):
            def main(self):
                self.add_error(101, "MOD1", 'message1 not defined in config')
                self.add_pass(100, "MOD1")

        tpobj = TestProgram(env).init()
        with CaptureStdoutLog() as p:
            print()
            obj = Checker1(tpobj)
            obj.run()     # This command called in individual checker run

        expect = '''
Passing stats:
Qgate#100: MOD1                      pass count=1

There are errors: 1
MOD1 -QGate101- message1 not defined in config
'''
        self.assertTextEqual('\n'.join(trimut(p.getvalue(), empty=True)), expect)

        expect = '''
101 MOD1 message1 not defined in config
(100, 'MOD1'): 1
'''
        self.assertTextEqual(obj.ut_result(), expect)

    def test_not_from_pr(self):

        class Checker3(QGateBase):

            def main(self):
                # This qgate is applicable only on PR. Ignore for tpbuild.
                if self.not_from_pr():     # pragma: no cover
                    log.info(f'-i- {self.__class__.__name__} is skipped, not from PR.')
                    return 1

                return 0

        env = f'{UT_DIR_REPO}/Simple3_missingports/POR_TP/TGLH81/EnvironmentFile.env'
        tpobj = TestProgram(env)

        # Normal run, skipped since not from pr
        self.assertEqual(Checker3(tpobj).main(), 1)

        # Normal run, from pr
        with MockVar(os.environ, 'FROM_PR', 'True'):
            self.assertEqual(Checker3(tpobj).main(), 0)

        # Normal run, from pr
        with MockVar(os.environ, 'FROM_PR', 'False'):
            self.assertEqual(Checker3(tpobj).main(), 1)

        # Normal run, standalone
        self.assertEqual(Checker3(tpobj, frompr=True).main(), 0)

    def test_check(self):
        env = f'{UT_DIR_REPO}/Simple3_missingports/POR_TP/TGLH81/EnvironmentFile.env'

        class Checker2(QGateBase):
            def main(self):
                self.check(True, 100, 'MOD1', 'This is pass')
                self.check(False, 101, 'MOD1', 'This is fail')

        tpobj = TestProgram(env).init()
        obj = Checker2(tpobj)
        obj.main()     # This command called in individual checker run
        expect = '''
101 MOD1 This is fail
(100, 'MOD1'): 1
'''
        self.assertTextEqual(obj.ut_result(), expect)

    def test_basic_no_error(self):
        env = f'{UT_DIR_REPO}/Simple3_missingports/POR_TP/TGLH81/EnvironmentFile.env'

        class Checker1(QGateBase):
            def main(self):
                self.add_pass(100, "MOD1")

        tpobj = TestProgram(env).init()
        with CaptureStdoutLog() as p:
            print()
            Checker1(tpobj).run()     # This command called in individual checker run

        expect = '''
Passing stats:
Qgate#100: MOD1                      pass count=1

Success! no errors
'''
        self.assertTextEqual('\n'.join(trimut(p.getvalue(), empty=True)), expect)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/SimpleNVL5', chdir=True, delete=True)
    def test_fulltp_untar(self):
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env').init()

        # complete_tp.tar.gz is missing
        QGateBase(tpobj=tpobj)
        self.assertEqual(QGateBase.fulltpobj, None)

        # complete_tp.tar.gz is existing
        TarAdd('complete_tp.tar.gz', '.', exclude=['.git', 'temp'])
        QGateBase(tpobj=tpobj)
        self.assertEqual(basename(QGateBase.fulltpobj.envdir), 'TGLH81')

        with MockVar(QGateBase, '_fulltp_untar', Mock(side_effect=Exception)):
            QGateBase(tpobj=tpobj)   # this should pass

        # clear it for suceceding unittests
        QGateBase.fulltpobj = None
        QGateBase.fulltp_tempdir = None


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
