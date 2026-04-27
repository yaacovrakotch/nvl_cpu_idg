#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Sort bot stuff

Usage 1: labeller only
sort_bot.py ${{ github.base_ref }} ${{ github.event.pull_request.head.ref }}

Usage 2: qualdoc checker only
sort_bot.py -qualdoc

"""
from setenv import ROOT_ENV      # must be first in the imports
from gadget.gizmo import Elapsed
from gadget.shell import SystemCall
from gadget.errors import ErrorUser
from gadget.getgit import GitHub, GetCmd
from main.nvl_buildtp import NVLBuildTP
from os.path import basename, exists
import sys
import os
import re

# Below is a simple way to inform user if they are python version <3.5. This is checked before any other code during the Parsing phase.
f'If you see SyntaxError, this means your python version is old. Pls upgrade to python3.8 minimum: http://python.org/downloads'


class SortBot:

    def __init__(self):
        pass

    def main(self):
        """
        Main Entry point
        """
        if len(sys.argv) == 1:
            print("Nothing to do. Base branch is not specified")
            return 1

        self.qualdoc_check()      # Independent routine, This will exit, if set

        refbranch = sys.argv[1]
        localbranch = sys.argv[2]

        # add labels ==============
        cmd = f'gh pr diff {sys.argv[2]}'
        try:
            _, out = SystemCall(GetCmd.exe(cmd), disp=True).run_outtxt()
        except UnicodeDecodeError:    # pragma: no cover
            print("Skip SortBot - UnicodeDecodeError")
            return      # Do nothing when there is error

        modfiles = GitHub._proc_pr_diff(out)

        newlabels = NVLBuildTP.id_labels(modfiles)

        GitHub.add_labels(newlabels, branch=localbranch)

        # add milestone - This is only applicable to WaterFall method, thus commenting
        # milestone = basename(refbranch)
        # cmd = f'gh pr edit {localbranch} --milestone {milestone}'
        # _, out = SystemCall(GetCmd.exe(cmd), disp=True).run_outtxt()

        self.remove_old_labels(newlabels)

    @classmethod
    def qualdoc_check(cls):
        if '-qualdoc' not in sys.argv:
            return 1     # do nothing, backwards compatible

        _, out = SystemCall(GetCmd.exe('gh pr view'), disp=True).run_outtxt()

        if '[x] tpdb qualdoc' in out.lower():
            exit(0)      # pass, exit out

        robj = re.compile(r'(\[\s*x\s*\].*)$')
        for line in out.lower().split('\n'):
            if '[x]' in line:   # valid line
                continue
            res = robj.search(line)
            if res:
                raise ErrorUser(f'"{res.group(1)}" is an invalid line in PR."',
                                f'Pls replace it with "[X]" (no spaces) so that it will render correctly.')

        raise ErrorUser('"tpdb Qualdoc" is not specified for this PR',
                        'Pls Make sure Qualdoc is in place, then tick the checkbox on the PR description of TPDB Qualdoc')

    def remove_old_labels(self, newlabels):
        """Remove old labels"""
        labels = GitHub.get_labels()

        # Get all auto-generated labels
        all_tp_labels = set('Misc UserCode TPConfig YML PORTP Shared'.split())   # These are special labels in id_labels()
        if exists('Modules'):
            for ff in os.listdir('Modules'):
                all_tp_labels.add(ff)
                all_tp_labels.add(ff.split('_')[0])    # team name

        # remove unknown labels
        extra = (labels - newlabels) & all_tp_labels
        if extra:
            GitHub.remove_labels(extra)


if __name__ == '__main__':  # pragma: no cover
    SortBot().main()
