#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for basenum_range.py
CoPilot Assisted

"""
import sys
try:
    from setenv_unittest import UT_DIR_REPO, ROOT_ENV     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest/')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR_REPO, ROOT_ENV     # must be first import for unittests

from qgates.basenum_range import *        # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock, patch, MagicMock


class TestBaseNumRange(TestCase):

    def test_basic(self):
        # Passing case - vminTC, with TestMode not Functional, and valid basenumber
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple4d/POR_TP/TGLH81/EnvironmentFile.env').init()
        # print(f'{UT_DIR_REPO}')
        data = [('SCN_CCF_C68', 'Test6', {'TEMPLATE': 'VminTC', 'BaseNumbers': '13555', 'TestMode': 'SingleVmin'},
                 {999: 'SBFT_ATOM_VMIN_K_LTTCSOC_X_VCCSA_F3_2500_L2DRAGON_1507'})]

        with MockVar(tpobj.mtpl, "iter_flows", Mock(return_value=data)):
            obj = BaseNumRange(tpobj)
            obj.main()
            self.assertEqual(obj.result, [])                     # expected errors added - should be none
            self.assertEqual(obj.passed, {(246, 'SCN_CCF_C68'): 1, (245, 'SCN_CCF_C68'): 1})

        # Failing case - basenumber out of range for module
        bad_basenum_data = [('SCN_CCF_C68', 'Test6', {'TEMPLATE': 'VminTC', 'BaseNumbers': '14555', 'TestMode': 'SingleVmin'},
                             {999: 'SBFT_ATOM_VMIN_K_LTTCSOC_X_VCCSA_F3_2500_L2DRAGON_1507'})]

        with MockVar(tpobj.mtpl, "iter_flows", Mock(return_value=bad_basenum_data)):
            obj = BaseNumRange(tpobj)
            obj.main()
            self.assertEqual(obj.result, [{'message': 'Base#:14555 is not in the expected range range(13000, 14000)',
                                           'id': 245,
                                           'module': 'SCN_CCF_C68'}])

        # Failing Case - basenumber in range, but VminTC template with TestMode of Functional
        bad_basenum_data = [('SCN_CCF_C68', 'Test6', {'TEMPLATE': 'VminTC', 'BaseNumbers': '13555', 'TestMode': 'Functional'},
                             {999: 'SBFT_ATOM_VMIN_K_LTTCSOC_X_VCCSA_F3_2500_L2DRAGON_1507'})]

        with MockVar(tpobj.mtpl, "iter_flows", Mock(return_value=bad_basenum_data)):
            obj = BaseNumRange(tpobj)
            obj.main()
            self.assertEqual(obj.result, [{'message': 'Base#: SCN_CCF_C68 Test:Test6 with VminTC template is not allowed to have a basenumber and have Functional TestMode',
                                           'id': 246,
                                           'module': 'SCN_CCF_C68'}])

    def test_PCD(self):
        # Passing case - vminTC, with TestMode not Functional, and valid basenumber
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple4d/POR_TP/TGLH81/EnvironmentFile.env').init()
        # print(f'{UT_DIR_REPO}')
        data = [('SCN_CCF_P68', 'Test6', {'TEMPLATE': 'VminTC', 'BaseNumbers': '38555', 'TestMode': 'SingleVmin'},
                 {999: 'SBFT_ATOM_VMIN_K_LTTCSOC_X_VCCSA_F3_2500_L2DRAGON_1507'}),
                ('SCN_CCF_C68', 'Test6', {'TEMPLATE': 'VminTC', 'BaseNumbers': '13555', 'TestMode': 'SingleVmin'},
                 {999: 'SBFT_ATOM_VMIN_K_LTTCSOC_X_VCCSA_F3_2500_L2DRAGON_1507'})
                ]
        expect = []

        with MockVar(tpobj.mtpl, "iter_flows", Mock(return_value=data)):
            obj = BaseNumRange(tpobj)
            obj.main()

        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 3)

# NEW LINES
    @patch("glob.glob", return_value=[])
    def test_config_file_missing(self, mock_glob):
        tpobj = MagicMock()
        tpobj.tpldir = "nonexistent_dir"
        tpobj.mtpl.iter_flows = MagicMock(return_value=[])
        obj = BaseNumRange(tpobj)
        obj.main()
        self.assertTrue(any('does not exist' in r.get('message', '') for r in obj.result))

    @patch("glob.glob", return_value=['file1.json', 'file2.json'])
    def test_config_file_multiple(self, mock_glob):
        tpobj = MagicMock()
        tpobj.tpldir = "some_dir"
        tpobj.mtpl.iter_flows = MagicMock(return_value=[])
        obj = BaseNumRange(tpobj)
        obj.main()
        self.assertTrue(any('multiple configs' in r.get('message', '') for r in obj.result))

    @patch("glob.glob", return_value=['fake_path/basenum_ranges.json'])
    @patch("builtins.open", new_callable=MagicMock)
    @patch("json.load", return_value={'MOD2': {'start': 10000, 'end': 20000}})
    def test_module_not_in_expected_range(self, mock_json, mock_open, mock_glob):
        tpobj = MagicMock()
        tpobj.tpldir = "some_dir"
        tpobj.mtpl.iter_flows = MagicMock(return_value=[
            ('MOD1', 'TestNotInRange', {'TEMPLATE': 'VminTC', 'ScoreboardBaseNumber': '12345'}, {999: 'SBFT'}),
        ])
        obj = BaseNumRange(tpobj)
        obj.main()
        self.assertTrue(any('no defined valid range' in r.get('message', '') for r in obj.result))

    @patch("glob.glob", return_value=['fake_path/basenum_ranges.json'])
    @patch("builtins.open", new_callable=MagicMock)
    @patch("json.load", return_value={'MOD1': {'start': 10000, 'end': 20000}})
    def test_skip_concurrent_traces_vmintc(self, mock_json, mock_open, mock_glob):
        tpobj = MagicMock()
        tpobj.tpldir = "some_dir"
        tpobj.mtpl.iter_flows = MagicMock(return_value=[
            ('MOD1', 'TestConcurrent', {'TEMPLATE': 'ConcurrentTracesVminTC', 'ScoreboardBaseNumber': '12345'},
             {999: 'SBFT'}),
        ])
        obj = BaseNumRange(tpobj)
        obj.main()
        self.assertTrue(all('TestConcurrent' not in r.get('message', '') for r in obj.result))

    @patch("glob.glob", return_value=['fake_path/basenum_ranges.json'])
    @patch("builtins.open", new_callable=MagicMock)
    @patch("json.load", return_value={'MOD1': {'start': 10000, 'end': 20000}})
    def test_skip_no_base_number(self, mock_json, mock_open, mock_glob):
        tpobj = MagicMock()
        tpobj.tpldir = "some_dir"
        tpobj.mtpl.iter_flows = MagicMock(return_value=[
            ('MOD1', 'TestNoBase', {'TEMPLATE': 'VminTC'}, {999: 'SBFT'}),
        ])
        obj = BaseNumRange(tpobj)
        obj.main()
        self.assertTrue(all('TestNoBase' not in r.get('message', '') for r in obj.result))

    @patch("glob.glob", return_value=['fake_path/basenum_ranges.json'])
    @patch("builtins.open", new_callable=MagicMock)
    @patch("json.load", return_value={'MOD1': {'start': 10000, 'end': 20000}})
    def test_skip_base_number_zero(self, mock_json, mock_open, mock_glob):
        tpobj = MagicMock()
        tpobj.tpldir = "some_dir"
        tpobj.mtpl.iter_flows = MagicMock(return_value=[
            ('MOD1', 'TestZeroBase', {'TEMPLATE': 'VminTC', 'ScoreboardBaseNumber': '0'}, {999: 'SBFT'}),
        ])
        obj = BaseNumRange(tpobj)
        obj.main()
        self.assertTrue(all('TestZeroBase' not in r.get('message', '') for r in obj.result))

    @patch("glob.glob", return_value=['fake_path/basenum_ranges.json'])
    @patch("builtins.open", new_callable=MagicMock)
    @patch("json.load", return_value={'MOD1': {'start': 10000, 'end': 20000}})
    def test_testname_freq_flowindex_renaming(self, mock_json, mock_open, mock_glob):
        tpobj = MagicMock()
        tpobj.tpldir = "some_dir"
        tpobj.bin_matrix = MagicMock(return_value=['FLOWINDEX'])
        tpobj.get_bom = MagicMock(return_value=None)

        class MockMatch:
            def group(self, idx):
                return f"g{idx}"

        import qgates.basenum_range
        qgates.basenum_range.cfg['ti_name3'] = MagicMock()
        qgates.basenum_range.cfg['ti_name3'].search = MagicMock(return_value=MockMatch())
        tpobj.mtpl.iter_flows = MagicMock(return_value=[
            ('MOD1', 'TEST_FLOWINDEX', {'TEMPLATE': 'VminTC', 'ScoreboardBaseNumber': '12345'}, {999: 'SBFT'}),
        ])
        obj = BaseNumRange(tpobj)
        obj.main()
        self.assertTrue(True)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
