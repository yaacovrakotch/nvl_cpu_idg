#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Various shell routines and os related helpers.

Routines here must work in unix and windows

Variable summary:
   HOSTNAME       - machine name
   USERNAME       - user name
   CALLERBIN      - name of executable caller (derived from sys.argv[0])
   LAUNCH_CWD     - original cwd when script is launched
"""

import subprocess
import multiprocessing
import time
import os
import sys
import re
import shlex
import socket
from os.path import join, expanduser, exists, basename
from .gizmo import CacheThis, IS_UNIX, IS_WIN
from .strmore import regex, group, putquotes, to_ascii, curtime
from .files import TempName, TempDir, File
from .dictmore import DictDot, autodict
from .helperclass import Enum, OPT, TagOnce, Timeout
from .tvpv import TvpvEnv
from .config_release_sites_common import sitecfg_common as access_machines
from collections import deque
from itertools import chain
from .pylog import log    # to support py3 imports
from random import sample

try:
    import grp
    import pwd
except BaseException:
    pass


def is_machine_up(machine, sshok=False, timeout=30):
    """
    Pings the specified machine and returns a boolean indicating whether
    the machine is alive or not.
    Set vepok=True: Check if machine can run vep ok.
    """
    msg = SystemCall("ping -c 1 " + machine).run_outonly()
    if 'packet loss' in msg:
        if "100% packet loss" in msg:
            return False
        else:
            # At this point, ping is a success.
            if sshok:
                # ssh to the machine and do a df
                try:
                    with Timeout(timeout, Exception):
                        msg = SystemCall("ssh %s df /tmp" % machine).run_outonly()
                        return bool('Mounted on' in msg)
                except Exception:
                    return False

            return True    # Success
    else:
        return False


def ping_host(host, attempts=5):
    """
    Pings the specified host a certain number of times and returns average latency
    """

    msg = SystemCall("ping -c %s %s" % (attempts, host)).run_outonly()
    match = re.search(r"rtt min\/avg\/max\/mdev\s+=\s+\d+\.\d+\/(\d+\.\d+)\/.+\s(\w+)\s*$", msg)

    # matched avg ping, return time in specified units
    if match:
        return match.group(1) + match.group(2)
    else:
        return False


def fullcmdline(with_exec=False):
    """
    Returns the full commandline (name of script not included) and
    adds single/double quotes as necessary.
    Using plain ' '.join(sys.argv[1:]) will have problem with space
    single quote or double quote inside args.
    Set with_exec to True to return full path to executable as well
    """
    if with_exec:
        return "%s %s" % (CALLERBIN, " ".join(putquotes(sys.argv[1:])))

    return " ".join(putquotes(sys.argv[1:]))


def is_netbatch():
    """
    Looks at the current ENV vars to determine whether this process is running in netbatch or an
    interactive shell.
    :return: False if in an interactive shell, True if in netbatch
    """
    if '__NB_CLASS' not in os.environ:
        return False
    if os.environ.get('__NB_CLASS', "").endswith('vnc'):
        return False
    if 'interactive' in os.environ.get('__NB_QUEUE', ""):
        return False
    if os.environ.get('__NB_POOL', "").endswith('ion'):
        return False
    if '__NB_INTERACTIVE_SESSIONID' in os.environ:
        return False

    return True


def get_calling_stack(pid, pid_dir='/proc'):
    """
    Recursively checks the /proc/ directory to find the cmdlines of the processes
    that call the passed in pid and return the list as an array reference.
    The name associated with the passed in PID will be the first entry in the
    returned list.

    :param pid: Unix Process ID to find the caller stack of
    :param pid_dir: Unix dir to find process files in. Defaults to /proc. Can be overridden for unit tests.
    :returns: array ref containing just the names of the calling scripts, passed in PID
        name will be the first entry.  Will be empty if the PID is the shell (nothing
        left to find!)
    """
    stack = []

    # Exit out if an invalid pid is provided
    if pid is None:
        return stack

    # Find the name of the process
    process_name = None
    proc_dir = join(pid_dir, str(pid))
    cmdline_file = join(proc_dir, 'cmdline')

    # blacklist - Don't record items in the blacklist, stop parsing this line but keep looking for more parents.
    #             Sometimes our own tools create shell scripts that we still want to find that grandparent
    # interpreters - Skip this individual string, keep parsing same line for the real exe name
    # stoplist - You have reached 'root' or the base ION executable.  Stop looking completely.
    blacklist = ['xterm', 'ionshell', 'konsole']
    interpreters = [r'^perl[\d\.\-(threads)]*$', r'^python[\d\.]*$', '^-', '^java', '^tcsh', '^csh', '^bash', '^sh$']
    stoplist = [r'nbjobleader\.out', '^sshd2', 'loginsh', r'startSession\.pl']

    if exists(cmdline_file):
        process_cmdline = File(cmdline_file).read().replace('\0', ' ')  # remove meta characters
        found_black = False

        # Open the process status file to pull out the parent info
        parent_pid = None
        status_file = join(proc_dir, 'status')
        if exists(status_file):
            for line in File(status_file).read().split('\n'):
                m = re.search(r"PPid:\s+(\d+)\s*$", line)
                if m:
                    parent_pid = int(m.group(1))

        # Grab the first path that isn't Perl/Python interpreter or argument
        for field in process_cmdline.split():
            exe_name = basename(field)
            found_interpreter = False

            # Check for Perl/Python type of interpreters, move on to next string if found
            for interp_regex in interpreters:
                if re.search(interp_regex, exe_name):
                    found_interpreter = True
            if found_interpreter:
                continue

            # Check for black list items like shells. Stop looking, don't record, but keep gathering parents
            for black_regex in blacklist:
                if re.search(black_regex, exe_name):
                    found_black = True
            if found_black:
                break

            # Check for top-level callers like root or ION. Stop looking and do not look for more parents
            for stop_regex in stoplist:
                if re.search(stop_regex, exe_name):
                    # Time to leave, don't return anything
                    return stack

            # Only grab the first one seen.
            process_name = exe_name
            break

        # Found a Valid process, update stack, use the parent process id and get parent stack
        if process_name is not None:
            # Add the name of the current process, recursively call for the parent info
            stack.append(process_name)
        if parent_pid is not None and parent_pid != 1:
            parent_stack = get_calling_stack(parent_pid, pid_dir)
            stack.extend(parent_stack)

    return stack


def untar(tarfname, dest, option='r:gz'):
    """
    tarfile wrapper so that the following warning will go away:
    Python 3.14 will, by default, filter extracted tar archives and reject files or modify their metadata. Use the filter argument to control this behavior.

    :param tarfname: tar file
    :param dest:
    :param option: optional string, default is gz
    :return: None
    """
    from .disk import mkdirs
    import tarfile

    mkdirs(dest)
    with tarfile.open(tarfname, option) as tar:
        try:   # pragma: no cover   (default is older version)
            # Use this first - newer pythong version
            tar.extractall(path=dest, filter='fully_trusted')
        except TypeError:
            # backwards compatibility
            tar.extractall(path=dest)


def vmsize(d="VmSize"):
    """
    Return VmSize from /proc/<pid>/status file. Returns '0 kB' if not found
       example: print vmsize()    # Output: 55656 kB
    """
    try:
        res = File(os.path.join('/proc', str(os.getpid()), 'status')).read()
    except BaseException:     # pragma: no cover    (safety check)
        res = ""
    valid = "VmPeak VmSize VmData".split()
    if d not in valid:
        raise Exception("[%s] is invalid. It must be one of %s" % (d, valid))
    if regex(d + r'[\s\:]+(.*)', res, name='vmsizefunc'):
        return group(1, name='vmsizefunc')
    return "0 kB"                            # pragma: no cover   (fail safe only!)


class TarAdd:

    def __init__(self, tarfname, folder, exclude=None):
        """
        Create a tar file with exclude folder or files

        :param tarfname: tarfilename
        :param folder: folder or files to tar
        :param exclude: list of folders or files to exclude. Example: ['.git', 'complete_tp.tar.gz']
        """
        import tarfile
        tar = tarfile.open(tarfname, "w:gz")

        if exclude:
            self.excludes_dirs = tuple(f'{folder}/{x}/' for x in exclude)  # folder: trailing slash match
            self.excludes_files = [f'{folder}/{x}' for x in exclude]  # file: exact name match
            tar.add(folder, filter=self._exclude)
        else:
            tar.add(folder)

        tar.close()

    def _exclude(self, tarinfo):
        if tarinfo.name.startswith(self.excludes_dirs):
            return None  # Exclude directory
        if tarinfo.name in self.excludes_files:
            return None  # Exclude exact file
        return tarinfo


class FromSysArgv:
    """
    Container for various routines that deal with sys.argv directly
    Note: full arg names provided by user is needed for these functions to work
    Only use this class when OPT is not available yet.
    Use Args() and OPT for normal argument handling.
    """

    @classmethod
    def single(cls, option):
        """
        Returns a single sys.argv value given option
        option is '-serev' for example
        if no value is provided, then it returns empty string
        """
        tokens = sys.argv + ['']   # to avoid index error
        for idx, token in enumerate(tokens):
            if token != option:
                continue
            return tokens[idx + 1]
        return ''

    @classmethod
    def multi(cls, option):
        """
        Returns a a list of sys.argv value given option
        option is '-serev' for example
        if no value is provided, then element is empty string
        """
        tokens = sys.argv + ['']   # to avoid index error
        res = []
        for idx, token in enumerate(tokens):
            if token != option:
                continue
            res.append(tokens[idx + 1])
        return res


class MaxVMsize:
    """
    A class to monitor the vmsize of the script. It will spawn a child process.
    Invoke this class early on the script, Use context manager (required).

    Example:
    with MaxVMsize() as vm:
        call_your_routine()
        print 'Max VMsize:', vm.get_maxvmsize()
    """

    def __init__(self, sleepn=1):
        """
        sleepn is sleep in seconds for the monitor before getting the vmsize
        """
        self.sleep = sleepn
        self.pid = os.getpid()

    def _invoke_child(self):
        self.p = multiprocessing.Process(target=self._childvmsize, name='Childvmsize')
        self.p.start()
        # ==== at this point, there are two processes running

    def _childvmsize(self):  # pragma: no cover  (separate process, coverage cannot catch)
        self.file = os.path.join('/proc', str(self.pid), 'status')
        while True:
            if not os.path.exists(self.tname):
                exit(0)    # Done!
            self._getvm()
            time.sleep(self.sleep)

    def _getvm(self):  # pragma: no cover  (separate process, coverage cannot catch)
        res = File(self.file).read()
        if regex(r'VmData[\s\:]+(.*)', res):
            open(self.tname, "a").write("%s %s vmsize\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), group(1)))
            # print os.getpid(),group(1)

    def close(self):
        """Close the child process"""
        print("Max VMSize:", self.get_maxvmsize())
        while self.p.is_alive():
            if os.path.exists(self.tname):
                os.unlink(self.tname)
            time.sleep(self.sleep + 0.5)
        self.tobj.close()

    def get_maxvmsize(self):
        """Returns the largest vmsize"""
        if not hasattr(self, 'tname'):
            raise Exception("Error on MaxVMsize usage: MaxVMsize must always be run from a context manager")
        m = set([0])
        for line in open(self.tname):
            if regex(r'(\d+) \w+ vmsize', line, name='maxvm'):
                m.add(int(group(1, name='maxvm')))
        return max(m)

    def __exit__(self, *arg):
        self.close()

    def __enter__(self):
        self.tobj = TempName()
        self.tname = self.tobj.name()
        open(self.tname, "a").write("PID %s\n%s %s\n" % (self.pid, sys.argv[0], fullcmdline()))
        self._invoke_child()
        return self


class SystemCall:
    """
    Easy to use system call interface (via subprocess).
    Usage:
        result            = SystemCall(cmd).run_outonly()
        ecode, result     = SystemCall(cmd).run_outtxt()
        ecode             = SystemCall(cmd).run_outfile(outfile)
        ecode             = SystemCall(cmd).run()          # ecode only
        ecode, sout, serr = SystemCall(cmd).run_sout_serr()
        <iterobj>         = SystemCall(cmd).run_stream()   # use return_ecode() to get exit code

    Streaming Usage:
        syscall = SystemCall(cmd)
        for line in syscall.run_stream():
            print line
        ecode = syscall.return_ecode()

    Can't do |, > or & directly in SystemCall()

    To execute:
        ps uaxw | egrep -i \"(%s|%s)\";crontab -l

    Put this in a tempfile, add "#!/usr/intel/bin/tcsh" as first line, make it executable, then execute this tempfile in SystemCall.
    """

    def __init__(self, cmd, exe=False, disp=False, cwd=None):
        """
        :param cmd: Command string or list
        :param exe: Set to True for python
        :param disp: Set to True to log cmd and output
        :param cwd: Change to this directory before executing the command
        """
        if isinstance(cmd, str):
            if IS_UNIX:
                self.cmd = shlex.split(cmd)
            else:     # pragma: no cover    windows
                self.cmd = shlex.split(cmd.replace('\\', '/'))
                if self.cmd[0].endswith('.py'):
                    self.cmd = ['python'] + self.cmd
        else:
            self.cmd = cmd

        # display
        self.disp = disp
        if self.disp:
            log.info("CMD: %s" % ' '.join(putquotes(self.cmd)))

        # exe processing
        if exe:
            self.cmd = [sys.executable, '-u'] + self.cmd

        # attributes
        self._pr = None
        self._ecode = None     # saved exitcode
        self.cwd = cwd

    @classmethod
    def _subprocess_call(cls, final, stdout, stderr, is_popen=True, cwd=None):
        """
        Child routine. Calls subprocess.
        :param final: final command string
        :param stdout: stdout object
        :param stderr: stderr object
        :param is_popen: Use Popen if True, else call
        :param cwd: Change to this directory before executing the command
        :return: subprocess object
        """
        try:
            # Windows: wrap with 'cmd /c' so builtins (echo, dir, copy, ...) work
            if IS_WIN:
                if isinstance(final, list):
                    final = ['cmd', '/c'] + final
                else:
                    final = ['cmd', '/c', final]
            if is_popen:
                return subprocess.Popen(final, stdout=stdout, stderr=stderr, universal_newlines=True, errors='replace', cwd=cwd)
            else:
                return subprocess.call(final, stdout=stdout, stderr=stderr, universal_newlines=True, cwd=cwd)

        except OSError as e:
            suggestion = ("Suggestion: Try a different machine other than %s. "
                          "If problem persist, submit tvpvhelp and include the two machines that you tried. "
                          "" % HOSTNAME)
            raise OSError("%s: [%s]\n%s" % (e, ' '.join(final) if isinstance(final, list) else str(final), suggestion))

    def return_ecode(self):
        """
        Returns the errorcode of executed command.

        Usage:
            call = SystemCall(cmd)
            call.run()
            print call.return_ecode()

        :return: ecode of the call
        :rtype: int
        """
        if self._ecode is None:
            if self._pr is None:
                raise Exception("Error: return_ecode() is called but actual system call execute was not called. "
                                "Call the execute routines first.")
            else:
                self._ecode = self._pr.wait()

        return self._ecode

    def run_outfile(self, outfile):
        """
        Executes cmd and Writes interleaved stdout and stderr in a given outfile.

        :param outfile: Output filepath string
        :return: ecode
        :rtype: int
        """
        with open(outfile, 'w') as fh:
            pr = self._subprocess_call(self.cmd, stdout=fh, stderr=fh, cwd=self.cwd)
            self._ecode = pr.wait()

        if self.disp:
            with open(outfile, errors='replace') as tn:
                result = to_ascii(tn.read()).rstrip()

            log.info("===== Stdout+Stderr:")
            if result:
                log.info(result)
            log.info("===end of stdout+stderr===")

        return self._ecode

    def run_outtxt(self, interleaved=True):
        """
        Executes cmd and returns interleaved stdout and stderr in a result string.

        :return: ecode, result
        :rtype: (int, str)
        """
        if interleaved:
            with TempName(name=True) as tname:
                self.run_outfile(tname)
                with open(tname, errors='replace') as tn:
                    result = tn.read()
        else:
            _, sout, serr = self.run_sout_serr()
            result = f'{sout}\n{serr}'

        return self._ecode, result.rstrip()

    def run_outonly(self) -> str:
        """
        Executes cmd and returns interleaved stdout and stderr in a result string.

        :return: result str
        """
        return self.run_outtxt()[1]

    def run_sout_serr(self, timeout=None):
        """
        Executes cmd
        :return: ecode, sout, serr
        :rtype: (int, str, str)
        """
        pr = SystemCall._subprocess_call(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.cwd)

        if timeout:
            try:
                sout, serr = pr.communicate(timeout=timeout)
                self._ecode = pr.returncode
            except subprocess.TimeoutExpired:
                sout = ''
                serr = f'TIMEOUT at {timeout} secs'
                self._ecode = 1
        else:
            sout, serr = pr.communicate()
            self._ecode = pr.returncode

        if self.disp:
            log.info("===== Stdout:")
            if sout:
                log.info(sout.rstrip())
            if serr:
                log.info("===== Stderr:")
                log.info(serr.rstrip())
            log.info("===end of stdout or stderr===")

        return self._ecode, sout.rstrip(), serr.rstrip()

    def run_stream(self):
        """
        Iterator: executes cmd and yields combined stdout+stderr
        Get the errorcode by obj.return_ecode()
        :yield: stdout & stderr message (EOL char stripped)
        """
        assert not self.disp, "Cannot use disp=True on run_stream()"

        # This is unbuffered output (realtime display, but slow). Using pr.stdout alone is buffered (fast version).
        # It's ok not to use context manager for this since subprocess is killed when parent is killed.
        # Also, subprocess will wait/halt if buffer is full.
        self._pr = self._subprocess_call(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=self.cwd)
        for item in iter(self._pr.stdout.readline, ""):
            yield item.rstrip()

    def run(self, disp=False, exitout=None):
        """
        Executes cmd, disposing stdout and stderr results.
        :param disp: Set to True to print stdout and stderr
        :param exitout: Set to <error_message_string>, which will be raised as Exception if failure happens during execution
        :return: ecode
        :rtype: int
        """
        msg = "Error: args to run() is exitout=%s. It should be exitout=<message>" % exitout
        assert not isinstance(exitout, bool), msg

        if disp:
            # This usage is purely backwards compatible
            if not self.disp:
                log.info("CMD: %s" % ' '.join(putquotes(self.cmd)))
            self.disp = True
            _, sout, serr = self.run_sout_serr()
        else:
            assert not self.disp, "Cannot use SystemCall(disp=True) on run(). Use run(disp=True) or run_outtxt() instead."
            devnull = '/dev/null' if IS_UNIX else 'NUL'
            pr = SystemCall._subprocess_call(self.cmd, stdout=open(devnull, "w"), stderr=open(devnull, "w"), cwd=self.cwd)
            self._ecode = pr.wait()

        # If exitout is provided, then raise the provided message
        if exitout and self._ecode:
            raise Exception(exitout)

        return self._ecode


class BgCmd:
    """
    Class to manage systems calls launched in background (unix only).
    Number of parallel jobs run is number of cpu.
    Will wait for a job to be freed up before launching next one when all cores are filled
    This class will not consider existing cpu load yet.
    If you want to consider existing cpu load, then set ncpu to the value.

    Example:
        bg = BgCmd()
        bg.send('somescript')                 # call this several times for all the commands
        bg.launch_and_finish(self.process)    # self.process is your own func. It takes in job as argument.

    job attributes:
         job.name    # name of job
         job.cmd     # cmd list
         job.sout    # filename of std output
         job.serr    # filename of std error
         job.status  # Enum of: WAIT, DONE, WIP
         job.pr      # Subprocess object. job.pr.pid is the process id #
         job.seqid   # Sequence id
         job.elapsed # completion time
         job.ecode   # exit code / return code (not yet complete is -1)
    """
    STATUS = Enum(WAIT=hash("WAIT"),
                  DONE=hash("DONE"),
                  WIP=hash("WIP"))    # prevent using numbers directly

    def __init__(self,
                 ncpu=multiprocessing.cpu_count(),
                 launchlistmax=10,
                 startid=0,
                 deltmpdir=True,
                 min_load_add=1,
                 timeout=157680000):     # five year timeout, aka, no-time-out

        self.ncpu = ncpu       # number of cpu
        self.jobs = {}         # dictionary of jobs
        self.maxid = startid    # incremental number for id
        self.tdir = TempDir(delete=deltmpdir)     # temporary dir for output of launches
        self.launchlist = deque(maxlen=launchlistmax)   # launched list order (used in unittest)
        self.runninglist = set()       # set of cmd lines that is running
        self.timeout = timeout
        self._cpu_count = multiprocessing.cpu_count()
        self.min_load_add = min_load_add

    def send(self, cmd, listargs=None, name=None, seqid=None, timeout=None):
        """
        Adds cmd in the queue.
        cmd can have spaces. listargs is optional which is appended to the cmd.
        name is the job name.
        seqid is a number. The lower the number the higher the priority.
        timeout is a number of seconds. Will default to self.timeout if not specified
        """
        self.maxid = self.maxid + 1
        job = DictDot()

        # check the name
        # name
        if name is None:
            job.name = "r%s" % self.maxid
        else:
            if not regex(r'^[\w\.-]+$', name):
                raise Exception("Name %r must not contain special characters" % name)
            if name in self.jobs:
                raise Exception("Name %r already exist in job names. Cannot have duplicate name" % name)
            job.name = name

        # get command line
        if IS_UNIX:
            job.cmd = shlex.split(cmd)
        else:    # pragma: no cover
            job.cmd = cmd    # as-is for windows

        if listargs is not None:
            # Cannot use shlex.split() in windows because of space in paths.
            assert IS_UNIX or isinstance(cmd, list), f'Input cmd={cmd} must be a list to use with listargs={listargs}'

            if isinstance(listargs, str):
                job.cmd.append(listargs)
            else:
                job.cmd.extend(listargs)

        # assign the rest of the attributes
        if seqid is None:
            job.seqid = self.maxid
        else:
            job.seqid = seqid
        job.sout = join(self.tdir.name(), "sout.%s" % job.name)
        job.serr = join(self.tdir.name(), "serr.%s" % job.name)
        job.status = self.STATUS.WAIT
        job.pr = None    # none yet
        job.ecode = -1      # Cannot use None, since None is a False, and False ecode means success
        job.elapsed = time.time()
        job.timeout = timeout if timeout else self.timeout

        self.jobs[job.name] = job
        return job.name

    def run(self):
        """
        Launches the commands in background until all cpu's are full
        Will return False if all jobs are exhausted
        Will return True if cpu is full and more jobs to run
        """
        if IS_UNIX:
            load = os.getloadavg()[0]
        else:       # pragma: no cover
            load = 1     # There is no simple equivalent on windows

        launched = 0             # launched on this run
        while True:
            for target in sorted(self.all(), key=lambda j: j.seqid):
                if target.status == self.STATUS.WAIT:
                    break       # at least one job is running
            else:
                return False    # all jobs are done

            # Return if all cpu are full
            if self.count() >= self.ncpu:
                return True

            # Return if machine is overloaded, do not launch new job
            # Validation run: /nfs/pdx/disks/mdo_tvpv_019/jqdelosr/nhm_userdir/analysis/LoadAware/BgCmd/res1 & res2,
            # using expt.py
            if self.count() > 0 and (load + launched + self.min_load_add) >= self._cpu_count:
                return True

            # launch it
            launched += 1
            self.launchlist.append(target.name)
            pr = subprocess.Popen(target.cmd, stdout=open(target.sout, "w"), stderr=open(target.serr, "w"), universal_newlines=True)
            target.pr = pr
            target.status = self.STATUS.WIP
            target.elapsed = time.time()
            self.runninglist.add(" ".join(putquotes(target.cmd)))

    def count(self):
        """
        Return the count of number of running jobs
        Update the jobs to DONE state
        """
        # refresh first
        for job in self.all():
            if job.status == self.STATUS.WIP:
                timeout = job.timeout if 'timeout' in job else self.timeout
                # if (time.time()-job.st)>0.10 and (not job.pr.poll() is None):
                if not job.pr.poll() is None:

                    # job is complete
                    job.ecode = job.pr.returncode
                    job.status = self.STATUS.DONE
                    job.elapsed = time.time() - job.elapsed
                    self.runninglist.discard(" ".join(putquotes(job.cmd)))    # remove from runninglist

                elif time.time() - job.elapsed > timeout:

                    # job has timedout, kill it
                    job.ecode = 1   # forced error
                    job.status = self.STATUS.DONE
                    job.elapsed = time.time() - job.elapsed
                    job.pr.terminate()
                    File(job.serr).touch("\nTIMEOUT at %s Secs!\n" % job.elapsed)    # add a timeout message in stderr
                    self.runninglist.discard(" ".join(putquotes(job.cmd)))    # remove from runninglist

        cnt = len([job.name for job in self.all() if job.status == self.STATUS.WIP])
        return cnt

    def queue(self, done=False, wip=False, wait=False):
        """
        Iterator to return jobs depending if done, wip or wait
        Set done=True to return completed jobs
        Set wip =True to return running jobs
        Set wait=True to return jobs on queue
        """
        for job in self.all():
            if done and job.status == self.STATUS.DONE:
                yield job
            elif wip and job.status == self.STATUS.WIP:
                yield job
            elif wait and job.status == self.STATUS.WAIT:
                yield job

    def all(self):
        """
        Iterator for all the jobs
        """
        for job in list(self.jobs.values()):   # make a copy
            yield job

    def purge(self, jobname):
        """
        Purge (remove from memory) the job with name=jobname
        """
        job = self.get(jobname)

        if job.status == self.STATUS.WIP:
            raise Exception("%r cannot be deleted since it is still WIP/Running" % jobname)

        File(job.sout).unlink()   # delete sout
        File(job.serr).unlink()   # delete serr
        del self.jobs[jobname]    # delete the entry

    def get(self, jobname):
        """
        Returns the job object with name=jobname
        """
        if jobname not in self.jobs:
            raise Exception("%r is not a valid job name" % jobname)

        return self.jobs[jobname]

    def close(self):
        """
        Delete the temporary directory
        """
        self.tdir.close()

    def is_running(self, cmd):
        """Returns True if cmd is still running"""
        return cmd in self.runninglist

    def is_job_exist(self, name):
        """Returns True if job name exist"""
        return name in self.jobs

    def launch_and_finish(self, func, disp=True):
        """
        Launch the jobs, process completed runs and finish all
        Calls func(job) to process the jobs
        """
        self._is_disp = disp

        # Run the jobs
        while self.run():
            for job in self.queue(done=True):   # these are completed jobs
                func(job)
                self.purge(job.name)
            time.sleep(0.05)

        # Wait for all jobs to complete
        for job in self.queue(wip=True):
            self.disp("Waiting for {nam}, pid={p}".format(nam=job.name, p=job.pr.pid))

        once = TagOnce()
        while self.count() > 0:
            for job in self.queue(done=True):
                if once(job.name):
                    self.disp("{} is done".format(job.name))
            time.sleep(0.2)

        # Process the rest of completed jobs
        for job in self.queue(done=True):
            func(job)
            self.purge(job.name)

    def disp(self, msg):
        """Print msg in stderr"""
        if self._is_disp:
            sys.stderr.write('-i- BgCmd: %s\n' % msg)


def is_exe(cmd):
    """
    Returns True if cmd is a valid executable.
    Unix 'which' will be called
    """
    return SystemCall("which " + cmd).run_outtxt()[0] == 0


def pjoin(*args):
    """
    pjoin - 'path join'. os.path.join (space separated string)

    Example:
    >>> pjoin('a', 'b c d', 'e f')
    /a/b/c/d/e/f
    """
    arr = chain(*list(x.split() for x in args))
    return join(*arr)


def getcaller():
    """
    Returns the abspath of executable caller
    """

    # caller is eclipse, when executed as unittest
    if iseclipse_ut():  # pragma: no cover
        return os.path.abspath(sys.argv[1])

    return os.path.abspath(sys.argv[0])


def tmpdir():
    """
    Returns the tmp directory
    """
    if IS_UNIX:
        return "/tmp"
    else:
        return os.environ['TEMP']


def getuid():
    """
    Returns the userid number for linux and username for windows
    """
    if IS_UNIX:
        return os.geteuid()
    else:  # pragma: no cover
        import getpass
        return getpass.getuser()


def is_idsid_valid(idsid):
    """
    This function checks to make sure the idsid exists in UNIX
    Returns True if user exists, False otherwise
    """
    # Don't use a system command, find the user's home dir to verify
    result = expanduser('~{}'.format(idsid))

    return bool(result.startswith('/'))


def is_gid_valid(gid):
    """
    This function checks to make sure a groupID (gid) is valid
    Returns True if the group exists, False otherwise
    """
    result = None
    try:
        import grp
        result = grp.getgrgid(gid)
    except KeyError as e:
        pass
    return bool(result)


def iseclipse_ut():
    """Returns True if called from eclipse as unittest"""
    return 'plugins/org.python.pydev' in sys.argv[0]


def group_names():
    """
    Return the list of group names
    """
    res = []
    for id in os.getgroups():
        try:
            import grp
            res.append(grp.getgrgid(id).gr_name)
        except BaseException:     # For some reason, netbatch adds some junk groups
            pass
    return res


def cdis(idsid, key='DomainAddress'):
    """
    Returns Intel dictionary info given idsid
    Uses cdislookup
    """
    cmd = '/usr/intel/bin/cdislookup -i %s' % idsid
    ecode, sout, serr = SystemCall(cmd).run_sout_serr()
    if ecode:
        raise Exception("Error executing [%s]" % cmd)
    res = DictDot()
    for line in sout.split('\n'):
        if '=' in line:
            k, v = line.split('=', 2)
            if k.strip() == key:
                return v.strip()
    return ''   # empty string, if not found


def homedir(user=None):
    if user is None:
        user = USERNAME
    return expanduser('~%s' % user)


def which(exe):
    """
    Python clone of POSIX's /usr/bin/which
    Copied from https://gist.github.com/SEJeff/2576984, with minor modification.
    """
    (path, name) = os.path.split(exe)
    if os.access(exe, os.X_OK):
        return exe
    for path in os.environ.get('PATH').split(os.pathsep):
        full_path = os.path.join(path, exe)
        if os.access(full_path, os.X_OK):
            return full_path

    return None


def check_valid_user(user=None):
    """Exits with error if invalid user"""
    if user is None:
        return 1

    try:
        import pwd
        pwd.getpwnam(user)
    except BaseException:
        raise Exception('%s is not a valid user' % user,
                        'Pls provide a valid user name.')


def nfs_standard_path(path, check_exist=False):
    """
    Given a path, return the path with the
    specific site directory (ex. pdx, iil, png) replace by "site".

    Ex.
        Input:  /nfs/pdx/disk
        Outout: /nfs/site/disk

    :param check_exist: Boolean flag to determine whether or not to
    check for existance before translating the path name.
    """

    if not path:
        raise Exception("Invalid value: %s for path. Please provide a valid path." % path)

    if check_exist:
        if not os.path.exists(path):
            raise Exception("Provided path: %s does not exist." % path)

    # remove extra '/' at end
    if path.endswith('/'):
        path = path[:-1]

    return re.sub(pattern=r"/nfs/\w+", repl="/nfs/site", string=path)


class MyException(Exception):
    '''For use with Timeout, since Timeout will raise an exception upon timeout'''
    pass


def is_alive_ssh(machine, timeout=15, native_timeout=False, freegb=0, dfdir='/tmp'):
    """
    Returns True if machine is alive, via ssh
    machine: machine to test is up
    timeout: how long to wait for a response
    native_timeout: Use ssh's timeout mechanism (verses with Timeout)
    freegb: number of free gigbytes required.  It is possible gdf will return
            another scale (K or M), but this is only matching G
    dfdir: Path to test 'df' free against freegb.  Default is /tmp
    """

    if native_timeout:
        if MachineInfo().sles_version() == 12:
            command = 'ssh -o ConnectTimeout={} {} /usr/intel/bin/gdf -h {}'.format(timeout, machine, dfdir)
        else:
            command = 'ssh -o ConnectionTimeout={} {} /usr/intel/bin/gdf -h {}'.format(timeout, machine, dfdir)
        try:
            errcode, out = SystemCall(command).run_outtxt()
        except Exception as e:
            log.info(" cmd failed: %s, e: %s" % (command, e))
            return False    # not alive
        if errcode:
            log.info(" cmd failed: %s with %s" % (command, out))
            return False    # not alive
    else:
        with Timeout(timeout, MyException):
            command = 'ssh {} /usr/intel/bin/gdf -h {}'.format(machine, dfdir)
            try:
                errcode, out = SystemCall(command).run_outtxt()
            except MyException as e:
                log.info(" is_alive_ssh Exception: %s" % e)
                return False    # not alive
        if errcode:
            log.info(" cmd: %s failed: ecode %s, %s" % (command, errcode, out))
            return False    # not alive

    if freegb > 0:
        for output in out.split('\n'):
            if regex(r'\S+\s+\d+\.?\d?[KMGTkmgt][bB]?\s+\d+\.?\d?[KMGTkmgt][bB]?\s+(\d+\.?\d?)([KMGTkmgt])[bB]?\s+\d+[\%]', output):  # would need to fake df output to cover mismatch
                found_freegb = float(regex.group(1))
                found_scale = str(regex.group(2))

                if found_scale == 'K' or found_scale == 'k':
                    found_freegb = int(found_freegb / (1024 * 1024))
                elif found_scale == 'M' or found_scale == 'm':
                    found_freegb = int(found_freegb / 1024)
                elif found_scale == 'T' or found_scale == 't':
                    found_freegb = int(found_freegb * 1024)

                if found_freegb > freegb:
                    log.dev("Host: %s: %s > %s, return True, line: %s" % (machine, found_freegb, freegb, output))
                    return True
                else:
                    log.info("Host: %s: %s < %s, return False, line: %s" % (machine, found_freegb, freegb, output))
                    return False

            elif regex(r'Filesystem\s+', output):
                pass
            else:
                log.info("Host: %s: mismatch line: %s" % (machine, output))

        log.info("Requested freegb: %s, didn't find required space in\n%s" % (freegb, out))
        return False

    mount_in_out = bool('Mounted on' in out)
    if mount_in_out:
        return True
    else:
        log.info(" 'Mounted on' not found in %s" % out)
        return False


def get_caller_exe(_ut_cmdline=None):
    """
    :return: The caller executable (fullpath). Returns empty string if none found.
    """
    parentid = os.getppid()
    if _ut_cmdline:
        cmdline = _ut_cmdline
    else:
        cmdline = File('/proc/%s/cmdline' % parentid).read().split('\0')
    # print '%r' % cmdline
    for item in cmdline:
        if os.path.basename(item).startswith(('python', 'perl', 'pyston')):   # ignore python or perl interpreters
            continue
        if item in ('-csh', '-sh'):
            return item      # return as-is
        if item.startswith('-'):     # ignore args
            continue
        return item

    return ""


def is_vnc_machine():
    """
    :return: True if current machine is vnc
    """
    # This algo is from crichmon
    return bool('vnc' in os.environ.get('__NB_CLASS', '').lower())


class RunChild(multiprocessing.Process):
    """
    A context Manager extension to multiprocessing.Process
    It will guarantee that child process has completed.

    Timeout during context manager closure is 60 seconds (default),
      then it will terminate child process.

    If context manager is not needed, then use multiprocessing.Process directly.

    Arguments: All kwargs of multiprocess.Process applies. Below are additional arguments:
       timeout:<secs>    # set maximum wait (in Sec) for the child to finish before it is killed

    Usage:
    with RunChild(timeout=10, target=foo, args=(arg1,)) as p:   # set timeout to 10 sec
        <some code>

    with RunChild(target=foo, args=(arg1,)) as p:
        pass   # Wait for child to be complete (default timeout is 60 sec)

    with RunChild(target=foo) as vm:
        p.terminate()           # Kill the child

    Common multiprocessing methods:
        p.terminate()           # terminate the child forcefully
        p.is_alive()            # returns True if child is still alive
        p.join([timeout_secs])  # wait for the child to finish. If timeout exceeded, then p.join() continues, child process is still alive
    """

    def __init__(self, *args, **kwargs):
        # set the timeout
        if "timeout" in kwargs:
            self.cm_timeout = kwargs['timeout']    # timeout during close()
            del kwargs['timeout']
        else:
            self.cm_timeout = 60     # default timeout, in seconds

        self.cm_terminate = False    # Indicator if process was forcefully terminated

        multiprocessing.Process.__init__(self, *args, **kwargs)

    def close(self):
        """Close the child process"""
        self.join(self.cm_timeout)
        if self.is_alive():
            self.cm_terminate = True
            self.terminate()
            for i in range(60 * 10):   # max of 60 seconds
                if not self.is_alive():
                    break
                time.sleep(0.1)
            else:  # pragma: no cover      # Safety check only
                raise Exception("Process id %s cannot be terminated." % self.pid)

    def is_force_terminate(self):
        """
        Returns True if process is force-terminated (that is, child did not exit gracefully)
        Call this outside of context manager
        """
        return self.cm_terminate

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            self.cm_timeout = 1     # Error occurred so, kill the client job immediately
        self.close()

    def __enter__(self):
        self.start()   # Start the process
        return self

    @classmethod
    def waitready(cls, ready, timeout=10):
        """
        Wait for child process to be ready.
        ready must be a multiprocessing.Value()

        Usage:
            def myfunc(ready):
               # some code
               ready.value = 1
               # some more code

            ready   = multiprocessing.Value('i', 0)   # shared variable
            with RunChild(target=myfunc, args=(ready,)) as p:
                p.waitready(ready)
                <somecode>
        """
        for i in range(10 * timeout):  # 10 seconds max
            if ready.value == 1:
                return
            time.sleep(0.1)
        else:
            raise Exception("Server did not become ready")


class MachineInfo:
    """
    related to /proc/cpuinfo, /proc/meminfo, machine core, memory, number of user and etc
    for vedb class use
    """

    my_cache = CacheThis()

    def __init__(self, cpuinfo="/proc/cpuinfo", meminfo="/proc/meminfo", vmstat="/proc/vmstat", stat="/proc/stat"):
        """Read the info files and put it in var"""
        self.cpuinfo_file = cpuinfo
        self.meminfo_file = meminfo
        self.vmeminfo_file = vmstat
        self.statinfo_file = stat
        self.cpuinfo = File(cpuinfo).read()
        self.meminfo = File(meminfo).read()
        self.sysstat = autodict()

    @classmethod
    def max_pid(self):
        """
        Return the max pid number and length of that number
        should be a 5-6 digit number, but could be 7 on a 64b machine
        """
        max_procs = File('/proc/sys/kernel/pid_max').read().strip()
        pid_length = len(max_procs)
        return max_procs, pid_length

    def machine_type(self, d="model name"):
        """machine model name"""
        if d in self.cpuinfo:
            linelist = list(set(re.findall(d + r'[\s\:]+(.*)', self.cpuinfo)))
            mt = "".join(linelist)
            return mt
        else:
            log.info("cpuinfo contents:\n%s" % self.cpuinfo)
            raise Exception(" No %s in %s" % (d, self.cpuinfo_file))

    def n_physical_cpu(self, d="physical id"):
        '''number of physical cpu in machine'''
        if d in self.cpuinfo:
            npc = len(list(set(re.findall(d + r'[\s\:]+(.*)', self.cpuinfo))))
            return npc
        else:
            return 0

    def n_physical_cores(self, d="siblings"):
        """number of physical cores in machine"""
        if d in self.cpuinfo:
            linelist = list(set(re.findall(d + r'[\s\:]+(.*)', self.cpuinfo)))
            linestr = "".join(linelist)
            npc = int(linestr) * self.n_physical_cpu()
            return npc
        else:
            npc = self.n_logical_cores()
            return npc

    def n_logical_cores(self, d="processor"):
        """number of logical cores in machine"""
        if d in self.cpuinfo:
            nlc = len(re.findall(d + r'[\s+\:]+(\d+)', self.cpuinfo))
            return nlc
        else:
            log.info("cpuinfo contents:\n%s" % self.cpuinfo)
            raise Exception(" No %s in %s" % (d, self.cpuinfo_file))

    def uptime_load(self):
        """top info in machine"""'/proc/meminfo'
        ul = SystemCall('uptime').run_outonly()
        return ul

    def n_users(self):
        """number of users in machine"""
        nu = int("".join(re.findall(r'\s(\d+)\suser', self.uptime_load())))
        return nu

    def machine_memory_gb(self, d="MemTotal"):
        """machine memory in GB"""
        if d in self.meminfo:
            # mmdb = int("".join(re.findall(d + r'[\s\:]+(\d+)\skB', self.meminfo))) // 1000000
            # mmdb = int("".join(re.findall(d + r'[\s\:]+(\d+)\skB', self.meminfo))) / 1000000
            mmdb = int("".join(re.findall(d + r'[\s\:]+(\d+)\skB', self.meminfo))) // (1024 * 1024)
            return mmdb
        else:
            log.info("meminfo contents:\n%s" % self.meminfo)
            raise Exception(" No %s in %s" % (d, self.meminfo_file))

    def total_run_time(self, sw):
        """Return Total execution time"""
        return sw(pretty=False)

    def get_history(self):
        """user, host, date"""
        (year, month, day, hour, minn, sec, dummy, dummy, dummy) = time.localtime(time.time())
        timestring = "%02d/%02d/%04d %02d:%02d:%02d" % (month, day, year, hour, minn, sec)
        h = DictDot()
        h.user = USERNAME
        h.host = HOSTNAME
        h.date = timestring
        h.timesec = int(time.time())
        return h

    def vmsize_kb(self):
        """Return the vmsize from the process file, in kb"""
        return self.getkb(vmsize())

    def vmdata_kb(self):
        """Return the vmdata from the process file, in kb"""
        return self.getkb(vmsize('VmData'))

    def vpeak_kb(self):
        """Return the vmpeak from the process file, in kb"""
        return self.getkb(vmsize('VmPeak'))

    def getkb(self, inp):
        """Given a string '0 kB', etc, return an integer value of kb"""
        inp = inp.strip()
        if inp.isdigit():
            return int(inp) // 1024

        try:
            (value, unit) = inp.split()
        except BaseException:
            raise Exception("getkb(): Cannot get unit (kb,mb,gb) from [%s]" % inp)

        if unit.lower() == 'kb':
            return int(value)
        if unit.lower() == 'mb':
            return int(value) * 1024
        if unit.lower() == 'gb':
            return int(value) * 1024 * 1024
        if unit.lower() == 'tb':
            return int(value) * 1024 * 1024 * 1024

        raise Exception("getkb(): Unknown unit [%s] from [%s]" % (unit, inp))

    def sles_version(self, _file_to_read="/etc/SuSE-release"):
        """Returns Suse version (integer), returns 0 if not suse"""
        try:
            suse_release = File(_file_to_read).read()
            return int(re.findall(r"VERSION = (\d+)", suse_release)[0])
        except BaseException:
            return 0

    @my_cache
    def sysname(self, cmd='/usr/intel/bin/sysname'):
        """Return the sysname/<cmd>, non gating"""
        try:
            return SystemCall(cmd).run_outonly()
        except Exception as e:
            return "Error: [%s]" % e

    def statinfo(self):
        for line in File(self.statinfo_file).read().split('\n'):
            yield line

    def SystemStatus(self, mytime=0, sleep=0):
        """
        Collect /proc/stat and /proc/vmstat data and store to self.sysstat.stage.[field], where stage
        is 'pre' or 'post' delay for getting delta values to calculate machine load
        Call the first time with a time value of 0, and capture the time as return value.
        On a subsequent call, pass in that time to store the delta values in the 'post' stage for
        delta calcs for current machine load

        NOTE: code is OS sensitive. See 'man proc' for details related to kernel versions reported values
        """
        core_cnt = 0
        my_sysname = self.sysname()

        stage = 'pre'
        if mytime == 0:
            now = time.time()
            # print " stage %s, now %s" % (stage, now)
        else:
            # sleep until <sleep> seconds after original call, not <sleep> more seconds
            if sleep > 0:
                until = mytime + sleep
                left = until - time.time()
                if left > 0:
                    time.sleep(left)
            None
            now = time.time()
            stage = 'post'
            # print " stage %s, now %s, sleep time %s" % (stage, now, left)

        for line in self.statinfo():
            if regex(r"^cpu\s+", line):
                if '2.6.16' in my_sysname:
                    (cpu, user, nice, system, idle, iowait, irq, softirq, steal) = line.split()
                elif ('3.0' in my_sysname) or ('2.6.24' in my_sysname) or ('4.12' in my_sysname):
                    (cpu, user, nice, system, idle, iowait, irq, softirq, steal, guest, guest_nice) = line.split()
                else:
                    raise Exception(" Unhandled kernel version.  Add condition for %s" % my_sysname)
                self.sysstat[stage]['user'] = user
                self.sysstat[stage]['nice'] = nice
                self.sysstat[stage]['system'] = system
                self.sysstat[stage]['idle'] = idle
                self.sysstat[stage]['iowait'] = iowait
                self.sysstat[stage]['irq'] = irq
                self.sysstat[stage]['softirq'] = softirq
                self.sysstat[stage]['steal'] = steal
                if ('3.0' in my_sysname) or ('2.6.24' in my_sysname):
                    self.sysstat[stage]['guest'] = guest
                    self.sysstat[stage]['guest_nice'] = guest_nice

            elif regex(r"^cpu\d+\s+", line):
                core_cnt += 1
            elif regex(r"^procs_running\s+(\d+)$", line):
                self.sysstat[stage]['procs_running'] = group(1)
            elif regex(r"^procs_blocked\s+(\d+)$", line):
                self.sysstat[stage]['procs_blocked'] = group(1)

        self.sysstat[stage]['cores'] = core_cnt

        for line in File(self.vmeminfo_file).read().split('\n'):
            if regex(r"^pswpin\s+(\d+)$", line):
                self.sysstat[stage]['swapin'] = group(1)
            elif regex(r"^pswpout\s+(\d+)$", line):
                self.sysstat[stage]['swapout'] = group(1)

        for line in File(self.meminfo_file).read().split('\n'):
            if regex(r"^MemTotal:\s+(\d+)\s+kB", line):
                self.sysstat[stage]['memtotal'] = int(group(1))
            elif regex(r"^MemFree:\s+(\d+)\s+kB", line):
                self.sysstat[stage]['memfree'] = int(group(1))
            elif regex(r"^Buffers:\s+(\d+)\s+kB", line):
                self.sysstat[stage]['membuffers'] = int(group(1))
            elif regex(r"^Cached:\s+(\d+)\s+kB", line):
                self.sysstat[stage]['memcached'] = int(group(1))
            elif regex(r"^Active:\s+(\d+)\s+kB", line):
                self.sysstat[stage]['memactive'] = int(group(1))
            elif regex(r"^Inactive:\s+(\d+)\s+kB", line):
                self.sysstat[stage]['meminactive'] = int(group(1))
            elif regex(r"^VmallocUsed:\s+(\d+)\s+kB", line):
                self.sysstat[stage]['vmallocused'] = int(group(1))
            elif regex(r"^SwapTotal:\s+(\d+)\s+kB", line):
                self.sysstat[stage]['swaptotal'] = int(group(1))
            elif regex(r"^SwapFree:\s+(\d+)\s+kB", line):
                self.sysstat[stage]['swapfree'] = int(group(1))

        return now

    def CalcLoad(self, delta=0):
        """
        Calculate how busy the machine is, taking into account memory and swap usage
        """
        self.sysload = autodict()

        for stage in ('post', 'pre'):
            self.sysload[stage]['busy'] = 0
            self.sysload[stage]['idle'] = 0

        for stage in ('post', 'pre'):
            for stat_busy_field in ("user nice system irq softirq steal guest guest_nice").split():
                if not self.sysstat[stage][stat_busy_field]:
                    continue
                self.sysload[stage]['busy'] += int(self.sysstat[stage][stat_busy_field])

            for stat_idle_field in ("idle iowait").split():
                if not self.sysstat[stage][stat_idle_field]:
                    continue
                self.sysload[stage]['idle'] += int(self.sysstat[stage][stat_idle_field])

        pre_total = self.sysload['pre']['busy'] + self.sysload['pre']['idle']
        post_total = self.sysload['post']['busy'] + self.sysload['post']['idle']
        idle_delta = self.sysload['post']['idle'] - self.sysload['pre']['idle']
        busy_delta = self.sysload['post']['busy'] - self.sysload['pre']['busy']
        total_delta = max(1, (post_total - pre_total))
        # print " pre_total %s, post_total %s, idle_delta %s, busy_delta %s, total_delta %s" % (pre_total, post_total, idle_delta, busy_delta, total_delta)
        self.sysload['swapin'] = int(self.sysstat['post']['swapin']) - int(self.sysstat['pre']['swapin'])
        self.sysload['swapout'] = int(self.sysstat['post']['swapout']) - int(self.sysstat['pre']['swapout'])
        self.sysload['stage'] = 'post'  # pre/post doesn't matter most likely.  These are snapshot numbers, not trends at this point like load is
        self.sysload['loadavg'] = os.getloadavg()
        self.sysload['cores'] = self.sysstat['post']['cores']
        self.sysload['cpubusy'] = float(((float(total_delta - idle_delta) / float(total_delta)) * 100))
        self.sysload['running'] = int(self.sysstat['post']['procs_running'])
        self.sysload['blocked'] = int(self.sysstat['post']['procs_blocked'])
        self.sysload['mem_used'] = self.sysstat[stage]['memactive'] + self.sysstat[stage]['meminactive']
        self.sysload['mem_really'] = self.sysload['mem_used'] - (self.sysstat[stage]['memcached'] + self.sysstat[stage]['membuffers'])
        self.sysload['mem_pcnt_raw'] = float((self.sysload['mem_used'] / float(self.sysstat[stage]['memtotal'])) * 100)
        self.sysload['mem_pcnt_really'] = float((self.sysload['mem_really'] / float(self.sysstat[stage]['memtotal'])) * 100)
        self.sysload['swap_used'] = float(((float(self.sysstat[stage]['swaptotal']) - float(self.sysstat[stage]['swapfree'])) / float(self.sysstat[stage]['swaptotal'])) * 100)

        load_data = " System cores: %2d cpu: (last %2.0f sec) busy %3.1f%%, running %2d, blocked %2d; avg load: %s\n" \
            % (self.sysload['cores'], delta, self.sysload['cpubusy'], self.sysload['running'], self.sysload['blocked'], self.sysload['loadavg'])

        load_data += " System mem: Used(raw) %4.1f%%, Excl buffers/cache %4.1f%%, Swap used %4.1f%% : swap in/out %d/%d" \
            % (self.sysload['mem_pcnt_raw'], self.sysload['mem_pcnt_really'], self.sysload['swap_used'], self.sysload['swapin'], self.sysload['swapout'])

        self.sysload['loadsummary'] = load_data

        return load_data


class Stdin:
    """
    Methods related to Stdin

    Usage (See bin/extract_name.py for sample usage):
    1) To identify to print help or not:
        if not OPT.all and (not Stdin.is_stdin()):
            self.print_help()

    2) Code to process:
        for line in Stdin.get_fh():    # use Stdin -or- OPT.all[0]
            # do something with line
    """

    @classmethod
    def is_stdin(cls):
        """Returns True if there is stdin"""
        try:
            return not sys.stdin.isatty()
        except BaseException:
            return False    # if sys.stdin is closed, then it is not stdin

    @classmethod
    def get_fh(cls):
        """Return the filehandle, either from stdin (if OPT.all is not defined) or OPT.all[0]"""
        import fileinput
        if not OPT.all:
            return fileinput.input('-')     # returns stdin filehandle
        else:
            return File(OPT.all[0]).fh()


class RsyncerBase(object):
    """
    A flexible rsync wrapper allowing transfering over pipes, staging as p6vector / faceless and a host of other options.
    Derive from this base class in your module to add specific behaviour
    """

    def __init__(self, site, rsync_exe=None, allow_local_cp=False):
        # setup vars
        self.run_time = time.time()
        self.previous_machine = None

        # Logging methods
        self.logger = log

        self.rsync_exe = "/usr/intel/bin/rsync"

        if rsync_exe:
            self.rsync_exe = rsync_exe

        self.allow_local_cp = allow_local_cp

        self.pipes = "/usr/intel/common/pkgs/pipes/1.47/bin/pipes"
        from .tvpv import TvpvEnv
        self.site_dict = TvpvEnv.site_mapping

        # Translate:
        self.site = self.site_dict.get(site.lower(), site.upper())
        # from config.config_release_sites_common import sitecfg_common as access_machines

        if self.site not in access_machines.keys():
            raise IOError("Bad site given. {} not recognized as a valid site. try: {}"
                          .format(self.site, access_machines.keys()))

        # look for pipes override
        if 'pipes' in access_machines[self.site]:
            self.pipes = access_machines[self.site].pipes

    def _remote_chmod(self, host, dest_dir, ch_str="ugo+rwx"):
        cmd = "ssh {host} chmod {chs} {dst}".format(host=host, dst=dest_dir, chs=ch_str)
        ecode, sout, serr = SystemCall(cmd, disp=True).run_sout_serr()
        if ecode != 0:
            self.logger.info("ecode: {}".format(ecode))
            self.logger.info("sout: {}".format(sout))
            self.logger.info("serr: {}".format(serr))
            return False
        self.logger.debug("sout:\n{}".format(sout))
        return True

    def _rsync_preprocessing(self):
        """
        Implement logic to run as an rsync preprocessing - prepare your data, check permissions, etc...
        """
        pass

    def _rsync_postprocessing(self):
        """
        Implement logic to run as an rsync postprocessing - validate data transfer, update logs, etc....
        NOTE: This method's return value will become do_rsync() return value.
        On default, this runs only if the do_rsync()'s rsync is successfull. However,
        if do_rsync() is called with postprocess_on_fail=True, this method is called on failure too.
        in which case, the return value here will be the return value of rsync()
        """
        return True

    # Some benchmarks:
    # Pushing IDC->JF: 582 MB in 85-90secs AVG. [85.302,88.391,93.272,104.267,88.939,90.120 Secs]
    # Pulling JF->IDC: 581 MB in 127-140 secs AVG. [132.606,140.720,127.956,139.215,124.591 Secs]
    def do_rsync(self, src_dirs, dest_dir, direction="push", use_stage=False, use_pipes=True,
                 rsync_options="--recursive -avz --partial", postprocess_on_fail=False, list_file=None, retries=1):
        """
        Do the actual rsync of the files. Uses rsync over pipes.
        :param src_dirs: list of files/dirs to rsync (can be a list)
        :param dest_dir: destination directory on dest machine
        :param direction: "push" / "pull"
        :param use_stage: bool, whether to use stager to rsync as p6vector / faceless or not. Required for rsyncing to central.
        :param use_pipes: bool, whether to use pipes as a remote-shell (tcp/ip sockets to boost perf). Not available in sort sites.
        :param rsync_options: Additional rsync options, as string. --partial is used as a default as it can speed up
                                the rsync when retries are used.
        :param retries: number of retries to attempt if rsync fails.
        :return: True if cmd_safe ecode is 0, False otherwise
        """
        self._rsync_preprocessing()
        if direction not in ["push", "pull"]:
            raise IOError("Invalid value for rsync direction: {}. Use: push/pull".format(direction))
        remote_machine = self.get_remote_machines()

        if not remote_machine:
            return False

        if isinstance(src_dirs, list):
            if list_file:
                self.logger.info(" 0) For rsync, when using a list_file you must only supply one source dir")
                return False
            for src in src_dirs:
                if re.match(r"\w+:", src):
                    self.logger.info(" 1) For rsync %s, source can't specify a host %s" % (direction, src))
                    return False
        elif re.match(r"\w+:", src_dirs):
            self.logger.info(" 2) For rsync %s, source path can't specify a host %s" % (direction, src_dirs))
            return False

        if re.match(r"\w+:", dest_dir):
            self.logger.info(" 3) For rsync %s, destination path can't specify a host %s" % (direction, dest_dir))
            return False

        if list_file:
            if direction != "push":
                self.logger.info(" 4) For rsync with a list file, only push is allowed")
                return False
            if not os.path.isfile(list_file):
                self.logger.info(" 5) The list file is not found: %s" % list_file)
                return False
            rsync_options += " -avr --no-R --files-from=%s" % list_file

        # Determine if we should run locally.  If so, we will cp rather than rsync
        # This is based on:
        # 1) All paths (src and dest) are local paths.  This is determined by:
        #   a) All src paths exist
        #   b) The parent of test path exists (actual path may not exist)
        # 2) The enable flag self.allow_local_cp is true
        local = False
        if self.allow_local_cp:
            # Assume everything is local until something not local is found
            local = True
            # Check that src dir(s) exist
            if isinstance(src_dirs, list):
                for src in src_dirs:
                    if not os.path.exists(src):
                        local = False
                        self.logger.debug(" do_rsync: in src list: src doesn't exist, clearing local, src [%s]" % src)
            else:
                if not os.path.exists(src_dirs):
                    local = False
                    self.logger.debug(" do_rsync: indv: src doesn't exist, clearing local, src_dirs [%s]" % src_dirs)

            # Check that parent of dest path exists (dest path does not need to exist)
            #   Strip the dest dir of trailing "/"s, since they affect the output of os.path.dirname
            if not os.path.exists(os.path.dirname(dest_dir.rstrip("/"))):
                local = False
                self.logger.debug(" do_rsync: dest parent doesn't exist, clearing local, dest_dir [%s]" % dest_dir)

        # If current site is different from -to site then local is False.
        local_site = TvpvEnv.get_site()
        if local_site != self.site:
            local = False

        # Put together src/dest strings.  Determine if remote strings are needed ("machine:dir")
        remote_prefix = remote_machine + ":"
        self.logger.debug(" local is %s, direction is %s, remote site->host %s->%s" % (local, direction, self.site,
                                                                                       remote_machine))

        if local:
            remote_prefix = ""

        if direction == "push":
            if isinstance(src_dirs, list):
                src_str = " ".join(src_dirs)
            else:
                src_str = src_dirs
            dest_str = remote_prefix + dest_dir
        else:
            if isinstance(src_dirs, list):
                src_str = " ".join(remote_prefix + src_d for src_d in src_dirs)
            else:
                src_str = remote_prefix + src_dirs
            dest_str = dest_dir

        # Need to ensure that when not using pipes, only a single whitespace character ends up being placed
        # between {rsync} and {src}.  This is because multi-space creates a problem if this command is fed info
        # a faceless execution (i.e. suid_src) as it messes with performing checksum/sha operations.
        pipes_str = "--rsh={} ".format(self.pipes) if use_pipes else ""
        cmd = ("{rsync} {opts} --timeout=60 --rsync-path={rsync} {pipes}{src} {dest}"
               .format(rsync=self.rsync_exe,
                       opts=rsync_options,
                       pipes=pipes_str,
                       src=src_str,
                       dest=dest_str))

        log.info(f'{curtime()}: {cmd}')

        ecode = -1
        count = 0
        sout = ''
        serr = ''
        while ecode != 0 and count < retries:
            # Spread out retry attempts a little bit
            if count:
                time.sleep(10)
            count += 1
            ecode, sout, serr = SystemCall(cmd, disp=True).run_sout_serr()

        if ecode != 0:
            self.logger.info("cmd: {}".format(cmd))
            self.logger.info("sout: {}".format(sout))
            self.logger.info("error code: {}".format(ecode))
            self.logger.info("serr: {}".format(serr))
            self.logger.info("RSYNC failed. Exiting...")
            if postprocess_on_fail:
                return self._rsync_postprocessing()
            else:
                return False

        # self.logger.debug("sout:\n{}".format(sout))     # duplicate print, since SystemCall() already printing

        self.run_time = time.time()

        return self._rsync_postprocessing()

    def get_remote_machines(self, site=None, machine_timeout=(30 * 60)):
        """
        Get a list of the remote rsync machines in the given site.
        :return - The first working machine
        """

        if (time.time() < (self.run_time + machine_timeout)) and (self.previous_machine is not None):
            return self.previous_machine

        if site is None:
            site = self.site

        # self.logger.debug(site)
        # self.logger.debug(access_machines[site])
        access_machines_list = access_machines[site]["hosts"]

        # rsync a test file to validate that the machine is up
        # if machine is not up, move on to the next machine in the list
        # return the first working machine (e.g. "plxc25571.pdx.intel.com")
        # raise exception if there are no valid machines
        randomized = sample(access_machines_list, len(access_machines_list))
        for each_machine in randomized:
            # create test file
            File(join("/tmp", USERNAME + "_rsync_test")).touch("rsync test", newfile=True).chmod("0775")

            pipes_str = "--rsh={}".format(self.pipes)
            cmd = ("{rsync} {opts} --timeout=60 --rsync-path={rsync} {src} {dest}"
                   .format(rsync=self.rsync_exe,
                           opts="-avz",
                           src="/tmp/" + USERNAME + "_rsync_test",
                           dest=each_machine + ":/tmp/"))

            ecode, sout, serr = SystemCall(cmd, disp=True).run_sout_serr()
            if ecode:
                self.logger.info(" rsync test-copy failed: %s %s %s %s" % (cmd, ecode, sout, serr))
                continue

            if is_alive_ssh(each_machine, freegb=5, native_timeout=True):
                self.previous_machine = each_machine
                return each_machine

            if ecode == 0:
                log.info(" get_remote_machines: host %s ecode[%s] is 0, meaning is_alive_ssh failed '/tmp freegb=10' "
                         "check. sout %s, serr %s" % (each_machine, ecode, sout, serr))

        log.info("No valid machines available! %s" % access_machines_list)
        return None


def get_username():   # pragma: no cover
    """unix/windows way to get username"""
    if IS_UNIX:
        try:
            import pwd
            return pwd.getpwuid(os.geteuid()).pw_name    # Suggested by crichmon. Works well with eseu.py.
        except BaseException:
            return 'tbd'

    # windows
    try:
        return os.getlogin()
    except OSError:
        pass

    try:
        import getpass
        return getpass.getuser()
    except BaseException:
        return 'tbd'


# Module variables
try:
    LAUNCH_CWD = os.getcwd()
except BaseException:  # pragma: no cover  - test by doing a "source <path>/sourceme.rc" from a stale NFS directory.
    raise SystemExit("ERROR: Cannot get cwd(). Execute 'pwd' in unix for more info. "
                     "Pls cd to an existing directory first. Exiting...")

USERNAME = get_username()
HOSTNAME = socket.gethostname()
CALLERBIN = getcaller()

if __name__ == '__main__':  # pragma: no cover

    print("USERNAME:    ", USERNAME)
    print("HOSTNAME:    ", HOSTNAME)
    print("CALLERBIN:   ", CALLERBIN)

    mi = MachineInfo()
    print("== MachineInfo ==")
    print("Memory:      ", mi.machine_memory_gb())
    print("Machine Type:", mi.machine_type())
    print("Phy CPU:     ", mi.n_physical_cpu())
    print("Log Cores:   ", mi.n_physical_cores())
    print("N users:     ", mi.n_users())
    print("SLES Version:", mi.sles_version())
    print("sysname:     ", mi.sysname())
