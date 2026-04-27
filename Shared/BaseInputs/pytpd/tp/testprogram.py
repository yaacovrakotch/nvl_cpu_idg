#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
testprogram module

Two type of Usage:
Usage#1: Application is specific to a testprogram (single stpl, or location)
    obj = TestProgram(<option>)
    obj.mtpl.methods()

Usage#2: Application is group of testprograms (all stpl's, or all sockets)
    obj = ProgramFamily(<group_of_testprograms>)
    obj.mtpl.methods()
"""
from os.path import join, dirname, basename, exists, isdir, abspath, isabs, realpath, isfile
from gadget.errors import ErrorInput, ErrorCockpit, ErrorCheck, confirm
from gadget.strmore import regex, group, sha1, to_list
from gadget.files import File, TempDir, basename_n
from gadget.disk import scandir_mtime, listdir_noerror, Chdir, delete_oldest_age
from gadget.helperclass import OPT, IS_UT
from gadget.gizmo import Elapsed
from gadget.pylog import log
from gadget.tputil import noquote, tuple_modname, OtplFile, XmlRead
from gadget.tvpv import TvpvEnv
from gadget.shell import IS_UNIX, IS_WIN
from gadget.dictmore import xmlfunc, find_dot_items, reverse_keyval
from tp.mtpl import Mtpl
from tp.timlvl import Timing, Usrv, Levels
from tp.pinsoc import PinSoc
from tp.plist import Plists
from collections import defaultdict, OrderedDict
from mod.setting import cfg
from pprint import pprint         # Don't remove, used for debug, demos or direct call
import xml.etree.ElementTree as ETree
import os
import re
import glob
import pickle


class TestProgram:
    """
    main object for testprogram
    mainly wrapper since most of the object is it's own class

    Class conventions:
    1. class __init__ should not do real work. Initializations in set_* methods.
    2. Methods call set_* methods if they need it. set_* methods can be called 1M times in 0.291 Sec (it is fast)
    3. set_* methods are set only once

    unit_test_protocol:
    0: unit test protocol with nothing enabled
    1: adds a check for PassFail property for all ports when parsing mtpl
    """

    _unit_test_protocol = 1 if not IS_UT else 0

    def __init__(self, envfile, stpl=None, soc=None, tpl=None, allplist=None, location=None, allpats=False, vars={}):
        """
        :param envfile: path to TP env file, TP directory or bare TP name
        :param tpl: path to tpl
        :param stpl: path to stpl
        :param soc: path to soc
        :param allplist: path to all plist file
        :param location: specify location string
        :param allpats: If True, include PreBurstPlist, PreBurst, etc
        :param vars: specify specific userv
        """
        # public attributes
        tp_real_path = self.tpname_to_path(envfile)
        env_file = self._find_env_file(tp_real_path)
        self.envfile = abspath(Env.xpath(env_file))      # absolute minimum
        self.envdir = dirname(self.envfile)
        self.env = Env(self.envfile)

        self.tpldir = self.env.get_hdmt_tpl_dir()
        self.tpl = self._derive_tpl(tpl)
        self.is_tos4 = self._is_tos4()
        self.env.is_tos4 = self.is_tos4       # cannot assign in earlier since code needs self.tpl
        self.testplan_base = self._get_testplan(self.tpl)
        self.soc = soc
        self.allplist = self._check_exist(allplist, self.tpldir)
        self.moddir = self._derive_moddir()
        self.allpats = allpats
        self.vars = vars
        self.is_tpie = not bool(glob.glob(f'{self.tpldir}/Shared*'))
        self.shareddir = self._derive_shareddir()

        # objects
        self.mtpl = Mtpl(self)
        self.plists = Plists(self)
        self.timing = Timing(self)
        self.levels = Levels(self)
        self.usrv = Usrv(self)
        self.locset = LocationSet(self, location)
        self.pgmrules = PgmRules(self)
        self.pin = PinSoc(self)

        # private attributes
        self._stpl = self._derive_stpl(stpl)    # optional, fullpath
        self._final_mtpl = None                 # Final programflow mtpl
        self._scope = {}                        # {'folder/file.mtpl': module_testplan_name}
        self._mtpl2ip = {}                      # {'folder/file.mtpl': ipname}
        self._mod2ip = {}                       # {module_testplan_name: ip}
        self._plist2ip = {}                     # {'filename.plist': ipname}
        self._read_plist_files = set()          # {'folder/PLIST_ALL.xml'}
        self._is_init = False
        self._check_validity()                  # last routine

    def tpname_to_path(self, tp_name):
        """
        TP name isn't always straight forward to find.  There are two primary paths it may exist in and some of the
        characters may be masked with 'X' in ways that are different for every product.
            Example Name:  TGLUTH6C0H16A20S025
            Match onDisk:  TGLXXXXCXH16A20S025
        :param tp_name:
        :type tp_name: str
        :return: Fullpath to the TestProgram directory
        :rtype: str
        """
        if isdir(tp_name) or isfile(tp_name):
            return tp_name

        # Try if input is bom name
        if isdir(f'POR_TP/{tp_name}'):
            return f'POR_TP/{tp_name}'

        # Check to see if the exact name was given first
        ipaths = self._get_idrives()
        for ipath in ipaths:
            fullpath = join(ipath, tp_name)
            if isdir(fullpath):
                return fullpath

        # Wasn't able to find the full name, look for a 'masked' version
        for ipath in ipaths:
            tps_found = [x for x in os.listdir(ipath) if isdir(join(ipath, x))]

            # We know that non of these names are an exact match, assume 'X' characters could match
            for tp in tps_found:
                tp_regex = tp.replace('X', '.')
                if re.search(tp_regex, tp_name):
                    return join(ipath, tp)

        raise ErrorInput("Unable to locate a TestProgram for: %s.  Please make sure you have the correct product "
                         "environment sourced or provide a fullpath to a valid .env file." % tp_name)

    @staticmethod
    def _find_env_file(tp_path):
        """
        Depending on how the user specifies the TP, do checks to located the .env file that is the main
        entry point for a TestProgram.
        :param tp_path: Fullpath to a testprogram. Can be a dir, or file at the top level of the TP
        :type tp_path: str
        :return: path to this TestProgram's Environment file
        :rtype: str
        """
        if isfile(tp_path):
            # This is the .env file you are looking for, return it
            if tp_path.endswith('.env'):
                return tp_path
            # Continue looking at the directory of the passed in file instead
            else:
                tp_path = dirname(tp_path)

        # Find the EnvironmentFile.env within the directory
        if isdir(tp_path):

            # try POR folder first
            result = glob.glob(f'{tp_path}/*_TP/*/*.env')
            for envfile in sorted(result):

                # ignore AHMT if there are multiple found: nvl case
                if len(result) > 1 and '_AHMT_' in envfile:
                    continue

                return envfile    # the first one

            # walk to all the folders
            for root, dirs, files in os.walk(tp_path):
                for ff in files:
                    if ff == 'EnvironmentFile.env':
                        return join(root, ff)

        raise ErrorInput("Unable to locate TestProgram's EnvironmentFile.env in %r" % tp_path)

    def pickle_key(self):
        """Return the pickle key"""
        all_mtimes = [mtime for f, mtime in scandir_mtime(self.tpldir) if not dirname(f).endswith('Reports')]
        sum_mtimes = sum(all_mtimes)

        return OrderedDict([('rev', self.pickle_rev()),
                            ('mtimes', sum_mtimes),
                            ('env', self.envfile),
                            ('stpl', self._stpl),
                            ('soc', self.soc),
                            ('tpl', self.tpl),
                            ('allplist', self.allplist),
                            ('loc', self.locset.location),
                            ('allpats', self.allpats),
                            ('vars', ' '.join([f'{k}={self.vars[k]}' for k in sorted(self.vars)]))])

    @staticmethod
    def pickle_rev():
        """Return the pickle key"""

        # Increment this when there are data struct changes
        # old rev1 - Initial Rev
        # old rev2 - Added self.pin object in init (but not automatically initialized)
        # old rev3 - patlist is as-is (do not remove IP)
        # old rev4 - (unused) plist to read Pat only (do not include PrePattern since these are precat or midamble)
        # old rev5 - Add patheader in plist to identify mainpat vs precats&ambles
        # old rev6 - location us based on PrimarySocketLocn usrv
        # old rev7 - moved mod.testprogram to tp.testprogram
        # rev1 - add envdir, mtpl's ttype, edata, new pickle filename with underscore. Torch capable version.
        # rev2 - add Env _env_stack_val in __init__()
        # rev3 - Read plist reference fix
        # rev4 - math_units hz fix
        # rev5 - plist reader to include PreBurstPList|PostBurstPList
        # rev6 - ternary fix and scientific number fix
        # rev7 - _scope attribute
        # rev8 - shareddir attribute
        # rev9 - math_units quoted string
        # rev10 - math_units quoted string improved for funcs("string")
        # rev11 - evaluate usrv local scoping fix
        # rev12 - _recurse_flow fix (seenloop)
        # rev13 - tos rule evaluate first then pgmrule, then final evaluate
        # rev14 - Added mtpl._dutflow_order
        # rev15 - Added mtpl._dutflow_at
        # rev16 - timlvl parsing improvement based on srf
        # rev17 - timlvl _userv add scoping
        # rev18 - add testplan_base
        # rev19 - new userv data structure
        # rev20 - mtpl mod2fname add
        # rev21 - add _mtpl2ip attribute
        # rev22 - timlvl separator due to PTL
        # rev23 - _plist2ip attribute
        # rev24 - plist RefPlist regex bug fix (Vicki feedback), 4/28/25
        return 24

    def _derive_tpl(self, tpl):
        """
        Derive tpl file if it is not defined
        Assume tpl file is in the same directory as envfile (self.tpldir)

        :param tpl:
        :return: tpl path
        """
        if tpl is not None:
            return tpl

        # TPIE: expect one file in TPL/ dir, parallel to env file
        target = self.tpldir
        found = glob.glob(join(target, '*.tpl'))

        # Torch - tpl is in <root>; given root/POR_TP/ATS_A0/EnvironmentFile.env
        if not found:
            target = dirname(dirname(self.tpldir))
            found = glob.glob(join(target, '*.tpl'))

        # Torch PTL
        if not found:
            target = self.envdir
            found = glob.glob(join(target, '*.tpl'))

        assert found, f'No .tpl found in {self.tpldir}. Pls specify which tpl to use in the object'
        assert len(found) == 1, f'Found two .tpl in {target}. Pls specify which tpl to use in the object'

        return abspath(found[0])

    def _derive_moddir(self):
        """Return the moduledir"""
        if self.tpl and isdir(join(dirname(self.tpl), 'Modules')):
            target = join(dirname(self.tpl), 'Modules')     # works for both tpie and torch
            assert isdir(target), f'Error: {target} does not exist. Where is it? Fix _derive_moddir()'
        else:
            target = join(self.tpldir, 'Modules')           # for unittests
        return target

    def _derive_shareddir(self):
        """Return the shared folder. If tpie, then return tpldir"""
        if self.is_tpie:
            return self.tpldir

        # get the Shared*, if one only then use it
        result = glob.glob(f'{self.tpldir}/Shared*')
        if len(result) == 1:
            return result[0]

        # open the tpconfig, get from SOCPath
        socpath = self.read_tpconfig('TestProgramFiles.SOCPath', default='../../Shared/blah/blah.soc')
        fpath = f'{dirname(self.envfile)}/{socpath}'
        return abspath(dirname(dirname(fpath)))

    def _derive_stpl(self, stpl):
        """
        Returns stpl file
        If stpl is not specified, the return the first one found.

        :param stpl: input stpl file
        :return: stpl file
        """
        if stpl:
            # if filename is just specified
            if stpl == basename(stpl):
                return join(self.envdir, stpl)

            return abspath(stpl)

        # See if stpl file exist based on env file
        target = join(self.envdir, f'SubTestPlan_{self.get_bom_from_env()}.stpl')
        if exists(target):
            return target

        target = join(self.envdir, 'SubTestPlan.stpl')
        if exists(target):
            return target

        # return the first occurrence, if not specified
        for ff in sorted(os.listdir(self.envdir)):
            if ff.endswith('.stpl'):
                return join(self.envdir, ff)

        return None     # used in unittest, get_stpl() will error anyway.

    def _get_testplan(self, fname):
        """Return the Testplan of the file"""
        if not fname:
            return "DEFAULTBASE"
        res = re.findall(r'^TestPlan\s+(\w+)', File(fname).read(), re.MULTILINE)
        if res:
            return res[0]   # first occurence
        return "DEFAULTBASE"

    @staticmethod
    def _check_exist(fname, path):
        """
        Check if fname exist (and make it full path)
        :param fname: input fname
        :param path: path where fname is
        :return: full path to fname
        """
        if not fname:
            return fname   # Do nothing
        if exists(fname):
            return abspath(fname)
        if exists(join(path, fname)):
            return join(path, fname)
        raise ErrorInput(f'Input file {fname} does not exist.')

    def init(self, skip=True, patload=True, light=False):
        """
        Testprogram initialize - similar to Tester's initialize

        Calling init() is optional: Don't call init() when you don't want pgmrules to take effect.
        You can call init() multiple times. If so, then pgmrules will be applied and timings/levels re-evaluated.

        :param skip: Set to False if re-init is desired.
        :param patload: Set to False to skip pattern init
        :param light: Set to True to initialize mtpl only. Patterns, usrv (eval), timing and levels are skipped
        :return: self, tp object
        """
        if skip and self._is_init:
            return self

        sw = Elapsed()

        # step1 - read mtpl and usrv, evaluate bypass value, needed by pgmrules
        self.mtpl.init_read()

        # step2 - apply pgmrules
        if light:
            pass
        else:
            self.usrv.set_data()        # evaluate will also happen here
            self.mtpl.eval_params()     # do tos rule first
            self.pgmrules.apply()       # timing and levels are initialized here
            self.mtpl.eval_params()     # re-evaluate all params after pgmrule

        # step3 - The rest of the reads
        if patload:
            self.plists.set_plb_map()   # Read the patterns (pgmrules may change patlist)
            self.plists.set_pat2plb()

        # step4 - Additional info adds
        self.mtpl.set_tn_attrib()

        # Below are already called by pgmrules.apply(). Don't call again ================
        # self.tp.timing.set_data()
        # self.tp.levels.set_data()
        # self.tp.locset.set_data()

        self._is_init = True

        log.info(f'-i- Completed init. _ADV_CNT={OtplFile._ADV_CNT[0]}, Elapsed={sw}')
        return self

    def check_init(self):
        """Error out if tp is not init"""
        assert self._is_init, "TestProgram is not init() yet. Pls init first."

    def pickle_init(self):
        """
        Check if pickle exist, if yes, load it, else, init and pickle save
        This must be called at start of routine

        Usage:
        tp = TestProgram(env).pickle_init()

        :return: testprogram Object
        :rtype: TestProgram
        """
        # get sha_key
        key = sha1(' '.join([str(y) for _, y in self.pickle_key().items()]))
        fname = join(cfg.pickle_dir, f'{self.pickle_rev()}_{key}.pickle')

        delete_oldest_age(cfg.pickle_dir, age=86400 * 7)

        is_pickle = True
        if not exists(fname):
            # init and save
            is_pickle = False
            self.init()

            # Do pickle clearing stuff (can't pickle lambda and functions)
            self.usrv.clear_cache()
            if '__builtins__' in self.usrv.uflat:       # pragma: no cover   # Problem only seen from test_sort_class_tp_diff
                del self.usrv.uflat['__builtins__']

            with open(fname, 'wb') as fh:
                pickle.dump(self, fh)
                log.info(f'-i- Created {fname} from {self.get_name()}')
            File(fname).chmod('0770')

        # make current object unusuable so it won't get accidentally used
        def errfunc(*x, **y):    # pragma: no cover
            """Raise an error when accessing a pickled TestProgram object directly."""
            raise ErrorInput("Incorrect use of pickle_init(). Use the TP object returned by pickle_init().",
                             "Correct usage: tp = TestProgram(<path>).pickle_init()")
        for item in [x for x in dir(self) if not x.startswith('__')]:
            setattr(self, item, errfunc)

        # so that output is consistent, return the unpickled object always
        with open(fname, 'rb') as fh:
            try:
                tp = pickle.load(fh)
            except Exception:    # catch all
                log.info(f'-i- Pickle File is {fname}')
                raise

            File(fname).touch()     # update mtime

            # populate lambdas and stuff
            tp.usrv.set_data()

            if is_pickle:
                log.info(f'-i- {tp.get_name()} will load from {fname}')
            return tp

    def is_torch_based_product(self):
        """Check if the test program follows a Torch-based directory structure.

        :return: True if the TP directory contains Modules, Shared, and POR_TP folders
        :rtype: bool
        """
        directories = os.listdir(self.envdir + '/../..')
        if 'Modules' not in directories:
            return False
        if 'Shared' not in directories:
            return False
        if 'POR_TP' not in directories:
            return False
        return True

    def get_stpl(self):
        """
        Return the stpl file

        :return: stpl file
        """
        if not self._stpl:

            raise ErrorInput("No .stpl file found in %s" % self.tpldir,
                             "Check if .stpl file exist, if yes, then you might be encountering 256 path limit in windows. "
                             "Rename your sandbox folder to be shorter name.")
        return self._stpl

    def get_all_mtpl_files(self):
        """
        Return all mtpl files from Module Dir (not considering stpl file)

        :return: list of mtpl paths (fullpath)
        """
        for mod in sorted(os.listdir(self.moddir)):
            for ff in sorted(listdir_noerror(join(self.moddir, mod))):
                if ff.endswith('.mtpl'):
                    yield join(self.moddir, mod, ff)

    def get_all_mtpl_from_stpl(self, ip='ALL', include_final=False):
        """
        Set self._final_mtpl value.
        Return all mtpl files from one stpl file.
        By default, This includes IP "Final" mtpl's.
        Set include_final to True to return self._final_mtpl as well

        :param ip: which mtpls to return. ALL for all.
        :param include_final: Include self._final_mtpl in the dict
        :return: Ordered dict of mtpl files
        """
        result = OrderedDict()
        ipname = None
        fname = self.get_stpl()    # stpl specified in input
        self._final_mtpl = None    # initialize

        r_ip = re.compile(r'^IPName\s+(\w+)')
        r_com = re.compile(r'^(Common\s*)?(\S+);')
        r_fin = re.compile(r'^Final\s+(\S+);')
        r_mtpl = re.compile(r'\b(\w+[/\\]\w+\.mtpl)')
        for lno, line in OtplFile(fname).readline():
            if line.startswith(('Version', '{', 'SubTestPlans')):
                continue
            line = line.replace('"', '')     # tos4 - remove quotes

            # ip logic
            res = r_ip.search(line)       # get IPName
            if res:
                ipname = res.group(1)
                continue
            if line == '}':       # clear IPName
                ipname = None
                continue

            if ip == 'ALL':                           # if input is 'ALL'
                # save it in dictionary
                res = r_mtpl.search(line)
                if res:
                    self._mtpl2ip[res.group(1).replace('\\', '/')] = ipname
            else:
                if ip != ipname:
                    continue       # allow only this specific ip

            # get modfile
            res = r_com.search(line)
            if res:
                modfile = res.group(2).replace('\\', '/')
                result[join(dirname(fname), modfile)] = True
                continue

            res = r_fin.search(line)
            if res:
                self._final_mtpl = join(dirname(fname), res.group(1).replace('\\', '/'))
                result[self._final_mtpl] = True    # assign this as module
                continue

            raise ErrorCockpit("Unknown stpl line: [%s]" % line)   # pragma: no cover

        if include_final or self._final_mtpl not in result:
            return result
        else:
            del result[self._final_mtpl]
            return result

    def _ref_plist_all_xml(self, fname):
        """
        Returns fname if IPReference does not exist.
        Returns a TempFile if exist, after reading all IPReference xml's

        :param fname: path to xml
        :return: fname
        """
        self._read_plist_files.add(fname)
        with File(fname) as fh:
            alltxt = fh.read()

        # populate self._plist2ip
        try:
            tree2 = ETree.parse(fname)
            root2 = tree2.getroot()
            for plist in root2.iter('PListFile'):
                plistname = plist.attrib.get('name')
                self._plist2ip[plistname] = None     # main IP
        except ETree.ParseError:
            log.info(f'-w- ParseError reading xml: {fname}')

        if 'IPReference' not in alltxt:
            return fname   # return as-is

        # read this file
        tree = XmlRead(fname).load()
        root = tree.getroot()
        plists = []
        for plist in root.iter('PListFile'):
            plists.append(plist.attrib.get('name'))
        for ref in root.iter('IPReference'):
            ip = ref.attrib.get('name')
            unix_path = ref.attrib.get('path').replace('\\', '/')
            self._read_plist_files.add(join(dirname(fname), unix_path))
            tree2 = XmlRead(join(dirname(fname), unix_path)).load()
            root2 = tree2.getroot()
            for plist in root2.iter('PListFile'):
                plistname = plist.attrib.get('name')
                # assert plistname not in plists, f"Error: {plistname} is defined twice in {unix_path}"
                plists.append(plistname)
                self._plist2ip[plistname] = ip

        self.tdir_xml = TempDir()
        tname = join(self.tdir_xml.get_name(), 'a.txt')
        with open(join(tname), 'w') as fh:
            for line in plists:
                fh.write('%s\n' % line)
        return tname

    def get_file_allplist_real(self):
        """
        Return the list of allplist files read
        :return: list
        """
        if not self._read_plist_files:
            self.get_file_allplist()
        return sorted(self._read_plist_files)

    def get_plist2ip(self):
        """
        Return dict {plistfilename.plist: IP}
        :return: dict
        """
        if not self._plist2ip:
            self.get_file_allplist()
        return self._plist2ip

    def _get_plist_from_tpconfig(self, bom):
        """
        Return the all_plist given the bom
        :return: None all_plist given bom
        """
        data = self.read_tpconfig(None)
        if not data:
            return None
        d1 = data.get('Configuration', {})
        d2 = d1.get('SupportedBomGroups', {})
        d3 = d2.get('BomGroup', [])
        for item in to_list(d3):
            if item.get('name') == bom:
                return f"{self.envdir}/{item['plist']}"
        return None

    def get_file_allplist(self, fnameonly=False):
        """
        Return the tp plist XML file that contains all of the reference plist names.
        :return: Fullpath to the Plist reference file
        :rtype: str
        """
        bom = self.get_bom()
        torch_plist = self.read_tpconfig("TestProgramFiles.PlistPath", default="na")
        bom_plist = self._get_plist_from_tpconfig(bom)
        for fname in (self.allplist,
                      f'{self.envdir}/PLIST_ALL.xml',         # TPIE
                      f'{self.envdir}/PLIST_ALL_{bom}.xml',   # TPIE w/ BOM
                      f'{self.envdir}/{torch_plist}',
                      f'{self.envdir}/all.plist.xml',         # Torch RPL
                      f'{self.envdir}/plist_all.plist.xml',   # Torch default1
                      f'{self.envdir}/PLIST_ALL.plist.xml',   # Torch default2
                      bom_plist,                              # Torch multi-bom (eg, srf)
                      ):
            if fname and exists(fname):
                if fnameonly:
                    return fname
                return self._ref_plist_all_xml(fname)

        raise ErrorInput("Cannot find %s/PLIST_ALL.xml." % self.envdir,
                         ("Pls check if this file exist. Contact jqdelosr if this error "
                          "persist, see get_file_allplist()."))

    def read_tpconfig(self, item, default=None, asis=False):
        """
        Read the tpconfig, if it exist, given the item
        :param item: key to find (example: BomGroup.plist)
        :param default: value (returned as-is)
        :param asis: Return the value asis (list)
        :return: single value, with backslash replaced or as-is=True, unique sorted list of Value of item
        """
        tpconfig = glob.glob(f'{self.envdir}/*.tpconfig')
        if len(tpconfig) == 0:
            return default
        assert len(tpconfig) == 1, f'How to handle multiple .tpconfig? {tpconfig}'

        data = xmlfunc.xml2dict(tpconfig[0])
        if item is None:
            return data   # as-is
        result = find_dot_items(data, item, default=default)
        if asis:
            return result
        if result == default:
            return result
        return result[0].replace('\\', '/')

    def _ut_write_stpl(self):
        """
        Write the stpl file for unittest
        Usage:
        tp = TestProgram('%s/env.env' % tdir, tpl='')._ut_write_stpl()

        :return: self
        """
        self._stpl = join(self.tpldir, 'a.stpl')
        code = 'SubTestPlans\n{\n'
        for mod in os.listdir(join(self.moddir)):
            for mtpl in glob.glob(join(self.moddir, mod, '*.mtpl')):
                code += '   .\\Modules\\%s\\%s;\n' % (mod, basename(mtpl))

        # Program flows
        if exists(join(self.tpldir, 'ProgramFlows.mtpl')):
            code += r'Final .\ProgramFlows.mtpl;\n'

        code += '}\n'
        File(self._stpl).write(code)

        return self

    def get_import_files(self, ext, withmodule=False):
        """
        Return ordered list of Import files with ext

        :param ext: extension, no dot
        :param withmodule: Set to True to return module
        :return: ordered dict of files, fullpath
        """
        result = OrderedDict()

        # open tpl first then modules next
        base = [self.tpl] + self._get_imp_from_tpl()

        for ff in base + list(self.get_all_mtpl_from_stpl()):
            for modl, item in self._read_for_import(ff, ext):
                if item in result:
                    continue    # Do not re-process the file
                if withmodule:
                    result[item] = (modl, ff)
                else:
                    result[item] = ff

        return result

    def _get_imp_from_tpl(self):
        """
        Return the import file from self.tpl

        :return: list of full path
        """
        bom = self.get_bomfolder()
        is_new_method = glob.glob(f'{self.shareddir}/*/*/Common_{bom}')

        restr = re.compile(r'^\s*Import\s+\"?(\S+\.imp)\b', re.MULTILINE)
        result = []
        # TODO: do not blindly get all files instead of use HDMT_TPL_something
        for item in restr.findall(File(self.tpl).read()):
            item = item.replace('\\', '/')     # NVPP case (from Yen Lee), import has path

            if is_new_method:
                # Collect dielet BOMs and _Files matches first
                dielet_bom = set(glob.glob(f'{self.tpldir}/*/*/*_{bom}/{item}') + glob.glob(f'{self.tpldir}/*/*/*_Files/{item}'))

                # Generic module usrv: exclude dielet BOM and _Files matches
                generic = [p for p in glob.glob(f'{self.tpldir}/*/*/*/{item}')
                           if p not in dielet_bom
                           and not re.search(r'_\w+$', basename(dirname(p.replace('\\', '/'))))]

                full_path = (glob.glob(f'{self.tpldir}/{item}') +  # TPL top level
                             list(dielet_bom) +
                             generic +
                             glob.glob(f'{self.shareddir}/*/*/Common_{bom}/{item}') +
                             glob.glob(f'{self.shareddir}/*/*/Common_Files/{item}'))

            else:
                full_path = (glob.glob(f'{self.tpldir}/{item}') +  # TODO: read paths in HDMT_OTPL_IMPORTS_PATH .env instead
                             glob.glob(f'{self.tpldir}/*/*/*/{item}') +  # NVL
                             glob.glob(f'{self.shareddir}/*/{item}') +
                             glob.glob(f'{self.shareddir}/*/*/*/{item}') +
                             glob.glob(f'{dirname(self.tpl)}/{item}'))    # same as top level (used with TPIE)

            # Allow if multiple and Common_Torch exist. Keep only Common_Torch.
            if len(set(full_path)) > 1:
                found = []
                for subi in full_path:
                    if not is_new_method and 'Common_Torch' in subi:
                        found.append(subi)

                if found:
                    full_path = found      # use this instead

            # Expect one only
            assert len(set(full_path)) == 1, f"Expecting 1 for {item}. Found: {set(full_path)}"

            result.append(full_path[0])

        return result

    def _read_for_import(self, ff, ext):
        """
        Iterator: Read one tpl or mtpl file

        :param ff: input file
        :param ext: ext to return
        :return: modulename, fullpath to the file
        """
        restr = re.compile(r'^\s*Import\s+(\S+\.%s)\b' % ext, re.MULTILINE)
        lines = []

        msg = '''Do the following:
   1. execute "git submodule update --init --recursive". It can be a shared module.
   2. Check if the .mtpl is really missing and debug why
   3. Update .stpl if the .mtpl should not exist
'''
        confirm(exists(ff),
                f'[{ff}] does not exist. Check .stpl: {self.get_stpl()}.',
                msg)

        with open(ff) as fh:
            for line in fh:
                lines.append(line)
                if line.startswith('{'):   # stop at first occurrence
                    break
            else:     # pragma: no cover
                None

        # get modulename
        testplans = re.findall(r'^TestPlan\s+(\w+)', ''.join(lines), re.MULTILINE)
        if testplans:
            modl = testplans[0]    # assume there is one only, so get first one
        else:
            modl = self.testplan_base

        imp_paths = [Env.xpath(x) for x in self.env.get_contents('HDMT_OTPL_IMPORTS_PATH', default='').split(';')]
        imp_paths += [self.tpldir]    # TOS adds this by default
        for item in restr.findall(''.join(lines)):
            for try_path in [dirname(ff)] + imp_paths:
                if item.startswith('"'):     # sometimes it has double quotes
                    item = item[1:]
                if item.startswith('./'):
                    item = item[2:]
                fpath = join(try_path, item.replace('\\', '/'))
                if exists(fpath):
                    yield modl, fpath
                    break
            else:
                raise ErrorInput(f"File [{item}] is not found from {[dirname(ff)] + imp_paths}",
                                 f"Check [{ff}]")

    def fullpath_tp(self, relative_path):
        """
        Return fullpath given relative path from module config files, e.g. inputfile = "./Module/something"

        :param relative_path: relative path from TPL/ folder. The value from mtpl config files.
        :return: fullpath
        """
        return join(self.tpldir, relative_path)

    def get_final_mtpl(self):
        """
        :return: Final mtpl ProgramFlows.mtpl
        """
        if not self._final_mtpl:
            self.get_all_mtpl_from_stpl()
        return self._final_mtpl

    def get_bomfolder(self):
        """Return the folder name after POR_TP, which is bom name used by NVL"""
        return basename(dirname(self.envfile))

    def get_bom(self):
        """Return the bom name used for this testprogram, from tpconfig or env filename"""
        # Try env file first
        bom = self.get_bom_from_env()
        if bom and (not bom.startswith('!')):
            return bom

        # Torch - get from tpconfig
        res = self.read_tpconfig('BomGroup.name', default=None)
        if res:

            # cannot return the folder name here since BinMatrix needs the exact string from tpconfig.
            # CTP will error if the foldername case-sensitive value is returned.

            return res    # return as-is

        # try stpl name
        res = re.search(r'SubTestPlan_(\w+)\.', self.get_stpl())
        if res:
            return res.group(1)

        # get from BinMatrix, first occurrence
        infile = f'{self.tpldir}/BinMatrix.xml'
        if exists(infile):
            res = re.findall(r'BOMGroup name=\"(\w+)\"', File(infile).read())
            assert res, f'No bomgroup found in {infile}. Is regex correct?'
            return res[0]

        return ''

    def get_bom_from_env(self):
        """
        Return the bom name based on env file

        :return: bom name or empty string if None
        """
        bname = basename(self.envfile)
        if 'EnvironmentFile_' in bname:
            bname = bname.replace('_TRCFAILED', '')
            bname = bname.replace('_CHKFAILED', '')
            return bname.replace('EnvironmentFile_', '').replace('.env', '')
        return ''

    def get_name(self):
        """
        Returns the testprogram name based on iCGL_TpAltName

        :return: testprogram name
        """
        # legacy
        from_usrv = self.usrv.get_var('RunTimeLibraryVars.iCGL_TpAltName', default="")
        if from_usrv:
            return from_usrv      # return it, if not empty

        # Sort
        from_usrv = self.usrv.get_var('SCVars.TP_PROGRAM_NAME', default="")
        if from_usrv:
            return from_usrv      # return it, if not empty

        # try pgmrules
        result = ''
        pgmrule = self.find_file('PGMRule_Base.txt')
        if not pgmrule:      # pragma: no cover  - temporary - cornercase from Sajeeth
            return result
        pgmdict = self.pgmrules._read_pgm_files(pgmrule, ('BASE', 'NA'))
        list_dict = pgmdict.popitem()[1]
        for item in list_dict:
            if item['var'] == 'iCGL_TpAltName':
                result = item['val']

        return result

    def get_family_name(self, bom_based=True):
        """
        Returns the 3 letter family name (lowercase)

        Algo:
        If bom_based==True, then use the BOM name (first 3 letters after Class_ if Class_ or, just first 3 letters)
        If bom_based==False, use first 3 letters of get_name(). Note: In NVL, this cannot be used bec there is only one value for all BOMs in .usrv

        :return:
        """
        if bom_based:
            if self.get_bomfolder().lower().startswith('class_'):
                return self.get_bomfolder().split('_')[1].lower()
            else:
                return self.get_bomfolder()[:3].lower()

        return self.get_name()[:3].lower()

    def get_tp_name(self):
        """
        Get the TestProgram name by looking at Path.
        Standard Path: /intel/hdmxprogs/tgl/TGLXXXXBXH13V20S015/TPL/
        Weird Path: /intel/tpvalidation/hdmxprogs/cml/CMLXXXXRXH29X5AS141/
        Sort path:  /intel/hdmxpats/tgl/sort_tp/tgl_sds/TGLSDSCA1H11U01S921/
        TORCH Path: /intel/hdmxprogs/rpl/RPLS8P5A0H10G11S043/POR_TP/RPL_1ST_SILICON/
        """
        # Start by trying to look from the Top of the path after 'hdmxprogs'
        dirs = os.path.normpath(self.envdir).split(os.sep)
        index = -1
        for prog in ['sort_tp', 'hdmxprogs', 'cmtprogs']:
            try:
                index = dirs.index(prog)
            except ValueError:
                pass

        # Make sure index was found and at least two more dirs exist
        if index != -1 and (index + 2) < (len(dirs) - 1):
            return dirs[index + 2]

        # Can't find name from top (non-standard area used), try looking from the bottom
        name = basename(self.envdir)
        return name if name != 'TPL' else basename(dirname(self.envdir))  # Go up one more directory

    def find_file(self, fname):
        """Try to find filename in tpldir, envdir or Shared*/Common"""
        shared = glob.glob(f'{self.shareddir}/*')
        for pp in [self.tpldir, self.envdir] + shared:
            found_path = f'{pp}/{fname}'
            if exists(found_path):
                return found_path

        return None   # not found

    def get_scope(self, fname, default):
        """
        Return the TestPlan name given the path

        :param fname: Path to mtpl or tcg file
        :param default: default value to return (e.g. Base)
        :return: scoping value or module name (aka, TestPlan name)
        """
        # assign it first if first time
        if not self._scope:
            for mtpl in self.get_all_mtpl_from_stpl():
                self._read_scope(mtpl)

        # return the mapping
        mtpl = fname.replace('\\', '/')
        key = f'{basename(dirname(mtpl))}/{basename(mtpl)}'

        # .mtpl case
        if key in self._scope:
            return self._scope[key]

        if fname.endswith('.mtpl'):
            return default

        # .tcg case (dirname)
        nmap = {}
        dup = set()
        for x, y in sorted(self._scope.items()):
            if dirname(x) in nmap:
                dup.add(dirname(x))
            nmap[dirname(x)] = y
        for item in dup:      # No duplicates in nmap
            del nmap[item]
        key = basename(dirname(mtpl))
        if key in nmap:
            return nmap[key]

        # default case
        return default

    def _read_scope(self, mtpl):
        """
        Read one mtpl file and populate self._scope
        :param mtpl: Inputfile
        :return: None
        """
        with open(mtpl, errors='ignore') as fh:    # fast way
            for line in fh:
                if line.strip().startswith('TestPlan '):
                    name = line.strip().split()[1].replace(';', '').strip()
                    key = f'{basename(dirname(mtpl))}/{basename(mtpl)}'
                    self._scope[key] = name
                    break
            else:
                if mtpl.endswith('.mtpl'):
                    raise ErrorInput(f"TestPlan line not found in {mtpl}", "Expecting TestPlan")

    def get_ipname(self, module):
        """
        Return the ip name given testplan module

        :param module: testplan module
        :return: ip name or None for ippkg
        """
        if not self._scope:
            self.get_scope('', '')    # intialize it

        # self._scope =   {'folder/file.mtpl': module_testplan_name}
        # self._mtpl2ip = {'folder/file.mtpl': ipname}

        r_scope = reverse_keyval(self._scope)
        confirm(module in r_scope,
                f'{module} is not found in any of the testplan names',
                f'Pls check if {module} is valid')
        key = r_scope[module]
        return self._mtpl2ip[key]

    def get_mod2ip_map(self):
        """
        Similar to get_ipname but return a dictionary
        :return: {module: ip}
        """
        if not self._scope:
            self.get_scope('', '')    # intialize it
        if self._mod2ip:
            return self._mod2ip

        result = {}
        for fname, module in self._scope.items():
            if fname.endswith('.mtpl'):
                result[module] = self._mtpl2ip[fname]
        self._mod2ip = result
        return self._mod2ip

    def bin_matrix(self, bom=None, _dd=None):
        """
        Returns dictionary of variables on bin matrix

        Usage: dd = tp.bin_matrix(tp.get_bom())

        :param bom: Specify bomgroup name. If empty, then read first one.
        :return: dict {bin: {attribute: value}}
        """
        result = {}
        if self.is_tpie:
            infile = f'{self.tpldir}/BinMatrix.xml'
        else:
            infile = glob.glob(f'{self.shareddir}/*/*.flm.xml') + glob.glob(f'{self.shareddir}/BaseInputs/Common/Common_Torch/*.flm.xml')
            if infile:
                infile = infile.pop()
            else:
                return result      # None found

        if not exists(infile):
            return result
        top = _dd if _dd else xmlfunc.xml2dict(infile)

        bomgroup = top['BinMatrix']['BOMGroupTable']['BOMGroup']
        if isinstance(bomgroup, dict):
            bomgroup = [bomgroup]
        for item_bg in bomgroup:
            if not bom:   # do the first one only
                bom = item_bg['name']
            if bom != item_bg['name']:
                continue

            flow = item_bg['ActiveFlowList']['Flow']  # ['binName']
            if isinstance(flow, dict):
                flow = [flow]
            for item_flow in flow:
                binname = item_flow['bin']
                result[binname] = {}

                attr = item_flow['Attribute']
                if isinstance(attr, dict):
                    attr = [attr]
                for item_attr in attr:
                    result[binname][item_attr['name']] = item_attr.get('_text', '')
                    if 'unit' in item_attr:
                        result[binname][item_attr['name']] += item_attr['unit']

        assert result, f'[{bom}] is not found in {infile}'
        return result

    def get_buildtype(self):
        """
        Returns ENG_TP or POR_TP, identifier for MV or fulltp
        :return: ENG_TP or POR_TP
        """
        return basename(dirname(dirname(self.envfile)))

    def is_eng_tp(self):
        """
        :return: True if loaded testprogram if from ENG_TP folder
        """
        return bool(self.get_buildtype() == 'ENG_TP')

    def get_builduser(self):
        """
        Reads the IntegrationReport.txt and determines the PDE who built the TP
        Also checks if pde is included in the cfg.pdxpdes
        :return: pde, vpde
                 pde = idsid
                 vpde = True of False
        """
        pder = re.compile(r'<TP Revision>(\s+)(\S+)(\s+).*')
        ir = f'{self.tpldir}/Reports/Integration_Report.txt'
        pde = 'grace'
        vpde = False
        if not exists(ir):
            raise ErrorCheck('TPIE integration report file is missing: %s' % ir,
                             'Double check the TPIE report is present:%s' % ir)
        with open(ir, 'r') as file:
            for line in file:
                line = line.strip()
                if '<TP Revision>' in line:
                    _pde = pder.search(line)
                    if not _pde:
                        raise ErrorCheck('Unable to acquire PDE from integ report!', 'Check if TPIE built correctly.')
                    if pde != _pde.group(2):
                        pde = _pde.group(2)
                        if pde in cfg.pdxpdes:
                            vpde = True
                        break

        return pde, vpde

    def get_module_folder_names(self):
        """Iterator: Returns sorted module folder names based on stpl"""
        for path in self.get_all_mtpl_from_stpl():
            if 'Modules' in path:
                yield basename(dirname(path))

    @staticmethod
    def _get_idrives():
        """
        TestPrograms usually live in one of two dirs:
           Class: /intel/hdmxprogs/<prd>/<name>
           Sort: /intel/hdmxpats/<prd>/sort_tp/<prd>_sds/<name>

        If no TVPV ENV is loaded (VEP or Flash), then auto-searching for idrives and TP Names won't work and no
        idrive results will be returned.
        :return: disks paths to check for TestProgram names
        :rtype: list
        """
        prod = TvpvEnv.get_tvpv_prodcode()
        ipaths = [
            join('/intel', 'hdmxprogs', prod),
            join('/intel', 'hdmxpats', prod, 'sort_tp', '%s_sds' % prod),
            join('/intel', 'tpvalidation', 'hdmxprogs', prod),
            join('/intel', 'cmtprogs', prod),
        ]
        return [x for x in ipaths if os.path.isdir(x)]

    def _is_tos4(self):
        """Returns True if testprogram is TOS4, as identified by Import " in .tpl file"""
        if self.tpl:
            alltxt = File(self.tpl).read()
            if '# TOS3 TP' in alltxt:
                return False
            return bool('Import "' in alltxt)

        return False   # Default

    @classmethod
    def dummy_tpobj(cls):
        """
        Returns a Dummy tpobj, uninitialized, for various use. It is a legit tpobject that you can initialize.
        tpobj is a real testprogram using Simple6tos4.
        The testprogram is created in tempdir, and will be deleted upon python exit.
        """
        import tarfile
        tdirobj = TempDir()
        tdir = tdirobj.name()
        roottp = dirname(realpath(__file__))
        with Chdir(tdir):
            tar = tarfile.open(f"{roottp}/simpletp.tar.gz", "r:gz")
            tar.extractall()
            tar.close()
        tpobj = cls(f"{tdir}/POR_TP/TGLH81/EnvironmentFile.env")
        tpobj._TDIROBJ = tdirobj
        return tpobj

    def _check_validity(self):
        """
        Various validity checks of testprogram
        This is performed early at init
        """
        # special check for NVL - cannot instantiate Shared env
        confirm(not basename_n(self.envfile, 4).startswith('Shared'),    # self.envfile is abspath at this point
                f'Cannot instantiate {self.envfile}',
                'Shared EnvironmentFile.env is not a valid .env file to use. Use the non Shared version.',
                cls=ErrorInput)


