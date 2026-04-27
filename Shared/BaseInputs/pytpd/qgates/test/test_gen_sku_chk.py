#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for gen_sku_chk.py

"""
import sys
try:
    from setenv_unittest import UT_DIR, UT_DIR_REPO, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR, UT_DIR_REPO, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests

from qgates.gen_sku_chk import *        # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock
import shutil


class TestGenSKU(TestCase):

    def test_pass(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple7c/POR_TP/TGLH81/EnvironmentFile.env').init()
        print("Running test_pass...")
        obj = GenSKUChk(tpobj)
        obj.main()
        # pprint(obj.result)

        # check results, one fail and one pass

        expect = []
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 0)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_error_209_noALLSKU(self):
        with TempDir(name=True, chdir=True, delete=True) as tdir:
            tpref = f'{UT_DIR}/Integ_2A_2'
            shutil.copytree(tpref, f'{tdir}/TPL')
            envfile = f'TPL/ENG_TP/Class_MTL_P68/EnvironmentFile.env'
            jsonfile = r'''
            {
            "Rules": [
                {
                    "Name": "CLASS_P68G2_6x",
                    "RecoveryArea": "SLICECORE",
                    "Trackers": [ "DSLC", "SLC7", "SLC6", "SLC5", "SLC4", "SLC3", "SLC2", "SLC1", "SLC0", "DCR", "CR5", "CR4", "CR3", "CR2", "CR1", "CR0", "ACRM1_23", "ACRM1_01", "ACRM0_23", "ACRM0_01" ],
                    "Mask" : "11111111000000001100000000000000",
                    "SKUs": [ "P68_6C+8A", "P68_6C+4A" ]
                },
                {
                    "Name": "CLASS_P68G2_4x",
                    "RecoveryArea": "SLICECORE",
                    "Trackers": [ "DSLC", "SLC7", "SLC6", "SLC5", "SLC4", "SLC3", "SLC2", "SLC1", "SLC0", "DCR", "CR5", "CR4", "CR3", "CR2", "CR1", "CR0", "ACRM1_23", "ACRM1_01", "ACRM0_23", "ACRM0_01" ],
                    "Mask" : "11111111000000001100000000000000",
                    "SKUs": [ "P68_6C+8A", "P68_6C+4A", "P68_4U+8A", "P68_4X+8A", "P68_4U+4A", "P68_4X+4A" ]
                },
                {
                    "Name": "CLASS_P68G2_x8",
                    "RecoveryArea": "SLICECORE",
                    "Trackers": [ "DSLC", "SLC7", "SLC6", "SLC5", "SLC4", "SLC3", "SLC2", "SLC1", "SLC0", "DCR", "CR5", "CR4", "CR3", "CR2", "CR1", "CR0", "ACRM1_23", "ACRM1_01", "ACRM0_23", "ACRM0_01" ],
                    "Mask" : "11111111000000001100000000000000",
                    "SKUs": [ "P68_6C+8A", "P68_4U+8A", "P68_4X+8A" ]
                },
                {
                    "Name": "CLASS_P68G2_x4",
                    "RecoveryArea": "SLICECORE",
                    "Trackers": [ "DSLC", "SLC7", "SLC6", "SLC5", "SLC4", "SLC3", "SLC2", "SLC1", "SLC0", "DCR", "CR5", "CR4", "CR3", "CR2", "CR1", "CR0", "ACRM1_23", "ACRM1_01", "ACRM0_23", "ACRM0_01" ],
                    "Mask" : "11111111000000001100000000000000",
                    "SKUs": [ "P68_6C+9A", "P68_6C+5A", "P68_4U+8A", "P68_4X+8A", "P68_4U+4A", "P68_4X+4A" ]
                }
            ]
            }
'''
            ybsfile = r'''<?xml version="1.0" encoding="utf-8"?>
<GT_SKUs_config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" >
   <Area name="SLICECORE">
       <UpsRecoveryGroupGsdsToken name="NA"/>
       <RecoveryGroups>
       </RecoveryGroups>
       <SKUs group="P68_6C+8A"></SKUs>
       <SKUs group="P68_6C+4A"></SKUs>
       <SKUs group="P68_4U+8A"></SKUs>
       <SKUs group="P68_4X+8A"></SKUs>
       <SKUs group="P68_4U+4A"></SKUs>
       <SKUs group="P68_4X+4A"></SKUs>
       <SKUs group="P28_2C+8A"></SKUs>
       <SKUs group="P28_2C+4A"></SKUs>
       <SKUs group="P28_1C+8A"></SKUs>
       <SKUs group="P28_1C+4A"></SKUs>
   </Area>
</GT_SKUs_config>
'''
            File('TPL/Modules/TPI_BASEPRIM_XXX/InputFiles/DieRecovery_Rules_P68.json').touch(jsonfile, mkdir=True, newfile=True)
            File('TPL/Modules/YBS_UPSS_YXX/InputFiles/IA_ATOM_Recovery.xml').touch(ybsfile, mkdir=True, newfile=True)
            tpobj = TestProgram(envfile).init()
            print("Running test_error_209_noALLSKU...")
            obj = GenSKUChk(tpobj)
            obj.main()
            # pprint(obj.result)
            expect = [{'id': 209,
                       'message': 'Recovery SKU TPD vs YBS compare check failed for test: '
                                  'CTRL_X_PRIMEDIERECOVERY_K_INIT_X_X_X_X_X, difference: '
                                  "['P68_6C+5A', 'P68_6C+9A']",
                       'module': 'TPI_BASEPRIM_XXX'}]

            self.assertEqual(obj.result, expect)
            self.assertEqual(len(obj.passed), 1)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_error_209(self):
        with TempDir(name=True, chdir=True, delete=True) as tdir:
            tpref = f'{UT_DIR}/Integ_2A_2'
            shutil.copytree(tpref, f'{tdir}/TPL')
            envfile = f'TPL/ENG_TP/Class_MTL_P68/EnvironmentFile.env'
            jsonfile = r'''
            {
            "Rules": [
                {
                    "Name": "CLASS_P68G2_6x",
                    "RecoveryArea": "SLICECORE",
                    "Trackers": [ "DSLC", "SLC7", "SLC6", "SLC5", "SLC4", "SLC3", "SLC2", "SLC1", "SLC0", "DCR", "CR5", "CR4", "CR3", "CR2", "CR1", "CR0", "ACRM1_23", "ACRM1_01", "ACRM0_23", "ACRM0_01" ],
                    "Mask" : "11111111000000001100000000000000",
                    "SKUs": [ "P68_6C+8A", "P68_6C+4A" ]
                },
                {
                    "Name": "CLASS_P68G2_4x",
                    "RecoveryArea": "SLICECORE",
                    "Trackers": [ "DSLC", "SLC7", "SLC6", "SLC5", "SLC4", "SLC3", "SLC2", "SLC1", "SLC0", "DCR", "CR5", "CR4", "CR3", "CR2", "CR1", "CR0", "ACRM1_23", "ACRM1_01", "ACRM0_23", "ACRM0_01" ],
                    "Mask" : "11111111000000001100000000000000",
                    "SKUs": [ "P68_6C+8A", "P68_6C+4A", "P68_4U+8A", "P68_4X+8A", "P68_4U+4A", "P68_4X+4A" ]
                },
                {
                    "Name": "CLASS_P68G2_x8",
                    "RecoveryArea": "SLICECORE",
                    "Trackers": [ "DSLC", "SLC7", "SLC6", "SLC5", "SLC4", "SLC3", "SLC2", "SLC1", "SLC0", "DCR", "CR5", "CR4", "CR3", "CR2", "CR1", "CR0", "ACRM1_23", "ACRM1_01", "ACRM0_23", "ACRM0_01" ],
                    "Mask" : "11111111000000001100000000000000",
                    "SKUs": [ "P68_6C+8A", "P68_4U+8A", "P68_4X+8A" ]
                },
                {
                    "Name": "CLASS_P68G2_x4",
                    "RecoveryArea": "SLICECORE",
                    "Trackers": [ "DSLC", "SLC7", "SLC6", "SLC5", "SLC4", "SLC3", "SLC2", "SLC1", "SLC0", "DCR", "CR5", "CR4", "CR3", "CR2", "CR1", "CR0", "ACRM1_23", "ACRM1_01", "ACRM0_23", "ACRM0_01" ],
                    "Mask" : "11111111000000001100000000000000",
                    "SKUs": [ "P68_6C+8A", "P68_6C+4A", "P68_4U+8A", "P68_4X+8A", "P68_4U+4A", "P68_4X+4A" ]
                }
            ],
            "ALLSKU": [
                {
                    "Ref": "Modules/TPI_BASEPRIM_XXX/InputFiles/IA_ATOM_Recovery.xml",
                    "SKUs": [ "P68_6C+9A", "P68_6C+4A", "P68_4U+8A", "P68_4X+8A", "P68_4U+4A", "P68_4X+4A", "P28_2C+8A", "P28_2C+4A", "P28_1C+8A", "P28_1C+4A"]
                }
            ]
            }
'''
            File('TPL/Modules/TPI_BASEPRIM_XXX/InputFiles/DieRecovery_Rules_P68.json').touch(jsonfile, mkdir=True,
                                                                                             newfile=True)
            tpobj = TestProgram(envfile).init()
            print("Running test_error_209...")
            obj = GenSKUChk(tpobj)
            obj.main()
            # pprint(obj.result)
            expect = [{'id': 209,
                       'message': 'Recovery SKU TPD vs YBS compare check failed for test: '
                                  'CTRL_X_PRIMEDIERECOVERY_K_INIT_X_X_X_X_X, difference: '
                                  "['P68_6C+9A']",
                       'module': 'TPI_BASEPRIM_XXX'}]
            self.assertEqual(obj.result, expect)
            self.assertEqual(len(obj.passed), 1)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_error_210(self):
        with TempDir(name=True, chdir=True, delete=True) as tdir:
            tpref = f'{UT_DIR}/Integ_2A_2'
            shutil.copytree(tpref, f'{tdir}/TPL')
            envfile = f'TPL/ENG_TP/Class_MTL_P68/EnvironmentFile.env'
            jsonfile = r'''
            {
            "Rules": [
                {
                    "Name": 'CLASS_P68G2_6x',
                    "RecoveryArea": "SLICECORE",
                    "Trackers": [ "DSLC", "SLC7", "SLC6", "SLC5", "SLC4", "SLC3", "SLC2", "SLC1", "SLC0", "DCR", "CR5", "CR4", "CR3", "CR2", "CR1", "CR0", "ACRM1_23", "ACRM1_01", "ACRM0_23", "ACRM0_01" ],
                    "Mask" : "11111111000000001100000000000000",
                    "SKUs": [ "P68_6C+8A", "P68_6C+4A" ]
                },
                {
                    "Name": "CLASS_P68G2_4x",
                    "RecoveryArea": "SLICECORE",
                    "Trackers": [ "DSLC", "SLC7", "SLC6", "SLC5", "SLC4", "SLC3", "SLC2", "SLC1", "SLC0", "DCR", "CR5", "CR4", "CR3", "CR2", "CR1", "CR0", "ACRM1_23", "ACRM1_01", "ACRM0_23", "ACRM0_01" ],
                    "Mask" : "11111111000000001100000000000000",
                    "SKUs": [ "P68_6C+8A", "P68_6C+4A", "P68_4U+8A", "P68_4X+8A", "P68_4U+4A", "P68_4X+4A" ]
                },
                {
                    "Name": "CLASS_P68G2_x8",
                    "RecoveryArea": "SLICECORE",
                    "Trackers": [ "DSLC", "SLC7", "SLC6", "SLC5", "SLC4", "SLC3", "SLC2", "SLC1", "SLC0", "DCR", "CR5", "CR4", "CR3", "CR2", "CR1", "CR0", "ACRM1_23", "ACRM1_01", "ACRM0_23", "ACRM0_01" ],
                    "Mask" : "11111111000000001100000000000000",
                    "SKUs": [ "P68_6C+8A", "P68_4U+8A", "P68_4X+8A" ]
                },
                {
                    "Name": "CLASS_P68G2_x4",
                    "RecoveryArea": "SLICECORE",
                    "Trackers": [ "DSLC", "SLC7", "SLC6", "SLC5", "SLC4", "SLC3", "SLC2", "SLC1", "SLC0", "DCR", "CR5", "CR4", "CR3", "CR2", "CR1", "CR0", "ACRM1_23", "ACRM1_01", "ACRM0_23", "ACRM0_01" ],
                    "Mask" : "11111111000000001100000000000000",
                    "SKUs": [ "P68_6C+8A", "P68_6C+4A", "P68_4U+8A", "P68_4X+8A", "P68_4U+4A", "P68_4X+4A" ]
                }
            ],
            "ALLSKU": [
                {
                    "Ref": "Modules/TPI_BASEPRIM_XXX/InputFiles/IA_ATOM_Recovery.xml",
                    "SKUs": [ "P68_6C+9A", "P68_6C+4A", "P68_4U+8A", "P68_4X+8A", "P68_4U+4A", "P68_4X+4A", "P28_2C+8A", "P28_2C+4A", "P28_1C+8A", "P28_1C+4A"]
                }
            ]
            }
'''
            File('TPL/Modules/TPI_BASEPRIM_XXX/InputFiles/DieRecovery_Rules_P68.json').touch(jsonfile, mkdir=True, newfile=True)
            tpobj = TestProgram(envfile).init()
            print("Running test_error_210...")
            obj = GenSKUChk(tpobj)
            obj.main()
            # pprint(obj.result)
            expect = [{'id': 210,
                       'message': 'Recovery SKU TPD vs YBS compare check failed, RulesFile is '
                                  'invalid or empty: '
                                  './Modules/TPI_BASEPRIM_XXX/InputFiles/DieRecovery_Rules_P68.json',
                       'module': 'TPI_BASEPRIM_XXX'}]
            self.assertEqual(obj.result, expect)
            self.assertEqual(len(obj.passed), 0)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
