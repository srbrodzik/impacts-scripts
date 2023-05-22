#!/usr/bin/python3

# NOTE: expects gunzipped grib2 files like this:
# MRMS_MergedRhoHV_19.00_20230111-150540.grib2

import os
import datetime
from datetime import date
from datetime import timezone
import glob

baseDir = '/home/disk/bob/impacts/raw/mrms/fillGaps/3DRhoHV'
filePrefix = 'MRMS_MergedRhoHV'
extension = 'grib2'
topLevel = '19.00'
paramDir = '/home/disk/bob/impacts/git/lrose-impacts/projDir/ingest/params'

#dt = datetime.datetime.now(timezone.utc)
#date = dt.strftime("%Y%m%d")
#hour = dt.strftime("%H")
#minute = dt.strftime("%M")
dateList = {'20230111':{'stime':'101038','etime':'163533'}}

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
                command = 'MrmsGribIngest -v -params '+paramDir+'/MrmsGribIngest.rhohv_fill -f '+dateDir+'/*'+dateTimeStr+ext
                os.system(command)
