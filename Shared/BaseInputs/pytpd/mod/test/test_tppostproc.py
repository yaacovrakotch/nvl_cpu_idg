#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for tppostproc.py
"""
from setenv_unittest import UT_DIR, UT_DIR_REPO, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests
from mod.tppostproc import *
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.disk import Chdir
from gadget.gizmo import MockVar, with_
from gadget.helperclass import CaptureStdoutLog
from gadget.files import TempDir
from gadget.shell import SystemCall
import sys
import mod.tppostproc as tpppostproc
import shutil


class TestTpPostProc(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic(self):
        src = UT_DIR + '/MTLcheckerMainPass'
        with TempDir(name=True) as tdir:
            shutil.copytree(src, f'{tdir}/MTL')
            with Chdir(f'{tdir}/MTL/TPL'), CaptureStdoutLog() as p:
                TpPostProc().main()
        result = p.getvalue()
        print(result)

        # Make sure module skip is run
        self.assertIn('Success: total instances=', result)

        # Make sure binhack is run
        self.assertIn('bdef processed', result)
        # self.assertIn('is updated by BinHack.main', result)

        self.assertIn('Reading inputFile', result)
        self.assertIn('New inputFile created', result)

    def test_binhack(self):
        with TempDir(name=True, chdir=True) as tdir:
            text = '''
            BinDefs
            {
        BinGroup SoftBins
        {

                LeafBin b100_pass_TPI_END_XXX_CTRL_X_BKGND_K_TESTPLANENDFLOW_X_X_X_X_STOPTIME_1    100    : "b100_pass_TPI_END_XXX_CTRL_X_BKGND_K_TESTPLANENDFLOW_X_X_X_X_STOPTIME_1",    b1_PASS_CMTTRAY_1;
                LeafBin b10010000_pass_pure    10010000    : "b10010000_pass_pure",    b1001_PASS;
LeafBin b10020000_pass_pure    10020000    : "b10020000_pass_pure",    b1002_PASS;
LeafBin b90123401_fail_FAIL_DPS_ALARM    90123401    : "b90123401_fail_FAIL_DPS_ALARM",    b99_FAIL_HARDWARE_ALARM;
LeafBin b90123402_fail_FAIL_DPS_OTHER    90123402    : "b90123402_fail_FAIL_DPS_OTHER",    b99_FAIL_HARDWARE_ALARM;
LeafBin b90123502_fail_FAIL_DPS_OTHER_SHARED_BIN    90123502    : "b90123502_fail_FAIL_DPS_OTHER_SHARED_BIN",    b99_FAIL_HARDWARE_ALARM;
LeafBin b90123501_fail_FAIL_DPS_ALARM_SHARED_BIN    90123501    : "b90123501_fail_FAIL_DPS_ALARM_SHARED_BIN",    b99_FAIL_HARDWARE_ALARM;
# shared bin part5
LeafBin b12345678_pass_SCN    12345678    : "b12345678_pass_SCN",    b1_PASS_CMTTRAY_1;
LeafBin b12345679_pass_SCNX   12345679    : "b12345679_pass_SCNX",   b1_PASS_CMTTRAY_1;
LeafBin b12345680_pass_SCNY   12345680    : "b12345680_pass_SCNY",   b1_PASS_CMTTRAY_1;
# non-shared part5
LeafBin b20038250_fail_SCN_GT_GXX_GT_ALL_VMIN_K_SGTF5_X_VCCGT_F5_1900_GT    20038250    : "b20038250_fail_SCN_GT_GXX_GT_ALL_VMIN_K_SGTF5_X_VCCGT_F5_1900_GT",    b1_PASS_CMTTRAY_1;
# mixed pass and fail - first occurrence
LeafBin b10111101_FAIL_DPS_OTHER    10111101    : "b10111101_FAIL_DPS_OTHER",    b99_FAIL_HARDWARE_ALARM;
LeafBin b10111102_PASS                   10111102    : "b10111102_PASS",    b1_PASS_CMTTRAY_1;
                LeafBin b9993_fail_TPI_BASE    9993    : "b9993_fail_",    b99_FAIL;
                LeafBin b993_fail_TPI_BASE    993    : "b9993_fail_",    b99_FAIL;
        }
        }
'''
            File('a.bdef').touch(text)
            obj = BinHack()
            obj._bin_hack_file('a.bdef')
            expect = '''
            BinDefs
            {
        BinGroup SoftBins
        {

                LeafBin b100_pass_TPI_END_XXX_CTRL_X_BKGND_K_TESTPLANENDFLOW_X_X_X_X_STOPTIME_1    100    : "b100_pass_TPI_END_XXX_CTRL_X_BKGND_K_TESTPLANENDFLOW_X_X_X_X_STOPTIME_1",    b1_PASS_CMTTRAY_1;
                LeafBin b10010000_pass_pure    10010000    : "b10010000_pass_pure",    b1_PASS_CMTTRAY_1;
LeafBin b10020000_pass_pure    10020000    : "b10020000_pass_pure",    b1_PASS_CMTTRAY_1;
LeafBin b90123401_fail_FAIL_DPS_ALARM    90123401    : "b90123401_fail_FAIL_DPS_ALARM",    b99_FAIL_HARDWARE_ALARM;
LeafBin b90123402_fail_FAIL_DPS_OTHER    90123402    : "b90123402_fail_FAIL_DPS_OTHER",    b99_FAIL_HARDWARE_ALARM;
LeafBin b90123502_fail_FAIL_DPS_OTHER_SHARED_BIN    90123502    : "b90123502_fail_FAIL_DPS_OTHER_SHARED_BIN",    b99_FAIL_HARDWARE_ALARM;
LeafBin b90123501_fail_FAIL_DPS_ALARM_SHARED_BIN    90123501    : "b90123501_fail_FAIL_DPS_ALARM_SHARED_BIN",    b99_FAIL_HARDWARE_ALARM;
# shared bin part5
LeafBin b12345678_pass_SCN    12345678    : "b12345678_pass_SCN",    b1_PASS_CMTTRAY_1;
LeafBin b12345679_pass_SCNX   12345679    : "b12345679_pass_SCNX",   b1_PASS_CMTTRAY_1;
LeafBin b12345680_pass_SCNY   12345680    : "b12345680_pass_SCNY",   b1_PASS_CMTTRAY_1;
# non-shared part5
LeafBin b20038250_fail_SCN_GT_GXX_GT_ALL_VMIN_K_SGTF5_X_VCCGT_F5_1900_GT    20038250    : "b20038250_fail_SCN_GT_GXX_GT_ALL_VMIN_K_SGTF5_X_VCCGT_F5_1900_GT",    b1_PASS_CMTTRAY_1;
# mixed pass and fail - first occurrence
LeafBin b10111101_FAIL_DPS_OTHER    10111101    : "b10111101_FAIL_DPS_OTHER",    b99_FAIL_HARDWARE_ALARM;
LeafBin b10111102_PASS                   10111102    : "b10111102_PASS",    b1_PASS_CMTTRAY_1;
                LeafBin b9993_fail_TPI_BASE    9993    : "b9993_fail_",    b99_FAIL;
                LeafBin b993_fail_TPI_BASE    993    : "b9993_fail_",    b99_FAIL;
LeafBin b0282_fail_SCN_GT_GXX_GT_ALL_VMIN_K_SGTF5_X_VCCGT_F5_1900_GT    0282    : "b0282_fail_SCN_GT_GXX_GT_ALL_VMIN_K_SGTF5_X_VCCGT_F5_1900_GT",    b1_PASS_CMTTRAY_1;
LeafBin b1101_FAIL_DPS_OTHER    1101    : "b1101_FAIL_DPS_OTHER",    b99_FAIL_HARDWARE_ALARM;
LeafBin b1102_PASS                   1102    : "b1102_PASS",    b1_PASS_CMTTRAY_1;
LeafBin b1111_PASS                   1111    : "b1111_PASS",    b1_PASS_CMTTRAY_1;
LeafBin b3156_pass_SCN_SHARED_BIN    3156    : "b3156_pass_SCN_SHARED_BIN",    b1_PASS_CMTTRAY_1;
LeafBin b3401_fail_FAIL_DPS_ALARM    3401    : "b3401_fail_FAIL_DPS_ALARM",    b99_FAIL_HARDWARE_ALARM;
LeafBin b3402_fail_FAIL_DPS_OTHER    3402    : "b3402_fail_FAIL_DPS_OTHER",    b99_FAIL_HARDWARE_ALARM;
LeafBin b3501_fail_FAIL_DPS_ALARM_SHARED_BIN    3501    : "b3501_fail_FAIL_DPS_ALARM_SHARED_BIN",    b99_FAIL_HARDWARE_ALARM;
LeafBin b3502_fail_FAIL_DPS_OTHER_SHARED_BIN    3502    : "b3502_fail_FAIL_DPS_OTHER_SHARED_BIN",    b99_FAIL_HARDWARE_ALARM;
LeafBin b5678_pass_SCN    5678    : "b5678_pass_SCN",    b1_PASS_CMTTRAY_1;
LeafBin b5679_pass_SCNX   5679    : "b5679_pass_SCNX",   b1_PASS_CMTTRAY_1;
LeafBin b5680_pass_SCNY   5680    : "b5680_pass_SCNY",   b1_PASS_CMTTRAY_1;
LeafBin b8250_fail_SCN_GT_GXX_GT_ALL_VMIN_K_SGTF5_X_VCCGT_F5_1900_GT    8250    : "b8250_fail_SCN_GT_GXX_GT_ALL_VMIN_K_SGTF5_X_VCCGT_F5_1900_GT",    b1_PASS_CMTTRAY_1;
        }
        }
'''
            self.assertTextEqual(File('a.bdef').read(), expect)    # first run

            print("Rerunning...")
            obj._bin_hack_file('a.bdef')
            self.assertTextEqual(File('a.bdef').read(), expect)    # second run - should be no change

    def test_binhack_octissue(self):
        with TempDir(name=True, chdir=True) as tdir:
            text = '''
            BinDefs
            {
        BinGroup SoftBins
        {
            LeafBin b11019120_fail_ARR_ATOM_CXX_LSA_ATOM_VMIN_K_LTTC_X_VCCIA_F1_0400_RF  11019120  : "b11019120_fail_ARR_ATOM_CXX_LSA_ATOM_VMIN_K_LTTC_X_VCCIA_F1_0400_RF",  b1_PASS_CMTTRAY_1;
            LeafBin b11029120_fail_ARR_ATOM_CXX_LSA_ATOM_VMIN_K_LTTC_X_VCCIA_F1_0400_RF  11029120  : "b11029120_fail_ARR_ATOM_CXX_LSA_ATOM_VMIN_K_LTTC_X_VCCIA_F1_0400_RF",  b1_PASS_CMTTRAY_1;
            LeafBin b11039120_fail_ARR_ATOM_CXX_LSA_ATOM_VMIN_K_LTTC_X_VCCIA_F1_0400_RF  11039120  : "b11039120_fail_ARR_ATOM_CXX_LSA_ATOM_VMIN_K_LTTC_X_VCCIA_F1_0400_RF",  b1_PASS_CMTTRAY_1;
            LeafBin b11049120_fail_ARR_ATOM_CXX_LSA_ATOM_VMIN_K_LTTC_X_VCCIA_F1_0400_RF  11049120  : "b11049120_fail_ARR_ATOM_CXX_LSA_ATOM_VMIN_K_LTTC_X_VCCIA_F1_0400_RF",  b1_PASS_CMTTRAY_1;
            LeafBin b11059120_fail_ARR_ATOM_CXX_LSA_ATOM_VMIN_K_LTTC_X_VCCIA_F1_0400_RF  11059120  : "b11059120_fail_ARR_ATOM_CXX_LSA_ATOM_VMIN_K_LTTC_X_VCCIA_F1_0400_RF",  b1_PASS_CMTTRAY_1;
            LeafBin b11069120_fail_ARR_ATOM_CXX_LSA_ATOM_VMIN_K_LTTC_X_VCCIA_F1_0400_RF  11069120  : "b11069120_fail_ARR_ATOM_CXX_LSA_ATOM_VMIN_K_LTTC_X_VCCIA_F1_0400_RF",  b1_PASS_CMTTRAY_1;
            LeafBin b90919120_fail_ARR_ATOM_CXX_LSA_ATOM_VMIN_K_LTTC_X_VCCIA_F1_0400_RF  90919120  : "b90919120_fail_ARR_ATOM_CXX_LSA_ATOM_VMIN_K_LTTC_X_VCCIA_F1_0400_RF",  b91_FAIL_WRONG_PRODUCT_OR_NTSC_CONFIG;
        }
        }
'''
            File('a.bdef').touch(text)
            obj = BinHack()
            obj._bin_hack_file('a.bdef')
            expect = '''
            BinDefs
            {
        BinGroup SoftBins
        {
            LeafBin b11019120_fail_ARR_ATOM_CXX_LSA_ATOM_VMIN_K_LTTC_X_VCCIA_F1_0400_RF  11019120  : "b11019120_fail_ARR_ATOM_CXX_LSA_ATOM_VMIN_K_LTTC_X_VCCIA_F1_0400_RF",  b1_PASS_CMTTRAY_1;
            LeafBin b11029120_fail_ARR_ATOM_CXX_LSA_ATOM_VMIN_K_LTTC_X_VCCIA_F1_0400_RF  11029120  : "b11029120_fail_ARR_ATOM_CXX_LSA_ATOM_VMIN_K_LTTC_X_VCCIA_F1_0400_RF",  b1_PASS_CMTTRAY_1;
            LeafBin b11039120_fail_ARR_ATOM_CXX_LSA_ATOM_VMIN_K_LTTC_X_VCCIA_F1_0400_RF  11039120  : "b11039120_fail_ARR_ATOM_CXX_LSA_ATOM_VMIN_K_LTTC_X_VCCIA_F1_0400_RF",  b1_PASS_CMTTRAY_1;
            LeafBin b11049120_fail_ARR_ATOM_CXX_LSA_ATOM_VMIN_K_LTTC_X_VCCIA_F1_0400_RF  11049120  : "b11049120_fail_ARR_ATOM_CXX_LSA_ATOM_VMIN_K_LTTC_X_VCCIA_F1_0400_RF",  b1_PASS_CMTTRAY_1;
            LeafBin b11059120_fail_ARR_ATOM_CXX_LSA_ATOM_VMIN_K_LTTC_X_VCCIA_F1_0400_RF  11059120  : "b11059120_fail_ARR_ATOM_CXX_LSA_ATOM_VMIN_K_LTTC_X_VCCIA_F1_0400_RF",  b1_PASS_CMTTRAY_1;
            LeafBin b11069120_fail_ARR_ATOM_CXX_LSA_ATOM_VMIN_K_LTTC_X_VCCIA_F1_0400_RF  11069120  : "b11069120_fail_ARR_ATOM_CXX_LSA_ATOM_VMIN_K_LTTC_X_VCCIA_F1_0400_RF",  b1_PASS_CMTTRAY_1;
            LeafBin b90919120_fail_ARR_ATOM_CXX_LSA_ATOM_VMIN_K_LTTC_X_VCCIA_F1_0400_RF  90919120  : "b90919120_fail_ARR_ATOM_CXX_LSA_ATOM_VMIN_K_LTTC_X_VCCIA_F1_0400_RF",  b91_FAIL_WRONG_PRODUCT_OR_NTSC_CONFIG;
            LeafBin b0191_fail_ARR_ATOM_CXX_LSA_ATOM_VMIN_K_LTTC_X_VCCIA_F1_0400_RF_SHARED_BIN  0191  : "b0191_fail_ARR_ATOM_CXX_LSA_ATOM_VMIN_K_LTTC_X_VCCIA_F1_0400_RF_SHARED_BIN",  b1_PASS_CMTTRAY_1;
            LeafBin b9120_fail_ARR_ATOM_CXX_LSA_ATOM_VMIN_K_LTTC_X_VCCIA_F1_0400_RF_SHARED_BIN  9120  : "b9120_fail_ARR_ATOM_CXX_LSA_ATOM_VMIN_K_LTTC_X_VCCIA_F1_0400_RF_SHARED_BIN",  b91_FAIL_WRONG_PRODUCT_OR_NTSC_CONFIG;
        }
        }
'''
            self.assertTextEqual(File('a.bdef').read(), expect)    # first run

    def test_binhack_mtpl(self):
        with TempDir(name=True, chdir=True) as tdir:
            txt1 = '''
        DUTFlowItem SHOPS_FUNC_P SHOPS_FUNC_P
        {
                Result -1
                {
                        Property PassFail = "Fail";
                        SetBin SoftBins.b90999901_fail_FAIL_DPS_ALARM;
                        Return -1;
                }
        }
            '''
            File('Modules/TPI/a.mtpl').touch(txt1, mkdir=True)
            txt2 = '''
        DUTFlowItem SHOPS_FUNC_P SHOPS_FUNC_P
        {
                Result -1
                {
                        Property PassFail = "Fail";
                        SetBin SoftBins.b90999901_fail_FAIL_DPS_ALARM;
                        SetBin SoftBins.b101_pass_TPI_BASE;
                        Return -1;
                }
        }
            '''
            File('Modules/TPI/b.mtpl').touch(txt2)

            obj = BinHack()
            obj.mtpl()
            self.assertEqual(File('Modules/TPI/a.mtpl').read(), txt1)     # unchanged
            expect = '''
        DUTFlowItem SHOPS_FUNC_P SHOPS_FUNC_P
        {
                Result -1
                {
                        Property PassFail = "Fail";
                        SetBin SoftBins.b90999901_fail_FAIL_DPS_ALARM;
                        SetBin SoftBins.b10010000_pass_pure;
                        Return -1;
                }
        }
            '''
            self.assertTextEqual(File('Modules/TPI/b.mtpl').read(), expect)

    def test_cl2rc(self):
        with TempDir(name=True, chdir=True) as tdir:
            f1 = 'Modules/TPI_DFF_XXX/InputFiles/MTL_ALL CLASS_P68G2_CLASS.xml'  # with space in the name
            f1n = 'Modules/TPI_DFF_XXX/InputFiles/MTL_ALL_CLASS_P68G2_CLASS.xml'  # replaced space, for checking later
            f2 = 'Modules/TPI_DFF_XXX/InputFiles/MTL_ALL_CLASS_P28G2_CLASS.xml'  # no space in the name
            f3 = 'Modules/TPI_DFF_XXX/InputFiles/ARL_ALL_CLASS_P28G2_CLASS.xml'  # no space in the name
            f4 = 'Modules/TPI_DFF_XXX/InputFiles/somedummy.txt'
            nf1 = 'Modules/TPI_DFF_XXX/InputFiles/MTL_ALL_CLASS_P68G2_RAWCLASS.xml'
            nf2 = 'Modules/TPI_DFF_XXX/InputFiles/MTL_ALL_CLASS_P28G2_RAWCLASS.xml'
            nf3 = 'Modules/TPI_DFF_XXX/InputFiles/ARL_ALL_CLASS_P28G2_RAWCLASS.xml'

            dffdata = """            <Token>
                <dff_token_id>1</dff_token_id>
                <name>QDFS</name>
                <first_socket_upload>PBIC_DAB</first_socket_upload>
                <upload_process_step>CLASSHOT</upload_process_step>
            </Token>
            <Token>
                <dff_token_id>2</dff_token_id>
                <name>PRIO</name>
                <first_socket_upload>RC_S1</first_socket_upload>
                <upload_process_step>CLASSHOT</upload_process_step>
            </Token>
            <Token>
                <dff_token_id>3</dff_token_id>
                <name>OLBCC2</name>
                <first_socket_upload>PBIC_DAB</first_socket_upload>
                <upload_process_step>CLASSCOLD</upload_process_step>
            </Token>
            <Token>
                <dff_token_id>4</dff_token_id>
                <name>OLBCC</name>
                <first_socket_upload>PBIC_DAB</first_socket_upload>
                <upload_process_step>CSM</upload_process_step>
            </Token>"""
            File(f1).touch(dffdata, mkdir=True, newfile=True)
            File(f2).touch(dffdata, mkdir=True, newfile=True)
            File(f3).touch(dffdata, mkdir=True, newfile=True)
            File(f4).touch(dffdata, mkdir=True, newfile=True)

            obj = TpPostProc()
            obj.cl2rc()

            # check for expected rawclass file data
            expect_rc = """            <Token>
                <dff_token_id>1</dff_token_id>
                <name>QDFS</name>
                <first_socket_upload>RC_S1</first_socket_upload>
                <upload_process_step>CLASSHOT</upload_process_step>
            </Token>
            <Token>
                <dff_token_id>2</dff_token_id>
                <name>PRIO</name>
                <first_socket_upload>RC_S1</first_socket_upload>
                <upload_process_step>CLASSHOT</upload_process_step>
            </Token>
            <Token>
                <dff_token_id>3</dff_token_id>
                <name>OLBCC</name>
                <first_socket_upload>RC_S1</first_socket_upload>
                <upload_process_step>CLASSCOLD</upload_process_step>
            </Token>
            <Token>
                <dff_token_id>4</dff_token_id>
                <name>OLBCC</name>
                <first_socket_upload>RC_S1</first_socket_upload>
                <upload_process_step>CSM</upload_process_step>
            </Token>"""

            self.assertTextEqual(File(nf1).read(), expect_rc)
            self.assertTextEqual(File(nf2).read(), expect_rc)
            self.assertTextEqual(File(nf3).read(), expect_rc)

            # check for expected class file data
            expect_cl = """            <Token>
                <dff_token_id>1</dff_token_id>
                <name>QDFS</name>
                <first_socket_upload>PBIC_DAB</first_socket_upload>
                <upload_process_step>CLASSHOT</upload_process_step>
            </Token>
            <Token>
                <dff_token_id>2</dff_token_id>
                <name>PRIO</name>
                <first_socket_upload>RC_S1</first_socket_upload>
                <upload_process_step>CLASSHOT</upload_process_step>
            </Token>
            <Token>
                <dff_token_id>3</dff_token_id>
                <name>OLBCC</name>
                <first_socket_upload>PBIC_DAB</first_socket_upload>
                <upload_process_step>CLASSCOLD</upload_process_step>
            </Token>
            <Token>
                <dff_token_id>4</dff_token_id>
                <name>OLBCC</name>
                <first_socket_upload>PBIC_DAB</first_socket_upload>
                <upload_process_step>CSM</upload_process_step>
            </Token>"""

            self.assertTextEqual(File(f1n).read(), expect_cl)  # expected change is now in the renamed file f1n
            self.assertTextEqual(File(f2).read(), expect_cl)
            self.assertTextEqual(File(f3).read(), expect_cl)


class TestMultiZonePin(TestCase):

    def test_basic(self):
        # case #1 - Main .pin file
        with TempDir(name=True, chdir=True) as tdir:
            text = """
