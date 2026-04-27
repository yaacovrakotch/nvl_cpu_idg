#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
fuse diff

cd /intel/tpvalidation/hdmxprogs/mtl
fuse_diff.py ??????????23*/POR_TP/*/EnvironmentFile.env
"""
import setenv      # must be first in the imports
from gadget.vepargs import Args, TA_StoreTrue, TA_All, TA_AppendSC
from tp.testprogram import TestProgram, Env
from gadget.gizmo import Elapsed
from gadget.pylog import log
from gadget.shell import SystemCall
from gadget.errors import confirm, ErrorUser
from gadget.files import File
from gadget.disk import listdir_noerror
from gadget.dictmore import DictDot
from gadget.helperclass import OPT
from gadget.strmore import str_index_expander
from pprint import pprint
from collections import defaultdict
from os.path import isdir, dirname, exists
import re
import os
import shutil
import sys


class FuseDiffArg(Args):   # parent: ArgsBase

    def config(self):
        """
        Define the arguments for the script.
        The order below will matter, it is the order of display during help.
        """
        cfg = DictDot()
        cfg.all = TA_All('see usage')
        cfg.noreleased = TA_StoreTrue('Do not include released versions')
        cfg.skip = TA_AppendSC('Skip these short TP')
        return cfg

    def main(self):
        """
        Main entry point of executable
        -h will not reach this method, since that is taken cared of in Args Base class
        """
        if not OPT.all:
            raise Exception(__doc__)

        FuseDiff().main()


class FuseDiff:

    def __init__(self):
        # accumulator for sspec summary of changed bits
        self.sum1 = []
        self.ctr1 = defaultdict(set)     # (item, field): list_of_TP

    def main(self):
        """Main Entry point"""
        sys.stderr.write("TP compare order:\n")
        prev = None
        prevtp = None
        prevfusedef = None
        for tp in self.get_tp_list():

            # specified skip
            sname = self.get_shortname(tp)
            if sname in OPT.skip:
                sys.stderr.write(f'TPName {sname} skipped via -skip\n')
                continue

            # skip wierd TP
            if not re.search(r"^\w\w\w\d\w\w", sname):
                sys.stderr.write(f'TPName {sname} skipped - non standard\n')
                continue

            tpobj = TestProgram(tp)
            sys.stderr.write(f'TPName {sname}\n')

            data = {}
            fusedef = {}
            for item in 'FUSE_ROOT_DIR_C28 FUSE_ROOT_DIR_C68 FUSE_ROOT_DIR_GLG FUSE_ROOT_DIR_GMD FUSE_ROOT_DIR_IOEP FUSE_ROOT_DIR_SXM'.split():
                path = Env.xpath(tpobj.env.get_item(item))
                fusedef[item] = self.read_fusedef(path)
                data[item] = self.read_sspec(path)

            if prev is not None:
                self.compare(self.get_shortname(tp), prev, data, self.get_shortname(prevtp), fusedef, prevfusedef)
            prev = data
            prevtp = tp
            prevfusedef = fusedef

        # display the summary
        print()
        print("Part1 - per TP summary:")
        for item in self.sum1:
            print(item)

        fieldctr = defaultdict(int)
        fieldctrTP = defaultdict(set)
        print()
        print("Part2 - per fuse bit changes:")
        for key in sorted(self.ctr1, key=lambda x: len(self.ctr1[x])):
            item, field = key
            itemshort = item.split('_')[-1]
            tps = ', '.join(self.ctr1[key])
            if '_heap_' not in field:    # Request by DavidB to skip

                # This is per bit summary
                print(f"-d- Sum2: {itemshort} - {field} - Changed {len(self.ctr1[key])} times: {tps}")
                # fieldctr[f'{itemshort} {fusedef[item][bit]}'] += len(self.ctr1[key])
                # fieldctrTP[f'{itemshort} {fusedef[item][bit]}'].update(self.ctr1[key])

        # TODO: Note: the fusedef[item][bit] is wrong, since fusedef is different per testprogram (aka, bit numbers move around)
        # Thus, make this so the key is the string, not the number

        # for item in sorted(fieldctr):
        #     tps = ', '.join(sorted(fieldctrTP[item]))
        #     print(f'SUM2: {item} - Changed {fieldctr[item]} times: {tps}')

    def compare(self, tpshort, prev, data, prevshort, fusedef, prevfusedef):
        """
        Compare two, then display
        :param tpshort: string: short name of new tp
        :param prev: dict: prev tp data {sspec: {bit: value}}
        :param data: dict: new tp data  {sspec: {bit: value}}
        :param prevshort: string: short name of prev tp
        :param fusedef: dict: new tp fusedef
        :param prevfusedef: dict: prev tp fusedef
        :return:
        """
        for item in data:
            itemshort = item.split('_')[-1]
            for sspec in data[item]:
                if item not in prev or sspec not in prev[item]:
                    continue
                if data[item][sspec] == prev[item][sspec]:
                    pass
                    # print(f"Sum1: {tpshort} - {itemshort} - {sspec} - NoDiff")
                else:
                    # count the diff
                    diffs = set()
                    for bit, value in data[item][sspec].items():
                        if value != prev[item][sspec][bit]:
                            field = fusedef[item][bit]
                            diffs.add(field)
                            self.ctr1[(item, field)].add(tpshort)

                    self.sum1.append(f"Sum1: {prevshort}->{tpshort}: {itemshort} - {sspec} - {len(diffs)} fuse fields changed")

    def read_sspec(self, path):
        """
        Read sspec, return data structure

        :param path: path to sspec file
        :return: {sspec: {bit: value}}
        """
        result = {}
        if not exists(f'{path}/sspec.txt'):
            return result

        for line in File(f'{path}/sspec.txt').chomp():
            line = line.strip()
            if line.startswith('FUSEDATA:'):
                if '#' in line:
                    line = line[:line.find('#')]
                elems = line.split(':')
                assert len(elems) == 5, f'Expecting 5 elements, Line: {line}'

                sdata = {}
                fullbits = elems[4].strip()
                fulllen = len(fullbits)
                for idx, value in enumerate(fullbits):
                    sdata[fulllen - idx - 1] = value

                sspec = elems[2].strip()
                result[sspec] = sdata

        return result

    def read_fusedef(self, path):
        """
        Read fusedef file, return data structure

        :param path: path
        :return: {bit: description}
        """
        result = {}
        for line in File(f'{path}/fusedef.txt').chomp():
            line = line.strip()
            if line.startswith('fusedef:'):
                if '#' in line:
                    line = line[:line.find('#')]
                elems = line.split(':')
                assert len(elems) == 6, f'Expecting 6 elements, Line: {line}'
                for bit in str_index_expander(elems[2]):
                    assert bit not in result, f'oopsie: {bit} already exist: {elems[4]}: {elems[5]}'
                    result[int(bit)] = f'{elems[4].strip()}: {elems[5].strip()}'

        return result

    def get_tp_list(self):
        """
        Return list of tp, from commandline: *23*/POR_TP
        It will sort according to the version
        """
        if OPT.noreleased:
            target = [x for x in OPT.all if x[13:15] != '00']
        else:
            target = OPT.all

        return sorted(target, key=self.get_shortname)

    def get_shortname(self, tp):
        """Returns the shortname of the tp"""
        return tp[10:16]


if __name__ == '__main__':  # pragma: no cover
    FuseDiffArg(desc=__doc__).main()