class Env:
    """
    Reads and holds env file info
    """

    def __init__(self, envfile, is_tos4=False):
        """
        :param envfile: Which envfile to read
        :param is_tos4: True for tos4
        """

        self.envfile = envfile
        self.is_tos4 = is_tos4

        # Below two data are used so we can re-write the .env file
        self._order = []      # list of keys or lines;   populated in set_env()
        self._env_dict = {}   # {key: 'longline'};       populated in set_env()
        self._env_stack_val = {}

    def set_env(self):
        """
        Read env file and put in a data structure
        self._order = []      # list of lines or keys
        self._env_dict = {}   # {key: 'longline'}

        :return: None
        """
        if self._env_dict:
            return   # Do nothing if already initialized

        self._read_env(self.envfile)
        self._clean_quotes()

    def _read_env(self, fname):
        """
        Read the env file including includes

        :param fname: file to read
        :return: None
        """
        re_item = re.compile(r'^(\w+)\s*=\s*\"(.*)\"')
        re_item2 = re.compile(r'^(\w+)\s*=$')
        re_subitem = re.compile(r'^\"(.*)\"')
        re_include = re.compile(r'^\$include\s+"([^"]+)"')
        key = None
        with open(fname, errors='ignore') as fh:
            for line in fh:
                line = line.strip()

                # empty line
                if not line:
                    continue

                res = re_include.search(line)
                if res:
                    self._read_env(f'{dirname(self.envfile)}/{Env.xpath(res.group(1))}')

                # key = "" line
                res = re_item.search(line)
                res2 = re_item2.search(line)    # no value
                if res or res2:
                    if res2:
                        res = res2

                    key = res.group(1)
                    self._order.append(key)
                    if key in self._env_dict:
                        self._env_stack_val[key] = self._env_dict[key]

                    if res2:
                        self._env_dict[key] = ""
                    else:
                        self._env_dict[key] = res.group(2)
                    continue

                # "" line
                res = re_subitem.search(line)
                if res:
                    self._env_dict[key] += res.group(1)
                    continue

                # everything else
                self._order.append(line)

    def _clean_quotes(self):
        """Remove "+" items in the env_dict - unnecessary"""
        robj = re.compile(r'(\"\s*\+\s*\")')
        for key, val in self._env_dict.items():
            if robj.search(val):
                self._env_dict[key] = robj.sub('', val)

    @staticmethod
    def to_unixpath(path, is_unix=IS_UNIX):
        """
        Return unix path

        :param path: windows path
        :param is_unix: Set to True for Unix call
        :return: unix path
        """
        result = path.replace('\\', '/').replace('//', '/')
        if not is_unix:    # pragma: no cover  - windows only
            return result
        for k, v in cfg.win2unix.items():
            result = result.replace(k, v)

        # catch all
        result = result.replace('I:/', '/intel/')

        return result

    @classmethod     # cannot use static method here since it messes up with Mock()
    def to_winpath(cls, path, sort=False, idrive=False):
        r"""
        Return windows I:\ path
        This will return None for MTL, since class TP does not include sort anyway

        :param path: unix path
        :param sort: Set to True to return sort path
        :param idrive: Set to True to return I:\ drive, if possible
        :return: string
        """
        if sort:
            for k, v in cfg.unix2win_sort.items():
                path = path.replace(k, v)
        else:
            for k, v in cfg.unix2win_class.items():
                path = path.replace(k, v)

        # \\amr.corp.intel.com\ec\proj\mdl\jf\intel\tpvalidation\jqdelosr
        # in windows, try to convert to I:\ drive path instead of global path
        if idrive and IS_WIN:
            trypath = realpath(path)
            trypath = trypath.replace('\\', '/')
            res = re.search(r'^(//.*\.intel\.com/.*?intel/)', trypath)
            if res:
                path = trypath.replace(res.group(1), 'I:/')

        path = path.replace('/', '\\')
        return path

    @staticmethod
    def xpath(path):    # unix/windows smart converter
        """Returns path that works in windows or unix"""
        result = path.replace('\\', '/')
        if exists(result):
            return result

        if IS_UNIX:
            return Env.to_unixpath(path)
        else:   # pragma: no cover  - windows only
            result = Env.to_winpath(path)
            return result.replace('\\', '/')

    def get_env_dict(self, stackval=False):
        """
        Returns the env dict
        :param stackval: Set to True to return stackval
        :return: env dict
        """
        self.set_env()
        if stackval:
            return self._env_stack_val
        else:
            return self._env_dict

    @classmethod
    def list_or_str(cls, item, islist):
        """
        Given item separated by ';', Return list or string depending on islist.
        :param item: input string
        :param islist: Set to True to return list (separated by ;)
        :return: list or string
        """
        if islist:
            return item.split(';')
        else:
            return item   # as-is

    def get_contents(self, item, default=None, as_is=False, islist=False, _max=1000):
        """
        Return the content of the env item after evaluating variables
        It will raise an error if the item is not found

        :param item: item in env file
        :param default: Default value if item is not existing. If None, then error out.
        :param as_is: Set to True to return as is
        :param islist: Set to True to return list
        :param _max: Max iteration
        :return: contents of that item (string)
        """
        self.set_env()   # fast

        if item == '~HDMT_TP_BASE_DIR' or item == '~HDMT_TPL_DIR':
            return self.get_hdmt_tpl_dir()

        if item not in self._env_dict:
            if default is None:
                raise ErrorInput('[%s] item is not found in env' % item,
                                 'Pls check %s' % self.envfile)
            else:
                return self.list_or_str(default, islist)

        # evaluate any variables
        value = self._env_dict[item]
        if as_is:
            return self.list_or_str(value, islist)

        if '$' in value:
            replacedict = dict(self._env_dict)    # make a copy
            replacedict[item] = self._env_stack_val.get(item, "")
            for _ in range(_max):
                if '$' not in value:
                    break
                value_py = re.sub(r'\$(\w+)', r'{\1}', value)
                try:
                    value = value_py.format(**replacedict)
                except KeyError as e:
                    raise ErrorInput(f"{e} is not defined but used in .env file",
                                     f"Check {self.envfile}")
            else:
                raise ErrorCockpit("Max number of iteration reached in get_contents()")

        value = value.replace('~HDMT_TPL_DIR', self.get_hdmt_tpl_dir())
        value = value.replace('~HDMT_TP_BASE_DIR', self.get_hdmt_tpl_dir())
        return self.list_or_str(value, islist)

    def get_hdmt_tpl_dir(self):
        """
        Returns the value of HDMT_TPL_DIR given the envfile
        Torch aware

        :return: tpldir
        """
        # get starting dir
        assert isabs(self.envfile), f'envfile=[{self.envfile}] must be abspath.'
        envdir = dirname(self.envfile)

        if exists(f'{dirname(dirname(envdir))}/Modules'):
            return dirname(dirname(envdir))    # Torch dir structure

        return envdir

    def get_plist_paths(self, var='HDST_PLIST_PATH'):
        """
        Return a list of plist paths given TP env. These will be the paths that a specific plist 'might'
        be in and can be searched in the future to find the location of plists in a TestProgram.

        :return: paths where plists are stored. Typically <idrive>/<prd>/<module>/<rev>/<patch>/plb
        :rtype: list
        """
        result = [self.to_unixpath(x) for x in self.get_contents(var).split(';')]
        return result

    def convert_fullpath(self, path):
        """
        Convert path to fullpath, considering env variables (~something)

        :param path: xml, input or patmod path
        :return: full path
        """
        self.set_env()   # fast
        if path.startswith('./Modules'):
            return path.replace('./Modules', join(self.get_hdmt_tpl_dir(), 'Modules'))
        if regex(r'^~(\w+)', path):
            envvar = group(1)
            if envvar not in self._env_dict:
                raise ErrorInput("[%s] is not found in %s" % (envvar, self.envfile))
            envpath = self.to_unixpath(self._env_dict[envvar])
            return path.replace('~' + envvar, envpath)
        return path   # do nothing

    def set_item(self, key, value):
        """
        Set this key to this value. value can be str or list
        If key is not in _order, then it will add at end

        :param key: variable name
        :param value: str or list
        :return: None
        """
        if key not in self._order:
            self._order.append(key)

        if isinstance(value, str):
            self._env_dict[key] = value
        else:
            self._env_dict[key] = ';'.join(value)

    def get_item(self, key, islist=False, default=None):
        """
        Get this key
        :param key: keyname
        :param islist: Set to True to return list
        :param default: default value to return. None to error out. Empty string to return empty.
        :return: str (default) or list
        """
        self.set_env()
        if key in self._env_dict:
            return self.list_or_str(self._env_dict[key], islist)

        if default is not None:
            return default

        assert key in self._env_dict, f'Error in Env("{self.envfile}": [{key}] is not found.'

    def del_item(self, key):
        """
        Remove this item
        :param key: variable name
        :return:
        """
        assert key in self._env_dict, f'Error in Env("{self.envfile}": [{key}] is not found.'
        del self._env_dict[key]
        self._order.remove(key)

    def rebuild(self, special=['NPR_FOLDER_PATH']):
        """
        Rebuilds the env file given data structure
        This will process $include into a single file, thus it comments out $include

        :special: list of special vars do not concatenate
        :return: full env text
        """
        result = []
        for item in self._order:
            if item[0].isalnum() or item[0] == '_':  # variable: first char is alphanumeric
                # assign value: list
                assert item in self._env_dict, f"Env variable error: [{item}] is not found in env_dict."
                value = self._env_dict[item].split(';')

                # convert to forward slash always for tos4, for path
                if self.is_tos4:
                    if self.get_item('TP_STRUCTURE', islist=False, default='TORCH') != 'TORCH_TO_SORT':
                        for idx in range(len(value)):
                            value[idx] = value[idx].replace('\\', '/')

                if item in special:
                    result.append(f'{item} = "{self._env_dict[item]}";')    # as-is
                elif len(value) == 1:
                    result.append(f'{item} = "{value[0]}";')
                else:
                    for idx in range(len(value)):
                        if idx == 0:
                            result.append(f'{item} = "{value[0]};" +')
                        else:
                            if idx + 1 == len(value):
                                result.append(f'    "{value[idx]}";')    # last one
                            else:
                                result.append(f'    "{value[idx]};" +')

                result.append('')  # space identifier

            else:   # print as is

                # $include is commented out - already processed
                if item.strip().startswith('$include '):
                    result.append(f'# {item}')
                    continue

                result.append(item)

        return '\n'.join(result)

    @classmethod
    def get_envfile(cls, path='.', firstonly=False):
        """Return the (only) envfile from current working dir"""
        wild = f'{path}/*_TP/*/*.env'
        res = glob.glob(wild) + glob.glob(f'{path}/*.env') + glob.glob(f'{path}/TPL/*.env')
        res = [x for x in res if not x.endswith('.g.env')]    # These are Torch autogenerated files on pobj cache
        if len(res) == 1:
            return cls.xpath(res[0])     # Straightforward, there is only one

        # pick POR_TP first
        final = []
        for item in sorted(res):
            if 'POR_TP' in item:
                final.append(item)

        confirm(firstonly or len(final) == 1,
                f'Found {len(final)} env file(s) in {os.path.abspath(path)}. Expecting one: {final}',
                f'Pls check the folder and see where the env file is: [{wild}]')
        confirm(len(final) >= 1,
                f'Found {len(final)} env file(s) in {os.path.abspath(path)}. Expecting one: {final}',
                f'Pls check the folder and see where the env file is: [{wild}]')
        return cls.xpath(final[0])

    @classmethod
    def get_root_dir(cls, envfile):
        """Return the root_dir of TP given envfile. Works for sort or class"""
        # class case
        root = dirname(dirname(dirname(abspath(envfile))))
        if exists(f'{root}/Modules'):
            return cls.xpath(root)

        # sort case
        root = dirname(abspath(envfile))
        if exists(f'{root}/Modules'):
            return cls.xpath(root)

        raise ErrorInput(f'Cannot derive tp root from {abspath(envfile)}. Modules/ folder cannot be found.',
                         f'Check the path. Where is Modules/ Folder?')

    @classmethod
    def get_nvlrzl_env(cls, root='.'):     # can act as is_nvlrzl()
        """
        Generic utility, given root tpl folder, return env files for nvl and rzl repos
        This routine can act as is_nvlrzl()

        :return: list of nvl, rzl env files
        """
        result = sorted(glob.glob(f'{root}/POR_TP/Class_NVL_*/EnvironmentFile.env') +
                        glob.glob(f'{root}/POR_TP/Class_RZL_*/EnvironmentFile.env'))
        result = [cls.xpath(_path) for _path in result]

        return result


