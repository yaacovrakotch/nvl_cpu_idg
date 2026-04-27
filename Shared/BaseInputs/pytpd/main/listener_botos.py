#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
botos listener.
Run from tester.

Normal Usage:
   listener_botos.py begin      # Add the "start teambots" signal
   listener_botos.py end        # Add the "end teambots" signal

Developer Usage:
   listener_botos.py botstart   # Start the listener daemon
   listener_botos.py botstop    # Set the tester to stop state. Do not accept new jobs.
   listener_botos.py botdown    # Set the tester to down state. Do not accept new jobs.
   listener_botos.py botup      # Set the tester back online.

Note: Do not ctrl+c, since greaceful cleanup may not happen.
"""
import setenv      # must be first in the imports
from gadget.files import TempDir, File
from gadget.tputil import CheckerLog
from gadget.shell import HOSTNAME, SystemCall, IS_UNIX, untar
from gadget.lockfile import force_refresh
from gadget.gizmo import Elapsed
from gadget.pylog import log
from gadget.errors import confirm, ErrorInput, ErrorUser, ErrorCockpit
from gadget.disk import mkdirs, Chdir, delete_oldest
from gadget.tvpv import TvpvEnv
from gadget.helperclass import IS_UT, AutoRestart
from gadget.strmore import curtime
from mod.indicators import TPBotFail
from main.manager_botos import BotOS
from mod.BOT2Trace import traceIT
from gadget.data_host import DataHost
from subprocess import call, run
from os.path import exists, basename, dirname, realpath, isdir
import time
import glob
import sys
import os
import shutil
import re
import json
from collections import defaultdict, deque

# TODO: When Ctrl+C is made, can a signal automatically be sent as stopped?
# TODO: code the "occupied" status when we code teambots


class ListenerBotOS:

    def __init__(self):
        self.tester = HOSTNAME
        self.root = f'{BotOS.root}/testers/{self.tester}'
        self.logdir = TPBotFail.TESTERLOGS
        self._ut = []
        self.tdir = None
        self.folderidx = 0
        self.nop = True      # True - no action, False - with Action; Used to print "Waiting..."
        mkdirs(self.root, mode='02775')
        self.hardBin_list = deque(maxlen=3)
        self.sendtime = time.time()
        self.bom = ''
        self.tp_options = {}
        self.force_ticket_path = 'I:/tpvalidation/engtools/tptools/mtl/infra/torch/exe/force-ticket.exe'

    def main(self, maxloop=63072000, sleeptime=5):     # this is 10 yrs at 5 sec sleep
        """This is the infinite loop"""

        # other options
        if sys.argv[1] != 'botstart':
            # this is to check that listener is running in the background
            if self.check_running_process(check_only=True):
                self.other(sys.argv[1])
                return 0   # exit out normally
            else:
                raise ErrorInput(f"Listener is not executed yet.",
                                 "Please execute listener first!")

        # Start of daemon process =====================
        # Check to ensure only 1 package info is defined in folder
        package_info = glob.glob(f'{self.root}/*.package.info')
        confirm(len(package_info) == 1,
                f'Expecting 1 *.package.info in {self.root}. Got: {package_info}',
                'Pls make sure there is one <package>.package.info file')

        AutoRestart(f'{BotOS.root}/testers/{HOSTNAME}/listener_botos.txt')

        # Make sure only one listener is running
        if self.check_running_process(check_only=False):
            raise ErrorInput(f"Listener is already running.",
                             "Only one listener is allowed per tester.")

        # At this point, there is only one listener running.
        log.flush('-i- Listener starting.')
        with TempDir(chdir=True):
            self.tdir = realpath(os.getcwd())
            os.chdir(self.tdir)              # This is needed since TOS does not like sys_tp~1 in the path (sys_tprobot)

            for loopidx in range(maxloop):
                AutoRestart()
                self.nop = bool(loopidx)     # False for 0, first; True for >1, 2nd or more
                self.set_status('idle')      # always set the status to idle at very start
                self.set_status_dashboard()

                try:
                    self.main_one_run()
                except Exception as e:
                    log.flush(f'-i- Exception: {e}')
                bot_error = self.are_three_hardbin_same()
                if bot_error:
                    # Only send email for 3-strike tpbot failed for real testers.
                    self.bot_error_found()

                if not self.nop:
                    log.flush(f"{curtime()} Waiting and Listening...")

                sys.stdout.flush()
                time.sleep(sleeptime)

    def main_one_run(self):
        """This is one execute of a job"""
        force_refresh(self.root)

        # step1: look at job.tar.gz
        tarfiles = glob.glob(f'{self.root}/*.tar.gz')
        for tf in tarfiles:
            self.nop = False
            log.flush(f'Executing: {basename(tf)}')
            File(f'{self.root}/done').unlink()     # Delete this if it exist. User cannot set "done" before it's loaded.

            # step2: update status
            self.set_status('running')
            self._ut.append(set(os.listdir(self.root)))      # unittest hook

            # step3a: get tpcwd
            tpcwd = self.get_tpcwd(tf)

            # step3: untar then run load_and_run.py
            self._ut.append(tpcwd)
            mkdirs(tpcwd)
            with Chdir(tpcwd):

                # untar it
                sw = Elapsed()
                untar(tf, '.')
                log.flush(f'-i- Untar {tf} to {tpcwd} in {sw}')
                if exists('load_from_local.txt'):
                    load_from_local = File('load_from_local.txt').read().strip()
                    log.flush(f'-i- Loading test program from path: {load_from_local}')
                    if os.path.exists(load_from_local):

                        if os.path.exists(f'load_and_run.json'):
                            log.flush(f'-i- Copy load_and_run.json to: {load_from_local}')
                            shutil.copyfile('load_and_run.json', f'{load_from_local}/load_and_run.json')

                        with Chdir(load_from_local):
                            self.tester_execute(tf)

                    else:
                        log.flush(f'-e- load_from_local path does not exist: {load_from_local}')

                else:
                    self.tester_execute(tf)

            # step4: delete job.tar.gz
            File(tf).unlink()

            # step5: update status
            self.set_status('idle')

    def tester_execute(self, tf):
        """
        Calling tester execute function
        :param tf: tarfile
        """
        # read the options
        if exists('load_and_run.json'):
            self.tp_options = BotOS.json.load('load_and_run.json', 'main_one_run()')
        else:
            log.info(f'-i- load_and_run.json does not exist')
            self.tp_options = {}

        # write the team file
        if 'TEAM' in self.tp_options:
            File(f"{self.root}/{self.tp_options['TEAM']}.team").touch()

        # run
        wild = '*_TP/*/Scripts'     # required folder
        lar = glob.glob(wild)
        if len(lar) == 1:
            if os.path.exists('Shared/BaseInputs/Scripts/bot_test_unit.py'):
                lar_path = 'Shared/BaseInputs/Scripts/bot_test_unit.py'
            else:
                lar_path = f'Shared/{lar[0]}/load_and_run.py'

            if exists(lar_path):
                # Set self.bom
                if '/' in lar[0]:
                    self.bom = lar[0].split('/')[1]  # get the 2nd folder name, which is the bom name
                else:
                    self.bom = lar[0].split('\\')[1]  # get the 2nd folder name, which is the bom name

                # Execute it
                sw = Elapsed()
                log.flush(f'CWD TP: {os.getcwd()}')
                os.environ['_BOT_EMAIL_FNAME'] = f'{self.root}/email1.{BotOS.get_metafname(tf)}.command'       # so that load and run know the path
                code, out = SystemCall(f'{sys.executable} {lar_path}', disp=True).run_outtxt()
                log.flush(f'-i- Done with {basename(tf)}. Elapsed: {sw}')

                self.teambot_wait(tf)

                # Writing the result.json for normal case and the result log file based on running the golden_basetp or golden_fulltp
                self.write_result_golden(tf, code, out)

            else:
                log.flush(f'-e- {tf}: Expecting {lar_path}: not exist')
                self.write_result(tf, code=1, out=f'problem on load_and_run.py. not Found: {lar_path}')

        else:
            log.flush(f'-e- {tf}: Expecting one folder: Found: {lar}. wild: {wild}')
            self.write_result(tf, code=1, out=f'problem on load_and_run.py. Found: {lar}')

    def get_tpcwd(self, tf, _maxiter=100):
        r"""
        Return which which tp folder to use
        mbot: I:\ drive   [needed for TRACE]
        tpbot: C:\ drive  [for performance]

        :param tf: tarfile (eg, 8000_1748119774796_B.tar.gz)
        :return: path to write testprogram
        """
        if '_E.tar' in tf:     # mbot job
            # Return I:\ drive
            root = f'{BotOS.root}/mbot_rolling'
            confirm(isdir(root), f'{root} does not exist', 'contact jqdelosr to enable')
            delete_oldest(root, keep=100, message='-i- Deleting mbot_rolling:')
            for idx in range(_maxiter):
                tpcwd = f'{root}/{BotOS.get_metafname(tf)}.{idx}'
                if not isdir(tpcwd):
                    return tpcwd
            raise ErrorCockpit(f'Max iteration exceeded: {idx} on {tpcwd}', 'Check the disk why')

        # tpbot job or any other non-mbot job: return C:\ temp drive
        tpcwd = f'{self.tdir}/{self.folderidx}'
        if exists(tpcwd):
            try:
                shutil.rmtree(tpcwd)
            except Exception as e:
                log.flush(f'-e- rmtree error [{tpcwd}]: {e}')
                self.folderidx += 1
                tpcwd = f'{self.tdir}/{self.folderidx}'

        return tpcwd

    log_headers = ['Ituff file', 'Test Unit log', 'INIT log', 'Load log']

    def write_result(self, tf, code, out):
        """
        Write the json file
        :param tf: tarfile
        :param code: code
        :param out: out text
        :return: None
        """
        # copy the tarfile first so we have copy in tp_rolling_botos
        tproll = f'{BotOS.root}/tp_rolling_botos/{BotOS.get_metafname(tf)}'
        mkdirs(tproll, mode='02770')
        File(tf).copy(tproll)
        logfile = f'{tproll}/log.{self.tester}.txt'
        File(logfile).touch(out).compress(File.gz)       # TODO: move this at the very end if this routine, and include log.flush() here, so we can grep log prints.

        # create log file in perma archive area
        confirm(not (IS_UT and self.logdir.startswith('/intel/')), 'Error in unittest.', 'Pls Mock obj.logdir')
        bname = basename(tf).split('.')[0]
        perma = f'{self.logdir}/{curtime(dateonly=True)}/{bname}_{self.tester}.txt'
        mkdirs(dirname(perma), mode='02770')
        log.flush(f'-i- Writing in perma out: {perma}')
        File(perma).touch(out).compress(File.gz)

        # get the log files
        tracelots = []
        data = {}
        robj = re.compile(r'(%s): (\S+\.txt)' % '|'.join(self.log_headers))
        retest_count = defaultdict(list)
        r_number = re.compile(r'_(\d+)_')
        for item in sorted(set(tuple(x) for x in robj.findall(out))):
            logtype, fname = item

            # copy ituff to standard area so we can see it in trace
            if logtype == 'Ituff file' and BotOS.get_metafname(tf)[-1] in ('A', 'E'):    # mbot job only
                log.flush(f"-i- Transferring {fname} to prod area for Trace")
                tracelots = traceIT(fname)

            # Copy to tprolling
            try:
                File(fname).copy(tproll).compress(File.gz)
                File(fname).compress(File.gz)
            except Exception as e:
                log.flush(f'-e- Exception on copy+compress of {fname}: {e}')

            # Handle Restest Ituff file and Test Unit log, with *_1*.txt
            retest_count[logtype].append(fname)

        # Assign the latest log to the base log type key and previous logs to incremented keys
        for logtype, fnames in retest_count.items():
            # Sort the filenames according to , _1, _2
            fnames.sort(key=lambda x: (x.count('_'), int(r_number.search(x).group(1)) if r_number.search(x) else 0), reverse=False)
            for i, fname in enumerate(fnames):
                if i == 0:
                    data[logtype] = fname
                else:
                    data[f"{logtype} {i}"] = fname

        # get the HardBin line or last line to be written in comment
        found = ''
        lastline = ''
        for line in out.split('\n'):
            if 'HardBin' in line:
                found = line

            if line:
                lastline = line    # as long as not empty

        if found:
            comment = found
            self.tpbot_3strike_logic(tf, found, code)

        else:
            comment = f'No HardBin found. See logs. Lastline: [{lastline}]'

        if code == 1:
            # if workflow failed, send email right away
            if found:
                self.workflow_failed_sent_email(found)
            else:
                self.workflow_failed_sent_email(lastline)

        # Write the result.json file
        data['code'] = code
        data['tprolling'] = tproll
        data['logfile'] = perma
        data['site'] = TvpvEnv.get_site()
        data['command'] = 'done'
        data['comment'] = comment
        data['tracelot'] = ','.join(tracelots)
        BotOS.json.dump(f'{self.root}/{BotOS.get_metafname(tf)}.result.json', data)

    def check_running_process(self, check_only, is_unix=IS_UNIX):
        """
        Check if a listener is already running, if yes, print message and exit out
        This is only for windows, so validate manually!
        :param check_only: True for checkonly, False for daemon
        :return: True if running, False if not running
        """
        if is_unix:
            return 1    # do nothing for unix (aka, it is running)

        processes = glob.glob(f'{self.root}/*.process')

        # put the processes in a dict, these are processes saved by running listener.py
        process_dict = {}    # {<id>: path_of_process_file}
        for processfile in processes:
            processid = basename(processfile).replace('.process', '')
            process_dict[processid] = processfile

        # get all processid of listener that is running
        code, out = SystemCall('tasklist').run_outtxt()
        for line in out.strip().split('\n'):
            if "python" in line.lower():
                columns = line.split()
                pid = columns[1]        # Process name is always first column and PID is the second column, for python.exe
                if pid in process_dict:
                    return True

        # this switch is when arg is used in listener_bot.py
        # if there is no listener process running, then exit out, no need to create a new process
        if check_only:
            return False

        # at this point, there is no other listener running, so delete <id>.process in disk
        for processid in process_dict:
            log.flush(f'Deleting: {process_dict[processid]}')
            File(process_dict[processid]).unlink()     # delete the <id>.process in disk

        # write the process id for this
        File(f'{self.root}/{os.getpid()}.process').touch()
        return False   # success

    def set_status_dashboard(self):
        """
        Re-update the status based on special signals. This is called after "idle" set.
        :return:
        """
        if exists(f'{self.root}/stop'):
            self.set_status('stopped')
        if exists(f'{self.root}/down'):
            self.set_status('down')

    def set_status(self, status):
        """
        Write the status file.
        Delete all status file that exist.
        """
        sfiles = glob.glob(f'{self.root}/*.status')
        for statusfile in sfiles:
            File(statusfile).unlink()    # delete the existing status file
        File(f'{self.root}/{status}.status').touch()

        # Do some cleanup for 'idle'
        if status == 'idle':
            for ff in glob.glob(f'{self.root}/expiry.*.txt'):
                File(ff).unlink()
            for ff in glob.glob(f'{self.root}/*.team'):
                File(ff).unlink()

    def other(self, cmd):
        """check cmd and write out in folder"""
        if cmd == 'botstop':
            File(f'{self.root}/stop').touch()
            log.flush(f'Wrote stop signal for {self.tester}.')

        elif cmd == 'botdown':
            File(f'{self.root}/down').touch()
            log.flush(f'Wrote down signal for {self.tester}.')
            # put more code here later to inform labs that it's down

        elif cmd == 'botup':
            File(f'{self.root}/stop').unlink()
            File(f'{self.root}/down').unlink()
            log.flush(f'{self.tester} is back online')

        elif cmd == 'begin':
            File(f'{self.root}/begin').touch()
            self.set_status('occupied')
            log.flush('-i- Success: begin command is acknowledged.')

        elif cmd == 'help' or cmd == '-h':
            print(__doc__)

        elif cmd == 'end':     # Note: "idle.status" is set by listener running process.
            if exists(f'{self.root}/begin'):
                File(f'{self.root}/begin').unlink()
                log.flush('-i- Success: end command is acknowledged.')
            else:
                log.flush('-i- The tester is not in teambots mode. There is nothing to end.')
            File(f'{self.root}/done').touch()

        else:
            raise ErrorUser(f'Given command is {cmd}. '
                            'Valid options are: botstop, botdown, botup, begin, end',
                            'Pls fix command')

    def update_expiry(self, secsadd, is_start=True):
        """
        Update the expiry file. Guarantee one only

        :param secsadd: None or secs
        :return: epoch seconds - expiry
        """
        self._ut.append(secsadd)

        # get current expiry, and delete existing expiry files
        current_expiry = int(time.time())
        force_refresh(self.root)
        for ff in glob.glob(f'{self.root}/expiry.*.txt'):
            elems = basename(ff).split('.')
            current_expiry = int(elems[1])
            File(ff).unlink()

        if is_start:
            current_expiry = int(time.time())

        # write new expiry
        secs = current_expiry + secsadd
        File(f'{self.root}/expiry.{secs}.txt').touch()
        log.flush(f"{curtime()}: new expiry +{secsadd}: {curtime(secs)}")
        return secs

    def teambot_wait(self,
                     tarfname,
                     timeout_first=1800,
                     timeout_second=3600 * 6,
                     sleeptime=5,
                     renewtime=3600 * 2,
                     forever=3600 * 168):     # 1 week
        """
        If job is a teambot (aka, "D"), then do the "wait-and-release" logic.

        Temporarily, for backwards compatibility/transition: Code requires "teambot_wait.txt" which is written
        by load_and_run.py.

        :param tarfname: fullpath to the tar filename
        :param timeout_first: Timeout on first wait, in seconds: 30 mins
        :param timeout_second: Timeout on second wait, in seconds: 6 hrs
        :param sleeptime: Seconds
        :param renewtime: Seconds for renew
        :return: unittest code
        """
        if not BotOS.get_metafname(tarfname).endswith('D'):
            return -1    # Not a teambot

        if 'teambot_wait.txt' not in os.listdir(self.root):
            log.flush(f"'teambot_wait.txt' file not exist. exiting teambot_wait()")
            return -5

        File(f'{self.root}/teambot_wait.txt').unlink()

        # Create expiry_<secs> file
        self._ut = []
        expiry_secs = self.update_expiry(timeout_first)               # 30 mins

        beginonce = True
        for loopbegin in range(int(forever / sleeptime)):
            force_refresh(self.root)    # so that os.listdir() is up to date

            if beginonce and 'begin' in os.listdir(self.root):
                log.flush(f"{curtime()}: begin signal detected...")
                expiry_secs = self.update_expiry(timeout_second)     # 6 hrs
                beginonce = False

            if 'renew' in os.listdir(self.root):
                log.flush(f"{curtime()}: renew signal detected...")
                expiry_secs = self.update_expiry(renewtime, is_start=False)
                File(f'{self.root}/renew').unlink()

            if 'done' in os.listdir(self.root):
                log.flush(f"{curtime()}: User signal Team Bot Job end. Exiting.")
                File(f'{self.root}/begin').unlink()
                File(f'{self.root}/done').unlink()
                return -3

            if int(time.time()) > expiry_secs:       # expired
                break

            time.sleep(sleeptime)

        log.flush(f"{curtime()}: Team Bot job reached allowed limit (expiry {curtime(expiry_secs)}). Releasing tester!")
        File(f'{self.root}/begin').unlink()
        return -4

    def are_three_hardbin_same(self):
        """
        Check if all 3 hardbins in hardBin_list are the same.
        """
        if len(self.hardBin_list) < 3:
            return False  # Less than 3 items, skip the check

        temp_hardbin_list = [item.split('-')[0] for item in self.hardBin_list]

        if set(temp_hardbin_list) == {'1'}:
            return False

        return len(set(temp_hardbin_list)) == 1  # Return True if all items are the same, False otherwise

    def workflow_failed_sent_email(self, line):
        """
        Send an email if the workflow failed.
        """
        load_and_run_data = self.tp_options
        if not load_and_run_data:
            return ''

        workflow = load_and_run_data.get('GITHUB_WORKFLOW', 'None')
        log.info(f'Workflow: {workflow}')
        if workflow == 'TPBot_schedule' or workflow == 'SCHEDULER_INIT':
            repo = load_and_run_data.get('GITHUB_REPOSITORY', 'unknown')
            failed_status = line
            msg = self.send_error_email(workflow, repo, failed_status)
            log.info(f'Sent email: {msg}')
            return msg

    def send_error_email(self, error='HardBin Error', repo='unknown', failed_status='unknown'):
        """
        Send an error email if:
        + The hardBin_list has 3 same items.
        + TPBOT Scheduler error
        + SCHEDULER_INIT error
        """
        if error == 'TPBot_schedule':
            subject = f'Mainline Full TP is broken for {self.bom} for {self.tester}'
            message = (f'TPBot schedule error encountered for {self.bom} for {self.tester}.\n'
                       f'Repo: {repo}\n'
                       f'Failed Status: {failed_status} for {self.bom}\n'
                       f'Please check the testers for more details.')
        elif error == 'SCHEDULER_INIT':
            workflow_fail_file = 'workflow_failed.json'
            if os.path.exists(workflow_fail_file):
                with open(workflow_fail_file, 'r', encoding='utf-8') as f:
                    workflow_fail_data = json.load(f)
                    print(f'Loaded job input json file: {workflow_fail_data}')
                socket = workflow_fail_data.get('current_socket', '6248_CLASSHOT')
            else:
                print(f'{workflow_fail_file} does NOT exist. Continue with default parameters.')
                socket = '6248_CLASSHOT'
            subject = f'SCHEDULER_INIT failed for {socket} for {self.bom} for {self.tester}'
            message = (f'SCHEDULER_INIT failed for {socket} for {self.bom} for {self.tester}.\n'
                       f'Repo: {repo}\n'
                       f'Failed Status: {failed_status} for {self.bom} for {socket}\n'
                       f'Please check the SCHEDULER_INIT in {repo} workflow for more details.')
        else:
            temp_pr_list = []
            temp_hardbin = ''
            for item in self.hardBin_list:
                if '-' not in item:
                    log.warning(f'Invalid hardBin_list entry (missing "-"): {item}')
                    continue
                parts = item.split('-', 1)
                if len(parts) != 2 or not parts[0] or not parts[1]:
                    log.warning(f'Invalid hardBin_list entry format: {item}')
                    continue
                hardbin, pr_number = parts
                temp_hardbin = hardbin
                temp_pr_list.append(pr_number)
            if temp_pr_list and temp_hardbin:
                subject = (f'Tester {self.tester} encountered 3 consecutive same HardBin '
                           f'{temp_hardbin} for PRs {temp_pr_list} for {self.bom}.')
                message = (f'Tester {self.tester} encountered 3 consecutive same HardBin '
                           f'{temp_hardbin} for PRs {temp_pr_list} for {self.bom}.\n'
                           f'Please check the testers for more details. Additionally, consider to '
                           f'take down the tester for maintenance.\n'
                           f'Error: {failed_status}\n')
            else:
                subject = (f'Tester {self.tester} encountered 3 consecutive same HardBin '
                           f'for {self.bom}.')
                message = (f'Tester {self.tester} encountered 3 consecutive same HardBin for '
                           f'{self.bom}.\n'
                           f'Please check the testers for more details. Additionally, consider to '
                           f'take down the tester for maintenance.\n'
                           f'Error: {failed_status}\n')
        msg = {'to_list': ['john.q.delos.reyes@intel.com', 'tai.pham@intel.com', 'erick.a.lang@intel.com', 'sunny.r.ty@intel.com', 'weng.keen.wong@intel.com', 'maroon.maroon@intel.com', 'hai.m.pearson@intel.com'],
               'cc_list': 'mpe_ddg_pde_tp_team@intel.com',
               'subject': subject,
               'message': message,
               'html': True}
        log.info(f'{msg}')
        if time.time() - self.sendtime > 3600 * 2:      # send only once in two hours
            # send email
            log.info(f'Sending email {subject}...')
            self.sendtime = time.time()    # reset it
            DataHost().central("sendmail", msg, check=True)
        return msg

    def bot_error_found(self):
        """
        Actions to take when bot error is found (3 consecutive same HardBin)
        """
        golden_fulltp = f'{BotOS.root}/golden_check/golden_fulltp_{self.bom}'
        golden_basetp = f'{BotOS.root}/golden_check/golden_basetp_{self.bom}'
        log.info(f'Found 3 consecutive same HardBin {self.hardBin_list} for BOM {self.bom}.')
        if os.path.exists(golden_basetp):
            log.info(f'Run {golden_basetp}')
            self.tester_execute(golden_basetp)
        else:
            log.info(f'golden_basetp {golden_basetp} does not exist. Trigger sending email directly.')
            self.send_error_email('golden_basetp missing', 'N/A', f'golden_basetp {golden_basetp} does not exist for BOM {self.bom}.')
        if os.path.exists(golden_fulltp):
            log.info(f'Run {golden_fulltp}')
            self.tester_execute(golden_fulltp)
        else:
            log.info(f'golden_fulltp {golden_fulltp} does not exist. Trigger sending email directly.')
            self.send_error_email('golden_fulltp missing', 'N/A', f'golden_fulltp {golden_fulltp} does not exist for BOM {self.bom}.')

        # Case 1: golden_basetp failed and golden_fulltp failed => Send error email and submit Force Ticket
        if os.path.exists(f'{self.root}/golden_basetp_failed.log') and os.path.exists(f'{self.root}/golden_fulltp_failed.log'):
            log.info(f'golden_basetp and golden_fulltp failed for BOM {self.bom}. Sending error email and submit Force Ticket')
            if os.path.exists(self.force_ticket_path):
                result = run([self.force_ticket_path, '-machine', f'{self.tester}', '-problemDescription', 'Tester failed executing golden test program. Please investigate and take down the tester for maintenance.'], capture_output=True, text=True, check=False)
                log.info(f'Force Ticket output: {result.stdout}')
                self.send_error_email('Both golden_basetp and golden_fulltp failed', 'N/A', f'Both golden_basetp and golden_fulltp failed for bom {self.bom} on tester {self.tester}. Force Ticket has been submitted')
                if result.stderr:
                    log.error(f'Force Ticket error: {result.stderr}')
                    self.send_error_email('Both golden_basetp and golden_fulltp failed', 'N/A', f'Both golden_basetp and golden_fulltp failed for bom {self.bom} on tester {self.tester}. Failed to sent FORCE TICKET. Please take down the tester for maintenance.')

            else:
                log.info(f'force-ticket.exe does not exist. Skipping Force Ticket submission.')
                self.send_error_email('Both golden_basetp and golden_fulltp failed', 'N/A', f'Both golden_basetp and golden_fulltp failed for bom {self.bom} on tester {self.tester}. FORCE-TICKET APP does not exist. Please take down the tester for maintenance.')

        # Case 2: golden_basetp passed and golden_fulltp passed => No need to send error email. This could be PR issue. Reset the hardBin_list
        elif os.path.exists(f'{self.root}/golden_basetp_passed.log') and os.path.exists(f'{self.root}/golden_fulltp_passed.log'):
            log.info(f'golden_basetp and golden_fulltp both passed for BOM {self.bom}. No need to send error email. This could be PR issue')

        # Case 3: golden_basetp passed and golden_fulltp failed => Send error email to TPI for replacing the unit
        elif os.path.exists(f'{self.root}/golden_basetp_passed.log') and os.path.exists(f'{self.root}/golden_fulltp_failed.log'):
            log.info(f'golden_basetp passed but golden_fulltp failed for BOM {self.bom}. Sending error email to TPI for replacing the unit.')
            self.send_error_email('Bad unit', 'N/A', f'Unit is bad on {self.tester} for bom {self.bom}')

        # Case 4: golden_basetp failed and golden_fulltp passed => Send error email to TPI for replacing the golden_basetp
        elif os.path.exists(f'{self.root}/golden_basetp_failed.log') and os.path.exists(f'{self.root}/golden_fulltp_passed.log'):
            log.info(f'golden_basetp failed but golden_fulltp passed for BOM {self.bom}. golden_basetp is no longer valid. Sending error email to TPI for replacing the golden_basetp.')
            self.send_error_email('Bad golden_basetp', 'N/A', f'golden_basetp is bad for bom {self.bom}. Please update the golden_basetp.')

        else:
            self.send_error_email()

        self.hardBin_list = deque(maxlen=3)  # reset the hardBin_list
        log_files = glob.glob(f'{self.root}/golden_*.log')
        for log_file in log_files:
            log.info(f'Removing log file: {log_file}')
            os.remove(log_file)

    def write_result_golden(self, tf, code, out):
        """
        Write logfile for golden_basetp and golden_fulltp to skip writing result.json
        Write result.json only for normal tps
        :param tf: testprogram path
        :param code: code
        :param out: out text
        :return: None
        """
        if 'golden_basetp' in tf and code == 1:
            log.info(f'-i- Skipping write_result for golden_basetp {tf}')
            log.info(f'-i- golden_basetp failed with code {code}.')
            with open(f'{self.root}/golden_basetp_failed.log', 'w', encoding='utf-8') as f:
                f.write(f'{curtime()}: golden_basetp failed with code {code}.\n')
                f.write(f'Error: {out}\n')
        elif 'golden_basetp' in tf and code == 0:
            log.info(f'-i- golden_basetp {tf} passed with code {code}.')
            with open(f'{self.root}/golden_basetp_passed.log', 'w', encoding='utf-8') as f:
                f.write(f'{curtime()}: golden_basetp passed with code {code}.\n')
        elif 'golden_fulltp' in tf and code == 1:
            log.info(f'-i- golden_fulltp failed with code {code}.')
            with open(f'{self.root}/golden_fulltp_failed.log', 'w', encoding='utf-8') as f:
                f.write(f'{curtime()}: golden_fulltp failed with code {code}.\n')
                f.write(f'Error: {out}\n')
        elif 'golden_fulltp' in tf and code == 0:
            log.info(f'-i- golden_fulltp {tf} passed with code {code}.')
            with open(f'{self.root}/golden_fulltp_passed.log', 'w', encoding='utf-8') as f:
                f.write(f'{curtime()}: golden_fulltp passed with code {code}.\n')
        else:
            self.write_result(tf, code, out)

    def tpbot_3strike_logic(self, tf, found, code):
        """
        TPBOT 3 strike logic: If 3 consecutive same HardBin found, take action
        :param tf: testprogram path
        :param found: line containing HardBin info
        :param code: code
        :return: None
        """
        if BotOS.get_metafname(tf)[-1] == 'B':
            log.info(f'Found TPBOT job for {BotOS.get_metafname(tf)}. Recording HardBin.')
        else:
            log.info(f'Not a TPBOT job for {BotOS.get_metafname(tf)}. Skipping HardBin recording.')
            return

        hardBin = found.split("HardBin = ")[1].split(",")[0].strip()
        job_json = f'{BotOS.root}/pool/_metadata/{BotOS.get_metafname(tf)}.json'
        if os.path.exists(job_json):
            with open(job_json, 'r', encoding='utf-8') as f:
                job_data = json.load(f)
        else:
            log.info(f'Job json file does NOT exist: {job_json}. Cannot get PR number.')
            job_data = {}

        pr_number = job_data.get('job', 'notfound')
        if pr_number != 'notfound':
            log.info(f'PR Number: {pr_number} for hardbin: {hardBin}')
        else:
            log.info(f'PR number is NOT found for hardbin: {hardBin}')
            return

        if f'{hardBin}-{pr_number}' not in self.hardBin_list:
            self.hardBin_list.append(f'{hardBin}-{pr_number}')
        else:
            log.info(f'HardBin {hardBin} with PR number {pr_number} is already in the list. Not appending again.')
        log.info(f'HardBin list: {self.hardBin_list}')

        load_and_run_data = self.tp_options
        if not load_and_run_data:
            return

        repo = load_and_run_data.get('GITHUB_REPOSITORY', 'unknown')
        log.info(f'Repo: {repo}')
        if 'nvl.common' in repo and code == 0:
            log.info(f'Job is TPBOT from {repo} with code {code}.')
        else:
            log.info(f'Not copying full TP common to central golden FULL TP. Repo: {repo}, code: {code}.')
            return

        log.info(f'Copying full TP common to central golden FULL TP for {self.bom} for PR number {pr_number} with repository {repo}.')
        tarfiles = glob.glob(f'{self.root}/*.tar.gz')
        if not tarfiles:
            log.info(f'No tar.gz files found in {self.root}. Cannot copy full TP common to central golden FULL TP for {self.bom}.')
            return
        tarfiles = tarfiles[0]   # there should be only one .tar.gz
        golden_fulltp = f'{BotOS.root}/golden_check/golden_fulltp_{self.bom}'
        golden_fulltp_wip = f'{BotOS.root}/golden_check/golden_fulltp_{self.bom}.wip.tar.gz'
        if not os.path.exists(golden_fulltp):
            mkdirs(f'{BotOS.root}/golden_check/golden_fulltp_{self.bom}', mode='02770')
        elif (time.time() - os.path.getmtime(golden_fulltp)) <= (12 * 3600):
            log.info(f'Golden fulltp folder is less than 12 hours, age: {(time.time() - os.path.getmtime(golden_fulltp)) / 3600:.2f} hours')
            log.info(f'Skip copying full TP common to central golden FULL TP for {self.bom} due to golden fulltp is less than 12 hours old.')
        elif os.path.exists(golden_fulltp_wip):
            log.info(f'Golden fulltp wip tar.gz already exists. Skip copying full TP common to central golden FULL TP for {self.bom}.')
        else:
            log.info(f'Golden fulltp folder is older than 12 hours, age: {(time.time() - os.path.getmtime(golden_fulltp)) / 3600:.2f} hours')
            log.info(f'Proceed to copy full TP common to central golden FULL TP for {self.bom}.')
            shutil.copyfile(tarfiles, golden_fulltp_wip)

            # Extract to temp location, remove old golden_fulltp, then rename
            temp_extract = f'{golden_fulltp}_temp'
            mkdirs(temp_extract, mode='02770')
            untar(golden_fulltp_wip, f'{golden_fulltp}_temp')

            # Remove old golden_fulltp folder
            if os.path.exists(golden_fulltp):
                shutil.rmtree(golden_fulltp)
                log.info(f'Removed old golden_fulltp folder: {golden_fulltp}')

            # Rename temp folder to golden_fulltp
            shutil.move(temp_extract, golden_fulltp)
            log.info(f'Done generate the new golden full tp at {golden_fulltp}')
            # Remove the .wip tar.gz file
            os.remove(golden_fulltp_wip)


if __name__ == '__main__':  # pragma: no cover
    # no args
    if len(sys.argv) == 1:
        print(__doc__)
        exit(0)

    CheckerLog.setup(toolname='listener')      # all the log.info here are in tester/<tester>/listener_botos.txt file
    obj = ListenerBotOS()
    obj.main()
