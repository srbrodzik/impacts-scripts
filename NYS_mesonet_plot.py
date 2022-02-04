#!/usr/bin/python3

"""
Created August/September 2019
@author: masonf3
Modified January 2020
@author: Joe Finlon
Modified May 2020
@author: Stacy Brodzik
Modified January 2022
@author: Stacy Brodzik

Original code named: NYS_mesonet_save_and_plot.py
Make 3-day plots and save daily .nc files of key weather variables for NYS mesonet stations (126 stations in network)
Data is read from UW Atmospheric Sciences LDM server
Some code modified from Joe Zagrodnik's 'plot_mesowest_3day.py', used for similar task in the OLYMPEX field campaign

Newest version of code split into two parts -- NYS_mesonet_save.py and NYS_mesonet_plot.py

**File Saving Information for current code**
3-day plots, one each time code is run, ftp'd to: NCAR Field Catalog
"""

import os
import shutil
import pandas as pd
import xarray as xr
import glob
from datetime import datetime, timedelta
import numpy as np 
import matplotlib 
from matplotlib.dates import DayLocator, HourLocator, DateFormatter
matplotlib.use('Agg') 
import matplotlib.transforms as transforms
from matplotlib.cbook import get_sample_data
import matplotlib.pyplot as plt
from ftplib import FTP

### SUBROUTINES ###

def mps_to_kts(val):
    """
    Convert meters per second to knots
    """
    return val*1.94384

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

def dewpoint_calc_simple(T,RH):
    """
    Got formula from here: https://iridl.ldeo.columbia.edu/dochelp/QA/Basic/dewpoint.html

    Parameters:
    T (float): 
    RH (float):

    Returns:
    Td (float): dewpoint temperature (degC)
    """

    Td =  T - ((100 - RH)/5.)
    return Td

def dewpoint_calc(T,RH):
    """
    Equations from metpy code:
    https://github.com/Unidata/MetPy/blob/main/src/metpy/calc/thermo.py

    Parameters:
    T (float): temperature in deg C
    RH (float):

    Returns:
    Td (float): dewpoint temperature (degC)
    """
    # Compute the saturation vapor pressure as a function of temperature.
    # Follows the Bolton (1980) formula (his Eqn. 10)
    # Returns e_s in hPa
    e_s = 6.112 * np.exp((17.67*T / (T + 243.5)))

    # Compute vapor pressure (RH ratio between 0 & 1, not a %)
    e = RH/100.0 * e_s

    # Compute Td, inverting the equation in step 1
    val = np.log(e / 6.112)
    Td = (243.5 * val) / (17.67 - val)
    
    return Td

