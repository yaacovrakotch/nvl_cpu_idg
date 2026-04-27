#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
import setenv      # must be first in the imports
# from mod.db_ctp import *
from tp.testprogram import TestProgram, pprint, Env
import sys
import re
from gadget.files import File, basename_n
from gadget.disk import Allfiles, Chdir
from gadget.shell import SystemCall
from os.path import basename, dirname, exists
from gadget.disk import Chdir
import json
from datetime import datetime
from gadget.gizmo import Elapsed
import os
from collections import defaultdict
import glob


# PR stats per ww: gh pr list --json number,mergedAt -s closed --limit 10000 > res.json
# demo.py res.json ptlsort
from gadget.strmore import wwno
with open(sys.argv[1]) as fh:
    data = json.load(fh)
def secs(ds):
    return int(datetime.strptime(ds, '%Y-%m-%dT%H:%M:%SZ').timestamp())
for item in data:
    if not item['mergedAt']:
        continue
    ss = secs(item['mergedAt'])
    print('%s,%s,%s' % (sys.argv[2], item['number'], wwno(ss, year=True)))
exit(0)

with open(sys.argv[1]) as fh:
    data = json.load(fh)
pprint(data)
exit(0)

# =========================
# Alan's request: edc/kill given testprogram - put this in tp_audit later
# =========================
rkil = defaultdict(int)
redc = defaultdict(int)
tpobj = TestProgram(sys.argv[1]).pickle_init()
for mod, tname, dd in tpobj.mtpl.iter_flows('MAIN', edict=True, bypass=True):
    if 'patlist' not in dd:
        continue
    pats = tpobj.plists.get_pats_from_plb(dd['patlist'])

    # print(mod, tname, len(pats), dd['_EDCKIL'])
    if dd['_EDCKIL'] == 'KIL':
        rkil[mod] += len(pats)
    else:
        redc[mod] += len(pats)

print('%-20s %-5s %-5s %-5s' % ('Module', 'KILL', 'EDC', 'Total'))
for mod in sorted(rkil.keys() | redc.keys()):
    print('%-20s %5d %5d %5d' % (mod, rkil[mod], redc[mod], rkil[mod] + redc[mod]))
exit(0)

for ff in sys.argv[1:]:
    text = File(ff).read()
    if re.search("Failed to 'Fixing Test Program'", text):
        if re.search("Error: Object reference not set to an instance of an object", text):
            print(ff)


exit(0)

# =========================
# Given res.json that has "body" info, get all the first line of the Why is this PR needed.
# =========================
def get_why(txt):
    start = False
    result = []
    for line in txt.split('\n'):
        if 'Why is this' in line:
            line = line.replace('### Why is this PR needed?', '')
            line = line.replace('Why is this PR needed?', '')
            start = True

        if start and 'Who/Where' in line:
            start = False

        if start and line.strip():
            return line.strip()

    # final = (' '.join(result)).strip()
    # if not final:
    #     print(txt)

    return ""

from gadget.tputil import JsonRead
data = JsonRead(sys.argv[1]).load()
for item in data:
    why = get_why(item["body"])
    if why:
        print(f'"{why}"')
exit(0)

# =========================
# List out all atomic changes
# gh pr list -B main --json mergedAt,number,title,createdAt,body -L 1000 -s merged > res.json
# =========================
from gadget.tputil import JsonRead
data = JsonRead(sys.argv[1]).load()       # input is the output of gh pr list above
cnt = 0
for _, item in enumerate(sorted(data, key=lambda x: x['createdAt'], reverse=True)):
    if item['createdAt'].startswith('2025-07-04'):
        break

    # type1
    body = item['body']
    res = re.findall(' BRANCH:', body, re.MULTILINE)
    if ' BRANCH:' in body:
        cnt += 1
        print(cnt, item['createdAt'][:10], 'cnt=', len(res), "pr=", item['number'], item['title'])
exit(0)

# =========================
# code to study common PR
# =========================
from gadget.tputil import JsonRead

robj = re.compile(r"Class_NVL_(\w+)")
def get_bom(files):
    bom = set()
    for ff in files:
        fname = ff['path']
        res = robj.search(fname)
        if res:
            bom.add(res.group(1))
    if not bom:
        return "NA"
    if len(bom) == 3:
        return "ALL"
    return '+'.join(bom)

def get_type(files):
    tt = set()
    for ff in files:
        fname = ff['path']
        if fname.startswith('Modules'):
            tt.add(f'MOD/{fname.split("/")[2]}')
        elif 'yml' in fname or 'load_and_run.py' in fname:
            tt.add('pipelines')
        elif 'Flows' in basename(fname):
            tt.add('Flows')
        elif fname.endswith('.dll'):
            continue
        elif basename(fname).startswith('qgate_') or basename(fname) == 'pytpd':
            tt.add('qgate')
        elif 'BinMatrix' in basename(fname):
            tt.add('BinMatrix')
        else:
            tt.add(basename(fname))

    for result in tt:
        yield result

# gh pr list -B main --json mergedAt,number,title,createdAt,files -L 1000 -s merged > res.json
data = JsonRead(sys.argv[1]).load()
for cnt, item in enumerate(sorted(data, key=lambda x: x['createdAt'], reverse=True)):
    if item['createdAt'].startswith('2025-07-04'):
        break

    # type1
    bom = get_bom(item['files'])
    print(cnt + 1, item['createdAt'], bom, item['number'], item['title'])
    # print(item['createdAt'][:10], sys.argv[1].split('.')[-1])

    # type2
    # for ff in get_type(item['files']):
    #   print(ff, item['number'], item['title'])

exit(0)

# =====================================
# Print the author of all modules
# Do "git pull" on all the repos first, then run
# demo.py nvl.???/Modules/*/*/*.mtpl _work/nvl.common/nvl.common/Modules/*/*/*.mtpl > res
# =====================================
result = {}
for mtpl in sys.argv[1:]:
    folder = dirname(mtpl)
    with Chdir(folder):
        out = SystemCall(f'git log .').run_outonly()
        for line in out.split('\n'):
            if line.startswith('Author:'):
                result[folder] = line
                break

for item in sorted(result):
    print(item, result[item])
exit(0)

tpobj = TestProgram(sys.argv[1]).pickle_init()
res = tpobj.plists.get_pats_from_plb('array_epbist_DV_hptp_atom_sort_list', patonly=True)
pprint(res)
exit(0)

print("Total: %6d patterns" % len(tp.plists.get_pats_all()))
print("Total: %6d testinstances" % len(list(tp.mtpl.iter_tests())))
exit(0)

# read xml
from gadget.dictmore import xmlfunc
from gadget.printmore import Dumper
data = xmlfunc.xml2dict(sys.argv[1])
for item in sorted(data['Quicksim']['virtualdut']['response'], key=lambda x:x['testInstance']):
    name = item['testInstance']
    out = Dumper(item, dot=True, p=False).string()
    for line in out.split('\n'):
        if line.strip():
            print(f'{name} {line}')

exit(0)
from gadget.tvpv import TvpvEnv
print('result: %r' % TvpvEnv.get_site())
exit()

# =====================================
# Count number of pymtpl
# demo.py Shared/Modules/*/*/*.mtpl Modules/*/*.mtpl Modules/*/*/*.mtpl
# =====================================
for mtpl in sys.argv[1:]:
    res = [x for x in glob.glob(f'{dirname(mtpl)}/*.py') if 'qs.py' not in x]
    if not res:
        print(mtpl)
        # print(File(mtpl).read())

exit(0)

# =====================================
# count the number of patterns per dielet  (David Ballard request)
# =====================================
result = defaultdict(set)                    # key is dielet, value is set of patterns
for plist in File(sys.argv[1]).chomp():      # sys.argv[1] is the file output of tp_audit.py -plist

    # identify which dielet based on path

    # below for ARL
    res = re.search('/(MA|MH|MI|MS|MC|Ma)', plist)

    # below for NVL
    # res = re.search('/(nvl_gcd|nvl_hub|nvl_nps|nvl_cpu|nvl|Supersedes)/', plist)

    if not res:
        print(f'Error: {plist} - unknown path')
        continue
    marker = res.group(1)
    mapping = {'MA': 'FullChip',
               'Ma': 'FullChip',
               'MH': 'GCD',
               'MI': 'IOE',
               'MS': 'SOC',
               'MC': 'CPU',
               'nvl_gcd': 'GCD',
               'nvl_hub': 'HUB',
               'nvl_nps': 'PCD',
               'nvl_cpu': 'CPU',
               'nvl': 'FullChip',
               'Supersedes': 'FullChip'}
    if marker not in mapping:
        print(f'Error: {marker} - unknown mapping')
        continue
    die = mapping[marker]

    # read the file
    alltxt = File(plist).read()
    for pat in re.findall(r"^\s*Pat\s+(\w+)", alltxt, re.MULTILINE):
        result[die].add(pat)

for dielet in sorted(result):
    print(f'{dielet}: {len(result[dielet])}')

exit(0)

# =====================================
# bm.expand() example
# =====================================
from tp.mtpl import BM
tp = TestProgram(sys.argv[1])
bm = BM(tp)
name = '"CAM_ATOM_VMIN_K_CATF1_X_VCCIA_F1_" + CustomFlowMatrixSpecs.AT_F1_FREQ_MHz + "_RF_" + FlowMatrix.bin'
marker = 'CSharpTrialTest Dummy '
for line in bm.expand(f'{marker}{name}'):
    final_name = line.replace(marker, '')
    print(final_name)
exit(0)

# =====================================
# write_json example
# =====================================
from main.manager_botos import Remote

# Get all tester ping
print('\n'.join(str(x) for x in Remote().get_tester_files()))
exit(0)

# write example
Remote().write_json('PG', {'blah': 1}, '1733762489999_X.json',
                    f'/intel/tpvalidation/engtools/tptools/mtl/infra/torch/botos/completed')
print("Thank you Tai")
exit(0)

# =====================================
# create the usrv one time for flwflags
# =====================================
tp = TestProgram(sys.argv[1], tpl=sys.argv[2])
print(tp.tpldir)
exit(0)
# create the .usrv given the flowflags
vv = set()
for line in File(sys.argv[1]).raw():
    res = re.search(r'FLWSKP\.(\w+)', line)
    if res:
        vv.add(res.group(1))

final = ['''Version 1.0;

Shared
{
   UserVars FLWSKP
   {
''']
for var in sorted(vv):
    final.append(f'      Integer {var} = 1;\n')
final.append('''   }
}
''')
File(sys.argv[1].replace(".mtpl", ".usrv")).rewrite(''.join(final), 'hack')
exit(0)

# =====================================
# Malou's TOS4 bin, one-time convert (Part1 and Part2)
# =====================================

