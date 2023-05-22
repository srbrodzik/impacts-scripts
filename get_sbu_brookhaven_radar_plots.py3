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

def listFD(url, ext=''):
    page = requests.get(url).text
    #print page
    soup = BeautifulSoup(page, 'html.parser')
    return [url + '/' + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]

def listFD_new(url, prefix='', ext='', substr=''):
    page = requests.get(url).text
    #print page
    soup = BeautifulSoup(page, 'html.parser')
    #list = [url + '/' + node.get('href') for node in soup.find_all('a') if ( node.get('href').endswith(ext) and substr in node.get('href') )]
    list = [url + '/' + node.get('href') for node in soup.find_all('a') if ( node.get('href').startswith(prefix) and node.get('href').endswith(ext) and substr in node.get('href') )]
    return list

# User inputs
debug = True
test = False
secsPerDay = 86400
pastSecs = secsPerDay*2

# Raw file naming conventions
# http://doppler.somas.stonybrook.edu/IMPACTS/BNL/[instrument name]/images/quicklooks/
#       mrrprowhite_realtime_<YYYYMMDD>.png
#       mwrmp3000A_<YYYYMMDD>.png
#       parsivel_realtime_<YYYYMMDD>.png
#       pluvio_<YYYYMMDD>.png
#       cl51_<YYYYMMDD>.png
#    	WACR_<YYYYMMDD-<hhmmss>-<YYYYMMDD>-<hhmmss>.png	

# FC Naming Conventions
# radar.MRR.<datetime>.Brookhaven_NY_time_ht.png
# upperair.MWR.<datetime>.Brookhaven_NY.png
# surface.Parsivel.202003050000.Brookhaven_NY.png
# surface.Pluvio.<datetime>.Brookhaven_NY.png
# lidar.Ceilometer.202003050000.Brookhaven_NY_15000m.png
# radar.WACR.<datetime>.Brookhaven_NY_time_ht.png

#baseUrl = 'https://doppler.somas.stonybrook.edu/ARCHIVE/IMAGES'
baseUrl = 'https://doppler.somas.stonybrook.edu/IMPACTS/BNL'
urlLoginData = {'identifiant':'DataAccess',
                'motdepasse':'WinterAtSBU'}
products   = {'mrrpro2white':{'prefix':'mrrprowhite_realtime','catPrefix':'radar','catPlatform':'MRR','catProduct':'Brookhaven_NY_time_ht'},
              'mwr-mp3000a':{'prefix':'mwrmp3000A','catPrefix':'upperair','catPlatform':'MWR','catProduct':'Brookhaven_NY'},
              'parsivel':{'prefix':'parsivel_realtime','catPrefix':'surface','catPlatform':'Parsivel','catProduct':'Brookhaven_NY'},
              'pluvio':{'prefix':'pluvio','catPrefix':'surface','catPlatform':'Pluvio','catProduct':'Brookhaven_NY'},
              'vceilo15k':{'prefix':'cl51','catPrefix':'lidar','catPlatform':'Ceilometer','catProduct':'Brookhaven_NY_15000m'},
              'wcr':{'prefix':'WACR','catPrefix':'radar','catPlatform':'WACR','catProduct':'Brookhaven_NY_time_ht'}}
file_ext = 'png'
localDirBase = '/home/disk/bob/impacts/radar/sbu_images'

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
                        
# get current date
nowTime = time.gmtime()
now = datetime(nowTime.tm_year, nowTime.tm_mon, nowTime.tm_mday,
               nowTime.tm_hour, nowTime.tm_min, nowTime.tm_sec)
nowDateStr = now.strftime("%Y%m%d")
if debug:
    print('nowDateStr = ', nowDateStr)

# compute list of dates to check
pastDelta = timedelta(0, pastSecs)
startTime = now - pastDelta
startDateStr = startTime.strftime("%Y%m%d")
if debug:
    print('startDateStr = ', startDateStr)

# set up dates to be checked
nDates = int((pastSecs / secsPerDay) + 1)
dateStrList = []
for iDate in range(0, nDates):
    deltaSecs = timedelta(0, iDate * secsPerDay)
    dayTime = now - deltaSecs
    dateStr = dayTime.strftime("%Y%m%d")
    dateStrList.append(dateStr)
if debug:
    print('dateStrList = ', dateStrList)

for idate in range(0,nDates):
    currentDate = dateStrList[idate]
    currentYear = currentDate[0:4]

    # go through each product
    for prod in products:
        if debug:
            print('Processing', currentDate, 'for', prod, 'data')

        localDir = localDirBase+'/'+prod+'/'+currentDate
        if not os.path.isdir(localDir):
            os.makedirs(localDir)
        os.chdir(localDir)

        urlFile = products[prod]['prefix']+'_'+currentDate+'.'+file_ext
        url = baseUrl+'/'+prod+'/images/quicklooks/'+urlFile
        catFile = products[prod]['catPrefix']+'.'+products[prod]['catPlatform']+'.'+currentDate+'0000.'+products[prod]['catProduct']+'.'+file_ext
        #get = requests.get(url)
        if get.status_code == 200:
            
            catName = catFilePrefix[iprod]+'.'+catPlatform[iprod]+'.'+currentDate+'0000.'+catProduct[iprod]+'.'+file_ext

            if os.path.isfile(localDir+'/'+catName):
                continue
            else:
                try:
                    command = 'wget '+url
                    os.system(command)
                    shutil.move(localDir+'/'+urlFile,
                                localDir+'/'+catName)
                except Exception as e:
                    print('    wget failed, exception: ', e)
                    continue

                ftpFile = open(localDir+'/'+catName,'rb')
                catalogFTP.storbinary('STOR '+catName,ftpFile)
                ftpFile.close()

        else:
            print('url =',url,'does not exist')
            
# Close ftp connection
catalogFTP.quit()

