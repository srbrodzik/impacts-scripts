
# coding: utf-8

#!/usr/bin/env python3
"""
Created June/July 2019
@author: masonf3 (Mason Friedman)

Modified Sep 2020 by S Brodzik
Added weather_cond_code variable to download & precip plot

Modified Sep 2020 by S Brodzik
Replaced precip info with precip API info
"""

'''
ASOS_save_and_plot.py
Make 3-day plots and save daily .csv files of key weather variables for a list of ASOS weather stations.
Code can be easily modified to cover a different time range.
Designed to be run once per hour. 
Data is read from Synoptic Developers Mesonet API Time Series Service:
https://developers.synopticdata.com/mesonet/v2/stations/timeseries/
Some code modified from Joe Zagrodnik's 'plot_mesowest_3day.py', used for similar task in the OLYMPEX field campaign

**File Saving Information**
CSV files, one per day, save to: '/home/disk/funnel/impacts/data_archive/asos'
3-day plots, one per hour, save to: '/home/disk/funnel/impacts/archive/ops/asos'
'''
import os 
import pandas as pd 
import json            #javascript object notation encoder and decoder
import urllib 
import urllib.parse
import urllib.request
import math
import csv 
import time, datetime
from time import strftime 
from datetime import timedelta
import numpy as np 
import matplotlib 
from matplotlib.dates import DayLocator, HourLocator, DateFormatter
matplotlib.use('Agg') 
import matplotlib.transforms as transforms
import matplotlib.pyplot as plt 
import pickle

MINS_IN_HOUR = 60
HRS_IN_DAY = 24
missingValue = -999.

#define access token, sitelist, sitetitles, and directories to save files 
# Mason token
#token = '554c724392de446cb9f915fc14c1e8ce' #given to specific user after making account with synopticdata.com, Mason in this case
# Brodzik token
token = '8c150f37a5ba47ad929c0a24180e877c'

# site information
pickle_jar = '/home/disk/bob/impacts/bin/pickle_jar/'
infile = open(pickle_jar + "sitelist.pkl",'rb')
#infile = open(pickle_jar + "sitelist_test.pkl",'rb')
sitelist = pickle.load(infile)
infile.close()

# site titles
infile2 = open(pickle_jar + 'sitetitles.pkl','rb')
#infile2 = open(pickle_jar + 'sitetitles_test.pkl','rb')
sitetitles = pickle.load(infile2)
infile.close()

# FOR TESTING ONLY
#sitelist = ['KALB']
#sitetitles = ['Albany International Airport (NY)']
sitelist = ['KGLS']
sitetitles = ['Scholes International Airport (Galveston, TX)']

csv_dir = '/home/disk/funnel/impacts/data_archive/asos_precip'
plot_dir = '/home/disk/funnel/impacts/archive/ops/asos_precip'
#csv_dir = '/home/disk/funnel/impacts/data_archive/asos'
#plot_dir = '/home/disk/funnel/impacts/archive/ops/asos'
#csv_dir = '/home/disk/p/broneil/Documents/Impacts/ASOS_map/ASOS_CSV'
#plot_dir = '/home/disk/p/broneil/Documents/Impacts/ASOS_map/ASOS_plots'
#csv_dir = '/home/disk/meso-home/masonf3/IMPACTS/asos_data'  #for testing
#plot_dir = '/home/disk/meso-home/masonf3/IMPACTS/asos_plots' #for testing

