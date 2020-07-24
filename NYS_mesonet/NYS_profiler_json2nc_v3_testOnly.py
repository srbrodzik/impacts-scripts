#!/usr/bin/python

'''
THIS CODE IS NON-FUNCTIONING - I WAS USING IT TO TEST SOME CONCEPTS

Read all files for a site for a day and write newer data over older data.
The result will be a complete set of data for the previous day.

File for dd/0000 contains dd-1/0000 thru dd-1/2340
         dd/2350 contains dd-1/2350 thru   dd/2340

NOTES:
Need to check for previous day's data at beginning of files and remove it if necessary
'''

import os
import sys
import json
import pandas as pd
import netCDF4 as nc4
import numpy as np
from datetime import timedelta,datetime
import xarray as xr
import glob
import shutil
from NYS_profiler_utils_v2 import make_2d_list, add_missing_lidar_vars

# ----- SUBROUTINES -----

def get_file_list(date_obj,next_date_obj,flist_in,flist_out):

    last_time_obj = date_obj
    for index in range(0,len(flist_in)):
        with open(flist_in[index],'r') as f:
            data = json.load(f)
        lidar = None
        mwr = None
        if type(data.get('lidar')) == dict:
            lidar = data['lidar']
            lidar_times = lidar['coords']['time']['data']
            time_obj = datetime.strptime(lidar_times[-1],"%Y-%m-%dT%H:%M:%S")
            if time_obj > last_time_obj and time_obj < next_date_obj:
                fileList.append(flist_in[index])
                last_time_obj = time_obj
            else:
                return
        elif type(data.get('mwr')) == dict:
            mwr = data['mwr']
            mwr_times = mwr['coords']['time']['data']
            time_obj = datetime.strptime(mwr_times[-1],"%Y-%m-%dT%H:%M:%S")
            if time_obj > last_time_obj and time_obj < next_date_obj:
                fileList.append(flist_in[index])
                last_time_obj = time_obj
            else:
                return
    
# ----- MAIN CODE -----
                    
jsonLidarBaseDir = '/home/disk/funnel/impacts/data_archive/nys_prof/2020/json_QC/lidar'
ncLidarBaseDir = '/home/disk/funnel/impacts/data_archive/nys_prof/2020/netcdf_QC'

'''
sites = {'ALBA':'Albany',
         'BELL':'Belleville',
         'BRON':'Bronx',
         'CHAZ':'Buffalo',
         'CLYM':'Chazy',
         'EHAM':'East_Hampton',
         'JORD':'Jordan',
         'OWEG':'Owego',
         'QUEE':'Queens',
         'REDH':'Red_Hook',
         'STAT':'Staten_Island',
         'STON':'Stony_Brook',
         'SUFF':'Suffern',
         'TUPP':'Tupper_Lake',
         'WANT':'Wantagh',
         'WEBS':'Webster'}
'''
sites = {'ALBA':'Albany'}

secsPerMin = 60
secsPerHour = secsPerMin * 60
secsPerDay = secsPerHour*24
missing_value = -999.
prefix_lidar = 'nys_profiler_lidar'
num_lidar_dims = 2
num_lidar_vars = 5
prefix_mwr = 'nys_profiler_mwr'
num_mwr_dims = 4
num_mwr_vars =  15

for site in sites.keys():
    print(site)

    # make date list
    dates = []
    for file in os.listdir(jsonLidarBaseDir+'/'+site):
        parts = file.split('_')
        dates.append(parts[0])

    for date in dates:

        # get files
        flist = glob.glob(jsonLidarBaseDir+'/'+site+'/'+date+'*')
        
        for date_file in flist:
            
            # read json file into dict
            with open(file,'r') as f:
                data = json.load(f)

                lidar = None
                if type(data.get('lidar')) == dict:
            
                    # create lidar dict
                    lidar = data['lidar']

                    # check to make sure all lidar vars are present
                    if len(lidar['data_vars'].keys()) != num_lidar_vars:
                        lidar = add_missing_lidar_vars(lidar,missing_value)
                    
                    # turn times into seconds since first time
                    lidar_times = lidar['coords']['time']['data']
                    lidar_datetimes = pd.to_datetime(lidar_times)
                    lidar_seconds = []
                    for i,t in enumerate(lidar_datetimes):
                        lidar_seconds.append(int((lidar_datetimes[i]-datetime(1970,1,1)).total_seconds()))
                    lidar['coords']['time']['data'] = lidar_seconds
                    lidar_seconds_unit = 'seconds since 1970-01-01T00:00:00Z'
                    lidar['coords']['time']['attrs']['units'] = lidar_seconds_unit

                    # create xarray.core.dataset.Dataset & decode according to cf conventions
                    lidar = xr.Dataset.from_dict(lidar)
                    lidar = xr.decode_cf(lidar)

                    # create dataframe and add to parent
                    lidar_df = lidar.to_dataframe()


