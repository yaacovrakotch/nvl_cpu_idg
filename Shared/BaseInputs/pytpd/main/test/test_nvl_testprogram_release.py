#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for checkers
"""
from setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.files import TempDir, File, check_and_del
from gadget.gizmo import MockVar
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock
from gadget.disk import Chdir
from main.testprogram_release import *
import main.nvl_testprogram_release as TPrelease
from os.path import join, dirname, abspath
import sys
import os
from unittest.mock import patch


class FakeDate:

    @classmethod
    def today(cls):
        return '2024-01-09'


class TestBasic(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_release_all(self):
        expected_result = r"""<html style="font-family: Calibri; font-size: 12px;">
<head>
<title>NVLXXXXAXH01A0BSXXX Full Daily Build Report</title>
</head><body>
<h1><table border='1' cellspacing='0' style='font-family: Calibri;'>
<tr style='padding-left: 15px; text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='4' style ='font-size:15px;'><pre>NVLXXXXAXH01A0BSXXX Full Daily Build Report
Class_NVL_S28C A0 01A0B Test Program
Built to JF
Built Date 2024-01-09</pre></td></tr>  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Test Program Objective/Special Notes</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>TP/75 ARL-U28G1</td>
    </tr>
  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Issues</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>None</td>
    </tr>
<tr style='text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='4' style ='font-size:15px;'>Test Program Summary Information</td></tr>
  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Test Program Name</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>NVLXXXXAXH01A0BSXXX</td>
    </tr>
  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Test Program Short Name [Nick Name]</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>01A0B Full</td>
    </tr>
  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Products/Subfamily</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>NVL Class_NVL_S28C A0</td>
    </tr>
  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Test Program Integrator</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>Ferlito Carpio/Tai Pham/Danny Phan</td>
    </tr>
  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Test Program Product Owner</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>Pearson, Hai</td>
    </tr>
  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Fuse Path</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>I:/fuse/release/NVL/NVL_S_28C_Int/NVL_S_28C_Int_25ww20<br>I:/fuse/release/NVL/CPU_Int/CPU_A0_25WW17P0_preSi<br>I:/fuse/release/NVL/PIXE3S_32EU/nvlgcd_a0_25ww03a_presi_25ww17<br>I:/fuse/release/NVL/PIXE3H_64EU/nvlgcd_a0_24ww46e_presi_25WW12<br>I:/fuse/release/NVL/HUB_NVL/HUB_A0_25ww17_preSi<br>I:/fuse/release/ARL_FLAME/IOEP_ARL/ARLS68_IOEP0_B0_24ww01_PO</td>
    </tr>
  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Handler Rev</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>N/A</td>
    </tr>
  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>TOS Profile</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>hdmtOS_4.0.2.1</td>
    </tr>
  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>PRIME_DLL_PATH</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>I:/tpapps/userlibs/nvl/prime_v13.2.0-ddg251600<br>I:/tpapps/userlibs/nvl/modules/prime_v13.2.0/binning/UPS2519.0_UC1.0</td>
    </tr>
  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Skipped Modules</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>None</td>
    </tr>
  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Supersedes</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>BaseInputs/GCD/GCD_Torch/Supersedes/code/CsioCmemTC.dll<br>BaseInputs/HUB/HUB_Torch/Supersedes/code/CsioCmemTC.dll<br>BaseInputs/CPU/CPU_Torch/Supersedes/code/CsioCmemTC.dll<br>BaseInputs/CPU/CPU_Torch/Supersedes/code/HPTPImpedance.dll<br>BaseInputs/CPU/CPU_Torch/Supersedes/code/HPTPSetupScan.dll<br>BaseInputs/CPU/CPU_Torch/Supersedes/code/HPTPTimingCalibration.dll<br>BaseInputs/CPU/CPU_Torch/Supersedes/code/HPTP_EyeDiagramTestMethod.dll</td>
    </tr>
