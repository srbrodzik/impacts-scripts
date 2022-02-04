#!/usr/bin/python3

import os
import shutil
from datetime import datetime
from datetime import timedelta
import time

test = True
saveDirBase = '/home/disk/bob/impacts/radar/nasa_gail'
tempDir = '/tmp'
# set startFlag
#    0 -> start now
#    1 -> start at startDate
startFlag = 1
startDate = '202201112359'
# set number of days to go back from startDate
num_days = 1
secsPerDay = 86400

urlBase = 'https://trmm-fc.gsfc.nasa.gov/ftp/pub/distro/mrr/mrr2-03/NetCDF'

# Get start date
if startFlag == 0:
    nowTime = time.gmtime()
    now = datetime(nowTime.tm_year, nowTime.tm_mon, nowTime.tm_mday,
                   nowTime.tm_hour, nowTime.tm_min, nowTime.tm_sec)
else:
    nowDateStr = startDate
    now = datetime.strptime(nowDateStr,'%Y%m%d%H%M')

# Get todays date
#now = datetime.utcnow()
nowDateTimeStr = now.strftime("%Y%m%d%H%M")
nowDateStr = now.strftime("%Y%m%d")
nowYearStr = now.strftime("%Y")
nowMonthStr = now.strftime("%m")
nowDayStr = now.strftime("%d")

# Make list of dates to process
dateTimeStrList = []
dateStrList = []
yearStrList = []
monthStrList = []
dayStrList = []
timeStrList = []
for idate in range(0,num_days):
    deltaSecs = timedelta(0, idate * secsPerDay)
    nextDate = now - deltaSecs
    nextDateTimeStr = nextDate.strftime("%Y%m%d%H%M")
    dateTimeStrList.append(nextDateTimeStr)
    nextDateStr = nextDate.strftime("%Y%m%d")
    dateStrList.append(nextDateStr)
    nextYearStr = nextDate.strftime("%Y")
    yearStrList.append(nextYearStr)
    nextMonthStr = nextDate.strftime("%m")
    monthStrList.append(nextMonthStr)
    nextDayStr = nextDate.strftime("%d")
    dayStrList.append(nextDayStr)
    nextTimeStr = nextDate.strftime("%H%M")
    timeStrList.append(nextTimeStr)
print('dateStrList = ',dateStrList)
   
for idx,idate in enumerate(dateStrList,0):

    # Get MRR data
    saveDir = saveDirBase+'/mrr2-03'
    os.chdir(saveDir)
    url = urlBase+'/'+yearStrList[idx]+monthStrList[idx]
    rawFileZip = monthStrList[idx]+dayStrList[idx]+'.ave.nc.zip'
    rawFileNc = monthStrList[idx]+dayStrList[idx]+'.ave.nc'
    daacFile = 'IMPACTS_NASA_mrr_'+dateStrList[idx]+'_'+timeStrList[idx]+'_GAIL_Trailer.nc'
    command = 'wget '+url+'/'+rawFileZip
    os.system(command)
    command = 'unzip '+rawFileZip
    os.system(command)
    os.remove(rawFileZip)
    shutil.move(rawFileNc,daacFile)
    os.system('gzip '+daacFile)
    #ftpFile = open(os.path.join(tempDir,catFile),'rb')
    #catalogFTP.storbinary('STOR '+catFile,ftpFile)
    #ftpFile.close()
    #os.remove(tempDir+'/'+daacFile)

