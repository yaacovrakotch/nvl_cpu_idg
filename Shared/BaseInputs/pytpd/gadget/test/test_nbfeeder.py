#!/usr/intel/pkgs/python3/3.6.3a/modules/r1/bin/python3
"""
nbfeeder unittests
This unittest will use the site-specific configuration (and will test if nbfeeder is working or not)
"""
import setenv_unittest     # must be first import for unittests
from os.path import basename, exists
from shutil import rmtree

from gadget.errors import ErrorVep
from gadget.nbfeeder import *
from gadget.ut import unittest, is_ut_option, TestCase
from gadget.gizmo import MockVar, switch, IS_UNIX, IS_WIN
from gadget.files import TempDir, tempname, TempName
from gadget.dictmore import TVPVConfigDict
from unittest.mock import Mock
import gadget.nbfeeder as nbfeeder_base


class Helper(object):
    """
    Various Helper routines for nbfeeder unittest
    """

    def __init__(self):
        self.do_not_delete = False

    def delay_dir(self, dirs):
        """
        Need to delay deletion of temporary dir since nbfeeder is still writing to it
        """
        if self.do_not_delete:
            return

        print("Test is Done. Sleeping before deleting:", dirs)
        for i in range(2):   # 2
            if isdir(dirs):
                time.sleep(2)
                rmtree(dirs, ignore_errors=True)
            else:
                break
#        else:
#            print "Warning: trash dir was not deleted after 10 tries. Contents: %r" % os.listdir(dirs)

    def killfeeder(self, cfgb):
        """
        Kill this feeder
        """
        with TempDir(name=True) as tn:
            obj = NBFeeder(cfg=cfgb)
            obj.logdir = tn
            obj.donedir = tn
            obj._init_exec(start_target=False)
            if obj.get_target() is not None:
                obj.kill_feeder()
                time.sleep(20)

                # confirm it is killed
                if obj.get_target() is not None:
                    raise Exception("Helper.killfeeder(): Cannot kill feeder: %s" % obj.get_target())


class NBFake(NBFeeder):
    """
    Fake system commands for NBFeeder
    This is for a particular nbfeeder version
    """

    def nb_init(self):
        NBFeeder.nb_init(self)

        # Fixed values
        self.host = "plxsodin070"   # Fixed host
        self.user = "utuser_" + USERNAME
        self.cfg.nbpatch = "nbflow_2.0.0_build_0200_00_cp31.jar"

    def _system(self, args, which, retall=False, logit=True):
        case = {}
        case['check_nbq()'] = self.sys_check_nbq
        case['start_target()'] = self.sys_start_target
        case['get_target()'] = self.sys_get_target
        case['kill_feeder()'] = self.sys_kill_feeder
        case['remove_jobs()'] = self.sys_remove_jobs
        case['launch()'] = self.sys_launch
        case['status()'] = self.sys_status
        case['nbqstat()'] = self.sys_nbqstat

        action = switch(which, case)
        if action is None:
            raise Exception("which=%s is not defined in NBFake")

        return self._retall(retall, 0, action(), "")

    def sys_nbqstat(self):
        return '''
[pdxnbm043]
                        NetBatch QUEUE status - pool linux1

                 Matbatch v8.1.0_0463_08 on since: Wed Jul 31 07:09:57 2013
                      Time now: Thu Aug 29 08:16:49 2013

------------------------------------------------------------------------------------------------
State   JobID Class        Slot           User       Command                      Jobname/Server
------------------------------------------------------------------------------------------------
Wait     1301261600  SLES_EM> 528             bjslecht g /p/dpg/arch/bin/do_indigo_exp -ve
Wait     1301261600  SLES_EM> 528             bjslecht g /p/dpg/arch/bin/do_indigo_exp -ve
-------------------------------------------------------------------------------------------------
Run      28871303  SLES_EM> 26              mdechene g /nfs/site/proj/dpg/arch/bin/do_wi plxc5939
Send     28872951  SLES_EM> 26              mdechene g /nfs/site/proj/dpg/arch/bin/do_wi plxc5934
Run      28874227  SLES_EM> 26              mdechene g /nfs/site/proj/dpg/arch/bin/do_wi plxc5788
Run      28874227  SLES_EM> 26              mdechene g /nfs/site/proj/dpg/arch/bin/do_wi plxc5788
-------------------------------------------------------------------------------------------------
                     Number of jobs in WAITING queue: 1
                          Number of RUNNING jobs: 10

'''

    def sys_check_nbq(self):
        return '''
Your job has been queued (JobID 119413520, Class EXPR, Queue Slot 1017)
  +pdx_vp.119413520 (removed successfully)
'''

    def sys_start_target(self):
        return '''
Starting nbfeeder (2.0.0_0200_00_cp31_r93761_d2012-04-23) ...
Log file will be written to: /tmp/jqdelosr/nbfeeder_vep2_UNITTEST/nbflow_2.0.0_build_0200_00_cp31.jar/logs/nbfeeder.plxsodin070.log
Feeder name is: jqdelosr_plxsodin070_1768367196
nbfeeder is running on port 54992
'''

    def sys_get_target(self):
        return '''
plxwpdelnas002:54391  [crashed]         pid:9090    /tmp/jqdelosr/nbfeeder_for_vcf jqdelosr_plxwpdelnas002_1257392747 N/A
  plxc6850:47480   [crashed]         pid:12889   /tmp/jqdelosr/nbfeeder_for_vcf jqdelosr_plxc6850_1388359542 N/A
  plxc6023:40314   [alive]         pid:26487   /tmp/utuser_{uname}/nbfeeder_vep2/mypatch111 jqdelosr_plxc6025_1424062934 hsw_vcf
  plxsodin070:36737  [alive]           pid:19758   /tmp/utuser_{uname}/nbfeeder_vep2/nbflow_2.0.0_build_0200_00_cp31.jar jqdelosr_plxsodin070_1898067539 hsw_vcf
  plxc5910:36461   [alive]           pid:2741    /nfs/pdx/disks/nehalem.pde.32/hswtrash/trash/nbfeeder/jqdelosr/nbfeeder_vep2/nbflow_2.0.0_build_0200_00_cp31.jar jqdelosr_plx
'''.format(uname=USERNAME)

    def sys_kill_feeder(self):
        return '''
No useful output
'''

    def sys_remove_jobs(self):
        return '''
No useful output
'''

    def sys_launch(self):
        return '''
Your task has been queued (TaskID: 132, Name: launcher1377728795.158499.1)
'''

    def sys_status(self):
        return '''
Status,Jobid,TimesRestarted,Wtime,ExitStatus,Delegate,RemoteServerHostName
Wait,405,0,,,false,
Wait,406,0,,,false,
Wait,407,0,,,false,
'''


