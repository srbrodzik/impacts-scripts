#!/usr/bin/python

import os
from netCDF4 import Dataset
import pickle
import pandas as pd

#ncBaseDir = '/home/disk/funnel/impacts-website/data_archive/nys_prof/2020/netcdf_QC'
ncBaseDir = '/home/disk/bob/impacts/raw/nys_profiler_2022'
pickleDir = '/home/disk/bob/impacts/bin/pickle_jar'
pickleFile = 'nys_prof.pkl'
nc_prefix = 'nys_profiler'

# To create pickle file used this:
# df = pd.read_csv('nys_prof.csv')
# with open('nys_prof.pkl','wb') as f:
#     pickle.dump(df,f)

# Read site information from pickle
#with open(pickleDir+'/'+pickleFile,'rb') as f:
#    site_info = pickle.load(f)
site_info = pd.read_pickle(pickleDir+'/'+pickleFile)
site_info.set_index('stid',inplace=True)
site_info.rename(columns={'lat [deg]':'lat', 'lon [deg]':'lon', 'elev [m]':'elev'},inplace=True)

for date in os.listdir(ncBaseDir):

    if os.path.isdir(ncBaseDir+'/'+date) and date.startswith('202'):
        print(date)
        inDir = ncBaseDir+'/'+date

        for file in os.listdir(inDir):

            if file.endswith('nc'):

                print(file)

                (base,ext) = os.path.splitext(file)
                (prefix,date,site) = base.split('.')
        
                # Get site info
                site_lat = site_info.at['PROF_'+site.upper(),'lat']
                site_lon = site_info.at['PROF_'+site.upper(),'lon']
                site_elev = site_info.at['PROF_'+site.upper(),'elev']
                site_name_long = site_info.at['PROF_'+site.upper(),'name']
                site_name_abbr = 'PROF_'+site.upper()
                site_county = site_info.at['PROF_'+site.upper(),'county']
    
                ncid = Dataset(inDir+'/'+file,'a')
                ncid.site_latitude = site_lat
                ncid.site_longitude = site_lon
                ncid.site_elevation = site_elev
                ncid.site_name_long = site_name_long
                ncid.site_name_abbr = site_name_abbr
                ncid.site_county = site_county
                ncid.close()
                

