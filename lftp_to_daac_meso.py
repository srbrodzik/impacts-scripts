#!/usr/bin/python3

# lftp impacts@ghrc.nsstc.nasa.gov
# cd goes16-2023/Mesoscale-1
# lcd /home/disk/bob/impacts/raw/goes16/Mesoscale-1
# mirror -R

import os

inDirBase = '/home/disk/bob/impacts/daac'

for channel in os.listdir(inDirBase):
    if channel.startswith('Channel') and os.path.isdir(inDirBase+'/'+channel):
        channelDir = inDirBase+'/'+channel
        for date in os.listdir(channelDir):
            if date.startswith('2023') and os.path.isdir(channelDir+'/'+date):
                dateDir = channelDir+'/'+date
            
                os.chdir(dateDir)
                #command = 'lftp -c "open ftp://impacts:snowfallATLANTIC2020\!@ghrc.nsstc.nasa.gov; cd GOES16_Mesoscale; cd Channel01; mirror -R"'
                command = 'lftp -c "open ftp://impacts:snowfallATLANTIC2020\!@ghrc.nsstc.nasa.gov; cd goes16-2023; cd MesoscaleSectors; cd '+channel+'; cd '+date+'; mirror -R"'
                os.system(command)