Version 1.0;

PinDescription
{
        Resource EnabledClock
        {
                GPPC_A_11_PMC_I2C_SDA_I2S3_SCLK__EC;
                GPPC_F_00_CNV_BRI_DT_UART0_RTSB__EC;
        }
        DomainDefinitions
        {
                Domain ALL
                {
                        all_dmn_scoped
                }

                Domain CPU_PWR
                {
                        all_cpu_pwr_hc,
                        all_cpu_pwr_tdyn,
                        all_cpu_pwr_uei
                }
                Domain DDR
                {
                        all_ddr_scoped
                }
                Domain PCH_PWR
                {
                        all_pch_pwr_hc,
                        all_pch_pwr_tdyn,
                        all_pch_pwr_uei
                }
        }
}
"""
            File('PinDefinitions.pin').touch(text)
            File('PinDefinitions_IP_PCH.pin').touch('Version 1.0;\n')   # no change
            MultiZonePin().main()
            expect = """
Version 1.0;

PinDescription
{
        Resource EnabledClock
        {
                GPPC_A_11_PMC_I2C_SDA_I2S3_SCLK__EC;
                GPPC_F_00_CNV_BRI_DT_UART0_RTSB__EC;
        }
        DomainDefinitions
        {
                Domain ALL
                {
                        all_dmn_scoped
                }

                Domain DDR
                {
                        all_ddr_scoped
                }
        }
        ThermalDomainDefinitions
        {
                ThermalDomain CPU_PWR
                {
                        all_cpu_pwr_hc,
                        all_cpu_pwr_tdyn,
                        all_cpu_pwr_uei
                }
                ThermalDomain PCH_PWR
                {
                        all_pch_pwr_hc,
                        all_pch_pwr_tdyn,
                        all_pch_pwr_uei
                }
        }
}
"""
            self.assertTextEqual(File('PinDefinitions.pin').read(), expect)
            self.assertTextEqual(File('PinDefinitions_IP_PCH.pin').read(), 'Version 1.0;\n')

        # case#2 - IP_CPU and IP_PCH
        with TempDir(name=True, chdir=True) as tdir:
            File('PinDefinitions_IP_PCH.pin').touch(text)
            File('PinDefinitions_IP_CPU.pin').touch(text)
            MultiZonePin().main()
            expect = """
