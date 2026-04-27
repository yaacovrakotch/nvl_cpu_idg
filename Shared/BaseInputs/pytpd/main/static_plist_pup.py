#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Generate the static plist

Usage:
static_plist_pup.py path_to_tp path_to_ptd
"""
from setenv import ROOT_ENV      # must be first in the imports
from gadget.gizmo import Elapsed
from gadget.errors import confirm
from gadget.disk import mkdirs, chmodr
from gadget.files import File
from gadget.tputil import remove_ip, OtplFile
from gadget.pylog import log
from tp.testprogram import TestProgram
from os.path import basename, exists, dirname
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
    # file and instance name to modify for version
    VERSION_MTPL_FILE = 'Modules/TPI_BASE_XXX/TPI_BASE_XXX.mtpl'
    VERSION_INSTANCE = 'CTRL_X_PUP_K_START_X_X_X_X_PUPREV'

    # Below are list of SRH subflows. The rest will be PUP enabled.
    SUBFLOWS = '''
DUTFlow SATF1_SubFlow
DUTFlow SATF2_SubFlow
DUTFlow SATF3_SubFlow
DUTFlow SATF4_SubFlow
DUTFlow SATF5_SubFlow
DUTFlow SATF6_SubFlow
DUTFlow SCHDCF1_SubFlow
DUTFlow SCLRF1_SubFlow
DUTFlow SCLRF2_SubFlow
DUTFlow SCLRF3_SubFlow
DUTFlow SCLRF4_SubFlow
DUTFlow SCLRF5_SubFlow
DUTFlow SCLRF6_SubFlow
DUTFlow SCRF1_SubFlow
DUTFlow SCRF2_SubFlow
DUTFlow SCRF3_SubFlow
DUTFlow SCRF4_SubFlow
DUTFlow SCRF5_SubFlow
DUTFlow SCRF6_SubFlow
DUTFlow SGTF1_SubFlow
DUTFlow SGTF2_SubFlow
DUTFlow SGTF3_SubFlow
DUTFlow SGTF4_SubFlow
DUTFlow SGTF5_SubFlow
DUTFlow SGTF6_SubFlow
DUTFlow SSHDCF1_SubFlow
DUTFlow SSNF1_SubFlow
DUTFlow SSNF2_SubFlow
DUTFlow SSNF3_SubFlow
'''

    def __init__(self, tpenv, ptdfile):
        self.tpenv = tpenv
        self.ptdfile = ptdfile
        self.tpobj = TestProgram(self.tpenv).init()     # do not pickle_init(), because of rename_incremental()
        # self.tpobj = TestProgram(self.tpenv).pickle_init()     # do not pickle_init(), because of rename_incremental()
        self.dest = f'{self.tpobj.tpldir}/Shared/BaseInputs/Supersedes/POR_PUP'
        self.bom = basename(dirname(ptdfile))
        # self.dest = f'{self.tpobj.tpldir}/../POR_PUP'   # debug only
        self.version = 'None'
        self.ptd = None        # {patlist: {set_of_patterns_to_disable}}
        self.warnings = []     # list of warnings
        self.found = set()     # set of found patlist
        self.used = set()      # set of used patlist in TP
        self.reenabled = {}    # {patlist: pat_line}     # dictionary of re-enabled patlist
        self.cnt_up = 0
        self.cnt_tot = 0

    def main(self):
        """Main Entry Point"""
        if self.tpobj.get_buildtype() == 'ENG_TP':
            return 1     # Do nothing for MV (Do not generate the POR_PUP folder)

        if exists(f'{self.tpobj.envdir}/InputFiles/No_Static_Hybrid_Pup'):
            return 2

        # initialize
        sw = Elapsed()
        File(self.dest).rename_incremental()
        mkdirs(self.dest, mode='02775')
        mkdirs(f'{self.dest}/orig', mode='02775')

        # First step: read & update ptd file
        srh_patlist = self.get_srh_patlist()
        self.read_ptdfile(srh_patlist)

        # Get all connected patlists bypassed and unbypassed
        for mod, tname, dd, _ in self.tpobj.mtpl.iter_tests(key_name='patlist', edict=True):
            self.used.add(remove_ip(dd['patlist']))

        # Write each .plist
        for plist in sorted(self.tpobj.plists.get_plist_list()):
            self.process_plist(plist)

        # Check that all plists are found
        for plb in self.ptd:
            if plb not in self.found:
                self.warning(f'-w- [{plb}] is not found for this TP')     # cannot find case because of hybrid model

        # Update the version in mtpl
        self.update_version()
        self.copy_npr(srh_patlist)

        self.copy_parallel(self.dest, self.bom)

        # Write the warnings in a file (report)
        # pprint(self.reenabled)
        self.warning(f'-i- Total of {len(self.reenabled)} reenabled patlists with single pat')
        self.warning(f'-i- Completed successfully in {sw}. Updated {self.cnt_up}/{self.cnt_tot} plists.')
        self.warning('')
        File(f'{self.dest}/report.txt').touch('\n'.join(self.warnings))

    @classmethod
    def copy_parallel(cls, destdir, bom):
        """
        Copy destdir/<folder> to <folder_g> or viceversa
        :param destdir: /path/POR_PUP
        :param bom: bom folder
        :return:
        """
        if bom.endswith('_g'):
            target = bom[:-2]
        else:
            target = f'{bom}_g'
        shutil.copytree(f'{destdir}/{bom}', f'{destdir}/{target}')
        chmodr(f'{destdir}/{target}', '0775')

    def copy_npr(self, srh):
        """Copy the npr files and update the other file"""
        # Copy this file as-is
        File(f'{dirname(self.ptdfile)}/NPRCriteriaFile.csv').copy(f'{self.dest}/{self.bom}')

        # Modify NPRInputFile.csv: remove the SRH patplist
        final = []
        lines = File(f'{dirname(self.ptdfile)}/NPRInputFile.csv').raw()
        for line in lines:
            elems = line.rstrip().split(',')
            if len(elems) > 1:
                plb = elems[1]
                if plb in srh:
                    continue   # skip srh since this is already static
            final.append(line)
        File(f'{self.dest}/{self.bom}/NPRInputFile.csv').touch(''.join(final), newfile=True)

    def update_version(self):
        """Update the version in mtpl"""
        self.version = self.version.replace('.', '').replace('-', '').replace('+', '')
        confirm(re.search(r"^\w+$", self.version), f'[{self.version}] has special characters', 'pls fix')
        mtpl_input = f'{self.tpobj.tpldir}/{self.VERSION_MTPL_FILE}'
        dummyinstance = self.VERSION_INSTANCE
        replacement = f'{dummyinstance}_{self.version}'
        confirm(exists(mtpl_input), f'{mtpl_input} does not exist', 'This file is required for revision')
        lines = File(mtpl_input).raw()
        found = False
        for idx in range(len(lines)):
            if dummyinstance in lines[idx]:
                if replacement in lines[idx]:
                    return    # Do nothing, it is already replaced

                lines[idx] = lines[idx].replace(dummyinstance, replacement)
                found = True

        if not found:
            self.warning(f'-w- dummy instance is not found [{dummyinstance}] for version update')
        File(mtpl_input).rewrite(''.join(lines), 'update_version()')

    def read_ptdfile(self, srh):
        """Read the ptdfile and put in a data structure: self.ptd"""
        with open(self.ptdfile) as fh:
            data = json.load(fh)
        self.version = data['Version']
        assert len(data['ProcessTypes']) == 1, 'Tool only supports one process type. If >1, how is dir structure and env file?'
        ptd = data['ProcessTypes'][0]['PerPatlistPatternsToDisable']

        final = {}
        for item in ptd:
            plb = remove_ip(item['Patlist'])
            if plb in srh:    # SRH only
                final[plb] = {x['Pattern'] for x in item['PatternsToDisable']}

        self.ptd = final

        # update the ptd file
        new = []
        for item in ptd:
            plb = remove_ip(item['Patlist'])
            if plb not in srh:
                new.append(item)
        data['ProcessTypes'][0]['PerPatlistPatternsToDisable'] = new
        mkdirs(f'{self.dest}/{self.bom}', mode='02775')
        dest = f'{self.dest}/{self.bom}/{basename(self.ptdfile)}'
        File(self.ptdfile).copy(f'{self.dest}/orig')    # Make a copy
        print(f'Writing: {dest}')
        with open(dest, 'w') as fh:
            json.dump(data, fh, indent=3)

        return final

    def warning(self, msg):
        """Print the warning and add in a list to write later"""
        log.info(msg)
        self.warnings.append(msg)

    def process_plist(self, plist):
        """Process one .plist"""
        File(plist).copy(f'{self.dest}/orig')      # Make a copy of the original for easy diff later
        File(plist).copy(self.dest)                # So we will just rewrite it
        nplist = f'{self.dest}/{basename(plist)}'
        final = File(nplist).raw()
        orig = list(final)    # make a copy
        self.cnt_tot += 1

        active = None
        disabled = set()
        stack = []
        stack_lno = {}
        updated_lines = []
        for idx in range(len(final)):
            sline = final[idx].strip()
            confirm(not sline.startswith('{'), 'Invalid .plist file. Start brachet at start of line is not allowed', 'Fix .plist')

            if sline.startswith('GlobalPList'):
                plb = sline.split()[1]
                stack.append(plb)
                stack_lno[plb] = idx
                if plb in self.ptd:

                    if active:
                        uniqleaf = len(self.ptd[plb] - self.ptd[active])
                        if uniqleaf:
                            self.warning(f'-w- double active. Ignoring leaf. uniq_in_leaf: {uniqleaf}. leaf: {plb}: {len(self.ptd[plb])} -vs- parent: {active} : {len(self.ptd[active])}')
                    else:
                        disabled = set()
                        active = plb
                    self.found.add(plb)

            if sline.startswith('}'):
                popped = stack.pop()

                # comment the block if empty
                self.empty_plist(final, stack_lno[popped], idx, active, basename(plist), updated_lines)
                updated_lines = []
                del stack_lno[popped]

                # Do check for disabled patterns
                if active and active == popped:
                    for pat in self.ptd[active]:
                        if pat not in disabled:
                            self.warning(f'-w- [{active}] does not have {pat}, but pat is in PTD file')
                    active = None
                    disabled = set()

            if sline.startswith('Pat') and active:
                pat = sline.replace(';', ' ').split()[1]
                if pat in self.ptd[active]:

                    if '[Skip]' not in final[idx]:
                        final[idx] = final[idx].replace(';', ' [Skip];')    # disable it
                        updated_lines.append(idx)

                    # final[idx] = f'# {final[idx].rstrip()} {active}\n'
                    disabled.add(pat)

        confirm(not stack, f'{plist} has issue: unmatched brackets', 'check this plist')
        confirm(not stack_lno, f'logic error: stack_lno is not empty on {plist}', 'check stack_lno logic')
        confirm(not active, f'plist {nplist} is still active at end. Why?', 'pls check logic')

        # write it
        if orig != final:
            self.cnt_up += 1
        File(nplist).rewrite(''.join(final), 'StaticPlistPup()')

    def empty_plist(self, final, lno_start, lno_end, active, fname, updated_lines):
        """
        If plist block is all skip, then Uncomment first pattern that was skipped
        Cannot have empty plist block
        """
        for idx in range(lno_start + 1, lno_end):
            sline = final[idx].strip()
            if sline.startswith('#'):
                continue
            if not sline:
                continue
            if '[Skip]' in sline:
                continue
            return     # It is not empty, thus do nothing

        # At this point, the block is empty. Get the plb name
        sline = final[lno_start].strip()
        confirm(sline.startswith('GlobalPList'), 'starting line does not start with GlobalPlist', f'sline: {sline}')
        plb = sline.split()[1]

        # Check if this plb is used by tp. If so, cannot disable and re-enable disabled pattern
        if plb in self.used:
            confirm(updated_lines, f'[{plb}] on {fname} does not have disabled Pats and it is empty', 'pls check.')
            final[updated_lines[0]] = final[updated_lines[0]].replace(' [Skip]', '')
            self.reenabled[plb] = final[updated_lines[0]]
            return

        # ASSUMPTION: PTD cannot disable all, since globalplist cannot be empty
        # Thus check this assumption: The plb being disabled (empty) should not be the active one.
        confirm(plb != active, f'ERROR: [{plb}] on {fname} is empty', 'Cannot disable all patterns in the plist.')

    def get_srh_patlist(self):
        """
        Return srh patlist
        :return dict: {patlist: info}
        """
        subflows = {x for x in self.SUBFLOWS.split()}
        subflows.remove('DUTFlow')

        # Get SRH patlists
        patlists = {None: None}
        i2s = self.tpobj.mtpl.get_instance_to_subflows()    # i2s - instance to subflows
        for key in i2s:
            mod, ins = key
            if i2s[key] & subflows:   # match, this mod+ins is a SRH
                dd = self.tpobj.mtpl.get_instance(mod, ins, evaluated=True)
                assert ':' not in dd.get('patlist', ''), f'expecting no IP for patlist in {mod}::{ins}'
                patlists[dd.get('patlist')] = f'{ins} {sorted(i2s[key])}'
        del patlists[None]

        # Determine if there is SRH vs CLR cross contamination (based on subflows)
        for mod, tn, dd, _ in self.tpobj.mtpl.iter_tests(key_name='patlist'):
            plb = dd['patlist']
            if plb in patlists:
                sf = i2s[(mod, tn)]
                if not (sf & subflows) and 'MAIN' in sf:
                    print(f'Cross Contamination: {plb}:\n    {patlists[plb]}\nvs: {tn} {sorted(sf)}')
                    self.warning(f'-w- Cross contamination: {plb} at {patlists[plb]} vs {tn} {sorted(sf)}')
                    del patlists[plb]     # remove the dirty patlist

        return patlists


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 3, f'Incorrect usage!\n\n{__doc__}'
    StaticPlistPup(sys.argv[1], sys.argv[2]).main()
