#!/usr/bin/python

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

# User inputs
debug = 0
debug2 = 1
secsPerDay = 86400
pastSecs = secsPerDay
secsPerRun = secsPerDay/4
deltaBetweenForecastHours = [1,3]  # 1 for files 1-36, 3 for files 37-52
lastForecastHour = 84
namUrl = 'https://tropicaltidbits.com/analysis/models/namconus'
targetDirBase = '/home/disk/bob/impacts/model/nam_12km'
products = ['ref_frzn_us','temp_adv_fgen_700_us','z500_vort_us','uv250_us','T2m_us']
has_anal_prod = [0,1,1,1,1]
catalogBaseDir = '/home/disk/funnel/impacts-website/archive/model/nam_12km'

# get model date and time closest to current time
nowTime = time.gmtime()
now = datetime(nowTime.tm_year, nowTime.tm_mon, nowTime.tm_mday,
               nowTime.tm_hour, nowTime.tm_min, nowTime.tm_sec)
nowDateStr = now.strftime("%Y%m%d")
nowHourStr = now.strftime("%H")
if nowHourStr >= '00' and nowHourStr < '06':
    lastModelDateTimeStr = nowDateStr+'00'
elif nowHourStr >= '06' and nowHourStr < '12':
    lastModelDateTimeStr = nowDateStr+'06'
elif nowHourStr >= '12' and nowHourStr < '18':
    lastModelDateTimeStr = nowDateStr+'12'
elif nowHourStr >= '18':
    lastModelDateTimeStr = nowDateStr+'18'
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
nRuns = ((pastSecs / secsPerDay) * 4) + 1
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
    for i in range(0,len(products)):
        if debug:
            print >>sys.stderr, "Processing ", currentModelRun, " run for ", products[i], " data"

        # get list of files on server for this run and this product
        # only interested in forecasts up to and including 'lastForecastHour'
        urlFileList = []
        #urlDateList = []
        #urlDateTimeList = []
        url = namUrl+'/'+dateHourStrList[t]+'/'
        ext = 'png'
        for file in listFD(url, ext):
            tmp = os.path.basename(file)
            (base,ext) = os.path.splitext(tmp)
            parts = base.split('_')
            forecast_num = parts[-1]
            if len(forecast_num) < 2:
                forecast_num = '0'+forecast_num
            if has_anal_prod[i]:
                #last_forecast_num = str(lastForecastHour/deltaBetweenForecastHours + 1)
                last_forecast_num = '53'
            else:
                #last_forecast_num = str(lastForecastHour/deltaBetweenForecastHours)
                last_forecast_num = '52'
            if products[i] in tmp and forecast_num <= last_forecast_num:
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
            #localFileList.reverse()
            #if debug:
            #    print >>sys.stderr, "  localFileList: ", localFileList

            # get url file list (not sure I need this)
            #urlFileList.sort()
            #urlFileList.reverse()

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
                        command = 'wget '+namUrl+'/'+currentModelRun+'/'+urlFileName
                        os.system(command)
                    except Exception as e:
                        print sys.stderr, "    wget failed, exception: ", e
                        continue

                    # rename file and move to web server
                    # first get forecast_hour
                    (base,ext) = os.path.splitext(urlFileName)
                    parts = base.split('_')
                    if debug2:
                        print >>sys.stderr, "base      = ", base
                        print >>sys.stderr, "   parts[-1] = ", parts[-1]
                    if has_anal_prod[i]:
                        if int(parts[-1]) <= 37:
                            forecast_hour = str( (int(parts[-1])-1) * deltaBetweenForecastHours[0])
                        else:
                            forecast_hour = str(36 + ( (int(parts[-1]) - 37) * deltaBetweenForecastHours[1] ) )
                        if debug2:
                            print >>sys.stderr, "   has_anal_prod: forecast_hour = ", forecast_hour
                    else:
                        if int(parts[-1]) <= 36:
                            forecast_hour = str(int(parts[-1])*deltaBetweenForecastHours[0])
                        else:
                            forecast_hour = str(36 + ( (int(parts[-1]) - 36) * deltaBetweenForecastHours[1] ) )
                        if debug2:
                            print >>sys.stderr, "   no_anal_prod: forecast_hour = ", forecast_hour
                    if len(forecast_hour) == 1:
                        forecast_hour = '0'+forecast_hour
                    if debug:
                        print >>sys.stderr, "    forecast_hour = ", forecast_hour

                    # only copy three hourly files to web server
                    if not (int(forecast_hour) % 3):
                        
                        # create full file name
                        newFileName = 'model.nam_12km.'+currentModelRun+'00.'+forecast_hour+'_'+products[i]+'.png'
                        if debug:
                            print >>sys.stderr, "    newFileName = ", newFileName

                        # check to make sure that web server path exists
                        catalogDir = catalogBaseDir+'/'+dateStrList[t]
                        if not os.path.exists(catalogDir):
                            os.makedirs(catalogDir)

                        # copy file to web server
                        shutil.copy(targetDir+'/'+urlFileName,catalogDir+'/'+newFileName)






    

                              
