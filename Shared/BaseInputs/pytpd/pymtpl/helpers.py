"""
pymtpl helper classes and routines

# Initialize the module by defining the output mtpl path and the module name
Initialize('./ProgramFlowsNvlChassis', 'ProgramFlowsNvlChassis', tosversion="tos4")

program_flows = '''
START               TPI_FLWFLGS_XXX           r2p
START               TPI_BASE_XXX              r2p:TPI_PRESI_XXX  r3f
START               TPI_DFF_XXX               r2p                r3p
START               TPI_VCC_XXX               r2p
START               TPI_SHOPS_XXX             r2p
START               TPI_EDM_XXX               r2p
START               TPI_PWRUP_YXXK
START               FUS_FUSECFG_SXX
START               FUS_UNITINFO_SXX
START               TPI_PBMFC_YXX
START               TPI_GFXAGG_GXX            # The scope IP_PCH:: will be added automatically
START               TPI_END_XXX

SHAREDRAILSNOM      TPI_FLWFLGS_XXX           r2p
SHAREDRAILSNOM      TPI_BASE_XXX              r2p
'''

"""
from pymtpl.core import Flow, Fitem, Initialize, pPass, pFail, ModuleFlow, PyMtpl, required, Spec
from collections import OrderedDict, defaultdict
from gadget.tputil import remove_ip, OtplFile, JsonRead
from gadget.files import File
from gadget.errors import confirm, ErrorUser, Check
from gadget.gizmo import get_caller_lno
from pprint import pprint
from pathlib import Path
from gadget.helperclass import OPT, IS_UT
import re
from tp.testprogram import Env
from tp.testprogram import TestProgram
import os
import site
from os.path import isdir, dirname, exists
import inspect
from gadget.pylog import log


