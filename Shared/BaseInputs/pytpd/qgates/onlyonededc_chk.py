#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Purpose of QGATE Check:
Ensures that TMM DedcRVCallbackTC appears exactly once within the whole TP
"""

import sys
import re
import setenv

from gadget.pylog import log
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
from os.path import basename


class OnlyOneDEDC(QGateBase):

    def main(self):
        hits = []
        for module, _, data, _ in self.tpobj.mtpl.iter_tests():
            if data['TEMPLATE'] == 'DedcRVCallbackTC':
                hits.append(module)

        if len(hits) == 0:
            self.add_pass(254, 'base')
            log.info('No valid DEDC infra found in current TP. The feature needs to enabled.')
        elif len(hits) == 1 and hits[0].startswith('TPI'):
            self.add_pass(254, 'base')
            log.info('DEDC is enabled in TPI module successfully!')
        else:
            self.add_error(
                254, 'base', f'Found {len(hits)} occurrences of "DedcRVCallbackTC", '
                             f'expect only one and exists in TPI module only. '
                             f'Remove this TMM in your module if you see this error.'
            )


if __name__ == '__main__':
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    OnlyOneDEDC(TestProgram(sys.argv[1]).pickle_init()).run()
