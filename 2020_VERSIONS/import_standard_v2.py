#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 17:52:13 2019

@author: brodzik

ToDo: 
    1. Remove data from previos day
    2. Get first record from next day to get precip total

"""
import sys
import os.path
import pandas as pd
import matplotlib.pyplot as plt
#from pandas import Series, DataFrame

if len(sys.argv) == 2:
    file = sys.argv[1]
else:
    print ('Usage: %s [infile]' % (sys.argv[0]))
    sys.exit()

#%matplotlib

recsPerHr = 12

print ('file = %s' % (file))

#indir = '/home/disk/bob/impacts/bin/data_in'
indir = '/home/disk/data/albany/standard'
outdir = '/home/disk/bob/impacts/bin/data_out'
savedir = '/home/disk/bob/impacts/bin/saved'

#file = '2019-06-30-23:02-latest-all.csv'
#file = '2019-06-30-23:06-latest-all.csv'
#file = '2019-06-30-23:11-latest-all.csv'
date = file[0:4]+file[5:7]+file[8:10]
saved_file = date+'.pkl'

# read new data
data = pd.read_csv(indir+'/'+file)   # To read file as param
#data = pd.read_csv(sys.stdin)       # To read file from stdin

# add column for datetime object
#data.datetime = datetime.strptime(data['time'],'%Y-%m-%d %H:%M:%S UTC')
data['datetime'] = pd.to_datetime(data['time'],format='%Y-%m-%d %H:%M:%S UTC')

# if it exists, open file with previous data for this date
# and merge two data sets and eliminate duplicate records
if os.path.isfile(savedir+'/'+saved_file):
    from_file = pd.read_pickle(savedir+'/'+saved_file)
    from_file = from_file.append(data,ignore_index=True)
    #sorted = from_file.sort_values('time',inplace=True)
    to_file = from_file.drop_duplicates(['station','time'],keep='last')
    to_file = to_file.sort_values(by=['station','time'], ascending=True)
    to_file.to_pickle(savedir+'/'+saved_file)
else:
    data.to_pickle(savedir+'/'+saved_file)

# plotting
# extract data for one site, say BUFF
site = 'BUFF'
site_data = to_file.loc[to_file['station'] == site]
# get last three hours of data (12 records per hour)
site_sub = site_data.tail(3 * recsPerHr)
ax = plt.gca()
site_sub.plot(kind='line',title=site +' - '+date+' - wind speed & dir',x='datetime',y='avg_wind_speed_merge [m/s]',ax=ax)
site_sub.plot(kind='line',secondary_y=True,x='datetime',y='wind_direction_merge [degree]',color='red',ax=ax)
plt.savefig(outdir+'/'+site+'_'+date+'_winds.png')

