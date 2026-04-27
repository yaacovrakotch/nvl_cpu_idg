#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Generate MV testprogram

torch_mv.py jsonname <outputdir>
"""
import setenv      # must be first in the imports
import glob
from gadget.vepargs import Args, TA_StoreBool, TA_All, TA_Store, TA_StoreTrue
from gadget.helperclass import OPT
from gadget.dictmore import DictDot
from gadget.pylog import log
from gadget.files import File, TempDir
from gadget.gizmo import Elapsed, CacheThis
from gadget.shell import SystemCall, IS_UNIX, IS_WIN
from gadget.tputil import CheckerLog
from gadget.errors import ErrorUser, ErrorInput, confirm, check
from gadget.disk import Chdir, mkdirs, rmtree
from gadget.strmore import indent
from gadget.data_host import DataHost
from tp.testprogram import TestProgram, Env
from os.path import basename, dirname, exists
from pprint import pprint
from main.torch_postproc import TorchPostProc
from main.torch_fixer import DoFixer
from mod.moduleskip import ModuleSkip
from mod.mtplencode import NPRTrigger
from collections import defaultdict, deque
from functools import partial
from mod.alttc import ALttc
import shutil
import re
import os
import json
import tarfile


# Below is a simple way to inform user if they are python version <3.5. This is checked before any other code during the Parsing phase.
f'If you see SyntaxError, this means your python version is old. Pls upgrade to python3.8 minimum: http://python.org/downloads'


class MVArg(Args):
    utobj = [None]

    def config(self):
        """
        Define the arguments for the script.
        The order below will matter, it is the order of display during help.
        """
        cfg = DictDot()
        cfg.all = TA_All('see usage')
        cfg.tp = TA_Store('Which POR_TP folder', metavar='por_tp_folder_name')
        cfg.fast = TA_StoreBool('Use fast method', default=False, metavar='true|false')
        cfg.notrigger = TA_StoreTrue('Do not trigger NPR')
        cfg.recipe = TA_StoreTrue('Generate recipe')
        cfg.nodel = TA_StoreTrue('Do not delete temp export folder')
        cfg.unix = TA_StoreTrue('Skip torch calls. Assume TPConfig/ is copied.')
        cfg.nobuild = TA_StoreTrue('Do not run Torch build')
        cfg.exever = TA_Store('Which Torch.exe version to use', metavar='latest|<ver>|3.11.0')
        return cfg

    def main(self):
        """Main Entry point"""
        self.call_methods(['future',    # this will call do_future(), if -future
                           ])

    def do_else(self):
        """
        Entry point to various fixers.
        Calling this script the 2nd time should *do nothing*
        """
        DoMV.display_jsons(OPT.all)
        confirm(len(OPT.all) == 2,
                f'Incorrect inputs. Expecting two arg input to torch_mv.py',
                f'Usage: torch_mv.py <modulefile.json> <output_dir>')

        mv = DoMV(tp=OPT.tp,
                  fast=OPT.fast,
                  nprtrigger=not OPT.notrigger,
                  recipe=OPT.recipe,
                  nodel=OPT.nodel,
                  nobuild=OPT.nobuild)
        mv.main(OPT.all[0], OPT.all[1])

        self.utobj[0] = mv   # unittest only


class DoMV:
    root_templates = 'TPConfig/MV_Templates'
    my_cache = CacheThis()

    def __init__(self, tp=None, fast=False, nprtrigger=True, recipe=False, nodel=False, nobuild=False):
        """
        All options are here
        There should be no OPT beyond this point
        """
        self.tpfolder = tp              # Which POR folder
        self.modonly = set()            # set of module TestPlan name to keep
        self.mod_folder_keep = set()    # set of module folder name to keep
        self.fullpath_mtpl = {}         # {full_path_mtpl: boolean}
        self.outdir = None
        self.jsonname = None
        self.fast = fast                # set to True to use datahost transfer
        self.nprtrigger = nprtrigger    # set to False to not trigger
        self.recipe = recipe            # set to True to enable recipe creation
        self.nodel = nodel              # set to True to not delete TP
        self.nobuild = nobuild          # set to True to not run build

    def main(self, jsonname, outdir):
        """
        Main entry point

        Sequence:
        1. call torch_fixer api
        2. call torch_fixer.py
        3. call torch export api
        4. Do Module Skip
        5. call torch_postproc

        :param jsonname: Input name inside json
        :param outdir: outputdir
        """
        sw = Elapsed()
        self.check_output(outdir)
        self.outdir = outdir
        self.jsonname = jsonname
        modre = self.process_json(self.root_templates, jsonname)
        TorchPostProc.set_repo_sha()

        # step1: run usual stuff: torch fixer api -> torch_fixer.py -> torch export api
        # For fast performance, do everything in C:\ drive, then copy them at end
        # with TempDir(name=True, delete=not self.nodel, copydir='I:/tpvalidation/jqdelosr/temp/first/out') as tdir:
        with TempDir(name=True, delete=not self.nodel) as tdir:
            TorchPostProc.custom_scripts(Env.get_envfile(), 'buildpre_*')
            ALttc(TestProgram(Env.get_envfile())).main()
            self.tpexport(tdir)

            with Chdir(tdir):
                # step2: rename to ENG_TP
                File(dirname(dirname(Env.get_envfile()))).rename('ENG_TP')
                self.replace_portp_engtp_recipe()

                # step3: Do the moduleskip
                log.info(f'-i- Starting ModuleSkip...')
                tpobj = TestProgram(Env.get_envfile())
                self.modonly = self.get_mv_modules(tpobj, modre)
                if TorchPostProc.is_tos4():
                    tpobj.plists.error_out = False
                ModuleSkip(tpobj, onlylist=self.modonly).main()

                # step3a. Remove the module folders
                modlist_print = indent(3, [f'Accepted: {x}' for x in sorted(self.modonly)])
                log.info('-i- List of accepted modules:\n%s' % modlist_print)
                self.delete_folder()

                # step4 - Do postprocess
                log.info(f'-i- Starting torch_postproc...')
                try:
                    TorchPostProc().main()      # PlistEdit is called here
                except Exception:
                    self.copy_to_dest(outdir, tdir)
                    raise
                tpnew = TestProgram(Env.get_envfile())

            # step5 - copy to outdir
            self.copy_to_dest(outdir, tdir)

            # Success note
            count = len(list(tpnew.mtpl.iter_flows()))
            log.info(f'Success: MV creation complete in {sw}. Total of {count} instances in MV TP')

    def check_output(self, outdir):
        """Check output dir"""
        if self.fast:
            out = DataHost().central("check_destdir", Env.to_unixpath(outdir, is_unix=True), check=True)
            log.info(f'-i- datahost: {out}')

            # make sure cp exist
            _, out = SystemCall('which cp').run_outtxt()
            confirm(out.startswith('/'),
                    f'Sorry but cp is not found. Are you using gitbash? output: [{out}]',
                    f'Pls use gitbash, or if you continue to see this error, use [-fast false]')
        else:
            check.is_dir_empty_writeable(outdir)

    def copy_to_dest(self, outdir, src):
        """Copy to idrive (outdir)"""
        sw1 = Elapsed()
        if self.fast:
            log.info(f"WAIT, it's not yet done, transferring files to {outdir} now using FAST method.")

            # tar it
            with TempDir(name=True) as tardir:
                tmptar = f'{tardir}/tp.tar.gz'
                with tarfile.open(tmptar, "w:gz") as tarfh:
                    with Chdir(src):
                        tarfh.add('.')
                mkdirs(outdir, mode='770')   # the destdir is deleted by check_output()
                SystemCall(f'cp {tmptar} {outdir}').run_outtxt()
                File(f'{outdir}/tp.tar.gz').chmod('777')

            # untar it
            out = DataHost().central("untar", Env.to_unixpath(f'{outdir}/tp.tar.gz', is_unix=True), check=True)
            log.info(f'-i- datahost untar output: {out}')
            log.info(f'-i- fast tar+untar elapsed: {sw1}')

        else:
            log.info(f"WAIT, it's not yet done, transferring files to {outdir} now.")
            shutil.copytree(src, outdir)
            log.info(f'-i- copytree to {outdir} in {sw1}')

    def delete_folder(self):
        """
        Delete all module folders which are not part of modlist
        Reason: PDEs get confused and ask: "The TP is full TP" without looking at stpl file
        """
        modules_only = re.compile(r'\bModules\b')
        for fp in sorted(self.fullpath_mtpl):
            dname = dirname(fp)
            modname = basename(dname)
            if not modules_only.search(fp):
                continue
            if modname not in self.mod_folder_keep:
                rmtree(dname)
                log.info(f'Skip Module: Deleting: {modname}')

    def tpexport(self, destination):
        """
        1. call torch_fixer api
        2. call torch_fixer.py
        3. call torch export api
        """
        sln_file = self.derive_sln()
        tpproj_file = self.derive_tpproj_file()

        # ====== Uncomment this for debug in unix, given a TP that is EXPORTONLY, and after copying TPConfig/ manually
        if OPT.unix:     # pragma: no cover  - debug only
            os.rmdir(destination)
            shutil.copytree('.', destination)
            shutil.rmtree(f'{destination}/TPConfig')
            return

        if not exists(self.root_templates):    # This tp is already exported
            log.info(f'-i- {self.root_templates} already exist. Skipping fix-tp, fixer and export')
            return sln_file, tpproj_file       # unittest only

        confirm(IS_WIN,
                'Cannot run torch_mv.py from unix because it will call Torch api (windows only).',
                'Pls run torch_mv.py from windows. '
                'You can call torch_mv.py in unix after torch export in windows (with -unix and manual copy of TPConfig/)')

        confirm(sln_file,
                f'No .sln file found in {os.getcwd()}',
                f'This file is required for tp export.')

        # DoMV.no_dup_env_keys(tpproj_file)    # check dup env var before fix-tp

        # call torch fixer api
        sw = Elapsed()
        cmd = f'{DoMV.get_torch_exe()} fix-tp -s {sln_file} -p {tpproj_file}'
        log.info(f'-i- CMD: {cmd}')
        code, out = SystemCall(cmd).run_outtxt()
        log.info(out)
        log.info(f'fix-tp is complete in {sw}')
        confirm(not code, f'Command failed: {cmd}', 'Check output above.')

        # call torch_fixer.py
        DoFixer().main()

        # call torch export api
        sw = Elapsed()
        br = '-b -r' if self.recipe else ''
        cmd = f'{DoMV.get_torch_exe()} export-tp -s {sln_file} -p {tpproj_file} -i -c -l {br} -d {destination}'
        log.info(f'-i- CMD: {cmd}')
        code, out = SystemCall(cmd).run_outtxt()
        log.info(out)
        log.info(f'export-tp is complete in {sw}')
        confirm(not code,
                (f"Torch Export failed. See CMD: and output error above for hints. "
                 f"buildtp script is calling Torch.exe as a black box here."),
                (f"If this error is from your branch or your PR, then check your changes as it breaks Torch export. "
                 f"Try doing a Torch Build in VS and fix errors first. Usually Torch export fails if there is a "
                 f"Torch build error. If you think it has nothing to do with your changes, then ask TPI(s) for help. "
                 f"If you see this error from torch_mv, try adding [-exever latest] in command line to "
                 f"use latest Torch version. You can also specify specific Torch CLI version with [-exever]"))

        # call torch build - last, so that export-tp will not fail this is diag only anyway
        DoMV.torch_build(sln_file, tpproj_file, dest=destination, skip=self.nobuild)

    def replace_portp_engtp_recipe(self):
        """
        Replace the recipe from POR_TP to ENG_TP since torch_mv renamed it
        :return:
        """
        if not exists('ENG_TP'):
            return 1     # Nothing to do
        for ff in glob.glob('astra/*/*/*/*/*'):
            lines = [x.replace('POR_TP', 'ENG_TP') for x in File(ff).raw()]
            File(ff).rewrite(''.join(lines), 'replace_portp_engtp_recipe()')

    def derive_sln(self):
        """Return one .sln file to use"""
        result = glob.glob('*.sln')
        if len(result) == 0:
            return None
        elif len(result) == 1:
            return result[0]
        else:
            found = []
            for item in result:
                if '.debug.sln' in item:
                    continue
                found.append(item)
            confirm(len(found) == 1,
                    f'Expecting one .sln file: {found}',
                    f'Pls check your work area. All .sln file found: {result}')
            return found[0]

    def derive_tpproj_file(self):
        """Return the tpproj_file"""
        # see if there is only one tpproj
        wild = 'POR_TP/*/*.tpproj'
        result = glob.glob(wild)
        confirm(len(result) > 0,
                f'Expecting at least one .tpproj in {os.getcwd()}/{wild}',
                f'Pls check if you are in git checkout top level dir')
        if len(result) == 1:
            return result[0]

        # There are multiple, see if self.tpfolder is specified
        if self.tpfolder:
            wild = f'POR_TP/{basename(self.tpfolder)}/*.tpproj'
            result = glob.glob(wild)
            confirm(len(result) == 1,
                    f'Expecting one .tpproj in {os.getcwd()}/{wild}',
                    f'Pls check current work directory or your [-tp {self.tpfolder}] input')
            return result[0]

        # Try to derive first element of jsonname
        elem = self.jsonname.split('_')[0]
        wild = f'POR_TP/*{elem}*/*.tpproj'
        result = glob.glob(wild)
        if len(result) == 1:
            return result[0]

        raise ErrorUser(f'There are multiple POR_TP: {glob.glob("POR_TP/*")}.',
                        f'Pls specify which one via [-tp POR_TP/<foldername>]')

    def get_mv_modules(self, tpobj, modre):
        """
        Return set of TestPlan module names to keep
        :param tpobj: tp object
        :param modre: sorted list of regex module (folder name)
        :return: set of modules (TestPlan) to keep
        """
        # get the modules
        self.fullpath_mtpl = tpobj.get_all_mtpl_from_stpl()   # {full_path_mtpl: boolean}
        mega = '(%s)' % '|'.join(modre)
        rmega = re.compile(mega)
        set_mod_folder = set()     # module folder name to keep
        for fp in self.fullpath_mtpl:
            mod = basename(dirname(fp))
            if rmega.search(mod):
                set_mod_folder.add(mod)

        self.mod_folder_keep = set_mod_folder

        # get the testplan module name, module_skip needs testplan module name
        mm = tpobj.mtpl.get_modfolder2mod()
        return {mm[x] for x in mm if x in set_mod_folder}

    def json_load(self, ff):
        """
        Try to load this json file, with comma fix
        :return: data
        """
        # first try: as-is
        with open(ff) as fh:
            try:
                return json.load(fh)
            except Exception as e:
                origerror = str(e)

        # 2nd try: try to fix
        with TempDir(name=True) as tdir:
            lines = File(ff).raw()
            for idx in range(len(lines)):
                if lines[idx].strip().endswith(',') and lines[idx + 1].strip().startswith(']'):
                    lines[idx] = lines[idx].strip()[:-1]   # modify it
            try:
                return json.loads(' '.join(x.strip() for x in lines))
            except json.decoder.JSONDecodeError:
                # In cases where it is still error
                raise ErrorInput(f'Error reading {ff}: Error: {origerror}', f'Pls fix {ff}')

    def process_json(self, root, jsonname, jfiles=None):
        """
        Recursive - Return module regex list (folder name)

        :param root: directory where json files are
        :param jsonname: Name inside json to use
        :param jfiles: lower fname mapping
        :return: module (regex) list
        """
        # make sure dir is existing
        confirm(exists(root),
                f'{os.path.realpath(root)} does not exist. cwd: {os.getcwd()}',
                f'Expecting this directory to exist. Pls run torch_mv from source TP repo.')

        if not jfiles:
            jfiles = {x.lower(): x for x in os.listdir(root)}

        # get the fname
        fname = jsonname.lower()
        if not fname.endswith('.json'):
            fname = f'{fname}.json'

        confirm('/' not in fname.replace('\\', '/'),
                f'[{fname}] must be <file>.json and should not include path',
                f'Pls try again and remove the path.')

        confirm(fname in jfiles,
                f'{fname} (case-insensitive filename) does not exist in {root}',
                f'Check {root}')

        jdata = set()
        data = self.json_load(f'{root}/{jfiles[fname]}')
        for item in data:
            jdata.update(item['modules'])
            for ff in item['config_imports']:
                jdata.update(self.process_json(root, ff, jfiles))

        # read thru the json
        return sorted(jdata)

    @classmethod
    def display_jsons(cls, args):
        """Display all json files if args is empty"""
        if args:
            return   # do nothing
        confirm(exists(cls.root_templates),
                f'[{cls.root_templates}] does not exist.',
                'Pls run torch_mv.py from TP repo root directory')
        log.info('List of json files:')
        for ff in sorted(os.listdir(cls.root_templates)):
            log.info(ff)
        exit(0)

    @classmethod
    def no_dup_env_keys(cls, tpproj):
        """
        Simple way of checking all POR*/*/*.env file to not have duplicate key
        Reason: Torch3.5 fix-tp errors out if there are duplicate.
        It's not good to have duplicate anyway.
        We have a duplicate check in sherlock, but that is after fix-tp and export, and that checks
        The combined .env file together. Consider this a pre-check

        :param tpproj: tpproj file to derive env
        :return: unittest use only
        """
        envfiles = f'{dirname(tpproj)}/*.env'
        all_env = glob.glob(envfiles)
        confirm(all_env, f'Cannot find any {envfiles}', f'Pls check {os.getcwd()}')
        confirm(len(all_env) == 1, f'More than one .env file found: {all_env}', 'Expecting one .env only')
        robj = re.compile(r'^(\w+)\s*=')
        envfile = all_env[0]
        found = set()
        errs = set()
        for line in File(envfile).chomp(comment='#', strip=True):
            res = robj.search(line)
            if res:
                var = res.group(1)
                if var in found:
                    errs.add(var)
                found.add(var)
        if errs:
            var = ', '.join(errs)
            raise ErrorUser(f'[{var}] is defined twice in {envfile}',
                            'Duplicated env variables is not allowed. Pls fix this.')

        log.info(f'-i- {envfile} has no duplicate vars. count env={len(found)}')
        return len(found)    # for unittest only

    @classmethod
    def torch_build(cls, sln_file, tpproj_file, dest, skip=False):
        """
        Execute torch build

        :param sln_file: sln file
        :param tpproj_file: tpproj file
        :param dest: Destination folder (root tp)
        :param skip: Set to True to skip
        :return: None
        """
        if skip:
            log.info("TorchBuild is intentionally skipped")
            return
        if 'SKIP_TORCHBUILD' in os.environ:
            log.info("TorchBuild is skipped via env var")
            return
        lang_server = 'I:/tpapps/TORCH/Prod22/LanguageServer'
        sw = Elapsed()
        cmd = f'{DoMV.get_torch_exe()} build -s {sln_file} -p {tpproj_file} -l {lang_server} --maxParallel -1'
        log.info(f'-i- CMD: {cmd}')
        code, sout, serr = SystemCall(cmd).run_sout_serr(60 * 3)    # 3 min timeout
        out = f'{sout}\n{serr}'
        edata, wdata, udata = cls.build_process_txt(out)

        confirm(tpproj_file.startswith('POR_TP'), f'Expecting {tpproj_file} to start with POR_TP', 'Pls check code!')
        File(f'{dest}/{dirname(tpproj_file)}/Reports/build_errors.txt').touch(out, newfile=True, mkdir=True)
        log.info(f'TorchBuild exitcode={code}, error={len(edata)}, unknown={len(udata)}, elapsed={sw}')

    @classmethod
    def build_process_txt(cls, out):
        """
        Process the build output
        :param out: output of build
        :return: edata, wdata, udata
        """
        edata = []
        wdata = []
        udata = []
        eprint = defaultdict(partial(deque, maxlen=10))
        robj = re.compile(r'^(.*\.)(\w+)\(([\d,]+)\):.*(warning|error)( \w+):(.*)')
        for line in out.split('\n'):
            if 'Build Test Program' in line:
                log.info(line)
                continue
            if not line.strip():
                continue
            res = robj.search(line)
            if res:
                elems = res.groups()
                ff = f'{elems[0]}{elems[1]}'.replace('\\', '/')
                modname = basename(dirname(ff))
                line_data = {'file': ff,
                             'module': modname,
                             'lno': elems[2],
                             'code': elems[4].strip(),
                             'msg': elems[5].strip()}
                if elems[3] == 'error':
                    eprint[modname].append(line)
                    edata.append(line_data)
                else:
                    wdata.append(line_data)
            else:
                udata.append(line)
                log.info(f'UnknownLine: {line}')

        # display errors per module, max of 10
        for modname in eprint:
            for line in eprint[modname]:
                try:
                    log.info(f'ErrorLine {modname}: {line}')
                except UnicodeEncodeError:      # pragma: no cover  - stupid unicode
                    log.info(f'ErrorLine {modname}: <unicode error>')

        return edata, wdata, udata

    @classmethod
    @my_cache                  # One time read only
    def get_torch_exe(cls):
        """
        Return the torch.exe executable
        Default version is used by runners, which is hardcoded version so that
        new Torch release will not break pipelines
        """
        # check if yml specified torch rev first
        torch_exe_version = os.environ.get('TORCH_VERSION')
        if torch_exe_version:
            return torch_exe_version

        shared_f_txt0 = glob.glob(f'Shared/*_TP/*/InputFiles/torch_exe_version.txt')
        f_txt0 = glob.glob('POR_TP/*/InputFiles/torch_exe_version.txt')
        f_shared_common = 'Shared/BaseInputs/Inputs/torch_exe_version.txt'

        if OPT.exever == 'latest':
            # commandline: -exever latest
            return 'I:/tpapps/TORCH/Prod22/CLI/Torch.exe'

        elif OPT.exever:
            # commandline: -exever 3.14.0
            return f'I:/tpapps/TORCH/Prod22/CLI/{OPT.exever}/Torch.exe'

        elif len(shared_f_txt0) == 1:
            log.info(f'-w- torch_version: using {shared_f_txt0}')
            return File(shared_f_txt0[0]).read().strip()

        elif exists(f_shared_common):
            log.info(f'-w- torch_version: using {f_shared_common}')
            return File(f_shared_common).read().strip()

        elif f_txt0:
            # InputFiles/torch_exe_version.txt: Always use this
            confirm(len(f_txt0) == 1, f'Found more than one: {f_txt0}', 'Expecting one only per repo.')
            log.info(f'-w- torch_version: using {f_txt0}')
            return File(f_txt0[0]).read().strip()

        # default version
        log.info('-w- torch_version: Default OLD way - 3.58.0')
        return 'I:/tpapps/TORCH/Prod22/CLI/3.58.0/Torch.exe'