class LocationSet:
    """
    Reads and Holds LocationSet and TP location

    This class will kick in once testprogram is init() (or PgmRules.apply() is called)
    """

    def __init__(self, tpobj: TestProgram, location: str):
        """Initialize LocationSet with TP object and optional location.

        :param tpobj: TestProgram object providing TP context
        :type tpobj: TestProgram
        :param location: Location string (e.g. 'CLASSHOT')
        :type location: str
        """
        self.tpobj = tpobj
        self.locset_file = None
        self._allmap = None        # {HOT: <set of values>}
        self._loc_code = None      # {HOT: <set of number codes>}
        self._code_loc = None      # {<number>: <set of string>}
        self.location = location   # Use uservar's PrimarySocketLocn value for default

    def set_data(self):
        """Reads the locationset file"""

        if self.locset_file:
            return

        # Derive locationset file
        target = (glob.glob(f'{self.tpobj.shareddir}/*/LocationsSets.*') +       # Torch version
                  glob.glob(f'{self.tpobj.tpldir}/LocationsSets.*') +            # TPIE version
                  glob.glob(f'{self.tpobj.shareddir}/*/*/*/LocationsSets.*'))    # NVL structure
        assert len(target) > 0, 'No LocationsSets.(txt|usrv) found. Where is it?'

        # prioritize on .txt - backwards compatible (If .txt is not up to date, then ask product to delete .txt)
        for item in sorted(target):
            target = item
            if item.endswith('.txt'):
                target = item
                break

        self.locset_file = target
        data, loc_code, code_loc, v_order = self._read_file()

        # assign
        self._allmap = self._eval_allmap(data, v_order)
        self._loc_code = loc_code
        self._code_loc = code_loc

        # Check testprogram location
        self._check_tploc()

    def _read_file(self):
        """Read locationset file"""
        is_usrv = self.locset_file.endswith('.usrv')
        r_var = re.compile(r"^(\w+)\s*=\s*(.*)$")
        r_n = re.compile(r'(\d+):(\w+)')
        r_nonly = re.compile(r'\b(\d+)\b')
        data = {}
        v_order = []
        loc_code = defaultdict(set)
        code_loc = defaultdict(set)
        for lno, line in OtplFile(self.locset_file).text_readline():
            # special .usrv handling
            if is_usrv:
                if line.startswith('Const String'):
                    line = line.replace('Const String', '').strip()
                if line.startswith(('Version', 'Shared', 'UserVars', '{', '}')):
                    continue
                line = line.replace('__shared__ ::', '')    # PTL case
                line = line.replace('__shared__::', '')     # BI case
                line = line.replace('LocationSets.', '')
                line = line.replace('LocationCategory.', '')
                line = line.replace('"," +', '')
                line = line.replace('"', '')
                line = line.replace(';', '')
                line = line.replace('[', '')
                line = line.replace(']', '')

            res = r_var.search(line)
            if res:
                var = res.group(1)
                val = res.group(2)

                for item in r_n.findall(val):
                    loc_code[item[1]].add(item[0])
                    code_loc[item[0]].add(item[1])
                    val = val.replace(f'{item[0]}:{item[1]}', f"'{item[1]}'")
                for item in r_nonly.findall(val):
                    loc_code[var].add(item)
                    code_loc[item].add(var)
                    val = val.replace(item, f"'{var}'")   # replace code with string

                assert not (',' in val and '+' in val), f'[{val}] contains both , and +. This is unexpected!'
                if ',' in val:
                    val = '{%s}' % val
                elif '+' in val:
                    val = val.replace('+', '|')   # so that python set will work
                elif val.startswith("'"):
                    val = "{%s}" % val

                v_order.append(var)
                data[var] = val
                continue

            raise ErrorInput(f'line [{line}] is invalid in line#{lno} at {self.locset_file}')    # pragma: no cover

        return data, loc_code, code_loc, v_order

    def _eval_allmap(self, data, v_order):
        """Evaluate allmap given data and v_order"""

        # eval all in order
        # Dumper(data)
        for var in v_order:
            try:
                data[var] = eval(data[var], data)
            except Exception as e:
                raise ErrorInput('Error on var %s=eval(%r)' % (var, data[var]),
                                 'Error message: %s' % e)

        # create allmap
        if '__builtins__' in data:       # pragma: no cover, pypy compatibility
            del data['__builtins__']     # this gets added automatically during eval global
        allmap = defaultdict(set)
        for item in data:
            allmap[item].update(data[item])    # This is to guarantee that all items in allmap are set

        # put all single item
        for key in list(allmap):
            for item in allmap[key]:
                if item not in allmap:
                    allmap[item].add(item)

        return allmap

    def _check_tploc(self):
        """
        Check tplocation and guess if not specified
        """
        # get valid locations
        valid = set()
        for items in self._allmap.values():
            valid.update(items)

        # try to guess
        if not self.location:
            val = self.tpobj.usrv.get_var('PrimarySocketLocn', default='CLASSHOT')  # get location from usrv
            val = val.split(':')[-1]
            self.location = self.num_to_location(val)

        # check
        if self.location not in valid:
            raise ErrorInput(f'location={self.location} is not valid',
                             'Valid values: %s' % ','.join(sorted(valid)))

    def num_to_location(self, loc):
        """Convert numeric loc to string"""
        if not loc.isdigit():
            return loc  # return as-is

        assert loc in self._code_loc, f"Location code [{loc}] is not found in {self.locset_file}"
        return sorted(self._code_loc[loc])[0]

    def is_valid(self, loc, lno, filename):
        """
        Returns True if this location code is valid for this testprogram

        :param loc: location to check
        :param lno: line number
        :param filename: which file
        :return: bool
        """
        self.set_data()

        if '/' in loc:
            target = dict(self._allmap)  # make a copy
            origloc = loc
            loc = loc.strip().replace(' ', '')   # remove spaces
            loc = loc.replace('/', '|')          # make it python set syntax
            loc = loc.replace('|-', '-')         # minus
            loc = loc.replace('|+', '|')         # add
            try:
                target = eval(loc, target)
            except Exception as e:
                raise ErrorInput('Error on input %r which is eval(%r)' % (origloc, loc),
                                 'Error message: %s' % e)

        else:
            assert loc in self._allmap, f'location={loc} is not valid, in line#{lno} of {filename}'
            target = self._allmap[loc]

        return bool(self.location in target)


