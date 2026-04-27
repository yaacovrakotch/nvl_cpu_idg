#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
This Qgate will check if the Shared submodule are pointing to the "main*" branch only.
Module submodules are checked if enable_main_branchname.txt exist on root folder:
     Modules/*/enable_main_branchname.txt
     Shared/Modules/*/enable_main_branchname.txt

This will help to prevent other module owner to point the Shared branch to other
branch and cause the issue later or break the dielet main branch.
"""
import sys
import setenv

from gadget.pylog import log
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
from gadget.shell import SystemCall
from gadget.getgit import GetCmd
from gadget.disk import Chdir
from main.qgate import QGateExecute
from pprint import pprint
import os
import glob


class SharedMainOnly(QGateBase):
    """
    This Qgate will check if the Shared submodule are pointint to the main branch only.
    """

    def return_sha_shared(self, folder):
        """Return the sha given submodule folder"""
        cmd = f'git submodule status {folder}'
        _, out = SystemCall(GetCmd.exe(cmd), disp=True).run_outtxt()
        if not out:
            return ''
        sha = out.strip().split()[0]
        return sha

    def get_target_folders(self):
        """
        Iterator: return folders that need checking
        Submodules that have enable_main_branchname.txt at root level will be checked
        """
        if os.path.isdir('Shared'):
            yield 'Shared'     # required for dielet

        # Module subfolders
        for targ in (glob.glob('Modules/*/enable_main_branchname.txt') +
                     glob.glob('Shared/Modules/*/enable_main_branchname.txt')):
            yield os.path.dirname(targ)

    def main(self):
        """Entry point of checker"""

        # This qgate is applicable only on PR. Ignore for tpbuild.
        if self.not_from_pr():     # pragma: no cover
            log.info(f'-i- {self.__class__.__name__} is skipped, not from PR.')
            return 1

        with Chdir(QGateExecute.repodir):

            for folder in self.get_target_folders():
                log.info(f'-i- SharedMainOnly: Checking {folder}:')
                shared_sha = self.return_sha_shared(folder)

                if shared_sha.startswith('+'):     # This is output when shared submodule is changed
                    continue

                if len(shared_sha) != 40:
                    self.add_error(247, 'BASE', f'Cannot get correct sha of {folder}. Result: [{shared_sha}]')
                    continue

                cmd = f'git -C {folder} branch -r --contains {shared_sha}'
                log.info(f'CMD: {cmd}')
                _, out = SystemCall(GetCmd.exe(cmd), disp=True).run_outtxt()

                main_flag = False
                for item in out.splitlines():
                    if 'origin/main' in item.strip():      # starts with 'main'
                        log.info(f'Found {item}')
                        main_flag = True

                if main_flag:
                    self.add_pass(247, 'BASE')
                else:
                    self.add_error(247, 'BASE', f'{folder} submodule is NOT from the MAIN branch.')


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    SharedMainOnly(TestProgram(sys.argv[1]), frompr=True).run()
