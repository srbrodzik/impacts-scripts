#!/usr/bin/python

import os
import sys
import shutil

inDirBase = '/home/disk/funnel/impacts-website/archive/ops'
outDirBase = '/home/disk/funnel/impacts-website/archive_ncar/surface'
category_new = 'surface'
#platforms = {'extrema':'NWS',
#             'totals':'NWS'}
platforms = {'extrema':'NWS'}
extrema_products = {'max_temp':'max_temp',
                    'min_temp':'min_temp'}
#totals_products = {'precip24':'precip_24hr'}
             
for platform in platforms.keys():

    # get appropriate product dictionary
    if platform == 'extrema':
        products = extrema_products
    elif platform == 'totals':
        products = totals_products
    else:
        print('Unknown platform = '+platform+'. . . exiting')
        sys.exit()

    # make output product dir
    if not os.path.isdir(outDirBase+'/'+platforms[platform]):
        os.mkdir(outDirBase+'/'+platforms[platform])

    # go through dates & files
    for date in os.listdir(inDirBase+'/'+platform):
        if not os.path.isdir(outDirBase+'/'+platforms[platform]+'/'+date):
            os.mkdir(outDirBase+'/'+platforms[platform]+'/'+date)
        for file in os.listdir(inDirBase+'/'+platform+'/'+date):
                print('file = '+file)
                basename = os.path.splitext(file)[0]
                ext = os.path.splitext(file)[1]
                (category_orig,platform_orig,datetime,product_orig) = basename.split('.')
                file_new = category_new+'.'+platforms[platform]+'.'+datetime+'.'+products[product_orig]+ext
                print('file_new = '+file_new)
                shutil.copy(inDirBase+'/'+platform+'/'+date+'/'+file,
                            outDirBase+'/'+platforms[platform]+'/'+date+'/'+file_new)
            
