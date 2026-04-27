#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Run unnittest for b69_validator.py
Checking simple pass and fail cases.

"""
import sys
try:
    from setenv_unittest import UT_DIR_REPO, ROOT_ENV     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR_REPO, ROOT_ENV     # must be first import for unittests

from qgates.vec_mem_chk import *        # replace this with your checker py.
# import qgates.base_specs_chk as base_specs
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock
from gadget.gizmo import with_, MockVar
from tp.testprogram import Env


class VecMem(TestCase):

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple7j', chdir=True, delete=True)
    def test_missing_soc(self):
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')
        perslice1 = f'{UT_DIR_REPO}/Simple7l/POR_TP/TGLH81/Reports/perslicevectormem_file.csv'
        obj = VecMemUse(tpobj)
        with MockVar(VecMemUse, "compare", Mock(return_value=perslice1)):
            obj.main()
            # pprint(obj.result)
            self.assertEqual(len(obj.result), 1)
            self.assertIn('HVM.soc does not exist', obj.result[0]['message'])

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple7l', chdir=True, delete=True)
    def test_command(self):
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')
        perslice1 = f'{UT_DIR_REPO}/Simple7l/POR_TP/TGLH81/Reports/perslicevectormem_file.csv'
        File(f'Shared/BaseInputs/Common/Common_TGLH81/HVM.soc').touch('''''', mkdir=True)
        with MockVar(VecMemUse, "compare", Mock(return_value=perslice1)):
            with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(1, ''))):
                obj = VecMemUse(tpobj)
                obj.main()
                self.assertTextEqual(obj.ut_result(), '257 BASE perslicevectormem_*.csv was not generated. Check TPPatternSuiteAnalyzer output')

                # sort version via os.environ
                with MockVar(os.environ, 'SOCFILE', 'blah/blah.soc'):
                    obj = VecMemUse(tpobj)
                    obj.main()
                    self.assertTextEqual(Env.xpath(obj.ut_result()), f'257 BASE {Env.xpath(os.getcwd() + "/blah/blah.soc")} does not exist')

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple7l', chdir=True, delete=True)
    def test_basic_pass(self):
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')

        # pass case
        obj = VecMemUse(tpobj)
        obj.compare([f'{UT_DIR_REPO}/misc_files/perslicevectormem_pass.csv'])
        self.assertEqual(obj.result, [])
        self.assertEqual(obj.passed, {(257, 'BASE'): 36})
        expect = '''
{
    "CPU_ALL:10_0": 408876032,
    "CPU_ALL:10_1": 408876032,
    "GCD_ALL:03_0": 14140416,
    "GCD_ALL:03_1": 14140416,
    "HUB_ALL:08_1": 89666560,
    "HUB_ALL:09_0": 89666560,
    "PCD_ALL:02_0": 119649280,
    "PCD_ALL:09_1": 119649280
}
'''
        self.assertTextEqual(File('POR_TP/TGLH81/Reports/vecmem.json').read(), expect)

        # fail case
        obj = VecMemUse(tpobj)
        obj.compare([f'{UT_DIR_REPO}/misc_files/perslicevectormem_fail.csv'])
        self.assertEqual(obj.result, [{'message': ' Slice: 02_0:PCD_ALL 120107649280 exceeded the 3500000000 limit',
                                       'id': 257,
                                       'module': 'BASE'}])
        self.assertEqual(obj.passed, {(257, 'BASE'): 35})


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
