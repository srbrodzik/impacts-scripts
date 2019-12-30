#!/usr/bin/python

import os
import sys
import time
from datetime import timedelta
from datetime import datetime
import shutil

# User inputs
debug = 1
secsPerDay = 86400
pastSecs = secsPerDay*2
deltaBetweenForecastHours = 1
base_url = 'https://doppler.somas.stonybrook.edu/ARCHIVE/IMAGES/RadarTruck'
url_subdirs = ['CHM15K','AirmarWeather','MRRPRO','Parsivel']
#filename format: <product>_YYYYMMDD.png
products         = ['chm15k','airmar','mrrpro','parsivel']
products_catalog = ['ceil150','met_station','mrr_pro','parsivel']
file_ext = 'png'
catalogBaseDir = '/home/disk/funnel/impacts-website/archive/research/stonybrookmobile'
catalogFilePrefix = 'research'
site = 'stonybrookmobile'

# get current date
nowTime = time.gmtime()
now = datetime(nowTime.tm_year, nowTime.tm_mon, nowTime.tm_mday,
               nowTime.tm_hour, nowTime.tm_min, nowTime.tm_sec)
nowDateStr = now.strftime("%Y%m%d")
if debug:
    print >>sys.stderr, "nowDateStr = ", nowDateStr

# compute list of dates to check
pastDelta = timedelta(0, pastSecs)
startTime = now - pastDelta
startDateStr = startTime.strftime("%Y%m%d")
if debug:
    print >>sys.stderr, "startDateStr = ", startDateStr

# set up list of model runs to be checked
nDates = (pastSecs / secsPerDay) + 1
dateStrList = []
for iDate in range(0, nDates):
    deltaSecs = timedelta(0, iDate * secsPerDay)
    dayTime = now - deltaSecs
    dateStr = dayTime.strftime("%Y%m%d")
    dateStrList.append(dateStr)
if debug:
    print >>sys.stderr, "dateStrList = ", dateStrList

for t in range(0,nDates):
    currentDate = dateStrList[t]
    currentYear = currentDate[0:4]

    # make date dir in catalog
    catalogDir = catalogBaseDir+'/'+currentDate
    if not os.path.exists(catalogDir):
        os.makedirs(catalogDir)
    os.chdir(catalogDir)

    # go through each product
    for i in range(0,len(products)):
        if debug:
            print >>sys.stderr, "Processing ", currentDate, " for ", products[i], " data"

        url_file = products[i]+'_'+currentDate+'.'+file_ext
        url = base_url+'/'+url_subdirs[i]+'/'+currentYear+'/'+url_file
        cat_fname = catalogFilePrefix+'.'+site+'.'+currentDate+'0000.'+products_catalog[i]+'.'+file_ext

        if os.path.isfile(cat_fname):
            continue
        else:
            try:
                command = 'wget '+url
                os.system(command)
                shutil.move(url_file,cat_fname)
            except Exception as e:
                print sys.stderr, "    wget failed, exception: ", e
                continue

