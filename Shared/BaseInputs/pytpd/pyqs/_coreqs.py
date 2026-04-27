"""
core classes for pyqs
"""
from gadget.pylog import log
from gadget.errors import confirm, ErrorUser, ErrorInput, Check
from gadget.files import File
from gadget.strmore import sha1, to_list
from gadget.tputil import to_regex
from gadget.gizmo import get_caller_lno
from os.path import isdir, dirname, exists
from importlib.machinery import SourceFileLoader
from collections import OrderedDict, defaultdict
import traceback
from pprint import pprint
import re
import glob


INDENT = '    '       # one xml indent


class Merge:
    tpobj = [None]     # global tpobj

    def __init__(self, tpobj):
        self.final = None     # final xml string
        self.tpobj[0] = tpobj
        self.inj_list = None

    @classmethod
    def get_tpobj(cls):
        return cls.tpobj[0]

    @classmethod
    def clear(cls):
        """
        Clear all registry
        :return:
        """
        SetModule.clear()
        PortInject.clear()
        BaseAuto.clear()
        ManualInject.clear()

    def main(self):
        """Main entry point"""
        self.final = '\n'.join(self.write())
        return self.final

    def write(self):
        """Iterator for the intire thing"""
        # Header
        yield '<?xml version="1.0" encoding="utf-8" ?>'
        yield '<Quicksim>'
        yield '<virtualdut name="HappyPathFlow" type="flow" >'

        # step1 - manual inject
        for line in ManualInject.write_main():
            yield f'{INDENT}{line}'

        # step2 - autoinject
        for line in BaseAuto.write_main():
            yield f'{INDENT}{line}'

        # step3 - portinjections
        for obj in PortInject.registry:
            for line in obj.write_main():
                yield f'{INDENT}{line}'

        # end
        yield '</virtualdut>'
        yield '</Quicksim>'

    def write_file(self, outfile):
        """Write to a file"""
        confirm(self.final is not None, 'Error: pls call main() first', 'Usage error')
        File(outfile).rewrite(self.final, 'Merge.write()')

    def importall(self):
        """
        Import all QS files in tp
        If qs.py exist and empty, pyqs will create PortInjection.
        If qs.py does not exist, then no QuickSim injections will be created.
        """
        for mtpl in Merge.get_tpobj().get_all_mtpl_from_stpl():
            target_list = glob.glob(f'{dirname(mtpl)}/*qs.py')
            for target in target_list:
                self.import_one(target, mtpl)

    def import_one(self, target, mtpl):
        """Import one qs file given mtpl"""
        if len(File(target).read()):
            print(f'-i- Importing {target}')
            SourceFileLoader(sha1(target), target).load_module()
        else:
            # empty file
            print(f'-i- Creating auto-port-inject: {target}')
            self.auto_port1(mtpl, Merge.get_tpobj())

    def read_port1_inject(self, tpobj):
        """Read the port inject file"""
        if self.inj_list:
            return 1

        inj_list_file = f'{tpobj.shareddir}/BaseInputs/Scripts/auto_port1_inject_list.txt'
        confirm(exists(inj_list_file), f'Expecting file: {inj_list_file}', 'This file is required')
        self.inj_list = set()
        for line in File(inj_list_file).chomp():
            self.inj_list.add(line)

    def auto_port1(self, mtpl, tpobj):
        """Create the auto port1 inject for this module"""

        # read the inject list
        self.read_port1_inject(tpobj)
        modname = tpobj.get_scope(mtpl, None)
        mod2tname = defaultdict(set)    # {mod: <set_of_testinstance>}
        for md, tn, data in tpobj.mtpl.iter_flows('MAIN', idict=True):
            if md != modname:
                continue

            if data['TEMPLATE'] in self.inj_list:
                mod2tname[md].add(tn)

        for md in mod2tname:
            scope = tpobj.get_ipname(md)
            if scope:
                SetModule(f'{scope}::{md}')
            else:
                SetModule(md)
            for tn in mod2tname[md]:
                PortInject(tn)

    @classmethod
    def xmlline(cls, keyname, dd):
        """
        Returns one xml line
        :param keyname: Name of key
        :param dd: empty or populated
        :return: one line
        """
        if dd:
            line = f'<{keyname}'
            for key in sorted(dd):
                line = f'{line} {key}="{dd[key]}"'
            line = f'{line}>'
            return line
        else:
            return f'<{keyname}>'


