#!/usr/bin/python3

"""
Created August/September 2019
@author: masonf3
Modified January 2020
@author: Joe Finlon
Modified May 2020
@author: Stacy Brodzik

Original code named: NYS_mesonet_save_and_plot.py
Make 3-day plots and save daily .csv files of key weather variables for NYS mesonet stations (126 stations in network)
Data is read from UW Atmospheric Sciences LDM server
Some code modified from Joe Zagrodnik's 'plot_mesowest_3day.py', used for similar task in the OLYMPEX field campaign

Newest version of code split into two parts -- NYS_mesonet_save.py and NYS_mesonet_plot.py

**File Saving Information for current code**
3-day plots, one each time code is run, save to: '/home/disk/funnel/impacts/archive/ops/nys_ground'
"""

import os
import pandas as pd 
import csv 
from datetime import datetime, timedelta
import numpy as np 
import matplotlib 
from matplotlib.dates import DayLocator, HourLocator, DateFormatter
matplotlib.use('Agg') 
import matplotlib.transforms as transforms
from matplotlib.cbook import get_sample_data
import matplotlib.pyplot as plt
import gc

### SUBROUTINES ###

def trim_data(csv_data):
    '''
    Removes duplicates and trims data to latest 3 days for plotting.
    '''
    csv_data
    csv_data_unique = csv_data_dt.loc[~site_data_dt.index.duplicated(keep='last')] # remove duplicate times
    
def Tmv_calc(e, p, Tm):
    '''Given current vapor pressure, station pressure, & mean 12-hour temp, returns mean 12-hour virtual temp.
    Eq. from Ch.3 of "Atmospheric Science, An Introductory Survey, Second Edition" by John M. Wallace and Peter V. Hobbs
    
    Parameters:
    Tm (float): mean 12-hour temp, in degrees celsius (i.e. (T_now+T_12ago)/2) 
    e (float): vapor pressure, in (find out)
    p (float): station pressure (2m to be exact), in hPa (check this?)
    
    Returns:
    Tv_bar (float): average virtual temperature, in degrees kelvin
    '''
    Tmv = (Tm+273.15)/(1-((e/p)*(1-0.622)))
    return Tmv

def mslp_calc(Tmv, zs, p):
    '''Given current station elevation, station pressure, and mean 12-hour virtual temp, returns mean sea-level pressure.
    Eq. from Ch.3 of "Atmospheric Science, An Introductory Survey, Second Edition" by John M. Wallace and Peter V. Hobbs
    
    *Note: MSLP calculations will be slightly incorrect for the very first 12 hours of data ever read by this script 
    because calculations use 12 hour average ambient temperature in their formulation. 
    
    Parameters:
    Tmv (float): mean 12-hour virtual temp, in degrees kelvin
    zs (float): station elevation, in meters
    p (float): station pressure, in hPa
    
    Returns:
    p0 (float): mean sea-level pressure, in hPa (mb)
    '''
    g = 9.80665                          #acceleration of gravity in m*s^-2
    Rd = 287.0                           #gas constant of dry air in J*K^-1*kg^-1
    z = zs + 2                           #true elevation, in m (temp is taken at 2-m)
    p0 = p*np.exp((g*(z+2))/(Rd*Tmv))
    return p0

