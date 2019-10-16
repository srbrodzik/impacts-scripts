
# coding: utf-8

# In[1]:

#!/usr/bin/env python3

"""
Created August/September 2019
@author: masonf3
"""
'''NYS_mesonet_save_and_plot.py
Make 3-day plots and save daily .csv files of key weather variables for NYS mesonet stations (126 stations in network)
Data is read from UW Atmospheric Sciences LDM server
Some code modified from Joe Zagrodnik's 'plot_mesowest_3day.py', used for similar task in the OLYMPEX field campaign

**File Saving Information**
CSV files, one per day, save to: '/home/disk/funnel/impacts/data_archive/nys_ground' 
3-day plots, one each time code is run, save to: '/home/disk/funnel/impacts/archive/ops/nys_ground'
'''
import os 
import pandas as pd 
import csv 
import time, datetime, glob 
from time import strftime 
from datetime import timedelta
import numpy as np 
import matplotlib 
from matplotlib.dates import DayLocator, HourLocator, DateFormatter
matplotlib.use('Agg') 
import matplotlib.transforms as transforms
import matplotlib.pyplot as plt


# In[9]:

#define directories
indir = '/home/disk/data/albany/standard/*'                                      #where the LDM server loads data to
savedir = '/home/disk/bob/impacts/bin/saved'                                     #folder containing pickle files 
station_info = '/home/disk/funnel/impacts/data_archive/nys_ground/meta_nysm.csv' #file containing station lat/lon/alt
csv_dir = '/home/disk/funnel/impacts/data_archive/nys_ground'                    #save csv files here
plot_dir = '/home/disk/funnel/impacts/archive/ops/nys_ground'                    #save plots here 
#indir = '/home/disk/meso-home/masonf3/IMPACTS/standard/*'                        #test - where I copied from LDM server 
#savedir = '/home/disk/meso-home/masonf3/IMPACTS/saved'                           #test - folder containing pickle files
#station_info = '/home/disk/meso-home/masonf3/IMPACTS/station_info/nysm.csv'      #test - file containing station lat/lon/alt
#csv_dir = '/home/disk/meso-home/masonf3/IMPACTS/csv_test_NYS'                    #test - csv directory
#plot_dir = '/home/disk/meso-home/masonf3/IMPACTS/plot_test_NYS'                  #test - plot directory


# In[10]:

def vapor_pressure_calc(T,RH):
    '''Given temperature and relative humidity, returns vapor pressure.
    From https://www.weather.gov/media/epz/wxcalc/vaporPressure.pdf 
    
    Parameters: 
    T (float): temperature, in degrees celsius
    RH (float): relative humidity, in %
                
    Returns: 
    e (float): vapor pressure, in (find out)
    es (float): saturation vapor pressure, in (find out)
    '''
    es = 6.11 * 10**((7.5*T)/(237.3+T)) #saturation vapor pressure calculation
    e = (RH/100) * es                   #current vapor pressure calculation (using RH)
    return e,es

def Td_calc(es,RH):
    '''Given saturation vapor pressure and relative humidity, returns dew point temperature.
    From https://www.weather.gov/media/epz/wxcalc/vaporPressure.pdf
    
    Parameters: 
    es (float): saturation vapor presure, in (find out)
    RH (float): relative humidity, in %

    Returns: 
    Td (float): dew point temperature, in degrees celsius
    '''
    Td = (237.3*np.log((es*RH)/611))/(7.5*np.log(10)-np.log((es*RH)/611))
    return Td

def Tmv_calc(e,p,Tm):
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

def mslp_calc(Tmv,zs,p):
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


# In[11]:

