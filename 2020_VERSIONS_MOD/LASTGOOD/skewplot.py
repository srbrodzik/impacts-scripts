#!/usr/bin/python

# Brody Fuchs, CSU, November 2015
# brfuchs@atmos.colostate.edu

#EDITED: Clayton Sasaki, UW, MAY 2019
# crs326@uw.edu
#EDITED: Stacy Brodzik, UW, JAN 2022

## Update the skewT code to be smarter using classes and what not
# use the KUILsounding.txt as an example or KBMXsounding.txt

# Start out by just plotting the raw data first

import numpy as np
import matplotlib.pyplot as plt
plt.switch_backend('agg')
from skewPy import SkewT
import os
import datetime
import glob
import argparse
import xarray as xr
import linecache


### FORMAT FOR NEW UIUC NC FILES
uiuc_fmt = 'UIUCnc' 

stn_info = {'87344': {'longname': 'Cordoba Aerodrome', 'shortname': 'Cordoba_AR', 'lat': -31.297, 'lon': -64.212},
            '87418': {'longname': 'Mendoza Aerodrome', 'shortname': 'Mendoza_AR', 'lat': -32.844, 'lon': -68.796},
            '87244': {'longname': 'Villa Maria del Rio Seco', 'shortname': 'Villa_Maria_AR', 'lat': -29.906, 'lon': -63.726},
            '87155': {'longname': 'Resistencia Aerodrome', 'shortname': 'Resistencia_AR', 'lat': -27.446, 'lon': -59.051},
}


variable_snd_info = {'M1': {'longname': 'AMF site', 'shortname': 'M1', 'lat': -32.126, 'lon': -64.728},
                     'S1': {'longname': 'Villa Dolores', 'shortname': 'S1', 'lat': -31.951, 'lon': -65.149}
}

# Cordoba: -31.296639, -64.211855
# Mendoza: -32.843745, -68.796345
# Rio Seco: -29.90637, -63.72592

file_out_dt_fmt = '%Y%m%d%H%M'
title_dt_fmt = '%Y%m%d %H%MZ'

file_in_dt_fmt_lst = '%y%m%d_%H'
file_in_dt_fmt_DOE = '%Y%m%d.%H%M'
file_in_dt_fmt_SCOUT = '%Y%m%d%H%M'
file_in_dt_fmt_UIUC = '%Y%m%d%H%M'
file_in_dt_fmt_CSU = '%Y%m%d_%H%M'
file_in_dt_fmt_UWYO = '%Y%m%d%H%M'
file_in_dt_fmt_UIUCnc = '%Y-%m-%d-%H%M'

parser = argparse.ArgumentParser(description='Put in a file to be processed')

#parser.add_argument('--noarg', action="store_true", default=False)
parser.add_argument('--file', action="store", dest="file", default=None)

# location of sounding files
parser.add_argument('--filepath', action='store', dest='filepath', default='.')
# where you want to output skewTs
parser.add_argument('--outpath', action='store', dest='outpath', default='.')
# the first part of the sounding raw data file, need it to search for possible files
                    # other possibilities are 'K' for K*** UWYO soundings, could also be 'EDT' for Vaisala soundings
parser.add_argument('--prefix', action="store", dest="prefix", default='')
# This can currently be 'EC' for Canadian format, 'UWYO' for Wyoming soundings or 'EDT' for Vaisala CSU soundings
#(All options the suffixes of the file_in_dt_fmt_...)
# Or XML, so some dumb*** reason. Gave us something to do on the SPURS2 cruise, I suppose
parser.add_argument('--format', action='store', dest='format', default='XML')
# put this in if want to override the station name in the title of the skewT, default is fmt above
                                    # otherwise just put None
parser.add_argument('--station', action='store', dest='station', default=None)
# turning this switch on will just print more stuff, maybe needed if trying to debug
parser.add_argument('--debug', action='store', dest='debug', type=int, default=0)
# This will process a certain file in the filepath. The number will correspond to the index of the file
parser.add_argument('--number', action='store', dest='number', default=None)
# This will process the last file in the filepath
parser.add_argument('--last', action='store', dest='last', default=None)
# Option for whether the lifted parcel is displayed
parser.add_argument('--parcel', action='store', dest='parcel', default=True)
# Option for whether the hodograph is displayed
parser.add_argument('--hodograph', action='store', dest='hodograph', default=True)

