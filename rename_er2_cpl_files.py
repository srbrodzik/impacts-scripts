#!/usr/bin/python

import os
import time
from datetime import datetime
import shutil

#in_base_dir = '/home/disk/funnel/impacts/archive/research/er2/CPL_qc'
in_base_dir = '/home/disk/bob/impacts/lidar/er2'
#catalog_base_dir = '/home/disk/funnel/impacts/archive/research/er2_qc'
catalog_prefix = 'aircraft.NASA_ER2'

prod_dict = {'1064':'CPL_1064nm',
             '355':'CPL_355nm',
             '532':'CPL_532nm',
             'aod':'CPL_aerosol_opt_depth',
             'cod':'CPL_cloud_opt_depth',
             'colOD':'CPL_column_opt_depth',
             'depol':'CPL_depol_ratio',
             'ext':'CPL_extinction_coef',
             'ftype':'CPL_feature_type',
             'iwc':'CPL_iwc'}

for date in os.listdir(in_base_dir):
    if os.path.isdir(in_base_dir+'/'+date):
        for file in os.listdir(in_base_dir+'/'+date):
            if file.endswith('png') or file.endswith('gif'):
                (basename,ext) = os.path.splitext(file)
                parts = basename.split('_')
                if 'imgseg' in parts[0]:
                    product = 'CPL_combo'
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
                    product = 'CPL_flight_track'
                    date_str_orig = parts[2]
                    date_obj = datetime.strptime(date_str_orig,'%d%b%y')
                    date_str = date_obj.strftime('%Y%m%d')
                    file_new = catalog_prefix+'.'+date_str+'.'+product+ext              
                else:
                    print('Unknown product ... skip it')
                    continue

                print('File = '+file)
                print('New file = '+file_new)
            
                #move file
                shutil.move(in_base_dir+'/'+date+'/'+file,
                            in_base_dir+'/'+date+'/'+file_new)

    
