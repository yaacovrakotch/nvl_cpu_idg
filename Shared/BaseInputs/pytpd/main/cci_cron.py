#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Automatic run of cci

Usage:
   source /intel/tpvalidation/engtools/tptools/mtl/infra/torch/tpinfra_runner/proxy.cshrc
   /intel/tpvalidation/engtools/tptools/mtl/beta/pytpd.jqdelosr/main/cci_cron.py

For debug and development:
   cci_cron.py -once

"""

import setenv        # must be first in the imports
from gadget.shell import SystemCall
from gadget.strmore import curtime
from gadget.disk import Chdir
from gadget.gizmo import Elapsed
from gadget.files import File
from gadget.getgit import GetCmd
from mod.cci_list import CCI
from os.path import basename, exists
import time
import sys
import os
import json
import glob


class CCICron:
    """
    Inifiniteloop run

    # json structure: each file is a json for one main branch:
    {"repo": "/nfs/pdx/disks/mpe_sctp_004/torch/repo_checkouts/MTL68",
     "logfile": "/intel/engtools/tptools/mtl/logs/cci_metric/39.log",
     "basebranch": "TP/39",
     "autoready": 0,      # Default is 1. Set to 0 to disable for this main branch.
     "offline": 1,        # Default is 0. Set to 1 to enable offline for this main branch.
     }
    """
    ROOT = '/intel/tpvalidation/engtools/tptools/mtl/infra/torch/cci_cron'

    def __init__(self):
        self.repos = None
        self.read_repos()

    def read_repos(self):
        """
        Read the repo json files. See above for json file structure
        """
        self.repos = {}
        for item in glob.glob(f'{self.ROOT}/*.json'):
            with open(item) as fh:
                try:
                    data = json.load(fh)
                except json.decoder.JSONDecodeError as e:
                    print(f'Error: {item} has error: {e}')
                    continue

                for ky in data:
                    if ky not in 'repo logfile basebranch autoready offline'.split():
                        print(f"Error: {item} has [{ky}] which is invalid.")

                self.repos[basename(item)] = data

    def one_run(self, item):
        """Execute one item"""
        with Chdir(self.repos[item]['repo']):
            cci = CCI(self.repos[item]['basebranch'], 100, 'open', disp=False)
            cci.read_config()
            cci.main_init()

            result = self.process(cci.data, list(cci.get_prs('open')))

            # write it
            txt = (f"open={result['open']} "
                   f"wip={result['wip']} "
                   f"ready={result['ready']} "
                   f"fail_tester={result['fail_tester']} ")
            fname = self.repos[item]['logfile']
            File(fname).logprint(txt)
            print(f'{curtime()}: {basename(fname)} {txt}')

    @classmethod
    def process(cls, data, open_pr):
        """
        :param data: {pr: <dict>}
        :param open_pr: [list of pr number]
        :return:
        """
        wip = [x for x in open_pr if 'TEST_IN_PROGRESS' in data[x]['labels']]

        # get ready list, excluding test_in_progress
        ready = set()
        for pr in open_pr:
            for label in data[pr]['labels']:
                if 'READY' in label:
                    if 'TEST_IN_PROGRESS' not in data[pr]['labels']:
                        ready.add(pr)

        # get failed on tester
        fail_tester = set()
        for pr in open_pr:
            for label in data[pr]['labels']:
                if 'FAILED' in label:
                    if 'PASSED_Chk' in data[pr]['labels']:
                        fail_tester.add(pr)

        return {'open': len(open_pr),
                'wip': len(wip),
                'ready': len(ready),
                'fail_tester': len(fail_tester)}

    def main(self, loop=10000000, nap=60 * 5):
        """
        Entry point, infiniteloop (well, 95 years worth of loop at 5 min nap)

        :param loop: Max loop
        :param nap: sleep time in seconds
        :return: None
        """
        isdebug = bool('-once' in sys.argv)
        for _ in range(loop):
            sw = Elapsed()

            self.read_repos()
            for item in self.repos:
                try:
                    self.one_run(item)
                    AutoReady().main(self.repos[item]['repo'],
                                     self.repos[item]['basebranch'],
                                     autoready=self.repos[item].get('autoready', 1),
                                     offline=self.repos[item].get('offline', 0),
                                     )
                except Exception as e:     # pragma: no cover
                    print("Ooops Error exception: {e}")

            print(f'{curtime()}: Elapsed: {sw}')
            if isdebug:
                return
            time.sleep(nap)


class AutoReady:
    """
    Auto-ready label add
    """
    ghexe = '/intel/tpvalidation/engtools/tptools/mtl/tools/gh/gh_2.82.0_linux_amd64/gh'

    def main(self, path, branch, autoready=1, offline=0):
        """
        Execute one repo for auto ready label add

        :param path: repo path
        :param branch: branch
        :param autoready: boolean, True for enabled autoready
        :param offline: boolean, True for offline enabled (require the other label)
        :return: unittest only
        """
        ctr = 0
        with Chdir(path):
            cci = CCI(branch, 100, 'open', disp=False)
            cci.read_config()
            cci.main_init()
            bundle_pr = self.id_bundle(cci)

            for prno in cci.get_prs('open'):
                ctr += 1
                labels = cci.data[prno]['labels']
                approved = cci.data[prno]['approved']
                age = cci.data[prno]['update_age']
                # print('-i-', prno, approved, labels, age)

                # Criteria:
                # 0. it is not draft  (For loop query is 'open' pr only)
                # 1. It is approved
                # 2. It is passing checkers
                # 3a. It does not have READY label         # _is_ready_exist())
                # 3b. It is not a BUNDLE PR                # _is_ready_exist())
                # 3c. It does not have FAILED label        # _is_ready_exist())
                # 3d. It does not have NO_AUTO_RDY label   # _is_ready_exist())
                # 4. tprobot is not run yet
                # 5. It is not part of bundle
                # 6. Special file to enable/disable does not exist
                # 7. 10 mins of no activity in the PR (previously 30 mins, not an issue even if we are bundling)
                pass_chk_label = self.get_pass_chk_label(labels)
                if (approved == 'Approved' and
                        pass_chk_label.issubset(labels) and
                        (not self._is_ready_exist(labels)) and
                        ('PASSED_Si' not in labels) and
                        prno not in bundle_pr and
                        autoready and
                        self.is_offline(offline, labels) and
                        age > 10 * 60):    # 10 mins of no activity

                    print(f'{curtime()}: Adding ready label {prno}: {approved}, age:{int(age)}, '
                          f'branch={branch}, repo={basename(path)}, labels:{labels}')
                    cmd = f'{self.ghexe} pr edit {prno} --add-label READY'
                    _, out = SystemCall(GetCmd.exe(cmd), disp=True).run_outtxt()

        return ctr    # for unittest

    def get_pass_chk_label(self, labels):
        """
        Return set of expected passing labels

        mtl/arl: {PASSED_Chk}
        nvl: {PASSED_<bom>}
        """
        passed = set()
        expectbom = -1
        for item in labels:
            if item == 'PASSED_OFFLINE':
                continue        # ignore this special arl passed_offline label

            if item.startswith('PASSED_'):
                passed.add(item)

            if item.startswith('BOMCNT'):
                expectbom = int(item[6:])

        # case1 - PASSED_Chk exist - known mtl/arl
        if passed == {'PASSED_Chk'}:
            return {'PASSED_Chk'}    # default

        # case2 - no PASSED_ labels
        if not passed:
            return {'PASSED_Chk'}    # default - we don't know if arl/nvl

        # case3 - nvl PASS case
        if len(passed) == expectbom:
            return passed            # return the same set, meaning we are good

        return {'__NO_MATCH__'}      # no match

    def is_offline(self, offline, labels):
        """Return True if offline is enabled"""
        if not offline:
            return True    # default
        if 'PASSED_OFFLINE' in labels:
            return True
        return False

    def id_bundle(self, cci):
        """Return set of pr that in bundle"""
        result = set()
        for prno in cci.get_prs('open'):
            title = cci.data[prno].get('title', '')
            if title.startswith('bundle of') and ':' in title:
                prs = title.split(':')[1].strip().split()
                result.update([int(x.replace('#', '')) for x in prs])
                result.add(prno)
        return result

    @classmethod
    def _is_ready_exist(cls, labels):
        """
        :param labels: set of labels
        :return: True if ready label exist
        """
        found = False
        for label in labels:
            if 'READY' in label:
                found = True
            if 'FAILED' in label:    # Do not run FAILED PR
                found = True
            if 'BUNDLE' in label:
                found = True
            if 'NO_AUTO_RDY' in label:
                found = True
            if 'I_AM_TPI_Skip_Bot' in label:
                found = True
            if 'TEST_IN_PROGRESS' in label:     # PR is already being tested
                found = True
        return found


if __name__ == '__main__':  # pragma: no cover
    CCICron().main()


# note: This needs configuration if mbot and tpbot are shared.
# "gh workflow view MBOT_P28B0"
# ===========================
# MBOT_P28B0 - mrobot_P28B0.yml
# ID: 45472704
#
# Total runs 188
# Recent runs
# completed       success Removing IP patterns from PKG module    MBOT_P28B0      DRV/ODRV6-1012  workflow_dispatch       47m35s  4347148801
# completed       failure Removing IP patterns from PKG module    MBOT_P28B0      DRV/ODRV6-1012  workflow_dispatch       1m15s   4347110504
# in_progress     Merge branch 'TP/37' into TPI/37C_nonprqchk     TPRobot_P28     TPI/37C_nonprqchk       pull_request    9s      4348385693
#
#
