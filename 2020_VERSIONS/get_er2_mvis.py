#!/usr/bin/python

import os
import sys
import shutil
#import fnmatch

debug = 1
url = "https://asp-interface.arc.nasa.gov/API/parameter_data/N809NA/MVIS"
downloadFile = os.path.basename(url)
tmpDir = "/tmp"
targetBaseDir = "/home/disk/bob/impacts/er2/MVIS"
catalogBaseDir = "/home/disk/funnel/impacts/archive/research/er2"
mvisInfoFile = targetBaseDir+'/mvis_info'

# remove any old MVIS files from tmpDir
#removeFilesByMatchingPattern(tmpDir, 'MVS')

# get latest data from url
os.chdir(tmpDir)
command = "wget "+url
os.system(command)

# read file
f = open(downloadFile,'r')
recordWithEOL = f.read()
record = recordWithEOL.strip()
f.close()
os.remove(downloadFile)

# parse record to get filename
parts = record.split(',')
fileUrl = parts[-1]
mvisFile = os.path.basename(fileUrl)
(base,ext) = os.path.splitext(mvisFile)
(prefix,datetime) = base.split('-')
date = datetime[0:8]
year = date[0:4]
month = date[4:6]
day = date[6:]
time = datetime[8:]
hour = time[0:2]
minute = time[2:4]
second = time[4:]

targetDir = targetBaseDir+'/'+year+month+day
if not os.path.exists(targetDir):
    os.makedirs(targetDir)
os.chdir(targetDir)

# get list of files in targetBaseDir; if mvisFile not included, download it there
mvisFileList = os.listdir(targetDir)
if mvisFile not in mvisFileList:

    if debug:
        print >>sys.stderr, mvisfile,"not downloaded yet -- downloading . . . "
    
    command = "wget "+fileUrl
    os.system(command)

    # convert to gif
    #(base,ext) = os.path.splitext(mvisFile)
    #mvisGifFile = base+'.jpg'
    #command = 'convert '+mvisFile+' -background white -flatten '+mvisGifFile
    #os.system(command)
    
    # rename jpg file, copy to catalog, remove it
    catalogFile = 'research.er2.'+year+month+day+hour+minute+second+'.mvis.jpg'
    catalogDir = catalogBaseDir+'/'+year+month+day
    if not os.path.exists(catalogDir):
        os.makedirs(catalogDir)
    shutil.copy(targetDir+'/'+mvisFile,catalogDir+'/'+catalogFile)
    #os.remove(sondeGifFile)
    
    # add record to concatenated list of mvis records
    with open(mvisInfoFile,"a") as myfile:
        myfile.write(recordWithEOL)
    myfile.close()
        
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
