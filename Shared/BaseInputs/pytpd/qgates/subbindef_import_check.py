#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Ensure Subbindef IP import is matched with the tpproj file.
This will fix the issue with load when others are cloning the repo directly
"""

import os
import shutil
import sys
import setenv
from gadget.disk import Chdir
from gadget.pylog import log
from gadget.shell import SystemCall, CALLERBIN, untar
from qgates.qgate_base import QGateBase
from gadget.gizmo import Elapsed
from tp.testprogram import TestProgram
from os.path import basename, dirname
import glob


class SubbindefImportChk(QGateBase):
    """
    This will check if the imported-subbindef-file module exists in the tpproj.
    If not, gate the PR because it will fail load if the MO load the repo directly.
    """

    def return_subbindef_files(self, tpldir):
        """
        Return the list of subbindef files in the tpldir.
        """
        subbindef_files = (glob.glob(f'{tpldir}/BaseInputs/*/*_Files/*_SubBindef.imp') +
                           glob.glob(f'{tpldir}/Shared/BaseInputs/Common/Common_Files/*_SubBindef.imp'))
        log.info(f'-i- Found {len(subbindef_files)} subbindef files in {tpldir}')
        return subbindef_files

    def main(self):

        # use the complete tar file for this qgate, because of MV or SkipModule, the programflows is updated
        if not QGateBase.fulltpobj:
            log.info('-i- No fulltpobj, using complete_tp.tar.gz')
            self.add_error(260, 'BASE', f'complete_tp.tar.gz does not exist')
            log.info("SubbindefImportChk Qgate: Please rerun your checker to verify.")
            return
        with Chdir(QGateBase.fulltpobj.tpldir):
            log.info(f'-i- fulltp (temp) cwd: {os.getcwd()}')

            self.tpobjfull = QGateBase.fulltpobj

            tpldir = self.tpobjfull.tpldir
            env_path = self.tpobjfull.envfile

            # Get the SubBindef.imp files
            subbindef_files = self.return_subbindef_files(tpldir)
            # Get subbindef modules
            subbindef_mods = []
            for item in subbindef_files:
                log.info(f'-i- Checking: {item}')
                with open(item, 'r') as f:
                    f_lines = f.readlines()
                for line in f_lines:
                    if line.startswith('Import'):
                        mod_path = line.split('\"')[1]
                        mod = basename(dirname(mod_path))
                        subbindef_mods.append(mod)
            log.info(f'-i- Found {len(subbindef_mods)} subbindef modules: {subbindef_mods}')
            # Read the tpproj file
            log.info(f'-i- Checking tpproj file in {dirname(env_path)}')
            tpproj = glob.glob(f'{dirname(env_path)}/*.tpproj')[0]
            with open(tpproj, 'r') as f:
                tpproj_content = f.read()
            for mod in subbindef_mods:
                if mod not in tpproj_content:
                    self.add_error(260, 'BASE', f'SubBindef module {mod} not found in tpproj file')
                    log.error(f'-e- SubBindef module {mod} not found in tpproj file {tpproj}')
                else:
                    self.add_pass(260, 'BASE')


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    SubbindefImportChk(TestProgram(sys.argv[1]))
