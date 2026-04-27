#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
cleantp module

# TODO: flw remove instances
"""
import re
from gadget.files import File, basename_n
from gadget.errors import ErrorInput, ErrorCockpit, confirm
from gadget.dictmore import xmlfunc, find_dot_items
from gadget.strmore import curtime
from gadget.disk import mkdirs
from gadget.pylog import log
from gadget.tputil import OtplFile, remove_ip, JsonRead
from gadget.gizmo import Elapsed
from gadget.helperclass import IS_UT
from datetime import datetime
from os.path import basename, exists, dirname
from tp.testprogram import TestProgram, Env
from collections import defaultdict
import json
import os
from pprint import pprint


class CleanTP:
    """
    CleanTP - https://wiki.ith.intel.com/display/ITSpdxtp/cleanTP
    Main class entry point
    """

    def __init__(self, tpobj: TestProgram):
        self.tpobj = tpobj

    @classmethod
    def revert(cls, tpobj):
        """
        FOR TESTING PURPOSES ONLY
        Reverts cleaned TCG files back to original uncleaned version
        """
        mod2fnames = tpobj.mtpl.get_mod2fname()

        for mod in mod2fnames:
            folder = dirname(mod2fnames[mod])
            for file in os.listdir(folder):
                # Revert TCGs
                if file.endswith(".tcg.orig"):
                    print(f'Reverting file {file}')
                    filename = file[:-5]
                    os.remove(f'{folder}/{filename}')
                    os.rename(f'{folder}/{file}', f'{folder}/{filename}')
                # Revert MTPLs
                if file.endswith(".mtpl.old"):
                    print(f'Reverting file {file}')
                    filename = file[:-4]
                    os.remove(f'{folder}/{filename}')
                    os.rename(f'{folder}/{file}', f'{folder}/{filename}')
        folder = dirname(tpobj.get_stpl())
        # Delete full report CSV
        csv_file = f'{folder}/Reports/Cleantp_fullreport.csv'
        if(exists(csv_file)):
            print(f'Removing file {csv_file}')
            os.remove(csv_file)
        # Revert ENV file
        for file in os.listdir(folder):
            if file.endswith('.env.old'):
                print(f'Reverting file {file}')
                filename = file[:-4]
                os.remove(f'{folder}/{filename}')
                os.rename(f'{folder}/{file}', f'{folder}/{filename}')

    @classmethod
    def add2summary(cls, tpobj, data):
        """
        Adds dictionary into cleantp.json file
        :Returns json data as a string for unit testing
        """
        json_data = {}
        folder = dirname(tpobj.get_stpl())
        if (exists(f'{folder}/Reports/Cleantp.json')) and (os.path.getsize(f'{folder}/Reports/Cleantp.json') > 0):
            with open(f'{folder}/Reports/Cleantp.json', 'r') as f:
                json_data = json.load(f)

        json_data.update(data)
        json_data_string = json.dumps(json_data, indent=4)

        with open(f'{folder}/Reports/Cleantp.json', 'w+') as f:
            f.write(json_data_string)

        return json_data_string

    @classmethod
    def add2fullreport(cls, tpobj, type, cleaned, dataset):
        """
        Adds granular clean/fat info to .csv file
        :Dataset - set OR list of (mod,testinst) tuples
        :Returns location of csv file for unit testing
        """
        folder = dirname(tpobj.get_stpl())
        csv_file = f'{folder}/Reports/Cleantp_fullreport.csv'
        header = 'Type, Module, Cleaned/Fat, Name, Owner\n'

        if (not exists(csv_file)) or os.path.getsize(csv_file) == 0:
            with open(csv_file, 'w') as f:
                f.write(header)

        with open(csv_file, 'a') as f:
            for item in dataset:
                if len(item) == 3:
                    line = f'{type}, {item[0]}, {cleaned}, {item[1]}, {item[2]}\n'
                else:
                    line = f'{type}, {item[0]}, {cleaned}, {item[1]}, \n'
                f.write(line)

        return csv_file

    @classmethod
    def init_optin(cls, tpobj):
        """
        Identify modules with optin file - called by CleanInstance and Cleanplist
        :Return set of MOD that have opted in
        """
        optin_modules = set()

        mod2fnames = tpobj.mtpl.get_mod2fname()
        # NVL - Check if “Shared/BaseInputs/InputFiles/cleantp_on_default.txt”. If this exist, then all modules are optin by default
        # If a module wants to opt out in NVL, MOs have to add tags to “Do not remove”

        trigger_from_env = tpobj.env.get_item('CLEANTP_TRIGGER', islist=False, default=f'{tpobj.tpldir}/Shared/BaseInputs/InputFiles/cleantp_on_default.txt')
        trigger_from_env = trigger_from_env.replace('~HDMT_TPL_DIR', tpobj.env.get_hdmt_tpl_dir())
        trigger_from_env = trigger_from_env.replace('~HDMT_TP_BASE_DIR', tpobj.env.get_hdmt_tpl_dir())
        if File(Env.xpath(trigger_from_env)).exists() or exists(f'{tpobj.tpldir}/Shared/BaseInputs/Inputs/cleantp_on_default.txt'):
            optin_modules = set(mod2fnames.keys())
        else:  # ARL - will still do the OPTIN method by MOs
            for mod in mod2fnames:
                folder = dirname(mod2fnames[mod])
                if exists(f'{folder}/cleantp_enable.txt'):
                    optin_modules.add(mod)

        print(f'-i- Total cleantp optin modules: {len(optin_modules)} of {len(mod2fnames)}')
        report = {"modules": {"opt-in": len(optin_modules), "total": len(mod2fnames)}}
        CleanTP.add2summary(tpobj, report)

        return optin_modules

    @classmethod
    def get_value_tosrule(cls, tpobj: TestProgram, param, testplan, _robj=re.compile(r'\((?!.*HDMT_TP_BASE_DIR)([^)(]+)\)')):  # Added to process TOS rule correctly when HDMT_TP_BASE_DIR is specified
        """
        Given some test instance param, identify if tos rule is present and return all values inside
        :Return list of params
        """
        get_tos_rules = _robj.findall(param)
        evaluated_params = []
        if len(get_tos_rules) != 0:
            for item in get_tos_rules[0].split(','):
                if '"' in item:
                    evaluated_params.append(item.strip().replace('"', ''))
                else:
                    evaluated_params.append(tpobj.usrv.eval_param(item, testplan))
            return evaluated_params
        else:
            if '.' in param:
                try:
                    return [tpobj.usrv.eval_param(param, testplan, is_print=False)]
                except ErrorInput:
                    return [param]
            return [param]

    def main(self):
        """Main Entry point"""
        sw = Elapsed()

        # Test Instance Removal
        cleaninst = CleanInstance(self.tpobj)
        cleaninst.main()

        # Reload
        self.tpobj = TestProgram(self.tpobj.envfile, allpats=True).init()

        # Plist Removal
        cplist = CleanPlist(self.tpobj)
        cplist.main()
        CleanPPR(self.tpobj).main()

        # TCG Removal
        tcg = CleanTCG(self.tpobj)
        tcg.main()

        # Confirm TP is still good
        print('===== confirming that TP is good')
        self.tpobj = TestProgram(self.tpobj.envfile, allpats=True).init()
        log.info(f'-z- CleanTp() Total Elapsed: {sw}')


class CleanInstance:
    """
    Class that takes care of unused instances
    """
    all_flows = 'INIT MAIN LOTENDFLOW LOTSTARTFLOW TESTPLANENDFLOW TESTPLANSTARTFLOW DUTCHANGEFLOW'.split()  # added for sort support to process EZA test

    floating_instance_call = {'PerPartitionExecution': 'InstanceNameToExecute', 'VminTC': 'PostInstance'}  # added support to look for such tests to make sure to not delete them since they are floating

    def __init__(self, tpobj: TestProgram):
        self.tpobj = tpobj
        self.stats = {'rewrite_instance_files': 0}
        self.optin = set()

    def main(self):
        self.optin = CleanTP.init_optin(self.tpobj)
        # part1 - test instances
        self.do_instances()

    def do_instances(self):
        """Identify instances to be removed"""
        os.chdir(self.tpobj.tpldir)

        log.info('-i- Test Instance stats:')

        # get all instances
        everything = self.get_everything()

        # get all connected
        connected = self.get_connected()

        # get all floating
        floating = everything - connected

        # get all connected and hardcoded bypass
        bypassed = self.get_hardcoded_bypassed()

        # total remove
        remove_all = floating | bypassed

        # get all no remove
        no_remove = self.get_dedc_evg(remove_all)
        no_remove |= self.get_dedc_prime(remove_all)
        no_remove |= self.get_pgmrules(remove_all)

        # get all noclean
        no_clean = self.get_noclean()
        no_remove |= no_clean

        # cannot remove first items in dutflow (because of wiring or if it's single instance Return)
        no_remove |= self.get_first_dutflow(bypassed)

        # get all RunCallBack tests that are floating when its Callback used is 'JsonRun' and dependent tests found in Json file
        runcallback_not_remove = self.get_runcallback(remove_all - no_remove)

        # Exclude RunCallBack tests that are floating from Total Floating tests to be considered for cleanup
        # runcallback_filter = remaining_remove - runcallback_not_remove
        no_remove |= runcallback_not_remove

        # Exclude PrimePinProfilerTestMethod template - new in NVL
        prime_pinprofiler_not_remove = self.get_prime_pinprofilerTM()
        no_remove |= prime_pinprofiler_not_remove

        # Exclude Floating tests from removal
        floating_tests_not_remove = self.get_floatingInstance_invoked_by_activeTests(remove_all - no_remove)
        no_remove |= floating_tests_not_remove

        # leave first dutflowitem for empty dutflow blocks.
        no_remove |= self.get_empty_dutflow(remove_all)

        # You must calculate remaining fat from remaining remove to not include dedc, first
        remaining_remove = remove_all - no_remove

        # update all mtpl given instances to be removed
        removed = set()
        removed_report = set()   # to keep track of removed instances for reporting, with owner info if available, as (mod, ti, owner)
        mod2fname = self.tpobj.mtpl.get_mod2fname()
        for module in sorted(set(x[0] for x in everything)):
            if module in self.optin:
                module_path = mod2fname.get(module, None)  # to raise error if module is missing from mod2fname mapping
                if module_path is None:
                    continue

                owner = ''
                owner_file = os.path.join(dirname(module_path), 'owner.txt')
                if os.path.exists(owner_file):
                    with open(owner_file, 'r') as file:
                        for line in file:
                            if re.search(r'\s*owner\s*:', line.strip(), re.IGNORECASE):
                                owner = line.split(':', 1)[1].strip()
                                break
                else:
                    log.info(f'-i- owner.txt not found for module {module} at expected location {owner_file}. Owner info will be blank for this module in the report.')

                fname = module_path
                self.remove_instances(fname, module, remove_all, no_remove)
                removed.update({(md, ti) for md, ti in (remove_all - no_remove) if md == module})
                removed_report.update({(md, ti, owner) for md, ti in (remove_all - no_remove) if md == module})

        remaining_fat = remaining_remove - (removed | (no_clean & remove_all))

        # Add cleaned test instances to CSV
        CleanTP.add2fullreport(self.tpobj, "TestInstance", "Cleaned", removed_report)
        # Add fat (not cleaned, but identified as fat to clean) to CSV
        CleanTP.add2fullreport(self.tpobj, "TestInstance", "Fat", remaining_fat)

        ti_report = {
            "instances": {
                "total": len(everything),
                "noclean": len(no_clean),
                "cleaned": len(removed),
                "remaining_fat": len(remaining_fat)
            }
        }

        CleanTP.add2summary(self.tpobj, ti_report)

        # write stats
        self.stats['everything'] = len(everything)
        self.stats['connected'] = len(connected)
        self.stats['floating'] = len(floating)
        self.stats['bypassed'] = len(bypassed)
        self.stats['no_remove'] = len(no_remove)

        log.info(f'-i- Count of all instances:   {len(everything)}')
        log.info(f'-i- Count of connected:       {len(connected)}')
        log.info(f'-i- Count of floating:        {len(floating)}')
        log.info(f'-i- Count of hardcode bypass: {len(bypassed)}')
        log.info(f'-i- Count of no_remove:       {len(no_remove)}')

    def get_connected(self):
        """
        Return set of connected instances
        :Return set of (mod, tname)
        """
        connected = set()
        for flow in self.get_all_flows():
            connected.update((mod, tname) for mod, tname in self.tpobj.mtpl.iter_flows(flow, bypass=False))
        return connected

    def get_everything(self):
        """
        Return set of all test instances
        :Return set of (mod, tname)
        """
        return {(mod, tname) for mod, tname, _, _ in self.tpobj.mtpl.iter_tests()}

    def get_noclean(self):
        """Return set of all test instances with # NOCLEAN tag"""

        noclean_instances = set()
        comments = {}
        regex_match = re.compile(r'# REGEX_NOCLEAN:\s*(.*)')
        ti_set = self.tpobj.mtpl.iter_tests()

        folder2mods = self.tpobj.mtpl.get_modfolder2mod()
        for file in self.tpobj.get_all_mtpl_from_stpl():
            regex_list = []
            mod = folder2mods[basename(dirname(file))]
            comments = self.tpobj.mtpl.read_comments(file)[0]
            for instance, inst_cmnts, in comments.items():
                if "# NOCLEAN" in inst_cmnts:
                    noclean_instances.add((mod, instance))
                for cmnt in inst_cmnts:
                    match = regex_match.search(cmnt)
                    if match:
                        regex_list.append(match.group(1))
            if regex_list:
                for ti in ti_set:
                    if ti[0] == mod:
                        for rgx in regex_list:
                            match = re.search(rgx, ti[1])
                            if match:
                                noclean_instances.add((mod, ti[1]))

        return noclean_instances

    def get_all_flows(self):
        """Return all valid flows"""
        all_subflows = self.tpobj.mtpl.get_subflows()
        for item in self.all_flows:
            if item in all_subflows:
                yield item

    def get_empty_dutflow(self, to_remove):
        """
        Return first instance in dutflow if dutflow block is empty

        :param to_remove: all instances to be removed
        :return: set (module, tname
        """
        # This is only for mtl and evergreen. empty dutflow is ok on 100% prime.
        # opportunity to remove this routine later, if we are 100% prime and cleantp is still bin1
        df = self.tpobj.mtpl.get_dutflow_map()    # {'module::subflow': {_ORDER: ['list of dfi'], dfi: {999: testinstancename}
        final = set()
        for subflow in df:
            mod = subflow.split(':')[0]
            firstitem = None
            for dfi in df[subflow]['_ORDER']:
                item = (mod, df[subflow][dfi][999])   # (mod, ti)
                if not firstitem:
                    firstitem = item
                if item not in to_remove:
                    break    # it is not empty
            else:
                # at this point dutflow is empty
                final.add(firstitem)

        log.info(f'-i- Count of emptydutflow no_remove: {len(final)}')
        return final

    def get_first_dutflow(self, to_remove):
        """
        Return all first instances in dutflow for all modules that's in to_remove
        to_remove is hardcoded bypass list
        Reason: first instances have two corner cases:
            #1 The next dutflowitem is not necessarily port1, so you have to move the port1 instance to top (complex)
            #2 If first dutflowitem can have port1 to be Return. If so, then need to remove the entire dutflow block

        :return: set (module, tname)
        """
        df = self.tpobj.mtpl.get_dutflow_map()   # {'module::subflow': {_ORDER: ['list of dfi'], dfi: {999: testinstancename}
        final = set()
        for subflow in df:
            mod = subflow.split(':')[0]

            # some DutFlow block is empty (eg. 66B0B, ARR_COMMON_GXX module, ARR_COMMON_GXX_INIT)
            if not df[subflow]['_ORDER']:    # pragma: no cover
                continue

            dfi = df[subflow]['_ORDER'][0]
            item = (mod, df[subflow][dfi][999])    # (mod, ti)
            if item in to_remove:
                final.add(item)

        log.info(f'-i- Count of firstdfi no_remove: {len(final)}')
        return final

    def get_dedc_evg(self, remove_all):
        """
        Get all dedc instances that we cant remove because init will fail
        :return: set of (mod, instance)
        """
        ffile = set()
        for mod, tname, dd in self.tpobj.mtpl.iter_flows('MAIN', edict=True, keyparam='config_file', template='iCDEDCTest'):
            if not File(dd['config_file']).exists() or str(dd.get('bypass_global', dd.get('BypassPort', None))) == "1":
                continue
            else:
                ffile.add(dd['config_file'])

        final = set()
        for fname in sorted(ffile):
            data = xmlfunc.xml2dict(fname)
            for item in find_dot_items(data, regex=r'(Segment.*name|Segment)\b', default=[]):
                if '::' in item:
                    elems = item.split('::')
                    final.add((elems[-2], elems[-1]))

        log.info(f'-i- Count of dedc_evg: {len(final)}, no_remove_count: {len(remove_all & final)}')
        return final

    def get_dedc_prime(self, remove_all):
        """
        Get all dedc instances that we cant remove because init will fail
        :return: set of (mod, instance)
        """
        ffile = set()
        for mod, tname, dd in self.tpobj.mtpl.iter_flows('INIT', edict=True, keyparam='ConfigFile', template='DedcLoadConfigTC'):
            if dd['ConfigFile']:
                if self.tpobj.is_tos4 and not exists(Env.xpath(dd['ConfigFile'])):  # TOS4 and for cases when path is not resolvable
                    # some modules have DEDC json path
                    # (A)--> ConfigFile = GetEnvironmentVariable("~HDMT_TP_BASE_DIR")+"./Modules/PCD/SCN_PCD_PKS/InputFiles/dedc_callback_all.json";
                    if len(dd['ConfigFile'].split('Modules')) > 1:
                        fpath = dd['ConfigFile'].replace("./Modules", "/Modules")
                        ffile.add(fpath.replace("\\", "/"))
                    else:  # (B)--> ConfigFile = "InputFiles/dedc_callback_all.json";
                        fpath = os.path.dirname(self.tpobj.mtpl.get_mod2fname()[mod]) + '/' + dd['ConfigFile']
                        ffile.add(fpath.replace("\\", "/"))
                else:  # TOS3
                    ffile.add(Env.xpath(dd['ConfigFile']))

        final = set()
        for fname in sorted(ffile):

            # some json are not existing, as found in 66B0B TP.
            if not exists(fname):      # pragma: no cover
                continue

            for item in re.findall(r'"Name":\s*"(\S+::\S+)\"', File(fname).read()):
                confirm('::' in item, f'[{item}] found in {fname}', 'Expecting Module name separated by ::')
                elems = item.split('::')
                final.add((elems[-2], elems[-1]))

        log.info(f'-i- Count of dedc_prime: {len(final)}, no_remove_count: {len(remove_all & final)}')
        return final

    def get_runcallback(self, removable):
        """
        Get all Floating/not-floating RunCallBack instances that we can't remove because it could be called by other tests connected in the flow
        :return: set of (mod, instance)
        """
        not_remove = set()
        ffile = set()
        for mod, tname, dd, _ in self.tpobj.mtpl.iter_tests(template_name='RunCallback', edict=False):
            if 'Callback' in dd and 'JsonRun' in dd['Callback']:
                not_remove.update({(mod, tname)})  # if RunCallback template is floating then exclude from cleanup
                for item in CleanTP.get_value_tosrule(self.tpobj, str(dd['Parameters']), mod):  # adding to process TOS Rules if present
                    if self.tpobj.is_tos4 and not exists(Env.xpath(item)):  # TOS4 and for cases when path is not resolvable
                        # (A)--> ConfigFile = GetEnvironmentVariable("~HDMT_TP_BASE_DIR")+"./Modules/PCD/SCN_PCD_PKS/InputFiles/dedc_callback_all.json";
                        if len(item.split('Modules')) > 1:
                            fpath = item.replace("./Modules", "/Modules")
                            ffile.add(fpath.replace("\\", "/"))
                        elif item != '':  # (B)--> ConfigFile = "InputFiles/dedc_callback_all.json";
                            fpath = os.path.dirname(self.tpobj.mtpl.get_mod2fname()[mod]) + '/' + item
                            ffile.add(fpath.replace("\\", "/"))
                    else:  # TOS3
                        ffile.add(Env.xpath(item))

        for fname in sorted(ffile):
            # some json are not existing, as found in 66B0B TP.
            if not exists(fname):      # pragma: no cover
                continue

            for item in re.findall(r'\s*"(\S+::\S+)\"', File(fname).read()):
                confirm('::' in item, f'[{item}] found in {fname}', 'Expecting Module name separated by ::')
                elems = item.split('::')
                if (elems[-2], elems[-1]) in removable:
                    not_remove.update({(elems[-2], elems[-1])})

        log.info(f'-i- Count of RunCallBack tests and its dependencies not to be removed: {len(not_remove)} out of total removable tests/candidates: {len(removable)}')
        return not_remove

    def get_prime_pinprofilerTM(self):
        """
        Get all PinProfiler tests that needs to be not removed by cleantp - appears as PreInstance or PostInstance calls
        """
        not_remove = set()
        for mod, tname, dd, _ in self.tpobj.mtpl.iter_tests(template_name='PrimePinProfilerTestMethod', edict=True):
            not_remove.update({(mod, tname)})

        return not_remove

    def get_floatingInstance_invoked_by_activeTests(self, removable):
        """
        Get all floating tests invoked by active tests that should not be removed.

        Sources covered:
        1) Explicit instance calls, e.g. PerPartitionExecution.InstanceNameToExecute
        2) JsonRun references in active test parameters that list scoped test names
        """
        not_remove = set()

        # Step 1: Collect all files that need to be read (deduplicate across iter_tests)
        ffile_set = set()

        for item in self.floating_instance_call.keys():
            for mod, tname, dd, _ in self.tpobj.mtpl.iter_tests(template_name=item, edict=False):
                # Explicit instance call handler
                if self.floating_instance_call[item] in dd:
                    elems = dd[self.floating_instance_call[item]].split('::')
                    if len(elems) >= 2 and (elems[-2], elems[-1]) in removable:
                        not_remove.update({(elems[-2], elems[-1])})

                # Collect files with JsonRun references
                if self.floating_instance_call[item] not in dd or 'JsonRun' not in dd[self.floating_instance_call[item]]:
                    continue

                jsonrun_regex = r'JsonRun\s*\((.*?)\)'
                f_jsonRun = re.sub(jsonrun_regex, r'JsonRun("\1")', str(dd[self.floating_instance_call[item]]))
                for param in CleanTP.get_value_tosrule(self.tpobj, f_jsonRun, mod):
                    if self.tpobj.is_tos4 and not exists(Env.xpath(param)):
                        # (A) ConfigFile = GetEnvironmentVariable(...)+"./Modules/...json";
                        if len(param.split('Modules')) > 1:
                            fpath = param.replace("./Modules", "/Modules")
                            ffile_set.add(Env.xpath(fpath.replace("\\", "/")))
                        # (B) ConfigFile = "InputFiles/...json";
                        else:
                            fpath = os.path.dirname(self.tpobj.mtpl.get_mod2fname()[mod]) + '/' + param
                            ffile_set.add(Env.xpath(fpath.replace("\\", "/")))
                    else:
                        ffile_set.add(Env.xpath(param))

        # Step 2: Read each file once and extract all test names via regex
        file_tests_cache = {}  # fname -> set of (mod, tname) tuples
        for fname in sorted(ffile_set):
            if not exists(fname):
                continue

            tests_in_file = set()
            for test in re.findall(r'\s*\"(\S+::\S+)\"', File(fname).read()):
                confirm('::' in test, f'[{test}] found in {fname}', 'Expecting Module name separated by ::')
                elems = test.split('::')
                if len(elems) >= 2:
                    tests_in_file.add((elems[-2], elems[-1]))

            file_tests_cache[fname] = tests_in_file

        # Step 3: Check cached results against removable tests
        for tests_in_file in file_tests_cache.values():
            not_remove.update(tests_in_file & removable)

        return not_remove

    def get_pgmrules(self, remove_all):
        """
        Get all pgmrules test instance that we cant remove because init will fail
        :param remove_all: set of remove
        :return: set of (mod, instance)
        """
        ffile = {}

        # grab all iCGlXpressTest in INIT flow
        for mod, tn, dd in self.tpobj.mtpl.iter_flows('INIT', template='iCGlXpressTest', bypass=True, edict=True):
            ffile[os.path.join(self.tpobj.tpldir, dd['gl_xpress_file_path'])] = (mod, tn)
        for mod, tn, dd in self.tpobj.mtpl.iter_flows('MAIN', template='iCGlXpressTest', bypass=True, edict=True):
            ffile[os.path.join(self.tpobj.tpldir, dd['gl_xpress_file_path'])] = (mod, tn)

        data = {}   # pgmrules data
        for fname, mod_tn in ffile.items():
            data.update(self.tpobj.pgmrules._read_pgm_files(fname, mod_tn))

        final = set()
        for key in data:
            for elem in data[key]:
                item = elem['tn']
                if '::' in item:
                    elems = item.split('::')
                    final.add((elems[-2], elems[-1]))

        log.info(f'-i- Count of pgmrules total: {len(final)}, no_remove_count: {len(remove_all & final)}')
        return final

    def get_hardcoded_bypassed(self):
        """
        Get all hardcoded always bypassed instances
        :return: set of (mod, testinstance) that are hardcoded bypassed
        """
        hardcoded = set()
        for mod, tname, dd in self.tpobj.mtpl.iter_flows('MAIN', bypass=False, idict=True):
            result = dd.get('bypass_global', dd.get('BypassPort', ''))

            if str(result) == '1':
                hardcoded.add((mod, tname))

        return hardcoded

    def is_module_skip(self, fname, module):
        """
        Determine if this fname or module need to be skipped

        :param fname: mtpl filename
        :param module: testplan module name
        :return: True if module is skipped
        """
        # temporary debug, only reduce these, see if we don't get b98
        # if module in self.get_base_modules():
        #     log.info(f'-i- skipping {module} since it is a base')
        #     return

        # Temporary: CLK cannot be skipped for ARLS since it causes bin98
        if module.startswith('CLK'):    # pragma: no cover
            log.info(f'-i- skipping {module} since it is a special (causing b98)')
            return True

        return False

    def remove_instances(self, fname, module, to_remove, no_remove):
        """
        Update the mtpl and remove floating and bypassed instances and heal the wiring.
        :param fname: mtpl file
        :param module: which module
        :param to_remove: set of instances to remove
        :param no_remove: set of instances not to remove
        :return: unittest only
        """
        if self.is_module_skip(fname, module):
            return 1

        log.info(f'-i- Processing {basename_n(fname, 2)}')
        instances = {ti for md, ti in (to_remove - no_remove) if md == module}

        # 1st pass: reformat it
        OtplFile(fname).reformat()

        # 2nd pass: identify all lines to be deleted
        nest = 0
        delete = None
        dellines = set()
        port = None
        dfi = None
        dports = defaultdict(dict)    # deleted instances dict: {dfi: {port: 'goto|return'}
        for lno, line in OtplFile(fname).readline(comments=True):

            if line == '{':
                nest += 1

            # closure
            elif line == '}':
                nest -= 1
                port = None
                if delete == nest:
                    dellines.add(lno)
                    delete = None
                    dfi = None

                if nest == 0:
                    dfi = None

            # instance
            if nest == 0 and line.startswith(('CSharpTest ', 'Test ', 'MultiTrialTest ')):
                name = line.split()[-1]
                if name in instances:
                    delete = nest

            # dutflow
            if line.startswith(('DUTFlowItem ', 'FlowItem ')):
                elems = line.split()
                dfi = elems[1]
                if elems[2] in instances:
                    delete = nest

            if delete is not None:
                if line.startswith('Result '):
                    port = line.split()[1]

                if dfi and line.startswith(('Return ', 'GoTo ')):
                    assert port is not None, f'Error in line#{lno} of {fname}. No port number found.'
                    dports[dfi][port] = line

                # delete the line
                dellines.add(lno)

        # 3rd pass: Update the wires (heal it)
        olines = File(fname).raw()
        replines = {}
        for lno, line in OtplFile(fname).readline():
            if line.startswith('GoTo '):
                dfi = line.split()[1].replace(';', '')
                if dfi in dports:
                    replines[lno] = olines[lno - 1].replace(line, self.follow(dports, dfi, line, fname))

        # delete the lines in the actual file
        lines = []
        for lno, line in enumerate(olines, 1):
            if lno in dellines:
                continue

            if lno in replines:
                lines.append(replines[lno])
            else:
                lines.append(line)

        final = re.sub(r'\n{3,}', '\n\n', ''.join(lines))
        # write it
        res = File(fname).rewrite(final, 'CleanTP.remove_instances()', keep="old")
        self.stats['rewrite_instance_files'] += int(res)

    def follow(self, dports, dfi, line, fname, port='1', _maxloop=1000):
        """
        :param dports: deleted instances dict: {dfi: {port: 'goto|return'}
        :param dfi: dfi name of block being removed
        :param line: current line
        :param fname: mtpl file (for error print)
        :param port: Which port to follow (default of 1)
        :return: The final line
        """
        # TODO: implement the port, as specified by user
        orig_dfi = dfi
        for _ in range(_maxloop):
            if dfi not in dports:
                return line

            line = dports[dfi][port]
            if line.startswith('GoTo '):
                dfi = line.split()[1].replace(';', '')

                # This will not happen in latest code
                # if dfi == orig_dfi:     # you can't goto a deleted dfi
                #     # try port 3
                #     if '3' in dports[dfi]:
                #         port = '3'    # try this port
                #     else:
                #         port = '0'    # fail port

            else:
                return line

        raise ErrorCockpit(f'Maximum loops for dfi={dfi} in {fname}',
                           'There seems to be a recursive loop. Pls contact jqdelosr')

    def get_base_modules(self):      # pragma: no cover
        """
        Return base modules for ARLS - debug only
        """
        base_mods = '''IP_CPU_BASE DRV_RESET_CXX TPI_BASE_IPCPU TPI_DFF_CXX TPI_DWNSTFRK_CXX
        TPI_ENDIPCPU_XXX TPI_EVGBRDG_CXX TPI_FLWFLGS_CXX TPI_PWRUP_CXX IP_CPU_CONCURRENT_FLOWS
        IP_PCH_BASE DRV_RESET_GXX DRV_RESET_IXP TPI_BASE_IPPCH TPI_DFF_GXX TPI_DWNSTFRK_GXX
        TPI_ENDIPPCH_XXX TPI_EVGBRDG_PXX TPI_FLWFLGS_PXX TPI_GFXAGG_GXX TPI_PWRUP_HXX
        IP_PCH_CONCURRENT_FLOWS CLK_BASE_CXX CLK_BASE_SXN DRV_RESET_SXN DRV_RSTCMN_XXX
        DRV_RESET_IXPK DRV_RESET_SXS FUS_FLE_YXX FUS_FUSECFG_CXX FUS_FUSECFG_GXX FUS_FUSECFG_IXP
        FUS_FUSECFG_SXX FUS_ISEED_YXX FUS_UNITINFO_CXX FUS_UNITINFO_GXX FUS_UNITINFO_IXP
        FUS_UNITINFO_SXX PPR PTH_BGCEP_CXX PTH_DIODE_XXX PTH_DLVR_CXX PTH_DTS_CXX PTH_DTS_GXX
        PTH_DTS_IXX PTH_DTS_SXX PTH_THRMSET_XXX PTH_THRSOAK_XXX PTH_VDAC_CXX SIO_INIT_YXX
        TPI_END_XXX TPI_BASEPRIM_XXX TPI_BASE_XXX TPI_DFF_XXX TPI_DIESLCT_XXX TPI_DWNSTFRK_SXX
        TPI_EDM_XXX TPI_EVGBRDG_XXX TPI_EVMINS_YXXK TPI_EXPRESS_YXX TPI_FLWFLGS_XXX TPI_IDUTFORK_XXX
        TPI_IDUTRCS_XXX TPI_PBMFC_YXX TPI_PRMDEDC_XXX TPI_PUP_XXX TPI_PWRUP_DCYXXK TPI_PWRUP_YXXK
        TPI_SHOPS_XXX TPI_SOCREC_SXX TPI_VCC_XXX'''
        return set(base_mods.split())


