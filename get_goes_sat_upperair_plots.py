#!/usr/bin/python3

# Plots are created every 3 hours UTC time starting at 00Z with one hour lag
# So they are available every 3 hours starting at 01Z
# For the cron, subtract 7 hours so 01Z image available at 18Z local

import os
import sys
import time
from datetime import timedelta
from datetime import datetime
import shutil
from ftplib import FTP

# User inputs
debug = True
test = False
secsPerDay = 86400
pastSecs = secsPerDay/4   # check data from last 6 hours
#pastSecs = 360   # check data from last 6 minutes
#pastSecs = 600   # check data from last 10 minutes
basePath = '/home/disk/data/images/sat_east_impacts_obs'
basePathObs = '/home/disk/data/images/sat_east_impacts_obs'
productList = {'500mb':{'suffix':'ir_ch02_500mb','extension':'gif'},
               '850mb':{'suffix':'ir_ch02_850mb','extension':'gif'} }
tempDir = '/tmp'
catalog_prefix = 'satellite.GOES-16'

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

# getdate and time - are now and nowObj the same thing??
nowTime = time.gmtime()
nowObj = datetime(nowTime.tm_year, nowTime.tm_mon, nowTime.tm_mday,
                  nowTime.tm_hour, nowTime.tm_min, nowTime.tm_sec)
nowUnixTime = int(nowObj.strftime("%s"))
nowStr = nowObj.strftime("%Y%m%d%H%M%S")
nowDateStr = nowObj.strftime("%Y%m%d")
if debug:
    print("nowStr = ", nowStr)

# compute start time
pastDelta = timedelta(0, pastSecs)
startObj = nowObj - pastDelta
startUnixTime = int(startObj.strftime("%s"))
startStr = startObj.strftime("%Y%m%d%H%M%S")
startDateStr = startObj.strftime("%Y%m%d")
if debug:
    print("startStr = ", startStr)

# Open ftp connection to NCAR sever
if test:
    catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser,ftpCatalogPassword)
    catalogFTP.cwd(catalogDestDir)
else:
    catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
    catalogFTP.cwd(catalogDestDir)

for product in productList.keys():
    print("product = ", product)
    
    # get list of files from last 5 minutes
    for file in os.listdir(basePath):
        if file.endswith(product+'.'+productList[product]['extension']):
            #(base,ext) = os.path.splitext(file)
            (fileTimeStr,junk,ext) = file.split('.')
            fileObjTime = datetime.strptime(fileTimeStr, '%Y%m%d%H%M')
            fileDateStr = fileObjTime.strftime("%Y%m%d")
            fileUnixTime =  int(fileObjTime.strftime("%s"))
            if fileUnixTime <= nowUnixTime and fileUnixTime >= startUnixTime:
        
                print("file = ",file)
             
                # rename file and copy to tempDir
                catalog_name = catalog_prefix+'.'+fileTimeStr+'.'+productList[product]['suffix']+'.'+ext
                shutil.copy(basePath+'/'+file,tempDir+'/'+catalog_name)
                
                # ftp file to catalog location
                ftpFile = open(os.path.join(tempDir,catalog_name),'rb')
                catalogFTP.storbinary('STOR '+catalog_name,ftpFile)
                ftpFile.close()
                print("ftp'd ", file, " to field catalog")

                # remove file from tempDir
                os.remove(os.path.join(tempDir,catalog_name))

# Close ftp connection
catalogFTP.quit()

