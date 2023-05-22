#!/usr/bin/python3

import os
from datetime import datetime
import shutil

baseDir = '/home/disk/bob/impacts/raw/goes16/CONUS'
channels = ['Channel01','Channel02','Channel03','Channel08',
            'Channel09','Channel10','Channel13']

for channel in channels:
    for file in os.listdir(baseDir+'/'+channel):
        if file.startswith('OR_ABI'):
            print(file)
            idx = file.find('_s')
            # date is in YYYYJJJJ format
            jul_date = file[idx+2:idx+2+7]
            jul_date_obj = datetime.strptime(jul_date,'%Y%j')
            date = jul_date_obj.strftime('%Y%m%d')
            if not os.path.isdir(baseDir+'/'+channel+'/'+date):
                os.makedirs(baseDir+'/'+channel+'/'+date)
            shutil.move(baseDir+'/'+channel+'/'+file,
                        baseDir+'/'+channel+'/'+date+'/'+file)
        