class CleanPlist:
    """Remove all unused plists"""
    # dict of template: param that has plb reference in json file
    json_plbs = {'MbistRasterRepairTC': 'RasterInputFile',
                 'VminTC': 'PostInstance',
                 'PthPowerSetupTM': 'ConfigurationFileSicc'}

    def __init__(self, tpobj: TestProgram):
        self.tpobj = tpobj
        self.dest = f'{self.tpobj.tpldir}/clean_plist'
        self.globalplist = 'PList ' if self.tpobj.is_tos4 else 'GlobalPList '
        self.optin = set()
        self.non_opt_fnames = set()
        self.pat_mregex_cache = dict()

    def main(self, _maxiter=10):
        # initialize
        self.optin = CleanTP.init_optin(self.tpobj)
        used = set()
        used_pat = set()  # holds all patterns that are used (corresponds to used plbs)
        keeppats = set()     # Set of keep patterns
        total_plb_overall = set()
        fat_plb = skipped_fnames = 0
        patterns_remaining_fat = set()
        total_pat = len(self.tpobj.plists.get_pats_all())
        plb_map = self.tpobj.plists.get_plb_map()     # dict of plb:fname
        for plb in plb_map:
            total_plb_overall.update({(plb_map[plb], plb)})     # Get set of tuples (fname,plb)

        # Get non opt in fnames
        self.non_opt_fnames = self.non_opt_plist_files()

        # part1 - get all used patlists in all instances (connected or unconnected)
        plist_params = 'patlist LkgHiPlist LkgLoPlist'.split()
        for param in plist_params:
            for mod, tname, dd, _ in self.tpobj.mtpl.iter_tests(key_name=param, edict=False):
                plb_used = {item for item in CleanTP.get_value_tosrule(self.tpobj, dd[param], mod)}
                for plb in plb_used:
                    used.update({remove_ip(plb)})
                    used_pat.update(self.tpobj.plists.get_pats_from_plb(plb, False, False, False, False))

        # get plb referenced in Json files like used for QRE sockets/Raster json files
        used = self.get_plb_from_json(used)
        used = self.get_plb_from_JsonRun_calls(used)

        # part2 - Update keep pats for various reasons
        keeppats.update(self.get_instance_regex(used_pat, 'SetPointsRegEx'))  # used_pat holds used patterns in TP, optimizies cleanplist in total cleanup and TT spent
        keeppats.update(self.get_instance_regex(used_pat, 'RegEx'))  # used_pat holds used patterns in TP, optimizies cleanplist in total cleanup and TT spent
        # Method to accumulate plbs of patterns referenced in ALEPH file (through PatternsRegEx) in INIT flow
        init_plb_to_keep = self.get_pat_regex_from_aleph_env(used_pat, 'SetPoint')  # returns tuple containing (1) dictionary of {plb: set_of_pat} and (2) plbs to be not cleaned (as they are in ALEPH files). Now this function calls self.get_PatternsRegEx()

        # part3 - Update used plists
        keepdict = self.keep2dict(keeppats, init_plb_to_keep[0], self.non_opt_fnames)         # keepdict = mix of {plb: set_of_pat}
        used.update(keepdict)                       # add plb of keep patterns
        used.update(init_plb_to_keep[1])  # making sure plbs found in ALPEH files are deemed as **used** to avoid INIT issues

        # part3.5 - Get manually commented plists to not clean
        noclean = self.get_plist_noclean()
        used.update(noclean)

        # self.get_reference_plists(used, _maxiter)   # commenting it out here since we want to get subplist and parentplist first before getting reference/dependent plists
        subplists = set()
        used_with_all_refs = set()
        used_with_all_refs.update(used)
        for plb in used:
            if plb in plb_map:
                subplists = self.tpobj.plists.get_subplists(plb)
                parentlists = self.tpobj.plists.get_parentplists(plb)
                used_with_all_refs.update(subplists | parentlists)

        self.get_reference_plists(used_with_all_refs, _maxiter)  # Add used in reference plists

        # Create set of tuples {(plist_file, plb)} being used
        # "used_set" has plbs or PLISTS that are absolutely essential ones without which TP will fail to LOAD/INIT
        used_set = set()

        for plb in used_with_all_refs:
            if plb in plb_map:
                used_set.update({(plb_map[plb], plb)})
            else:
                print(f'-w- cannot find plb loaded in file: {plb}')

        # "plb_to_remove" is TOTAL FAT PLB
        plb_to_remove = total_plb_overall - used_set
        # "patterns_to_remove" is TOTAL FAT PATTERNS
        patterns_to_remove = set()
        for plb in plb_to_remove:
            patterns_to_remove.update(self.tpobj.plists.get_pats_from_plb(plb[1]))

        # part4 - rewrite the patlists
        mkdirs(self.dest, '02775')
        # "removed_plbs" is FAT PLBS REMOVED
        removed_plbs = set()
        removed_plbs_owner = set()   # to keep track of removed plbs for reporting, with owner info if available, as (fname, plb, owner)
        for fname in self.tpobj.plists.get_plist_list():
            if basename(fname).lower() in self.non_opt_fnames:
                skipped_fnames += 1
                continue
            removed_plbs_owner.update(self.process_plist(fname, used_with_all_refs, keepdict))    # return set of (fname, plb, owner) as removed

        removed_plbs.update({item[:2] for item in removed_plbs_owner})
        # "plb_remaining_fat" is REMAINING FAT PLB
        plb_remaining_fat = plb_to_remove - removed_plbs

        # part5 - update env
        newval = self.tpobj.env.get_item('HDST_PLIST_PATH', islist=True)
        if self.tpobj.env.get_item('TP_STRUCTURE', islist=False, default='TORCH') != 'TORCH_TO_SORT' and "clean_plist" not in '\t'.join(newval):
            newval.insert(0, r'~HDMT_TPL_DIR\clean_plist')    # first, since Supersedes are already processed
        elif self.tpobj.env.get_item('TP_STRUCTURE', islist=False, default='TORCH') == 'TORCH_TO_SORT' and "clean_plist" not in '\t'.join(newval):
            newval.insert(0, r'~HDMT_TPL_DIR\\clean_plist')    # first, since Supersedes are already processed
        else:
            newval.insert(0, r'~HDMT_TPL_DIR\clean_plist')    # first, since Supersedes are already processed
        self.tpobj.env.set_item('HDST_PLIST_PATH', newval)
        File(self.tpobj.envfile).rewrite(''.join(self.tpobj.env.rebuild()), 'Env of CleanPlist().main()', keep='old')

        # display stats
        newobj = TestProgram(self.tpobj.envfile, allpats=False)
        fat_pat = total_pat - len(newobj.plists.get_pats_all())
        # "patterns_remaining_fat" is REMAINING FAT PATTERNS
        # patterns_remaining_fat = len(patterns_to_remove) - fat_pat

        for plb in plb_remaining_fat:
            patterns_remaining_fat.update(newobj.plists.get_pats_from_plb(plb[1]))

        total_plists = len(self.tpobj.plists.get_plist_list())

        CleanTP.add2fullreport(self.tpobj, "Plist", "Cleaned", removed_plbs_owner)
        CleanTP.add2fullreport(self.tpobj, "Plist", "Fat", plb_remaining_fat)

        plists_report = {
            "plists": {
                "total plb": len(total_plb_overall),
                "total pat": total_pat,
                "noclean": len(noclean),
                "plbs_cleaned": len(removed_plbs),
                "patterns_cleaned": fat_pat,  # len(patterns_to_remove)
                "remaining_fat_plb": len(plb_remaining_fat),
                "remaining_fat_patterns": len(patterns_remaining_fat)
            }
        }

        CleanTP.add2summary(self.tpobj, plists_report)

        print(f'-i- Cleaned {total_plists-skipped_fnames} out of {total_plists} plist files')
        print(f'-i- Total plb:    {len(total_plb_overall)}')
        print(f'-i- Removed plb:  {len(removed_plbs)}')  # {fat_plb}
        print(f'-i- Total pats:   {total_pat}')
        print(f'-i- Removed pats: {fat_pat}')
        print(f'-i- Remaining fat plb: {len(plb_remaining_fat)}')  # {len(plb_to_remove) - (fat_plb + len(noclean & plb_to_remove))}
        print(f'-i- Remaining fat pats: {len(patterns_remaining_fat)} ')

    def get_plb_from_JsonRun_calls(self, used):
        """
        Get all Floating/not-floating RunCallBack instances and plb referenced within json files called upon by RunCallBack instances
        that we can't remove because it could be called by other tests connected in the flow or during QRE sockets
        :return: set of plbs
        """
        not_remove_plb = set()
        ffile = set()
        for mod, tname, dd, _ in self.tpobj.mtpl.iter_tests(template_name='RunCallback', edict=False):
            if 'Callback' in dd and 'JsonRun' in dd['Callback']:
                for item in CleanTP.get_value_tosrule(self.tpobj, str(dd['Parameters']), mod):  # adding to process TOS Rules if present
                    if self.tpobj.is_tos4 and not exists(Env.xpath(item)):  # TOS4 and for cases when path is not resolvable
                        # (A)--> ConfigFile = GetEnvironmentVariable("~HDMT_TP_BASE_DIR")+"./Modules/PCD/SCN_PCD_PKS/InputFiles/dedc_callback_all.json";
                        if len(item.split('Modules')) > 1:
                            fpath = item.replace("./Modules", "/Modules")
                            ffile.add(Env.xpath(fpath.replace("\\", "/")))
                        elif item != '':  # (B)--> ConfigFile = "InputFiles/dedc_callback_all.json";
                            fpath = os.path.dirname(self.tpobj.mtpl.get_mod2fname()[mod]) + '/' + item
                            ffile.add(Env.xpath(fpath.replace("\\", "/")))
                        # ffile.add(Env.xpath(os.path.abspath(item)))
                    else:  # TOS3
                        ffile.add(Env.xpath(item))

        for fname in sorted(ffile):
            # some json are not existing, as found in 66B0B TP.
            if not exists(fname):      # pragma: no cover
                continue
            data = JsonRead(File(fname).get_name(), error_out=False).load()
            not_remove_plb.update(set(find_dot_items(data, 'plist', default=[])))

        log.info(f'-i- Count of plb calls from Json file: {len(not_remove_plb)}')
        used.update(not_remove_plb)
        return used

    def get_plb_from_json(self, used):
        """
        Get all plbs referenced in json that needs to be not removed by cleantp - appears as one of test instance parameter of a given template
        :return: set of plbs
        """
        jsonrun_regex = r'JsonRun\s*\((.*?)\)'
        f_jsonRun = None
        for item in self.json_plbs.keys():
            for mod, tname, dd, _ in self.tpobj.mtpl.iter_tests(template_name=item, edict=False):
                if self.json_plbs[item] in dd and bool(re.search(r"\.json", dd[self.json_plbs[item]])):
                    f_jsonRun = re.sub(jsonrun_regex, r'JsonRun("\1")', str(dd[self.json_plbs[item]]))
                    ff_list = CleanTP.get_value_tosrule(self.tpobj, f_jsonRun, mod)
                    for ff in ff_list:
                        fpath = File.realname(Env.xpath(os.path.abspath(ff)))
                        if not File(fpath).exists():
                            continue  # InputFiles/MBIST_RASTER_allplist.json

                        data = JsonRead(File(fpath).get_name(), error_out=False).load()

                        if bool(re.search(r"JsonRun", f_jsonRun)):
                            used.update(set(find_dot_items(data, 'plist', default=[])))
                        else:
                            used.update(set(find_dot_items(data, regex='Plist', default=[])))
                            if isinstance(data, dict) and 'PLists' in data:
                                for plb in data["PLists"].keys():
                                    if plb not in used:
                                        used.update({plb})

        return used

    def keep2dict(self, keeppats, init_plb_to_keep, non_opt_fnames):
        """
        :param init_plb_to_keep is dictionary of {plb: set_of_pat} where all plbs need to be retained for successful TP load and INIT
        :param keeppats holds set of patterns identified from Regex call made through Test Instances definition
        :param non_opt_fnames has set of plist files for those modules not opted in cleanTP
        Return dictionary with mix of {plb: set_of_pat} | {plb : set_of_testinstances}"""
        result = defaultdict(set)
        setfname = set()
        pat2plb = self.tpobj.plists.get_plbs_usedby_pats(keeppats)     # dictionary of {pat: set_of_plb}
        for pat, setplb in pat2plb.items():
            for plb in setplb:
                setfname = self.tpobj.plists.plb_to_filename([plb], fullpath=False)
                for fname in setfname:
                    if (fname.lower() not in non_opt_fnames):  # and (plb in plb_mod_dict):
                        result[plb].add(pat)  # dictionary of {plb: set_of_pat}
                        result[plb].update(self.tpobj.plists.get_pats_from_plb(plb))

        for plb in init_plb_to_keep:
            result[plb].update(set(init_plb_to_keep[plb]))
            result[plb].update(self.tpobj.plists.get_pats_from_plb(plb))

        return result

    def get_reference_plists(self, used, _maxiter):
        """Get reference plists from used, and update used"""
        dd = self.tpobj.plists.get_refplist()
        for ctr in range(_maxiter):   # 10 iterations or redirections
            found = False
            for plb in dd:
                if plb in used:
                    for item in dd[plb]:
                        if item not in used:
                            found = True
                            used.add(item)

            if not found:
                log.info(f'-i- get_plist_dependent() iteration: {ctr}')
                break

    def get_PatternsRegEx(self, config_name_dict, used_pat, kw='Name'):
        """Return **tuple** containing
            (1) set of patterns and
            (2) set of plists called in ALEPH files
        after parsing ALEPH .json files to pick out PatternRegEx regex values and Plists ONLY for "Configuration Names"
        found from ConfigurationFile json file specific to 'SetPoint' referenced in mtpl file for INIT subflow
        :param config_name_dict is list of "Configuration Names" referenced in ConfigurationFile json file specific to 'SetPoint' referenced in mtpl file for INIT subflow
        """
        result = set()
        alpeh_plb = set()
        to_match = []
        to_match_count = set()
        for ff in self.tpobj.env.get_contents('ALEPH_FILES', islist=True):
            # process one json file
            fpath = Env.xpath(ff)
            if not fpath.endswith('.json'):
                continue
            if not File(fpath).exists():
                continue

            data = JsonRead(File(fpath).get_name(), error_out=False).load()
            aleph_config_list = find_dot_items(data, regex=kw, default=[])
            pat_result = set()

            to_match = find_dot_items(data, 'PatternsRegEx', default=[])  # +'.*PatternsRegEx'
            to_match_count.update(to_match)
            alpeh_plb.update(set(find_dot_items(data, 'Plists', default=[])))
            for aleph_config in aleph_config_list:
                reduced_to_match = tuple()
                if aleph_config in config_name_dict.keys():
                    if len(aleph_config_list) == len(to_match):
                        if to_match[aleph_config_list.index(aleph_config)] != "g.*":
                            reduced_to_match = tuple(sorted({to_match[aleph_config_list.index(aleph_config)]}))
                    else:
                        reduced_to_match = tuple(sorted({x for x in to_match if x != "g.*"}))

                    if reduced_to_match in self.pat_mregex_cache:
                        pat_result = self.pat_mregex_cache[reduced_to_match]
                    else:
                        pat_result = self.pat_mregex(reduced_to_match, self.tpobj.plists.get_pats_all(), used_pat)
                        self.pat_mregex_cache[reduced_to_match] = pat_result

                    result.update(pat_result)

        log.info(f'-i- PatternsRegEx() pat count: {len(result)}, plists count in ALEPH files: {len(alpeh_plb)}, regex total: {len(to_match_count)}')
        return (result, alpeh_plb)

    @classmethod
    def pat_mregex(cls, re_list, pat_list, used_pat=''):
        """
        Process a list of regex (re_list) and apply them into pattern list (pat_list)
        This routine will separate regex vs non-regex (exact match)

        :param re_list: list of pattern regex from xml of mtpl
        :param pat_list: list of patterns to match
        :return: set of patterns that match regex list
        """
        to_match = set()
        exact_match = set()
        result = set()

        # fix the list first
        for item in re_list:
            # item = item.split(':')[0]     # remove ip ---> line not needed as IP section is never specified in patregex json and ":" could be part of regex itself
            if item == '.*':    # cannot add all
                continue

            if item.startswith('^'):
                item = item[1:]

            dollar = False
            if item.endswith('$'):
                item = item[:-1]
                dollar = True

            if set(item) & set('.*([{?'):
                pass  # regex
            else:
                exact_match.add(item)
                continue

            if not dollar:
                if not item.endswith('.*'):
                    item = f'{item}.*'

            to_match.add(item)

        mregex = '^(%s)$' % '|'.join(sorted(to_match))

        bigpat = '\n'.join(sorted(pat_list))            # Concatenate all patterns
        if used_pat:
            usedpat = '\n'.join(sorted(used_pat))            # Concatenate all patterns
        robj = re.compile(mregex, re.MULTILINE)
        print(f"-i- Running large count={len(to_match)} regex on {len(pat_list)} patterns...")
        sw = Elapsed()
        if used_pat:
            result = {pat if isinstance(pat, str) else pat[0] for pat in robj.findall(usedpat)}      # List of patterns that match the megaregex
        if len(result) == 0:
            result = {pat if isinstance(pat, str) else pat[0] for pat in robj.findall(bigpat)}      # List of patterns that match the megaregex
        print(f'-i- regex Elapsed: {sw}, found={len(result)}')

        result.update(exact_match & pat_list)
        return result

    def get_pat_regex_from_aleph_env(self, used_pat, kw='SetPoint'):
        """
        Get all plbs of patterns being referenced through ALEPH file (through PatternsRegEx within ALEPH FILES) that are called or referenced fom INIT subflow
        :param keyword 'SetPoint'
        :return: tuple containing (1) result_plb_dict containing {plb: set_of_pats} and (2) plb found in ALPEH files to be not cleaned. Here keys of this dictionary are the plbs to be kept/retained for TP to load and pass INIT
        """
        config_name_dict = {}  # dictionary to hold Configuration Names as key and value as TestInstance where ConfigurationName is getting referenced
        setpoint_dict = {}
        plist_dict = defaultdict(set)  # # holds {plb : set_of_testinstances}
        result_plb_dict = defaultdict(set)  # holds {plb: set_of_pats} or {plb : set_of_testinstances}
        for which in (True, False):   # So pass flow first, then fail flow
            kwargs = dict(passonly=which, bypass=True, keyparam='SetPoint', edict=True)  # bypass=True skips bypassed instances
            for flow in ['INIT', 'MAIN']:
                for md, tn, data in self.tpobj.mtpl.iter_flows(flow, **kwargs):
                    mtpl_json_list = []  # list of Configuration Names referenced in ConfigurationFile json file specific to 'SetPoint' referenced in mtpl file for INIT subflow
                    if 'PrimePatConfigTestMethod' in data.values() and 'RegEx' not in data and 'SetPoint' in data and 'Plist' not in data:  # scenario where PrimePatConfigTestMethod has only SetPoint and Configuration json file for INIT subflow
                        ff = data["ConfigurationFile"]

                        if self.tpobj.is_tos4 and not exists(ff):  # TOS4 and for cases when path is not resolvable
                            # (A)--> ConfigFile = GetEnvironmentVariable("~HDMT_TP_BASE_DIR")+"./Modules/PCD/SCN_PCD_PKS/InputFiles/ABCD.json";
                            if len(ff.split('Modules')) > 1:
                                fpath = re.sub(r'\s*\+\s*"?\./Modules', '/Modules', ff)
                                fpath = re.sub(r'\\', '/', fpath)
                                fpath = re.sub(r'GetEnvironmentVariable\s*\(\s*"~HDMT_TP_BASE_DIR"\s*\)', self.tpobj.env.get_hdmt_tpl_dir(), fpath)
                            else:  # (B)--> ConfigFile = "InputFiles/ABCD.json";
                                fpath = os.path.dirname(self.tpobj.mtpl.get_mod2fname()[md]) + '/' + ff
                                fpath = re.sub(r'\\', '/', fpath)
                                fpath = Env.xpath(fpath)
                        else:
                            fpath = Env.xpath(ff)

                        fpath = File.realname(Env.xpath(os.path.abspath(fpath)))
                        fpath = re.sub(r"""['"]?\s*;?\s*$""", '', fpath)

                        if fpath.endswith('.json') and File(fpath).exists():
                            print(f'-i- RAM Processing json file: {fpath} for ConfigurationFile and ,\
                                   SetPoint reference in mtpl file for INIT subflow for TestInstance: {tn}')
                            data = JsonRead(File(fpath).get_name(), error_out=False).load()
                            mtpl_json_list = find_dot_items(data, regex='Configurations.*Configuration', default=[])
                            for item in mtpl_json_list:
                                config_name_dict[item] = tn
                    if 'PrimePatConfigTestMethod' in data.values() and 'RegEx' not in data and 'SetPoint' in data and 'Plist' in data:  # PrimePatConfigTestMethod has Plist, SetPoint and Configuration json file for INIT subflow
                        fplist = (data["Plist"] if "::" not in data["Plist"] else data["Plist"].split("::")[1])  # if IP (IPG/IPH etc) section is specified, remove it else take the plist as it is referenced
                        plist_dict[fplist].add(tn)

        for flow in ['INIT', 'MAIN']:
            # Helps with avoiding getting cleaned when RunCallBack is used to execute SetPoint patmods and hence no plist cleanup in those cases - Seen on GCD Sort TP
            kwargs = dict(passonly=True, bypass=True, keyparam='Callback', edict=True)  # bypass=True skips bypassed instances
            for md, tn, data in self.tpobj.mtpl.iter_flows(flow, **kwargs):
                if 'RunCallback' in data.values() and data["Callback"] == 'ExecutePatConfigSetPoint':
                    # Parameters = "MGarr:bisr_modify_BP49:bisrrepair:Global,MGarr:bisr_modify_BP50:bisrrepair:Global,MGarr:bisr_modify_BP51:bisrrepair:Global,MGarr:bisr_modify_BP52:bisrrepair:Global";
                    for setpoint in CleanTP.get_value_tosrule(self.tpobj, str(data['Parameters']), md):
                        for item in setpoint.split(","):
                            if item != '':
                                param = item.split(":")[1]
                                setpoint_dict[param] = tn
            # Helps with avoiding getting cleaned when PrimePauseTestMethod is used to execute SetPoint patmods and hence no plist cleanup in those cases - Seen on Class TP
            kwargs = dict(passonly=True, bypass=True, keyparam='SetPointsPreInstance', edict=True)  # bypass=True skips bypassed instances
            for md, tn, data in self.tpobj.mtpl.iter_flows(flow, **kwargs):
                if 'PrimePauseTestMethod' in data.values() and 'SetPointsPreInstance' in data.keys():
                    for setpoint in CleanTP.get_value_tosrule(self.tpobj, str(data['SetPointsPreInstance']), md):
                        for item in setpoint.split(","):
                            if item != '':
                                param = item.split(":")[1]
                                setpoint_dict[param] = tn

        for ff in self.tpobj.env.get_contents('ALEPH_FILES', islist=True):
            # process one json file
            fpath = File.realname(Env.xpath(ff))
            if not fpath.endswith('PatConfigSetpoints.json'):
                continue

            data = JsonRead(File(fpath).get_name(), error_out=False).load()
            setpoint_in_mtpl_list = find_dot_items(data, regex='Groups.*Name', default=[])

            for item in setpoint_in_mtpl_list:
                if item in setpoint_dict.keys():
                    aleph_setpoint_list = find_dot_items(data, regex='Groups.*Configurations.*Name', default=[])
                    for item_setpoint in aleph_setpoint_list:
                        config_name_dict[item_setpoint] = item

        for flow in ['INIT', 'MAIN']:
            # Helps with avoiding getting cleaned when PrimeHptpTimingCalibrationTestMethod is used to execute SetPoint patmods by setting TimingCalPatmodConfiguration - Seen on Class TP
            kwargs = dict(passonly=True, bypass=True, keyparam='TimingCalPatmodConfiguration', edict=True)  # bypass=True skips bypassed instances
            for md, tn, data in self.tpobj.mtpl.iter_flows(flow, **kwargs):
                if 'PrimeHptpTimingCalibrationTestMethod' in data.values() and 'TimingCalPatmodConfiguration' in data.keys():
                    for setpoint in CleanTP.get_value_tosrule(self.tpobj, str(data['TimingCalPatmodConfiguration']), md):
                        config_name_dict[setpoint] = tn

        pat_result = self.get_PatternsRegEx(config_name_dict, used_pat, 'Configurations.*Name')
        pat2plb = self.tpobj.plists.get_plbs_usedby_pats(pat_result[0])
        for pat, setplb in pat2plb.items():
            for plb in setplb:
                result_plb_dict[plb].add(pat)

        if len(plist_dict) == 0:
            return (result_plb_dict, pat_result[1])
        else:
            for plb in plist_dict:
                result_plb_dict[plb].update(self.tpobj.plists.get_pats_from_plb(plb))
            return (result_plb_dict, pat_result[1])

    def get_instance_regex(self, used_pat, kw='SetPointsRegEx'):
        """
        Get all patterns used in SetPointsRegEx in PrimePauseTestMethod (or any template) excluding bypassed test instances
        :return: Set of patterns to keep
        """
        to_match = set()
        for mod, tname, dd, _ in self.tpobj.mtpl.iter_tests(key_name=kw, edict=True):
            result = str(dd.get('bypass_global', dd.get('BypassPort', None)))
            if (result != "1"):
                to_match.add(dd[kw])

        to_match = tuple(to_match)

        if to_match in self.pat_mregex_cache:
            result = self.pat_mregex_cache[to_match]
        else:
            result = self.pat_mregex(to_match, self.tpobj.plists.get_pats_all(), used_pat)
            self.pat_mregex_cache[to_match] = result

        log.info(f'-i- get_instance_regex({kw}) pat count: {len(result)}')
        return result

    def non_opt_plist_files(self):
        """return: set of plist files being used by non-opt-in modules"""
        all_mods = set()
        non_opt_plists = set()

        all_mods = self.tpobj.mtpl.get_mod2fname().keys()
        non_opt_mods = all_mods - self.optin
        mod2plist_map = self.tpobj.plists.get_mod2plist_map()
        for mod in mod2plist_map:
            if mod in non_opt_mods:
                mod2plist_map_lowercase = [s.lower() for s in mod2plist_map[mod]]
                non_opt_plists.update(mod2plist_map_lowercase)
        return non_opt_plists

    def get_plist_noclean(self):
        """
        Return set of all plbs contained in # PATLIST_NOCLEAN tag
        Example:
         # patlist = "shops_M_list"; # PATLIST_NOCLEAN: can't clean because <reason>
        """

        noclean_plbs = set()
        comments = {}
        re_match = re.compile(r'patlist\s*=\s*(?:"([^"]+)"|\'([^\']+)\'|([^#;\s]+))', re.IGNORECASE)
        tag_match = re.compile(r'#\s*PATLIST_NOCLEAN\b', re.IGNORECASE)
        regex_match = re.compile(r'#\s*REGEX_PATLIST_NOCLEAN\s*:\s*(.*)', re.IGNORECASE)
        regex_list = []
        all_plb = self.tpobj.plists.get_plb_map().keys()

        for file in self.tpobj.get_all_mtpl_from_stpl():
            comments = self.tpobj.mtpl.read_comments(file)[0]
            for _, inst_cmnts, in comments.items():
                for comment in inst_cmnts:
                    if tag_match.search(comment):
                        for groups in re_match.findall(comment):
                            # Regex groups are mutually exclusive; pick the non-empty value.
                            plb_name = groups[0] or groups[1] or groups[2]
                            if plb_name in all_plb:
                                noclean_plbs.add(plb_name)
                    match = regex_match.search(comment)
                    if match:
                        regex_list.append(match.group(1))
        for rgx in regex_list:
            for plb in all_plb:
                match = re.match(rgx, plb)
                if match:
                    noclean_plbs.add(plb)

        return noclean_plbs

    def process_plist(self, inputfname, used, keepdict):
        """
        Update plist file
        :param fname: Input plist file
        :param used: set of used plist, including partial blocks
        :param keepdict: {plb: set_of_keeppats} dictionary of partial blocks
        """
        # copy the plist
        entireplist = File(inputfname).read()
        fname = File(f'{self.dest}/{basename(inputfname)}').touch(entireplist, newfile=True).get_name()

        # reformat
        OtplFile(fname).reformat()
        raw = File(fname).raw()

        # id blocks to remove
        stack = []
        foundused = set()
        everything = set()
        parentused = -1
        nest = 0
        for line in raw:
            sline = line.strip()

            if sline.startswith('{'):
                nest += 1
            elif sline.startswith('}'):
                nest -= 1
                if parentused == nest:
                    parentused = -1
                stack.pop()

            if sline.startswith(self.globalplist):
                plbname = sline.split()[1]
                stack.append(plbname)
                everything.add(plbname)

                if parentused > -1:
                    foundused.add(plbname)

                elif plbname in used:
                    parentused = nest
                    foundused.update(stack)    # add all in stack

        # remove the blocks
        removeset = everything - foundused
        final = self.remove_block(raw, removeset, keepdict)
        if not IS_UT and len(final) > 1:
            if not re.match('# copy from:', final[1]):             # do not re-add the full path comment if it is already there
                final.insert(1, f'# copy from: {inputfname}\n')    # add full path of plist as a comment

        # Returns {module: set_of_plist_file}
        # Cache mod2plist_map on this CleanPlist so we only compute it once per instance
        if not hasattr(self, '_mod2plist_map'):
            # dict: {module: set_of_plist_file} map to help find the module for the input plist file to be removed,
            # so that we can get the owner of the module through owner.txt file to add into final report
            self._mod2plist_map = self.tpobj.plists.get_mod2plist_map()
        mod2plist_map = self._mod2plist_map

        # Normalize plist filenames to lowercase for case-insensitive lookup to match other code paths like non_opt_plist_files
        if not hasattr(self, '_plist2mod_map'):
            # Map each plist filename (lowercased) to the set of modules that reference it.
            # Some plists (e.g., fuse.plist) can legitimately be shared across multiple modules,
            # so we must retain all module associations instead of letting later ones overwrite earlier.
            plist2mod_map = {}
            for mod, plist_file_set in mod2plist_map.items():
                for plist_file in plist_file_set:
                    key = str(plist_file).lower()
                    plist2mod_map.setdefault(key, set()).add(mod)
            self._plist2mod_map = plist2mod_map
        plist2mod_map = self._plist2mod_map

        plist_key = basename(inputfname).lower()
        modules_for_plist = plist2mod_map.get(plist_key)
        if not modules_for_plist:
            # fallback to UnknownModule if input plist file is not found in the mapping, to avoid KeyError
            module_of_inputfname = 'UnknownModule'
        elif len(modules_for_plist) == 1:
            # unambiguous ownership
            module_of_inputfname = next(iter(modules_for_plist))
        else:
            # shared plist referenced by multiple modules; do not arbitrarily pick one
            module_of_inputfname = 'MULTIPLE'

        # Resolve owner once per plist file (same module/owner for all removed blocks in this file)
        owner = ''
        if module_of_inputfname not in ('UnknownModule', 'MULTIPLE'):
            # get_mod2fname() returns {module: fullpath of module file}, so we can get the directory of the module file
            # and find owner.txt under that directory to get the owner of the module for the final report
            module_path = self.tpobj.mtpl.get_mod2fname().get(module_of_inputfname)
            if module_path:
                owner_file_path = os.path.join(os.path.dirname(module_path), 'owner.txt')
                if os.path.exists(owner_file_path):
                    with open(owner_file_path, 'r') as file:
                        for line in file:
                            if re.search(r'\s*owner\s*:', line.strip(), re.IGNORECASE):
                                owner = line.split(':', 1)[1].strip()
                                break
                else:
                    owner = module_of_inputfname
            else:
                owner = module_of_inputfname

        removed_plbs = set()
        for item in removeset:
            # Extract plb name (strip array notation if present: 'abc_list[PreBurst' -> 'abc_list')
            plb_name = item.split("[")[0]
            removed_plbs.update({(inputfname, plb_name, owner)})

        # rewrite
        confirm('tptools/mtl/unittests/' not in fname,
                'Unittest problem. Cannot write to UT_DIR area',
                'Contact jqdelosr')
        File(fname).rewrite(''.join(final), 'CleanPlist()')
        return removed_plbs

    def remove_block(self, raw, removeset, keepdict):
        """
        Remove blocks that are in removeset
        :param raw: list of raw lines
        :param removeset: set of blocks to be removed
        :param keepdict: {plbname: {set_of_keeppat}}
        :return: raw
        """
        nest = 0
        delete = None
        final = []
        partial = None
        for line in raw:
            sline = line.strip()

            if sline.startswith('{'):
                nest += 1

            # closure
            elif sline.startswith('}'):
                nest -= 1
                partial = None
                if delete == nest:
                    delete = None
                    continue    # Do not append this line

            # plist block
            if sline.startswith(self.globalplist) and delete is None:
                plbname = sline.split()[1]
                if plbname in removeset:
                    delete = nest
                elif plbname in keepdict:
                    partial = plbname

            # partial block
            if partial and sline.startswith('Pat '):
                patname = sline.split()[1].split(';')[0]
                if patname not in keepdict[partial]:
                    continue     # Do not append this pattern

            if delete is None:
                final.append(line)

        return final


