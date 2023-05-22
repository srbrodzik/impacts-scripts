#!/usr/bin/python3

import os
import shutil
from datetime import timedelta
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import shutil
from ftplib import FTP
import glob

def listFD(url, ext='', user='', pw=''):
    page = requests.get(url,auth=(user,pw)).text
    soup = BeautifulSoup(page, 'html.parser')
    return [url + '/' + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]

# Mobile soundings
# infile = GrawSonde_RadarTruck_RTS_YYYYMMDD_hhmmss.nc
# outfile = 'upperair.SBU_sonde.YYYYMMDDhhmmss.skewT.png'

# Static soundings
# file = GrawSonde_SBUSouthP_RTS_YYYYMMDD_hhmmss.nc
# outfile = 'upperair.SBU_sonde.YYYYMMDDhhmmss.Stonybrook_NY_skewT.png'

type = 'GrawSonde'
sndgDict = {'RadarTruck':{'url':'http://doppler.somas.stonybrook.edu/IMPACTS/RadarTruck/grawmetsounding/netcdf',
                          'format':'SBUnc',
                          'rawPrefix':type+'_RTS',
                          'ncSuffix':'Mobile',
                          'catalogSuffix':'skewT'},
            'SBUSouthP':{'url':'http://doppler.somas.stonybrook.edu/IMPACTS/grawmetsounding/netcdf',
                         'format':'SBUnc_static',
                         'rawPrefix':type+'_SBUSouthP_RTS',
                         'ncSuffix':'Fixed',
                         'catalogSuffix':'Stonybrook_NY_skewT'}
}
# SBU credentials
sbuUser = 'DataAccess'
sbuPassword = 'WinterAtSBU'

binDir = '/home/disk/bob/impacts/bin'
localDirBase = '/home/disk/bob/impacts/upperair/sbu'
tempDir = '/tmp'
catalogPrefix = 'upperair.SBU_sonde'
ext = 'nc'
debug = True
test = False

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

# Get current date and time
now = datetime.utcnow()
nowDateStr = now.strftime("%Y%m%d")
nowDateTimeStr = now.strftime("%Y%m%d%H%M%S")
startTime = now - timedelta(2)
startDateStr = startTime.strftime("%Y%m%d")
startDateTimeStr = startTime.strftime("%Y%m%d%H%M%S")
if debug:
    print('startDateTimeStr = ',startDateTimeStr)
    print('nowDateTimeStr   = ',nowDateTimeStr)
    
# List of dates to check for new data
if test:
    dateStrList = ['20210207']
    startDateStr = '20210207'
else:
    dateStrList = [startDateStr,nowDateStr]

for sndg in sndgDict.keys():

    if debug:
        print('sndg = ',sndg)

    # Get list of files of interest on SBU server from last 24 hours
    for date in dateStrList:
        sbuFileList = []
        sbuFileDate = []
        sbuFileTime = []
        sbuFileSite = []
        for file in listFD(sndgDict[sndg]['url'], ext, sbuUser, sbuPassword):
            tmp = os.path.basename(file)
            (base,end) = os.path.splitext(tmp)
            print('base = ',base)
            if not base.startswith('GrawSonde_RTS'):
                (ftype,site,rts,fdate,ftime) = base.split('_')

                #if ftype == type and fdate >= startDateStr:
                if ftype == type and fdate == date:
                    sbuFileList.append(tmp)
                    sbuFileDate.append(fdate)
                    sbuFileTime.append(ftime)
                    sbuFileSite.append(site)

        if debug:
            print('sbuFileList = ',sbuFileList)

        # Go to localDir and download files that are not present
        localDir = os.path.join(localDirBase,date)
        if not os.path.exists(localDir):
            os.makedirs(localDir)
        os.chdir(localDir)
        localFileList = os.listdir('.')
        for idx,sbuFileName in enumerate(sbuFileList,0):

            # Rename netcdf file upon download - maybe don't do this???
            if sndg =='RadarTruck':
                ncFileName = catalogPrefix+'.'+sbuFileDate[idx]+sbuFileTime[idx][0:4]+'.RadarTruck.nc'
            else if sndg == 'SBUSouthP':
                ncFileName = catalogPrefix+'.'+sbuFileDate[idx]+sbuFileTime[idx][0:4]+'.Stonybrook_NY.nc'
            
            if ncFileName not in localFileList:

                # wget file & rename
                #ncFileName = catalogPrefix+'.'+sbuFileDate[idx]+sbuFileTime[idx]+'.'+sndgDict[sndg]['ncSuffix']+'.nc'
                command = 'wget -O '+ncFileName+' --user '+sbuUser+' --password '+sbuPassword+' --cut-dirs=4 '+sndgDict[sndg]['url']+'/'+sndgDict[sndg]['rawPrefix']+'_'+sbuFileDate[idx]+'_'+sbuFileTime[idx]+'.nc'
                os.system(command)

                # create skewt - modify code for new infile format
                command = binDir+'/skewplot.py --file '+ncFileName+' --outpath '+tempDir+' --format '+sndgDict[sndg]['format']+' --parcel False --hodograph False'
                os.system(command)
                plots = glob.glob(tempDir+'/'+catalogPrefix+'.'+date+'*.png')
                catalogName = os.path.basename(plots[0])
                
                # ftp file to catalog location
                ftpFile = open(os.path.join(tempDir,catalogName),'rb')
                catalogFTP.storbinary('STOR '+catalogName,ftpFile)
                ftpFile.close()

                # remove file from tempDir
                os.remove(os.path.join(tempDir,catalogName))
            
# Close ftp connection
catalogFTP.quit()