class FuncTest(TestCase):
    """
    Small function (which are independent) unit tests
    """

    def test_template(self):
        obj = NBFeeder()
        obj.cfg.timeout = "p11"
        obj.cfg.nbpatch = "{timeout}"

        obj = NBFeeder(maincfg=obj.cfg)
        obj.user = "jqdelosr"
        self.assertEqual(obj._template("/tmp/{user}/nbfeeder_vep2/{nbpatch}"), "/tmp/jqdelosr/nbfeeder_vep2/p11")

    def test_config_ok_to_change(self):
        obj = NBFeeder()
        orig = obj.cfg.retry
        obj.cfg['retry'] = 10
        self.assertNotEqual(obj.cfg.retry, orig)
        obj = NBFeeder()
        self.assertEqual(obj.cfg.retry, orig)

    @unittest.skipIf(IS_WIN, 'unix only to check /proc/cpuinfo')
    def test_is_xhost(self):
        obj = NBFeeder()

        with MockVar(nbfeeder_base, "is_vnc_machine", Mock(return_value=False)):
            # megafeeder True
            with MockVar(obj.cfg, "megafeeder", False, isdict=True):
                obj.host = obj.cfg.centralhost
                self.assertFalse(obj._is_xhost(), "Random machine %s is xhost. Must not be xhost." % obj.host)

            # megafeeder False
            with MockVar(obj.cfg, "megafeeder", True, isdict=True):
                obj.host = obj.cfg.centralhost
                self.assertTrue(obj._is_xhost(), "Must be True with megafeeder=True")

            # memory test
            with MockVar(obj.cfg, "megafeeder", False, isdict=True):
                obj.host = obj.cfg.centralhost
                self.assertFalse(obj._is_xhost(), "Random machine %s is xhost. Must not be xhost." % obj.host)

                with MockVar(obj.cfg, "mach_min_memory", 1000, isdict=True):
                    self.assertTrue(obj._is_xhost(), "minimum machine memory check")

        # vnc test
        with MockVar(nbfeeder_base, "is_vnc_machine", Mock(return_value=True)):
            self.assertTrue(obj._is_xhost(), "vnc machine")

    def test_config_override(self):
        obj = NBFeeder()
        dd = DictDot()
        dd.abc = 123
        dd.ghi = 456
        obj._config_override(dd, {'abc': 999})
        self.assertEqual(dd, {'abc': 999, 'ghi': 456})

        self.assertRaises(ErrorInput, obj._config_override, dd, {'abcq': 999})

    def test_is_queue_full(self):

        class UTFull(NBFeeder):
            def _system(self, args, which, retall=False):
                res = '''
                  Matbatch v8.1.0_0463_08 on since: Wed Jul 31 07:09:57 2013
                      Time now: Mon Aug 26 15:22:26 2013

------------------------------------------------------------------------------------------------
State   JobID Class        Slot           User       Command                      Jobname/Server
------------------------------------------------------------------------------------------------
Wait     1300959808  SLES10_> 5201            wquek1   trex scu/gpio/glitch_filter:pin_93
Wait     1300963520  SLES10_> 5201            jgoo1    trex ilb/ilb_hpet_irq_routing_ioapi
Wait     1300987929  SLES10_> 5201            wquek1   trex scu/gpio/gpio_multi_pin:seed_1
Wait     1300993217  SLES10_> 5201            wquek1   trex scu/gpio/wake_scu:pin_50 -m ac
Wait     1300958088  SLES10_> 5202            ywong10  trex scu/reg_access/scu_gpio_reg_ac
Wait     1300988601  SLES10_> 5227            htan31   trex iosf/sb_dn_mbb -m acerun -ace_
-------------------------------------------------------------------------------------------------
Run      322478883  SLES10_> #6496           ttle2    xsiteenv /p/cse/asic/datools/pkgs/R plxc5924
Run      322479372  SLES10_> #6496           ttle2    xsiteenv /p/cse/asic/datools/pkgs/R plxc25856
Run      322487556  SLES10_> #6496           ttle2    xsiteenv /p/cse/asic/datools/pkgs/R plxc0587
'''
                return self._retall(retall, 1, res, "")

        class UTNotFull(NBFeeder):
            def _system(self, args, which, retall=False):
                res = '''
[pdxnbm043]
                        NetBatch QUEUE status - pool linux1

                 Matbatch v8.1.0_0463_08 on since: Wed Jul 31 07:09:57 2013
                      Time now: Mon Aug 26 15:24:00 2013

------------------------------------------------------------------------------------------------
State   JobID Class        Slot           User       Command                      Jobname/Server
------------------------------------------------------------------------------------------------
                           WAITING queue is empty.
                           No job is RUNNING now.
'''
                return self._retall(retall, 1, res, "")

        # pass case
        obj = UTFull()
        obj.final_pool = "a"
        obj.final_qslot = "b"
        self.assertTrue(obj.is_queue_full(), "Queue must be full")

        # fail case
        obj = UTNotFull()
        obj.final_pool = "a"
        obj.final_qslot = "b"
        self.assertTrue(not obj.is_queue_full(), "Queue must be not full")

    def test_all_nbpool_exec(self):

        # old syntax using cfg.config
        cfgb = TVPVConfigDict()
        cfgb.config.default.qslot = 1
        cfgb.config.low.qslot = 2
        cfgb.config.med.qslot = 3
        cfgb.config.high.qslot = 1
        self.assertEqual(NBFeeder.all_nbpool(cfgb), None)

        # new syntax using cfg.nbpool
        cfgb.nbpool.default1.qslot = 1
        cfgb.nbpool.low1.qslot = 2
        cfgb.nbpool.med1.qslot = 3
        cfgb.nbpool.high1.qslot = 1
        self.assertEqual(set(NBFeeder.all_nbpool(cfgb)), set("default1 low1 med1 high1".split()))

    def test_get_nbpoolcfg(self):
        cfgb = TVPVConfigDict()
        # old method
        self.assertEqual(NBFeeder._get_nbpoolcfg(cfgb), '')

        # new method
        cfgb.nbpool.vcf.pool = 'something'
        cfgb.nbpool.fast.pool = 'something2'
        cfgb.nbpool_default = 'vcf'

        # default
        self.assertEqual(NBFeeder._get_nbpoolcfg(cfgb), 'vcf')

        # -nbpool fast
        with MockVar(OPT, "nbpool", "fast"):
            self.assertEqual(NBFeeder._get_nbpoolcfg(cfgb), 'fast')

    def test_timeout(self):
        # Default options
        obj = NBFeeder()
        self.assertEqual(obj.timeout, "48h")
        self.assertEqual(obj.softime, "48h")

        # with VR2, cfg.vr2.timeout
        with MockVar(OPT, "replay", True):
            obj1 = NBFeeder()
            self.assertEqual(obj1.timeout, "120h")
            self.assertEqual(obj1.softime, "120h")

        # default, cfg.timeout
        with MockVar(OPT, "replay", None):
            obj2 = NBFeeder()
            self.assertEqual(obj2.timeout, "48h")
            self.assertEqual(obj2.softime, "48h")

        # with OPT.timeout in vcf cmd
        with MockVar(OPT, "timeout", "199"):
            obj3 = NBFeeder()
            self.assertEqual(obj3.timeout, "199h")
            self.assertEqual(obj3.softime, "199h")

        # with OPT.timeout in vcf cmd and VR2
        with MockVar(OPT, "timeout", "88"), MockVar(OPT, "vr2opts", {"vrev": "vrevAA1"}):
            obj4 = NBFeeder()
            self.assertEqual(obj4.timeout, "88h")
            self.assertEqual(obj4.softime, "88h")

        # with OPT.timeout in vcf cmd and VR2
        with MockVar(OPT, "vr2opts", {"vrev": "vrevAA1"}), MockVar(OPT, "timeout", "66"):
            obj5 = NBFeeder()
            self.assertEqual(obj5.timeout, "66h")
            self.assertEqual(obj5.softime, "66h")

    def test_get_nbclass(self):

        # Setup the config
        cfgb = TVPVConfigDict()
        cfgb.config.AA.min_mem = 0
        cfgb.config.AA.max_mem = 4
        cfgb.config.BB.min_mem = 5
        cfgb.config.BB.max_mem = 16
        cfgb.config.CC.min_mem = 17
        cfgb.config.CC.max_mem = 200
        cfgb.config.Z1.min_mem = 17
        cfgb.config.Z2.somevar = 'a'
        cfgb.config.NBCLASSQ.min_mem = 400
        cfgb.AUTO_OFF()

        # with MockVar(OPT, "nbclass", "NBCLASSQ"):
        #     self.assertEqual(NBFeeder.get_nbclass(4, cfgb), "NBCLASSQ")

        self.assertEqual(NBFeeder.get_nbclass(1, cfgb), 'AA')
        self.assertEqual(NBFeeder.get_nbclass(4, cfgb), 'AA')
        self.assertEqual(NBFeeder.get_nbclass(5, cfgb), 'BB')
        self.assertEqual(NBFeeder.get_nbclass(15, cfgb), 'BB')
        self.assertEqual(NBFeeder.get_nbclass(16, cfgb), 'BB')
        self.assertEqual(NBFeeder.get_nbclass(17, cfgb), 'CC')
        self.assertEqual(NBFeeder.get_nbclass(18, cfgb), 'CC')
        self.assertEqual(NBFeeder.get_nbclass(199, cfgb), 'CC')
        self.assertEqual(NBFeeder.get_nbclass(200, cfgb), 'CC')
        self.assertRaises(ErrorEnv, NBFeeder.get_nbclass, 201, cfgb)

        # ===================================================
        # New methodology
        cfgb = TVPVConfigDict()
        cfgb.nbpool_default = 'default'
        cfgb.nbpool.default.pool = 'testpool'
        cfgb.nbpool.default.classos = 'sles11'
        cfgb.nbpool.default.valid_memclass = 'AA BB CC Z1 Z2 NBCLASSQ'.split()

        cfgb.memclassmap.AA.sles_any = 'SLES&&2G'
        cfgb.memclassmap.BB.sles_any = 'SLES&&2G'
        cfgb.memclassmap.CC.sles_any = 'SLES&&2G'
        cfgb.memclassmap.Z1.sles_any = 'SLES&&2G'
        cfgb.memclassmap.Z2.sles_any = 'SLES&&2G'
        cfgb.memclassmap.NBCLASSQ.sles_any = 'SLES&&2G'

        cfgb.memclass.AA.min_mem = 0
        cfgb.memclass.AA.max_mem = 4
        cfgb.memclass.BB.min_mem = 5
        cfgb.memclass.BB.max_mem = 16
        cfgb.memclass.CC.min_mem = 17
        cfgb.memclass.CC.max_mem = 200
        cfgb.memclass.Z1.min_mem = 17
        cfgb.memclass.Z2.somevar = 'a'
        cfgb.memclass.NBCLASSQ.min_mem = 400
        cfgb.AUTO_OFF()
        cfgc = DictDot(NBFeeder._vepdefault(cfgb))

        with MockVar(OPT, "nbclass", "NBCLASSQ"):
            self.assertEqual(NBFeeder.get_nbclass(4, cfgc), "default_NBCLASSQ")

    def test_cleanups(self):
        with TempDir(name=True) as tdir:
            mkdirs(join(tdir, "task/somelaunch/delegates"))
            obj = NBFeeder()
            obj.logdir = tdir
            with MockVar(nbfeeder_base, "File", Mock()) as m:
                obj._cleanups()
                m.assert_any_call(join(tdir, "task", "somelaunch"))
                m.assert_any_call(join(tdir, "task", "somelaunch", "delegates"))
                self.assertEqual(len(m.call_args_list), 2)

    def test_get_host(self):
        obj = NBFeeder()
        # fail case
        with MockVar(obj.cfg, "centralhost", None), \
                MockVar(obj, "_is_xhost", Mock(return_value=True)):
            self.assertRaisesRegex(ErrorConfig, 'Cannot launch', obj._get_host)

        # local case
        with MockVar(obj, "_is_xhost", Mock(return_value=False)):
            self.assertTrue(obj._get_host()[1].startswith('/tmp'))

    def test_is_raw_nbclass(self):
        self.assertFalse(NBFeeder.is_raw_nbclass(None))
        self.assertFalse(NBFeeder.is_raw_nbclass('mem32g'))
        self.assertFalse(NBFeeder.is_raw_nbclass('mem32g6c'))
        self.assertTrue(NBFeeder.is_raw_nbclass('SLES12&&32G'))
        self.assertTrue(NBFeeder.is_raw_nbclass('SLES11_EMT64_32G'))

    def test_add_job(self):
        """
        Unittests for function add_job, which adds a new job to the task
        """
        with TempDir(name=True) as tdir:
            obj = NBTask(taskdir=tdir)

            # case 1: jobsfile exists, expected result = ErrorVep
            obj._jobsfile = "jobsfile"
            self.assertRaises(ErrorVep, obj.add_job, "ls", "mytag1")

            # case 2: jobsfile does not exist, job with same tag already added to task
            obj._jobsfile = None
            obj._jobs_dict = ["mytag1"]
            self.assertRaises(ErrorInput, obj.add_job, "ls", "mytag1")

    def test_set_nbinfo(self):
        """
        Unittests for function _set_nbinfo, which checks the validity of nbclass
        """
        # case 1 - -user_*
        with MockVar(NBFeeder, "_get_nbclasscfg", Mock(return_value="myclass")),\
                MockVar(NBFeeder, "__init__", Mock(return_value=None)):
            nb = NBFeeder()
            # These are usually set in the init that is being mocked
            nb.nbpool = None
            nb.nbqslot = None
            nb.nbclass = None
            nb.cfg = DictDot()
            nb.cfg.memclass = "2G"
            nb.cfg.config = {"myclass": DictDot({"pool": "swim", "qslot": "w", "classname": "normal", "machine_count": "2"})}

            with MockVar(OPT, "user_nbpool", "pdx_normal"),\
                    MockVar(OPT, "user_nbclass", "myclass"),\
                    MockVar(OPT, "user_nbqslot", "/mdo/tvpv/sles11"):
                nb._set_nbinfo("normal", 0.1)

                self.assertEqual(nb.nbclass, "myclass")
                self.assertEqual(nb.final_pool, "pdx_normal")
                self.assertEqual(nb.final_classname, "myclass")
                self.assertEqual(nb.final_machcnt, "2")
                self.assertEqual(nb.final_qslot, "/mdo/tvpv/sles11")

        # case 2 - -use_nb_env
        with MockVar(NBFeeder, "_get_nbclasscfg", Mock(return_value="env_class")),\
                MockVar(NBFeeder, "__init__", Mock(return_value=None)):
            nb2 = NBFeeder()
            # These are usually set in the init that is being mocked
            nb2.nbpool = None
            nb2.nbqslot = None
            nb2.nbclass = None
            nb2.cfg = DictDot()
            nb2.cfg.config = {"env_class": DictDot({"pool": "swim", "qslot": "w", "classname": "normal", "machine_count": "2"})}

            with MockVar(os.environ, "NBPOOL", "env_pool"), \
                    MockVar(os.environ, "NBCLASS", "env_class"), \
                    MockVar(os.environ, "NBQSLOT", "env_qslot"),\
                    MockVar(OPT, "use_nb_env", True),\
                    MockVar(OPT, "tid", "123456"):  # so is_oneclick returns True
                nb2._set_nbinfo("normal_e", 0.1)

                self.assertEqual(nb2.nbclass, "env_class")
                self.assertEqual(nb2.final_pool, "env_pool")
                self.assertEqual(nb2.final_classname, "env_class")
                self.assertEqual(nb2.final_machcnt, "2")
                self.assertEqual(nb2.final_qslot, "env_qslot")

        # case 3 - -user_*, with -timeout
        with MockVar(NBFeeder, "_get_nbclasscfg", Mock(return_value="myclass")),\
                MockVar(NBFeeder, "__init__", Mock(return_value=None)),\
                MockVar(OPT, "timeout", "24"):
            nb3 = NBFeeder()
            # These are usually set in the init that is being mocked
            nb3.nbpool = None
            nb3.nbqslot = None
            nb3.nbclass = None

            nb3.cfg = DictDot()
            nb3.cfg.memclass = "2G"
            nb3.cfg.timeout = "40"
            nb3.cfg.softime = "12"
            nb3.cfg.config = {"myclass": DictDot({"pool": "swim", "qslot": "w", "classname": "normal", "machine_count": "2"})}

            with MockVar(OPT, "user_nbpool", "pdx_normal"),\
                    MockVar(OPT, "user_nbclass", "myclass"),\
                    MockVar(OPT, "user_nbqslot", "/mdo/tvpv/sles11"):
                nb3._set_nbinfo("normal", None)

                self.assertEqual(nb3.nbclass, "myclass")
                self.assertEqual(nb3.final_pool, "pdx_normal")
                self.assertEqual(nb3.final_classname, "myclass")
                self.assertEqual(nb3.final_machcnt, "2")
                self.assertEqual(nb3.final_qslot, "/mdo/tvpv/sles11")
                self.assertEqual(nb3.timeout, "24h")
                self.assertEqual(nb3.softime, "24h")

        # case 3a - timeout default
        with MockVar(NBFeeder, "_get_nbclasscfg", Mock(return_value="myclass")),\
                MockVar(NBFeeder, "__init__", Mock(return_value=None)):
            nb3 = NBFeeder()
            # These are usually set in the init that is being mocked
            nb3.nbpool = None
            nb3.nbqslot = None
            nb3.nbclass = None
            nb3.cfg = DictDot()
            nb3.cfg.memclass = "2G"
            nb3.cfg.timeout = "40h"
            nb3.cfg.softime = "12h"
            nb3.cfg.config = {"myclass": DictDot({"pool": "swim", "qslot": "w", "classname": "normal", "machine_count": "2"})}

            nb3._set_nbinfo("normal", None)
            self.assertEqual(nb3.timeout, "40h")
            self.assertEqual(nb3.softime, "12h")

        # case 4 - -user_* - replay with vr2_timeout
        with MockVar(NBFeeder, "_get_nbclasscfg", Mock(return_value="myclass")),\
                MockVar(NBFeeder, "__init__", Mock(return_value=None)),\
                MockVar(OPT, "replay", True):
            nb4 = NBFeeder()
            # These are usually set in the init that is being mocked
            nb4.nbpool = None
            nb4.nbqslot = None
            nb4.nbclass = None
            nb4.cfg = DictDot()
            nb4.cfg.memclass = "2G"
            nb4.cfg.timeout = "40"
            nb4.cfg.softime = "12"
            nb4.cfg.vr2_timeout = "22h"
            nb4.cfg.vr2_softime = "53h"
            nb4.cfg.config = {"myclass": DictDot({"pool": "swim", "qslot": "w", "classname": "normal", "machine_count": "2"})}

            with MockVar(OPT, "user_nbpool", "pdx_normal"),\
                    MockVar(OPT, "user_nbclass", "myclass"),\
                    MockVar(OPT, "user_nbqslot", "/mdo/tvpv/sles11"):
                nb4._set_nbinfo("normal", None)

                self.assertEqual(nb4.nbclass, "myclass")
                self.assertEqual(nb4.final_pool, "pdx_normal")
                self.assertEqual(nb4.final_classname, "myclass")
                self.assertEqual(nb4.final_machcnt, "2")
                self.assertEqual(nb4.final_qslot, "/mdo/tvpv/sles11")
                self.assertEqual(nb4.timeout, "22h")
                self.assertEqual(nb4.softime, "53h")

        # case 4a - -user_* - replay without vr2_timeout
        with MockVar(NBFeeder, "_get_nbclasscfg", Mock(return_value="mem4g_myclass")),\
                MockVar(NBFeeder, "__init__", Mock(return_value=None)),\
                MockVar(OPT, "replay", True):
            nb4 = NBFeeder()
            # These are usually set in the init that is being mocked
            nb4.nbpool = None
            nb4.nbqslot = None
            nb4.nbclass = None
            nb4.cfg = DictDot()
            nb4.cfg.memclass = "2G"
            nb4.cfg.timeout = "40h"
            nb4.cfg.softime = "12h"
            nb4.cfg.config = {"mem4g_myclass": DictDot({"pool": "swim", "qslot": "w", "classname": "normal",
                                                        "machine_count": "2"})}

            with MockVar(OPT, "user_nbpool", "pdx_normal"),\
                    MockVar(OPT, "user_nbclass", "mem4g_myclass"),\
                    MockVar(OPT, "user_nbqslot", "/mdo/tvpv/sles11"):
                nb4._set_nbinfo("normal", None)

                self.assertEqual(nb4.final_pool, "pdx_normal")
                self.assertEqual(nb4.final_classname, "mem4g_myclass")
                self.assertEqual(nb4.final_machcnt, "2")
                self.assertEqual(nb4.final_qslot, "/mdo/tvpv/sles11")
                self.assertEqual(nb4.timeout, "40h")
                self.assertEqual(nb4.softime, "12h")

        # case 5 - normal run
        with MockVar(NBFeeder, "_get_nbclasscfg", Mock(return_value="mem4g_env")),\
                MockVar(NBFeeder, "__init__", Mock(return_value=None)):
            nb2 = NBFeeder()
            # These are usually set in the init that is being mocked
            nb2.nbpool = None
            nb2.nbqslot = None
            nb2.nbclass = None
            nb2.cfg = DictDot()
            nb2.cfg.config = {"mem4g_env": DictDot({"pool": "swimming",
                                                    "qslot": "W",
                                                    "classname": "first",
                                                    "machine_count": "2"})}

            with MockVar(os.environ, "NBPOOL", "unused1"), \
                    MockVar(os.environ, "NBCLASS", "unused2"), \
                    MockVar(os.environ, "NBQSLOT", "unused3"):  # os.environ here *SHOULD* not be used
                nb2._set_nbinfo("mem4g_env", 0.1)

                self.assertEqual(nb2.nbclass, "mem4g_env")
                self.assertEqual(nb2.final_pool, "swimming")
                self.assertEqual(nb2.final_classname, "first")
                self.assertEqual(nb2.final_machcnt, "2")
                self.assertEqual(nb2.final_qslot, "W")

        # case 7 - fail case1
        nb2 = NBFeeder()
        # These are usually set in the init that is being mocked
        with MockVar(os.environ, "NBPOOL", MockVar.delete),\
                MockVar(OPT, "use_nb_env", True):
            with self.assertRaisesRegex(ErrorUser, 'is not set in environment'):
                nb2._set_nbinfo("vcf_mem4g", 0.1)

        # case 9 - fail - both options
        nb2 = NBFeeder()
        with MockVar(OPT, "use_nb_env", True),\
                MockVar(OPT, "user_nbpool", "swimming"):
            with self.assertRaisesRegex(ErrorUser, 'cannot be used together with'):
                nb2._set_nbinfo("vcf_mem4g", 0.1)


