#!/usr/intel/pkgs/python3/3.6.3a/modules/r1/bin/python3 -u

"""
Full featured TP differ

Usage:
CMD> tp_diff.py <path_tpold>/EnvironmentFile.env <path_tpnew>/EnvironmentFile.env
CMD> tp_diff.py <path_tpold>/EnvironmentFile.env <path_tpnew>/EnvironmentFile.env -stpl1 file.stpl [-stpl2 file.stpl]

Note: If module is missing, then it will show in #1 Tid summary diff and #4 plb and tuple diff
"""
import setenv      # must be first in the imports
import datetime
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
from gadget.tputil import log_usage, get_param
from gadget.disk import listdir_noerror
from gadget.printmore import Dumper
from tp.testprogram import TestProgram
from mod.tiddb import TidDb
from mod.setting import cfg
from collections import defaultdict
from os.path import exists, abspath, dirname, join, basename, isdir
from misc import usage_track as utrack
import os
import sys
import glob
import re
import pickle
import csv
import pandas as pd


class TPDiff(Args):  # parent: ArgsBase
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
        cnfg.s = TA_StoreTrue('Show only differences, used with -sdiff')
        cnfg.W = TA_StoreNumber('Specify column length for -sdiff', default=60, metavar=60)
        cnfg.value = TA_StoreTrue('Show value instead of equation for -tim or -lvl')
        cnfg.tim = TA_AppendSC('CMD: Do timing diff. [-s, -W, -value]', metavar='tc1[,tc2]')
        cnfg.lvl = TA_AppendSC('CMD: Do level diff. [-s, -W, -value]', metavar='tc1[,tc2]')
        cnfg.userinputlist = TA_StoreFile('Specify user input list for Sort Class Comparison', metavar='file.xslx')

        return cnfg

    def main(self):
        """
        Main entry point of executable
        -h will not reach this method, since that is taken cared of in Args Base class
        """

        # SCRIPT USAGE
        script_name = utrack.get_script_name(sys.argv[0])
        utrack.add_start_hit(script_name)  # Track script usage

        # independent options
        log_usage('tp_diff', cfg)
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
                    args=('MAIN',))

        flow.disp_flows(OPT.flows)  # -flows: help: Display flows
        self.disp_options()  # Display options
        diff.intro()  # Display which testprogram
        flow.run()  # execute the flows

        log.info('')
        log.info('-i- End of diff')

        # SCRIPT USAGE
        utrack.add_finish_hit(script_name)  # Track script usage

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
            return []  # empty string, do not instantiate a TP

        if not OPT.all or len(OPT.all) <= 1:
            log.info("Error: First and 2nd argument must be testprogram env file.")
            log.info("Usage: tp_diff.py  <path_tp1>/EnvironmentFile.env <path_tp2>/EnvironmentFile.env")
            log.info("Execute 'tp_diff.py -h' for more info.")
            log.info('')
            exit(0)

        return None  # default run

    def do_sdiff(self):
        """do -sdiff, independent command run"""
        if not OPT.sdiff:
            return  # Do nothing

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

        self.out = OPT.out  # Output directory
        self.robj_mod = None
        self.is_detail = OPT.detail
        self.userinputlist = OPT.userinputlist

        if OPT.module:
            self.robj_mod = re.compile(r'^\s*(%s)' % OPT.module)

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
            self.tp[0] = self.tp[0].pickle_init()
            self.tp[1] = self.tp[1].pickle_init()
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
        tp = [self.tp[0], self.tp[1]]  # shortcut
        stpl = [basename(tp[0].get_stpl()), basename(tp[1].get_stpl())]
        loc = [tp[0].locset.location, tp[1].locset.location]

        log.info('')
        log.info(f"Left TP: {tp[0].get_name()}, {tp[0].envfile}, {stpl[0]}, {loc[0]}")
        log.info(f"Right TP: {tp[1].get_name()}, {tp[1].envfile}, {stpl[1]}, {loc[1]}")
        log.info('')

    def tim_diff(self):
        result = [defaultdict(dict), defaultdict(dict)]
        result_TP1 = defaultdict(dict)  # define dict
        result_TP2 = defaultdict(dict)
        TP_Dictionary = [defaultdict(dict), defaultdict(dict)]
        Freq_comparison_dict = defaultdict(list)
        if self.userinputlist:  # sort vs class algorithm based on user input mapping
            self.read_userinputlist(self.userinputlist)  # can used it in other defination
            ref = [defaultdict(set), defaultdict(set)]
            TP1_md_tn = []  # make an empty list
            TP2_md_tn = []
            user_mdtn = []
            Freq_group = []
            self.user_md = pd.read_excel(self.userinputlist, sheet_name='TimToMatch')  # open dataframe from excel
            self.user_md_tn1 = self.user_md['Module_TP1'].tolist()  # read excel column to become list
            self.user_md_tn2 = self.user_md['Module_TP2'].tolist()
            for i in range(len(self.user_md_tn1)):
                usermodule = '%s|%s' % (self.user_md_tn1[i], self.user_md_tn2[i])
                user_mdtn.append(usermodule)
            self.pin_tocompare1 = self.user_md['Freq_to_Compare_TP1'].tolist()
            self.pin_tocompare2 = self.user_md['Freq_to_Compare_TP2'].tolist()
            for i in range(len(self.pin_tocompare1)):
                userpin = '%s|%s' % (self.pin_tocompare1[i], self.pin_tocompare2[i])
                Freq_group.append(userpin)
            # self.pin_tocompare_dict={user_mdtn[i]:user_pin[i] for i in range (len(user_pin))}
            # pin_comparison_dict = {user_mdtn[i]:user_pin[i] for i in range (len(user_pin))}
            module_pin_tuple = list(zip(user_mdtn, Freq_group))  # way to have duplicate key
            for k, v in module_pin_tuple:
                Freq_comparison_dict[k].append(v)
            # print("comparison_dict:{}".format(Freq_comparison_dict))

            for TP1_module_tn, TP2_module_tn in self.user_mapping.items():
                TP1_md_tn = TP1_module_tn.split("::")
                TP2_md_tn = TP2_module_tn.split("::")
                TP1_Data = self.tp[0].mtpl.get_instance(TP1_md_tn[0], TP1_md_tn[1])
                TP2_Data = self.tp[1].mtpl.get_instance(TP2_md_tn[0], TP2_md_tn[1])
                timing_TP1 = get_param(TP1_Data, 'timing')
                # print("TP1_timing:{}".format(timing_TP1))
                timing_TP2 = get_param(TP2_Data, 'timing')
                # print("TP2_timing:{}".format(timing_TP2))
                result_TP1 = self.tp[0].timing.get_period_param(timing_TP1)
                # print("TP1_result:{}".format(result_TP1))
                result_TP2 = self.tp[1].timing.get_period_param(timing_TP2)
                # print("TP2_result:{}".format(result_TP2))

                keys = []
                TP1_value = []
                keys1 = []
                TP2_value = []
                for key, value in result_TP1.items():  # pin and lvl for TP1
                    keys.append(key)
                    TP1_value.append(value)
                # print("TP1_key:{}".format(keys))
                # print("TP1_value:{}".format(TP1_value))
                for key, value in result_TP2.items():
                    keys1.append(key)
                    TP2_value.append(value)
                # print("TP2_key:{}".format(keys1))
                # print("TP2_value:{}".format(TP2_value))

                TP_Dictionary[0][TP1_module_tn][timing_TP1] = {keys[i]: TP1_value[i] for i in range(len(keys))}
                TP_Dictionary[1][TP2_module_tn][timing_TP2] = {keys1[i]: TP2_value[i] for i in range(len(keys1))}
                # print("Dict1:{}".format(TP_Dictionary[0][TP1_module_tn][timing_TP1]))
                # print("Dict2:{}".format(TP_Dictionary[1][TP2_module_tn][timing_TP2]))
                # example: TP_Dictionary[0][TP1_module_tn][timing_TP1] = {freq:value}

            outcsv = "SortClasstimingDiff"
            self.sortclass_timing_diff(TP_Dictionary, outcsv, Freq_comparison_dict, self.user_mapping)
            # log.info(TP_Dictionary)

        else:
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
                for md, tn, data in self.tp[nn].mtpl.iter_flows('MAIN', **kwargs):
                    ref[nn][get_param(data, 'timing', 'NA')].add(f'{md}  {tn}')

            outcsv = "timDiff"
            self.twolevel_diff(result, ref, outcsv, outcsv)

    def lvl_diff(self):
        """Level diff for sort class TP"""  # handling missing key
        result = [defaultdict(dict), defaultdict(dict)]
        result_TP1 = defaultdict(dict)  # define dict
        result_TP2 = defaultdict(dict)
        TP_Dictionary = [defaultdict(dict), defaultdict(dict)]
        pin_comparison_dict = defaultdict(list)
        # print(self.User_MD_TN)
        if self.userinputlist:  # sort vs class algorithm based on user input mapping
            self.read_userinputlist(self.userinputlist)  # can used it in other defination
            ref = [defaultdict(set), defaultdict(set)]
            TP1_md_tn = []  # make an empty list
            TP2_md_tn = []
            user_mdtn = []
            user_pin = []
            compareDict = []
            # level_diff poc testing
            # reading module and pin names from userinput file
            self.user_md = pd.read_excel(self.userinputlist, sheet_name='PinsToMatch')  # open dataframe from excel
            self.user_md_tn1 = self.user_md['Module_TP1'].tolist()  # read excel column to become list
            self.user_md_tn2 = self.user_md['Module_TP2'].tolist()
            for i in range(len(self.user_md_tn1)):
                usermodule = '%s|%s' % (self.user_md_tn1[i], self.user_md_tn2[i])
                user_mdtn.append(usermodule)
            self.pin_tocompare1 = self.user_md['Pin_to_Compare_TP1'].tolist()
            self.pin_tocompare2 = self.user_md['Pin_to_Compare_TP2'].tolist()
            for i in range(len(self.pin_tocompare1)):
                userpin = '%s|%s' % (self.pin_tocompare1[i], self.pin_tocompare2[i])
                user_pin.append(userpin)
            # self.pin_to_compare_dict={user_mdtn[i]:user_pin[i] for i in range (len(user_pin))}
            # pin_comparison_dict = {user_mdtn[i]:user_pin[i] for i in range (len(user_pin))}
            module_pin_tuple = list(zip(user_mdtn, user_pin))  # way to have duplicate key
            for k, v in module_pin_tuple:
                pin_comparison_dict[k].append(v)

            for TP1_module_tn, TP2_module_tn in self.user_mapping.items():
                TP1_md_tn = TP1_module_tn.split("::")
                TP2_md_tn = TP2_module_tn.split("::")
                TP1_Data = self.tp[0].mtpl.get_instance(TP1_md_tn[0], TP1_md_tn[1])
                TP2_Data = self.tp[1].mtpl.get_instance(TP2_md_tn[0], TP2_md_tn[1])
                levels_TP1 = get_param(TP1_Data, 'level')
                levels_TP2 = get_param(TP2_Data, 'level')
                result_TP1 = self.tp[0].levels.get_lvl_pin_val(levels_TP1, 'VForce')
                result_TP2 = self.tp[1].levels.get_lvl_pin_val(levels_TP2, 'VForce')
                keys = []
                TP1_withV = []
                keys1 = []
                TP2_withV = []
                for key, value in result_TP1.items():  # pin and lvl for TP1
                    keys.append(key)
                    if value[1] == "":
                        TP1_withV.append(value[0])
                    else:
                        TP1_withV.append(value[1])
                for key, value in result_TP2.items():
                    keys1.append(key)
                    if value[1] == "":
                        TP2_withV.append(value[0])
                    else:
                        TP2_withV.append(value[1])

                TP1_remove_V = [str(s).replace("V", "") for s in TP1_withV]  # for removing V
                TP2_remove_V = [str(s).replace("V", "") for s in TP2_withV]  # for removing V
                new_dict = {keys[i]: TP1_remove_V[i] for i in range(len(keys))}
                new_dict1 = {keys1[i]: TP2_remove_V[i] for i in range(len(keys1))}
                TP_Dictionary[0][TP1_module_tn][levels_TP1] = new_dict
                TP_Dictionary[1][TP2_module_tn][levels_TP2] = new_dict1

                Dict_compare = pin_comparison_dict.values()
                Dict_compare1 = TP_Dictionary[0][TP1_module_tn][levels_TP1].values()
                # print('Values:{}'.format(TP_Dictionary[0][TP1_module_tn][levels_TP1].values()))
                # print('Keys:{}'.format(TP_Dictionary[0][TP1_module_tn][levels_TP1].keys()))

                # for param, value in self.tp[0].levels.iter_params(levels_TP1, isvalue=True):
                #    result[0][levels_TP1][param] = value
                # #print('ya:{}'.format(value))
                # for param, value in self.tp[1].levels.iter_params(levels_TP2, isvalue=True):
                #    result[1][levels_TP2][param] = value
                # #print('ya1:{}'.format(value))

                ref[0][levels_TP1].add(f'{TP1_md_tn[0]}  {TP1_md_tn[1]}')  # add new element to a set
                ref[1][levels_TP2].add(f'{TP2_md_tn[0]}  {TP2_md_tn[1]}')

            outcsv = "SortClassLvlPinDiff"
            self.sortclass_level_diff(TP_Dictionary, outcsv, pin_comparison_dict, self.user_mapping)
            # log.info(TP_Dictionary)

        else:
            result = [defaultdict(dict), defaultdict(dict)]
            for nn in (0, 1):
                for tc in self.tp[nn].levels.iter_tc():
                    # print("KM2 {}".format(tc))
                    if self.is_skip_module(tc):
                        continue
                    for param, value in self.tp[nn].levels.iter_params(tc, isvalue=True):
                        result[nn][tc][param] = value

            # get mapping of timings to testinstance
            ref = [defaultdict(set), defaultdict(set)]
            for nn in (0, 1):
                kwargs = dict(passonly=False, bypass=False, keyparam='patlist', edict=True)
                for md, tn, data in self.tp[nn].mtpl.iter_flows('MAIN', **kwargs):
                    ref[nn][get_param(data, 'level', 'NA')].add(f'{md}  {tn}')
            outcsv = "LvlDiff"
            self.twolevel_diff(result, ref, outcsv, outcsv)

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
            for plb in self.tp[nn].plists.get_plb_map():  # all loaded plb
                md = mapmod[nn].get(plb, ('', None))[0]  # md is empty when plb is unused by testinstance
                if self.is_skip_module(md):
                    continue
                pats = self.tp[nn].plists.get_pats_from_plb(plb, order=True)
                raw[nn][md][plb] = [tid_from_pat(x) for x in pats]  # just get tid number

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
            for plb in self.tp[nn].plists.get_plb_map():  # all loaded plb
                md = mapmod[nn].get(plb, ('', None))[0]  # md is empty when plb is unused by testinstance
                if self.is_skip_module(md):
                    continue
                pats = self.tp[nn].plists.get_pats_from_plb(plb)
                raw[nn][md][plb] = {tuple_tid(pat)[0]: pat for pat in pats}  # full patternname

        # Process
        out_lines = defaultdict(list)
        out_cnt = defaultdict(int)
        for md, plb in sorted(iter_levels(raw[1], 2)):
            if md and plb in raw[0][md] and raw[0][md][plb] != raw[1][md][plb]:
                key = f'{md} {plb}'
                for tup in sorted(raw[1][md][plb]):  # use 2nd tp as reference!
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
        raw = [defaultdict(dict), defaultdict(dict)]  # <plb>: {tid: tuple}
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
        if self.userinputlist:
            """sort class tid diff based on user input module, test instance"""
            self.read_userinputlist(self.userinputlist)
            outlines = []
            text = 'Module,TestInstance,corner,freq,edckill,patlist,tid,pattern,diff,Module,TestInstance,corner,freq,' \
                   'edckill,patlist,tid,pattern '
            outlines.append(text)

            for md1, md2 in self.user_mapping.items():
                tp1_mdtn = md1.split("::")
                tp2_mdtn = md2.split("::")
                md_tn = [tp1_mdtn, tp2_mdtn]
                data = [self.tp[0].mtpl.get_instance(md_tn[0][0], md_tn[0][1]),
                        self.tp[1].mtpl.get_instance(md_tn[1][0], md_tn[1][1])]
                patlist = [data[0]['patlist'], data[1]['patlist']]

                raw = [defaultdict(dict), defaultdict(dict)]

                for nn in (0, 1):
                    pats = self.tp[nn].plists.get_pats_from_plb(patlist[nn])
                    result_tidset = self.tp[nn].plists.get_tid_from_pats(pats)
                    # set default if the key is not found
                    data[nn].setdefault('_CORNER', 'None')
                    data[nn].setdefault('_FREQ', 'None')
                    data[nn].setdefault('_EDCKIL', 'None')
                    key = ','.join([md_tn[nn][1], data[nn]['_CORNER'], data[nn]['_FREQ'],
                                    data[nn]['_EDCKIL'], patlist[nn]])
                    raw[nn][md_tn[nn][0]][key] = {tuple_tid(pat)[1]: pat for pat in pats}

                key1 = ','.join([md_tn[0][1], data[0]['_CORNER'], data[0]['_FREQ'], data[0]['_EDCKIL'], patlist[0]])
                key2 = ','.join([md_tn[1][1], data[1]['_CORNER'], data[1]['_FREQ'], data[1]['_EDCKIL'], patlist[1]])

                for tid in sorted(raw[0][md_tn[0][0]][key1].keys()):
                    if tid in sorted(raw[1][md_tn[1][0]][key2].keys()):
                        c1 = ['%s %s %s' % (md_tn[0][0], key1, tid)]
                        c2 = ['match']
                        c3 = ['%s %s %s' % (md_tn[1][0], key2, tid)]
                    else:
                        c1 = ['%s %s %s' % (md_tn[0][0], key1, tid)]
                        c2 = ['<']
                        c3 = ['']
                    for r1, r2, r3 in zip(c1, c2, c3):
                        r1 = ["{} {}".format(r1, n) for m, n in raw[0][md_tn[0][0]][key1].items() if
                              m in r1.split(' ')[2].strip()]
