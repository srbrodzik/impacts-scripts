#!/usr/bin/python

"""
Created on Tue Oct  1 09:21:18 2019

@author: Sean O'Neil

This script takes in sounding data from the University of Wyoming atmos website and produces 
vertical T and Tw profiles labeled by the station ID and datetime.

"""

import os
import sys
import numpy as np
# These next 2 lines allows script to be run from cron without complaining about DISPLAY
# Otherwise, they are unnecessary
#--------------------------------------------------------------------------------------
import matplotlib as mpl
mpl.use('Agg')
#--------------------------------------------------------------------------------------
import matplotlib.pyplot as plt

KM2FEET = 3280.84

def read_in_data(filename):
    '''
    Read and parse an html file of vertical thermodynamic variables and output
    the variables into an array
    '''
    with open(filename, 'r') as fname:

        # Initial array to be filled
        sounding_data = np.zeros((1,11), dtype = float) 
        # Count represents the number of times the first element in a line contains "-".
        # After the second line of only "-", data will be inputted into the array
        count = 0

        # Loops through all lines in file
        for line in fname: 
            
            # Split all lines by " ", and insert all the variables into a list
            input_list = line.split() 

            # First element of the input list to be tested for flags
            first_element = input_list[0] 

            # Break out of for loop after all data has looped over
            if ("</PRE><H3>") in first_element: 
                break 
            
            # Will ignore all lines before the last header of "-" 
            if count == 2: 

                # Convert all input data to floats
                input_float_list = [float(x) for x in input_list]
                
                # Convert input list to an array for concatenating 
                input_array = np.asarray(input_float_list) 

                # Fill initial array if it is the first line of data
                if np.count_nonzero(sounding_data) == 0 and len(input_array) == 11: 
                    sounding_data = input_array
                # Concatenate final array with only input arrays that are not missing values
                elif len(input_array) == 11: 
                    sounding_data = np.c_[sounding_data, input_array]

            # Count the header lines of only "-"
            if "-" in first_element: 
                count += 1

    sounding_data = sounding_data.transpose(1,0)

    return sounding_data


def get_wet_bulb(sounding_data):
    '''
    Take in an array of sounding data and calculate Tw from a function provided 
    by Yuler using a form of Tetens equation.  The function returns the sounding 
    data array with 12th column being the calculated Tw. 
    '''
    from wetbulb_AMS import calc_wetbulb_temp

    # Get temperature, dewpoint temperature and pressure
    T = sounding_data[:,2]
    Td = sounding_data[:,3]
    P = sounding_data[:,0]
    wbt = np.zeros(np.shape(T))  

    # Iterate by indices based off length of T
    for i in np.arange(len(T)): 
        wbt[i] = calc_wetbulb_temp(T[i],Td[i],P[i])

    # Final concatenation
    return np.c_[sounding_data,wbt] 
    
    
def make_vertical_T_plot(sounding_wb_data,vert_lim,filename,outfile):

    '''
    Take in sounding data with calculated wet bulb temperature, vertical boundries for 
    the y-axis, and save a figure of vertical temperature with wet bulb profile.
    '''
    # Get vectors of the T,Tw,and H variables
    T = sounding_wb_data[:,2]
    Tw = sounding_wb_data[:,11]
    H = sounding_wb_data[:,1]
    
    # Create main plotting axis (left)
    fig, axL = plt.subplots()
    
    axL.set_xlabel("Degrees (C)$^\circ$")
    axL.set_ylabel('Height (km)')
    # Set vertical limits (THIS MAY HAVE TO BE CHANGED)
    axL.set_ylim(0,int(vert_lim)) 
    
    # Plot T and Tw vs H in km
    axL.axvline(0,color = 'c', linestyle = 'dashed')
    
    axL.plot(Tw,H/1000.0,'b',linewidth = 2)
    axL.plot(T,H/1000.0,'r',  linewidth = 3)
    
    # Array of zeros for filling region where T is above freezing
    x=np.zeros(len(T))
    axL.fill_betweenx(H/1000.0,x,T, where= T > x, facecolor = 'lightpink')

    axL.grid()
    
    # Create right axis labeled in feet
    axR = axL.twinx()
    axR.set_ylabel('Height (ft\')')
    # Maintain vertical limit to keep both axes equal
    axR.set_ylim(0,int(vert_lim))
    # Y ticks corresponding to the left axis (may be changed if the left axis tick
    # marks are specified)
    axR.set_yticks(np.arange(0,int(vert_lim)+1))
    # Convert km into ft and round to the nearest foot
    axR.set_yticklabels(int(np.round(i*KM2FEET)) for i in np.arange(0,int(vert_lim)+1)) 
    
    '''Multi line comment
    #Gets the freezing level or levels
    freezing_level = find_freezing_level(T,H)
    #Plots as many FL's as necessary in km on the left axis
    for ii in range(len(freezing_level)):
        axL.axhline(freezing_level[ii]/1000.0,color ='g',linestyle = 'dashed', label = 'Freezing Level') 
    '''
    
    # Creates legend on left axis plots (ALL)
    axL.legend(["0 C$^\circ$","Wet-Bulb Temperature","Temperature"])
    fig.tight_layout()
    
    # Get title and plot it
    # Assume filename is of form ops.text_sounding.YYYYMMDDhhmm.<site>.html
    base = os.path.basename(outfile)
    parts = base.split('.')
    dtg = parts[2]
    date = dtg[0:8]
    time = dtg[8:]
    site = parts[3]
    title = 'Sounding for '+site+' at '+date+'/'+time+'Z'
    fig.suptitle(title,y=0.99)
    # Save figure so no need to return anything
    fig.savefig(outfile)


