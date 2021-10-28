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

def listFD_new(url, prefix='', ext='', substr=''):
    page = requests.get(url).text
    #print page
    soup = BeautifulSoup(page, 'html.parser')
    list = [url + '/' + node.get('href') for node in soup.find_all('a') if ( node.get('href').startswith(prefix) and node.get('href').endswith(ext) and substr in node.get('href') )]
    return list

# User inputs
debug = 1
secsPerDay = 86400
pastSecs = secsPerDay*2
deltaBetweenForecastHours = 1
base_url = 'https://doppler.somas.stonybrook.edu/ARCHIVE/IMAGES'
url_subdirs = ['MWR','PLUVIO','ROGER','SOLARTRACKER']
#filename format: <product>_YYYYMMDD.png
products         = ['mwr','pluvio','roger','solartracker']
products_catalog = ['mwr','pluvio','roger','solar_tracker']
file_ext = 'png'
catalogBaseDir = '/home/disk/funnel/impacts-website/archive/research/stonybrook'
catalogFilePrefix = 'research'
site = 'stonybrook'

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
        try:
            command = 'wget '+url
            os.system(command)
            cat_fname = catalogFilePrefix+'.'+site+'.'+currentDate+'0000.'+products[i]+'.'+file_ext
            if os.path.isfile(cat_fname):
                os.remove(url_file)
            else:
                shutil.move(url_file,cat_fname)
        except Exception as e:
            print sys.stderr, "    wget failed, exception: ", e
            continue

