#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for trace_trc_torch.py
"""
from setenv_unittest import UT_DIR_REPO, ROOT_ENV     # must be first import for unittests
from main.trace_trc_torch import *
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.disk import Chdir
from gadget.gizmo import MockVar, with_
from gadget.helperclass import CaptureStdoutLog
from gadget.files import TempDir
from gadget.dictmore import keys_atlevel
from gadget.printmore import Dumper
from unittest.mock import Mock
import sys
import shutil
import os


class TestTraceTrc(TestCase):

    def test_pass_notrc(self):
        with TempDir(name=True, chdir=True) as tdir1:
            File('POR_TP/Class_MTL_M28/SubTestPlan_g.stpl').touch(mkdir=True)
            File('POR_TP/Class_MTL_M28/trc_report_19k1d.csv').touch(mkdir=True)
            with CaptureStdoutLog() as p:
                self.assertEqual(TraceTrc().main(), True)
            print(p.getvalue())
            self.assertIn('Check TRACE.', p.getvalue())
            self.assertEqual(os.listdir('POR_TP/Class_MTL_M28'), ['SubTestPlan_g.stpl'])

    def test_pass_trc(self):
        with TempDir(name=True, chdir=True) as tdir1:
            File('POR_TP/Class_MTL_M28/SubTestPlan.stpl').touch(mkdir=True)
            File('POR_TP/Class_MTL_M28/SubTestPlan_g.stpl').touch(mkdir=True)
            File(f'{UT_DIR_REPO}/trc_files/trc_report_19k1d.uniq.csv').copy('POR_TP/Class_MTL_M28')
            with CaptureStdoutLog() as p, MockVar(File, "unlink", Mock()):
                self.assertEqual(TraceTrc().main(), False)
            print(p.getvalue())
            self.assertIn('NO ERROR, TRACE TRC PASSED', p.getvalue())
            self.assertItemsEqual(os.listdir('POR_TP/Class_MTL_M28'), ['SubTestPlan_g.stpl',
                                                                       'SubTestPlan.stpl',
                                                                       'Reports'])
            self.assertItemsEqual(os.listdir('POR_TP/Class_MTL_M28/Reports'), ['trc_report_19k1d.uniq.csv',
                                                                               'FULL_TRC_Report.txt'])

    def test_pass_trc2(self):
        # No unlink mock
        with TempDir(name=True, chdir=True) as tdir1:
            File('POR_TP/Class_MTL_M28/SubTestPlan.stpl').touch(mkdir=True)
            File('POR_TP/Class_MTL_M28/SubTestPlan_g.stpl').touch(mkdir=True)
            mkdirs('POR_TP/Class_MTL_M28/Reports')
            with CaptureStdoutLog() as p:
                self.assertEqual(TraceTrc().main(), True)
            print(p.getvalue())
            self.assertItemsEqual(os.listdir('POR_TP/Class_MTL_M28'), ['SubTestPlan_g.stpl',
                                                                       'SubTestPlan.stpl',
                                                                       'Reports'])
            self.assertItemsEqual(os.listdir('POR_TP/Class_MTL_M28/Reports'), [])

    def test_fail_trc(self):
        with TempDir(name=True, chdir=True) as tdir1:
            File('POR_TP/Class_MTL_M28/SubTestPlan_g.stpl').touch(mkdir=True)
            File(f'{UT_DIR_REPO}/trc_files/trc_report_19k_raw.uniq.csv').copy('POR_TP/Class_MTL_M28')
            with MockVar(File, "unlink", Mock()):
                with self.assertRaisesRegex(ErrorUser, 'There are TRC errors'):
                    TraceTrc().main()

    def test_fail_ignore(self):
        with TempDir(name=True, chdir=True, delete=True) as tdir1:
            File('POR_TP/Class_MTL_M28/SubTestPlan_g.stpl').touch(mkdir=True)
            File(f'{UT_DIR_REPO}/trc_files/trc_report_19k_raw.uniq.csv').copy('POR_TP/Class_MTL_M28/ignore_trc.csv')
            File(f'{UT_DIR_REPO}/trc_files/trc_report_19k_raw.uniq.csv').copy('POR_TP/Class_MTL_M28')
            with MockVar(File, "unlink", Mock()):
                TraceTrc().main()    # There should be no fails

    def test_ut_passfail(self):
        with TempDir(name=True, chdir=True):
            text = """Scrum,Module,Bom Groups,Category,Description,Details
FUN,FUN_ATOM_CXX,SubTestPlan,Bin 69 - The Module fails units without a bad bin assignment,Bin 69
FUN,FUN_ATOM_CXX,SubTestPlan,Module name does not follow the naming conventions
Base,,SubTestPlan,VCC - Pins found that are defined but NEVER tested
QNR,QNR_CARV_XXX,SubTestPlan,XML file is missing XSD schema definition,XML file
SCN,SCN_ATOM_CXX,SubTestPlan,Random error skip
            """
            text2 = """Scrum,Module,Bom Groups,Category,Description,Details
SCN,SCN_ATOM_CXX,SubTestPlan,Random error skip
            """
            File('POR_TP/Class_MTL_M28/SubTestPlan_g.stpl').touch(mkdir=True)
            File('POR_TP/Class_MTL_M28/trc_report_SubTestPlan_g.stpl').touch(text)
            File('POR_TP/Class_MTL_M28/ignore_trc.csv').touch(text2)
            obj = TraceTrc()
            with MockVar(obj, '_final_exit', Mock()):
                obj.trcout_check('POR_TP/Class_MTL_M28/trc_report_SubTestPlan_g.stpl')
            self.assertEqual(obj.wep_count, {'w': 2, 'e': 1, 'p': 0})


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
