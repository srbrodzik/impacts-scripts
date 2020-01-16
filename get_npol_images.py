import os
import sys
import time
from datetime import timedelta
from datetime import datetime
import shutil

# User inputs
debug = 1
secsPerDay = 86400
pastSecs = secsPerDay/12
wolffBaseDir = '/home/disk/meso-home/wolff/NPOL_Plots'
#PPI filename format: npol1_<year>_<monthday>_<time>_PPI_<field>.png
#RHI filename format: npol1_<year>_<monthday>_<time>_RHI_01_<field>.png
fields = {'DR':'zdr','DZ':'dbz','FH':'hid','RH':'rhohv','RP':'rainr','VR':'vel'}
file_ext = 'png'
catalogBaseDir = '/home/disk/funnel/impacts-website/archive/research/npol'
catalogFilePrefix = 'research.npol'

# get current time
nowTime = time.gmtime()
now = datetime(nowTime.tm_year, nowTime.tm_mon, nowTime.tm_mday,
               nowTime.tm_hour, nowTime.tm_min, nowTime.tm_sec)
#now = datetime.strptime('202001141300','%Y%m%d%H%M')
nowDateStr = now.strftime("%Y%m%d")
nowTimeStr = now.strftime("%H%M%S")

# compute start time
pastDelta = timedelta(0, pastSecs)
startTime = now - pastDelta
startDateStr = startTime.strftime("%Y%m%d")
startTimeStr = startTime.strftime("%H%M%S")
if debug:
    print >>sys.stderr, "startDateStr = ", startDateStr
    print >>sys.stderr, "startTimeStr = ", startTimeStr

# copy files to catalog since startTime

# get dates of interest
dateStrList = []
if nowDateStr == startDateStr:
    dateStrList = [nowDateStr]
else:
    dateStrList = [startDateStr,nowDateStr]
    
for idate in range(0,len(dateStrList)):
    date = dateStrList[idate]
    year = date[0:4]
    monthDay = date[4:]
    wolffDir = wolffBaseDir+'/'+year+'_'+monthDay
    if os.path.exists(wolffDir):
        for file in os.listdir(wolffDir):
            if file.endswith('png'):
                (base,ext) = os.path.splitext(file)
                if 'PPI' in base:
                    (radar,year_file,monthDay_file,time_file,scan,field) = base.split('_')
                elif 'RHI' in base:
                    (radar,year_file,monthDay_file,time_file,scan,junk,field) = base.split('_')
                if field in fields:
                    dateTimeStr_file = year_file+monthDay_file+time_file
                    fileTime = datetime.strptime(dateTimeStr_file,'%Y%m%d%H%M%S')
                    if fileTime > startTime:
                        catalogDir = catalogBaseDir+'/'+year_file+monthDay_file
                        if not os.path.exists(catalogDir):
                            os.makedirs(catalogDir)
                        newFile = catalogFilePrefix+'.'+dateTimeStr_file+'.'+scan.lower()+'_'+fields[field]+ext
                        shutil.copy(wolffDir+'/'+file,catalogDir+'/'+newFile)
                
    
    
