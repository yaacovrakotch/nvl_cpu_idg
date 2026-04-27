#!/usr/intel/pkgs/python3/3.12.3/bin/python3 -u
"""
Display MBOT job status
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')       # This require python3.7+. This is needed to avoid unicode errors.
print("Content-type: text/html\n\n");

import traceback
import cgi
import sys
import os

# basic html routines ===========================================
def cgiFieldStorageToDict(fieldStorage):
   """ Get a plain dictionary rather than the '.value' system used by the 
   cgi module's native fieldStorage class. """
   params = {}
   for key in fieldStorage.keys(  ):
      params[key] = fieldStorage[key].value
   return params

def get_cookie(key, _allc={}):
    """Read all cookies from the browser"""
    if _allc:
        return _allc.get(key,"")     # return empty if key is not found
    
    # get the cookie
    if 'HTTP_COOKIE' in os.environ:
        for item in os.environ['HTTP_COOKIE'].split(';'):
            if '=' in item:
                result = item.strip().split('=',2)
                if len(result)==2:
                    _allc[result[0]]=result[1]
    else:
        _allc['NONE']=None
        
    return _allc.get(key, "")     # return empty if key is not found

def log_usage(outfile):
    """Log the Usage"""
    from datetime import datetime
    user = get_cookie('IDSID')
    sw = Elapsed(importtime=True)
    txt = '%s: %s %s\n' % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), sw(), user)
    fh = open(outfile, 'a')
    fh.write(txt)
    fh.close()

OPT = cgiFieldStorageToDict(cgi.FieldStorage())

# web specific setup
os.environ["https_proxy"] = 'http://proxy-dmz.intel.com:912'
if 'HOME' not in os.environ or 'USER' not in os.environ:
    os.environ['USER'] = 'p6vector'
    os.environ['LOGNAME'] = 'p6vector'
    os.environ['HOME'] = '/nfs/site/home/p6vector'
    os.environ['WEBPYTPD'] = 'True'    # Indicator that this is web run
    os.environ['SSL_CERT_FILE']='/var/lib/ca-certificates/ca-bundle.pem'

# needed for datahost to work
os.environ['NO_PROXY'] = 'localhost,127.0.0.0/8,172.16.0.0/20,192.168.0.0/16,10.0.0.0/8,intel.com'   

# check permissions
import subprocess
user = get_cookie('IDSID')
OPT['_user'] = user
if not user:
    import setenv                  # must be first in the imports for pytpd
    from gadget.strmore import day_code
    if OPT.get('code') == day_code():    # for api use
        user = 'jqdelosr'
    else:
        print(f'Cannot identify username. Pls enable cookies and visit circuit first.')
        exit(0)
fh = subprocess.Popen(['groups', user], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out, err = fh.communicate()
expect = out.decode(errors='ignore').split()
if 'gdlusers' not in expect:
    print(f'user: [{user}] does not have permissions to access this website.')
    exit(0)

# END basic html routines ==================

# commandline run / debug
if len(sys.argv) == 2:
    OPT = {'br': sys.argv[1]}

# run it
try:
    import setenv                  # must be first in the imports for pytpd
    from mod.mbot_dashboard import MBotDB, TesterStatusDB
    from gadget.gizmo import Elapsed
    if OPT.get('tester') == 'True':    
        TesterStatusDB.OPT = OPT
        TesterStatusDB().main()
    else:
        MBotDB.OPT = OPT
        MBotDB().main()
except Exception as e:
    print('<pre>')
    print("Exception:<br>")
    print(traceback.format_exc())
    print('</pre>')

# log usage ==========================
log_usage('/nfs/pdx/disks/tvpvweb/cgi-bin/bots-dashboard/usage.log')
