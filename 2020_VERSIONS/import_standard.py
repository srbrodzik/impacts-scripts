#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 17:52:13 2019

@author: brodzik
"""

import os.path
import pandas as pd
#from pandas import Series, DataFrame

indir = '/home/disk/bob/impacts/bin/data_in'
savedir = '/home/disk/bob/impacts/bin/saved'

#file = '2019-06-30-23:02-latest-sub.csv'
#file = '2019-06-30-23:06-latest-sub.csv'
file = '2019-06-30-23:11-latest-sub.csv'
date = file[0:4]+file[5:7]+file[8:10]
saved_file = date+'.pkl'

# read new data
data = pd.read_csv(indir+'/'+file)

# if it exists, open file with previous data for this date
# and merge two data sets and eliminate duplicate records
if os.path.isfile(savedir+'/'+saved_file):
    print saved_file,' exists\n'
    from_file = pd.read_pickle(savedir+'/'+saved_file)
    from_file = from_file.append(data,ignore_index=True)
    #sorted = from_file.sort_values('time',inplace=True)
    to_file = from_file.drop_duplicates('time',keep='last')
    
# save data to pickle file
to_file.to_pickle(savedir+'/'+saved_file)


