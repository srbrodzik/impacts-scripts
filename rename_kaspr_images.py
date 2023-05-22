#!/usr/bin/python3

import os
import shutil
from ftplib import FTP

# User inputs
test = False
debug = True
inDirBase = '/home/disk/bob/impacts/radar/sbu_images/kaspr/quicklooks'
tempDir = '/tmp'
dateList = ['20221215']
products = {'RHI_LDR':'rhi_ldr','RHI_ZDR':'rhi_zdr','RHI_dBZ':'rhi_dbz','RHI_phi_dp':'rhi_phidp',
            'RHI_rho_hv':'rhi_rhohv','RHI_rho_xh':'rhi_rhoxh','RHI_spectral_width':'rhi_sw',
            'RHI_velocity_dual':'rhi_veldp','RHI_velocity_single':'rhi_vel',
            'PPI_LDR':'ppi_ldr','PPI_ZDR':'ppi_zdr','PPI_dBZ':'ppi_dbz','PPI_phi_dp':'ppi_phidp',
            'PPI_rho_hv':'ppi_rhohv','PPI_rho_xh':'ppi_rhoxh','PPI_spectral_width':'ppi_sw',
            'PPI_velocity_dual':'ppi_veldp','PPI_velocity_single':'ppi_vel'}
catalog_prefix = 'radar.KaSPR'

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

# Open ftp connection to NCAR sever
if test:
    catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser,ftpCatalogPassword)
    catalogFTP.cwd(catalogDestDir)
else:
    catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
    catalogFTP.cwd(catalogDestDir)

for date in dateList:
    for dir in os.listdir(inDirBase+'/'+date):
        if dir.startswith('imagesetPPI') and os.path.isdir(inDirBase+'/'+date+'/'+dir):
            (junk,datetime) = dir.split('_')
            (date,time) = datetime.split('-')
            for file in os.listdir(inDirBase+'/'+date+'/'+dir):
                if file.startswith('Ka-band_pp_PPI') and file.endswith('png'):
                    print('file =',file)
                    (base,ext) = os.path.splitext(file)
                    parts = base.split('_')
                    if len(parts) == 4:
                        (band,pp,scan,field) = base.split('_')
                        prod = scan+'_'+field
                    elif len(parts) == 5:
                        (band,pp,scan,field1,field2) = base.split('_')
                        prod = scan+'_'+field1+'_'+field2
                    if prod in products:
                        fileNew = catalog_prefix+'.'+date+time[0:4]+'.'+products[prod]+ext
                        shutil.copy(inDirBase+'/'+date+'/'+dir+'/'+file,
                                    tempDir+'/'+fileNew)
                        # ftp file to catalog
                        ftpFile = open(os.path.join(tempDir,fileNew),'rb')
                        catalogFTP.storbinary('STOR '+fileNew,ftpFile)
                        ftpFile.close()
                        if debug:
                            print('   ftpd',fileNew,'to NCAR FC\n')

                        # remove file from tempDir
                        os.remove(os.path.join(tempDir,fileNew))

# Close ftp connection
catalogFTP.quit()


                    