# ================= PART3- fix, after manual edit pass load init, so everything is b01xx
# read the databin first
outfile = 'BinDefinitions.bdefs'     # This is TOS4
r9 = re.compile(r'^b1\d\d\d(\d\d)\d\d')
r4 = re.compile(r'^b\d\d\d\d')
softbins = {}
final = []
hmap = {}
for line in File(f'{outfile}.loading').raw():
    sline = line.strip()
    if sline.startswith('Bin '):
        elem = sline.split()
        hmap[elem[1]] = elem[-1]

    if sline.startswith('LeafBin'):
        elem = sline.split()
        hardbin = elem[-1].replace(';', '')
        res = r9.search(elem[1])
        if res:
            dig4 = f'b01{res.group(1)}'
            softbins[dig4] = 'b1_PASS_CMTTRAY_1'
            # print(f'From: {line.strip()}')
            final.append(line.replace(elem[-1], f'{dig4};'))
            # print(f'To:   {final[-1].strip()}')

            continue

    final.append(line)

# add the softbins
final2 = []
start = False
for line in final:
    sline = line.strip()
    if sline.startswith('BinGroup SoftBins'):
        start = True
    if start and sline == '}':
        start = False
        for dig4 in softbins:
            if dig4 not in hmap:
                dig = dig4[1:]
                newline = f'        Bin {dig4}    {int(dig)}        : "{dig4}",    {softbins[dig4]};\n'
                final2.append(newline)
                print(f'Added: {newline.strip()}')

    final2.append(line)

File(outfile).rewrite(''.join(final2), 'demo.py() rewritten')
exit(0)


# ================= PART2- fix the Databin (Malou's TOS4 bin)
# read the databin first
outfile = 'BinDefinitions.bdefs'     # This is TOS4
r9 = re.compile(r'^b\d\d(\d\d)\d\d(\d\d)')
r4 = re.compile(r'^b\d\d\d\d')
softbins = {}
final = []
hmap = {}
for line in File(f'{outfile}.complete').raw():
    sline = line.strip()
    if sline.startswith('Bin '):
        elem = sline.split()
        hmap[elem[1]] = elem[-1]

    if sline.startswith('LeafBin'):
        elem = sline.split()
        hardbin = elem[-1].replace(';', '')
        res = r9.search(elem[1])
        if res:
            dig4 = f'b{res.group(1)}{res.group(2)}'
            softbins[dig4] = hardbin
            # print(f'From: {line.strip()}')
            final.append(line.replace(elem[-1], f'{dig4};'))
            # print(f'To:   {final[-1].strip()}')

            if len(hardbin) == 5:
                if hardbin in hmap:
                    softbins[dig4] = hmap[hardbin]
                else:
                    print(f"No hmap: {hardbin}")

            continue
        else:
            if r4.search(elem[1]):
                print(f'Skip 4digit: {line.strip()}')
                continue

    final.append(line)

# add the softbins
final2 = []
start = False
for line in final:
    sline = line.strip()
    if sline.startswith('BinGroup SoftBins'):
        start = True
    if start and sline == '}':
        start = False
        for dig4 in softbins:
            if dig4 not in hmap:
                dig = dig4[1:]
                newline = f'        Bin {dig4}    {int(dig)}        : "{dig4}",    {softbins[dig4]};\n'
                final2.append(newline)
                print(f'Added: {newline.strip()}')

    final2.append(line)

File(outfile).rewrite(''.join(final2), 'demo.py() rewritten')

# write the Softbin
exit(0)

# ================= PART1- add all the LeafBins lines (Malou's TOS4 bin)
# read first the source
bdefsrc = '/intel/hdmxprogs/arl/ARLXXXXB0H66G00S436/Shared/BaseInputs/BinDefinitions.bdefs'
leafbins = {}
for line in File(bdefsrc).raw():
    sline = line.strip()
    if sline.startswith('LeafBin'):
        elem = sline.split()
        leafbins[elem[1]] = f'        {line.lstrip()}'

# write those leafbin lines
outfile = 'BinDefinitions.bdefs'     # This is TOS4
final = []
started = False
exist = {}
for line in File(f'{outfile}.orig').raw():
    sline = line.strip()
    if sline.startswith('LeafBin'):
        started = True
        elem = line.split()
        exist[elem[1]] = True
        line = f'        {line.lstrip()}'

    if started and sline == '}':
        print("Adding it")
        for key in sorted(leafbins):
            if key not in exist:
                final.append(leafbins[key])
        started = False

    final.append(line)

File(f'{outfile}.complete').rewrite(''.join(final), 'demo.py() rewritten')
exit(0)


from pymtpl.helpers import ValidationMtplConvert
root = '/nfs/site/disks/mve_mig_001/tpvalidation/hdmxprogs/arl/ARLXXXXXXX75Y6DSXXX'
env = f'{root}/POR_TP/Class_ARL_U28/EnvironmentFile.env'
mtpl = f'{root}/POR_TP/Class_ARL_U28/ProgramFlowsTestPlan/ProgramFlows.mtpl'
outpy = 'POR_TP/Class_ARL_U28/programflows.py'
ValidationMtplConvert().main(env=env, mtpl=mtpl, outpy=outpy)
exit(0)

tp = TestProgram(sys.argv[1]).init(light=True, patload=False)
for mod, tname, dd in tp.mtpl.iter_flows('MAIN', idict=True):
    print(mod, tname, dd)
    exit(0)

# TILE console pretty print
text = '{}'
data = json.loads(text)
for item, val in data.items():
    if '\n' in str(val):
        print(f'{item}:')
        print(val)
    elif val:
        print(f'%s: %r' % (item, val))
exit(0)

# get_PatternsRegEx debug
from mod.cleantp_mod import CleanTCG
tp = TestProgram(sys.argv[1]).pickle_init()
# for ff in tp.get_import_files('tcg'):
#     print(ff)
# exit(0)
cplist = CleanTCG(tp)
cplist.main()
# result = cplist.get_setpointsregex()
# print(len(result))
exit(0)

# identify all params used by tcg
tp = TestProgram(sys.argv[1]).pickle_init()
everything = set(tp.timing.iter_tc()) | set(tp.levels.iter_tc())
nameonly = [x.split(':')[-1] for x in everything]
mregex = '^(.*)(%s)' % '|'.join(sorted(nameonly))
robj = re.compile(mregex, re.MULTILINE)
for ff in tp.get_all_mtpl_from_stpl():
    for elems in robj.findall(File(ff).read()):
        print(elems[0].strip().split()[0])
exit(0)

# expect: number of patterns match with original from cleaned list
for line in File(sys.argv[1]):
    line = line.strip()
    # if re.search(r'g.*longreset_ioe_fuse_over.*_MIfun_func_usb3p2', line):
    # if re.search(r"[gdx]................_.._......._............._I..U.................8.*", line):
    if re.search(r'[gdx]................_.._......._............._S..C.................4.*', line):
        print(line)
exit(0)


# debug of mega regex
_bigpat = ['g0495533C5427906D_FJ_B0FPP25_CB2PHCAAC030M_C69UVSC030Dr0700001xx_gxx080808kxxmxxxxxx_xx0x_longreset_cpu_lr_infra_MCfun',
           'g0014509I4063142B_WD_B0RPPay_AA2PHSHBC150C_IxPUVxB0Ct0103r0700008x_nxxxxxxxxxxxxx_x0_longreset_ioe_tapunlock',
           'g0454998C9219922D_OV_B0F0500_CB2PHCAAC010M_C69WVSC030Bm040000xxx_cxx080808kxxxxxxxxx_xx0x_DTSTEMPCFG_MCfun',
           'g0454998C9219922D_OV_B0F0500_clk_cpu_lnc4_fc_airef',
           'g0454999C9219922D_OV_B0F0500_clk_cpu_lnc4_fc_axref',
           ]
to_match = ['XX[gd].*',     # full regex - ok
            'XX.*219922D',  # partial  - not OK
            'XX.*(4063142|9219922D).*',
            ".*_clk_cpu_lnc4_fc_(?!.*iref).*",
            ]
bigpat = '\n'.join(sorted(_bigpat))
mregex = '^(%s)' % '|'.join(sorted(to_match))
robj = re.compile(mregex, re.MULTILINE)

pprint({pat[0] for pat in robj.findall(bigpat)})
exit(0)

import setenv     # must be the first import
from gadget.strmore import day_code
url = f'https://tvpv.pdx.intel.com/cgi-bin/pr-report/cci_list.cgi?repo=arls68&PR_CNT=SUM&br=65&code={day_code()}'
import urllib.request
with urllib.request.urlopen(url) as response:
    data = response.read()
    print(data.decode())
exit(0)

import requests
import urllib3
urllib3.disable_warnings()
headers = {'Content-Type': 'application/json',
           'Authorization': 'Basic'}
proxy = {'http': '', 'https': ''}
url = f'https://tvpv.pdx.intel.com/cgi-bin/pr-report/cci_list.cgi?repo=arls68&PR_CNT=SUM&br=65&code={day_code()}'
response = requests.get(url, headers=headers, proxies=proxy, verify=False)
print(f'Status: {response.status_code}')
print(response.text)
exit(0)

from mod.cci_list import CCI
cci = CCI('TP/75', 10000, repo='arlu28')      # This works given one branch
head, res = cci.main(cmd_prcnt='DETAIL')
pprint(res)
exit(0)

# =====================================
# Proof on how fast BotBoss triggering system, JF<->PG, on windows, via Q:\ drive
# =====================================
# Summary for BotBoss: sleep in 15 seconds. It takes 2 seconds to get data.
# Result: first number is os.listdir() elapsed. Second number is force_refresh() elapsed()
# 0.614 Secs 5.235 Secs set()
# 0.614 Secs 1.851 Secs {'abc'}
# 0.626 Secs 2.101 Secs {'ghi', 'abc'}
# 0.614 Secs 1.868 Secs {'abc'}
# 0.614 Secs 1.844 Secs {'abc', 'def'}
# 0.614 Secs 1.843 Secs {'aaa', 'abc', 'def'}
# 0.614 Secs 2.048 Secs {'bbb', 'aaa', 'abc', 'def'}
# 0.614 Secs 1.843 Secs {'aaa', 'abc', 'def'}
# 0.614 Secs 1.843 Secs {'bbb', 'aaa', 'abc', 'def'}
# 0.596 Secs 1.999 Secs {'def', 'aaa', 'bbb', 'abc'}          # using UNC, from JF tester
# 0.597 Secs 1.790 Secs {'def', 'ccc', 'aaa', 'bbb', 'abc'}

