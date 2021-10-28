#!/usr/bin/python3

import os 
import pandas as pd 
import json            #javascript object notation encoder and decoder
import urllib 
import urllib.parse
import urllib.request
import csv 
import time, datetime
from time import strftime 
from datetime import timedelta
from datetime import datetime
import pickle
import numpy as np

# output data order
# 1. date_time
# 2. air_temp_set_1
# 3. dew_point_temperature_set_1
# 4. dew_point_temperature_set_1d
# 5. precip_accumulated_set_1d
# 6. precip_intervals_set_1d
# 7. sea_level_pressure_set_1
# 8. sea_level_pressure_set_1d
# 9. wind_direction_set_1
# 10. wind_gust_set_1
# 11. wind_speed_set_1

# Brodzik token
token = '8c150f37a5ba47ad929c0a24180e877c'

# site information
pickle_jar = '/home/disk/bob/impacts/bin/pickle_jar/'
infile = open(pickle_jar + "sitelist.pkl",'rb')
sitelist = pickle.load(infile)
infile.close()

# site title information
infile2 = open(pickle_jar + 'sitetitles.pkl','rb')
sitetitles = pickle.load(infile2)
infile.close()

# date of interest
date_str = '20200201'
date_obj = datetime.strptime(date_str,'%Y%m%d')
datePlusOne_obj = date_obj + timedelta(days=1)
datePlusOne_str = datePlusOne_obj.strftime('%Y%m%d')
date_dt_format = date_obj.strftime('%Y-%m-%d')
csv_dir = '/home/disk/funnel/impacts/data_archive/asos_test/'+date_str
if not os.path.exists(csv_dir):
    os.makedirs(csv_dir)

# for testing
#sitelist = ['KBOS']
#sitetitles = ['BOSTON INTL']

# go through sites in sitelist and get data
for i,site in enumerate(sitelist):

    print(site)
    
    sitetitle = sitetitles[i]  # global attribute
    lower_site = site.lower()

    #use API service
    startStr = date_str+'0000'
    endStr = datePlusOne_str+'0000'
    args = {
        #'recent':time_length,
        #'start':'202002010000',   
        'start': startStr,   
        'end':   endStr,
        'obtimezone':'UTC',
        'hfmetars':'1',
        'precip':'1',
        'vars':'air_temp,dew_point_temperature,wind_speed,wind_direction,wind_gust,sea_level_pressure,'\
        'precip_accum,snow_depth,snow_water_equiv,estimated_snowfall_rate',
        'stids':site,
        'units':'temp|C,speed|kts,alti|inhg,pres|mb,precip|mm',
        'token':token
    }   #other vars that may be useful: alti, rh, wx_cond_code, wx_cond, past_wx_code
 
    apiString = urllib.parse.urlencode(args)
    url = "http://api.mesowest.net/v2/stations/timeseries"
    fullUrl = '{}?{}'.format(url,apiString)
    response = urllib.request.urlopen(fullUrl).read()
    responseDict = json.loads(response.decode('utf-8'))
    #print(responseDict.keys())
    try:
        new_data = pd.DataFrame(responseDict['STATION'][0]['OBSERVATIONS'])
    except:
        print("Problem reading data for %s. Data was not updated" % site)
        continue

    new_data['date_time'] = pd.to_datetime(new_data['date_time'])
    new_data = new_data.set_index('date_time')

    # Standaradize the format of all the ASOS csv files
    try:
        new_data = new_data[['air_temp_set_1','dew_point_temperature_set_1','dew_point_temperature_set_1d',
                             'precip_accumulated_set_1d','precip_intervals_set_1d',
                             'sea_level_pressure_set_1','sea_level_pressure_set_1d',
                             'wind_direction_set_1','wind_gust_set_1','wind_speed_set_1']]
    except KeyError as keyErr:

        #Catches non reported fields and enters a set of "NaNs" in their place                    
        #Edits the key error into a string which has only the missing fields with spaces inbetween
        keyErr = str(keyErr)[3:].replace("] not in index\"","")
        keyErr = keyErr.replace("\'","")
        keyErr = keyErr.replace("\\n","")

        #Splits the missing fields into a list
        missing_items = keyErr.split()
        #print(missing_items)
        for item in missing_items: #Adds a column of NaNs corrected for the length of the data
            new_data[item] = [float('NaN') for x in np.arange(new_data.shape[0])] 
        #Standardizes the format
        new_data = new_data[['air_temp_set_1','dew_point_temperature_set_1','dew_point_temperature_set_1d',
                             'precip_accumulated_set_1d','precip_intervals_set_1d',
                             'sea_level_pressure_set_1','sea_level_pressure_set_1d',
                             'wind_direction_set_1','wind_gust_set_1','wind_speed_set_1']]

    df = new_data
    # Eliminate any data for days other than start date
    data = df[date_dt_format]
    # Sort by date
    data = data.sort_index(axis=0)
    # Convert to csv
    data.to_csv(csv_dir+'/ops.asos.'+date_str+'.'+lower_site+'.csv')
