import os
import sys
import time
from datetime import timedelta
from datetime import datetime
import shutil

secsPerDay = 86400
pastSecs = secsPerDay * 2
baseDir = '/home/disk/bob/impacts/radar'
radar = ['kaspr']
dir_prefix = 'imageset'

# Get current time
nowTime = time.gmtime()
now = datetime(nowTime.tm_year, nowTime.tm_mon, nowTime.tm_mday,
               nowTime.tm_hour, nowTime.tm_min, nowTime.tm_sec)
nowDateHourStr = now.strftime("%Y%m%d%H")
nowUnixTime = int(now.strftime("%s"))

# Compute oldest time to keep
pastDelta = timedelta(0, pastSecs)
lastGoodTime = now - pastDelta
lastGoodTimeStr = lastGoodTime.strftime("%Y%m%d%H")
lastGoodUnixTime = int(lastGoodTime.strftime("%s"))

# For each model, removed runs older than 2 days old
for iradar in range(0,len(radar)):
    radarBaseDir = baseDir+'/'+radar[iradar]
    for dir in os.listdir(radarBaseDir):
        dirUnixTime = int(dir.replace(dir_prefix,''))
        if dirUnixTime < lastGoodUnixTime:
            shutil.rmtree(radarBaseDir+'/'+dir)
            

#dirObjTime = datetime.fromtimestamp(dirUnixTime)
