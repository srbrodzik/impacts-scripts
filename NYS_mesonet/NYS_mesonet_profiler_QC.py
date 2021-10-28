#!/usr/bin/python

"""
Created September 2019
@author: masonf3 (Mason Friedman)

Modified by Joe Finlon for 2020 field campaign
Ran on his own cron set for XX:04 due to ldm time lag
Need to add this cron to project crontab file at ~meso/cron/crontab.imp_scripts

NOTE: Might need to run on another system as it is very computation intensive

Modified by Stacy Brodzik after 2020 field campaign

NYS_mesonet_profiler_TEST.py
Make 1-day plots of key weather variables for NYS Profiler stations.
Some code modified from Joe Zagrodnik's 'plot_mesowest_3day.py', used for similar task in the OLYMPEX field campaign.
Code to read in data developed by Nathan Bain's 'read_profiler_data.py', used at NYS Mesonet.

File Saving Information:
1-day plots, one per hour, save to: /home/disk/funnel/impacts/archive/ops/
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
#matplotlib.use('Agg') 
from matplotlib.dates import DayLocator, HourLocator, DateFormatter
import matplotlib.transforms as transforms
from matplotlib.cbook import get_sample_data
import xarray as xr
from PIL import Image
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

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

def load_data(path,station, curr_dt_string):
    '''
    Given filepath to data stream with .json files and a profiler station, returns 
    1. three dataframes with microwave radiometer and lidar data and
    2. two flags indicating whether radiometer and lidar data were successfully read
    
    Parameters:
    path (filepath): path to directory where json files live
    station (str): string of station ID
    curr_dt_string: string of datetime (YYYYMMDDhhmm)
    
    Returns:
    mwr_4plot_df (dataframe): pandas dataframe of microwave radiometer data for the 3panel plot
    mwr_precip_df (dataframe): pandas dataframe of microwave radiometer data for the precip/cloud height plot
    lidar_df (dataframe): pandas dataframe of lidar data for that station
    successMWR
    successLidar
    '''

    # Initialize variables
    successMWR = True
    successLidar = True
    mwr = None
    lidar = None
    curr_dt_obj = datetime.strptime(curr_dt_string,'%Y%m%d%H%M')
    curr_date_obj = datetime.strptime(curr_dt_string[0:8],'%Y%m%d')

    # Get list of files up to curr_dt_string
    # Use last file in list to create dataframes since each file contains 24 hours of data
    file_list = glob.glob(path + '/*'  + station + '.json')
    file_list.sort()
    # remove possible files AFTER current/user-specified date
    file_list_trimmed = []
    for file in file_list:
        fileTime_string = file.split('/')[-2][:]+file.split('/')[-1][:4]
        fileTime_obj = datetime.strptime(fileTime_string,'%Y%m%d%H%M')
        if fileTime_obj <= curr_dt_obj+timedelta(minutes=3):
            # +3 to allow for 3-minute buffer in case files still being saved
            file_list_trimmed.append(file)

    # if there are files in file_list_trimmed, continue
    if len(file_list_trimmed) > 0:
        latest_file = file_list_trimmed[-1]

        # Load data from last file in file list
        with open(latest_file, "r") as f:
            data = json.load(f)

            try:    
                mwr = data['mwr']
                mwr = xr.Dataset.from_dict(mwr)
                mwr = xr.decode_cf(mwr)  # decode using CF conventions
            
                # Each field had to broken up into separate dataframes to avoid a memory error
                mwr_p = mwr['pressure_level'].to_dataframe()
                mwr_t = mwr['temperature'].to_dataframe()
                mwr_td = mwr['dew_point'].to_dataframe()
                mwr_rh = mwr['relative_humidity'].to_dataframe()
                mwr_lq = mwr['liquid'].to_dataframe()
                mwr_iv = mwr['integrated_vapor'].to_dataframe()
                mwr_il = mwr['integrated_liquid'].to_dataframe()
                mwr_cb = mwr['cloud_base'].to_dataframe()
                mwr_rf = mwr['rain_flag'].to_dataframe()

                # Create potential temperature dataframe
                theta_vals = (mwr['temperature']+273.15) * (1000. / mwr['pressure_level']) ** (2./7.) #xarray
                theta = mwr['temperature'].copy()  #xarray
                theta.values = theta_vals.values.reshape(mwr['temperature'].shape) #array
                theta.attrs['units'] = 'K'
                theta = theta.rename('theta') #rename 'temperature' var as 'theta'
                mwr_th = theta.to_dataframe()

                # Two different mwr dataframes are created:
                # 1. mwr_4plot_df: multi index of times->heights->t,td,th,rh,lq
                # 2. mwr_precip_df: single index of times->iv,il,cb,rf
            
                # Second element is concatenated together to drop repetative "angle" columns
                mwr_4plot_df = pd.concat([mwr_t.iloc[:,1], mwr_td.iloc[:,1], mwr_th.iloc[:,1],
                                          mwr_rh.iloc[:,1], mwr_lq.iloc[:,1]], axis=1)

                # Rain flags are 30 seconds offset from the other variables 
                # Depending on where the data starts, sometimes the rain flag series will have a different
                #   length than the rest of the data by one value
                # iv, il, cb indices dropped and replaced with index of rain flag or
                #   rain index is dropped and replaced with index of other data (cb,il,iv)
                data_indices = mwr_cb.index
                index_diff = len(mwr_rf.index) - len(mwr_cb.index)
                if index_diff < 0:
                    # Remove last index_diff entries from mwr_iv, mwr_il, mwr_cb
                    data_indices = mwr_cb[:index_diff].index
                elif index_diff > 0:
                    # Remove last index_diff entries from mwr_rf
                    mwr_rf = mwr_rf.iloc[:-index_diff, :]

                # Set index values to match other parameters
                mwr_rf = mwr_rf.reset_index(drop=True)
                mwr_rf = mwr_rf.set_index(data_indices)
                mwr_precip_df = pd.concat([mwr_iv.iloc[:,1],mwr_il.iloc[:,1],mwr_cb.iloc[:,1],mwr_rf.iloc[:,1]],
                                          axis=1,sort=True)
            
            except:
                successMWR = False
                print("  Problem reading microwave radiometer data for "+station)
                mwr_df = []
                mwr_4plot_df = pd.DataFrame(mwr_df)  
                mwr_precip_df = pd.DataFrame(mwr_df)

            try:
                lidar = data['lidar']
                lidar = xr.Dataset.from_dict(lidar)
                lidar = xr.decode_cf(lidar)
                lidar_df = lidar.to_dataframe()
                # IS NEXT STATEMENT NEEDED??
                lidar_df = pd.DataFrame(lidar_df)
            
            except:
                successLidar = False
                print("  Problem reading lidar data for "+station)
                lidar_df = []
                lidar_df = pd.DataFrame(lidar_df)

    else:
        print("  No microwave radiometer data at this time for "+station)
        successMWR = False
        mwr_df = []
        mwr_4plot_df = pd.DataFrame(mwr_df)  
        mwr_precip_df = pd.DataFrame(mwr_df)
        
        print("  No lidar data at this time for "+station)
        successLidar = False
        lidar_df = []
        lidar_df = pd.DataFrame(lidar_df)

    return mwr_4plot_df, mwr_precip_df, lidar_df, successMWR, successLidar

def plot_mwr_ts(mwr_df, station, station_name, logo_path, curr_dt):
    '''
    Given microwave radiometer dataframe and station ID, save plot of mwr profiler data 
    
    Parameters: 
    mwr_df (dataframe): pandas dataframe of mwr time series data for that station.
    station (str): string of station ID
    station_name (str): string of station location
    logo_path (string): full path to logo file
    curr_dt (datetime) - current date & hour
    
    Returns:
    Timeseries plot output to (plot_parent_dir + 'nys_mwr_ts_qc/' + today_date)
    '''
    
    # Make sure mwr_df is not full of NaN's
    empty_columns = []
    for col in mwr_df.columns:
        if mwr_df[col].count() == 0:
            empty_columns.append(col)
    if len(empty_columns) == len(mwr_df.columns):
        print('  mwr_4plot_df missing all fields - no timeseries plot will be created.')
        return

    # ---------------------------
    # GET DATA READY FOR PLOTTING
    # ---------------------------
    # Get times (which are first level index)
    times_df = pd.DataFrame(mwr_df.index.get_level_values('time'))
    times_array = np.array(times_df.drop_duplicates()['time'])
    if len(times_array) < min_times:
        print('  mwr_df has only {} times - no timeseries plot will be created.'.format(len(times_array)))
        return
    datetimes_array = pd.to_datetime(times_array)
    
    # Get heights (which are second level index)
    heights_df = pd.DataFrame(mwr_df.index.get_level_values('range'))
    # Flip height vector since rows run from top to bottom
    heights_array = np.flip(np.array(heights_df.drop_duplicates()['range']))
    
    # Get start and stop time strings for plot title and current date string
    graphtimestamp_start=datetimes_array[0].strftime("%H UTC %m/%d/%y")
    graphtimestamp_end=curr_dt.strftime("%H UTC %m/%d/%y")
    today_date = curr_dt.strftime('%Y%m%d')

    # Create empty temperature, theta, liquid and rel humidity arrays
    temps_array = np.empty([len(heights_array),len(times_array)]) * np.nan
    th_array = np.empty([len(heights_array),len(times_array)]) * np.nan
    lq_array = np.empty([len(heights_array),len(times_array)]) * np.nan
    rh_array = np.empty([len(heights_array),len(times_array)]) * np.nan

    # Fill arrays for contour plotting so heights are reversed (high to low) & dims order = (heights,time)
    if mwr_df['temperature'].count() > 0:
        temps_df = pd.DataFrame(mwr_df['temperature'])
        temps_array = np.flip(np.transpose(np.array(temps_df).reshape((len(times_array),len(heights_array)))),0)
    if mwr_df['theta'].count() > 0:
        th_df = pd.DataFrame(mwr_df['theta'])
        th_array = np.flip(np.transpose(np.array(th_df).reshape((len(times_array),len(heights_array)))),0)
    if mwr_df['liquid'].count() > 0:
        lq_df = pd.DataFrame(mwr_df['liquid'])
        lq_array = np.flip(np.transpose(np.array(lq_df).reshape((len(times_array),len(heights_array)))),0)
    if mwr_df['relative_humidity'].count() > 0:
        rh_df = pd.DataFrame(mwr_df['relative_humidity'])
        rh_array = np.flip(np.transpose(np.array(rh_df).reshape((len(times_array),len(heights_array)))),0)

    # Replaced these two 'for' loops with above statements
    #for i in range(0,len(times_array)):
    #    for j in range(0,len(heights_array)):
    #        temps_array[j,i] = mwr_df.loc[(times_array[i],heights_array[j]),'temperature']
    #        th_array[j,i] = mwr_df.loc[(times_array[i],heights_array[j]),'theta']
    #        lq_array[j,i] = mwr_df.loc[(times_array[i],heights_array[j]),'liquid']
    #        rh_array[j,i] = mwr_df.loc[(times_array[i],heights_array[j]),'relative_humidity']

    # -----------
    # CREATE PLOT
    # -----------
    fig = plt.figure(figsize = (10, 7.875))
    axes = []
    
    # TEMPERATURE
    ax1 = fig.add_subplot(4,1,1)  # 4x1 grid, 1st subplot
    # QUESTION - shouldn't temps_array be (times x range) instead of (range x times)?
    if np.count_nonzero(np.isnan(temps_array)) != len(heights_array)*len(times_array):
        temp = ax1.contourf(datetimes_array, heights_array/1000., temps_array, levels=np.arange(-50,21,2),
                            extend='both', cmap='viridis')
        contour = ax1.contour(datetimes_array,heights_array/1000.,temps_array, levels=np.arange(-50,21,10),
                              colors='grey')
    else:
        ax1.text(0.5,0.20,'NO DATA AVAILABLE',horizontalalignment='center')
    plt.clabel(contour,fmt='%1.f',colors = 'green') # plot contour labels
    cb = plt.colorbar(temp)
    cb.set_ticks(np.arange(-50,21,10))
    cb.set_ticklabels(np.arange(-50,21,10))
    cb.ax.tick_params(labelsize=13)  # 16 in field
    cb.set_label('Temp. ($^\circ$C)', fontsize = 15)  # 16 in field
    ax1.tick_params(axis='x',which='both',bottom='off',top='off')
    ax1.set_xticks([])
    #ax1.set_title('{} ({}) MWR Products\n{} - {}'.format(station_name, station, graphtimestamp_start,
    #                                                     graphtimestamp_end), fontsize = 24)    
    plt.suptitle  ('{} ({}) MWR Products'.format(station_name, station), x = 0.465, fontsize = 24)
    plt.title('{} - {}'.format(graphtimestamp_start, graphtimestamp_end), ha = 'center', fontsize = 20)
    axes.append(ax1)
    
    # POTENTIAL TEMPERATURE (theta)
    ax2 = fig.add_subplot(4,1,2)  # 4x1 grid, 2nd subplot
    if np.count_nonzero(np.isnan(th_array)) != len(heights_array)*len(times_array):
        theta = ax2.contourf(datetimes_array, heights_array/1000., th_array, levels=np.arange(250,361,2),
                             extend='both', cmap='gist_ncar')
        contour = ax2.contour(datetimes_array,heights_array/1000.,th_array,levels=np.arange(250,361,10),
                              colors='grey')
    else:
        ax2.text(0.5,0.20,'NO DATA AVAILABLE',horizontalalignment='center')
    plt.clabel(contour,fmt='%1.f',colors = 'green')
    cb = plt.colorbar(theta)
    cb.set_ticks(np.arange(250,361,20))
    cb.set_ticklabels(np.arange(250,361,20))
    cb.ax.tick_params(labelsize=13)  # 16 in field
    cb.set_label('$\Theta$ (K)', fontsize = 15)  # 16 in field
    ax2.tick_params(axis='x',which='both',bottom='off',top='off')
    ax2.set_xticks([])
    axes.append(ax2)

    #LIQUID
    ax3 = fig.add_subplot(4,1,3)

    # Get lower and upper ends of log of data
    levs = np.power(10, np.arange(-3, 0.01, 0.125))  # These are powers of 10 for y-axis
    if np.count_nonzero(np.isnan(lq_array)) != len(heights_array)*len(times_array):
        lq = ax3.contourf(datetimes_array, heights_array/1000., lq_array, levels=levs, extend='both',
                          cmap='rainbow')
        # Contour only every 8th level (10^-2,10^-1,10^0)
        contour = ax3.contour(datetimes_array,heights_array/1000.,lq_array,levels=levs[8::8],colors='black')
    else:
        ax3.text(0.5,0.20,'NO DATA AVAILABLE',horizontalalignment='center')
        
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
    cb.set_label('Liquid (g m$^{-3}$)', fontsize = 15)  # 16 in field
    ax3.tick_params(axis='x',which='both',bottom='off',top='off')
    ax3.set_xticks([])
    axes.append(ax3)
    
    # RH
    ax4 = fig.add_subplot(4,1,4)
    if np.count_nonzero(np.isnan(rh_array)) != len(heights_array)*len(times_array):
        rh = ax4.contourf(datetimes_array, heights_array/1000., rh_array, levels=np.arange(0,110,5),
                          cmap='BrBG')
        contour = ax4.contour(datetimes_array,heights_array/1000.,rh_array,levels=np.array([40,60,80,90,99]))
    else:
        ax4.text(0.5,0.20,'NO DATA AVAILABLE',horizontalalignment='center')
    plt.clabel(contour,contour.levels,fmt='%1.f')
    cb = plt.colorbar(rh)
    cb.set_ticks(np.arange(0,110,20))
    cb.set_ticklabels(np.arange(0,110,20))
    cb.ax.tick_params(labelsize=13)  # 16 in field
    cb.set_label('RH (%)',fontsize=15)  # 16 in field
    
    ax4.set_xlabel('Time (UTC)', fontsize=15)  # 16 in field
    # Place x-label away from figure
    ax4.get_xaxis().set_label_coords(0.5,-0.25)
    # Add ticks at labeled times
    ax4.tick_params(axis='x',which='both',bottom='on',top='off')
    ax4.tick_params(axis='x', which='major', length=8)
    ax4.tick_params(axis='x', which='minor', length=4)
    ax4.set_xlim(curr_dt-timedelta(hours=24), datetimes_array[-1])
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
    plot_path = plot_parent_dir + 'nys_mwr_ts_qc/' + today_date
    if not os.path.exists(plot_path):
        os.mkdir(plot_path)
    plt.savefig(plot_path + '/ops.nys_mwr_ts.' + curr_dt_string + '.' + station.lower() + '.png',
                bbox_inches='tight')
    print('  Plotted MWR timeseries for ' + station)

    # Clear current figure and axes, and close window - this is probably redundant:-)
    plt.clf, plt.cla(), plt.close()

def lidar_field_plotting(station, station_name, lidar_df, field, logo_path, curr_dt):
    '''
    Takes in the lidar data and will produce a plot of either CNR, Horizonal Speed or Vertical Speed
    for a specific station.  Each plot will range from 100m to 3000m and will have wind barbs with the 
    direction of wind.
    
    Parameters:
    station (str): string of the 4 character station name.
    station_name (str): long name of station
    lidar_df (dataframe): pandas dataframe of lidar data for that station.
    field (string): must be one of ['cnr', 'w', 'velocity']
    logo_path (string): full path to logo file
    curr_dt (datetime) - current date & hour

    Returns:
    Plot of field data output to (plot_parent_dir + 'nys_lidar_<field>_qc/' + today_date)
    '''

    # Make sure input field is valid
    valid_fields = ['cnr','w','velocity']
    if field not in valid_fields:
        print('lidar field = {} not valid ... returning with no plot for {}.'.format(field,curr_dt))
        return
    
    # Make sure lidar_df is not full of NaN's
    empty_columns = []
    for col in lidar_df.columns:
        if lidar_df[col].count() == 0:
            empty_columns.append(col)
    if len(empty_columns) > 0:
        print('  lidar_df missing fields {} - no {} plot will be created.'.format(empty_columns,field))
        return

    # ---------------------------
    # GET DATA READY FOR PLOTTING
    # ---------------------------
    # Get times (which are second level index)
    times_df = pd.DataFrame(lidar_df.index.get_level_values('time'))
    times_array = np.array(times_df.drop_duplicates()['time'])
    if len(times_array) < min_times:
        print('  lidar_df has only {} times - no {} plot will be created.'.format(len(times_array),field))
        return
    datetimes_array = pd.to_datetime(times_array)

    # Get heights (which are first level index) between 100-3000m
    heights_df = pd.DataFrame(lidar_df.index.get_level_values('range'))
    heights_df = heights_df.loc[(heights_df['range'] >= 100) & (heights_df['range'] <= 3000)]
    # Flip array (highest to lowest value) for plotting
    heights_array = np.flip(np.array(heights_df.drop_duplicates()['range']))
    
    # Get start and stop time strings for plot title and current date string
    graphtimestamp_start=datetimes_array[0].strftime("%H UTC %m/%d/%y")
    graphtimestamp_end=curr_dt.strftime("%H UTC %m/%d/%y")
    today_date = curr_dt.strftime('%Y%m%d')

    # Initialize field_array (contains data in 'field' input param)
    field_array = np.zeros([len(heights_array),len(times_array)])
    
    # Create empty Uwind and Vwind arrays and fill with NaN's
    Uwind = np.full([len(heights_array),len(times_array)], np.nan)
    Vwind = np.full([len(heights_array),len(times_array)], np.nan)

    # Fill in field_array, Uwind and Vwind arrays
    for i in range(0,len(times_array)):
        for j in range(0,len(heights_array)):
            field_array[j,i] = lidar_df.loc[(heights_array[j],times_array[i]),field]
            direction = lidar_df.loc[(heights_array[j],times_array[i]),'direction']
            velocity = lidar_df.loc[(heights_array[j],times_array[i]),'velocity']
            #Take every other row and column of wind data 
            if (j % 2 == 0) and (i % 2 == 0):
                #direction is 450 degrees offset from plotting orientation
                #HOW DO WE KNOW THIS?
                Uwind[j,i] = np.cos((450. - direction)/180.*np.pi)*velocity 
                Vwind[j,i] = np.sin((450. - direction)/180.*np.pi)*velocity 

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
    ax.barbs(datetimes_array[::4],heights_array[::4]/1000.,Uwind[::4, ::4],Vwind[::4, ::4],length = 7)
    # Only plots black contour lines for vertical velocity or CNR data
    if field == 'w' or field == 'cnr':
        # Use every fourth level value
        contour = ax.contour(datetimes_array,heights_array/1000.,field_array,levels=levs[::4],colors='black')
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
    #ax.set_title('{} ({}) Lidar {}\n{} - {}'.format(station_name, station, field_title, graphtimestamp_start,
    #                                                            graphtimestamp_end), fontsize = 24)
    if field == 'cnr':
        plt.suptitle ('{} ({}) Lidar {}'.format(station_name, station,field_title), x = 0.47, fontsize = 22)
    elif field == 'w':
        plt.suptitle ('{} ({}) Lidar {}'.format(station_name, station,field_title), x = 0.465, fontsize = 22)
    elif field == 'velocity':
        plt.suptitle ('{} ({}) Lidar {}'.format(station_name, station,field_title), x = 0.465, fontsize = 22)        
    plt.title('{} - {}'.format(graphtimestamp_start, graphtimestamp_end), ha = 'center', fontsize = 18)

    # Set Y-axis height ticks  
    height_ticks = np.array([0.1,0.5,1,1.5,2,2.5,3])
    ax.set_yticks(height_ticks)
    ax.set_yticklabels(height_ticks, fontsize = 14)  # 16 in field
    ax.set_ylim(0.1,3)
    ax.set_ylabel('Height (km)', fontsize = 16)  # 20 in field
    
    # Set X-axis time ticks
    ax.set_xlabel('Time (UTC)', fontsize=16)  # 20 in field
    # DO WE NEED NEXT LINE?
    ax.tick_params(axis='x',which='both',bottom='on',top='off')                  #add ticks at labeled times

    ax.tick_params(axis='both', which='major', length=8)
    ax.tick_params(axis='both', which='minor', length=4)
    ax.yaxis.grid(linestyle = '--')
    ax.set_xlim(curr_dt-timedelta(hours=24), datetimes_array[-1])
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
    plot_path = plot_parent_dir + 'nys_lidar_' + save_name + '_qc/' + today_date
    if not os.path.exists(plot_path):
        os.mkdir(plot_path)
    plt.savefig(plot_path + '/ops.nys_lidar_' + save_name + '.' + curr_dt_string + '.' + station.lower() + '.png',
                bbox_inches='tight')
    print('  Plotted ' + field + ' Lidar' + ' for ' + station)

    # Clear current figure and axes, and close window - this is probably redundant:-)
    plt.clf, plt.cla(), plt.close()

def  plot_cloud_liquid(mwr_df, station, station_name, logo_path, curr_dt):
    '''
    Takes in a df with field variables integrated vapor, integrated liquid, cloud base (km), 
    and a rain flag of either 0.0 or 1.0.  Outputs a scatter plot of the df variables with the 
    left axis in kilometers and the right axis in mm liquid/ cm vapor.

    Parameters:
    mwr_df (dataframe): pandas dataframe of mwr precip data for that station.
    station (str): string of the 4 character station name.
    station_name (str): long name of station
    logo_path (string): full path to logo file
    curr_dt (datetime) - current date & hour
    
    Returns:
    Scatter plot output to (plot_parent_dir + 'nys_mwr_cloud_qc/' + today_date)
    '''
    
    # Make sure lidar_df is not full of NaN's
    empty_columns = []
    for col in mwr_df.columns:
        if mwr_df[col].count() == 0:
            empty_columns.append(col)
    if len(empty_columns) > 0:
        print('  mwr_df missing fields {} - no mwr cloud plot will be created.'.format(empty_columns))
        return

    # ---------------------------
    # GET DATA READY FOR PLOTTING
    # ---------------------------
    # Get times (which are first level index)
    # Can't use next two statements because index is not labelled
    #times_df = pd.DataFrame(mwr_df.index.get_level_values('time_integrated'))
    #times_array = np.array(times_df.drop_duplicates()['time_integrated'])
    times_df = pd.DataFrame(mwr_df.index.get_level_values(0).values)
    times_array = np.array(times_df.drop_duplicates()[0].values)
    if len(times_array) < min_times:
        print('  mwr_df has only {} times - no mwr cloud plot will be created.'.format(len(times_array)))
        return
    datetimes_array = pd.to_datetime(times_array)

    # Get start and stop time strings for plot title and current date string
    graphtimestamp_start=datetimes_array[0].strftime("%H UTC %m/%d/%y")
    graphtimestamp_end=curr_dt.strftime("%H UTC %m/%d/%y")
    today_date = curr_dt.strftime('%Y%m%d')
    
    # Get non-zero values of rain flag which represent rain
    rain = mwr_df['rain_flag'].values
    rain_indices = np.where( rain != 0.0 )[0]

    # -----------
    # CREATE PLOT
    # -----------
    fig, axL = plt.subplots(figsize = (9, 7.875))

    #axL.set_title('{} ({}) Derived MWR Products\n{} - {}'.format(
    #    station_name, station, graphtimestamp_start, graphtimestamp_end), fontsize = 24)    
    plt.suptitle('{} ({}) Derived MWR Products'.format(station_name, station), x = 0.57, fontsize = 24)
    plt.title('{} - {}'.format(graphtimestamp_start, graphtimestamp_end), ha = 'center', fontsize = 20)

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
    cb = axL.scatter(datetimes_array.values, mwr_df['cloud_base'].values,c='black') #in kms
    iv = axR.scatter(datetimes_array.values, mwr_df['integrated_vapor'].values,c='red')
    il = axR.scatter(datetimes_array.values, mwr_df['integrated_liquid'].values,c='blue')
    
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
        axR.legend((cb,iv,il) , ("Cloud Base","Integrated Vapor", "Integrated Liquid"), fontsize = 14)  # 16 in field
    
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
    axL.set_xlim(curr_dt-timedelta(hours=24), datetimes_array[-1])
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
    plot_path = plot_parent_dir + 'nys_mwr_cloud_qc/' + today_date
    if not os.path.exists(plot_path):
        os.mkdir(plot_path)
    plt.savefig(plot_path + '/ops.nys_mwr_cloud.' + curr_dt_string + '.' + station.lower() +'.png',
        bbox_inches='tight')
    print('  Plotted ' + 'MWR cloud/liquid profile' + ' for ' + station)
   
    # Clear current figure and axes, and close window - this is probably redundant:-)
    plt.clf, plt.cla(), plt.close()

def save_station_data(mwr_4plot_df,mwr_precip_df,lidar_df,station):
    '''
    Given a mwr dataframe of the 3 panel plot, a mwr dataframe of the precip parameter plot, 
    a lidar dataframe, and station ID, saves .csv files for that station.
    
    Parameters:
    mwr_4plot_df (dataframe): pandas dataframe of mwr containing T, Td, Lq, and RH data
    mwr_precip_df (dataframe): pandas dataframe of mwr containing T, Td, Lq, and RH data
    lidar_df (dataframe): pandas dataframe of lidar data
    
    Returns:
    csv files for mwr and lidar data
    '''
    
    mwr_3panel_times_df = pd.DataFrame(mwr_4plot_df.index.get_level_values(0).values)
    mwr_3panel_datetimes = pd.to_datetime(mwr_3panel_times_df[0].values)
    mwr_4plot_df['datetimes'] = mwr_3panel_datetimes
    mwr_4plot_df['range'] = mwr_4plot_df.index.get_level_values(1).values
    mwr_4plot_df['times'] = mwr_4plot_df.index.get_level_values(0).values
    mwr_4plot_df = mwr_4plot_df.set_index('datetimes')

    mwr_precip_times_df = pd.DataFrame(mwr_precip_df.index.values)
    mwr_precip_datetimes = pd.to_datetime(mwr_precip_times_df[0].values)
    mwr_precip_df['datetimes'] = mwr_precip_datetimes
    mwr_precip_df['times'] = mwr_precip_df.index.values
    mwr_precip_df = mwr_precip_df.set_index('datetimes')

    lidar_times_df = pd.DataFrame(lidar_df.index.get_level_values(1).values)
    lidar_datetimes_array_all = np.array(pd.to_datetime(lidar_times_df[0].values))
    lidar_datetimes_list_all = list(lidar_datetimes_array_all)

    lidar_df['datetimes'] = lidar_datetimes_list_all
    lidar_df['range'] = lidar_df.index.get_level_values(0).values
    lidar_df['times'] = lidar_df.index.get_level_values(1).values
    lidar_df = lidar_df.set_index('datetimes')
    
    latest = mwr_3panel_datetimes[-1] 
    lower_station = station.lower()
    
    # Define date in YYYYmmdd format (for saving and finding files)
    today_date = latest.strftime('%Y%m%d')

    # Define dates in YYYY-mm-dd format (for selecting ranges of data from dataframes)
    today_date_dt_format = latest.strftime('%Y-%m-%d')
    
    path0_mwr_dir = csv_mwr_dir+'/'+today_date
    path0_lidar_dir = csv_lidar_dir+'/'+today_date
    path0_mwr_3panel_file = path0_mwr_dir+'/ops.nys_mwr_thermo_profiler.'+today_date+'.'+lower_station+'.csv'
    path0_mwr_precip_file = path0_mwr_dir+'/ops.nys_mwr_precip_profiler.'+today_date+'.'+lower_station+'.csv'
    path0_lidar_file = path0_lidar_dir+'/ops.nys_lidar__profiler.'+today_date+'.'+lower_station+'.csv'
     
    if not os.path.exists(path0_mwr_dir):
        os.mkdir(path0_mwr_dir)
    if not os.path.exists(path0_lidar_dir):
        os.mkdir(path0_lidar_dir)
    if today_date == latest.strftime('%Y%m%d'):   #assure data exists for today before making today file
        today_mwr_3panel_data = mwr_4plot_df[today_date_dt_format]
        today_mwr_3panel_data.to_csv(path0_mwr_3panel_file)
        today_mwr_precip_data = mwr_precip_df[today_date_dt_format]
        today_mwr_precip_data.to_csv(path0_mwr_precip_file)
        print('saved MWR .csv file for '+station)
        today_lidar_data = lidar_df[today_date_dt_format]
        today_lidar_data.to_csv(path0_lidar_file)
        print('saved Lidar .csv file for '+station)
        
### MAIN CODE ###

# Set paths
indir = '/home/disk/data/albany/profiler'
plot_parent_dir = '/home/disk/funnel/impacts-website/archive/ops/'
#logo_path = '/home/disk/meso-home/jfinlon/impacts/mesonet/NYSM_logo_96x96.png'
logo_path = '/home/disk/bob/impacts/bin/NYS_mesonet/NYSM_logo_96x96.png'

# Number of contours for the LIDAR plots (must be a float)
bin_number = 20.

# Number of times required to create plot (usually there are 143 times so this is ~one quarter)
min_times = 35

# FOR REAL TIME USE
#curr_dt = datetime.utcnow(); curr_dt = curr_dt.replace(minute=0, second=0, microsecond=0)

# FOR TESTING & QC
#for month in range(1,3):
for month in range(2,3):
    if month == 1:
        first_day = 12
        last_day = 31
    elif month == 2:
        #first_day = 1
        first_day = 18
        last_day = 29
    for day in range(first_day,last_day+1):
        if month == 1 and day == first_day:
            #hours = range(4,24)
            hours = range(18,24)
        elif month == 2 and day == first_day:
            hours = range(8,24)
        else:
            hours = range(0,24)
        for hour in hours:
            print(datetime(2020,month,day,hour,0))

            #curr_dt = datetime(2020,2,6,21,0)
            curr_dt = datetime(2020,month,day,hour,0)
            
            curr_dt_string = datetime.strftime(curr_dt, '%Y%m%d%H%M')
            curr_date_string = datetime.strftime(curr_dt, '%Y%m%d')
            curr_hourMin_string = datetime.strftime(curr_dt, '%H%M')
            if curr_hourMin_string[:-1] == '000':
                create_netcdf = True
            else:
                create_netcdf = False

            #station_dict = {'ALBA': 'Albany, NY',
            #                'BELL': 'Belleville, NY',
            station_dict = {'BELL': 'Belleville, NY',
                            'BRON': 'Bronx, NY',
                            'BUFF': 'Buffalo, NY',
                            'CHAZ': 'Chazy, NY',
                            'CLYM': 'Clymer, NY',
                            'EHAM': 'East Hampton, NY',
                            'JORD': 'Jordan, NY',
                            'OWEG': 'Owego, NY',
                            'QUEE': 'Queens, NY',
                            'REDH': 'Red Hook, NY',
                            'STAT': 'Staten Island, NY',
                            'STON': 'Stony Brook, NY',
                            'SUFF': 'Suffern, NY',
                            'TUPP': 'Tupper Lake, NY',
                            'WANT': 'Wantagh, NY',
                            'WEBS': 'Webster, NY'}

            for station in station_dict.keys():
                print('Plotting and saving data for {} at {}.'.format(station,curr_dt))
                station_name = station_dict[station]
                mwr_4plot_df,mwr_precip_df,lidar_df,successMWR,successLidar = load_data(indir + '/' + curr_date_string,
                                                                                        station, curr_dt_string)
                
                # Create netcdf files - one each for lidar and MWR data
                if create_netcdf:
                    print('creating netcdf files from mwr_4plot_df, mwr_precip_df and lidar_df')
    
                # Create MWR plots
                if successMWR is True:
                    plot_mwr_ts(mwr_4plot_df,station, station_name, logo_path, curr_dt)
                    plot_cloud_liquid(mwr_precip_df, station, station_name, logo_path, curr_dt)

                # Create Lidar plots
                if successLidar is True:
                    lidar_field_plotting(station, station_name, lidar_df, 'cnr', logo_path, curr_dt)
                    lidar_field_plotting(station, station_name, lidar_df, 'w', logo_path, curr_dt)
                    lidar_field_plotting(station, station_name, lidar_df, 'velocity', logo_path, curr_dt)

                print('\n')
