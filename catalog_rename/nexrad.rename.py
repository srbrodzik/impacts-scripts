#!/usr/bin/python

import os
import shutil

inDir = '/home/disk/funnel/impacts-website/archive/ops/nexrad'
outDir = '/home/disk/funnel/impacts-website/archive_ncar/radar/NEXRAD'
category_new = 'radar'
platform_suffix = '-NEXRAD'

for date in os.listdir(inDir):
    if not os.path.isdir(outDir+'/'+date):
        os.mkdir(outDir+'/'+date)
    for file in os.listdir(inDir+'/'+date):
        if 'nexrad' in file:
            print('file = '+file)
            basename = os.path.splitext(file)[0]
            ext = os.path.splitext(file)[1]
            (category,platform,datetime,product) = basename.split('.')
            (site,field) = product.split('_')
            platform_new = site.upper()+platform_suffix
            if field == 'bref':
                product_new = 'DBZ'
            elif field == 'vel':
                product_new = 'VEL'
            file_new = category_new+'.'+platform_new+'.'+datetime+'.'+product_new+ext
            print('file_new = '+file_new)
            shutil.copy(inDir+'/'+date+'/'+file,outDir+'/'+date+'/'+file_new)
            
