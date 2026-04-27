#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for nvl_gen_testplace QGATE

"""
import sys
try:
    from setenv_unittest import UT_DIR, ROOT_ENV, UT_DIR_REPO     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR, ROOT_ENV     # must be first import for unittests

from qgates.nvl_gen_testplace import *        # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock
from gadget.gizmo import with_, MockVar
import shutil
from pprint import pformat
import os


ut_blueprint = """BEGCPUMAX BEGGCDMAX BEGHUBMAX BEGIN BEGINCPU BEGINCPUNOM BEGINCPUPKG BEGINGCD BEGINGCDNOM
        BEGINGCDPKG BEGINHUB BEGINHUBNOM BEGINHUBPKG BEGINPCD BEGINPCD1 BEGINPCD2 BEGINPCD3 BEGINPCD4 BEGINPCD5
        BEGINPCD6 BEGINPCDNOM BEGINPCDPKG BEGINPREPRL1 BEGPCDMAX BGEINPREPRL2 CATCLRF1 CATCLRF2 CATCLRF3 CATCLRF4
        CATCLRF4LO CATCLRF5 CATCLRF5LO CATCLRF6 CATCLRF6LO CATCLRFMIN CATF1 CATF2 CATF3 CATF4 CATF4LO CATF5 CATF5LO
        CATF6 CATF6LO CATFMIN CCLRF1 CCLRF2 CCLRF3 CCLRF4 CCLRF4LO CCLRF5 CCLRF5LO CCLRF6 CCLRF6LO CCLRFMIN CCRF1 CCRF2
        CCRF3 CCRF4 CCRF4LO CCRF5 CCRF5LO CCRF6 CCRF6LO CCRFMIN CGTF1 CGTF2 CGTF3 CGTF4 CGTF5 CGTFMIN CSNF1 CSNF2 CSNF3
        CSNFMIN END ENDCPU ENDCPUMAX ENDCPUNOM ENDCPUPKG ENDGCD ENDGCDMAX ENDGCDNOM ENDGCDPKG ENDHUB ENDHUBMAX
        ENDHUBNOM ENDHUBPKG ENDPCD ENDPCDMAX ENDPCDNOM ENDPCDPKG ENDPOSTYBSCPU ENDPOSTYBSGCD ENDPOSTYBSHUB ENDPOSTYBSPCD
        ENDPREPRL0 ENDPREPRL1 ENDPREPRL2 ENDPREPRL3 ENDPREPRL4 ENDYBSCPU ENDYBSGCD ENDYBSHUB ENDYBSPCD EOTRAMP
        F6TEMPDOWN FACT FACTFUSBUILDCPU FACTFUSBUILDGCD FACTFUSBUILDHUB FACTFUSBUILDPCD FACTFUSBURNCPU FACTFUSEBURNGCD
        FACTFUSEBURNHUB FACTFUSEBURNPCD FACTPOSTFUSEBURN FACTPREFUSEBURN FACTPREPRL0 FACTPREPRL1 FINAL HVBICPU
        HVBICPUPKG HVBIGCD HVBIGCDPKG HVBIHUB HVBIHUBPKG HVBIPCD HVBIPCDPKG HVBIPREPRL0 LTTCCOMMON LTTCCPU LTTCCPUMAX
        LTTCCPUPKG LTTCGCD LTTCGCDMAX LTTCGCDPKG LTTCHUB LTTCHUBMAX LTTCHUBPKG LTTCPCD LTTCPCDMAX LTTCPCDPKG LTTCPOST
        LTTCPREPRL0 LTTCPREPRL1 LTTCPREPRL2 LTTCRAMPCHKCPU LTTCRAMPGCD LTTCRAMPHUB LTTCRAMPPCD LTTCRAMPSETCPU MAXATCLRHI
        MAXATCLRLO MAXATHI MAXATLO MAXCLRHI MAXCLRLO MAXCRHI MAXCRLO MAXGT MAXHITEMPDOWN MAXSN PRESRHAT PRESRHCLR
        PRESRHCR PRESRHGT PRESRHSN PSTSRHAT PSTSRHCLR PSTSRHCR PSTSRHGT PSTSRHSN RESUMETEMP SATCLRF1 SATCLRF3 SATCLRF4
        SATCLRF4LO SATCLRF5 SATCLRF5LO SATCLRF6 SATCLRF6LO SATCRLF2 SATF1 SATF2 SATF3 SATF4 SATF4LO SATF5 SATF5LO SATF6
        SATF6LO SCHDCF1 SCLRF1 SCLRF2 SCLRF3 SCLRF4 SCLRF4LO SCLRF5 SCLRF5LO SCLRF6 SCLRF6LO SCRF1 SCRF2 SCRF3 SCRF4
        SCRF4LO SCRF5 SCRF5LO SCRF6 SCRF6LO SGTF1 SGTF2 SGTF3 SGTF4 SGTF5 SHAREDRAILSMAX SHAREDRAILSMAX SHAREDRAILSMIN
        SHAREDRAILSMINLTTC SHAREDRAILSNOM SHAREDRAILSNOMFUSEBURN SPEEDPREPRL0 SPEEDPREPRL1 SPEEDPREPRL2 SPEEDPREPRL3
        SPEEDPREPRL4 SPEEDPREPRL5 SPEEDPREPRL6 SPEEDPREPRL7 SSHDCF1 SSNF1 SSNF2 SSNF3 START STARTANA0CPU STARTANA0GCD
        STARTANA0HUB STARTANA0PCD STARTANA1CPU STARTANA1GCD STARTANA1HUB STARTANA1PCD STARTCPUNOM STARTGCDNOM
        STARTHPTPDRVCPU STARTHPTPDRVGCD STARTHPTPDRVHUB STARTHPTPDRVPCD STARTHUBNOM STARTPATMODS STARTPCDNOM
        STARTPREPRL0 STARTPREPRL1 STARTPREPRL2 STARTPREPRL3 STARTPREPRL4 STARTPWR STARTPWRCPU STARTPWRGCD STARTPWRHUB
        STARTPWRPCD F5TEMPDOWN F4XAT F3XATCCF FMINXCCF BEGINCPUMAX FMAXXCCF F4XATCCF F3XCR FMINXAT F1XCCF FMAXXAT F4XCR
        F4XCCFLO FMINXATCCF F1XAT FMAXXATCCF F4XATLO FMINXCR F1XATCCF FMAXXCR VMAXXCCFLO F4XATCCFLO SPEEDCPUEMPTY0 F1XCR
        VMAXXCCF VMAXXATLO F4XCRLO SPEEDCPUEMPTY1 FMAXXCCFLO VMAXXAT VMAXXATCCFLO F2XCCF SPEEDCPUEMPTY2 FMAXXATLO
        VMAXXATCCF VMAXXCRLO F2XAT FMAXXATCCFLO VMAXXCR F3XCCF F2XATCCF FMAXXCRLO F4XCCF F3XAT F2XCR ALARM BEGINPREPRL0
        LTTCSHAREDRAILSMIN FACTEOTRAMP STARTCPUPATMODSPKG LTTCRAMP STARTSHAREDRAILSNOM ENDSHAREDRAILSMAX
        STARTGCDPATMODSPKG BEGINSHAREDRAILSNOM STARTHUBPATMODSPKG LTTCSHAREDRAILSMIN1 FACTSHAREDRAILSNOM
        STARTPCDPATMODSPKG STARTSHAREDRAILSMIN FACTPREPLRL0 HVBISHAREDRAILSMIN BEGINSHAREDRAILSMAX BEGINPREPRL2
        ENDSHAREDRAILSMIN LTTCSHAREDRAILSMAX FACTPREPLRL1 SPEEDSHAREDRAILSMIN ENDSHAREDRAILSNOM BEGINSHAREDRAILSMIN
        STARTSHAREDRAILSMIN1""".split()


def filter(inp):
    """Filter out the ini records"""
    return [x for x in inp if not x['message'].startswith(('init1 has lower case characters',
                                                           'ini1 has lower case characters'))]


class TestInstName(TestCase):

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/SimpleNVL', chdir=True, delete=True)
    def test_basic_ra(self):
        os.remove('POR_TP/TGLH81/ProgramFlowsTestPlan/ProgramFlows.mtpl')
        File(f'POR_TP/TGLH81/ProgramFlowsTestPlan/ProgramFlows.mtpl_copy').copy('POR_TP/TGLH81/ProgramFlowsTestPlan/ProgramFlows.mtpl')
        os.remove('Modules/SCN/scan.mtpl')
        File(f'Modules/SCN/scan.mtpl_copy').copy('Modules/SCN/scan.mtpl')
        File(f'POR_TP/TGLH81/ProgramFlowsTestPlan/IPC_FLOWS.py').touch('''
MAIN_code = """
START_SubFlow       ARR_CXX   rm2m2 a_SubFlow
SHAREDRAILSNOM    something   this is just a comment a_SubFlow
BEGINCPUPKG_TopFlow SCN_CXX   rm2m2
PREPRLFLOW          SCN_CXX_SubFlow   rm2m2 a_SubFlow
PREPRL2FLOW          SCN_CXX   rm2m2 a_SubFlow
#PREPRL0FLOW_SubFlow          SCN_CXX   rm2m2
INIT    SCN_CXX   rm2m2  a_SubFlow
"""
''')
        File('Shared/POR_TP/TGLH81/ProgramFlowsTestPlan/ProgramFlows_Config.py').touch('''
''', mkdir=True)
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env').init()
        print("Running test_basic_ra...")
        obj = NVLTestPlace(tpobj)
        obj.main()
        # pprint(obj.result)

        expect = '''
243 BASE SHAREDRAILSNOM should be either "SHAREDRAILSNOM_SubFlow" or "SHAREDRAILSNOM_TopFlow
243 BASE PREPRL2FLOW::SCN_CXX should have either "_SubFlow or "_TopFlow
244 ARR CA2TF_ATOM_VMAX_K_SHAREDRAILSNOM_X_CRA_F6_3800_FUSA_VMAX_RECOVERY_1501 is using _SHAREDRAILSNOM_ but does not exist as SubFlow or TopFlow in the ProgramFlows
244 ARR CA2TF_ATOM_VMAX_K_SHAREDRAILSNOM_X_CRA_F6_3800_FUSA_VMAX_RECOVERY_1501 is using _SHAREDRAILSNOM_ but does not exist as SubFlow or TopFlow in the ProgramFlows
244 ARR CA2TF_ATOM_VMAX_K_SHAREDRAILSNOM_X_X_F6_3800_FUSA_VMAX_RECOVERY_1502 is using _SHAREDRAILSNOM_ but does not exist as SubFlow or TopFlow in the ProgramFlows
244 ARR CA2TF_ATOM_VMAX_K_SHAREDRAILSNOM_X_X_F6_3800_FUSA_VMAX_RECOVERY_1502 is using _SHAREDRAILSNOM_ but does not exist as SubFlow or TopFlow in the ProgramFlows
244 SCN CCA_LJ_CMEM_K_BEGINCPUPKG_X_CLRB_F4_TFM is using _BEGINCPUPKG_ but does not exist as SubFlow or TopFlow in the ProgramFlows
244 PTH CAM_ATOM_VMIN_X_CATF1_X_ATA_F1_0400_2001 is using _CATF1_ but does not exist as SubFlow or TopFlow in the ProgramFlows
244 PTH CAM_ATOM_VMIN_X_CATF1_X_ATA_F1_0400_2001 is using _CATF1_ but does not exist as SubFlow or TopFlow in the ProgramFlows
244 PTH CTRL_X_UC_X_START_X_X_X_X_SETTPSGSDSCHECK is using _START_ but does not exist as SubFlow or TopFlow in the ProgramFlows
244 PTH CTRL_X_UC_X_START_X_X_X_X_SETTPSGSDSCHECK is using _START_ but does not exist as SubFlow or TopFlow in the ProgramFlows
(243, 'BASE'): 1
(244, 'SCN'): 1
'''
        self.assertTextEqual(obj.ut_result(), expect)
        self.assertEqual(len(obj.passed), 2)     # START_SubFlow and BEGINCPUPKG_TopFlow passing

        @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple7h', chdir=True, delete=True)
        def test_basic_ra2(self):
            File(f'POR_TP/TGLH81/ProgramFlowsTestPlan/IPC_FLOWS.py').touch('''
    MAIN_code = """
    START_SubFlow       ARR_CXX   rm2m2
    # SHAREDRAILSNOM    something   this is just a comment
    BEGINCPUPKG_TopFlow SCN_CXX   rm2m2
    INIT    SCN_CXX_SubFlow rm2m2
    """
    ''')
            File('Shared/POR_TP/TGLH81/ProgramFlowsTestPlan/ProgramFlows_Config.py').touch('''
    ''', mkdir=True)
            tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env').init()
            print("Running test_basic_RA...")
            obj = NVLTestPlace(tpobj)
            obj.main()
            # pprint(obj.result)

            self.assertEqual(len(obj.result), 6)
            self.assertEqual(len(obj.passed), 2)  # START_SubFlow and BEGINCPUPKG_TopFlow passing


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
