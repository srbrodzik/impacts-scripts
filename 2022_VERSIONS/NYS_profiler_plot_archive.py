#!/usr/bin/python3

"""
Created September 2019
@author: masonf3 (Mason Friedman)

Modified by Joe Finlon for 2020 field campaign
Ran on his own cron set for XX:04 due to ldm time lag
Need to add this cron to project crontab file at ~meso/cron/crontab.imp_scripts

NOTE: Might need to run on another system as it is very computation intensive

Modified by Stacy Brodzik after 2020 field campaign

Modified by Stacy Brodzik for 2022 field campaign
   Changed input files from json to netcdf
   Corrected u and v wind component calculation in lidar plotting routine
   Changed size of wind barbs (7 -> 6)

NYS_mesonet_profiler_TEST.py
Make 1-day plots of key weather variables for NYS Profiler stations.
Some code modified from Joe Zagrodnik's 'plot_mesowest_3day.py', used for similar task in the 
OLYMPEX field campaign.

File Saving Information:
1-day plots, one per hour, save to: /home/disk/bob/impacts/images/NYSM_profiler
"""

import os 
import json
import pandas as pd
import time, datetime, glob
from time import strftime 
from datetime import datetime, timedelta
import numpy as np
import matplotlib
import matplotlib.pyplot as plt 
# Comment out for running manually
matplotlib.use('Agg') 
from matplotlib.dates import DayLocator, HourLocator, DateFormatter
import matplotlib.transforms as transforms
from matplotlib.cbook import get_sample_data
import xarray as xr
from PIL import Image
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
from ftplib import FTP

### SUBROUTINES ###

def e_calc(Td):
    '''
    Given dew point, returns vapor pressure.
    
    Parameters:
    Td (float): Dew point temperature, in degrees C
    
    Returns:
    e (float): vapor pressure, in hPa
    '''
    
    e = 6.11*10**((7.5*Td)/(237.3+Td))
    return e
    
def vapor_density_calc(e,T):
    '''
    Given vapor pressure and temperature, returns vapor density (a.k.a. absolute humidity)
    
    Parameters:
    e (float): vapor pressure, in hPa
    T (float): temperature, in degrees Celsius
    
    Returns:
    Vd (float): vapor density, in kg/m^3
    '''
    
    e_Pa = e*100            #Pa (kg*m^-1*s^-2)
    T_kelvin = T+273.15     #K
    Rw = 461                #J*K^-1*kg^-1 (m^2*s^-2*K^-1)
    Vd = e_Pa/(Rw*T_kelvin) #kg/m^-3
    return Vd

def rel_humidity_calc(Td,T):
    '''
    Given dew point temperature and actual temperature, returns a relative humidity value.
    
    Parameters: 
    Td (float): Dew point temperature, in degrees C
    T (float): Actual temperature, in degrees C
    
    Returns:
    RH (float): Relative humidity, in %
    '''
    
    e = 6.11*10**((7.5*Td)/(237.3+Td))
    es = 6.11*10**((7.5*T)/(237.3+T))
    RH = (e/es)*100
    return RH

def K_to_C(degK):
    '''
    Given Kelvin temperature, returns a Celsius temperature.
    
    Parameters: 
    degK (float): Actual temperature, in degrees K
    
    Returns:
    degC (float): Actual temperature, in degrees C
    '''
    
    degC = degK - 273.15
    return degC

def ftp_to_catalog(test, imagePath, imageName):
    '''
    ftps imageName to test location or field catalog.
    
    Parameters: 
    test: (logical): if True, ftp to test location; if False, ftp to FC
    imagePath (string): full path to image
    imageName (string): name of image
    
    Returns:
    Nothing
    '''
    # Open ftp connection to NCAR sever
    if test:
        catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser,ftpCatalogPassword)
        catalogFTP.cwd(catalogDestDir)
    else:
        catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
        catalogFTP.cwd(catalogDestDir)

    # ftp image
    ftpFile = open(os.path.join(imagePath,imageName),'rb')
    catalogFTP.storbinary('STOR '+imageName,ftpFile)
    ftpFile.close()

    # Close ftp connection
    catalogFTP.quit()

