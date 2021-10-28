#!/usr/bin/python3

import os 
import pandas as pd 
import xarray
import time, datetime
from datetime import datetime
import pickle

prefix = 'IMPACTS_ASOS'
missingValue = -999.

csvBaseDir = '/home/disk/funnel/impacts-website/data_archive/asos_isu'
ncBaseDir = '/home/disk/funnel/impacts-website/data_archive/asos_isu_nc'

varDict = {'time':{'units':'seconds', 'long_name':'seconds since 1970-01-01'},
           'tmpc':{'units':'degC' ,'long_name':'temperature' },
           'dwpc':{'units':'degC' ,'long_name':'dewpoint temperature' },
           'drct':{'units':'deg' ,'long_name':'wind direction' },
           'sknt':{'units':'kts' ,'long_name':'wind speed' },
           'gust':{'units':'kts' ,'long_name':'wind gust' },
           'mslp':{'units':'mb' ,'long_name':'sea level pressure' },
           'p01m':{'units':'mm' ,'long_name':'precip for last time interval(hour)' },
           'wxcodes':{'units':'none' ,'long_name':'current weather codes' }}

# Get site information
pickle_jar = '/home/disk/bob/impacts/bin/pickle_jar/'
infile = open(pickle_jar + "sitelist.pkl",'rb')
sitelist = pickle.load(infile)
infile.close()

# Get sitetitles
infile2 = open(pickle_jar + 'sitetitles.pkl','rb')
sitetitles = pickle.load(infile2)
infile.close()

# dates of interest
date_strs = ['20191229','20191230','20191231',
             '20200101','20200102','20200103','20200104','20200105',
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

for date in date_strs:

    for isite,site in enumerate(sitelist):

        print(date,site)

        # read in csv file
        if os.path.exists(csvBaseDir+'/'+date+'/'+prefix+'_'+date+'_'+site.lower()+'.csv'):
            data = pd.read_csv(csvBaseDir+'/'+date+'/'+prefix+'_'+date+'_'+site.lower()+'.csv')
            if len(data) != 0:
                # Rename 'date_time' as 'time'
                data.rename(columns={'date_time':'time'},inplace=True)
                # Convert date_time strings to datetime objects
                data['time'] = pd.to_datetime(data['time'])
                # Set date_time as index
                data = data.set_index('time')

                # Convert 'times' to seconds since 1970-01-01
                data.index = data.index.map(lambda time: int( (time - datetime(1970,1,1)).total_seconds() ) )

                # For all vars except 'wxcodes' handle missing values
                for key in data.keys():
                    # if missing values in data, have to replace with NaNs and then convet to numeric
                    # as it originaly is read strings instead of float64; coerce flag nicely takes
                    # anything that cannot be converted and puts NaN
                    if key != 'wxcodes':
                        if data[key].dtype.name != 'float64' and data[key].dtype.name != 'int64':
                            data[key] = pd.to_numeric(data[key], errors='coerce')

                # Create xarray and assign var and global attributes
                xr = xarray.Dataset.from_dataframe(data)
                for var in varDict.keys():
                    xr[var].attrs=varDict[var]
                #xr.attrs['weather_code_reference'] = 'https://developers.synopticdata.com/about/weather-condition-codes'
                xr.attrs['site_location'] = sitetitles[isite]
                xr.attrs['weather_code_reference'] = 'See Weather Codes in https://www.unidata.ucar.edu/software/gempak/man/parm/apxA.html'

                # Create ncFile name
                ncDir = ncBaseDir+'/'+date
                if not os.path.exists(ncDir):
                    os.makedirs(ncDir)
                ncFile = ncDir+'/'+prefix+'_'+date+'_'+site.lower()+'.nc'
        
                # Convert xarray to netcdf with all _FillValues set to missing_value
                encoding ={}
                for var in varDict.keys():
                    if var != 'wxcodes':
                        encoding[var] = {'_FillValue':missingValue}
                xr.to_netcdf(ncFile,encoding=encoding)
       

    
