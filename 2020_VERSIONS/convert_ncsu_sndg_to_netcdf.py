#!/usr/bin/python

# File naming convention for NWS sounding netcdf files:
# IMPACTS_sounding_<start date>_<start time>_<site name>.nc

import os
import sys
import shutil
from datetime import datetime
import pandas as pd
import xarray
from netCDF4 import Dataset

#inDirBase = '/home/snowband/impacts/Downloads/sounding/NCSU'
inDirBase = '/home/disk/funnel/impacts-website/archive/research/text_sounding'
#outDirBase = inDirBase
outDirBase = '/home/disk/funnel/impacts-website/data_archive/soundings/impacts'
missing_value = -999
nc_prefix = 'IMPACTS_sounding'

for date in os.listdir(inDirBase):
    if os.path.isdir(inDirBase+'/'+date):
        inDir = inDirBase+'/'+date
        outDir = outDirBase+'/'+date
        if not os.path.exists(outDir):
            os.makedirs(outDir)
            shutil.copy(outDirBase+'/index.php',outDir)
        
        for file in os.listdir(inDir):
            if file.endswith('csv'):

                print >>sys.stdout, 'Input file = ', file
        
                # Read in csv file
                with open(inDir+'/'+file,'r') as f:

                    # read and parse header info
                    header = f.readline()
                    header = header.rstrip()
                    
                    latStrBegin = header.find('lat=', 0)
                    latValEnd = header.find(',', latStrBegin)
                    latVal = float(header[latStrBegin+len('lat='):latValEnd])

                    lonStrBegin = header.find('lon=', 0)
                    lonValEnd = header.find(',', lonStrBegin)
                    lonVal = float(header[lonStrBegin+len('lon='):lonValEnd])
                    
                    timeStrBegin = header.find('utc_time=')
                    datetimeStr = header[timeStrBegin+len('utc_time='):]

                    # convert datetime to DateTime object
                    datetimeObj = datetime.strptime(datetimeStr,"%Y-%m-%d %H:%M")
                    date = datetimeObj.strftime("%Y%m%d")
                    time = datetimeObj.strftime("%H%M%S")

                # read in file after header as DataFrame
                df = pd.read_csv(inDir+'/'+file,skiprows=1)
                #origKeys = df.keys()
                df = df.rename(columns={df.keys()[0]:'ht',
                                        df.keys()[1]:'pres',
                                        df.keys()[2]:'temp',
                                        df.keys()[3]:'rh',
                                        df.keys()[4]:'wspd',
                                        df.keys()[5]:'wdir'})
                                   
                for key in df.keys():
	            # if missing values in data, have to replace with NaNs and then convet to numeric as it
                    # originaly is read strings instead of float64; coerce flag nicely takes anything that
                    # cannot be converted and puts NaN
                    if df[key].dtype.name != 'float64' and df[key].dtype.name != 'int64':
                        df[key] = pd.to_numeric(df[key], errors='coerce')
                    
                # Create xarray and assign var and global attributes
                xr = xarray.Dataset.from_dataframe(df)
                xr['ht'].attrs={'units':'m AGL', 'long_name':'height'}
                xr['pres'].attrs={'units':'mb', 'long_name':'pressure'}
                xr['temp'].attrs={'units':'degC', 'long_name':'temperature'}
                xr['rh'].attrs={'units':'%', 'long_name':'relative_humidity'}
                xr['wspd'].attrs={'units':'m/s', 'long_name':'wind_speed'}
                xr['wdir'].attrs={'units':'deg', 'long_name':'wind_direction'}
                #xr.attrs = attributes

                # Create ncFile name
                (base,junk1,ext) = file.split('.')
                (site,date,time) = base.split('_')
                (year,month,day) = date.split('-')
                ncFile = outDir+'/'+nc_prefix+'_'+year+month+day+'_'+time+'_'+site+'.nc'
        
                # Convert xarray to netcdf
                encoding = {
                    'ht': {'_FillValue':missing_value},
                    'pres': {'_FillValue':missing_value},
                    'temp': {'_FillValue':missing_value},
                    'rh': {'_FillValue':missing_value},
                    'wspd': {'_FillValue':missing_value},
                    'wdir': {'_FillValue':missing_value}
                }
                xr.to_netcdf(ncFile,encoding=encoding)
