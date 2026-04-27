#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Parallel Flow  routine
"""
from gadget.files import File
from gadget.tputil import read_blocks, OtplFile
from gadget.pylog import log
from gadget.errors import ErrorInput, confirm
from os.path import join, dirname, exists, realpath, basename
from tp.testprogram import TestProgram
from pprint import pprint
import json
import glob


class PrlFlow:
    """
    Create (aka, Stitch) parallel flow connection based on serial flow.
    See wiki: https://wiki.ith.intel.com/x/Jpfaiw

    Algo:  main()                - entry point
    step1. initial_map()         - Read the initial subflow to portno mapping from programflows.mtpl
           read_json()           - Read intradut_flows.json for each parallel subflow start and end.
           process()             - For each parallel subflow, do step2 to 6.
    step2. get_all_subflows()    - Read the testprogram, get all the subflows between start and end
    step3. paste_dutflow()       - Get all dutFlow blocks for subflows from step2 above. Insert this in the IP_*CONCURRENT*.mtpl
    step4. insert_dutflowitems() - Insert all the subflows in dutflowitem
    step5: one_dutflowitem()     - Remap the ports (dynamic add based on when it's read)
    step6: update_programflow()  - Update ProgramFlows.mtpl based on step5 info for the ports
    """

    def __init__(self, envfile):
        """

        :param envfile: TP Envfile
        """
        # class vars
        self.tpobj = TestProgram(envfile)   # Don't instantiate the entire program, so it's fast
        self.DutFlow = 'Flow' if self.tpobj.is_tos4 else 'DUTFlow'
        self.startend = {}   # {'IP::prlsubflowname': (start, end)}

        # initialize the flows
        self.tpobj.mtpl.init_dutflow()
        # {'MAIN': {
        #             'BEGCPU_SubFlow': {-2: {'GoTo': 'ALARM_SubFlow', 'PassFail': 'Fail'},
        #                                -1: {'GoTo': 'ALARM_SubFlow', 'PassFail': 'Fail'},
        #                                 0: {'GoTo': 'FFPKG_SubFlow', 'PassFail': 'Fail'},
        #                                 1: {'GoTo': 'SCHDCF1_SubFlow', 'PassFail': 'Pass'},
        #                                 2: {'GoTo': 'IPFFCPU_SubFlow', 'PassFail': 'Fail'},
        #                               999: 'BEGCPU_SubFlow'},

        self.tpobj.mtpl._read_mtpl_flow(self.tpobj.get_final_mtpl())
        self.dutflows = self.tpobj.mtpl._dutflow['MAIN']
        self.prl2ip = self.get_prl2ip(self.tpobj.get_final_mtpl())   # {'IP::prlsubflow': 'prlname'}

        self.mapping = self.initial_map()    # {'prlname': {subflow: portno}}    # This is auto-populated

        self.startend = self.read_json(f'{dirname(realpath(envfile))}/intradut_flows.json')
        self.ext_name = 'origprl'

    def main(self):
        """Main Entry point - Iterate on each parallel flow, as defined in json"""
        if not self.startend:
            log.info(f"-i- intradut_flows.json is not found for PrlFlow(). Nothing to do.")
            return    # Do nothing

        self.check_rerun()

        for prlflows in self.startend:
            assert len(self.startend[prlflows]) == 3, f'json input incorrect for {prlflows}. Expecting 3 elements.'
            self.process(prlflows, self.startend[prlflows][0], self.startend[prlflows][1:])

        # Write ProgramFlows file
        pfile = self.tpobj.get_final_mtpl()
        programflowlines = self.update_programflow(pfile)
        File(pfile).rewrite(''.join(programflowlines), f'PrlFlow().main()', keep=self.ext_name)

    def process(self, key, insertat, startend):
        """
        Process one parallel flow

        :param key: 'IP_CPU_CONCURRENT_FLOWS::PRL0CPUGT_IP_CPU_FLOW_SubFlow'
        :param insertat: starting subflow to insert the flow
        :param startend: (startflow, endflow)
        :return:
        """
        log.info(f"-i- PrlFlow: processing {key}...")
        pfile = self.tpobj.get_final_mtpl()

        # step1: Get all subflows between start and end
        subflows = self.get_all_subflows(startend)

        # step2: Get all dutflow blocks
        mtplfile = self.get_ip_mtpl(key)
        new_subflows = self.get_new_subflows(mtplfile, subflows)
        blocks = read_blocks(pfile, [f'{self.DutFlow} {x}' for x in new_subflows])

        # step3: paste dutflows into IP.mtpl
        flines = list(self.paste_dutflow(mtplfile, blocks))

        # step4: insert the dutflowitems into flines
        flines = self.insert_dutflowitems(flines, key, subflows, mtplfile, insertat)

        # step5: Write flines to IP.mtpl
        File(mtplfile).rewrite(''.join(flines), f'PrlFlow().process({key})', keep=self.ext_name)

    def check_rerun(self):
        """Allow rerun, by renaming .origprl files back"""
        # Programflow/*.mtpl - tpie
        # Modules/*/*.mtpl - tpie & Torch
        # POR_TP/Class_MTL_P68_DEBUG/ProgramFlowsTestPlan/*.mtpl
        #   1           2                    3
        allfiles = (glob.glob(f'{self.tpobj.tpldir}/*/*.{self.ext_name}') +
                    glob.glob(f'{self.tpobj.tpldir}/*/*/*.{self.ext_name}') +
                    glob.glob(f'{self.tpobj.tpldir}/*/*/*/*.{self.ext_name}'))
        for ff in allfiles:
            oname = ff.replace(f'.{self.ext_name}', '')
            File(oname).unlink()    # delete new file
            File(ff).rename(basename(oname))    # rename it back
            log.info(f'-i- Rerun: renaming back {ff}')

    def read_json(self, jsonfile):
        """
        Read configuration jsonfile

        :param jsonfile:
        :return: startend and mapping dictionary
        """
        if not exists(jsonfile):
            return {}
        log.info(f'-i- Reading PrlFlow config: {jsonfile}')
        with open(jsonfile) as fh:
            data = json.load(fh)
        return data['STARTEND']

    def initial_map(self):
        """
        :return: Initial mapping for all parallel flows
        """
        result = {}
        for prlflow in sorted(set(self.prl2ip.values())):
            result[prlflow] = {}
            for portno in self.dutflows[prlflow]:
                if 'GoTo' in self.dutflows[prlflow][portno]:
                    sflow = self.dutflows[prlflow][portno]['GoTo']
                    result[prlflow][sflow] = portno
        return result

    def get_new_subflows(self, mtplfile, subflows):
        """
        Read all dutflow in mtplfile, then return only new subflows

        :param mtplfile: mtpfile
        :param subflows: list of subflows
        :return: list of new
        """
        existing = set()
        with open(mtplfile) as fh:
            for line in fh:
                sline = line.strip()
                if sline.startswith(f'{self.DutFlow} '):
                    existing.add(sline.split(' ')[1])

        result = []
        for item in subflows:
            if item not in existing:
                result.append(item)
        return result

    def update_programflow(self, pfile):
        """
        Iterator: Update ProgramFlows.mtpl for one parallel flow
        Assumes that dutflowItem is correctly formatted (ie, brackets are in it's own line)
        :param pfile: Path to ProgramFlows.mtpl
        :return: line (iterator)
        """
        prlflows = tuple(f'{self.DutFlow}Item {x}' for x in self.mapping)
        start = 0
        name = None
        startgoto = False
        passnext = None
        with open(pfile) as fh:
            for line in fh:
                sline = line.strip()
                if sline.startswith(prlflows):
                    yield line
                    name = line.split()[1]
                    start = 1
                if start and sline == '{':
                    if start == 1:
                        yield line
                    start += 1
                    continue
                if start and sline.startswith('Result 1'):
                    startgoto = True
                if startgoto and sline.startswith('GoTo'):
                    passnext = sline.split()[1].replace(';', '')
                    startgoto = False
                if start and sline == '}':
                    start -= 1
                    if start == 1:
                        for insertline in self._programflow_lines(name, passnext):
                            yield insertline
                        start = 0
                    else:
                        continue    # pragma: no cover    (due to python optimizations)

                if not start:
                    yield line

        assert not start, (f'{pfile} {self.DutFlow}Item for parallelflows if incorrectly formatted '
                           f'(brackets must be its own line.')

    def _programflow_lines(self, flowname, passnext):
        """
        Iterator: return lines for dutflowItem block

        Why is this private method? Because it is not unittested invididually.
        It is tested as part of update_programflow()

        :param flowname: parallel flow name
        :param passnext: next goto line
        :return: line (iterator)
        """
        revmap = {}    # {portno: name}
        for key in self.mapping[flowname]:
            revmap[self.mapping[flowname][key]] = key

        # ports -2 to 1
        text = """
            Result -2
            {
                Property PassFail = "Fail";
                GoTo ALARM_SubFlow;
            }
            Result -1
            {
                Property PassFail = "Fail";
                GoTo ALARM_SubFlow;
            }
            Result 0
            {
                Property PassFail = "Fail";
                GoTo %s;
            }
            Result 1
            {
                Property PassFail = "Pass";
                GoTo %s;
            }""" % (revmap[0], passnext)
        for line in text.split('\n'):
            yield f'{line}\n'

        # The rest of the ports
        for portno in sorted(revmap):
            if portno in (-2, -1, 0, 1):
                continue
            yield(f'            Result {portno}\n')
            yield(f'            {{\n')
            yield(f'                Property PassFail = "Fail";\n')
            yield(f'                GoTo {revmap[portno]};\n')
            yield(f'            }}\n')

    def insert_dutflowitems(self, flines, key, subflows, mtplfile, insertat):
        """
        Insert Dutflowitems in flines

        :param flines: lines of mtpl
        :param key: subflow name: 'IP_CPU_CONCURRENT_FLOWS::PRL0CPUGT_IP_CPU_FLOW_SubFlow'
        :param subflows: list of subflows
        :param mtplfile: filename
        :param insertat: insert at this subflow
        :return: new flines
        """
        # get dutflow_target
        dutflow_target = '%s %s' % (self.DutFlow, key.split(':')[-1])

        # create mapping
        mapkey = self.prl2ip[key]
        mapping = self.mapping[mapkey]

        # goto all the lines
        final = []
        found = 0
        for line in flines:

            # find first "Result 1" of the starting block, then replace the goto
            if line.strip() == dutflow_target:
                found = 1

            if found == 1 and f'FlowItem {insertat} ' in line:
                found = 2

            if found == 2 and line.strip() == 'Result 1':
                found = 3

            if found == 3 and line.strip().startswith('GoTo '):
                found = 4
                replacement = 'GoTo %s;\n' % subflows[0]
                final.append(f'         {replacement}')
                lastflowitem = line.strip().split()[-1][:-1]     # remove semicolon

                # do check
                error_msg = f'{mtplfile} is already postprocessed. Pls revert to original (.old) file first.'
                assert line.strip() != replacement.strip(), error_msg

                # do not re-write this line
                continue     # pragma: no cover    (due to python optimizations)

            # insert each subflow block
            if found == 4 and line.strip().startswith(('FlowItem ', 'DUTFlowItem ')):
                found = 5

                for idx in range(len(subflows)):
                    # determine next flow
                    if idx == len(subflows) - 1:
                        nextflow = lastflowitem
                    else:
                        nextflow = subflows[idx + 1]

                    # write out the block
                    for item in self.one_dutflowitem(subflows[idx], nextflow, mapping):
                        final.append(item)

            # add the line
            final.append(line)

        assert found != 3, f'{insertat} cannot be the last item for {key}'
        assert found == 5, f'{dutflow_target} is not found in {mtplfile}! Cannot insert parallel flow.'
        return final

    def one_dutflowitem(self, subflow, nextflow, mapping):
        """
        Iterator: return the durflowitem block of this subflow

        :param subflow: Which subflow
        :param nextflow: Next subflow
        :param mapping: port mapping
        :return: line (iterator)
        """
        yield f'    {self.DutFlow}Item {subflow} {subflow}\n'
        yield f'    {{\n'

        # Iterate to  all the ports of this subflow (from ProgramFlows.mtpl -> MAIN)
        assert subflow in self.dutflows, f'{subflow} is not found in MAIN!'
        for ret_port in sorted(self.dutflows[subflow]):
            if ret_port == 999:    # special port
                continue

            # Determine return port
            if ret_port == 1:
                ret = f'GoTo {nextflow}'
            else:
                # remap
                if 'GoTo' in self.dutflows[subflow][ret_port]:
                    item = self.dutflows[subflow][ret_port]['GoTo']

                    # Add it if it does not exist
                    if item not in mapping:
                        mapping[item] = max(mapping.values()) + 1

                    value = mapping[item]
                    if item == 'ALARM_SubFlow' and ret_port == -2:   # special case
                        value = -2
                else:
                    confirm('Return' in self.dutflows[subflow][ret_port],
                            f'{subflow} of port={ret_port} does not have Return or GoTo.',
                            f'Check {subflow} Expecting either Return or GoTo.')
                    value = self.dutflows[subflow][ret_port]['Return']
                ret = f'Return {value}'

            # property Pass or Fail based on serial flow
            prop = self.dutflows[subflow][ret_port]['PassFail']
            yield f'        Result {ret_port}\n'
            yield f'        {{\n'
            yield f'            Property PassFail = "{prop}";\n'
            yield f'            {ret};\n'
            yield f'        }}\n'

        yield f'    }}\n'

    def paste_dutflow(self, mtplfile, blocks):
        """
        iterator: insert blocks from infile, starting from first "DUTFlow" block

        :param mtplfile: Input file
        :param blocks: list of lines
        :return: line (iterator)
        """
        once = True
        with open(mtplfile) as fh:
            for line in fh:
                if line.startswith(f'{self.DutFlow} ') and once:
                    once = False
                    for item in blocks:
                        yield item

                yield line

    def get_ip_mtpl(self, key):
        """
        Return mtpl associated to the key
        :param key: 'IP_CPU_CONCURRENT_FLOWS::PRL0CPUGT_IP_CPU_FLOW_SubFlow'
        :return: filename
        """
        ipname = key.split(':')[0]
        result = None
        stpl = self.tpobj.get_stpl()
        for lno, line in OtplFile(stpl).readline():
            line = line.replace('\\', '/')
            if f'/{ipname}' in line:
                result = line
        assert result, f'/{ipname}/ not found in {self.tpobj.get_stpl()}'
        result = result.replace('Final ', '')
        result = result.replace(';', '').replace('"', '')
        return join(dirname(stpl), result)

    def get_all_subflows(self, startend, _max=10000):
        """
        :param startend:  (startflow, endflow)
        :return: list of subflows between startflow and endflow
        """
        subflows = []

        assert startend[0] in self.dutflows, f"{startend[0]} is not found. This is required (starting subflow)"
        assert startend[1] in self.dutflows, f"{startend[1]} is not found. This is required (ending subflow)"

        start = startend[0]
        for _ in range(_max):
            subflows.append(start)
            if start == startend[1]:
                break
            assert 'GoTo' in self.dutflows[start][1], f"{start} does not have GoTo on port1. Expecting GoTo"
            start = self.dutflows[start][1]['GoTo']
        else:      # pragma: no cover    (safety check only)
            raise ErrorInput(f'Maximum iteration for {startend[0]} to {startend[1]} on ProgramFlows.mtpl')

        return subflows

    def get_prl2ip(self, pfile):
        """
        Get ip parallel to parallel flow name

        :param pfile:
        :return: dictionary given ip parallel to parallel flow name
        """
        result = {}
        name = None
        for lno, line in OtplFile(pfile).readline():
            if line.startswith('ConcurrentFlow '):
                name = line.split()[1]
            if line.startswith('ConcurrentFlowItem '):
                item = line.split()[2].replace(';', '')
                result[item] = name

        return result
