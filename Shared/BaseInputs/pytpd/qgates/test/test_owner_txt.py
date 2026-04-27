#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for owner_txt.py

"""
import sys
try:
    from setenv_unittest import UT_DIR, UT_DIR_REPO, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR, UT_DIR_REPO, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests
from qgates.owner_txt import *        # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from gadget.gizmo import with_
from unittest.mock import Mock


class TestOwnerTxt(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR}/Simple5', chdir=True, delete=True)
    def test_folder(self):
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')
        data1 = {'ARR1': 'ARR',   # pass1
                 'SCN1': 'SCN',   # pass2
                 'PTH1': 'PTH',   # fail
                 'QQQ1': 'QQQ'    # ignore
                 }
        data2 = {'SCN': '/blah/Modules/SCN/SCN1/a.mtpl',
                 'ARR': '\\blah\\Modules\\ARR\\ARR1\\b.mtpl',
                 'PTH': '/blah/Modules/PTH/a.mtpl',
                 'QQQ': '/blah/Common/a.mtpl',
                 }

        with MockVar(tpobj.mtpl, 'get_modfolder2mod', Mock(return_value=data1)), \
                MockVar(tpobj.mtpl, 'get_mod2fname', Mock(return_value=data2)):
            obj = OwnerTxt(tpobj, frompr=True)
            obj.main()
        expect = '''
261 PTH Modules/PTH/a.mtpl does not follow Module .mtpl structure. Expecting: Modules/<team>/<modulefolder>/<file>.mtpl
259 ARR1 owner.txt does not exist. This is required, see: https://wiki.ith.intel.com/x/ZRfT_
259 SCN1 SCN1/owner.txt does not exist. This is required, see: https://wiki.ith.intel.com/x/ZRfT_
259 PTH1 PTH/owner.txt does not exist. This is required, see: https://wiki.ith.intel.com/x/ZRfT_
(261, 'ARR'): 1
(261, 'SCN'): 1
'''
        self.assertTextEqual(obj.ut_result(), expect)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple5', chdir=True, delete=True)
    def test_basic(self):
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')

        # ARR - missing owner.txt
        # SCN - incorrect owner and manager
        # PTH - missing manager
        # TPI_FLWFLGS - wrong location
        File('Modules/SCN/owner.txt').touch('owner: a b\nmanager: b,c', mkdir=True)
        File('Modules/PTH/owner.txt').touch('owner: a', mkdir=True)
        File('Modules/TPI_FLWFLGS_XXX/InputFiles/owner.txt').touch('owner: a\nmanager: b', mkdir=True)
        File('Modules/TPI_DIESLCT_XXX/owner.txt').touch('\n# blah\n\nowner: a\nmanager: b\n', mkdir=True)
        obj = OwnerTxt(tpobj, frompr=True)
        obj.main()

        expect = '''
261 ARR Modules/ARR/array.mtpl does not follow Module .mtpl structure. Expecting: Modules/<team>/<modulefolder>/<file>.mtpl
261 PTH Modules/PTH/pth.mtpl does not follow Module .mtpl structure. Expecting: Modules/<team>/<modulefolder>/<file>.mtpl
261 SCN Modules/SCN/scan.mtpl does not follow Module .mtpl structure. Expecting: Modules/<team>/<modulefolder>/<file>.mtpl
261 TPI_DIESLCT_XXX Modules/TPI_DIESLCT_XXX/TPI_DIESLCT_XXX.mtpl does not follow Module .mtpl structure. Expecting: Modules/<team>/<modulefolder>/<file>.mtpl
261 TPI_FLWFLGS_XXX Modules/TPI_FLWFLGS_XXX/TPI_FLWFLGS_XXX.mtpl does not follow Module .mtpl structure. Expecting: Modules/<team>/<modulefolder>/<file>.mtpl
259 ARR ARR/owner.txt does not exist. This is required, see: https://wiki.ith.intel.com/x/ZRfT_
259 SCN SCN/owner.txt has invalid line: [owner: a b]. Expecting "(owner|manager): <idsid>". One only. See: https://wiki.ith.intel.com/x/ZRfT_
259 SCN SCN/owner.txt has invalid line: [manager: b,c]. Expecting "(owner|manager): <idsid>". One only. See: https://wiki.ith.intel.com/x/ZRfT_
259 SCN SCN/owner.txt is missing: ['manager', 'owner'] keyword. See https://wiki.ith.intel.com/x/ZRfT_
259 PTH PTH/owner.txt is missing: ['manager'] keyword. See https://wiki.ith.intel.com/x/ZRfT_
259 TPI_FLWFLGS_XXX Pls move TPI_FLWFLGS_XXX/InputFiles/owner.txt to TPI_FLWFLGS_XXX/owner.txt; Reason: InputFiles/ are files meant to be loaded on tester.
(259, 'PTH'): 2
(259, 'TPI_DIESLCT_XXX'): 5
'''
        self.assertTextEqual(obj.ut_result(), expect)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple5', chdir=True, delete=True)
    def test_pass_case(self):
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')

        # ARR - pass case members
        # SCN - pass case normal
        File('Modules/ARR/owner.txt').touch('owner: bl ah Members\nmanager: b', mkdir=True)
        File('Modules/SCN/owner.txt').touch('owner: a\nmanager: b', mkdir=True)
        File('Modules/PTH/owner.txt').touch('owner: blah Members\nowner: someone\nmanager: b', mkdir=True)
        obj = OwnerTxt(tpobj, frompr=True)
        obj.main()

        expect = '''
261 ARR Modules/ARR/array.mtpl does not follow Module .mtpl structure. Expecting: Modules/<team>/<modulefolder>/<file>.mtpl
261 PTH Modules/PTH/pth.mtpl does not follow Module .mtpl structure. Expecting: Modules/<team>/<modulefolder>/<file>.mtpl
261 SCN Modules/SCN/scan.mtpl does not follow Module .mtpl structure. Expecting: Modules/<team>/<modulefolder>/<file>.mtpl
261 TPI_DIESLCT_XXX Modules/TPI_DIESLCT_XXX/TPI_DIESLCT_XXX.mtpl does not follow Module .mtpl structure. Expecting: Modules/<team>/<modulefolder>/<file>.mtpl
261 TPI_FLWFLGS_XXX Modules/TPI_FLWFLGS_XXX/TPI_FLWFLGS_XXX.mtpl does not follow Module .mtpl structure. Expecting: Modules/<team>/<modulefolder>/<file>.mtpl
259 PTH PTH/owner.txt has multiple owner. Expecting 1 only.
259 TPI_FLWFLGS_XXX TPI_FLWFLGS_XXX/owner.txt does not exist. This is required, see: https://wiki.ith.intel.com/x/ZRfT_
259 TPI_DIESLCT_XXX TPI_DIESLCT_XXX/owner.txt does not exist. This is required, see: https://wiki.ith.intel.com/x/ZRfT_
(259, 'ARR'): 5
(259, 'PTH'): 5
(259, 'SCN'): 5
'''
        self.assertTextEqual(obj.ut_result(), expect)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