class ProgramFlows:
    """Create pymtpl objects for ProgramFlows.mtpl"""

    def __init__(self):
        self.topflow = None
        self.topdict = {}

    def _read_cfgtext(self, cfgtext):
        """
        Read the input text and put it in a data structure (ordered dict)

        :param cfgtext: Input text
        :return: {subflow: [(module, ports_list)]}
        """
        subflow_list = OrderedDict()
        for line in cfgtext.split('\n'):
            line = line.strip()
            if not line:  # empty line
                continue
            if line.startswith('#'):  # comment
                continue

            elems = line.split()  # <subflow> <module> <ports>
            subflow = elems[0]
            module = elems[1]
            ports = elems[2:]  # empty if no ports in the line

            if subflow not in subflow_list:
                subflow_list[subflow] = []  # initialize to a list

            subflow_list[subflow].append((module, ports))

        return subflow_list

    def main(self, cfgtext, topflow, ip=False):
        """
        Format:
           <subflow>           <module>                 <port> ...

        Example:
           START               TPI_FLWFLGS_XXX           r2p

        Syntax of the ports:
          r2p           - result 2,  pass, return 1 (default)
          r2p2          - result 2,  pass, return 2
          r2pm1         - result 2,  fail, return -1
          r2pn          - result 2,  fail, goto <next>
          rm1pn         - result -1, fail, goto <next>
          r2f:<modname> - result 2,  fail, goto <modname>

        Strategy: Specify the port and use Qgate to check if we miss a port.
        Reason: Script does not know what to do with the port
        Automatically write the IP, so below is just "module" name

        :param cfgtext: Input config text
        :param topflow: "MAIN" or "INIT"
        :param ip: Set to False for IP*.mtpl (IP will be auto written). Set to True for ProgramFlows (IP will not be auto written)
        :return:
        """
        self.topflow = topflow
        self.ip = ip

        # MAIN                START                     r6p2:ALARM
        subflow_list = self._read_cfgtext(cfgtext)  # {subflow: [(module, ports_list)]}

        # Create the pymtpl objects, from dictionary:
        #     START = [Fitem('TPI_FLWFLGS_XXX_START', ModuleFlow('TPI_FLWFLGS_XXX'), r0=pFail(), r2=pPass()),
        #              Fitem('TPI_BASE_XXX_START',  ModuleFlow('TPI_BASE_XXX'),  r0=pFail(), r2=pPass()),
        #              Fitem('TPI_PWRUP_DCYXXK_START',  ModuleFlow('TPI_DFF_XXX'),  r0=pFail())]
        #     START_SubFlow = Flow('START_SubFlow', START)
        subflowdict = {}
        subflowport = OrderedDict()  # {subflow: {port: pPass|pFail}}
        robj = re.compile(r'^(r\d+|rm\d+)([pfx])(n|m\d+|\d+)?(:\S+)?')
        mainport = OrderedDict()
        maindefault = {'r0': pFail(ret=0)}  # default for MAIN
        for subflow in subflow_list:
            subflows = []
            subflowport[subflow] = {}
            name_wo_subflow = subflow.replace('_SubFlow', '').replace('_TopFlow', '')

            # set defaults
            if subflow == self.topflow:
                defaults = {'r0': pFail(ret=0)}
            else:
                defaults = {'rm2': pFail(ret=-2),
                            'rm1': pFail(ret=-1),
                            'r0': pFail(ret=0)}

            for module_encoded, port_list in subflow_list[subflow]:
                module = module_encoded[1:] if module_encoded.startswith('$') else module_encoded

                if module == 'DEFAULTS':  # This must be first in definition
                    kwports = {'r0': pFail(ret=0)}  # This always exist, but can be overridden
                else:
                    kwports = dict(defaults)  # make a copy

                for port in port_list:
                    res = robj.search(port)
                    confirm(res,
                            f'port [{port}] in {subflow} {module} is invalid',
                            'Valid syntax: r2p r2pn r2f2 r2f2:<mod>')

                    result_n = res.group(1)
                    passfail = res.group(2)
                    return_n = res.group(3)
                    return_n = return_n.replace('m', '-') if return_n else return_n
                    modx = res.group(4)

                    if passfail == 'p':
                        portobj = pPass
                        portret = '1'
                    elif passfail == 'x':
                        if result_n in kwports:
                            del kwports[result_n]
                        continue
                    else:
                        portobj = pFail
                        portret = '0'

                    nn = return_n if return_n else portret
                    if modx:  # goto is specified
                        modgname = modx[1:].split(":")[-1]
                        if subflow == self.topflow:
                            modgoto = f'{modgname}'
                        else:
                            modgoto = f'{modgname}_{name_wo_subflow}'
                        kwports[result_n] = portobj(goto=modgoto)
                    elif nn == 'n':
                        kwports[result_n] = portobj(goto='NEXT')
                    else:
                        kwports[result_n] = portobj(ret=nn)
                        if nn != '1':
                            subflowport[subflow][f'r{nn.replace("-", "m")}'] = portobj(ret=portret)

                if self.ip:
                    ipstr = '~'  # ip programflows
                else:
                    ipstr = ''  # programflows

                # assign the ports
                if module == 'DEFAULTS' and subflow == self.topflow:
                    defaults = kwports
                    maindefault = defaults
                elif module == 'DEFAULTS' and subflow != self.topflow:
                    defaults = kwports
                elif subflow == self.topflow:
                    mainport[module] = kwports
                elif subflow.endswith('_TopFlow') or module.endswith('_SubFlow'):
                    # Parse module for optional :SUFFIX notation to override flow item name suffix
                    # Only apply custom suffix if single colon exists and no double colon (::) is present
                    if '::' not in module and ':' in module:
                        # Custom suffix specified with single colon (e.g., TPI_FLWFLGS_XXX:BEGIN)
                        module_base, custom_suffix = module.rsplit(':', 1)
                        dfi = f'{module_base.split(":")[-1]}_{custom_suffix}'
                        module_for_flow = module_base  # Use base module without custom suffix for flow reference
                    else:
                        # No custom suffix or has IP scope (::), use default behavior (subflow name as suffix)
                        dfi = f'{module.split(":")[-1]}_{name_wo_subflow}'
                        module_for_flow = module
                    subflows.append(Fitem(dfi, ModuleFlow(f'{ipstr}${module_for_flow}'), **kwports))
                else:  # Normal Module
                    # Parse module for optional :SUFFIX notation to override flow item name suffix
                    # Only apply custom suffix if single colon exists and no double colon (::) is present
                    if '::' not in module and ':' in module:
                        # Custom suffix specified with single colon (e.g., TPI_FLWFLGS_XXX:BEGIN)
                        module_base, custom_suffix = module.rsplit(':', 1)
                        dfi = f'{module_base.split(":")[-1]}_{custom_suffix}'
                        # Use base module without custom suffix for flow reference, preserving $ prefix if present
                        if module_encoded.startswith('$'):
                            module_encoded_for_flow = '$' + module_base
                        else:
                            module_encoded_for_flow = module_base
                    else:
                        # No custom suffix or has IP scope (::), use default behavior (subflow name as suffix)
                        dfi = f'{module.split(":")[-1]}_{name_wo_subflow}'
                        module_encoded_for_flow = module_encoded
                    subflows.append(Fitem(dfi, ModuleFlow(f'{ipstr}{module_encoded_for_flow}'), **kwports))

            if subflow != self.topflow:
                subflowdict[subflow] = Flow(f'{subflow}', subflows)

        # Create the DUTFlow MAIN
        self._mainflow(subflowport, subflowdict, mainport, maindefault)

    def _mainflow(self, subflowport, subflowdict, mainport, maindefault):
        """
        Creates the DUTFlow MAIN

        :param subflowport: {subflow: {port: pPass|pFail}}
        :param subflowdict: {subflow: Flow()}
        :param mainport: {subflow: pPass|Fail}
        :param maindefault: {port: pPass|pFail}
        :return: None
        """
        # Add all the subflows in MAINFLOW:
        #     MAINFLOW = [Fitem('START_SubFlow', START_SubFlow, r0=pFail()),
        #                 Fitem('SHAREDRAILSNOM_SubFlow', SHAREDRAILSNOM_SubFlow, r0=pFail()),
        #                 Fitem('PREPRL0_SubFlow', PREPRL0_SubFlow, r0=pFail())]
        #     Flow('MAIN', MAINFLOW)
        flows = []
        for subflow in mainport:
            kwports = mainport[subflow]

            # This is a normal subflow
            if subflow in subflowport:
                for port in subflowport[subflow]:
                    if port not in kwports:
                        kwports[port] = subflowport[subflow][port]
                flows.append(Fitem(subflow, subflowdict[subflow], **kwports))

            # This is direct module call
            elif '::' in subflow:
                sname = subflow.split(':')[-1]
                flows.append(Fitem(sname, ModuleFlow(subflow), **kwports))

            # This is parallel flow
            else:
                flows.append(Fitem(subflow, ModuleFlow(f'${subflow}'), **kwports))

        if flows:
            Flow(self.topflow, flows)


