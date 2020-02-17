#!/usr/bin/python

import os
import sys
import shutil
#import fnmatch

debug = 1
url = "https://asp-interface.arc.nasa.gov/API/parameter_data/N426NA/AVAPS_QuickLook"
tmpDir = "/tmp"
targetBaseDir = "/home/disk/bob/impacts/sonde"
catalogBaseDir = "/home/disk/funnel/impacts/archive/research/p3"
sondeInfoFile = targetBaseDir+'/sonde_info'

# remove any old AVAPS files from tmpDir
#removeFilesByMatchingPattern(tmpDir, 'AVAPS')

# get latest data from url
os.chdir(tmpDir)
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

# get list of files in targetBaseDir; if sondeFile not included, download it there
sondeFileList = os.listdir(targetDir)
if sondeFile not in sondeFileList:

    if debug:
        print >>sys.stderr, sondefile,"not downloaded yet -- downloading . . . "
    
    command = "wget "+fileUrl
    os.system(command)

    # convert to gif
    (base,ext) = os.path.splitext(sondeFile)
    sondeGifFile = base+'.gif'
    command = 'convert '+sondeFile+' -background white -flatten '+sondeGifFile
    os.system(command)
    
    # rename gif file, copy to catalog, remove it
    catalogFile = 'research.p3.'+dateSonde+timeSonde+'.dropsonde.gif'
    catalogDir = catalogBaseDir+'/'+dateSonde
    if not os.path.exists(catalogDir):
        os.makedirs(catalogDir)
    shutil.copy(targetDir+'/'+sondeGifFile,catalogDir+'/'+catalogFile)
    os.remove(sondeGifFile)
    
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
