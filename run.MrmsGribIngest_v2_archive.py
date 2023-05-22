#!/usr/bin/python3

import os
import sys
import datetime
from datetime import date
from datetime import timezone
from datetime import datetime
from datetime import timedelta
import glob

if len(sys.argv) != 3:
    print('Usage: {} [startTime(YYYYMMDDHH)] [endTime(YYYYMMDDHH)]'.format(sys.argv[0]))
    sys.exit()
else:
    startTime = sys.argv[1]
    endTime = sys.argv[2]

if (len(startTime) != 10) or (len(endTime) != 10):
    print('startTime and endTime must be in YYYYMMDDHH format')
    exit()
    
baseDir = '/home/disk/data/nexrad/mrms/3DRefl'
filePrefix = 'MRMS_MergedReflectivityQC'
extension = 'grib2'
topLevel = '19.00'
paramDir = '/home/disk/bob/impacts/git/lrose-impacts/projDir/ingest/params'
minDelta = 10

startTimeObj = datetime.strptime(startTime,'%Y%m%d%H')
endTimeObj = datetime.strptime(endTime,'%Y%m%d%H')

startTimeNextObj = startTimeObj
print('startTimeNextObj = {}'.format(startTimeNextObj))
print('endTimeObj       = {}'.format(endTimeObj))
while startTimeNextObj < endTimeObj:
    date = startTimeNextObj.strftime('%Y%m%d')
    hour = startTimeNextObj.strftime('%H')
    minute = startTimeNextObj.strftime('%M')
    dateDir = baseDir+'/'+date
    
    files_topLevel = sorted(glob.glob(dateDir+'/'+filePrefix+'_'+topLevel+'_'+date+'-'+hour+'*'+extension))
    for filePath in files_topLevel:
        (path,file) = os.path.split(filePath)
        (base,ext) = os.path.splitext(file)
        (junk,hhmmss) = base.split('-')
        fileMinute = hhmmss[2:4]
        if minute == fileMinute:
            volFiles = sorted(glob.glob(dateDir+'/'+filePrefix+'_*_'+date+'-'+hhmmss+'.'+extension))
            if len(volFiles) == 33:
                command = 'MrmsGribIngest -v -params '+paramDir+'/MrmsGribIngest.refl_real_archive -f '+dateDir+'/*'+date+'-'+hhmmss+ext
                os.system(command)
            continue

    startTimeNextObj = startTimeNextObj + timedelta(minutes=minDelta)
    print('startTimeNextObj = {}'.format(startTimeNextObj))
    print('endTimeObj       = {}'.format(endTimeObj))
