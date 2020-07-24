#!/usr/bin/python

import os
import shutil

inDir = '/home/disk/funnel/impacts-website/archive/research/skewt'
outDirBase = '/home/disk/funnel/impacts-website/archive_ncar/upperair'
category_new = 'upperair'
platform_new = {'NCSU':'NCSU_sonde',
                'SBU':'SBU_sonde',
                'UIUC_Mobile_Sonde':'UILL_sonde'}    
product_new = 'skewT'

for date in os.listdir(inDir):
    for file in os.listdir(inDir+'/'+date):
        if 'skewt' in file:
            print('file = '+file)
            basename = os.path.splitext(file)[0]
            ext = os.path.splitext(file)[1]
            (category,platform,datetime,product) = basename.split('.')
            file_new = category_new+'.'+platform_new[product]+'.'+datetime+'.'+product_new+ext
            print('file_new = '+file_new)
            outDir = outDirBase+'/'+platform_new[product]
            if not os.path.isdir(outDir):
                os.mkdir(outDir)
            if not os.path.isdir(outDir+'/'+date):
                os.mkdir(outDir+'/'+date)
            shutil.copy(inDir+'/'+date+'/'+file,
                        outDir+'/'+date+'/'+file_new)
            
