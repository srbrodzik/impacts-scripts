#!/usr/bin/python

import os 
import json
import pandas as pd
import time, datetime
from time import strftime 
from datetime import datetime, timedelta
import xarray as xr
import shutil

indir = '/home/disk/funnel/impacts/data_archive/nys_prof/2020/json_FIELD'
outdir_lidar = '/home/disk/funnel/impacts/data_archive/nys_prof/2020/json_QC/lidar'
outdir_mwr = '/home/disk/funnel/impacts/data_archive/nys_prof/2020/json_QC/mwr'

for site in os.listdir(indir):
    for file in os.listdir(indir+'/'+site):
        if file.endswith('json'):
            print("Processing file = "+file)
            with open(indir+'/'+site+'/'+file, "r") as f:
                data = json.load(f)
                try:
                    mwr = data['mwr']
                    times = mwr['coords']['time']['data']
                    #times_integrated = mwr['coords']['time_integrated']['data']
                    #times_surface = mwr['coords']['time_surface']['data']
                    mwr_first = times[0]
                    mwr_first_obj = datetime.strptime(mwr_first,'%Y-%m-%dT%H:%M:%S')
                    mwr_first_new = mwr_first_obj.strftime("%Y%m%d_%H%M")
                    mwr_last = times[-1]
                    mwr_last_obj = datetime.strptime(mwr_last,'%Y-%m-%dT%H:%M:%S')
                    mwr_last_new = mwr_last_obj.strftime("%Y%m%d_%H%M")
                    file_new = mwr_first_new+'_to_'+mwr_last_new+'-resampled.MWR_'+site+'.json'
                    with open(outdir_mwr+'/'+site+'/'+file_new,'w') as json_file:
                        json.dump(mwr,json_file)
                except:
                    print("  Problem reading mwr data in "+file)

                try:
                    lidar = data['lidar']
                    times = lidar['coords']['time']['data']
                    lidar_first = times[0]
                    lidar_first_obj = datetime.strptime(lidar_first,'%Y-%m-%dT%H:%M:%S')
                    lidar_first_new = lidar_first_obj.strftime("%Y%m%d_%H%M")
                    lidar_last = times[-1]
                    lidar_last_obj = datetime.strptime(lidar_last,'%Y-%m-%dT%H:%M:%S')
                    lidar_last_new = lidar_last_obj.strftime("%Y%m%d_%H%M")
                    file_new = lidar_first_new+'_to_'+lidar_last_new+'-resampled.LIDAR_'+site+'.json'
                    with open(outdir_lidar+'/'+site+'/'+file_new,'w') as json_file:
                        json.dump(lidar,json_file)
                except:
                    print("  Problem reading lidar data in "+file)
