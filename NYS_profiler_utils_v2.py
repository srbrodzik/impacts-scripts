import os
import sys
import glob
import shutil
import json
import pandas as pd
import netCDF4 as nc4
import numpy as np
from datetime import timedelta,datetime
import xarray as xr

def make_2d_list(rows, cols, val):
    a=[]
    for row in xrange(rows): a += [[val]*cols]
    return a

def add_missing_lidar_vars(lidar,missing_value):

    timeDim = lidar['dims']['time']
    rangeDim = lidar['dims']['range']

    if 'pressure_level' not in lidar['data_vars'].keys():
        lidar['data_vars']['pressure_level'] = {'dims':['time','range'],
                                                'data':make_2d_list(timeDim, rangeDim, missing_value),
                                                'attrs':{'units':'millibar'} }

    elif 'velocity' not in lidar['data_vars'].keys():
         lidar['data_vars']['velocity'] = {'dims':['time','range'],
                                           'data':make_2d_list(timeDim, rangeDim, missing_value),
                                           'attrs':{'units':'knots'} }
       
                    
    elif 'direction' not in lidar['data_vars'].keys():
         lidar['data_vars']['direction'] = {'dims':['time','range'],
                                            'data':make_2d_list(timeDim, rangeDim, missing_value),
                                            'attrs':{'units':'degree'} }
       
                    
    elif 'cnr' not in lidar['data_vars'].keys():
         lidar['data_vars']['cnr'] = {'dims':['time','range'],
                                      'data':make_2d_list(timeDim, rangeDim, missing_value),
                                      'attrs':{'units':'dB', 'long_name':'carrier to noise ratio'} }
       
    elif 'w' not in lidar['data_vars'].keys():
         lidar['data_vars']['w'] = {'dims':['time','range'],
                                    'data':make_2d_list(timeDim, rangeDim, missing_value),
                                    'attrs':{'units':'m/s', 'standard_name':'upward air velocity'} }
       
                    
    return lidar
