#!/usr/bin/python3

import os
from bs4 import BeautifulSoup
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from datetime import timedelta
import time

urlBase = 'https://doppler.somas.stonybrook.edu/IMPACTS'
urlUser = 'DataAccess'
urlPwd = 'WinterAtSBU'

tempDir = '/tmp'
targetDirBase = '/home/disk/bob/impacts/radar/sbu'
# set startFlag
#    0 -> start now
#    1 -> start at startDate
startFlag = 1
startDate = '20230302'
startTime = '0000'
# set number of days to go back from startDate
num_days = 65
secsPerDay = 86400

bnlProd = {#'mrrpro2white':{'subpath':'BNL/mrrpro2white/netcdf','prefix':'',         'suffix':'nc'},
           #'parsivel'    :{'subpath':'BNL/parsivel/netcdf',    'prefix':'parsivel_','suffix':'nc'},
           #'pluvio'      :{'subpath':'BNL/pluvio/csv',         'prefix':'pluvio2_', 'suffix':'txt'},
           'vceilo15k'   :{'subpath':'BNL/vceilo15k/netcdf',   'prefix':'L3_',      'suffix':'nc'} }

# NOTE: Might need to download airmar data manually using these commands
# cd /home/disk/bob/impacts/radar/sbu/RadarTruck/airmarweather:
# wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=5 https://doppler.somas.stonybrook.edu/IMPACTS/RadarTruck/airmarweather/netcdf/Jan_23_2023_PORT_6_0183.nc
#truckProd = {'airmar'  :{'subpath':'RadarTruck/airmarweather/netcdf','prefix':'airmar_',  'suffix':'nc'},
truckProd = {'parsivel2':{'subpath':'RadarTruck/parsivel2/netcdf',    'prefix':'parsivel_','suffix':'nc'} }

# NOTE: No netcdf files for 2023 on site
#SBUProd = {'kasprPPI':{'subpath':'kaspr/images/quicklooks','prefix':'imagesetPPI_','catPrefix':'radar.KaSPR','catProduct':'ppi_'},
#           'kasprPPI':{'subpath':'kaspr/images/quicklooks','prefix':'imagesetRHI_','catPrefix':'radar.KaSPR','catProduct':'rhi_'} }

# Get start date
if startFlag == 0:
    # use yesterday's date to ensure file is complete
    nowDate = datetime.now() - timedelta(seconds=secsPerDay)
    nowDateStr = datetime.strftime(nowDate,'%Y%m%d')+startTime
    now = datetime.strptime(nowDateStr,'%Y%m%d%H%M')
else:
    nowDateStr = startDate+startTime
    now = datetime.strptime(nowDateStr,'%Y%m%d%H%M')

# Make list of dates to process
dateStrList = []
for idate in range(0,num_days):
    deltaSecs = timedelta(0, idate * secsPerDay)
    nextDate = now - deltaSecs
    nextDateStr = nextDate.strftime("%Y%m%d")
    dateStrList.append(nextDateStr)
print('dateStrList = ',dateStrList)
   
auth = HTTPBasicAuth(urlUser,urlPwd)

for idate in dateStrList:

    print('date =',idate)
    yyyymm = idate[0:6]

    for prod in bnlProd:

        print('prod =',prod)

        # get list of files in targetDir for idate
        if prod == 'mrrpro2white':
            targetDir = targetDirBase+'/BNL/'+prod+'/'+idate
        else:
            targetDir = targetDirBase+'/BNL/'+prod
        if not os.path.isdir(targetDir):
            os.makedirs(targetDir)
        os.chdir(targetDir)
        flist = os.listdir(targetDir)
        targetList = []
        for file in flist:
            if file.startswith(bnlProd[prod]['prefix']) and file.endswith(bnlProd[prod]['suffix']) :
                targetList.append(file)

        if prod == 'mrrpro2white':
            url = urlBase+'/'+bnlProd[prod]['subpath']+'/'+yyyymm+'/'+idate
        else:
            url = urlBase+'/'+bnlProd[prod]['subpath']
        r = requests.get(url = url, auth=auth, verify=False)
        #print(r.text)
        soup = BeautifulSoup(r.text, 'html.parser')
        files = [url + '/' + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(bnlProd[prod]['suffix'])]
        for file in files:
            base = os.path.basename(file)
            if base not in targetList and base.startswith(bnlProd[prod]['prefix']) and idate in base:

                print('  base =',base)
                
                if prod == 'mrrpro2white':
                    command = 'wget -r --user '+urlUser+' --password '+urlPwd+' --no-parent -nH --cut-dirs=6 '+file
                else:
                    command = 'wget -r --user '+urlUser+' --password '+urlPwd+' --no-parent -nH --cut-dirs=5 '+file
                os.system(command)

    """
    for prod in truckProd:

        print('prod =',prod)

        # get list of files in targetDir for idate
        targetDir = targetDirBase+'/RadarTruck/'+prod
        if not os.path.isdir(targetDir):
            os.makedirs(targetDir)
        os.chdir(targetDir)
        flist = os.listdir(targetDir)
        targetList = []
        for file in flist:
            #if file.startswith(truckProd[prod]['prefix']) and idate in file and file.endswith('png'):
            if file.startswith(truckProd[prod]['prefix']) and file.endswith('png'):
                targetList.append(file)
    
        url = urlBase+'/'+truckProd[prod]['subpath']
        r = requests.get(url = url, auth=auth, verify=False)
        #print(r.text)
        soup = BeautifulSoup(r.text, 'html.parser')
        files = [url + '/' + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(truckProd[prod]['suffix'])]
        for file in files:
            base = os.path.basename(file)
            if base not in targetList and idate in base:

                print('  base =',base)
                
                command = 'wget -r --user '+urlUser+' --password '+urlPwd+' --no-parent -nH --cut-dirs=5 '+file
                os.system(command)
    """        

            
    
            