def plot_station_data(site, dt, time_start, time_end, site_data, logo_path):
    '''Given a pandas dataframe containing all weather data for a specific station, this function saves a plot with
    the last 3 days worth of weather data for that station (or as much data as available if not yet 3-days). 
    
    Parameters:
    site: 4 letter site identifier
    dt: dataframe contain all datetimes being plotted
    time_start: first datetime in dt; redundant
    time_end: last datetime in dt; redundant
    site_data (dataframe): pandas df containing all site data for 3 days to be plotted
    logo_path: path to png file containing NYS Mesonet logo
    
    Returns:
    Saves plots to plot_dir listed near top of MAIN CODE*
    plot_dir = '/home/disk/funnel/impacts/archive/ops/nys_ground_qc'
    '''
    
    time_start_string = datetime.strftime(time_start, '%H UTC %m/%d/%y')
    time_end_string = datetime.strftime(time_end, '%H UTC %m/%d/%y')
    markersize = 1.5                                        #markersize, for subplots
    linewidth = 1.5 #linewidth, for subplots
    fig = plt.figure() #create figure
    fig.set_size_inches(10, 10) #size figure
    
    ax1 = fig.add_subplot(6, 1, 1)
    ax2 = fig.add_subplot(6, 1, 2, sharex=ax1)
    ax3 = fig.add_subplot(6, 1, 3, sharex=ax1)
    ax4 = fig.add_subplot(6, 1, 4, sharex=ax1)
    ax5 = fig.add_subplot(6, 1, 5, sharex=ax1)
    ax6 = fig.add_subplot(6, 1, 6, sharex=ax1)                       
    
    ax1.set_title('{}, NY ({}) Meteogram\n{} - {}'.format(site_data['name'][0], site,
                                                           time_start_string, time_end_string), fontsize=16)
    #plot airT and dewT
    if 'temp_2m [degC]' in site_data.keys():
        airT = site_data['temp_2m [degC]']
        ax1.plot_date(dt, airT, 'o-', label="Temp", color="red", linewidth=linewidth, markersize=markersize)
        ax1.set_xlim(time_start, time_end)
    if 'dew_point_temp_2m [degC]' in site_data.keys():
        Td = site_data['dew_point_temp_2m [degC]']
        ax1.plot_date(dt,Td,'o-',label="Dew Point",color="forestgreen",linewidth=linewidth,markersize=markersize)
        # REDUNDANT??
        #ax1.set_xlim(time_start, time_end)
    # draw 0 degC line if y limits go from negative to positive values
    if ax1.get_ylim()[0] < 0 < ax1.get_ylim()[1]:
        ax1.axhline(0, linestyle='-', linewidth = 1.0, color='deepskyblue')
        # USED FOR PLACING TEXT THAT WE DON'T NEED - drawing '0 degC' in light blue on y axis
        ##trans = transforms.blended_transform_factory(ax1.get_yticklabels()[0].get_transform(), ax1.transData)
        ##ax1.text(0, 0, '0$^\circ$C', color="deepskyblue", transform=trans, ha="right", va="center") #light blue line at 0 degrees C
    ax1.set_ylabel('2-m Temp ($^\circ$C)')
    ax1.legend(loc='best', ncol=2)
    axes = [ax1]                                                #begin axes list

    #plot wind speed and gust
    if 'avg_wind_speed_merge [m/s]' in site_data.keys():
        wnd_spd = site_data['avg_wind_speed_merge [m/s]'] * 1.94384 #convert to knots
        ax2.plot_date(dt,wnd_spd,'o-',label='Speed',color="black",linewidth=linewidth,markersize=markersize)
    if 'max_wind_speed_merge [m/s]' in site_data.keys():
        wnd_gst = site_data['max_wind_speed_merge [m/s]'] * 1.94384 #convert to knots
        max_wnd_gst = wnd_gst.max(skipna=True)
        ax2.plot_date(dt,wnd_gst,'o-',label='Gust [Max=' + str(round(max_wnd_gst,1)) + ' kt]',color="blue",linewidth=linewidth,markersize=markersize)
    ax2.set_ylabel('Wind (kt)')
    ax2.legend(loc='best',ncol=2)
    axes.append(ax2)
    
    #plot wind direction
    if 'wind_direction_merge [degree]' in site_data.keys():
        wnd_dir = site_data['wind_direction_merge [degree]']
        ax3.plot_date(dt,wnd_dir,'o-',label='Direction',color="purple",linewidth=0.2, markersize=markersize)
    ax3.set_ylim(-10,370)
    ax3.set_ylabel('Wind Direction')
    ax3.set_yticks([0,90,180,270,360])                          #locking y-ticks for wind direction 
    axes.append(ax3)
    
    #plot MSLP (or station pressure, if MSLP unavailable)
    if 'mean_sea_level_pressure [mbar]' in site_data.keys():
        mslp = site_data['mean_sea_level_pressure [mbar]']
        min_mslp = mslp.min(skipna=True)                        #min 3-day mslp value
        max_mslp = mslp.max(skipna=True)                        #max 3-day mslp value
        labelname = 'Min=' + str(round(min_mslp,1)) + ' | Max=' + str(round(max_mslp,1)) + ' hPa'
        ax4.plot_date(dt,mslp,'o-',label=labelname,color='darkorange',linewidth=linewidth,markersize=markersize)
        ax4.set_ylabel('MSLP (hPa)')
    elif 'station_pressure [mbar]' in site_data.keys():                                                   
        sp = site_data['station_pressure [mbar]']
        min_sp = sp.min(skipna=True)                            #min 3-day station pressure value
        max_sp = sp.max(skipna=True)                            #max 3-day station pressure value
        labelname = 'Min=' + str(round(min_sp,1)) + ' | Max=' + str(round(max_sp,1)) + ' hPa'
        ax4.plot_date(dt,sp,'o-',label=labelname,color='darkorange',linewidth=linewidth,markersize=markersize)
        ax4.set_ylabel('Station Pressure (hPa)')
        print('unable to get mslp, used station pressure instead')
    ax4.legend(loc='best')
    axes.append(ax4)

    #plot precip accum
    if 'precip_incremental [mm]' in site_data.keys():
        precip_inc = site_data['precip_incremental [mm]']
        precip_accum = np.nancumsum(precip_inc)
        labelname = 'Max=' + str(round(precip_accum[-1],2)) + ' mm'
        ax5.plot_date(dt,precip_accum,'o-',label=labelname,color='navy',linewidth=linewidth,markersize=markersize)
        if precip_accum[-1] > 0:
            ax5.set_ylim(0,precip_accum[-1]*1.2)
        else:
            ax5.set_ylim(0, 1)
    ax5.legend(loc='best')
    ax5.set_ylabel('Precip (mm)')
    axes.append(ax5)
    
    #plot snow depth
    if 'snow_depth [cm]' in site_data.keys():
        snow_depth_mm = site_data['snow_depth [cm]'] * 10         #convert to mm
        max_snow_depth_mm = snow_depth_mm.max(skipna=True)
        min_snow_depth_mm = snow_depth_mm.min(skipna=True)
        labelname = 'Min=' + str(round(min_snow_depth_mm,2)) + ' | Max=' + str(round(max_snow_depth_mm,2)) + ' mm'
        ax6.plot_date(dt,snow_depth_mm,'o-',label=labelname,color='deepskyblue',linewidth=linewidth,markersize=markersize)
        if max_snow_depth_mm > 0:
            ax6.set_ylim(-0.1*max_snow_depth_mm,max_snow_depth_mm*1.2)
        else:
            ax6.set_ylim(0, 1)
        ax6.legend(loc='best')
        ax6.set_ylabel('Snow Depth (mm)')
        axes.append(ax6)
                        
    for item, ax in enumerate(axes):
        # remove dark borders on all subplots except bottom border
        ax.spines["top"].set_visible(False)                             
        ax.spines["right"].set_visible(False)  
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_visible(True)

        # set x & y axis params
        ax.tick_params(axis='both', which='major', length=8)
        ax.tick_params(axis='both', which='minor', length=4)        
        ax.xaxis.set_major_locator( DayLocator() )                      #one date written per day
        ax.xaxis.set_major_formatter( DateFormatter('%b-%d') )          #show date, written as 'Jul-12'
        ax.xaxis.set_minor_locator( HourLocator(np.linspace(3,21,7)) )  #hour labels every 3 hours
        ax.xaxis.set_minor_formatter( DateFormatter('%H') )             #show hour labels
        ax.yaxis.grid(linestyle = '--')                                 #adds y-axis grid lines
        ax.get_yaxis().set_label_coords(-0.06,0.5)                      #properly places y-labels away from figure
        
    # Add mesonet logo
    fig.subplots_adjust(bottom=0.1,left=.05,right=1.1)
    im = plt.imread(get_sample_data(logo_path))
    new_ax = fig.add_axes([1, 0, 0.1, 0.1])
    new_ax.imshow(im)
    new_ax.axis('off')

    # Get warning on next line:
    # "This figure includes Axes that are not compatible with tight_layout, so results might be incorrect."
    plt.tight_layout()
    
    # Save the plot
    plot_path = plot_dir + '/' + current_date_string
    if not os.path.exists(plot_path):
        os.mkdir(plot_path)
    plt.savefig(plot_path + '/ops.nys_ground.' + current_dt_filestring + '.' + site.lower() + '.png', bbox_inches='tight')
    plt.clf(), plt.cla(), plt.close()

