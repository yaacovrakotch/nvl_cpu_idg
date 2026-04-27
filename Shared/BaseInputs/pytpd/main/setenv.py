#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Set the python path for pytpd projects. This must be first import
With this import, sourceme is not needed. Just need to call script abs path
"""
# set the path
import sys
from os.path import dirname, realpath

ROOT_ENV = dirname(dirname(realpath(__file__)))

if ROOT_ENV not in sys.path:
    sys.path.insert(0, ROOT_ENV)
