#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 09:21:18 2019

@author: Sean O'Neil

This script takes in sounding data from the University of Wyoming atmos website or the mobile sounders of UIUC and produces 
vertical T and Tw profiles labeled by the station ID and datetime. UIUC soundings should be in nc format.

To run from command line:
    python3 vertical_TvsTw.py --file [filename] --outpath [path] (optional- default is current directory) 
"""

import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import argparse
import datetime
from wetbulb import calc_wetbulb_temp

def parse():
    '''Parses the file arguement. 
    '''
    parser = argparse.ArgumentParser(description='Put in a file to be processed')
    #Filename
    parser.add_argument('--file', action='store', dest='file', default="")
    #File format. Available options: html,UIUC, SBU
    parser.add_argument('--fmt', action='store', dest='fmt', default="")
    # where you want to output skewTs
    parser.add_argument('--outpath', action='store', dest='outpath', default='.')
    pargs = parser.parse_args()
    return pargs

def read_html_data(filename):
    '''Reads and parses a html file of vertical thermodynamic variables and outputs an array
       the variables into an array
    '''
    with open(filename, 'r') as fname:
        sounding_data = np.zeros((1,11), dtype = float) #Initial array to be filled
        #Count represents the number of times the first element in a line contains "-".
        #After the second line of only "-", data will be inputted into the array
        count = 0 
        for line in fname: #loops through all the lines in the file
            input_list = line.split() #splits all lines by " ", and inserts all the variables into a list
            first_element = input_list[0] #first element of the input list to be tested for flags
            
            if ("</PRE><H3>") in first_element: #Breaks out of the for loop after all data has looped over
                break 
            
            # Will ignore all lines before the last header of "-" 
            if count == 2:   
                input_float_list = [float(x) for x in input_list] #Converts all input data to floats
                input_array = np.asarray(input_float_list) #Converts the input list to an array for concatenating 
                if np.count_nonzero(sounding_data) == 0 and len(input_array) == 11: # Fills the initial array if it is the first line of data
                    sounding_data = input_array
                elif len(input_array) == 11: #Concatenates the final array with only input arrays that are not missing values                    
                    sounding_data = np.c_[sounding_data, input_array]   
            if "-" in first_element: #Counts the header lines of only "-"
                count += 1
    sounding_data = sounding_data.transpose(1,0)
    sounding_data = sounding_data[0:4]
    return sounding_data

def get_html_title(filename):
    '''Takes in the filename, parses through it to ouput a title string of " 'Station Name' Sounding for 'HH Z' 'yyyy'-'mm'-'dd' "
    '''
    date_string = get_digits(filename)
    station_string = get_uppercase(filename)
    figtitle = str("%s Tw Profile %sZ %s-%s-%s" %
               (station_string,date_string[-4:-2],date_string[-8:-6], date_string[-12:-8], date_string[-6:-4]))
    savetitle = '{stn}.Tw_Profile.{dt}'.format(stn=station_string, dt = "%s%s%s_%sZ" 
                 %(date_string[-8:-6], date_string[-12:-8], date_string[-6:-4],date_string[-4:-2]))
    return figtitle, savetitle

def get_digits(str1):
    '''Gets digits embedded in the string.
    '''
    c = ""
    for i in str1:
        if i.isdigit():
            c += i
    return c

def get_uppercase(str1):
    '''Gets the uppercase letters in a string (station name).
    '''
    u = ""
    for i in str1:
        if i.isupper():
            u += i
    return u

def read_UIUCnc_data(filename):
    '''Uses xarray to parse the nc file and will output an np array of H,P,T, and Td.  Also returns the dataset so the attributes
       can be parsed for title.
    '''
    ds = xr.open_dataset(filename)    
    T = ds['TC'].values
    H = ds['HAGL'].values
    P = ds['PRESS'].values
    RH = ds['RH'].values
    Td = np.array([])
    for i,val in enumerate(T):
        Td = np.append(Td,calculate_dewpoint(T[i],RH[i]))
    sounding_data = np.c_[P,H,T,Td]
    return ds,sounding_data

def get_UIUCnc_title(ds):
    '''Takes in the dataset to parse the location, station id, and date of the sounding for the title.
       Returns the figure title and save title in string format.
    '''
    attrs = ds.attrs
    #Location is outputted in a string of lat and long including words
    location_str = attrs['location']
    location_list = location_str.split()
    lat = float(location_list[0])
    lon = float(location_list[3])
    #Sets the values to negative if in the Western or Southern Hemispere
    if location_list[-1] == 'west':
        lon *= -1
    if location_list[2] == 'south':
        lat *= -1
    stn_id = attrs['institution']
    file_time = datetime.datetime.strptime(attrs['start_datetime'],'%Y-%m-%dT%H:%M:%SZ')
    figtitle = ('{stn} Tw Profile {dt} at ({lati:.3f}, {long:.3f})'
                .format(stn = stn_id, dt = file_time.strftime('%H:%MZ %Y-%m-%d'), lati=lat, long=lon))
    savetitle = '{stn}.Tw_Profile.{dt}.png'.format(stn = stn_id.replace(" ","_"), dt = file_time.strftime('%Y%m%d_%H%MZ'))
    return figtitle, savetitle

def read_SBUnc_data(filename):
    ds = xr.open_dataset(filename)
    #Since the data oscillates, the profile is current until the sensor begins falling
    #which is the first time the derivative of height turns negative
    try:
        end_index = np.where(np.gradient(ds['geometric_height'].values) < 0  )[0][0]
    except:
        end_index = -1
    P = ds['pressure'].values[:end_index]
    H = ds['geometric_height'].values[:end_index]
    T = ds['temperature'].values[:end_index]
    Td = ds['dewpoint_yemperature'].values[:end_index]

    sounding_data = np.c_[P,H,T,Td]
    return ds,sounding_data
    
def get_SBUnc_title(ds):
    attrs = ds.attrs
        
    file_time = datetime.datetime.strptime(attrs['ReleaseTime'],'%Y/%m/%d %H:%M:%S')
    #stn_id = attrs['InputFile'][:3]
    stn_id = 'SBU'
    figtitle = '{stn} Tw Profile {dt}'.format(stn = stn_id, dt = file_time.strftime('%H:%MZ %Y-%m-%d'))
    savetitle = '{stn}.Tw_Profile.{dt}.png'.format(dt = file_time.strftime('%H:%MZ %Y-%m-%d'), stn = stn_id)
    return figtitle,savetitle
    
def calculate_dewpoint(T, RH):
    #Tetens Formual from
    # https://andrewsforest.oregonstate.edu/sites/default/files/lter/data/studies/ms01/dewpt_vpd_calculations.pdf
    x = np.log(RH/100) + ((17.269*T) / (237.3 + T))
    Td = (237.3 * x)/(17.269-x) 
    return Td


def get_wet_bulb(sounding_data):
    '''Takes in an array of the sounding data and calculates Tw from a function provided by Yuler using a form of Tetens equation.  The function returns the sounding data array
       with 12th column being the calculated Tw. 
    '''

    T = sounding_data[:,2] #Gets temperature
    Td = sounding_data[:,3] #Gets dewpoint temperature
    P = sounding_data[:,0] #Gets Pressure
    wbt = np.zeros(np.shape(T))  
    
    for i in np.arange(len(T)): #Iterates by indices based off the length of T
        wbt[i] = calc_wetbulb_temp(T[i],Td[i],P[i])

    return np.c_[sounding_data,wbt] #Final concatenation
    
    
def make_vertical_T_plot(sounding_wb_data,vert_lim,figtitle,savetitle):
    '''Takes in the sounding data with the calculated wet bulb temperature, vertical boundries for the y-axis, figtitle, savetitle and saves a figure
       of the vertical temperature with wet bulb profile.
       
       For freezing levels, just uncomment the section titled "Freezing Levels"
    '''
    #Gets vectors of the T,Tw,and H variables
    T = sounding_wb_data[:,2]
    Tw = sounding_wb_data[:,-1]
    H = sounding_wb_data[:,1]
    #Creates the main plotting axis (left)
    fig, axL = plt.subplots()
    
    axL.set_xlabel("Degrees (C)$^\circ$")
    axL.set_ylabel('Height (km)')
    axL.set_ylim(0,vert_lim) #Sets the vertical limits (THIS MAY HAVE TO BE CHANGED)
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
    axR.set_ylim(0,vert_lim) #Maintaining the vertical limit to keep both axes equal
    axR.set_yticks(np.arange(0,vert_lim+1)) #Y ticks corresponding to the left axis (may be changed if the left axis tick marks are specified)
    axR.set_yticklabels(int(np.round(i*3280.94)) for i in np.arange(0,vert_lim+1)) #Converts km into ft and rounds to the nearest foot
##    #Freezing Levels
#    freezing_level = find_freezing_level(T,H)
#    #Plots as many FL's as necessary in km on the left axis
#    for ii in range(len(freezing_level)):
#        axL.axhline(freezing_level[ii]/1000.0,color ='g',linestyle = 'dashed', label = 'Freezing Level') 

    #Creates the legend on the left axis plots (ALL)
    axL.legend(["0 C$^\circ$","Wet-Bulb Temperature","Temperature"])
    fig.tight_layout()
    #Gets the title and plots it       
    fig.suptitle(figtitle,y=.993)
    #Saves the figure so no need to return anything
    fig.savefig(savetitle)


def find_freezing_level(T,H):
    '''Either finds the freezing level or approximates it if T passes over the value of 0C using a linear interpolation scheme.  Returns 
       an array of freezing level(s).
    '''
    #Checks to see if T ever equals 0
    freezing_level = np.where(T==0)[0]
    
    if len(freezing_level) == 0: #if T passes over 0, then array will be empty
        freezing_crossover = np.where(np.diff(np.sign(T)))[0] #Finds the indices before T changes sign thus passes over 0
        #Iterates over the indices before the T changes sign
        for value in freezing_crossover:
            
            baseline = T[value] #Before sign change for Temperature
            changed_sign_value = T[value + 1] #After signchange  for Temperature 
            
            H_baseline = H[value] #Before signchange  for Height
            H_changed_sign = H[value + 1] #After signchange  for Height
            
            #Linear interpolation of T and H vectors between the two values of where T changes sign
            T_span = np.linspace(baseline,changed_sign_value,100)
            H_span = np.linspace(H_baseline,H_changed_sign,100)
            
            min_value = np.min(np.abs(T_span)) #Takes the value of T closest to 0
            min_index = np.where(T_span==min_value)[0] #Finds the index of T closest to 0
            
            if len(freezing_level) == 0: 
                freezing_level = H_span[min_index] #Sets the freezing level to the height that corresponds to T being closest to 0
            else:
                freezing_level = np.append(freezing_level,H_span[min_index]) # Same as above if second or more time through loop
            
    else:
        freezing_level = H[freezing_level] # Height level if T is recorded at 0
    return freezing_level


def main():
    pargs = parse()
    filename = pargs.file
    fmt = pargs.fmt
    #Gets data from html format
    if "html" in fmt.lower():    
        sounding_data = read_html_data(filename)
        figtitle,savetitle = get_html_title(filename)
    #Gets data from UIUC format
    elif  "UIUC" in fmt.upper():
        ds, sounding_data = read_UIUCnc_data(filename)
        figtitle,savetitle = get_UIUCnc_title(ds)
    #Gets data from SBU format
    elif "SBU" in fmt.upper(): 
        ds, sounding_data = read_SBUnc_data(filename)
        figtitle,savetitle = get_SBUnc_title(ds)
    #Takes in the case where no file is given and exits before crashing
    elif filename == "":
        print("No file given.")
        return
    #Adds a column of Tw to the array
    sounding_wb_data = get_wet_bulb(sounding_data)
    #Takes the vertical limit of the y axis in km
    vert_lim = 7
    make_vertical_T_plot(sounding_wb_data,vert_lim,figtitle,savetitle)
   
main()