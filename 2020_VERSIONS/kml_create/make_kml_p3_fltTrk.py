#!/usr/bin/python3

import os
import sys
from datetime import datetime
import pandas as pd

inDirBase = '/home/disk/funnel/impacts-website/archive/missions'
outDirBase = '/home/disk/funnel/impacts-website/archive_ncar/gis/aircraft'
missingValue = -999
kml_prefix = 'gis.NASA_'
planes = ['er2','p3']
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

for plane in planes:
    for date in os.listdir(inDirBase+'/'+plane):
        if os.path.isdir(inDirBase+'/'+plane+'/'+date):
            inDir = inDirBase+'/'+plane+'/'+date
            for file in os.listdir(inDir):
                if 'flight_track_only.txt' in file:

                    print(file)

                    # Read in csv data as Datafreme object
                    df = pd.read_csv(inDir+'/'+file)
        
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
                                          'roll','side_slip','ang_of_attack','amb_temp','stat_pres','dyn_pres',
                                          'cabin_pres','vert_wspd','solar_zen','sun_el_ac','sun_az_grnd',
                                          'sun_az_ac'])
                    
                    # Replace Nan'S with missingValue
                    df = df.fillna(missingValue)

                    # Open output kml file
                    outDir = outDirBase+'/NASA_'+plane.upper()+'/'+date
                    if not os.path.isdir(outDir):
                        os.makedirs(outDir)
                    lastTime_dt = df.iloc[-1].time
                    lastTime_str = lastTime_dt.strftime("%Y%m%d%H%M")
                    lastHrMin_str = lastTime_dt.strftime("%H:%M:%S")
                    kmlFile = kml_prefix+plane.upper()+'.'+lastTime_str+'.flight_track.kml'
                    fout = open(outDir+'/'+kmlFile,'w')

                    # Write header info
                    fout.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                    fout.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
                    fout.write('  <Document>\n')
                    fout.write('    <name>NASA_'+plane.upper()+' '+date+' '+lastHrMin_str+'</name>\n')
                    fout.write('    <Style id="PM1">\n')
                    fout.write('      <IconStyle>\n')
                    fout.write('        <scale>0.5</scale>\n')
                    fout.write('        <Icon>\n')
                    fout.write('          <href>http://www.eol.ucar.edu/flight_data/display/red.png</href>\n')
                    fout.write('        </Icon>\n')
                    fout.write('      </IconStyle>\n')
                    fout.write('    </Style>\n')
                    fout.write('    <Style id="PM2">\n')
                    fout.write('      <IconStyle>\n')
                    fout.write('        <scale>0.5</scale>\n')
                    fout.write('        <Icon>\n')
                    fout.write('          <href>http://www.eol.ucar.edu/flight_data/display/white.png</href>\n')
                    fout.write('        </Icon>\n')
                    fout.write('      </IconStyle>\n')
                    fout.write('    </Style>\n')
                    fout.write('    <Style id="TRACK_RED">\n')
                    fout.write('      <LineStyle>\n')
                    fout.write('        <color>ff0000aa</color>\n')
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
                    fout.write('        <name>Track</name>\n')
                    fout.write('        <visibility>1</visibility>\n')
                    fout.write('        <open>1</open>\n')
                    fout.write('        <styleUrl>#TRACK_RED</styleUrl>\n')
                    fout.write('        <LineString>\n')
                    fout.write('          <extrude>1</extrude>\n')
                    fout.write('          <tessellate>1</tessellate>\n')
                    fout.write('          <altitudeMode>absolute</altitudeMode>\n')
                    fout.write('          <coordinates>\n')
                   
                    # Output lon/lat/alt triads to kml file
                    for ind in range(0,len(df.index)):
                        #fout.write(f'{df.iloc[ind].lon},{df.iloc[ind].lat},{df.iloc[ind].gps_msl_alt}\n')  # too many digits
                        fout.write('            {a:0.4f},{b:0.4f},{c:0.1f}\n'.format(a=df.iloc[ind].lon,b=df.iloc[ind].lat,c=df.iloc[ind].gps_msl_alt))

                    fout.write('          </coordinates>\n')
                    fout.write('        </LineString>\n')
                    fout.write('      </Placemark>\n')

                    # Output current position
                    fout.write('      <Placemark>\n')
                    fout.write('        <name>NASA_'+plane.upper()+'</name>\n')
                    fout.write('        <description><![CDATA[{a} {b}<br>Lat: {c:0.4f}<br>Lon: {d:0.4f}<br>Alt: {e:0.1f} m<br>]]></description>\n'.format(a=date,b=lastHrMin_str,c=df.iloc[-1].lat,d=df.iloc[-1].lon,e=df.iloc[-1].gps_msl_alt))
                    fout.write('        <TimeStamp>\n')
                    fout.write('          <when>{a}</when>\n'.format(a=date))
                    fout.write('        </TimeStamp>\n')
                    fout.write('        <styleUrl>#PM1</styleUrl>\n')
                    fout.write('        <Point>\n')
                    fout.write('          <altitudeMode>absolute</altitudeMode>\n')
                    fout.write('          <coordinates>{a:0.4f},{b:0.4f},{c:0.1f} m</coordinates>\n'.format(a=df.iloc[-1].lon,b=df.iloc[-1].lat,c=df.iloc[-1].gps_msl_alt))
                    fout.write('        </Point>\n')
                    fout.write('      </Placemark>\n')

                    # Output all previous positions if minutes are multiples of 5
                    lastMinUsed = -1
                    for ind in range(0,len(df.index)-1):
                        currTime_dt = df.iloc[ind].time
                        currMinutes = int(currTime_dt.strftime("%M"))
                        if currMinutes%5 == 0 and currMinutes != lastMinUsed:
                            lastMinUsed = currMinutes
                        
                            currTime_str = currTime_dt.strftime("%H:%M:%S")
                            fout.write('      <Placemark>\n')
                            fout.write('        <name>{a}</name>\n'.format(a=currTime_str))
                            fout.write('        <description><![CDATA[{a}<br>Lat: {b:0.4f}<br>Lon: {c:0.4f}<br>Alt: {d:0.1f} m<br>]]></description>\n'.format(a=currTime_str,b=df.iloc[ind].lat,c=df.iloc[ind].lon,d=df.iloc[ind].gps_msl_alt))
                            fout.write('        <TimeStamp>\n')
                            fout.write('          <when>{a}Z</when>\n'.format(a=currTime_str))
                            fout.write('        </TimeStamp>\n')
                            fout.write('        <styleUrl>#PM1</styleUrl>\n')
                            fout.write('        <Point>\n')
                            fout.write('          <altitudeMode>absolute</altitudeMode>\n')
                            fout.write('          <coordinates>{a:0.4f},{b:0.4f},{c:0.1f}</coordinates>\n'.format(a=df.iloc[ind].lon,b=df.iloc[ind].lat,c=df.iloc[ind].gps_msl_alt))
                            fout.write('        </Point>\n')
                            fout.write('      </Placemark>\n')

                    # Output hyperlink ends
                    fout.write('    </Folder>\n')
                    fout.write('  </Document>\n')
                    fout.write('</kml>\n')

                    # Close file
                    fout.close()
                    
