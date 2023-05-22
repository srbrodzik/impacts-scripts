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

# User inputs
debug = True
test = False
secsPerDay = 86400
#pastSecs = secsPerDay/12
pastSecs = secsPerDay/2
npolUrlBase = 'https://pmm-gv.gsfc.nasa.gov/pub/gpmarchive/Radar/NPOL/Newark/plots'
#PPI path format: npolUrlBase/YYYY/MM/DD/multi/PPI/NPOL_<YYYY>_<MMDD>_<hhmmss>_8panel_sw00_PPI.png
#RHI path format: npolUrlBase/YYYY/MM/DD/multi/RHI/NPOL_<YYYY>_<MMDD>_<hhmmss>_8panel_<aaa.a>AZ_RHI.png
targetDirBase = '/home/disk/bob/impacts/images/npol'
tempDir = '/tmp'
products = {'PPI':{'suffix':'ppi_8panel','extension':'png'},
            'RHI':{'suffix':'rhi_8panel','extension':'png'} }
file_ext = 'png'
catalogFilePrefix = 'radar.NPOL'

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

# get current time

# REAL TIME MODE
nowTime = time.gmtime()
now = datetime(nowTime.tm_year, nowTime.tm_mon, nowTime.tm_mday,
               nowTime.tm_hour, nowTime.tm_min, nowTime.tm_sec)
# ARCHIVE MODE
#now = datetime.strptime('202301050400','%Y%m%d%H%M')

nowDateStr = now.strftime("%Y%m%d")
nowTimeStr = now.strftime("%H%M%S")
nowDateTimeStr = nowDateStr+nowTimeStr
if debug:
    print("nowDateTimeStr =", nowDateTimeStr)

# compute start time
pastDelta = timedelta(0, pastSecs)
startTime = now - pastDelta
startDateStr = startTime.strftime("%Y%m%d")
startTimeStr = startTime.strftime("%H%M%S")
startDateTimeStr = startDateStr+startTimeStr
if debug:
    print("startDateTimeStr = ", startDateTimeStr)
 
# get dates of interest
dateStrList = []
if nowDateStr == startDateStr:
    dateStrList = [nowDateStr]
else:
    dateStrList = [startDateStr,nowDateStr]
if debug:
    print("dateStrList = ", dateStrList)
    
for idate in range(0,len(dateStrList)):
    date = dateStrList[idate]
    for prod in products:
        if debug:
            print("Processing", date, "for", prod, "data")

        # get list of files on server for this date and this product
        urlFileList = []
        npolUrl = npolUrlBase+'/'+date[0:4]+'/'+date[4:6]+'/'+date[6:8]+'/multi/'+prod
        get = requests.get(npolUrl)
        if get.status_code == 200:
            ext = 'png'
            for file in listFD(npolUrl, ext):
                tmp = os.path.basename(file)
                (base,ext) = os.path.splitext(tmp)
                (site,yyyy,mmdd,hhmmss,junk,junk,junk) = base.split('_')
                fileDateTimeStr = yyyy+mmdd+hhmmss
                if prod in tmp and fileDateTimeStr >= startDateTimeStr and fileDateTimeStr <= nowDateTimeStr:
                    urlFileList.append(tmp)
            if debug:
                print("urlFileList = ", urlFileList)
    
        if len(urlFileList) == 0:
            if debug:
                print("WARNING: ignoring date and product - no data on server")
                print("  for date   :", date)
                print("  for product:", prod)

        else:
            # make target directory, if necessary, and cd to it
            #targetDir = targetDirBase+'/'+dateHourStrList[i]+'/'+products[i]
            targetDir = targetDirBase+'/'+prod.lower()+'/'+date
            if not os.path.exists(targetDir):
                os.makedirs(targetDir)
            os.chdir(targetDir)

            # get local file list - i.e. those which have already been downloaded
            localFileList = os.listdir('.')

            for idx,urlFileName in enumerate(urlFileList,0):
                if debug:
                    print("  idx =", idx,"and urlFileName =", urlFileName)

                if urlFileName not in localFileList:
                    if debug:
                        print("    ",urlFileName,"not in localFileList -- get file")
                    try:
                        command = 'wget '+npolUrl+'/'+urlFileName
                        os.system(command)
                    except Exception as e:
                        print("    wget failed, exception: ", e)
                        continue

                    # rename file and move to targetDir
                    if prod == 'PPI':
                        # NPOL_<YYYY>_<MMDD>_<hhmmss>_8panel_sw00_PPI.png
                        (base,ext) = os.path.splitext(urlFileName)
                        (site,year,mmdd,time,junk,junk,junk,) = base.split('_')
                        newFileDateTime = year+mmdd+time[0:4]
                    elif prod == 'RHI':
                        # NPOL_<YYYY>_<MMDD>_<hhmmss>_8panel_<aaa.a>AZ_RHI.png
                        (base,ext) = os.path.splitext(urlFileName)
                        (site,year,mmdd,time,junk,azStr,junk) = base.split('_')
                        newFileDateTime = year+mmdd+time[0:4]

                    # create full file name
                    catalogName = catalogFilePrefix+'.'+newFileDateTime+'.'+products[prod]['suffix']+ext
                    if debug:
                        print("    catalogName = ", catalogName)

                    # copy file to tempDir and rename
                    shutil.copy(targetDir+'/'+urlFileName,tempDir+'/'+catalogName)

                    # ftp file to catalog location
                    os.chdir(tempDir)
                    ftpFile = open(os.path.join(tempDir,catalogName),'rb')
                    catalogFTP.storbinary('STOR '+catalogName,ftpFile)
                    ftpFile.close()
                    os.chdir(targetDir)
                    if debug:
                        print('ftpd',catalogName,'to NCAR FC')

                    # remove file from tempDir
                    os.remove(os.path.join(tempDir,catalogName))

# Close ftp connection
catalogFTP.quit()
