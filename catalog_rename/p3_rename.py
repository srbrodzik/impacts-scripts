#!/usr/bin/python

import os
import shutil

inDir = '/home/disk/funnel/impacts-website/archive/research/p3'
# These pair 'old product name':'new product name'
products = {'2DS_distributions':'2DS_distributions',
            '2DS_images':'2DS_images',
            'altitude':'altitude_plot',
            'flight_track':'flight_track_composite',
            'dropsonde':'AVAPS',
            'FCDP_distributions':'FCDP_distributions',
            'HVPS3A_distributions':'HVPS3A_distributions',
            'HVPS3A_images':'HVPS3A_images.',
            'phips_camera_C1':'PHIPS_camera_C1',
            'phips_camera_C2':'PHIPS_camera_C2',
            'tamms':'TAMMS'}
outDir = '/home/disk/funnel/impacts-website/archive_ncar/aircraft/NASA_P3'
category_new = 'aircraft'
platform_new = 'NASA_P3'

for date in os.listdir(inDir):
    if os.path.isdir(inDir+'/'+date) and '2020' in date:
        if not os.path.isdir(outDir+'/'+date):
            os.mkdir(outDir+'/'+date)
        for file in os.listdir(inDir+'/'+date):
            if 'p3' in file and (file.endswith('png') or file.endswith('gif') or file.endswith('jpg')):
                print('file = '+file)
                basename = os.path.splitext(file)[0]
                ext = os.path.splitext(file)[1]
                (category,plat,datetime,prod) = basename.split('.')
                file_new = category_new+'.'+platform_new+'.'+datetime+'.'+products[prod]+ext
                print('file_new = '+file_new)
                shutil.copy(inDir+'/'+date+'/'+file,
                            outDir+'/'+date+'/'+file_new)
