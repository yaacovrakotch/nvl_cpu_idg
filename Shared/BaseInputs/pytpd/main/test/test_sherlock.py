#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for checkers
"""
import sys
from setenv_unittest import UT_DIR, UT_DIR_REPO, ROOT_ENV, EXIST_PDX_I_DRIVE    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.gizmo import MockVar, with_
from gadget.files import TempDir, File
from gadget.disk import Chdir
from gadget.helperclass import CaptureStdoutLog
from gadget.errors import ErrorUser
from main.sherlock import *
from tp.mtpl import Mtpl
from os.path import join, dirname, abspath
from tp.plist import Plists
from tp.testprogram import Env
from unittest.mock import Mock
import shutil


class TestCheckers(TestCase):

    def test_run_check(self):
        obj = Checkers()

        # success case
        with TempDir(name=True, chdir=True) as tdir:
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)
            obj = Checkers()

            obj.skipchks = [
                obj.mtl_mfcchk,
                obj.gen_upchk
            ]

            obj.run_check(obj.mtl_mfcchk, True, 'ARR_CORE_CXX')  # skip
            obj.run_check(obj.gen_upchk, True, 'ARR_CORE', 'EVMINS_CR_VMIN_K_END_X_VX_F2_X_1504')  # skip
            obj.run_check(obj.gen_fcchk, True, 'ARR_SOC', 'EVMINS_SA_VMIN_K_BEGSOC_X_VCCSA_FMIN_X_1504')  # do not skip

            self.assertEqual(set(obj.sum.keys()), {obj.gen_fcchk})

    @with_(TempDir, chdir=True, delete=True)
    def test_final_decide_error(self):
        obj = Checkers()
        mkdirs('Shared/BaseInputs')

        # case1: no trigger file
        # ==== no error
        obj.final_decide_error('')
        # ==== with exception
        obj.final_decide_error('Some exception')
        # ==== with errors
        with MockVar(obj, 'allerrors', {'error1'}):
            obj.final_decide_error('')

        # case2: empty sherlock.trigger.txt - POR case
        File('Shared/BaseInputs/sherlock.trigger.txt').touch()
        # ===== no error
        obj.final_decide_error('')
        # ===== with exception
        with self.assertRaisesRegex(ErrorCheck, 'Sherlock has errors: Some exception'):
            obj.final_decide_error('Some exception')
        # ==== with errors
        with MockVar(obj, 'allerrors', {'error1'}):
            with self.assertRaisesRegex(ErrorCheck, 'Sherlock has errors: 1 new errors'):
                obj.final_decide_error('')

        # case3: some content on sherlock.trigger.txt
        File('Shared/BaseInputs/sherlock.trigger.txt').touch('error1\nerror2\n')
        # ===== no error
        obj.final_decide_error('')
        # ===== with exception
        with self.assertRaisesRegex(ErrorCheck, 'Sherlock has errors: Some exception'):
            obj.final_decide_error('Some exception')
        # ==== with errors, skipped
        with MockVar(obj, 'allerrors', {'error1'}):
            obj.final_decide_error('')
        # ==== with errors, new and exception
        with MockVar(obj, 'allerrors', {'error1', 'error3'}):
            with self.assertRaisesRegex(ErrorCheck, 'Sherlock has errors: 1 new errors'):
                obj.final_decide_error('')
            with self.assertRaisesRegex(ErrorCheck, 'Sherlock has errors: Some exceptionx'):
                obj.final_decide_error('Some exceptionx')

    def test_env_gate_rename(self):
        obj = Checkers()

        # success case
        with TempDir(name=True, chdir=True, delete=True):
            File('EnvironmentFile_CLASS_P28G2.env').touch()
            obj.env_gate_rename()
            self.assertEqual(os.listdir('.'), ['EnvironmentFile_CLASS_P28G2.env'])   # no change
            self.assertEqual(os.path.getsize('EnvironmentFile_CLASS_P28G2.env'), 0)

        # success case - A4
        with TempDir(name=True, chdir=True, delete=True):
            targ = 'EnvironmentFile_CLASS_P68G2_TRCFAILED.env'
            File(targ).touch()
            obj.env_gate_rename()
            self.assertEqual(os.listdir('.'), [targ])   # no change
            self.assertEqual(os.path.getsize(targ), 0)

        # pass case
        with TempDir(name=True, chdir=True, delete=True):
            targ = 'EnvironmentFile_CLASS_P28G2_CHKFAILED.env'
            File(targ).touch()
            obj.env_gate_rename()
            self.assertEqual(os.listdir('.'), [targ])   # no change
            self.assertEqual(os.path.getsize(targ), 0)

        # fail case
        with TempDir(name=True, chdir=True, delete=True):
            File('EnvironmentFile_CLASS_P28G2_TRCFAILED.env').touch()
            mkdirs('Reports')
            obj.env_gate_rename()
            self.assertEqual(os.listdir('Reports'), ['file_da39a3.bat'])
            self.assertGreater(os.path.getsize('EnvironmentFile_CLASS_P28G2_TRCFAILED.env'), 100)

    # common routines/non-checking functions
    def test_gen_subflow(self):
        with TempDir(name=True, chdir=True) as tdir:
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)
            obj = Checkers()
            sf = obj.gen_subflow('EVMINS_CR_VMIN_K_SCRF2_X_X_X_X_TEST3_1001')
            self.assertTextEqual(sf, 'SCRF2')
            sf = obj.gen_subflow('EVMINS_CR_VMIN_K_BEGCPU_X_X_X_X_TEST3')
            self.assertTextEqual(sf, 'BEGCPU')
            sf = obj.gen_subflow('EVMINS_CR_VMIN_K_START_X')
            self.assertTextEqual(sf, 'START')
            sf = obj.gen_subflow('EVMINS_TEST')
            self.assertTextEqual(sf, 'NYET')

    def test_gen_badenv(self):
        with TempDir(name=True, chdir=True) as tdir:
            renenv = 1  # Sherlock errors observed
            f1 = 'EnvironmentFile_CLASS_P68G2.env'
            f2 = 'EnvironmentFile_CLASS_P28G2_TRCFAILED.env'
            f3 = 'EnvironmentFile_CLASS_P28G1_TRCFAILED_CHKFAILED.env'
            f1new = 'EnvironmentFile_CLASS_P68G2_CHKFAILED.env'
            f2new = 'EnvironmentFile_CLASS_P28G2_TRCFAILED_CHKFAILED.env'
            f3nef = 'EnvironmentFile_CLASS_P28G1_TRCFAILED_CHKFAILED_CHKFAILED.env'

            File(f1).touch('', mkdir=True, newfile=True)
            File(f2).touch('', mkdir=True, newfile=True)
            File(f3).touch('', mkdir=True, newfile=True)

            obj = Checkers()
            obj.gen_badenv(renenv)
            self.assertTrue(exists(f1new))
            self.assertTrue(exists(f2new))
            self.assertFalse(exists(f3nef))

        with TempDir(name=True, chdir=True) as tdir:
            renenv = 0  # Sherlock errors ZERO
            f1 = 'EnvironmentFile_CLASS_P68G2.env'
            f2 = 'EnvironmentFile_CLASS_P28G2_TRCFAILED.env'
            f3 = 'EnvironmentFile_CLASS_P28G1_TRCFAILED_CHKFAILED.env'
            f1new = 'EnvironmentFile_CLASS_P68G2_CHKFAILED.env'
            f2new = 'EnvironmentFile_CLASS_P28G2_TRCFAILED_CHKFAILED.env'

            File(f1).touch('', mkdir=True, newfile=True)
            File(f2).touch('', mkdir=True, newfile=True)
            File(f3).touch('', mkdir=True, newfile=True)

            obj = Checkers()
            obj.gen_badenv(renenv)
            self.assertFalse(exists(f1new))
            self.assertFalse(exists(f2new))

    def test_gen_janitor(self):
        with TempDir(name=True, chdir=True) as tdir:
            f1 = 'EnvironmentFile_CLASS_P68G2.env.old'
            f2 = 'EnvironmentFile_CLASS_P28G2_TRCFAILED.env'
            s1 = 'SubTestPlan_CLASS_P28G2.stpl.old'
            s2 = 'SubTestPlan_CLASS_P68G2.stpl.old'
            f1new = 'Reports/EnvironmentFile_CLASS_P68G2.env.old'
            f2new = 'Reports/EnvironmentFile_CLASS_P28G2_TRCFAILED.env'
            s1new = 'Reports/SubTestPlan_CLASS_P28G2.stpl.old'
            s2new = 'Reports/SubTestPlan_CLASS_P68G2.stpl.old'
            rpt = 'Reports/dummy.txt'

            File(f1).touch('', mkdir=True, newfile=True)
            File(f2).touch('', mkdir=True, newfile=True)
            File(s1).touch('', mkdir=True, newfile=True)
            File(s2).touch('', mkdir=True, newfile=True)
            File(rpt).touch('', mkdir=True, newfile=True)

            obj = Checkers()
            obj.gen_janitor()
            self.assertFalse(exists(f1))
            self.assertTrue(exists(f2))
            self.assertFalse(exists(s1))
            self.assertFalse(exists(s2))
            self.assertTrue(exists(f1new))
            self.assertFalse(exists(f2new))
            self.assertTrue(exists(s1new))
            self.assertTrue(exists(s2new))

    # targeted checker unit tests
    def test_gen_skuchk(self):
        obj = Checkers()
        with TempDir(name=True, chdir=True, delete=True) as tdir:
            data = {'TEMPLATE': 'DieRecoveryBase',
                    'LogLevel': 'DISABLED',
                    'RulesFile': 'DieRecovery_Rules_P68.json',
                    'SKUFile': 'IA_ATOM_Recovery.xml',
                    'TrackerFile': './Modules/TPI_BASEPRIM_Y68K/InputFiles/DieRecoveryTrackers_68.json',
                    'AllowDefeatures': 'True'}

            rules_path = join(tdir, 'DieRecovery_Rules_P68.json')
            File(rules_path).touch('', mkdir=True, newfile=True)

            sku_path = join(tdir, 'IA_ATOM_Recovery.xml')
            File(sku_path).touch('', mkdir=True, newfile=True)

            # success case
            with open(rules_path, 'w') as f:
                rules_data = {
                    "Rules": [
                        {
                            "Name": "CLASS_P68G2_6x",
                            "SKUs": ["P68_6C+8A", "P68_6C+4A"]
                        }
                    ],
                    "ALLSKU": [
                        {
                            "Ref": "IA_ATOM_Recovery.xml",
                            "SKUs": ["P68_6C+8A", "P68_6C+4A", "P68_4C+8A", "P68_4C+4A"]
                        }
                    ]
                }

                json.dump(rules_data, f)

            with open(sku_path, 'w') as f:
                f.write('''<GT_SKUs_config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                <Area name="SLICECORE">
                <SKUs group="P68_6C+8A"/>
                <SKUs group="P68_6C+4A"/>
                <SKUs group="P68_4C+8A"/>
                <SKUs group="P68_4C+4A"/>
                </Area>
                </GT_SKUs_config>''')
                # root = etree.Element('GT_SKUs_config', nsmap={
                #     'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
                # })
                # area = etree.SubElement(root, 'Area', {
                #     'name': 'SLICECORE'
                # })
                # groups = ["P68_6C+8A", "P68_6C+4A", "P68_4C+8A", "P68_4C+4A"]
                # for group in groups:
                #     etree.SubElement(area, 'SKUs', {
                #         'group': group
                #     })
                #
                # f.write(etree.tostring(root))
            # self.assertTextEqual(File(sku_path).read(), '')

            obj.run_check(obj.gen_skuchk, True, 'ARR_CORE', 'EVMINS_CR_VMIN_K_END_X_VX_F2_X_1504', data)

            # fail case -> SKUs do not match Ref
            with open(rules_path, 'w') as f:
                rules_data = {
                    "Rules": [
                        {
                            "Name": "CLASS_P68G2_6x",
                            "SKUs": ["P68_6C+8A", "P68_6C+4A"]
                        },
                        {
                            "Name": "CLASS_P68G2_4x",
                            "SKUs": ["P68_6C+8A", "P68_6C+4A", "P68_4C+8A"]
                        }
                    ],
                    "ALLSKU": [
                        {
                            "Ref": "IA_ATOM_Recovery.xml",
                            "SKUs": ["P68_6C+8A", "P68_6C+4A", "P68_4C+8A"]
                        }
                    ]
                }

                json.dump(rules_data, f)

            obj.run_check(obj.gen_skuchk, True, 'ARR_CORE', 'EVMINS_CR_VMIN_K_END_X_VX_F2_X_1504', data)

            # fail case -> "ALLSKU" key does not exists (warning)
            with open(rules_path, 'w') as f:
                rules_data = {
                    "Rules": [
                        {
                            "Name": "CLASS_P68G2_6x",
                            "SKUs": ["P68_6C+8A", "P68_6C+4A"]
                        },
                        {
                            "Name": "CLASS_P68G2_4x",
                            "SKUs": ["P68_6C+8A", "P68_6C+4A", "P68_4C+8A"]
                        }
                    ]
                }

                json.dump(rules_data, f)

            obj.run_check(obj.gen_skuchk, True, 'ARR_CORE', 'EVMINS_CR_VMIN_K_END_X_VX_F2_X_1504', data)

            # fail case -> invalid - empy RulesFile
            with open(rules_path, 'w') as f:
                f.write(' ')

            obj.run_check(obj.gen_skuchk, True, 'ARR_CORE', 'EVMINS_CR_VMIN_K_END_X_VX_F2_X_1504', data)

            # check
            self.assertEqual(obj.sum[obj.gen_skuchk], {'ARR_CORE': {'e': 1, 'w': 2, 'p': 1}})

    def test_mtl_mfcchk(self):
        with TempDir(name=True, chdir=True) as tdir:
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)
            obj = Checkers()
            obj.run_check(obj.mtl_mfcchk, True, 'ARR_CORE_CXX')
            obj.run_check(obj.mtl_mfcchk, True, 'ARR_CORE')
            obj.run_check(obj.mtl_mfcchk, True, 'ARR_CCF_AON_CXX')
            obj.run_check(obj.mtl_mfcchk, True, 'IP_CPU_BASE')
            self.assertEqual(obj.sum[obj.mtl_mfcchk], {'ARR_CCF_AON_CXX': {'e': 1, 'w': 0, 'p': 0},
                                                       'ARR_CORE': {'e': 1, 'w': 0, 'p': 0},
                                                       'ARR_CORE_CXX': {'e': 0, 'w': 0, 'p': 1}
                                                       })
            self.assertEqual(obj.msgstr,
                             ['ARR_CORE -Error111- ModuleName FieldCount check failed, must have 3fields',
                              'ARR_CCF_AON_CXX -Error111- ModuleName FieldCount check failed, must have 3fields'
                              ])

    def test_mtl_dup_plist(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple3/POR_TP/TGLH81/EnvironmentFile.env')

        # pass case - no duplicate
        with TempDir(name=True, chdir=True) as tdir:
            text = '''<HdmtReferenceFile>
  <IPReference name="IP_PCH" path=".\\PLIST_ALL_IP_PCH.plist.ipxml" />
  <IPReference name="IP_CPU" path=".\\PLIST_ALL_IP_CPU.plist.ipxml" />
  <PList>
    <PListFile name="AAA_drv_cdie_C28_vrevC28B0P_ippkg_CLASS_P28G2.plist" />
    <PListFile name="PTH_BGCEP_c28_CLASS_P28G2.plist" />
  </PList>
</HdmtReferenceFile>
'''
            File('PLIST_ALL_CLASS_P28G1.plist.xml').touch(text)
            text = '''<HdmtReferenceFile>
  <PList>
    <PListFile name="AAA_drv_cdie_C28_vrevC28B0P_class_CLASS_P28G2.plist" />
    <PListFile name="arr_cdie_mbist_class_ks_eccl_perbistportallstepspbap_CLASS_P28G2.plist" />
  </PList>
</HdmtReferenceFile>
'''
            File('PLIST_ALL_IP_CPU.plist.ipxml').touch(text)

            text = '''<HdmtReferenceFile>
              <PList>
                <PListFile name="AAA_drv_gdie_GLG_vrevGLGA3P_class_class_p68g2.plist" />
                <PListFile name="array_gt_class_p68g2.plist" />
              </PList>
            </HdmtReferenceFile>
            '''

            File('PLIST_ALL_IP_PCH.plist.ipxml').touch(text)
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)
            obj = Checkers()

            plist_files = ['PLIST_ALL_CLASS_P28G1.plist.xml', 'PLIST_ALL_IP_CPU.plist.ipxml', 'PLIST_ALL_IP_PCH.plist.ipxml']
            with MockVar(tpobj, 'get_file_allplist_real', Mock(return_value=plist_files)):
                result = obj.mtl_dup_plist(tp=tpobj)
            self.assertEqual(result, None)

        # fail case - w/ duplicate
        with TempDir(name=True, chdir=True) as tdir:
            text = '''<HdmtReferenceFile>
  <IPReference name="IP_PCH" path=".\\PLIST_ALL_IP_PCH.plist.ipxml" />
  <IPReference name="IP_CPU" path=".\\PLIST_ALL_IP_CPU.plist.ipxml" />
  <PList>
    <PListFile name="AAA_drv_cdie_C28_vrevC28B0P_ippkg_CLASS_P28G2.plist" />
    <PListFile name="PTH_BGCEP_c28_CLASS_P28G2.plist" />
  </PList>
</HdmtReferenceFile>
'''
            File('PLIST_ALL_CLASS_P28G1.plist.xml').touch(text)
            text = '''<HdmtReferenceFile>
  <PList>
    <PListFile name="AAA_drv_cdie_C28_vrevC28B0P_class_CLASS_P28G2.plist" />
    <PListFile name="PTH_BGCEP_c28_CLASS_P28G2.plist" />
  </PList>
</HdmtReferenceFile>
'''
            File('PLIST_ALL_IP_CPU.plist.ipxml').touch(text)
            text = '''<HdmtReferenceFile>
              <PList>
                <PListFile name="AAA_drv_gdie_GLG_vrevGLGA3P_class_class_p68g2.plist" />
                <PListFile name="array_gt_class_p68g2.plist" />
              </PList>
            </HdmtReferenceFile>
            '''

            File('PLIST_ALL_IP_PCH.plist.ipxml').touch(text)

            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)
            obj = Checkers()
            plist_files = ['PLIST_ALL_CLASS_P28G1.plist.xml', 'PLIST_ALL_IP_CPU.plist.ipxml', 'PLIST_ALL_IP_PCH.plist.ipxml']
            with MockVar(tpobj, 'get_file_allplist_real', Mock(return_value=plist_files)):
                result = obj.mtl_dup_plist(tp=tpobj)
                print("RESULT: ", result)
            self.maxDiff = None
            self.assertEqual(result, [{'type': 'non-bypass',
                                       'message': 'DUPLICATE: PTH_BGCEP_c28_CLASS_P28G2.plist: PLIST_ALL_IP_CPU.plist.ipxml and PLIST_ALL_CLASS_P28G1.plist.xml',
                                       'id': '207',
                                       'module': 'env'}])
            # fail case 3 duplicates
            with TempDir(name=True, chdir=True) as tdir:
                text = '''<HdmtReferenceFile>
      <IPReference name="IP_PCH" path=".\\PLIST_ALL_IP_PCH.plist.ipxml" />
      <IPReference name="IP_CPU" path=".\\PLIST_ALL_IP_CPU.plist.ipxml" />
      <PList>
        <PListFile name="AAA_drv_cdie_C28_vrevC28B0P_ippkg_CLASS_P28G2.plist" />
        <PListFile name="array_gt_class_p68g2.plist" />
      </PList>
    </HdmtReferenceFile>
    '''
                File('PLIST_ALL_CLASS_P28G1.plist.xml').touch(text)
                text = '''<HdmtReferenceFile>
      <PList>
        <PListFile name="AAA_drv_cdie_C28_vrevC28B0P_class_CLASS_P28G2.plist" />
        <PListFile name="array_gt_class_p68g2.plist" />
      </PList>
    </HdmtReferenceFile>
    '''
                File('PLIST_ALL_IP_CPU.plist.ipxml').touch(text)
                text = '''<HdmtReferenceFile>
                  <PList>
                    <PListFile name="AAA_drv_gdie_GLG_vrevGLGA3P_class_class_p68g2.plist" />
                    <PListFile name="array_gt_class_p68g2.plist" />
                  </PList>
                </HdmtReferenceFile>
                '''

                File('PLIST_ALL_IP_PCH.plist.ipxml').touch(text)

                env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
                File(env).touch('', mkdir=True, newfile=True)
                obj = Checkers()
                plist_files = ['PLIST_ALL_CLASS_P28G1.plist.xml', 'PLIST_ALL_IP_CPU.plist.ipxml',
                               'PLIST_ALL_IP_PCH.plist.ipxml']
                with MockVar(tpobj, 'get_file_allplist_real', Mock(return_value=plist_files)):
                    result = obj.mtl_dup_plist(tp=tpobj)
                self.assertEqual(result, [{'type': 'non-bypass',
                                           'message': 'DUPLICATE: array_gt_class_p68g2.plist: PLIST_ALL_IP_CPU.plist.ipxml and PLIST_ALL_CLASS_P28G1.plist.xml',
                                           'id': '207',
                                           'module': 'env'},
                                          {'type': 'non-bypass',
                                           'message': 'DUPLICATE: array_gt_class_p68g2.plist: PLIST_ALL_IP_PCH.plist.ipxml and PLIST_ALL_CLASS_P28G1.plist.xml',
                                           'id': '207',
                                           'module': 'env'}])

    def test_gen_upchk(self):
        with TempDir(name=True, chdir=True) as tdir:
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)
            obj = Checkers()
            obj.run_check(obj.gen_upchk, True, 'ARR_CORE', 'EVMINS_CR_VMIN_K_END_X_VX_F2_X_1504')
            obj.run_check(obj.gen_upchk, True, 'ARR_CORE', 'EVMINS_CR_vmin_K_END_X_VX_F2_X_1504')
            obj.run_check(obj.gen_upchk, True, 'IP_CPU_BASE', 'EVMINS_CR_vmin_K_END_X_VX_F2_X_1504')
            self.assertEqual(obj.sum[obj.gen_upchk], {'ARR_CORE': {'e': 1, 'w': 0, 'p': 1}})
            self.assertEqual(obj.msgstr, ['ARR_CORE -Error112- UpperCase check failed for test: EVMINS_CR_vmin_K_END_X_VX_F2_X_1504'])

    def test_gen_fcchk(self):
        with TempDir(name=True, chdir=True) as tdir:
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)
            obj = Checkers()
            obj.run_check(obj.gen_fcchk, True, 'ARR_CORE', 'EVMINS_CR_VMIN_K')
            obj.run_check(obj.gen_fcchk, True, 'ARR_CORE', 'EVMINS_CR_VMIN_K_END_X_VX_F2_X_1504_X_X')
            obj.run_check(obj.gen_fcchk, True, 'ARR_CORE', 'EVMINS_CR_VMIN_K_END_X_VX_F2_X')
            obj.run_check(obj.gen_fcchk, True, 'ARR_CORE', 'EVMINS_CR_VMIN_K_END_X_VX_F2_X_1504')
            obj.run_check(obj.gen_fcchk, True, 'IP_CPU_BASE', 'EVMINS_CR_VMIN_K_END_X_VX_F2_X')
            obj.run_check(obj.gen_fcchk, True, 'ARR_SOC', 'EVMINS_SA_VMIN_K_BEGSOC_X_VCCSA_FMIN_X_1504')  # pass: test for FMIN
            obj.run_check(obj.gen_fcchk, True, 'ARR_SOC', 'EVMINS_SA_VMIN_K_BEGSOC_X_VCCSA_MIN_350_1504')  # pass: test for 3char freq
            obj.run_check(obj.gen_fcchk, True, 'ARR_SOC', 'EVMINS_SA_VMIN_K_BEGSOC_X_VCCSA_VMIN_0350_1504')  # pass: test for 0.3char freq
            obj.run_check(obj.gen_fcchk, True, 'ARR_SOC', 'EVMINS_SA_VMIN_K_BEGSOC_X_VCCSA_FMAX_3333_1504')  # pass: test for 4char freq
            obj.run_check(obj.gen_fcchk, True, 'ARR_SOC', 'EVMINS_SA_VMIN_K_BEGSOC_X_VCCSA_FMIN_10000_CLKYTEST')  # pass: test for 5char freq
            self.assertEqual(obj.sum[obj.gen_fcchk], {'ARR_CORE': {'e': 1, 'w': 0, 'p': 3},
                                                      'ARR_SOC': {'e': 0, 'w': 0, 'p': 5}})
            self.assertEqual(obj.msgstr, ['ARR_CORE -Error113- Testname Convention check failed for test: EVMINS_CR_VMIN_K'])

    def test_gen_sfchk(self):
        with TempDir(name=True, chdir=True) as tdir:
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)
            obj = Checkers()
            obj.run_check(obj.gen_sfchk, True, 'ARR_CORE', 'EVMINS_CR_VMIN_K_END_X_VX_F2_X_1504')
            obj.run_check(obj.gen_sfchk, True, 'ARR_CORE', 'EVMINS_CR_VMIN_K_BEND_X_VX_F2_X_1504')
            obj.run_check(obj.gen_sfchk, True, 'ARR_CORE', 'EVMINS_CR_VMIN_K_BEND_X_VX_F2_X_USER')
            obj.run_check(obj.gen_sfchk, True, 'IP_CPU_BASE', 'DUMMY_CR_VMIN_K_END_X_VX_F2_X_1504')
            obj.run_check(obj.gen_sfchk, True, 'ARR_CORE', 'SHORT_NAME')  # solid fail
            obj.run_check(obj.gen_sfchk, True, 'ARR_CORE', 'EVMINS_CR_VMIN_K_END_DEADBEEF')  # pass subflow but fail regex query
            obj.run_check(obj.gen_sfchk, True, 'ARR_CORE', 'EVMINS_CR_VMIN_K_INFCR_X_VX_F2_X_1504')
            obj.run_check(obj.gen_sfchk, True, 'ARR_CORE', 'EVMINS_CR_VMIN_K_INFCPU_X_VX_F2_X_1504')
            obj.run_check(obj.gen_sfchk, True, 'ARR_CORE', 'EVMINS_CR_VMIN_K_THRFF_X_VX_F2_X_1504')
            self.assertEqual(obj.sum[obj.gen_sfchk], {'ARR_CORE': {'e': 4, 'w': 0, 'p': 4}})
            self.assertEqual(obj.msgstr, ['ARR_CORE -Error115- Invalid subflow=BEND from test: EVMINS_CR_VMIN_K_BEND_X_VX_F2_X_1504',
                                          'ARR_CORE -Error115- Invalid subflow=BEND from test: EVMINS_CR_VMIN_K_BEND_X_VX_F2_X_USER',
                                          'ARR_CORE -Error114- TestName Convention failed hence unable to parse subflow correctly for test: SHORT_NAME',
                                          'ARR_CORE -Error115- Invalid subflow=INFCR from test: EVMINS_CR_VMIN_K_INFCR_X_VX_F2_X_1504'
                                          ])

    def test_cttrchk(self):
        with TempDir(name=True, chdir=True) as tdir:
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)
            obj = Checkers()
            obj.run_check(obj.cttrchk, False, 'ARR_CORE_CXX', 'EVMINS_CLR_VMIN_K_END_X_VX_F1_X_2401', 'drv_clr_end_ipcpu_list', 1001)
            obj.run_check(obj.cttrchk, False, 'ARR_CORE_CXX', 'EVMINS_CLR_VMIN_K_END_X_VX_F1_X_2401', 'drv_clr_bend_ipcpu_list', 1001)
            obj.run_check(obj.cttrchk, False, 'ARR_CORE_CXX', 'EVMINS_CLR_VMIN_K_END_X_VX_F1_X_2401', 'drv_clr_bend_list', 1001)
            obj.run_check(obj.cttrchk, False, 'IP_CPU_BASE', 'EVMINS_CLR_VMIN_K_END_X_VX_F1_X_2401', 'drv_clr_end_ipcpu_list', 1001)
            obj.run_check(obj.cttrchk, False, 'DUMMY', 'TPIE_PgmRules', 'drv_clr_end_ipcpu_list', 1001)  # unlikely scenario, UT only
            self.assertEqual(obj.sum[obj.mtl_cttrchk], {'ARR_CORE_CXX': {'e': 0, 'w': 2, 'p': 1},
                                                        'IP_CPU_BASE': {'e': 0, 'w': 0, 'p': 1}
                                                        })
            self.assertEqual(obj.msgstr, ['ARR_CORE_CXX -Warning116- Patlist used in wrong test/subflow, test:EVMINS_CLR_VMIN_K_END_X_VX_F1_X_2401 subflow:END != patlist:drv_clr_bend_ipcpu_list subflow:BEND',
                                          'ARR_CORE_CXX -Warning117- Unable to check cttr compliance for test: EVMINS_CLR_VMIN_K_END_X_VX_F1_X_2401 patlist:drv_clr_bend_list base#:1001'
                                          ])

    def test_gen_preplbchk(self):
        with TempDir(name=True, chdir=True) as tdir:
            bomplbs = ['/intel/hdmxpats/mtl/ARR/RevT123.0/p0/plb', '/intel/hdmxpats/mtl/ARR/RevT123.0/p0/plb/slim',
                       '/intel/hdmxpats/mtl/SCN/RevT324.1/p4/plb']
            obj = Checkers()
            self.assertEqual(obj.gen_preplbchk(bomplbs), ['/intel/hdmxpats/mtl/ARR/RevT123.0/p0/',
                                                          '/intel/hdmxpats/mtl/SCN/RevT324.1/p4/'
                                                          ])

    def test_gen_fetchinteg(self):
        with TempDir(name=True, chdir=True) as tdir:
            ir = join(tdir, 'POR_TP/blah/Reports/Integration_Report.txt')
            ir_data = """
