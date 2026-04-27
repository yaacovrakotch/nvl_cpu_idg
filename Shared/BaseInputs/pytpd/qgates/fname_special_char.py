#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Checks for special character name in tp filename
This qgate will review all the file path/names and see if the filenames do not have
weird characters in them
"""
import sys
import setenv

from gadget.disk import Allfiles, Chdir
from qgates.qgate_base import QGateBase
from gadget.tputil import get_modulename
from tp.testprogram import TestProgram
import re


class FnameSpecialChar(QGateBase):

    def main(self):
        """Entry point of checker"""
        fr = re.compile(r'[A-Za-z0-9\/\.\_\-\+]+')  # file spchar regex
        ubr = re.compile('UserCode.bin.(Release|Debug)')   # Ignore /UserCode/bin/Release/UpsEngine/.NETFramework,Version=v4.6.2.AssemblyAttri files
        with Chdir(self.tpobj.tpldir):
            for f in Allfiles('.'):
                if ubr.search(f):
                    continue
                mod = get_modulename(f)
                if mod is None:
                    mod = 'BASE'

                ff = fr.search(f)
                ffd = ff.group(0)
                if f != ffd:
                    self.add_error(194, mod, f'File: [{f}] has an invalid char in the name!')
                else:
                    self.add_pass(194, mod)


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    FnameSpecialChar(TestProgram(sys.argv[1]).pickle_init()).run()
