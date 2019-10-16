#!/usr/bin/python                                                                                                  
                                                                                                                     
import sys
import os
import time
import datetime
from datetime import timedelta
import requests
from bs4 import BeautifulSoup
import wget
import shutil

def listFD(url, ext=''):
    page = requests.get(url).text
    soup = BeautifulSoup(page, 'html.parser')
    return [url + '/' + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]

url = 'http://weather.uwyo.edu/upperair/maps'
ext = 'gif'
gifType = 'oa'
tmpDir = '/tmp/uwyo'
category = 'ops'
platform = 'upper_air'
outDirBase = '/home/disk/funnel/impacts/archive/ops/upper_air'
mbList = ['200','300','500','700','850']
debug = 0

# Check to make sure tmpDir exists
if not os.path.exists(tmpDir):
    os.makedirs(tmpDir)

# Get current date and time
nowTime = time.gmtime()
now = datetime.datetime(nowTime.tm_year, nowTime.tm_mon, nowTime.tm_mday,
                        nowTime.tm_hour, nowTime.tm_min, nowTime.tm_sec)
nowDateStr = now.strftime("%Y%m%d")
nowDateTimeStr = now.strftime("%Y%m%d%H%M%S")
if debug:
    print >>sys.stderr, 'nowDateStr = ',nowDateStr,' and nowDateTimeStr = ',nowDateTimeStr

# Get current date and time minus one day - this will be startTime
UTC_OFFSET_TIMEDELTA = datetime.datetime.utcnow() - datetime.datetime.now()
date_1_day_ago = datetime.datetime.now() - timedelta(hours=24) + UTC_OFFSET_TIMEDELTA
startDateStr = date_1_day_ago.strftime("%Y%m%d")
startDateTimeStr = date_1_day_ago.strftime("%Y%m%d%H%M%S")
if debug:
    print >>sys.stderr, 'startDateStr = ',startDateStr,' and startDateTimeStr = ',startDateTimeStr

# List of dates to check for new data
dateStrList = [startDateStr,nowDateStr]

# Get list of files of interest on UWyo server from last 24 hours
uwyoFileList = []
uwyoFileDate = []
uwyoFileHour = []
uwyoFileLevel = []
for file in listFD(url, ext):
    tmp = os.path.basename(file)
    parts = tmp.split('.')
    datetime = parts[0]
    fdate = datetime[0:8]
    fhour = datetime[8:10]
    level = parts[1]
    region = parts[2]
    if region == 'naconf' and level.endswith(gifType) and fdate >= startDateStr:
        mb = level[:-len(gifType)]
        if mb.endswith('0') and mb in mbList:
            uwyoFileList.append(tmp)
            uwyoFileDate.append(fdate)
            uwyoFileHour.append(fhour)
            uwyoFileLevel.append(mb)

if debug:
    print >>sys.stderr, "  uwyoFileList: ", uwyoFileList
    print >>sys.stderr, "  uwyoFileDate: ", uwyoFileDate
    print >>sys.stderr, "  uwyoFileHour: ", uwyoFileHour
    print >>sys.stderr, "  uwyoFileLevel: ", uwyoFileLevel
    
# loop through days
for dateStr in dateStrList:
    if (dateStr not in uwyoFileDate):
        if debug:
            print >>sys.stderr, "WARNING: ignoring date, does not exist on UWyo site"
            print >>sys.stderr, "  dateStr: ", dateStr
        continue
    
    if debug:
        print >>sys.stderr, " dateStr = ", dateStr
        
    # make target directory
    localDayDir = os.path.join(outDirBase, dateStr)
    if not os.path.exists(localDayDir):
        os.makedirs(localDayDir)
    os.chdir(localDayDir)
    if debug:
        print >>sys.stderr, "  localDayDir = ", localDayDir

    # get local file list - i.e. those which have already been downloaded
    localFileList = os.listdir('.')
    if debug:
        print >>sys.stderr, "  localFileList: ", localFileList

    # loop through the UWyo file list, downloading those that have
    # not yet been downloaded
    for idx,uwyoFileName in enumerate(uwyoFileList,0):
        if debug:
            print >>sys.stderr, "  idx = ", idx
            print >>sys.stderr, "  uwyoFileName = ", uwyoFileName
        if uwyoFileDate[idx] == dateStr:
            if debug:
                print >>sys.stderr, " processing ",uwyoFileName
            fileTimeStr = uwyoFileHour[idx]+'0000'
            fileDateTimeStr = dateStr + fileTimeStr
            if (int(fileDateTimeStr) < int(startDateTimeStr)):
                if debug:
                    print >>sys.stderr, "  file time too old: ", fileDateTimeStr
                    print >>sys.stderr, "  startDateTimeStr:  ", startDateTimeStr
            else:
                uwyoFileName_new = category+'.'+platform+'.'+uwyoFileDate[idx]+uwyoFileHour[idx]+'00.'+uwyoFileLevel[idx]+'mb.gif'
                if (uwyoFileName_new not in localFileList):
                    if debug:
                        print >>sys.stderr, uwyoFileName_new," not in localFileList -- get file"
                    try:
                        wget.download(url+'/'+uwyoFileName,tmpDir)
                    except Exception as e:
                        print >>sys.stderr, "wget failed, exception: ", e
                        continue
                    if debug:
                        print >>sys.stderr, "Done with wget"
                    shutil.move(tmpDir+'/'+uwyoFileName,localDayDir+'/'+uwyoFileName_new)
                else:
                    if debug:
                        print >>sys.stderr, "  File ",uwyoFileName," already downloaded"
