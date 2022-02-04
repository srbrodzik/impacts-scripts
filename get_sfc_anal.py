#!/usr/bin/python3

import os
import sys
from datetime import datetime
from ftplib import FTP
import shutil

debug = 1
test = False
tempDir = '/tmp'
#outdir = '/home/disk/funnel/impacts/archive/ops/sfc_anal'
url1 = 'https://ocean.weather.gov/UA/East_coast.gif'
url2 = 'https://ocean.weather.gov/UA/USA.gif'
catalogPrefix = 'surface.NWS_Surface_Analysis'

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

# Open ftp connection
if test:
    catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser,ftpCatalogPassword)
    catalogFTP.cwd(catalogDestDir)
else:
    catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
    catalogFTP.cwd(catalogDestDir)

# get date and time info
dateTime = datetime.utcnow()
dateStr = dateTime.strftime("%Y%m%d")
hourStr = dateTime.strftime("%H")

# determine fileDateTime
if hourStr == '04':
    fileDateTime = dateStr+'0000'
elif hourStr == '10':
    fileDateTime = dateStr+'0600'
elif hourStr == '16':
    fileDateTime = dateStr+'1200'
elif hourStr == '22':
    fileDateTime = dateStr+'1800'
else:
    print('hour =',hourStr,': Not one of 4 hours of interest')
    sys.exit(0)

# download files, rename them and ftp them
os.chdir(tempDir)

command = 'wget '+url1
os.system(command)
catalogName = catalogPrefix+'.'+fileDateTime+'.Atlantic.gif'
shutil.move('East_coast.gif',
            catalogName)
ftpFile = open(os.path.join(tempDir,catalogName),'rb')
catalogFTP.storbinary('STOR '+catalogName,ftpFile)
ftpFile.close()
os.remove(os.path.join(tempDir,catalogName))
if debug:
    print('ftpd ',catalogName,' to NCAR FC')

command = 'wget '+url2
os.system(command)
catalogName = catalogPrefix+'.'+fileDateTime+'.North_America.gif'
shutil.move('USA.gif',
            catalogName)
ftpFile = open(os.path.join(tempDir,catalogName),'rb')
catalogFTP.storbinary('STOR '+catalogName,ftpFile)
ftpFile.close()
os.remove(os.path.join(tempDir,catalogName))
if debug:
    print('ftpd ',catalogName,' to NCAR FC')

# Close ftp connection
catalogFTP.quit()



