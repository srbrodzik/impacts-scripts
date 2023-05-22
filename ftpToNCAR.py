#!/usr/bin/python3

import os
import sys
from ftplib import FTP

# Read input args
numargs = len(sys.argv)
if numargs != 2:
    print('Usage: {} [file]'.format(sys.argv[0]))
    exit()
else:
    file = sys.argv[1]
print('{} {}'.format('file = ',file))

test = False

# NCAR ftp data area inputs
ftpCatalogServer = 'catalog.eol.ucar.edu'
ftpCatalogUser = 'anonymous'
catalogDestDir = '/pub/incoming/catalog/impacts'

# Open ftp connection
catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
catalogFTP.cwd(catalogDestDir)

# ftp to NCAR ftp data area
ftpFile = open(file,'rb')
catalogFTP.storbinary('STOR '+file,ftpFile)
ftpFile.close()

# Close ftp connection
catalogFTP.quit()

