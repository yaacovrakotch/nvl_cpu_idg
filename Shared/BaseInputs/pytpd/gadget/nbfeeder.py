#!/usr/intel/pkgs/python3/3.6.3a/modules/r1/bin/python3
"""
Launcher - nbfeeder module

Python interface to nbfeeder
Submit jobs and query status

How nbfeeder works:
==================
1. There must be a nbfeeder target (ie, self.target).  '<machine>:<pid>'
   The target is created by ('nbfeeder start'). See start_target()
   A target is associated to a workarea (ie. self.workarea).
   workarea directory config is:
       local:   cfg.workarea_local+cfg.workarea_subpath
       central: cfg.workarea_central+cfg.workarea_subpath  (for xhost machine or megafeeder)

2. Jobs can be launched through to the nbfeeder target via 'nbtask load'.
   each call to 'nbtask load' will have a taskid (ie. self.taskid).
   each taskid has several jobid.

Important Directories:
======================
self.workarea    - nbfeeder target/server directory ('/tmp/<something')
self.logdir      - where the job log files will be written (stdout and stderr)
self.logdir/task - delegate log files. This is the cwd on the client machine.
self.donedir     - completed log files

General Strategy:
=================
1. nbfeeder is not 100.000% robust. There can be lost jobs or
   jobs not queued or jobs lost in blackhole machine.
2. Given (1) above, then the final identification of a completed job (either pass or fail) is via
   log files (since it has the cmd line anyway).
3. (feature!) If wait==0 and run==0 for a certain period (say 60 seconds), then resubmit the lost jobs.
4. (feature!) 'Resubmit if non-fatal-fail and same machine.
    On retry, if fail occurs, and errorcode is >100, and same machine, then resubmit this job.
5. Note: if netbatch queue is full, then do something smart. Logic is outside this object.
   Status via: is_queue_full(seconds)
6. fatal-fail is identified by 'ErrorFatal:' exception raised (exit code is not used for fatal-fail)
   If ErrorFatal then do not resubmit. All other fails will re-try.

Other Notes:
===========
1. nbfeeder retry - sometimes same machine, sometimes not. No guarantee.
2. nbfeeder class assumes that cmds are unique. It is used as a key for the different command jobs.
3. On timeout (Exit Code -3002), it is considered a FAIL, thus it will try to relaunch (hopefully in different machine).
4. This command shows the queue: (can determine if wait is high)
/usr/intel/bin/nbqstat -P jf_tvpv slot=1017 class='jf_tvpv_6G||jf_tvpv_256G||jf_tvpv_8G||jf_tvpv_10G||jf_tvpv_144G||jf_tvpv_32G_sles9'
/usr/intel/bin/nbqstat -P linux1 slot=1015
"""

# TODO: For cases where job is completed successfully, but run=<value> still exist, then:
#   kill the feeder, and send email to admin, make the job complete and proceed normally

# TODO: Capability for feeder to restart automatically based on age (e.g. there is new config file
#   to fix a bug and feeder has to be restarted). use timestamp below to determine age.
#      -rw-r----- 1 jqdelosr users  487 2013-09-23 10:52 {workarea}/NBFeeder_conf.txt


from .dictmore import DictDot, DictConfig, TVPVConfigDict
from .files import File
from .disk import mkdirs, get_free_space
from .shell import HOSTNAME, USERNAME, MachineInfo, is_vnc_machine, CALLERBIN, SystemCall
from .strmore import regex, group, baseN
from .gizmo import get_sec, check_slots
from .pylog import log
from .helperclass import OPT
from .errors import check, ErrorInput, ErrorConfig, ErrorEnv, ErrorUser, ErrorVep

from os.path import join, isdir, basename, exists, isfile, dirname
from random import randint
import os
import time
import re

# secs before a netbatch log file is safe to move / gzip.
# Reason: netbatch will send email if the logfile is moved or gzipped if it is still writing to it
# TODO: Is this actually used anywhere?
LOG_AGE_LIMIT = 10


class UniqInc(object):
    """
    Returns a unique 4-character base-36 (1679616 combinations) given a string.
    It will return an incremental sequence (0,1,2,..,y,z,10,11,12)
    Used for nbfeeder log filename.
    Usage:
    >>> obj = UniqInc()
    >>> print obj('string1')
    0000
    """
    __slots__ = ['data']

    @check_slots
    def __init__(self):
        self.data = {}

    def __call__(self, name):
        if not hash(name) in self.data:
            self.data[hash(name)] = baseN(len(self.data), 36)
        return self.data[hash(name)].zfill(4)