class SetModule:
    """Set the modulename for this .py file"""
    modulename = [None]

    def __init__(self, modulename):
        self.modulename[0] = modulename

    @classmethod
    def get_module(cls):
        """Return the module name"""
        return cls.modulename[0]

    @classmethod
    def clear(cls):
        cls.modulename[0] = None


class PortInject:
    registry = []    # list of Portobject

    def __init__(self, *args):
        """
        PortInject("a", "b", "c")
        PortInject(["a", "b", "c"])
        PortInject("testinstance:2")     # inject port2

        :param args: list of instances or regex
        """
        self.args = args
        self.module = SetModule.get_module()
        self.id_lno = get_caller_lno()
        self.registry.append(self)

        # process inputlist
        self.inputlist = []
        for item in args:
            if isinstance(item, list):
                self.inputlist.extend(item)
            else:
                self.inputlist.append(item)

    def write_main(self):
        """Iterator: xml output of this object"""
        robj = re.compile(r'^(.*):(\d+)$')
        for item in self.inputlist:
            # do the port logic
            res = robj.search(item)
            if res:
                instancename = res.group(1)
                portno = res.group(2)
            else:
                instancename = item
                portno = '1'

            yield f'<response testInstance="{self.module}::{instancename}">'
            yield f'{INDENT}<flowResult>'
            yield f'{INDENT}{INDENT}<occurrence default="true"><portData port="{portno}" status="Pass"/></occurrence>'
            yield f'{INDENT}</flowResult>'
            yield f'</response>'
            yield f''

    @classmethod
    def clear(cls):
        cls.registry.clear()


class BaseAuto:
    registry = []     # list of AutoInject

    @classmethod
    def write_main(cls):
        for obj in cls.registry:
            for line in obj.write():
                yield line
            yield ''

    @classmethod
    def clear(cls):
        cls.registry.clear()


class ManualInject:
    registry = []    # List of ManualInject

    def __init__(self,
                 testInstance,
                 plist=None,
                 plistResult=None,
                 flowResult=None,
                 dcResult=None,
                 thermalResult=None,
                 occurrence=None,
                 actions=[]):
        """
        Manual Inject object
        """
        self.testInstance = testInstance
        self.plist = plist
        self.occurrence = occurrence
        self.actions = actions
        self.module = SetModule.get_module()
        self.id_lno = get_caller_lno()

        # check actions
        for item in actions:
            confirm(isinstance(item, BaseAction), f'Unknown action item: [{type(item)}]',
                    'Expecting Action object')

        # *result - One only per object
        self.resulttype = None
        if flowResult is not None:
            self.resulttype = 'flowResult'
            self.resultvalue = flowResult

        if plistResult is not None:
            confirm(self.resulttype is None, f'{self.resulttype} is already set',
                    f'Cannot reassign, in line#{self.id_lno}')
            self.resulttype = 'plistResult'
            self.resultvalue = plistResult

        if dcResult is not None:
            confirm(self.resulttype is None, f'{self.resulttype} is already set',
                    f'Cannot reassign, in line#{self.id_lno}')
            self.resulttype = 'dcResult'
            self.resultvalue = dcResult

        if thermalResult is not None:
            confirm(self.resulttype is None, f'{self.resulttype} is already set',
                    f'Cannot reassign, in line#{self.id_lno}')
            self.resulttype = 'thermalResult'
            self.resultvalue = thermalResult

        confirm(self.resulttype is not None, f'[*Result] is not specified',
                f'[*Result] is required, in line#{self.id_lno}')

        # add to registry
        self.registry.append(self)

    @classmethod
    def write_main(cls):
        """Main write of Manual Inject - Write all objects"""
        # get occurrence first per instance/module/plist
        occdata = {}    # {key: {occstring: <cnt>}}
        for obj in ManualInject.registry:
            occstring = str(obj.occurrence)
            key = (obj.testInstance, obj.module, obj.plist, obj.resulttype, str(obj.resultvalue))
            if key not in occdata:
                occdata[key] = defaultdict(int)
            occdata[key][occstring] += 1

        # get all unique first
        uniq = defaultdict(list)
        octr = defaultdict(int)
        for obj in ManualInject.registry:
            occstring = str(obj.occurrence)
            key = (obj.testInstance, obj.module, obj.plist, obj.resulttype, str(obj.resultvalue))
            if occdata[key][occstring] > 1:
                octr[(key, occstring)] += 1
                ctr = octr[(key, occstring)]
            else:
                ctr = 1

            uniq[(obj.testInstance, obj.module, obj.plist, ctr)].append(obj)

        # write it
        for key in uniq:
            # header
            name, module, plist, idx = key
            if plist:
                yield f'<response testInstance="{module}::{name}" plist="{plist}">'
            else:
                yield f'<response testInstance="{module}::{name}">'

            # data
            for line in cls.write_level2(uniq[key]):
                yield f'{INDENT}{line}'

            # footer
            yield '</response>'
            yield ''    # empty space between

    @classmethod
    def write_level2(cls, list_obj):
        """Write flowResult, dcResult, etc"""
        # get all unique first
        uniq = defaultdict(list)
        for obj in list_obj:
            head = Merge.xmlline(obj.resulttype, obj.resultvalue)
            uniq[(head, obj.resulttype)].append(obj)

        # write it
        for key in uniq:
            head, foot = key
            yield head
            for obj in uniq[key]:
                for line in obj.write_level34():
                    yield f'{INDENT}{line}'
            yield f'</{foot}>'

    def write_level34(self):
        """Write level3 and level4"""
        # header
        default = {'default': 'true', 'status': 'Pass'}
        line = Merge.xmlline('occurrence', self.occurrence if self.occurrence else default)
        yield line

        # single item objects
        for item in self.actions:
            if item.is_single():
                for line in item.write():
                    yield f'{INDENT}{line}'     # action line

        # multi-item objects
        for line in patternData.write_main(self.actions):
            yield f'{INDENT}{line}'

        # footer
        yield '</occurrence>'

    @classmethod
    def clear(cls):
        cls.registry.clear()


