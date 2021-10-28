#!/usr/bin/python3

# Read IWG1 ascii data and plot time series of chosen field
# FORMAT: iwg1,date_time,lat,lon,gps_msl_alt,wgs84_alt,press_alt,radar_alt,grnd_spd,true_airspeed,indicated_airspeed,mach_number,vert_velocity,true_hdg,track,drift,pitch,roll,side_slip,angle_of_attack,ambient_temp,dew_point,total_temp,static_press,dynamic_press,cabin_pressure,wind_speed,wind_dir,vert_wind_spd,solar_zenith,sun_elev_ac,sun_az_grd,sun_az_ac

# For testing
inDir = '/home/disk/funnel/impacts-website/archive/missions/p3/20200201'
inFile = 'missions.p3.20200201.flight_track.txt'
#inDir = '/home/disk/funnel/impacts-website/archive/missions/p3/20200125'
#inFile = 'missions.p3.20200125.flight_track.txt'
#inDir = '/home/disk/funnel/impacts-website/archive/missions/p3/20200118'
#inFile = 'missions.p3.20200118.flight_track.txt'
#inDir = '/home/disk/funnel/impacts-website/archive/missions/p3/20200112'
#inFile = 'missions.p3.20200112.flight_track.txt'
paramIndex = 4
paramName = 'alt'
outDir = '/tmp'
outFile = '20200201_p3_'+paramName+'.png'

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import matplotlib.dates as mdates
from matplotlib.dates import DayLocator, HourLocator, MinuteLocator, DateFormatter
#matplotlib.use('Agg') 
import matplotlib.transforms as transforms
import matplotlib.pyplot as plt 

'''
if len(sys.argv) != 7:
    print >>sys.stderr, "Useage: ", sys.argv[0], " <inDir> <csvFile> <paramIndex> <paramName> <outDir> <outFile>"
    sys.exit()
else:
    inDir = sys.argv[1]
    inFile = sys.argv[2]
    paramIndex = sys.argv[3]
    paramName = sys.argv[4]
    outDir = sys.argv[5]
    outFile = sys.argv[6]
    print >>sys.stderr, "inDir      = ", inDir
    print >>sys.stderr, "inFile     = ", inFile
    print >>sys.stderr, "paramIndex = ", paramIndex
    print >>sys.stderr, "paramName  = ", paramName
    print >>sys.stderr, "outDir     = ", outDir
    print >>sys.stderr, "outFile    = ", outFile
'''

# Use this if first row contains field names
#df = pd.read_csv(inDir+'/'+inFile)

# Use this if first row contains data
df = pd.read_csv(inDir+'/'+inFile,
                 usecols=[1,paramIndex],
                 names=["date_string",paramName])

# Assign datatime index
df.index = pd.to_datetime(df["date_string"], format="%Y-%m-%dT%H:%M:%S.%f")
df = df.drop(columns=["date_string"])

# Get rid of data when plane is on or close to ground
df_new = df[df['alt']>20]
dt_new = df_new.index[:]
vals = df_new[paramName]

# Plot data - simple plot
#df_new.plot(figsize=(15,4),grid=True,y="alt",title="P3 Altitude - 20200201")
#plt.savefig('20200201_p3_alt.png')
#plt.show()

#timestamp_end=str(df.index[-1].strftime('%Y%m%d%H%M'))
graphtimestamp_start=dt_new[0].strftime("%m/%d/%y %H:%M") 
graphtimestamp_end=dt_new[-1].strftime("%m/%d/%y %H:%M")      
markersize = 1.5
linewidth = 1.0

# make figure and plot axes
fig, ax = plt.subplots()
fig.set_size_inches(15,4)
ax.set_title('P3 Altitude '+graphtimestamp_start+' - '+graphtimestamp_end)
ax.plot_date(dt_new,vals,'o-',label=paramName,color="blue",linewidth=linewidth,markersize=markersize)

ax.set_ylabel('Altitude (m)')
ax.legend(loc='best',ncol=1)

ax.xaxis.set_major_locator( MinuteLocator(np.linspace(0,60,5)) )
ax.xaxis.set_major_formatter( DateFormatter('%H:%M') )
#ax.xaxis.set_minor_locator( MinuteLocator(np.linspace(0,60,5)) )
#ax.xaxis.set_minor_formatter( DateFormatter('%M') )

ax.minorticks_on()
ax.grid(which='major',linestyle='-',color='red')
ax.grid(which='minor',linestyle=':',color='black')

plt.savefig(outDir+'/'+outFile,bbox_inches='tight')
plt.close()
