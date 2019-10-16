#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 17:25:40 2019

@author: brodzik
"""

import pandas as pd
from pandas import Series, DataFrame

# Series

obj = Series([4,7,-5,3])
#print obj
#print obj.values
#print obj.index

obj2 = Series([4,7,-5,3], index=['d','b','a','c'])
#print 'obj2[a] = ',obj2['a']
obj2['d'] = 6
#print 'obj2[c,a,d] = \n',obj2[['c','a','d']]
#print 'obj2 > 0 = \n',obj2[obj2 > 0]

sdata = {'Ohio':35000, 'Texas':71000, 'Oregon':16000, 'Utah':5000}
obj3 = Series(sdata)
#print 'obj3 = \n',obj3

states = ['California', 'Ohio', 'Oregon', 'Texas']
obj4 = Series(sdata, index=states)
#print 'obj4 = \n',obj4
#print 'pd.notnull(obj4) = \n', pd.notnull(obj4)
#print 'obj3 + obj4 = \n',obj3+obj4

obj4.name = 'population'
obj4.index.name = 'state'
#print 'obj4 = \n',obj4

# DataFrame

data = {'state':['Ohio','Ohio','Ohio','Nevada','Nevada'],
        'year':[2000,2001,2002,2001,2002],
        'pop':[1.5,1.7,3.6,2.4,2.9]}
frame = DataFrame(data)
print 'frame = \n',frame
print 'DataFrame(data,columns=[year,state,pop]) = \n',DataFrame(data,columns=['year','state','pop'])

frame2 = DataFrame