#!/usr/bin/python3

import os
import datetime
from datetime import date
from datetime import timezone
import glob

baseDir = '/home/disk/data/nexrad/mrms/3DRefl'
filePrefix = 'MRMS_MergedReflectivityQC'
extension = 'grib2'

dt = datetime.datetime.now(timezone.utc)
date = dt.strftime("%Y%m%d")
hour = dt.strftime("%H")
minute = dt.strftime("%M")

if minute.startswith('0'):
    lastvolumeminute = '58'
    lastHour = str(int(hour)-1)
    if len(lastHour) == 1:
        hour = '0'+lastHour
    else:
        hour = lastHour
elif minute.startswith('1'):
    lastvolumeminute = '08'
elif minute.startswith('2'):
    lastvolumeminute = '18'
elif minute.startswith('3'):
    lastvolumeminute = '28'
elif minute.startswith('4'):
    lastvolumeminute = '38'
elif minute.startswith('5'):
    lastvolumeminute = '48'

files = sorted(glob.glob(baseDir+'/'+date+'/'+filePrefix+'_*_'+date+'-'+hour+lastvolumeminute+'*.'+extension))
print(files)
if len(files) == 33:
    fileBase = os.path.basename(files[-1])
    (base,ext) = os.path.splitext(fileBase)
    (category,product,level,fileDateTime) = base.split('_')
    command = 'MrmsGribIngest -v -params MrmsGribIngest.refl_archive -f '+baseDir+'/'+date+'/*'+fileDateTime+'*.grib2'
    os.system(command)
