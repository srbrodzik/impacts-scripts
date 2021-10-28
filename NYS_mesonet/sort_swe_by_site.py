#!/usr/bin/python3

import os
import shutil

indir = '/home/disk/bob/impacts/raw/nys_swe_2021/csv_by_date'
outdir = '/home/disk/bob/impacts/raw/nys_swe_2021/csv_by_site'

for date in os.listdir(indir):
    if date.startswith('2021'):
        for file in os.listdir(indir+'/'+date):
            if file.endswith('.csv'):
                print(file)
                (category,platform,date,site,suffix) = file.split('.')
                siteDir = outdir+'/'+site
                if not os.path.isdir(siteDir):
                    os.makedirs(siteDir)
                shutil.copy(indir+'/'+date+'/'+file,
                            siteDir)
