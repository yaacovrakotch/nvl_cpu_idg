#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for ctp_cron.py
"""
from setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE    # must be first import for unittests
from main.ctp_cron import *
from unittest.mock import Mock
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.gizmo import MockVar
from gadget.helperclass import CaptureStdoutLog
from gadget.files import TempDir, File
from gadget.disk import mkdirs
from pprint import pprint
import main.ctp_cron as ctp_cron


class CTPTest(TestCase):

    def test_derive_args(self):
        res = CTPCron.derive_args('eseu.py rsync -rlptoDv al4vprtptxap1.ra.intel.com:/nfs/td_sdx_1278_arh_prod_vol/td_1278_arh_prod_sds/hdmtprogs /nfs/pdx/disks/mpe_sctp_004/torch/ctp_tp/10047575_sds')
        pprint(res)
        self.assertEqual(res, {'dest': '/nfs/pdx/disks/mpe_sctp_004/torch/ctp_tp/10047575_sds/tp',
                               'host': 'al4vprtptxap1.ra.intel.com',
                               'rpath': '/nfs/td_sdx_1278_arh_prod_vol/td_1278_arh_prod_sds/hdmtprogs',
                               'tlpath': '/nfs/pdx/disks/mpe_sctp_004/torch/ctp_tp/10047575_sds/rsync_tpname'})

        self.assertEqual(CTPCron.derive_args('rsync host:blah blah'), None)

    def test_proc_rsync_output(self):
        # empty
        ctp = CTPCron()
        txt = '''receiving incremental file list

sent 1,951 bytes  received 621,948 bytes  40,251.55 bytes/sec
total size is 782,561,101  speedup is 1,254.31
'''
        self.assertEqual(ctp.proc_rsync_output(txt, 'rsync -av blah /blah1'), set())

        # two output
        ctp = CTPCron()
        txt = '''receiving incremental file list
tptorrent/MTGEBSC64G207464G1/Shared/Common/
/unknown/somedir/Shared/Common/
unknown line
tptorrent/somedir/Shared/Common/

sent 1,951 bytes  received 621,948 bytes  40,251.55 bytes/sec
total size is 782,561,101  speedup is 1,254.31
'''
        self.assertEqual(ctp.proc_rsync_output(txt, 'rsync -av blah /blah1'),
                         {'/blah1/tptorrent/MTGEBSC64G207464G1',
                          '/blah1/tptorrent/somedir'})

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_xfer_rsync(self):
        ctp = CTPCron()
        with MockVar(TTP, 'main', Mock(return_value=['/tp1'])):
            result = ctp.xfer('eseu.py rsync -av machine:/path /tppath/abc', 1)
        self.assertEqual(result, {'/tp1'})

    def test_xfer_local(self):
        ctp = CTPCron()
        with TempDir(name=True) as tdir, TempDir(name=True) as tdir1:
            File(f'{tdir}/TP1').touch()
            File(f'{tdir}/TP2').touch()
            File(f'{tdir1}/TP1').touch()
            ctp.glob_env[1] = '*'
            result = ctp.xfer(f'{tdir1} {tdir}', 1)
            self.assertEqual(result, {f'{tdir}/TP2'})

    def test_get_envfile(self):
        ctp = CTPCron()
        sort = 'EnvironmentFile.env EnvironmentFile_!ENG!.env'.split()
        with TempDir(name=True) as tdir:
            # default, no file found
            self.assertEqual(ctp.get_envfile(tdir, sort), None)
            # normal sort
            File(f'{tdir}/EnvironmentFile.env').touch()
            self.assertEqual(ctp.get_envfile(tdir, sort), 'EnvironmentFile.env')

        with TempDir(name=True) as tdir:
            # normal sort
            File(f'{tdir}/EnvironmentFile_!ENG!.env').touch()
            self.assertEqual(ctp.get_envfile(tdir, sort), 'EnvironmentFile_!ENG!.env')

    def test_istrig(self):
        with TempDir(name=True) as tdir_tp, TempDir(name=True) as tdir_trig:
            ctp = CTPCron()
            ctp.cmds = {1: f'eseu.py rsync -av sortmach:/sortpath/tptorrent {tdir_tp}'}
            ctp.trig_dir = {1: tdir_trig}

            # Write out testprograms
            File(f'{tdir_tp}/tp/MTL10C').touch(mkdir=True, mtime=time.time())
            File(f'{tdir_tp}/tp/MTL10B').touch(mkdir=True, mtime=time.time() - 1000)
            File(f'{tdir_tp}/tp/MTL10A').touch(mkdir=True, mtime=time.time() - 2000)

            # case1 - specific tp
            mkdirs(f'{tdir_trig}/MTL10B')
            File(f'{tdir_trig}/MTL10A').touch()
            result = ctp.is_trig()
            self.assertEqual(dict(result), {1: {f'{tdir_tp}/tp/MTL10B',
                                                f'{tdir_tp}/tp/MTL10A'}})
            self.assertEqual(os.listdir(tdir_trig), [])

            # case2 - latest tp
            File(f'{tdir_trig}/trig').touch()
            result = ctp.is_trig()
            self.assertEqual(dict(result), {1: {f'{tdir_tp}/tp/MTL10C'}})
            self.assertEqual(os.listdir(tdir_trig), [])

            # case3 - no trigger
            result = ctp.is_trig()
            self.assertEqual(result, {})

        with TempDir(name=True) as tdir_tp, TempDir(name=True) as tdir_trig:
            ctp = CTPCron()
            ctp.cmds = {1: f'{tdir_trig} {tdir_tp}'}
            ctp.trig_dir = {1: tdir_trig}

            # Write out testprograms
            File(f'{tdir_tp}/MTL10C').touch(mkdir=True, mtime=time.time())
            File(f'{tdir_tp}/MTL10B').touch(mkdir=True, mtime=time.time() - 1000)
            File(f'{tdir_tp}/MTL10A').touch(mkdir=True, mtime=time.time() - 2000)

            # case2 - latest tp
            File(f'{tdir_trig}/trig').touch()
            result = ctp.is_trig()
            self.assertEqual(dict(result), {1: {f'{tdir_tp}/MTL10C'}})
            self.assertEqual(os.listdir(tdir_trig), [])

    # def test_main(self):
    #     # This unittest must be run outside of trigger time. It should result to nothing
    #     with CaptureStdoutLog() as p:
    #         CTPCron().main(loop=1, nap=0)
    #     self.assertEqual(p.getvalue(), '')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_onerun(self):
        # No env found
        with TempDir(name=True) as tdir:
            def fake_system(slf):
                return 0, """receiving incremental file list

