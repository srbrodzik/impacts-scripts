#!/usr/bin/python3

import os

inDirBase = '/home/disk/bob/impacts/daac/CONUS/Channel01'

for date in os.listdir(inDirBase):
    if date.startswith('2023') and os.path.isdir(inDirBase+'/'+date):
        inDir = inDirBase+'/'+date
        print(date)
        os.chdir(inDir)
        command = 'lftp -c "open ftp://impacts:snowfallATLANTIC2020\!@ghrc.nsstc.nasa.gov; cd goes16-2023; cd CONUS; cd Channel01; cd '+date+'; mirror -R"'
        os.system(command)
