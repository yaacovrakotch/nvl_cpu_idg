#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
import setenv      # must be first in the imports
import sys
import os
import shutil
import glob
from mod.setting import cfg


def main():  # pragma: no cover
    # Enforce TRACE TRC launch here
    consoletrc = cfg.consoletrc
    if os.path.isfile(consoletrc):
        print('============================================')
        print('-i- Calling auto-TRACE_TRC...')

        # check first if csv is safe to rewrite by checking excel
        try:
            trcs = glob.glob('trc_report*.csv')
            for t in trcs:
                file = open(t, 'w')
                file.close()
        except:
            raise IOError('-ERROR- trc_report*.csv is open in Excel, pls close it and then rerun cmd.')
        os.system('%s -dir .' % consoletrc)			
        print('-i- Done running auto-TRACE_TRC!')
        print('============================================')

    else:
        raise ValueError('-ERROR- Unable to launch automated TRACE TRC=%s...Check if your I: drive is mapped!' % consoletrc)

if __name__ == '__main__':  # pragma: no cover
    main()