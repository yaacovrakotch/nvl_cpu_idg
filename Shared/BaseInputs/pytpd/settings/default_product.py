#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
This file identifies the configuration file to use
Strategy is:
1. master will have default_product upon discretion of pytpd developers
2. products, which is in a branch, can have different DEFAULT_PRODUCT value
3. products in branch just get latest code via [git merge origin/master]
4. master can have many product configuration files
"""

DEFAULT_PRODUCT = "tgl.py"   # this file must be in settings/ directory
