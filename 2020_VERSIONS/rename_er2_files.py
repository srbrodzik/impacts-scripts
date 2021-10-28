#!/usr/bin/python

import os
import time
from datetime import datetime
import shutil

in_base_dir = '/home/disk/funnel/impacts/archive/research/er2'
catalog_base_dir = '/home/disk/funnel/impacts/archive/research/er2'
catalog_prefix = 'research.er2'

for file in os.listdir(in_base_dir):
    if file.endswith('png'):
        #(product,junk2,junk3,start,junk4,end,junk5) = file.split('_')
        parts = file.split('_')
        if parts[0] == 'HIWRAP':
            product = parts[0]+'_'+parts[1]
            start = parts[4]
        elif parts[0] == 'CRS' or parts[0] == 'EXRAD':
            product = parts[0]
            start = parts[3]
        else:
            print('Unknown product ... skip it')
            continue
        date_time_str = start.replace('T','')
        date_time_obj = datetime.strptime(date_time_str,'%Y%m%d%H%M%S')
        date_str = date_time_obj.strftime("%Y%m%d")

        #create output dir, if necessary
        catalog_dir = catalog_base_dir+'/'+date_str
        if not os.path.exists(catalog_dir):
            os.makedirs(catalog_dir)

        #create output file name
        catalog_file = catalog_prefix+'.'+date_time_str+'.'+product.lower()+'.png'

        #move file
        shutil.move(in_base_dir+'/'+file,catalog_dir+'/'+catalog_file)

    
