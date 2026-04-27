#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Checks the pattern/plist and patmodify paths in the env file to make sure that they exist
to ensure tptorrent will not fail (including the proper letter case)
"""
import setenv  # must be first in the imports
from gadget.dictmore import xmlfunc, iter_dot_items, find_dot_items
from gadget.pylog import log
from gadget.tputil import remove_ip
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
from tp.testprogram import Env
from collections import defaultdict
from pprint import pprint
import sys
import os
import re


class EnvPatCase(QGateBase):

    def main(self):
        modrev = defaultdict(set)
        modlist = defaultdict(list)
        mapmodd = defaultdict(list)
        listdir_cache = {}
        r_path = re.compile(r'^(\S+)\/+(\w+)\/+(Rev[\w\.]+)\/+(\S+)')

        for varname in self.tpobj.env.get_env_dict():
            for item in self.tpobj.env.get_contents(varname, islist=True):
                if item.startswith(('I:', 'i:', '/intel')):
                    if 'hdmxpats' in item:
                        item2 = item.replace('\\', '/')
                        pathbreak = r_path.search(item2)
                        if not pathbreak:
                            # self.add_error(314, "BASE", f'Invalid path {item} found in env file')
                            continue
                        mod = pathbreak.group(2)
                        rev = pathbreak.group(3)
                        modrev[mod].add(rev)
                        listme = pathbreak.group(1) + '/' + mod
                        if listme not in listdir_cache:
                            if os.path.isdir(Env.xpath(listme)):
                                listdir_cache[listme] = os.listdir(Env.xpath(listme))
                            else:
                                listdir_cache[listme] = [rev]
                        folder = listdir_cache[listme]
                        modlist[mod].extend(folder)

        # This block is for getting the module names for messaging purpose
        for mod in modrev:
            mapmod = self.tpobj.plists.get_cimod2mod_map().get(mod, ['NA'])
            mapmodd[mod].extend(mapmod)

        # check it
        for mod, rev_list in modrev.items():
            for rev in rev_list:
                if rev in modlist[mod]:
                    for tpmodule in mapmodd[mod]:
                        self.add_pass(314, tpmodule)
                else:
                    for tpmodule in mapmodd[mod]:
                        self.add_error(314, tpmodule, f'.env file hdmxpats rev case-mismatch for {mod}: '
                                                      f'{rev} does not exist. Please fix case name of the rev.')


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    EnvPatCase(TestProgram(sys.argv[1]).pickle_init()).run()
