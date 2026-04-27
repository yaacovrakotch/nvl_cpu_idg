#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
This script is one-time/initial scripting needs
This script is not unittested since it is not used long term
See bottom of script for all commands
"""
import setenv      # must be first in the imports
from tp.testprogram import TestProgram, pprint
from gadget.files import File
from gadget.dictmore import read_csv
from collections import defaultdict
from mod.mtplencode import MtplEncode
from gadget.tputil import OtplFile
from gadget.errors import confirm
from os.path import basename, dirname
import sys
import re
import json


class Binning:
    """Various bin related"""

    def update_modulename_in_bin(self):
        """
        Update all .mtpl binning to match module
        See separate routine to show which are mismatched
        """
        assert len(sys.argv) == 3, 'usage: onetime.py bin_module path/EnvironmentFile.env'
        tpobj = TestProgram(sys.argv[2])
        for ff in tpobj.get_all_mtpl_from_stpl():
            lines = File(ff).raw()
            module = basename(dirname(ff))
            for idx in range(len(lines)):
                if lines[idx].strip().startswith('SetBin'):
                    lines[idx] = lines[idx].replace(module.replace('68', '28'), module)
                    lines[idx] = lines[idx].replace(module.replace('C68', 'C2P'), module)
            File(ff).rewrite(''.join(lines), 'update_modulename_in_bin')

    def id_bin_wrong_mod(self):
        """
        Identify modules with wrong module name
        """
        assert len(sys.argv) == 3, 'usage: onetime.py id_bin_module path/EnvironmentFile.env'
        tpobj = TestProgram(sys.argv[2])
        for ff in tpobj.get_all_mtpl_from_stpl():
            lines = File(ff).raw()
            module = basename(dirname(ff))
            for idx in range(len(lines)):
                line = lines[idx]
                if line.strip().startswith('SetBin'):
                    if module not in line:
                        if '_fail_FAIL_' in line:
                            continue
                        if '_SHARED_BIN' in line:
                            continue
                        print(module, line.strip())


class WriteFSM(MtplEncode):
    """Read fsm config and put tags in mtpl"""

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
        rtest = re.compile(r"(Test|TrialTest|CSharpTest|CSharpTrialTest)\s+\w+\s+(\S+)")
        taglno = defaultdict(set)
        rewrite = False
        for lno, line in OtplFile(fname).readline(comments=True):

            # get module
            if line.startswith('TestPlan'):
                res = re.search(r"^TestPlan\s+(\w+)", line)      # no need to compile - one time
                module = res.group(1)
                continue

            # get testname
            elif line.startswith(('Test ', 'CSharpTest ')):
                eline_lno = lno
                elines = [line]
                # print(module, elines)
                continue

            elif line.startswith(('TrialTest ', 'CSharpTrialTest ')):
                eline_lno = lno
                elines = list(self.bm.expand(line, f'Fix line#{lno} {module} File: {fname}'))
                # print(module, elines)
                self.ctr += 1
                continue

            elif line.startswith('}'):
                elines = None

            elif line.startswith('{') and elines and module in self.tnre:
                for eline in elines:
                    res = rtest.search(eline)
                    confirm(res,
                            f'Error on line#{eline_lno}: [{line}] Cannot derive the instance name',
                            f'Check {fname}')
                    testname = res.group(2)
                    if self.tnre[module].search(testname):
                        taglno[lno].add(f'    # FSM: HOT: {self.ip[module]}\n')
                        rewrite = True
                        self.found[module].add(testname)
                elines = None

        if rewrite:
            final = []
            for lno, line in enumerate(File(fname).raw()):
                if lno in taglno:
                    final.extend(taglno[lno])
                final.append(line)
            File(fname).rewrite(''.join(final), 'WriteMtpl()')

    @classmethod
    def main(cls):
        assert len(sys.argv) == 4, 'Usage: onetime.py fsm EnvironmentFile.env <path>/FullSkipModelInput.csv'

        # note: it assumes there there is only one config: uniq.add(','.join(elems[:10]))
        fsm_config = sys.argv[3]

        # read fsmconfig
        tnlist = defaultdict(set)    # {module: set(testname_regex)}
        cls.ip = {}        # {module: IP_NAME}
        cls.found = defaultdict(set)     # {(module, testname): True}
        cls.tnre = {}      # {module: regexobj}
        for elems in read_csv(fsm_config, return_dict=True):
            tnlist[elems['ModuleName']].add(elems['InstanceName'])
            cls.ip[elems['ModuleName']] = elems['IPName']

        # create big regex
        for md in tnlist:
            cls.tnre[md] = re.compile('(%s)' % ('|'.join(tnlist[md])))

        # Execute
        tp1 = TestProgram(sys.argv[2])
        cls(tp1)._read_all_mtpl()

        # Write report of missing
        for module in tnlist:
            for testname in tnlist[module]:
                for ftn in cls.found.get(module, []):
                    if re.search(testname, ftn):
                        break
                else:
                    print(f'NOT FOUND in mtpl but in .csv: {module} {testname}')


class WritePPR(MtplEncode):
    """Read ppr config and put tags in mtpl"""

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
        rtest = re.compile(r"(Test|TrialTest|CSharpTest|CSharpTrialTest)\s+\w+\s+(\S+)")
        taglno = defaultdict(list)
        rewrite = False
        for lno, line in OtplFile(fname).readline(comments=True):

            # get module
            if line.startswith('TestPlan'):
                res = re.search(r"^TestPlan\s+(\w+)", line)      # no need to compile - one time
                module = res.group(1)
                continue

            # get testname
            elif line.startswith(('Test ', 'CSharpTest ')):
                eline_lno = lno
                elines = [line]
                # print(module, elines)
                continue

            elif line.startswith(('TrialTest ', 'CSharpTrialTest ')):
                eline_lno = lno
                elines = list(self.bm.expand(line, f'Fix line#{lno} {module} File: {fname}'))
                # print(module, elines)
                self.ctr += 1
                continue

            elif line.startswith('}'):
                elines = None

            elif (line.startswith('}') or line.startswith('PatternNameMap')) and elines and module in self.tnre:
                once = None
                for eline in sorted(elines):
                    res = rtest.search(eline)
                    confirm(res,
                            f'Error on line#{eline_lno}: [{line}] Cannot derive the instance name',
                            f'Check {fname}')
                    testname = res.group(2)
                    if testname in self.tnre[module]:
                        if once is None:
                            taglno[lno].append(f'    # PPR: {self.ip[module]}: *: Config{self.t2n[(module, testname)]}\n')
                            once = self.t2n[(module, testname)]
                        else:
                            if self.t2n[(module, testname)] == once:
                                pass   # No print
                            else:
                                taglno[lno].append(f'    # PPR: {self.ip[module]}: {testname}: Config{self.t2n[(module, testname)]}\n')

                        rewrite = True
                        self.found[module].add(testname)
                elines = None

        if rewrite:
            final = []
            for lno, line in enumerate(File(fname).raw()):
                if lno in taglno:
                    final.extend(taglno[lno])
                final.append(line)
            File(fname).rewrite(''.join(final), 'WriteMtpl()')

    @classmethod
    def main(cls):
        assert len(sys.argv) == 4, 'Usage: onetime.py ppr EnvironmentFile.env <path>/PprConfiguration.json'

        cls.ip = {}                      # {module: IP_NAME}
        cls.found = defaultdict(set)     # {(module, testname): True}
        cls.tnre = defaultdict(set)      # {module: set_testname}
        cls.t2n = {}                     # {(module, testname): n}
        cls.pprcfg = {}                  # {n: dict}

        # read pprconfig
        ppr_config = sys.argv[3]
        with open(ppr_config) as fh:
            data = json.load(fh)

        # read and generate unique configs
        for tname, val in data['TestInstance2Tolerances'].items():
            (real_ip, module, real_tname) = tname.split('::')
            cls.tnre[module].add(real_tname)
            cls.ip[module] = real_ip

            # uniq configs
            found = None
            for ref, valref in cls.pprcfg.items():
                if val == valref:
                    found = ref
                    break
            if not found:
                if cls.pprcfg:
                    found = max(cls.pprcfg) + 1
                else:
                    found = 1
                cls.pprcfg[found] = val
            cls.t2n[(module, real_tname)] = found

        # Execute
        tp1 = TestProgram(sys.argv[2])
        cls(tp1)._read_all_mtpl()

        # Write report of missing
        for module in cls.tnre:
            for testname in cls.tnre[module]:
                for ftn in cls.found.get(module, []):
                    if re.search(testname, ftn):
                        break
                else:
                    print(f'NOT FOUND in mtpl but in .json: {module} {testname}')

        # Write the config
        print("## Config:")
        print(json.dumps({f'Config{x}': y for x, y in cls.pprcfg.items()}, indent=3))


HELP_MESSAGE = '''

Usage:
    onetime.py <command> <args>

Commands: 
    onetime.py fsm              # Write FSM config (and put tags in mtpl)
    onetime.py ppr              # Write PPR config (and put tags in mtpl)
    onetime.py bin_module       # Update all .mtpl binning to match module
    onetime.py id_bin_module    # Identify modules with wrong module name
'''


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) != 1, HELP_MESSAGE

    # List of commands below
    if sys.argv[1] == 'fsm':
        WriteFSM.main()
    elif sys.argv[1] == 'ppr':
        WritePPR.main()
    elif sys.argv[1] == 'bin_module':
        Binning().update_modulename_in_bin()
    elif sys.argv[1] == 'id_bin_module':
        Binning().id_bin_wrong_mod()
    else:
        print(f"Unknown command: {sys.argv[1]}")
