#!/usr/bin/python3

# ICONS: http://catalog.eol.ucar.edu/kmlicons/ ... scout_blank.png, green_dot.png, blue_dot.png, yellow_dot.png, cyan_dot.png, orange_dot.png

import os
import sys
import glob
from datetime import datetime
from datetime import timedelta
import pandas as pd

inDirBase = '/home/disk/bob/impacts/raw/aircraft'
# Use outDirBase for now but eventually ftp the result to NCAR catalog site
outDirBase = '/home/disk/funnel/impacts-website/archive_ncar/gis/aircraft/ALL'
missingValue = -999
kmlPrefix = 'gis.'
planes = {'N809NA':'NASA_ER2'}
#planes = {'N426NA':'NASA_P3'}
flightDates = ['20200227','20200228']
missingValue = -999
varDict = {'time':{'units':'seconds','long_name':'seconds since 1970-01-01'},
           'lat':{'units':'degN','long_name':'latitude'},
           'lon':{'units':'degE','long_name':'longitude'},
           'gps_msl_alt':{'units':'m','long_name':'GPS altitude, mean sea level'},
           'wgs84_alt':{'units':'m','long_name':'WGS 84 geoid altitude'},
           'pres_alt':{'units':'ft','long_name':'pressure altitude'},
           'radar_alt':{'units':'ft','long_name':'radar altimeter altitude'},
           'grnd_spd':{'units':'m/s','long_name':'ground speed'},
           'true_airspd':{'units':'m/s','long_name':'true airspeed'},
           'ind_airspd':{'units':'knots','long_name':'indicated airspeed'},
           'mach':{'units':'none','long_name':'aircraft mach number'},
           'vert_vel':{'units':'m/s','long_name':'aircraft vertical velocity'},
           'true_hdg':{'units':'deg','long_name':'true heading'},
           'track':{'units':'deg','long_name':'track angle'},
           'drift':{'units':'deg','long_name':'drift angle'},
           'pitch':{'units':'deg','long_name':'pitch angle'},
           'roll':{'units':'deg','long_name':'roll angle'},
           'side_slip':{'units':'deg','long_name':'side slip angle'},
           'ang_of_attack':{'units':'deg','long_name':'angle of attack'},
           'amb_temp':{'units':'degC','long_name':'ambient temperature'},
           'dewpt':{'units':'degC','long_name':'dew point'},
           'tot_temp':{'units':'degC','long_name':'total temperature'},
           'stat_pres':{'units':'mb','long_name':'static pressure'},
           'dyn_pres':{'units':'mb','long_name':'dynamic pressure (total minus static)'},
           'cabin_pres':{'units':'mb','long_name':'cabin pressure'},
           'wspd':{'units':'m/s','long_name':'wind speed'},
           'wdir':{'units':'deg','long_name':'wind direction'},
           'vert_wspd':{'units':'m/s','long_name':'vertical wind speed'},
           'solar_zen':{'units':'deg','long_name':'solar zenith angle'},
           'sun_el_ac':{'units':'deg','long_name':'sun elevation from aircraft'},
           'sun_az_grnd':{'units':'deg','long_name':'sun azimuth from ground'},
           'sun_az_ac':{'units':'deg','long_name':'sun azimuth from aircraft'} }

now = datetime.utcnow()
now_str = now.strftime("%Y%m%d%H%M")

