#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
r"""
pobj caching script.
See: https://wiki.ith.intel.com/x/YS9BwQ

SystemCall(below)
HdmtSocketTranslator.exe -i I:\engineering\dev\sctp\users\pbusser_sctp\ARL\POBJ_CACHE\soc_pin_dir\%1\%2_CPU.txt
-s I:\engineering\dev\sctp\users\pbusser_sctp\ARL\POBJ_CACHE\soc_pin_dir\%1\CLASS_H68G2_HDMT_1.soc
-n I:\engineering\dev\sctp\users\pbusser_sctp\ARL\POBJ_CACHE\soc_pin_dir\%1\
-o L:\cachepatterns\OutputPobj_%1
-j 50 -b IP_CPU

Script usage:
main/pobj_cache.py preload  <path_to_env>        # Call this before bot (deletes tpfix)
main/pobj_cache.py postload <path_to_env>        # Call this after bot (copy tpfix to L:\)
main/pobj_cache.py postload_donly <path_to_env>  # Call this after bot, if no L:\ drive (copy tpfix to D:\)
main/pobj_cache.py sha <path_to_env>             # Print the soc sha of this TP
"""
import setenv      # must be first in the imports
from tp.testprogram import TestProgram
from gadget.gizmo import Elapsed
from gadget.pylog import log
from gadget.shell import SystemCall
from gadget.errors import confirm, ErrorUser
from gadget.files import File
from gadget.disk import listdir_noerror
from collections import defaultdict
from os.path import isdir, dirname, exists
import re
import os
import shutil
import sys


