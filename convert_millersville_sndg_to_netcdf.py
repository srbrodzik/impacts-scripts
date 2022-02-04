#!/usr/bin/python3

import os
import sys
import shutil
from datetime import datetime
from datetime import timedelta
import pandas as pd
import xarray
from netCDF4 import Dataset

def convertTime(t):
    x = time.strptime(t,'%H:%M:%S')
    return str(int(datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds()))

print('len(sys.argv) = ',len(sys.argv))

if len(sys.argv) != 4:
    print('Useage: ',sys.argv[0],' [inDir] [inFile] [outDir]')
    sys.exit()
else:
    inDir = sys.argv[1]
    file = sys.argv[2]
    outDir = sys.argv[3]

#inDirBase = '/home/disk/funnel/impacts-website/archive/missions'
#inDirBase = '/home/disk/meso-home/brodzik/impacts/Data/soundings/Millersville'
#outDirBase = '/home/disk/funnel/impacts-website/data_archive/flight_tracks'
#outDirBase = '/home/disk/meso-home/brodzik/impacts/Data/soundings/Millersville'
missingValue = -9999.
nc_prefix = 'upperair.UMILL_sonde'
nc_suffix = 'skewT'
lines_in_header = 13
varDict = {'time_offset':{'units':'seconds','long_name':'seconds since release time'},
           'time':{'units':'seconds','long_name':'seconds since midnight'},
           'geometric_height':{'units':'meters','long_name':'height above the ground'},
           'temperature':{'units':'degrees C','long_name':'temperature'},
           'dewpoint_temperature':{'units':'degrees C','long_name':'dewpoint temperature'},
           'mixing_ratio':{'units':'g/kg','long_name':'mixing ratio'},
           'relative_humidity':{'units':'%','long_name':'relative humidity'},
           'virtual_temperature':{'units':'degrees C','long_name':'virtual temperature'},
           'pressure':{'units':'hPa','long_name':'pressure'},
           'wind_direction':{'units':'degrees from north','long_name':'wind direction'},
           'wind_speed':{'units':'m/s','long_name':'wind speed'},
           'ucomp_wind':{'units':'m/s','long_name':'east componenet of wind'},
           'vcomp_wind':{'units':'m/s','long_name':'north component of wind'},
           'ascent_rate':{'units':'m/s','long_name':'ascent rate'},
           'latitude':{'units':'degrees','long_name':'latitude'},
           'longitude':{'units':'degrees','long_name':'longitude'} }
globalAttrDict = {}
          
# Read in csv file header
with open(inDir+'/'+file,encoding='unicode_escape') as f:
    header = f.readlines()[0:lines_in_header]

    for i in range(1,len(header)-1):
        line = header[i].strip()
        (param,value) = line.split('\t')
        param = param.strip()
        param = param.replace(' ','_')
        if param == 'Balloon_release_date_and_time':
            param = 'ReleaseTime'
            datetimeObj = datetime.strptime(value,"%Y-%m-%dT%H:%M:%S")
            value = datetimeObj.strftime("%Y/%m/%d %H:%M:%S")
        elif param == 'Release_point_latitude':
            param = 'SiteLocation_Latitude'
            if 'N' in value:
                value = value[0:len(value)-2]+' N'
            else:
                value = '-'+value[0:len(value)-2]+' N'
        elif param == 'Release_point_longitude':
            param = 'SiteLocation_Longitude'
            if 'E' in value:
                value = value[0:len(value)-2]+' E'
            else:
                value = '-'+value[0:len(value)-2]+' E'
        elif param == 'Release_point_height_from_sea_level':
            param = 'SiteLocation_Altitude'
        globalAttrDict[param] = value
    #print(globalAttrDict)
                        
    # Read in csv data after header as Datafreme object
    df = pd.read_csv(inDir+'/'+file,skiprows=lines_in_header,delimiter='\s+',
                     #index_col=1,
                     #converters={'time': hh_mm_ss2seconds},
                     encoding="latin1")
    # Remove last column which is created due to space in 'Elapsed Time'
    df.drop(columns=df.columns[-1],axis=1,inplace=True)
    # Remove units row
    df.drop(df.index[0],inplace=True)
    # Create column headings
    df.columns = ['n','time_offset','time','geometric_height','temperature',
                  'dewpoint_temperature','mixing_ratio','relative_humidity',
                  'virtual_temperature','pressure','wind_direction',
                  'wind_speed','ucomp_wind','vcomp_wind','ascent_rate',
                  'latitude','longitude']
    # Remove index column
    df = df.drop('n',axis=1)
                
    # Convert time from yyyy-mm-ddThh:mm:ss.ssssss' to seconds since midnight
    df['dt'] = pd.to_datetime(df['time']).dt.time
    df['seconds'] = df['dt'].map(lambda dt:int(timedelta(hours=dt.hour, minutes=dt.minute, seconds=dt.second).total_seconds()))
    #df['seconds'] = df['time'].apply(convertTime)
    df.drop(['dt'],axis=1,inplace=True)
                
    # Replace time values with seconds values and remove seconds column
    df['time'] = df['seconds']
    df.drop(['seconds'],axis=1,inplace=True)

    # Set time as index
    df.set_index('time',inplace=True)
                    
    # For all vars except 'time_offset' handle missing values
    for key in df.keys():
        # if missing values in data, have to replace with NaNs and then convet to numeric
        # as it originaly is read strings instead of float64; coerce flag nicely takes
        # anything that cannot be converted and puts NaN
        if df[key].dtype.name != 'float64' and df[key].dtype.name != 'int64':
            df[key] = pd.to_numeric(df[key], errors='coerce')

    # Create xarray and assign var and global attributes
    xr = xarray.Dataset.from_dataframe(df)
    for var in varDict.keys():
        xr[var].attrs=varDict[var]
    for attr in globalAttrDict.keys():
        xr.attrs[attr]=globalAttrDict[attr]

    # Create ncFile name
    if not os.path.exists(outDir):
        os.makedirs(outDir)
    # if fname = impactsdata_YYYYMMDD_hhmm.txt
    #(base,ext) = os.path.splitext(file)
    #(junk,date,time) = base.split('_')
    # if fname = upperair.UMILL_sonde.YYYYMMDDhhmm.txt
    (base,ext) = os.path.splitext(file)
    (junk1,junk2,datetime) = base.split('.')    
    ncFile = outDir+'/'+nc_prefix+'.'+datetime+'.nc'
        
    # Convert xarray to netcdf with all _FillValues set to missing_value
    encoding ={}
    for var in varDict.keys():
        if var != 'time' and var != 'time_offset':
            encoding[var] = {'_FillValue':missingValue}
    xr.to_netcdf(ncFile,encoding=encoding)
                
