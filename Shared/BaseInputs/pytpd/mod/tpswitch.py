#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
tpswitch module - generic search and replace object
"""
import re
from gadget.files import File
from gadget.errors import ErrorUser, confirm
from gadget.strmore import sha1
from os.path import exists, isdir, dirname
from importlib.machinery import SourceFileLoader
from gadget.pylog import log
from tp.testprogram import TestProgram
import shutil
import glob
import os
from pprint import pprint


class TPSwitch:
    """Class for tpswitch - Programmable version of ReplJson"""
    tpobj = [None]
    registry = []

    def __init__(self, fname):
        """
        :param fname: path to file, relative to tplroot; can be wildcard. Must result to 1.
        """
        # determine root
        self.root = '.'
        if self.tpobj[0]:
            self.root = self.tpobj[0].tpldir

        if '*' in fname:
            listing = glob.glob(f'{self.root}/{fname}')
            confirm(len(listing) == 1,
                    f'[{fname}] resulted to {listing}',
                    'Expecting one resultant file.')
            self.fname = listing[0]
        else:
            self.fname = f'{self.root}/{fname}'

        # replace {INPUTBOM} - special keyword in fname (bom folder)
        if '{INPUTBOM}' in self.fname:
            confirm(TPSwitch.tpobj[0], 'tpobj is not yet initialized', 'Pls call TPSwitch from nvl_buildtp')
            self.fname = self.fname.replace('{INPUTBOM}', TPSwitch.tpobj[0].get_bomfolder())

        self.is_exist = exists(self.fname)

        # attributes
        self.written = False
        self.lines = []               # list of lines with newline
        self.registry.append(self)    # used for checking if it was written
        self.clsname = self.__class__.__name__

    @classmethod
    def _set_tpobj(cls, tpobj):
        """Set the tpobj"""
        TPSwitch.tpobj[0] = tpobj

    @classmethod
    def _process(cls, infile, root='.'):
        """
        :param infile: string or comma delimited or fullpath (from yml env)
        :return: unittest only
        """
        fflist, ut_type = cls._proc_infile(infile, root)
        for ff in fflist:
            cls._read(ff)

        return ut_type

    @classmethod
    def _proc_infile(cls, infile, root='.'):
        """
        Return list of infiles
        :param infile: input from os.environ('ACPY')
        :param root: root area
        :return: (list, ut_type)
        """
        if not infile:  # empty string
            return [], 1
        if infile == 'None':
            return [], 2
        if infile.startswith('ACPY:'):
            return [], 3

        result = []
        for ff in infile.split(','):
            if exists(ff):       # user specified full path
                result.append(ff)
                continue

            # check extension
            if not ff.endswith('.py'):
                ff = f'{ff}.py'      # add py

            if exists(f'{root}/Shared/TPConfig/TPSwitch/{ff}'):
                result.append(f'{root}/Shared/TPConfig/TPSwitch/{ff}')
            elif exists(f'{root}/TPConfig/TPSwitch/{ff}'):
                result.append(f'{root}/TPConfig/TPSwitch/{ff}')
            else:
                # must ignore missing file because of switch2: it may not exist in dielet
                log.info(f'-w- TPConfig/TPSwitch/{ff} is not found in {os.getcwd()}/{root}. Skipping.')

        return result, 4

    @classmethod
    def _read(cls, fname):
        """
        Check and Read switch file (switch1 or switch2)

        :param fname:
        :return:
        """
        classname = f'{cls.__name__}('
        if classname in File(fname).read():
            cls._import(fname)
            return 1

        log.info(f'-i- {classname[:-1]}: skipping {fname} due to {classname}) not found.')
        return 0

    @classmethod
    def _import(cls, pyfile):     # pragma: no cover
        confirm(exists(pyfile),
                f'Expecting {pyfile}',
                f'Pls confirm this file in your branch')
        log.info(f'-i- {cls.__name__}: loading {pyfile}')
        SourceFileLoader(sha1(pyfile), pyfile).load_module()

    def delete(self):
        """Delete this file or folder"""
        if not self.is_exist:
            log.info(f'-i- delete(): {self.fname} not exist')
            return

        File(self.fname).unlink()

    def copy_dir(self, source):
        """Copy directory"""
        if not exists(source):
            log.info(f'-i- copy_dir(): {source} not exist')
            return

        if isdir(self.fname):
            shutil.rmtree(self.fname)

        if source[:2].isalnum():
            shutil.copytree(f'{self.root}/{source}', self.fname)     # relative path
        else:
            shutil.copytree(source, self.fname)     # full path

    def overwrite_with(self, source):
        """
        Overwrite fname with source
        Used with binary file or any complete file replacement
        """
        if not exists(dirname(self.fname)):
            log.info(f'-i- overwrite_with(): {dirname(self.fname)} not exist')
            return

        self.written = True
        confirm(exists(f'{self.root}/{source}'),
                f'[{self.root}/{source}] does not exist.',
                'Expecting this file to exist')
        File(self.fname).unlink()
        File(f'{self.root}/{source}').copy(self.fname)
        log.info(f'-i- {self.clsname}: overwriting {self.fname}')

    def _init(self):
        """
        Read the file - one time
        :return:
        """
        self.written = False
        if self.lines:
            return    # Do nothing
        self.lines = File(self.fname).raw()

    def search_replace(self, search, replace, marker=None, isregex=False, n=10000):
        """
        Search and replace

        :param search: search string (can be regex)
        :param replace: replacement string or list
        :param isregex: Set to True for regex
        :param marker: Optional, if set, look for this string first (regex)
        :param n: maximum replacements
        :return: None
        """
        if not self.is_exist:
            log.info(f'-i- search_replace({search}): {self.fname} not exist')
            return

        self._init()
        count = 0

        robj = None
        if isregex:
            robj = re.compile(search)

        rmark = None
        if marker:
            rmark = re.compile(marker)

        for idx in range(len(self.lines)):
            if marker and (not rmark.search(self.lines[idx])):
                continue     # ignore

            if isregex:
                if robj.search(self.lines[idx]):
                    self.lines[idx] = robj.sub(replace, self.lines[idx])
                    count += 1

            else:
                if search in self.lines[idx]:
                    self.lines[idx] = self.lines[idx].replace(search, replace)
                    count += 1

            if count == n:
                break

        return self

    def block_replace(self, search, replace, name):
        """
        Search and replace given block name.
        The block name is instance name, for example.
        The block is closed when a close bracket is found (starts with close bracket)
        Only first occurrence is changed

        :param search: search string (non-regex)
        :param replace: replacement string or list
        :param name: block name (regex)
        :return: None
        """
        if not self.is_exist:
            log.info(f'-i- block_replace({search}): {self.fname} not exist')
            return

        self._init()

        found = False
        robj = re.compile(name)

        for idx in range(len(self.lines)):
            if robj.search(self.lines[idx]):
                found = True
                continue    # do not search block line

            if self.lines[idx].lstrip().startswith('}'):
                found = False

            if found and search in self.lines[idx]:
                self.lines[idx] = self.lines[idx].replace(search, replace)
                found = False

        return self

    def write(self):
        """
        Rewrite the file
        """
        if not self.is_exist:
            log.info(f'-i- write(): {self.fname} not exist')
            return

        self.written = True
        File(self.fname).rewrite(''.join(self.lines), 'TPSwitch.write()')

    def _check_written(self):
        """Checks if file is written, so user don't forget"""
        confirm(self.written,
                f'TPSwitch("{self.fname}") has missing .write() call.',
                "Don't forget to write it.")

    @classmethod
    def main(cls, inputbom, root, which):
        """Call TP switch"""
        log.info(f'-i- START: TPSwitch {which} for {inputbom} in {root}')
        TPSwitch._set_tpobj(TestProgram(f'{root}/POR_TP/{inputbom}'))
        TPSwitch._process(os.environ.get('ACPY'), root=root)