for plane in planes.keys():
    print(plane)
    if os.path.isdir(inDirBase+'/'+plane+'/'+flightDates[0]):
        
        # Create concatenated file all all IWG records from this flight to date
        iwgFile = '/tmp/'+plane+'.'+now_str+'.csv'
        if os.path.isdir(inDirBase+'/'+plane+'/'+flightDates[0]) and os.path.isdir(inDirBase+'/'+plane+'/'+flightDates[1]):
            cmd = 'cat '+inDirBase+'/'+plane+'/'+flightDates[0]+'/*IWG1 '+inDirBase+'/'+plane+'/'+flightDates[1]+'/*IWG1 > '+iwgFile
            os.system(cmd)
        else:
            cmd = 'cat '+inDirBase+'/'+plane+'/'+flightDates[0]+'/*IWG1 > '+iwgFile
            os.system(cmd)

        # Read in csv data as Datafreme object
        df = pd.read_csv(iwgFile)
        
        # Create column headings
        df.columns = ['iwg','time','lat','lon','gps_msl_alt','wgs84_alt',
                      'pres_alt','radar_alt','grnd_spd','true_airspd',
                      'ind_airspd','mach','vert_vel','true_hdg','track',
                      'drift','pitch','roll','side_slip','ang_of_attack',
                      'amb_temp','dewpt','tot_temp','stat_pres','dyn_pres',
                      'cabin_pres','wspd','wdir','vert_wspd','solar_zen',
                      'sun_el_ac','sun_az_grnd','sun_az_ac']

        # Convert times from yyyy-mm-ddThh:mm:ss.ssssss' to datetime objects
        df['time'] = pd.to_datetime(df['time'])

        # Drop unnecessary columns (check to make sure I'm keeping the correct altitude)
        # NOTE: vert_wspd and dewpt seem to always be NaN's
        df = df.drop(columns=['iwg','wgs84_alt','pres_alt','radar_alt','grnd_spd','true_airspd',
                              'ind_airspd','mach','vert_vel','true_hdg','track','drift','pitch',
                              'roll','side_slip','ang_of_attack','amb_temp','dewpt','tot_temp',
                              'stat_pres','dyn_pres','cabin_pres','wspd','wdir','vert_wspd',
                              'solar_zen','sun_el_ac','sun_az_grnd','sun_az_ac'])
                    
        # Replace Nan'S with missingValue
        df = df.fillna(missingValue)

        # Filter out rows with missing lat, lon or alt
        df = df[df['lat'] != missingValue]

        # Create output dir for kml files
        outDir = outDirBase
        #if not os.path.isdir(outDir):
        #    os.makedirs(outDir)

        # Open output kml file for entire flight
        firstTime_dt = df.iloc[0].time
        firstTime_str = firstTime_dt.strftime("%Y%m%d%H%M")
        firstDate_str = firstTime_dt.strftime("%Y%m%d")
        firstHrMin_str = firstTime_dt.strftime("%H:%M:%S")
        kmlFile = kmlPrefix+planes[plane]+'.'+firstTime_str+'.flight_track.kml'
        fout = open(outDir+'/'+kmlFile,'w')

        # Write header info
        fout.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        fout.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
        fout.write('  <Document>\n')
        fout.write('    <name>'+planes[plane]+'</name>\n')
        fout.write('    <Style id="TRACK_BLUE">\n')
        fout.write('      <LineStyle>\n')
        fout.write('        <color>ffff7f00</color>\n')
        fout.write('        <width>2</width>\n')
        fout.write('      </LineStyle>\n')
        fout.write('      <PolyStyle>\n')
        fout.write('        <color>7f00ff00</color>\n')
        fout.write('      </PolyStyle>\n')
        fout.write('    </Style>\n')
        fout.write('    <Style id="TRACK_YELLOW">\n')
        fout.write('      <LineStyle>\n')
        fout.write('        <color>ff00ffff</color>\n')
        fout.write('        <width>2</width>\n')
        fout.write('      </LineStyle>\n')
        fout.write('      <PolyStyle>\n')
        fout.write('        <color>7f00ff00</color>\n')
        fout.write('      </PolyStyle>\n')
        fout.write('    </Style>\n')
        fout.write('    <Folder>\n')
        fout.write('      <name>track</name>\n')
        fout.write('      <open>1</open>\n')
        fout.write('      <Placemark>\n')
        fout.write('        <visibility>1</visibility>\n')
        fout.write('        <open>1</open>\n')
        fout.write('        <styleUrl>#TRACK_YELLOW</styleUrl>\n')
        fout.write('        <LineString>\n')
        fout.write('          <altitudeMode>absolute</altitudeMode>\n')
        fout.write('          <coordinates>\n')
        
        # Output lon/lat/alt triads to kml file
        for ind in range(0,len(df.index)):
            fout.write('            {a:0.4f},{b:0.4f},{c:0.1f}\n'.format(a=df.iloc[ind].lon,b=df.iloc[ind].lat,c=df.iloc[ind].gps_msl_alt))
            
        fout.write('          </coordinates>\n')
        fout.write('        </LineString>\n')
        fout.write('      </Placemark>\n')

        # Output hyperlink ends
        fout.write('    </Folder>\n')
        fout.write('  </Document>\n')
        fout.write('</kml>\n')

        # Remove iwgFile and close kml file
        os.remove(iwgFile)
        fout.close()
                    
