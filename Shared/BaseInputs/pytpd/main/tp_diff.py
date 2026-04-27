#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Full featured TP differ

Usage:
CMD> tp_diff.py <path_tpold>/EnvironmentFile.env <path_tpnew>/EnvironmentFile.env
CMD> tp_diff.py <path_tpold>/EnvironmentFile.env <path_tpnew>/EnvironmentFile.env -stpl1 file.stpl [-stpl2 file.stpl]

Note: If module is missing, then it will show in #1 Tid summary diff and #4 plb and tuple diff
"""
import setenv      # must be first in the imports
from gadget.vepargs import Args, TA_All, TA_StoreTrue, TA_StoreFile, TA_StoreDir, TA_StoreNumber
from gadget.vepargs import TA_AppendSC, TA_Store, TA_KeyVal_CaseSensitive
from gadget.errors import ErrorUser, ErrorCockpit
from gadget.helperclass import OPT, Flow, IS_UT
from gadget.dictmore import DictDot, iter_levels, key_exist
from gadget.files import File, TempDir
from gadget.shell import vmsize, SystemCall
from gadget.gizmo import Elapsed
from gadget.strmore import indent, space2comma, sample_list
from gadget.pylog import log
from gadget.tputil import time_disp, SDiff, tuple_tid, tid_from_pat, pat_section_diff
from gadget.tputil import log_usage, get_param, OtplFile
from gadget.disk import listdir_noerror
from gadget.printmore import Dumper
from tp.testprogram import TestProgram
from mod.tiddb import TidDb
from mod.setting import cfg
from collections import defaultdict
from os.path import exists, abspath, dirname, join, basename, isdir
import os
import glob
import re
import pickle


class TPDiff(Args):   # parent: ArgsBase
    """
    TP differ
    """

    def config(self):
        """
        Define the arguments for the script.
        The order below will matter, it is the order of display during help.
        """
        cnfg = DictDot()
        cnfg.all = TA_All('First and 2nd arg are TP env file to compare')
        cnfg.stpl1 = TA_StoreFile('Specify stpl file for first TP', metavar='file.stpl')
        cnfg.stpl2 = TA_StoreFile('Specify stpl file for second TP', metavar='file.stpl')
        cnfg.loc1 = TA_Store('Specify location for first TP', metavar='CLASSHOT')
        cnfg.loc2 = TA_Store('Specify location for second TP', metavar='CLASSHOT')
        cnfg.var1 = TA_KeyVal_CaseSensitive('Specify Vars for first TP', metavar='SCVars.SC_REV=E')
        cnfg.var2 = TA_KeyVal_CaseSensitive('Specify Vars for second TP', metavar='SCVars.SC_REV=E')
        cnfg.out = TA_StoreDir('Specify output dir for .csv files', metavar='outdir')
        cnfg.nopickle = TA_StoreTrue('Do not use / create pickle cache file')
        cnfg.only = TA_AppendSC('Specify which diff items to run only', metavar='flowitem')
        cnfg.skip = TA_AppendSC('Specify which diff items to skip', metavar='flowitem')
        cnfg.add = TA_AppendSC('Specify which diff items to add (skip by default)', metavar='flowitem')
        cnfg.module = TA_Store('Specify which modules to report. Regex string', metavar='modname')
        cnfg.detail = TA_StoreTrue('Display detail of tid, plb, patreorder diff')
        cnfg.flows = TA_StoreTrue('Help: Display all the flowitem')
        cnfg.auto = TA_StoreTrue('(UNUSED) Auto testinstance pair based on most TID match')
        cnfg.inspect = TA_StoreTrue('(UNUSED) Display testinstance pair settings')
        cnfg.sdiff = TA_StoreTrue('CMD: Execute generic sdiff given two files')
        cnfg.otpl = TA_Store('CMD: Execute generic sdiff given two otpl files', metavar='sdiff|<tool>')
        cnfg.s = TA_StoreTrue('Show only differences, used with -sdiff')
        cnfg.W = TA_StoreNumber('Specify column length for -sdiff', default=60, metavar=60)
        cnfg.value = TA_StoreTrue('Show value instead of equation for -tim or -lvl')
        cnfg.tim = TA_AppendSC('CMD: Do timing diff. [-s, -W, -value]', metavar='tc1[,tc2]')
        cnfg.lvl = TA_AppendSC('CMD: Do level diff. [-s, -W, -value]', metavar='tc1[,tc2]')

        return cnfg

    def main(self):
        """
        Main entry point of executable
        -h will not reach this method, since that is taken cared of in Args Base class
        """
        # independent options
        log_usage('tp_diff', cfg)
        self.do_otpl()
        self.do_sdiff()
        self.do_timlvl()

        # Do opt checks
        in_arg = self.check_opt_all()

        # tp diff
        diff = Diff(in_arg)

        flow = Flow(only=OPT.only, skip=OPT.skip, add=OPT.add)
        flow.append(diff.tid_diff, '1 TID Summary diff')
        flow.append(diff.usrv_diff, '2 USRV diff')
        flow.append(diff.ins_diff, '3 Testinstance name,corner,freq,edckill diff')
        flow.append(diff.plb_diff, '4 plb and tuple diff')
        flow.append(diff.patreorder_diff, '5a TID reorder per plb')
        flow.append(diff.fullpat_diff, '5b Full Patname same tuple diff')
        flow.append(diff.ins_detail, '6a Testinstance detail diff')
        flow.append(diff.basenumber_diff, '6b Basenumber diff')
        flow.append(diff.tim_diff, '7a Timing value diff')
        flow.append(diff.lvl_diff, '7b Levels value diff')
        flow.append(diff.ctrbin_diff, '8a Counter&Softbin changes (add&del not shown)')
        flow.append(diff.passfail_diff, '8b port property diff')
        flow.append(diff.allports_diff, '8c INIT flow diff', args=('INIT',))
        flow.append(diff.port_diff, '8d port connection diff')
        flow.append(diff.tp_files_top, '9a TOP-LEVEL Files diff')
        flow.append(diff.tp_files_mod, '9b Module InputFiles diff')

        # Optional flows
        flow.append(diff.allports_diff, 's1 all-ports/flow diff', skip=True,
                    args=('MAIN,INIT',))

        flow.disp_flows(OPT.flows)    # -flows: help: Display flows
        self.disp_options()           # Display options
        diff.intro()                  # Display which testprogram
        flow.run()                    # execute the flows

        log.info('')
        log.info('-i- End of diff')

    def disp_options(self):
        """Display options"""
        once = True
        for item in 'only skip add module'.split():
            if item in OPT and OPT[item]:
                if once:
                    log.info('')
                    once = False
                if isinstance(OPT[item], list):
                    log.info('Option: -%s %s' % (item, ','.join(OPT[item])))
                else:
                    log.info('Option: -%s %r' % (item, OPT[item]))

    def check_opt_all(self):
        """Check if opt is good"""
        if OPT.flows:
            return []    # empty string, do not instantiate a TP

        if not OPT.all or len(OPT.all) <= 1:
            log.info("Error: First and 2nd argument must be testprogram env file.")
            log.info("Usage: tp_diff.py  <path_tp1>/EnvironmentFile.env <path_tp2>/EnvironmentFile.env")
            log.info("Execute 'tp_diff.py -h' for more info.")
            log.info('')
            exit(0)

        return None    # default run

    def do_otpl(self):
        """do -otpl, independent command run"""
        if not OPT.otpl:
            return   # Do nothing

        self.check_opt_all()

        a0 = [x for _, x in OtplFile(OPT.all[0]).readline()]
        a1 = [x for _, x in OtplFile(OPT.all[1]).readline()]

        with TempDir(chdir=True):
            File('a0').touch('\n'.join(a0))
            File('a1').touch('\n'.join(a1))
            _, out = SystemCall(f'{OPT.otpl} a0 a1').run_outtxt()
            print(out)

        exit(0)

    def do_sdiff(self):
        """do -sdiff, independent command run"""
        if not OPT.sdiff:
            return   # Do nothing

        self.check_opt_all()

        with open(OPT.all[0]) as fh:
            a0 = fh.read().split('\n')
        with open(OPT.all[1]) as fh:
            a1 = fh.read().split('\n')

        SDiff().simple(a0, a1, col=OPT.W, diffonly=OPT.s)
        exit(0)

    def do_timlvl(self):
        """Do timing diff given testcondition"""
        if not (OPT.tim or OPT.lvl):
            return

        diff = Diff(self.check_opt_all())
        diff.tc_tim_diff(tim=OPT.tim, lvl=OPT.lvl,
                         is_diffonly=OPT.s, is_value=OPT.value, col=OPT.W)
        exit(0)


class Diff:
    """TP Diff class"""

    def __init__(self, tp):
        """
        tp input is:
        1. None: use OPT.all; main routine
        2. []: for non-testprogram unittests
        3. [tpobj1, tpobj2]: for testprogram unittests
        """

        # process all OPT.<something> here. There should be no OPT.<something> outside of init
        self.out = OPT.out     # Output directory
        self.robj_mod = None
        self.is_detail = OPT.detail
        if OPT.module:
            self.robj_mod = re.compile(r"^\s*(%s)" % OPT.module)

        # assign tp object
        if tp is None:
            self.tp = self.load_tp(OPT.all[0], OPT.all[1],
                                   nopickle=OPT.nopickle,
                                   stpl1=OPT.stpl1,
                                   stpl2=OPT.stpl2,
                                   loc1=OPT.loc1,
                                   loc2=OPT.loc2,
                                   var1=OPT.var1,
                                   var2=OPT.var2)
        elif tp:
            self.tp = tp
            self.tp[0].init()
            self.tp[1].init()
        else:
            self.tp = []

        # other variables
        self.change_legend_print = True

    def load_tp(self, tp0, tp1, nopickle, stpl1, stpl2, loc1, loc2, var1, var2):
        """Create the tp object"""
        sw = Elapsed()

        if nopickle:
            tp = [TestProgram(tp0, stpl=stpl1, location=loc1, vars=var1).init(),
                  TestProgram(tp1, stpl=stpl2, location=loc2, vars=var2).init()]
        else:
            tp = [TestProgram(tp0, stpl=stpl1, location=loc1, vars=var1).pickle_init(),
                  TestProgram(tp1, stpl=stpl2, location=loc2, vars=var2).pickle_init()]

        log.info(f'-i- Total Elapsed for two inits: {sw}')
        return tp

    def intro(self):
        """Writes the header/intro"""
        tp = [self.tp[0], self.tp[1]]    # shortcut
        stpl = [basename(tp[0].get_stpl()), basename(tp[1].get_stpl())]
        loc = [tp[0].locset.location, tp[1].locset.location]

        log.info('')
        log.info(f"Left TP: {tp[0].get_name()}, {tp[0].envfile}, {stpl[0]}, {loc[0]}")
        log.info(f"Rght TP: {tp[1].get_name()}, {tp[1].envfile}, {stpl[1]}, {loc[1]}")
        log.info('')

    def tim_diff(self):
        """Timing diff given two tp"""
        result = [defaultdict(dict), defaultdict(dict)]
        for nn in (0, 1):
            for tc in self.tp[nn].timing.iter_tc():
                if self.is_skip_module(tc):
                    continue
                for param, value in self.tp[nn].timing.iter_params(tc, isvalue=True):
                    result[nn][tc][param] = value

        # get mapping of timings to testinstance
        ref = [defaultdict(set), defaultdict(set)]
        for nn in (0, 1):
            kwargs = dict(passonly=False, bypass=False, keyparam='patlist', edict=True)
            for md, tn, data in self.tp[nn].mtpl.iter_flows_multi('MAIN,INIT', **kwargs):
                ref[nn][get_param(data, 'timing', 'NA')].add(f'{md}  {tn}')

        self.twolevel_diff(result, ref)

    def lvl_diff(self):
        """Level diff given two tp"""
        result = [defaultdict(dict), defaultdict(dict)]
        for nn in (0, 1):
            for tc in self.tp[nn].levels.iter_tc():
                if self.is_skip_module(tc):
                    continue
                for param, value in self.tp[nn].levels.iter_params(tc, isvalue=True):
                    result[nn][tc][param] = value

        # get mapping of timings to testinstance
        ref = [defaultdict(set), defaultdict(set)]
        for nn in (0, 1):
            kwargs = dict(passonly=False, bypass=False, keyparam='patlist', edict=True)
            for md, tn, data in self.tp[nn].mtpl.iter_flows_multi('MAIN,INIT', **kwargs):
                ref[nn][get_param(data, 'level', 'NA')].add(f'{md}  {tn}')

        self.twolevel_diff(result, ref)

    def usrv_diff(self):
        """USRV diff given two tp"""
        SDiff().keyval(self.dict_skip_module(self.tp[0].usrv.get_usrv_map()),
                       self.dict_skip_module(self.tp[1].usrv.get_usrv_map()),
                       col=80, diffonly=True, sep=' = ', nc=True)

    def patreorder_diff(self):
        """tid reorder diff in plb"""
        # initialize
        mapmod = [self.tp[0].plists.get_modname_map(), self.tp[1].plists.get_modname_map()]
        raw = [defaultdict(dict), defaultdict(dict)]
        for nn in (0, 1):
            for plb in self.tp[nn].plists.get_plb_map():   # all loaded plb
                md = mapmod[nn].get(plb, ('', None))[0]    # md is empty when plb is unused by testinstance
                if self.is_skip_module(md):
                    continue
                pats = self.tp[nn].plists.get_pats_from_plb(plb, order=True)
                raw[nn][md][plb] = [tid_from_pat(x) for x in pats]      # just get tid number

        # Display
        is_changed = False
        for md, plb in iter_levels(raw[1], 2):
            if md and plb in raw[0][md]:
                rlist = SDiff().is_reorder(raw[0][md][plb], raw[1][md][plb])
                if rlist:
                    is_changed = True
                    tot = len(raw[1][md][plb])
                    log.info('Reordered: %-20s %s, reordered=%s of %s: %s'
                             '' % (md, plb, len(rlist), tot, sample_list(rlist, 4)))
                    if self.is_detail:
                        SDiff().is_reorder(raw[0][md][plb], raw[1][md][plb], disp=True)
                        log.info('')

        if not is_changed:
            log.info('No change')

    def fullpat_diff(self):
        """full patternname diff per plb"""
        # initialize
        mapmod = [self.tp[0].plists.get_modname_map(), self.tp[1].plists.get_modname_map()]
        raw = [defaultdict(dict), defaultdict(dict)]
        for nn in (0, 1):
            for plb in self.tp[nn].plists.get_plb_map():   # all loaded plb
                md = mapmod[nn].get(plb, ('', None))[0]    # md is empty when plb is unused by testinstance
                if self.is_skip_module(md):
                    continue
                pats = self.tp[nn].plists.get_pats_from_plb(plb)
                raw[nn][md][plb] = {tuple_tid(pat)[0]: pat for pat in pats}    # full patternname

        # Process
        out_lines = defaultdict(list)
        out_cnt = defaultdict(int)
        for md, plb in sorted(iter_levels(raw[1], 2)):
            if md and plb in raw[0][md] and raw[0][md][plb] != raw[1][md][plb]:
                key = f'{md} {plb}'
                for tup in sorted(raw[1][md][plb]):   # use 2nd tp as reference!
                    if tup.isdigit():
                        out_cnt[key] += 1
                        if tup in raw[0][md][plb] and raw[0][md][plb][tup] != raw[1][md][plb][tup]:
                            sd, _ = pat_section_diff(raw[0][md][plb][tup], raw[1][md][plb][tup])
                            out_lines[key].append(f'   {sd} vs {raw[1][md][plb][tup]}')

        # print it
        for key in out_lines:
            log.info('')
            log.info(f'{key}, {len(out_lines[key])} of {out_cnt[key]}:')
            for line in out_lines[key]:
                log.info(line)

        if not out_lines:
            log.info('No change')

    def plb_diff(self):
        """plb and tuple diff given two tp"""
        # initialize
        mapmod = [self.tp[0].plists.get_modname_map(), self.tp[1].plists.get_modname_map()]
        raw = [defaultdict(dict), defaultdict(dict)]      # <plb>: {tid: tuple}
        for nn in (0, 1):
            for plb in self.tp[nn].plists.get_plb_map():
                md = mapmod[nn].get(plb, ('', None))[0]
                if self.is_skip_module(md):
                    continue
                pats = self.tp[nn].plists.get_pats_from_plb(plb)
                raw[nn][md][plb] = {y: x for x, y in map(tuple_tid, pats) if x.isdigit()}

        # Display
        is_changed = False
        is_header = True
        template = '%-25s %-20s %s'
        for md, plb in iter_levels(raw[0], 2):
            if plb in raw[1][md]:
                if md and raw[0][md][plb] != raw[1][md][plb]:
                    is_changed = True
                    _, a2, _ = SDiff().keyval(raw[0][md][plb], raw[1][md][plb], disp=False)
                    if is_header:
                        is_header = False
                        log.info('')
                        log.info(template % ('TID count, +add/-del/chng', 'Module', 'patlist'))
                        log.info(template % ('-------------------------', '------', '-------'))
                    text = 'Total: %4d, %s' % (len(a2), SDiff.count_diff(a2))
                    log.info(template % (text, md, plb))
                    if self.is_detail:
                        SDiff().keyval(raw[0][md][plb], raw[1][md][plb], sep=' tid = tuple ', indent=3, diffonly=True)

        for md, plb in iter_levels(raw[0], 2):
            if md and plb not in raw[1][md]:
                is_changed = True
                log.info(template % ('Removed', md, plb))

        for md, plb in iter_levels(raw[1], 2):
            if md and plb not in raw[0][md]:
                is_changed = True
                log.info(template % ('Added', md, plb))

        if not is_changed:
            log.info('No change')

    def tid_diff(self):
        """TID diff given two tp"""
        # initialize
        tdb = [None, None]     # TidDb
        dctr = [None, None]    # final dictionary
        for nn in (0, 1):
            tdb[nn] = TidDb(self.tp[nn])
            raw = tdb[nn].summary_mod_tid()
            dctr[nn] = self.dict_skip_module({k: raw[k][0] for k in raw})

        if self.is_detail:
            log.info("Detail:")
            d1, d2 = SDiff.set2key({f'{k} tid': v for k, v in dctr[0].items()},
                                   {f'{k} tid': v for k, v in dctr[1].items()},
                                   aligned=True)
            SDiff().keyval(d1, d2,
                           indent=3, col=60, diffonly=True, nc=True, sep=' = ')
            log.info('')
            log.info('Summary:')

        c1, c2, c3 = SDiff().keyval({k: len(v) for k, v in dctr[0].items()},
                                    {k: len(v) for k, v in dctr[1].items()},
                                    indent=0, col=60, diffonly=True, nc=True, sep=' tids = ')

        # report summary .csv
        if self.out:
            with open(join(self.out, 'tid_diff.csv'), 'w') as fh:
                text = 'Module,corner,freq,edckill,tid_count,diff,Module,corner,freq,edckill,tid_count'
                fh.write(f'{text}\n')   # header
                expect = len(text.split(','))
                for r1, r2, r3 in zip(c1, c2, c3):
                    r1 = '%s %s' % (r1, len(dctr[0][r1])) if r1 else r1
                    r3 = '%s %s' % (r3, len(dctr[1][r3])) if r3 else r3
                    text = '%s,%s,%s' % (space2comma(r1, 5), r2, space2comma(r3, 5))
                    fh.write(f'{text}\n')
                    tokens = len(text.split(','))
                    assert expect == tokens, f'Error expect column count={expect} but got {tokens} instead'

                # Write the detail tid
                for nn in (0, 1):
                    tdb[nn].dump(join(self.out, f'{self.tp[nn].get_name()}.tid.csv'))

    def ctrbin_diff(self):
        """Flow diff given two tp"""
        result = [defaultdict(dict), defaultdict(dict)]
        for nn in (0, 1):
            kwargs = dict(passonly=False, bypass=True, flownames=True, pdict=True, r_mod=self.robj_mod)
            for md, dutflow, dutitem, ports in self.tp[nn].mtpl.iter_flows_multi('MAIN,INIT', **kwargs):
                key = f'{dutflow} {dutitem}'
                result[nn][md][key] = self.port2dict(ports)

        # Changed
        changed = defaultdict(list)
        for md, key in iter_levels(result[0], 2):
            if not key_exist(result[1], md, key):
                continue

            lines = []
            for item in result[0][md][key]:
                if not ('IncrementCounters' in item or 'SetBin' in item):
                    continue   # only above items

                if item in result[1][md][key] and result[0][md][key][item] != result[1][md][key][item]:
                    lines.append('   %s = %s vs %s' % (item, result[0][md][key][item], result[1][md][key][item]))
            if lines:
                dutflow, dutitem = key.split()
                changed[tuple(lines)].append(f'Changed {md} {dutflow} {dutitem}:')

        for lines in sorted(changed, key=lambda x: changed[x][0]):
            for item in sorted(set(changed[lines])):
                print(item)
            for line in lines:
                print(line)

        if not changed:
            log.info('No change')

    def port_diff(self):
        """Flow diff given two tp"""
        self._port_diff_real('connection')

    def _port_diff_real(self, portitem):
        """Perform port diff given portitem"""

        result = [defaultdict(dict), defaultdict(dict)]
        for nn in (0, 1):
            kwargs = dict(passonly=False, bypass=True, flownames=True, pdict=True, r_mod=self.robj_mod)
            for md, dutflow, dutitem, ports in self.tp[nn].mtpl.iter_flows_multi('MAIN,INIT', **kwargs):
                key = f'{dutflow} {dutitem}'
                port_dict = self.port2dict(ports).items()
                result[nn][md][key] = {x: y for x, y in port_dict if portitem in x}

        # Changed
        changed = False
        for md, key in iter_levels(result[0], 2):
            if not key_exist(result[1], md, key):
                continue

            if result[0][md][key] != result[1][md][key]:
                changed = True
                log.info(f'Changed {md} {key}:')
                d1 = self.uniqport_dict(result[0][md][key], result[1][md][key])
                d2 = self.uniqport_dict(result[1][md][key], result[0][md][key])
                SDiff().keyval(d1, d2, diffonly=True, col=0, indent=3)

        if not changed:
            log.info('No change')

    def passfail_diff(self):
        """Flow diff given two tp"""
        self._port_diff_real('PassFail')

    def allports_diff(self, which):
        """
        all ports/Flow diff given flow
        Note: On MAIN, this is optional since details are already in ctrbin_diff, port_diff and passfail_diff
        This is called for INIT.
        """
        result = [defaultdict(dict), defaultdict(dict)]
        for nn in (0, 1):
            kwargs = dict(passonly=False, bypass=True, flownames=True, pdict=True, r_mod=self.robj_mod)
            for md, dutflow, dutitem, ports in self.tp[nn].mtpl.iter_flows_multi(which, **kwargs):
                key = f'{dutflow} {dutitem}'
                result[nn][md][key] = self.port2dict(ports)

        # Changed
        is_changed = False
        for md, key in iter_levels(result[0], 2):
            if key_exist(result[1], md, key) and result[0][md][key] != result[1][md][key]:
                is_changed = True
                log.info(f'Changed {md} {key}')
                SDiff().keyval(result[0][md][key], result[1][md][key], indent=3, col=0, diffonly=True)

        # Removed
        for md, key in iter_levels(result[0], 2):
            if md in result[1] and key not in result[1][md]:
                is_changed = True
                log.info(f'Removed {md} {key}')

        # Added
        for md, key in iter_levels(result[1], 2):
            if md in result[0] and key not in result[0][md]:
                is_changed = True
                log.info(f'Added   {md} {key}')

        if not is_changed:
            log.info('No change')

    def ins_diff(self):
        """Instance diff given two tp: passflow and with patlist"""

        # read the testprograms
        idata = [defaultdict(dict), defaultdict(dict)]
        for nn in (0, 1):
            kwargs = dict(passonly=True, bypass=True, keyparam='patlist', edict=True, r_mod=self.robj_mod)
            for md, tn, data in self.tp[nn].mtpl.iter_flows_multi('MAIN,INIT', **kwargs):
                key = self.strip_tn(tn, data['_FREQ'])
                if key not in idata[nn][md]:
                    idata[nn][md][key] = set()
                idata[nn][md][key].add("%s %s %-5s" % (data['_EDCKIL'], data['_CORNER'], data['_FREQ']))

        # convert all sets to dict items
        for md in sorted(idata[0]):
            if md in idata[1]:
                idata[0][md], idata[1][md] = SDiff.set2key(idata[0][md], idata[1][md])

        # make key fixed length
        ndata = [defaultdict(dict), defaultdict(dict)]
        for nn in (0, 1):
            for md in idata[nn]:
                for key, value in idata[nn][md].items():
                    ndata[nn][md][f'{key:60}'] = value
        idata = None   # so it's not accessible anymore

        # report it
        outlines = []
        text = 'Module,instance,edckil,corner,freq,diff,Module,instance,edckil,corner,freq'
        outlines.append(text)
        expect = len(text.split(','))

        diff_char = set()
        for md in sorted(ndata[0]):
            if md not in ndata[1]:
                log.info('')
                log.info(f'{md}: ==== NOT EXIST in 2nd TP')
                continue

            if ndata[0][md] != ndata[1][md]:
                log.info('')
                log.info(f"{md}: ======")

            c1, c2, c3 = SDiff().keyval(ndata[0][md], ndata[1][md], indent=3, col=80, diffonly=True)
            diff_char.update(c2)

            for r1, r2, r3 in zip(c1, c2, c3):
                r1 = '%s %s %s' % (md, r1, ndata[0][md][r1]) if r1 else r1
                r3 = '%s %s %s' % (md, r3, ndata[1][md][r3]) if r3 else r3

                text = '%s,%s,%s' % (space2comma(r1, 5), r2, space2comma(r3, 5))
                outlines.append(text)
                tokens = len(text.split(','))
                assert expect == tokens, f'Error expect column count={expect} but got {tokens} instead'

        if self.out:
            with open(join(self.out, 'ins_diff.csv'), 'w') as fh:
                # fh = open(join(self.out, 'ins_diff.csv'), 'w')
                fh.write('\n'.join(outlines))
                fh.write('\n')

        if diff_char == {' '} or (not diff_char):
            log.info('No change')

    def ins_detail(self):
        """Instance detail diff given two tp"""

        # read the testprograms
        idata = [defaultdict(dict), defaultdict(dict)]
        for nn in (0, 1):
            kwargs = dict(passonly=False, bypass=True, edict=True, r_mod=self.robj_mod)
            for md, tn, data in self.tp[nn].mtpl.iter_flows_multi('MAIN,INIT', **kwargs):
                idata[nn][md][tn] = self.filter_shared(data)

        diff_tn = defaultdict(list)
        for md in sorted(idata[0]):
            if md not in idata[1]:
                continue
            for key in idata[0][md]:
                if key not in idata[1][md]:
                    continue     # Display only same key

                if idata[0][md][key] != idata[1][md][key]:
                    a1, a2, a3 = SDiff().keyval(idata[0][md][key], idata[1][md][key], disp=False)

                    # make it row instead of column
                    diffdata = []
                    for c1, c2, c3 in zip(a1, a2, a3):
                        if c2 == '<':
                            diffdata.append(f'     {c1} = {idata[0][md][key][c1]}')
                            diffdata.append(f'   < (none)')
                        elif c2 == '>':
                            diffdata.append(f'     (none)')
                            diffdata.append(f'   > {c3} = {idata[1][md][key][c3]}')
                        elif c2 == ' ':
                            pass
                        else:
                            diffdata.append(f'     {c1} = {idata[0][md][key][c1]}')
                            diffdata.append(f'   {c2} {c3} = {idata[1][md][key][c3]}')
                    diff_tn[tuple(diffdata)].append(f'{md} {key}')

        # display it
        legend = True
        for item in sorted(diff_tn, key=lambda x: diff_tn[x][0]):
            if legend:
                log.info(f'1st line is TP1: {self.tp[0].get_name()}')
                log.info(f'2nd line is TP2: {self.tp[1].get_name()}')
                legend = False

            log.info('')
            for md_tn in sorted({self.strip_tn(x, None) for x in diff_tn[item]}):
                log.info(f'{md_tn}:')
            for line in item:
                log.info(line)

        if not diff_tn:
            log.info('No change')

    def basenumber_diff(self):
        """BaseNumber diff given two tp"""
        idata = [{}, {}]
        for nn in (0, 1):
            kwargs = dict(passonly=False, bypass=True, edict=True, r_mod=self.robj_mod)
            for md, tn, data in self.tp[nn].mtpl.iter_flows_multi('MAIN,INIT', **kwargs):
                idata[nn][f'{md} {tn}'] = data.get('base_number', '')

        # Show only those testinstance that exist in both
        fdata = [{}, {}]
        for item in idata[0]:
            if item in idata[1]:
                fdata[0][item] = idata[0][item]
                fdata[1][item] = idata[1][item]

        SDiff().keyval(fdata[0], fdata[1], nc=True, diffonly=True, sep=' = ')

    def tp_files_top(self):
        """Display Files diff - top level"""
        if self.robj_mod:
            return    # Do not show if specific module diffs

        self.change_legend_print = True
        tc = self.show_dir_diff(self.tp[0].tpldir, self.tp[1].tpldir, '', ign={'TPIE.Signature'})
        if not tc:
            log.info('No change')

    def tp_files_mod(self):
        """Display Files diff - mod level"""
        tc = []
        self.change_legend_print = True
        for md in self.tp[0].mtpl.get_modules():
            if self.is_skip_module(md):
                continue
            if not isdir(join(self.tp[1].moddir, md)):
                log.info(f'Module Missing: {md}')
                continue
            # tc.extend(self.show_dir_diff(join(self.tp[0].moddir, md),
            #                              join(self.tp[1].moddir, md),
            #                              f'{md}/'))
            tc.extend(self.show_dir_diff(join(self.tp[0].moddir, md, 'InputFiles'),
                                         join(self.tp[1].moddir, md, 'InputFiles'),
                                         f'{md}/InputFiles/'))
        if not tc:
            log.info('No change')

    def tc_tim_diff(self, tim, lvl, is_diffonly, is_value, col):
        """
        Diff two testconditions

        :param tim: 1 or 2 element testconditions for tim diff
        :param lvl: 1 or 2 element testconditions for lvl diff
        :param is_diffonly: If True, show diffonly
        :param is_value: If True, show evaluated values
        :param col: Column width
        """
        if tim:
            targ = [self.tp[0].timing, self.tp[1].timing]
            tclist = tim

        if lvl:
            targ = [self.tp[0].levels, self.tp[1].levels]
            tclist = lvl

        if len(tclist) == 1:
            tclist.append(tclist[0])

        # Display
        if is_value:
            foo = time_disp
        else:
            def foo(x):
                return x

        tc1 = ['%-30s %s' % (x, foo(y)) for x, y in targ[0].iter_params(tclist[0], isvalue=is_value)]
        tc2 = ['%-30s %s' % (x, foo(y)) for x, y in targ[1].iter_params(tclist[1], isvalue=is_value)]

        SDiff().simple(tc1, tc2, col=col, diffonly=is_diffonly, autowrap=True)
        print("-i- tim_diff [%s vs %s] Done." % (tclist[0], tclist[1]))

    def dict_skip_module(self, dd):
        """
        Returns a new dict filtered based on -module

        :param dd: input dictionary
        :return: dict
        """
        if not self.robj_mod:
            return dd    # Do nothing

        return {x: y for x, y in dd.items() if self.robj_mod.search(x)}

    def is_skip_module(self, md):
        """
        Returns True if this module is skipped, based on -module

        :param md: module name
        :return: True if flow is skipped
        """
        if not self.robj_mod:
            return False    # Do not skip

        return not self.robj_mod.search(md)

    def uniqport_dict(self, d1, d2, _robj=re.compile(r"Port#(\S+)")):
        """Try to uniquify port keys, for different values"""
        result = {}
        d1_cnt = defaultdict(set)
        for k, v in d1.items():
            d1_cnt[v].add(k)

        for k, v in d1.items():
            if k in d2 and d1[k] == d2[k]:
                result[k] = v
                continue
            if len(d1_cnt[v]) == 1:
                result[k] = v
                continue

            allp = [_robj.search(x).group(1) for x in sorted(d1_cnt[v]) if _robj.search(x)]
            new = _robj.sub('Port#%s' % ','.join(allp), k)
            result[new] = v
        return result

    def show_dir_diff(self, src, dest, md, ign=set()):
        """
        Display dir diff in a given directory

        :param src: source dir
        :param dest: dest dir
        :param md: module
        :param ign: set of ignore files
        :return: list of changed & missing files
        """
        if not isdir(src):
            return []   # Do nothing, e.g. <mod>/Inputfiles not exist

        missing = []
        changed = []
        added = []
        with TempDir(name=True) as tdir1, TempDir(name=True) as tdir2:
            for ff in sorted(os.listdir(src)):
                if ff in ign:
                    continue    # ignore these files
                if isdir(join(src, ff)):
                    continue    # ignore directories
                if ff.endswith(('.flw', '.onetoc2')):
                    continue    # These files are not worth showing

                if exists(join(dest, ff)):
                    if File(join(src, ff)).sha1() == File(join(dest, ff)).sha1():   # This makes it 3.5x faster
                        res = '+0/-0/0'   # no change since sha is the same
                    else:
                        Diff.smart_strip(join(src, ff), join(tdir1, ff))
                        Diff.smart_strip(join(dest, ff), join(tdir2, ff))
                        res = Diff.diff_arc(join(tdir1, ff), join(tdir2, ff))

                    if res != '+0/-0/0':
                        changed.append((res, f'{md}{ff}'))
                else:
                    missing.append(f'{md}{ff}')

            # Do added
            for ff in sorted(listdir_noerror(dest)):
                if ff in ign:
                    continue    # ignore these files
                if isdir(join(dest, ff)):
                    continue    # ignore directories
                if ff.endswith('.flw'):
                    continue    # These files are not worth showing
                if not exists(join(src, ff)):
                    added.append(f'{md}{ff}')

            # display changed
            template = '%s %-20s %s'
            for line in changed:
                if self.change_legend_print:
                    self.change_legend_print = False
                    log.info('Legend: (+add_lines/-removed_lines/changed_lines)')
                log.info(template % ('Changed', line[0], line[1]))
            for line in missing:
                log.info(template % ('Missing', '', line))
            for line in added:
                log.info(template % ('Added  ', '', line))
            return changed + missing + added

    @staticmethod
    def smart_strip(infile, outfile):
        """
        Smart strip - remove known lines so it does not show up in diff

        :param infile: input file
        :param outfile: output file
        """
        bname = basename(infile)
        pgmrule = ('iCGL_TpAltName', 'UFG_FREV_SPEC', 'UFG_OLF_FRV_COMPATIBLE')
        liport = ('<Suite>', '<BinMatrix>', '<FuseFileRelease>', '<CreatedBy>', '<CreatedDateTime>')
        with open(infile, 'rb') as fh, open(outfile, 'w') as fho:
            for line in fh.read().decode(errors='ignore').split('\n'):
                line = line.strip()
                if line.startswith('#'):
                    continue
                if bname.startswith('LIPORT_') and line.startswith(liport):
                    continue
                if bname == 'PGMRule_Base.txt' and line.startswith(pgmrule):
                    continue
                fho.write(f'{line}\n')

    @staticmethod
    def diff_arc(src, dest):
        """Return added/removed/changed in two files"""
        cmd = 'sdiff -s -t -w 40 --strip-trailing-cr'.split() + [src, dest]
        _, result = SystemCall(cmd).run_outtxt()
        # if basename(src) == 'LIPORT_Q24TXNAVAR.xml':
        #     log.info(result)
        changed = removed = added = 0
        for line in result.split('\n'):

            if not line:
                continue
            marker = line[19]
            if marker == '|':
                changed += 1
            elif marker == '<':
                removed += 1
            elif marker == '>':
                added += 1
            else:    # pragma: no cover - safety only
                raise ErrorCockpit(f'Unknown line[{line}] from sdiff output. marker=[{marker}]')

        return f'+{added}/-{removed}/{changed}'

    @staticmethod
    def strip_tn(tn, freq, robj=re.compile(r"^(.*)_\d+$")):
        """
        Strip Testname for each diff

        :param tn: Testname
        :param freq: freq (part of testname
        :return: Stripped testname
        """
        tn = robj.sub(r'\1_*', tn)
        if freq:
            tn = tn.replace(freq, '*')
        return tn

    @staticmethod
    def port_trace(trc, _robj=re.compile(r"port=(\S+)")):
        """Given trc array from iter_flows, return port numbers"""
        result = []
        for item in trc:
            res = _robj.search(item)
            if res:
                result.append(res.group(1))
            else:
                result.append('c')
        return ''.join(result)

    @staticmethod
    def port2dict(dd, _robj=re.compile(r"(\d\d\d\d+)")):
        """Convert port dictionary dd to a simple dictionary for sdiff"""
        result = {}
        for port in dd:
            if port == 999:
                result['Test'] = dd[port]
                continue

            for item in dd[port]:
                fitem = item
                fval = dd[port][item]

                if item in ('GoTo', 'Return'):
                    fval = f'{item} {dd[port][item]}'
                    fitem = 'connection'
                elif item in ('IncrementCounters', 'SetBin'):  # Get only the digit for these item
                    nval = _robj.search(dd[port][item])
                    if nval:
                        fval = nval.group(1)

                result[f'Port#{port} {fitem}'] = fval

        return result

    def twolevel_diff(self, result, ref):
        """
        Display two level diff of result dictionary

        structure:
        result[tp][testcondition][param] = value
        """
        some_changed = False
        for tc in sorted(result[0]):
            if tc not in result[1]:
                log.info(f'Removed: {tc}')
                self.disp_instances(ref[0], tc)
                some_changed = True
                continue
            if result[0][tc] != result[1][tc]:
                log.info(f'Changed: {tc}')
                self.disp_instances(ref[1], tc)
                some_changed = True
                SDiff().keyval(result[0][tc], result[1][tc],
                               col=60, diffonly=True, sep=' = ', indent=3)

        for tc in result[1]:
            if tc not in result[0]:
                log.info(f'Added:   {tc}')
                self.disp_instances(ref[1], tc)
                some_changed = True
                continue

        if not some_changed:
            log.info('No change')

    def disp_instances(self, ref, tc):
        """Display all testinstances"""
        for item in sorted(ref.get(tc, [])):
            log.info(f'  UseBy: {item}')

    @staticmethod
    def filter_shared(data,
                      timlvl=set('timings timing levels level'.split()),
                      robj=re.compile('_SHARED_[0-9A-F]+')):
        """removed shared since it's useless and don't include _EDCKIL"""
        result = {}
        for k, v in data.items():
            if k == '_EDCKIL':
                continue
            if k in timlvl:
                v = robj.sub('_SHARED_', v)
            result[k] = v
        return result


class PairModule:    # pragma: no cover
    """Pair at module level based on TID existence, for those that are not matching"""

    def __init__(self, tp1: TestProgram, tp2: TestProgram):
        self.tp = [tp1, tp2]
        self.map = defaultdict(set)           # {mod_tp1: set(mod_tp2)}   # 1:many
        self.uniq = [set(), set()]     # unique modules, no TID match
        self.tidtp = [defaultdict(set), defaultdict(set)]    # 0-tp1: {md: set(tid)}

        # read tid per module
        self.read_module_tid(self.tp[0], self.tidtp[0])
        self.read_module_tid(self.tp[1], self.tidtp[1])

        self.process()

        self.report()

    def process(self):
        """Process the module pairing"""

        # Do same module name pair
        found = set()     # found in tp2
        for md in self.tidtp[0]:
            if md in self.tidtp[1]:
                self.map[md].add(md)
                found.add(md)

        # Do pairing of uniq modules
        for md in self.tidtp[0]:
            if md in self.tidtp[1]:
                continue   # ignore existing
            for md2 in self.tidtp[1].keys() - found:
                common = self.tidtp[0][md] & self.tidtp[1][md2]
                if len(common):
                    # print(f'{md} vs {md2} {common}')
                    self.map[md].add(md2)
                    found.add(md2)

        self.uniq[1] = self.tidtp[1].keys() - found
        self.uniq[0] = self.tidtp[0].keys() - self.map.keys()

        # Debug =============================
        # print("Mapping which module maps to which module:")
        # for md in sorted(self.map):
        #     if {md} != self.map[md]:
        #         print("   %-15s: %r" % (md, self.map[md]))

    def report_uniq_mod(self, tpidx):
        """Print uniq modules for this tp"""
        if not self.uniq[tpidx]:
            return   # Nothing to print
        log.info(f"Unique modules for TP{tpidx+1}, with patlist:")
        log.info(indent(3, sorted(self.uniq[tpidx])))

    def report(self):
        """Display Report"""
        self.report_uniq_mod(0)
        self.report_uniq_mod(1)

        # Debug per module Tid
        log.info("Per-module-TID Stats:")
        for md in sorted(self.map):
            alltid = set()
            for md2 in self.map[md]:
                alltid.update(self.tidtp[1][md2])
            common = self.tidtp[0][md] & alltid
            uniq1 = self.tidtp[0][md] - alltid
            uniq2 = alltid - self.tidtp[0][md]
            log.info('   %-15s Total TP1: %5d, Common: %5d, Uniq TP1: %5d, Uniq TP2: %5d'
                     '' % (md, len(self.tidtp[0][md]), len(common), len(uniq1), len(uniq2)))

    def read_module_tid(self, tpobj, tidset, istestname=False):
        """Read all tid in a module and store in tidset"""
        for md, tn, dd in tpobj.mtpl.iter_flows(passonly=True, edict=True, keyparam='patlist'):
            try:
                result_tidset = tpobj.plists.get_tid_from_pats(tpobj.plists.get_pats_from_plb(dd['patlist']), istestname)
            except BaseException:
                continue     # temporary, remove this later when the iter_flows is bypass=True and all pass flows
            tidset[md].update(result_tidset)


class PairInstance:    # pragma: no cover
    """Smart pair of testinstances"""

    def __init__(self, tp1: TestProgram, tp2: TestProgram):
        self.tp = [tp1, tp2]
        self.map = {}                  # {(mod, tn): (mod, tn)}
        self.tidmap = [{}, {}]         # 0 - tp1: {(mod, tn): set of tid or testname}
        self.remaining = [None, None]  # 0 - tp1: {(mod, tn)}  - uniq instances
        self.mtdata = [{}, {}]         # 0 - tp1: {(mod, tn): {instance_dict}}

        # populate self.tidmap
        self.set_tid(self.tidmap[0], 0)
        self.set_tid(self.tidmap[1], 1)

        # stage1 pairing
        self.stage1()

        log.info(f"Common: {len(self.map)}")
        log.info(f"Uniq TP1: {len(self.remaining[0])}")
        log.info(f"Uniq TP2: {len(self.remaining[1])}")

        for item in sorted(self.remaining[0]):
            log.info(f'    TP1 uniq: {item}')
        for item in sorted(self.remaining[1]):
            log.info(f'    TP2 uniq: {item}')

    def set_tid(self, result: dict, idxtp: int, istestname=False) -> None:
        """
        Assign tid or testname into each testinstance (Populate self.tidmap)

        :param result: dict {(mod, tn): set of tid}
        :param idxtp: Which tp
        :param istestname: Set to True to use testname
        """
        tpobj = self.tp[idxtp]
        for md, tn, dd in tpobj.mtpl.iter_flows(passonly=True, edict=True, keyparam='patlist'):
            # for md, tn, dd, _ in tpobj.mtpl.iter_tests(key_name='patlist'):   # all testinstances with patlist
            patlist = dd['patlist']
            self.mtdata[idxtp][(md, tn)] = dd

            # TODO: temporary only, replace this with iter_flows() and remove this line
            if tpobj.mtpl.is_bypassed(md, tn, safe=False, dd=dd):
                continue

            # tid
            result[(md, tn)] = tpobj.plists.get_tid_from_pats(tpobj.plists.get_pats_from_plb(patlist), istestname)

    def stage1(self):
        """
        Main pairing algo. Populate self.map
        """
        # stage1: pair on same module and same name
        self.remaining[0] = self.get_remaining(0, 1)
        self.remaining[1] = self.get_remaining(1, 0)

        # stage2: with the module find common tid
        rem_tp2 = defaultdict(dict)    # {md: {tn: set_of_tid}}
        for md, tn in self.remaining[1]:
            rem_tp2[md][tn] = self.tidmap[1][(md, tn)]
        for md, tn in sorted(self.remaining[0]):
            subresult = {}
            if md in rem_tp2:
                settid1 = self.tidmap[0][(md, tn)]
                for tn2 in rem_tp2[md]:
                    cnt = settid1 & rem_tp2[md][tn2]
                    if cnt:
                        subresult[tn2] = len(cnt)

            if subresult:
                self.dispi()
                self.dispi(f"{md:18} TP1:{tn} cnt={len(settid1)} same module:")
                first = True
                for tn2 in sorted(subresult, key=lambda x: (subresult[x], x), reverse=True):
                    if first:
                        selected = ">>>"
                        first = False
                        if OPT.auto:
                            self.map[(md, tn)] = (md, tn2)
                            self.remaining[0].discard((md, tn))
                            self.remaining[1].discard((md, tn2))
                        del rem_tp2[md][tn2]     # done!
                    else:
                        selected = "   "
                    msg_of = f"{subresult[tn2]} of {len(settid1)}"
                    self.dispi('%s%13s = TP2:%s' % (selected, msg_of, tn2))

    def dispi(self, msg=''):
        """Display messages during inspect of testname assignment"""
        if OPT.inspect:
            log.info(msg)

    def get_remaining(self, src, dest) -> set:
        """
        Return remaining set after stage1 pair.

        :param src: source tp idx
        :param dest: 2nd tp idx
        :return: remaining set of (md, tn)
        """
        remaining = set()

        # stage1: same module and same name
        for md_tn in self.tidmap[src].keys():
            if md_tn in self.tidmap[dest]:
                self.map[md_tn] = md_tn
            else:
                remaining.add(md_tn)

        # remove param 'setting_values' or 'corner_identifier' so duplicates can be removed
        for md_tn in remaining:
            d1 = self.mtdata[src][md_tn]
            if 'setting_values' in d1:
                del d1['setting_values']
            if 'corner_identifier' in d1:
                del d1['corner_identifier']

        # remove testinstances that are "duplicate" by content
        dlist = set()    # delete list
        for md_tn in sorted(remaining):
            if md_tn in dlist:
                continue
            d1 = self.mtdata[src][md_tn]
            for target in remaining - dlist:
                if target == md_tn:
                    continue
                if target in dlist:
                    continue
                d2 = self.mtdata[src][target]
                if d1 == d2:
                    log.info(f"-i- Collapsing from TP{src+1}: {target}, keep: {md_tn[1]}")
                    dlist.add(target)

        return remaining - dlist


if __name__ == '__main__':  # pragma: no cover
    TPDiff(desc=__doc__).main()