from gadget.lockfile import force_refresh
import time
# Note: This works, as long as Q:\ drive is mapped earlier
path = r'\\gar.corp.intel.com\ec\proj\mdl\pg\intel\engtools/tptools/mtl/beta/trig1'
print('start', len(os.listdir(path)))
prev = {'init'}
for i in range(1000000):
    sw = Elapsed()
    force_refresh(path)    # from gadget.lockfile
    e1 = f'{sw}'

    sw = Elapsed()
    files = set(os.listdir(path))
    if files != prev:
        print(sw, e1, files)
        prev = files

    time.sleep(0.01)
exit(0)


from main.slim_tpload import Slim
ss = Slim(sys.argv[1])
slim_list = set()
ss.keep_pats_json(slim_list)
print('slim:', len(slim_list))
exit(0)

from main.cleantp_main import CleanTP
tp = TestProgram(sys.argv[1]).pickle_init()
pfdata = tp.mtpl.dict_flows()
mapping = {'P': 'PassFlow', 'F': 'FailFlow', 'B': 'Bypassed'}
for mod, tname in tp.mtpl.iter_flows('MAIN'):
    pf = mapping[pfdata[(mod, tname)]]
    print('%s %-18s %s' % (pf, mod, tname))
exit(0)

print(' '.join(tpobj.mtpl.get_mod2fname()))
exit(0)
obj = CleanTP(tpobj)
pprint(obj.get_dedc_prime())
exit(0)

tpobj = TestProgram(sys.argv[1])
pprint(tpobj.mtpl.get_modfolder2mod())
exit(0)
print(len(tpobj.usrv.get_usrv_map()))
print(len(tpobj.usrv.get_rule_map()))
print(sw)
exit(0)
#print(tpobj.get_bom_from_env())
#print(tpobj.read_tpconfig('TestProgramFiles.PlistPath'))
print(tpobj._get_plist_from_tpconfig('LCCSP_C0'))
exit(0)

# =====================================
# Summarize test instance name (tname) according to fields
# =====================================
vals = {x: defaultdict(int) for x in range(10)}
val2 = {x: defaultdict(set) for x in range(10)}
tp = TestProgram(sys.argv[1]).pickle_init()
for elem in tp.mtpl.iter_tests():
    tname = elem[1]
    field = tname.split('_', 9)
    for idx in range(len(field)):
        vals[idx][field[idx]] += 1
        val2[idx][field[idx]].add(elem[0])

for idx in sorted(vals):
    print('')
    print(f'====== field {idx+1}, total count={len(vals[idx])}:')
    for x in sorted(vals[idx], key=lambda x: vals[idx][x]):
        mm = ', '.join(val2[idx][x])
        print(f'field={idx+1}: {x:40} Cnt: {vals[idx][x]:4}, Mods: {mm}')
exit(0)

# =====================================
# Create a pattern folder replica, with all files as softlink so David can write to the folder
# David and Sundar's request (offline pattern resolver)
# =====================================
def proc(path):
    """Process one pattern path"""
    if not path.startswith('/intel/hdmxpats'):
        return  # do nothing
    apath = path.replace('/intel/hdmxpats/', '')
    name = path.replace('/intel/hdmxpats/', '').replace('/', '_')
    targ = f'{dest}/{name}'
    if exists(targ):
        return     # already existing
    mkdirs(targ, '02775')
    for ff in os.listdir(path):
        # it has to be relative path so windows work
        os.symlink(f'../../../../../{apath}/{ff}', f'{targ}/{ff}')

from gadget.disk import mkdirs
dest = '/intel/hdmxpats/mtl/dev/jqdelosr/23Y'   # destination path
assert exists(dest)
tp = TestProgram(sys.argv[1])
tp.env.set_env()
everything = sorted(tp.env.get_plist_paths('HDST_PAT_PATH'))
for idx in range(len(everything)):
    print(f'Processing {idx} of {len(everything)} - {everything[idx]}')
    proc(everything[idx])
exit(0)

# =====================================
# CTP to LLM purpose column for scan
# =====================================
for line in File(sys.argv[1]).chomp():
    elems = line.split(',')
    ti = elems[0]

    elem = ti.split('_', 9)
    if elem[0] == 'ATPG':
        typ = 'stuckat'
    elif elem[0] == 'SOT':
        typ = 'Start of Test'
    elif elem[0] == 'TATPG':
        typ = 'transition'
    else:
        typ = elem[0]
    if len(elem) > 7:
        purpose = f'Scan uncore {typ} {elem[-1].replace("$", "")} for {elem[1]} partition for {elem[2]} on {elem[4]} subflow for {elem[6]} on {elem[7]} frequency'
    else:
        purpose = 'na'
    print(f'{line},{purpose}')
exit(0)

# =====================================
# Scandir test given testprogram HDST_PAT_PATH and PLIST_PATH
# =====================================
tpobj = TestProgram(sys.argv[1])
final = tpobj.env.get_plist_paths()
final.extend(x for x in tpobj.env.get_plist_paths('HDST_PAT_PATH') if 'cachepatterns' not in x and 'OutputPobj_' not in x)
tot = []
sw = Elapsed()
for path in final:
    tot.extend(os.scandir(path))
print(f'dirs={len(final)}, total_files={len(tot)}, {sw}')
exit(0)

# =====================================
# open gh pr json and display pr number
# gh pr list -s merged -B TP/23 -L 1000 --json number,labels > 23.json
# =====================================
with open(sys.argv[1]) as fh:
    data = json.load(fh)
for item in data:
    labels = []
    for ll in item['labels']:
        name = ll['name']
        if 'FAILED' in name or 'PASSED' in name or 'I_AM_TPI_Skip_Bot' in name:
            continue
        labels.append(name)
    print('%s,%s' % (item['number'], ','.join(labels)))
exit(0)

# ===================================================
# convert and give time difference given two hh:mm:ss
# ===================================================
def conv(tm):    # convert hh:mm:ss to seconds
    elem = tm.split(':')
    return int(elem[0])*3600 + int(elem[1])*60 + int(elem[2])

start = sys.argv[1]
end = sys.argv[2]
diff = conv(end) - conv(start)
hr = int(diff/3600)
print('%s hr %s min %s sec' % ( hr, int((diff - hr*3600)/60), diff % 60))
exit(0)

# ===========================
# Jonathan timing request: Sweep a variable in timings
# ===========================

envfile = '/intel/tpvalidation/hdmxprogs/mtl/MTLXXXXXXX39E0RSXXX/POR_TP/Class_MTL_P28/EnvironmentFile.env'
tpobj = TestProgram(envfile)
tpobj.timing.set_data()      # initialize it

timtc = 'IP_CPU_BASE::cpu_tdo2stf_perpin_timing_tdo2stf_tclk100_sclk400_cclk400'
timing_name = tpobj.timing._tc[timtc]['Timing']

# Get the param_name of this specific pin
domain = 'CPU_TAP_ALL'
pin_or_pingroup = 'cpu_tap_in'
param_name = tpobj.timing._timing[timing_name][domain][pin_or_pingroup]['drive']
print(f"Paramname = {param_name}, for {pin_or_pingroup} on {domain}")

# Get the value of this param_name
var_to_change = 'p_mtd_per'
val = tpobj.timing.get_tc_value(timtc, param_name)
mtd_per = tpobj.timing.get_tc_value(timtc, var_to_change)
print(f'{param_name} Value = {val} at {var_to_change}={mtd_per}')

# Let's say we change p_mtd_per to a different value
for item in tpobj.timing.set_param(timtc, var_to_change, '11nS'):
    print(f'-i- set_param(): {item}')
tpobj.timing.evaluate()      # Need to evaluate when variable is changed

val = tpobj.timing.get_tc_value(timtc, param_name)
mtd_per = tpobj.timing.get_tc_value(timtc, var_to_change)
print(f'{param_name} Value = {val} at {var_to_change}={mtd_per}')

exit(0)

# ===========================
# display all unique counters
# ===========================
from gadget.tputil import OtplFile
tpobj = TestProgram(sys.argv[1]).pickle_init()
ctrs = []
for ff in tpobj.get_all_mtpl_from_stpl():
    block = OtplFile(ff).get_block('Counters', parsed=True)
    ctrs.extend(x for x in block if x not in ('Counters', '}', '{'))
print('\n'.join(sorted(ctrs)))
exit(0)

# =========================
# prove the bug from Tai
# ============================
from mod.update_mtpl import FlowUpdater
tpobj = TestProgram(sys.argv[1]).pickle_init()

file_path = 'Modules/TPI_BASE_XXX/TPI_BASE_XXX.mtpl'
obj = FlowUpdater(tpobj, file_path, 'TPI_BASE_XXX')
insert_dict = {-2: {'PassFail': 'Fail', 'SetBin':'SoftBins.b90999901_fail_FAIL_DPS_ALARM', 'Return':'-2'},
               -1: {'PassFail': 'Fail', 'SetBin':'SoftBins.b90989801_fail_FAIL_SYSTEM_SOFTWARE', 'Return':'-1'},
               0: {'PassFail': 'Fail', 'Return':'1'},
               1: {'PassFail': 'Pass', 'PREVIOUS': True}}
obj.insert('TPI_BASE_XXX_LOTSTARTFLOW',
           'CTRL_X_ITUFF_K_LOTSTARTFLOW_X_X_X_X_STARTLOT', 1,
           'CTRL_X_BINRULES_K_LOTSTARTFLOW_X_X_X_X_FMI_BINRULES',
           'CTRL_X_BINRULES_K_LOTSTARTFLOW_X_X_X_X_FMI_BINRULES',
           insert_dict)
obj.write()
exit(0)

# cd /infrastructure/p6vector/temp
# ====== module:
# demo.py prod_ARLXXXXXXX60B0FSXXX/POR_TP/Class_ARL_H68/EnvironmentFile.env prod_ARLXXXXXXX60B0FSXXX/Modules/FUN_CORE_C68/FUN_CORE_C68_CLASS_P68G2_CLASS_H68G2_g.mtpl FUN_CORE_C68_CLASS_P68G2_CLASS_H68G2_g.mtpl
# ====== programflows:
# demo.py prod_ARLXXXXXXX60B0FSXXX/POR_TP/Class_ARL_H68/EnvironmentFile.env prod_ARLXXXXXXX60B0FSXXX/POR_TP/Class_ARL_H68/ProgramFlowsTestPlan/ProgramFlows_CLASS_H68G2.mtpl ProgramFlows_CLASS_H68G2.mtpl

from gadget.tputil import remove_ip
plb = 'scn_cmt_x_vccia_f1_catf1_sNs100_edt_cmt_trans_m0_classhvm_list'
flatreset = re.compile(r'^resetplb_')
tp = TestProgram(sys.argv[1], allpats=True).pickle_init()
res = tp.plists.get_flat(remove_ip(plb), stopat=flatreset)
# print(f'====================== {tp.plists._plb2n["scn_cmt_x_vccia_f1_catf1_sNs100_edt_cmt_trans_m0_classhvm_list"]}')
#pprint(tp.plists._plbattr)
pprint(res)
exit(0)
obj = FlowUpdater(tp, sys.argv[2], None)  #'FUN_CORE_C68')
obj.mtplfile = sys.argv[3]
obj.write()
exit(0)

