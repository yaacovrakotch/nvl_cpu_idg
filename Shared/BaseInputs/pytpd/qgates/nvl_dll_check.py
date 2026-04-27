"""
QGate that checks dll folder and fails if too few.
This will catch problems associated to build or copy step failures.

The check performs the following:

1) Searches for files matching the glob pattern
   ``UserCode/lib/Release/net6.0/*.dll``.
2) Requires at least three DLL files to be present to avoid false passes
   from partial or failed builds that still produce a small number of DLLs.
3) Reports QGate result code 271, marking the QGate as pass when the
   requirement is met or error when it is not.
"""


import setenv
import sys
from gadget.pylog import log
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
import glob


class DllChecker(QGateBase):

    def main(self):
        dll_files = glob.glob('UserCode/lib/Release/net6.0/*.dll')
        dll_count = len(dll_files)
        if dll_count >= 3:
            log.info(f'-i- Found {dll_count} dll files in UserCode dir. DLL Check Passed.')
            self.add_pass(271, 'DLL Check passes')
        else:
            self.add_error(271, 'DLL Check Fail', f'No dll files found in the UserCode dir. Please re-run TPBuild to ensure fresh copy of the UserCode dir')


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    DllChecker(TestProgram(sys.argv[1]).pickle_init()).run()
