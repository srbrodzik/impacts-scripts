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
pastSecs = secsPerDay
deltaBetweenFiles = secsPerDay
snowUrl = 'https://www.nohrsc.noaa.gov/snow_model/images/full/National/ruc_snow_precip_24hr'
targetDirBase = '/home/disk/bob/impacts/raw/surface/snow'
products = ['ruc_snow_precip_24hr']
catalogBaseDir = '/home/disk/funnel/impacts-website/archive/ops/noaa'

# get current date and hour
nowTime = time.gmtime()
now = datetime(nowTime.tm_year, nowTime.tm_mon, nowTime.tm_mday,
               nowTime.tm_hour, nowTime.tm_min, nowTime.tm_sec)
nowYearMonthStr = now.strftime("%Y%m")
nowDateStr = now.strftime("%Y%m%d")
if debug:
    print >>sys.stderr, "nowYearMonthStr = ", nowYearMonthStr
    print >>sys.stderr, "nowDateStr = ", nowDateStr

# compute start time
pastDelta = timedelta(0, pastSecs)
nowDate = datetime.strptime(nowDateStr,'%Y%m%d')
startTime = nowDate - pastDelta
startYearMonthStr = startTime.strftime("%Y%m")
startDateStr = startTime.strftime("%Y%m%d")
if debug:
    print >>sys.stderr, "startYearMonthStr = ", startYearMonthStr
    print >>sys.stderr, "startDateStr = ", startDateStr

# set up list of date-hour combos to be checked
nFiles = (pastSecs / deltaBetweenFiles) + 1
yearMonthStrList = []
dateHourStrList = []
for iFile in range(0, nFiles):
    deltaSecs = timedelta(0, iFile * deltaBetweenFiles)
    dayTime = now - deltaSecs
    yearMonthStr = dayTime.strftime("%Y%m")
    dateStr = dayTime.strftime("%Y%m%d")
    dateHourStr = dateStr + '05'
    yearMonthStrList.append(yearMonthStr)
    dateHourStrList.append(dateHourStr)
if debug:
    print >>sys.stderr, "yearMonthStrList = ", yearMonthStrList
    print >>sys.stderr, "dateHourStrList = ", dateHourStrList

# get list of files meeting criteria from url
urlYearMonthList = []
urlFileList = []
for t in range(0,nFiles):
    currentYearMonth = yearMonthStrList[t]
    currentFileTime = dateHourStrList[t]
    for i in range(0,len(products)):
        # get list of files on server for this time and this product
        nextFile = products[i]+'_'+currentFileTime+'_National.jpg'
        urlYearMonthList.append(currentYearMonth)
        urlFileList.append(nextFile)
if debug:
    print >>sys.stderr, "urlYearMonthList = ", urlYearMonthList
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
        urlYearMonth = urlYearMonthList[idx]
        if debug:
            print >>sys.stderr, "  idx = ", idx
            print >>sys.stderr, "  urlFileName = ", urlFileName

        if urlFileName not in localFileList:
            if debug:
                print >>sys.stderr, urlFileName,"    not in localFileList -- get file"
            try:
                command = 'wget '+snowUrl+'/'+urlYearMonth+'/'+urlFileName
                os.system(command)
            except Exception as e:
                print sys.stderr, "    wget failed, exception: ", e
                continue
                
            # rename file and move to web server
            # first get forecast_hour
            (base,ext) = os.path.splitext(urlFileName)
            base = base.replace(products[i]+'_','')
            dateTime = base.replace('_National','')
            newFileName = 'ops.noaa.'+dateTime+'00.snow_precip_24hr.jpg'
            if debug:
                print >>sys.stderr, "    newFileName = ", newFileName

            # check to make sure that web server path exists
            catalogDir = catalogBaseDir+'/'+dateTime[0:8]
            if not os.path.exists(catalogDir):
                os.makedirs(catalogDir)

            # copy file to web server
            shutil.copy(targetDirBase+'/'+urlFileName,catalogDir+'/'+newFileName)






    

                              
