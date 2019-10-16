
# coding: utf-8

# In[98]:


#!/usr/bin/env python3
"""
Created September 2019
@author: masonf3 (Mason Friedman)
"""
'''
NYS_profiler_save_and_plot.py
Make 1-day plots and saves daily .csv files of key weather variables for NYS Profiler stations.
Some code modified from Joe Zagrodnik's 'plot_mesowest_3day.py', used for similar task in the OLYMPEX field campaign.
Code to read in data developed by Nathan Bain's 'read_profiler_data.py', used at NYS Mesonet.

**File Saving Information**
CSV files, one per day, save to: *insert Stacy's directory*
1-day plots, one per hour, save to: *insert Stacy's directory*
'''
import os 
import json            #javascript object notation encoder and decoder
import pandas as pd
import time, datetime, glob
from time import strftime 
from datetime import timedelta
import numpy as np 
import matplotlib 
get_ipython().magic('matplotlib inline')
from matplotlib.dates import DayLocator, HourLocator, DateFormatter
matplotlib.use('Agg') 
import matplotlib.transforms as transforms
import matplotlib.pyplot as plt 
import xarray as xr


# In[106]:

#Defining directories
indir = '/home/disk/data/albany/profiler/'
#csv_mwr_dir = *insert Stacy's directory where mwr files are saved*
#csv_lidar_dir = *insert Stacy's directory where lidar files are saved*
#plot_mwr_dir = *insert Stacy's directory where mwr plots are saved*
#plot_lidar_dir = *insert Stacy's directory where lidar plots are saved*

#indir = '/home/disk/meso-home/masonf3/IMPACTS/profiler/*'                    #for testing
#csv_mwr_dir = '/home/disk/meso-home/masonf3/IMPACTS/csv_test_prof/MWR'        #for testing
#csv_lidar_dir = '/home/disk/meso-home/masonf3/IMPACTS/csv_test_prof/Lidar'    #for testing
#plot_mwr_dir = '/home/disk/meso-home/masonf3/IMPACTS/plot_test_prof/MWR'      #for testing
#plot_lidar_dir = '/home/disk/meso-home/masonf3/IMPACTS/plot_test_prof/Lidar'  #for testing


# In[100]:

#calculations
def e_calc(Td):
    '''Given dew point, returns vapor pressure.
    
    Parameters:
    Td (float): Dew point temperature, in degrees C
    
    Returns:
    e (float): vapor pressure, in hPa
    '''
    e = 6.11*10**((7.5*Td)/(237.3+Td))
    return e
    
def vapor_density_calc(e,T):
    '''Given vapor pressure and temperature, returns vapor density (a.k.a. absolute humidity)
    
    Parameters:
    e (float): vapor pressure, in hPa
    T (float): temperature, in degrees Celsius
    
    Returns:
    Vd (float): vapor density, in kg/m^3
    '''
    e_Pa = e*100 #Pa (kg*m^-1*s^-2)
    T_kelvin = T+273.15 #K
    Rw = 461 #J*K^-1*kg^-1 (m^2*s^-2*K^-1)
    Vd = e_Pa/(Rw*T_kelvin) #kg/m^-3
    return Vd