def load_data(path):
    '''Given a filepath with timeseries of .csv files, return a dataframe containing data from the last three full days 
    to the present. Also returns a list of site station IDs in the observation network. 
    
    Parameters: 
    path (str): filepath to directory containing observation data .csv files which are added in time.
    
    Returns:
    all_data (dataframe): a dataframe of all obs data from three days ago, two days ago, yesterday, and today,
    indexed by datetime and containing station elevation data. 
    sitelist (list): a list of site station IDs in the NYS mesonet network
    '''
    file_list = glob.glob(path)                                 #all files in path directory
    file_list.sort()                                            #sort file list
    latest_file = file_list[-1]                                 #most recent data file
   
    station_info_data = pd.read_csv(station_info)               #read station info from .csv file 
    station_info_data = station_info_data.set_index('stid')     #index by station id 
    
    df = pd.read_csv(latest_file)                               #read latest weather data from NYS mesonet
    df = df.set_index('station')                                #temporary index by station id for new data
    for i in df.index:                                          #add elev, station full names to new data 
        df.loc[i,'station_elevation [m]'] = station_info_data.loc[i,'elevation [m]']
        df.loc[i,'name'] = station_info_data.loc[i,'name']
    df = df.reset_index()                                       #reset new data index
    df['datetime'] = pd.to_datetime(df['time'],format='%Y-%m-%d %H:%M:%S UTC') #add column for datetime object
    new_df = df.set_index('datetime')                           #set new data index to datetime 
    
    today_pickle = new_df.index[-1].strftime('%Y%m%d')+'.pkl'
    yesterday_pickle = (new_df.index[-1]-timedelta(days=1)).strftime('%Y%m%d')+'.pkl'
    two_days_ago_pickle = (new_df.index[-1]-timedelta(days=2)).strftime('%Y%m%d')+'.pkl'
    three_days_ago_pickle = (new_df.index[-1]-timedelta(days=3)).strftime('%Y%m%d')+'.pkl'
    
    if os.path.isfile(savedir+'/'+today_pickle):                                
        from_file = pd.read_pickle(savedir+'/'+today_pickle)
        today_data = from_file.append(new_df,ignore_index=False) #append latest NYS data to previous NYS data
        today_data.to_pickle(savedir+'/'+today_pickle)
        all_data = today_data
        if os.path.isfile(savedir+'/'+yesterday_pickle):
            yesterday_data = pd.read_pickle(savedir+'/'+yesterday_pickle)
            all_data = pd.concat([today_data,yesterday_data],ignore_index=False)
            if os.path.isfile(savedir+'/'+two_days_ago_pickle):
                two_days_ago_data = pd.read_pickle(savedir+'/'+two_days_ago_pickle)
                all_data = pd.concat([all_data,two_days_ago_data],ignore_index=False)
                if os.path.isfile(savedir+'/'+three_days_ago_pickle):
                    three_days_ago_data = pd.read_pickle(savedir+'/'+three_days_ago_pickle)
                    all_data = pd.concat([all_data,three_days_ago_data],ignore_index=False)
    else:
        today_data = new_df
        today_data.to_pickle(savedir+'/'+today_pickle)
        all_data = today_data
        if os.path.isfile(savedir+'/'+yesterday_pickle):
            yesterday_data = pd.read_pickle(savedir+'/'+yesterday_pickle)
            all_data = pd.concat([today_data,yesterday_data],ignore_index=False)
            if os.path.isfile(savedir+'/'+two_days_ago_pickle):
                two_days_ago_data = pd.read_pickle(savedir+'/'+two_days_ago_pickle)
                all_data = pd.concat([all_data,two_days_ago_data],ignore_index=False)
                if os.path.isfile(savedir+'/'+three_days_ago_pickle):
                    three_days_ago_data = pd.read_pickle(savedir+'/'+three_days_ago_pickle)
                    all_data = pd.concat([all_data,three_days_ago_data],ignore_index=False)
            
    all_data = all_data.drop_duplicates(['station','time'],keep='last')
    all_data = all_data.sort_values(by=['station','time'],ascending=True) 
    
    sitelist = list(df['station'].drop_duplicates())            #a list of site IDs for later use
    
    return all_data, sitelist


# In[12]:

def calculate_derived_data(all_data,site):
    '''Given a dataframe of NYS weather data, calculates new dataframe columns of dew point and mean sea-level pressure.
    
    *Note: MSLP calculations will be slightly incorrect for the very first 12 hours of data ever read by this script 
    because calculations should use 12 hour average ambient temperature rather than observed temp in the formula*

    Parameters: 
    all_data (dataframe): a dataframe of all obs data from three days ago, two days ago, yesterday, and today,
    indexed by datetime and containing station elevation data
    site (str): site station ID for a station in the NYS mesonet network
    
    Returns: 
    site_data (dataframe): pandas dataframe containing all data, both directly observed and calculated, 
    for a specific station 
    '''
    site_data = all_data.loc[all_data['station'] == site]
    if 'relative_humidity [percent]' and 'temp_2m [degC]' in site_data.keys():
        e,es = vapor_pressure_calc(site_data['temp_2m [degC]'],site_data['relative_humidity [percent]']) 
        Td = Td_calc(es,site_data['relative_humidity [percent]'])  
        site_data['dew_point_temp_2m [degC]'] = Td                          #add calculated dew point to new data  
        if 'station_pressure [mbar]' and 'station_elevation [m]' in site_data.keys(): 
            for dt in site_data.index[:]:
                if dt-timedelta(hours=12) in site_data.index[:]:                                          
                    first_dt = dt-timedelta(hours=12)
                    Tm = (site_data['temp_2m [degC]'][first_dt]+site_data['temp_2m [degC]'][dt])/2 #if 12hr+ data exists 
                else:                                                     
                    Tm = site_data['temp_2m [degC]'][dt]                    #if not 12hr+ of data                  
                Tmv =  Tmv_calc(e[dt],site_data['station_pressure [mbar]'][dt],Tm) #calc average virtual temp
                mslp = mslp_calc(Tmv,site_data['station_elevation [m]'][dt],site_data['station_pressure [mbar]'][dt])
                site_data.loc[dt,'mean_sea_level_pressure [mbar]'] = mslp   #add calculated mslp to data frame
    site_data = site_data.drop_duplicates(['station','time'],keep='last')   #drop duplicate data
    
    return site_data                                            


