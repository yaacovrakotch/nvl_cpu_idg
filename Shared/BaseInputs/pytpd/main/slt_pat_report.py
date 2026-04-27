#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Generate a report given two testprograms.

Usage:
slt_pat_report.py <sort_path/EnvironmentFile.env> <class_path/EnvironmentFile.env>

Note: This script is generic with exception of '/class/' search in path for finder output class only.

"""
import setenv      # must be first in the imports
from tp.testprogram import TestProgram
from gadget.vepargs import Args, TA_All, TA_StoreTrue
from gadget.dictmore import DictDot, keys_atlevel
from gadget.helperclass import OPT
from gadget.printmore import PctIndicator, PrintAlign
from gadget.gizmo import Elapsed
from gadget.tputil import remove_ip
from gadget.files import TempName, File
from gadget.shell import SystemCall
from pprint import pprint
from collections import defaultdict
from os.path import basename
import glob
import re
import os


class SArgs(Args):   # parent: ArgsBase

    def config(self):
        """
        Define the arguments for the script.
        The order below will matter, it is the order of display during help.
        """
        cfg = DictDot()
        cfg.all = TA_All('SortTP and ClassTP')
        cfg.idrive = TA_StoreTrue('Compare with idrive')
        return cfg

    def main(self):
        """
        Main entry point of executable
        -h will not reach this method, since that is taken cared of in Args Base class
        """
        assert len(OPT.all) == 2, f"Incorrect input. See usage below\\:n\n{__doc__}"
        if OPT.idrive:
            self.main2()
            return

        sort_tp = TestProgram(OPT.all[0]).pickle_init()
        clas_tp = TestProgram(OPT.all[1]).pickle_init()
        all_pats_clas = clas_tp.plists.get_pats_all()
        mod_pats_sort = self.get_mod_pat(sort_tp)

        # Display result
        pa = PrintAlign(sep='|')
        pa('Module', 'tuple+tid Total', 'tid total', 'tuple+tid ClassTP', 'tid only ClassTP')
        for mod in sorted(mod_pats_sort):
            pa(mod,
               self.count(mod_pats_sort[mod], mod_pats_sort[mod]),
               self.count(mod_pats_sort[mod], mod_pats_sort[mod], True),
               self.count(mod_pats_sort[mod], all_pats_clas),
               self.count(mod_pats_sort[mod], all_pats_clas, True)
               )

        pa.disp()

    def main2(self):
        """
        Main entry point of executable
        -h will not reach this method, since that is taken cared of in Args Base class
        """
        assert len(OPT.all) == 2, f"Incorrect input. See usage below\\:n\n{__doc__}"

        sort_tp = TestProgram(OPT.all[0]).pickle_init()
        clas_tp = TestProgram(OPT.all[1]).pickle_init()
        all_pats_clas = clas_tp.plists.get_pats_all()
        mod_pats_sort = self.get_mod_pat(sort_tp)
        pats_idrv = ReadHdmxPats(clas_tp).read_all_pats()
        pats_tvpv = ReadTvpv(mod_pats_sort).read_all_pats()

        # Display result
        pa = PrintAlign(sep='|')
        pa('Module', 'Total', 'TVPV_Disk', 'IDrive', 'ClassTP')
        for mod in sorted(mod_pats_sort):
            pa(mod,
               self.count(mod_pats_sort[mod], mod_pats_sort[mod]),     # So it's consistent (tuple+tid)
               self.count(mod_pats_sort[mod], pats_tvpv),
               self.count(mod_pats_sort[mod], pats_idrv),
               self.count(mod_pats_sort[mod], all_pats_clas)
               )

        pa.disp()

    @staticmethod
    def count(refsort, target, tid_only=False):
        """
        Return count of matching tuple+tid
        :param refsort: patterns sort
        :param target: patterns target
        :param tid_only: use tid only as key
        :return: count of matching tuple+tid
        """
        if tid_only:
            set_ref = {x[9:16] for x in refsort}
            set_tar = {x[9:16] for x in target}
        else:
            set_ref = {x[:16] for x in refsort}
            set_tar = {x[:16] for x in target}

        # uncomment to display the patterns
        # for tup in set_ref & set_tar:
        #     for item in target:
        #         if item.startswith(tup):
        #             print(item)

        return len(set_ref & set_tar)

    @staticmethod
    def get_mod_pat(tpobj):
        """
        Return dictionary of module: patterns used

        :param tpobj: input module
        :return: {module: patterns}
        """
        result = defaultdict(set)

        kwargs = dict(passonly=False, bypass=True, keyparam='patlist', idict=True)
        for mod, item, data in tpobj.mtpl.iter_flows('MAIN', **kwargs):
            result[mod].update(tpobj.plists.get_pats_from_plb(remove_ip(data['patlist'])))
        return result


class ReadTvpv:
    """
    Read what is in tvpv using finder
    """
    def __init__(self, sort_dict):
        allpats = set(keys_atlevel(sort_dict, 1))
        self.tups = {x[:8] for x in allpats}

    def read_all_pats(self):
        """
        Return set of pattern that exist in tvpv disk via finder
        :return set of patterns
        """
        # call finder
        print(f"-i- Calling finder for {len(self.tups)} tuples ...")
        with TempName(name=True) as tname:
            File(tname).touch('\n'.join(self.tups))
            cmd = f'finder.py -list {tname} -echo bin'
            _, res = SystemCall(cmd).run_outtxt()

        # process output
        pats = set()
        for line in res.split('\n'):
            if not line.startswith('/'):
                continue
            if '/sort/' in line:    # class patterns only (MTL implementation!)
                continue
            path = line.split()[0]
            pats.add(basename(path))
        return pats


class ReadHdmxPats:
    """
    Read the i:\\ drive (/intel/hdmxpats)
    """

    def __init__(self, tpobj):
        self.roots = self._derive_roots(tpobj)

    def read_all_pats(self):
        """
        Read all pat/indv_bin directory in i:\\ drive
        :return: set of pattern names (with extension)
        """

        # Performance:
        # Reading each dir, total: 4309 ...
        #    152.058 Secs 2489643
        # Compared to read all .plist files and derive the patterns:
        #    Reading each .plists, total: 51301 ...
        #    1242.071 Secs

        allpats = set()
        for root in self.roots:
            print(f'Getting all pat/indv_bin in {root} ...')
            alldirs = glob.glob(f'{root}/*/*/*/pat/indv_bin')
            print(f'Reading each dir, total: {len(alldirs)} ...')
            sw = Elapsed()
            with PctIndicator(len(alldirs)) as ind:
                for dd in alldirs:
                    ind.disp()
                    allpats.update(os.listdir(dd))
            print(f"-i- Done reading: {sw}, total: {len(allpats)}")
        return allpats

    # def read_all_plist(self):
    #     """Read all plists to get all patterns"""
    #     # Reading each .plists, total: 51301 ...
    #     # 1242.071 Secs    <<<<< slow!!
    #
    #     r_pat = re.compile(r'^\s*(PrePattern|PreBurst|Pat)\s+(\w+)', re.MULTILINE)
    #     allpats = set()
    #     for root in self.roots:
    #         print(f'Getting all .plists in {root} ...')
    #         allplists = glob.glob(f'{root}/*/*/*/plb/*.plist')
    #         print(f'Reading each .plists, total: {len(allplists)} ...')
    #         sw = Elapsed()
    #         with PctIndicator(len(allplists)) as ind:
    #             for plb in allplists:
    #                 ind.disp()
    #                 with open(plb) as fh:
    #                     txt = fh.read()
    #                 for _, pat in r_pat.findall(txt):
    #                     allpats.add(pat)
    #         print(sw)

    def _derive_roots(self, tpobj):
        """Derive all the hdmxpats roots given tp"""
        rpath = re.compile(r"^((?:I:|/intel)/hdmxpats/\w+)")
        result = set()
        for item in sorted(tpobj.env.get_plist_paths()):
            res = rpath.search(item)
            if res:
                result.add(res.group(1))
        return result


if __name__ == '__main__':  # pragma: no cover
    SArgs(desc=__doc__).main()
