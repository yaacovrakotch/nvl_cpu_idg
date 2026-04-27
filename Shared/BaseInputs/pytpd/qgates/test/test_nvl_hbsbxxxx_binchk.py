#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for nvl_hbsbxxxx_binchk.py

To run: python testnvl_hbsbxxxx_binchk.py -v
"""
import sys
try:
    from setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests

from qgates.nvl_hbsbxxxx_binchk import *
from tp.testprogram import TestProgram
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from unittest.mock import Mock


class TestBinning(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic(self):
        tpobj = TestProgram(f'{UT_DIR}/MTLXXXXXXX37B0ASXXX/POR_TP/Class_MTL_P28/EnvironmentFile.env')
        flows = [
            ('MOD1', 'ITEM1', {}, {1: {'SetBin': 'BIN1_1', 'Return': 'RET1', 'IncrementCounters': 'BIN1_1'}}),
            ('MOD2', 'ITEM2', {}, {2: {'SetBin': 'BIN2_2', 'Return': 'RET2', 'IncrementCounters': 'BIN2_2'},
                                   3: {'SetBin': 'BIN2_2', 'Return': 'RET3', 'IncrementCounters': 'BIN2_2'}}),
            ('MOD3', 'ITEM3', {}, {4: {'SetBin': 'BIN1_4', 'Return': 'RET4', 'IncrementCounters': 'BIN1_4'}}),
        ]
        with MockVar(tpobj.mtpl, "iter_flows", Mock(return_value=flows)):
            obj = Binning(tpobj)
            obj.main()
        expect = '''
282 MOD2 ITEM2 BIN2_2 of port RET3 does not end with "_<port_number>" or "_n1"/"_n2"
284 MOD2 Duplicate SetBin "BIN2" found within module MOD2
285 MOD1 SetBin "BIN1" is used by multiple modules: MOD1, MOD3
285 MOD3 SetBin "BIN1" is used by multiple modules: MOD1, MOD3
(282, 'MOD1'): 1
(282, 'MOD2'): 1
(282, 'MOD3'): 1
(283, 'MOD1'): 1
(283, 'MOD2'): 2
(283, 'MOD3'): 1
(284, 'MOD1'): 1
(284, 'MOD3'): 1
(285, 'MOD2'): 1
        '''
        self.assertTextEqual(obj.ut_result(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_setbin_port_number_error(self):
        tpobj = TestProgram(f'{UT_DIR}/MTLXXXXXXX37B0ASXXX/POR_TP/Class_MTL_P28/EnvironmentFile.env')
        flows = [
            ('MODX', 'ITEMX', {}, {99: {'SetBin': 'BINX_n1', 'Return': 'RETX', 'IncrementCounters': 'BINX_99'}}),
        ]
        with MockVar(tpobj.mtpl, "iter_flows", Mock(return_value=flows)):
            obj = Binning(tpobj)
            obj.main()
        expect = '''
282 MODX ITEMX BINX_n1 of port RETX does not end with "_<port_number>" or "_n1"/"_n2"
(283, 'MODX'): 1
(284, 'MODX'): 1
(285, 'MODX'): 1
        '''
        self.assertTextEqual(obj.ut_result(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_setbin_incrementcounter_mismatch(self):
        tpobj = TestProgram(f'{UT_DIR}/MTLXXXXXXX37B0ASXXX/POR_TP/Class_MTL_P28/EnvironmentFile.env')
        flows = [
            ('MODY', 'ITEMY', {}, {5: {'SetBin': 'BINY_5', 'Return': 'RETY', 'IncrementCounters': 'BINZ_5'}}),
        ]
        with MockVar(tpobj.mtpl, "iter_flows", Mock(return_value=flows)):
            obj = Binning(tpobj)
            obj.main()
        expect = '''
283 MODY ITEMY of port RETY has a SetBin: BINY and IncrementCounter: BINZ 8 digit bin that do not match
(282, 'MODY'): 1
(284, 'MODY'): 1
(285, 'MODY'): 1
        '''
        self.assertTextEqual(obj.ut_result(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_no_duplicate_setbin_within_module(self):
        tpobj = TestProgram(f'{UT_DIR}/MTLXXXXXXX37B0ASXXX/POR_TP/Class_MTL_P28/EnvironmentFile.env')
        flows = [
            ('MODZ', 'ITEMZ', {}, {7: {'SetBin': 'BINZ_7', 'Return': 'RETZ', 'IncrementCounters': 'BINZ_7'},
                                   8: {'SetBin': 'BINY_8', 'Return': 'RETZ2', 'IncrementCounters': 'BINY_8'}}),
        ]
        with MockVar(tpobj.mtpl, "iter_flows", Mock(return_value=flows)):
            obj = Binning(tpobj)
            obj.main()
        expect = '''
(282, 'MODZ'): 2
(283, 'MODZ'): 2
(284, 'MODZ'): 1
(285, 'MODZ'): 2
        '''
        self.assertTextEqual(obj.ut_result(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_incrementcounter_with_colon(self):
        tpobj = TestProgram(f'{UT_DIR}/MTLXXXXXXX37B0ASXXX/POR_TP/Class_MTL_P28/EnvironmentFile.env')
        flows = [
            ('MODC', 'ITEMC', {}, {5: {'SetBin': 'BINY_5', 'Return': 'RETC', 'IncrementCounters': 'prefix::BINZ_5'}}),
        ]
        with MockVar(tpobj.mtpl, "iter_flows", Mock(return_value=flows)):
            obj = Binning(tpobj)
            obj.main()
        expect = '''
283 MODC ITEMC of port RETC has a SetBin: BINY and IncrementCounter: BINZ 8 digit bin that do not match
(282, 'MODC'): 1
(284, 'MODC'): 1
(285, 'MODC'): 1
        '''
        self.assertTextEqual(obj.ut_result(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_no_setbin_in_values(self):
        # Covers line 29: if 'SetBin' in values:
        tpobj = TestProgram(f'{UT_DIR}/MTLXXXXXXX37B0ASXXX/POR_TP/Class_MTL_P28/EnvironmentFile.env')
        flows = [
            ('MODN', 'ITEMN', {}, {1: {'Return': 'RET1', 'IncrementCounters': 'BIN1_1'}}),  # No 'SetBin'
        ]
        with MockVar(tpobj.mtpl, "iter_flows", Mock(return_value=flows)):
            obj = Binning(tpobj)
            obj.main()
        # Only summary lines for MODN should be present
        expect = '''

        '''
        self.assertTextEqual(obj.ut_result(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_no_incrementcounters_in_values(self):
        # Covers line 45: if 'IncrementCounters' in values:
        tpobj = TestProgram(f'{UT_DIR}/MTLXXXXXXX37B0ASXXX/POR_TP/Class_MTL_P28/EnvironmentFile.env')
        flows = [
            ('MODI', 'ITEMI', {}, {1: {'SetBin': 'BINI_1', 'Return': 'RETI'}}),  # No 'IncrementCounters'
        ]
        with MockVar(tpobj.mtpl, "iter_flows", Mock(return_value=flows)):
            obj = Binning(tpobj)
            obj.main()
        # Should pass 282, but no 283 error or pass
        expect = '''
(282, 'MODI'): 1
(284, 'MODI'): 1
(285, 'MODI'): 1
        '''
        self.assertTextEqual(obj.ut_result(), expect)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
