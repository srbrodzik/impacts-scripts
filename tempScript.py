#!/usr/bin/python

import os
import shutil

inDirBase = '/home/disk/funnel/impacts-website/archive_ncar/surface/Meteogram'

for date in os.listdir(inDirBase):
    if date.startswith('20200'):
        inDir = inDirBase+'/'+date
        origDir = inDir+'/ORIG'
        if not os.path.isdir(origDir):
            makedirs(origDir)
        for file in os.listdir(inDir):
            if 'ASOS' in file:
                shutil(inDir+'/'+file,origDir+'/'+file)


