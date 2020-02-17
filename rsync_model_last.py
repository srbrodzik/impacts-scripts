#!/usr/bin/python

import os
import sys
from datetime import timedelta, datetime

secsPerDay = 86400
pastSecs = secsPerDay
userAndServer = 'ldm@bob.atmos.washington.edu'
serverBaseDir = '/home/bob/impacts/mdv/wrf'
clientBaseDir = '/media/usb/data/mdv/wrf'
models = ['gfs_12km','gfs_36km']

# get two days out and prior 3 dates
now = datetime.utcnow()
futureDelta =  timedelta(0,pastSecs*2)
startDate = now + futureDelta
dates = []
for idate in range(0,4):
    pastDelta = timedelta(0,pastSecs*idate)
    time = startDate - pastDelta
    date = time.strftime("%Y%m%d")
    dates.append(date)

# rsync 12km and 36km gfs files for dates

for model in models:
    print >>sys.stderr,'model = ',model
    for date in dates:
        print >>sys.stderr, '   date = ',date
        clientDir = clientBaseDir+'/'+model
        print >>sys.stderr, '   clientDir = ',clientDir
        os.chdir(clientDir)
        serverDir = serverBaseDir+'/'+model+'/'+date
        print >>sys.stderr, '   serverDir = ',serverDir
        command = 'rsync -av '+userAndServer+':'+serverDir+' ./'
        print >>sys.stderr, '   command = ',command
        os.system(command)
        
