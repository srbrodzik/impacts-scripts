#!/usr/bin/python

import os
import shutil

inDir = '/home/disk/funnel/impacts-website/archive/forecast/wxbriefing'
outDir = '/home/disk/funnel/impacts-website/archive_ncar/reports/weather'
category_new = 'report'
platform_new = 'weather'
product_new = 'discussion'
suffix = 'pdf'

for date in os.listdir(inDir):
    if not os.path.isdir(outDir+'/'+date):
        os.mkdir(outDir+'/'+date)
    for file in os.listdir(inDir+'/'+date):
        if file.endswith(suffix):
            print(file)
            basename = os.path.splitext(file)[0]
            (category,platform,datetime,product) = basename.split('.')
            if product == 'morning':
                datetime = datetime+'1400'
            elif product == 'update':
                datetime = datetime+'2100'
            else:
                print('Product = '+product+' is not recognized')
            file_new = category_new+'.'+platform_new+'.'+datetime+'.'+product_new+'.'+suffix
            print(file_new)
            shutil.copy(inDir+'/'+date+'/'+file,outDir+'/'+date+'/'+file_new)
