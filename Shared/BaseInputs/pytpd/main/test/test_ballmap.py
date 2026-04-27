#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for ballmap.py
"""
from setenv_unittest import UT_DIR_REPO    # must be first import for unittests
from main.ballmap import *
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.gizmo import MockVar, with_
from gadget.helperclass import CaptureStdout
from gadget.files import TempDir
import sys
import main.ballmap as ballmap


class BMTest(TestCase):

    def test_basic(self):

        # execute
        udir = f'{UT_DIR_REPO}/ballmap_ut'
        cmd = f"ballmap.py -p {udir}/mtl_pindef_p28.csv -c {udir}/MTLP682_ConnectivityMatrixReport.csv"
        with MockVar(sys, "argv", cmd.split()):
            with CaptureStdout() as p:
                print()
                MainArg().main()
        print(p.getvalue())
        for item in ('-i- Exact match found: 606 of 855',
                     '-i- w/o underscore: 37, Total exact match found: 643 of 855',
                     '-i- counts pindef=855, final=830'):

            assert item in p.getvalue(), f'"{item}" is not found in output'

    def test_noarg(self):
        cmd = "ballmap.py"
        with MockVar(sys, "argv", cmd.split()), CaptureStdout() as p:
            with self.assertRaises(SystemExit):
                MainArg().main()
            self.assertIn('usage: ballmap.py', p.getvalue())


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
