#!/usr/bin/python3

"""
Created Feb 2020
@author: S. Brodzik
"""
'''
ASOS_plot_data_KALX.py
Make 1-day plots for a list of ASOS weather stations.
Data is read from csv files created by ASOS_get_data_KALX.py

**File Saving Information**
1-day plots, one per day, save to: '/home/disk/funnel/impacts/archive/ops/asos_1day'
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

# sites and dates of interest
sitelist = {'KACY':'ATLANTIC CITY INTL AP',
            'KADW':'JOINT BASE ANDREWS AP',
            'KAHN':'ATHENS BEN EPPS GA AP',
            'KAVC':'MECKLENBURG BRUNSWICK RGNL AP',
            'KAVL':'ASHEVILLE RGNL AP',
            'KCDW':'ESSEX COUNTY AP',
            'KCEW':'BOB SIKES-EGLIN AFB AP',
            'KCHA':'LOVELL FIELD CHATTANOOGA AP',
            'KCHS':'CHARLESTON AFB INTL AP',
            'KCKB':'CLARKSBURG BENEDUM AP',
            'KCQX':'CHATHAM MUNI AP',
            'KDAN':'DANVILLE RGNL AP',
            'KEXX':'DAVIDSON COUNTY AP',
            'KFBG':'SIMMONS FT BRAGGS AF',
            'KFFC':'ATLANTA REG AP FALCON FIELD',
            'KGAD':'NE ALABAMA REG AP',
            'KGZH':'EVERGREEN REG AP-MIDDLETON FIELD',
            'KHFF':'MACKALL ARMY AF',
            'KHKY':'HICKORY REG AP',
            'KHLX':'TWIN COUNTY VA AP',
            'KHSE':'BILLY MITCHELL HATTERAS AP',
            'KHTS':'HUNTINGTON TRI-STATE AP',
            'KHWO':'NORTH PERRY HOLLYWOOD AP',
            'KINT':'SMITH REYNOLDS WINST-SALEM AP',
            'KISP':'ISLIP-LI MACARTHUR AP',
            'KLEE':'LEESBURG INTL AP',
            'KLSF':'LAWSON ARMY FT BENNING AF',
            'KLYH':'LYNCHBURG INTL AP',
            'KMAI':'MARIANNA MUNI AP',
            'KMGM':'MONTGOMERY REG AP',
            'KMOB':'MOBILE REG AP',
            'KMSY':'LOUIS ARMSTRONG NEW ORLEANS INTL AP',
            'KMYR':'MYRTLE BEACH INTL AP',
            'KNEL':'LAKEHURST MAXFIELD AP',
            'KNFE':'FENTRESS NAVAL AUX FIELD',
            'KNGU':'NORFOLK NAS',
            'KNMM':'MERIDIAN NAS',
            'KNSE':'WHITING FIELD NAS NORTH',
            'KOFP':'MIAMI-OPA LOCKA EXEC AP',
            'KOXB':'OCEAN CITY MUNI AP',
            'KOXC':'WATERBURY-OXFORD AP',
            'KPAM':'TYNDALL AFB AP',
            'KPIB':'HATTIESBURG-LAUREL REG AP',
            'KRHP':'WESTERN CAROLINA REG AP',
            'KRIC':'RICHMOND INTL AP',
            'KROA':'ROANOKE INTL AP',
            'KRWI':'ROCKY MOUNT-WILSON REG AP',
            'KSBY':'SALISBURY-WICOMICO RGNL AP',
            'KSSC':'SHAW AFB AP',
            'KTCL':'TUSCALOOSA AL AP',
            'KTRI':'TRI-CITIES TN AP',
            'KTYS':'MCGHEE TYSON AP',
            'KVPC':'CARTERSVILLE AP',
            'KWRB':'WARNER-ROBINS AFP AP',
            'KWST':'WESTERLY STATE AP',
            'KWWD':'CAPE MAY COUNTY AP'}
#            '42002':'',
#            '42036':'',
#            '42039':'',
#            '42040':'',
#            '42395':''}
datelist = ['20200207']

csv_dir = '/home/disk/funnel/impacts/data_archive/asos_csv'
plot_dir = '/home/disk/funnel/impacts/archive/ops/asos_1day'

def load_station_data(date,site):
    '''Given a site station ID, returns 1-day DataFrame of specified weather variables. 
    
    Parameters:
    site (str): string of ASOS station ID
    date (str): YYYYMMDD string for last of 3 days to plot
    
    Returns: 
    df (dataframe): dataframe containing last 24 hours (1 days) of ASOS station data 
    
    '''
    lower_site = site.lower()
    now = datetime.strptime(date,'%Y%m%d')
    
    # define date to plot
    today_date = now.strftime('%Y%m%d')
    
    # define date in YYYY-mm-dd format (for selecting ranges of data from dataframes)
    today_date_dt_format = now.strftime('%Y-%m-%d')

    # define data path and filename
    path0_dir = csv_dir+'/'+today_date
    path0_file = path0_dir+'/ops.asos.'+today_date+'.'+lower_site+'.csv'
    
    if os.path.exists(path0_file):
        today_all = pd.read_csv(path0_file)
        today_all['time'] = pd.to_datetime(today_all['time'])
        today_all = today_all.set_index('time')
    else: 
        print('some data is missing -- go to next plot')
    
    # concatenate three DataFrame objects into one
    frames = [today_all]
    df = pd.concat(frames)
    
    return df

def plot_station_data(date,site,sitetitle,df):
    '''Given site station ID, the title of that site, and a dataframe of ASOS observation data from the last 1 day,
    returns a plot of the last day of weather at that site. 
    
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
    graphtimestamp_start=dt[0].strftime("%m/%d/%y %H:%M") 
    graphtimestamp=dt[-1].strftime("%m/%d/%y %H:%M")      
    #now = datetime.datetime.utcnow()
    now = datetime.strptime(date,'%Y%m%d')
    today_date = dt[-1].strftime('%Y%m%d')
    markersize = 1.5
    linewidth = 1.0
    
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
    
    ax1.set_title(site+' '+sitetitle+' '+graphtimestamp_start+' - '+graphtimestamp)
    #plot airT and dewT
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

    #plotting wind speed and gust
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
    
    #plotting wind direction
    if 'wind_direction_set_1' in df.keys():
        wnd_dir = df['wind_direction_set_1']
        ax3.plot_date(dt,wnd_dir,'o-',label='Direction',color="purple",linewidth=0.2, markersize=markersize)
    ax3.set_ylim(-10,370)
    ax3.set_ylabel('Wind Direction')
    ax3.set_yticks([0,90,180,270,360])
    axes.append(ax3)
    
    #plotting MSLP
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
    
    #plotting precip accumulation
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
        ax5.plot_date(precip_dt_list,precip_accum_list,'o-',label=labelname,color='navy',linewidth=linewidth,markersize=markersize)
        if max_precip > 0:
            ax5.set_ylim(-0.1*max_precip,max_precip+max_precip*0.2)
        else:
            ax5.set_ylim(-0.5,5)
    ax5.legend(loc='best')
    ax5.set_ylabel('Precip (mm)')
    axes.append(ax5)
    
    #plotting snow depth
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
    for site in sitelist.keys():
        sitetitle = sitelist[site]
        print(f'site = {site} and sitetitle = {sitetitle}')
        df = load_station_data(date,site)
        plot_station_data(date,site,sitetitle,df)
