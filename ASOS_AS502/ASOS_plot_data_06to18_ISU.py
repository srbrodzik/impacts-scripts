#!/usr/bin/python3

"""
Created Feb 2020
@author: S. Brodzik

Modified Sep 2020
@author: S Brodzik
NEW: Added weather_cond_code variable to precip plot

Modified Apr 2022
@author: S Brodzik
NEW: Used for AS502 time series
"""

'''
ASOS_plot_data_1day_ISU.py
Make 1-day plots for a list of ASOS weather stations.
Data is read from csv files created by ASOS_get_site_data_from_ISU_for502.py

**File Saving Information**
1-day plots, one per day, save to: '/home/disk/funnel/impacts/archive/ops/asos_1day_isu'
'''
import os
import sys
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
from metpy.plots import (StationPlot, StationPlotLayout, wx_code_map, current_weather)

if len(sys.argv) != 3:
    print('Usage: sys.argv[0] [startdate(YYYYMMDD)] [enddate(YYYYMMDD)]')
    sys.exit()
else:
    date_start_str = sys.argv[1]
    date_end_str = sys.argv[2]

test = False
debug = True

"""
sitelist = {'KAOO':'ALTOONA-BLAIR CTY AP',
            'KAVL':'ASHEVILLE REG AP',
            'KBFM':'MOBILE DOWNTOWN AP',
            'KBGM':'GTR BINGHAMTON AP',
            'KBKW':'RALEIGH CTY MEM AP',
            'KEKN':'ELKINS-RANDOLPH CTY AP',
            'KELZ':'WELLSVILLE MUN AP',
            'KFFC':'ATLANTA REG AP',
            'KGAD':'NE ALABAMA REG AP',
            'KGEV':'ASHE CTY AP',
            'KGPT':'GULFPORT-BILOXI INTL AP',
            'KHKY':'HICKORY REG AP',
            'KLZU':'GWINNETT CTY AP',
            'KMSY':'LOUIS ARMSTRONG NEW ORLEANS INTL AP',
            'KMXF':'MAXWELL AFB',
            'KPIL':'PORT ISABEL-CAMERON CTY AP',
            'KRMG':'RUSSELL REG AP',
            'KROA':'ROANOKE-BLACKSBURG REG AP',
            'KROC':'ROCHESTER GTR INTL',
            'KTRI':'TRI-CITIES AP'}

sitelist = {'KAOO':'Altoona PA',
            'KAVL':'Asheville NC',
            'KBFM':'Mobile AL',
            'KBGM':'Binghamton NY',
            'KBKW':'Beckley WV',
            'KEKN':'Elkins WV',
            'KELZ':'Wellsville NY',
            'KFFC':'Atlanta GA',
            'KGAD':'Gadsden AL',
            'KGEV':'Jefferson NC',
            'KGPT':'Gulfport MS',
            'KHKY':'Hickory NC',
            'KLZU':'Lawrenceville GA',
            'KMSY':'New Orleans LA',
            'KMXF':'Montgomery AL',
            'KPIL':'Port Isabel TX',
            'KRMG':'Rome GA',
            'KROA':'Roanoke VA',
            'KROC':'Rochester NY',
            'KTRI':'Kingsport TN'}
"""
sitelist = {'KAKQ':'Wakefield VA',
            'KFIG':'Clearfield PA',
            'KHSE':'Hatteras NC',
            'KECG':'Elizabeth City NC',
            'KCTZ':'Clinton NC',
            'KLBE':'Latrobe PA'}

date_end_obj = datetime.strptime(date_end_str,'%Y%m%d')
date_str = date_start_str

date_obj = datetime.strptime(date_str,'%Y%m%d')
datelist = []
while date_obj <= date_end_obj:
    datelist.append(date_str)
    date_obj = date_obj + timedelta(days=1)
    date_str = date_obj.strftime('%Y%m%d')
print('{} {}'.format('datelist =',datelist))

