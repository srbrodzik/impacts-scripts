#!/usr/bin/python3

import os
import shutil
from datetime import datetime
from datetime import timedelta
import time
from ftplib import FTP

test = True
tempDir = '/tmp'
product = 'NASA_GAIL_UConn'
# set startFlag
#    0 -> start now
#    1 -> start at startDate
startFlag = 0
startDate = '20220114'
startTime = '0000'
# set number of days to go back from startDate
num_days = 1
secsPerDay = 86400

urlBase = 'https://wallops-prf.gsfc.nasa.gov/Field_Campaigns/IMPACTS/Plots'
urlAIO = 'https://wallops-prf.gsfc.nasa.gov/All-in-1/Plots'
# MRRpath: urlBase/MRR2-03/YYYY/MM/DD/ql/rawFile
#   rawFile = WFF_MRR2-03_YYYY_MMDD_ql.png
#   catFile = radar.MRR.<datetime>.GAIL_UConn.png
# 2DVDpath: PLOTS UNAVAILABLE
#   rawFile
#   catFile
# ParsivelDSDpath: urlBase/apu18/DSD/YYYY/rawFile
#   rawFile = WFF_apu18_YYYY_MMDD_dsd.png
#   catFile = surface.Parsivel.<datetime>.GAIL_UConn_DSD.png
# ParsivelRainPath: urlBase/apu18/Rain/YYYY/rawFile
#   rawFile = WFF_apu18_YYYY_MMDD_rain.png
#   catFile = surface.Parsivel.<datetime>.GAIL_UConn_Rain.png
# PIPpath: urlBase/PIP003/YYYY/MM/rawFile
#   rawFile = 00320YYMMDD_Summary_Figure.png
#   catFile = surface.PIP.<datetime>.GAIL_UConn.png
# Pluvio: PLOTS UNAVAILABLE
#   rawFile
#   catFile
# All-in-1: urlAIO/YYYY/rawFile
#   rawFile = AIO_YYYY_MMDD.png
#   catFile = surface.Meteogram.<datetime>.GAIL_UConn.png

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
#now = datetime.utcnow()
nowDateTimeStr = now.strftime("%Y%m%d")+startTime
nowDateStr = now.strftime("%Y%m%d")
nowYearStr = now.strftime("%Y")
nowMonthStr = now.strftime("%m")
nowDayStr = now.strftime("%d")
print(nowDateTimeStr)

# Make list of dates to process
dateTimeStrList = []
dateStrList = []
yearStrList = []
monthStrList = []
dayStrList = []
for idate in range(0,num_days):
    deltaSecs = timedelta(0, idate * secsPerDay)
    nextDate = now - deltaSecs
    nextDateTimeStr = nextDate.strftime("%Y%m%d%H%M")
    dateTimeStrList.append(nextDateTimeStr)
    nextDateStr = nextDate.strftime("%Y%m%d")
    dateStrList.append(nextDateStr)
    nextYearStr = nextDate.strftime("%Y")
    yearStrList.append(nextYearStr)
    nextMonthStr = nextDate.strftime("%m")
    monthStrList.append(nextMonthStr)
    nextDayStr = nextDate.strftime("%d")
    dayStrList.append(nextDayStr)
print('dateStrList = ',dateStrList)
print('dateTimeStrList = ',dateTimeStrList)
   
# Change to tempDir
os.chdir(tempDir)

for idx,idate in enumerate(dateStrList,0):

    # Get MRR iamge
    rawFile = 'WFF_MRR2-03_'+yearStrList[idx]+'_'+monthStrList[idx]+dayStrList[idx]+'_ql.png'
    catFile = 'radar.MRR.'+dateTimeStrList[idx]+'.'+product+'.png'
    command = 'wget '+urlBase+'/MRR2-03/'+yearStrList[idx]+'/'+monthStrList[idx]+'/'+dayStrList[idx]+'/ql/'+rawFile
    os.system(command)
    if os.path.exists(tempDir+'/'+rawFile):
        shutil.move(tempDir+'/'+rawFile,
                    tempDir+'/'+catFile)
        ftpFile = open(os.path.join(tempDir,catFile),'rb')
        catalogFTP.storbinary('STOR '+catFile,ftpFile)
        ftpFile.close()
        #os.remove(tempDir+'/'+catFile)

    # Get Parsivel images
    rawFile = 'WFF_apu18_'+yearStrList[idx]+'_'+monthStrList[idx]+dayStrList[idx]+'_dsd.png'
    catFile = 'surface.Parsivel.'+dateTimeStrList[idx]+'.'+product+'_DSD.png'
    command = 'wget '+urlBase+'/apu18/DSD/'+yearStrList[idx]+'/'+rawFile
    os.system(command)
    if os.path.exists(tempDir+'/'+rawFile):
        shutil.move(tempDir+'/'+rawFile,
                    tempDir+'/'+catFile)
        ftpFile = open(os.path.join(tempDir,catFile),'rb')
        catalogFTP.storbinary('STOR '+catFile,ftpFile)
        ftpFile.close()
        #os.remove(tempDir+'/'+catFile)

    rawFile = 'WFF_apu18_'+yearStrList[idx]+'_'+monthStrList[idx]+dayStrList[idx]+'_rain.png'
    catFile = 'surface.Parsivel.'+dateTimeStrList[idx]+'.'+product+'_Rain.png'
    command = 'wget '+urlBase+'/apu18/Rain/'+yearStrList[idx]+'/'+rawFile
    os.system(command)
    if os.path.exists(tempDir+'/'+rawFile):
        shutil.move(tempDir+'/'+rawFile,
                    tempDir+'/'+catFile)
        ftpFile = open(os.path.join(tempDir,catFile),'rb')
        catalogFTP.storbinary('STOR '+catFile,ftpFile)
        ftpFile.close()
        #os.remove(tempDir+'/'+catFile)

    # Get PIP image
    rawFile = '003'+yearStrList[idx]+monthStrList[idx]+dayStrList[idx]+'_Summary_Figure.png'
    catFile = 'surface.PIP.'+dateTimeStrList[idx]+'.'+product+'.png'
    command = 'wget '+urlBase+'/PIP003/'+yearStrList[idx]+'/'+monthStrList[idx]+'/'+rawFile
    os.system(command)
    if os.path.exists(tempDir+'/'+rawFile):
        shutil.move(tempDir+'/'+rawFile,
                    tempDir+'/'+catFile)
        ftpFile = open(os.path.join(tempDir,catFile),'rb')
        catalogFTP.storbinary('STOR '+catFile,ftpFile)
        ftpFile.close()
        #os.remove(tempDir+'/'+catFile)

    # All-in-1: urlAIO/YYYY/rawFile
    #   rawFile = AIO_YYYY_MMDD.png
    #   catFile = surface.Meteogram.<datetime>.GAIL_UConn.png
    # Get All-in-One image
    rawFile = 'AIO_'+yearStrList[idx]+'_'+monthStrList[idx]+dayStrList[idx]+'.png'
    catFile = 'surface.Meteogram.'+dateTimeStrList[idx]+'.'+product+'.png'
    command = 'wget '+urlAIO+'/'+yearStrList[idx]+'/'+rawFile
    os.system(command)
    if os.path.exists(tempDir+'/'+rawFile):
        shutil.move(tempDir+'/'+rawFile,
                    tempDir+'/'+catFile)
        ftpFile = open(os.path.join(tempDir,catFile),'rb')
        catalogFTP.storbinary('STOR '+catFile,ftpFile)
        ftpFile.close()
        os.remove(tempDir+'/'+catFile)