class PobjCopy:
    """
    POBJ Cache copy to L:\\ drive. See main() for algo.
    This is called from mbot or tpbot.

    Rev1 Workflow (Do nothing if L:\\ path is not socsha)
    #0  - Call preload() from buildtp.py, before TP is loaded, only for xbots.
    #00 - PRELOAD: convention "L:\\cachepatterns\\OutputPobj_ARLA_<tpsocsha6>;"
    #0a - PRELOAD: If .soc is not matching socsha, then ERROR out, that L:\\ drive cache must be updated to new sha
    #0b - PRELOAD: See if tpfix is socsha, if no, delete all tpfix, via dirname(TPFIXPATH)/sha_tpfixpath.txt
    #0c - PRELOAD: Confirm() L:\\ and D:\\ path is the same in env file.
    #0d - PRELOAD: Copy L:\\ to D:\\ (so both tpbot and mbot works). Store sw()
    #1  - Load TP normally. This will populate TPFIXPATH for new pobj. Loadtime is slow first time around.
    #2  - Call main() from buildtp.py, after TP is done, only for bin1, only for TPBOT (do not call on mbot).
    #   - main() will copy tpfix to L:\\ drive

    Validation:
    #1 - Use tpbot, draft pr, TPI_NR, branch with socsha in env file
    #2 - first time, expect tpfix deleted, then pobj copied to L:\
       - confirm that excluded file is both _com and _pre
    #3 - second time, expect no tpfix delete, no pobj copied to L:\\ drive - fast load.
    #4 - delete a file in L:\\ drive, reload, expect 1 missing, confirm it copied in L:\\ drive

    Scenarios (L:/drive_path is socsha):
    #1 - New socsha, first TP
          -> tpfix is deleted PRE-LOAD
          -> Load normally, tpfix populated
          -> all pobj is copied to L:\\ drive. This is clean.
    #2 - Existing socsha, 2nd or N TP
          -> Load normally, tpfix populated
          -> all missing pobj is copied to L:\\ drive. This is also clean.
    #3 - Different socsha, nth TP
          -> tpfix is deleted PRE-LOAD
          -> Load normally, tpfix populated for missing
          -> all pobj is copied to L:\\ drive. This is clean.
    """
    TPFIXPATH = r'C:\Users/SysC/AppData/Local/Temp/TPFIXPATH'
    ROBJ_SHA = re.compile('_([0-9a-f]{6})$')

    def __init__(self, tpobj):
        self.tpobj = tpobj

    def main_preload(self):
        """Do preload logic - called from buildtp.py before tp is loaded"""
        sw = Elapsed()

        # 00 - PRELOAD: convention "L:\cachepatterns\OutputPobj_ARLA_<tpsocsha6>;"
        lpath = self.get_lpath()
        res = self.ROBJ_SHA.search(lpath)
        if not res:
            log.info(f'-i- PobjCopy() is ignored since L:/cachepatterns path [{lpath}] does not follow convention.')
            return 1       # Do nothing

        # 0a - PRELOAD: If .soc is not matching socsha, then ERROR out, that L:\ drive cache must be updated to new sha
        cachesha = res.group(1)
        tpsha = self.tpobj.pin.get_soc_sha()
        confirm(cachesha == tpsha,
                f'env file has [{lpath}], expecting sha of _{tpsha} based on .soc files',
                f'Pls update env file (both L: and D:) cache path to use _{tpsha}')

        # 0b - PRELOAD: See if tpfix is socsha, if no, delete all tpfix, via dirname(TPFIXPATH)/sha_tpfixpath.txt
        tpfixsha_fname = f'{dirname(self.TPFIXPATH)}/sha_tpfixpath.txt'
        tpfixsha = ''
        if exists(tpfixsha_fname):
            tpfixsha = File(tpfixsha_fname).read().strip()
        if cachesha != tpfixsha:
            log.info(f'-i- PobjCopy() deleting {self.TPFIXPATH} since socsha is different')
            for subdir in listdir_noerror(self.TPFIXPATH):
                shutil.rmtree(f'{self.TPFIXPATH}/{subdir}')
            File(tpfixsha_fname).touch(cachesha, newfile=True)

        # 0c - PRELOAD: Confirm() L:\ and D:\ path is the same sha in env file.
        dpath = self.get_dpath()
        res = self.ROBJ_SHA.search(dpath)
        if not res:
            log.info('-i- PobjCopy() is ignored since D:/OutputPobj_<sha> does not exist.')
            return 2   # Do nothing
        dsha = res.group(1)
        confirm(cachesha == dsha,
                f'Inconsistent sha in env: [{lpath}] and [{dpath}].',
                f'Pls make sure sha of L: and D: path in env file matches')

        # 0d - PRELOAD: Copy L:\ to D:\ (so both tpbot and mbot works). Store sw()
        self.robocopy(lpath, dpath)
        log.info(f'-i- PobjCopy() preload is complete in {sw}')

    def main_postload(self, donly=False):
        """
        Copy to L:\\ drive. Do not put this in mbot yml.

        Algo:
        #1 - Get the "L:\\cachepatterns" path from env file
        #2 - Get all .pobj in this path
        #3 - Get all .pobj in TPFIXPATH
        #4 - Check for two .pobj in TPFIXPATH. Delete if there are. Reason: we don't know which one to copy.
        #5 - Copy sha-folder via robocopy, for those that are missing in L:\\ drive
        """

        # 1 – Get the "L:\cachepatterns" path from env file
        if donly:
            lpath = self.get_dpath()
        else:
            lpath = self.get_lpath()

        log.info(f'-i- PobjCopy postload: using {lpath}')
        if not self.ROBJ_SHA.search(lpath):
            log.info(f'-i- PobjCopy() is ignored since L:/cachepatterns path [{lpath}] does not follow convention.')
            return 11       # Do nothing

        # 2 – Get all .pobj in this path
        all_el = self.read_onedir(lpath)

        # 3 – Get all .pobj in TPFIXPATH
        # 4 – Check for two .pobj in TPFIXPATH. Delete if there are. Reason: we dont know which one to copy.
        all_tpfix = self.read_tpfix()

        # 5 – Copy the .pobj that is missing in L:\, to L:\ drive
        missing = all_tpfix.keys() - all_el
        # for item in missing:
        #    print(f'{all_tpfix[item]}/{item} {lpath}')

        log.info(f'-i- PobjCopyStat: missing_pobj: {len(missing)} from {lpath}, Total: {len(all_el)}. '
                 f'TPFIXPATH: {len(all_tpfix)}')
        subfolder = {all_tpfix[x] for x in missing}
        sw = Elapsed()
        for item in sorted(subfolder):
            self.robocopy(item, lpath)

        print(f"-i- PobjCopy complete in {sw}, missing_pobj: {len(missing)}")
        self.missing = missing    # for unittests

    def robocopy(self, item, lpath):    # pragma: no cover
        """Run robocopy"""
        cmd = f'robocopy {item} {lpath} /E /XC /XN /XO /NFL /NP /R:1 /W:1 /XF ???_com*.pobj ???_pre*.pobj'
        SystemCall(cmd, disp=True).run_outtxt()

    def get_lpath(self):
        r"""Get the L:\cachepatterns path from env file"""
        ppath = self.tpobj.env.get_item('HDST_PAT_PATH', islist=True)
        robj = re.compile('L:.cachepatterns')
        for item in ppath:
            if robj.search(item):
                return item
        return ''

    def get_dpath(self):
        r"""Get the D:\OutputPobj path from env file"""
        ppath = self.tpobj.env.get_item('HDST_PAT_PATH', islist=True)
        robj = re.compile('D:.OutputPobj_')
        for item in ppath:
            if robj.search(item):
                return item
        return ''

    def read_onedir(self, path):
        """Return all files (set) in path, if it exist"""
        if isdir(path):
            return set(os.listdir(path))
        return set()

    def read_tpfix(self):
        """Return all files {patname: location} in tpfix, less duplicates"""
        tpfix = self.TPFIXPATH
        if not isdir(tpfix):
            return {}

        combined = defaultdict(list)
        for sdir in os.listdir(tpfix):
            for item in self.read_onedir(f'{tpfix}/{sdir}'):
                if item[3:7] in ('_com', '_pre'):    # Do not save subroutines/preambles
                    continue
                combined[item].append(f'{tpfix}/{sdir}')

        # delete duplicates
        final = {}
        for item, val in combined.items():
            if len(val) > 1:   # duplicate
                log.info(f'-i- Duplicate found in TPFIX. Deleting: {item}')
                for ditem in val:
                    os.unlink(f'{ditem}/{item}')

            else:
                assert len(val) == 1, f'code error: len is zero for {item}. Call jqdelosr'
                final[item] = val[0]

        return final

    @classmethod
    def main(cls):
        """Main entry point of executable"""
        confirm(len(sys.argv) == 3, 'Incorrect input args', __doc__)
        tpobj = TestProgram(sys.argv[2])
        if sys.argv[1] == 'preload':
            res = cls(tpobj).main_preload()
        elif sys.argv[1] == 'postload':
            res = cls(tpobj).main_postload()
        elif sys.argv[1] == 'postload_donly':
            res = cls(tpobj).main_postload(donly=True)
        elif sys.argv[1] == 'sha':
            print(tpobj.pin.get_soc_sha())
            res = 5
        else:
            raise ErrorUser(f'[{sys.argv[1]}] is invalid', __doc__)

        return res    # for unittest


