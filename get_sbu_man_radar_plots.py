#!/usr/bin/python

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
pastSecs = secsPerDay*2
baseUrl = 'https://doppler.somas.stonybrook.edu/ARCHIVE/IMAGES'
#urlSubDirs = ['CL51','MRR','PARSIVEL']   # 2020
urlSubDirs = ['CL51','PARSIVEL']
#products         = ['cl51','mrrpro','parsivel']  # 2020
products         = ['cl51','parsivel']
file_ext = 'png'
localDirBase = '/home/disk/bob/impacts/radar/sbu_images'
catFilePrefix = ['lidar','surface']
#catPlatform = ['ceil150','mrr_pro','parsivel']  #2020
catPlatform = ['Ceilometer','Parsivel']
catProduct = ['Manhattan_NY_15000m','Manhattan_NY']

# FC Naming Conventions
# lidar.Ceilometer.202003050000.Manhattan_NY_15000m.png
# surface.Parsivel.202003050000.Manhattan_NY.png

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
                        
# get current date
nowTime = time.gmtime()
now = datetime(nowTime.tm_year, nowTime.tm_mon, nowTime.tm_mday,
               nowTime.tm_hour, nowTime.tm_min, nowTime.tm_sec)
nowDateStr = now.strftime("%Y%m%d")
if debug:
    print('nowDateStr = ', nowDateStr)

# compute list of dates to check
pastDelta = timedelta(0, pastSecs)
startTime = now - pastDelta
startDateStr = startTime.strftime("%Y%m%d")
if debug:
    print('startDateStr = ', startDateStr)

# set up dates to be checked
nDates = int((pastSecs / secsPerDay) + 1)
dateStrList = []
for iDate in range(0, nDates):
    deltaSecs = timedelta(0, iDate * secsPerDay)
    dayTime = now - deltaSecs
    dateStr = dayTime.strftime("%Y%m%d")
    dateStrList.append(dateStr)
if debug:
    print('dateStrList = ', dateStrList)

for idate in range(0,nDates):
    currentDate = dateStrList[idate]
    currentYear = currentDate[0:4]

    # go through each product
    for iprod in range(0,len(products)):
        if debug:
            print('Processing', currentDate, 'for', products[iprod], 'data')

        localDir = localDirBase+'/'+products[iprod]
        if not os.path.isdir(localDir):
            os.makedirs(localDir)
        os.chdir(localDir)

        urlFile = products[iprod]+'_'+currentDate+'.'+file_ext
        url = baseUrl+'/'+urlSubDirs[iprod]+'/'+currentYear+'/'+urlFile
        catName = catFilePrefix[iprod]+'.'+catPlatform[iprod]+'.'+currentDate+'0000.'+catProduct[iprod]+'.'+file_ext

        if os.path.isfile(localDir+'/'+catName):
            continue
        else:
            try:
                command = 'wget '+url
                os.system(command)
                shutil.move(localDir+'/'+urlFile,
                            localDir+'/'+catName)
            except Exception as e:
                print('    wget failed, exception: ', e)
                continue

            ftpFile = open(localDir+'/'+catName,'rb')
            catalogFTP.storbinary('STOR '+catName,ftpFile)
            ftpFile.close()
            
# Close ftp connection
catalogFTP.quit()

