#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Testplan module - https://wiki.ith.intel.com/display/ITSpdxtp/TP+testplans

Strategy:
1. Multiple py plans can be run as long as they are of the same prodstep.
   Reason: qbox can only process one die at a time.
2. One testprogram (one stpl and one location) per tp_plans.py run

TODO:
* multiple feature mismatch is displayed for the same xls row
* pattern audit based on bits (Feature2)
* to think: floating instance? (for spofi or QRE)... module only visibility

Feature2: pattern audit based on bits
Another one, audit based on bits.
"I expect to have 4 patterns with <tracebit_filters> ratio=400mhz core_ratio=10"
* ">80%" mismatch would make feature to be no-point

Completed items:
44. 12/20: eta feature
43. 12/20: hsd in csv
42. 12/13: IP and subplist
41. 12/12: Trust()
40. 12/7: ModWwaived - waiver as a way to show "F1" is all that's needed.
======
1. Error when Plan's name='chk*F1' found 2 or more matches in TP
   Reason is: one row in testplan is a physical testinstance in tpie or Torch
   That is, for speedflow: collapse the "speedflow field"
2. EDC/kill via setBin
3. Note: If TestPlan is EDC and testprogram is KILL, this is considered POR and no lost points.
4. Capability: edc vs kill result (POR and Enabled)
5. Really look at the parameters for voltage and freq
6. Feature1: tid audit based on linus/vault
======
7. Name is required, this is used to match... then if the attributes are not right, then no points on feature
8. change name SetPointsPreInstance to match .mtpl file
9. add TestMode=<value>
10. Fix the mismatch problem found in yesterday's demo
11. Improve printout and reason as to why Feature is missed
=======
12. voltage=<value>
13. look at failflow as well, but count this as feature miss if test is in failflow
14. failflow=True option in Plan()
15. global build time spec support
16. tid matching to include chunks
17. generic instance attributes
18. special level,timing map to level,levels,LevelsTc,etc
19. no feature point: when actual>expect, do not count more than expect
20. usrv=<value>
21. testname with speedflow collapse: keep the bin, but keep first occurrence only
22. Don't trigger content_expect if missing (This will be caught by review)
23. (drop) scan chunk num auto-grab. Use content_expect so it is a check and balance (We don't want to replicate pcar3 in plans)
24. csv rollup
25. Be able to run N plans
26. search passflow only first before searching failflow (found by James)
27. derive location from PrimarySocketLocn usrv (found by James)
28. summary tid expect add in csv. Waivers not included in .csv since it's fyi only during run.
29. per-module weightage - put in plan_settings.py. Add plan_settings.py in git (also waivers file)
30. fix formula sum(x/y)*weight)
31. Reorder of Sections; filename starts with number
32. Missing tp add tidexpect column; foundplan add enabled/por column
33. bypassed should be feature miss and not missing in tp
34. loc=sds option in Plan() so we can collapse common module (update CEP_gt.py). SetLocation()
35. updated wiki for commands, release to beta
36. missing modules (write in csv)
37. 9/24: global TP.loc(), so we can access location from plan code
38. 9/25: Two+ found should be MultipleMatch category
39. 9/29: Bucketing

Details: ====================================================
Feature1: tid audit based on linus/vault
Where is linus/vault set of tid used: <pcar-like-syntax> or tracebits
FastTest( name='CHK*F1', content_expect=4, linus='array_gt_gcd_lr_phase2')  # result to 11,12,13,14
case1: Actual TP showed: 25,26,27,14
Thus: 4 out of 4 rollup
      "feature" is 0 of 1 because tid mismatched
case2: Actual TP showed, 11,12,13
    3 out of 4 rollup
    "feature" is 1 of 1