### MAIN CODE ###

# set paths
working_dir = os.getcwd() # current working directory
# file containing lat/lon/alt of stations to plot
station_file = '/home/disk/funnel/impacts/data_archive/nys_ground_QC/meta_nysm_catalog.csv'
# directory for daily, site-specific CSV data
csv_dir = '/home/disk/funnel/impacts/data_archive/nys_ground_QC'
# save plots here
plot_dir = '/home/disk/funnel/impacts/archive/ops/nys_ground_qc'
logo_path = '/home/disk/bob/impacts/bin/NYS_mesonet/NYSM_logo_96x96.png'

# read station names and info
station_info_data = pd.read_csv(station_file) # read station info from .csv file
station_info_data = station_info_data.set_index('stid') # index by station id
station_list = list(station_info_data.index)

# get current date and time and list of dates to plot
# FOR REAL TIME USE
#current_dt = datetime.utcnow()
# FOR TESTING
#current_dt = datetime(2020,1,5,18,20)
#current_dt = datetime(2020,2,25,1,5)

#for month in range(1,2):  # January
for month in range(2,3):   # February
    #for day in range(4,32):  # January
    for day in range(1,30):  # February
        for hour in range(0,24):
            current_dt = datetime(2020,month,day,hour,5)
            print(current_dt)
            
            current_dt = current_dt.replace(minute=0, second=0, microsecond=0)
            current_dt_string = datetime.strftime(current_dt, '%Y%m%d%H')
            current_dt_filestring = datetime.strftime(current_dt, '%Y%m%d%H%M')
            current_date_string = datetime.strftime(current_dt, '%Y%m%d')
            current_date_obj = datetime.strptime(current_date_string,'%Y%m%d')
            date_list = []
            for idate in range(0,4):
                date_list.append( (current_date_obj-timedelta(hours=24*idate)).strftime('%Y%m%d') )
            date_list.sort()

            for site in station_list:  # use site = station_list[4] for testing

                print(site)
                station_string = site.lower()

                # get csv site data for dates in date_list
                csv_files = [csv_dir+'/'+date+'/ops.nys_ground.'+date+'.'+station_string+'.csv' for date in date_list]
                # FOR TESTING
                #csv_files = ['/home/disk/funnel/impacts/data_archive/nys_ground_QC/20200222/ops.nys_ground.20200222.buff.csv',
                #             '/home/disk/funnel/impacts/data_archive/nys_ground_QC/20200223/ops.nys_ground.20200223.buff.csv',
                #             '/home/disk/funnel/impacts/data_archive/nys_ground_QC/20200224/ops.nys_ground.20200224.buff.csv',
                #             '/home/disk/funnel/impacts/data_archive/nys_ground_QC/20200225/ops.nys_ground.20200225.buff_test.csv']
                data = pd.concat((pd.read_csv(file) for file in csv_files)) # merge data into one dataframe object for processing
                data_dt = data.set_index('datetime') # set new data index to datetime
                data_unique = data_dt.loc[~data_dt.index.duplicated(keep='last')].copy(deep=True) # remove duplicate times
                data_unique['datetime'] = pd.to_datetime(data_unique.index, format='%Y-%m-%d %H:%M:%S') # get datetime objects
                data_unique = data_unique.set_index('datetime') # set new data index to datetime

                last_time = current_dt
                first_time = current_dt - timedelta(hours=72)
                    
                data_temp = data_unique.loc[data_unique.index > first_time]
                data_3day = data_temp.loc[data_temp.index <= last_time]
                #data_3day = data_unique.loc[data_unique.index > (data_unique.index[-1]-timedelta(hours=72))] # time indices w/i past 72 hrs
                    
                dt = data_3day.index
                time_start = dt[0] # first datapoint is HH:55...start plotting at HH+1:00
                # NO LONGER NEED TO KLUDGE THIS SINCE CSV FILES ARE CORRECT
                #time_end = dt[-1] + timedelta(minutes=5) # last datapoint is HH:55...end plotting at HH+1:00
                time_end = dt[-1]
    
                # Calculate MSLP using mean from past 12 hours and add to data_3day dataframe
                # CAN WE DO THIS WITHOUT for LOOP?
                # Causes SettingWithCopyWarning warning
                data_3day['mean_sea_level_pressure [mbar]'] = np.nan
                for ob_dt in data_3day.index[:]:
                    temp_mean = np.nanmean(data_unique.loc[data_unique.index >
                                                               (ob_dt-timedelta(hours=12))]['temp_2m [degC]'].values)
                    Tv_mean =  Tmv_calc(data_3day['vapor_pressure [mbar]'][ob_dt],
                                        data_3day['station_pressure [mbar]'][ob_dt], temp_mean) # calc average virtual temp
                    mslp = mslp_calc(Tv_mean, data_3day['station_elevation [m]'][ob_dt], data_3day['station_pressure [mbar]'][ob_dt])
                    # Next line causes SettingWithCopyWarning warning
                    #data_3day.loc[ob_dt, 'mean_sea_level_pressure [mbar]'] = mslp
                    data_3day.at[ob_dt, 'mean_sea_level_pressure [mbar]'] = mslp

                # Remove negative snow_depth values (make them all zero)
                data_3day.loc[data_3day['snow_depth [cm]'] < 0.0, 'snow_depth [cm]'] = 0.0
  
                plot_station_data(site, dt, time_start, time_end, data_3day, logo_path)

                # Delete dataframes and release from memory
                del[[data,data_dt,data_unique,data_temp,data_3day]]
                gc.collect()
                data = pd.DataFrame()
                data_dt = pd.DataFrame()
                data_unique = pd.DataFrame()
                data_temp = pd.DataFrame()
                data_3day = pd.DataFrame()
