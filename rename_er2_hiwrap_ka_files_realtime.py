#!/usr/bin/python3

import os
import sys
import shutil
from datetime import datetime
from datetime import timedelta
import datetime as dt
import pytz

if len(sys.argv) != 2:
    #print('Usage: sys.argv[0] [YYYYMMDD]')
    print('Usage: {} [YYYYMMDD]'.format(sys.argv[0]))
    sys.exit()
else:
    date = sys.argv[1]

indir = '/home/disk/bob/impacts/radar/er2/postFlight/realtime/HIWRAP_KA'+'/'+date
prefix = 'aircraft.NASA_ER2'
suffix = 'HIWRAP_Ka_dBZ_vel'
convertEasternToUTC = True

os.chdir(indir)

for file in os.listdir(indir):
    print(file)
    (base,ext) = os.path.splitext(file)
    (radar,band,RT,dateTime) = base.split('_')
    dateTimeStr = dateTime[:-2]
    if convertEasternToUTC:
        dateTimeObj = datetime.strptime(dateTimeStr,"%Y%m%d%H%M")
        dateTimeObjUTC = dateTimeObj+timedelta(hours=5)
        dateTimeStrUTC = dateTimeObjUTC.strftime("%Y%m%d%H%M")
    else:
        dateTimeStrUTC = datetimeStr
        
    catName = prefix+'.'+dateTimeStrUTC+'.'+suffix+ext
    shutil.move(file,catName)
    
    
