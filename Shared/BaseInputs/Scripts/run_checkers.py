#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Run checkers from common

Usage:
run_checkers.py
"""
import sys
try:
    import setenv      # must be first in imports
except ImportError:    # pragma: no cover    - Used when local qgate .py is in tp area
    sys.path.append('Shared/BaseInputs/pytpd')     # This works, as long as script is called from TP root area
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')

from main.build_common import BuildCommon
from gadget.shell import SystemCall
from gadget.getgit import GitHub
from gadget.disk import Chdir
from main.qgate import QGateExecute
from tp.testprogram import TestProgram
import os

# Below is a simple way to inform user if they are using old python version
f'If you see SyntaxError, this means your python version is old. Pls upgrade to python3.8 minimum: https://wiki.ith.intel.com/display/ITSpdxtp/python+download'


def main():
    # read labels before anything else
    GitHub.get_labels()

    # Step1 - build the tp
    # TODO: change this to full tp later
    tp = BuildCommon().main('nvl.cpu', 'main', 'None')

    # Step2 - run qgate
    with Chdir(tp):
        tpobjfull = TestProgram('POR_TP/Class_NVL_S28C/EnvironmentFile.env', allpats=True).init(light=False)
        QGateExecute(tpobjfull).main()


if __name__ == '__main__':  # pragma: no cover
    main()
