#!/usr/bin/python

# File names are: (correct code for these changes from 2020)
# mrr/mrr_ualb_timeheight_20201217.png
# mrr/mrr_ualb_cfads_20201217.png
# parsivel/parsivel_ualb_psd_timeseries_20201217.png
# parsivel/parsivel_ualb_vdhist_20201217.png
# parsivel/parsivel_mrr_ualb_timeseries_20201217.png
# parsivel/parsivel_ualb_psd_rrdbz_composite_20201217.png

import os
import sys
import time
from datetime import timedelta
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import shutil
from ftplib import FTP

def listFD(url, ext=''):
    page = requests.get(url).text
    #print page
    soup = BeautifulSoup(page, 'html.parser')
    return [url + '/' + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]

# User inputs
debug = 1
test = 1
baseUrl = 'http://www.atmos.albany.edu/student/mbartolini/research/impacts/images/'
#subDir = { 'mrr': {'mrr_ualb_cfads':'mrr_cfad','mrr_ualb_timeheight':'mrr'},
#           'parsivel' : {'parsivel_mrr_ualb_timeseries':'mrr_parsivel_tseries','parsivel_ualb_psd_timeseries':'parsivel'} }
subDir = { 'mrr': {'mrr_ualb_cfads':'UAlbany_CFAD',
                   'mrr_ualb_timeheight':'UAlbany_time_ht'},
           'parsivel' : {'parsivel_mrr_ualb_timeseries':'UAlbany_MRR_vs_Parsivel',
                         'parsivel_ualb_psd_timeseries':'UAlbany'} }
targetDirBase = '/home/disk/bob/impacts/radar/ualbany'
tempDir = '/tmp'
ext = 'png'
catalogPrefix = 'surface' or 'radar'

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

# get yesterday's date
dateStr = datetime.strftime(datetime.now() - timedelta(1), '%Y%m%d')
if debug:
    print("dateStr = ", dateStr)

for sd_id, sd_info in subDir.items():
    if debug:
        print("subdir_id = ",sd_id)
        print("subdir_info = ",sd_info)
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
            print("WARNING: no data of interest on server")
    else:
        # create targetDir and cd to it           
        targetDir = targetDirBase+'/'+sd_id
        if not os.path.exists(targetDir):
            os.makedirs(targetDir)
        os.chdir(targetDir)
        localFileList = os.listdir('.')
            
        for idx,urlFileName in enumerate(urlFileList,0):
            if debug:
                print("  idx = ", idx)
                print("  urlFileName = ", urlFileName)

            if urlFileName not in localFileList:
                if debug:
                    print("    ",urlFileName,"not in localFileList -- get file")
                try:
                    command = 'wget '+url+'/'+urlFileName
                    os.system(command)
                except Exception as e:
                    print("    wget failed, exception: ", e)
                    continue
                
                # rename file and move to web server
                # first get forecast_hour
                (base,ext) = os.path.splitext(urlFileName)
                product = base.replace('_'+dateStr,'')

                # create full file name - CHANGE THIS
                catalogName = 'research.ualbany.'+dateStr+'.'+sd_info[product]+ext
                if debug:
                    print("    catalogName = ", catalogName)

                # copy file to tempDir and rename
                shutil.copy(targetDir+'/'+urlFileName,
                            tempDir+'/'+catalogName)

                # ftp file to catalog location
                ftpFile = open(os.path.join(tempDir,catalogName),'rb')
                catalogFTP.storbinary('STOR '+catalogName,ftpFile)
                ftpFile.close()

                # remove file from tempDir
                os.remove(os.path.join(tempDir,catalogName))

# Close ftp connection
catalogFTP.quit()
 
