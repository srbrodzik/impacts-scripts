#!/usr/bin/python

import os
import time
from datetime import datetime
import shutil

in_base_dir = '/home/disk/funnel/impacts/archive/research/er2/CPL_qc'
catalog_base_dir = '/home/disk/funnel/impacts/archive/research/er2_qc'
catalog_prefix = 'research.er2'

prod_dict = {'1064':'cpl_1064nm',
             '355':'cpl_355nm',
             '532':'cpl_532nm',
             'aod':'cpl_aerosol_od',
             'cod':'cpl_cloud_od',
             'colOD':'cpl_column_od',
             'depol':'cpl_depol_ratio',
             'ext':'cpl_extinction_coef',
             'ftype':'cpl_feature_type',
             'iwc':'cpl_iwc'}

for date in os.listdir(in_base_dir):
    for file in os.listdir(in_base_dir+'/'+date):
        if file.endswith('png') or file.endswith('gif'):
            basename = os.path.splitext(file)[0]
            ext = os.path.splitext(file)[1]
            parts = basename.split('_')
            if 'imgseg' in parts[0]:
                product = 'cpl_combo'
                date_str_orig = parts[2]
                date_obj = datetime.strptime(date_str_orig,'%d%b%y')
                date_str = date_obj.strftime('%Y%m%d')
                date_suffix = parts[0].replace('imgseg','')
                date_tot = date_str+'_'+date_suffix
                file_new = catalog_prefix+'.'+date_tot+'.'+product+ext
            elif 'imgsum' in parts[0]:
                prod_orig = parts[3]
                product = prod_dict[prod_orig]
                date_str_orig = parts[2]
                date_obj = datetime.strptime(date_str_orig,'%d%b%y')
                date_str = date_obj.strftime('%Y%m%d')
                file_new = catalog_prefix+'.'+date_str+'.'+product+ext
            elif 'map' in parts[0]:
                product = 'cpl_map'
                date_str_orig = parts[2]
                date_obj = datetime.strptime(date_str_orig,'%d%b%y')
                date_str = date_obj.strftime('%Y%m%d')
                file_new = catalog_prefix+'.'+date_str+'.'+product+ext              
            else:
                print('Unknown product ... skip it')
                continue

            print('File = '+file)
            print('New file = '+file_new)
            
            #create output dir, if necessary
            catalog_dir = catalog_base_dir+'/'+date
            if not os.path.exists(catalog_dir):
                os.makedirs(catalog_dir)

            #move file
            #shutil.move(in_base_dir+'/'+file,catalog_dir+'/'+catalog_file)
            shutil.copy(in_base_dir+'/'+date+'/'+file,catalog_dir+'/'+file_new)

    