class BaseAction:
    """Base class for ManualInject action objects"""

    def is_single(self):
        """
        Return True if this class is single line, False otherwise
        For non single line, write_main() is needed to be implemented.
        """
        return True   # Default Single

    def write_main(self):       # pragma: no cover
        """This is implemented in subclass like patternData() in which it needs a collection of objects"""
        raise Exception("Code is not implemented in single-type-classes")


class ctvData(BaseAction):

    def __init__(self, pin, value, captureDirection=None, burst=None):
        self.pin = pin
        self.value = value
        self.capdir = captureDirection
        self.burst = burst
        self.id_lno = get_caller_lno()

    def write(self):
        """Iterate on output of this object"""
        if self.capdir:
            line = f'<ctvData captureDirection="{self.capdir}" pin="{self.pin}" value="{self.value}"'
        else:
            line = f'<ctvData pin="{self.pin}" value="{self.value}"'
        if self.burst:
            line = f'{line} burst="{self.burst}"'
        line = f'{line}/>'
        yield line    # no indents on BaseAction, since indent is on caller


class triggerData(BaseAction):

    def __init__(self, name, type):
        self.name = name
        self.type = type

    def write(self):
        """Iterate on output of this object"""
        yield f'<triggerData type="{self.type}" name="{self.name}"/>'


class cycleData(BaseAction):

    def __init__(self, address, actions):
        self.address = address
        self.actions = actions

    def write(self):
        """Iterate on output of this object"""
        yield f'<cycleData address="{self.address}">'

        for item in self.actions:
            for line in item.write():
                yield f'{INDENT}{line}'

        yield f'</cycleData>'


