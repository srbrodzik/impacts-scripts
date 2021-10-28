#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 09:21:18 2019

@author: Sean O'Neil

This script takes in sounding data from the University of Wyoming atmos website and produces 
vertical T and Tw profiles labeled by the station ID and datetime.

"""

import os
import numpy as np
import matplotlib.pyplot as plt

def read_in_data(filename):
    '''Reads and parses a html file of vertical thermodynamic variables and outputs an array
       the variables into an array
    '''
    with open(filename, 'r') as fname:
        
        sounding_data = np.zeros((1,11), dtype = float) #Initial array to be filled
        #Count represents the number of times the first element in a line contains "-".
        #After the second line of only "-", data will be inputted into the array
        count = 0 
        for line in fname: #loops through all the lines in the file

            print 'line = ',line
            
            input_list = line.split() #splits all lines by " ", and inserts all the variables into a list
            
            first_element = input_list[0] #first element of the input list to be tested for flags
            
            if ("</PRE><H3>") in first_element: #Breaks out of the for loop after all data has looped over
                break 
            
            # Will ignore all lines before the last header of "-" 
            if count == 2: 
                
                input_float_list = [float(x) for x in input_list] #Converts all input data to floats
                input_array = np.asarray(input_float_list) #Converts the input list to an array for concatenating 
                print 'len(input_array) = ',len(input_array)
                
                if np.count_nonzero(sounding_data) == 0 and len(input_array) == 11: # Fills the initial array if it is the first line of data
                    sounding_data = input_array
                elif len(input_array) == 11: #Concatenates the final array with only input arrays that are not missing values                    
                    sounding_data = np.c_[sounding_data, input_array]
                    
                    
            if "-" in first_element: #Counts the header lines of only "-"
                count += 1

    sounding_data = sounding_data.transpose(1,0)

    return sounding_data

def get_wet_bulb(sounding_data):
    '''Takes in an array of the sounding data and calculates Tw from a function provided by Yuler using a form of Tetens equation.  The function returns the sounding data array
       with 12th column being the calculated Tw. 
    '''
    from wetbulb_AMS import calc_wetbulb_temp
    T = sounding_data[:,2] #Gets temperature
    Td = sounding_data[:,3] #Gets dewpoint temperature
    P = sounding_data[:,0] #Gets Pressure
    wbt = np.zeros(np.shape(T))  
    
    for i in np.arange(len(T)): #Iterates by indices based off the length of T
        wbt[i] = calc_wetbulb_temp(T[i],Td[i],P[i])

    return np.c_[sounding_data,wbt] #Final concatenation
    
    
def make_vertical_T_plot(sounding_wb_data,vert_lim,filename):
    '''Takes in the sounding data with the calculated wet bulb temperature, vertical boundries for the y-axis, and saves a figure
       of the vertical temperature with wet bulb profile.
    '''
    
    #Gets vectors of the T,Tw,and H variables
    T = sounding_wb_data[:,2]
    Tw = sounding_wb_data[:,11]
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
    
    ''' Multi line comment
    #Gets the freezing level or levels
    freezing_level = find_freezing_level(T,H)
    #Plots as many FL's as necessary in km on the left axis
    for ii in range(len(freezing_level)):
        axL.axhline(freezing_level[ii]/1000.0,color ='g',linestyle = 'dashed', label = 'Freezing Level') 
    '''
    #Creates the legend on the left axis plots (ALL)
    axL.legend(["0 C$^\circ$","Wet-Bulb Temperature","Temperature"])
    fig.tight_layout()
    
    #Gets the title and plots it    
    title = get_title(filename)
    print title
    fig.suptitle(title,y=0.99)
    #Saves the figure so no need to return anything
    fig.savefig(title)
    
    


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

def get_title(filename):
    '''Takes in the filename, parses through it to ouput a title string of " 'Station Name' Sounding for 'HH Z' 'mm'-'dd'-'yyyy' "
    '''
    date_string = get_digits(filename)
    station_string = get_uppercase(filename)
    return str("%s Souding for %sZ %s-%s-%s" %
               (station_string,date_string[-4:-2],date_string[-8:-6], date_string[-6:-4],date_string[-12:-8]))
    
    
    
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


def main():
    filename = "/home/disk/bob/impacts/bin/ops.text_sounding.201910040000.PIT2.html"
    #filename = "ops.text_sounding.201910040000.PIT.html"
    sounding_data = read_in_data(filename)
    sounding_wb_data = get_wet_bulb(sounding_data)
    
    make_vertical_T_plot(sounding_wb_data,7,filename)
   
main()