class NBSetup:
    """
    The NBFeeder object is separated into two class (just because it's too big):
      NBSetup:      NBFeeder Setup and Start
      NBFeederBase: NBFeeder launching and monitoring

      NBFeederBase inherits NBSetup.

    Refer to NBFeederBase for usage.
    """
    _exectype = "N"                  # One letter indicator of class type. "N" for abstract
    _ORIG_PYTHONPATH = os.environ.get('PYTHONPATH', "")

    def __init__(self,
                 logdir=None,      # directory where job stdout & stderr are written
                 nbclass=None,     # netbatch nbclass to use (defined in config_nbfeeder)
                 nbqslot=None,
                 nbpool=None,
                 seq=False,        # nbfeeder sequential or not
                 timeout=None,     # timeout
                 maincfg=None,     # config file to use
                 cfgb=None):       # config override dictionary, specific items only (e.g. timout or workdir
        """Main NBFeeder initialization routine"""
        self.logdir = logdir
        self.jobs = {}    # dict of jobs for launch. key is cmdline, value is the aliasname|None
        self.jobdb = {}    # dict of jobs. key is hashdig, value is DictDot(), with various keys.

        # Uniq incremental identifier of commands. Used with self.jobsdb[self.uniqinc(cmd)] = DictDot()
        self.uniqinc = UniqInc()

        self.nbchecked = False     # has the pool been checked for queuing
        self.cfg = DictDot(self._vepdefault(maincfg))    # create a copy so any changes will not affect config_nbfeeder
        self.seq = seq

        if nbclass is None:
            self.logdir = logdir
        else:
            self.logdir = join(logdir, nbclass)

        if logdir is None:
            self.donedir = None
        else:
            self.donedir = join(logdir, "done")

        self.nb_init()

        # Miscellaneous initializations
        self.nbqslot = nbqslot
        self.nbpool = nbpool
        self.nbclass = None
        self._config_override(self.cfg, cfgb)
        self._set_nbinfo(nbclass, timeout)
        self.target = None

        # Execute configuration if logdir exist
        if logdir is not None:
            self._init_exec()

    def nb_init(self):
        """
        Various initializations
        """
        self.user = USERNAME              # username, for easy unittesting
        self.host = HOSTNAME              # host machine, for easy unittesting
        self.tvpvroot = '/p/pde/tvpv/tst/'  # veppaths.tvpvroot()   # tvpvroot, used in _template()

        self.target = None         # target string "<machine>:pid"
        self.nbhost = None         # feeder host machine, set in _init_exec()
        self.workarea = None         # workarea directory, set in _init_exec()
        self.ut_feeder_start = False   # for unittest: indicator if feeder_started or not
        self.nameid = "%s_%r" % ("launcher", time.time())    # change "launcher" to args later. This is a unique identifier for this object.

    def _init_exec(self, start_target=True):
        """Execute the nbfeeder startup sequence"""

        self._check_nbq()
        self.nbhost, self.workarea = self._get_host()   # get the target host
        self._setup_work_area()
        self._setup_environ()
        if start_target:  # pragma: no cover    - unittest only
            self._start_target()

    @classmethod
    def _vepdefault(cls, cfg_in):
        """Returns the default vep configuration"""
        if cfg_in is None:
            cfgb = cfg
        else:
            cfgb = cfg_in

        # Make new cfg.nbpool and cfg.memclass backwards-compatible to cfg.config
        if 'nbpool' in cfgb:
            for nbpool in cfgb.nbpool:
                for memclass in cfgb.nbpool[nbpool].valid_memclass:
                    if 'config' not in cfgb:
                        cfgb.config = DictConfig()

                    nbclass = nbpool + '_' + memclass
                    cfgb.config[nbclass] = DictConfig()  # Initialize this dict entry
                    cfgb.config[nbclass].SAME_AS(cfgb.nbpool[nbpool])
                    cfgb.config[nbclass].SAME_AS(cfgb.memclass[memclass])

        return cfgb

    def send_cmd(self, cmd_string, aliasname="cmd"):
        """
        Submits one job to memory queue
        aliasname, if specified, will be added in the log name for easy identification.
        """
        if cmd_string in self.jobs:
            raise ErrorInput("Job %s is already in queue. Cannot submit the same job twice."
                             "" % cmd_string,
                             "Add extra arguments to make the job unique.")

        self.jobs[cmd_string] = aliasname

    def is_complete(self):
        """Returns true if all jobs are done (ie, fail+ok = total)"""
        stat = self.status()
        done = sum(1 for cmd in self.jobdb if self.jobdb[cmd].done)
        if done == stat.total and stat.wait == 0 and stat.run == 0:
            return True

        return False

    def status(self):
        """
        Get the status of the jobs. Must assign resulting DictDot to self.stat
        Returns a DictDot of:
           {run:<val>,     # Running jobs. From nbstat.
            wait:<val>,    # Waiting jobs. From nbstat.
            good:<val>,      # Passing jobs. From log file.
            fail:<val>,    # (Confirmed) failing jobs. From log file.
            total:<val>}   # Total jobs
        """

    def _template(self, t_string, add_dict={}):
        """Given a template (t_string), return the evaluated value"""
        dd = dict(self.cfg)      # make a copy
        dd.update(vars(self))    # all object attributes
        dd.update(add_dict)
        while regex(r'\{\w+\}', t_string):
            t_string = t_string.format(**dd)
        return t_string

    def _is_xhost(self):
        """
        Returns True if central nbfeeder machine will be used
        """
        # based on config, if megafeeder is true
        if self.cfg.megafeeder:
            return True

        # machine memory is less than configured minimum setting
        if MachineInfo().machine_memory_gb() < self.cfg.mach_min_memory:
            return True

        # the machine is vnc
        if is_vnc_machine():
            return True

        return False

    def _get_host(self):
        """
        Identifies the host to use.
        If xhost machine, then return a beefy TVPV machine, if defined
        else, return current machine
        """
        if self._is_xhost():
            if not self.cfg.centralhost:
                raise ErrorConfig("Cannot launch netbatch/nbfeeder from [%s] because it is a vnc "
                                  "machine. " % HOSTNAME,
                                  "Pls use non-vnc machine to run %s. Get one by running ion."
                                  "" % basename(CALLERBIN))

            return (self.cfg.centralhost,
                    join(self._template(self.cfg.workarea_central),
                         self._template(self.cfg.workarea_subpath)))
        else:
            return (self.host,
                    join(self._template(self.cfg.workarea_local),
                         self._template(self.cfg.workarea_subpath)))

    def _create_check_space(self, dr, space_free):
        """
        Check if dir (dr) is writable (or create if not existing) and
        check for enough space
        """
        if isdir(dr):
            check.is_dir_writable(dr)
        else:
            mkdirs(dr, "02770")

        if get_free_space(dr) < space_free:
            raise ErrorEnv("Not enough disk space on %r. Free space is %d. Need at least %d." %
                           (dr, get_free_space(dr), space_free))

    def _move_existing_files(self, logdir):
        """
        Move existing files, if exist in logdir to logdir/prevfiles.<seconds>
        """
        if len(os.listdir(logdir)) == 0:
            return False

        # at this point, there are files
        prev = join(logdir, "prevfiles.%d" % time.time())
        self._create_check_space(prev, self.cfg.min_disk_space_kb)
        for ff in os.listdir(logdir):
            if ff.startswith("prevfiles."):
                continue
            os.rename(join(logdir, ff), join(prev, ff))
        return True

    @classmethod
    def _check_nbpool_big_memory(cls, cfgb, defaultpool, size):
        """
        If cfg.nbpool_big_memory exists
           e.g. cfg.nbpool_big_memory = (32, 'longjobs')
        If size >= the config memory size, re-route to the configured pool
        """
        (bigsize, bigpool) = cfgb.nbpool_big_memory
        if size >= bigsize:
            return bigpool
        else:
            return defaultpool

    @classmethod
    def _get_nbpoolcfg(cls, cfgb, size=0, patobj=None):
        """Return empty string if it's old methodology, or 'nbpool' if it's new methodology."""
        # If old methodology, don't change nbclass, else use nbpool_nbclass
        if 'nbpool' in cfgb:  # new methodology if self.cfg.nbpool exists
            defaultpool = cls._default_nbpool(cfgb.nbpool_default)

            if 'nbpool' in OPT and OPT.nbpool:  # See if OPT.nbpool is defined
                return OPT.nbpool

            if patobj is not None:              # return patobj nbpool definition if defined
                target = patobj.get_nbpool()
                if target is not None:
                    return target

            if 'nbpool_big_memory' in cfgb:
                return cls._check_nbpool_big_memory(cfgb, defaultpool, size)

            # return default pool
            return defaultpool

        return ''

    @classmethod
    def _get_nbclasscfg(cls, cfgb, user_nbclass=None, return_memclass=False, size=0, patobj=None):
        """
        Make memclass and nbpool backward-compatible to nbclass.

        If user_nbclass is given, use it
        Else if OPT.nbclass is given, use it
        Else use default nbclass

        Check if old config methodology, just return nbclass, else if new config structure (cfg.nbpool exists),
        return nbpool_nbclass.
        """
        # Assign nbclass
        if user_nbclass:  # user_nbclass has first priority
            nbclass = user_nbclass
            if 'nbpool' in cfgb and return_memclass:
                for memclass in cfgb.memclassmap:
                    if nbclass.endswith(memclass):
                        return memclass

            if nbclass in cfgb.config:
                return nbclass

        elif 'nbclass' in OPT and OPT.nbclass:  # OPT.nbclass has next priority
            nbclass = OPT.nbclass
        else:  # else use default
            memclass_default = None
            if 'memclass_default' in cfgb:
                memclass_default = cfgb.memclass_default
            nbclass = cls._default_nbclass(memclass_default)

        # If nbpool is not empty string, it is new methodology, so nbclass=nbpool_memclass
        nbpool = cls._get_nbpoolcfg(cfgb, size, patobj)
        if nbpool:
            if return_memclass:
                return nbclass    # If new methodology and you only want memclass (to access cfg.memclassmap)

            # Check that nbpool has nbclass as a valid memclass
            if nbclass not in cfgb.nbpool[nbpool].valid_memclass:
                raise ErrorInput("Memclass -nbclass [%s] is not valid with -nbpool [%s].\n"
                                 "Valid -nbclass values are: %s" % (nbclass, nbpool, ','.join(cfgb.nbpool[nbpool].valid_memclass)))

            # Define backwards-compatible key
            nbclass = nbpool + '_' + nbclass

        # Check if config exists
        if nbclass not in cfgb.config:
            raise ErrorInput("Input nbclass=%s is not defined in config_nbfeeder" % nbclass)

        return nbclass

    def _set_nbinfo(self, user_nbclass, timeout):
        """check validity of nbclass"""
        # Get nbclass (could be old format nbclass or new format 'nbpool_memclass')
        if self.is_raw_nbclass(user_nbclass):
            nbclass = user_nbclass
        else:
            nbclass = NBFeeder._get_nbclasscfg(self.cfg, user_nbclass)
            # In new methodology, .classname is dynamically assigned based on the nbclass and classos
            if 'nbpool' in self.cfg:
                memclass = NBFeeder._get_nbclasscfg(self.cfg, user_nbclass, return_memclass=True)
                classos = self.cfg.config[nbclass].classos
                self.cfg.config[nbclass].classname = self.cfg.memclassmap[memclass][classos]

        self.final_machcnt = self.cfg.config[nbclass].machine_count if nbclass in self.cfg.config else 0

        # Get and Check timeout
        softime = timeout
        if timeout is None:                            # timeout is not specified in args
            timeout = self.cfg.timeout                 # default value
            softime = self.cfg.softime

            if OPT.timeout:                            # use OPT.timeout first, if specified
                timeout = str(OPT.timeout) + "h"       # time units is "h"
                softime = str(OPT.timeout) + "h"       # time units is "h"

            elif OPT.replay:
                if 'vr2_timeout' in self.cfg:
                    timeout = self.cfg.vr2_timeout  # vr2 need longer time

                if 'vr2_softime' in self.cfg:
                    softime = self.cfg.vr2_softime

        # Assign the final values of nbclass, classname, qslot
        # If user has specified nbclass, nbqslot or nbpool, use those instead
        self.timeout = timeout
        self.softime = softime

        # Determine if user NB settings are used or not
        user_nb_msg = ""    # default boolean false

        if OPT.use_nb_env:
            user_nb_msg = ("-use_nb_env is provided but [{nbvar}] is not set in environment.",
                           "[{nbvar}] is needed for -use_nb_env. OR remove -use_nb_env altogether.")

            if OPT.user_nbclass or OPT.user_nbpool or OPT.user_nbqslot:
                raise ErrorUser("-use_nb_env cannot be used together with -user_nbclass/-user_nbpool/-user_nbqslot",
                                "Choose one or the other.")

        # check existence of user env vars for -use_nb_env or oneclick flow
        nb_items = {'NBPOOL': 'user_nbpool',
                    'NBCLASS': 'user_nbclass',
                    'NBQSLOT': 'user_nbqslot'}
        if user_nb_msg:
            for req_nbvar in nb_items:
                if OPT[nb_items[req_nbvar]]:
                    continue    # -user* is specified, so do not check existence of this env
                if req_nbvar not in os.environ:
                    raise ErrorUser(user_nb_msg[0].format(nbvar=req_nbvar),
                                    user_nb_msg[1].format(nbvar=req_nbvar))

        self.final_pool = self.nbpool if self.nbpool else self.cfg.config[nbclass].pool
        self.final_classname = nbclass if self.is_raw_nbclass(nbclass) else self.cfg.config[nbclass].classname
        self.final_qslot = self.nbqslot if self.nbqslot else self.cfg.config[nbclass].qslot  # new methodology
        self.nbclass = self.nbclass if self.nbclass else nbclass

        if user_nb_msg:
            self.final_pool = os.environ.get("NBPOOL", "")
            self.final_classname = os.environ.get("NBCLASS", "")
            self.final_qslot = os.environ.get("NBQSLOT", "")

        if OPT.user_nbclass:
            self.final_classname = OPT.user_nbclass

        if OPT.user_nbpool:
            self.final_pool = OPT.user_nbpool

        if OPT.user_nbqslot:
            self.final_qslot = OPT.user_nbqslot

    @staticmethod
    def is_raw_nbclass(nbclass):
        """Checks if nbclass is a valid NBClass to use directly or if a config lookup is needed"""
        if not isinstance(nbclass, str):
            return False
        elif re.search(r'(mem\d+g|normal)', nbclass):  # VEP Style classes: mem8g, mem128g6c, normal, normal_4c
            return False
        return True  # Raw classes: SLES12&&32G, SLES11_64MT_32G

    @classmethod
    def _default_nbpool(cls, nbpool_default=None):
        """Returns the default nbpool string"""
        if nbpool_default:
            return nbpool_default

        raise ErrorEnv("cfg.nbpool_default must be defined")

    @classmethod
    def _default_nbclass(cls, nbclass_default=None):
        """Returns the default nbclass string"""
        if nbclass_default:
            return nbclass_default

        return 'default'  # legacy

    @classmethod
    def get_nbclass(cls, size, cfgb=None, patobj=None):
        """Returns the nbclass name given the GB size of pattern or OPT arguments"""
        cfgb = cls._vepdefault(cfgb)

        # New methodology (cfg.nbpool and cfg.memclass exist)
        if 'nbpool' in cfgb:
            if OPT.nbclass:
                return cls._get_nbclasscfg(cfgb, OPT.nbclass, size=size, patobj=patobj)

            for memclass in cfg.memclass:
                cfgp = cfgb.memclass[memclass]
                if 'min_mem' in cfgp and 'max_mem' in cfgp:
                    if size >= cfgp.min_mem and size <= cfgp.max_mem:
                        return cls._get_nbclasscfg(cfgb, memclass, size=size, patobj=patobj)

        # old methodology
        else:
            if 'nbclass' in OPT and OPT.nbclass:
                return cls._get_nbclasscfg(cfg, OPT.nbclass, patobj=patobj)

            for nbclass in cfgb.config:
                cfgp = cfgb.config[nbclass]
                if 'min_mem' in cfgp and 'max_mem' in cfgp:
                    if size >= cfgp.min_mem and size <= cfgp.max_mem:
                        return nbclass

        raise ErrorEnv("Submitted job has size of %s. "
                       "No netbatch nbclass config (with .min_mem and .max_mem) has this size"
                       "." % size)

    def _config_override(self, maincfg, cfgb):
        """Given an override dictionary (cfg), update it in maincfg, after checks"""
        if cfgb is not None:
            check.required_valid(cfgb.keys(), valid=list(maincfg),
                                 message="Override cfg error:", errorclass=ErrorInput)
            maincfg.update(cfgb)

    @classmethod
    def check_config(cls, cfgb):
        """check the configuration files"""
        keys = ('centralhost '
                'cmd_check_nbq cmd_get_queue_full cmd_get_target cmd_kill_target '
                'cmd_launch cmd_nbjob cmd_remove_jobs cmd_start_target cmd_status cmd_nbqstat '
                'delegate_file non_delegate_file dlgfile fail_relaunch fail_relaunch_max '
                'use_delegates mach_min_memory max_jobpermach megafeeder '
                'min_disk_space_kb nbdir nbfeeder_config nbfeeder_group '
                'nbpatch nbproperties special_exit_codes cmd_remove_job regex_nb_removed '
                'regex_alive regex_nb_alive regex_taskid '
                'retry seqdelegates softime timeout '
                'unittest_nbclass workarea_central workarea_local workarea_subpath')

        nkeys = set(keys.split(" ") +
                    ["vr2_timeout", "vr2_softime", "config", "nbpool", "memclass", "memclassmap", "nbpool_default",
                     "memclass_default", "nbpool_big_memory"])

        # Check for valid and required keys
        check.required_valid(cfgb.keys(), required=keys, valid=nkeys,
                             message="config_nbfeeder error:")

        # Check for "nbpool" and "memclass" validity - new methodology
        if 'nbpool' in cfgb or 'memclass' in cfgb:
            # ---------------------------------------------
            # Checks for cfg.nbpool
            # ---------------------------------------------
            # Check for "nbpool" validity (if configured)
            if 'nbpool' not in cfgb:
                raise ErrorConfig("cfg.memclass exists but cfg.nbpool does not; they both need to be configured")

            check.is_dict(cfgb.nbpool, message="cfg.nbpool is not a dictionary type. It is a {type}")
            for nbpool in cfgb.nbpool:
                check.required_valid(cfgb.nbpool[nbpool].keys(),
                                     required="pool qslot machine_count classos valid_memclass",
                                     valid="pool qslot machine_count classos valid_memclass",
                                     message="config_nbfeeder error for cfg.nbpool.%s:" % nbpool)

                # Check that 'valid_memclass' is a list, and that all of the keys are valid in cfg.memclass
                check.is_list(cfgb.nbpool[nbpool].valid_memclass)
                for memclass in cfgb.nbpool[nbpool].valid_memclass:
                    if memclass not in cfgb.memclass:
                        raise ErrorConfig("cfg.nbpool.%s.valid_memclass key %s is not a valid key in cfg.memclass" % (nbpool, memclass))

                # Check that the four required nbpool names exist
                for poolname in ['tvpvadmin', 'critical', 'vcf', 'longjobs']:
                    if poolname not in cfgb.nbpool:
                        raise ErrorConfig("cfg.nbpool.%s is a required config" % poolname)

            # Check for cfg.default_nbpool
            if 'nbpool_default' not in cfgb:
                raise ErrorConfig("cfg.nbpool_default must be defined")

            # Check if cfg.default_nbpool is a valid nbpool
            if cfgb.nbpool_default not in cfgb.nbpool:
                raise ErrorConfig("Default cfg.nbpool_default %r is not a valid key in cfg.nbpool" %
                                  cfgb.nbpool_default)

            # ---------------------------------------------
            # Checks for cfg.memclass
            # ---------------------------------------------
            # Check for "memclass" validity (if configured)
            if 'memclass' not in cfgb:
                raise ErrorConfig("cfg.nbpool exists but cfg.memclass does not; they both need to be configured")

            check.is_dict(cfgb.memclass, message="cfg.memclass is not a dictionary type. It is a {type}")
            for memclass in cfgb.memclass:
                check.required_valid(cfgb.memclass[memclass].keys(),
                                     required="min_mem max_mem",
                                     valid="min_mem max_mem",
                                     message="config_nbfeeder error for cfg.memclass.%s:" % memclass)

            # Check for cfg.default_memclass
            if 'memclass_default' not in cfgb:
                raise ErrorConfig("cfg.memclass_default must be defined")

            # Check if cfg.default_memclass is a valid memclass
            if cfgb.memclass_default not in cfgb.memclass:
                raise ErrorConfig("Default cfg.memclass_default %r is not a valid key in cfg.memclass" %
                                  cfgb.memclass_default)

            # ---------------------------------------------
            # Check for cfg.nbpool_big_memory if it exists
            # ---------------------------------------------
            if 'nbpool_big_memory' in cfgb:
                if len(cfgb.nbpool_big_memory) != 2:
                    raise ErrorConfig("cfg.nbpool_big_memory must be a tuple of format (intsize, poolname)")
                (size, pool) = cfgb.nbpool_big_memory
                check.is_int(size, message="cfg.nbpool_big_memory first tuple element must be an int")
                if pool not in cfgb.nbpool:
                    raise ErrorConfig("cfg.nbpool_big_memory second tuple element must be a valid cfg.nbpool pool name")

            # ---------------------------------------------
            # Checks for cfg.memclassmap
            # ---------------------------------------------
            # Check for "memclassmap" validity (if configured)
            if 'memclassmap' not in cfgb:
                raise ErrorConfig("cfg.nbpool exists but cfg.memclassmap does not; they both need to be configured")

            check.is_dict(cfgb.memclassmap, message="cfg.memclassmap is not a dictionary type. It is a {type}")

            # Populate memclasslist
            memclasslist = dict()  # key is memclass, value is set of classos
            for nbpool in cfgb.nbpool:
                classos = cfgb.nbpool[nbpool].classos
                valid_memclasses = cfgb.nbpool[nbpool].valid_memclass
                for memclass in valid_memclasses:
                    if memclass not in memclasslist:
                        memclasslist[memclass] = set()
                    memclasslist[memclass].add(classos)

            # Do checking on memclasslist
            for memclass in memclasslist:
                check.required_valid(cfgb.memclassmap.keys(),
                                     required=' '.join(list(memclasslist.keys())),
                                     valid=' '.join(list(memclasslist.keys())),
                                     message="config_nbfeeder error for cfg.memclassmap.%s:" % memclass)

        # Check for "config" validity - old methodology
        else:
            check.is_dict(cfgb.config, message="cfg.config is not a dictionary type. It is a {type}")
            for nbclass in cfgb.config:
                check.required_valid(cfgb.config[nbclass].keys(),
                                     required="pool classos classname machine_count qslot",
                                     valid="pool classos classname machine_count qslot min_mem max_mem valid_memclass",
                                     message="config_nbfeeder error for cfg.config.%s:" % nbclass)

            # check for default nbclass existence
            nbclass = cls._default_nbclass()
            if nbclass not in cfgb.config:
                raise ErrorConfig("Default nbclass %r is missing in cfg.config" % nbclass)

        # Check for template keyword eval
        obj = cls()
        info = {'target': "(target)",    # for readability during printout
                'logdir': "(logdir)"}
        for ky in sorted(cfgb):
            if ky.startswith(('cmd', 'regex', 'dlg', 'workarea')):
                # this will raise exception if there are problems.
                print("%-20s: %s" % (ky, obj._template(cfgb[ky], add_dict=info)))
            else:
                print("%-20s: %s" % (ky, cfgb[ky]))   # this will raise exception if there are problems.
        print()

        # Check for existence of all cmd_* first element existence
        for ky in cfgb:
            if ky.startswith('cmd'):
                cmd = obj._template(cfgb[ky]).split()[0]
                if not exists(cmd):
                    raise ErrorConfig("config_nbfeeder error on %r. %r does not exist" % (ky, cmd))

        # Check for auto-off
        check.is_auto_off(cfgb, message=("config_nbfeeder: Input dictionary has autovivification. "
                                         "Turn off by AUTO_OFF()."))

    def _check_nbq(self):
        """
        Check if given pool,qslot,classname is valid
        Queue directly to the pool rather than waiting to have a feeder to queue to
        """
        if self.nbchecked:
            return
        self.nbchecked = True

        ecode1, out1, err1 = self._system(self._template(self.cfg.cmd_check_nbq), which="check_nbq()", retall=True)
        # print "\n Got: ecode1 %s, out1 %s, err1 %s, regex %s" % (ecode1, out1, err1, self.cfg.regex_nb_alive)

        if not regex(self.cfg.regex_nb_alive, out1):
            raise ErrorEnv("%s failed: stdout=%r stderr=%r" % (self._template(self.cfg.cmd_check_nbq), out1, err1))
        jobid = regex.group(1)

        ecode2, out2, err2 = self._system(self._template(self.cfg.cmd_remove_job) % jobid, which="check_nbq()", retall=True)
        # print "\n Got: ecode2 %s, out2 %s, err2 %s" % (ecode2, out2, err2)

        if not regex(self.cfg.regex_nb_removed, out2):
            raise ErrorEnv("cmd_remove_job %s failed with: %s, %s, %s" % (jobid, ecode2, out2, err2))

    def _setup_work_area(self):
        """Set the work area"""

        # need to be in tmp for non xhost. This has "environment/  logs/  machines_locks/  persistency/  root_task_wa/"
        os.environ['WORK_AREA'] = self.workarea

        # create the different directories
        self._create_check_space(self.logdir, self.cfg.min_disk_space_kb)   # resulting files

        # Do not move existing files, since multi-pool will use the same log file
        self._move_existing_files(self.logdir)

        self._create_check_space(join(self.logdir, "task"), self.cfg.min_disk_space_kb)
        self._create_check_space(join(self.donedir), self.cfg.min_disk_space_kb)
        self._create_check_space(self.workarea, self.cfg.min_disk_space_kb)

    def _setup_environ(self):
        """
        Sets the nbfeeder environment vars
        nbfeeder is heavy on env vars
        """
        if self.seq:
            os.environ['DELEGATEGROUP'] = ""
            os.environ['SEQUENTIAL'] = "sequential"
        else:
            os.environ['DELEGATEGROUP'] = "netbatch"
            os.environ['SEQUENTIAL'] = ""

        os.environ['SEQHOSTNAME'] = self.host
        os.environ['SEQ_DELEGATES'] = str(self.cfg.seqdelegates)
        os.environ['NBPROPERTIES'] = self.cfg.nbproperties
        os.environ['RETRY'] = str(self.cfg.retry)
        os.environ['NBFLOW_PATCH_LIST'] = self.cfg.nbpatch
        os.environ['__NBFEEDER_MONITOR_COMMAND'] = '/bin/echo EXIT'
        # each launch must have a unique bucket name ????

        os.environ['DELEGATE_LOGS'] = "/dev/null"

        # environment not needed
        if 'NB_POOLS' in os.environ:  # pragma: no cover
            del os.environ['NB_POOLS']

        # this one does not work with p6vector / faceless suid if set, tvpvhelp 25430
        if 'NB_WASH_GROUPS' in os.environ:  # pragma: no cover
            del os.environ['NB_WASH_GROUPS']

        log.debug("-i- Netbatch: DELEGATEGROUP %s" % os.environ["DELEGATEGROUP"])
        log.debug("-i- Netbatch: SEQUENTIAL %s" % os.environ["SEQUENTIAL"])
        log.debug("-i- Netbatch: SEQHOSTNAME %s" % os.environ["SEQHOSTNAME"])
        log.debug("-i- Netbatch: SEQ_DELEGATES %s" % os.environ["SEQ_DELEGATES"])
        log.debug("-i- Netbatch: NBPROPERTIES %s" % os.environ["NBPROPERTIES"])
        log.debug("-i- Netbatch: RETRY %s" % os.environ["RETRY"])
        log.debug("-i- Netbatch: NBFLOW_PATCH_LIST %s" % os.environ["NBFLOW_PATCH_LIST"])
        log.debug("-i- Netbatch: __NBFEEDER_MONITOR_COMMAND %s" % os.environ["__NBFEEDER_MONITOR_COMMAND"])
        log.debug("-i- Netbatch: DELEGATE_LOGS %s" % os.environ["DELEGATE_LOGS"])

    def _start_target(self, sleep=2):
        """Start nbfeeder target, if it does not exist"""
        self.get_target()
        if self.target is not None:
            return

        if exists(join(self.workarea, "NBFeeder_conf.txt")):
            os.unlink(join(self.workarea, "NBFeeder_conf.txt"))

        open(join(self.workarea, "NBFeeder_conf.txt"), "w").write(self.cfg.nbfeeder_config)

        # Start new daemon
        self.ut_feeder_start = True
        cmd = self._template(self.cfg.cmd_start_target)

        # Update cmd if remote machine
        if self.nbhost != self.host:
            cmd = self._template("ssh {nbhost} 'setenv NBFLOW_PATCH_LIST {nbpatch}; " + cmd + "'")

        ecode, out, err = self._system(cmd, which="start_target()", retall=True)

        if ecode:  # pragma: no cover    - safety check only
            raise ErrorEnv("nbfeeder start failed. See log file for details.")

        # Then get the feeder again
        try_loops = 15
        time.sleep(1)   # give a very small delay
        for i in range(try_loops):   # max of 15 tries (default of 30 seconds)
            self.get_target()
            if self.target is not None:
                return
            time.sleep(sleep)

        raise SystemExit('''
Error: Cannot find nbfeeder target after %s tries

Suggested fix:
1. Try running vcf in another machine
2. Try killing your nbfeeder by 'nbfeeder kill --target <machine:pid>'
   wait for few secs, then rerun vcf again on the same machine.
   Get the <machine:pid> from by running 'nbfeeder list'
3. Please try running vcf in ION machine if suggestion 1&2 does not work.
    Get the ION machine by running 'Xion &' in xterm. In ION GUI > New Session > select group > Automatically select machine > ok
4. Submit tvpvhelp if above suggestion(s) does not work.
''' % try_loops)  # pragma: no cover    - safety check only

    def _retall(self, retall, ecode, resout, reserr):
        """
        wrapper for retall (True: Return all three, False: Return resout only)
        """
        if retall:
            return ecode, resout, reserr
        return resout

    def _system(self, args, which, retall=False, logit=True):
        """
        Executes a system command
        This is a separate method for easy unittesting
        """
        if logit:
            log.debug("%s CMD: %s" % (which, args))

        ecode, resout, reserr = SystemCall(args).run_sout_serr()

        if logit:
            log.debug("%s stdout:\n%s" % (which, resout))
            if len(reserr) > 0:  # pragma: no cover    - logging only
                log.debug("%s stderr:\n%s" % (which, reserr))

        return self._retall(retall, ecode, resout, reserr)

    def get_target(self):
        """
        Returns feeder that is alive or None.
        """
        out = self._system(self._template(self.cfg.cmd_get_target),
                           which="get_target()")

        s_re = self._template(self.cfg.regex_alive)
        log.debug("Looking for: '%s'" % s_re)
        if regex(s_re, out):
            target = group(1)
            log.debug("-i- target: %s" % target)
            self.target = target
        else:
            # remove this log message if cause of "Failed to start feeder" errors are resolved
            log.info("-i- no match for %s in %s" % (s_re, out))
            self.target = None

        return self.target

    def kill_feeder(self):
        """Kill the feeder"""
        if self.target is None:
            return False  # nothing to kill

        self._system(self._template(self.cfg.cmd_kill_target),
                     which="kill_feeder()")
        return True

    def is_queue_full(self):
        """Returns True if there are jobs waiting in this qslot"""
        out = self._system(self._template(self.cfg.cmd_get_queue_full),
                           which="is_queue_full()")
        for line in out.split('\n'):
            if line.startswith('Wait'):
                return True    # at least one job is waiting

        return False  # no jobs is waiting

    def _cleanups(self):
        """NBFeeder specific cleanups"""
        # put back os.environ
        os.environ['PYTHONPATH'] = self._ORIG_PYTHONPATH

        # change permission of logdir/task
        startdir = join(self.logdir, "task")
        for root, dirs, files in os.walk(startdir):
            for dd in dirs:
                File(join(root, dd)).chmod("0770")

    @classmethod
    def all_nbclass(cls, cfgb=None):
        """Returns the nbclass names. Used on help"""
        cfgc = cls._vepdefault(cfgb)

        # If user has moved to the new configs, return cfg.memclass, else return cfg.config
        if 'memclass' in cfgc:
            return cfgc.memclass

        return cfgc.config

    @classmethod
    def all_nbpool(cls, cfgb=None):
        """Returns the nbpool names. Used on help"""
        cfgc = cls._vepdefault(cfgb)

        if 'nbpool' in cfgc:
            return cfgc.nbpool

        return None