Version 1.0;

PinDescription
{
        Resource EnabledClock
        {
                GPPC_A_11_PMC_I2C_SDA_I2S3_SCLK__EC;
                GPPC_F_00_CNV_BRI_DT_UART0_RTSB__EC;
        }
        DomainDefinitions
        {
                Domain ALL
                {
                        all_dmn_scoped
                }

                Domain DDR
                {
                        all_ddr_scoped
                }
        }
}
"""
            self.assertTextEqual(File('PinDefinitions_IP_CPU.pin').read(), expect)
            expect = """
Version 1.0;

PinDescription
{
        Resource EnabledClock
        {
                GPPC_A_11_PMC_I2C_SDA_I2S3_SCLK__EC;
                GPPC_F_00_CNV_BRI_DT_UART0_RTSB__EC;
        }
        DomainDefinitions
        {
                Domain ALL
                {
                        all_dmn_scoped
                }

                Domain DDR
                {
                        all_ddr_scoped
                }
        }
}
"""
            self.assertTextEqual(File('PinDefinitions_IP_PCH.pin').read(), expect)


class TestBinHack2(TestCase):

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_basic(self):
        tp = TestProgram('POR_TP/TGLH81/EnvironmentFile.env')
        BinHack2(tp).main()

        # no change
        self.assertGoldEqual('Shared/BaseInputs/BinDefinitions.bdefs',
                             f'{UT_DIR_REPO}/Simple6/Shared/BaseInputs/BinDefinitions.bdefs')

        # with change
        File(f'{UT_DIR_REPO}/misc_files/BinDefinitions_tos4.bdefs').copy('Shared/BaseInputs/BinDefinitions.bdefs')
        BinHack2(tp).main()
        self.assertGoldEqual('Shared/BaseInputs/BinDefinitions.bdefs',
                             f'{UT_DIR_REPO}/misc_files/BinDefinitions_tos4.bdefs.gold')


class TestEnvHack(TestCase):

    def test_tpl_input(self):
        # basic test with one variable already existing
        with TempDir(name=True, chdir=True) as tdir:
            text = r"""
