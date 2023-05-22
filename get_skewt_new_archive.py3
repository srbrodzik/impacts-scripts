#!/usr/bin/python3

import os
import sys
import time
from datetime import timedelta
from datetime import datetime
import requests
import shutil
from ftplib import FTP

# user inputs
debug = True
test = False
binDir = '/home/disk/bob/impacts/bin'

if test:
    ftpCatalogServer = 'ftp.atmos.washington.edu'
    ftpCatalogUser = 'anonymous'
    ftpCatalogPassword = 'brodzik@uw.edu'
    catalogDestDir = 'brodzik/incoming/impacts'
else:
    ftpCatalogServer = 'catalog.eol.ucar.edu'
    ftpCatalogUser = 'anonymous'
    catalogDestDir = '/pub/incoming/catalog/impacts'

out_base_dir = '/home/disk/bob/impacts/upperair/nws'
max_ht = 7
secsPerDay = 86400
# set startFlag
#    0 -> start now
#    1 -> start at startDate
startFlag = 1
startDate = '20230226'
# set number of days to go back from startDate
num_days = 1

hourList = ['00','03','06','09','12','15','18','21']
siteList = {'72659':{'long_name':'Aberdeen_SD','short_name':'ABR'},
            '72518':{'long_name':'Albany_NY','short_name':'ALB'},
            '72634':{'long_name':'Gaylord_MI','short_name':'APX'},
	    '72528':{'long_name':'Buffalo_NY','short_name':'BUF'},
            '72712':{'long_name':'Caribou_ME','short_name':'CAR'},
            '74494':{'long_name':'Chatham_MA','short_name':'CHH'},
            '72208':{'long_name':'Charleston_SC','short_name':'CHS'},
            '72632':{'long_name':'Detroit_MI','short_name':'DTX'},
            '74455':{'long_name':'Davenport_IA','short_name':'DVN'},
            '72215':{'long_name':'Peachtree_City_GA','short_name':'FFC'},
            '72645':{'long_name':'Green_Bay_WI','short_name':'GRB'},
            '72317':{'long_name':'Greensboro_NC','short_name':'GSO'},
            '74389':{'long_name':'Gray_ME','short_name':'GYX'},
            '72403':{'long_name':'Sterling_VA','short_name':'IAD'},
            '72426':{'long_name':'Wilmington_OH','short_name':'ILN'},
            '74560':{'long_name':'Lincoln_IL','short_name':'ILX'},
            '72747':{'long_name':'International_Falls_MN','short_name':'INL'},
            '72305':{'long_name':'Newport_NC','short_name':'MHX'},
            '72649':{'long_name':'Minneapolis_MN','short_name':'MPX'},
            '72501':{'long_name':'Upton_NY','short_name':'OKX'},
            '72520':{'long_name':'Pittsburgh_PA','short_name':'PIT'},
            '72318':{'long_name':'Blacksburg_VA','short_name':'RNK'},
            '72402':{'long_name':'Wallops_VA','short_name':'WAL'}
            }
siteList = {'72210':{'long_name':'Tampa_Bay_FL','short_name':'TBW'}}
numHours = len(hourList)
numSites = len(siteList)
outfile_prefix = 'upperair.SkewT'
outfile_wb_suffix = '_Wet_Bulb'

# Get start date
if startFlag == 0:
    nowTime = time.gmtime()
    now = datetime(nowTime.tm_year, nowTime.tm_mon, nowTime.tm_mday,
                   nowTime.tm_hour, nowTime.tm_min, nowTime.tm_sec)
else:
    nowDateStr = startDate
    now = datetime.strptime(nowDateStr,'%Y%m%d')

nowDateStr = now.strftime("%Y%m%d")
nowYearStr = now.strftime("%Y")
nowMonthStr = now.strftime("%m")
nowDayStr = now.strftime("%d")

