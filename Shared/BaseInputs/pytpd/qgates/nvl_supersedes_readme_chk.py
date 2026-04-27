#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Check if there are any DLL files in the BaseInputs/Common/Supersedes/code folder
under the test program shared directory.
No DLL files should be present in the BaseInputs/Common/Supersedes/code directory.
Link: https://wiki.ith.intel.com/display/ITSpdxtp/MTL+Module+Checkers

"""
import sys
import setenv

from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
import glob
import os


class SuperSedesReadmeChk(QGateBase):

    def main(self):
        """Entry point of checker"""

        # Get list of supersedes dll files
        dll_files = glob.glob(f'{self.tpobj.shareddir}/BaseInputs/Common/Supersedes/code/*.dll')
        dll_file_names = [os.path.basename(file) for file in dll_files]

        # Check maximum DLL count - No DLL files are allowed in the supersedes folder.
        max_count = 0
        dll_count = len(dll_file_names)
        self.check(dll_count <= max_count, 275, 'BASE',
                   f'Found {dll_count} supersede DLLs, but maximum allowed is {max_count}. '
                   f'No DLL supersedes are allowed; please remove all DLL files from '
                   f'/Shared/BaseInputs/Common/Supersedes/code/.')


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    SuperSedesReadmeChk(TestProgram(sys.argv[1])).run()
