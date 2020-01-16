#!/usr/bin/python

import os
import sys
import time
from datetime import timedelta
from datetime import datetime
import shutil

# User inputs
debug = 1
secsPerDay = 86400
pastSecs = secsPerDay/6   # 4 hours
deltaBetweenFiles = secsPerDay / 24
#lastForecastHour = 6
metarUrl = 'http://weather.rap.ucar.edu/surface'
targetDirBase = '/home/disk/bob/impacts/raw/surface/metars'
products = ['metars_alb','metars_bwi','metars_dtw']
catalogBaseDir = '/home/disk/funnel/impacts-website/archive/ops/sfc_metar'

# get current date and hour
nowTime = time.gmtime()
now = datetime(nowTime.tm_year, nowTime.tm_mon, nowTime.tm_mday,
               nowTime.tm_hour, nowTime.tm_min, nowTime.tm_sec)
nowDateStr = now.strftime("%Y%m%d")
nowHourStr = now.strftime("%H")
nowDateHourStr = nowDateStr+nowHourStr
if debug:
    print >>sys.stderr, "nowDateHourStr = ", nowDateHourStr

# compute start time
pastDelta = timedelta(0, pastSecs)
nowDateHour = datetime.strptime(nowDateHourStr,'%Y%m%d%H')
startTime = nowDateHour - pastDelta
startDateHourStr = startTime.strftime("%Y%m%d%H")
startDateStr = startTime.strftime("%Y%m%d")
if debug:
    print >>sys.stderr, "startDateHourStr = ", startDateHourStr

# set up list of date-hour combos to be checked
nFiles = (pastSecs / deltaBetweenFiles)
dateHourStrList = []
for iFile in range(0, nFiles):
    deltaSecs = timedelta(0, iFile * deltaBetweenFiles)
    dayTime = now - deltaSecs
    dateStr = dayTime.strftime("%Y%m%d")
    dateHourStr = dayTime.strftime("%Y%m%d%H")
    dateHourStrList.append(dateHourStr)
if debug:
    print >>sys.stderr, "dateHourStrList = ", dateHourStrList

# get list of files meeting criteria from url
urlFileList = []
for t in range(0,nFiles):
    currentFileTime = dateHourStrList[t]
    for i in range(0,len(products)):
        # get list of files on server for this time and this product
        nextFile = currentFileTime+'_'+products[i]+'.gif'
        urlFileList.append(nextFile)
if debug:
    print >>sys.stderr, "urlFileList = ", urlFileList

# if files in urlFileList not in localFileList, download them
if len(urlFileList) == 0:
    if debug:
        print >>sys.stderr, "WARNING: no data on server"
else:
    # make sure targetBaseDir directory exists and cd to it
    if not os.path.exists(targetDirBase):
        os.makedirs(targetDirBase)
    os.chdir(targetDirBase)
    
    # get local file list - i.e. those which have already been downloaded
    localFileList = os.listdir('.')
    if debug:
        print >>sys.stderr, "  localFileList: ", localFileList

    # loop through the url file list, downloading those that have
    # not yet been downloaded
    #if debug:
    #    print >>sys.stderr, "Starting to loop through url file list"
            
    for idx,urlFileName in enumerate(urlFileList,0):
        if debug:
            print >>sys.stderr, "  idx = ", idx
            print >>sys.stderr, "  urlFileName = ", urlFileName

        if urlFileName not in localFileList:
            if debug:
                print >>sys.stderr, urlFileName,"    not in localFileList -- get file"
            try:
                command = 'wget '+metarUrl+'/'+urlFileName
                os.system(command)
            except Exception as e:
                print sys.stderr, "    wget failed, exception: ", e
                continue
                
            # rename file and move to web server
            # first get forecast_hour
            (base,ext) = os.path.splitext(urlFileName)
            (dateTime,junk,location) = base.split('_')
            if location == 'alb':
                region = 'northeast'
            elif location == 'bwi':
                region = 'mid_atlantic'
            else:
                region = 'mid_west'
            newFileName = 'ops.sfc_metar.'+dateTime+'00.'+region+'.gif'
            if debug:
                print >>sys.stderr, "    newFileName = ", newFileName

            # check to make sure that web server path exists
            catalogDir = catalogBaseDir+'/'+dateTime[0:8]
            if not os.path.exists(catalogDir):
                os.makedirs(catalogDir)

            # copy file to web server
            shutil.copy(targetDirBase+'/'+urlFileName,catalogDir+'/'+newFileName)






    

                              
