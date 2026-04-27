#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
tputil module - TP related utilities

Routines here should not import any mod/ files.
Routines here are Testprogram related helpers
"""
from .pylog import log
from .disk import mkdirs, listdir_noerror, get_free_diskspace
from .strmore import curtime, indent
from .shell import fullcmdline, USERNAME, HOSTNAME
from .errors import ErrorEnv, confirm, ErrorUser, ErrorInput
from .files import File, TempDir
from .dictmore import xmlfunc
from .gizmo import Elapsed
from os.path import isdir, dirname, abspath, exists, join, basename
from itertools import zip_longest
from mod.setting import cfg
from platform import python_version
import re
import os
import time
import json
import sys


def delete_por_tp(tpdir, bom, envname='EnvironmentFile.env'):
    """
    Delete all POR_TP folders except the bom folder (exact match)

    :param tpdir: tp root folder
    :param bom: exact match bom name
    :param envname: Environment file name. Should not be wildcard
    :return: deleted folders
    """
    import shutil
    import glob

    count = 0
    sw = Elapsed()

    por_folders = glob.glob(f'{tpdir}/POR_TP/*/{envname}')
    baseinputs_folders = glob.glob(f'{tpdir}/BaseInputs/*/*/Supersedes')
    com_por_folders = glob.glob(f'{tpdir}/Shared/POR_TP/*/{envname}')
    com_baseinputs_folders = glob.glob(f'{tpdir}/Shared/BaseInputs/Common/*/Supersedes')

    # Delete BOM folders in Dielet and Common shared POR_TP folders
    for desc, folder_list in [
            ('POR_TP', por_folders),
            ('BaseInputs_Dielet', baseinputs_folders),
            ('POR_TP_Common', com_por_folders),
            ('BaseInputs_Common', com_baseinputs_folders)]:
        if len(folder_list) > 1:
            for item in folder_list:
                tbom = basename(dirname(item))
                tbom_split = tbom.split('_')
                if len(tbom_split) > 3:
                    tbom = '_'.join(tbom_split[-3:])   # only last 3 fields
                if bom != tbom:
                    targ = dirname(item)
                    log.info(f'-i- Deleting {targ}; {tbom}: keeping only {bom} ({desc})')
                    shutil.rmtree(targ)
                    count += 1

    log.info(f'-z- delete_por_tp(keep={bom}), total={count}, Elapsed {sw}')
    return count


def tid_from_pat(patname: str, chunk=True, pos=None) -> str:
    """
    Returns tid_chunknum from pat

    chunknum is the field before testname

    :param patname: patternname
    :param chunk: Set to False to return tid only
    :param pos: chunk position location
    :return: tid_chunknum or tid
    """
    tidonly = patname[9:16]
    if not chunk:
        return tidonly
    if pos:
        return f'{tidonly}_{patname[pos:pos + 2]}'
    for ii in range(cfg.testname_pos, len(patname)):
        if patname[ii] == '_':
            return f'{tidonly}_{patname[ii-2:ii]}'
    return f'{tidonly}_00'


def tuple_tid(patname: str) -> tuple:
    """
    Returns (tuple, tid) from pat

    :param patname: patternname
    :return: (tuple, tid)
    """
    return patname[1:8], tid_from_pat(patname)


def testname_from_pat(patname: str) -> str:
    """
    Returns testname from pat

    :param patname: patternnmae
    :return: testname
    """
    for ii in range(cfg.testname_pos, len(patname)):
        if patname[ii] == '_':
            return patname[ii + 1:]
    return ''   # none found


def correct_type(val, ref):
    """
    Converts val to the correct type based of ref
    Usage:
    somevar = correct_type(newval, somevar)
    """
    if type(val) == type(ref):
        return val
    elif ref is None:
        return val
    elif isinstance(ref, str):
        return str(val)
    elif isinstance(ref, int):
        return int(val)
    elif isinstance(ref, float):
        return float(val)
    else:
        raise TypeError('Unknown type: [%r]: %s' % (ref, type(ref)))


def is_int(val) -> bool:
    """
    Returns True if val is simple int or empty string

    :param val: input value (either str or int)
    :return: bool
    """
    if isinstance(val, int):
        return True

    assert isinstance(val, str), f'Error is_int({val}): Expecting string.'
    if val != '':   # empty is ok
        try:
            int(val)
        except ValueError:
            return False
    return True


def noquote(line: str, quote='"') -> str:
    """
    Returns string inside quotes if string is wrapped in quotes.
    Testprogram specific - double quotes only

    :param line: any string line
    :param quote: Character to check. Defaults to double quotes
    :return: line without quotes
    """
    if line.startswith(quote) and line.endswith(quote) and line.count(quote) == 2:
        return line[1:-1]
    else:
        return line


def remove_ip(name: str, _robj=re.compile('^(IP[A-Z]::|IP_[A-Z]+(?:::|_BASE::))')) -> str:
    """
    Remove the ip from name, if it exist - hardcoded tp IP_CPU and IP_PCH

    :param name: input name
    :return: string without ip
    """
    res = _robj.search(name)
    if res:
        return name.replace(res.group(1), '')
    return name


def ip_tuple(name: str) -> tuple:
    """Return tuple of (ip, string) of name. ip is None if No IP in string"""
    elems = name.split('::')
    if 'IP_CPU::' in name:
        return 'IP_CPU', elems[-1]
    if 'IP_PCH::' in name:
        return 'IP_PCH', elems[-1]
    return None, elems[-1]


def is_validip(name: str) -> bool:
    """Return True if name is a valid IP"""
    return name in ('IP_CPU', 'IP_PCH')


def tuple_modname(name: str) -> tuple:
    """
    Return (module, name)

    :param name: module::instance_name
    :return: (module, name)
    :rtype: (str, str)
    """
    if '::' in name:        # 1.1sec if check first -vs- 1.2sec if split then check len()
        result = name.split('::')
        return result[-2], result[-1]
    else:
        return 'BASE', name


def time_disp(var: float, dec=3) -> str:
    """
    Return max of N decimals string, considering m,u,n,p units (Time)

    :param var: float or string
    :param dec: number of significant digits
    :return: string
    """
    return num_disp(var, dec, 'S')


def volt_disp(var: float, dec=3) -> str:
    """
    Return max of N decimals string, considering m,u,n,p units (Voltage)

    :param var: float
    :param dec: Number of significant digits
    :return: string
    """
    return num_disp(var, dec, 'V')


def num_disp(var: float, dec=3, unit="") -> str:
    """
    Return max of N decimals string, considering m,u,n,p units

    example: 100.1016 will return 100.102
               1.1016 will return 1.102

    :param var: float or string
    :param dec: Number of significant digits
    :param unit: character to add at end (unit)
    :return: string
    """
    if not isinstance(var, (int, float)):
        return var

    fmt = '%%%s.%sf' % (4 + dec, dec)
    if var == 0:
        res = fmt % var
        up = ''
    elif abs(var) < 0.000000001:
        res = fmt % (var / 0.000000000001)
        up = 'p'
    elif abs(var) < 0.000001:
        res = fmt % (var / 0.000000001)
        up = 'n'
    elif abs(var) < 0.001:
        res = fmt % (var / 0.000001)
        up = 'u'
    elif abs(var) < 1.0:
        res = fmt % (var / 0.001)
        up = 'm'
    else:
        res = fmt % var
        up = ''

    # remove the zeros in the decimal places
    for _ in range(10):
        if '.' not in res:
            break
        if res[-1] in ('0', '.'):
            res = res[:-1]
        else:
            break

    # pad to fixed 3+1+dec+len(unit) length
    value = '%s%s%s' % (res, up, unit)
    fmt = '%%-%ds' % (4 + dec + len(unit) + 1)
    final = fmt % value

    return final


def trimut(text: str, istext=False, empty=False) -> list:
    """
    Removed unwated lines (starts with '-') in text, for unittests compares

    :param text: output from screen
    :param istext: Set to True to return text instead of array
    :param empty: Set to True to return empty lines as well
    :return: a list to check expect on
    """
    result = []
    for line in text.split('\n'):
        print(line)
        if not line and (not empty):
            continue
        if line.startswith('-'):
            continue
        result.append(line)

    if istext:
        return '\n'.join(result)

    return result


def log_usage(subdir, cfg):
    """
    Log usage given subdir

    :param subdir: subdirectory in cfg.log_dir
    :param cfg: cfg object
    """
    from gadget.helperclass import IS_UT
    if IS_UT:
        return 1    # Do not log unittests
    target = f'{cfg.log_dir}/{subdir}'
    assert isdir(cfg.root), (f"[{cfg.root}] root directory does not exist. "
                             "Try to map J:\\ drive to point to pdx/fm/pg I:\\ drive, then call script from J:\\. "
                             "Otherwise, email jqdelosr to enable pytpd for your site.")
    mkdirs(target, mode='02775')
    assert isdir(target), f"Cannot access {target} directory. Pls email jqdelosr to enable {subdir} for your site."
    text = '%s@%s: %s' % (USERNAME, os.getcwd(), fullcmdline(True))
    File(f'{target}/usage.log').logprint(text)


def pat_section_diff(pat1, pat2):
    """
    Return the section in pattern that has difference.
    A section is separated by underscores. Assumed sections are the same

    :param pat1:
    :param pat2:
    :return: (section_pat1, section_pat2)
    """
    item1 = pat1.split('_')
    item2 = pat2.split('_')
    result1 = []
    result2 = []
    for a, b in zip_longest(item1, item2, fillvalue='None'):
        if a != b:
            if item1[0] == a:   # first element
                result1.append(f'{a}_')
                result2.append(f'{b}_')
            elif item1[-1] == a or item2[-1] == b:  # last element
                result1.append(f'_{a}')
                result2.append(f'_{b}')
            else:
                result1.append(f'_{a}_')
                result2.append(f'_{b}_')

    return ' '.join(result1), ' '.join(result2)


def to_regex(pseudoregex, exact=False, maxlen=10000):
    """
    Converts pseudoregex to real regex

    :param pseudoregex: input string. Pseudoregex can use "*" instead of ".*"
    :param exact: Set to True for exact match
    :param maxlen: Maximum length to process
    :return: regex string
    """
    if pseudoregex == '':
        return '^$'
    if not pseudoregex:
        return ''

    # logic: insert '.' before '*' if character before it isalnum()
    for idx in range(1, maxlen):   # max of 10000 chars
        if idx == len(pseudoregex):
            break
        if pseudoregex[idx] == '*' and pseudoregex[idx - 1] != '.':
            pseudoregex = f'{pseudoregex[:idx]}.{pseudoregex[idx:]}'

    # corner case: first char
    if pseudoregex[0] == '*':
        pseudoregex = f'.{pseudoregex}'

    if exact:
        if pseudoregex[0] != '^':
            pseudoregex = f'^{pseudoregex}'
        if pseudoregex[-1] != '$':
            pseudoregex = f'{pseudoregex}$'

    return pseudoregex


def get_param(data, item, default=None, _alias={'_DO_NOT_TOUCH_': [],
                                                'level': ('levels', 'LevelsTc'),
                                                'timing': ('TimingsTc', 'timings')}):
    """
    Similar to data.get(item), but item has certain list of aliases
    note: patlist and Patlist is directly mapped in _read_mtpl_test()

    :param data: dictionary input
    :param item: key
    :param default: default value
    :return: value
    """
    all_items = ', '.join(_alias)
    assert item in _alias, f'{item} is not supported. Supported items: {all_items}'
    assert '_DO_NOT_TOUCH_' in _alias, 'Cannot change _alias!'
    if item in data:
        return data[item]

    for key in _alias[item]:
        if key in data:
            return data[key]

    return default


def instancename_no_speed(name, ro=re.compile(r'^('
                                              r'\w+\d\d\d+_\w+|'
                                              r'\w+_F\d_\w+|'
                                              r'\w+\d\d\d+'
                                              r')(_\d{4})$')):
    """
    Replaces the speedflow element in testinstance name, if it exist
    Assume 4 digit
    """
    res = ro.search(name)
    final = name
    freq = None
    if res:
        final = f'{res.group(1)}_*'

        # Try to remove freq as well, only for speed flows
        ddict = ti_disassemble(name, isdict=True)
        freq = ddict.get('freq', None)
        if freq and freq.isdigit():
            to_replace = f'_{freq}_'
            final = final.replace(to_replace, '_*_')

    if freq and freq.isdigit():
        return final, int(freq)
    else:
        return final, 0


def float_2_noerr(float_str):
    """
    Returns a float with 2 decimal if number else string (as-is)

    :param float_str: float or string
    :return: float with two decimal if number, else string
    """
    num = Units.to_number(float_str)
    if num is None:
        return float_str   # as-is (string)
    else:
        return float('%.2f' % float(num))


def ti_disassemble(name, isdict=False, isclass=False):
    """
    Returns the elements of testname

    :param name: testinstance name
    :param isdict: Set to True to return dictionary
    :param isclass: Set to True for class dictionary
    :return: Empty if invalid name. list or dict
    """

    # try with speedflow at end
    elements = []
    if isclass:
        res = cfg.ti_name1.search(name)
    else:
        res = cfg.ti_name3.search(name)

    if res:
        elements = list(res.groups())
        if elements[-2]:     # remove the underscore in userinput
            elements[-2] = elements[-2][1:]
        else:
            elements[-2] = ''
    else:

        # without speedflow
        if isclass:
            res = cfg.ti_name2.search(name)
        else:
            res = cfg.ti_name4.search(name)

        if res:
            elements = list(res.groups())
            if elements[-1]:     # remove the underscore in userinput
                elements[-1] = elements[-1][1:]
            else:
                elements[-1] = ''
            elements.append('')

    keys = cfg.ti_elem.strip().split()

    # empty
    if not elements:
        if isdict:
            return {}
        else:
            return []

    assert len(elements) == len(keys), f'cfg.ti_elem count {len(keys)} != {len(elements)} count of cfg.ti_name1 or cfg.ti_name2'

    # Return
    if isdict:
        return {keys[idx]: elements[idx] for idx in range(len(keys))}

    return elements    # list


def read_blocks(fname, blocks):
    """
    Return list of lines given list of blocks.
    This routine is bracket aware.

    :param fname: input mtpl file
    :param blocks: list of block names (full line), e.g. "DUTFlow BEGCPU".
                   If line ends with "*" then it will use .startswith()
    :return: list of lines. lines here have EOL delimiter
    """
    # determine full line vs partial
    full = []
    partial = []
    for line in blocks:
        if line.endswith('*'):
            partial.append(line[:-1])
        else:
            full.append(line)
    partial = tuple(partial)

    # read "uniformed" otpl
    pairs = {}
    start = False
    slno = None
    stack = 0
    for lno, line in OtplFile(fname).readline():
        if line in full or line.startswith(partial):
            start = True
            slno = lno
        if start:
            if line == '{':
                stack += 1
            if line == '}':
                stack -= 1
                if stack == 0:
                    pairs[slno] = lno
                    start = False

    # read the input file
    start = False
    final = []
    with open(fname) as fh:
        for lno, line in enumerate(fh, start=1):
            if lno in pairs:
                end = pairs[lno]
                start = True
            if start:
                final.append(line)
                if lno == end:
                    start = False
                    final.append('\n')   # extra line

    return final


def get_modulename(path,
                   _r0=re.compile(r'.*[\/\\](\w+)[\/\\](InputFiles|PymtplInputFiles|AlephFiles)'),
                   _r1=re.compile(r'\bModules[\/\\](\w+)[\/\\][\w\-\.]+$'),
                   _r2=re.compile(r'\bModules[\/\\][\w\-]+[\/\\](\w+)[\/\\][\w+\-\.]+$'),
                   _r3=re.compile(r'\bModules\b'),
                   _r4=re.compile(r'\bModules[\/\\](\w+)[\/\\](\.github)'),
                   _r5=re.compile(r'\bModules[\/\\]\w+[\/\\](_source)[\/\\](\w+)')
                   ):
    """
    Return the module name given path. Module name is Module/<path> or Module/<dd>/<path>
    :param path: file path
    :return: the module name or None
    """
    # no Modules in path
    if not _r3.search(path):
        return None
    if basename(path) in ['.gitignore']:    # special stuff
        return None
    if 'Modules.' in basename(path):
        return None
    # Modules/<file>
    if basename(dirname(path)) == 'Modules':
        return None

    # <module>/(InputFiles|AlephFiles)
    res = _r0.search(path)
    if res:
        return res.group(1)

    # Modules/<module>/<name.ext>
    res = _r1.search(path)
    if res:
        return res.group(1)

    # Modules/shared/<module>/<name.ext>
    res = _r2.search(path)
    if res:
        return res.group(1)

    # Modules/<module>/.github
    res = _r4.search(path)
    if res:
        return res.group(1)

    # Modules/<module>/.github
    res = _r5.search(path)
    if res:
        return res.group(2)

    raise ErrorUser(f'Unknown file in Modules/ area: {path}',
                    'If you think this is a legit Module file, contact jqdelosr so get_modulename() can be fixed')


def is_number(value):
    """
    Return True if value is a valid number (eg. -1.23)

    :param value: string
    :return: True if value is number or float
    """
    try:      # try/except is faster than regex() filter  (2.5s vs 2.7s for 375K)
        _ = float(value)
        return True
    except BaseException:
        return False


def find_files_given_paths(fnames, list_path, suggestion, error_out=True):
    """
    Return set of fullpaths on first found given fnames, case-insensitive so it works in unix and windows

    :param fnames: list of fnames to find
    :param list_path: list of paths to search, in order
    :param suggestion: message if fname is not found
    :param error_out: Throw and error if not found. Otherwise just warning. This is so it can match original
                        VEP behavior
    :return: set of fullpaths
    """
    # get all dir listings first
    dfiles = {}      # {<filename_lower>: <location_dir>}
    for x in reversed(list_path):
        if isdir(x):
            dfiles.update({y.lower(): (x, y) for y in os.listdir(x)})

    result = set()
    errors = []
    for ff in sorted(fnames):
        if ff.lower() in dfiles:
            result.add(f'{dfiles[ff.lower()][0]}/{dfiles[ff.lower()][1]}')  # case-sensitive path
        else:
            errors.append(f"-e- Cannot find: {ff} from search paths.")

    if error_out and errors:
        log.info('Search paths:')
        log.info(indent(3, list_path))
        for item in errors:
            log.info(item)
        raise ErrorEnv(f"Cannot find {len(errors)} file(s). See above for details.", suggestion)

    return result


class CheckerLog:
    repo_sha = ('none', 'not_available_set_by_one_click_build')

    @classmethod
    def setup(cls, toolname='checkers'):
        """
        Setup logging inside checkers, copied from pingroups.py
        :return:
        """
        from gadget.helperclass import IS_UT
        if IS_UT:
            return 1

        root = f'{cls.get_log_path()}/{toolname}/{curtime(dateonly=True)}'    # date
        mkdirs(root, mode='02770')
        tool = basename(sys.argv[0]).replace('.py', '')
        log_filename = "%s_%s_%s_%s.log" % (tool, USERNAME, HOSTNAME, int(time.time()))
        log.filemixed(os.path.join(root, log_filename))
        log.info(f"-i- FULL CMD: {fullcmdline(with_exec=True)}")
        log.info(f"-i- EXECUTE INFO: {python_version()}, {HOSTNAME}, {curtime()}")
        log.info(f"-i- CWD: {os.getcwd()}")
        log.info(f"-i- TOOLSHA: {cls.get_tool_sha()}")

        cdrive = 'C:\\'
        if isdir(cdrive):   # pragma: no cover
            log.info(f"-i- DISKFREE_KB {cdrive}: {get_free_diskspace(cdrive)}")

        # display temp free space
        with TempDir(name=True) as tdir:
            log.info(f"-i- DISKFREE_KB {dirname(tdir)}: {get_free_diskspace(tdir)}")

        return 0

    @classmethod
    def get_tool_sha(cls, _targ=dirname(dirname(__file__))):
        """Return the sha of tool"""
        return cls.get_folder_sha(_targ)

    @classmethod
    def get_folder_sha(cls, folder):
        """Return sha of folder (direct clone or submodule)"""
        gdir = f'{folder}/.git'
        confirm(exists(gdir),
                f'{gdir} does not exist: {listdir_noerror(folder)}. cwd: {os.getcwd()} folder: {folder}',
                'This folder is required to determine the git version.',
                cls=ErrorInput)

        if exists(f'{gdir}/logs/HEAD'):
            head = f'{gdir}/logs/HEAD'
        else:
            # assume it's submodule at this point
            rpath = File(gdir).read().strip().replace('gitdir: ', '')
            head = f'{folder}/{rpath}/logs/HEAD'

        confirm(exists(head),
                f'{head} does not exist: cwd: {os.getcwd()} folder: {folder}',
                'This file is required to determine the git version.',
                cls=ErrorInput)
        lines = [x for x in File(head).raw() if x.strip()]
        return lines[-1].split()[1]    # 2nd element of last line

    @classmethod
    def get_log_path(cls):
        """
        /i/tpvalidation/engtools/tptools/mtl/beta/latest/main/torch_fixer.py
        In unix this is straightforward but in windows, cfg._logdir is incorrect due to sort drive map
        :return: Return the log path
        """
        targ = join(dirname(dirname(dirname(dirname(abspath(sys.argv[0]))))), 'logs')
        if exists(targ):
            return targ
        if exists(cfg.log_dir):
            return cfg.log_dir
        raise ErrorEnv(f"{cfg.log_dir} or {targ} does not exist. This must be created first.",
                       f"Contact jqdelosr to create.")

    @classmethod
    def build_checks(cls, envs, env_glob):
        """
        Common checks for one-click-build

        :param envs: list of env
        :param env_glob: regex string
        :return:
        """
        # correct directory?
        confirm(exists('BaseTestPlan.tpl'),
                f'BaseTestPlan.tpl is not found in current directory: {os.getcwd()}',
                'Please cd to the root directory of testprogram where BaseTestPlan.tpl is.')

        # LC_ALL found? For unix
        confirm('LC_ALL' not in os.environ,
                'Env variable LC_ALL is found. This cause problem in reading testprogram files.',
                "Execute 'unsetenv LC_ALL' in your xterm and rerun script again. ")

        # no env found
        confirm(envs,
                f'No .env found: [{os.getcwd()}/{env_glob}]',
                'Where is the env file?')

    @classmethod
    def set_repo_sha(cls):
        """
        Called  by torch_mv or buildtp, given the repo
        Written by Misc().tpshainfo()
        """
        head = '.git/logs/HEAD'
        if not exists(head):
            cls.repo_sha = ('none', 'not_available_logs_head_not_found')
            return

        lines = [x for x in File(head).raw() if x.strip()]
        rsha = lines[-1].split()[1]    # 2nd element of last line

        head_file = '.git/HEAD'
        confirm(exists(head_file), f'Expecting: {head_file}', 'Contact jqdelosr right away')
        br = File(head_file).read().strip()
        if 'ref: refs/heads/' in br:
            br = br.replace('ref: refs/heads/', '')
        cls.repo_sha = (br, rsha)
        log.info(f'-i- git_ref: {br}')
        log.info(f'-i- git_sha: {rsha}')


class Units:

    # Below is mapping formula equivalent
    UNITS = {'ghz': '*1000000000',
             'mhz': '*1000000',
             'khz': '*1000',
             'hz': '',
             'ps': '*0.000000000001',
             'ns': '*0.000000001',
             'us': '*0.000001',
             'ua': '*0.000001',
             'ms': '*0.001',
             'mv': '*0.001',
             'ma': '*0.001',
             'v': '',
             'a': '',
             'c': '',
             }

    # Below is mapping numerical equivalent
    UNITMAP = {'ghz': 1000000000,
               'mhz': 1000000,
               'khz': 1000,
               'hz': 1,
               'ps': 0.000000000001,
               'ns': 0.000000001,
               'us': 0.000001,
               'ua': 0.000001,
               'ms': 0.001,
               'mv': 0.001,
               'ma': 0.001,
               'v': 1,
               'a': 1,
               'c': 1,
               }
    assert set(UNITS) == set(UNITMAP), 'UNITS and UNITMAP are not equivalent. Pls fix!'

    # Performance: staticmethod vs classmethod performance on py3 is almost the same

    _r_unit = re.compile(r'^([\d\.]+)(%s)$' % '|'.join(UNITS), re.IGNORECASE)
    _r_token = re.compile(r'[^\w\.]+|[\w\.]+')

    @classmethod
    def math_units(cls, val):
        """
        Replaces units (mV, nS) to numerical expression for eval later

        :param val: string expression with mV, etc
        :return: numerical expression
        """
        # Performance comparing search() vs findall(): 20455 calls, TGLXXXXRXH35H00S025 -tim_list p_bclkper_spec
        # _r_unit.findall(): 0.065    # Also, cleaner code from readability standpoint
        # _r_unit.search():  0.075
        if val.startswith('"') and val.endswith('"'):
            return val    # Do nothing, as it is quoted string
        final = []
        o_line = []
        for tok in cls._r_token.findall(val):
            o_line.append(tok)
            res = cls._r_unit.search(tok)
            if res:
                num = res.group(1)
                unit = res.group(2)
            else:
                final.append(tok)
                continue

            if unit.lower().endswith('hz'):
                new = '(1.0/(%s%s))' % (num, cls.UNITS[unit.lower()])
            else:
                new = '(%s%s)' % (num, cls.UNITS[unit.lower()])

            final.append(new)

        assert val == ''.join(o_line), 'Logic error: %r!=%r. Pls fix regex!' % (val, ''.join(o_line))
        return ''.join(final)

    _isunit = re.compile(r'^(-?[\d\.]+)(%s)$' % '|'.join(UNITMAP), re.IGNORECASE)

    @classmethod
    def to_number(cls, value) -> float:
        """
        Converts string value to float. Returns as-is if input is already number.

        :param value: string or int/float, eg. 10ns
        :return: float equivalent, or None if it can't be converted
        """
        if isinstance(value, (int, float)):
            return value

        if value in ('0nS', '0.0nS', '0V'):     # special case
            return 0.0

        if not value or value[0].isalpha() or value[0] == '(':
            return None     # Not a number

        # normal number
        try:      # try/except is faster than regex() filter  (2.5s vs 2.7s for 375K)
            return float(value)
        except BaseException:
            pass

        # with units
        res = cls._isunit.search(value)
        if res:
            if res.group(2).lower().endswith('hz'):
                return 1.0 / (float(res.group(1)) * cls.UNITMAP[res.group(2).lower()])
            else:
                return float(res.group(1)) * cls.UNITMAP[res.group(2).lower()]

        # Not a number
        return None


class SDiff:
    """
    Compare two lists (or two dict), sdiff style
    Assumption: lists content is unique and sorted
    arr1 and arr2 will be modified.

    Usage:
    SDiff().simple(sorted(list1), sorted(list2))
    Sdiff().keyval(d1, d2)
    """

    def _process(self, arr1, arr2, mode=0):
        """
        Process the diff

        :param arr1: list1 (will be modified)
        :param arr2: list2 (will be modified)
        :param mode: 0 for simple (<, >, |), 1 for < or > only
        """
        # Algo:
        # 1. Step through array1, first row to last row
        # 2. If array1 row match array2, then re-align (add blank rows) in array2. Goto next row. Done.
        # 3. Try to find array1 row in array2, If found, then re-align (add blank rows) in array1
        # 4. After everything is done, align both arrays to be same length (add blank rows)
        # Performance: Diff of 242152 lines, 75320 resulting diff, 28631 '|' lines, in 3.4 sec

        set_lines = set(arr2)
        ptr = 0      # index pointer of array2
        idx = -1     # index pointer of array1
        while True:
            idx += 1
            if idx == len(arr1):
                break
            if ptr == len(arr2):
                break

            line = arr1[idx]

            # exact match
            if line == arr2[ptr]:
                if ptr == idx or (not line):    # empty line is special case because of inserts
                    ptr += 1
                else:
                    # re-align arr2
                    for _ in range(idx - ptr):
                        arr2.insert(ptr, '')
                        ptr += 1
                continue   # proceed to next line

            # find for matching line
            found = 0
            if line in set_lines:    # for performance!
                try:
                    found = arr2.index(line, ptr + 1)
                except ValueError:       # on cases of duplicate lines
                    pass

            if found:
                if found - idx < 0:      # corner case - line is found after a mismatch
                    # re-align arr2
                    for _ in range(idx - found):
                        arr2.insert(found, '')
                        ptr += 1
                else:
                    # re-align arr1
                    for _ in range(found - idx):
                        arr1.insert(idx, '')
                        idx += 1
                    ptr = found + 1
            else:
                if mode:
                    arr2.insert(ptr, '')
                    ptr += 1

        # loop is done, make the length the same
        if len(arr1) < len(arr2):
            arr1.extend(['' for _ in range(len(arr2) - len(arr1))])
        if len(arr1) > len(arr2):
            arr2.extend(['' for _ in range(len(arr1) - len(arr2))])

        assert len(arr1) == len(arr2), f'Error: {len(arr1)} != {len(arr2)}. Must be equal!'

    def _assign_char(self, arr1, arr2):
        """Assign diff character per row"""
        assert len(arr1) == len(arr2), f'Error: {len(arr1)} != {len(arr2)}. Must be equal!'

        result = []
        for a, b in zip(arr1, arr2):
            if a == b:
                char = ' '
            elif not a and b:
                char = '>'
            elif a and not b:
                char = '<'
            else:
                char = '|'

            result.append(char)

        assert len(arr1) == len(result), f'Error: {len(arr1)} != {len(result)}. Must be equal!'
        return result

    def simple(self,
               arr1: list,
               arr2: list,
               col=60,
               mode=0,
               disp=True,
               diffonly=False,
               indent=0,
               autowrap=False,
               maxdisp=1000) -> list:
        """
        Do simple list compare: Will update arr1 and arr2

        :param arr1: sorted array1
        :param arr2: sorted array2
        :param col: column length. Set to zero for two line
        :param mode: 0 for simple (<, >, |), 1 for < or > only
        :param disp: Set to False to not display
        :param diffonly: Set to True to display diffonly
        :param indent: How many characters to indent
        :param autowrap: Set to True to show two-lines if len > col
        :param maxdisp: Max number of lines to display
        :return: char difference array
        """
        assert isinstance(arr1, list), f'Input {type(arr1)} must be list'
        assert isinstance(arr2, list), f'Input {type(arr2)} must be list'

        self._process(arr1, arr2, mode)
        char = self._assign_char(arr1, arr2)
        cnt = 0

        # Display
        if disp:
            ind = ' ' * indent
            template = f'{ind}%-{col}s %s %-{col}s'
            for a1, c, a2 in zip(arr1, char, arr2):
                if diffonly and c == ' ':
                    continue

                if col == 0 or (autowrap and (len(a1) >= col or len(a2) >= col)):
                    # Two line print
                    v1 = a1 if a1 else '(none)'
                    v2 = a2 if a2 else '(none)'
                    cn = '=' if c == ' ' else c
                    if cnt < maxdisp:
                        log.info(f'{ind}  {v1}')
                        log.info(f'{ind}{cn} {v2}')
                    cnt += 2
                else:
                    if cnt < maxdisp:
                        log.info(template % (a1, c, a2))
                    cnt += 1

        return char

    def keyval(self, d1: dict, d2: dict, col=60, disp=True, diffonly=False, indent=0, sep=' ',
               nc=False, autowrap=False) -> tuple:
        """
        Do key-val sdiff

        :param d1: first dictionary
        :param d2: second dictionary
        :param col: column length
        :param disp: Set to False to not display
        :param diffonly: Set to True to display diffonly
        :param indent: How many characters to indent
        :param sep: separator char between key and value
        :param nc: print no change if there are no changes
        :param autowrap: Set to True to show two-lines if len > col
        :return arr1, char, arr2
        """
        assert isinstance(d1, dict), f'Input {type(d1)} must be dict'
        assert isinstance(d2, dict), f'Input {type(d2)} must be dict'

        arr1 = sorted(d1)
        arr2 = sorted(d2)
        self._process(arr1, arr2, mode=1)
        char = self._assign_char(arr1, arr2)

        ind = ' ' * indent
        template = f'{ind}%-{col}s %s %-{col}s'
        fchar = []    # final char array
        for a1, c, a2 in zip(arr1, char, arr2):
            # update the char
            if c == ' ' and d1[a1] != d2[a2]:

                # make sure type is correct
                getnum1 = self.get_num(d1[a1])
                getnum2 = self.get_num(d2[a2])
                if ((isinstance(getnum1, int) and isinstance(getnum2, int)) or
                   (isinstance(getnum1, float) and isinstance(getnum2, float))):
                    _ = None    # equal to a "pass"
                else:
                    getnum1 = str(getnum1)
                    getnum2 = str(getnum2)

                if getnum1 < getnum2:
                    c = '+'
                else:
                    c = '-'

            fchar.append(c)

            if not disp:
                continue
            if diffonly and c == ' ':
                continue

            # set value to display
            v1 = f'{a1}{sep}{d1[a1]}' if a1 else ''
            v2 = f'{a2}{sep}{d2[a2]}' if a2 else ''

            # Display
            if col == 0 or (autowrap and (len(v1) >= col or len(v2) >= col)):
                # Two line print
                v1 = v1 if a1 else '(none)'
                v2 = v2 if a2 else '(none)'
                cn = '=' if c == ' ' else c
                log.info(f'{ind}  {v1}')
                log.info(f'{ind}{cn} {v2}')
            else:
                log.info(template % (v1, c, v2))

        if nc and (set(fchar) == {' '} or not fchar):
            log.info(f"{ind}No change")

        assert len(fchar) == len(char)
        return arr1, fchar, arr2

    def is_reorder(self, arr1, arr2, disp=False, ind=3, col=10):
        """
        Returns True if arr1 vs arr2 is reordered

        :param arr1: first array
        :param arr2: second array
        :param disp: Set to True to display detail
        :param ind: indent
        :param col: col length
        :return: True if arr1 vs arr2 is reordered
        """
        if arr1 == arr2:
            return []   # Do nothing is both array are the same

        # Do the diff
        arr1 = list(arr1)   # make a copy, so input is unchanged
        arr2 = list(arr2)   # make a copy, so input is unchanged
        self._process(arr1, arr2, mode=1)
        char = self._assign_char(arr1, arr2)

        # process and display
        set_arr1 = set(arr1)
        set_arr2 = set(arr2)
        ind_string = ' ' * ind
        template = f'{ind_string}%-{col}s %s %s'
        result = []         # list of reordered lines
        for a1, c, a2 in zip(arr1, char, arr2):
            cdisp = c
            if c == '<' and a1 in set_arr2 and a1 in set_arr1:
                result.append(a1)
                set_arr1.discard(a1)
                cdisp = 'R'
            if c == '>' and a2 in set_arr1 and a2 in set_arr2:
                result.append(a2)
                set_arr2.discard(a2)
                cdisp = 'R'
            if disp:
                log.info(template % (a1, cdisp, a2))

        return result

    @staticmethod
    def get_num(text, robj=re.compile(r'^(\d+)')):
        """Return the numeric portion if exist"""
        if not isinstance(text, str):
            return text   # return as-is
        res = robj.search(text)
        if res:
            return int('%6s' % res.group(1))
        return text

    @staticmethod
    def set2key(d1, do2, aligned=False):
        """
        Convert d1 with value of set() to string for easy keyval sdiff

        :param d1: dict with set() values
        :param d2: dict with set() values
        :param aligned: Set to True to align all keys
        :return r1, r2: r1 and r2 are dict with str values
        """
        # 1. match set first for the same key so that it is aligned
        # 2. For the rest of the keys, then incrementally add 1,2,3 etc
        # 3. No more sets for all items

        # because d2 is being modified, make a new copy
        d2 = {x: set(y) for x, y in do2.items()}
        r1 = {}   # result1
        r2 = {}   # result2

        # iterate to all keys in d1 first
        for k1, v1 in d1.items():
            v2 = d2.get(k1, set())

            # empty set()
            if not v1:
                if aligned:
                    r1[f'{k1}#0'] = ''
                else:
                    r1[k1] = ''
                continue

            for idx, item in enumerate(sorted(v1)):
                if aligned:
                    key = f'{k1}#{idx}'
                else:
                    key = f'{k1}-{idx}' if idx else k1
                if item in v2:
                    # exact match
                    r1[key] = item
                    r2[key] = item
                    v2.discard(item)
                else:
                    # this item not exist in the other
                    r1[key] = item

        # at this point r1 is complete. Iterate to all of d2 items
        for k2, v2 in d2.items():
            if not v2:
                if aligned:
                    if f'{k2}#0' not in r2:
                        r2[f'{k2}#0'] = ''
                else:
                    if k2 not in r2:
                        r2[k2] = ''
                    _ = 1     # nop, for coverage
                continue
            idx = -1
            for item in sorted(v2):
                for _ in range(10000):
                    idx += 1
                    if aligned:
                        key = f'{k2}#{idx}'
                    else:
                        key = f'{k2}-{idx}' if idx else k2
                    if key in r2:
                        continue
                    r2[key] = item
                    break
                else:     # pragma: no cover
                    raise Exception("CockpitError: max loop reached in set2key()")

        return r1, r2

    @staticmethod
    def count_diff(arr):
        """Returns the +0/-0/0 given array"""
        add = rem = cha = 0
        for item in arr:
            if item == '<':
                rem += 1
            elif item == '>':
                add += 1
            elif item != ' ':
                cha += 1
        return f'+{add}/-{rem}/{cha}'


class OtplFile:
    """Otpl reader (& text files)"""
    _ADV_CNT = [0]     # count of advance shlex

    def __init__(self, fname=''):
        """
        set fname to ".plist" if list is a .plist in readline()
        :param fname: filename (optional)
        """
        self.fname = fname
        assert not self.fname.endswith('.gz'), 'Otpl() cannot handle compressed files'

        # cache data for get_block(), populated by get_block()
        self.alines = None     # all lines original
        self.mlines = None     # modified lines

    def readline(self, iterlines=None, comments=False, emptyline=False):
        """
        Iterator, for opening otpl files and will return bracket char in it's own line
           and combine multi-lines into a single line.
        Line terminator is semicolon ";"
        Remove empty line, comment lines and trailing spaces.
        Remove comments within the line as well.
        Routine knows quotes.

        Usage:
        for lno, line in OtplFile(fname).readline():
            <dosomething>

        Strategy:
        1. The code in readline() is fast but cannot parse the line with brackets or semi-colon.
        2. The code in _otpl_bline() is slow but will parse the line correctly.

        :param iterlines: list of lines
        :param comments: Set to True to return comment line. It will not return EOL comments.
        :param emptyline: Set to True to return empty lines
        :return: lno, line
        """
        # Performance: 807K lines read in 35H testprogram, several mtpl:
        # Baseline open(): 0.250 Sec; OtplFile(): 0.897, 5396 _ADV_CNT; 2.291 Secs for 574220 _ADV_CNT.
        # Using cython is 17% faster
        assert self.fname or iterlines, 'Incorrect usage: Either provide filename or readline(input_list)'
        is_plist = self.fname.endswith('.plist')
        if iterlines is None:
            with open(File.realname(self.fname), 'rb') as fh:
                iterlines = fh.read().decode(errors='ignore').split('\n')

        alines = [x.replace('\t', ' ').strip() for x in iterlines]
        r_ctrcmnt = re.compile(r'^(\w+\s*,)\s*#')
        todore = re.compile(r'#USER TODO: define value.*$')
        maxlines = len(alines)
        for lno, line in enumerate(alines, start=1):

            # empty line
            if not line:
                if emptyline:      # pragma: no cover   - This is tested, python optimization is causing it. We want to keep python optimization though
                    yield lno, line
                continue

            # comment line
            if line.startswith('#'):
                if comments:
                    yield lno, line
                continue     # pragma: no cover - this is tested, coverage python thing

            # pure brackets
            if line == '{' or line == '}':
                yield lno, line
                continue

            # line that is pureword and ends with ','. eg. counters (need this for performance)
            if line[:-1].isidentifier() and line.endswith(','):
                yield lno, line
                continue

            # line that is pureword with comments, eg. counters
            if '#' in line and ',' in line:     # 57 occurence only in MTL
                _rescmnt = r_ctrcmnt.search(line)
                if _rescmnt:
                    yield lno, _rescmnt.group(1)
                    continue

            # items below are optimizations ================
            # simple end bracket with comment
            if line[0] == '}' and line[1:].strip().startswith('#'):    # 1.30 sec. If regex '^\}\s*\#': 1.60 sec
                yield lno, '}'
                continue

            # common case
            if line.endswith(('{', '}')):
                tline = line[:-1].strip()
                if (not ('}' in tline or '{' in tline or '#' in tline)) and tline.count(';') <= 1:
                    yield lno, tline
                    yield lno, line[-1]
                    continue

            # plist and #KEEP#
            if is_plist and line.endswith('#KEEP#'):
                line = line.replace('#KEEP#', '').strip()

            # Torch auto comment
            if line.endswith('#USER TODO: define value'):
                line = todore.sub('', line).rstrip()

            # end of optimizations =========================

            # bracket or comment or multiple ; or line does not end with ;
            if ('}' in line or
                    '{' in line or
                    '#' in line or
                    (not line.endswith(';') and lno != maxlines and not alines[lno].startswith(('{', '}'))) or
                    line.count(';') > 1):   # this is still faster than regex

                # print('%d ADV %d %r' % (self._ADV_CNT[0], lno, line))
                self._ADV_CNT[0] += 1     # counter for performance
                for item in self._otpl_bline(line, alines, lno, maxlines):
                    item = item.strip()
                    if item:
                        yield lno, item
                continue

            # normal line
            yield lno, line

    def _otpl_bline(self, line, alines, lno, maxlines,
                    maxloop=100000,
                    _r=re.compile(r'[^"\';\{\}#]+|#|;|""|\'\'|\{|\}|".+?"|\'.+?\''),
                    _requal=re.compile(r'^([^{]+= )(\{[^\}]*\})(.*)')):
        """
        Iterator: Process line and returns complete otpl lines, terminated by /;{}/
        Will split lines if several are in one line.
        Will combine lines if they are split in multiple lines.
        Will remove comment strings

        :param line: target string
        :param alines: full list of lines
        :param lno: current lineno to process
        :param maxlines: total elements in alines
        :param maxloop: maximum loop
        :param _r: regex for token split (quote aware)
        :param _requal: regex for tpie problem
        :return: complete otpl lines, brackets are returned by itself.
        """

        # special: check for "param = {var}". TPIE did not expand since it is not defined.
        if ' = {' in line:
            res = _requal.search(line)
            if res:
                yield f'{res.group(1)}"{res.group(2)}"{res.group(3)}'
                return

        for _ in range(maxloop):   # max of 100k loops

            # multi-line continuation - append
            if line.endswith('\\'):
                line = line[:-1] + alines[lno]
                alines[lno] = ''

            acc = []    # accumulator
            for item in _r.findall(line):

                if item == '#':
                    break   # This line is done, exit loop

                elif item == ';':
                    if acc:
                        acc.append(item)
                        yield ''.join(acc)
                        acc = []

                elif item == '}' or item == '{':
                    if acc:
                        yield ''.join(acc)
                        acc = []
                    yield item

                else:
                    acc.append(item)

            # remaining
            final = (''.join(acc)).strip()
            if final == '':
                return   # Done

            # this line is complete
            if final.endswith(';') or lno == maxlines or alines[lno].startswith(('{', '}')):
                yield final
                return   # Done

            # At this point, need to append next line, since this line is not complete.
            line = f'{final}{alines[lno]}'    # append
            alines[lno] = ''
            lno = lno + 1   # loop again
        else:
            raise Exception("Error: max loop on otpl_bline read. Check the file.")

    def text_readline(self):
        """
        Iterator: Plain text readline. Used with non-otpl text files.
        It will not return empty lines
        It will not return comment lines

        :return: lno, line.strip()
        """
        with open(self.fname, 'r') as fh:
            for lno, line in enumerate(fh, start=1):
                line = line.strip()
                if (not line) or line.startswith('#'):
                    continue

                if '#' in line:
                    # remove in-line comments
                    tmpline = ' '.join(x.strip() for x in self._otpl_bline(line, [''], 1, 1))
                    yield lno, tmpline.strip()
                else:
                    # normal line
                    yield lno, line

    def raw(self, islist=True):
        """
        Open the file, return "raw" lines, same method as readline().
        Use this when lineno must exactly match. There are cases when mixed multi-line will screw BdefFix()

        :return: list of lines with line endings
        """
        with open(self.fname, 'rb') as fh:
            alltxt = fh.read().decode(errors='ignore').rstrip()

        result_list = [f'{x.rstrip()}\n' for x in alltxt.split('\n')]
        if islist:
            return result_list
        else:
            return ''.join(result_list)

    def set_cache(self):
        """
        Assign self.alines and self.mlines
        """
        if not self.alines:
            with open(self.fname, 'r') as fh:
                self.alines = list(fh)
            self.mlines = list(self.readline())
        return self

    def get_block(self, block=None, name=None, elemno=1, parsed=False):
        """
        Iterator: given a block and name, return the lines for that block
        Returns the original line
        Routine is bracket aware.
        Returns first occurrence of block only

        :param block: name of block, example: DUTFlow
        :param name: example: IREF_TRIM_ATOM0
        :param elemno: element number. set to 2 for Test
        :param parsed: True for parsed line, False for original line
        :return: original lines with EOL char
        """
        self.set_cache()

        start = 0    # This is also the count of brackets
        complete = set()
        prev = 0
        for lno, line in self.mlines:
            # start logic
            if not start:
                elem = line.replace('(', ' ').split()
                if block:
                    # block name is defined
                    if elem[0] == block:
                        if name:
                            if len(elem) > 1 and elem[elemno] == name:
                                start = 1
                        else:
                            start = 1
                else:
                    # block name is empty, Apply only to Test and DUTFlow
                    if elem[0] == 'Test' and elem[2] == name:
                        start = 1
                    elif elem[0] == 'DUTFlow' and elem[1] == name:
                        start = 1

            if start and line == '{':
                start += 1
            if start and line == '}':
                start -= 1
            if start:
                if prev and lno != prev + 1:
                    for idx_u in range(prev, lno - 1):
                        if not parsed:
                            yield self.alines[idx_u]    # comment lines
                prev = lno
                if lno not in complete:
                    if parsed:
                        yield line
                    else:
                        yield self.alines[lno - 1]
                        complete.add(lno)
                if start == 1 and line == '}':
                    return   # done!

    def with_eol_comment(self):
        """
        Iterator: readline() wrapper that returns eol comments (and comments and empty lines)
        Returns lno, line
        """
        _rcmt = re.compile('(#.*?)$')
        olines = [''] + [x.replace('\t', ' ') for x in self.raw(islist=True)]
        for lno, line in self.readline(comments=True, emptyline=True):

            # add the EOL comment back from original line
            if line and (not line.startswith('#')) and '#' in olines[lno]:
                idx = olines[lno].find(line)
                if idx == -1:
                    # This means comment is "squashed"
                    cmnt = _rcmt.search(olines[lno])
                    line = f'{line}    {cmnt.group(1)}'
                else:
                    # simple case
                    comment = olines[lno][idx + len(line):].lstrip().rstrip()
                    if comment.startswith('#'):
                        line = f'{line}    {comment}'

            yield lno, line

    def reformat(self):
        """Reformat and rewrite the otpl file"""
        final = []
        cnt = 0
        for _, line in self.with_eol_comment():
            if not line:
                final.append('\n')
                continue

            if line.startswith('}'):
                cnt -= 1
            inds = '\t' * cnt
            final.append(f'{inds}{line}\n')
            if line.startswith('{'):
                cnt += 1

        if not final[-1].strip():
            del final[-1]   # Do not add extra line at end
        File(self.fname).rewrite(''.join(final), 'OtplFile.reformat()')


class MtplBlocks:
    """
    Read mtpl and put top level blocks into a dictionary,
    so it can be easily manipulated and be put together
    Usage:
    mb = MtplBlocks(fname)
    <manipulate mb.final>
    mb.write()
    """

    def __init__(self, fname):
        self.fname = fname
        self.head = []          # header part of otpl before the first block
        self.blocks = {}        # {blockname: list_of_lines}
        self.btype = {}         # {blockname: block_type_string}
        self.block_types = ('Test', 'CSharpTest', 'MultiTrialTest', 'DUTFlow', 'Flow')    # Ordered list of block types in mtpl

        # Read the file
        self.ofile = OtplFile(fname).set_cache()
        self.read()

        # Make a copy. Manipulate final for edits.
        self.final = dict(self.blocks)    # Final {blockname: list_of_lines}.

    def read(self):
        """
        Parse the .mtpl to create self.head and self.blocks
        """
        head = []
        original = {}
        btype = {}
        start = 0      # also count of brackets
        start_lno = name = nametype = None

        for lno, line in self.ofile.mlines:
            elem = line.split()
            if not start:
                confirm(not head, f"Error on {self.fname}, mismatched brackets found on line#{lno}", "Check file.")
                if elem[0] in self.block_types:
                    start = 1
                    head = self.ofile.alines[:lno - 1]
                else:
                    _ = None   # coverage only
                    continue

            # at this point, start is positive and header is done
            if line == '{':
                start += 1
                continue

            if line == '}':
                start -= 1
                if start == 1:
                    confirm(name and nametype,
                            f'Error on line#{lno} of {self.fname}: {line}',
                            f'No name found! Is the mtpl valid?')
                    original[name] = self.ofile.alines[start_lno - 1:lno]
                    btype[name] = nametype
                    start_lno = name = nametype = None
                _ = None   # coverage only
                continue

            if start == 1:
                nametype = elem[0]
                confirm(nametype in self.block_types,
                        f'Error Unknown type on line#{lno} of {self.fname}: {line}',
                        f'Contact jqdelosr to fix MtplBlocks()')
                start_lno = lno
                if nametype in ('Test', 'CSharpTest'):
                    name = elem[2]
                else:
                    name = elem[1]

        assert len(btype) == len(original), 'Algo problem! btype count != block count'
        self.head = head
        self.blocks = original
        self.btype = btype

    def write(self, caller, dest=None):
        """
        Write to output file
        method1: output is in a different folder (ARR_FUN_CXX_LINK -> ARR_FUN_CXX)  (dest == self.fname)
        method2: output is in the same folder (dest != self.fname)

        :param caller: name of caller
        :param dest: Destination file
        """
        if dest is None:
            dest = self.fname

        # Checks before writing
        if dest == self.fname:
            # make a copy of original
            File(self.fname).copy(f'{self.fname}.source')
        else:
            # Check if outputfile is "edited"
            orig = f'{dest}.orig.txt'
            if exists(orig) and File(dest).read() != File(orig).read():
                short = f'{basename(dirname(dest))}/{basename(dest)}'
                raise ErrorUser(f'{short} was modified. Compare {short} with original {short}.orig.txt '
                                f'first before overwriting.',
                                f'Delete {short}.orig.txt if you want to overwrite the mtpl.')

        # Write the output
        File(dest).rewrite(''.join(self.flatten_final()), f'{caller}()')

        # make a copy if method2
        if dest != self.fname:
            File(dest).copy(f'{dest}.orig.txt')

    def flatten_final(self):
        """
        Iterator: Given final dictionary, return flat list of lines
        :return: lines
        """
        # head first
        for line in self.head:
            yield line

        done = set()
        test_only = ('Test', 'CSharpTest', 'MultiTrialTest', None)
        assert set(test_only) == (set(self.block_types) - {'Flow', 'DUTFlow'} | {None})  # Cockpit: Pls update test_only or block_types
        for btype in test_only:
            for name in self.sort_dependent(self.final, btype):
                if btype is None or self.final[name][0].strip().startswith(f'{btype} '):
                    confirm(name not in done, f'Error! {name} is written twice.', f'Check {self.fname}')
                    for line in self.final[name]:
                        yield line
                    done.add(name)

        # Make sure everything is accounted for
        confirm(len(done) == len(self.final),
                f'Error! These blocks were not written: {self.final.keys() - done}',
                f'Check {self.fname}. Contact jqdelosr.')

    @staticmethod
    def sort_dependent(final, btype):
        """
        Return correct sorted keys. For DUTFlow, it should return correct order based on dependency.

        :param final: input dictionary
        :param btype: DUTFlow or Test, etc
        :return: sorted keys with correct dependency for btype='DUTFlow'
        """
        if btype:
            return sorted(final)

        # get all DUTFlow|Flow
        dutflow = {}   # {name: set_of_dependency}
        for item, lines in final.items():
            if lines[0].strip().startswith(('DUTFlow ', 'Flow ')):
                dutflow[item] = set()

        # Determine dependencies
        for item in dutflow:
            for line in final[item]:
                if line.strip().startswith('DUTFlowItem '):
                    elems = line.strip().split()
                    target = elems[2]
                    if target in dutflow:
                        dutflow[item].add(target)

        # sort it
        sortdict = MtplBlocks.dependent_values(dutflow)
        return sorted(dutflow, key=lambda x: (sortdict[x], x))

    @staticmethod
    def dependent_values(dutflow):
        """
        Generic / reusable routine
        Return a dictionary of item: integer based on dependent blocks.
        The integer is low if it has no dependence and high if it has dependence.

        Usage:
            data = MtplBlocks.dependent_values(dependents)
            result = sorted(data, key=lambda x: (data[x], x))

        :param dutflow: dictionary {item: set_of_dependent}
        :return: dictionary {item: integer}, for use with sorted()
        """
        # assign a value, 0 is unassigned. If all value is non-zero then this function is done.
        sortdict = {x: 0 for x in dutflow}

        # first pass - no dependency, assign to 1, aka, first
        ctr = 1
        for item in sorted(sortdict):
            if len(dutflow[item]) == 0:
                sortdict[item] = ctr    # no dependency
                ctr += 1

        for _ in range(500):    # max of 500 loops
            for target in sorted(sortdict):
                if sortdict[target]:
                    continue    # this target done already, do not reprocess

                # get the number to use
                value = 0
                for dependent in sorted(dutflow[target]):
                    if sortdict[dependent]:
                        value = max(value + 1, sortdict[dependent] + 1)
                    else:
                        value = 0   # this target is still unknown since dependent has no number. Process later.
                        break
                if value:
                    sortdict[target] = value   # found, so assign it

            # Are we done?
            done = True
            for item in sortdict:
                if not sortdict[item]:
                    done = False
            if done:
                break
        else:
            from pprint import pprint
            pprint(dutflow)
            raise ErrorUser("Cannot find ordering! See above for dependency.",
                            "Is there cyclic dependency among DUTFlow(s)?")

        return sortdict

    def recurse(self, block, result):
        """
        Get block, get all instances associated to this block, recurse if it is a DUTFlow (aka, composite)
        Assign in result

        :param block: target block name
        :param result: resultant dict {name: list_of_lines}
        :return: None
        """
        # get the lines of main block
        confirm(block in self.blocks,
                f'[DUTFlow {block}] is not found in {self.fname}',
                f'Pls check {self.fname} as this block is used')
        result[block] = list(self.blocks[block])    # make a copy, so original don't get modified

        # get the names of this block
        names = set()
        for _, line in OtplFile().readline(self.blocks[block]):
            elems = line.split()
            if elems[0] == 'DUTFlowItem':
                names.add(elems[2])

        # get the lines of testinstances (or composite)
        for name in names:
            if name not in result:
                confirm(name in self.blocks,
                        f'[{name}] is not found in {self.fname}. Used by [{block}] block.',
                        f'Pls check {self.fname} as this block is used.')
                result[name] = list(self.blocks[name])    # make a copy, so original don't get modified

        # recurse to all composites
        for name in names:
            elems = result[name][0].strip().split()   # First line
            if elems[0] == 'DUTFlow':
                self.recurse(elems[1], result)


class XmlRead:
    """
    Improved xml reader so if there is error it will give which filename.

    Usage:
    obj = XmlRead(fname).load()
    dict = XmlRead(fname).todict
    """
    def __init__(self, fname):
        self.fname = fname

    def load(self):
        """Returns etree object"""
        import xml.etree.ElementTree as ETree
        try:
            return ETree.parse(self.fname)
        except ETree.ParseError as e:
            raise ErrorInput(f"Error xml parse: {e}", f"Check {self.fname}")

    def todict(self):
        """
        Returns dictionary
        Wrapper around xml2dict but it will error out with filename.
        xml2dict is vanilla etree parse
        """
        import xml.etree.ElementTree as ETree
        try:
            return xmlfunc.xml2dict(self.fname)
        except ETree.ParseError as e:
            raise ErrorInput(f"Error xml parse: {e}", f"Check {self.fname}")


class JsonRead:
    """
    Improved python json reader because of:
    1. lines with comments: // comment stirng
    2. lines that has ',' at end and next line is } or ]
    3. Exception will display filename
    4. Ability to put suggestion

    Usage:
    data = JsonRead(fname).load()
    data = JsonRead(fname, 'Contact blah blah').load()
    """

    def __init__(self, fname, suggestion='Pls check the json file', error_out=True):
        self.fname = fname
        self.suggestion = suggestion
        self.error_out = error_out

    def load(self):
        """
        Main entry point - read the json
        :return: python data structure
        """
        with open(self.fname) as fh:
            try:
                data = json.load(fh)
                return data
            except json.decoder.JSONDecodeError:
                pass

        return self._process()

    def _process(self):
        """Do the processing. Previous json load failed"""
        final = File(self.fname).raw(islist=True)
        rcom = re.compile('^(.*)(//[^"]+)$')
        length = len(final)
        block_comment = False

        # remove first char unicode on first line
        if len('%r' % final[0][0]) != 3 and final[0][0].strip():
            final[0] = final[0][1:]

        # remove comment lines and block comments first
        for idx in range(length):
            line = final[idx].strip()

            # ignore block comments /* and */
            if line.startswith('/*') or block_comment:
                block_comment = True
                final[idx] = '\n'
            if line.endswith('*/'):
                block_comment = False

            # ignore lines that start with //
            if line.startswith('//'):
                final[idx] = '\n'

        for idx in range(length):
            line = final[idx].rstrip()

            nextline = ''
            for nidx in range(idx + 1, length):
                nextline = final[nidx].strip()
                if nextline:
                    break      # accept only non-blank next line

            # remove in-line comment
            if '//' in line:
                for tries in range(10):     # multiple comments in line
                    res = rcom.search(line)
                    if res:
                        final[idx] = res.group(1)
                        line = final[idx].rstrip()
                    else:
                        break

            # comma at end
            if line.endswith(',') and nextline.startswith(('}', ']')):
                final[idx] = line[:-1] + '\n'    # remove the comma

        try:
            return json.loads(''.join(final))
        except json.decoder.JSONDecodeError as e:
            # print(''.join(final))
            if self.error_out:
                raise ErrorInput(f"Error on [{os.path.abspath(self.fname)}]: json read exception: {e}", self.suggestion)
            else:
                return {}
