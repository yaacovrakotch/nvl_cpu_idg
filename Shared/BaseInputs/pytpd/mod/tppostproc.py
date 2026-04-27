#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
This script will run the skipjson cfg in tp_audit.py
"""
import glob
from mod.moduleskip import ModuleSkip
from os.path import exists, basename
from tp.testprogram import TestProgram
from gadget.pylog import log
from gadget.files import File
from gadget.errors import confirm
from mod.prlflow import PrlFlow
import re


class TpPostProc:
    """
    Skip module wrapper for postTP builds
    """

    def __init__(self):
        self.envs = glob.glob('./EnvironmentFile*.env')

    def skipjson(self):
        """
        Runs the ModuleSkip.skipjson routine
        :return:
        """
        env = self.envs[0]
        assert exists(env), 'Unable to find %s file! Verify that your script ran inside the TPL folder' % env
        ModuleSkip.skipjson_main(env)

        return

    def cl2rc(self):
        """
        Read MTL_ALL_*_CLASS.xml, rename by removing spaces in the name, replace file data (from OLBCC2 to OLBCC), save
        Creates MTL_ALL_*_RAWCLASS.xml files inside TPI_DFF_XXX/InputFiles based from MTL_ALL_*_CLASS.xml
        :return: None
        """
        # remove spaces from the filename
        rf = re.compile(r'(\S+)/InputFiles/(.*)')
        c2rcfiles = glob.glob('Modules/TPI_DFF_*/InputFiles/*_ALL*_CLASS.xml')
        for f in c2rcfiles:
            f = f.replace('\\', '/')
            rt = rf.search(f)
            assert rt, 'Unable to regexify the dff xml:%s' % f
            fp = rt.group(1) + '/InputFiles/'  # file path
            fn = rt.group(2)  # this is the filename.xml
            fnn = fn.replace(' ', '_')  # rename fn, remove spaces, replace with underscore
            File(f).move(fp).rename(fnn)  # nested move+rename

        # replace OLBCC2 with OLBCC
        c2rcfiles = glob.glob('Modules/TPI_DFF_*/InputFiles/*_ALL*_CLASS.xml')
        cc2 = '<name>OLBCC2</name>'
        cc = '<name>OLBCC</name>'
        for f in c2rcfiles:
            with open(f, 'r') as file:
                log.info(f'-i- Reading inputFile {f}...')
                xmldata = file.read()
            xmldata = xmldata.replace(cc2, cc)
            with open(f, 'w') as file:
                file.write(xmldata)
                log.info(f'-i- OLBCC2 replaced with OLBCC inside InputFile: {f}!')

        # create the _RAWCLASS.xml files
        c2rcfiles = glob.glob('Modules/TPI_DFF_*/InputFiles/*_ALL*_CLASS.xml')
        cl = '<first_socket_upload>PBIC_DAB'
        rc = '<first_socket_upload>RC_S1'
        for f in c2rcfiles:
            ff = f[:-9] + 'RAWCLASS.xml'
            with open(f, 'r') as file:
                log.info(f'-i- Reading inputFile {f}...')
                xmldata = file.read()
            xmldata = xmldata.replace(cl, rc)
            with open(ff, 'w') as file:
                file.write(xmldata)
                log.info(f'-i- New inputFile created: {ff}!')

        return

    def main(self):
        """Main Entry point"""
        self.skipjson()
        BinHack().main()
        BinHack().mtpl()
        self.cl2rc()
        EnvHack().tpl_input_file()
        EnvHack().prime_schema_path()
        MultiZonePin().main()

        for env in self.envs:
            PrlFlow(env).main()


class EnvHack:
    """
    Various env related hacks
    """
    def prime_schema_path(self):
        r"""
        To support update in User Code release prime_v8.02.02-evg5040502-tos31000-ddg221702, need to add
        ~HDMT_TPL_DIR\Supersedes\code and $PRIME_USER_CODE_DLL_DIR into env file
        """
        for f in glob.glob('*.env'):
            self._one_prime_schema_path(f)

    def _one_prime_schema_path(self, ff):
        """Process one env file. Assumes that HDMT_TPL_INPUT_FILES is more than one line."""
        final = []
        with open(ff) as fh:
            for line in fh:
                if line.strip().startswith('PRIME_SCHEMA_PATH ') and line.strip().endswith(';'):
                    final.append('PRIME_SCHEMA_PATH = "~HDMT_TPL_DIR\\Supersedes\\code;" +\n')
                    final.append('                    "$PRIME_USER_CODE_DLL_DIR;" +\n')
                    final.append('                    "$HDMT_TPL_INPUT_FILES";\n')
                    continue
                final.append(line)

        # write it
        File(ff).rewrite(''.join(final), 'prime_schema_path()')

    def tpl_input_file(self):
        """
        Due to caching, need to add FUSE_ROOT_DIR* into HDMT_TPL_INPUT_FILES
        Assumes that HDMT_TPL_INPUT_FILES is multi-line and will add at the end.
        Will not add if it is already added.
        """
        for f in glob.glob('*.env'):
            self._one_env_tpl_input_files(f)

    def _one_env_tpl_input_files(self, ff):
        """Process one env file. Assumes that HDMT_TPL_INPUT_FILES is more than one line."""
        # Get all FUSE_ROOT_DIR_*
        varnames = set()
        for line in File(ff).chomp(strip=True, comment='#'):
            if line.startswith('FUSE_ROOT_DIR_'):
                varnames.add(f'${line.split()[0]}')

        # Find HDMT_TPL_INPUT_FILES, get existing lines, then add at the end minus 1
        final = []
        found = set()
        start = False
        robj = re.compile(r'^\s*\"([^\";]+);?\"')
        with open(ff) as fh:
            for line in fh:
                # do not process empty lines or comment lines
                if (not line.strip()) or line.strip().startswith('#'):
                    final.append(line)
                    continue

                if start:   # inside of HDMT_TPL_INPUT_FILES
                    res = robj.search(line)
                    assert res, f'_one_env_tpl_input_files(): unknown line: {line}'
                    value = res.group(1)
                    found.add(value)

                    if line.strip().endswith(';'):
                        # insert new items before last line
                        for additem in sorted((varnames - found)):
                            final.append(f'                                "{additem};" +\n')
                        start = False

                if line.strip().startswith('HDMT_TPL_INPUT_FILES'):
                    start = True

                final.append(line)

        # write it
        File(ff).rewrite(''.join(final), 'tpl_input_file()')


class BinHack2:
    """TOS4 bin processing for ARL"""

    def __init__(self, tpobj):
        self.tpobj = tpobj

    def main(self):
        # get all pass b\d+ first
        robj = re.compile(r'^\s*Bin\s+(b\d+)\s*\d+\s*:\s*"b\d+_PASS"')
        pass_b = set()
        for key in self.tpobj.get_import_files('bdefs'):
            with open(key) as fh:
                for line in fh:
                    res = robj.search(line)
                    if res:
                        pass_b.add(res.group(1))

        # replace all passing b\d+ to b1_PASS_CMTTRAY_1
        for key in self.tpobj.get_import_files('bdefs'):
            self._hack_bdef(key, pass_b)

    def _hack_bdef(self, fname, pass_b):
        """Update bdef file to b1_PASS_CMTTRAY_1"""
        raw = File(fname).raw()
        final = []
        concat = '|'.join(sorted(pass_b))
        robj = re.compile(fr'\s({concat});')
        for line in raw:
            res = robj.search(line)
            if res:
                to_replace = f'{res.group(1)};'
                final.append(line.replace(to_replace, 'b1_PASS_CMTTRAY_1;'))
            else:
                final.append(line)
        File(fname).rewrite(''.join(final), 'BinHack2.main()')


class BinHack:

    def __init__(self, envglob='./EnvironmentFile*.env'):
        self.envs = [x for x in glob.glob(envglob) if not x.endswith('.g.env')]
        self.robj1 = re.compile(r'^\s*LeafBin.*\b(b\d+_PASS);')
        self.robj34 = re.compile(r'^\s*LeafBin\s+(b\d{3}_\w+|b\d{4}_\w+)\s+(\d+)\s*:\s*"(\w+)".*')
        self.robj8 = re.compile(r'^\s*LeafBin\s+(b\d{8}_\w+)\s+(\d+)\s*:\s*"(\w+)".*')
        # LeafBin b90999901_fail_FAIL_DPS_ALARM    90999901    : "b90999901_fail_FAIL_DPS_ALARM",    b99_FAIL_HARDWARE_ALARM;

    def main(self):
        """Request by Mic, so that ituff is printed correctly for pass bins"""
        env = self.envs[0]
        tp = TestProgram(env)
        res = tp.get_import_files('bdefs')
        for key in res:
            self._bin_hack_file(key)
            log.info(f"-i- bdef processed: {key}")

    def _bin_hack_file(self, ff):
        """
        bindef hacking
        https://wiki.ith.intel.com/x/voOqgg
        """

        final = []
        digit8 = []
        digit34 = []

        with open(ff) as fh:
            for line in fh:
                newline = line

                # Part1 - Replace all occurrence of "b\d+_PASS;" to "b1_PASS_CMTTRAY_1;" (yes, hardcoded)
                # for lines that start with "LeafBin", only for BinDefinitions.bdefs file
                res = self.robj1.search(newline)
                if res:
                    newline = newline.replace(res.group(1), 'b1_PASS_CMTTRAY_1')

                # Part2 - Add new 4-digit LeafBins from 8-digits:
                res = self.robj34.search(newline)
                if res:
                    digit34.append(newline)
                res = self.robj8.search(newline)
                if res:
                    digit8.append(newline)

                if digit8 and line.strip().startswith('}'):
                    for item in self._make_4_digits(digit8, digit34):
                        final.append(item)
                    digit8 = []   # write it once only

                final.append(newline)

        # replace it
        File(ff).rewrite(''.join(final), 'BinHack.main()')

    def _make_4_digits(self, digit8, digit34):
        """
        Return a set of 4 digit bins based on eightdigit
        From:
        LeafBin b90999901_fail_FAIL_DPS_ALARM    90999901    : "b90999901_fail_FAIL_DPS_ALARM",    b99_FAIL_HARDWARE_ALARM;
        To:
        LeafBin b9999_fail_FAIL_DPS_ALARM    9999    : "b9999_fail_FAIL_DPS_ALARM",    b99_FAIL_HARDWARE_ALARM;
        """
        result = {}        # {4_digit_int: final_4_digit_line}
        result34 = set()    # {3_digit_int}

        # Get all 3-digit bins, keep these but make sure no duplicates when 4-digit is created
        for line in digit34:
            res = self.robj34.search(line)
            result34.add(int(res.group(2)))

        # Part2
        for line in sorted(digit8, reverse=True):
            res = self.robj8.search(line)
            fourdig = res.group(2)[4:8]
            confirm(len(fourdig) == 4,
                    'Error: Expecting 8-digit for %r.' % res.group(2),
                    'Check .bdef file in this line [%s]' % line)
            key = int(fourdig)
            target = line.replace(res.group(2), fourdig)
            if key in result34 or (not key):
                continue     # Do not add existing 3-digits
            if key in result:
                if '_SHARED_BIN' not in result[key]:
                    result[key] = self._add_shared_bin(result[key])
            else:
                result[key] = target

        # Part5
        for line in digit8:
            if '_PASS_CMTTRAY_' not in line:
                continue
            res = self.robj8.search(line)
            fourdig = f'{res.group(2)[2]}{res.group(2)[0]}{res.group(2)[4:6]}'
            confirm(len(fourdig) == 4,
                    'Error: Expecting 8-digit for %r.' % res.group(2),
                    'Check .bdef file in this line [%s]' % line)
            key = int(fourdig)
            target = line.replace(res.group(2), fourdig)
            if key in result34:
                continue     # Do not add existing 3-digits
            if key in result:
                if '_SHARED_BIN' not in result[key]:
                    result[key] = self._add_shared_bin(result[key])
            else:
                result[key] = target

        return sorted(result.values())

    def _add_shared_bin(self, line):
        """Add _SHARED_BIN in line"""

        res = self.robj34.search(line)
        assert res, f'Expecting robj4 to pass: {line}'
        assert res.group(1) == res.group(3), f'Code expects {res.group(1)} vs {res.group(3)} to be same'
        return line.replace(res.group(1), f'{res.group(1)}_SHARED_BIN')

    def mtpl(self):
        """
        Replace all occurrence of 'SoftBins.b101_pass' to 'SoftBins.b10010000_pass_pure;'
        in .mtpl.: "Part3"
        """
        for ff in glob.glob('Modules/*/*.mtpl'):
            alltxt = File(ff).read()
            if 'SetBin SoftBins.b101_pass' in alltxt:
                self._mtpl_replace(ff, alltxt)

    def _mtpl_replace(self, ff, alltxt):
        """
        Replace contents of ff (one file):
        Replace all occurrence of 'SoftBins.b101_pass' to 'SoftBins.b10010000_pass_pure;'
        It is assumed (no check) that SoftBins.b10010000_pass_pure already exist in BinDefinitions.bdefs
        """
        final = []
        for line in alltxt.split('\n'):
            if 'SetBin SoftBins.b101_pass' in line:
                line = '                        SetBin SoftBins.b10010000_pass_pure;'
            final.append(line)

        # replace it
        File(ff).rewrite('\n'.join(final), 'BinHack.mtpl()')


class MultiZonePin:

    def main(self):
        """
        Main entry point of MultiZonePin postprocess
        """
        for pinfile in glob.glob('./*.pin'):
            self.process(pinfile)

    def process(self, ff):
        """
        Move CPU_PWR or PCH_PWR into it's ThermalDomainDefinition

        :param pinfile:
        :return:
        """
        final = []
        block_start = False
        block = []
        updated = False

        with open(ff) as fh:
            for line in fh:
                if line.strip() in ('Domain CPU_PWR', 'Domain PCH_PWR'):
                    block_start = True
                    updated = True
                if block_start:
                    if line.strip() == '}':
                        block_start = False
                    block.append(line)
                    continue

                # Add the new ThermalDomainDefinitions when the final end bracket is found
                if line.startswith('}') and block:

                    if not ('IP_CPU' in ff or 'IP_PCH' in ff):   # Do not write in IP_PCH or IP_CPU
                        final.append('        ThermalDomainDefinitions\n')
                        final.append('        {\n')

                        for linex in block:
                            if linex.strip().startswith('Domain '):
                                final.append(linex.replace('Domain', 'ThermalDomain'))
                            else:
                                final.append(linex)

                        final.append('        }\n')

                final.append(line)

        # replace it
        if updated:
            File(ff).rewrite(''.join(final), 'MultiZonePin()')
