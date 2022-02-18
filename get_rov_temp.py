#!/usr/bin/python3

import os
import numpy as np
import netCDF4 as nc

def K_to_C(degK):
    '''
    Given Kelvin temperature, returns a Celsius temperature.
    
    Parameters: 
    degK (float): Actual temperature, in degrees K
    
    Returns:
    degC (float): Actual temperature, in degrees C
    '''
    
    degC = degK - 273.15
    return degC

inDirBase = '/home/disk/bob/impacts/raw/nys_profiler_2022'
outFile = '/home/disk/bob/impacts/raw/nys_profiler_2022/temp_info.txt'

fout = open(outFile,'w')

min_all = 1000.0
max_all = -1000.0

for date in os.listdir(inDirBase):
    if os.path.isdir(inDirBase+'/'+date) and date.startswith('20220'):
        inDir = inDirBase+'/'+date
        for file in os.listdir(inDir):
            if file.endswith('nc'):
                print('{} {}'.format('file =',file))
                ncid = nc.Dataset(inDir+'/'+file,'r')
                t = ncid['temperature'][:]
                ncid.close()
                min = np.min(t)
                max = np.max(t)
                if min < min_all:
                    min_all = min
                if max > max_all:
                    max_all = max
                fout.write('{}: t_min = {:.3f} t_max = {:.3f}\n'.format(file,K_to_C(min),K_to_C(max)))

fout.write('All Files: t_min = {:.3f} t_max = {:.3f}\n'.format(K_to_C(min_all),K_to_C(max_all)))
fout.close()

                
                
