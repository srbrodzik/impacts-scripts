#!/usr/bin/python3

# This is a kludge to get rid of the redundant files that RadxConvert is
# currently creating on the RaXPOL data.

import os
import shutil

indir = '/home/disk/bob/impacts/cfradial/raxpol/sur/20220225'
outdir = indir+'/extra'
lastTime = '999999'

if not os.path.exists(outdir):
    os.makedirs(outdir)

files = os.listdir(indir)
files.sort()

for file in files:
    if file.endswith('SUR.nc'):
        print(file)
        (prefix,start,end,suffix1,suffix2,ext) = file.split('.')
        (junk1,junk2,endDate,endTime) = end.split('_')
        if endTime == lastTime:
            shutil.move(indir+'/'+file,
                        outdir+'/'+file)
        else:
            lastTime = endTime
            