<tr style='text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='4' style ='font-size:15px;'>Test Program Files for Loadings</td></tr>
  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>TP Base Dir</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>\intel\tpvalidation\engtools\tptools\mtl\unittests\nvl_testprogram_release\NVLXXXXAXH01A0BSXXX</td>
    </tr>
  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Test Plan</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>BaseTestPlan.tpl</td>
    </tr>
  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Sub-Test Plan</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>POR_TP\Class_NVL_S28C\SubTestPlan.stpl</td>
    </tr>
  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Plist Reference</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>POR_TP\Class_NVL_S28C\PLIST_ALL_CLASS_NVL_S28C.plist.xml</td>
    </tr>
  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Socket File</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>Shared\BaseInputs\Common\Common_Class_NVL_S28C\HVM.soc</td>
    </tr>
  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Environment File</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>POR_TP\Class_NVL_S28C\EnvironmentFile.env</td>
    </tr>
  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>BOM Definition</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>564AAA*VA, 564AAA*V_A</td>
    </tr>
  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Stepping</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>A0</td>
    </tr>
  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>Classification</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>Engineering</td>
    </tr>
  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td colspan ='2' style='padding-right:15px; font-size:12px;'>BOM Groups</td>
        <td colspan ='2' style='padding-right:5px; font-size:12px;'>Class_NVL_S28C</td>
    </tr>
<tr style='text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='4' style ='font-size:15px;'>Test Program Change List</td></tr>
  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
            <td style='padding-right:15px; font-weight: bold; font-size:12px;'>PR Number</td>
            <td style='padding-right:15px; font-weight: bold; font-size:12px;'>Title</td>
            <td style='padding-right:15px; font-weight: bold; font-size:12px;'>Submitted By</td>
            <td style='padding-right:15px; font-weight: bold; font-size:12px;'>URL</td>
        </tr>
<tr style='text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='4' style ='font-size:15px;'>REPO: nvl.common</td></tr>
  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
                <td style='padding-right:15px; font-size:12px;'>232</td>
                <td style='padding-right:15px; font-size:12px;'>updating programflow for 52 to match 28</td>
                <td style='padding-right:15px; font-size:12px;'>shiv-gourshetty-intel</td>
                <td style='padding-right:15px; font-size:12px;'>https://github.com/intel-restricted/nvl.common/pull/232</td>
                </tr>
  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
                <td style='padding-right:15px; font-size:12px;'>231</td>
                <td style='padding-right:15px; font-size:12px;'>Pindef update PLT Rev4.1</td>
                <td style='padding-right:15px; font-size:12px;'>jonathan-urtecho-intel</td>
                <td style='padding-right:15px; font-size:12px;'>https://github.com/intel-restricted/nvl.common/pull/231</td>
                </tr>
<tr style='text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='4' style ='font-size:15px;'>REPO: nvl.cpu</td></tr>
  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
                <td style='padding-right:15px; font-size:12px;'>377</td>
                <td style='padding-right:15px; font-size:12px;'>Added Missing Modules for C die 52C BOM</td>
                <td style='padding-right:15px; font-size:12px;'>chen3-chen-intel</td>
                <td style='padding-right:15px; font-size:12px;'>https://github.com/intel-restricted/nvl.cpu/pull/377</td>
                </tr>
  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
                <td style='padding-right:15px; font-size:12px;'>376</td>
                <td style='padding-right:15px; font-size:12px;'>Sync 28C vs 52C program flow.</td>
                <td style='padding-right:15px; font-size:12px;'>chen3-chen-intel</td>
                <td style='padding-right:15px; font-size:12px;'>https://github.com/intel-restricted/nvl.cpu/pull/376</td>
                </tr>
<tr style='text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='4' style ='font-size:15px;'>REPO: nvl.gcd</td></tr>
  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
                <td style='padding-right:15px; font-size:12px;'>219</td>
                <td style='padding-right:15px; font-size:12px;'>Update the programflow pymtpl to point to 52C.</td>
                <td style='padding-right:15px; font-size:12px;'>chen3-chen-intel</td>
                <td style='padding-right:15px; font-size:12px;'>https://github.com/intel-restricted/nvl.gcd/pull/219</td>
                </tr>
  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
                <td style='padding-right:15px; font-size:12px;'>218</td>
                <td style='padding-right:15px; font-size:12px;'>Timings fix and common repoint</td>
                <td style='padding-right:15px; font-size:12px;'>jonathan-urtecho-intel</td>
                <td style='padding-right:15px; font-size:12px;'>https://github.com/intel-restricted/nvl.gcd/pull/218</td>
                </tr>