# Make list of dates to process
dateStrList = []
yearStrList = []
monthStrList = []
dayStrList = []
for idate in range(0,num_days):
    deltaSecs = timedelta(0, idate * secsPerDay)
    nextDate = now - deltaSecs
    nextDateStr = nextDate.strftime("%Y%m%d")
    dateStrList.append(nextDateStr)
    nextYearStr = nextDate.strftime("%Y")
    yearStrList.append(nextYearStr)
    nextMonthStr = nextDate.strftime("%m")
    monthStrList.append(nextMonthStr)
    nextDayStr = nextDate.strftime("%d")
    dayStrList.append(nextDayStr)
print('dateStrList = ',dateStrList)
   
# Go to data directory
os.chdir(out_base_dir)

for idx,idate in enumerate(dateStrList,0):

    # define year, month and day
    year = yearStrList[idx]
    month = monthStrList[idx]
    day = dayStrList[idx]

    # define date dirs and create them if necessary
    out_dir = out_base_dir+'/'+idate
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # get list of files in out_dir
    out_dir_files = os.listdir(out_dir)
            
    # cd to out_dir
    os.chdir(out_dir)
            
    for site in siteList:

        print('site = ', siteList[site])

        for hour in hourList:

            print('hour =', hour)

            # define output file names
            outFile_skewt = outfile_prefix+'.'+idate+hour+'00.'+siteList[site]['long_name']+'.png'
            outFile_wetbulb = outfile_prefix+'.'+idate+hour+'00.'+siteList[site]['long_name']+outfile_wb_suffix+'.png'
            outFile_html = outfile_prefix+'.'+idate+hour+'00.'+siteList[site]['short_name']+'.html'
            (base,ext) = os.path.splitext(outFile_html)

            # Check to make sure we don't already have data for this hour
            if not outFile_html in out_dir_files:

                # get ascii data
                urlStr = 'http://weather.uwyo.edu/cgi-bin/sounding?region=naconf&TYPE=TEXT%3ALIST&YEAR='+year+'&MONTH='+month+'&FROM='+day+hour+'&TO='+day+hour+'&STNM='+site

                # make sure url exists
                get = requests.get(urlStr)
                if get.status_code == 200:
                    command = "lwp-request '"+urlStr+"' > "+outFile_html
                    os.system(command)
                    #print('Done getting html file')

                    # check filesize of html file
                    fileSize = os.path.getsize(outFile_html)
                    if fileSize <= 3000:
                        #print('html file too small - go to next hour')
                        os.remove(outFile_html)
                    else:
                        print('html file okay - create skewt & wetbulb files')
                
                        # Remove html tags from file
                        command = binDir+'/removeHtmlTags.csh '+outFile_html+' '+base+'.txt'
                        os.system(command)
                
                        # Remove missing data records from file
                        command = binDir+'/removeLinesWithMissingData.py '+base+'.txt '+base+'.new'
                        os.system(command)

                        #print('Done creating txt and new files from html file')
                        
                        # Open ftp connection
                        if test:
                            catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser,ftpCatalogPassword)
                            catalogFTP.cwd(catalogDestDir)
                        else:
                            catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
                            catalogFTP.cwd(catalogDestDir)
                        
                        # Create skewt and move to field catalog directory
                        localSkewtPath = out_dir+'/'+outFile_skewt
                        command = binDir+'/plot_skewt.py --inpath '+out_dir+' --infile '+base+'.new --outpath '+out_dir+' --fmt UWYO --hodo False --wb True --vlim 7'
                        print('skewt command =',command)
                        os.system(command)
                    
                        # Move to field catalog directory
                        ftpFile = open(localSkewtPath,'rb')
                        catalogFTP.storbinary('STOR '+outFile_skewt,ftpFile)
                        ftpFile.close()
                
                        # ftp wetbulb plot
                        # NOTE: Change code so figure header uses short_name instead of long_name
                        localWbPath = out_dir+'/'+outFile_wetbulb
                        ftpFile = open(localWbPath,'rb')
                        catalogFTP.storbinary('STOR '+outFile_wetbulb,ftpFile)
                        ftpFile.close()
                
                        # Close ftp connection
                        catalogFTP.quit()
                
                        # Clean up
                        command = '/bin/rm '+base+'.txt '+base+'.new'
                        os.system(command)
                    
                        print('Done making skewt & wetbulb files')