class TPSwitch2(TPSwitch):

    @classmethod
    def _get_short_bom(cls):
        """Return shortbom name from tpobj"""
        confirm(TPSwitch.tpobj[0], 'tpobj is not defined', 'tpobj must be defined first')
        robj = re.compile(r"class_(\w+)", re.IGNORECASE)
        bomfolder = TPSwitch.tpobj[0].get_bomfolder()
        res = robj.search(bomfolder)
        confirm(res, f'Cannot find [{robj.pattern}] in {bomfolder}', 'Cannot derive Shortbom. Pls check')
        return res.group(1)

    @classmethod
    def _get_por_tps(cls, infile):
        """
        Iterator: return list of por_tp folders to copy. Return empty list if tpswitch1
        :param infile: os.environ('ACPY')
        :return: (portp, fname)
        """
        fflist, _ = cls._proc_infile(infile)
        robj = re.compile(r"POR_TP = (\[.*)$", re.MULTILINE)

        for fname in fflist:

            dd = {'SHORTBOM': cls._get_short_bom()}
            classname = f'{cls.__name__}('

            fulltext = File(fname).read()
            if classname not in fulltext:
                continue    # not TPSwitch2

            res = robj.search(fulltext)
            if res:
                rlist = eval(res.group(1))
            else:
                raise ErrorUser(f"No '{robj.pattern}' is found in {fname}",
                                f"'{robj.pattern}' is required in switch2 file")

            confirm(len(rlist) == 1, f"Expecting 1 element only in POR_TP = {res.group(1)}", f'Pls fix {fname}')

            for item in rlist:
                yield item.format(**dd), fname
