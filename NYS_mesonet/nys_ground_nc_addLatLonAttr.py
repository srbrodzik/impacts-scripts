#!/usr/bin/python

import os
from netCDF4 import Dataset
import pickle

ncBaseDir = '/home/disk/funnel/impacts-website/data_archive/nys_ground/2020/netcdf_QC'
pickleDir = '/home/disk/bob/impacts/bin/pickle_jar'
pickleFile = 'nysm.pkl'
nc_prefix = 'IMPACTS_nys_ground'

# Read site information from pickle
with open(pickleDir+'/'+pickleFile,'rb') as f:
    site_info = pickle.load(f)
site_info.set_index('stid',inplace=True)
site_info.rename(columns={'lat [degrees]':'lat', 'lon [degrees]':'lon'},inplace=True)

for site in os.listdir(ncBaseDir):
    print(site)

    # Get site info
    site_lat = site_info.at[site.upper(),'lat']
    site_lon = site_info.at[site.upper(),'lon']
    
    if os.path.isdir(ncBaseDir+'/'+site):
        inDir = ncBaseDir+'/'+site
        
        for file in os.listdir(inDir):
            if file.endswith('.nc'):
                print(file)
                ncid = Dataset(inDir+'/'+file,'a')
                ncid.site_latitude = site_lat
                ncid.site_longitude = site_lon
                ncid.close()
                

