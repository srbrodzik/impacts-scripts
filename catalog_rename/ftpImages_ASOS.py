#!/usr/bin/python3

import os
from ftplib import FTP

ftpCatalogServer = 'catalog.eol.ucar.edu'
ftpCatalogUser = 'anonymous'
catalogDestDir = '/pub/incoming/catalog/impacts'
localBaseDir = '/home/disk/funnel/impacts-website/archive_ncar/surface/Meteogram'
#filename = 'radar.DTX-NEXRAD.202002011719.DBZ.gif'
siteList = ['Atlantic_City_NJ','Albany_NY','Scranton_PA','Boston_MA','Binghamton_NY','Buffalo_NY',
            'BWI_International_MD','Columbus_OH','Concord_NH','Reagan_National_VA',
            'Detroit_Coleman_Municipal_MI','Newark_International_NJ','Georgetown_DE',
            'Bradley_International_CT','Indianapolis_International_IN','Islip_Airport_NY',
            'JFK_International_NY','LaGuardia_Airport_NY','Norfolk_VA','Peoria_International_IL',
            'Philadelphia_International_PA','Pittsburgh_International_PA','Portland_ME',
            'Richmond_International_VA','Wallops_FF_VA']

catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
catalogFTP.cwd(catalogDestDir)

for date in os.listdir(localBaseDir):
    if date.startswith('20200215'):
        os.chdir(localBaseDir+'/'+date)
        for filename in os.listdir(localBaseDir+'/'+date):
            #print(filename)
            if filename.startswith('surface'):
                (category,platform,datetime,product,ext) = filename.split('.')
                site = product.replace('ASOS_','')
                if 'ASOS' in filename and (site in siteList):
                    print('filename = '+filename)
                    try:
                        localFilePath = localBaseDir+'/'+date+'/'+filename
                        ftpFile = open(localFilePath,'rb')
                        catalogFTP.storbinary('STOR '+filename,ftpFile)
                        ftpFile.close()
                    
                        #fp = open(filename, 'rb')
                        #res = ftp.storbinary("STOR " + filename, fp)
                        #if not res.startswith('226 Transfer complete'):
                        #    print('Upload failed')
                        #    fp.close()
                
                    except ftplib.all_errors as e:
                        print ('FTP error:', e)

catalogFTP.quit()
        
#surface.Meteogram.202001010000.ASOS_Albany_NY.png
#surface.Meteogram.202001010000.ASOS_Norfolk_VA.png
