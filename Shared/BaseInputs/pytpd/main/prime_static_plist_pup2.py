#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Generate the static plist in coordination with Prime
Full plan: https://wiki.ith.intel.com/x/3Odsz

Usage:
prime_static_plist_pup2.py PTD_file tp.env output_folder
"""
from setenv import ROOT_ENV      # must be first in the imports
from gadget.gizmo import Elapsed
from gadget.errors import confirm
from gadget.strmore import str_index_expander
from gadget.files import File, TempDir
from gadget.tputil import remove_ip, OtplFile
from gadget.pylog import log
from gadget.disk import mkdirs
from tp.testprogram import TestProgram
from os.path import basename, exists, dirname
from collections import defaultdict
from pprint import pprint
import json
import sys
import re
import shutil


# Below is a simple way to inform user if they are python version <3.5. This is checked before any other code during the Parsing phase.
f'If you see SyntaxError, this means your python version is old. Pls upgrade to python3.8 minimum: http://python.org/downloads'


class StaticPlistPup:
    """
    Generate the static plist based on ptdfile
    Reason: PUP init time is causing VM mem swap, thus, make the plist static
    """

    def __init__(self, ptdfile, tpenv, destdir):
        self.tpenv = tpenv
        self.ptdfile = ptdfile
        self.tpobj = TestProgram(self.tpenv).init()     # do not pickle_init(), because of rename_incremental()
        # self.tpobj = TestProgram(self.tpenv).pickle_init()     # do not pickle_init(), because of rename_incremental()
        self.dest = destdir
        self.version = 'None'
        self.ptd = None                    # {patlist: {patterns_to_disable: list_of_occurrence}}
        self.meta = None                   # {patlist: {typename|stepname|functionality: value}}
        self.warnings = []                 # list of warnings
        self.short = defaultdict(list)     # {ip: list_of_lines}
        self.cnt_up = 0
        self.cnt_tot = 0
        mkdirs(self.dest)
        mkdirs(f'{self.dest}/debugref')

    def main(self):
        """Main Entry Point"""
        if self.tpobj.get_buildtype() == 'ENG_TP':
            return 1     # Do nothing for MV (Do not generate the POR_PUP folder)

        if exists(f'{self.tpobj.envdir}/InputFiles/No_Static_Prime_Pup2'):
            return 2

        # initialize
        sw = Elapsed()

        # First step: read the ptdfile
        self.read_ptdfile()
        File(self.ptdfile).copy(self.dest)       # Copy ptd file to output, since output plist depends on this file

        # Read each .plist
        for plist in sorted(self.tpobj.plists.get_plist_list()):
            ip = self.tpobj.get_plist2ip()[basename(plist)]
            self.process_plist(plist, ip)

        # Write the short plists per ip
        for ip in self.short:
            ipx = f'_{ip}' if ip else ''
            fname = f'pup_short_plists{ipx}.plist'
            self.short[ip].insert(0, 'Version 5.0;\n')
            File(f'{self.dest}/{fname}').rewrite(''.join(self.short[ip]), 'StaticPlistPup()')

        # Write the warnings in a file (report)
        self.warning(f'-i- Completed successfully in {sw}. Updated {self.cnt_up} of {self.cnt_tot} plists.')
        self.warning('')
        File(f'{self.dest}/report.txt').touch('\n'.join(self.warnings))

    def read_ptdfile(self):
        """Read the ptdfile and put in a data structure: self.ptd"""
        with open(self.ptdfile) as fh:
            data = json.load(fh)
        self.version = data['Version']
        assert len(data['ProcessTypes']) == 1, 'Tool only supports one process type. If >1, how is dir structure and env file?'
        ptd = data['ProcessTypes'][0]['PerPatlistPatternsToDisable']
        typename = data['ProcessTypes'][0]['Name']
        stepname = data['ProcessTypes'][0]['StepName']

        final = {}
        meta = {}
        for item in ptd:
            plb = remove_ip(item['Patlist'])
            functionality = item.get('Functionality', 'short')
            meta[plb] = {'typename': typename,
                         'stepname': stepname,
                         'functionality': functionality}

            final[plb] = {x['Pattern']: str_index_expander(x.get('Occurrence', '1')) for x in item['PatternsToDisable']}

        self.ptd = final
        self.meta = meta

        return final

    def process_plist(self, plist, ip):
        """Process one .plist"""

        print(f'Processing {plist}')

        # reformat first
        with TempDir(name=True) as tdir:
            tname = f'{tdir}/{basename(plist)}'
            File(plist).copy(tname)
            OtplFile(tname).reformat()
            final = File(tname).raw()

            # make a copy - Comment later
            File(tname).copy(f'{self.dest}/debugref/{basename(plist)}.orig')

        # process the plist
        self.cnt_tot += 1
        firstplb = sorted(self.meta)[0]     # used with non-existent
        patsplb = defaultdict(set)          # {plb: set of pats}
        displb = defaultdict(set)           # {plb: set of disabled pats}
        disabledpat = set()                 # {linenumbers} for disabled patterns
        disabledplb = set()                 # {linenumbers} for disabled plb
        toplines = set()                    # {linenumbers} of top level plb
        firstpat = {}                       # {plb: line_no}
        occur = {}                          # {plb: {pat: occurrence_cnt}}
        stack = []
        is_disable_flag = False             # top level disable flag
        for idx in range(len(final)):
            sline = final[idx].strip()

            if sline.startswith('{'):
                confirm(final[idx - 1].strip().startswith('GlobalPList'),
                        f'Error on [{final[idx - 1].strip()}]: Unexpected open bracket after this line!',
                        f'Error on {plist}. Pls check')

            if sline.startswith('GlobalPList'):
                plb = sline.split()[1]
                occur[plb] = defaultdict(int)
                stack.append(plb)
                if len(stack) == 1:
                    toplines = set()    # reset it
                    is_disable_flag = False

                # replace the name
                if plb in self.meta:
                    md = self.meta[plb]
                else:
                    md = self.meta[firstplb]
                newname = f'{plb}_{md["functionality"]}_{md["stepname"]}_{md["typename"]}'
                final[idx] = final[idx].replace(plb, newname)

            if stack:
                toplines.add(idx)

            if sline.startswith('}'):
                if len(stack) == 1:
                    if not is_disable_flag:
                        disabledplb.update(toplines)

                popped = stack.pop()
                plb = stack[-1] if stack else None

                # check if plb is empty
                # if len(patsplb[popped]) == len(displb[popped]) and len(patsplb[popped]) > 0:
                #     disabledpat.remove(firstpat[popped])    # put back firstpat

            if sline.startswith('Pat'):
                pat = sline.replace(';', ' ').split()[1]
                patsplb[plb].add(pat)
                if plb not in firstpat:
                    firstpat[plb] = idx       # save the firstpat

                for itemplb in stack:
                    occur[itemplb][pat] += 1
                    if pat in self.ptd.get(itemplb, []):
                        if occur[itemplb][pat] not in self.ptd[itemplb][pat]:
                            continue    # occurrence logic

                        if '#KEEP#' not in sline:

                            # Disable the pattern
                            displb[plb].add(pat)
                            disabledpat.add(idx)
                            is_disable_flag = True     # this is for top-level plb

        confirm(not stack, f'{plist} has issue: unmatched brackets', 'check this plist')

        if not disabledpat:
            self.cnt_up += 1     # This means that plist is unchanged, no disabled pat
            self.warning(f'-i- unchanged: {plist}')
            return

        # Create a shortened plist
        # prev = ''
        dbg = []
        for idx in range(len(final)):
            fstrip = final[idx].strip()
            if idx in disabledpat:
                continue
            if idx in disabledplb:
                continue
            if fstrip.startswith('Version '):   # Print this once
                continue

            # Don't know where below requirement came from, thus, commenting it out
            # if fstrip.startswith('PList ') and fstrip == prev:
            #     continue     # cannot do consecutive PList
            # if fstrip and (not fstrip.startswith('#')):     # not blank and not comment
            #     prev = fstrip

            dbg.append(final[idx])

        dbg = self.remove_empty(dbg)

        # Add it in short plist
        self.short[ip].append(f'# Source: {plist}\n')
        for line in dbg:
            self.short[ip].append(line)

        # debug only, comment this later
        File(f'{self.dest}/debugref/{basename(plist)}').rewrite(''.join(dbg), 'debug only process_plist()')

    @classmethod
    def remove_empty(cls, lines):
        """Remote empty lines"""
        final = []
        foundstack = []    # lowest leaf only
        empty = True
        foundone = False
        for line in lines:
            sline = line.strip()

            if sline.startswith('GlobalPList'):
                if foundstack:
                    final.extend(foundstack)
                foundstack = [line]
                empty = True
                continue

            if foundstack:
                foundstack.append(line)
                if sline.startswith(('{', '#')) or (not sline):
                    continue
                if sline.startswith('}'):
                    if empty:
                        foundone = True
                    else:
                        final.extend(foundstack)
                    foundstack = []
                    empty = True
                    continue
                empty = False

            else:
                final.append(line)

        if foundone:
            final = cls.remove_empty(final)

        return final

    def warning(self, msg):
        """Print the warning and add in a list to write later"""
        log.info(msg)
        self.warnings.append(msg)


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 4, f'Incorrect usage!\n\n{__doc__}'
    StaticPlistPup(sys.argv[1], sys.argv[2], sys.argv[3]).main()


# validation
# prime_static_plist_pup2.py /intel/ulat/pup/release/arl/ARLXXA1H75P10/1000/CLASS_U28G1_g/PAS_PTD.pup.json /intel/hdmxprogs/arl/ARLXXXXA1H75P10S429/POR_TP/Class_ARL_U28/EnvironmentFile.env /intel/tpvalidation/jqdelosr/75P_static_pup
# [done] feedback1: update code based on Slave reply
# [done] feedback2: arr_cdie_pbist_core_ks_scrf1_stf_all_CLASS_P28G1.plist  (There should be no consecutive "PList " line)
# [done] feedback3: more unittest cases
