#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
r"""
Checks SkipModules vs committed files, branch vs main branch, temporary vs permanent

Error if this PR has skipmodule and modified module file.
Reason: MO might have forgotten to enable the module back

Definition:
1. branch name: Main branch: TP/\d+ name
                all other branches: !main_branch
2. permanent vs temporary: permanent: SkipModule/<mod>.permanent
                                      SkipModule/<mod>.txt

Usage:
1. Main branch: permanent is ok, temporary is error
2. Feature branch: permanent is ok, temporary is ok
3. Either branch: if modified file is a skipmodule, then error. Protection to remove the skip file.

Wiki: https://wiki.ith.intel.com/x/II-foQ

"""
import sys
import setenv

from gadget.pylog import log
from qgates.qgate_base import QGateBase
from main.qgate import QGateExecute
from tp.testprogram import TestProgram
from gadget.getgit import GitHub
from gadget.disk import Chdir
from gadget.tputil import get_modulename
from os.path import basename
import os
import glob


class SkipModuleCheck(QGateBase):

    def main(self):
        """Entry point of checker
        """
        # This qgate is applicable only on PR. Ignore for tpbuild.
        if self.not_from_pr():     # pragma: no cover
            log.info(f'-i- {self.__class__.__name__} is skipped, not from PR.')
            return 1

        # At this point, we are a PR
        # Do not accept any temporary in main branch
        skips = set(glob.glob('POR_TP/*/SkipModules/*.txt') +
                    glob.glob('Shared/POR_TP/*/SkipModules/*.txt'))
        skips = {x for x in skips if basename(x).lower() != 'readme.txt'}

        if skips:
            self.add_error(255, 'BASE',
                           (f'Cannot have temporary SkipModules in main branch. Temporary list: {skips} '
                            f'Either fix these modules or request approval to make these permanent'))
        else:
            self.add_pass(255, 'BASE')

        # Now check for modified files ====================
        with Chdir(QGateExecute.repodir):
            labels = GitHub.get_labels()
            modfiles = GitHub.get_modfiles()

        # Per PR override on modfile vs skipmodule
        # Example: TPI_IDV is permanently skipped but a file is updated in TPI_IDV
        if 'FORCED_MODULESKIP' in labels:
            log.info('-i- FORCED_MODULESKIP exist. Skipping check_skipmodule_commit()')
            return 2

        # get all skipmod files first
        skipmods = {}
        for ff in (glob.glob('POR_TP/*/SkipModules/*.txt') +
                   glob.glob('POR_TP/*/SkipModules/*.permanent') +
                   glob.glob('Shared/POR_TP/*/SkipModules/*.txt') +
                   glob.glob('Shared/POR_TP/*/SkipModules/*.permanent')):
            modname = basename(ff).split('.')[0]
            skipmods[modname] = ff

        # Error if found
        for modfile in modfiles:
            modname = get_modulename(modfile)
            if modname in skipmods:
                self.add_error(256, modname,
                               (f'Module=[{modname}] is skipped, but [{modfile}] is part of commit '
                                f'Pls delete [{skipmods[modname]}] first in your branch. '
                                f'This will enable {modname}. Or add FORCED_MODULESKIP label to keep this module skipped.'))
            else:
                self.add_pass(256, modname)


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    SkipModuleCheck(TestProgram(sys.argv[1]), frompr=True).run()
