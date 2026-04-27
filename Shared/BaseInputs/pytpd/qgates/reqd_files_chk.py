#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Ensures files that are required to load the TP exist
"""
import setenv      # must be first in the imports
import re
import os
from os.path import dirname, basename, exists
from gadget.dictmore import xmlfunc, iter_dot_items, find_dot_items
from gadget.pylog import log
from gadget.strmore import curtime, strvalue, truncate, to_str
from qgates.qgate_base import QGateBase
from gadget.tputil import remove_ip
from tp.testprogram import TestProgram
from pprint import pprint
from xml.etree import cElementTree as ElementTree
from os.path import basename
from mod.setting import cfg
import sys
import json
import glob


class ReqdFilesChk(QGateBase):

    def main(self):
        """
        This function checks for files that are required to load the TP and other DB related functionality
        :return:
        """
        # reqdfiles = ['*_TP/*/Reports/LTL_Files.zip', 'BaseTestPlan.tpl', 'Shared/Package_Shared/Package.imp'] Example
        reqdfiles = ['*_TP/*/Reports/LTL_Files.zip']  # Add more required files, comma separated
        for f in reqdfiles:
            if glob.glob(f'{self.tpobj.tpldir}/{f}'):
                self.add_pass(151, 'Base')
                continue
            else:
                self.add_error(151, 'Base', f'File:{f} is MISSING! HVM quality is compromised!')

        return


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    ReqdFilesChk(TestProgram(sys.argv[1]).pickle_init()).run()
