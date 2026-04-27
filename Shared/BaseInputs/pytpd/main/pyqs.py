#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
pyqs.py merge
pyqs.py /path/xml -convert

How it works:
1. Read all Modules/*/*qs.py
2. If empty, do port-injection
3. If not exist, do nothing.
"""
import setenv      # must be first in the imports
from gadget.vepargs import Args, TA_StoreTrue, TA_All, TA_AppendSC, TA_StoreDir, TA_StoreFile
from gadget.tputil import remove_ip
from gadget.dictmore import DictDot, xmlfunc
from gadget.errors import ErrorInput, confirm
from gadget.files import File
from gadget.helperclass import OPT
from gadget.disk import mkdirs
from pyqs import Merge
from tp.testprogram import Env, TestProgram
from collections import defaultdict
from pprint import pprint


class PyQsArgs(Args):   # parent: ArgsBase

    def config(self):
        """
        Define the arguments for the script.
        The order below will matter, it is the order of display during help.
        """
        cfg = DictDot()
        cfg.all = TA_All('Source code')
        cfg.env = TA_StoreFile('Env file', metavar='envfile')
        cfg.convert = TA_StoreTrue('Convert input xml')
        cfg.mtpl = TA_StoreFile('Run one qs.py given mtpl', metavar='/path/file.mtpl')
        return cfg

    def main(self):
        """
        Main entry point of executable
        -h will not reach this method, since that is taken cared of in Args Base class
        """
        if not OPT.all:
            self.print_help()

        if OPT.all[0] == 'merge':
            self.do_merge()

        elif OPT.convert:
            return Convert(OPT.all[0]).main()

        elif OPT.mtpl:
            self.do_one()

        else:
            print("Unknown command")
            self.print_help()

    def do_one(self):
        """One qs run"""
        env = OPT.env if OPT.env else Env.get_envfile()
        tpobj = TestProgram(env).init()
        obj = Merge(tpobj)
        obj.import_one(OPT.all[0], OPT.mtpl)
        obj.main()
        obj.write_file('final_qs.xml')

    def do_merge(self):
        """Merge"""
        env = OPT.env if OPT.env else Env.get_envfile()
        tpobj = TestProgram(env).init()
        obj = Merge(tpobj)
        obj.importall()
        obj.main()
        obj.write_file('final_qs.xml')


class Convert:
    """
    Given xml that contains manual inject, convert it to pyqs syntax
    One virtual dut only
    """

    def __init__(self, inputxml):
        self.inputxml = inputxml
        self.default_occurrence = {'default': 'true', 'status': 'Pass'}
        self.module = None
        self.contact = 'Pls contact jqdelosr or vsgatcha to fix this'

    def main(self):
        """Main entry point"""
        # read xml first
        data = xmlfunc.xml2dict(self.inputxml)

        final = defaultdict(list)   # {module: [list_of_lines]}
        response = data['Quicksim']['virtualdut']['response']
        if isinstance(response, dict):
            response = [response]
        for item in response:
            for line in self.process(item):
                final[self.module].append(line)

        # write to file
        for module in final:
            output = [self.get_import(),
                      f"SetModule('{module}')"]
            output.extend(final[module])
            mkdirs(f'Modules/{remove_ip(module)}')
            File(f'Modules/{remove_ip(module)}/qs.py').rewrite('\n'.join(output), 'Convert()')

        print(f"Convert Success: Total of {len(final)} modules process.")
        return '\n'.join(final)

    def get_import(self):
        """Return the import line"""
        return ("from pyqs import PortInject, ManualInject, SetModule, ctvData, portData, pinData, "
                "thermalData, userVar, cycleData, triggerData, patternData")

    def process(self, level2):
        """One response item"""
        ti = level2['testInstance']
        plist = level2.get('plist')
        INDENT = '    '

        # module and ip
        elems = level2['testInstance'].split(':')
        if len(elems) == 5:
            ip, _, mod, _, ti = elems
            self.module = f'{ip}::{mod}'
        elif len(elems) == 3:
            ip = None
            mod, _, ti = elems
            self.module = mod
        else:
            raise ErrorInput(f"Missing module scope? {level2['testInstance']}", "Expecting module::name")

        # result types (level2)
        keys_rtype = {'flowResult', 'plistResult', 'dcResult', 'thermalResult'}
        chk = level2.keys() - (keys_rtype | {'testInstance', 'plist'})
        confirm(not chk, f'Error: Key {chk} is not coded for level2', self.contact)
        for rtype in sorted(level2.keys() & keys_rtype):
            level3 = level2[rtype]    # occurrence

            chk = level3.keys() - {'injectTime', 'occurrence'}
            confirm(not chk, f'Error: Key {chk} is not coded for level3', self.contact)

            # rtype value
            rvalue = {}
            for attrib in ('injectTime', ):
                if attrib in level3:
                    rvalue[attrib] = level3[attrib]

            level4top = level3['occurrence']
            if isinstance(level4top, dict):
                level4top = [level4top]

            for level4 in level4top:
                keys_level4 = {'status', 'default', 'start', 'stop'}
                keys_l4objects = {'ctvData', 'portData', 'pinData', 'thermalData', 'userVar', 'cycleData', 'triggerData', 'patternData'}
                chk = level4.keys() - (keys_level4 | keys_l4objects)
                confirm(not chk, f'Error: Key {chk} is not coded for level4', self.contact)

                # occurence value
                ovalue = {}
                for attrib in sorted(keys_level4):
                    if attrib in level4:
                        ovalue[attrib] = level4[attrib]
                if ovalue == self.default_occurrence:
                    ovalue = None

                yield f'ManualInject("{ti}",'
                if plist:
                    yield f'{INDENT}plist="{plist}",'
                yield f'{INDENT}{rtype}={rvalue},'
                if ovalue:
                    yield f'{INDENT}occurrence={ovalue},'
                yield f'{INDENT}actions=['

                for l4type in sorted(level4.keys() & keys_l4objects):
                    if l4type == 'patternData':
                        level5 = level4[l4type]
                        if isinstance(level5, dict):
                            level5 = [level5]
                        for level5d in level5:
                            for line in self.patternData(level5d):
                                yield line

                    else:
                        level4data = level4[l4type]
                        if isinstance(level4data, dict):
                            level4data = [level4data]

                        for level4a in level4data:
                            yield f'{INDENT}{INDENT}{l4type}({self.to_keyeqval(level4a)}),'

                yield f'{INDENT}])'

    def patternData(self, level5):
        """
        {'domainData': {'name': 'ACPU_TAP_ALL',
                        'triggerData': [{'name': 'Trigger1', 'type': 'LevelsTC'},
                                        {'name': 'Trigger1', 'type': 'LevelsTC'}]},
         'pattern': 'g0417338C'}

        :param level5:
        :return:
        """
        INDENT = '    '

        chk = level5.keys() - {'domainData', 'pattern'}
        confirm(not chk, f'Error: Key {chk} is not coded for level5 patternData', self.contact)

        chk = level5["domainData"].keys() - {'name', 'triggerData', 'cycleData'}
        confirm(not chk, f'Error: Key {chk} is not coded for level6 patternData domainData', self.contact)

        yield f'{INDENT}{INDENT}patternData('
        yield f'{INDENT}{INDENT}{INDENT}domainData="{level5["domainData"]["name"]}",'
        yield f'{INDENT}{INDENT}{INDENT}pattern="{level5["pattern"]}",'
        yield f'{INDENT}{INDENT}{INDENT}actions=['

        if "triggerData" in level5["domainData"]:
            triggerdata = level5["domainData"]["triggerData"]
            if isinstance(triggerdata, dict):
                triggerdata = [triggerdata]
            for level6 in triggerdata:
                yield f'{INDENT}{INDENT}{INDENT}{INDENT}triggerData({self.to_keyeqval(level6)}),'

        if "cycleData" in level5["domainData"]:
            cycledata = level5["domainData"]["cycleData"]
            confirm(isinstance(cycledata, dict), f'Expecting dict: {cycledata}', 'Check logic of cycleData')
            yield f'{INDENT}{INDENT}{INDENT}{INDENT}cycleData({cycledata["address"]}, actions=['
            if isinstance(cycledata["pinData"], dict):
                pindata = [cycledata["pinData"]]
            else:
                pindata = cycledata["pinData"]
            for level6 in pindata:
                yield f'{INDENT}{INDENT}{INDENT}{INDENT}{INDENT}pinData({self.to_keyeqval(level6)}),'
            yield f'{INDENT}{INDENT}{INDENT}{INDENT}]),'

        yield f'{INDENT}{INDENT}{INDENT}]),'

    def to_keyeqval(self, dd):
        """Return a string key=value, etc"""
        final = []
        for key, value in sorted(dd.items()):
            final.append(f'{key}="{value}"')
        return ', '.join(final)


if __name__ == '__main__':    # pragma: no cover
    PyQsArgs(desc=__doc__).main()