class ReplJson:
    """Refurbishing logic - given one or more json files, it will search and replace files"""

    def __init__(self, repljson):
        """
        :param repljson: empty, None or comma delimited
        """
        self.repldata = {}                 # repl data structure from json
        self.repljson = repljson

        # Do checks
        if repljson and repljson != 'None':
            for ffjson in repljson.split(','):
                if exists(ffjson):   # user specified full path
                    fname = ffjson
                elif ffjson.endswith('.json'):
                    fname = f'TPConfig/ReplaceJson/{ffjson}'
                else:
                    fname = f'TPConfig/ReplaceJson/{ffjson}.json'
                confirm(exists(fname), f'Expecting {fname}', f'Pls confirm this file in your branch')
                with open(fname) as fh:
                    ffdata = json.load(fh)
                self.repldata.update(ffdata)

    def apply(self, cwd=None):
        """
        Perform the replace needed for benchtop to work by applying self.repljson
        Called from modulebot only
        """
        if not self.repldata:
            return    # Do nothing

        if not cwd:
            cwd = os.getcwd()

        with Chdir(cwd):
            # structure:
            # repldata = {ff: [{comment: <>, search: <>, replace: <>}
            sw = Elapsed()
            for ff in self.repldata:
                confirm(exists(ff), f'File Not exist: {ff}', f'Required file, specified in {self.repljson}')
                text = File(ff).read()
                for item in self.repldata[ff]:
                    if isinstance(item['replace'], str):
                        replace = item['replace']
                    else:
                        replace = '\n'.join(item['replace'])
                    text = re.sub(item['search'], replace, text, re.MULTILINE)
                File(ff).rewrite(text, 'apply_replace() of modulebot')
        log.info(f'apply_replace() completed in {sw}, at {cwd}')


if __name__ == '__main__':  # pragma: no cover
    CheckerLog.setup()
    obj = MVArg(desc=__doc__)
    obj.main()
