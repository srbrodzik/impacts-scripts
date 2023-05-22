#!/usr/bin/python3

import os
from netCDF4 import Dataset
import pickle

ncBaseDir = '/home/disk/bob/impacts/raw/nys_ground_2022'
pickleDir = '/home/disk/bob/impacts/bin/pickle_jar'
pickleFile = 'nysm_2021.pkl'
nc_prefix = 'nysm_standard'

# Read site information from pickle
# To create pickle file used this:
# df = pd.read_csv('nys_prof.csv')
# with open('nys_prof.pkl','wb') as f:
#     pickle.dump(df,f)
with open(pickleDir+'/'+pickleFile,'rb') as f:
    site_info = pickle.load(f)
#site_info = pd.read_pickle(pickleDir+'/'+pickleFile)
site_info.set_index('stid',inplace=True)
site_info.rename(columns={'lat [degrees]':'lat', 'lon [degrees]':'lon', 'elevation [m]':'elev'},inplace=True)

for date in os.listdir(ncBaseDir):

    if os.path.isdir(ncBaseDir+'/'+date):
    
        print(date)
        inDir = ncBaseDir+'/'+date

        for file in os.listdir(inDir):

            if file.endswith('nc'):

                print(file)

                (base,ext) = os.path.splitext(file)
                (prefix,date,site) = base.split('.')
        
                # Get site info
                site_lat = site_info.at[site.upper(),'lat']
                site_lon = site_info.at[site.upper(),'lon']
                site_elev = site_info.at[site.upper(),'elev']
                #site_name_long = site_info.at[site.upper(),'name']
                #site_name_abbr = site.upper()
                #site_wfo_code = site_info.at[site.upper(),'wfo']
                #site_nearest_city = site_info.at[site.upper(),'nearest_city']
                #site_county = site_info.at[site.upper(),'county']
                #site_state = site_info.at[site.upper(),'state']
    
                ncid = Dataset(inDir+'/'+file,'a')
                ncid.site_latitude = site_lat
                ncid.site_longitude = site_lon
                ncid.site_elevation = site_elev
                #ncid.site_name_long = site_name_long
                #ncid.site_name_abbr = site_name_abbr
                #ncid.site_wfo_code = site_wfo_code
                #ncid.site_nearest_city = site_nearest_city
                #ncid.site_county = site_county
                #ncid.site_state = site_state
                ncid.close()
                