class CleanTCG:
    """Remove all unused tcg"""

    def __init__(self, tpobj: TestProgram):
        self.tpobj = tpobj
        self.missing_tcdict = set()

    def main(self):
        # Part1: Get all used tcg
        # timing first
        target = self.tpobj.timing      # self.tpobj.levels
        params = 'TestConditionName TimingsTc timings timing'.split()
        everything_tim = set(target.iter_tc())     # get all tcg blocks
        used_tim = self.get_used(params)
        tc_all = dict(target.get_tc_dict())
        print(f'-i- tim everything: {len(everything_tim)}')
        print(f'-i- tim used:       {len(used_tim)}')

        # levels next
        target = self.tpobj.levels
        params = 'LevelsTc level levels PowerDownTc PowerOnTc DcLevels TestConditionName LkgHiLevels LkgLoLevels'.split()
        everything_lvl = set(target.iter_tc())     # get all tcg blocks
        used_lvl = self.get_used(params)
        tc_all.update(target.get_tc_dict())
        print(f'-i- lvl everything: {len(everything_lvl)}')
        print(f'-i- lvl used:       {len(used_lvl)}')

        # Part2: Build data structure of removed blocks
        # Get all F. Note that F is scoped
        F_everything = everything_tim | everything_lvl
        tim_used = self.update_tc_name(used_tim | self.get_used_ptm(), tc_all)
        lvl_used = self.update_tc_name(used_lvl | self.get_used_ptm(), tc_all)
        F_used = self.update_tc_name(used_tim | used_lvl | self.get_tcg_noclean() | self.get_used_ptm(), tc_all)
        # pprint(F_used - F_everything)      # ideally this is empty, but some blocks are not in data structure because ThermalMeasure and ThermalControl is not read by pytpd

        # {path: testplan_name} - to determine scope
        path2mod = {dirname(y): x for x, y in self.tpobj.mtpl.get_mod2fname().items()}

        # {scope: set_of_removed_blocks}
        scope_tim = self.get_scopedict(everything_tim, tim_used, tc_all, path2mod)
        scope_lvl = self.get_scopedict(everything_lvl, lvl_used, tc_all, path2mod)
        scopedict = self.get_scopedict(F_everything, F_used, tc_all, path2mod)

        # Part 2.5: Create sets of individual timing/lvl test conditions (only) to report
        # grab set for timings and levels from scope dict
        tim_remove = set()
        lvl_remove = set()
        for i in scope_tim:
            tim_remove |= scope_tim[i]
        for j in scope_lvl:
            lvl_remove |= scope_lvl[j]

        # remove scope from everything sets for lvls and timings to compare
        everything_tim_no_scope = set()
        everything_lvl_no_scope = set()
        for tim in everything_tim:
            everything_tim_no_scope.add(tim.split('::')[1])
        for lvl in everything_lvl:
            everything_lvl_no_scope.add(lvl.split('::')[1])

        # compare items in remove sets to all TC set to get which TC we're removing
        tim_tc_removed = set()
        lvl_tc_removed = set()
        for tim in tim_remove:
            if tim in everything_tim_no_scope:
                tim_tc_removed.add(tim)
        for lvl in lvl_remove:
            if lvl in everything_lvl_no_scope:
                lvl_tc_removed.add(lvl)

        tim_report = set()
        lvl_report = set()

        # Part3: Cleanup tcg files
        mod2fname = self.tpobj.mtpl.get_mod2fname()

        def resolve_owner_for_module(scope, mod2fname):
            """Resolve the owner for a given module scope using owner.txt.

            :param scope: Module scope name.
            :type scope: str
            :param mod2fname: Mapping from module scope to file name.
            :type mod2fname: dict
            :return: Owner string for the module scope, or empty string if not found.
            :rtype: str
            """
            owner = ''
            if scope in mod2fname:
                owner_file_path = os.path.join(
                    os.path.dirname(mod2fname[scope]),
                    'owner.txt'
                )
                if os.path.exists(owner_file_path):
                    with open(owner_file_path, 'r') as fh:
                        for line in fh:
                            if re.search(
                                    r'\s*owner\s*:',
                                    line.strip(),
                                    re.IGNORECASE):
                                owner = line.split(':', 1)[1].strip()
                                break
                else:
                    owner = ''
            return owner

        for ff in self.tpobj.get_import_files('tcg'):
            scope = path2mod.get(dirname(ff), 'BASE')
            self.remove_blocks(ff, scopedict[scope])

            # Look up owner from owner.txt in the module directory
            owner = resolve_owner_for_module(scope, mod2fname)
            # Create cleaned sets for full report
            for item in scope_tim[scope]:
                tim_report.update({(scope, item, owner)})
            for item in scope_lvl[scope]:
                lvl_report.update({(scope, item, owner)})

        CleanTP.add2fullreport(self.tpobj, "Timing TCG", "Cleaned", tim_report)
        CleanTP.add2fullreport(self.tpobj, "Lvl TCG", "Cleaned", lvl_report)

        # Part4: Create report block and add to report file
        tcg_report = {
            "TCG": {
                "timings": {
                    "cleaned": len(tim_tc_removed),
                    "total": len(everything_tim)
                },
                "levels": {
                    "cleaned": len(lvl_tc_removed),
                    "total": len(everything_lvl)
                }
            }
        }

        CleanTP.add2summary(self.tpobj, tcg_report)

        return scopedict    # for unittests

    def get_tcg_noclean(self):
        """
        Return set of all tcgs contained in # TCG_NOCLEAN tag
        Example:
         # tcg = "PTH::timings_blah"; # TCG_NOCLEAN: can't clean because <reason>
        """

        noclean_tcgs = set()
        comments = {}
        re_match = re.compile(r'tcg\s*=\s*(?:"([^"]+)"|\'([^\']+)\'|([^#;\s]+))', re.IGNORECASE)
        tag_match = re.compile(r'#\s*TCG_NOCLEAN\b', re.IGNORECASE)

        for file in self.tpobj.get_all_mtpl_from_stpl():
            comments = self.tpobj.mtpl.read_comments(file)[0]
            for _, inst_cmnts, in comments.items():
                for comment in inst_cmnts:
                    if tag_match.search(comment):
                        match = re_match.search(comment)
                        if match:
                            # Regex guarantees one non-empty capture group when match succeeds.
                            tcg_name = match.group(1) or match.group(2) or match.group(3)
                            noclean_tcgs.add(tcg_name)

        return noclean_tcgs

    def get_used_ptm(self):
        """
        :return: Used level tc from ptm file
        """
        robj = re.compile(r'Trigger\d+\s*=\s*(\w+)')
        used = set()
        for ff in self.tpobj.get_import_files('ptm'):
            for _, line in OtplFile(ff).readline():
                res = robj.search(line)
                if res:
                    used.add(res.group(1))

        return used

    def get_scopedict(self, F_everything, F_used, tc_all, path2mod):
        """
        Get removed blocks per scope

        :param F_everything: set of F (scoped) everything
        :param F_used: set of F (scoped) used
        :param tc_all: dict {F: data}
        :param path2mod: dict {path: module}
        :return: {scope: set_of_removed_blocks}
        """
        scopedict = {}     # {scope: set_of_removed_blocks}
        stats = {'total': 0, 'used': 0, 'fat': 0}
        all_used_blocks = self.get_ABE(F_used, tc_all)
        for ff in self.tpobj.get_import_files('tcg'):
            scope = path2mod.get(dirname(ff), 'BASE')
            if scope in scopedict:
                continue   # Do not reprocess

            everything = {x for x in F_everything if x.startswith(f'{scope}:')}   # everything based on scope
            used = {x for x in F_used if x.startswith(f'{scope}:')}               # used based on scope

            # return all remove blocks given the scope
            all_blocks = self.get_ABE(everything, tc_all)
            used_blocks = self.get_ABE(used, tc_all)
            remove_blocks = all_blocks - used_blocks
            orphan = used - all_blocks       # These are blocks that are not in data structure. eg. ThermalMeasure and ThermalControl
            confirm(not (orphan & remove_blocks), f'Cockpit Error: {scope}: Cannot remove orhans!', 'Pls check algo')
            # print(f'{scope}: {len(remove_blocks)}/{len(all_blocks)}')

            scopedict[scope] = {x.split(':')[-1] for x in remove_blocks}

            # cannot remove used which have specific scoping
            used_scope = {x.split(':')[-1] for x in all_used_blocks if x.startswith(f'{scope}:')}
            print(f"CANT remove {scope}: {len(scopedict[scope] & used_scope)}")
            scopedict[scope] -= used_scope

            # stats overall
            stats['total'] += len(all_blocks)
            stats['fat'] += len(scopedict[scope])

        # Display items missing in tc_dict
        print("-i- The following items are missing in tc_dict:")
        for item in sorted(self.missing_tcdict):
            print(f'   {item}')
        print()

        # Display stats
        print(f'-i- TCG Total blocks: {stats["total"]}')
        print(f'-i- TCG fat blocks:   {stats["fat"]}')

        return scopedict

    def remove_blocks(self, ff, remove):
        """
        Update the tcg file
        :param ff: Target file
        :param remove: blocks to remove - no scoping
        :return: None
        """
        # reformat otpl first so it is consistent
        OtplFile(ff).reformat()
        File(ff).copy(f'{ff}.orig')

        # process file and remove the blocks
        nest = 0
        delete = None
        final = []
        for line in File(ff).raw():
            sline = line.strip()

            if sline.startswith('{'):
                nest += 1

            # closure
            elif sline.startswith('}'):
                nest -= 1
                if delete == nest:
                    delete = None
                    continue    # Do not append this line

            # normal block
            if sline.startswith(('SpecificationSet ', 'TestConditionGroup ', 'TestCondition ')) and nest == 0:
                blockname = sline.split()[1]
                if blockname in remove:
                    delete = nest

            if delete is None:
                final.append(line)

        File(ff).rewrite(''.join(final), 'CleanTCG()')

    def get_ABE(self, F_set, tc_all):
        """
        Given F, return A, B, E, F blocks
        :param F_set: set of F block names
        :param tc_all: dictionary
        :return: set of A, B, E, F blocks
        """
        # {'BASE::F_tc':  {'Timing|Level':     '__main__::A_timing',
        #                  'SpecificationSet': 'BASE::B_specset',
        #                  'Selector':         'D_selector',
        #                  'TCG':              'E_tcg_name)}
        result = {None}
        for item in F_set:
            if item in tc_all:
                result.update({item,
                               tc_all[item].get('Timing'),
                               tc_all[item].get('Level'),
                               tc_all[item]['SpecificationSet'],
                               tc_all[item]['TCG'],
                               tc_all[item]['Inherit']}
                              )
            else:
                self.missing_tcdict.add(item)

        result.remove(None)
        return result

    @classmethod
    def update_tc_name(cls, tc_set, tc_all):
        """
        Update the name to:
        1. replace __main__ to BASE
        2. remove IP, if exist

        :param tc_set: Set of testcondition name from used
        :param tc_all: All tcsets with scoping
        :return: set
        """
        # create dictionary of no scoping
        noscope = {}     # {tc_name: scope}
        for item in tc_all:
            scope, name = item.split('::')
            if name in noscope:
                noscope[name] += f',{scope}'
            else:
                noscope[name] = scope

        # process tc_set
        final = set()
        for x in tc_set:

            # 1. replace __main__ to BASE
            if x.startswith('__main__'):
                x = x.replace('__main__', 'BASE')

            # 2. remove IP, if exist
            elems = x.split(':')
            if len(elems) == 5:
                x = x.replace(f'{elems[0]}::', '')

            # 3. no scope, add BASE
            if ':' not in x:
                scope = noscope.get(x, '')

                if ',' in scope:
                    for y in scope.split(','):
                        log.info(f'-w- Cannot remove {y}::{x} because multiple scopes found')
                        final.add(f'{y}::{x}')
                    continue
                if scope:
                    x = f'{scope}::{x}'

            final.add(x)
        return final

    def get_used(self, params):
        """
        Return used tcg
        :param params: list of params
        :return: set of used tcg
        """
        used = set()
        for param in params:
            for mod, tname, dd, _ in self.tpobj.mtpl.iter_tests(key_name=param, edict=False):
                items = CleanTP.get_value_tosrule(self.tpobj, dd[param], mod)
                used.update(items)

        return used