OASIS_TPL_DIR = "~HDMT_TPL_DIR";

PLIST_PROD_FILE_NAME = "~HDMT_TPL_DIR\PLIST_ALL.xml";

FUSE_ROOT_DIR_C28 = "I:\fuse\release\MTL_CPU_28\A3_22WW08\0";

FUSE_ROOT_DIR_GLG = "I:\fuse\release\MTL_PIXE_P\A0_22WW15\1";

FUSE_ROOT_DIR_IOEP = "I:\fuse\release\MTL_IOE_P\A0_22WW16\1";

FUSE_ROOT_DIR_SXM = "I:\fuse\release\MTL_SOC_M\A0_22WW16\1";

FUSE_ROOT_DIR_C68 = "I:\fuse\release\MTL_CPU_68\P0_22WW16\1";

PLIST_BURST_OPTION_PXR_CHECK_DISABLE = "TRUE";

HDMT_TPL_INPUT_FILES = "$EVERGREEN_VERSION_DIR;" +
                                "$EVERGREEN_PH_DIR;" +
                                "$EVERGREEN_VERSION_DIR\tpe\xsd;" +
                                "$FUSE_ROOT_DIR_C68;" +
                                "$PRIME_VERSION_DIR\resources\schemas;" +
                                "$MSTPI_PATMODIFY_PATH";

