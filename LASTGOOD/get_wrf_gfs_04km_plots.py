import os
import sys
import time
from datetime import timedelta
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import shutil

def listFD(url, ext=''):
    page = requests.get(url).text
    #print page
    soup = BeautifulSoup(page, 'html.parser')
    return [url + '/' + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]

def listFD_new(url, prefix='', ext='', substr=''):
    page = requests.get(url).text
    #print page
    soup = BeautifulSoup(page, 'html.parser')
    list = [url + '/' + node.get('href') for node in soup.find_all('a') if ( node.get('href').startswith(prefix) and node.get('href').endswith(ext) and substr in node.get('href') )]
    return list

# User inputs
debug = 1
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
products = ['refl_10cm','temps_sfc','pcp3','850_dBZfronto','700_dBZfronto','500_avo']
file_ext = 'gif'
has_anal_prod = [1,1,0,1,1,1]
catalogBaseDir = '/home/disk/funnel/impacts-website/archive/model/wrf_gfs_04km'
catalogFilePrefix = 'model.wrf_gfs_04km'

# get model date and time closest to current time
nowTime = time.gmtime()
now = datetime(nowTime.tm_year, nowTime.tm_mon, nowTime.tm_mday,
               nowTime.tm_hour, nowTime.tm_min, nowTime.tm_sec)
nowDateStr = now.strftime("%Y%m%d")
nowHourStr = now.strftime("%H")
#nowDateStr = '20200108'
#nowHourStr = '13'
if nowHourStr < '12':
    lastModelHourStr = '00'
else:
    lastModelHourStr = '12'
lastModelDateTimeStr = nowDateStr+lastModelHourStr
if debug:
    print >>sys.stderr, "lastModelDateTimeStr = ", lastModelDateTimeStr

# compute start time
pastDelta = timedelta(0, pastSecs)
lastModelDateTime = datetime.strptime(lastModelDateTimeStr,'%Y%m%d%H')
startTime = lastModelDateTime - pastDelta
startDateHourStr = startTime.strftime("%Y%m%d%H")
startDateStr = startTime.strftime("%Y%m%d")
if debug:
    print >>sys.stderr, "startDateHourStr = ", startDateHourStr

# set up list of model runs to be checked
nRuns = (pastSecs / secsPerRun) + 1
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
    print >>sys.stderr, "dateHourStrList = ", dateHourStrList

for t in range(0,nRuns):
    currentModelRun = dateHourStrList[t]
    
    # get list of files on server for this run
    url = wrfUrl+'/'+currentModelRun+'/'
    #currentModelFList = listFD_new(url, file_ext, domain)
    currentModelFList = listFD_new(url, initModel, file_ext, domain)

    # go through each product
    for i in range(0,len(products)):
        if debug:
            print >>sys.stderr, "Processing ", currentModelRun, " run for ", products[i], " data"

        # only interested in forecasts up to and including 'lastForecastHour'
        urlFileList = []
        for file in currentModelFList:
            tmp = os.path.basename(file)
            (base,ext) = os.path.splitext(tmp)
            parts = base.split('.')
            forecast_num = parts[-1]
            if len(forecast_num) == 2:
                if products[i] in tmp and int(forecast_num) <= int(last_forecast_num):
                    urlFileList.append(tmp)
        #if debug:
        #    print >>sys.stderr, "urlFileList = ", urlFileList
    
        if len(urlFileList) == 0:
            if debug:
                print >>sys.stderr, "WARNING: ignoring run and product - no data on server"
                print >>sys.stderr, "  for model run time: ", currentModelRun
                print >>sys.stderr, "  for product       : ", products[i]

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
            if debug:
                print >>sys.stderr, "Starting to loop through url file list"
            
            for idx,urlFileName in enumerate(urlFileList,0):
                if debug:
                    print >>sys.stderr, "  idx = ", idx
                    print >>sys.stderr, "  urlFileName = ", urlFileName
                    #print >>sys.stderr, "  urlDateList[",idx,"] = ", urlDateList[idx]
                    #print >>sys.stderr, "  dateStr = ", dateStr

                if urlFileName not in localFileList:
                    if debug:
                        print >>sys.stderr, urlFileName,"    not in localFileList -- get file"
                    try:
                        command = 'wget '+wrfUrl+'/'+currentModelRun+'/'+urlFileName
                        os.system(command)
                    except Exception as e:
                        print sys.stderr, "    wget failed, exception: ", e
                        continue

                    # rename file and move to web server
                    # first get forecast_hour
                    (base,ext) = os.path.splitext(urlFileName)
                    parts = base.split('.')
                    forecast_hour = parts[-1]
                    #if has_anal_prod[i]:
                    #    forecast_hour = str( (int(parts[-1])-1) * deltaBetweenForecastHours)
                    #else:
                    #    forecast_hour = str(int(parts[-1])*deltaBetweenForecastHours)
                    #if len(forecast_hour) == 1:
                    #    forecast_hour = '0'+forecast_hour
                    if debug:
                        print >>sys.stderr, "    forecast_hour = ", forecast_hour

                    # create full file name
                    newFileName = catalogFilePrefix+'.'+currentModelRun+'00.'+forecast_hour+'_'+products[i]+ext
                    if debug:
                        print >>sys.stderr, "    newFileName = ", newFileName

                    # check to make sure that web server path exists
                    catalogDir = catalogBaseDir+'/'+dateStrList[t]
                    if not os.path.exists(catalogDir):
                        os.makedirs(catalogDir)

                    # copy file to web server
                    shutil.copy(targetDir+'/'+urlFileName,catalogDir+'/'+newFileName)