pargs = parser.parse_args()

#Will change the input of hodograph and parcel from a string to a boolean
try:
    if pargs.parcel.lower() == 'false':
        pargs.parcel = False
    else:
        print("Improper parcel flag. Use \"False\" to turn off the parcel plot." )
        pargs.parcel = True
#Except will be triggered if parcel is a boolean and has no lower() method
except:
    pass
try:
    if pargs.hodograph.lower() == 'false':
        pargs.hodograph = False
    else:
        print("Improper hodograph flag. Use \"False\" to turn off the hodograph plot." )
        pargs.hodograph = True
except:
    pass
##### PARAMETERS YOU CAN CHANGE HERE #########

# file_path = 'Data/soundings/'            self.plot_skewt(parcel=True, parcel_draw=True)

# out_path = 'Images/soundings/'
# prefix = 'Revelle' # the first part of the sounding raw data file, need it to search for possible files
#                     # other possibilities are 'K' for K*** UWYO soundings, could also be 'EDT' for Vaisala soundings
# fmt = 'XML'
# station_name = None # put this in if want to override the station name in the title of the skewT, default is fmt above
#                                     # otherwise just put None

########### DON'T NEED TO WORRY ABOUT ANYTHING BELOW HERE ############

if pargs.file is not None:
    sounding_files = [pargs.file]

elif pargs.filepath is not None:
    sounding_files = sorted(glob.glob('%s/%s*%s'%(pargs.filepath, pargs.prefix, pargs.format)))

else:
    sounding_files = sorted(glob.glob('%s/*'%(pargs.filepath)))

#print 'processing the following files: {}'.format(sounding_files)

