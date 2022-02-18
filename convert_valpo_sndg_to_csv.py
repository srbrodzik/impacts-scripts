#!/usr/bin/python3

# File naming convention for NWS sounding netcdf files:
# IMPACTS_sounding_<start date>_<start time>_<site name>.nc

import os
import sys
import shutil
from datetime import datetime
import pandas as pd

if len(sys.argv) != 2:
    print('Usage: sys.argv[0] [date(YYYYMMDD)]')
    sys.exit()
else:
    date = sys.argv[1]

inDirBase = '/home/disk/bob/impacts/upperair/valpo'
outDirBase = inDirBase
inDir = inDirBase+'/'+date
outDir = outDirBase+'/'+date
csvPrefix = 'upperair.VALPO_sonde'
"""
colNames = {'pres':{'units':'hPa','long_name': ''},
            'temp':{'units':'degC','long_name':''},
            'dewpt':{'units':'degC','long_name':''},
            'rh':{'units':'%','long_name':''},
            'ht':{'units':'m','long_name':'height above ground level'},
            'wspd':{'units':'knots','long_name':'wind speed'},
            'wdir':{'units':'deg','long_name':''},
            'flt_time':{'units':'seconds','long_name':''},
            'ascent_rate':{'units':'m/min','long_name':''},
            'type':{'units':'','long_name':''}}
"""
lat = 41.464
lon = -87.039

# create csv
for file in os.listdir(inDir):
    if file.endswith('SIGLVLS.txt'):
        (base,ext) = os.path.splitext(file)
        (date,hour,junk) = base.split('_')
        csvFile = csvPrefix+'.'+date+hour+'00.csv'
        #csvFile = base+'.csv'
        fout = open(outDir+'/'+csvFile,'w')
        fout.write('{} {} {}'.format('date:',date,'\n'))
        fout.write('{} {}{}'.format('time:',hour,'00\n'))
        fout.write('{} {} {}'.format('lat:',lat,'\n'))
        fout.write('{} {} {}'.format('lon:',lon,'\n'))
        with open(inDir+'/'+file,encoding='unicode_escape') as fin:
            numLines = 0
            for line in fin:
                if numLines == 2:
                    fout.write(line)
                if len(line) > 1:
                    shortLine = line.strip()
                    if shortLine[0].isdigit():
                        fout.write(line)
                numLines = numLines + 1
        fout.close()

