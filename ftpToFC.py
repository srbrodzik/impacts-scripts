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

# ftp kmlFile to Field Catalog
ftpFile = open(file,'rb')
catalogFTP.storbinary('STOR '+file,ftpFile)
ftpFile.close()

