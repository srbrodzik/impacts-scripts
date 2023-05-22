#!/usr/bin/python3

import os

inDirBase = '/home/disk/bob/impacts/daac/MRMS/ZDR'

for date in os.listdir(inDirBase):
    if date.startswith('2023') and os.path.isdir(inDirBase+'/'+date):
        inDir = inDirBase+'/'+date
        print(date)
        os.chdir(inDir)
        command = 'lftp -c "open ftp://impacts:snowfallATLANTIC2020\!@ghrc.nsstc.nasa.gov; cd mrms-2023; cd ZDR; cd '+date+'; mirror -R"'
        os.system(command)
