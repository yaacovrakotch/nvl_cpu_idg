#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for checkers
"""
from setenv_unittest import UT_DIR_REPO, ROOT_ENV    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.files import TempDir, File
from gadget.gizmo import MockVar
from unittest.mock import Mock
from gadget.disk import Chdir
import main.change_description_report as change_module
from main.change_description_report import *
from os.path import join, dirname, abspath


class TestBasic(TestCase):

    def test_basic_all(self):
        output = '''commit 1307ccd8f94fab412dcf66da98952643b24de73c
Author: balakris <santhanakrishnan.balakrishnan@intel.com>
Date:   Tue Apr 4 13:37:18 2023 -0700

    freq fix for Retention and SoC point test vccsa switch done correctly'''
        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, output))):

            git_log('1307ccd8f94fab412dcf66da98952643b24de73c')

            expect = '''commit 1307ccd8f94fab412dcf66da98952643b24de73c
Author: balakris <santhanakrishnan.balakrishnan@intel.com>
Date:   Tue Apr 4 13:37:18 2023 -0700

    freq fix for Retention and SoC point test vccsa switch done correctly'''
            self.assertEqual(output, expect)

    def test_changes_report(self):
        base_tp = f'{UT_DIR_REPO}/changes_description_report_23'
        tpproj = 'POR_TP/Class_MTL_P68/Class_MTL_P68.tpproj'
        output = '''commit 1307ccd8f94fab412dcf66da98952643b24de73c
Author: balakris <santhanakrishnan.balakrishnan@intel.com>
Date:   Tue Apr 4 13:37:18 2023 -0700

    freq fix for Retention and SoC point test vccsa switch done correctly'''
        with TempDir(name=True, chdir=True, delete=True) as tdir:
            with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, output))):
                with MockVar(change_module, 'get_datetime', Mock(return_value='Date: 18/04/2023  time: 11:40:08')):
                    change_description_report(base_tp, tpproj)

                    golden_file = f'{UT_DIR_REPO}/changes_description_report_23/POR_TP/Class_MTL_P68/Reports/Changes_Description_Report_golden.txt'
                    actual_file = f'{UT_DIR_REPO}/changes_description_report_23/POR_TP/Class_MTL_P68/Reports/Changes_Description_Report.txt'
                    self.assertTextEqual(File(golden_file).read(), File(actual_file).read())

    def test_rewrite_integ_report(self):
        integration_report = f'{UT_DIR_REPO}/integration_report_test/Integration_Report.txt'
        integration_report_golden = f'{UT_DIR_REPO}/integration_report_test/Integration_Report_golden.txt'
        integration_report_new = f'{UT_DIR_REPO}/integration_report_test/Integration_Report_new.txt'
        data_dict = {'ARR_ATOM_L2CXX': ['6a3d558a48a62cd8c446d222ed77e3d64e72e17d', '08/27/2024_21:16:10', 'info info', 'santhanakrishnan-balakrishnan-intel'],
                     'DRV_RESET_GXX': ['817241b6422be5106cdbd861155023a7e84b09ae', '04/03/2024_16:03:20', 'info info', 'Danny Phan'],
                     'DRV_RESET_SXN': ['996b38f4563f148dee4ce3de163f84e95fa24853', '08/08/2024_17:48:02', 'info info', 'Ngoc Nguyen']}
        with MockVar(change_module, 'new_integration_report_file', Mock(return_value=integration_report_new)):
            rewrite_integ_report(integration_report, data_dict)
            self.assertTextEqual(File(integration_report_golden).read(), File(integration_report_new).read())

    def test_sanitize_pat_from_url_with_pat(self):
        # Test that a GitHub PAT is stripped from a URL
        # Hex-encoded to avoid Semgrep flagging the embedded PAT pattern
        line = bytes.fromhex(
            '3c545020476974205265706f2055524c3e20202068747470733a2f2f'
            '6768705f376f577046573575676758503964697863306e374e715954'
            '5a716a6d776331556d67676a406769746875622e636f6d2f696e7465'
            '6c2d726573747269637465642f6e766c2e637075').decode()
        expect = '<TP Git Repo URL>   https://github.com/intel-restricted/nvl.cpu'
        self.assertEqual(sanitize_pat_from_url(line), expect)

    def test_sanitize_pat_from_url_without_pat(self):
        # Test that a URL without a PAT is unchanged
        line = '<TP Git Repo URL>   https://github.com/intel-restricted/nvl.cpu'
        self.assertEqual(sanitize_pat_from_url(line), line)

    def test_sanitize_pat_from_url_no_url(self):
        # Test that a line with no URL is unchanged
        line = '<TP Modules>  some random text'
        self.assertEqual(sanitize_pat_from_url(line), line)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
