#!/usr/bin/python3

import os
import shutil
from datetime import datetime
from datetime import timedelta
import time
import requests

targetDirBase = '/home/disk/bob/impacts/radar/uconn'
tempDir = '/tmp'
# set startFlag
#    0 -> start now
#    1 -> start at startDate
startFlag = 0
startDate = '20230116'
startTime = '0000'
# set number of days to go back from startDate
num_days = 2
secsPerDay = 86400

urlBase = 'https://wallops-prf.gsfc.nasa.gov/Field_Campaigns/IMPACTS_2023'
# MRR6path: urlBase/MRR/MRRPRO-06/CDF/Daily/YYYY/UCONN_D3R_MRRPRO-06_YYYY_MMDD.nc.gz
# MRR7path: urlBase/MRR/MRRPRO-07/CDF/Daily/YYYY/UCONN_GAIL_MRRPRO-07_YYYY_MMDD.nc.gz

products = {'MRRPRO-06':{'subpath':'MRR/MRRPRO-06/CDF/Daily','prefix':'UCONN_D3R_MRRPRO-06', 'saveSubPath':'nasa_d3r'},
            'MRRPRO-07':{'subpath':'MRR/MRRPRO-07/CDF/Daily','prefix':'UCONN_GAIL_MRRPRO-07','saveSubPath':'nasa_gail'} }

# NOT SURE HOW TO ACCESS THIS:
# GaugePath: urlBase/????/2A56_IMPACTS_2023

# Get start date
if startFlag == 0:
    nowStr = datetime.strftime(datetime.now() - timedelta(1), '%Y%m%d')
    now = datetime.strptime(nowStr,'%Y%m%d')
else:
    nowDateStr = startDate
    now = datetime.strptime(nowDateStr,'%Y%m%d')

# Get todays date
nowDateStr = now.strftime("%Y%m%d")
print(nowDateStr)

# Make list of dates to process
dateStrList = []
for idate in range(0,num_days):
    deltaSecs = timedelta(0, idate * secsPerDay)
    nextDate = now - deltaSecs
    nextDateStr = nextDate.strftime("%Y%m%d")
    dateStrList.append(nextDateStr)
print('dateStrList = ',dateStrList)
   
for idate in dateStrList:

    print('date =',idate)

    year = idate[0:4]
    month = idate[4:6]
    day = idate[6:8]
    year_mmdd = year+'_'+month+day

    for prod in products.keys():

        print('prod =',prod)

        # Change to targetDir
        targetDir = targetDirBase+'/'+products[prod]['saveSubPath']
        if not os.path.isdir(targetDir):
            os.makedirs(targetDir)
        targetFileList = os.listdir(targetDir)
        os.chdir(targetDir)

        # get prod data file names and download data
        dataFileBase = products[prod]['prefix']+'_'+year+'_'+month+day
        dataFile = dataFileBase+'.nc.gz'
        if dataFile not in targetFileList:
            url = urlBase+'/'+products[prod]['subpath']+'/'+year+'/'+dataFile
            get = requests.get(url)
            if get.status_code == 200:
                command = 'wget '+url
                os.system(command)


