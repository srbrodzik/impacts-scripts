#!/usr/bin/python

import os
import sys
import time
from datetime import timedelta
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import shutil

def listFD(url, ext=''):
    page = requests.get(url).text
    #print page
    soup = BeautifulSoup(page, 'html.parser')
    return [url + '/' + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]

# User inputs
debug = 1
secsPerDay = 86400
pastSecs = secsPerDay   # check last days
winwxUrl = 'https://www.wpc.ncep.noaa.gov/archives/winwx'
targetDirBase = '/home/disk/bob/impacts/raw/surface/winwx'
products = ['lowtrack','day1_psnow_gt_04','day2_psnow_gt_04','day3_psnow_gt_04']
catalogBaseDir = '/home/disk/funnel/impacts-website/archive/ops/noaa'

# get current time
nowTime = time.gmtime()
now = datetime(nowTime.tm_year, nowTime.tm_mon, nowTime.tm_mday,
               nowTime.tm_hour, nowTime.tm_min, nowTime.tm_sec)
nowDateStr = now.strftime("%Y%m%d")
nowTimeStr = now.strftime("%H%M%S")
if debug:
    print >>sys.stderr, "nowDateTimeStr = ", nowDateStr+nowTimeStr

# compute start time
pastDelta = timedelta(0, pastSecs)
startTime = now - pastDelta
startDateStr = startTime.strftime("%Y%m%d")
startTimeStr = startTime.strftime("%H%M%S")
if debug:
    print >>sys.stderr, "startDateTimeStr = ", startDateStr+startTimeStr

# set up list of dates to be checked
dateStrList = []
dateStrList.append(nowDateStr)
if nowDateStr != startDateStr:
    dateStrList.append(startDateStr)
if debug:
    print >>sys.stderr, "dateStrList = ", dateStrList
    
nDates = len(dateStrList)
for t in range(0,nDates):
    currentDate = dateStrList[t]
    for i in range(0,len(products)):
        if debug:
            print >>sys.stderr, "Processing ", currentDate, " run for ", products[i], " data"

        # get list of files on server for this run and this product
        # only interested in forecasts up to and including 'lastForecastHour'
        urlFileList = []
        #urlDateList = []
        #urlDateTimeList = []
        url = winwxUrl+'/'+currentDate+'/'
        ext = 'gif'
        for file in listFD(url, ext):
            tmp = os.path.basename(file)
            if products[i] in tmp:
                if products[i] == 'lowtrack':
                    (base,ext) = os.path.splitext(tmp)
                    parts = base.split('_')
                    if len(parts) == 2:
                        urlFileList.append(tmp)
                else:
                    urlFileList.append(tmp)
        if debug:
            print >>sys.stderr, "urlFileList = ", urlFileList
    
        if len(urlFileList) == 0:
            if debug:
                print >>sys.stderr, "WARNING: ignoring run and product - no data on server"
                print >>sys.stderr, "  for model run time: ", currentModelRun
                print >>sys.stderr, "  for product       : ", products[i]

        else:
            # make target directory, if necessary, and cd to it
            #targetDir = targetDirBase+'/'+dateHourStrList[i]+'/'+products[i]
            targetDir = targetDirBase
            if not os.path.exists(targetDir):
                os.makedirs(targetDir)
            os.chdir(targetDir)

            # get local file list - i.e. those which have already been downloaded
            localFileList = os.listdir('.')
            #localFileList.reverse()
            #if debug:
            #    print >>sys.stderr, "  localFileList: ", localFileList

            # get url file list (not sure I need this)
            #urlFileList.sort()
            #urlFileList.reverse()

            # loop through the url file list, downloading those that have
            # not yet been downloaded
            if debug:
                print >>sys.stderr, "Starting to loop through url file list"
            
            for idx,urlFileName in enumerate(urlFileList,0):
                if debug:
                    print >>sys.stderr, "  idx = ", idx
                    print >>sys.stderr, "  urlFileName = ", urlFileName
                    #print >>sys.stderr, "  urlDateList[",idx,"] = ", urlDateList[idx]
                    #print >>sys.stderr, "  dateStr = ", dateStr

                if urlFileName not in localFileList:
                    if debug:
                        print >>sys.stderr, urlFileName,"    not in localFileList -- get file"
                    try:
                        command = 'wget '+winwxUrl+'/'+currentDate+'/'+urlFileName
                        os.system(command)
                    except Exception as e:
                        print sys.stderr, "    wget failed, exception: ", e
                        continue

                    # rename file and move to web server
                    if products[i] == 'lowtrack':
                        (dateHr,rest) = urlFileName.split('_')
                        fileDate = dateHr[0:8]
                        fileHour = dateHr[8:10]
                        if fileHour == '15':
                            newFileDateTime = fileDate+'1200'
                        elif fileHour == '03':
                            newFileDateTime = fileDate+'0000'
                    else:
                        (base,ext) = os.path.splitext(urlFileName)
                        (junk1,junk2,junk3,junk4,dateHr) = base.split('_')
                        fileDate = dateHr[0:8]
                        fileHour = dateHr[8:10]
                        newFileDateTime = fileDate+fileHour+'00'

                    # create full file name
                    newFileName = 'ops.noaa.'+newFileDateTime+'.'+products[i]+'.gif'
                    if debug:
                        print >>sys.stderr, "    newFileName = ", newFileName

                    # check to make sure that web server path exists
                    catalogDir = catalogBaseDir+'/'+fileDate
                    if not os.path.exists(catalogDir):
                        os.makedirs(catalogDir)

                    # copy file to web server
                    shutil.copy(targetDir+'/'+urlFileName,catalogDir+'/'+newFileName)






    

                              
