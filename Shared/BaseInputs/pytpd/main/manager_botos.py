#!/usr/intel/pkgs/python3/3.12.3/bin/python3 -u
"""
botos manager

Usage:
   cd /intel/tpvalidation/engtools/tptools/mtl/beta/latest/main
   manager_botos.py start              # as a cron, in unix
   manager_botos.py -check <site>      # check datahost in a particular site
"""
import setenv      # must be first in the imports
from gadget.files import TempDir, File
from gadget.gizmo import Elapsed, send_mail
from gadget.tputil import CheckerLog
from gadget.disk import listdir_noerror, mkdirs, scandir_mtime, delete_oldest
from gadget.shell import HOSTNAME, USERNAME
from gadget.shell import SystemCall, IS_UNIX
from gadget.dictmore import keys_atlevel, key_exist, DictDot
from gadget.pylog import log
from gadget.errors import confirm, ErrorCockpit, ErrorUser
from gadget.data_host import DataHost
from gadget.strmore import curtime
from gadget.tvpv import TvpvEnv
from gadget.helperclass import IS_UT, AutoRestart, OPT
from gadget.vepargs import Args, TA_All, TA_StoreTrue, TA_Store
from collections import defaultdict, OrderedDict
from functools import partial
from os.path import exists, isdir, dirname, basename
from pprint import pprint
import re
import time
import glob
import sys
import os
import json


# TODO: Code to delete residual files (aka, metadata.json that does not have tar file)
# TODO: In pool/_metadata/<file>.json, add info on which tester is the job run at.
# TODO: Delete completed/* tp_rolling_botos/* files older than 5 days
# TODO: If rsync fails, it will retry every 5 seconds. Send email if this happens? Show in status web.
# TODO: Q1: website to manually re-prioritize number
# TODO: Move sitecfg_common.PG.hosts so that we can add or remote machine without change in code


class ManagerEntry(Args):

    def config(self):
        """
        Define the arguments for the script.
        The order below will matter, it is the order of display during help.
        """
        cfg = DictDot()
        cfg.all = TA_All('see usage')
        cfg.check = TA_Store('Check datahost server', metavar=','.join(Remote._SITES))
        cfg.force = TA_StoreTrue('Force restart of cron ignoring running processes (be careful with using this!).')
        return cfg

    def main(self):
        """Main Entry point"""
        if OPT.all and OPT.all[0] == 'start':
            AutoRestart(f'{BotOS.root}/logfiles/manager_botos.log')
            CheckerLog.setup(toolname='manager')
            ManagerBotOS().main()
            return 1

        self.call_methods(['check',     # this will call do_check(), if -check
                           ])

    def do_check(self):
        """Check a specific datahost site"""
        obj = Remote()
        obj.sites = {OPT.check: Remote._SITES[OPT.check]}
        pprint(obj.get_tester_files())