EVERGREEN_SCHEMA_DIR = "~HDMT_TPL_DIR\Supersedes\code;" +
                                "$HDMT_TPL_INPUT_FILES";
"""
            File('a.env').touch(text)
            EnvHack().tpl_input_file()
            expect = r"""
OASIS_TPL_DIR = "~HDMT_TPL_DIR";

PLIST_PROD_FILE_NAME = "~HDMT_TPL_DIR\PLIST_ALL.xml";

FUSE_ROOT_DIR_C28 = "I:\fuse\release\MTL_CPU_28\A3_22WW08\0";

FUSE_ROOT_DIR_GLG = "I:\fuse\release\MTL_PIXE_P\A0_22WW15\1";

FUSE_ROOT_DIR_IOEP = "I:\fuse\release\MTL_IOE_P\A0_22WW16\1";

FUSE_ROOT_DIR_SXM = "I:\fuse\release\MTL_SOC_M\A0_22WW16\1";

FUSE_ROOT_DIR_C68 = "I:\fuse\release\MTL_CPU_68\P0_22WW16\1";

PLIST_BURST_OPTION_PXR_CHECK_DISABLE = "TRUE";

HDMT_TPL_INPUT_FILES = "$EVERGREEN_VERSION_DIR;" +
                                "$EVERGREEN_PH_DIR;" +
                                "$EVERGREEN_VERSION_DIR\tpe\xsd;" +
                                "$FUSE_ROOT_DIR_C68;" +
                                "$PRIME_VERSION_DIR\resources\schemas;" +
                                "$FUSE_ROOT_DIR_C28;" +
                                "$FUSE_ROOT_DIR_GLG;" +
                                "$FUSE_ROOT_DIR_IOEP;" +
                                "$FUSE_ROOT_DIR_SXM;" +
                                "$MSTPI_PATMODIFY_PATH";