class NBFeeder(NBSetup):
    """
    Submit, Check and Query functions for NBFeeder
    ENV var NBTOOLS_BIN can be set to override the version of nbtask used to launch.

    Usage:
    >>> feeder = NBFeeder(nblogdir, nbpool=nbpool, nbqslot=nbqslot, nbclass=nbclass)
    >>> my_task = NBTask(taskdir, taskname=taskname, nbpool=nbpool, nbclass=nbclass, nbqslot=nbqslot)
    >>> my_task.add_job(cmd, tag=jobid)
    >>> my_task.write_task_file()
    >>> feeder.launch(my_task)
    """

    def nb_init(self):
        super().nb_init()       # Call parent

        self.taskid = set()       # taskid number (will be populated in launch())
        self.stat = None        # stat dictionary (populated in status())

        self.launch_cnt = 0         # Count of launch calls
        self.statcnt = 0         # Count of status calls
        self.reftime = time.time() * 2   # Reference time since last queue>1 or running>1
        # Make this really large number upon start
        self.cntw0r0 = -1000     # Count of w0r0 occurrence

    def _nbqstat(self):
        """
        Get the number of waiting and running jobs in the queue slot
        This include other users. This indicator tells how long will my job be in the queue.
        """
        cmd = self._template(self.cfg.cmd_nbqstat)
        cmd = cmd.replace(r'\|', '|')
        out = self._system(cmd, which="nbqstat()", logit=self.statcnt == 1)
        stat = DictDot()
        stat.waitslot = 0
        stat.runslot = 0
        for line in out.split('\n'):
            if line.startswith('Wait'):
                stat.waitslot += 1
            if line.startswith(('Run', 'Send')):
                stat.runslot += 1
        return stat

    def _nbstatus(self):
        """
        Get results from netbatch nbstatus. Returns a dictionary of
           {run:<val>, wait:<val>, ok:<val>, fail:<val>, total:<val>}
        """
        self.statcnt += 1

        out = self._system(self._template(self.cfg.cmd_status) %
                           '||'.join('Task==' + x for x in self.taskid),
                           which="status()", logit=self.statcnt == 1)

        # init counters
        stat = DictDot()
        stat.total = 0
        stat.fail = 0
        stat.good = 0
        stat.wait = 0
        stat.run = 0

        fields = {}  # field index by field name

        for line in out.split('\n'):
            res = line.split(',')
            if line.startswith('Status'):
                for idx, value in enumerate(res):
                    fields[value] = idx
                log.dev(" _nbstatus fields: %s" % fields)
                continue
            if len(res) > 1:
                if 'Status' not in fields:  # Make sure 'Status' exists in fields, NB issue jitbit51624
                    log.info("NB status command failure, returns: %s" % out)
                    break
                stat.total += 1
                status = res[fields['Status']]
                log.dev(" jobID %s in dd: %s" % (int(res[fields['Jobid']]), res))

                if status == 'Run':
                    stat.run += 1
                elif status == 'Wait':
                    stat.wait += 1
                elif status == 'Comp':
                    nbexit = int(res[fields['ExitStatus']])
                    if nbexit == 0:
                        stat.good += 1
                    else:
                        stat.fail += 1

        return stat

    def status(self):
        """
        Get the status of the jobs.
        Returns a dictionary of:
           {run:<val>,     # Running jobs. From nbstat.
            wait:<val>,    # Waiting jobs. From nbstat.
            ok:<val>,      # Passing jobs. From log file.
            fail:<val>,    # (Confirmed) failing jobs. From log file.
            total:<val>}   # Total jobs
        """
        if len(self.jobdb) == 0 and len(self.taskid) == 0:
            raise ErrorInput("No jobs were launched. Cannot get status when jobs are not launched")

        jdb = self.jobdb
        nbstat = self._nbstatus()    # get from nbstatus (status of this object)
        nbqstat = self._nbqstat()    # get from nbqstat (status of the slot - this includes jobs from other users)

        # create dictionary
        stat = DictDot()
        stat.wait = nbstat.wait     # from nbstat
        stat.run = nbstat.run      # from nbstat
        stat.waitslot = nbqstat.waitslot
        stat.runslot = nbqstat.runslot
        stat.total = len(jdb)
        stat.good = sum(1 for cmd in jdb if jdb[cmd].done and jdb[cmd].exitcode == 0)
        stat.fail = sum(1 for cmd in jdb if jdb[cmd].done and jdb[cmd].exitcode != 0)
        self.stat = stat

        return stat

    def _readlog(self, ff):
        """
        Given a file, read it:
        return     hidx: actually, base logfile name
                   host: the host name the job ran on
               exitcode: apparant exit code from the job
        return exitcode as None if file is not complete (missing netbatch log footer)
        """
        hidx = None
        host = None
        jobid = 0
        success = 'no success msg'
        taskcmd = 'no task found'
        exitcode = None
        stackdump = False

        # Get the hex index from the filename. This is the unique cmdline/logfile name.
        ff_split = basename(ff).split('.')
        if len(ff_split) >= 3:
            hidx = ff_split[1]

        if not exists(ff):
            return hidx, None, None

        for line in File(ff).chomp():
            if regex(r"^\| Executed on\s+:\s+(\S+)", line):
                host = group(1)
            elif host is None and regex(r"^MACHINE:\s+(\S+)", line):
                host = group(1)

            elif regex(r"^\| Job id\s+:\s+(\d+)", line):
                jobid = group(1)  # this is a batch job verses -seq job

            elif regex(r"^\| Command\s+:\s+make_pattern.py ", line):
                taskcmd = 'make_pattern'
            elif taskcmd == 'no task found' and regex(r"^CMD:\s+.*/bin/make_pattern.py ", line):
                taskcmd = 'make_pattern'

            elif regex("ErrorFatal:", line):
                exitcode = 999999997    # Fatal Fail exitcode
                break

            elif regex(r"^Traceback \(most recent call last", line):
                stackdump = True  # any reason a stack dump isn't a failure?

            elif regex(r"^(\S+)\s+STATUS: PASS", line):
                success = group(1)  # which tool passed (make_pattern.py)

            # don't clear an existing failing exit code.  Should only be one match in the log, but...
            elif exitcode is None and regex(r"^\| Exit Status\s+:\s+(\S+)", line):
                exitcode = group(1)

                # Convert to int
                try:
                    exitcode = int(exitcode)
                except BaseException:
                    log.debug("WARNING: exitcode=%r is not number for %s" %
                              (exitcode, ff))
                    exitcode = None
                log.dev(" Final exitcode %s" % exitcode)

        if exitcode is None and (taskcmd == 'make_pattern' and taskcmd == success):
            exitcode = 0  # -seq jobs don't report exit code, but have CMD and success messages

        if (exitcode is None or exitcode == 0) and (taskcmd == 'make_pattern' and taskcmd != success):
            log.dev(" Set exit_code to 1: taskcmd %s, success %s" % (taskcmd, success))
            exitcode = 1  # can't be a passing run without passing message

        if stackdump and (taskcmd == 'make_pattern' and taskcmd == success):
            stackdump = False  # can't be a failing run with passing message (traceback in try/except block)

        if stackdump and exitcode >= 0:
            log.dev(" Set exit_code to 1: stackdump %s, exitcode %s" % (stackdump, exitcode))
            exitcode = 1

        return hidx, host, exitcode

    def launch_NBTask(self, nbtask, use_timeout=True):
        """
        launch a netbatch task. Can use ENV var NBTOOLS_BIN to provide a path for an different version of nbtask.
        :param nbtask: An NBTask object
        :type nbtask: NBTaskBase
        :param use_timeout: Use the config specified timeout values to kill a too long running task
        :type use_timeout: bool
        :return True: if successful
        :raise ErrorInput: if no NBTask object has no jobs, or no logdir is specified
        """

        if nbtask.get_job_count() == 0:
            raise ErrorInput("Cannot launch task: %s with no jobs" % nbtask.get_task_name())

        if self.logdir is None:
            raise ErrorInput("Cannot launch when logdir is not specified (__init__ arguments)")

        # start new feeder if needed, self.target == '<machine>:<pid>'
        if self.target is None:
            self._start_target()

        # Default to bare 'nbtask' cmd if nothing set. This is needed because design is overriding nbtask versions
        # through the ToolConfig in the MODEL_ROOT and they aren't being very detail oriented about picking
        # versions that exist at all sites for their products.
        nbtask_path = os.getenv("NBTOOLS_BIN", '')
        nbtask_cmd = join(nbtask_path, 'nbtask')
        cmd = "%s load" % nbtask_cmd

        if self.timeout and use_timeout:
            cmd += " --timeout %s" % get_sec(self.timeout)
        cmd += " --target %s" % self.target

        # ensure task file exists before loading job: write to it if not, overwrite if so
        taskfile = nbtask.get_task_file()
        cmd += " %s" % taskfile

        # get taskid from output
        output = SystemCall(cmd).run_outonly()
        taskid = None

        if output is None:
            raise OSError("Failed to load task to Netbatch with cmd: %s" % cmd)

        # output = Your task has been queued (TaskID: <id#>, Name: taskName)
        re_obj = regex(r'TaskID:\s*(\d+)\s*', output)
        if re_obj:
            taskid = re_obj.group(1)

        if taskid is None:
            raise ErrorVep("Unable to load task to Netbatch with cmd '%s'.  Reason: %s" % (cmd, output))

        # This method sets the nbtask's taskid, and sets the state to LAUNCHED
        nbtask.set_as_launched(self.target, taskid)

        self.taskid.add(taskid)
        log.debug("-i- taskid: %s" % taskid)

        if nbtask.get_taskid() is None:
            raise ErrorEnv("Submission to nbfeeder failed. "
                           "Cannot get taskid based on regex. "
                           "Seems that nbfeeder lost its mind.",
                           "Pls try to kill nbfeeder by executing: [nbfeeder kill --target %s]. "
                           "If that does not work, try a different machine. "
                           "If all things fail, file TVPVHELP")

        return True


