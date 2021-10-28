#!/usr/bin/python

import os
import shutil

inDirBase = '/home/disk/funnel/impacts-website/archive/research/stonybrookmobile'
outDirBase = '/home/disk/funnel/impacts-website/archive_ncar/surface/Meteogram'
category_new = 'surface'
platform_new = 'Meteogram'
products = {'met_station':'SBU_Mobile'}
             
# go through dates & files
for date in os.listdir(inDirBase):
    if not os.path.isdir(outDirBase+'/'+date):
        os.mkdir(outDirBase+'/'+date)
    for file in os.listdir(inDirBase+'/'+date):
        if 'met_station' in file:
            print('file = '+file)
            (basename,ext) = os.path.splitext(file)
            (category_orig,platform_orig,datetime,product_orig) = basename.split('.')
            file_new = category_new+'.'+platform_new+'.'+datetime+'.'+products[product_orig]+ext
            print('file_new = '+file_new)
            shutil.copy(inDirBase+'/'+date+'/'+file,
                        outDirBase+'/'+date+'/'+file_new)
            