# NOW CREATE NETCDF FROM CONCAT DF

                    
                    # create netcdf file
                    lidar_out = ncDir+'/'+prefix_lidar+'.'+date+'.'+sites[site]+'.nc'
                    encoding = {
                        'pressure_level': {'_FillValue': missing_value},
                        'velocity': {'_FillValue': missing_value}, 
                        'direction': {'_FillValue': missing_value},
                        'cnr': {'_FillValue': missing_value},
                        'w': {'_FillValue': missing_value},
                    }
                    lidar.to_netcdf(path=lidar_out, encoding=encoding)

                else:
                    
                    print >>sys.stderr, '   no lidar data'


'''
# TESTING BELOW
                    
import json
import pandas as pd
import xarray as xr
import numpy as np

# Read in two lidar json files
indir = '/home/disk/funnel/impacts-website/data_archive/nys_prof/2020/json_QC/lidar/ALBA'
outdir = '/home/disk/funnel/impacts-website/data_archive/nys_prof/2020/json_QC/lidar/ALBA/TEST'
file1 = '20200229_0000_to_20200229_2340-resampled.LIDAR_ALBA.json'
file2 = '20200229_0010_to_20200229_2350-resampled.LIDAR_ALBA.json'

f = open(indir+'/'+file1,'r')
lidar1 = json.load(f)
f.close()
# convert to xarray
lidar1 = xr.Dataset.from_dict(lidar1)
lidar1 = xr.decode_cf(lidar1)
# convert to dataframe
lidar1_df = lidar1.to_dataframe()
    
f = open(indir+'/'+file2,'r')
lidar2 = json.load(f)
f.close()
# convert to xarray
lidar2 = xr.Dataset.from_dict(lidar2)
lidar2 = xr.decode_cf(lidar2)
# convert to dataframe
lidar2_df = lidar2.to_dataframe()

# Concatenate and remove dups
lidar = pd.concat([lidar1_df,lidar2_df])
lidar = lidar.loc[~lidar.index.duplicated(keep='last')]
lidar_df = lidar.sort_index(level='range',sort_remaining='True')


# Save df as new json file -- THIS FILE IS NOT RECOGNIZED AS A JSON FILE WHEN TRYING TO READ IN WITH JSON.LOAD
lidar_df.to_json(outdir+'/test.json')

'''
f = open(indir+'/'+file,'r')
lidar = json.load(f)
lidar = xr.Dataset.from_dict(lidar)
lidar = xr.decode_cf(lidar)
lidar_df = lidar.to_dataframe()
f.close()
lidar_df
times_df = pd.DataFrame(lidar_df.index.get_level_values('time'))
times_array = np.array(times_df.drop_duplicates()['time'])
datetimes_array = pd.to_datetime(times_array)
datetimes_array[0:70]

f = open(indir+'/'+file,'r')
mwr = json.load(f)
mwr = xr.Dataset.from_dict(mwr)
mwr = xr.decode_cf(mwr)  # decode using CF conventions
mwr_df = mwr['pressure_level'].to_dataframe()
f.close()
times_df = pd.DataFrame(mwr_df.index.get_level_values('time'))
times_array = np.array(times_df.drop_duplicates()['time'])
datetimes_array = pd.to_datetime(times_array)
datetimes_array[0:70]


