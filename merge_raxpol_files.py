#!/usr/bin/python3

import os
import netCDF4 as nc
import glob
from copyRaxpolAttsDimsVarsToNewFile import copyRaxpolAttsDimsVarsToNewFile

inDirBase = '/home/disk/bob/impacts/raw/radar/raxpol/sur'
outDirBase = '/home/disk/bob/impacts/raw/radar/raxpol/sur/volumes'
dateStr = '20230125'
fields = {'D':{'inName':'Differential_Reflectivity','outName':'ZDR'},
          'P':{'inName':'PhiDP','outName':'PHIDP'},
          'R':{'inName':'RhoHV','outName':'RHOHV'},
          'V':{'inName':'Radial_Velocity','outName':'VEL'},
          'W':{'inName':'Width','outName':'SW'},
          'Z':{'inName':'Intensity','outName':'REFL'}
          }
excludedAttrs = ['TypeName','Unit-unit','Unit-value','ColorMap-unit',
                 'ColorMap-value']

os.chdir(inDirBase+'/'+dateStr)
Zfiles = glob.glob('RAXPOL*-Z.nc')

for Zfile in Zfiles:
    print(Zfile)
    (base,ext) = os.path.splitext(Zfile)
    volFiles = glob.glob(base[:-1]+'*.nc')
    for index,inFile in enumerate(volFiles,0):
        print('   ',inFile)
        firstFile = False
        (base,ext) = os.path.splitext(inFile)
        (raxpol,date,time,junk,field) = base.split('-')
        if index == 0:
            # Create path and name for new netcdf file
            outDir = outDirBase+'/'+date
            if not os.path.isdir(outDir):
                os.makedirs(outDir)
            outName = 'raxpol.'+date+'.'+time+'.nc'
            outFile = outDir+'/'+outName
            firstFile = True
        copyRaxpolAttsDimsVarsToNewFile(inFile,outFile,excludedAttrs,fields,field,firstFile)
        

