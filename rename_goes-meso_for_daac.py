#!/usr/bin/python3

import os
import shutil
from datetime import datetime
from datetime import timedelta

mesoDir = '/home/disk/bob/impacts/raw/goes16'
outBase = '/home/disk/bob/impacts/daac'
prefix_out = 'IMPACTS_goes16_mesoscale'

for sector in os.listdir(mesoDir):
    if sector.startswith('Mesoscale-') and os.path.isdir(mesoDir+'/'+sector):
        sectorDir = mesoDir+'/'+sector
        for channel in os.listdir(sectorDir):
            if channel.startswith('Channel') and os.path.isdir(sectorDir+'/'+channel):
                channelDir = sectorDir+'/'+channel
                suffix_out = 'ch'+channel[-2:]+'.nc'
                for date in os.listdir(channelDir):
                    if date.startswith('2023') and os.path.isdir(channelDir+'/'+date):
                        dateDir = channelDir+'/'+date
                        for file in os.listdir(dateDir):
                            if file.endswith('nc'):
                                (base,ext) = os.path.splitext(file)
                                (junk,junk,junk,start,end,junk) = base.split('_')
                                time = start[8:14]
                                dir_out = outBase+'/'+channel+'/'+date
                                if not os.path.isdir(dir_out):
                                    os.makedirs(dir_out)
                                file_out = prefix_out+'_'+date+'_'+time+'_'+suffix_out
                                print('file_out = ',file_out)
                                shutil.copy(dateDir+'/'+file,
                                            dir_out+'/'+file_out)
