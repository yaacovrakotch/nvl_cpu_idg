#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Strategy:
mod/db_ctp.py       - This file, connect to db and all routines
main/upload_ctp.py  - Executable from unix
main/ctp_hsd_cgi.py - cgi file

DONE:
1. date is 7 digit 2023115
2. .txt in torch repo on handshake (not using *.json)
3. yml output is speedid folder
4. change product is speedid; output dir is speedid folder
5. speedid correct on ww=toc and ww=<value>
6. tpname in toc is 4 char only (on output of api)
7. socket matching
8. toc for all products incuding json
9. add the dummy - json for mock
10. detail=true will give both hsd and ctp details (summary query)
11. debug the milestone, it seems not making impact
12. show summary even if there is no new ctp (aka, new hsd)
13. Return "live" data if ww=today for hsd on summary
14. enable cron hsd and output2_csv
15. Fix the "+1w" to become "+1"
16. return empty on error. Add debug=True
17. debug EDC=True. RootCause: all caps EDC vs edc. Fixed in code.
18. Always return hsd, even if no hsd data (case 3 and case 5 of ww)
19. add syntax check in pipeline. xls2json add label on success after sleep. New yml label based, use gh pr diff, this is PR gate in settings.
20. hsd to look at json config to get official speedid
21. use speedid config to get hsd url
22. disable old mongo upload