sent 1,951 bytes  received 621,948 bytes  40,251.55 bytes/sec
total size is 782,561,101  speedup is 1,254.31"""

            with MockVar(SystemCall, 'run_outtxt', fake_system):
                self.assertEqual(CTPCron().one_run(1, tdir), 1)

    @unittest.skipIf(*is_ut_option('SKIP_NIGHTLY_BUILD', message='manual run only', neg=False))
    def test_integration_norun(self):
        # Executes full flow, but there should be no new TP to run
        SystemCall.real_run_outtxt = SystemCall.run_outtxt

        def fake_system1(slf):
            if slf.cmd[0] == 'eseu.py':
                return 0, """receiving incremental file list

sent 1,951 bytes  received 621,948 bytes  40,251.55 bytes/sec
total size is 782,561,101  speedup is 1,254.31"""
            else:
                return slf.real_run_outtxt()

        with CaptureStdoutLog() as p,\
                MockVar(OnceADay, '__call__', Mock(return_value=True)),\
                MockVar(SystemCall, 'run_outtxt', fake_system1),\
                MockVar(CTPCron, 'compass_refresh', Mock()), \
                MockVar(CTPCron, 'compass_refresh_presi', Mock()), \
                MockVar(CTPCron, 'json_files', Mock()), \
                MockVar(sys, "argv", "a.py -once".split()):
            CTPCron().main()
        print(p.getvalue())
        self.assertNotIn('tp_plans.py', p.getvalue())

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @unittest.skipIf(*is_ut_option('SKIP_NIGHTLY_BUILD', message='manual run only', neg=False))
    def test_integration(self):
        # Executes full flow, but with latest tp trigger
        ctp = CTPCron()
        File(f'{ctp.trig_dir[1]}/latest_trig').touch()
        SystemCall.real_run_outtxt = SystemCall.run_outtxt

        def fake_system2(slf):
            if slf.cmd[0] == 'eseu.py':
                return 0, """receiving incremental file list

sent 1,951 bytes  received 621,948 bytes  40,251.55 bytes/sec
total size is 782,561,101  speedup is 1,254.31"""
            elif 'tp_plans.py' in ' '.join(slf.cmd):
                return 0, 'Success'
            else:
                return slf.real_run_outtxt()

        with CaptureStdoutLog() as p,\
                MockVar(OnceADay, '__call__', Mock(return_value=True)),\
                MockVar(SystemCall, 'run_outtxt', fake_system2),\
                MockVar(CTPCron, 'json_files', Mock()), \
                MockVar(ctp_cron, 'CALLERBIN', f'{ROOT_ENV}/main/ctp_cron.py'):
            print("======= Start of Run ========")
            ctp.main(loop=1, nap=0)
        print(p.getvalue())
        self.assertIn('tp_plans.py', p.getvalue())


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
