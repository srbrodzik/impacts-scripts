#!/usr/bin/python3

import os
import sys
import time
from datetime import timedelta
from datetime import datetime
import shutil
from ftplib import FTP

# User inputs
debug = 1
test = False
secsPerDay = 86400
pastSecs = secsPerDay*1.5   # check data from last 30 minutes
#pastSecs = 360   # check data from last 6 minutes
#pastSecs = 600   # check data from last 10 minutes
basePath = '/home/disk/data/images/sat_east_impacts'
basePathObs = '/home/disk/data/images/sat_east_impacts_obs'
productList = {'ch02':{'suffix':'vis_ch02','extension':'gif'},
               'ch08':{'suffix':'wv_ch08','extension':'gif'},
               'ch13':{'suffix':'ir_ch13','extension':'gif'},
               'color':{'suffix':'multi_ch_color','extension':'jpg'} }
#targetDirBase = '/home/disk/bob/impacts/sat'
tempDir = '/tmp'
#catalogBaseDir = '/home/disk/funnel/impacts/archive/ops/goes_east'
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
catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
catalogFTP.cwd(catalogDestDir)
# for testing
#catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser,ftpCatalogPassword)
#catalogFTP.cwd(catalogDestDir)

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