* ">90%" tid mismatch would make feature to be no-point
"""

from gadget.tputil import remove_ip, tid_from_pat, to_regex, instancename_no_speed
from gadget.tputil import ti_disassemble, get_param, float_2_noerr, Units, is_number
from gadget.strmore import indent, curtime, to_list, wwno, regex_with_not
from gadget.pylog import log
from gadget.errors import ErrorInput
from gadget.files import File
from gadget.shell import CALLERBIN, SystemCall
from gadget.helperclass import IS_UT
from gadget.gizmo import get_caller_lno
from mod.querytid import qbox, _TidQueryBase, Funcs
from mod.querytid import QueryTid, SetProdStep, OR, AND, CONCAT, SUBTRACT    # Do not remove this line!
from mod.setting import cfg
from pprint import pprint
from os.path import basename, exists, dirname, abspath
from collections import defaultdict
from gadget.helperclass import OPT
import traceback
import re
import csv as csv_module
import os


class BasePlans:
    """Top level heirarchy of all plans"""

    def __repr__(self):
        """Representation of this object"""
        args = []
        for k, v in self.items(isname=False):
            if k == 'content_expect':     # don't print this by default
                continue
            if k == 'multiple_match' and v == 1:
                continue
            args.append(f'{k}={v}')

        return f"{self.__class__.__name__}('{self.name}', {', '.join(args)})"

    def items(self, isname=True):
        """Iterator: return an (item: value)"""
        if isname:
            yield 'name', self.name

        for item in self._attribs:
            val = getattr(self, item)
            if val:
                yield item, val

        if hasattr(self, 'kwargs'):
            kwargs = getattr(self, 'kwargs')
            for item in sorted(kwargs):
                yield item, kwargs[item]

    @classmethod
    def all_modules(cls):
        """
        Return set of all_modules in all plans
        Module may mor maynot be a valid TP module because of Trust
        """
        return {ti.module for ti in Plan.tiobj_list + Trust.tiobj_list}

    @classmethod
    def clear(cls):
        """Clear the class level variables for unittests"""
        Plan._clear()
        Trust._clear()
        ModuleName.clear()
        SetLocation.clear()
        TPName.clear()


class Plan(BasePlans):
    tiobj_list = []

    def __init__(self,
                 name=None,
                 voltage_corner=None,
                 freq=None,
                 corner=None,
                 content_expect=None,
                 edc=None,          # boolean
                 por=None,          # boolean
                 module=None,       # This will override ModuleName()
                 loc=None,          # This will override SetLocation()
                 tp=None,           # This will override TPName()
                 tid_expect=None,   # query object
                 voltage=None,
                 failflow=False,
                 usrv=None,
                 _utlno=None,       # unittest lineno
                 ip=None,           # ip name
                 hsd=None,          # string or list
                 subplist='',
                 por_plan='',       # string from .xls, passed to output
                 eta=None,          # This Plan() become "waived" if eta > TP_envfile_ww
                 multiple_match=1,  # Number of expected testinstance matches
                 blocked=None,      # boolean
                 chunk=None,
                 **kwargs           # The rest of the args
                 ):
        # lowercase/uppercase initialize. Note: Be sure to add in ignore_kwargs as well
        loc = kwargs.get('LOC', loc)
        ignore_kwargs = 'owner comment loc stepping'.split()   # it exist in xls

        # Start of initialize
        self.name = Funcs.check_regex_str('name', name, pseudo=True)
        self.voltage_corner = Funcs.check_string('voltage_corner', voltage_corner, valid='^v?(nom|min|max)$')
        self.freq = Funcs.check_string('freq', freq, valid=r"^(\d+|F\d)$")
        self.voltage = Funcs.check_string('voltage', voltage, valid='^[^=]+=[^=]+$')
        self.usrv = Funcs.check_string('usrv', usrv, valid='^[^=]+=[^=]+$')
        self.content_expect = Funcs.check_int('content_expect', content_expect, noneok=True)
        self.edc = Funcs.check_bool('edc', edc)
        self.por = Funcs.check_bool('por', por)
        self.corner = Funcs.check_string('corner', corner)
        self.tid_expect = tid_expect
        self.failflow = Funcs.check_bool('failflow', failflow)
        self.id_lno = _utlno if _utlno else get_caller_lno()     # caller line number, also used as id
        self.module = module if module else ModuleName.get_name()
        self.loc = loc if loc else SetLocation.get_name()
        self.tp = tp if tp else TPName.get_name()
        self.ip = Funcs.check_string('ip', ip)
        self.hsd = Funcs.check_all_string('hsd', to_list(hsd))
        self.subplist = Funcs.check_regex_str('subplist', subplist, pseudo=True)
        self.eta = Funcs.check_int('eta', eta, noneok=True)
        self.multiple_match = Funcs.check_int('multiple_match', multiple_match, noneok=False)
        self.por_plan = Funcs.check_string('por_plan', por_plan)
        self.blocked = Funcs.check_bool('blocked', blocked)
        self.kwargs = {k: v for k, v in kwargs.items() if k.lower() not in ignore_kwargs}
        self._origdict = {}

        # make sure all attributes are in for _repr_
        self._attribs = ('id_lno module content_expect blocked multiple_match loc voltage_corner freq corner voltage usrv edc por failflow '
                         'tid_expect ip hsd tp subplist eta por_plan').split()
        for item in vars(self):
            if item.startswith(('_', 'name', 'kwargs')):    # ignore these
                continue
            assert item in self._attribs, f'Cockpit Error: {item} is not registered in self._attribs. Pls fix code.'

        # check correctness
        assert name, "name='<instance_name_regex>' is required"
        assert self.module, f'No module name specified for {name}. Pls specify module.'
        msg = f'Invalid tid_expect={type(tid_expect)}. Expecting QueryTid type'
        assert (not tid_expect) or isinstance(tid_expect, _TidQueryBase), msg

        # Compiled attributes
        self.r_tp = re.compile(self.tp) if self.tp else None

        # register the object
        self.tiobj_list.append(self)
        log.info(f"-i- Registering {self}")

        # special attribute - chunk setting (one-time/singular
        if chunk:
            TPName.chunk[0] = int(float(chunk))

    def short(self):
        """Return the short name"""
        return f"{self.__class__.__name__}('{self.name}', id_lno={self.id_lno}, module={self.module})"

    def eval_vars(self, dd):
        """Update all attributes given dictionary"""
        attrdict = {x: getattr(self, x) for x in self._attribs}
        attrdict.update(self.kwargs)
        for item, val in attrdict.items():
            if not isinstance(val, str):
                continue

            # use original value. Need to use original variable since trialtest has different value MTT speedflow
            if item in self._origdict:
                val = self._origdict[item]
            else:
                self._origdict[item] = val

            if '{' not in val:
                continue

            # evaluate
            try:
                newval = val.format(**dd)
            except KeyError as e:
                newval = f"VARIABLE_NOT_DEFINED {e} in '{val}'"

            if item in self.kwargs:
                self.kwargs[item] = newval
            else:
                setattr(self, item, newval)

    def feature_match(self, ti_name, data, foundtid, planobj=None):
        """
        Feature match logic

        :param ti_name: testinstance name from testprogram
        :param data: testinstance dictionary
        :param foundtid: set of tid found in tp
        :param planobj: PlanReport object
        :return: "MATCH" for feature match or first non-match occurrence
        """
        # Logic here: Assume innocent until proven guilty

        # create lowercase data
        datalower = {k.lower(): v for k, v in data.items()}

        # re-eval the vars first
        if data and 'namefield' in data and planobj:
            inputdict = planobj.get_inputdict(data)
            self.eval_vars(inputdict)   # evaluate

        # special
        if self.voltage_corner and data['_CORNER'] != self.voltage_corner:
            return ('%s: voltage_corner mismatch [%s] vs tp:[%s]'
                    '' % (self.short(), self.voltage_corner, data['_CORNER']))
        if self.usrv:
            var, expect = self.usrv.split('=')
            res = planobj.tpobj.usrv.get_var(var, default='<NOT_IN_INSTANCE>')
            if res != expect:
                return ('%s: usrv mismatch %s=[%s] vs tp:[%s]'
                        '' % (self.short(), var, expect, res))

        # name-based
        if self.freq and data['namefield']['freq'] != self.freq:
            return ('%s: freq mismatch [%s] vs tp:[%s]'
                    '' % (self.short(), self.freq, data['namefield']['freq']))
        if self.corner and data['namefield']['corner'] != self.corner:
            return ('%s: corner mismatch [%s] vs tp:[%s]'
                    '' % (self.short(), self.corner, data['namefield']['corner']))

        # instance attributes
        for item in sorted(self.kwargs):
            itemlower = item.lower()

            # special
            val = self.kwargs[item]
            if itemlower in ('level', 'timing'):    # special, these map to multiple attributes
                expect = get_param(data, itemlower, default='<NOT_IN_INSTANCE>')
            else:
                if itemlower == 'testmode' and itemlower not in datalower:        # temporary because of default
                    expect = 'SingleVmin'
                else:
                    expect = datalower.get(itemlower, '<NOT_IN_INSTANCE>')

            if val == expect:
                pass     # proceed
            elif is_number(val) and is_number(expect) and float(val) == float(expect):
                pass     # proceed
            elif val == 'NOT_SET' and expect == '<NOT_IN_INSTANCE>':
                pass     # proceed
            elif val == 'NOT_SET' and expect == '':
                pass     # proceed
            else:        # val != expect:
                # failure in regex (because of preInstance line) is considered exact match
                try:
                    resultre = re.search(to_regex(val, exact=True), str(expect))
                    mismatch = (not resultre)
                except re.error:
                    mismatch = True

                if mismatch:
                    return ('%s: %s mismatch [%s] vs tp:[%s]'
                            '' % (self.short(), item, val, expect))

        # multiple_match
        cnt_mm = len(planobj.mmdd[(self.module, self.name)]) if planobj else 1
        if self.multiple_match != cnt_mm:
            if cnt_mm > 0 and self.multiple_match != -1:   # -1 means any number of matches
                found_names = sorted(x for _, x in planobj.mmdd[(self.module, self.name)])
                return ('%s: multiple_match mismatch: %s (Found) vs %s (Plan): %s'
                        '' % (self.short(), cnt_mm, self.multiple_match, ','.join(found_names)))

        # if    passflow                   and      instance is in failflow
        if (not self.failflow) and planobj and planobj.passfail[(self.module, ti_name)] == 'F':
            return '%s: is in failflow of testprogram' % self.short()

        # if    passflow                   and      instance is in failflow
        if planobj and planobj.passfail[(self.module, ti_name)] == 'B':
            return '%s: is bypassed' % self.short()

        # foundtid > content_expect
        if self.content_expect is not None and foundtid and len(foundtid) > self.content_expect:
            return f'{self.short()}: found tid {len(foundtid)} > content_expect {self.content_expect}'

        result = 'MATCH'
        result = self.analyze_voltage(result, get_param(data, 'level'), planobj)
        result = self.analyze_tid_expect(foundtid, result)

        return result

    def analyze_voltage(self, instr, level, planobj):
        """
        Analyze voltage

        :param instr: input string: Previous result
        :param level: levels string
        :return: new result
        """
        if not self.voltage:
            return instr    # do nothing

        var, expect = self.voltage.split('=')
        try:
            actual = planobj.tpobj.levels.get_tc_value(level, var)
        except Exception as e:
            return f'EXCEPTION on get_tc_value(): {e}'

        if float_2_noerr(actual) != float_2_noerr(expect):
            return ('%s: voltage mismatch [%s] vs tp:[%s]'
                    '' % (self.short(), float_2_noerr(expect), float_2_noerr(actual)))

        return instr

    def analyze_tid_expect(self, foundtid, instr):
        """
        Analyze tid_expect

        :param foundtid: set of tid's
        :param instr: input string: Previous result
        :return: original result for pass, string for fail
        """
        if not self.tid_expect:
            return instr      # tid_expect is not specified

        set_expect = set(self.tid_expect.result())
        result = {x[:7] for x in foundtid} - set_expect    # result is tid-list which are in TP but not in expect list
        if len(result) / len(set_expect) > 0.1:    # 10% or more mismatch

            # At this point, there are *extra* tids in tid_expect vs what is in testprogram
            resultstr = ','.join(sorted(result)[:10])       # first 10 only
            return ('%s: tid_expect extra_count=%s, Extra tid: %s'
                    '' % (self.short(), len(result), resultstr))

        return instr

    def is_eta(self, secs):
        """
        Returns True if This Plan() is waived based on eta setting

        :param secs: Testprogram env secs
        :return: bool
        """
        if self.eta is None:
            return False
        if self.eta > wwno(secs, year=True):
            return True
        return False

    @classmethod
    def _clear(cls):
        """Clear the class level variables for unittests"""
        cls.tiobj_list = []


class Trust(BasePlans):
    tiobj_list = []

    def __init__(self,
                 name,
                 sort=None,
                 sds=None,
                 sdt=None,
                 chot=None,
                 ccold=None,
                 module=None,
                 ip=None,
                 tp=None,
                 loc=None,
                 edc=None,
                 hsd=None,
                 _utlno=None,       # unittest lineno
                 ):
        self.name = Funcs.check_string('name', name)
        self.sort = Funcs.check_int('sort', sort, noneok=True)
        self.sds = Funcs.check_int('sds', sds, noneok=True)
        self.sdt = Funcs.check_int('sdt', sdt, noneok=True)
        self.chot = Funcs.check_int('chot', chot, noneok=True)
        self.ccold = Funcs.check_int('ccold', ccold, noneok=True)
        self.module = module if module else ModuleName.get_name()
        self.tp = tp if tp else TPName.get_name()
        self.ip = Funcs.check_string('ip', ip)
        self.loc = Funcs.check_regex_str('loc', loc)
        self.edc = Funcs.check_bool('edc', edc)
        self.hsd = Funcs.check_all_string('hsd', to_list(hsd))
        self.id_lno = _utlno if _utlno else get_caller_lno()     # caller line number, also used as id

        # make sure all attributes are in for _repr_
        self._attribs = 'sort sds sdt chot ccold id_lno module ip tp loc edc hsd'.split()
        for item in vars(self):
            if item.startswith(('_', 'name')):    # ignore these
                continue
            assert item in self._attribs, f'Cockpit Error: {item} is not registered in self._attribs. Pls fix code.'

        # register the object
        self.tiobj_list.append(self)
        log.info(f"-i- Registering {self}")

    def locations(self, dlocs):
        """
        Return set of valid locations for this object

        :param dlocs: {'sds': 'ALL_SDS', 'chot': 'CLASSHOT}
        :return: {'ALL_SDS': value}
        """
        result = {}
        for item in ('sort', 'sds', 'sdt', 'chot', 'ccold'):
            key = dlocs.get(item, item)
            val = getattr(self, item)
            if val:    # non-zero
                result[key] = val
        return result

    @classmethod
    def _clear(cls):
        """Clear the class level variables"""
        cls.tiobj_list = []


class SetLocation:
    """
    Location storage
    Unspecified location means Plan() is applicable to all locations
    Location is reset to None every plan.py file
    """
    location_name = [None]

    def __init__(self, name):
        """name is full location match (not a regex)"""
        self.location_name[0] = name

    @classmethod
    def get_name(cls):
        """Return the module name"""
        return cls.location_name[0]

    @classmethod
    def clear(cls):
        """Clear the module name"""
        cls.location_name[0] = None


class TPName:
    """
    TestProgramName storage
    Unspecified TPName means Plan() is applicable to all
    TPName is reset to None every plan.py file
    """
    tp_name = [None]
    chunk = [None]

    def __init__(self, name):
        """name is full location match (not a regex)"""
        self.tp_name[0] = name

    @classmethod
    def get_name(cls):
        """Return the module name"""
        return cls.tp_name[0]

    @classmethod
    def clear(cls):
        """Clear the module name"""
        cls.tp_name[0] = None


class ModuleName:
    """
    Module name storage
    Module name is reset every plan.py file

    Usage:
        ModuleName(<full_module_nameA>)
        Plan()   # This will use A
        Plan()   # This will use A
        ModuleName(<B>)
        Plan()   # This will use B
    """
    module_name = [None]    # list of one element

    def __init__(self, name, cdict=None):
        """
        Set the module name

        :param name: name is full module name match (not a regex). Default.
        :param cdict: Conditional dictionary for module name.
        Use TP.loc() or TP.name() since TP is populated early on.
            Format:
            {'<modulename>': True/False/Condition}
            Example:
            {'FUN_GT_GMD_SDT': TP.loc()=='ALL_SDT'}
        """
        if cdict:
            for key in cdict:
                if cdict[key]:
                    self.module_name[0] = key
                    return     # first occurrence

        # default
        self.module_name[0] = name

    @classmethod
    def get_name(cls):
        """Return the module name"""
        return cls.module_name[0]

    @classmethod
    def clear(cls):
        """Clear the module name"""
        cls.module_name[0] = None


class Waiver(BasePlans):
    """Waiver object"""
    wobj_list = []      # Waiver list is across many plan files

    def __init__(self, module, name, reason):
        self.module = module
        self.name = name
        self.reason = reason

        # make sure all attributes are in for _repr_
        self._attribs = 'module name reason'.split()
        for item in vars(self):
            if item.startswith('_'):    # ignore these
                continue
            assert item in self._attribs, f'Cockpit Error: {item} is not registered in self._attribs. Pls fix code.'

        self.r_name = re.compile(to_regex(self.name))
        self.wobj_list.append(self)    # register object

    @classmethod
    def is_waived(cls, ti_obj):
        """Returns True if ti_obj is part of waived"""
        for obj in cls.wobj_list:
            if obj.module != ti_obj.module:
                continue
            if obj.r_name.search(ti_obj.name):
                return True
        return False

    @classmethod
    def check_waivers(cls):
        """Checks if all waiver objects have some matching in TestPlan objects"""
        allmodules = BasePlans.all_modules()
        notfound = []
        for obj in cls.wobj_list:
            if obj.module not in allmodules:   # process only modules in this testplan
                continue
            for ti_obj in Plan.tiobj_list:
                if obj.r_name.search(ti_obj.name):
                    break
            else:
                notfound.append(f"{len(notfound)+1}. {obj}")

        if notfound:
            print("Waivers not found in this testplan:")
            print(indent(3, notfound))
            print()


class TP:
    """
    Holds TP info and various things for plan call
    """
    tpobj = [None]

    @classmethod
    def set_tp(cls, tpobj):
        """
        Set the testprogram object.
        This is called at the very start of tp_plans, even before any ctp files are imported

        :param tpobj: Testprogram object
        :return: None
        """
        cls.tpobj[0] = tpobj

    @classmethod
    def loc(cls, loc=None):
        """
        Returns True if loc (regex) matches location, if loc is specified
        Return location if loc is not specified
        """
        result = cls.tpobj[0].locset.location
        if loc:
            return bool(re.search(loc, result))
        else:
            return result

    @classmethod
    def name(cls, name=None):
        """
        Returns True if name (regex) matches TP name, if name is specified
        Returns TP name if name is not specified
        """
        result = cls.tpobj[0].get_name()
        if name:
            return bool(re.search(name, result))
        else:
            return result

    @classmethod
    def get_tp(cls):
        """Returns True if tpobj is set"""
        return cls.tpobj[0]


class ReportData:
    """
    Holds the data for PlanReport, do the counting and display it
    See PlanReport() for class heirarchy.
    """

    def __init__(self, tn_data):

        # (all, with-waived)
        self.num_content = [0, 0]           # numerator
        self.den_content = [0, 0]           # denominator
        self.num_feature = [0, 0]           # numerator, enabled (edc+kill)
        self.den_feature = [0, 0]           # denominator
        self.numpor_feature = [0, 0]        # numerator, POR (kill)
        self.numpor_content = [0, 0]        # numerator, POR (kill)

        self.trust_total = 0
        self.trust_por = 0
        self.trust_en = 0
        self.trust = {ENABLED: 0,
                      EDC: 0,
                      WIP: 0,
                      BLOCKED: 0}

        self.waive_list = []           # list of waived objects
        self.missing_tp_list = []      # missing in testprogram
        self.missing_plan_set = set()  # missing in plan
        self.feature_miss_list = []    # missing features
        self.tn_data = tn_data         # testname data structure

    def process_onetrust(self, ti, pr_obj):
        """
        Process one trust object and accumulate in data structure

        :param ti: Trust object
        :param pr_obj: PlanReport object
        :return: None
        """
        dloc = ti.locations(pr_obj.csv.get_setting('trust_locations'))
        tploc = pr_obj.tpobj.locset.location

        # Is this plan object specific for this location
        if ti.loc and not regex_with_not(ti.loc, tploc):
            print(f'-i- Skipping due to {ti.loc} != {tploc}: {ti}')
            return

        # Is this plan object valid for this location?
        if tploc not in dloc:
            print(f'-i- Skipping due to loc={tploc}: {ti}')
            return

        self.trust_total += 1
        value = dloc[tploc]
        if value in (ENABLED, WIP, BLOCKED):
            self.trust[value] += 1
        if value in (ENABLED, EDC, KILL):
            self.trust_en += 1
        if value == EDC and (not ti.edc):     # edc but not edc forever
            self.trust[value] += 1

        # por calculation
        por = 0
        if value == KILL or (value == EDC and ti.edc):
            por = 1
        self.trust_por += por

        modip = f'{ti.module} ({ti.ip})' if ti.ip else ti.module
        pr_obj.csv.add('TrustItem',
                       modip,
                       pr_obj.tpobj.locset.location,
                       value if value > 0 else '',
                       por,
                       ti.name,
                       1 if value == ENABLED else 0,
                       1 if value == EDC else 0,
                       1 if value == KILL else 0,
                       1 if value == WIP else 0,
                       1 if value == BLOCKED else 0
                       )

        # Add hsd
        for idx, hsd in enumerate(ti.hsd, start=1):
            pr_obj.csv.add('TrustHSD',
                           modip,
                           pr_obj.tpobj.locset.location,
                           idx,
                           len(ti.hsd),
                           ti.name,
                           hsd)

    def _plan_feature_match(self, md_tn, ti, pr_obj, nonwaived):
        """Process the plan if it is match or non-match"""
        foundtid, instance_dict = self.tn_data[md_tn]
        foundtid = self.get_subplist(foundtid, ti, instance_dict, md_tn, pr_obj)
        edckill = instance_dict.get('_EDCKIL')
        textwaive = '' if nonwaived else 'waived, '
        print(f'-i- found {edckill}={len(foundtid)} of {ti.content_expect}, {textwaive}{ti} {md_tn[1]}')

        try:
            match_str = ti.feature_match(md_tn[1], instance_dict, foundtid, pr_obj)
        except Exception as e:
            match_str = f"{ti.short()}: EXCEPTION: {ErrorInput.get_main_error(e)}"
            if not OPT.write:
                raise            # Raise exception on manual run
        return match_str, foundtid, edckill

    def process_oneplan(self, ti, pr_obj):
        """
        Process one plan object and accumulate in data structure

        :param ti: plan object
        :param pr_obj: PlanReport object
        :return: None
        """
        # Is this plan object valid for this location?
        if ti.loc and not regex_with_not(ti.loc, pr_obj.tpobj.locset.location) and (not OPT.check):
            print(f'-i- Skipping due to loc={pr_obj.tpobj.locset.location}: {ti}')
            return

        # Is this plan object valid for this tpname?
        if ti.tp and (not ti.r_tp.search(pr_obj.tpobj.get_name())) and (not OPT.check):
            print(f'-i- Skipping due to tp={pr_obj.tpobj.get_name()}: {ti}')
            return

        # Find the plan object in the testprogram
        md_tn = pr_obj.find_in_tp(ti, passflowonly='P')          # find in pass flow only (unless failflow=True)
        if md_tn is None:
            md_tn = pr_obj.find_in_tp(ti, passflowonly='F')      # try fail flow
        if md_tn is None:
            md_tn = pr_obj.find_in_tp(ti, passflowonly='B')      # try bypassed flow

        # is this waived?
        nonwaived = True
        if Waiver.is_waived(ti) or ti.is_eta(pr_obj.secs_tp):
            self.waive_list.append(ti)
            nonwaived = False

        # Do the counting
        content_expect = ti.content_expect if ti.content_expect else 0
        self.den_feature[0] += 1
        self.den_feature[1] += 1 if nonwaived else 0
        self.den_content[0] += content_expect
        self.den_content[1] += content_expect if nonwaived else 0

        # Force match for -check (CTP PR gate)
        if OPT.check and md_tn is None:
            for item in sorted(self.tn_data):
                md_tn = item                # last match, any will do

        if md_tn is not None:
            match_str, foundtid, edckill = self._plan_feature_match(md_tn, ti, pr_obj, nonwaived)

            # confirm that feature match for all of the instances
            if ti.multiple_match != 1:
                if match_str == 'MATCH':
                    for m_mod, m_name in sorted(pr_obj.mmdd[(ti.module, ti.name)]):
                        match_str, m_foundtid, _ = self._plan_feature_match((m_mod, m_name), ti, pr_obj, nonwaived)
                        if match_str != 'MATCH':
                            match_str = f'{match_str} [{m_name}]'
                            break
                else:
                    match_str = f'{match_str} [{md_tn[1]}]'     # add testinstance so it is not ambiguous

            if match_str == 'MATCH':
                feature_point = 1
            else:
                feature_point = 0
                self.feature_miss_list.append((match_str, md_tn[1]))

            # *Enabled* content (both edc and kill)
            por_en = 'En'
            self.num_content[0] += min(len(foundtid), content_expect)
            self.num_content[1] += min(len(foundtid), content_expect) if nonwaived else 0
            self.num_feature[0] += feature_point
            self.num_feature[1] += feature_point if nonwaived else 0

            # *POR* content (kill and edc-forever)
            if edckill == 'KIL' or ti.edc or ti.por:
                por_en = 'POR'
                self.numpor_content[0] += min(len(foundtid), content_expect)
                self.numpor_content[1] += min(len(foundtid), content_expect) if nonwaived else 0
                self.numpor_feature[0] += feature_point
                self.numpor_feature[1] += feature_point if nonwaived else 0

            if ti.blocked:
                por_en = 'BLK'

            modip = f'{ti.module} ({ti.ip})' if ti.ip else ti.module
            pr_obj.csv.add('FoundPlan', modip, len(foundtid), ti.content_expect, por_en, ti.por_plan, md_tn[1])

        else:
            self.missing_tp_list.append(ti)

        # Add hsd
        for idx, hsd in enumerate(ti.hsd, start=1):
            pr_obj.csv.add('PlanHSD',
                           modip,
                           idx,
                           len(ti.hsd),
                           '',
                           ti.name,
                           hsd)

    def get_subplist(self, foundtid, ti, instance_dict, md_tn, pr_obj):
        """
        Return set of tid, if subplist is defined

        :param foundtid: set of found tid
        :param ti: object
        :param instance_dict: testinstance dict
        :param md_tn: (module, tn)
        :param pr_obj: planreport object
        :return: set of found tid
        """
        if not ti.subplist:
            return foundtid    # Do nothing
        robj = re.compile(to_regex(ti.subplist))

        tids = set()
        if 'patlist' in instance_dict and pr_obj.passfail[md_tn] != 'B':
            patlist = instance_dict['patlist']
            plbfound = None
            for plb in sorted(pr_obj.tpobj.plists.get_subplists(patlist)):
                if robj.search(plb):
                    if plbfound:
                        print(f'-w- subplist={ti.subplist} found multiple matches: {plb} vs {plbfound}')
                        return set()

                    tids = {tid_from_pat(pat, chunk=True, pos=TPName.chunk[0])
                            for pat in pr_obj.tpobj.plists.get_pats_from_plb(plb, patonly=True, iserror=False)}
                    plbfound = plb

            if not plbfound:
                print(f'-w- subplist={ti.subplist} is not found in patlist={patlist}')
        else:
            print(f'-w- subplist is defined but instance is bypassed: {md_tn[1]} {ti}')
            tids = set()
        return tids

    def display(self, module, csv, ip):
        """
        Display data
        :param module: module name
        :param csv: csv object
        :param ip: ipname
        :return: None
        """
        txtip = f', IP={ip}' if ip else ''
        fip = ip if ip else module
        por_f = self.numpor_feature[0] + self.trust_por
        en_f = self.num_feature[0] + self.trust_en
        total_f = self.den_feature[0] + self.trust_total
        if self.den_content[0] == 0 and total_f == 0 and (not self.missing_plan_set):
            print()
            print(f'Nothing to display for {module}')
            print()
            return

        print()
        print(f'Result for {module}{txtip}:')
        print(f'   Content rollup POR:     {self.numpor_content[0]}/{self.den_content[0]}')
        print(f'   Content rollup Enabled: {self.num_content[0]}/{self.den_content[0]}')
        print(f'   Feature rollup POR:     {por_f}/{total_f}')
        print(f'   Feature rollup Enabled: {en_f}/{total_f}')
        print(f'   Feature found  Total:   {self.num_feature[0]+len(self.feature_miss_list)}/{self.den_feature[0]}')
        print()

        if len(self.waive_list):
            print('Result w/ waiver:')
            print(f'   Content rollup POR:     {self.numpor_content[1]}/{self.den_content[1]}')
            print(f'   Content rollup Enabled: {self.num_content[1]}/{self.den_content[1]}')
            print(f'   Feature rollup POR:     {self.numpor_feature[1]}/{self.den_feature[1]}')
            print(f'   Feature rollup Enabled: {self.num_feature[1]}/{self.den_feature[1]}')
            print()

            csv.add('ModWaived', module,
                    self.numpor_content[1], self.den_content[1],
                    self.num_content[1], self.den_content[1],
                    self.numpor_feature[1], self.den_feature[1],
                    self.num_feature[1], self.den_feature[1], fip)

        if self.trust_total:
            print(f'Trust Result for {csv.tpobj.locset.location}:')
            print(f'   Enabled Only: {self.trust[ENABLED]}/{self.trust_total}')
            print(f'   EDC Only:     {self.trust[EDC]}/{self.trust_total}')
            print(f'   POR:          {self.trust_por}/{self.trust_total}')
            print(f'   WIP:          {self.trust[WIP]}/{self.trust_total}')
            print(f'   BLOCKED:      {self.trust[BLOCKED]}/{self.trust_total}')
            print()
            csv.add('TrustSummary', module, self.trust_total,
                    self.trust[ENABLED],
                    self.trust[EDC],
                    self.trust_por,
                    self.trust[WIP],
                    self.trust[BLOCKED], fip)

        # write csv
        csv.add('ModSummary', module,
                self.numpor_content[0], self.den_content[0],
                self.num_content[0], self.den_content[0],
                self.numpor_feature[0], self.den_feature[0],
                self.num_feature[0], self.den_feature[0], fip)

        print('Missing from testprogram:')       # These are primary "feature" miss
        for idx, item in self.enumerate_print(self.missing_tp_list):
            is_waive = ' (WAIVED)' if item in self.waive_list else ''
            print(f'   {idx}. {item}{is_waive}')
            csv.add('MissingFromTP', item.module, None, item.content_expect, is_waive, str(item))
        print('')

        print('Missing from testplan:')
        for idx, item in self.enumerate_print(sorted(self.missing_plan_set)):
            corner = self.tn_data[item][1]['_CORNER']
            freq = self.tn_data[item][1]['_FREQ']
            tid = len(self.tn_data[item][0])
            print(f'   {idx}. {item[0]} {item[1]}: voltage_corner={corner} freq={freq} tid={tid}')
            csv.add('MissingFromPlan', item[0], tid, None, corner, item[1])
        print('')

        print('Feature misses:')                # These are secondary "feature" misses
        for idx, item in self.enumerate_print(self.feature_miss_list):
            print(f'   {idx}. {item[0]}')
            csv.add('FeatureMiss', csv.get_module(item[0]), None, None, item[1], item[0])
        print("")

    @staticmethod
    def enumerate_print(seq):
        """Iterator, Similar to enumerate() but prints None if seq is empty"""
        if len(seq) == 0:
            print('   None')
        else:
            for idx, item in enumerate(seq, start=1):
                yield idx, item


class PlanReport:
    """
    Process and Report out the test plans for ONE py file

    ## Usage and Heirarchy:
    tp = TestProgram()
    csv = CsvPlan()
    for each plan.py:
        pr = PlanReport(tp, csv=csv)
        <import plan.py>
        pr.main()    # ReportData() is instantiated here
    csv.write()
    """

    def __init__(self, tpobj, passfail=None, csv=None):
        BasePlans.clear()
        self.tpobj = tpobj
        self.secs_tp = os.path.getmtime(tpobj.envfile)
        self.passfail = passfail if passfail else tpobj.mtpl.dict_flows(flowitem=OPT.get('flows', 'MAIN'))
        self.tn_data = None
        self.vars = {}
        self.allfound = None    # assigned in main()
        self.allmodules = {}      # set, used by tp_plans, assigned in read_tp()
        self.csv = csv if csv else CsvPlan()
        self.mmdd = defaultdict(set)   # {md_tn: set(md_tn_found)}

    def readvars(self, module):
        """Read module, return dictionary for scalar values"""
        result = {}
        for item in dir(module):
            if item.startswith('_'):
                continue
            val = getattr(module, item)
            if isinstance(val, (str, int, float)):
                result[item] = val

        self.vars.update(result)

    def do_debug(self, debugplan):
        """
        Do -debugplan
        :param debugplan: {lno: instancename}
        """
        self.tn_data = self.read_tp()
        tn_data = self.tn_data
        print()
        print('Start debug ======')
        for id_lno, tname in debugplan.items():
            print()

            # get module first
            mod = None
            for ti in Plan.tiobj_list:     # Iterate to all testplan objects
                if ti.id_lno == int(id_lno):
                    print(f"Debug for: {ti}")
                    mod = ti.module
            assert mod, f'id_lno={id_lno} is not found in TestPlans. Refer to Registered items above'

            if (mod, f'{tname}_*') in tn_data:
                tname = f'{tname}_*'
            key = (mod, tname)

            msg = (f"Error: {mod}::{tname} not found in testprogram. "
                   f"If this is speedflow then remove the last field (speedflow 4 digit)")
            assert key in tn_data, msg

            print(f'Namefield for {tname}:')
            for k, v in sorted(tn_data[key][1]['namefield'].items()):
                print('   %-10s = %r' % (k, v))

            print(f'Data for {tname}:')
            for k, v in sorted(tn_data[key][1].items()):
                if k == 'namefield':
                    continue
                print('   %-10s = %r' % (k, v))

            for ti in Plan.tiobj_list:     # Iterate to all testplan objects
                if ti.id_lno == int(id_lno):
                    result = ti.feature_match(tname, tn_data[key][1], {}, planobj=self)
                    print(f"Match Result: {result}")

    def read_tp(self):
        """
        Read TP and return dictionary

        :return: tn_data {(mod, testname): (tids, data)}
        """
        tp = self.tpobj
        log.info(f"TP: {tp.get_name()}, {tp.envfile}, {basename(tp.get_stpl())}, {tp.locset.location}")

        # Get what is in TP - pass, fail and bypassed
        allmodules = BasePlans.all_modules()
        tn_data = {}      # {testname: (set_of_tid, data)}

        # First pass: Get all testnames first
        if not hasattr(tp, 'CACHE_ITER'):
            kwargs = dict(passonly=False, bypass=False, idict=True, edict=True)
            tp.CACHE_ITER = list(tp.mtpl.iter_flows_multi(OPT.get('flows', 'MAIN'), **kwargs))

        # Process tn_data
        for mod, item, data in tp.CACHE_ITER:
            if mod not in allmodules:
                continue

            if 'patlist' in data and self.passfail[(mod, item)] != 'B':
                plb = remove_ip(data['patlist'])
                tids = {tid_from_pat(pat, chunk=True, pos=TPName.chunk[0])
                        for pat in tp.plists.get_pats_from_plb(plb, patonly=True, iserror=False)}
            else:
                tids = set()

            # Refer to commit before 8/1/2023 for ctp with speedflow collapse algo
            key = item
            data_with_field = dict(data)
            data_with_field['namefield'] = ti_disassemble(key, isdict=True)
            tn_data[(mod, key)] = (tids, data_with_field)     # last instance will be taken in

        self.allmodules = allmodules
        return tn_data

    def get_inputdict(self, data):
        """
        Return the inputdict (variable dictionary from bin_matrix) used for evaluating vars
        :param data: testinstance dictionary
        :return: inputdict
        """
        inputdict = dict(self.vars)

        # Read binmatrix
        speedflow_bin = data['namefield'].get('speedflow', '')
        try:
            bm_dict = self.tpobj.bin_matrix(self.tpobj.get_bom())
        except KeyError as e:     # added this for sort TP which has binmatrix but they dont use
            log.info(f'-i- BinMatrix is not read for this TP. There is problem with BinMatrix: {e}')
            bm_dict = {}
        if bm_dict and not speedflow_bin:
            speedflow_bin = list(sorted(bm_dict))[-1]    # last one
        inputdict.update(bm_dict.get(speedflow_bin, {}))
        return inputdict

    def mhz_name_number(self, value):
        """
        If value ends with Hz, then convert to number and make it mhz for name replace from binmatrix.
        e.g. TRANS_PAR_*MAX_{GT_F1_FREQ}_*NORAM_GT$ where GT_F1_FREQ is 0.4GHz
             TRANS_PAR_*MAX_400_*NORAM_GT$
        :param value:
        :return: string containing number
        """
        if value.lower().endswith('hz'):
            return '%.f' % (1 / Units.to_number(value) / 1000000)
        return value   # as-is

    def find_in_tp(self, ti, passflowonly='P'):
        """
        Find ti (obj) in testprogram's tn_data

        :param ti: testinstance object
        :param passflowonly: Set to True for passflowonly
        :return: md_tn
        """
        found_md_tn = None
        tn_data = self.tn_data

        # evaluate if there are variables in name
        if '{' in ti.name:
            dd = {x: self.mhz_name_number(y) for x, y in self.get_inputdict({'namefield': {}}).items()}
            try:
                ti.name = ti.name.format(**dd)
            except KeyError as e:
                raise ErrorInput(f"Variable not defined: {e}, for name='{ti.name}'",
                                 "Make sure this variable is defined in the testplans or binmatrix.")

        r_name = re.compile(to_regex(ti.name))
        for md_tn in sorted(tn_data):
            # filters
            if md_tn[0] != ti.module:
                continue

            # 02/28/24: Commented this two lines since we can have multiple Plans() that match the same testinstance
            # if ti.subplist in self.allfound.get(md_tn, []):    # module, testname and subplist is found?
            #     continue     # process it once only!

            if self.passfail[md_tn] != passflowonly:
                continue     # skip

            # name match
            name_res = r_name.search(md_tn[1])
            if name_res:
                if ti.content_expect and 'patlist' not in tn_data[md_tn][1]:
                    continue      # Note: 'MissingFromTP' when content_expect is set but no patlist in testinstance
                self.mmdd[(ti.module, ti.name)].add(md_tn)
                self.allfound[md_tn].add(ti.subplist)
                found_md_tn = md_tn

        # return the last match
        return found_md_tn

    def summary_tid_expect(self):
        """
        Checks and summarizes all tid_expect vs content_expect
        """
        result = []
        for ti in sorted(Plan.tiobj_list, key=lambda x: x.id_lno):    # Iterate to all testplan objects
            if ti.tid_expect and ti.content_expect:
                tid_expect = len(set(ti.tid_expect.result()))
                if tid_expect / ti.content_expect < 0.9:
                    result.append('%s. Plan(id_lno=%s, content_expect=%s): tid_expect count=%s'
                                  '' % (len(result) + 1, ti.id_lno, ti.content_expect, tid_expect))
                    self.csv.add('TidExpectMiss', ti.module, tid_expect, ti.content_expect)

        if result:
            print("Large variation of tid_expect vs content_expect:")
            print(indent(3, result))
            print()

    def main(self):
        """Main entry for Plan Reports"""
        # Check if this plan is valid based on TPName
        if TPName.get_name() and not re.search(TPName.get_name(), self.tpobj.get_name()):
            print(f"-i- Skipping this plan file since TP name is not valid: "
                  f"{TPName.get_name()} vs {self.tpobj.get_name()}")
            return  # Do nothing

        # High level initializations
        self.tn_data = self.read_tp()
        qbox.process()                     # Process QueryTid objects

        # process per module
        for mod in sorted(BasePlans.all_modules()):
            self.allfound = defaultdict(set)
            allip = sorted({x.ip for x in Plan.tiobj_list + Trust.tiobj_list if x.module == mod})
            for ip in allip:
                res = ReportData(self.tn_data)     # result data structure

                # Iterate to all plan objects, do the counts: content and feature
                for planobj in sorted(Plan.tiobj_list, key=lambda x: x.id_lno):    # Iterate to all testplan objects
                    if planobj.module == mod and planobj.ip == ip:
                        res.process_oneplan(planobj, self)
                for trustobj in sorted(Trust.tiobj_list, key=lambda x: x.id_lno):    # Iterate to all testplan objects
                    if trustobj.module == mod and trustobj.ip == ip:
                        res.process_onetrust(trustobj, self)

                # calculate missing in testplan (in passflow)
                if ip == allip[-1]:   # last one only, since it must be accumulated for entire module
                    missing_set = {k for k in self.tn_data if 'patlist' in self.tn_data[k][1]}   # start with instances w/ patlist only
                    missing_set = {k for k in missing_set if k[0] == mod}
                    missing_set.difference_update(self.allfound.keys())          # remove found items
                    missing_set.difference_update({k for k, v in self.passfail.items() if v != 'P'})   # remove Fail and Bypass items
                    res.missing_plan_set = missing_set

                # display results
                res.display(mod, self.csv, ip)

        self.summary_tid_expect()
        Waiver.check_waivers()


class CsvPlan:
    """
    Write out the csv output file
    See PlanReport() for class heirarchy.

    Strategy:
    1. One .csv file per TP (Written in a specific dir)
    2. The .csv file for that TP will get written and re-written (aka, updated) on a per-module level
    """

    def __init__(self, tpobj=None, modwaiver=None, outfile=None):
        self.tpobj = tpobj
        self.items = []
        self.outfile = outfile
        self.mod2fname = {}
        self._modwaiver = modwaiver    # access via get_setting()

    def get_fname(self):
        if not self.tpobj:
            return None
        if self.outfile:
            return self.outfile
        secs = int(os.path.getmtime(self.tpobj.envfile) / 3600)
        fname = f'{secs}_{self.tpobj.get_name()}_{self.tpobj.locset.location}.csv'
        return f'{dirname(cfg.plan_waivers)}/outputs/{fname}'

    def get_team(self, module):
        """Return the team given the module"""
        return module.split('_')[0]

    def add(self, which, module, *data):
        """Add this data into the structure"""

        # Do not add if it is empty (eg, this plan file is skipped)
        if which == 'ModSummary' and sum(data[:-1]) == 0:
            return    # Do not append

        # Add this item
        self.items.append([which, module, self.get_team(module)] + list(data))

    def set_module(self, modules, planfile):
        """Assign module to planfile. Called from tp_plans.py"""
        for item in modules:
            self.mod2fname[item] = planfile

    def get_module(self, line, _re=re.compile(r"module=(\w+)")):
        """Return the module name from line"""
        res = _re.search(line)
        if res:
            return res.group(1)
        return "CANT_DERIVE_MODULE"

    def get_all_modules(self):
        """Return set of all modules"""
        mods = {k[1] for k in self.items}
        mods.discard('Module')
        return mods

    @staticmethod
    def read_csv(fname):
        """
        Read filename.csv

        :param fname: csv filename
        :return: list of rows
        """
        if not exists(fname):
            return []

        allcsv = []
        with open(fname) as fh:
            reader = csv_module.reader(fh)
            for row in reader:
                allcsv.append(row)
        return allcsv

    def div(self, val1, val2):
        """Return val1/val2 where val1 and val2 are string and val2 can be zero"""
        return int(val1) / max(int(val2), 1)

    def compute_summary(self, rows, weight_c, weight_f):
        """
        Calculate the sum
        If module is not defined in weight dictionary, then module is considered zero
        """
        result = []

        # SummaryTotal
        total = defaultdict(int)
        wtotal = defaultdict(int)
        for row in rows:
            if row[0] == 'Summary':
                for idx in (3, 4, 5, 6):    # content
                    total[idx] += int(row[idx])
                wtotal[34] += self.div(row[3], row[4]) * weight_c.get(row[1], 0)
                wtotal[56] += self.div(row[5], row[6]) * weight_c.get(row[1], 0)

                for idx in (7, 8, 9, 10):   # feature
                    total[idx] += int(row[idx])
                wtotal[78] += self.div(row[7], row[8]) * weight_f.get(row[1], 0)
                wtotal[91] += self.div(row[9], row[10]) * weight_f.get(row[1], 0)

        result.append(['SummaryTotal', None, None] + [total[idx] for idx in sorted(total)])

        # SummaryPct
        result.append(['WeightedPct', None, None,
                       None, '%.1f%%' % wtotal[34],    # C_POR
                       None, '%.1f%%' % wtotal[56],    # C_En
                       None, '%.1f%%' % wtotal[78],    # F_POR
                       None, '%.1f%%' % wtotal[91]])   # F_En

        # Do printout of modules with missing weights
        for mod in sorted(k[1] for k in rows if k[0] == 'Summary'):
            if mod not in weight_c:
                log.info(f'-w- [{mod}] does not exist in weight_content.')
            if mod not in weight_f:
                log.info(f'-w- [{mod}] does not exist in weight_feature.')

        sum_c = sum(v for v in weight_c.values())
        if sum_c != 100:
            log.info(f'-w- weight_content sum does not equal to 100: [{sum_c}]')
        sum_f = sum(v for v in weight_f.values())
        if sum_f != 100:
            log.info(f'-w- weight_feature sum does not equal to 100: [{sum_f}]')

        return result

    def timestamp_update(self, final):
        """Updates final (list) to have timstamps"""
        if not self.mod2fname:
            return  # Do nothing

        in_modules = self.get_all_modules()

        # remove TimeStamp+module in final
        delete = []
        for row in final:
            if row[0] == 'TimeStamp' and row[1] in in_modules:
                delete.append(row)
        for row in delete:
            final.remove(row)

        # Add TimeStamp+module
        for module in in_modules:
            lastmod = self.mod2fname[module]
            final.append(['TimeStamp', module, self.get_team(module),
                          curtime(), curtime(seconds=os.path.getmtime(self.mod2fname[module])),
                          File(self.mod2fname[module]).sha1(), basename(self.mod2fname[module])
                          ])

        # Add TP info
        final.append(['TimeStamp', '_TPNAME', 'INFO',
                      curtime(), curtime(seconds=os.path.getmtime(self.tpobj.envfile)),
                      'X', self.tpobj.envfile])
        final.append(['TimeStamp', '_REPO_EXE', 'INFO',
                      curtime(), 'X',
                      dirname(abspath(lastmod)), CALLERBIN])

    def missing_modules(self, final, pf):
        """Return missing Modules"""
        mod_existing = {x[1] for x in final if x[0] == 'ModSummary'}
        tid_cnt = defaultdict(set)
        tst_cnt = defaultdict(set)
        for md_tn in pf:
            if md_tn[0] in mod_existing:
                continue
            if pf[md_tn] != 'P':     # Look at pass flow only
                continue
            data = self.tpobj.mtpl.get_instance(*md_tn)
            if 'patlist' in data:
                plb = remove_ip(data['patlist'])
                tids = {tid_from_pat(pat, chunk=True, pos=TPName.chunk[0])
                        for pat in self.tpobj.plists.get_pats_from_plb(plb, patonly=True, iserror=False)}
                tid_cnt[md_tn[0]].update(tids)
            tst_cnt[md_tn[0]].add(md_tn[1])

        result = []
        for mod in tst_cnt:
            result.append(['MissingModule', mod, self.get_team(mod), len(tid_cnt[mod]), None, len(tst_cnt[mod])])
        return result

    def waive_modules(self, final):
        """Add modules if ModWaived exist"""

        # Check if there is ModWaived
        found = set()
        ref = {}
        for item in final:
            if item[0] == 'ModWaived':
                found.add(item[1])
            if item[0] == 'ModSummary':
                ref[item[1]] = item[1:]

        if not found:
            return []  # Nothing to do

        # Make sure all modules are there
        result = []
        for mod in ref:
            if mod not in found:
                result.append(['ModWaived'] + ref[mod])
        return result

    def get_setting(self, item, default=None):
        """Return the settings item from self._modwaiver. Default if not specified is a dictionary"""
        default = {} if default is None else default
        return getattr(self._modwaiver, item, default)

    def headers(self, final):
        """Add the headers"""
        sum_header = ('Module Team '
                      'C_POR_Actual C_POR_Expect '
                      'C_En_Actual C_En_Expect '
                      'F_POR_Actual F_POR_Expect '
                      'F_En_Actual F_En_Expect').split()
        mapping = {'Summary': ['HeadSummary'] + sum_header,
                   'ModSummary': ['HeadMod'] + sum_header + ['IP'],
                   'ModWaived': ['HeadModW'] + sum_header + ['IP'],
                   'MissingFromTP': 'HeadMissingTP   Module Team X          tid_expect is_waive Detail'.split(),     # pragma: no pep8 E241
                   'FoundPlan': 'HeadFound       Module Team tid_count  tid_expect PorEn POR_plan TestName'.split(),   # pragma: no pep8 E241
                   'MissingFromPlan': 'HeadMissingPlan Module Team tid_count  X          corner   Detail'.split(),     # pragma: no pep8 E241
                   'FeatureMiss': 'HeadFeatureMiss Module Team X          X          TestName    Detail'.split(),     # pragma: no pep8 E241
                   'TidExpectMiss': 'HeadTidExpect   Module Team tid_actual tid_expect'.split(),                     # pragma: no pep8 E241
                   'MissingModule': 'HeadMissMod     Module Team tid_count  X          TestInsCount'.split(),        # pragma: no pep8 E241
                   'MultipleFound': 'HeadMultiple    Module Team lineno     name       tid_expect    Detail'.split(),     # pragma: no pep8 E241
                   'TimeStamp': 'HeadTimeStamp   Module Team Date_Run   Date_PlanFile SHA_PlanFile PlanFile'.split(),  # pragma: no pep8 E241
                   'TrustSummary': 'HeadTrustSum Module Team Total Enabled EDC POR WIP Blocked IP'.split(),   # pragma: no pep8 E241
                   'TrustItem': 'HeadTrustItem Module Team Location  ETA POR  Item Enabled EDC Kill WIP Blocked'.split(),   # pragma: no pep8 E241
                   'TrustHSD': 'HeadTrustHSD Module Team Location index total Item HSD'.split(),
                   'PlanHSD': 'HeadPlanHSD Module Team index total X Name HSD'.split(),
                   }

        col_one = {x[0]: x for x in final}

        result = []
        for item in mapping:
            head = mapping[item][0]
            if head not in col_one and item in col_one:
                result.append(mapping[item])
                assert len(col_one[item]) == len(mapping[item]), f'{item} vs {head} length does not match!'

        return result

    def derive_summary(self, final, buckets):
        """
        Derive the summary rows by reading ModSummary and TrustSummary lines

        :param final: rows
        :param buckets: dictionary {'ARR': set_of_modules'}
        :return: Summary rows
        """
        mb = {}   # {module: <bucket>}
        for k, v in buckets.items():
            for module in v:
                assert module not in mb, f'{module} is defined twice in buckets'
                mb[module] = k

        # Add the rest of the modules, bucket by team
        allmods = {x[1] for x in final if x[0] in ('ModSummary', 'TrustSummary')}
        for module in allmods:
            if module not in mb:
                mb[module] = self.get_team(module)

        result = {}   # {module: <list_val>}
        for row in final:

            if row[0] == 'TrustSummary':
                #   Total Enabled EDC POR WIP Blocked
                #      3      4    5   6   7      8
                #                       por_act      por_exp      en_act                     en_exp
                data_add = [0, 0, 0, 0, int(row[6]), int(row[3]), int(row[5]) + int(row[6]), int(row[3])]
            elif row[0] == 'ModSummary':
                data_add = [int(x) for x in row[3:-1]]
            else:
                _ = 'pacify coverage only'
                continue    # ignore all other rows

            bucket = mb[row[1]]
            if bucket not in result:
                result[bucket] = [bucket] + data_add
            else:
                # add it
                for idx in (3, 4, 5, 6, 7, 8, 9, 10):
                    result[bucket][idx - 2] += data_add[idx - 3]

        return [(['Summary', k] + v) for k, v in result.items()]

    def write(self, iswrite, passfail={}):
        """
        Main entry point of this class.
        Write the final .csv.
        The .csv is like a database.
        One module run will update that module only, and then all summary rows are recalculated.

        :param iswrite: Set to True to write to csv. Normally, csv is not written (module owner run)
        :param passfail: passfail dictionary
        :return: None
        """
        fname = self.get_fname()
        if not fname:
            return     # Do nothing
        if not self.items:
            return 1   # Nothing to update
        if not iswrite:
            return 2   # Do not update

        # get modules in current run, remove this in .csv input file
        in_modules = self.get_all_modules()
        restcsv = []
        allcsv = self.read_csv(fname)
        for row in allcsv:
            if not row:
                continue    # empty rows
            if row[1] in in_modules:
                continue    # do not includes these modules
            if row[0] in ('Summary', 'SummaryTotal', 'WeightedTotal', 'WeightedPct', 'MissingModule'):
                continue    # These are automatically generated
            if row[0].startswith('Head'):   # So that newer header will be taken in, if there is a new header
                continue
            restcsv.append(row)

        # get settings
        cfg_buckets = self.get_setting('buckets')
        cfg_weight_content = self.get_setting('weight_content')
        cfg_weight_feature = self.get_setting('weight_feature')

        # manipulate
        final = restcsv + self.items                 # combine together
        self.timestamp_update(final)                 # update timestamps
        final.extend(self.derive_summary(final, cfg_buckets))   # create summary rows
        final.extend(self.compute_summary(final, cfg_weight_content, cfg_weight_feature))
        final.extend(self.missing_modules(final, passfail))   # missing modules
        final.extend(self.waive_modules(final))      # add modules which does not have waivers
        final.extend(self.headers(final))            # add the headers

        # sort order of section mapping
        sortmap = {'HeadSummary': '00',
                   'Summary': '01',
                   'SummaryTotal': '02',
                   'WeightedPct': '03',
                   'HeadMod': '05',
                   'ModSummary': '06',
                   'HeadModW': '07',
                   'ModWaived': '08',
                   'HeadTrustSum': '09',
                   'TrustSummary': '10',
                   'HeadMissingTP': '11',
                   'MissingFromTP': '12',
                   'HeadFeatureMiss': '20',
                   'FeatureMiss': '21',
                   'HeadMissingPlan': '30',
                   'MissingFromPlan': '31',
                   'HeadFound': '40',
                   'FoundPlan': '41',
                   'HeadTidExpect': '50',
                   'TidExpectMiss': '51',
                   'HeadMultiple': '55',
                   'MultipleFound': '56',
                   'HeadMissMod': '60',
                   'MissingModule': '61',
                   'HeadTrustItem': '62',
                   'TrustItem': '63',
                   'HeadPlanHSD': '64',
                   'PlanHSD': '65',
                   'HeadTrustHSD': '66',
                   'TrustHSD': '67',
                   'HeadTimeStamp': '70',
                   'TimeStamp': '71',
                   }
        final.sort(key=lambda x: f'{sortmap[x[0]]}{x[1]}')   # sort in place, Key is section->module

        # write it out
        mods = ', '.join(in_modules)
        log.info(f"-i- [{mods}] updated in {fname}")
        assert exists(dirname(abspath(fname))), f'Pls create {dirname(abspath(fname))} first with 2770 permissions.'
        with open(fname, 'w', newline='') as fh:
            csv_fh = csv_module.writer(fh, dialect='excel')
            for row in final:
                if row[0].startswith('Head'):
                    csv_fh.writerow([])   # empty
                csv_fh.writerow(row)
        File(fname).chmod('0660', ignoreError=True)

        # upload to Mongo db
        # upload_py = '/intel/tpvalidation/jqdelosr/apf_git/product_execution_status.rel/upload.py'
        # if (not IS_UT) and exists(upload_py):     # pragma: no cover   - dont upload to real db during unittest
        #     print("-i- Uploading to mongo db:")
        #     cmd = f'{upload_py} {fname}'
        #     _, out = SystemCall(cmd).run_outtxt()
        #     print(out)


# constants
ENABLED = -1     # This means this trust item is enabled (it works in standing die, but not in TP)
EDC = -2         # It's in TP but EDC
KILL = -3        # POR
DONE = -3        # same as POR
BLOCKED = -4     # i am blocked with issue
WIP = -5         # wip / in progress

# ==============================================================================================
#
# # Below are wiki cut and paste examples
#
# Plan( name='*F1*', content_expect=10,
#       tid_expect=QueryTid(attributes='west'))
#
#
# # ifpm_modifygroups = "bt!core_ratio_VAL_0_4GHz!0.5GHz,bt!ring_ratio!0.5GHz,bt!ratio_modify!RATIO4,at!";
#
#
# Plan( name='CHK*F1', freq_ifpm='VAL_0=0.5GHz', content_expect=10)
#
# # SetPointsPreInstance = "Mdrv:core_ratio_SCN:2.2GHz,Mdrv:ring_ratio_SCN:2GHz,MscnCore:mymainpatmod:setting";
#
#
# Plan( name='CHK*F1', SetPointsPreInstance='Mdrv:core_ratio_SCN:2.2GHz', content_expect=10)
#
