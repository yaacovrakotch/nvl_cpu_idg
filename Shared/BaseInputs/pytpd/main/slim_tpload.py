#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Make slim plists

Usage:
slim_tpload.py <envfile> -out <outdir>
"""
import setenv      # must be first in the imports
from gadget.disk import Allfiles
from gadget.dictmore import DictDot, xmlfunc, find_dot_items
from gadget.vepargs import Args, TA_StoreDir, TA_All
from gadget.strmore import regex, group
from gadget.files import File
from gadget.helperclass import OPT
from gadget.printmore import Dumper
from gadget.errors import ErrorInput, confirm
from gadget.gizmo import Elapsed
from gadget.pylog import log
from gadget.tputil import noquote
from collections import defaultdict
from tp.testprogram import TestProgram
from os.path import join, basename, isdir, exists, dirname
from pprint import pprint
import os
import re
import json


class Slim(object):

    def __init__(self, envfile, noinit=False):
        self.envfile = envfile
        self.keep_pats = set()    # set of pattern names, populated in set_keep_pats()
        self.warns = set()        # set of warning messages, for unittest purpose
        if noinit:
            self.tpobj = TestProgram(envfile)
        else:
            self.tpobj = TestProgram(envfile).pickle_init()
        self.plists = self.tpobj.plists

    def main(self, outdir):
        """
        Rewrite all .plist to make them slim

        :param outdir: output dir
        :return: None
        """
        sw = Elapsed()
        # Get all keep pats
        self.set_keep_pats()

        # Convert all partial names to full names (since regex is slow)
        self._full_names(set(self.plists.get_pats_all()))
        log.info("-i- Writing plists to %s" % OPT.out)

        # get all .plist for load based on ALLPLIST.xml
        for plist in self.plists.get_plist_list():
            self._make_slim_plist(plist, outdir)
        log.info(f"-i- Done in {sw}")

    def set_keep_pats(self):
        """
        Return all patterns needed for TP to load based on patmod.txt
        by reading mtpl and getting at least one pattern regex

        :return: None. Set self.keep_pats
        """
        slim = set()
        self.keep_pats_patmodtxt(slim)
        self.keep_pats_ifpm(slim)
        self.keep_pats_ipo(slim)
        self.keep_pats_reset(slim)
        self.keep_pats_json(slim)   # must be last

        # store it
        self.keep_pats = slim
        log.info("Final slim count: %s" % len(slim))

    def keep_pats_reset(self,
                        slim_names,
                        cfg_mod=re.compile('^(DRV)'),            # regex of modules to keep
                        cfg_plb=re.compile('^(resetplb)'),       # regex of plb to keep
                        ):
        """
        Get all reset of all drv modules (and other modules that require no-slim)
        :param slim_names: set of slim names to keep
        :param cfg_mod: regex modules to keep
        :param cfg_plb: regex plb to keep
        :return:
        """
        # get mapping
        plb2plist = self.tpobj.plists.get_plb_map()             # {plb: set_of_fullpath_plist}
        mod2plist = self.tpobj.plists.get_mod2plist_map()       # {module: set_of_plist}

        # {plist: set_of_plb}
        plist2plb = defaultdict(set)
        for plb, fpath in plb2plist.items():
            plist2plb[basename(fpath)].add(plb)

        resets = set()
        for mod in mod2plist:
            if not cfg_mod.search(mod):
                continue
            for plist in mod2plist[mod]:
                for plb in plist2plb[plist]:
                    if cfg_plb.search(plb):
                        resets.update(self.tpobj.plists.get_pats_from_plb(plb))

        log.info(f'Total resets: {len(resets)}')
        slim_names.update(resets)

    def keep_pats_json(self, slim_names):
        """Read json files, get PatternsRegEx"""
        orig_count = len(slim_names)

        # Get all json files
        jsonfiles = set()
        for item in self.tpobj.env.get_env_dict():
            if item.startswith('ALEPH_FILES'):
                for ff in self.tpobj.env.get_plist_paths(item):
                    if ff.startswith('/'):
                        fpath = ff
                    else:
                        fpath = f'{self.tpobj.tpldir}/{ff}'
                    if exists(fpath):
                        jsonfiles.add(fpath)

        all_pats = set(self.plists.get_pats_all())
        all_pats_str = '\n'.join(sorted(all_pats))

        # get regex on json files
        for ff in sorted(jsonfiles):
            set_regex = set()
            if not ff.endswith('.json'):
                continue
            with open(ff) as fh:
                try:
                    res = json.load(fh)
                except json.decoder.JSONDecodeError as e:
                    res = {}
                    print(f"Error json load on {ff}: {e}")

            for item in find_dot_items(res, 'PatternsRegEx', default=[]):
                set_regex.add(item.split(':')[0])

            PatMod.regex_find(set_regex, ff, slim_names, all_pats, all_pats_str, is_ifpm=False)

        log.info(f'-i- slim count json: {len(slim_names) - orig_count}')

    def keep_pats_ipo(self, slim_names):
        """Read iCIPOTest, get all configs, then read all plb's, make all these slim"""

        # Get all iCIPOTest config files
        filexml = set()
        for mod, tn, test_instance, _ in sorted(self.tpobj.mtpl.iter_tests('iCIPOTest', edict=True)):
            if not self.tpobj.mtpl.is_bypassed(mod, tn, test_instance):
                filexml.add(test_instance['config_file'])

        # get all plbs from the config
        saveplb = set()
        for ff in sorted(filexml):
            fpath = join(self.tpobj.tpldir, ff)
            for item in re.findall(r'patlist name="(\w+)"', File(fpath).read()):
                saveplb.add(item)

        # get all patterns of saveplb, put them in slim
        plb_map = self.plists.get_plb_map()
        for plb in sorted(saveplb):
            if plb in plb_map:
                slim_names.update(self.plists.get_pats_from_plb(plb))

        log.info("slim count ipo (cum): %s" % len(slim_names))

    def keep_pats_ifpm(self, slim_names):
        """
        Return all patterns needed for TP to load based on ifpm patmod, via:
        1. read all mtpl, get ifpm xml's files
        2. read all regex blocks from the xml
        3. get at least one pattern for each regex

        :param slim_names: set of slim names
        :return: set of keep pats
        """
        # TODO: This needs to be refactored, since TP with multiple env will not work here
        uniq = set()
        for mod, tin, data, tpobj in sorted(self.tpobj.mtpl.iter_tests(edict=True), key=lambda x: (x[0], x[1])):
            if 'ifpm_input_file' in data:
                # TODO: remove the dd=data below, is_bypassed should be using edata!
                if not tpobj.mtpl.is_bypassed(mod, tin, dd=data):    # Do not include testinstance with bypass_global
                    uniq.add(data['ifpm_input_file'])

        # get all names
        all_pats = set(self.plists.get_pats_all())

        # get the regex
        patmod = PatMod()
        all_pats_str = '\n'.join(sorted(all_pats))
        # uniq = ['/intel/hdmxpats/tgl/MfunSa/RevTTR1.0/p1/cfg/merged_Mfunsa_class.xml']

        for path in sorted(uniq):
            if path.strip():
                ff = tpobj.env.convert_fullpath(path)
                patmod.read_ifpm(ff, all_pats_str, all_pats, slim_names)

        log.info("slim count ifpm (cum): %s" % len(slim_names))

    def keep_pats_patmodtxt(self, slim_names):
        """
        Return all patterns needed for TP to load based on patmod.txt, via:
        1. read all mtpl, get patmod.txt file and it's token
        2. read all patmod.txt
        3. get at least one pattern for each token regex

        :param slim_names: set of slim names
        :return: set of keep pats
        """
        ds = {}    # resulting ds (data structure): {module::instancename: (inputfile, token)}

        tpobj_mod = set()   # unique tpobj, mod combination
        for mod, tn, dd, tpobj in self.tpobj.mtpl.iter_tests(edict=True):
            tpobj_mod.add((tpobj, mod))
        for tpobj, mod in tpobj_mod:
            ds.update(self.patmod_mtpl(tpobj, mod))

        ds.update(self.glxpress_patmod(ds))

        # get all uniq patmod files
        patmod_f = {}     # {patmodfile: module::testname}
        for ins in ds:
            patmod_f[ds[ins][0]] = ins

        # get all names
        all_pats = set(self.plists.get_pats_all())

        patmod = PatMod()
        for ff in sorted(patmod_f):
            log.info(f"Processing: {ff}")
            mod, tn = patmod_f[ff].split('::')
            is_bypass = self.tpobj.mtpl.is_bypassed(mod, tn)
            patmod.read_for_slim(ff, ds, all_pats, slim_names, is_bypass)

        log.info(f"ds (#ftest):  {len(ds)}")
        log.info(f"patmod_files: {len(patmod_f)}")
        log.info(f"all_pats:     {len(all_pats)}")
        log.info(f"slim_names:   {len(slim_names)}")

    @staticmethod
    def patmod_mtpl(tpobj, mod):
        """
        Read specific mtpl and return unique iCPatternModifyTest

        :param tpobj: tpobj
        :param mod: which module
        """
        result = {}
        for tmod, tn, dd, _ in sorted(tpobj.mtpl.iter_tests('iCPatternModifyTest', edict=True), key=lambda x: x[1]):
            if tmod != mod:
                continue

            if 'input_file' in dd:
                input_file = tpobj.env.convert_fullpath(dd['input_file'])
            else:
                continue   # do nothing

            # TODO: remove the dd=dd below, is_bypassed should be using edata!
            if tpobj.mtpl.is_bypassed(tmod, tn, dd=dd):
                modify_token = 'INIT'
            else:
                modify_token = dd['modify_token']
            result['%s::%s' % (mod, tn)] = (input_file, modify_token)

        return result

    def glxpress_patmod(self, in_ds):
        """
        Read all glxpress files

        get all patmodfiles from glxpress
        :param in_ds: Input data_structure: {tname: (input_file, token)}
        :return: data_structure: {tname: (input_file, token)}
        """
        # TODO: This needs to be refactored since it will only work with one env file
        # get all gl_xpress_file_path files
        glx = {}   # {"mod::testinstancename": input_file}
        for mod, tin, ins, tpobj in sorted(self.tpobj.mtpl.iter_tests('iCGlXpressTest', edict=True)):
            glx['%s::%s' % (mod, tin)] = ins['gl_xpress_file_path']

        # get all patmodfiles from each file
        # print("-i- glx data structure:")
        # Dumper(glx)
        data = {}
        for mod_tin in sorted(glx):
            glxfile = join(dirname(self.envfile), glx[mod_tin])
            if not exists(glxfile):
                log.info("WARNING: %s not found" % glxfile)
                continue
            for line in File(glxfile).chomp():
                if line.strip().startswith('input_file'):
                    patmod_file, tname = self.glxline(line)
                    patmod_file = tpobj.fullpath_tp(patmod_file)

                    result = self.key_startswith(tname, in_ds)
                    if not result:
                        raise Exception("[%s] does not match any testinstancename, from %s" % (tname, glx[mod_tin]))
                    for found_tname in sorted(result):
                        data[tname] = (patmod_file, in_ds[found_tname][1])

        # print("-i- glx 'input_file' output structure:")
        # Dumper(data)
        return data

    def glxline(self, line):
        """
        Parse one glxexpress line
        :param line: glxexpress line
        :return: patmod_file, mod_tname
        """
        elem = line.split(',')

        # parse first element
        if regex(r"\w+[\s=]+(\S.*)", elem[0].strip()):
            value = noquote(group(1))
        else:
            value = None

        # parse third element - mod+testname
        if regex(r"(\S+)", elem[2].strip()):
            mod_tname = group(1)
        else:
            mod_tname = None
        return value, mod_tname

    @staticmethod
    def key_startswith(keyval, dd):
        """
        Iterator, return all keys of dd given keyval

        :param keyval: string, may end with '*', which means startswith
        :param dd: some dictionary
        :return: matching keys
        """
        if keyval.endswith('*'):
            keyval = keyval[:-1]
            for item in dd:
                if item.startswith(keyval):
                    yield item
        else:
            # exact match
            if keyval in dd:
                yield keyval

    def set_keep_pats2(self):    # pragma: no cover
        """
        OLD/previous routine!
        Return all patterns needed for TP to load
        by reading all cfg files and return all pattern looking names

        :return: None. Set self.keep_pats
        """
        pats_to_keep = set()
        for cfgfile in self._id_cfg_files():
            pats_to_keep.update(self._read_file(cfgfile))
        log.info("Total keep_pats: %s" % len(pats_to_keep))
        self.keep_pats = pats_to_keep

    def _expt_pats_from_tpl(self):      # pragma: no cover
        """
        Read all files underneath TPL/, and get all pattern names

        :return: set of pats
        """
        pats = set()
        for ff in Allfiles(dirname(self.envfile), fullpath=True):
            found = self._read_file(ff)
            pats.update(found)
            if found:
                log.info("%s %s %s" % (len(pats), len(found), ff))

    def _expt_pats_from_rev_cfg(self):    # pragma: no cover
        """
        Read all files defined in env file /intel/hdmxpats/*/cfg/ directory and get all pattern names

        :return: set of pats
        """
        pats = set()
        cip_paths = TP().get_cip_paths(self.envfile)
        for cip in cip_paths:
            for ff in os.listdir(join(cip, 'cfg')):
                if 'hry.txt' in ff:
                    continue     # skip this for now
                found = self._read_file(join(cip, 'cfg', ff))
                pats.update(found)
                log.info("%s %s %s" % (len(pats), len(found), join(cip, 'cfg', ff)))

    def _read_file(self, fname, _robj=re.compile(r'\b([dg]\d{7}\w\d{7}\w+)')):
        """
        Read any file, determine main pattern

        :param fname: any kind of file
        :return: set of patterns
        """
        if isdir(fname):
            return set()

        return set(_robj.findall(open(fname).read()))

    def _full_names(self, all_pats):
        """
        Update self.keep_pats to full names
        :param all_pats: set of patnames
        """
        # first pass: make sure all exist
        keep = set()
        all_pats_str = '\n'.join(sorted(all_pats))
        sw = Elapsed()
        ctr = 0
        for pat in sorted(self.keep_pats):
            if pat in all_pats:
                keep.add(pat)
            else:
                res = re.search('^(.*%s.*)$' % pat, all_pats_str, re.MULTILINE)
                confirm(res, f'{pat} is not found in any of the pats', 'Why?')
                keep.add(res.group(1))
                ctr += 1

        self.keep_pats = keep
        log.info(f'full_names: {ctr} partial names is added in {sw}')
        return ctr     # unittest use

    def _make_slim_plist(self, fname, outdir):
        """
        Make this plist slim and rewrite in outdir

        :param fname: path to .plist file
        :param outdir: outfile
        :return:
        """
        ro_pats = re.compile(r"^\s*Pat\s+([dg]\d{7}\w+)")    # 1000 calls is 0.002 Secs
        # ro_plb = re.compile('^\s*GlobalPList')
        target = join(outdir, basename(fname))
        keep = set(self.keep_pats)    # make a copy

        # first pass: add at least one pattern for each block in keep pats
        first = None
        for line in File(fname).chomp():
            res_pats = ro_pats.search(line)
            if res_pats:

                if first is None:
                    first = res_pats.group(1)
                elif res_pats.group(1) in keep:
                    first = False
                else:
                    None        # for coverage
                    continue    # skip

            if line.strip().startswith('}'):
                if first:
                    keep.add(first)
                first = None

        # print "Writing %s" % target
        with open(target, 'w') as fho:
            for line in File(fname).chomp():
                res_pats = ro_pats.search(line)
                if res_pats:
                    if res_pats.group(1) not in keep:
                        continue    # skip this line. No keep

                fho.write("%s\n" % line)

    def _id_cfg_files(self):    # pragma: no cover  - unused
        """
        Identify all cfg files used from pattern area

        :return: set of config files used by all mtpls - fullpath
        """
        result = set()
        mdir = join(dirname(self.envfile), 'Modules')
        for mod in os.listdir(mdir):
            for ff in os.listdir(join(mdir, mod)):
                if not ff.endswith('.mtpl'):
                    continue
                result.update(self._get_cfgs(join(mdir, mod, ff)))
        return result

    def _get_cfgs(self, fname, _robj=re.compile(r'\b(\w+)\s*=\s*\"(~\w+PATMODIFY_PATH[~/\/\w\.-]+|./Modules/\S+/InputFiles/[^\"\*!]+)')):
        """
        Given mtpl file, Get all:
         1. ~\\w+PATMODIFY_PATH.*
         2. Inputfiles
         Then convert to full path

        :param fname: path to one mtpl file
        :return: set of paths to config files to read
        """
        # get value of env
        obj = self.tpobj.env
        env_dict = obj.get_env_dict()

        tpldir = dirname(self.envfile)
        t_path = set(_robj.findall(open(fname).read()))
        final = set()
        warns = set()
        for keyword, path in sorted(t_path):
            if keyword in ('function_parameter'):
                continue

            if path.startswith('./Modules'):
                path = join(tpldir, path)   # make it full path

            # replace ~PATMODIFY_PATH with real value
            if regex(r"~(\w+)", path):
                var = group(1)
                if var not in env_dict:
                    warns.add("-i- WARNING: [%s] var is not found in env file." % var)
                    continue
                path = path.replace('~%s' % var, obj.to_unixpath(env_dict[var]))

            if not exists(path):
                warns.add("-i- WARNING: [%s] does not exist" % path)
                continue

            final.add(path)

        if warns:
            log.info('\n'.join(warns))
            self.warns.update(warns)
        return final


