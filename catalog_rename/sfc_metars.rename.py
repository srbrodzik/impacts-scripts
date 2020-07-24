#!/usr/bin/python

import os
import shutil

inDir = '/home/disk/funnel/impacts-website/archive/ops/sfc_metar'
outDir = '/home/disk/funnel/impacts-website/archive_ncar/surface/GTS_Station_Plot'
category_new = 'surface'
platform_new = 'GTS_Station_Plot'
products = {'mid_atlantic':'Mid_Atlantic_Region',
            'mid_west':'Mid_West_Region',
            'northeast':'Northeast_Region'}

for date in os.listdir(inDir):
    if not os.path.isdir(outDir+'/'+date):
        os.mkdir(outDir+'/'+date)
    for file in os.listdir(inDir+'/'+date):
        if 'metar' in file:
            print('file = '+file)
            basename = os.path.splitext(file)[0]
            ext = os.path.splitext(file)[1]
            (category,platform,datetime,product) = basename.split('.')
            file_new = category_new+'.'+platform_new+'.'+datetime+'.'+products[product]+ext
            print('file_new = '+file_new)
            shutil.copy(inDir+'/'+date+'/'+file,outDir+'/'+date+'/'+file_new)
            
