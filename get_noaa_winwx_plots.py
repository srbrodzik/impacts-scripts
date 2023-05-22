#!/usr/bin/python3

import os
import sys
import time
from datetime import timedelta
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import shutil
from ftplib import FTP

def listFD(url, ext=''):
    page = requests.get(url).text
    #print page
    soup = BeautifulSoup(page, 'html.parser')
    return [url + '/' + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]

# User inputs
debug = 1
test = False
secsPerDay = 86400
pastSecs = secsPerDay   # check last days
winwxUrl = 'https://www.wpc.ncep.noaa.gov/archives/winwx'
targetDirBase = '/home/disk/bob/impacts/sfc/winwx'
products = {'lowtrack':'low_tracks_and_clusters',
            'day1_psnow_gt_04':'day1_psnow_gt_4in',
            'day2_psnow_gt_04':'day2_psnow_gt_4in',
            'day3_psnow_gt_04':'day3_psnow_gt_4in'}
catalogPrefix = 'surface.NOAA_WPC'
tempDir = '/tmp'

# Field Catalog inputs
if test:
    ftpCatalogServer = 'ftp.atmos.washington.edu'
    ftpCatalogUser = 'anonymous'
    ftpCatalogPassword = 'brodzik@uw.edu'
    catalogDestDir = 'brodzik/incoming/impacts'
else:
    ftpCatalogServer = 'catalog.eol.ucar.edu'
    ftpCatalogUser = 'anonymous'
    catalogDestDir = '/pub/incoming/catalog/impacts'

# Open ftp connection to NCAR sever
if test:
    catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser,ftpCatalogPassword)
    catalogFTP.cwd(catalogDestDir)
else:
    catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
    catalogFTP.cwd(catalogDestDir)

# get current time
nowTime = time.gmtime()
now = datetime(nowTime.tm_year, nowTime.tm_mon, nowTime.tm_mday,
               nowTime.tm_hour, nowTime.tm_min, nowTime.tm_sec)
nowDateStr = now.strftime("%Y%m%d")
nowTimeStr = now.strftime("%H%M%S")
if debug:
    print("nowDateTimeStr = ", nowDateStr+nowTimeStr)

# compute start time
pastDelta = timedelta(0, pastSecs)
startTime = now - pastDelta
startDateStr = startTime.strftime("%Y%m%d")
startTimeStr = startTime.strftime("%H%M%S")
if debug:
    print("startDateTimeStr = ", startDateStr+startTimeStr)

# set up list of dates to be checked
dateStrList = []
dateStrList.append(nowDateStr)
if nowDateStr != startDateStr:
    dateStrList.append(startDateStr)
if debug:
    print("dateStrList = ", dateStrList)
    
nDates = len(dateStrList)
for t in range(0,nDates):
    currentDate = dateStrList[t]
    for prod in products:
        if debug:
            print("Processing", currentDate, "run for", prod, "data")

        # get list of files on server for this run and this product
        # only interested in forecasts up to and including 'lastForecastHour'
        urlFileList = []
        url = winwxUrl+'/'+currentDate+'/'
        ext = 'gif'
        for file in listFD(url, ext):
            tmp = os.path.basename(file)
            if prod in tmp:
                if prod == 'lowtrack':
                    (base,ext) = os.path.splitext(tmp)
                    parts = base.split('_')
                    if len(parts) == 2:
                        urlFileList.append(tmp)
                else:
                    urlFileList.append(tmp)
        if debug:
            print("urlFileList = ", urlFileList)
    
        if len(urlFileList) == 0:
            if debug:
                print("WARNING: ignoring run and product - no data on server")
                print("  for model run time: ", currentModelRun)
                print("  for product       : ", products[i])

        else:
            # make target directory, if necessary, and cd to it
            #targetDir = targetDirBase+'/'+dateHourStrList[i]+'/'+products[i]
            targetDir = targetDirBase
            if not os.path.exists(targetDir):
                os.makedirs(targetDir)
            os.chdir(targetDir)

            # get local file list - i.e. those which have already been downloaded
            localFileList = os.listdir('.')
            #if debug:
            #    print("  localFileList: ", localFileList)

            # loop through the url file list, downloading those that have
            # not yet been downloaded
            if debug:
                print("Starting to loop through url file list")
            
            for idx,urlFileName in enumerate(urlFileList,0):
                if debug:
                    print("  idx =", idx,"and urlFileName =", urlFileName)

                if urlFileName not in localFileList:
                    if debug:
                        print("    ",urlFileName,"not in localFileList -- get file")
                    try:
                        command = 'wget '+winwxUrl+'/'+currentDate+'/'+urlFileName
                        os.system(command)
                    except Exception as e:
                        print("    wget failed, exception: ", e)
                        continue

                    # rename file and move to web server
                    if prod == 'lowtrack':
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
                    catalogName = catalogPrefix+'.'+newFileDateTime+'.'+products[prod]+'.gif'
                    if debug:
                        print("    catalogName = ", catalogName)

                    # copy file to tempDir and rename
                    shutil.copy(targetDir+'/'+urlFileName,tempDir+'/'+catalogName)

                    # ftp file to catalog location
                    os.chdir(tempDir)
                    ftpFile = open(os.path.join(tempDir,catalogName),'rb')
                    catalogFTP.storbinary('STOR '+catalogName,ftpFile)
                    ftpFile.close()
                    os.chdir(targetDir)
                    if debug:
                        print('ftpd',catalogName,'to NCAR FC')

                    # remove file from tempDir
                    os.remove(os.path.join(tempDir,catalogName))

# Close ftp connection
catalogFTP.quit()