class CleanPPR:
    """Test Class that checks if PPR_CleanTP_Enable.txt and GlobalPPRconfiguration.json exists under PPR module
    If so, it looks up for all plists that are NOT tagged under GlobalPPRconfiguration.json
    to remove all PostPattern references ie., anything resembling (.*)DTSTEMPREAD(.*)
    Works for both TOS3 and TOS4 plist structure
    https://wiki.ith.intel.com/pages/viewpage.action?pageId=3762041250
    """
    all_flows = 'INIT MAIN LOTENDFLOW LOTSTARTFLOW TESTPLANENDFLOW TESTPLANSTARTFLOW'.split()

    def __init__(self, tpobj: TestProgram):
        self.tpobj = tpobj
        self.dest = f'{self.tpobj.tpldir}/clean_plist'
        self.globalplist = 'PList ' if self.tpobj.is_tos4 else 'GlobalPList '

    def main(self):
        # PPR untagging
        if CleanPPR.flag_for_PPR_cleanup(self.tpobj):
            glblPPR_plb = set()
            plb_map = self.tpobj.plists.get_plb_map()
            glblPPR_testinstance_mod = self.read_PPR_config()
            glblPPR_plb = self.get_plb_for_PPR_untag(glblPPR_testinstance_mod)
            self.PPR_untag_cleanplist(glblPPR_plb)

    @classmethod
    def flag_for_PPR_cleanup(cls, tpobj: TestProgram):
        """
        Check if PPR Global configuration file exists or not
        """

        if exists(f'{tpobj.tpldir}/Modules/PPR/InputFiles/PPR_CleanTP_Enable.txt') and exists(f'{tpobj.tpldir}/Modules/PPR/InputFiles/GlobalPPRconfiguration.json'):
            return True
        else:
            return False

    def PPR_untag_cleanplist(self, glblPPR_plb):
        """updates plist to have PostPattern removed"""

        if len(glblPPR_plb) != 0:

            plb_map = self.tpobj.plists.get_plb_map()
            fname_plb_dict = dict()
            for plb in glblPPR_plb:
                fname_plb_dict[plb] = plb_map[plb]     # Get dict of (fname:plb)

            fname_plb = defaultdict(set)
            for inputfname in fname_plb_dict.values():
                plist_list = []
                for plistname, plb_filename in fname_plb_dict.items():
                    if inputfname == plb_filename:
                        plist_list.append(plistname)
                fname_plb[inputfname] = plist_list

            for inputfname in fname_plb.keys():
                raw = File(inputfname).raw()
                plb_to_remove = set()
                # for plb in fname_plb_dict[inputfname]:
                for plb in fname_plb[inputfname]:

                    plb_to_remove.update(self.tpobj.plists.get_subplists(plb))
                    plb_to_remove.update({plb})
                    # print(f'len(plb_to_remove) -- {(plb_to_remove)} && {inputfname}')

                if raw[1].strip() == "Version 6.0;":
                    final = []
                    flag = 0
                    for line in raw:
                        sline = line.strip()
                        aline = re.sub(r"^\s+", "", sline)

                        if (flag == 0) and (aline.startswith(self.globalplist)) and (sline.split()[1] in plb_to_remove):
                            flag = 1

                        if flag == 1:
                            ln = re.match(r'(.*)\s*(Pat\s*.*DTSTEMPREAD\w*)\s*(.*)', sline)
                            if ln:
                                final.append(ln.group(1) + " " + ln.group(3))
                            else:
                                final.append(line)
                        else:
                            final.append(line)

                        if aline.startswith("}") and flag == 1:
                            flag = 0

                else:
                    final = []
                    for line in raw:
                        sline = line.strip()
                        aline = re.sub(r"^\s+", "", sline)

                        # print(f'stripped - {aline}')
                        if aline.startswith(self.globalplist):
                            plbname = sline.split()[1]
                            # print(f'-plbname-{plbname}--COOL-- {plb_to_remove}')
                            if plbname in plb_to_remove:
                                # print(f'-plbname-{plbname} -- YES')
                                ln = re.match(r'(.*)\s*(\[\s*PostPattern\s*.*DTSTEMPREAD\w*\])\s*(.*)', sline)
                                if ln:
                                    # print(f'-SEE-{ln.group(1) + " " + ln.group(3)} --')
                                    final.append(ln.group(1) + " " + ln.group(3))
                                else:
                                    final.append(line)
                            else:
                                final.append(line)
                        else:
                            final.append(line)

                if final != raw:
                    fname = File(f'{self.dest}/{basename(inputfname)}').get_name()
                    File(fname).rewrite(''.join(final), 'CleanPPR()')
                    OtplFile(fname).reformat()

                else:
                    print(rf'Did not create new plist file for {inputfname} to clean up PostPattern since no changes were identified or PostPattern not meeting regex (.*)\s*(\[\s*PostPattern\s*.*DTSTEMPREAD\w*\])\s*(.*)')
        else:
            print('no plists were identified to be cleaned up for PPR')

    def get_plb_for_PPR_untag(self, gppr_dict):
        """Return plb that needs to have PostPattern removed"""
        testnames = set()

        all_subflows = self.tpobj.mtpl.get_subflows()
        for item in self.all_flows:
            if item in all_subflows:
                testnames.update(tname for mod, tname in self.tpobj.mtpl.iter_flows(item, bypass=True))

        plb_PPR_untag = set()
        plb_PPR_tag = set()
        for mod, tname, dd, _ in self.tpobj.mtpl.iter_tests(key_name='patlist', edict=False):
            if (tname in testnames) and (tname in gppr_dict.keys()):
                if ("DtsConfiguration" in dd) and (dd["DtsConfiguration"] != ""):
                    # print(f' RETAIN PPR {tname}')
                    plb_PPR_tag.update({remove_ip(item) for item in CleanTP.get_value_tosrule(self.tpobj, dd['patlist'], mod)})
                    continue
                else:
                    # print(f' REMOVE {tname} {dd["patlist"]}')
                    plb_PPR_untag.update({remove_ip(item) for item in CleanTP.get_value_tosrule(self.tpobj, dd['patlist'], mod)})
            else:
                # print(f' REMOVE {tname} {dd["patlist"]}')
                plb_PPR_untag.update({remove_ip(item) for item in CleanTP.get_value_tosrule(self.tpobj, dd['patlist'], mod)})

        print(f'plb PPR {plb_PPR_untag} && {len(plb_PPR_untag)} ## {len(plb_PPR_tag)} ^^ {plb_PPR_tag}')
        return (plb_PPR_untag - plb_PPR_tag)

    def read_PPR_config(self):
        """Read PPR Global Config file and return dictionary {TestInstance: Module}"""

        gppr_data = JsonRead(
            File(f'{self.tpobj.tpldir}/Modules/PPR/InputFiles/GlobalPPRconfiguration.json').get_name(),
            error_out=False
        ).load()
        tests_mod_pair = defaultdict(set)
        gppr_dict = defaultdict(set)

        all_subflows = self.tpobj.mtpl.get_subflows()
        for item in self.all_flows:
            if item in all_subflows:
                for mod, tname in self.tpobj.mtpl.iter_flows(item, bypass=False):
                    tests_mod_pair[tname] = mod

        for item in gppr_data.get("PPRTargetTests", {}).keys():
            if '::' in item:
                elems = item.split('::')
                mod = elems[-2]
                test = elems[-1]
                # print(f'testname for PPR {test}')
                robj = re.compile(f"{test}")
                for tname in tests_mod_pair.keys():
                    match = robj.findall(tname)
                    # print(f'MATCH {match} $$ {tname}')
                    if match:
                        gppr_dict[tname] = tests_mod_pair[tname]

        # print(f'final {gppr_dict} && {len(gppr_dict)}')
        return gppr_dict

