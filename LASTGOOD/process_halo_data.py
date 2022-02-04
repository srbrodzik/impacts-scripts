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

# Field Catalog inputs
ftpCatalogServer = 'catalog.eol.ucar.edu'
ftpCatalogUser = 'anonymous'
catalogDestDir = '/pub/incoming/catalog/impacts'
# For testing
#ftpCatalogServer = 'ftp.atmos.washington.edu'
#ftpCatalogUser = 'anonymous'
#catalogDestDir = 'brodzik/incoming/impacts'

# Other inputs
prefix = 'aircraft.NASA_P3'
products = {'F1_532_bsr_3D':'HALO_aerosol_scat_ratio_3D_532nm',
            'F1_AOT_hi_col532':'HALO_column_aerosol_opt_thick_532nm',
            'F1_AerosolID':'HALO_aerosol_type',
            'F1_Angstrom_Dust':'HALO_angstrom_coef_of_dust_particles',
            'F1_Angstrom_Spherical':'HALO_angstrom_coef_of_spherical_particles',
            'F1_Dust_Mixing_Ratio':'HALO_dust_mixing_ratio',
            'F1_RHi_v':'HALO_rh_over_ice',
            'F1_RHw_v':'HALO_rh_over_water',
            'F1_Sa532':'HALO_extinction_backscatter_ratio_532nm',
            'F1_aer_dep1064':'HALO_aerosol_depol_ratio_1064nm',
            'F1_aer_dep532':'HALO_aerosol_depol_ratio_532nm',
            'F1_aer_dep_ratio1064_532':'HALO_ratio_of_depol_ratios',
            'F1_bsc1064':'HALO_aerosol_backscatter_1064nm',
            'F1_bsc532':'HALO_aerosol_backscatter_532nm',
            'F1_bsr1064':'HALO_aerosol_scat_ratio_1064nm',
            'F1_bsr532':'HALO_aerosol_scat_ratio_532nm',
            'F1_dep1064':'HALO_total_depol_ratio_1064nm',
            'F1_dep532':'HALO_total_depol_ratio_532nm',
            'F1_ext1064':'HALO_aerosol_extinction_1064nm',
            'F1_ext532':'HALO_aerosol_extinction_532nm',
            'F1_flight_track':'HALO_flight_track',
            'F1_h2o_mmr_v':'HALO_water_vapor_mix_ratio',
            'F1_h2o_mmr_v_3D':'HALO_water_vapor_mix_ratio_3D',
            'F1_total_attn_bsc1064':'HALO_total_atten_backscatter_1064nm',
            'F1_total_attn_bsc532':'HALO_total_atten_backscatter_532nm',
            'F1_wvd1064_532':'HALO_backscatter_angstrom_exp',
            'HALO_532aot_map':'HALO_aerosol_opt_thick_532nm',
            'HALO_PWV_clear_v_map':'HALO_precip_wv_cloud_free',
            'HALO_PWV_cloudy_v_map':'HALO_precip_wv_cloud'}

if len(sys.argv) != 3:
    print('Useage: ',sys.argv[0],' [zipDir] [zipFile] [takeoffTime]')
    sys.exit()
else:
    zipDir = sys.argv[1]
    zipFile = sys.argv[2]
    takeoffTime = sys.argv[3]

# For testing
#zipDir = '/home/disk/meso-home/brodzik/impacts/Data/HALO/tempdir'
#zipFile = 'CPEXAW-HALO-images_DC8_20210828_20210829_RA.zip'
#takeoffTime = '1201'
    
# Open ftp connection to NCAR sever
catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
catalogFTP.cwd(catalogDestDir)

# Go to zip file directory
os.chdir(zipDir)

if zipFile.endswith('.zip'):
    # unzip zipFile
    (zipSubDir,ext) = os.path.splitext(zipFile)
    with ZipFile(zipFile,'r') as zipObj:
        zipObj.extractall()
    os.remove(zipFile)
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
            os.remove(os.path.join(zipDir,zipSubDir,fileNew))
            
# Close ftp connection
catalogFTP.quit()
    
    
