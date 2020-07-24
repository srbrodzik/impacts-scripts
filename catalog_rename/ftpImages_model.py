#!/usr/bin/python3

import os
from ftplib import FTP

ftpCatalogServer = 'catalog.eol.ucar.edu'
catalogDestDir = '/pub/incoming/catalog/impacts'
localBaseDir = '/home/disk/funnel/impacts-website/archive_ncar/model'
#models = ['GFS_28km','HRRR_01km','HRRR_03km','NAM_12km','WRF_GFS_SBU_04km','WRF_GFS_SBU_12km','WRF_GFS_SBU_36km']
models = ['HRRR_01km']

ftp = FTP(ftpCatalogServer)
ftp.login()
ftp.cwd(catalogDestDir)

for model in models:
    for date in os.listdir(localBaseDir+'/'+model):
        if date.startswith('2020022'):
            os.chdir(localBaseDir+'/'+model+'/'+date)
            for filename in os.listdir(localBaseDir+'/'+model+'/'+date):
                if 'model' in filename:
                    print('filename = '+filename)
                    try:
                        fp = open(filename, 'rb')
                        res = ftp.storbinary("STOR " + filename, fp)
                        if not res.startswith('226 Transfer complete'):
                            print('Upload failed')
                            fp.close()
                
                    except ftplib.all_errors as e:
                        print ('FTP error:', e)

ftp.close()
        

