#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Strategy:
1. This script is called from torch_postproc.py by default.
2. This script is run from windows since it calls TRC. Unix call will "do nothing".
3. If TRACE executable fails, then it will still proceed, torch_postproc.py will give large warning.
4. If there are TRC errors, then this script will raise Exception

Usage:
cd <tp path where BaseTestPlan.tpl is>
trace_trc_torch.py
"""
import setenv      # must be first in the imports
import re
import glob
from gadget.errors import ErrorUser
from gadget.printmore import PrintAlign
from gadget.files import File
from gadget.pylog import log
from gadget.shell import SystemCall, IS_UNIX, IS_WIN
from gadget.disk import mkdirs
from mod.setting import cfg
from os.path import dirname, abspath, exists, basename


class TraceTrc:

    def __init__(self):
        self.msgstr = []          # loginfo message dictionary dump area
        self.ignore_msgstr = []  # loginfo message dictionary for ignored errors
        self.chksumrpt = 'Reports/FULL_TRC_Report.txt'  # this is the TRC table-format report
        self.wep_count = {'w': 0, 'e': 0, 'p': 0}
        self.trc_sumry = {}
        self.warninglist = set()   # set of (mod, msg) to become warning
        self.stpldir = None

    def _read_ignore_trc(self):
        """
        A special file, "ignore_trc.csv" located in .stpl folder is used to ignore known errors for the time being
        Read the ignore_trc.csv file, if exist and store it as a set
        """
        targ = f'{self.stpldir}/ignore_trc.csv'
        if not exists(targ):
            return   # Do nothing if this file does not exist

        line_re = re.compile(r'(\w+),(\w*),(\w+),(.*)')
        with open(targ, 'r') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                ts = line_re.search(line)
                assert ts, f'Trace line [{line}] is invalid. Pls check'
                mod = ts.group(2)
                msg = ts.group(4)
                if not mod or mod == 'Module':
                    _ = None     # coverage only
                    continue
                self.warninglist.add((mod, msg))

    def trcout_check(self, trcf):
        """
        Checks if there are TRACE TRC violations given the trace_report*.csv

        :param trcf: Input tracefile.csv
        :return: None
        """
        self.stpldir = dirname(trcf)
        self._read_ignore_trc()
        self._readfile(trcf)
        self._write(self._table_summary())

        # relocate trc_report* files before exiting
        File(trcf).move(f'{self.stpldir}/Reports', overwrite_rename=True)

        # Exit if there are errors
        self._final_exit()

    def _readfile(self, trcf):
        """

        :param trcf: Input file
        :return:
        """
        # Skip these lines
        skip_list = ['Scrum,Module',
                     'Module name does not follow the naming conventions'     # ignore this case as module name is checked in the checkers.py
                     ]

        # These are warnings
        warn_list = ['TESTPLANENDFLOW',
                     'XSD schema definition',
                     'No bin assigned in kill instance',
                     'Referenced UserVar is not defined',
                     'Plist is not found',      # P28 problem since TRC is not evaluating bom rules correctly
                     ]

        line_re = re.compile(r'(\w+),(\w*),(\w+),(.*)')
        skip_re = re.compile('(' + '|'.join(skip_list) + ')')
        warn_re = re.compile('(' + '|'.join(warn_list) + ')')

        with open(trcf, 'r') as file:

            for line in file:
                line = line.strip()
                if skip_re.search(line) or (not line):
                    continue
                ts = line_re.search(line)
                assert ts, f'Trace line [{line}] is invalid. Pls check'
                grp = ts.group(1)
                mod = ts.group(2)
                msg = ts.group(4)

                if not mod:    # ignore no modules
                    continue

                if grp not in self.trc_sumry:
                    self.trc_sumry[grp] = {}

                if mod not in self.trc_sumry[grp]:
                    self.trc_sumry[grp][mod] = {'w': 0, 'e': 0, 'p': 0}

                # hardcoded list of errors to ignore (become warning)
                if (mod, msg) in self.warninglist:
                    self.ignore_msgstr.append('%s -Warning101- TRC [module ignored]: msg=%s' % (mod, msg))
                    self.trc_sumry[grp][mod]['w'] += 1
                    self.wep_count['w'] += 1

                # warnings
                elif warn_re.search(line):
                    self.ignore_msgstr.append('%s -Warning102- TRC [test ignored]: msg=%s' % (mod, msg))
                    self.trc_sumry[grp][mod]['w'] += 1
                    self.wep_count['w'] += 1

                # errors
                else:
                    self.msgstr.append('%r -Error101- msg=%s' % (mod, msg))
                    self.trc_sumry[grp][mod]['e'] += 1
                    self.wep_count['e'] += 1

    def _table_summary(self):
        """Get table summary"""
        out = ['TRC Report:']
        pa = PrintAlign(rjust=False)
        pa('Team', 'Module', '[P]ass', '[W]arning', '[E]rror')

        for grp in sorted(self.trc_sumry):
            for mod in sorted(self.trc_sumry[grp]):
                wep = self.trc_sumry[grp][mod]
                pa(grp, mod, wep['p'], wep['w'], wep['e'])

        for item in pa.get_result():
            out.append(item)

        # No TRC error scenario
        if self.wep_count['e'] == 0:
            out.append('NO ERROR, TRACE TRC PASSED!')
            out.append('')
        return out

    def _write(self, out):
        """Write out"""
        out.append('')
        out.append('')
        out.append('Flagged Errors Message Stream')
        out.append('=============================')
        out.extend(f' {idx+1}. {line}' for idx, line in enumerate(sorted(self.msgstr)))
        out.append('')

        log.info('\n'.join(out))

        # Below just write in file, not in screen
        out.append('Ignored Errors Message Stream')
        out.append('=============================')
        out.extend(f' {idx+1}. {line}' for idx, line in enumerate(sorted(self.ignore_msgstr)))
        out.append('')

        log.info('Total Ignored Errors (aka, Warnings): %s' % len(self.ignore_msgstr))
        log.info('')

        mkdirs(f'{self.stpldir}/{dirname(self.chksumrpt)}')
        File(f'{self.stpldir}/{self.chksumrpt}').rewrite('\n'.join(out), "TraceTrc()")

    def _final_exit(self):
        if self.wep_count['e'] != 0:
            raise ErrorUser('There are TRC errors!',
                            f'Check {self.stpldir}/{self.chksumrpt}')

    def main(self):
        """
        Main routine. Will invoke TRACE TRC.

        :return: True for failure
        """
        stpls = glob.glob('*TP/*/*.stpl')
        assert stpls, 'No stpl found in [*TP/*/*.stpl]. Are you in root tpl directory?'
        is_error = False

        stpl_paths = set()
        for stpl_item in stpls:
            stpl_paths.add(abspath(dirname(stpl_item)))
        for stpl_path in sorted(stpl_paths):

            # delete first
            for ff in glob.glob(f'{stpl_path}/trc_report*.csv'):
                log.info(f'-i- Deleting existing trc_report: {ff}')
                File(ff).unlink()

            if IS_WIN:      # pragma: no cover
                log.info(f'-i- Calling Trace TRC check for: {stpl_path}')
                cmd = f'{cfg.consoletrc} -dir {stpl_path}'
                code, out = SystemCall(cmd).run_outtxt()
                log.info(out)
                log.info('')

            trc_result = glob.glob(f'{stpl_path}/trc_report*.csv')
            if trc_result:
                # There are two .stpl, they are the same, use one
                self.trcout_check(trc_result.pop())    # This will raise exception if there are TRC fails
            else:
                log.info(f"-i- WARNING!!! No trc_report*.csv generated in {stpl_path}. Check TRACE.")
                is_error = True

        return is_error


if __name__ == '__main__':  # pragma: no cover
    if IS_UNIX:
        log.info("TRACE TRC needs windows env. Pls re-execute trace_trc_torch.py in windows.")
    else:
        TraceTrc().main()