class ConstError(TypeError):
    pass


class NBTask(object):
    """
    Object class to create and manage an individual Net Batch Task

    Input variables:
        Required:
            taskdir - the dir to place the task file into
        Optional:
            tag - tag to add to auto-generated task name
                    (tag is not added to taskname if explicitly set)
            taskname - overrides the name of the task instead of auto-generating
            max_waiting - max jobs allowed in wait queue for this task (default=50)
            task_update_freq, ttltask_days - netbatch-specific controls
            nbool, nbqslot, nbclass - overrides netbatch pool/qslot/class variables


    Usage:
        my_task = NBTask(taskdir=my_task_dir)
        my_task.add_job(cmd="do something", tag="my_tag")
            ... add more jobs as needed
        my_task.write_task_file()
            ... task is now ready for launch into feeder
    """

    def __init__(self,
                 taskdir=None,     # The dir to place the task file into
                 cfgb=None,        # cfg dict
                 tag=None,         # Tag to add to auto-generated task name
                 taskname=None,    # Overrides the name of the task
                 max_waiting=None,  # Max jobs allowed in wait queue
                 task_update_freq=None,  # Netbatch update frequency
                 ttltask_days=3,   # ttltask option (# days)
                 nbpool=None,      # NBPool
                 nbqslot=None,     # NBQSlot
                 nbclass=None,     # NBClass (default: $NBCLASS in env)
                 taskfile=None,    # explicitly set task file, eg: for tracegen tasks
                 jobsfile=None,
                 depends_on=None,  # Task Name of dependency. NB Will wait for first task to complete before this runs
                 ):   # explicitly set jobs file. jobs file is required for a task file

        # Check taskdir argument for the case where taskdir=None is passed in
        if taskdir is None and (taskfile is None or jobsfile is None):
            raise ErrorInput("taskdir or taskfile/jobsfile is required in NBTask init",
                             suggestion="This is a bug.  Please submit SnA help ticket.")

        self._taskdir = taskdir
        self._jobs_dict = DictDot()
        self._cfg = cfgb
        self._tag = tag
        self._taskname = taskname
        self._state = None
        self._taskid = None
        self._target = None
        self._max_waiting = max_waiting
        self._task_update_freq = task_update_freq
        self._ttltask_days = ttltask_days  # The number of days the task will not be deleted
        self._nbpool = nbpool
        self._nbqslot = nbqslot
        self._nbclass = nbclass
        self._depends_on = depends_on

        # get_task_name() will auto-populate _taskname if not yet set.
        if taskfile is None:
            self._taskfile = join(self._taskdir, "%s.task" % self.get_task_name())
            self._jobsfile = None
        elif isfile(taskfile) and isfile(jobsfile):
            self._taskdir = dirname(taskfile)
            self._taskfile = taskfile
            self._jobsfile = jobsfile
            self.get_task_name()
        else:
            raise ErrorVep("Task file or jobs file specified is not a valid file: %s %s" % (taskfile, jobsfile))

        self._valid_states = ["NEW", "LAUNCHED", "PASSED", "FAILED", "KILLED"]

        # Set initial state to NEW state
        self.set_state("NEW")

    @property
    def JOB_STATES(self):
        """
        constnant list of possible job states; used by self.get_job_state_count(), and any class wanting to report on
        the job states.
        """
        # DO NOT CHANGE WITHOUT SPEAKING TO JDR
        return ['LocalWaiting', 'RemoteWaiting', 'Running', 'Completed', 'Successful', 'Failed', 'Skipped']

    @JOB_STATES.setter
    def JOB_STATES(self, value):
        """
        setter property used to catch any attempts to edit/change the nbtask JOB_STATES
        :param value:
        :return: Nothing
        :raise: ConstError
        """
        raise ConstError("Cannot change value of JOB_STATES!")

    def _set_nb_vars(self):
        """
        Set the _nbpool, _nbclass, and _nbqslot object vars
        If var is already set, do not change (this happens if passed into init)
        Priority for each is:
          1) Leave as is if not None, or
          2) Cmdline args if not None, or
          3) Environment variables if not None, or
          4) Cfg file if not None, or
          5) EXCEPTION

        Input: None
        """
        bad_vars = []
        for varname in ("nbpool", "nbclass", "nbqslot"):
            obj_varname = "_" + varname
            env_varname = varname.upper()
            # First check if _varname is already set in object.  Don't change if it is.
            if getattr(self, obj_varname, None):
                continue
            # Next check if varname is set in cmdline options.
            if OPT.get(varname):
                setattr(self, obj_varname, OPT.get(varname))
                continue
            # Next check if varname is set in environment
            if os.environ.get(env_varname):
                setattr(self, obj_varname, os.environ.get(env_varname))
                continue
            # Next check if varname is set in the cfg.  Note that cfg is optional.
            if self._cfg and self._cfg.get(varname):
                setattr(self, obj_varname, self._cfg.get(varname))
                continue
            # If none of those, add list to bad_vars.  Exception will be raised.
            bad_vars.append(varname)

        if bad_vars:
            if self._cfg:
                nb_sources = "cmdline, environment, or cfg"
            else:
                nb_sources = "cmdline or environment"
            raise ErrorUser("Could not determine netbatch %s '%s' from %s" %
                            ("vars" if len(bad_vars) > 1 else "var",
                             "','".join(bad_vars),
                             nb_sources),
                            suggestion="Set missing vars either on cmdline (%s) or in environment (%s)" %
                                       (",".join('-%s' % var for var in bad_vars),
                                        ",".join(var.upper() for var in bad_vars)))

    def add_job(self, cmd, tag, nbclass=None, submission_args=None,
                post_cmd=None, pre_cmd=None):
        """
        Add a new job to the task

        Input:
            Required:
                cmd - The cmd to run in netbatch
                tag - A unique task tag (e.g. tid)
            Optional:
                nbclass - NBCLASS value to set uniquely for this job
                submission_args - Extra submission args for this job
                pre_cmd - Extra pre cmd to run before cmd
                post_cmd - Extra post cmd to run after cmd
            Raises Exception if job already added
        """
        if self._jobsfile is None:
            # raise exception if job with same tag already added to task
            if tag in self._jobs_dict:
                raise ErrorInput("A job with tag '%s' has already been added" % tag)

            # Create new job and add to task
            nbjob = NBJob(cmd=cmd, tag=tag,
                          nbclass=nbclass, submission_args=submission_args,
                          pre_cmd=pre_cmd, post_cmd=post_cmd)
            self._jobs_dict[tag] = nbjob
        else:  # jobsfile exists
            # This implementation is not currently working, but leaving commented for now
            #   in case it's needed in the future and velocity is given to debug it.
            # nbjob_cmd = "nbjob run --logfile {ttag}.log --incremental-log --exec-limits 48h:48h {command}".\
            #     format(command=cmd, ttag=tag)
            # File(self._jobsfile).touch(appendtxt=nbjob_cmd)
            raise ErrorVep("Adding jobs to NBTask where task and jobs files are passed in is not allowed.",
                           suggestion="This is a coding bug.  Please file an SnA help ticket")

    def has_jobs_file(self):
        return self._jobsfile is not None

    def get_job_count(self):
        """
        Find the number of jobs in the task
        Input: none
        Returns: Number of jobs (integer: 0 or more)
        """
        if self._jobsfile is None:
            return len(self._jobs_dict)
        else:
            # Get number of jobs in the jobs file
            jobfile_contents = File(self._jobsfile).read()
            jobfile_content_list = jobfile_contents.split("\n")

            count = 0
            for job_content in jobfile_content_list:
                if job_content.strip() != '':
                    count += 1
            return count

    def get_task_name(self):
        """
        Determine/Return the name of the task
            If _taskname is not yet set, then auto populate.
            Task name format = toolname.rundirnum[.tag]
        Input: none
        Returns: Task Name (string)
        """
        toolname = os.path.basename(CALLERBIN).replace('.py', '')
        rundir_num = randint(0, 10000)

        if self._taskname is None:
            self._taskname = "%s.%s" % (toolname, rundir_num)
            if self._tag is not None:
                self._taskname += ".%s" % self._tag

        return self._taskname

    def get_task_dir(self):
        """
        Return the task dir path
        :return: taskdir
        """
        return self._taskdir

    def get_taskid(self):
        return self._taskid

    def get_job_cmds(self):
        """
        Generator function giving the
        :yields: tuple of strings jobid and jobcmd
        :ytype: tuple
        """
        for (jobid, job_obj) in list(self._jobs_dict.items()):
            yield jobid, job_obj.cmd

    def write_task_file(self, nested_jobs=True):
        """
        Write the task file
        Input: none
        Raises exception if unable to open file
        :param nested_jobs: Default to writing jobs as nested tasks so dependencies can be used. This is the
        traditional VCF way. If set to False, will use a simple JobsFile instead that NBFeeder team recommends.
        """
        # First set the NB vars.  These are needed to be set before writing the task file.
        # This will raise ErrorUser exception if any nb vars could not be set.
        self._set_nb_vars()

        # Open the task file for writing, creating directories if needed
        mkdirs(self._taskdir)
        try:
            fh = open(self._taskfile, "w")
        except Exception as e:
            raise type(e)("The taskfile could not be opened for writing.  %s" % e)

        # Collect lines to write to file
        buffer_lines = [
            "task %s" % self._taskname,
            "{",
            "    WorkArea %s" % self._taskdir,
            "    TTL   %dd" % self._ttltask_days,
            "",
            "    queue %s" % self._nbpool,
            "    {",
            "        qslot %s" % self._nbqslot
        ]
        if self._max_waiting is not None:
            buffer_lines.append(
                "        maxwaiting %s" % self._max_waiting)
        if self._task_update_freq is not None:
            buffer_lines.append(
                "        updatefrequency %s" % self._task_update_freq)
        buffer_lines.append(
            "    }")

        if self._depends_on:
            buffer_lines.append(
                "    DependsOn %s [OnSuccess]" % self._depends_on
            )

        # Add each job to the task file
        # use key=str for py3 so keys of strings and ints can be used in the same dict
        joblist = []
        for jobid, job in sorted(iter(self._jobs_dict.items()), key=str, reverse=True):
            # Set up the nbjob cmd
            nbjob_cmd = "nbjob run --log-file %s.log" % jobid
            if job.pre_cmd is not None:
                nbjob_cmd += " --pre-exec '%s'" % job.pre_cmd
            if job.post_cmd is not None:
                nbjob_cmd += " --post-exec '%s'" % job.post_cmd
            # Set up the nbclass.  Override with job nbclass if set.
            if job.nbclass is not None:
                nbclass = job.nbclass
            else:
                nbclass = self._nbclass
            # Set up the submission args
            sub_args_array = ["--class %s" % nbclass]
            if job.submission_args is not None:
                sub_args_array.append(job.submission_args)
            # Print the job info
            if nested_jobs:
                buffer_lines.extend((
                    "    task %s {" % jobid,
                    "        SubmissionArgs %s" % " ".join(sub_args_array),
                    "        jobs {",
                    "            %s %s" % (nbjob_cmd, job.cmd),
                    "        }",
                    "    }"
                ))
            else:
                joblist.append("%s %s" % (nbjob_cmd, job.cmd))

        if not nested_jobs:
            my_jobs_file = self._taskfile + ".joblist"
            File(my_jobs_file).touch("\n".join(joblist))
            buffer_lines.append("    JobsFile %s " % my_jobs_file)

        # Close out the task file
        buffer_lines.extend((
            "}",
            ""
        ))

        # Write the file
        for line in buffer_lines:
            fh.write("%s\n" % line)
        fh.close()

    def task_file_is_empty(self):
        """
        :return: True/False
        determine whether the taskfile is empty
        """
        return os.path.getsize(self._taskfile) <= 0

    def get_task_file(self):
        """
        return the populated task file.
        If task file has not been written yet, call self.write_task_file
        """

        if self.task_file_is_empty():
            self.write_task_file()
        return self._taskfile

    def _get_task_state(self):
        """
        If task is in LAUNCHED state, query NB for status of the task, and update state if completed.
        Return the enumerated state value from self.states
        """

        # If state is not LAUNCHED, return state
        if self._state == "LAUNCHED":
            # Sanity check that target and taskid are set
            if self._target is None or self._taskid is None:
                raise ErrorVep("Target and/or taskid are not set with task in LAUNCHED state: target=%s, taskid=%s" %
                               (self._target, self._taskid))
            # Call Netbatch cmd to get task state
            cmd = "nbstatus tasks --target %s --fields TaskID,Status,ExitStatus --format csv TaskID=%s" % \
                  (self._target, self._taskid)
            ecode, results = SystemCall(cmd).run_outtxt()
            if ecode != 0:
                raise ErrorVep("Failed to run task status cmd (ecode = %d): %s\n%s" % (ecode, cmd, results))

            # Parse the results, get the exit code
            found_task_result = False
            for line in results.split("\n"):
                each_res = line.split(",")
                if len(each_res) == 3:
                    (taskid, status, exitstatus) = line.split(",")
                    if taskid == self._taskid:
                        found_task_result = True
                        # Check the exitstatus.
                        # empty string = still running (no change to state)
                        # 0 = completed and all jobs passed (set state to PASSED)
                        # anything else = completed and at least one job failed (set state to FAILED)
                        if exitstatus == "":
                            pass
                        elif exitstatus == "0":
                            self.set_state("PASSED")
                        else:
                            self.set_state("FAILED")
            if not found_task_result:
                # Did not find result for this task.  Must be missing in Netbatch.  Assume it was killed.
                self.set_state("KILLED")

        return self._state

    def get_job_status(self):
        """
        return the status of each job for this Task object
        nbstatus jobs --fields JobID,Status,Task,Cmdline,ExitStatus --target plxc25360:49173
        :return: job_status_dict: [{jobid:"", Status:"", Task:"", Cmdline:"",ExitStatus:""},] or empty list
        """
        job_status_dict = []

        if self._target is None or self._taskid is None:
            raise ErrorVep("Target and/or taskid are/is not set. Has this task been launched?",
                           suggestion="please confirm your task has been launched before attempting to get job status")

        if self.has_jobs_file():
            cmd = "nbstatus jobs --fields JobID,Status,Task,ExitStatus,Cmdline --target %s --format csv" % self._target

            ecode, sout, serr = SystemCall(cmd=cmd).run_sout_serr()

            if ecode != 0:
                raise ErrorVep("Failed to run task status cmd (ecode = %d): %s" % (ecode, serr))

            job_status_dict.extend(self._process_status_result(sout))

        # attempting to use the above approach for jobs added via self.add_job will yield an empty list because these
        # jobs are seen as nested tasks, and each will have its own task_id, i.e we cannot match them to this parent
        # task (self) by task id. However for each nested task, the taskid is incremented by 1, so we can consistently
        # derive them and then run nbstatus Tasks for each as opposed to nbstatus Jobs
        # Note: I have not seen any rule that says self._jobs_dict > 0 and self.has_jobsfile() are mutually exclusive

        if len(self._jobs_dict) > 0:
            taskid = int(self._taskid)
            taskid_list = []
            for tag in self._jobs_dict:
                taskid += 1
                taskid_list.append(taskid)

            cmd = "nbstatus tasks --fields Taskid,Status,Task,ExitStatus --target %s --format csv" % self._target

            ecode, sout, serr = SystemCall(cmd=cmd).run_sout_serr()

            if ecode != 0:
                raise ErrorVep("Failed to run task status cmd (ecode = %d): %s" % (ecode, serr))

            # print "1869: get_job_status: nbstatus tasks\n"
            job_status_dict.extend(self._process_status_result(sout, taskid_list))

        return job_status_dict

    def _process_status_result(self, sout, taskid_list=None):
        """
        parse sout to get the status of jobs or nested tasks (depending on res_type), and build then return a list
        of jobs status

        :param sout: std output from SystemCall
        :param taskid_list: optional, list of task_ids for nested tasks, used when nbstatus tasks is run,
        i.e. res_type=='task'
        :return: job_status_dict: [{jobid:"", Status:"", Task:"", Cmdline:"",ExitStatus:""},]
        """

        job_status_dict = []
        if self._taskid is None:
            raise ErrorVep("Taskid is not set. Has this task been launched?")

        if not sout:
            return job_status_dict
        is_task = False
        is_job = False
        results = sout.split("\n")
        for result in results:
            if "taskid" in result.lower():
                is_task = True
                continue

            if "jobid" in result.lower():
                is_job = True
                continue

            result_list = result.split(",")

            if len(result_list) < 4:
                continue  # skip any empty lines

            if is_task:
                if taskid_list is None:
                    raise ErrorVep("Cannot process a task status result without list of nested task IDs")

                if int(result_list[0]) not in taskid_list:
                    continue

            job_dict = {"Jobid": result_list[0],
                        "Status": result_list[1],
                        "Task": result_list[2],
                        "ExitStatus": result_list[3]}

            if is_job:
                if self._taskid != result_list[2]:
                    continue
                job_dict["Cmdline"] = result_list[4]

            job_status_dict.append(job_dict)

        return job_status_dict

    def get_job_state_count(self):
        """
        Given target and taskid are set, get the number of jobs in each given state

        :return: dict representing job state count:
        {'Completed': '5', 'LocalWaiting': '0', 'RemoteWaiting': '0', 'Running': '0', 'Successful': '0', 'Failed': '0',
         'Skipped': '0'}

        :raises: ErrorVep if target/taskid is not set or if nbstatus SystemCall failed
        """

        if self._target is None or self._taskid is None:
            raise ErrorVep("Target and/or taskid are not set with task in LAUNCHED state: target=%s, taskid=%s" %
                           (self._target, self._taskid))

        job_state_str = "jobs,".join(self.JOB_STATES) + "jobs"
        # convert self.JOB_STATES to a string, with 'jobs' appended to each field
        # job_state_str :
        #           LocalWaitingJobs,RemoteWaitingJobs,RunningJobs,CompletedJobs,SuccessfulJobs,FailedJobs,SkippedJobs

        cmd = "nbstatus tasks --target %s --fields Status,%s --format csv TaskID=%s" % \
              (self._target, job_state_str, self._taskid)

        ecode, sout, serr = SystemCall(cmd=cmd).run_sout_serr()

        if ecode != 0:
            raise ErrorVep("Failed to run task status cmd (ecode = %d): %s" % (ecode, serr))
        # sout:
        # Status,LocalWaitingJobs,RemoteWaitingJobs,RunningJobs,CompletedJobs,SuccessfulJobs,FailedJobs,SkippedJobs
        # Completed,0,0,0,9,8,1,0

        nbstatus_result_list = sout.split("\n")
        task_result_list = nbstatus_result_list[1].split(",")
        job_state_count = dict()
        i = 0

        while i < 7:
            # task_result_list[2] is the number of LocalWaitingJobs
            # self.job_states[0] == 'LocalWaiting'.. and so on
            job_state_count[self.JOB_STATES[i]] = task_result_list[i + 1]
            i += 1

        return job_state_count

    def is_running(self):
        """
        Check if task is running (i.e. in LAUNCHED state)
        :return: True if task is running (LAUNCHED)
        :return: False if task is not running (e.g. NEW, PASSED/FAILED, KILLED, etc)
        """
        return bool(self._get_task_state() == "LAUNCHED")

    def set_state(self, new_state):
        """
        Sets the state to the new state name
        Requires that state name be valid, and that the state progression is correct.
        :param new_state: String value of the new state ("NEW", "LAUNCHED", "PASSED", or "FAILED")
        """

        # Check input is a valid state
        if new_state is None or new_state not in self._valid_states:
            raise ErrorVep("New state %s is not a valid new state name.  Valid states: %s" %
                           (new_state, ",".join(self._valid_states)))

        # Check state progression
        state_change_ok = False
        if new_state == "NEW" and self._state is None:
            state_change_ok = True
        elif new_state == "LAUNCHED" and self._state == "NEW":
            state_change_ok = True
        elif new_state in ("PASSED", "FAILED", "KILLED") and self._state == "LAUNCHED":
            state_change_ok = True

        if not state_change_ok:
            raise ErrorVep("Invalid state progression from state %s to state %s" %
                           (self._state, new_state))

        # Set the new state
        self._state = new_state

    def set_as_launched(self, target, taskid):
        """
        Sets the task as having been launched.
        Does not actually launch the task to Netbatch (this should be done externally of NBTask)
        :param target: String representation of target feeder:port value.  Example: "plxc1234:56789"
        :param taskid: The task id for this task (numeric stored as string), as launched into the Netbatch
        """

        # Check for valid target and taskid format
        if target is None or not re.match(r"\w+:\w+$", target):
            raise ErrorVep("Target '%s' is not a valid target string.  Expected format 'feeder:port'" % target)
        if not isinstance(taskid, str):
            raise ErrorVep("Task ID is not a string, but is %s" % type(taskid))
        if not taskid.isdigit():
            raise ErrorVep("Task ID string is not numeric: %s" % taskid)

        # Set the state as Launched (will raise exception if not in a valid launchable state)
        self.set_state("LAUNCHED")

        # Set the target and taskid values
        self._target = target
        self._taskid = taskid


