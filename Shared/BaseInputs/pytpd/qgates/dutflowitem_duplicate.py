#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Identify duplicate DUTFlowItem names, since infrabll does not like it. Issue on 5/18/23
"""
import sys
import setenv

from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
from gadget.tputil import get_modulename, OtplFile
import re


class DFIDup(QGateBase):

    def main(self):
        """Entry point of checker"""
        for mtpl in self.tpobj.get_all_mtpl_from_stpl():
            self.check(mtpl)

    def check(self, mtpl):
        """Check one file"""
        module = get_modulename(mtpl)
        if not module:    # pragma: no cover
            return

        uniq = set()
        for lno, line in OtplFile(mtpl).readline():
            if line.startswith('DUTFlowItem '):
                name = line.split()[1]
                if name in uniq:
                    self.add_error(222, module, f'DUTFlowItem {name} is duplicated!')   # This is how to specify error
                else:
                    self.add_pass(222, module)         # once
                    uniq.add(name)

        robj = re.compile(r'^\s*#\s*DUTFlowItem\s+(\w+)')
        failed = False
        for lno, line in OtplFile(mtpl).readline(comments=True):
            res = robj.search(line)
            if res:
                self.add_error(223, module, f'Commented DUTFlowItem is not allowed: [{line}]')
                failed = True

        if not failed:
            self.add_pass(223, module)


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    DFIDup(TestProgram(sys.argv[1]).pickle_init()).run()
