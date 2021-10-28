#!/usr/bin/python

import os
import sys
from ftplib import FTP

# user inputs
ncDir = '/home/disk/funnel/impacts-website/data_archive/nys_ground/2020/netcdf_QC'
ftpCatalogServer = 'ftp.eol.ucar.edu'
ftpCatalogUser = 'anonymous'
catalogDestDir = '/pub/data/incoming/socrates'

# get list of sites
for site in os.listdir(ncDir):

    if len(site) == 4:
            
        print >>sys.stderr, 'site = ', site

        inDir = ncDir+'/'+site
        os.chdir(inDir)

        # Open ftp connection
        catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
        catalogFTP.cwd(catalogDestDir)

        for file in os.listdir(inDir):

            if file.endswith('.nc'):
        
                print >>sys.stderr, 'file = ', file

                # ftp to EOL
                ftpFile = open(file,'rb')
                catalogFTP.storbinary('STOR '+file,ftpFile)
                ftpFile.close()

        # Close ftp connection
        catalogFTP.quit()
                
