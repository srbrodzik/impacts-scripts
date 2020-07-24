#!/usr/bin/python

import os
import shutil

inDir = '/home/disk/funnel/impacts-website/archive/ops/upper_air'
outDir = '/home/disk/funnel/impacts-website/archive_ncar/upperair/Constant_Pressure'
category_new = 'upperair'
platform_new = 'Constant_Pressure'
products = {'200mb':'200mb_chart',
            '300mb':'300mb_chart',
            '500mb':'500mb_chart',
            '700mb':'700mb_chart',
            '850mb':'850mb_chart'}

for date in os.listdir(inDir):
    if not os.path.isdir(outDir+'/'+date):
        os.mkdir(outDir+'/'+date)
    for file in os.listdir(inDir+'/'+date):
        if 'mb' in file:
            print('file = '+file)
            basename = os.path.splitext(file)[0]
            ext = os.path.splitext(file)[1]
            (category,platform,datetime,product) = basename.split('.')
            file_new = category_new+'.'+platform_new+'.'+datetime+'.'+products[product]+ext
            print('file_new = '+file_new)
            shutil.copy(inDir+'/'+date+'/'+file,
                        outDir+'/'+date+'/'+file_new)
            
