#!/usr/bin/python

import os
import sys
from ftplib import FTP

# user inputs
csvDir = '/home/disk/funnel/impacts-website/data_archive/nys_ground/2020/csv_QC'
ftpCatalogServer = 'ftp.eol.ucar.edu'
ftpCatalogUser = 'anonymous'
catalogDestDir = '/pub/data/incoming/socrates'

# get list of dates
for date in os.listdir(csvDir):

    if date.startswith('20200'):
            
        print >>sys.stderr, 'date = ', date

        inDir = csvDir+'/'+date
        os.chdir(inDir)

        # Open ftp connection
        catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
        catalogFTP.cwd(catalogDestDir)

        for file in os.listdir(inDir):

            if file.endswith('.csv'):
        
                print >>sys.stderr, 'file = ', file

                # ftp to EOL
                ftpFile = open(file,'rb')
                catalogFTP.storbinary('STOR '+file,ftpFile)
                ftpFile.close()

        # Close ftp connection
        catalogFTP.quit()
                
