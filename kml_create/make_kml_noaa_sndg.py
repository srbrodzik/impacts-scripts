#!/usr/bin/python3

import os
import pandas as pd

def remove_dups_from_list(x):
  return list(dict.fromkeys(x))

siteLocs = '/home/disk/bob/impacts/bin/NOAA_sounding_sites.csv'
indir = '/home/disk/funnel/impacts-website/archive_ncar/upperair/SkewT'
outdir = '/home/disk/funnel/impacts-website/archive_ncar/gis/SkewT'
catalogBaseUrl = 'http://catalog.eol.ucar.edu/impacts_2020/upperair/skewt'

# read in site locations
# to access data use:
# siteDict[lat/lon/alt/site_abbr][site_long]
siteDict = pd.read_csv(siteLocs, header=0, index_col=0, squeeze=True).to_dict()

for date in os.listdir(indir):
    if date.startswith('2020'):
        timeList = []
        df = pd.DataFrame(columns=['time','site_abbr','site_long','lat','lon','alt','filename'])
        for file in os.listdir(indir+'/'+date):
            if 'Wet_Bulb' not in file:
                print(file)
                (base,ext) = os.path.splitext(file)
                (category,platform,datetime,site_long) = base.split('.')
                time = datetime[8:]
                timeList.append(time)
                df = df.append({'time':time,
                                'site_abbr':siteDict['site_abbr'][site_long],
                                'site_long':site_long,
                                'lat':siteDict['lat'][site_long],
                                'lon':siteDict['lon'][site_long],
                                'alt':siteDict['alt'][site_long],
                                'filename':file}, ignore_index=True)
        uniqueTimes = remove_dups_from_list(timeList)

        # create kml file for each time
        for fileTime in uniqueTimes:
            kmlName = outdir+'/gis.SkewT.'+date+fileTime+'.operational_gts.kml'
            fout = open(kmlName,'w')

            # write header
            fout.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            fout.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
            fout.write('<Document>\n')
            fout.write(' <name>IMPACTS NOAA Skewt Plots at '+date+time+'</name>\n')
            fout.write(' <Style id="site">\n')
            fout.write('  <IconStyle>\n')
            fout.write('   <scale>1</scale>\n')
            fout.write('   <Icon>\n')
            fout.write('    <href>http://www.eol.ucar.edu/flight_data/display/red.png</href>\n')
            fout.write('   </Icon>\n')
            fout.write('  </IconStyle>\n')
            fout.write(' </Style>\n')
            fout.write(' <Folder>\n')
            fout.write('  <name></name>\n')
            fout.write('  <open>1</open>\n')
            
            # Get df indices matching fileTime and create kml entry for each one
            ind = df.index[df['time'] == fileTime].tolist()
            for index in ind:
                data = df.iloc[index]
                if data.lat > 0:
                    lat = str(data.lat)+'N'
                else:
                    lat = str(abs(data.lat))+'S'
                data = df.iloc[index]
                if data.lon > 0:
                    lon = str(data.lon)+'E'
                else:
                    lon = str(abs(data.lon))+'W'
                filename_WB = data.filename.replace(data.site_long,data.site_long+'_Wet_Bulb')
                fout.write('  <Placemark>\n')
                fout.write('   <description><![CDATA[ <b>Date: '+date+'/'+fileTime[0:2]+'Z</b><br><b>Site: NOAA - '+
                           data.site_abbr+'</b><br><b>Location:</b> '+lat+' '+lon+'<br>\n')
                fout.write('  <a width=700 href="'+catalogBaseUrl+'/'+date+'/'+fileTime[0:2]+'/'+data.filename+
                           '" target="blank">\n')
                fout.write('<img width=700  src="'+catalogBaseUrl+'/'+date+'/'+fileTime[0:2]+'/'+data.filename+
                           '"><br>\n')
                fout.write('  <a width=700 href="'+catalogBaseUrl+'/'+date+'/'+fileTime[0:2]+'/'+filename_WB+
                           '" target="blank">\n')
                fout.write('<img width=700  src="'+catalogBaseUrl+'/'+date+'/'+fileTime[0:2]+'/'+filename_WB+
                           '">]]></description>\n')
                fout.write('   <styleUrl>#site</styleUrl>\n')
                fout.write('   <Point>\n')
                fout.write('   <altitudeMode>absolute</altitudeMode>\n')
                fout.write('   <coordinates>'+str(data.lon)+','+str(data.lat)+','+str(data.alt)+'</coordinates>\n')
                fout.write('   </Point>\n')
                fout.write('  </Placemark>\n')

            # Write end of file
            fout.write(' </Folder>\n')
            fout.write('</Document>\n')
            fout.write('</kml>\n')

            # Close file
            fout.close()
            