class PatMod:

    def read_for_slim(self, ff, ds, all_names, slim_names, is_bypassed):
        """
        Updates slim_names given patmod file

        :param ff: patmod file
        :param ds: data structure {testname: (file, token)}
        :param all_names: set of patnames, full list
        :param slim_names: set of patnames, slim list
        :param is_bypassed: bool: True if this instance is skipped
        :return: None
        """
        sorted_all_names = sorted(all_names)

        # get unique tokens
        u_tokens = set()
        for fname, token in ds.values():
            if fname == ff:
                for indv_token in token.replace(',', ' ').split():
                    u_tokens.add(indv_token)

        # read the file
        patmod = {}    # {token: {set_of_regex}}  #don't use defaultdict here, because of MAIN PLIST
        if exists(ff):
            for line in File(ff).safeopen():
                line = line.strip()
                if not line.startswith('+'):  # from EPS: '+' means enable, '-' means disable.
                    continue
                spl = line.split()
                # if len(spl) < 4:
                #     continue
                if spl[2] == 'MAIN':
                    if spl[1] not in patmod:
                        patmod[spl[1]] = set()   # empty
                    if spl[3] == 'PAT':
                        patmod[spl[1]].add(spl[4])
        else:
            if u_tokens != {'INIT'}:
                raise IOError("File does not exist and use token %r: %r" % (u_tokens, ff))

        # add INIT - special
        if 'INIT' in patmod:
            u_tokens.add('INIT')      # in cases where INIT is not in test_instance
        if 'INIT' not in patmod:
            u_tokens.discard('INIT')   # in cases where INIT is added due to bypass

        # Use min tokens if instance is bypassed, else, use all the tokens
        if is_bypassed:
            targtoken = u_tokens
        else:
            targtoken = patmod      # read all tokens

        for token in sorted(targtoken):    # jqdelosr debug
            # for token in patmod:
            assert token in patmod, "[%s] token not found in %s" % (token, ff)
            for regex_str in sorted(patmod[token]):
                self._proc_one_token(token, regex_str, sorted_all_names, slim_names, ff)

    def _proc_one_token(self, token, regex_str, all_names, slim_names, ff):
        """
        Updates slim_names given the regex

        :param token: token name
        :param regex_str: patmod regex
        :param all_names: all names to search from (sorted list)
        :param slim_names: slim names
        :param ff: patmod filename
        :return: None
        """
        # print "Processing: token %r, %r" % (token, regex_str)
        if '!' in regex_str:
            regex_str = regex_str.split('!')[1]
        regex_str = regex_str.split(':')[0]
        anchor = r'\b'
        regex_str1 = anchor + regex_str.replace('*', '.*') + anchor
        try:
            robj = re.compile(regex_str1)
        except Exception as e:
            log.info('-w- invalid regex: %r' % regex_str1)
            return

        result = robj.findall('\n'.join(slim_names))
        if result:
            return    # already exist
        for pat in all_names:
            if robj.search(pat):
                # print(f"JDR: {pat} {regex_str1}")
                slim_names.add(pat)
                return

        # not found
        assert False, ('Error: No pattern found for regex[%s] for token[%s], file[%s]'
                       '' % (regex_str, token, ff))

    def read_ifpm(self, ff, all_names_str, all_names, slim_names):
        """
        Read the ifpm patmod xml and generate slim_names

        :param ff: ifpm patmod
        :param all_names_str: all names to search from
        :param all_names: all names to search from (set)
        :param slim_names: slim names (set)
        :return: None
        """
        xml = xmlfunc.xml2dict(ff)
        regex_element = xml['ifpm_setup']['regex_list']['regex']

        # regex_element can be list or scalar
        if isinstance(regex_element, list):
            regex_list1 = regex_element
        else:
            regex_list1 = [regex_element]

        # elements can be scalar or list
        regex_list2 = []
        for item in regex_list1:
            if isinstance(item['value'], list):
                regex_list2 += item['value']
            else:
                regex_list2.append(item['value'])

        self.regex_find(regex_list2, ff, slim_names, all_names, all_names_str)

    @staticmethod
    def regex_find(regex_list2, ff, slim_names, all_names, all_names_str, is_ifpm=True):
        """

        :param regex_list2: list of regex from ifpm or json
        :param ff: filename
        :param slim_names: set slim_names
        :param all_names: set all_names
        :param all_names_str: all_names to search from
        :param is_ifpm: Set to True fo ifpm, False for json
        """
        if not regex_list2:
            return    # Nothing to do

        # separate between regex
        r_com = re.compile('^..._com')
        r_plain = re.compile(r"^\w+$")
        regex_list = []
        plain_list = []
        for item in sorted(set(regex_list2)):

            # temporary skip commonfiles. If this cause missing pattern in load+init, then add logic to add slim_name based on cfx bit of commonfile
            if r_com.search(item):
                continue

            if r_plain.search(item):
                plain_list.append(item)
            else:
                regex_list.append(item)

        log.info("regex cnt: %s, slim cnt: %s,  Processing %s" % (len(regex_list2), len(slim_names), ff))    # debug only

        # iterate to all plain strings
        for item in plain_list:
            if item in slim_names:
                continue   # already exist in slim
            if item in all_names:
                slim_names.add(item)
            else:
                log.info("-w- regex (plain) [%s] has no match, found in %s" % (item, ff))

        # iterate to all regex strings
        anchor = r'\b'
        all_slim = '\n'.join(slim_names)

        for idx, item in enumerate(regex_list):
            if is_ifpm:
                re_str = '^(%s)$' % item
                re_str = re_str.replace('*', '.*')
            else:
                if item.startswith('.*'):
                    re_str = '(%s)$' % item[2:]
                elif item.startswith('^.*'):
                    re_str = '(%s)$' % item[3:]
                else:
                    re_str = '^(%s)$' % item

            # if re.findall(re_str, all_slim, re.MULTILINE):
            if re.search(re_str, all_slim, re.MULTILINE):
                continue    # already exist in slim
            # for found in re.findall(re_str, all_names_str, re.MULTILINE):
            res = re.search(re_str, all_names_str, re.MULTILINE)
            if res:
                slim_names.add(res.group(1))

                # if isinstance(found, str):
                #     slim_names.add(found)
                # else:
                #     slim_names.add(found[0])
                all_slim = '\n'.join(slim_names)
                # break     # first one found
            else:
                log.info("-w- Regex [%s] has no match, defined in %s" % (item, ff))


class SlimArgs(Args):
    """
    slim plist generator
    """

    def config(self):
        """
        Define the arguments for the script.
        The order below will matter, it is the order of display during help.
        """
        cfg = DictDot()
        cfg.all = TA_All('env_file')
        cfg.out = TA_StoreDir('Write the output in this dir', metavar='outdir')
        return cfg

    def main(self):
        """
        Main entry point of executable
        -h will not reach this method, since that is taken cared of in Args Base class
        """
        # list of arg commands (will be translated to do_<argument>()
        self.call_methods(['all',       # this will call do_all(), main routine
                           ])           # do_else() is called if no argument command is processed

    def do_all(self):
        """Main routine"""
        obj = Slim(OPT.all[0])

        if OPT.out:
            obj.main(OPT.out)
        else:   # pragma: no cover  - due to unit testtime
            log.info("-i- NO PLISTS WRITTEN. Add -out <outdir> to write plists.")

        return obj

    def do_else(self):
        """
        Execute this if no valid command is specified
        do_else() in base class will just print the help message
        """
        self.print_help()


if __name__ == '__main__':  # pragma: no cover
    SlimArgs(desc=__doc__).main()