# ================================
# Display all shared submodule repos
# ================================
for line in File(sys.argv[1]):
    bs = r'\\'      # backslash regex
    if re.search(fr'Modules{bs}\w+{bs}\w+{bs}\w+\.mtpl', line):
        print(line.strip())
exit(0)

# ================================
# Code to tell if the TP is released on time or not
# cd /intel/tpvalidation/hdmxprogs/mtl
# demo.py ??????????23????XXX/POR*/*/EnvironmentFile.env
# ================================
from gadget.strmore import curtime
for ff in sys.argv[1:]:
    tprev = ff[10:15]
    tim = curtime(os.path.getmtime(ff)).replace('_', ' ')
    flag = '<<<<<' if int(tim[11:13])>=17 else ''    # 5pm and beyond
    print(f'{tprev} {tim} {flag}')
exit(0)

# ===============================
# ituff get all ShmooResults
# cd /prod/hdmxdata/prod
# ===============================
def one_ituff(ff, pct):
    name = None
    lot = basename(dirname(ff))
    tpname = "No_prgnm"
    vid = ""
    for line in File(ff).chomp():
        if line.startswith('6_prgnm_'):
            tpname = line.replace('6_prgnm_', '')
            continue
        if line.startswith('2_visualid_'):
            vid = line.replace('2_visualid_', '')
            continue
        if line.endswith('_ShmooResults'):
            name = line
            continue
        if name:
            if line.startswith('2_strgval'):
                print('%d,%s,%s,%s,%s,%s' % (int(pct), lot, tpname, vid, name.split(':')[-1], line.replace('2_strgval_', '')))
            else:
                print('%d,%s,%s,%s,%s,%s' % (int(pct), lot, tpname, vid, name.split(':')[-1], 'None'))
            name = None

all = glob.glob('*/*.gz')
for ctr, ff in enumerate(sorted(all)):
    one_ituff(ff, ctr*100/len(all))
exit(0)

# ===============================
from mod.pobj_cache import PobjCopy
tpobj = TestProgram('I:/tpvalidation/hdmxprogs/mtl/MTLXXXXXXX23Z7CSXXX/POR_TP/Class_MTL_P68/EnvironmentFile.env')
obj = PobjCopy(tpobj)
obj.main()
exit(0)
# /c/Users/SysC/AppData/Local/Temp/TPFIXPATH
# using tprobot tester: tpfixpath is empty (most probably it's using the D:\ or L:\)?
# mrobot P28 experiment: There is no D:\ drive in this tester.
# EXPT1: use P28 mrobot: Empty TPFIXPATH and L:\ is not in env.
#    what will become of TPFIXPATH? answer regenerated. Files in TPFIXPATH: 57,382
#    Mbot run is 1hr 54 mins (slow)
#    How much is uniq in TPFIXPATH vs L:? 2494
#    learning: TPFIXPATH is auto populated (loadtime is slow)
# EXPT2: 58K files in TPFIXPATH. How much of pats in copy_TPFIXPATH is in L:\ or D:\.
#    Total L: 99425, unique in TPFIXPATH: 2483

uniq = set()
for subdir in os.listdir('.'):
    ff = set(os.listdir(subdir))
    print('%s %5d %5d Duplicates %s' % (subdir, len(ff), len(uniq), uniq & ff))
    uniq.update(ff)

# compare with D:\OutputPobj_TP38  (not exist in mbot tester)
# print()
# d_drive = '/d/OutputPobj_TP38'
# d_files = set(os.listdir(d_drive))
# print('Total D: %s, unique in TPFIXPATH: %s' % (len(d_files), len(uniq - d_files)))

print()
l_drive = f'L:/cachepatterns/OutputPobj_TP38'
print('exist', os.path.exists(l_drive))
print('isdir', os.path.isdir(l_drive))
l_files = set(os.listdir(l_drive))
print('Total L: %s, unique in TPFIXPATH: %s' % (len(l_files), len(uniq - l_files)))

exit(0)

# ===============================
# get all users of git repos via git blame
# cd to_inventory_clone
# res contains list of files to do git blame: find . | grep repos.yml > res
# ===============================
robj = re.compile(r'\((.+?)20\d.*\) name: (.*)')       # get the username and the repo path
for ff in File('res').chomp():
    _, out = SystemCall(f'git blame {ff}').run_outtxt()
    for line in out.split('\n'):
        res = robj.search(line)
        if res:
            print('%-40s %s' % (res.group(1), res.group(2)))
exit(0)

# ===============================
# count qgate catches: As of 9/19: 642 saves, out of 19514 total TP builds.
# ===============================
import glob
sw = Elapsed()
afiles = glob.glob('2023-*/*')       # cd /nfs/site/home/jqdelosr/pytpd_rel/logs/checkers
tpr = re.compile(r'(CMD: .* tprobot_.*)', re.MULTILINE)
count = 0
sherlock = 0
qgates = 0
for idx, item in enumerate(afiles):
    print(f'processing {idx}/{len(afiles)}, count:{count}, sherlock:{sherlock}, qgates:{qgates}')
    if '.onetoc2' in item:
        continue
    if 'sherlock_' in item:
        continue

    text = File(item).read()
    res = tpr.search(text)
    if res:
        continue    # tpbot

    # marker here
    if 'START: sherlock Checkers' in text or 'START: QGate' in text:
        count += 1
        flag = True
    else:
        flag = False

    if 'Sherlock has errors' in text:
        sherlock += 1
        if not flag:
            raise Exception(f'Pls check, marker is incorrect: {item}')
    if 'There are Quality Errors' in text:
        qgates += 1

print(f'count:{count}, sherlock:{sherlock}, qgates:{qgates}')
exit(0)
# ===============================
# code to show invalid chars
# ===============================
with open(sys.argv[1], 'rb') as fh:
    for lno, line in enumerate(fh):
        print(lno, line)
exit(0)
tpobj = TestProgram(sys.argv[1]).pickle_init()
dd = tpobj.mtpl.get_instance_to_subflows()  # {(module, instance): set(subflows)}
target = 'HVBIGT_SubFlow'
for module_instance, subflows in dd.items():
    if target in subflows:
        print(module_instance)

exit(0)
# get all modules with ForwardingMode != InputOutput
kwargs = dict(bypass=True, keyparam='ForwardingMode', edict=True)
result = defaultdict(int)
for mod, tname, edict in tp.mtpl.iter_flows('MAIN', **kwargs):
    fmode = edict['ForwardingMode']
    if fmode != 'InputOutput':
        result[(fmode, mod)] += 1
pprint(result)
exit(0)


# =====================================
# Sajeeth ask: do you have a script that you can run on a TP to list out all the modules
# that are using TOS rules to bypass their content at any socket?
# Usage: cd <TP>/Modules
#        demo.py 23T */*.mtpl >> ~/tpval/tosrules.csv
# =====================================

from gadget.tputil import OtplFile
def proc(ff):
    mod = ff.split('/')[0]
    robj = re.compile(r'(BypassPort|bypass_global)\s*=\s*(.*);')
    for lno, line in OtplFile(ff).readline():
        if line.startswith('Test '):
            ti = line.split()[2]
        res = robj.search(line)
        if res:
            value = res.group(2)
            if value not in ('1', '-1', '"1"', '"-1"'):
                print(f'{sys.argv[1]},{mod},{ti},{value}')
                # print(value)

for ff in sys.argv[2:]:
    proc(ff)
exit(0)

# =====================================
# bug on timing inheritance
# =====================================
# tp.timing.set_data()
result = tp.timing.get_period_param('PSCN_SOC_SXX::soc_hvm_ddrless_timing_perpin_tclk100_xtal38p4_rtc4_bclk400_tam200_ssnin200_ssnout200_SHARED_8D2D91729D5E664F5DA906943D02CAC02597AC6CA41DDCCECD189907811AA0E1')
print(result)
exit(0)

# Get vecmem per pattern
pats = {'g1979199W5162753A_LG_VC28xCB023_Vm020t00xxx06_dxxx0808082axxxxxxxxx_cC28B0PxxATC011J0k0_x02_cmt_bus4core_edt_sa_sns_maw3clk': 'A',
        'g1980191W5183317A_8V_VC28xCB023_Vm020t00xxx06_dxxx0808082axxxxxxxxx_cC28B0PxxATC011J0k0_x00_stfinit_bus_edt_sa_sns_xnawrc2clk': 'A',
        'g3613197W4069022A_Gw_VC68xCS017_Aa020j00xxxAA_dxxx0808084bxxxxxxxxx_cC68S0PxxATC016J1w6_x00_sbft_module_precat_seq_bubble1': 'B'}