# Directories of interest
csv_dir = '/home/disk/bob/impacts/raw/asos_isu'
plot_dir = '/home/disk/bob/impacts/images/asos_isu'

#From metpy.plots.wxsymbols:
wx_codes = {'': 0, 'M': 0, 'TSNO': 0, 'TS': 0, 'VA': 4, 'FU': 4, 'HZ': 5,
            'DU': 6, 'BLDU': 7, 'PO': 8, 'VCSS': 9, 'BR': 10,
            'MIFG': 11, 'VCTS': 13, 'VIRGA': 14, 'VCSH': 16,
            '-VCTSRA': 17, 'VCTSRA': 17, '+VCTSRA': 17,
            'THDR': 17, 'SQ': 18, 'FC': 19, 'DS': 31, 'SS': 31,
            '+DS': 34, '+SS': 34, 'DRSN': 36, '+DRSN': 37, 'BLSN': 38,
            '+BLSN': 39, 'VCFG': 40, 'BCFG': 41, 'PRFG': 44, 'FG': 45,
            'FZFG': 49, '-DZ': 51, 'DZ': 53, '+DZ': 55, '-FZDZ': 56,
            'FZDZ': 57, '+FZDZ': 57, '-DZRA': 58, 'DZRA': 59, '-RA': 61,
            'RA': 63, '+RA': 65, '-FZRA': 66, 'FZRA': 67, '+FZRA': 67,
            '-RASN': 68, 'RASN': 69, '+RASN': 69, '-SN': 71, 'SN': 73,
            '+SN': 75, 'IN': 76, '-UP': 76, 'UP': 76, '+UP': 76, 'SG': 77,
            'IC': 78, '-PL': 79, 'PL': 79, '-SH': 80, '-SHRA': 80,
            'SH': 81, 'SHRA': 81, '+SH': 81, '+SHRA': 81, '-SHRASN': 83,
            '-SHSNRA': 83, 'SHRASN': 84, '+SHRASN': 84, 'SHSNRA': 84,
            '+SHSNRA': 84, '-SHSN': 85, 'SHSN': 86, '+SHSN': 86, '-GS': 87,
            '-SHGS': 87, 'GS': 88, 'SHGS': 88, '+GS': 88, '+SHGS': 88,
            '-GR': 89, '-SHGR': 89, 'GR': 90, 'SHGR': 90, '+GR': 90,
            '+SHGR': 90, '-TSRA': 95, 'TSRA': 95, 'TSSN': 95, 'TSPL': 95,
            'TSGS': 96, 'TSGR': 96, '+TSRA': 97, '+TSSN': 97, '+TSPL': 97,
            'TSSA': 98, 'TSDS': 98, '+TSGS': 99, '+TSGR': 99}