class ValidationMtplConvert:  # pragma: no cover
    """
    Validation Code to convert ProgramFlows.mtpl into pymtpl format

    # Caller Code. Copy {root} to /tmp first then cd to /tmp/<dir>
    root = '/nfs/site/disks/mve_mig_001/tpvalidation/hdmxprogs/arl/ARLXXXXXXX75Y6DSXXX'
    env = f'{root}/POR_TP/Class_ARL_U28/EnvironmentFile.env'
    mtpl = f'{root}/POR_TP/Class_ARL_U28/ProgramFlowsTestPlan/ProgramFlows.mtpl'
    outpy = 'POR_TP/Class_ARL_U28/programflows.py'
    ValidationMtplConvert().main(env=env, mtpl=mtpl, outpy=outpy)

    # The gold file must be OtplFile.reformat()

    # To get the MAIN block only
    tp_grep.py 'DUTFlow MAIN' POR_TP/Class_ARL_U28/programflows.mtpl -block > POR_TP/Class_ARL_U28/programflows.mtpl.MAIN
    """

    def __init__(self, is_main=False):
        self.is_main = is_main

    def main(self, env, mtpl, outpy):
        """
        Main entry point

        :param env: Path to env file
        :param mtpl: Path to programflows.mtpl
        :param outpy: Path to output .py file
        :return:
        """
        from tp.testprogram import TestProgram
        from gadget.helperclass import OPT

        # initialize
        tp = TestProgram(env)
        outfile = outpy.replace('.py', '')
        lines = []

        # write the pymtpl file
        lines.append("text = '''")
        for line in self.to_pymtpl(tp, mtpl):
            lines.append(line)
        lines.append("'''")
        lines.append('from pymtpl.helpers import ProgramFlows')
        lines.append('from pymtpl.core import Initialize')
        lines.append(f"Initialize('{outfile}', 'Flows')")
        lines.append("ProgramFlows().main(text, 'MAIN')")

        File(outpy).rewrite('\n'.join(lines), 'main')

        # call pymtpl
        OPT.all = [outpy]
        PyMtpl().main()

        # strip no lines so we can easily diff
        self.no_empty_lines(outpy.replace('.py', '.mtpl'))

        # tkdiff programflows_gold.mtpl POR_TP/Class_ARL_U28/programflows.mtpl

    def to_pymtpl(self, tpobj, mtplfile):
        """Iterator: Convert the mtplfile to pymtpl format"""
        tpobj.mtpl.init_dutflow()
        tpobj.mtpl._read_mtpl_flow(mtplfile)
        dm = tpobj.mtpl.get_dutflow_map()

        # Get the correct order of DUTFlows
        order = []
        # if self.is_main:
        #     for line in OtplFile(mtplfile).get_block('DUTFlow', 'MAIN'):
        #         if line.strip().startswith('DUTFlowItem') and '::' not in line:
        #             elem = line.split()
        #             if elem[2] not in order:
        #                 order.append(elem[2])
        #     order.append('MAIN')

        # normal dutflows
        for lno, line in OtplFile(mtplfile).readline():
            if line.startswith('DUTFlow '):
                elem = line.split()
                order.append(elem[1])
        # pprint(order)

        # print one block at a time
        for subflow_key in order:
            subflow = subflow_key.replace('_SubFlow', '').replace('_Subflow', '')
            for idx in range(len(dm[subflow_key]['_ORDER'])):
                module_item = dm[subflow_key]['_ORDER'][idx]

                if idx + 1 == len(dm[subflow_key]['_ORDER']):
                    next_item = ""
                else:
                    next_item = dm[subflow_key]['_ORDER'][idx + 1]

                if subflow_key == 'MAIN':
                    module = module_item.replace(f'_SubFlow', '')
                else:
                    module = module_item.replace(f'_{subflow}', '')

                portstring = []
                for port in sorted(dm[subflow_key][module_item]):
                    if port == 999:
                        continue

                    dp = dm[subflow_key][module_item][port]
                    portnum = str(port).replace('-', 'm')
                    if 'PassFail' not in dp:
                        continue  # ConcurrentFlow
                    pf = dp['PassFail'][0].lower()

                    # Last element
                    laste = ''
                    if 'GoTo' in dp:
                        if dp['GoTo'] == next_item:
                            laste = 'n'
                        else:
                            if subflow_key == 'MAIN':
                                laste = ':%s' % dp['GoTo'].replace(f'_SubFlow', '')
                            else:
                                laste = ':%s' % dp['GoTo'].replace(f'_{subflow}', '')

                    if 'Return' in dp:
                        laste = dp['Return'].replace('-', 'm')

                    # port encoding
                    encoding = f'r{portnum}{pf}{laste}'
                    if encoding in ['r1pn']:
                        portstring.append('')
                    elif encoding == 'r1p1' and next_item == '':
                        portstring.append('')
                    else:
                        portstring.append(encoding)

                # return the line
                ports = ' '.join(f'{x:6}' for x in portstring)
                yield f'{subflow:13}  {module:19}  {ports}'

            yield ''

    def no_empty_lines(self, fname):
        """Remove empty lines and comments for easy diffing"""
        raw = File(fname).raw()
        final = []
        robj = re.compile(r'^(\s*})\s+#')
        for line in raw:
            if not line.strip():
                continue
            res = robj.search(line)
            if res:
                final.append(f'{res.group(1)}\n')
                continue
            final.append(line)

        File(fname).rewrite(''.join(final), 'main')