from gadget.tputil import remove_ip
class Get_1x:

    @classmethod
    def vecmem(self, pats):
        """Display vecmem summary"""
        # pats is {name: module}
        from veplib.prod.patstatus import patinfo, patvedb
        from gadget.sepshelve import SqlDict
        db = SqlDict('/intel/tpvalidation/jqdelosr/nvl_mtl23M0D/data816.sqlite')
        datai = patinfo.fetch(pats)
        # datav = patvedb.fetch(pats)

        # get vecmem from datai
        vecmem = {}
        for pat in datai:
            if 'vecmem' not in datai[pat]:
                print(f"WARNING: {pat} does not have vecmem in patinfo")
                vecmem[pat] = 0
                continue
            for item in datai[pat]['vecmem']:
                if 'FAB_ALL' in item['domain_name']:
                    vecmem[pat] = item['memory']

        # get busclk from datav
        # vecmem1x = {}
        # for pat in datav:
        #     if 'vedb_src_convert' not in datav[pat]:
        #         print(f"WARNING: {pat} does not have vedb_src_convert in patvedb")
        #         continue
        #     for item in datav[pat]['vedb_src_convert']['domain']:
        #         if item['domain_name'] == 'CPU_FAB_ALL':
        #             vecmem1x[pat] = item['bus_cycles']

        # get 1x data then save to db
        # for idx, pat in enumerate(datai):
        #     if pat in db:
        #         continue
        #     linkn = None
        #     cnt = 0
        #     if 'files' in datai[pat]:
        #         for item in datai[pat]['files']['src']:
        #             if 'FAB_ALL' in item:
        #                 for line in File(f'{item}.gz.bz2').chomp():
        #                     if '{ S {' in line:
        #                         if linkn is None:
        #                             linkn = len(line.split('}{'))
        #                         cnt += 1
        #                 if not linkn:
        #                     db[pat] = vecmem[pat]
        #                 else:
        #                     assert linkn >= 2
        #                     db[pat] = vecmem[pat] + (cnt * (linkn - 1))
        #                 print(f'{idx}/{len(datai)}', cnt, linkn, vecmem[pat], db[pat], pat)
        # exit(0)

        # display
        summary = defaultdict(int)
        summary_v = defaultdict(int)
        total = defaultdict(int)
        cnt = defaultdict(int)
        alldb = {k: v for k, v in db.iteritems()}
        for pat in vecmem:
            summary_v[pats[pat]] += vecmem[pat]
            if pat not in alldb:
                print(f"NOTE: {pat} not in alldb")
                continue
            if not alldb[pat]:
                print(f"NOTE2: {pats[pat]} - {pat} is zero in alldb")
            summary[pats[pat]] += alldb[pat]
            total[pats[pat]] += 1
            if vecmem[pat] != alldb[pat]:
                cnt[pats[pat]] += 1
            print(f'{pats[pat]} {alldb[pat]} {vecmem[pat]}  {pat}')

        # summary
        for mod in sorted(summary):
            print('%s %.3f %.3f %s' % (mod.split()[0], summary[mod]/1024, summary_v[mod]/1024, f'{cnt[mod]}/{total[mod]}'))

    @classmethod
    def tap_scan(self, pats):
        """
        Display if there is tap channel linking in the entire pattern suite
        Result: zero pattern use tap channel link
        """
        # pats is {name: module}
        # from veplib.prod.patstatus import patinfo, patvedb
        from gadget.printmore import PctIndicator
        # datai = patinfo.fetch(pats)
        import pickle
        with open('all_datai', 'rb') as fh:
            datai = pickle.load(fh)

        # determine if pattern source has scan
        print(f'Total: {len(datai)}')
        with PctIndicator(len(datai)) as ind:
            for idx, pat in enumerate(datai):
                ind.disp(idx)

                if 'files' in datai[pat]:
                    for item in datai[pat]['files']['src']:
                        if 'TAP_ALL' in item:
                            alltext = File(f'{item}.gz.bz2').read()
                            if '{ S {' in alltext:
                                print(f'{idx}/{len(datai)}', pat)
        exit(0)

    @classmethod
    def domain_ratio(self, pats):
        """
        Display if there is tap channel linking in the entire pattern suite
        Result: zero pattern use tap channel link
        """
        # pats is {name: module}
        # from veplib.prod.patstatus import patinfo, patvedb
        from gadget.printmore import PctIndicator
        # datai = patinfo.fetch(pats)
        import pickle
        with open('all_datai', 'rb') as fh:
            datai = pickle.load(fh)

        # determine if pattern source has scan
        print(f'Total: {len(datai)}')
        with PctIndicator(len(datai)) as ind:
            for idx, pat in enumerate(datai):
                ind.disp(idx)

                if 'files' in datai[pat]:
                    for item in datai[pat]['files']['src']:
                        if 'TAP_ALL' in item:
                            alltext = File(f'{item}.gz.bz2').read()
                            if '{ S {' in alltext:
                                print(f'{idx}/{len(datai)}', pat)
        exit(0)

    @classmethod
    def duptid(cls, pats):
        """Print duplicate tid count, per module"""
        tids = set()
        total = defaultdict(int)
        dups = defaultdict(int)
        for pat, mod in pats.items():
            tid = pat[9:16]
            total[mod] += 1
            if tid in tids:
                dups[mod] += 1
            tids.add(tid)

        for mod in sorted(total):
            print(mod, dups[mod], total[mod])

        exit(0)

    @classmethod
    def all_pats(cls):
        """Get all patterns in flow, not bypassed"""
        tp = TestProgram(sys.argv[1], allpats=True).pickle_init()
        kwargs = dict(bypass=True, keyparam='patlist', edict=True)
        allpats = {}
        mod2ci = defaultdict(str)
        for mod, tname, edict in tp.mtpl.iter_flows('MAIN', **kwargs):
            if mod not in mod2ci:
                res = tp.plists.get_cipmodules([mod])
                for cimod in res:
                    mod2ci[mod] += f'{cimod} '

            plb = edict['patlist']
            for pat in tp.plists.get_pats_from_plb(remove_ip(plb)):
                # if mod2ci[mod] != 'None':
                allpats[pat] = mod2ci.get(mod, 'oops')

        print(len(allpats), 'pats')
        return allpats   # {x: v for x, v in allpats.items() if 'MC' in v}

    @classmethod
    def vecmem_totals(cls):
        """Display the total based on vecmem_rpt"""
        # Get summary of vecmem at module level
        tp = TestProgram(sys.argv[1])
        tp.plists.set_plist_list()
        all_rev = set()
        loaded_plist = {}
        for item in sorted(tp.plists.get_plist_list()):
            if 'TCC' in item:
                loaded_plist[basename(item)] = 1
            targ = f'{dirname(dirname(item))}/doc/vecmem_rpt_sort.txt'
            if not exists(targ):
                targ = f'{dirname(dirname(item))}/doc/vecmem_rpt_class_p68g2.txt'
            all_rev.add(targ)

        for item in sorted(all_rev):
            # print(exists(item), item)
            for line in File(item).chomp():
                if 'TOTAL' in line:
                    module = basename_n(item, 5).split('/')[0]
                    print(line.replace('K', '').replace('TOTAL', module))
        exit(0)

# Get_1x.vecmem_totals()
pats = Get_1x.all_pats()
Get_1x.vecmem(pats)
# Get_1x.domain_ratio(pats)
exit(0)

# code proof that we can read while windows is writing (as long as you don't delete). Run this in parallel.
import time
if sys.argv[1] == 'write':
    for ii in range(1000000):
        with open('c:/temp/a.txt', 'a') as fh:
            fh.write(f'{ii} This is a long line. The quick brown fox jumps over the lazy dog. g1979199W5162753A_LG_VC28xCB023_Vm020t00xxx06_dxxx0808082axxxxxxxxx_cC28B0PxxATC011J0k0_x02_cmt_bus4core_edt_sa_sns_maw3clk\n')
            print(ii)

if sys.argv[1] == 'read':
    for ii in range(1000000):
        with open('c:/temp/a.txt', 'r') as fh:
            for line in fh:
                lastline = line
            print(f'last line: {lastline.split()[0]}')

exit(0)

import requests
os.environ["https_proxy"] = 'http://proxy-dmz.intel.com:912'
url = 'http://compass-mfg-api-dev.apps1-fm-int.icloud.intel.com/api/mfg_readiness/plan_vs_actual'
# url = 'http://compass-mfg-api-dev.apps1-fm-int.icloud.intel.com/api/'
sw = Elapsed()
response = requests.get(url) # , headers=headers)
pprint(response.json())
print(sw)
exit(0)

# Code to get status of runners! status: offline|online; busy: True/False
import requests
os.environ["https_proxy"] = 'http://proxy-dmz.intel.com:912'
val = '746f6b656e206768705f736776493873444668384a423947383342383861455a456b573354777076344752787076'
key = '417574686f72697a6174696f6e'
owner = 'intel-restricted'
repo = 'mtlp68'
url = f'https://api.github.com/repos/{owner}/{repo}/actions/runs'      # this works!
url = f'https://api.github.com/repos/{owner}/{repo}/actions/runners'   # this works!
headers = {bytes.fromhex(key).decode(): bytes.fromhex(val).decode()}
response = requests.get(url, headers=headers)
pprint(response.json())
exit(0)

os.environ['https_proxy'] = 'http://proxy-chain.intel.com:912'
from gadget.getgit import GitHub
print(len(GitHub.get_modfiles()))
exit(0)

from gadget.shell import SystemCall
import os
os.environ['https_proxy'] = 'http://proxy-chain.intel.com:912'
SystemCall('gh pr diff').run_outtxt()
SystemCall('gh pr diff').run_sout_serr()
print('Success')
exit(0)

# pyston vs python bootup - pyston is faster:
sw = Elapsed()
for x in range(100):
    # 3.1 sec vs 2.3 sec for basic; 9.3 vs 9.3 secs for gadget.shell
    # _, out = SystemCall("/usr/intel/pkgs/python3/3.6.3a/modules/r1/bin/python3 -c 'import gadget.shell; print(2)'").run_outtxt()
    # tmp vs nfs pyston install: 6.598 Sec /tmp, 9.247 Sec /nfs (100 calls). That is, 10 calls per sec.
    _, out = SystemCall("/tmp/pyston2.3.4/bin/pyston -c 'import gadget.shell; print(2)'").run_outtxt()
    assert out == '2', out
print(sw)
exit(0)

# replace content
for ff in sys.argv[1:]:
    text = File(ff).raw(islist=False)
    old = "I:/tpvalidation/engtools/tptools/mtl/beta/latest/main"
    new = "I:/tpvalidation/jqdelosr/pytpd/main"
    text = text.replace(old, new)
    File(ff).rewrite(text, 'demo')
exit(0)

# unicode check read of all files
ignore_extensions = ('.pyc', '.xlsx', '.xlsm', '.dll', '.zip', '.git', '.cat', '.old',
                     '.bak', '.gold', '.pdb', '.exe', '.mtproj')
ctr = 0
err = []
for ff in Allfiles('.', skipsvn=True):
    if ff.endswith(ignore_extensions):
        continue
    with open(ff, 'rb') as fh:
        text = fh.read()
        if b'Module' in text:
            _ = 'Module' in text.decode(errors='ignore')
            ctr += len(text)
            print(f"{ctr}. {ff}")
print(len(err), "errors")
exit(0)

# PR age: gh pr list -B TP/23 --json mergedAt,number,createdAt -L 1000 -s merged
with open(sys.argv[1]) as fh:
    data = json.load(fh)
def secs(ds):
    return int(datetime.strptime(ds, '%Y-%m-%dT%H:%M:%SZ').timestamp())
for item in data:
    age = secs(item['mergedAt']) - secs(item['createdAt'])
    print('%s,%s' % (item['number'],age))
exit(0)

tp = TestProgram(sys.argv[1])
robj = re.compile(r'(Modules/.*)/\w+\.')
for ff in tp.get_all_mtpl_from_stpl():
    res = robj.search(ff)
    if not res:
        continue
    mod = res.group(1)
    modx = mod.replace('/', '.')
    for f1 in Allfiles(mod):
        if f1.endswith(('.mtpl', '.pyc', '.xlsx', '.xlsm', '.dll', '.zip', '.git', '.cat')):
            continue
        try:
            all = File(f1).read()
            for line in re.findall(modx, File(f1).read()):
                print(f1, line)
        except:
            print(f"FAIL: {f1}")
exit(0)

