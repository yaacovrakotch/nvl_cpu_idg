#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Ensures patterns that will be transferred to JF, FM and PG
This is to avoid the issue with missing patterns in other sites.
"""
import sys
import setenv

from gadget.pylog import log
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
from gadget.data_host import DataHost
import os


class CheckPatterns_AllSites(QGateBase):
    """
    Check if patterns exists in JF, FM, and PG.
    """

    def main(self):
        """Entry point of checker"""
        self.tpobj = TestProgram(self.tpobj.envfile)

        # This qgate is applicable only on PR. Ignore for tpbuild.
        if self.not_from_pr():     # pragma: no cover
            log.info(f'-i- {self.__class__.__name__} is skipped, not from PR.')
            return 1

        paths_to_check = self.get_class_plist_pat()
        for site in 'JF PG FM'.split():
            log.info(f'-i- Patterns site check starts in {site}.')

            try:
                result = DataHost().central("path_exists", paths_to_check, check=True, site=site)
            except Exception:
                result = {}

            for pattern, exist_flag in result.items():
                self.check(exist_flag, 258, 'BASE', f'{pattern} does NOT exist in {site}')

    def get_class_plist_pat(self):
        """Iterator: returns class plist"""
        self.tpobj.env.set_env()
        paths_to_check = []
        for item in sorted(self.tpobj.env.get_plist_paths()):
            if not item.endswith('plb'):
                continue       # skip slim path
            if 'hdmxpats' not in item:
                continue

            paths_to_check.append(item)
        return paths_to_check


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    CheckPatterns_AllSites(TestProgram(sys.argv[1]), frompr=True).run()
