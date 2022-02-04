#!/usr/bin/python3

import os 
import pandas as pd 
import xarray
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

missingValue = -999
convertToCdf = 0   # set to 1 if you want to output netcdf file as well

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
           'wind_speed_set_1':{'units':'kts' ,'long_name':'instantaneous wind speed' } }

# date of interest
date_str = '20200207'
date_obj = datetime.strptime(date_str,'%Y%m%d')
datePlusOne_obj = date_obj + timedelta(days=1)
datePlusOne_str = datePlusOne_obj.strftime('%Y%m%d')
date_dt_format = date_obj.strftime('%Y-%m-%d')
csvDir = '/home/disk/funnel/impacts/data_archive/asos_csv/'+date_str
if not os.path.exists(csvDir):
    os.makedirs(csvDir)

# create netcdf directory, if necessary
if convertToCdf:
    ncDir = '/home/disk/funnel/impacts/data_archive/asos_nc/'+date_str
    if not os.path.exists(ncDir):
        os.makedirs(ncDir)
    ncPrefix = 'IMPACTS_asos'
    
# sites of interest
sitelist = {'KACY':'ATLANTIC CITY INTL AP',
            'KADW':'JOINT BASE ANDREWS AP',
            'KAHN':'ATHENS BEN EPPS GA AP',
            'KAVC':'MECKLENBURG BRUNSWICK RGNL AP',
            'KAVL':'ASHEVILLE RGNL AP',
            'KCDW':'ESSEX COUNTY AP',
            'KCEW':'BOB SIKES-EGLIN AFB AP',
            'KCHA':'LOVELL FIELD CHATTANOOGA AP',
            'KCHS':'CHARLESTON AFB INTL AP',
            'KCKB':'CLARKSBURG BENEDUM AP',
            'KCQX':'CHATHAM MUNI AP',
            'KDAN':'DANVILLE RGNL AP',
            'KEXX':'DAVIDSON COUNTY AP',
            'KFBG':'SIMMONS FT BRAGGS AF',
            'KFFC':'ATLANTA REG AP FALCON FIELD',
            'KGAD':'NE ALABAMA REG AP',
            'KGZH':'EVERGREEN REG AP-MIDDLETON FIELD',
            'KHFF':'MACKALL ARMY AF',
            'KHKY':'HICKORY REG AP',
            'KHLX':'TWIN COUNTY VA AP',
            'KHSE':'BILLY MITCHELL HATTERAS AP',
            'KHTS':'HUNTINGTON TRI-STATE AP',
            'KHWO':'NORTH PERRY HOLLYWOOD AP',
            'KINT':'SMITH REYNOLDS WINST-SALEM AP',
            'KISP':'ISLIP-LI MACARTHUR AP',
            'KLEE':'LEESBURG INTL AP',
            'KLSF':'LAWSON ARMY FT BENNING AF',
            'KLYH':'LYNCHBURG INTL AP',
            'KMAI':'MARIANNA MUNI AP',
            'KMGM':'MONTGOMERY REG AP',
            'KMOB':'MOBILE REG AP',
            'KMSY':'LOUIS ARMSTRONG NEW ORLEANS INTL AP',
            'KMYR':'MYRTLE BEACH INTL AP',
            'KNEL':'LAKEHURST MAXFIELD AP',
            'KNFE':'FENTRESS NAVAL AUX FIELD',
            'KNGU':'NORFOLK NAS',
            'KNMM':'MERIDIAN NAS',
            'KNSE':'WHITING FIELD NAS NORTH',
            'KOFP':'MIAMI-OPA LOCKA EXEC AP',
            'KOXB':'OCEAN CITY MUNI AP',
            'KOXC':'WATERBURY-OXFORD AP',
            'KPAM':'TYNDALL AFB AP',
            'KPIB':'HATTIESBURG-LAUREL REG AP',
            'KRHP':'WESTERN CAROLINA REG AP',
            'KRIC':'RICHMOND INTL AP',
            'KROA':'ROANOKE INTL AP',
            'KRWI':'ROCKY MOUNT-WILSON REG AP',
            'KSBY':'SALISBURY-WICOMICO RGNL AP',
            'KSSC':'SHAW AFB AP',
            'KTCL':'TUSCALOOSA AL AP',
            'KTRI':'TRI-CITIES TN AP',
            'KTYS':'MCGHEE TYSON AP',
            'KVPC':'CARTERSVILLE AP',
            'KWRB':'WARNER-ROBINS AFP AP',
            'KWST':'WESTERLY STATE AP',
            'KWWD':'CAPE MAY COUNTY AP'}
#            '42002':'',
#            '42036':'',
#            '42039':'',
#            '42040':'',
#            '42395':''}

# go through sites in sitelist and get data
for site in sitelist.keys():

    print(site)
    
    sitetitle = sitelist[site]  # global attribute
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

    # Standaradize the format of all the ASOS csv files
    try:
        data = data[['air_temp_set_1','dew_point_temperature_set_1',
                     'dew_point_temperature_set_1d','precip_accumulated_set_1d',
                     'precip_intervals_set_1d','sea_level_pressure_set_1',
                     'sea_level_pressure_set_1d','wind_direction_set_1',
                     'wind_gust_set_1','wind_speed_set_1']]
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
            data[item] = [float('NaN') for x in np.arange(data.shape[0])] 
        #Standardizes the format
        data = data[['air_temp_set_1','dew_point_temperature_set_1','dew_point_temperature_set_1d',
                     'precip_accumulated_set_1d','precip_intervals_set_1d',
                     'sea_level_pressure_set_1','sea_level_pressure_set_1d',
                     'wind_direction_set_1','wind_gust_set_1','wind_speed_set_1']]

    # Eliminate any data for days other than start date
    data = data[date_dt_format]
    # Sort by date
    data = data.sort_index(axis=0)
    # Convert to csv
    data.to_csv(csvDir+'/ops.asos.'+date_str+'.'+lower_site+'.csv')

    # Convert to netcdf if flag is set
    if convertToCdf:
    
        '''
        #----------------------------------------------------------------------------------------------------------------
        # Use these lines if doing this as a separate step
        # read in csv file
        lower_site = 'kalx'
        data = pd.read_csv('/home/disk/funnel/impacts-website/data_archive/asos_csv/20200206/ops.asos.20200206.kalx.csv') 
        # Convert date_time strings to datetime objects
        data['time'] = pd.to_datetime(data['time'])
        # Set date_time as index
        data = data.set_index('time')
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

        # Create ncFile name
        ncFile = ncDir+'/'+ncPrefix+'_'+date_str+'_'+lower_site+'.nc'
        
        # Convert xarray to netcdf with all _FillValues set to missing_value
        encoding ={}
        for var in varDict.keys():
            if var != 'time':
                encoding[var] = {'_FillValue':missingValue}
        xr.to_netcdf(ncFile,encoding=encoding)
       

    
