#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Ensure Subflow name is all capital case: Error 226.
Flow flag check for each subflow. If it doesn't exist or NOT place at first of subflow, the checker will error out with 227.
"""
import setenv      # must be first in the imports
from gadget.dictmore import xmlfunc, iter_dot_items, find_dot_items
from gadget.pylog import log
from gadget.tputil import remove_ip
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
from pprint import pprint
from xml.etree import cElementTree as ElementTree
from os.path import basename
import sys
import json


class FlwflagCheck(QGateBase):

    def main(self):
        tpobj = self.tpobj
        # below is all the "subflows" in the .mtpl, connected or unconnected
        all_subflow_list = tpobj.mtpl.get_subflows()      # {x for x in tpobj.mtpl._dutflow if '::' not in x}

        # iterator to all the connected flows. Add passonly=True to walk in passflow only
        all_items = tpobj.mtpl.iter_flows('MAIN', bypass=True, edict=True, traceinfo=True)
        allconnected = set()
        for module, testname, params, trc in all_items:
            subflow = all_subflow_list & set(trc)        # to filter only "subflows"
            if 'MAIN' in subflow:
                allconnected.update(subflow)

        # Capital case naming convention check for each subflow.
        case_chk = sorted(allconnected)
        for flwitem in case_chk:
            uppercase_chk1 = flwitem.rstrip("_SubFlow")
            uppercase_chk2 = uppercase_chk1.rstrip("_Subflow")
            uppercase_final = uppercase_chk2.isupper()
            if not uppercase_final:
                self.add_error(228, "BASE", f'{flwitem} name is NOT all capital case.')
            else:
                self.add_pass(228, "BASE")
        # Check if Flow Flag module is the first module of each subflow.
        tppath = tpobj.envdir
        # mtplpath = tppath + '\ProgramFlowsTestPlan\ProgramFlows.mtpl'
        mtplpath = self.tpobj.get_final_mtpl()
        found = 0
        with open(mtplpath, "r") as prgline:
            for prgpharse in prgline:
                if "DUTFlow " in prgpharse and ("_SubFlow" in prgpharse or "_Subflow" in prgpharse) and not ("}" in prgpharse or "#" in prgpharse) and not ("DEDC" in prgpharse):
                    subflow_name = prgpharse
                    found = 1
                if found == 1 and "DUTFlowItem " in prgpharse:
                    if "TPI_FLWFLGS" in prgpharse:
                        self.add_pass(227, "BASE")
                        found = 0
                    else:
                        self.add_error(227, "BASE", f'There is NO Flow "Flag Module" at the beginning of this {subflow_name}.')
                        found = 0


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    FlwflagCheck(TestProgram(sys.argv[1]).pickle_init()).run()