# identify mismatched testplan plan vs module folder name
tp = TestProgram(sys.argv[1])
for ff in tp.get_all_mtpl_from_stpl():
    plan = tp.get_scope(ff, 'Base')
    mod = basename(dirname(ff))
    if mod != plan:
        print(mod, plan)
exit(0)

# call rest api
import requests
headers = {'Content-Type': 'application/json'}
proxy = {'http': 'http://proxy-chain.intel.com:911', 'https': 'http://proxy-chain.intel.com:912'}
url = 'https://api.github.com/repos/intel-restricted/ctp-mtl/contents/ProductConfig/10047184.json'
r = requests.get(url, headers=headers, proxies=proxy, verify=False)
print(r.json())
exit(0)

# update mongo db ctp
connect()
data = list(Hsd.objects.all())
for item in data:
    if item.product != '10047184':
        continue
    item.product = '10047156'
    item.save()
    print(f'Done: {item.product}')
exit(0)

from mod.mtplencode import MtplEncode
tp1 = TestProgram(sys.argv[1])
mtp1 = MtplEncode(tp1)
mtp1.generate_meta()

tp2 = TestProgram(sys.argv[2])
mtp2 = MtplEncode(tp2)
mtp2.metapath = mtp1.metapath
mtp2.read_meta()
mtp2.do_fsm()
exit(0)

# Validate generate and read meta: arg1=repo arg2=i_drive
from mod.mtplencode import MtplEncode
tp1 = TestProgram(sys.argv[1])
mtp1 = MtplEncode(tp1)
mtp1.generate_meta()

tp2 = TestProgram(sys.argv[2])
mtp2 = MtplEncode(tp2)
mtp2.metapath = mtp1.metapath
mtp2.read_meta()
exit(0)

# Given a sha determine the branch
from gadget.getgit import GetGit
obj = GetGit()
obj.init()
for item in obj.flatten('492e72c20031f3349b6b65bda11d4307c9bbeb24'):
    print(item)
exit(0)

from mod.db_ctp import call_json_api
pprint(call_json_api('https://tvpv.pdx.intel.com/cgi-bin/ctp2/ctp_hsd.cgi?ww=2023.ww11.6'))
exit(0)
# generate the summary code
import json
# /nfs/site/home/jqdelosr/tpval/forjames/ctp/Backups_JSONs/2023.WW04.5.json
with open(sys.argv[1]) as fh:
    data1 = json.load(fh)

pprint(summary_hsd(data1['data']))

exit(0)
# TODO: timeout in SystemCall =====================================
import subprocess

