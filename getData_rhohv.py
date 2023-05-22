#!/usr/bin/python3

import os
import shutil
import time
import datetime
from datetime import timedelta
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import shutil

def listFD(url, ext=''):
    page = requests.get(url).text
    soup = BeautifulSoup(page, 'html.parser')
    return [url + '/' + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]

def listDD(url, ext=''):
    page = requests.get(url).text
    soup = BeautifulSoup(page, 'html.parser')
    return [url + '/' + node.get('href') for node in soup.find_all('a')]

#url = 'https://mrms.ncep.noaa.gov/data/2D/MergedBaseReflectivityQC'
#localDirBase = '/home/disk/bob/impacts/raw/mrms/fillGaps/2DBaseReflQC'
#dateList = {'20230111':{'stime':'101412','etime':'161017'}}

#url = 'https://mrms.ncep.noaa.gov/data/2D/MergedReflectivityComposite'
#localDirBase = '/home/disk/bob/impacts/raw/mrms/fillGaps/2DReflComp'
#dateList = {'20230111':{'stime':'101437','etime':'162232'}}

#url = 'https://mrms.ncep.noaa.gov/data/3DRefl'
#localDirBase = '/home/disk/bob/impacts/raw/mrms/fillGaps/3DRefl'
#dateList = {'20230111':{'stime':'101235','etime':'162232'}}

url = 'https://mrms.ncep.noaa.gov/data/3DRhoHV'
localDirBase = '/home/disk/bob/impacts/raw/mrms/fillGaps/3DRhoHV'
dateList = {'20230111':{'stime':'101038','etime':'162534'}}

#url = 'https://mrms.ncep.noaa.gov/data/3DZdr'
#localDirBase = '/home/disk/bob/impacts/raw/mrms/fillGaps/3DZdr'
#dateList = {'20230111':{'stime':'101038','etime':'162534'}}

#url = 'https://mrms.ncep.noaa.gov/data/3DMergedBaseReflectivityQC'
#localDirBase = '/home/disk/bob/impacts/raw/mrms/fillGaps/Kdp'
#dateList = {'20230111':{'stime':'101038','etime':'162533'}}

#url = 'https://mrms.ncep.noaa.gov/data/3DMergedBaseReflectivityQC'
#localDirBase = '/home/disk/bob/impacts/raw/mrms/fillGaps/SPW'
#dateList = {'20230111':{'stime':'101038','etime':'163533'}}

ext = 'gz'

os.chdir(localDirBase)

for date in dateList.keys() :
    s_datetime = date+dateList[date]['stime']
    e_datetime = date+dateList[date]['etime']

    if '3D' in url:
        subdirs = listDD(url)
        for sd in subdirs:
            if 'Merged' in sd:
                for file in listFD(sd, ext):
                    print(file)
                    if file.endswith('grib2.gz') and 'latest' not in file:
                        tmp = os.path.basename(file)
                        (base,ext) = os.path.splitext(tmp)
                        (base2,ext2) = os.path.splitext(base)
                        (junk,junk,junk,dateTimeStr) = base2.split('_')
                        (fdate,ftime) = dateTimeStr.split('-')
                        fdatetime = fdate+ftime
                        if fdatetime > s_datetime and fdatetime < e_datetime:
                            command = 'wget '+file
                            os.system(command)


    elif '2D' in url:
    
        for file in listFD(url, ext):
            print(file)
            if file.endswith('grib2.gz') and 'latest' not in file:
                tmp = os.path.basename(file)
                (base,ext) = os.path.splitext(tmp)
                (base2,ext2) = os.path.splitext(base)
                (junk,junk,junk,dateTimeStr) = base2.split('_')
                (fdate,ftime) = dateTimeStr.split('-')
                fdatetime = fdate+ftime
                if fdatetime > s_datetime and fdatetime < e_datetime:
                    command = 'wget '+file
                    os.system(command)



