#!/usr/bin/python3

import os
import shutil

indir = '/home/disk/bob/impacts/sfc/metars'

for file in os.listdir(indir):
    if file.endswith('gif'):
        print(file)
        (datetime,junk,junk) = file.split('_')
        date = datetime[:-2]
        if not os.path.isdir(indir+'/'+date):
            os.makedirs(indir+'/'+date)
        shutil.move(indir+'/'+file,
                    indir+'/'+date+'/'+file)
        