EVERGREEN_SCHEMA_DIR = "~HDMT_TPL_DIR\Supersedes\code;" +
                                "$HDMT_TPL_INPUT_FILES";
"""
            self.assertTextEqual(File('a.env').read(), expect)

    def test_two_tpl_input(self):
        # duplicate at end
        with TempDir(name=True, chdir=True) as tdir:
            text = r"""
OASIS_TPL_DIR = "~HDMT_TPL_DIR";

PLIST_PROD_FILE_NAME = "~HDMT_TPL_DIR\PLIST_ALL.xml";

FUSE_ROOT_DIR_C28 = "I:\fuse\release\MTL_CPU_28\A3_22WW08\0";

FUSE_ROOT_DIR_GLG = "I:\fuse\release\MTL_PIXE_P\A0_22WW15\1";

FUSE_ROOT_DIR_IOEP = "I:\fuse\release\MTL_IOE_P\A0_22WW16\1";

FUSE_ROOT_DIR_SXM = "I:\fuse\release\MTL_SOC_M\A0_22WW16\1";

FUSE_ROOT_DIR_C68 = "I:\fuse\release\MTL_CPU_68\P0_22WW16\1";

PLIST_BURST_OPTION_PXR_CHECK_DISABLE = "TRUE";

HDMT_TPL_INPUT_FILES = "$EVERGREEN_VERSION_DIR;" +
                                "$EVERGREEN_PH_DIR;" +
                                # "$FUSE_ROOT_DIR_GLG;" +
                                "$EVERGREEN_VERSION_DIR\tpe\xsd;" +
                                "$FUSE_ROOT_DIR_C68";

