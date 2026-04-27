#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
swiss_knife.py - various development tools

Usages:
swiss_knife.py *.yml -replace I:/tpvalidation/jqdelosr/pytpd         # sandbox validation
swiss_knife.py *.yml -replace any_string -src string_to_replace      # generic search and replace
swiss_knife.py *.yml -rule <path_to_py_rule> [-prev]                 # programmable search and replace
swiss_knife.py /intel/hdmxprogs/nvl /intel/tpvalidation/hdmxprogs/nvl -tprel              # tprel stats

See "CMD:" in -h
"""
from setenv import ROOT_ENV      # must be first in the imports
from gadget.vepargs import Args, TA_StoreTrue, TA_All, TA_Store, TA_StoreFile
from gadget.helperclass import OPT, CaptureStdoutLog, TagOnce
from gadget.dictmore import DictDot
from gadget.disk import Allfiles
from gadget.files import File, check_and_del
from gadget.pylog import log
from gadget.strmore import sha1, wwno, curtime
from collections import defaultdict, OrderedDict
from importlib.machinery import SourceFileLoader
from os.path import basename, dirname, join, isdir
from gadget.tvpv import TvpvEnv
import sys
import re
import os


class SKArgs(Args):   # parent: ArgsBase

    def config(self):
        """
        Define the arguments for the script.
        The order below will matter, it is the order of display during help.
        """
        cfg = DictDot()
        cfg.all = TA_All('see usage')
        cfg.imp = TA_StoreTrue('CMD: Count all used routines given import (eg. <dir>.<module>)')
        cfg.path = TA_StoreTrue('sourceme: Return the path to use')
        cfg.checkenv = TA_StoreTrue('sourceme: Prints success (after importing TestProgram)')
        cfg.emptyout = TA_StoreTrue('CMD: Empty out or zero out contents of this file, so unittests are faster')
        cfg.delgit = TA_StoreTrue('CMD: Delete special directory due to transition from gitsubmodule')
        cfg.compile = TA_StoreTrue('CMD: Compile all .py files')
        cfg.escape = TA_StoreTrue('CMD: Fix Invalid Scape encoding')
        cfg.src = TA_Store('Specify src string to replace. Used with -replace')
        cfg.replace = TA_Store('CMD: Replace all yml (or any file) with new value', metavar='I:/drive_path|replace_string')
        cfg.rule = TA_StoreFile('CMD: Replace all files in <arg0> given py rule file', metavar='path_to_py')
        cfg.notebook = TA_StoreTrue('CMD: Delete all [Open Notebook.onetoc2] file')
        cfg.prev = TA_StoreTrue('Used with -rule. Preview mode')
        cfg.tprel = TA_StoreTrue('CMD: Generate nvl hdmx and tpval tp release stats')
        cfg.noduptp = TA_StoreTrue('CMD: Output only uniq tp lines (used with -tprel out.csv files')
        return cfg

    def main(self):
        """
        Main entry point of executable
        -h will not reach this method, since that is taken cared of in Args Base class
        """
        if not OPT.all:
            if not (OPT.path or OPT.checkenv or OPT.compile or OPT.notebook):
                self.do_else()

        self.call_methods(['imp',       # call do_imp(), if -imp
                           'path',      # call do_path(), if -path
                           'checkenv',  # call do_checkenv(), if -checkenv
                           'emptyout',  # call do_emptyout(), if -emptyout
                           'delgit',    # call do_delgit(), if -delgit
                           'compile',   # call do_compile(), if -compile
                           'replace',   # call do_replace(), if -replace
                           'rule',      # call do_rule(), if -rule
                           'notebook',  # call do_notebook(), if -notebook
                           'tprel',     # call do_tprel(), if -tprel
                           'noduptp',   # call do_noduptp(), if -noduptp
                           'escape'     # call do_escape(), if -escape
                           ])           # do_else() is called if no argument command is processed

    def _import_module(self, pyfile):     # pragma: no cover
        """
        Returns the imported module
        """
        return SourceFileLoader(sha1(pyfile), pyfile).load_module()

    def do_tprel(self):
        """
        Gen tp rel stats
        :return:
        """
        TpRel().main(OPT.all)

    def do_noduptp(self):
        """
        Return no duplicate tp lines
        :return:
        """
        TpRel().nodup(OPT.all)

    def do_notebook(self):
        """
        Delete all [Open Notebook.onetoc2] files recursively from cwd
        """
        for ff in Allfiles('.'):
            if basename(ff) == 'Open Notebook.onetoc2':
                log.info(f'Deleting: {ff}')
                check_and_del(ff, error=False)

    def do_rule(self):
        """
        Given a python rule file (programmable), replace all specified files
        """
        rf = self._import_module(OPT.rule)
        for key in "regex replace".split():
            if not hasattr(rf, key):
                raise Exception(f"{OPT.rule} does not have [{key}]. This is required key. ")

        mainre = re.compile(rf.regex)

        # neg_re is the negative regex/filter-out
        if hasattr(rf, "negative"):
            neg_re = re.compile(rf.negative)
        else:
            neg_re = re.compile("SURE_notexist__1_2_888_" + "9_9")

        once = TagOnce()
        for fullpath in OPT.all:
            # dictionary per file, accessible in rules
            fd = DictDot()
            fd.filename = basename(fullpath)
            fd.path = dirname(fullpath)
            final = []
            found = 0

            if OPT.prev:
                for line in File(fullpath).raw():
                    robj = mainre.search(line)
                    if robj and (not neg_re.search(line)):
                        if line != rf.replace(line, robj, fd):
                            if once(fullpath):
                                log.info("\n{}:".format(fullpath))
                            log.info("From: {}".format(line.strip()))
                            log.info("  To: {}".format(rf.replace(line, robj, fd).strip()))

            else:
                for line in File(fullpath).raw():
                    robj = mainre.search(line)
                    if robj and (not neg_re.search(line)):
                        if line != rf.replace(line, robj, fd):
                            line = rf.replace(line, robj, fd)
                            found += 1
                    final.append(line)

                File(fullpath).rewrite(''.join(final), f'do_rule(). Replaced: {found} lines')

    def do_replace(self):
        """Update replace"""
        if OPT.src:
            replace = OPT.src
        else:
            replace = 'I:/tpvalidation/engtools/tptools/mtl/beta/gen1'

        for ff in OPT.all:
            found = 0
            lines = File(ff).raw()
            final = []
            for line in lines:

                if replace in line:
                    found += 1
                    line = line.replace(replace, OPT.replace)

                final.append(line)

            if not found:
                log.info(f'-w- File {ff} does not have [{replace}]. Is this expected?')

            File(ff).rewrite(''.join(final), f'do_yml(). Replaced: {found} lines')

    def do_escape(self):
        robj = re.compile(r'^(.*re\.(?:compile|search|findall|match)\()([\'\"].*)$')
        for file_path in OPT.all:
            final = []
            for line in File(file_path).raw():
                sline = line.rstrip()
                res = robj.search(sline)
                if res:
                    line = f'{res.group(1)}r{res.group(2)}\n'
                final.append(line)

            File(file_path).rewrite(''.join(final), 'do_escape()')

    def do_compile(self):
        """Create pyc files for all"""
        import compileall
        print(f"Starting compile from: {ROOT_ENV}")
        with CaptureStdoutLog(disp=False) as p:
            compileall.compile_dir(ROOT_ENV, quiet=0)
        for line in p.getvalue().split('\n'):
            if line.startswith('Compiling'):    # pragma: no cover
                print(line)
        print(f"Done! Compiler: {sys.executable}")

    def do_delgit(self):
        """
        Used by github automation, delete these special directory because of transition from
        normal to gitsubmodule. Use this im yml, then "git restore ." then "git submodule update blah"
        """
        for dd in "Modules/DRV_RESET_SXN".split():
            check_and_del(dd)
            print(f'{dd}: exists? {os.path.exists(dd)}')

    def do_path(self):
        """
        Prints the PATH to use. Used with env
        """
        to_add = f'{ROOT_ENV}/main'
        existing_path = os.environ.get('PATH', '.')

        if to_add in existing_path:
            print(existing_path)                          # same, no change
        else:
            print(f'{to_add}:{existing_path}')            # add path in front

    def do_emptyout(self):
        """Empty out the file (e.g. InputFiles/*) so that unittests is faster and save on disk space"""
        cnt = 0
        for ff in OPT.all:
            if os.path.isdir(ff):
                print(f"Skipping {ff} - directory")
                continue
            cnt += 1
            if os.path.getsize(ff) == 0:
                continue
            with open(ff, 'wb') as fh:
                print(f"Empty out: {ff}")
        print(f'-i- Done. Processed {cnt} files')

    def do_checkenv(self):
        """
        imports testprogram and prints success
        """
        from tp.testprogram import TestProgram
        print(f"Success! pytpd environment is {ROOT_ENV}")

    def do_imp(self):
        """
        Count all routines given import file
        Used to determine which routine is used where
        """
        robj = re.compile(f'^\\s*(from {OPT.all[0]} import )([^#\n]+)', re.MULTILINE)
        result = defaultdict(int)
        for fullpath in sorted(Allfiles(ROOT_ENV, skipsvn=True, rx=r"\.py$")):
            rpath = fullpath.replace(ROOT_ENV, '.')
            if '/test/' in fullpath:    # skip unittests
                continue

            lines = File(fullpath).read()
            for found in robj.findall(lines):
                print(f'{rpath:30} {found[0]}{found[1]}')

                # accumulate result
                for item in found[1].split(','):
                    result[item.strip()] += 1

        # print result
        print()
        for item in sorted(result, key=result.get, reverse=True):
            print('%3d  %s' % (result[item], item))


class TpRel:

    def __init__(self):
        self.site = TvpvEnv.get_site()

    def main(self, tppaths):
        """Main entry point"""
        # header
        print('tp,ww,area,site,series')

        # iterate to all paths
        for path in tppaths:
            self.process(path)

    def process(self, path):
        """Process one path area"""
        for tp in os.listdir(path):
            if not isdir(f'{path}/{tp}'):
                continue
            mtime = os.path.getmtime(f'{path}/{tp}')
            ww = 'ww%s' % (wwno(mtime, year=True))
            series = tp[10:12]
            if series:
                print('%s,%s,%s,%s,%s' % (tp, ww, path.split('/')[2], self.site, series))

    def nodup(self, files):
        """Read all the .csv files and return no dup"""
        data = OrderedDict()
        for ff in files:
            for line in File(ff).chomp():
                key = line.split(',')[0]
                if key not in data:
                    data[key] = line

        for key in data:
            print(data[key])


if __name__ == '__main__':  # pragma: no cover
    SKArgs(desc=__doc__).main()