def plot_mwr_ts(df_site,station,station_name_file,station_name_plot,logo_path,current_dt,test):
    '''
    Given profiler dataframe and station ID, save plot of mwr profiler data 
    
    Parameters: 
    df_site (dataframe): pandas dataframe of mwr time series data for that station.
    station (str): string of station ID
    station_name_file (str): string of station location used in filename
    station_name_plot (str): string of station location used in plot title
    logo_path (string): full path to logo file
    current_dt (datetime): current date & hour
    test (logical): if True, ftp to test location; if False, ftp to FC
    
    Returns:
    Timeseries plot output to (plotDirBase+'/mwr/'+today_date)
    '''
    
    # Make sure df_site is not full of NaN's
    ts_columns = ['temperature','liquid','vapor_density','relative_humidity']
    empty_columns = []
    for col in df_site.columns:
        if col in ts_columns and df_site[col].count() == 0:
            empty_columns.append(col)
    if len(empty_columns) == len(ts_columns):
        #print('  df_site missing data for {} - no mwr timeseries plot will be created.'.format(ts_columns))
        print('  df_site missing data - no mwr timeseries plot will be created.')
        return

    # ---------------------------
    # GET DATA READY FOR PLOTTING
    # ---------------------------
    # Get times (which are first level index)
    times_df = pd.DataFrame(df_site.index.get_level_values('time'))
    times_array = np.array(times_df.drop_duplicates()['time'])
    datetimes_array = pd.to_datetime(times_array)
    
    # Get heights (which are second level index)
    heights_df = pd.DataFrame(df_site.index.get_level_values('range'))
    # Flip height vector since rows run from top to bottom
    heights_array = np.flip(np.array(heights_df.drop_duplicates()['range']))
    #heights_array = np.array(heights_df.drop_duplicates()['range'])
    
    # Get start and stop time strings for plot title and current date string
    graphtimestamp_start=datetimes_array[0].strftime("%H UTC %m/%d/%y")
    graphtimestamp_end=current_dt.strftime("%H UTC %m/%d/%y")
    today_date = current_dt.strftime('%Y%m%d')

    # Create empty temperature, theta, liquid and rel humidity arrays
    temps_array = np.empty([len(heights_array),len(times_array)]) * np.nan
    lq_array = np.empty([len(heights_array),len(times_array)]) * np.nan
    vd_array = np.empty([len(heights_array),len(times_array)]) * np.nan
    rh_array = np.empty([len(heights_array),len(times_array)]) * np.nan

    # Fill arrays for contour plotting so heights are reversed (high to low)
    # & dims order = (heights,time)
    if df_site['temperature'].count() > 0:
        temps_df = pd.DataFrame(df_site['temperature'])
        temps_array = K_to_C( np.flip(np.transpose(np.array(temps_df).reshape((len(times_array),len(heights_array)))),0) )
    if df_site['liquid'].count() > 0:
        lq_df = pd.DataFrame(df_site['liquid'])
        lq_array = np.flip(np.transpose(np.array(lq_df).reshape((len(times_array),len(heights_array)))),0)
    if df_site['vapor_density'].count() > 0:
        vd_df = pd.DataFrame(df_site['vapor_density'])
        vd_array = np.flip(np.transpose(np.array(vd_df).reshape((len(times_array),len(heights_array)))),0)
    if df_site['relative_humidity'].count() > 0:
        rh_df = pd.DataFrame(df_site['relative_humidity'])
        rh_array = np.flip(np.transpose(np.array(rh_df).reshape((len(times_array),len(heights_array)))),0)

    # -----------
    # CREATE PLOT
    # -----------
    fig = plt.figure(figsize = (10, 7.875))
    axes = []
    
    # TEMPERATURE
    ax1 = fig.add_subplot(4,1,1)  # 4x1 grid, 1st subplot
    
    # QUESTION - shouldn't temps_array be (times x range) instead of (range x times)?
    if np.count_nonzero(np.isnan(temps_array)) != len(heights_array)*len(times_array):
        temp = ax1.contourf(datetimes_array, heights_array/1000., temps_array,
                            #levels=np.arange(-50,21,2),extend='both', cmap='viridis')
                            levels=np.arange(-50,21,2),extend='both', cmap='jet')
        contour = ax1.contour(datetimes_array,heights_array/1000.,temps_array,
                              levels=np.arange(-50,21,10),colors='grey')
    else:
        ax1.text(0.5,0.20,'NO DATA AVAILABLE',horizontalalignment='center')

    # Make labels
    plt.clabel(contour,fmt='%1.f',colors = 'green') # plot contour labels
    cb = plt.colorbar(temp)
    cb.set_ticks(np.arange(-50,21,10))
    cb.set_ticklabels(np.arange(-50,21,10))
    cb.ax.tick_params(labelsize=13)  # 16 in field
    cb.set_label('Temp. ($^\circ$C)', fontsize = 13)  # 16 in field
    ax1.tick_params(axis='x',which='both',bottom='off',top='off')
    ax1.set_xticks([])
    #ax1.set_title('{} ({}) MWR Products\n{} - {}'.format(station_name, station, graphtimestamp_start,
    #                                                     graphtimestamp_end), fontsize = 24)    
    plt.suptitle  ('{} ({}) MWR Products'.format(station_name_plot, station), x = 0.465, fontsize = 24)
    plt.title('{} - {}'.format(graphtimestamp_start, graphtimestamp_end), ha = 'center', fontsize = 20)
    axes.append(ax1)
    
    #LIQUID
    ax2 = fig.add_subplot(4,1,2)  # 4x1 grid, 2nd subplot

    # Get lower and upper ends of log of data
    levs = np.power(10, np.arange(-3, 0.01, 0.125))  # These are powers of 10 for y-axis
    if np.count_nonzero(np.isnan(lq_array)) != len(heights_array)*len(times_array):
        lq = ax2.contourf(datetimes_array, heights_array/1000., lq_array, levels=levs,
                          extend='both',cmap='rainbow')
        # Contour only every 8th level (10^-2,10^-1,10^0)
        contour = ax2.contour(datetimes_array,heights_array/1000.,lq_array,
                              levels=levs[8::8],colors='black')
    else:
        ax2.text(0.5,0.20,'NO DATA AVAILABLE',horizontalalignment='center')
        
    # Make labels in log format 
    fmt = matplotlib.ticker.LogFormatterMathtext()
    plt.clabel(contour,contour.levels,fmt=fmt,colors = 'white')
    norm = matplotlib.colors.LogNorm(vmin = .001, vmax = 1) 
    sm = plt.cm.ScalarMappable(norm=norm, cmap = lq.cmap)
    sm.set_array([])
    cb = plt.colorbar(sm)
    cb.set_ticks(levs[::8])
    #cb.set_ticklabels(['$10^-3$','$10^-2$','$10^-1$','$10^0$'])
    cb.set_ticklabels(['$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^{0}$'])
    cb.ax.tick_params(labelsize=13)  # 16 in field
    cb.set_label('Liquid (g m$^{-3}$)', fontsize = 13)  # 16 in field
    ax2.tick_params(axis='x',which='both',bottom='off',top='off')
    ax2.set_xticks([])
    axes.append(ax2)
    
    # VAPOR DENSITY
    ax3 = fig.add_subplot(4,1,3)  # 4x1 grid, 3rd subplot
    
    if np.count_nonzero(np.isnan(vd_array)) != len(heights_array)*len(times_array):
        vd = ax3.contourf(datetimes_array, heights_array/1000., vd_array, levels=np.arange(0,11,1),
                             extend='both', cmap='gist_ncar')
        contour = ax3.contour(datetimes_array,heights_array/1000.,vd_array,levels=np.arange(0,11,2),
                              colors='grey')
    else:
        ax3.text(0.5,0.20,'NO DATA AVAILABLE',horizontalalignment='center')
        
    plt.clabel(contour,fmt='%1.f',colors = 'green')
    cb = plt.colorbar(vd)
    cb.set_ticks(np.arange(0,11,2))
    cb.set_ticklabels(np.arange(0,11,2))
    cb.ax.tick_params(labelsize=13)  # 16 in field
    cb.set_label('Vap Den (g m$^{-3}$)', fontsize = 13)  # 16 in field
    ax3.tick_params(axis='x',which='both',bottom='off',top='off')
    ax3.set_xticks([])
    axes.append(ax3)

    # RH
    ax4 = fig.add_subplot(4,1,4)
    
    if np.count_nonzero(np.isnan(rh_array)) != len(heights_array)*len(times_array):
        rh = ax4.contourf(datetimes_array, heights_array/1000., rh_array,
                          levels=np.arange(0,110,5),cmap='BrBG')
        contour = ax4.contour(datetimes_array,heights_array/1000.,rh_array,
                              levels=np.array([40,60,80,90,99]))
    else:
        ax4.text(0.5,0.20,'NO DATA AVAILABLE',horizontalalignment='center')
        
    plt.clabel(contour,contour.levels,fmt='%1.f')
    cb = plt.colorbar(rh)
    cb.set_ticks(np.arange(0,110,20))
    cb.set_ticklabels(np.arange(0,110,20))
    cb.ax.tick_params(labelsize=13)  # 16 in field
    cb.set_label('RH (%)',fontsize=13)  # 16 in field
    
    ax4.set_xlabel('Time (UTC)', fontsize=15)  # 16 in field
    # Place x-label away from figure
    ax4.get_xaxis().set_label_coords(0.5,-0.25)
    # Add ticks at labeled times
    ax4.tick_params(axis='x',which='both',bottom='on',top='off')
    ax4.tick_params(axis='x', which='major', length=8)
    ax4.tick_params(axis='x', which='minor', length=4)
    ax4.set_xlim(current_dt-timedelta(hours=24), datetimes_array[-1])
    # One date written per day
    ax4.xaxis.set_major_locator( DayLocator(interval = 1) )
    # Show date, written as 'Jul-12'
    ax4.xaxis.set_major_formatter( DateFormatter('%b-%d') )
    # Hour labels every 2 hours
    ax4.xaxis.set_minor_locator( HourLocator(byhour=range(2,24,2),interval = 1) )
    # Show hour labels
    ax4.xaxis.set_minor_formatter( DateFormatter('%H') )
    ax4.xaxis.get_major_ticks()[0].label.set_fontsize(13)  # 16 in field
    for tick in ax4.xaxis.get_minor_ticks():
        tick.label.set_fontsize(13)  # 16 in field
    axes.append(ax4)

    # Plot times from x-axis of each plot
    for ax in axes:
        ax.set_ylabel('Height (km)',fontsize = 15)  # 16 in field
        ax.tick_params(axis='y',which='both',left='on',right='off', labelsize=13)  # 16 in field
        ax.tick_params(axis='y', which='major', length=8)
        ax.tick_params(axis='y', which='minor', length=4)
        ax.yaxis.grid(linestyle = '--')
        # Place y-labels away from figure
        ax.get_yaxis().set_label_coords(-0.05,0.5)
            
    # Add mesonet logo
    fig.subplots_adjust(bottom=0.1,left=.05,right=1.1)
    
    # Read image from file to array
    im = plt.imread(get_sample_data(logo_path))
    # Add axes, plot image and remove x and y axes
    #new_ax = fig.add_axes([0.94, -0.01, 0.1, 0.1])
    new_ax = fig.add_axes([0.93, -0.01, 0.1, 0.1])
    new_ax.imshow(im)
    new_ax.axis('off')

    # Save plot
    plot_path = plotDirBase+'/mwr/'+today_date
    
    if not os.path.exists(plot_path):
        os.makedirs(plot_path)
    catName = 'upperair.MWR.'+current_dt_string+'.NYSM_'+station_name_file+'_timeseries.png'
    plt.savefig(plot_path+'/'+catName,bbox_inches='tight')
    print('  Plotted MWR for ' + station)

    # Clear current figure and axes, and close window - this is probably redundant:-)
    plt.clf, plt.cla(), plt.close()

    # ftp image to catalog
    #ftp_to_catalog(test, plot_path, catName)
    
