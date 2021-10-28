#!/usr/bin/python3

"""
Created: October 2021
@author: brodzik

Saves daily .csv files of key weather variables for NYS SWE stations (20 stations in network - 13 are colocated
with Standard NYSM sites; 7 near Standard NYSM sites but more sheltered from wind and called "external" sites)
During 2022 deployment, data will be read from UW Atmospheric Sciences LDM server
Some code modified from Joe Zagrodnik's 'plot_mesowest_3day.py', used for similar task in the OLYMPEX field campaign

Newest version of code split into two parts -- NYS_swe_save.py and NYS_swe_plot.py

This is the version of the save code modified for 2021 data.

**File Saving Information for current code**
CSV files, one per site per day, save to: '/home/disk/bob/impacts/raw/nys_swe_2021/csv_by_site' 
"""

import sys, os
import pandas as pd 
import csv 
import time, datetime, glob 
from time import strftime 
from datetime import datetime, timedelta
import numpy as np
import shutil

### SUBROUTINES ###
def parse_daily_data(csv_dir, station_file, daily_data):
    os.chdir(csv_dir)
    station_info_data = pd.read_csv(station_file) # read station info from .csv file
    station_info_data = station_info_data.set_index('stid') # index by station id
    station_list = list(station_info_data.index)
    
    for site in station_list:

        print(site)
        
        # Remove 'SNOW_' from beginning of site name
        site_short = site.replace('SNOW_','')
        
        # Query and trim station-specific data
        station_info_temp = station_info_data.loc[station_info_data.index == site].copy(deep=True)
        site_data = daily_data.loc[daily_data['stid'] == site_short] # query data for current station

        if site_data.empty is False:
        
            # NOTE: Getting SettingWithCopyWarning on next line
            site_data.loc[site_data.stid == site_short,'datetime'] = pd.to_datetime(site_data['time'], format='%Y-%m-%d %H:%M:%S')
            # Two attempts at fixing warning - both worked but still gave warning
            #site_data['datetime'] = site_data.apply(lambda row: pd.to_datetime(row.time, format='%Y-%m-%d %H:%M:%S UTC'), axis=1)
            #site_data.loc[site_data.station == site_short,'datetime'] = site_data.apply(lambda row: pd.to_datetime(row.time, format='%Y-%m-%d %H:%M:%S UTC'), axis=1)
            #site_data.loc[site_data.station == site_short,'datetime'] = site_data['time'].map(lambda time: pd.to_datetime(time, format='%Y-%m-%d %H:%M:%S UTC') )
            #site_data.loc[:,'datetime'] = pd.to_datetime(site_data['time'], format='%Y-%m-%d %H:%M:%S UTC')

            site_data_dt = site_data.set_index('datetime') # set new data index to datetime
            site_data_unique = site_data_dt.loc[~site_data_dt.index.duplicated(keep='last')] # remove duplicate times
        
            # Prepare to save daily station data to file
            station_string = site_short.lower()
            timestamp = datetime.strftime(site_data_unique.index[-1], '%Y%m%d')
            if os.path.exists(timestamp) is False: # create directory since it doesn't exist
                os.mkdir(timestamp)

            # Output today's data
            outFile = csv_dir + '/' + timestamp + '/ops.nys_swe.' + timestamp + '.' + station_string + '.csv'
            site_data_unique.to_csv(outFile)
            print('Sucessfully saved {} swe data for {} ({}).'.format(timestamp, station_info_temp['name'].values[0], site))

### MAIN CODE ###

# set paths
station_file = '/home/disk/bob/impacts/raw/nys_swe_2021/csv/snow.csv'    # file containing station lat/lon/alt
csv_dir = '/home/disk/bob/impacts/raw/nys_swe_2021/csv_by_date'      # save csv files here
swe_dir_base = '/home/disk/bob/impacts/raw/nys_swe_2021/csv'

columns = ['stid','fname','time','recNum','int_end_time','network','serialNum','K_counts_uncorr','K_counts_corr',
           'Tl_counts_corr','swe_K','K_Tl_ratio','swe_Tl','sm_K','sm_Tl','sm_K_Tl','precip_index','crystal_temp_min',
           'crystal_temp_max','hist_blocks','K_disp','stats','pwr_volt']

for csvFile in os.listdir(swe_dir_base):
    if csvFile.startswith('2021'):

        with open(swe_dir_base+'/tempFile','w', encoding='UTF8') as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            with open(swe_dir_base+'/'+csvFile) as csvData:
                csv_reader = csv.reader(csvData, delimiter=',')
                for row in csv_reader:
                    writer.writerow(row)
        daily_data = pd.read_csv(swe_dir_base+'/tempFile')
        shutil.move(swe_dir_base+'/tempFile',
                    swe_dir_base+'/'+csvFile)
        parse_daily_data(csv_dir, station_file, daily_data)