class NBTest(TestCase):
    """Unit tests for NBFeeder - Does not submit jobs"""

    @unittest.skipIf(IS_WIN, 'unix only to check /proc/cpuinfo')
    def test_move_files_logdir(self):
        with TempDir(name=True, chdir=True) as tn:
            File("somefile").touch()
            File("prevfiles.123").touch()

            obj = NBFake(tn)
            self.assertTrue(exists("prevfiles.123"), "Should not be moved")
            self.assertTrue(not exists("somefile"), "Should be moved")

    def test_check_nbclass(self):
        self.assertRaises(ErrorInput, NBFeeder, logdir="/tmp", nbclass="mem32g_some_bad_class")

    @unittest.skipIf(IS_WIN, 'tools only for UNIX')
    def test_config_check(self):
        # pass case
        obj = NBFeeder()
        NBFeeder.check_config(obj.cfg)

        # fail on template
        obj = NBFeeder()
        obj.cfg.dlgfile = "{unknown} key"
        self.assertRaises(KeyError, NBFeeder.check_config, obj.cfg)

        # fail on existence
        obj = NBFeeder()
        obj.cfg.cmd_check_nbq = "/tmp/sure_NOT_exist_file key"
        self.assertRaisesRegex(ErrorConfig, "does not exist", NBFeeder.check_config, obj.cfg)

        # missing default nbclass
        obj = NBFeeder()
        # new nethodology using cfg.nbpool and cfg.memclass skips this check
        if not ('nbpool_default' in cfg and 'memclass_default' in cfg):
            class UTN2(NBFeeder):
                @classmethod
                def _default_nbclass(cls, nbclass_default=None):
                    return "NOTEXIST"
            self.assertRaisesRegex(ErrorConfig, "NOTEXIST", UTN2.check_config, obj.cfg)

    def test_get_target(self):
        # passcase
        obj = NBFake()
        obj.cfg.workarea_subpath = 'mypatch111'
        obj.nbhost = "plxc6023"
        self.assertEqual(obj.get_target(), "plxc6023:40314")

        # failcase
        obj = NBFake()
        obj.cfg.workarea_subpath = 'mypatch111'
        obj.nbhost = "somemachine"
        self.assertEqual(obj.get_target(), None)

    @unittest.skipIf(IS_WIN, 'unix only to check /proc/cpuinfo')
    def test_new_target(self):
        class UT1(NBFake):
            def sys_get_target(self):
                if not hasattr(self, "count1"):
                    self.count1 = 0
                self.count1 += 1

                if self.count1 <= 4:
                    return '''
plxwpdelnas002:54391  [crashed]         pid:9090    /tmp/jqdelosr/nbfeeder_for_vcf jqdelosr_plxwpdelnas002_1257392747 N/A
  plxc6850:47480   [crashed]         pid:12889   /tmp/jqdelosr/nbfeeder_for_vcf jqdelosr_plxc6850_1388359542 N/A
  plxc6023:40314   [alive]         pid:26487   /tmp/utuser_{uname}/nbfeeder_vep2/mypatch111 jqdelosr_plxc6025_1424062934 hsw_vcf
  plxsodin070:36737  [alive]           pid:19758   /tmp/jqdelosr/nbfeeder_vep2/nbflow_2.0.0_build_0200_00_cp31.jar jqdelosr_plxsodin070_1898067539 hsw_vcf
  plxc5910:36461   [alive]           pid:2741    /nfs/pdx/disks/nehalem.pde.32/hswtrash/trash/nbfeeder/jqdelosr/nbfeeder_vep2/nbflow_2.0.0_build_0200_00_cp31.jar jqdelosr_plx
'''.format(uname=USERNAME)

                else:
                    return '''
plxwpdelnas002:54391  [crashed]         pid:9090    /tmp/jqdelosr/nbfeeder_for_vcf jqdelosr_plxwpdelnas002_1257392747 N/A
  plxc6850:47480   [crashed]         pid:12889   /tmp/jqdelosr/nbfeeder_for_vcf jqdelosr_plxc6850_1388359542 N/A
  plxc6023a:40314   [alive]         pid:26487   /tmp/utuser_{uname}/nbfeeder_vep2/mypatch111 jqdelosr_plxc6025_1424062934 hsw_vcf
  plxsodin070:36737  [alive]           pid:19758   /tmp/utuser_{uname}/nbfeeder_vep2/nbflow_2.0.0_build_0200_00_cp31.jar jqdelosr_plxsodin070_1898067539 hsw_vcf
  plxc5910:36461   [alive]           pid:2741    /nfs/pdx/disks/nehalem.pde.32/hswtrash/trash/nbfeeder/jqdelosr/nbfeeder_vep2/nbflow_2.0.0_build_0200_00_cp31.jar jqdelosr_plx
'''.format(uname=USERNAME)

        # new target case
        with TempDir(name=True) as tn:
            obj = UT1(tn)
            obj.cfg.workarea_subpath = 'mypatch111'
            obj.nbhost = "plxc6023a"
            obj._start_target(sleep=0)

    def test_check_nbq0(self):
        obj = NBFeeder()

        # fail case (need Mockvar since obj.cfg is a dictionary reference
        with MockVar(obj.cfg, "regex_nb_alive", "TEXTNOTEXT", isdict=True):
            self.assertRaises(ErrorEnv, obj._check_nbq)

        # pass case
        obj._check_nbq()

    def test_check_nbq1(self):
        """
        Make sure fail to remove test job raises an exception
        """
        class UT2_status(NBFeeder):
            def __init__(self):
                NBFeeder.__init__(self)
                self.taskid = set(['1'])
                self.logdir = '/tmp/path'
                self.jobdb = {}

            def _system(self, cmd, which=None, retall=False):
                if regex("nbjob remove", cmd):
                    res = "Failed to remove job"
                    print("\n res %s, cmd %s" % (res, cmd))
                    return self._retall(True, 1, res, "")
                else:
                    res = "Your job has been queued (JobID 12345, "
                    print("\n res %s, cmd %s" % (res, cmd))
                    return self._retall(True, 0, res, "")

        obj = UT2_status()
        self.assertRaises(ErrorEnv, obj._check_nbq)

        # pass case
        obj._check_nbq()

    def test_nbstatus(self):
        class UT1_status(NBFeeder):
            def __init__(self):
                NBFeeder.__init__(self)
                self.taskid = set(['1'])
                self.logdir = '/tmp/path'
                self.jobdb = {}
                for i in range(1, 11):  # 10 jobs
                    self.jobdb[i] = DictDot()

            def _update_jobdb(self, ff):
                # Get the hash_dig from the filename. This is the unique cmdline.
                ff_split = basename(ff).split('.')
                if len(ff_split) >= 3:
                    hcmd = ff_split[1]
                if hcmd == '0002':
                    return(hcmd, -4)
                else:
                    return(hcmd, 0)

            def _system(self, args, which, retall=False, logit=False):
                res = 'Status,Jobid,TimesRestarted,Wtime,ExitStatus,delegate,JobLogFile\n'
                res += 'Comp,46,0,1.0,0,false,/tmp/path/log.0000.logfile1.1\n'
                res += 'Comp,47,0,1.0,0,false,/tmp/path/log.0001.logfile1.1\n'
                res += 'Comp,48,3,,-4,false,/tmp/path/log.0002.logfile1.1\n'
                res += 'Wait,49,0,240.0,0,false,\n'
                res += 'Wait,50,0,240.0,,false,\n'
                res += 'Wait,51,0,240.0,,false,\n'
                res += 'Run,52,0,240.0,0,false,/tmp/path/log.0003.logfile1.1\n'
                res += 'Run,53,0,240.0,0,false,/tmp/path/log.0004.logfile1.1\n'
                res += 'Run,54,0,240.0,0,false,/tmp/path/log.0005.logfile1.1\n'
                res += 'Run,55,0,240.0,0,false,/tmp/path/log.0006.logfile1.1\n'

                return self._retall(retall, 1, res, "")

        obj = UT1_status()
        self.assertEqual(obj._nbstatus(), {'fail': 1, 'run': 4, 'total': 10, 'good': 2, 'wait': 3})

    def test_readlog(self):
        """
        Test readlog()
        """
        obj = NBFeeder()
        with TempDir(chdir=True) as tdir:

            # Empty file case
            tn = "log.123444.1"
            open(tn, "w").write('''
            ''')
            self.assertEqual(obj._readlog(tn), ("123444", None, None))

            # No file exists case
            tm = "log.183444.1"
            self.assertRaises(Exception, obj._readlog(tm))

            # Unfinished case
            open(tn, "w").write('''
+-----------------------------------------------------------------------------+
| Logfile        : log.3.1377210415.817626.3                                  |
| Job id         : 138                        Class: EXECUTED_BY_DELEGATE Qslot: /25  |
| Executed on    : plxc9488.pdx.intel.com:50994 Pool : jqdelosr_plxsodin070_1208882641|
| Queueing time  : Thu Aug 22 15:26:55 2013                                   |
| Starting time  : Thu Aug 22 15:27:22 2013          Qwait:   0h:00m:27s      |
| Command        : cd false                                                   |
+-----------------------------------------------------------------------------+
            ''')
            self.assertEqual(obj._readlog(tn), ("123444", "plxc9488.pdx.intel.com:50994", None))

            # Passing Case
            open(tn, "w").write('''
+-----------------------------------------------------------------------------+
| Logfile        : log.3.1377210415.817626.3                                  |
| Job id         : 138                        Class: EXECUTED_BY_DELEGATE Qslot: /25  |
| Executed on    : plxc9488.pdx.intel.com:50994 Pool : jqdelosr_plxsodin070_1208882641|
| Queueing time  : Thu Aug 22 15:26:55 2013                                   |
| Starting time  : Thu Aug 22 15:27:22 2013          Qwait:   0h:00m:27s      |
| Command        : make_pattern.py -fullpath /p/pde/tvpv                      |
+-----------------------------------------------------------------------------+
CMD:        /p/pde/tvpv/tgl/vep2/rel/TGL/bin/make_pattern.py -fullpath
make_pattern STATUS: PASS
+-----------------------------------------------------------------------------+
| Exit Status    : 0                                                         |
NB: Job execution passed on remote machine
| Finishing time : Thu Aug 22 15:27:22 2013                                   |
| CPU time       : Usr 0.0s    Sys 0.0s    WC  0h:00m:00s                     |
| Rusage Stats   : Mem:0      PF:  0/0       CSv/f:  0/0     Swaps:0          |
|                :           Msg:    0/0     IOops:  0/0     Sigs :0          |
+-----------------------------------------------------------------------------+
            ''')
            self.assertEqual(obj._readlog(tn), ("123444", "plxc9488.pdx.intel.com:50994", 0))

            # Passing Case, sequential job
            open(tn, "w").write('''
CMD:        /p/pde/tvpv/tgl/vep2/rel/TGL/bin/make_pattern.py -fullpath
MACHINE:    plxcfe004 Uptime
make_pattern STATUS: PASS
            ''')
            self.assertEqual(obj._readlog(tn), ("123444", "plxcfe004", 0))

            # Passing Case with stacktrace
            open(tn, "w").write('''
+-----------------------------------------------------------------------------+
| Logfile        : log.3.1377210415.817626.3                                  |
| Job id         : 138                        Class: EXECUTED_BY_DELEGATE Qslot: /25  |
| Executed on    : plxc9488.pdx.intel.com:50994 Pool : jqdelosr_plxsodin070_1208882641|
| Queueing time  : Thu Aug 22 15:26:55 2013                                   |
| Starting time  : Thu Aug 22 15:27:22 2013          Qwait:   0h:00m:27s      |
| Command        : make_pattern.py -fullpath /p/pde/tvpv                      |
+-----------------------------------------------------------------------------+
CMD:        /p/pde/tvpv/tgl/vep2/rel/TGL/bin/make_pattern.py -fullpath
Traceback (most recent call last):
  File "/nfs/pdx/disks/nehalem.pde.252/hsw/tvpv/user_dir/jqdelosr/ewsJDR/vep/try/try1.py", line 23, in <module>
    raise ErrorEnv("test")
make_pattern STATUS: PASS
+-----------------------------------------------------------------------------+
| Exit Status    : 0                                                         |
| Finishing time : Thu Aug 22 15:27:22 2013                                   |
| CPU time       : Usr 0.0s    Sys 0.0s    WC  0h:00m:00s                     |
| Rusage Stats   : Mem:0      PF:  0/0       CSv/f:  0/0     Swaps:0          |
|                :           Msg:    0/0     IOops:  0/0     Sigs :0          |
+-----------------------------------------------------------------------------+
            ''')
            self.assertEqual(obj._readlog(tn), ("123444", "plxc9488.pdx.intel.com:50994", 0))

            # Passing Case without success message
            open(tn, "w").write('''
+-----------------------------------------------------------------------------+
| Logfile        : log.3.1377210415.817626.3                                  |
| Job id         : 138                        Class: EXECUTED_BY_DELEGATE Qslot: /25  |
| Executed on    : plxc9488.pdx.intel.com:50994 Pool : jqdelosr_plxsodin070_1208882641|
| Queueing time  : Thu Aug 22 15:26:55 2013                                   |
| Starting time  : Thu Aug 22 15:27:22 2013          Qwait:   0h:00m:27s      |
| Command        : make_pattern.py -fullpath /p/pde/tvpv                      |
+-----------------------------------------------------------------------------+
CMD:        /p/pde/tvpv/tgl/vep2/rel/TGL/bin/make_pattern.py -fullpath
+-----------------------------------------------------------------------------+
| Exit Status    : 0                                                         |
| Finishing time : Thu Aug 22 15:27:22 2013                                   |
| CPU time       : Usr 0.0s    Sys 0.0s    WC  0h:00m:00s                     |
| Rusage Stats   : Mem:0      PF:  0/0       CSv/f:  0/0     Swaps:0          |
|                :           Msg:    0/0     IOops:  0/0     Sigs :0          |
+-----------------------------------------------------------------------------+
            ''')
            self.assertEqual(obj._readlog(tn), ("123444", "plxc9488.pdx.intel.com:50994", 1))

            # Completed Case
            open(tn, "w").write('''
+-----------------------------------------------------------------------------+
| Logfile        : log.3.1377210415.817626.3                                  |
| Job id         : 138                        Class: EXECUTED_BY_DELEGATE Qslot: /25  |
| Executed on    : plxc9488.pdx.intel.com:50994 Pool : jqdelosr_plxsodin070_1208882641|
| Queueing time  : Thu Aug 22 15:26:55 2013                                   |
| Starting time  : Thu Aug 22 15:27:22 2013          Qwait:   0h:00m:27s      |
| Command        : cd false                                                   |
+-----------------------------------------------------------------------------+
+-----------------------------------------------------------------------------+
| Exit Status    : -4                                                         |
NB: Job execution failed on remote machine
| Finishing time : Thu Aug 22 15:27:22 2013                                   |
| CPU time       : Usr 0.0s    Sys 0.0s    WC  0h:00m:00s                     |
| Rusage Stats   : Mem:0      PF:  0/0       CSv/f:  0/0     Swaps:0          |
|                :           Msg:    0/0     IOops:  0/0     Sigs :0          |
+-----------------------------------------------------------------------------+
            ''')
            self.assertEqual(obj._readlog(tn), ("123444", "plxc9488.pdx.intel.com:50994", -4))

            # Fatal fail Case
            open(tn, "w").write('''
+-----------------------------------------------------------------------------+
| Logfile        : log.3.1377210415.817626.3                                  |
| Job id         : 138                        Class: EXECUTED_BY_DELEGATE Qslot: /25  |
| Executed on    : plxc9488.pdx.intel.com:50994 Pool : jqdelosr_plxsodin070_1208882641|
| Queueing time  : Thu Aug 22 15:26:55 2013                                   |
| Starting time  : Thu Aug 22 15:27:22 2013          Qwait:   0h:00m:27s      |
| Command        : cd false                                                   |
+-----------------------------------------------------------------------------+
Traceback (most recent call last):
  File "/nfs/pdx/disks/nehalem.pde.252/hsw/tvpv/user_dir/jqdelosr/ewsJDR/vep/try/try1.py", line 23, in <module>
    raise ErrorEnv("test")
veplib.prod.errors.ErrorFatal:    <<< Error Type
==============================================================================================
Error:      test
Suggestion: Pls read error message and do basic debug first. If error persist, then file TVPVhelp and paste this error message including the traceback information"
ErrorSig:   try1.py:<module>() lno#23
==============================================================================================
+-----------------------------------------------------------------------------+
| Exit Status    : 1                                                      |
NB: Job execution failed on remote machine
| Finishing time : Thu Aug 22 15:27:22 2013                                   |
| CPU time       : Usr 0.0s    Sys 0.0s    WC  0h:00m:00s                     |
| Rusage Stats   : Mem:0      PF:  0/0       CSv/f:  0/0     Swaps:0          |
|                :           Msg:    0/0     IOops:  0/0     Sigs :0          |
+-----------------------------------------------------------------------------+
            ''')
            self.assertEqual(obj._readlog(tn), ("123444", "plxc9488.pdx.intel.com:50994", 1))

            # command line error, 0 exit status
            open(tn, "w").write('''
+-----------------------------------------------------------------------------+
| Logfile        : log.3.1377210415.817626.3                                  |
| Job id         : 138                        Class: EXECUTED_BY_DELEGATE Qslot: /25  |
| Executed on    : plxc9488.pdx.intel.com:50994 Pool : jqdelosr_plxsodin070_1208882641|
| Queueing time  : Thu Aug 22 15:26:55 2013                                   |
| Starting time  : Thu Aug 22 15:27:22 2013          Qwait:   0h:00m:27s      |
| Command        : make_pattern.py -fullpath /p/pde/tvpv/tgl/trc/d04
+-----------------------------------------------------------------------------+
usage: make_pattern.py [-h] [-start flowname] [-stop flowname]
                       [-info] [-content modulecontent] [-ut module name]
make_pattern.py: error: unrecognized arguments: ringratio=21 ddrratio=17 ddrref=1
+-----------------------------------------------------------------------------+
| Exit Status    : 0                                                          |
| Finishing time : Thu Aug 22 15:27:22 2013                                   |
| CPU time       : Usr 0.0s    Sys 0.0s    WC  0h:00m:00s                     |
| Rusage Stats   : Mem:0      PF:  0/0       CSv/f:  0/0     Swaps:0          |
|                :           Msg:    0/0     IOops:  0/0     Sigs :0          |
+-----------------------------------------------------------------------------+
            ''')
            self.assertEqual(obj._readlog(tn), ("123444", "plxc9488.pdx.intel.com:50994", 1))

            # traceback fail Case with 0 exit code
            open(tn, "w").write('''
+-----------------------------------------------------------------------------+
| Logfile        : log.3.1377210415.817626.3                                  |
| Job id         : 138                        Class: EXECUTED_BY_DELEGATE Qslot: /25  |
| Executed on    : plxc9488.pdx.intel.com:50994 Pool : jqdelosr_plxsodin070_1208882641|
| Queueing time  : Thu Aug 22 15:26:55 2013                                   |
| Starting time  : Thu Aug 22 15:27:22 2013          Qwait:   0h:00m:27s      |
| Command        : make_pattern.py -fullpath                                  |
+-----------------------------------------------------------------------------+
CMD:        /p/pde/tvpv/tgl/vep2/rel/TGL/bin/make_pattern.py -fullpath
Traceback (most recent call last):
  File "/nfs/pdx/disks/nehalem.pde.252/hsw/tvpv/user_dir/jqdelosr/ewsJDR/vep/try/try1.py", line 23, in <module>
    raise ErrorEnv("test")
==============================================================================================
Error:      test
Suggestion: Pls read error message and do basic debug first. If error persist, then file TVPVhelp and paste this error message including the traceback information"
ErrorSig:   try1.py:<module>() lno#23
==============================================================================================
+-----------------------------------------------------------------------------+
| Exit Status    : 0                                                      |
NB: Job execution failed on remote machine
| Finishing time : Thu Aug 22 15:27:22 2013                                   |
| CPU time       : Usr 0.0s    Sys 0.0s    WC  0h:00m:00s                     |
| Rusage Stats   : Mem:0      PF:  0/0       CSv/f:  0/0     Swaps:0          |
|                :           Msg:    0/0     IOops:  0/0     Sigs :0          |
+-----------------------------------------------------------------------------+
            ''')
            self.assertEqual(obj._readlog(tn), ("123444", "plxc9488.pdx.intel.com:50994", 1))

            # Resubmitted job for -14
            open(tn, "w").write('''
+-----------------------------------------------------------------------------+
| Logfile        : log.3.1377210415.817626.3                                  |
| Job id         : 138                        Class: EXECUTED_BY_DELEGATE Qslot: /25  |
| Executed on    : plxc9488.pdx.intel.com:50994 Pool : jqdelosr_plxsodin070_1208882641|
| Queueing time  : Thu Aug 22 15:26:55 2013                                   |
| Starting time  : Thu Aug 22 15:27:22 2013          Qwait:   0h:00m:27s      |
| Command        : make_pattern.py -fullpath                                  |
+-----------------------------------------------------------------------------+
CMD:        /p/pde/tvpv/tgl/vep2/rel/TGL/bin/make_pattern.py -fullpath
==============================================================================================
+-----------------------------------------------------------------------------+
| Exit Status    : -14                                                        |
  NB: Job resubmited by a specific remote request
| Finishing time : Thu Aug 22 15:27:22 2013                                   |
| CPU time       : Usr 0.0s    Sys 0.0s    WC  0h:00m:00s                     |
| Rusage Stats   : Mem:0      PF:  0/0       CSv/f:  0/0     Swaps:0          |
|                :           Msg:    0/0     IOops:  0/0     Sigs :0          |
+-----------------------------------------------------------------------------+
            ''')
            self.assertEqual(obj._readlog(tn), ("123444", "plxc9488.pdx.intel.com:50994", -14))

            # Unknown exitcode case
            open(tn, "w").write('''
+-----------------------------------------------------------------------------+
| Logfile        : log.3.1377210415.817626.3                                  |
| Job id         : 138                        Class: EXECUTED_BY_DELEGATE Qslot: /25  |
| Executed on    : plxc9488.pdx.intel.com:50994 Pool : jqdelosr_plxsodin070_1208882641|
| Command        : cd false                                                   |
+-----------------------------------------------------------------------------+
+-----------------------------------------------------------------------------+
| Exit Status    : -4q                                                        |
NB: Job execution failed on remote machine
| Finishing time : Thu Aug 22 15:27:22 2013                                   |
+-----------------------------------------------------------------------------+
            ''')
            self.assertEqual(obj._readlog(tn), ("123444", "plxc9488.pdx.intel.com:50994", None))

    def test_kill_feeder(self):
        obj = NBFeeder()
        self.assertTrue(not obj.kill_feeder(), "Nothing to kill")

    @unittest.skipIf(*is_ut_option('OPTIONAL', message='due to pdx shutdown 9/12/23. Enable this again later'))
    def test_launch_nbtask(self):
        # logdir is None
        feeder = NBFeeder()
        task = NBTask("taskdir")
        with MockVar(NBTask, "get_job_count", Mock(return_value=1)):
            self.assertRaises(ErrorInput, feeder.launch_NBTask, task)

        with TempDir(name=True) as tdir:
            logdir = join(tdir, "nb_unittest", basename(tempname()))
            feeder = NBFeeder(logdir, nbclass=NBFeeder().cfg.unittest_nbclass,
                              cfgb={'workarea_subpath': "{user}/nbfeeder_vep2_UNITTEST/{nbpatch}",
                                    'megafeeder': False})
            # NBTask is None
            self.assertRaises(AttributeError, feeder.launch_NBTask, None)

            # NBTask().get_job_count() returns 0
            self.assertRaises(ErrorInput, feeder.launch_NBTask, task)

        with TempDir(name=True) as taskdir:
            my_task = NBTask(taskdir, taskname="testTask", nbclass="nbclass", nbpool="nbpool", nbqslot="nbqslot")
            my_task.add_job("echo 'somestring'", tag="testStr")
            my_task.add_job("ls ", tag="list")
            my_task.write_task_file()

            # nbfeeder().target is already set
            output = "Your task has been queued (TaskID: 3, Name: taskName)"
            with MockVar(SystemCall, "run_outonly", Mock(return_value=output)):
                with MockVar(NBFeeder, "_start_target", Mock(return_value="plxv1234:12345")):

                    # nbfeeder().target is already set
                    my_task._taskid = None
                    self.assertTrue(feeder.launch_NBTask(my_task))
                    self.assertEqual("3", my_task._taskid)

                    # nbfeeder().target is None
                    feeder.target = None
                    self.assertRaises(ErrorVep, feeder.launch_NBTask, my_task)

            # cmd_safe returned None
            with MockVar(SystemCall, "run_outonly", Mock(return_value=None)):
                with MockVar(NBFeeder, "_start_target", Mock(return_value="plxv1234:12345")):
                    self.assertRaises(OSError, feeder.launch_NBTask, my_task)

            # cmd_safe returned some error command, so output is not as expected, and re_obj is None
            with MockVar(SystemCall, "run_outonly", Mock(return_value="some failure reason")):
                with MockVar(NBFeeder, "_start_target", Mock(return_value="plxv1234:12345")):
                    err_reg = r"Unable to load task .* Reason: some failure reason"
                    self.assertRaisesRegex(ErrorVep, err_reg, feeder.launch_NBTask, my_task)