# In[13]:

def save_station_data(site_data):
    '''Given a pandas dataframe containing all weather data for a specific station, this function saves
    a day's worth of data into a .csv file for that station, within a folder for that day. 
    
    Parameters:
    site_data (dataframe): pandas dataframe containing all data, both directly observed and calculated, 
    for a specific station 
    
    Returns: 
    None
    
    *Saves .csv files to csv_dir listed near top of script*
    '''
    latest = site_data.index[-1]
    site = site_data['station'][0] 
    lower_site = site.lower()
    
    #definining dates in YYYYmmdd format (for saving and finding files)
    yesterday_date = (latest-timedelta(hours=24)).strftime('%Y%m%d')
    today_date = latest.strftime('%Y%m%d')
    
    #defining dates in YYYY-mm-dd format (for selecting ranges of data from dataframes)
    yesterday_date_dt_format = (latest-timedelta(hours=24)).strftime('%Y-%m-%d')
    today_date_dt_format = latest.strftime('%Y-%m-%d')
    
    path1_dir = csv_dir+'/'+yesterday_date
    path0_dir = csv_dir+'/'+today_date
    path1_file = path1_dir+'/ops.nys_ground.'+yesterday_date+'.'+lower_site+'.csv'
    path0_file = path0_dir+'/ops.nys_ground.'+today_date+'.'+lower_site+'.csv'

    # ********  PROBLEM WITH THIS COMMAND ********
    if yesterday_date in site_data.index.strftime('Y%m%d'):
        if not os.path.exists(path1_dir):
            os.mkdir(path1_dir)
        if not os.path.exists(path1_file):  
            yesterday_data = site_data[yesterday_date_dt_format]
            yesterday_data.to_csv(path1_file)
     
    if not os.path.exists(path0_dir):
        os.mkdir(path0_dir)
    if today_date == latest.strftime('%Y%m%d'):   #assure data exists for today before making today file
        today_data = site_data[today_date_dt_format]
        today_data.to_csv(path0_file)
    print('saved ' + site + ' csv')


# In[17]:

