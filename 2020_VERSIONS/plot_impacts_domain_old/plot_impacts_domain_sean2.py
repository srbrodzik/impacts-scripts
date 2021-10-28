#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  4 13:30:03 2019

@author: broneil
"""

#These next 2 lines allows script to be run from cron without complaining about DISPLAY
#Otherwise, they are unnecessary
#--------------------------------------------------------------------------------------
import matplotlib 
matplotlib.use('Agg') 
#--------------------------------------------------------------------------------------
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects
import numpy as np
import pickle
import geopy.distance 
import os
import scipy
from scipy import stats
import glob
from datetime import datetime
from shutil import copy2
import pandas as pd


plt.rcParams.update({'figure.max_open_warning': 0})

#################GLOBAL###############################
buffer = 25 #The distance between stations which dictates wether the station is displayed 
#Choose the desired field - > 0: Date
#                             1: air_temp_set_1
#                             2: dew_point_temperature_set_1
#                             3: dew_point_temperature_set_1d
#                             4: precip_accumulated_set_1d ->Precip from the beginning of the API grab
#                             5: precip_intervals_set_1d -> Daily accumulated precip
#                             6: sea_level_pressure_set_1
#                             7: sea_level_pressure_set_1d
#                             8: wind_direction_set_1
#                             9: wind_gust_set_1
#                            10: wind_speed_set_1
field = 5 #Should be 5 for Impacts map


#########################################################################
######################       Base Plot           ########################
#########################################################################

#Old extent
#ext = [-88.0, 36.2, -66.5, 48]

ext = [-82.0, 36.2, -66.5, 48]
orig_lat = 42.
orig_lon = -77.

fig = plt.figure(figsize=(16, 12))
bmap = Basemap(epsg=4326, 
               llcrnrlon=ext[0], 
               llcrnrlat=ext[1],
               urcrnrlon=ext[2], 
               urcrnrlat=ext[3],
	           lat_0=orig_lat,lon_0=orig_lon,
               resolution = 'i')

bmap.drawcoastlines()
bmap.drawcountries()
bmap.drawstates()
bmap.shadedrelief()
                        #Lat/Lon Lines
#bmap.drawparallels(np.arange(35,50,.5),labels=[1,0,0,0])
#bmap.drawmeridians(np.arange(-90,-65,5),labels=[0,0,0,1])


#########################################################################
######################           PATHS           ########################
#########################################################################

#Directory of CSV directories ie dates as directories containing CSV data from that date
#date_directory = '/home/disk/funnel/impacts-website/data_archive/asos/*'
date_directory = '/home/disk/p/broneil/Documents/Impacts/ASOS_map/ASOS_CSV/*'
#Name of the saved figure
impacts_domain_figure_name = "Impacts_test_figure.png"
#Directory of plots where dates are directory names of plots that occur that day
directory_of_plots = '/home/disk/p/broneil/Documents/Impacts/ASOS_map/ASOS_plots'
#Directory of most recent plots that will be linked on the website
updated_plots = '/home/disk/p/broneil/public_html/impacts/plots'
#destination of image that gets bashed over
figure_destination = '/home/disk/p/broneil/public_html/impacts/'
# Directory of pickles
pickle_jar = '/home/disk/p/broneil/Documents/Impacts/ASOS_map/pickle_jar/' 
#html plots directory
html_plots = 'https://atmos.uw.edu/~broneil/impacts/plots'

#########################################################################
######################           Functions       ########################
#########################################################################
def load_us():
    ''' Loads in a pickle file dictionary with keys as station identifiers (KSSS) and a list item of station name, state,
        long (float), lat (float), elevation (float) for US ASOS stations.
    '''
    # add ASOS sites
    infile = open(pickle_jar + "ASOS_stations.pkl",'rb')
    ASOS_us = pickle.load(infile)
    infile.close()
    return ASOS_us


def load_ca():
    ''' Loads in a pickle file dictionary with keys as station identifiers (CSSS) and a list item of station name, state,
    long (float), lat (float), elevation (float) for Canadian ASOS stations.
    '''
    #Candadian Stations
    canadafile = open(pickle_jar + "ASOS_canada_stations.pkl",'rb')
    ASOS_ca = pickle.load(canadafile)
    canadafile.close()
    return ASOS_ca


################# SORTING OUT CLOSE STATIONS
def thin_station_density(ASOS):
    '''Loops through the dictionary of ASOS stations and gets the lat/long coordinates of the station.  The function will be passed
       another function which will pop out stations that are within a certain buffer distance (defined gloabally).  International
       airports are the first priority to maintain so the function will maintain any station with "INTL" in the station name.
    '''
    ASOS_final = {} #Creates a new, copy dictionary of ASOS
    ASOS_final.update(ASOS) #ASOS final will have elements popped out of it, so it can't be iterated over it
    for port in ASOS.keys():
        if "INTL" in ASOS[port][0]: #Finds international airports
            intl_long = ASOS[port][2]
            intl_lat = ASOS[port][3]
            coords = [intl_lat,intl_long] 
            ASOS_final = distance_pop(ASOS_final,coords,port)
        else: #Every non international airport
            port_long = ASOS[port][2]
            port_lat = ASOS[port][3]
            coords = [port_lat,port_long]
            ASOS_final = distance_pop(ASOS_final,coords,port)
    
    return ASOS_final


def distance_pop(ASOS,coords,port):
    '''Calculates the distance between two stations in the same dictionary and will pop the stations that are within the 
       buffer distance of 'port'. INTL ports will be preserved even if they are within the buffer distance.
    '''
    for station in list(ASOS.keys()): #Loops through all the stations to compare port with every other station
        station_long = ASOS[station][2]
        station_lat = ASOS[station][3]
        station_coords = [station_lat,station_long] 
        
        distance = geopy.distance.distance(coords,station_coords) #Distance between based in kms
        if distance < buffer and port != station and not "INTL" in ASOS[station][0]: #will only pop non "INTL" port nor pop itself
            ASOS.pop(station)       
    return ASOS


def get_asos_data():
    '''Gets the available ASOS data and outputs a dictionary with station ID "KSSS" or "CSSS" as keys and a list of 11 atmospheric
       fields is the item.
    '''
    list_of_dir = glob.glob(date_directory)  
    Path = max(list_of_dir, key=os.path.getctime)
    Data_Path = Path + '/'    

    filelist = os.listdir(Data_Path) #Gets the files listed in the path directory
    if len(filelist) == 0: #Will exit the function if there is no data in the directory
        print("Latest directory of data files is empty. The script was exited and the figures and map were not updated.")
        return 0
    asos_data = {} #Dictionary to be returned
    for i in filelist: # Loops through the files
        with open(Data_Path + i, 'r') as f:
            df = pd.read_csv(f)
            if field == 5:
                precip_intervals = df.iloc[:,5].dropna()
                daily_accum_precip = float(precip_intervals.sum())
                data = list(df.iloc[-1,:].values)
                data[5] = daily_accum_precip
                
            else:
                data = list(df.iloc[-1,:].values)
                
            asos_data[station] = data #Fills the dictionary
    return asos_data


def plot_ASOS(ASOS):    
    '''Plots ASOS data for sites that have data. The displayed field is selected using the index of desired
       atmospheric field as the field parameter. Returns a list of the asos stations with data.
    '''    
    asos_data = get_asos_data() #Gets the dictionary of asos data
    #will exit the function if there is no new data represented by 0
    if asos_data == 0:
        return 0
    asos_keys = list(asos_data.keys())
    
    #Saves a list of stations ID's for which there is data to be passed to get_pixels4clickbox.py
    #Uncomment if the data keys ever change
    #with open(pickle_jar + "asos_keys.pkl",'wb') as f:
    #    pickle.dump(asos_keys,f,protocol=2)    

    zscores = magnitude_scaling(asos_data)
    for station in asos_keys: #loops through the stations with data    
        try:    
            lon = ASOS[station][2]
            lat = ASOS[station][3]    
    
            if np.all([lat > ext[1],lat < ext[3], lon > ext[0], lon < ext[3]]): #plots only the sites within the domain 
                x, y = bmap(lon,lat)
                plt.plot(x,y,color="red",marker="D",markersize=4,linestyle="None")
                #Faux Snow
                #data_string = str(round(np.random.sample(1)*10 + (np.random.sample(1)+1)*10,1))
                data_point = np.round(float(asos_data[station][field]),1) #Gets the text of the displayed field value
                
                if zscores[station] > 5:
                    zscores[station] = 5
                #Places text centered and above the station
                txt = plt.text(x - .17, y + .1, data_point, weight = 'bold', fontsize = 9.5 + zscores[station] ) 
                #Creates a white outline
                txt.set_path_effects([PathEffects.withStroke(linewidth = 2, foreground = 'w')]) 
                
        except:
            pass
    file_time = datetime.strptime(asos_data[station][0],'%Y-%m-%d %H:%M:%S')
    figtitle = "Precip Accumulation (mm) for %s 00:00 - %s UTC " % (file_time.strftime("%Y-%m-%d"),file_time.strftime("%H:%M"))
    fig.suptitle(figtitle, fontsize = 18, y=.9)
    plt.savefig(impacts_domain_figure_name,bbox_inches = 'tight', pad_inches = 0)
    return asos_keys
    

def magnitude_scaling(asos_data):
    '''Takes in ASOS data, and returns bins corresponding to the text size of station based on the z-score.
    '''
    #List of only digits
    field_values = []
    #List of all values with None in place for NaNs
    all_values = []
    for item in asos_data.items():
        if item[1][field].replace(".","").isdigit() or item[1][field].replace(".","") == "00": #Removes "." so isdigit can find the numbers
            field_values.append(float(item[1][field])) #adds the float value
            all_values.append(float(item[1][field])) 
        else:
            all_values.append(-9999) #Adds to where there are Nans only in all values
    #Calculates the mean of the reported values
    mean = scipy.mean(field_values)
    all_values = np.array(all_values)
    #Fills NaNs with the mean
    indices = np.where(all_values == -9999)[0]
    all_values[indices] = mean
    #Z-scores with NaNs not being affecting
    zscores = stats.zscore(all_values) / 2  
    count = 0 #Iterator for zscores
    zscore_dict = {}
    #Adds in a dictionary of stations to zscore... Otherwise the zscore was not aligning properly when passed back
    for item in asos_data.items():
        zscore_dict[item[0]] = zscores[count]
        count += 1
    return zscore_dict


def keys2list(ASOS):
    '''Takes in a dictionary and outputs the keys as a list and a second list of stations names. The two lists are saved as 
       pickle files.
    '''
    sites = list(ASOS.keys())
    sitenames = [ASOS[site][0] for site in sites]
    
    f = open(pickle_jar + "sitelist.pkl",'wb')
    pickle.dump(sites,f)
    f.close()    
    f2 = open(pickle_jar + 'sitetitles.pkl','wb')
    pickle.dump(sitenames,f2)
    f2.close()
    return sites,sitenames
    

def write_plots2html(sites,ASOS):
    '''Will write most recent plot of each site to an html directory to be called upon by get_pixels4clickbox.py.
       This function will update the plot at the html directory every time the cron runs.
    '''
    #Gets the directory of today
    now = datetime.utcnow()
    date = now.strftime("%Y%m%d")
    for site in sites:
        
        #gets all files of a station in the "today" directory        
        today_directory = directory_of_plots + '/%s/*%s*' % (date, site.lower())
        files = glob.glob(today_directory)
        try:
            latest_file = max(files, key=os.path.getctime) #Finds the file that was last created
            copy2( directory_of_plots + '/%s/%s' % (date, os.path.basename(latest_file)), 
                  updated_plots + '/%s.png' %site )
            copy2( os.getcwd() + "/" + impacts_domain_figure_name, figure_destination + impacts_domain_figure_name )
            write_html_file(site)
        except:
            pass



def write_html_file(site):
        #Writing plots to html
        with open(updated_plots + '/%s.html' %site.lower(), 'w') as f:
            message = """<html>
    <head>
        <title>Real-time Weather Plots</title>
    
    </head>
        <body>"""
            f.write(message)

            message3 = ('        <img src = \"%s/%s.png\" alt=\"3-day\">' %(html_plots,site))
            f.write(message3)
            message4 = """
        </body>
</html>"""
            f.write(message4)





def main():
    ASOS = load_us()
    
    #ASOS_ca = load_ca()
    #ASOS.update(ASOS_ca)

    ASOS = thin_station_density(ASOS) 
    keys2list(ASOS)
    
    asos_keys = plot_ASOS(ASOS)
    #Gracefully exits the script without updating plots
    if asos_keys == 0:
        return
    write_plots2html(asos_keys,ASOS)


main()