class NBJob(object):
    """
    Internal object class to define an individual Net Batch Job
    This class is a helper class for the NBTask class.

    Object variables:
        Required:
            cmd - The cmd to run in netbatch
            tag - A unique job tag (e.g. tid)
        Optional:
            pre_cmd - Extra pre cmd to run before cmd
            post_cmd - Extra post cmd to run after cmd
            nbclass - Override the nbclass for just this job

    Usage:
    myjob1 = NBJob(cmd="run this", tag="12345")
    myjob2 = NBJob(cmd="run this", tag="12345",
        pre_cmd = "run this before", post_cmd = "run this after")
    """

    def __init__(self,
                 cmd,              # The cmd to run in netbatch
                 tag,              # A unique job tag (e.g. tid)
                 nbclass=None,   # Override the nbclass for just this job
                 submission_args=None,  # Extra submission args for the job
                 pre_cmd=None,   # Extra pre cmd to run before cmd
                 post_cmd=None):  # Extra post cmd to run after cmd

        # Check required arguments for the case where arg=None is passed in
        for req_arg in ("cmd", "tag"):
            if locals().get(req_arg) is None:
                raise ErrorInput("%s is required in _NBJob init" % req_arg,
                                 suggestion="This is a bug.  Please submit SnA help ticket.")

        self.cmd = cmd
        self.tag = tag
        self.nbclass = nbclass
        self.submission_args = submission_args
        self.pre_cmd = pre_cmd
        self.post_cmd = post_cmd


