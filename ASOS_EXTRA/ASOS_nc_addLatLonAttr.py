#!/usr/bin/python

import os
from netCDF4 import Dataset
import pickle

ncBaseDir = '/home/disk/funnel/impacts-website/data_archive/asos_isu_nc'
pickleDir = '/home/disk/bob/impacts/bin/pickle_jar'
pickleFile = 'ASOS_stations.pkl'

# Read site information from pickle
with open(pickleDir+'/'+pickleFile,'rb') as f:
    site_info = pickle.load(f)
#site_info.set_index('stid',inplace=True)
#site_info.rename(columns={'lat [degrees]':'lat', 'lon [degrees]':'lon'},inplace=True)

for date in os.listdir(ncBaseDir):
    print(date)
    inDir = ncBaseDir+'/'+date

    for file in os.listdir(inDir):
        if file.endswith('.nc'):

            # Get site name
            (basename,ext) = os.path.splitext(file)
            (project,platform,day,site) = basename.split('_')
            print(site)
        
            # Get site info
            site_lat = site_info[site.upper()][3]
            site_lon = site_info[site.upper()][2]
            site_elev = site_info[site.upper()][4]            

            # Add global attributes
            ncid = Dataset(inDir+'/'+file,'a')
            ncid.site_latitude = site_lat
            ncid.site_longitude = site_lon
            ncid.site_elevation = site_elev
            ncid.close()
                

