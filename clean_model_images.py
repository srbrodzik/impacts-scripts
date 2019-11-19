import os
import sys
import time
from datetime import timedelta
from datetime import datetime
import shutil

secsPerDay = 86400
pastSecs = secsPerDay * 2
baseDir = '/home/disk/bob/impacts/model'
model = ['gfs_28km','nam_12km','hrrr_03km']

# Get current time
nowTime = time.gmtime()
now = datetime(nowTime.tm_year, nowTime.tm_mon, nowTime.tm_mday,
               nowTime.tm_hour, nowTime.tm_min, nowTime.tm_sec)
nowDateHourStr = now.strftime("%Y%m%d%H")

# Compute oldest time to keep
pastDelta = timedelta(0, pastSecs)
lastGoodTime = now - pastDelta
lastGoodTimeStr = lastGoodTime.strftime("%Y%m%d%H")

# For each model, removed runs older than 2 days old
for imodel in range(0,len(model)):
    modelBaseDir = baseDir+'/'+model[imodel]
    for dir in os.listdir(modelBaseDir):
        if dir < lastGoodTimeStr:
            shutil.rmtree(modelBaseDir+'/'+dir)
            
