#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for nvl_lsaraster_port4.py

To run: python test_nvl_lsaraster_port4.py -v
"""
import sys
try:
    from setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests

from qgates.nvl_lsaraster_port4 import Binning
from tp.testprogram import TestProgram
from gadget.ut import TestCase, unittest, MockVar
from unittest.mock import Mock


class TestBinning(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_missing_port_4(self):
        tpobj = TestProgram(f'{UT_DIR}/MTLXXXXXXX37B0ASXXX/POR_TP/Class_MTL_P28/EnvironmentFile.env')
        flows = [
            ('MOD1', 'ITEM1', {'TEMPLATE': 'PrimeLSARasterTestMethod'}, {1: {}, 2: {}}),
        ]
        with MockVar(tpobj.mtpl, "iter_flows", Mock(return_value=flows)):
            obj = Binning(tpobj)
            obj.main()
        result = obj.ut_result()
        self.assertIn("269 MOD1 PrimeLSARasterTestMethod test:ITEM1 does not have a required port 4", result)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_with_port_4(self):
        tpobj = TestProgram(f'{UT_DIR}/MTLXXXXXXX37B0ASXXX/POR_TP/Class_MTL_P28/EnvironmentFile.env')
        flows = [
            ('MOD2', 'ITEM2', {'TEMPLATE': 'PrimeLSARasterTestMethod'}, {4: {}, 1: {}}),
        ]
        with MockVar(tpobj.mtpl, "iter_flows", Mock(return_value=flows)):
            obj = Binning(tpobj)
            obj.main()
        result = obj.ut_result()
        self.assertIn("(269, 'MOD2'): 1", result)
        self.assertNotIn("does not have a required port 4", result)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_non_prime_template(self):
        tpobj = TestProgram(f'{UT_DIR}/MTLXXXXXXX37B0ASXXX/POR_TP/Class_MTL_P28/EnvironmentFile.env')
        flows = [
            ('MOD3', 'ITEM3', {'TEMPLATE': 'OtherTestMethod'}, {1: {}, 4: {}}),
        ]
        with MockVar(tpobj.mtpl, "iter_flows", Mock(return_value=flows)):
            obj = Binning(tpobj)
            obj.main()
        result = obj.ut_result()
        self.assertEqual(result.strip(), '')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_multiple_flows(self):
        tpobj = TestProgram(f'{UT_DIR}/MTLXXXXXXX37B0ASXXX/POR_TP/Class_MTL_P28/EnvironmentFile.env')
        flows = [
            ('MOD1', 'ITEM1', {'TEMPLATE': 'PrimeLSARasterTestMethod'}, {1: {}, 2: {}}),  # missing port 4
            ('MOD2', 'ITEM2', {'TEMPLATE': 'PrimeLSARasterTestMethod'}, {4: {}, 1: {}}),  # has port 4
            ('MOD3', 'ITEM3', {'TEMPLATE': 'OtherTestMethod'}, {4: {}}),                  # not checked
        ]
        with MockVar(tpobj.mtpl, "iter_flows", Mock(return_value=flows)):
            obj = Binning(tpobj)
            obj.main()
        result = obj.ut_result()
        self.assertIn("269 MOD1 PrimeLSARasterTestMethod test:ITEM1 does not have a required port 4", result)
        self.assertIn("(269, 'MOD2'): 1", result)
        self.assertNotIn("269 MOD3", result)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
