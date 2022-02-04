#!/usr/bin/python3

import os
import xarray
import pandas as pd
import glob
import numpy as np
from datetime import datetime
from datetime import timedelta

ldmDirBase = '/home/disk/data/albany/standard'
siteNcDirBase = '/home/disk/bob/impacts/raw/nys_ground_2022'
ncPrefix = 'nysm_standard'
missingValue = -996.
# get dates for today and yesterday
current_dt = datetime.utcnow()
current_date_str = datetime.strftime(current_dt,'%Y%m%d')
current_hour_str = datetime.strftime(current_dt,'%H')
current_date_obj = datetime.strptime(current_date_str,'%Y%m%d')
yesterday_date_obj = current_date_obj - timedelta(hours=24)
yesterday_date_str = datetime.strftime(yesterday_date_obj,'%Y%m%d')
if current_hour_str == '00':
    date_list = [yesterday_date_str,current_date_str]
else:
    date_list = [current_date_str]
#date_list = ['20220119']

for date in date_list:

    # read nc file into dataframe & save attribute info
    ldmDir = ldmDirBase
    ncFile = glob.glob(ldmDir+'/*'+date+'*.nc')[0]
    #ncFile = ldmDir+'/2358-netcdf.proc.20220106.nc'
    print('ncFile = ',ncFile)
    ds = xarray.open_dataset(ncFile)
    # save attributes in dict
    globalAttrDict = ds.attrs 
    # ADD SITE LONG/SHORT NAMES AND LAT/LON/ALT TO GLOBAL ATTS
    varAttrDict = {'time_5M':{'units':'seconds','long_name':'seconds since 1970-01-01 00:00:00'}}
    for var in ds.data_vars.keys():
        #print(var)        
        dict = ds[var].attrs
        varAttrDict[var] = dict
    df = ds.to_dataframe()

    # get site list from file
    site_list = []
    for ind in df.index.values:
        site_list.append(ind[0])
    site_list = list(set(site_list))

    # create netcdf files by site
    for site in site_list:
        #print(site)
        df_site = df.loc[site]

        # Convert times from yyyy-mm-ddThh:mm:ss.ssssss' to seconds since 01-01-1970
        df_site.reset_index(inplace=True)
        # getting warnings on next two lines
        # A value is trying to be set on a copy of a slice from a DataFrame.
        # Try using .loc[row_indexer,col_indexer] = value instead
        df_site['time_5M'] = pd.to_datetime(df_site['time_5M'])
        df_site['time_5M'] = df_site['time_5M'].map(lambda time: int( (time - datetime(1970,1,1)).total_seconds() ) )
        df_site.set_index('time_5M',inplace=True)

        # convert to xarray
        xr = xarray.Dataset.from_dataframe(df_site)
        for var in varAttrDict.keys():
            xr[var].attrs = varAttrDict[var]
        for attr in globalAttrDict.keys():
            xr.attrs[attr] = globalAttrDict[attr]

        # convert to netcdf
        siteNcDir = siteNcDirBase+'/'+date
        if not os.path.exists(siteNcDir):
            os.makedirs(siteNcDir)
        ncFile = siteNcDir+'/'+ncPrefix+'.'+date+'.'+site.lower()+'.nc'

        encoding = {}
        for var in varAttrDict.keys():
            #print('var =',var)
            if var != 'time_5M':
                encoding[var] = {'_FillValue':missingValue}
        xr.to_netcdf(ncFile,encoding=encoding)
        
            

        
