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
debug = 1
baseUrl = 'http://www.atmos.albany.edu/student/mbartolini/research/impacts/images/'
subDir = { 'mrr': {'mrr_ualb_cfads':'mrr_cfad','mrr_ualb_timeheight':'mrr'},
           'parsivel' : {'parsivel_mrr_ualb_timeseries':'mrr_parsivel_tseries','parsivel_ualb_psd_timeseries':'parsivel'} }
targetDirBase = '/home/disk/bob/impacts/radar/ualbany'
catalogBaseDir = '/home/disk/funnel/impacts-website/archive/research/ualbany'
ext = 'png'

# get yesterday's date
dateStr = datetime.strftime(datetime.now() - timedelta(1), '%Y%m%d')
if debug:
    print >>sys.stderr, "dateStr = ", dateStr

# define catalogDir
catalogDir = catalogBaseDir+'/'+dateStr
if not os.path.exists(catalogDir):
    os.makedirs(catalogDir)
    
for sd_id, sd_info in subDir.items():
    if debug:
        print >>sys.stderr, "subdir_id = ",sd_id
        print >>sys.stderr, "subdir_info = ",sd_info
    url = baseUrl+'/'+sd_id
    
    # get list of files at url
    urlFileList = []
    for file in listFD(url, ext):
        tmp = os.path.basename(file)
        (base,ext) = os.path.splitext(tmp)
        parts = base.split('_')
        if dateStr in parts:
            nameParts = parts[:-1]
            prefix = '_'
            prefix = prefix.join(nameParts)
            if prefix in sd_info.keys():
                urlFileList.append(base+ext)

    if len(urlFileList) == 0:
        if debug:
            print >>sys.stderr, "WARNING: no data of interest on server"
    else:
        # create targetDir and cd to it           
        targetDir = targetDirBase+'/'+sd_id
        if not os.path.exists(targetDir):
            os.makedirs(targetDir)
        os.chdir(targetDir)
        localFileList = os.listdir('.')
            
        for idx,urlFileName in enumerate(urlFileList,0):
            if debug:
                print >>sys.stderr, "  idx = ", idx
                print >>sys.stderr, "  urlFileName = ", urlFileName

            if urlFileName not in localFileList:
                if debug:
                    print >>sys.stderr, urlFileName,"    not in localFileList -- get file"
                try:
                    command = 'wget '+url+'/'+urlFileName
                    os.system(command)
                except Exception as e:
                    print sys.stderr, "    wget failed, exception: ", e
                    continue
                
                # rename file and move to web server
                # first get forecast_hour
                (base,ext) = os.path.splitext(urlFileName)
                product = base.replace('_'+dateStr,'')

                # create full file name
                newFileName = 'research.ualbany.'+dateStr+'.'+sd_info[product]+ext
                if debug:
                    print >>sys.stderr, "    newFileName = ", newFileName

                # copy file to web server
                shutil.copy(targetDir+'/'+urlFileName,catalogDir+'/'+newFileName)