class NBTaskTest(TestCase):

    def test_init(self):
        """
        test object construction/instantiation
        """
        with TempDir(name=True) as tdir:

            feeder_obj = NBFeeder()  # for feeder_obj.cfg

            # raise ErrorInput exception when taskdir is None
            self.assertRaises(ErrorInput, NBTask, taskdir=None)

            gold_states = ["NEW", "LAUNCHED", "PASSED", "FAILED", "KILLED"]

            # Initialize with minimal args
            obj = NBTask(taskdir=tdir)
            self.assertTrue(obj)
            self.assertEqual(obj._taskdir, tdir)
            self.assertEqual(obj._taskname, obj.get_task_name())
            self.assertEqual(obj._taskfile, join(tdir, "%s.task" % obj._taskname))
            self.assertIsNone(obj._taskid)
            self.assertIsNone(obj._target)
            self.assertIsNone(obj._max_waiting)
            self.assertIsNone(obj._task_update_freq)
            self.assertEqual(obj._ttltask_days, 3)
            self.assertIsNone(obj._nbpool)
            self.assertIsNone(obj._nbqslot)
            self.assertIsNone(obj._nbclass)
            self.assertEqual(obj._valid_states, gold_states)
            self.assertEqual(obj._state, "NEW")

            # Initialize with all args set
            obj = NBTask(
                taskdir=tdir,
                cfgb=feeder_obj.cfg,
                taskname="my_task_name",
                max_waiting=20,
                task_update_freq=60,
                ttltask_days=5,
                nbpool="normal",
                nbqslot="/ORG/grp/jobfunc",
                nbclass="SLES11_stuff")
            self.assertTrue(obj)
            self.assertEqual(obj._taskdir, tdir)
            self.assertEqual(obj._taskname, "my_task_name")
            self.assertEqual(obj._taskfile, join(tdir, "my_task_name.task"))
            self.assertIsNone(obj._taskid)
            self.assertIsNone(obj._target)
            self.assertEqual(obj._max_waiting, 20)
            self.assertEqual(obj._task_update_freq, 60)
            self.assertEqual(obj._ttltask_days, 5)
            self.assertEqual(obj._nbpool, "normal")
            self.assertEqual(obj._nbqslot, "/ORG/grp/jobfunc")
            self.assertEqual(obj._nbclass, "SLES11_stuff")
            self.assertEqual(obj._valid_states, gold_states)
            self.assertEqual(obj._state, "NEW")

            # Initialize with all args set and taskfile and jobsfile
            File(join(tdir, "jobsfile")).touch("# line1\n # line 2\n # line3 \n # line4").chmod("0775")
            File(join(tdir, "my_task_name.task")).touch("# line1\n # line 2\n # line3 \n # line4").chmod("0775")
            with MockVar(NBTask, "get_task_name", Mock(return_value=True)):
                obj = NBTask(
                    taskdir=tdir,
                    cfgb=feeder_obj.cfg,
                    taskname="my_task_name",
                    max_waiting=20,
                    task_update_freq=60,
                    ttltask_days=5,
                    nbpool="normal",
                    nbqslot="/ORG/grp/jobfunc",
                    nbclass="SLES11_stuff",
                    taskfile=join(tdir, "my_task_name.task"),
                    jobsfile=join(tdir, "jobsfile"))
                self.assertTrue(obj)
                self.assertEqual(obj._taskdir, tdir)
                self.assertEqual(obj._taskname, "my_task_name")
                self.assertEqual(obj._taskfile, join(tdir, "my_task_name.task"))
                self.assertIsNone(obj._taskid)
                self.assertIsNone(obj._target)
                self.assertEqual(obj._max_waiting, 20)
                self.assertEqual(obj._task_update_freq, 60)
                self.assertEqual(obj._ttltask_days, 5)
                self.assertEqual(obj._nbpool, "normal")
                self.assertEqual(obj._nbqslot, "/ORG/grp/jobfunc")
                self.assertEqual(obj._nbclass, "SLES11_stuff")
                self.assertEqual(obj._valid_states, gold_states)
                self.assertEqual(obj._state, "NEW")
                self.assertEqual(obj._jobsfile, join(tdir, "jobsfile"))

        # Error case
        with TempDir(name=True) as tdir:
            feeder_obj = NBFeeder()  # for feeder_obj.cfg
            gold_states = ["NEW", "LAUNCHED", "PASSED", "FAILED", "KILLED"]
            File(join(tdir, "my_task_name.task")).touch("# line1\n # line 2\n # line3 \n # line4").chmod("0775")
            with self.assertRaisesRegex(ErrorVep, "Task file or jobs file specified is not a valid file."):
                NBTask(
                    taskdir=tdir,
                    cfgb=feeder_obj.cfg,
                    taskname="my_task_name",
                    max_waiting=20,
                    task_update_freq=60,
                    ttltask_days=5,
                    nbpool="normal",
                    nbqslot="/ORG/grp/jobfunc",
                    nbclass="SLES11_stuff",
                    taskfile=join(tdir, "my_task_name.task"),
                    jobsfile=join(tdir, "jobsfile"))

    def test_set_nb_vars(self):
        """
        test _set_nb_vars function
        """
        cfgb = NBFeeder().cfg

        # Use Mock to unset all vars as an initial test state
        with TempDir(name=True) as tdir, \
                MockVar(cfg, "nbpool", MockVar.delete), \
                MockVar(cfg, "nbclass", MockVar.delete), \
                MockVar(cfg, "nbqslot", MockVar.delete), \
                MockVar(os.environ, "NBPOOL", MockVar.delete), \
                MockVar(os.environ, "NBCLASS", MockVar.delete), \
                MockVar(os.environ, "NBQSLOT", MockVar.delete), \
                MockVar(OPT, "nbpool", MockVar.delete), \
                MockVar(OPT, "nbclass", MockVar.delete), \
                MockVar(OPT, "nbqslot", MockVar.delete):

            # Run tests by:
            # 1) Setting all var groups with each group having its own Mock context
            # 2) Run each test by exiting the Mock contexts one at a time to unset each var group
            # Test conditions for each var group:
            #   cfg    env    opt    init  ==>  Expected results
            #   ================================================
            #   set    set    set    set   ==>  init vars
            #   set    set    set    None  ==>  opt vars
            #   set    set    None   None  ==>  env vars
            #   set    None   None   None  ==>  cfg vars
            #   None   None   None   None  ==>  EXCEPTION
            with MockVar(cfgb, "nbpool", "cfg_pool"), \
                    MockVar(cfgb, "nbclass", "cfg_class"), \
                    MockVar(cfgb, "nbqslot", "cfg_qslot"):
                with MockVar(os.environ, "NBPOOL", "env_pool"), \
                        MockVar(os.environ, "NBCLASS", "env_class"), \
                        MockVar(os.environ, "NBQSLOT", "env_qslot"):
                    with MockVar(OPT, "nbpool", "opt_pool"), \
                            MockVar(OPT, "nbclass", "opt_class"), \
                            MockVar(OPT, "nbqslot", "opt_qslot"):

                        # Test: all vars are set.  Choose init vars
                        obj = NBTask(taskdir=tdir,
                                     cfgb=cfgb,
                                     nbpool="init_pool",
                                     nbclass="init_class",
                                     nbqslot="init_qslot")
                        obj._set_nb_vars()
                        self.assertEqual(obj._nbpool, "init_pool")
                        self.assertEqual(obj._nbclass, "init_class")
                        self.assertEqual(obj._nbqslot, "init_qslot")

                        # Test: all vars are set, except for init vars.  Choose cmdline opt vars
                        obj = NBTask(taskdir=tdir, cfgb=cfgb)
                        obj._set_nb_vars()
                        self.assertEqual(obj._nbpool, "opt_pool")
                        self.assertEqual(obj._nbclass, "opt_class")
                        self.assertEqual(obj._nbqslot, "opt_qslot")

                    # Test: Only cfg file and environment vars are set.  Choose environment vars
                    obj = NBTask(taskdir=tdir, cfgb=cfgb)
                    obj._set_nb_vars()
                    self.assertEqual(obj._nbpool, "env_pool")
                    self.assertEqual(obj._nbclass, "env_class")
                    self.assertEqual(obj._nbqslot, "env_qslot")

                # Test: Only cfg file vars are set.  Choose cfg file vars
                obj = NBTask(taskdir=tdir, cfgb=cfgb)
                obj._set_nb_vars()
                self.assertEqual(obj._nbpool, "cfg_pool")
                self.assertEqual(obj._nbclass, "cfg_class")
                self.assertEqual(obj._nbqslot, "cfg_qslot")

            # Test: No vars are set.  Raise exception
            obj = NBTask(taskdir=tdir, cfgb=cfgb)
            msg = "Could not determine netbatch vars .* from cmdline, environment, or cfg"
            self.assertRaisesRegex(ErrorUser, msg, obj._set_nb_vars)

            # Test: No vars are set, and cfg is None.  Correct exception is raised.
            obj = NBTask(taskdir=tdir)
            msg = "Could not determine netbatch vars 'nbpool','nbclass','nbqslot' from cmdline or environment"
            self.assertRaisesRegex(ErrorUser, msg, obj._set_nb_vars)

            # Test: Mixed case (not all vars need to come from the same place)
            with MockVar(cfgb, "nbpool", "cfg_pool"), \
                    MockVar(os.environ, "NBCLASS", "env_class"), \
                    MockVar(OPT, "nbqslot", "opt_qslot"):
                obj = NBTask(taskdir=tdir, cfgb=cfgb)
                obj._set_nb_vars()
                self.assertEqual(obj._nbpool, "cfg_pool")
                self.assertEqual(obj._nbclass, "env_class")
                self.assertEqual(obj._nbqslot, "opt_qslot")

            # Test: Case where only some things are defined.  Should raise exception
            with MockVar(cfgb, "nbpool", "cfg_pool"), \
                    MockVar(cfgb, "nbclass", "cfg_class"):
                obj = NBTask(taskdir=tdir, cfgb=cfgb)
                msg = "Could not determine netbatch var 'nbqslot' from cmdline, environment, or cfg"
                self.assertRaisesRegex(ErrorUser, msg, obj._set_nb_vars)

    def test_get_task_name(self):
        """
        test get_task_name function
        """
        with TempDir(name=True) as tdir, \
                MockVar(nbfeeder_base, "randint", Mock(return_value=1235)), \
                MockVar(nbfeeder_base, "CALLERBIN", "/p/pde/some/dir/bin/fancy_script.py"):

            # Task name is not passed in.  Should auto-populate.
            obj = NBTask(taskdir=tdir)
            self.assertEqual(obj.get_task_name(), "fancy_script.1235")

            # Task name is not passed in.  Tag is specified
            obj = NBTask(taskdir=tdir, tag="myfancytask")
            self.assertEqual(obj.get_task_name(), "fancy_script.1235.myfancytask")

            # Task name is passed in.  Should use that.
            obj = NBTask(taskdir=tdir, taskname="my_task_name")
            self.assertEqual(obj.get_task_name(), "my_task_name")

    def test_add_job_get_job_count(self):
        """
        test add_job and get_job_count functions
        """
        with TempDir(name=True) as tdir:
            obj = NBTask(taskdir=tdir)

            # Should be 0 jobs initially
            self.assertEqual(obj.get_job_count(), 0)

            # Add a job.  Should now be 1 job.
            cmd_1 = "do something"
            tag_1 = 34567
            obj.add_job(cmd=cmd_1, tag=tag_1)
            self.assertEqual(obj.get_job_count(), 1)
            self.assertIn(tag_1, obj._jobs_dict)
            self.assertEqual(obj._jobs_dict[tag_1].cmd, cmd_1)

            # Fail adding a job with the same tag.
            cmd_2 = "do something else"
            self.assertRaises(ErrorInput, obj.add_job, cmd=cmd_2, tag=tag_1)
            self.assertEqual(obj.get_job_count(), 1)

            # Add a job with a different tag (non-numeric this time)
            #   Also include pre_cmd and post_cmd
            cmd_3 = "do something different"
            tag_3 = "my_fancy_job"
            nbclass_3 = "SLES11_different"
            subargs_3 = "--extra-arg blah"
            pre_3 = "do before"
            post_3 = "do after"
            obj.add_job(cmd=cmd_3, tag=tag_3, nbclass=nbclass_3,
                        submission_args=subargs_3, pre_cmd=pre_3, post_cmd=post_3)
            # Should have 2 jobs now
            self.assertEqual(obj.get_job_count(), 2)
            self.assertIn(tag_1, obj._jobs_dict)
            self.assertEqual(obj._jobs_dict[tag_1].cmd, cmd_1)
            self.assertIsNone(obj._jobs_dict[tag_1].nbclass)
            self.assertIsNone(obj._jobs_dict[tag_1].submission_args)
            self.assertIsNone(obj._jobs_dict[tag_1].pre_cmd)
            self.assertIsNone(obj._jobs_dict[tag_1].post_cmd)
            self.assertIn(tag_3, obj._jobs_dict)
            self.assertEqual(obj._jobs_dict[tag_3].cmd, cmd_3)
            self.assertEqual(obj._jobs_dict[tag_3].nbclass, nbclass_3)
            self.assertEqual(obj._jobs_dict[tag_3].submission_args, subargs_3)
            self.assertEqual(obj._jobs_dict[tag_3].pre_cmd, pre_3)
            self.assertEqual(obj._jobs_dict[tag_3].post_cmd, post_3)

        # Test with jobsfile (i.e. tracegen task)
        with TempDir(name=True) as tdir:
            taskfile = join(tdir, "taskfile")
            jobsfile = join(tdir, "jobsfile")
            File(taskfile).touch()
            File(jobsfile).touch("job1\njob2\n  \n\njob3")
            obj = NBTask(taskfile=taskfile, jobsfile=jobsfile)
            self.assertEqual(obj.get_job_count(), 3)

    @unittest.skipIf(IS_WIN, 'unix only supports setting file permissions using number')
    def test_write_task_file(self):
        """
        test write_task_file function
        """
        cfgb = NBFeeder().cfg

        with TempDir(name=True) as tdir:
            # Should throw exception when can't open task file
            obj = NBTask(
                taskdir=join(tdir, "no_access_dir"),
                nbpool="normal",
                nbclass="SLES11_stuff",
                nbqslot="/ORG/grp/jobfunc")
            os.mkdir(obj._taskdir, 0o500)
            self.assertRaises(IOError, obj.write_task_file)
            # Restore permissions to ensure tempdir can be cleaned up
            os.chmod(obj._taskdir, 0o770)

            # Should throw exception when an nbvar is missing (in this case, nbpool)
            with TempDir(name=True) as tdir2, \
                    MockVar(cfg, "nbpool", MockVar.delete), \
                    MockVar(os.environ, "NBPOOL", MockVar.delete), \
                    MockVar(OPT, "nbpool", MockVar.delete):
                obj = NBTask(
                    taskdir=join(tdir2, "no_access_dir"),
                    nbclass="SLES11_stuff",
                    nbqslot="/ORG/grp/jobfunc")
                self.assertRaises(ErrorUser, obj.write_task_file)

            # Should NOT throw exception when env vars are defined in cfg/env/options instead of init
            # (Purpose of this test: init will set the vars, even if _set_nb_vars is not run.
            #     We want to verfify that _set_nb_vars is getting run.
            with TempDir(name=True) as tdir2, \
                    MockVar(OPT, "nbpool", "normal"), \
                    MockVar(OPT, "nbclass", "SLES11_stuff"), \
                    MockVar(OPT, "nbqslot", "/ORG/grp/jobfunc"):
                obj = NBTask(taskdir=join(tdir2, "no_access_dir"))
                obj.write_task_file()

            # Write task file with no tasks
            obj = NBTask(
                taskdir=tdir,
                taskname="fancy_task",
                nbpool="normal",
                nbclass="SLES11_stuff",
                nbqslot="/ORG/grp/jobfunc")
            obj.write_task_file()
            tfile = File(obj._taskfile)
            self.assertTrue(tfile.exists())
            tcontents = tfile.read()
            self.maxDiff = None
            self.assertEqual(tcontents,
                             """task fancy_task
{
    WorkArea %s
    TTL   3d

    queue normal
    {
        qslot /ORG/grp/jobfunc
    }
}

""" % obj._taskdir)

            # Write task file with multiple tasks, creating directories
            obj = NBTask(
                taskdir=join(tdir, "outer_dir", "inner_dir"),
                taskname="another_fancy_task",
                max_waiting=20,
                task_update_freq=60,
                nbpool="normal",
                nbclass="SLES11_stuff",
                nbqslot="/ORG/grp/jobfunc")
            obj.add_job(cmd="do something", tag=34567)
            obj.add_job(
                cmd="do something different",
                tag="my_fancy_job",
                nbclass="SLES11_different",
                submission_args="--extra-arg blah",
                pre_cmd="do before",
                post_cmd="do after")
            obj.write_task_file()
            tfile = File(obj._taskfile)
            self.assertTrue(tfile.exists())
            tcontents = tfile.read()
            self.assertEqual(tcontents,
                             """task another_fancy_task
{
    WorkArea %s
    TTL   3d

    queue normal
    {
        qslot /ORG/grp/jobfunc
        maxwaiting 20
        updatefrequency 60
    }
    task 34567 {
        SubmissionArgs --class SLES11_stuff
        jobs {
            nbjob run --log-file 34567.log do something
        }
    }
    task my_fancy_job {
        SubmissionArgs --class SLES11_different --extra-arg blah
        jobs {
            nbjob run --log-file my_fancy_job.log --pre-exec 'do before' --post-exec 'do after' do something different
        }
    }
}

""" % obj._taskdir)

    def test_get_task_file(self):
        """
        Unit test for function that returns the populated task file
        """
        with MockVar(NBTask, "__init__", Mock(return_value=None)):
            with MockVar(NBTask, "task_file_is_empty", Mock(return_value=True)),\
                    MockVar(NBTask, "write_task_file", Mock(return_value=True)):
                nbt = NBTask()
                res = nbt._taskfile = "123"
                self.assertEqual(nbt.get_task_file(), res)

            with MockVar(NBTask, "task_file_is_empty", Mock(return_value=False)):
                nbt = NBTask()
                res = nbt._taskfile = "456"
                self.assertEqual(nbt.get_task_file(), res)

    def test_get_task_state(self):
        """
        test get_task_state function
        """

        with MockVar(NBTask, "__init__", Mock(return_value=None)):
            nbt = NBTask()
            nbt._valid_states = ["NEW", "LAUNCHED", "PASSED", "FAILED", "KILLED"]
            nbt._taskid = None
            nbt._target = None

            # All states except LAUNCHED return same state
            with MockVar(nbt, "_state", "NEW"):
                self.assertEqual(nbt._get_task_state(), "NEW")
            with MockVar(nbt, "_state", "PASSED"):
                self.assertEqual(nbt._get_task_state(), "PASSED")
            with MockVar(nbt, "_state", "FAILED"):
                self.assertEqual(nbt._get_task_state(), "FAILED")
            with MockVar(nbt, "_state", "KILLED"):
                self.assertEqual(nbt._get_task_state(), "KILLED")

            # LAUNCHED state requires taskid and target to be set
            with MockVar(nbt, "_state", "LAUNCHED"):
                self.assertRaisesRegex(ErrorVep,
                                       "Target and/or taskid are not set with task in LAUNCHED state",
                                       nbt._get_task_state)

            # Task in LAUNCHED state, and is still running
            with MockVar(SystemCall, "run_outtxt",
                         Mock(return_value=(0, "TaskID,Status,ExitStatus\n3,Running,\n"))), \
                    MockVar(nbt, "_state", "LAUNCHED"), \
                    MockVar(nbt, "_taskid", "3"), \
                    MockVar(nbt, "_target", "plxc1234:56789"):
                self.assertEqual(nbt._get_task_state(), "LAUNCHED")
                self.assertEqual(nbt._state, "LAUNCHED")

            # Task in LAUNCHED state, and has since passed
            with MockVar(SystemCall, "run_outtxt",
                         Mock(return_value=(0, "TaskID,Status,ExitStatus\n3,Completed,0\n"))), \
                    MockVar(nbt, "_state", "LAUNCHED"), \
                    MockVar(nbt, "_taskid", "3"), \
                    MockVar(nbt, "_target", "plxc1234:56789"):
                self.assertEqual(nbt._get_task_state(), "PASSED")
                self.assertEqual(nbt._state, "PASSED")

            # Task in LAUNCHED state, and has since failed
            with MockVar(SystemCall, "run_outtxt",
                         Mock(return_value=(0, "TaskID,Status,ExitStatus\n3,Completed,-10\n"))), \
                    MockVar(nbt, "_state", "LAUNCHED"), \
                    MockVar(nbt, "_taskid", "3"), \
                    MockVar(nbt, "_target", "plxc1234:56789"):
                self.assertEqual(nbt._get_task_state(), "FAILED")
                self.assertEqual(nbt._state, "FAILED")

            # Task in LAUNCHED state, but has apparently been killed (task is no longer in feeder)
            with MockVar(SystemCall, "run_outtxt",
                         Mock(return_value=(0, "TaskID,Status,ExitStatus\n"))), \
                    MockVar(nbt, "_state", "LAUNCHED"), \
                    MockVar(nbt, "_taskid", "3"), \
                    MockVar(nbt, "_target", "plxc1234:56789"):
                self.assertEqual(nbt._get_task_state(), "KILLED")
                self.assertEqual(nbt._state, "KILLED")

            # Task in LAUNCHED state, and nbstatus command fails
            with MockVar(SystemCall, "run_outtxt",
                         Mock(return_value=(1, "Blah Fail\n"))), \
                    MockVar(nbt, "_state", "LAUNCHED"), \
                    MockVar(nbt, "_taskid", "3"), \
                    MockVar(nbt, "_target", "plxc1234:56789"):
                self.assertRaisesRegex(ErrorVep, "Failed to run task status cmd", nbt._get_task_state)

    def test_get_job_status(self):
        with MockVar(NBTask, "__init__", Mock(return_value=None)):
            nbt = NBTask()
            nbt._valid_states = ["NEW", "LAUNCHED", "PASSED", "FAILED", "KILLED"]
            nbt._taskid = None
            nbt._target = None
            nbt._jobsfile = None
            nbt._jobs_dict = {}
            # taskid or target not set
            self.assertRaisesRegex(ErrorVep, "Target and/or taskid are/is not set", nbt.get_job_status)

            # nbstatus queries begin here

            nbt._taskid = "1"
            nbt._target = "plxc2468:36912"
            expected = [{'Jobid': "10", 'Status': "Comp", 'Task': "1", 'Cmdline': "trex 13579 /p/pde/tvpv/global_db/apparatelocal/..", 'ExitStatus': "0"},
                        {'Jobid': "12", 'Status': "Comp", 'Task': "1", 'Cmdline': "trex 24680 /p/pde/tvpv/global_db/apparatelocal/..", 'ExitStatus': "0"}]

            # no jobs file and len(self._job_dict) == 0
            with MockVar(SystemCall, "run_sout_serr",
                         Mock(return_value=(0, "", ""))):
                self.assertEqual([], nbt.get_job_status())

            nbt._jobsfile = "jobsfile"
            # system call failed
            with MockVar(SystemCall, "run_sout_serr", Mock(return_value=(1, "", "some std err"))):
                # ecode, sout, serr
                self.assertRaisesRegex(ErrorVep, "Failed to run task status cmd", nbt.get_job_status)

            # successful system calls
            # nbstatus jobs --fields JobID,Status,Task,Cmdline,ExitStatus --target plxc25360:49173 --format csv

            # 'nbstatus jobs' returns just the header, no jobs to view
            with MockVar(SystemCall, "run_sout_serr",
                         Mock(return_value=(0, "Jobid,Status,Task,Cmdline,ExitStatus\n", ""))):
                self.assertEqual([], nbt.get_job_status())

            with MockVar(SystemCall, "run_sout_serr",
                         Mock(return_value=(0, "Jobid,Status,Task,Cmdline,ExitStatus", ""))):
                self.assertEqual([], nbt.get_job_status())

            # no jobs from main task (nbt) in result
            sout = "Jobid,Status,Task,ExitStatus,Cmdline\n" \
                   "10,Comp,5,0,trex 13579 /p/pde/tvpv/global_db/apparatelocal/..\n" \
                   "11,Comp,3,0,trex 13579 /p/pde/tvpv/global_db/apparatelocal/..\n" \
                   "12,Comp,9,0,trex 24680 /p/pde/tvpv/global_db/apparatelocal/..\n" \
                   "13,Comp,2,0,trex 13579 /p/pde/tvpv/global_db/apparatelocal/..\n" \
                   "19,Comp,4,0,trex 64895 /p/pde/tvpv/global_db/apparatelocal/.."
            with MockVar(SystemCall, "run_sout_serr", Mock(return_value=(0, sout, ""))):
                self.assertEqual([], nbt.get_job_status())

            # result containing multiple jobs from different tasks on this target
            sout = "Jobid,Status,Task,ExitStatus,Cmdline\n" \
                   "10,Comp,1,0,trex 13579 /p/pde/tvpv/global_db/apparatelocal/..\n" \
                   "11,Comp,3,0,trex 13579 /p/pde/tvpv/global_db/apparatelocal/..\n" \
                   "12,Comp,1,0,trex 24680 /p/pde/tvpv/global_db/apparatelocal/..\n" \
                   "13,Comp,2,0,trex 13579 /p/pde/tvpv/global_db/apparatelocal/..\n" \
                   "19,Comp,4,0,trex 64895 /p/pde/tvpv/global_db/apparatelocal/.."

            with MockVar(SystemCall, "run_sout_serr", Mock(return_value=(0, sout, ""))):
                actual = nbt.get_job_status()
                self.assertEqual(expected, actual)

            # len(task.jobs_dict) > 0
            # initialize jobs dict
            nbt._jobs_dict = {'nestedTask.one': NBJob(cmd="some cmd", tag="nestedTask.one"),
                              'nestedTask.two': NBJob(cmd="some cmd", tag="nestedTask.two")}
            nbt._jobsfile = None
            nbt._taskid = "1"

            # 'nbstatus tasks' returns just the header, no tasks to view
            sout = "Taskid,Status,Task,ExitStatus\n"
            with MockVar(SystemCall, "run_sout_serr",
                         Mock(return_value=(0, sout, ""))):
                self.assertEqual([], nbt.get_job_status())

            sout = "Taskid,Status,Task,ExitStatus"
            with MockVar(SystemCall, "run_sout_serr",
                         Mock(return_value=(0, sout, ""))):
                self.assertEqual([], nbt.get_job_status())

            # system call failed
            with MockVar(SystemCall, "run_sout_serr", Mock(return_value=(1, "", "some std err"))):
                # ecode, sout, serr
                self.assertRaisesRegex(ErrorVep, "Failed to run task status cmd", nbt.get_job_status)

            # result contains no nested tasks from this main task (nbt)
            sout = "Taskid,Status,Task,ExitStatus\n" \
                   "11,Complete,yet.another.task,0\n" \
                   "13,Complete,some.other.task,0\n" \
                   "19,Complete,another.task,0"
            with MockVar(SystemCall, "run_sout_serr", Mock(return_value=(0, sout, ""))):
                self.assertEqual([], nbt.get_job_status())

            # result contains nested tasks from this main task
            sout = "Taskid,Status,Task,ExitStatus\n" \
                   "2,Complete,nestedTask.one,0\n" \
                   "11,Complete,yet.another.task,0\n" \
                   "3,Complete,nestedTask.two,0\n" \
                   "13,Complete,some.other.task,0\n" \
                   "19,Complete,another.task,0"
            expected = [{'Jobid': '2', 'Status': 'Complete', 'Task': 'nestedTask.one', 'ExitStatus': '0'},
                        {'Jobid': '3', 'Status': 'Complete', 'Task': 'nestedTask.two', 'ExitStatus': '0'}]

            with MockVar(SystemCall, "run_sout_serr", Mock(return_value=(0, sout, ""))):
                actual = nbt.get_job_status()
                self.assertEqual(expected, actual)

    def test_process_status_result(self):
        with MockVar(NBTask, "__init__", Mock(return_value=None)):
            nbt = NBTask()
            nbt._valid_states = ["NEW", "LAUNCHED", "PASSED", "FAILED", "KILLED"]
            nbt._taskid = None

            self.assertRaisesRegex(ErrorVep, "Taskid is not set", nbt._process_status_result, "", "")

            nbt._taskid = "1"

            # sout is empty str
            self.assertEqual([], nbt._process_status_result(""))

            # no jobs/ tasks to view, nbstatus returns only a header
            self.assertEqual([], nbt._process_status_result("Jobid,Status,Task,ExitStatus,Cmdline"))

            self.assertEqual([], nbt._process_status_result("Jobid,Status,Task,ExitStatus,Cmdline\n"))

            self.assertEqual([], nbt._process_status_result("Taskid,Status,Task,ExitStatus"))

            self.assertEqual([], nbt._process_status_result("Taskid,Status,Task,ExitStatus\n"))

            # parse nested task status
            sout = "Taskid,Status,Task,ExitStatus\n" \
                   "2,Complete,nestedTask.one,0\n" \
                   "11,Complete,yet.another.task,0\n" \
                   "3,Complete,nestedTask.two,0\n" \
                   "13,Complete,some.other.task,0\n" \
                   "19,Complete,another.task,0"
            expected = [{"Jobid": "2", "Status": "Complete", "Task": "nestedTask.one", "ExitStatus": "0"},
                        {"Jobid": "3", "Status": "Complete", "Task": "nestedTask.two", "ExitStatus": "0"}]

            # task_id list is not given
            self.assertRaisesRegex(ErrorVep, "Cannot process a task status result without list of nested task IDs",
                                   nbt._process_status_result, sout)

            # none of the tasks in sout match task_id list
            taskid_list = [6, 7]
            self.assertEqual([], nbt._process_status_result(sout, taskid_list))

            # multiple tasks in sout match taskid_list
            taskid_list = [2, 3]
            self.assertEqual(expected, nbt._process_status_result(sout, taskid_list))

            # parse job status

            sout = "Jobid,Status,Task,ExitStatus,Cmdline\n" \
                   "11,Comp,3,0,trex 13579 /p/pde/tvpv/global_db/apparatelocal/..\n" \
                   "13,Comp,2,0,trex 13579 /p/pde/tvpv/global_db/apparatelocal/..\n" \
                   "19,Comp,4,0,trex 64895 /p/pde/tvpv/global_db/apparatelocal/.."

            # sout has no results matching nbt._Taskid
            self.assertEqual([], nbt._process_status_result(sout))

            sout = "Jobid,Status,Task,ExitStatus,Cmdline\n" \
                   "10,Comp,1,0,trex 13579 /p/pde/tvpv/global_db/apparatelocal/..\n" \
                   "11,Comp,3,0,trex 13579 /p/pde/tvpv/global_db/apparatelocal/..\n" \
                   "12,Comp,1,0,trex 24680 /p/pde/tvpv/global_db/apparatelocal/..\n" \
                   "13,Comp,2,0,trex 13579 /p/pde/tvpv/global_db/apparatelocal/..\n" \
                   "19,Comp,4,0,trex 64895 /p/pde/tvpv/global_db/apparatelocal/.."

            expected = [{'Jobid': "10", 'Status': "Comp", 'Task': "1", 'Cmdline': "trex 13579 /p/pde/tvpv/global_db/apparatelocal/..", 'ExitStatus': "0"},
                        {'Jobid': "12", 'Status': "Comp", 'Task': "1", 'Cmdline': "trex 24680 /p/pde/tvpv/global_db/apparatelocal/..", 'ExitStatus': "0"}]

            # sout contains results that match nbt._Taskid
            self.assertEqual(expected, nbt._process_status_result(sout))

    def test_get_job_state_count(self):
        with MockVar(NBTask, "__init__", Mock(return_value=None)):
            nbt = NBTask()
            nbt._valid_states = ["NEW", "LAUNCHED", "PASSED", "FAILED", "KILLED"]
            nbt._taskid = None
            nbt._target = None

            self.assertRaisesRegex(ErrorVep, "Target and/or taskid are not set", nbt.get_job_state_count)

            # attempt to set JOB_STATES
            with self.assertRaisesRegex(ConstError, "Cannot change value of JOB_STATES"):
                nbt.JOB_STATES = ['1', '2', '3', '4', '5', '6', '7']

            with MockVar(SystemCall, "run_sout_serr", Mock(return_value=(1, "", "some std err"))):
                nbt._taskid = "1"
                nbt._target = "plx123:target1"
                self.assertRaisesRegex(ErrorVep, "Failed to run task status cmd", nbt.get_job_state_count)

            # passing case
            sout = "Status,LocalWaitingJobs,RemoteWaitingJobs,RunningJobs,CompletedJobs,SuccessfulJobs,FailedJobs," \
                   "SkippedJobs\nCompleted,0,0,0,9,8,1,0"
            with MockVar(SystemCall, "run_sout_serr", Mock(return_value=(0, sout, ""))):
                expected = {'LocalWaiting': '0', 'RemoteWaiting': '0', 'Running': '0', 'Completed': '9',
                            'Successful': '8', 'Failed': '1', 'Skipped': '0'}
                self.assertEqual(expected, nbt.get_job_state_count())

    def test_has_jobs_file(self):
        with MockVar(NBTask, "__init__", Mock(return_value=None)):
            nbt = NBTask()
            nbt._jobs_dict = {"Item1": "A", "Item2": "B", "Item3": "C"}
            nbt._jobsfile = None
            nbt._valid_states = ["NEW", "LAUNCHED", "PASSED", "FAILED", "KILLED"]
            nbt._taskid = None
            nbt._target = None

            self.assertFalse(nbt.has_jobs_file())

            nbt._jobsfile = "jobsfile"
            self.assertTrue(nbt.has_jobs_file)

    def test_get_job_count(self):
        with MockVar(NBTask, "__init__", Mock(return_value=None)):
            nbt = NBTask()
            nbt._jobs_dict = {"Item1": "A", "Item2": "B", "Item3": "C"}
            nbt._jobsfile = None
            nbt._valid_states = ["NEW", "LAUNCHED", "PASSED", "FAILED", "KILLED"]
            nbt._taskid = None
            nbt._target = None
            self.assertEqual(nbt.get_job_count(), 3)

            # make mock jobsfile
            with TempDir(name=True, chdir=True) as tn:
                File("jobsfile").touch("# line1\n # line 2\n # line3 \n # line4").chmod("0775")
                nbt2 = NBTask()
                nbt2._jobs_dict = {"Item1": "A", "Item2": "B", "Item3": "C"}
                nbt2._jobsfile = join(tn, "jobsfile")
                nbt2._valid_states = ["NEW", "LAUNCHED", "PASSED", "FAILED", "KILLED"]
                nbt2._taskid = None
                nbt2._target = None
                self.assertEqual(nbt2.get_job_count(), 4)

    def test_is_running(self):
        """
        test is_running function
        """

        with MockVar(NBTask, "__init__", Mock(return_value=None)):
            nbt = NBTask()

            # Non-running states return False
            for state in ["NEW", "PASSED", "FAILED", "KILLED"]:
                with MockVar(nbt, "_get_task_state", Mock(return_value=state)):
                    self.assertEqual(nbt.is_running(), False)

            # Running states return True
            for state in ["LAUNCHED"]:
                with MockVar(nbt, "_get_task_state", Mock(return_value=state)):
                    self.assertEqual(nbt.is_running(), True)

    def test_set_state(self):
        """
        test set_state function
        """
        with MockVar(NBTask, "__init__", Mock(return_value=None)):
            # case 1: input is not a valid state, results in ErrorVep
            # new_state is None
            nbt = NBTask()
            nbt._valid_states = ["NEW", "LAUNCHED", "PASSED", "FAILED", "KILLED"]

            with self.assertRaisesRegex(ErrorVep, "is not a valid new state name"):
                nbt.set_state(None)

            # new_state contains invalid value, RERUN
            with self.assertRaisesRegex(ErrorVep, "is not a valid new state name"):
                nbt.set_state("RERUN")

            # case 2: input is invalid: new_state is NEW and self._state is LAUNCHED
            # results in ErrorVep
            with MockVar(nbt, "_state", "LAUNCHED"):
                with self.assertRaisesRegex(ErrorVep, "Invalid state progression from state LAUNCHED to state NEW"):
                    nbt.set_state("NEW")

            # case 3: input is invalid: new_state is LAUNCHED and self._state is PASSED
            # results in ErrorVep
            with MockVar(nbt, "_state", "PASSED"):
                with self.assertRaisesRegex(ErrorVep, "Invalid state progression from state PASSED to state LAUNCHED"):
                    nbt.set_state("LAUNCHED")

            # case 4: input is invalid: new_state is LAUNCHED and self._state is FAILED
            # results in ErrorVep
            with MockVar(nbt, "_state", "FAILED"):
                with self.assertRaisesRegex(ErrorVep, "Invalid state progression from state FAILED to state LAUNCHED"):
                    nbt.set_state("LAUNCHED")

            # case 5: input is invalid: new_state is LAUNCHED and self._state is FAILED
            # results in ErrorVep
            with MockVar(nbt, "_state", "FAILED"):
                with self.assertRaisesRegex(ErrorVep, "Invalid state progression from state FAILED to state LAUNCHED"):
                    nbt.set_state("LAUNCHED")

            # Passing test cases
            # None -> NEW
            # NEW -> LAUNCHED
            # LAUNCHED -> PASSED, FAILED, or KILLED
            for old_state, new_state in (
                (None, "NEW"),
                ("NEW", "LAUNCHED"),
                ("LAUNCHED", "PASSED"),
                ("LAUNCHED", "FAILED"),
                ("LAUNCHED", "KILLED")
            ):
                with MockVar(nbt, "_state", old_state):
                    nbt.set_state(new_state)
                    self.assertEqual(nbt._state, new_state)

    def test_set_as_launched(self):
        """
        test set_as_launched function
        """

        with MockVar(NBTask, "__init__", Mock(return_value=None)):
            nbt = NBTask()
            nbt._valid_states = ["NEW", "LAUNCHED", "PASSED", "FAILED", "KILLED"]
            nbt._target = None
            nbt._taskid = None

            target = "plxc1234:56789"
            taskid = "123"
            # Invalid state progression
            with MockVar(nbt, "_state", "PASSED"):
                self.assertRaisesRegex(ErrorVep, "Invalid state progression",
                                       nbt.set_as_launched, target, taskid)
                self.assertIsNone(nbt._target)
                self.assertIsNone(nbt._taskid)
                self.assertEqual(nbt._state, "PASSED")

            # target is None
            with MockVar(nbt, "_state", "NEW"):
                self.assertRaisesRegex(ErrorVep, "Target 'None' is not a valid target string",
                                       nbt.set_as_launched, None, taskid)
                self.assertIsNone(nbt._target)
                self.assertIsNone(nbt._taskid)
                self.assertEqual(nbt._state, "NEW")

            # target is not a valid target
            with MockVar(nbt, "_state", "NEW"):
                self.assertRaisesRegex(ErrorVep, "Target 'feeder_name' is not a valid target string",
                                       nbt.set_as_launched, "feeder_name", taskid)
                self.assertIsNone(nbt._target)
                self.assertIsNone(nbt._taskid)
                self.assertEqual(nbt._state, "NEW")

            # taskid is None
            with MockVar(nbt, "_state", "NEW"):
                self.assertRaisesRegex(ErrorVep, "Task ID is not a string, but is <.* 'NoneType'>",
                                       nbt.set_as_launched, target, None)
                self.assertIsNone(nbt._target)
                self.assertIsNone(nbt._taskid)
                self.assertEqual(nbt._state, "NEW")

            # taskid is not numeric
            with MockVar(nbt, "_state", "NEW"):
                self.assertRaisesRegex(ErrorVep, "Task ID string is not numeric: abc",
                                       nbt.set_as_launched, target, "abc")
                self.assertIsNone(nbt._target)
                self.assertIsNone(nbt._taskid)
                self.assertEqual(nbt._state, "NEW")

            # taskid is an int instead of a string
            with MockVar(nbt, "_state", "NEW"):
                self.assertRaisesRegex(ErrorVep, "Task ID is not a string, but is <.* 'int'>",
                                       nbt.set_as_launched, target, 123)
                self.assertIsNone(nbt._target)
                self.assertIsNone(nbt._taskid)
                self.assertEqual(nbt._state, "NEW")

            # Passing test case
            with MockVar(nbt, "_state", "NEW"):
                nbt.set_as_launched(target, taskid)
                self.assertEqual(nbt._target, target)
                self.assertEqual(nbt._taskid, taskid)
                self.assertEqual(nbt._state, "LAUNCHED")