class Remote:
    """Class that takes care of remote things"""
    _SITES = {'PG': ('https://tvpv.png.intel.com/cgi-bin/pytpdhost.cgi',
                     '/intel/tpvalidation/engtools/tptools/mtl/beta/latest',
                     'tgl.py'),    # Yeah, this is old, but this is the only one
              'FM': ('https://tvpv.fm.intel.com/cgi-bin/pytpdhost.cgi',
                     '/intel/tpvalidation/engtools/tptools/mtl/beta/latest',
                     'tgl.py'),    # Yeah, this is old, but this is the only one
              'IDC': ('https://tvpv.iil.intel.com/cgi/pytpdhost.cgi',
                      '/intel/tpvalidation/engtools/tptools/mtl/beta/latest',
                      'tgl.py'),    # Yeah, this is old, but this is the only one
              'BA': ('https://tvpv1.iind.intel.com/cgi-bin/pytpdhost.cgi',
                     '/intel/tpvalidation/engtools/tptools/mtl/beta/latest',
                     'tgl.py'),    # Yeah, this is old, but this is the only one
              'JF': ('https://tvpv.pdx.intel.com/cgi-bin/pytpdhost.cgi',
                     '/intel/tpvalidation/engtools/tptools/mtl/beta/latest',
                     'tgl.py')    # Yeah, this is old, but this is the only one
              }
    # _SITES = {}

    def __init__(self, check=False):
        self.selfsite = TvpvEnv.get_site()
        self.sites = {x: y for x, y in self._SITES.items() if x != self.selfsite}
        self._origsites = dict(self.sites)
        if check:
            self._check_sites(False)

    def move_job(self, infile, tester):
        """
        Given the job from pool, move it remotely
        This is called when job is in PG and tester is in PG (and botos in JF)

        :param infile: {job}.remote
        :param tester: which tester will it move to
        :return: unittest only
        """
        confirm(infile.endswith('.remote'), f'Expecting .remote file. Received: {infile}', 'Check algo')
        site, pkg, job = File(infile).read().split()
        if site in self.sites:
            DataHost().central('move_job', (pkg, job, tester), check=True, urp=self.sites[site])
        else:
            log.flush(f'-i- remote move_job() site not exist: {site} {pkg} {job}')
        return site, pkg, job

    def cleanup_dir(self, folders_to_clean):
        """
        Cleanup these folders remotely

        :param folders_to_clean: dict {folder: max_count}
        :return: list of deleted folders
        """
        result = []
        for site in self.sites:
            data = DataHost().central('cleanup_dir', folders_to_clean, check=True, urp=self.sites[site])
            for ff in data:
                log.info(f'-i- remote cleanup_dir {site}: {ff}')
                result.append(f'{site} {ff}')
        return result

    def get_tester_files(self):
        """
        get tester files in all the sites with age

        :return: {(site, tester): {fname: age}}
        """
        result = {}
        for site in self.sites:
            data = DataHost().central('get_files', False, check=True, urp=self.sites[site])
            result.update({(site, x): y for x, y in data.items()})
        return result

    def get_staging_files(self):
        """
        get all files in all the sites with age

        :return: {site: {pkg: {fname: age}}
        """
        result = {}
        for site in self.sites:
            data = DataHost().central('get_files', True, check=True, urp=self.sites[site])
            result[site] = data
        return result

    def delete_files(self, for_delete):
        """
        Delete the files remotely
        :param for_delete: {site: [fullpath]}
        :return:
        """
        for site in for_delete:
            if site in self.sites:
                data = DataHost().central('delete_files', for_delete[site], check=True, urp=self.sites[site])
                for line in data.split('\n'):
                    log.flush(f'-i- [{site}] {line}')
            else:
                log.flush(f'-i- remote delete_files() site not exist: {site}: {for_delete[site]}')

    def get_meta_content(self):
        """
        Read the staging meta content and put in dictionary
        :return: dict {site: {fname: value}}
        """
        result = {}
        for site in self.sites:
            result[site] = DataHost().central('get_meta_content', None, check=True, urp=self.sites[site])
        return result

    def write_files(self, fname, text):
        """
        Write fname in remote sites with text
        :param fname: path/fname
        :param text: contents
        :return: None
        """
        if IS_UT:
            return 0

        for site in self.sites:
            DataHost().central('write_file', (fname, text, True), check=True, urp=self.sites[site])
        return 1

    def write_json(self, site, data, nrfname, folder):
        """
        Write json file in this site

        :param site: site string
        :param data: data structure to write
        :param nrfname: filename
        :param folder: which folder
        :return: None
        """
        if site in self.sites:
            res = DataHost().central('write_json', (data, nrfname, folder), check=True, urp=self.sites[site])
            log.flush(f'write_json(): site={site}: {res}')
        else:
            log.flush(f'-i- remote write_json() site not exist: {site} {nrfname} {folder}')

    def read_json(self, site, folder, tester, fname):
        """
        Read json file in this site

        :param site: site string
        :param folder: root folder
        :param tester: tester
        :param fname: filename
        :return: data
        """
        if site in self.sites:
            return DataHost().central('read_json', f'{folder}/testers/{tester}/{fname}', check=True, urp=self.sites[site])
        else:
            log.flush(f'-i- remote read_json() site not exist: {site} {folder} {tester} {fname}')

    def read_completed(self):
        """
        Read all json in completed folder for remote sites

        :return: {site: {filename: <data>} }
        """
        data = {}
        for site in self.sites:
            data[site] = DataHost().central('read_completed', None, check=True, urp=self.sites[site])
        return data

    def initial_stm(self):
        """
        Return the staging_files, tester_files and meta_content, while taking care of bad site
        """
        try:
            sfiles = self.get_staging_files()       # {site: {pkg: {fname: age}}}
            tfiles = self.get_tester_files()        # {(site, tester): {fname: age}}
            mfiles = self.get_meta_content()        # {site: {package: {fname: value}}}
            self._check_sites(True)                 # try to re-enable failed site

        except Exception as e:
            log.flush(f'-i- Remote() Exception: {e}')
            sfiles = {}
            tfiles = {}
            mfiles = {}
            self._check_sites(False)    # disable the site

        return sfiles, tfiles, mfiles

    def _check_sites(self, ispass):
        """
        Update self.sites depending if site is alive
        :param ispass: True if check for disabled sites
        :return:
        """
        if ispass:
            if self.sites == self._origsites:
                return 1    # Do nothing

        # at this point, need to update self.sites for sites that are alive
        self.sites = {}
        for site, urp in self._SITES.items():
            if site != self.selfsite:
                try:
                    DataHost().central('test1', 1, check=True, urp=urp)
                    self.sites[site] = urp
                except Exception:
                    pass


