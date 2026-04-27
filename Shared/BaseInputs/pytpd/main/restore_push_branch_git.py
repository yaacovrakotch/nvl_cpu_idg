#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Simple script to update a file into multiple branches

Usage:
restore_push_branch_git.py TP/<rev_target> <file> --source=TP/ref
"""
import setenv      # must be first in the imports
from tp.testprogram import TestProgram, pprint
import sys
import re
from gadget.files import File
from gadget.disk import Allfiles
from gadget.shell import SystemCall
from os.path import basename, dirname
from gadget.errors import confirm

assert len(sys.argv) == 4, 'Usage Error!\n\nExpecting 3 args:\n %s' %  __doc__

target = sys.argv[1]
ff = sys.argv[2]
src = sys.argv[3]
confirm(src.startswith('--source'), f'incorrect {src}', 'pls fix')

# make sure clean
_, out = SystemCall('git status', disp=True).run_outtxt()
confirm('nothing to commit, working tree clean' in out, 'git status not clean', 'pls fix')

# checkout
print()
code, out = SystemCall(f'git checkout {target}', disp=True).run_outtxt()
confirm(code == 0, 'error', 'pls check')

# pull
print()
code, out = SystemCall(f'git pull', disp=True).run_outtxt()
confirm(code == 0, 'error', 'pls check')

# put the file
print()
code, out = SystemCall(f'git restore {ff} {src}', disp=True).run_outtxt()
confirm(code == 0, 'error', 'pls check')

# add
print()
code, out = SystemCall(f'git add {ff}', disp=True).run_outtxt()
confirm(code == 0, 'error', 'pls check')

# commit
print()
code, out = SystemCall(f'git commit -m updated_{ff}', disp=True).run_outtxt()
confirm(code == 0, 'error', 'pls check')

# push
print()
code, out = SystemCall(f'git push', disp=True).run_outtxt()
confirm(code == 0, 'error', 'pls check')