#                        else:
#                            i = ["{} {} none".format(md_tn[0][0], key1)]
                        if len(r3) > 0:
                            j = ["{} {}".format(r3, y) for x, y in raw[1][md_tn[1][0]][key2].items() if
                                 x in r3.split(' ')[2].strip()]
                        else:
                            j = ["{} {} none none".format(md_tn[1][0], key2)]

                        r1 = '%s' % r1 if r1 else r1
                        r3 = '%s' % j if r1 else j
                        r1 = r1.strip("['']").replace('#0', '')
                        r3 = r3.strip("['']").replace('#0', '')
                        text = '%s,%s,%s' % (space2comma(r1, 8), r2, space2comma(r3, 8))
                        outlines.append(text)
                for tid1 in sorted(raw[1][md_tn[1][0]][key2].keys()):
                    if tid1 not in sorted(raw[0][md_tn[0][0]][key1].keys()):
                        c1 = ['']
                        c2 = ['>']
                        c3 = ['%s %s %s' % (md_tn[1][0], key2, tid1)]

                    for r1, r2, r3 in zip(c1, c2, c3):
                        if len(r1) > 0:
                            i = ["{} {}".format(r1, n) for m, n in raw[0][md_tn[0][0]][key1].items() if
                                 m in r1.split(' ')[2].strip()]
                        else:
                            i = ["{} {} none none".format(md_tn[0][0], key1)]

                        r3 = ["{} {}".format(r3, y) for x, y in raw[1][md_tn[1][0]][key2].items() if
                              x in r3.split(' ')[2].strip()]
