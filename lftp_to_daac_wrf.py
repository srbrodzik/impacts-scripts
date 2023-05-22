#!/usr/bin/python3

# lftp impacts@ghrc.nsstc.nasa.gov
# cd goes16-2023/Mesoscale-1
# lcd /home/disk/bob/impacts/raw/goes16/Mesoscale-1
# mirror -R

import os

inDirBase = '/home/disk/bob/impacts/daac/WRF'

for init in os.listdir(inDirBase):
    if (init.startswith('GFS') or init.startswith('NAM') ) and os.path.isdir(inDirBase+'/'+init):
        initDir = inDirBase+'/'+init
        for date in os.listdir(initDir):
            if date.startswith('202') and os.path.isdir(initDir+'/'+date):
                dateDir = initDir+'/'+date
                os.chdir(dateDir)
                command = 'lftp -c "open ftp://impacts:snowfallATLANTIC2020\!@ghrc.nsstc.nasa.gov; cd wrf-2023; cd '+init+'; cd '+date+'; mirror -R"'
                os.system(command)
