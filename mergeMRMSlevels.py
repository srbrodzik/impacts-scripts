#!/usr/bin/python3

import os
import netCDF4 as nc
import numpy as np
import sys
import shutil
from copyAttsDimsVarsToNewFile import copyAttsDimsVarsToNewFile

#if len(sys.argv) != 2:
#    errMsg = 'Usage: '+sys.argv[0]+': [grib2 filename]'
#    sys.exit(errMsg)
#else:
#    file = sys.argv[1]
file = 'MRMS_MergedReflectivityQC_19.00_20211027-000037.grib2.gz'

tempdir = '/tmp'
outdirbase = '/home/disk/bob/impacts/netcdf/mrms'
nalts = 33
refl_name = 'dbz_qc'

levelDict = {'00.50':0,'00.75':1,'01.00':2,'01.25':3,'01.50':4,'01.75':5,
             '02.00':6,'02.25':7,'02.50':8,'02.75':9,'03.00':10,'03.50':11,
             '04.00':12,'04.50':13,'05.00':14,'05.50':15,'06.00':16,'06.50':17,
             '07.00':18,'07.50':19,'08.00':20,'08.50':21,'09.00':22,'10.00':23,
             '11.00':24,'12.00':25,'13.00':26,'14.00':27,'15.00':28,'16.00':29,
             '17.00':30,'18.00':31,'19.00':32}
altList = []
for alt in levelDict.keys():
    altList.append(float(alt))
    altArr = np.array(altList)
          
if file.endswith('grib2.gz'):

    # strip off pathname, if it exists
    file_base = os.path.basename(file)
    
    # uncompress grib2 file and write to tempdir
    [gribFile,ext] = os.path.splitext(file_base)
    command = 'zcat '+file+' > '+tempdir+'/'+gribFile
    os.system(command)

    # convert grib2 to netcdf
    # These commands give me these errors:
    # ** Warning: reference time includes non-zero minutes/seconds **
    # 1:0:d=2021102700:ConusMergedReflectivityQC:750 m above mean sea level:anl:

    [base,ext] = os.path.splitext(gribFile)
    ncFile = tempdir+'/'+base+'.nc'
    command = 'wgrib2 '+tempdir+'/'+gribFile+' -netcdf '+ncFile
    os.system(command)

    # reduce dimensions of ncFile
    #command = 'ncea -d latitude,25.,50. -d longitude,-105.,-65. '+ncFile+' '+ncFile+'.new'
    command = 'ncea -d latitude,32.,47. -d longitude,-93.,-67. '+ncFile+' '+ncFile+'.new'
    os.system(command)
    shutil.move(ncFile+'.new',ncFile)
    
    # create merge file name
    [product,var,level,date_time] = base.split('_')
    [date,time] = date_time.split('-')
    outdir = outdirbase+'/'+date
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    ncFile_out = outdir+'/'+product+'.'+var+'.'+date+'.'+time+'.nc'

    # create merge file if it doesn't exist
    if not os.path.isfile(ncFile_out):
        copyAttsDimsVarsToNewFile(ncFile,ncFile_out,nalts,refl_name,altArr)

    # copy refl data from input file to appropriate level of output file
    with nc.Dataset(ncFile) as src:
        for var_name, varin in src.variables.items():
            if 'Reflectivity' in var_name:
                #refl_name = var_name
                refl = src[var_name][:]
    #[refl_name_merge,junk] = refl_name.split('_')
    refl[refl<0] = -999.

    with nc.Dataset(ncFile_out, "a") as dst:
        #dst[refl_name_merge][:,levelDict[level],:,:] = refl
        dst[refl_name][:,levelDict[level],:,:] = refl

    # clean up 
    os.remove(tempdir+'/'+gribFile)
    os.remove(ncFile)

