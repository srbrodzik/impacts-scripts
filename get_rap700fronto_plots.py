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

def listFD_new(url, prefix='', ext=''):
    page = requests.get(url).text
    #print page
    soup = BeautifulSoup(page, 'html.parser')
    list = [url + '/' + node.get('href') for node in soup.find_all('a') if ( node.get('href').startswith(prefix) and node.get('href').endswith(ext) )]
    return list

# User inputs
debug = 1
url = 'https://climate.cod.edu/data/mesoanalysis'
targetDirBase = '/home/disk/bob/impacts/model/rap700fronto'
products = ['rap700fronto']
file_ext = 'gif'
catalogBaseDir = '/home/disk/funnel/impacts-website/archive/ops/upper_air'
catalogFilePrefix = 'ops.upper_air'
catalogFileSuffix = ['700mb_fronto']

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
        (prefix,date,hour) = base.split('.')
    
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
            newFileName = catalogFilePrefix+'.'+date+hour+'00.'+suffix+ext
            if debug:
                print >>sys.stderr, "    newFileName = ", newFileName

            # check to make sure that web server path exists
            catalogDir = catalogBaseDir+'/'+date
            if not os.path.exists(catalogDir):
                os.makedirs(catalogDir)

            # copy file to web server
            shutil.copy(targetDir+'/'+baseFileName,catalogDir+'/'+newFileName)