class Compact:
    """
    For use in unittests, make the output more compact so it's easy for asserts.

    Usage: self.assertEqual(str(Compact(file)), expect)
    """

    def __init__(self, filename):
        self.filename = filename

    def __repr__(self):
        """Return str representation of object"""
        return '\n'.join(self._compact())

    def _compact(self):
        """
        Iterator: a compacted mtpl text for unittest expect
        """
        lines = list(File(self.filename).chomp())
        lines.append('')  # because of nline
        stack = []
        indent = ''
        for idx in range(len(lines) - 1):
            line = lines[idx].strip()
            nline = lines[idx + 1].strip()

            if not line:
                pass  # skip empty

            elif line.startswith('Result '):
                stack.append(f'{indent}{lines[idx].lstrip()}')
            elif stack and line == '{':
                stack.append(line)
            elif stack and line.startswith(('Property ', 'Return ', 'GoTo ')):
                stack.append(line)
            elif stack and line == '}':
                stack.append(line)
                yield ' '.join(stack)
                stack = []

            elif nline == '{':
                yield f'{indent}{lines[idx].lstrip()} {{'
                indent = f'{indent} '
            elif line == '{':
                pass
            elif line == '}':
                indent = indent[:-1]
                yield f'{indent}{lines[idx].lstrip()}'

            else:
                yield f'{indent}{lines[idx].lstrip()}'


