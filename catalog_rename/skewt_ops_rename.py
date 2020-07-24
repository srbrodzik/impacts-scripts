#!/usr/bin/python

import os
import shutil

#plot_type = 'skewt'
plot_type = 'wet_bulb'

if plot_type == 'skewt':
    inDir = '/home/disk/funnel/impacts-website/archive/ops/skewt'
elif plot_type == 'wet_bulb':
    inDir = '/home/disk/funnel/impacts-website/archive/ops/wet_bulb'
else:
    print('Unknown plot_type = '+plot_type+' . . . exiting')
    
outDir = '/home/disk/funnel/impacts-website/archive_ncar/upperair/SkewT'
category_new = 'upperair'
platform_new = 'SkewT'

products = {'ALB':'Albany_NY',
            'APX':'Gaylord_MI',
            'BUF':'Buffalo_NY',
            'CHH':'Chatham_MA',
            'CHS':'Charleston_SC',
            'DTX':'Detroit_MI',
            'DVN':'Davenport_IA',
            'GRB':'Green_Bay_WI',
            'GSO':'Greensboro_NC',
            'GYX':'Gray_ME',
            'IAD':'Sterling_VA',
            'ILN':'Wilmington_OH',
            'ILX':'Lincoln_IL',
            'MHX':'Newport_NC',
            'MPX':'Minneapolis_MN',
            'OKX':'Upton_NY',
            'PIT':'Pittsburgh_PA',
            'RNK':'Blacksburg_VA',
            'WAL':'Wallops_VA'}

for date in os.listdir(inDir):
    if not os.path.isdir(outDir+'/'+date):
        os.mkdir(outDir+'/'+date)
    for file in os.listdir(inDir+'/'+date):
        if plot_type in file:
            print('file = '+file)
            basename = os.path.splitext(file)[0]
            ext = os.path.splitext(file)[1]
            (category,platform,datetime,product) = basename.split('.')
            if plot_type == 'skewt':
                file_new = category_new+'.'+platform_new+'.'+datetime+'.'+products[product]+ext
            elif plot_type == 'wet_bulb':
                file_new = category_new+'.'+platform_new+'.'+datetime+'.'+products[product]+'_Wet_Bulb'+ext
            print('file_new = '+file_new)
            shutil.copy(inDir+'/'+date+'/'+file,
                        outDir+'/'+date+'/'+file_new)
            
