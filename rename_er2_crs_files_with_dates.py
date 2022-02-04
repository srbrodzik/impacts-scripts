#!/usr/bin/python3

import os
import shutil
from datetime import datetime
from datetime import timedelta
import datetime as dt
import pytz

indir = '/home/disk/bob/impacts/radar/er2/postFlight/realtime/CRS/20220129'
prefix = 'aircraft.NASA_ER2'
suffix = 'CRS_dBZ_vel'
convertEasternToUTC = True

os.chdir(indir)

for file in os.listdir(indir):
    print(file)
    (base,ext) = os.path.splitext(file)
    (radar,RT,dateTime) = base.split('_')
    dateTimeStr = dateTime[:-2]
    if convertEasternToUTC:
        dateTimeObj = datetime.strptime(dateTimeStr,"%Y%m%d%H%M")
        dateTimeObjUTC = dateTimeObj+timedelta(hours=5)
        dateTimeStrUTC = dateTimeObjUTC.strftime("%Y%m%d%H%M")
    else:
        dateTimeStrUTC = datetimeStr
        
    catName = prefix+'.'+dateTimeStrUTC+'.'+suffix+ext
    shutil.move(file,catName)
    
    
