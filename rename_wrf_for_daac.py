#!/usr/bin/python3

import os
import shutil
from datetime import datetime
from datetime import timedelta

wrfDir = '/home/disk/bob/impacts/raw/wrf_from_colle'
initModel = ['GFS','NAM']
secsPerHour = 3600
prefix_out = 'IMPACTS_wrfout'
suffix_out = 'nc'

for init in initModel:
    for runTime in os.listdir(wrfDir+'/'+init):
        runTime_dt = datetime.strptime(runTime, '%Y%m%d%H')
        for fname_in in os.listdir(wrfDir+'/'+init+'/'+runTime):
            if fname_in.startswith('wrfout'):
                print('fname_in = ',fname_in)
                (prefix_in,domain,fdate,ftime) = fname_in.split('_')
                fcstTime = fdate+' '+ftime
                fcstTime_dt = datetime.strptime(fcstTime,'%Y-%m-%d %H:%M:%S')
                deltaHours = str( int( (fcstTime_dt - runTime_dt).total_seconds() / secsPerHour ))
                if len(deltaHours) < 2:
                    deltaHours = '0'+deltaHours
                fname_out = prefix_out+'_'+domain+'_'+runTime+'_'+deltaHours+'_'+init+'.'+suffix_out
                print('fname_out = ',fname_out)
                shutil.move(wrfDir+'/'+init+'/'+runTime+'/'+fname_in,
                            wrfDir+'/'+init+'/'+runTime+'/'+fname_out)
