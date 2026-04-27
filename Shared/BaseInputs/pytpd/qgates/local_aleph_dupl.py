#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
This Qgate is checking the individual local Aleph files for Fuse Modules only and check if there are duplicate register names with other Fuse modules
"""
import setenv  # must be first in the imports
from gadget.dictmore import xmlfunc, iter_dot_items, find_dot_items
from gadget.pylog import log
from gadget.tputil import remove_ip
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
from gadget.tputil import JsonRead
from pprint import pprint
from collections import defaultdict
from gadget.errors import ErrorInput
import sys
from tp.testprogram import TestProgram, Env
import os
import json


class LocalAleph(QGateBase):

    def main(self):
        envpath = self.tpobj.envdir
        envfile = envpath + '/EnvironmentFile.env'
        allnamereg = defaultdict(set)  # {mod: <set_of_names>}
        envobj = Env(os.path.abspath(envfile))
        torchauto = envobj.get_contents('TORCH_AUTO_ALEPH_FILES', default='', islist=True)
        alephfiles = envobj.get_contents('ALEPH_FILES', islist=True)
        allaleph = torchauto + alephfiles
        allaleph = [x.strip() for x in allaleph]  # remove any whitespace
        for i in range(len(allaleph)):

            # ignore if not exist
            if not(os.path.exists(allaleph[i])):
                continue

            # ignore if not json
            if not allaleph[i].endswith('.json'):
                continue

            try:
                json_object = JsonRead(allaleph[i]).load()
            except ErrorInput:
                self.add_error(251, 'BASE', f'{allaleph[i]} failed json reader.  Please fix by using a json parser')
                continue

            if isinstance(json_object, list):
                print(allaleph[i], "is a list")
                continue

            for keys, values in json_object.items():
                for keyval in values:
                    if isinstance(keyval, dict):
                        for keys2, values2 in keyval.items():
                            if keys2.startswith('Name') or keys2.startswith('name') or keys2.startswith('RegisterName'):
                                mod = allaleph[i].split('/')[-3]
                                fuse = allaleph[i].split('/')[-4]
                                patmod = allaleph[i].split('/')[-1]
                                if 'FUS' in fuse or 'PTH' in fuse or 'patmod' in patmod:
                                    if isinstance(values2, str):
                                        values2 = values2.strip()
                                        self.process_values(allnamereg, allaleph[i], values2, mod)
                                    if isinstance(values2, list):
                                        for j in range(len(values2)):
                                            values2[j] = values2[j].strip()
                                            self.process_values(allnamereg, allaleph[i], values2[j], mod)

    def process_values(self, allnamereg, aleph, values, mod):
        afile = aleph.split('/')[-1]
        for k, v in allnamereg.items():
            if k != mod and values in v:
                self.add_error(251, mod,
                               f'File: {afile} used by: {mod} is using a DUPLICATE value: "{values}" that is used by "{k}" json file(s)  Please check if valid')
                break
            else:
                self.add_pass(251, mod)
        else:
            allnamereg[mod].add(values)


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    LocalAleph(TestProgram(sys.argv[1]).pickle_init()).run()
