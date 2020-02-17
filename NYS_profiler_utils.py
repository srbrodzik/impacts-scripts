import os
import sys
import json
import pandas as pd
import netCDF4 as nc4
import numpy as np
from datetime import timedelta,datetime
import xarray as xr
import glob

def load_data(jsonDir,file):

    ''' Given json file name and path, read data and return 5 dataframes

    Parameters:
    jsonDir (str): path to json file
    file (str): json filename

    Returns:
    mwr_time_range_df (dataframe): mwr data with dims = time, range
    mwr_time_df (dataframe): mwr data with dim = time
    mwr_time_int_df (dataframe): mwr data with dim = time_integrated
    mwr_time_surf_df (dataframe): mwr data with dim = time_surface
    lidar_df (dataframe): lidar data with dimes = time, range

    mwr data
    dims: 
      range=58
      time=143
      time_integrated=743
      time_surface=745
    vars:
      liquid_qc(time)
      relative_humidity_qc(time)
      temperature_qc(time)
      vapor density_qc (time)

      cloud_base(time_integrated)
      integrated_liquid (time_integrated)
      integrated_vapor(time_integrated)
      integrated_qc(time_integrated)

      rain_flag(time_surface)

      dew_point(time,range)
      liquid(time,range)
      pressure_level(time,range)
      relative_humidity(time,range)
      temperature(time,range)
      vapor_density(time,range)

    lidar data
    dims:
      range=157
      time=143  (YYYY-MM-DDThh:mm:ss)
    vars:
      cnr(time,range)
      direction(time,range)
      pressure_level(time,range)
      velocity(time,range)
      w(time,range)
    '''

    mwr = None
    lidar = None
    # read json file into dict
    with open(file,'r') as f:
        data = json.load(f)
            
    try:    
        mwr = data['mwr']
        mwr = xr.Dataset.from_dict(mwr)
        mwr = xr.decode_cf(mwr)
                
        # Create pandas DataFrame out of 'time', 'range' data
        mwr_td = mwr['dew_point'].to_dataframe()
        mwr_lq = mwr['liquid'].to_dataframe()
        mwr_p = mwr['pressure_level'].to_dataframe()
        mwr_rh = mwr['relative_humidity'].to_dataframe()
        mwr_t = mwr['temperature'].to_dataframe()
        mwr_vd = mwr['vapor_density'].to_dataframe()
        mwr_time_range_df = pd.concat([mwr_td.iloc[:,1],mwr_lq.iloc[:,1],mwr_p.iloc[:,1],mwr_rh.iloc[:,1],mwr_t.iloc[:,1],mwr_vd.iloc[:,1]], axis=1)

        # Create pandas DataFrame out of 'time' data
        mwr_lq_qc = mwr['liquid_qc'].to_dataframe()
        mwr_rh_qc = mwr['relative_humidity_qc'].to_dataframe()
        mwr_t_qc = mwr['temperature_qc'].to_dataframe()
        mwr_vd_qc = mwr['vapor_density_qc'].to_dataframe()
        mwr_time_df = pd.concat([mwr_lq_qc.iloc[:,1],mwr_rh_qc.iloc[:,1],mwr_t_qc.iloc[:,1],mwr_vd_qc.iloc[:,1]], axis=1)

        # Create pandas DataFrame out of 'time_integrated' data
        mwr_cb = mwr['cloud_base'].to_dataframe()
        mwr_il = mwr['integrated_liquid'].to_dataframe()
        mwr_iv = mwr['integrated_vapor'].to_dataframe()
        mwr_int_qc = mwr['integrated_qc'].to_dataframe()
        mwr_time_int_df = pd.concat([mwr_cb.iloc[:,1],mwr_il.iloc[:,1],mwr_iv.iloc[:,1],mwr_int_qc.iloc[:,1]], axis=1)

        # Create pandas DataFrame out of 'time_surface' data
        mwr_rf = mwr['rain_flag'].to_dataframe()
        mwr_time_surf_df = pd.concat([mwr_rf.iloc[:,1]], axis=1)
                
    except:
        print >>sys.stderr, 'Problem radar mwr data in ',file
        mwr_time_range_df = []
        mwr_time_range_df = pd.DataFrame(mwr_time_range_df)
        mwr_time_df = []
        mwr_time_df = pd.DataFrame(mwr_time_df)
        mwr_time_int_df = []
        mwr_time_int_df = pd.DataFrame(mwr_time_int_df)
        mwr_time_surf_df = []
        mwr_time_surf_df = pd.DataFrame(mwr_time_surf_df)
            
    try:
        # create lidar dict
        lidar = data['lidar']
                
        #for key in lidar.keys():
        #    print(key)
        #for dim in lidar['dims']:
        #    print(dim)
                    
        # create xarray.core.dataset.Dataset & decode according to cf conventions
        lidar = xr.Dataset.from_dict(lidar)
        lidar = xr.decode_cf(lidar)

        # create pandas.core.frame.DataFrame
        lidar_df = lidar.to_dataframe()
        # what does this do??
        lidar_df = pd.DataFrame(lidar_df)
                
    except:
        print >>sys.stderr, 'Problem radar lidar data in ',file
        lidar_df = []
        lidar_df = pd.DataFrame(lidar_df)

    return mwr_time_range_df,mwr_time_df,mwr_time_int_df,mwr_time_surf_df,lidar_df

    # ANOTHER WAY
    # Pack all dataframes into a dict and return it to calling routine
    #prof_data = {'mwr_time_range_data': mwr_time_range_df,
    #             'mwr_time_data': mwr_time_df,
    #             'mwr_time_int_data': mwr_time_int_df,
    #             'mwr_time_surf_data': mwr_time_surf_df,
    #             'lidar_data': lidar_df}
    #return prof_data



def get_lidar_array(lidar_df,heights_array,times_array,fieldName):
                    
    ''' Given dataframe and time and height arrays, read fieldName data into output array

    Parameters:
    lidar_df (dataframe): lidar data with dimes = time, range
    heights_array (np.array): height array
    times_array (np.array): times array
    fieldName (str): name of field to get data for

    Returns:
    field_array (np.array): fieldName data array
    '''

    field_array = np.zeros([len(heights_array),len(times_array)])
    for i in range(0,len(times_array)):
        for j in range(0,len(heights_array)):
            field_array[j,i] = lidar_df.loc[(heights_array[j],times_array[i]),fieldName]
            
    return field_array

#def make_nc_file()
