#!/usr/bin/python

import os
import os.path
import sys
import time
from datetime import timedelta
from datetime import datetime
import shutil

# User inputs
debug = 1
secsPerDay = 86400
pastSecs = secsPerDay/24
SBUurl = 'https://doppler.somas.stonybrook.edu/IMPACTS/kaspr/images/quicklooks'
SBUusername = 'DataAccess'
SBUpassword = 'WinterAtSBU'
products = {'RHI_LDR':'rhi_ldr','RHI_ZDR':'rhi_zdr','RHI_dBZ':'rhi_dbz','RHI_phi_dp':'rhi_phidp',
            'RHI_rho_hv':'rhi_rhohv','RHI_rho_xh':'rhi_rhoxh','RHI_spectral_width':'rhi_sw',
            'RHI_velocity_dual':'rhi_veldp','RHI_velocity_single':'rhi_vel',
            'PPI_LDR':'ppi_ldr','PPI_ZDR':'ppi_zdr','PPI_dBZ':'ppi_dbz','PPI_phi_dp':'ppi_phidp',
            'PPI_rho_hv':'ppi_rhohv','PPI_rho_xh':'ppi_rhoxh','PPI_spectral_width':'ppi_sw',
            'PPI_velocity_dual':'ppi_veldp','PPI_velocity_single':'ppi_vel'}
targetBaseDir = '/home/disk/bob/impacts/gdrive/IMPACTS/kaspr/quicklooks'
wget_flist = 'index.html'
wget_flist_notags = 'index.noTags'
catalogBaseDir = '/home/disk/funnel/impacts-website/archive/research/kaspr'
raw_prefix = 'Ka-band_pp_'
raw_ext1 = 'png'
raw_ext2 = 'eps'
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

# for testing
#nowDateStr = '20200119'
#nowTimeStr = '000000'
#nowStr = nowDateStr+nowTimeStr
#nowObj = datetime.strptime(nowStr,'%Y%m%d%H%M%S')
#nowUnixTime = int(nowObj.strftime("%s"))

if debug:
    print >>sys.stderr, "nowStr = ", nowStr

# compute start time
pastDelta = timedelta(0, pastSecs)
startObj = nowObj - pastDelta
startUnixTime = int(startObj.strftime("%s"))
startStr = startObj.strftime("%Y%m%d%H%M%S")
if debug:
    print >>sys.stderr, "startStr = ", startStr

#-------------------------------------
# get list of new image dirs on server
#-------------------------------------
# remove old files
os.chdir(targetBaseDir)
if os.path.exists(wget_flist):
    os.remove(wget_flist)
if os.path.exists(wget_flist_notags):
    os.remove(wget_flist_notags)

# get server file listing
command = 'wget --user '+SBUusername+' --password '+SBUpassword+' --no-remove-listing '+SBUurl+'/'
os.system(command)

# remove html tags from server file listing file
command = '/home/disk/bob/impacts/bin/removeHtmlTags.csh '+wget_flist+' '+wget_flist_notags
os.system(command)

# make list of image dirs
targetBaseDirList = os.listdir(targetBaseDir)
subdirs = []
with open(wget_flist_notags,'rt') as fin:
    for line in fin:
        line = line.strip()
        if line.startswith('imagesetPPI') or line.startswith('imagesetRHI'):
            line = line.replace('/','')
            if line not in targetBaseDirList:
                subdirs.append(line)
if debug:
    print >>sys.stderr, "finished getting list of new subdirs"
                
for dir in subdirs:
    
    os.chdir(targetBaseDir)
    
    command = 'wget -N -r --user '+SBUusername+' --password '+SBUpassword+' --no-parent -nH --cut-dirs=4 '+SBUurl+'/'+dir+'/'
    os.system(command)

    # get time associated with this dir
    dirName = dir
            
    # for naming convention 'imagesetPPI_YYYYMMDD-hhmmss
    (dir_prefix,dt_str) = dirName.split('_')
    dirObj = datetime.strptime(dt_str,'%Y%m%d-%H%M%S')
    dirUnixTime = int(dirObj.strftime("%s"))
    dirDateStr = dirObj.strftime("%Y%m%d")
    dirStr = dirObj.strftime("%Y%m%d%H%M%S")

    # make catalog dir for this date if necessary
    catalogDir = catalogBaseDir+'/'+dirDateStr
    if not os.path.exists(catalogDir):
        os.mkdir(catalogDir)

    # for naming convention 'imageset<unixtime>'
    #dirStrUnixTime = dirName.replace('imageset','')
    #dirUnixTime = int(dirStrUnixTime)
    #dirObj = datetime.utcfromtimestamp(dirUnixTime)
    #dirDateStr = dirObj.strftime("%Y%m%d")
    #dirStr = dirObj.strftime("%Y%m%d%H%M%S")
    
    if dirUnixTime >= startUnixTime and dirUnixTime <= nowUnixTime:
        if debug:
            print >>sys.stderr, "dir = ", dir, "dirUnixTime = ", dirUnixTime
        targetDir = targetBaseDir+'/'+dir
        os.chdir(targetDir)
            
        # get list of files in dir
        for file in os.listdir('.'):
            if file.startswith(raw_prefix) and (file.endswith(raw_ext1) or file.endswith(raw_ext2)):
                if debug:
                    print >>sys.stderr, "file = ",file
                (base,ext) = os.path.splitext(file)
                if 'eps' in ext:
                    command = 'convert '+file+' '+base+'.png'
                    os.system(command)
                    os.remove(file)
                    file = base+'.png'
                type = base.replace(raw_prefix,'')
                field = products.get(type)

                # copy file to catalog location
                catalog_name = catalog_prefix+'.'+dirStr+'.'+field+'.png'
                if debug:
                    print >>sys.stderr, "Copied ", file, " to ", catalog_name
                shutil.copy(targetDir+'/'+file,catalogDir+'/'+catalog_name)
            


