#!/usr/bin/python

import os
import shutil

inDir = '/home/disk/funnel/impacts-website/archive/research/npol'
outDir = '/home/disk/funnel/impacts-website/archive_ncar/radar/NPOL'
category_new = 'radar'
platform_new = 'NPOL'

for date in os.listdir(inDir):
    if not os.path.isdir(outDir+'/'+date):
        os.mkdir(outDir+'/'+date)
    for file in os.listdir(inDir+'/'+date):
        if 'npol' in file:
            print('file = '+file)
            basename = os.path.splitext(file)[0]
            ext = os.path.splitext(file)[1]
            (category,platform,datetime,product) = basename.split('.')
            file_new = category_new+'.'+platform_new+'.'+datetime+'.'+product+ext
            print('file_new = '+file_new)
            shutil.copy(inDir+'/'+date+'/'+file,
                        outDir+'/'+date+'/'+file_new)
            
