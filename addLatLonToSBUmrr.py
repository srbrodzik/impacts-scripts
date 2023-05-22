#!/usr/bin/python3

import os
import shutil

indirbase = '/home/disk/bob/impacts/radar/sbu/2022/mrrpro2white/netcdf'

for dir in os.listdir(indirbase):
    if dir.startswith('2022') and os.path.isdir(indirbase+'/'+dir):
        indir = indirbase+'/'+dir
        os.chdir(indir)
        for fileIn in os.listdir(indir):
            if fileIn.endswith('nc'):
                print(fileIn)
                (base,ext) = os.path.splitext(fileIn)
                fileOut1 = base+'_new1'+ext
                fileOut2 = base+'_new2'+ext
                command = "ncap2 -s 'longitude = -73.127' "+fileIn+" "+fileOut1
                os.system(command)
                command = "ncap2 -s 'latitude = 40.897' "+fileOut1+" "+fileOut2
                os.system(command)
                os.remove(fileIn)
                os.remove(fileOut1)
                shutil.move(fileOut2,fileIn)
                

