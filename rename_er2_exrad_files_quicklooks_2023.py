#!/usr/bin/python3

import os
import sys
import shutil
from datetime import datetime
from datetime import timedelta

if len(sys.argv) != 2:
    print('Usage: {} [YYYYMMDD]'.format(sys.argv[0]))
    sys.exit()
else:
    date = sys.argv[1]

indir = '/home/disk/bob/impacts/radar/er2/postFlight/quicklooks/EXRAD'
outdir = '/home/disk/bob/impacts/radar/er2/postFlight/quicklooks/EXRAD'
prefix = 'aircraft.NASA_ER2'

fields = {'UncalRef':'EXRAD_dBZ',
          'dBZe':'EXRAD_dBZ',
          'dopplerCorrected':'EXRAD_vel',
          'specwid':'EXRAD_sw'}

for file in os.listdir(indir+'/'+date):
    if file.startswith('EXRAD'):
        print(file)
        (base,ext) = os.path.splitext(file)
        (junk,junk,project,fstart,junk,fend,fprod) = base.split('_')
        fstartObj = datetime.strptime(fstart, '%Y%m%dT%H%M%S')
        catDatetime = fstartObj.strftime('%Y%m%d%H%M')
        catName = prefix+'.'+catDatetime+'.'+fields[fprod]+ext
        shutil.move(indir+'/'+date+'/'+file,
                    outdir+'/'+date+'/'+catName)