class patternData(BaseAction):

    def __init__(self, pattern, domainData, actions):
        self.pattern = pattern
        self.domainData = domainData
        self.actions = actions
        self.id_lno = get_caller_lno()

    def is_single(self):
        """This class is not a single type"""
        return False

    @classmethod
    def write_main(cls, list_objs):
        """Main caller"""
        # get all unique first
        uniq = defaultdict(list)
        for obj in list_objs:
            if isinstance(obj, cls):
                uniq[obj.pattern].append(obj)

        # write it
        for key in uniq:
            yield f'<patternData pattern="{key}">'
            for line in cls.write_level5(uniq[key]):
                yield f'{INDENT}{line}'
            yield f'</patternData>'

    @classmethod
    def write_level5(cls, list_objs):
        """Main caller"""
        # get all unique first
        uniq = defaultdict(list)
        for obj in list_objs:
            uniq[obj.domainData].append(obj)

        # write it
        for key in uniq:
            yield f'<domainData name="{key}">'
            for obj in uniq[key]:
                for line in obj.write_level6():
                    yield f'{INDENT}{line}'
            yield f'</domainData>'

    def write_level6(self):
        """lowest level"""
        for obj in self.actions:
            for line in obj.write():
                yield line


class thermalData(BaseAction):

    def __init__(self, pin, value):
        self.pin = pin
        self.value = value

    def write(self):
        """Iterate on output of this object"""
        yield f'<thermalData pin="{self.pin}" value="{self.value}"/>'


class pinData (BaseAction):

    def __init__(self, pin, value, repeat=None):
        self.pin = pin
        self.value = value
        self.repeat = repeat

    def write(self):
        """Iterate on output of this object"""
        if self.repeat is not None:
            yield f'<pinData pin="{self.pin}" value="{self.value}" repeat="{self.repeat}"/>'
        else:
            yield f'<pinData pin="{self.pin}" value="{self.value}"/>'


class userVar (BaseAction):

    def __init__(self, name, value, type):
        self.name = name
        self.value = value
        self.type = type

    def write(self):
        """Iterate on output of this object"""
        yield f'<userVar name="{self.name}" value=\'{self.value}\' type="{self.type}"/>'


class portData (BaseAction):

    def __init__(self, port, status):
        self.port = port
        self.status = status

    def write(self):
        """Iterate on output of this object"""
        yield f'<portData port="{self.port}" status="{self.status}"/>'


class Comment (BaseAction):

    def __init__(self, comment):
        self.comment = comment

    def write(self):
        """Iterate on output of this object"""
        yield f'<!-- {self.comment} -->'


class simpleAuto(BaseAuto):
    """
    Reference class for Auto Injection

    This example will auto-port all instances that match this template
    """

    def __init__(self, template):
        self.template = template
        self.module = SetModule.get_module()
        self.id_lno = get_caller_lno()
        self.registry.append(self)

    def write(self):
        """Main writer - This takes care of writing the response blocks"""
        for mod, test, data in Merge.get_tpobj().mtpl.iter_flows('MAIN', bypass=True, edict=True):

            if mod != self.module:
                continue         # process only for this module
            if data['TEMPLATE'] != self.template:
                continue         # process only for this template

            yield f'<response testInstance="{mod}::{test}">'
            yield f'{INDENT}<flowResult>'
            yield f'{INDENT}{INDENT}<occurrence default="true"></occurrence>'
            yield f'{INDENT}</flowResult>'
            yield f'</response>'


