#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Ensures that there are no Duplicate VARIABLE in env file
"""
import setenv      # must be first in the imports
import re
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


class DupEnvVar(QGateBase):

    def main(self):
        """
        This routine checks for duplicate env variable
        QE: 22016005321
        :return:
        """

        if not(self.tpobj.env.get_env_dict(stackval=True)):
            self.add_pass(206, 'Base')

        for item in self.tpobj.env.get_env_dict(stackval=True):
            if not(f'${item}' in self.tpobj.env.get_item(item)):
                self.add_error(206, 'Base', f'{item} is redefined in env. Cannot redefine.')
                continue   # ok usage of env_stacked
        return


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    DupEnvVar(TestProgram(sys.argv[1]).pickle_init()).run()
