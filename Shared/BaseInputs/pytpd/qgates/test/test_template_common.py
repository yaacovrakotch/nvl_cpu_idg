#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for template_common.py

Steps:
1. For module qgate, remove "qgates." in "from qgates." since py file and unitest are on the same folder.
2. Replace TestCheckerNameHere to the name of the checker class
3. Run coverage and see what code is not tested
4. To run, execute this file "test_template_common.py -v"

"""
import sys
try:
    from setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests
from qgates.template_common import *        # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock


class TestCheckerNameHere(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic(self):
        tpobj = TestProgram(f'{UT_DIR}/MTLXXXXXXX37B0ASXXX/POR_TP/Class_MTL_P28/EnvironmentFile.env')

        ports = {999: 'abc'}
        data = [('ARR', 'XSA_SOC_VMIN_K_CSNF2_X_VCCSA_F2_2400_NONRECOVERY_KS_1507',
                 {'config_file': '~/file.xml', 'config_set': 'some_setting'}, ports),
                ('ARR', 'XSA_SOC_VMIN_K_CSNF2_X_VCCSA_F2_KS',
                 {'config_file': '~/file.xml', 'config_set': 'some_setting'}, ports)]
        with MockVar(tpobj.mtpl, "iter_flows", Mock(return_value=data)):
            obj = CheckerNameHere(tpobj)
            obj.main()

        # check results, one fail and one pass
        expect = '''
150 ARR XSA_SOC_VMIN_K_CSNF2_X_VCCSA_F2_2400_NONRECOVERY_KS_1507 has NONRECOVERY in name.
(150, 'ARR'): 1
'''
        self.assertTextEqual(obj.ut_result(), expect)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
