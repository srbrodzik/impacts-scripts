#!/usr/bin/python

import os
import shutil
import sys
from datetime import datetime
from datetime import timedelta

if len(sys.argv) != 2:
    print('Usage: sys.argv[0] [YYMMDD]')
    sys.exit()
else:
    date = sys.argv[1]

indir = '/home/disk/bob/impacts/er2/CRS'
outdir = '/home/disk/bob/impacts/er2/CRS'
prefix = 'research.er2'

if date == '20200125':
    features = {'xfeature01':'1850',
                'xfeature02':'1920',
                'xfeature03':'2000',
                'xfeature04':'2030',
                'xfeature05':'2054',
                'xfeature06':'2107',
                'xfeature07':'2124',
                'xfeature08':'2135',
                'xfeature09':'2202',
                'xfeature10':'2215',
                'xfeature11':'2238',
                'xfeature12':'2247',
                'xfeature13':'2302',
                'xfeature14':'2310'}
elif date == '20200201':
    features = {'xfeature01':'1147',
                'xfeature02':'1205',
                'xfeature03':'1225',
                'xfeature04':'1244',
                'xfeature05':'1306',
                'xfeature06':'1326',
                'xfeature07':'1354',
                'xfeature08':'1430',
                'xfeature09':'1500',
                'xfeature10':'1526'}
elif date == '20200205':
    features = {'xfeature01':'1927',
                'xfeature02':'2055',
                'xfeature03':'2143',
                'xfeature04':'2234',
                'xfeature05':'2307',
                'xfeature06':'2329',
                'xfeature07':'2347'}
elif date == '20200207':
    features = {'xfeature01':'1239',
                'xfeature02':'1355',
                'xfeature03':'1434',
                'xfeature04':'1457',
                'xfeature05':'1508',
                'xfeature06':'1530',
                'xfeature07':'1556',
                'xfeature08':'1620'}
elif date == '20200225':
    features = {'xfeature01':'2030',
                'xfeature02':'2210',
                'xfeature03':'2231',
                'xfeature04':'2254',
                'xfeature05':'2321',
                'xfeature06':'2337',
                'xfeature07':'2348',
                'xfeature08':'0012',
                'xfeature09':'0030',
                'xfeature10':'0108',
                'xfeature11':'0129',
                'xfeature12':'0150'}
elif date == '20200227':
    features = {'xfeature01':'0757',
                'xfeature02':'0859',
                'xfeature03':'0950',
                'xfeature04':'1023',
                'xfeature05':'1055',
                'xfeature06':'1126',
                'xfeature07':'1152',
                'xfeature08':'1215',
                'xfeature09':'1234',
                'xfeature10':'1252',
                'xfeature11':'1305'}
else:
    print('Date = '+date+' not recognized')
    sys.exit()
    
date_obj = datetime.strptime(date,'%Y%m%d')
fields = {'dBZe':'crs_dbz',
          'doppler':'crs_vel',
          'ldr':'crs_ldr',
          'spectrumwidth':'crs_sw'}

for file in os.listdir(indir+'/'+date):
    if file.startswith('IMPACTS') and 'xfeature' in file:
        print(file)
        basename = os.path.splitext(file)[0]
        ext = os.path.splitext(file)[1]
        basename = basename.replace('IMPACTS_CRS_L1B_Ver1_','')
        (start,to,stop,feature,field) = basename.split('_')
        if date == '20200225' and features[feature] < '1000':
            date_new_obj = date_obj + timedelta(days=1)
            date_new = date_new_obj.strftime('%Y%m%d')
        else:
            date_new = date
        file_new = prefix+'.'+date_new+features[feature]+'.'+fields[field]+ext
        shutil.move(indir+'/'+date+'/'+file,
                    outdir+'/'+date+'/'+file_new)
        
        
