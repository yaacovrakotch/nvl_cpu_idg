#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for checkers
"""
from setenv_unittest import UT_DIR, UT_DIR_REPO, ROOT_ENV, EXIST_PDX_I_DRIVE    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.files import TempDir, File, check_and_del
from gadget.files import TempDir, File
from gadget.gizmo import MockVar
from unittest.mock import Mock
from gadget.disk import Chdir
import main.daily_integration_release as daily_release
from main.daily_integration_release import *
from os.path import join, dirname, abspath


class FakeDate:

    @classmethod
    def today(cls):
        return '2023-10-17'


class TestBasic(TestCase):

    def test_isGitRepo(self):
        TP_path = f'{UT_DIR_REPO}/MTLXXXXXXX39A0KSXXX'
        result = daily_release.isGitrepo(TP_path)
        self.assertEqual(result, 0)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic_all(self):
        TP_path = f'{UT_DIR}/MTLXXXXXXX39A0KSXXX'
        Input_file = f'{UT_DIR}/daily_release_inputFile/daily_release_note.txt'
        PR_report_file = f'{UT_DIR}/daily_release_inputFile/PR_report_39A0K.txt'
        golden_file = f'{UT_DIR}/daily_release_inputFile/39A0K_gold.html'
        actual_file = f'{UT_DIR}/daily_release_inputFile/39A0K.html'
        check_and_del(actual_file)

        with MockVar(daily_release, 'find_TP_Path', Mock(return_value=TP_path)), \
                MockVar(daily_release, 'get_PR_report_file', Mock(return_value=PR_report_file)), \
                MockVar(daily_release, 'setting_Tags', Mock(return_value='TP_39A0K')), \
                MockVar(daily_release, 'get_tp_report_file', Mock(return_value=actual_file)), \
                MockVar(daily_release, 'date', FakeDate):
            daily_release.release_email(Input_file)
        self.assertGoldEqual(actual_file, golden_file)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
