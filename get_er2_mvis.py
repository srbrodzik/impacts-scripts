#!/usr/bin/python3

# Inconsistent naming of daily subdirectories after unzip.  Sometimes HH, othertimes HHMM

import os
import sys
import shutil
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from ftplib import FTP
from zipfile import ZipFile

def listFD(url, ext=''):
    page = requests.get(url).text
    #print page
    soup = BeautifulSoup(page, 'html.parser')
    return [url + '/' + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]

def getImageHHMM(path):
    flist = os.listdir(path)
    hhmmList = []
    for file in flist:
        (base,ext) = os.path.splitext(file)
        # assumes base is YYYYMMDDhhmmss
        hhmm = base[8:12]
        if hhmm not in hhmmList:
            hhmmList.append(hhmm)
    return hhmmList
    
if len(sys.argv) != 2:
    print('Usage: sys.argv[0] [YYYY-MM-DD]')
    sys.exit()
else:
    date = sys.argv[1]    

# User inputs
debug = 1
file_ext = 'zip'
#url = 'https://asp-archive.arc.nasa.gov/IMPACTS/N809NA/video_2022/'+date+'/MVIS'
url = 'https://asp-archive.arc.nasa.gov/IMPACTS/N809NA/still-images_2022/'+date+'/MVIS'
tempDir = "/tmp"
targetDirBase = "/home/disk/bob/impacts/images/MVIS"
catPrefix = 'aircraft.NASA_ER2'
catSuffix = 'MVIS'
ftpCatalogServer = 'catalog.eol.ucar.edu'
ftpCatalogUser = 'anonymous'
catalogDestDir = '/pub/incoming/catalog/impacts'

# Create image directory, if needed
targetDir = targetDirBase+'/'+date.replace('-','')
if not os.path.exists(targetDir):
    os.makedirs(targetDir)
    
# Get filelist from url
urlFlist = listFD(url, file_ext)

# Save first file every minute
os.chdir(targetDir)
for file in urlFlist:
    command = 'wget '+file
    os.system(command)
    # naming convention is:
    # IMPACTS-MVIS_ER2_2022010815_R0_still-images-jpeg.zip
    fname = os.path.basename(file)
    (proj,plane,dateHour,junk,suffix) = fname.split('_')
    # ONE OR THE OTHER - DUE TO INCONSISTENT DIRECTORY NAMING CONVENTIONS
    #time = dateHour[-2:]+'00'
    time = dateHour[-2:]
    try:
        with ZipFile(fname, 'r') as zip:
            zip.extractall()
        os.remove(fname)
        if os.path.exists('__MACOSX'):
            shutil.rmtree('__MACOSX')
        os.chdir(targetDir+'/'+time)
        for imgFile in os.listdir():
            print(imgFile)
            if '_' in imgFile or os.path.getsize(imgFile) == 0:
                print('  {} removed'.format(imgFile))
                os.remove(targetDir+'/'+time+'/'+imgFile)
            else:
                (base,ext) = os.path.splitext(imgFile)
                hhmm = base[8:12]
                if hhmm not in getImageHHMM(targetDir):
                    shutil.move(targetDir+'/'+time+'/'+imgFile,
                                targetDir+'/'+imgFile)
                else:
                    os.remove(targetDir+'/'+time+'/'+imgFile)
        os.chdir(targetDir)
        os.rmdir(time)
    except:
        print('Unable to unzip {}'.format(fname))

"""
# Open ftp connection
catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
catalogFTP.cwd(catalogDestDir)

# Rename jpg files & upload to catalog
for file in os.listdir(targetDir):
    print(file)
    (imageTime,ext) = os.path.splitext(file)
    imageTime = imageTime[:-2]
    catName = catPrefix+'.'+imageTime+'.'+catSuffix+ext
    shutil.copy(targetDir+'/'+file,
                tempDir+'/'+catName)
        
    ftpFile = open(tempDir+'/'+catName,'rb')
    catalogFTP.storbinary('STOR '+catName,ftpFile)
    ftpFile.close()

    os.remove(tempDir+'/'+catName)

# Close ftp connection
catalogFTP.quit()
"""
