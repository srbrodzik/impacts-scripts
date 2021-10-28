#!/usr/bin/python

import os
import sys
from ftplib import FTP

# user inputs
jsonDir = '/home/disk/funnel/impacts-website/data_archive/nys_prof/2020/json_QC'
ftpCatalogServer = 'ftp.eol.ucar.edu'
ftpCatalogUser = 'anonymous'
catalogDestDir = '/pub/data/incoming/socrates'
#instrumentList = ['lidar','mwr']
instrumentList = ['mwr']
siteList = ['alba','bell','bron','buff','chaz','clym','eham','jord','oweg','quee',
            'redh','stat','ston','suff','tupp','want','webs']

for instrument in instrumentList:

    if os.path.isdir(jsonDir+'/'+instrument):

        # get list of sites
        sites = os.listdir(jsonDir+'/'+instrument)
            
        for site in sites:

            if site.lower() in siteList:
    
                print >>sys.stderr, 'site = ', site

                inDir = jsonDir+'/'+instrument+'/'+site+'/FOR_NCAR_ARCHIVE'
                os.chdir(inDir)

                # Open ftp connection
                catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
                catalogFTP.cwd(catalogDestDir)

                for file in os.listdir(inDir):

                    if file.endswith('.json'):
        
                        print >>sys.stderr, 'file = ', file

                        # ftp to EOL
                        ftpFile = open(file,'rb')
                        catalogFTP.storbinary('STOR '+file,ftpFile)
                        ftpFile.close()

                # Close ftp connection
                catalogFTP.quit()
                