def lidar_field_plotting(station,station_name_file,station_name_plot,df_site,field,logo_path,
                         current_dt,test):
    '''
    Takes in the lidar data and will produce a plot of either CNR, Horizonal Speed or Vertical 
    Speed for a specific station.  Each plot will range from 100m to 3000m and will have wind 
    barbs with the direction of wind.
    
    Parameters:
    station (str): string of the 4 character station name.
    station_name_file (str): string of station location used in filename
    station_name_plot (str): string of station location used in plot title
    df_site (dataframe): pandas dataframe of lidar data for that station.
    field (string): must be one of ['cnr', 'w', 'velocity']
    logo_path (string): full path to logo file
    current_dt (datetime): current date & hour
    test (logical): if True, ftp to test location; if False, ftp to FC

    Returns:
    Plot of field data output to (plotDirBase+'/lidar/'+today_date)
    '''

    # Make sure df_site is not full of NaN's
    empty_columns = []
    for col in df_site.columns:
        if df_site[col].count() == 0:
            empty_columns.append(col)
    if len(empty_columns) > 0:
        #print('  df_site missing {} - no {} plot will be created.'.format(empty_columns,field))
        print('  df_site missing data - no {} plot will be created.'.format(field))
        return

    # ---------------------------
    # GET DATA READY FOR PLOTTING
    # ---------------------------
    # Get heights (which are one of indices) between 100-3000m
    heights_df = pd.DataFrame(df_site.index.get_level_values('range'))
    heights_df = heights_df.loc[(heights_df['range'] >= 100) & (heights_df['range'] <= 3000)]
    # Flip array (highest to lowest value) for plotting
    heights_array = np.flip(np.array(heights_df.drop_duplicates()['range']))
    
    # Get times (which are one of indices)
    times_df = pd.DataFrame(df_site.index.get_level_values('time'))
    times_array = np.array(times_df.drop_duplicates()['time'])
    if len(times_array) < min_times:
        print('  df_site has only {} times - no {} plot will be created.'.format(len(times_array),
                                                                                 field))
        return
    datetimes_array = pd.to_datetime(times_array)
    #pd.Timestamp(val).to_pydatetime()

    # Get start and stop time strings for plot title and current date string
    graphtimestamp_start=datetimes_array[0].strftime("%H UTC %m/%d/%y")
    graphtimestamp_end=current_dt.strftime("%H UTC %m/%d/%y")
    today_date = current_dt.strftime('%Y%m%d')

    # Swap df_site indices so range is first and time is second
    df_site = df_site.swaplevel()
    
    # Initialize field_array (contains data in 'field' input param)
    field_array = np.zeros([len(heights_array),len(times_array)])
    
    # Create empty Uwind and Vwind arrays and fill with NaN's
    Uwind = np.full([len(heights_array),len(times_array)], np.nan)
    Vwind = np.full([len(heights_array),len(times_array)], np.nan)

    # Fill in field_array, Uwind and Vwind arrays
    for i in range(0,len(times_array)):
        for j in range(0,len(heights_array)):
            field_array[j,i] = df_site.loc[(heights_array[j],times_array[i]),field]
            direction = df_site.loc[(heights_array[j],times_array[i]),'direction']
            velocity = df_site.loc[(heights_array[j],times_array[i]),'velocity']
            """
            #Take every other row and column of wind data
            if (j % 2 == 0) and (i % 2 == 0):
                # According to:
                # http://colaweb.gmu.edu/dev/clim301/lectures/wind/wind-uv
                # to convert from "wind weather direction" to "math direction" use:
                #    md = 270 − wwd
                # If result < 0, add 360
                if direction > 270:
                    Uwind[j,i] = np.cos((360+(270. - direction))/180.*np.pi)*velocity
                    Vwind[j,i] = np.sin((360+(270. - direction))/180.*np.pi)*velocity
                else:
                    Uwind[j,i] = np.cos((270. - direction)/180.*np.pi)*velocity
                    Vwind[j,i] = np.sin((270. - direction)/180.*np.pi)*velocity
            """
            if direction > 270:
                Uwind[j,i] = np.cos((360+(270. - direction))/180.*np.pi)*velocity
                Vwind[j,i] = np.sin((360+(270. - direction))/180.*np.pi)*velocity
            else:
                Uwind[j,i] = np.cos((270. - direction)/180.*np.pi)*velocity
                Vwind[j,i] = np.sin((270. - direction)/180.*np.pi)*velocity

    # -----------
    # CREATE PLOT
    # -----------
    # Get the smallest and largest non-nan of the field_array data
    field_max = np.nanmax(field_array)
    field_min = np.nanmin(field_array)
    
    # Get the binsize based off the amount of bins defined globally
    binsize = (field_max - field_min)/bin_number

    # Round levels more precisely, define colorbar levels and choose cmap
    if field == 'w':
        levs = np.arange(-5, 5.01, 0.25)
        cblevs = np.arange(-5, 5.01, 1)
        colormap = 'bwr'
        extend = 'both'
    elif field == 'cnr':
        levs = np.arange(-30, 6, 1)
        cblevs = np.arange(-30, 6, 5)
        colormap = 'gist_ncar'
        extend = 'max'
    else:  # for velocity
        levs = np.arange(0, 101, 2)# np.round(levs)
        cblevs = np.arange(0, 101, 10)
        colormap = 'nipy_spectral'#'cool'
        extend = 'max'

    # Create figure
    fig, ax = plt.subplots(figsize = (10, 5.625))
    
    # Background array allows for the figure background color to be customized
    background = np.zeros([len(heights_array),len(times_array)])

    # Plot field filled contours and Uwind and Vwind vectors
    # Background color
    ax.contourf(datetimes_array,heights_array/1000.,background, colors = 'aliceblue')
    color_plot = ax.contourf(datetimes_array, heights_array/1000., field_array, levels = levs,
                             extend=extend, cmap=colormap)
    # Use every fourth wind value; length is length of barb in points
    ax.barbs(datetimes_array[::4],heights_array[::4]/1000.,Uwind[::4, ::4],Vwind[::4, ::4],
             length = 6)
    # Use every second wind value; length is length of barb in points
    #ax.barbs(datetimes_array[::2],heights_array[::2]/1000.,Uwind[::2, ::2],Vwind[::2, ::2],
    #         length = 6)
    # Only plots black contour lines for vertical velocity or CNR data
    if field == 'w' or field == 'cnr':
        # Use every fourth level value
        contour = ax.contour(datetimes_array,heights_array/1000.,field_array,levels=levs[::4],
                             colors='black')
        # Add labels to contours
        plt.clabel(contour,fmt='%1.1f',colors='white')

    # Plot colorbar
    cb = plt.colorbar(color_plot)
    cb.set_ticks(cblevs)
    cb.set_ticklabels(cblevs)
    cb.ax.tick_params(labelsize=14)

    # Label colorbar and get info for plot title
    # W and velocity have the same units
    if field == 'cnr':
        cb.set_label('CNR (dB)',fontsize=16)  # 20 in field
        field_title = 'Carrier-to-Noise Ratio'
        save_name = field
    elif field == 'w': 
        cb.set_label('m s$^{-1}$',fontsize=16)  # 20 in field
        field_title = 'Vertical Velocity'
        save_name = 'vert_wspd'
    elif field == 'velocity':
        cb.set_label('kt',fontsize=16)  # 20 in field
        field_title = 'Horizontal Velocity'
        save_name = 'horz_wspd'
    else:  # SINCE WE ALREADY CHECKED FOR VALID FIELD THIS MIGHT NOT BE NECESSARY
        cb.set_label('dB',fontsize = 16)  # 20 in field
        field_title = field.upper()
        save_name = field
        
    # Set title & subtitle of plot
    #ax.set_title('{} ({}) Lidar {}\n{} - {}'.format(station_name, station, field_title,
    #                                                graphtimestamp_start,
    #                                                graphtimestamp_end), fontsize = 24)
    if field == 'cnr':
        plt.suptitle ('{} ({}) Lidar {}'.format(station_name_plot, station,field_title),
                      x = 0.47, fontsize = 22)
    elif field == 'w':
        plt.suptitle ('{} ({}) Lidar {}'.format(station_name_plot, station,field_title),
                      x = 0.465, fontsize = 22)
    elif field == 'velocity':
        plt.suptitle ('{} ({}) Lidar {}'.format(station_name_plot, station,field_title),
                      x = 0.465, fontsize = 22)        
    plt.title('{} - {}'.format(graphtimestamp_start, graphtimestamp_end), ha = 'center',
              fontsize = 18)

    # Set Y-axis height ticks  
    height_ticks = np.array([0.1,0.5,1,1.5,2,2.5,3])
    ax.set_yticks(height_ticks)
    ax.set_yticklabels(height_ticks, fontsize = 14)  # 16 in field
    ax.set_ylim(0.1,3)
    ax.set_ylabel('Height (km)', fontsize = 16)  # 20 in field
    
    # Set X-axis time ticks
    ax.set_xlabel('Time (UTC)', fontsize=16)  # 20 in field
    # DO WE NEED NEXT LINE? (add ticks at labeled times)
    ax.tick_params(axis='x',which='both',bottom='on',top='off')                  

    ax.tick_params(axis='both', which='major', length=8)
    ax.tick_params(axis='both', which='minor', length=4)
    ax.yaxis.grid(linestyle = '--')
    ax.set_xlim(current_dt-timedelta(hours=24), datetimes_array[-1])
    # One date written per day
    ax.xaxis.set_major_locator( DayLocator(interval = 1), )
    # Show date, written as 'Jul-12'
    ax.xaxis.set_major_formatter( DateFormatter('%b-%d'))
    # Hour labels every 2 hours
    ax.xaxis.set_minor_locator( HourLocator(byhour=range(2,24,2),interval = 1) )
    # Show hour labels
    ax.xaxis.set_minor_formatter( DateFormatter('%H'))
    ax.get_yaxis().set_label_coords(-0.08,0.5)
    ax.xaxis.get_major_ticks()[0].label.set_fontsize(14)  # 16 in field
    cb.ax.tick_params(labelsize=14)  # 16 in field
    for tick in ax.xaxis.get_minor_ticks():
        tick.label.set_fontsize(14)  # 16 in field
    
    # Add mesonet logo
    fig.subplots_adjust(bottom=0.1,left=.05,right=1.1)
    # Read image from file to array
    im = plt.imread(get_sample_data(logo_path))
    # Add axes, plot image and remove x and y axes
    #new_ax = fig.add_axes([0.95, -0.02, 0.1, 0.1])
    new_ax = fig.add_axes([0.93, -0.02, 0.1, 0.1])
    new_ax.imshow(im)
    new_ax.axis('off')
    
    # Save plot
    plot_path = plotDirBase+'/lidar/'+today_date
    if not os.path.exists(plot_path):
        os.makedirs(plot_path)
    catName = 'lidar.DL.'+current_dt_string+'.NYSM_'+station_name_file+'_'+field+'.png'
    plt.savefig(plot_path+'/'+catName,bbox_inches='tight')
    print('  Plotted ' + field + ' Lidar' + ' for ' + station)
    
    # Clear current figure and axes, and close window - this is probably redundant:-)
    plt.clf, plt.cla(), plt.close()

    # ftp image to catalog
    #ftp_to_catalog(test, plot_path, catName)
    
