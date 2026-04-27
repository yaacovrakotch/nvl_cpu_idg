#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
TestProgram audit tool
"""
import setenv      # must be first in the imports
from gadget.vepargs import Args, TA_All, TA_StoreTrue, TA_StoreFile, TA_Store, TA_KeyVal_CaseSensitive
from gadget.vepargs import TA_AppendSC
from gadget.errors import ErrorUser, confirm
from gadget.helperclass import OPT
from gadget.dictmore import DictDot
from gadget.files import File
from gadget.shell import vmsize
from gadget.disk import Chdir
from gadget.gizmo import Elapsed
from gadget.strmore import indent, cjoin, to_seconds
from gadget.tputil import time_disp, volt_disp, log_usage, remove_ip, Units, OtplFile, get_modulename
from gadget.printmore import PrintAlign
from gadget.getgit import GitHub
from os.path import exists, abspath, realpath, basename
from tp.testprogram import TestProgram, PinSoc, Env
from mod.setting import cfg
from mod.tiddb import TidDb
from mod.envreorder import EnvReorder
from mod.moduleskip import ModuleSkip
from mod.alttc import ALttc
from collections import defaultdict
from pprint import pprint
from main.torch_postproc import PlistEdit
import csv as csv_module
import pickle
import re
import json
import glob
import os


class TPInfo(Args):   # parent: ArgsBase
    """
    TestProgram Info
    """

    def config(self):
        """
        Define the arguments for the script.
        The order below will matter, it is the order of display during help.
        """
        cfg = DictDot()
        cfg.all = TA_All('First arg is TP environment file')
        cfg.patrev = TA_StoreTrue('CMD: Display TP Pattern Rev')
        cfg.plist = TA_StoreTrue('CMD: Display all loaded plists. Add -out <path> to copy them.')
        cfg.catplist = TA_StoreTrue('CMD: Concatenate all loaded plists')
        cfg.findplist = TA_Store('CMD: Find given plist and show who uses it', metavar='plist_name_OR_PAT')
        cfg.checkpatlist = TA_StoreTrue('CMD: Check all patlist (demo)')
        cfg.pickle = TA_StoreTrue('CMD: Show info of this pickle file')
        cfg.stats = TA_StoreTrue('CMD: Show TP stats')
        cfg.stats2 = TA_StoreTrue('CMD: Show TP stats -light version')
        cfg.flowall = TA_Store('CMD: Display the flow trace for all (pass*fail)', metavar='<param>|ALL')
        cfg.flowpass = TA_Store('CMD: Display the flow trace for pass flow', metavar='<param>|ALL')
        cfg.envupdate = TA_StoreTrue('CMD: Update the env for latest subroutine (demo)')
        cfg.reformat = TA_StoreTrue('CMD: Reformat mtpl files. Input is positional args')
        cfg.param = TA_AppendSC('Show param values. Use with -flowall|-flowpass ALL', metavar='<param>|_EDCKIL')
        cfg.evg = TA_StoreTrue('CMD: Run the evg report. Positional arg is TP folder (not env file)')
        cfg.prcnt = TA_Store('CMD: Count all PR per TP based on tags. Use "." for arg1 (unused).',
                             metavar='<number_tp_series>')
        cfg.usrv = TA_StoreTrue('CMD: Show evaluated usrv/userv values')
        cfg.alttc = TA_StoreTrue('CMD: Run ALTTC standalone')
        cfg.initlog = TA_Store('CMD: Generate report given two hdmt log of init', metavar='diff|csv')
        cfg.timediff = TA_StoreTrue('CMD: Give the difference between two time string')
        cfg.fix = TA_StoreTrue('CMD: Fix this testprogram for various broken things like :: spaces')
        cfg.vecmem = TA_StoreTrue('CMD: Calculate vecmem used for this testprogram')
        cfg.orderplist = TA_StoreTrue('CMD: Perform smart plist ordering routine')

        # module skip related
        cfg.skipjson = TA_StoreTrue('CMD: Skip the modules from skip_modules.json')
        cfg.skipmod = TA_AppendSC('CMD: Skip the specified modules, separated by comma')
        cfg.skipall = TA_AppendSC('CMD: Skip all modules, keep specified, separated by comma')

        # PLT audits
        cfg.pin = TA_Store('CMD: Inspect pins/pingroups. Input can be .pin file.',
                           metavar='list|dpin|<resourcepin>|<group_name>')
        cfg.soc = TA_StoreFile('CMD: Inspect soc. Arg1 Input can be .pin file.',
                               metavar='file.soc')
        cfg.tim_list = TA_Store('CMD: Display all timing TestConditions. Use DISP to display params.',
                                metavar='param|DISP|ANY')
        cfg.lvl_list = TA_Store('CMD: Display all levels TestConditions. Use DISP to display params.',
                                metavar='param|DISP|ANY')
        cfg.tim_pin = TA_Store('CMD: Checks timing pins. Use "." for all',
                               metavar='timname_regex|.|DISP')

        cfg.tim_tc = TA_Store('CMD: Display all params given tim TestCondition', metavar='tc')
        cfg.lvl_tc = TA_Store('CMD: Display all params given lvl TestCondition', metavar='tc')
        cfg.lvl_ps = TA_AppendSC('CMD: Generate levels powersupply values .csv for all TC',
                                 metavar='VForce|VIH|VIL|VOX')

        # Patterns and tids
        cfg.flatreset = TA_Store('CMD: Display all flattened resets for pass flow. Arg is "resetplb" or pattern_startswith',
                                 metavar='resetplb_')
        cfg.tid_find = TA_Store('CMD: Display all instances where this TID is used.', metavar='tid#_chunk')
        cfg.unused_pat = TA_StoreTrue('CMD: Display unused patterns and its patlist')
        cfg.used_pat = TA_StoreTrue('CMD: Display used patterns and its patlist')
        cfg.tid = TA_Store('CMD: Audit tid usage (specify module or ALL)', metavar='module|ALL')
        cfg.tid_dump = TA_Store('CMD: tid csv dump, use -out', metavar='module|ALL')
        cfg.summary = TA_StoreTrue('Show summary only. Used with -tid')
        cfg.out = TA_Store('Specify which file to write output', metavar='outfile')
        cfg.content = TA_AppendSC('CMD: Generate the per-module content summary', metavar='sort_tp(s)')
        cfg.patlist = TA_StoreTrue('CMD: Display module, patlist, pattern for pass&fail flow')
        cfg.plbdependent = TA_StoreTrue('CMD: Display plist dependent and missing plbs')
        cfg.ituff = TA_StoreFile('Specify ituff. Used with -flatreset, -flowall, -flowpass', metavar='file.ituff')
        cfg.repo = TA_Store('Specify which repo folder. This is confi2.json key name. Used with -prcnt', metavar='mtlp68')
        cfg.detail = TA_StoreTrue('Run the testinstance detail report. Used with -evg')

        # tp options
        cfg.stpl = TA_StoreFile('Specify stpl file', metavar='file.stpl')
        cfg.loc = TA_Store('Specify location', metavar='CLASSHOT')
        cfg.pgmrule_disp = TA_StoreTrue('Display pgmrule apply info')
        cfg.vars = TA_KeyVal_CaseSensitive('Specify Vars', metavar='SCVars.SC_REV=E')
        cfg.nopickle = TA_StoreTrue('Do not use / create pickle cache file. Used with -stat only')
        cfg.grp = TA_AppendSC('Specify domain names to check with. Used with -tim_pin', metavar='domain_name')

        return cfg

    def main(self):
        """
        Main entry point of executable
        -h will not reach this method, since that is taken cared of in Args Base class
        """
        if not OPT.all:
            print("Error: First argument must be testprogram env file.")
            print("Usage: tp_info.py <path_to_env_file> <command_options>")
            print("Execute 'tp_info.py -h' for more info.")
            exit(0)

        if not exists(OPT.all[0]):
            raise ErrorUser("[%s] does not exist" % OPT.all[0],
                            "Pls provide env file that exist")

        # list of arg commands (will be translated to do_<argument>()
        log_usage('tp_audit', cfg)
        self.call_methods(['patrev',    # this will call do_patrev(), if -patrev
                           'plist',     # this will call do_plist(), if -plist
                           'catplist',  # this will call do_catplist(), if -catplist
                           'findplist',  # this will call do_findplist(), if -findplist
                           'checkpatlist',  # this will call do_checkpatlist(), if -checkpatlist
                           'stats',     # this will call do_stats(), if -stats
                           'stats2',     # this will call do_stats2(), if -stats2
                           'tim_list',  # this will call do_tim_list(), if -tim_list
                           'tim_pin',   # this will call do_tim_pin(), if -tim_pin
                           'lvl_list',  # this will call do_lvl_list(), if -lvl_list
                           'pickle',    # this will call do_pickle(), if -pickle
                           'tim_tc',    # this will call do_tim_tc(), if -tim_tc
                           'lvl_tc',    # this will call do_lvl_tc(), if -lvl_tc
                           'tid_find',  # this will call do_tid_find(), if -tid_find
                           'tid',       # this will call do_tid(), if -tid
                           'tid_dump',  # this will call do_tid_dump(), if -tid_dump
                           'unused_pat',  # this will call do_unused_pat(), if -unused_pat
                           'used_pat',  # this will call do_used_pat(), if -used_pat
                           'lvl_ps',    # this will call do_lvl_ps(), if -lvl_ps
                           'pin',       # this will call do_pin(), if -pin
                           'soc',       # this will call do_pin(), if -soc
                           'flowall',   # this will call do_flowall(), if -flowall
                           'flowpass',  # this will call do_flowpass(), if -flowpass
                           'envupdate',  # this will call do_envupdate(), if -envupdate
                           'skipjson',  # this will call do_skipjson(), if -skipjson
                           'skipmod',   # this will call do_skipmod(), if -skipmod
                           'skipall',   # this will call do_skipall(), if -skipall
                           'content',   # this will call do_content(), if -content
                           'reformat',  # this will call do_reformat(), if -reformat
                           'patlist',   # this will call do_patlist(), if -patlist
                           'flatreset',  # this will call do_flatreset(), if -flatreset
                           'plbdependent',   # this will call do_plbdependent(), if -plbdependent
                           'evg',            # this will call do_evg(), if -evg
                           'prcnt',          # this will call do_prcnt(), if -prcnt
                           'usrv',           # this will call do_usrv(), if -usrv
                           'alttc',          # this will call do_alttc(), if -alttc
                           'initlog',        # this will call do_initlog(), if -initlog
                           'timediff',       # this will call do_timediff(), if -timediff
                           'fix',            # this will call do_fix(), if -fix
                           'vecmem',         # this will call do_vecmem(), if -vecmem
                           'orderplist',     # this will call do_orderplist(), if -orderplist
                           ])           # do_else() is called if no argument command is processed

    def do_orderplist(self):
        """Commandline smart plist reorder"""
        tp = TestProgram(OPT.all[0], stpl=OPT.stpl, location=OPT.loc, vars=OPT.vars)
        PlistEdit(tp).main()
        print(f'-i- Success: orderplist')

    @classmethod
    def do_usrv(cls):      # class method since it is called in test_timlvl
        """Display userv values"""
        sw = Elapsed()
        tp = TestProgram(OPT.all[0], stpl=OPT.stpl, location=OPT.loc, vars=OPT.vars)
        tp.usrv.set_data()
        tp.usrv.print_usrv()
        print(f'-i- Elapsed: {sw}')

    def do_vecmem(self):
        """Calculate vecmem"""
        tp = TestProgram(OPT.all[0], stpl=OPT.stpl, allpats=True).pickle_init()
        allpats = tp.plists.get_pats_all()

        # read vecmem info from ci_plist area
        perpat = defaultdict(dict)
        for item in sorted(tp.env.get_plist_paths()):
            fname = f'{item}/../doc/vecmem_perpat.txt'
            if exists(fname):
                for line in File(fname).chomp():
                    elems = line.replace(':', ' ').split()
                    if 'K' in elems[-1]:
                        perpat[elems[0]][elems[-2]] = int(float(elems[-1].replace('K', '')) * 1000)
                    else:    # pragma: no cover    fyi only
                        print(f"Oops: {elems[-1]} of {fname}")

        # sum it
        vsum = defaultdict(int)
        missing = []
        for pat in allpats:
            if pat in perpat:
                for domain in perpat[pat]:
                    vsum[domain] += perpat[pat][domain]
            else:
                missing.append(pat)

        # display it
        print()
        print(f'Patterns with no vecmem info: {len(missing)}')
        for pat in missing:
            print(f'   {pat}')
        print()

        print("Vecmem Summary per domain:")
        pa = PrintAlign(header=False, rjust=False, space=0, sep='   ')
        for domain in sorted(vsum, key=lambda x: x.split('_')[1] if len(x.split('_')) > 1 else x):
            pa(domain, '%10d' % vsum[domain])

        pa.disp()

    def do_fix(self):
        """
        Do one-time fix which is not done by OtplFile(). This is usually on alien TP used for various things.
        Fix#1 - ::\\s\\w+
        """
        tp = TestProgram(OPT.all[0], stpl=OPT.stpl)
        r_colon = re.compile(r"::\s+")
        for mtpl in tp.get_all_mtpl_from_stpl():
            final = []
            for line in File(mtpl).raw():
                if '::' in line and r_colon.search(line):
                    line = r_colon.sub('::', line)
                final.append(line)
            File(mtpl).rewrite(''.join(final), 'do_fix()')

    def do_alttc(self):
        """Call ALTTC module"""
        tp = TestProgram(OPT.all[0], stpl=OPT.stpl, location=OPT.loc, vars=OPT.vars)

        # Cannot do init() because it will fail various pgm rules since we are initting the source repo (before expland)
        # Thus, initialize mtpl manually
        tp.mtpl.read_mtpls()
        tp.mtpl.read_mtpl_flow()

        ALttc(tp).main()

    def do_timediff(self):     # pragma: no cover    - dev only
        """Generate report given to hdmtos log of init()"""
        confirm(len(OPT.all) == 3,
                'Usage: tp_audit.py <anyvalidfile_ignored> 01:01:02 01:01:03 -timediff',
                'Pls fix commandline args')
        diff = to_seconds(OPT.all[1]) - to_seconds(OPT.all[2])
        print(f'{diff:.3f} Seconds')
        hr = int(diff / 3600)
        print('%s hr %s min %s sec' % (hr, int((diff - hr * 3600) / 60), int(diff) % 60))

    def do_initlog(self):     # pragma: no cover    - dev only
        """
        Generate report given to hdmtos log of init()
        Two usage:
        tp_audit.py hdmtlog1.txt hdmtlog2.txt -initlog 0            # compare two init hdmt tos log
        tp_audit.py hdmtlog1.txt hdmtlog2.txt ... -initlog csv     # Display hdmt tos log in csv
        """
        confirm(len(OPT.all) >= 2,
                'Usage: tp_audit.py hdmtlog1.txt hdmtlog2.txt ... -initlog',
                'Pls fix commandline args')

        r_start = re.compile(r"^\[\S+\s+([\d:\.]+)\].*StartTest\s+(\S+)")
        r_stop = re.compile(r"^\[\S+\s+([\d:\.]+)\].*StopTest\s+(\S+)")

        def read_one(fname):
            data = {}
            stime = None
            for line in File(fname).chomp():
                res = r_start.search(line)
                if res:
                    stime = to_seconds(res.group(1))
                res = r_stop.search(line)
                if res:
                    assert stime, f'No StartTest found for: {line}'
                    data[res.group(2)] = to_seconds(res.group(1)) - stime
            return data

        if OPT.initlog == 'diff':
            # ======= Usage 1
            data1 = read_one(OPT.all[0])
            data2 = read_one(OPT.all[1])
            for item in data1:
                if item in data2:
                    diff = data1[item] - data2[item]
                    if abs(diff) > 1.0:
                        print(f'{data1[item]:7.3f} - {data2[item]:7.3f} = {diff:7.3f} : {item}')
        else:
            # ======= Usage 2
            # header first
            print("instance,%s" % (','.join(OPT.all)))
            data = []
            allkeys = set()
            for ff in OPT.all:
                data.append(read_one(ff))
                allkeys.update(data[-1])

            for item in sorted(allkeys):
                row = [item]
                for idx, _ in enumerate(OPT.all):
                    if item in data[idx]:
                        row.append(f"{data[idx][item]:.3f}")
                    else:
                        row.append('')
                print(','.join(row))

    def do_evg(self):         # pragma: no cover    - temporary, long term call via release
        """Give the evergreen to prime report"""
        from datetime import datetime
        with Chdir(OPT.all[0]):
            result = self.evg()
            tpname = basename(realpath(OPT.all[0]))
            dt = datetime.fromtimestamp(os.path.getmtime('.'))
            deyt = dt.strftime("%Y%m%d")

            # determine path
            if OPT.detail:
                path = f'/intel/tpvalidation/engtools/tptools/mtl/infra/dashboard/primedetail_indicator/{tpname}_{deyt}_6248.json'
            else:
                path = f'/intel/tpvalidation/engtools/tptools/mtl/infra/dashboard/prime_indicator/{tpname}_{deyt}_6248.json'
            if OPT.out:
                path = OPT.out     # user specified

            with open(Env.xpath(path), 'w') as fh:
                json.dump(result, fh, indent=3)
            print(f'Written: {path}')

    @classmethod
    def evg(cls):
        """
        evg prime report callable routine
        :return: dictionary
        """
        env = glob.glob('POR_TP/*/*.env')
        confirm(len(env) > 0, f'Expecting one env: {env}', f'Check {os.getcwd()}')
        tp = TestProgram(sorted(env)[0])
        d_evg = defaultdict(int)
        d_prime = defaultdict(int)
        l_all = []
        for mtpl in tp.get_all_mtpl_from_stpl():
            mod = get_modulename(mtpl)
            for lno, line in OtplFile(mtpl).readline():
                if not line.startswith(('Test ', 'TrialTest ', 'CSharpTest ', 'CSharpTrialTest ')):
                    continue
                tokens = line.split()
                template = tokens[1]
                tname = tokens[2]
                if template.startswith(('iC', 'OASIS_code')):
                    d_evg[mod] += 1
                    l_all.append(('EVG', template, mod, tname))
                else:
                    d_prime[mod] += 1
                    l_all.append(('Prime', template, mod, tname))

        # Display details per testinstance and template
        if OPT.detail:
            final = []
            for item in sorted(l_all):
                ep, template, mod, tname = item
                final.append({'module': mod,
                              'team': mod.split('_')[0],
                              'evg_or_prime': ep,
                              'template': template,
                              'tiname': tname})
            return final

        final = []
        for item in sorted(d_evg.keys() | d_prime.keys()):
            final.append({'module': item,
                          'team': item.split('_')[0],
                          'evg': d_evg[item],
                          'prime': d_prime[item],
                          'total': d_evg[item] + d_prime[item]})
        return final

    def do_prcnt(self):     # pragma: no cover    - unused
        """
        PR count per TP based on tags (including patches / RC)
        Assumptions:
        1 - branch names are TP/<rev> and TP/RC_<rev>
        2 - tag names are TP_<string>
        """
        print("Pls run directly from web using PR_CNT=SUM|DETAIL|TEAM")
        # from mod.cci_list import CCI
        # ver = OPT.prcnt
        # confirm(OPT.repo, '-repo <key_from_config2.json> is required', 'eg. mtlp68')
        #
        # # get all branches, including RC branches
        # allbr = []
        # for br in sorted(GitHub.get_all_branches()):
        #     if re.search(f'^(TP/|TP/RC_){ver}', br):
        #         allbr.append(br)
        #
        # results = []
        # for idx, br in enumerate(allbr):
        #     print(f'Processing {br}: {idx} of {len(allbr)-1}:')
        #     cci = CCI(br, 10000, repo=OPT.repo)      # This works given one branch
        #     res = cci.main(cmd_prcnt='.')
        #     results.extend(res)
        #     print(f"Found: {br}: {len(res)}")
        #
        # # Display result
        # print('===================')
        # print("TP, date, PR_count")
        # print('\n'.join(sorted(results, key=lambda x: x.split()[1])))

    def do_envupdate(self):    # pragma: no cover    - demo/testing only
        tp = TestProgram(OPT.all[0])
        EnvReorder(tp).main(disp=True)

    def do_skipjson(self):
        ModuleSkip.skipjson_main(OPT.all[0])

    def do_skipmod(self):
        tp = TestProgram(OPT.all[0])
        ModuleSkip(tp, modlist=OPT.skipmod).main()    # modify it
        print("Checking....")
        tp1 = TestProgram(OPT.all[0])
        result = len(list(tp1.mtpl.iter_flows()))
        print(f"Success: total instances={result}.")

    def do_skipall(self):
        tp = TestProgram(OPT.all[0])
        ModuleSkip(tp, onlylist=OPT.skipall).main()    # modify it
        print("Checking....")
        tp1 = TestProgram(OPT.all[0])
        result = len(list(tp1.mtpl.iter_flows()))
        print(f"Success: total instances={result}.")

    def do_pickle(self):
        """Do -pickle, show testprogram info given pickle file"""
        with open(OPT.all[0], 'rb') as fh:
            tp = pickle.load(fh)

        for key, item in tp.pickle_key().items():
            print('%-8s: %s' % (key, item))
        exit(0)

    def do_patrev(self):
        """
        Display all pattern rev paths (plb)
        """
        tp = TestProgram(OPT.all[0])
        tp.env.set_env()
        for item in sorted(tp.env.get_plist_paths()):
            print(item)

    def do_findplist(self):
        """
        Display which plist file is a particular plist or pattern used
        """
        inp = OPT.findplist
        prevline = ""
        space = "   "
        print(f'-i- Finding [{inp}] from all loaded plists...')
        tp = TestProgram(OPT.all[0])
        tp.plists.set_plist_list()
        for plist_file in sorted(tp.plists.get_plist_list()):
            stack = []
            for lno, line in OtplFile(plist_file).readline():
                if line.startswith('{'):
                    stack.append(prevline)
                if line.startswith('}'):
                    stack.pop()

                # display
                if inp in line:
                    print()
                    print(f'File: {plist_file}')
                    for idx, stk in enumerate(stack):
                        print(f'{space*idx}{stk}')
                    print(f"FOUND >>> {line}")
                    break    # first occurrence only

                prevline = line

    def do_plist(self):
        """
        Display all loaded plists
        """
        tp = TestProgram(OPT.all[0])
        tp.plists.set_plist_list()
        for item in sorted(tp.plists.get_plist_list()):
            print(item)
            if OPT.out:
                File(item).copy(OPT.out)

    def do_plbdependent(self):
        """
        Display plist dependency
        """
        tp = TestProgram(OPT.all[0], allpats=True)
        dependents = tp.plists.get_plist_dependent()       # {plist: set_of_plist_dependent}
        result = {k: v for k, v in dependents.items() if v}
        pprint(result)

    def do_catplist(self):
        """
        Concatenate all loaded plists
        """
        tp = TestProgram(OPT.all[0])
        tp.plists.set_plist_list()
        for item in sorted(tp.plists.get_plist_list()):
            print(f'# File: {item}')
            print(File(item).read())

    def do_checkpatlist(self):
        """
        Checker demo - get all patlist and see if they all exist in .plist files
        This uses iter_tests() which does not look at connectivity or bypassed
        """
        tp = TestProgram(OPT.all[0], stpl=OPT.stpl, location=OPT.loc, vars=OPT.vars).pickle_init()
        testinstances = list(tp.mtpl.iter_tests(key_name='patlist'))

        errors = set()
        for mod, tn, dd, _ in testinstances:
            plb = remove_ip(dd['patlist'])
            if plb not in tp.plists.get_plb_map():
                errors.add('Error: %s in %s is not found in any .plist. Bypass=%s'
                           '' % (plb, mod, tp.mtpl.is_bypassed(mod, tn)))

        # Display errors
        for line in sorted(errors):
            print(line)
        print('-i- Done checking %s patlists' % len(testinstances))

    def do_stats(self):
        """
        Load all info of testprogram and show stats
        """
        sw = Elapsed()
        print("-i- Start: %s" % vmsize())

        tpx = TestProgram(OPT.all[0], stpl=OPT.stpl, location=OPT.loc, vars=OPT.vars)
        if OPT.nopickle:
            tp = tpx.init()
        else:
            tp = tpx.pickle_init()

        # Optional inits
        tp.pin.set_data()

        # Display results
        print("Total: %6d patterns" % len(tp.plists.get_pats_all()))
        print("Total: %6d GlobalPlists" % len(tp.plists.get_plb_map()))
        print("Total: %6d testinstances" % len(list(tp.mtpl.iter_tests())))
        print("Total: %6d testinstances with patlist" % len(list(tp.mtpl.iter_tests(key_name='patlist'))))
        print("Total: %6d testinstances connected" % len(list(tp.mtpl.iter_flows(keyparam='patlist'))))
        print("Total: %6d testinstances non-bypass" % len(list(tp.mtpl.iter_flows(bypass=True, keyparam='patlist'))))
        print("Total: %6d mtpl files" % len(list(tp.get_all_mtpl_files())))
        print("Total: %6d flows total" % len(list(tp.mtpl.iter_flows())))
        print("Total: %6d flows pass" % len(list(tp.mtpl.iter_flows(passonly=True))))
        print("Total: %6d timing test condition" % len(list(tp.timing.iter_tc())))
        print("Total: %6d level test condition" % len(list(tp.levels.iter_tc())))
        print("Total: %6d uservars" % len(tp.usrv.get_usrv_map()))
        print("Total: %6d pgmrule lines" % tp.pgmrules._cnt_items)
        print("Total: %6d pgmrule applied" % tp.pgmrules._cnt_apply)
        print("-i- Elapsed: %s: vmsize: %s" % (sw, vmsize()))

    def do_stats2(self):
        """
        Load all info of testprogram and show stats
        """
        sw = Elapsed()
        print("-i- Start: %s" % vmsize())

        tpx = TestProgram(OPT.all[0], stpl=OPT.stpl, location=OPT.loc, vars=OPT.vars)
        tp = tpx.init(light=True)

        # Display results
        print("Total: %6d patterns" % len(tp.plists.get_pats_all()))
        print("Total: %6d GlobalPlists" % len(tp.plists.get_plb_map()))
        print("Total: %6d testinstances" % len(list(tp.mtpl.iter_tests())))
        print("Total: %6d testinstances with patlist" % len(list(tp.mtpl.iter_tests(key_name='patlist'))))
        print("Total: %6d testinstances connected" % len(list(tp.mtpl.iter_flows(keyparam='patlist'))))
        print("Total: %6d mtpl files" % len(list(tp.get_all_mtpl_files())))
        print("Total: %6d flows total" % len(list(tp.mtpl.iter_flows())))
        print("Total: %6d flows pass" % len(list(tp.mtpl.iter_flows(passonly=True))))
        print("-i- Elapsed: %s: vmsize: %s" % (sw, vmsize()))

    def do_tim_tc(self):
        """Display info given timing testcondition"""
        tp = TestProgram(OPT.all[0], stpl=OPT.stpl, location=OPT.loc, vars=OPT.vars).pickle_init()
        for param, eqn in tp.timing.iter_params(OPT.tim_tc):
            print('%-25s %-13s %s' % (param,
                                      time_disp(tp.timing.get_tc_value(OPT.tim_tc, param)),
                                      eqn))

    def do_lvl_ps(self):
        """Generate .csv for all level pins"""
        tp = TestProgram(OPT.all[0], stpl=OPT.stpl, location=OPT.loc, vars=OPT.vars).pickle_init()

        msg = f'Error: Pls remove .csv extension in [-out {OPT.out}] since .csv and attribute will be added in name'
        assert not (OPT.out and OPT.out.endswith('.csv')), msg

        for item in OPT.lvl_ps:
            self._lvl_ps(tp, item)

    def _lvl_ps(self, tp, item):
        """Do one item of -lvl_ps"""

        # display header
        if OPT.out:
            result = [f'Pin,Var/Val,{item},Equation,TestCondition']
        else:
            print()
            print(f'{"Pin":25} {"var/val":23} {item:10}  {"Equation":23} TestCondition')

        for tc in sorted(tp.levels.iter_tc()):
            dd = tp.levels.get_lvl_pin_val(tc, item)
            for pin in sorted(dd):
                var, val, eqn = dd[pin]
                if isinstance(val, str):
                    assert not val, f'Error: [{val}] is expected to be numeric. Pls debug'
                    val = Units.to_number(var)

                if OPT.out:
                    result.append(f'{pin},{var},{val},{eqn},{tc}')
                else:
                    sval = '%6.3f' % val
                    print(f'{pin:25} {var:23} {sval:10}  {eqn:23} {tc}')

        if OPT.out:
            outfile = f'{abspath(OPT.out)}.{item}.csv'
            with open(outfile, 'w') as fho:
                fho.write('\n'.join(result))
            print(f'-i- [{outfile}] is written')
        else:
            print('-i- Add [-out <outfile>] to write to csv')

    def do_lvl_tc(self):
        """Display info given level testcondition"""
        tp = TestProgram(OPT.all[0], stpl=OPT.stpl, location=OPT.loc, vars=OPT.vars).pickle_init()

        # display the power supplies
        tp.levels.get_lvl_param(OPT.lvl_tc, display=True)

        print()
        print('Equations:')
        for param, eqn in tp.levels.iter_params(OPT.lvl_tc):
            print('%-25s %-13s %s' % (param,
                                      volt_disp(tp.levels.get_tc_value(OPT.lvl_tc, param)),
                                      eqn))

    def do_tim_pin(self):
        """Do timing check with regards to pins"""
        tp = TestProgram(OPT.all[0], stpl=OPT.stpl, location=OPT.loc, vars=OPT.vars).pickle_init()
        tc = TimCheck(tp, OPT.tim_pin, OPT.grp)
        tc.main()

    def do_tim_list(self):
        """Do timing list"""
        self.timlvl_list(OPT.tim_list, None)

    def do_lvl_list(self):
        """Do levels list"""
        self.timlvl_list(None, OPT.lvl_list)

    def timlvl_list(self, tim, lvl):
        """Display all testconditions and value of param"""
        tp = TestProgram(OPT.all[0], stpl=OPT.stpl, location=OPT.loc, vars=OPT.vars).pickle_init()

        if tim:
            obj = tp.timing
            disp = time_disp
            input = tim
        else:
            obj = tp.levels
            disp = volt_disp
            input = lvl

        for tc in sorted(obj.iter_tc()):

            # display all params on the first one
            if input == 'DISP':
                print("TestCondition: %s" % tc)
                for param, val in sorted(obj.iter_params(tc)):
                    print("%s = %s" % (param, val))
                return

            if input == 'ANY':
                if list(obj.iter_params(tc)):
                    useparam = sorted(obj.iter_params(tc))[0][0]
                else:    # pragma: no cover   (MTL cornercase, when specificationset is empty)
                    useparam = None
            else:
                useparam = input

            # normal output
            try:
                value = obj.get_tc_value(tc, useparam)
            except BaseException:
                value = "NOT_FOUND"

            print('%-25s = %s %s' % (useparam, disp(value), tc))

    def do_tid_find(self):
        """Display all testinstances given tid"""
        tid = OPT.tid_find
        assert '_' in tid, f'Pls use [-tid_find {tid}_00]. Input tid should have chunk.'

        tp = TestProgram(OPT.all[0], stpl=OPT.stpl, location=OPT.loc, vars=OPT.vars).pickle_init()
        tdb = TidDb(tp)
        items = tdb.get_tid(tid)
        if not items:
            print(f"tid {tid} is not found in flow")
            return

        pa = PrintAlign(header=False, rjust=False, space=0, sep=' ')
        plbset = set()
        for item in sorted(items):
            key = ('%s,%s,%s,%s' % (item[tdb.MOD],
                                    item[tdb.COR],
                                    item[tdb.FRQ],
                                    item[tdb.EKL]))
            instdata = tdb.get_inst(item[tdb.MOD], item[tdb.TI_])
            pa('Found', tid, 'in:', key, item[tdb.TI_], instdata['patlist'])
            plbset.add(instdata['patlist'])
        pa.disp()

        # Display location of each plb
        print()
        print("patlist to filename map:")
        pa = PrintAlign(header=False, rjust=False, space=0, sep=' ')
        for plb in sorted(plbset):
            pa(plb, tp.plists.plb_to_filename([plb], fullpath=True))
        pa.disp()

    def do_reformat(self):
        """Reformat given files so that it is properly indented"""
        for ff in OPT.all:
            OtplFile(ff).reformat()

    def do_content(self):
        """Content rollup per module edc/kill"""
        assert len(OPT.all) == 2, 'Usage: tp_audit.py class_TP_previous class_TP_current -content sort_TP_cdie -content sort_TP_gdie'

        ContentSummary().compare(OPT.all[0], OPT.all[1])

    def do_tid(self):
        """Audit all tid"""
        tp = TestProgram(OPT.all[0], stpl=OPT.stpl, location=OPT.loc, vars=OPT.vars).pickle_init()
        tdb = TidDb(tp)
        dctr = tdb.summary_mod_tid()
        if OPT.tid != 'ALL':
            robj = re.compile(f'^{OPT.tid}')
            dctr = {x: y for x, y in dctr.items() if robj.search(y[1]['MOD'])}

        print('Summary:')
        print('========')
        for n, item in enumerate(sorted(dctr), 1):
            print("%s. %-35s %4d tids" % (n, item, len(dctr[item][0])))
        if OPT.summary:
            return

        print()
        print('TestInstances:')
        print('==============')
        for n, item in enumerate(sorted(dctr), 1):
            print("%s. %-35s %4d tids" % (n, item, len(dctr[item][0])))

            # Display all testinstances
            for tn in sorted(dctr[item][2]):
                patlist = tdb.get_inst(dctr[item][1]['MOD'], tn)['patlist']
                cnt = len(tp.plists.get_pats_from_plb(patlist))
                print(f'   {cnt:4} {tn:80} {patlist}')

        print()
        print('Patterns:')
        print('=========')
        for n, item in enumerate(sorted(dctr), 1):
            print("%s. %-35s %4d tids" % (n, item, len(dctr[item][0])))

            # Display all patterns
            md = dctr[item][1]['MOD']
            result = {tdb.get_inst(md, tn)['patlist'] for tn in dctr[item][2]}
            for nn, patlist in enumerate(sorted(result), 1):
                print(f'   {n}.{nn}. {patlist}:')
                for idx, pat in enumerate(tp.plists.get_pats_from_plb(patlist, order=True), 1):
                    print(f'      {n}.{nn}.{idx}. {pat}')

    def do_tid_dump(self):
        """Write csv tid"""
        assert OPT.out, '-out <outfile.csv> is required to write output'
        tp = TestProgram(OPT.all[0], stpl=OPT.stpl, location=OPT.loc, vars=OPT.vars).pickle_init()
        tdb = TidDb(tp)
        if OPT.tid_dump == 'ALL':
            tdb.dump(OPT.out)
        else:
            tdb.dump(OPT.out, re.compile(f'^{OPT.tid_dump}'))
        print(f'-i- Output written to {abspath(OPT.out)}')

    def do_unused_pat(self):
        """Display unused patterns"""
        tp = TestProgram(OPT.all[0], stpl=OPT.stpl, location=OPT.loc, vars=OPT.vars, allpats=True).pickle_init()

        # get all patlists
        allplb = set()
        kwargs = dict(passonly=False, bypass=True, keyparam='patlist', idict=True, edict=True)
        for mod, item, data in tp.mtpl.iter_flows('MAIN', **kwargs):
            allplb.add(remove_ip(data['patlist']))

        # get all used pats
        used_pats = set()
        for plb in allplb:
            used_pats.update(tp.plists.get_pats_from_plb(plb))

        # get all pats
        plb_map = tp.plists.get_plb_map()
        result = []
        for pat in tp.plists.get_pats_all():
            if pat in used_pats:
                continue
            patlists = set()
            for plb in tp.plists.get_plbs_usedby_pat(pat):
                patlists.add(plb)
            str_patlist = ','.join(sorted(patlists))
            ci_module = tp.plists.get_modname(plb_map[plb])
            result.append(f'{ci_module} {pat} {str_patlist}')

        # display/write
        self.disp_or_csv(result)

    @staticmethod
    def disp_or_csv(result):
        """
        Write to screen or write to csv given result list
        :param result: list, lines, space delimited
        """
        if OPT.out:
            with open(OPT.out, 'w') as fh:
                for line in sorted(result):
                    fh.write('%s\n' % line.replace(' ', ','))
            print(f'-i- {abspath(OPT.out)} is written')
        else:
            for line in sorted(result):
                print(line)
            print('-i- Add [-out <outfile.csv>] to write to csv')

    def do_used_pat(self):
        """Display used patterns"""
        tp = TestProgram(OPT.all[0], stpl=OPT.stpl, location=OPT.loc, vars=OPT.vars).pickle_init()

        # get all patlists
        allplb = {}
        kwargs = dict(passonly=False, bypass=True, keyparam='patlist', idict=True, edict=True)
        for mod, tn, data in tp.mtpl.iter_flows('MAIN', **kwargs):
            plb = remove_ip(data['patlist'])
            allplb[plb] = (mod, tn)

        # get all used pats
        used_pats = set()
        for plb in allplb:
            used_pats.update(tp.plists.get_pats_from_plb(plb))

        # get all pats
        plb_map = tp.plists.get_plb_map()
        result = []
        for pat in used_pats:
            patlists = set()
            mod, tn = None, None
            for plb in sorted(tp.plists.get_plbs_usedby_pat(pat)):
                if plb in allplb:
                    patlists.add(plb)
                    mod, tn = allplb[plb]    # first one
            str_patlist = ','.join(sorted(patlists))
            ci_module = tp.plists.get_modname(plb_map[plb])

            result.append(f'{mod} {ci_module} {pat} {tn} {str_patlist}')

        # display/write
        self.disp_or_csv(result)

    def do_soc(self):
        """soc audits"""

        # Input can either be .env or .pin
        infile = OPT.all[0]
        if infile.endswith('.pin'):
            po = PinSoc(None)
            po.set_data(infile)
        else:
            po = TestProgram(infile).pin
            po.set_data()

        p2d = po.get_pin2domain()
        soc = po.read_soc(OPT.soc)
        unc = {pin: ('[U]' if soc[pin]['u'] else '') for pin in soc}
        pa = PrintAlign(header=False, rjust=False, space=0, sep=' ')
        for pin in sorted(po.get_resource('dpin')):
            assert pin in soc, f'[{pin}] is not found in {OPT.soc}'
            pa(pin, soc[pin]['ch'], unc[pin], ', '.join(sorted(p2d.get(remove_ip(pin), {'_NO_DOMAIN_'}))))
        pa.disp()

    def do_pin(self):
        """pin audits"""

        # Input can either be .env or .pin
        infile = OPT.all[0]
        if infile.endswith('.pin'):
            po = PinSoc(None)
            po.set_data(infile)
        else:
            po = TestProgram(infile).pin
            po.set_data()

        # Option1: list all domain/resource/group
        if OPT.pin == 'list':
            pa = PrintAlign(header=False, rjust=False, space=0, sep=' ')

            dd = po.get_domains()
            for item in sorted(dd):
                pa('Domain', item, len(dd[item]))

            dd = po.get_resources()
            for item in sorted(dd):
                pa('Resource', item, len(dd[item]))

            dd = po.get_groups()
            for item in sorted(dd):
                pa('Group', item, len(dd[item]))

            pa.disp()
            return

        # Option2: list all digital pins and their domains
        p2d = po.get_pin2domain()
        if OPT.pin == 'dpin':
            pa = PrintAlign(header=False, rjust=False, space=0, sep=' ')
            for pin in sorted(po.get_resource('dpin')):
                pa(pin, 'Domains: ', ', '.join(sorted(p2d.get(remove_ip(pin), {'_NO_DOMAIN_'}))))
            pa.disp()
            return

        # Option3: display which group this pin is associated with
        if po.is_resource(OPT.pin):
            targetpin = remove_ip(OPT.pin)
            for dd in (po.get_domains(), po.get_groups()):
                for item in dd:
                    for pin in po.flatten(item):
                        if pin == targetpin or pin.endswith(f':{targetpin}'):
                            print(f'{pin} Found in {item}')
            return

        # Option4: list the pins of a domain or group - flattened
        pa = PrintAlign(header=False, rjust=False, space=0, sep=' ')
        for pin in po.flatten(OPT.pin, strip_ip=True):     # This will error out if pin is not found
            pa(pin, 'Domains: ', ', '.join(sorted(p2d[pin])))
        pa.disp()

    def do_flatreset(self):
        """Display all resets of pass flow"""
        tp = TestProgram(OPT.all[0], stpl=OPT.stpl, location=OPT.loc, vars=OPT.vars, allpats=True).pickle_init()
        tname_set = tp.mtpl.ituff_tnames(OPT.ituff)

        flatreset = re.compile('^%s' % OPT.flatreset)
        print('mod,resetplb,patlist_name,testinstance_name')
        if tname_set:
            kwargs = dict(bypass=True, keyparam='patlist', edict=True)
        else:
            kwargs = dict(passonly=True, bypass=True, keyparam='patlist', edict=True)
        for mod, tname, ed in tp.mtpl.iter_flows('MAIN', **kwargs):
            # print(f'{mod} {tname}')
            res = tp.plists.get_flat(remove_ip(ed['patlist']), stopat=flatreset)
            for item in res:
                if flatreset.search(item):
                    if tname_set and (mod, tname) not in tname_set:
                        continue
                    print('%s,%s,%s,%s' % (mod, item, remove_ip(ed['patlist']), tname))

    def do_flowpass(self):
        """Display flow passonly"""
        self.do_flowall(input_passonly=OPT.flowpass)

    def do_flowall(self, input_passonly=None):
        """Display flow all"""
        tp = TestProgram(OPT.all[0], stpl=OPT.stpl, location=OPT.loc, vars=OPT.vars).pickle_init()
        tname_set = tp.mtpl.ituff_tnames(OPT.ituff)
        pfdata = tp.mtpl.dict_flows()

        if input_passonly:
            passonly = True
            keyparam = None if input_passonly == 'ALL' else input_passonly
        else:
            passonly = False
            keyparam = None if OPT.flowall == 'ALL' else OPT.flowall

        cnt = 0
        mapping = {'P': 'PassFlow',
                   'F': 'FailFlow',
                   'B': 'Bypassed'}
        kwargs = dict(passonly=passonly, bypass=passonly, keyparam=keyparam, traceinfo=True, edict=True)
        for mod, tname, edict, trc in tp.mtpl.iter_flows('MAIN', **kwargs):
            if tname_set and (mod, tname) not in tname_set:
                continue
            pf = mapping[pfdata[(mod, tname)]]
            if OPT.param:
                for pp in OPT.param:
                    if pp in edict:
                        print(f'{mod} {pf} {tname} {edict[pp]}')
            else:
                print('%4d. %s %-18s %s Trace: %s' % (cnt, pf, mod, tname, trc))
                cnt += 1

    def do_patlist(self):
        """Display flow all, module, patlist, pattern"""
        tp = TestProgram(OPT.all[0], stpl=OPT.stpl, location=OPT.loc, vars=OPT.vars).pickle_init()
        allset = set()
        kwargs = dict(bypass=True, keyparam='patlist', edict=True)
        for mod, tname, ed in tp.mtpl.iter_flows('MAIN', **kwargs):
            allset.add((mod, ed['patlist']))   # So that mod+patlist is unique
        for mod, patlist in sorted(allset):
            for pat in tp.plists.get_pats_from_plb(patlist):
                print(f'{mod} {patlist} {pat}')


class TimCheck:

    def __init__(self, tpobj, timnames, input_refpin):
        """
        Checks Timings with regards to pins:
           1. Duplicate pin assignment
           2. Missing pin (based on Domain name)
           3. Incorrect pin assignment
           4. Pin not defined in pattern domain

        :param tpobj: testprogram object
        :param timnames: regex tim names (OPT.tim_pin)
        :param domains: list of domains (optional) (OPT.grp)
        """
        self.tpobj = tpobj
        self.timnames = timnames
        self.input_refpin = input_refpin

        self.tpobj.pin.set_data()
        self.all_timings = self.tpobj.timing.get_timings()    # set of timings names

        # Option: Display all timing names
        if self.timnames == 'DISP':
            for name in sorted(self.all_timings):
                print(name)
            exit(0)

        # all pins in domains
        self.allpins = tpobj.pin.get_pin2domain()   # {pin_without_ip: set_of_domain}

        # Get reference pinlist from OPT.grp, if specified
        self.refpin_optgrp = {}
        alldom = set()
        alldom.update(*self.allpins.values())
        validdom = indent(3, sorted(alldom))    # valid domain list
        for domain in self.input_refpin:
            toadd = {pin: domain for pin in self.allpins if domain in self.allpins[pin]}
            assert toadd, (f'[-grp {domain}] does not have any pin. Is this a valid group/domain? '
                           f'List of valid domains: \n{validdom}')
            self.refpin_optgrp.update(toadd)

    def main(self):
        """Start the tim checks"""

        # Iterate on matching timing names
        targetlist = [name for name in sorted(self.all_timings) if re.search(self.timnames, name)]
        assert targetlist, f'{self.timnames} does not match any timing name. Run [-tim_pin DISP] to display valid.'
        for name in targetlist:
            print()
            print(f"Processing {name} ...")
            tim_grps = self.tpobj.timing.get_pingrps(name)     # {pingrp: domain}

            # get refpins to use. This are the pins that should exist in timings.
            if self.input_refpin:
                refpin = self.refpin_optgrp
            else:
                refpin = {}     # {pin: domain}
                for domain in set(tim_grps.values()):
                    toadd = {pin: domain for pin in self.allpins if domain in self.allpins[pin]}
                    assert toadd, f'{name}: [{domain}] does not have any pin. Is this a valid domain?'
                    refpin.update(toadd)

            errors = self._tim_check(name, tim_grps, refpin)

            if not errors:
                print(f"Clean:     {name}")

    def _tim_check(self, name, tim_grps, refpin):
        """Do the checks given one timing"""
        errors = 0

        # Show duplicated assignments
        found = {}    # {pin: timing_group_name}
        for grp in tim_grps:
            for pin in self.tpobj.pin.flatten(grp, strip_ip=True):
                if pin in found:
                    print(f'-e- {name} has {pin} defined twice. In {grp} and in {found[pin]}')
                    errors += 1
                found[pin] = grp

        # Show unassigned pins
        for pin in refpin:
            if pin not in found:
                print(f'-e- {name} does not have {pin} defined. Domain for this pin: {refpin[pin]}')
                errors += 1

        # Show pins in wrong domain
        for grp in tim_grps:
            for pin in self.tpobj.pin.flatten(grp, strip_ip=True):

                if pin not in self.allpins:
                    print(f'-e- {pin} in {grp} is not defined in any pattern domain.')
                    errors += 1
                    continue

                dom_list = self.allpins[pin]
                if tim_grps[grp] not in dom_list:
                    print(f'-e- {name} has domain mismatch for {pin}: '
                          f'{cjoin(dom_list)} (domain) vs {tim_grps[grp]} (timing)')
                    errors += 1

        return errors


class ContentSummary:

    def compare(self, tp1, tp2):
        """
        Do a full compare of tpsort, tp1 and tp2
        Idea: tpsort is the reference

        :param tpsort: reference testprogram path
        :param tp1: testprogram path previous TP
        :param tp2: testprogram path current TP
        :return:
        """
        datasort = {}
        for idx, tpsort in enumerate(OPT.content):
            self._merge(datasort, self.process(tpsort, "R"), idx)
        datatp1 = self.process(tp1, "A")
        datatp2 = self.process(tp2, "B")
        result = self.display(datasort, datatp1, datatp2)
        self.write_csv(result)

    def _merge(self, dd1, dd2, idx):
        """Merge dd2 into dd1. If there are duplicate entries, then add number"""
        for key in dd2:
            if key in dd1:
                dd1[f'{key}-{idx}'] = dd2[key]
            else:
                dd1[key] = dd2[key]

    def process(self, tp, which):
        """
        Process one testprogram and return the total

        :param tp: testprogram path
        :param which: R, A or B
        :return: {module: (kill_tid_count, edc_tid_count)}
        """
        tp = TestProgram(tp).pickle_init()
        print(f'{which}: {tp.get_name()}')
        tdb = TidDb(tp)
        dctr = tdb.summary_mod_tid()
        # 1:{'COR': 'min', 'EKL': 'EDC', 'FRQ': '0800', 'MOD': 'ARR_ATOM_CXX'}
        # 0:{set_of_tid}

        edc_kill = {}    # <module>: {'EDC'|'KIL': set}
        for item in dctr:
            ekl = dctr[item][1]['EKL']   # EDC or KIL
            mod = dctr[item][1]['MOD']
            if mod not in edc_kill:
                edc_kill[mod] = {'EDC': set(),
                                 'KIL': set()}
            edc_kill[mod][ekl].update(dctr[item][0])

        # generate final dictionary
        result = {}     # {module: (edc_tid_count, kill_tid_count)}
        for mod in edc_kill:
            result[mod] = (len(edc_kill[mod]["KIL"]), len(edc_kill[mod]["EDC"] - edc_kill[mod]["KIL"]))
        return result

    def display(self, datasort, datatp1, datatp2):
        """
        Display in screen and output in csv

        :param datasort: reference tp
        :param datatp1: previous tp
        :param datatp2: current TP
        :return:
        """
        allmods = datasort.keys() | datatp1.keys() | datatp2.keys()
        pa = PrintAlign(header=True, rjust=False, space=1, sep='|')
        csv = [["Module", "R-Total", "R-KILL", "R-EDC", "A-Total", "A-KILL", "A-EDC", "B-Total", "B-KILL", "B-EDC"]]
        pa(*csv[0])
        for mod in sorted(allmods):
            cols = ['', '', '', '', '', '', '', '', '']
            if mod in datasort:
                cols[0] = datasort[mod][0] + datasort[mod][1]
                cols[1] = datasort[mod][0]
                cols[2] = datasort[mod][1]
            if mod in datatp1:
                cols[3] = datatp1[mod][0] + datatp1[mod][1]
                cols[4] = datatp1[mod][0]
                cols[5] = datatp1[mod][1]
            if mod in datatp2:
                cols[6] = datatp2[mod][0] + datatp2[mod][1]
                cols[7] = datatp2[mod][0]
                cols[8] = datatp2[mod][1]
            pa(mod, *cols)
            csv.append([mod] + cols)
        pa.disp()
        return csv

    def write_csv(self, final):
        """Write to csv file"""
        if not OPT.out:
            print('-i- Specify -out <outfile.csv> to write .csv')
            return 1

        with open(OPT.out, 'w', newline='') as fh:
            csv_fh = csv_module.writer(fh, dialect='excel')
            for row in final:
                csv_fh.writerow(row)


if __name__ == '__main__':  # pragma: no cover
    TPInfo(desc=__doc__).main()