for fname in sounding_files:
    #file_title = os.path.basename(fname)[4:-4]

    fbase = os.path.basename(fname)
    #print(fbase)
    print('Processing %s'%os.path.basename(fbase))
    # this next part is going to be RELAMPAGO specific
    # the files look like they're coming in the format of YYMMDD_HH_STN.lst
    # so need to parse that

    ##file_title = os.path.basename(fname)[:-4]
    
    # reads in files and plots sounding
    S = SkewT.Sounding(fname, fmt=pargs.format, station_name=pargs.station, flip_barb=True)

    # gets lat and lon (optional attributes) for sounders that are mobile assets and imformation was read in SkewT.py readfile function
    if pargs.format == 'CSU' or pargs.format == 'SCOUT' or pargs.format == 'UIUC':

        lat = S.data['lat'][0]
        lon = S.data['lon'][0]

    # adds infromation on the specifc sounding plotted for various types of sounders
    
    if pargs.format == 'lst':
        file_time_string = fbase[:9]

        file_time = datetime.datetime.strptime(file_time_string, file_in_dt_fmt_lst)

        stn_id = fbase[10:15]
        si = stn_info[stn_id]
        #print 'Station: {}'.format(si['shortname'])

        out_fname = 'upperair.SkewT.{date}.{site}.png'.format(date=file_time.strftime(file_out_dt_fmt), site=si['shortname'])

        figtitle = '{stn} {ln} {t} sounding ({lat:.3f}, {lon:.3f})'.format(stn=stn_id, ln=si['longname'], t=file_time.strftime(title_dt_fmt),
                                                    lat=si['lat'], lon=si['lon'])
    ##Added by Sean O'Neil (Nov 2019)
    elif pargs.format == 'UIUCnc':
        ds = xr.open_dataset(fname)
        attrs = ds.attrs
        
        #stn_id = attrs['institution'].replace(" ","_")
        stn_id = 'UILL_Mobile'
        file_time = datetime.datetime.strptime(attrs['start_datetime'],'%Y-%m-%dT%H:%M:%SZ')
        #Location is outputted in a string of lat and long including words
        location_str = attrs['location']
        location_list = location_str.split()
        
        lat = float(location_list[0])
        lon = float(location_list[3])
        #Sets the values to negative if in the Western or Southern Hemispere
        if location_list[-1] == 'west':
            lon *= -1
        if location_list[2] == 'south':
            lat *= -1
        #out_fname = 'upperair.SkewT.{dt}.{stn}.png'.format(dt = file_time.strftime(file_out_dt_fmt), stn = stn_id)
        out_fname = 'upperair.UILL_sonde.{dt}.skewT.png'.format(dt = file_time.strftime(file_out_dt_fmt))
        figtitle = '{stn} {dt} sounding ({lati:.3f}, {long:.3f})'.format(stn = stn_id, dt = file_time.strftime(title_dt_fmt), lati=lat, long=lon)

    elif pargs.format == 'SBUnc':
        ds = xr.open_dataset(fname)
        attrs = ds.attrs
        
        #stn_id = attrs['InputFile'][:3]
        stn_id = 'SBU_Mobile'
        file_time = datetime.datetime.strptime(attrs['ReleaseTime'],'%Y/%m/%d %H:%M:%S')

        #Location is outputted in two strings of lat and long including words
        lat_str_raw = attrs['SiteLocation_Latitude']
        lon_str_raw = attrs['SiteLocation_Longitude']
        (lat_str,lat_dir) = lat_str_raw.split()
        (lon_str,lon_dir) = lon_str_raw.split()
        lat = float(lat_str)
        lon = float(lon_str)
        
        out_fname = 'upperair.SBU_sonde.{dt}.skewT.png'.format(dt = file_time.strftime(file_out_dt_fmt))
        figtitle = '{stn} {dt} sounding ({lati:.3f}, {long:.3f})'.format(stn = stn_id, dt = file_time.strftime(title_dt_fmt), lati=lat, long=lon)

    elif pargs.format == 'SBUnc_static':
        ds = xr.open_dataset(fname)
        attrs = ds.attrs
        
        #stn_id = attrs['InputFile'][:3]
        stn_id = 'SBU'
        file_time = datetime.datetime.strptime(attrs['ReleaseTime'],'%Y/%m/%d %H:%M:%S')

        #Location is outputted in two strings of lat and long including words
        lat_str_raw = attrs['SiteLocation_Latitude']
        lon_str_raw = attrs['SiteLocation_Longitude']
        (lat_str,lat_dir) = lat_str_raw.split()
        (lon_str,lon_dir) = lon_str_raw.split()
        lat = float(lat_str)
        lon = float(lon_str)
        
        out_fname = 'upperair.SBU_sonde.{dt}.Stonybrook_NY_skewT.png'.format(dt = file_time.strftime(file_out_dt_fmt))
        print(out_fname)
        #out_fname = 'upperair.SkewT.{dt}.{stn}.png'.format(dt = file_time.strftime(file_out_dt_fmt), stn = stn_id)
        figtitle = '{stn} {dt} sounding ({lati:.3f}, {long:.3f})'.format(stn = stn_id, dt = file_time.strftime(title_dt_fmt), lati=lat, long=lon)
        print(figtitle)

    elif pargs.format == 'MUnc':
        ds = xr.open_dataset(fname)
        attrs = ds.attrs
        
        #stn_id = attrs['InputFile'][:3]
        #stn_id = 'MillersvilleU'
        stn_id = 'UMILL'
        file_time = datetime.datetime.strptime(attrs['ReleaseTime'],'%Y/%m/%d %H:%M:%S')

        #Location is outputted in two strings of lat and long including words
        lat_str_raw = attrs['SiteLocation_Latitude']
        lon_str_raw = attrs['SiteLocation_Longitude']
        (lat_str,lat_dir) = lat_str_raw.split()
        (lon_str,lon_dir) = lon_str_raw.split()
        lat = float(lat_str)
        lon = float(lon_str)
        
        out_fname = 'upperair.UMILL_sonde.{dt}.skewT.png'.format(dt = file_time.strftime(file_out_dt_fmt))
        figtitle = '{stn} {dt} sounding ({lati:.3f}, {long:.3f})'.format(stn = stn_id, dt = file_time.strftime(title_dt_fmt), lati=lat, long=lon)

    elif pargs.format == 'MUtxt_ws':

        # Get lat and lon of launch site
        saveLine = ''
        with open(fname, 'r') as fp:
            lines = fp.readlines()
            for line in lines:
                if 'lat' in line:
                    saveLine = line

        if len(saveLine) > 0:
            latLonStr = saveLine.strip()
            (site,latStr,lonStr) = latLonStr.split(' ')
            lat = float(latStr.replace('lat=',''))
            lon = float(lonStr.replace('lon=',''))
        else:
            #print('done')
            print('{}'.format('lat and lon not found in header, set them to zero'))
            lat = 0.0
            lon = 0.0

        # Assumes parts of input file name separated by periods & filename = upperair.UNCA_windsonde1.<datetime>.txt
        parts = fbase.split('.')
        snd_id = parts[1]
        file_time_string = parts[2]
        
        file_time = datetime.datetime.strptime(file_time_string, file_in_dt_fmt_UWYO)
        out_fname = 'upperair.{snd}.{dt}.skewT.png'.format(snd=snd_id, dt=file_time.strftime(file_out_dt_fmt))
        figtitle = '{snd} {dt} sounding ({lati:.3f}, {long:.3f})'.format(snd=snd_id, dt=file_time.strftime(title_dt_fmt), lati=lat, long=lon)
        #figtitle = '{snd} {dt} sounding'.format(snd=snd_id, dt=file_time.strftime(title_dt_fmt))

    elif pargs.format == 'VALtxt':

        # Read date, time, lat and lon from header
        latFound = False
        lonFound = False
        with open(fname, 'r') as fp:
            while not latFound or not lonFound:
                line = fp.readline().strip()
                #print(line)
                if 'lat' in line:
                    #print('found lat')
                    lat = float(line.replace('lat: ',''))
                    latFound = True
                elif 'lon' in line:
                    #print('found lon')
                    lon = float(line.replace('lon: ',''))
                    lonFound = True

        # Assumes parts of input file name separated by periods & filename = upperair.VALPO_sonde.<datetime>.csv
        parts = fbase.split('.')
        snd_id = parts[1]
        file_time_string = parts[2]
        
        file_time = datetime.datetime.strptime(file_time_string, file_in_dt_fmt_UWYO)
        out_fname = 'upperair.{snd}.{dt}.skewT.png'.format(snd=snd_id, dt=file_time.strftime(file_out_dt_fmt))
        figtitle = '{snd} {dt} sounding ({lati:.3f}, {long:.3f})'.format(snd=snd_id, dt=file_time.strftime(title_dt_fmt), lati=lat, long=lon)
        #figtitle = '{snd} {dt} sounding'.format(snd=snd_id, dt=file_time.strftime(title_dt_fmt))

    elif pargs.format == 'raw':

        dash_ind = fbase.index('-')

        snd_id = fbase[dash_ind+4:dash_ind+6]

        si = variable_snd_info[snd_id]

        file_snd_id = fbase[:14]
        file_time_string = fbase[15:28]
        file_time = datetime.datetime.strptime(file_time_string, file_in_dt_fmt_DOE)
        out_fname = 'upperair.DOE_{sn}_sonde.{dt}.skewT.png'.format(fsi=file_snd_id, sn=si['shortname'], dt=file_time.strftime(file_out_dt_fmt))
        figtitle = '{sn} {ln} {dt} sounding ({lat:.3f}, {lon:.3f})'.format(sn=si['shortname'], ln=si['longname'], dt=file_time.strftime(title_dt_fmt), lat=si['lat'], lon=si['lon'])

    elif pargs.format == 'cdf':

        dash_ind = fbase.index('b1')

        snd_id = fbase[dash_ind-3:dash_ind-1]

        si = variable_snd_info[snd_id]

        file_snd_id = fbase[:14]
    
        file_time_string = fbase[18:31]
        
        file_time = datetime.datetime.strptime(file_time_string, file_in_dt_fmt_DOE)
        out_fname = 'upperair.DOE_{sn}_sonde.{dt}.skewT.png'.format(fsi=file_snd_id, sn=si['shortname'], dt=file_time.strftime(file_out_dt_fmt))
        figtitle = '{sn} {ln} {dt} sounding ({lat:.3f}, {lon:.3f})'.format(sn=si['shortname'], ln=si['longname'], dt=file_time.strftime(title_dt_fmt), lat=si['lat'], lon=si['lon'])

    elif pargs.format == 'CSU':


        file_time_string = fbase[4:17]
        file_time = datetime.datetime.strptime(file_time_string, file_in_dt_fmt_CSU)
        out_fname = 'upperair.CSU_sonde.{dt}.skewT.png'.format(dt=file_time.strftime(file_out_dt_fmt))
        figtitle = 'CSU {dt} sounding ({lat:.3f} {lon:.3f})'.format(dt=file_time.strftime(title_dt_fmt), lat=lat, lon=lon)

    elif pargs.format == 'SCOUT':

        dash_ind = fbase.index('-')

        snd_id = fbase[dash_ind+1:dash_ind+7]

        file_snd_id = fbase[:14]
        file_time_string = fbase[:12]
        file_time = datetime.datetime.strptime(file_time_string, file_in_dt_fmt_SCOUT)
        out_fname = 'upperair.SCOUT_{snd}_sonde.{dt}.skewT.png'.format(snd=snd_id, dt=file_time.strftime(file_out_dt_fmt))
        figtitle = '{snd} {dt} sounding ({lat:.3f} {lon:.3f})'.format(snd=snd_id, dt=file_time.strftime(title_dt_fmt), lat=lat, lon=lon)

    elif pargs.format == 'UIUC':

        dash_ind = fbase.index('-')

        snd_id = fbase[dash_ind+1:dash_ind+6]

        file_snd_id = fbase[:14]
        file_time_string = fbase[:12]
        file_time = datetime.datetime.strptime(file_time_string, file_in_dt_fmt_UIUC)
        out_fname = 'upperair.UIUC_{snd}_sonde.{dt}.skewT.png'.format(snd=snd_id, dt=file_time.strftime(file_out_dt_fmt))
        figtitle = '{snd} {dt} sounding ({lat:.3f} {lon:.3f})'.format(snd=snd_id, dt=file_time.strftime(title_dt_fmt), lat=lat, lon=lon)

    elif pargs.format == 'UWYO':

        # Assumes parts of input file name separated by periods
        parts = fbase.split('.')
        snd_id = parts[3]
        file_time_string = parts[2]
        # used for IMPACTS 2020 - input file naming convention: ops.skewt.<datetime>.<site>.png
        #snd_id = fbase[31:34]
        
        #start_time_ind = fbase.index('.2019')
        #start_time_ind = fbase.index('.2020')
        #file_time_string = fbase[start_time_ind+1:start_time_ind+13]

        #print file_time_string

        file_time = datetime.datetime.strptime(file_time_string, file_in_dt_fmt_UWYO)
        #out_fname = 'upperair.NWS_{snd}_sonde.{dt}.skewT.png'.format(snd=snd_id, dt=file_time.strftime(file_out_dt_fmt))
        out_fname = 'upperair.SkewT.{dt}.{snd}.png'.format(dt=file_time.strftime(file_out_dt_fmt),snd=snd_id)
        figtitle = '{snd} {dt} sounding'.format(snd=snd_id, dt=file_time.strftime(title_dt_fmt))

    # USED IN 2020??
    #elif pargs.format == 'UWYO':
    #
    #    snd_id = fbase[31:34]
    #    
    #    #start_time_ind = fbase.index('.2019')
    #    #start_time_ind = fbase.index('.2020')
    #
    #    file_time_string = fbase[start_time_ind+1:start_time_ind+13]
    #    #print file_time_string
    #
    #    file_time = datetime.datetime.strptime(file_time_string, file_in_dt_fmt_UWYO)
    #    out_fname = 'upperair.NWS_{snd}_sonde.{dt}.skewT.png'.format(snd=snd_id, dt=file_time.strftime(file_out_dt_fmt))
    #    figtitle = '{snd} {dt} sounding'.format(snd=snd_id, dt=file_time.strftime(title_dt_fmt))

    #print 'fname: ', fname
    # plots actual skewT. Done here because figure title nessary
    S.plot_skewt(parcel=pargs.parcel, parcel_draw=pargs.parcel, title=figtitle, hodograph = pargs.hodograph)
    # calculates cape
    # commented next line out for testing windsondes from Millersville
    #CAPE = S.cape()
    #print 'PRINT', CAPE

    # The filenames are made this way to follow the project catalog convention
    plt.savefig('%s/%s'%(pargs.outpath, out_fname), dpi=120)
    plt.close('all')
