#!/usr/bin/python3

"""
Created Feb 2020
@author: S. Brodzik

Modified Sep 2020
@author: S Brodzik
Added weather_cond_code variable to precip plot
"""

'''
ASOS_plot_data_for_archive.py
Make 3-day plots for a list of ASOS weather stations.
Data is read from csv files created by ASOS_get_data_for_archive.py

**File Saving Information**
3-day plots, every hour, save to: '/home/disk/funnel/impacts/archive/ops/asos_new'
'''
import os 
import pandas as pd 
import urllib 
import urllib.parse
import urllib.request
import csv 
import time
from datetime import datetime
from datetime import timedelta
import numpy as np 
import matplotlib 
from matplotlib.dates import DayLocator, HourLocator, DateFormatter
matplotlib.use('Agg') 
import matplotlib.transforms as transforms
import matplotlib.pyplot as plt 
import pickle

# Get sitelist
pickle_jar = '/home/disk/bob/impacts/bin/pickle_jar/'
infile = open(pickle_jar + "sitelist.pkl",'rb')
sitelist = pickle.load(infile)
infile.close()
# FOR TESTING
#sitelist = ['KCMH']
sitelist = ['KBGM']

# Get sitetitles
# NOTE: To get sitetitle for a specific site in sitelist use this:
# sitetitles[sitelist.index(<site>)]
infile2 = open(pickle_jar + 'sitetitles.pkl','rb')
sitetitles = pickle.load(infile2)
infile.close()
# FOR TESTING
#sitetitles = ['PORT COLUMBUS INTL AP']
sitetitles = ['BINGHAMTON GREATER AP']

# Get datelist
date_start_str = '20200101'
date_end_str = '20200229'
date_end_obj = datetime.strptime(date_end_str,'%Y%m%d')
date_str = date_start_str
date_obj = datetime.strptime(date_str,'%Y%m%d')
datelist = []
while date_obj <= date_end_obj:
    datelist.append(date_str)
    date_obj = date_obj + timedelta(days=1)
    date_str = date_obj.strftime('%Y%m%d')
# FOR TESTING
#datelist = ['20200112']
datelist = ['20200207']

# Directories of interest
csv_dir = '/home/disk/funnel/impacts/data_archive/asos_csv'
plot_dir = '/home/disk/funnel/impacts/archive/ops/asos_new'

def load_station_data(date,site):
    '''Given a site station ID, returns 3-day DataFrame of specified weather variables. 
    
    Parameters:
    site (str): string of ASOS station ID
    date (str): YYYYMMDD string for last of 3 days to plot
    
    Returns: 
    df (dataframe): dataframe containing last 72 hours (3 days) of ASOS station data 
    
    '''
    lower_site = site.lower()
    now = datetime.strptime(date,'%Y%m%d')
    
    # define dates to plot
    two_days_ago_date = (now-timedelta(hours=48)).strftime('%Y%m%d')
    yesterday_date = (now-timedelta(hours=24)).strftime('%Y%m%d')
    today_date = now.strftime('%Y%m%d')
    
    #defining dates in YYYY-mm-dd format (for selecting ranges of data from dataframes)
    two_days_ago_date_dt_format = (now-timedelta(hours=48)).strftime('%Y-%m-%d')
    yesterday_date_dt_format = (now-timedelta(hours=24)).strftime('%Y-%m-%d')
    today_date_dt_format = now.strftime('%Y-%m-%d')
    
    path2_dir = csv_dir+'/'+two_days_ago_date
    path1_dir = csv_dir+'/'+yesterday_date
    path0_dir = csv_dir+'/'+today_date
    
    path2_file = path2_dir+'/IMPACTS_ASOS_'+two_days_ago_date+'_'+lower_site+'.csv'
    path1_file = path1_dir+'/IMPACTS_ASOS_'+yesterday_date+'_'+lower_site+'.csv'
    path0_file = path0_dir+'/IMPACTS_ASOS_'+today_date+'_'+lower_site+'.csv'
    
    #figuring out if most of last 3-day data already exists, and if so, grabbing it from os
    if os.path.exists(path2_file) and os.path.exists(path1_file) and os.path.exists(path0_file):
        two_days_ago_all = pd.read_csv(path2_file)
        two_days_ago_all['time'] = pd.to_datetime(two_days_ago_all['time'])
        two_days_ago_all = two_days_ago_all.set_index('time')
        
        yesterday_all = pd.read_csv(path1_file)
        yesterday_all['time'] = pd.to_datetime(yesterday_all['time'])
        yesterday_all = yesterday_all.set_index('time')
        
        today_all = pd.read_csv(path0_file)
        today_all['time'] = pd.to_datetime(today_all['time'])
        today_all = today_all.set_index('time')

    else: 
        print('some data is missing -- go to next plot')
    
    # concatenate three DataFrame objects into one
    frames = [two_days_ago_all, yesterday_all, today_all]
    df = pd.concat(frames)
    
    return df

