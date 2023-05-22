#!/usr/bin/python3

import os
import shutil
from datetime import datetime
from datetime import timedelta
import time
from ftplib import FTP
import requests

urlBase = 'https://wallops-prf.gsfc.nasa.gov/Field_Campaigns/IMPACTS_2023'

# MRR6path: urlBase/MRR/MRRPRO-06/Plots/Daily/YYYY
#   rawFile = UCONN_MRRPRO-06_YYYY_MMDD.png
#   catFile = radar.MRR.<datetime>.NASA_D3R_UConn.png
# MRR7path: urlBase/MRR/MRRPRO-07/Plots/Daily/YYYY
#   rawFile = UCONN_MRRPRO-07_YYYY_MMDD.png
#   catFile = radar.MRR.<datetime>.NASA_GAIL_UConn.png
# RainGaugePath: urlBase/Gauge/Plots/YYYY/MM
#   rawFile = IMPACTS-0027-20230113.png
#   catFile = surface.Meteogram.<datetime>.NASA_D3R_UConn_Rain.png
# RainGaugePath: urlBase/Gauge/Plots/YYYY/MM
#   rawFile = IMPACTS-0028-20230113.png
#   catFile = surface.Meteogram.<datetime>.NASA_GAIL_UConn_Rain.png
# APU27ParsivelRainPath: urlBase/APU/APU27/Plots/Rain
#   rawFile = UCONN_APU27_2023_0113_rain.png (d3r)
#   catFile = surface.Parsivel.<datetime>.NASA_D3R_UConn_Rain.png
# APU28ParsivelRainPath: urlBase/APU/APU28/Plots/Rain
#   rawFile = UCONN_APU28_2023_0113_rain.png (d3r)
#   catFile = surface.Parsivel.<datetime>.NASA_GAIL_UConn_Rain.png
# APU27ParsivelDSDPath: urlBase/APU/APU27/Plots/DSD
#   rawFile = UCONN_APU27_2023_0113_dsd.png
#   catFile = surface.Parsivel.<datetime>.NASA_D3R_UConn_DSD.png
# APU28ParsivelDSDPath: urlBase/APU/APU28/Plots/DSD
#   rawFile = UCONN_APU28_2023_0113_dsd.png
#   catFile = surface.Parsivel.<datetime>.NASA_GAIL_UConn_DSD.png
# PIPpath: urlBase/????
#   rawFile = ????
#   catFile = surface.PIP.<datetime>.NASA_GAIL_UConn.png
# All-in-1 path: urlBase/AIO/Plots
#   rawFile = UCONN_D3R_AIO_2023_0113.png
#   catFile = surface.Meteogram.<datetime>.NASA_D3R_UConn.png
# All-in-1 path: urlBase/AIO/Plots
#   rawFile = UCONN_GAIL_AIO_2023_0113.png
#   catFile = surface.Meteogram.<datetime>.NASA_GAIL_UConn.png
# AnemometerPath: urlBase/RMY/RMY_APU27/Plots
#   rawFile = UCONN_RMYAPU27_2023_0113.png
#   catFile = surface.Meteogram.<datetime>.NASA_D3R_UConn_Wind.png

test = False
tempDir = '/tmp'
targetDirBase = '/home/disk/bob/impacts/sfc/nasa'
# set startFlag
#    0 -> start now
#    1 -> start at startDate
startFlag = 0
startDate = '20230116'
startTime = '0000'
# set number of days to go back from startDate
num_days = 2
secsPerDay = 86400

products = {'MRRPRO-06':{'subpath':'MRR/MRRPRO-06/Plots/Daily','prefix':'UCONN_MRRPRO-06','catPrefix':'radar.MRR',        'catProduct':'NASA_D3R_UConn'},
            'MRRPRO-07':{'subpath':'MRR/MRRPRO-07/Plots/Daily','prefix':'UCONN_MRRPRO-07','catPrefix':'radar.MRR',        'catProduct':'NASA_GAIL_UConn'},
            'Gauge27':  {'subpath':'Gauge/Plots',              'prefix':'IMPACTS-0027',   'catPrefix':'surface.Meteogram','catProduct':'NASA_D3R_UConn_Rain'},
            'Gauge28'  :{'subpath':'Gauge/Plots',              'prefix':'IMPACTS-0028',   'catPrefix':'surface.Meteogram','catProduct':'NASA_GAIL_UConn_Rain'},
            'APU27DSD' :{'subpath':'APU/APU27/Plots/DSD',      'prefix':'UCONN_APU27',    'catPrefix':'surface.Parsivel', 'catProduct':'NASA_D3R_UConn_DSD'},
            'APU28DSD' :{'subpath':'APU/APU28/Plots/DSD',      'prefix':'UCONN_APU28',    'catPrefix':'surface.Parsivel', 'catProduct':'NASA_GAIL_UConn_DSD'},
            'APU27Rain':{'subpath':'APU/APU27/Plots/Rain',     'prefix':'UCONN_APU27',    'catPrefix':'surface.Parsivel', 'catProduct':'NASA_D3R_UConn_Rain'},
            'APU28Rain':{'subpath':'APU/APU28/Plots/Rain',     'prefix':'UCONN_APU28',    'catPrefix':'surface.Parsivel', 'catProduct':'NASA_GAIL_UConn_Rain'},
            'AIOD3R'   :{'subpath':'AIO/Plots',                'prefix':'UCONN_D3R_AIO',  'catPrefix':'surface.Meteogram','catProduct':'NASA_D3R_UConn'},
            'AIOGAIL'  :{'subpath':'AIO/Plots',                'prefix':'UCONN_GAIL_AIO', 'catPrefix':'surface.Meteogram','catProduct':'NASA_GAIL_UConn'},
            'Winds'    :{'subpath':'RMY/RMY_APU27/Plots',      'prefix':'UCONN_RMYAPU27', 'catPrefix':'surface.Meteogram','catProduct':'NASA_D3R_UConn_Wind'} }
