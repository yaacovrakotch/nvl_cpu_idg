#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
This script will run right after TPIE build to reorder <path>/pat/common dirs for subr correctness
"""
import setenv      # must be first in the imports
import glob
from gadget.errors import ErrorCheck
from gadget.files import File
from tp.testprogram import TestProgram
from mod.envreorder import EnvReorder
from gadget.tputil import CheckerLog
from os.path import exists


class TpPost:
    """
    Env patch reorder external wrapper for post TP builds
    """

    def __init__(self):
        self.envs = glob.glob('./EnvironmentFile*.env')

    def envreorder(self):
        """
        Function runs env patch reorder to account for common subr in MTL
        :return: None
        """
        for f in self.envs:
            t = TestProgram(f)
            EnvReorder(t).main(disp=False, update=True)

        return


if __name__ == '__main__':  # pragma: no cover
    CheckerLog.setup()
    obj = TpPost()
    obj.envreorder()
