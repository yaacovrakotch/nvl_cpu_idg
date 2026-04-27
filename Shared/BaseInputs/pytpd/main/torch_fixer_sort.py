#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Various torch fixer routines -sort derivative

Same usage as torch_fixer.py.

Usage:
cd <your_root_path>
torch_fixer.py     # no args means fix .bdef
torch_fixer.py <file.mtpl> ... -link
torch_fixer.py <file.mtpl> ... -counters
torch_fixer.py <file.mtpl> -removeme <composite_name>
torch_fixer.py -lockall <env>
torch_fixer.py <exported_tp_path> -tar /destination/file.tar
torch_fixer.py path1.env path2.env -multibom /destination_path

"""
import setenv      # must be first in the imports
from gadget.tputil import CheckerLog
from gadget.helperclass import OPT
from main.torch_fixer import Fixer


if __name__ == '__main__':  # pragma: no cover
    CheckerLog.setup()
    obj = Fixer()
    OPT.sort = True
    obj.main()
