"""
Created August/September 2019
@author: masonf3
"""
'''NYS_mesonet_save_and_plot.py
Make 3-day plots and save daily .csv files of key weather variables for NYS mesonet stations (126 stations in network)
Data is read from UW Atmospheric Sciences LDM server
Some code modified from Joe Zagrodnik's 'plot_mesowest_3day.py', used for similar task in the OLYMPEX field campaign

**File Saving Information**
CSV files, one per day, save to: '/home/disk/funnel/impacts/data_archive/nys_ground' 
3-day plots, one each time code is run, save to: '/home/disk/funnel/impacts/archive/ops/nys_ground'
'''
import sys, os
import pandas as pd 
import csv 
import time, datetime, glob 
from time import strftime 
from datetime import datetime, timedelta
import numpy as np 
import matplotlib 
from matplotlib.dates import DayLocator, HourLocator, DateFormatter
matplotlib.use('Agg') 
import matplotlib.transforms as transforms
import matplotlib.pyplot as plt

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
        site_data['datetime'] = pd.to_datetime(site_data['time'], format='%Y-%m-%d %H:%M:%S UTC') # get datetime objects
        site_data_dt = site_data.set_index('datetime') # set new data index to datetime
        site_data_unique = site_data_dt.loc[~site_data_dt.index.duplicated(keep='last')] # remove duplicate times
        
        # Add additional columns containing station and other meteorological data
        site_data_unique['station_elevation [m]'] = station_info_temp['elevation [m]'].values[0]
        site_data_unique['name'] = station_info_temp['name'].values[0]
        
        if 'relative_humidity [percent]' and 'temp_2m [degC]' in site_data_unique.keys():
            e, es = vapor_pressure_calc(site_data_unique['temp_2m [degC]'], site_data_unique['relative_humidity [percent]'])
            Td = Td_calc(es, site_data_unique['relative_humidity [percent]'])
            site_data_unique['vapor_pressure [mbar]'] = e # add calculated vapor pressure to new data
            site_data_unique['saturated_vapor_pressure [mbar]'] = es # add calculated saturated vapor pressure to new data
            site_data_unique['dew_point_temp_2m [degC]'] = Td # add calculated dew point to new data
        
        # Save daily station data to file
        timestamp = datetime.strftime(site_data_unique.index[-1], '%Y%m%d')
        station_string = site.lower()
        if os.path.exists(timestamp) is False: # create directory since it doesn't exist
            os.mkdir(timestamp)
            
        outFile = csv_dir + '/' + timestamp + '/ops.nys_ground.' + timestamp + '.' + station_string + '.csv'
        site_data_unique.to_csv(outFile)
        print('Sucessfully saved {} mesonet data for {} ({}).'.format(timestamp, station_info_temp['name'].values[0], site))
    
# Query list of files to process
# current_dt = datetime(2020, 1, 1, 23, 0) # uncomment this if you need to retroactively create CSVs for an earlier date
current_dt = datetime.utcnow()
current_hour = current_dt.hour
current_date_string = datetime.strftime(current_dt, '%Y%m%d')
mesonet_dir = '/home/disk/data/albany/standard/' + current_date_string
all_files = glob.glob(mesonet_dir + '/*.csv')
hourly_files = []
for hour in range(0, current_dt.hour+1):
    subset_files = glob.glob(mesonet_dir + '/' + str(hour).zfill(2) + '*.csv')
    if len(subset_files)>0:
        hourly_files.append(subset_files[-1])
    else:
        print('No data for the {} hour.'.format(str(hour).zfill(2)))

station_file = '/home/disk/funnel/impacts/data_archive/nys_ground/meta_nysm.csv' # file containing station lat/lon/alt
working_dir = os.getcwd() # current working directory
csv_dir = '/home/disk/funnel/impacts/data_archive/nys_ground' # save csv files here

daily_data = pd.concat((pd.read_csv(file) for file in hourly_files)) # merge data into one dataframe object for processing
# daily_data = daily_data[daily_data.station != 'station'] # remove duplicate headers read in from stdin
parse_daily_data(csv_dir, station_file, daily_data)