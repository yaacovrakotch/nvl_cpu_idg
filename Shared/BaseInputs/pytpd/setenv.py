#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Set the python path for pytpd projects. This must be first import
With this import, sourceme is not needed. Just need to call script abs path
"""
# set the path
import sys
from os.path import dirname, realpath, basename

ROOT_ENV = dirname(dirname(realpath(sys.argv[0])))

# check if executed from unittest
if basename(ROOT_ENV) == 'gadget':
    ROOT_ENV = dirname(ROOT_ENV)

if ROOT_ENV not in sys.path:
    sys.path.insert(0, ROOT_ENV)