def plot_station_data(site, site_long, dt, time_start, time_end, site_data, logo_path):
    '''Given a pandas dataframe containing all weather data for a specific station, this function saves a plot with
    the last 3 days worth of weather data for that station (or as much data as available if not yet 3-days). 
    
    Parameters:
    site: 4 letter site identifier
    site_long: long name of site
    dt: dataframe contain all datetimes being plotted
    time_start: first datetime in dt; redundant
    time_end: last datetime in dt; redundant
    site_data (dataframe): pandas df containing all site data for 3 days to be plotted
    logo_path: path to png file containing NYS Mesonet logo
    
    Returns:
    Saves plots to plot_dir listed near top of MAIN CODE*
    plot_dir = '/home/disk/funnel/impacts/archive/ops/nys_ground'
    plot_dir = '/home/disk/bob/impacts/images/NYSM_standard'+'/'+site
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
    
    ax1.set_title('{}, NY ({}) Meteogram\n{} - {}'.format(site_long, site,
                                                           time_start_string, time_end_string), fontsize=16)
    
    #plot airT and dewT
    if 'tair' in site_data.keys():
        airT = site_data['tair']
        ax1.plot_date(dt, airT, 'o-', label="Temp", color="red", linewidth=linewidth, markersize=markersize)
        ax1.set_xlim(time_start, time_end)
    if 'dewpt_temp' in site_data.keys():
        Td = site_data['dewpt_temp']
        ax1.plot_date(dt,Td,'o-',label="Dew Point",color="forestgreen",linewidth=linewidth,markersize=markersize)
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
    if 'wspd_merge' in site_data.keys():
        wnd_spd = mps_to_kts(site_data['wspd_merge'])  #convert to knots
        ax2.plot_date(dt,wnd_spd,'o-',label='Speed',color="black",linewidth=linewidth,markersize=markersize)
    if 'wmax_merge' in site_data.keys():
        wnd_gst = mps_to_kts(site_data['wmax_merge'])  #convert to knots
        max_wnd_gst = wnd_gst.max(skipna=True)
        ax2.plot_date(dt,wnd_gst,'o-',label='Gust [Max=' + str(round(max_wnd_gst,1)) + ' kt]',color="blue",linewidth=linewidth,markersize=markersize)
    ax2.set_ylabel('Wind (kt)')
    ax2.legend(loc='best',ncol=2)
    axes.append(ax2)
    
    #plot wind direction
    if 'wdir_merge' in site_data.keys():
        wnd_dir = site_data['wdir_merge']
        ax3.plot_date(dt,wnd_dir,'o-',label='Direction',color="purple",linewidth=0.2, markersize=markersize)
    ax3.set_ylim(-10,370)
    ax3.set_ylabel('Wind Direction')
    ax3.set_yticks([0,90,180,270,360])                          #locking y-ticks for wind direction 
    axes.append(ax3)
    
    #plot MSLP (or station pressure, if MSLP unavailable)
    if 'mslp' in site_data.keys():
        mslp = site_data['mslp']
        min_mslp = mslp.min(skipna=True)                        #min 3-day mslp value
        max_mslp = mslp.max(skipna=True)                        #max 3-day mslp value
        labelname = 'Min=' + str(round(min_mslp,1)) + ' | Max=' + str(round(max_mslp,1)) + ' hPa'
        ax4.plot_date(dt,mslp,'o-',label=labelname,color='darkorange',linewidth=linewidth,markersize=markersize)
        ax4.set_ylabel('MSLP (hPa)')
    elif 'pres' in site_data.keys():                                                   
        sp = site_data['pres']
        min_sp = sp.min(skipna=True)                            #min 3-day station pressure value
        max_sp = sp.max(skipna=True)                            #max 3-day station pressure value
        labelname = 'Min=' + str(round(min_sp,1)) + ' | Max=' + str(round(max_sp,1)) + ' hPa'
        ax4.plot_date(dt,sp,'o-',label=labelname,color='darkorange',linewidth=linewidth,markersize=markersize)
        ax4.set_ylabel('Station Pressure (hPa)')
        print('unable to get mslp, used station pressure instead')
    ax4.legend(loc='best')
    axes.append(ax4)

    #plot precip accum
    if 'precip' in site_data.keys() and 'precip_total' in site_data.keys():
        precip_offset = site_data['precip_total'][0]
        precip_accum = site_data['precip_total'] - precip_offset
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
    if 'snow_depth' in site_data.keys():
        snow_depth_mm = site_data['snow_depth'] * 1000             # input data in m; convert to mm
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
    catName = 'surface.Meteogram.' + current_dt_filestring + '.NYSM_' + site_long + '_NY' + '.png'
    plt.savefig(plot_path + '/' + catName, bbox_inches='tight')
    plt.clf(), plt.cla(), plt.close()

    # Open ftp connection
    if test:
        catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser,ftpCatalogPassword)
        catalogFTP.cwd(catalogDestDir)
    else:
        catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
        catalogFTP.cwd(catalogDestDir)

    catalogFTP.set_pasv(False)
        
    # ftp plot to catalog
    ftpFile = open(plot_path+'/'+catName,'rb')
    catalogFTP.storbinary('STOR '+catName,ftpFile)
    ftpFile.close()

    # Close ftp connection
    catalogFTP.quit()

 
### MAIN CODE ###

# set paths
working_dir = os.getcwd() # current working directory
binDir = '/home/disk/bob/impacts/bin'
# file containing lat/lon/alt of stations to plot
station_file = '/home/disk/funnel/impacts/data_archive/nys_ground/meta_nysm_catalog.csv'
# directory for daily, site-specific netcdf data
ncDir = '/home/disk/bob/impacts/raw/nys_ground_2022'
# plot stuff
plot_dir = '/home/disk/bob/impacts/images/NYSM_standard'
logo_path = '/home/disk/bob/impacts/bin/NYS_mesonet/NYSM_logo_96x96.png'

catalogPrefix = 'surface.Meteogram'
ext = 'nc'
debug = True
test = False

# Field Catalog inputs
if test:
    ftpCatalogServer = 'ftp.atmos.washington.edu'
    ftpCatalogUser = 'anonymous'
    ftpCatalogPassword = 'brodzik@uw.edu'
    catalogDestDir = 'brodzik/incoming/impacts'
else:
    ftpCatalogServer = 'catalog.eol.ucar.edu'
    ftpCatalogUser = 'anonymous'
    catalogDestDir = '/pub/incoming/catalog/impacts'

# read station names and info
station_info_data = pd.read_csv(station_file) # read station info from .csv file
station_info_data = station_info_data.set_index('stid') # index by station id
station_list = list(station_info_data.index)
station_list_long = list(station_info_data['nearest_city'])   # NEED TO REPLACE SPACES WITH UNDERSCORES

# get current date and time and list of dates to plot
current_dt = datetime.utcnow()

current_dt = current_dt.replace(minute=0, second=0, microsecond=0)
current_dt_string = datetime.strftime(current_dt, '%Y%m%d%H')
current_dt_filestring = datetime.strftime(current_dt, '%Y%m%d%H%M')
current_date_string = datetime.strftime(current_dt, '%Y%m%d')
current_date_obj = datetime.strptime(current_date_string,'%Y%m%d')
date_list = []
for idate in range(0,4):
    date_list.append( (current_date_obj-timedelta(hours=24*idate)).strftime('%Y%m%d') )
date_list.sort()

# Go through data for each site in station_list
for i,site in enumerate(station_list,0):

    station_string = site.lower()
    site_long = station_list_long[i]
    if ' ' in  site_long:
        site_long = site_long.replace(' ','_')

    # Create dataframe with datetime values as index
    df_all = pd.DataFrame()
    for idate in range(0,len(date_list)):
        date = date_list[idate]
        ncFile = ncDir+'/'+date+'/nysm_standard.'+date+'.'+station_string+'.nc'
        ds = xr.open_dataset(ncFile)
        df = ds.to_dataframe()
        if date == date_list[-1]:
            df.reset_index(inplace=True)
            lastDataIndex = ds.attrs['latest_time_5M']
            df = df[0:lastDataIndex+1]
            df = df.set_index('time_5M')
        df_all = df_all.append(df)
    df_all = df_all.loc[~df_all.index.duplicated(keep='last')].copy(deep=True)
    df_all.reset_index(inplace=True)
    # time_5M is timeDelta object; convert to datetime object
    df_all['time_5M'] = df_all['time_5M'].map(lambda time_5M:datetime(1970,1,1)+time_5M)
    df_all = df_all.set_index('time_5M') # set new data index to datetime

    data_3day = df_all.loc[df_all.index > (df_all.index[-1]-timedelta(hours=72))] # time indices w/i past 72 hrs
    dt = data_3day.index
    time_start = dt[0] # first datapoint is HH:55...start plotting at HH+1:00
    time_end = dt[-1]
    
    # Add dewpoint temp
    data_3day['dewpt_temp'] = np.nan
    data_3day['dewpt_temp'] = data_3day.apply(lambda x: dewpoint_calc(x['tair'],x['relh']),axis=1)
    
    # Remove negative snow_depth values (make them all zero)
    data_3day['snow_depth'] = np.where(data_3day['snow_depth']<0,0.0,data_3day['snow_depth'])
    
    #plot_station_data(site, dt, time_start, time_end, data_3day, logo_path)
    plot_station_data(site, site_long, dt, time_start, time_end, data_3day, logo_path)
