#!/usr/bin/python3

import os
import shutil
import sys
from datetime import datetime
from datetime import timedelta

if len(sys.argv) != 2:
    print('Usage: sys.argv[0] [YYYYMMDD]')
    sys.exit()
else:
    date = sys.argv[1]

print('date =',date)
    
indir = '/home/disk/bob/impacts/radar/er2/postFlight/quicklooks/CRS'
outdir = '/home/disk/bob/impacts/radar/er2/postFlight/quicklooks/CRS'
prefix = 'aircraft.NASA_ER2'
suffix = 'CRS_dBZ'

if date == '20230113':
    features = {'CRSv3-Science_0000':'0335',
                'CRSv3-Science_0001':'0420',
                'CRSv3-Science_0002':'0500',
                'CRSv3-Science_0003':'0545',
                'CRSv3-Science_0004':'0625',
                'CRSv3-Science_0005':'0710',
                'CRSv3-Science_0006':'0750',
                'CRSv3-Science_0007':'0835',
                'CRSv3-Science_0008':'0915',
                'CRSv3-Science_0009':'1000',
                'CRSv3-Science_0010':'1038'}
elif date == '20230115':
    features = {'CRSv3-Science_0000':'1300',
                'CRSv3-Science_0001':'1340',
                'CRSv3-Science_0002':'1425',
                'CRSv3-Science_0003':'1505',
                'CRSv3-Science_0004':'1550',
                'CRSv3-Science_0005':'1630',
                'CRSv3-Science_0006':'1715',
                'CRSv3-Science_0007':'1755',
                'CRSv3-Science_0008':'1840',
                'CRSv3-Science_0009':'1920'}
elif date == '20230119':
    features = {'CRSv3-Science_0000':'1945',
                'CRSv3-Science_0001':'2030',
                'CRSv3-Science_0002':'2110',
                'CRSv3-Science_0003':'2155',
                'CRSv3-Science_0004':'2235',
                'CRSv3-Science_0005':'2320',
                'CRSv3-Science_0006':'0000',
                'CRSv3-Science_0007':'0045',
                'CRSv3-Science_0008':'0125',
                'CRSv3-Science_0009':'0210',
                'CRSv3-Science_0010':'0250'}
elif date == '20230123':
    features = {'CRSv3-Science_0000':'1210',
                'CRSv3-Science_0001':'1255',
                'CRSv3-Science_0002':'1335',
                'CRSv3-Science_0003':'1420',
                'CRSv3-Science_0004':'1500',
                'CRSv3-Science_0005':'1545',
                'CRSv3-Science_0006':'1625',
                'CRSv3-Science_0007':'1710',
                'CRSv3-Science_0008':'1750',
                'CRSv3-Science_0009':'1835',
                'CRSv3-Science_0010':'1914'}
elif date == '20230125':
    features = {'CRSv3-Science_0000':'1745',
                'CRSv3-Science_0001':'1825',
                'CRSv3-Science_0002':'1910',
                'CRSv3-Science_0003':'1950',
                'CRSv3-Science_0004':'2035',
                'CRSv3-Science_0005':'2115',
                'CRSv3-Science_0006':'2200',
                'CRSv3-Science_0007':'2240',
                'CRSv3-Science_0008':'2325',
                'CRSv3-Science_0009':'0005',
                'CRSv3-Science_0010':'0050'}
elif date == '20230129':
    features = {'CRSv3-Science_0000':'1245',
                'CRSv3-Science_0001':'1330',
                'CRSv3-Science_0002':'1410',
                'CRSv3-Science_0003':'1455',
                'CRSv3-Science_0004':'1535',
                'CRSv3-Science_0005':'1620',
                'CRSv3-Science_0006':'1700',
                'CRSv3-Science_0007':'1745'}
elif date == '20230205':
    features = {'CRSv3-Science_0000':'1245',
                'CRSv3-Science_0001':'1325',
                'CRSv3-Science_0002':'1410',
                'CRSv3-Science_0003':'1450',
                'CRSv3-Science_0004':'1535',
                'CRSv3-Science_0005':'1615',
                'CRSv3-Science_0006':'1700',
                'CRSv3-Science_0007':'1740',
                'CRSv3-Science_0008':'1825',
                'CRSv3-Science_0009':'1905',
                'CRSv3-Science_0010':'1950'}
elif date == '20230212':
    features = {'CRSv3-Science_0001':'1340',
                'CRSv3-Science_0002':'1420',
                'CRSv3-Science_0003':'1505',
                'CRSv3-Science_0004':'1545',
                'CRSv3-Science_0005':'1630',
                'CRSv3-Science_0006':'1710',
                'CRSv3-Science_0007':'1755',
                'CRSv3-Science_0008':'1835',
                'CRSv3-Science_0009':'1920'}
elif date == '20230214':
    features = {'CRSv3-Science_0001':'2220',
                'CRSv3-Science_0002':'2305',
                'CRSv3-Science_0003':'2345',
                'CRSv3-Science_0004':'0030',
                'CRSv3-Science_0005':'0110',
                'CRSv3-Science_0006':'0155',
                'CRSv3-Science_0007':'0235',
                'CRSv3-Science_0008':'0320',
                'CRSv3-Science_0009':'0400'}
elif date == '20230217':
    features = {'CRSv3-Science_0001':'1245',
                'CRSv3-Science_0002':'1325',
                'CRSv3-Science_0003':'1410',
                'CRSv3-Science_0004':'1450',
                'CRSv3-Science_0005':'1535',
                'CRSv3-Science_0006':'1615',
                'CRSv3-Science_0007':'1700',
                'CRSv3-Science_0008':'1740',
                'CRSv3-Science_0009':'1825'}
else:
    print('Date = '+date+' not recognized')
    sys.exit()
    
date_obj = datetime.strptime(date,'%Y%m%d')
#fields = {'dBZe':'CRS_dBZ',
#          'dopplerCorrected':'CRS_vel',
#          'ldr':'CRS_ldr',
#          'specwid':'CRS_sw'}


for file in os.listdir(indir+'/'+date):
    if file.startswith('CRS') and 'CRSv3-Science' in file:
        print(file)
        (base,ext) = os.path.splitext(file)
        (base,junk) = base.split('.')
        (radar,junk,junk,junk,project,ffeature,fnum) = base.split('_')
        ifeature = ffeature+'_'+fnum
        if (date == '20230119' or date == '20230125' or date == '20230214') and features[ifeature] < '1000':
            date_new_obj = date_obj + timedelta(days=1)
            date_new = date_new_obj.strftime('%Y%m%d')
        else:
            date_new = date
        catName = prefix+'.'+date_new+features[ifeature]+'.'+suffix+ext
        shutil.move(indir+'/'+date+'/'+file,
                    outdir+'/'+date+'/'+catName)
        
        
