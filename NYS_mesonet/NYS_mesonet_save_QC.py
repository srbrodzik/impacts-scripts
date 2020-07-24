#!/usr/bin/python

"""
Created August/September 2019
@author: masonf3
Modified January 2020
@author: Joe Finlon
Modified May 2020
@author: Stacy Brodzik

Original code named: NYS_mesonet_save_and_plot.py
Make 3-day plots and save daily .csv files of key weather variables for NYS mesonet stations (126 stations in network)
Data is read from UW Atmospheric Sciences LDM server
Some code modified from Joe Zagrodnik's 'plot_mesowest_3day.py', used for similar task in the OLYMPEX field campaign

Newest version of code split into two parts -- NYS_mesonet_save.py and NYS_mesonet_plot.py

**File Saving Information for current code**
CSV files, one per site per day, save to: '/home/disk/funnel/impacts/data_archive/nys_ground' 
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
        
        # Add additional columns containing station and other meteorological data
        site_data_unique.loc[site_data_unique.station == site.upper(),'station_elevation [m]'] = station_info_temp['elevation [m]'].values[0].round(decimals=3)
        site_data_unique.loc[site_data_unique.station == site.upper(),'name'] = station_info_temp['name'].values[0]
        
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

        # Remove data from date=timestamp at 00:00 and before; add it to previous day's file if it exists
        timestamp_dt = datetime.strptime(timestamp,'%Y%m%d')
        site_data_unique_today = site_data_unique.loc[site_data_unique.index > timestamp_dt]
        site_data_unique_yest = site_data_unique.loc[site_data_unique.index <= timestamp_dt]
        
        timestamp_yest = (timestamp_dt+timedelta(hours=-24)).strftime('%Y%m%d')
        outFile_yest = csv_dir + '/' + timestamp_yest + '/ops.nys_ground.' + timestamp_yest + '.' + station_string + '.csv'
        if os.path.exists(outFile_yest) and len(site_data_unique_yest) > 0:
            yest_data = pd.read_csv(outFile_yest)
            yest_data = yest_data.set_index('datetime')
            yest_data_total = pd.concat([yest_data,site_data_unique_yest]).drop_duplicates(subset='time',keep='last')
            yest_data_total['station_elevation [m]'] = yest_data_total['station_elevation [m]'].round(decimals=3)
            yest_data_total['vapor_pressure [mbar]'] = yest_data_total['vapor_pressure [mbar]'].round(decimals=3)
            yest_data_total['saturated_vapor_pressure [mbar]'] = yest_data_total['saturated_vapor_pressure [mbar]'].round(decimals=3)
            yest_data_total['dew_point_temp_2m [degC]'] = yest_data_total['dew_point_temp_2m [degC]'].round(decimals=3)
            yest_data_total.to_csv(outFile_yest)

        # Output today's data
        outFile = csv_dir + '/' + timestamp + '/ops.nys_ground.' + timestamp + '.' + station_string + '.csv'
        site_data_unique_today.to_csv(outFile)
        print('Sucessfully saved {} mesonet data for {} ({}).'.format(timestamp, station_info_temp['name'].values[0], site))
    
# Query list of files to process
# Save latest file for each hour as it contains all the data from that hour
# REAL-TIME:
# current_dt = datetime.utcnow()
# TESTING:
# January 2020
for day in range(1,32):
    current_dt = datetime(2020, 1, day, 23, 0)

# February 2020
#for day in range(1,30):
    #current_dt = datetime(2020, 2, day, 23, 0)

    # set paths
    station_file = '/home/disk/funnel/impacts/data_archive/nys_ground_QC/meta_nysm.csv' # file containing station lat/lon/alt
    working_dir = os.getcwd() # current working directory
    csv_dir = '/home/disk/funnel/impacts/data_archive/nys_ground_QC' # save csv files here

    # get list of hourly files
    current_date_string = datetime.strftime(current_dt, '%Y%m%d')
    mesonet_dir = '/home/disk/data/albany/standard/' + current_date_string
    all_files = glob.glob(mesonet_dir + '/*.csv')
    hourly_files = []
    for hour in range(0, current_dt.hour+1):
        subset_files = sorted(glob.glob(mesonet_dir + '/' + str(hour).zfill(2) + '*.csv'))
        if len(subset_files)>0:
            hourly_files.append(subset_files[-1])
        else:
            print('No data for the {} hour.'.format(str(hour).zfill(2)))
        
    # merge data into one dataframe object for processing
    daily_data = pd.concat((pd.read_csv(file) for file in hourly_files))

    # process each site
    parse_daily_data(csv_dir, station_file, daily_data)
