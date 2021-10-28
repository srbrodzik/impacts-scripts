#!/usr/bin/python

"""
Created August/September 2019
@author: masonf3
Modified January 2020
@author: Joe Finlon
Modified May 2020
@author: Stacy Brodzik
Modified October 2021
@author: Stacy Brodzik

Original code named: NYS_mesonet_save_and_plot.py
Made 3-day plots and saved daily .csv files of key weather variables for NYS mesonet stations (126 stations in network)
Data was read from UW Atmospheric Sciences LDM server
Some code modified from Joe Zagrodnik's 'plot_mesowest_3day.py', used for similar task in the OLYMPEX field campaign

Newest version of code split into two parts -- NYS_mesonet_save.py and NYS_mesonet_plot.py

This is the version of the save code modified for 2021 data.

**File Saving Information for current code**
CSV files, one per site per day, save to: '/home/disk/bob/impacts/raw/nys_ground_2021/csv_by_site' 
"""

import sys, os
import pandas as pd 
import csv 
import time, datetime, glob 
from time import strftime 
from datetime import datetime, timedelta
import numpy as np 

### SUBROUTINES ###
def vapor_pressure_calc(T, RH):
    '''Given temperature and relative humidity, returns vapor pressure.
    From https://www.weather.gov/media/epz/wxcalc/vaporPressure.pdf 
    
    Parameters: 
    T (float): temperature, in degrees celsius
    RH (float): relative humidity, in %
                
    Returns: 
    e (float): vapor pressure, in (find out)
    es (float): saturation vapor pressure, in (find out)
    '''
    es = 6.11 * 10**((7.5*T)/(237.3+T)) #saturation vapor pressure calculation
    e = (RH/100) * es                   #current vapor pressure calculation (using RH)
    return e, es

def Td_calc(es, RH):
    '''Given saturation vapor pressure and relative humidity, returns dew point temperature.
    From https://www.weather.gov/media/epz/wxcalc/vaporPressure.pdf
    
    Parameters: 
    es (float): saturation vapor presure, in (find out)
    RH (float): relative humidity, in %

    Returns: 
    Td (float): dew point temperature, in degrees celsius
    '''
    Td = (237.3*np.log((es*RH)/611))/(7.5*np.log(10)-np.log((es*RH)/611))
    return Td

def parse_daily_data(csv_dir, station_file, daily_data):
    os.chdir(csv_dir)
    station_info_data = pd.read_csv(station_file) # read station info from .csv file
    station_info_data = station_info_data.set_index('stid') # index by station id
    station_list = list(station_info_data.index)
    
    for site in station_list:
        # Query and trim station-specific data
        station_info_temp = station_info_data.loc[station_info_data.index == site].copy(deep=True)
        site_data = daily_data.loc[daily_data['station'] == site] # query data for current station
        
        # NOTE: Getting SettingWithCopyWarning on next line
        site_data.loc[site_data.station == site,'datetime'] = pd.to_datetime(site_data['time'], format='%Y-%m-%d %H:%M:%S UTC')
        # Two attempts at fixing warning - both worked but still gave warning
        #site_data['datetime'] = site_data.apply(lambda row: pd.to_datetime(row.time, format='%Y-%m-%d %H:%M:%S UTC'), axis=1)
        #site_data.loc[site_data.station == site,'datetime'] = site_data.apply(lambda row: pd.to_datetime(row.time, format='%Y-%m-%d %H:%M:%S UTC'), axis=1)
        #site_data.loc[site_data.station == site,'datetime'] = site_data['time'].map(lambda time: pd.to_datetime(time, format='%Y-%m-%d %H:%M:%S UTC') )
        #site_data.loc[:,'datetime'] = pd.to_datetime(site_data['time'], format='%Y-%m-%d %H:%M:%S UTC')

        site_data_dt = site_data.set_index('datetime') # set new data index to datetime
        site_data_unique = site_data_dt.loc[~site_data_dt.index.duplicated(keep='last')] # remove duplicate times
        
        if 'relative_humidity [percent]' and 'temp_2m [degC]' in site_data_unique.keys():
            e, es = vapor_pressure_calc(site_data_unique['temp_2m [degC]'], site_data_unique['relative_humidity [percent]'])
            Td = Td_calc(es, site_data_unique['relative_humidity [percent]'])
            site_data_unique.loc[site_data_unique.station == site.upper(),'vapor_pressure [mbar]'] = e.round(decimals=3)
            site_data_unique.loc[site_data_unique.station == site.upper(),'saturated_vapor_pressure [mbar]'] = es.round(decimals=3)
            site_data_unique.loc[site_data_unique.station == site.upper(),'dew_point_temp_2m [degC]'] = Td.round(decimals=3) 
        else:
            site_data_unique.loc[site_data_unique.station == site.upper(),'vapor_pressure [mbar]'] = np.nan
            site_data_unique.loc[site_data_unique.station == site.upper(),'saturated_vapor_pressure [mbar]'] =np.nan
            site_data_unique.loc[site_data_unique.station == site.upper(),'dew_point_temp_2m [degC]'] = np.nan
        
        # Prepare to save daily station data to file
        station_string = site.lower()
        timestamp = datetime.strftime(site_data_unique.index[-1], '%Y%m%d')
        if os.path.exists(timestamp) is False: # create directory since it doesn't exist
            os.mkdir(timestamp)

        # Output today's data
        outFile = csv_dir + '/' + timestamp + '/ops.nys_ground.' + timestamp + '.' + station_string + '.csv'
        site_data_unique.to_csv(outFile)
        print('Sucessfully saved {} mesonet data for {} ({}).'.format(timestamp, station_info_temp['name'].values[0], site))

### MAIN CODE ###

# set paths
station_file = '/home/disk/bob/impacts/raw/nys_ground_2021/csv/nysm.csv' # file containing station lat/lon/alt
csv_dir = '/home/disk/bob/impacts/raw/nys_ground_2021/csv_by_date' # save csv files here
mesonet_dir_base = '/home/disk/bob/impacts/raw/nys_ground_2021/csv'

for csvFile in os.listdir(mesonet_dir_base):
    if csvFile.startswith('2021'):
        daily_data = pd.read_csv(mesonet_dir_base+'/'+csvFile)
        parse_daily_data(csv_dir, station_file, daily_data)
