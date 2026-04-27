#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Ensures submodule changes are newer, unless label, 'revert_submodule' is specified in PR
https://hsdes.intel.com/resource/22018448928
https://hsdes.intel.com/resource/14019978721

This qgate only works from a PR folder
"""
import sys
import setenv

from gadget.pylog import log
from qgates.qgate_base import QGateBase
from main.qgate import QGateExecute
from tp.testprogram import TestProgram
from gadget.getgit import GetCmd, GitHub
from gadget.shell import SystemCall, IS_UNIX
from gadget.errors import confirm
from gadget.disk import Chdir
from pprint import pprint
from os.path import basename
import re
import os


class NewerSub(QGateBase):
    is_unix = IS_UNIX

    def main(self):
        """Entry point of checker"""
        if self.is_unix:    # pragma: no cover
            log.info("-i- newer_submodule() is skipped because IS_UNIX")
            return

        # This qgate is applicable only on PR. Ignore for tpbuild.
        if self.not_from_pr():     # pragma: no cover
            log.info(f'-i- {self.__class__.__name__} is skipped, not from PR.')
            return 1

        with Chdir(QGateExecute.repodir):    # We must be inside the original repo checkout
            log.info(f'newer_submodule(): cwd: {os.getcwd()}')

            # Step1 - Get pr label, skip if revert_submodule
            pr_labels = GitHub.get_labels()
            if 'revert_submodule' in pr_labels:
                log.info('-i- newer_submodule is skipped due to revert_submodule label existence')
                return

            # Step2 - Get Submodule Changes
            for subm, sha_a, sha_b in self.get_submodule_changes():

                # Step3 - Check if newer
                self.is_newer(subm, sha_a, sha_b)

    def get_submodule_changes(self):
        """
        Get submodule changes in PR

        :return: submodule_folder, sha_a, sha_b
        """
        r_mod = re.compile(r'diff --git a/(\S+)')   # This applies to modified, add and deleted
        r_sm = re.compile(r'^(.)Subproject commit (\S+)')
        rpath = None
        sha_a = None

        # Run gh pr diff
        cmd = "gh pr diff"
        _, out = SystemCall(GetCmd.exe(cmd)).run_outtxt()
        alines = out.split('\n')
        log.info(f'newer_submodule: [gh pr diff] output is {len(alines)} lines')

        for line in alines:
            res = r_mod.search(line)
            if res:
                rpath = res.group(1)

            res = r_sm.search(line)
            if res:
                if res.group(1) == '-':
                    sha_a = res.group(2)

                if res.group(1) == '+':
                    # At this point it is submodule
                    confirm(rpath, 'rpath marker not found!', 'contact jqdelosr')
                    # confirm(sha_a, 'sha_a marker not found!', 'contact jqdelosr')    # sha_a can be None, when very first submodule commit
                    log.info(f'-i- newer_submodule found: {rpath} {sha_a} {res.group(2)}')
                    yield rpath, sha_a, res.group(2)

    def is_newer(self, subm, sha_a, sha_b):
        """
        Performs the check.
        Logic: "git log" shows the sha history order.
        If sha_a is inside "git log <sha_b>", then sha_b is confirmed newer compared to sha_a.

        :param subm: submodule folder
        :param sha_a: sha_a (from)
        :param sha_b: sha_b (to)
        :return: None
        """
        with Chdir(subm):    # We must be inside the submodule folder
            cmd = f'git log {sha_b} --pretty=format:"%H"'
            log.info(f'CMD: {cmd}')
            _, out = SystemCall(GetCmd.exe(cmd)).run_outtxt()
            alines = [x.strip() for x in out.split('\n')]
            if len(alines) < 10:
                log.info(f'[git log {sha_b}] output:')
                log.info(out)
            else:
                log.info(f'[git log {sha_b}] output is {len(alines)} lines')
            md = basename(subm)

            # make sure git log output is correct
            if alines[0] != sha_b:
                self.add_error(231, md, (f'Output of [git log] seems to be incorrect since first sha is not found '
                                         f'{sha_b} vs [{alines[0]}]. Pls check above output.'))
                return

            # do the compare of newer vs older
            if sha_a in alines + [None]:     # None for initial submodule
                self.add_pass(231, md)
            else:
                self.add_error(231, md, (f'Commit sha of {subm} is from older rev. From: {sha_a} to {sha_b}. '
                                         f'Did you mean to revert the submodule? If so, add [revert_submodule] label in the PR.'))


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    NewerSub(TestProgram(sys.argv[1])).run()
