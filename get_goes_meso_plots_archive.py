#!/usr/bin/python

import os
import sys
import time
from datetime import timedelta
from datetime import datetime
import shutil
from ftplib import FTP

# Read input args
numargs = len(sys.argv) - 1
if numargs != 1:
    print("Usage: %s [sector(1 or 2)]" % (sys.argv[0]))
    exit()
sector = sys.argv[1]

# User inputs
test = False
debug = True
secsPerDay = 86400
pastSecs = secsPerDay/12
#pastSecs = secsPerDay/12   # check data from last 2 hours
#pastSecs = 300   # check data from last 5 minutes
basePath = '/home/disk/data/images/sat_east_meso_impacts'
targetDirBase = '/home/disk/bob/impacts/sat'
tempDir = '/tmp'
ext = 'jpg'
catalogPrefix = 'satellite.GOES-16'
product = 'M'+sector+'color'
catalogSuffix = 'meso_sector_'+sector+'_color'

if test:
    ftpCatalogServer = 'ftp.atmos.washington.edu'
    ftpCatalogUser = 'anonymous'
    ftpCatalogPassword = 'brodzik@uw.edu'
    catalogDestDir = 'brodzik/incoming/impacts'
else:
    ftpCatalogServer = 'catalog.eol.ucar.edu'
    ftpCatalogUser = 'anonymous'
    catalogDestDir = '/pub/incoming/catalog/impacts'

# Open ftp connection
if test:
    catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser,ftpCatalogPassword)
    catalogFTP.cwd(catalogDestDir)
else:
    catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
    catalogFTP.cwd(catalogDestDir)

# getdate and time - are now and nowObj the same thing??
# REAL TIME
nowTime = time.gmtime()
nowObj = datetime(nowTime.tm_year, nowTime.tm_mon, nowTime.tm_mday,
                  nowTime.tm_hour, nowTime.tm_min, nowTime.tm_sec)
nowUnixTime = int(nowObj.strftime("%s"))
nowStr = nowObj.strftime("%Y%m%d%H%M%S")
nowDateStr = nowObj.strftime("%Y%m%d")

# ARCHIVE MODE
nowStr = '202301150700'
nowObj = datetime.strptime(nowStr,'%Y%m%d%H%M')
nowUnixTime = int(nowObj.strftime("%s"))
nowDateStr = nowObj.strftime("%Y%m%d")

if debug:
    print('nowStr =', nowStr)

# compute start time
pastDelta = timedelta(0, pastSecs)
startObj = nowObj - pastDelta
startUnixTime = int(startObj.strftime("%s"))
startStr = startObj.strftime("%Y%m%d%H%M%S")
startDateStr = startObj.strftime("%Y%m%d")
if debug:
    print('startStr =', startStr)

print('product =', product)
    
# get list of files from last 5 minutes
for file in os.listdir(basePath):
    if debug:
        print('file = ', file)
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
                shutil.copy(basePath+'/'+file,
                            targetDir)
                    
                # copy file to tempDir and rename
                catalogName = catalogPrefix+'.'+fileTimeStr+'.'+catalogSuffix+'.'+ext
                shutil.copy(targetDir+'/'+file,
                            tempDir+'/'+catalogName)

                # ftp to EOL
                ftpFile = open(tempDir+'/'+catalogName,'rb')
                catalogFTP.storbinary('STOR '+catalogName,ftpFile)
                ftpFile.close()

                # remove from tempDir
                os.remove(tempDir+'/'+catalogName)
                
# Close ftp connection
catalogFTP.quit()
