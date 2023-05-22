#!/usr/bin/python3

import os
from ftplib import FTP

indir = '/home/disk/bob/impacts/raw/nys_ground_2021/netcdf_by_site'

ftpCatalogServer = 'ftp.eol.ucar.edu'
ftpCatalogUser = 'anonymous'
catalogDestDir = '/pub/data/incoming/impacts'

# Open ftp connection
catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
catalogFTP.cwd(catalogDestDir)

for site in os.listdir(indir):
    print(site)
    dir = indir+'/'+site
    if os.path.isdir(dir):
        for file in os.listdir(dir):
            if file.startswith('nysm_standard'):
                print(file)
                ftpFile = open(dir+'/'+file,'rb')
                catalogFTP.storbinary('STOR '+file,ftpFile)
                ftpFile.close()

# Close ftp connection
catalogFTP.quit()