class NVLProgramFlows:
    PORT_DEF = {'CPU': '[-2:-1],  IPC',
                'HUB': '[-2:-1],  IPH',
                'GCD': '[-2:-1],  IPG',
                'PCD': '[-2:-1],  IPP'}

    PORT0_DEF = {'CPU': '0,  IPC',
                 'HUB': '0,  IPH',
                 'GCD': '0,  IPG',
                 'PCD': '0,  IPP'}

    FAIL_DEF = {'CPU': '20,  IPC',
                'HUB': '40,  IPH',
                'GCD': '30,  IPG',
                'PCD': '50,  IPP'}

    PASS_DEF = {'CPU': '1',
                'HUB': '1',
                'GCD': '1',
                'PCD': '1'}

    DIE_TO_IP_MAP = {'CPU': 'IPC',
                     'HUB': 'IPH',
                     'GCD': 'IPG',
                     'PCD': 'IPP'}

    PRIORITY = ['CPU', 'HUB', 'GCD', 'PCD']

    @classmethod
    def get_flow_params(cls, dc, templatename):
        """
        output:
                IPC=f'IPC_FLOWS::{cpu_name}',
                IPH=f'IPH_FLOWS::{hub_name}',
                IPG=f'IPG_FLOWS::{gcd_name}',
                IPP=f'IPP_FLOWS::{pcd_name}',
                result=['IPC, IPH, IPG, IPP, EffectiveIPResult',
                       '1, *, *, *, IPC',
                       '[*:0], *, *, *,  IPH',
                       '1, [*:0], *, *,  IPG',
                       '[2:*], *, *, *,  IPP']

        ConcurrentFlow PRL0CPUIOE_SubFlow [Parallel]
        {
            ConcurrentFlowItem    IP_CPU    IP_CPU_CONCURRENT_FLOWS::PRL0CPUIOE_IP_CPU_FLOW_SubFlow;
            ConcurrentFlowItem    IP_PCH    IP_PCH_CONCURRENT_FLOWS::PRL0CPUIOE_IP_PCH_FLOW_SubFlow;
            ConcurrentResultTable (IP_CPU, IP_PCH, EffectiveIPResult)
            {

                1, *, IP_PCH;
                [*:0], *, IP_CPU;
                [2:*], *, IP_CPU;
            }
        }
        :param dc: list of die_combo: ['CPU', 'GCD']
        :param templatename: IP subflow name
        :return: dictionary for use in ConCurrentFlow()
        """
        result_rows = []
        result_dict = {}

        # Determine the column name list
        selected_columns = []
        for key in dc:
            _, col = [x.strip() for x in cls.PORT_DEF[key].split(',')]
            selected_columns.append(col)
            result_dict[col] = f'{col}_FLOWS::{templatename % key}'

        # PORT_DEF: Based on colum name list to build result rows
        for key in dc:
            cond_str, col = [x.strip() for x in cls.PORT_DEF[key].split(',')]
            row = {c: '*' for c in selected_columns}
            row[col] = cond_str
            row['Result'] = col
            result_rows.append(row)

        # PORT0_DEF: Based on colum name list to build result rows
        for key in dc:
            cond_str, col = [x.strip() for x in cls.PORT0_DEF[key].split(',')]
            row = {c: '*' for c in selected_columns}
            row[col] = cond_str
            row['Result'] = col
            result_rows.append(row)

        # FAIL_DEF: Based on colum name list to build result rows
        for key in dc:
            cond_str, col = [x.strip() for x in cls.FAIL_DEF[key].split(',')]
            row = {c: '*' for c in selected_columns}
            row[col] = cond_str
            row['Result'] = col
            result_rows.append(row)

        # Add pass control row
        for key in cls.PRIORITY:
            if key in dc:
                fallback_col = cls.DIE_TO_IP_MAP[key]
                fallback_cond = cls.PASS_DEF[key]
                row = {c: '1' for c in selected_columns}
                row[fallback_col] = fallback_cond
                row['Result'] = fallback_col
                result_rows.append(row)
                break

        # Build final result list
        header = ', '.join(selected_columns + ['EffectiveIPResult'])
        result_lines = [header]
        for row in result_rows:
            line = ', '.join(row[col] for col in selected_columns) + f",  {row['Result']}"
            result_lines.append(line)

        result_dict['result'] = result_lines
        return result_dict

    @classmethod
    def get_subflow_name(cls, die_combo, templatename):
        """
        Return the name of the subflow for one die
        :param die_combo: ['GCD']
        :param templatename: templatestring (with %s)
        :return: f'{templateCPU}_SubFlow'
        """
        confirm(len(die_combo) == 1, 'Expecting one die_combo only for get_subflow_name()', 'Pls fix code')
        mapdd = {'CPU': templatename % 'CPU',
                 'GCD': templatename % 'GCD',
                 'HUB': templatename % 'HUB',
                 'PCD': templatename % 'PCD'}
        confirm(die_combo[0] in mapdd,
                f'Expecting IP scope, valid values={",".join(mapdd)}. Input={die_combo[0]}',
                f'Pls fix mapdd in get_subflow_name() if {die_combo[0]} is valid.')
        return mapdd[die_combo[0]]

    @classmethod
    def get_module_flow_name(cls, die_combo, templatename):
        """
        :param die_combo: ['CPU']
        :param templatename: templatestring (with %s)
        :return: IPC::IPC_FLOWS::BEGINCPU
        """
        confirm(len(die_combo) == 1, 'Expecting one die_combo only for get_module_flow_name()', 'Pls fix code')
        mapdd = {'CPU': templatename % 'CPU',
                 'GCD': templatename % 'GCD',
                 'HUB': templatename % 'HUB',
                 'PCD': templatename % 'PCD'}
        mapip = {'CPU': 'IPC',
                 'GCD': 'IPG',
                 'HUB': 'IPH',
                 'PCD': 'IPP',
                 }
        confirm(die_combo[0] in mapdd,
                f'Expecting IP scope, valid values={",".join(mapdd)}. Input={die_combo[0]}',
                f'Pls fix mapdd and mapip in get_module_flow_name() if {die_combo[0]} is valid.')

        ipname = mapip[die_combo[0]]
        return f'{ipname}::{ipname}_FLOWS::{mapdd[die_combo[0]]}'

    @classmethod
    def strip_dielets(cls, main_code, die_list):
        """
        Updates main_code to be dielet if die_list is subset
        The strategy here is: main_code is FULL TP flow (Row11 in blueprint), so we need this routine to reduce it
        to dielet if die_list is not-full-tp

        :param main_code: lines of programflows
        :param die_list: list of die (CPU,GCD,HUB,PCD)
        :return:
        """
        if len(die_list) == 4:  # Nothing to reduce
            return main_code

        # get all FULLTPONLY first
        fulltponly = ['_MARKERONLY_']
        for item in re.findall(r'^#\s+FULLTPONLY:\s+(\w+)', main_code, re.MULTILINE):
            fulltponly.append(item)

        alldie = 'CPU GCD HUB PCD'.split()
        delete_die = set(alldie) - set(die_list)
        robj = re.compile(r'^(\w{1,20})(%s)' % '|'.join(alldie))

        # Need to strip out dielet modules based on "FF_" because these don't exist in dielet TP. Example:
        # HUBIPFF_SubFlow               DRV_RESET_HXX        rm2fm2 rm1fm1 r0f0
        robjf = re.compile(r'^(%s)(\w{0,5}FF_\w{1,20})' % '|'.join(alldie))  #

        final = []
        replace = []
        for line in main_code.split('\n'):
            if line.strip():  # ignore empty lines
                elems = line.split()
                res1 = robj.search(elems[0])  # regex on the first element
                res1f = robjf.search(elems[0])  # regex on the first element in failflow
                res2 = robj.search(elems[1])  # regex on the second element
                res2ff = robjf.search(elems[1])  # regex on the second element in failflow
                res2f = elems[1]  # second element: modulename or subflow

                # check if second element starts with fulltponly modules
                if re.search('^(%s)' % '|'.join(fulltponly), res2f):
                    continue  # this module is not allowed in dielet programflows

                elif res1:  # .*CPU|GCD|HUB|PCD is found in the first element name
                    founddie1 = res1.group(2)
                    if founddie1 in delete_die:
                        continue  # do not write this line

                elif res1f:  # ^(CPU|GCD|HUB|PCD).*FF_ is found in the first element name
                    founddie1f = res1f.group(1)
                    if founddie1f in delete_die:
                        continue  # do not write this line

                elif res2:  # .*CPU|GCD|HUB|PCD is found in the second element name
                    # Note: There is no situation where CPU is in first element and GPU is in second element (does not make sense)
                    founddie2 = res2.group(2)
                    if founddie2 in delete_die:
                        continue  # do not write this line

                elif res2ff:  # ^(CPU|GCD|HUB|PCD).*FF_ is found in second element name
                    founddie2f = res2ff.group(1)
                    if founddie2f in delete_die:
                        replace.append(elems[1])
                        continue  # do not write this line

            final.append(line)

        final = '\n'.join(final)
        # Replace the strip out Failflow goto port to always existing Final subflow.
        replace_subflw = 'FINAL_SubFlow'
        for ffsubflw in replace:
            final = final.replace(ffsubflw, replace_subflw)
        return final

    @classmethod
    def ignore_emptycomp(cls, comp_name, die_combo):
        """
        Feature for NVL Programflow disagg.
        Detect if importing composite (comp_name) is empty or start with "###".
        This routie remove the target composit from a certain block (ignore_sect).

        Example:
        comp_name = 'INITCPUPKG_SubFlow'
        die_combo = 'CPU'

        This routine will Remove the line below from ignore_sect (aka, TopFlow)
        INIT         INITCPUPKG_SubFlow    {init_stdports}
        """
        keywords = []
        comp_name = comp_name.strip().splitlines()

        # Get the first element, called keyword of the line, for use in next section. Example below, get INITCPUPKG_SubFlow
        # ###INITCPUPKG_SubFlow Your_Module_Name::Your_Module_Name_INIT {init_stdports}
        for die in die_combo:
            regex = re.compile(rf'^###\S*{die}\S*')
            for line in comp_name:
                first_element = line.split()[0] if line.split() else ''
                if regex.match(first_element):
                    stripped = first_element[3:] if first_element.startswith('###') else first_element
                    keywords.append(stripped)

        # Strip out lines which match keywords in the TopFlow
        update_init_flow = []
        for line in comp_name:
            split_line = line.strip().split()
            if len(split_line) >= 2 and split_line[1] in keywords:
                continue
            update_init_flow.append(line)

        return '\n'.join(update_init_flow)


