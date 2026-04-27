#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
bgrep.py - block grep, display block name (otpl files) where found lines are

Usage:
   tp_grep.py search_string <file> ...
   tp_grep.py regex_string  <file> ...
   tp_grep.py "DUTFlow Item" <file> -block
   tp_grep.py IREF_TRIM_ATOM0 IREF_TRIM_ATOM1 ATOM1:ATOM0 -link file.mtpl
   tp_grep.py Modules/*/*.usrv -duprule

"""
import setenv      # must be first in the imports
from gadget.vepargs import Args, TA_StoreTrue, TA_All, TA_Store
from gadget.helperclass import OPT
from gadget.dictmore import DictDot
from gadget.errors import ErrorUser, confirm
from gadget.files import File
from gadget.tputil import OtplFile, SDiff, MtplBlocks
from gadget.strmore import indent
from os.path import basename, dirname
from collections import defaultdict
import re


class BArgs(Args):   # parent: ArgsBase

    def config(self):
        """
        Define the arguments for the script.
        The order below will matter, it is the order of display during help.
        """
        cfg = DictDot()
        cfg.all = TA_All('see usage')
        cfg.i = TA_StoreTrue('Ignore case')
        cfg.n = TA_StoreTrue('Show line no')
        cfg.f = TA_StoreTrue('Do not display filename')
        cfg.block = TA_StoreTrue('CMD: grab this block and display it. Enclose in quotes for block and name.')
        cfg.recurse = TA_StoreTrue('CMD: grab this block and all its members recursively.')
        cfg.link = TA_Store('Compare and show diff', metavar='file.mtpl')
        cfg.duprule = TA_StoreTrue('Report duplicate rules given *.usrv files')
        return cfg

    def main(self):
        """Main Entry point"""
        self.call_methods(['link',      # this will call do_link(), if -link
                           'block',     # this will call do_block(), if -block
                           'recurse',   # this will call do_recurse(), if -recurse
                           'duprule',   # this will call do_duprule(), if -duprule
                           ])

    def do_duprule(self):
        """Display duplicate rules given the .usrv files"""
        clean = 0
        for ff in OPT.all:
            if DupRule(ff).identify(detail=bool(len(OPT.all) == 1)):
                clean += 1

        print()
        print(f"Total clean files: {clean}")

    def do_block(self):
        """-block"""
        for fname in OPT.all[1:]:
            for line in OtplFile(fname).get_block(*OPT.all[0].split()):
                print(line.rstrip())

    def do_recurse(self):
        """-recurse"""
        for fname in OPT.all[1:]:
            res = {}
            MtplBlocks(fname).recurse(OPT.all[0], res)
            for item in sorted(res):
                for line in res[item]:
                    print(line.rstrip())

    def do_else(self):
        """
        Main grep
        """
        if not OPT.all:
            print("Nothing to do.")
            print("")
            self.print_help()

        confirm(len(OPT.all) >= 2,
                "Incorrect number of arguments",
                "Usage: bgrep.py search_string <file> ...")

        text = OPT.all[0]
        files = OPT.all[1:]

        # main search regex object
        if OPT.i:
            robj = re.compile(text, re.IGNORECASE)
        else:
            robj = re.compile(text)

        for fname in files:
            self._grep_file(fname, robj, files)

    def do_link(self):
        """
        Compare the blocks
        :return:
        """
        mtpl = OPT.link
        block1, block2, replace = tuple(OPT.all)

        res1 = {}
        MtplBlocks(mtpl).recurse(block1, res1)
        res2 = {}
        MtplBlocks(mtpl).recurse(block2, res2)

        # do the search and replace
        r_find, r_replace = replace.split(':')
        list1 = []
        for item in sorted(res1):
            for line in res1[item]:
                list1.append(line)
        list2 = []
        for item in sorted(res2):
            for line in res2[item]:
                list2.append(line)
        list2 = [x.replace(r_find, r_replace) for x in sorted(list2)]
        list2 = [x.replace(r_find.lower(), r_replace.lower()) for x in list2]

        print(f'Stat: {block1}:{len(list1)} {block2}:{len(list2)}')
        print('Compare Result ===================')
        SDiff().simple(list1, list2, diffonly=True, autowrap=True)

    def _grep_file(self, fname, robj, files):
        """
        grep one file

        :param fname: filename
        :param robj: regex obj
        :param files: list of files
        :return:
        """
        # initialization: filename display
        fdisp = ""
        if len(files) > 1:
            fdisp = '%s: ' % basename(fname)
        if OPT.f:
            fdisp = ""

        # read the file first, put all "}" into previous line, since this identifies a block
        result = []
        for line in File(fname):
            line = line.split('#')[0].strip()
            if line.startswith('{'):
                result[-1] += ' {'
            result.append(line)

        # do the grep
        self.robj_block = re.compile(r"^(\w.*?)\s*\{$")     # Also used by unittests
        block = []
        number = ""
        for lno, line in enumerate(result):
            # display found line
            if robj.search(line):
                if OPT.n:
                    number = "#%s " % (lno + 1)
                print(("{fname}{number}{block}: {line}"
                       "".format(fname=fdisp,
                                 number=number,
                                 block='->'.join(block),
                                 line=line)))

            # block logic
            res = self.robj_block.search(line)
            if res:
                block.append(res.group(1))
            if line.startswith('}'):
                if not block:
                    raise ErrorUser("[%s] seems to be having problems. '}' is found in line#%s but no opening "
                                    "block found." % (fname, lno + 1),
                                    "Contact jqdelosr.")
                block.pop()


class DupRule:

    def __init__(self, fname):
        self.fname = fname
        self.ofile = OtplFile(fname).set_cache()
        self.module = basename(dirname(fname))

    def get_all_blocks(self):
        """
        :return: list of SelectorRule blocks
        """
        robj = re.compile(r"^SelectorRule\s+(\w+)")
        result = set()

        for lno, line in self.ofile.mlines:
            res = robj.search(line)
            if res:
                name = res.group(1)
                confirm(name not in result,
                        f'[SelectorRule {name}] is defined twice in {self.fname}',
                        f'Contact jqdelosr')
                result.add(res.group(1))
        return result

    def identify(self, detail=False):
        """
        Identify duplicate rules
        :param detail: Set to True to show details
        :return: True for clean
        """
        blocks = self.get_all_blocks()

        # iterate to all blocks and see what is dup
        dup = defaultdict(set)
        for block in blocks:
            lines = list(self.ofile.get_block('SelectorRule', block))
            key = '\n'.join(x.strip() for x in lines[1:])
            dup[key].add(block)

        if detail:
            for key in sorted(dup):
                print()
                for idx, block in enumerate(sorted(dup[key])):
                    print(f'{idx + 1}. {block}:')
                print(indent(3, key))
            print()

        if len(blocks) and len(blocks) != len(dup):
            print('count=%3d uniq=%3d: %s' % (len(blocks), len(dup), self.fname))
            return False

        return True   # clean


if __name__ == '__main__':  # pragma: no cover
    BArgs(desc=__doc__).main()
