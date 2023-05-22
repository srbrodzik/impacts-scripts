#!/usr/bin/python3

"""
Created on Tue Oct  1 09:21:18 2019
@author: Sean O'Neil

Generalized on Mon Jan 30 2023.  Inputs are dataframe object with required data and outfile
name and figure title

This script takes in sounding data and produces vertical T and Tw profiles labeled by the 
station ID and datetime.

"""

import os
import sys
import numpy as np
sys.path.append('/home/disk/bob/impacts/bin')

#These next 2 lines allows script to be run from cron without complaining about DISPLAY
#Otherwise, they are unnecessary
#--------------------------------------------------------------------------------------
import matplotlib as mpl
mpl.use('Agg')
#--------------------------------------------------------------------------------------

import matplotlib.pyplot as plt
from wetbulb_AMS import calc_wetbulb_temp
from metpy.units import units

KM2FEET = 3280.84

def plot_wb(df, out_path, out_fname, figtitle, vlim):

    debug = True

    if debug:
        print('FOR WETBULB:')
        print('   out_path  =',out_path)
        print('   out_fname =',out_fname)
        print('   figtitle  =',figtitle)
        print('   vlim      =',vlim)

    # Get wet bulb temperature
    df['wbt'] = df.apply(lambda row: calc_wb(row), axis=1)

    # Create plot
    make_vertical_T_plot(df,out_path,out_fname,figtitle,vlim)
    
def calc_wb(row):
     return calc_wetbulb_temp(row['temperature'],row['dewpoint'],row['pressure'])
    
def make_vertical_T_plot(df,out_path,out_fname,figtitle,vlim):

    #Takes in the sounding data with the calculated wet bulb temperature, vertical boundries for the y-axis, and saves a figure
    #of the vertical temperature with wet bulb profile.
    
    #Gets vectors of the T,Tw,and H variables
    #T = df['temperature'].values * units.degC
    #Tw = df['wbt'].values * units.degC
    #H = df['height'].values * units.m
    T = df['temperature'].values
    Tw = df['wbt'].values
    H = df['height'].values
   
    #Creates the main plotting axis (left)
    fig, axL = plt.subplots()
    
    axL.set_xlabel("Degrees (C)$^\circ$")
    axL.set_ylabel('Height (km)')
    axL.set_ylim(0,int(vlim))
    
    #Plots T and Tw vs H in km
  
    axL.axvline(0,color = 'c', linestyle = 'dashed')
    
    axL.plot(Tw,H/1000.0,'b',linewidth = 2)
    axL.plot(T,H/1000.0,'r',  linewidth = 3)
    
    #Array of zeros for filling the region where T is above freezing
    x=np.zeros(len(T))
    axL.fill_betweenx(H/1000.0,x,T, where= T > x, facecolor = 'lightpink')

    axL.grid()
    
    #Creating the right axis labeled in feet
    axR = axL.twinx()
    axR.set_ylabel('Height (ft\')') 
    axR.set_ylim(0,int(vlim)) #Maintaining the vertical limit to keep both axes equal
    axR.set_yticks(np.arange(0,int(vlim)+1)) #Y ticks corresponding to the left axis (may be changed if the left axis tick marks are specified)
    axR.set_yticklabels(int(np.round(i*KM2FEET)) for i in np.arange(0,int(vlim)+1)) #Converts km into ft and rounds to the nearest foot
    
    #Creates the legend on the left axis plots (ALL)
    axL.legend(["0 C$^\circ$","Wet-Bulb Temperature","Temperature"])
    fig.tight_layout()
    
    #title = 'Sounding for '+site+' at '+date+'/'+time+'Z'
    title = figtitle
    fig.suptitle(title,y=0.99)
    #Saves the figure so no need to return anything
    fig.savefig(out_path+'/'+out_fname)
    
