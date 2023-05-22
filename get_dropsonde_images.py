#!/usr/bin/python3

import os
import sys
import shutil
from ftplib import FTP
#import fnmatch

debug = True
test = False
url = "https://asp-interface.arc.nasa.gov/API/parameter_data/N426NA/AVAPS_QuickLook"
tempDir = "/tmp"
targetBaseDir = "/home/disk/bob/impacts/sonde"
#catalogBaseDir = "/home/disk/funnel/impacts/archive/research/p3"
sondeInfoFile = targetBaseDir+'/sonde_info'
catalogBaseUrl = 'http://catalog.eol.ucar.edu/impacts_2023/aircraft/nasa_p3'

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

# Open ftp connection
if test:
    catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser,ftpCatalogPassword)
    catalogFTP.cwd(catalogDestDir)
else:
    catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
    catalogFTP.cwd(catalogDestDir)

# remove any old AVAPS files from tempDir
#removeFilesByMatchingPattern(tempDir, 'AVAPS')

# get latest data from url
os.chdir(tempDir)
command = "wget "+url
os.system(command)

# read file
f = open('AVAPS_QuickLook','r')
recordWithEOL = f.read()
record = recordWithEOL.strip()
f.close()
os.remove('AVAPS_QuickLook')

# record is in this format:
# AVAPS_QuickLook,2023-01-23T18:10:09.005000,43.219871521,-69.889011383,,220.84,1.13,0.75,https://asp-interface.arc.nasa.gov/cameras/filehomeavapsdataskewtD20230123_180403_P.1.svg

# parse record to get filename & dropsonde date and time
# this data is actually the datetime, lat, lon, alt, pitch, roll WHEN THE P3 TRANSMITS
#   THE FILE (useless); also the time,lat,lon on the plot is the LAUNCH point
(junk1,datetime,latOrig,lonOrig,junk2,junk3,junk4,junk5,fileUrl) = record.split(',')
sondeFile = os.path.basename(fileUrl)
temp = sondeFile.replace('filehomeavapsdataskewtD','')
(dateSonde,timeSonde,junk) = temp.split('_')

# get lat/lon info for later
lat = str(round(float(latOrig),3))
lon = str(round(float(lonOrig),3))
if lat[0] == '-':
    latDir = 'S'
    latNoSign = lat[1:]
else:
    latDir = 'N'
    latNoSign = lat
if lon[0] == '-':
    lonDir = 'W'
    lonNoSign = lon[1:]
else:
    lonDir = 'E'
    lonNoSign = lon

targetDir = targetBaseDir+'/'+dateSonde
if not os.path.exists(targetDir):
    os.makedirs(targetDir)
os.chdir(targetDir)

# get list of files in targetDir; if sondeFile not included, download it there
sondeFileList = os.listdir(targetDir)
if sondeFile not in sondeFileList:

    if debug:
        print(sondeFile,"not downloaded yet -- downloading . . . ")
    
    command = "wget "+fileUrl
    os.system(command)

    # convert to gif
    (base,ext) = os.path.splitext(sondeFile)
    sondeGifFile = base+'.gif'
    command = 'convert '+sondeFile+' -background white -flatten '+sondeGifFile
    os.system(command)
    
    # rename gif file, ftp to catalog, save locally
    catalogName = 'aircraft.NASA_P3.'+dateSonde+timeSonde+'.AVAPS.gif'
    shutil.move(targetDir+'/'+sondeGifFile,
                targetDir+'/'+catalogName)
    
    ftpFile = open(os.path.join(targetDir,catalogName),'rb')
    catalogFTP.storbinary('STOR '+catalogName,ftpFile)
    ftpFile.close()
            
    # add record to concatenated list of sondes
    with open(sondeInfoFile,"a") as myfile:
        myfile.write(recordWithEOL)

    # create and ftp kml file to catalog
    kmlName = 'gis.NASA_P3.'+dateSonde+timeSonde[0:4]+'.drop_points.kml'
    print('{} {}'.format('kml file: ',kmlName))
    fout = open(targetDir+'/'+kmlName,'w')
        
    # write header
    fout.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    fout.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
    fout.write('<Document>\n')
    fout.write(' <name>P3 Sonde '+dateSonde+' '+timeSonde[0:4]+'Z</name>\n')
    fout.write(' <Style id="blueCircle">\n')
    fout.write('  <IconStyle>\n')
    fout.write('   <Icon>\n')
    fout.write('    <href>http://catalog.eol.ucar.edu/kmlicons/blue_circle.png</href>\n')
    fout.write('   </Icon>\n')
    fout.write('  </IconStyle>\n')
    fout.write(' </Style>\n')

    # get indiv strings for year, month, day, hour, minute, second
    yrStr = dateSonde[0:4]
    moStr = dateSonde[4:6]
    dayStr = dateSonde[6:8]
    hrStr = timeSonde[0:2]
    minStr = timeSonde[2:4]
    secStr = timeSonde[4:6]
    
    # write content
    fout.write(' <Placemark>\n')
    fout.write('   <name>Drop - NASA_P3</name>\n')
    fout.write('   <description><![CDATA[<p><b>'+moStr+'/'+dayStr+'/'+yrStr+' '+hrStr+':'+minStr+':'+secStr+' UTC</b></p> <br>\n')
    fout.write('    <a href="'+catalogBaseUrl+'/'+dateSonde+'/'+hrStr+'/'+catalogName+'" target="blank">\n')
    fout.write('   <img src="'+catalogBaseUrl+'/'+dateSonde+'/'+hrStr+'/'+catalogName+'"></a>\n')
    fout.write('   <br>Lat: '+latNoSign+latDir+'<br> Lon: '+lonNoSign+lonDir+'<br>]]></description>\n')
    fout.write('   <styleUrl>#blueCircle</styleUrl>\n')
    fout.write('   <Point>\n')
    fout.write('    <coordinates>'+lon+','+lat+',0.0</coordinates>\n')
    fout.write('   </Point>\n')
    fout.write(' </Placemark>\n')

    # write footer
    fout.write('</Document>\n')
    fout.write('</kml>\n')

    # close kml file
    fout.close()

    # ftp file to catalog
    ftpFile = open(os.path.join(targetDir,kmlName),'rb')
    catalogFTP.storbinary('STOR '+kmlName,ftpFile)
    ftpFile.close()

# Close ftp connection
catalogFTP.quit()

'''
Generic function to delete all the files from a given directory based on matching pattern
'''
#def removeFilesByMatchingPattern(dirPath, pattern):
#    listOfFilesWithError = []
#    for parentDir, dirnames, filenames in os.walk(dirPath):
#        for filename in fnmatch.filter(filenames, pattern):
#            try:
#                os.remove(os.path.join(parentDir, filename))
#            except:
#                print("Error while deleting file : ", os.path.join(parentDir, filename))
#                listOfFilesWithError.append(os.path.join(parentDir, filename))
 
#    #return listOfFilesWithError
