#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
This will run an executable file to execute TPtorrent B69 check.
If there is B69, gating the PR.
"""
import sys
import setenv

from gadget.dictmore import xmlfunc, iter_dot_items, find_dot_items
from gadget.pylog import log
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
from gadget.shell import SystemCall
from gadget.errors import ErrorInput, confirm
from pprint import pprint
from xml.etree import cElementTree as ElementTree
from os.path import basename
import json
import glob
import os


class Bin69Validator(QGateBase):
    """Will check B69 using tptorrent logic by calling B69.exe
    B69.exe: I:/engineering/dev/team_classtp/torch/validators/Bin69/Bin69.exe stpl_dir
    """

    def bin69_tool(self):
        """This will return the path for Bin69 tool"""

        b69_tool = 'I:/engineering/dev/team_classtp/torch/validators/Bin69/Bin69.exe'
        return b69_tool

    def return_dutflow(self):
        df = self.tpobj.mtpl.get_dutflow_map()
        return df

    def main(self):
        """Entry point of checker"""

        stpl_dir = self.tpobj.envdir
        b69_tool = self.bin69_tool()
        confirm(b69_tool, f'{b69_tool} does not exist', 'This tool is required')
        log.info('Running B69 Validator')
        cmd = f"{b69_tool} {stpl_dir}"
        code, out = SystemCall(cmd).run_outtxt()
        log.info(f'Exit code: {code}')
        log.info(out)
        moduleName = 'BASE'    # default

        if code == 1:
            df = self.return_dutflow()
            # print(df)
            for item in out.splitlines():
                if 'Bin 69' in item:
                    flowName = item.split('\'')[1].replace('\'', '')
                    for key, value in df.items():
                        if flowName in value:
                            moduleName = key.split('::')[0]
                            log.info(f'{moduleName}:{flowName}')
                    self.add_error(281, f'{moduleName}', f'{item}')
        elif code == 0:
            log.info('No Bin69 FOUND.')
            self.add_pass(281, 'BASE')

        else:
            log.info('There are issues with running B69 Validator. Please check with TPI')
            self.add_error(248, f'BASE', f'There are issues with running B69 Validator. Please check with TPI.')


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    Bin69Validator(TestProgram(sys.argv[1]).init(light=True)).run()
