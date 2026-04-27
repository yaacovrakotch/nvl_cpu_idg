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
import main.TP_release as TPrelease
from main.TP_release import *
from os.path import join, dirname, abspath


class FakeDate:

    @classmethod
    def today(cls):
        return '2023-05-15'


class TestBasic(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic_all(self):

        TP_path = f'{UT_DIR}/MTLXXXXBXH37J00S317'
        Input_file = f'{UT_DIR}/TP_release_inputFile/TP_release_note.txt'
        golden_file = f'{UT_DIR}/TP_release_inputFile/37J00_gold2.html'
        actual_file = f'{UT_DIR}/TP_release_inputFile/37J00.html'
        check_and_del(actual_file)

        handler_recipe = 'R18'
        pup_release = 'I:\\ulat\\pup\\release\\mtl\\MTLXXBXH37J0\\1006'
        with MockVar(TPrelease, 'input_release_note', Mock(return_value=Input_file)), \
                MockVar(TPrelease, 'get_TP_path', Mock(return_value=TP_path)), \
                MockVar(TPrelease, 'get_report_file', Mock(return_value=actual_file)), \
                MockVar(TPrelease, 'get_handler_re_path', Mock(return_value=handler_recipe)), \
                MockVar(TPrelease, 'get_pup_release', Mock(return_value=pup_release)), \
                MockVar(TPrelease, 'date', FakeDate):
            release_email()
        self.assertGoldEqual(actual_file, golden_file)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
