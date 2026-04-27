#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for local_aleph_dupl.py
"""
import sys

try:
    from setenv_unittest import UT_DIR_REPO, ROOT_ENV  # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR_REPO, ROOT_ENV  # must be first import for unittests

from qgates.local_aleph_dupl import *  # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from os.path import basename
from gadget.gizmo import with_
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock
import os
from pprint import pformat


class EnvCheckTest(TestCase):

    def atest_passing_case(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/SimpleNVL2/POR_TP/TGLH81/EnvironmentFile.env').init()
        obj = LocalAleph(tpobj)
        obj.main()
        # pprint(obj.result)

        # Passing case using Simple5 test program
        expect = [{'id': 251,
                   'message': 'File: FUSEREAD.patmod.json used by: FUS_FUSECFG_PXX is using a '
                   'DUPLICATE value: "MARGIN_NOM" that is used by "FUS_FUSECFG_GXX" '
                   'json file(s)  Please check if valid',
                   'module': 'FUS_FUSECFG_PXX'},
                  {'id': 251,
                   'message': 'File: FUSEREAD.patmod.json used by: FUS_FUSECFG_PXX is using a '
                   'DUPLICATE value: "MARGIN_M0" that is used by "FUS_FUSECFG_GXX" '
                   'json file(s)  Please check if valid',
                   'module': 'FUS_FUSECFG_PXX'},
                  {'id': 251,
                   'message': 'File: FUSEREAD.patmod.json used by: FUS_FUSECFG_PXX is using a '
                   'DUPLICATE value: "MARGIN_M1" that is used by "FUS_FUSECFG_GXX" '
                   'json file(s)  Please check if valid',
                   'module': 'FUS_FUSECFG_PXX'},
                  {'id': 251,
                   'message': 'File: VLD.patmod.json used by: FUS_FUSECFG_CXX is using a '
                   'DUPLICATE value: "Undervolt_CFG" that is used by '
                   '"FUS_FUSECFG_HXX" json file(s)  Please check if valid',
                   'module': 'FUS_FUSECFG_CXX'}]
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 4)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/SimpleNVL2', chdir=True, delete=True)
    def test_failing_case(self):
        os.remove('POR_TP/TGLH81/EnvironmentFile.env')
        # Mock-up failing cases Env file with ;" at end of a line.
        # Or split with "; + between values.
        File(f'{UT_DIR_REPO}/envchk_unittest/local_aleph/EnvironmentFileTestCase.env').copy('POR_TP/TGLH81/EnvironmentFile.env')
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env').init()
        obj = LocalAleph(tpobj)
        obj.main()
        # pprint(obj.result)

        expect = [{'id': 251,
                   'message': 'File: VLD.patmod.json used by: ARR2 is using a DUPLICATE value: '
                   '"Undervolt_CFG" that is used by "FUS_FUSECFG_CXX" json file(s)  '
                   'Please check if valid',
                   'module': 'ARR2'},
                  {'id': 251,
                   'message': 'File: VLD2.patmod.json used by: FUS_FUSECFG_HXX is using a '
                   'DUPLICATE value: "Undervolt_CFG" that is used by '
                   '"FUS_FUSECFG_CXX" json file(s)  Please check if valid',
                   'module': 'FUS_FUSECFG_HXX'},
                  {'id': 251,
                   'message': 'File: VLD2.patmod.json used by: FUS_FUSECFG_HXX is using a '
                   'DUPLICATE value: "HXX_Overvolt_BW" that is used by "ARR2" json '
                   'file(s)  Please check if valid',
                   'module': 'FUS_FUSECFG_HXX'},
                  {'id': 251,
                   'message': 'File: VLD2.patmod.json used by: FUS_FUSECFG_HXX is using a '
                   'DUPLICATE value: "HXX_Overvolt_CFG" that is used by "ARR2" json '
                   'file(s)  Please check if valid',
                   'module': 'FUS_FUSECFG_HXX'},
                  {'id': 251,
                   'message': 'File: VLD2.patmod.json used by: FUS_FUSECFG_HXX is using a '
                   'DUPLICATE value: "HXX_Undervolt_BW" that is used by "ARR2" json '
                   'file(s)  Please check if valid',
                   'module': 'FUS_FUSECFG_HXX'}]

        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 3)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
