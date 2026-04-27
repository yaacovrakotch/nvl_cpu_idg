#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
mtpl encode module

Purpose: Capability to embed tags (which are comments) in mtpl for various input file generation
         that require testnames in the output files.
                      ^^^^^^^^^

Used by: FSM config and PPR config and future config files

Root Problem: Torch export does not include comments, specially with MTT expand.

Strategy and Design:
Step1: torch_fixer.py (pre-export mtpl) will create meta_info.do_not_commit.log
       This file is part of .gitignore, thus, it's not committed.
Step2: torch_postproc.py (post-export mtpl) will create the "generated" files
       This will check if testname exist, with exception of disabled modules (100% missing for the module).
       Display age of meta_info.do_not_commit.log as info

meta_info.do_not_commit.log:
  1. *.log must be part of .gitignore. Thus, this file is not committed.
  2. json file with indent=3 so that it is readable by humans. We can grep.
  3. Structure:
     { "module testname": [<tags>] }
"""
from os.path import isdir
from gadget.errors import confirm, ErrorInput, ErrorCockpit
from gadget.tputil import OtplFile, to_regex, get_modulename, JsonRead
from gadget.pylog import log
from gadget.gizmo import Elapsed
from gadget.files import basename_n, File
from gadget.dictmore import read_csv
from gadget.strmore import curtime
from gadget.lockfile import force_refresh
from gadget.disk import mkdirs, Chdir, rmtree, delete_oldest
from gadget.printmore import Dumper
from gadget.strmore import indent, truncate
from gadget.data_host import DataHost
from gadget.tvpv import TvpvEnv
from gadget.shell import TarAdd
from tp.mtpl import BM
from tp.testprogram import TestProgram, Env
from collections import defaultdict
from os.path import exists, dirname, basename
from pprint import pprint
import json
import re
import os
import glob
import time
import csv


class MtplEncode:
    ROOTNAME = 'meta_info.do_not_commit.log'
    TAGS = ('# FSM:', '# PPR:')
    ULAT_ENGG = Env.xpath('I:/engineering/dev/sctp/tptorrent/ulat')

    def __init__(self, tpobj: TestProgram):
        self.tpobj = tpobj
        self.metapath = f'{self.tpobj.envdir}/{self.ROOTNAME}'
        self.data = None  # { "module testname": [<tags>] }
        self.bm = None
        self.skip_mod = set()     # Set of modules to skip since they don't exist in exported tp
        self.alltn = set()        # set of all (module, testname), populated by _read_mtpl()
        self.ctr = 0      # Counter on number of TrialTest expanded lines
        self.rtest = re.compile(r'^(Test|TrialTest|CSharpTest|CSharpTrialTest)\s+\w+\s+(\S+)')   # used in _read_mtpl and add_alltn

    def _get_ulat_mv_path(self):
        """
        Get the product-specific ULAT_MV path dynamically.

        :return: ULAT_MV path for the detected product (nvl/dnl/rzl)
        :rtype: str
        """
        prod = self.tpobj.get_family_name()[:3].lower()  # Changed from get_name() to get_family_name()
        return Env.xpath(f'I:/engineering/dev/sctp/tptorrent/hdmxprogs/{prod}/ulat_mv')

    def generate_meta(self):
        """
        Generate the meta file.
        Called by torch_fixer.py
        Used on pre-export tp
        """
        sw = Elapsed()

        # read all mtpl
        self.data = self._read_all_mtpl()

        # write
        with open(self.metapath, 'w') as fh:
            json.dump(self.data, fh, indent=3)

        log.info(f'-i- {basename_n(self.metapath, 2)} is written, key cnt={len(self.data)}, TrialTest={self.ctr}, {sw}')

    def _read_all_mtpl(self):
        """
        Read all mtpl and populate dictionary plus self.alltn
        """
        # read all mtpl
        data = defaultdict(list)
        self.bm = BM(self.tpobj)

        for ff in self.tpobj.get_all_mtpl_from_stpl():
            self._read_mtpl(ff, data)

        return data

    def _read_mtpl(self, fname, data):
        """
        Read one mtpl file and put in data
        :param fname: mtpl file
        :param data: dictionary (resulting data)
        :return: None
        """
        elines = None
        module = None
        eline_lno = None
        for lno, line in OtplFile(fname).readline(comments=True):

            # get module
            if line.startswith('TestPlan'):
                res = re.search(r'^TestPlan\s+(\w+)', line)  # no need to compile - one time
                module = res.group(1)
                continue

            # get testname
            elif line.startswith(('Test ', 'CSharpTest ')):
                eline_lno = lno
                elines = [line]
                self._add_alltn(module, elines)
                # print(module, elines)
                continue

            elif line.startswith(('TrialTest ', 'CSharpTrialTest ')):
                eline_lno = lno
                try:
                    elines = list(self.bm.expand(line, f'Fix line#{lno} {module} File: {fname}'))
                except ErrorInput as e:
                    elines = ["_ERROR_"]
                    log.info(f"-i- Error: {e}")

                self._add_alltn(module, elines)
                # print(module, elines)
                self.ctr += 1
                continue

            # tag found
            elif line.startswith(self.TAGS):
                confirm(module,
                        f'Error on line#{lno}: tag found [{line}] but no module',
                        f'Check {fname}')
                confirm(elines,
                        f'Error on line#{lno}: tag found [{line}] but no Test or TrialTest',
                        f'Check {fname}')
                for eline in elines:
                    confirm(eline != "_ERROR_",
                            f'Error on line#{eline_lno} of {fname}: Failed to expand!',
                            ('Check for the variables and search for "fail_eval" message. '
                             'Do not use variables in BinMatrixSpecs.flm.usrv. '
                             'Use BinMatrix.flm.usrv instead'))
                    res = self.rtest.search(eline)
                    confirm(res,
                            f'Error on line#{eline_lno}: [{line}] Cannot derive the instance name',
                            f'Check {fname}')
                    testname = res.group(2)
                    testname = testname.replace('"', '').replace(';', '')
                    key = f'{module} {testname}'
                    data[key].append(line)

    def _add_alltn(self, module, elines):
        """
        Add the testnames in a self.alltn - safe
        Reason why this is safe: if regex fails, then it will error out in tags confirmation anyway

        :param module: module name
        :param elines: list of test lines
        :return:
        """
        for eline in elines:
            res = self.rtest.search(eline)
            if res:
                self.alltn.add((module, res.group(2)))

    def read_meta(self):
        """Read meta file and display info"""
        if not exists(self.metapath):
            log.info(f'-i- {self.ROOTNAME} does not exist. Skipping...')
            self.data = {}
            return self

        # header
        log.info(f'-i- {basename_n(self.metapath, 2)} age is {File(self.metapath).age()} secs')

        # read the json
        with open(self.metapath) as fh:
            self.data = json.load(fh)

        # display missing info
        self._read_all_mtpl()
        missing = defaultdict(list)
        total = defaultdict(int)
        for md_tn in self.data:
            md, tn = md_tn.split()
            total[md] += 1
            if (md, tn) not in self.alltn:
                missing[md].append(md_tn)

        if missing:
            log.info('Missing modules report (meta_info). Count is number of instances:')
        for md in missing:
            log.info('   %s = %d of %d missing' % (md, len(missing[md]), total[md]))
            self.skip_mod.add(md)

            # accept only missing entire module (MV or disabled modules)
            list_missing = truncate(indent(3, missing[md]))
            confirm(len(missing[md]) == total[md],
                    f'The following instances are missing in exported TP:\n{list_missing}',
                    f'Was torch_fixer.py run? If you see this error on TPbuild or *bot, then contact jqdelosr.')

        return self

    def get_all_duplicate_dutflow(self):
        """Determine all duplicate dutflow items"""
        modfolder2mod = self.tpobj.mtpl.get_modfolder2mod()
        dups = set()
        for mtpl in self.tpobj.get_all_mtpl_from_stpl():
            module = get_modulename(mtpl)
            if not module:
                continue
            uniq = set()
            for lno, line in OtplFile(mtpl).readline():
                if line.startswith(('FlowItem', 'DUTFlowItem ')):
                    name = line.split()[1]
                    if name in uniq:
                        dups.add((modfolder2mod[module], name))
                    else:
                        uniq.add(name)
        return dups

    def do_fsm(self, bom=None):
        """
        Purpose: Consolidate all FSM.csv to generate a single file FullSkipModelInput.csv
        Problem1: FullSkipModelInput.csv is a single file and not maintainable by module owners bec of conflicts
        Problem2: Make the input simple for module owners

        Format on mtpl:
        # FSM: COLD: IP_CPU

        Format on fsm config json:
        [
           {"process": "PHMHOT, PHMCOLD, CLASSCOLD",
            "ip": "IP_CPU",
            "module": "string|<regex>",          # required! regex for POR_TP and exact match for <module>
            "regex": <regex_of_testname>,        # keep the regex as is
           }
        ]
        """
        confirm(self.data is not None, 'Incorrect usage', 'Pls execute read_meta() first to initialize')

        # Read the FSM_Config.csv
        if bom is None:
            fsm_config_g = (glob.glob(f'{self.tpobj.envdir}/InputFiles/FSM_Config.csv') +
                            glob.glob(f'{self.tpobj.shareddir}/BaseInputs/Common/Common_Torch/FSM_Config.csv'))
        else:
            fsm_config_g = (glob.glob(f'{self.tpobj.envdir}/InputFiles/FSM_Config.csv') +
                            glob.glob(f'{self.tpobj.shareddir}/BaseInputs/Common/Common_{bom}/FSM_Config.csv'))

        if not fsm_config_g:
            log.info(f'-i- fsm_consolidate is skipped. not exist: FSM_Config.csv')
            return 1
        confirm(len(fsm_config_g) == 1, f'Expecting only 1: {fsm_config_g}', 'Only one FSM_Config.csv per bom')
        fsm_config = fsm_config_g[0]

        sw = Elapsed()

        # Create the header dict
        cfg_map = defaultdict(list)
        cfg = {}
        for elems in read_csv(fsm_config, return_dict=False):
            encode_column = elems[-2]
            confirm(encode_column, f'encode column cannot be blank for [{elems[0]}].', f'pls fix {fsm_config}')
            if elems[0] not in cfg:
                cfg[elems[0]] = ','.join(elems[1:])  # first one
            cfg[f'{elems[0]}-{encode_column}'] = ','.join(elems[1:])  # Always add this
            cfg_map[elems[0]].append(f'{elems[0]}-{encode_column}')

        # read all FSM tags
        all_rows = []
        robj = re.compile(r'^# FSM: ([^:]+):\s*(\w+)?$')
        for md_tn, tags in sorted(self.data.items()):
            for tag in tags:
                if not tag.startswith('# FSM:'):
                    continue
                md, tn = md_tn.split()

                if md in self.skip_mod:
                    continue  # These are modules not existing in exported TP

                res = robj.search(tag)

                confirm(res,
                        f'Error on [{md_tn}]: Invalid FSM tag: [{tag}]',
                        f'Pls fix. Expecting: [# FSM: <process_step>: <ip>]')

                pstep_res = res.group(1)
                ip = res.group(2)
                if ip is None:
                    ip = ''
                for pstep in pstep_res.split(','):
                    pstep = pstep.strip()
                    all_rows.append((pstep, md, tn, ip))

        # add the config regex
        all_rows, totals = self._fsm_re_cfg(all_rows)

        # write totals
        text = '\n'.join(f'{x[0]},{x[1]},{x[2]},{x[3]}' for x in totals)
        File(f'{self.tpobj.envdir}/Reports/FSM.csv').touch(text, newfile=True, mkdir=True)

        # write output
        outfile = f'{self.tpobj.envdir}/FullSkipModelInput.csv'
        with open(outfile, 'w') as fh:
            # header
            fh.write(f'{cfg["ProcessStep"]},ModuleName,InstanceName,IPName\n')
            for row in all_rows:
                confirm(row[0] in cfg, f'[{row[0]}] is not defined in FSM_Config.csv.',
                        f'Fix {row[1]},{row[2]}')

                if row[0] in cfg_map:
                    pstep_list = cfg_map[row[0]]  # multiple matches
                else:
                    pstep_list = [row[0]]

                for item in pstep_list:
                    fh.write(f'{cfg[item]},{row[1]},{row[2]},{row[3]}\n')

        log.info(f"-i- {basename_n(outfile, 2)} is written in {sw}")

    def do_fsm_env_copy(self, fsm_final_path, bom):
        """
        Update the env and copy the fsm csv

        Strategy/Usage:
        1. I:/ulat/fsm     - Production, via tptorrent, TPI only, HVM release. Need #2 first.
        2. tptorrent/ulat  - Engg, x-geo, This is for TPI only. V:\\ drive full TP. Correlation.
                             Why do we need x-geo (and not just build locally?).
                             We build once and run this in 2 or more site.
        3. {prod}/ulat_mv  - MV, local only (use tpbuild_site specific for the site) - now supports nvl/dnl/rzl

        :param fsm_final_path: path to copy
        """
        ut_only = 0

        # update the fsm path in ENV file
        if 'FSM_FILE_PATH' not in self.tpobj.env.get_env_dict():
            return -1  # No FSM_FILE_PATH in env, do nothing

        self.tpobj.env.set_item('FSM_FILE_PATH', fsm_final_path)

        # rebuild the env with new FSM path
        File(self.tpobj.envfile).rewrite(''.join(self.tpobj.env.rebuild()), 'FSM.UpdateEnv()')

        if fsm_final_path.startswith('I:/ulat/fsm'):  # I:/ulat/fsm is for manual tptorrent
            # TODO: tptorrent api call here
            ut_only += 1

        elif '/ulat_mv' in fsm_final_path:    # ulat_mv MV path - now supports nvl/dnl/rzl
            destination_path = dirname(fsm_final_path)
            contents = File(f'{self.tpobj.envdir}/FullSkipModelInput.csv').read()
            DataHost().central("ulatmv_copy", (Env.to_unixpath(basename_n(fsm_final_path, 5)), contents),
                               site=TvpvEnv.get_site(), check=True)
            ut_only += 2

        else:
            destination_path = dirname(fsm_final_path)    # V drive ulat path I:/engineering/dev/sctp/tptorrent/ulat/fsm/hdmx/{prod}/{bom}/{tpname}
            contents = File(f'{self.tpobj.envdir}/FullSkipModelInput.csv').read()
            DataHost().central("ulat_copy", (Env.to_unixpath(basename_n(fsm_final_path, 4)), contents),
                               site=TvpvEnv.get_site(), check=True)
            ut_only += 3

        # cleanup oldest - now supports nvl/dnl/rzl
        ulat_mv = self._get_ulat_mv_path()
        if fsm_final_path.startswith(ulat_mv):
            delete_oldest(ulat_mv, keep=1000, message='-i- Deleting ulat_mv')

        # transfer to x-geo
        if fsm_final_path.startswith(MtplEncode.ULAT_ENGG):
            # TODO: FSM file transfers to x-geo I: drive.
            # Read the FSM_Site_Config.JF.PG12.IDC.BA.txt
            # Inside of file FSM_Site_Config.JF.PG12.IDC.BA.txt, provide the site name instruction for user.
            fsm_site_config = glob.glob(f'{self.tpobj.shareddir}/BaseInputs/Common/Common_{bom}/FSM_Site_Config.*.txt')
            if not fsm_site_config:
                return -2  # Do nothing, assume it just needs single site copy

            else:
                confirm(len(fsm_site_config) == 1, 'Only 1 FSM_Site_Config file allowed per BOM',
                        'Please keep only one config file in repo.')
                config_file_name = basename_n(fsm_site_config[0], 1)
                split_name = config_file_name.split('.')
                site_info_list = split_name[1:-1]
                print(f'site_info list: {site_info_list}')

            for site in site_info_list:
                if site == TvpvEnv.get_site():
                    continue  # skip local site

                else:
                    log.info(f'-i- Starting ulat_copy to site {site}')
                    contents = File(fsm_final_path).read()
                    DataHost().central("ulat_copy", (Env.to_unixpath(basename_n(fsm_final_path, 4)), contents), site=site, check=True)
            ut_only += 100

        log.info(f"-i- {fsm_final_path} is copied in place.")
        return ut_only

    def _fsm_re_cfg(self, all_rows):
        """
        Process the FSM data

        Read the config the insert in all_rows, avoid duplicates
        return final rows (no duplicate)
        """
        dups = self.get_all_duplicate_dutflow()

        # read all FSM files
        data = {}
        for ff, module in self._all_fsm_input():
            with open(ff) as fh:
                log.info(f'Reading {ff}')
                data[(ff, module)] = json.load(fh)

                # make sure module exist in the elements or not exist
                for item in data[(ff, module)]:
                    confirm('process' in item, f"[process] key is required in {ff}", f"Pls fix {ff}")
                    confirm('ip' in item, f"[ip] key is required in {ff}", f"Pls fix {ff}")
                    confirm('module' in item, f"[module] key is required in {ff}", f"Pls fix {ff}")

                    if module is not None:
                        confirm(item['module'] == module,
                                f"Value of [module] does not match: {item['module']} vs {module}.",
                                f"Pls fix module key in {ff}")

        # create a dictionary of mod -> tn
        dmt = defaultdict(list)
        for mod, tn in self.alltn:  # set of (module, testname)
            dmt[mod].append(tn)

        # do the counting of existing rows from mtpl encode
        cnt = {}  # count per (md,tn)
        for pstep, md, tn, _ in all_rows:
            cnt[(pstep, md, tn)] = 1  # no duplicates here
            msg = f'Error: {md}::{tn} is duplicated in DUTFlowItem. This is not allowed for FSM'
            assert (md, tn) not in dups, msg

        # process, add in all_rows, by using self.alltn
        total = defaultdict(int)  # counter per (module,regex)
        for key in data:  # key = (ff, module)
            for item in data[key]:

                # process one item
                module = key[1]
                if module is None:
                    modlist = item['module'].split(',')
                else:
                    modlist = [module]

                rtn = re.compile(to_regex(item['regex']))
                for pstep in item['process'].split(','):
                    pstep = pstep.strip()
                    for md in modlist:
                        if md not in dmt:
                            log.info(f'-w- FSM: [{md}] module is not found. Ignoring this FSM item.')
                            continue
                        all_rows.append((pstep.strip(), md, to_regex(item['regex']), item['ip']))
                        for tn in dmt[md]:
                            if (pstep, md, tn) not in cnt:
                                cnt[(pstep, md, tn)] = 0  # initialize. cannot use defaultdict here
                            if rtn.search(tn):
                                cnt[(pstep, md, tn)] += 1
                                total[(pstep, md, item['regex'])] += 1
                                msg = f'Error: {md}::{tn} is duplicated in DUTFlowItem. This is not allowed for FSM'
                                assert (md, tn) not in dups, msg

        # Do all the unique (pstep, md, tn) later after everything is done. Pls do ip_checks
        uniq = {}
        final = []
        for item in sorted(all_rows):
            pstep, md, tn, ip = item
            key = (pstep, md, tn)
            if key in uniq:
                confirm(uniq[key] == ip,
                        f'Error on ip [{uniq[key]} vs {ip}] for {key}',
                        f'Pls make sure ip is consistent.')
                continue
            uniq[key] = ip
            final.append(item)

        # process totals from total and cnt
        totals = [("count", "pstep", "module", "testname")]
        for key in sorted(cnt):
            totals.append((cnt[key], key[0], key[1], key[2]))
        totals.append(("count", "pstep", "module_regex", "testname_regex"))
        for key in sorted(total):
            totals.append((total[key], key[0], key[1], key[2]))

        return final, totals

    def _all_fsm_input(self):
        """
        Iterator, return all fsm input files
        :return: path, module (module is None if not coming from module)
        """
        # .fsm.json files
        #  Product way: BaseInputs/*     / *   /*.fsm.json
        #           BaseInputs/CPU   /<bom>/cpu.fsm.json         # this works in dielet
        #           BaseInputs/Common/<bom>/fulltp.fsm.json      # this is fulltp
        for fjson in (glob.glob(f'{self.tpobj.envdir}/InputFiles/*.fsm.json') +         # legacy usage, do not use for new products
                      glob.glob(f'{self.tpobj.tpldir}/BaseInputs/*/*/*.fsm.json') +     # Product usage dielet
                      glob.glob(f'{self.tpobj.shareddir}/BaseInputs/*/*/*.fsm.json')):  # Product usage common
            yield fjson, None

        # per module. Cannot use glob bec of shared module
        for mtpl in self.tpobj.get_all_mtpl_from_stpl():
            path = f'{dirname(mtpl)}/InputFiles/input.fsm.json'  # fixed name, not wildcard
            if exists(path):
                yield path, self.tpobj.get_scope(mtpl, None)

    def do_ppr(self):
        """
        Purpose: Consolidate all info and write output PprConfiguration.json
        Problem1: PprConfiguration.json is a single file and not maintainable by module owners bec of conflicts
        Problem2: Info (testname) is in two places: PprConfiguration.json and mtpl. This can lead to mis-sync, forgotten updates, etc

        Format on mtpl:
        # PPR: IP_CPU: *: <config>
        # note: The default, with "*" must be the first.
        """
        confirm(self.data is not None, 'Incorrect usage', 'Pls execute read_meta() first to initialize')

        # Check if PPR generation is valid
        ppr_root = f'{self.tpobj.tpldir}/Modules/PPR/InputFiles'
        ppr_config = f'{ppr_root}/PPR_Config.json'
        if not exists(ppr_config):
            log.info(f'-i- ppr_generate is skipped. not exist: {ppr_config}')
            return 1

        # Read the PPR_Config.json
        with open(ppr_config) as fh:
            cfg = json.load(fh)
            confirm('DEFAULT' in cfg, f'[DEFAULT] is required in {ppr_config}', 'Fix the file.')
            confirm('PPR_general_fields' in cfg, f'[PPR_general_fields] is required in {ppr_config}', 'Fix the file.')

        # read all PPR tags
        all_data = cfg['PPR_general_fields']
        all_data['TestInstance2Tolerances'] = {}

        att = all_data['TestInstance2Tolerances']
        robj = re.compile(r'^# PPR: (\w+): (\S+): (\w+)$')
        for md_tn, tags in sorted(self.data.items()):
            for tag in tags:
                if not tag.startswith('# PPR:'):
                    continue
                md, tn = md_tn.split()

                if md in self.skip_mod:
                    continue  # These are modules not existing in exported TP

                res = robj.search(tag)
                confirm(res,
                        f'Error on [{md_tn}]: Invalid FSM tag: [{tag}]',
                        f'Pls fix. Expecting: [# FSM: <process_step>: <ip>]')

                tag_ip = res.group(1)
                tag_re = res.group(2)
                tag_cfg = res.group(3)
                confirm(tag_cfg in cfg, f'[{tag_cfg}] is not defined in {basename_n(ppr_config, 3)}',
                        f'Fix {md} mtpl file')

                if tag_re == '*' or re.search(to_regex(tag_re), tn):
                    key = f'{tag_ip}::{md}::{tn}'
                    value = dict(cfg['DEFAULT'][0])  # make a copy
                    value.update(cfg[tag_cfg][0])
                    att[key] = [value]

        if not att:
            att['DEFAULT'] = cfg['DEFAULT']

        # use global config (overwrite) if it exist
        ppr_global = f'{ppr_root}/GlobalPPRconfiguration.json'
        if exists(ppr_global):
            print("Current data, which will be thrown away:")
            pprint(att)
            log.info(f'-i- {ppr_global} exist. Using this data. Above will be thrown away.')
            gdata = JsonRead(ppr_global).load()
            newatt = self._process_global_ppr(gdata['PPRTargetTests'], cfg)     # Required toplevel key in GlobalPPRconfiguration.json
            all_data['TestInstance2Tolerances'] = newatt

        # write output
        outfile = f'{ppr_root}/PprConfiguration.json'
        with open(outfile, 'w') as fh:
            if 'DEFAULT' in all_data['TestInstance2Tolerances']:
                all_data['TestInstance2Tolerances']['DEFAULT::DEFAULT'] = all_data['TestInstance2Tolerances']['DEFAULT']
                del all_data['TestInstance2Tolerances']['DEFAULT']
            json.dump(all_data, fh, indent=3)
        log.info(f"-i- {basename_n(outfile, 3)} is written by do_ppr()")

    def _process_global_ppr(self, pdata, cfg):
        """
        Process global PPR data
        :param pdata: dictionary {"IP_CPU::ARR_CORE_C28::LSA_CORE_VMIN_K_CCRF6_080808_VCORE_F6_.+": "Config3"}
        :param cfg: cfg data
        :return: dictionary newatt
        """
        # create megamap
        megamap1 = defaultdict(list)  # {md: <list_of_tn>}
        for md, tn in sorted(self.alltn):
            megamap1[md].append(tn)
        megamap2 = {}  # {md: tn_string_for_regex}
        for md, tnlist in megamap1.items():
            megamap2[md] = '\n'.join(tnlist)

        # process the dictionary
        att = {}
        for key, tag_cfg in pdata.items():
            elems = key.split('::')
            confirm(len(elems) == 3, f'Invalid data in GlobalPPRconfiguration.json: {key}',
                    'Expecting 3 elements: <ip>::<module>::<regex_testname>')
            tag_ip, md, tnre = elems

            if md in self.skip_mod:
                continue  # These are modules not existing in exported TP

            confirm(tag_cfg in cfg, f'[{tag_cfg}] is not defined in PPR_Config.json',
                    f'Fix GlobalPPRconfiguration.json')

            for tn in re.findall(tnre, megamap2.get(md, "")):    # This is partial match. The regex string must be complete
                key = f'{tag_ip}::{md}::{tn}'
                value = dict(cfg['DEFAULT'][0])  # make a copy
                value.update(cfg[tag_cfg][0])
                att[key] = [value]

        return att

    def do_ppr_2nd(self):
        """
        Purpose: Postprocess (aka, PostAction) the PprConfiguration.json based on SafeDefaults.

        Problem: The default value of DefaultPowerScalingFactor (which is 1), is not good,
        so use a good safe default value based on Learned Silicon values.

        This routine has nothing to do with MtplEncode per-se, but it has something to do with do_ppr,
        that's why it's here.

        Format of Modules/PPR/InputFiles/SafeDefaults.json:
        {
            "DefaultPowerScalingFactor": {
                "IP_CPU::ARR_CCF_C68::LSA_X_VMIN_K_CCLRF6_080808_VCCR_F6_3400_1506": 1.45,
                "IP_CPU::ARR_CCF_C68::LSA_X_VMIN_K_CCLRF6_080808_VCCR_F6_3400_1507": 1.62,
                "IP_CPU::ARR_CCF_C68::SSA_X_VMIN_K_CCLRF6_080808_VCCR_F6_3400_1506": 0.98,
                "IP_CPU::ARR_CCF_C68::SSA_X_VMIN_K_CCLRF6_080808_VCCR_F6_3400_1507": 1.27
            }
        }

        """
        # Check if PPR generation is valid
        ppr_root = f'{self.tpobj.tpldir}/Modules/PPR/InputFiles'
        ppr_safe = f'{ppr_root}/SafeDefaults.json'  # Safe default value based on Learned Si data.
        outfile = f'{ppr_root}/PprConfiguration.json'  # Final output file
        report_nosafe = f'{self.tpobj.envdir}/Reports/ppr_instancenames_no_safe_value.txt'
        if not exists(ppr_safe):
            log.info(f'-i- ppr_generate 2nd edition (postaction) is skipped since {ppr_safe} not exist')
            return 1
        confirm(exists(outfile), f"Expecting: {outfile}", "This file is needed for ppr_generate 2nd edition")

        # Read outfile
        with open(outfile) as fh:
            all_data = json.load(fh)

        # Read ppr_safe
        with open(ppr_safe) as fh:
            safe = json.load(fh)
        key = 'DefaultPowerScalingFactor'
        confirm(key in safe, f'{key} is required as top level element in json', f'Pls fix {ppr_safe}')
        allti = safe[key]

        # Update the dictionary
        tolkey = 'TestInstance2Tolerances'
        errors = []
        for ti in allti:
            if ti not in all_data[tolkey]:
                errors.append(ti)
                continue
            for item in all_data[tolkey][ti]:
                item[key] = allti[ti]  # replace it

        # generate report of unupdated instances
        notfound = []
        for ti in all_data[tolkey]:
            if ti not in allti:
                notfound.append(ti)
        notfound.append('')
        File(report_nosafe).touch('\n'.join(notfound), mkdir=True, newfile=True)

        # Error out if there are errors
        if errors and (not self.tpobj.is_eng_tp()):
            message = indent(3, errors)
            outbase = basename_n(outfile, 3)
            raise ErrorInput(f'There are {len(errors)} error(s). ie, instance name not found in {outbase}. '
                             f'It is possible that testinstance name have changed.',
                             f'Pls fix {basename_n(ppr_safe, 3)} to match {outbase} instance names. '
                             f'See below for mismatches:\n{message}')

        # write output
        with open(outfile, 'w') as fh:
            json.dump(all_data, fh, indent=3)

        log.info(f"-i- {basename_n(outfile, 3)} is updated by do_ppr_2nd()")

    def do_fsmpath_assembl(self, tpname, bom, isval, ispart):
        """
        Due to different user scenarios, FSM path is updated per conditions below:
        I: drive FULL –
        FSM_FILE_PATH = "I:/ulat/fsm/hdmx/{Prod}/{BOM}/{TPname}/FullSkipModelInput.csv"
        V: drive VALL and PARTIAL –
        FSM_FILE_PATH = "I:/engineering/dev/sctp/tptorrent/ulat/fsm/hdmx/{Prod}/{BOM}/{TPname}{DieIndicator}/FullSkipModelInput.csv"
        MV or Engineering TP -
        FSM_FILE_PATH = "I:/engineering/dev/sctp/tptorrent/hdmxprogs/{Prod}/ulat_mv/fsm/{timesec}/FullSkipModelInput.csv "
        """
        if tpname is None:
            # no x-site geo for this, local only
            prod = self.tpobj.get_family_name()[:3].lower()  # Changed from get_name() to get_family_name()
            fsm_file_path = f'I:/engineering/dev/sctp/tptorrent/hdmxprogs/{prod}/ulat_mv/fsm/{time.time()}/FullSkipModelInput.csv'

        else:
            prod = tpname[:3].lower()
            if isval:
                # x-site geo
                fsm_v_tpname = tpname[10:14] + '0'
                fsm_file_path = f'I:/engineering/dev/sctp/tptorrent/ulat/fsm/hdmx/{prod}/{bom}/{fsm_v_tpname}/FullSkipModelInput.csv'
            elif ispart:
                # x-site geo
                fsm_part_tpname = tpname[10:14] + '0' + tpname[15:17]
                fsm_file_path = f'I:/engineering/dev/sctp/tptorrent/ulat/fsm/hdmx/{prod}/{bom}/{fsm_part_tpname}/FullSkipModelInput.csv'
            else:
                # production, manual tptorrent
                fsm_prod_tpname = tpname[10:15]
                fsm_file_path = f'I:/ulat/fsm/hdmx/{prod}/{bom}/{fsm_prod_tpname}/FullSkipModelInput.csv'

        return fsm_file_path


class NPRTrigger:
    """
    NPR Triggering for PUP
    https://wiki.ith.intel.com/display/ITSpdxtp/MTL+NPR
    """

    def __init__(self, tpobj):
        self.tpobj = tpobj
        self.fname = None
        self.timeout = 600  # In seconds - 10 mins max wait for trigger
        self.sleep_sec = 10  # Sleep interval between checks
        self.trigflag = False  # flag to indicate if trigger happens

        # prod family name - lower case
        self.familyname = self.tpobj.get_family_name()
        # paths
        self.trigpath = Env.xpath(
            f'/intel/engineering/dev/sctp/tptorrent/hdmxprogs/{self.familyname}/{self.familyname.upper()}_triggers')

    def main(self, nprtrigger, outdir=None):
        """
        Main algo for NPR triggering

        :param
        nprtrigger: True to enable trigger
        outdir: user defined outdir path to get the TP name. None will skip the trigger.
        :return: unittest code
        """
        # step1 - Check if trigger conditions are met. If not, skip the trigger with proper log message and return code.
        # For automation yml, which case DONT WANT triggers (eg, checkers)
        if not nprtrigger:  # used by checkers
            log.info('-i- NPRTrigger is skipped, user specified.')
            return 1

        if outdir is None:
            log.info('-i- NPRTrigger is skipped, outdir is not provided by user.')
            return 2

        # Is this TP valid for triggering
        resultcode = self.is_invalid()
        if resultcode:
            return resultcode

        # step2 - parse the central csv file to determine npr mode ON/OFF
        central_csv = 'Shared/BaseInputs/Common/Common_Files/PUP_HERMES_Config.csv'

        # step3 - Process the TP name decoding from user input outdir and module modifications based on NPR mode.
        prod_type, tp_input_name = self.outdir_tpname_decode(outdir)
        found, lineno = self.npr_csv_parser(central_csv, 'TP_naming', value=tp_input_name[7:12])

        if not found:
            log.info(
                f'-i- NPRTrigger is skipped, TP name "{tp_input_name[7:12]}" not found in central csv file {central_csv}.')
            return 6

        # If found, check the "PUPONOFF" column for that line to determine status.
        npr_mode = self.npr_csv_parser(central_csv, 'PUPONOFF', line_number=lineno)

        if npr_mode.strip().lower() == 'off':
            # PUP mode is OFF, make necessary mod updates to turn off PUP related modules, and skip the trigger.
            self.modify_mod_pupoff()
            log.info(f'-i- NPRTrigger is skipped, '
                     f'NPR_Mode for TP name "{tp_input_name}" is set to "{npr_mode}" in central csv file {central_csv}.')
            return 7

        # PUP mode is ON, make necessary mod updates to turn on PUP related modules, and proceed to trigger.
        self.modify_mod_pupon()
        log.info(f'-i- NPRTrigger will be triggered, '
                 f'NPR_Mode for TP name "{tp_input_name}" is set to "{npr_mode}" in central csv file {central_csv}.')

        # step4 - ENV file modifications
        self.modify_env(outdir)

        # step5 - trigger it
        self.trigger(outdir)  # Do the trigger

    def modify_mod_pupoff(self):
        """
        Update NPR related modules for the PUP off condition.

        This applies the following off-mode changes:

        * In ``Shared/Modules/TPI/TPI_BASE_XXX/*.mtpl``, force
          ``EnableHermesMode = "False"`` for the
          ``VminForwardingBase CTRL_X_PRIMEVMINFORWARDING_K_INIT_X_X_X_X_VMIN``
          test instance.
        * In ``Shared/Modules/TPI/TPI_PUP_XXX/*.mtpl``, update the
          ``PlistConfigTC CTRL_X_PLISTCONFIG_E_INIT_X_X_X_X_SKIPSHORT`` test
          instance to set ``OptionValue = "True"`` and ``BypassPort = -1``.

        :return: Status code indicating the PUP off update operation completed
        :rtype: int
        """
        mod_path_off_base = 'Shared/Modules/TPI/TPI_BASE_XXX/*.mtpl'
        updates_off_base = [
            {
                'test_instance': 'VminForwardingBase CTRL_X_PRIMEVMINFORWARDING_K_INIT_X_X_X_X_VMIN',
                'param': 'EnableHermesMode = ',
                'replace_val': '"False"',
            }
        ]
        self.mod_inst_update(mod_path_off_base, updates_off_base)
        log.info(f'-i- NPRTrigger modify_mod_pupoff: Updated {mod_path_off_base} with PUP off settings.')

        mod_path_off_pup = 'Shared/Modules/TPI/TPI_PUP_XXX/*.mtpl'
        updates_off_pup = [
            {
                'test_instance': 'PlistConfigTC CTRL_X_PLISTCONFIG_E_INIT_X_X_X_X_SKIPSHORT',
                'param': 'OptionValue = ',
                'replace_val': '"True"',
            },
            {
                'test_instance': 'PlistConfigTC CTRL_X_PLISTCONFIG_E_INIT_X_X_X_X_SKIPSHORT',
                'param': 'BypassPort = ',
                'replace_val': '-1',
            }
        ]
        self.mod_inst_update(mod_path_off_pup, updates_off_pup)
        log.info(f'-i- NPRTrigger modify_mod_pupoff: Updated {mod_path_off_pup} with PUP off settings.')
        return 12

    def modify_mod_pupon(self):
        """
        Update NPR related modules based on PUP On condition.
        HERMESMODE in TPI_BASE forcing to set True.
        """
        # Forcing HERMESMODE in TPI_BASE to set "TRUE".
        mod_path_on_base = 'Shared/Modules/TPI/TPI_BASE_XXX/*.mtpl'
        updates_on_base = [
            {
                'test_instance': 'VminForwardingBase CTRL_X_PRIMEVMINFORWARDING_K_INIT_X_X_X_X_VMIN',
                'param': 'EnableHermesMode = ',
                'replace_val': '"True"',
            }
        ]
        self.mod_inst_update(mod_path_on_base, updates_on_base)
        log.info(f'-i- NPRTrigger modify_mod_pupon: Updated {mod_path_on_base} with PUP on settings.')

        # Turn on PrimePUPTestMethod to "Enabled".
        # Unbypass PlistConfigTC skip short __0.
        mod_path_on_pup = 'Shared/Modules/TPI/TPI_PUP_XXX/*.mtpl'
        updates_on_pup = [
            {
                'test_instance': 'PrimePUPTestMethod CTRL_X_PUP_K_TESTPLANENDFLOW_X_X_X_X_PRINTITUFF',
                'param': 'Mode = ',
                'replace_val': '"Enabled"',
            },
            {
                'test_instance': 'PlistConfigTC CTRL_X_PLISTCONFIG_E_INIT_X_X_X_X_SKIPSHORT',
                'param': 'BypassPort = ',
                'replace_val': '-1',
            }
        ]
        self.mod_inst_update(mod_path_on_pup, updates_on_pup)
        log.info(f'-i- NPRTrigger modify_mod_pupon: Updated {mod_path_on_pup} with PUP on settings.')
        return 13

    def mod_inst_update(self, mod_path, updates=None):
        """
        Routine to modify test instance values based on a list of update dicts.

        Each dict in ``updates`` specifies an instance block to find and a key/value
        to replace within that block.

        :param mod_path: Glob path to the target mtpl file(s) - str
        :param updates: List of dicts, each with keys:

            - ``test_instance`` (str): String to identify the target instance block
            - ``param`` (str): String to identify the line to modify within the block
            - ``replace_val`` (str): New value to set after ``param``

        :type updates: list[dict]
        :return: Status code (1=no updates found, 2=no mtpl found, 3=modified, 4=no modification made)
        :rtype: int

        Usage::

            obj.mod_instance_update(
                mod_path='Shared/Modules/TPI/TPI_PUP_XXX/*.mtpl',
                updates=[
                    {
                        'test_instance': 'PrimePUPTestMethod CTRL_X_PUP_K_TESTPLANENDFLOW_X_X_X_X_PRINTITUFF',
                        'param': 'Mode = ',
                        'replace_val': 'Enabled',
                    },
                    {
                        'test_instance': 'PrimeCallbacksRegistrarTestMethod CTRL_X_CALLBACKS_K_INIT_X_X_X_X_PUP',
                        'param': 'LogLevel =',
                        'replace_val': 'Enabled',
                    },
                ]
            )
        """
        if updates is None:
            log.info(f'-i- NPRTrigger mod_instance_update: skipped, no updates provided')
            return 1

        mtpls = glob.glob(mod_path)
        if not mtpls:
            log.info(f'-i- NPRTrigger mod_instance_update: skipped, no mtpl found at {mod_path}')
            return 2

        modified = False
        lines = File(mtpls[0]).raw()

        for update in updates:
            test_instance = update['test_instance']
            param = update['param']
            replace_val = update['replace_val']

            found = False
            for idx in range(len(lines)):
                if test_instance in lines[idx]:
                    found = True
                if found and '}' in lines[idx]:
                    found = False
                if found and lines[idx].lstrip().startswith(param):
                    # Replace everything after param with the new value
                    prefix = lines[idx][:lines[idx].index(param) + len(param)]
                    suffix = lines[idx][lines[idx].index('\n'):] if '\n' in lines[idx] else ''
                    lines[idx] = f'{prefix}{replace_val};{suffix}'
                    modified = True

        if modified:
            File(mtpls[0]).rewrite(''.join(lines), 'NPRTrigger.mod_instance_update()')
            return 3
        else:
            raise ErrorInput('NPRTrigger mod_instance_update: no modification made.',
                             'Either test_instance or param are not found from user updates, please check the inputs and try again.')

    def modify_env(self, outdir):
        """
        Update env for PUP triggering
        """
        # PUP owner defined param
        env_param_list = ['PUP_PATTERNS_DIR', 'NPR_FOLDER_PATH', 'PUP_SHORT_PLISTS_PATH']
        set_value = self.do_puppath_assembl(outdir)

        for param in env_param_list:
            self.tpobj.env.set_item(param, set_value)

        File(self.tpobj.envfile).rewrite(''.join(self.tpobj.env.rebuild()), 'NPRTrigger.modify_env()')  # Enable the PUP trigger in ENV file
        log.info(f'-i- modify_env: Done with env modification for PUP triggering. Set {env_param_list} to {set_value}.')
        return 10

    def do_puppath_assembl(self, outdir):
        """
        engg outdir: I:/engineering/dev/PQV/dtv/xGFx/wwei8/Hermes_PUP_with_bom'
        prod outdir: I:/engineering/dev/sctp/tptorrent/hdmxprogs/nvl/NVLS763B0H02S0BS609'

        Due to different user scenarios, PUP ENV path (PUP_PATTERNS_DIR/NPR_FOLDER_PATH) is updated per conditions below:

        I: drive FULL - 'I:/ulat/pup/release/nvl/NVLXXA0H01U1P'
        V: drive VALL and PARTIAL – 'I:/engineering/dev/sctp/tptorrent/ulat/pup/staging/nvl/NVLXXA0H01U1P'
        MV or Engineering TP - 'I:/engineering/dev/sctp/tptorrent/hdmxprogs/nvl/ulat_mv/pup/1772066770.895739'
        """
        # Grab TP name from either outdir or TP alt name.
        prod_type, tp_name = self.outdir_tpname_decode(outdir)
        prod = self.familyname

        if prod_type:
            # This is production TP, assemble PUP folder name.
            pup_folder = f'{prod.upper()}XX{tp_name[7:15].upper()}'
            if tp_name[14:15].isdigit():  # Check if it's I drive TP. Manual TP Torrent push.
                pup_path = f'I:/ulat/pup/release/{prod}/{pup_folder}'
            else:  # Else is V drive TP.
                pup_path = f'I:/engineering/dev/sctp/tptorrent/ulat/pup/staging/{prod}/{pup_folder}'
        else:
            pup_path = f'I:/engineering/dev/sctp/tptorrent/hdmxprogs/{prod}/ulat_mv/pup/{time.time()}'

        return pup_path

    def outdir_tpname_decode(self, outdir):
        """
        Decode the TP name from the outdir.
        If outdir is None or invalid path, grab information from TP alt name.

        :param outdir: output directory specified by user in yml
        :return: [Upper case]TP name decoded from outdi or TP alt name if outdir is invalid
        """
        # Grab prod name from tp name.
        prod = self.tpobj.get_name()[:3].lower()

        # Analyze the TP path to determine if it's for integration
        prod_path = f'I:/engineering/dev/sctp/tptorrent/hdmxprogs/{prod}'
        regex = re.compile(rf'^{prod.upper()}.{{7}}\d{{2}}[A-Z]\d.{{5}}$')

        name_decode = self.tpobj.get_name()
        if outdir is None:
            return False, name_decode

        # Normalize backslashes to forward slashes for cross-platform comparison
        outdir_unix = outdir.replace('\\', '/')
        if dirname(outdir_unix) == prod_path and re.match(regex, basename(outdir_unix)):
            return True, basename(outdir_unix)
        else:
            return False, name_decode

    def npr_csv_parser(self, file_path, header, value=None, line_number=None):
        """
        Parse the central CSV file for NPR mode configuration.

        Usage: (Type 1) npr_csv_parser(file, header, value="tp_naming")
               (Type 2)npr_csv_parser(file, header, line_number=3

        Two modes of operation:

        **Type 1** - Find line number by column name and value::

            found, lineno = npr_csv_parser('file.csv', 'tp_naming', value='NVLS763B0H02S0BS609')
            # Returns (True, 3) if found, (False, -1) if not found

        **Type 2** - Get value by line number and column name::

            val = npr_csv_parser('file.csv', 'mode', line_number=3)
            # Returns the cell value at that column for the given line

        :param file_path: Path to the CSV file (str)
        :param header: Column header name to search (ignore case-insensitive)
        :param value: (Type 1) The value to match in the column (str or None)
        :param line_number: (Type 2) 1-based line number (excluding header) to read from (int or None)
        :return: (Type 1) tuple of (bool, int) - (found, line_number), (Type 2) str cell value (tuple or str)
        :raises ErrorInput: If file not found, column not found, or line number out of range
        """
        confirm(exists(file_path), f'Config.csv file not found: {file_path}', 'Pls check the file path.')

        with open(file_path, 'r') as fh:
            reader = csv.reader(fh)
            rows = [row for row in reader]

        # Parse header row (first line), case-insensitive column lookup
        first_line = rows[0]
        first_line_lower = [col.strip().lower() for col in first_line]
        header_lower = header.strip().lower()

        col_idx = first_line_lower.index(header_lower)
        data_rows = rows[1:]  # all rows excluding header, 1-based index = data_rows[line_number - 1]

        # ---- Type 1: find line number by value match ----
        if value is not None and line_number is None:
            for idx, row in enumerate(data_rows, start=1):
                if col_idx < len(row) and row[col_idx].strip().lower() == value.strip().lower():
                    log.info(f'-i- npr_csv_parser: found "{value}" in Config.csv column "{header}" at line {idx}')
                    return True, idx
            log.info(f'-i- npr_csv_parser: "{value}" not found in Config.csv column "{header}"')
            return False, -1

        # ---- Type 2: get value by line number and column name ----
        if line_number is not None and value is None:
            row = data_rows[line_number - 1]
            result = row[col_idx].strip()
            log.info(f'-i- npr_csv_parser: line={line_number}, col="{header}" => "{result}"')
            return result

        raise ErrorInput(
            'npr_csv_parser: Invalid usage. Provide either value (Type 1) or line_number (Type 2), not both or neither.',
            'Usage: npr_csv_parser(file, header, value="tp_naming") or npr_csv_parser(file, header, line_number=3)'
        )

    def is_invalid(self):
        """Return non-zero if this TP is not valid for NPR"""
        die_indicator = self.tpobj.usrv.get_var('DieletIndicator.DIELET_INDICATOR', default='')
        if die_indicator == 'PCD':
            log.info('-i- NPRTrigger is skipped, PCD dielet test program.')
            return 3
        if not self.allowed_modules():
            log.info('-i- NPRTrigger is skipped, TP does not have digital (aka, allowed) modules.')
            return 4
        if not isdir(self.trigpath):
            log.info(f'-i- NPRTrigger is skipped, {self.trigpath} not exist')
            return 5
        return 0

    def trigger(self, outdir):
        r"""
        To save TP build time, send a trimmed version of the current test program
        to the PUP trigger path.

        PUP trigger time can run in parallel with TP build non-modification functions.
        The test program is sent as a compressed tarball named ``<fname>.tar.gz``,
        where ``fname`` is taken from ``self.fname`` (or, if not set, generated
        from the current time and process ID). The tarball is copied to
        ``self.trigpath`` and then renamed with a ``.trigger`` suffix to signal NPR.

        The trigger path is typically::

            I:\engineering\dev\sctp\tptorrent\hdmxprogs\nvl\NVL_triggers

        :param outdir: string
        :return: None
        :rtype: None
        """
        if outdir is None:
            content = f'TP_PATH: User defined TP build destination is none, treat as MV.'
            log.info('-i- NPRTrigger trigger: user define TP build destination is None, treat as MV.')

        else:
            content = f'TP_PATH: {outdir}\n'

        uname = curtime().replace(':', '-')
        if not self.fname:
            self.fname = f'{uname}_{os.getpid()}'

        # Build a list of folders which no need for PUP trigger
        input_files_dirs = [p.replace('\\', '/').lstrip('./')
                            for p in (glob.glob('Modules/*/*/InputFiles') + glob.glob('Shared/Modules/*/*/InputFiles'))]
        exclude_list = ['.git', '.github', 'Shared/.github', 'astra', 'TPConfig', 'UserCode', 'Shared/TPConfig', 'temp',
                        'complete_tp.tar.gz'] + input_files_dirs + [f'{self.fname}.tar.gz']

        # Create a trimmed TP tar file.
        TarAdd(f'{self.fname}.tar.gz', '.', exclude=exclude_list)

        # Copy tar.gz to trigpath with .progress extension, then rename to .trigger
        tar_src = f'{self.fname}.tar.gz'
        tar_progress = f'{self.trigpath}/{self.fname}.tar.gz'
        tar_trigger = f'{self.trigpath}/{self.fname}.trigger'
        try:
            File(tar_src).copy(tar_progress)
            log.info(f'-i- Copying {self.fname}.tar.gz to {tar_progress}')
            File(tar_trigger).touch(content)
            log.info(f'-i- NPRTrigger triggered: {tar_trigger}')
            self.trigflag = True
        finally:
            File(tar_src).unlink()  # always clean up local tar.gz

    def wait(self):
        """
        If trigger never happens, skip
        If trigger happens, Wait for the file
        Check for the sccuess file then pass the flow
        Raise errors when the trigger file failed or timeout of generation
        """
        if not self.trigflag:
            log.info('-i- NPRTrigger wait: skipped, trigger did not happen.')
            return 0    # For unit test

        sw = Elapsed()
        log.info(f'-i- NPRTrigger is waiting to finish... Pls wait... timeout of {self.timeout} secs')
        for _ in range(int(self.timeout / self.sleep_sec)):
            force_refresh(self.trigpath)

            successfile = f'{self.trigpath}/{self.fname}.success'
            if exists(successfile):
                log.info(f'-i- NPRTrigger wait: complete after {sw}')
                return 18    # For unit test

            errfile = f'{self.trigpath}/{self.fname}.ERROR'
            if exists(errfile):
                raise ErrorInput(
                    f'NPRTrigger error: {errfile}, after {sw}',
                    'Please check with the GTO team responsible for the trigger process.')

            time.sleep(self.sleep_sec)

        raise ErrorInput(
            f'NPRTrigger wait: timeout of {self.timeout} seconds reached while waiting for PUP trigger to finish.',
            'Please check with the GTO team responsible for the trigger process.')

    def allowed_modules(self):
        """Return True if any digital modules are found in TP for NPR trigger"""

        # digital module regex for folder name
        robj = re.compile('^.?(ARR|FUN|SCN)')  # PSCN or SCN or SFUN or FUN

        # get all modules from stpl
        for mtpl in self.tpobj.get_all_mtpl_from_stpl():  # mtpl is full path to .mtpl file
            modname = basename(dirname(mtpl))  # module folder name
            if robj.search(modname):
                return True  # first found is ok

        return False  # no match, so this tp has no digital module

    @classmethod
    def ignore_func(cls, root, files):
        """
        copytree ignore function
        This routine is called for every directory
        :param root: directory
        :param files: list of files
        :return: ignored files
        """
        for item in [os.path.join(os.sep, _path) for _path in ['astra', 'UserCode']]:
            if item in root:
                return files  # ignore all
        return []  # no ignore