ext = 'png'

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
   
# Change to tempDir
os.chdir(tempDir)

for idx,idate in enumerate(dateStrList,0):

    print('date =',idate)

    year = idate[0:4]
    month = idate[4:6]
    day = idate[6:8]
    year_mmdd = year+'_'+month+day

    for prod in products.keys():

        print('prod =',prod)

        # get list of images in target dir
        targetDir = targetDirBase+'/'+prod
        if not os.path.isdir(targetDir):
            os.makedirs(targetDir)
        targetFileList = os.listdir(targetDir)

        # get prod image names and datetime for idate
        if 'MRR' in prod:
            imageNameBase = products[prod]['prefix']+'_'+year+'_'+month+day
            url = urlBase+'/'+products[prod]['subpath']+'/'+year+'/'+imageNameBase+'.'+ext
            (site,instr,yyyy,mmdd) = imageNameBase.split('_')
            datetime = yyyy+mmdd+'0000'
        elif 'Gauge' in prod:
            imageNameBase = products[prod]['prefix']+'-'+idate
            url = urlBase+'/'+products[prod]['subpath']+'/'+year+'/'+month+'/'+imageNameBase+'.'+ext
            (proj,inst,datetime) = imageNameBase.split('-')
            datetime = datetime+'0000'
        elif 'APU' in prod:
            if 'Rain' in prod:
                imageNameBase = products[prod]['prefix']+'_'+year+'_'+month+day+'_rain'
                url = urlBase+'/'+products[prod]['subpath']+'/'+imageNameBase+'.'+ext
            elif 'DSD' in prod:
                imageNameBase = products[prod]['prefix']+'_'+year+'_'+month+day+'_dsd'
                url = urlBase+'/'+products[prod]['subpath']+'/'+imageNameBase+'.'+ext
            (site,inst,yyyy,mmdd,type) = imageNameBase.split('_')
            datetime = yyyy+mmdd+'0000'
        elif 'AIO' in prod:
            imageNameBase = products[prod]['prefix']+'_'+year+'_'+month+day
            url = urlBase+'/'+products[prod]['subpath']+'/'+imageNameBase+'.'+ext
            (site,loc,inst,yyyy,mmdd) = imageNameBase.split('_')
            datetime = yyyy+mmdd+'0000'
        elif prod == 'Winds':
            imageNameBase = products[prod]['prefix']+'_'+year+'_'+month+day
            url = urlBase+'/'+products[prod]['subpath']+'/'+imageNameBase+'.'+ext 
            (site,instr,yyyy,mmdd) = imageNameBase.split('_')
            datetime = yyyy+mmdd+'0000'

        # download urlFiles not already downloaded to target dir
        os.chdir(tempDir)
        imageName = imageNameBase+'.'+ext
        if imageName not in targetFileList:
            print('   not in targetDir')
            get = requests.get(url)
            if get.status_code == 200:
                command = 'wget '+url
                os.system(command)

                # assign catalog file name
                catName = products[prod]['catPrefix']+'.'+datetime+'.'+products[prod]['catProduct']+'.'+ext

                # copy original file name to targetDir
                shutil.copy(tempDir+'/'+imageName,
                            targetDir+'/'+imageName)

                # rename file, ftp to catalog, remove from tempDir
                shutil.move(tempDir+'/'+imageName,
                            tempDir+'/'+catName)
                ftpFile = open(os.path.join(tempDir,catName),'rb')
                catalogFTP.storbinary('STOR '+catName,ftpFile)
                ftpFile.close()
                os.remove(tempDir+'/'+catName)
                
                