# \rm -rf autoctr.sbx ; cp -pdr /intel/tpvalidation/hdmxprogs/arl/ARLXXXXXXX65C0YSXXX autoctr.sbx ; chmod g+w autoctr.sbx ; cd autoctr.sbx

# apr15 status, run#4, https://github.com/intel-restricted/class_arls68/actions/runs/8675579521
# failed init due to dedc
#   2467 [DUT: 11_IP_PCH]ERROR: Class=[iCDEDCTest] Instance=[IP_PCH::ARR_GT_GXX::XSA_X_VMIN_E_CGTF6_X_X_X_X_DEDC] Function=[DedcMode::Serialize] File=[GEN_DEDC_xml.cpp] Line=[14
#   2468 Failed Generating EDC Flow within Trigger=[GT_SSA_CHKF2_1]
# Unable to find Segment=[IP_PCH::ARR_GT_GXX::DPSSA_X_SHMOO_E_CGTF6_X_VCCGT_F6_X_DEDCSHMOOTC].
# file: Modules/ARR_GT_GXX/InputFiles/ARR_GT_GXX_DEDC_PROD_P682.xml, defined in Test iCDEDCTest, config_file param
# fix: add get_dedc()

# apr22 status, run#7
# [2024-Apr-22 11:29:34.224][C][TAL][DUT: 11] Encounter error while executing flow item 'Flows::INIT::FUS_FUSEREAD_SXX_INIT': Attempt to execute flow FUS_FUSEREAD_SXX::FUS_FUSEREAD_SXX_INIT when no start item is defined
# fix: temporary: specific instance cannot be removed
# fix: Do not remove init hardcoded bypass, just MAIN. There are 87 INIT instances that got removed which are hardcoded bypassed=1.