def plot_station_data(site_data):
    '''Given a pandas dataframe containing all weather data for a specific station, this function saves a plot with
    the last 3 days worth of weather data for that station (or as much data as available if not yet 3-days). 
    
    Parameters:
    site_data (dataframe): pandas dataframe containing all data, both directly observed and calculated, 
    for a specific station 
    
    Returns:
    None 
    
    *saves plots to plot_dir listed near top of script*
    '''
    latest = site_data.index[-1]
    site = site_data['station'][0]
    lower_site = site.lower()
    site_slice = site_data.loc[site_data.index >= (latest-timedelta(hours=72))] #slice data to last 72hrs
    timestamp_end = site_slice.index[-1].strftime('%Y%m%d%H%M') #timestamp end for saving .csv files 
    dt = site_slice.index[:]                                #define dt for making subplots 
    sitetitle = site_slice['name'][0]                       #define sitetitle for fig title
    graphtimestamp_start=dt[0].strftime("%m/%d/%y")         #start date, for fig title
    graphtimestamp=dt[-1].strftime("%m/%d/%y")              #end date, for fig title
    markersize = 1.5                                        #markersize, for subplots
    linewidth = 1.0                                         #linewidth, for subplots
    fig = plt.figure()                                      #create figure
    fig.set_size_inches(10,10)                              #size figure
    
    if max(site_slice['snow_depth [cm]']) > 0:              #six axes if there is snow depth
        ax1 = fig.add_subplot(6,1,1)
        ax2 = fig.add_subplot(6,1,2,sharex=ax1)
        ax3 = fig.add_subplot(6,1,3,sharex=ax1)
        ax4 = fig.add_subplot(6,1,4,sharex=ax1)
        ax5 = fig.add_subplot(6,1,5,sharex=ax1)
        ax6 = fig.add_subplot(6,1,6,sharex=ax1)
        ax6.set_xlabel('Time (UTC)')                        
    else:                                                   #five axes if no snow depth
        ax1 = fig.add_subplot(5,1,1)                            
        ax2 = fig.add_subplot(5,1,2,sharex=ax1)
        ax3 = fig.add_subplot(5,1,3,sharex=ax1)
        ax4 = fig.add_subplot(5,1,4,sharex=ax1)
        ax5 = fig.add_subplot(5,1,5,sharex=ax1)
        ax5.set_xlabel('Time (UTC)')                        
    
    ax1.set_title(site+' '+sitetitle+', NY '+graphtimestamp_start+' - '+graphtimestamp) #title figure 
    #plot airT and dewT
    if 'temp_2m [degC]' in site_slice.keys():
        airT = site_slice['temp_2m [degC]']
        ax1.plot_date(dt,airT,'o-',label="Temp",color="blue",linewidth=linewidth,markersize=markersize) 
    if 'dew_point_temp_2m [degC]' in site_slice.keys():
        Td = site_slice['dew_point_temp_2m [degC]']
        ax1.plot_date(dt,Td,'o-',label="Dew Point",color="black",linewidth=linewidth,markersize=markersize)
    if ax1.get_ylim()[0] < 0 < ax1.get_ylim()[1]:
        ax1.axhline(0, linestyle='-', linewidth = 1.0, color='deepskyblue')
        trans = transforms.blended_transform_factory(ax1.get_yticklabels()[0].get_transform(), ax1.transData)
        ax1.text(0,0,'0C', color="deepskyblue", transform=trans, ha="right", va="center") #light blue line at 0 degrees C
    ax1.set_ylabel('2m Temp ($^\circ$C)')
    ax1.legend(loc='best',ncol=2)
    axes = [ax1]                                                #begin axes list

    #plot wind speed and gust
    if 'avg_wind_speed_merge [m/s]' in site_slice.keys():
        wnd_spd = site_slice['avg_wind_speed_merge [m/s]'] * 1.94384 #convert to knots
        ax2.plot_date(dt,wnd_spd,'o-',label='Speed',color="forestgreen",linewidth=linewidth,markersize=markersize)
    if 'max_wind_speed_merge [m/s]' in site_slice.keys():
        wnd_gst = site_slice['max_wind_speed_merge [m/s]'] * 1.94384 #convert to knots
        max_wnd_gst = wnd_gst.max(skipna=True)
        ax2.plot_date(dt,wnd_gst,'o-',label='Gust (Max ' + str(round(max_wnd_gst,1)) + 'kt)',color="red",linewidth=linewidth,markersize=markersize)
    ax2.set_ylabel('Wind (kt)')
    ax2.legend(loc='best',ncol=2)
    axes.append(ax2)
    
    #plot wind direction
    if 'wind_direction_merge [degree]' in site_slice.keys():
        wnd_dir = site_slice['wind_direction_merge [degree]']
        ax3.plot_date(dt,wnd_dir,'o-',label='Direction',color="purple",linewidth=0.2, markersize=markersize)
    ax3.set_ylim(-10,370)
    ax3.set_ylabel('Wind Direction')
    ax3.set_yticks([0,90,180,270,360])                          #locking y-ticks for wind direction 
    axes.append(ax3)
    
    #plot MSLP (or station pressure, if MSLP unavailable)
    if 'mean_sea_level_pressure [mbar]' in site_slice.keys():
        mslp = site_slice['mean_sea_level_pressure [mbar]']
        min_mslp = mslp.min(skipna=True)                        #min 3-day mslp value
        max_mslp = mslp.max(skipna=True)                        #max 3-day mslp value
        labelname = 'Min ' + str(round(min_mslp,2)) + 'hPa, Max ' + str(round(max_mslp,2)) + 'hPa'
        ax4.plot_date(dt,mslp,'o-',label=labelname,color='darkorange',linewidth=linewidth,markersize=markersize)
        ax4.set_ylabel('MSLP (hPa)')
    elif 'station_pressure [mbar]' in site_slice.keys():                                                   
        sp = site_slice['station_pressure [mbar]']
        min_sp = sp.min(skipna=True)                            #min 3-day station pressure value
        max_sp = sp.max(skipna=True)                            #max 3-day station pressure value
        labelname = 'Min ' + str(round(min_sp,2)) + 'hPa, Max ' + str(round(max_sp,2)) + 'hPa'
        ax4.plot_date(dt,sp,'o-',label=labelname,color='darkorange',linewidth=linewidth,markersize=markersize)
        ax4.set_ylabel('STATION Pressure (hPa)')
        print('unable to get mslp, used station pressure instead')
    ax4.legend(loc='best')
    axes.append(ax4)

    #plot precip accum
    if 'precip_incremental [mm]' in site_slice.keys():
        precip_inc = site_slice['precip_incremental [mm]']
        precip_accum = 0.0
        precip_accum_list = []
        for increment in precip_inc:                            #calculate precip accumulation 
            precip_accum = precip_accum + increment
            precip_accum_list.append(precip_accum)
        max_precip = max(precip_accum_list)
        labelname = 'Precip (' + str(round(max_precip,2)) + 'mm)'
        ax5.plot_date(dt,precip_accum_list,'o-',label=labelname,color='navy',linewidth=linewidth,markersize=markersize)
        if max_precip > 0:
            ax5.set_ylim(-0.1*max_precip,max_precip+max_precip*0.2)
        else:
            ax5.set_ylim(-0.5,5)
    ax5.legend(loc='best')
    ax5.set_ylabel('Precip (mm)')
    axes.append(ax5)
    
    #plot snow depth
    if 'snow_depth [cm]' in site_slice.keys() and max(site_slice['snow_depth [cm]']) > 0:
        snow_depth = site_slice['snow_depth [cm]'] * 10         #convert to mm
        max_snow_depth = snow_depth.max(skipna=True)
        min_snow_depth = snow_depth.min(skipna=True)
        labelname = 'Min Depth ' + str(round(min_snow_depth,2)) + 'mm, Max Depth ' + str(round(max_snow_depth,2)) + 'mm'
        ax6.plot_date(dt,snow_depth,'o-',label=labelname,color='deepskyblue',linewidth=linewidth,markersize=markersize)
        ax6.set_ylim(-0.1*max_snow_depth,max_snow_depth+max_snow_depth*0.2)
        if max_snow_depth > 0:
            ax5.set_ylim(-0.1*max_snow_depth,max_snow_depth+max_snow_depth*0.2)
        ax6.legend(loc='best')
        ax6.set_ylabel('Snow Depth (mm)')
        axes.append(ax6)
                        
    for ax in axes: 
        ax.spines["top"].set_visible(False)                             #remove dark borders on subplots
        ax.spines["right"].set_visible(False)  
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.tick_params(axis='x',which='both',bottom='on',top='off')     #add ticks at labeled times
        ax.tick_params(axis='y',which='both',left='on',right='off') 
        ax.xaxis.set_major_locator( DayLocator() )                      #one date written per day
        ax.xaxis.set_major_formatter( DateFormatter('%b-%d') )          #show date, written as 'Jul-12'
        ax.xaxis.set_minor_locator( HourLocator(np.linspace(6,18,3)) )  #hour labels every 6 hours
        ax.xaxis.set_minor_formatter( DateFormatter('%H') )             #show hour labels
        ax.fmt_xdata = DateFormatter('Y%m%d%H%M%S')                     #fixes labels
        ax.yaxis.grid(linestyle = '--')                                 #adds y-axis grid lines
        ax.get_yaxis().set_label_coords(-0.06,0.5)                      #properly places y-labels away from figure
    
    #define dates in YYYYmmdd format (for saving and finding files)
    three_days_ago_date = (latest-timedelta(hours=72)).strftime('%Y%m%d')
    two_days_ago_date = (latest-timedelta(hours=48)).strftime('%Y%m%d')
    yesterday_date = (latest-timedelta(hours=24)).strftime('%Y%m%d')
    today_date = latest.strftime('%Y%m%d')
    
    plot_path = plot_dir+'/'+today_date
    if not os.path.exists(plot_path):
            os.mkdir(plot_path)
    plt.savefig(plot_path+'/ops.nys_ground.'+timestamp_end+'.'+lower_site+'.png',bbox_inches='tight')
    plt.close()
    print('plotted ' + site)


# In[18]:

all_data,sitelist = load_data(indir)
print('Done reading data')
for site in sitelist:
    print('site = '+site)
    site_data = calculate_derived_data(all_data,site)
    save = save_station_data(site_data)
    plot = plot_station_data(site_data)
print('All NYS Mesonet ground data plotted and saved')


# In[ ]:



