#!/usr/bin/python3

import os
import shutil
from datetime import datetime
from datetime import timedelta
import datetime as dt
import pytz

#indir = '/home/disk/bob/impacts/radar/er2/20220108/CRS'
indir = '/home/disk/bob/impacts/er2/quicklooks/20220119_quicklooks/CRS'

os.chdir(indir)

for file in os.listdir(indir):
    print(file)
    (base,ext) = os.path.splitext(file)
    (category,platform,dateTimeStr,product) = base.split('.')
    dateTimeObj = datetime.strptime(dateTimeStr,"%Y%m%d%H%M")
    dateTimeObjUTC = dateTimeObj+timedelta(hours=5)
    dateTimeStrUTC = dateTimeObjUTC.strftime("%Y%m%d%H%M")
    fileUTC = category+'.'+platform+'.'+dateTimeStrUTC+'.'+product+ext
    shutil.move(file,fileUTC)
