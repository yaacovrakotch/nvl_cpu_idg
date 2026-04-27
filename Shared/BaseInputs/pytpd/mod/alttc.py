#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
alttc module - See: https://wiki.ith.intel.com/display/ITSpdxtp/ARL+Auto-LTTC+Infrastructure

# TODO: LTTC multitrial counter must be unique (currently we just copy and dont change it)
# TODO: Do we really need a supercede base json, when we can edit the module json directly?
# TODO: Add setbin for TrialAction Exit
# Idea: NVL: In base json can we define barebones here? So that TPI does not need to create barebones.
"""
import re
from gadget.files import File
from gadget.errors import ErrorUser, confirm, ErrorInput
from collections import OrderedDict
from copy import deepcopy
from pprint import pprint
from mod.update_mtpl import FlowUpdater
from collections import defaultdict
from gadget.pylog import log
from os.path import exists, dirname, basename
from gadget.tputil import OtplFile, is_number
import glob
import json


class ALttc:
    """
    This class expects cwd to be repo root

    General algo:

    Step1: main() is called  << entry point
    Step2: process_subflow() is called (for every item in registry)
    Step3: Then process_json() is called, which is one module .json file. One .json per subflow.
           process_json() has all the steps to add the lttc instances
    Step4: ProgramFlows.mtpl is updated once for the entire routine

    """

    def __init__(self, tpobj):
        self.tpobj = tpobj
        self.m2f = None
        self.folder2testplan = None
        self.cnt_files = set()
        self.json_wip = None    # Name of file being read

    def main(self):
        """Main entry point"""

        # Read the registry first
        registry_file = f'{self.tpobj.envdir}/InputFiles/ALTTC_registry.json'
        if not exists(registry_file):
            log.info('-i- InputFiles/ALTTC_registry.json does not exist. Skipping ALTTC.')
            return       # Do nothing

        # call the tpobj mtpl stuff
        if not self.tpobj.mtpl.get_dutflow_map():
            self.tpobj.mtpl.read_mtpls()
            self.tpobj.mtpl.read_mtpl_flow()

        self.m2f = self.tpobj.mtpl.get_mod2fname()
        self.folder2testplan = self.tpobj.mtpl.get_modfolder2mod()
        self.flowupdater = FlowUpdater(self.tpobj, self.tpobj.get_final_mtpl(), None)

        # Read registry
        with open(registry_file) as fh:
            try:
                registry = json.load(fh)    # {'subflow' : <list_of_jsons_first_element_is_flow>}
            except Exception as e:
                raise ErrorInput(f'Error reading [{registry_file}]. Error: {e}', 'Pls fix registry file')

        # Iterate to all the subflow in the registry
        for subflow in registry:
            self.process_subflow(subflow, registry[subflow])

        # Write the programflows back
        self.flowupdater.write()

        print(f"Success ALTTC total {len(self.cnt_files)} files processed.")
        return len(self.cnt_files)

    def process_subflow(self, subflow, rlist):
        """
        Process one subflow
        :param subflow: Name of subflow
        :param rlist: List of json with first element is the anchor
        :return:
        """
        confirm(rlist, f'{subflow} in ALTTC_registry.json is empty', 'This is not allowed')

        if len(rlist) == 1:    # Anchor only
            return    # Nothing to add

        anchor = rlist[0]
        for lttc_file in rlist[1:]:
            self.cnt_files.add(lttc_file)
            self.json_wip = lttc_file
            with open(lttc_file) as fh:
                try:
                    data = json.load(fh)
                except json.decoder.JSONDecodeError as e:
                    raise ErrorUser(f'LTTC json has error: {e}', f'Pls fix {lttc_file}')

                module = basename(dirname(dirname(lttc_file)))
                self.process_json(subflow, anchor, module, data, lttc_file)

    def process_json(self, subflow, anchor, module, data, lttc_file):
        """
        Process one jsonfile (data) given the subflow and anchor
        Aka, process one mtpl

        :param subflow: subflow name
        :param anchor: anchor name
        :param module: module folder name
        :param data: lttc json data
        :param lttc_file: filename
        :return:
        """
        mod_testplan = self.folder2testplan[module]
        mtplfile = self.m2f[mod_testplan]
        mtplobj = OtplFile(mtplfile)

        # {"comment": "This instance caused several issues in 61B0 TP",
        #  "Instance Name": "BGCEP_X_ANAMEAS_K_BEGCPUPKG_X_X_X_X_BGR_ANAPRB_POST",
        #  "DUTFlow Name": "PTH_BGCEP_CXX_LTTCCPUPKG_TEST",
        #  "Module Port": {0: 'NEXT',
        #                  1: 'NEXT',
        #                  2: 'NEXT',
        #                  3: 'NEXT',
        #                  4: 'NEXT',
        #                  5: 'NEXT',
        #                  6: 'Delete',
        #                  },
        #  },

        lines = File(mtplfile).raw()
        found_programflow = None
        all_counters = set()
        dutflow = defaultdict(list)
        added_ti = []
        scope_val = self.tpobj.get_ipname(mod_testplan)
        scope_val = scope_val if scope_val else 'PKG'
        for idx, item in enumerate(data):

            # Check for the one-time info
            if 'ProgramFlow Port' in item:
                found_programflow = item['ProgramFlow Port']
                self.check_keys(item, ['ProgramFlow Port'], lttc_file)
                continue

            self.check_keys(item,
                            ['Instance Name', 'DUTFlow Name', 'Module Port', 'param', 'SetBin'],
                            lttc_file)

            # step1: copy the instance item["Instance Name"]
            ti = item['Instance Name']
            new_block = list(mtplobj.get_block('Test', ti, elemno=2))
            if not new_block:
                # Try MultiTrial
                new_block = list(mtplobj.get_block('MultiTrialTest', ti, elemno=1))
                confirm(new_block, f'Test {ti} is not found in {mtplfile}', 'Pls check.')

            # step2: Determine next ti_name, empty if none
            if idx == (len(data) - 1):
                new_ti_next = None
            else:
                new_ti_next = self.update_name(data[idx + 1]['Instance Name'], subflow.split('_')[0])

            # step2: Rename the 5th section to subflow name
            new_ti = self.update_name(ti, subflow.split('_')[0])
            new_block[0] = new_block[0].replace(ti, new_ti)       # replacing Test or MultiTrialTest name
            new_block.append('\n')

            self.replace_trialtest_name(new_block, subflow.split('_')[0])

            self.process_param(new_block, item.get("param", {}))

            self.process_basenumber(new_block, mtplfile)

            self.insert_ti(lines, new_block, mtplfile)

            # step3: update the item["param"]

            # step4: Create a DUTFlow from item["DUTFlow Name"]
            dutflowname = item['DUTFlow Name']
            ports, edcports = self.read_module_ports(item["Module Port"])
            if dutflowname not in dutflow:
                dutflow[dutflowname].append('')
                dutflow[dutflowname].append(f'DUTFlow {dutflowname}')
                dutflow[dutflowname].append('{')

            added_ti.append((dutflowname, new_ti))
            dutflow[dutflowname].append(f'    DUTFlowItem {new_ti} {new_ti}')
            dutflow[dutflowname].append('    {')
            dutflow[dutflowname].append('        Result -2')
            dutflow[dutflowname].append('        {')
            dutflow[dutflowname].append('            Property PassFail = "Fail";')
            dutflow[dutflowname].append('            SetBin SoftBins.b90999901_fail_FAIL_DPS_ALARM;')
            dutflow[dutflowname].append('            Return -1;')
            dutflow[dutflowname].append('        }')
            dutflow[dutflowname].append('        Result -1')
            dutflow[dutflowname].append('        {')
            dutflow[dutflowname].append('            Property PassFail = "Fail";')
            dutflow[dutflowname].append('            SetBin SoftBins.b90989801_fail_FAIL_SYSTEM_SOFTWARE;')
            dutflow[dutflowname].append('            Return -1;')
            dutflow[dutflowname].append('        }')

            # merge original port and json port into all_ports.
            # The design of SetBin from json is: The Setbin will be copied from original .mtpl.
            # The SetBin in json will specify additional SetBin in the lttc testinstance.
            # User will get bin69 if they forget. Script cannot decide when or when not to put SetBin.
            all_ports = self.get_original_ports(ti, ports, mod_testplan, new_ti_next, item.get("SetBin", {}))

            for port in sorted(all_ports):
                if port in (-2, -1):    # These are special port, hardcoded above
                    continue
                dutflow[dutflowname].append(f'        Result {port}')
                dutflow[dutflowname].append('        {')
                pf = all_ports[port]['PassFail']
                dutflow[dutflowname].append(f'            Property PassFail = "{pf}";')

                # Step5: Increment Counter handling unique
                res = self.derive_counter(all_ports[port], new_ti)
                if res:
                    all_counters.add(res)
                    dutflow[dutflowname].append(f'            IncrementCounters {res};')

                # Step6: SetBin handling
                res = self.derive_setbin(all_ports[port], module, new_ti)
                if res:
                    if port not in edcports:
                        dutflow[dutflowname].append(f'            SetBin {res};')

                newline = all_ports[port]["finalline"]
                dutflow[dutflowname].append(f'            {newline};')
                dutflow[dutflowname].append('        }')

            dutflow[dutflowname].append('    }')    # end bracket of DUTFLowItem

        dutflow[dutflowname].append('}')   # end bracket of DUTFLow

        # step6: insert the created dutflow blocks
        for dutflowname in dutflow:
            for line in dutflow[dutflowname]:
                lines.append(f'{line}\n')

        # step7: Update the counter block
        self.update_counter_block(lines, all_counters, mtplfile)

        # step8: We write the mtpl
        File(mtplfile).rewrite(''.join(lines), 'ALttc.process_json()')

        # step9: We update the flw
        self.update_flw(mtplfile, added_ti, mod_testplan)

        # step9: Add the info in ProgramFlows
        # dutflow, dfi, which_port, dfi_new, dfi_testname, dict_update):
        confirm(found_programflow,
                f'[ProgramFlow Port] is not defined in {lttc_file}',
                'This is required to identify the ports on ProgramFlows')

        scope = f'{scope_val}::' if scope_val != 'PKG' else ''
        self.flowupdater.insert(subflow, anchor, 1, dutflowname, f'{scope}{mod_testplan}::{dutflowname}',
                                self.get_port_dict(found_programflow))

    def get_port_dict(self, pfd):    # pfd is programflow dictionary
        """Return the port dictionary for insert in program flows"""

        pd = {-2: {'PassFail': 'Fail', 'Return': '-1'},
              -1: {'PassFail': 'Fail', 'Return': '-1'},
              0: {'PassFail': 'Fail', 'Return': '0'},
              1: {'PassFail': 'Pass', 'PREVIOUS': True}
              }
        # {"0": "Pass: Return 0",
        #  "1": "Fail: NEXT",
        #  "2": "Pass: GoTo <value>",
        # }
        robj = re.compile(r'(Pass|Fail): (Return [\-\d]+|NEXT|GoTo \w+)')
        for port in pfd:
            res = robj.search(pfd[port])
            confirm(res,
                    f'Error on port {port}: "{pfd[port]}": Invalid syntax on the json file: {self.json_wip}',
                    f'Expecting line syntax of: {robj.pattern}')
            if res.group(2).startswith('NEXT'):
                pd[int(port)] = {'PassFail': res.group(1), 'PREVIOUS': True}
            elif res.group(2).startswith('Return'):
                pd[int(port)] = {'PassFail': res.group(1), 'Return': res.group(2).split()[-1]}
            else:   # GoTo
                pd[int(port)] = {'PassFail': res.group(1), 'GoTo': res.group(2).split()[-1]}
        return pd

    def update_flw(self, mtplfile, added_ti, module):
        """
        Update the flw file

        :param mtplfile:
        :param added_ti:
        :return:
        """
        flwfile = mtplfile.replace('.mtpl', '.flw')
        confirm(exists(flwfile),
                f'{flwfile} does not exist',
                f'Code is expecting this file to exist. Pls make sure .flw name is the same with .mtpl')

        raw = File(flwfile).raw()

        final = []
        start = True
        for line in raw:
            if line.strip().startswith('<FlowItem') and start:
                start = False
                # we insert the new items
                for df, item in added_ti:
                    final.append(f'  <FlowItem name="{module}::{df}.{item}" X="25" Y="25" />\n')

            final.append(line)

        File(flwfile).rewrite(''.join(final), 'update_flw()')

    def replace_trialtest_name(self, new_block, composite):
        """
        Update the TrialTeset name to be unique
        :param new_block: list of lines
        :return:
        """
        r_obj = re.compile(r'TrialTest\s+\S+\s+\"(\w+)')
        for idx in range(len(new_block)):
            res = r_obj.search(new_block[idx])
            if res:
                subname = res.group(1)    # this is the name inside quotes
                new_block[idx] = new_block[idx].replace(subname, self.update_name(subname, composite))

    def update_counter_block(self, lines, all_counters, mtplfile):
        """Update the counter block with the new counters"""
        if not all_counters:
            return 1    # Do nothing if no new counters

        start = False
        found = False
        for idx in range(len(lines)):
            line = lines[idx]
            if line.strip() == 'Counters':
                start = True
                found = True
            if line.strip() == '{' and start:
                # insert the new counters
                new_counter_lines = [f'        {x.split(":")[-1]},\n' for x in sorted(all_counters)]
                lines[idx + 1:idx + 1] = new_counter_lines
            if start and line.strip().startswith('}'):
                start = False

        confirm(found, f'Counter block is not found in {mtplfile}',
                'Pls Add a counter block with one element in the mtpl first')

    def derive_counter(self, dd, new_ti):
        """
        Orig Counters  HBSBEFGH
        LTTC Counters: 94HBSBFG

        :param dd: input dictionary
        :return: The alttc counter given original counter (if it exist)
        """
        if 'IncrementCounters' not in dd:
            return None
        inputctr = dd['IncrementCounters']

        #                               H B S B  E  F G  H
        res = re.search(r'^(\w+::[np])(\d\d\d\d)\d(\d\d)\d(_pass_|_fail_)(.*)', inputctr)
        #                     1         2            3         4        5

        if res:
            return f'{res.group(1)}94{res.group(2)}{res.group(3)}{res.group(4)}{new_ti}'
        else:
            raise ErrorInput(f'Counter [{inputctr}] does not follow counter naming convention.',
                             f'Pls fix the Counter name so it follows standard counter naming convention!')

    def derive_setbin(self, dd, module, new_ti):
        """
        SetBin    90HBHBSB   -> 909494HB
        :param module: module name
        :param dd: input dictionary
        :return: The alttc setbin given original setbin (if it exist)

        'SetBin', 'IncrementCounters'):
        """
        if 'SetBin' not in dd:
            return None

        inputbin = dd['SetBin']

        res = re.search(r'^(SoftBins.b\d\d)(\d\d)(\d\d\d\d)(.*)', inputbin)     # SoftBins.b90272723_fail_PTH
        #                        1            2      3      4

        if not res:
            raise ErrorInput(f'Setbin [{inputbin}] does not follow setbin naming convention.',
                             f'Pls fix the Setbin name so it follows standard bin naming convention!')

        if 'SHARED_BIN' in inputbin:
            return f'{res.group(1)}9494{res.group(2)}{res.group(4)}'
        else:
            return f'{res.group(1)}9494{res.group(2)}_fail_{module}_{new_ti}'

    @classmethod
    def read_module_ports(cls, ports):
        """
        Process ports dictionary so we return edc ports and normal module ports
        :param ports: {0: <value>
        :return: ports, edcports
        """
        final_port = {}
        final_edcport = {}
        for port, value in ports.items():
            if value.startswith('EDC:'):
                final_edcport[int(port)] = True
                value = value[4:].strip()
            final_port[port] = value

        return final_port, final_edcport

    def process_basenumber(self, block, fname):
        """
        Special feature - Request from Wei wei
        Automatically update BaseNumbers to start with 9.
        The agreement is that ALTTC will use 9xxxx.
        Qgate will take care of duplicate basenumbers within the testprogram.
        If source instance is already using "9xxxx", then error out.
        :param block: list of lines
        :param fname: mtpl filename
        """
        robj = re.compile(r'(BaseNumbers\s*=\s*")(\d)')
        for idx, line in enumerate(block):
            res = robj.search(line)
            if res:
                confirm(res != '9',
                        f'File {fname} uses [{line}] which starts with 9.',
                        'This is not allowed in alttc. Source instance should start with 1 to 8 basenumbers.')
                block[idx] = block[idx].replace(res.group(1) + res.group(2), f'{res.group(1)}9')

    def process_param(self, block, param):
        """
        Update the test instance lock to param if it exist
        :param block: list of lines
        :param param: dictionary {param: value}
        :return:
        """
        if not param:
            return   # do nothing

        found = set()
        r_line = re.compile(r'^(\s*\w.*)\s*=(.*)$')
        r_line2 = re.compile(r'^(\s*TrialParam)\s+(\w.*)\s*=(.*)$')
        r_line3 = re.compile(r'^\s*(TrialVariable|TrialVariableExitAction)\s+(\S.*)$')
        openbracket = None
        prev = ""
        for idx, line in enumerate(block):

            # special case - TrialAction is always replaced to "TrialAction Exit"
            if line.strip().startswith('TrialAction '):
                block[idx] = '                        TrialAction Exit;\n'
                continue

            # save prev line
            if line.strip() != '{':
                prev = line.strip()

            # store the first open bracket
            if '{' in line and prev.startswith(('Test ', 'TrialTest ', 'CSharpTest ', 'CSharpTrialTest ')):
                openbracket = idx

            # <var> = <value>
            foundvar = None
            res = r_line.search(line)
            if res:
                var = res.group(1)
                if var.strip() in param:
                    foundvar = var.strip()
                if f'TrialParam {var.strip()}' in param:
                    foundvar = f'TrialParam {var.strip()}'

            # TrialParam <var> = <value>
            res = r_line2.search(line)
            if res:
                var = res.group(2)
                if var.strip() in param:
                    foundvar = var.strip()

            # TrialVariable
            res = r_line3.search(line)
            if res:
                var = res.group(1)
                if var.strip() in param:
                    foundvar = var.strip()

            if foundvar:
                found.add(foundvar)
                newvalue = param[foundvar].replace("'", '"')
                if 'TrialVariable' in foundvar:
                    block[idx] = f'            {foundvar} {newvalue};\n'
                elif is_number(newvalue) or 'TrialParam' in foundvar:
                    block[idx] = f'            {foundvar} = {newvalue};\n'
                else:
                    block[idx] = f'            {foundvar} = "{newvalue}";\n'

        # Add the missing params
        confirm(openbracket is not None, 'Cannot find openbracket in Test: \n%s' % ''.join(block),
                'Pls check')
        for var in sorted(param):
            if var not in found:
                newvalue = param[var]
                if is_number(newvalue):
                    block[openbracket + 1:openbracket + 1] = [f'    {var} = {newvalue};\n']
                else:
                    block[openbracket + 1:openbracket + 1] = [f'    {var} = "{newvalue}";\n']

    def get_original_ports(self, ti, ports, mod_testplan, new_ti, setbin={}):
        """
        Given the testinstance name (ti)

        :param ti: original testinstance name
        :param ports: json override dictionary
        :param mod_testplan: module testplan name
        :param new_ti: Next ti name
        :param setbin: setbin dictionary {0: <full_bin_string>}
        :return: {"0": {'passfail': 'Fail',
                        'finalline': 'Return or Goto'}}
        """
        df = self.tpobj.mtpl.get_dutflow_map()
        final = {}
        for subflow in df:
            if subflow.startswith(mod_testplan):
                for dfi in df[subflow]:
                    if dfi == '_ORDER':
                        continue
                    if df[subflow][dfi][999] == ti:
                        # pprint(df[subflow][dfi]); exit(0
                        return self.update_orig_port(df[subflow][dfi], ports, new_ti, setbin)

        raise ErrorInput(f'{ti} is not found in {mod_testplan}', 'Pls fix input json')

    def update_orig_port(self, origport, newport, new_ti, setbin={}):
        """

        :param origport: original dictionary ports
        :param newport: json dictionary ports
        :param new_ti: next ti name, empty if there is no next ti name
        :return: {"0": {'passfail': 'Fail',
                        'finalline': 'Return or Goto'}}
        """
        final = {}
        for port in origport:
            if port == 999:
                continue    # cannot process this special port

            # PassFail
            final[port] = {'PassFail': origport[port].get('PassFail', 'Fail')}

            # Copy these two key into the final output
            for key in ('SetBin', 'IncrementCounters'):
                if key in origport[port]:
                    final[port][key] = origport[port][key]

            # process finalline
            if str(port) in newport:
                if newport[str(port)] == 'NEXT':

                    # remove the SetBin if NEXT (either goto or return)
                    if 'SetBin' in final[port]:
                        del final[port]['SetBin']

                    if new_ti:
                        final[port]['finalline'] = f'GoTo {new_ti}'
                    else:
                        final[port]['finalline'] = 'Return %s' % origport[port].get('Return', '# No Goto or Return')
                else:
                    final[port]['finalline'] = newport[str(port)]     # whatever in json we put it in
            else:
                if 'GoTo' in origport[port] and new_ti:
                    final[port]['finalline'] = f'GoTo {new_ti}'
                else:
                    final[port]['finalline'] = 'Return %s' % origport[port].get('Return', 1 if port == 1 else 0)

            # add the setbin from json
            if str(port) in setbin:
                final[port]['SetBin'] = setbin[str(port)]

        return final

    @classmethod
    def insert_ti(cls, lines, new_block, mtplfile):
        """

        :param lines: The full mtpl line
        :param new_block: the block to be inserted
        :param mtplfile: file name
        :return: Nothing, because it will update lines
        """
        for idx in range(len(lines)):
            if lines[idx].strip().startswith(('Test ', 'CSharpTest ')):
                lines[idx:idx] = new_block
                return
        raise ErrorInput(f'No Test line found in {mtplfile}', 'Code is expecting at least one Test')

    @classmethod
    def update_name(cls, ti, replacement,
                    r_name=re.compile('^([^_]+_[^_]+_[^_]+_[^_]+_)([^_]+)(_.*)')):     # 5th element is the subflow name
        """
        Given testinstance name (for MTL) replace the 5th element with replacement
        :param ti: test instance name
        :param replacement: new subflow name
        :return: updated name
        """
        res = r_name.search(ti)
        confirm(res, f'[{ti}] does not follow naming convention', 'Expecting at least 6 elements.')
        return r_name.sub(r'\1' + replacement + r'\3', ti)

    def check_keys(self, item, valid_keys, lttc_file):
        """
        Checks item dictionary that keys are in valid_keys
        :param item: dictionary input
        :param valid_keys: list of keys
        :param lttc_file: name of file
        :return:
        """
        for key in item:
            if key in valid_keys:
                continue
            if key == 'comment':
                continue
            raise ErrorInput(f'{key} is not a valid key in {lttc_file}',
                             f'Pls fix {lttc_file}')
