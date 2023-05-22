#!/usr/bin/python3

import os
from bs4 import BeautifulSoup
import requests
from requests.auth import HTTPBasicAuth
import shutil
from datetime import datetime
from datetime import timedelta
import time
from ftplib import FTP

urlBase = 'https://doppler.somas.stonybrook.edu/IMPACTS'
urlUser = 'DataAccess'
urlPwd = 'WinterAtSBU'

test = False
tempDir = '/tmp'
targetDirBase = '/home/disk/bob/impacts/radar/sbu_images'
# set startFlag
#    0 -> start now
#    1 -> start at startDate
startFlag = 0
startDate = '20230120'
startTime = '0000'
# set number of days to go back from startDate
num_days = 2
secsPerDay = 86400

# NOTE: Do not need to download WCR images - SBU is doing that
bnlProd = {'mrrpro2white':{'subpath':'BNL/mrrpro2white/images/quicklooks','prefix':'mrrprowhite_realtime_','catPrefix':'radar.MRR',       'catProduct':'Brookhaven_NY'},
           'mwr-mp3000a' :{'subpath':'BNL/mwr_mp3000a/images/quicklooks', 'prefix':'mwrmp3000A_',          'catPrefix':'upperair.MWR',    'catProduct':'Brookhaven_NY'},
           'parsivel'    :{'subpath':'BNL/parsivel/images/quicklooks',    'prefix':'parsivel_realtime_',   'catPrefix':'surface.Parsivel','catProduct':'Brookhaven_NY'},
           'pluvio'      :{'subpath':'BNL/pluvio/images/quicklooks',      'prefix':'pluvio_',              'catPrefix':'surface.Pluvio',  'catProduct':'Brookhaven_NY'},
           'vceilo15k'   :{'subpath':'BNL/vceilo15k/images/quicklooks',   'prefix':'cl51_',                'catPrefix':'lidar.Ceilometer','catProduct':'Brookhaven_NY_15000m'} }
           #'wcr'         :{'subpath':'BNL/wcr/images/quicklooks',        'prefix':'WACR_',                'catPrefix':'radar.WCR-QPC',   'catProduct':'Brookhaven_NY_time_ht'} }

# NOTE: Change product names of existing parsivel files in catalog 
truckProd = {'airmar'  :{'subpath':'RadarTruck/airmarweather/images/quicklooks','prefix':'airmar_',  'catPrefix':'surface.Meteogram','catProduct':'SBU_Mobile'},
             'parsivel':{'subpath':'RadarTruck/parsivel2/images/quicklooks',    'prefix':'parsivel_','catPrefix':'surface.Parsivel', 'catProduct':'SBU_Mobile'} }

# NOTE: Mariko is creating 6 panel images of this data and uploading to FC directly
#SBUProd = {'kasprPPI':{'subpath':'kaspr/images/quicklooks','prefix':'imagesetPPI_','catPrefix':'radar.KaSPR','catProduct':'ppi_'},
#           'kasprPPI':{'subpath':'kaspr/images/quicklooks','prefix':'imagesetRHI_','catPrefix':'radar.KaSPR','catProduct':'rhi_'} }

# Field Catalog inputs
if test:
    ftpCatalogServer = 'ftp.atmos.washington.edu'
    ftpCatalogUser = 'anonymous'
    ftpCatalogPassword = 'brodzik@uw.edu'
    catalogDestDir = 'brodzik/incoming/impacts'
else:
    ftpCatalogServer = 'catalog.eol.ucar.edu'
    ftpCatalogUser = 'anonymous'
    catalogDestDir = '/pub/incoming/catalog/impacts'

# Open ftp connection
if test:
    catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser,ftpCatalogPassword)
    catalogFTP.cwd(catalogDestDir)
else:
    catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
    catalogFTP.cwd(catalogDestDir)

# Get start date
if startFlag == 0:
    nowDate = datetime.now().date()
    nowDateStr = datetime.strftime(nowDate,'%Y%m%d')+startTime
    now = datetime.strptime(nowDateStr,'%Y%m%d%H%M')
else:
    nowDateStr = startDate+startTime
    now = datetime.strptime(nowDateStr,'%Y%m%d%H%M')

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
   
os.chdir(tempDir)
auth = HTTPBasicAuth(urlUser,urlPwd)

for idate in dateStrList:

    print('date =',idate)

    for prod in bnlProd:

        print('prod =',prod)

        # get list of files in targetDir for idate
        targetDir = targetDirBase+'/BNL/'+prod
        if not os.path.isdir(targetDir):
            os.makedirs(targetDir)
        flist = os.listdir(targetDir)
        targetList = []
        for file in flist:
            if file.startswith(bnlProd[prod]['prefix']) and idate in file and file.endswith('png'):
                targetList.append(file)
    
        url = urlBase+'/'+bnlProd[prod]['subpath']
        r = requests.get(url = url, auth=auth, verify=False)
        #print(r.text)
        soup = BeautifulSoup(r.text, 'html.parser')
        files = [url + '/' + node.get('href') for node in soup.find_all('a') if node.get('href').endswith('png')]
        for file in files:
            base = os.path.basename(file)
            if base not in targetList and idate in base:

                print('  base =',base)
                
                command = 'wget -r --user '+urlUser+' --password '+urlPwd+' --no-parent -nH --cut-dirs=5 '+file
                os.system(command)
            
                # copy fle to targetDir
                shutil.copy(tempDir+'/'+base,
                            targetDir+'/'+base)

                # rename file and ftp to catalog
                (root,ext) = os.path.splitext(base)
                if prod == 'mrrpro2white' or prod == 'parsivel':
                    (junk,junk,date) = root.split('_')
                elif prod == 'mwr-mp3000a' or prod == 'pluvio' or prod == 'vceilo15k':
                    (junk,date) = root.split('_')
                datetime = date+'0000'
                
                catName = bnlProd[prod]['catPrefix']+'.'+datetime+'.'+bnlProd[prod]['catProduct']+ext
                shutil.move(tempDir+'/'+base,
                            tempDir+'/'+catName)

                ftpFile = open(os.path.join(tempDir,catName),'rb')
                catalogFTP.storbinary('STOR '+catName,ftpFile)
                ftpFile.close()
                os.remove(tempDir+'/'+catName)

    for prod in truckProd:

        print('prod =',prod)

        # get list of files in targetDir for idate
        targetDir = targetDirBase+'/RadarTruck/'+prod
        if not os.path.isdir(targetDir):
            os.makedirs(targetDir)
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
        files = [url + '/' + node.get('href') for node in soup.find_all('a') if node.get('href').endswith('png')]
        for file in files:
            base = os.path.basename(file)
            if base not in targetList and idate in base:

                print('  base =',base)
                
                command = 'wget -r --user '+urlUser+' --password '+urlPwd+' --no-parent -nH --cut-dirs=5 '+file
                os.system(command)
            
                # copy fle to targetDir
                shutil.copy(tempDir+'/'+base,
                            targetDir+'/'+base)

                # rename file and ftp to catalog
                (root,ext) = os.path.splitext(base)
                (junk,date) = root.split('_')
                datetime = date+'0000'
                catName = truckProd[prod]['catPrefix']+'.'+datetime+'.'+truckProd[prod]['catProduct']+ext
                
                shutil.move(tempDir+'/'+base,
                            tempDir+'/'+catName)

                ftpFile = open(os.path.join(tempDir,catName),'rb')
                catalogFTP.storbinary('STOR '+catName,ftpFile)
                ftpFile.close()
                os.remove(tempDir+'/'+catName)

            
    
            
