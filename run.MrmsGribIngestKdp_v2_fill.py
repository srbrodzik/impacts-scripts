#!/usr/bin/python3

import os
import datetime
from datetime import date
from datetime import timezone
import glob

baseDir = '/home/disk/data/nexrad/mrms/Kdp'
filePrefix = 'MRMS_EXP_MergedKdp'
extension = 'grib2'
topLevel = '19.00'
paramDir = '/home/disk/bob/impacts/git/lrose-impacts/projDir/ingest/params'

#dt = datetime.datetime.now(timezone.utc)
#date = dt.strftime("%Y%m%d")
#hour = dt.strftime("%H")
#minute = dt.strftime("%M")
dateList = {'20230111':{'stime':'101038','etime':'163532'}}

for date in dateList.keys() :
    dateDir = baseDir+'/'+date
    s_datetime = date+dateList[date]['stime']
    e_datetime = date+dateList[date]['etime']

    files_topLevel = sorted(glob.glob(dateDir+'/'+filePrefix+'_'+topLevel+'_*'+extension))
    for idx,fileFull in enumerate(files_topLevel,0):
        file = os.path.basename(fileFull)
        (base,ext) = os.path.splitext(file)
        (junk,junk,junk,dateTimeStr) = base.split('_')
        (fdate,ftime) = dateTimeStr.split('-')
        fdatetime = fdate+ftime
        if fdatetime > s_datetime and fdatetime < e_datetime:
    
            files_current = sorted(glob.glob(dateDir+'/'+filePrefix+'_*_'+dateTimeStr+ext))

            if len(files_current) == 33:
                command = 'MrmsGribIngest -v -params '+paramDir+'/MrmsGribIngest.kdp_archive -f '+dateDir+'/*'+dateTimeStr+ext
                os.system(command)
