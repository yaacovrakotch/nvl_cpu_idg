#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
plist module
"""
from os.path import join, dirname, basename, exists
from gadget.errors import ErrorInput, confirm
from gadget.files import File
from gadget.gizmo import Elapsed
from gadget.pylog import log
from gadget.tputil import remove_ip, tid_from_pat, testname_from_pat, OtplFile, find_files_given_paths
from gadget.dictmore import reverse_set, reverse_keyval
from collections import defaultdict
import xml.etree.ElementTree as ETree
import os
import re
import glob


class Plists:
    """
    Class that holds loaded Patterns (through plists)

    # Get the list of CIPModules given TPL/<modules>
    list_cip_modules = Plists(envfile).get_cipmodules(['MARR_CORE'])

    # Get the all plist filenames used by all modules
    list_plist_filenames = Plists(envfile).get_plist_filenames()
    """

    def __init__(self, tpobj):
        """
        :param tpobj: TestProgram object
        :type tpobj: tp.testprogram.TestProgram
        """
        self.tpobj = tpobj
        self.envfile = tpobj.envfile
        self._plist_list = None        # set of path/<files.plist>, from PLIST_ALL.xml    # Populated in set_plist_list
        self._plb_map = None           # {plb_name: full_path_to_plist_file}              # Populated in set_plb_map
        self._plb_map_dup = None       # {plb_name: set(full_path_to_plist_file)}
        self._rev_paths = None         # set of path/rev/plb                              # Populated in set_all_revs
        self._available_plist = None   # set of <files.plist>, from i:\ drive             # Populated in set_all_revs
        self.error_out = True

        # Populated in set_pat2plb(): n: plb; nn: pat
        self._pat2nn = None         # {pat: nn}
        self._nn2pat = None         # {nn: pat}
        self._plb2n = None          # {plb: n}
        self._n2plb = None          # {n: plb}
        self._plb2pat = None        # {n: list(nn)}     # order is retained - flattened
        self._plb2patraw = None     # {n: list(nn)}     # order is retained - non-flat (allpats=True)
        self._pat2plb = None        # {nn: set(n)}
        self._plbchild = None       # {n: set(n)}       # children of n, including n itself
        self._patheaders = None     # {nn}              # set of pattern in headers (PreBurst, PrePattern)
        self._refplist = None       # {n: set(plb_referenced)}      # must set tpobj.allpats = True
        self._plbattr = None        # {n: {attr: value}}
        self._plb2any = None        # {n: list((plb|nn, 0|1))}      # for allpats=True only

        # Populated in get_pat_details()
        self._patopts = None        # {plb: {patn: {key: value}}}  Only populated for patts w/level options
        self._pattags = None        # {plbn: {patn: }} # cant be empty, that is patterns will not be here if no tags

    def set_plist_list(self):
        """
        Populate plist_list - list of path/<file>.plist

        :return: none
        """
        if self._plist_list:
            return    # Do nothing if already initialized.

        # get the all plist file
        env_paths = self.tpobj.env.get_plist_paths()    # list of paths
        apf = self.tpobj.get_file_allplist()

        # locate all .plist names
        plists = set()
        if apf.endswith('txt'):
            for plist in File(apf).chomp():
                plists.add(plist)
        else:
            tree = ETree.parse(apf)
            root = tree.getroot()
            for plist in root.iter('PListFile'):
                plists.add(plist.attrib.get('name'))

        msg = "Pls check testprogram Env file or Modules/*/*mconfig on where this file should be."
        self._plist_list = find_files_given_paths(plists, env_paths, msg, error_out=self.error_out)

    def set_all_revs(self):
        """
        Populate rev_paths - list of path/plb
        """
        if self._rev_paths:
            return    # Do nothing if already initialized

        result = set()
        for fp in self.tpobj.env.get_plist_paths():
            if not fp.endswith('/plb'):
                continue
            if not exists(fp):
                continue
            result.add(fp)

        self._rev_paths = result

        # open each paths and get all .plists
        all_plist = set()
        for fp in self._rev_paths:
            for ff in os.listdir(fp):
                if ff.endswith('.plist'):
                    all_plist.add(ff)

        self._available_plist = all_plist

    def set_plb_map(self, is_error=True):
        """
        Populate:
        self._plb_map = {plb_name: full_path_to_plist_file}
        self._plb_map_dup = {plb_name: set(full_path_to_plist)}

        :param is_error: Set to True to error out
        """
        if self._plb_map:
            return   # Do nothing if already initialized

        self.set_plist_list()
        plb_map = {}
        plb_map_dup = defaultdict(set)
        if self.tpobj.is_tos4:
            robj = re.compile(r'^\s*PList\s+(\w+)', re.MULTILINE)
        else:
            robj = re.compile(r'^\s*GlobalPList\s+(\w+)', re.MULTILINE)

        sw = Elapsed()
        for ff in sorted(self._plist_list):
            for item in robj.findall(File(ff).read()):
                if plb_map.get(item, ff) != ff:
                    if is_error:
                        raise ErrorInput("plb [%s] is both in %s and %s" % (item, plb_map[item], ff),
                                         "This is not allowed. Edit PLIST_ALL*.xml and remove one of the .plist")
                    else:
                        plb_map_dup[item].add(ff)
                        plb_map_dup[item].add(plb_map[item])

                plb_map[item] = ff

        self._plb_map = plb_map
        self._plb_map_dup = plb_map_dup

        log.info("-i- Finished reading in %s: %d GlobalPlists from %d .plist files"
                 "" % (sw, len(self._plb_map), len(self._plist_list)))

    def set_pat2plb(self):
        """Wrapper to _read_all_plists()"""
        if self._pat2nn:
            return   # Do nothing if already initialized

        self._read_all_plists()

    def _read_all_plists(self):
        """
        Read all plist files and store main patterns
        Populate pat2plb, plb2pat, pat2nn, nn2pat, plb2n, n2plb

        Performance: 1.5 sec, 56335 pats, 10798 plb (35H TP)

        :return: None
        """
        sw = Elapsed()

        # data structure
        pat2nn = {}                 # {pat: nn}
        nn2pat = {}                 # {nn: pat}
        plb2n = {}                  # {plb: n}
        n2plb = {}                  # {n: plb}
        plb2pat = defaultdict(list)  # {n: list(nn)}
        pat2plb = defaultdict(set)   # {nn: set(n)}
        plbchild = defaultdict(set)  # {n: set(n)}
        patheaders = set()           # {nn}    # list of pat in headers (PrePattern, PreBurst)
        refplist = defaultdict(list)  # {n: list(plb)}
        n2plist = {}                  # {n: plist}  # internal only
        plbattr = defaultdict(dict)   # {n: {attr: value}}, populated only if is_allpats
        plb2any = defaultdict(list)   # {n: list(plb|nn, 0|1)}

        stack = []
        is_allpats = self.tpobj.allpats
        r_burst = re.compile(r'\b(BurstOff|BurstOffDeep)\b')

        if not self.tpobj.is_tos4:
            # TOS3 ================================================
            if is_allpats:
                r_pat = re.compile(r'\b(PrePattern|PreBurst|PostBurst|PostPattern|Pat|KeepAlive)\s+(\w+)')
                r_plist = re.compile(r'\b(PList|PreBurstPList|PostBurstPList|PrePList|PostPList)\s*(\w+)')
            else:
                r_pat = re.compile(r'\b(PrePattern|PreBurst|Pat)\s+(\w+)')
                r_plist = re.compile(r'^(PList)\s*(\w+)')

            r_plb = re.compile(r'^GlobalPList\s*(\w+)\b')
            r_valid = re.compile(r'^(Pat|Version|GlobalPList|PList)\b')
        else:
            # TOS4 ===============================================
            r_pat = re.compile(r'^(PreExecPat|PostExecPat|Pat)\s+(\w+)')
            r_plist = re.compile(r'^(PostExecRefPList|RefPList|PreExecRefPList)\s*(\w+)\b')
            r_plb = re.compile(r'^PList\s*(\w+)\b')
            r_valid = re.compile(r'^(Pat|Version|PList|PostExecRefPList|RefPList|PreExecRefPList|PreExecPat|PostExecPat)\b')

        for ff in sorted(self.get_plist_list()):
            for lno, line in OtplFile(ff).readline():       # use read_plist() to read one specific file for debug

                # globalplist line
                is_glob_line = False
                res = r_plb.search(line)
                if res:
                    is_glob_line = True
                    plb = res.group(1)
                    plb2n[plb] = len(plb2n)
                    n = plb2n[plb]
                    n2plist[n] = basename(ff)
                    n2plb[n] = plb
                    stack.append(n)
                    for x in stack:
                        plbchild[x].add(n)

                    if is_allpats:
                        res_burst = r_burst.search(line)
                        if res_burst:
                            plbattr[n][res_burst.group(1)] = True
                        # add in previous stack
                        if len(stack) > 1:
                            plb2any[stack[-2]].append((plb, 0))

                if line == '}':
                    stack.pop()
                    continue

                # main pattern line
                for kw, pat in r_pat.findall(line):
                    if pat not in pat2nn:
                        pat2nn[pat] = len(pat2nn)
                        nn2pat[pat2nn[pat]] = pat
                    nn = pat2nn[pat]
                    pat2plb[nn].update(stack)
                    if kw != 'Pat':
                        patheaders.add(nn)
                    for x in stack:
                        plb2pat[x].append(nn)
                    if is_allpats:
                        if is_glob_line:
                            plbattr[n][kw] = pat
                        else:
                            plb2any[n].append((nn, 1))

                # Plist reference
                for attr, plb1 in r_plist.findall(line):
                    for x in stack:
                        refplist[x].append(plb1)
                        plb2pat[x].append(plb1)
                        # Value above is temporary, will resolve later, since plb1 is not yet read.
                        # However, need to add it here to maintain correct order

                    if is_allpats:
                        if is_glob_line:
                            plbattr[n][attr] = plb1
                        else:
                            plb2any[n].append((plb1, 0))

                # UserBurstBreak - throw away, don't know what to do with this for now
                if line.startswith('UserBurstBreak'):
                    continue

                # Make sure all lines are processed
                if r_valid.search(line) or line == '{':
                    continue
                raise ErrorInput(f"Invalid line#{lno}: [{line}] in {ff}.")

        # process refplists
        for x in refplist:
            for plb in refplist[x]:

                # check first if it exist (common error)
                if plb not in plb2n:
                    dd = reverse_set(self.get_mod2plist_map())   # {plist: set_of_mods}
                    mod = dd.get(n2plist[x], 'MOD_NOT_FOUND')
                    raise ErrorInput(f'GlobalPList {plb} is not found.',
                                     f'Referenced in {n2plb[x]} of {n2plist[x]} of module={mod}')

                # add in plbchild
                n_plb = plb2n[plb]
                plbchild[x].add(n_plb)

        if is_allpats:
            self._plb2patraw = {x: list(y) for x, y in plb2pat.items()}      # make a copy

        # resolve plb2pat keys (name to number)
        for x in list(plb2pat):
            for _ in range(1000000):     # while loop (limited)
                found = False
                for idx in range(len(plb2pat[x])):
                    if not isinstance(plb2pat[x][idx], int):
                        to_insert = []
                        n_plb = plb2n[plb2pat[x][idx]]
                        for nn in plb2pat[n_plb]:
                            to_insert.append(nn)
                            if plb2pat[x][idx].startswith('resetplb_'):
                                patheaders.add(nn)
                        plb2pat[x][idx:idx + 1] = to_insert
                        found = True
                        break
                if not found:
                    break
            else:    # pragma: no cover
                raise Exception("loop exceeded, something went wrong!")

        # assign
        self._refplist = refplist
        self._pat2nn = pat2nn
        self._nn2pat = nn2pat
        self._plb2n = plb2n
        self._n2plb = n2plb
        self._plb2pat = plb2pat
        self._pat2plb = pat2plb
        self._plbchild = plbchild
        self._patheaders = patheaders
        self._plbattr = plbattr
        self._plb2any = plb2any

        log.info("-i- Finished reading in %s: %s pats from %s files" % (sw, len(pat2nn), len(self._plist_list)))

    def read_plist(self, plistfile):
        """
        Given a specific plist file, Read it and populate data structure.
        This routine is for DEBUG/adhoc use given 1 specific plist.
        WARNING: It will clear all plist data loaded in tpobj.

        :param plistfile: Can be a list-of-filenames or a filename
        :return: None
        """
        # Clear everything
        self.__init__(self.tpobj)

        # Set the input plistfile
        if isinstance(plistfile, list):
            self._plist_list = plistfile
        else:
            self._plist_list = [plistfile]

        # Read it
        self.set_pat2plb()

    def get_pats_from_plb(self, plb, order=False, patonly=False, iserror=True, ref=True):
        """
        Return set of pats given plb

        :param plb: plbname
        :param order: Set to True to return list (order is retained) instead of set
        :param patonly: Set to True to return main patterns only (PreBurst and PrePattern removed)
        :param iserror: Set to False to not error (since some patlist are missing due to bypassed)
        :param ref: Set to False to not return refplists
        :return: set of pats
        :rtype: set
        """
        self.set_pat2plb()

        if ref:
            plb2pat = self._plb2pat
        else:
            plb2pat = self._plb2patraw
            confirm(plb2pat is not None,
                    f'ref=True requires allpats=True in testprogram object',
                    'Pls use a testprogram object with Testprogram(allpats=True)')

        plb = remove_ip(plb)
        if plb not in self._plb2n:
            if iserror:
                raise ErrorInput("Error: [%s] is not found in any of the plists" % plb,
                                 "Pls check if this plist actually exist")
            else:
                log.info(f'-w- [{plb}] is not found in any of the loaded plists.')
                return set()

        if patonly:
            rem = self._patheaders
        else:
            rem = set()

        nn2pat = self._nn2pat
        if order:
            result = [nn2pat[x] for x in plb2pat[self._plb2n[plb]] if x not in rem and x in nn2pat]
        else:
            result = {nn2pat[x] for x in plb2pat[self._plb2n[plb]] if x not in rem and x in nn2pat}

        return result

    def get_plbs_usedby_pat(self, pat):
        """
        Return set of plbs used by pat

        :param pat: patname
        :return: set of plbs
        :rtype: set
        """
        self.set_pat2plb()
        assert pat in self._pat2nn, "Error: [%s] is not found in any of the plists" % pat
        result = {self._n2plb[x] for x in self._pat2plb[self._pat2nn[pat]]}
        return result

    def get_plbs_usedby_pats(self, pats):
        """
        Return dict of plbs used by pat

        :param pats: set of patnames
        :return: dict: {pat: set_of_plb}
        :rtype: dict
        """
        self.set_pat2plb()
        result = defaultdict(set)
        for pat in pats:
            if pat in self._pat2nn:
                for x in self._pat2plb[self._pat2nn[pat]]:
                    result[pat].add(self._n2plb[x])
        return result

    def get_pats_all(self):
        """
        Return all pats

        :return: set of pattern names
        :rtype: set
        """
        self.set_pat2plb()
        return self._pat2nn.keys()

    def get_plb_map(self):
        """
        Return plb_map dict

        :return: plb_map dict {plb_name: full_path_to_plist_file}
        :rtype dict
        """
        self.set_plb_map()
        return self._plb_map

    def get_plist_list(self):
        """
        Return plist_list: set of path/<files.plist>, from PLIST_ALL.xml

        :return: set of path/<files.plist>
        :rtype: set
        """
        self.set_plist_list()
        return self._plist_list

    def get_rev_paths(self):
        """
        Return plist_list: set of path/rev/plb

        :return: set of path/rev/plb
        :rtype: set
        """
        self.set_all_revs()
        return self._rev_paths

    def get_available_plist(self):
        r"""
        Return available_plist: set of <files.plist>, from i:\ drive

        :return: set of <files.plist>
        :rtype: set
        """
        self.set_all_revs()
        return self._available_plist

    def get_subplists(self, plb):
        """
        Return list of subplists given plb

        :param plb: patlist name
        :return: set of plists, including input plb
        """
        self.set_pat2plb()

        assert plb in self._plb2n, f'patlist={plb} is not loaded'
        return {self._n2plb[n] for n in self._plbchild[self._plb2n[plb]]}

    def get_parentplists(self, plb):
        """
        Return list of parentplists given plb

        :param plb: patlist name
        :return: set
        """
        self.set_pat2plb()

        parent_plists = set()

        assert plb in self._plb2n, f'patlist={plb} is not loaded'
        inputn = self._plb2n[plb]
        for ntarget in self._plbchild:
            if inputn in self._plbchild[ntarget]:
                parent_plists.add(self._n2plb[ntarget])
        return parent_plists

    def _get_all_patlist(self, modlist=None):
        """
        :return: list of all patlist
        :rtype: set
        """
        mtpl = self.tpobj.mtpl
        patlist = set()
        for mod, tn, dd, _ in mtpl.iter_tests(key_name='patlist', edict=True):
            if modlist and mod not in modlist:
                continue
            patlist.add(remove_ip(dd['patlist']))
        return patlist

    def get_cipmodules(self, modlist):
        """
        Return set of cip_modules used in modlist

        Note: A module can use 2 cip_modules. e.g. Modules/PARR_MBISTKS_CLASS in TGLXXXXBXH13Z00S018
              This will cause module *dependency* when there is a change in .plist

        :param modlist: list of module names
        :return: set of cip_modules
        """
        # Performance: ~3sec given all modules for a full TP
        self.set_plb_map()

        cip_module = set()
        patlist = self._get_all_patlist(modlist)
        if not patlist:
            return cip_module     # empty

        for plb in patlist:

            if plb not in self._plb_map:
                log.info('WARNING: %s is not found in any of the .plists' % plb)
                # print all the plist files
                # for plist in self._plist_list:
                #     log.info('-i- plist used: %s' % plist)
                # raise ErrorInput('[%s] is not found in any of the .plists above.' % plb,
                #                  'Where is %s defined?' % plb)
                continue

            # get the module name
            ff = self._plb_map[plb]
            modname = self.get_modname(ff)
            if modname:
                cip_module.add(modname)

        return cip_module

    @staticmethod
    def get_modname(path, _mod_re=re.compile(r'/(\w+)/Rev[\w\.]+/p\d+')):
        """
        Get the ci module name from fullpath (plist)

        :param path: fullpath or directory path
        :param _mod_re: compiled regex to get modulename
        :return: ci module name
        """
        path = path.replace('\\', '/').replace('//', '/')
        res = _mod_re.search(path)
        if '/Supersedes/' in path:
            log.info("-w- Ignoring %s" % path)
            return None
        if not res:
            raise ErrorInput("Cannot find module name for path %r" % path,
                             "Is this a valid .plist path?")
        return res.group(1)

    def get_modname2(self, path):
        """
        Get the ci module from plist
        This is the version of get_modname() without the need of ci_module in the path.
        Example: all plists are in supercede.

        :param path: plist or path to plist
        :return: ci module name
        """
        m2ci = reverse_set(self.get_cimod2mod_map())
        p2m = reverse_set(self.get_mod2plist_map())
        f2m = reverse_keyval(self.tpobj.mtpl.get_modfolder2mod())
        plist = basename(path)
        for modf in p2m.get(plist, {"_none_"}):
            mod = f2m.get(modf, '_none')
            if mod in m2ci:
                return m2ci[mod].pop()
        return "none"

    def get_cimod2mod_map(self):
        """
        Return {ci_plist_module: set_of_module_folder_name} map by reading mconfig

        :return: dict: {ci_plist_module: set_of_module} map
        """
        result = defaultdict(set)
        robj = re.compile(r'PORRoot.*hdm.pats[^\w]\w+[^\w](\w+)')
        for mtpl in self.tpobj.get_all_mtpl_from_stpl():
            if 'Modules' not in mtpl:
                continue
            mod = basename(dirname(mtpl))
            mwild = glob.glob(f'{dirname(mtpl)}/*.mconfig')
            if mwild:    # not all modules has this file
                confirm(len(mwild) == 1,
                        f'Expecting one *.mconfig in {dirname(mtpl)}. Found: {len(mwild)}',
                        'Pls fix to have one .mconfig file only')
                mconfig = mwild[0]
                with open(mconfig, 'r') as fh:
                    for cimod in robj.findall(fh.read()):
                        result[cimod].add(mod)

        if not len(result):
            log.info('-w- No valid cimodule found in Modules/*/module.mconfig. If this is fulltp, then something is very wrong!')

        return result

    def get_mod2plist_map(self):
        """
        Return {module: set_of_plist_file} map by reading mconfig. module here is TestPlan name

        :return: dict: {module: set_of_plist_file} map
        """
        # get all plist files first
        allplist = {basename(x).lower() for x in self.get_plb_map().values()}
        m2m = self.tpobj.mtpl.get_modfolder2mod()

        result = defaultdict(set)
        robj = re.compile(r'([\w\-\.]+\.plist)')
        for mtpl in self.tpobj.get_all_mtpl_from_stpl():
            if 'Modules' not in mtpl:
                continue
            mod = m2m[basename(dirname(mtpl))]
            for mconfig in glob.glob(f'{dirname(mtpl)}/*.mconfig'):
                with open(mconfig, 'r') as fh:
                    for plistfile in robj.findall(fh.read()):
                        if plistfile.lower() in allplist:
                            result[mod].add(plistfile)

        if not len(result):
            log.info('-w- No valid .plist found in Modules/*/module.mconfig. Are there modules.mconfig in Modules/* folder?')

        return result

    def plb_to_filename(self, patlist, fullpath=False):
        """
        Given patlists, return list of filenames

        :param patlist: list of plb
        :param fullpath: Set to True to return fullpath instead of just filename
        :return: set of filenames
        """
        self.set_plb_map()      # self._plb_map = {plb_name: full_path_to_plist_file}

        result = set()
        is_error = False
        for plb in patlist:
            plb = remove_ip(plb)
            if plb in self._plb_map:
                if fullpath:
                    result.add(self._plb_map[plb])
                else:
                    result.add(basename(self._plb_map[plb]))
            else:
                log.info("-ERROR- %s does not exist in any .plist file in %s" % (plb, basename(self.envfile)))
                is_error = True

        if is_error and self.error_out:
            raise ErrorInput("See above ERRORs. At least one plb is not found in %s" % self.envfile,
                             "Check the .env file")
        return result

    def get_modname_map(self):
        """
        Return dict of {plb: (module, ti_name)}, first occurrence in pass flow.

        :return: dict
        """
        self.set_plb_map()
        self.set_pat2plb()
        result = {}
        for which in (True, False):   # So pass flow first, then fail flow
            kwargs = dict(passonly=which, bypass=True, keyparam='patlist', edict=True)
            for md, tn, data in self.tpobj.mtpl.iter_flows('MAIN', **kwargs):
                plb = remove_ip(data['patlist'])
                assert plb in self._plb_map, f'Error: {plb} at {md}, {tn} not found in any .plist'

                for n in self._plbchild[self._plb2n[plb]]:
                    tplb = self._n2plb[n]
                    if tplb not in result:
                        result[tplb] = (md, tn)

        return result

    @staticmethod
    def get_tid_from_pats(pat_set: set, istestname=False) -> set:
        """
        Return set of main pattern tids or testnames from pats

        :param pat_set: set of patterns
        :param istestname: Set to True to return testname instead
        :return: set of TID (or testname)
        """
        # testname
        if istestname:
            result = {testname_from_pat(x) for x in pat_set}
            result.discard('')
            return result

        # tid
        result = {tid_from_pat(x) for x in pat_set}

        # remove amble tids
        result.discard('9999992_00')
        result.discard('9999991_00')
        result.discard('9999993_00')
        return result

    def get_all_plists(self):
        """
        Return list of all plists - fullpath
        :return: list_plist_fullpath
        """
        mainfile = self.tpobj.read_tpconfig('TestProgramFiles.PlistPath')
        if not mainfile:
            mainfile = 'PLIST_ALL.xml'      # TODO: change this logic so it uses tpobj.get_file_allplist()
        fp_mainfile = f'{self.tpobj.envdir}/{mainfile}'
        confirm(exists(fp_mainfile), f'Not found: {fp_mainfile}', 'Expecting this file.')
        allplists = [fp_mainfile]
        for plist in re.findall(r'IPReference\s.*path="([^\"]+)', File(fp_mainfile).read()):
            target = '%s/%s' % (self.tpobj.envdir, plist.replace('\\', '/'))
            confirm(exists(target), f'Not found: {target}', 'Expecting this file.')
            allplists.append(target)

        return allplists

    def get_flat(self, plb, stopat=re.compile('^resetplb_')):
        """
        Return the flattened structure of plb. Main entry point
        :param plb: plb string
        :param stopat: regex object: don't traverse further if this plb matches
        :return: list of resets
        """
        result = []
        self._get_flat(plb, result, stopat, 0)

        # preburst: skip that is same and collapsible
        final = []
        prevtype1 = None
        for reset, ttype in result:
            if ttype == 1:
                if reset == prevtype1:
                    continue
                prevtype1 = reset
            if ttype == 11:
                prevtype1 = None
            final.append((reset, ttype))

        # postburst: skip that is same and collapsible
        final2 = []
        prevtype2 = None
        for reset, ttype in reversed(final):

            if ttype == 2:
                if reset == prevtype2:
                    continue
                prevtype2 = reset

            final2.append(reset)

        return list(reversed(final2))

    def _get_flat(self, plb, result, stopat=re.compile('^resetplb_'), ttype=None):   # model recursive template
        """
        Return the flattened structure of plb. Recursive function.

        :param plb: plb string
        :param result: accumulated resulting list.
        :param stopat: regex object: don't traverse further if this plb matches
        :param ttype: 0 for normal pattern, non-collapsible
                      1 preburst
                      11 preburst startover (aka, burstoff)
                      2 postburst
                      22 postburst startover (aka, burstoff) -> not really used due to reverse() logic in get_flat()
        :return: result
        """
        assert ttype is not None

        # Special case for templates that use patlist but it's not a real patlist
        if '*' in plb:
            result.append((f'IGNORED:{plb}', ttype))
            return result

        # Do some checks
        confirm(self._plb2any, 'TP object is not initialized with allpats=True', 'Pls run init() using TestProgram(allpats=True)')
        confirm(self.tpobj.allpats,
                'Can only use get_flat() when allpats=True on TP object',
                'Update TestProgram object call to include allpats=True')
        confirm(plb in self._plb2n, f'{plb} is not found', 'Check if this globalplist actually exist')

        if stopat.search(plb):
            result.append((plb, ttype))
            return result  # done

        n = self._plb2n[plb]
        attr = self._plbattr[n]
        is_burstoff = bool('BurstOff' in attr or 'BurstOffDeep' in attr)

        if 'PreBurstPList' in attr and not is_burstoff:       # burstoff is inside the loop, so don't duplicate
            self._get_flat(attr['PreBurstPList'], result, stopat, 1)
        if 'PreBurst' in attr and not is_burstoff:
            result.append((attr['PreBurst'], 1))

        # print(f"Start {plb}")
        for nnplb, is_pat in self._plb2any[n]:   # nnplb: nn for pat, plbname for plb
            # print('     ', nnplb, is_pat)

            # Do the plb attributes first
            if 'PreBurstPList' in attr and is_burstoff:
                self._get_flat(attr['PreBurstPList'], result, stopat, 11)

            if 'PreBurst' in attr and is_burstoff:
                result.append((attr['PreBurst'], 11))

            if 'PrePList' in attr:
                self._get_flat(attr['PrePList'], result, stopat, 0)

            if 'PrePattern' in attr:
                result.append((attr['PrePattern'], 0))

            if is_pat:
                result.append((self._nn2pat[nnplb], ttype))
            else:
                self._get_flat(nnplb, result, stopat, 0)

            if 'PostPList' in attr:
                self._get_flat(attr['PostPList'], result, stopat, 0)

            if 'PostPattern' in attr:
                result.append((attr['PostPattern'], 0))

            if 'PostBurstPList' in attr and is_burstoff:
                self._get_flat(attr['PostBurstPList'], result, stopat, 22)
            if 'PostBurst' in attr and is_burstoff:
                result.append((attr['PostBurst'], 22))

        # post
        if 'PostBurstPList' in attr and not is_burstoff:
            self._get_flat(attr['PostBurstPList'], result, stopat, 2)
        if 'PostBurst' in attr and not is_burstoff:
            result.append((attr['PostBurst'], 2))

        return result

    def get_refplist(self):
        """
        Get plb to plb dependency
        Return: {plb: list_plb_dependent}
        """
        return {self._n2plb[x]: self._refplist[x] for x in self._refplist}

    def get_plist_dependent(self):
        """
        Get plist to plist dependency
        :return: {plist: set(plist)}
        """
        # initialize
        self.set_pat2plb()
        # {plb: list_dependent}
        refplist = {self._n2plb[x]: self._refplist[x] for x in self._refplist}
        # {plb: fullpath_plist}
        plbmap = self.get_plb_map()
        # {plb: plist}
        plb2plist = {x: basename(y) for x, y in plbmap.items()}

        # translate refplist to plists
        result = defaultdict(set)
        for plb in refplist:
            for item in refplist[plb]:
                if plb2plist[item] != plb2plist[plb]:
                    result[plb2plist[plb]].add(plb2plist[item])

        # add the rest of the plists without any dependency
        final = dict(result)
        for item in plb2plist.values():
            plistonly = basename(item)
            if plistonly not in final:
                final[plistonly] = set()    # No dependency

        return final

    def get_pat_details(self):
        """
        Return patopts dict and pattags dict

        :return:
            patopts: {plb: {pat: [option1, option2, etc]}}
            pattags: {plb: {pat: [tag1, tag2, etc]}}
        :rtype tuple
        """
        self.read_pat_details()
        return self._patopts, self._pattags

    def read_pat_details(self):
        """
        Read all plist files, finds the patts showing an 'execution modification' and stores that info
        execution modification: those cases where the patt shows a [BurstOff] or [Mask] or a CTTR tag such as #KEEP#
        Populates: _patopt, _pattag
        """
        if self._patopts or self._pattags:        # Already populated, no need to reparse
            return

        sw = Elapsed()

        # Datastructure
        patopts = {}   # {plb: {pat: [option1, option2, etc.].  Only populated for patts w/level options
        pattags = {}   # {plb: {pat: [tag1, tag2, etc.].  Only populated for patts w/cttr tags

        # REGEXES def
        if not self.tpobj.is_tos4:
            # TOS3 ================================================
            r_pat = re.compile(r'\bPat\s+(\w+)')
            r_plb = re.compile(r'^GlobalPList\s*(\w+)\b')
        else:
            # TOS4 ===============================================
            r_pat = re.compile(r'^Pat\s+(\w+)')
            r_plb = re.compile(r'^PList\s*(\w+)\b')

        r_patoption = re.compile(r'\[(.+)\]')
        r_patoption_cleanup = re.compile(r"\s*;.*")
        r_pattag = re.compile(r'.*?;.*?#(.*?)#')

        stack, plbchild = [], defaultdict(set)        # Global plist main/child tracking
        for ff in self.get_plist_list():
            for lno, line in OtplFile(ff).with_eol_comment():
                # globalplist line
                plbline = r_plb.search(line)
                if plbline:
                    plb = plbline.group(1)
                    for splb in stack:
                        plbchild[splb].add(plb)
                    stack.append(plb)
                    continue
                if line == '}':     # Close globalplist
                    stack.pop()
                    continue

                # main pattern line
                patline = r_pat.search(line)
                if patline:
                    pat = patline.group(1)

                    # Pat options
                    option_flag, poptions = self._get_pat_options(line, r_patoption, r_patoption_cleanup)
                    if option_flag:
                        for actplbs in stack:       # Populate the datastructure for ALL active plists
                            if actplbs not in patopts:
                                patopts[actplbs] = {pat: poptions}
                            else:
                                if pat not in patopts[actplbs]:
                                    patopts[actplbs][pat] = poptions
                                else:
                                    patopts[actplbs][pat] = list(set(patopts[actplbs][pat] + poptions))

                    # CTTR tags
                    tag_flag, ptags = self._get_pat_tags(line, r_pattag)
                    if tag_flag:
                        for actplbs in stack:       # Populate the datastructure for ALL active plists
                            if actplbs not in pattags:
                                pattags[actplbs] = {pat: ptags}
                            else:
                                if pat not in pattags[actplbs]:
                                    pattags[actplbs][pat] = ptags
                                else:
                                    pattags[actplbs][pat] = list(set(pattags[actplbs][pat] + ptags))

        # Sort the options and values
        for plb in patopts:
            for pat in patopts[plb]:
                patopts[plb][pat] = sorted(patopts[plb][pat])
        for plb in pattags:
            for pat in pattags[plb]:
                pattags[plb][pat] = sorted(pattags[plb][pat])

        # assign
        self._patopts = patopts
        self._pattags = pattags
        log.info("-i- Finished reading patt level options and CTTR tags in %s" % sw)

    @classmethod
    def _get_pat_tags(cls, rawpatstr, r_pattag):
        """
        Given a raw pattern string it extracts the CTTR tags
        :param rawpatstr: str
        :param r_pattag: compiled regex to extract patt tags
        :return: tuple
            tag_flag: bool if a tag is present or not
            ptags: list of strs
        """
        tag_flag = False
        ptags = []

        if '#' in rawpatstr:    # Quick and dirt check if there is any CTTR taag
            t_pattag = r_pattag.search(rawpatstr)
            if t_pattag:
                ptags = t_pattag.group(1).upper()
                ptags = re.split(r",", ptags)  # Ex: ["KEEP", "HOT"] upper case
                ptags = [x.strip() for x in ptags]
                tag_flag = True

        return tag_flag, ptags

    @classmethod
    def _get_pat_options(cls, rawpatstr, r_patoption, r_patoption_cleanup):
        """
        Given a raw pattern string it extracts the pattern level options
        :param rawpatstr: str
        :param r_patoption: compiled regex to extract patt options
        :param r_patoption_cleanup: compiled regex to clean up the patt str
        :return: tuple
            option_flag: bool if an option is present or not
            poptions: list of strs
        """
        option_flag = False
        poptions = []
        if '[' in rawpatstr:  # Quick and dirt check if there is any PATT LEVEL OPTIONS
            pat = r_patoption_cleanup.sub("", rawpatstr)  # Removes anything outside patt str that can cause false positive
            t_patopt = r_patoption.search(pat)
            if t_patopt:
                poptions = t_patopt.group(1)
                poptions = re.split(r"\]", poptions)  # Ex: ["BurstOff", "Unmask TDO"]

                # Clean up each option
                poptions = [x.strip() for x in poptions]    # remove spaces
                poptions = [x.strip("[") for x in poptions]
                poptions = [x.strip("]") for x in poptions]
                poptions = [x.strip() for x in poptions]    # remove spaces

                option_flag = True
        return option_flag, poptions


import tp.testprogram    # used for :type
