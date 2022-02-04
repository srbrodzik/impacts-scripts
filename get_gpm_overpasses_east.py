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

def listFD_new(url, prefix='', ext=''):
    page = requests.get(url).text
    #print page
    soup = BeautifulSoup(page, 'html.parser')
    list = [url + '/' + node.get('href') for node in soup.find_all('a') if ( node.get('href').startswith(prefix) and node.get('href').endswith(ext) )]
    return list

# User inputs
debug = True
test = False
url = 'https://gpm-gv.gsfc.nasa.gov/Tier1/Files_07day/IMPACTS-EAST'
tempDir = '/tmp'
targetDirBase = '/home/disk/bob/impacts/gpm'
products = ['IMAGE_GPM_7DAY_IMPACTS-EAST']
file_ext = 'png'
catalogFilePrefix = 'satellite.GPM'
catalogFileSuffix = ['overpass_east']

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

# go through each product
for i in range(0,len(products)):
    prod = products[i]
    suffix = catalogFileSuffix[i]
    if debug:
        print('Processing', prod)
    
    # get list of files on server 
    currentFList = listFD_new(url, prod, file_ext)

    for file in currentFList:
        baseFileName = os.path.basename(file)
        (base,ext) = os.path.splitext(baseFileName)
        parts = base.split('_')
        if len(parts) == 6:
            raw_date = parts[4]
            raw_time = parts[5]
            (year,month,day) = raw_date.split('-')
            (hour,minute,second) = raw_time.split('-')
            date = year+month+day
            time = hour+minute+second

            # make target directory, if necessary, and cd to it
            targetDir = targetDirBase+'/'+date
            if not os.path.exists(targetDir):
                os.makedirs(targetDir)
            os.chdir(targetDir)

            # get local file list - i.e. those which have already been downloaded
            localFileList = os.listdir('.')

            if baseFileName not in localFileList:
                if debug:
                    print(baseFileName,'not in localFileList -- get file')
                try:
                    command = 'wget '+url+'/'+baseFileName
                    os.system(command)
                except Exception as e:
                    print('    wget failed, exception: ', e)
                    continue
            
                # copy to cat file name and ftp to catalog
                catFile = catalogFilePrefix+'.'+date+time+'.'+suffix+ext
                if debug:
                    print('    catFile =', catFile)
                shutil.copy(targetDir+'/'+baseFileName,
                            tempDir+'/'+catFile)
                ftpFile = open(os.path.join(tempDir,catFile),'rb')
                catalogFTP.storbinary('STOR '+catFile,ftpFile)
                ftpFile.close()
                os.remove(tempDir+'/'+catFile)
                

