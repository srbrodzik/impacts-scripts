#!/usr/bin/python3

"""
This code takes a zip file of HALO images as input, unzips it, renames the 
files and ftp's them to the NCAR server for posting to the IMPACTS Field 
Catalog
"""

import os
import sys
from zipfile import ZipFile
from ftplib import FTP
import shutil

if len(sys.argv) != 2:
    print('Useage: ',sys.argv[0],' [zipDir] [takeoffTime]')
    sys.exit()
else:
    zipDir = sys.argv[1]
    takeoffTime = sys.argv[3]

# FOR TESTING
zipDir = '/home/disk/ftp/incoming/brodzik/impacts'
takeoffTime = '1600'

# User inputs
test = False
tempDir = '/tmp'
prefix = 'aircraft.NASA_P3'
products = {'F1_532_bsr_3D':'HALO_aer_scat_ratio_3D_532nm',
            'F1_RHi_v':'HALO_rh_over_ice',
            'F1_RHw_v':'HALO_rh_over_water',
            'F1_aer_dep532':'HALO_aer_depol_ratio_532nm',
            'F1_bsc532':'HALO_aer_backsctr_532nm',
            'F1_bsc532cs':'HALO_aer_backsctr_532nm_cloud_screened',
            'F1_dep532':'HALO_total_depol_ratio_532nm',
            'F1_flight_track':'HALO_flight_track',
            'F1_h2o_mmr_v':'HALO_water_vapor_mix_ratio',
            'F1_h2o_mmr_v_3D':'HALO_water_vapor_mix_ratio_3D',
            'HALO_532aot_map':'HALO_aer_opt_thick_532nm',
            'HALO_PWV_clear_v_map':'HALO_precip_wv_cloud_free',
            'HALO_PWV_cloudy_v_map':'HALO_precip_wv_cloud'}

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

# Go to zip file directory
os.chdir(zipDir)

for file in os.listdir(zipDir):
    if file.endswith('.zip'):
        (zipSubDir,ext) = os.path.splitext(file)
        try:
            with ZipFile(file,'r') as zipObj:
                zipObj.extractall()
            os.remove(file)
            if os.path.exists('__MACOSX'):
                shutil.rmtree('__MACOSX')
            # Rename and ftp each image
            os.chdir(zipDir+'/'+zipSubDir)
            for file in os.listdir():
                if file.endswith('.png'):
                    # Rename file
                    (base,ext) = os.path.splitext(file)
                    parts = base.split('_')
                    date = parts[0]
                    origProd = base.replace(date+'_','')
                    fileNew = prefix+'.'+date+takeoffTime+'.'+products[origProd]+ext
                    shutil.move(file,fileNew)
                    # ftp to NCAR server
                    ftpFile = open(os.path.join(zipDir,zipSubDir,fileNew),'rb')
                    catalogFTP.storbinary('STOR '+fileNew,ftpFile)
                    ftpFile.close()
                    #os.remove(os.path.join(zipDir,zipSubDir,fileNew))
        except:
            print('Bad zip file')

# Remove zipSubDir
os.chdir(tempDir)
os.remove(zipDir+'/'+zipSubDir

# Close ftp connection
catalogFTP.quit()
    
    
