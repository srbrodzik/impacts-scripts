#!/usr/bin/python

import os
import shutil

inDirBase = '/home/disk/funnel/impacts-website/archive/research'
outDirBase = '/home/disk/funnel/impacts-website/archive_ncar/surface'
category_new = 'surface'
platforms = {'stonybrook':'Pluvio',
             'manhattan':'Parsivel',
             'stonybrookmobile':'Parsivel',
             'ualbany':'Parsivel'}
SBU_products = {'pluvio':'Stonybrook_NY'}
manhattan_products = {'parsivel':'Manhattan_NY'}
SBUM_products = {'parsivel':'Stonybrook_NY_Mobile'}
UAlbany_products = {'parsivel':'UAlbany'}
             
for platform in platforms.keys():

    # get appropriate product dictionary
    if platform == 'stonybrook':
        products = SBU_products
    elif platform == 'manhattan':
        products = manhattan_products
    elif platform == 'stonybrookmobile':
        products = SBUM_products
    else:
        products = UAlbany_products

    # make output product dir
    if not os.path.isdir(outDirBase+'/'+platforms[platform]):
        os.mkdir(outDirBase+'/'+platforms[platform])

    # go through dates & files
    for date in os.listdir(inDirBase+'/'+platform):
        if not os.path.isdir(outDirBase+'/'+platforms[platform]+'/'+date):
            os.mkdir(outDirBase+'/'+platforms[platform]+'/'+date)
        for file in os.listdir(inDirBase+'/'+platform+'/'+date):
            (basename,ext) = os.path.splitext(file)
            if file.endswith(products.keys()[0]+ext):
                print('file = '+file)
                (category_orig,platform_orig,datetime,product_orig) = basename.split('.')
                file_new = category_new+'.'+platforms[platform]+'.'+datetime+'.'+products[product_orig]+ext
                print('file_new = '+file_new)
                shutil.copy(inDirBase+'/'+platform+'/'+date+'/'+file,
                            outDirBase+'/'+platforms[platform]+'/'+date+'/'+file_new)
            