def find_freezing_level(T,H):
    '''
    Either find freezing level or approximate it if T passes over the value 
    of 0C using a linear interpolation scheme.  Return an array of freezing level(s).
    '''
    # Check to see if T ever equals 0
    freezing_level = np.where(T==0)[0]

    #if T passes over 0, then array will be empty
    if len(freezing_level) == 0:
        # Find indices before T changes sign thus passes over 0
        freezing_crossover = np.where(np.diff(np.sign(T)))[0]
        
        # Iterate over indices before the T changes sign
        for value in freezing_crossover:

            # Before sign change for Temperature
            baseline = T[value]
            # After signchange  for Temperature 
            changed_sign_value = T[value + 1] 

            # Before signchange  for Height
            H_baseline = H[value]
            # After signchange  for Height
            H_changed_sign = H[value + 1] 
            
            # Linear interpolation of T and H vectors between the two values of where
            # T changes sign
            T_span = np.linspace(baseline,changed_sign_value,100)
            H_span = np.linspace(H_baseline,H_changed_sign,100)

            #Take value of T closest to 0
            min_value = np.min(np.abs(T_span))
            # Find index of T closest to 0
            min_index = np.where(T_span==min_value)[0] 
            
            if len(freezing_level) == 0:
                # Set freezing level to height that corresponds to T being closest to 0
                freezing_level = H_span[min_index] 
            else:
                # Same as above if second or more time through loop
                freezing_level = np.append(freezing_level,H_span[min_index]) 
            
    else:
        # Height level if T is recorded at 0
        freezing_level = H[freezing_level] 
    
    return freezing_level


def get_title(filename):
    '''
    Take in filename and parse through it to ouput a title string of 
    " 'Station Name' Sounding for 'HH Z' 'mm'-'dd'-'yyyy' "
    '''
    date_string = get_digits(filename)
    station_string = get_uppercase(filename)
    return str("%s Souding for %sZ %s-%s-%s" %
               (station_string,date_string[-4:-2],date_string[-8:-6], date_string[-6:-4],date_string[-12:-8]))
    
    
def get_digits(str1):
    '''
    Get digits embedded in string.
    '''
    c = ""
    for i in str1:
        if i.isdigit():
            c += i
    return c


def get_uppercase(str1):
    '''
    Get uppercase letters in string (station name).
    '''
    u = ""
    for i in str1:
        if i.isupper():
            u += i
    return u


def main():
    # Check for correct input arguments
    if len(sys.argv) != 4:
        raise SystemExit("Useage: {} {} {}".format(sys.argv[0],
                                                   "[infile]", "[outfile] [vert_lim]"))
    filename = sys.argv[1]
    outfile = sys.argv[2]
    vert_lim = sys.argv[3]

    sounding_data = read_in_data(filename)
    sounding_wb_data = get_wet_bulb(sounding_data)
    
    make_vertical_T_plot(sounding_wb_data,vert_lim,filename,outfile)
   
main()