class PgmRules:
    """
    Reads, Holds and apply PgmRules

    This class will kick in once testprogram is init()
    See initialize flows for required objects
    """
    # TODO: If testname not is not found, does it error?
    # TODO: Is glxexpress valid for non-init? Answer: Yes, valid, but glxexpress should not be bypassed by default
    # TODO: What happens on regex match partial (bl*100 vs blah100_SICC), does it match or not?

    def __init__(self, tpobj: TestProgram):
        """Initialize PgmRules with TP object and empty data structures.

        :param tpobj: TestProgram object providing TP context
        :type tpobj: TestProgram
        """
        self.tpobj = tpobj
        self._pgm_files = {}    # {file: (mod, tn)}

        # {mod_tn_f: [{'var': '',
        #              'val': '',
        #              'tn': '',
        #              'typ': '',
        #              'elem': 13_elem_list}]
        self._data = {}
        self._cnt_skip = 0    # Total items applied
        self._cnt_apply = 0    # Total items applied
        self._cnt_items = 0    # Total items

    def apply(self):
        """
        Apply pgmrules. re-apply() is ok (in cases where values are overwritten).

        Usage:
            tp = TestProgram(location='CLASSHOT')
            tp.pgmrules.apply()
            # Do stuff
        """
        # step1: Initialize required objects
        self.tpobj.mtpl.read_mtpls()        # test instances
        self.tpobj.mtpl.read_mtpl_flow()    # needed to get all INIT instances for glx express
        self.tpobj.usrv.set_data()          # uservars
        self.tpobj.timing.set_data(evaluate=False)
        self.tpobj.levels.set_data(evaluate=False)
        self.tpobj.locset.set_data()

        self._cnt_apply = 0    # Total items applied
        self._cnt_skip = 0     # Total items skipped
        self._cnt_items = 0    # Total items

        if not self._pgm_files:     # read only once

            # step2: grab all iCGlXpressTest in INIT flow
            for mod, tn, dd in self.tpobj.mtpl.iter_flows('INIT', template='iCGlXpressTest', bypass=True, edict=True):
                self._pgm_files[join(self.tpobj.tpldir, dd['gl_xpress_file_path'])] = (mod, tn)
            for mod, tn, dd in self.tpobj.mtpl.iter_flows('MAIN', template='iCGlXpressTest', bypass=True, edict=True):
                self._pgm_files[join(self.tpobj.tpldir, dd['gl_xpress_file_path'])] = (mod, tn)

            # step3: Read the pgmrules files
            for fname, mod_tn in self._pgm_files.items():
                self._data.update(self._read_pgm_files(fname, mod_tn))

        # step4: Apply pgmrules
        mapfunc = self._mapping()
        for mod_tn_file, items in self._data.items():
            for dd in items:
                self._cnt_items += 1
                self._apply_item(dd, mod_tn_file, mapfunc)

        # step5: evaluate timing and levels
        self.tpobj.timing.evaluate()
        self.tpobj.levels.evaluate()

        log.info(f'-i- PgmRule: Total items applied: {self._cnt_apply}. Skipped: {self._cnt_skip}. '
                 f'Add -pgmrule_disp to display')

    def _read_pgm_files(self, fname, mod_tn):
        """Read one pgm file, populate self._data"""
        # patlist = "fun_sa_sbft_chkSAQ_F6_list",   Template,   FUN_SA::SBFT_SA_VMIN_K_CHKSAQF6_X_X_3200_X_8C_45_1005 : *,*,*,*,*,*,*,*,*,*,*,*,CHOT
        #    0                 1                        2                                     3                           4 5 6 7 8 9 0 1 2 3 4  5

        # note: re.compile() is expensive during first time but python internally caches it:
        #       0.5 sec for 1M re.compile() for succeeding compiles.
        r_ln = re.compile(r'^([\w\.:]+)\s*=\s*(\"[^\"]+\"\s*|[^,]+),([^,]+),([^,]+),([^,]+),([^,]+),'
                          # tokens: 0                  1              2        3       4       5
                          r'([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),(.*)$')
        #   6       7        8      9       10      11      12      13      14    15

        # print(f"Processing {fname}")
        result = defaultdict(list)
        for lno, line in OtplFile(fname).text_readline():
            res = r_ln.search(line)
            if res:
                tokens = list(res.groups())

                # token 3 special handling
                sec_split = tokens[3].split(':')
                first_sec = ':'.join(sec_split[:-1]).strip()
                last_sec = sec_split[-1].strip()

                # remove spaces
                for idx in range(len(tokens)):
                    tokens[idx] = tokens[idx].strip()

                # val special handling
                tokens[1] = noquote(tokens[1])
                key = (mod_tn[0], mod_tn[1], fname)

                result[key].append({'var': tokens[0],
                                    'val': tokens[1],
                                    'typ': tokens[2],
                                    'tn': first_sec,
                                    'elem': [None, last_sec] + tokens[4:],
                                    'lno': lno})
                continue

            if line.startswith('KEY_DEFINITION'):
                log.info(f"-w- IGNORING pgm file: {fname} due to KEY_DEFINITION")
                return result

            raise ErrorInput(f'Invalid pgm line at lno#{lno} of {fname}; See below for actual line.\n'
                             f'{line}',
                             'Check logic or pgmfile')

        return result

    def _mapping(self):
        """Assign mapping"""

        # 1 : Package - SC_PACKAGE
        # 2 : Sample Type - SC_DEVICE
        # 3 : Processor Family - SC_DEVICE
        # 4 : Market Segment - SC_DEVICE
        # 5 : Cache Size - SC_DEVICE
        # 6 : DLCP category - SC_DEVICE
        # 7 : Unused (factory)- SC_DEVICE
        # 8 : Revision - SC_REV
        # 9 : Stepping - SC_STEP
        # 10: Eng ID - SC_ENGID
        # 11: Unused - SC_FABID
        # 12: Unused - SC_SSPEC
        # 13: Location sets - special, via location sets

        return {1: lambda: self.tpobj.usrv.get_var('SCVars.SC_PACKAGE'),
                2: lambda: self.tpobj.usrv.get_var('SCVars.SC_DEVICE')[0],
                3: lambda: self.tpobj.usrv.get_var('SCVars.SC_DEVICE')[1],
                4: lambda: self.tpobj.usrv.get_var('SCVars.SC_DEVICE')[2],
                5: lambda: self.tpobj.usrv.get_var('SCVars.SC_DEVICE')[3],
                6: lambda: self.tpobj.usrv.get_var('SCVars.SC_DEVICE')[4],
                7: lambda: self.tpobj.usrv.get_var('SCVars.SC_DEVICE')[5],
                8: lambda: self.tpobj.usrv.get_var('SCVars.SC_REV'),
                9: lambda: self.tpobj.usrv.get_var('SCVars.SC_STEP'),
                10: lambda: self.tpobj.usrv.get_var('SCVars.SC_ENGID'),
                11: lambda: self.tpobj.usrv.get_var('SCVars.SC_FABID'),
                12: lambda: self.tpobj.usrv.get_var('SCVars.SC_SSPEC'),
                }    # pragma: no cover

    def _apply_item(self, pgmdict, mod_tn_file, mapfunc):
        """
        Apply one pgm item in this module

        :param pgmdict: pgm dict
        :param mod_tn_file: (mod, testname, pgmrule_filename)
        :param mapfunc: dictionary mapping func
        :return unittest codes only
        """
        # {mod_tn_f: [{'var': '',
        #              'val': '',
        #              'tn': '',
        #              'elem': 12_elem_list}]

        # local vars
        typ = pgmdict['typ'].lower()
        var = pgmdict['var']
        val = pgmdict['val']
        tnm = pgmdict['tn']       # If single ':' is valid, then use: tnm.replace(':', '::').replace('::::', '::')
        elem = pgmdict['elem']
        lno = pgmdict['lno']

        self.disp(True, f'-d- PgmRule: About to Apply lno#{lno} {mod_tn_file[0]}/{basename(mod_tn_file[2])}', skip=None)

        # location set - element 13
        assert ',' not in elem[13], (f'Error: extra element on {elem[13]} '
                                     f'lno#{lno} {mod_tn_file[0]}/{basename(mod_tn_file[2])}')
        if elem[13] != '*' and not self.tpobj.locset.is_valid(elem[13], lno, mod_tn_file[2]):
            self.disp(1, (f'-i- PgmRule: skip locset: {elem[13]} vs {self.tpobj.locset.location} '
                          f'lno#{lno} {mod_tn_file[0]}/{basename(mod_tn_file[2])}'), skip=True)
            return 13

        # process all the rest of elements
        for idx in mapfunc:
            if elem[idx] != '*':
                valid = False
                for match in elem[idx].split('/'):
                    if match.startswith('-') and match[1:] != mapfunc[idx]():
                        valid = True
                    if match == mapfunc[idx]():
                        valid = True
                if not valid:
                    self.disp(1, (f'-i- PgmRule: skip idx={idx} {elem[idx]} != {mapfunc[idx]()} '
                                  f'lno#{lno} {mod_tn_file[0]}/{basename(mod_tn_file[2])}'), skip=True)
                    return idx

        # case typ
        if typ == 'template':
            if "::" in tnm:
                md, tn = tuple_modname(tnm)
            else:
                md = mod_tn_file[0]
                tn = tnm

            for oldval, realtn in self.tpobj.mtpl.set_instance(md, tn, var, val):
                self.disp(oldval, f"-i- PgmRule: Applying {var}={val} in {md}::{realtn}")

        elif typ == 'global':
            fvar = self._get_scoping_usrv(tnm, var)
            modl, _ = tuple_modname(tnm)
            if modl == 'BASE':
                modl = mod_tn_file[0]
            oldval = self.tpobj.usrv.set_var(fvar, val, mod_tn_file, testplan=modl)
            self.disp(oldval, f"-i- PgmRule: Applying {fvar}={val} from {oldval} in Global {tnm}")

        elif typ in ('timing', 'levels'):
            if typ == 'timing':
                obj = self.tpobj.timing
            else:
                obj = self.tpobj.levels

            # print(f"{mod_tn_file} {tnm} {var} {val}")
            for oldval, realtn in obj.set_param(tnm, var, val):
                self.disp(oldval, f"-i- PgmRule: Applying {var}={val} from {oldval} in {typ} for {realtn}")

        else:   # pragma: no cover
            raise ErrorInput(f"type=[{typ}] is unknown, in {mod_tn_file}",
                             "Contact jqdelosr")

    def disp(self, oldval, msg, skip=False):
        """
        Display PgmRule apply

        :param oldval: oldvalue
        :param msg: message string
        :param skip: Set to True to count skip
        :return: None
        """
        if oldval is None:
            return    # Do nothing, do not display

        if skip:
            self._cnt_skip += 1
        if skip is False:
            self._cnt_apply += 1

        if OPT.pgmrule_disp:
            log.info(msg)

    def _get_scoping_usrv(self, tnm, var):
        """
        Return the scoping given tnm

        :param tnm: pgmrules token#2
        :param var: variable name
        :return: correct scoping of var
        """
        # TODO: usrv should be per-ip. Removing IP for now: grep GBVars /intel/hdmxprogs/tgl/TGLXXXXBXH14P00S109/TPL/./Modules/TPI_BASE/InputFiles/PGMRule_GB.txt
        if '::' in tnm:
            tnm = tnm.split('::')[-1]

        if '::' in var:
            var = var.split('::')[-1]   # usrv does not have scoping

        if tnm.lower() in ('_uservars', 'none'):
            return var    # asis

        return f'{tnm}.{var}'

    def get_pgm_files(self):
        """Return dictionary of pgmfiles"""
        return self._pgm_files


