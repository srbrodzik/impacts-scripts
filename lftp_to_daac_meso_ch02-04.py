#!/usr/bin/python3

import os

inDirBase = '/home/disk/bob/impacts/raw/goes16/MesoscaleDAAC'

for chan in os.listdir(inDirBase):
    if ( chan.startswith('Channel02') or chan.startswith('Channel03') or chan.startswith('Channel04') ) and os.path.isdir(inDirBase+'/'+chan):
        chanDir = inDirBase+'/'+chan
        for date in os.listdir(chanDir):
            if date.startswith('20220') and os.path.isdir(chanDir+'/'+date):
                dateDir = chanDir+'/'+date
                if os.path.isdir(dateDir):
                    print(date)
                    os.chdir(dateDir)
                    #command = 'lftp -c "open ftp://impacts:snowfallATLANTIC2020\!@ghrc.nsstc.nasa.gov; cd GOES16_Mesoscale; cd Channel01; mirror -R"'
                    command = 'lftp -c "open ftp://impacts:snowfallATLANTIC2020\!@ghrc.nsstc.nasa.gov; cd GOES16_Mesoscale; cd '+chan+'; mirror -R"'
                    os.system(command)
