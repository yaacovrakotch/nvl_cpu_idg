#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Usage:

upload_ctp.py              # show all ctp records
upload_ctp.py del          # delete all ctp records
upload_ctp.py hsd          # show all hsd records
upload_ctp.py hsddel       # delete all hsd records
upload_ctp.py hsdwrite     # read hsd and upload it
upload_ctp.py cron         # execute the ctp_hsd cron (read CRNT and hsd)
upload_ctp.py <file.csv>   # Upload this ctp .csv
"""
import setenv      # must be first in the imports
from mod.db_ctp import connect, CTP, UploadCtp, Hsd, HsdRead, CtpRepo, Overrides
import sys
import json
import pprint
import time
import os
from gadget.helperclass import OnceADay
from gadget.files import File
from gadget.disk import mkdirs
import glob


if len(sys.argv) == 1:
    # read
    connect()
    data = list(CTP.objects.all())
    for ctr, item in enumerate(data):
        print(f'{ctr}. {item.tpname}, {item.ww}, {item.product}, {item.step}, {item.socket}, '
              f'records={len(item.records)} ')  # , end='')

        # pprint(item)

        # Write to json one row
        if False and ctr == 0:
            row_fields = 'module testinstance flags status ErrorMessage ContentExpect ContentActual ConditionComplete edc PorPlan'.split()
            top_fields = 'tpname product step socket ww'.split()
            tp = {x: getattr(item, x) for x in top_fields}
            result = []
            for rec in item.records:
                result.append({x: getattr(rec, x) for x in row_fields})
            tp['records'] = result
            print("Writing: out.json")
            with open('out.json', 'w') as fh:
                json.dump(tp, fh, indent=3)

elif sys.argv[1] == 'del':
    # delete ctp
    connect()
    data = list(CTP.objects.all())
    for item in data:
        print(f"Deleting {item.ww}")
        item.delete()

elif sys.argv[1] == 'hsd':
    # read hsd
    connect()
    data = list(Hsd.objects.all())
    for ctr, item in enumerate(data):
        print(f'{ctr}. {item.ww} {item.product}, {item.step}, {item.socket}, {len(item.records)}')  # , end='')
        # pprint.pprint(item)

elif sys.argv[1] == 'hsddel':
    # delete hsd
    connect()
    data = list(Hsd.objects.all())
    raise Exception('why? This exist to prevent accidental run. uncomment this line if intentional')
    for item in data:
        print(f"Deleting {item.ww}")
        item.delete()

elif sys.argv[1] == 'hsdwrite':
    # write hsd
    # with open(sys.argv[1]) as fh:
    #     HsdRead.upload_hsd(json.load(fh), speedid)
    connect()
    for speedid in CtpRepo.all_speedid():
        HsdRead(speedid).upload()

elif sys.argv[1] == 'cron':
    istime = OnceADay(23)
    while True:
        try:
            connected = False
            if istime():
                connect()
                Overrides(None).save()
                for speedid in CtpRepo.all_speedid():
                    HsdRead(speedid).upload()

            for dd in glob.glob('/intel/tpvalidation/engtools/tptools/mtl/plan_waivers/outputs_ctp2/1*_*'):
                for ff in os.listdir(dd):
                    if ff == 'done':               # done folder
                        continue
                    if not ff.endswith('.csv'):    # random files
                        continue
                    if not connected:              # connect once
                        connect()
                        connected = True

                    target = f'{dd}/{ff}'
                    print(f"Uploading {target}")
                    UploadCtp(target).main()
                    mkdirs(f'{dd}/done', mode='02775')
                    File(target).move(f'{dd}/done', overwrite_rename=True)
        except Exception as e:
            print(f"Exception: {e}")

        print("Sleeping\r\r\r\r\r\r\r\r", end='')
        time.sleep(5 * 60)

else:
    connect()
    UploadCtp(sys.argv[1]).main()