if __name__ == '__main__':  # pragma: no cover
    PobjCopy.main()


# CODE STUDY
# /c/Users/SysC/AppData/Local/Temp/TPFIXPATH
# using tprobot tester: tpfixpath is empty (most probably it's using the D:\ or L:\)?
# mrobot P28 experiment: There is no D:\ drive in this tester.
# EXPT1: use P28 mrobot: Empty TPFIXPATH and L:\ is not in env.
#    what will become of TPFIXPATH? answer regenerated. Files in TPFIXPATH: 57,382
#    Mbot run is 1hr 54 mins (slow)
#    How much is uniq in TPFIXPATH vs L:? 2494
#    learning: TPFIXPATH is auto populated (loadtime is slow)
# EXPT2: 58K files in TPFIXPATH. How much of pats in copy_TPFIXPATH is in L:\ or D:\.
#    Total L: 99425, unique in TPFIXPATH: 2483

# uniq = set()
# for subdir in os.listdir('.'):
#     ff = set(os.listdir(subdir))
#     print('%s %5d %5d Duplicates %s' % (subdir, len(ff), len(uniq), uniq & ff))
#     uniq.update(ff)

# compare with D:\OutputPobj_TP38  (not exist in mbot tester)
# print()
# d_drive = '/d/OutputPobj_TP38'
# d_files = set(os.listdir(d_drive))
# print('Total D: %s, unique in TPFIXPATH: %s' % (len(d_files), len(uniq - d_files)))

# print()
# l_drive = f'L:/cachepatterns/OutputPobj_TP38'
# print('exist', os.path.exists(l_drive))
# print('isdir', os.path.isdir(l_drive))
# l_files = set(os.listdir(l_drive))
# print('Total L: %s, unique in TPFIXPATH: %s' % (len(l_files), len(uniq - l_files)))
# exit(0)
