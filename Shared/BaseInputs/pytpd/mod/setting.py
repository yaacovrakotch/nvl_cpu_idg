#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Reads the settings
"""
from settings.default_product import DEFAULT_PRODUCT
from os.path import dirname, join
from importlib.machinery import SourceFileLoader


# return the configuration dictionary based on default_product
root = dirname(dirname(__file__))
_mod = SourceFileLoader('configfile', join(root, 'settings', DEFAULT_PRODUCT)).load_module()
cfg = _mod.cfg
