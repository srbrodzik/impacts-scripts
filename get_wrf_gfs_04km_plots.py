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

def listFD_new(url, prefix='', ext='', substr=''):
    page = requests.get(url).text
    #print page
    soup = BeautifulSoup(page, 'html.parser')
    #list = [url + '/' + node.get('href') for node in soup.find_all('a') if ( node.get('href').endswith(ext) and substr in node.get('href') )]
    list = [url + '/' + node.get('href') for node in soup.find_all('a') if ( node.get('href').startswith(prefix) and node.get('href').endswith(ext) and substr in node.get('href') )]
    return list

# User inputs
debug = 1
test = 0
secsPerDay = 86400
pastSecs = secsPerDay/2
secsPerRun = secsPerDay/2
deltaBetweenForecastHours = 1
last_forecast_num = 18
wrfUrl = 'http://itpa.somas.stonybrook.edu/sbuwrf'
targetDirBase = '/home/disk/bob/impacts/model/wrf_gfs_04km'
#filename format: <initModel>.<product>.<domain>.<fcasthour>.<file_ext>
initModel = 'GFS'
domain = 'd03'
products = {'refl_10cm':{'suffix':'refl_preciptype_mslp_wind','has_anal_prod':1},
            'temps_sfc':{'suffix':'T2m_mslp_uv10m','has_anal_prod':1},
            'pcp3':{'suffix':'3hr_precip','has_anal_prod':0},
            '850_dBZfronto':{'suffix':'850hPa_ht_fronto_refl','has_anal_prod':1},
            '700_dBZfronto':{'suffix':'700hPa_ht_fronto_refl','has_anal_prod':1},
            '500_avo':{'suffix':'500hPa_wind_ht_vort','has_anal_prod':1}}
file_ext = 'gif'
tempDir = '/tmp'
catalogPrefix = 'model.WRF_GFS_SBU_04km'

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
nowDateStr = now.strftime("%Y%m%d")
nowHourStr = now.strftime("%H")
#nowDateStr = '20200104'
#nowHourStr = '13'
if nowHourStr < '12':
    lastModelHourStr = '00'
else:
    lastModelHourStr = '12'
lastModelDateTimeStr = nowDateStr+lastModelHourStr
if debug:
    print("lastModelDateTimeStr = ", lastModelDateTimeStr)

# compute start time
pastDelta = timedelta(0, pastSecs)
lastModelDateTime = datetime.strptime(lastModelDateTimeStr,'%Y%m%d%H')
startTime = lastModelDateTime - pastDelta
startDateHourStr = startTime.strftime("%Y%m%d%H")
startDateStr = startTime.strftime("%Y%m%d")
if debug:
    print("startDateHourStr = ", startDateHourStr)

# set up list of model runs to be checked
nRuns = int((pastSecs / secsPerRun) + 1)
dateStrList = []
dateHourStrList = []
for iRun in range(0, nRuns):
    deltaSecs = timedelta(0, iRun * secsPerRun)
    dayTime = lastModelDateTime - deltaSecs
    dateStr = dayTime.strftime("%Y%m%d")
    dateHourStr = dayTime.strftime("%Y%m%d%H")
    dateStrList.append(dateStr)
    dateHourStrList.append(dateHourStr)
if debug:
    print("dateHourStrList = ", dateHourStrList)

for t in range(0,nRuns):
    currentModelRun = dateHourStrList[t]
    
    # get list of files on server for this run
    url = wrfUrl+'/'+currentModelRun+'/'
    #currentModelFList = listFD_new(url, file_ext, domain)
    currentModelFList = listFD_new(url, initModel, file_ext, domain)

    # go through each product
    for prod in products:
        if debug:
            print("Processing", currentModelRun, "run for", prod, "data")

        # only interested in forecasts up to and including 'lastForecastHour'
        urlFileList = []
        for file in currentModelFList:
            tmp = os.path.basename(file)
            (base,ext) = os.path.splitext(tmp)
            parts = base.split('.')
            forecast_num = parts[-1]
            if len(forecast_num) == 2:
                if prod in tmp and int(forecast_num) <= int(float(last_forecast_num)):
                    urlFileList.append(tmp)
        #if debug:
        #    print("urlFileList = ", urlFileList)
    
        if len(urlFileList) == 0:
            if debug:
                print("WARNING: ignoring run and product - no data on server")
                print("  for model run time: ", currentModelRun)
                print("  for product       : ", prod)

        else:
            # make target directory, if necessary, and cd to it
            #targetDir = targetDirBase+'/'+dateHourStrList[i]+'/'+products[i]
            targetDir = targetDirBase+'/'+currentModelRun
            if not os.path.exists(targetDir):
                os.makedirs(targetDir)
            os.chdir(targetDir)

            # get local file list - i.e. those which have already been downloaded
            localFileList = os.listdir('.')
            #if debug:
            #    print >>sys.stderr, "  localFileList: ", localFileList

            # loop through the url file list, downloading those that have
            # not yet been downloaded
            #if debug:
            #    print >>sys.stderr, "Starting to loop through url file list"
            
            for idx,urlFileName in enumerate(urlFileList,0):
                #if debug:
                #    print("  idx = ", idx)
                #    print("  urlFileName = ", urlFileName)
                #    #print("  urlDateList[",idx,"] = ", urlDateList[idx])
                #    #print("  dateStr = ", dateStr)

                if urlFileName not in localFileList:
                    #if debug:
                    #    print("    ",urlFileName,"not in localFileList -- get file")
                    try:
                        command = 'wget '+wrfUrl+'/'+currentModelRun+'/'+urlFileName
                        os.system(command)
                    except Exception as e:
                        print("    wget failed, exception: ", e)
                        continue

                    # rename file and ftp to catalog server
                    # first get forecast_hour
                    (base,ext) = os.path.splitext(urlFileName)
                    parts = base.split('.')
                    forecast_hour = parts[-1]
                    #if products[prod]['has_anal_prod']:
                    #    forecast_hour = str( (int(parts[-1])-1) * deltaBetweenForecastHours)
                    #else:
                    #    forecast_hour = str(int(parts[-1])*deltaBetweenForecastHours)
                    #if len(forecast_hour) == 1:
                    #    forecast_hour = '0'+forecast_hour
                    #if debug:
                    #    print("    forecast_hour = ", forecast_hour)

                    # create full file name
                    if len(forecast_hour) == 1:
                        forecast_hour = '00'+forecast_hour
                    elif len(forecast_hour) == 2:
                        forecast_hour = '0'+forecast_hour
                    catalogName = catalogPrefix+'.'+currentModelRun+'00.'+forecast_hour+'_'+products[prod]['suffix']+ext
                    #if debug:
                    #    print("    catalogName = ", catalogName)

                    # copy file to tempDir and rename
                    shutil.copy(targetDir+'/'+urlFileName,
                                tempDir+'/'+catalogName)

                    # ftp file to catalog location
                    ftpFile = open(os.path.join(tempDir,catalogName),'rb')
                    catalogFTP.storbinary('STOR '+catalogName,ftpFile)
                    ftpFile.close()

                    # remove file from tempDir
                    os.remove(os.path.join(tempDir,catalogName))

# Close ftp connection
catalogFTP.quit()
                   
