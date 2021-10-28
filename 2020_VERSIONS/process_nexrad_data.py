#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 13:50:11 2019

@author: brodzik
"""

import os
import sys
#import glob
#from shutil import copyfile
#from ftplib import FTP
import time
import datetime
from datetime import timedelta
#import subprocess
#import paramiko
import shutil

def find_nth(string, substring, n):
    if (n == 1):
        return string.find(substring)
    else:
        return string.find(substring, find_nth(string, substring, n - 1) + 1)

# User inputs
debug = 0
secsPerDay = 86400
pastSecs = 86400/12     # defined as seconds in two hour
#uwServer = 'freshair2.atmos.washington.edu'
#uwUser = 'brodzik'
#uwPasswd = ''
uwSourceDirBase = '/home/disk/data/gempak/nexrad/craft'
#homeDir = os.getenv('HOME')
rawDirBase = '/home/disk/bob/impacts/raw/nexrad'
sites = ['KBOX','KDIX']
#suffix = ['curM1','curS1']
#gifDir = os.path.join(homeDir, 'soundings/DOE/gifs')
#ftpCatalogServer = 'catalog.eol.ucar.edu'
#ftpCatalogUser = 'anonymous'
cfradialDirBase = '/home/disk/bob/impacts/cfradial'

# get current date and time
nowTime = time.gmtime()
now = datetime.datetime(nowTime.tm_year, nowTime.tm_mon, nowTime.tm_mday,
                        nowTime.tm_hour, nowTime.tm_min, nowTime.tm_sec)
nowDateStr = now.strftime("%Y%m%d")
nowDateTimeStr = now.strftime("%Y%m%d%H%M%S")
nowHour = now.strftime("%H")

# compute start time
pastDelta = timedelta(0, pastSecs)
startTime = now - pastDelta
startDateTimeStr = startTime.strftime("%Y%m%d%H%M%S")
startDateStr = startTime.strftime("%Y%m%d")
print >>sys.stderr, "startDateStr = ", startDateStr

# set up list of days to be checked
if nowHour > "00":
    nDays = 1
else:
    nDays = 2
dateStrList = []
for iDay in range(0, nDays):
    deltaSecs = timedelta(0, iDay * secsPerDay)
    dayTime = now - deltaSecs
    dateStr = dayTime.strftime("%Y%m%d")
    dateStrList.append(dateStr)
if debug:
    print >>sys.stderr, "dateStrList = ", dateStrList

for i in range(0,len(sites)):
    if debug:
        print >>sys.stderr, "Processing ",sites[i]," Data"
    uwSourceDir = uwSourceDirBase+'/'+sites[i]
    if debug:
        print >>sys.stderr, "uwSourceDir = ", uwSourceDir
    rawDir = rawDirBase+'/'+sites[i]
    if not os.path.exists(rawDir):
        os.makedirs(rawDir)

    # look for new radar data
    uwFileList = []
    uwDateList = []
    uwDateTimeList = []
    
    for file in sorted(os.listdir(uwSourceDir)):
        if file.startswith(sites[i]):
            for x in dateStrList: 
                if x in file:
                    uwFileList.append(file)
                    [junk,date,time] = file.split('_')
                    uwDateList.append(date)
                    uwDateTimeList.append(date+time)
    if debug:
        print >>sys.stderr, "uwFileList = ", uwFileList
        print >>sys.stderr, "uwDateList = ", uwDateList
        print >>sys.stderr, "uwDateTimeList = ", uwDateTimeList

    # loop through days
    for dateStr in dateStrList:
        if (dateStr not in uwDateList):
            if debug:
                print >>sys.stderr, "WARNING: ignoring date, does not exist on uw site"
                print >>sys.stderr, "  dateStr: ", dateStr
            continue

        if debug:
            print >>sys.stderr, " dateStr = ", dateStr
        
        # make raw directory if it doesn't exist
        localDayDir = os.path.join(rawDir, dateStr)
        if not os.path.exists(localDayDir):
            os.makedirs(localDayDir)
        os.chdir(localDayDir)
        if debug:
            print >>sys.stderr, "  localDayDir = ", localDayDir

        # get local file list - i.e. those which have already been downloaded
        localFileList = os.listdir('.')
        localFileList.reverse()
        if debug:
            print >>sys.stderr, "  localFileList: ", localFileList

        # reverse sort uw server lists
        uwFileList.reverse()
        uwDateList.reverse()
        uwDateTimeList.reverse()
        if debug:
            print >>sys.stderr, "  uwDateTimeList: ", uwDateTimeList
            print >>sys.stderr, "  uwFileList: ", uwFileList
            
        # loop through the uw file list, copying those files that have
        # not yet been copied to rawDir
        if debug:
            print >>sys.stderr, "Starting to loop through uw file list"
        for idx,uwFileName in enumerate(uwFileList,0):
            if debug:
                print >>sys.stderr, "  idx = ", idx
                print >>sys.stderr, "  uwFileName = ", uwFileName
                print >>sys.stderr, "  uwDateList[",idx,"] = ", uwDateList[idx]
                print >>sys.stderr, "  dateStr = ", dateStr
            if uwDateList[idx] == dateStr:
                if debug:
                    print >>sys.stderr, " uwDateList[idx]=dateStr: processing ",uwFileName

                uwDateTimeStr = uwDateTimeList[idx]+'00'
                localFileName = uwFileName
                if debug:
                    print >>sys.stderr, "  uwDateTimeStr = ", uwDateTimeStr
                    print >>sys.stderr, "  localFileName = ", localFileName
                    print >>sys.stderr, "  int(uwDateTimeStr) = ", int(uwDateTimeStr)
                    print >>sys.stderr, "  int(startDateTimeStr) = ", int(startDateTimeStr)
                if (int(uwDateTimeStr) < int(startDateTimeStr)):
                    if debug:
                        print >>sys.stderr, "  int(uwDateTimeStr) < int(startDateTimeStr)"
                        print >>sys.stderr, "    file time too old: ", uwDateTimeStr
                        print >>sys.stderr, "    startDateTimeStr:  ", startDateTimeStr
                else:
                    if debug:
                        print >>sys.stderr, "  int(uwDateTimeStr) >= int(startDateTimeStr)"
                        print >>sys.stderr, "    file time okay :  ", uwDateTimeStr
                        print >>sys.stderr, "    startDateTimeStr: ", startDateTimeStr
                        print >>sys.stderr, "    localFileName:    ", localFileName
                        print >>sys.stderr, "    localFileList:    ", localFileList
                    if (localFileName not in localFileList):
                        if debug:
                            print >>sys.stderr, localFileName," not in localFileList -- get file"
                        uwSourceFile = uwSourceDir+'/'+uwFileName
                        localFile = localDayDir+'/'+uwFileName
                        if debug:
                            print >>sys.stderr, "  uwSourceFile = ", uwSourceFile
                            print >>sys.stderr, "  localFile     = ", localFile
                        shutil.copyfile(uwSourceFile,localFile)
                        if debug:
                            print sys.stderr, "  copied file to ", localDayDir

                        # Uncompress file
                        cmd = "java -classpath /home/disk/freshair_ldm/local/java/netcdfAll-4.6.jar ucar.nc2.FileWriter2 -in "+localFile+" -out "+localFile+".nc"
                        if debug:
                            print >>sys.stderr, "cmd = ", cmd
                        os.system(cmd)
                        if os.path.exists(localFile+'.uncompress'):
                            cmd = "rm "+localFile+".uncompress"
                            os.system(cmd)
                        if debug:
                            print >>sys.stderr, "   Done uncompressing file"
                            
                        # Create cfradial file
                        uncmprLocalFile = localFile+'.nc'
                        if os.path.exists(uncmprLocalFile):
                            print >>sys.stderr, "uncmprLocalFile = ", uncmprLocalFile
                            cmd = "RadxConvert -v -params <paramsFile> -f "+uncmprLocalFile
                            if debug:
                                print >>sys.stderr, "cmd = ", cmd
                            #os.system(cmd)
                            os.remove(uncmprLocalFile)
                            if debug:
                                print >>sys.stderr, "   Done creating cfradial file"
                        else:
                            if debug:
                                print >>sys.stderr, "   cfradial file not created"
                                                     
                        # ftp cfradial file to IMPACTS server
                        if debug:
                            print >>sys.stderr, "   Done ftp'ing file to IMPACTS server"
                        
                    else:
                        if debug:
                            print >>sys.stderr, "  File ",uwFileName," already in rawDir"
            else:
                if debug:
                    print >>sys.stderr, "  Nothing done . . . uwDateList[idx] != dateStr"
                    print >>sys.stderr, "    uwDateList[idx] = ", uwDateList[idx]
                    print >>sys.stderr, "    dateStr = ", dateStr
            