#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
update_mtpl module - Rewrites the mtpl given data structure

# TODO: (Major, new class) TestUpdater
# TODO: Preserve line comments on DUTFlow
# TODO: Put back updated dictionary in tpobj after write()
"""
import re
from gadget.files import File
from gadget.errors import ErrorUser, confirm
from collections import OrderedDict
from copy import deepcopy
from pprint import pprint


class FlowUpdater:
    """
    This is a class to update one mtpl file for DUTFlow block

    Limitation: Cannot update ConcurrentFlow blocks (The structure is different / odd)
    """

    def __init__(self, tpobj, mtplfile, module):
        """

        :param tpobj: Testprogram object
        :param mtplfile: which .mtpl are we editing (module or programflows)
        :param module: The module testplan name or None for programflows
        """
        self.tpobj = tpobj
        self.module = module
        self.mtplfile = mtplfile
        self.dutflow = {}                      # {<composite|subflow>: {dict_of_dutflow_items} }
        self.dutflow_order = OrderedDict()     # ordered {<composite|subflow>: <type>}
        self.dutflow_at = self.tpobj.mtpl.get_dutflow_map(at=True)    # This is not a copy

        # Let's populate dutflow
        df = self.tpobj.mtpl.get_dutflow_map()
        for composite, value in df.items():
            if module:
                # this is a module
                if composite.startswith(f'{module}::'):
                    self.dutflow[composite] = deepcopy(value)
            else:
                # this is programflows
                if '::' not in composite:
                    self.dutflow[composite] = deepcopy(value)

        # Let's populate dutflow_order
        df_order = self.tpobj.mtpl.get_dutflow_map(order=True)
        for composite, value in df_order.items():
            if module:
                # this is a module
                if composite.startswith(f'{module}::'):
                    self.dutflow_order[composite] = deepcopy(value)
            else:
                # this is programflows
                if '::' not in composite:
                    self.dutflow_order[composite] = deepcopy(value)

    def _get_instances(self, allraw):
        """
        Get all lines until first DUTFlow or Flow
        :return: list of lines
        """
        # Write everything as-is until first DUTFlow or Flow
        final = []
        re_test = re.compile(r'^Test\s+\w+\s+\w+$')

        start = True
        for line in allraw:
            if line.strip().startswith(('DUTFlow ', 'Flow ')) or line.strip() == 'FlowDefs':
                start = False

            if re_test.search(line.strip()):
                start = True

            if start:
                final.append(line.rstrip())

        return final

    def update(self, dutflow, dfi, dict_update):
        """
        Update one flow item

        :param dutflow: The dutflow block
        :param dfi: The item
        :param dict_update: Dictionary (based of dutflow) on what we want to change
        :return:
        """
        if self.module:
            df = f'{self.module}::{dutflow}'     # module
        else:
            df = dutflow       # ProgramFlows
        confirm(df in self.dutflow,
                f'{df} does not exist.',
                f'Pls confirm that {df} exist first.')
        confirm(dfi in self.dutflow[df],
                f'{dfi} does not exist in {df}',
                'Pls confirm that this exist first.')

        self.dutflow[df][dfi].update(dict_update)

    def delete(self, dutflow, dfi, which_port=1):
        """
        Delete one flow item

        Limitation: Cannot leave the DutFlow block empty!
        Limitation: Cannot delete floating dutflowitem

        :param dutflow: The dutflow block
        :param dfi: The item
        :param which_port: Which port to goto after deletion. Default is 1
        :return:
        """
        if self.module:
            df = f'{self.module}::{dutflow}'     # module
        else:
            df = dutflow       # ProgramFlows
        confirm(df in self.dutflow,
                f'{df} does not exist.',
                f'Pls confirm that {df} exist first.')
        confirm(dfi in self.dutflow[df],
                f'{dfi} does not exist in {df}',
                'Pls confirm that this exist first.')

        # get the next instance
        prevgoto = None
        prevreturn = None
        if 'GoTo' in self.dutflow[df][dfi][which_port]:
            prevgoto = self.dutflow[df][dfi][which_port]['GoTo']
        if 'Return' in self.dutflow[df][dfi][which_port]:
            prevreturn = self.dutflow[df][dfi][which_port]['Return']

        # remove it from the order
        orderlist = self.dutflow[df]['_ORDER']
        idx = orderlist.index(dfi)     # This will raise exception if dutflowitem is "floating"
        del orderlist[idx]

        # Trying to delete first
        if idx == 0:
            confirm(prevgoto,
                    f'DUTFlowItem [{dfi}] does not have goto and it is the first in the DUTFlow',
                    f'Cannot have empty DUTFlow block. Pls make sure DUTFlow block has at least 1 item')
            del orderlist[orderlist.index(prevgoto)]
            orderlist.insert(0, prevgoto)
            return   # deletion is done, no other changes

        # next reroute the wire
        prev_dfi = orderlist[idx - 1]
        for target_port in self.dutflow[df][prev_dfi]:
            if ('GoTo' in self.dutflow[df][prev_dfi][target_port] and
                    self.dutflow[df][prev_dfi][target_port]['GoTo'] == dfi):
                if prevgoto:
                    self.dutflow[df][prev_dfi][target_port]['GoTo'] = prevgoto

                else:
                    confirm(prevreturn is not None,
                            f'DUTFlowItem [{dfi}] neither has goto or return',
                            'Is this possible?')
                    self.dutflow[df][prev_dfi][target_port]['Return'] = prevreturn
                    del self.dutflow[df][prev_dfi][target_port]['GoTo']

    def insert(self, dutflow, dfi, which_port, dfi_new, dfi_testname, dict_update):
        """
        Insert one flow item

        Assumption here is inserting in a flow where the source dfi GoTo is updated, no other changes in source dfi.
        If the bin or the counter needs to be updated, then need to call update() for it

        :param dutflow: The dutflow block where to insert from
        :param dfi: The dutflowitem to insert from, Specify None if start
        :param which_port: which port to insert from
        :param dfi_new: New dfi name
        :param dfi_testname: The testinstance name
        :param dict_update: port dictionary
        :return:
        """
        if self.module:
            df = f'{self.module}::{dutflow}'     # module
        else:
            df = dutflow                         # ProgramFlows

        # Checking
        confirm(df in self.dutflow,
                f'{df} does not exist.',
                f'Pls confirm that {df} exist first.')
        confirm(dfi_new not in self.dutflow[df],
                f'{dfi_new} is already existing',
                'Pls specify a DUTFlowItem name that is new / non-existent to insert()')
        if dfi:
            confirm(dfi in self.dutflow[df],
                    f'{dfi} does not exist in {df}',
                    'Pls confirm that this exist first.')
            confirm(which_port in self.dutflow[df][dfi],
                    f'port {which_port} does not exist in {df} block of {dfi}',
                    'Pls Add the port first if this port is non-existent.')

        prevgoto = None
        prevreturn = None
        if dfi:   # middle or end case
            # get the original value
            if 'GoTo' in self.dutflow[df][dfi][which_port]:
                prevgoto = self.dutflow[df][dfi][which_port]['GoTo']
            if 'Return' in self.dutflow[df][dfi][which_port]:
                prevreturn = self.dutflow[df][dfi][which_port]['Return']
                del self.dutflow[df][dfi][which_port]['Return']
            # update the source dfi
            self.dutflow[df][dfi][which_port]['GoTo'] = dfi_new

        else:    # begging of dutflow case
            prevgoto = self.dutflow[df]['_ORDER'][0]

        # update dict_update with the new connections
        for port in dict_update:
            if 'PREVIOUS' in dict_update[port]:
                del dict_update[port]['PREVIOUS']     # remove it
                if prevgoto is not None:
                    dict_update[port]['GoTo'] = prevgoto
                if prevreturn is not None:
                    dict_update[port]['Return'] = prevreturn

        # add the new dfi
        self.dutflow[df][dfi_new] = dict_update
        # Add the testinstance name
        self.dutflow[df][dfi_new][999] = dfi_testname

        # Add the order in the order
        orderlist = self.dutflow[df]['_ORDER']
        if dfi:
            orderlist.insert(orderlist.index(dfi) + 1, dfi_new)
        else:
            orderlist.insert(0, dfi_new)

    def write(self):
        """Rewrite the mtpl file"""
        allraw = File(self.mtplfile).raw()
        final = self._get_instances(allraw)

        # Write the DUTFlows
        for item in self.dutflow_order:
            item_name = item.split(':')[-1]
            ttype = self.dutflow_order[item]
            if ttype == 'ConcurrentFlow':
                continue     # ConcurrentFlow cannot be modified. The structure is different
            final.append(f'{ttype} {item_name}')
            final.append('{')
            for fitem in self.dutflow[item]['_ORDER']:
                final.extend(self._fitem_lines(item, fitem, ttype))

            final.append(f'}} # End of {ttype} {item}')
            final.append('')

        # Write it
        final.extend(self._get_remaining_lines(allraw))
        File(self.mtplfile).rewrite('\n'.join(final), 'FlowUpdater()')

    def _fitem_lines(self, item, fitem, ttype):
        """
        Iterator to return the one DUTFlowItem block
        """
        # get the @EDC, if exist
        at = ''
        if (item, fitem) in self.dutflow_at:
            at = f' {self.dutflow_at[(item, fitem)]}'

        ti = self.dutflow[item][fitem][999]
        if ttype == 'DUTFlow':
            yield f'    DUTFlowItem {fitem} {ti}{at}'
        else:
            yield f'    FlowItem {fitem} {ti}{at}'

        yield '    {'
        for port in sorted(self.dutflow[item][fitem]):
            if port == 999:
                continue
            yield f'        Result {port}'
            yield '        {'
            dip = self.dutflow[item][fitem][port]
            if 'PassFail' in dip:
                yield f'            Property PassFail = "{dip["PassFail"]}";'
            for kw in ('IncrementCounters', 'SetBin', 'Return', 'GoTo'):
                if kw in dip:
                    yield f'            {kw} {dip[kw]};'
            yield '        }'
        yield '    }'

    def _get_remaining_lines(self, allraw):
        """Iterator - return lines after FlowDefs"""
        start = False
        for line in allraw:
            if line.strip().startswith('FlowDefs'):
                start = True
            if start:
                yield line.rstrip()
