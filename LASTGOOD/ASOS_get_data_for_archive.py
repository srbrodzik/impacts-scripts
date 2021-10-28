#!/usr/bin/python3

import os 
import pandas as pd 
import xarray
import json            #javascript object notation encoder and decoder
import urllib 
import urllib.parse
import urllib.request
import math
import csv 
import time, datetime
from time import strftime 
from datetime import timedelta
from datetime import datetime
import pickle
import numpy as np

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
# 12. weather_cond_code_set_1

# Brodzik token
token = '8c150f37a5ba47ad929c0a24180e877c'

missingValue = -999.

# site information
pickle_jar = '/home/disk/bob/impacts/bin/pickle_jar/'
infile = open(pickle_jar + "sitelist.pkl",'rb')
sitelist = pickle.load(infile)
infile.close()
# FOR TESTING
#sitelist = ['KDAW']

varDict = {'time':{'units':'seconds', 'long_name':'seconds since 1970-01-01'},
           'air_temp_set_1':{'units':'degC' ,'long_name':'temperature' },
           'dew_point_temperature_set_1':{'units':'degC' ,'long_name':'instantaneous dewpoint temperature' },
           'dew_point_temperature_set_1d':{'units':'degC' ,'long_name':'average dewpoint temperature' },
           'precip_accumulated_set_1d':{'units':'mm' ,'long_name':'accumulated precip for day' },
           'precip_intervals_set_1d':{'units':'mm' ,'long_name':'precip for last time interval' },
           'sea_level_pressure_set_1':{'units':'mb' ,'long_name':'instantaneous sea level pressure' },
           'sea_level_pressure_set_1d':{'units':'mb' ,'long_name':'average sea level pressure for day' },
           'wind_direction_set_1':{'units':'deg' ,'long_name':'instantaneous wind direction' },
           'wind_gust_set_1':{'units':'kts' ,'long_name':'instantaneous wind gust' },
           'wind_speed_set_1':{'units':'kts' ,'long_name':'instantaneous wind speed' },
           #'weather_cond_code_set_1':{'units':'none' ,'long_name':'current weather code' },
           'weather_code_1':{'units':'none' ,'long_name':'current weather code' },
           'weather_code_2':{'units':'none' ,'long_name':'current weather code' },
           'weather_code_3':{'units':'none' ,'long_name':'current weather code' }}

ncPrefix = 'IMPACTS_ASOS'

# dates of interest
date_strs = ['20200101','20200102','20200103','20200104','20200105',
             '20200106','20200107','20200108','20200109','20200110',
             '20200111','20200112','20200113','20200114','20200115',
             '20200116','20200117','20200118','20200119','20200120',
             '20200121','20200122','20200123','20200124','20200125',
             '20200126','20200127','20200128','20200129','20200130','20200131',
             '20200201','20200202','20200203','20200204','20200205',
             '20200206','20200207','20200208','20200209','20200210',
             '20200211','20200212','20200213','20200214','20200215',
             '20200216','20200217','20200218','20200219','20200220',
             '20200221','20200222','20200223','20200224','20200225',
             '20200226','20200227','20200228','20200229']
# FOR TESTING
#date_strs = ['20200101']

