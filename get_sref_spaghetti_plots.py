#!/usr/bin/python3

"""
Sample Image url
https://www.spc.noaa.gov/exper/sref/gifs/latest/SREF_Spaghetti_H8_0__f000.gif
Model runs are at 03, 09, 15, 21Z - when are images posted?
15Z images still 'current' at 2242Z
Get every 6 forecast hours out to 48 - f000,f006,f012,f018,...f048
Set cron to run just prior to model init times (0255,0855,1455,2055)
"""

import os
import sys
import time
from datetime import timedelta
from datetime import datetime
import shutil
from ftplib import FTP
import requests

# User inputs
debug = True
test = False
secsPerDay = 86400
pastSecs = secsPerDay
secsPerRun = secsPerDay/4
deltaBetweenForecastHours = 6
lastForecastHour = 87
deltaInitHour = 6
deltaFcastHour = 6
srefUrl = 'https://www.spc.noaa.gov/exper/sref/gifs/latest'
category = 'model'
platform = 'SREF'
productList = {'Spaghetti_H8_0':'850mb_0degC_isotherm'}
fcastHours = ['000','006','012','018','024','030','036','042','048',
              '054','060']
ext = 'gif'
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

# get model date and time closest to current time
nowTime = time.gmtime()
now = datetime(nowTime.tm_year, nowTime.tm_mon, nowTime.tm_mday,
               nowTime.tm_hour, nowTime.tm_min, nowTime.tm_sec)
nowDate = datetime(nowTime.tm_year, nowTime.tm_mon, nowTime.tm_mday)
yesterdayDate = nowDate - timedelta(1)
yesterdayDateStr = yesterdayDate.strftime("%Y%m%d")
nowDateStr = now.strftime("%Y%m%d")
nowHourStr = now.strftime("%H")
if nowHourStr >= '06' and nowHourStr < '12':
    lastModelDateTimeStr = nowDateStr+'0300'
elif nowHourStr >= '12' and nowHourStr < '18':
    lastModelDateTimeStr = nowDateStr+'0900'
elif nowHourStr >= '18' and nowHourStr <= '23':
    lastModelDateTimeStr = nowDateStr+'1500'
#elif nowHourStr >= '23' and nowHourStr < '24':
#    lastModelDateTimeStr = nowDateStr+'2100'
elif nowHourStr >= '00' or nowHourStr < '06':
    lastModelDateTimeStr = yesterdayDateStr+'2100'
if debug:
    print("lastModelDateTimeStr = ", lastModelDateTimeStr)

for product in productList.keys():
    for hour in fcastHours:

        # download file into tempDir
        file = platform+'_'+product+'__f'+hour+'.gif'
        urlStr = srefUrl+'/'+file
        get = requests.get(urlStr)
        if get.status_code == 200:
            command = "lwp-request '"+urlStr+"' > "+tempDir+'/'+file
            os.system(command)
        
            # rename file and copy to tempDir
            catalogName = category+'.'+platform+'.'+lastModelDateTimeStr+'.'+hour+'_'+productList[product]+'.'+ext
            shutil.move(tempDir+'/'+file,tempDir+'/'+catalogName)
                
            # ftp file to catalog location
            ftpFile = open(os.path.join(tempDir,catalogName),'rb')
            catalogFTP.storbinary('STOR '+catalogName,ftpFile)
            ftpFile.close()
            print("ftp'd ", file, " to field catalog")

            # remove file from tempDir
            os.remove(os.path.join(tempDir,catalogName))

        else:
            print('urlStr =',urlStr,'does not exist')

# Close ftp connection
catalogFTP.quit()
