#!/usr/bin/python3

import os
import sys
import time
from datetime import timedelta
from datetime import datetime
import shutil

secsPerDay = 86400
pastSecs = secsPerDay * 2
baseDir = '/home/disk/bob/impacts/radar'
baseDirNexrad = baseDir+'/nexrad'
radar = ['kaspr']
nexrad = ['AKQ','BGM','BOX','CCX','CLE','DIX','DOX','DTX','DVN','ENX',
          'GRB','GRR','GYX','ILN','ILX','IND','IWX','LOT','LWX','MHX',
          'MKX','OKX','RAX','TYX','VWX']
nexradProd = ['N0R','N0V']
dir_prefix = 'imageset'

# Get current time
nowTime = time.gmtime()
now = datetime(nowTime.tm_year, nowTime.tm_mon, nowTime.tm_mday,
               nowTime.tm_hour, nowTime.tm_min, nowTime.tm_sec)
nowDateHourStr = now.strftime("%Y%m%d%H")
nowUnixTime = int(now.strftime("%s"))

# Compute oldest time to keep
pastDelta = timedelta(0, pastSecs)
lastGoodTimeObj = now - pastDelta
lastGoodTimeStr = lastGoodTimeObj.strftime("%Y%m%d%H")
lastGoodUnixTime = int(lastGoodTimeObj.strftime("%s"))
print 'lastGoodTime = ',lastGoodTimeStr

# For each radar, remove runs older than 2 days
for iradar in range(0,len(radar)):
    radarBaseDir = baseDir+'/'+radar[iradar]
    for dir in os.listdir(radarBaseDir):
        dirUnixTime = int(dir.replace(dir_prefix,''))
        if dirUnixTime < lastGoodUnixTime:
            shutil.rmtree(radarBaseDir+'/'+dir)
            
# For each nexrad radar, remove images older than 2 days
for inexrad in range(0,len(nexrad)):
    for iprod in range(0,len(nexradProd)):
        localDir = baseDirNexrad+'/'+nexrad[inexrad]+'/'+nexradProd[iprod]
        for file in os.listdir(localDir):
            (fileTimeStr,ext) = os.path.splitext(file)
            fileTimeObj = datetime.strptime(fileTimeStr,'%Y%m%d%H%M')
            fileTimeUnix = int(fileTimeObj.strftime("%s"))
            if fileTimeUnix < lastGoodUnixTime:
                os.remove(localDir+'/'+file)
                #print 'removed ',file
            
        




#dirObjTime = datetime.fromtimestamp(dirUnixTime)