# run8:
# ARR_MBIST_C68K_DEDC.json, "Name": "ARR_MBIST_C68K::XSA_CDIE_SHMOO_E_DEDC_X_VNNAON_F1_X_X",
# Test DedcLoadConfigTC MBIST_X_DEDC_K_INIT_X_X_X_X_CONFIG

# run9: pass init but failed b98: /intel/engineering/dev/team_classtp/torch/testerload/2024-04-22/ituff_CLASSHOT_TestUnitLog_2024-04-22-19-11-28.txt.gz

# -i- Count of everything:      16317
# -i- Count of connected:       11377
# -i- Count of floating:        4940
# -i- Count of hardcode bypass: 1022
# -i- Count of no_remove:       103

# run11: commented out hardcode bypass: still b98; Some DUTFlow items are removed, those which are "not connected" by iter_flow.

# run12: Pass Bin1: Limit the .mtpl changes to ARR,FUN,SCN

# run13: Limit .mtpl changes to non-base modules: Result b98

# run14: timeout of run15
# run15: bin1:  base + CLK,FUS,PTH,QNR. Thus it is one of these four modules.
# run16: bin1:  TPI, FUS, CLK skipped
# run17: bin1:  FUS, CLK skipped
# run18: bin98: FUS skipped
# run19: bin1:  CLK skipped <<<< root cause module

