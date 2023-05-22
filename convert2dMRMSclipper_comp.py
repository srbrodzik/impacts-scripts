#!/usr/bin/python3

import os
import netCDF4 as nc
import numpy as np
import sys
import shutil
import glob
from copyAttsDimsVarsToNewFileClipper import copyAttsDimsVarsToNewFileClipper

tempdir = '/tmp'
#-----
#indirbase = '/home/disk/bob/impacts/raw/mrms/AlbertaClippers/base_refl/BASE_REFL/00.00'
indirbase = '/home/disk/bob/impacts/raw/mrms/AlbertaClippers/cref/CREF/00.50'
#-----
#outdirbase = '/home/disk/bob/impacts/netcdf/mrms/2DBaseRefl/AlbClip'
outdirbase = '/home/disk/bob/impacts/netcdf/mrms/2DCompRefl/AlbClip'
#-----
nalts = 1
#-----
#var_name_in = 'BASE_REFL'
var_name_in = 'CREF'
#-----
#var_name_out = 'DBZ_base'
var_name_out = 'DBZ_comp'
#-----
#long_name = 'Mosaic Base Reflectivity'
long_name = 'Composite Reflectivity Mosaic '
#-----
#units = 'dBZ'
units = 'dBZ'
#-----
outfilePrefix = 'IMPACTS_mrms'
#-----
#outfileSuffix = 'BaseDBZ.nc'
outfileSuffix = 'CompDBZ.nc'
#-----
missing = -999.

altArr = np.array(['00.50'])
    
indir = indirbase
for file in os.listdir(indir):

    print(file)

    # get date and time from input file
    [path,f] = os.path.split(file)
    [fBase,ext] = os.path.splitext(f)
    [date,time] = fBase.split('-')

    # get full path of input file
    ncFile = indir+'/'+file
    
    # create output file name
    outdir = outdirbase+'/'+date
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    ncFile_out = outdir+'/'+outfilePrefix+'_'+date+'_'+time+'_'+outfileSuffix

    # create output file if it doesn't exist
    if not os.path.isfile(ncFile_out):
        missing_data = copyAttsDimsVarsToNewFileClipper(ncFile,ncFile_out,nalts,
                                                        var_name_in,var_name_out,
                                                        long_name,units,altArr,
                                                        missing)

    # copy var data from input file to appropriate level of output file
    with nc.Dataset(ncFile) as src:
        for var_name, varin in src.variables.items():
            if var_name_in in var_name:
                #var_name_in = var_name
                var_values = src[var_name][:]
    var_values[var_values==missing_data] = missing
    var_values[var_values<0] = missing
    [nlat,nlon] = var_values.shape
    var_values = np.reshape(var_values,(1,1,nlat,nlon))

    with nc.Dataset(ncFile_out, "a") as dst:
        dst[var_name_out][:,:,:,:] = var_values

    # clean up 
    #os.remove(ncFile)

