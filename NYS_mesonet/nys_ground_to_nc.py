#!/usr/bin/python

import os
import sys
import shutil
from datetime import datetime
from datetime import timedelta
import pandas as pd
import xarray
from netCDF4 import Dataset

inDirBase = '/home/disk/funnel/impacts-website/data_archive/nys_ground_TEST/csv_by_site'
outDirBase = '/home/disk/funnel/impacts-website/data_archive/nys_ground_TEST/netcdf_by_site'
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

for site in os.listdir(inDirBase):
    #if site == 'buff' and os.path.isdir(inDirBase+'/'+site):
    if os.path.isdir(inDirBase+'/'+site):
        inDir = inDirBase+'/'+site
        
        for file in os.listdir(inDir):
            if file.startswith('ops.nys_ground'):

                # Get date from filename
                (category,type,date,site_extra,suffix) = file.split('.')
                #date_obj = datetime.strptime(date,'%Y%m%d')

                # Read file convert time to datetime
                df = pd.read_csv(inDir+'/'+file)
                # Convert 'datetime' values to datetimes
                df['datetime'] = pd.to_datetime(df['datetime'])
                
                # Save site and site elevation to use as global attributes
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

                # Set snow_depths less than 0.0 to 0.0
                df['snow_depth'] = df['snow_depth'].mask(df['snow_depth'] < 0, 0.0)
                
                # For all vars except 'time' handle missing values
                for key in df.keys():
                    # if missing values in data, have to replace with NaNs and then convert to numeric
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
                                 'site_name_abbr':site,
                                 'site_elevation':station_elev,
                                 'reference':'http://www.nysmesonet.org/networks/standard'}
                xr.attrs = globalAttDict

                # Create ncFile name
                outDir = outDirBase+'/'+site
                if not os.path.exists(outDir):
                    os.makedirs(outDir)
                ncFile = outDir+'/'+nc_prefix+'_'+date+'_'+site+'.nc'
        
                # Convert xarray to netcdf with all _FillValues set to missing_value
                encoding ={}
                for var in varDict.keys():
                    if var != 'time':
                        encoding[var] = {'_FillValue':missingValue}
                xr.to_netcdf(ncFile,encoding=encoding)
       
