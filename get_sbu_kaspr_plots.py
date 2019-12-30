#!/usr/bin/python

import os
import sys
import time
from datetime import timedelta
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import shutil

def listFD(url, prefix=''):
    page = requests.get(url).text
    #print page
    soup = BeautifulSoup(page, 'html.parser')
    return [url + '/' + node.get('href') for node in soup.find_all('a') if node.get('href').startswith(prefix)]

# User inputs
debug = 1
secsPerDay = 86400
pastSecs = secsPerDay*1.5
url = 'https://doppler.somas.stonybrook.edu/ARCHIVE/IMAGES/KASPR'
targetDirBase = '/home/disk/bob/impacts/radar/kaspr'
products = {'RHI_LDR':'rhi_ldr','RHI_ZDR':'rhi_zdr','RHI_dBZ':'rhi_dbz','RHI_phi_dp':'rhi_phidp',
            'RHI_rho_hv':'rhi_rhohv','RHI_rho_xh':'rhi_rhoxh','RHI_spectral_width':'rhi_sw',
            'RHI_velocity_dual':'rhi_veldp','RHI_velocity_single':'rhi_vel',
            'PPI_LDR':'ppi_ldr','PPI_ZDR':'ppi_zdr','PPI_dBZ':'ppi_dbz','PPI_phi_dp':'ppi_phidp',
            'PPI_rho_hv':'ppi_rhohv','PPI_rho_xh':'ppi_rhoxh','PPI_spectral_width':'ppi_sw',
            'PPI_velocity_dual':'ppi_veldp','PPI_velocity_single':'ppi_vel'}
catalogBaseDir = '/home/disk/funnel/impacts-website/archive/research/kaspr'
prefix_dir = 'imageset'
prefix = 'Ka-band_pp_'
suffix = 'png'
catalog_prefix = 'research.kaspr'

# getdate and time
nowTime = time.gmtime()
now = datetime(nowTime.tm_year, nowTime.tm_mon, nowTime.tm_mday,
               nowTime.tm_hour, nowTime.tm_min, nowTime.tm_sec)
nowDateStr = now.strftime("%Y%m%d")
nowTimeStr = now.strftime("%H%M%S")
nowUnixTime = int(now.strftime("%s"))
nowStr = nowDateStr+nowTimeStr
nowObj = datetime.strptime(nowStr,'%Y%m%d%H%M%S')
if debug:
    print >>sys.stderr, "nowStr = ", nowStr

# compute start time
pastDelta = timedelta(0, pastSecs)
startObj = nowObj - pastDelta
startUnixTime = int(startObj.strftime("%s"))
startStr = startObj.strftime("%Y%m%d%H%M%S")
if debug:
    print >>sys.stderr, "startStr = ", startStr

# get list of files on server 
for dir in listFD(url, prefix_dir):
    # remove last slash
    dir = dir[:-1]
    # get time associated with this dir
    parts = dir.split('/')
    dirName = parts[-1]
    dirUnixTime = int(dirName.replace(prefix_dir,''))
    dirObj = datetime.utcfromtimestamp(dirUnixTime)
    dirDateStr = dirObj.strftime("%Y%m%d")
    dirStr = dirObj.strftime("%Y%m%d%H%M%S")
    if dirUnixTime >= startUnixTime and dirUnixTime <= nowUnixTime:
        if debug:
            print >>sys.stderr, "dir = ", dir, "dirUnixTime = ", dirUnixTime
        # if data not yet copied, create and cd to target dir
        targetDir = targetDirBase+'/'+dirName
        if not os.path.exists(targetDir):
            os.mkdir(targetDir)
            os.chdir(targetDir)
            
            # get list of urls with correct prefix in dir
            fileUrlList = listFD(url+'/'+dirName, prefix)
            for fileUrl in fileUrlList:
                if debug:
                    print >>sys.stderr, "fileUrl = ",fileUrl
                try:
                    command = 'wget '+fileUrl
                    os.system(command)
                except Exception as e:
                    print sys.stderr, "    wget failed, exception: ", e
                    continue
                fname = os.path.basename(fileUrl)
                (base,ext) = os.path.splitext(fname)
                type = base.replace(prefix,'')
                field = products.get(type)

                # copy file to catalog location
                catalog_name = catalog_prefix+'.'+dirStr+'.'+field+ext
                if not os.path.exists(catalogBaseDir+'/'+dirDateStr):
                    os.mkdir(catalogBaseDir+'/'+dirDateStr)
                if debug:
                    print >>sys.stderr, "Copied ", fname, " to ", catalog_name
                shutil.copy(targetDir+'/'+fname,catalogBaseDir+'/'+dirDateStr+'/'+catalog_name)
            
