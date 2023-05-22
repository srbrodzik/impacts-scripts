#!/usr/bin/python3

import os
import sys
import time
from datetime import datetime
from datetime import timedelta
import shutil
from ftplib import FTP

if len(sys.argv) != 5:
    print('Usage: sys.argv[0] [YYYYMMDD] [takeoff Time] [first seg time] [dateID]')
    sys.exit()
else:
    dateStr = sys.argv[1]
    dateObj = datetime.strptime(dateStr,"%Y%m%d")
    # format needs to be dd(abrMonth)YY
    date = (dateObj.strftime("%d%b%y")).lower()
    timeStr = sys.argv[2]
    segStartStr = dateStr+sys.argv[3]
    segStartObj = datetime.strptime(segStartStr,"%Y%m%d%H%M")
    dateID = sys.argv[4]

# User inputs
test = False
debug = True
segDelta = 30   #minutes
tempDir = '/tmp'
#holdDir = '/home/disk/bob/impacts/er2/CPL'
holdDirBase = '/home/disk/bob/impacts/lidar/er2'
url_trk = 'https://cpl.gsfc.nasa.gov/impacts22/Support_data'
urlBase = 'https://cpl.gsfc.nasa.gov/impacts22/Analy_quick'
catalogPrefix = 'aircraft.NASA_ER2'
sumDict = {'1064':'CPL_1064nm',
           '355':'CPL_355nm',
           '532':'CPL_532nm',
           'aod':'CPL_aerosol_opt_depth',
           'cod':'CPL_cloud_opt_depth',
           'colOD':'CPL_column_opt_depth',
           'depol':'CPL_depol_ratio',
           'ext':'CPL_extinction_coef',
           'ftype':'CPL_feature_type',
           'iwc':'CPL_iwc'}

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

os.chdir(tempDir)
holdDir = holdDirBase+'/'+dateStr
if not os.path.exists(holdDir):
    os.makedirs(holdDir)

# Download segment images
for val in range(1,20):
    if val >= 10:
        val = str(val)
    else:
        val = '0'+str(val)
    print('val =',val)
    file = 'imgseg'+val+'_'+dateID+'_'+date+'.png'
    print('file =',file)
    url = urlBase+'/'+file
    try:
        command = 'wget '+url
        os.system(command)
        (basename,ext) = os.path.splitext(file)
        nextSegObj = segStartObj + timedelta(minutes=segDelta*(int(val)-1))
        nextSegStr =  nextSegObj.strftime("%Y%m%d%H%M")
        #newName = catalogPrefix+'.'+dateStr+'00'+val+'.CPL_combo'+ext
        catFile = catalogPrefix+'.'+nextSegStr+'.CPL_combo'+ext
        print('catFile =',catFile)

        #rename file
        shutil.move(tempDir+'/'+file,
                    holdDir+'/'+catFile)   

        ##ftp file
        #ftpFile = open(os.path.join(holdDir,catFile),'rb')
        #catalogFTP.storbinary('STOR '+catFile,ftpFile)
        #ftpFile.close()
    except:
        print('file =',file,'unavailable')
        continue

# Process summary images
for val in sumDict.keys():
    file = 'imgsum_'+dateID+'_'+date+'_'+val+'.png'
    url = urlBase+'/'+file
    try:
        command = 'wget '+url
        os.system(command)
        (basename,ext) = os.path.splitext(file)
        parts = basename.split('_')
        if 'imgsum' in parts[0]:
            prodOrig = parts[3]
            product = sumDict[prodOrig]
            catFile = catalogPrefix+'.'+dateStr+timeStr+'.'+product+ext

        print('file = '+file)
        print('catFile = '+catFile)

        #rename file
        shutil.move(tempDir+'/'+file,
                    holdDir+'/'+catFile)

        ##ftp file
        #ftpFile = open(os.path.join(holdDir,catFile),'rb')
        #catalogFTP.storbinary('STOR '+catFile,ftpFile)
        #ftpFile.close()
    except:
        print('file =',file,'unavailable')

# Process track image
file = 'map_'+dateID+'_'+date+'.png'
print('file =',file)
url = url_trk+'/'+file
try:
    command = 'wget '+url
    os.system(command)
    catFile = catalogPrefix+'.'+dateStr+timeStr+'.CPL_flight_track'+ext
    print('catFile =',catFile)
    
    #rename file
    shutil.move(tempDir+'/'+file,
                holdDir+'/'+catFile)

    ##ftp file
    #ftpFile = open(os.path.join(holdDir,catFile),'rb')
    #catalogFTP.storbinary('STOR '+catFile,ftpFile)
    #ftpFile.close()
except:
    print('file =',file,'unavailable')
 
# Close ftp connection
catalogFTP.quit()
    
