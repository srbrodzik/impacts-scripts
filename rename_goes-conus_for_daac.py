#!/usr/bin/python3

import os
import shutil
from datetime import datetime
from datetime import timedelta

baseDir = '/home/disk/bob/impacts/mdv'
outBase = '/home/disk/bob/impacts/daac/CONUS'
prefix_out = 'IMPACTS_goes16_conus'

for channel in os.listdir(baseDir):
    if channel.startswith('goes16') and os.path.isdir(baseDir+'/'+channel):
        channelDir = baseDir+'/'+channel
        suffix_out = 'ch'+channel[-2:]+'.nc'
        for date in os.listdir(channelDir):
            if date.startswith('2023') and os.path.isdir(channelDir+'/'+date):
                dateDir = channelDir+'/'+date
                for file in os.listdir(dateDir):
                    if file.endswith('nc'):
                        (base,ext) = os.path.splitext(file)
                        (junk,datetime,junk) = base.split('.')
                        dir_out = outBase+'/Channel'+channel[-2:]+'/'+date
                        if not os.path.isdir(dir_out):
                            os.makedirs(dir_out)
                        file_out = prefix_out+'_'+datetime+'_'+suffix_out
                        print('file_out = ',file_out)
                        shutil.copy(dateDir+'/'+file,
                                    dir_out+'/'+file_out)
