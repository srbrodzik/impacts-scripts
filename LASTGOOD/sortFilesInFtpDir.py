#!/usr/bin/python

# MUST RUN THIS AS 'BRODZIK' FOR ACCESS TO FTP INCOMING DIRECTORY

import os
import sys
import shutil
from ftplib import FTP

test = False
ftpDir = '/home/disk/ftp/brodzik/incoming/impacts'
binDir = '/home/disk/bob/impacts/bin'
#webserverDirBase = '/home/disk/funnel/impacts'
#webserverDataDir = webserverDirBase+'/data_archive'
ncDirBase = '/home/disk/bob/impacts/upperair'
tempDir = '/tmp'

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

# Change permissions on all files and rename SBU file names
#for file in os.listdir(ftpDir):
#    if os.path.isfile(ftpDir+'/'+file):
#        cmd = 'chmod a+rw '+ftpDir+'/'+file
#        os.system(cmd)
            
for file in os.listdir(ftpDir):
    print('file =', file)
    if os.path.isfile(ftpDir+'/'+file):
        if file.endswith('tar'):
            shutil.move(ftpDir+'/'+file,
                        '/home/disk/bob/impacts/radar/er2/postFlight')
        elif file.startswith('aircraft.NASA_P3') and file.endswith('gif'):
            # ftp dropsonde to catalog
            ftpFile = open(os.path.join(ftpDir,file),'rb')
            catalogFTP.storbinary('STOR '+file,ftpFile)
            ftpFile.close()
            os.remove(ftpDir+'/'+file)
        elif file.endswith('nc') or file.endswith('txt'):
            print('   processing file')
            if 'windsond1' in file:
                file = file.replace('windsond1','windsonde1')
            elif 'windsond2' in file:
                file = file.replace('windsond2','windsonde2')
            if file.endswith('sharppy.txt'):
                file = file.replace('sharppy.txt','txt')
            if file.startswith('GrawSonde'):
                (base,ext) = os.path.splitext(file)
                (junk1,site,junk2,date,time) = base.split('_')
                time = time[0:4]
                if site == 'RadarTruck':
                    fileNew = 'upperair.SBU_sonde_RadarTruck.'+date+time+'.nc'
                elif site == 'SBUSouthP':
                    fileNew = 'upperair.SBU_sonde_SBUSouthP.'+date+time+'.nc'
                shutil.move(ftpDir+'/'+file,
                            ftpDir+'/'+fileNew)
                file = fileNew
                print('   renaming SBU file to:',file)
            try:
                (prefix,product,date,suffix) = file.split('.')
                yyyymmdd = date[0:8]

                if 'sonde' in product:
                    print('   processing sonde')
                    
                    # prepare to create skewt
                    if product == 'UILL_sonde':
                        format = 'UIUCnc'
                        ncSubDir = 'uill'
                        dataDir = ncDirBase+'/'+ncSubDir+'/'+yyyymmdd
                        if not os.path.exists(dataDir):
                            os.makedirs(dataDir)
                    elif product == 'UMILL_sonde':
                        format = 'MUnc'
                        ncSubDir = 'umill'
                        dataDir = ncDirBase+'/'+ncSubDir+'/'+yyyymmdd
                        if not os.path.exists(dataDir):
                            os.makedirs(dataDir)
                        # create nc file & move text file to dataDir
                        command = binDir+'/convert_millersville_sndg_to_netcdf.py '+ftpDir+' '+file+' '+ftpDir
                        os.system(command)                        
                        (base,ext) = os.path.splitext(file)
                        shutil.move(ftpDir+'/'+file,
                                    dataDir+'/'+file)
                        file = base+'.nc'
                        print('UMILL nc file = ',file)
                    elif product == 'UMILL_windsonde':
                        format = 'MUtxt_ws'
                        ncSubDir = 'umill'
                        dataDir = ncDirBase+'/'+ncSubDir+'/'+yyyymmdd
                        if not os.path.exists(dataDir):
                            os.makedirs(dataDir)
                        # create nc file & move text file to dataDir
                        #command = binDir+'/convert_millersville_sndg_to_netcdf.py '+ftpDir+' '+file+' '+ftpDir
                        os.system(command)                        
                        #(base,ext) = os.path.splitext(file)
                        shutil.move(ftpDir+'/'+file,
                                    dataDir+'/'+file)
                        #file = base+'.nc'
                        print('UMILL txt windsonde file = ',file)
                    elif product == 'SBU_sonde_RadarTruck':
                        print('   processing SBU RadarTruck file')
                        format = 'SBUnc'
                        ncSubDir = 'sbu'
                        dataDir = ncDirBase+'/'+ncSubDir+'/'+yyyymmdd
                        if not os.path.exists(dataDir):
                            os.makedirs(dataDir)   
                    elif product == 'SBU_sonde_SBUSouthP':
                        format = 'SBUnc_static'
                        ncSubDir = 'sbu'
                        dataDir = ncDirBase+'/'+ncSubDir+'/'+yyyymmdd
                        if not os.path.exists(dataDir):
                            os.makedirs(dataDir)

                    if 'SBU_sonde' in product:
                        parts = product.split('_')
                        productCat = parts[0]+'_'+parts[1]
                    else:
                        productCat = product
                            
                    # create skewt & move to NCAR catalog
                    skewtPath = tempDir
                    if not os.path.exists(skewtPath):
                         os.makedirs(skewtPath)
                    if format == 'MUtxt_ws':
                        command = binDir+'/2020_VERSIONS_MOD/WINDSONDE/skewplot.py --file '+ftpDir+'/'+file+' --outpath '+skewtPath+' --format '+format+' --parcel False --hodograph False'
                    else:
                        command = binDir+'/2020_VERSIONS_MOD/skewplot.py --file '+ftpDir+'/'+file+' --outpath '+skewtPath+' --format '+format+' --parcel False --hodograph False'
                    print('command = ',command)
                    os.system(command)
                        
                    # ftp skewt to NCAR catalog
                    catalogName = prefix+'.'+productCat+'.'+date+'.skewT.png'
                    if catalogName in os.listdir(tempDir):
                        ftpFile = open(os.path.join(tempDir,catalogName),'rb')
                        catalogFTP.storbinary('STOR '+catalogName,ftpFile)
                        ftpFile.close()
                        shutil.move(os.path.join(tempDir,catalogName),
                                    os.path.join(dataDir,catalogName))
                        print('   moved ',catalogName,' to ',dataDir)
                    else:
                        print('No skewt created for ',file)

                    # move data file to data_archive
                    shutil.move(ftpDir+'/'+file,
                                dataDir+'/'+file)
                    print('   moved ',file,' to ',dataDir)

            except ValueError:
                #print sys.stderr, "   processing fails"
                if not os.path.exists(ftpDir+'/junk'):
                    os.mkdir(ftpDir+'/junk')
                shutil.move(ftpDir+'/'+file,ftpDir+'/junk'+'/'+file)
                continue
        