# run20: bin98: with hardcode bypass all modules
# run21: bin98: hardcode bypass for ARR,FUN,SCN only
# run22: bin1:  hardcode bypass for ARR,FUN,SCN only with logic fix (do not delete first dfi)
# run23: bin1:  hardcode bypass for all (MAIN) only <<<< success
# run24: bin1:  65D0D pass, POR using 5d2eba commit, 04/26

# mtl run1: fix regex of dedc_evg
# mtl run2: brita does not like empty DUTFlow blocks, ARR_MBIST_IXPK::RASTER
# mtl run3: fail init: RESET_X_FUNC_K_BEGCPU_X_INF_X_X_LR_PHASE2 is used in iCInstLoopTest
# Thus, mtl/evg will not be supported, too many corner cases on evg: https://github.com/intel-restricted/mtlp68/actions/runs/8862637290

# 06/12 run: \rm -rf autoctr.sbx ; cp -pdr /intel/tpvalidation/hdmxprogs/arl/ARLXXXXXXX66B0JSXXX autoctr.sbx ; chmod g+w -R autoctr.sbx ; cd autoctr.sbx ; \rm -rf astra
# run1: Failed due to tos4 syntax - fixed
# run2: Failed init due to SetPointsRegEx in PrimePauseTestMethod. Cannot remove these patterns.
# run 07/06: https://github.com/intel-restricted/class_arls68/actions/runs/9769185768/job/27121958822
#            /intel/engineering/dev/team_classtp/torch/testerload/2024-07-06/CLASSHOT_initLog_2024-07-06-18-58-41.txt
#            Some instances are failing for some reason on removed patterns. Module owner need to tell why.
#            ~30% pattern removal for cleantp
# run 07/13: Failed for scoping
# run 07/14: Failed for .ptm
# run 07/15: Failed for inherit