#                        else:
#                            j = ["{} {} none none".format(md_tn[1][0], key2)]

                        r1 = '%s' % i if i else i
                        r3 = '%s' % r3 if i else r3
                        r1 = r1.strip("['']").replace('#0', '')
                        r3 = r3.strip("['']").replace('#0', '')
                        text = '%s,%s,%s' % (space2comma(r1, 8), r2, space2comma(r3, 8))
                        outlines.append(text)

            # print sort class report summary .csv
            with open(join(self.out, 'sort_class_tid_diff.csv'), 'w') as fh:
                outlines = list(dict.fromkeys(outlines))  # remove duplication
                fh.write('1st line is TP1: {}\n'.format(self.tp[0].get_name()))
                fh.write('2nd line is TP2: {}\n'.format(self.tp[1].get_name()))
                fh.write('\n'.join(outlines))
                fh.write('\n')

                log.info(f'Printing sort class tid diff report to: {join(self.out)}.sort_class_tid_diff.csv')
        else:
            if OPT.module:
                self.tidpat_diff()
            else:
                # initialize
                tdb = [None, None]  # TidDb
                dctr = [None, None]  # final dictionary
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
                                            indent=0, col=60, diffonly=True, nc=True, sep=' tids  = ')

                # report summary .csv
                if self.out:
                    with open(join(self.out, 'tid_diff.csv'), 'w') as fh:
                        text = 'Module,corner,freq,edckill,tid_count,diff,Module,corner,freq,edckill,tid_count'
                        fh.write(f'{text}\n')  # header
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
                            tdb[nn].dumpfile(join(self.out, f'{self.tp[nn].get_name()}.tid.csv'))

    def tidpat_diff(self):
        """ TID with pat diff given two tp"""
        # read the test program
        idata = [defaultdict(dict), defaultdict(dict)]
        pdata = [{}, {}]
        for nn in (0, 1):
            kwargs = dict(passonly=False, bypass=True, keyparam='patlist', edict=True, r_mod=self.robj_mod)
            for md, tn, data in self.tp[nn].mtpl.iter_flows('MAIN', **kwargs):
                if self.is_skip_module(md):
                    continue
                pats = self.tp[nn].plists.get_pats_from_plb(data['patlist'])
                set_plistfiles = self.tp[nn].plists.plb_to_filename([data['patlist']], fullpath=True)
                key = ','.join([tn, data['_CORNER'], data['_FREQ'], data['_EDCKIL']])
                # ,data.get('plistfile', set_plistfiles.pop())]
                pkey = ','.join([md, tn, data['_CORNER'], data['_FREQ'], data['_EDCKIL'], data['patlist']])
                idata[nn][md][key] = {tuple_tid(pat)[1]: pat for pat in pats}
                pdata[nn][(md, tn)] = pkey

        outlines = []
        text = 'Module,TestInstance,corner,freq,edckill,patlist,tid,pattern,diff,Module,TestInstance,corner,freq,' \
               'edckill,patlist,tid,pattern '

        outlines.append(text)

        diff_char = set()
        is_changed = False
        for md, key in iter_levels(idata[1], 2):
            if md in idata[0] and key in idata[0][md]:
                is_changed = True
                d1, d2 = SDiff().set2key({f'{md} {key} {k} ': set([v]) for k, v in idata[0][md][key].items()},
                                         {f'{md} {key} {k} ': set([v]) for k, v in idata[1][md][key].items()},
                                         aligned=True)

                c1, c2, c3 = SDiff().keyval(d1, d2, indent=0, col=80, diffonly=True, sep=' = ')
                diff_char.update(c2)

                for r1, r2, r3 in zip(c1, c2, c3):
                    if len(r1) > 0:
                        i = ["{} {}".format(r1, n) for m, n in idata[0][md][key].items() if
                             m in r1.split(' ')[2].strip()]
                    else:
                        i = ["{} {} none none".format(md, key)]
                    if len(r3) > 0:
                        j = ["{} {}".format(r3, y) for x, y in idata[1][md][key].items() if
                             x in r3.split(' ')[2].strip()]
                    else:
                        j = ["{} {} none none".format(md, key)]
                    if r2 == ' ':
                        r2 = 'match'

                    r1 = '%s' % i if i else i
                    r3 = '%s' % j if i else j
                    r1 = r1.strip("['']").replace('#0', '')
                    r3 = r3.strip("['']").replace('#0', '')
                    """append patlist"""
                    # TP1
                    r1 = space2comma(r1, 8)
                    r1 = r1.split(',')
                    k = (r1[0], r1[1])
                    j = pdata[0][k]
                    m = j.split(',')
                    r1_all_fields = ','.join((r1[0], r1[1], r1[2], r1[3], r1[4], m[5], r1[5], r1[6]))
                    # TP2
                    r3 = space2comma(r3, 8)
                    r3 = r3.split(',')
                    n = (r3[0], r3[1])
                    p = pdata[1][n]
                    q = p.split(',')
                    r3_all_fields = ','.join((r3[0], r3[1], r3[2], r3[3], r3[4], q[5], r3[5], r3[6]))
                    text = '%s,%s,%s' % (r1_all_fields, r2, r3_all_fields)
                    outlines.append(text)
        if not is_changed:
            log.info('No change')
        # print it
        if self.out:
            with open(join(self.out, 'tidpat_diff.csv'), 'w') as fh:
                fh.write('\n'.join(outlines))
                fh.write('\n')
        from gadget.helperclass import IS_UT
        if IS_UT:
            return 1
        log.info('Print output table to tidpat_diff_module.csv')

    def ctrbin_diff(self):
        """Flow diff given two tp"""
        result = [defaultdict(dict), defaultdict(dict)]
        for nn in (0, 1):
            kwargs = dict(passonly=False, bypass=True, flownames=True, pdict=True, r_mod=self.robj_mod)
            for md, dutflow, dutitem, ports in self.tp[nn].mtpl.iter_flows('MAIN', **kwargs):
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
                    continue  # only above items

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
            for md, dutflow, dutitem, ports in self.tp[nn].mtpl.iter_flows('MAIN', **kwargs):
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
            for md, dutflow, dutitem, ports in self.tp[nn].mtpl.iter_flows(which, **kwargs):
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
            for md, tn, data in self.tp[nn].mtpl.iter_flows('MAIN', **kwargs):
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
        idata = None  # so it's not accessible anymore

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
        if self.userinputlist:  # sort vs class algorithm based on user input mapping
            self.read_userinputlist(self.userinputlist)

            diff_tn = defaultdict(list)
            match_tn = defaultdict(list)

            for md, key in self.user_mapping.items():
                TP1_md_tn = md.split("::")
                TP2_md_tn = key.split("::")
                TP1_Data = self.tp[0].mtpl.get_instance(TP1_md_tn[0], TP1_md_tn[1])
                TP2_Data = self.tp[1].mtpl.get_instance(TP2_md_tn[0], TP2_md_tn[1])
                # if TP1_Data != TP2_Data:
                a1, a2, a3 = SDiff().keyval(TP1_Data, TP2_Data, disp=False)
                # make it row instead of column
                diffdata = []
                matchdata = []
                for c1, c2, c3 in zip(a1, a2, a3):
                    if c2 == '<':
                        diffdata.append(f'{c1} = {TP1_Data[c1]} | < | (none)=(none)')
                        # diffdata.append(f'   < (none)')
                    elif c2 == '>':
                        diffdata.append(f'(none)=(none) | > |  {c3} = {TP2_Data[c3]}')
                        # diffdata.append(f'   > {c3} = {idata[1][md][key][c3]}')
                    elif c2 == ' ':
                        # pass
                        matchdata.append(f'{c1} = {TP1_Data[c1]} | matching | {c3} = {TP2_Data[c3]}')
                    else:
                        diffdata.append(f'{c1} = {TP1_Data[c1]} | {c2} | {c3} = {TP2_Data[c3]}')
                        # print("DiffData = {}".format(diffdata))
                        # diffdata.append(f'   {c2} {c3} = {idata[1][md][key][c3]}')
                diff_tn[tuple(diffdata)].append(f'{md} {key}')
                match_tn[tuple(matchdata)].append(f'{md} {key}')

        else:
            # To do
            # 1.
            # read the testprograms
            idata = [defaultdict(dict), defaultdict(dict)]

            for nn in (0, 1):
                kwargs = dict(passonly=False, bypass=True, edict=True, r_mod=self.robj_mod)
                for md, tn, data in self.tp[nn].mtpl.iter_flows('MAIN', **kwargs):
                    idata[nn][md][tn] = self.filter_shared(data)

            diff_tn = defaultdict(list)
            match_tn = defaultdict(list)
            # print(diff_tn)

            for md in sorted(idata[0]):
                if md not in idata[1]:
                    # print(md)
                    continue
                for key in idata[0][md]:
                    key2 = key  # key2 read from the input excel, create another function to get the user input

                    if key not in idata[1][md]:  # change to key2
                        continue  # Display only same key

                    if idata[0][md][key] != idata[1][md][key2]:
                        a1, a2, a3 = SDiff().keyval(idata[0][md][key], idata[1][md][key2], disp=False)
                        # print("{}:{}:{}".format(a1,a2,a3))
                        # make it row instead of column
                        diffdata = []
                        matchdata = []
                        for c1, c2, c3 in zip(a1, a2, a3):
                            if c2 == '<':
                                diffdata.append(f'{c1} = {idata[0][md][key][c1]} | < | (none)=(none)')
                                # diffdata.append(f'   < (none)')
                            elif c2 == '>':
                                diffdata.append(f'(none)=(none) | > |  {c3} = {idata[1][md][key][c3]}')
                                # diffdata.append(f'   > {c3} = {idata[1][md][key][c3]}')
                            elif c2 == ' ':
                                # pass
                                matchdata.append(
                                    f'{c1} = {idata[0][md][key][c1]} | matching | {c3} = {idata[1][md][key][c3]}')
                            else:
                                diffdata.append(
                                    f'{c1} = {idata[0][md][key][c1]} | {c2} | {c3} = {idata[1][md][key][c3]}')
                                # print("DiffData = {}".format(diffdata))
                                # diffdata.append(f'   {c2} {c3} = {idata[1][md][key][c3]}')
                        diff_tn[tuple(diffdata)].append(f'{md} {key}')
                        # print("AfterLoopDiffData = {}".format(diff_tn))
                        match_tn[tuple(matchdata)].append(f'{md} {key}')
        time_now = datetime.datetime.now()
        outfile_name = str('TestInstanceParamDiff_{}'.format(time_now.isoformat())).replace(':', '-').rsplit('.')[0]
        matchfile_name = str('TestInstanceMatchParam_{}'.format(time_now.isoformat())).replace(':', '-').rsplit('.')[0]
        if self.userinputlist:
            header = 'TP1_Test_Name, TP2_Test_Name, Param, TP1 Value, Diff, TP2 Value\n'
        else:
            header = 'Test_Name, Param, TP1 Value, Diff, TP2 Value\n'
        output_file = outfile_name + '.csv'
        matchfile_name = matchfile_name + '.csv'
        # print("diff_tn = {}".format(diff_tn))
        # print("match_tn = {}".format(match_tn))

        if self.out:
            with open(join(self.out, output_file), 'w') as writeOutput:
                legend = True
                writeOutput.write(header)
                for item in sorted(diff_tn, key=lambda x: diff_tn[x][0]):
                    if legend:
                        writeOutput.write('1st line is TP1: {}\n'.format(self.tp[0].get_name()))
                        writeOutput.write('2nd line is TP2: {}\n'.format(self.tp[1].get_name()))
                        legend = False

                    # for md_tn in sorted({self.strip_tn(x, None) for x in diff_tn[item]}):
                    for md_tn in sorted(diff_tn[item]):
                        TP1_TP2_TestName = md_tn.split(" ")
                        for line in item:
                            tp1Param = line.split("=")[0].strip()
                            tp1List = line.split("=")[1].strip()
                            tp1ValueA = tp1List.split("|")[0].strip()
                            try:
                                diff = tp1List.split("|")[1].strip()
                                tp2Key = tp1List.split("|")[2].strip()
                            except (Exception,):
                                pass
                            tp2Value = line.split("=")[2].strip()

                            if tp1Param == "(none)":
                                tp1Param = tp2Key

                            if self.userinputlist:
                                writeOutput.write('"{}","{}","{}","{}","{}","{}"\n'.format
                                                  (TP1_TP2_TestName[0], TP1_TP2_TestName[1], tp1Param, tp1ValueA,
                                                   diff, tp2Value))
                            else:
                                writeOutput.write('"{}","{}","{}","{}","{}"\n'.format
                                                  (md_tn, tp1Param, tp1ValueA, diff, tp2Value))

            if not diff_tn:
                log.info('No change')

        if self.out:
            with open(join(self.out, matchfile_name), 'w') as writerOutput:
                legend = True
                writerOutput.write(header)
                for items in sorted(match_tn, key=lambda x: match_tn[x][0]):
                    # print(items)
                    if legend:
                        writerOutput.write('1st line is TP1: {}\n'.format(self.tp[0].get_name()))
                        writerOutput.write('2nd line is TP2: {}\n'.format(self.tp[1].get_name()))
                        legend = False

                    # for md_tn in sorted({self.strip_tn(x, None) for x in match_tn[items]}):
                    for md_tn in sorted(match_tn[items]):
                        TP1_TP2_TestName = md_tn.split(" ")
                        for line in items:
                            tp1Param = line.split("=")[0].strip()
                            tp1List = line.split("=")[1].strip()
                            tp1ValueA = tp1List.split("|")[0].strip()
                            try:
                                diff = tp1List.split("|")[1].strip()
                                tp2Key = tp1List.split("|")[2].strip()
                            except (Exception,):
                                pass
                            tp2Value = line.split("=")[2].strip()