[Program Identification]
#-------------------------------------------------------------------------------
<Program Type>    Module Validation
<Program Family>  Meteorlake
<Subfamily>       Class MTL P1
<Base TP Name>    Integ5
#-------------------------------------------------------------------------------
[Environment settings]
#-------------------------------------------------------------------------------
<Pattern Revs>    | Pattern Module | Revision       | Dependent modules
                   #------------------------------------------------------------
                    aaacdrv          RevTCCXXA0.0p0   DRV_RESET_CXX,DRV_RESET_GXX*
                    scn              RevTCCXXA0.0p0   SCN_CORE,SCN_RING
                  #[* indicates modules which specify older/different pattern revs that
"""
            File(ir).touch(ir_data, mkdir=True, newfile=True)
            obj = Checkers()
            self.assertEqual(obj.gen_fetchinteg(), ({'aaacdrv': ['DRV_RESET_CXX', 'DRV_RESET_GXX'],
                                                     'scn': ['SCN_CORE', 'SCN_RING']}))

        with TempDir(name=True, chdir=True) as tdir:
            ir = join(tdir, 'POR_TP/blah/Reports/Integration_Report.txt')
            ir_data = """
[Program Identification]
#-------------------------------------------------------------------------------
<Program Type>    Release Candidate
<Program Family>  Meteorlake
<Subfamily>       Class MTL P1
<Base TP Name>    Integ5
#-------------------------------------------------------------------------------
[Environment settings]
#-------------------------------------------------------------------------------
<Pattern Revs>    | Pattern Module | Revision       | Dependent modules
                   #------------------------------------------------------------
                    aaacdrv          RevTCCXXA0.0p0   DRV_RESET_CXX,DRV_RESET_GXX*
                    scn              RevTCCXXA0.0p0   SCN_CORE,SCN_RING
                  #[* indicates modules which specify older/different pattern revs that
"""
            File(ir).touch(ir_data, mkdir=True, newfile=True)
            obj = Checkers()
            self.assertEqual(obj.gen_fetchinteg(), ({'aaacdrv': ['DRV_RESET_CXX', 'DRV_RESET_GXX'],
                                                     'scn': ['SCN_CORE', 'SCN_RING']}))

        # Raise error scenario
        with TempDir(name=True, chdir=True) as tdir:
            ir = join(tdir, 'POR_TP/blah/Reports/Integration_Report.txt')
            ir_data = """
[Program Identification]
#-------------------------------------------------------------------------------
<Program Type>    Release Candidate
<Program Family>  Meteorlake
<Subfamily>       Class MTL P1
<Base TP Name>    Integ5
#-------------------------------------------------------------------------------
[Environment settings]
#-------------------------------------------------------------------------------
<Pattern Revs>    | Pattern Module | Revision       | Dependent modules
                   #------------------------------------------------------------
                    yyycdrv          RevTCCXXA0.0p0   DRV_RESET_CXX,DRV_RESET_GXX*
                    zzscnRevTCCXXA0.0p0SCN_CORE,SCN_RING
                  #[* indicates modules which specify older/different pattern revs that
"""
            File(ir).touch(ir_data, mkdir=True, newfile=True)
            obj = Checkers()
            with self.assertRaisesRegex(ErrorUser, 'Unable to parse the plb patch from integration report'):
                obj.gen_fetchinteg()

    def test_gen_plistchk(self):
        with TempDir(name=True, chdir=True) as tdir:
            testinstances = [('DRV_RESET_SXN', 'RESET_TEST1', {'TEMPLATE': 'PrimeFunctionalTestMethod', 'LevelsTc': 'BASE::levels', 'patlist': 'socn_lr_phase1a_list', 'TimingsTc': 'BASE::timings', 'BypassPort': '-1'}, ''),  # pass
                             ('DRV_RESET_SXN', 'RESET_TEST2', {'TEMPLATE': 'PrimeFunctionalTestMethod', 'LevelsTc': 'BASE::levels', 'patlist': 'socn_lr_phase2a_list', 'TimingsTc': 'BASE::timings', 'BypassPort': '-1'}, ''),  # pass
                             ('DRV_RESET_SXN', 'RESET_TEST3', {'TEMPLATE': 'PrimeFunctionalTestMethod', 'LevelsTc': 'BASE::levels', 'patlist': 'FAIL_lr_phase2a_list', 'TimingsTc': 'BASE::timings', 'BypassPort': '-1'}, ''),  # Error missing patlist
                             ('DRV_RESET_SXN', 'RESET_TEST4', {'TEMPLATE': 'PrimeFunctionalTestMethod', 'LevelsTc': 'BASE::levels', 'patlist': 'IP_PCH::socn_lr_phase2a_list', 'TimingsTc': 'BASE::timings', 'BypassPort': '-1'}, ''),  # pass
                             ('DRV_RESET_SXN', 'RESET_TEST5', {'TEMPLATE': 'PrimeFunctionalTestMethod', 'LevelsTc': 'BASE::levels', 'patlist': 'IP_CPU::socn_lr_phase2b_list', 'TimingsTc': 'BASE::timings', 'BypassPort': '-1'}, ''),  # Error missing patlist
                             ('DRV_RESET_SXN', 'RESET_TEST6', {'TEMPLATE': 'PrimeFunctionalTestMethod', 'LevelsTc': 'BASE::levels', 'patlist': 'IP_CPU::socn_lr_phase2c_list', 'TimingsTc': 'BASE::timings', 'BypassPort': '1'}, ''),  # ignore missing patlist
                             ('DRV_RESET_SXN', 'RESET_TEST7', {'TEMPLATE': 'PrimeFunctionalTestMethod', 'LevelsTc': 'BASE::levels', 'patlist': 'socn_lr_phase1a_list', 'TimingsTc': 'BASE::timings'}, ''),  # pass
                             ('TPI_PRESI_CXX', 'DUMMY_TEST', {'TEMPLATE': 'PrimeFunctionalTestMethod', 'LevelsTc': 'BASE::levels', 'patlist': 'IP_CPU::missinglist', 'TimingsTc': 'BASE::timings'}, ''),  # ignore TPI_PRESI
                             ('DRV_RESET_SXN', 'RESET_TEST8', {'TEMPLATE': 'PlistConfigTC', 'LevelsTc': 'BASE::levels', 'patlist': '.*a', 'TimingsTc': 'BASE::timings', 'BypassPort': '-1'}, ''),  # Special template
                             ]
            plbmap = {'socn_lr_phase1a_list': '/path/drv_resetA.plist', 'socn_lr_phase2a_list': '/path/drv_resetA.plist'}
            bom = 'CLASS_P68G2'

            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)
            obj = Checkers()

            class fake_mtpl_obj:
                @staticmethod
                def is_bypassed(mod, test):
                    for md, tn, data, _ in testinstances:
                        if md == mod and test == tn:
                            if data.get('BypassPort') == '1':
                                return True
                    return False

            obj.run_check(obj.gen_plistchk, True, testinstances, plbmap, bom, fake_mtpl_obj)
            self.assertEqual(obj.sum[obj.gen_plistchk], {'DRV_RESET_SXN': {'e': 2, 'w': 0, 'p': 5}})
            self.assertEqual(obj.msgstr, ['DRV_RESET_SXN -Error121- Patlist:FAIL_lr_phase2a_list for test:RESET_TEST3 is missing! Bypass:False BOM:CLASS_P68G2',
                                          'DRV_RESET_SXN -Error121- Patlist:socn_lr_phase2b_list for test:RESET_TEST5 is missing! Bypass:False BOM:CLASS_P68G2'
                                          ])

    def test_gen_pgmruleprep(self):
        with TempDir(name=True, chdir=True) as tdir:
            fam = [('DRV_RESET_SXN', 'RESET_TEST1', {'TEMPLATE': 'PrimeFunctionalTestMethod', 'LevelsTc': 'BASE::levels', 'patlist': 'socn_lr_phase1a_list', 'TimingsTc': 'BASE::timings'}, ''),
                   ('ARR_CORE', 'TORCH_PgmRules', {'TEMPLATE': 'iCGlXpressTest', 'allow_multiple_gl_xpress_match': 'TRUE', 'allow_zero_gl_xpress_match': 'FALSE', 'user_mode': 'DEFAULT_MODE', 'gl_xpress_file_path': './Modules/ARR_CORE/TPIE_pgmRules_CLASS_P28G2.txt'}, ''),
                   ('ARR_CORE', 'GLXPRESS01', {'TEMPLATE': 'iCGlXpressTest', 'allow_multiple_gl_xpress_match': 'TRUE', 'allow_zero_gl_xpress_match': 'FALSE', 'user_mode': 'DEFAULT_MODE', 'gl_xpress_file_path': './Modules/ARR_CORE/pgmRules01.txt'}, ''),
                   ('ARR_CORE', 'GLXPRESS02', {'TEMPLATE': 'iCGlXpressTest', 'allow_multiple_gl_xpress_match': 'TRUE', 'allow_zero_gl_xpress_match': 'FALSE', 'user_mode': 'DEFAULT_MODE', 'gl_xpress_file_path': './Modules/ARR_CORE/pgmRules02.txt'}, ''),
                   ('ARR_CORE', 'GLXPRESS02', {'TEMPLATE': 'iCGlXpressTest', 'allow_multiple_gl_xpress_match': 'TRUE', 'allow_zero_gl_xpress_match': 'FALSE', 'user_mode': 'DEFAULT_MODE', 'gl_xpress_file_path': './Modules/ARR_CORE/pgmRules02_REPEAT.txt'}, ''),
                   ('ARR_RING', 'GLXPRESS01', {'TEMPLATE': 'iCGlXpressTest', 'allow_multiple_gl_xpress_match': 'TRUE', 'allow_zero_gl_xpress_match': 'FALSE', 'user_mode': 'DEFAULT_MODE', 'gl_xpress_file_path': './Modules/ARR_RING/pgmRules01.txt'}, '')
                   ]
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)
            obj = Checkers()
            result = obj.gen_pgmruleprep(fam)
            pprint(result)
            self.assertEqual(result, {'ARR_CORE': {'GLXPRESS01': {'combo': {}, 'glx': './Modules/ARR_CORE/pgmRules01.txt', 'bpg': None},
                                                   'GLXPRESS02': {'combo': {}, 'glx': './Modules/ARR_CORE/pgmRules02_REPEAT.txt', 'bpg': None}},
                                      'ARR_RING': {'GLXPRESS01': {'combo': {}, 'glx': './Modules/ARR_RING/pgmRules01.txt', 'bpg': None}}
                                      })

    def test_gen_pgmrulechk(self):  # will fail here!
        with TempDir(name=True, chdir=True) as tdir:
            pgmrule = {'ARR_CORE': {'CORE_TEST': {'glx': 'Modules/ARR_CORE/Input_Files/pgm.txt', 'bpg': '-1'}},
                       'ARR_RING': {'RING_TEST': {'glx': 'Modules/ARR_RING/Input_Files/pgm.txt', 'bpg': None}}
                       }

            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)
            # clean run on ARR_CORE, dirty on ARR_RING with double entry and missing ALL/ALL_CLASS
            arrc_pgm = join(tdir, 'Modules/ARR_CORE/Input_Files/pgm.txt')
            arrc_ptxt = """bypass_global = "-1", Template, ARR_CORE::EVMINS_SAQ_VMIN_K_END_X_VX_F1_WEVATEST_1503   : H6,*,*,*,*,*,*,*,*,*,*,*,ALL/-PHM
bypass_global = "1", Template, ARR_CORE::EVMINS_SAQ_VMIN_K_END_X_VX_F1_WEVATEST_1503   : H6,*,*,*,*,*,*,*,*,*,*,*,PHM
"""
            File(arrc_pgm).touch(arrc_ptxt, mkdir=True)
            arrr_pgm = join(tdir, 'Modules/ARR_RING/Input_Files/pgm.txt')
            arrr_ptxt = """bypass_global = "-1", Template, ARR_RING::EVMINS_SAQ_VMIN_K_END_X_VX_F1_WEVATEST_1503   : H6,*,*,*,*,*,*,*,*,*,*,*,ALL/-CSM
bypass_global = "1", Template, ARR_RING::EVMINS_SAQ_VMIN_K_END_X_VX_F1_WEVATEST_1503   : H6,*,*,*,*,*,*,*,*,*,*,*,CSM
# This is a comment, line below is an empty line (elif not line)

       # this is also a comment, line.strip() should clear the starting spaces
