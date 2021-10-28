#!/usr/bin/python

import os
import shutil

inDirBase = '/home/disk/funnel/impacts-website/archive/research'
outDirBase = '/home/disk/funnel/impacts-website/archive_ncar/radar'
category_new = 'radar'
platforms = {'manhattan':'MRR',
             'stonybrookmobile':'MRR',
             'ualbany':'MRR'}
manhattan_products = {'mrr_pro':'Manhattan_NY_time_ht'}
SBUM_products = {'mrr_pro':'Stonybrook_NY_Mobile_time_ht'}
UAlbany_products = {'mrr':'UAlbany_time_ht',
                    'mrr_cfad':'UAlbany_CFAD',
                    'mrr_parsivel_tseries':'UAlbany_MRR_vs_Parsivel'}
             
for platform in platforms.keys():

    # get appropriate product dictionary
    if platform == 'manhattan':
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
            if ((platform=='manhattan' or platform=='stonybrookmobile') and file.endswith(products.keys()[0]+ext)) or (platform == 'ualbany' and 'ualbany' in file and 'parsivel.png' not in file):
                print('file = '+file)
                (category_orig,platform_orig,datetime,product_orig) = basename.split('.')
                if len(datetime) == 8:
                    datetime = datetime + '0000'
                file_new = category_new+'.'+platforms[platform]+'.'+datetime+'.'+products[product_orig]+ext
                print('file_new = '+file_new)
                shutil.copy(inDirBase+'/'+platform+'/'+date+'/'+file,
                            outDirBase+'/'+platforms[platform]+'/'+date+'/'+file_new)
            
