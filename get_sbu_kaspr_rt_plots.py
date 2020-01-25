#!/usr/bin/python

import os
import sys
import time
from datetime import timedelta
from datetime import datetime
import shutil

# User inputs
debug = 1
secsPerDay = 86400
pastSecs = secsPerDay/48
SBUurl = 'https://doppler.somas.stonybrook.edu/IMPACTS/kaspr/images/quicklooks'
SBUusername = 'DataAccess'
SBUpassword = 'WinterAtSBU'
targetDirBase = '/home/disk/bob/impacts/gdrive/IMPACTS/kaspr/quicklooks'
products = {'RHI_LDR':'rhi_ldr','RHI_ZDR':'rhi_zdr','RHI_dBZ':'rhi_dbz','RHI_phi_dp':'rhi_phidp',
            'RHI_rho_hv':'rhi_rhohv','RHI_rho_xh':'rhi_rhoxh','RHI_spectral_width':'rhi_sw',
            'RHI_velocity_dual':'rhi_veldp','RHI_velocity_single':'rhi_vel',
            'PPI_LDR':'ppi_ldr','PPI_ZDR':'ppi_zdr','PPI_dBZ':'ppi_dbz','PPI_phi_dp':'ppi_phidp',
            'PPI_rho_hv':'ppi_rhohv','PPI_rho_xh':'ppi_rhoxh','PPI_spectral_width':'ppi_sw',
            'PPI_velocity_dual':'ppi_veldp','PPI_velocity_single':'ppi_vel'}
catalogBaseDir = '/home/disk/funnel/impacts-website/archive/research/kaspr_rt'
prefix = 'Ka-band_pp_'
catalog_prefix = 'research.kaspr'

# getdate and time
#nowTime = time.gmtime()
#now = datetime(nowTime.tm_year, nowTime.tm_mon, nowTime.tm_mday,
#               nowTime.tm_hour, nowTime.tm_min, nowTime.tm_sec)
#nowDateStr = now.strftime("%Y%m%d")
#nowTimeStr = now.strftime("%H%M%S")
#nowUnixTime = int(now.strftime("%s"))
#nowStr = nowDateStr+nowTimeStr
#nowObj = datetime.strptime(nowStr,'%Y%m%d%H%M%S')

# for testing
nowDateStr = '20200119'
nowTimeStr = '000000'
nowStr = nowDateStr+nowTimeStr
nowObj = datetime.strptime(nowStr,'%Y%m%d%H%M%S')
nowUnixTime = int(nowObj.strftime("%s"))

if debug:
    print >>sys.stderr, "nowStr = ", nowStr

# compute start time
pastDelta = timedelta(0, pastSecs)
startObj = nowObj - pastDelta
startUnixTime = int(startObj.strftime("%s"))
startStr = startObj.strftime("%Y%m%d%H%M%S")
if debug:
    print >>sys.stderr, "startStr = ", startStr

# run rsync of image dir
os.chdir(targetDirBase)
#command = 'wget -S -r --user '+SBUusername+' --password '+SBUpassword+' --no-parent -nH --cut-dirs=4 '+SBUurl
command = 'wget -N -r --user '+SBUusername+' --password '+SBUpassword+' --no-parent -nH --cut-dirs=4 '+SBUurl
os.system(command)
print >>sys.stderr, "Done with wget"

# get list of files on server 
for dir in os.listdir(targetDirBase):
    if os.path.isdir(dir):
        if dir.startswith('imagesetPPI') or dir.startswith('imagesetRHI'):
            if debug:
                print >>sys.stderr, "imagedir = ",dir

            # define targetDir
            targetDir = targetDirBase+'/'+dir
            
            # get time associated with this dir
            dirName = dir
            (dir_prefix,dt_str) = dirName.split('_')
            dirObj = datetime.strptime(dt_str,'%Y%m%d-%H%M%S')
            dirUnixTime = int(dirObj.strftime("%s"))
            dirDateStr = dirObj.strftime("%Y%m%d")
            dirStr = dirObj.strftime("%Y%m%d%H%M%S")
    
            if dirUnixTime >= startUnixTime and dirUnixTime <= nowUnixTime:
                if debug:
                    print >>sys.stderr, "dir = ", dir, "dirUnixTime = ", dirUnixTime
                os.chdir(dir)
            
                # get list of files in dir
                for file in os.listdir('.'):
                    if file.startswith(prefix):
                        if debug:
                            print >>sys.stderr, "file = ",file
                        (base,ext) = os.path.splitext(file)
                        type = base.replace(prefix,'')
                        field = products.get(type)

                        # copy file to catalog location
                        catalogDir = catalogBaseDir+'/'+dirDateStr
                        catalog_name = catalog_prefix+'.'+dirStr+'.'+field+ext
                        if not os.path.exists(catalogBaseDir+'/'+dirDateStr):
                            os.mkdir(catalogBaseDir+'/'+dirDateStr)
                        if debug:
                            print >>sys.stderr, "Copied ", file, " to ", catalog_name
                        shutil.copy(targetDir+'/'+file,catalogDir+'/'+catalog_name)
            
