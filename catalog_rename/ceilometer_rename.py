#!/usr/bin/python

import os
import shutil

#inDirBase = '/home/disk/funnel/impacts-website/archive/research/brookhaven'
#inDirBase = '/home/disk/funnel/impacts-website/archive/research/manhattan'
inDirBase = '/home/disk/funnel/impacts-website/archive/research/stonybrookmobile'
outDirBase = '/home/disk/funnel/impacts-website/archive_ncar/lidar/Ceilometer'
category_new = 'lidar'
platform_new = 'Ceilometer'
#product_new = 'Brookhaven_NY_7500m'
#product_new = 'Manhattan_NY_15000m'
product_new = 'Stonybrook_NY_Mobile_15000m'
            
# go through dates & files
for date in os.listdir(inDirBase):
    if date.startswith('20200'):
        if not os.path.isdir(outDirBase+'/'+date):
            os.mkdir(outDirBase+'/'+date)
        for file in os.listdir(inDirBase+'/'+date):
            if 'ceil' in file:
                print('file = '+file)
                (basename,ext) = os.path.splitext(file)
                (category_orig,platform_orig,datetime,product_orig) = basename.split('.')
                file_new = category_new+'.'+platform_new+'.'+datetime+'.'+product_new+ext
                print('file_new = '+file_new)
                shutil.copy(inDirBase+'/'+date+'/'+file,
                            outDirBase+'/'+date+'/'+file_new)
            
