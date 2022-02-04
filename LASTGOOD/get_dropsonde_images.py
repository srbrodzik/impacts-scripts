#!/usr/bin/python

import os
import sys
import shutil
from ftplib import FTP
#import fnmatch

debug = 1
test = False
url = "https://asp-interface.arc.nasa.gov/API/parameter_data/N426NA/AVAPS_QuickLook"
tempDir = "/tmp"
targetBaseDir = "/home/disk/bob/impacts/sonde"
#catalogBaseDir = "/home/disk/funnel/impacts/archive/research/p3"
sondeInfoFile = targetBaseDir+'/sonde_info'

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

# parse record to get filename & dropsonde date and time
(junk1,datetime,lat,lon,junk2,junk3,junk4,junk5,fileUrl) = record.split(',')
sondeFile = os.path.basename(fileUrl)
temp = sondeFile.replace('filehomeavapsdataskewtD','')
(dateSonde,timeSonde,junk) = temp.split('_')
#date = datetime[0:10]
#(year,month,day) = date.split('-')
#time = datetime[11:19]
#(hour,minute,second) = time.split(':')

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
