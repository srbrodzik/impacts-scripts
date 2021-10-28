#!/usr/bin/python

import os
import sys
from ftplib import FTP

# user inputs
ncDir = '/home/disk/funnel/impacts-website/data_archive/nys_prof/2020/netcdf_QC'
ftpCatalogServer = 'catalog.eol.ucar.edu'
ftpCatalogUser = 'anonymous'
catalogDestDir = '/pub/incoming/catalog/impacts'
siteList = ['alba','bell','bron','buff','chaz','clym','eham','jord','oweg','quee',
            'redh','stat','ston','suff','tupp','want','webs']

# get list of sites in ncDir
sites = os.listdir(ncDir)
            
for site in sites:

    if site in siteList:
    
        print >>sys.stderr, 'site = ', site

        os.chdir(ncDir+'/'+site)

        # Open ftp connection
        catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
        catalogFTP.cwd(catalogDestDir)

        for file in os.listdir(ncDir+'/'+site):

            if file.endswith('.nc'):
        
                print >>sys.stderr, 'file = ', file

                # ftp to EOL
                ftpFile = open(file,'rb')
                catalogFTP.storbinary('STOR '+file,ftpFile)
                ftpFile.close()

        # Close ftp connection
        catalogFTP.quit()
                
