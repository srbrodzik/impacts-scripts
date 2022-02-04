#!/usr/bin/python3

import os
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
import shutil
from ftplib import FTP

test = False
#difaxMinDir = '/home/disk/data/archive/images/difax/difax_min'
difaxMinDir = '/home/disk/data/images/difax/difax_min'
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
#yearMonthStr = yesterday.strftime("%Y%m")

# note for 2021: new maps are in DifaxMinDir+'/'+year+month
# e.g. /home/disk/data/archive/images/difax/difax_min/202112
#for file in os.listdir(os.path.join(difaxMinDir,yearMonthStr)):
for file in os.listdir(difaxMinDir):
    if dateStr in file and file.endswith('gif'):
        print('file = ',file)
        (dateTime,ext) = file.split('.')
        date = dateTime[0:8]
        print('date = ',date)
        catalogName = catalogPrefix+'.'+dateTime+'.min_temp.gif'
        print('catalogName = ',catalogName)
    
        #shutil.copy(os.path.join(difaxMinDir,yearMonthStr,file),
	#	    tempDir+'/'+catalogName)
        shutil.copy(os.path.join(difaxMinDir,file),
		    tempDir+'/'+catalogName)
            
        # ftp file to catalog location
        ftpFile = open(os.path.join(tempDir,catalogName),'rb')
        catalogFTP.storbinary('STOR '+catalogName,ftpFile)
        ftpFile.close()
        
        # remove file from tempDir
        os.remove(os.path.join(tempDir,catalogName))

# Look for today's map
dateStr = today.strftime("%Y%m%d")
#yearMonthStr = today.strftime("%Y%m")

#for file in os.listdir(os.path.join(difaxMinDir,yearMonthStr)):
for file in os.listdir(difaxMinDir):
    if dateStr in file and file.endswith('gif'):
        print('file = ',file)
        (dateTime,ext) = file.split('.')
        date = dateTime[0:8]
        print('date = ',date)
        catalogName = catalogPrefix+'.'+dateTime+'.min_temp.gif'
        print('catalogName = ',catalogName)
    
        #shutil.copy(os.path.join(difaxMinDir,month,file),
	#	    tempDir+'/'+catalogName)
        shutil.copy(os.path.join(difaxMinDir,file),
		    tempDir+'/'+catalogName)
            
        # ftp file to catalog location
        ftpFile = open(os.path.join(tempDir,catalogName),'rb')
        catalogFTP.storbinary('STOR '+catalogName,ftpFile)
        ftpFile.close()

        # remove file from tempDir
        os.remove(os.path.join(tempDir,catalogName))

# Close ftp connection
catalogFTP.quit()
