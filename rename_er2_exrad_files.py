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

if date == '20220108':
    features = {'xfeature01':'1619',
                'xfeature02':'1630',
                'xfeature03':'1639',
                'xfeature04':'1705',
                'xfeature05':'1744',
                'xfeature06':'1751',
                'xfeature07':'1830',
                'xfeature08':'1849',
                'xfeature09':'1939'}
elif date == '20220119':
    features = {'xfeature01':'1220',
                'xfeature02':'1231',
                'xfeature03':'1259',
                'xfeature04':'1316',
                'xfeature05':'1338',
                'xfeature06':'1409',
                'xfeature07':'1424',
                'xfeature08':'1445',
                'xfeature09':'1459',
                'xfeature10':'1518',
                'xfeature11':'1535',
                'xfeature12':'1547'}
elif date == '20220129':
    features = {'xfeature01':'2310',
                'xfeature02':'0033',
                'xfeature03':'0045',
                'xfeature04':'0055',
                'xfeature05':'0116',
                'xfeature06':'0133',
                'xfeature07':'0201'}
else:
    print('Date = '+date+' not recognized')
    sys.exit()
    
date_obj = datetime.strptime(date,'%Y%m%d')
fields = {'dBZe':'EXRAD_dBZ',
          'dopplerCorrected':'EXRAD_vel',
          'specwid':'EXRAD_sw'}

for file in os.listdir(indir+'/'+date):
    if file.startswith('EXRAD') and 'xfeature' in file:
        print(file)
        basename = os.path.splitext(file)[0]
        ext = os.path.splitext(file)[1]
        basename = basename.replace('EXRAD_NADIR_','')
        (feature,junk,field) = basename.split('_')
        if date == '20220129' and features[feature] < '1000':
            date_new_obj = date_obj + timedelta(days=1)
            date_new = date_new_obj.strftime('%Y%m%d')
        else:
            date_new = date
        file_new = prefix+'.'+date_new+features[feature]+'.'+fields[field]+ext
        shutil.move(indir+'/'+date+'/'+file,
                    outdir+'/'+date+'/'+file_new)
        
        
