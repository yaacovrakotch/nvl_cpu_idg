#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for runner_precheck.py
"""
from setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests
from main.runner_precheck import *
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.gizmo import MockVar, with_
from gadget.helperclass import CaptureStdoutLog
from gadget.files import TempDir, File
from gadget.disk import Chdir
from gadget.printmore import Dumper
from unittest.mock import Mock


class TestPreCheck(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_get_changed_files(self):
        with Chdir(f'{UT_DIR}/git_checkout_testing'):
            result = PreCheck().get_changed_files()
            self.assertEqual(result, ['main/checkers.py',
                                      'main/test/test_checkers.py',
                                      'main/test/test_torch_postproc.py',
                                      'main/torch_postproc.py'])

    @with_(TempDir, chdir=True, delete=True)
    def test_basic(self):
        # Run the whole script
        with CaptureStdoutLog() as p:
            PreCheck().main()

        # Make sure it completed successfully
        print(p.getvalue())
        self.assertIn('Runner PreCheck() complete ', p.getvalue())


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
