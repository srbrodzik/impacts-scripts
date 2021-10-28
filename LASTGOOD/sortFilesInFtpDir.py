#!/usr/bin/python

import os
import sys
import shutil

ftpDir = '/home/disk/ftp/brodzik/incoming'
webserverDirBase = '/home/disk/funnel/impacts'
webserverImageDir = webserverDirBase+'/archive'
webserverDataDir = webserverDirBase+'/data_archive'

# Change permissions on all files and rename SBU soundings
for file in os.listdir(ftpDir):
    if os.path.isfile(ftpDir+'/'+file):
        cmd = 'chmod a+rw '+ftpDir+'/'+file
        os.system(cmd)
        if file.startswith('GrawSonde'):
            (base,ext) = os.path.splitext(file)
            (product,junk,date,time) = base.split('_')
            newName = 'research.sounding.'+date+time+'.SBU_Mobile'+ext
            os.rename(ftpDir+'/'+file,ftpDir+'/'+newName)
            
for file in os.listdir(ftpDir):
    #print sys.stderr, "file = ", file
    if os.path.isfile(ftpDir+'/'+file):
        if file.endswith('pdf') or file.endswith('.jpg') or file.endswith('png') or file.endswith('gif') or file.endswith('nc'):
            #print sys.stderr, "   processing file"
            try:
                (prefix,product,date,category,suffix) = file.split('.')
                yyyymmdd = date[0:8]

                # soundings get handled differently
                if product == 'sounding' and suffix == 'nc':
                    # create skewt
                    if category == 'UIUC_Mobile':
                        format = 'UIUCnc'
                    elif category == 'SBU_Mobile':
                        format = 'SBUnc'
                    skewtPath = webserverImageDir+'/'+prefix+'/skewt/'+yyyymmdd
                    if not os.path.exists(skewtPath):
                         os.makedirs(skewtPath)
                    command = '/usr/bin/python /home/disk/bob/impacts/bin/skewplot.py --file '+ftpDir+'/'+file+' --outpath '+skewtPath+' --format '+format+' --parcel False --hodograph False'
                    os.system(command)
                    
                    # rename skewt for catalog
                    for plot in os.listdir(skewtPath):
                        if plot.startswith('upperair'):
                            plotNew = plot.replace('upperair.SkewT','research.skewt')
                            os.rename(skewtPath+'/'+plot,skewtPath+'/'+plotNew)
                            
                    # create nc output dir if necessary
                    dataDir = webserverDataDir+'/soundings/impacts/'+yyyymmdd
                    if not os.path.exists(dataDir):
                        os.makedirs(dataDir)
                        
                    # move nc file to data_archive
                    time = date[8:12]
                    ncFile = 'IMPACTS_sounding_'+yyyymmdd+'_'+time+'_'+category+'.nc'
                    shutil.move(ftpDir+'/'+file,dataDir+'/'+ncFile)
                    
                else:
                    # create output dir if necessary
                    imageDirBase = webserverImageDir+'/'+prefix+'/'+product
                    imageDir = imageDirBase+'/'+yyyymmdd
                    if not os.path.exists(imageDir):
                        os.makedirs(imageDir)
                        if product == 'science_plan':
                            shutil.copy(imageDirBase+'/index.php',imageDir)                    
                    
                    # if science_plan, make new link        
                    if product == 'science_plan':
                        os.unlink(imageDirBase+'/DailySciencePlan.pdf')
                        os.symlink(imageDir+'/'+file,imageDirBase+'/DailySciencePlan.pdf')

                    # move file to archive
                    shutil.move(ftpDir+'/'+file,imageDir+'/'+file)
                    
            except ValueError:
                #print sys.stderr, "   processing fails"
                if not os.path.exists(ftpDir+'/junk'):
                    os.mkdir(ftpDir+'/junk')
                shutil.move(ftpDir+'/'+file,ftpDir+'/junk'+'/'+file)
                continue
        

