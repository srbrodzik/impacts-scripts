#!/usr/bin/python3

import os
import datetime
from datetime import date
from datetime import timezone
import glob

baseDir = '/home/disk/data/nexrad/mrms/3DRefl'
filePrefix = 'MRMS_MergedReflectivityQC'
extension = 'grib2'
topLevel = '10.00'
paramDir = '/home/disk/bob/impacts/git/lrose-impacts/projDir/ingest/params'

dt = datetime.datetime.now(timezone.utc)
date = dt.strftime("%Y%m%d")
hour = dt.strftime("%H")
minute = dt.strftime("%M")
dateDir = baseDir+'/'+date

# get file list of all grib2 files from latest volume
files_topLevel = sorted(glob.glob(dateDir+'/'+filePrefix+'_'+topLevel+'_*'+extension))
file = os.path.basename(files_topLevel[-1])
(base,ext) = os.path.splitext(file)
dateTimeStr = base.replace(filePrefix+'_'+topLevel+'_','')
files_current = sorted(glob.glob(dateDir+'/'+filePrefix+'_*_'+dateTimeStr+ext),reverse=True)

# limit files_current to files at or below topLevel
baseFile = os.path.basename(files_current[0])
(platform,product,level,dtPlus) = baseFile.split('_')
while float(level) > float(topLevel):
    files_current.remove(files_current[0])
    baseFile = os.path.basename(files_current[0])
    (platform,product,level,dtPlus) = baseFile.split('_')
files_current = sorted(files_current)

# convert files_current list to a string
file_list = ''
for file in files_current:
    file_list = file_list+' '+file

# convert grib2 files to mdv file
command = 'MrmsGribIngest -v -params '+paramDir+'/MrmsGribIngest.refl -f '+file_list
print(command)
os.system(command)