def  plot_cloud_liquid(df_site,station,station_name_file,station_name_plot,logo_path,
                       current_dt,test):
    '''
    Takes in a df with field variables integrated vapor, integrated liquid, cloud base (km), 
    and a rain flag of either 0.0 or 1.0.  Outputs a scatter plot of the df variables with the 
    left axis in kilometers and the right axis in mm liquid/ cm vapor.

    Parameters:
    df_site (dataframe): pandas dataframe of profiler data for that station.
    station (str): string of the 4 character station name.
    station_name_file (str): string of station location used in filename
    station_name_plot (str): string of station location used in plot title
    logo_path (string): full path to logo file
    current_dt (datetime): current date & hour
    test (logical): if True, ftp to test location; if False, ftp to FC
    
    Returns:
    Scatter plot output to (plotDirBase+'/mwr/'+today_date)
    '''
    
    # Make sure df_site is not full of NaN's
    cl_columns = ['integrated_vapor','integrated_liquid','cloud_base','rain_flag']
    empty_columns = []
    for col in df_site.columns:
        if col in cl_columns and df_site[col].count() == 0:
            empty_columns.append(col)
    if len(empty_columns) > 0:
        print('  df_site missing data - no mwr cloud plot will be created.')
        return

    # ---------------------------
    # GET DATA READY FOR PLOTTING
    # ---------------------------
    # Get times
    times_df = pd.DataFrame(df_site.index.get_level_values('time'))
    #times_array = np.array(times_df.drop_duplicates()['time'])
    times_array = np.array(times_df['time'])
    datetimes_array = pd.to_datetime(times_array)
    
    # Get start and stop time strings for plot title and current date string
    graphtimestamp_start=datetimes_array[0].strftime("%H UTC %m/%d/%y")
    graphtimestamp_end=current_dt.strftime("%H UTC %m/%d/%y")
    today_date = current_dt.strftime('%Y%m%d')
    
    # Get non-zero values of rain flag which represent rain
    rain = df_site['rain_flag'].values
    rain_indices = np.where( rain != 0.0 )[0]

    # -----------
    # CREATE PLOT
    # -----------
    fig, axL = plt.subplots(figsize = (9, 7.875))

    #axL.set_title('{} ({}) Derived MWR Products\n{} - {}'.format(
    #    station_name, station, graphtimestamp_start, graphtimestamp_end), fontsize = 24)    
    plt.suptitle('{} ({}) Derived MWR Products'.format(station_name_plot, station),x = 0.57,
                 fontsize = 24)
    plt.title('{} - {}'.format(graphtimestamp_start, graphtimestamp_end), ha = 'center',
              fontsize = 20)

    # Height axis for cloud base height 
    height_ticks = np.arange(0,11,1)
    axL.set_ylim(0,10)
    axL.set_yticks(height_ticks)
    axL.set_yticklabels(height_ticks, fontsize = 13)  # 16 in field
    axL.set_ylabel('Cloud Base (km)', fontsize = 15)  # 20 in field
    
    # Right axis for integrated liquid/vapor
    axR = axL.twinx()
    axR.set_ylim(0,10)
    axR.set_yticks(height_ticks)
    axR.set_yticklabels(height_ticks, fontsize = 13)  # 16 in field
    axR.set_ylabel('Integrated Moisture (mm liquid | cm vapor)', fontsize = 15)  # 20 in field
    
    # Make scatter plots
    cb = axL.scatter(datetimes_array.values, df_site['cloud_base'].values,c='black') #in kms
    iv = axR.scatter(datetimes_array.values, df_site['integrated_vapor'].values,c='red')
    il = axR.scatter(datetimes_array.values, df_site['integrated_liquid'].values,c='blue')
    
    # Plot vertical line for rainfall, and save last line as object for legend
    try:
        # WHY STOP AT SECOND LAST VALID INDEX?
        for rainy_time in datetimes_array[rain_indices][:-1]:
            # Set low value for alpha to get lighter color
            axL.axvline(rainy_time,color = 'g',alpha=.2)
        rf = axL.axvline(datetimes_array[rain_indices][-1],color = 'g',alpha=.5)
        axR.legend((cb,iv,il,rf) , ("Cloud Base","Integrated Vapor", "Integrated Liquid", "Rain Flag"),
                   fontsize = 14)  # 16 in field
    except:
        axR.legend((cb,iv,il) , ("Cloud Base","Integrated Vapor", "Integrated Liquid"),
                   fontsize = 14)  # 16 in field
    
    # Get the time ticks
    axL.set_xlabel('Time (UTC)', fontsize=15)  # 20 in field
    # Add ticks at labeled times 
    axL.tick_params(axis='x',which='both',bottom='on',top='off')
    axL.yaxis.grid(linestyle = '--')
    # One date written per day
    axL.xaxis.set_major_locator( DayLocator(interval = 1) )
    # Show date, written as 'Jul-12'
    axL.xaxis.set_major_formatter( DateFormatter('%b-%d') )
    # Hour labels every 2 hours
    axL.xaxis.set_minor_locator( HourLocator(byhour=range(2,24,2),interval = 1) )
    # Show hour labels
    axL.xaxis.set_minor_formatter( DateFormatter('%H') )
    # Axis will squueze to size of actual data
    axL.set_xlim(current_dt-timedelta(hours=24), datetimes_array[-1])
    axL.get_yaxis().set_label_coords(-0.04,0.5)
    axL.xaxis.get_major_ticks()[0].label.set_fontsize(13)  # 16 in field
    for tick in axL.xaxis.get_minor_ticks():
        tick.label.set_fontsize(14)  # 16 in field
    
    # Add mesonet logo
    fig.subplots_adjust(bottom=0.1,left=.05,right=1.1)
    # Read image from file to array
    im = plt.imread(get_sample_data(logo_path))
    # Add axes, plot image and remove x and y axes
    new_ax = fig.add_axes([1.07, -0.01, 0.1, 0.1])
    new_ax.imshow(im)
    new_ax.axis('off')
    
    # Save plot
    plot_path = plotDirBase+'/mwr/'+today_date
    if not os.path.exists(plot_path):
        os.makedirs(plot_path)
    catName = 'upperair.MWR.'+current_dt_string+'.NYSM_'+station_name_file+'_cloud.png'
    plt.savefig(plot_path+'/'+catName,bbox_inches='tight')
    print('  Plotted ' + 'cloud/liquid profile' + ' for ' + station)
   
    # Clear current figure and axes, and close window - this is probably redundant:-)
    plt.clf, plt.cla(), plt.close()

    # ftp image to catalog
    #ftp_to_catalog(test, plot_path, catName)
    
