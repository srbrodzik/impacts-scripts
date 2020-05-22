#!/usr/bin/python

import os
import sys
import time
from datetime import timedelta
from datetime import datetime
import shutil

# Read input args
numargs = len(sys.argv) - 1
if numargs != 1:
    print("Usage: %s [sector(1 or 2)]" % (sys.argv[0]))
    exit()
sector = sys.argv[1]

# User inputs
debug = 1
secsPerDay = 86400
pastSecs = secsPerDay*4
#pastSecs = secsPerDay/12   # check data from last 2 hours
#pastSecs = 300   # check data from last 5 minutes
basePath = '/home/disk/data/images/sat_east_meso_impacts'
targetDirBase = '/home/disk/bob/impacts/sat'
catalogBaseDir = '/home/disk/funnel/impacts/archive/ops/goes_east'
ext = 'jpg'
catalog_prefix = 'ops.goes_east'
product = 'M'+sector+'color'
catalog_suffix = product

# getdate and time - are now and nowObj the same thing??
nowTime = time.gmtime()
nowObj = datetime(nowTime.tm_year, nowTime.tm_mon, nowTime.tm_mday,
               nowTime.tm_hour, nowTime.tm_min, nowTime.tm_sec)
nowUnixTime = int(nowObj.strftime("%s"))
nowStr = nowObj.strftime("%Y%m%d%H%M%S")
nowDateStr = nowObj.strftime("%Y%m%d")
if debug:
    print >>sys.stderr, "nowStr = ", nowStr

# compute start time
pastDelta = timedelta(0, pastSecs)
startObj = nowObj - pastDelta
startUnixTime = int(startObj.strftime("%s"))
startStr = startObj.strftime("%Y%m%d%H%M%S")
startDateStr = startObj.strftime("%Y%m%d")
if debug:
    print >>sys.stderr, "startStr = ", startStr

print >>sys.stderr, "product = ", product
    
# get list of files from last 5 minutes
for file in os.listdir(basePath):
    if debug:
        print >>sys.stderr, 'file = ', file
    if file.endswith(product+'.'+ext):
        #(base,ext) = os.path.splitext(file)
        (fileTimeStr,junk,ext) = file.split('.')
        fileObjTime = datetime.strptime(fileTimeStr, '%Y%m%d%H%M')
        fileDateStr = fileObjTime.strftime("%Y%m%d")
        fileUnixTime =  int(fileObjTime.strftime("%s"))
        if fileUnixTime <= nowUnixTime and fileUnixTime >= startUnixTime:
        
            # create and cd to target dir
            targetDir = targetDirBase+'/'+product
            if not os.path.exists(targetDir):
                os.makedirs(targetDir)
            os.chdir(targetDir)

            # get list of files in targetDir
            targetFileList = os.listdir(targetDir)

            # if file not in targetFileList copy it over
            if not file in targetFileList:
                shutil.copy(basePath+'/'+file,targetDir)
                    
                # copy file to catalog location
                catalog_name = catalog_prefix+'.'+fileTimeStr+'.'+catalog_suffix+'.'+ext
                if not os.path.exists(catalogBaseDir+'/'+fileDateStr):
                    os.mkdir(catalogBaseDir+'/'+fileDateStr)
                shutil.copy(targetDir+'/'+file,catalogBaseDir+'/'+fileDateStr+'/'+catalog_name)
                if debug:
                    print >>sys.stderr, "Copied ", file, " to ", catalog_name
            
