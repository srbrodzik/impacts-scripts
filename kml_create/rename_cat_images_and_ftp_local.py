#!/usr/bin/python

import shutil
import sys
import os
from ftplib import FTP

test = False
inDir = '/media/usb/data/raw/images'
dict = {'goes_vis': {'category':'gis','platform':'GOES-16',    'product':'vis_ch01'},
        'goes_ir':  {'category':'gis','platform':'GOES-16',    'product':'ir_ch13'},
        'mrms_refl_gis':{'category':'gis','platform':'MRMS_MOSAIC','product':'DBZ'},
        'mrms_refl_radar':{'category':'radar','platform':'MRMS_MOSAIC','product':'DBZ'}}

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

os.chdir(inDir)
for file in os.listdir(inDir):
    if os.path.isfile(inDir+'/'+file) and not file.startswith('_'):
        if file.startswith('gis.GOES16_CH01') and file.endswith('png'):
            print(file)
            type = 'goes_vis'

        elif file.startswith('gis.GOES16_CH13') and file.endswith('png'):
            print(file)
            type = 'goes_ir'

        elif file.startswith('gis.DBZ') and file.endswith('png'):
            print(file)
            type = 'mrms_refl_gis'

        elif file.startswith('radar.DBZ') and file.endswith('png'):
            print(file)
            type = 'mrms_refl_radar'

        (cat,plat1,plat2,plat3,datetime,ext) = file.split('.')
        if len(datetime) > 12:
            datetime = datetime[0:12]
        date = datetime[0:8]
        catFile = dict[type]['category']+'.'+dict[type]['platform']+'.'+datetime+'.'+dict[type]['product']+'.'+ext
        shutil.move(file,catFile)
        ftpFile = open(os.path.join(inDir,catFile),'rb')
        catalogFTP.storbinary('STOR '+catFile,ftpFile)
        ftpFile.close()
        outDir = inDir+'/'+date
        if not os.path.isdir(outDir):
            os.makedirs(outDir)
        shutil.move(inDir+'/'+catFile,
                    outDir+'/'+catFile)



