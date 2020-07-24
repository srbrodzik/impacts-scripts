#!/usr/bin/python

import os
import shutil

inDirBase = '/home/disk/funnel/impacts-website/archive/ops/sfc_anal'
outDirBase = '/home/disk/funnel/impacts-website/archive_ncar/surface/NWS_Surface_Analysis'
category_new = 'surface'
platform_new = 'NWS_Surface_Analysis'
products = {'atlantic':'Atlantic',
            'n_amer':'North_America'}
             
# go through dates & files
for date in os.listdir(inDirBase):
    if not os.path.isdir(outDirBase+'/'+date):
        os.mkdir(outDirBase+'/'+date)
    for file in os.listdir(inDirBase+'/'+date):
        print('file = '+file)
        basename = os.path.splitext(file)[0]
        ext = os.path.splitext(file)[1]
        (category_orig,platform_orig,datetime,product_orig) = basename.split('.')
        file_new = category_new+'.'+platform_new+'.'+datetime+'.'+products[product_orig]+ext
        print('file_new = '+file_new)
        shutil.copy(inDirBase+'/'+date+'/'+file,
                    outDirBase+'/'+date+'/'+file_new)
            
