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
#indirbase = '/home/disk/bob/impacts/raw/mrms/AlbertaClippers/mrefl/Reflectivity3D'
indirbase = '/home/disk/bob/impacts/raw/mrms/AlbertaClippers/mkdp/KDP3D'
#indirbase = '/home/disk/bob/impacts/raw/mrms/AlbertaClippers/mrhohv/RHOHV3D'
#indirbase = '/home/disk/bob/impacts/raw/mrms/AlbertaClippers/mspw/SPW3D'
#indirbase = '/home/disk/bob/impacts/raw/mrms/AlbertaClippers/mzdr/ZDR3D'
#-----
#outdirbase = '/home/disk/bob/impacts/netcdf/mrms/3DRefl/AlbClip'
outdirbase = '/home/disk/bob/impacts/netcdf/mrms/3DKdp/AlbClip'
#outdirbase = '/home/disk/bob/impacts/netcdf/mrms/3DRhoHV/AlbClip'
#outdirbase = '/home/disk/bob/impacts/netcdf/mrms/3DSW/AlbClip'
#outdirbase = '/home/disk/bob/impacts/netcdf/mrms/3DZdr/AlbClip'
#-----
nalts = 17
#-----
#var_name_in = 'Reflectivity3D'
var_name_in = 'KDP3D'
#var_name_in = 'RHOHV3D'
#var_name_in = 'SPW3D'
#var_name_in = 'ZDR3D'
#-----
#var_name_out = 'DBZ'
var_name_out = 'KDP'
#var_name_out = 'RHOHV'
#var_name_out = 'SW'
#var_name_out = 'ZDR'
#-----
#long_name = 'WSR-88D 3D Reflectivty Mosaic with SE Canadian radars'
long_name = 'specific_differential_phase'
#long_name = 'correlation_coefficient'
#long_name = 'spectrum_width'
#long_name = 'differential_reflectivity"'
#-----
#units = 'dBZ'
units = 'deg/km'
#units = '-'
#units = 'm/s'
#units = 'dB'
#-----
outfilePrefix = 'IMPACTS_mrms'
#-----
#outfileSuffix = 'DBZ.nc'
outfileSuffix = 'KDP.nc'
#outfileSuffix = 'RHOHV.nc'
#outfileSuffix = 'SW.nc'
#outfileSuffix = 'ZDR.nc'
#-----
missing = -999.

levelDict = {'00.50':0,'00.75':1,'01.00':2,'01.25':3,'01.50':4,'01.75':5,
             '02.00':6,'02.25':7,'02.50':8,'02.75':9,'03.00':10,'03.50':11,
             '04.00':12,'04.50':13,'05.00':14,'05.50':15,'06.00':16}
altList = []
for alt in levelDict.keys():
    altList.append(float(alt))
    altArr = np.array(altList)
    
indir = indirbase+'/'+list(levelDict.keys())[0]
for file in os.listdir(indir):

    print(file)

    # get files at all other levels for that date and time
    flist = glob.glob(indirbase+'/0?.??/'+file)

    for ncFile in flist:

        print(ncFile)

        [path,f] = os.path.split(ncFile)
        [fBase,ext] = os.path.splitext(f)
        [date,time] = fBase.split('-')
        path_subdirs = path.split('/')
        level = path_subdirs[-1]
    
        # create merge file name
        outdir = outdirbase+'/'+date
        if not os.path.isdir(outdir):
            os.makedirs(outdir)
        ncFile_out = outdir+'/'+outfilePrefix+'_'+date+'_'+time+'_'+outfileSuffix

        # create merge file if it doesn't exist
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
            dst[var_name_out][:,levelDict[level],:,:] = var_values

        # clean up 
        #os.remove(ncFile)