for date_str in date_strs:
    date_obj = datetime.strptime(date_str,'%Y%m%d')
    datePlusOne_obj = date_obj + timedelta(days=1)
    datePlusOne_str = datePlusOne_obj.strftime('%Y%m%d')
    date_dt_format = date_obj.strftime('%Y-%m-%d')
    csvDir = '/home/disk/funnel/impacts/data_archive/asos_csv/'+date_str
    if not os.path.exists(csvDir):
        os.makedirs(csvDir)
    ncDir = '/home/disk/funnel/impacts/data_archive/asos_nc/'+date_str
    if not os.path.exists(ncDir):
        os.makedirs(ncDir)
    
    # go through sites in sitelist and get data
    for i,site in enumerate(sitelist):

        print(date_str,site)
    
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

        # Read dict into dataframe object
        try:
            data = pd.DataFrame(responseDict['STATION'][0]['OBSERVATIONS'])
        except:
            print("Problem reading data for %s. Data was not updated" % site)
            continue

        # Convert date_time strings to datetime objects
        data['date_time'] = pd.to_datetime(data['date_time'])
        # Rename 'date_time' to 'time'
        data = data.rename(columns={'date_time':'time'})
        # Set date_time as index
        data = data.set_index('time')

        # Decode weather codes and add them to dataframe
        if 'weather_cond_code_set_1' in data.keys():
            decode_weather_cond_code(data,missingValue)

        # Standaradize the format of all the ASOS csv files
        try:
            data = data[['air_temp_set_1','dew_point_temperature_set_1','dew_point_temperature_set_1d',
                         'precip_accumulated_set_1d','precip_intervals_set_1d',
                         'sea_level_pressure_set_1','sea_level_pressure_set_1d',
                         'wind_direction_set_1','wind_gust_set_1','wind_speed_set_1',
                         'weather_code_1','weather_code_2','weather_code_3']]
        except KeyError as keyErr:
            #Catches non reported fields and enters a set of "NaNs" in their place                    
            #Edits the key error into a string which has only the missing fields with spaces in between
            keyErr = str(keyErr)[3:].replace("] not in index\"","")
            keyErr = keyErr.replace("\'","")
            keyErr = keyErr.replace("\\n","")

            #Splits the missing fields into a list
            missing_items = keyErr.split()
            #print(missing_items)
            for item in missing_items: #Adds a column of NaNs corrected for the length of the data
                data[item] = [float('NaN') for x in np.arange(data.shape[0])] 
            #Standardizes the format
            data = data[['air_temp_set_1','dew_point_temperature_set_1','dew_point_temperature_set_1d',
                         'precip_accumulated_set_1d','precip_intervals_set_1d',
                         'sea_level_pressure_set_1','sea_level_pressure_set_1d',
                         'wind_direction_set_1','wind_gust_set_1','wind_speed_set_1',
                         'weather_code_1','weather_code_2','weather_code_3']]

        # Eliminate any data for days other than start date
        data = data[date_dt_format]
        # Sort by date
        data = data.sort_index(axis=0)
        # Convert to csv
        data.to_csv(csvDir+'/IMPACTS_ASOS_'+date_str+'_'+lower_site+'.csv')

        # -----------------
        # Convert to netcdf
        #------------------

        '''
        #----------------------------------------------------------------------------------------------------------------
        ## Use these lines if doing this as a separate step
        ## read in csv file
        #lower_site = 'kbos'
        #data = pd.read_csv('/home/disk/funnel/impacts-website/data_archive/asos_csv/20200202/ops.asos.20200202.kbos.csv') 
        ## Convert date_time strings to datetime objects
        #data['time'] = pd.to_datetime(data['time'])
        ## Set date_time as index
        #data = data.set_index('time')
        #----------------------------------------------------------------------------------------------------------------
        '''

        # Convert 'times' to seconds since 1970-01-01
        data.index = data.index.map(lambda time: int( (time - datetime(1970,1,1)).total_seconds() ) )

        # For all vars except 'time' handle missing values
        for key in data.keys():
            # if missing values in data, have to replace with NaNs and then convet to numeric
            # as it originaly is read strings instead of float64; coerce flag nicely takes
            # anything that cannot be converted and puts NaN
            if data[key].dtype.name != 'float64' and data[key].dtype.name != 'int64':
                data[key] = pd.to_numeric(data[key], errors='coerce')

        # Create xarray and assign var and global attributes
        xr = xarray.Dataset.from_dataframe(data)
        for var in varDict.keys():
            xr[var].attrs=varDict[var]
        #xr.attrs['weather_code_reference'] = 'https://developers.synopticdata.com/about/weather-condition-codes'
        xr.attrs['weather_code_reference'] = 'See Weather Codes (WNUM) in https://www.unidata.ucar.edu/software/gempak/man/parm/apxA.html'

        # Create ncFile name
        ncFile = ncDir+'/'+ncPrefix+'_'+date_str+'_'+lower_site+'.nc'
        
        # Convert xarray to netcdf with all _FillValues set to missing_value
        encoding ={}
        for var in varDict.keys():
            if var != 'time':
                encoding[var] = {'_FillValue':missingValue}
        xr.to_netcdf(ncFile,encoding=encoding)
       

    