def load_station_data(date,site):
    '''Given a site station ID, returns 1-day DataFrame of specified weather variables. 
    
    Parameters:
    site (str): string of ASOS station ID
    date (str): YYYYMMDD string for last of 3 days to plot
    
    Returns: 
    df (dataframe): dataframe containing 24 hours (1 days) of ASOS station data 
    
    '''
    lower_site = site.lower()
    now = datetime.strptime(date,'%Y%m%d')
    
    # define date to plot
    today_date = now.strftime('%Y%m%d')
    
    # define date in YYYY-mm-dd format (for selecting ranges of data from dataframes)
    today_date_dt_format = now.strftime('%Y-%m-%d')

    # define time limits
    today_start = now.strftime('%Y-%m-%d')+' 06:00:00'
    #tomorrow_midnight = (now+timedelta(hours=24)).strftime('%Y-%m-%d')+' 00:00:00'
    today_end = now.strftime('%Y-%m-%d')+' 18:00:00'
    
    # define data path and filename
    path0_dir = csv_dir+'/'+today_date
    path0_file = path0_dir+'/IMPACTS_ASOS_'+today_date+'_'+lower_site+'.csv'
    
    if os.path.exists(path0_file):
        today_all = pd.read_csv(path0_file)
        today_all['time'] = pd.to_datetime(today_all['time'])
        today_all = today_all.set_index('time')
        temp_12hrs = today_all.loc[today_all.index >= today_start]
        today_12hrs = temp_12hrs.loc[temp_12hrs.index <= today_end]

        # concatenate DataFrame objects
        frames = [today_12hrs]
        df = pd.concat(frames)

    else:
        
        print('some data is missing -- go to next plot')
        df = pd.DataFrame()
    
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
    #if isinstance(df, int): #Returns if the station is not reporting
    #    return

    if df.empty:
        print('dataframe is empty -- go to next plot')
        return
    
    lower_site = site.lower()
    timestamp_end=str(df.index[-1].strftime('%Y%m%d%H%M'))
    dt = df.index[:]
    graphtimestamp_start=dt[0].strftime("%m/%d/%y") 
    graphtimestamp=dt[-1].strftime("%m/%d/%y")      
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

    #------------------
    #plot airT and dewT
    #------------------
    if 'tmpc' in df.keys():
        airT = df['tmpc']
        airT_new = airT.dropna()
        airT_list = list(airT_new.values)
        airT_dt_list = []
        for i in range(0,len(airT)):
            if pd.isnull(airT[i]) == False:
                airT_dt_list.append(dt[i])
        #ax1.plot_date(airT_dt_list,airT_list,'o-',label="Temp",color="blue",linewidth=linewidth,markersize=markersize)  
        ax1.plot_date(airT_dt_list,airT_list,linestyle='solid',label="Temp",color="blue",linewidth=linewidth,marker='None')  
        #ax1.plot_date(dt,airT,'-',label="Temp",color="blue",linewidth=linewidth)  
    if 'dwpc' in df.keys():
        dewT = df['dwpc']
        dewT_new = dewT.dropna()
        dewT_list = list(dewT_new.values)
        dewT_dt_list = []
        for i in range(0,len(dewT)):
            if pd.isnull(dewT[i]) == False:
                dewT_dt_list.append(dt[i])
        #ax1.plot_date(dewT_dt_list,dewT_list,'o-',label="Dew Point",color="black",linewidth=linewidth,markersize=markersize)
        ax1.plot_date(dewT_dt_list,dewT_list,linestyle='solid',label="Dew Point",color="black",linewidth=linewidth,marker='None')
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
    if 'sknt' in df.keys():
        wnd_spd = df['sknt']
        #ax2.plot_date(dt,wnd_spd,'o-',label='Speed',color="forestgreen",linewidth=linewidth,markersize=markersize)
        ax2.plot_date(dt,wnd_spd,linestyle='solid',label='Speed',color="forestgreen",linewidth=linewidth,marker='None')
    if 'gust' in df.keys():
        wnd_gst = df['gust']
        max_wnd_gst = wnd_gst.max(skipna=True)
        ax2.plot_date(dt,wnd_gst,'o-',label='Gust (Max ' + str(round(max_wnd_gst,1)) + 'kt)',color="red",linewidth=0.0,markersize=markersize) 
    ax2.set_ylabel('Wind (kt)')
    ax2.legend(loc='best',ncol=2)
    axes.append(ax2)
    
    #-----------------------
    #plotting wind direction
    #-----------------------
    if 'drct' in df.keys():
        wnd_dir = df['drct']
        wnd_dir_new = wnd_dir.dropna()
        wnd_dir_list = list(wnd_dir_new.values)
        wnd_dir_dt_list = []
        for i in range(0,len(wnd_dir)):
            if pd.isnull(wnd_dir[i]) == False:
                wnd_dir_dt_list.append(dt[i])
        #ax3.plot_date(dt,wnd_dir,'o-',label='Direction',color="purple",linewidth=0.2, markersize=markersize)
        #ax3.plot_date(wnd_dir_dt_list,wnd_dir_list,'o-',label='Direction',color="purple",linewidth=0.2, markersize=markersize)
        ax3.plot_date(wnd_dir_dt_list,wnd_dir_list,linestyle='solid',label='Direction',color="purple",linewidth=linewidth, marker='None')
    ax3.set_ylim(-10,370)
    ax3.set_ylabel('Wind Direction')
    ax3.set_yticks([0,90,180,270,360])
    axes.append(ax3)
    
    #-------------
    #plotting MSLP
    #-------------
    if 'mslp' in df.keys():
        mslp = df['mslp']
        mslp_new = mslp.dropna()
        mslp_list = list(mslp_new.values)
        mslp_dt_list = []
        for i in range(0,len(mslp)):
            if pd.isnull(mslp[i]) == False:
                mslp_dt_list.append(dt[i])
        max_mslp = mslp.max(skipna=True)
        min_mslp = mslp.min(skipna=True)
        labelname = 'Min ' + str(round(min_mslp,1)) + 'hPa, Max ' + str(round(max_mslp,2)) + 'hPa'
        #ax4.plot_date(mslp_dt_list,mslp_list,'o-',label=labelname,color='darkorange',linewidth=linewidth,markersize=markersize)
        ax4.plot_date(mslp_dt_list,mslp_list,linestyle='solid',label=labelname,color='darkorange',linewidth=linewidth,marker='None')
    ax4.legend(loc='best')
    ax4.set_ylabel('MSLP (hPa)')
    ax4.set_xlabel('Time (UTC)')
    axes.append(ax4)
    
    #-------------------------------------------
    #plotting precip accumulation & precip types
    #-------------------------------------------        

    # Move date_time from index to column
    df = df.reset_index()

    if 'p01m' in df.keys():
        df['p01m'] = df['p01m'].fillna(0)
        last_val = df.iloc[0]['p01m']
        last_time = df.iloc[0]['time']
        last_hour = last_time.strftime('%H')
        last_minute = last_time.strftime('%M')
        precip_inc = [last_val]
        precip_accum = 0.0
        precip_accum_list = [last_val]
        num_ge_55_for_curr_hour = 0
        
        for index in range(1,len(df)):
        #for index in range(1,12):
            val = df.iloc[index]['p01m']
            time = df.iloc[index]['time']
            hour = time.strftime('%H')
            minute = time.strftime('%M')
            #print('LAST: val=',last_val,' hour=',last_hour,' minute=',last_minute)
            #print('CURR: val=',val,' hour=',hour,' minute=',minute)
            if hour != last_hour:
                num_ge_55_for_curr_hour = 0
            
            #if val == last_val:
            #    increment = 0.0
            #else:
            #    #if last_minute == '53':
            #    if last_minute > '50' and last_minute < '55':
            #        increment = val
            #    else:
            #        increment = val-last_val

            if minute >= '55':
                if num_ge_55_for_curr_hour == 0:
                    increment = val
                else:
                    if val > last_val:
                        increment = val - last_val
                    else:
                        increment = 0
                num_ge_55_for_curr_hour = num_ge_55_for_curr_hour + 1
            else:
                if val == last_val:
                    increment = 0
                else:
                    if val > last_val:
                        increment = val - last_val
                    else:
                        increment = 0
                        
            precip_accum = precip_accum + increment
            precip_accum_list.append(precip_accum)
            precip_inc.append(increment)
            last_val = val
            last_hour = hour
            last_minute = minute
        #df['p01m_mod'] = precip_inc
        max_precip = sum(precip_inc)
        # max_precip is also precip_accum_list[-1]
        #p01m_mod = list(df['p01m_mod'].values)
        p01m_mod_dt = list(df['time'].values)
        
        #max_precip = max(precip_accum_list)
        labelname = 'Precip (' + str(round(max_precip,2)) + 'mm)'
        #ax5.plot_date(p01m_mod_dt,precip_accum_list,'o-',label=labelname,color='navy',linewidth=linewidth,markersize=markersize)
        ax5.plot_date(p01m_mod_dt,precip_accum_list,linestyle='solid',label=labelname,color='navy',linewidth=linewidth,marker='None')
        if max_precip > 0:
            ax5.set_ylim(-0.1*max_precip,max_precip+max_precip*0.2)
        else:
            ax5.set_ylim(-0.1,0.5)
            
    # Add weather_code info to plot
    if 'wxcodes' in df.keys():
        df['wxcodes'] = df['wxcodes'].fillna('')
        wxcodes_wto = []
        for index in range(0,len(df)):
            time = df.iloc[index]['time']
            minute = time.strftime('%M')
            #if minute == '53':
            if minute > '50' and minute < '55':
                # convert alphanumeric code to wto code number
                wxcodes = df.iloc[index]['wxcodes']
                
                # Added in a check in case of unexpected weather codes
                # Used to resolve case when code set to -FZRAGR instead of -FZRA GR
                # Unidata says this will work as well:
                #   wxcode_num = wx_code_map.get(wxcodes.split()[0], 0)
                # Here is reference: https://docs.python.org/3/library/stdtypes.html#dict.get
                if len(wxcodes) > 0 and wxcodes.split()[0] in wx_codes.keys():
                    wxcode_num = wx_code_map[wxcodes.split()[0]]
                else:
                    wxcode_num = 0
                    
            else:
                wxcode_num = 0
            wxcodes_wto.append(wxcode_num)
        #df['wxcodes_wto'] = wxcode_wto
        #wxcodes_wto = list(df['wxcodes_wto'].values)
        wxcodes_wto_dt = list(df['time'].values)

        if max_precip > 0:
            dummy_y_vals = np.ones(len(wxcodes_wto)) * (0.10*max_precip)
        else:
            dummy_y_vals = np.ones(len(wxcodes_wto)) * (0.10*0.5)
            
        sp = StationPlot(ax5, wxcodes_wto_dt, dummy_y_vals)
        #ax.plot(dates, temps)
        sp.plot_symbol('C', wxcodes_wto, current_weather, fontsize=16, color='red')
        #sp.plot_symbol('C', wxcodes_wto, current_weather, fontsize=14, color='red')

    ax5.legend(loc='best')
    ax5.set_ylabel('Precip (mm)')
    axes.append(ax5)

    try:
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
            
            #ax.xaxis.set_minor_locator( HourLocator(np.linspace(6,18,3)) )
            ax.xaxis.set_minor_locator( HourLocator(np.linspace(6,18,5)) )
            ax.xaxis.set_minor_formatter( DateFormatter('%H') )
            ax.fmt_xdata = DateFormatter('Y%m%d%H%M%S')
            ax.yaxis.grid(linestyle = '--')
            ax.get_yaxis().set_label_coords(-0.06,0.5)

        # Write plot to file
        plot_path = plot_dir+'/'+today_date+'_AS502'
        if not os.path.exists(plot_path):
            os.makedirs(plot_path)
        catalogName = 'surface.Meteogram.'+timestamp_end+'.ASOS_'+sitelist[site].replace(' ','_')+'.png'
        #plt.savefig(plot_path+'/ops.asos.'+timestamp_end+'.'+lower_site+'.png',bbox_inches='tight')
        plt.savefig(plot_path+'/'+catalogName,bbox_inches='tight')
        plt.close()

    except:
        print('Problem creating plot . . . continute to next site')


#-----------------------------### MAIN CODE ###-----------------------------
        
for date in datelist:
    print(f'date = {date}')
    for site in sitelist.keys():
        sitetitle = sitelist[site]
        print(f'site = {site} and sitetitle = {sitetitle}')
        df = load_station_data(date,site)
        plot_station_data(date,site,sitetitle,df)
        