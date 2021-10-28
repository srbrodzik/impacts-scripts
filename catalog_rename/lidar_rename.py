#!/usr/bin/python

import os
import shutil

#inDirBase = '/home/disk/funnel/impacts-website/archive/ops/nys_lidar_cnr_qc'
#inDirBase = '/home/disk/funnel/impacts-website/archive/ops/nys_lidar_horz_wspd_qc'
inDirBase = '/home/disk/funnel/impacts-website/archive/ops/nys_lidar_vert_wspd_qc'
outDirBase = '/home/disk/funnel/impacts-website/archive_ncar/lidar/DL'
category_new = 'lidar'
platform_new = 'DL'
products = {'alba':'NYSM_Albany_NY',
            'bell':'NYSM_Belleville_NY',
            'bron':'NYSM_Bronx_NY',
            'buff':'NYSM_Buffalo_NY',
            'chaz':'NYSM_Chazy_NY',
            'clym':'NYSM_Clymer_NY',
            'eham':'NYSM_East_Hampton_NY',
            'jord':'NYSM_Jordan_NY',
            'oweg':'NYSM_Owego_NY',
            'quee':'NYSM_Queens_NY',
            'redh':'NYSM_Red_Hook_NY',
            'stat':'NYSM_Staten_Island_NY',
            'ston':'NYSM_Stony_Brook_NY',
            'suff':'NYSM_Suffern_NY',
            'tupp':'NYSM_Tupper_Lake_NY',
            'want':'NYSM_Wantagh_NY',
            'webs':'NYSM_Webster_NY'}
#product_new_suffix = 'cnr'
#product_new_suffix = 'horz_wspd'
product_new_suffix = 'vert_wspd'
            
# go through dates & files
for date in os.listdir(inDirBase):
    if date.startswith('202002'):
        print('date = '+date)
        if not os.path.isdir(outDirBase+'/'+date):
            os.mkdir(outDirBase+'/'+date)
        for file in os.listdir(inDirBase+'/'+date):
            print('file = '+file)
            (basename,ext) = os.path.splitext(file)
            (category_orig,platform_orig,datetime,product_orig) = basename.split('.')
            file_new = category_new+'.'+platform_new+'.'+datetime+'.'+products[product_orig]+'_'+product_new_suffix+ext
            print('file_new = '+file_new)
            shutil.copy(inDirBase+'/'+date+'/'+file,
                        outDirBase+'/'+date+'/'+file_new)
            