#                            if tp1Param == "(none)":
#                                tp1Param = tp2Key
#
#                            if tp2Key == "(none)":
#                                tp2Key = tp1Param

                            if self.userinputlist:
                                writerOutput.write('"{}","{}","{}","{}","{}","{}"\n'.format
                                                   (TP1_TP2_TestName[0], TP1_TP2_TestName[1], tp1Param, tp1ValueA,
                                                    diff, tp2Value))
                            else:
                                writerOutput.write('"{}","{}","{}","{}","{}"\n'.format
                                                   (md_tn, tp1Param, tp1ValueA, diff, tp2Value))
                if not match_tn:
                    log.info('No change')

        # print('Test parameter file: {}'.format(output_file))
        # print('Matching Test parameter file: {}'.format(matchfile_name))

        log.info(f'-i- Test Instance Diff Parameter file: {output_file}')
        log.info(f'-i- Test Instance Match Parameter file: {matchfile_name}')

    def basenumber_diff(self):
        """BaseNumber diff given two tp"""
        idata = [{}, {}]
        for nn in (0, 1):
            kwargs = dict(passonly=False, bypass=True, edict=True, r_mod=self.robj_mod)
            for md, tn, data in self.tp[nn].mtpl.iter_flows('MAIN', **kwargs):
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
            return  # Do not show if specific module diffs

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
            return dd  # Do nothing

        return {x: y for x, y in dd.items() if self.robj_mod.search(x)}

    def is_skip_module(self, md):
        """
        Returns True if this module is skipped, based on -module

        :param md: module name
        :return: True if flow is skipped
        """
        if not self.robj_mod:
            return False  # Do not skip

        return not self.robj_mod.search(md)

    def uniqport_dict(self, d1, d2, _robj=re.compile(r'Port#(\S+)')):
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
            return []  # Do nothing, e.g. <mod>/Inputfiles not exist

        missing = []
        changed = []
        added = []
        with TempDir(name=True) as tdir1, TempDir(name=True) as tdir2:
            for ff in sorted(os.listdir(src)):
                if ff in ign:
                    continue  # ignore these files
                if isdir(join(src, ff)):
                    continue  # ignore directories
                if ff.endswith('.flw'):
                    continue  # These files are not worth showing

                if exists(join(dest, ff)):
                    if File(join(src, ff)).sha1() == File(join(dest, ff)).sha1():  # This makes it 3.5x faster
                        res = '+0/-0/0'  # no change since sha is the same
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
                    continue  # ignore these files
                if isdir(join(dest, ff)):
                    continue  # ignore directories
                if ff.endswith('.flw'):
                    continue  # These files are not worth showing
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
            else:  # pragma: no cover - safety only
                raise ErrorCockpit(f'Unknown line[{line}] from sdiff output. marker=[{marker}]')

        return f'+{added}/-{removed}/{changed}'

    @staticmethod
    def strip_tn(tn, freq, robj=re.compile(r'^(.*)_\d+$')):
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
    def port_trace(trc, _robj=re.compile(r'port=(\S+)')):
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
    def port2dict(dd, _robj=re.compile(r'(\d\d\d\d+)')):
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

    def pivottable(self, output_file, shnm):
        df = pd.read_csv(join(self.out, output_file))
        df.fillna('(Blank)', inplace=True)
        # df['TP1_Module'] = df['TP1_Module'].fillna('(Blank)')
        df['Count'] = 1
        # df['t_count'] = df.groupby('TP1_Module')['TP1_Module'].transform('count')
        print(df)
        # a=df.groupby(['TP1_Param','Diff'], as_index=False).size()
        a = pd.pivot_table(data=df, index=['TP1_Module'], columns=['Diff'], values='Count', aggfunc='sum', margins=True,
                           margins_name='Grand Total')
        b = pd.pivot_table(data=df, index=['TP2_Module'], columns=['Diff'], values='Count', aggfunc='sum', margins=True,
                           margins_name='Grand Total')
        print(a)
        print(b)
        with pd.ExcelWriter(join(self.out, '{}_summary.xlsx'.format(output_file))) as writer:
            df.to_excel(writer, sheet_name=shnm)
            a.to_excel(writer, sheet_name='TP1_Summary')
            b.to_excel(writer, sheet_name='TP2_Summary')

    def twolevel_diff(self, result, ref, outcsv, shnm):
        """
        Display two level diff of result dictionary

        structure:
        result[tp][testcondition][param] = value
        """
        some_changed = False
        outlines = []
        text = 'TP1_Module,TP1_Test,TP1_TestCond,TP1_Param, TP1_Timlvl_value,Diff,TP2_Module,TP2_Test,TP2_TestCond,' \
               'TP2_Param,TP2_Timlvl_value '
        text0 = 'TP1_Module,TP1_Test,TP1_TestCond,TP1_Param, TP1_Timlvl_value,Diff'
        outlines.append(text)
        expect = len(text.split(','))
        expect0 = len(text0.split(','))
        tc_status = ""
        diff_char = set()
        instance = "None None"

        for tc in sorted(result[0]):
            if tc not in result[1]:
                tc_status = 'Removed:{}'.format(tc)
                log.info(f'Removed: {tc}')
                # self.disp_instances(ref[0], tc)
                for item in sorted(ref[0].get(tc, [])):
                    if len(item) > 0:
                        log.info(f'  UseBy: {item}')
                        instance = item
                    else:
                        log.info(f'  UseBy: None')
                        instance = 'None'
                some_changed = True

                for param_value in result[0][tc]:
                    c1 = param_value.split("|")
                    c2 = "<"

                    for r1, r2 in zip(c1, c2):
                        r1 = '%s %s %s %s' % (instance, tc_status, r1, result[0][tc][r1]) if r1 else r1

                        text = '%s,%s' % (space2comma(r1, 5), r2)
                        outlines.append(text)
                        tokens = len(text0.split(','))
                        assert expect0 == tokens, f'Error expect column count={expect0} but got {tokens} instead..'
                continue
            if result[0][tc] != result[1][tc]:
                tc_status = 'Changed:{}'.format(tc)
                log.info(f'Changed:{tc}')
                # self.disp_instances(ref[1], tc)
                for items in sorted(ref[1].get(tc, [])):
                    if len(items) > 0:
                        log.info(f'  UseBy: {items}')
                        instance = items
                    else:
                        log.info(f'  UseBy: None')
                        instance = 'None'
                some_changed = True
                c1, c2, c3 = SDiff().keyval(result[0][tc], result[1][tc],
                                            col=60, diffonly=True, sep=' = ', indent=3)

                diff_char.update(c2)

                for r1, r2, r3 in zip(c1, c2, c3):
                    r1 = '%s %s %s %s' % (instance, tc_status, r1, result[0][tc][r1]) if r1 else r1
                    r3 = '%s %s %s %s' % (instance, tc_status, r3, result[1][tc][r3]) if r3 else r3
                    if r2 == ' ':
                        r2 = 'matched'
                    text = '%s,%s,%s' % (space2comma(r1, 5), r2, space2comma(r3, 5))
                    outlines.append(text)
                    tokens = len(text.split(','))
                    assert expect == tokens, f'Error expect column count={expect} but got {tokens} instead..'

        for tc in result[1]:
            if tc not in result[0]:
                tc_status = 'Added:{}'.format(tc)
                log.info(f'Added:   {tc}')
                # self.disp_instances(ref[1], tc)
                for items in sorted(ref[1].get(tc, [])):
                    if len(items) > 0:
                        log.info(f'  UseBy: {items}')
                        instance = items
                    else:
                        log.info(f'  UseBy: None')
                        instance = 'None'
                some_changed = True

                for param_value1 in result[1][tc]:
                    c1 = '%s %s %s %s' % (None, None, None, None)
                    c2 = ">"
                    c3 = param_value1.split("|")

                    for r1, r2, r3 in zip(c1, c2, c3):
                        r3 = '%s %s %s %s' % (instance, tc_status, r3, result[1][tc][r3]) if r3 else r3

                        text = '%s,%s,%s' % (space2comma(r1, 5), r2, space2comma(r3, 5))
                        outlines.append(text)
                        tokens = len(text.split(','))
                        assert expect == tokens, f'Error expect column count={expect} but got {tokens} instead..'
                continue

        time_now = datetime.datetime.now()
        outfile_name = str('{}_{}'.format(outcsv, time_now.isoformat())).replace(':', '-').rsplit('.')[0]
        output_file = outfile_name + '.csv'
        if self.out:
            with open(join(self.out, output_file), 'w') as fh:
                fh.write('\n'.join(outlines))
                fh.write('\n')

        if diff_char == {' '} or (not diff_char):
            log.info('No change')

        if self.out:
            self.pivottable(output_file, shnm)

        from gadget.helperclass import IS_UT
        if IS_UT:
            return 1
        log.info(f'Print output {output_file} successfully!')

    def sortclass_level_diff(self, TP_Dictionary, outcsv, user_pin_comparison, user_mapping):
        """
        Display the VForce differences based on the pin to match specified by user
        """
        pinsToMatchTP1 = []
        pinsToMatchTP2 = []
        MatchOutlines = []  # define list

        TP_Dict_ForPrinting = TP_Dictionary
        MatchText = 'TP1_Module,TP1_Test,TP1_TestCond,TP1_Param,TP1_Lvl_value,Diff,TP2_Module,TP2_Test,TP2_TestCond,' \
                    'TP2_Param,TP2_Lvl_value '
        MatchOutlines.append(MatchText)

        for TP1ModuleName, TP2ModuleName in user_mapping.items():
            TP1_md_tn = TP1ModuleName.split("::")
            TP2_md_tn = TP2ModuleName.split("::")
            TP1_Pins = defaultdict(list)
            TP2_Pins = defaultdict(list)
            PairedModule = "{}|{}".format(TP1_md_tn[0], TP2_md_tn[0])

            for pin_pairing in user_pin_comparison[PairedModule]:
                pin_after_split = pin_pairing.split("|")

                TP1_level = ""
                TP2_level = ""

                for level_key in TP_Dictionary[0][TP1ModuleName]:
                    TP1_level = level_key
                    if pin_after_split[0] in TP_Dictionary[0][TP1ModuleName][level_key]:
                        pinsToMatchTP1.append(pin_after_split[0])
                    else:
                        log.info("ERROR:Pin {} not found in {}. Please check your PinsToMatch tab".format
                                 (pin_after_split[0], TP1ModuleName))
                        return

                for level_key1 in TP_Dictionary[1][TP2ModuleName]:
                    TP2_level = level_key1
                    if pin_after_split[1] in TP_Dictionary[1][TP2ModuleName][level_key1]:
                        pinsToMatchTP2.append(pin_after_split[1])
                    else:
                        log.info("ERROR:Pin {} not found in {}. Please check your PinsToMatch tab".format
                                 (pin_after_split[1], TP2ModuleName))
                        return

            # PairedModule = "{}|{}".format(TP1_md_tn[0],TP2_md_tn[0])

            for pin_elements in user_pin_comparison[PairedModule]:
                split_paired_pin = pin_elements.split("|")
                pin_value_TP1 = "{:.5f}".format(float(TP_Dictionary[0][TP1ModuleName][TP1_level][split_paired_pin[0]]))
                TP_Dict_ForPrinting[0][TP1ModuleName][TP1_level].pop(split_paired_pin[0])
                pin_value_TP2 = "{:.5f}".format(float(TP_Dictionary[1][TP2ModuleName][TP2_level][split_paired_pin[1]]))
                TP_Dict_ForPrinting[1][TP2ModuleName][TP2_level].pop(split_paired_pin[1])
                if pin_value_TP1 > pin_value_TP2:
                    text1 = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % (TP1_md_tn[0], TP1_md_tn[1], TP1_level,
                                                                  split_paired_pin[0], pin_value_TP1, "-", TP2_md_tn[0],
                                                                  TP2_md_tn[1], TP2_level, split_paired_pin[1],
                                                                  pin_value_TP2)
                    MatchOutlines.append(text1)
                elif pin_value_TP1 < pin_value_TP2:
                    text1 = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % (TP1_md_tn[0], TP1_md_tn[1], TP1_level,
                                                                  split_paired_pin[0], pin_value_TP1, "+", TP2_md_tn[0],
                                                                  TP2_md_tn[1], TP2_level, split_paired_pin[1],
                                                                  pin_value_TP2)
                    MatchOutlines.append(text1)
                else:
                    text1 = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % (TP1_md_tn[0], TP1_md_tn[1], TP1_level,
                                                                  split_paired_pin[0], pin_value_TP1, "match",
                                                                  TP2_md_tn[0], TP2_md_tn[1], TP2_level,
                                                                  split_paired_pin[1], pin_value_TP2)
                    MatchOutlines.append(text1)

        # time_now = datetime.datetime.now()
        # outfile_name = str('{}_{}'.format("MatchPins",time_now.isoformat())).replace(':','-').rsplit('.')[0]
        # output_file = outfile_name + '.csv'
        # if self.out:
        #     with open(join(self.out, output_file), 'w') as fh:
        #         fh.write('\n'.join(MatchOutlines))
        #         fh.write('\n')

        outlines = []  # define list
        text = 'TP1_Module,TP1_Test,TP1_TestCond,TP1_Param,TP1_Lvl_value,Diff,TP2_Module,TP2_Test,TP2_TestCond,' \
               'TP2_Param,TP2_Lvl_value '
        outlines.append(text)
        TP1_TextValues = []
        TP2_TextValues = []
        TP1_EmptyValues = []
        TP2_EmptyValues = []
        Diff = ''
        for TP1ModuleName, TP2ModuleName in user_mapping.items():
            TP1_md_tn = TP1ModuleName.split("::")
            TP2_md_tn = TP2ModuleName.split("::")
            TP1_TextValues.clear()  # clear content exist after loop
            TP2_TextValues.clear()
            TP1_EmptyValues.clear()
            TP2_EmptyValues.clear()
            for level_TP1, pin_value in TP_Dict_ForPrinting[0][TP1ModuleName].items():
                tp1_empty_line = '%s,%s,%s,%s,%s' % (TP1_md_tn[0], TP1_md_tn[1], level_TP1, None, None)
                TP1_EmptyValues.append(tp1_empty_line)

                for VforcePin, VforceValue in pin_value.items():
                    text1 = '%s,%s,%s,%s,%s' % (TP1_md_tn[0], TP1_md_tn[1], level_TP1, VforcePin, VforceValue)
                    TP1_TextValues.append(text1)

            for level_TP2, pin_value in TP_Dict_ForPrinting[1][TP2ModuleName].items():
                tp2_empty_line = '%s,%s,%s,%s,%s' % (TP2_md_tn[0], TP2_md_tn[1], level_TP2, None, None)
                TP2_EmptyValues.append(tp2_empty_line)
                for VforcePin, VforceValue in pin_value.items():
                    text2 = '%s,%s,%s,%s,%s' % (TP2_md_tn[0], TP2_md_tn[1], level_TP2, VforcePin, VforceValue)
                    TP2_TextValues.append(text2)

            if (len(TP1_TextValues)) == (len(TP2_TextValues)):
                for i in range(len(TP1_TextValues)):
                    text = '%s,%s,%s' % (TP1_TextValues[i], Diff, TP2_TextValues[i])
                    outlines.append(text)
            elif (len(TP1_TextValues)) < (len(TP2_TextValues)):
                size_difference = len(TP2_TextValues) - len(TP1_TextValues)
                for i in range(len(TP2_TextValues)):
                    if i >= (len(TP2_TextValues) - size_difference):
                        text = '%s,%s,%s' % ((", ".join(TP1_EmptyValues)), Diff, TP2_TextValues[i])
                        outlines.append(text)
                    else:
                        text = '%s,%s,%s' % (TP1_TextValues[i], Diff, TP2_TextValues[i])
                        outlines.append(text)
            else:
                size_difference = len(TP1_TextValues) - len(TP2_TextValues)
                for i in range(len(TP1_TextValues)):
                    if i >= (len(TP1_TextValues) - size_difference):
                        text = '%s,%s,%s' % (TP1_TextValues[i], Diff, (", ".join(TP2_EmptyValues)))
                        outlines.append(text)
                        continue
                    text = '%s,%s,%s' % (TP1_TextValues[i], Diff, TP2_TextValues[i])
                    outlines.append(text)

        time_now = datetime.datetime.now()
        outfile_name = str('{}_PinsToMatch_{}'.format(outcsv, time_now.isoformat())).replace(':', '-').rsplit('.')[0]
        output_file = outfile_name + '.csv'
        if self.out:
            with open(join(self.out, output_file), 'w') as fh:
                fh.write('\n'.join(MatchOutlines))
                fh.write('\n')
        log.info(f'Print output {output_file} successfully!')

        outfile_name = str('{}_{}'.format(outcsv, time_now.isoformat())).replace(':', '-').rsplit('.')[0]
        output_file = outfile_name + '.csv'
        if self.out:
            with open(join(self.out, output_file), 'w') as fh:
                fh.write('\n'.join(outlines))
                fh.write('\n')

        log.info(f'Print output {output_file} successfully!')
        # if self.out:
        #     self.pivottable(output_file, shnm)

    def sortclass_timing_diff(self, TP_Dictionary, outcsv, Freq_comparison_dict, user_mapping):

        timToMatchTP1 = []
        timToMatchTP2 = []
        MatchOutlines = []  # define list

        TP_Dict_ForPrinting = TP_Dictionary
        # print("Original_Dict_TP1={}".format(TP_Dictionary[0]))
        # print("Original_Dict_TP2={}".format(TP_Dictionary[1]))
        MatchText = 'TP1_Module,TP1_Test,TP1_TestCond,TP1_Param,TP1_Tim_value,Diff,TP2_Module,TP2_Test,TP2_TestCond,' \
                    'TP2_Param,TP2_Tim_value '
        MatchOutlines.append(MatchText)

        for TP1ModuleName, TP2ModuleName in user_mapping.items():
            TP1_md_tn = TP1ModuleName.split("::")
            TP2_md_tn = TP2ModuleName.split("::")
            # TP1_tim = defaultdict(list)
            # TP2_tim = defaultdict(list)
            PairedModule = "{}|{}".format(TP1_md_tn[0], TP2_md_tn[0])

            for freq_pairing in Freq_comparison_dict[PairedModule]:
                tim_after_split = freq_pairing.split("|")
                # print("freq_split={}".format(tim_after_split))
                TP1_tim = ""
                TP2_tim = ""

                for tim_key in TP_Dictionary[0][TP1ModuleName]:
                    TP1_tim = tim_key
                    if tim_after_split[0] in TP_Dictionary[0][TP1ModuleName][tim_key]:
                        timToMatchTP1.append(tim_after_split[0])
                    else:
                        log.info("ERROR:Timing Param {} not found in {}. Please check your TimToMatch tab".format
                                 (tim_after_split[0], TP1ModuleName))
                        return

                for tim_key1 in TP_Dictionary[1][TP2ModuleName]:
                    TP2_tim = tim_key1
                    if tim_after_split[1] in TP_Dictionary[1][TP2ModuleName][tim_key1]:
                        timToMatchTP2.append(tim_after_split[1])
                    else:
                        log.info("ERROR:Timing Param {} not found in {}. Please check your TimToMatch tab".format
                                 (tim_after_split[1], TP2ModuleName))
                        return

            # PairedModule = "{}|{}".format(TP1_md_tn[0],TP2_md_tn[0])

            for freq_elements in Freq_comparison_dict[PairedModule]:
                split_paired_tim = freq_elements.split("|")
                tim_value_TP1 = "{}".format(float(TP_Dictionary[0][TP1ModuleName][TP1_tim][split_paired_tim[0]]))
                TP_Dict_ForPrinting[0][TP1ModuleName][TP1_tim].pop(split_paired_tim[0])
                tim_value_TP2 = "{}".format(float(TP_Dictionary[1][TP2ModuleName][TP2_tim][split_paired_tim[1]]))
                TP_Dict_ForPrinting[1][TP2ModuleName][TP2_tim].pop(split_paired_tim[1])
                if tim_value_TP1 > tim_value_TP2:
                    text1 = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % (TP1_md_tn[0], TP1_md_tn[1], TP1_tim,
                                                                  split_paired_tim[0], tim_value_TP1, "-", TP2_md_tn[0],
                                                                  TP2_md_tn[1], TP2_tim, split_paired_tim[1],
                                                                  tim_value_TP2)
                    MatchOutlines.append(text1)
                elif tim_value_TP1 < tim_value_TP2:
                    text1 = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % (TP1_md_tn[0], TP1_md_tn[1], TP1_tim,
                                                                  split_paired_tim[0], tim_value_TP1, "+", TP2_md_tn[0],
                                                                  TP2_md_tn[1], TP2_tim, split_paired_tim[1],
                                                                  tim_value_TP2)
                    MatchOutlines.append(text1)
                else:
                    text1 = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % (TP1_md_tn[0], TP1_md_tn[1], TP1_tim,
                                                                  split_paired_tim[0], tim_value_TP1, "match",
                                                                  TP2_md_tn[0], TP2_md_tn[1], TP2_tim,
                                                                  split_paired_tim[1], tim_value_TP2)
                    MatchOutlines.append(text1)

        outlines = []  # define list
        text = 'TP1_Module,TP1_Test,TP1_TestCond,TP1_Param,TP1_Tim_value,Diff,TP2_Module,TP2_Test,TP2_TestCond,' \
               'TP2_Param,TP2_Tim_value '
        outlines.append(text)
        TP1_TextValues = []
        TP2_TextValues = []
        TP1_EmptyValues = []
        TP2_EmptyValues = []
        Diff = ''
        for TP1ModuleName, TP2ModuleName in user_mapping.items():
            TP1_md_tn = TP1ModuleName.split("::")
            TP2_md_tn = TP2ModuleName.split("::")
            TP1_TextValues.clear()  # clear content exist after loop
            TP2_TextValues.clear()
            TP1_EmptyValues.clear()
            TP2_EmptyValues.clear()
            for tim_TP1, freq_value in TP_Dict_ForPrinting[0][TP1ModuleName].items():
                tp1_empty_line = '%s,%s,%s,%s,%s' % (TP1_md_tn[0], TP1_md_tn[1], tim_TP1, None, None)
                TP1_EmptyValues.append(tp1_empty_line)
                for Tim, TimValue in freq_value.items():
                    text1 = '%s,%s,%s,%s,%s' % (TP1_md_tn[0], TP1_md_tn[1], tim_TP1, Tim, TimValue)
                    TP1_TextValues.append(text1)

            for tim_TP2, freq_value in TP_Dict_ForPrinting[1][TP2ModuleName].items():
                tp2_empty_line = '%s,%s,%s,%s,%s' % (TP2_md_tn[0], TP2_md_tn[1], tim_TP2, None, None)
                TP2_EmptyValues.append(tp2_empty_line)
                for Tim, TimValue in freq_value.items():
                    text2 = '%s,%s,%s,%s,%s' % (TP2_md_tn[0], TP2_md_tn[1], tim_TP2, Tim, TimValue)
                    TP2_TextValues.append(text2)

            if (len(TP1_TextValues)) == (len(TP2_TextValues)):
                for i in range(len(TP1_TextValues)):
                    text = '%s,%s,%s' % (TP1_TextValues[i], Diff, TP2_TextValues[i])
                    outlines.append(text)
            elif (len(TP1_TextValues)) < (len(TP2_TextValues)):
                size_difference = len(TP2_TextValues) - len(TP1_TextValues)
                for i in range(len(TP2_TextValues)):
                    if i >= (len(TP2_TextValues) - size_difference):
                        text = '%s,%s,%s' % ((", ".join(TP1_EmptyValues)), Diff, TP2_TextValues[i])
                        outlines.append(text)
                    else:
                        text = '%s,%s,%s' % (TP1_TextValues[i], Diff, TP2_TextValues[i])
                        outlines.append(text)
            else:
                size_difference = len(TP1_TextValues) - len(TP2_TextValues)
                for i in range(len(TP1_TextValues)):
                    if i >= (len(TP1_TextValues) - size_difference):
                        text = '%s,%s,%s' % (TP1_TextValues[i], Diff, (", ".join(TP2_EmptyValues)))
                        outlines.append(text)
                        continue
                    text = '%s,%s,%s' % (TP1_TextValues[i], Diff, TP2_TextValues[i])
                    outlines.append(text)

        time_now = datetime.datetime.now()
        outfile_name = str('{}_TimToMatch_{}'.format(outcsv, time_now.isoformat())).replace(':', '-').rsplit('.')[0]
        output_file = outfile_name + '.csv'
        if self.out:
            with open(join(self.out, output_file), 'w') as fh:
                fh.write('\n'.join(MatchOutlines))
                fh.write('\n')
        log.info(f'Print output {output_file} successfully!')

        outfile_name = str('{}_{}'.format(outcsv, time_now.isoformat())).replace(':', '-').rsplit('.')[0]
        output_file = outfile_name + '.csv'
        if self.out:
            with open(join(self.out, output_file), 'w') as fh:
                fh.write('\n'.join(outlines))
                fh.write('\n')

        log.info(f'Print output {output_file} successfully!')
        # if self.out:
        #     self.pivottable(output_file,shnm)

    def read_userinputlist(self, userinputlist):
        self.user_mapping = {}
        wb = pd.read_excel(userinputlist, sheet_name='Input')
        tp1_mod = wb['TP1_Module'].tolist()
        tp1_tn = wb['TP1_TestName'].tolist()
        tp2_mod = wb['TP2_Module'].tolist()
        tp2_tn = wb['TP2_TestName'].tolist()

        tp1_list = self.join_input(tp1_mod, tp1_tn)
        tp2_list = self.join_input(tp2_mod, tp2_tn)

        for i in range(len(tp1_mod)):
            self.user_mapping[tp1_list[i]] = tp2_list[i]
        log.info(self.user_mapping)

    def join_input(self, md, tn):
        md_tn = []
        for i in range(len(md)):
            assert (not pd.isna(md[i])), "Module column consist of empty cells in row{}".format(i + 2)
            assert (not pd.isna(tn[i])), "TestName column consist of empty cells in row{}".format(i + 2)
            input = "{}::{}".format(md[i], tn[i])
            md_tn.append(input)

        return md_tn

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


