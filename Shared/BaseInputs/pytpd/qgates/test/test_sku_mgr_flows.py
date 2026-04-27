#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Run unittest for sku_mgr_flows.py
AI assisted using GitHUB CoPilot
"""
import sys
try:
    from setenv_unittest import UT_DIR, ROOT_ENV     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR, ROOT_ENV     # must be first import for unittests

from qgates.sku_mgr_flows import *
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from unittest.mock import MagicMock, mock_open
import os


class TestSkuMgrChk(TestCase):
    def setUp(self):
        tpobj = MagicMock()
        tpobj.envdir = '/path/to/envdir'
        tpobj.tpldir = '/path/to/tpldir'
        tpobj.mtpl.get_mod2fname.return_value = {
            'mod1': '/fake/file1',
            'mod2': '/fake/file2'
        }
        self.sku_mgr = SkuMgrChk(tpobj)
        self.sku_mgr.tpobj = tpobj
        self.sku_mgr.add_pass = MagicMock()
        self.sku_mgr.add_error = MagicMock()
        self.corners_content = [
            'UserVars Corners',
            'Array<String> AT_C5 = ["F7","F6","F5"];',
            '}'
        ]
        self.correct_module_content = [
            'MultiTrialTest ARR_ATOM_VMIN_K_F5XAT_HITO_VCCIA_F5_X_COMBINED',
            'TrialVariable IPC::CPU_TRIALS::FlowDomain.ATOM_TOP;',
            'CSharpTrialTest VminTC "ARR_ATOM_VMIN_K_F5XAT_HITO_VCCIA_F5_" + __shared__::Corners.AT_C5 + "_COMBINED"'
        ]
        self.wrong_module_content = [
            'MultiTrialTest ARR_ATOM_VMIN_K_F5XAT_HITO_VCCIA_F5_X_COMBINED',
            'TrialVariable IPC::CPU_TRIALS::FlowDomain.ATOM;',
            'CSharpTrialTest VminTC "ARR_ATOM_VMIN_K_F5XAT_HITO_VCCIA_F5_" + __shared__::Corners.AT_C5 + "_COMBINED"'
        ]
        self.lowfreq_top_content = [
            'MultiTrialTest ARR_ATOM_VMIN_K_F1XAT_HITO_VCCIA_F1_X_COMBINED',
            'TrialVariable IPC::CPU_TRIALS::FlowDomain.ATOM_TOP;',
            'CSharpTrialTest VminTC "ARR_ATOM_VMIN_K_F1XAT_HITO_VCCIA_F1_" + __shared__::CustomFlowMatrixSpecs.AT_F1_FREQ_MHz + "_COMBINED"'
        ]
        self.wrong_freq_content = [
            'MultiTrialTest ARR_ATOM_VMIN_K_F8XAT_HITO_VCCIA_F8_X_COMBINED',
            'TrialVariable IPC::CPU_TRIALS::FlowDomain.ATOM_TOP;',
            'CSharpTrialTest VminTC "ARR_ATOM_VMIN_K_F8XAT_HITO_VCCIA_F8_" + __shared__::Corners.AT_C5 + "_COMBINED"'
        ]
        self.module_content = self.correct_module_content

    def _mocked_open(self, file, *args, **kwargs):
        if file.endswith('BinMatrixSpecs.flm.usrv'):
            content = self.corners_content
        elif file in ['/fake/file1', '/fake/file2']:
            content = self.module_content
        else:
            raise FileNotFoundError(file)
        m = mock_open(read_data='\n'.join(content)).return_value
        m.__iter__ = lambda *a, **k: iter(content)
        return m

    def test_main_calls_add_pass_for_correct_combo(self):
        self.module_content = self.correct_module_content
        with MockVar(os.path, 'isfile', lambda f: True), \
                MockVar(__import__('builtins'), 'open', self._mocked_open):
            self.sku_mgr.main()
        self.sku_mgr.add_pass.assert_any_call(263, 'mod1')
        self.sku_mgr.add_pass.assert_any_call(263, 'mod2')
        self.sku_mgr.add_error.assert_not_called()

    def test_main_calls_add_error_for_wrong_freq(self):
        self.module_content = self.wrong_freq_content
        with MockVar(os.path, 'isfile', lambda f: True), \
                MockVar(__import__('builtins'), 'open', self._mocked_open):
            self.sku_mgr.main()
        self.sku_mgr.add_error.assert_any_call(
            264, 'mod1', 'ARR_ATOM_VMIN_K_F8XAT_HITO_VCCIA_F8_X_COMBINED is using a wrong/nonexistent frequency "_F8_" but using Corners.AT_C5. Valid Freq: [\'F7\', \'F6\', \'F5\']'
        )

    def test_main_calls_add_error_for_lowfreq_top(self):
        self.module_content = self.lowfreq_top_content
        with MockVar(os.path, 'isfile', lambda f: True), \
                MockVar(__import__('builtins'), 'open', self._mocked_open):
            self.sku_mgr.main()
        self.sku_mgr.add_error.assert_any_call(
            264, 'mod1', '"ARR_ATOM_VMIN_K_F1XAT_HITO_VCCIA_F1_X_COMBINED" should NOT be using _TOP in FlowDomain when not using any collection from BinMatrixSpecs.flm.usrv'
        )

    def test_parse_corners_file_not_exist(self):
        with MockVar(os.path, 'isfile', lambda f: False):
            result = self.sku_mgr._parse_corners()
            self.assertIsNone(result)

    def test_parse_corners_skips_empty_lines(self):
        self.corners_content = [
            '',  # empty line
            'UserVars Corners',
            'Array<String> AT_C5 = ["F7","F6","F5"];',
            '}'
        ]
        with MockVar(os.path, 'isfile', lambda f: True), \
                MockVar(__import__('builtins'), 'open', self._mocked_open):
            result = self.sku_mgr._parse_corners()
        self.assertIn('AT_C5', result)
        self.assertEqual(result['AT_C5'], ['F7', 'F6', 'F5'])

    def test_parse_corners_skips_manual_block(self):
        self.corners_content = [
            'UserVars CustomFlowMatrixSpecsManual',
            'Array<String> IGNORED = ["X"];',
            '}',
            'UserVars Corners',
            'Array<String> AT_C5 = ["F7","F6","F5"];',
            '}'
        ]
        with MockVar(os.path, 'isfile', lambda f: True), \
                MockVar(__import__('builtins'), 'open', self._mocked_open):
            result = self.sku_mgr._parse_corners()
        self.assertIn('AT_C5', result)
        self.assertNotIn('IGNORED', result)

    def test_parse_corners_skips_lines_within_manual_block(self):
        self.corners_content = [
            'UserVars CustomFlowMatrixSpecsManual',
            'Array<String> IGNORED = ["X"];',
            '}',
            'UserVars Corners',
            'Array<String> AT_C5 = ["F7","F6","F5"];',
            '}'
        ]
        with MockVar(os.path, 'isfile', lambda f: True), \
                MockVar(__import__('builtins'), 'open', self._mocked_open):
            result = self.sku_mgr._parse_corners()
        self.assertIn('AT_C5', result)
        self.assertNotIn('IGNORED', result)

    def test_parse_corners_skips_unexpected_format(self):
        self.corners_content = [
            'UserVars Corners',
            'Array<String> AT_C5 ["F7","F6","F5"];',  # missing '='
            '}'
        ]
        with MockVar(os.path, 'isfile', lambda f: True), \
                MockVar(__import__('builtins'), 'open', self._mocked_open), \
                MockVar(__import__('builtins'), 'print', MagicMock()) as mock_print:
            result = self.sku_mgr._parse_corners()
            mock_print.assert_called()
        self.assertNotIn('AT_C5', result)

    def test_parse_corners_returns_domains(self):
        self.corners_content = [
            'UserVars Corners',
            'Array<String> AT_C5 = ["F7","F6","F5"];',
            '}'
        ]
        with MockVar(os.path, 'isfile', lambda f: True), \
                MockVar(__import__('builtins'), 'open', self._mocked_open):
            result = self.sku_mgr._parse_corners()
        self.assertIsInstance(result, dict)
        self.assertIn('AT_C5', result)

    def test_main_flowmatrix_not_exist(self):
        with MockVar(os.path, 'isfile', lambda f: False):
            self.sku_mgr.main()
        self.sku_mgr.add_error.assert_called()

    def test_validate_test_lowfreq_top(self):
        self.sku_mgr.add_pass.reset_mock()
        self.sku_mgr.add_error.reset_mock()
        self.sku_mgr._validate_test(
            mod_path='mod1',
            tname='ARR_ATOM_VMIN_K_F1XAT_HITO_VCCIA_F1_X_COMBINED',
            tnamefreq='F1XAT',
            flowdomain='ATOM_TOP',
            param='CSharpTrialTest VminTC "ARR_ATOM_VMIN_K_F1XAT_HITO_VCCIA_F1_" + __shared__::CustomFlowMatrixSpecs.AT_F1_FREQ_MHz + "_COMBINED"',
            crnfid=None,
            domains={}
        )
        self.sku_mgr.add_error.assert_called_once_with(
            264, 'mod1', '"ARR_ATOM_VMIN_K_F1XAT_HITO_VCCIA_F1_X_COMBINED" should NOT be using _TOP in FlowDomain when not using any collection from BinMatrixSpecs.flm.usrv'
        )
        self.sku_mgr.add_pass.assert_not_called()

    def test_validate_test_lowfreq_no_top(self):
        self.sku_mgr.add_pass.reset_mock()
        self.sku_mgr.add_error.reset_mock()
        self.sku_mgr._validate_test(
            mod_path='mod1',
            tname='ARR_ATOM_VMIN_K_F1XAT_HITO_VCCIA_F1_X_COMBINED',
            tnamefreq='F1XAT',
            flowdomain='ATOM',
            param='CSharpTrialTest VminTC "ARR_ATOM_VMIN_K_F1XAT_HITO_VCCIA_F1_" + __shared__::CustomFlowMatrixSpecs.AT_F1_FREQ_MHz + "_COMBINED"',
            crnfid=None,
            domains={}
        )
        self.sku_mgr.add_pass.assert_called_once_with(264, 'mod1')
        self.sku_mgr.add_error.assert_not_called()

    def test_validate_test_top_freq_no_corners_no_top(self):
        self.sku_mgr.add_pass.reset_mock()
        self.sku_mgr.add_error.reset_mock()
        domains = {'AT_C5': ['F7', 'F6', 'F5']}
        self.sku_mgr._validate_test(
            mod_path='mod1',
            tname='ARR_ATOM_VMIN_K_F5XAT_HITO_VCCIA_F5_X_COMBINED',
            tnamefreq='F5',
            flowdomain='ATOM',
            param='CSharpTrialTest VminTC "ARR_ATOM_VMIN_K_F5XAT_HITO_VCCIA_F5_" + __shared__::CustomFlowMatrixSpecs.AT_F5_FREQ_MHz + "_COMBINED"',
            crnfid='AT_C5',
            domains=domains
        )
        self.sku_mgr.add_pass.assert_called_once_with(263, 'mod1')
        self.sku_mgr.add_error.assert_not_called()

    def test_validate_test_wrong_freq_add_pass(self):
        self.sku_mgr.add_pass.reset_mock()
        self.sku_mgr.add_error.reset_mock()
        domains = {'AT_C5': ['F7', 'F6', 'F5']}
        self.sku_mgr._validate_test(
            mod_path='mod1',
            tname='ARR_ATOM_VMIN_K_HITO_VCCIA_X_COMBINED',
            tnamefreq=None,
            flowdomain='ATOM_TOP',
            param='CSharpTrialTest VminTC "ARR_ATOM_VMIN_K_HITO_VCCIA_X_" + __shared__::Corners.AT_C5 + "_COMBINED"',
            crnfid='AT_C5',
            domains=domains
        )
        self.sku_mgr.add_pass.assert_called_once_with(264, 'mod1')
        self.sku_mgr.add_error.assert_not_called()

        self.sku_mgr.add_pass.reset_mock()
        self.sku_mgr.add_error.reset_mock()
        self.sku_mgr._validate_test(
            mod_path='mod1',
            tname='ARR_ATOM_VMIN_K_VMAX_HITO_VCCIA_X_COMBINED',
            tnamefreq='VMAX',
            flowdomain='ATOM_TOP',
            param='CSharpTrialTest VminTC "ARR_ATOM_VMIN_K_VMAX_HITO_VCCIA_X_" + __shared__::Corners.AT_C5 + "_COMBINED"',
            crnfid='AT_C5',
            domains=domains
        )
        self.sku_mgr.add_pass.assert_called_once_with(264, 'mod1')
        self.sku_mgr.add_error.assert_not_called()

    def test_validate_test_top_freq_else_branch(self):
        self.sku_mgr.add_pass.reset_mock()
        self.sku_mgr.add_error.reset_mock()
        domains = {'AT_C5': ['F7', 'F6', 'F5']}
        self.sku_mgr._validate_test(
            mod_path='mod1',
            tname='ARR_ATOM_VMIN_K_F5XAT_HITO_VCCIA_F5_X_COMBINED',
            tnamefreq='F5',
            flowdomain='ATOM',  # No _TOP
            param='CSharpTrialTest VminTC "ARR_ATOM_VMIN_K_F5XAT_HITO_VCCIA_F5_" + __shared__::CustomFlowMatrixSpecs.AT_F5_FREQ_MHz + "_COMBINED"',
            crnfid='AT_C5',
            domains=domains
        )
        found = False
        for call in self.sku_mgr.add_pass.call_args_list:
            args = call[0]
            if args[0] == 263 and args[1] == 'mod1':
                found = True
                break
        self.assertTrue(found, "Expected add_pass(263, 'mod1') call not found")
        self.sku_mgr.add_error.assert_not_called()

    def test_validate_test_top_freq_add_error(self):
        self.sku_mgr.add_pass.reset_mock()
        self.sku_mgr.add_error.reset_mock()
        domains = {'AT_C5': ['F7', 'F6', 'F5']}
        self.sku_mgr._validate_test(
            mod_path='mod1',
            tname='ARR_ATOM_VMIN_K_F5XAT_HITO_VCCIA_F5_X_COMBINED',
            tnamefreq='F5',
            flowdomain='ATOM',  # No _TOP
            param='CSharpTrialTest VminTC "ARR_ATOM_VMIN_K_F5XAT_HITO_VCCIA_F5_" + __shared__::Corners.AT_C5 + "_COMBINED"',
            crnfid='AT_C5',
            domains=domains
        )
        self.sku_mgr.add_error.assert_called_once_with(
            263, 'mod1',
            'TOP Freq test: ARR_ATOM_VMIN_K_F5XAT_HITO_VCCIA_F5_X_COMBINED is not using the correct _TOP FlowDomain and BinMatrixSpecs.flm.usrv Collection combo'
        )
        self.sku_mgr.add_pass.assert_not_called()


if __name__ == '__main__':
    unittest.main()