# Start the subprocess
proc = subprocess.Popen(["long_running_script.sh"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

try:
    # Wait for the process to complete
    stdout, stderr = proc.communicate(timeout=60)
    print("Process completed successfully!")
except subprocess.TimeoutExpired:
    # If the process takes longer than the specified timeout, terminate the process
    proc.terminate()
    print("Process terminated gracefully!")


# TODO: update pytpd code to use (works for both unix and windows) =====================
import threading

class TimeoutException(Exception):
    pass

def code_execution():
    # Code to be executed within the specified time
    pass

class CodeTimeout:
    def __init__(self, seconds):
        self.seconds = seconds

    def __enter__(self):
        self.timer = threading.Timer(self.seconds, self.timeout_handler)
        self.timer.start()

    def __exit__(self, exc_type, exc_value, traceback):
        self.timer.cancel()

    def timeout_handler(self):
        raise TimeoutException("Code execution timed out")

# Example usage
with CodeTimeout(5):
    code_execution()
exit(0)

# mtt expand of evmins - Chen's ask
# To run: Create a .mtpl.torchexpand which is Torch expand from MTT native
#         cp TPI_EVMINS_YXXK_CLASS_P68G2.mtpl.torchexpand TPI_EVMINS_YXXK_CLASS_P68G2.mtpl ; ~/pytpd/main/demo.py TPI_EVMINS_YXXK_CLASS_P68G2.mtpl
#         Then confirm output of: grep FlowControl_ TPI_EVMINS_YXXK_CLASS_P68G2.mtpl
#                                 grep SetFlowInfo_ TPI_EVMINS_YXXK_CLASS_P68G2.mtpl
#         vs expect
from main.torch_postproc import MTTExpand
tpobj = TestProgram('/nfs/site/home/jqdelosr/mtl/tpval/MTLXXXXXXX21D0ZSXXX/POR_TP/Class_MTL_P68/EnvironmentFile.env')
me = MTTExpand(tpobj)
me._main_one_mtpl(sys.argv[1])
exit(0)


# ==============================
# json rest query - see mod.db_ctp import call_json_api
# =======================

# check current tp in cwd for plistedit
from main.torch_postproc import PlistEdit, Env
tpobj = TestProgram(Env.get_envfile())
PlistEdit(tpobj).main()
exit(0)

# gh pr diff check
SystemCall('gh pr diff', disp=True).run_outtxt()
with Chdir('Modules/TPI'):
    SystemCall('git diff --name-only 50fe028', disp=True).run_outtxt()
exit(0)

# TPBuild standalone checkouts
from main.buildtp import TPBuild
TPBuild.ube_folder = '/intel/engineering/dev/team_classtp/torch/bot_ube'
bt = TPBuild('P68_ARR', './blah', robot='mrobot_P68B0_Dig1', batfile='', repljson='mv_evmins')
print(bt.get_soc_file(sys.argv[1]))
exit(0)

from mod.moduleskip import ModuleSkip
tpobj = TestProgram(sys.argv[1])
ModuleSkip(tpobj, skipfile=True).main()
exit(0)

# read datahost in PG
from gadget.data_host import DataHost
urp = ('https://tvpv.png.intel.com/cgi-bin/pytpdhost.cgi',
       '/intel/tpvalidation/engtools/tptools/mtl/beta/latest',
       'tgl.py')
print(DataHost().central("getinfo", 1, check=False, urp=urp))    # set urp=None for JF
sw = Elapsed()
print(DataHost().central("getinfo", 2, check=False, urp=urp))
print(sw)     # 1.2 to 1.3 sec
exit(0)

from gadget.dictmore import find_dot_items
import json
import os
cc = os.path.realpath('/i/tpapps/TORCH/Prod/CLI/Torch.exe')
print(SystemCall(f'I:/tpapps/TORCH/Prod/CLI/Torch.exe -h').run_outtxt())
exit(0)

from main.slim_tpload import Slim
sl = Slim('/intel/hdmxprogs/mtl/MTLXXXXAXH19R00S222/POR_TP/Class_MTL_P68/EnvironmentFile.env')
slim_names = set()
sl.keep_pats_json(slim_names)
print(len(slim_names))
exit(0)

from gadget.getgit import GetGit
gg = GetGit().init()
print(gg.get_root(sys.argv[1]))
exit(0)

def all_pr(tip_tp):
    """
    Given main branch (must be tip), display all PR commits of this line
    :param tpbranch: tpbranch name
    :return:
    """
    # get all Integs
    ias = gg.integ_sha()   # {sha_root_integ: name}

    # display
    startsha = gg.branch[f'remotes/origin/{tip_tp}']
    integ = 'No_Integ'
    for sha in list(gg.flatten(startsha)):
        if sha in ias:
            integ = ' '.join(ias[sha])
        else:
            integ = ''
        if gg.detail[sha]['pr']:
            print('%s %s PR%s %s' % (sha[:9], integ, gg.detail[sha]['pr'], gg.detail[sha]['desc']))

    exit(0)
    # for br in sorted(gg.branch, reverse=False):
    #     if br.startswith('remotes/origin/Integ'):
    #         for root in gg.get_root(gg.branch[br]):
    #             rsha, rootbranch = root.split()
    #             if rootbranch == f'TP/{tpbranch}':
    #                 ias[rsha] = br.replace('remotes/origin/', '')
    #             # print(f'skipped:{root.split()[1]} already: {ias[root.split()[0]]}')

    # get main branch
    data = gg.logs_dict(f'origin/{branch}')       # get all logs of branch
    sha = gg.branch[f'remotes/origin/{branch}']
    integ = ias.get(sha, 'Integ/NA')

    for sha in data:
        if sha in ias:
            integ = ias[sha]
        if data[sha]['pr']:
            # allroot = ' '.join(gg.get_root(sha))
            # if branch in allroot:
            # if tpbranch in integ:
            print(sha[:9], integ, gg.pr_desc(data[sha]['desc']))

    # for _ in range(100000):
    #     # if gg.sha2branch(sha) != tps:
    #     #     print(f'-i- DONE: {sha} is now {gg.sha2branch(sha)} vs orig:{tps}')
    #     #     return   # Done
    #
    #     if data[sha]['pr']:
    #         print(sha[:9], integ, gg.pr_desc(data[sha]['desc']))
    #
    #     # get next sha
    #     found = None
    #     for parent in sorted(gg.parent[sha], reverse=True):
    #         if parent in ias:
    #             integ = ias[parent]
    #         if data[parent]['pr']:
    #             assert not found, f"double parent of {sha}: {found} {parent}"
    #             found = parent
    #     if not found:
    #         return   # Done
    #     sha = found


all_pr('TP/19R')
exit(0)

# br = 'remotes/origin/Integ/36A0Z'
# print(gg.get_root(gg.branch[br]))  # 5799150bd3193a40a54ec9d5969f9675606c5982
# exit(0)
def to_from(sha_top, sha_set, found):
    if sha_top in found:
        return
    yield sha_top
    if sha_top in sha_set:
        return    # Done
    found.add(sha_top)

    for parent in gg.parent[sha_top]:
        for result in to_from(parent, sha_set, found):
            yield result

def count_integ(branch, disp=False):
    tsha = gg.get_root(gg.branch[branch])[0].split()[0]
    ias_without = ias.keys() - {tsha}
    cnt = 0
    robj = re.compile(r'(Merge pull request #\d+)')
    for item in gg.logs(tsha, 2000):
        if item['pr']:
            if disp:
                print(item['sha'], robj.search(item['desc']).group(1))
            cnt += 1
        if item['sha'] in ias_without:
            break
    return cnt

def count_integ2(branch, disp=False):
    """
    Algo to count how many PR are there given branch
    :param branch:
    :param disp:
    :return:
    """
    root = gg.get_root(gg.branch[branch])[0]
    tsha = root.split()[0]
    ias_without = ias.keys() - {tsha}
    cnt = 0
    robj = re.compile(r'(Merge pull request #\d+)')
    start = False
    for item in gg.logs(f'origin/{root.split()[1]}', 5000):
        if not start:
            if item['sha'] == tsha:
                start = True
            else:
                continue
        if item['pr']:
            if disp:
                print(item['sha'], robj.search(item['desc']).group(1))
            cnt += 1
        if item['sha'] in ias_without:
            break
    return cnt

for br in gg.branch:
    if br.startswith('remotes/origin/Integ'):
        ias[gg.get_root(gg.branch[br])[0].split()[0]] = br

for br in gg.branch:
    if br.startswith('remotes/origin/Integ'):
        print('%s:' % br.replace('remotes/origin/', ''), count_integ2(br))
        # count_integ2(br, disp=True)

exit(0)

# rename all files
for ff in Allfiles('.'):
    if '.git/' in ff:
        continue
    bname = basename(ff)
    if not 'CLASS_P28G2' in bname:
        continue
    newname = bname.replace('CLASS_P28G2', 'CLASS_P28G1')
    # This command is for "exported path"
    # SystemCall(f'/bin/mv {ff} {dirname(ff)}/{newname}').run_outtxt()
    # This command is for "git"
    SystemCall(f'git mv {ff} {dirname(ff)}/{newname}').run_outtxt()
    print(f'Renamed: {ff}')
exit(0)

#tp = TestProgram('/intel/tpvalidation/hdmxprogs/mtl/MTLXXXXXXX19J0DSXXX/POR_TP/Class_MTL_P68/EnvironmentFile.env').pickle_init()
#tp = TestProgram('/intel/tpvalidation/hdmxprogs/mtl/MTLXXXXXXX19N0BSXXX/POR_TP/Class_MTL_P68/EnvironmentFile.env').pickle_init()
#tp = TestProgram('/intel/tpvalidation/hdmxprogs/mtl/MTLXXXXXXX19G1ESXXX/TPL/EnvironmentFile_CLASS_P68G2.env').pickle_init()
tp = TestProgram('/intel/hdmxprogs/tgl/TGLXXXXBXH15B00S204/TPL/EnvironmentFile.env').pickle_init()
for mod, item, trc in tp.mtpl.iter_flows('MAIN', passonly=False, bypass=True, traceinfo=True):
    pass
    # print(mod, item)
exit(0)


# ====================================================================================
# title: Dhanya - HVBIIOE, HVBICPU, HVBIGT
# Torch .mtpl does not have these subflows (DNG)
# TPIE .mtpl will have these, so need to get the blocks from tpie .mtpl to torch .mtpl
# ====================================================================================
from gadget.tputil import MtplBlocks
tpie = sys.argv[1]
torch = sys.argv[2]

# Read TPIE mtpl, get all blocks
mb_tpie = MtplBlocks(tpie)

# find the block first
blockfound = []
for block in 'HVBIIOE HVBICPU HVBIGT'.split():
    for item in mb_tpie.final:
        if item.endswith(f'_{block}'):
            print(f'Found: {item}')
            blockfound.append(item)

res = {}
for block in blockfound:
    if block in mb_tpie.final:
        mb_tpie.recurse(block, res)

# read torch .mtpl
mb_torch = MtplBlocks(torch)

# do some checks, keep the torch block if it already exist
for item in list(res):
    if item in mb_torch.final and mb_torch.final[item] != res[item]:
        print(f"Warning: {item} is Different. Skipping this.")
        del res[item]

mb_torch.final.update(res)    # add it
mb_torch.write('from_tpie_blocks')
exit(0)


# ==================================
# title: replace something given the inputs via CompLink
# ==================================
from gadget.tputil import MtplBlocks

# inputs
instance_list = ['SICC_X_DC_E_BEGIOEPKG_X_X_X_X_PGOFF_ALL',
                 'SICC_X_DC_E_BEGIOEPKG_X_X_X_X_PGON_ALL']
robj = re.compile(r'(bypass_global|BypassPort) = (.*);')
replacement = 'TOSRule.isphm(-1, -1, 1)'

mb = MtplBlocks(sys.argv[1])
mb.final = dict(mb.blocks)
for testname in instance_list:
    for testname, lines in mb.blocks.items():
        for idx in range(len(lines)):
            res = robj.search(lines[idx])
            if res:
                lines[idx] = '    %s = %s;\n' % (res.group(1), replacement)
mb.write()
exit(0)

# =================================
# title: get uniq lines from trc trc
# =================================
dd = {}
with open(sys.argv[1]) as fh:
    for line in fh:
        elem = line.split(',')
        dd[elem[3]] = line
for item in sorted(dd):
    print(dd[item].strip())
exit(0)

# ===================================
# title: get unique modules from git status
# ===================================
result = set()
for line in File(sys.argv[1]).chomp():
    res = re.search(r'(Modules/\w+)', line)
    if res:
        result.add(res.group(1))
print('\n'.join(sorted(result)))

exit(0)

# ===================================
# title: get all emails from git timeline: git log --all > outfile
# ===================================
user = set()
with open(sys.argv[1]) as fh:
    for line in fh:
        if 'Author:' in line:
            # normal intel
            res = re.search(r'<(\S+intel.com)>', line)
            if res:
                user.add(res.group(1))
                continue
            # github
            res = re.search(r'\d+\+(\S+)\-intel', line)
            if res:
                ename = res.group(1).replace('-', '.')
                ename = f'{ename}@intel.com'
                user.add(ename)
                continue
            print(f"Cannot process: {line.strip()}")

print(';'.join(sorted(user)))
#print('\n'.join(sorted(user)))
print(len(user))
exit(0)

# ===================================
# title: replace a string in all files
# ===================================
def replace(ff, intext, repl):
    with open(ff, 'rb') as fh:
        text = fh.read()
    text = text.replace(intext, repl)
    with open(ff, 'wb') as fh:
        fh.write(text)
    print(f"Replaced: {ff}")

from gadget.disk import Allfiles
for ff in Allfiles('.'):
    if 'proj' in ff:
        replace(ff, b"\\Shared\\Common\\", b'\\Shared\\BaseInputs\\')
exit(0)

# Print all bypass_global values (all instances)
tp = TestProgram(sys.argv[1]).pickle_init()
for mod in sorted(tp.mtpl.tdata):
    for tn in sorted(tp.mtpl.tdata[mod]):
        for param in sorted(tp.mtpl.tdata[mod][tn]):
            if param in ('bypass_global', 'BypassPort'):
                val = tp.mtpl.edata[mod][tn][param]
                try:
                    print('%s %s %s = %r' % (mod, tn, param, int(0 if val == '' else val)))
                except:
                    print('%s %s %s = %r' % (mod, tn, param, val))
exit(0)

# title: DEMO: Given a pattern, which testinstance is using it?
tp = TestProgram('/intel/hdmxprogs/mtl/MTLXXXXAXH19R00S222/POR_TP/Class_MTL_P68/EnvironmentFile.env').pickle_init()
target = 'g1834858W4639762A_9C_VC68xCR024_Hm026p00xxx0p_dxxx0808084bxxxxxxxxx_cC68R0PxxATC014J0l3_x00_ccpi_tbe_scan_x_s_ff'
for mod, item, data in tp.mtpl.iter_flows('MAIN', passonly=False, bypass=True, keyparam='patlist', edict=True):
    pats = tp.plists.get_pats_from_plb(data['patlist'])
    print('%-18s %-70s %s' % (mod, item, len(pats)))
    #if target in pats:
    #    print('%-18s %-70s %s' % (mod, item, len(pats)))
exit(0)


# title: DEMO: Display all pass flow test instances
tp = TestProgram('/intel/hdmxprogs/mtl/MTLXXXXAXH19R00S222/POR_TP/Class_MTL_P68/EnvironmentFile.env').pickle_init()
cnt = 0
for mod, item in tp.mtpl.iter_flows('MAIN', passonly=True, bypass=True, keyparam='patlist'):
    print('%4d %-18s %s' % (cnt, mod, item))
    cnt += 1
exit(0)

# Live python IDE runs ==========================================
from tp.testprogram import TestProgram, pprint

tp = TestProgram('/intel/hdmxprogs/mtl/MTLXXXXAXH19R00S222/POR_TP/Class_MTL_P68/EnvironmentFile.env').pickle_init()

# 1. get the patlist given module & testinstance
data = tp.mtpl.get_instance('ARR_CCF_C68', 'LSA_X_VMIN_K_CCLRF4_080808_VCCR_F4_2000_1506')
pprint(data)

# 2. Whats the patterns for this?
pats = tp.plists.get_pats_from_plb(data['patlist'])
pprint(pats)

# 3. What the timings?
result = tp.timing.get_period_param(data['TimingsTc'])
from gadget.tputil import time_disp
time_disp()

result = tp.levels.get_lvl_param(data['LevelsTc'], display=True)
pprint(result)  # of above

# 4. What are all the available levels?
print('\n'.join(tp.levels._levels.keys()))

# 5. show passflow -> iter_flows()

# 6. flow patlist (modify above iter_flow)
print('%-18s %-70s %s' % (mod, item, data['patlist']))

# 7. how many patterns (modify above iter_flow)
# press up arrow
pats = tp.plists.get_pats_from_plb(data['patlist'])
print('%-18s %-70s %s' % (mod, item, len(pats)))


# title: wei mrb 080321 ==========================================================================
def wei_080321_mrb():
    # 080321 MRB, given TP, and list of affected patterns (mrb7k), get which plist is this pattern
    # identify used / unused

    from gadget.helperclass import OPT
    from gadget.tputil import remove_ip
    OPT.pgmrule_disp = True
    tp = TestProgram('/intel/hdmxprogs/tgl/TGLXXXXBXH14R10S110/TPL/EnvironmentFile.env',
                     stpl='SubTestPlan_CLASS_TGLY42.stpl'
                     ).pickle_init()

    #tp.usrv.set_var('SCVars.SC_REV', 'E', 'manual')
    tp.init(skip=False)
    data = tp.mtpl.get_instance('SCN_GT', 'TRANS_GTALL_SHMOO_E_DEDC_X_VCCGT_F3_DYN_MEDIA_LIST_SECTIONAL')
    print(data['patlist'])
    exit(0)

    # read all affected pats
    allpat = {}
    fpat = {}
    for line in File('/nfs/pdx/home/jqdelosr/tpval/../mrb7k.txt').chomp():
        fname, module = line.split()
        pat = fname.split('.')[0]
        if pat[3] == '_':
            continue
        allpat[pat] = module
        fpat[pat] = fname

    # get all used patlists
    allplb = set()
    for mod, item, data in tp.mtpl.iter_flows('MAIN', passonly=False, bypass=True, keyparam='patlist', idict=True):
        allplb.add(remove_ip(data['patlist']))

    # for plb in allplb:
    #     for pat in tp.plists.get_pats_from_plb(plb):
    #         print(f'{pat},{plb}')
    # exit(0)

    for pat in allpat:
        result = set()
        allused = set()
        for plb in tp.plists.get_plbs_usedby_pat(pat):
            allused.add(plb)
            if plb in allplb:
                result.add(plb)

        if result:
            print('%s,%s,%s' % (fpat[pat], allpat[pat], ','.join(result)))
        else:
            print('%s,%s,UNUSED,%s' % (fpat[pat], allpat[pat], ','.join(allused)))


# title: jonathan ask ==========================================================================
def jonathan():
    tp = TestProgram('/nfs/pdx/disks/mpe_tvpv_085/mtl/tvpv/trash/tp/MTGEBSC12B1504KAP0/EnvironmentFile.env').pickle_init()
    seen = set()
    for dutflow, dutflowitem, trc in tp.mtpl._recurse_flow('MAIN', ['MAIN'], '', set(), {}):
        # don't print duplicates
        if (dutflow, dutflowitem) in seen:
            continue
        seen.add((dutflow, dutflowitem))

        # one dutflow item
        module, testinstance = tp.mtpl.get_flow_instance(dutflow, dutflowitem)
        print(f'dutflow={dutflow} dutflowitem={dutflowitem}')   # trace={trc}'

        # display/process the port
        dfi = tp.mtpl._dutflow[dutflow][dutflowitem]
        for port in dfi:
            if port == 999:   # special key
                continue
            if 'GoTo' in dfi[port]:
                print(f'   {port:2}: GoTo {dfi[port]["GoTo"]}')
            else:
                print(f'   {port:2}: Return {dfi[port]["Return"]}')

# ==========================================================================
# title: merge the softbins of two BinDefinitions.bdefs (sds and sdt) - sys.arg[1] and sys.arg[2]
import sys
def readsoft(fname):
    """Read BinDefinitions.bdefs and return dict of softbins"""
    with open(fname) as fh1:
        start = False
        dd = {}
        for line in fh1:
            oline = line.rstrip()
            line = line.strip()

            if line.startswith('BinGroup SoftBins'):
                start = True
                continue
            if line.startswith(('{', '}', 'SortBinGroup =')) or not line:
                continue
            if start:
                elem = line.split()
                key = (elem[1], int(elem[2]))
                assert key not in dd, key
                dd[key] = oline
    return dd

def writesoft(fname, d1, d2):
    """Read BinDefinitions.bdefs and print combined"""
    print(f'Total: {len(d1)+len(d2)}')
    d2.update(d1)
    print(f'Final: {len(d2)}')
    with open(fname) as fh1:
        start = 0
        for line in fh1:
            oline = line.rstrip()
            line = line.strip()

            if line.startswith('BinGroup SoftBins'):
                start = 1
                print(oline)
                continue
            if line.startswith(('{', '}', 'SortBinGroup =')) or not line:
                print(oline)
                continue
            if start:
                if start == 1:
                    for key in sorted(d2, key=lambda x: x[1]):
                        print(d2[key])
                    start = 2
            else:
                print(oline)

d1 = readsoft(sys.argv[1])
d2 = readsoft(sys.argv[2])

# Write it
writesoft(sys.argv[1], d1, d2)


# =============================================================
# title: remove all duplicate softbins in .mtpl:
# step0: Need to run readsoft() and writesoft() first to merge BinDefinitions.bdefs
# step1: demo.py Modules/*/*.mtpl POR_TP/*/ProgramFlowsTestPlan/*.mtpl
# (Above will modify all .mtpl files, replace the softbin names)
# step2: rename Shared/Common/BinDefinitions.bdefs.new to Shared/Common/BinDefinitions.bdefs
from gadget.files import File
import sys
import re
import os

def readbin(fname):
    """Read BinDefinitions.bdefs and return dict {removed: replaced}"""
    with open(fname) as fh1:
        start = False
        dd = {}    # {removed: name_to_keep}
        reg = {}   # {softbin: name}
        for line in fh1:
            line = line.strip()

            if line.startswith('BinGroup SoftBins'):
                start = True
                continue
            if line.startswith(('{', '}', 'SortBinGroup =')) or not line:
                continue
            if start:
                elem = line.split()
                name, softbin = elem[1], int(elem[2])
                if not softbin in reg:
                    reg[softbin] = name
                    continue    # keep this
                dd[name] = reg[softbin]
    return dd

def hack_bindef(fname, dd, rr):
    """
    Hack mtpl, rename softbin based on dd dictionary
    :param fname: mtpl file
    :param dd: {removed: name_to_keep}
    :return:
    """
    print(f"Processing {fname}")
    with open(fname) as fh1, open(f'{fname}.new', 'w') as fho:
        for line in fh1:
            res = rr.search(line)
            if res:
                continue
            fho.write(line)

def hack_mtpl(fname, dd, rr):
    """
    Hack mtpl, rename softbin based on dd dictionary
    :param fname: mtpl file
    :param dd: {removed: name_to_keep}
    :return:
    """
    # performance: 00.5 for regex, 5.81 if forloop dd
    print(f"Processing {fname}")
    with open(fname) as fh1, open(f'{fname}.new', 'w') as fho:
        for line in fh1:
            res = rr.search(line)
            if res:
                line = line.replace(res.group(1), dd[res.group(1)])
            fho.write(line)
    File(fname).unlink()
    File(f'{fname}.new').rename(os.path.basename(fname))

dremove = readbin('Shared/Common/BinDefinitions.bdefs')
rr = re.compile(r'\b(%s)\b' % '|'.join(dremove))
hack_bindef('Shared/Common/BinDefinitions.bdefs', dremove, rr)
for ff in sys.argv[1:]:
    hack_mtpl(ff, dremove, rr)

exit(0)

# ==============================================
# title: hack mtproj to add IP_CPU_BASE common
# ==============================================
all = r'''
		..\..\Modules\ARR_COMMON_GXX\ARR_COMMON_GXX_CLASS_P68G2.mtpl;
		..\..\Modules\ARR_GT_GXX\ARR_GT_GXX_CLASS_P68G2.mtpl;
		..\..\Modules\DRV_RESET_GXX\DRV_RESET_GXX.mtpl;
		..\..\Modules\FUN_GT_GXX\FUN_GT_GXX_CLASS_P68G2.mtpl;
		..\..\Modules\SCN_GT_GXX\SCN_GT_GXX_CLASS_P68G2.mtpl;
		..\..\Modules\TPI_BASE_IPPCH\TPI_BASE_IPPCH.mtpl;
		..\..\Modules\TPI_ENDIPPCH_XXX\TPI_ENDIPPCH_XXX_CLASS_P68G2.mtpl;
		..\..\Modules\TPI_GFXAGG_GXX\TPI_GFXAGG_GXX_CLASS_P68G2.mtpl;
		..\..\Modules\TPI_PRESI_PXX\TPI_PRESI_PXX.mtpl;
		..\..\Modules\TPI_PWRUP_HXX\TPI_PWRUP_HXX.mtpl;
		..\..\Modules\YBS_INTRPPRE_GXX\YBS_INTRPPRE_GXX_CLASS_P68G2.mtpl;
'''

from os.path import dirname, basename, exists
import os
def hack_mtproj(ff):   # Hack .mtproj
    with open(ff) as fh:
        text = fh.read()
    if 'ipctproj' in text:
        print(f'{ff} is already done')
        return
    final = []
    with open(ff, 'r') as fh:
        for line in fh:
            final.append(line)
            if 'ProjectReference' in line:
                final.append(r'    <ProjectReference Include="..\..\Shared\IP_PCH_BASE\IP_PCH_BASE.ipctproj" />\n')
    os.unlink(ff)
    with open(ff, 'w') as fh:
        fh.write(''.join(final))
    print(f'{ff} written')

def hack_mconfig(ff):    # Hack module.mconfig
    ff = f'{dirname(ff)}/module.mconfig'
    if not exists(ff):
        return
    with open(ff) as fh:
        text = fh.read()
    if 'IPName' in text:
        print(f'{ff} is already done')
        return
    final = []
    with open(ff, 'r') as fh:
        for line in fh:
            if '/ModuleConfiguration' in line:
                final.append('<IPName>IP_PCH</IPName>\n')
            final.append(line)
    os.unlink(ff)
    with open(ff, 'w') as fh:
        fh.write(''.join(final))
    print(f'{ff} written')

def main():
    for item in all.split('\n'):
        if not item:
            continue
        ff = dirname(item.strip()[6:-1].replace('\\', '/'))
        targ = f'{ff}/{basename(ff)}.mtproj'
        if not exists(targ):
            print(f'oops: {targ}')
            exit(0)
        hack_mtproj(targ)
        hack_mconfig(targ)
main()
exit(0)

# ==============================================
# title: Identify filenames that has special characters
# ==============================================
import re
from gadget.disk import Allfiles
from os.path import basename
for ff in Allfiles('.', skipsvn=True):
    bn = basename(ff)
    res = re.findall(r'[^\w\.\-\!]', bn)
    if res:
        print(res, ff)
exit(0)

# ==============================================
# update all content_expect from found
# ==============================================
import sys
import re
r1 = re.compile(r' found=(\d+)')
fname = sys.argv[1]
final = []
with open(fname) as fh:
    for line in fh:
        res = r1.search(line)
        if res:
            final.append(line.replace('content_expect=1', f'content_expect={res.group(1)}'))
        else:
            final.append(line)

with open(fname, 'w') as fh:
    fh.write(''.join(final))
print("Done.")
exit(0)


# ==============================================
# title: how many different domains per domain
# ==============================================
import re
from os.path import basename, dirname
from gadget.files import File
for line in sorted(re.findall(r'Modules.(\w+)', File(sys.argv[1]).read())):
    print(line)
exit(0)
robj = re.compile(r'PrimeFlowControlForkTestMethod\s+(\w+)', re.MULTILINE)
result = {}
for mtpl in sys.argv[1:]:
    mod = basename(dirname(mtpl))
    result[mod] = set(robj.findall(File(mtpl).read()))
for item in result:
    if len(result[item]) > 1:
        print(item, result[item])
exit(0)

# ===================================
# title: get all users from Integration_Report.txt in all files
# cd ~/mtl
# demo.py */*/TPL*/Reports/Integration_Report.txt
# ===================================
user = set()
for ff in sys.argv[1:]:
    with open(ff) as fh:
        for item in re.findall(r'^\s*\w+\s+(\w+)\s+\S+_(AM|PM)', fh.read(), re.MULTILINE):
            # print(item)
            user.add(item[0])
print(';'.join(sorted(user)))
print(len(user))
exit(0)

# =====================================
# proof of reproduceable sorting
# =====================================
# from random import shuffle
# from collections import OrderedDict
# keys = list('abcdefghijklmnopqrstuvwkyx')
# for _ in range(3):
#     shuffle(keys)
#     dep_sortable = OrderedDict([(x, 2) for x in keys])
#     psorted = sorted(dep_sortable, key=lambda x: (dep_sortable[x], x))
#     print(psorted)