class ManagerBotOS:
    """Manager routines"""
    _is_ut_email = IS_UT

    def __init__(self):
        self.root = None         # Set in set_root()
        self.job_count = 0       # Number of jobs sent to a tester
        self.remote = Remote()
        self.set_root(BotOS.root)
        self.cleanup_last = time.time()
        self.idfile = f'logfiles/manager.id.{os.getpid()}.{HOSTNAME}'
        self.all_meta = {}       # metafname: <dictdata>
        self.teamweight = {}     # {team: count}

    def set_root(self, root):
        """Set root"""
        self.root = root
        mkdirs(f'{root}/pool/_metadata', mode='02775')
        mkdirs(f'{root}/testers', mode='02775')
        mkdirs(f'{root}/teams', mode='02775')

    def main(self, maxloop=63072000, sleeptime=5):     # this is 10 yrs at 5 sec sleep
        """This is the infinite loop"""

        # Start of daemon process
        self.check_running_process()

        # At this point, there is only one listener running.
        for _ in range(maxloop):
            AutoRestart()
            self.job_count = 0
            self.check_quit()

            try:
                self.main_one_run()
            except Exception as e:
                log.flush(f'-e- Exception main(): {e}')

            if not self.job_count:
                time.sleep(sleeptime)

        return 1

    def main_one_run(self):
        """
        Execute one big loop, for all packages

        Performance of main_one_run() per pkg:
            arlh68n3b run: 0.034 Secs
            arls68 run:    0.018 Secs
            arls68jf run:  0.018 Secs
            arls68n3b run: 0.019 Secs
            arlu28 run:    0.033 Secs
            nvlhx28c run:  0.019 Secs
            nvls28c run:   0.234 Secs
            nvls52c run:   0.061 Secs
            sim run:       0.048 Secs
            2025-08-22_10:56:23 one_run(): jobs=0, rsites=PG,FM, Elapsed=5.409 Secs

        :return: True if it did something, False if nothing
        """
        # step1 - loop to all the packages in the folder
        sw = Elapsed()

        self.read_teamweight()

        # sfiles (staging_files) = {site: {pkg: {fname: age}}}
        # tfiles (tester_files)  = {(site, tester): {fname: age}}
        # mfiles (meta_content)  = {site: {package: {fname: value}}}
        sfiles, tfiles, mfiles = self.remote.initial_stm()

        for pkg in self.get_pkgs(sfiles):
            self.main_one_package_run(pkg, sfiles, tfiles, mfiles)

        # process all results
        self.process_results(tfiles)

        # cleanup folders
        self.cleanup()

        validsites = ','.join(self.remote.sites)
        print(f'{curtime()} one_run(): jobs={self.job_count}, rsites={validsites}, Elapsed={sw}')

    def main_one_package_run(self, pkg, sfiles, tfiles, mfiles):
        """
        Execute one package. This is the "core" of botos

        :param pkg: package name
        :param sfiles: remote staging files dict {site: {folder: {fname: age}}}
        :param tfiles: remote tester files dict
        :param mfiles: remote metadata files content {site: {fname: value}}
        :return:
        """
        self.delete_old_teambot_jobs(pkg)

        # step2a - local - transfer jobs in staging to the pool/
        staging = f'{self.root}/staging'
        mfolder = listdir_noerror(f'{staging}/_metadata')
        for item in listdir_noerror(f'{staging}/{pkg}'):
            mname = BotOS.get_metafname(item)
            if item.endswith('.tar.gz') and f'{mname}.json' in mfolder:
                try:
                    File(f'{staging}/{pkg}/{item}').move(f'{self.root}/pool/{pkg}')
                    File(f'{staging}/_metadata/{mname}.json').copy(f'{self.root}/pool/_metadata')
                    File(f'{staging}/_metadata/{mname}.json').unlink()
                    File(f'{self.root}/pool/_metadata/{mname}.json').chmod('0777')
                except Exception as e:
                    log.flush(f'-e- Exception staging->pool on {item}: {e}')

        # step2b - remote - write jobs to pool/
        for site in sfiles:
            for folder in sfiles[site]:
                if folder != pkg:       # accept only this pkg
                    continue

                for item in sfiles[site][folder]:
                    if not item.endswith('.tar.gz'):
                        continue

                    # Do not write if file already exist since it was written earlier
                    remotefile = f'{self.root}/pool/{pkg}/{item}.remote'
                    if exists(remotefile):
                        continue

                    # Write the .remote file in pool
                    File(remotefile).touch(f'{site} {pkg} {item}', newfile=True, mode='0777')
                    metaname = f'{BotOS.get_metafname(item)}.json'
                    if key_exist(mfiles, site, metaname):
                        mpath = f'{self.root}/pool/_metadata/{metaname}'
                        BotOS.json.dump(mpath, mfiles[site][metaname])
                    else:
                        log.flush(f'-w- No metadata found in remote {site},{metaname}')

        # step3 - get all available testers (local and remote)
        # testers = {(is_local, tester): testertype}
        # physical = {(site, pkg): {tester: team}}
        testers, physical = self.get_available_testers(pkg, tfiles)
        testerteam = self.get_testerteam(testers, physical, pkg)

        # step4a - read all metadata and store
        self.read_all_metadata(f'{self.root}/pool/_metadata')

        # step4 - send the job to the tester (local or remote)
        for tester in self.sorted_tester_teams(testers, physical):
            job = self.sorted_top_job(pkg, testers[tester], tester=tester[1], team=testerteam[tester])
            try:
                std_tester = self.send(job, tester, pkg)
                self.update_metafile(std_tester, job)
            except Exception as e:
                log.flush(f'-e- Exception send(): {e}')

    def send(self, job, local_tester, pkg):
        """
        Send the job to this tester.
        tester is either local or remote depending on job name

        case1: runner is botos site (local), tester is botos site (local)
        case2: runner is remote site PG, tester PG is remote site (same site)
        case3: runner is botos site, tester is remote
        case4: runner is remote site, tester is local
        case5: runner is remote site PG, tester FM is remote site (different site)

        :param job: job file name
        :param local_tester: (is_local, tester)
        :param pkg: package
        :return: tester tuple (site, testername) or None
        """
        if not job:
            return None      # Do nothing

        sw = Elapsed()
        self.job_count += 1
        is_local, tester = local_tester

        # get the tester site
        tester_site = None
        if is_local:
            log.flush(f'-i- Sending: pool/{pkg}/{job} to {tester}')
            std_tester = (self.remote.selfsite, tester)
        else:
            tester_site, tester_remote = tester
            std_tester = tester
            log.flush(f'-i- Sending: pool/{pkg}/{job} to @{tester_site}:{tester_remote}')

        # get job site
        job_site = None
        if job.endswith('.remote'):
            job_site, job_pkg, job_fname = File(f'{self.root}/pool/{pkg}/{job}').read().split()
            log.flush(f'-i- remote job: site={job_site} pkg={job_pkg} fname={job_fname}')
            if job_pkg != pkg:     # safety check only to ensure our algo is good
                log.flush(f'-w- {job_fname} is remote={job_pkg} but processing {pkg}')

        # case1: tester is botos site (local), runner is botos site (local)
        if is_local and (not job.endswith('.remote')):
            File(f'{self.root}/pool/{pkg}/{job}').rename(f'{job}.wip.gz')
            File(f'{self.root}/pool/{pkg}/{job}.wip.gz').move(f'{self.root}/testers/{tester}')
            File(f'{self.root}/testers/{tester}/{job}.wip.gz').rename(job)

        # case2: tester PG is remote site, runner is remote site PG (same site)
        elif (not is_local) and job.endswith('.remote') and tester_site == job_site:
            self.remote.move_job(f'{self.root}/pool/{pkg}/{job}', tester_remote)
            remote_meta_path = f'{self.root}/staging/_metadata/{BotOS.get_metafname(job)}.json'
            self.remote.delete_files({job_site: [remote_meta_path]})
            File(f'{self.root}/pool/{pkg}/{job}').unlink()

        # case3: tester is remote, runner is local (botos site)
        elif (not is_local) and (not job.endswith('.remote')):
            jobpath = f'{self.root}/pool/{pkg}/{job}'
            File(jobpath).push_remote(f'{self.root}/testers/{tester_remote}', tester_site)
            File(jobpath).unlink()

        # case4: tester is local, runner is remote site
        elif is_local and job.endswith('.remote'):
            remote_path = f'{self.root}/staging/{job_pkg}/{job_fname}'
            remote_meta_path = f'{self.root}/staging/_metadata/{BotOS.get_metafname(job_fname)}.json'
            File(remote_path).copy_remote(f'{self.root}/testers/{tester}', job_site)
            self.remote.delete_files({job_site: [remote_path, remote_meta_path]})
            File(f'{self.root}/pool/{pkg}/{job}').unlink()

        # case5: tester FM is remote site, runner is remote site PG (different site)
        elif (not is_local) and job.endswith('.remote') and tester_site != job_site:
            remote_path = f'{self.root}/staging/{job_pkg}/{job_fname}'
            remote_meta_path = f'{self.root}/staging/_metadata/{BotOS.get_metafname(job_fname)}.json'
            File(remote_path).another_remote(f'{self.root}/testers/{tester_remote}', job_site, tester_site)
            self.remote.delete_files({job_site: [remote_path, remote_meta_path]})
            File(f'{self.root}/pool/{pkg}/{job}').unlink()

        else:   # pragma: no cover
            raise ErrorCockpit("Unknown case. What happened here???", "Contact jqdelosr or kliew2")

        log.flush(f'-i- {curtime()} send: {pkg}, {job}, {local_tester}, completed in {sw}')
        return std_tester

    def update_metafile(self, std_tester, job):
        """Add the tester in the metafile - needed by dashboard"""
        if not std_tester:
            return    # Do nothing if no tester

        metafullpath = f'{self.root}/pool/_metadata/{BotOS.get_metafname(job)}.json'
        if not exists(metafullpath):
            log.flush(f'-e- {metafullpath} does not exist. Cannot add tester info in update_metafile()')
            return None

        metadata = BotOS.json.load(metafullpath, 'update_metafile()')

        # add tester info
        metadata['tester'] = f'{std_tester[0]}: {std_tester[1]}'

        BotOS.json.dump(metafullpath, metadata)

    def get_available_testers(self, pkg, tfiles):
        """
        Return list of available testers (local and remote)
        How about new tester? listener will create folder automatically

        :return: ({(is_local, tester): testertype},
                  {(site, pkg): list_of_testers})
        """
        available = {}
        physical = {}

        # local first
        self._process_available(available, True, pkg, BotOS.get_files_local(time.time()), physical)

        # remote next
        self._process_available(available, False, pkg, tfiles, physical)

        # write available tpbot counts
        self.write_tpbot_count(pkg, BotOS.get_files_local(time.time()), tfiles)

        return available, physical

    def _process_available(self, available, is_local, pkg, data, physical):
        """
        Process available testers given the data structure

        :param available: resultant list of available testers: OrderedDict {(is_local, tester): testertype}
        :param is_local: True for local, False for remote
        :param pkg: package
        :param data: {tester: {fname: age}}    # tester = folder if is_local else (site, tester) for remote
        :param physical: resultant list of physical testers: {(site, pkg): {tester: team}}.
        :return: Nothing
        """
        for tester in sorted(data):
            if f'{pkg}.package.info' not in data[tester]:
                continue         # wrong package
            if data[tester].get('idle.status', 0) > 900:       # 15 mins
                continue         # this tester does not have listener running
            if 'stop' in data[tester]:
                continue         # there is a stop signal
            if 'down' in data[tester]:
                continue         # there is a stop signal
            if 'reserved' in data[tester]:
                continue         # there is a reserved signal.

            # Determine the type
            if 'type1.info' in data[tester]:
                testertype = 1       # tpbot and mbot only
            elif 'teambotonly.info' in data[tester]:
                testertype = 3       # teambot only
            else:
                testertype = 2       # Any job (tpbot, mbot, teambot)

            # get physical testers for teambots use
            self._update_physical(physical, pkg, tester, data, is_local, testertype)

            # tester is busy states
            if 'idle.status' not in data[tester]:
                continue         # not idle
            if [x for x in data[tester] if x.endswith('.tar.gz')]:
                continue         # there is a .tar.gz already there

            # assign it
            available[(is_local, tester)] = testertype

    def _update_physical(self, physical, pkg, tester, data, is_local, testertype):
        """
        Process the physical dictionary
        """
        # Get the key for physical
        if is_local:
            site = TvpvEnv.get_site()
        else:
            site = tester[0]
        key = (site, pkg)

        if key not in physical:       # initialize
            physical[key] = {}

        # get if team is allocated
        team_allocated = ''
        for ff in data[tester]:
            if ff.endswith('.team'):
                team_allocated = ff.split('.')[0]

        # tpbot
        if testertype == 1:
            team_allocated = 'tpbot'

        if is_local:
            physical[key][tester] = team_allocated
        else:
            physical[key][tester[1]] = team_allocated

    def write_tpbot_count(self, pkg, data1, data2):
        """
        This routine is it's own box.

        Purpose is to write available tpbots testers, so that tester-retest (runner_botos) knows if it will resend
        or not. It will only resend if there are >1 tester available for that package.

        Write to root/tpbot_count/{pkg}

        :param pkg: pkg we are working on
        :param data1: local data
        :param data2: remote data
        :return: None
        """
        count = 0
        for data in (data1, data2):
            for tester, dt in data.items():
                set_dt = set(dt)
                if f'{pkg}.package.info' not in dt:
                    continue         # wrong package
                if 'type1.info' not in dt:       # count only type1.info testers. type2 testers are only opportunistic.
                    continue         # allow type1 only
                if not ({'idle.status', 'running.status'} & set_dt):
                    continue         # not valid
                if 'idle.status' in dt and dt['idle.status'] > 900:       # 15 mins
                    continue         # this tester does not have listener running
                if {'stop', 'down', 'reserved'} & set_dt:
                    continue         # tester is stopped or downed

                count += 1

        # write local first
        targ = f'{self.root}/tpbot_count/{pkg}'
        if exists(targ):
            try:
                prevcnt = int(File(targ).read().strip())
            except ValueError:
                prevcnt = 0
        else:
            prevcnt = 0

        if prevcnt == count:
            return count      # no change needed, current is correct

        # write local
        log.info(f'-i- write_tpbot_count() pkg={pkg} count={count}')
        File(targ).touch(f'{count}\n', newfile=True, mkdir=True, mode='770')

        # write remote
        self.remote.write_files(targ, f'{count}\n')
        return -1

    def _keyteam(self, is_local, site, tester):
        """Give the key that is compatible to available testers"""
        if is_local:
            return tuple((is_local, tester))
        else:
            return tuple((is_local, (site, tester)))

    def get_testerteam(self, testers, physical, pkg='none'):
        """
        Calculate and Map the available testers given physical testers and create dict

        # testers(available) = OrderedDict {(is_local, tester): testertype}
        # physical(all_testers) = {(site, pkg): {tester: team}}
        # self.teamweight = {team: count}
        # allocated = {tester: team}

        :param testers: dict available testers
        :param physical: dict physical testers
        :param pkg: which package
        :return: dictionary {(is_local, tester): team}
        """
        # get % per team (all testers). This percentages is used across site+package combination
        total_team = sum(self.teamweight.values())
        pct = {x.lower(): (y * 100.0 / total_team) for x, y in self.teamweight.items()}

        # assign the testers
        result = {}

        for site_pkg in sorted(physical):     # group according to site+package

            # initialize vars
            site, pkg = site_pkg
            is_local = bool(site == TvpvEnv.get_site())
            used = defaultdict(int)
            unknown = {v for v in physical[site_pkg].values() if v and v.lower() not in pct} | {'tpbot'}
            total_site_pkg = len([k for k, v in physical[site_pkg].items() if v not in unknown])

            # first pass - used
            for tester, team in sorted(physical[site_pkg].items()):
                team = team.lower()
                if team:
                    result[self._keyteam(is_local, site, tester)] = team
                    used[team] += 1

            # second pass - percentage
            for tester, useteam in sorted(physical[site_pkg].items()):
                if not useteam:
                    for team in sorted(pct):
                        if ((used[team] + 1) * 100.0 / total_site_pkg) <= pct[team]:
                            result[self._keyteam(is_local, site, tester)] = team
                            used[team] += 1
                            break

            # third pass - remainder - leave empty
            for tester, team in sorted(physical[site_pkg].items()):
                key = self._keyteam(is_local, site, tester)
                if key not in result:
                    result[key] = ''

        debugdata = {'percentage': pct,
                     'physical_and_occupied': {str(x): y for x, y in physical.items()},
                     'result': {str(x): y for x, y in result.items()}}
        mkdirs(f'{self.root}/tpbot_count')
        BotOS.json.dump(f'{self.root}/tpbot_count/_teambots_allocation.{pkg}.json', debugdata)
        return result

    def process_results(self, tfiles):
        """
        Read the <job>.result.json, delete it and delete _metadata

        :param tfiles: remote tester files
        :return:
        """
        # local first
        self._process_results(True, BotOS.get_files_local(time.time()))

        # remote next
        self._process_results(False, tfiles)

    def _process_results(self, is_local, files):
        """
        Read the <job>.result.json, delete it and delete _metadata

        :param is_local: True if local
        :param files: {tester: {fname: age}}
        :return: None
        """
        for_delete = defaultdict(list)    # {site: [f'{realtester}/{fname}']}
        for tester in files:
            for fname in files[tester]:
                self.send_email_teambot(fname, is_local, tester, for_delete)

                if fname.endswith('.result.json'):
                    # read the metadata
                    nrfname = fname.replace('.result', '')
                    metafullpath = f'{self.root}/pool/_metadata/{nrfname}'
                    if exists(metafullpath):
                        print(f"Reading {metafullpath}")
                        metadata = BotOS.json.load(metafullpath, '_process_results(1)')
                    else:
                        log.flush(f'-e- METADATA is missing: {metafullpath}')
                        metadata = {}

                    if is_local:
                        # read <job>.result.json
                        data = BotOS.json.load(f'{self.root}/testers/{tester}/{fname}', '_process_results(2)')

                        # write completed/<job>.json (on the runner location)
                        data['pkg'] = metadata.get('pkg', '')
                        data['email'] = metadata.get('email', '')
                        data['tester'] = metadata.get('tester', '')
                        data['url'] = metadata.get('url', '')
                        self.write_completed(data, metadata.get('site'), nrfname)

                        # delete <job>.result.json
                        log.flush(f'-i- Delete (local): {tester}/{fname}')
                        File(f'{self.root}/testers/{tester}/{fname}').unlink()        # delete it

                    else:
                        site, realtester = tester
                        data = self.remote.read_json(site, self.root, realtester, fname)

                        # write completed/<job>.json (on the runner location)
                        data['pkg'] = metadata.get('pkg', '')
                        data['email'] = metadata.get('email', '')
                        data['tester'] = metadata.get('tester', '')
                        data['url'] = metadata.get('url', '')
                        self.write_completed(data, metadata.get('site'), nrfname)

                        # delete <job>.result.json later
                        for_delete[site].append(f'{self.root}/testers/{realtester}/{fname}')

                    self.send_email_mbot(fname, data)

                    # Delete the pool/_metadata/<job>
                    log.flush(f'-i- {curtime()} Delete (local): pool/_metadata/{nrfname}')
                    File(metafullpath).unlink()   # delete it

        # ask datahost to delete these files
        self.remote.delete_files(for_delete)

    def read_all_metadata(self, metadir):
        """Read all json files in metafolder and save it in memory"""
        allff = set()
        cnt = 0
        for ff in os.listdir(metadir):
            if not ff.endswith('.json'):
                continue    # ignore

            allff.add(ff)

            if ff in self.all_meta:
                continue    # already read, ignore

            cnt += 1
            self.all_meta[ff] = BotOS.json.load(f'{metadir}/{ff}', 'read_all_metadata()')

        # delete items which are not in pool anymore
        for item in list(set(self.all_meta) - allff):
            del self.all_meta[item]

        return cnt     # number of read

    def send_email_teambot(self, fname, is_local, tester, for_delete):
        """
        Send email for teambots
        The root/testers/email1.<jobid>.command is written by load_and_run.py
        :return: None
        """
        if not fname.startswith('email1.'):
            return 1

        jobid = fname.split('.')[1]
        jobid = BotOS.get_metafname(jobid)

        # Delete the email filename
        if is_local:
            File(f'{self.root}/testers/{tester}/{fname}').unlink()
        else:
            site, realtester = tester
            for_delete[site].append(f'{self.root}/testers/{realtester}/{fname}')

        subject = f'teambot job is ready: {jobid}'
        message = f'''
Proceed to {tester}

Click on "I'm here" button to start your session.
When you are done, click on "I'm Done" to end the session and release tester.
Be sure to put the golden unit back if you have removed it.
The tester will be released automatically 30 mins from INIT completion if you have not taken the tester.
Max of 6 hrs of tester use, unless you RENEW it. Each renew is 2 hours. To renew click on "TeamBotStarted" button.

Be sure to check the 'Expiry Time' column on tester dashboard to confirm you have tester:
https://tvpv.pdx.intel.com/cgi-bin/bots-dashboard/mbot_dashboard.cgi?tester=True
'''
        self.email_now(jobid, subject, message)

    def send_email_mbot(self, fname, jsondata):
        """
        Send email for mbot
        :return: None
        """
        if not fname.endswith(('_E.result.json', '_A.result.json')):
            return 1

        jobid = fname.split('.')[0]
        subject = f'mbot job complete: {jobid}'
        message = '\n'.join(BotOS.message_results(jsondata))
        self.email_now(jobid, subject, message)

    def email_now(self, jobid, subject, message):
        """
        Read the metadata json and send email
        :param jobid: jobid
        :param subject: subject
        :param message: message
        :return:
        """
        log.flush(f'email_now({subject})')

        # Read the metadata json to get email address ====================
        metafile = f'{self.root}/pool/_metadata/{jobid}.json'
        if not exists(metafile):
            log.flush(f'-e- {metafile} not exist. Cannot send email.')
            return 2

        data = BotOS.json.load(metafile, 'email_now()')

        # Send the email ==================
        if not data.get('email'):
            log.flush(f'-e- {metafile} does not have email.')
            return 3

        confirm(not self._is_ut_email, 'Cannot send email in unittest', 'pls set _is_ut_email to False')

        try:
            send_mail('frombot', data['email'], subject, message)
        except Exception as e:      # pragma: no cover
            log.info(f'Error: send_mail(): {e}')

    def write_completed(self, data, site, nrfname):
        """
        Write completed json

        :param site: string, site where runner came from
        :param nrfname: string, no-result-filename
        :return:
        """
        if (not site) or site == self.remote.selfsite:   # runner site is equal to botos site
            if not exists(f'{self.root}/completed/{nrfname}'):
                # write it directly
                BotOS.json.dump(f'{self.root}/completed/{nrfname}', data)

        else:
            # Write the data via datahost
            self.remote.write_json(site, data, nrfname, f'{self.root}/completed')

    def get_pkgs(self, rfiles):
        """
        Iterator, return all pkgs (local and remote)
        :param rfiles: {site: {pkg: {} } }
        :return: sorted valid packages
        """
        # get list of local package from staging
        local_pkg = set()
        for pkg in os.listdir(f'{self.root}/staging'):
            if isdir(f'{self.root}/staging/{pkg}'):
                local_pkg.add(pkg)

        # get list of remote packages
        remote_pkg = keys_atlevel(rfiles, 1)

        # return it
        for pkg in sorted(set(os.listdir(f'{self.root}/pool')) | set(remote_pkg) | local_pkg):
            if not exists(f'{self.root}/pool/{pkg}'):      # create pkg folder, if not exist
                mkdirs(f'{self.root}/pool/{pkg}', mode='02775')
            if not isdir(f'{self.root}/pool/{pkg}'):       # ignore non-folder
                continue
            if pkg == '_metadata':
                continue
            yield pkg

    def _parse_fname(self, job, _robj=re.compile(r'^(\d+)_(\d+)_(\w)')):
        """
        Parse the job filename
        :param job: filename
        :return: tuple (number, timestamp, job_letter)
        """
        res = _robj.search(job)
        if res:
            return int(res.group(1)), int(res.group(2)), res.group(3)
        else:
            return 100000, 10000000000, 'A'

    def _sort_routine(self, testertype, x):
        """
        Sorting routine based on job type -> priority number -> timestamp
        Based on the job filename
        type1: A,B,C,E,F
        type2: D,A,B,C,E,F
        :param testertype: 1 or 2
        :param x: the data being sorted
        :return: tuple (number, timestamp, job_letter)
        """
        number, timestamp, letter = self._parse_fname(x)
        if testertype == 2 and letter == 'D':
            return '@', number, timestamp    # @ char is earlier than A in ascii table
        else:
            return letter, number, timestamp

    def sorted_tester_teams(self, testers, physical):
        """
        Sort testers according to:

        local
            non-empty-team
            empty-team
        remote
            non-empty-team
            empty-team

        Purpose: 1. process local testers first
                 2. process testers with team name next
        """
        # testers = {(is_local, tester): testertype}
        # physical = {(site, pkg): {tester: team}}

        teamdict = {}
        for key in physical:
            for tester, team in physical[key].items():
                teamdict[tester] = team

        sorted_list = sorted(testers, reverse=True, key=lambda x: teamdict.get(x[1], ''))

        # local first
        result = []
        for tester in sorted_list:
            if tester[0]:
                result.append(tester)

        # remote next
        for tester in sorted_list:
            if not tester[0]:
                result.append(tester)

        return result

    def sorted_top_job(self, pkg, testertype=2, tester=None, team=''):
        """
        Read the pkg folder and give the highest priority job
        This routine is called for every available tester:
        aka, "given this available tester, which job will I submit?"

        :param pkg: package name
        :param testertype: 1 or 2
        :param tester: which tester (string for local, tuple for remote)
        :param team: which team is this tester allocated to
        :return: job file name
        """
        # get the real tester
        if isinstance(tester, tuple):
            realtester = tester[1]
        else:
            realtester = tester

        # first pass - specific tester
        testerspecific = set()
        for job in sorted(os.listdir(f'{self.root}/pool/{pkg}'), key=partial(self._sort_routine, testertype)):
            if not job.endswith(('.tar.gz', '.remote')):
                continue     # invalid file

            mfname = f'{BotOS.get_metafname(job)}.json'
            datameta = self.all_meta.get(mfname, {})
            _, _, letter = self._parse_fname(job)

            if datameta.get('tester', 'any').lower() == 'any':
                continue      # ignore this job since it is any
            if datameta.get('tester', 'any').lower().startswith('!'):
                continue      # ignore this job since it is negative

            if testertype == 1 and letter == 'D':
                continue   # don't allow teambot job in type1 tester

            if testertype == 3 and letter != 'D':
                continue   # don't allow mbot/tpbot job in type3 tester

            # at this point, tester is specified
            testerspecific.add(job)
            if realtester.lower().startswith(datameta['tester'].lower()):   # startswith
                return job    # return this job

        # second pass - normal
        for job in sorted(os.listdir(f'{self.root}/pool/{pkg}'), key=partial(self._sort_routine, testertype)):
            if not job.endswith(('.tar.gz', '.remote')):
                continue     # invalid file

            # negative tester
            mfname = f'{BotOS.get_metafname(job)}.json'
            datameta = self.all_meta.get(mfname, {})
            if datameta.get('tester', 'any').startswith('!'):
                avoidtester = datameta.get('tester', 'any').lower()[1:]
                if realtester.lower() == avoidtester:
                    continue    # cannot launch this job in this tester

            # normal case
            _, _, letter = self._parse_fname(job)

            if testertype == 1 and letter == 'D':
                continue   # don't allow teambot job in type1 tester
            if testertype == 3 and letter != 'D':
                continue   # allow only teambot job in type3 tester
            if job in testerspecific:
                continue   # do not launch job here, since it is tester specific
            if datameta.get('team', '') and team.lower() and datameta['team'].lower() != team.lower():
                continue   # This tester is not for this job

            # return the first valid job
            return job

        return None

    def cleanup(self, interval=3600):
        """Cleanup all necessary files, once per hour only"""
        if (time.time() - self.cleanup_last) < interval:
            return    # Do nothing

        folders_to_clean = {f'{self.root}/tp_rolling_botos': 100,
                            f'{self.root}/completed/*_B.json': 600,   # tpbot
                            f'{self.root}/completed/*_D.json': 100,   # teambot
                            f'{self.root}/completed/*_E.json': 200,   # mbot
                            }

        # cleanup local
        result = []
        for folder in folders_to_clean:
            res = delete_oldest(folder, keep=folders_to_clean[folder], message='-i- cleanup delete:')
            result.extend(res)

        # cleanup remote
        res = self.remote.cleanup_dir(folders_to_clean)
        return result + res         # for unittests

    def read_teamweight(self):
        """Read teams in root folder, store in self.teamweight"""
        result = {}
        for ff in os.listdir(f'{self.root}/teams'):
            if ff.endswith('.txt'):
                elems = ff.split('.')
                if len(elems) == 3:
                    result[elems[0]] = int(elems[1])

        self.teamweight = result

    def delete_old_teambot_jobs(self, pkg, _max=86400):
        """
        Delete teambot jobs older than 24 hrs.
        Folks does not want these as they are usually stale.
        Requested in NVL TP office Hours, group chat 9/19/25
        """
        folder = f'{self.root}/pool/{pkg}'
        with os.scandir(folder) as fhdir:
            for name, mtime in [(entry.name, entry.stat().st_mtime) for entry in fhdir]:
                if '_D.' in name:      # teambot only
                    if (time.time() - mtime) > _max:
                        mname = BotOS.get_metafname(name)
                        log.info(f'-i- Deleting OLD teambot: {name}')
                        File(f'{folder}/{name}').unlink()
                        File(f'{self.root}/pool/_metadata/{mname}.json').unlink()

    def check_running_process(self):
        """
        Make sure there is no parallel running process
        """
        import atexit
        res = glob.glob(f'{self.root}/logfiles/manager.id.*')
        if res:
            if OPT.force:
                File(res[0]).unlink()
            else:
                raise ErrorUser(f'file: {res} already exist. manager seems to be running.',
                                'Delete this file if the manager is not running.')

        File(f'{self.root}/{self.idfile}').touch(USERNAME, mkdir=True)
        atexit.register(self.close)

    def close(self):
        """Delete the id.file"""
        print(f'-i- Exiting... deleting {self.idfile}') if not IS_UT else None
        File(f'{self.root}/{self.idfile}').unlink()

    def check_quit(self):
        """check if quit file exist, so we can kill the manager. 'kill switch'"""
        quitfile = f'{self.root}/pool/_metadata/quit'
        if exists(quitfile):
            File(quitfile).unlink()
            self.close()    # delete the idfile
            log.flush(f'-i- quit file exist. Exiting')
            exit(0)


