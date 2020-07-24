#!/usr/bin/python

import os
import shutil

inDirBase = '/home/disk/funnel/impacts-website/archive/ops'
outDirBase = '/home/disk/funnel/impacts-website/archive_ncar/satellite'
category_new = 'satellite'
platforms = {'goes_east':'GOES-16',
             'gpm':'GPM'}
goes_products = {'multi_ch_color':'multi_chan_color',
                 'vis_ch02':'ch02_vis',
                 'vis_4km':'4km_vis',
                 'ir_4km':'4km_ir',
                 'wv_4km':'4km_wv',
                 'M1color':'meso_sector_1_color',
                 'M2color':'meso_sector_2_color'}
gpm_products = {'2Ku':'2Ku_refl',
                'overpass_west':'overpass_west',
                'overpass_east':'overpass_east'}
             
for platform in platforms.keys():

    # get appropriate product dictionary
    if platform == 'goes_east':
        products = goes_products
    elif platform == 'gpm':
        products = gpm_products
    else:
        products = wrf_products

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
            