EVERGREEN_SCHEMA_DIR = "~HDMT_TPL_DIR\Supersedes\code;" +
                                "$HDMT_TPL_INPUT_FILES";
"""
            File('a.env').touch(text)
            EnvHack().tpl_input_file()
            expect = r"""
OASIS_TPL_DIR = "~HDMT_TPL_DIR";

PLIST_PROD_FILE_NAME = "~HDMT_TPL_DIR\PLIST_ALL.xml";

FUSE_ROOT_DIR_C28 = "I:\fuse\release\MTL_CPU_28\A3_22WW08\0";

FUSE_ROOT_DIR_GLG = "I:\fuse\release\MTL_PIXE_P\A0_22WW15\1";

FUSE_ROOT_DIR_IOEP = "I:\fuse\release\MTL_IOE_P\A0_22WW16\1";

FUSE_ROOT_DIR_SXM = "I:\fuse\release\MTL_SOC_M\A0_22WW16\1";

FUSE_ROOT_DIR_C68 = "I:\fuse\release\MTL_CPU_68\P0_22WW16\1";

PLIST_BURST_OPTION_PXR_CHECK_DISABLE = "TRUE";

HDMT_TPL_INPUT_FILES = "$EVERGREEN_VERSION_DIR;" +
                                "$EVERGREEN_PH_DIR;" +
                                # "$FUSE_ROOT_DIR_GLG;" +
                                "$EVERGREEN_VERSION_DIR\tpe\xsd;" +
                                "$FUSE_ROOT_DIR_C28;" +
                                "$FUSE_ROOT_DIR_GLG;" +
                                "$FUSE_ROOT_DIR_IOEP;" +
                                "$FUSE_ROOT_DIR_SXM;" +
                                "$FUSE_ROOT_DIR_C68";

