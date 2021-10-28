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
date = '20200125'
vadUrl = 'https://har.gsfc.nasa.gov/storm/IMPACTS-2020/QLOOK_EXRAD-VAD_CRS-DOP'
targetDirBase = '/home/disk/bob/impacts/er2/EXRAD/vad/quicklooks'
file_ext = 'png'

# get list of files on server
# ***** NOTE: This doesn't work - permission problem?? *****
url = vadUrl+'/'+date+'/'
vadFList = listFD(url, file_ext)
    
if len(vadFList) == 0:
    if debug:
        print >>sys.stderr, "WARNING: no data on server for ", date

else:
    # make target directory, if necessary, and cd to it
    targetDir = targetDirBase+'/'+date
    if not os.path.exists(targetDir):
        os.makedirs(targetDir)
    os.chdir(targetDir)

    for idx,urlFileName in enumerate(urlFileList,0):
        #if debug:
        #    print >>sys.stderr, "  idx = ", idx
        #    print >>sys.stderr, "  urlFileName = ", urlFileName
        #    #print >>sys.stderr, "  urlDateList[",idx,"] = ", urlDateList[idx]
        #    #print >>sys.stderr, "  dateStr = ", dateStr

        try:
            command = 'wget '+wrfUrl+'/'+currentModelRun+'/'+urlFileName
            os.system(command)
        except Exception as e:
            print sys.stderr, "    wget failed, exception: ", e
            continue
