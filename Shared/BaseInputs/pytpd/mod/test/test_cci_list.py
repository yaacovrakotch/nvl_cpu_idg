#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Unit test for cci_list
"""
from setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE    # must be first import for unittests
from gadget.ut import TestCase, unittest
from gadget.gizmo import MockVar, with_
from gadget.helperclass import CaptureStdoutLog
from gadget.printmore import Dumper
from gadget.files import TempDir
from gadget.disk import Chdir
from mod.cci_list import *
from unittest.mock import Mock
import mod.cci_list as cci_list
from gadget.strmore import curtime
from os.path import basename
import os
import re


class TestCCI(TestCase):

    @with_(MockVar, TPBotFail, 'get_list', Mock(return_value=[]))
    def test_basic(self):
        cci = CCI('TP/38', 50)

        cmd_list = []

        def fake_outtxt(slf, *args):
            """fake run_outtxt"""
            cmd_list.append(' '.join(slf.cmd))
            raise Exception(f"Unknown cmd in fake_outtxt(): {slf.cmd}")

        def fake_run_outfile(slf, fname):
            """fake run_outfile"""
            cmd_list.append(' '.join(slf.cmd))
            if '--json' in ' '.join(slf.cmd):
                File(fname).touch(
                    File(f'{UT_DIR}/cci_pr/37a.json').read(), newfile=True)
                return 0
            if 'pr list' in ' '.join(slf.cmd):
                File(fname).touch(
                    '2582 blah DRAFT\n2122 blah OPEN\n', newfile=True)
                return 0
            if 'git tag' in ' '.join(slf.cmd):
                File(fname).touch('TPI/37C_FSM\n', newfile=True)
                return 0
            if 'git log' in ' '.join(slf.cmd):
                File(fname).touch('TPI/37C_FSM: Enabling FSM into 37D (#2814)\n', newfile=True)
                return 0
            raise Exception(f"Unknown cmd in fake_run_outfile(): {slf.cmd}")

        with CaptureStdoutLog() as p, \
                MockVar(CCI, 'get_curtime', Mock(return_value=1677888950.5311604)), \
                MockVar(SystemCall, 'run_outfile', fake_run_outfile), \
                MockVar(CCI, '_git_pull', Mock()), \
                MockVar(SystemCall, 'run_outtxt', fake_outtxt):
            cci.main()

        # monkey the expect
        result = p.getvalue()
        result = re.sub('<pre>.*TP/38 CCI Report.*?</pre>',
                        '<pre>TP/38</pre>', result)
        result = re.sub('<title>.*TP/38 CCI.*?</title>',
                        '<title>TP/38</title>', result)
        result = re.sub(r"from lno#\d+", 'from lno#1', result)
        result = re.sub(r"please contact: \S+", 'please contact: mpe_ddg_pde_10n_tp_team@intel.com</h2>', result)
        with TempDir(name=True) as tdir:
            File(f'{tdir}/a.txt').touch(result)
            self.assertGoldEqual(f'{tdir}/a.txt', f'{UT_DIR}/cci_pr/37c.gold12')

    @with_(MockVar, TPBotFail, 'get_list', Mock(return_value=[]))
    def test_basic2(self):
        # good template
        cci = CCI('TP/38', 50)

        cmd_list = []

        def fake_outtxt(slf, *args):
            """fake run_outtxt"""
            cmd_list.append(' '.join(slf.cmd))
            raise Exception(f"Unknown cmd in fake_outtxt(): {slf.cmd}")

        def fake_run_outfile(slf, fname):
            """fake run_outfile"""
            _cmd = ' '.join(slf.cmd)
            cmd_list.append(_cmd)
            if '--json' in ' '.join(slf.cmd):
                self.assertIn('milestone', _cmd)      # milestone=True
                File(fname).touch('''[{
      "author": {
         "login": "john-q-delos-reyes-intel"
      },
      "closed": true,
      "milestone": {"title": "msx"},
      "labels": [
         {
            "id": "LA_kwDOHYgjhc8AAAABNDIw7w",
            "name": "PASSED_Chk",
            "description": "",
            "color": "258824"
         }
      ],
      "mergedAt": "2023-03-03T23:01:21Z",
      "number": 2685,
      "title": "37 CCI - P28 main-line check",
      "updatedAt": "2023-03-01T04:25:27Z",
      "url": "https://github.com/intel-restricted/mtlp68/pull/2009"
   }
]
''', newfile=True)
                return 0
            if 'pr list' in ' '.join(slf.cmd):
                File(fname).touch(
                    '2582 blah DRAFT\n2122 blah OPEN\n', newfile=True)
                return 0
            if 'git tag' in ' '.join(slf.cmd):
                File(fname).touch('TPI/37C_FSM\n', newfile=True)
                return 0
            if 'git log' in ' '.join(slf.cmd):
                File(fname).touch('TPI/37C_FSM: Enabling FSM into 37D (#2814)\n', newfile=True)
                return 0
            raise Exception(f"Unknown cmd in fake_run_outfile(): {slf.cmd}")

        with CaptureStdoutLog() as p, \
                MockVar(CCI, 'get_curtime', Mock(return_value=1677888950.5311604)), \
                MockVar(SystemCall, 'run_outfile', fake_run_outfile), \
                MockVar(CCI, '_git_pull', Mock()), \
                MockVar(SystemCall, 'run_outtxt', fake_outtxt), \
                MockVar(cci, "OPT", {'milestone': True}):
            cci.main()

        # monkey the expect
        result = p.getvalue()
        result = re.sub('<pre>.*TP/38 CCI Report.*?</pre>',
                        '<pre>TP/38</pre>', result)
        result = re.sub('<title>.*TP/38 CCI.*?</title>',
                        '<title>TP/38</title>', result)
        result = re.sub(r"from lno#\d+", 'from lno#1', result)
        result = re.sub(r"please contact: \S+", 'please contact: mpe_ddg_pde_10n_tp_team@intel.com</h2>', result)
        expect = '''
<div id="status">
Getting all PR's mtlp68<br>
Getting tag list...<br>
Reading drafts<br>
Getting all open PRs<br>

</div>
<script>
    var myDiv = document.getElementById("status");
    myDiv.style.display = "none";
</script>


<html style="font-family: Calibri; font-size: 15px;">
<head>
<title>TP/38</title>
</head>
<body>
<h1><table border='1' cellspacing='0' style='font-family: Calibri;'>
<tr style='padding-left: 15px; text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='7' style ='font-size:15px;'><pre>TP/38</pre></td></tr><tr style='text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='7' style ='font-size:15px;'>Total Open PRs: 0 </td></tr>
<tr style='padding-left: 5px; font-weight: bold; text-align: left; background-color: #F0F8FF; color: #000000;'>

        <td>PR #</td>
        <td>Title</td>
        <td>Tags</td>
        <td><a href="https://wiki.ith.intel.com/x/zA_syQ" target="_blank">Atomic_rev</a></td>
        <td>Atomic_bom_impacted</td>
        <td>Submitted By</td>
        <td>Status</td>
        </tr>

<tr style='text-align: center; font-weight: bold; background-color: #F0F8FF; color: #0000FF;'><td colspan='7' style ='font-size:15px;'>Merged PRs</td></tr>
<tr style='padding-left: 5px; font-weight: bold; text-align: left; background-color: #F0F8FF; color: #000000;'>
        <td>PR #</td>
        <td>Title</td>
        <td>Tags</td>
        <td><a href="https://wiki.ith.intel.com/x/zA_syQ" target="_blank">Atomic_rev</a></td>
        <td>Atomic_bom_impacted</td>
        <td>Submitted By</td>
        <td>Merged At</td>
        </tr>
  <tr style='padding-left: 5px; text-align: left; background-color: #E6E6FF; color: #000000;'>
                <td>2685</td>
                <td><a href='https://github.com/intel-restricted/mtlp68/pull/2009'>37 CCI - P28 main-line check</a></td>
                <td> </td>
                <td></td>
                <td></td>
                <td>john-q-delos-reyes-i</td>
                <td>0.1 days ago: 2023-03-03 15:01:21 Manual</td>
            </tr>
</table>
</h1>
<h2 style = 'font-size: 15px;'>
To increase row count, add '&rows=100' in url. Default is 50.<br>
For more details, please contact: mpe_ddg_pde_10n_tp_team@intel.com</h2>
</body></html>

'''
        self.assertTextEqual(result, expect)

    def test_tpbot_fails(self):
        cci = CCI('TP/38', 50)
        cci.data = {11: {'url': 'http://11', 'title': 'title11'}}
        cci.URL = 'http:/ut'

        rec11 = {'prno': 11, 'logpath': '/blah', 'time': 1, 'filename': '11_blah.open.json', 'title': 't1', 'author': 'a1'}
        rec12 = {'prno': 12, 'logpath': '/blah2', 'time': 2, 'filename': '12_blah.open.json', 'title': 't2', 'author': 'a2'}
        with MockVar(TPBotFail, 'get_list', Mock(return_value=[rec11, rec12])), \
                MockVar(cci, 'get_curtime', Mock(return_value=1677888950)), \
                MockVar(time, 'time', Mock(return_value=1677888950)), \
                MockVar(cci, "OPT", {'milestone': True}):
            result = cci.tpbot_fails('stylerow\n', 'headerstyle\n')

        # monkey the expect
        expect = '''
stylerow
TPBot Fails: 2</td></tr>
headerstyle


        <td>PR #</td>
        <td>PR Title of TPBOT fail</td>
        <td>Dispo &darr;</td>
        <td>Dispo &darr;</td>
        <td>Dispo &darr;</td>
        <td>Submitted By</td>
        <td>Fail date</td>
        </tr>
<tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
                    <td>11</td>
                    <td><a href='http://11'>t1</a></td>
                    <td><a href='http:/ut?br=x&tpbotfail=11_blah.open.json&repo=None&dispo=MV'>MV Fail</a></td>
                    <td><a href='http:/ut?br=x&tpbotfail=11_blah.open.json&repo=None&dispo=TRUE'>TRUE Fail</a></td>
                    <td><a href='http:/ut?br=x&tpbotfail=11_blah.open.json&repo=None&dispo=SETUP'>SETUP Fail</a></td>
                    <td>a1</td>
                    <td><a href='http:/ut?br=x&viewlog2=.//blah'>19420.0 days ago, 1969-12-31 16:00:01</a></td>
                </tr>
<tr style='padding-left: 5px; text-align: left; background-color: #F0F8FF; color: #000000;'>
                    <td>12</td>
                    <td><a href='http://12'>t2</a></td>
                    <td><a href='http:/ut?br=x&tpbotfail=12_blah.open.json&repo=None&dispo=MV'>MV Fail</a></td>
                    <td><a href='http:/ut?br=x&tpbotfail=12_blah.open.json&repo=None&dispo=TRUE'>TRUE Fail</a></td>
                    <td><a href='http:/ut?br=x&tpbotfail=12_blah.open.json&repo=None&dispo=SETUP'>SETUP Fail</a></td>
                    <td>a2</td>
                    <td><a href='http:/ut?br=x&viewlog2=.//blah2'>19420.0 days ago, 1969-12-31 16:00:02</a></td>
                </tr>
'''
        self.assertTextEqual(result, expect)

    @with_(MockVar, TPBotFail, 'get_list', Mock(return_value=[]))
    def test_prcnt(self):
        cmd_list = []

        def fake_outtxt(slf, *args):
            """fake run_outtxt"""
            cmd_list.append(' '.join(slf.cmd))
            raise Exception(f"Unknown cmd in fake_outtxt(): {slf.cmd}")

        def fake_run_outfile(slf, fname):
            """fake run_outfile"""
            cmd_list.append(' '.join(slf.cmd))
            if '--json' in ' '.join(slf.cmd):
                File(fname).touch(
                    File(f'{UT_DIR}/cci_pr/37a.json').read(), newfile=True)
                return 0
            if 'pr list' in ' '.join(slf.cmd):
                File(fname).touch(
                    '2582 blah DRAFT\n2122 blah OPEN\n', newfile=True)
                return 0
            if 'pr view 2686' in ' '.join(slf.cmd):
                File(fname).touch(
                    'reviewers:      npwilkes (Approved)\n', newfile=True)
                return 0
            if 'pr view' in ' '.join(slf.cmd):
                File(fname).touch('reviewers:      npwilkes\n', newfile=True)
                return 0
            if 'git tag' in ' '.join(slf.cmd):
                File(fname).touch('TP_23A\n', newfile=True)
                return 0
            if 'git log TP_23A' in ' '.join(slf.cmd):
                File(fname).touch('Enabling FSM into 37D (#2681)\n', newfile=True)
                return 0
            raise Exception(f"Unknown cmd in fake_run_outfile(): {slf.cmd}")

        with TempDir(name=True) as tdir:
            cci = CCI('TP/38', 50)
            cci.tag_cache_dir = tdir

            with MockVar(CCI, 'get_curtime', Mock(return_value=1677888950.5311604)), \
                    MockVar(SystemCall, 'run_outfile', fake_run_outfile), \
                    MockVar(CCI, '_git_pull', Mock()), \
                    MockVar(AtomicRevisionManager, '_load_atomic_json', Mock(return_value={})), \
                    MockVar(os.environ, 'https_proxy', 'some_proxy'), \
                    MockVar(SystemCall, 'run_outtxt', fake_outtxt):

                _, result = cci.main(cmd_prcnt='SUM')
                self.assertEqual(result, ['TP_23A, 2023-03-02, 9'])

                _, result1 = cci.main(cmd_prcnt='DETAIL')
                _, result2 = cci.main(cmd_prcnt='TEAM')

            expect = '''
['TP_23A, 2023-03-02, 2681, None, danny-phan-intel, Save default empty pup solution to enable MO ENG_TPs/MVs [Shar]',
 'TP_23A, 2023-03-02, 2672, None, feng-wang-intel, NSIO/37_PCIE5_kill : PCIE5 gen5 nonisio back in kill (FIX)',
 'TP_23A, 2023-03-02, 2666, None, megha-jacob-intel, soc_main python file update',
 'TP_23A, 2023-03-02, 2521, None, victor-danielle-gatc, update sherlock.trigger.txt file to set a new error for Duplicate Plist t [PORT]',
 'TP_23A, 2023-03-02, 2655, None, kavya-gangavarapu-in, SFUN/SFUN_37C to TP/37 merge: SFUN SXM patmod update from evg to prime',
 'TP_23A, 2023-03-02, 2628, None, vrchandr, Torch TOS Rule Redundant removal for DRV_RESET_SXS  refpll update and mplla/b pr',
 'TP_23A, 2023-03-02, 2652, None, kenneth-j-anderson-i, Integ/37B0C to TP/37 post-Validation [User]',
 'TP_23A, 2023-03-02, 2625, None, victor-danielle-gatc, TPI/ Remove PLIST_PROD_FILE_NAME in all env file to address QE ticke [EnvF Envi]',
 'TP_23A, 2023-03-02, 2649, None, trannhi28, FUS/P281_37B_Final_FFR to TP/37B Merge:37B Final FFR Update PR [EnvF]']
'''
            self.assertTextEqual(pformat(result1, width=200), expect)
            expect = '''
['TP_23A, 2681, Shared, Shared, Save default empty pup solution to enable MO ENG_TPs/MVs [Shar]',
 'TP_23A, 2672, NSIO, NSIO_PCIE5_IXP, NSIO/37_PCIE5_kill : PCIE5 gen5 nonisio back in kill (FIX)',
 'TP_23A, 2672, NSIO, NSIO_PCIE5_IXPK, NSIO/37_PCIE5_kill : PCIE5 gen5 nonisio back in kill (FIX)',
 'TP_23A, 2666, CLK, CLK, soc_main python file update',
 'TP_23A, 2521, PORTP, PORTP, update sherlock.trigger.txt file to set a new error for Duplicate Plist t [PORT]',
 'TP_23A, 2655, SFUN, SFUN_TAM_SXM, SFUN/SFUN_37C to TP/37 merge: SFUN SXM patmod update from evg to prime',
 'TP_23A, 2655, TPI, TPI, SFUN/SFUN_37C to TP/37 merge: SFUN SXM patmod update from evg to prime',
 'TP_23A, 2655, WBIO, WBIO_CSI, SFUN/SFUN_37C to TP/37 merge: SFUN SXM patmod update from evg to prime',
 'TP_23A, 2655, WBIO, WBIO_DP, SFUN/SFUN_37C to TP/37 merge: SFUN SXM patmod update from evg to prime',
 'TP_23A, 2628, DRV, DRV_RESET_SXS, Torch TOS Rule Redundant removal for DRV_RESET_SXS  refpll update and mplla/b pr',
 'TP_23A, 2652, TPI, TPI_BASEPRIM_Y28K, Integ/37B0C to TP/37 post-Validation [User]',
 'TP_23A, 2652, Uservar, Uservar, Integ/37B0C to TP/37 post-Validation [User]',
 'TP_23A, 2625, EnvFile, EnvFile, TPI/ Remove PLIST_PROD_FILE_NAME in all env file to address QE ticke [EnvF Envi]',
 'TP_23A, 2625, EnvironmentFile, EnvironmentFile, TPI/ Remove PLIST_PROD_FILE_NAME in all env file to address QE ticke [EnvF Envi]',
 'TP_23A, 2649, Class, Class_MTL_P28, FUS/P281_37B_Final_FFR to TP/37B Merge:37B Final FFR Update PR [EnvF]',
 'TP_23A, 2649, EnvFile, EnvFile, FUS/P281_37B_Final_FFR to TP/37B Merge:37B Final FFR Update PR [EnvF]']
'''
            self.assertTextEqual(pformat(result2, width=200), expect)

    @with_(MockVar, TPBotFail, 'get_list', Mock(return_value=[]))
    def test_no_output(self):
        cci = CCI('TP/38', 50)

        def fake_run_outfile(slf, fname):
            """fake run_outfile"""
            File(fname).touch(newfile=True)
            return 0

        with CaptureStdoutLog() as p, \
                MockVar(CCI, 'get_curtime', Mock(return_value=1677888950.5311604)), \
                MockVar(CCI, '_git_pull', Mock()), \
                MockVar(SystemCall, 'run_outfile', fake_run_outfile):
            cci.main()

        self.assertEqual(cci.data, {})

    def test_gitpull(self):
        # interval is negative
        with TempDir(chdir=True):
            cci = CCI('TP/38', 50)
            self.assertEqual(cci._git_pull(interval=-10), 1)

        # pull=True
        with TempDir(chdir=True):
            cci = CCI('TP/38', 50)
            cci.OPT = {'pull': 'True'}
            self.assertEqual(cci._git_pull(interval=500), 1)

        # Nothing - it's up to date
        with TempDir(chdir=True):
            cci = CCI('TP/38', 50)
            self.assertEqual(cci._git_pull(interval=500), 0)

        # pull=True with submodule
        with TempDir(chdir=True):
            cci = CCI('TP/38', 50)
            cci.OPT = {'pull': 'True'}
            self.assertEqual(cci._git_pull(submodule=True, interval=500), 1)

    @with_(TempDir, chdir=True)
    def test_viewlog(self):
        cci = CCI('TP/38', 50, repo='blah')
        cci.OPT = {'viewlog': './abc.txt'}
        File('./abc.txt').touch("Hello there")
        with CaptureStdoutLog() as p, \
                MockVar(SuccessRate, 'LOGDIR', './'):
            with self.assertRaises(SystemExit):
                cci._viewlog()
        expect = '''
<pre>
Hello there
</pre>
'''
        self.assertTextEqual(p.getvalue(), expect)

    @with_(TempDir, chdir=True)
    def test_viewlog2(self):
        cci = CCI('TP/38', 50, repo='blah')
        cci.OPT = {'viewlog2': './abc.txt'}
        File('./abc.txt').touch("Hello there2")
        with CaptureStdoutLog() as p, \
                MockVar(TPBotFail, 'TESTERLOGS', './'):
            with self.assertRaises(SystemExit):
                cci._viewlog2()
        expect = '''
<pre>
Hello there2
</pre>
'''
        self.assertTextEqual(p.getvalue(), expect)

    @with_(TempDir, chdir=True)
    def test_tbr(self):
        cci = CCI('TP/38', 50, repo='blah')
        cci.OPT = {'tbr': 'ut_aa,ut_bb'}

        File('./ut_aa/junk').touch(mkdir=True)
        File('./ut_aa/2024-08-23.json').touch('''
{
   "total": [],
   "failinit": [],
   "failload": [],
   "cancelled": [],
   "rc": []
}''', mkdir=True)
        File('./ut_aa/2024-09-23.json').touch('''
{
   "pass": [
      "./2024-09-04/buildtp_tbd_JF04TXBT64287A_1725441656.log.gz",
      "./2024-09-04/buildtp_tbd_JF04TXBT64287A_1725480226.log.gz",
      "./2024-09-04/buildtp_tbd_JF04TXBT64287A_1725482578.log.gz",
      "./2024-09-04/buildtp_tbd_JF04TXBT64287A_1725494212.log.gz",
      "./2024-09-04/buildtp_tbd_JF04TXBT64287A_1725497118.log.gz"
   ],
   "total": [
      "./2024-09-04/buildtp_tbd_JF04TXBT64287A_1725441656.log.gz",
      "./2024-09-04/buildtp_tbd_JF04TXBT64287A_1725474365.log.gz",
      "./2024-09-04/buildtp_tbd_JF04TXBT64287A_1725475343.log.gz",
      "./2024-09-04/buildtp_tbd_JF04TXBT64287A_1725480226.log.gz",
      "./2024-09-04/buildtp_tbd_JF04TXBT64287A_1725482578.log.gz",
      "./2024-09-04/buildtp_tbd_JF04TXBT64287A_1725494212.log.gz",
      "./2024-09-04/buildtp_tbd_JF04TXBT64287A_1725497118.log.gz"
   ],
   "failsi": [
      "./2024-09-04/buildtp_tbd_JF04TXBT64287A_1725475343.log.gz"
   ],
   "failinit": [],
   "failload": [],
   "cancelled": [],
   "rc": []
}''', mkdir=True)
        File('./faildb/ut_aa/a.json').touch('''
{
   "prno": "1071",
   "logpath": "I:/engineering/dev/team_classtp/torch/testerload/2024-09-23/ituff_CLASSHOT_1_TestUnitLog_2024-09-23-16-02-28.txt",
   "time": 1727133924.5508578,
   "author": "danny-phan-intel",
   "title": "Default TP setup to 75W0Z and A1 part type",
   "comment": "PR updated default uservar setup for part type to A1 material, but the bot script was still setting A0, so PR failed due to wrong part",
   "dispo": "SETUP",
   "user": "dannypha"
}''', mkdir=True)
        File('./faildb/ut_aa/b.json').touch('''
{
   "prno": "1072",
   "logpath": "",
   "time": 1717133924.5508578,
   "author": "danny-phan-intel",
   "title": "Default TP",
   "comment": "This PR should not show up since it is pretty old",
   "dispo": "SETUP",
   "user": "dannypha"
}''', mkdir=True)

        with CaptureStdoutLog() as p, \
                MockVar(SuccessRate, 'CACHEDIR', './'), \
                MockVar(SuccessRate, 'LOGDIR', './'), \
                MockVar(TPBotFail, 'ROOTDB', './faildb'):
            with self.assertRaises(SystemExit):
                cci._tpbotreport()
        File('result.txt').touch(p.getvalue())
        self.assertGoldEqual('result.txt', f'{UT_DIR}/cci_pr/botfail.gold2')

    @with_(TempDir, chdir=True)
    def test_tpbotfail(self):
        cci = CCI('TP/38', 50, repo='blah')
        cci.OPT = {'tpbotfail': './abc.json',
                   'dispo': 'MV'}
        File('./abc.json').touch('{"logpath": "a.txt"}')
        File('./a.txt').touch('This is sometext')
        with CaptureStdoutLog() as p, \
                MockVar(TPBotFail, 'ROOTDB', './'):
            with self.assertRaises(SystemExit):
                cci._tpbotfail()
        self.assertIn('This is sometext', p.getvalue())
        self.assertIn('input type="hidden" name="dispo" value="MV"', p.getvalue())

    def test_z_evg(self):   # need to be after pr_age
        cci = CCI('TP/38', 50, repo='blah')
        cci.OPT = {'evg': True}
        with CaptureStdoutLog() as p:
            with TempDir(name=True, chdir=True, startcopy=f'{UT_DIR}/Simple4') as tdir:
                File(tdir).chmod('02770')
                with self.assertRaises(SystemExit):
                    cci._evg()
        expect = '''
Module,EVG_count,Prime_count,Total
ARRX,4,0,4
PTH,3,0,3
SCNX,0,3,3
'''
        self.assertTextEqual('\n'.join([x for x in p.getvalue().split('\n') if ',' in x]), expect)

        cci.OPT = {'evg': 'detail'}
        with CaptureStdoutLog() as p:
            with TempDir(name=True, chdir=True, startcopy=f'{UT_DIR}/Simple3a') as tdir:
                File(tdir).chmod('02770')
                with self.assertRaises(SystemExit):
                    cci._evg()
        expect = '''
Type,Template,Module,tname
EVG,iCFuncTest,ARRX,CCB
EVG,iCFuncTest,ARRX,CCD
EVG,iCFuncTest,PTH,CCA_1200_blah_1502
EVG,iCFuncTest,SCNX,CCB
EVG,iCGlXpressTest,ARRX,TPIE_PgmRules
EVG,iCGlXpressTest,PTH,TPIE_PgmRules
EVG,iCGlXpressTest,SCNX,TPIE_PgmRules
EVG,iCSimpleScoreboardTest,ARRX,CCA
EVG,iCSimpleScoreboardTest,PTH,CCA_1100_blah_1501
EVG,iCSimpleScoreboardTest,SCNX,CCA
'''
        self.assertTextEqual('\n'.join([x for x in p.getvalue().split('\n') if ',' in x]), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, 'JF only test due to time zone dependence')
    def test_pr_age(self):
        cci = CCI('TP/38', 50, repo='blah')
        cci.OPT = {'PR_AGE': True}
        text = '''[
  {
    "createdAt": "2023-05-16T21:49:12Z",
    "mergedAt": "2023-05-16T23:58:12Z",
    "changedFiles":1,
    "number": 3559
  },
  {
    "createdAt": "2023-05-15T16:30:41Z",
    "mergedAt": "2023-05-16T00:04:23Z",
    "changedFiles":1,
    "number": 3536
  },
  {
    "createdAt": "2023-05-11T22:14:30Z",
    "mergedAt": "2023-05-12T02:51:17Z",
    "changedFiles":1,
    "number": 3510
  }
]'''
        with MockVar(SystemCall, 'run_outtxt', Mock(return_value=(0, text))):
            with CaptureStdoutLog() as p:
                with self.assertRaises(SystemExit):
                    cci._pr_age()
        expect = '''<pre>
pr#,age_in_secs,merge_date,ww,changedFiles
3559,7740.0,2023-05-16,2023.ww20,1
3536,27222.0,2023-05-15,2023.ww20,1
3510,16607.0,2023-05-11,2023.ww19,1
</pre>
'''
        self.assertTextEqual(p.getvalue(), expect)

    def test_divhide(self):
        with CaptureStdoutLog() as p:
            with DivHide('a', pre=True):
                print("Hello")
        expect = '''
<div id="statusa">
<pre>
Hello
</pre>

</div>
<script>
    var myDiv = document.getElementById("statusa");
    myDiv.style.display = "none";
</script>

'''
        self.assertTextEqual(p.getvalue(), expect)

    def test_repo_not_found(self):
        # repo not found
        cci = CCI('TP/38', 50, repo='blah')
        with self.assertRaises(SystemExit):
            cci.read_config()

        # Legit config
        cci = CCI('TP/37', 50)
        self.assertGreater(len(cci.read_config(valid_list=True)), 2)   # must be first
        self.assertEqual(cci.read_config(), 1)
        self.assertEqual(cci.read_config(), 0)

        # help
        cci = CCI(None, 50)
        with self.assertRaises(SystemExit):
            with CaptureStdoutLog() as p:
                cci.main()
        self.assertIn('Valid repo values', p.getvalue())

    def test_diebins_status_nvl(self):
        cci = CCI('TP/38', 50, repo='blah', disp=True)

        # empty
        text = '''
### Why is this PR needed?
_Provide a concise summary explaining the motivation for this change._

### Who/Where is the source of the request of this PR change?
_Specify HSD URL, GitHub issue number (e.g., #1234), or if coming from TPTracker, CTP, etc._

### Which Die is affected (CPU, GCD, HUB, PCD)?
- [ ] CPU
- [ ] GCD
- [ ] HUB
- [ ] PCD

### What Bin(s) are affected (e.g., B60)?
_List all affected bins:_
e.g., B60

### Socket(s) affected by this PR (HOT/COLD/PHM)?
- [ ] HOT
- [ ] COLD
- [ ] PHM
'''
        self.assertEqual(cci._diebins_status(text), '')

        # filled up
        text = '''
### Why is this PR needed?
some blah

### Who/Where is the source of the request of this PR change?
_Specify HSD URL, GitHub issue number (e.g., #1234), or if coming from TPTracker, CTP, etc._

### Which Die is affected (CPU, GCD, HUB, PCD)?
- [X] CPU
- [ ] GCD
blah
- [X] HUB
- [ ] PCD

### What Bin(s) are affected (e.g., B60)?
B60

### Socket(s) affected by this PR (HOT/COLD/PHM)?
- [ ] HOT
- [ ] COLD
- [ ] PHM
'''
        self.assertEqual(cci._diebins_status(text, {'title': 'ms1'}), 'CPU, HUB, B60, ms1')

        # special - all are filled
        text = '''
### Why is this PR needed?
some blah

### Which Die is affected (CPU, GCD, HUB, PCD)?
- [X] CPU
- [X] GCD
- [X] HUB
- [X] PCD
'''
        self.assertEqual(cci._diebins_status(text), 'ALL')

    def test_diebins_status_arl(self):
        cci = CCI('TP/38', 50, repo='blah', disp=True)

        # Basic
        text = '''What is this PR for? blah

Which Die is affected (CDIE, GDIE, SOC)? CDIE

What Bin(s) are affected (B60)?
B60
'''
        self.assertEqual(cci._diebins_status(text), 'CDIE, B60')

        # missing CDIE
        text = '''What is this PR for? blah

Which Die is affected (CDIE, GDIE, SOC)?

What Bin(s) are affected (B60)?
B60,B70,B80

Sockets?
'''
        self.assertEqual(cci._diebins_status(text), 'B60,B70')

        # missing B60
        text = '''What is this PR for? blah

Which Die is affected (CDIE, GDIE, SOC)?
CDIE

What Bin(s) are affected (B60)?

Sockets?
'''
        self.assertEqual(cci._diebins_status(text), 'CDIE')

        # none specified
        text = '''What is this PR for? blah

Which Die is affected (CDIE, GDIE, SOC)?
What Bin(s) are affected (B60)?
Sockets?
'''
        self.assertEqual(cci._diebins_status(text), '')
        self.assertEqual(cci._diebins_status('blah'), '')

        # coverage1 - all is exhausted
        text = '''What is this PR for? blah

Which Die is affected (CDIE, GDIE, SOC)?
'''
        self.assertEqual(cci._diebins_status(text), '')

        # coverage2 - all is exhausted
        text = '''What is this PR for? blah

What Bin(s) are affected (B60)?
'''
        self.assertEqual(cci._diebins_status(text, {'blah': 1}), '')

        self.assertEqual(cci._diebins_status(text, {'title': 'ms1'}), 'ms1')

    def test_module_status(self):
        cci = CCI('TP/38', 50, repo='blah', disp=True)

        # Less than 3, combined team, truncated, ignored labels
        self.assertEqual(cci._module_status({'READY', 'PASSED_Si', 'ARR_CORE', 'ARR_CCF', 'EnvironmentFile', 'SCN_X'}),
                         'ARR,SCN')

        # more than 3
        self.assertEqual(cci._module_status({'ARR_CORE', 'FB21', 'TPI_X', 'SCN_1', 'PTH_2', 'I_REVIEWED', 'EnvironmentFile'}),
                         'ARR,PTH,SCN,+1')

    def test_title(self):
        cci = CCI('TP/38', 50, repo='blah', disp=True)
        self.assertEqual(cci._title('Some title', {'READY', 'PASSED_Si'}),
                         'Some title')
        self.assertEqual(cci._title('Some title Very Long Very Long Very Long Very Long Very Long Very Long ending',
                                    {'EnvironmentFile', 'ProgramFlows'}),
                         'Some title Very Long Very Long Very Long Very Long Very Long Very Lo [Envi,Prog]')

    def test_isdisp(self):
        with CaptureStdoutLog() as p:
            cci = CCI('TP/38', 50, repo='blah', disp=True)
            cci.disp_status("blah")
        self.assertEqual(p.getvalue(), "blah<br>\n")

        with CaptureStdoutLog() as p:
            cci = CCI('TP/38', 50, repo='blah', disp=False)
            cci.disp_status("blah")
        self.assertEqual(p.getvalue(), "")

        self.assertTrue(cci.get_curtime())   # make sure it returns something

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, 'JF only test due to time zone dependence')
    def test_utc(self):
        # make sure utc is correct
        self.assertEqual(curtime(seconds=utc2local('2023-03-03T23:01:23Z').timestamp()),
                         '2023-03-03_15:01:23')

    def test_call_pr_list(self):

        def fake(*args):
            result[0] += 1
            return []

        # default
        result = [0]
        cci = CCI('TP/38', 50, disp=True)
        with MockVar(cci, '_call_pr_list', fake):
            cci._set_all_pr()
        self.assertEqual(result[0], 2)   # called twice
        self.assertEqual(cci.data, {})

        # open only
        result = [0]
        cci = CCI('TP/38', 50, disp=True, prtype='open')
        with MockVar(cci, '_call_pr_list', fake):
            cci._set_all_pr()
        self.assertEqual(result[0], 1)   # called once
        self.assertEqual(cci.data, {})

    def test_set_approved(self):

        def fake(*args, **kwargs):
            # why eval() so that pep8 will not kick in. Below is cut and paste from gh action
            return eval('''
[
  {
    "number": 269,
    "reviews": []
  },
  {
    "number": 270,
    "reviews": []
  },
  {
    "number": 265,
    "reviews": [
      {
        "author": {
          "login": "skorlam1994"
        },
        "authorAssociation": "CONTRIBUTOR",
        "body": "Approved.",
        "submittedAt": "2024-01-30T01:32:06Z",
        "includesCreatedEdit": False,
        "reactionGroups": [],
        "state": "APPROVED"
      }
    ]
  },
  {
    "number": 264,
    "reviews": [
      {
        "author": {
          "login": "mockedup"
        },
        "state": "ChangeRequested"
      }
    ]
  }
]
''')

        # default
        cci = CCI('TP/38', 50, disp=True)
        cci.data = {269: {},
                    265: {},
                    264: {}}
        with MockVar(cci, '_call_pr_list', fake):
            cci._set_approved()
        self.assertEqual(cci.data, {269: {'approved': 'Need_Review'},
                                    265: {'approved': 'Approved'},
                                    264: {'approved': 'Need_Review'}})

    def test_process_bundle(self):
        cci = CCI('TP/38', 50, repo='blah', disp=True)
        cci.data = {123: {'title': 'random',
                          'labels': set(),
                          'merge_age': 1,
                          'openclose': 'merged'},
                    222: {'title': 'random',
                          'labels': {'READY'},
                          'merge_age': 1,
                          'openclose': 'merged'},
                    456: {'title': 'bundle of 2: 123 987 222',
                          'merge_age': 5,
                          'labels': set(),
                          'openclose': 'merged'}
                    }
        cci._process_bundle()
        expect = '''123.labels.[0] = 'PASSED_Si'
123.merge_age = 6
123.openclose = 'merged'
123.title = 'random'
222.labels.[0] = 'PASSED_Si'
222.labels.[1] = 'READY'
222.merge_age = 6
222.openclose = 'merged'
222.title = 'random'
456.merge_age = 5
456.openclose = 'merged'
456.title = 'bundle of 2: 123 987 222'
'''
        self.assertTextEqual(Dumper(cci.data, dot=True).string(), expect)

    def test_id_manual(self):
        cci = CCI('TP/38', 50, repo='blah', disp=True)
        self.assertEqual(cci._manual_status(['blah']), ' Manual')
        self.assertEqual(cci._manual_status(['PASSED_Si', 'blah']), '')
        self.assertEqual(cci._manual_status(['I_AM_TPI_Skip_Bot', 'blah']), ' BotSkip')
        self.assertEqual(cci._manual_status(['I_AM_TPI_Skip_Bot', 'PASSED_Si']), ' BotSkip')
        self.assertEqual(cci._manual_status(['tprobot_A', 'tprobot_B']), '')
        self.assertEqual(cci._manual_status(['FAILED_HX', 'tprobot_A']), ' Manual,FAIL_HX')
        self.assertEqual(cci._manual_status(['tprobot_HX', 'FAILED_HXC', 'tprobot_S28C']), '')
        self.assertEqual(cci._manual_status(['tprobot_HX', 'FAILED_HXC', 'FAILED_S28C']), ' Manual,FAIL_S28C')

    def test_label_status(self):
        cci = CCI('TP/38', 50, repo='blah', disp=True)
        status = []
        cci._label_status(status, ['AAREADY', 'FAILED_Si', 'RANDOM',
                                   'TEST_IN_PROGRESS', 'I_AM_TPI_Skip_Bot'])
        self.assertEqual(status, ['AAREADY', 'FAILED_Si', 'BotSkip', 'TEST_IN_PROGRESS', 'Missing_Chk'])

        status = []
        cci._label_status(status, ['PASSED_Chk', 'BLAH', 'READY', 'FAILED'])
        self.assertEqual(status, ['FAILED', 'READY'])

        status = []
        cci._label_status(status, ['PASSED_Chk', 'BLAH', 'FAILED_Si', 'FB44'])
        self.assertEqual(status, ['FAILED_Si', 'FB44'])

    def test_set_tags(self):
        # Pass it when the list of tag is correct

        # This function will define a list of tags
        def fake_list_of_tags(slf, fname):
            fake_tags = '''
TP_38D0D 24e75361abcc15b61554957e4acce8169e934099 Added the following subflows: (#4137)
TP_38E0A 030f96a36945b09365d3d41f67c499f5ab3dbab7 Default TPName/FSM solution to 38E
TP_38ZZZ 030f96a36945b09365d3d41f67c499f5ab3dbab7 Default TPName/FSM solution to 38E
TP_38E0B 085f2463824ab02ab0ed5229df7859dc8485f91b CCF parsbo #4193 #4194 skipped for chain atpg and tatpg
'''
            File(fname).touch(fake_tags, newfile=True)
            return 0

        cci = CCI('TP/38', 50, repo='mtlp68', disp=True)
        cci.cfg = {}
        cci.data = {4137: {},
                    4193: {},
                    4167: {}}
        with MockVar(SystemCall, 'run_outfile', fake_list_of_tags):
            tag_list = cci._set_tags_list()
            self.assertEqual(tag_list, [None, 'TP_38D0D', 'TP_38E0A', 'TP_38ZZZ', 'TP_38E0B'])
            self.assertEqual(cci.data, {4137: {'tags': 'TP_38D0D'},
                                        4167: {'tags': 'TP_38E0A'},
                                        4193: {'tags': 'TP_38E0B'}})

    @with_(TempDir, chdir=True)
    def test_get_tag_prno(self):
        cci = CCI('TP/38', 50, repo='mtlp68', disp=True)
        cci.tag_cache_dir = '.'

        # normal case
        line = 'TP_60B0D 2c2b043ef36651aa2be665c98b24b1129aab4ad3 Merge pull request #513 from intel-restricted/FUN'
        cci.data = {513: {}}
        self.assertEqual(cci._get_tag_prno(line), 'TP_60B0D')
        self.assertEqual(cci.data, {513: {'tags': 'TP_60B0D'}})

        # not found case
        cci.data = {12: {}}
        self.assertEqual(cci._get_tag_prno('TP_99B0D beef none'), 'TP_99B0D')
        self.assertEqual(cci.data, {12: {}})

        # not found case, but found in git log
        cci.data = {12: {}}
        text = '''
commit 2c2b043ef36651aa2be665c98b24b1129aab4ad3 (tag: TP_60B0D)
Merge: 2053f6f8 9c1b1ae6
Author: shiv-gourshetty-intel <107504937+shiv-gourshetty-intel@users.noreply.github.com>
Date:   Fri Oct 6 15:02:09 2023 -0700

    Fun/fun ccf bpkosara ww39 To TP/60 FUN CCF Initial Module release

commit 9c1b1ae6373a31b3aaf9ab24ec1f770f2ffe5331
Merge: 6ae61250 2053f6f8
Author: maria-luisa-ignacio-intel <109625786+maria-luisa-ignacio-intel@users.noreply.github.com>
Date:   Fri Oct 6 13:47:02 2023 -0700

    Merge branch 'TP/60' into FUN/FUN_CCF_bpkosara_ww39 (#11)

commit 2053f6f8769b46126fac67a966abfcd6788ae9ff
Author: edward-j-sayers-intel <102987833+edward-j-sayers-intel@users.noreply.github.com>
Date:   Fri Oct 6 13:31:53 2023 -0700

    FUN_CORE_C68 Initial release (#12)

'''

        def fake_run_outfile(slf, fname):
            """fake run_outfile"""
            if 'git log' in ' '.join(slf.cmd):
                File(fname).touch(text, newfile=True)
                return 0
            raise Exception(f"Unknown cmd in fake_run_outfile(): {slf.cmd}")

        with MockVar(SystemCall, 'run_outfile', fake_run_outfile):
            self.assertEqual(cci._get_tag_prno('TP_99B0D beef none'), 'TP_99B0D')
            self.assertEqual(cci.data, {12: {'tags': 'TP_99B0D'}})

        # cached case
        cci.data = {12: {}}
        self.assertEqual(cci._get_tag_prno('TP_99B0D beef none'), 'TP_99B0D')
        self.assertEqual(cci.data, {12: {'tags': 'TP_99B0D'}})

    def test_get_atomic_info(self):
        # Test _get_atomic_info method for various BOM flag scenarios
        cci = CCI('main', 50, repo='nvlcommon')

        def fake_load_atomic_json():
            return {
                '100': ['1.0'],  # Old format - no BOM flags
                '101': ['2.0.00000000000'],  # All zeros
                '102': ['2.0.11111111111'],  # All ones
                '103': ['2.0.10000000001'],  # First and last
                '104': ['2.0.11000000001'],  # Multiple BOMs
                '105': ['2.0.01000000000'],  # Single middle BOM
                '106': ['2.0.00000000001'],  # Last BOM only
                '107': ['2.0.10100000000'],  # Non-contiguous BOMs
                '108': ['2.0.00000000010'],  # Second-to-last BOM
                '109': ['2.0.11111111110'],  # All but last
                '110': ['2.0.1'],  # Anomaly - wrong format
                '999': ['1.5', '1.6.11000000000']  # Multiple revisions
            }

        with MockVar(cci.atomic_mgr, '_load_atomic_json', fake_load_atomic_json):
            # Test old format with no BOM flags
            atomic_rev, atomic_bom = cci.atomic_mgr._get_atomic_info('100')
            self.assertEqual(atomic_rev, '1.0')
            self.assertEqual(atomic_bom, 'NA')

            # Test all zeros
            atomic_rev, atomic_bom = cci.atomic_mgr._get_atomic_info('101')
            self.assertEqual(atomic_rev, '2.0')
            self.assertEqual(atomic_bom, 'NA')

            # Test all ones (All_BOM)
            atomic_rev, atomic_bom = cci.atomic_mgr._get_atomic_info('102')
            self.assertEqual(atomic_rev, '2.0')
            self.assertEqual(atomic_bom, 'All_BOM')

            # Test multiple BOMs
            atomic_rev, atomic_bom = cci.atomic_mgr._get_atomic_info('104')
            self.assertEqual(atomic_rev, '2.0')
            self.assertIn('NVL_S28C', atomic_bom)
            self.assertIn('NVL_S52C', atomic_bom)
            self.assertIn('NVL_AX16C', atomic_bom)

            # Test non-contiguous BOMs
            atomic_rev, atomic_bom = cci.atomic_mgr._get_atomic_info('107')
            self.assertEqual(atomic_rev, '2.0')
            self.assertIn('NVL_S28C', atomic_bom)
            self.assertIn('NVL_S28C_BLLC', atomic_bom)

            # Test anomaly (wrong format)
            atomic_rev, atomic_bom = cci.atomic_mgr._get_atomic_info('110')
            self.assertEqual(atomic_bom, 'NA')

            # Test multiple revisions
            atomic_rev, atomic_bom = cci.atomic_mgr._get_atomic_info('999')
            self.assertIn('1.5', atomic_rev)
            self.assertIn('1.6', atomic_rev)

    def test_load_atomic_json(self):
        # Test _load_atomic_json caching behavior
        cci = CCI('main', 50, repo='nvlcommon')

        # Mock file operations
        def fake_exists(path):
            return True

        def fake_access(path, mode):
            return True

        def fake_open_json():
            return {
                "latest": "2.0.11111111111",
                "nvl.common": {"100": ["2.0.11111111111"]}
            }

        # Test caching - should only read file once
        read_count = [0]

        def mock_file_read():
            read_count[0] += 1
            return json.dumps(fake_open_json())

        import builtins
        from unittest.mock import MagicMock, mock_open

        with MockVar(os.path, 'exists', fake_exists), \
                MockVar(os, 'access', fake_access), \
                MockVar(cci.atomic_mgr, '_atomic_json_cache', None):

            # First call should read file
            m_open = mock_open(read_data=json.dumps(fake_open_json()))
            with MockVar(builtins, 'open', m_open):
                result1 = cci.atomic_mgr._load_atomic_json()
                self.assertEqual(m_open.call_count, 1)

            # Second call should use cache
            result2 = cci.atomic_mgr._load_atomic_json()
            self.assertEqual(m_open.call_count, 1)  # Still 1, no additional read

            # Results should be same
            self.assertEqual(result1, result2)

    def test_get_initial_atomic_rev(self):
        # Test _get_initial_atomic_rev method with timestamp-based display logic
        cci = CCI('main', 50, repo='nvlcommon')

        def fake_load_atomic_json():
            # JSON is ordered by actual merge sequence
            return {
                '50': ['1.0'],                 # Merged first (old)
                '80': ['1.1.10000000000'],     # Merged second
                '60': ['1.2.11000000000'],     # Merged third (most recent before display)
                '120': ['2.0.11111111111']     # Merged fourth (in display range)
            }

        # Mock display range PRs - note these are NOT in PR number order!
        # Display order by timestamp: 100, 101, 102, 61, 81, 103, 104...
        closed_PR = [100, 101, 102, 61, 81, 103, 104, 120]

        # Mock merge ages - higher means merged longer ago
        cci.data = {
            50: {'merge_age': 20},   # Very old
            80: {'merge_age': 15},   # Old
            60: {'merge_age': 12},   # Most recent before display (baseline)
            100: {'merge_age': 10},  # Oldest in display range
            101: {'merge_age': 9},
            102: {'merge_age': 8},
            61: {'merge_age': 7},    # Different PR, not same as JSON '60'
            81: {'merge_age': 6},    # Different PR, not same as JSON '80'
            103: {'merge_age': 5},
            104: {'merge_age': 4},
            120: {'merge_age': 3},   # Has its own atomic data
        }

        with MockVar(cci.atomic_mgr, '_load_atomic_json', fake_load_atomic_json):
            # Should find PR 60 (most recently merged before display range) and return its revision with BOM
            atomic_rev, atomic_bom = cci.atomic_mgr._get_initial_atomic_rev(closed_PR, cci.data)
            self.assertEqual(atomic_rev, '1.2')
            # '1.2.11000000000' has bits at positions 0,1 which map to NVL_S28C and NVL_S52C
            self.assertEqual(atomic_bom, 'NVL_S28C, NVL_S52C')

    def test_get_initial_atomic_rev_missing_from_display(self):
        # Test atomic PRs that are too old to be in display data (real-world scenario)
        cci = CCI('main', 50, repo='nvlgcd')

        def fake_load_atomic_json():
            # JSON ordered by merge sequence - PRs 15 and 500 are too old for display
            return {
                '15': ['1.1.11111111111'],     # Too old, not in display
                '500': ['1.2.10011111111'],    # Also too old, not in display (more recent than 15)
                '1095': ['2.0.11111111111']    # In display range
            }

        # Display range: recent PRs only (15 and 500 are too old to show)
        closed_PR = [1085, 1086, 1091, 1095]

        cci.data = {
            # NOTE: PR 15 and 500 are NOT in self.data (too old for 50-row display)
            1085: {'merge_age': 10},  # Older than 1095, should get baseline
            1086: {'merge_age': 9},   # Older than 1095, should get baseline
            1091: {'merge_age': 8},   # Older than 1095, should get baseline
            1095: {'merge_age': 7},   # Has its own atomic data (2.0)
        }

        with MockVar(cci.atomic_mgr, '_load_atomic_json', fake_load_atomic_json):
            # Should use PR 500's revision (1.2) as baseline since it's most recent before display
            atomic_rev, atomic_bom = cci.atomic_mgr._get_initial_atomic_rev(closed_PR, cci.data)
            self.assertEqual(atomic_rev, '1.2')
            # '1.2.10011111111' has multiple bits set which map to various NVL BOMs
            # Preserve original BOM order from BOM_MAPPING, not alphabetical
            self.assertEqual(atomic_bom, 'NVL_S28C, NVL_S16C, NVL_UL6C, NVL_U8C, NVL_H16C, NVL_P16C, NVL_HX28C, NVL_AX28C, NVL_AX16C')

    def test_get_initial_atomic_rev_multiple_revisions(self):
        # Test baseline handling when PR has multiple atomic revisions
        cci = CCI('main', 50, repo='nvlgcd')

        def fake_load_atomic_json():
            # JSON with PR having multiple revisions
            return {
                '500': ['1.5.10000000000', '1.6.11000000000'],  # Multiple revisions: one with 1 BOM, one with 2 BOMs
                '1095': ['2.0.11111111111']         # In display range
            }

        # Display range: recent PRs only (PR 500 is too old)
        closed_PR = [1085, 1086, 1095]

        cci.data = {
            # NOTE: PR 500 is NOT in self.data (too old for display)
            1085: {'merge_age': 10},  # Should get baseline
            1086: {'merge_age': 9},   # Should get baseline
            1095: {'merge_age': 7},   # Has its own atomic data (2.0)
        }

        with MockVar(cci.atomic_mgr, '_load_atomic_json', fake_load_atomic_json):
            # Should use PR 500's revisions (1.5 and 1.6) as baseline
            atomic_rev, atomic_bom = cci.atomic_mgr._get_initial_atomic_rev(closed_PR, cci.data)
            # Both revisions should be included, comma-separated
            self.assertEqual(atomic_rev, '1.5, 1.6')
            # BOM should deduplicate overlapping BOMs: NVL_S28C from 1.5 and NVL_S28C, NVL_S52C from 1.6
            # Result: sorted unique set = 'NVL_S28C, NVL_S52C'
            self.assertEqual(atomic_bom, 'NVL_S28C, NVL_S52C')

    def test_precompute_atomic_info(self):
        # Test that _precompute_atomic_info() correctly stores atomic info in PR data for NVL mode
        cci = CCI('main', 50, repo='nvlcommon')

        # Set up merged and open PRs with required fields
        cci.merged_prs = [
            {'number': 100, 'merge_age': 2},
            {'number': 200, 'merge_age': 1}
        ]
        cci.open_prs = [{'number': 300}]
        cci.data = {
            100: {'merge_age': 2, 'openclose': 'merged'},
            200: {'merge_age': 1, 'openclose': 'merged'},
            300: {'openclose': 'open'}
        }

        # Track which PRs get atomic info computed
        computed_prs = []

        def mock_get_atomic_info(prno, pr_data=None):
            computed_prs.append(prno)
            if prno == 100:
                return ('1.0.10000000000', 'NVL_S28C')
            elif prno == 200:
                return ('1.1.11000000000', 'NVL_S28C, NVL_S52C')
            else:
                return ('', '')

        with MockVar(cci.atomic_mgr, '_get_atomic_info', mock_get_atomic_info):
            cci._precompute_atomic_info()

        # Verify _computed_atomic_rev and _computed_atomic_bom are stored in PR data
        self.assertEqual(cci.data[100].get('_computed_atomic_rev'), '1.0.10000000000')
        self.assertEqual(cci.data[100].get('_computed_atomic_bom'), 'NVL_S28C')
        self.assertEqual(cci.data[200].get('_computed_atomic_rev'), '1.1.11000000000')
        self.assertEqual(cci.data[200].get('_computed_atomic_bom'), 'NVL_S28C, NVL_S52C')

        # Verify open PR also got computed
        self.assertEqual(cci.data[300].get('_computed_atomic_rev'), '')
        self.assertEqual(cci.data[300].get('_computed_atomic_bom'), '')

        # Verify all PRs were processed (merged and open)
        self.assertIn(100, computed_prs)
        self.assertIn(200, computed_prs)
        self.assertIn(300, computed_prs)


class TestSR(TestCase):

    @with_(TempDir, chdir=True)
    def test_basic(self):

        class UT(SuccessRate):
            LOGDIR = f'{os.getcwd()}/checkers'
            CACHEDIR = f'{os.getcwd()}/successrate_db'
            URL = 'h:'

        tb = 'Traceback (most recent call last)'
        fail = 'Error: FAILED_Si'

        mkdirs(UT.CACHEDIR)
        # pass case
        File('checkers/2023-07-05/JF04TXBT01.log').touch('FULL CMD: blah.py tprobotx\n', mkdir=True)
        # invalid case
        File('checkers/2023-07-05/JF04TXBT02.log').touch('FULL CMD: blah.py tproboty\n')
        File('checkers/2023-07-05/random.log').touch('FULL CMD: blah.py tprobotx\n', mkdir=True)
        File('checkers/Notebook.onetoc').touch()
        # fail case
        File('checkers/2023-07-05/JF04TXBT03.log').touch(f'FULL CMD: blah.py tprobotx\n{tb}\n')
        # fail case si
        File('checkers/2023-07-05/JF04TXBT04.log').touch(f'FULL CMD: blah.py tprobotx\n{tb}\n{fail}\n')
        # pass case - different day
        File('checkers/2023-07-06/JF04TXBT01.log').touch('FULL CMD: blah.py tprobotx\n', mkdir=True)
        # pass case - today day
        File(f'checkers/{UT.today()}/JF04TXBT01.log').touch('FULL CMD: blah.py tprobotx\n', mkdir=True)
        # empty day
        File('checkers/2023-07-07/JF04TXBT02.log').touch('FULL CMD: blah.py tproboty\n', mkdir=True)

        sr = UT('tprobotx')
        with CaptureStdoutLog() as p:
            sr.main()
        self.assertIn('Processing', p.getvalue())
        self.assertNotIn('2023-07-07 ', p.getvalue())
        self.assertNotIn('2023-07-08 ', p.getvalue())
        self.assertIn('2023-07-06   1/  1 = 100.00%', p.getvalue())
        self.assertIn('2023-07-05   1/  3 =  33.33%', p.getvalue())

        # run again, cached
        File(f'{UT.CACHEDIR}/tprobotx/Notebook.onetoc').touch()
        sr = UT('tprobotx')
        with CaptureStdoutLog() as p:
            sr.main()
        self.assertNotIn('Processing', p.getvalue())
        self.assertIn('2023-07-06   1/  1 = 100.00%', p.getvalue())
        self.assertIn('2023-07-05   1/  3 =  33.33%', p.getvalue())

    @with_(TempDir, chdir=True)
    def test_letters(self):

        class UT(SuccessRate):
            LOGDIR = f'{os.getcwd()}/checkers'
            CACHEDIR = f'{os.getcwd()}/successrate_db'
            URL = 'h:'

        tb = 'Traceback (most recent call last)'

        mkdirs(UT.CACHEDIR)

        # pass case
        aa = File('checkers/2023-07-05/JF04TXBT01.log')
        aa.touch('FULL CMD: blah.py tprobotx\n', mkdir=True)
        aa = File('checkers/2023-07-05/JF04TXBT02.log')
        aa.touch('FULL CMD: blah.py tproboty\n', mkdir=True)    # incorrect robot
        aa = File('checkers/2023-07-05/JF04TXBT03.log')
        aa.touch(f'FULL CMD: blah.py tprobotx\n{tb}\nError: something', mkdir=True)

        # invalid case
        aa = File('checkers/2023-07-06/JF04TXBT02.log')
        aa.touch(f'FULL CMD: blah.py tprobotx\n{tb}\n', mkdir=True)

        # fail case si
        aa = File('checkers/2023-07-07/JF04TXBT04.log')
        aa.touch(f'FULL CMD: blah.py tprobotx\n{tb}\nError: FAILED_Si\n', mkdir=True)

        # fail case failed init
        aa = File('checkers/2023-07-08/JF04TXBT04.log')
        aa.touch(f'FULL CMD: blah.py tprobotx\n{tb}\nError: FAILED_Init\n', mkdir=True)

        # fail case failed
        aa = File('checkers/2023-07-09/JF04TXBT04.log')
        aa.touch(f'FULL CMD: blah.py tprobotx\n{tb}\nError: [FAILED]\n', mkdir=True)

        # fail case cancelled
        aa = File('checkers/2023-07-10/JF04TXBT04.log')
        aa.touch(f'FULL CMD: blah.py tprobotx\n{tb}\nKeyboardInterrupt\n', mkdir=True)

        # fail case rc
        aa = File('checkers/2023-07-11/JF04TXBT04.log')
        aa.touch(f'FULL CMD: blah.py tprobotx\n{tb}\nError: TPI READY label does not exist\n', mkdir=True)

        sr = UT('tprobotx')
        with CaptureStdoutLog() as p:
            sr.main()
        expect = '''
<div id="status">
Processing 2023-07-05<br>
Processing 2023-07-06<br>
Processing 2023-07-07<br>
Processing 2023-07-08<br>
Processing 2023-07-09<br>
Processing 2023-07-10<br>
Processing 2023-07-11<br>

</div>
<script>
    var myDiv = document.getElementById("status");
    myDiv.style.display = "none";
</script>

<pre>
Legend: F: Silicon Fail, i: Init Fail, L: Load Fail, C: Cancelled run, R: TPI_READY, *: Other Fail

2023-07-09   0/  1 =   0.00%: <a href="h:?br=x&viewlog=./2023-07-09/JF04TXBT04.log">L</a>
2023-07-08   0/  1 =   0.00%: <a href="h:?br=x&viewlog=./2023-07-08/JF04TXBT04.log">i</a>
2023-07-07   0/  1 =   0.00%: <a href="h:?br=x&viewlog=./2023-07-07/JF04TXBT04.log">F</a>
2023-07-06   0/  1 =   0.00%: <a href="h:?br=x&viewlog=./2023-07-06/JF04TXBT02.log">*</a>
2023-07-05   1/  2 =  50.00%: <a href="h:?br=x&viewlog=./2023-07-05/JF04TXBT03.log">*</a>
</pre>

'''
        self.assertTextEqual(p.getvalue(), expect)

    @with_(TempDir, chdir=True)
    def test_checkers(self):

        class UT(CheckerRate):
            LOGDIR = f'{os.getcwd()}/checkers'
            CACHEDIR = f'{os.getcwd()}/successrate_db'
            URL = 'h:'

        tb = 'Traceback (most recent call last)'

        mkdirs(UT.CACHEDIR)
        File(f'{UT.CACHEDIR}/ignoreme.txt').touch()
        File('checkers/ignoreme.txt').touch('', mkdir=True)
        File('successrate_db/2023-07-03.json').touch('{ "total": [] }', mkdir=True)   # ignore json
        File('successrate_db/2023-07-04.json').touch('''{
   "pass": [],
   "total": ["./2023-07-04/buildtp1.log"],
   "Q": ["./2023-07-04/buildtp1.log"],
   "S": [],
   "G": [],
   "U": [],
   "T": [],
   "C": [],
   "E": []
}
''', mkdir=True)

        # pass case - today day
        File(f'checkers/{UT.today()}/buildtp1.log').touch('FULL CMD: buildtp.py FULL None\n', mkdir=True)

        # pass case
        aa = File('checkers/2023-07-04/buildtp1.log')     # This is already cached
        aa.touch('FULL CMD: buildtp.py FULL None\n', mkdir=True)
        aa = File('checkers/2023-07-05/buildtp1.log')
        aa.touch('FULL CMD: buildtp.py FULL None\n', mkdir=True)
        aa = File('checkers/2023-07-05/buildtp2.log')
        aa.touch('FULL CMD: buildtp.py FULL68 None\n', mkdir=True)    # incorrect robot
        aa = File('checkers/2023-07-05/buildtp2a.log')     # Ignore
        aa.touch('FULL CMD: buildtp.py FULL tprobot\n', mkdir=True)

        # fail cases
        aa = File('checkers/2023-07-05/buildtp3.log')
        aa.touch(f'FULL CMD: buildtp.py FULL None\n{tb}\nError: something', mkdir=True)
        aa = File('checkers/2023-07-06/buildtp3.log')
        aa.touch(f'FULL CMD: buildtp.py FULL None\n{tb}\nError: Torch export failed', mkdir=True)
        aa = File('checkers/2023-07-06/buildtp4.log')
        aa.touch(f'FULL CMD: buildtp.py FULL None\n{tb}\nError: GlobalPList blah', mkdir=True)

        sr = UT()
        with CaptureStdoutLog() as p:
            sr.main()
        expect = '''
<div id="status">
Processing 2023-07-05<br>
Processing 2023-07-06<br>

</div>
<script>
    var myDiv = document.getElementById("status");
    myDiv.style.display = "none";
</script>

<pre>
Legend:
   C: Cannot create a file when that file already exists
   E: Torch export failed
   G: GlobalPList
   Q: There are Quality Errors!
   S: Sherlock has errors
   T: There are TRC errors
   U: Unlocked pattern patch found

2023-07-06   0/  2 =   0.00%: <a href="h:?br=x&viewlog=./2023-07-06/buildtp3.log">E</a> <a href="h:?br=x&viewlog=./2023-07-06/buildtp4.log">G</a>
2023-07-05   2/  3 =  66.67%: <a href="h:?br=x&viewlog=./2023-07-05/buildtp3.log">*</a>
2023-07-04   0/  1 =   0.00%: <a href="h:?br=x&viewlog=./2023-07-04/buildtp1.log">Q</a>
</pre>

'''
        self.assertTextEqual(p.getvalue(), expect)


class TestSharedCCI(TestCase):

    @with_(TempDir, chdir=True)
    def test_tpbotsubmit(self):
        cci = CCI('TP/38', 50, repo='blah')
        cci.OPT = {'botfailsubmit': './abc.open.json',
                   'comment': 'it works',
                   '_user': 'jdr',
                   'dispo': 'MV'}
        File('./abc.open.json').touch('{"logpath": "a.txt"}')
        with CaptureStdoutLog() as p, \
                MockVar(TPBotFail, 'ROOTDB', './'):
            with self.assertRaises(SystemExit):
                cci._tpbotsubmit()

        self.assertEqual(os.listdir('.'), ['abc.json'])   # File is renamed
        expect = '''
{
   "logpath": "a.txt",
   "comment": "it works",
   "dispo": "MV",
   "user": "jdr"
}
'''
        self.assertTextEqual(File('abc.json').read(), expect)


class TestBomMappingIntegrity(TestCase):
    # Guardrail tests: adding a new BOM to BOM_MAPPING must not silently break
    # bitmask parsing, the consistency checker, or CCI display.

    def test_bom_mapping_no_duplicate_short_names(self):
        # BOM_MAPPING must not contain duplicate short names — duplicates would cause
        # incorrect bit-position lookups in both cci_list and check_atomic_consistency
        short_names = [short for _, short in AtomicChange.BOM_MAPPING]
        self.assertEqual(len(short_names), len(set(short_names)),
                         f'Duplicate short names in BOM_MAPPING: {short_names}')

    def test_bom_mapping_no_duplicate_display_names(self):
        # BOM_MAPPING display names (PR checkbox labels) must also be unique
        display_names = [display for display, _ in AtomicChange.BOM_MAPPING]
        self.assertEqual(len(display_names), len(set(display_names)),
                         f'Duplicate display names in BOM_MAPPING: {display_names}')

    def test_known_bit_positions_are_stable(self):
        # Spot-check that known BOMs remain at their expected bit positions.
        # If a new BOM is inserted in the MIDDLE it will shift these and fail here.
        short_names = [short for _, short in AtomicChange.BOM_MAPPING]
        self.assertEqual(short_names[0], 'NVL_S28C')
        self.assertEqual(short_names[10], 'NVL_AX16C')
        self.assertEqual(short_names[11], 'DNL_S28C')

    def test_parse_12bit_dnl_s28c_bit_set(self):
        # 12-bit mask with DNL_S28C (bit 11) set must include DNL_S28C in output
        cci = CCI('main', 50, repo='nvlcommon')

        def fake_load():
            return {'1': ['6.0.000000000001']}

        with MockVar(cci.atomic_mgr, '_load_atomic_json', fake_load):
            _, atomic_bom = cci.atomic_mgr._get_atomic_info('1')
            self.assertIn('DNL_S28C', atomic_bom)
            self.assertNotIn('NVL_S28C', atomic_bom)

    def test_parse_12bit_all_ones_is_all_bom(self):
        # 12-bit all-ones mask must resolve to All_BOM
        cci = CCI('main', 50, repo='nvlcommon')

        def fake_load():
            return {'1': ['6.0.111111111111']}

        with MockVar(cci.atomic_mgr, '_load_atomic_json', fake_load):
            _, atomic_bom = cci.atomic_mgr._get_atomic_info('1')
            self.assertEqual(atomic_bom, 'All_BOM')

    def test_parse_legacy_11bit_all_ones_still_all_bom(self):
        # Old 11-bit all-ones entries must still display as All_BOM after DNL_S28C was added
        cci = CCI('main', 50, repo='nvlcommon')

        def fake_load():
            return {'1': ['5.1.11111111111']}

        with MockVar(cci.atomic_mgr, '_load_atomic_json', fake_load):
            _, atomic_bom = cci.atomic_mgr._get_atomic_info('1')
            self.assertEqual(atomic_bom, 'All_BOM')

    def test_parse_single_char_anomaly_is_na(self):
        # Malformed bitmask of single '1' must not be mistaken for All_BOM
        cci = CCI('main', 50, repo='nvlcommon')

        def fake_load():
            return {'1': ['2.0.1']}

        with MockVar(cci.atomic_mgr, '_load_atomic_json', fake_load):
            _, atomic_bom = cci.atomic_mgr._get_atomic_info('1')
            self.assertNotEqual(atomic_bom, 'All_BOM')


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
