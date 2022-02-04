#!/usr/bin/python3

import os
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
import shutil
from ftplib import FTP

test = False
#difaxMaxDir = '/home/disk/data/archive/images/difax/difax_max'
difaxMaxDir = '/home/disk/data/images/difax/difax_max'
# Possible replacement:
# https://www.cpc.ncep.noaa.gov/products/tanal/1day/max_min/20211214.1day.max_min.C.gif
tempDir = '/tmp'
catalogPrefix = 'surface.NWS'
    
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

# Look for yesterday's map
today = datetime.utcnow()
yesterday = today - timedelta(days = 1)
dateStr = yesterday.strftime("%Y%m%d")

# note for 2021: new maps are in DifaxMaxDir+'/'+year+month
# e.g. /home/disk/data/archive/images/difax/difax_max/202112
#for file in os.listdir(os.path.join(difaxMaxDir,yearMonthStr)):
for file in os.listdir(difaxMaxDir):
    if dateStr in file and file.endswith('gif'):
        print('file = ',file)
        (dateTime,ext) = file.split('.')
        date = dateTime[0:8]
        print('date = ',date)
        catalogName = catalogPrefix+'.'+dateTime+'.max_temp.gif'
        print('catalogName = ',catalogName)
    
        #shutil.copy(os.path.join(difaxMaxDir,yearMonthStr,file),
	#	    tempDir+'/'+catalogName)
        shutil.copy(os.path.join(difaxMaxDir,file),
		    tempDir+'/'+catalogName)
            
        # ftp file to catalog location
        ftpFile = open(os.path.join(tempDir,catalogName),'rb')
        catalogFTP.storbinary('STOR '+catalogName,ftpFile)
        ftpFile.close()
        
        # remove file from tempDir
        os.remove(os.path.join(tempDir,catalogName))

# Look for today's map
dateStr = today.strftime("%Y%m%d")

#for file in os.listdir(os.path.join(difaxMaxDir,yearMonthStr)):
for file in os.listdir(difaxMaxDir):
    if dateStr in file and file.endswith('gif'):
        print('file = ',file)
        (dateTime,ext) = file.split('.')
        date = dateTime[0:8]
        print('date = ',date)
        catalogName = catalogPrefix+'.'+dateTime+'.max_temp.gif'
        print('catalogName = ',catalogName)
    
        #shutil.copy(os.path.join(difaxMaxDir,month,file),
	#	    tempDir+'/'+catalogName)
        shutil.copy(os.path.join(difaxMaxDir,file),
		    tempDir+'/'+catalogName)
            
        # ftp file to catalog location
        ftpFile = open(os.path.join(tempDir,catalogName),'rb')
        catalogFTP.storbinary('STOR '+catalogName,ftpFile)
        ftpFile.close()

        # remove file from tempDir
        os.remove(os.path.join(tempDir,catalogName))

# Close ftp connection
catalogFTP.quit()