def rel_humidity_calc(Td,T):
    '''Given dew point temperature and actual temperature, returns a relative humidity value.
    
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


# In[101]:

def load_data(path,station):
    '''Given filepath to data stream with .json files and a profiler station, returns a dataframe with
    microwave radiometer data and lidar data, plus the station name.
    
    Parameters:
    path (filepath): path to directory where data, in .json files, comes in
    station (str): string of station ID
    
    Returns:
    mwr_df (dataframe): pandas dataframe of microwave radiometer data for that station
    lidar_df (dataframe): pandas dataframe of lidar data for that station
    '''
    mwr = None
    lidar = None
    file_list = glob.glob(path+'*.json')     #all json files in path directory
    file_list.sort()                      
    latest_file = file_list[-1]
    latest_file_start = latest_file[0:latest_file.find('PROF_')+5]
    file = latest_file_start+station+'.json'
    
    with open(file, "r") as f:
        data = json.load(f)
        try:
            mwr = data['mwr']
            mwr = xr.Dataset.from_dict(mwr)
            mwr = xr.decode_cf(mwr)
            mwr_df = mwr.to_dataframe()
            mwr_df = pd.DataFrame(mwr_df)
        except:
            print("Problem reading microwave radiometer data for "+station)
            mwr_df = []
            mwr_df = pd.DataFrame(mwr_df)

        try:
            lidar = data['lidar']
            lidar = xr.Dataset.from_dict(lidar)
            lidar = xr.decode_cf(lidar)
            lidar_df = lidar.to_dataframe()
            lidar_df = pd.DataFrame(lidar_df)
        except:
            print("Problem reading lidar data for "+station)
            lidar_df = []
            lidar_df = pd.DataFrame(lidar_df)
    
    return mwr_df,lidar_df,station


# In[102]:

def plot_mwr(mwr_df,station):
    '''Given microwave radiometer dataframe and a station ID, saves plot of mwr profiler data for the last day at
    that station
    
    Parameters: 
    mwr_df (dataframe): pandas dataframe of microwave radiometer data for that station
    station (str): string of station ID
    
    Returns:
    None
    '''
    heights_df = pd.DataFrame(mwr_df.index.get_level_values(0).values)
    heights_array = pd.array(heights_df.drop_duplicates()[0].values)
    times_df = pd.DataFrame(mwr_df.index.get_level_values(1).values)
    times_array = pd.array(times_df.drop_duplicates()[0].values)
    datetimes_array = pd.to_datetime(times_array)
    
    graphtimestamp_start=datetimes_array[0].strftime("%m/%d/%y")        #start date, for fig title
    graphtimestamp_end=datetimes_array[-1].strftime("%m/%d/%y")         #end date, for fig title
    timestamp_end = datetimes_array[-1].strftime('%Y%m%d%H%M')          #timestamp end for saving plots
    today_date = datetimes_array[-1].strftime('%Y%m%d')
    lower_station = station.lower()

    temps_array = np.zeros([len(heights_array),len(times_array)])
    dewT_array = np.zeros([len(heights_array),len(times_array)])
    pres_lvl_array = np.zeros([len(heights_array),len(times_array)])
    
    for i in range(0,len(heights_array)):
        for j in range(0,len(times_array)):
            temps_array[i,j] = mwr_df.loc[(heights_array[i],times_array[j]),'temperature']
            dewT_array[i,j] = mwr_df.loc[(heights_array[i],times_array[j]),'dew_point']
            pres_lvl_array[i,j] = mwr_df.loc[(heights_array[i],times_array[j]),'pressure_level']
        
    Vd_array = vapor_density_calc(e_calc(dewT_array),temps_array)      
    RH_array = rel_humidity_calc(dewT_array,temps_array)
    
    fig = plt.figure(figsize = (28,16))
    fig.suptitle(station+' Microwave Radiometer '+ graphtimestamp_start+' - '+graphtimestamp_end,x=0.44, y = 0.92)
    
    axes = []
    ax1 = fig.add_subplot(3,1,1)
    ax1.set_title('Temperature')
    temp = ax1.contourf(datetimes_array,heights_array,temps_array,levels=np.arange(-50,51,2),cmap='nipy_spectral')
    contour = ax1.contour(datetimes_array,heights_array,temps_array,levels=[0],colors='white')
    plt.clabel(contour,fmt='%1.f')
    cb = plt.colorbar(temp)
    cb.set_ticks(np.arange(-50,51,10))
    cb.set_ticklabels(np.arange(-50,51,10))
    cb.set_label('degrees C')
    axes.append(ax1)

    '''
    #add Liquid data here
    ax2 = fig.add_subplot(4,1,2)
    ax2.set_title('Liquid')
    #ax2.contourf(datetimes_array,heights_array,Lq_array)
    axes.append(ax2)
    '''
    
    ax3 = fig.add_subplot(3,1,2)
    ax3.set_title('Vapor Density')
    vapor = ax3.contourf(datetimes_array,heights_array,Vd_array*1000,levels=np.arange(0,26,1),cmap='rainbow')
    cb = plt.colorbar(vapor)
    cb.set_ticks(np.arange(0,26,5))
    cb.set_ticklabels(np.arange(0,26,5))
    cb.set_label('g/m^3')
    axes.append(ax3)

    ax4 = fig.add_subplot(3,1,3)
    ax4.set_title('Relative Humidity')
    rh = ax4.contourf(datetimes_array,heights_array,RH_array,levels=np.arange(0,110,5),cmap='BrBG')
    contour = ax4.contour(datetimes_array,heights_array,RH_array,levels=[100])
    plt.clabel(contour,fmt='%1.f')
    cb = plt.colorbar(rh)
    cb.set_ticks(np.arange(0,110,20))
    cb.set_ticklabels(np.arange(0,110,20))
    cb.set_label('percent')
    ax4.set_xlabel('Time (UTC)')
    ax4.get_xaxis().set_label_coords(0.5,-0.20)                         #properly places x-label away from figure
    axes.append(ax4)

    for ax in axes:
        ax.set_ylabel('Height (m)')
        ax.tick_params(axis='x',which='both',bottom='on',top='off')     #add ticks at labeled times
        ax.tick_params(axis='y',which='both',left='on',right='off') 
        ax.yaxis.grid(linestyle = '--')   
        ax.xaxis.set_major_locator( DayLocator() )                      #one date written per day
        ax.xaxis.set_major_formatter( DateFormatter('%b-%d') )          #show date, written as 'Jul-12'
        ax.xaxis.set_minor_locator( HourLocator(byhour=range(2,24,2)) ) #hour labels every 6 hours
        ax.xaxis.set_minor_formatter( DateFormatter('%H') )             #show hour labels
        ax.get_yaxis().set_label_coords(-0.04,0.5)                      #properly places y-labels away from figure
       
    plot_path = plot_mwr_dir+'/'+today_date
    if not os.path.exists(plot_path):
            os.mkdir(plot_path)
    plt.savefig(plot_path+'/ops.nys_mwr_profiler.'+timestamp_end+'.'+lower_station+'.png',bbox_inches='tight')
    plt.close()
    print('plotted MWR for ' + station)


# In[103]:

def plot_lidar(lidar_df,station):
    '''Given lidar dataframe and a station ID, saves plot of lidar profiler data for the last day at
    that station
    
    Parameters: 
    lidar_df (dataframe): pandas dataframe of lidar data for that station
    station (str): string of station ID
    
    Returns:
    None
    '''
    heights_df = pd.DataFrame(lidar_df.index.get_level_values(0).values)
    heights_array = np.array(heights_df.drop_duplicates()[0].values)
    heights_list = list(heights_array)
    heights_array = heights_array[0:(heights_list.index(3000)+1)]
    
    times_df = pd.DataFrame(lidar_df.index.get_level_values(1).values)
    times_array = np.array(times_df.drop_duplicates()[0].values)
    datetimes_array = pd.to_datetime(times_array)
    
    graphtimestamp_start=datetimes_array[0].strftime("%m/%d/%y")        #start date, for fig title
    graphtimestamp_end=datetimes_array[-1].strftime("%m/%d/%y")         #end date, for fig title
    timestamp_end = datetimes_array[-1].strftime('%Y%m%d%H%M')          #timestamp end for saving plots
    today_date = datetimes_array[-1].strftime('%Y%m%d')
    lower_station = station.lower()
    
    hws_array = np.zeros([len(heights_array),len(times_array)])
    wind_dir_array = np.zeros([len(heights_array),len(times_array)])
    pres_lvl_array = np.zeros([len(heights_array),len(times_array)])
        
    for i in range(0,len(heights_array)):
        for j in range(0,len(times_array)):
            hws_array[i,j] = lidar_df.loc[(heights_array[i],times_array[j]),'velocity']
            wind_dir_array[i,j] = lidar_df.loc[(heights_array[i],times_array[j]),'direction']
            pres_lvl_array[i,j] = lidar_df.loc[(heights_array[i],times_array[j]),'pressure_level']
        
    fig = plt.figure(figsize = (28,16))
    fig.suptitle(station + ' Lidar ' + graphtimestamp_start + ' - ' + graphtimestamp_end, x=0.44, y=0.92)
    
    axes = []
    '''
    #Add CNR data here
    ax1 = fig.add_subplot(4,1,1)
    ax1.set_title('CNR')
    cnr = ax1.contourf(datetimes_array,heights_array,cnr_array,levels=np.arange(-35,10,0.1),cmap='')
    cb = plt.colorbar(temp)
    cb.set_ticks(np.arange(-35,10,5))
    cb.set_ticklabels(np.arange(-35,10,5))
    cb.set_label('dB')
    axes.append(ax1)
    '''

    ax2 = fig.add_subplot(2,1,1)
    ax2.set_title('Horizontal Wind Speed')
    hws = ax2.contourf(datetimes_array,heights_array,hws_array,levels=np.arange(0,101,5),cmap='nipy_spectral')
    contour = ax2.contour(datetimes_array,heights_array,hws_array,levels = [30]) #blizzard condition wind contour
    plt.clabel(contour,fmt='%1.f')
    cb = plt.colorbar(hws, pad = 0.2)
    cb.set_ticks(np.arange(0,101,20))
    cb.set_ticklabels(np.arange(0,101,20))
    cb.set_label('knots')
    axes.append(ax2)            
    
    '''
    #Add vertical wind speed data here
    ax3 = fig.add_subplot(4,1,3)
    ax3.set_title('Vertical Wind Speed')
    vws = ax3.contourf(datetimes_array,heights_array,vws_array,levels=np.arange(0,5,0.5),cmap='bwr')
    cb = plt.colorbar(vapor)
    cb.set_ticks(np.arange(0,5,1))
    cb.set_ticklabels(np.arange(0,5,1))
    cb.set_label('knots')
    axes.append(ax3)
    '''

    ax4 = fig.add_subplot(2,1,2)
    ax4.set_title('Wind Direction')
    rh = ax4.contourf(datetimes_array,heights_array,wind_dir_array,levels=np.arange(0,361,3),cmap='hsv')
    cb = plt.colorbar(rh)
    cb.set_ticks(np.arange(0,361,30))
    cb.set_ticklabels(np.arange(0,361,30))
    cb.set_label('degrees')
    ax4.set_xlabel('Time (UTC)')
    ax4.get_xaxis().set_label_coords(0.5,-0.20)                         #properly places x-label away from figure
    axes.append(ax4)
    
    for ax in axes:
        ax.set_ylabel('Height (m)')
        ax.tick_params(axis='x',which='both',bottom='on',top='off')     #add ticks at labeled times
        ax.tick_params(axis='y',which='both',left='on',right='off') 
        ax.yaxis.grid(linestyle = '--')   
        ax.xaxis.set_major_locator( DayLocator() )                      #one date written per day
        ax.xaxis.set_major_formatter( DateFormatter('%b-%d') )          #show date, written as 'Jul-12'
        ax.xaxis.set_minor_locator( HourLocator(byhour=range(2,24,2)) ) #hour labels every 6 hours
        ax.xaxis.set_minor_formatter( DateFormatter('%H') )             #show hour labels
        ax.get_yaxis().set_label_coords(-0.06,0.5)                      #properly places y-labels away from figure

    plot_path = plot_lidar_dir+'/'+today_date
    if not os.path.exists(plot_path):
            os.mkdir(plot_path)
    plt.savefig(plot_path+'/ops.nys_lidar_profiler.'+timestamp_end+'.'+lower_station+'.png',bbox_inches='tight')
    plt.close()
    print('plotted Lidar for ' + station)


# In[104]:

def save_station_data(mwr_df,lidar_df,station):
    '''Given a microwave radiometer dataframe, a lidar dataframe, and station ID, saves .csv files
    for that station.
    
    Parameters:
    mwr_df (dataframe): pandas dataframe of microwave radiometer data for that station
    lidar_df (dataframe): pandas dataframe of lidar data for that station
    
    Returns:
    None
    '''
    mwr_times_df = pd.DataFrame(mwr_df.index.get_level_values(1).values)
    mwr_times_array = pd.array(mwr_times_df.drop_duplicates()[0].values)
    mwr_datetimes_array_all = pd.array(pd.to_datetime(mwr_times_df[0].values))
    mwr_datetimes_list_all = list(mwr_datetimes_array_all)
    mwr_datetimes_array = pd.to_datetime(mwr_times_array)
    mwr_df['datetimes'] = mwr_datetimes_list_all
    mwr_df['range'] = mwr_df.index.get_level_values(0).values
    mwr_df['times'] = mwr_df.index.get_level_values(1).values
    mwr_df = mwr_df.set_index('datetimes')
    
    lidar_times_df = pd.DataFrame(lidar_df.index.get_level_values(1).values)
    lidar_times_array = pd.array(lidar_times_df.drop_duplicates()[0].values)
    lidar_datetimes_array_all = pd.array(pd.to_datetime(lidar_times_df[0].values))
    lidar_datetimes_list_all = list(lidar_datetimes_array_all)
    lidar_datetimes_array = pd.to_datetime(lidar_times_array)
    lidar_df['datetimes'] = lidar_datetimes_list_all
    lidar_df['range'] = lidar_df.index.get_level_values(0).values
    lidar_df['times'] = lidar_df.index.get_level_values(1).values
    lidar_df = lidar_df.set_index('datetimes')
    
    latest = mwr_datetimes_list_all[-1] 
    lower_station = station.lower()
    
    #definining date in YYYYmmdd format (for saving and finding files)
    today_date = latest.strftime('%Y%m%d')
    
    #defining dates in YYYY-mm-dd format (for selecting ranges of data from dataframes)
    today_date_dt_format = latest.strftime('%Y-%m-%d')
    
    path0_mwr_dir = csv_mwr_dir+'/'+today_date
    path0_lidar_dir = csv_lidar_dir+'/'+today_date
    path0_mwr_file = path0_mwr_dir+'/ops.nys_mwr_profiler.'+today_date+'.'+lower_station+'.csv'
    path0_lidar_file = path0_lidar_dir+'/ops.nys_lidar_profiler.'+today_date+'.'+lower_station+'.csv'
     
    if not os.path.exists(path0_mwr_dir):
        os.mkdir(path0_mwr_dir)
    if not os.path.exists(path0_lidar_dir):
        os.mkdir(path0_lidar_dir)
    if today_date == latest.strftime('%Y%m%d'):   #assure data exists for today before making today file
        today_mwr_data = mwr_df[today_date_dt_format]
        today_mwr_data.to_csv(path0_mwr_file)
        print('saved MWR .csv file for '+station)
        today_lidar_data = lidar_df[today_date_dt_format]
        today_lidar_data.to_csv(path0_lidar_file)
        print('saved Lidar .csv file for '+station)


# In[105]:

#station_list = ['BRON'] #for testing
station_list = ['ALBA','BELL','BRON','BUFF','CHAZ','CLYM','EHAM','JORD','OWEG','QUEE','REDH','STAT','STON','SUFF','TUPP','WANT','WEBS']
for station in station_list:
    mwr_df,lidar_df,station = load_data(indir,station)
    if mwr_df.empty is False:
        plot_mwr(mwr_df,station)
    if lidar_df.empty is False:
        plot_lidar(lidar_df,station)
    if mwr_df.empty is False and lidar_df.empty is False:
        save_station_data(mwr_df,lidar_df,station)
print('Finished saving and plotting all stations')


# In[ ]:



