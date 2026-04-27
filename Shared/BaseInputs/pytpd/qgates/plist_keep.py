#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Check to ensure #KEEP# usage is correct. If the tags are incorrect or inconsistent, it can cause TTR or DPM problems (or both).
Checks:
1) 242 - #KEEP# - not #KEEP
2) 241 - For any tests w/ #KEEP#, make sure if same TID (for array/fun) or same TUPLE (for scan) shows up again in plist,
#KEEP# on all repeats.
"""
import sys

import setenv
import re
from gadget.dictmore import xmlfunc, iter_dot_items, find_dot_items
from gadget.pylog import log
from gadget.strmore import curtime, strvalue, truncate, to_str
from qgates.qgate_base import QGateBase
from gadget.tputil import remove_ip, tid_from_pat
from gadget.files import File
from tp.testprogram import TestProgram
from pprint import pprint
from xml.etree import cElementTree as ElementTree
from os.path import basename
from mod.setting import cfg
import sys
import json

# 1:make list of TIDs/tuples with #KEEP# per plist that is actually used in the TP (and add error if you see "#KEEP" without trailing hash)
# 2:make list of TIDs/tuples without #KEEP# per plist
# 3:look for TID/tuples from list1 in list 2 - if exist, add error for module and plist


class PListKeep(QGateBase):

    def main(self):
        plists = set()
        mod_plists = {}
        pats = []
        for mod, item, params, ports in self.tpobj.mtpl.iter_flows('MAIN', bypass=True, edict=True, pdict=True):
            if 'PlistConfigTC' in params['TEMPLATE']:
                continue    # skip this Template
            for param in ('Plist', 'patlist'):
                if param in params:
                    patlist = params[param]
                    patlist2 = remove_ip(patlist)
                    plists.add(patlist2)
                    if patlist2 not in mod_plists:
                        mod_plists[patlist2] = []
                    mod_plists[patlist2].append(mod)
        # map of plbs to the files they live in
        plbmap = self.tpobj.plists.get_plb_map()
        # lets make a reverse map so we only open each file once, and know every plb we care about in there
        filemap = {}
        for plist, filename in plbmap.items():
            if plist in plists:
                if filename not in filemap:
                    filemap[filename] = []
                filemap[filename].append(plist)
        # lets go through all of the files in the filemap
        for filename, plistlist in filemap.items():
            with open(File.realname(filename), "r") as file:
                # print(f'opening file {filename} for plists {plistlist}')
                content = file.read()
                self.process_plist(content, plistlist, mod_plists)
        return

    def process_plist(self, content, valid_plists, mod_plists):
        plistlevel = 0
        current_plist = ""
        strings = {}
        active_plists = []
        errors = []
        # make a plist stack that grows each time you see GlobalPlist before a }. When you see a },
        # pop the last entry on the list. Foreach  plist in current stack, add the pattern
        # to a dict with plists for keys, and "keep" and "nokeep" lists of patterns.
        lines = content.split('\n')
        for line in lines:
            plistnamematch = re.match(r'\s*GlobalPList (\w+)\s+', line)
            if plistnamematch:
                plistlevel += 1
                current_plist = plistnamematch.group(1)
                strings[current_plist] = {'keep': [], 'nokeep': []}
                active_plists.append(current_plist)
                continue
            if plistlevel >= 1:
                badkeeppatmatch = re.match(r'\s*Pat\s+(\w+);\s*#KEEP\s*$', line)
                # While we are at it, check for a malformed #KEEP Tag (note - could be expanded, this is the case Wei asked for)
                if badkeeppatmatch:
                    for plist in active_plists:
                        # make sure the plist is a key in mod_plists
                        if plist in mod_plists:
                            for module in mod_plists[plist]:
                                self.add_error(242, module, f'#KEEP missing trailing # in {plist} - Pat {badkeeppatmatch.group(1)}')
                                if module not in errors:
                                    errors.append(module)
                patmatch = re.match(r'\s*Pat\s+(\w+);\s*(#KEEP#)?', line)
                if patmatch:
                    for plist in active_plists:
                        patstring = patmatch.group(1)
                        if(patmatch.group(2) == '#KEEP#'):
                            strings[plist]['keep'].append(patstring)
                        else:
                            strings[plist]['nokeep'].append(patstring)
                if re.search(r'\}', line):
                    active_plists.pop()
                    plistlevel -= 1
                    continue
                # print(f'plistlevel: {plistlevel} strings: {strings}')
        if len(errors) == 0:
            self.add_pass(242, 'ALL')
        # now go through the plists we actually care about, and see if they contain any patterns with both keep and nokeep
        for plist in valid_plists:
            # print(f'checking {plist}')
            # scan can have the same tid for multiple chunks - so need to compare full pattern. All other
            # modules should check tids instead of full patname since ttr is done on tids, not tuples
            for module in mod_plists[plist]:
                if 'SCN' in module:
                    for pat in strings[plist]['keep']:
                        if pat in strings[plist]['nokeep']:
                            # print(f'Holy Guacamole - Pat {pat} appears in plist {plist} with and without #KEEP#')
                            self.add_error(241, module, f'#KEEP# Pattern also appears without keep in {plist} - Pat {pat}')
                else:
                    for keeppat in strings[plist]['keep']:
                        keeptid = tid_from_pat(keeppat, False)
                        for nokeeppat in strings[plist]['nokeep']:
                            nokeeptid = tid_from_pat(nokeeppat, False)
                            if keeptid == nokeeptid:
                                # print(f'Holy Guacamole - TID {keeptid} appears in plist {plist} with and without #KEEP#')
                                self.add_error(241, module, f'#KEEP# TID also appears without keep in {plist} - TID {keeptid}')

                self.add_pass(241, module)


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    PListKeep(TestProgram(sys.argv[1]).pickle_init()).run()
