#!/usr/bin/python3

import os
import shutil
from datetime import datetime

inDirBase = '/home/disk/bob/impacts/raw/goes16/Mesoscale-2'
outDirBase = '/home/disk/bob/impacts/daac'
prefix = 'IMPACTS_goes16_mesoscale'
chanDict = {'Channel01':'ch01',
            'Channel02':'ch02',
            'Channel03':'ch03',
            'Channel04':'ch04',
            'Channel05':'ch05',
            'Channel06':'ch06',
            'Channel07':'ch07',
            'Channel08':'ch08',
            'Channel09':'ch09',
            'Channel10':'ch10',
            'Channel11':'ch11',
            'Channel12':'ch12',
            'Channel13':'ch13',
            'Channel14':'ch14',
            'Channel15':'ch15',
            'Channel16':'ch106'}
            
for chan in os.listdir(inDirBase):
    if chan.startswith('Channel') and os.path.isdir(inDirBase+'/'+chan):
        chanDir = inDirBase+'/'+chan
        for date in os.listdir(chanDir):
            if date.startswith('20220') and os.path.isdir(chanDir+'/'+date):
                dateDir = chanDir+'/'+date
                for file in os.listdir(dateDir):
                    if file.endswith('.nc'):
                        print(file)
                        outDir = outDirBase+'/'+chan+'/'+date
                        if not os.path.isdir(outDir):
                            os.makedirs(outDir)
                        (base,ext) = os.path.splitext(file)
                        (junk,bandInfo,sat,start,end,created) = base.split('_')
                        dateTime = start[1:-1]
                        dateTimeObj = datetime.strptime(dateTime,'%Y%j%H%M%S')
                        date = dateTimeObj.strftime('%Y%m%d')
                        time = dateTimeObj.strftime('%H%M%S')
                        newFile = prefix+'_'+date+'_'+time+'_'+chanDict[chan]+ext
                        print(newFile)
                        shutil.copy(dateDir+'/'+file,
                                    outDir+'/'+newFile)
                        
                
        
    