# ##################################################################################
# VEP TST Config copied in here.
#
# Netbatch configuration file - common
#
# Heirarchy: config_nbfeeder_common -> config_nbfeeder_site -> config_nbfeeder
# ##################################################################################
cfg = TVPVConfigDict()

# Configuration knobs ========================================
# netbatch delegates can reduce job wait latency, the cost is more difficult debug because of details in logs
cfg.use_delegates = 0
cfg.seqdelegates = 1    # Used with seq=True (sequential delegates). Number of parallel jobs to run during sequential.
cfg.retry = 1    # nbfeeder retry (set to zero for no retry)
cfg.fail_relaunch = 2    # on fail retry (non-fatal-fail), how many different machine before final-fail
cfg.fail_relaunch_max = 3    # How many nbfeeder relaunches before consider fail
cfg.max_jobpermach = 1    # Maximum number of jobs in machine once it is grabbed (used in delegates)

# default timeout time. On timeout (Exit Code -3002), it is considered a FAIL, thus it will try to relaunch
cfg.timeout = "48h"
cfg.softime = "48h"
cfg.vr2_timeout = "120h"  # timeout time for VR2
cfg.vr2_softime = "120h"

cfg.min_disk_space_kb = 100000  # 100MB free space at least, for logdir and work area
cfg.megafeeder = False  # Set to True if always use central nbfeeder machine (feeder is still per user)

