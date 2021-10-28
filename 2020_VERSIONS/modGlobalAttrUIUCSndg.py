#!/usr/bin/python3

import os
from netCDF4 import Dataset
from datetime import datetime

baseDir = '/home/disk/funnel/impacts-website/data_archive/soundings/impacts'

for date in os.listdir(baseDir):
    if os.path.isdir(baseDir+'/'+date) and date.startswith('2020'):
        for file in os.listdir(baseDir+'/'+date):
            if file.endswith('.nc'):
                (prefix1,prefix2,date,time,suffix1,suffix2) = file.split('_')
                date_time_str = date+time+'00'
                date_time_obj = datetime.strptime(date_time_str, '%Y%m%d%H%M%S')
                valid_time = date_time_obj.strftime('%Y-%m-%dT%H:%M:%SZ')
                ds = Dataset(baseDir+'/'+date+'/'+file,'a')
                ds.release_datetime = ds.start_datetime
                ds.start_datetime = valid_time
                ds.close()
    
#valid_time
#release_time
