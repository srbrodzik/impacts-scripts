#!/usr/bin/python3

import os
import shutil

targetDirBase = '/home/disk/bob/impacts/images/MVIS'
catPrefix = 'aircraft.NASA_ER2'
catSuffix = 'MVIS'

for date in os.listdir(targetDirBase):
    if date.startswith('20220108'):
        targetDir = targetDirBase+'/'+date
        for file in os.listdir(targetDir):
            if file.startswith(date):
                print(file)
                (imageTime,ext) = os.path.splitext(file)
                imageTime = imageTime[:-2]
                catName = catPrefix+'.'+imageTime+'.'+catSuffix+ext
                shutil.move(targetDir+'/'+file,
                            targetDir+'/'+catName)