# Site specific configurations ========================================
cfg.nbfeeder_group = "mpe_vep2"  # used on CAC netbatch monitoring on which group the jobs are
cfg.nbproperties = "PROJECTNAME=ALL_MPE,ACTIVITY=Pattern Generation"
cfg.nbpatch = "nbflow21.jar"
cfg.nbdir = "/usr/intel/bin"
cfg.centralhost = "plxv9020"

# Command definition (templates) ========================================
cfg.cmd_check_nbq = "/usr/intel/bin/nbjob run --tar {final_pool} --class {final_classname} --qslot {final_qslot} " \
                    "--log-file /dev/null ls"
cfg.cmd_start_target = ("{nbdir}/nbfeeder start --work-area {workarea} --join "
                        "--conf {workarea}/NBFeeder_conf.txt --group {nbfeeder_group}")
cfg.cmd_get_queue_full = """/usr/intel/bin/nbstatus jobs --tar {final_pool} --fields 'Status,Jobid,Class::25,Qslot::25,User,Cmdline,Workstation' "Qslot=='{final_qslot}'" """
cfg.cmd_get_target = "{nbdir}/nbfeeder list"
cfg.cmd_kill_target = "{nbdir}/nbfeeder kill --target {target}"
cfg.cmd_remove_job = "{nbdir}/nbjob remove --target {final_pool} --reason queuing_test_complete %s"
cfg.cmd_remove_jobs = "{nbdir}/nbtask stop --target {target} --reason user_ctrl_c %s"
cfg.cmd_launch = "{nbdir}/nbtask load --target {target} {dlgfile}"
cfg.cmd_nbqstat = """/usr/intel/bin/nbstatus jobs --tar {final_pool} --fields 'Status,Jobid,Class::25,Qslot::25,User,Cmdline,Workstation' """

cfg.cmd_status = ("{nbdir}/nbstatus jobs --target {target} --fields "
                  #                             0      1      2             3     4            5        6
                  "Status,Jobid,TimesRestarted,Wtime,ExitStatus,delegate,JobLogFile"
                  " --format csv (%s)&&Delegate==false")

cfg.cmd_nbjob = ("{nbdir}/nbjob run --log-file {logdir}/%s --incremental-log "
                 "--exec-limits {softime}:{timeout} --log-file-dir {logdir} %s")

# nbfeeder regex config ========================================
cfg.regex_alive = r'\b({nbhost}:\d+)\s+\[alive\]\s.*{workarea_subpath}\b'  # "nbfeeder list" to determine alive target
cfg.regex_nb_alive = r"Your job has been queued \(JobID (\d+),"
cfg.regex_nb_removed = r"\d+\s+\(removed successfully\)"
cfg.regex_taskid = r'TaskID:\s+(\d+)'

# Other configurations ========================================
cfg.dlgfile = "{logdir}/DelegatesTaskFile.txt"  # Delegate file
cfg.workarea_local = "/tmp"                            # directory for local workarea
cfg.workarea_central = "{tvpvroot}/trash/nbfeeder"  # directory for central workarea # TODO: put this in its own disk
cfg.workarea_subpath = "{user}/nbfeeder_vep2/{nbpatch}"  # workarea subpath. This identifies a unique feeder.
cfg.mach_min_memory = 10  # minimum memory (in gb) for nbfeeder server (..or else, use central server)
cfg.nbpool_default = "vcf"
cfg.memclass_default = "mem4g"