def decode_weather_cond_code(data,missingValue):
    '''
    Given a weather_cond_code, returns A, B and C representing current weather condition codes
    See this link for a description of the algorithm:
    https://developers.synopticdata.com/about/weather-condition-codes/

    WNUM Values

    Code  Description
    0   (no value)
    1   R (mod rain)
    2   L (mod drizzle)
    3   S (mod snow)
    4   A (mod hail)
    5   T (thunder)
    6   H (haze)
    7   K (smoke)
    8   D (dust)
    9   F (fog)
    10  Q (squalls)
    11  V volcanic ash)
    12   
    13  R- (lt rain)
    14  R+ (hvy rain)
    15  ZR (mod frz rain)
    16  RW (mod rain shwr)
    17  L- (lt drizzle)
    18  L+ (hvy drizzle)
    19  ZL (frz drizzle)
    20  S- (lt snow)
    21  S+ (hvy snow)
    22  SW (mod snow shwr)
    23  IP (mod ice pellet)
    24  SG (mod snow grain)
    25  SP (mod snow pellet)
    26  A- (lt hail)
    27  A+ (hvy hail)
    28  T- (lt thunder)
    29  T+ (hvy thunder)
    30  IF (ice fog)
    31  GF (ground fog)
    32  BS (blowing snow)
    33  BD (blowing dust)
    34  BY (blowing spray)
    35  BN (blowing sand)
    36  IC (mod ice crystals)
    37  IN (ice needles)
    38  AP (small hail)
    39  KH (smoke, haze)
    40  PO (dust whirls)
    41  UP (unknown prcp)
    42   
    43   
    44   
    45   
    46   
    47   
    48   
    49  ZR- (lt frz rain)
    50  ZR+ (hvy frz rain)
    51  RW- (lt rain shwr)
    52  RW+ (hvy rain shwr)
    53  ZL- (lt freezing drizzle)
    54  ZL+ (hvy freezing drizzle)
    55  SW- (lt snow shwr)
    56  SW+ (hvy snow shwr)
    57  IP- (lt ice pellets)
    58  IP+ (hvy ice pellets)
    59  SG- (lt snow grains)
    60  SG+ (hvy snow grains)
    61  SP- (lt snow pellets)
    62  SP+ (hvy snow pellets)
    63  IPW (mod ice pellet shwr)
    64  IC- (lt ice crystals)
    65  IC+ (hvy ice crystals)
    66  TRW (mod thunder shwr)
    67  SPW (snow pellet shwr)
    68  BD+ (hvy blowing dust)
    69  BN+ (hvy blowing sand)
    70  BS+ (hvy blowing snow)
    71   
    72   
    73   
    74   
    75  IPW- (lt ice pellet shwr)
    76  IPW+ (hvy ice pellet shwr)
    77  TRW- (lt rain thunder shwr)
    78  TRW+ (hvy rain thunder shwr)
    79   
    And there are 3 Manual character codes which will only be sent on their own:
    
    Code        Description
    -1  Tornado
    -2  Funnel Cloud
    -3  Water Spout

    Parameters:
    code (int): value of weather condition code

    Returns:
    data (dataframe): with 3 new keys
    '''

    data['weather_code_1'] = [float('NaN') for x in np.arange(data.shape[0])]
    data['weather_code_2'] = [float('NaN') for x in np.arange(data.shape[0])]
    data['weather_code_3'] = [float('NaN') for x in np.arange(data.shape[0])]

    # decode values >= 6400
    indices = data.index[data['weather_cond_code_set_1'] >= 6400].tolist()
    for index in indices:
        data.at[index,'weather_code_1'] = math.trunc(data.at[index,'weather_cond_code_set_1']/6400)
        remainder = data.at[index,'weather_cond_code_set_1'] - (6400 * data.at[index,'weather_code_1'])
        if remainder >= 80:
            data.at[index,'weather_code_2'] = math.trunc(remainder/80)
            remainder = data.at[index,'weather_cond_code_set_1'] -(6400 * data.at[index,'weather_code_1']) - (80 * data.at[index,'weather_code_2'])
            if remainder > 0:
                data.at[index,'weather_code_3'] = remainder
        elif remainder > 0:
            data.at[index,'weather_code_2'] = remainder

    # decode values >= 80 and <6400
    data_sub = data.loc[ (data['weather_cond_code_set_1']>=80) & (data['weather_cond_code_set_1']<6400) ]
    indices = data_sub.index.tolist()
    for index in indices:
        data.at[index,'weather_code_1'] = math.trunc(data.at[index,'weather_cond_code_set_1']/80)
        remainder = data.at[index,'weather_cond_code_set_1'] - (80 * data.at[index,'weather_code_1'])
        if remainder != 0:
            data.at[index,'weather_code_2'] = remainder

    # decode values >0 and <80
    data_sub = data.loc[ (data['weather_cond_code_set_1']>0) & (data['weather_cond_code_set_1']<80) ]
    indices = data_sub.index.tolist()
    for index in indices:
        data.at[index,'weather_code_1'] = data.at[index,'weather_cond_code_set_1']


