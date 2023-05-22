#!/usr/bin/python3

import os
import sys
import time
from datetime import timedelta
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import shutil
from ftplib import FTP

def listFD(url, ext=''):
    page = requests.get(url).text
    #print page
    soup = BeautifulSoup(page, 'html.parser')
    return [url + '/' + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]

# User inputs
debug = True
test = False
urlBase = 'https://dd.weather.gc.ca/radar/CAPPI/GIF'
sites = {'CASBV':{'platform':'EC_CASBV'},
         'CASSF':{'platform':'EC_CASSF'}}
targetDirBase = '/home/disk/bob/impacts/radar'
products = {'SNOW':{'product':'Snow_Rate'},
            'RAIN':{'product':'Rain_Rate'}}
tempDir = '/tmp'
category = 'radar'

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

# get model date and time closest to current time
nowTime = time.gmtime()
now = datetime(nowTime.tm_year, nowTime.tm_mon, nowTime.tm_mday,
               nowTime.tm_hour, nowTime.tm_min, nowTime.tm_sec)
nowMinusHour = now - timedelta(hours=1)
nowDateHourStr = now.strftime("%Y%m%d%H")
nowMinusHourDateHourStr = nowMinusHour.strftime("%Y%m%d%H")
dateHours = [nowMinusHourDateHourStr,nowDateHourStr]

# set up list of model runs to be checked
for site in sites.keys():
    targetDir = targetDirBase+'/'+site.lower()
    if debug:
        print('Site    = {}'.format(site))

    # get list of files on server for this date and this product
    urlFileList = []
    url = urlBase+'/'+site+'/'
    ext = 'gif'
    for file in listFD(url, ext):
        os.chdir(tempDir)
        tmp = os.path.basename(file)
        #if tmp.endswith('SNOW.gif') or tmp.endswith('RAIN.gif'):
        if tmp.endswith('SNOW.gif'):
            (base,ext) = os.path.splitext(tmp)
            (fileDate,fileSite,junk1,fileElev,fileProduct) = base.split('_')
            if fileDate[0:10] in dateHours:
                if debug:
                    print('file = {}'.format(tmp))
                # download file
                command = 'wget '+file
                os.system(command)
                
                catName = category+'.'+sites[site]['platform']+'.'+fileDate+'.'+products[fileProduct]['product']+ext
                targetDateDir = targetDir+'/'+fileDate[0:8]
                if not os.path.isdir(targetDateDir):
                    os.makedirs(targetDateDir)
                shutil.move(tempDir+'/'+tmp,
                            targetDateDir+'/'+catName)
                
                # ftp file to catalog location
                ftpFile = open(os.path.join(targetDateDir,catName),'rb')
                catalogFTP.storbinary('STOR '+catName,ftpFile)
                ftpFile.close()

# Close ftp connection
catalogFTP.quit()
    

                              
