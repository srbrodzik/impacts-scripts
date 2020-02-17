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
from NYS_profiler_utils import load_data,get_lidar_array

jsonBaseDir = '/home/disk/data/albany/profiler'
ncBaseDir = '/home/disk/funnel/impacts-website/data_archive/nys_prof'
'''
sites = {'ALBA':'Albany',
         'BELL':'Belleville',
         'BRON':'Bronx',
         'CHAZ':'Buffalo',
         'CLYM':'Chazy',
         'EHAM':'East Hampton',
         'JORD':'Jordan',
         'OWEG':'Owego',
         'QUEE':'Queens',
         'REDH':'Red Hook',
         'STAT':'Staten Island',
         'STON':'Stony Brook',
         'SUFF':'Suffern',
         'TUPP':'Tupper Lake',
         'WANT':'Wantagh',
         'WEBS':'Webster'}
'''
sites = {'ALBA':'Albany'}
secsPerDay = 86400

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

    for site in sites.keys():
        #fileList = glob.glob('*'+site+'*')
        #fileList.sort()
        fileList = ['0000-resampled.PROF_ALBA.json']
        for file in fileList:

            (mwr_time_range_df,mwr_time_df,mwr_time_int_df,mwr_time_sfc_df,lidar_df) = load_data(jsonDir,file)
            
            # Get lidar times and heights
            # index 0 -> range
            # index 1 -> time
            heights_lidar_df = pd.DataFrame(lidar_df.index.get_level_values(0).values)
            heights_lidar_array = np.array(heights_lidar_df.drop_duplicates()[0].values)
            times_lidar_df = pd.DataFrame(lidar_df.index.get_level_values(1).values)
            times_lidar_array = np.array(times_lidar_df.drop_duplicates()[0].values)
            datetimes_lidar_array = pd.to_datetime(times_lidar_array)

            # Get mwr times and heights            
            # For mwr_time_range_df:
            # index 0 -> times
            # index 1 -> range
            heights_mwr_df = pd.DataFrame(mwr_time_range_df.index.get_level_values(1).values)
            heights_mwr_array = np.array(heights_mwr_df.drop_duplicates()[0].values)
            times_mwr_df = pd.DataFrame(mwr_time_range_df.index.get_level_values(0).values)
            times_mwr_array = np.array(times_mwr_df.drop_duplicates()[0].values)
            datetimes_mwr_array = pd.to_datetime(times_mwr_array)           
            # For mwr_time_int_df:
            # index 0 ->time_integrated
            times_int_mwr_df = pd.DataFrame(mwr_time_int_df.index.get_level_values(0).values)
            times_int_mwr_array = np.array(times_int_mwr_df.drop_duplicates()[0].values)
            datetimes_int_mwr_array = pd.to_datetime(times_int_mwr_array)
            # For mwr_time_sfc_df:
            # index 0 ->time_surface
            times_sfc_mwr_df = pd.DataFrame(mwr_time_sfc_df.index.get_level_values(0).values)
            times_sfc_mwr_array = np.array(times_sfc_mwr_df.drop_duplicates()[0].values)
            datetimes_sfc_mwr_array = pd.to_datetime(times_sfc_mwr_array)

            # Get lidar data
            for ifield in range(0,len(lidar_df.keys())):
                fieldName = lidar_df.keys()[ifield]
                exec(fieldName+'= get_lidar_array(lidar_df,heights_array,times_array,fieldName)' )

            # Get mwr data
                
            # Create netcdf file
            ncDir = ncBaseDir+'/'+data_date
            if not os.path.exists(ncDir):
                os.makedirs(ncDir)
            ncName = 'nys_profiler.'+data_date+'.'+sites[site]+'.nc'
            nc = nc4.Dataset(ncDir+'/'+ncName, 'w', format='NETCDF4')
            #root_grp = Dataset(ncDir+'/'+ncName, 'w', format='NETCDF4')
            #root_grp.description = 'NYS Profiler data for '

            # define dims
            time_lidar = nc.createDimension('time_lidar',len(times_lidar_array))
            time_mwr = nc.createDimension('time_mwr',len(times_mwr_array))
            time_int_mwr = nc.createDimension('time_integrated_mwr',len(times_int_mwr_array))
            time_sfc_mwr = nc.createDimension('time_surface_mwr',len(times_sfc_mwr_array))
            range_lidar = nc.createDimension('range_lidar',len(heights_lidar_array))
            range_mwr = nc.createDimension('range_mwr',len(heights_mwr_array))
            
            # define vars and attributes
            times_lidar = nc.createVariable('time_lidar','',('time_lidar',))
            times_mwr = nc.createVariable('time_mwr','',('time_mwr',))
            times_int_mwr = nc.createVariable('time_int_mwr','',('time_int_mwr',))
            times_sfc_mwr = nc.createVariable('time_sfc_mwr','',('time_sfc_mwr',))
            ranges_lidar = nc.createVariable('range_lidar','i4',('range_lidar',))
            ranges_mwr = nc.createVariable('range_mwr','i4',('range_mwr',))
            # LIDAR
            p_lidar = nc.createVariable('pressure_level','f8',('time_lidar','range_lidar',))
            vel = nc.createVariable('velocity','f8',('time_lidar','range_lidar',))
            dir = nc.createVariable('direction','f8',('time_lidar','range_lidar',))
            cnr = nc.createVariable('cnr','f8',('time_lidar','range_lidar',))
            w = nc.createVariable('w','f8',('time_lidar','range_lidar',))
            # MWR
            liq_qc = nc.createVariable('liquid_qc','f8',('time_mwr',))
            rh_qc = nc.createVariable('relative_humidity_qc','f8',('time_mwr',))
            temp_qc = nc.createVariable('temperature_qc','f8',('time_mwr',))
            vd_qc = nc.createVariable('vd_qc','f8',('time_mwr',))
            cb = nc.createVariable('cloud_base','f8',('time_int_mwr',))
            il = nc.createVariable('integrated_liquid','f8',('time_int_mwr',))
            iv = nc.createVariable('integrated_vapor','f8',('time_int_mwr',))
            int_qc = nc.createVariable('integrated_qc','f8',('time_int_mwr',))
            rf = nc.createVariable('rain_flag','f8',('time_sfc_mwr',))
            dp = nc.createVariable('dew_point','f8',('time_mwr','range_mwr',))
            liq = nc.createVariable('liquid','f8',('time_mwr','range_mwr',))
            p_mwr = nc.createVariable('liquid','f8',('time_mwr','range_mwr',))
            
            # add data
            
                








            '''
            # for testing
            print(lidar_df.iloc[0][0])
            # print all values in row 0
            print(lidar_df.iloc[0][:])
            print(lidar_df.iloc[0])
            # access data by row
            for index, row in lidar_df.iterrows():
                print(row['pressure_level'],row['cnr'])
            '''

            
            '''
            # OTHER CODE
            # Select a particular time and convert to a pandas dataframe for display
            print(lidar.sel(time='2020-02-06T00:10:00').to_dataframe())

            for col in ['range', 'pressure_level', 'velocity', 'direction']:
            print("Units for {} are {}".format(col, lidar[col].attrs['units']))
            '''