def getvalidboms(name):
    """
    Return valid boms by reading Shared/BaseInputs/Inputs/bom_to_category.json given category name

    :param name: category name
    :return:
    """
    confirm(OPT.env,
            'Env file not found when running Pymtpl',
            'Pls specify the env command for Pymtpl or reach out to the TPI team to get help.')

    envfile = OPT.env
    tpobj = TestProgram(envfile)

    json_file_path = os.path.join(tpobj.tpldir, 'Shared/BaseInputs/Inputs/bom_to_category.json')

    confirm(exists(json_file_path),
            "BOMMapping file not found so EvalValidBoms cannot be used.",
            ('Pls contact the TPI team to setup the BOMMapping file or define the list of boms manually '
             'in the form of MConfig(plistinfo = {"sample.plist": ["BOM1", "BOM2", "BOM3"]})'))

    bommap_json = JsonRead(json_file_path,
                           suggestion=f"Pls contact the TPI team to fix the BOMMapping json file and try again.").load()

    confirm(name in bommap_json,
            f"EvalValidBoms name {name} not found in BOMMapping file",
            f"Valid names are {list(bommap_json.keys())}")

    return bommap_json[name]


def get_bin_limits_from_json(module_name):
    """
    Reads the module_name.BinLimits.json file for the specified module and returns bin ranges as a list of tuples.

    Args:
        module_name (str): Name of the module (e.g., "MIO_DDR") to be concatenated with .BinLimits.json and looked for in the current directory (e.g., Modules\\MIO_DDR\\MIO_DDR.BinLimits.json).
        The json file should contain a key "BinLimits" with a list of 3-4 integer [min, max] bin ranges, for instance:
        {
            "BinLimits": [
                [9825, 9850],
                [ 900,  999],
                [6800, 6899]
            ]
        }
        These ranges are the middle 4 digits of the 8 digit bin. 909825xx
        These allow bins in the range of 90982500 to 90985099, 90090000 to 90099999, and 90680000 to 90689999.
        Any keys other than BinLimits in the json file will be ignored and can be used for comments or other purposes.
        Module owners are expected to create this optional file in their module's directory.

        For more information, see https://github.com/intel-innersource/applications.manufacturing.intel.mpe.mdcx.extra-torch-tools#binlimitsjson

    Raises:
        ErrorUser: If the JSON file does not exist, is empty, or does not contain the expected structure.
        Check: If the bin ranges are not formatted correctly or contain invalid values.

    Returns:
        list: A list of tuples where each tuple contains (start_bin, end_bin)
    """
    # Construct the path to the JSON file
    json_file_path = os.path.join(os.getcwd(), f"{module_name}.BinLimits.json")
    alternate_json_file_path = os.path.join(os.getcwd(), f".BinLimits.json")

    # Use alternate path if primary does not exist
    if not exists(json_file_path) and exists(alternate_json_file_path):
        json_file_path = alternate_json_file_path

    # Check if file exists
    confirm(exists(json_file_path),
            f"Bin Limits file not found at {json_file_path}",
            'Please verify that your bin limits file is in the right location and named correctly (MODULE_NAME.BinLimits.json or .BinLimits.json).')

    # Read the JSON file
    bin_data = JsonRead(json_file_path, suggestion=f"Please check json file structure {json_file_path}").load()

    # make sure bin limits is there
    confirm("BinLimits" in bin_data,
            f"BinLimits key not found in {json_file_path}",
            'Please check the structure of your BinLimits JSON file.')

    # make sure they aren't empty
    confirm(len(bin_data) > 0,
            f"BinLimits in {json_file_path} is empty",
            'Please ensure that the BinLimits JSON file contains valid data.')

    # Extract bin limits and convert to list of tuples
    bin_limits = []
    for bin_range in bin_data["BinLimits"]:
        # make sure they're tuples with exactly two elements
        confirm(len(bin_range) == 2,
                f"Invalid bin range format in {json_file_path}: {bin_range}",
                'Each bin range should be a list with exactly two elements: [start_bin, end_bin].')
        # create tuple
        start_bin, end_bin = bin_range

        # confirm that start_bin and end_bin are integers
        confirm(isinstance(start_bin, int) and isinstance(end_bin, int),
                f"Invalid bin range values in {json_file_path}: {bin_range}",
                'Both start_bin and end_bin should be integers.')

        confirm(start_bin >= 0 and end_bin >= 0,
                f"Invalid bin range values in {json_file_path}: {bin_range}",
                'Both start_bin and end_bin should be non-negative integers.')

        confirm(start_bin <= end_bin,
                f"Invalid bin range in {json_file_path}: start_bin ({start_bin}) must be less than or equal to end_bin ({end_bin})",
                'Please check the bin limits for correctness.')

        bin_limits.append((int(start_bin), int(end_bin)))

    return bin_limits


