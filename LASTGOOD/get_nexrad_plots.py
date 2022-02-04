#!/usr/bin/python3

import os
import sys
import time
from datetime import timedelta
from datetime import datetime
import shutil
from ftplib import FTP

# User inputs
debug = 0
secsPerDay = 86400
#pastSecs = secsPerDay*6    # check data from last six days
#pastSecs = secsPerDay/12   # check data from last two hours
#pastSecs = secsPerDay/24   # check data from last one hour
pastSecs = secsPerDay/48   # check data from last 30 minutes
basePath = '/home/disk/data/images/newnexrad'
siteList = ['AKQ','BGM','BOX','BUF','CCX','CLE','DIX','DOX','DTX','DVN','ENX',
            'GRB','GRR','GYX','ILN','ILX','IND','IWX','LOT','LWX','MHX','MKX',
            'OKX','PIT','RAX','TYX','VWX']
productList = {'REF1':'DBZ','VEL1':'VEL'}
tempDir = '/tmp'
suffix = 'gif'

# Field Catalog inputs
ftpCatalogServer = 'catalog.eol.ucar.edu'
ftpCatalogUser = 'anonymous'
catalogDestDir = '/pub/incoming/catalog/impacts'
catalog_category = 'radar'
# For testing
#ftpCatalogServer = 'ftp.atmos.washington.edu'
#ftpCatalogUser = 'anonymous'
#ftpCatalogPassword = 'brodzik@uw.edu'
#catalogDestDir = 'brodzik/incoming/impacts'
#catalog_category = 'radar'

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
# For testing
#catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser,ftpCatalogPassword)
#catalogFTP.cwd(catalogDestDir)
    
for site in siteList:
    catalog_prefix = catalog_category+'.'+site+'-NEXRAD'
    for product in productList.keys():
        print("site = ", site, " and product = ", product)
    
        # get list of files from last two hours
        if os.path.isdir(basePath+'/'+site+'/'+product):
            for file in os.listdir(basePath+'/'+site+'/'+product):
                if file.endswith(suffix):
                    (base,ext) = os.path.splitext(file)
                    fileTimeStr = base
                    fileObjTime = datetime.strptime(fileTimeStr, '%Y%m%d%H%M')
                    fileDateStr = fileObjTime.strftime("%Y%m%d")
                    fileUnixTime =  int(fileObjTime.strftime("%s"))
                    if fileUnixTime <= nowUnixTime and fileUnixTime >= startUnixTime:
        
                        # copy file to /tmp with catalog filename
                        catalogName = catalog_prefix+'.'+fileTimeStr+'.'+productList[product]+ext
                        shutil.copy(basePath+'/'+site+'/'+product+'/'+file,
                                    tempDir+'/'+catalogName)

                        # ftp file to catalog location
                        ftpFile = open(os.path.join(tempDir,catalogName),'rb')
                        catalogFTP.storbinary('STOR '+catalogName,ftpFile)
                        ftpFile.close()
                        if debug:
                            print("ftp'd", catalogName, "to NCAR field catalog")

                        # remove file from tempDir
                        os.remove(os.path.join(tempDir,catalogName))
                                
# Close ftp connection
catalogFTP.quit()
