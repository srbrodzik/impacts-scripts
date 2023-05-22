#!/usr/bin/python3

import os

inDirBase = '/home/disk/bob/impacts/netcdf/mrms/3DZdr'

for date in os.listdir(inDirBase):
    inDir = inDirBase+'/'+date
    if os.path.isdir(inDir):
        print(date)
        os.chdir(inDir)
        #command = 'lftp -c "open ftp://impacts:snowfallATLANTIC2020\!@ghrc.nsstc.nasa.gov; mirror -R"'
        command = 'lftp -c "open ftp://impacts:snowfallATLANTIC2020\!@ghrc.nsstc.nasa.gov; cd MRMS; cd ZDR; mirror -R"'
        os.system(command)
