#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""

Purpose of QGATE Check:
Ensures that module defined uservar files do not have a SelectorRuleCollection titled TpRule as that is restricted to base uservar file

Problem was found:
    Sent: Jan 28, 2023 9:25 PM
    Subject: LOAD_FAIL due to same module local TOS rule name vs. ready to release Base TOS rule name
    Description: A module used the same local TOS rule naming as BASE TP TOS rule naming (SelectorRuleCollection TpRule & SelectorRule If_COLD). Module should not use the same TOS rule name in SelectorRuleCollection & SelectorRule.

"""
import sys
import setenv

from gadget.dictmore import xmlfunc, iter_dot_items, find_dot_items
from gadget.pylog import log
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
from pprint import pprint
from xml.etree import cElementTree as ElementTree
from os.path import basename
import json
import os
from gadget.tputil import OtplFile
import re
from tp.testprogram import Env


class TpRuleUservar(QGateBase):

    def get_selectorvars(self):
        """
        Find all SelectorRuleCollection names found in the base inputs uservar file.
        These names should not be redefined in modules.
        Parse the base uservar file and create a list of uservar names that should not be used in module uservars.

        :return: list of SelectorRuleCollection names in the base uservar file
        """

        baserules = []
        tppath = self.tpobj.tpldir
        basevar = f'{tppath}/Shared/BaseInputs/UservarDefinitions.usrv'

        for lno, line in OtplFile(basevar).readline():
            if 'SelectorRuleCollection' in line:
                splitline = line.split(' ')
                rule = splitline[1]
                rule = rule.lower()
                if rule not in baserules:
                    baserules.append(rule)
        return baserules

    def check_if_error(self, baserules):
        """
        Using the list of SelectorRuleCollection variables provided, search all module uservar files and see if any redefine a base SelectorRuleCollection.
        Search through all uservar files in the Modules folder.
        Open the file if it is a uservar file.
        Check if there are any SelectorRuleCollection uservars defined as the same as a base uservar.
        Print the uservar file, line, and error if there is an error.

        any uservar files in the Modules folder are parsed

        :param baserules: list of SelectorRuleCollection variables in base input file
        """
        robj = re.compile(r"Modules.(\w+)")
        for usrvfile in self.tpobj.get_import_files('usrv'):
            res = robj.search(usrvfile)
            if res:
                modulename = res.group(1)
                for lno, line in OtplFile(usrvfile).readline():
                    if 'SelectorRuleCollection' in line:
                        fail = False
                        for rulecheck in baserules:
                            if rulecheck in line.lower():
                                msg = f'file {usrvfile}: line: {lno}, {line}, has {rulecheck} not allowed.'
                                self.add_error(232, modulename, msg)
                                fail = True

                        if not fail:
                            self.add_pass(232, modulename)

    def main(self):
        returned_var = self.get_selectorvars()
        self.check_if_error(returned_var)


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    TpRuleUservar(TestProgram(sys.argv[1]).pickle_init()).run()
