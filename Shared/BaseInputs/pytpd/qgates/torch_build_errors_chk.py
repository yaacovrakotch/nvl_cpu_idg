#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Checks and gates for Torch Build errors
"""
import setenv  # must be first in the imports
from gadget.dictmore import xmlfunc, iter_dot_items, find_dot_items
from gadget.pylog import log
from gadget.tputil import remove_ip
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
from main.torch_mv import DoMV
from gadget.files import File
from gadget.tputil import get_modulename
from gadget.tputil import OtplFile
from collections import defaultdict
from pprint import pprint
import sys
import os


class TorchBuildErrors(QGateBase):

    def check_TP0346(self, file, lno, instlist, msg):
        """
        TP0346 for VMinTC only. Ignore if not.
        """
        filex = file.split('/')[-2:]
        file2 = f'{self.tpobj.tpldir}/Modules/{filex[0]}/{filex[1]}'
        if not os.path.exists(file2):
            return f'[{file2}] is not found. Build error: {msg}'

        line_num = int(lno.split(',')[0])

        # read file and cache it
        if file2 not in self.cache_file:
            self.cache_file[file2] = {}
            for lno2, line in OtplFile(file2).readline():
                self.cache_file[file2][lno2] = line

        # is line number existing?
        if line_num not in self.cache_file[file2]:
            return f'line#{line_num} of {file2} is not FOUND: {msg}'
        line = self.cache_file[file2][line_num]

        # Is it DUTFlow item?
        if not ('DUTFlowItem' in line):
            return f'line#{line_num} of {file2} is not DUTFlowItem: {msg}'
        instance = line.split(' ')[2]

        # Is it vminTC?
        if instance in instlist:
            return (f'Please fix: Missing required port build error on "{instance}" '
                    f'at line number "{lno}" with error: "{msg}"')

        log.info(f'-i- Ignoring TP0346 error since it is not a VminTC template: {instance}')
        return   # Do not error

    def main(self):
        """Main Entry point"""
        self.cache_file = {}   # {file: <list>}

        error_file = f'{self.tpobj.envdir}/Reports/build_errors.txt'

        if not os.path.exists(error_file):
            # This is valid on tpbot - build is not executed. Only on checkers or tpbuild where it is checked.
            log.info(f'-w- TorchBuildErrors is skipped: {error_file} is not found.')
            return

        # Get all VminTC instances
        instlist = set()
        for mod, test, data, _ in self.tpobj.mtpl.iter_flows('MAIN', bypass=True, edict=True, pdict=True):
            if data['TEMPLATE'].startswith('VminTC'):
                instlist.add(test)

        edata, wdata, udata = DoMV.build_process_txt(File(f'{error_file}').read())
        print(f'error lines:   {len(edata)}')
        print(f'warning lines: {len(wdata)}')
        print(f'unknown lines: {len(udata)}')

        module_list = set()         # set of failing modules
        for i in range(len(edata)):
            file = edata[i]['file']
            filesplt = file.split('/')[-1]
            module = edata[i]['module']
            module_list.add(module)
            lno = edata[i]['lno']
            msg = edata[i]['msg']
            code = edata[i]['code']

            # improve the message (add the instance name)
            if code == 'TP0346':
                newmsg = self.check_TP0346(file, lno, instlist, msg)
                if newmsg:
                    msg = newmsg
                else:
                    log.info(f'-i- Ignoring TP0346 error since it is not a VminTC template: {msg}')
                    continue     # Do not error

            # error out
            self.add_error(250, module, f'Please fix: Torch build error on "{filesplt}" at line number: '
                                        f'"{lno}" with error: "{msg}"')

        # get all modules for pass report
        allmodule_list = set()
        for mtpl in self.tpobj.get_all_mtpl_from_stpl():
            allmodule = get_modulename(mtpl)
            allmodule_list.add(allmodule)

        for module in allmodule_list:
            if module and module not in module_list:
                self.add_pass(250, module)


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    TorchBuildErrors(TestProgram(sys.argv[1]).pickle_init()).run()