class NBJobTest(TestCase):

    def test_init(self):
        """
        test object construction/instantiation
        """

        # raise ErrorInput exception when cmd is None
        self.assertRaises(ErrorInput, NBJob, cmd=None, tag=34567)

        # raise ErrorInput exception when tag is None
        self.assertRaises(ErrorInput, NBJob, cmd="do something", tag=None)

        # Initialize with minimal args
        obj = NBJob(cmd="do something", tag=34567)
        self.assertTrue(obj)
        self.assertEqual(obj.cmd, "do something")
        self.assertEqual(obj.tag, 34567)
        self.assertIsNone(obj.nbclass)
        self.assertIsNone(obj.submission_args)
        self.assertIsNone(obj.pre_cmd)
        self.assertIsNone(obj.post_cmd)

        # Initialize with all args set
        obj = NBJob(cmd="do something", tag=34567,
                    nbclass="SLES11_different", submission_args="--extra-arg blah",
                    post_cmd="do after", pre_cmd="do before")
        self.assertTrue(obj)
        self.assertEqual(obj.cmd, "do something")
        self.assertEqual(obj.tag, 34567)
        self.assertEqual(obj.nbclass, "SLES11_different")
        self.assertEqual(obj.submission_args, "--extra-arg blah")
        self.assertEqual(obj.pre_cmd, "do before")
        self.assertEqual(obj.post_cmd, "do after")


if __name__ == '__main__':
    unittest.main()
