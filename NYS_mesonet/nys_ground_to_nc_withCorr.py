#!/usr/bin/python

import os
import sys
import shutil
from datetime import datetime
from datetime import timedelta
import pandas as pd
import xarray
from netCDF4 import Dataset
import pickle

#inDirBase = '/home/disk/funnel/impacts-website/data_archive/nys_ground/csv_by_site_orig'
inDirBase = '/home/disk/funnel/impacts-website/data_archive/nys_ground/2020/csv_FIELD/csv_by_site'
#outDirCsvBase = '/home/disk/funnel/impacts-website/data_archive/nys_ground/csv_by_site_corr'
outDirCsvBase = '/home/disk/funnel/impacts-website/data_archive/nys_ground/2020/csv_QC_test'
#outDirNetcdfBase = '/home/disk/funnel/impacts-website/data_archive/nys_ground/netcdf_by_site'
outDirNetcdfBase = '/home/disk/funnel/impacts-website/data_archive/nys_ground/2020/netcdf_QC_test'
pickleDir = '/home/disk/bob/impacts/bin/pickle_jar'
pickleFile = 'nysm.pkl'
missingValue = -999
nc_prefix = 'IMPACTS_nys_ground'
missingValue = -999
varDict = {'time':{'units':'seconds','long_name':'seconds since 1970-01-01'},
           'temp_2m':{'units':'degC','long_name':'2 meter temperature'},
           'temp_9m':{'units':'degC','long_name':'9 meter temperature'},
           'rh':{'units':'%','long_name':'relative humidity'},
           'pres':{'units':'mb','long_name':'station pressure'},
           'ws_avg':{'units':'m/s','long_name':'average wind speed merge'},
           'ws_max':{'units':'m/s','long_name':'max wind speed merge'},
           'ws_stdev':{'units':'m/s','long_name':'wind speed stddev merge'},
           'wd':{'units':'deg','long_name':'wind direction merge'},
           'wd_stdev':{'units':'deg','long_name':'wind direction stddev merge'},
           'solar_ins':{'units':'W/m^2','long_name':'solar insolation'},
           'soil_temp_05cm':{'units':'degC','long_name':'soil temperature at 5 cm'},
           'soil_temp_25cm':{'units':'degC','long_name':'soil temperature at 25 cm'},
           'soil_temp_50cm':{'units':'degC','long_name':'soil temperature at 50 cm'},
           'soil_moist_05cm':{'units':'m^3/m^3','long_name':'soil moisture at 5 cm'},
           'soil_moist_25cm':{'units':'m^3/m^3','long_name':'soil moisture at 25 cm'},
           'soil_moist_50cm':{'units':'m^3/m^3','long_name':'soil moisture at 50 cm'},
           'precip_total':{'units':'mm','long_name':'daily total precip'},
           'precip_inc':{'units':'mm','long_name':'incremental precip'},
           'precip_max_rate':{'units':'mm/min','long_name':'precip max intensity'},
           'snow_depth':{'units':'cm','long_name':'snow depth'},
           'vpres':{'units':'mb','long_name':'vapor pressure'},
           'vpres_sat':{'units':'mb','long_name':'saturated vapor pressure'},
           'dp':{'units':'degC','long_name':'2 meter dewpoint temperature'} }

# Read site information from pickle
with open(pickleDir+'/'+pickleFile,'rb') as f:
    site_info = pickle.load(f)
site_info.set_index('stid',inplace=True)
site_info.rename(columns={'lat [degrees]':'lat', 'lon [degrees]':'lon'},inplace=True)