def load_and_save_station_data(site):
    '''Given a site station ID, returns 3-day DataFrame of specified weather variables. Also saves a each day's
    worth of data for the last three days into a .csv file for that station, within a folder for that day. 
    
    Parameters:
    site (str): string of ASOS station ID
    
    Returns: 
    df (dataframe): dataframe containing last 72 hours (3 days) of ASOS station data 
    
    *Saves .csv files to csv_dir listed near top of script*
    '''
    lower_site = site.lower()
    now = datetime.datetime.utcnow()
    
    ## ONLY USE THIS SECTION IF GRABBING LATEST DATA, OTHERWISE COMMENT OUT & USE CODE STARTING AT API CALL
    #definining dates in YYYYmmdd format (for saving and finding files)
    three_days_ago_date = (now-timedelta(hours=72)).strftime('%Y%m%d')
    two_days_ago_date = (now-timedelta(hours=48)).strftime('%Y%m%d')
    yesterday_date = (now-timedelta(hours=24)).strftime('%Y%m%d')
    today_date = now.strftime('%Y%m%d')
    
    #defining dates in YYYY-mm-dd format (for selecting ranges of data from dataframes)
    three_days_ago_date_dt_format = (now-timedelta(hours=72)).strftime('%Y-%m-%d')
    two_days_ago_date_dt_format = (now-timedelta(hours=48)).strftime('%Y-%m-%d')
    yesterday_date_dt_format = (now-timedelta(hours=24)).strftime('%Y-%m-%d')
    today_date_dt_format = now.strftime('%Y-%m-%d')
    
    path3_dir = csv_dir+'/'+three_days_ago_date
    path2_dir = csv_dir+'/'+two_days_ago_date
    path1_dir = csv_dir+'/'+yesterday_date
    path0_dir = csv_dir+'/'+today_date
    
    path3_file = path3_dir+'/ops.asos.'+three_days_ago_date+'.'+lower_site+'.csv'
    path2_file = path2_dir+'/ops.asos.'+two_days_ago_date+'.'+lower_site+'.csv'
    path1_file = path1_dir+'/ops.asos.'+yesterday_date+'.'+lower_site+'.csv'
    path0_file = path0_dir+'/ops.asos.'+today_date+'.'+lower_site+'.csv'
    
    #figuring out if most of last 3-day data already exists, and if so, grabbing it from os
    if os.path.exists(path3_file) and os.path.exists(path2_file) and os.path.exists(path1_file):
        three_days_ago_all = pd.read_csv(path3_file)
        three_days_ago_all['date_time'] = pd.to_datetime(three_days_ago_all['date_time'])
        three_days_ago_all = three_days_ago_all.set_index('date_time')
        
        two_days_ago_all = pd.read_csv(path2_file)
        two_days_ago_all['date_time'] = pd.to_datetime(two_days_ago_all['date_time'])
        two_days_ago_all = two_days_ago_all.set_index('date_time')
        
        yesterday_all = pd.read_csv(path1_file)
        yesterday_all['date_time'] = pd.to_datetime(yesterday_all['date_time'])
        yesterday_all = yesterday_all.set_index('date_time')
        
        #today's path won't exist yet if first hour of new day
        if os.path.exists(path0_file):
            today_all = pd.read_csv(path0_file)
            today_all['date_time'] = pd.to_datetime(today_all['date_time'])
            today_all = today_all.set_index('date_time')
        
            #If there's missing data for today, API will grab all data up to midnight
            earliest_time = pd.to_datetime(today_all.iloc[0].name)
            latest_time = pd.to_datetime(today_all.iloc[-1].name) 
            #Time from the first data point to midnight where the new dataset should begin
            earliest_time_to_midnight = (earliest_time.hour*60) + earliest_time.minute
            if earliest_time_to_midnight > 60: #Gets data since midnight
                time_length = now - datetime.datetime(now.year,now.month,now.day,0,0)
            else: #If no missing hours of data, then gets the difference between the last data point and the current time
                time_diff = now - latest_time
                time_length = str(int(np.round(time_diff.days + time_diff.seconds/60,0)))
        else: #If there's no data for today, get data since midnight plus any data missing from yesterday
            latest_time = pd.to_datetime(yesterday_all.iloc[-1].name)
            time_diff = now - latest_time
            time_length = str(int(np.round(time_diff.days + time_diff.seconds/60,0)))
            #time_length = now - datetime.datetime(now.year,now.month,now.day,0,0)
            #Converts to minutes
            #time_length = str(int(np.round(time_length.seconds/60,0)))
        data_type = 'appended'
    else: #Last 3 days worth of data (add in 20 minutes extra)
        time_length = str( (3 * HRS_IN_DAY * MINS_IN_HOUR) + 20 )
        data_type = 'entirely new'
    ##
    
    #use timeseries API service to get all but precip data
    args = {
        'recent':time_length,
        #'start':'201801010000',   
        #'end':'201801050000',
        'obtimezone':'UTC',
        'hfmetars':'1',
        #'precip':'1',
        #'vars':'air_temp,dew_point_temperature,wind_speed,wind_direction,wind_gust,sea_level_pressure,'\
        #'precip_accum,snow_depth,snow_water_equiv,estimated_snowfall_rate','weather_cond_code',
        'vars':'air_temp,dew_point_temperature,wind_speed,wind_direction,wind_gust,sea_level_pressure,'\
        'snow_depth,snow_water_equiv,estimated_snowfall_rate,weather_cond_code',
        'stids':site,
        'units':'temp|C,speed|kts,alti|inhg,pres|mb,precip|mm',
        'token':token
    }   #other vars that may be useful: alti, rh, wx_cond_code, wx_cond, past_wx_code
 
    apiString = urllib.parse.urlencode(args)
    url = "http://api.mesowest.net/v2/stations/timeseries"
    fullUrl = '{}?{}'.format(url,apiString)
    timeseries = urllib.request.urlopen(fullUrl).read()
    timeseriesDict = json.loads(timeseries.decode('utf-8'))
    
    #use precip API service to ge hourly precip data
    args = {
        'recent':time_length,
        #'start':'201801010000',   
        #'end':'201801050000',
        'pmode':'intervals',
        'interval':'hour',
        'obtimezone':'UTC',
        'stids':site,
        'units':'precip|mm',
        'token':token
    }
 
    apiString = urllib.parse.urlencode(args)
    url = "https://api.synopticdata.com/v2/stations/precip"
    fullUrl = '{}?{}'.format(url,apiString)
    precip = urllib.request.urlopen(fullUrl).read()
    precipDict = json.loads(precip.decode('utf-8'))

    #Sometimes the data is pretty messed up, this attempts to catch these situations
    try:
        #Check for non reporting stations
        if len(timeseriesDict['STATION']) == 0 or len(precipDict['STATION']) == 0:
            print("Problem reading data for %s. Data was not updated" % site)
            return 0 #Exits the function
        #Read dicts into dataframe objects
        new_ts_data = pd.DataFrame(timeseriesDict['STATION'][0]['OBSERVATIONS'])
        new_precip_data = pd.DataFrame(precipDict['STATION'][0]['OBSERVATIONS']['precipitation'])
        #Rename and remove columns in precip data
        new_precip_data.rename(columns={'last_report':'date_time','total':'precip_inc'},inplace=True)
        new_precip_data.drop(['count','first_report','interval','report_type'],axis=1,inplace=True)
    except:
        print("Problem reading data for %s. Data was not updated" % site)
        return 0
    
    # Merge dataframes
    merged_data = new_ts_data.copy()
    merged_data = merged_data.join(new_precip_data.set_index('date_time'), on='date_time')

    # Convert date_time strings to datetime objects
    merged_data['date_time'] = pd.to_datetime(merged_data['date_time'])

    # Set date_time as index
    merged_data = merged_data.set_index('date_time')

    # Decode weather codes and add them to dataframe
    if 'weather_cond_code_set_1' in merged_data.keys():
        decode_weather_cond_code(merged_data,missingValue)

    # Standaradize the format of all the ASOS csv files
    try:
        merged_data = merged_data[['air_temp_set_1','dew_point_temperature_set_1','dew_point_temperature_set_1d',
                                   #'precip_accumulated_set_1d','precip_intervals_set_1d',
                                   'precip_inc',
                                   'sea_level_pressure_set_1','sea_level_pressure_set_1d',
                                   'wind_direction_set_1','wind_gust_set_1','wind_speed_set_1',
                                   'weather_cond_code_set_1',
                                   'weather_code_1','weather_code_2','weather_code_3']]
    except KeyError as keyErr:
        #Catches non reported fields and enters a set of "NaNs" in their place                    
        #Edits the key error into a string which has only the missing fields with spaces inbetween
        keyErr = str(keyErr)[3:].replace("] not in index\"","")
        keyErr = keyErr.replace("\'","")
        keyErr = keyErr.replace("\\n","")

        #Splits the missing fields into a list
        missing_items = keyErr.split()
        #Adds a column of NaNs corrected for the length of the data
        for item in missing_items:
            merged_data[item] = [float('NaN') for x in np.arange(merged_data.shape[0])] 
        #Standardizes the format
        merged_data = merged_data[['air_temp_set_1','dew_point_temperature_set_1','dew_point_temperature_set_1d',
                             #'precip_accumulated_set_1d','precip_intervals_set_1d',
                             'precip_inc',
                             'sea_level_pressure_set_1','sea_level_pressure_set_1d',
                             'wind_direction_set_1','wind_gust_set_1','wind_speed_set_1',
                             'weather_cond_code_set_1',
                             'weather_code_1','weather_code_2','weather_code_3']]
    
    #find datetime 3 days ago for slicing later
    begin_offset_dt_format = (merged_data.index[-1]-timedelta(hours=72)).strftime('%Y-%m-%d %H:%M') 
    
    #concatenating existing .csv files, saving yesterday's data and today's as new files
    if os.path.exists(path3_file) and os.path.exists(path2_file) and os.path.exists(path1_file):
        if os.path.exists(path0_file):
            df_extra = pd.concat([three_days_ago_all,two_days_ago_all,yesterday_all,today_all,merged_data])
        else:
            df_extra = pd.concat([three_days_ago_all,two_days_ago_all,yesterday_all,merged_data])
        df = df_extra[begin_offset_dt_format:]
        
        # Copy index to new column called 'dt' - there must be an easier way to do this!!
        #df['dt'] = df.index
        df.reset_index(level=0,inplace=True)
        df['dt'] = df['date_time']
        df = df.set_index('date_time')

        # Remove duplicates and drop the 'dt' column
        df = df.drop_duplicates()
        df = df.drop(labels='dt',axis=1)

        #either add to or create today's data file
        if not os.path.exists(path0_dir):
            os.makedirs(path0_dir)
            
        #Making sure the data is in the right day -> Could be the case for the first run
        if today_date == df.index[-1].strftime('%Y%m%d'):
            today_data = df[today_date_dt_format]
            today_data = today_data.sort_index()
            today_data.to_csv(path0_file)

        # When code is run right after date change, there might be some new data for the end of yesterday
        yesterday_data = df[yesterday_date_dt_format]
        if yesterday_all.iloc[-1].name < yesterday_data.iloc[-1].name:
            yesterday_data.to_csv(path1_file)

    else:
        #if no 3-day data exists yet in os as .csv files, grab it all using API instead
        #delete extra data from beginning
        df_extra = merged_data
        df = df_extra[begin_offset_dt_format:]

        # add date_time (dt) as new column to check for duplicate times
        #df['dt'] = df.index
        df.reset_index(level=0,inplace=True)
        df['dt'] = df['date_time']
        df = df.set_index('date_time')
        
        df = df.drop_duplicates()
        df = df.drop(labels='dt',axis=1)
        
        #Three days ago data
        if not os.path.exists(path3_dir): 
            os.makedirs(path3_dir)
        #If any data is missing from previous dates, function will return 0
        try:
            three_days_ago_data = df_extra[three_days_ago_date_dt_format]
        except:
            print("Missing data from three days ago for %s. Data was not updated." %site)
            return 0
        three_days_ago_data.to_csv(path3_file)
        
        #Two days ago data
        if not os.path.exists(path2_dir):
            os.makedirs(path2_dir)
        #If any data is missing from previous dates, function will return 0
        try:
            two_days_ago_data = df[two_days_ago_date_dt_format]
        except:
            print("Missing data from two days ago for %s. Data was not updated." %site)
            return 0
        two_days_ago_data.to_csv(path2_file)
        
        #Yesterday Data
        if not os.path.exists(path1_dir):
            os.makedirs(path1_dir)
        #If any data is missing from previous dates, function will return 0
        try:
            yesterday_data = df[yesterday_date_dt_format]
        except: 
            print("Missing data from yesterday for %s. Data was not updated." %site)
            return 0
        yesterday_data.to_csv(path1_file)

        #Today Data
        if not os.path.exists(path0_dir):
            os.makedirs(path0_dir)
        # Prevent problem when script is run first time in a new day when no data for that day exists yet
        if today_date == df.index[-1].strftime('%Y%m%d'):
            today_data = df[today_date_dt_format]
            today_data.to_csv(path0_file)
            
    #print(data_type + ' data')
    return df

