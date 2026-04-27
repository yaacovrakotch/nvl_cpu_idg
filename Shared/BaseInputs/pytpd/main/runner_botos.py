#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Botos runner
Called from yml
Purpose is to "build" the tp, tar it, and save tar to staging area.

Usage:
   runner_botos.py arl_tpbot          # tpbot yml call (pr gate)
   runner_botos.py arl_mbot           # mbot or team bots (yml call)

   runner_botos.py nvl_simtpbot.nvls28c.nvl_cpu    # tpbot yml call (pr gate) - offline
   runner_botos.py nvl_tpbot.nvls28c.nvl_cpu       # tpbot yml call (pr gate) - real tester
   runner_botos.py nvl_mbot.<pkg>.<reponame>       # mbot or team bots (yml call)

Note1: arl will call TPBuild
       nvl will call TPBuildNVL

Note2: Currently, buildtp.py is doing the following
   1. create the tp: TPBuild() class   -> call this here (Runner)
   2. run in bot: Bot() class          -> call this in load_and_run.py

Strategy: We use env as a way to send arguments. This is always called from yml anyway.
    The following env are used:
        EMAIL: email used to inform user
        DEST:  destination folder (for mbot).
        IN1:   json_mv_string (or 'FULL')
"""
import setenv      # must be first in the imports
from gadget.gizmo import Elapsed
from gadget.files import TempDir, File
from gadget.disk import Chdir, mkdirs, get_free_diskspace, check_disk_threshold
from gadget.tputil import CheckerLog
from gadget.shell import untar, TarAdd
from gadget.pylog import log
from gadget.errors import confirm, ErrorUser
from gadget.getgit import GitHub
from gadget.lockfile import force_refresh
from gadget.strmore import curtime
from os.path import exists, dirname, basename, isdir
from main.manager_botos import BotOS
from main.nvl_buildtp import NVLBuildTP
from mod.affected_boms import AffectedBom
from tp.testprogram import TestProgram, Env
from pyqs import Merge
from gadget.tvpv import TvpvEnv
from pprint import pprint, pformat
import time
import glob
import sys
import os
import shutil


class RunnerBotOS:
    SLEEP_SEC = 5
    MAX_WAIT_SECS = 6 * 3600     # 6 hrs
    PRINT_EVERY_SEC = 60         # Print every 60 sec

    def __init__(self):
        confirm(len(sys.argv) == 2, 'Expecting one argument to the tool', 'refer to docstring')
        self.cmd = sys.argv[1]
        self.root = BotOS.root
        self.metafnames = {}      # {metafname: bom}
        self.summary = []

        # tester retest
        self.tmpdir_tar = TempDir()
        self.meta2tar = {}          # {metafname: (stagingdir, tar_path)}
        self.meta2meta = {}         # {metafname: meta_dict}
        self.metarelaunch = set()   # set of metafnames that is relaunched

    def main(self):
        """Main routine of runner"""

        if 'I_AM_TPI_Skip_Bot' in GitHub.get_labels():
            log.info('-i- Skipping TPBot for all BOMs due to I_AM_TPI_Skip_Bot')
            return 1

        self.special_asis()

        for bom in self.affected_boms(is_tpbot=True, cmd=self.cmd):
            self.main_onetp(bom)

        log.info('\nSummary: ===============')
        for line in self.summary:
            log.info(line)
        log.info('')

        # Wait for job to finish for tpbot ===================
        self.tpbot_wait()
        self.tmpdir_tar.close()    # Delete retest tempdir

    @classmethod
    def special_asis(cls):
        """Updates IN1 and DEST env var based on special value, like NOLOAD"""
        rootspecial = Env.xpath('/intel/tpvalidation/engtools/tptools/mtl/infra/torch/special_asis')

        if isdir(rootspecial):
            special = os.listdir(rootspecial)
        else:
            special = []

        if os.environ.get('IN1') in special:
            name = os.environ['IN1']
            os.environ['IN1'] = 'ASIS'
            os.environ['DEST'] = f'{rootspecial}/{name}'
            log.info(f'Setting ASIS to {rootspecial}/{name}')

    @classmethod
    def _decode_cmd(cls, cmd, enbom):
        """
        Decode and return the final cmd since bom is encoded (output of affected_boms()):
            <nvl2_simtpbot|nvl2_tpbot>.<pkginfo>.<bom>

        :param cmd: string <cmd>.<bom>.<dielet>.[pkginfo]
        :param enbom: encoded bom, with ".", <nvl2_simtpbot|nvl2_tpbot>.<pkginfo>.<bom>
        :return: final cmd: (jobtype, bom, repo, pkginfo) or (jobtype, bom, repo)

        """
        # decode the enbom
        if '.' in enbom:
            ccmd, pkginfo, bom = enbom.split('.')
        else:
            pkginfo = None
            bom = enbom
            ccmd = None

        # parse the cmd
        final = cmd   # asis
        elems = cmd.split('.')
        if not ccmd:
            ccmd = elems[0]

        if len(elems) == 3:
            if pkginfo:
                final = f'{ccmd}.{bom}.{elems[2]}.{pkginfo}'
            else:
                final = f'{ccmd}.{bom}.{elems[2]}'
        elif len(elems) == 4:
            final = f'{ccmd}.{bom}.{elems[2]}.{elems[3]}'     # pkginfo from cmd takes over because it is specified in yml

        elem_len = len(final.split('.'))
        confirm(elem_len == 1 or elem_len == 4 or elem_len == 3,
                f'Error: cmd={cmd} enbom={enbom} final={final}',
                'Logic error: expecting 3 or 4 elems on final. Contact jqdelosr.')

        return final

    def main_onetp(self, bom):
        """Submit one tp"""
        # Check DEST environment variable (user specified destination)
        dest_path = os.environ.get('DEST', '')
        check_disk_threshold(dest_path, threshold_gb=2)

        prno = GitHub.get_prno()                  # TODO: Make this run id for mbot
        author = GitHub.get_pr_info('author')     # TODO: This is empty if mbot since there is no PR
        url = GitHub.get_pr_info('url')
        cmd = self._decode_cmd(self.cmd, bom)
        log.info(f'-i- encoded_bom: {bom}')
        log.info(f'-i- final_cmd:   {cmd}')
        with TempDir(name=True) as tdir:

            # Build the testprogram to tdir =======================
            sw = Elapsed()
            log.info('-i- Starting TP Build')
            with Chdir(os.getcwd()):        # so that cwd will be put back
                timestamp = self.get_timestamp_msec()
                NVLBuildTP.JOBID = timestamp
                job_letter, package, repo = self.get_job_type(cmd, tdir)
                metafname = f'{timestamp}_{job_letter}'

            # TODO: Write the branch name to a file. This file is read by load_and_run.py

            # Write the load_and_run.json file to pass the mbot options to tester
            self.write_bot_options(tdir, package=package, job_letter=job_letter, repo=repo)

            # tar the tp ==============================
            log.info(f'-z- Elapsed TP Build: {sw}')
            log.info('-i- Starting TP tar')
            sw = Elapsed()
            with Chdir(tdir):
                fullpath = f'{self.root}/staging/{package}/8000_{metafname}.tar.wip.gz'
                mkdirs(dirname(fullpath), mode='02775')
                TarAdd(fullpath, '.')

                # copy the tp to destination if specified
                json_input = os.environ.get('IN1', '')
                if json_input != 'ASIS_LOCAL':
                    self.copy_tp(fullpath, os.environ.get('DEST', ''), json_input)

                # copy to retest folder
                File(fullpath).copy(self.tmpdir_tar.name())
                self.meta2tar[metafname] = (dirname(fullpath), f'{self.tmpdir_tar.name()}/{basename(fullpath)}')

                # rename the wip to non-wip so botos can now run it
                fp = File(fullpath).rename(basename(fullpath).replace('.tar.wip.gz', '.tar.gz'))    # remove the .wip
                log.info(f'-z- Elapsed Tar: {sw}')

                # Summary print
                msg = f'-i- Written {bom}: {fp.get_name()}'
                log.info(msg)
                self.summary.append(msg)

            # write the metadata =======================
            fullpath = f'{self.root}/staging/_metadata/{metafname}.json'
            mkdirs(dirname(fullpath), mode='02775')
            data = {'job': prno,
                    'repo': repo,
                    'url': url,
                    'author': author,
                    'pkg': package,
                    'email': os.environ.get('EMAIL', ''),
                    'site': TvpvEnv.get_site(),
                    'team': os.environ.get('TEAM', ''),
                    'tester': os.environ.get('TESTER', 'Any')}
            log.info(pformat(data))
            BotOS.json.dump(fullpath, data)
            self.meta2meta[metafname] = data

            # add this in list of jobs
            self.add_tpbot_wait(job_letter, metafname, bom)

    def add_tpbot_wait(self, job_letter, metafname, bom):
        """
        Add metafname if tpbot

        :param job_letter: letter
        :param metafname: fname
        :param bom: bomname
        :return:
        """
        url = "https://tvpv.pdx.intel.com/cgi-bin/bots-dashboard/mbot_dashboard.cgi"
        if job_letter == 'B':     # B is tpbot
            self.metafnames[metafname] = bom
        elif job_letter == 'D':
            print(f"Job is submitted. Goto {url} to check status. Job id: {metafname}")
            print("Note: Your TeamBot job is submitted. You should have received an email from "
                  "'frombot' with the tester name. Please claim the tester within 30 mins. "
                  "If not, your job queue will be cancelled.")
        else:
            print(f"Job is submitted. Goto {url} to check status. Job id: {metafname}")
            print("Note: Your mbot job is submitted. However, it is NOT YET COMPLTED. "
                  "Please check the link above and you will receive an email when it is completed.")

    def write_bot_options(self, tdir, package="NA", job_letter="NA", repo="NA"):
        """Write BOT options to a load_and_run.json file, and tester will be able to read it."""
        bot_vars = dict(os.environ.items())
        bot_vars['package'] = package
        bot_vars['job_letter'] = job_letter
        bot_vars['repo'] = repo
        load_and_run_options = f'{tdir}/load_and_run.json'
        BotOS.json.dump(load_and_run_options, bot_vars)

    @classmethod
    def copy_tp(cls, tarfname, dest, json):
        """
        Copy the testprogram to the destination drive
        :param tarfname: path to tarfile
        :param dest: destination dir, specified from yml. Will incremental rename if folder already exist.
        :param json: mvjson
        :return: unittest only
        """

        if (not dest) or len(dest) == 3:    # Why 3? because of yml default of "I:/"
            return 1       # do nothing, no destination specified
        if json == 'ASIS':
            return 2       # do nothing, because dest is source
        if isdir(dest):
            File(dest).rename_incremental()    # rename existing dir

        # write it
        untar(tarfname, dest)

    def tpbot_wait(self):
        """
        Wait for results to finish for all tpbots
        :return: unittest only
        """
        folder = f'{self.root}/completed'
        lastprint = 0
        sw = Elapsed()
        allfnames = ','.join(sorted(self.metafnames))
        print(f'-i- Will wait for botos to finish: completed/{allfnames}')

        results = set()          # set of {metafname.json}
        resultretest = set()     # set of retested metafname.json
        for _ in range(int(self.MAX_WAIT_SECS / self.SLEEP_SEC)):
            force_refresh(folder)
            completed = os.listdir(folder)

            for metafname in list(self.metafnames):
                fname = f'{metafname}.json'
                if fname in completed and fname not in results:
                    results.add(fname)
                    print(f'-z- {curtime()} Completed: {fname}({self.get_metabom(fname, short=True)}): {len(results)} of {len(self.metafnames)}')
                    self.tester_retest(folder, metafname, resultretest)

            # do some printing
            if (time.time() - lastprint) > self.PRINT_EVERY_SEC:
                wip = ','.join(sorted({f'{x}.json({self.get_metabom(x, short=True)})' for x in self.metafnames} - results))
                wip = 'ALL DONE' if not wip else wip
                print(f'-z- {curtime()} Total: {len(self.metafnames)}; Waiting for {wip}')
                lastprint = time.time()

            # check if done
            if len(results) == len(self.metafnames):
                break

            time.sleep(self.SLEEP_SEC)
        else:
            GitHub.add_labels({'FAILED'})
            raise ErrorUser(f'Timeout occurred while waiting for {folder}/{allfnames}',
                            'Did the tester run?')

        # read it
        log.info(f'-z- TPBot wait Elapsed: {sw}')
        failed = set()
        for fname in results:
            retest = '-FIRST_RETESTED' if fname in resultretest else ''
            log.info(f'######### {fname} ({self.get_metabom(fname)}){retest}:')
            data = BotOS.json.load(f'{folder}/{fname}', 'tpbot_wait()')

            # Display info
            for line in BotOS.message_results(data):
                log.info(line)

            if fname in resultretest:
                continue     # ignore the retested tests

            if data.get('code', 1):
                log.info(f'{fname} FAILED.')
                failed.add(f'FAILED_{self.get_metabom(fname, short=True)}')

        if failed:
            GitHub.add_labels(failed)    # TODO: Distinguish between Si, init or load fail?
            exit(1)    # fail

        # This is commented out since yml add the label
        # else:
        #     if self.metafnames:
        #         GitHub.add_labels({'PASSED_Si'})       # Add labels only for tpbot runs

    def get_metabom(self, fname, short=False):
        """
        Given the metafname, return the bomname

        :param fname: fname without extension
        :param short: if True, return shortened version based on product type
        :return: bomname
        """
        fname = fname.replace('.json', '')
        if fname not in self.metafnames:
            return 'NoBOM'
        bom = self.metafnames[fname].split('.')[-1]

        if short:
            first_letter = ''    # default empty for NVL
            parts = bom.split('_')

            # Check if it's an NVL product, add the first letter
            if 'NVL' not in bom:
                if len(parts) >= 3:  # Ensure we have at least Class_XXX_YYY format
                    first_letter = parts[1][0]  # First letter of product (DNL->D, RZL->R)

            return f"{first_letter}{parts[-1]}"  # DS28C, RS28C
        else:
            return bom

    def tester_retest(self, complete_dir, metafname, resultretest):
        """
        Do the tester relaunch logic
        :param complete_dir: botos root/completed folder
        :param metafname: metafname only
        :param resultretest: set of metafname dictionary
        :return:
        """
        # read first
        fname = f'{metafname}.json'
        data = BotOS.json.load(f'{complete_dir}/{fname}', 'tester_retest()')

        # Do nothing if pass
        if not data.get('code', 1):
            return 1     # pass

        # was this relaunched already?
        if metafname in self.metarelaunch:
            return 2     # already relaunched

        # get tester
        if 'tester' not in data:
            log.info(f'-w- tester_retest(): {metafname} does not have tester data')
            return 3     # no tester info

        # are there enough testers?
        stagingdir, tmptar = self.meta2tar[metafname]
        cnt_file = f'{self.root}/tpbot_count/{basename(stagingdir)}'
        if not exists(cnt_file):
            log.info(f'-w- tester_retest(): {cnt_file} does not exist')
            return 5

        tpbot_cnt = int(File(cnt_file).read().strip())
        if tpbot_cnt <= 1:
            log.info(f'-w- tester_retest(): tpbot_count is {tpbot_cnt}. No tester to resubmit to.')
            return 6

        # write the tar file
        newmetafname = self._incmeta(metafname)
        self.metarelaunch.add(newmetafname)
        fp = File(tmptar)
        fp.rename(f'7000_{newmetafname}.tar.gz')    # no need for .tar.wip in staging since metadata.json is needed
        fp.copy(stagingdir)

        # write metadata
        datam = self.meta2meta[metafname]
        failtester = data['tester'].split()[-1]    # "JF: JF04TXBT62017A"
        datam['tester'] = f'!{failtester}'
        BotOS.json.dump(f'{self.root}/staging/_metadata/{newmetafname}.json', datam)
        logline = data.get('comment', 'n/a')
        log.info(f'-i- {metafname}: {logline}')
        log.info(f'-i- tester_retest(): failtester={failtester} from:{metafname} to:{newmetafname}')

        # update self.metafnames
        self.metafnames[newmetafname] = self.metafnames[metafname]
        resultretest.add(fname)
        return 4

    @classmethod
    def _incmeta(cls, metafname):
        """increment the metafname by 1"""
        elems = metafname.split('_')
        return f'{int(elems[0]) + 1}_{elems[1]}'

    @classmethod
    def get_timestamp_msec(cls):
        """
        Return current time in milliseconds
        :return: int. digit is in milleseconds
        """
        epoch = time.time()
        msecs = int(epoch) * 1000       # This is UTC time, so same baseline across sites
        msecs += int((epoch - int(epoch)) * 1000)
        return msecs

    @classmethod
    def get_job_type(cls, cmd, tdir):       # pragma: no cover
        """
        Return the job type, etc
        :param cmd: input command from yml
        :param tdir: destination tempdir
        :return: job_letter, package, repo
        """
        # this is old - unused
        if cmd.startswith('nvl_'):       # pragma: no cover
            jobtype, package, repo = cmd.split('.')
            cls.do_nvl_build(tdir, package, repo, jobtype, os.environ.get('IN1', ''))
            return 'B', 'sim', repo

        # nvl jobs: nvl2_simmbot, nvl2_simtpbot
        if cmd.startswith('nvl2_'):

            elems = cmd.split('.')
            if len(elems) == 3:
                jobtype, bom, repo = elems                      # traditional
                pkginfo = f'nvl{bom.split("_")[-1].lower()}'    # autoderived
            else:
                jobtype, bom, repo, pkginfo = elems      # encoded

            cls.do_nvl2_build(tdir, bom, repo, jobtype, os.environ.get('IN1', ''))
            if jobtype == 'nvl2_simtpbot':
                return 'B', 'sim', repo
            elif jobtype == 'nvl2_tpbot':
                return 'B', pkginfo, repo
            elif jobtype == 'nvl2_mbot':
                return 'E', pkginfo, repo
            elif jobtype == 'nvl2_simmbot':
                return 'E', 'sim', repo
            elif jobtype == 'nvl2_teambot':
                return 'D', pkginfo, repo
            else:
                raise ErrorUser(f'Invalid nvl2 command: {jobtype}', 'Contact taipham or jqdelosr')

        raise ErrorUser(f"Invalid argument: {cmd}", 'Refer to docstring for valid args.')

    @classmethod
    def do_nvl2_build(cls, tdir, package, repo, jobtype, json):
        """
        Do the nvl build - Rev1
        Latest and Current way.

        :param tdir: destination tempdir
        :param package: bom name
        :param repo: repo name
        :param jobtype: nvl_simtpbot | nvl_tpbot | nvl_mbot
        :param json: mvjson string
        :return:
        """
        # TODO: add jobtype differentiation here?

        # create the TP
        os.rmdir(tdir)     # tempdir should not exist for copytree or Integrate

        if json == 'ASIS':
            log.info(f"-i- ASIS command detected: {os.environ['DEST']}")
            shutil.copytree(os.environ['DEST'], tdir, ignore=lambda *x: ['.git', 'temp'])
        elif json == 'ASIS_LOCAL':
            log.info(f"-i- ASIS_LOCAL command detected: {os.environ['DEST']}")
            log.info(f"-i- Create tdir folder: {tdir}")
            mkdirs(tdir, mode='02775')
            load_from_local = f'{tdir}/load_from_local.txt'
            File(load_from_local).touch(os.environ["DEST"], newfile=True)
        else:
            with TempDir(name=True) as tdir2:
                NVLBuildTP.main_flow_onebom(package,
                                            is_common=bool(repo == 'nvl_common'),
                                            is_tpbot=True,
                                            outdir=tdir,
                                            tempdir=tdir2)

    @classmethod
    def affected_boms(cls, bom='none', is_tpbot=False, cmd='none'):
        """
        This returns list of affected boms, based on PR modified files
        This routine must return one element for ARL (so we don't break ARL)

        The control on NVL is via:
           POR_TP/*/InputFiles/bot.<name>.<pkginfo>    # name is nvl2_simtpbot|nvl2_tpbot

        Example:
           POR_TP/Class_NVL_S28C/InputFiles/bot.nvl2_simtpbot.nvls28c
           POR_TP/Class_NVL_S28C/InputFiles/bot.nvl2_tpbot.nvls28c

        Encoded bom:
           nvl2_simtpbot.<pkginfo>.<bom>

        :param bom: specific bom or none (for all boms)
        :param is_tpbot: Set to True if caller is for tpbot; False (default) if called by checkers.
        :return: list of boms or encoded boms
        """
        allboms = sorted(basename(x) for x in glob.glob('POR_TP/Class_*'))

        if 'TARGETBOM' in os.environ:     # This is set by tpbot|mbot yml (from the mbot form)
            # tpbot|mbot yml: desired boms
            if os.environ['TARGETBOM'] == 'ALL':
                targetboms = allboms
            else:
                targetboms = os.environ['TARGETBOM'].split(',')

            ccmd = cmd.split('.')[0]
            result = []
            for bom_item in targetboms:
                confirm(bom_item in allboms,
                        f'Input BOM [{bom_item}] is invalid. Valid list is: {allboms}',
                        'Fix the input bom name in the form. Make sure it is case sensitive.')

                # Convert Class_NVL_S28C to nvls28c
                if cmd.split('.')[-1] in ('nvl_dielet', 'nvl_common'):
                    pkg_info = bom_item.replace('Class_', '').replace('_', '').lower()
                else:
                    pkg_info = cmd.split('.')[-1]

                new_bom = f'{ccmd}.{pkg_info}.{bom_item}'
                result.append(new_bom)

        elif bom.lower() == 'none':
            # tpbot yml: all boms

            if is_tpbot:     # return encoded boms: nvl2_simtpbot|nvl2_tpbot>

                if 'Class_NVL_S28C' in allboms:      # aka, NVL
                    # NVL case
                    bot_cfg = sorted(glob.glob('POR_TP/*/InputFiles/bot.*'))      # bot.nvl2_simtpbot.<BOM>
                    if bot_cfg:
                        result = []
                        for ff in bot_cfg:
                            tbom = basename(dirname(dirname(ff)))
                            result.append(f'{basename(ff)[4:]}.{tbom}')
                    else:
                        result = allboms

                else:
                    # non-nvl, return as-is
                    result = allboms
            else:
                # non-runner_botos, return all boms
                result = allboms

        else:
            # arl and all others
            result = [bom]      # fixed bom based on input

        # PR-based affected bom
        if 'REPO_DIR' in os.environ:     # it is PR
            abom_list = AffectedBom().main()
            final = []
            for item in result:
                for abom in abom_list:
                    if abom in item:
                        final.append(item)
                        break
            result = final

        log.info(f'-i- affected_boms(): {result}')
        return result

    @classmethod
    def do_nvl_build(cls, tdir, package, repo, jobtype, json):     # pragma: no cover   - OLD code, unused
        """
        Do the nvl build - Rev0 (old way)

        :param tdir: destination tempdir
        :param package: package name
        :param repo: repo name
        :param jobtype: nvl_simtpbot | nvl_tpbot | nvl_mbot
        :param json: mvjson string
        :return:
        """
        # TODO: add json info here
        # TODO: code json=='ASIS' here, see do_arl_build()
        raise ErrorUser('do_nvl_build() is now obsolete', 'Update your branch to latest main')

        from main.nvl_buildtp import BuildCommon

        if repo == 'nvl_common':
            tp = BuildCommon().main('nvl.cpu', 'main', 'None')   # TODO: Add spawning option here

            # Call pyqs - required for tpbot main
            tpobj = TestProgram('POR_TP/Class_NVL_S28C/EnvironmentFile.env', allpats=True).init()        # Reload obj after cleantp
            obj = Merge(tpobj)
            obj.importall()
            obj.main()
            obj.write_file('final_qs.xml')

        else:
            tp = '.'

        os.rmdir(tdir)     # tempdir should not exist for copytree
        shutil.copytree(tp, tdir, ignore=lambda *x: ['.git', 'temp'])


if __name__ == '__main__':  # pragma: no cover
    CheckerLog.setup(toolname='runner')
    obj = RunnerBotOS()
    obj.main()
