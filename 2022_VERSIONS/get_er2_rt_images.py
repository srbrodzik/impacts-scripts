#!/usr/bin/python3

import os
import shutil
from datetime import datetime
from datetime import timedelta
import time
from ftplib import FTP

test = False
tempDir = '/tmp'

# all real time images will be here
urlBase = 'https://har.gsfc.nasa.gov/storm/IMPACTS-2022/radar_rt_plot'

# merged files in catalog will be here:
# catUrlBase/YYYYMMDD/HH/aircraft.NASA_ER2.<datetime>.radar_all_refl.png
catUrlBase = 'http://catalog.eol.ucar.edu/impacts_2022/aircraft/nasa_er2'

# local base directory for merged radar product
mergeDirBase = '/home/disk/bob/impacts/radar/er2'
radarDirBase = '/home/disk/bob/impacts/radar/er2/radars'

# filenames:
#     'CRS':{'orig':'CRS_rt_current.png','catalog':'aircraft.NASA_ER2.<datetime>.CRS_dBZ_vel.png'},
#     'EXRAD':{'orig':'EXRAD_rt_current.png','catalog':'aircraft.NASA_ER2.<datetime>.EXRAD_dBZ_vel.png'},
#     'HIWRAP_KA':'orig':'HIWRAP_KA_rt_current.png','catalog':'aircraft.NASA_ER2.<datetime>.HIWRAP_Ka_dBZ_vel.png'},
#     'HIWRAP_KU': 'orig':'HIWRAP_KU_rt_current.png','catalog':'aircraft.NASA_ER2.<datetime>.HIWRAP_Ku_dBZ_vel.png'}
radarList = ['CRS','EXRAD','HIWRAP_KA','HIWRAP_KU']
mergeFile = 'radars_rt_current_merge.png'
rawFileSuffix = '_rt_current.png'
catFilePrefix = 'aircraft.NASA_ER2'
catFileSuffix = 'dBZ_vel.png'

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

# Get current time
now = datetime.utcnow()
nowDateStr = now.strftime("%Y%m%d")
nowDateTimeStr = now.strftime("%Y%m%d%H%M")
nowHourStr = now.strftime("%H")

# Change to tempDir
os.chdir(tempDir)

# Get single radar images
for radar in radarList:
    # download image
    command = 'wget '+urlBase+'/'+radar+'/'+radar+rawFileSuffix
    os.system(command)
    # rename image
    catalogName = catFilePrefix+'.'+nowDateTimeStr+'.'+radar+'_'+catFileSuffix
    shutil.move(tempDir+'/'+radar+rawFileSuffix,
                tempDir+'/'+catalogName)

    # ftp image
    ftpFile = open(os.path.join(tempDir,catalogName),'rb')
    catalogFTP.storbinary('STOR '+catalogName,ftpFile)
    ftpFile.close()

    # Move image to radarDir
    radarDir = os.path.join(radarDirBase,nowDateStr)
    if not os.path.exists(radarDir):
        os.makedirs(radarDir)
    shutil.move(os.path.join(tempDir,catalogName),
                os.path.join(radarDir,catalogName))
    #os.remove(os.path.join(tempDir,catalogName))

# Get merged radar image
command = 'wget '+urlBase+'/'+mergeFile
os.system(command)
# rename image
catalogName = catFilePrefix+'.'+nowDateTimeStr+'.radar_all_refl.png'
shutil.move(os.path.join(tempDir,mergeFile),
            os.path.join(tempDir,catalogName))

# ftp image
ftpFile = open(os.path.join(tempDir,catalogName),'rb')
catalogFTP.storbinary('STOR '+catalogName,ftpFile)
ftpFile.close()

# Move image to mergeDir
mergeDir = os.path.join(mergeDirBase,nowDateStr)
if not os.path.exists(mergeDir):
    os.makedirs(mergeDir)
shutil.move(os.path.join(tempDir,catalogName),
            os.path.join(mergeDir,catalogName))
#os.remove(os.path.join(tempDir,catalogName))

    
    