for site in os.listdir(inDirBase):

    # Get site info
    site_lat = site_info.at[site.upper(),'lat']
    site_lon = site_info.at[site.upper(),'lon']
    
    #if site == 'buff' and os.path.isdir(inDirBase+'/'+site):
    if os.path.isdir(inDirBase+'/'+site):
        inDir = inDirBase+'/'+site
        
        for file_today in os.listdir(inDir):
            if file_today.startswith('ops.nys_ground'):

                # Get date_today and site from file_today
                (category,type,date_today,site,suffix) = file_today.split('.')
                date_today_obj = datetime.strptime(date_today,'%Y%m%d')

                # Get date_tomorrow & file_tomorrow if it exists
                date_tomorrow = (date_today_obj+timedelta(hours=24)).strftime('%Y%m%d')
                file_tomorrow = file_today.replace(date_today,date_tomorrow)
                
                # Get first and last valid time
                # Time stamps refer to end of interval, so 00:00 tomorrow belongs to today
                first_valid_obj = datetime.strptime(date_today+' 0000','%Y%m%d %H%M')
                last_valid_obj = datetime.strptime(date_tomorrow+' 0000','%Y%m%d %H%M')

                # Read file_today convert time to datetime and make it the df index
                df_today = pd.read_csv(inDir+'/'+file_today)
                # Convert 'datetime' values to datetimes
                df_today['datetime'] = pd.to_datetime(df_today['datetime'])
                # Set 'datetime' as index
                df_today.set_index('datetime',inplace=True)
                # Get subset of times after first_valid time
                df_today_valid = df_today.loc[df_today.index > first_valid_obj]
                # Reset index
                df_today_valid = df_today_valid.reset_index()
                
                # Get tomorrow info
                if file_tomorrow in os.listdir(inDir):
                    # Read file_tomorrow convert time to datetime and make it the df index
                    df_tomorrow = pd.read_csv(inDir+'/'+file_tomorrow)
                    # Convert 'datetime' values to datetimes
                    df_tomorrow['datetime'] = pd.to_datetime(df_tomorrow['datetime'])
                    # Set 'datetime' as index
                    df_tomorrow.set_index('datetime',inplace=True)
                    # Get subset of times before last_valid time
                    df_tomorrow_valid = df_tomorrow.loc[df_tomorrow.index <= last_valid_obj]
                    # Reset index
                    df_tomorrow_valid = df_tomorrow_valid.reset_index()
                else:
                    df_tomorrow_valid = pd.DataFrame(columns = df_today_valid.keys())
                    
                # concatenate two DataFrame objects into one
                frames = [df_today_valid, df_tomorrow_valid]
                df = pd.concat(frames)

                # remove duplicate rows
                df = df.drop_duplicates(keep='last')
                
                # Save df as new csv file
                df.set_index('datetime',inplace=True)
                outDirCsv = outDirCsvBase+'/'+site
                if not os.path.exists(outDirCsv):
                    os.makedirs(outDirCsv)
                outFileCsv = outDirCsv+'/'+file_today
                # NOTE: values are not rounded in new file - WHY??
                df.to_csv(path_or_buf=outFileCsv,index_label='datetime')

                # Save site and site elevation to use as global attributes
                df = df.reset_index()
                station_short = df.loc[0].at['station']
                station_long = df.loc[0].at['name']
                station_elev = df.loc[0].at['station_elevation [m]']

                # Remove extra columns (station and time) and repeated (station_elevation and name) columns
                df = df.drop('station',axis=1)
                df = df.drop('time',axis=1)
                df = df.drop('station_elevation [m]',axis=1)
                df = df.drop('name',axis=1)

                # Convert times from yyyy-mm-dd hh:mm:ss UTC' to seconds since 01-01-1970
                df['datetime'] = df['datetime'].map(lambda time: int( (time - datetime(1970,1,1)).total_seconds() ) )
                
                # Create column headings
                df.columns = ['time','temp_2m','temp_9m','rh','pres','ws_avg','ws_max','ws_stdev','wd',
                              'wd_stdev','solar_ins','soil_temp_05cm','soil_temp_25cm','soil_temp_50cm',
                              'soil_moist_05cm','soil_moist_25cm','soil_moist_50cm','precip_total',
                              'precip_inc','precip_max_rate','snow_depth','vpres','vpres_sat','dp']

                # For all vars except 'time' handle missing values
                for key in df.keys():
                    # if missing values in data, have to replace with NaNs and then convet to numeric
                    # as it originaly is read strings instead of float64; coerce flag nicely takes
                    # anything that cannot be converted and puts NaN
                    if df[key].dtype.name != 'float64' and df[key].dtype.name != 'int64':
                        df[key] = pd.to_numeric(df[key], errors='coerce')

                # Create xarray and assign var attributes
                df.set_index('time',inplace=True)
                xr = xarray.Dataset.from_dataframe(df)
                for var in varDict.keys():
                    xr[var].attrs=varDict[var]
                    
                # Create dictionary of global attributes and add to xarray
                globalAttDict = {'site_name_long':station_long,
                                 'site_name_abbr':station_short,
                                 'site_latitude':site_lat,
                                 'site_longitude':site_lon,
                                 'site_elevation':station_elev,
                                 'reference':'http://www.nysmesonet.org/networks/standard'}
                xr.attrs = globalAttDict

                # Create ncFile name
                outDirNetcdf = outDirNetcdfBase+'/'+site
                if not os.path.exists(outDirNetcdf):
                    os.makedirs(outDirNetcdf)
                ncFile = outDirNetcdf+'/'+nc_prefix+'_'+date_today+'_'+site+'.nc'
        
                # Convert xarray to netcdf with all _FillValues set to missing_value
                encoding ={}
                for var in varDict.keys():
                    if var != 'time':
                        encoding[var] = {'_FillValue':missingValue}
                xr.to_netcdf(ncFile,encoding=encoding)
       