bypass_global = "1", Template, ARR_RING::EVMINS_SAQ_VMIN_K_END_X_VX_F1_WEVATEST_1504   : H6,*,*,*,*,*,*,*,*,*,*,*,COLD
bypass_global = "1", Template, ARR_RING::EVMINS_SAQ_VMIN_K_END_X_VX_F1_WEVATEST_1504   : H6,*,*,*,*,*,*,*,*,*,*,*,COLD
"""
            File(arrr_pgm).touch(arrr_ptxt, mkdir=True)
            obj = Checkers()
            obj.run_check(obj.gen_pgmrulechk, True, pgmrule)
            self.assertEqual(obj.sum[obj.gen_pgmrulechk], {'ARR_CORE': {'e': 0, 'w': 0, 'p': 1},
                                                           'ARR_RING': {'e': 1, 'w': 0, 'p': 1}
                                                           })
            self.assertEqual(obj.msgstr, ['ARR_RING -Error120- PGMrule test:RING_TEST with action on param|test combo:bypass_global_ARR_RING::EVMINS_SAQ_VMIN_K_END_X_VX_F1_WEVATEST_1504 does not have default ALL/ALL_CLASS setting'])

    def test_mtl_getvalidcid(self):
        with TempDir(name=True, chdir=True) as tdir:  # pass scenario
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)
            upsfile = join(tdir, 'Modules/TPI_BASEPRIM_XXX/InputFiles/MTL_CLASS_P68G2_VminForwardingConfiguration.json')
            bom = 'CLASS_P68G2'

            upsfile_data = """{
    "powerDomains":[
    {
        "name":"AT",
        "instances":"AT1,AT0",
        "corners":[
            {
                "name":"F6",
                "frequencySource":{
                    "type":"BinMatrix",
                    "value":"AT_F6_FREQ"
                },
                "voltageSources":{
                    "sharedStorageLimitCheck":"VMINDFF_ATF6",
                    "corner":[
                        "AT@F5"
                    ],
                    "frequencySwitchAdjustment":"AT@F5"
                },
                "exportStorageVariable":{
                    "voltageVariablePrefix":"CURRENT_FAST_VMIN_VCCC_",
                    "frequencyVariablePrefix":"CURRENT_FAST_VMINFREQUENCY_"
                }
            },
            {
                "name":"F5",
                "frequencySource":{
                    "type":"BinMatrix",
                    "value":"AT_F5_FREQ"
                },
                "voltageSources":{
                    "sharedStorageLimitCheck":"VMINDFF_ATF5",
                    "corner":[
                        "AT@F4"
                    ],
                    "frequencySwitchAdjustment":"AT@F4"
                },
                "exportStorageVariable":{
                    "voltageVariablePrefix":"CURRENT_FAST_VMIN_VCCC_",
                    "frequencyVariablePrefix":"CURRENT_FAST_VMINFREQUENCY_"
                }
            }
        ]
    }
    {
        "name":"CR",
        "instances":"CR5,CR4,CR3,CR2",
        "corners":[
            {
                "name":"F6",
                "frequencySource":{
                    "type":"BinMatrix",
                    "value":"CR_F6_FREQ"
                },
                "voltageSources":{
                    "sharedStorageLimitCheck":"VMINDFF_CRF6",
                    "corner":[
                        "CR@F5"
                    ],
                    "frequencySwitchAdjustment":"CR@F5"
                },
                "exportStorageVariable":{
                    "voltageVariablePrefix":"CURRENT_FAST_VMIN_VCCC_",
                    "frequencyVariablePrefix":"CURRENT_FAST_VMINFREQUENCY_"
                }
            }
        ]
    }
    {
        "name":"GT",
        "instances":"GT0",
        "corners":[
            {
                "name":"F6",
                "frequencySource":{
                    "type":"BinMatrix",
                    "value":"GT_F6_FREQ"
                },
                "voltageSources":{
                    "sharedStorageLimitCheck":"VMINDFF_GTF6",
                    "corner":[
                        "GT@F5"
                    ],
                    "frequencySwitchAdjustment":"GT@F5"
                },
                "exportStorageVariable":{
                    "voltageVariablePrefix":"CURRENT_FAST_VMIN_VCCGT_",
                    "frequencyVariablePrefix":"CURRENT_FAST_VMINFREQUENCY_"
                }
            },
            {
                "name":"F5",
                "frequencySource":{
                    "type":"BinMatrix",
                    "value":"GT_F5_FREQ"
                    },
                "voltageSources":{
                    "sharedStorageLimitCheck":"VMINDFF_GTF5",
                    "corner":[
                        "GT@F4"
                    ],
                    "frequencySwitchAdjustment":"GT@F4"
                },
                "exportStorageVariable":{
                    "voltageVariablePrefix":"CURRENT_FAST_VMIN_VCCGT_",
                    "frequencyVariablePrefix":"CURRENT_FAST_VMINFREQUENCY_"
                }
            }
        }
    ]
}
"""
            File(upsfile).touch(upsfile_data, mkdir=True, newfile=True)
            obj = Checkers()
            self.assertEqual(obj.mtl_getvalidcid(bom), ['AT1@F6', 'AT0@F6', 'AT1@F5', 'AT0@F5', 'CR5@F6', 'CR4@F6', 'CR3@F6', 'CR2@F6', 'GT0@F6', 'GT0@F5'])

        with TempDir(name=True, chdir=True) as tdir:  # missing upsfile scenario
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)
            upsfile = join(tdir, 'Modules/TPI_BASEPRIM_XXX/InputFiles/MTL_CLASS_P68G2_VminForwardingConfiguration.json')
            bom = 'CLASS_P68G2'
            # File(upsfile).touch(upsfile_data, mkdir=True, newfile=True)  # do not generate the file
            obj = Checkers()
            with self.assertRaisesRegex(ErrorUser, 'No files found'):
                obj.mtl_getvalidcid(bom)

        with TempDir(name=True, chdir=True) as tdir:  # instances data is missing/unreadable
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)
            upsfile = join(tdir, 'Modules/TPI_BASEPRIM_XXX/InputFiles/MTL_CLASS_P68G2_VminForwardingConfiguration.json')
            bom = 'CLASS_P68G2'

            upsfile_data = """{
    "powerDomains":[
    {
        "name":"AT",
        "instances":"",
        "corners":[
            {
                "name":"F6",
                "frequencySource":{
                    "type":"BinMatrix",
                    "value":"AT_F6_FREQ"
                },
                "voltageSources":{
                    "sharedStorageLimitCheck":"VMINDFF_ATF6",
                    "corner":[
                        "AT@F5"
                    ],
                    "frequencySwitchAdjustment":"AT@F5"
                },
                "exportStorageVariable":{
                    "voltageVariablePrefix":"CURRENT_FAST_VMIN_VCCC_",
                    "frequencyVariablePrefix":"CURRENT_FAST_VMINFREQUENCY_"
                }
            }
        ]
    }
}
"""
            File(upsfile).touch(upsfile_data, mkdir=True, newfile=True)
            obj = Checkers()
            with self.assertRaisesRegex(ErrorCheck, 'Unable to acquire the target ups domain/s from line'):
                obj.mtl_getvalidcid(bom)

        with TempDir(name=True, chdir=True) as tdir:  # freq data is missing/unreadable
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)
            upsfile = join(tdir, 'Modules/TPI_BASEPRIM_XXX/InputFiles/MTL_CLASS_P68G2_VminForwardingConfiguration.json')
            bom = 'CLASS_P68G2'

            upsfile_data = """{
    "powerDomains":[
    {
        "name":"AT",
        "instances":"AT1,AT0",
        "corners":[
            {
                "name":"F6",
                "frequencySource":{
                    "type":"BinMatrix",
                    "value":"AT_F6_FREQ"
                },
                "voltageSources":{
                    "sharedStorageLimitCheck":"VMINDFF_ATF6",
                    "corner":[
                        "AT@F5"
                    ],
                    "frequencySwitchAdjustment":"AT@F5"
                },
                "exportStorageVariable":{
                    "voltageVariablePrefix":"CURRENT_FAST_VMIN_VCCC_",
                    "frequencyVariablePrefix":"CURRENT_FAST_VMINFREQUENCY_"
                }
            },
            {
                "name":"F ",
                "frequencySource":{
                    "type":"BinMatrix",
                    "value":"AT_F5_FREQ"
                },
                "voltageSources":{
                    "sharedStorageLimitCheck":"VMINDFF_ATF5",
                    "corner":[
                        "AT@F4"
                    ],
                    "frequencySwitchAdjustment":"AT@F4"
                },
                "exportStorageVariable":{
                    "voltageVariablePrefix":"CURRENT_FAST_VMIN_VCCC_",
                    "frequencyVariablePrefix":"CURRENT_FAST_VMINFREQUENCY_"
                }
            }
        ]
    }
}
"""
            File(upsfile).touch(upsfile_data, mkdir=True, newfile=True)
            obj = Checkers()
            with self.assertRaisesRegex(ErrorCheck, 'Unable to acquire the target freq from line'):
                obj.mtl_getvalidcid(bom)

        with TempDir(name=True, chdir=True) as tdir:  # pass scenario
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)
            upsfile = join(tdir, 'Modules/TPI_BASEPRIM_XXX/InputFiles/MTL_CLASS_P68G2_VminForwardingConfiguration.json')
            bom = 'CLASS_P68G2'

            upsfile_data = """{
    "powerDomains":[
    {
        "name":"AT",
        "instances":"AT1,AT0",
        "corners":[
            {
                "name":"F6",
                "frequencySource":{
                    "type":"BinMatrix",
                    "value":"AT_F6_FREQ"
                },
                "voltageSources":{
                    "sharedStorageLimitCheck":"VMINDFF_ATF6",
                    "corner":[
                        "AT@F5"
                    ],
                    "frequencySwitchAdjustment":"AT@F5"
                },
                "exportStorageVariable":{
                    "voltageVariablePrefix":"CURRENT_FAST_VMIN_VCCC_",
                    "frequencyVariablePrefix":"CURRENT_FAST_VMINFREQUENCY_"
                }
            },
            {
                "name":"F6",
                "frequencySource":{
                    "type":"BinMatrix",
                    "value":"AT_F5_FREQ"
                },
                "voltageSources":{
                    "sharedStorageLimitCheck":"VMINDFF_ATF5",
                    "corner":[
                        "AT@F4"
                    ],
                    "frequencySwitchAdjustment":"AT@F4"
                },
                "exportStorageVariable":{
                    "voltageVariablePrefix":"CURRENT_FAST_VMIN_VCCC_",
                    "frequencyVariablePrefix":"CURRENT_FAST_VMINFREQUENCY_"
                }
            }
        ]
    }
}
"""
            File(upsfile).touch(upsfile_data, mkdir=True, newfile=True)
            obj = Checkers()
            with self.assertRaisesRegex(ErrorCheck, 'Duplicate cornerid detected'):
                obj.mtl_getvalidcid(bom)

    def test_mtl_pltscpchk(self):
        with TempDir(name=True, chdir=True) as tdir:
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)
            ipcpu = {'DUMMY_CPU', 'ARR_CORE_CXX', 'IP_CPU_BASE'}
            ippch = {'DUMMY_PCH', 'ARR_CORE_PXX', 'IP_PCH_BASE'}
            obj = Checkers()
            obj.run_check(obj.mtl_pltscpchk, True, 'IP_CPU_BASE', 'TEST', 'patlist', 'level', 'timings', ipcpu, ippch)  # ignore modules
            obj.run_check(obj.mtl_pltscpchk, True, 'IP_PCH_BASE', 'TEST', 'patlist', 'level', 'timings', ipcpu, ippch)  # ignore modules
            obj.run_check(obj.mtl_pltscpchk, True, 'ARR_CORE_CXX', 'TEST', 'IP_CPU::patlist', 'IP_CPU::level', 'IP_CPU::timings', ipcpu, ippch)  # CPU sc21
            obj.run_check(obj.mtl_pltscpchk, True, 'ARR_CORE_CXX', 'TEST', None, 'IP_CPU::level', 'IP_CPU::timings', ipcpu, ippch)  # CPU with no patlist, unlikely scnerio for UT only
            obj.run_check(obj.mtl_pltscpchk, True, 'ARR_CORE_PXX', 'TEST', 'IP_PCH::patlist', 'IP_PCH::level', 'IP_PCH::timings', ipcpu, ippch)  # PCH sc22
            obj.run_check(obj.mtl_pltscpchk, True, 'ARR_CORE_CXX', 'TEST', 'patlist', 'IP_CPU::level', 'IP_CPU::timings', ipcpu, ippch)  # CPU sc02
            obj.run_check(obj.mtl_pltscpchk, True, 'ARR_CORE_CXX', 'TEST', 'patlist', 'ARR_CORE_CXX::level', 'IP_CPU::timings', ipcpu, ippch)  # CPU with UDC Levels sc08
            obj.run_check(obj.mtl_pltscpchk, True, 'ARR_CORE_CXX', 'TEST', 'patlist', 'IP_CPU::level', 'ARR_CORE_CXX::timings', ipcpu, ippch)  # CPU with UDC Timings sc07
            obj.run_check(obj.mtl_pltscpchk, True, 'ARR_CORE_CXX', 'TEST', 'patlist', 'ARR_CORE_CXX::level', 'ARR_CORE_CXX::timings', ipcpu, ippch)  # CPU with UDC Levels/Timings sc05
            obj.run_check(obj.mtl_pltscpchk, True, 'ARR_CORE_PXX', 'TEST', 'patlist', 'IP_PCH::level', 'IP_PCH::timings', ipcpu, ippch)  # PCH sc03
            obj.run_check(obj.mtl_pltscpchk, True, 'ARR_CORE_PXX', 'TEST', 'patlist', 'ARR_CORE_PXX::level', 'IP_PCH::timings', ipcpu, ippch)  # PCH with UDC Levels sc10
            obj.run_check(obj.mtl_pltscpchk, True, 'ARR_CORE_PXX', 'TEST', 'patlist', 'IP_PCH::level', 'ARR_CORE_PXX::timings', ipcpu, ippch)  # PCH with UDC Timings sc09
            obj.run_check(obj.mtl_pltscpchk, True, 'ARR_CORE_PXX', 'TEST', 'patlist', 'ARR_CORE_PXX::level', 'ARR_CORE_PXX::timings', ipcpu, ippch)  # PCH with UDC Levels/Timings sc06
            obj.run_check(obj.mtl_pltscpchk, True, 'ARR_CORE_XXX', 'TEST', 'patlist', '_pkg_level', 'timings', ipcpu, ippch)  # pure PKG sc01 _pkg_level
            obj.run_check(obj.mtl_pltscpchk, True, 'ARR_CORE_XXX', 'TEST', 'patlist', '_die_level', 'timings', ipcpu, ippch)  # pure PKG sc01 _die_level (sort like levels name)
            obj.run_check(obj.mtl_pltscpchk, True, 'ARR_CORE_XXX', 'TEST', 'IP_CPU::patlist', '_pkg_level', 'IP_CPU::timings', ipcpu, ippch)  # PKG with IP plist/timings sc11
            obj.run_check(obj.mtl_pltscpchk, True, 'ARR_CORE_XXX', 'TEST', 'IP_PCH::patlist', '_pkg_level', 'IP_PCH::timings', ipcpu, ippch)  # PKG with IP plist/timings sc12
            obj.run_check(obj.mtl_pltscpchk, True, 'ARR_CORE_XXX', 'TEST', 'IP_CPU::patlist', '_pkg_level', 'ARR_CORE_XXX::timings', ipcpu, ippch)  # error138 PKG with IP_CPU plist UDC timing sc17
            obj.run_check(obj.mtl_pltscpchk, True, 'ARR_CORE_XXX', 'TEST', 'IP_PCH::patlist', '_pkg_level', 'ARR_CORE_XXX::timings', ipcpu, ippch)  # error139 PKG with IP_PCH plist UDC timing sc18
            obj.run_check(obj.mtl_pltscpchk, True, 'ARR_CORE_CXX', 'TEST', 'IP_CPU::patlist', 'IP_PCH::level', 'IP_PCH::timings', ipcpu, ippch)  # else error 118
            obj.run_check(obj.mtl_pltscpchk, True, 'ARR_CORE_CXX', 'TEST', 'IP_CPU::patlist', 'level', 'timings', ipcpu, ippch)  # else error 118
            obj.run_check(obj.mtl_pltscpchk, True, 'ARR_CORE_PXX', 'TEST', 'IP_PCH::patlist', 'level', 'timings', ipcpu, ippch)  # else error 118
            obj.run_check(obj.mtl_pltscpchk, True, 'ARR_DLVR_XXX', 'TEST', 'patlist', '_pkg_level', 'IP_CPU::timings', ipcpu, ippch)  # else error 118
            obj.run_check(obj.mtl_pltscpchk, True, 'ARR_DLVR_XXX', 'TEST', 'patlist', 'IP_CPU::level', 'timings', ipcpu, ippch)  # else error 118
            obj.run_check(obj.mtl_pltscpchk, True, 'ARR_DLVR_XXX', 'TEST', 'patlist', 'IP_CPU::level', 'IP_CPU::timings', ipcpu, ippch)  # else error 118
            obj.run_check(obj.mtl_pltscpchk, True, 'ARR_DLVR_XXX', 'TEST', 'patlist', 'ARR_DLVR_XXXX::_pkg_level', 'timings', ipcpu, ippch)  # pass sc23
            obj.run_check(obj.mtl_pltscpchk, True, 'ARR_DLVR_XXX', 'TEST', 'patlist', '_pkg_level', 'ARR_DLVR_XXX::timings', ipcpu, ippch)  # pass sc24
            obj.run_check(obj.mtl_pltscpchk, True, 'ARR_DLVR_XXX', 'TEST', 'patlist', 'ARR_DLVR_XXX::_pkg_level', 'ARR_DLVR_XXX::timings', ipcpu, ippch)  # PKG with UDC Levels/Timings pass sc04
            obj.run_check(obj.mtl_pltscpchk, True, 'ARR_DLVR_XXX', 'TEST', 'IP_CPU::patlist', 'IP_CPU::level', 'IP_CPU::timings', ipcpu, ippch)  # error142 PKG with IP_CPU PLT sc19
            obj.run_check(obj.mtl_pltscpchk, True, 'ARR_DLVR_XXX', 'TEST', 'IP_PCH::patlist', 'IP_PCH::level', 'IP_PCH::timings', ipcpu, ippch)  # error143 PKG with IP_PCH PLT sc20
            obj.run_check(obj.mtl_pltscpchk, True, 'ARR_DLVR_XXX', 'TEST', 'IP_CPU::patlist', 'ARR_DLVR_XXX::level', 'IP_CPU::timings', ipcpu, ippch)  # error144 PKG with UDC levels/IP_CPU timings sc15
            obj.run_check(obj.mtl_pltscpchk, True, 'ARR_DLVR_XXX', 'TEST', 'IP_PCH::patlist', 'ARR_DLVR_XXX::level', 'IP_PCH::timings', ipcpu, ippch)  # error145 PKG with UDC levels/IP_PCH timings sc16
            obj.run_check(obj.mtl_pltscpchk, True, 'ARR_DLVR_XXX', 'TEST', 'IP_CPU::patlist', 'ARR_DLVR_XXX::_pkg_level', 'IP_CPU::timings', ipcpu, ippch)  # PKG with UDC _pkg_Levels/IP_CPU patlist/timings pass sc13
            obj.run_check(obj.mtl_pltscpchk, True, 'ARR_DLVR_XXX', 'TEST', 'IP_PCH::patlist', 'ARR_DLVR_XXX::_pkg_level', 'IP_PCH::timings', ipcpu, ippch)  # PKG with UDC _pkg_Levels/IP_PCH patlist/timings pass sc14
            obj.run_check(obj.mtl_pltscpchk, True, 'ARR_DLVR_XXX', 'TEST', 'IP_CPU::patlist', 'ARR_DLVR_XXX::_die_level', 'IP_CPU::timings', ipcpu, ippch)  # PKG with UDC _die_Levels/IP_CPU patlist/timings pass sc13 (sort like levels name)
            obj.run_check(obj.mtl_pltscpchk, True, 'ARR_DLVR_XXX', 'TEST', 'IP_PCH::patlist', 'ARR_DLVR_XXX::_die_level', 'IP_PCH::timings', ipcpu, ippch)  # PKG with UDC _die_Levels/IP_PCH patlist/timings pass sc14 (sort like levels name)
            self.assertEqual(obj.sum[obj.mtl_pltscpchk], {'ARR_CORE_CXX': {'e': 2, 'w': 0, 'p': 5},
                                                          'ARR_CORE_PXX': {'e': 1, 'w': 0, 'p': 5},
                                                          'ARR_CORE_XXX': {'e': 2, 'w': 0, 'p': 4},
                                                          'ARR_DLVR_XXX': {'e': 7, 'w': 0, 'p': 7}})
            self.assertEqual(obj.msgstr, ['ARR_CORE_XXX -Error138- PKG module using IP_CPU::patlist cannot use Timings with overrides test:TEST p=IP_CPU::patlist l=_pkg_level t=ARR_CORE_XXX::timings',
                                          'ARR_CORE_XXX -Error139- PKG module using IP_PCH::patlist cannot use Timings with overrides test:TEST p=IP_PCH::patlist l=_pkg_level t=ARR_CORE_XXX::timings',
                                          'ARR_CORE_CXX -Error118- Patlist/levels/timings are not matching idut scope on test:TEST p=IP_CPU::patlist l=IP_PCH::level t=IP_PCH::timings',
                                          'ARR_CORE_CXX -Error118- Patlist/levels/timings are not matching idut scope on test:TEST p=IP_CPU::patlist l=level t=timings',
                                          'ARR_CORE_PXX -Error118- Patlist/levels/timings are not matching idut scope on test:TEST p=IP_PCH::patlist l=level t=timings',
                                          'ARR_DLVR_XXX -Error118- Patlist/levels/timings are not matching idut scope on test:TEST p=patlist l=_pkg_level t=IP_CPU::timings',
                                          'ARR_DLVR_XXX -Error118- Patlist/levels/timings are not matching idut scope on test:TEST p=patlist l=IP_CPU::level t=timings',
                                          'ARR_DLVR_XXX -Error118- Patlist/levels/timings are not matching idut scope on test:TEST p=patlist l=IP_CPU::level t=IP_CPU::timings',
                                          'ARR_DLVR_XXX -Error142- PKG module using IP_CPU in these params patlist/timings/levels test:TEST p=IP_CPU::patlist l=IP_CPU::level t=IP_CPU::timings',
                                          'ARR_DLVR_XXX -Error143- PKG module using IP_PCH in these params patlist/timings/levels test:TEST p=IP_PCH::patlist l=IP_PCH::level t=IP_PCH::timings',
                                          'ARR_DLVR_XXX -Error144- PKG module using IP_CPU::patlist cannot use Levels with overrides test:TEST p=IP_CPU::patlist l=ARR_DLVR_XXX::level t=IP_CPU::timings',
                                          'ARR_DLVR_XXX -Error145- PKG module using IP_PCH::patlist cannot use Levels with overrides test:TEST p=IP_PCH::patlist l=ARR_DLVR_XXX::level t=IP_PCH::timings'
                                          ])

    def test_mtl_ioepltscpchk(self):
        with TempDir(name=True, chdir=True) as tdir:
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)
            ipcpu = {'DUMMY_CPU', 'ARR_CORE_CXX', 'IP_CPU_BASE'}
            ippch = {'DUMMY_PCH', 'ARR_CORE_PXX', 'IP_PCH_BASE'}
            obj = Checkers()
            # override soc infra data
            obj.cfg['sum_locinfrachk']['DRV_RESET_SXN::RESET_X_FUNC_K_INFIOE_X_VNNAON_X_X_SOCINFRA_IOE']['t'] = 'soc_hvm_timing_perpin'
            obj.cfg['sum_locinfrachk']['DRV_RESET_SXN::RESET_X_FUNC_K_INFIOE_X_VNNAON_X_X_SOCINFRA_IOE']['p'] = 'infioe_list'
            obj.cfg['sum_locinfrachk']['DRV_RESET_SXN::RESET_X_FUNC_K_INFCPUIOE_X_VNNAON_X_X_SOCINFRA_CPUIOE']['t'] = 'soc_hvm_timing_perpin'
            obj.cfg['sum_locinfrachk']['DRV_RESET_SXN::RESET_X_FUNC_K_INFCPUIOE_X_VNNAON_X_X_SOCINFRA_CPUIOE']['p'] = 'infcpuioe_list'

            obj.run_check(obj.mtl_ioepltscpchk, True, 'DRV_RESET_IXP', 'TESTA', 'patlist', '_pkg_level', 'timings', ipcpu, ippch)  # DRV reset ignore
            obj.run_check(obj.mtl_ioepltscpchk, True, 'ARR_CORE_IXP', 'TESTB', 'IP_PCH::patlist', '_pkg_level', 'timings', ipcpu, ippch)  # Error156
            obj.run_check(obj.mtl_ioepltscpchk, True, 'ARR_CORE_IXX', 'TESTC', 'patlist', '_pkg_level', 'timings', ipcpu, ippch)  # Error157
            obj.run_check(obj.mtl_ioepltscpchk, True, 'ARR_CORE_IXX', 'TESTD', 'patlist', '_die_level', 'timings', ipcpu, ippch)  # Error157
            obj.run_check(obj.mtl_ioepltscpchk, True, 'ARR_CORE_IXX', 'TESTE', 'infcpuioe_list', '_die_level', 'soc_hvm_timing_perpin', ipcpu, ippch)  # p == i_p and t == i_t  pass!
            obj.run_check(obj.mtl_ioepltscpchk, True, 'ARR_CORE_IXX', 'TESTF', 'infcpuioe_list', '_die_level', 'soc_hvm_timing', ipcpu, ippch)  # p == i_p and t == i_t  Error155
            obj.run_check(obj.mtl_ioepltscpchk, True, 'ARR_CORE_IXX', 'TESTG', 'infioe_list', '_die_level', 'soc_hvm_timing_perpin', ipcpu, ippch)  # p == inf*ioe_list and t == i_t  pass!
            obj.run_check(obj.mtl_ioepltscpchk, True, 'ARR_CORE_IXX', 'TESTH', 'infioe_list', '_die_level', 'soc_hvm_timing', ipcpu, ippch)  # p == inf*ioe_list and t != i_t  Error158
            obj.run_check(obj.mtl_ioepltscpchk, True, 'ARR_CORE_IXX', 'TESTJ', 'patlist', '_pkg_level', 'ioep_pkg_xtal_timings', ipcpu, ippch)  # pure PKG sc01 _pkg_level
            obj.run_check(obj.mtl_ioepltscpchk, True, 'ARR_CORE_IXX', 'TESTK', 'patlist', '_die_level', 'ioep_pkg_xtal_timings', ipcpu, ippch)  # pure PKG sc01 _die_level (sort like levels name)
            obj.run_check(obj.mtl_ioepltscpchk, True, 'ARR_CORE_IXX', 'TESTL', 'patlist', '_pkg_level', 'ioem_pkg_xtal_timings', ipcpu, ippch)  # pure PKG sc01 _pkg_level
            obj.run_check(obj.mtl_ioepltscpchk, True, 'ARR_CORE_IXX', 'TESTM', 'patlist', '_die_level', 'ioem_pkg_xtal_timings', ipcpu, ippch)  # pure PKG sc01 _die_level (sort like levels name)
            obj.run_check(obj.mtl_ioepltscpchk, True, 'DRV_RESET', 'TESTN', 'patlist', '_pkg_level', 'timings', ipcpu, ippch)  # Not followwing naming convention #1
            obj.run_check(obj.mtl_ioepltscpchk, True, 'TPI_RESET', 'TESTP', 'patlist', '_pkg_level', 'timings', ipcpu, ippch)  # Not followwing naming convention #2
            self.assertEqual(obj.sum[obj.mtl_ioepltscpchk], {'ARR_CORE_IXX': {'e': 4, 'w': 0, 'p': 6},
                                                             'ARR_CORE_IXP': {'e': 1, 'w': 0, 'p': 0}})
            self.assertEqual(obj.msgstr, ['ARR_CORE_IXP -Error156- IOE PKG module is not using correct PLT settings for Astep test:TESTB p=IP_PCH::patlist l=_pkg_level t=timings',
                                          'ARR_CORE_IXX -Error157- IOE PKG module is not using correct PLT settings for Astep test:TESTC p=patlist l=_pkg_level t=timings',
                                          'ARR_CORE_IXX -Error157- IOE PKG module is not using correct PLT settings for Astep test:TESTD p=patlist l=_die_level t=timings',
                                          'ARR_CORE_IXX -Error158- IOE PKG module is not using correct pkg timings for Astep test:TESTF p=infcpuioe_list l=_die_level t=soc_hvm_timing SOCINFRA_TIM=soc_hvm_timing_perpin',
                                          'ARR_CORE_IXX -Error155- IOE PKG module is not using correct pkg timings for Astep test:TESTH p=infioe_list l=_die_level t=soc_hvm_timing SOCINFRA_TIM=soc_hvm_timing_perpin'
                                          ])

    def test_gen_spcharchk(self):
        with TempDir(name=True, chdir=True) as tdir:
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)

            # most cases are tested from using the small checkersTP/TPL
            badfiles = {'./Modules/ARR_CORE_CXX/InputFiles/document1.txt': ["line#111: 'qa_flag    = –1, GLOBAL, NONE :*,*,*,*,*,*,*,*,*,*,*,*,PHM\n'"],
                        './Modules/TPI_IDV_CXX/InputFiles/MTL_A0_LITE_0650.idvp.xml': ["Cannot read xml file: duplicate attribute: line 842, column 235"],
                        'trc_report_TGLU42_CLASS.csv': ["Bin 69 – unit exits fail flow without fail bin assignment,Bin 69 – unit exits fail flow starting\n"],
                        './Modules/YBS_UPSS_YXX/InputFiles/upload.xml': ["XML Line with special char: \n"],
                        r".\Modules\FUN_CORE_CXX\InputFiles\document2.txt": ["line#112: 'qb_flag    = –1, GLOBAL, NONE :*,*,*,*,*,*,*,*,*,*,*,*,PHM\n'"]
                        }
            obj = Checkers()
            with self.assertRaisesRegex(ErrorCheck, 'Unable to parse the module name from the filename'):
                obj.run_check(obj.gen_spcharchk, True, badfiles)

    def test_gen_spcharfilechk(self):
        with TempDir(name=True, chdir=True) as tdir:
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)

            # most cases are tested from using the small checkersTP/TPL
            filepaths = ['./Modules/ARR_CORE_CXX/ARR_CORE_CXX_CLASS_P68G2.mtpl',  # pass
                         './Modules/ARR_CORE_CXX/InputFiles/PASS FAIL.txt',  # fail due to space in filename
                         './Modules/ARR_CORE_CXX/InputFiles/PASS_FAIL.txt',  # pass
                         './Modules/ARR_CORE_CXX/InputFiles/PASS-FAIL.txt',  # pass with - sign
                         './Modules/ARR_CORE_CXX/InputFiles/PASS_FAIL0.txt',  # pass with _ sign
                         './Modules/SCN_CORE_CXX/SCN_CORE_CXX_CLASS_P68G2.mtpl',  # pass
                         './Modules/SCN_CORE_CXX/InputFiles/PASS$FAIL.txt',  # fail due to $ sign
                         './Modules/SCN_CORE_CXX/InputFiles/PASS+FAIL.txt',  # pass with + sign
                         './Modules/SCN_CORE_CXX/Input Files/PASSFAIL.txt',  # fail due to space in folder name
                         './Modules/SCN_CORE_CXX/InputFiles/@PASSFAIL.txt'  # fail due to @ sign in filename
                         ]
            obj = Checkers()
            obj.run_check(obj.gen_spcharfilechk, True, filepaths)
            self.assertEqual(obj.sum[obj.gen_spcharfilechk], {'ARR_CORE_CXX': {'e': 1, 'w': 0, 'p': 0},
                                                              'SCN_CORE_CXX': {'e': 3, 'w': 0, 'p': 0}
                                                              })
            self.assertEqual(obj.msgstr, ['ARR_CORE_CXX -Error194- File:./Modules/ARR_CORE_CXX/InputFiles/PASS FAIL.txt has an invalid char in the name!',
                                          'SCN_CORE_CXX -Error194- File:./Modules/SCN_CORE_CXX/InputFiles/PASS$FAIL.txt has an invalid char in the name!',
                                          'SCN_CORE_CXX -Error194- File:./Modules/SCN_CORE_CXX/Input Files/PASSFAIL.txt has an invalid char in the name!',
                                          'SCN_CORE_CXX -Error194- File:./Modules/SCN_CORE_CXX/InputFiles/@PASSFAIL.txt has an invalid char in the name!'
                                          ])

    def test_gen_testplacechk(self):
        with TempDir(name=True, chdir=True) as tdir:
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)

            # most cases are tested from using the small checkersTP/TPL
            ipcpu = {'ARR_CORE_CXX', 'FUN_CORE_CXX', 'TPI_BASE_IPCPU'}
            ippch = {'PSCN_SCN_IXX', 'TPI_BASE_IPPCH'}
            ipcpuflows = ['BEGCPU', 'HVBICPU', 'MAXCLR']
            ippchflows = ['BEGGT', 'BEGIOE']
            pkgflows = ['MAIN', 'BEGCPUPKG', 'BEGIOEPKG', 'PREPRLCPUGT', 'THRFF', 'BEGSOC']
            testtrace = {('ARR_CORE_CXX', 'EVMINS_CR_TEST_DUMMY'): ['MAIN', 'ARR_CORE_CXX::ARR_CORE_CXX_MAIN'],  # NYET scenario
                         ('FUN_CORE_CXX', 'EVMINS_CR_VMIN_K_BEGGT_X_X_X_X_TEST'): ['MAIN', 'FUN_CORE_CXX::FUN_CORE_CXX_BEGGT'],  # error: ipcpu module with ippch subflow
                         ('PSCN_SCN_IXX', 'EVMINS_CR_VMIN_K_BEGCPU_X_X_X_X_TEST'): ['MAIN', 'PSCN_SCN_IXX::PSCN_SCN_IXX_BEGCPU'],  # error: ippch module with ipcpu subflow
                         ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_BEGCPUPKG_X_X_X_X_TEST'): ['MAIN', 'ARR_CORE_CXX::ARR_CORE_CXX_BEGCPUPKG'],  # error: ipcpu module with PKG subflow
                         ('PSCN_SCN_IXX', 'EVMINS_CR_VMIN_K_BEGIOEPKG_X_X_X_X_TEST'): ['MAIN', 'PSCN_SCN_IXX::PSCN_SCN_IXX_BEGIOEPKG'],  # error: ipcpch module with PKG subflow
                         ('TPI_BASE_XXX', 'EVMINS_CR_VMIN_K_HVBICPU_X_X_X_X_TEST'): ['MAIN', 'TPI_BASE_XXX::TPI_BASE_XXX_HVBICPU'],  # error: pkg module with ipcpu subflow
                         ('TPI_BASE_IPCPU', 'EVMINS_CR_VMIN_K_PREPRLCPUGT_X_X_X_X_TEST'): ['MAIN', 'TPI_BASE_IPCPU::TPI_BASE_IPCPU_PREPRLCPUGT'],  # valid: ipcpu module with pkg subflow, select INFRA only
                         ('TPI_BASE_IPPCH', 'EVMINS_CR_VMIN_K_PREPRLCPUGT_X_X_X_X_TEST'): ['MAIN', 'TPI_BASE_IPPCH::TPI_BASE_IPPCH_PREPRLCPUGT'],  # valid: ippch module with pkg subflow, select INFRA only
                         ('DRV_RESET_SXN', 'EVMINS_CR_VMIN_K_HVBICPU_X_X_X_X_TEST'): ['MAIN', 'DRV_RESET_SXN::DRV_RESET_SXN_HVBICPU'],  # valid: DRV_RESET_SXN PKG module inside IP_ HVBI subflows
                         ('TPI_DIESLCT_XXX', 'EVMINS_CR_VMIN_K_HVBICPU_X_X_X_X_TEST'): ['MAIN', 'TPI_DIESLCT_XXX::TPI_DIESLCT_XXX_HVBICPU'],  # valid: TPI_DIESLCT_XXX PKG module inside IP_ HVBI subflows
                         ('TPI_EDM_XXX', 'EVMINS_CR_VMIN_K_THRFF_X_X_X_X_TEST'): ['MAIN', 'TPI_EDM_XXX::TPI_EDM_XXX_THRFF'],  # valid: TPI_EDM_XXX pkg module in pkg subflow, basic check
                         ('TPI_FUSEDRNG_SXX', 'DRNG_SOC_FUNC_K_BEGSOC_X_X_X_X_TEST'): ['MAIN', 'TPI_FUSEDRNG_SXX::TPI_FUSEDRNG_SXX_BEGSOC'],  # valid: pkg module in pkg subflow
                         ('TPI_FUSEDRNG_SXX', 'DRNG_SOC_FUNC_K_BEGCPU_X_X_X_X_TEST'): ['MAIN', 'TPI_FUSEDRNG_SXX::TPI_FUSEDRNG_SXX_BEGCPU'],  # error: pkg module in ip_ subflow
                         ('TPI_BASE_XXX', 'EVMINS_CLR_FUNC_K_MAXCLR_X_X_X_X_TEST'): ['MAIN', 'TPI_BASE_XXX::TPI_BASE_XXX_MAXCLR'],  # error: TPI_BASE_XXX pkg module in ip_ subflow
                         ('FUN_CORE_CXX', 'DRNG_CR_FUNC_K_DEBUGX_X_X_X_X_TEST'): ['MAIN', 'FUN_CORE_CXX::FUN_CORE_CXX_DEBUGX']  # error: module subflow in name matches placement but invalid subflow
                         }
            obj = Checkers()
            obj.run_check(obj.gen_testplacechk, True, testtrace, ipcpuflows, ippchflows, pkgflows, ipcpu, ippch)
            self.assertEqual(obj.sum[obj.gen_testplacechk], {'ARR_CORE_CXX': {'e': 1, 'w': 0, 'p': 0},
                                                             'DRV_RESET_SXN': {'e': 0, 'w': 0, 'p': 0},
                                                             'FUN_CORE_CXX': {'e': 2, 'w': 0, 'p': 0},
                                                             'PSCN_SCN_IXX': {'e': 2, 'w': 0, 'p': 0},
                                                             'TPI_BASE_IPCPU': {'e': 0, 'w': 0, 'p': 0},
                                                             'TPI_BASE_IPPCH': {'e': 0, 'w': 0, 'p': 0},
                                                             'TPI_BASE_XXX': {'e': 2, 'w': 0, 'p': 0},
                                                             'TPI_DIESLCT_XXX': {'e': 0, 'w': 0, 'p': 0},
                                                             'TPI_EDM_XXX': {'e': 0, 'w': 0, 'p': 0},
                                                             'TPI_FUSEDRNG_SXX': {'e': 1, 'w': 0, 'p': 0}
                                                             })
            self.assertEqual(obj.msgstr, ['FUN_CORE_CXX -Error124- Test:EVMINS_CR_VMIN_K_BEGGT_X_X_X_X_TEST is IP_CPU scope but is placed in subflow:BEGGT that is for IP_PCH testing',
                                          'PSCN_SCN_IXX -Error125- Test:EVMINS_CR_VMIN_K_BEGCPU_X_X_X_X_TEST is IP_PCH scope but is placed in subflow:BEGCPU that is for IP_CPU testing',
                                          'ARR_CORE_CXX -Error148- Test:EVMINS_CR_VMIN_K_BEGCPUPKG_X_X_X_X_TEST is IP_CPU scope but is placed in subflow:BEGCPUPKG that is for PKG testing',
                                          'PSCN_SCN_IXX -Error149- Test:EVMINS_CR_VMIN_K_BEGIOEPKG_X_X_X_X_TEST is IP_PCH scope but is placed in subflow:BEGIOEPKG that is for PKG testing',
                                          'TPI_BASE_XXX -Error126- Test:EVMINS_CR_VMIN_K_HVBICPU_X_X_X_X_TEST is PKG scope but is placed in subflow:HVBICPU that is not valid for PKG testing',
                                          'TPI_FUSEDRNG_SXX -Error126- Test:DRNG_SOC_FUNC_K_BEGCPU_X_X_X_X_TEST is PKG scope but is placed in subflow:BEGCPU that is not valid for PKG testing',
                                          'TPI_BASE_XXX -Error126- Test:EVMINS_CLR_FUNC_K_MAXCLR_X_X_X_X_TEST is PKG scope but is placed in subflow:MAXCLR that is not valid for PKG testing',
                                          'FUN_CORE_CXX -Error127- Test:DRNG_CR_FUNC_K_DEBUGX_X_X_X_X_TEST inside invalid subflow:DEBUGX that might be currently in use for debug'
                                          ])

    def test_mtl_socinfrachk(self):
        with TempDir(name=True, chdir=True) as tdir:
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)

            ipcpu = {'ARR_CORE_CXX', 'FUN_CORE_CXX'}
            ippch = {'PSCN_SCN_IXX'}

            # most cases are tested from using the small checkersTP/TPL
            obj = Checkers()
            obj.run_check(obj.mtl_socinfrachk, True, 'ARR_CORE_CXXP', 'EVMINS_CR_VMIN_K_BEGCPU_X_X_X_X_TEST', 'ExecuteInstance(--test DRV_RESET_SXN::RESET_X_FUNC_K_INFCPU_X_VNNAON_X_X_SOCINFRA_CPUGT)', ipcpu, ippch, 'some_list')  # basic cpu pass
            obj.run_check(obj.mtl_socinfrachk, True, 'ARR_GT_CXXP', 'EVMINS_CR_VMIN_K_BEGGT_X_X_X_X_TEST', 'ExecuteInstance(--test DRV_RESET_SXN::RESET_X_FUNC_K_INFGT_X_VNNAON_X_X_SOCINFRA_CPUGT)', ipcpu, ippch, 'some_list')  # basic gt pass
            obj.run_check(obj.mtl_socinfrachk, True, 'ARR_IOE_CXXP', 'EVMINS_CR_VMIN_K_BEGIOE_X_X_X_X_TEST', 'ExecuteInstance(--test DRV_RESET_SXN::RESET_X_FUNC_K_INFIOE_X_VNNAON_X_X_SOCINFRA_IOE)', ipcpu, ippch, 'some_list')  # basic ioe pass
            obj.run_check(obj.mtl_socinfrachk, True, 'ARR_IOE_CXXP', 'EVMINS_CR_VMIN_K_BEGIOE_X_X_X_X_TEST2', 'ExecuteInstance(--test DRV_RESET_SXN::RESET_X_FUNC_K_INFCPUIOE_X_VNNAON_X_X_SOCINFRA_CPUIOE)', ipcpu, ippch, 'some_list')  # basic cpuioe pass
            obj.run_check(obj.mtl_socinfrachk, True, 'ARR_CORE_CXXP', 'EVMINS_CR_VMIN_K_BEGCPU_X_X_X_X_TEST', 'ExecuteInstance(--test DRV_RESET_CHE::RESET_X_FUNC_K_INFCPU_X_VNNAON_X_X_SOCINFRA_CPUGT)', ipcpu, ippch, 'some_list')  # si not in list
            obj.run_check(obj.mtl_socinfrachk, True, 'ARR_CORE_CXXP', 'EVMINS_CR_AUX_K_ENDCPU_X_X_X_X_TEST', 'ExecuteInstance(--test DRV_RESET_SXN::RESET_X_FUNC_K_INFCPU_X_VNNAON_X_X_SOCINFRA_CPUGT)', ipcpu, ippch, '')  # test without plt calling socinfra warning
            obj.run_check(obj.mtl_socinfrachk, True, 'ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_BEGCPU_X_X_X_X_TEST', 'ExecuteInstance(--test DRV_RESET_SXN::RESET_X_FUNC_K_INFCPU_X_VNNAON_X_X_SOCINFRA_CPUGT)', ipcpu, ippch, 'some_list')  # ipcpu test calling pkg soc infra
            obj.run_check(obj.mtl_socinfrachk, True, 'PSCN_SCN_IXX', 'EVMINS_CR_VMIN_K_BEGCPU_X_X_X_X_TEST', 'ExecuteInstance(--test DRV_RESET_SXN::RESET_X_FUNC_K_INFCPU_X_VNNAON_X_X_SOCINFRA_CPUGT)', ipcpu, ippch, 'some_list')  # ippch test calling pkg soc infra
            with self.assertRaisesRegex(ErrorCheck, 'SOC Infra UF was used but unable to parse'):
                obj.run_check(obj.mtl_socinfrachk, True, 'ARR_CORE_CXXP', 'EVMINS_CR_VMIN_K_BEGCPU_X_X_X_X_TEST', 'ExecuteInstance(--testDRV_RESET_SXN::RESET_X_FUNC_K_INFCPU_X_VNNAON_X_X_SOCINFRA_CPU)', ipcpu, ippch, 'some_list')  # unable to parse soc infra
            self.assertEqual(obj.sum[obj.mtl_socinfrachk], {'ARR_CORE_CXX': {'e': 1, 'w': 0, 'p': 0},
                                                            'ARR_CORE_CXXP': {'e': 1, 'w': 0, 'p': 0},
                                                            'ARR_GT_CXXP': {'e': 0, 'w': 0, 'p': 0},
                                                            'ARR_IOE_CXXP': {'e': 0, 'w': 0, 'p': 0},
                                                            'PSCN_SCN_IXX': {'e': 1, 'w': 0, 'p': 0}
                                                            })
            self.assertEqual(obj.msgstr, ['ARR_CORE_CXXP -Error129- Test:EVMINS_CR_VMIN_K_BEGCPU_X_X_X_X_TEST preinstance:ExecuteInstance(--test DRV_RESET_CHE::RESET_X_FUNC_K_INFCPU_X_VNNAON_X_X_SOCINFRA_CPUGT) is using an invalid SOC INFRA:DRV_RESET_CHE::RESET_X_FUNC_K_INFCPU_X_VNNAON_X_X_SOCINFRA_CPUGT',
                                          'ARR_CORE_CXX -Error130- Test:EVMINS_CR_VMIN_K_BEGCPU_X_X_X_X_TEST Invalid call of socinfra, IP_CPU test calling a PKG test:DRV_RESET_SXN::RESET_X_FUNC_K_INFCPU_X_VNNAON_X_X_SOCINFRA_CPUGT',
                                          'PSCN_SCN_IXX -Error131- Test:EVMINS_CR_VMIN_K_BEGCPU_X_X_X_X_TEST Invalid call of socinfra, IP_PCH test calling a PKG test:DRV_RESET_SXN::RESET_X_FUNC_K_INFCPU_X_VNNAON_X_X_SOCINFRA_CPUGT'
                                          ])

    def test_mtl_locinfrachk(self):
        with TempDir(name=True, chdir=True) as tdir:
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)

            obj = Checkers()
            obj.run_check(obj.mtl_locinfrachk, False, 'DRV_RESET_SXN', 'RESET_X_FUNC_K_INFCPU_X_VNNAON_X_X_SOCINFRA_CPUGT', 'infcpugt_list', '_pkg_level', 'soc_timings')  # basic pass INFCPU
            obj.run_check(obj.mtl_locinfrachk, False, 'DRV_RESET_SXN', 'RESET_X_FUNC_K_INFGT_X_VNNAON_X_X_SOCINFRA_CPUGT', 'infcpugt_list', '_pkg_level', 'soc_timings')  # basic pass INFGT
            obj.run_check(obj.mtl_locinfrachk, False, 'DRV_RESET_SXN', 'RESET_X_FUNC_K_INFIOE_X_VNNAON_X_X_SOCINFRA_IOE', 'infioe_list', '_pkg_level', 'soc_timings')  # basic pass INFIOE
            obj.run_check(obj.mtl_locinfrachk, False, 'DRV_RESET_SXN', 'RESET_X_FUNC_K_INFCPUIOE_X_VNNAON_X_X_SOCINFRA_CPUIOE', 'infcpuioe_list', '_pkg_level', 'soc_timings')  # basic pass INFCPUIOE, out of order request
            obj.run_check(obj.mtl_locinfrachk, False, 'DRV_RESET_SXN', 'RESET_X_FUNC_K_INFIOE_X_VNNAON_X_X_BABYSTEP', 'patlist', 'level', 'timings')  # non-infra test
            self.assertEqual(obj.cfg['sum_locinfrachk'], {'DRV_RESET_SXN::RESET_X_FUNC_K_INFCPU_X_VNNAON_X_X_SOCINFRA_CPUGT': {'att': 'present', 'p': 'infcpugt_list', 'l': '_pkg_level', 't': 'soc_timings'},
                                                          'DRV_RESET_SXN::RESET_X_FUNC_K_INFGT_X_VNNAON_X_X_SOCINFRA_CPUGT': {'att': 'present', 'p': 'infcpugt_list', 'l': '_pkg_level', 't': 'soc_timings'},
                                                          'DRV_RESET_SXN::RESET_X_FUNC_K_INFIOE_X_VNNAON_X_X_SOCINFRA_IOE': {'att': 'present', 'p': 'infioe_list', 'l': '_pkg_level', 't': 'soc_timings'},
                                                          'DRV_RESET_SXN::RESET_X_FUNC_K_INFCPUIOE_X_VNNAON_X_X_SOCINFRA_CPUIOE': {'att': 'present', 'p': 'infcpuioe_list', 'l': '_pkg_level', 't': 'soc_timings'}
                                                          })

    def test_mtl_cntinfrachk(self):
        with TempDir(name=True, chdir=True) as tdir:
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)

            valid_si = {'DRV_RESET_SXN::RESET_X_FUNC_K_INFCPU_X_VNNAON_X_X_SOCINFRA_CPUGT': {'att': 'absent', 'p': '', 'l': '', 't': ''},
                        'DRV_RESET_SXN::RESET_X_FUNC_K_INFGT_X_VNNAON_X_X_SOCINFRA_CPUGT': {'att': 'absent', 'p': '', 'l': '', 't': ''},
                        'DRV_RESET_SXN::RESET_X_FUNC_K_INFIOE_X_VNNAON_X_X_SOCINFRA_IOE': {'att': 'absent', 'p': '', 'l': '', 't': ''},
                        'DRV_RESET_SXN::RESET_X_FUNC_K_INFCPUIOE_X_VNNAON_X_X_SOCINFRA_CPUIOE': {'att': 'absent', 'p': '', 'l': '', 't': ''}}
            locinfrchk = {'DRV_RESET_SXN::RESET_X_FUNC_K_INFCPU_X_VNNAON_X_X_SOCINFRA_CPUGT': {'att': 'present', 'p': 'infcpugt_list', 'l': 'lvl', 't': 'tim'},
                          'DRV_RESET_SXN::RESET_X_FUNC_K_INFGT_X_VNNAON_X_X_SOCINFRA_CPUGT': {'att': 'absent', 'p': 'infcpugt_list', 'l': 'lvl', 't': 'tim'},
                          'DRV_RESET_SXN::RESET_X_FUNC_K_INFIOE_X_VNNAON_X_X_SOCINFRA_IOE': {'att': 'present', 'p': 'infioe_list', 'l': 'lvl', 't': 'tim'},
                          'DRV_RESET_SXN::RESET_X_FUNC_K_INFCPUIOE_X_VNNAON_X_X_SOCINFRA_CPUIOE': {'att': 'present', 'p': 'infioe_list', 'l': 'lvl', 't': 'tim'}}
            obj = Checkers()
            obj.run_check(obj.mtl_cntinfrachk, True, valid_si, locinfrchk)
            self.assertEqual(obj.sum[obj.mtl_cntinfrachk], {'DRV_RESET_SXN': {'e': 1, 'w': 0, 'p': 3}})
            self.assertEqual(obj.msgstr, ['DRV_RESET_SXN -Error133- SOC INFRA test:DRV_RESET_SXN::RESET_X_FUNC_K_INFGT_X_VNNAON_X_X_SOCINFRA_CPUGT is missing'])

    def test_gen_tlchk(self):
        with TempDir(name=True, chdir=True) as tdir:
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)

            ipcpu = {'ARR_CORE_CXX', 'FUN_CORE_CXX'}
            ippch = {'PSCN_SCN_IXX'}
            obj = Checkers()
            obj.run_check(obj.gen_tlchk, True, 'ARR_CORE_CXXP', 'EVMINS_CR_VMIN_K_BEGCPU_X_X_X_X_TEST', ipcpu, ippch)  # PKG pass
            obj.run_check(obj.gen_tlchk, True, 'ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_BEGCPU_X_X_X_X_TEST', ipcpu, ippch)  # IP_CPU pass
            obj.run_check(obj.gen_tlchk, True, 'PSCN_SCN_IXX', 'EVMINS_CR_VMIN_K_BEGCPU_X_X_X_X_TEST', ipcpu, ippch)  # IP_PCH pass
            obj.run_check(obj.gen_tlchk, True, 'TPI_IDUTFORK_XXX', 'EVMINS_CR_VMIN_K_HVBIGT_X_X_X_X_TEST', ipcpu, ippch)  # PKG on IP_PCH flow, valid ignore
            obj.run_check(obj.gen_tlchk, True, 'TPI_IDUTFORK_XXX', 'EVMINS_CR_VMIN_K_HVBICPU_X_X_X_X_TEST', ipcpu, ippch)  # PKG on IP_CPU flow, valid ignore
            obj.run_check(obj.gen_tlchk, True, 'ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_BEGCPU_X_X_X_X_TEST_VERY_LOOOOOOOOOOOOOOOOONNNNNGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG_NAME', ipcpu, ippch)  # IP_CPU fail
            self.assertEqual(obj.sum[obj.gen_tlchk], {'ARR_CORE_CXX': {'e': 1, 'w': 0, 'p': 0},
                                                      'ARR_CORE_CXXP': {'e': 0, 'w': 0, 'p': 0},
                                                      'PSCN_SCN_IXX': {'e': 0, 'w': 0, 'p': 0},
                                                      'TPI_IDUTFORK_XXX': {'e': 0, 'w': 0, 'p': 0}
                                                      })
            self.assertEqual(obj.msgstr, ['ARR_CORE_CXX -Error132- Test: IP_CPU::ARR_CORE_CXX::EVMINS_CR_VMIN_K_BEGCPU_X_X_X_X_TEST_VERY_LOOOOOOOOOOOOOOOOONNNNNGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG_NAME length:132 is over the allowed limit:100 characters'])

    def test_mtl_ctrlrstchk(self):
        with TempDir(name=True, chdir=True) as tdir:
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)
            modpatch = {'arr': ['ARR_CORE', 'ARR_RING'],
                        'scn': ['SCN_CORE', 'SCN_RING'],
                        'aaadrv': ['DRV_RESET_CXX', 'DRV_RESET_XXX', 'ARR_CORE'],
                        'cccdrv': ['DRV_RESET_GXX', 'ARR_CORE']
                        }
            obj = Checkers()
            obj.run_check(obj.mtl_ctrlrstchk, True, modpatch)
            self.assertEqual(obj.sum[obj.mtl_ctrlrstchk], {'ARR_CORE': {'e': 2, 'w': 0, 'p': 0}})
            self.assertEqual(obj.msgstr, ['ARR_CORE -Error134- Module:ARR_CORE is not from DRV but is using a drv patch:aaadrv!',
                                          'ARR_CORE -Error134- Module:ARR_CORE is not from DRV but is using a drv patch:cccdrv!'])

    def test_mtl_bannedchk(self):
        with TempDir(name=True, chdir=True) as tdir:
            stpldata = [('ARR_RING_CXX', 'EVMINS_CLR_VMIN_K_BEGCPU_X_X_X_X_TEST1', {'TEMPLATE': 'VminTC', 'BypassPort': '1'}, ''),
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_BEGCPU_X_X_X_X_TEST2', {'TEMPLATE': 'VminTC', 'BypassPort': '1'}, ''),
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_BEGCPU_X_X_X_X_TEST2A', {'TEMPLATE': 'VminTC', 'preplist': 'VDAC!SetVDAC CORES:0.65'}, ''),
                        ('ARR_RING_CXX', 'EVMINS_CLR_VMIN_K_BEGCPU_X_X_X_X_TEST3', {'TEMPLATE': 'iCShmooTest', 'bypass_global': '1'}, ''),
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_BEGCPU_X_X_X_X_TEST4', {'TEMPLATE': 'iCFASTTest', 'bypass_global': '-1'}, ''),
                        ('ARR_CORE_CXX', 'FlowControl', {'TEMPLATE': 'iCBinMatrixFlowControlTest', 'loop_mode': 'VLOOP'}, ''),
                        ('ARR_CORE_CXX', 'SetFlowInfo_Flow2', {'TEMPLATE': 'iCBinMatrixFlowControlTest', 'invalid_flows': '1'}, ''),
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_BEGCPU_X_X_X_X_TEST5', {'TEMPLATE': 'iCAuxiliaryTest', 'bypass_global': '-1', 'ifpm_input_file': 'file1.txt', 'ifpm_modifygroups': 'patmod'}, ''),
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_BEGCPU_X_X_X_X_TEST6', {'TEMPLATE': 'iCGlXpressTest', 'gl_xpress_file_path': './Modules/ARR_CORE_CXX/pgmRules01.txt'}, ''),
                        ('ARR_RING_CXX', 'EVMINS_CLR_PATMOD_K_INIT_X_X_X_X_INIT', {'TEMPLATE': 'iCPatternModifyTest', 'bypass_global': '-1'}, '')
                        ]
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)
            obj = Checkers()
            obj.run_check(obj.mtl_bannedchk, True, stpldata)
            # TODO: Enable Warning to Error conversion
            self.assertEqual(obj.sum[obj.mtl_bannedchk], {'ARR_CORE_CXX': {'e': 6, 'w': 0, 'p': 0},
                                                          'ARR_RING_CXX': {'e': 2, 'w': 0, 'p': 0}})
            self.assertEqual(obj.msgstr, ['ARR_CORE_CXX -Error141- Test:EVMINS_CR_VMIN_K_BEGCPU_X_X_X_X_TEST2A has illegal VDAC_UF call in param:preplist=VDAC!SetVDAC CORES:0.65!',
                                          'ARR_RING_CXX -Error136- Test:EVMINS_CLR_VMIN_K_BEGCPU_X_X_X_X_TEST3 uses illegal shmoo template:iCShmooTest!',
                                          'ARR_CORE_CXX -Error137- Test:EVMINS_CR_VMIN_K_BEGCPU_X_X_X_X_TEST4 uses illegal vmin template:iCFASTTest!',
                                          'ARR_CORE_CXX -Error140- Test:FlowControl uses illegal bmfc template:iCBinMatrixFlowControlTest!',
                                          'ARR_CORE_CXX -Error140- Test:SetFlowInfo_Flow2 uses illegal bmfc template:iCBinMatrixFlowControlTest!',
                                          'ARR_CORE_CXX -Error135- Test:EVMINS_CR_VMIN_K_BEGCPU_X_X_X_X_TEST5 uses illegal ifpm param:ifpm_input_file=file1.txt!',
                                          'ARR_CORE_CXX -Error135- Test:EVMINS_CR_VMIN_K_BEGCPU_X_X_X_X_TEST5 uses illegal ifpm param:ifpm_modifygroups=patmod!',
                                          'ARR_RING_CXX -Error146- Test:EVMINS_CLR_PATMOD_K_INIT_X_X_X_X_INIT uses illegal patmod template:iCPatternModifyTest!'
                                          ])

    def test_gen_badbuildchk(self):
        with TempDir(name=True, chdir=True) as tdir:
            stpldata = [('ARR_RING_CXX', 'EVMINS_CLR_VMIN_K_BEGCPU_X_X_X_X_TEST1', {'TEMPLATE': 'VminTC', 'BypassPort': '1'}, ''),
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_BEGCPU_X_X_X_X_TEST2', {'TEMPLATE': 'VminTC', 'BypassPort': '{BYPASS_PORT}'}, '')
                        ]
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)
            obj = CheckersUT()
            obj.run_check(obj.gen_badbuildchk, True, stpldata)
            self.assertEqual(obj.sum[obj.gen_badbuildchk], {'ARR_CORE_CXX': {'e': 1, 'w': 0, 'p': 0},
                                                            'ARR_RING_CXX': {'e': 0, 'w': 0, 'p': 0}})
            self.assertEqual(obj.msgstr, ['ARR_CORE_CXX -Error147- Test:EVMINS_CR_VMIN_K_BEGCPU_X_X_X_X_TEST2 has param:BypassPort={BYPASS_PORT} that was not converted by TPIE!'])

    def test_mtl_relaytokenchk(self):
        with TempDir(name=True, chdir=True) as tdir:
            stpldata = [('ARR_RING_CXX', 'EVMINS_CLR_VMIN_K_BEGCPU_X_X_X_X_TEST1', {'TEMPLATE': 'FUNC', 'BypassPort': '1'}, ''),
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_BEGCPU_X_X_X_X_TEST2', {'TEMPLATE': 'SCOREBOARD', 'relay_token': 'tp_default'}, ''),
                        ('FUN_CORE_CXX', 'EVMINS_CR_VMIN_K_BEGCPU_X_X_X_X_TEST3', {'TEMPLATE': 'SCOREBOARD', 'relay_token': 'tp_default!'}, ''),
                        ('SCN_CORE_CXX', 'EVMINS_CR_VMIN_K_BEGCPU_X_X_X_X_TEST4', {'TEMPLATE': 'SCOREBOARD', 'relay_token': ''}, '')
                        ]
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)
            obj = CheckersUT()
            obj.run_check(obj.mtl_relaytokenchk, True, stpldata)
            self.assertEqual(obj.sum[obj.mtl_relaytokenchk], {'ARR_CORE_CXX': {'e': 1, 'w': 0, 'p': 0},
                                                              'ARR_RING_CXX': {'e': 0, 'w': 0, 'p': 0},
                                                              'FUN_CORE_CXX': {'e': 1, 'w': 0, 'p': 0},
                                                              'SCN_CORE_CXX': {'e': 1, 'w': 0, 'p': 0}})
            self.assertEqual(obj.msgstr, ['ARR_CORE_CXX -Error150- Test:EVMINS_CR_VMIN_K_BEGCPU_X_X_X_X_TEST2 illegal use of relay_token=tp_default',
                                          'FUN_CORE_CXX -Error150- Test:EVMINS_CR_VMIN_K_BEGCPU_X_X_X_X_TEST3 illegal use of relay_token=tp_default!',
                                          'SCN_CORE_CXX -Error150- Test:EVMINS_CR_VMIN_K_BEGCPU_X_X_X_X_TEST4 illegal use of relay_token='
                                          ])

    def test_gen_reqdfileschk(self):
        with TempDir(name=True, chdir=True) as tdir:
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)
            reqdfiles = ['./Reports/LTL_Files.zip', './VERY_IMPORTANT_FILE.txt', './Reports/LTL_Files.zip']  # important file for ut only

            File('./Reports/LTL_Files.zip').touch('', mkdir=True, newfile=True)
            # do not create the VERY_IMPORTANT_FILE which should trigger in the report
            obj = Checkers()
            obj.run_check(obj.gen_reqdfileschk, True, reqdfiles)
            self.assertEqual(obj.sum[obj.gen_reqdfileschk], {'./Reports/LTL_Files.zip': {'e': 0, 'w': 0, 'p': 0},
                                                             './VERY_IMPORTANT_FILE.txt': {'e': 1, 'w': 0, 'p': 0}})
            self.assertEqual(obj.msgstr, ['ReqdFile -Error151- File:./VERY_IMPORTANT_FILE.txt is MISSING! HVM quality is compromised!'])

    def test_mtl_ipminlvlchk(self):
        with TempDir(name=True, chdir=True) as tdir:
            ipcpu = {'ARR_CORE_CXX'}
            ippch = {'ARR_GT_GXX'}
            srhchkflows = ['SGTF1', 'CGTF1', 'SCRF1', 'CCRF1']
            stpldata = [('ARR_GT_GXX', 'EVMINS_GT_VMIN_K_SGTF1_X_X_X_X_TEST1_1001', {'TEMPLATE': 'FUNC', 'LevelsTc': 'gcd_all_bf_x_x_ippch_lvl_min_lvl'}, ''),  # prime pass: ip_pch everywhere speedflow
                        ('ARR_GT_GXX', 'EVMINS_GT_VMIN_K_SGTF1_X_X_X_X_TEST1', {'TEMPLATE': 'FUNC', 'LevelsTc': 'gcd_all_bf_x_x_ippch_lvl_min_lvl'}, ''),  # prime pass: ip_pch everywhere
                        ('ARR_GT_GXX', 'EVMINS_GT_VMIN_K_SGTF1_X_X_X_X_TEST2', {'TEMPLATE': 'FUNC', 'LevelsTc': 'gcd_all_bf_x_x_pkg_lvl_min_lvl'}, ''),  # prime fail: ip_pch test with pkg lvl
                        ('ARR_GT_GXX', 'EVMINS_GT_VMIN_K_SGTF1_X_X_X_X_TEST3', {'TEMPLATE': 'FUNC', 'LevelsTc': 'gcd_all_bf_x_x_ipcpu_lvl_min_lvl'}, ''),  # prime fail: ip_pch test with ipcpu lvl
                        ('ARR_GT_GXX', 'EVMINS_GT_VMIN_K_BEGGT_X_X_X_X_TEST1', {'TEMPLATE': 'FUNC', 'LevelsTc': 'gcd_all_bf_x_x_ippch_lvl_nom_lvl'}, ''),  # prime ignore, BEGGT with ip_pch nom lvl
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_SCRF1_X_X_X_X_TEST1_1001', {'TEMPLATE': 'FUNC', 'LevelsTc': 'cpu_all_bf_x_x_ipcpu_lvl_min_lvl'}, ''),  # prime pass: ip_cpu everywhere speedflow
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_SCRF1_TESTX', {'TEMPLATE': 'FUNC', 'LevelsTc': 'cpu_all_bf_x_x_ipcpu_lvl_min_lvl'}, ''),  # prime pass: ip_cpu everywhere testname is short
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_SCRF1_X_X_X_X_TEST1', {'TEMPLATE': 'FUNC', 'LevelsTc': 'cpu_all_bf_x_x_ipcpu_lvl_min_lvl'}, ''),  # prime pass: ip_cpu everywhere
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_SCRF1_X_X_X_X_TEST2', {'TEMPLATE': 'FUNC', 'LevelsTc': 'cpu_all_bf_x_x_pkg_lvl_min_lvl'}, ''),  # prime fail: ip_cpu test with pkg lvl
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_SCRF1_X_X_X_X_TEST3', {'TEMPLATE': 'FUNC', 'LevelsTc': 'cpu_all_bf_x_x_ippch_lvl_min_lvl'}, ''),  # prime fail: ip_cpu test with ippch lvl
                        ('ARR_GT_GXX', 'EVMINS_GT_VMIN_K_CGTF1_X_X_X_X_TEST1', {'TEMPLATE': 'FUNC', 'level': 'gcd_all_bf_x_x_ippch_lvl_min_lvl'}, ''),  # evg pass: ip_pch everywhere
                        ('ARR_GT_GXX', 'EVMINS_GT_VMIN_K_CGTF1_X_X_X_X_TEST2', {'TEMPLATE': 'FUNC', 'level': 'gcd_all_bf_x_x_pkg_lvl_min_lvl'}, ''),  # evg fail: ip_pch test with pkg lvl
                        ('ARR_GT_GXX', 'EVMINS_GT_VMIN_K_CGTF1_X_X_X_X_TEST3', {'TEMPLATE': 'FUNC', 'level': 'gcd_all_bf_x_x_ipcpu_lvl_min_lvl'}, ''),  # evg fail: ip_pch test with ipcpu lvl
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF1_X_X_X_X_TEST1', {'TEMPLATE': 'FUNC', 'level': 'cpu_all_bf_x_x_ipcpu_lvl_min_lvl'}, ''),  # evg pass: ip_cpu everywhere
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF1_X_X_X_X_TEST2', {'TEMPLATE': 'FUNC', 'level': 'cpu_all_bf_x_x_pkg_lvl_min_lvl'}, ''),  # evg fail: ip_cpu test with pkg lvl
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF1_X_X_X_X_TEST3', {'TEMPLATE': 'FUNC', 'level': 'cpu_all_bf_x_x_ippch_lvl_min_lvl'}, ''),  # evg fail: ip_cpu test with ippch lvl
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_SCRF1_X_X_X_X_TEST9', {'TEMPLATE': 'SCOREBOARD', 'relay_token': 'tp_default'}, ''),  # levels = None
                        ('ARR_CORE_CXX', 'TEST_FAIL', {'TEMPLATE': 'FUNC', 'level': 'cpu_all_bf_x_x_ipcpu_lvl_min_lvl'}, ''),  # bad test name, nyet scenario
                        ('TPI_EVMINS_YXX', 'EVMINS_SOC_VMIN_K_SCRF1_X_X_X_X_TEST1', {'TEMPLATE': 'FUNC', 'LevelsTc': 'soc_all_bf_x_x_pkg_lvl_min_lvl'}, '')  # prime fail: pkg module + ip subflow + pkg min lvl
                        ]

            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)
            obj = Checkers()
            obj.run_check(obj.mtl_ipminlvlchk, False, stpldata, srhchkflows, ipcpu, ippch)
            self.assertEqual(obj.sum[obj.mtl_ipminlvlchk], {'ARR_CORE_CXX': {'e': 0, 'w': 4, 'p': 0},
                                                            'ARR_GT_GXX': {'e': 0, 'w': 4, 'p': 0},
                                                            'TPI_EVMINS_YXX': {'e': 0, 'w': 1, 'p': 0}
                                                            })
            self.assertEqual(obj.msgstr, ['ARR_GT_GXX -Warning153- Test:EVMINS_GT_VMIN_K_SGTF1_X_X_X_X_TEST2 is not using *ippch_lvl_min_lvl! (level=gcd_all_bf_x_x_pkg_lvl_min_lvl)',
                                          'ARR_GT_GXX -Warning153- Test:EVMINS_GT_VMIN_K_SGTF1_X_X_X_X_TEST3 is not using *ippch_lvl_min_lvl! (level=gcd_all_bf_x_x_ipcpu_lvl_min_lvl)',
                                          'ARR_CORE_CXX -Warning152- Test:EVMINS_CR_VMIN_K_SCRF1_X_X_X_X_TEST2 is not using *ipcpu_lvl_min_lvl! (level=cpu_all_bf_x_x_pkg_lvl_min_lvl)',
                                          'ARR_CORE_CXX -Warning152- Test:EVMINS_CR_VMIN_K_SCRF1_X_X_X_X_TEST3 is not using *ipcpu_lvl_min_lvl! (level=cpu_all_bf_x_x_ippch_lvl_min_lvl)',
                                          'ARR_GT_GXX -Warning153- Test:EVMINS_GT_VMIN_K_CGTF1_X_X_X_X_TEST2 is not using *ippch_lvl_min_lvl! (level=gcd_all_bf_x_x_pkg_lvl_min_lvl)',
                                          'ARR_GT_GXX -Warning153- Test:EVMINS_GT_VMIN_K_CGTF1_X_X_X_X_TEST3 is not using *ippch_lvl_min_lvl! (level=gcd_all_bf_x_x_ipcpu_lvl_min_lvl)',
                                          'ARR_CORE_CXX -Warning152- Test:EVMINS_CR_VMIN_K_CCRF1_X_X_X_X_TEST2 is not using *ipcpu_lvl_min_lvl! (level=cpu_all_bf_x_x_pkg_lvl_min_lvl)',
                                          'ARR_CORE_CXX -Warning152- Test:EVMINS_CR_VMIN_K_CCRF1_X_X_X_X_TEST3 is not using *ipcpu_lvl_min_lvl! (level=cpu_all_bf_x_x_ippch_lvl_min_lvl)',
                                          'TPI_EVMINS_YXX -Warning154- Test:EVMINS_SOC_VMIN_K_SCRF1_X_X_X_X_TEST1 subflow=SCRF1 & lvl=soc_all_bf_x_x_pkg_lvl_min_lvl IP_ combo error'])

    def test_mtl_flowdomainchk(self):
        with TempDir(name=True, chdir=True) as tdir:
            stpldata = [('TPI_EVMINS_YXXK', 'FlowControl_ATOMC', {'TEMPLATE': 'PrimeFlowControlForkTestMethod', 'DomainName': 'ATOMC'}, ''),
                        ('TPI_EVMINS_YXXK', 'SetFlowInfo_ATOMC_Flow1', {'TEMPLATE': 'PrimeFlowControlSetTestMethod', 'DomainName': 'ATOMC'}, ''),
                        ('TPI_EVMINS_CXX', 'SetFlowInfo_CORE_Flow1', {'TEMPLATE': 'PrimeFlowControlSetTestMethod', 'DomainName': 'CORE'}, ''),
                        ('TPI_EVMINS_CXX', 'FlowControl_CORE', {'TEMPLATE': 'PrimeFlowControlForkTestMethod', 'DomainName': 'CORE'}, ''),
                        ('TPI_EVMINS_YXXK', 'FlowControl_RING', {'TEMPLATE': 'PrimeFlowControlForkTestMethod', 'DomainName': 'RING'}, ''),
                        ('TPI_EVMINS_YXXK', 'FlowControl_GT', {'TEMPLATE': 'PrimeFlowControlForkTestMethod', 'DomainName': 'GT'}, ''),
                        ('TPI_EVMINS_YXXK', 'FlowControl_SOC', {'TEMPLATE': 'PrimeFlowControlForkTestMethod', 'DomainName': 'SOC'}, ''),
                        ('TPI_EVMINS_YXXK', 'FlowControl_ATOMC_EDC', {'TEMPLATE': 'PrimeFlowControlForkTestMethod', 'DomainName': 'ATOMC_EDC'}, ''),
                        ('TPI_EVMINS_YXXK', 'FlowControl_CORE_EDC', {'TEMPLATE': 'PrimeFlowControlForkTestMethod', 'DomainName': 'CORE_EDC'}, ''),
                        ('TPI_EVMINS_YXXK', 'FlowControl_RING_EDC', {'TEMPLATE': 'PrimeFlowControlForkTestMethod', 'DomainName': 'RING_EDC'}, ''),
                        ('TPI_EVMINS_YXXK', 'FlowControl_GT_EDC', {'TEMPLATE': 'PrimeFlowControlForkTestMethod', 'DomainName': 'GT_EDC'}, ''),
                        ('TPI_EVMINS_YXXK', 'FlowControl_SOC_EDC', {'TEMPLATE': 'PrimeFlowControlForkTestMethod', 'DomainName': 'SOC_EDC'}, ''),
                        ('ARR_EVMINS_YYXK', 'FAILFlowControl_SOC_EDC', {'TEMPLATE': 'PrimeFlowControlForkTestMethod', 'DomainName': 'SOC_EDC'}, ''),  # edc flowdomain but in kill
                        ('ARR_EVMINS_YYXK', 'FAILSetFlowInfo_ATOMC_Flow1', {'TEMPLATE': 'PrimeFlowControlSetTestMethod', 'DomainName': 'SOC_EDC'}, ''),  # edc flowdomain but in kill
                        ('TPI_EVMINS_YXXK', 'TEST_RING', {'TEMPLATE': 'VminForwardingSaveFakeDataTC', 'Domains': 'CLR0'}, ''),  # not pbmfc tests
                        ('ARR_CORE_CXX', 'TEST_NENAF', {'TEMPLATE': 'PrimeFlowControlForkTestMethod', 'DomainNameFalse': ''}, ''),  # Error159
                        ('ARR_CORE_CXX', 'TEST_NENAS', {'TEMPLATE': 'PrimeFlowControlSetTestMethod', 'DomainNameFalse': ''}, ''),  # Error160
                        ('TPI_EVMINS_YXXK', 'FlowControl_ATOMB', {'TEMPLATE': 'PrimeFlowControlForkTestMethod', 'DomainName': 'ATOMB'}, ''),  # Error164
                        ('TPI_EVMINS_YXXK', 'SetFlowInfo_ATOMB_Flow1', {'TEMPLATE': 'PrimeFlowControlSetTestMethod', 'DomainName': 'ATOMB'}, ''),  # Error164
                        ('FUN_CORE_CXX', 'SetFlowInfo_CORE_Flow1', {'TEMPLATE': 'PrimeFlowControlSetTestMethod', 'DomainName': 'CORE_EDC'}, '')
                        ]

            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)
            obj = Checkers()
            obj.run_check(obj.mtl_flowdomainchk, True, stpldata)
            self.assertEqual(obj.sum[obj.mtl_flowdomainchk], {'ARR_CORE_CXX': {'e': 2, 'w': 0, 'p': 0},
                                                              'ARR_EVMINS_YYXK': {'e': 0, 'w': 0, 'p': 0},
                                                              'FUN_CORE_CXX': {'e': 1, 'w': 0, 'p': 0},
                                                              'TPI_EVMINS_CXX': {'e': 0, 'w': 0, 'p': 0},
                                                              'TPI_EVMINS_YXXK': {'e': 1, 'w': 0, 'p': 0}
                                                              })
            self.assertEqual(obj.msgstr, ['ARR_CORE_CXX -Error159- Module uses PMBFC FlowControl without a DomainName!',
                                          'ARR_CORE_CXX -Error160- Module uses PMBFC SetFlow without a DomainName!',
                                          'TPI_EVMINS_YXXK -Error164- Module uses an invalid DomainName=ATOMB',
                                          'FUN_CORE_CXX -Error163- DomainName=CORE_EDC present in SetFlow but missing in FlowControl'
                                          ])

    def test_gen_supercedechk(self):
        with TempDir(name=True, chdir=True) as tdir:  # basic pass scenario
            d1 = 'Supersedes/code/iCAwesomeCode.dll'
            d2 = 'Supersedes/code/iTest.dll'
            d3 = 'Supersedes/code/iMissing.dll'
            rd = 'supersedes_code_readme.txt'

            rddata = """iCAwesomeCode.dll Awesome dll for awesome testing
iTest.dll basic test dll
iMissing.dll dll that is always missing
"""
            File(d1).touch('', mkdir=True, newfile=True)
            File(d2).touch('', mkdir=True, newfile=True)
            File(d3).touch('', mkdir=True, newfile=True)
            File(rd).touch(rddata, mkdir=True, newfile=True)

            obj = Checkers()
            obj.run_check(obj.gen_supercedechk, True)
            self.assertEqual(obj.sum[obj.gen_supercedechk], {})
            self.assertEqual(obj.msgstr, [])

        with TempDir(name=True, chdir=True) as tdir:  # No supercede files
            obj = Checkers()
            obj.run_check(obj.gen_supercedechk, True)

        with TempDir(name=True, chdir=True) as tdir:  # Has supercede but supersedes_code_readme.txt is missing
            d1 = 'Supersedes/code/iCAwesomeCode.dll'
            File(d1).touch('', mkdir=True, newfile=True)
            obj = Checkers()
            obj.run_check(obj.gen_supercedechk, True)
            self.assertEqual(obj.sum[obj.gen_supercedechk], {'supersedes_code_readme.txt': {'e': 1, 'w': 0, 'p': 0}})
            self.assertEqual(obj.msgstr, ['supersedes_code_readme.txt -Error165- Missing Supersedes/code documentation:supersedes_code_readme.txt'])

        with TempDir(name=True, chdir=True) as tdir:  # dll has missing info inside Readme.txt
            d1 = 'Supersedes/code/iCAwesomeCode.dll'
            d2 = 'Supersedes/code/iTest.dll'
            d3 = 'Supersedes/code/iMissing.dll'
            rd = 'supersedes_code_readme.txt'

            rddata = """iCAwesomeCode.dll Awesome dll for awesome testing
iTest.dll basic test dll
"""
            File(d1).touch('', mkdir=True, newfile=True)
            File(d2).touch('', mkdir=True, newfile=True)
            File(d3).touch('', mkdir=True, newfile=True)
            File(rd).touch(rddata, mkdir=True, newfile=True)

            obj = Checkers()
            obj.run_check(obj.gen_supercedechk, True)
            self.assertEqual(obj.sum[obj.gen_supercedechk], {'iMissing.dll': {'e': 1, 'w': 0, 'p': 0}})
            self.assertEqual(obj.msgstr, ['iMissing.dll -Error166- Supersedes/code file=Supersedes/code/iMissing.dll is not documented in supersedes_code_readme.txt'])

    def test_gen_copycatchk(self):
        with TempDir(name=True, chdir=True) as tdir:
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)
            obj = Checkers()
            obj.run_check(obj.gen_copycatchk, False, 'ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_END_X_VX_F2_X_1504_COPY')
            obj.run_check(obj.gen_copycatchk, False, 'ARR_CORE_CXX', 'EVMINS_CR_FUNC_K_END_X_VX_F2_X_COPY_1503')
            obj.run_check(obj.gen_copycatchk, False, 'IP_CPU_BASE', 'EVMINS_CR_UF_K_END_X_VX_F2_X_COPY')
            obj.run_check(obj.gen_copycatchk, False, 'IP_PCH_BASE', 'EVMINS_CR_UF_K_END_X_VX_F2_X_PASS')
            self.assertEqual(obj.sum[obj.gen_copycatchk], {'ARR_CORE_CXX': {'e': 0, 'w': 2, 'p': 0},
                                                           'IP_CPU_BASE': {'e': 0, 'w': 1, 'p': 0}
                                                           })
            self.assertEqual(obj.msgstr, ['ARR_CORE_CXX -Warning167- Test:EVMINS_CR_VMIN_K_END_X_VX_F2_X_1504_COPY has "_COPY", is this a copy/paste error?!',
                                          'ARR_CORE_CXX -Warning167- Test:EVMINS_CR_FUNC_K_END_X_VX_F2_X_COPY_1503 has "_COPY", is this a copy/paste error?!',
                                          'IP_CPU_BASE -Warning167- Test:EVMINS_CR_UF_K_END_X_VX_F2_X_COPY has "_COPY", is this a copy/paste error?!'])

    def test_mtl_dlvrchk(self):
        with TempDir(name=True, chdir=True) as tdir:
            ipcpuflows = ['SCRF1', 'CCRF1', 'SCRF2', 'CCRF2', 'BEGCPU', 'BEGCPUPKG']
            stpldata = [('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_SCRF1_X_X_X_X_TEST1_1001', {'TEMPLATE': 'VminTC', 'patlist': 'arr_list', 'VoltageConverter': '--dlvrpins IP_CPU::VCCIA_HC'}, ''),  # pass: prime with VoltageConverter
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_SCRF1_X_X_X_X_TEST2_1001', {'TEMPLATE': 'VminTC', 'patlist': 'arr_list', 'PreInstance': '--dlvrpins IP_CPU::VCCIA_HC'}, ''),  # pass: prime with PreInstance
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_SCRF2_X_X_X_X_TEST3_1001', {'TEMPLATE': 'iCFunc', 'patlist': 'arr_list', 'preinstance': '--dlvrpins IP_CPU::VCCIA_HC'}, ''),  # pass: evg with preinstance
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_SCRF1_X_X_X_X_TEST4_1001', {'TEMPLATE': 'VminTC', 'patlist': 'arr_list', 'PrePlist': '--dlvrpins IP_CPU::VCCIA_HC'}, ''),  # pass: prime with PrePlist
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_SCRF2_X_X_X_X_TEST5_1001', {'TEMPLATE': 'iCFunc', 'patlist': 'arr_list', 'preplist': '--dlvrpins IP_CPU::VCCIA_HC'}, ''),  # pass: evg with preplist
                        ('ARR_CORE_CXXK', 'EVMINS_CR_VMIN_K_BEGCPUPKG_X_X_X_X_TEST', {'TEMPLATE': 'VminTC', 'patlist': 'arr_list', 'PrePlist': '--dlvrpins IP_CPU::VCCIA_HC'}, ''),  # pass: prime with PrePlist @PKG flow
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_SCRF1_X_X_X_X_TEST1_1002', {'TEMPLATE': 'VminTC', 'patlist': 'arr_list', 'VoltageConverter': 'powermux'}, ''),  # fail: prime with VoltageConverter but no dlvrpins
                        ('FUN_CORE_CXX', 'EVMINS_CR_VMIN_K_SCRF1_X_X_X_X_TEST2_1002', {'TEMPLATE': 'VminTC', 'patlist': 'arr_list', 'PreInstance': 'powermux'}, ''),  # fail: prime with PreInstance but no dlvrpins
                        ('SCN_CORE_CXX', 'EVMINS_CR_VMIN_K_SCRF2_X_X_X_X_TEST3_1002', {'TEMPLATE': 'iCFunc', 'patlist': 'arr_list'}, ''),  # fail: evg without dlvrpins
                        ('SCN_CORE_CXXK', 'EVMINS_NONCCF_VMIN_K_BEGCPU_X_VNNAON_X_X_TEST_1001', {'TEMPLATE': 'iCFunc', 'patlist': 'scn_list'}, ''),  # pass: ignore case for NONCCF+VNNAON in IP_CPU subflow
                        ('ARR_CORE_CXXK', 'EVMINS_NONCCF_VMIN_K_BEGCPUPKG_X_VNNAON_X_X_TEST_1001', {'TEMPLATE': 'iCFunc', 'patlist': 'arr_list'}, ''),  # pass: ignore case for NONCCF+VNNAON in PKG subflow
                        ('ARR_GT_GXX', 'EVMINS_CR_VMIN_K_SGTF2_X_X_X_X_TEST3_1001', {'TEMPLATE': 'VminTC', 'patlist': 'arr_list', 'PreInstance': 'patmodme'}, ''),  # prime with PreInstance + gt == ignore
                        ('ARR_GT_GXX', 'EVMINS_CR_VMIN_K_SGTF2_X_X_X_X_TEST4_1001', {'TEMPLATE': 'iCFunc', 'patlist': 'arr_list', 'preinstance': 'patmodme'}, ''),  # evg with preinstance + gt == ignore
                        ('DRV_RESET_CXX', 'RESET_X_FUNC_E_BEGCPU_X_INF_X_X_BASIC_RESET_BBS', {'TEMPLATE': 'VminTC', 'patlist': 'arr_list', 'PreInstance': 'patmodme'}, ''),  # DRV_RESET_CXX coreless test = skipped/ignored
                        ('PTH_DLVR_CXX', 'DLVR_X_ANAMEAS_E_BEGCPUPKG_X_X_X_X_ADC0_OFFSET_TRIM', {'TEMPLATE': 'VminTC', 'patlist': 'pth_list'}, '')  # pass: Ignore pth module inside
                        ]
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)
            obj = Checkers()
            obj.run_check(obj.mtl_dlvrchk, True, stpldata, ipcpuflows)
            self.assertEqual(obj.sum[obj.mtl_dlvrchk], {'ARR_CORE_CXX': {'e': 1, 'w': 0, 'p': 0},
                                                        'ARR_CORE_CXXK': {'e': 0, 'w': 0, 'p': 0},
                                                        'ARR_GT_GXX': {'e': 0, 'w': 0, 'p': 0},
                                                        'FUN_CORE_CXX': {'e': 1, 'w': 0, 'p': 0},
                                                        'PTH_DLVR_CXX': {'e': 0, 'w': 0, 'p': 0},
                                                        'SCN_CORE_CXX': {'e': 1, 'w': 0, 'p': 0},
                                                        'SCN_CORE_CXXK': {'e': 0, 'w': 0, 'p': 0}
                                                        })
            self.assertEqual(obj.msgstr, ['ARR_CORE_CXX -Error168- Test:EVMINS_CR_VMIN_K_SCRF1_X_X_X_X_TEST1_1002 in cdie subflow=SCRF1 is missing dlvr call!',
                                          'FUN_CORE_CXX -Error168- Test:EVMINS_CR_VMIN_K_SCRF1_X_X_X_X_TEST2_1002 in cdie subflow=SCRF1 is missing dlvr call!',
                                          'SCN_CORE_CXX -Error168- Test:EVMINS_CR_VMIN_K_SCRF2_X_X_X_X_TEST3_1002 in cdie subflow=SCRF2 is missing dlvr call!'])

    def test_mtl_ttrpatmapchk(self):
        with TempDir(name=True, chdir=True) as tdir:
            srhflows = ['SCRF1', 'SGTF1']
            stpldata = [('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_SCRF1_X_X_X_X_TESTC_1001', {'TEMPLATE': 'VminTC', 'patlist': 'test_list'}, ''),  # no pnm/no bnm
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_SCRF1_X_X_X_X_TEST1_1001', {'TEMPLATE': 'VminTC', 'PatternNameMap': '9,10,11,12,13,14,15', 'ScoreboardBaseNumber': '23011'}, ''),  # warning169
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF1_X_X_X_X_TEST1_1001', {'TEMPLATE': 'VminTC', 'PatternNameMap': '9,10,11,12,13,14,15', 'ScoreboardBaseNumber': '23012'}, ''),  # prime pass; 9-15 no space
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF1_X_X_X_X_TEST1_1002', {'TEMPLATE': 'VminTC', 'PatternNameMap': '1,2,3,4,5,6,7'}, ''),  # prime pass; 1-7 no space
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF1_X_X_X_X_TEST1_1003', {'TEMPLATE': 'VminTC', 'PatternNameMap': '9,10,11,12,13,14, 15'}, ''),  # prime pass; 9-15 with space
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF1_X_X_X_X_CLK_1001', {'TEMPLATE': 'VminTC', 'PatternNameMap': '9,10,11,12,13,14, 15', 'FeatureSwitchSettings': 'per_pattern_printing'}, ''),  # prime pass; per_pattern_printing no basenumber
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF1_X_X_X_X_CLK_1002', {'TEMPLATE': 'VminTC', 'PatternNameMap': '9,10,11,12,13,14, 15', 'FeatureSwitchSettings': 'per_pattern_printing', 'ScoreboardBaseNumber': '23012'}, ''),  # prime fail; per_pattern_printing with basenumber
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF1_X_X_X_X_CLK_2001', {'TEMPLATE': 'VminTC', 'PatternNameMap': '98,99,100', 'FeatureSwitchSettings': 'per_pattern_printing'}, ''),  # prime pass; per_pattern_printing no basenumber
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF1_X_X_X_X_CLK_2002', {'TEMPLATE': 'VminTC', 'PatternNameMap': '98,99,100', 'FeatureSwitchSettings': 'per_pattern_printing', 'ScoreboardBaseNumber': '23012'}, ''),  # prime fail error181; per_pattern_printing with basenumber
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF1_X_X_X_X_CLK_3001', {'TEMPLATE': 'VminTC', 'PatternNameMap': '98,99,100', 'FeatureSwitchSettings': 'fivr_mode_on'}, ''),  # prime fail error182; no per_pattern_printing no basenumber
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF1_X_X_X_X_CLK_3002', {'TEMPLATE': 'VminTC', 'PatternNameMap': '98,99,100', 'FeatureSwitchSettings': 'fivr_mode_on', 'ScoreboardBaseNumber': '23012'}, ''),  # prime fail error182;  no per_pattern_printing with basenumber
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF1_X_X_X_X_TEST2_1001', {'TEMPLATE': 'iCSimpleScoreBoard', 'pattern_name_map': '9,10,11,12,13,14,15', 'base_number': '32011'}, ''),  # evg pass; 9-15 no space
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF1_X_X_X_X_TEST2_1002', {'TEMPLATE': 'iCSimpleScoreBoard', 'pattern_name_map': '1,2,3,4,5,6,7', 'base_number': '32012'}, ''),  # evg pass; 1-7 no space
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_BEGCPU_X_X_X_X_TEST2_1002', {'TEMPLATE': 'iCSimpleScoreBoard', 'pattern_name_map': '0,1,2,3,4,5,6', 'base_number': '32013'}, ''),  # error170
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_ENDCPU_X_X_X_X_TEST2_1002', {'TEMPLATE': 'iCSimpleScoreBoard', 'pattern_name_map': '98,99,100', 'base_number': '32013'}, '')  # warning171
                        ]
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)
            obj = Checkers()
            obj.run_check(obj.mtl_ttrpatmapchk, True, stpldata, srhflows)
            self.assertEqual(obj.sum[obj.mtl_ttrpatmapchk], {'ARR_CORE_CXX': {'e': 5, 'w': 1, 'p': 0}})
            self.assertEqual(obj.msgstr, ['ARR_CORE_CXX -Warning169- Test:EVMINS_CR_VMIN_K_SCRF1_X_X_X_X_TEST1_1001 in SRH flow:SCRF1, scoreboard NOT reqd',
                                          'ARR_CORE_CXX -Error181- Test:EVMINS_CR_VMIN_K_CCRF1_X_X_X_X_CLK_2002 uses per_pattern_printing and base# at the same time! patmap=98,99,100 base#=23012',
                                          'ARR_CORE_CXX -Error182- Test:EVMINS_CR_VMIN_K_CCRF1_X_X_X_X_CLK_3001 has user_defined pattern_name_map=98,99,100!',
                                          'ARR_CORE_CXX -Error182- Test:EVMINS_CR_VMIN_K_CCRF1_X_X_X_X_CLK_3002 has user_defined pattern_name_map=98,99,100!',
                                          'ARR_CORE_CXX -Error170- Test:EVMINS_CR_VMIN_K_BEGCPU_X_X_X_X_TEST2_1002 uses letters for pattern_name_map=0,1,2,3,4,5,6!',
                                          'ARR_CORE_CXX -Error171- Test:EVMINS_CR_VMIN_K_ENDCPU_X_X_X_X_TEST2_1002 has user_defined pattern_name_map=98,99,100!'
                                          ])

    def test_gen_testemptychk(self):
        with TempDir(name=True, chdir=True) as tdir:
            stpldata = [('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_SCRF1_X_X_X_X_TESTC_1001', {'TEMPLATE': 'VminTC'}, ''),  # Error172
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_SCRF1_X_X_X_X_TEST1_1001', {'TEMPLATE': 'VminTC', 'PatternNameMap': '9,10,11,12,13,14,15', 'ScoreboardBaseNumber': '23011'}, ''),  # pass
                        ('FUN_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF1_X_X_X_X_TEST1_1001', {'TEMPLATE': 'VminTC', 'PatternNameMap': '9,10,11,12,13,14,15', 'ScoreboardBaseNumber': '23012'}, ''),  # pass
                        ('SCN_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF1_X_X_X_X_TEST1_1002', {'TEMPLATE': 'VminTC', 'PatternNameMap': '1,2,3,4,5,6,7'}, ''),  # pass
                        ('SCN_CORE_CXX', 'EVMINS_CR_VMIN_K_BEGCPU_X_X_X_X_TEST2_1002', {'TEMPLATE': 'iCSimpleScoreBoard'}, ''),  # Error172
                        ('SCN_CORE_CXX', 'EVMINS_CR_VMIN_K_ENDCPU_X_X_X_X_TEST2_1002', {'TEMPLATE': 'iCSimpleScoreBoard'}, '')  # Error172
                        ]
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)
            obj = Checkers()
            obj.run_check(obj.gen_emptytestchk, True, stpldata)
            self.assertEqual(obj.sum[obj.gen_emptytestchk], {'ARR_CORE_CXX': {'e': 1, 'w': 0, 'p': 0},
                                                             'SCN_CORE_CXX': {'e': 2, 'w': 0, 'p': 0}})
            self.assertEqual(obj.msgstr, ['ARR_CORE_CXX -Error172- Test:EVMINS_CR_VMIN_K_SCRF1_X_X_X_X_TESTC_1001 has no parameter settings!',
                                          'SCN_CORE_CXX -Error172- Test:EVMINS_CR_VMIN_K_BEGCPU_X_X_X_X_TEST2_1002 has no parameter settings!',
                                          'SCN_CORE_CXX -Error172- Test:EVMINS_CR_VMIN_K_ENDCPU_X_X_X_X_TEST2_1002 has no parameter settings!'])

    def test_mtl_vmintcchk(self):
        with TempDir(name=True, chdir=True) as tdir:
            cids = ['CR5@F1', 'CR4@F1', 'CR3@F1', 'CR2@F1', 'CRU1@F1', 'CRU0@F1', 'GT@F1', 'CLR0@F1', 'CLR0@F2']
            bomflows = ['1001', '1002', '1003', '1201', '1202', '1203']
            stpldata = [('ARR_CORE_CXX', 'EVMINS_CR_FUNC_K_MAXCR_X_X_X_X_TESTC_1001', {'TEMPLATE': 'iCSimpleScoreBoard', 'base_number': '12345'}, ''),  # nonVminTC, skip
                        ('ARR_CORE_CXX', 'EVMINS_CR_FUNC_K_BEGCPU_X_X_X_X_TESTC', {'TEMPLATE': 'VminTC'}, ''),  # VminTC But Static test, skip
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_SCRF1_X_X_X_X_TESTC_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'CornerIdentifiers': 'CR5@F1,CR4@F1,CR3@F1,CR2@F1,CRU1@F1,CRU0@F1', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'RecoveryMode': 'RecoveryLoop', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin', 'VoltagesOffset': 'GBVars.VoltageOffset', 'LimitGuardband': 'GBVars.LimitGuardband'}, ''),  # basic vmin CDIE KILL SRH pass, , Unneeded VoltagesOffset and LimitGuardband inside SRH test
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF1_X_X_X_X_TESTC_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'CornerIdentifiers': 'CR5@F1,CR4@F1,CR3@F1,CR2@F1,CRU1@F1,CRU0@F1', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'RecoveryMode': 'NoRecovery', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin', 'VoltagesOffset': 'GBVars.VoltageOffset', 'LimitGuardband': 'GBVars.LimitGuardband'}, ''),  # basic vmin CDIE KILL CHK pass
                        ('ARR_CCF_CXX', 'EVMINS_CLR_VMIN_K_SCLRF1_X_X_X_X_TESTC_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'CornerIdentifiers': 'CLR0@F1', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'RecoveryMode': 'RecoveryLoop', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'SingleVmin'}, ''),  # basic vmin CDIE KILL SRH pass CLR
                        ('ARR_CCF_CXX', 'EVMINS_CLR_VMIN_K_CCLRF1_X_X_X_X_TESTC_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'CornerIdentifiers': 'CLR0@F1', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'RecoveryMode': 'NoRecovery', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'SingleVmin', 'VoltagesOffset': 'GBVars.VoltageOffset', 'LimitGuardband': 'GBVars.LimitGuardband'}, ''),  # basic vmin CDIE KILL CHK pass CLR
                        ('ARR_CCF_CXX', 'EVMINS_CLR_VMIN_K_SCLRF1_X_X_X_X_TESTC_1003', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'CornerIdentifiers': 'CLR0@F1', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'TestMode': 'SingleVmin'}, ''),  # basic vmin CDIE KILL pass CLR
                        ('ARR_GT_GXX', 'EVMINS_GT_VMIN_K_SGTF1_X_X_X_X_TESTC_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'CornerIdentifiers': 'GT@F1', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'TestMode': 'SingleVmin'}, ''),  # basic vmin GT KILL SRH pass
                        ('ARR_GT_GXX', 'EVMINS_GT_VMIN_K_CGTF1_X_X_X_X_TESTC_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'CornerIdentifiers': 'GT@F1', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'TestMode': 'SingleVmin', 'VoltagesOffset': 'GBVars.VoltageOffset', 'LimitGuardband': 'GBVars.LimitGuardband'}, ''),  # basic vmin GT KILL CHK pass
                        ('ARR_GT_GXX', 'EVMINS_GT_VMIN_K_SGTF1_X_X_X_X_TESTC_1003', {'TEMPLATE': 'VminTC', 'BypassPort': '1', 'CornerIdentifiers': 'GT@F1', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'TestMode': 'SingleVmin'}, ''),  # basic floating bypassed test
                        ('ARR_GT_GXX', 'EVMINS_GT_VMIN_K_CGTF1_X_X_X_X_TESTC_1003', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', 'CornerIdentifiers': 'GT@F1', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'TestMode': 'SingleVmin', 'VoltagesOffset': 'GBVars.VoltageOffset', 'LimitGuardband': 'GBVars.LimitGuardband'}, ''),  # basic floating unbypassed test
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_E_SCRF1_X_X_X_X_TA1_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'EDC', 'ForwardingMode': 'Input', 'RecoveryMode': 'RecoveryLoop', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin'}, ''),  # EDC vmin #1 CDIE non-CLR fmd:Input Mode RecoveryLoop scenario
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_E_SCRF1_X_X_X_X_TA1_1002', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'EDC', 'ForwardingMode': 'Input', 'RecoveryMode': 'NoRecovery', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin'}, ''),  # EDC vmin #1 CDIE non-CLR fmd:Input Mode NoRecovery scenario
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_E_SCRF1_X_X_X_X_TA1_1003', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'EDC', 'ForwardingMode': 'None', 'RecoveryMode': 'NoRecovery', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin'}, ''),  # EDC vmin #1 CDIE non-CLR fmd:Input Mode NoRecovery scenario
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_E_SCRF1_X_X_X_X_TA2_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'EDC', 'ForwardingMode': 'None', 'RecoveryMode': 'Default', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin'}, ''),  # EDC vmin #1 CDIE non-CLR fmd:None Mode scenario
                        ('ARR_CCF_CXX', 'EVMINS_CLR_VMIN_E_SCLRF1_X_X_X_X_TA1_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'EDC', 'ForwardingMode': 'Input', 'RecoveryMode': 'RecoveryLoop', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'SingleVmin'}, ''),  # EDC vmin #1 CDIE CLR fmd:Input Mode RecoveryLoop scenario
                        ('ARR_CCF_CXX', 'EVMINS_CLR_VMIN_E_SCLRF1_X_X_X_X_TA1_1002', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'EDC', 'ForwardingMode': 'Input', 'RecoveryMode': 'NoRecovery', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'SingleVmin'}, ''),  # EDC vmin #1 CDIE CLR fmd:Input Mode NoRecovery scenario
                        ('ARR_CCF_CXX', 'EVMINS_CLR_VMIN_E_SCLRF1_X_X_X_X_TA1_1003', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'EDC', 'ForwardingMode': 'None', 'RecoveryMode': 'NoRecovery', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'SingleVmin'}, ''),  # EDC vmin #1 CDIE CLR fmd:Input Mode NoRecovery scenario
                        ('ARR_CCF_CXX', 'EVMINS_CLR_VMIN_E_SCLRF1_X_X_X_X_TA2_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'EDC', 'ForwardingMode': 'None', 'RecoveryMode': 'Default', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'SingleVmin'}, ''),  # EDC vmin #1 CDIE CLR fmd:None Mode scenario
                        ('ARR_CCF_CXX', 'EVMINS_CLR_VMIN_E_SCLRF2_X_X_X_X_TA4_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'EDC', 'ForwardingMode': 'None', 'TestMode': 'SingleVmin'}, ''),  # EDC vmin #1 CDIE CLR fmd:None Mode scenario
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_E_SCRF4_X_X_X_X_TA4_1201', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'EDC', 'ForwardingMode': 'None', 'TestMode': 'MultiVmin'}, ''),  # EDC vmin #1 CDIE non-CLR fmd:None Mode scenario
                        ('ARR_SOC_SXX', 'EVMINS_SAQ_VMIN_E_SSNF1_X_X_X_X_TA1_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'EDC', 'ForwardingMode': 'None', 'TestMode': 'SingleVmin'}, ''),  # EDC vmin #1 SOC fmd:None Mode scenario
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_E_SCRF1_X_X_X_X_TA3_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'EDC', 'CornerIdentifiers': 'CR5@F1,CR4@F1,CR3@F1,CR2@F1,CRU1@F1,CRU0@F1', 'ForwardingMode': 'Input', 'FlowIndex': '1', 'RecoveryMode': 'Default', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin'}, ''),  # EDC vmin #2 CDIE non-CLR fmd:!NoRecovery
                        ('ARR_CCF_CXX', 'EVMINS_CLR_VMIN_E_SCLRF1_X_X_X_X_TA3_1003', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'EDC', 'CornerIdentifiers': 'CLR0@F1', 'ForwardingMode': 'Input', 'FlowIndex': '1', 'RecoveryMode': 'Default', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'SingleVmin'}, ''),  # EDC vmin #2 CDIE CLR fmd:!NoRecovery
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_E_SCRF1_X_X_X_X_TA3_1201', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'EDC', 'CornerIdentifiers': 'CR5@F1,CR4@F1,CR3@F1,CR2@F1,CRU1@F1,CRU0@F1', 'ForwardingMode': 'Input', 'FlowIndex': '1', 'RecoveryMode': 'NoRecovery', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin'}, ''),  # EDC vmin #2 CDIE non-CLR fmd:!NoRecovery
                        ('ARR_CCF_CXX', 'EVMINS_CLR_VMIN_E_SCLRF1_X_X_X_X_TA3_1203', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'EDC', 'CornerIdentifiers': 'CLR0@F1', 'ForwardingMode': 'Input', 'FlowIndex': '1', 'RecoveryMode': 'NoRecovery', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'SingleVmin'}, ''),  # EDC vmin #2 CDIE CLR fmd:!NoRecovery
                        ('ARR_CCF_CXX', 'EVMINS_CLR_VMIN_E_SCLRF2_X_X_X_X_TA2_1003', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'EDC', 'CornerIdentifiers': 'CLR0@F2', 'ForwardingMode': 'Input', 'FlowIndex': '1', 'TestMode': 'SingleVmin'}, ''),  # EDC vmin #2 CDIE CLR fmd:INput Mode scenario
                        ('ARR_GT_GXX', 'EVMINS_GT_VMIN_E_SGTF1_X_X_X_X_TA2_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'EDC', 'CornerIdentifiers': 'GT@F1', 'ForwardingMode': 'Input', 'FlowIndex': '1', 'TestMode': 'SingleVmin'}, ''),  # EDC vmin #2 GDIE fmd:INput Mode scenario
                        ('ARR_SOC_SXX', 'EVMINS_SAQ_VMIN_E_SSNF1_X_X_X_X_TA2_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'EDC', 'CornerIdentifiers': 'GT@F1', 'ForwardingMode': 'Input', 'FlowIndex': '1', 'TestMode': 'SingleVmin'}, ''),  # EDC vmin #2 SOC fmd:Input Mode scenario
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMAX_K_MAXCR_X_X_X_X_TA4_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'ForwardingMode': 'Input', 'FlowIndex': '1', 'RecoveryMode': 'NoRecovery', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'Functional'}, ''),  # KILL vmax #1 CDIE non-CLR fmd:Input
                        ('ARR_CCF_CXX', 'EVMINS_CLR_VMAX_K_MAXCLR_X_X_X_X_TA4_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'ForwardingMode': 'Input', 'FlowIndex': '1', 'RecoveryMode': 'NoRecovery', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'Functional'}, ''),  # KILL vmax #1 CDIE CLR fmd:Input
                        ('ARR_CCF_CXX', 'EVMINS_CLR_VMAX_K_MAXCLR_X_X_X_X_TX3_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'ForwardingMode': 'None', 'FlowIndex': '1', 'TestMode': 'Functional'}, ''),  # KILL vmax #1 CDIE CLR fmd:None
                        ('ARR_GT_GXX', 'EVMINS_GT_VMAX_K_MAXGT_X_X_X_X_TA3_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'ForwardingMode': 'None', 'FlowIndex': '1', 'TestMode': 'Functional'}, ''),  # KILL vmax #1 GDIE fmd:None
                        ('ARR_SOC_SXX', 'EVMINS_SAQ_VMAX_K_ENDSOC_X_X_X_X_TA3_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'ForwardingMode': 'None', 'FlowIndex': '1', 'TestMode': 'Functional'}, ''),  # KILL vmax #1 DOSC fmd:None
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMAX_E_MAXCR_X_X_X_X_TA5_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'EDC', 'ForwardingMode': 'Input', 'RecoveryMode': 'NoRecovery', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'Functional'}, ''),  # EDC vmax #1 CDIE non-CLR fmd:Input
                        ('ARR_CCF_CXX', 'EVMINS_CLR_VMAX_E_MAXCLR_X_X_X_X_TA5_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'EDC', 'ForwardingMode': 'Input', 'RecoveryMode': 'NoRecovery', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'Functional'}, ''),  # EDC vmax #1 CDIE CLR fmd:Input
                        ('ARR_GT_GXX', 'EVMINS_GT_VMAX_E_MAXGT_X_X_X_X_TA4_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'EDC', 'ForwardingMode': 'None', 'TestMode': 'Functional'}, ''),  # EDC vmax #1 GDIE fmd:None
                        ('ARR_CCF_CXX', 'EVMINS_CLR_VMAX_E_MAXCLR_X_X_X_X_TA4_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'EDC', 'ForwardingMode': 'None', 'TestMode': 'Functional'}, ''),  # EDC vmax #1 CDIE+CLR subflow fmd:None
                        ('ARR_SOC_SXX', 'EVMINS_SAQ_VMAX_E_ENDSOC_X_X_X_X_TA4_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'EDC', 'ForwardingMode': 'None', 'TestMode': 'Functional'}, ''),  # EDC vmax #1 SOC fmd:None
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_E_SCRF1_X_X_X_X_BADKILL_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'EDC', 'CornerIdentifiers': 'CR5@F1,CR4@F1,CR3@F1,CR2@F1,CRU1@F1,CRU0@F1', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'RecoveryMode': 'Default', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin'}, ''),  # basic vmin CDIE KILL settings but test is in EDC mode
                        ('ARR_GT_GXX', 'EVMINS_GT_VMIN_E_SGTF1_X_X_X_X_BADKILL_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'EDC', 'CornerIdentifiers': 'GT@F1', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'TestMode': 'SingleVmin'}, ''),  # basic vmin GT KILL settings but test is in EDC mode
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_BEGCPU_X_X_X_X_TESTC_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'RecoveryMode': 'RecoveryLoop', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin'}, ''),  # begcpu pt test that looks like a vmin search, high/low limits==same, no cornerid, only dierecovery
                        ('ARR_GT_GXX', 'EVMINS_GT_VMIN_E_CGTF1_X_X_X_X_BADKILL_1203', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'EDC', 'CornerIdentifiers': 'GTR@F1', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'TestMode': 'SingleVmin'}, ''),  # basic vmin GT KILL settings but test is in EDC mode, missing VoltagesOffset and LimitGuardband
                        ('ARR_GT_GXX', 'EVMINS_GT_VMIN_K_BEGGT_X_X_X_X_STATICBADKILL', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'FlowIndex': '1', 'TestMode': 'SingleVmin'}, '')  # error188, illeglal use of flowindex in a static vminTC test
                        ]
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)
            obj = Checkers()

            class fake_mtpl_obj:
                @staticmethod
                def is_bypassed(mod, test):
                    for md, tn, data, _ in stpldata:
                        if md == mod and test == tn:
                            if data.get('BypassPort') == '1':
                                return True
                    return False

            obj.run_check(obj.mtl_vmintcchk, True, stpldata, bomflows, cids, fake_mtpl_obj)
            self.assertEqual(obj.sum[obj.mtl_vmintcchk], {'ARR_CCF_CXX': {'e': 0, 'w': 0, 'p': 0},
                                                          'ARR_CORE_CXX': {'e': 2, 'w': 1, 'p': 0},
                                                          'ARR_GT_GXX': {'e': 3, 'w': 5, 'p': 0},
                                                          'ARR_SOC_SXX': {'e': 0, 'w': 0, 'p': 0}
                                                          })
            expect = '''ARR_CORE_CXX -Error184- Test:EVMINS_CR_VMIN_K_SCRF1_X_X_X_X_TESTC_1001 dont need VoltagesOffset value:GBVars.VoltageOffset when in SRH subflow:SCRF1
ARR_CORE_CXX -Error185- Test:EVMINS_CR_VMIN_K_SCRF1_X_X_X_X_TESTC_1001 dont need LimitGuardband value:GBVars.LimitGuardband when in SRH subflow:SCRF1
ARR_GT_GXX -Warning173- Test:EVMINS_GT_VMIN_K_SGTF1_X_X_X_X_TESTC_1003 is floating+bypassed! TestInfo=Bypass:True KillEdc:None CornerID=GT@F1 ForwardingMode=InputOutput FlowIndex=1 RecMode=None RecOptions=None RecTrackIncoming=None RecTrackOutgoing=None TestMode:SingleVmin Subflow=SGTF1
ARR_GT_GXX -Warning174- Test:EVMINS_GT_VMIN_K_CGTF1_X_X_X_X_TESTC_1003 is floating+unbypassed! TestInfo=Bypass:False KillEdc:None CornerID=GT@F1 ForwardingMode=InputOutput FlowIndex=1 RecMode=None RecOptions=None RecTrackIncoming=None RecTrackOutgoing=None TestMode:SingleVmin Subflow=CGTF1
ARR_CORE_CXX -Warning175- Test:EVMINS_CR_VMIN_E_SCRF1_X_X_X_X_BADKILL_1001 wrong speedflow setup! TestInfo=vd:0111111111 Bypass:False KillEdc:EDC CornerID=CR5@F1,CR4@F1,CR3@F1,CR2@F1,CRU1@F1,CRU0@F1 ForwardingMode=InputOutput FlowIndex=1 RecMode=Default RecOptions=RWCDefeaturingVector_CLASS_P68G2,6 RecTrackIncoming=CR5,CR4,CR3,CR2,CR1,CR0 RecTrackOutgoing=CR5,CR4,CR3,CR2,CR1,CR0 TestMode:MultiVmin Subflow=SCRF1
ARR_GT_GXX -Warning175- Test:EVMINS_GT_VMIN_E_SGTF1_X_X_X_X_BADKILL_1001 wrong speedflow setup! TestInfo=vd:0111000010 Bypass:False KillEdc:EDC CornerID=GT@F1 ForwardingMode=InputOutput FlowIndex=1 RecMode=None RecOptions=None RecTrackIncoming=None RecTrackOutgoing=None TestMode:SingleVmin Subflow=SGTF1
ARR_GT_GXX -Warning175- Test:EVMINS_GT_VMIN_E_CGTF1_X_X_X_X_BADKILL_1203 wrong speedflow setup! TestInfo=vd:0111000010 Bypass:False KillEdc:EDC CornerID=GTR@F1 ForwardingMode=InputOutput FlowIndex=1 RecMode=None RecOptions=None RecTrackIncoming=None RecTrackOutgoing=None TestMode:SingleVmin Subflow=CGTF1
ARR_GT_GXX -Error183- Test:EVMINS_GT_VMIN_E_CGTF1_X_X_X_X_BADKILL_1203 used an invalid cornerid:GTR@F1
ARR_GT_GXX -Error186- Test:EVMINS_GT_VMIN_E_CGTF1_X_X_X_X_BADKILL_1203 VoltagesOffset value:None not equal to GBVars.VoltageOffset
ARR_GT_GXX -Warning187- Test:EVMINS_GT_VMIN_E_CGTF1_X_X_X_X_BADKILL_1203 LimitGuardband value:None not equal to GBVars.LimitGuardband
ARR_GT_GXX -Error188- Test:EVMINS_GT_VMIN_K_BEGGT_X_X_X_X_STATICBADKILL Illegal use of FlowIndex=1 in static vminTC'''
            self.assertTextEqual('\n'.join(obj.msgstr), expect)

    def test_mtl_vmintcflicbchk(self):
        with TempDir(name=True, chdir=True) as tdir:
            bomflows = ['1001', '1002', '1003', '1201', '1202', '1203']
            stpldata = [('ARR_CORE_CXX', 'EVMINS_CR_FUNC_K_MAXCR_X_X_X_X_TESTC_1001', {'TEMPLATE': 'iCSimpleScoreBoard', 'base_number': '12345'}, ''),  # nonVminTC, skip
                        ('ARR_CORE_CXX', 'EVMINS_CR_FUNC_K_BEGCPU_X_X_X_X_TESTC', {'TEMPLATE': 'VminTC'}, ''),  # VminTC but in SRH, skip
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_E_CCRF1_X_X_X_X_TESTC_1001', {'TEMPLATE': 'VminTC', '_EDCKIL': 'EDC'}, ''),  # VminTC in CHK but not KILL, skip
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_E_CCRF1_X_X_X_X_TESTH', {'TEMPLATE': 'VminTC', '_EDCKIL': 'KIL'}, ''),  # VminTC in CHK KILL, but static only
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF1_X_X_X_X_TESTC_1002', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'FlowIndexCallbackName': 'CheckFlow(CORE)', 'VoltageTargets': 'CORE5,CORE4,CORE3,CORE2,CORE1,CORE0', 'CornerIdentifiers': 'CR5@F1,CR4@F1,CR3@F1,CR2@F1,CRU1@F1,CRU0@F1', 'ForwardingMode': 'InputOutput', 'FlowIndex': '2',
                         'RecoveryMode': 'RecoveryLoop', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin', 'VoltagesOffset': 'GBVars.VoltageOffset', 'LimitGuardband': 'GBVars.LimitGuardband'}, ''),  # basic vmin CDIE CR KILL CHK pass
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF1_X_X_X_X_TESTC_1003', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'FlowIndexCallbackName': 'CheckFlow(CR)', 'VoltageTargets': 'CORE5,CORE4,CORE3,CORE2,CORE1,CORE0', 'CornerIdentifiers': 'CR5@F1,CR4@F1,CR3@F1,CR2@F1,CRU1@F1,CRU0@F1', 'ForwardingMode': 'InputOutput', 'FlowIndex': '3', 'RecoveryMode': 'RecoveryLoop',
                         'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin', 'VoltagesOffset': 'GBVars.VoltageOffset', 'LimitGuardband': 'GBVars.LimitGuardband'}, ''),  # basic vmin CDIE KILL CHK pass, incorrect FlowIndexCallbackName data
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF1_X_X_X_X_TESTD_1002', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'VoltageTargets': 'CORE5,CORE4,CORE3,CORE2,CORE1,CORE0', 'CornerIdentifiers': 'CR5@F1,CR4@F1,CR3@F1,CR2@F1,CRU1@F1,CRU0@F1', 'ForwardingMode': 'InputOutput', 'FlowIndex': '2', 'RecoveryMode': 'RecoveryLoop',
                         'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin', 'VoltagesOffset': 'GBVars.VoltageOffset', 'LimitGuardband': 'GBVars.LimitGuardband'}, ''),  # basic vmin CDIE KILL CHK fail/error, missing FlowIndexCallbackName bypass=false
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF1_X_X_X_X_TESTD_1003', {'TEMPLATE': 'VminTC', 'BypassPort': '1', '_EDCKIL': 'KIL', 'VoltageTargets': 'CORE5,CORE4,CORE3,CORE2,CORE1,CORE0', 'CornerIdentifiers': 'CR5@F1,CR4@F1,CR3@F1,CR2@F1,CRU1@F1,CRU0@F1', 'ForwardingMode': 'InputOutput', 'FlowIndex': '3', 'RecoveryMode': 'RecoveryLoop',
                         'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin', 'VoltagesOffset': 'GBVars.VoltageOffset', 'LimitGuardband': 'GBVars.LimitGuardband'}, ''),  # basic vmin CDIE KILL CHK fail/warning, missing FlowIndexCallbackName bypass=true
                        ('ARR_GT_GXX', 'EVMINS_GT_VMIN_K_CGTF1_X_X_X_X_TESTC_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'FlowIndexCallbackName': 'CheckFlow(GT)', 'VoltageTargets': 'VCCGT_HC', 'CornerIdentifiers': 'GT0@F1', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'TestMode': 'SingleVmin', 'VoltagesOffset': 'GBVars.VoltageOffset', 'LimitGuardband': 'GBVars.LimitGuardband'}, ''),  # basic vmin GT KILL CHK pass
                        ('ARR_SA_SXX', 'EVMINS_SAQ_VMIN_K_CSNF1_X_X_X_X_TESTC_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'FlowIndexCallbackName': 'CheckFlow(SOC)', 'VoltageTargets': 'VCCSA_HC', 'CornerIdentifiers': 'SAQ0@F1', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'TestMode': 'SingleVmin', 'VoltagesOffset': 'GBVars.VoltageOffset', 'LimitGuardband': 'GBVars.LimitGuardband'}, ''),  # basic vmin SOC KILL CHK pass
                        ('ARR_ATOM_CXX', 'EVMINS_AT_VMIN_K_CATF1_X_X_X_X_TESTC_1002', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'FlowIndexCallbackName': 'CheckFlow(ATOMC)', 'VoltageTargets': 'ATOM1,ATOM0', 'CornerIdentifiers': 'AT1@F1,AT0@F1', 'ForwardingMode': 'InputOutput', 'FlowIndex': '2', 'TestMode': 'MultiVmin', 'VoltagesOffset': 'GBVars.VoltageOffset', 'LimitGuardband': 'GBVars.LimitGuardband'}, ''),  # basic vmin CDIE ATOM KILL CHK pass
                        ('ARR_RING_CXX', 'EVMINS_CLR_VMIN_K_CCLRF1_X_X_X_X_TESTC_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'FlowIndexCallbackName': 'CheckFlow(RING)', 'VoltageTargets': 'CCF', 'CornerIdentifiers': 'CLR0@F1', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'TestMode': 'SingleVmin', 'VoltagesOffset': 'GBVars.VoltageOffset', 'LimitGuardband': 'GBVars.LimitGuardband'}, ''),  # basic vmin RING KILL CHK pass
                        ('ARR_RING_CXX', 'EVMINS_CLR_VMIN_K_CCLRF1_X_X_X_X_TESTH_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'FlowIndexCallbackName': 'CheckFlow(RING)', 'VoltageTargets': 'CLR', 'CornerIdentifiers': 'CLR0@F1', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'TestMode': 'SingleVmin', 'VoltagesOffset': 'GBVars.VoltageOffset', 'LimitGuardband': 'GBVars.LimitGuardband'}, '')  # basic vmin RING KILL CHK trigger, wrong VoltageTargets causing fd==NYET
                        ]
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)
            obj = Checkers()

            class fake_mtpl_obj:
                @staticmethod
                def is_bypassed(mod, test):
                    for md, tn, data, _ in stpldata:
                        if md == mod and test == tn:
                            if data.get('BypassPort') == '1':
                                return True
                    return False

            obj.run_check(obj.mtl_vmintcflicbchk, True, stpldata, bomflows, fake_mtpl_obj)
            self.assertEqual(obj.sum[obj.mtl_vmintcchk], {'ARR_CORE_CXX': {'e': 2, 'w': 1, 'p': 0},
                                                          'ARR_RING_CXX': {'e': 1, 'w': 0, 'p': 0}
                                                          })
            self.assertEqual(obj.msgstr, ['ARR_CORE_CXX -Error189- Test:EVMINS_CR_VMIN_K_CCRF1_X_X_X_X_TESTC_1003 missing/incorrect required data=CheckFlow(CORE) on param=FlowIndexCallbackName; bypass=False',
                                          'ARR_CORE_CXX -Error189- Test:EVMINS_CR_VMIN_K_CCRF1_X_X_X_X_TESTD_1002 missing/incorrect required data=CheckFlow(CORE) on param=FlowIndexCallbackName; bypass=False',
                                          'ARR_CORE_CXX -Warning189- Test:EVMINS_CR_VMIN_K_CCRF1_X_X_X_X_TESTD_1003 missing/incorrect required data=CheckFlow(CORE) on param=FlowIndexCallbackName; bypass=True',
                                          'ARR_RING_CXX -Error189- Test:EVMINS_CLR_VMIN_K_CCLRF1_X_X_X_X_TESTH_1001 Unable to determine FlowDomain with VoltageTargets=CLR CornerID=CLR0@F1; bypass=False'
                                          ])

    def test_mtl_cttrchk(self):
        with TempDir(name=True, chdir=True) as tdir:
            bomflows = ['1001', '1002', '1003', '1201', '1202', '1203']
            stpldata = [('FUN_CORE_CXX', 'EVMINS_CR_VMIN_K_SCRF1_X_VCORE_F1_800_SLCA_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'CornerIdentifiers': 'CR5@F1,CR4@F1,CR3@F1,CR2@F1,CRU1@F1,CRU0@F1', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'RecoveryMode': 'RecoveryLoop', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin'}, ''),  # basic vmin SRH pass
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_SCRF1_X_VCORE_F1_800_MLCA_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'CornerIdentifiers': 'CR5@F1,CR4@F1,CR3@F1,CR2@F1,CRU1@F1,CRU0@F1', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'RecoveryMode': 'RecoveryLoop', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin'}, ''),  # basic vmin SRH pass
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F6_5000_MLCA_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'CornerIdentifiers': 'CR5@F6,CR4@F6,CR3@F6,CR2@F6,CRU1@F6,CRU0@F6', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'RecoveryMode': 'NoRecovery', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin'}, ''),  # basic vmin CHK pass
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F5_5000_MLCB_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'CornerIdentifiers': 'CR5@F6,CR4@F6,CR3@F6,CR2@F6,CRU1@F6,CRU0@F6', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'RecoveryMode': 'NoRecovery', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin'}, ''),  # warning177: subflow freq do not match freq corner
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F6_500A_MLCC_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'CornerIdentifiers': 'CR5@F6,CR4@F6,CR3@F6,CR2@F6,CRU1@F6,CRU0@F6', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'RecoveryMode': 'NoRecovery', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin'}, ''),  # warning176: freq value has letter instead of digit
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F5_500A_MLCB_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'CornerIdentifiers': 'CR5@F6,CR4@F6,CR3@F6,CR2@F6,CRU1@F6,CRU0@F6', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'RecoveryMode': 'NoRecovery', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin'}, ''),  # warning176: subflow freq do not match freq corner AND freq value has letter instead of digit
                        ('FUN_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F5_500A_SLCB_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'CornerIdentifiers': 'CR5@F6,CR4@F6,CR3@F6,CR2@F6,CRU1@F6,CRU0@F6', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'RecoveryMode': 'NoRecovery', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin'}, ''),  # warning176: subflow freq do not match freq corner AND freq value has letter instead of digit
                        ('FUN_CORE_CXX', 'EVMINS_CR_VMIN_K_EARTH_X_VCORE_F5_5000_SLCC_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'CornerIdentifiers': 'CR5@F6,CR4@F6,CR3@F6,CR2@F6,CRU1@F6,CRU0@F6', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'RecoveryMode': 'NoRecovery', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin'}, ''),  # skip: subflow is not in sccttrflows
                        ('FUN_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F6_6000_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'CornerIdentifiers': 'CR5@F6,CR4@F6,CR3@F6,CR2@F6,CRU1@F6,CRU0@F6', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'RecoveryMode': 'NoRecovery', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin'}, ''),  # basic vmin SRH pass no user field data
                        ('FUN_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F5_X_1201', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'CornerIdentifiers': 'CR5@F6,CR4@F6,CR3@F6,CR2@F6,CRU1@F6,CRU0@F6', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'RecoveryMode': 'NoRecovery', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin'}, ''),  # warning177/178
                        ('FUN_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F6_X_1202', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'CornerIdentifiers': 'CR5@F6,CR4@F6,CR3@F6,CR2@F6,CRU1@F6,CRU0@F6', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'RecoveryMode': 'NoRecovery', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin'}, ''),  # warning177/178
                        ('ARR_MBIST_SXX', 'XSA_SOC_VMIN_K_CSNF1_X_VCCSA_F1_X_SIDEROM_KS_1203', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'TestMode': 'SingleVmin'}, ''),  # warning178 SOC SRH
                        ]
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)
            obj = Checkers()
            obj.run_check(obj.mtl_cttrchk, False, stpldata, bomflows)
            self.assertEqual(obj.sum[obj.mtl_cttrchk], {'ARR_CORE_CXX': {'e': 0, 'w': 3, 'p': 0},
                                                        'ARR_MBIST_SXX': {'e': 0, 'w': 1, 'p': 0},
                                                        'FUN_CORE_CXX': {'e': 0, 'w': 4, 'p': 0}
                                                        })
            self.assertEqual(obj.msgstr, ['ARR_CORE_CXX -Warning177- Test:EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F5_5000_MLCB_1001 sf=CCRF6 and fc=F5 do not match',
                                          'ARR_CORE_CXX -Warning176- Test:EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F6_500A_MLCC_1001 does not follow speedflow naming',
                                          'ARR_CORE_CXX -Warning176- Test:EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F5_500A_MLCB_1001 does not follow speedflow naming',
                                          'FUN_CORE_CXX -Warning176- Test:EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F5_500A_SLCB_1001 does not follow speedflow naming',
                                          'FUN_CORE_CXX -Warning177- Test:EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F5_X_1201 sf=CCRF6 and fc=F5 do not match',
                                          'FUN_CORE_CXX -Warning178- Test:EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F5_X_1201 Frequency=X should all be digits',
                                          'FUN_CORE_CXX -Warning178- Test:EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F6_X_1202 Frequency=X should all be digits',
                                          'ARR_MBIST_SXX -Warning178- Test:XSA_SOC_VMIN_K_CSNF1_X_VCCSA_F1_X_SIDEROM_KS_1203 Frequency=X should all be digits'
                                          ])

    def test_mtl_cttrbnmchk(self):
        with TempDir(name=True, chdir=True) as tdir:
            bomflows = ['1001', '1002', '1003', '1201', '1202', '1203']
            stpldata = [('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F6_5000_MLCA_1001', {'ScoreboardBaseNumber': '11211', 'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'CornerIdentifiers': 'CR5@F6,CR4@F6,CR3@F6,CR2@F6,CRU1@F6,CRU0@F6', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'RecoveryMode': 'NoRecovery', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin'}, ''),  # basic vmin CHK pass with basenumber + speedflow
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F6_5000_MLCA_1002', {'ScoreboardBaseNumber': '11211', 'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'CornerIdentifiers': 'CR5@F6,CR4@F6,CR3@F6,CR2@F6,CRU1@F6,CRU0@F6', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'RecoveryMode': 'NoRecovery', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin'}, ''),  # basic vmin CHK pass with basenumber + speedflow
                        ('FUN_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F6_5000_MLCA_1201', {'ScoreboardBaseNumber': '12345', 'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'CornerIdentifiers': 'CR5@F6,CR4@F6,CR3@F6,CR2@F6,CRU1@F6,CRU0@F6', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'RecoveryMode': 'NoRecovery', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin'}, ''),  # test in one module sharing same basenumber
                        ('FUN_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F6_5000_MLCB_1201', {'ScoreboardBaseNumber': '12345', 'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'CornerIdentifiers': 'CR5@F6,CR4@F6,CR3@F6,CR2@F6,CRU1@F6,CRU0@F6', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'RecoveryMode': 'NoRecovery', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin'}, ''),  # test in one module sharing same basenumber
                        ('SCN_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F6_5000_ATPG_1201', {'ScoreboardBaseNumber': '12346', 'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'CornerIdentifiers': 'CR5@F6,CR4@F6,CR3@F6,CR2@F6,CRU1@F6,CRU0@F6', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'RecoveryMode': 'NoRecovery', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin'}, ''),  # basenumber shared with another module
                        ('FUN_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F6_5000_SLC0_1201', {'ScoreboardBaseNumber': '12346', 'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'CornerIdentifiers': 'CR5@F6,CR4@F6,CR3@F6,CR2@F6,CRU1@F6,CRU0@F6', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'RecoveryMode': 'NoRecovery', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin'}, ''),  # basenumber shared with another module
                        ('FUN_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F6_5000_SLC0_1201', {'ScoreboardBaseNumber': '2346', 'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'CornerIdentifiers': 'CR5@F6,CR4@F6,CR3@F6,CR2@F6,CRU1@F6,CRU0@F6', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'RecoveryMode': 'NoRecovery', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin'}, ''),  # basenumber is not 5digits
                        ('FUN_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F6_5000_SLICE0', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'CornerIdentifiers': 'CR5@F6,CR4@F6,CR3@F6,CR2@F6,CRU1@F6,CRU0@F6', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'RecoveryMode': 'NoRecovery', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin'}, ''),  # no basenumber
                        ('FUN_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F6_5000_SLICE1', {'ScoreboardBaseNumber': '0', 'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'CornerIdentifiers': 'CR5@F6,CR4@F6,CR3@F6,CR2@F6,CRU1@F6,CRU0@F6', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'RecoveryMode': 'NoRecovery', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin'}, ''),  # basenumber is not 5digits
                        ]
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)
            obj = Checkers()
            obj.run_check(obj.mtl_cttrbnmchk, True, stpldata, bomflows)
            self.assertEqual(obj.sum[obj.mtl_cttrchk], {'ARR_CORE_CXX': {'e': 0, 'w': 0, 'p': 0},
                                                        'FUN_CORE_CXX': {'e': 4, 'w': 0, 'p': 0},
                                                        'SCN_CORE_CXX': {'e': 1, 'w': 0, 'p': 0}
                                                        })
            self.assertEqual(obj.msgstr, ["SCN_CORE_CXX -Error197- Base#:12346 in test:EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F6_$FREQ_ATPG_$FLOWINDEX is used across multiple modules:['SCN_CORE_CXX', 'FUN_CORE_CXX']",
                                          "FUN_CORE_CXX -Error197- Base#:12346 in test:EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F6_$FREQ_SLC0_$FLOWINDEX is used across multiple modules:['SCN_CORE_CXX', 'FUN_CORE_CXX']",
                                          "FUN_CORE_CXX -Error198- Base#:2346 in test:EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F6_$FREQ_SLC0_$FLOWINDEX not eq to 5digits inside module:['FUN_CORE_CXX']",
                                          "FUN_CORE_CXX -Error199- Test:EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F6_$FREQ_MLCA_$FLOWINDEX shares Base#:12345 with other tests inside module",
                                          "FUN_CORE_CXX -Error199- Test:EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F6_$FREQ_MLCB_$FLOWINDEX shares Base#:12345 with other tests inside module"
                                          ])

    def test_mtl_cttredgechk(self):
        with TempDir(name=True, chdir=True) as tdir:
            bomflows = ['1001', '1002', '1003', '1201', '1202', '1203']
            stpldata = [('ARR_CORE_CXX', 'EVMINS_CR_USER_K_CCRF6_X_VCORE_F6_2000_AUXT', {'TEMPLATE': 'iCAuxialliary', 'BypassPort': '-1', '_EDCKIL': 'KIL'}, ''),  # Non-speedflow test
                        ('ARR_CORE_CXX', 'EVMINS_CR_USER_K_CCRF6_X_VCORE_F6_5000_AUXT_1001', {'TEMPLATE': 'iCAuxialliary', 'BypassPort': '-1', '_EDCKIL': 'KIL'}, ''),  # NonVminTC template test
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_SCRF6_X_VCORE_F6_5000_BIST_1001', {'ScoreboardBaseNumber': '11211', 'ScoreboardEdgeTicks': '3', 'ScoreboardMaxFails': '20', 'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'CornerIdentifiers': 'CR5@F6,CR4@F6,CR3@F6,CR2@F6,CRU1@F6,CRU0@F6', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'RecoveryMode': 'NoRecovery', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin'}, ''),  # skip test not in CHK subflow
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F6_5000_BIST_1001', {'ScoreboardBaseNumber': '11211', 'ScoreboardEdgeTicks': '3', 'ScoreboardMaxFails': '20', 'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'CornerIdentifiers': 'CR5@F6,CR4@F6,CR3@F6,CR2@F6,CRU1@F6,CRU0@F6', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'RecoveryMode': 'NoRecovery', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin'}, ''),  # basic vmin CHK pass with basenumber + speedflow
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F6_5000_BIST_1002', {'ScoreboardBaseNumber': '11211', 'ScoreboardEdgeTicks': '3', 'ScoreboardMaxFails': '20', 'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'CornerIdentifiers': 'CR5@F6,CR4@F6,CR3@F6,CR2@F6,CRU1@F6,CRU0@F6', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'RecoveryMode': 'NoRecovery', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin'}, ''),  # basic vmin CHK pass with basenumber + speedflow
                        ('FUN_CORE_CXX', 'EVMINS_CR_FUNC_K_CCRF6_X_VCORE_F6_5000_MLCA_1001', {'ScoreboardBaseNumber': '14401', 'ScoreboardEdgeTicks': '3', 'ScoreboardMaxFails': '20', 'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'CornerIdentifiers': 'CR5@F6,CR4@F6,CR3@F6,CR2@F6,CRU1@F6,CRU0@F6', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'RecoveryMode': 'NoRecovery', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'Scoreboard'}, ''),  # basic func CHK illegal
                        ('FUN_CORE_CXX', 'EVMINS_CR_VMIN_E_CCRF6_X_VCORE_F6_5000_MLCA_1002', {'ScoreboardBaseNumber': '14402', 'ScoreboardEdgeTicks': '3', 'ScoreboardMaxFails': '20', 'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'EDC', 'CornerIdentifiers': 'CR5@F6,CR4@F6,CR3@F6,CR2@F6,CRU1@F6,CRU0@F6', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'RecoveryMode': 'NoRecovery', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin'}, ''),  # basic vmin CHK pass with basenumber + speedflow
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F6_4000_BIST_1001', {'ScoreboardBaseNumber': '1225', 'ScoreboardEdgeTicks': '3', 'ScoreboardMaxFails': '20', 'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'CornerIdentifiers': 'CR5@F6,CR4@F6,CR3@F6,CR2@F6,CRU1@F6,CRU0@F6', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'RecoveryMode': 'NoRecovery', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin'}, ''),  # fail basenumber not equal to 5
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F6_4000_BIST_1002', {'ScoreboardBaseNumber': '11225', 'ScoreboardEdgeTicks': '1', 'ScoreboardMaxFails': '20', 'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'CornerIdentifiers': 'CR5@F6,CR4@F6,CR3@F6,CR2@F6,CRU1@F6,CRU0@F6', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'RecoveryMode': 'NoRecovery', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin'}, ''),  # fail edge tick != 3
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F6_4000_BIST_1003', {'ScoreboardBaseNumber': '11225', 'ScoreboardEdgeTicks': '1', 'ScoreboardMaxFails': '10', 'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'CornerIdentifiers': 'CR5@F6,CR4@F6,CR3@F6,CR2@F6,CRU1@F6,CRU0@F6', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'RecoveryMode': 'NoRecovery', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin'}, ''),  # fail max fail != 20
                        ]
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)
            obj = Checkers()
            obj.run_check(obj.mtl_cttredgechk, True, stpldata, bomflows)
            self.assertEqual(obj.sum[obj.mtl_cttrchk], {'ARR_CORE_CXX': {'e': 3, 'w': 1, 'p': 0}})
            self.assertEqual(obj.msgstr, ['ARR_CORE_CXX -Error200- Base#:1225 in CHK test:EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F6_4000_BIST_1001 is not eq to 5digits',
                                          'ARR_CORE_CXX -Error201- EdgeTick:1 in CHK test:EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F6_4000_BIST_1002 is not eq to 3',
                                          'ARR_CORE_CXX -Error201- EdgeTick:1 in CHK test:EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F6_4000_BIST_1003 is not eq to 3',
                                          'ARR_CORE_CXX -Warning202- ScoreboardMaxFails:10 in CHK test:EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F6_4000_BIST_1003 is not eq to 20'
                                          ])

    def test_mtl_cttrbnmdiechk(self):
        with TempDir(name=True, chdir=True) as tdir:
            bomflows = ['1001', '1002', '1003', '1201', '1202', '1203']
            stpldata = [('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_SCRF6_X_VCORE_F6_5000_BIST_1001', {'ScoreboardBaseNumber': '11211', 'ScoreboardEdgeTicks': '3', 'ScoreboardMaxFails': '20', 'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'TestMode': 'MultiVmin'}, ''),  # skip test not in CHK subflow
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F6_4000_BIST_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'TestMode': 'MultiVmin'}, ''),  # skip test no base#
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F6_5000_BIST_1001', {'ScoreboardBaseNumber': '11211', 'ScoreboardEdgeTicks': '3', 'ScoreboardMaxFails': '20', 'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'TestMode': 'MultiVmin'}, ''),  # pass test in CHK CDIE subflow with cdie bnm start
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F6_3000_BIST_1001', {'ScoreboardBaseNumber': '1225', 'ScoreboardEdgeTicks': '3', 'ScoreboardMaxFails': '20', 'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'TestMode': 'MultiVmin'}, ''),  # skip basenumber not equal to 5
                        ('FUN_CORE_CXX', 'EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F6_5000_MLCA_1001', {'ScoreboardBaseNumber': '22211', 'ScoreboardEdgeTicks': '3', 'ScoreboardMaxFails': '20', 'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'TestMode': 'MultiVmin'}, ''),  # fail test in CHK CDIE subflow without cdie bnm start
                        ('ARR_GT_GXX', 'EVMINS_GT_VMIN_K_CGTF6_X_VCCGT_F6_3000_BIST_1001', {'ScoreboardBaseNumber': '24211', 'ScoreboardEdgeTicks': '3', 'ScoreboardMaxFails': '20', 'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'TestMode': 'SingleVmin'}, ''),  # pass test in CHK GDIE subflow with gdie bnm start
                        ('ARR_GT_GXX', 'EVMINS_GT_VMIN_K_CGTF6_X_VCCGT_F6_4000_BIST_1001', {'ScoreboardBaseNumber': '34211', 'ScoreboardEdgeTicks': '3', 'ScoreboardMaxFails': '20', 'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'TestMode': 'SingleVmin'}, ''),  # fail test in CHK GDIE subflow without gdie bnm start
                        ('ARR_SOC_SXX', 'EVMINS_SAQ_VMIN_K_CSNF3_X_VCCSA_F3_3000_BIST_1001', {'ScoreboardBaseNumber': '44421', 'ScoreboardEdgeTicks': '3', 'ScoreboardMaxFails': '20', 'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'TestMode': 'SingleVmin'}, ''),  # pass test in CHK SOC subflow with soc bnm start
                        ('ARR_SOC_SXX', 'EVMINS_SAQ_VMIN_K_CSNF3_X_VCCSA_F3_2000_BIST_1001', {'ScoreboardBaseNumber': '34421', 'ScoreboardEdgeTicks': '3', 'ScoreboardMaxFails': '20', 'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'TestMode': 'SingleVmin'}, ''),  # fail test in CHK SOC subflow without soc bnm start
                        ('ARR_ADM_BXX', 'EVMINS_ADM_VMIN_K_CBSF1_X_VCCSA_F1_1000_BIST_1001', {'ScoreboardBaseNumber': '54421', 'ScoreboardEdgeTicks': '3', 'ScoreboardMaxFails': '20', 'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'TestMode': 'SingleVmin'}, ''),  # ELSE test in CHK ADM subflow with adm/base bnm start
                        ]
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)
            obj = Checkers()
            obj.run_check(obj.mtl_cttrbnmdiechk, True, stpldata, bomflows)
            self.assertEqual(obj.sum[obj.mtl_cttrchk], {'ARR_ADM_BXX': {'e': 0, 'w': 0, 'p': 0},
                                                        'ARR_CORE_CXX': {'e': 0, 'w': 0, 'p': 0},
                                                        'ARR_GT_GXX': {'e': 1, 'w': 0, 'p': 0},
                                                        'ARR_SOC_SXX': {'e': 1, 'w': 0, 'p': 0},
                                                        'FUN_CORE_CXX': {'e': 1, 'w': 0, 'p': 0}
                                                        })
            self.assertEqual(obj.msgstr, ['FUN_CORE_CXX -Error203- Base#:22211 in CDIE CHK test:EVMINS_CR_VMIN_K_CCRF6_X_VCORE_F6_5000_MLCA_1001 should start with number:1',
                                          'ARR_GT_GXX -Error204- Base#:34211 in GDIE CHK test:EVMINS_GT_VMIN_K_CGTF6_X_VCCGT_F6_4000_BIST_1001 should start with number:2',
                                          'ARR_SOC_SXX -Error205- Base#:34421 in SOC CHK test:EVMINS_SAQ_VMIN_K_CSNF3_X_VCCSA_F3_2000_BIST_1001 should start with number:4'
                                          ])

    def test_mtl_reqdrvprlmvchk(self):
        with TempDir(name=True, chdir=True) as tdir:  # pass scenario
            stpldata = [('FUN_CORE_CXX', 'EVMINS_CR_VMIN_K_SCRF1_X_VCORE_F1_800_SLCA_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'CornerIdentifiers': 'CR5@F1,CR4@F1,CR3@F1,CR2@F1,CRU1@F1,CRU0@F1', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'RecoveryMode': 'RecoveryLoop', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin'}, ''),  # basic vmin SRH pass
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_SCRF1_X_VCORE_F1_800_MLCA_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'CornerIdentifiers': 'CR5@F1,CR4@F1,CR3@F1,CR2@F1,CRU1@F1,CRU0@F1', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'RecoveryMode': 'RecoveryLoop', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin'}, ''),  # basic vmin SRH pass
                        ('DRV_RESET_CXX', 'RESET_X_FUNC_K_BEGCPU_X_INF_X_X_LR_PHASE2', {'TEMPLATE': 'VminTC', 'BypassPort': '-1'}, ''),  # DRV_RESET_CXX required test
                        ('DRV_RESET_GXX', 'RESET_X_FUNC_K_BEGGT_X_INF_X_X_LR_PHASE2_PRIME', {'TEMPLATE': 'VminTC', 'BypassPort': '-1'}, ''),  # DRV_RESET_GXX required test
                        ('DRV_RESET_GXX', 'RESET_X_FUNC_K_BEGGT_X_INF_X_X_LR_HELLO', {'TEMPLATE': 'VminTC', 'BypassPort': '-1'}, '')  # DRV_RESET_GXX other/else test
                        ]
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)
            obj = CheckersUT()
            obj.run_check(obj.mtl_reqdrvprlmvchk, True, stpldata)
            self.assertEqual(obj.sum[obj.mtl_reqdrvprlmvchk], {'DRV_RESET_CXX': {'e': 0, 'w': 0, 'p': 1},
                                                               'DRV_RESET_GXX': {'e': 0, 'w': 0, 'p': 1}
                                                               })
            self.assertEqual(obj.msgstr, [])

        with TempDir(name=True, chdir=True) as tdir:  # fail scenario
            stpldata = [('FUN_CORE_CXX', 'EVMINS_CR_VMIN_K_SCRF1_X_VCORE_F1_800_SLCA_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'CornerIdentifiers': 'CR5@F1,CR4@F1,CR3@F1,CR2@F1,CRU1@F1,CRU0@F1', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'RecoveryMode': 'RecoveryLoop', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin'}, ''),  # basic vmin SRH pass
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_SCRF1_X_VCORE_F1_800_MLCA_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL', 'CornerIdentifiers': 'CR5@F1,CR4@F1,CR3@F1,CR2@F1,CRU1@F1,CRU0@F1', 'ForwardingMode': 'InputOutput', 'FlowIndex': '1', 'RecoveryMode': 'RecoveryLoop', 'RecoveryOptions': 'RWCDefeaturingVector_CLASS_P68G2,6', 'RecoveryTrackingIncoming': 'CR5,CR4,CR3,CR2,CR1,CR0', 'RecoveryTrackingOutgoing': 'CR5,CR4,CR3,CR2,CR1,CR0', 'TestMode': 'MultiVmin'}, ''),  # basic vmin SRH pass
                        ('DRV_RESET_CXX', 'RESET_X_FUNC_K_BEGCPU_X_INF_X_X_LR_PHASE2', {'TEMPLATE': 'VminTC', 'BypassPort': '-1'}, '')  # DRV_RESET_CXX required test
                        ]
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)
            obj = CheckersUT()
            obj.run_check(obj.mtl_reqdrvprlmvchk, True, stpldata)
            self.assertEqual(obj.sum[obj.mtl_reqdrvprlmvchk], {'DRV_RESET_CXX': {'e': 0, 'w': 0, 'p': 1},
                                                               'DRV_RESET_GXX': {'e': 1, 'w': 0, 'p': 0}
                                                               })
            self.assertEqual(obj.msgstr, ['DRV_RESET_GXX -Error179- Parallel MV loop test:DRV_RESET_GXX::RESET_X_FUNC_K_BEGGT_X_INF_X_X_LR_PHASE2_PRIME is missing'])

    def test_mtl_dedcbbchk(self):
        with TempDir(name=True, chdir=True) as tdir:  # missing barebone scenario
            stpldata = [('FUN_CORE_CXX', 'EVMINS_CR_VMIN_K_SCRF1_X_VCORE_F1_800_SLC', {'TEMPLATE': 'VminTC', 'BypassPort': '-1'}, '')]  # non dedc test, skip
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)
            obj = Checkers()

            class fake_mtpl_obj:
                @staticmethod
                def is_bypassed(mod, test):
                    for md, tn, data, _ in stpldata:
                        if md == mod and test == tn:
                            if data.get('BypassPort') == '1':
                                return True
                            elif data.get('bypass_global') == '1':
                                return True
                    return False

            obj.run_check(obj.mtl_dedcbbchk, True, stpldata, fake_mtpl_obj)
            self.assertEqual(obj.sum[obj.mtl_dedcbbchk], {'TPI_DEDCHIST_YXX': {'e': 1, 'w': 0, 'p': 0}})
            self.assertEqual(obj.msgstr, ['TPI_DEDCHIST_YXX -Error190- DEDC MasterBarebone file for comparison checks is missing: TPI_DEDCHIST_YXX/InputFiles/DEDC_SHERLOCK_MASTERBAREBONE.txt'])

        with TempDir(name=True, chdir=True) as tdir:  # pass scenario /Modules/DRV_RESET_IXPK/InputFiles/DRV_RESET_IOEP_DEDC_PROD.xml
            stpldata = [('FUN_CORE_CXX', 'EVMINS_CR_VMIN_K_SCRF1_X_VCORE_F1_800_SLC', {'TEMPLATE': 'VminTC', 'BypassPort': '-1'}, ''),  # non dedc test, skip
                        ('ARR_CORE_CXX', 'EVMINS_CR_DEDC_K_DEDC_X_VCORE_F1_800_MLC', {'TEMPLATE': 'iCDEDCTest', 'bypass_global': '-1', 'config_file': './Modules/ARR_CORE_CXX/InputFiles/ARR_CORE_CXX_DEDC_PROD.xml'}, ''),  # dedc, matches barebone
                        ('FUN_CORE_CXX', 'EVMINS_CR_DEDC_K_DEDC_X_VCORE_F1_800_FC', {'TEMPLATE': 'iCDEDCTest', 'bypass_global': '-1', 'config_file': './Modules/FUN_CORE_CXX/InputFiles/FUN_CORE_CXX_DEDC_PROD.xml'}, ''),  # dedc, mis-matches barebone, unbypassed
                        ('FUN_CORE_CXX', 'EVMINS_CR_DEDC_K_DEDC_X_VCORE_F2_800_FC', {'TEMPLATE': 'iCDEDCTest', 'bypass_global': '1', 'config_file': './Modules/FUN_CORE_CXX/InputFiles/FUN_CORE_CXX_DEDC_PRODZ.xml'}, ''),  # dedc, mis-matches barebone, bypassed
                        ('SCN_CORE_CXX', 'EVMINS_CR_DEDC_K_DEDC_X_VCORE_F1_800_ATPG', {'TEMPLATE': 'iCDEDCTest', 'bypass_global': '-1'}, ''),  # dedc, cfg file not coded, unbypassed
                        ('SCN_CORE_CXX', 'EVMINS_CR_DEDC_K_DEDC_X_VCORE_F2_800_ATPG', {'TEMPLATE': 'iCDEDCTest', 'bypass_global': '1'}, ''),  # dedc, cfg file not coded, bypassed
                        ('ARR_CORE_CXX', 'EVMINS_CR_DEDC_K_DEDC_X_VCORE_F1_800_BIST', {'TEMPLATE': 'iCDEDCTest', 'bypass_global': '-1', 'config_file': './Modules/ARR_CORE_CXX/InputFiles/ARR_CORE_CXX_DEDC_ENGR.xml'}, ''),  # dedc, cfg coded but file is missing, unbypassed
                        ('ARR_CORE_CXX', 'EVMINS_CR_DEDC_K_DEDC_X_VCORE_F2_800_BIST', {'TEMPLATE': 'iCDEDCTest', 'bypass_global': '1', 'config_file': './Modules/ARR_CORE_CXX/InputFiles/ARR_CORE_CXX_DEDC_ENGRZ.xml'}, '')  # dedc, cfg coded but file is missing, bypassed
                        ]
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)

            File('%s/Modules/TPI_DEDCHIST_YXX/InputFiles/DEDC_SHERLOCK_MASTERBAREBONE.txt' % tdir).touch('I will wait', mkdir=True, newfile=True)
            File('%s/Modules/ARR_CORE_CXX/InputFiles/ARR_CORE_CXX_DEDC_PROD.xml' % tdir).touch('I will wait', mkdir=True, newfile=True)
            File('%s/Modules/FUN_CORE_CXX/InputFiles/FUN_CORE_CXX_DEDC_PROD.xml' % tdir).touch('I\'ll find you', mkdir=True, newfile=True)
            File('%s/Modules/FUN_CORE_CXX/InputFiles/FUN_CORE_CXX_DEDC_PRODZ.xml' % tdir).touch('I\'ll find you', mkdir=True, newfile=True)
            obj = Checkers()

            class fake_mtpl_obj:
                @staticmethod
                def is_bypassed(mod, test):
                    for md, tn, data, _ in stpldata:
                        if md == mod and test == tn:
                            if data.get('BypassPort') == '1':
                                return True
                            elif data.get('bypass_global') == '1':
                                return True
                    return False

            obj.run_check(obj.mtl_dedcbbchk, True, stpldata, fake_mtpl_obj)
            self.assertEqual(obj.sum[obj.mtl_dedcbbchk], {'ARR_CORE_CXX': {'e': 1, 'w': 1, 'p': 0},
                                                          'FUN_CORE_CXX': {'e': 1, 'w': 1, 'p': 0},
                                                          'SCN_CORE_CXX': {'e': 1, 'w': 1, 'p': 0}
                                                          })
            self.assertEqual(obj.msgstr, ['FUN_CORE_CXX -Error191- Test:EVMINS_CR_DEDC_K_DEDC_X_VCORE_F1_800_FC byp:False dedc file:./Modules/FUN_CORE_CXX/InputFiles/FUN_CORE_CXX_DEDC_PROD.xml does not match the dedc barebone:./Modules/TPI_DEDCHIST_YXX/InputFiles/DEDC_SHERLOCK_MASTERBAREBONE.txt',
                                          'FUN_CORE_CXX -Warning191- Test:EVMINS_CR_DEDC_K_DEDC_X_VCORE_F2_800_FC byp:True dedc file:./Modules/FUN_CORE_CXX/InputFiles/FUN_CORE_CXX_DEDC_PRODZ.xml does not match the dedc barebone:./Modules/TPI_DEDCHIST_YXX/InputFiles/DEDC_SHERLOCK_MASTERBAREBONE.txt',
                                          'SCN_CORE_CXX -Error192- Test:EVMINS_CR_DEDC_K_DEDC_X_VCORE_F1_800_ATPG uses dedc but does not have cfg file. bypass:False',
                                          'SCN_CORE_CXX -Warning192- Test:EVMINS_CR_DEDC_K_DEDC_X_VCORE_F2_800_ATPG uses dedc but does not have cfg file. bypass:True',
                                          'ARR_CORE_CXX -Error193- Test:EVMINS_CR_DEDC_K_DEDC_X_VCORE_F1_800_BIST uses dedc cfg:./Modules/ARR_CORE_CXX/InputFiles/ARR_CORE_CXX_DEDC_ENGR.xml but file does not exist. bypass:False',
                                          'ARR_CORE_CXX -Warning193- Test:EVMINS_CR_DEDC_K_DEDC_X_VCORE_F2_800_BIST uses dedc cfg:./Modules/ARR_CORE_CXX/InputFiles/ARR_CORE_CXX_DEDC_ENGRZ.xml but file does not exist. bypass:True'
                                          ])

    def test_gen_edcvskillchk(self):
        with TempDir(name=True, chdir=True) as tdir:  # missing barebone scenario
            stpldata = [('FUN_CORE_CXX', 'TEST', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL'}, ''),  # unable to splice testname
                        ('FUN_CORE_CXX', 'EVMINS_CR_VMIN_K_SCRF1_X_VCORE_F1_800_SLC_1201', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL'}, ''),  # pass: kill la KIL
                        ('FUN_CORE_CXX', 'EVMINS_CR_VMIN_E_SCRF2_X_VCORE_F2_800_SLC', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'KIL'}, ''),  # fail: edc la KIL
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_E_SCRF3_X_VCORE_F3_800_SLC_1001', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'EDC'}, ''),  # pass: edc la EDC
                        ('ARR_CORE_CXX', 'EVMINS_CR_VMIN_K_SCRF4_X_VCORE_F4_800_SLC', {'TEMPLATE': 'VminTC', 'BypassPort': '-1', '_EDCKIL': 'EDC'}, '')  # fail: kill la EDC
                        ]  # pass: kill  la KIL
            env = join(tdir, 'EnvironmentFile_CLASS_P68G2.env')
            File(env).touch('', mkdir=True, newfile=True)
            obj = Checkers()

            obj.run_check(obj.gen_edcvskillchk, False, stpldata)
            self.assertEqual(obj.sum[obj.gen_edcvskillchk], {'FUN_CORE_CXX': {'e': 0, 'w': 1, 'p': 0},
                                                             'ARR_CORE_CXX': {'e': 0, 'w': 1, 'p': 0}
                                                             })
            self.assertEqual(obj.msgstr, ['FUN_CORE_CXX -Warning196- Test:EVMINS_CR_VMIN_E_SCRF2_X_VCORE_F2_800_SLC says EDC in tname but port connections are in KILL',
                                          'ARR_CORE_CXX -Warning195- Test:EVMINS_CR_VMIN_K_SCRF4_X_VCORE_F4_800_SLC says KILL in tname but port connections are in EDC'
                                          ])

    @with_(TempDir, chdir=True, startcopy=f'{UT_DIR_REPO}/Simple3', delete=True)
    def test_skip_json(self):     # good template
        # reference first
        obj = Checkers()
        obj.main()
        result = [x for x in obj.allerrors if 'Error112' in x]
        self.assertEqual(len(result), 5)
        self.assertEqual(len(obj.allerrors), 20)

        # with skip
        code = '{ "gen_upchk": "unittestonly" }'
        File('POR_TP/TGLH81/InputFiles/sherlock_skip_checks.json').touch(code, mkdir=True)
        obj = Checkers()
        obj.main()
        result = [x for x in obj.allerrors if 'Error112' in x]
        self.assertEqual(len(result), 0)    # skip took effect!
        self.assertEqual(len(obj.allerrors), 15)

    @with_(TempDir, chdir=True, delete=True)
    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_gen_duplicate_envvar(self):
        # fail case
        tp = TestProgram(f'{UT_DIR}/M28_24G_1_lkle_mvtp/ENG_TP/Class_MTL_M28_DEBUG/EnvironmentFile.env')
        obj = Checkers()
        obj.tpobj = tp
        obj.run_check(obj.gen_duplicate_envvar, True)
        self.assertEqual(obj.sum[obj.gen_duplicate_envvar], {'env': {'e': 1, 'w': 0, 'p': 0}})

        # pass case no issue
        tp = TestProgram(f'{UT_DIR}/Simple3/POR_TP/TGLH81/EnvironmentFile.env')
        obj = Checkers()
        obj.tpobj = tp
        obj.run_check(obj.gen_duplicate_envvar, True)
        self.assertEqual(obj.sum[obj.gen_duplicate_envvar], {})

        # pass case stack
        src = f'{UT_DIR}/Simple3'
        shutil.copytree(src, 'TPL')
        File('TPL/POR_TP/TGLH81/EnvironmentFile.env').touch('''
HDMT_TPL_INPUT_FILES = "def";

HDMT_TPL_INPUT_FILES = "$HDMT_TPL_INPUT_FILES; abc";

HDMT = "a";
''', newfile=True)
        tp = TestProgram(f'TPL/POR_TP/TGLH81/EnvironmentFile.env')
        obj = Checkers()
        obj.tpobj = tp
        obj.run_check(obj.gen_duplicate_envvar, True)
        self.assertEqual(obj.sum[obj.gen_duplicate_envvar], {'env': {'e': 0, 'w': 0, 'p': 0}})

    @with_(TempDir, chdir=True, delete=True)
    @unittest.skipIf(*is_ut_option('SLOW', message="not needed for coverage"))
    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_mtl_integ(self):
        # checks the output on a real MTL program
        src = f'{UT_DIR}/M28_24G_1_lkle_mvtp'
        shutil.copytree(src, 'TPL')
        fullreport = 'ENG_TP/Class_MTL_M28_DEBUG/Reports/FULL_Checkers_Report.txt'

        with Chdir('TPL'):
            self.assertFalse(exists(fullreport))  # test case should not have this file
            with MockVar(sys, "argv", 'sherlock.py'.split()):
                CheckersUT().main()

            # remove empty reports
            ctr = 0
            final = []
            for line in File(fullreport).raw():
                if '-no errors!-' in line:
                    ctr += 1
                    continue
                final.append(line)
            File(f'{fullreport}1').rewrite(''.join(final), 'UT')

            # Below confirms that new routine is hooked up
            self.assertEqual(ctr, 25)      # Count of hooked up error routines (no errors).
            self.assertGoldEqual(f'{fullreport}1', f'{src}/{fullreport}.gold6a')

    @with_(TempDir, chdir=True, delete=True)
    def test_main(self):
        # make sure it runs, using production settings
        src = f'{UT_DIR_REPO}/Simple3'
        shutil.copytree(src, 'TPL')
        fullreport = 'POR_TP/TGLH81/Reports/FULL_Checkers_Report.txt'

        with Chdir('TPL'):
            self.assertFalse(exists(fullreport))  # test case should not have this file
            with MockVar(sys, "argv", 'sherlock.py'.split()):
                Checkers().main()
            self.assertTrue(exists(fullreport))  # test case should have this file

    @with_(TempDir, chdir=True, delete=True)
    @unittest.skip('Skipped due to passfail protocol. Sherlock is obsolete anyway. Need to delete sherlock in future')
    def test_integration(self):
        # system call
        src = f'{UT_DIR_REPO}/Simple3'
        shutil.copytree(src, 'TPL')
        with Chdir('TPL'):
            _, out = SystemCall(f'{ROOT_ENV}/main/sherlock.py').run_outtxt()

        print(out)
        self.assertIn('Error Codes Explained:', out)


LOC = join(dirname(abspath(__file__)))
if __name__ == '__main__':  # pragma: no cover
    unittest.main()