def create_test_instance_with_defaults(testmethod=None, defaults=None, **kwargs):
    """
    Create a test instance of type testmethod with default parameters overridden by kwargs.

    Example Usage using functools.partial:
        from functools import partial
        from pymtpl.helpers import create_test_instance_with_defaults
        from por_methods import MyTestMethod
        MyTest = partial(create_test_instance_with_defaults, testmethod=MyTestMethod, defaults={'param1': 'default1'})
        MyTest(param2='value2', param3='value3')  # This will create an instance of MyTestMethod with param1='default1', param2='value2', param3='value3'

    :param testmethod: Test instance to be updated with defaults
    :param defaults: Dictionary of default parameters to be applied to the test instance
    :param kwargs: Additional keyword arguments to override defaults
    :return: Updated test instance
    """

    id_lno = get_caller_lno()

    confirm(testmethod is not None,
            f'Error, testmethod is None on line {id_lno}',
            f'Pls provide a valid testmethod to create an instance.')

    # Ensure testmethod is a class type
    confirm(isinstance(testmethod, type),
            f'Error, testmethod must be a class on line {id_lno}',
            f'Pls provide a class to create an instance.')

    # Avoid mutable default argument
    if defaults is None:
        defaults = {}
    confirm(isinstance(defaults, dict),
            f'defaults must be a dict, got {type(defaults)}',
            'Pls provide defaults as a dictionary.')

    # Do not mutate input dict; create a new one by combining defaults and kwargs with kwargs taking precedence
    params = {**defaults, **kwargs}

    # Ensure we include the required parameters
    required_params = _get_required_params(testmethod)
    missing = [param for param in required_params if param not in params]
    confirm(not missing,
            f'Missing required parameter(s): {missing} for {testmethod.__name__} on line {id_lno}',
            f'Pls provide all required parameters to create the test instance of {testmethod.__name__}.')

    # Create and return the test instance
    return testmethod(**params)


def _get_required_params(testmethod):
    """ Get the required parameters for a test method. """
    sig = inspect.signature(testmethod.__init__)
    required_params = []
    for name, param in sig.parameters.items():
        # Skip 'self'
        if name == 'self':
            continue
        # Required if no default value
        if param.default is inspect.Parameter.empty:
            required_params.append(name)
        # Also treat 'required' sentinel as required
        elif param.default == required:  # If you use a sentinel named 'required'
            required_params.append(name)
    return required_params


class InputFilePathOptions:
    """
    Options for inputfile() function

    Attributes:
        USE_SPEC = True
            True = Whether to wrap the path in Spec(), to directly write a string without quotes
            Default is True because we're using GetEnvironmentVariable("~HDMT_TP_BASE_DIR") which needs Spec()
        OVERRIDE_INPUTFILE_PATH = None
            If set, this path will be used directly, instead of the default input files path
            e.g. "/Shared/Modules/TPI/TPI_BASE_XXX/InputFiles"
        JOINING_OPERATOR = '/'
            The operator to use when joining the base path and the file path in inputfile()
            e.g. ' + "' to add a concatenation
            Odd-numbered " are automatically closed at the end of the path
    """
    USE_SPEC = True
    OVERRIDE_INPUTFILE_PATH = None
    JOINING_OPERATOR = '/'

    @classmethod
    def reset(cls):
        """
        Reset all class variables to their default values.

        This method is useful for testing to ensure a clean state between tests.
        It resets:
            - USE_SPEC to True
            - OVERRIDE_INPUTFILE_PATH to None
            - JOINING_OPERATOR to '/'
        """
        cls.USE_SPEC = True
        cls.OVERRIDE_INPUTFILE_PATH = None
        cls.JOINING_OPERATOR = '/'

    @classmethod
    def InputFilePathFromUserVar(cls, uservar_path):
        """
        Convenience method to configure InputFilePathOptions for a UserVars-based input file path.

        This method simplifies setup by automatically setting both OVERRIDE_INPUTFILE_PATH
        and JOINING_OPERATOR appropriately for UserVars usage in a single call.

        :param uservar_path: UserVars attribute reference (e.g., usrv.InputFilePath).
                            Can be a Spec object, string, or any object with a valid
                            string representation in the format 'ModuleName.VarName'.
        :type uservar_path: Spec or str or any

        Usage::

            from pymtpl.uservars import UserVars
            from pymtpl.helpers import inputfile, InputFilePathOptions

            # Create UserVars and define InputFilePath
            usrv = UserVars('PTH_DTS')
            usrv.InputFilePath = ('GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "/Modules/PTH_DTS/InputFiles/" + FlowMatrix.BomGroupName + "/"', str)

            # Configure InputFilePathOptions with one call
            InputFilePathOptions.InputFilePathFromUserVar(usrv.InputFilePath)

            # Now use inputfile() as normal
            ConfigFile = inputfile('config.csv')
            # Result in MTPL: PTH_DTS.InputFilePath + "config.csv"

        This is equivalent to manually setting::

            InputFilePathOptions.OVERRIDE_INPUTFILE_PATH = 'PTH_DTS.InputFilePath'
            InputFilePathOptions.JOINING_OPERATOR = ' + "'

        :raises ErrorUser: If uservar_path is None, empty string, or contains only whitespace
        """
        id_lno = get_caller_lno()

        # Validate input - convert to string and strip whitespace
        path_str = str(uservar_path).strip() if uservar_path is not None else ''

        confirm(uservar_path is not None and path_str != '',
                'uservar_path must be a non-empty string or Spec object (whitespace-only strings are not allowed)',
                f'Please provide a valid UserVars attribute reference at line# {id_lno}')

        # Set OVERRIDE_INPUTFILE_PATH to the UserVars path (whitespace stripped)
        cls.OVERRIDE_INPUTFILE_PATH = path_str

        # Set JOINING_OPERATOR for UserVars concatenation
        cls.JOINING_OPERATOR = ' + "'


