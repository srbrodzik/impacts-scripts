#!/usr/bin/python

import os

indir = '/home/disk/data/albany/profiler'
outdir = '/home/disk/bob/impacts/bin/NYS_mesonet/prof_output'

for date in os.listdir(indir):
    sites = {'ALBA':0,'BELL':0,'BRON':0,'BUFF':0,'CHAZ':0,'CLYM':0,'EHAM':0,
             'JORD':0,'OWEG':0,'QUEE':0,'REDH':0,'STAT':0,'STON':0,'SUFF':0,
             'TUPP':0,'WANT':0,'WEBS':0}
    if '2020' in date:
        print('Date: {}'.format(date))
        for file in os.listdir(indir+'/'+date):
            parts = file.split('.')
            
