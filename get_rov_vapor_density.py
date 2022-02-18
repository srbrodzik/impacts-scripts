#!/usr/bin/python3

import os
import numpy as np
import netCDF4 as nc

inDirBase = '/home/disk/bob/impacts/raw/nys_profiler_2022'
outFile = '/home/disk/bob/impacts/raw/nys_profiler_2022/vapor_density_info.txt'

fout = open(outFile,'w')

min_all = 100.0
max_all = 0.0

for date in os.listdir(inDirBase):
    if os.path.isdir(inDirBase+'/'+date) and date.startswith('20220'):
        inDir = inDirBase+'/'+date
        for file in os.listdir(inDir):
            if file.endswith('nc'):
                print('{} {}'.format('file =',file))
                ncid = nc.Dataset(inDir+'/'+file,'r')
                vd = ncid['vapor_density'][:]
                ncid.close()
                min = np.min(vd)
                max = np.max(vd)
                if min < min_all:
                    min_all = min
                if max > max_all:
                    max_all = max
                fout.write('{}: vd_min = {:.3f} vd_max = {:.3f}\n'.format(file,min,max))

fout.write('All Files: vd_min = {:.3f} vd_max = {:.3f}\n'.format(min_all,max_all))
fout.close()

                
                
