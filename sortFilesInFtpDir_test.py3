#!/usr/bin/python3

# MUST RUN THIS AS 'BRODZIK' FOR ACCESS TO FTP INCOMING DIRECTORY
# Tested for SBU Mobile
# Tested for 

import os
import sys
import shutil
import glob
from ftplib import FTP

test = True
ftpDir = '/home/disk/ftp/brodzik/incoming/impacts'
binDir = '/home/disk/bob/impacts/bin'
#webserverDirBase = '/home/disk/funnel/impacts'
#webserverDataDir = webserverDirBase+'/data_archive'
ncDirBase = '/home/disk/bob/impacts/upperair'
tempDir = '/tmp'
vert_lim = 7

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
        if file.endswith('tar.xz'):
            print('   processing RAXPOL data file')
            shutil.move(ftpDir+'/'+file,
                        '/home/disk/bob/impacts/sonde/'+file)            
        elif file.startswith('RAXPOL') and file.endswith('png'):
            print('   processing RAXPOL image file')
            shutil.move(ftpDir+'/'+file,
                        '/home/disk/bob/impacts/radar/raxpol/'+file)
        elif 'AVAPS' in file:
            print('   processing dropsonde file')
            if file.endswith('png'):
                ftpFile = open(os.path.join(ftpDir,file),'rb')
                catalogFTP.storbinary('STOR '+file,ftpFile)
                ftpFile.close()
            elif file.endswith('svg'):
                print('   svg file -- need to convert to gif or png')
            shutil.move(ftpDir+'/'+file,
                        '/home/disk/bob/impacts/sonde/'+file)
        elif file.endswith('tar'):
            print('   processing ER2 image tarball')
            shutil.move(ftpDir+'/'+file,
                        '/home/disk/bob/impacts/radar/er2/postFlight')
        elif file.startswith('aircraft.NASA_P3') and file.endswith('gif'):
            print('   ftp dropsonde to catalog')
            ftpFile = open(os.path.join(ftpDir,file),'rb')
            catalogFTP.storbinary('STOR '+file,ftpFile)
            ftpFile.close()
            os.remove(ftpDir+'/'+file)
        elif file.endswith('nc') or file.endswith('txt'):
            print('   processing sounding file')
            if 'windsond1' in file:
                file = file.replace('windsond1','windsonde1')
            elif 'windsond2' in file:
                file = file.replace('windsond2','windsonde2')
            elif file.startswith('OSW') and file.endswith('sharppy.txt'):
                print('Oswego sounding')
                (base,ext) = os.path.splitext(file)
                (dateStr,timeStr,junk) = base.split('_')
                site = dateStr[0:3]
                date = dateStr[3:]
                time = timeStr[0:2]+'00'
                fileNew = 'upperair.'+site+'_sonde.'+date+time+ext
                shutil.move(ftpDir+'/'+file,
                            ftpDir+'/'+fileNew)
                file = fileNew
            elif file.endswith('sharppy.txt'):
                file = file.replace('sharppy.txt','txt')
            elif file.startswith('GrawSonde'):
                # file naming convention: GrawSonde_RadarTruck_RTS_YYYYMMDD_hhmmss.nc
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
            elif file.startswith('UA'):
                # file naming conventions
                #    static site: UAETEC_YYYYMMDD_hhmm.txt
                #    mobile site: UAMBLE_YYYYMMDD_hhmm.txt
                fileTmp = file.replace('_','.')
                (site,day,time,junk,ext) = fileTmp.split('.')
                if site == 'UAETEC':
                    fileNew = 'upperair.UALB_sonde_fixed.'+day+time+'.'+ext
                elif site == 'UAMBLE':
                    fileNew = 'upperair.UALB_sonde_mobile.'+day+time+'.'+ext
                shutil.move(ftpDir+'/'+file,
                            ftpDir+'/'+fileNew)
                file = fileNew
                print('   renaming Albany file to:',file)
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
                    elif product == 'UALB_sonde_fixed':
                        format = 'Albany'
                        ncSubDir = 'ualbany'
                        dataDir = ncDirBase+'/'+ncSubDir+'/'+yyyymmdd
                        if not os.path.exists(dataDir):
                            os.makedirs(dataDir)
                    elif product == 'UALB_sonde_mobile':
                        format = 'Albany_mobile'
                        ncSubDir = 'ualbany'
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
                        print('   UMILL nc file =',file)
                    elif 'UMILL_windsonde' in product:
                        format = 'MUtxt_ws'
                        ncSubDir = 'umill'
                        dataDir = ncDirBase+'/'+ncSubDir+'/'+yyyymmdd
                        if not os.path.exists(dataDir):
                            os.makedirs(dataDir)
                        # create nc file & move text file to dataDir
                        #command = binDir+'/convert_millersville_sndg_to_netcdf.py '+ftpDir+' '+file+' '+ftpDir
                        #os.system(command)                        
                        #(base,ext) = os.path.splitext(file)
                        #shutil.move(ftpDir+'/'+file,
                        #            dataDir+'/'+file)
                        #file = base+'.nc'
                        print('   UMILL txt windsonde file =',file)
                    elif product == 'OSW_sonde':
                        print('   processing Oswego file')
                        format = 'Oswego'
                        ncSubDir = 'oswego'
                        dataDir = ncDirBase+'/'+ncSubDir+'/'+yyyymmdd
                        if not os.path.exists(dataDir):
                            os.makedirs(dataDir)
                    elif product == 'SBU_sonde_RadarTruck':
                        print('   processing SBU RadarTruck file')
                        format = 'SBUnc_mobile'
                        ncSubDir = 'sbu'
                        dataDir = ncDirBase+'/'+ncSubDir+'/'+yyyymmdd
                        if not os.path.exists(dataDir):
                            os.makedirs(dataDir)   
                    elif product == 'SBU_sonde_SBUSouthP':
                        format = 'SBUnc'
                        ncSubDir = 'sbu'
                        dataDir = ncDirBase+'/'+ncSubDir+'/'+yyyymmdd
                        if not os.path.exists(dataDir):
                            os.makedirs(dataDir)

                    if 'SBU_sonde' in product or 'UALB_sonde' in product:
                        parts = product.split('_')
                        productCat = parts[0]+'_'+parts[1]
                    else:
                        productCat = product
                            
                    # copy data file to data_archive
                    shutil.copy(ftpDir+'/'+file,
                                dataDir+'/'+file)
                    print('   copied',file,'to',dataDir)

                    # create skewt & move to NCAR catalog
                    skewtPath = tempDir
                    if not os.path.exists(skewtPath):
                         os.makedirs(skewtPath)
                    #command = binDir+'/plot_skewt.py --inpath '+ftpDir+' --infile '+file+' --outpath '+skewtPath+' --fmt '+format+' --hodo False'
                    command = binDir+'/plot_skewt_test.py --inpath '+ftpDir+' --infile '+file+' --outpath '+skewtPath+' --fmt '+format+' --hodo False --wb True --vlim '+str(vert_lim)
                    print('   command =',command)
                    os.system(command)
                    print('   created skewt and web bulb plots')
                        
                    # ftp skewt & wet bulb plot to NCAR catalog
                    if format == 'SBUnc':
                        catalogName = prefix+'.'+productCat+'.'+date+'.StonyBrook_NY_skewT.png'
                        catalogName_wb = prefix+'.'+productCat+'.'+date+'.StonyBrook_NY_Wet_Bulb.png'
                    elif format == 'Albany':
                        catalogName = prefix+'.'+productCat+'.'+date+'.Albany_NY_skewT.png'
                        catalogName_wb = prefix+'.'+productCat+'.'+date+'.Albany_NY_Wet_Bulb.png'
                    else:
                        catalogName = prefix+'.'+productCat+'.'+date+'.skewT.png'
                        catalogName_wb = prefix+'.'+productCat+'.'+date+'.Wet_Bulb.png'
                    flist = glob.glob(tempDir+'/upperair.'+productCat+'*.png')
                    for f in flist:
                        catalogName = os.path.basename(f)
                        if catalogName in [catalogName,catalogName_wb]:
                            ftpFile = open(os.path.join(tempDir,catalogName),'rb')
                            catalogFTP.storbinary('STOR '+catalogName,ftpFile)
                            ftpFile.close()
                            print('   ftped',catalogName,' to catalog')

                            shutil.move(os.path.join(tempDir,catalogName),
                                        os.path.join(dataDir,catalogName))
                            print('   moved',catalogName,' to ',dataDir)

                    # remove data file from ftpDir
                    os.remove(ftpDir+'/'+file)
                    print('   removed',file,'from ftp dir')

            except ValueError:
                #print sys.stderr, "   processing fails"
                if not os.path.exists(ftpDir+'/junk'):
                    os.mkdir(ftpDir+'/junk')
                shutil.move(ftpDir+'/'+file,ftpDir+'/junk'+'/'+file)
                continue
        

