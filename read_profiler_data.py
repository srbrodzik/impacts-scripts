#!/usr/bin/env python3

import os
import sys
import json
import xarray as xr

if len(sys.argv) != 2:
    raise SystemExit("Useage: {} {}".format(sys.argv[0], "[infile.json]"))
file = sys.argv[1]
file_base, file_ext = os.path.splitext(file)
site = file_base[-4:]

mwr = None
lidar = None
with open(file, "r") as f:
    #create dictionary called 'data'
    data = json.load(f)

    #get a list of dict keys - several ways
    #sorted( data.keys() )
    #list(data.keys())
    #list(data)
    #[*data]
    
    try:
        mwr = data['mwr']
        mwr = xr.Dataset.from_dict(mwr)
        mwr = xr.decode_cf(mwr)
        
        #convert to netcdf
        outfile_path = '/home/disk/shear2/brodzik/impacts/Data/NYSMesonet'
        outfile = 'mwr.nc'
        mwr.to_netcdf(path=outfile_path+'/'+outfile)

        #rename file using latest time in file
        time_mwr_vals = mwr.coords['time'].data
        last_time = time_mwr_vals[-1]
        dateStr = last_time[0:4]+last_time[5:7]+last_time[8:10]
        timeStr = last_time[11:13]+last_time[14:16]+last_time[17:]
        outfile_new = outfile_path+"/mwr."+dateStr+"."+timeStr+"."+site.lower()+".nc"
        os.rename(outfile,outfile_new)
        
    except:
        print("Problem reading microwave radiometer data")

    #In [74]: print(mwr)
    #<xarray.Dataset>
    #Dimensions:         (range: 58, time: 143)
    #Coordinates:
    #   * range           (range) int64 0 50 100 150 200 250 300 350 400 450 500 ...
    #     lv2_processor   <U10 'Angle20(A)'
    #   * time            (time) <U19 '2019-06-18T15:00:00' '2019-06-18T15:10:00' ...
    #Data variables:
    #     pressure_level  (time, range) float64 1.005e+03 999.0 993.2 987.4 981.6 ...
    #     dew_point       (time, range) float64 15.6 16.2 15.6 15.1 14.6 14.2 13.7 ...
    #     temperature     (time, range) float64 17.3 18.4 17.8 17.3 16.9 16.6 16.3 ...

    #get dim sizes for time and range
    #time_mwr_dim = len(mwr['time'])
    #range_mwr_dim = len(mwr['range'])
    #print("   mwr:   time_dim = {} and range_dim = {}".format( time_mwr_dim, range_mwr_dim) )

    #get time and range values and attributes
    #time_mwr_vals = mwr.coords['time'].data
    #range_mwr_vals = mwr.coords['range'].data
    #print("   mwr:   first time = {} and last time = {}".format(time_mwr_vals[0], time_mwr_vals[-1]) )
    #range_mwr_standard_name = mwr.coords['range'].attrs['standard_name']
    #range_mwr_long_name = mwr.coords['range'].attrs['long_name']
    #range_mwr_units = mwr.coords['range'].attrs['units']

    #convert times to seconds since 1970-01-01 00:00  ??

    #get pressure_level, dew_point and temperature values & attributes
    #first dim is time, second dim is range
    #pres_vals = mwr['pressure_level'].data 
    #pres_units = mwr['pressure_level'].attrs['units'] 
    #dpt_vals = mwr['dew_point'].data
    #dpt_units = mwr['dew_point'].attrs['units']
    #temp_vals = mwr['temperature'].data 
    #temp_units = mwr['temperature'].attrs['units'] 

    try:
        lidar = data['lidar']
        lidar = xr.Dataset.from_dict(lidar)
        lidar = xr.decode_cf(lidar)

        #convert to netcdf
        outfile_path = '/home/disk/shear2/brodzik/impacts/Data/NYSMesonet'
        outfile = 'lidar.nc'
        lidar.to_netcdf(path=outfile_path+'/'+outfile)
        print("Done converting lidar to netcdf")
        
        #rename file using latest time in file
        time_lidar_vals = lidar.coords['time'].data
        last_time = time_lidar_vals[-1]
        dateStr = last_time[0:4]+last_time[5:7]+last_time[8:10]
        timeStr = last_time[11:13]+last_time[14:16]+last_time[17:]
        outfile_new = outfile_path+"/lidar."+dateStr+"."+timeStr+"."+site.lower()+".nc"
        print("outfile_new = {}".format(outfile_new) )
        os.rename(outfile,outfile_new)
        
    except:
        print("Problem reading lidar data")

    #In [73]: print(lidar)
    #<xarray.Dataset>
    #Dimensions:         (range: 157, time: 143)
    #Coordinates:
    #   * range           (range) int64 100 125 150 175 200 225 250 275 300 325 ...
    #   * time            (time) <U19 '2019-06-18T15:00:00' '2019-06-18T15:10:00' ...
    #Data variables:
    #     pressure_level  (time, range) float64 993.2 990.3 987.4 984.5 981.6 ...
    #     velocity        (time, range) object 3 3 2 3 4 5 6 6 9 9 9 9 9 9 9 9 9 8 ...
    #     direction       (time, range) object 151 145 154 153 157 153 159 165 153 ...
        
    #get dim sizes for time and range
    #time_lidar_dim = len(lidar['time'])
    #range_lidar_dim = len(lidar['range'])
    #print("   lidar: time_dim = {} and range_dim = {}".format( time_lidar_dim, range_lidar_dim) )

    #get time and range values and attributes
    #time_lidar_vals = lidar.coords['time'].data
    #range_lidar_vals = lidar.coords['range'].data
    #print("   lidar: first time = {} and last time = {}".format(time_lidar_vals[0], time_lidar_vals[-1]) )
    #range_lidar_standard_name = lidar.coords['range'].attrs['standard_name']
    #range_lidar_units = lidar.coords['range'].attrs['units']

    #convert times to seconds since 1970-01-01 00:00  ??

    #get pressure_level, dew_point and temperature values & attributes
    #first dim is time, second dim is range
    #pres_vals = lidar['pressure_level'].data 
    #pres_units = lidar['pressure_level'].attrs['units'] 
    #wspd_vals = lidar['velocity'].data
    #wspd_units = lidar['velocity'].attrs['units']
    #wdir_vals = lidar['direction'].data 
    #wdir_units = lidar['direction'].attrs['units'] 

# Select a particular time and convert to a pandas dataframe for display
#print(lidar.sel(time='2019-06-19T14:40:00').to_dataframe())

#for col in ['range', 'pressure_level', 'velocity', 'direction']:
#  print("Units for {} are {}".format(col, lidar[col].attrs['units']))
