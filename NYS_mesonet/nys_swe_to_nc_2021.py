#!/usr/bin/python3

import os
import sys
import shutil
from datetime import datetime
from datetime import timedelta
import pandas as pd
import xarray
from netCDF4 import Dataset

inDirBase = '/home/disk/bob/impacts/raw/nys_swe_2021/csv_by_site'
outDirBase = '/home/disk/bob/impacts/raw/nys_swe_2021/netcdf_by_site'
missingValue = -999
nc_prefix = 'IMPACTS_nys_swe'
missingValue = -999
siteInfo = '/home/disk/bob/impacts/bin/pickle_jar/nysm_swe_2021.pkl'
varDict = {'time':{'units':'seconds since 1970-01-01','long_name':'observation time'},
           'int_end_time':{'units':'seconds since 1970-01-01','long_name':'time at end of interval'},
           'K_counts_uncorr':{'units':'none','long_name':'potassium (K) counts total (uncorrected)'},
           'K_counts_corr':{'units':'none','long_name':'potassium (K) counts total (corrected - used in SWE calcs'},
           'Tl_counts_corr':{'units':'none','long_name':'thallium (Tl) counts total (corrected - used in SWE calcs'},
           'swe_K':{'units':'mm','long_name':'swe generated from potassium (K)'},
           'ratio_K_Tl':{'units':'mm','long_name':'ratio generated from K and Tl'},
           'swe_Tl':{'units':'mm','long_name':'swe generated from thallium (Tl)'},
           'sm_K':{'units':'Gravimetric Soil Moisture in %','long_name':'soil moisture values generated from K'},
           'sm_Tl':{'units':'Gravimetric Soil Moisture in %','long_name':'soil moisture values generated from Tl'},
           'sm_K_Tl':{'units':'Gravimetric Soil Moisture in %','long_name':'soil moisture values generated from K and Tl'},
           'crystal_temp_min':{'units':'degC','long_name':'crystal temperature min'},
           'crystal_temp_max':{'units':'degC','long_name':'crystal temperature max'},
           'hist_blocks':{'units':'none','long_name':'total number of histogram blocks used for the analysis'},
           'K_disp':{'units':'bins','long_name':'displacement of the K peak from its nominal position'},
           'stats':{'units':'','long_name':'statistical significance of the swe Tl measurement'},
           'pwr_volt':{'units':'','long_name':'power input voltage at the CS725 after protection diode drop'} }

# Read station lat/lon/alt
site_info = pd.read_pickle(siteInfo)
site_info = site_info.set_index('stid')

for site in os.listdir(inDirBase):
    if os.path.isdir(inDirBase+'/'+site):
        
        inDir = inDirBase+'/'+site
        
        for file in os.listdir(inDir):
            if file.startswith('ops.nys_swe'):
                
                print(file)
                
                # Get date from filename
                (category,type,date,site_extra,suffix) = file.split('.')
                #date_obj = datetime.strptime(date,'%Y%m%d')

                # Read file into datetime
                df = pd.read_csv(inDir+'/'+file)
                
                # Convert 'datetime' values to datetimes
                df['datetime'] = pd.to_datetime(df['datetime'])
                df['int_end_time'] = pd.to_datetime(df['int_end_time'])
                
                # Save a few things to use as global attributes
                station_short = df.loc[0].at['stid']
                serial_number = df.loc[0].at['serialNum']
                network = df.loc[0].at['network']
                
                # Get station lat/lon/elev and long name from site_info
                station_lat = site_info.at['SNOW_'+site.upper(),'lat [degrees]']
                station_lon = site_info.at['SNOW_'+site.upper(),'lon [degrees]']
                station_elev = site_info.at['SNOW_'+site.upper(),'elevation [m]']
                station_long = site_info.at['SNOW_'+site.upper(),'name']

                # Remove extra columns (station, time, etc) and repeated (station_elevation and name) columns
                df = df.drop('stid',axis=1)
                df = df.drop('fname',axis=1)
                df = df.drop('time',axis=1)
                df = df.drop('recNum',axis=1)
                df = df.drop('network',axis=1)
                df = df.drop('serialNum',axis=1)
                df = df.drop('precip_index',axis=1)

                # Convert times from yyyy-mm-dd hh:mm:ss UTC' to seconds since 01-01-1970
                df['datetime'] = df['datetime'].map(lambda time: int( (time - datetime(1970,1,1)).total_seconds() ) )
                df['int_end_time'] = df['int_end_time'].map(lambda time: int( (time - datetime(1970,1,1)).total_seconds() ) )
                
                # Create column headings
                df.columns = ['time','int_end_time','K_counts_uncorr','K_counts_corr','Tl_counts_corr','swe_K',
                              'ratio_K_Tl','swe_Tl','sm_K','sm_Tl',
                              'sm_K_Tl','crystal_temp_min','crystal_temp_max','hist_blocks',
                              'K_disp','stats','pwr_volt']
                
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
                # Add serial number, 
                globalAttDict = {'site_name_long':station_long,
                                 'site_name_abbr':site,
                                 'site_latitude':station_lat,
                                 'site_longitude':station_lon,
                                 'site_elevation':station_elev,
                                 'serial_number':serial_number,
                                 'network':network,
                                 'comment1':'Data has not been quality controlled',
                                 'comment2':'NYSM recommends using swe_K for swe value',
                                 'reference':'https://www2.nysmesonet.org/networks/snow'}
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
       
