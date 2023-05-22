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
pastSecs = secsPerDay/6   # 4 hours
deltaBetweenFiles = secsPerDay / 24
#lastForecastHour = 6
metarUrl = 'http://weather.rap.ucar.edu/surface'
targetDirBase = '/home/disk/bob/impacts/sfc/metars'
tempDir = '/tmp'
#products = ['metars_alb','metars_bwi','metars_dtw']
products = ['metars_dlh','metars_dsm']
catalogPrefix = 'surface.GTS_Station_Plot'

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

# set up list of date-hour combos to be checked
dateHourStrList = ['2023022300','2023022301','2023022302','2023022303','2023022304','2023022305',
                   '2023022306','2023022307','2023022308','2023022309','2023022310','2023022311',
                   '2023022312','2023022313','2023022314','2023022315','2023022316','2023022317',
                   '2023022318','2023022319','2023022320','2023022321','2023022322','2023022323']
nFiles = len(dateHourStrList)
if debug:
    print("dateHourStrList = ", dateHourStrList)

# get list of files meeting criteria from url
urlFileList = []
for t in range(0,nFiles):
    currentFileTime = dateHourStrList[t]
    for i in range(0,len(products)):
        # get list of files on server for this time and this product
        nextFile = currentFileTime+'_'+products[i]+'.gif'
        urlFileList.append(nextFile)
if debug:
    print("urlFileList = ", urlFileList)

# if files in urlFileList not in localFileList, download, rename & ftp them
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
    for idx,urlFileName in enumerate(urlFileList,0):
        if debug:
            print("  idx = ", idx," and urlFileName = ",urlFileName)

        if urlFileName not in localFileList:
            if debug:
                print("   ",urlFileName,"not in localFileList -- get file")
            try:
                command = 'wget '+metarUrl+'/'+urlFileName
                os.system(command)
            except Exception as e:
                print("    wget failed, exception: ", e)
                continue

            # rename file and move to wftpserver
            # first get forecast_hour
            (base,ext) = os.path.splitext(urlFileName)
            (dateTime,junk,location) = base.split('_')
            if location == 'alb':
                region = 'Northeast_Region'
            elif location == 'bwi':
                region = 'Mid_Atlantic_Region'
            elif location == 'dtw':
                region = 'Mid_West_Region'
            elif location == 'dlh':
                region = 'Great_Lakes_West_Region'
            elif location == 'dsm':
                region = 'Chicago_West_Region'
            catalogName = catalogPrefix+'.'+dateTime+'00.'+region+'.gif'
            if debug:
                print("   catalogName = ", catalogName)

            # copy file to tmpDir as catalogName
            shutil.copy(targetDirBase+'/'+urlFileName,
                        tempDir+'/'+catalogName)

            # ftp file to catalog
            ftpFile = open(os.path.join(tempDir,catalogName),'rb')
            catalogFTP.storbinary('STOR '+catalogName,ftpFile)
            ftpFile.close()
            if debug:
                print('   ftpd',catalogName,'to NCAR FC\n')

            # remove file from tempDir
            os.remove(os.path.join(tempDir,catalogName))

# Close ftp connection
catalogFTP.quit()






    

                              
