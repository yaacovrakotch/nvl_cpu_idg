#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Test plans tool

Basic Usage:
    tp_plans.py <plan1.py> ... -tp /tp_path/EnvironmentFile.env
Pipeline Usage:
    tp_plans.py <path_ctp_repo> -tp /tp_path/EnvironmentFile.env -pipeline
"""
import setenv      # must be first in the imports
from gadget.vepargs import Args, TA_All, TA_StoreTrue, TA_StoreFile, TA_Store, TA_KeyVal_CaseSensitive
from gadget.helperclass import OPT, EmptyContext, CaptureStdoutLog, IS_UT
from gadget.dictmore import DictDot
from gadget.tputil import log_usage, get_modulename
from gadget.strmore import sha1
from gadget.printmore import PrintAlign, Dumper
from gadget.errors import confirm, ErrorUser
from gadget.shell import SystemCall
from gadget.disk import Chdir, mkdirs
from gadget.files import File, TempName
from gadget.pylog import log
from gadget.getgit import GitHub, GetCmd
from os.path import exists, abspath, dirname, isdir, basename
from tp.testprogram import TestProgram, Env
from collections import OrderedDict
from mod.setting import cfg
from mod.plans import PlanReport, CsvPlan, TP, Plan, Waiver
import csv as csv_module
from importlib.machinery import SourceFileLoader
import re
import sys
import json
import glob
import os


# Below is a simple way to inform user if they are python version <3.5. This is checked before any other code during the Parsing phase.
f'If you see SyntaxError, this means your python version is old. Pls upgrade to python3.8 minimum: http://python.org/downloads'


class TPPlans(Args):   # parent: ArgsBase
    """
    TestProgram Info
    """

    def config(self):
        """
        Define the arguments for the script.
        The order below will matter, it is the order of display during help.
        """
        cfg = DictDot()
        cfg.all = TA_All('First arg is plan file')
        cfg.tp = TA_Store('CMD: Specify Testprogram', metavar='path/EnvironmentFile.env')
        cfg.summary = TA_StoreTrue('Show summary only. Used with -tid')
        cfg.out = TA_Store('Specify which file to write output csv', metavar='outfile.csv')
        cfg.stpl = TA_StoreFile('Specify stpl file', metavar='file.stpl')
        cfg.loc = TA_Store('Specify location', metavar='CLASSHOT')
        cfg.pgmrule_disp = TA_StoreTrue('Display pgmrule apply info')
        cfg.vars = TA_KeyVal_CaseSensitive('Specify Vars', metavar='SCVars.SC_REV=E')
        cfg.write = TA_StoreTrue("Write/Update to output csv")
        cfg.debugplan = TA_KeyVal_CaseSensitive('Debug testplan',
                                                metavar='<id_lno>=instance_name')
        cfg.disp_always = TA_StoreTrue("Display to screen even if 2 or more plans are given")

        cfg.csv = TA_StoreTrue("CMD: Display csv file formatted to screen. Even without -csv, it will work.")
        cfg.check = TA_StoreTrue("CMD: Check all json that is modified, used in runners")
        cfg.pipeline = TA_StoreTrue("CMD: Run CTP2 per PR, used in runners, arg1 is CTP repo path")
        cfg.frompr = TA_StoreTrue("CMD: Run CTP2 per PR, improved, used in runners, arg1 is .")
        cfg.gen = TA_Store('CMD: Generate the plan file based on existing TP', metavar='modulename')
        cfg.ctp2 = TA_Store('CMD: Generate the ctp2 .csv file based on given plan file', metavar='out.csv')
        cfg.flows = TA_Store('CMD: Specify which flows to iterate (comma-delimited), e.g. MAIN,INIT',
                             metavar='MAIN,INIT', default='MAIN,INIT')

        return cfg

    def main(self):
        """
        Main entry point of executable
        -h will not reach this method, since that is taken cared of in Args Base class
        """
        if OPT.check:
            self.do_check()
            return   # Done

        if not OPT.all:
            print("Error: First argument must be testplan file.")
            print("Usage: tp_plans.py <plan1.py> ... -tp /tp_path/EnvironmentFile.env")
            print("Execute 'tp_plans.py -h' for more info.")
            exit(0)

        # Because of github runners, wildcard expansion is not happening
        if '*' in OPT.all[0]:
            OPT.all = glob.glob(OPT.all[0])

        for ff in OPT.all:
            msg = f"{ff} does not exist. Expecting an existing plan file."
            assert exists(ff), msg

        # list of arg commands (will be translated to do_<argument>()
        log_usage('tp_plans', cfg)

        # Input arg is .csv file, display it's content
        if OPT.all[0].endswith('.csv'):
            self.do_csv()
            return

        # safety check on unittests
        assert not TP.get_tp(), 'Pls add "TP.set_tp(None)" at the top of the unittest routine.'

        self.call_methods(['pipeline',   # this will call do_pipeline(), if -pipeline
                           'frompr',     # this will call do_frompr(), if -frompr
                           'ctp2',     # this will call do_ctp2(), if -ctp2
                           'tp',       # this will call do_tp(), if -tp
                           'csv',      # this will call do_csv(), if -csv
                           'gen',      # this will call do_gen(), if -gen
                           ])          # do_else() is called if no argument command is processed

    def do_frompr(self):
        """See _frompr. This is try/except wrapper"""
        labels = GitHub.get_labels()
        log.info('-i- labels: %s' % ', '.join(sorted(labels)))
        try:
            self._frompr()
        except Exception as e:
            if 'CTP_Fail_Ignore' in labels:
                log.info(f'-i- CTP Failed with error: {e}')
                return
            raise     # re-raise

    def _frompr(self):
        """
        Run CTP2 from PR pipelines (newer way compared to -pipeline), since this include git clone

        # Input
        -tp <folder>/_PRNO_/<path>/Environment.env     # tpbuild path
        -out <dir>                     # <dir>/<prno>.csv is added

        # Output
        -tp <folder>/Environment.env   # Direct path
        -out <dir>/<prno>.csv          # specific file
        """
        prno = GitHub.get_prno()

        # Add the prno in path
        if '_PRNO_' in OPT.tp:
            confirm(prno, 'Cannot get pr number!', 'Pls check why')
            OPT.tp = OPT.tp.replace('_PRNO_', prno)

        if OPT.tp and (not exists(OPT.tp)):
            log.info(f'{OPT.tp} not exist, skipping ctp')
            return   # do nothing

        mkdirs(OPT.out)
        if prno:
            OPT.out = f'{OPT.out}/{prno}.csv'
        else:
            OPT.out = f'{OPT.out}/0.csv'     # on cases of workflow run

        # Display
        log.info(f'-i- -tp: {OPT.tp}')
        log.info(f'-i- -out: {OPT.out}')

        # clone repo
        SystemCall('git clone https://github.com/intel-restricted/ctp-mtl.git', disp=True).run_outtxt()

        # do pipeline
        OPT.all = ['ctp-mtl']
        self.do_pipeline()

        if prno:
            self.pr_comment()

    def pr_comment(self):
        """
        Run CTP2 from PR runner to add comments
        Will eventually call do_tp()
        """
        OPT.out = None            # no more output
        OPT.all = ['ctp-mtl']     # reset
        OPT.disp_always = True    # display even if modules is > 1

        # get the module names
        modnames = [get_modulename(x) for x in GitHub.get_modfiles()]
        restr = '|'.join(x for x in modnames if x)
        if restr:
            finalre = f'Modules.*({restr})'
        else:
            log.info("-i- pr_comment(): No valid module found from get_modfiles()")
            return

        # capture the output
        with CaptureStdoutLog() as p:
            self.do_pipeline(re_match=re.compile(finalre))

        # save in pr
        with TempName(name=True) as tname:
            text = self._prtext(p.getvalue())
            if text:
                File(tname).touch(text)
                SystemCall(GetCmd.exe(f'gh pr comment -F {tname}'), disp=True).run_sout_serr()

    @classmethod
    def _prtext(cls, text):
        """Transform stdout text to pr comment markup"""
        final = []
        for line in text.split('\n'):
            if line.startswith(('-i- Registering Plan',
                                '-i- found',
                                '-i- Skipping due to',
                                '-i- No ctp.txt found')):
                continue    # Skip these
            final.append(f'{line}<br>')

        if final and final != ['<br>']:
            return '<pre>%s</pre>' % ''.join(final)
        else:
            return ''

    def do_pipeline(self, re_match=re.compile('.')):    # match everything
        """
        Run CTP2 from PR runner
        Will eventually call do_tp()
        OPT.all[0] is path to ctp repo, which will be replaced
        """
        ctp_repo = OPT.all[0]
        with Chdir(ctp_repo):

            # get all the ctp.txt in TP module area
            confirm(OPT.tp, '[-tp <path_to_env>] is required', 'Pls fix args')
            jsons = set()
            root_tp = Env.get_root_dir(OPT.tp)
            all_ctp = (glob.glob(f'{root_tp}/Modules/*/ctp.txt') +
                       glob.glob(f'{root_tp}/Modules/*/*/ctp.txt') +
                       glob.glob(f'{root_tp}/Shared/Modules/*/*/ctp.txt')
                       )
            match_ctp = [x for x in all_ctp if re_match.search(x)]
            for ff in match_ctp:
                ctpfiles = list(File(ff).chomp(strip=True, comment='#'))
                confirm(len(ctpfiles) == 1,
                        f'Expecting 1 and only 1 line on: {ff}',
                        f'This file contain full path on ctp repo to the ctp file.')
                ctpfile = ctpfiles[0]
                confirm(ctpfile.endswith(('.xls', '.xlsx', '.json')),
                        f'Expecting either .json or .xlsx CTP file: {ctpfile}',
                        f'Check input: {ff}')
                target = ctpfile.replace('.xlsx', '.json').replace('.xls', '.json')
                if exists(target):
                    jsons.add(target)

            if not jsons:
                log.info(f'-i- No ctp.txt found from {root_tp}. Nothing to do. Exiting.')
                return

            OPT.all = sorted(jsons)
            log.info('-i- pipeline: %s' % ','.join(OPT.all))
            self.do_tp()

    def do_check(self):
        """Checks all modified json files and see if it works"""

        # check that committed .json are legit
        all_json = []
        for ff in GitHub.get_modfiles():
            if ff.endswith('.json') and exists(ff):
                with open(ff) as fh:
                    print(f"Check json syntax: {ff}")
                    json.load(fh)      # This will raise exception

                if not ff.startswith(('ProductConfig', 'CronConfig')):
                    all_json.append(ff)

        if not all_json:
            print('Nothing to check')
            return

        # Use a small TP
        OPT.tp = '/intel/tpvalidation/engtools/tptools/mtl/unittests/Simple3a/POR_TP/TGLH81/EnvironmentFile.env'

        # Check one at a time
        for ff in all_json:
            with Chdir(dirname(ff)):   # Correct plan_settings
                print(f"CHECKING: {ff}")
                OPT.all = [basename(ff)]
                self.do_tp()

    def do_ctp2(self):
        """Generate the ctp2 .csv file given .py"""
        confirm(len(OPT.all) == 1,
                f'Expecting one input file only from script. Input argument is: {OPT.all}',
                f'Pls specify one <plan>.py file in args.')
        confirm(OPT.tp,
                f'Expecting [-tp <path>/EnvironmentFile.env]',
                f'Pls specify testprogram path via -tp')
        plan = OPT.all[0]
        outcsv = OPT.ctp2.replace('.py', '')        # For automation, convert all

        # import the plan file
        tp = TestProgram(OPT.tp, stpl=OPT.stpl, location=OPT.loc, vars=OPT.vars).pickle_init()
        TP.set_tp(tp)
        sys.path.append(dirname(abspath(plan)))     # So that plans can import plan_settings
        SourceFileLoader(sha1(plan), plan).load_module()   # Plan.tiobj_list will be populated

        # get all the data from plan objects
        data = [OrderedDict(x.items()) for x in sorted(Plan.tiobj_list, key=lambda y: y.name)]   # list of dictionary

        # generate the final list of list
        final = []    # (raw) list of list, e.g. [['col1','col2','col3']]

        # header first
        head = []
        for dd in data:
            for key in dd:
                if key not in head:
                    head.append(key)
        final.append(head)

        # the rest of the rows
        for dd in data:
            row = []
            for item in head:
                row.append(dd[item] if item in dd else None)
            final.append(row)

        # write the csv
        with open(outcsv, 'w', newline='') as fh:
            csv_fh = csv_module.writer(fh, dialect='excel')
            for row in final:
                csv_fh.writerow(row)

    def do_gen(self):
        """Generate the plan file given TP"""
        # check first
        if OPT.out:
            assert isdir(OPT.out), f'[OPT.out] is not a directory. Expecting directory output'

        tp = TestProgram(OPT.all[0], stpl=OPT.stpl, location=OPT.loc, vars=OPT.vars).pickle_init()
        pfdata = tp.mtpl.dict_flows(flowitem=OPT.get('flows', 'MAIN'))

        if OPT.gen == 'ALL':
            mod_list = tp.mtpl.get_modules()
        else:
            mod_list = [OPT.gen]

        for mod in mod_list:
            lines = '\n'.join(self.gen_mod(tp, mod, pfdata))
            if OPT.out:
                fname = f'{OPT.out}/{mod}.py'
                with open(fname, 'w') as fh:
                    fh.write(lines)
                print(f'{fname} is generated')
            else:
                print(lines)

    @staticmethod
    def gen_mod(tp, module, pfdata):
        result = []
        result.append("from mod.plans import Plan, ModuleName")
        result.append(f"ModuleName('{module}')")
        result.append('')

        kwargs = dict(passonly=True, bypass=False, keyparam=None, idict=1)
        for mod, tname, data in tp.mtpl.iter_flows_multi(OPT.get('flows', 'MAIN'), **kwargs):
            if mod != module:
                continue

            # content_expect
            if 'patlist' in data:
                content_expect = f'content_expect=1, '

                try:
                    cnt = len(tp.plists.get_pats_from_plb(data['patlist']))
                except BaseException:
                    cnt = -1
                actual = f'  # found={cnt}'
            else:
                content_expect = ''
                actual = ''

            # vf - voltage and freq
            if data['TEMPLATE'] == 'VminTC':
                if 'TestMode' in data:
                    testmode = data['TestMode']
                else:
                    testmode = 'SingleVmin'
                if 'SetPointsPreInstance' in data:
                    vf = f"TestMode='{testmode}', SetPointsPreInstance='{data['SetPointsPreInstance']}'"
                elif 'PreInstance' in data:
                    res = re.search(r'ExecutePatConfigSetPoint\(([^\)]+)\)', data['PreInstance'])
                    if res:
                        vf = f"TestMode='{testmode}', PreInstance='{res.group(1)}'"
                    else:
                        vf = f"TestMode='{testmode}', PreInstance='{data['PreInstance']}'"
                else:
                    vf = f"TestMode='{testmode}', SetPointsPreInstance='tbd'"

            elif '_CORNER' in data:
                vf = f"level='*{data['_CORNER'].lower()}*'"
            else:
                vf = ''

            # add it
            pfb = f'   # Bypassed' if pfdata[(module, tname)] == 'B' else ''
            spc = ' ' * (65 - len(tname))
            result.append(f"Plan(name='{tname}$',{spc}{content_expect}{vf}) {actual}{pfb}")

        result.append('')
        return result

    def do_csv(self):
        """Display csv in screen"""
        rows = CsvPlan.read_csv(OPT.all[0])
        args = dict(header=False, rjust=False, space=0, sep=' ')
        pa = PrintAlign(**args)
        nth = False
        for row in rows + ['']:
            # print(row)
            if not row:
                if nth:
                    pa.disp(strip=True)
                    pa = PrintAlign(**args)
                print()
                continue

            pa(*row)
            nth = True

    @staticmethod
    def import_waiver(planfile):
        """
        Return the imported waiver/settings file

        Logic:
        1. Assume plan_settings.py exist parallel to planfile. Use this if exist
        2. Else, use return a fake module
        """
        target = f'{dirname(abspath(planfile))}/plan_settings.py'

        if not exists(target):
            class FakeModule:
                weight_content = {'mod': 10}
                weight_feature = {'mod': 5}
                buckets = {}
                Waiver('ARR', name='*B', reason='This is for unittest. Do not remove')
                Waiver('ARR1', name='CHK*FY', reason='Not possible for A0')
                UNITTEST_V1 = '2.7'
            return FakeModule      # Same as Empty module

        return SourceFileLoader(sha1(target), target).load_module()

    @staticmethod
    def isprint(inputs, isdisp):
        """Returns context manager class to suppress print or not"""
        if len(inputs) == 1 or isdisp:
            return EmptyContext()     # Do printout
        return CaptureStdoutLog(disp=False)

    @staticmethod
    def json_load(planjson, vard):
        """
        Return the plan module
        :param planjson: planjson file
        :param vard: plan settings variable dictionary
        :return: "mod" like object based on planjson
        """
        with open(planjson) as fh:
            data = json.load(fh)

        # generate the var for eval
        fvar = dict(vard)
        fvar.update({'TP': TP})

        for tab in data:
            idx = 0
            for row in data[tab]:
                idx += 1
                rowdata = {'_utlno': idx}

                # case sensitive vs case-insensitive
                caseinsensitive = ('name module failflow edc content_expect por_plan stepping '
                                   'multiple_match blocked'.split())
                for item in row:
                    # ignore these columns
                    if item.lower() in ['__placeholder__']:      # this is just placeholder
                        continue

                    # add the columns
                    if item.lower() in caseinsensitive:
                        rowdata[item.lower().strip()] = row[item].strip()
                    else:
                        rowdata[item.strip()] = row[item].strip()

                # ignore headers
                if rowdata.get('module', '').lower() == 'module':
                    continue   # ignore this row

                # integer fields
                for item in 'content_expect multiple_match'.split():
                    if item in rowdata:
                        rowdata[item] = int(eval(rowdata[item], fvar))

                # boolean fields
                for item in 'failflow edc blocked'.split():
                    if item in rowdata:
                        rowdata[item] = bool(eval(rowdata[item], fvar))

                # if
                for item in rowdata:
                    if isinstance(rowdata[item], str) and 'if ' in rowdata[item]:
                        rowdata[item] = eval(rowdata[item], fvar)

                # create the object
                assert 'name' in rowdata, \
                    (f'[name] column is missing or name column cannot be blank. check this record:\n'
                     f'{Dumper(rowdata, p=False).string()}')

                if OPT.check:
                    # check module
                    assert ' ' not in rowdata.get('module', ''), f"name={rowdata['name']} has invalid module=[{rowdata['module']}]"
                    rowdata['module'] = 'ARR'     # hardcode to a valid module on check tp. This is checked by unittest.

                Plan(**rowdata)

        return None

    def do_tp(self):
        """Report testplan"""
        if TP.get_tp():       # This routine can be called multiple times for the same tp
            tp = TP.get_tp()
        else:
            tp = TestProgram(OPT.tp, stpl=OPT.stpl, location=OPT.loc, vars=OPT.vars).pickle_init()
            TP.set_tp(tp)

        tp.mtpl.set_tn_attrib(reset=True, keyparam=None)    # include instances without patlist
        pf = tp.mtpl.dict_flows(flowitem=OPT.get('flows', 'MAIN'))      # This is for optimized run
        modwaiver = self.import_waiver(OPT.all[0])        # plan_settings.py
        sys.path.append(dirname(abspath(OPT.all[0])))     # So that plans can import plan_settings
        csv = CsvPlan(tp, modwaiver=modwaiver, outfile=OPT.out)

        for plan in OPT.all:
            print(f'Plan file: {abspath(plan)}')
            with self.isprint(OPT.all, OPT.disp_always):
                pr = PlanReport(tp, pf, csv)
                pr.readvars(modwaiver)

                # read the plan file
                if plan.endswith('.py'):
                    modplan = SourceFileLoader(sha1(plan), plan).load_module()
                    pr.readvars(modplan)
                elif plan.endswith('.json'):
                    self.json_load(plan, pr.vars)
                else:
                    raise ErrorUser(f'Unknown input file type: {plan}',
                                    f'Expecting <plan>.json')

                # main routine
                if OPT.debugplan:
                    pr.do_debug(OPT.debugplan)
                else:
                    pr.main()
                    csv.set_module(pr.allmodules, plan)

        csv.write(OPT.write or OPT.out, passfail=pf)
        return pr    # return last one for unittest


if __name__ == '__main__':  # pragma: no cover
    TPPlans(desc=__doc__).main()
