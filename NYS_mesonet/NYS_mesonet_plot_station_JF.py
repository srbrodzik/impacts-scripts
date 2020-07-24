'''
This code is a variant of NYS_mesonet_plot.py and is useful for generating a 3-day meteogram for a specified location and ending date.

Inputs:
    plotDir: directory path (including trailing '/') to save meteogram
    site: 4-letter mesonet ground location (e.g., ston [for Stony Brook])
    endTime: end of 3-day period in YYYYMMDDHH format
'''
import sys, os, glob
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

def plot_station_data(plotDir, site, dt, time_start, time_end, site_data, logo_path):
    '''Given a pandas dataframe containing all weather data for a specific station, this function saves a plot with
    the last 3 days worth of weather data for that station (or as much data as available if not yet 3-days). 
    
    Parameters:
    site_data (dataframe): pandas dataframe containing all data, both directly observed and calculated, 
    for a specific station 
    
    Returns:
    None 
    
    *saves plots to plot_dir listed near top of script*
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
#         ax1.plot_date(dt,airT,'o-',label="Temp",color="blue",linewidth=linewidth,markersize=markersize) 
    if 'dew_point_temp_2m [degC]' in site_data.keys():
        Td = site_data['dew_point_temp_2m [degC]']
        ax1.plot_date(dt,Td,'o-',label="Dew Point",color="forestgreen",linewidth=linewidth,markersize=markersize)
        ax1.set_xlim(time_start, time_end)
    if ax1.get_ylim()[0] < 0 < ax1.get_ylim()[1]:
        ax1.axhline(0, linestyle='-', linewidth = 1.0, color='deepskyblue')
        trans = transforms.blended_transform_factory(ax1.get_yticklabels()[0].get_transform(), ax1.transData)
        ax1.text(0, 0, '0$^\circ$C', color="deepskyblue", transform=trans, ha="right", va="center") #light blue line at 0 degrees C
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
            ax5.set_ylim(0,precip_accum[-1]+precip_accum[-1]*0.2)
        else:
            ax5.set_ylim(0, 1)
    ax5.legend(loc='best')
    ax5.set_ylabel('Precip (mm)')
    axes.append(ax5)
    
    #plot snow depth
    if 'snow_depth [cm]' in site_data.keys():
        snow_depth = site_data['snow_depth [cm]'] * 10         #convert to mm
        max_snow_depth = snow_depth.max(skipna=True)
        min_snow_depth = snow_depth.min(skipna=True)
        labelname = 'Min=' + str(round(min_snow_depth,2)) + ' | Max=' + str(round(max_snow_depth,2)) + ' mm'
        ax6.plot_date(dt,snow_depth,'o-',label=labelname,color='deepskyblue',linewidth=linewidth,markersize=markersize)
        if max(site_data['snow_depth [cm]'])>0:
            ax6.set_ylim(-0.1*max_snow_depth,max_snow_depth+max_snow_depth*0.2)
        else:
            ax6.set_ylim(0, 1)
        ax6.legend(loc='best')
        ax6.set_ylabel('Snow Depth (mm)')
        axes.append(ax6)
                        
    for item, ax in enumerate(axes):
        ax.spines["top"].set_visible(False)                             #remove dark borders on subplots
        ax.spines["right"].set_visible(False)  
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_visible(True)
        ax.tick_params(axis='x',which='both')
        ax.tick_params(axis='both', which='major', length=8)
        ax.tick_params(axis='both', which='minor', length=4)
        ax.xaxis.set_major_locator( DayLocator() )                      #one date written per day
        ax.xaxis.set_major_formatter( DateFormatter('%b-%d') )          #show date, written as 'Jul-12'
        ax.xaxis.set_minor_locator( HourLocator(np.linspace(3,21,7)) )  #hour labels every 6 hours
        ax.xaxis.set_minor_formatter( DateFormatter('%H') )             #show hour labels
        ax.fmt_xdata = DateFormatter('Y%m%d%H%M%S')
        ax.tick_params(axis='y',which='both')
        ax.yaxis.grid(linestyle = '--')                                 #adds y-axis grid lines
        ax.get_yaxis().set_label_coords(-0.06,0.5)                      #properly places y-labels away from figure
        
    # Add mesonet logo
    fig.subplots_adjust(bottom=0.1,left=.05,right=1.1)
    im = plt.imread(get_sample_data(logo_path))
    new_ax = fig.add_axes([1, 0, 0.1, 0.1])
    new_ax.imshow(im)
    new_ax.axis('off')
    
    fig.set_tight_layout(True)#plt.tight_layout()
    
    # Save the plot
    if os.path.exists(plotDir):
        plt.savefig(plotDir + 'ops.nys_ground.' + endTime_dt_filestring + '.' + site.lower() + '.png', bbox_inches='tight')
        plt.clf(), plt.cla(), plt.close()

plotDir = sys.argv[1] # user-specified path to save meteogram plot
site = sys.argv[2] # user-specified 4-letter station ID
endTime = sys.argv[3] # YYYYMMDD marking the end of the 3-day time series

station_file = '/home/disk/funnel/impacts/data_archive/nys_ground/meta_nysm_catalog.csv' # file containing station lat/lon/alt
working_dir = os.getcwd() # current working directory
csv_dir = '/home/disk/funnel/impacts/data_archive/nys_ground' # directory for daily, site-specific CSV data
plot_dir = '/home/disk/funnel/impacts/archive/ops/nys_ground' # save plots here
logo_path = '/home/disk/meso-home/jfinlon/impacts/mesonet/NYSM_logo_96x96.png' # path to mesonet logo

station_info_data = pd.read_csv(station_file) # read station info from .csv file
station_info_data = station_info_data.set_index('stid') # index by station id
station_list = list(station_info_data.index)

endTime_dt = datetime.strptime(endTime, '%Y%m%d%H')
endTime_dt_filestring = datetime.strftime(endTime_dt, '%Y%m%d%H%M')
endTime_date_string = datetime.strftime(endTime_dt, '%Y%m%d')
endTime_date_int = int(endTime_date_string) # will use this to make a list of dates from D-3 to D+0
date_list = [str(endTime_date_int-3), str(endTime_date_int-2), str(endTime_date_int-1), str(endTime_date_int)]

station_string = site.lower()

csv_files = [csv_dir+'/'+date+'/ops.nys_ground.'+date+'.'+station_string+'.csv' for date in date_list]
data = pd.concat((pd.read_csv(file) for file in csv_files)) # merge data into one dataframe object for processing
data_dt = data.set_index('datetime') # set new data index to datetime
data_unique = data_dt.loc[~data_dt.index.duplicated(keep='last')].copy(deep=True) # remove duplicate times
data_unique['datetime'] = pd.to_datetime(data_unique.index, format='%Y-%m-%d %H:%M:%S') # get datetime objects
data_unique = data_unique.set_index('datetime') # set new data index to datetime

data_3day = data_unique.loc[data_unique.index > (data_unique.index[-1]-timedelta(hours=72))] # time indices w/i past 72 hrs
dt = data_3day.index
time_start = dt[0] # first datapoint is HH:55...start plotting at HH+1:00
time_end = dt[-1] + timedelta(minutes=5) # last datapoint is HH:55...end plotting at HH+1:00

# Calculate MSLP using mean from past 12 hours
for ob_dt in data_3day.index[:]:
    temp_mean = np.nanmean(data_unique.loc[data_unique.index >
                                           (ob_dt-timedelta(hours=12))]['temp_2m [degC]'].values)
    Tv_mean =  Tmv_calc(data_3day['vapor_pressure [mbar]'][ob_dt],
                        data_3day['station_pressure [mbar]'][ob_dt], temp_mean) # calc average virtual temp
    mslp = mslp_calc(Tv_mean, data_3day['station_elevation [m]'][ob_dt], data_3day['station_pressure [mbar]'][ob_dt])
    data_3day.loc[ob_dt, 'mean_sea_level_pressure [mbar]'] = mslp

plot_station_data(plotDir, site, dt, time_start, time_end, data_3day, logo_path)