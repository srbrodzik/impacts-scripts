#!/usr/bin/python3

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
# 2m Temp + 10m Wind                   1

import os
import sys
import time
import shutil
from ftplib import FTP
import glob

if len(sys.argv) != 2:
    print("Useage: ", sys.argv[0], " <modelruntime (YYYYMMDDhh)>")
    sys.exit()
else:
    modelInitTime = sys.argv[1]
    date = modelInitTime[0:8]
    initHour = modelInitTime[8:10]
    print("modelInitTime = ", modelInitTime)
    print("date = ", date)
    print("initHour = ",initHour)

# User inputs
debug = True
test = False
hrrrBaseUrl = 'https://rapidrefresh.noaa.gov/hrrr/NEST/for_web/hrrr_nest2_jet'
hrrrUrl = hrrrBaseUrl+'/'+modelInitTime+'/full'
products = ['cref_sfc','G114bt_sat','ctop','temp_925','temp_850','temp_700',
            'wind_250','lcc_sfc','mcc_sfc','hcc_sfc','temp_2m']
has_anal_prod = [1,1,1,1,1,1,1,1,1,1,1]
numFhours = 46
#numFhours = 33
ext = 'png'
tempDir = '/tmp'
catalogPrefix = 'model.HRRR_01km'

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

# go to tempDir
os.chdir(tempDir)

# request all products
for idx,prod in enumerate(products,0):

    #command = 'wget "https://rapidrefresh.noaa.gov/hrrr/HRRR/displayMapLocalDiskDateDomainZipTZA.cgi?keys=hrrr_nest2_jet:&runtime='+modelInitTime+'&plot_type=all'+prod+'&fcst='+initHour+'&time_inc=60&num_times=46&model=hrrr&ptitle=HRRR%20Model%20Fields%20-%20Experimental&maxFcstLen=48&fcstStrLen=-1&domain=full&adtfn=1&threshold=&attfn=-1&wjet=0"'
    command = 'wget "https://rapidrefresh.noaa.gov/hrrr/HRRR/displayMapLocalDiskDateDomainZipTZA.cgi?keys=hrrr_nest2_jet:&runtime='+modelInitTime+'&plot_type=all'+prod+'&fcst='+initHour+'&time_inc=60&num_times='+str(numFhours)+'&model=hrrr&ptitle=HRRR%20Model%20Fields%20-%20Experimental&maxFcstLen='+str(numFhours)+'&fcstStrLen=-1&domain=full&adtfn=1&threshold=&attfn=-1&wjet=0"'
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
        if debug:
            print('Downloading',baseFile)
        try:
            command = 'wget '+hrrrUrl+'/'+baseFile
            if debug:
                print('wget cmd: ',command)
            os.system(command)
            
            # rename file
            catalogName = catalogPrefix+'.'+modelInitTime+'00.0'+f_str+'_'+prod+'.png'
            shutil.move(tempDir+'/'+baseFile,tempDir+'/'+catalogName)
            
            # Open ftp connection to NCAR sever
            if test:
                catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser,ftpCatalogPassword)
                catalogFTP.cwd(catalogDestDir)
            else:
                catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
                catalogFTP.cwd(catalogDestDir)

            # ftp file to catalog
            ftpFile = open(os.path.join(tempDir,catalogName),'rb')
            catalogFTP.storbinary('STOR '+catalogName,ftpFile)
            ftpFile.close()
            if debug:
                print('ftped',catalogName,'to field catalog')
                
            # Close ftp connection
            catalogFTP.quit()
                
            # remove file
            os.remove(tempDir+'/'+catalogName)
            
        except Exception as e:
            print("    wget failed, exception: ", e)
            continue

# remove files
for file in glob.glob(tempDir+'/*'):
    if file.startswith(tempDir+'/displayMap'):
        os.remove(file)
 
