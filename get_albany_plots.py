#!/usr/bin/python

import os
import sys
import time
from datetime import timedelta
from datetime import datetime
import shutil
from ftplib import FTP

# User inputs
debug = 1
test = False
baseUrl = 'http://www.atmos.albany.edu/student/mbartolini/research/impacts/images'
tempDir = '/tmp'
catMrrPrefix = 'radar.MRR'
catParsivelPrefix = 'surface.Parsivel'

# Open ftp connection
if test:
    ftpCatalogServer = 'ftp.atmos.washington.edu'
    ftpCatalogUser = 'anonymous'
    ftpCatalogPassword = 'brodzik@uw.edu'
    catalogDestDir = 'brodzik/incoming/impacts'
else:
    ftpCatalogServer = 'catalog.eol.ucar.edu'
    ftpCatalogUser = 'anonymous'
    catalogDestDir = '/pub/incoming/catalog/impacts'

if test:
    catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser,ftpCatalogPassword)
    catalogFTP.cwd(catalogDestDir)
else:
    catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
    catalogFTP.cwd(catalogDestDir)

# Move to tempDir
os.chdir(tempDir)
    
# get yesterday's date in PST
# cron runs at 2000 PST or 0100 UCT
# images created for prior day
dateStr = datetime.strftime(datetime.now() - timedelta(1), '%Y%m%d')
#dateStr = now.strftime("%Y%m%d")
#dateStr = '20220114'
if debug:
    print("dateStr = ", dateStr)

mrrFiles = [catMrrPrefix+'.'+dateStr+'0000.UAlbany_CFAD.png',
            catMrrPrefix+'.'+dateStr+'0000.UAlbany_time_ht.png']
parsivelFiles = [catParsivelPrefix+'.'+dateStr+'0000.UAlbany_Parsivel_vs_MRR.png',
                 catParsivelPrefix+'.'+dateStr+'0000.UAlbany.png',
                 catParsivelPrefix+'.'+dateStr+'0000.UAlbany_vel_diam_hist.png',
                 catParsivelPrefix+'.'+dateStr+'0000.UAlbany_psd_rrdbz.png']

for file in mrrFiles:
    url = baseUrl+'/mrr/'+file
    command = 'wget '+url
    os.system(command)
    ftpFile = open(os.path.join(tempDir,file),'rb')
    catalogFTP.storbinary('STOR '+file,ftpFile)
    ftpFile.close()
    os.remove(os.path.join(tempDir,file))

for file in parsivelFiles:
    url = baseUrl+'/parsivel/'+file
    command = 'wget '+url
    os.system(command)
    ftpFile = open(os.path.join(tempDir,file),'rb')
    catalogFTP.storbinary('STOR '+file,ftpFile)
    ftpFile.close()
    os.remove(os.path.join(tempDir,file))

# Close ftp connection
catalogFTP.quit()
 