### MAIN CODE ###

# Set paths
ncDirBase = '/home/disk/bob/impacts/raw/nys_profiler_2022'
# plot stuff
plotDirBase = '/home/disk/bob/impacts/images/NYSM_profiler'
logo_path = '/home/disk/bob/impacts/bin/NYS_mesonet/NYSM_logo_96x96.png'

# Number of contours for the LIDAR plots (must be a float)
bin_number = 20.

# Number of times required to create plot (usually there are 143 times so this is ~one quarter)
min_times = 35

# Field Catalog inputs
test = False
if test:
    ftpCatalogServer = 'ftp.atmos.washington.edu'
    ftpCatalogUser = 'anonymous'
    ftpCatalogPassword = 'brodzik@uw.edu'
    catalogDestDir = 'brodzik/incoming/impacts'
else:
    ftpCatalogServer = 'catalog.eol.ucar.edu'
    ftpCatalogUser = 'anonymous'
    catalogDestDir = '/pub/incoming/catalog/impacts'

lidar_prods = ['cnr','w','velocity']
station_dict = {'ALBA': {'forFilename':'Albany_NY','forPlot':'Albany, NY'},
                'BELL': {'forFilename':'Belleville_NY','forPlot':'Belleville, NY'},
                'BRON': {'forFilename':'Bronx_NY','forPlot':'Bronx, NY'},
                'BUFF': {'forFilename':'Buffalo_NY','forPlot':'Buffalo, NY'},
                'CHAZ': {'forFilename':'Chazy_NY','forPlot':'Chazy, NY'},
                'CLYM': {'forFilename':'Clymer_NY','forPlot':'Clymer, NY'},
                'EHAM': {'forFilename':'East_Hampton_NY','forPlot':'East Hampton, NY'},
                'JORD': {'forFilename':'Jordan_NY','forPlot':'Jordan, NY'},
                'OWEG': {'forFilename':'Owego_NY','forPlot':'Owego, NY'},
                'QUEE': {'forFilename':'Queens_NY','forPlot':'Queens, NY'},
                'REDH': {'forFilename':'Red_Hook_NY','forPlot':'Red Hook, NY'},
                'STAT': {'forFilename':'Staten_Island_NY','forPlot':'Staten Island, NY'},
                'STON': {'forFilename':'Stony_Brook_NY','forPlot':'Stony Brook, NY'},
                'SUFF': {'forFilename':'Suffern_NY','forPlot':'Suffern, NY'},
                'TUPP': {'forFilename':'Tupper_Lake_NY','forPlot':'Tupper Lake, NY'},
                'WANT': {'forFilename':'Wantagh_NY','forPlot':'Wantagh, NY'},
                'WEBS': {'forFilename':'Webster_NY','forPlot':'Webster, NY'} }