class AutoIVCurve(BaseAuto):
    """
    Reference class for Auto Injection

    This example will auto-port all instances that match this template
    """

    def __init__(self, testinstance):
        self.testinstance = re.compile(to_regex(testinstance))
        self.template = self.__class__.__name__[4:]    # name of the class with "Auto" removed
        self.module = SetModule.get_module()
        self.id_lno = get_caller_lno()
        self.registry.append(self)

    def write(self):
        """Main writer - This takes care of writing the response blocks"""
        conversion_factors = {
            'A': 1,
            'V': 1,
            'v': 1,
            'mA': 1e-3,
            'ma': 1e-3,
            'nA': 1e-6,
            'na': 1e-6,
            'mV': 1e-3,
            'mv': 1e-3,
            'uA': 1e-6,
            'uV': 1e-6,
            'uv': 1e-6
        }
        for mod, test, data in Merge.get_tpobj().mtpl.iter_flows('MAIN', bypass=True, edict=True):

            if mod != self.module:
                continue         # process only for this module
            if data['TEMPLATE'] != self.template:
                continue         # process only for this template
            if not self.testinstance.search(test):
                continue         # process only testinstance that match

            tested_pins = re.split(r'[ ,]+', data['Pins'])
            lo_limits = re.split(r'[ ,]+', data['LowLimits'])
            hi_limits = re.split(r'[ ,]+', data['HighLimits'])
            yield f'<response testInstance="{mod}::{test}">'
            yield f'{INDENT}<dcResult>'
            yield f'{INDENT}{INDENT}<occurrence default="true">'
            for index, value in enumerate(tested_pins):
                lower_limit = None
                upper_limit = None
                matchlow = re.match(r'(-?\d*\.?\d+)([A-Za-z]+)', lo_limits[index])
                matchhigh = re.match(r'(-?\d*\.?\d+)([A-Za-z]+)', hi_limits[index])
                if matchlow:
                    valuel = float(matchlow.group(1))
                    unitl = matchlow.group(2)
                    if unitl in conversion_factors:
                        lower_limit = valuel * conversion_factors[unitl]
                else:
                    lower_limit = float(lo_limits[index])
                if matchhigh:
                    valueh = float(matchhigh.group(1))
                    unith = matchhigh.group(2)
                    if unith in conversion_factors:
                        upper_limit = valueh * conversion_factors[unith]
                else:
                    upper_limit = float(hi_limits[index])

                if lower_limit is not None and upper_limit is not None:
                    average = (lower_limit + upper_limit) / 2
                else:
                    raise ValueError("lower_limit or upper_limit not assigned a value for", mod, test, lo_limits[index], hi_limits[index])

                yield f'{INDENT}{INDENT}{INDENT}<pinData pin="{tested_pins[index]}" value="{average}"/>'
            yield f'{INDENT}{INDENT}</occurrence>'
            yield f'{INDENT}</dcResult>'
            yield f'</response>'


class AutoPrimeDcTestMethod(AutoIVCurve):
    pass


class AutoDcBinning(AutoIVCurve):
    pass


class AutoPort(BaseAuto):
    """
    Reference class for Auto Injection

    This example will auto-port all instances that match this template
    """

    def __init__(self, template, port=1):
        self.template = template
        self.module = SetModule.get_module()
        self.id_lno = get_caller_lno()
        self.registry.append(self)
        self.port = port

    def write(self):
        """Main writer - This takes care of writing the response blocks"""
        for mod, test, data in Merge.get_tpobj().mtpl.iter_flows('MAIN', bypass=True, edict=True):

            if mod != self.module:
                continue         # process only for this module
            if data['TEMPLATE'] != self.template:
                continue         # process only for this template

            yield f'<response testInstance="{mod}::{test}">'
            yield f'{INDENT}<flowResult>'
            yield f'{INDENT}{INDENT}<occurrence default="true">'
            yield f'{INDENT}{INDENT}{INDENT}<portData port="{self.port}" status="Pass"/>'
            yield f'{INDENT}{INDENT}</occurrence>'
            yield f'{INDENT}</flowResult>'
            yield f'</response>'


class AutoThermal(BaseAuto):
    """
    Auto inject thermal data based on the PinNames parameter of the instance and using temperature value from SCVars.SC_TEMPERATURE
    """

    def __init__(self, template):
        self.template = template
        self.module = SetModule.get_module()
        self.id_lno = get_caller_lno()
        self.registry.append(self)

    def write(self):
        """Main writer - This takes care of writing the response blocks"""
        for mod, test, data in Merge.get_tpobj().mtpl.iter_flows('MAIN', bypass=True, edict=True):

            if mod != self.module:
                continue         # process only for this module
            if data['TEMPLATE'] != self.template:
                continue         # process only for this template

            value = Merge.get_tpobj().usrv.get_var('SCVars.SC_TEMPERATURE')
            if 'PinNames' in data:
                td_pins = re.split(r'[ ,]+', data['PinNames'])
                yield f'<response testInstance="{mod}::{test}">'
                yield f'{INDENT}<thermalResult>'
                yield f'{INDENT}{INDENT}<occurrence default="true">'
                for pin in td_pins:
                    yield f'{INDENT}{INDENT}{INDENT}<thermalData pin="{pin}" value="{value}"/>'
                yield f'{INDENT}{INDENT}</occurrence>'
                yield f'{INDENT}</thermalResult>'
                yield f'</response>'
