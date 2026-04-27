#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
wiki: https://wiki.ith.intel.com/x/ZRfT_

Ensures owner.txt exist and has correct format
"""
import sys
import setenv
from gadget.files import File, basename_n
from gadget.pylog import log
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram, Env
from pprint import pprint
from os.path import exists, dirname
from collections import defaultdict
import re


class OwnerTxt(QGateBase):

    def main(self):
        """Entry point of checker"""
        # This qgate is applicable only on PR. Ignore for tpbuild.
        if self.not_from_pr():     # pragma: no cover
            log.info(f'-i- {self.__class__.__name__} is skipped, not from PR.')
            return 1

        folder2mod = self.tpobj.mtpl.get_modfolder2mod()
        mod2path = self.tpobj.mtpl.get_mod2fname()     # {module_test_plan_name: mtpl_file_path}
        url = 'https://wiki.ith.intel.com/x/ZRfT_'    # wiki page

        # check path structure consistency - Peach request
        rpath = re.compile(r'Modules/\w+/\w+/\w+\.mtpl')
        for testplan_name, mtpl in sorted(mod2path.items()):
            if 'Modules' not in mtpl:
                continue

            if rpath.search(mtpl.replace('\\', '/')):
                self.add_pass(261, testplan_name)
            else:
                errmsg = (f'{Env.xpath(basename_n(mtpl, 3))} does not follow Module .mtpl structure. '
                          'Expecting: Modules/<team>/<modulefolder>/<file>.mtpl')
                self.add_error(261, testplan_name, errmsg)

        # check owners.txt
        robj = re.compile(r'^(owner|manager):\s+(\w+|[\w\s]+ Members)$')
        for modname in folder2mod:
            mtpl = mod2path.get(folder2mod[modname])
            found = defaultdict(int)

            # Modules only
            if 'Modules' not in mtpl:
                continue

            # check old location
            ownerfilex = f'{Env.xpath(dirname(mtpl))}/InputFiles/owner.txt'
            ownerfilex_short = Env.xpath(basename_n(ownerfilex, 3))
            ownerfile = f'{Env.xpath(dirname(mtpl))}/owner.txt'
            ownerfile_short = Env.xpath(basename_n(ownerfile, 2))
            if exists(ownerfilex):
                self.add_error(259, modname, (f'Pls move {ownerfilex_short} to {ownerfile_short}; '
                                              'Reason: InputFiles/ are files meant to be loaded on tester.'))
                continue

            # Check existence first
            if not exists(ownerfile):
                self.add_error(259, modname, f'{ownerfile_short} does not exist. This is required, see: {url}')
                continue

            # Check validity
            for line in File(ownerfile).chomp(comment='#', strip=True):
                res = robj.search(line)
                if res:
                    self.add_pass(259, modname)
                    found[res.group(1)] += 1
                else:
                    errmsg = f'{ownerfile_short} has invalid line: [{line}]. Expecting "(owner|manager): <idsid>". One only. See: {url}'
                    self.add_error(259, modname, errmsg)

            # Make sure it is complete
            missing = sorted({'owner', 'manager'} - found.keys())
            self.check(not missing, 259, modname, f'{ownerfile_short} is missing: {missing} keyword. See {url}')

            # make sure it is one only
            for item in found:
                self.check(found[item] == 1, 259, modname, f'{ownerfile_short} has multiple {item}. Expecting 1 only.')


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    OwnerTxt(TestProgram(sys.argv[1]), frompr=True).run()
