#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Ensure ProgramFlows pymtpl source code matches mtpl.
This will re-generate the IP and PKG programflow files directly from the .py files.
Then compare them to existing IP and PKG programflow files to ensure they are matching.
Will result in Qgate error if it does not match.

"""

import os
import shutil
import sys

try:
    import setenv
except ImportError:    # pragma: no cover    - Used when local qgate .py is in tp area
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')

from gadget.dictmore import xmlfunc, iter_dot_items, find_dot_items
from gadget.disk import Chdir
from gadget.files import File, TempDir
from gadget.helperclass import OPT
from gadget.pylog import log
from gadget.shell import SystemCall, CALLERBIN, untar
from gadget.tputil import SDiff
from qgates.qgate_base import QGateBase
from gadget.gizmo import Elapsed
from tp.testprogram import TestProgram
from pymtpl.core import PyMtpl
from pprint import pprint
from os.path import basename, dirname


class ProgramFlowChecker(QGateBase):
    ERROR_TYPE = 'FLOW'

    die_list_mapping = {
        "IPC": "CPU",
        "IPG": "GCD",
        "IPH": "HUB",
        "IPP": "PCD",
    }

    mtpl_to_py = {
        "IPC_FLOWS.mtpl": "IPC_FLOWS.py",
        "IPG_FLOWS.mtpl": "IPG_FLOWS.py",
        "IPH_FLOWS.mtpl": "IPH_FLOWS.py",
        "IPP_FLOWS.mtpl": "IPP_FLOWS.py"
    }

    DIELET_PRIORITY = ["IPC_FLOWS.mtpl", "IPG_FLOWS.mtpl", "IPH_FLOWS.mtpl", "IPP_FLOWS.mtpl"]

    def backup_file(self, file_path):
        backup_path = file_path + '.backup'
        shutil.copy(file_path, backup_path)
        return backup_path

    # remove
    def read_file(self, file_path):
        with open(file_path, 'r') as f:
            return f.read().splitlines(keepends=True)
        # return File(file_path).read()

    def compare_files(self, filename, original_lines, new_lines):
        py_script = f'{filename.split(".")[0]}.py'
        if original_lines != new_lines:
            SDiff().simple(original_lines.split('\n'), new_lines.split('\n'), diffonly=True, maxdisp=20)
            self.add_error(270, self.ERROR_TYPE, f"{py_script} does not match with {filename}!")
        else:
            self.add_pass(270, self.ERROR_TYPE)

    # check_ip_flow() needs to be ran before running check_programflow() because check_ip_flow() sets DIE_LIST which is consumed by check_programflow()
    def check_ip_flows(self, programflow_path):
        die_list = []
        # for mtpl_file, script_file in self.mtpl_to_py.items():
        for mtpl_file in self.DIELET_PRIORITY:
            script_file = self.mtpl_to_py[mtpl_file]

            mtpl_file_path = os.path.join(programflow_path, mtpl_file)
            if os.path.exists(mtpl_file_path):
                print(f"Generating {mtpl_file}")

                # Backup the original .mtpl file
                backup_path = self.backup_file(mtpl_file_path)
                original_lines = File(mtpl_file_path).read()

                # Run the script to generate the new .mtpl file
                PyMtpl.run(os.path.join(programflow_path, script_file), self.tpobjfull.envfile)

                # Read the new .mtpl file
                new_lines = File(mtpl_file_path).read()

                # Compare the original and new .mtpl files using compare_files
                self.compare_files(mtpl_file, original_lines, new_lines)

                # Restore the original .mtpl file
                shutil.copy(backup_path, mtpl_file_path)
                os.remove(backup_path)

                # Update DIE_LIST
                ip = mtpl_file.split('_')[0]
                die_list.append(self.die_list_mapping.get(ip, ""))

        os.environ["DIE_LIST"] = ','.join(filter(None, die_list))
        print(f"DIE_LIST set to: {os.environ['DIE_LIST']}")

    # def check_programflow(self, tpldir, bom, env_path, mtpl_path):
    def check_programflow(self, programflow_path, sharedflow_path):
        # Backup the original .mtpl file
        mtpl_file_path = os.path.join(programflow_path, "ProgramFlows.mtpl")
        mtpl_backup_path = self.backup_file(mtpl_file_path)
        original_lines = File(mtpl_file_path).read()

        # Run the main ProgramFlows script located in the Shared folder
        PyMtpl.run(os.path.join(sharedflow_path, "ProgramFlows.py"), self.tpobjfull.envfile)

        # Read the new .mtpl file
        new_lines = File(mtpl_file_path).read()

        # Compare the original and new .mtpl files
        self.compare_files(basename(mtpl_file_path), original_lines, new_lines)

        # Restore the original file from the backup
        shutil.copy(mtpl_backup_path, mtpl_file_path)
        os.remove(mtpl_backup_path)

    def main(self):

        # This qgate is applicable only on PR. Ignore for tpbuild.
        if self.not_from_pr():     # pragma: no cover
            log.info(f'-i- {self.__class__.__name__} is skipped, not from PR.')
            return 1

        # use the complete tar file for this qgate, because of MV or SkipModule, the programflows is updated
        if not QGateBase.fulltpobj:
            self.add_error(270, self.ERROR_TYPE, f'complete_tp.tar.gz does not exist in {os.getcwd()}')
            return

        with Chdir(QGateBase.fulltpobj.tpldir):
            log.info(f'-i- fulltp (temp) cwd: {os.getcwd()}')

            self.tpobjfull = QGateBase.fulltpobj

            bom = self.tpobjfull.get_bom()
            tpldir = self.tpobjfull.tpldir
            env_path = self.tpobjfull.envfile
            mtpl_path = self.tpobjfull._final_mtpl

            programflow_path = f'{tpldir}/POR_TP/{bom}/ProgramFlowsTestPlan/'
            sharedflow_path = f'{tpldir}/Shared/POR_TP/{bom}/ProgramFlowsTestPlan/'

            # change to path because programflow scripts have relative paths
            with Chdir(programflow_path):
                self.check_ip_flows(programflow_path)
                self.check_programflow(programflow_path, sharedflow_path)


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    ProgramFlowChecker(TestProgram(sys.argv[1]), frompr=True).run()
