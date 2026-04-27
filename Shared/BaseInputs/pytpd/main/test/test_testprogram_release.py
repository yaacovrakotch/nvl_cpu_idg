#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for checkers
"""
from setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.files import TempDir, File, check_and_del
from gadget.gizmo import MockVar
from unittest.mock import Mock
from gadget.disk import Chdir
from main.testprogram_release import *
import main.testprogram_release as TPrelease
from os.path import join, dirname, abspath
import sys
from unittest.mock import patch


class FakeDate:

    @classmethod
    def today(cls):
        return '2024-01-09'


class TestBasic(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_prod_release_all(self):
        with MockVar(sys, 'argv', ['testprogram_release.py', '-script', 'prod', '-path', f'{UT_DIR}/testprogram_release/testprogram_release_notes.txt']):
            TP_path = f'{UT_DIR}/testprogram_release/MTLXXXXC1H39C00S347'
            Input_file = f'{UT_DIR}/testprogram_release/testprogram_release_notes.txt'
            golden_file = f'{UT_DIR}/testprogram_release/39C00_gold1.html'
            actual_file = f'{UT_DIR}/testprogram_release/39C00.html'
            list_pr_reports = [f'{UT_DIR}/testprogram_release/PR_reports/39C00.txt',
                               f'{UT_DIR}/testprogram_release/PR_reports/39C0A.txt',
                               f'{UT_DIR}/testprogram_release/PR_reports/39C0B.txt',
                               f'{UT_DIR}/testprogram_release/PR_reports/39C0C.txt',
                               f'{UT_DIR}/testprogram_release/PR_reports/39C0D.txt']
            check_and_del(actual_file)
            handler_recipe = 'R31'
            pup_release = 'I:\\ulat\\pup\\release\\mtl\\MTLXXC1H39C00\\1000'
            with MockVar(TPrelease, 'get_TP_Path', Mock(return_value=TP_path)), \
                    MockVar(TPrelease, 'get_report_file', Mock(return_value=actual_file)), \
                    MockVar(TPrelease, 'get_handler_re_path', Mock(return_value=handler_recipe)), \
                    MockVar(TPrelease, 'get_pup_release', Mock(return_value=pup_release)), \
                    MockVar(TPrelease, 'setting_Tags', Mock(return_value='TP_39C00')), \
                    MockVar(TPrelease, 'get_list_PR_report', Mock(return_value=list_pr_reports)), \
                    MockVar(TPrelease, 'date', FakeDate):
                prod_release_email(Input_file)
            self.assertGoldEqual(actual_file, golden_file)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_daily_release_all(self):
        with MockVar(sys, 'argv', ['testprogram_release.py', '-script', 'daily', '-path', f'{UT_DIR}/testprogram_release/testprogram_release_notes_1.txt']):
            TP_path = f'{UT_DIR}/testprogram_release/MTLXXXXXXX39C0ASXXX'
            Input_file = f'{UT_DIR}/testprogram_release/testprogram_release_notes_1.txt'
            golden_file = f'{UT_DIR}/testprogram_release/39C0A_gold.html'
            actual_file = f'{UT_DIR}/testprogram_release/39C0A.html'
            pr_reports = f'{UT_DIR}/testprogram_release/PR_reports/39C0A.txt'
            check_and_del(actual_file)
            handler_recipe = 'R31'
            pup_release = 'I:\\ulat\\pup\\release\\mtl\\MTLXXC1H39C0A\\1000'
            with MockVar(TPrelease, 'get_TP_Path', Mock(return_value=TP_path)), \
                    MockVar(TPrelease, 'get_daily_report_file', Mock(return_value=actual_file)), \
                    MockVar(TPrelease, 'get_handler_re_path', Mock(return_value=handler_recipe)), \
                    MockVar(TPrelease, 'get_pup_release', Mock(return_value=pup_release)), \
                    MockVar(TPrelease, 'setting_Tags', Mock(return_value='TP_39C0A')), \
                    MockVar(TPrelease, 'get_PR_report_file', Mock(return_value=pr_reports)), \
                    MockVar(TPrelease, 'date', FakeDate):
                daily_release_email(Input_file)
            self.assertGoldEqual(actual_file, golden_file)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