# Go through each hour of each day and month
for month in range(2,3):  # January
    if month == 1:
        minDate = 11
        maxDate = 31
    elif month == 2:
        minDate = 20
        maxDate = 22
    for day in range(minDate,maxDate+1):
        for hour in range(0,24):
            # Get date and time
            current_dt = datetime(2022,month,day,hour,0)
            current_dt_string = datetime.strftime(current_dt, '%Y%m%d%H%M')
            current_date_string = datetime.strftime(current_dt, '%Y%m%d')
            current_hourMin_string = datetime.strftime(current_dt, '%H%M')
            yesterday_dt = current_dt - timedelta(days=1)
            yesterday_date_string = datetime.strftime(yesterday_dt, '%Y%m%d')
            date_list = [yesterday_date_string,current_date_string]

            print('datetime = {}'.format(current_dt_string))
            for station in station_dict.keys():
                print('Plotting and saving data for {} at {}.'.format(station,current_dt_string))
                station_name_file = station_dict[station]['forFilename']
                station_name_plot = station_dict[station]['forPlot']

                # Create dataframe with datetime values as primary index
                df_all = pd.DataFrame()
                for date in date_list:
                    ncDir = ncDirBase+'/'+date
                    ncFile = 'nysm_profiler.'+date+'.'+station.lower()+'.nc'
                    if os.path.isfile(ncDir+'/'+ncFile):
                        ds = xr.open_dataset(ncDir+'/'+ncFile)
                        df = ds.to_dataframe()
                        df_all = df_all.append(df)
                    else:
                        print('{} does not exist'.format(ncFile))
                        continue

                if len(df_all) > 0:
                    #df_all = df_all.sort_index(level=1)
                    #df_all = df.swaplevel(0)
                    df_all.reset_index(inplace=True)
                    df_all['time'] = df_all['time'].astype(int)
                    df_all['time'] = df_all['time'].apply(lambda x: datetime.utcfromtimestamp(x))
                    #df_all['time'] = pd.to_datetime(df_all['time'])
                    df_all.set_index(['time','range'],inplace=True)
                    df_all = df_all.sort_index(level=0)

                    # Create subset of data for last 24 hours
                    last_time = current_dt
                    first_time = current_dt - timedelta(hours=24)
                    df_site = df_all[df_all.index.get_level_values('time') >= first_time]
                    df_site = df_site[df_site.index.get_level_values('time') <= last_time]
                    time_start = df_site.index[0][0]
                    time_end = df_site.index[-1][0]
    
                    # Create MWR plots
                    plot_mwr_ts(df_site,station,station_name_file,station_name_plot,logo_path,
                                current_dt,test)
                    plot_cloud_liquid(df_site,station,station_name_file,station_name_plot,
                                      logo_path,current_dt,test)

                    # Create Lidar plots
                    for prod in lidar_prods:
                        lidar_field_plotting(station,station_name_file,station_name_plot,df_site,
                                             prod,logo_path,current_dt,test)

                    print('\n')

                else:
                    print('No {} data at month {}, day {}, hour {}'.format(station,month,day,hour)) 
