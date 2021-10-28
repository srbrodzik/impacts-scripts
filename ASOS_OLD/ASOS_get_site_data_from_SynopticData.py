#!/usr/bin/python3

# NOTE: CHANGE date_time COLUMN NAME TO time TO ENABLE PLOTTING TO WORK WITH csv FILES

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
from datetime import datetime
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

# Brodzik token
token = '8c150f37a5ba47ad929c0a24180e877c'

sitelist = ['CYTR']
#sitelist = ['KITH','KRUT','KCSH','CYTR']
csv_dir = '/home/disk/funnel/impacts/data_archive/asos_csv'

date = '20200207'

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

    #definining dates in YYYYmmdd format (for saving and finding files)
    today_date = date  # string
    today_dt_obj = datetime.strptime(today_date,'%Y%m%d') # datetime object
    today_date_dt_format = today_dt_obj.strftime('%Y-%m-%d')  # YYYY-mm-dd format
    
    path0_dir = csv_dir+'/'+today_date
    path0_file = path0_dir+'/IMPACTS_ASOS_'+today_date+'_'+lower_site+'.csv'
    
    #use API service 
    args = {
        #'recent':time_length,
        'start':'202002070000',   
        'end':'202002072359',
        'obtimezone':'UTC',
        'hfmetars':'1',
        'precip':'1',
        'vars':'air_temp,dew_point_temperature,wind_speed,wind_direction,wind_gust,sea_level_pressure,'\
        'precip_accum,snow_depth,snow_water_equiv,estimated_snowfall_rate,weather_cond_code',
        'stids':site,
        'units':'temp|C,speed|kts,alti|inhg,pres|mb,precip|mm',
        'token':token
    }   #other vars that may be useful: alti, rh, wx_cond_code, wx_cond, past_wx_code
 
    apiString = urllib.parse.urlencode(args)
    url = "http://api.mesowest.net/v2/stations/timeseries"
    fullUrl = '{}?{}'.format(url,apiString)
    response = urllib.request.urlopen(fullUrl).read()
    responseDict = json.loads(response.decode('utf-8'))
    try:
        #Sometimes the data is pretty messed up, this attempts to catch these situations
        if len(responseDict['STATION']) == 0: #Checks for non reporting stations
            print("Problem reading data for %s. Data was not updated" % site)
            return 0 #Exits the function
        new_data = pd.DataFrame(responseDict['STATION'][0]['OBSERVATIONS'])
    except:
        print("Problem reading data for %s. Data was not updated" % site)
        return 0
    
    # Convert date_time strings to datetime objects
    new_data['date_time'] = pd.to_datetime(new_data['date_time'])
    
    # Set date_time as index
    new_data = new_data.set_index('date_time')

    # Decode weather codes and add them to dataframe
    if 'weather_cond_code_set_1' in new_data.keys():
        decode_weather_cond_code(new_data,missingValue)

    # Standaradize the format of all the ASOS csv files
    try: 
        new_data = new_data[['air_temp_set_1','dew_point_temperature_set_1','dew_point_temperature_set_1d',
                             'precip_accumulated_set_1d','precip_intervals_set_1d',
                             'sea_level_pressure_set_1','sea_level_pressure_set_1d',
                             'wind_direction_set_1','wind_gust_set_1','wind_speed_set_1',
                             'weather_cond_code_set_1',
                             'weather_code_1','weather_code_2','weather_code_3']]
    #Catches non reported fields and enters a set of "NaNs" in their place                    
    except KeyError as keyErr:

        #Edits the key error into a string which has only the missing fields with spaces inbetween
        keyErr = str(keyErr)[3:].replace("] not in index\"","")
        keyErr = keyErr.replace("\'","")
        keyErr = keyErr.replace("\\n","")

        #Splits the missing fields into a list
        missing_items = keyErr.split()
        for item in missing_items: #Adds a column of NaNs corrected for the length of the data
            new_data[item] = [float('NaN') for x in np.arange(new_data.shape[0])] 
        #Standardizes the format
        new_data = new_data[['air_temp_set_1','dew_point_temperature_set_1','dew_point_temperature_set_1d',
                             'precip_accumulated_set_1d','precip_intervals_set_1d',
                             'sea_level_pressure_set_1','sea_level_pressure_set_1d',
                             'wind_direction_set_1','wind_gust_set_1','wind_speed_set_1',
                             'weather_cond_code_set_1',
                             'weather_code_1','weather_code_2','weather_code_3']]
    
    #find datetime 3 days ago for slicing later
    #begin_offset_dt_format = (new_data.index[-1]-timedelta(hours=72)).strftime('%Y-%m-%d %H:%M') 
    
    #concatenating existing .csv files, saving yesterday's data and today's as new files
    data = new_data[today_date_dt_format]
    data = data.sort_index()
    data.to_csv(path0_file)

for i,site in enumerate(sitelist):
    #print(site)
    df = load_and_save_station_data(site)