def inputfile(path=None):
    """
    Given a file in the module's input files directory, return the path to the file using HDMT_TP_BASE_DIR
        Supports subfolders, e.g. inputfile("foldername/filename.csv")
        Normalizes the path to use single forward slashes instead of backslashes
        If given none or empty string, returns the module's input files folder path.
        To configure, use InputFilePathOptions.OVERRIDE_INPUTFILE_PATH and InputFilePathOptions.USE_SPEC

    :param path: Relative path to the file within the module's InputFiles directory, or None/empty for the directory itself
    :return: Full path to the file, wrapped in Spec() if InputFilePathOptions.USE_SPEC is True

    """

    confirm(isinstance(path, (str, type(None))),
            f'Error, path must be a string or None, got {type(path)}',
            'Pls provide a valid string path or None to get the input file path.')

    # get the base path
    if InputFilePathOptions.OVERRIDE_INPUTFILE_PATH:
        base_path = InputFilePathOptions.OVERRIDE_INPUTFILE_PATH
    else:
        modulename = Initialize.get_modulename()
        base_path = rf'GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "/Modules/{modulename}/InputFiles'

    # if no file is specified or it's an empty string, return the base path
    if not path:
        # base path should have a trailing forward slash so users don't have to add it when concatenating
        if not InputFilePathOptions.OVERRIDE_INPUTFILE_PATH and not base_path.endswith('/'):
            base_path += "/"
        # add that trailing " if we have an odd number
        if base_path.count('"') % 2 != 0:
            base_path += '"'
        if InputFilePathOptions.USE_SPEC:
            return Spec(base_path)
        else:
            return base_path

    # Normalize path to use single forward slashes instead of backslashes
    normalized_path = path.replace('\\', '/')
    normalized_path = normalized_path.replace('//', '/')  # in case user used double backslashes

    # combine base path and normalized path
    combined_path = f'{base_path}{InputFilePathOptions.JOINING_OPERATOR}{normalized_path}'

    # if the combined path contains an odd number of quotes, add one at the end to balance it
    if combined_path.count('"') % 2 != 0:
        combined_path += '"'

    # return wrapped in spec if need be
    if InputFilePathOptions.USE_SPEC:
        return Spec(combined_path)
    else:
        return combined_path


def inputfile_selector_rule(*args, selectorrule=None, argcount=None):
    """
    Used to create a function that uses a selector rule to choose between multiple input files in the module's InputFiles directory.

    Recommended usage:
            String InputFilePath = GetEnvironmentVariable("~HDMT_TP_BASE_DIR")+"/Modules/PTH_DTS/InputFiles/";  # create a uservar with the path
            from functools import partial
            from pymtpl.helpers import inputfile_selector_rule, inputfile, InputFilePathOptions
            InputFilePathOptions.OVERRIDE_INPUTFILE_PATH = 'MyUserVars.InputFilePath' # override the inputfile path to use the uservar
            FileByChop = partial(inputfile_selector_rule, selectorrule=TPKnobs.Chop, argcount=2) # create a new function called FileByChop
            ConfigurationFile = FileByChop("xcc.csv", "lcc.csv") # use FileByChop to get the path

    MTPL result will be ConfigurationFile = MyUserVars.InputFilePath + TPKnobs.Chop("xcc.csv", "lcc.csv")

    :param args: Arguments to pass to the selector rule
    :param selectorrule: The selector rule to use, e.g. TPKnobs.Chop
    :param argcount: The number of arguments for the selector rule to enforce
    """
    # get line number
    id_lno = get_caller_lno()

    confirm(selectorrule is not None and isinstance(selectorrule, str),
            f'Error, selectorrule must be a non-empty string on line {id_lno}',
            'Pls provide a valid selector rule string to use inputfile_selector_rule().')

    confirm(argcount is not None,
            f'Error, no argcount specified on line {id_lno}',
            'Pls provide argcount=n in the partial declaration for inputfile_selector_rule()')

    # verify we're using the right number of arguments
    confirm(len(args) == argcount,
            f'Error, expected {argcount} arguments, got {len(args)} on line {id_lno}',
            'Pls provide the correct number of arguments to inputfile_selector_rule().')

    # base is input file folder plus selector rule
    ret = inputfile() + f' + {selectorrule}('
    # put quotes around each positional arg and join by ,
    ret += ', '.join([f'"{v}"' for v in args])
    ret += ')'
    return Spec(ret)
