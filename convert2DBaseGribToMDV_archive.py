#!/usr/bin/python3

import sys
import os
import netCDF4 as nc
import shutil
import datetime
from datetime import date
from datetime import timezone
import glob

gribDir = '/home/disk/bob/impacts/raw/mrms/fillGaps/2DBaseReflQC'
filePrefix = 'MRMS_MergedBaseReflectivityQC'
extension = 'grib2'
ncDirBase = '/home/disk/bob/impacts/netcdf/mrms/2DBaseRefl'
mdvDirBase = '/home/disk/bob/impacts/mdv/mrms/2DBaseRefl'
paramsDir = '/home/disk/bob/impacts/git/lrose-impacts/projDir/ingest/params'
ncVarName = 'DBZ_base'
domain = ['32.','-105.','50.','-65.']   # [minLat,minLon,maxLat,maxLon]

for gribFile in os.listdir(gribDir):

    # convert grib2 to netcdf
    (base,ext) = os.path.splitext(gribFile)
    [mrms,product,level,dateAndTime] = base.split('_')
    [date,time] = dateAndTime.split('-')
    ncDir = ncDirBase+'/'+date
    ncFile = mrms+'.'+product+'.'+date+'.'+time+'.nc'

    if  not os.path.isdir(ncDir):
        os.makedirs(ncDir)
    command = 'wgrib2 '+gribDir+'/'+gribFile+' -netcdf '+ncDir+'/'+ncFile
    os.system(command)
    # Got this error when running as meso@bob:
    #/home/disk/sys/local/linux64/bin/wgrib2_stretch: error while loading shared libraries: libnetcdf.so.11: cannot open shared object file: No such file or directory

    # change variable name from MergedBaseReflectivityQC_500mabovemeansealevel to DBZ_base
    os.chdir(ncDir)
    ncFileNew = ncFile+'.new'
    command = 'ncrename -h -v MergedBaseReflectivityQC_500mabovemeansealevel,'+ncVarName+' '+ncFile+' '+ncFileNew
    os.system(command)

    # change base_refl attributes
    #command = 'ncatted -O -h -a short_name,base_refl,o,c,base_refl '+ncFileNew
    #os.system(command)
    #command = 'ncatted -O -h -a _FillValue,base_refl,o,f,-99 '+ncFileNew
    #os.system(command)

    # change all base_refl values < 0 to -999
    #with nc.Dataset(ncFileNew) as src:
    #    for varName, varIn in src.variables.items():
    #        if 'base_refl' in varName:
    #            base_refl = src[varName][:]
    #            base_refl[base_refl<0] = -999
    #            src[varName][:] = base_refl

    # rename ncFileNew
    shutil.move(ncFileNew,ncFile)

    # add alt dim to ncFile - PROBLEM WITH ' and "; need one more demarker
    #ncap2 -s 'defdim("altitude",1);altitude[altitude]=0.5;altitude@long_name="altitude";altitude@units="km"' -O MRMS.MergedBaseReflectivityQC.20211215.224819.nc MRMS.MergedBaseReflectivityQC.20211215.224819_new.nc
    command = "ncap2 -s \'defdim(\"altitude\",1);altitude[altitude]=0.5;altitude@long_name=\"altitude\";altitude@units=\"km\"\' -O "+ncFile+" "+ncFileNew
    os.system(command)
    shutil.move(ncFileNew,ncFile)

    # change domain to IMPACTS region
    #command = 'ncea -h -d latitude,32.,48. -d longitude,-100.,-66. '+ncFile+' '+ncFileNew
    command = 'ncea -h -d latitude,'+domain[0]+','+domain[2]+' -d longitude,'+domain[1]+','+domain[3]+' '+ncFile+' '+ncFileNew
    os.system(command)
    shutil.move(ncFileNew,ncFile)

    # set DATE environment var
    os.environ['DATE'] = date
    command = 'NcGeneric2Mdv -v -params '+paramsDir+'/NcGeneric2Mdv.mrms_base_refl -f '+ncFile
    os.system(command)

