#!/usr/bin/python3

import os
from ftplib import FTP

ftpCatalogServer = 'catalog.eol.ucar.edu'
catalogDestDir = '/pub/incoming/catalog/impacts'
localBaseDir = '/home/disk/funnel/impacts-website/archive_ncar/satellite/GOES-16'

ftp = FTP(ftpCatalogServer)
ftp.login()
ftp.cwd(catalogDestDir)

for date in os.listdir(localBaseDir):
    if date.startswith('20200227') or date.startswith('20200228') or date.startswith('20200229'):
        os.chdir(localBaseDir+'/'+date)
        for filename in os.listdir(localBaseDir+'/'+date):
            if 'GOES' in filename:
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
        