class _MyJson:
    """
    A json wrapper used in botos that is:
        json.dump: "thread" safe via .wip
        json.load: deletes blank json

    Usage: BotOs.json.load(filename, where)
           BotOs.json.dump(filename, data)
    """

    @classmethod
    def load(cls, fname, where):
        """
        json.load equivalent with these features:
            1. checks if file is zero. if so, delete it
            2. missing or failing will still raise exception
        :param fname: json file
        :param where: caller location
        :return: data
        """
        confirm(exists(fname), f'[{fname}] does not exist for json read', f'Caller: {where}')
        txt = File(fname).read()

        # Check if empty, if so, delete it
        if len(txt) == 0:
            log.info(f'-i- {fname} is empty. Deleting. Caller: {where}')
            File(fname).unlink()
            return {}

        try:
            data = json.loads(txt)
            return data
        except json.decoder.JSONDecodeError as e:
            log.info(f'-i- Error reading {fname} from {where}: {e}')
            raise

    @classmethod
    def dump(cls, fname, data):
        """
        json.dump equivalent with these features:
            1. Write to .wip first, then rename, so it's "thread" safe
            2. indent=3
            3. file permission 777

        :param fname: json file
        :param data: data
        :return: None
        """
        fobj = File(f'{fname}.wip')
        fobj.touch(json.dumps(data, indent=4), newfile=True, mode='0777')
        File(fname).unlink()
        fobj.rename(basename(fname))


