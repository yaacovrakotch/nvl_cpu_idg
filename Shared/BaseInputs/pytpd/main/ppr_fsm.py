#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Generate FSM and PPR config files based on mtpl.

# Call this before Torch export:
    ppr_fsm.py PRE POR_TP/Class_MTL_M28/EnvironmentFile.env

# Call this after Torch export:
    ppr_fsm.py POST POR_TP/Class_MTL_M28/EnvironmentFile.env
"""

import setenv      # must be first in the imports
from tp.testprogram import TestProgram
from mod.mtplencode import MtplEncode
import sys


# Below is a simple way to inform user if they are python version <3.5. This is checked before any other code during the Parsing phase.
f'If you see SyntaxError, this means your python version is old. Pls upgrade to python3.8 minimum: http://python.org/downloads'


class PprFsm:

    def main(self):
        # check tool inputs
        if len(sys.argv) != 3:
            print(__doc__)
            return

        assert sys.argv[1] in ('PRE', 'POST'), f'Incorect Usage:\n{__doc__}'

        # Load the testprogram object
        tpobj = TestProgram(sys.argv[2])

        # PRE routine - generate the meta file, call before Torch export.
        if sys.argv[1] == 'PRE':
            MtplEncode(tpobj).generate_meta()

        # POST routine - generate the output files
        if sys.argv[1] == 'POST':
            me = MtplEncode(tpobj).read_meta()
            me.do_fsm()
            me.do_ppr()

        print("Execution Success")


if __name__ == '__main__':  # pragma: no cover
    obj = PprFsm()
    obj.main()