class PairModule:  # pragma: no cover
    """Pair at module level based on TID existence, for those that are not matching"""

    def __init__(self, tp1: TestProgram, tp2: TestProgram):
        self.tp = [tp1, tp2]
        self.map = defaultdict(set)  # {mod_tp1: set(mod_tp2)}   # 1:many
        self.uniq = [set(), set()]  # unique modules, no TID match
        self.tidtp = [defaultdict(set), defaultdict(set)]  # 0-tp1: {md: set(tid)}

        # read tid per module
        self.read_module_tid(self.tp[0], self.tidtp[0])
        self.read_module_tid(self.tp[1], self.tidtp[1])

        self.process()

        self.report()

    def process(self):
        """Process the module pairing"""

        # Do same module name pair
        found = set()  # found in tp2
        for md in self.tidtp[0]:
            if md in self.tidtp[1]:
                self.map[md].add(md)
                found.add(md)

        # Do pairing of uniq modules
        for md in self.tidtp[0]:
            if md in self.tidtp[1]:
                continue  # ignore existing
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
            return  # Nothing to print
        log.info(f"Unique modules for TP{tpidx + 1}, with patlist:")
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
                result_tidset = tpobj.plists.get_tid_from_pats(tpobj.plists.get_pats_from_plb
                                                               (dd['patlist']), istestname)
            except BaseException:
                continue  # temporary, remove this later when the iter_flows is bypass=True and all pass flows
            tidset[md].update(result_tidset)


class PairInstance:  # pragma: no cover
    """Smart pair of testinstances"""

    def __init__(self, tp1: TestProgram, tp2: TestProgram):
        self.tp = [tp1, tp2]
        self.map = {}  # {(mod, tn): (mod, tn)}
        self.tidmap = [{}, {}]  # 0 - tp1: {(mod, tn): set of tid or testname}
        self.remaining = [None, None]  # 0 - tp1: {(mod, tn)}  - uniq instances
        self.mtdata = [{}, {}]  # 0 - tp1: {(mod, tn): {instance_dict}}

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
        rem_tp2 = defaultdict(dict)  # {md: {tn: set_of_tid}}
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
                        del rem_tp2[md][tn2]  # done!
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
        dlist = set()  # delete list
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
                    log.info(f"-i- Collapsing from TP{src + 1}: {target}, keep: {md_tn[1]}")
                    dlist.add(target)

        return remaining - dlist


if __name__ == '__main__':  # pragma: no cover
    TPDiff(desc=__doc__).main()
