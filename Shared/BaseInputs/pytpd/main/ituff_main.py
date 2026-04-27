#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
This script is purely for testing ituffread.py
"""
import setenv      # must be first in the imports
from gadget.gizmo import Elapsed, count_iter
from gadget.dictmore import keys_atlevel
from gadget.files import File
from pprint import pprint
# import pyximport
# pyximport.install(inplace=True, language_level=3)
import sys
#from mod.cyx import Cclass, Pclass
#from mod.ituff import Ituff as Ituffx

try:
    from mod.ituffreadx import Ituff
    print("USING CYTHON")
except BaseException:
    from mod.ituffread import Ituff

# ituff location: /intel/hdmxdata/prod

sw = Elapsed()
itf = Ituff()
# itf.foo(); print(sw); exit(0)
#itf = Ituff(multiple=['2_mrslt_'], retname='chuckid')

# single file read
# itf.read('/tmp/try1/J1230270_6261_1A_ALL')
# itf.read('/intel/hdmxdata/prod/NV145093EN_6248/NV145093EN_6248_chk_1_20211102220146_CLASSHOT.itf.gz')
itf.read(sys.argv[1])
# itf.read_lot(sys.argv[1], 'CLASSHOT')

out = itf.data
# pprint(out)
print(f"Proto1c: {sw}, len={len(out)} items={count_iter(keys_atlevel(out, 1))}")
exit(0)