# this is used by test_nbfeeder_base.py. SUIT does not use this.
cfg.unittest_nbclass = cfg.nbpool_default + '_' + cfg.memclass_default

# =========================================================================
# cfg.nbpool and cfg.memclass are new configs that replace cfg.config
#
# Internally to the code, they are combined to create cfg.config[pool_class] so that
# the existing code still works and older configs are backward-compatible.
#
# You need to create cfg.config.default after cfg.nbpool and cfg.memclass are defined
# =========================================================================

# Netbatch pool configuration ========================================
# Requires .pool, .qslot, .machine_count, .classos, .valid_memclass
# .machine_count is used to calculate the delegates - the bigger the machine count, the smaller the delegate

# nbpool configs listed in order of decreasing priority

# ---------------------------------------------------------------------------
# ATTENTION ADMINS:  At least the pool has to be overloaded in library/<site>/config/config_nbfeeder_site.py or
# the product config
# ---------------------------------------------------------------------------

# TVPV admin express
cfg.nbpool.tvpvadmin.pool = 'pdx_express'
cfg.nbpool.tvpvadmin.machine_count = 1
cfg.nbpool.tvpvadmin.qslot = '/MVE/MIG/TVPV/tvpv_dev'
cfg.nbpool.tvpvadmin.classos = 'sles12'
cfg.nbpool.tvpvadmin.valid_memclass = 'mem2g mem4g mem6g mem8g mem10g mem16g mem32g mem64g mem128g mem256g'.split()

# Normal VCF runs
cfg.nbpool.vcf.pool = 'pdx_express'
cfg.nbpool.vcf.machine_count = 1
cfg.nbpool.vcf.qslot = '/MVE/MIG/TVPV/tvpv_user'
cfg.nbpool.vcf.classos = 'sles11'
cfg.nbpool.vcf.valid_memclass = 'mem2g mem4g mem6g mem8g mem10g mem16g mem32g mem64g mem128g mem256g'.split()

# TVPV user express
cfg.nbpool.critical.pool = 'pdx_express'
cfg.nbpool.critical.machine_count = 1
cfg.nbpool.critical.qslot = '/MVE/MIG/TVPV/tvpv_user'
cfg.nbpool.critical.classos = 'sles12'
cfg.nbpool.critical.valid_memclass = 'mem2g mem4g mem6g mem8g mem10g mem16g mem32g mem64g mem128g mem256g'.split()

# Long runs, e.g. Scan pattern conversion that takes several hours or DRAGON traces
cfg.nbpool.longjobs.pool = 'pdx_express'
cfg.nbpool.longjobs.machine_count = 1
cfg.nbpool.longjobs.qslot = '/MVE/MIG/TVPV/tvpv_user'
cfg.nbpool.longjobs.classos = 'sles12'
cfg.nbpool.longjobs.valid_memclass = 'mem2g mem4g mem6g mem8g mem10g mem16g mem32g mem64g mem128g mem256g'.split()

# NB Class expression for SLES11
cfg.memclassmap.mem2g.sles11 = 'SLES11&&2G'
cfg.memclassmap.mem4g.sles11 = 'SLES11&&4G'
cfg.memclassmap.mem6g.sles11 = 'SLES11&&6G'
cfg.memclassmap.mem8g.sles11 = 'SLES11&&8G'
cfg.memclassmap.mem10g.sles11 = 'SLES11&&10G'
cfg.memclassmap.mem16g.sles11 = 'SLES11&&16G'
cfg.memclassmap.mem32g.sles11 = 'SLES11&&32G'
cfg.memclassmap.mem64g.sles11 = 'SLES11&&64G'
cfg.memclassmap.mem128g.sles11 = 'SLES11&&128G'
cfg.memclassmap.mem256g.sles11 = 'SLES11&&256G'

# NB Class expression for SLES12
cfg.memclassmap.mem2g.sles12 = 'SLES12&&2G'
cfg.memclassmap.mem4g.sles12 = 'SLES12&&4G'
cfg.memclassmap.mem6g.sles12 = 'SLES12&&6G'
cfg.memclassmap.mem8g.sles12 = 'SLES12&&8G'
cfg.memclassmap.mem10g.sles12 = 'SLES12&&10G'
cfg.memclassmap.mem16g.sles12 = 'SLES12&&16G'
cfg.memclassmap.mem32g.sles12 = 'SLES12&&32G'
cfg.memclassmap.mem64g.sles12 = 'SLES12&&64G'
cfg.memclassmap.mem128g.sles12 = 'SLES12&&128G'
cfg.memclassmap.mem256g.sles12 = 'SLES12&&256G'

# For Future use ONLY.  NB Class expression for SLES12
cfg.memclassmap.mem2g.sles12sp5 = 'SLES12SP5&&2G'
cfg.memclassmap.mem4g.sles12sp5 = 'SLES12SP5&&4G'
cfg.memclassmap.mem6g.sles12sp5 = 'SLES12SP5&&6G'
cfg.memclassmap.mem8g.sles12sp5 = 'SLES12SP5&&8G'
cfg.memclassmap.mem10g.sles12sp5 = 'SLES12SP5&&10G'
cfg.memclassmap.mem16g.sles12sp5 = 'SLES12SP5&&16G'
cfg.memclassmap.mem32g.sles12sp5 = 'SLES12SP5&&32G'
cfg.memclassmap.mem64g.sles12sp5 = 'SLES12SP5&&64G'
cfg.memclassmap.mem128g.sles12sp5 = 'SLES12SP5&&128G'
cfg.memclassmap.mem256g.sles12sp5 = 'SLES12SP5&&256G'

# Netbatch configs by memory class ===============================
# Requires .min_mem, .max_mem
# .min_mem and .max_mem are used in default finding of machines. There must be no overlap in values.
# mem2g is the default class that is used because patobj returns memory=2 in PatternBase
# To override a specific content (e.g scan atpg) to use bigger memory get_memsize() method
# see BXT/pat/bxtpat.py as example and contact jqdelosr
cfg.memclass.mem2g.min_mem = 0
cfg.memclass.mem2g.max_mem = 2

cfg.memclass.mem4g.min_mem = 3
cfg.memclass.mem4g.max_mem = 4

cfg.memclass.mem6g.min_mem = 5
cfg.memclass.mem6g.max_mem = 6

cfg.memclass.mem8g.min_mem = 7
cfg.memclass.mem8g.max_mem = 8

cfg.memclass.mem10g.min_mem = 9
cfg.memclass.mem10g.max_mem = 10

cfg.memclass.mem16g.min_mem = 11
cfg.memclass.mem16g.max_mem = 16

cfg.memclass.mem32g.min_mem = 17
cfg.memclass.mem32g.max_mem = 32

cfg.memclass.mem64g.min_mem = 33
cfg.memclass.mem64g.max_mem = 64

cfg.memclass.mem128g.min_mem = 65
cfg.memclass.mem128g.max_mem = 128

cfg.memclass.mem256g.min_mem = 129
cfg.memclass.mem256g.max_mem = 256

cfg.special_exit_codes['resub'][-6]["The Job leader died for unknown reason.  Netbatch resubmits such Jobs a "
                                    "limited number of times. This way, if the problem is not Job--related"]
cfg.special_exit_codes['resub'][-9]["Job killed by owner request (user submitted Job with --kill or --resubmit option)"]
cfg.special_exit_codes['resub'][-10]["Job killed by resubmit command (nbjob resubmit)"]
cfg.special_exit_codes['resub'][-14]["The Job was resubmitted by a specific remote request, and returns to the "
                                     "wait queue"]
cfg.special_exit_codes['resub'][-15]["The Job was resubmitted by a specific remote superuser request, and returns to "
                                     "the wait queue"]
cfg.special_exit_codes['resub'][-310]["Job failed because Feeder delegate was not available"]
cfg.special_exit_codes['resub'][-323]["The Job was resubmitted because the Workstation it was running on was locked"]
cfg.special_exit_codes['resub'][-3011]["The Job was resubmitted by the WSM auto-tuning service"]
cfg.special_exit_codes['resub'][-3013]["The Job was resubmitted because it exceeded a Wvmem limit"]
cfg.special_exit_codes['resub'][-3014]["The Job was resubmitted by another WSM because of preemption"]
cfg.special_exit_codes['resub'][-3019]["The Job was resubmitted because it was waiting in a physical Pool for too "
                                       "long (that is, longer than the period specified by the Virtual Pool's "
                                       "ResubmitThreshold"]
cfg.special_exit_codes['resub'][-3026]["The parallel Job was resubmitted because a slave Job was resubmitted"]

# Basic Task File setup =============================================================
cfg.non_delegate_file = """Task ${TASK_NAME} {
   WorkArea ${TASK_WORK_AREA}
   SubmissionArgs  --class ${CLASS}
   Queue ${POOL} {
      Qslot ${QSLOT}
      }
   JobsFile ${JOBFILE}
   }
"""

# Delegate-based Task File setup ============================================================
cfg.delegate_file = """Delegatedtask ${TASK_NAME} {
   WorkArea ${TASK_WORK_AREA}
   SubmissionArgs --on-job-finish ExitStatus>100||ExitStatus<0:Requeue(${RETRY})
   DelegateDispatchThreshold 2m

   PoolDelegatesGroup netbatch {
      Priority 20
      Queue ${POOL} {
         Qslot ${QSLOT}
         }
      MaxDelegates ${DELEGATES}
      SubmissionArgs --class ${CLASS}
      }

   MachineDelegatesGroup sequential {
      Priority 10
      Machines {
         ${SEQHOSTNAME}
         }
      JobsPerDelegate ${SEQ_DELEGATES}
      }

   UseDelegateGroups {
      ${SEQUENTIAL}
      ${DELEGATEGROUP}
      }
   JobsFile ${JOBFILE}
   }
"""

# Nbfeeder config File setup =============================================================
cfg.nbfeeder_config = """Policy IdleTimeKill {
   Schedule {
      Recurrence 120m
      Condition IdleTimeMinutes>2880 {
         ifTrue KillFeeder
         }
      }
   }

Policy TaskCleanup {
   Schedule {
      Recurrence 60m
      ifTrue DeleteOldTasks age=1d
      }
   }

CustomField ErrorString {
   Context job
   Type string
   Description DPR Return Status
   }

CustomField File {
   Context job
   Type string
   Description FileName
   KeepOnResubmit true
   }

FieldSize {
   Jobs ErrorString:1000
   }

Permission {
   Operations TaskLoad
   Groups gdlusers
   }
"""

cfg.AUTO_OFF()
