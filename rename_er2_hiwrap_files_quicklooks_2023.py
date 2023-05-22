#!/usr/bin/python3

import os
import sys
import shutil
from datetime import datetime
from datetime import timedelta

if len(sys.argv) != 3:
    print('Usage: {} [YYYYMMDD] [ka/ku]'.format(sys.argv[0]))
    sys.exit()
else:
    date = sys.argv[1]
    band = sys.argv[2]

indir = '/home/disk/bob/impacts/radar/er2/postFlight/quicklooks/HIWRAP_'+band.upper()
outdir = '/home/disk/bob/impacts/radar/er2/postFlight/quicklooks/HIWRAP_'+band.upper()
prefix = 'aircraft.NASA_ER2'

fields = {'UncalRef':'HIWRAP_'+band+'_dBZ',
          'dBZe':'HIWRAP_'+band+'_dBZ',
          'dopplerCorrected':'HIWRAP_'+band+'_vel',
          'ldr':'HIWRAP_'+band+'_ldr',
          'specwid':'HIWRAP_'+band+'_sw'}

for file in os.listdir(indir+'/'+date):
    if file.startswith('HIWRAP'):
        print(file)
        (base,ext) = os.path.splitext(file)
        (junk,fband,project,junk,fstart,junk,fend,fprod) = base.split('_')
        fstartObj = datetime.strptime(fstart, '%Y%m%dT%H%M%S')
        catDatetime = fstartObj.strftime('%Y%m%d%H%M')
        catName = prefix+'.'+catDatetime+'.'+fields[fprod]+ext
        shutil.move(indir+'/'+date+'/'+file,
                    outdir+'/'+date+'/'+catName)
        
        
