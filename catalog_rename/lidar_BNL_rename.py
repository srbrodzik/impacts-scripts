#!/usr/bin/python

import os
import shutil

inDirBase = '/home/disk/funnel/impacts-website/archive/research/brookhaven'
outDirBase = '/home/disk/funnel/impacts-website/archive_ncar/lidar/DL'
category_new = 'lidar'
platform_new = 'DL'
product_new = 'Brookhaven_NY_time_ht'
            
# go through dates & files
for date in os.listdir(inDirBase):
    if date.startswith('20200'):
        if not os.path.isdir(outDirBase+'/'+date):
            os.mkdir(outDirBase+'/'+date)
        for file in os.listdir(inDirBase+'/'+date):
            if 'dopp_lidar' in file:
                print('file = '+file)
                (basename,ext) = os.path.splitext(file)
                (category_orig,platform_orig,datetime,product_orig) = basename.split('.')
                file_new = category_new+'.'+platform_new+'.'+datetime+'.'+product_new+ext
                print('file_new = '+file_new)
                shutil.copy(inDirBase+'/'+date+'/'+file,
                            outDirBase+'/'+date+'/'+file_new)
            
