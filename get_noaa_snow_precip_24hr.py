#!/usr/bin/python

import os
import sys
import time
from datetime import timedelta
from datetime import datetime
import shutil
from ftplib import FTP

# User inputs
debug = 1
secsPerDay = 86400
pastSecs = secsPerDay
deltaBetweenFiles = secsPerDay
snowUrl = 'https://www.nohrsc.noaa.gov/snow_model/images/full/National/ruc_snow_precip_24hr'
targetDirBase = '/home/disk/bob/impacts/sfc/snow'
products = {'ruc_snow_precip_24hr':'snow_precip_24hr'}
catalogPrefix = 'surface.NOAA_WPC'
tempDir = '/tmp'

# Field Catalog inputs
ftpCatalogServer = 'catalog.eol.ucar.edu'
ftpCatalogUser = 'anonymous'
catalogDestDir = '/pub/incoming/catalog/impacts'
# for testing
#ftpCatalogServer = 'ftp.atmos.washington.edu'
#ftpCatalogUser = 'anonymous'
#ftpCatalogPassword = 'brodzik@uw.edu'
#catalogDestDir = 'brodzik/incoming/impacts'

# Open ftp connection to NCAR sever
catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
catalogFTP.cwd(catalogDestDir)
# For testing
#catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser,ftpCatalogPassword)
#catalogFTP.cwd(catalogDestDir)

# get current date and hour
nowTime = time.gmtime()
now = datetime(nowTime.tm_year, nowTime.tm_mon, nowTime.tm_mday,
               nowTime.tm_hour, nowTime.tm_min, nowTime.tm_sec)
nowYearMonthStr = now.strftime("%Y%m")
nowDateStr = now.strftime("%Y%m%d")
if debug:
    print("nowYearMonthStr = ", nowYearMonthStr)
    print("nowDateStr = ", nowDateStr)

# compute start time
pastDelta = timedelta(0, pastSecs)
nowDate = datetime.strptime(nowDateStr,'%Y%m%d')
startTime = nowDate - pastDelta
startYearMonthStr = startTime.strftime("%Y%m")
startDateStr = startTime.strftime("%Y%m%d")
if debug:
    print("startYearMonthStr = ", startYearMonthStr)
    print("startDateStr = ", startDateStr)

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
    print("yearMonthStrList = ", yearMonthStrList)
    print("dateHourStrList = ", dateHourStrList)

# get list of files meeting criteria from url
urlYearMonthList = []
urlFileList = []
for t in range(0,nFiles):
    currentYearMonth = yearMonthStrList[t]
    currentFileTime = dateHourStrList[t]
    for prod in products:
        # get list of files on server for this time and this product
        nextFile = prod+'_'+currentFileTime+'_National.jpg'
        urlYearMonthList.append(currentYearMonth)
        urlFileList.append(nextFile)
if debug:
    print("urlYearMonthList = ", urlYearMonthList)
    print("urlFileList = ", urlFileList)

# if files in urlFileList not in localFileList, download them
if len(urlFileList) == 0:
    if debug:
        print("WARNING: no data on server")
else:
    # make sure targetBaseDir directory exists and cd to it
    if not os.path.exists(targetDirBase):
        os.makedirs(targetDirBase)
    os.chdir(targetDirBase)
    
    # get local file list - i.e. those which have already been downloaded
    localFileList = os.listdir('.')
    if debug:
        print("  localFileList: ", localFileList)

    # loop through the url file list, downloading those that have
    # not yet been downloaded
    #if debug:
    #    print("Starting to loop through url file list")
            
    for idx,urlFileName in enumerate(urlFileList,0):
        urlYearMonth = urlYearMonthList[idx]
        if debug:
            print("  idx = ", idx,"and urlFileName = ", urlFileName)

        if urlFileName not in localFileList:
            if debug:
                print("    ",urlFileName,"not in localFileList -- get file")
            try:
                command = 'wget '+snowUrl+'/'+urlYearMonth+'/'+urlFileName
                os.system(command)
            except Exception as e:
                print("    wget failed, exception: ", e)
                continue
                
            # rename file and move to web server
            # first get forecast_hour
            (base,ext) = os.path.splitext(urlFileName)
            base = base.replace(prod+'_','')
            dateTime = base.replace('_National','')
            catalogName = 'ops.noaa.'+dateTime+'00.snow_precip_24hr.jpg'
            catalogName = catalogPrefix+'.'+dateTime+'00.'+products[prod]+'.jpg'
            if debug:
                print("    catalogName = ", catalogName)

            # copy file to tempDir and rename
            shutil.copy(targetDirBase+'/'+urlFileName,tempDir+'/'+catalogName)

            # ftp file to catalog location
            os.chdir(tempDir)
            ftpFile = open(os.path.join(tempDir,catalogName),'rb')
            catalogFTP.storbinary('STOR '+catalogName,ftpFile)
            ftpFile.close()
            os.chdir(targetDirBase)
                      
            # remove file from tempDir
            os.remove(os.path.join(tempDir,catalogName))

# Close ftp connection
catalogFTP.quit()





    

                              
