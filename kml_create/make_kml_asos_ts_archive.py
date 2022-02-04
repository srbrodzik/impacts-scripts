#!/usr/bin/python3

import os
import pandas as pd
from ftplib import FTP

def remove_dups_from_list(x):
  return list(dict.fromkeys(x))

test = False
siteLocs = '/home/disk/bob/impacts/bin/ASOS_sites.csv'
#indir = '/home/disk/funnel/impacts-website/archive_ncar/surface/Meteogram'
indir = '/home/disk/bob/impacts/images/asos_isu'
outdir = '/home/disk/funnel/impacts-website/archive_ncar/gis/Meteogram'
catalogBaseUrl = 'http://catalog.eol.ucar.edu/impacts_2022/surface/meteogram'

# Field Catalog inputs
if test:
    ftpCatalogServer = 'ftp.atmos.washington.edu'
    ftpCatalogUser = 'anonymous'
    ftpCatalogPassword = 'brodzik@uw.edu'
    catalogDestDir = 'brodzik/incoming/impacts'
else:
    ftpCatalogServer = 'catalog.eol.ucar.edu'
    ftpCatalogUser = 'anonymous'
    catalogDestDir = '/pub/incoming/catalog/impacts'

# read in site locations
# to access data use:
# siteDict[lat/lon/alt/site_abbr][site_long]
siteDict = pd.read_csv(siteLocs, header=0, index_col=0, squeeze=True).to_dict()

#for date in os.listdir(indir):
for date in ['20220101','20220102','20220103','20220104','20220105',
             '20220106','20220107','20220108','20220109','20220110',
             '20220111','20220112','20220113','20220114','20220115',
             '20220116','20220117','20220118','20220119','20220120',
             '20220121','20220122','20220123','20220124','20220125']:
  if date.startswith('2022'):
    hourList = []
    df = pd.DataFrame(columns=['hour','minute','site_abbr','site_long','lon','lat','alt','filename'])
    for file in os.listdir(indir+'/'+date):
      if 'ASOS' in file and file.endswith('png'):
        #print(file)
        (base,ext) = os.path.splitext(file)
        (category,platform,datetime,site_long) = base.split('.')
        if site_long in siteDict['site_abbr']:
          time = datetime[8:]
          hour = time[0:2]
          minute = time[2:]
          hourList.append(hour)
          df = df.append({'hour':hour,
                          'minute':minute,
                          'site_abbr':siteDict['site_abbr'][site_long],
                          'site_long':site_long,
                          'lon':siteDict['lon'][site_long],
                          'lat':siteDict['lat'][site_long],
                          'alt':siteDict['alt'][site_long],
                          'filename':file}, ignore_index=True)
    uniqueHours = sorted(remove_dups_from_list(hourList))

    # create kml file for each hour
    for fileHour in uniqueHours:
      kmlFile = 'gis.Meteogram.'+date+fileHour+'00.ASOS.kml'
      print(kmlFile)
      kmlName = outdir+'/'+kmlFile
      fout = open(kmlName,'w')

      # write header
      fout.write('<?xml version="1.0" encoding="UTF-8"?>\n')
      fout.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
      fout.write('<Document>\n')
      fout.write(' <name>IMPACTS ASOS Time Series Plots at '+date+'/'+fileHour+'00</name>\n')
      fout.write(' <Style id="site">\n')
      fout.write('  <IconStyle>\n')
      fout.write('   <scale>1</scale>\n')
      fout.write('   <Icon>\n')
      fout.write('    <href>http://catalog.eol.ucar.edu/kmlicons/green_dot.png</href>\n')
      fout.write('   </Icon>\n')
      fout.write('  </IconStyle>\n')
      fout.write(' </Style>\n')
      fout.write(' <Folder>\n')
      fout.write('  <name></name>\n')
      fout.write('  <open>1</open>\n')
      
      # Get df indices matching fileHour and create kml entry for each one
      ind = df.index[df['hour'] == fileHour].tolist()
      for index in ind:
        data = df.iloc[index]
        lat = round(data.lat,3)
        if lat > 0:
          lat_str = str(lat)+'N'
        else:
          lat_str = str(abs(lat))+'S'
        lon = round(data.lon,3)
        if lon > 0:
          lon_str = str(lon)+'E'
        else:
          lon_str = str(abs(lon))+'W'
        fout.write('  <Placemark>\n')
        fout.write('   <description><![CDATA[ <b>Date: '+date+'/'+fileHour+'Z</b><br><b>Site: ASOS - '+data.site_abbr+'</b><br><b>Location:</b> '+lat_str+' '+lon_str+'<br>\n')
        fout.write('  <a width=700 href="'+catalogBaseUrl+'/'+date+'/'+fileHour+'/'+data.filename+'" target="blank">\n')
        fout.write('<img width=700  src="'+catalogBaseUrl+'/'+date+'/'+fileHour+'/'+data.filename+'">]]></description>\n')
        fout.write('   <styleUrl>#site</styleUrl>\n')
        fout.write('   <Point>\n')
        fout.write('   <altitudeMode>absolute</altitudeMode>\n')
        fout.write('   <coordinates>'+str(lon)+','+str(lat)+','+str(data.alt)+'</coordinates>\n')
        fout.write('   </Point>\n')
        fout.write('  </Placemark>\n')
        
      # Write end of file
      fout.write(' </Folder>\n')
      fout.write('</Document>\n')
      fout.write('</kml>\n')

      # Close file
      fout.close()

      # Open ftp connection
      if test:
        catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser,ftpCatalogPassword)
        catalogFTP.cwd(catalogDestDir)
      else:
        catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
        catalogFTP.cwd(catalogDestDir)

      catalogFTP.set_pasv(False)
      
      # ftp file to catalog
      ftpFile = open(os.path.join(outdir,kmlFile),'rb')
      catalogFTP.storbinary('STOR '+kmlFile,ftpFile)
      ftpFile.close()
      