EVERGREEN_SCHEMA_DIR = "~HDMT_TPL_DIR\Supersedes\code;" +
                                "$HDMT_TPL_INPUT_FILES";
"""
            self.assertTextEqual(File('a.env').read(), expect)

            # re-run
            EnvHack().tpl_input_file()
            self.assertTextEqual(File('a.env').read(), expect)

    def test_prime_schema_path(self):
        with TempDir(name=True, chdir=True) as tdir:
            text = r"""
OASIS_TPL_DIR = "~HDMT_TPL_DIR";

PRIME_SCHEMA_PATH = "$HDMT_TPL_INPUT_FILES";

PLIST_BURST_OPTION_PXR_CHECK_DISABLE = "TRUE";
"""
            File('a.env').touch(text)
            EnvHack().prime_schema_path()
            expect = r"""
OASIS_TPL_DIR = "~HDMT_TPL_DIR";

PRIME_SCHEMA_PATH = "~HDMT_TPL_DIR\Supersedes\code;" +
                    "$PRIME_USER_CODE_DLL_DIR;" +
                    "$HDMT_TPL_INPUT_FILES";

PLIST_BURST_OPTION_PXR_CHECK_DISABLE = "TRUE";
"""
            self.assertTextEqual(File('a.env').read(), expect)

            # re-run
            EnvHack().prime_schema_path()
            self.assertTextEqual(File('a.env').read(), expect)

            # no change
            text = r"""
OASIS_TPL_DIR = "~HDMT_TPL_DIR";

PRIME_SCHEMA_PATH = "$HDMT_TPL_INPUT_FILES;" +
                    "SOME";

PLIST_BURST_OPTION_PXR_CHECK_DISABLE = "TRUE";
"""
            File('b.env').touch(text)
            EnvHack().prime_schema_path()
            self.assertTextEqual(File('b.env').read(), text)   # no change


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
