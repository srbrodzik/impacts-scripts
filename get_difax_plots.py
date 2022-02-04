#!/usr/bin/python3

import os
import shutil
import time
from datetime import timedelta
from datetime import datetime
from ftplib import FTP   

products = {'850mb':'/home/disk/data/images/difax/difax_850',
            '700mb':'/home/disk/data/images/difax/difax_700',
            '500mb':'/home/disk/data/images/difax/difax_500',
            '300mb':'/home/disk/data/images/difax/difax_300',
            '200mb':'/home/disk/data/images/difax/difax_200'}
            
tempDir = '/tmp'
catalogPrefix = 'upperair.difax'

# Field Catalog inputs
#ftpCatalogServer = 'catalog.eol.ucar.edu'
#ftpCatalogUser = 'anonymous'
#catalogDestDir = '/pub/incoming/catalog/impacts'
# for testing
ftpCatalogServer = 'ftp.atmos.washington.edu'
ftpCatalogUser = 'anonymous'
ftpCatalogPassword = 'brodzik@uw.edu'
catalogDestDir = 'brodzik/incoming/impacts'

# Open ftp connection to NCAR sever
#catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
#catalogFTP.cwd(catalogDestDir)
# For testing
catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser,ftpCatalogPassword)
catalogFTP.cwd(catalogDestDir)

#----------------------
# get today's 1200 data
#----------------------
#nowTime = time.gmtime()
#now = datetime(nowTime.tm_year, nowTime.tm_mon, nowTime.tm_mday,
#               nowTime.tm_hour, nowTime.tm_min, nowTime.tm_sec)
now = datetime.now()
nowDateStr = now.strftime("%Y%m%d")

for product in products:

    os.chdir(products[product])
    for file in os.listdir():
        if file.startswith(nowDateStr) and file.endswith('200.gif'):
            (dateTime,ext) = os.path.splitext(file)
            catalogName = catalogPrefix+'.'+dateTime+'.'+product+ext
            shutil.copy(file,
                        tempDir+'/'+catalogName)
            # ftp file to catalog location
            ftpFile = open(os.path.join(tempDir,catalogName),'rb')
            catalogFTP.storbinary('STOR '+catalogName,ftpFile)
            ftpFile.close()

            # remove file from tempDir
            os.remove(os.path.join(tempDir,catalogName))

#-------------------------
# get tomorrow's 0000 data
#-------------------------
#tomorrowTime = time.gmtime()
#tomorrow = datetime(tomorrowTime.tm_year, tomorrowTime.tm_mon, tomorrowTime.tm_mday,
#                    tomorrowTime.tm_hour, tomorrowTime.tm_min, tomorrowTime.tm_sec)
tomorrow = now + timedelta(1)
tomorrowDateStr = tomorrow.strftime("%Y%m%d")

for product in products:

    os.chdir(products[product])
    for file in os.listdir():
        if file.startswith(tomorrowDateStr) and file.endswith('000.gif'):
            (dateTime,ext) = os.path.splitext(file)
            catalogName = catalogPrefix+'.'+dateTime+'.'+product+ext
            shutil.copy(file,
                        tempDir+'/'+catalogName)
            # ftp file to catalog location
            ftpFile = open(os.path.join(tempDir,catalogName),'rb')
            catalogFTP.storbinary('STOR '+catalogName,ftpFile)
            ftpFile.close()

            # remove file from tempDir
            os.remove(os.path.join(tempDir,catalogName))

# Close ftp connection
catalogFTP.quit()