def plot_station_data(site,sitetitle,df):
    '''Given site station ID, the title of that site, and a dataframe of ASOS observation data from the last 3 days,
    returns a plot of the last 3-days of weather at that site. 
    
    Parameters: 
    site (str): string of ASOS station ID
    sitetitle (str): string of ASOS station full name 
    df (dataframe): dataframe containing last 72 hours (3 days) of ASOS station data 
    
    Returns: 
    None
    
    *saves plots to plot_dir listed near top of script*
    '''
    
    #Returns if the station is not reporting
    if isinstance(df, int): 
        return
    
    lower_site = site.lower()
    timestamp_end=str(df.index[-1].strftime('%Y%m%d%H%M'))
    dt = df.index[:]
    graphtimestamp_start=dt[0].strftime("%m/%d/%y") 
    graphtimestamp=dt[-1].strftime("%m/%d/%y")      
    now = datetime.datetime.utcnow()
    today_date = dt[-1].strftime('%Y%m%d')
    markersize = 1.5
    linewidth = 1.0
    
    #make figure and axes
    fig = plt.figure()
    fig.set_size_inches(18,10)
    if 'snow_depth_set_1' in df.keys():          #six axes if snow depth 
        ax1 = fig.add_subplot(6,1,1)
        ax2 = fig.add_subplot(6,1,2,sharex=ax1)
        ax3 = fig.add_subplot(6,1,3,sharex=ax1)
        ax4 = fig.add_subplot(6,1,4,sharex=ax1)
        ax5 = fig.add_subplot(6,1,5,sharex=ax1)
        ax6 = fig.add_subplot(6,1,6,sharex=ax1)
        ax6.set_xlabel('Time (UTC)')
    else:
        ax1 = fig.add_subplot(5,1,1)             #five axes if no snow depth
        ax2 = fig.add_subplot(5,1,2,sharex=ax1)
        ax3 = fig.add_subplot(5,1,3,sharex=ax1)
        ax4 = fig.add_subplot(5,1,4,sharex=ax1)
        ax5 = fig.add_subplot(5,1,5,sharex=ax1)
        ax5.set_xlabel('Time (UTC)')
    
    #ax1.set_title(site+' '+sitetitle+' '+graphtimestamp_start+' - '+graphtimestamp+' '+now.strftime("%H:%MZ"))
    ax1.set_title(site+' '+sitetitle+' '+graphtimestamp_start+' - '+graphtimestamp)
    #plot airT and dewT
    if 'air_temp_set_1' in df.keys():
        airT = df['air_temp_set_1']
        ax1.plot_date(dt,airT,'o-',label="Temp",color="blue",linewidth=linewidth,markersize=markersize)  
    if 'dew_point_temperature_set_1d' in df.keys():
        dewT = df['dew_point_temperature_set_1d']
        ax1.plot_date(dt,dewT,'o-',label="Dew Point",color="black",linewidth=linewidth,markersize=markersize)
    elif 'dew_point_temperature_set_1' in df.keys():
        dewT = df['dew_point_temperature_set_1']
        dewT_new = dewT.dropna()
        dewT_dt_list = []
        for i in range(0,len(dewT)):
            if pd.isnull(dewT[i]) == False:
                dewT_dt_list.append(dt[i])
        ax1.plot_date(dewT_dt_list,dewT_new,'o-',label="Dew Point",color="black",linewidth=linewidth,markersize=markersize)
    if ax1.get_ylim()[0] < 0 < ax1.get_ylim()[1]:
        ax1.axhline(0, linestyle='-', linewidth = 1.0, color='deepskyblue')
        trans = transforms.blended_transform_factory(ax1.get_yticklabels()[0].get_transform(), ax1.transData)
        ax1.text(0,0,'0C', color="deepskyblue", transform=trans, ha="right", va="center") #light blue line at 0 degrees C
    ax1.set_ylabel('Temp ($^\circ$C)')
    ax1.legend(loc='best',ncol=2)
    axes = [ax1]                             #begin axes

    #plotting wind speed and gust
    if 'wind_speed_set_1' in df.keys():
        wnd_spd = df['wind_speed_set_1']
        ax2.plot_date(dt,wnd_spd,'o-',label='Speed',color="forestgreen",linewidth=linewidth,markersize=markersize)
    if 'wind_gust_set_1' in df.keys():
        wnd_gst = df['wind_gust_set_1']
        max_wnd_gst = wnd_gst.max(skipna=True)
        ax2.plot_date(dt,wnd_gst,'o-',label='Gust (Max ' + str(round(max_wnd_gst,1)) + 'kt)',color="red",linewidth=0.0,markersize=markersize) 
    ax2.set_ylabel('Wind (kt)')
    ax2.legend(loc='best',ncol=2)
    axes.append(ax2)
    
    #plotting wind direction
    if 'wind_direction_set_1' in df.keys():
        wnd_dir = df['wind_direction_set_1']
        ax3.plot_date(dt,wnd_dir,'o-',label='Direction',color="purple",linewidth=0.2, markersize=markersize)
    ax3.set_ylim(-10,370)
    ax3.set_ylabel('Wind Direction')
    ax3.set_yticks([0,90,180,270,360])
    axes.append(ax3)
    
    #plotting MSLP
    if 'sea_level_pressure_set_1d' in df.keys():
        mslp = df['sea_level_pressure_set_1d']
        max_mslp = mslp.max(skipna=True)
        min_mslp = mslp.min(skipna=True)
        labelname = 'Min ' + str(round(min_mslp,1)) + 'hPa, Max ' + str(round(max_mslp,2)) + 'hPa'
        ax4.plot_date(dt,mslp,'o-',label=labelname,color='darkorange',linewidth=linewidth,markersize=markersize)
    elif 'sea_level_pressure_set_1' in df.keys():
        mslp = df['sea_level_pressure_set_1']
        mslp_new = mslp.dropna()
        mslp_dt_list = []
        for i in range(0,len(mslp)):
            if pd.isnull(mslp[i]) == False:
                mslp_dt_list.append(dt[i])
        max_mslp = mslp.max(skipna=True)
        min_mslp = mslp.min(skipna=True)
        labelname = 'Min ' + str(round(min_mslp,2)) + 'hPa, Max ' + str(round(max_mslp,2)) + 'hPa'
        ax4.plot_date(mslp_dt_list,mslp_new,'o-',label=labelname,color='darkorange',linewidth=linewidth,markersize=markersize)
    ax4.legend(loc='best')
    ax4.set_ylabel('MSLP (hPa)')
    ax4.set_xlabel('Time (UTC)')
    axes.append(ax4)

    # ADD RAIN AND SNOW CODES TO PLOT
    #plotting precip accumulation
    if 'precip_inc' in df.keys():
        precip_inc = df['precip_inc']
        precip_inc_new = precip_inc.dropna()
        precip_inc_new = list(precip_inc_new.values)
        precip_accum = 0.0
        precip_accum_list = []
        for increment in precip_inc_new:
            precip_accum = precip_accum + increment
            precip_accum_list.append(precip_accum)
        precip_dt_list = []
        for i in range(0,len(precip_inc)):
            if pd.isnull(precip_inc[i]) == False:
                precip_dt_list.append(dt[i])
        max_precip = max(precip_accum_list)
        labelname = 'Precip (' + str(round(max_precip,2)) + 'mm)'
        ax5.plot_date(precip_dt_list,precip_accum_list,'o-',label=labelname,color='navy',linewidth=linewidth,markersize=markersize)
        if max_precip > 0:
            ax5.set_ylim(-0.1*max_precip,max_precip+max_precip*0.2)
        else:
            ax5.set_ylim(-0.5,5)
    ax5.legend(loc='best')
    ax5.set_ylabel('Precip (mm)')
    axes.append(ax5)
    
    #plotting snow depth
    if 'snow_depth_set_1' in df.keys():
        snow_depth = df['snow_depth_set_1']
        snow_depth_new = snow_depth.dropna()
        snow_depth_dt_list = []
        for i in range(0,len(snow_depth)):
            if pd.isnull(snow_depth[i]) == False:
                snow_depth_dt_list.append(dt[i])  
        max_snow_depth = snow_depth.max(skipna=True)
        min_snow_depth = snow_depth.min(skipna=True)
        labelname = 'Min Depth ' + str(round(min_snow_depth,2)) + 'mm, Max Depth ' + str(round(max_snow_depth,2)) + 'mm'
        ax6.plot_date(snow_depth_dt_list,snow_depth_new,'o-',label=labelname,color='deepskyblue',linewidth=linewidth,markersize=markersize)
        if max_snow_depth > 0:
            ax6.set_ylim(-0.1*max_snow_depth,max_snow_depth+max_snow_depth*0.2)
        else:
            ax6.set_ylim(-0.5,5)
        ax6.legend(loc='best')
        ax6.set_ylabel('Snow Depth (mm)')
        axes.append(ax6)
        
    for ax in axes: 
        ax.spines["top"].set_visible(False)  #darker borders on the grids of each subplot
        ax.spines["right"].set_visible(False)  
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.tick_params(axis='x',which='both',bottom='on',top='off')     #add ticks at labeled times
        ax.tick_params(axis='y',which='both',left='on',right='off') 

        ax.xaxis.set_major_locator( DayLocator() )
        ax.xaxis.set_major_formatter( DateFormatter('%b-%d') )
        
        ax.xaxis.set_minor_locator( HourLocator(np.linspace(6,18,3)) )
        ax.xaxis.set_minor_formatter( DateFormatter('%H') )
        ax.fmt_xdata = DateFormatter('Y%m%d%H%M%S')
        ax.yaxis.grid(linestyle = '--')
        ax.get_yaxis().set_label_coords(-0.06,0.5)
       
    plot_path = plot_dir+'/'+today_date
    if not os.path.exists(plot_path):
            os.makedirs(plot_path)
    try:
        plt.savefig(plot_path+'/ops.asos.'+timestamp_end+'.'+lower_site+'.png',bbox_inches='tight')
    except:
        print("Problem saving figure for %s. Usually a maxticks problem" %site)
    plt.close()

for i,site in enumerate(sitelist):
    #print(site)
    sitetitle = sitetitles[i]
    df = load_and_save_station_data(site)
    plot_station_data(site,sitetitle,df)
