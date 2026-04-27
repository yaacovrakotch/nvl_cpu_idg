#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
This script will run aries validator and save the log for grepping.

TODO: need add check logic so below string will exit(1) if string does not exist.
INFO: Result summary is:NV348149MV_6248_CHK_1_20231130232601_CLASSHOT_20240126184304026.ITF PASSED ARIES iTUFF Validator and Loaded SUCCESSFULLY to ARIES database.
      ^^^^^^^^^^^^^^^^^                                                                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
"""
import setenv      # must be first in the imports
from gadget.shell import SystemCall
from gadget.tputil import CheckerLog
from gadget.gizmo import Elapsed
from gadget.pylog import log
import os
import sys


# Below is a simple way to inform user if they are python version <3.5. This is checked before any other code during the Parsing phase.
f'If you see SyntaxError, this means your python version is old. Pls upgrade to python3.8 minimum: http://python.org/downloads'


def main(exe='I:/tpvalidation/engtools/tptools/mtl/tools/Auto-ARIESValidator/Auto-ARIESValidator.exe'):
    sw = Elapsed()
    cwd = os.getcwd()
    target = f'{cwd}/bot.itf'
    if not os.path.exists(target):
        print(f'-w- Not exist: {target}')
        return 0     # considered pass if bot.itf does not exist

    extra = ' '.join(sys.argv[1:])      # arguments provided in commmand line
    cmd = f'{exe} --ituff {target} --email junk.junk@intel.com {extra}'.rstrip()
    code = SystemCall(cmd, disp=True).run(disp=True)
    log.info(f'Elapsed: {sw}')
    log.info(f'ARIES_ITUFF result: {code}')
    exit(code)


if __name__ == '__main__':  # pragma: no cover
    CheckerLog.setup()
    main()
