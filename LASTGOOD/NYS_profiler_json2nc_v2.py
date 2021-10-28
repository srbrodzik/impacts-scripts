#!/usr/bin/python

'''
Read all files for a site for a day and write newer data over older data.
The result will be a complete set of data for the previous day.

File for dd/0000 contains dd-1/0000 thru dd-1/2340
         dd/2350 contains dd-1/2350 thru   dd/2340
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

jsonBaseDir = '/home/disk/data/albany/profiler'
ncBaseDir = '/home/disk/funnel/impacts-website/data_archive/nys_prof'
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
#sites = {'STAT':'Staten_Island'}
secsPerDay = 86400
missing_value = -999.
prefix_lidar = 'nys_profiler_lidar'
num_lidar_dims = 2
num_lidar_vars = 5
prefix_mwr = 'nys_profiler_mwr'
num_mwr_dims = 4
num_mwr_vars =  15

#dates = []
#for file in os.listdir(jsonBaseDir):
#    if os.path.isdir(jsonBaseDir+'/'+file):
#        dates.append(file)
dates = ['20200207']

for date in dates:
    jsonDir = jsonBaseDir+'/'+date
    os.chdir(jsonDir)
    date_obj = datetime.strptime(date,"%Y%m%d")
    deltaSecs = timedelta(0, secsPerDay)
    data_date_obj = date_obj - deltaSecs
    data_date = data_date_obj.strftime("%Y%m%d")
    ncDir = ncBaseDir+'/'+data_date
    if not os.path.isdir(ncDir):
        os.makedirs(ncDir)
        shutil.copy(ncBaseDir+'/index.php',ncDir)

    for site in sites.keys():
        fileList = glob.glob('*'+site+'*')
        fileList.sort()

        for idx,file in enumerate(fileList):

            # use data from second file of the day
            if idx == 1 and '001' in file:

                print(file)

                # read json file into dict
                with open(file,'r') as f:
                    data = json.load(f)

                mwr = None
                if type(data.get('mwr')) == dict:
            
                    mwr = data['mwr']
                    
                    # turn all times vars from strings into seconds since 1970-01-01T00:00:00Z
                    mwr_times = mwr['coords']['time']['data']
                    mwr_datetimes = pd.to_datetime(mwr_times)
                    mwr_seconds = []
                    for i,t in enumerate(mwr_datetimes):
                        mwr_seconds.append(int((mwr_datetimes[i]-datetime(1970,1,1)).total_seconds()))
                        #mwr_seconds.append(int((mwr_datetimes[i]-mwr_datetimes[0]).total_seconds()))
                    mwr['coords']['time']['data'] = mwr_seconds
                    mwr_seconds_unit = 'seconds since 1970-01-01T00:00:00Z'
                    #mwr_seconds_unit = 'seconds since '+mwr_times[0].replace('T',' ')
                    mwr['coords']['time']['attrs']['units'] = mwr_seconds_unit
                    
                    mwr_int_times = mwr['coords']['time_integrated']['data']
                    mwr_int_datetimes = pd.to_datetime(mwr_int_times)
                    mwr_int_seconds = []
                    for i,t in enumerate(mwr_int_datetimes):
                        mwr_int_seconds.append(int((mwr_int_datetimes[i]-datetime(1970,1,1)).total_seconds()))
                        #mwr_int_seconds.append(int((mwr_int_datetimes[i]-mwr_int_datetimes[0]).total_seconds()))
                    mwr['coords']['time_integrated']['data'] = mwr_int_seconds
                    mwr_int_seconds_unit = 'seconds since 1970-01-01T00:00:00Z'
                    #mwr_int_seconds_unit = 'seconds since '+mwr_int_times[0].replace('T',' ')
                    mwr['coords']['time_integrated']['attrs']['units'] = mwr_int_seconds_unit
                    
                    mwr_sfc_times = mwr['coords']['time_surface']['data']
                    mwr_sfc_datetimes = pd.to_datetime(mwr_sfc_times)
                    mwr_sfc_seconds = []
                    for i,t in enumerate(mwr_sfc_datetimes):
                        mwr_sfc_seconds.append(int((mwr_sfc_datetimes[i]-datetime(1970,1,1)).total_seconds()))
                        #mwr_sfc_seconds.append(int((mwr_sfc_datetimes[i]-mwr_sfc_datetimes[0]).total_seconds()))
                    mwr['coords']['time_surface']['data'] = mwr_sfc_seconds
                    mwr_sfc_seconds_unit = 'seconds since 1970-01-01T00:00:00Z'
                    #mwr_sfc_seconds_unit = 'seconds since '+mwr_sfc_times[0].replace('T',' ')
                    mwr['coords']['time_surface']['attrs']['units'] = mwr_sfc_seconds_unit
                    
                    # create xarray.core.dataset.Dataset & decode according to cf conventions
                    mwr = xr.Dataset.from_dict(mwr)
                    mwr = xr.decode_cf(mwr)

                    # create netcdf file
                    mwr_out = ncDir+'/'+prefix_mwr+'.'+data_date+'.'+sites[site]+'.nc'
                    encoding = {
                        'vapor_density_qc': {'_FillValue': missing_value},
                        'integrated_liquid': {'_FillValue': missing_value}, 
                        'rain_flag': {'_FillValue': missing_value},
                        'liquid': {'_FillValue': missing_value},
                        'temperature_qc': {'_FillValue': missing_value},
                        'integrated_vapor': {'_FillValue': missing_value},
                        'cloud_base': {'_FillValue': missing_value},
                        'liquid_qc': {'_FillValue': missing_value},
                        'relative_humidity': {'_FillValue': missing_value},
                        'relative_humidity_qc': {'_FillValue': missing_value},
                        'vapor_density': {'_FillValue': missing_value},
                        'pressure_level': {'_FillValue': missing_value},
                        'integrated_qc': {'_FillValue': missing_value},
                        'dew_point': {'_FillValue': missing_value},
                        'temperature': {'_FillValue': missing_value}
                    }
                    mwr.to_netcdf(path=mwr_out, encoding=encoding)

                else:

                    print >>sys.stderr, '   no mwr data'

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
                        #lidar_seconds.append(int((lidar_datetimes[i]-lidar_datetimes[0]).total_seconds()))
                    lidar['coords']['time']['data'] = lidar_seconds
                    lidar_seconds_unit = 'seconds since 1970-01-01T00:00:00Z'
                    #lidar_seconds_unit = 'seconds since '+lidar_times[0].replace('T',' ')
                    lidar['coords']['time']['attrs']['units'] = lidar_seconds_unit

                    ## create encoding string
                    #var = data['lidar']['data_vars'].keys()[0]
                    #cmd = "encoding = { '"+var+"': {'_FillValue': "+str(missing_value)+"}"
                    #for var in lidar['data_vars'].keys()[1:]:
                    #    new_part = ", '"+var+"': {'_FillValue': "+str(missing_value)+"}"
                    #    cmd = cmd + new_part
                    #cmd = cmd+' }'
                    #exec(cmd)

                    # create xarray.core.dataset.Dataset & decode according to cf conventions
                    lidar = xr.Dataset.from_dict(lidar)
                    lidar = xr.decode_cf(lidar)

                    # create netcdf file
                    lidar_out = ncDir+'/'+prefix_lidar+'.'+data_date+'.'+sites[site]+'.nc'
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


