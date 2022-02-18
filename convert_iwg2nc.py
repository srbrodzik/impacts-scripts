#!/usr/bin/python

import os
import sys
import shutil
from datetime import datetime
import pandas as pd
import xarray
from netCDF4 import Dataset

if len(sys.argv) != 2:
    print('Useage: {} <date YYYYMMDD)>'.format(sys.argv[0]))
    sys.exit()
else:
    date = sys.argv[1]

if len(date) != 8:
    print('Date must be in YYYYMMDD format. Input date =',date,'is not')
    sys.exit()

#inDirBase = '/home/disk/bob/impacts/raw/aircraft/csv'
inDirBase = '/home/disk/funnel/impacts-website/data_archive/flight_tracks_field'
#outDirBase = '/home/disk/bob/impacts/raw/aircraft/netcdf'
outDirBase = '/home/disk/funnel/impacts-website/data_archive/flight_tracks_field'
missingValue = -999
nc_prefix = 'IMPACTS_flight_track'
planes = ['er2','p3']
missingValue = -999
varDict = {'time':{'units':'seconds','long_name':'seconds since 1970-01-01'},
           'lat':{'units':'degN','long_name':'latitude'},
           'lon':{'units':'degE','long_name':'longitude'},
           'gps_msl_alt':{'units':'m','long_name':'GPS altitude, mean sea level'},
           'wgs84_alt':{'units':'m','long_name':'WGS 84 geoid altitude'},
           'pres_alt':{'units':'ft','long_name':'pressure altitude'},
           'radar_alt':{'units':'ft','long_name':'radar altimeter altitude'},
           'grnd_spd':{'units':'m/s','long_name':'ground speed'},
           'true_airspd':{'units':'m/s','long_name':'true airspeed'},
           'ind_airspd':{'units':'knots','long_name':'indicated airspeed'},
           'mach':{'units':'none','long_name':'aircraft mach number'},
           'vert_vel':{'units':'m/s','long_name':'aircraft vertical velocity'},
           'true_hdg':{'units':'deg','long_name':'true heading'},
           'track':{'units':'deg','long_name':'track angle'},
           'drift':{'units':'deg','long_name':'drift angle'},
           'pitch':{'units':'deg','long_name':'pitch angle'},
           'roll':{'units':'deg','long_name':'roll angle'},
           'side_slip':{'units':'deg','long_name':'side slip angle'},
           'ang_of_attack':{'units':'deg','long_name':'angle of attack'},
           'amb_temp':{'units':'degC','long_name':'ambient temperature'},
           'dewpt':{'units':'degC','long_name':'dew point'},
           'tot_temp':{'units':'degC','long_name':'total temperature'},
           'stat_pres':{'units':'mb','long_name':'static pressure'},
           'dyn_pres':{'units':'mb','long_name':'dynamic pressure (total minus static)'},
           'cabin_pres':{'units':'mb','long_name':'cabin pressure'},
           'wspd':{'units':'m/s','long_name':'wind speed'},
           'wdir':{'units':'deg','long_name':'wind direction'},
           'vert_wspd':{'units':'m/s','long_name':'vertical wind speed'},
           'solar_zen':{'units':'deg','long_name':'solar zenith angle'},
           'sun_el_ac':{'units':'deg','long_name':'sun elevation from aircraft'},
           'sun_az_grnd':{'units':'deg','long_name':'sun azimuth from ground'},
           'sun_az_ac':{'units':'deg','long_name':'sun azimuth from aircraft'} }
          
if date in os.listdir(inDirBase):
    if date.startswith('2022'):
        inDir = inDirBase+'/'+date
        for file in os.listdir(inDir):
            if file.endswith('csv'):

                # Read in csv data as Datafreme object
                df = pd.read_csv(inDir+'/'+file)
        
                # Get rid of unnecessary 'iwg' column
                df = df.drop('IWG1',axis=1)

                # Create column headings
                df.columns = ['time','lat','lon','gps_msl_alt','wgs84_alt',
                              'pres_alt','radar_alt','grnd_spd','true_airspd',
                              'ind_airspd','mach','vert_vel','true_hdg','track',
                              'drift','pitch','roll','side_slip','ang_of_attack',
                              'amb_temp','dewpt','tot_temp','stat_pres','dyn_pres',
                              'cabin_pres','wspd','wdir','vert_wspd','solar_zen',
                              'sun_el_ac','sun_az_grnd','sun_az_ac']

                # Remove rows with no lat/lon info
                    
                # Convert times from yyyy-mm-ddThh:mm:ss.ssssss' to seconds since 01-01-1970
                df['time'] = pd.to_datetime(df['time'])
                df['time'] = df['time'].map(lambda time: int( (time - datetime(1970,1,1)).total_seconds() ) )

                # Set time as index
                df.set_index('time',inplace=True)
                    
                # For all vars except 'time' handle missing values
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

                # Create ncFile name
                if 'er2' in file:
                    plane = 'er2'
                elif 'p3' in file:
                    plane = 'p3'
                else:
                    plane = 'unk'
                    print('Not one of our aircraft: ',file)
                    
                outDir = outDirBase+'/'+date
                if not os.path.exists(outDir):
                    os.makedirs(outDir)
                #(category,platform,date,product,ext) = file.split('.')
                #ncFile = outDir+'/'+nc_prefix+'_'+date+'_'+platform+'.nc'
                ncFile = outDir+'/'+nc_prefix+'_'+date+'_'+plane+'.nc'
        
                # Convert xarray to netcdf with all _FillValues set to missing_value
                encoding ={}
                for var in varDict.keys():
                    if var != 'time':
                        encoding[var] = {'_FillValue':missingValue}
                xr.to_netcdf(ncFile,encoding=encoding)
       