class WrapMtpl:
    """Wrapper to mtpl public method to know multiple testprograms"""

    def __init__(self, famobj):
        """Initialize WrapMtpl with a ProgramFamily object.

        :param famobj: ProgramFamily object to wrap
        :type famobj: ProgramFamily
        """
        self.famobj = famobj

    def iter_tests(self, template_name=None, key_name=None):
        """
        Iterator: Return all testinstances (dictionary) - connected and unconnected - for all TP

        :param template_name: if specified, return testinstances with this template_name
        :param key_name: if specified, return testinstances that has key_name
        :return: (mod, testinstance_name, testinstance-dictionary, tpobj)
        :rtype: tuple
        """
        for tp in self.famobj:
            for item in tp.mtpl.iter_tests(template_name, key_name):
                yield item

    def get_modules(self):
        """
        Return all modules in all TP's sorted.
        :return:
        """
        mods = set()
        for tp in self.famobj:
            mods.update(tp.mtpl.get_modules())
        return sorted(mods)


class ProgramFamily:
    """
    Hold one or more testprogram.
    This class does not initialize the individual testprograms.

    Usage #1 - Many environment files (BOM group per env file):
    for tpobj in ProgramFamily('/path/mytpath/TPL').init_all_env():
        # do something in tpobj

    Usage #2 - Many stpl files (BOM group stpl, one env file):
    for tpobj in ProgramFamily('/path/mytpath/TPL').init_all_stpl():
        # do something in tpobj

    Note: tpobj must be init once only.
    """

    def __init__(self, tpldir):
        """
        :param tpldir: Testprogram dir
        """
        self._tp = {}    # Dictionary of tp objects
        self.tpldir = Env.xpath(tpldir)
        self.mtpl = WrapMtpl(self)

        assert isdir(self.tpldir), f'Error: {self.tpldir} is not a valid directory'

    def _init_family(self):
        """
        Initialize testprogram family

        :return:
        """
        # see if Plists() object can be shared
        result = set()
        for tp in self:
            result.add(File(tp.get_file_allplist()).sha1())

        if len(result) == 1:
            # assign only to one
            plistobj = None
            for tp in self:
                if not plistobj:
                    plistobj = tp.plists
                else:
                    tp.plists = plistobj

        # for item in self._tp:
        #     self._tp[item] = self._tp[item].pickle_init()

    def __iter__(self):
        """object Iterator: return all TestProgram objects"""
        for item in self._tp.values():
            yield item

    def init_all_env(self):
        """
        Read all env file in tpldir
        Usage: fam = ProgramFamily(tpldir).init_all_env()

        :return: self
        """
        for env in sorted(glob.glob(join(self.tpldir, '*.env'))):
            self._tp[env] = TestProgram(env)

        assert self._tp, f"Error: no env found in {self.tpldir}"
        self._init_family()
        return self

    def init_all_stpl(self, envfile=None):
        """
        Read all stpl given one env file
        Usage: fam = ProgramFamily(tpldir).init_all_stpl()

        :return: self
        """
        # Derive env first
        if not envfile:
            envfile = "EnvironmentFile.env"
        env = join(self.tpldir, basename(envfile))
        assert exists(env), f"Error: {env} does not exist. Pls check inputs"

        # assign
        for stpl in self.get_all_stpls():
            self._tp[stpl] = TestProgram(env, stpl=stpl)

        assert self._tp, f"Error: no stpls found in {self.tpldir}"
        self._init_family()
        return self

    def init_manual(self, list_tpobj):
        """
        Initialize manually

        :param list_tpobj: list of testprogram object
        :return:
        """
        # Do some checks first
        assert isinstance(list_tpobj, list), f'Input {type(list_tpobj)} must be a list of TestProgram objects'
        for item in list_tpobj:
            assert isinstance(item, TestProgram), f'Input {type(item)} must be TestProgram object'
            self._tp[str(len(self._tp))] = item

        self._init_family()
        return self

    def get_all_stpls(self):
        """
        Return full path to stpl files

        :return: list of stpl files
        """
        return sorted(glob.glob(join(self.tpldir, '*.stpl')))

    def any_tp(self):
        """Return a tpobj (sorted via key), for various things"""
        for tpx in sorted(self._tp):
            return self._tp[tpx]

    def iter_tp(self):
        """Return a tpobj (sorted via key), for various things"""
        for tpx in sorted(self._tp):
            yield self._tp[tpx]


##################################################################################
# make sure python is never used with -O. pytpd is dependent on the use of asserts.
##################################################################################
try:
    assert False
    raise ErrorInput("pytpd relies on assert statements. Pls turn off python -O")   # pragma: no cover - safety check only
except AssertionError:
    pass
###################################################################################


# TODO: Create a unittest so only tp.testprogram is imported outside
# CMD> pg ' tp\.' import | grep -v /test/ | grep -v tp.testprogram
