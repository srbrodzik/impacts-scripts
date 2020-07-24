#!/usr/bin/python

import os
import shutil

inDir = '/home/disk/funnel/impacts-website/archive/research/stonybrook'
outDir = '/home/disk/funnel/impacts-website/archive_ncar/radar/ROGER'
category_new = 'radar'
platform_new = 'ROGER'
products = {'roger_spectrum_refl':'spectrum_refl',
            'roger_time_ht':'time_ht'}

for date in os.listdir(inDir):
    if date.startswith('20200'):
        if not os.path.isdir(outDir+'/'+date):
            os.mkdir(outDir+'/'+date)
        for file in os.listdir(inDir+'/'+date):
            if file.endswith('roger_spectrum_refl.png') or file.endswith('roger_time_ht.png'):
                print('file = '+file)
                (basename,ext) = os.path.splitext(file)
                (category_orig,platform_orig,datetime,product_orig) = basename.split('.')
                file_new = category_new+'.'+platform_new+'.'+datetime+'.'+products[product_orig]+ext
                print('file_new = '+file_new)
                shutil.copy(inDir+'/'+date+'/'+file,
                            outDir+'/'+date+'/'+file_new)
            
