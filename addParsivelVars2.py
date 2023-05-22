#!/usr/bin/python3

import os
import netCDF4 as nc
import numpy as np
import sys
import shutil

inFile = '/home/disk/bob/impacts/radar/sbu/parsivel_info.nc'
# 2023
#indir = '/home/disk/bob/impacts/radar/sbu/BNL/parsivel/NEW'
# 2022
#indir = '/home/disk/bob/impacts/radar/sbu/2022/parsivel/netcdf/2022/NEW'
#indir = '/home/disk/bob/impacts/radar/sbu/2022/RadarTruck/parsivel2/netcdf/2022/NEW'
# 2020
#indir = '/home/disk/bob/impacts/radar/sbu/2020/parsivel/NEW'
#indir = '/home/disk/bob/impacts/radar/sbu/2020/parsivel2/NEW'
indir = '/home/disk/bob/impacts/radar/sbu/2020/RadarTruck/parsivel2/NEW'

os.chdir(indir)

for outFile in os.listdir(indir):
    if outFile.endswith('nc'):
        print(outFile)

        with nc.Dataset(inFile) as src, nc.Dataset(outFile, "a") as dst:
            # copy global attributes
            for name in src.ncattrs():
                dst.setncattr(name, src.getncattr(name))

            """
            # copy dimensions from src
            for dimName, dimValue in src.dimensions.items():
                print(dimName, len(dimValue))
                dst.createDimension(dimName, len(dimValue) if not dimValue.isunlimited() else None)
            """

            # copy all variables except reflectivity
            for varName, varIn in src.variables.items():
                #fill_value = None
                #if hasattr(varIn,'_FillValue'):
                #    fill_value = varIn._FillValue
                outVar = dst.createVariable(varName,varIn.datatype,
                                            varIn.dimensions)
                #print(varIn.datatype)
                #print(varIn.ncattrs())
                outVar.setncatts({k: varIn.getncattr(k) for k in varIn.ncattrs() if k not in ['_FillValue']})
                outVar[:] = varIn[:]


        
        
        
