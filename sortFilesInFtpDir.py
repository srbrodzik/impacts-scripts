#!/usr/bin/python

import os
import sys
import shutil

ftpDir = '/home/disk/ftp/brodzik/incoming'
webserverDir = '/home/disk/funnel/impacts/archive'

for file in os.listdir(ftpDir):
    #print sys.stderr, "file = ", file
    if os.path.isfile(ftpDir+'/'+file):
        cmd = 'chmod a+rw '+ftpDir+'/'+file
        os.system(cmd)
        if file.endswith('pdf') or file.endswith('.jpg') or file.endswith('png') or file.endswith('gif') or file.endswith('nc'):
            #print sys.stderr, "   processing file"
            try:
                (prefix,product,date,category,suffix) = file.split('.')
                yyyymmdd = date[0:8]
                if not os.path.exists(webserverDir+'/'+prefix+'/'+product+'/'+yyyymmdd):
                    os.makedirs(webserverDir+'/'+prefix+'/'+product+'/'+yyyymmdd)
                    if product == 'science_plan':
                        shutil.copy(webserverDir+'/'+prefix+'/'+product+'/index.php',webserverDir+'/'+prefix+'/'+product+'/'+yyyymmdd)
                # if science_plan, make new link        
                if product == 'science_plan':
                    os.unlink(webserverDir+'/'+prefix+'/'+product+'/DailySciencePlan.pdf')
                    os.symlink(webserverDir+'/'+prefix+'/'+product+'/'+yyyymmdd+'/'+file,webserverDir+'/'+prefix+'/'+product+'/DailySciencePlan.pdf')
                # if netcdf sounding, create skewt
                if product == 'sounding' and suffix == 'nc':
                    if category == 'UIUC_Mobile':
                        format = 'UIUCnc'
                    elif category == 'sbum':
                        format = 'SBUnc'
                    skewtPath = webserverDir+'/'+prefix+'/skewt/'+yyyymmdd
                    if not os.path.exists(skewtPath):
                         os.makedirs(skewtPath)
                    command = '/usr/bin/python /home/disk/bob/impacts/bin/skewplot.py --file '+ftpDir+'/'+file+' --outpath '+skewtPath+' --format '+format+' --parcel False --hodograph False'
                    os.system(command)
                    # rename skewt for catalog
                    for plot in os.listdir(skewtPath):
                        if plot.startswith('upperair'):
                            plotNew = plot.replace('upperair.SkewT','research.skewt')
                            os.rename(skewtPath+'/'+plot,skewtPath+'/'+plotNew)

                shutil.move(ftpDir+'/'+file,webserverDir+'/'+prefix+'/'+product+'/'+yyyymmdd+'/'+file)
                    
            except ValueError:
                #print sys.stderr, "   processing fails"
                if not os.path.exists(ftpDir+'/junk'):
                    os.mkdir(ftpDir+'/junk')
                shutil.move(ftpDir+'/'+file,ftpDir+'/junk'+'/'+file)
                continue
        

