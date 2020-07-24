#!/usr/bin/python

import os
import shutil

inDirOps = '/home/disk/funnel/impacts-website/archive/reports'
# These pair 'old platform name':'new platform name'
opsPlatforms = {'flight_plan':'ops',
                'plan_of_the_day':'ops',
                'science_plan':'ops',
                'science_summary':'science'}
opsProducts = {'flight_plan':'flight_plan',
                'plan_of_the_day':'plan_of_the_day',
                'science_plan':'daily_science_plan',
                'science_summary':'summary'}
outDir = '/home/disk/funnel/impacts-website/archive_ncar/reports'
category_new = 'report'
suffix = 'pdf'

for platform in opsPlatforms.keys():
    if not os.path.isdir(outDir+'/'+opsPlatforms[platform]):
        os.mkdir(outDir+'/'+opsPlatforms[platform])
    for date in os.listdir(inDirOps+'/'+platform):
        if os.path.isdir(inDirOps+'/'+platform+'/'+date):
            if not os.path.isdir(outDir+'/'+opsPlatforms[platform]+'/'+date):
                os.mkdir(outDir+'/'+opsPlatforms[platform]+'/'+date)
            for file in os.listdir(inDirOps+'/'+platform+'/'+date):
                if platform in file:  
                    print('file = '+file)
                    basename = os.path.splitext(file)[0]
                    ext = os.path.splitext(file)[1]
                    (category,plat,datetime,prod) = basename.split('.')
                    if platform == 'science_summary':
                        datetime = datetime+'2359'
                    else:
                        datetime = datetime+'1400'
                    file_new = category_new+'.'+opsPlatforms[platform]+'.'+datetime+'.'+opsProducts[platform]+ext
                    print('file_new = '+file_new)
                    shutil.copy(inDirOps+'/'+platform+'/'+date+'/'+file,
                                outDir+'/'+opsPlatforms[platform]+'/'+date+'/'+file_new)
