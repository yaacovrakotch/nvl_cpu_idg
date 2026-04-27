#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Automatic run of ctp

Usage, login to plxv9021 as jqdelosr:
   source /p/pde/tvpv/mtl/sourceme.rc
   cd /intel/tpvalidation/engtools/tptools/mtl/plan_waivers/trigger
   /intel/tpvalidation/engtools/tptools/mtl/beta/pytpd.jqdelosr/main/ctp_cron.py | tee -a log

For debug and development:
   ctp_cron.py -once
"""

import setenv        # must be first in the imports
from gadget.shell import SystemCall, CALLERBIN
from gadget.strmore import curtime
from gadget.disk import Chdir
from gadget.helperclass import OnceADay
from gadget.gizmo import send_mail, Elapsed
from gadget.files import File
from gadget.disk import mkdirs, listdir_noerror
from gadget.errors import confirm
from collections import defaultdict
from os.path import exists, basename, dirname
from mod.db_ctp import Compas, MainCgi, HSDCache, CTPCache, CtpRepo
from main.transfer import TTP
import re
import time
import os
import glob
import sys
import requests
import json
import urllib3
urllib3.disable_warnings()


class CTPCron:
    """
    Inifinite loop run
    """

    def __init__(self):
        self.repopath = '/intel/tpvalidation/jqdelosr/tp_plans/CronConfig'
        self.jsonroot = '/intel/tpvalidation/engtools/tptools/mtl/plan_waivers/jsonall'
        self.desc = {}
        self.cmds = {}
        self.git_checkout = {}
        self.trig_dir = {}
        self.out_dir = {}
        self.emails = {}
        self.env_list = {}
        self.glob_env = {}      # '*/EnvironmentFile.env' for eseu.py, '*' for direct

        self.read_cfgs()

    def read_cfgs(self):
        self.desc = {}
        self.cmds = {}
        self.git_checkout = {}
        self.trig_dir = {}
        self.out_dir = {}
        self.emails = {}
        self.env_list = {}
        self.glob_env = {}

        # read all jsons
        idx = 0
        keywords = 'desc cmds git_checkout trig_dir out_dir emails glob_env env_list'.split()
        for ff in sorted(glob.glob(f'{self.repopath}/*.json')):
            # check if debug run for specific json
            debugset = None
            for item in sys.argv:
                if item.endswith('.json'):
                    debugset = basename(item)
            if debugset:
                if basename(ff) != debugset:
                    print(f'-d- Skipping {basename(ff)} because {debugset} is specified')
                    continue

            # start of algo
            idx += 1
            with open(ff) as fh:
                try:
                    data = json.load(fh)
                except Exception as e:
                    print(f'-e- skipping {ff}: {e}')
                    continue

            error = False
            for item in keywords:
                if item not in data:
                    print(f'-w- {ff} is ignored: {item} is missing')
                    error = True
                if item in ('emails', 'env_list'):
                    if not isinstance(data[item], list):
                        print(f'-w- {ff} is ignored: {item} is not a list')
                        error = True

            if error:
                continue

            # Check correctness of rsync command
            if data['cmds'].startswith('eseu.py'):
                if self.derive_args(data['cmds'], ff) is None:
                    continue

            # Check correctness of glob_env
            if data['cmds'].startswith('eseu.py'):
                if not data['glob_env'].endswith('.env'):
                    print(f'-w- {ff} glob_env is incorrect. Expecting endswith(.env)')
                    continue
            else:
                if '/' in data['glob_env']:
                    print(f'-w- {ff} glob_env is incorrect. Expecting no path, it should only be wildcard')
                    continue

            # print(f'-i- key={idx} json={basename(ff)}')
            for item in keywords:
                var = getattr(self, item)
                var[idx] = data[item]

        # Make sure these are consistent
        assert self.desc.keys() == self.git_checkout.keys()
        assert self.desc.keys() == self.trig_dir.keys()
        assert self.desc.keys() == self.emails.keys()
        assert self.desc.keys() == self.env_list.keys()
        assert self.desc.keys() == self.glob_env.keys()
        assert self.desc.keys() == self.cmds.keys()
        assert self.desc.keys() == self.out_dir.keys()

    def disp(self, txt):
        """Display txt with time"""
        print(f'{curtime()}: {txt}')

    @classmethod
    def derive_args(self, cmd, fname=None):
        """
        Derive host, rpath, tlpath, dest from cmd
        Why? because the json config is an rsync command
        """
        res = re.search(r"rsync \S+ ([^:]+):(\S+) (\S+)", cmd)
        if not res:
            return None
        return {'host': res.group(1),
                'rpath': res.group(2),
                'tlpath': f'{res.group(3)}/rsync_tpname',
                'dest': f'{res.group(3)}/tp'}

    def xfer(self, cmd, key):
        """
        Returns list of testprogram directories that needs to be run

        :return: set of testprogram directories
        """
        if cmd.startswith('eseu.py'):
            args = self.derive_args(cmd)
            obj = TTP(host=args['host'], eseu=True)
            try:
                final = obj.main(rpath=args['rpath'],
                                 genv=self.glob_env[key],
                                 tlpath=args['tlpath'],
                                 dest=args['dest'])
            except Exception as e:
                print(e)
                return set()

            return set(final)

        # direct method
        processed_dir, src = cmd.split()
        with Chdir(src):
            validtp = set(glob.glob(self.glob_env[key]))
        final = set()
        for ff in set(os.listdir(src)) - set(os.listdir(processed_dir)):
            if ff in validtp:
                self.disp(f"Will process {src}/{ff} ...")
                final.add(f'{src}/{ff}')
            else:
                self.disp(f"Skipping {src}/{ff} since it is not valid based on glob_env")
            File(f'{processed_dir}/{ff}').touch()
        return final

    def proc_rsync_output(self, txt, cmd):
        """
        Process rsync output
        :param txt: rsync output
        :param cmd: rsync cmd (to derive full path)
        :return: set of directories
        """
        robj = re.compile(r"^(\w+/\w+)")
        root = cmd.split()[-1]
        result = set()
        for line in txt.split('\n'):
            if not line or line.startswith(('receiving incremental', 'sent ', 'total size')):
                continue
            res = robj.search(line)
            if res:
                result.add(f'{root}/{res.group(1)}')
        return result

    def is_trig(self):
        """
        Checks trigger directory

        :return: dict: {key: set of which TP to trigger}. Empty dict if no trigger
        """
        result = defaultdict(set)
        for key, trigdir in self.trig_dir.items():
            mkdirs(trigdir, mode='02775')
            for ff in os.listdir(trigdir):
                if self.cmds[key].startswith('eseu'):
                    tpdir = '%s/tp' % self.cmds[key].split()[-1]
                else:
                    tpdir = self.cmds[key].split()[-1]
                targ = f'{tpdir}/{ff}'
                if exists(targ):
                    print(f'-i- Trigger found: {targ}')
                    result[key].add(targ)
                else:
                    # get latest TP
                    latest = ""
                    for tpff in sorted(listdir_noerror(tpdir), key=lambda x: os.path.getmtime(f'{tpdir}/{x}')):
                        latest = f'{tpdir}/{tpff}'
                    print(f'-w- Trigger file: {targ} is not found. Using latest instead: {latest}')
                    result[key].add(latest)
                self.delete(f'{trigdir}/{ff}')
        return result

    def delete(self, fname):      # rmdir or unlink
        """Remove this fname (file or dir)"""
        if os.path.isdir(fname):
            os.rmdir(fname)
        else:
            os.unlink(fname)

    def get_envfile(self, tpdir, env_list):
        """
        Get the environment file

        :param tpdir: testprogram dir
        :param env_list: list of env file to match
        :return: Envfile
        """
        # first occurance
        for targ in env_list:
            if exists(f'{tpdir}/{targ}'):
                return targ

        return None

    def run(self, trig_tppaths):
        """
        Execute one run for all released testprograms

        :param trig_tppaths: set of trig_tppaths
        :return: None
        """
        if trig_tppaths:
            for key in trig_tppaths:
                self.disp(f"Start of Run {key} =================")
                cmd = self.cmds[key]
                tp_list = self.xfer(cmd, key)
                for tpdir in tp_list | trig_tppaths[key]:
                    with Chdir(self.git_checkout[key]):
                        self.one_run(key, tpdir)
        else:
            self.disp("Start of Run ALL =================")
            for key, cmd in self.cmds.items():
                self.disp(f"Run: {key}: {self.desc[key]}")
                tp_list = self.xfer(cmd, key)
                for tpdir in tp_list:
                    with Chdir(self.git_checkout[key]):
                        self.one_run(key, tpdir)

    def one_run(self, key, tpdir):
        """
        Execute one testprogram
        :param key: numerical key
        :param tpdir: testprogram dir
        :return: None
        """
        cmd = 'git pull'
        self.disp(f"CMD: {cmd}")
        _, res = SystemCall(cmd).run_outtxt()
        print(res)

        allpy = ' '.join(glob.glob('*.py'))
        envfile = self.get_envfile(tpdir, self.env_list[key])
        if not envfile:
            print(f'ERROR: No environment file found for item#{key}: {tpdir}')
            return 1

        mkdirs(self.out_dir[key], mode='02775')
        outfile = f'{self.out_dir[key]}/{basename(tpdir)}.csv'
        if self.desc[key].startswith('ctp1'):
            cmd = f'{dirname(CALLERBIN)}/tp_plans.py -tp {tpdir}/{envfile} {allpy} -out {outfile}'
        else:
            cmd = f'{dirname(CALLERBIN)}/tp_plans.py -tp {tpdir}/{envfile} -pipeline ./ -out {outfile}'

        self.disp(f"CMD: {cmd}")
        ecode, res = SystemCall(cmd).run_outtxt()
        print(res)
        if ecode:   # pragma: no cover
            try:
                send_mail('grp_vep2_no_reply@intel.com',
                          self.emails[key],
                          f'CTP Fail: {basename(tpdir)}',
                          f'TPDir: {tpdir}\n\n{res}')
            except Exception:
                print(f'-e- Error sending email {self.emails[key]}: {basename(tpdir)}')

        return 0

    def compass_refresh(self):     # pragma: no cover   - for now
        """Refresh compass"""
        url = 'http://compass.app.intel.com/api/mfg_readiness/plan_vs_actual?plc_stage=Post-Si'
        sw = Elapsed()
        response = requests.get(url)
        try:
            result = response.json()
        except requests.exceptions.JSONDecodeError as e:
            print(f"Error reading json! {e}")
            return

        if len(result) < 10:
            print(f"ERROR reading compass api: {len(result)}")
            return

        cl = Compas.ALL_DATA
        File(f'{cl}.wip').touch(json.dumps(result, indent=3), newfile=True)
        File(cl).unlink()
        File(f'{cl}.wip').rename(basename(cl))
        print(f'-i- {curtime(human=True)} compass refresh at {sw}')

    def compass_refresh_presi(self):     # pragma: no cover   - for now
        """Refresh compass"""
        url = 'http://compass.app.intel.com/api/mfg_readiness/plan_vs_actual?plc_stage=Pre-Si'
        sw = Elapsed()
        response = requests.get(url)
        try:
            result = response.json()
        except requests.exceptions.JSONDecodeError as e:
            print(f"Error reading json! {e}")
            return

        if len(result) < 10:
            print(f"ERROR reading compass api: {len(result)}")
            return

        cl = f'{Compas.ALL_DATA}_presi'
        File(f'{cl}.wip').touch(json.dumps(result, indent=3), newfile=True)
        File(cl).unlink()
        File(f'{cl}.wip').rename(basename(cl))
        print(f'-i- {curtime(human=True)} compass presi refresh at {sw}')

    @classmethod
    def write_json(cls, fname, data):
        """Write data into a json file, using .wip bkm"""
        with open(f'{fname}.wip', 'w') as fh:
            fh.write(json.dumps(data, indent=3))
        if exists(fname):
            os.unlink(fname)
        os.rename(f'{fname}.wip', fname)

    def json_files(self):
        """Generate all the json files"""

        sw = Elapsed()
        CtpRepo.git_pull(False)
        HSDCache.fetch()
        CTPCache.fetch()
        print(f'-i- Read db: {sw}. hsd: {len(HSDCache.data())}, ctp: {len(CTPCache.data())}')

        speedsoc = defaultdict(set)

        # A - toc
        sw = Elapsed()
        obj = MainCgi({'toc': 'all', 'internal': 'True'}, is_conn2=True)
        self.write_json(f'{self.jsonroot}/toc_all.json', obj.result)
        # print(f'-i- #A toc_all in {sw}')
        for x in obj.result[0]['contents']:
            speedsoc[x['speedid']].add(x['socket'])

        # B - map file for each speedid
        for sid in sorted(speedsoc):
            mkdirs(f'{self.jsonroot}/{sid}', mode='02775')
            obj = MainCgi({'toc': 'map', 'speedid': sid, 'internal': 'True'}, is_conn2=False)
            self.write_json(f'{self.jsonroot}/{sid}/map.json', obj.result)
            # print(f'-i- #B {sid} in {sw}')

        # C - toc ww
        for sid in sorted(speedsoc):
            for soc in sorted(speedsoc[sid]):
                obj = MainCgi({'toc': 'ww', 'speedid': sid, 'socket': soc, 'internal': 'True'}, is_conn2=False)
                self.write_json(f'{self.jsonroot}/{sid}/{soc}.wwtoc.json', obj.result)
                # print(f'-i- #C {sid},{soc} in {sw}')

                # D - data
                for x in obj.result[0]['contents']:
                    ww = x['ww']
                    obj = MainCgi({'ww': ww,
                                   'speedid': sid,
                                   'socket': soc,
                                   'override': 'True',
                                   'detail': 'True',
                                   'internal': 'True'},
                                  is_conn2=False)
                    self.write_json(f'{self.jsonroot}/{sid}/{ww}.{soc}.data.json', obj.result)
                    # print(f'-i- #D {sid},{soc},{ww} in {sw}')

            # Delete old files (CRNT)
            sroot = f'{self.jsonroot}/{sid}'
            for ff in os.listdir(sroot):
                fobj = File(f'{sroot}/{ff}')
                if fobj.age() > 86400:
                    fobj.unlink()

        print(f'-i- Completed jsonall in {sw}')

    def main(self, loop=10000000, nap=60):
        """
        Entry point, infiniteloop (well, 19 years worth of loop)

        :param loop: Max loop
        :param nap: sleep time in seconds
        :return: None
        """
        isdebug = bool('-once' in sys.argv)
        istime = OnceADay(2)  # 2am PST, 12 noon IDC, 6pm PG
        prevtime = time.time()
        for _ in range(loop):

            try:
                # every 20 min run
                if isdebug or (time.time() - prevtime) > (60 * 20):   # 20 mins
                    self.compass_refresh()
                    self.compass_refresh_presi()
                    self.read_cfgs()
                    prevtime = time.time()

                # once a day cron
                trig_paths = self.is_trig()
                if trig_paths or istime() or isdebug:
                    self.run(trig_paths)

                # generate the json files
                self.json_files()

            except Exception as e:
                self.disp(f"Exception: {e}")

            # re-loop
            if isdebug:
                return

            time.sleep(nap)


if __name__ == '__main__':  # pragma: no cover
    # CTPCron().json_files()
    CTPCron().main()