def plot_station_data(date,site,sitetitle,df):
    '''Given site station ID, the title of that site, and a dataframe of ASOS observation data from the last 3 days,
    returns a plot of the last 3-days of weather at that site. 
    
    Parameters: 
    site (str): string of ASOS station ID
    sitetitle (str): string of ASOS station full name 
    df (dataframe): dataframe containing last 72 hours (3 days) of ASOS station data 
    
    Returns: 
    None
    
    *saves plots to plot_dir listed near top of script*
    '''
    if isinstance(df, int): #Returns if the station is not reporting
        return
    
    lower_site = site.lower()
    timestamp_end=str(df.index[-1].strftime('%Y%m%d%H%M'))
    dt = df.index[:]
    dt_array = np.array(dt.values)
    graphtimestamp_start=dt[0].strftime("%m/%d/%y") 
    graphtimestamp=dt[-1].strftime("%m/%d/%y")      
    #now = datetime.datetime.utcnow()
    now = datetime.strptime(date,'%Y%m%d')
    today_date = dt[-1].strftime('%Y%m%d')
    markersize = 1.5
    linewidth = 1.0
    
    # Used for precip plot legend
    precip_types = {'lr':'Lt Rain',
                    'mr':'Mod Rain',
                    'hr':'Hvy Rain',
                    'lts':'Lt Snow',
                    'ms':'Mod Snow',
                    'hs':'Hvy Snow'}

    #make figure and axes
    fig = plt.figure()
    fig.set_size_inches(18,10)
    if 'snow_depth_set_1' in df.keys():          #six axes if snow depth 
        ax1 = fig.add_subplot(6,1,1)
        ax2 = fig.add_subplot(6,1,2,sharex=ax1)
        ax3 = fig.add_subplot(6,1,3,sharex=ax1)
        ax4 = fig.add_subplot(6,1,4,sharex=ax1)
        ax5 = fig.add_subplot(6,1,5,sharex=ax1)
        ax6 = fig.add_subplot(6,1,6,sharex=ax1)
        ax6.set_xlabel('Time (UTC)')
    else:
        ax1 = fig.add_subplot(5,1,1)             #five axes if no snow depth
        ax2 = fig.add_subplot(5,1,2,sharex=ax1)
        ax3 = fig.add_subplot(5,1,3,sharex=ax1)
        ax4 = fig.add_subplot(5,1,4,sharex=ax1)
        ax5 = fig.add_subplot(5,1,5,sharex=ax1)
        ax5.set_xlabel('Time (UTC)')
    
    #ax1.set_title(site+' '+sitetitle+' '+graphtimestamp_start+' - '+graphtimestamp+' '+now.strftime("%H:%MZ"))
    ax1.set_title(site+' '+sitetitle+' '+graphtimestamp_start+' - '+graphtimestamp)

    #------------------
    #plot airT and dewT
    #------------------
    if 'air_temp_set_1' in df.keys():
        airT = df['air_temp_set_1']
        ax1.plot_date(dt,airT,'o-',label="Temp",color="blue",linewidth=linewidth,markersize=markersize)  
    if 'dew_point_temperature_set_1d' in df.keys():
        dewT = df['dew_point_temperature_set_1d']
        ax1.plot_date(dt,dewT,'o-',label="Dew Point",color="black",linewidth=linewidth,markersize=markersize)
    elif 'dew_point_temperature_set_1' in df.keys():
        dewT = df['dew_point_temperature_set_1']
        dewT_new = dewT.dropna()
        dewT_dt_list = []
        for i in range(0,len(dewT)):
            if pd.isnull(dewT[i]) == False:
                dewT_dt_list.append(dt[i])
        ax1.plot_date(dewT_dt_list,dewT_new,'o-',label="Dew Point",color="black",linewidth=linewidth,markersize=markersize)
    if ax1.get_ylim()[0] < 0 < ax1.get_ylim()[1]:
        ax1.axhline(0, linestyle='-', linewidth = 1.0, color='deepskyblue')
        trans = transforms.blended_transform_factory(ax1.get_yticklabels()[0].get_transform(), ax1.transData)
        ax1.text(0,0,'0C', color="deepskyblue", transform=trans, ha="right", va="center") #light blue line at 0 degrees C
    ax1.set_ylabel('Temp ($^\circ$C)')
    ax1.legend(loc='best',ncol=2)
    axes = [ax1]                             #begin axes

    #----------------------------
    #plotting wind speed and gust
    #----------------------------
    if 'wind_speed_set_1' in df.keys():
        wnd_spd = df['wind_speed_set_1']
        ax2.plot_date(dt,wnd_spd,'o-',label='Speed',color="forestgreen",linewidth=linewidth,markersize=markersize)
    if 'wind_gust_set_1' in df.keys():
        wnd_gst = df['wind_gust_set_1']
        max_wnd_gst = wnd_gst.max(skipna=True)
        ax2.plot_date(dt,wnd_gst,'o-',label='Gust (Max ' + str(round(max_wnd_gst,1)) + 'kt)',color="red",linewidth=0.0,markersize=markersize) 
    ax2.set_ylabel('Wind (kt)')
    ax2.legend(loc='best',ncol=2)
    axes.append(ax2)
    
    #-----------------------
    #plotting wind direction
    #-----------------------
    if 'wind_direction_set_1' in df.keys():
        wnd_dir = df['wind_direction_set_1']
        ax3.plot_date(dt,wnd_dir,'o-',label='Direction',color="purple",linewidth=0.2, markersize=markersize)
    ax3.set_ylim(-10,370)
    ax3.set_ylabel('Wind Direction')
    ax3.set_yticks([0,90,180,270,360])
    axes.append(ax3)
    
    #-------------
    #plotting MSLP
    #-------------
    if 'sea_level_pressure_set_1d' in df.keys():
        mslp = df['sea_level_pressure_set_1d']
        max_mslp = mslp.max(skipna=True)
        min_mslp = mslp.min(skipna=True)
        labelname = 'Min ' + str(round(min_mslp,1)) + 'hPa, Max ' + str(round(max_mslp,2)) + 'hPa'
        ax4.plot_date(dt,mslp,'o-',label=labelname,color='darkorange',linewidth=linewidth,markersize=markersize)
    elif 'sea_level_pressure_set_1' in df.keys():
        mslp = df['sea_level_pressure_set_1']
        mslp_new = mslp.dropna()
        mslp_dt_list = []
        for i in range(0,len(mslp)):
            if pd.isnull(mslp[i]) == False:
                mslp_dt_list.append(dt[i])
        max_mslp = mslp.max(skipna=True)
        min_mslp = mslp.min(skipna=True)
        labelname = 'Min ' + str(round(min_mslp,2)) + 'hPa, Max ' + str(round(max_mslp,2)) + 'hPa'
        ax4.plot_date(mslp_dt_list,mslp_new,'o-',label=labelname,color='darkorange',linewidth=linewidth,markersize=markersize)
    ax4.legend(loc='best')
    ax4.set_ylabel('MSLP (hPa)')
    ax4.set_xlabel('Time (UTC)')
    axes.append(ax4)
    
    #-------------------------------------------
    #plotting precip accumulation & precip types
    #-------------------------------------------
    # Add weather_code info to plot
    # Determine indices in weather_code entries where lt/mod/hvy rain and snow exist
    if 'weather_code_1' in df.keys():
        code1 = df['weather_code_1'].values
        lt_rain_indices_1 = np.where( code1 == 13.0 )[0]
        mod_rain_indices_1 = np.where( code1 == 1.0 )[0]
        hvy_rain_indices_1 = np.where( code1 == 14.0 )[0]
        lt_snow_indices_1 = np.where( code1 == 20.0 )[0]
        mod_snow_indices_1 = np.where( code1 == 3.0 )[0]
        hvy_snow_indices_1 = np.where( code1 == 21.0 )[0]
    if 'weather_code_2' in df.keys():
        code2 = df['weather_code_2']
        lt_rain_indices_2 = np.where( code2 == 13.0 )[0]
        mod_rain_indices_2 = np.where( code2 == 1.0 )[0]
        hvy_rain_indices_2 = np.where( code2 == 14.0 )[0]
        lt_snow_indices_2 = np.where( code2 == 20.0 )[0]
        mod_snow_indices_2 = np.where( code2 == 3.0 )[0]
        hvy_snow_indices_2 = np.where( code2 == 21.0 )[0]
    if 'weather_code_3' in df.keys():
        code3 = df['weather_code_3']
        lt_rain_indices_3 = np.where( code3 == 13.0 )[0]
        mod_rain_indices_3 = np.where( code3 == 1.0 )[0]
        hvy_rain_indices_3 = np.where( code3 == 14.0 )[0]
        lt_snow_indices_3 = np.where( code3 == 20.0 )[0]
        mod_snow_indices_3 = np.where( code3 == 3.0 )[0]
        hvy_snow_indices_3 = np.where( code3 == 21.0 )[0]
    lt_rain_indices = np.concatenate((lt_rain_indices_1,lt_rain_indices_2,lt_rain_indices_3))
    mod_rain_indices = np.concatenate((mod_rain_indices_1,mod_rain_indices_2,mod_rain_indices_3))
    hvy_rain_indices = np.concatenate((hvy_rain_indices_1,hvy_rain_indices_2,hvy_rain_indices_3))
    lt_snow_indices = np.concatenate((lt_snow_indices_1,lt_snow_indices_2,lt_snow_indices_3))
    mod_snow_indices = np.concatenate((mod_snow_indices_1,mod_snow_indices_2,mod_snow_indices_3))
    hvy_snow_indices = np.concatenate((hvy_snow_indices_1,hvy_snow_indices_2,hvy_snow_indices_3))

    # Plot color coding for represented precip types 
    indices = {'lr':0,'mr':0,'hr':0,'lts':0,'ms':0,'hs':0}
    if len(lt_rain_indices) > 0:
        indices['lr'] = 1
        for rainy_time in dt_array[lt_rain_indices][:-1]:
            ax5.axvline(rainy_time,color = 'xkcd:pale green',alpha=.5)
        lr = ax5.axvline(dt_array[lt_rain_indices][-1],color = 'xkcd:pale green',alpha=.5)
    if len(mod_rain_indices) > 0:
        indices['mr'] = 1
        for rainy_time in dt_array[mod_rain_indices][:-1]:
            ax5.axvline(rainy_time,color = 'xkcd:hospital green',alpha=.5)
        mr = ax5.axvline(dt_array[mod_rain_indices][-1],color = 'xkcd:hospital green',alpha=.5)
    if len(hvy_rain_indices) > 0:
        indices['hr'] = 1
        for rainy_time in dt_array[hvy_rain_indices][:-1]:
            ax5.axvline(rainy_time,color = 'xkcd:tree green',alpha=.5)
        hr = ax5.axvline(dt_array[hvy_rain_indices][-1],color = 'xkcd:tree green',alpha=.5)
    if len(lt_snow_indices) > 0:
        indices['lts'] = 1
        for snowy_time in dt_array[lt_snow_indices][:-1]:
            ax5.axvline(snowy_time,color = 'xkcd:pale blue',alpha=.5)
        lts = ax5.axvline(dt_array[lt_snow_indices][-1],color = 'xkcd:pale blue',alpha=.5)
    if len(mod_snow_indices) > 0:
        indices['ms'] = 1
        for snowy_time in dt_array[mod_snow_indices][:-1]:
            ax5.axvline(snowy_time,color = 'xkcd:pastel blue',alpha=.5)
        ms = ax5.axvline(dt_array[mod_snow_indices][-1],color = 'xkcd:pastel blue',alpha=.5)
    if len(hvy_snow_indices) > 0:
        indices['hs'] = 1
        for snowy_time in dt_array[hvy_snow_indices][:-1]:
            ax5.axvline(snowy_time,color = 'xkcd:cobalt blue',alpha=.5)
        hs = ax5.axvline(dt_array[hvy_snow_indices][-1],color = 'xkcd:cobalt blue',alpha=.5)

    # Create legend for precip types that are represented
    legend = []
    for key in indices.keys():
        if indices[key] == 1:
            legend.append(key)
    if len(legend) == 1:
        eval('ax5.legend(('+legend[0]+') , ("'+precip_types[legend[0]]+'"), fontsize = 8)')
    elif len(legend) == 2:
        eval('ax5.legend(('+legend[0]+','+legend[1]+') , ("'+precip_types[legend[0]]+'","'+precip_types[legend[1]]+'"), fontsize = 8)')
    elif len(legend) == 3:        
        eval('ax5.legend(('+legend[0]+','+legend[1]+','+legend[2]+') , ("'+precip_types[legend[0]]+'","'+precip_types[legend[1]]+'","'+precip_types[legend[2]]+'"), fontsize = 8)')
    elif len(legend) == 4:        
        eval('ax5.legend(('+legend[0]+','+legend[1]+','+legend[2]+','+legend[3]+') , ("'+precip_types[legend[0]]+'","'+precip_types[legend[1]]+'","'+precip_types[legend[2]]+'","'+precip_types[legend[3]]+'"), fontsize = 8)')
    elif len(legend) == 5:        
        eval('ax5.legend(('+legend[0]+','+legend[1]+','+legend[2]+','+legend[3]+','+legend[4]+') , ("'+precip_types[legend[0]]+'","'+precip_types[legend[1]]+'","'+precip_types[legend[2]]+'","'+precip_types[legend[3]]+'","'+precip_types[legend[4]]+'"), fontsize = 8)')
    elif len(legend) == 6:        
        eval('ax5.legend(('+legend[0]+','+legend[1]+','+legend[2]+','+legend[3]+','+legend[4]+','+legend[5]+') , ("'+precip_types[legend[0]]+'","'+precip_types[legend[1]]+'","'+precip_types[legend[2]]+'","'+precip_types[legend[3]]+'","'+precip_types[legend[4]]+'","'+precip_types[legend[5]]+'"), fontsize = 8)')
    #ax5.legend((lr,mr,hr) , ("Lt Rain","Mod Rain", "Hvy Rain"), fontsize = 8)  # 16 in field

    # Plot precip time series
    if 'precip_intervals_set_1d' in df.keys():
        precip_inc = df['precip_intervals_set_1d']
        precip_inc_new = precip_inc.dropna()
        precip_inc_new = list(precip_inc_new.values)
        precip_accum = 0.0
        precip_accum_list = []
        for increment in precip_inc_new:
            precip_accum = precip_accum + increment
            precip_accum_list.append(precip_accum)
        precip_dt_list = []
        for i in range(0,len(precip_inc)):
            if pd.isnull(precip_inc[i]) == False:
                precip_dt_list.append(dt[i])
        max_precip = max(precip_accum_list)
        labelname = 'Precip (' + str(round(max_precip,2)) + 'mm)'
        # Commented out to allow precip/snow legend
        #ax5.plot_date(precip_dt_list,precip_accum_list,'o-',label=labelname,color='navy',linewidth=linewidth,markersize=markersize)
        ax5.plot_date(precip_dt_list,precip_accum_list,'o-',color='navy',linewidth=linewidth,markersize=markersize)
        if max_precip > 0:
            ax5.set_ylim(-0.1*max_precip,max_precip+max_precip*0.2)
        else:
            ax5.set_ylim(-0.5,5)
    # Commented out to allow precip/snow legend
    #ax5.legend(loc='best')
    # Next line needed for 2 legends but not sure how to implement
    #ax5.gca().add_artist(legend1)
    ax5.set_ylabel('Precip (mm)')
    axes.append(ax5)
    
    #-------------------
    #plotting snow depth
    #-------------------
    if 'snow_depth_set_1' in df.keys():
        snow_depth = df['snow_depth_set_1']
        snow_depth_new = snow_depth.dropna()
        snow_depth_dt_list = []
        for i in range(0,len(snow_depth)):
            if pd.isnull(snow_depth[i]) == False:
                snow_depth_dt_list.append(dt[i])  
        max_snow_depth = snow_depth.max(skipna=True)
        min_snow_depth = snow_depth.min(skipna=True)
        labelname = 'Min Depth ' + str(round(min_snow_depth,2)) + 'mm, Max Depth ' + str(round(max_snow_depth,2)) + 'mm'
        ax6.plot_date(snow_depth_dt_list,snow_depth_new,'o-',label=labelname,color='deepskyblue',linewidth=linewidth,markersize=markersize)
        if max_snow_depth > 0:
            ax6.set_ylim(-0.1*max_snow_depth,max_snow_depth+max_snow_depth*0.2)
        else:
            ax6.set_ylim(-0.5,5)
        ax6.legend(loc='best')
        ax6.set_ylabel('Snow Depth (mm)')
        axes.append(ax6)
        
    # Axes formatting
    for ax in axes: 
        ax.spines["top"].set_visible(False)  #darker borders on the grids of each subplot
        ax.spines["right"].set_visible(False)  
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.tick_params(axis='x',which='both',bottom='on',top='off')     #add ticks at labeled times
        ax.tick_params(axis='y',which='both',left='on',right='off') 

        ax.xaxis.set_major_locator( DayLocator() )
        ax.xaxis.set_major_formatter( DateFormatter('%b-%d') )
        
        ax.xaxis.set_minor_locator( HourLocator(np.linspace(6,18,3)) )
        ax.xaxis.set_minor_formatter( DateFormatter('%H') )
        ax.fmt_xdata = DateFormatter('Y%m%d%H%M%S')
        ax.yaxis.grid(linestyle = '--')
        ax.get_yaxis().set_label_coords(-0.06,0.5)

    # Write plot to file
    plot_path = plot_dir+'/'+today_date
    if not os.path.exists(plot_path):
            os.makedirs(plot_path)
    try:
        plt.savefig(plot_path+'/ops.asos.'+timestamp_end+'.'+lower_site+'.png',bbox_inches='tight')
    except:
        print("Problem saving figure for %s. Usually a maxticks problem" %site)
    plt.close()

for date in datelist:
    print(f'date = {date}')
    for isite,site in enumerate(sitelist):
        sitetitle = sitetitles[isite]
        print(f'site = {site} and sitetitle = {sitetitle}')
        df = load_station_data(date,site)
        plot_station_data(date,site,sitetitle,df)
