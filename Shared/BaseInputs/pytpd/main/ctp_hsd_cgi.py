#!/p/pde/tvpv/flash_tools/sw_tools/anaconda3.8/bin/python
"""
Main cgi call
"""
import setenv       # must be first in the imports
import urllib3
import cgi
from gadget.gizmo import Elapsed
print("Content-type: application/json\n")
urllib3.disable_warnings()


# basic html routines ===========================================
def cgiFieldStorageToDict(fieldStorage):
    """
    Get a plain dictionary rather than the '.value' system used by the
    cgi module's native fieldStorage class.
    """
    params = {}
    for key in fieldStorage.keys():
        params[key] = fieldStorage[key].value
    return params

def log_usage(outdir):
    """Log the Usage, log past 60 mins only, used for high frequency api calls"""
    import time
    import os
    if not os.path.isdir(outdir):
        return

    sw = Elapsed(importtime=True)
    secs = sw().replace(' ', '_')
    fname = (f"{int(time.time())}_{str(os.getpid()).zfill(6)}_{OPT.get('speedid', '00000000')}_"
             f"{OPT.get('ww', 'XXXXXXXXXXX')}_{secs}_{OPT.get('toc')}")
    with open(f'{outdir}/{fname}', 'w') as fh:
        pass   # touch file only

    # delete old
    for ff in os.listdir(outdir):
        elems = ff.split('_')
        if elems[0].startswith('Seconds'):
            continue   # ignore header
        if (time.time() - int(elems[0])) > 3600:
            try:
                os.unlink(f'{outdir}/{ff}')
            except Exception:
                pass    # quiet

def main():
    jsonroot = '/intel/tpvalidation/engtools/tptools/mtl/plan_waivers/jsonall'

    if 'real' in OPT:
        return True     # proceed traditionally

    elif OPT.get('toc') == 'all':   # TOP level TOC
        with open(f'{jsonroot}/toc_all.json') as fh:
            print(fh.read())

    elif OPT.get('toc') == 'map':   # Show the ProductConfig given speedid
        sid = OPT.get('speedid')
        with open(f'{jsonroot}/{sid}/map.json') as fh:
            print(fh.read())

    elif OPT.get('toc') == 'ww':    # Show all ww+TPName given speedid
        sid = OPT.get('speedid')
        soc = OPT.get('socket')
        with open(f'{jsonroot}/{sid}/{soc}.wwtoc.json') as fh:
            print(fh.read())

    elif 'ww' in OPT:               # Show summary given ww+speedid
        sid = OPT.get('speedid')
        soc = OPT.get('socket')
        ww = OPT.get('ww')
        with open(f'{jsonroot}/{sid}/{ww}.{soc}.data.json') as fh:
            print(fh.read())

    else:
        return True

    return False


OPT = cgiFieldStorageToDict(cgi.FieldStorage())
# ===============================================================

# =================== run
try:
    ret = main()
    if ret:
        from mod.db_ctp import MainCgi
        MainCgi(OPT)
except Exception as e:
    if 'debug' in OPT:
        import traceback
        print("Exception:")
        print(traceback.format_exc())
    else:
        import json
        print(json.dumps([{'error': str(e),
                           'suggestion': 'Add &debug=True to show traceback'}], indent=3))

# log usage ==========================
log_usage('/nfs/pdx/disks/tvpvweb/cgi-bin/ctp2/usage.dir')

