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

def listFD_new(url, prefix='', ext=''):
    page = requests.get(url).text
    #print page
    soup = BeautifulSoup(page, 'html.parser')
    list = [url + '/' + node.get('href') for node in soup.find_all('a') if ( node.get('href').startswith(prefix) and node.get('href').endswith(ext) )]
    return list

# User inputs
debug = 1
url = 'https://gpm-gv.gsfc.nasa.gov/Tier1/Files_07day/IMPACTS-WEST'
targetDirBase = '/home/disk/bob/impacts/gpm'
products = ['IMAGE_GPM_7DAY_IMPACTS-WEST']
file_ext = 'png'
catalogBaseDir = '/home/disk/funnel/impacts-website/archive/ops/gpm'
catalogFilePrefix = 'ops.gps'
catalogFileSuffix = ['overpass_west']

# go through each product
for i in range(0,len(products)):
    prod = products[i]
    suffix = catalogFileSuffix[i]
    if debug:
        print >>sys.stderr, "Processing ", prod
    
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
                    print >>sys.stderr, baseFileName," not in localFileList -- get file"
                try:
                    command = 'wget '+url+'/'+baseFileName
                    os.system(command)
                except Exception as e:
                    print sys.stderr, "    wget failed, exception: ", e
                    continue
            
                # rename file and copy to web server

                # create full file name
                newFileName = catalogFilePrefix+'.'+date+time+'.'+suffix+ext
                if debug:
                    print >>sys.stderr, "    newFileName = ", newFileName

                # check to make sure that web server path exists
                catalogDir = catalogBaseDir+'/'+date
                if not os.path.exists(catalogDir):
                    os.makedirs(catalogDir)

                # copy file to web server
                shutil.copy(targetDir+'/'+baseFileName,catalogDir+'/'+newFileName)