TODO:
0. bug: ww() api output on ww=<value> only show one Make sure logic is CRNT for default and use non-CRNT for exact ww match.
1. gh pr comment -b "<pre>line<br></pre>"
2. check for (enumerated) validity on por_tp: PO, POE, ES1, PTI, ES2, QS, PRQ (this is from justin)
3. Enforce unique Alias per Speed ID (justin request)
5. empty module means module where ctp.txt come from  (New args)
6. ctp repo pr_gate to check correctness of plans_setting. New check item and yml add.
7. multiple match on level param: voltage column but something like core_prog=1.1v, atom_prog=2v. See analyze_voltage()
8. unittest on tp_plans -check, check coverage
9. multiple found refactor
10. corner case: today and there are two records (A1E and CRNT); yesterday and two records A1E and CRNT
11. Consolidate ctp_cron and upload_ctp to be one cron only
"""
import urllib3
import csv
import json
import os
import re
import time
import requests
import base64
from collections import defaultdict
from datetime import datetime
from os.path import dirname, basename, exists
from pprint import pprint
import sys
import glob
from datetime import datetime
from json import JSONDecodeError

# do some monkey of path so that we can run in suse11 py3.6.3; anaconda does not work on suse11
sys.path.insert(0, '/intel/tpvalidation/engtools/tptools/mtl/tools/py3modules')
sys.path.insert(0, '/p/pde/tvpv/flash_tools/sw_tools/anaconda3.8/lib/python3.8/site-packages')

import pymongo
from pymodm import EmbeddedMongoModel, MongoModel
from pymodm import connect as mongo_connect
from pymodm import fields
from pymodm.errors import ValidationError

from gadget.strmore import workweek


def connect():
    """
    Connect to the database
    Unix only due to pymodm since it needs anaconda3
    """
    # TO USE: bytes.fromhex(url).decode()
    # TO ENCODE: url.encode().hex()
    with open('/intel/tpvalidation/engtools/tptools/mtl/configs/mongo.url.txt') as fh:
        url = fh.read().strip()

    # successful connect on python 3.6.3 if bson, pymodm and pymongo modules are from ana3
    mongo_connect(bytes.fromhex(url).decode(), tlsAllowInvalidCertificates=True)


def call_json_api(url):       # pragma: no cover  - tested in test_ctp_hsd_cgi.py
    """
    Call a url for json api

    :param url: url
    :return: python data structure
    """
    headers = {'Content-Type': 'application/json'}
    proxy = {'http': '', 'https': ''}
    r = requests.get(url, headers=headers, proxies=proxy, verify=False)
    try:
        return r.json()
    except JSONDecodeError as e:
        from gadget.errors import ErrorInput     # some debug message is printed if this is in front
        print("====== Web output start ======")
        print(r.text)
        raise ErrorInput(f'json error: {e}',
                         'See [=== Web output start ===] message above for actual web output')


class WW:
    opt = {}

    @classmethod
    def today(cls):
        """
        For easy unittest
        :return: today in seconds
        """
        return time.time()

    @classmethod
    def get_ww(cls, ff=None, secs=None):
        """
        Return the ww of timestamp of the file or secs or current ww

        :param ff: optional: file path
        :param secs: optional: secs
        :return: YYYY.wwWW.D
        """
        if ff:
            secs = os.path.getmtime(ff)
        elif secs is None:
            secs = cls.today()

        return workweek(secs=secs)

    @classmethod
    def to_int(cls, ywd):
        """
        This is not epoch seconds.

        :param ww: YYYY.wwWW.D or YYYYwwd
        :return: Return a sequential int representation of ww
        """
        # calculate the adder, in weeks
        adder = 0
        if '-' in ywd:
            ywd, adder = ywd.split('-')
            try:
                adder = int(adder.lower().replace('w', '')) * (-1)
            except ValueError:
                adder = 0

        if '+' in ywd:
            ywd, adder = ywd.split('+')
            try:
                adder = int(adder.lower().replace('w', ''))
            except ValueError:
                adder = 0

        if '.' in ywd:
            y, w, d = ywd.split('.')
            ww = int(w.lower().replace('ww', ''))
            yy = int(y)
            dd = int(d)
        else:
            assert len(ywd) == 7, f'Expecting YYYYwwD: {ywd}'
            yy = int(ywd[:4])
            ww = int(ywd[4:6])
            dd = int(ywd[-1])
        return (yy * 53) + ww + (dd / 10) + adder

    @classmethod
    def ispast(cls, today, target):
        """

        :param today: YYYY.wwWW.D
        :param entry: entry date: YYYY.wwWW.D
        :return:
        """
        to_int_today = cls.to_int(today)
        to_int_target = cls.to_int(target)
        if to_int_target <= to_int_today:
            return 1       # past
        return 0

    @classmethod
    def get_milestone(cls, item, default=None):
        """
        Return the milestone workweek, If not found return today's date
        Will set aside -<n> or +<n> for now. That is calculated later in to_int()
        """
        if default is None:
            default = cls.get_ww()

        realitem = item.replace(' ', '')   # no space
        nn = ''
        if '-' in realitem:
            realitem, nn = realitem.split('-')
            nn = f'-{nn}'
        if '+' in realitem:
            realitem, nn = realitem.split('+')
            nn = f'+{nn}'

        final = cls.opt.get(realitem, default)
        return f'{final}{nn}'


class CtpRepo:
    if os.environ.get('USER', 'p6vector') == 'p6vector':
        REPO_PATH = '/nfs/pdx/disks/mpe_sctp_004/torch/repo_checkouts/tp_plans'
    else:
        REPO_PATH = '/intel/tpvalidation/engtools/tptools/mtl/plan_waivers/jqdelosr_git/tp_plans'

    @classmethod
    def git_pull(cls, ispull, interval=10 * 60):
        """Do a git pull once every 10 mins - since new json config mapping may exist due to compas"""
        from gadget.lockfile import force_refresh
        from gadget.shell import SystemCall
        os.chdir(cls.REPO_PATH)

        # web git stuff
        os.environ["https_proxy"] = 'http://proxy-dmz.intel.com:912'
        if 'HOME' not in os.environ or 'USER' not in os.environ:
            os.environ['USER'] = 'p6vector'
            os.environ['LOGNAME'] = 'p6vector'
            os.environ['HOME'] = '/nfs/site/home/p6vector'
            os.environ['WEBPYTPD'] = 'True'    # Indicator that this is web run

        # git pull
        cwd = os.getcwd()
        age = os.path.getmtime(cwd)
        if (time.time() - age) > interval or ispull:
            force_refresh(cwd)
            cmd = f"/usr/intel/pkgs/git/2.23.0/bin/git pull"
            res = SystemCall(cmd).run_sout_serr()

    @classmethod
    def all_speedid(cls):
        """Iterator, return list of speedid in repo"""
        for ff in os.listdir(f'{cls.REPO_PATH}/ProductConfig'):
            if ff.endswith('.json') and ff.replace('.json', '').isdigit():
                yield ff.replace('.json', '')


class MainCgi:
    """Called from ctp_hsd_cgi.py - Main cgi call"""
    MOCKID = '10043978'

    def __init__(self, opt, is_conn=True, is_conn2=True):
        """

        :param opt: dictionary opts
        :param is_conn: Set to False for unittests
        :param is_conn2: Set to False if connect() is called outside of MainCgi
        """
        self.opt = opt
        WW.opt = opt     # Assign it one time
        self.isdetail = bool(opt.get('detail') == 'True')

        if is_conn and is_conn2:
            connect()

        # ==== start of commands
        if opt.get('toc') == 'hsd':     # pragma: no cover    - unused by justin
            result = self.toc_hsd_UNUSED()

        elif opt.get('toc') == 'evg':
            result = self.evg()

        elif (not is_conn):
            result = ['ut']

        elif opt.get('speedid') == self.MOCKID and 'ww' in opt:
            result = self.mock_ww()

        elif opt.get('speedid') == self.MOCKID and opt.get('toc') == 'ww':
            result = self.mock_toc()

        elif opt.get('toc') == 'ww':    # Show all ww+TPName given speedid
            result = self.toc()

        elif opt.get('toc') == 'all':   # TOP level TOC
            result = self.product()

        elif opt.get('toc') == 'map':   # Show the ProductConfig given speedid
            result = self.map()

        elif opt.get('owner', '').lower() == 'true':
            result = OwnerTP().main(opt.get('tp'))

        elif 'ww' in opt:               # Show summary given ww+speedid
            result = self.ww()

        elif 'ut' in opt:
            pass   # unittest for exception cases

        else:
            # live hsd data for one speedid
            result = {}
            for speedid in CtpRepo.all_speedid():
                result[speedid] = HsdRead(opt.get('speedid', speedid)).read_hsd()

        # display it
        if opt.get('indent'):
            print(json.dumps(result, indent=3))
        elif opt.get('internal'):
            self.result = result
        else:
            print(json.dumps(result))

    def _evg(self):
        """json api evg prime report"""
        from mod.cci_list import CCI
        from gadget.helperclass import CaptureStdoutLog
        from main.tp_audit import TPInfo

        cci = CCI('na', 50, repo=self.opt.get('repo'))
        cci.read_config()
        cci.set_chdir()

        with CaptureStdoutLog(disp=False):
            cci._git_pull(submodule=True)

        return TPInfo.evg()

    def mock_toc(self):
        """Mock data toc"""
        with open(f'/nfs/site/disks/pdel.intel11/tpvalidation/jqdelosr/temp/forjames/ctp/toc_details.json') as fh:
            return json.load(fh)

    def mock_ww(self):
        """Mock data ww"""
        with open(f'/nfs/site/disks/pdel.intel11/tpvalidation/jqdelosr/temp/forjames/ctp/{self.opt["ww"]}.json') as fh:
            return json.load(fh)

    def map(self):
        if 'speedid' not in self.opt:
            return [{'error': 'speedid arg in url is requred'}]

        CtpRepo.git_pull(self.opt.get('pull'))   # this will chdir
        path = f'ProductConfig/{self.opt["speedid"]}.json'
        if not os.path.exists(path):
            return [{'error': f'speedid={self.opt["speedid"]} is not found in ProductConfig/'}]

        with open(path) as fh:
            data = json.load(fh)

        # make sure no dup mheader
        uniq = set()
        for item in data[0]['contents']:
            if 'mheader' in item:
                if item['mheader'] in uniq:
                    return [{'error': f'mheader={item["mheader"]} is duplicate!'}]
                uniq.add(item['mheader'])

        return data

    def toc_hsd_UNUSED(self):        # pragma: no cover   - unused
        """Unused by justin"""
        data = HSDCache.data()
        uniq = set()
        for ctr, item in enumerate(data):
            uniq.add((item.product, item.step, item.socket))
        result = []
        for item in uniq:
            result.append({'product': item[0],
                           'step': item[1],
                           'socket': item[2]})
        return result

    def ignore_tp_list(self):
        """
        Return ctp ignore tp list

        To get all tpnames given speedid:
            CTPCache.fetch()
            for ctr, item in enumerate(CTPCache.data()):
                if item.product == '10047574':
                    print(item.tpname)
        """
        # Instead of deleting database, ignore data here for unneeded workweeks that is already in db
        return {'10047574': re.compile('(ARLXXXXXXX|ARLXXXXB0H66A30S422)'),    # these are tpvalidation tp
                }

    def toc(self):
        """Primary toc"""
        ignore_tp_regex = self.ignore_tp_list()

        data = CTPCache.data()
        uniq_tpname = {}
        for ctr, item in enumerate(data):
            if item.product == self.opt['speedid']:
                if item.product in ignore_tp_regex and ignore_tp_regex[item.product].search(item.tpname):
                    continue    # skip this testprogram
                if 'socket' not in self.opt or item.socket.lower() == self.opt['socket']:
                    uniq_tpname[item.tpname] = item.ww     # assumed sorted oldest to newest

        # force CRNT is today
        uniq_tpname['CRNT'] = WW.get_ww()
        items = []
        for tpname in sorted(uniq_tpname, key=uniq_tpname.get):
            items.append({'ww': uniq_tpname[tpname],
                          'tpname': Summary.tpname4(tpname)})

        return [{'contents': items}]

    def ww(self):
        """Summary, given ww and speedid"""

        assert 'speedid' in self.opt, 'speedid not specified in url'

        ignore_tp_regex = self.ignore_tp_list()
        result = []
        item_ww = []

        # ctp first
        data = CTPCache.data()
        item_crnt = None
        item_last = None
        for ctr, tmp_item in enumerate(data):
            if tmp_item.product != self.opt['speedid']:
                continue
            if tmp_item.product in ignore_tp_regex and ignore_tp_regex[tmp_item.product].search(tmp_item.tpname):
                continue    # skip this testprogram
            if 'socket' not in self.opt or tmp_item.socket.lower() == self.opt['socket']:
                item_last = tmp_item
                if tmp_item.tpname == 'CRNT':
                    item_crnt = tmp_item
                if tmp_item.ww == self.opt['ww']:
                    item_ww.append(tmp_item)

        # if no items found, use crnt first, else last item
        if not item_ww:
            if item_crnt:
                item_ww.append(item_crnt)
            elif item_last:
                item_ww.append(item_last)

        for item in item_ww:
            row_fields = 'module testinstance flags status ErrorMessage ContentExpect ContentActual ConditionComplete edc PorPlan'.split()
            top_fields = 'tpname product step socket ww'.split()
            tp = {x: getattr(item, x) for x in top_fields}
            records = []
            for rec in item.records:
                records.append({x: getattr(rec, x) for x in row_fields})
            tp['records'] = records

            onerec = Summary.ctp(tp)             # This has the headers
            onerec[0]['last_update'] = onerec[0]['ww']
            onerec[0]['ww'] = self.opt['ww']     # return what is being asked
            if self.isdetail:
                onerec[0]['records'] = records   # CTP details
            result.append(onerec[0])

        # HSD next
        for idx in range(len(result)):
            if WW.to_int(self.opt['ww']) == WW.to_int(WW.get_ww()):    # If current week
                try:
                    # data = HsdRead(self.opt['speedid']).read_hsd()
                    # valid = [x for x in data.get('data', []) if x['socket'] == self.opt.get('socket', x['socket'])]
                    valid = []
                    data = {'data': valid}
                except json.decoder.JSONDecodeError:
                    data = {'data': []}
                    result[idx]['hsd_fail_info'] = 'Failed hsd query.'
                hsd_result = Summary.hsd(data['data'])
                result[idx]['summary'].extend(hsd_result)

                if self.isdetail:
                    result[idx]['hsdrecords'] = data['data']   # HSD details

            else:
                # hsd next. If there is no record for that ww, then pick the previous one.
                item = None
                for ctr, tmp_item in enumerate(HSDCache.data()):
                    if tmp_item.product == self.opt['speedid']:
                        if 'socket' not in self.opt or tmp_item.socket.lower() == self.opt['socket']:
                            if WW.to_int(tmp_item.ww) <= WW.to_int(self.opt['ww']):
                                item = tmp_item

                if item:
                    row_fields = 'title state team feature sd_plan edc_plan por_plan'.split()
                    records = []
                    for rec in item.records:
                        records.append({x: getattr(rec, x) for x in row_fields})

                    hsd_result = Summary.hsd(records)
                    result[idx]['summary'].extend(hsd_result)

                    if self.isdetail:
                        result[idx]['hsdrecords'] = records   # HSD details

        # Compass next
        Compas.main(result, self.opt['speedid'])

        # Overrides
        if self.opt.get('override') == 'True':
            Overrides(self.opt['speedid']).override(result)

        return result

    def product(self):
        """Give all products"""
        cfg = f'{CtpRepo.REPO_PATH}/ProductConfig'
        uniq = {(MainCgi.MOCKID, 'sds')}

        # data = list(Hsd.objects.all())
        # for ctr, item in enumerate(data):
        #     uniq.add((item.product, item.socket.lower()))

        for ctr, item in enumerate(CTPCache.data()):
            uniq.add((item.product, item.socket.lower()))

        result = []
        for item in sorted(uniq):
            if exists(f'{cfg}/{item[0]}.json'):
                if item[1] == 'b':
                    continue
                result.append({'speedid': item[0],
                               'socket': item[1]})

        return [{'contents': result}]


class OwnerTP:
    path_list = ('/intel/tpvalidation/hdmxprogs/nvl',
                 '/intel/hdmxprogs/nvl',
                 '/intel/tpvalidation/engtools/tptools/mtl/infra/torch/repo_checkouts')

    def main(self, tp):
        """
        Return owner/manager: See https://wiki.ith.intel.com/display/ITSpdxtp/NVL+Module+Owner+Lookup+Table+for+Lists
        """
        for rpath in self.path_list:
            foundpath = f'{rpath}/{tp}'
            if os.path.isdir(foundpath):
                break
        else:
            final = {'Error': f'Cannot find {tp}. See below for valid TP.'}
            for rpath in self.path_list:
                final[rpath] = sorted(x for x in os.listdir(rpath) if 'nvl' in x.lower())
            return final

        found = glob.glob(f'{foundpath}/**/owner.txt', recursive=True)
        robj1 = re.compile(r"owner:\s+(\w.*)$", re.MULTILINE)
        robj2 = re.compile(r"manager:\s+(\w.*)$", re.MULTILINE)
        final = {}

        # delete env file - for web
        for k in os.environ:
            if k in ('PATH', 'LD_LIBRARY_PATH'):
                continue
            del os.environ[k]

        for item in found:

            module = basename(dirname(item))
            if module == 'InputFiles':
                module = basename(dirname(dirname(item)))

            final[module] = {}

            with open(item) as fh:
                text = fh.read()

            res = robj1.search(text)
            if res:
                final[module]['owner'] = self.get_last_first(res.group(1))

            res = robj2.search(text)
            if res:
                final[module]['manager'] = self.get_last_first(res.group(1))

        return final

    def get_last_first(self, idsid):
        """Return the last, first"""
        if idsid.endswith('Members'):
            return idsid    # as-is

        if '/' in idsid:
            idsid = idsid.split('/')[0]    # get first one

        root = '/intel/tpvalidation/engtools/tptools/mtl/infra/torch/idsid_db'
        if exists(f'{root}/{idsid}'):
            with open(f'{root}/{idsid}') as fh:
                return fh.read().strip()

        from gadget.shell import SystemCall
        out = SystemCall(f'/usr/intel/bin/cdislookup -u {idsid}').run_outonly()
        res = re.search(r"ccMailName\s+=\s*(.*)$", out, re.MULTILINE)
        if res:
            value = res.group(1)
        else:
            value = f'{idsid} (not-found)'    # asis

        # cache it
        with open(f'{root}/{idsid}', 'w') as fh:
            fh.write(f'{value}\n')

        return value


class Compas:
    """Compass routines"""
    ALL_DATA = '/intel/tpvalidation/engtools/tptools/mtl/plan_waivers/db_compass/latest'

    @classmethod
    def main(cls, result, speedid):
        """Add compass items into result"""

        # temporary hack for arl-s68
        # if speedid == '10047574':
        #     speedid = '10047572'

        # Read the product config
        jfile = f'{CtpRepo.REPO_PATH}/ProductConfig/{speedid}.json'
        if not os.path.exists(jfile):
            return    # not found, skip compas
        with open(jfile) as fh:
            datacfg = json.load(fh)
        cfg = datacfg[0]

        # Read the compass data
        with open(cls.ALL_DATA) as fh:
            data = json.load(fh)

        # Add the compass records into result
        stepping = cfg.get('compass_stepping', 'A0')
        for item in result:
            ww = item['ww']
            socket = item['socket']
            cmap = cls.get_cmap(cfg.get('compass_map', []), socket)
            for item2 in cfg['contents']:
                if 'mcompass' in item2:
                    rec = cls.one_ww(speedid, ww, item2['mcompass'], stepping, data, cmap)
                    rec['mteam'] = item2['mteam']     # use mteam from productconfig
                    item['summary'].append(rec)

    @classmethod
    def get_cmap(cls, compass_map, socket):
        """Return the cmap dict: {compass_key: powerbi_key}"""
        result = {}
        for item in compass_map:
            if item['cps_skt'] == socket:
                for k, v in item.items():
                    if k == 'cps_skt':
                        continue
                    if isinstance(v, list):
                        for vitem in v:
                            result[vitem.lower()] = k
                    else:
                        result[v.lower()] = k
        return result

    @classmethod
    def one_ww(cls, speedid, ww, team, stepping, data, cmap):
        """Return one data given speedid, ww, team"""
        result = defaultdict(list)
        cww = int(f'{ww[2:4]}{ww[7:9]}')
        for idx, item in enumerate(data):
            if (item['product_code_plc'] == int(speedid) and
                    item['team_name'] == team and
                    item['stage_id'] == 'Post-Si' and
                    item['stepping'] == stepping):
                for dataset in item['dataset']:
                    if dataset['yyww'] == cww:
                        for col in dataset['dynamic_column']:
                            if col['name'].lower() in cmap:
                                result[cmap[col['name'].lower()]].append(col['value'])

        # Do the average
        final = {k: sum(v) / len(v) for k, v in result.items()}
        final['source'] = 'compass'

        # Do the recalc ===========
        # cps_por = currently calculated cps_por (no change)
        # cps_edc = current cps_edc - cps_por, if <0 set to 0
        # cps_sd = current cps_sd - cps_por - (new) cps_edc, if <0 set to 0
        # compass gives 95(por) 90(edc) 90(sd) this should return 95/0/0
        # compass gives 95(por) 96(edc) 98(sd) this should return 95/1/2
        for item in 'cps_por cps_edc cps_en cps_por_plan cps_edc_plan cps_en_plan'.split():
            if item not in final:
                final[item] = 0
        final['cps_edc'] = final['cps_edc'] - final['cps_por']
        if final['cps_edc'] < 0:
            final['cps_edc'] = 0
        final['cps_en'] = final['cps_en'] - final['cps_por'] - final['cps_edc']
        if final['cps_en'] < 0:
            final['cps_en'] = 0

        final['cps_edc_plan'] = final['cps_edc_plan'] - final['cps_por_plan']
        if final['cps_edc_plan'] < 0:
            final['cps_edc_plan'] = 0
        final['cps_en_plan'] = final['cps_en_plan'] - final['cps_por_plan'] - final['cps_edc_plan']
        if final['cps_en_plan'] < 0:
            final['cps_en_plan'] = 0

        return final


class Overrides:
    """
    Capability to override returned data with historical support
    See wiki on usage and notes
    This assumes that webserver is located in JF because of the override.

    Strategy:
    1. Raw data is in mongo
    2. Override data is in nfs.
    3. api call is readonly to the nfs path
    4. Every midnight, in cron, save() is called that will save snapshot per-day of the override data
    """

    def __init__(self, speedid):
        self.speedid = speedid
        self.root = f'/intel/tpvalidation/engtools/tptools/mtl/plan_waivers/db_ctp2'

    def save(self):
        """Save all the overrides, for all speedid for this day - historical"""
        from gadget.disk import mkdirs
        from gadget.files import File
        ww = WW.get_ww()
        for speedid in CtpRepo.all_speedid():
            self.speedid = speedid
            data = self.get_crnt()
            if data:
                mkdirs(f'{self.root}/{self.speedid}', mode='02770')
                target = f'{self.root}/{self.speedid}/{ww}.json'
                with open(target, 'w') as fh:
                    json.dump(data, fh, indent=3)
                File(target).chmod('02770')
                print(f"Written: {target}")

    def get_crnt(self):
        """Return current overrides"""
        os.chdir(CtpRepo.REPO_PATH)
        path = f'ProductConfig/{self.speedid}.json'
        if not os.path.exists(path):
            return [{'error': f'{path} is not found'}]
        with open(path) as fh:
            data = json.load(fh)
        if 'overrides' not in data[0]:
            return []

        return data[0]['overrides']

    def get_historical(self, ww):
        """Return overrides for this ww"""
        target = f'{self.root}/{self.speedid}/{ww}.json'
        if exists(target):
            with open(target) as fh:
                return json.load(fh)
        return []

    def override(self, result):
        """Main entry point, with try/except"""
        try:
            result = self._override(result)
        except Exception as e:
            result[0]['override_failed'] = str(e)
        return result

    def _override(self, result):
        """
        Overrides
        Read the config, override the result if it exist
        1. Only for CRNT for codify
        2. For compass, copy as is
        3. For codify, use socket+mheader to match
        4. For hsd, use socket+team to match
        """
        # for tpname items
        for ritem in result:
            if ritem['tpname'] == 'CRNT':
                overrides = self.get_crnt()
            else:
                overrides = self.get_historical(ritem['ww'])

            resultsum = ritem['summary']
            for idx in range(len(resultsum)):
                for item in overrides:
                    if item['source'] == resultsum[idx]['source'] and item['source'] == 'codify':
                        for head in item['mheader'].split(','):
                            head = head.strip()
                            if '_found' not in item and ritem['socket'] == item['socket'] and resultsum[idx]['module'].startswith(head):
                                self._set_value(item, resultsum[idx])

                    if item['source'] == resultsum[idx]['source'] and item['source'] == 'hsd':
                        if ritem['socket'] == item['socket'] and resultsum[idx]['team'] == item['team']:
                            self._set_value(item, resultsum[idx])

                    if item['source'] == resultsum[idx]['source'] and item['source'] == 'compass':
                        if ritem['socket'] == item['socket'] and resultsum[idx]['mteam'] == item['mteam']:
                            self._set_value(item, resultsum[idx])

            # last, append not found
            for item in overrides:
                if '_found' not in item and ritem['socket'] == item['socket']:
                    item['override'] = 'True'
                    resultsum.append(item)   # as-is

    def _set_value(self, item, resultsum_idx):
        """
        Set the override values
        :param item: one override item block
        :param resultsum_idx: result block
        """
        item['_found'] = True
        resultsum_idx['override'] = 'True'
        for field in item:
            if field in ('source', 'socket', 'mteam', 'mheader', '_found', 'module'):
                continue
            resultsum_idx[field] = item[field]


class Summary:

    @classmethod
    def tpname4(cls, tpname):
        """Return the 4 char tpname"""
        if tpname == 'CRNT':
            return tpname
        return tpname[-9:-5]

    @classmethod
    def div_zero(cls, a, b, isnull=False):
        """Divide a/b, but retunr return 0 if b is zero"""
        if not b:
            if isnull:
                return None
            else:
                return 0
        return a / b

    @classmethod
    def ctp(cls, data):
        # data = data[0]    # one record only?
        if 'records' not in data:
            return None

        total_condition = {}    # Do not use defaultdict here to make sure datastructure is properly initialized
        total_content = {}
        por_condition = {}
        blk_condition = {}
        edc_condition = {}
        por_content = {}
        blk_content = {}
        edc_content = {}
        por_plan = {}
        featuremiss = {item['testinstance'] for item in data['records'] if item['flags'] == 'FeatureMiss'}

        for item in data['records']:

            # initialize
            module = item['module']
            if module not in total_condition:
                total_condition[module] = 0
                total_content[module] = 0
                por_condition[module] = 0
                blk_condition[module] = 0
                por_content[module] = 0
                blk_content[module] = 0
                edc_condition[module] = 0
                edc_content[module] = 0
                por_plan[module] = 0

            # process all flags
            if item['flags'] == 'MultipleFound':
                # Ignore this, since MultipleFound rows will already show in MissingFromTP
                continue

            elif item['flags'] == 'MissingFromPlan':
                # Nothing to count here, these are extra stuff in TP
                continue

            elif item['flags'] == 'FeatureMiss':
                # These are already in Found as enabled. This is a detail of why it's a miss
                continue

            elif item['flags'] == 'Found':
                total_condition[module] += 1
                total_content[module] += item['ContentExpect']

                if item['status'] == 'POR':        # POR means it is KILL (with setbin)
                    por_content[module] += min(item['ContentActual'], item['ContentExpect'])
                elif item['status'] == 'BLK':
                    blk_content[module] += min(item['ContentActual'], item['ContentExpect'])
                else:
                    edc_content[module] += min(item['ContentActual'], item['ContentExpect'])

                if item['testinstance'] not in featuremiss:
                    if item['status'] == 'POR':
                        por_condition[module] += 1     # POR means no condition miss, and it is in KILL
                    elif item['status'] == 'BLK':
                        blk_condition[module] += 1
                    else:
                        edc_condition[module] += 1

                por_plan[module] += WW.ispast(WW.get_ww(), WW.get_milestone(item['PorPlan']))

            elif item['flags'] == 'MissingModule':
                total_condition[module] += item['TestInsCount']
                total_content[module] += item['ContentExpect']

            elif item['flags'] == 'MissingFromTP':
                total_condition[module] += 1
                total_content[module] += item['ContentExpect']
                if 'blocked=True' in item['ErrorMessage']:
                    blk_condition[module] += 1
            else:
                raise Exception(f"Unknown flags: {item['flags']}")

        records = []
        for module in sorted(total_condition):
            rec_data = {'source': 'codify',
                        'module': module,
                        'content POR': cls.div_zero(por_content[module], total_content[module], True),
                        'content edc': cls.div_zero(edc_content[module], total_content[module], True),
                        'condition POR': cls.div_zero(por_condition[module], total_condition[module]),
                        'condition edc': cls.div_zero(edc_condition[module], total_condition[module]),
                        'por_plan': cls.div_zero(por_plan[module], total_condition[module])
                        }
            if blk_content[module]:
                rec_data['content blocked'] = cls.div_zero(blk_content[module], total_content[module])
                rec_data['condition blocked'] = cls.div_zero(blk_condition[module], total_condition[module])
            records.append(rec_data)

        return [{'tpname': Summary.tpname4(data['tpname']),
                 'product': data['product'],
                 'step': data['step'],
                 'socket': data['socket'],
                 'ww': data['ww'],
                 'summary': records}]

    @classmethod
    def hsd(cls, data):
        total = {}    # Do not use defaultdict here to make sure datastructure is properly initialized
        por = {}
        edc = {}
        blocked = {}
        por_plan = {}
        edc_plan = {}
        sd_plan = {}
        enabled = {}

        for item in data:

            if item['state'].lower() == 'rejected':
                continue

            # initialize
            module = (item['team'], item['feature'])
            if module not in total:
                total[module] = 0
                por[module] = 0
                edc[module] = 0
                blocked[module] = 0
                por_plan[module] = 0
                edc_plan[module] = 0
                sd_plan[module] = 0
                enabled[module] = 0

            total[module] += 1

            if item['state'].lower() == 'por':
                por[module] += 1
            elif item['state'].lower() == 'edc':
                edc[module] += 1
            elif item['state'].lower() == 'standing die':
                enabled[module] += 1
            elif item['state'].lower() == 'blocked':
                blocked[module] += 1

            # dates
            if item['sd_plan'] != 'n/a':
                sd_plan[module] += WW.ispast(WW.get_ww(), WW.get_milestone(item['sd_plan']))

            if item['edc_plan'] != 'n/a':
                edc_plan[module] += WW.ispast(WW.get_ww(), WW.get_milestone(item['edc_plan']))

            if item['por_plan'] != 'n/a':
                por_plan[module] += WW.ispast(WW.get_ww(), WW.get_milestone(item['por_plan']))

        records = []
        for team, feature in sorted(total):
            module = (team, feature)
            rec_data = {'source': 'hsd',
                        'team': team,
                        'feature': feature,
                        'POR': cls.div_zero(por[module], total[module]),
                        'edc': cls.div_zero(edc[module], total[module]),
                        'enabled': cls.div_zero(enabled[module], total[module]),
                        'por_plan': cls.div_zero(por_plan[module], total[module]),
                        'edc_plan': cls.div_zero(edc_plan[module], total[module]),
                        'sd_plan': cls.div_zero(sd_plan[module], total[module]),
                        }
            if blocked[module]:
                rec_data['blocked'] = cls.div_zero(blocked[module], total[module])
            records.append(rec_data)
        return records


class PAS(EmbeddedMongoModel):
    module = fields.CharField(required=True, max_length=20)
    testinstance = fields.CharField(required=True, max_length=256)

    # PAS
    status = fields.CharField(required=False, max_length=25)
    plist = fields.CharField(required=False, max_length=256)
    MonitorPatCount = fields.IntegerField(default=0)
    KillPatCount = fields.IntegerField(default=0)
    SkippedPatCount = fields.IntegerField(default=0)
    TestType = fields.IntegerField(default=0)
    ContentDirectory = fields.CharField(required=False, max_length=256)
    PatternRev = fields.CharField(required=False, max_length=64)
    Bins = fields.CharField(required=False, max_length=256)
    Counters = fields.CharField(required=False, max_length=256)

    class Meta:
        final = True
        ignore_unknown_fields = True

    def get_fields(self):
        """
        Helper function to get interal field objects.
        :return: MongoBaseField objects that are used by this MongoModel
        :rtype: list
        """
        return self._mongometa.get_fields()

    def get_field_names(self):
        """
        Helper function to get the names of fields.  Pymodm inheritance makes it hard to include these functions
        in an intermediate class, so they are reproduced and can't be consolidated
        :return: string names of the internal fields
        :rtype: list
        """
        return [x.mongo_name for x in self.get_fields()]


class CTPRows(EmbeddedMongoModel):
    module = fields.CharField(required=True, max_length=20)
    testinstance = fields.CharField(required=True, max_length=256)
    flags = fields.CharField(required=True, max_length=64)
    status = fields.CharField(required=False, max_length=64)
    ErrorMessage = fields.CharField(required=False, max_length=256)
    ContentExpect = fields.IntegerField(default=0)
    ContentActual = fields.IntegerField(default=0)
    ConditionComplete = fields.IntegerField(default=0)
    edc = fields.IntegerField(default=0)
    PorPlan = fields.CharField(required=False, blank=True, max_length=64)

    class Meta:
        final = True
        ignore_unknown_fields = True

    def get_fields(self):
        """
        Helper function to get interal field objects.
        :return: MongoBaseField objects that are used by this MongoModel
        :rtype: list
        """
        return self._mongometa.get_fields()

    def get_field_names(self):
        """
        Helper function to get the names of fields.  Pymodm inheritance makes it hard to include these functions
        in an intermediate class, so they are reproduced and can't be consolidated
        :return: string names of the internal fields
        :rtype: list
        """
        return [x.mongo_name for x in self.get_fields()]


class CTP(MongoModel):
    tpname = fields.CharField(required=True, max_length=50)
    product = fields.CharField(required=True, max_length=50)
    step = fields.CharField(required=True, max_length=50)
    socket = fields.CharField(required=True, max_length=50)
    ww = fields.CharField(required=True, max_length=50)

    # sub-document
    records = fields.EmbeddedDocumentListField(CTPRows)

    # MissingFromTP = fields.EmbeddedDocumentListField(CTPRows)
    # FeatureMiss = fields.EmbeddedDocumentListField(CTPRows)
    # MultipleFound = fields.EmbeddedDocumentListField(CTPRows)
    # MissingFromPlan = fields.EmbeddedDocumentListField(CTPRows)
    # Found = fields.EmbeddedDocumentListField(CTPRows)

    class Meta:
        final = True
        ignore_unknown_fields = True
        indexes = [
            pymongo.IndexModel([('product', pymongo.ASCENDING)]),
            pymongo.IndexModel([('step', pymongo.ASCENDING)]),
            pymongo.IndexModel([('socket', pymongo.ASCENDING)]),
            pymongo.IndexModel([('ww', pymongo.ASCENDING)])
        ]

    def get_fields(self):
        """
        Helper function to get interal field objects.
        :return: MongoBaseField objects that are used by this MongoModel
        :rtype: list
        """
        return self._mongometa.get_fields()

    def get_field_names(self, remove_id=True):
        """
        Helper function to get the names of fields.  Pymodm inheritance makes it hard to include these functions
        in an intermediate class, so they are reproduced and can't be consolidated
        :param remove_id: Do not include the '_id' field
        :type remove_id: bool
        :return: string names of the internal fields
        :rtype: list
        """
        doc_fields = [x.mongo_name for x in self.get_fields()]
        if remove_id:
            doc_fields.remove('_id')
        return doc_fields

    def update_from_document(self, doc):
        """
        Look at the passed in dictionary and update field values that exist within the passed in document
        :param doc: fields and values to update
        :type doc: dict
        """
        for field in self.get_field_names():
            if field in doc:
                self._data.set_mongo_value(field, doc[field])

    def increment_field(self, field, amount):
        """
        Helper function to increment the specified field value
        :param field: Name of the field to update
        :type field: str
        :param amount: amount to uncrease the field value by
        :type amount: int
        """
        if field not in self.get_field_names():
            raise KeyError(f"Invalid field {field}, cannot increment")

        setattr(self, field, getattr(self, field) + amount)


class UploadCtp:
    """Upload one csv file"""

    def __init__(self, file_csv):
        """
        output_ctp2/<speedid>_<socket>/<file>.csv
        output_ctp2/<speedid>_<stepping>_<socket>/<file>.csv

        :param file_csv: filepath, see above for structure
        :return:  None
        """

        # read csv
        csvrows = []
        with open(file_csv) as fh:
            reader = csv.reader(fh)
            for row in reader:
                csvrows.append(row)

        # initialize
        self.csvrows = [x for x in csvrows if x]    # remove empty
        foundplans = self.csv2dict('HeadFound', 'FoundPlan')
        self.found = [x['TestName'] for x in foundplans]    # list of testnames
        dname = basename(dirname(file_csv))
        assert '_' in dname, f'Directory name [{dname}] is expected to be: [<speedid>_<socket>] format'
        self.speedid = dname.split('_')[0]
        self.socket = dname.split('_')[-1]

        self.stepping = 'A'    # default

        # get the stepping from dname, if it is there
        if len(dname.split('_')) == 3:
            self.stepping = dname.split('_')[1].upper()

    def csv2dict(self, head, item):
        """
        Returns list of dictionary given header and item
        :param head: header
        :param item: item name
        :return: list of dictionary
        """
        headers = None
        result = []
        for row in self.csvrows:
            headcell = row[0]
            if headcell == head:
                headers = row
                continue
            if headcell == item:
                assert headers, f'No header {header} found for {item}'
                dd = {}
                for idx in range(len(headers)):
                    dd[headers[idx]] = row[idx]

                # remove modules that are invalid!
                if 'Module' in dd and len(dd['Module']) > 20:
                    print(f"-w- Skipping too long, Module: {dd['Module']}")
                    continue

                result.append(dd)
        return result

    def main(self):
        """Main upload routine"""
        if not self.csvrows:
            return 1

        # MissingFromTP
        rec_mft = []
        for dd in self.csv2dict('HeadMissingTP', 'MissingFromTP'):
            rec_mft.append({'flags': 'MissingFromTP',
                            'module': dd['Module'],
                            'testinstance': self.get_name_from_plan(dd['Detail']),
                            'ContentExpect': int(dd['tid_expect']) if dd['tid_expect'] else 0,
                            'ErrorMessage': dd['Detail'][:255]})

        # FeatureMiss
        rec_fms = []
        for dd in self.csv2dict('HeadFeatureMiss', 'FeatureMiss'):
            rec_fms.append({'flags': 'FeatureMiss',
                            'module': dd['Module'],
                            'testinstance': dd['TestName'],
                            'ErrorMessage': dd['Detail'][:255]})

        # MissingModule
        rec_mfo = []
        for dd in self.csv2dict('HeadMissMod', 'MissingModule'):
            rec_mfo.append({'flags': 'MissingModule',
                            'module': dd['Module'],
                            'ContentExpect': int(dd['tid_count']) if dd['tid_count'] else 0,
                            'testinstance': 'ALL',   # full name
                            'ErrorMessage': "Missing module: {dd['Module']}"})

        # MultipleFound
        rec_mfo = []
        for dd in self.csv2dict('HeadMultiple', 'MultipleFound'):
            rec_mfo.append({'flags': 'MultipleFound',
                            'module': dd['Module'],
                            'testinstance': dd['Detail'],   # full name
                            'ContentExpect': int(dd['tid_expect']) if dd['tid_expect'] else 0,
                            'ErrorMessage': dd['name']})    # regex

        # MissingFromPlan
        rec_mfp = []
        for dd in self.csv2dict('HeadMissingPlan', 'MissingFromPlan'):
            rec_mfp.append({'flags': 'MissingFromPlan',
                            'module': dd['Module'],
                            'testinstance': dd['Detail'],   # full name
                            'ContentActual': int(dd['tid_count']) if dd['tid_count'] else 0})

        # Found
        rec_fnd = []
        for dd in self.csv2dict('HeadFound', 'FoundPlan'):
            rec_fnd.append({'flags': 'Found',
                            'module': dd['Module'],
                            'ContentActual': int(dd['tid_count']) if dd['tid_count'] else 0,
                            'ContentExpect': int(dd['tid_expect']) if dd['tid_expect'] else 0,
                            'status': dd['PorEn'],
                            'PorPlan': dd['POR_plan'],
                            'testinstance': dd['TestName']})   # full name

        # tpname
        tpname = 'CRNT'
        ww = 'None'
        for dd in self.csv2dict('HeadTimeStamp', 'TimeStamp'):
            if dd['Module'] == '_TPNAME':
                dt = datetime.strptime(dd['Date_PlanFile'], '%Y-%m-%d_%H:%M:%S')
                ww = WW.get_ww(secs=dt.timestamp())
                if basename(dirname(dirname(dd['PlanFile']))) == 'POR_TP':
                    try_tpname = basename(dirname(dirname(dirname(dd['PlanFile']))))
                else:
                    try_tpname = basename(dirname(dd['PlanFile']))
                if len(try_tpname) in (19, 18):
                    tpname = try_tpname

        stepping = self.get_stepping(tpname, self.speedid, default=self.stepping)

        # main data
        data = {'tpname': tpname,
                'product': self.speedid,
                'step': stepping,
                'socket': self.socket,
                'ww': ww,
                'records': rec_mft + rec_fms + rec_mfo + rec_mfp + rec_fnd,
                }

        # find the record first (5 fields)
        found = None
        for itemxxx in CTP.objects.all():
            if ((itemxxx.tpname, itemxxx.product, itemxxx.step, itemxxx.socket) ==
                    (data['tpname'], data['product'], data['step'], data['socket'])):
                found = itemxxx

        if found is None:
            # write out new record
            obj = CTP.from_document(data)
            obj.save()
            print("Wrote New %r %r" % (tpname, ww))
        else:
            found.update_from_document(data)
            found.save()
            print("Wrote Upd %r %r" % (tpname, ww))

    def get_name_from_plan(self, detail):
        """Return the Plan name from detail"""
        res = re.search(r"Plan\('([^']+)'", detail)
        if res:
            return res.group(1)
        raise Exception(f'Cannot derive testinstance from {detail}')

    @classmethod
    def get_stepping(cls, tpname, speedid, default='A'):
        """Return the stepping given tpname"""
        try:
            if tpname != 'CRNT':
                assert tpname[7] != 'X'    # not a valid stepping
                return tpname[7]    # standard tpname convention

            # CRNT
            with open(f'{CtpRepo.REPO_PATH}/ProductConfig/{speedid}.json') as fh:
                data = json.load(fh)
            return data[0]['stepping']      # special key in ProductConfig (optional)

        except Exception:
            return default    # catch all


class HsdData(EmbeddedMongoModel):
    id = fields.CharField(required=True, max_length=25)
    title = fields.CharField(required=True, max_length=256)
    team = fields.CharField(required=False, blank=True, max_length=25)
    feature = fields.CharField(required=False, blank=True, max_length=50)
    state = fields.CharField(required=False, blank=True, max_length=25)
    priority = fields.CharField(required=False, blank=True, max_length=25)
    sd_plan = fields.CharField(required=False, blank=True, max_length=50)
    edc_plan = fields.CharField(required=False, blank=True, max_length=50)
    por_plan = fields.CharField(required=False, blank=True, max_length=50)
    owner = fields.CharField(required=False, blank=True, max_length=25)
    status = fields.CharField(required=False, blank=True, max_length=25)
    # comment is missing, which field is this?

    # project = fields.CharField(required=False, blank=True, max_length=50)
    # stepping = fields.CharField(required=False, blank=True, max_length=25)
    # socket = fields.CharField(required=False, blank=True, max_length=25)

    # reason = fields.CharField(required=False, blank=True, max_length=25)
    # milestone = fields.CharField(required=False, blank=True, max_length=25)
    # issue_type = fields.CharField(required=False, blank=True, max_length=25)
    # submitted_by = fields.CharField(required=False, blank=True, max_length=25)
    # submitted_date = fields.CharField(required=False, blank=True, max_length=25)
    # notify = fields.CharField(required=False, blank=True, max_length=256)
    # site = fields.CharField(required=False, blank=True, max_length=25)
    # hierarchy_id = fields.CharField(required=False, blank=True, max_length=25)
    # rev = fields.CharField(required=False, blank=True, max_length=25)
    # subject = fields.CharField(required=False, blank=True, max_length=256)
    # parent_id = fields.CharField(required=False, blank=True, max_length=25)
    # hierarchy_path = fields.CharField(required=False, blank=True, max_length=256)
    # field_acl = fields.CharField(required=False, blank=True, max_length=256)
    # is_current = fields.CharField(required=False, blank=True, max_length=25)
    # tenant = fields.CharField(required=False, blank=True, max_length=25)
    # record_type = fields.CharField(required=False, blank=True, max_length=25)
    # row_num = fields.CharField(required=False, blank=True, max_length=25)

    class Meta:
        final = True
        ignore_unknown_fields = True

    def get_fields(self):
        """
        Helper function to get interal field objects.
        :return: MongoBaseField objects that are used by this MongoModel
        :rtype: list
        """
        return self._mongometa.get_fields()

    def get_field_names(self):
        """
        Helper function to get the names of fields.  Pymodm inheritance makes it hard to include these functions
        in an intermediate class, so they are reproduced and can't be consolidated
        :return: string names of the internal fields
        :rtype: list
        """
        return [x.mongo_name for x in self.get_fields()]


class Hsd(MongoModel):
    product = fields.CharField(required=True, max_length=50)
    step = fields.CharField(required=True, max_length=50)
    socket = fields.CharField(required=True, max_length=50)
    ww = fields.CharField(required=True, max_length=50)

    # csv summary data rows
    records = fields.EmbeddedDocumentListField(HsdData)

    class Meta:
        final = True
        ignore_unknown_fields = True
        indexes = [
            pymongo.IndexModel([('product', pymongo.ASCENDING)]),
            pymongo.IndexModel([('step', pymongo.ASCENDING)]),
            pymongo.IndexModel([('socket', pymongo.ASCENDING)]),
            pymongo.IndexModel([('ww', pymongo.ASCENDING)])
        ]

    def get_fields(self):
        """
        Helper function to get interal field objects.
        :return: MongoBaseField objects that are used by this MongoModel
        :rtype: list
        """
        return self._mongometa.get_fields()

    def get_field_names(self, remove_id=True):
        """
        Helper function to get the names of fields.  Pymodm inheritance makes it hard to include these functions
        in an intermediate class, so they are reproduced and can't be consolidated
        :param remove_id: Do not include the '_id' field
        :type remove_id: bool
        :return: string names of the internal fields
        :rtype: list
        """
        doc_fields = [x.mongo_name for x in self.get_fields()]
        if remove_id:
            doc_fields.remove('_id')
        return doc_fields

    def update_from_document(self, doc):
        """
        Look at the passed in dictionary and update field values that exist within the passed in document
        :param doc: fields and values to update
        :type doc: dict
        """
        for field in self.get_field_names():
            if field in doc:
                self._data.set_mongo_value(field, doc[field])

    def increment_field(self, field, amount):
        """
        Helper function to increment the specified field value
        :param field: Name of the field to update
        :type field: str
        :param amount: amount to uncrease the field value by
        :type amount: int
        """
        if field not in self.get_field_names():
            raise KeyError(f"Invalid field {field}, cannot increment")

        setattr(self, field, getattr(self, field) + amount)


class HsdRead:
    """
    #1 - Need ags: HSDES API BasicAuth Access
         Justification: Needed for faceless account hsdes access for Codified Test Plans.
    #2 - Renew: https://hsdes.intel.com/appstore/token/       # up to 15 mins to take effect
    #3 (one time) - Goto "Token" section in https://hsdes-api.intel.com/rest/doc/
         -> First, click on POST/token/basicauth and then on GET/token/basicauth,
            and you should get your token and expiration date (tokens expire after 90 days).
         -> To renew the token, go to the HSD API and click on POST/token/basicauth/renew.
    """
    URLTEMPLATE = 'https://hsdes-pre.intel.com/rest/auth/query/_QUERYID_?max_results=1000'

    def __init__(self, speedid):
        if speedid == '123':        # unittest only
            speedid = '10047156'    # existing real one

        jfile = f'{CtpRepo.REPO_PATH}/ProductConfig/{speedid}.json'
        assert os.path.exists(jfile), f'{jfile} does not exist. This is required'
        with open(jfile) as fh:
            data = json.load(fh)
        self.queryid = data[0]['hsd_query'].replace('=', '/').split('/')[-1]
        self.url = self.URLTEMPLATE.replace('_QUERYID_', self.queryid)
        self.speedid = speedid

    def read_hsd(self):
        """
        Read hsd
        :return: The hsd data json data as-is
        """
        if not self.queryid:
            return {}

        # TO USE: bytes.fromhex(tok).decode()
        # TO ENCODE: tok.encode().hex()
        with open('/intel/tpvalidation/engtools/tptools/mtl/configs/hsd.tok.txt') as fh:
            TOK = fh.read().strip()

        tok = bytes.fromhex(TOK).decode()
        encoded_tok = base64.b64encode(tok.encode()).decode()
        headers = {'Content-Type': 'application/json', 'Authorization': 'Basic %s' % encoded_tok}
        proxy = {'http': '', 'https': ''}
        r = requests.get(self.url, headers=headers, proxies=proxy, verify=False)
        return r.json()

    def upload(self):
        """
        Call this in cron once a day.
        Upload does not DELETE. So if we upload multiple times, there will be multiple records
        :return:
        """
        urllib3.disable_warnings()
        connect()
        self.upload_hsd(self.read_hsd(), self.speedid)

    @classmethod
    def upload_hsd(cls, data, speedid):
        """
        :param data: data structure from json
        :return:  None
        """
        if not data:
            return

        result = defaultdict(list)
        ww = WW.get_ww()

        # get all product, stepping, socket
        for dd in data.get('data', []):
            result[(dd['product'], dd['stepping'], dd['socket'])].append(dd)
        for k, v in result.items():
            product, stepping, socket = k
            data = {'product': speedid,
                    'step': stepping,
                    'socket': socket,
                    'ww': ww,
                    'records': v
                    }

            # write it out
            obj = Hsd.from_document(data)
            obj.save()
            print(f"Wrote [{speedid}] [{stepping}] [{socket}] [{ww}]")


class CTPCache:
    """Cache for CTP Mongo model"""
    _data = None

    @classmethod
    def fetch(cls):
        connect()
        cls._data = list(CTP.objects.all())

    @classmethod
    def data(cls):
        if cls._data is None:
            cls.fetch()
        return cls._data


class HSDCache:
    """Cache for Hsd Mongo model"""
    _data = None

    @classmethod
    def to_dict(cls):
        """
        Convert pymodm data to dict so it's serializable to a pickle.
        However, cannot use json since json converts to dict. Methods need to call as a dictdot.

        from mod.db_ctp import connect, HSDCache
        HSDCache.fetch()
        with open('/intel/tpvalidation/engtools/tptools/mtl/plan_waivers/jsonall/hsd.json', 'w') as fh:
            json.dump(HSDCache.to_dict(), fh, indent=3)
        """
        from gadget.dictmore import DictDot

        alldata = []
        for item in cls._data:
            data = DictDot()
            data.records = []
            for field in item:
                if field == '_id':
                    continue
                if field == 'records':
                    drec = DictDot()
                    for rec in item.records:
                        for fr in rec:
                            if fr == 'id':
                                continue
                            drec[fr] = getattr(rec, fr)
                    data['records'].append(drec)
                else:
                    data[field] = getattr(item, field)

            alldata.append(data)

        return alldata

    @classmethod
    def fetch(cls):
        connect()
        cls._data = list(Hsd.objects.all())

    @classmethod
    def data(cls):
        if cls._data is None:
            cls.fetch()
        return cls._data
