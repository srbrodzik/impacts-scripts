#!/usr/bin/python3

import os
import sys
import shutil
from datetime import datetime
from datetime import timedelta
import pandas as pd
import xarray
from netCDF4 import Dataset

inDirBase = '/home/disk/bob/impacts/raw/nys_ground_2021/csv_by_site'
outDirBase = '/home/disk/bob/impacts/raw/nys_ground_2021/netcdf_by_site'
missingValue = -999
nc_prefix = 'IMPACTS_nys_ground'
missingValue = -999
siteInfo = '/home/disk/bob/impacts/bin/pickle_jar/nysm_2021.pkl'
varDict = {'time':{'units':'seconds','long_name':'seconds since 1970-01-01'},
           'temp_2m':{'units':'degC','long_name':'2 meter temperature'},
           'temp_9m':{'units':'degC','long_name':'9 meter temperature'},
           'rh':{'units':'%','long_name':'relative humidity'},
           'precip_inc':{'units':'mm','long_name':'incremental precip'},
           'precip_total':{'units':'mm','long_name':'daily total precip'},
           'precip_max_rate':{'units':'mm/min','long_name':'precip max intensity'},
           'ws_avg_prop':{'units':'m/s','long_name':'average wind speed from wind monitor'},
           'ws_max_prop':{'units':'m/s','long_name':'max wind speed from wind monitor'},
           'ws_stdev_prop':{'units':'m/s','long_name':'wind speed stddev from wind monitor'},
           'wd_prop':{'units':'deg','long_name':'wind direction from wind monitor'},
           'wd_stdev_prop':{'units':'deg','long_name':'wind direction stddev from wind monitor'},
           'ws_avg_sonic':{'units':'m/s','long_name':'average wind speed from sonic anemometer'},
           'ws_max_sonic':{'units':'m/s','long_name':'max wind speed from sonic anemometer'},
           'ws_stdev_sonic':{'units':'m/s','long_name':'wind speed stddev from sonic anemometer'},
           'wd_sonic':{'units':'deg','long_name':'wind direction from sonic anemometer'},
           'wd_stdev_sonic':{'units':'deg','long_name':'wind direction stddev from sonic anemometer'},
           'solar_ins':{'units':'W/m^2','long_name':'solar insolation'},
           'pres':{'units':'mb','long_name':'station pressure'},
           'snow_depth':{'units':'cm','long_name':'snow depth'},
           'soil_temp_05cm':{'units':'degC','long_name':'soil temperature at 5 cm'},
           'soil_temp_25cm':{'units':'degC','long_name':'soil temperature at 25 cm'},
           'soil_temp_50cm':{'units':'degC','long_name':'soil temperature at 50 cm'},
           'soil_moist_05cm':{'units':'m^3/m^3','long_name':'soil moisture at 5 cm'},
           'soil_moist_25cm':{'units':'m^3/m^3','long_name':'soil moisture at 25 cm'},
           'soil_moist_50cm':{'units':'m^3/m^3','long_name':'soil moisture at 50 cm'},
           'vpres':{'units':'mb','long_name':'vapor pressure'},
           'vpres_sat':{'units':'mb','long_name':'saturated vapor pressure'},
           'dp':{'units':'degC','long_name':'2 meter dewpoint temperature'} }

# Read station lat/lon/alt
site_info = pd.read_pickle(siteInfo)
site_info = site_info.set_index('stid')

for site in os.listdir(inDirBase):
    #if site == 'buff' and os.path.isdir(inDirBase+'/'+site):
    if os.path.isdir(inDirBase+'/'+site):
        
        inDir = inDirBase+'/'+site
        
        for file in os.listdir(inDir):
            if file.startswith('ops.nys_ground'):
                
                print(file)
                
                # Get date from filename
                (category,type,date,site_extra,suffix) = file.split('.')
                #date_obj = datetime.strptime(date,'%Y%m%d')

                # Read file into datetime
                df = pd.read_csv(inDir+'/'+file)
                
                # Convert 'datetime' values to datetimes
                df['datetime'] = pd.to_datetime(df['datetime'])
                
                # Save station short name to use as global attribute
                station_short = df.loc[0].at['station']

                # Get station lat/lon/elev and long name from site_info
                station_lat = site_info.at[site.upper(),'lat [degrees]']
                station_lon = site_info.at[site.upper(),'lon [degrees]']
                station_elev = site_info.at[site.upper(),'elevation [m]']
                station_long = site_info.at[site.upper(),'name']

                # Remove extra columns (station, time, etc) and repeated (station_elevation and name) columns
                df = df.drop('station',axis=1)
                df = df.drop('time',axis=1)
                df = df.drop('frozen_soil_05cm [bit]',axis=1)
                df = df.drop('frozen_soil_25cm [bit]',axis=1)
                df = df.drop('frozen_soil_50cm [bit]',axis=1)

                # Convert times from yyyy-mm-dd hh:mm:ss UTC' to seconds since 01-01-1970
                df['datetime'] = df['datetime'].map(lambda time: int( (time - datetime(1970,1,1)).total_seconds() ) )
                
                # Create column headings
                df.columns = ['time','temp_2m','temp_9m','rh','precip_inc','precip_total',
                              'precip_max_rate','ws_avg_prop','ws_max_prop','ws_stdev_prop',
                              'wd_prop','wd_stdev_prop','ws_avg_sonic','ws_max_sonic',
                              'ws_stdev_sonic','wd_sonic','wd_stdev_sonic','solar_ins',
                              'pres','snow_depth','soil_temp_05cm','soil_temp_25cm',
                              'soil_temp_50cm','soil_moist_05cm','soil_moist_25cm',
                              'soil_moist_50cm','vpres','vpres_sat','dp']

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
                                 'site_latitude':station_lat,
                                 'site_longitude':station_lon,
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
       