<tr style='text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='4' style ='font-size:15px;'>REPO: nvl.pcd</td></tr>
  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
                <td style='padding-right:15px; font-size:12px;'>222</td>
                <td style='padding-right:15px; font-size:12px;'>Sync 28C and 52C programflow.</td>
                <td style='padding-right:15px; font-size:12px;'>chen3-chen-intel</td>
                <td style='padding-right:15px; font-size:12px;'>https://github.com/intel-restricted/nvl.pcd/pull/222</td>
                </tr>
  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
                <td style='padding-right:15px; font-size:12px;'>221</td>
                <td style='padding-right:15px; font-size:12px;'>Repointing common and fixing 1GTs timings and adding PCD_PROBE_TRIG1 â€¦</td>
                <td style='padding-right:15px; font-size:12px;'>jonathan-urtecho-intel</td>
                <td style='padding-right:15px; font-size:12px;'>https://github.com/intel-restricted/nvl.pcd/pull/221</td>
                </tr>
<tr style='text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='4' style ='font-size:15px;'>REPO: nvl.hub</td></tr>
  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
                <td style='padding-right:15px; font-size:12px;'>210</td>
                <td style='padding-right:15px; font-size:12px;'>Sync the 28C vs 52C flow.</td>
                <td style='padding-right:15px; font-size:12px;'>chen3-chen-intel</td>
                <td style='padding-right:15px; font-size:12px;'>https://github.com/intel-restricted/nvl.hub/pull/210</td>
                </tr>
  <tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
                <td style='padding-right:15px; font-size:12px;'>208</td>
                <td style='padding-right:15px; font-size:12px;'>Timings fix and common repoint</td>
                <td style='padding-right:15px; font-size:12px;'>jonathan-urtecho-intel</td>
                <td style='padding-right:15px; font-size:12px;'>https://github.com/intel-restricted/nvl.hub/pull/208</td>
                </tr>
</table>
</h1>
            <h2 style = 'font-size: 12px;'>For more details, please contact: mpe_ddg_pde_tp_team@intel.com</h2>
</body></html>"""
        with MockVar(sys, 'argv', ['testprogram_release.py', '-path', f'{UT_DIR}/nvl_testprogram_release/testprogram_release_notes.txt']):
            Input_file = f'{UT_DIR}/nvl_testprogram_release/testprogram_release_notes.txt'
            golden_file = f'{UT_DIR}/nvl_testprogram_release/01A0B_gold.html'
            actual_file = f'{UT_DIR}/nvl_testprogram_release/01A0B.html'
            pr_reports = f'{UT_DIR}/nvl_testprogram_release/PR_reports/01A0B.json'
            check_and_del(actual_file)
            with MockVar(TPrelease, 'get_report_file', Mock(return_value=actual_file)), \
                    MockVar(TPrelease, 'setting_Tags', Mock(return_value='TP_01A0B')), \
                    MockVar(TPrelease, 'get_PR_report_file', Mock(return_value=pr_reports)), \
                    MockVar(TPrelease, 'date', FakeDate):
                TPrelease.release_email(Input_file)
            with open(actual_file, 'r') as f:
                result = f.read()
            self.assertTextEqual(result, expected_result)

    def test_send_email_auto(self):
        classification = 'Engineering'
        issue = 'None'
        email_subject = 'NVLXXXXAXH01A0BSXXX Full Daily Build Report'
        email_body = 'This is the body of the email.'
        special_notes = 'TP/75 ARL-U28G1'
        table1 = r"""<table border='1' cellspacing='0' style='font-family: Calibri;'>
<tr style='padding-left: 15px; text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='4' style ='font-size:15px;'><pre>NVLXXXXAXH01A0BSXXX Full Daily Build Report
Class_NVL_S28C A0 01A0B Test Program
Built to JF
Built Date 2024-01-09</pre></td></tr></table>"""
        TP_release_note = 'This is the release note.'
        with MockVar(TPrelease, 'get_email_list', Mock(return_value=['abc@intel.com', 'bcd@intel.com'])), \
                MockVar(TPrelease, 'IS_WIN', True), \
                MockVar(os, 'environ', {'AUTO_RELEASE_NOTE': 'True', 'SUBMITTER_EMAIL': 'tai.pham@intel.com'}), \
                CaptureStdoutLog() as p:
            TPrelease.send_email(classification, issue, email_subject, email_body, special_notes, table1, TP_release_note)
        self.assertIn('NVLXXXXAXH01A0BSXXX Full Daily Build Report', p.getvalue())


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
