#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Set the python path for pytpd projects for unittests.
This must be first import ON UNITTEST directory.
"""
# set the path
import sys
from os.path import dirname, realpath, join, exists

ROOT_ENV = dirname(dirname(dirname(__file__)))

if join(ROOT_ENV, 'main') not in sys.path:
    sys.path.insert(0, join(ROOT_ENV, 'main'))    # so that setenv import will not fail
    sys.path.insert(0, ROOT_ENV)

# unittest path
from mod.setting import cfg
UT_DIR = cfg.ut_dir
UT_DIR_REPO = f"{ROOT_ENV}/../pytpd-unittest"
EXIST_PDX_I_DRIVE = exists(UT_DIR)

# display friendly error message
urlut = 'https://github.com/intel-innersource/applications.manufacturing.ate-test.tp-tools.pytpd-unittest'
assert exists(UT_DIR_REPO), (f'Read below!\n'
                             f'   Directory [{UT_DIR_REPO}] does not exist.\n'
                             f'   Pls create this directory and do [git clone {urlut} .] on it.')
