#!/usr/bin/python

# SAMPLE PRODUCT LIST                  HAS ANAL PRODUCT
# composite refl (cref_sfc)            1
# IR Tb (G114bt_sat)                   1
# cloud top height (ctop)              1
# 925hPa temp/hgt/wind (temp_925)      1
# 850hPa temp/hgt/wind (temp_850)      1
# 700hPa temp/hgt/wind (temp_700)      1
# 250hPa wind/hgt (wind_250)           1
# low cloud (lcc_sfc)                  1
# medium cloud (mcc_sfc)               1
# high cloud (hcc_sfc)                 1

import os
import sys
import time
import shutil

if len(sys.argv) != 2:
    print >>sys.stderr, "Useage: ", sys.argv[0], " <modelruntime (YYYYMMDDhh)>"
    sys.exit()
else:
    modelInitTime = sys.argv[1]
    date = modelInitTime[0:8]
    print >>sys.stderr, "modelInitTime = ", modelInitTime
    print >>sys.stderr, "date = ", date

# User inputs
debug = 1
hrrrBaseUrl = 'https://rapidrefresh.noaa.gov/hrrr/NEST/for_web/hrrr_nest2_jet'
hrrrUrl = hrrrBaseUrl+'/'+modelInitTime+'/full'
products = ['cref_sfc','G114bt_sat','ctop','temp_925','temp_850','temp_700','wind_250','lcc_sfc','mcc_sfc','hcc_sfc']
has_anal_prod = [1,1,1,1,1,1,1,1,1,1]
numFhours = 46
ext = 'png'
targetBaseDir = '/home/disk/bob/impacts/model/hrrr_01km'
catalogBaseDir = '/home/disk/funnel/impacts-website/archive/model/hrrr_01km'
catalogPrefix = 'model.hrrr_01km'

# define target directory for image download
# and get list of preexisting files there
targetDir = targetBaseDir+'/'+modelInitTime
if not os.path.exists(targetDir):
    os.makedirs(targetDir)
os.chdir(targetDir)
localFileList = os.listdir('.')

# request all products
for idx,prod in enumerate(products,0):

    command = 'wget "https://rapidrefresh.noaa.gov/hrrr/HRRR/displayMapLocalDiskDateDomainZipTZA.cgi?keys=hrrr_nest2_jet:&runtime='+modelInitTime+'&plot_type=all'+prod+'&fcst=03&time_inc=60&num_times=46&model=hrrr&ptitle=HRRR%20Model%20Fields%20-%20Experimental&maxFcstLen=48&fcstStrLen=-1&domain=full&adtfn=1&threshold=&attfn=-1&wjet=0"'
    os.system(command)

# sleep for 60 seconds
time.sleep(60)

# download all products
for idx,prod in enumerate(products,0):

    if has_anal_prod[idx]:
        fRange = range(0,numFhours)
    else:
        fRange = range(1,numFhours)
    for f in fRange:
        f_str = str(f)
        if len(f_str) < 2:
            f_str = '0'+f_str
        baseFile = prod+'_f'+f_str+'.png'
        if baseFile not in localFileList:
            if debug:
                print >>sys.stderr,'Downloading ',baseFile
            try:
                command = 'wget '+hrrrUrl+'/'+baseFile
                if debug:
                    print >>sys.stderr, 'wget cmd: ',command
                os.system(command)
                # rename file and copy to catalog
                catalogDir = catalogBaseDir+'/'+date
                if not os.path.exists(catalogDir):
                    os.makedirs(catalogDir)
                catalogName = catalogPrefix+'.'+modelInitTime+'00.'+f_str+'_'+prod+'.png'
                shutil.copy(targetDir+'/'+baseFile,catalogDir+'/'+catalogName)
                if debug:
                    print >>sys.stderr, 'Copied ',catalogName,' to catalog dir'
            except Exception as e:
                print sys.stderr, "    wget failed, exception: ", e
                continue
            
