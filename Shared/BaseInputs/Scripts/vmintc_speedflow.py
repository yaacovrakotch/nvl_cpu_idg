#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Speedflow VminTC set in kill must have
   ForwardingMode = "InputOutput";
   and other required attributes
if not, vmin from this instance will not be accounted for in the vmin table

This is a request from BinSplit Team
"""
import sys
try:
    import setenv
except ImportError:    # pragma: no cover    - Used when local qgate .py is in tp area
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')

from gadget.dictmore import xmlfunc, iter_dot_items, find_dot_items
from gadget.pylog import log
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
from pprint import pprint
from xml.etree import cElementTree as ElementTree
from os.path import basename
import json
import re


class VminSpeedFlow(QGateBase):

    def main(self):
        """Entry point of checker"""

        # Iterate to all instances in the TP
        robj = re.compile('_\d\d\d\d$')    # speedflow testname always ends with 4 digits
        cobj = re.compile('.*_VMIN_K_C.*')    # Check flow will match this pattern, this is used for checking 'FlowIndexCallbackName'
        exclusion_list = ['_VMAX_','_MAXCR_','_MAXAT_','_MAXCLR_','_BEGSOC_','_ENDSOC_','LTTC','_VMIN_K_LTTC','_MAXCRLO_','_VCCR_F5_']
        all_instances = self.tpobj.mtpl.iter_flows('MAIN', bypass=True, edict=True, pdict=True)
        for module, testname, params, ports in all_instances:

            # Check only speedflow
            if not robj.search(testname):
                continue

            if any(exclusion in testname for exclusion in exclusion_list):
                continue    # ignore this because they are not using vmin data

            # Check only VminTC
            if params['TEMPLATE'] != 'VminTC':
                continue

            # Check only kill
            kill = False
            for port, values in ports.items():
                if port == -1 or port == -2 or port == 999:    # Ignore these: Alarms and special ports
                    continue
                if (ports[port]['PassFail']) == 'Fail' and 'SetBin' in values:   # it's a failport and a KILL
                    kill = True

            # Now check things if kill
            if kill:
                # ForwardingMode must be InputOutput
                fmode = params.get('ForwardingMode', 'NotDefined')
                if fmode != 'InputOutput':
                    self.add_error(123, module, f'{testname} has ForwardingMode {fmode}. Expecting InputOutput')   # This is how to specify error
                else:
                    self.add_pass(123, module)         # for every fail, there should be a pass counter to tell the check worked

                # FlowIndexCallbackName and CornerIdentifiers cannot be empty

                if params.get('CornerIdentifiers', 'NotDefined') in ('', 'NotDefined'):
                    self.add_error(124, module, f'{testname} has CornerIdentifiers empty.')   # This is how to specify error
                else:
                    self.add_pass(124, module)         # for every fail, there should be a pass counter to tell the check worked
                # FlowIndexCallbackName should be checked in CHK flow only
                if cobj.search(testname):
                    if params.get('FlowIndexCallbackName', 'NotDefined') in ('', 'NotDefined'):
                        self.add_error(125, module, f'{testname} has FlowIndexCallbackName empty.')   # This is how to specify error
                    else:
                        self.add_pass(125, module)         # for every fail, there should be a pass counter to tell the check worked

if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    VminSpeedFlow(TestProgram(sys.argv[1]).pickle_init()).run()
