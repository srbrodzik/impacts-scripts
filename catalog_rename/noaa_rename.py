#!/usr/bin/python

import os
import shutil

inDirBase = '/home/disk/funnel/impacts-website/archive/ops/noaa'
outDirBase = '/home/disk/funnel/impacts-website/archive_ncar/surface/NOAA_WPC'
category_new = 'surface'
platform_new = 'NOAA_WPC'
products = {'snow_precip_24hr':'snow_precip_24hr',
            'day1_psnow_gt_04':'day1_psnow_gt_4in',
            'day2_psnow_gt_04':'day2_psnow_gt_4in',
            'day3_psnow_gt_04':'day3_psnow_gt_4in',
            'lowtrack':'low_tracks_and_clusters'}
             
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
            