class BotOS:
    """
    This class are common routines across manager/runner/lister
    All routines are be classmethod
    """
    json = _MyJson

    if IS_UNIX:
        root = '/intel/tpvalidation/engtools/tptools/mtl/infra/torch/botos'
    else:     # pragma: no cover
        root = 'I:/tpvalidation/engtools/tptools/mtl/infra/torch/botos'

    def __init__(self):              # pragma: no cover
        raise Exception("Invalid use. BotOs() class is classmethod only")

    @classmethod
    def get_files_local(cls, secs, is_staging=False):
        """
        Get all local files
        This is called directly or thru DataHost

        :param: is_staging: if True, return staging files:  {pkg: {fname: age}}
        :return: {tester: {fname: age}}
        """
        localdata = {}
        if is_staging:
            startdir = f'{cls.root}/staging'
        else:
            startdir = f'{cls.root}/testers'

        for folder in os.listdir(startdir):
            if not isdir(f'{startdir}/{folder}'):
                continue   # not a directory
            localdata[folder] = {basename(x): secs - y
                                 for x, y in scandir_mtime(f'{startdir}/{folder}')}
        return localdata

    @classmethod
    def get_meta_content(cls):
        """
        Get all meta content
        This is called by DataHost

        :return: {package: {fname: value}}
        """
        localdata = {}
        startdir = f'{cls.root}/staging/_metadata'

        for fname in os.listdir(startdir):
            if fname.endswith('.json'):
                data = BotOS.json.load(f'{startdir}/{fname}', 'get_meta_content()')
                localdata[fname] = data
        return localdata

    @classmethod
    def get_metafname(cls, jobfname):
        """
        Return the metafname given jobfname
        There is no extension

        :return: string: \\w+_\\w
        """
        elems = basename(jobfname).split('.')[0].split('_')
        if len(elems) == 3:
            return f'{elems[1]}_{elems[2]}'
        else:
            return basename(jobfname).split('.')[0]     # return as-is without the extension

    @classmethod
    def message_results(cls, data, _max=100):
        """Iterator - Return the lines of Completed information from results.json"""
        from main.listener_botos import ListenerBotOS
        tprolling = data.get('tprolling')
        site = data.get('site')

        # to take account of each log written, _1, _2, etc.
        for logs in ListenerBotOS.log_headers:
            for retest_count in range(_max):  # Max of 100 retests
                log_retest_count = f"{logs} {retest_count}" if retest_count else logs
                if log_retest_count in data:
                    yield f'{log_retest_count}:'
                    yield f'   Path:        {tprolling}/{basename(data[log_retest_count])}'
                    yield f'   Direct link: {cls.http_link(site, data[log_retest_count])}'
                else:
                    break

        yield f'listener (script) log file:'
        yield f'   Path:        {data.get("logfile")}'
        yield f'   Direct link: {cls.http_link(site, data.get("logfile"))}'

        yield f'trace lot#s: {data.get("tracelot", "None")}'
        yield f'exit code:   {data.get("code")}'
        yield f'Result:      {data.get("comment")}'

    @classmethod
    def http_link(cls, site, path):
        """Call datahost viewer given site"""
        if site and path:
            domain = TvpvEnv.site_to_domain(site)
            dirdate = basename(dirname(path))
            dirfname = basename(path)
            if site.upper() == 'BA':
                return f'https://tvpv1.{domain}.intel.com/cgi-bin/pr-report/cci_list.cgi?br=x&viewlog2=./{dirdate}/{dirfname}'
            else:
                return f'https://tvpv.{domain}.intel.com/cgi-bin/pr-report/cci_list.cgi?br=x&viewlog2=./{dirdate}/{dirfname}'
        else:
            return f'<no http link>'

    @classmethod
    def get_timesecs(cls, fname):
        """
        Given mbot fname, return the epoc time in seconds for further conversion
        :param fname: bot fname
        :return: secs (epoch)
        """
        fname = fname.split('.')[0]
        if '_' not in fname:
            return 0
        fname = fname.split('_')[-2]
        secs = int(int(fname) / 1000)
        return secs


if __name__ == '__main__':  # pragma: no cover
    ManagerEntry(desc=__doc__).main()
