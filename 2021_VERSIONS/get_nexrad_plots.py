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
#pastSecs = secsPerDay*6     # check data from last six days
pastSecs = secsPerDay/12   # check data from last two hours
basePath = '/home/disk/data/images/newnexrad'
siteList = ['AKQ','BGM','BOX','CCX','CLE','DIX','DOX','DTX','DVN','ENX','FFC',
            'GRB','GRR','GYX','ILN','ILX','IND','IWX','LOT','LWX','MHX','MKX',
            'OKX','RAX','TYX','VWX']
#productList = {'N0R':'_bref','N0V':'_vel'}
productList = {'N0R':'DBZ','N0V':'VEL'}

# catalog ftp info
ftpCatalogServer = 'catalog.eol.ucar.edu'
ftpCatalogUser = 'anonymous'
catalogDestDir = '/pub/incoming/catalog/impacts'
#catalogBaseDir = '/home/disk/funnel/impacts/archive/ops/nexrad'

targetDirBase = '/home/disk/bob/impacts/radar/nexrad'
suffix = 'gif'
#catalog_prefix = 'ops.nexrad'
catalog_prefix_base = 'radar'

# getdate and time - are now and nowObj the same thing??
nowTime = time.gmtime()
nowObj = datetime(nowTime.tm_year, nowTime.tm_mon, nowTime.tm_mday,
               nowTime.tm_hour, nowTime.tm_min, nowTime.tm_sec)
nowUnixTime = int(nowObj.strftime("%s"))
nowStr = nowObj.strftime("%Y%m%d%H%M%S")
nowDateStr = nowObj.strftime("%Y%m%d")
if debug:
    print >>sys.stderr, "nowStr = ", nowStr

# compute start time
pastDelta = timedelta(0, pastSecs)
startObj = nowObj - pastDelta
startUnixTime = int(startObj.strftime("%s"))
startStr = startObj.strftime("%Y%m%d%H%M%S")
startDateStr = startObj.strftime("%Y%m%d")
if debug:
    print >>sys.stderr, "startStr = ", startStr

for site in siteList:
    catalog_prefix = catalog_prefix_base+'.'+site+'-NEXRAD'
    for product in productList.keys():
        print >>sys.stderr, "site = ", site, " and product = ", product
    
        # get list of files from last two hours
        for file in os.listdir(basePath+'/'+site+'/'+product):
            if file.endswith(suffix):
                (base,ext) = os.path.splitext(file)
                fileTimeStr = base
                fileObjTime = datetime.strptime(fileTimeStr, '%Y%m%d%H%M')
                fileDateStr = fileObjTime.strftime("%Y%m%d")
                fileUnixTime =  int(fileObjTime.strftime("%s"))
                if fileUnixTime <= nowUnixTime and fileUnixTime >= startUnixTime:
        
                    # create and cd to target dir
                    targetDir = targetDirBase+'/'+site+'/'+product
                    if not os.path.exists(targetDir):
                        os.makedirs(targetDir)
                        os.chdir(targetDir)

                    # get list of files in targetDir
                    targetFileList = os.listdir(targetDir)

                    # if file not in targetFileList copy it over
                    if not file in targetFileList:
                        shutil.copy(basePath+'/'+site+'/'+product+'/'+file,targetDir)
                    
                        # rename file
                        #catalog_name = catalog_prefix+'.'+fileTimeStr+'.'+site.lower()+productList[product]+ext
                        catalog_name = catalog_prefix+'.'+fileTimeStr+'.'+productList[product]+ext
                        shutil.copy(targetDir+'/'+file,'/tmp/'+catalog_name)
                        
                        # Replace next lines with ftp to EOL ftp site
                        #if not os.path.exists(catalogBaseDir+'/'+fileDateStr):
                        #    os.mkdir(catalogBaseDir+'/'+fileDateStr)
                        #shutil.copy(targetDir+'/'+file,catalogBaseDir+'/'+fileDateStr+'/'+catalog_name)
                        #if debug:
                        #    print >>sys.stderr, "Copied ", file, " to ", catalog_name
                        
                        # ftp file to EOL
                        catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
                        catalogFTP.cwd(catalogDestDir)
                        localFilePath = '/tmp/'+catalog_name
                        ftpFile = open(localFilePath,'rb')
                        catalogFTP.storbinary('STOR '+catalog_name,ftpFile)
                        ftpFile.close()
                        catalogFTP.quit()

                        # remove file in /tmp
                        os.remove(localFilePath)
