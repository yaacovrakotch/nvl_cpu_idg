#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
auto IncrementCounter tool - updates .mtpl with correct counters

Usage:
    autocounter.py       # Process all .mtpl
    autocounter.py [Module/<mod>/<file.mtpl] [...] [-env <file.env>]
    autocounter.py [Module/<mod>/<file.mtpl] [...] [-env <file.env>] [-tp <secondtp.env>]
"""
from setenv import ROOT_ENV      # must be first in the imports
from gadget.gizmo import Elapsed, count_iter
from gadget.shell import SystemCall, CALLERBIN
from gadget.errors import ErrorInput, confirm, ErrorUser
from gadget.files import File
from gadget.vepargs import Args, TA_All, TA_StoreFile, TA_AppendSC
from gadget.dictmore import DictDot
from gadget.helperclass import OPT
from gadget.tputil import OtplFile
from gadget.pylog import log
from tp.testprogram import TestProgram
from tp.mtpl import BM
from os.path import exists, dirname, basename, realpath
from collections import defaultdict
from itertools import chain
from pprint import pprint
import re
import glob
import os


# Below is a simple way to inform user if they are python version <3.5. This is checked before any other code during the Parsing phase.
f'If you see SyntaxError, this means your python version is old. Pls upgrade to python3.8 minimum: http://python.org/downloads'


class MainArg(Args):   # parent: ArgsBase
    """
    Main wrap
    """

    def config(self):
        """
        Define the arguments for the script.
        The order below will matter, it is the order of display during help.
        """
        cfg = DictDot()
        cfg.all = TA_All('Specify which mtpl to update')
        cfg.env = TA_StoreFile('Specify path to tp env file (Primary Repo)', metavar='file.env')
        cfg.tp = TA_AppendSC('Specify path to secondary tp(s) env file. This can be multiple', metavar='file.env')
        return cfg

    def main(self):
        """
        Main entry point
        """
        # This is testing code for "use github as the database"
        if OPT.all and OPT.all[0] == 'test':    # pragma: no cover
            File('README.md').touch("Autocounter run\n")
            SystemCall('git add -A', disp=True).run(disp=True)
            SystemCall('git commit -m autocounter', disp=True).run(disp=True)
            SystemCall('git push', disp=True).run(disp=True)
            exit(1)   # Fail

        # Main tool run
        if OPT.env:
            tpenv = [OPT.env]
        else:
            tpenv = glob.glob('POR_TP/*/*.env')
            confirm(tpenv, f'No POR_TP/*/*.env found in {os.getcwd()}.', 'Where is the env file?')

        # check - make sure OPT.all is mtpl files
        for item in OPT.all:
            confirm(item.endswith('.mtpl'), f'Error: [{item}] is not .mtpl file', 'Expecting .mtpl file.')
            confirm(exists(item), f'Error: [{item}] does not exist', 'Expecting .mtpl file that exist')

        tpobj = TestProgram(tpenv[0])
        AutoCounter(tpobj).main(mtplfiles=OPT.all, secondarytp=OPT.tp)


class AutoCounter:
    """
    Auto Counter add
    See: https://wiki.ith.intel.com/x/CBUDz
    """

    def __init__(self, tpobj, is_check=False):
        """

        :param tpobj: testprogram object
        :param is_check: Set to True to validator/checker/gate mode
        """
        self.tpobj = tpobj
        self.nocounter = {}                   # {fname: [(dfi, port, bin8, is_pass, lno)] }
        self.counter_block = {}               # {fname: (lno_counter_line, lno_endbracket)}
        self.first_dig8 = {}                  # {fname: 8-digit-softbin}              # for counters w/o softbin
        self.all_counter = []                 # list of [8-dig, string, dfi, port, lno, bin8, is_pass, fname]    # for writing and duplicate removal
        self.registry = defaultdict(set)      # {hbsb: set_of_4_digit_cntr_string
        self.mtt_registry = set()             # set of 4-digit mtt counters (includes duplicates)
        self.mtt_duplicate = set()            # set of 4-digit mtt counters
        self.mtt_loc = defaultdict(dict)      # {fname: {write_lno: dig4|None, dfi, port}}
        self.del_counter = defaultdict(set)   # {fname: <set_of_lno>}
        self.varbin = None                    # "BinMatrix.bin" or "FlowMatrix.bin"
        self.bm = None                        # BM object from mtpl
        self.is_check = is_check              # True if check mode
        self.othertp = set()                  # {8-digit counter}
        self._check_file_prev = None          # Used by check_print()

    def main(self, mtplfiles=[], secondarytp=[]):
        """
        Main Entry point
        :param mtplfiles: list of mtpl files to process. If empty, process all
        :param secondarytp: List of secondary tp env files
        :return: (files_processed, count)
        """
        if self.tpobj.is_tos4:
            log.info('-i- AutoCounter() is not coded for TOS4 yet')
            return 1

        # Read all tp's first, populate self.othertp
        for tp in secondarytp:
            self.read_secondarytp(tp, mtplfiles)

        # Confirm first if this TP is enabled
        enable_file = f'{self.tpobj.envdir}/InputFiles/enable_autocounter.txt'
        if self.is_check and (not exists(enable_file)):
            log.info(f'-i- AutoCounter() check is skipped, since {enable_file} does not exist.')
            return -1

        # start ====
        log.info('-i- AutoCounter() routine is starting.')
        sw = Elapsed()
        ctr = 0
        files_cnt = 0
        setfiles = {realpath(x) for x in mtplfiles}

        # iterate to all .mtpl files, read all increment counters, put in data structure
        for ff in self.tpobj.get_all_mtpl_from_stpl():
            self.nocounter[ff] = self.read_counters(ff)

        # Process duplicates (after reading all mtpl)
        self.process_dup()

        # For each mtpl, add the increment counter and write it
        for ff in sorted(self.nocounter):
            data = self.process(ff)         # data = {lno: Counter_to_add}
            ctr += len(data)

            data_mtt, data_mttexist = self.process_mtt(ff)
            data.update(data_mtt)
            data.update(data_mttexist)
            ctr += len(data_mtt)

            files_cnt += self.write(ff, data, setfiles)

        # check mode
        if self.is_check and ctr:
            pathcmd = dirname(CALLERBIN)
            raise ErrorUser(f'{ctr} IncrementCounters need fixing (Either not unique or missing). Refer to log messages above for details.',
                            f'Pls run {pathcmd}/autocounter.py from root repo path to fix this problem.')

        # done
        log.info(f"-i- Success AutoCounter(). Files written: {files_cnt}, Counters processed: {ctr}, Elapsed {sw}. ")
        return files_cnt, ctr

    def read_counters(self, mtplfile):
        """
        Read each mtplfile and store in data structure
        """
        if mtplfile.endswith('.imp'):
            return None  # Do nothing for this file
        if 'ProgramFlowsTestPlan' in mtplfile:
            return None  # Do nothing for ProgramFlowsTestPlan, they don't have counters

        r_pass = re.compile(r'Property\s+PassFail\s*=\s*"Pass"')
        r_pass2 = re.compile(r'PassFail\s+Pass')
        r_special = re.compile(r'(Matrix\.bin|fail_FAIL_DPS_ALARM|fail_FAIL_SYSTEM_SOFTWARE)')
        r_bin = re.compile(r'SoftBins\.b(\d+)')
        r_mttctr = re.compile(r'(\w+\.bin)\s*\+\s*\"(\d+)')
        r_passfail_pass = re.compile(r'PassFail\s+Pass')
        r_ctr = re.compile(r'\b([a-z](\d+)_\w+)')
        r_trialtest = re.compile(r'TrialTest\s*\w+\s*([^#]+)')
        nocounter = []

        nest = 0
        bin8 = None
        dfi = None
        startresult = None
        counter = False
        mtt_counter = False
        write_lno = None
        counterblock = None
        ctr_add = None
        dfiti = None
        ismtt = False
        is_pass = False
        iwantcounter = True
        foundonce = False
        mtt_ti = set()
        dfitrial = None
        dutflows = set()

        for lno, line in OtplFile(mtplfile).readline(comments=True):
            if line.startswith('#'):
                if line.startswith('# No IncrementCounters'):
                    iwantcounter = False
                _ = None    # coverage
                continue    # skip comments

            if line == '{':
                nest += 1

            # closure
            elif line == '}':
                nest -= 1
                assert nest >= 0, f"Error: Unbalanced close bracket detected line#{lno} of {mtplfile}"

                if ctr_add:    # we need bin8, so this has to be add end bracket
                    self.all_counter.append([ctr_add[0], ctr_add[1], dfi, startresult, ctr_add[2], bin8, is_pass, mtplfile])

                if startresult and (not ismtt) and (not counter) and iwantcounter:
                    assert dfi, f"Error: No name found in lno#{lno} of {mtplfile}"
                    nocounter.append((dfi, startresult, bin8, is_pass, write_lno))

                if startresult and ismtt and (not mtt_counter):
                    assert dfi, f"Error: No name found in lno#{lno} of {mtplfile}"
                    self.mtt_loc[mtplfile][write_lno] = (None, dfitrial, startresult)

                if counterblock:
                    self.counter_block[mtplfile][1] = lno

                startresult = None     # Result is last level so it's ok to clear it always
                counter = False
                mtt_counter = False
                write_lno = None       # Assumed there is always Property
                counterblock = None
                ctr_add = None
                is_pass = False
                iwantcounter = True
                if nest == 1:
                    dfi = None
                    bin8 = None
                    dfitrial = None

            elif line.startswith('MultiTrialTest '):
                dfi = line.split()[1]
                dfiti = None
                mtt_ti.add(dfi)
                ismtt = True

            elif line.startswith(('TrialTest ', 'CSharpTrialTest ')):
                res = r_trialtest.search(line)
                assert res, f'TrialTest Regex failed for {line}'
                dfitrial = res.group(1)

            elif line.startswith(('DUTFlowItem ', 'FlowItem ')):
                dfi = line.split()[1]
                dfiti = line.split()[2]
                ismtt = False

            # in case where counter block does not exist
            elif line.startswith(('Test ', 'DUTFlow ', 'CSharpTest ')):
                if mtplfile not in self.counter_block:
                    self.counter_block[mtplfile] = [lno - 1, None]      # minus one indicating counter block does not exist
                if line.startswith('DUTFlow '):
                    dutflows.add(line.split()[1])

            elif line.startswith(('Result ', 'TrialResult ')):
                startresult = line.split()[1]
                counter = False       # Add counter by default
                if ismtt and startresult in ('-1', '-2'):
                    counter = True    # No counter needed for these two special ports
                foundonce = False

            elif line == 'Counters':
                counterblock = True
                self.counter_block[mtplfile] = [lno, None]

            # read all existing counters in counter block
            elif counterblock:
                self.registry[line[1:5]].add(line[5:9])      # hbsb = cntr

            # duplicate IncrementCounter - delete this and move on. Only read the first one.
            elif startresult and foundonce and line.startswith('IncrementCounters '):
                self.del_counter[mtplfile].add(lno)

            # inside the Result block
            elif startresult:

                # logic if counter needs to be added
                if not counter:
                    if line.startswith('IncrementCounters '):
                        counter = True       # counter not needed, it already exist
                    elif startresult and 'Property ' in line and r_pass.search(line):
                        counter = True       # counter not needed for pass
                    elif startresult and 'PassFail ' in line and r_pass2.search(line):
                        counter = True       # counter not needed for pass
                    elif startresult and 'SetBin ' in line and r_special.search(line):
                        counter = True       # counter not needed for special bins
                    elif dfiti in mtt_ti:
                        counter = True       # counter not needed for MultiTrial dfi
                    elif dfiti in dutflows:
                        counter = True       # counter not needed for Composites

                # get the 8-digit bin
                if line.startswith('SetBin ') and (not r_special.search(line)):
                    res = r_bin.search(line)
                    assert res, f"Error: Invalid SetBin: [{line}] of line#{lno} of {mtplfile}"
                    if mtplfile not in self.first_dig8:
                        self.first_dig8[mtplfile] = res.group(1)
                    if not bin8 or startresult == '0':
                        bin8 = res.group(1)

                if line.startswith(('Property ', 'PassFail ')):
                    write_lno = lno
                    if r_passfail_pass.search(line):
                        mtt_counter = True     # Do not add Increment Counter for mtt pass port
                    if r_pass.search(line) or r_pass2.search(line):
                        is_pass = True

                if line.startswith('TrialAction '):
                    write_lno = lno

                # mtt counter logic
                if line.startswith('IncrementCounters ') and ismtt:
                    write_lno = lno
                    res = r_mttctr.search(line)
                    confirm(res, f'Error on {mtplfile} line: {line}', 'IncrementCounters is not using standard mtt Counter')
                    if not self.varbin:
                        self.varbin = res.group(1)
                    dig4 = res.group(2)
                    if dig4 in self.mtt_registry:
                        self.mtt_duplicate.add(dig4)
                    else:
                        self.mtt_registry.add(dig4)
                    self.mtt_loc[mtplfile][write_lno] = (dig4, dfitrial, startresult)
                    mtt_counter = True

                # non-mtt case
                if line.startswith('IncrementCounters ') and (not ismtt):
                    foundonce = True
                    if dfiti in mtt_ti:
                        # mtt dfi - remove it
                        self.del_counter[mtplfile].add(lno)
                    else:
                        # Normal case, register it
                        res = r_ctr.search(line)
                        if res:
                            dig8 = res.group(2)
                            if len(dig8) == 8:
                                ctr_add = (dig8, res.group(1), lno)
                            else:
                                counter = False     # Force write increment counter since it is wrong
                                self.del_counter[mtplfile].add(lno)
                        else:
                            counter = False     # Force write increment counter since it is wrong
                            self.del_counter[mtplfile].add(lno)

        # In case where no SetBin is found
        if mtplfile not in self.first_dig8:
            self.first_dig8[mtplfile] = '00010000'

        return nocounter

    def process_dup(self):
        """
        Process all duplicate counters based on self.all_counter.
        Update self.all_counter, self.del_counter and self.nocounter

        # self.all_counter.append([dig8, res.group(1), dfi, startresult, lno, bin8, is_pass, mtplfile])
        # self.del_counter[mtplfile].add(lno)
        # nocounter.append((dfi, startresult, bin8, is_pass, write_lno))
        :return: None
        """
        # get dups first
        dups = defaultdict(list)    # {dig8: list_of_idx}
        for idx, elems in enumerate(self.all_counter):
            dig8 = elems[0]
            dups[dig8].append(idx)

        # process it
        for dig8 in sorted(dups):
            if len(dups[dig8]) > 1:
                for idx in dups[dig8]:
                    _, _, dfi, port, lno, bin8, is_pass, fname = self.all_counter[idx]
                    self.nocounter[fname].append((dfi, port, bin8, is_pass, lno))      # Add a new counter
                    self.del_counter[fname].add(lno)    # Do not print this in .mtpl
                    self.all_counter[idx][1] = None     # Do not print it in headers

    def process_mtt(self, fname):
        """
        Process this particular mtpl given data structure for mtt

        self.mtt_registry = set()             # set of 4-digit mtt counters (includes duplicates)
        self.mtt_duplicate = set()            # set of 4-digit mtt counters
        self.mtt_loc = defaultdict(dict)      # {fname: {write_lno: dig4|None, dfi, port}}

        :param fname:
        :return: modify {lno: Counter_to_add}, everything {lno: Counter_to_add}
        """
        if fname not in self.mtt_loc:
            return {}, {}  # normal counter update only

        data = {}
        datx = {}
        for lno, struct in self.mtt_loc[fname].items():
            dig4, dfi, port = struct
            if port in ('-1', '-2') and dig4 is None:
                continue    # Do not add if there is no increment counter here

            if dig4 is None or dig4 in self.mtt_duplicate:
                number = self.new_mtt(port)
                data[lno] = f'{number}_fail_" + {dfi} + "_{port.replace("-", "m")}'     # mtt counter format
            else:
                number = dig4     # re-write the line so it shows up in counter header
                datx[lno] = f'{number}_fail_" + {dfi} + "_{port.replace("-", "m")}'     # mtt counter format

        return data, datx

    def new_mtt(self, port):
        """Return a new 4 digit mtt counter"""
        port_digit = port[-1]
        for i in range(1000):
            targ = f'{i:03}{port_digit}'
            if f'1001{targ}' in self.othertp:      # already used in other tp. Yes, 1001 is hardcoded
                continue
            if targ not in self.mtt_registry:
                self.mtt_registry.add(targ)
                return targ

        for i in range(10000):
            targ = f'{i:04}'
            if f'1001{targ}' in self.othertp:      # already used in other tp. Yes, 1001 is hardcoded
                continue
            if targ not in self.mtt_registry:
                self.mtt_registry.add(targ)
                return targ

        raise ErrorInput(f'All 10K counters are exhausted for multitrial speedflow.',
                         'Pls reduce MultiTrial tests.')

    def process(self, fname):
        """
        Process this particular mtpl given data structure

        nocounter[(dfi, startresult)] = (bin8, write_lno)

        :param fname:
        :return: {lno: Counter_to_add}
        """
        if not self.nocounter[fname]:
            return {}   # mtt update only

        confirm(fname in self.first_dig8,
                f'Error: No SetBin found {fname}',
                'At least one SetBin is required, so that there is a reference hbsb to use in auto-counters')

        data = {}
        for dfi, port, bin8, is_pass, lno in self.nocounter[fname]:
            port_digit = port[-1]
            if bin8:
                hbsb = bin8[-4:]
            else:
                hbsb = self.first_dig8[fname][-4:]

            if is_pass:
                hbsb = f'99{hbsb[0:2]}'

            # get cntr which is the first uniq one for this hbsb
            registered = self.registry.get(hbsb, set())
            for target in range(1000):   # max of 999
                cntr = f'{target:03}{port_digit}'
                if f'{hbsb}{cntr}' in self.othertp:      # already used in other tp
                    continue
                if cntr not in registered:
                    registered.add(cntr)
                    break   # found one
            else:
                for target in range(10000):      # max of 9999
                    cntr = str(target).zfill(4)
                    if f'{hbsb}{cntr}' in self.othertp:      # already used in other tp
                        continue
                    if cntr not in registered:
                        registered.add(cntr)
                        break
                else:
                    raise ErrorInput(f'All counters are exhausted for hbsb={hbsb}',
                                     'Pls update SetBin of some instances to different hbsb')

            self.registry[hbsb] = registered     # save it

            # HBSBCNTR
            number = f'{hbsb}{cntr}'     # bin8 is 90HBHBSB
            assert len(number) == 8, 'Error: expecting 8-digit: [{number}]. hbsb={hbsb}, cntr={cntr}'

            if is_pass:
                # although we are not automatically writing pass port, this is needed for existing pass port counters where it is duplicate
                data[lno] = f'p{number}_pass_{dfi}_{port.replace("-", "m")}'
            else:
                # n<number>_fail_<keyname>_<port>
                data[lno] = f'n{number}_fail_{dfi}_{port.replace("-", "m")}'

        return data

    def check_print(self, line1, line2, lno, fname, is_append):
        """
        :param line1: Main line to print (or old line)
        :param line2: new line
        :param lno: line number
        :param fname: mtpl filename
        :param is_append: Set to True to append
        :return: None
        """
        if line1.strip() == line2.strip():
            return    # Nothing to print

        if self._check_file_prev != fname:
            log.info('')
            log.info(f'File: {basename(dirname(fname))}/{basename(fname)}')
            self._check_file_prev = fname

        if is_append:
            keyword = 'append'
        else:
            keyword = 'update'
        prev = f'line#{lno}'
        new = '%s%s' % (keyword, ''.zfill(len(prev) - 6).replace('0', ' '))
        log.info(f'   {prev}: {line1.strip()}')
        log.info(f'   {new}: {line2.strip()}')

    def add_header(self, final, data, module, fname):
        """
        Add the header lines
        :param final:
        :return:
        """
        everything = set()

        # add the processed counters
        for _item in sorted(data.values()):
            for item in self.counter_name_expand(_item, module):
                everything.add(item)

        # add the rest of the existing counters
        for elems in sorted(self.all_counter, key=lambda x: x[0]):
            if elems[-1] == fname:
                if elems[1]:
                    everything.add(elems[1])

        # Create the block
        final.append('Counters\n')
        final.append('{\n')

        for item in sorted(everything):
            final.append(f'        {item},\n')

        final[-1] = f'{final[-1][:-2]}\n'    # remove comma on previous line
        final.append('}\n')

    def write(self, fname, data, setfiles):
        """
        Write one mtpl file

        :param fname: Target filename
        :param data: {lno: <counter_to_add>}
        :param setfiles: <set_of_realpath>
        :return: None
        """
        if not data:
            return 0   # nothing to write
        if setfiles and realpath(fname) not in setfiles:
            return 0   # nothing to write, skip this file

        confirm(fname in self.counter_block,
                f'Error: Counters block is not found in {fname}',
                'Counters block must be defined with at least one element.')
        if not self.varbin:
            self.varbin = 'FlowMatrix.bin'    # default

        allraw = File(fname).raw()
        final = []
        module = None
        counter_block_start = False
        for lno, line in enumerate(allraw, start=1):
            # part1 - header
            if lno == self.counter_block[fname][0]:    # this is counter block start
                if self.counter_block[fname][1] is not None:
                    counter_block_start = True
                self.add_header(final, data, module, fname)

            if counter_block_start:
                if lno == self.counter_block[fname][1]:
                    counter_block_start = False
                _ = None     # For coverage
                continue     # Skip the entire block

            # normal lines
            if lno in self.del_counter[fname]:
                final.append('\n')
            else:
                final.append(line)

            if line.strip().startswith('TestPlan '):
                module = line.strip().split()[1].replace(';', '')

            # part2 - Counter lines - Add & Replace
            if lno in data:
                if data[lno].startswith(('n', 'p')):
                    increment_counter = f'IncrementCounters {module}::{data[lno]};'
                else:
                    increment_counter = f'IncrementCounters {self.mtt_name(data[lno], module)};'

                is_append = False
                if '}' in line:     # same line
                    if 'TrialAction ' in final[-1]:
                        final[-1] = re.sub('(TrialAction(.*?);)', rf'\1 {increment_counter}', final[-1])
                    else:
                        final[-1] = re.sub('(Property(.*?);)', rf'\1 {increment_counter}', final[-1])

                elif 'Property' in line and ('GoTo ' in line or 'Return ' in line):
                    # odd case found in ARL TP: Both Propert and Goto|Return are in same line. So insert it in middle.
                    final[-1] = re.sub('(Property(.*?);)', rf'\1 {increment_counter} ', final[-1])

                else:
                    full_line = f'                        {increment_counter}\n'
                    if line.strip().startswith('IncrementCounters'):
                        final[-1] = full_line      # replace
                    else:
                        is_append = True
                        final.append(full_line)    # append

                self.check_print(line, final[-1], lno, fname, is_append)

        # Write it
        if self.is_check:
            is_written = 0
        else:
            is_written = File(fname).rewrite(''.join(final), 'AutoCounter.write()')

        return int(is_written)

    def mtt_name(self, item, module):
        """Return the mtt counter name (expression"""
        return f'"{module}::n" + {self.varbin} + "{item}"'

    def counter_name_expand(self, item, module):
        """Return the counter name taking into consideration mtt"""
        if item.startswith(('n', 'p')):
            yield item     # return as-is for non-mtt counters
            return

        if not self.bm:
            self.bm = BM(self.tpobj).init()

        counter = f'SetBin {self.mtt_name(item, module)}'
        for line in self.bm.expand(counter):
            line = line[7:]                # remove SetBin (for expand)
            line = line.split('::')[-1]    # Remove module
            yield line

    def _dutflow_without_counters(self):      # pragma: no cover - validation only
        allnames = set()
        robj = re.compile(r'^DUTFlowItem\s+(\w+)')
        for ff in self.tpobj.get_all_mtpl_from_stpl():
            for line in File(ff).raw():
                line_strip = line.strip()
                res = robj.search(line_strip)
                if res:
                    allnames.add(res.group(1))

            # Call db (per module)
            sw = Elapsed()
            result = DataHost().central('autocounter', allnames, check=True)
            print(basename(ff), len(allnames), len(result), sw)
            exit(0)

    def read_secondarytp(self, tpenv, mtpls):
        """Read secondarytp and assign to self.othertp"""
        confirm(mtpls,
                "Error: Secondary tp (-tp) only works if mtpls are provided",
                "Pls provide specific mtpl to update")
        r_ctr = re.compile(r'\b([a-z](\d+)_\w+)', re.MULTILINE)
        set_mtpl = {basename(ff) for ff in mtpls}

        tpobj = TestProgram(tpenv)
        for ff in tpobj.get_all_mtpl_from_stpl():
            if basename(ff) in set_mtpl:
                continue    # Don't process this file
            if not ff.endswith('.mtpl'):
                continue
            otpl = OtplFile(ff)
            text = ''.join(list(otpl.get_block('Counters')))
            for ctr in r_ctr.findall(text):
                self.othertp.add(ctr[1])

        print(f'-i- Total secondary counters from other tp: {len(self.othertp)}')


if __name__ == '__main__':  # pragma: no cover
    MainArg(desc=__doc__).main()
