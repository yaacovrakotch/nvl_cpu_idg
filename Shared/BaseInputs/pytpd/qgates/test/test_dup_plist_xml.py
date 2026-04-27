#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for dup_plist_xml.py
"""
import sys
try:
    from setenv_unittest import UT_DIR_REPO, ROOT_ENV     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR_REPO, ROOT_ENV     # must be first import for unittests

from qgates.dup_plist_xml import *        # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock
from os.path import join


class TestDupPlistXml(TestCase):

    def test_basic(self):
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
            obj = DupPlistXml(tpobj)

            plist_files = ['PLIST_ALL_CLASS_P28G1.plist.xml', 'PLIST_ALL_IP_CPU.plist.ipxml', 'PLIST_ALL_IP_PCH.plist.ipxml']
            with MockVar(tpobj, 'get_file_allplist_real', Mock(return_value=plist_files)):
                obj.main()
            self.assertEqual(obj.result, [])                     # failed result
            self.assertEqual(obj.passed, {(207, 'BASE'): 6})     # passed result

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
            obj = DupPlistXml(tpobj)
            plist_files = ['PLIST_ALL_CLASS_P28G1.plist.xml', 'PLIST_ALL_IP_CPU.plist.ipxml', 'PLIST_ALL_IP_PCH.plist.ipxml']
            with MockVar(tpobj, 'get_file_allplist_real', Mock(return_value=plist_files)):
                obj.main()
                print("RESULT: ", obj.result)
            self.maxDiff = None
            self.assertEqual(obj.result, [{'id': 207,
                                           'message': 'DUPLICATE: PTH_BGCEP_c28_CLASS_P28G2.plist: PLIST_ALL_IP_CPU.plist.ipxml and PLIST_ALL_CLASS_P28G1.plist.xml',
                                           'module': 'BASE'}])

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
                obj = DupPlistXml(tpobj)
                plist_files = ['PLIST_ALL_CLASS_P28G1.plist.xml', 'PLIST_ALL_IP_CPU.plist.ipxml',
                               'PLIST_ALL_IP_PCH.plist.ipxml']
                with MockVar(tpobj, 'get_file_allplist_real', Mock(return_value=plist_files)):
                    obj.main()

                expect = [{'id': 207,
                           'message': 'DUPLICATE: array_gt_class_p68g2.plist: '
                                      'PLIST_ALL_IP_CPU.plist.ipxml and PLIST_ALL_CLASS_P28G1.plist.xml',
                           'module': 'BASE'},
                          {'id': 207,
                           'message': 'DUPLICATE: array_gt_class_p68g2.plist: '
                                      'PLIST_ALL_IP_PCH.plist.ipxml and PLIST_ALL_CLASS_P28G1.plist.xml',
                           'module': 'BASE'}]
                self.assertEqual(obj.result, expect)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
