#!/usr/bin/python3

import os
import sys
from ftplib import FTP

if len(sys.argv) != 2:
    print('Usage: sys.argv[0] [YYYYMMDD]')
    sys.exit()
else:
    date = sys.argv[1]

ftpCatalogServer = 'catalog.eol.ucar.edu'
ftpCatalogUser = 'anonymous'
catalogDestDir = '/pub/incoming/catalog/impacts'

catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
catalogFTP.cwd(catalogDestDir)

inDirBase = '/home/disk/bob/impacts/images/asos_isu'

"""
sites = ['Atlantic_City_NJ','Albany_NY','Scranton_PA','Boston_Logan_MA','Binghamton_NY',
         'Buffalo_NY','BWI_International_MD','Columbus_OH','Concord_NH','Reagan_National_VA',
         'Detroit_Metropolitan_MI','Newark_International_NJ','Georgetown_DE','Hartford_CT',
         'Lincoln_IL','Indianapolis_International_IN','Islip_Airport_NY','JFK_International_NY',
         'LaGuardia_Airport_NY','Norfolk_VA','Philadelphia_International_PA',
         'Pittsburgh_International_PA','Portland_ME','Richmond_International_VA','Wallops_FF_VA',
         'Bradley_International_CT','Detroit_Coleman_Municipal_MI']
"""
sites = ['Richmond_International_VA']

#for date in os.listdir(inDirBase):
if os.path.isdir(inDirBase+'/'+date):
    inDir = inDirBase+'/'+date
    for file in os.listdir(inDir):
        if file.endswith('png'):
            (catgory,platform,date,product,ext) = file.split('.')
            product = product.replace('ASOS_','')
            if product in sites:
                print('{} {}'.format('ftp-ing file =',file))
                ftpFile = open(os.path.join(inDir,file),'rb')
                catalogFTP.storbinary('STOR '+file,ftpFile)
                ftpFile.close()

catalogFTP.quit()


                    
         
