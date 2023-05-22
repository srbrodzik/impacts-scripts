#!/usr/bin/python3

import os

inDirBase = '/home/disk/bob/impacts/raw/goes16/CONUS/Channel13'

for date in os.listdir(inDirBase):
    inDir = inDirBase+'/'+date
    if os.path.isdir(inDir):
        print(date)
        os.chdir(inDir)
        command = 'lftp -c "open ftp://impacts:snowfallATLANTIC2020\!@ghrc.nsstc.nasa.gov; cd GOES16_CONUS; cd Channel13; mirror -R"'
        os.system(command)
