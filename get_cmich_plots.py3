#!/usr/bin/python3

import os
import sys
import time
from datetime import timedelta
from datetime import datetime
import shutil
from ftplib import FTP
import requests
from bs4 import BeautifulSoup
import pytz

def listFD(url, ext=''):
    page = requests.get(url).text
    #print page
    soup = BeautifulSoup(page, 'html.parser')
    return [url + '/' + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]

def EDT2UTC(edtStr,fmt):

    # Convert EDT string to UTC datetime object (4 hours, not 5 as for EST)

    import pytz
    from datetime import datetime
    from datetime import timedelta

    # Subtract an hour from edtStr to convert from EDT to EST
    utc=pytz.utc
    eastern=pytz.timezone('US/Eastern')
    date_est=datetime.strptime(edtStr,fmt)-timedelta(hours=1)

    date_eastern=eastern.localize(date_est,is_dst=True)
    date_utc=date_eastern.astimezone(utc)

    #print('date_edt =',datetime.strptime(edtStr,fmt))
    #print('date_est =',date_est)
    #print('date_utc =',date_utc)
    
    return date_utc

# User inputs
debug = True
test = False
baseUrl = 'http://weather.eas.cmich.edu/rad/images'
tempDir = '/tmp'
targetDirBase = '/home/disk/bob/impacts/radar/cmu'
ext = 'png'
catPrefix = 'radar.MRR'
catSuffix = 'CMU_MI'

# Open ftp connection
if test:
    ftpCatalogServer = 'ftp.atmos.washington.edu'
    ftpCatalogUser = 'anonymous'
    ftpCatalogPassword = 'brodzik@uw.edu'
    catalogDestDir = 'brodzik/incoming/impacts'
else:
    ftpCatalogServer = 'catalog.eol.ucar.edu'
    ftpCatalogUser = 'anonymous'
    catalogDestDir = '/pub/incoming/catalog/impacts'

if test:
    catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser,ftpCatalogPassword)
    catalogFTP.cwd(catalogDestDir)
else:
    catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
    catalogFTP.cwd(catalogDestDir)
    
# get dates to look for - images created for last two hours
startObj = datetime.utcnow() - timedelta(hours=2)
startObj = startObj.replace(tzinfo=pytz.utc)
startDateStr = datetime.strftime(startObj, '%Y%m%d')
endObj = datetime.utcnow()
endObj = endObj.replace(tzinfo=pytz.utc)
endDateStr = datetime.strftime(startObj, '%Y%m%d')
if startDateStr == endDateStr:
    dates = [endDateStr]
else:
    dates = [startDateStr,endDateStr]
if debug:
    print('dates = ', dates)
    print('startObj = ',startObj)
    print('endObj   = ',endObj)

for date in dates:

    # Create target dir if necessary and cd to it
    targetDir = targetDirBase+'/'+date
    if not os.path.isdir(targetDir):
        os.makedirs(targetDir)
    os.chdir(targetDir)

    # get list of files already downloaded
    targetFiles = os.listdir(targetDir)

    # get list of files on server 
    url = baseUrl
    currentFList = listFD(url, ext)
    for file in currentFList:
        if 'mrr2' in file and file.endswith('png'):
            print('file = ',file)
            baseFileName = os.path.basename(file)
            (base,ext) = os.path.splitext(baseFileName)
            (prefix,fileDateTimeStr) = base.split('_')
            fileDateTimeObj = datetime.strptime(fileDateTimeStr,'%Y-%m-%d-%H-%M')
            fileDateTimeStr = fileDateTimeObj.strftime('%Y%m%d%H%M')
            fileDateStr = fileDateTimeObj.strftime('%Y%m%d')

            # convert time from EDT to UTC
            utcObj = EDT2UTC(fileDateTimeStr,'%Y%m%d%H%M')
            utcStr = utcObj.strftime('%Y%m%d%H%M')
            utcDateStr = utcObj.strftime('%Y%m%d')
            print('utcObj = ',utcObj)

            if date == utcDateStr and file not in targetFiles and utcObj > startObj and utcObj < endObj:
                print('Downloading file')
                command = 'wget '+url+'/'+baseFileName
                os.system(command)
                
                # copy to cat file name and ftp to catalog
                catFile = catPrefix+'.'+utcStr+'.'+catSuffix+ext
                if debug:
                    print('    catFile =', catFile)
                shutil.copy(targetDir+'/'+baseFileName,
                            tempDir+'/'+catFile)
                ftpFile = open(os.path.join(tempDir,catFile),'rb')
                catalogFTP.storbinary('STOR '+catFile,ftpFile)
                ftpFile.close()
                os.remove(tempDir+'/'+catFile)

# Close ftp connection
catalogFTP.quit()


