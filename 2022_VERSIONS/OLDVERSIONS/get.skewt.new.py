#!/usr/bin/python3

# For some reason skewplot.py has the year hardcoded into it for the NWS soundings
# so this will not run for other years unless that is changed

import os
import sys
import time
from datetime import timedelta
from datetime import datetime
import shutil
from ftplib import FTP

# user inputs
debug = 1
bin_dir = '/home/disk/bob/impacts/bin'

ftpCatalogServer = 'catalog.eol.ucar.edu'
ftpCatalogUser = 'anonymous'
catalogDestDir = '/pub/incoming/catalog/impacts'
#ftpCatalogServer = 'ftp.atmos.washington.edu'
#ftpCatalogUser = 'anonymous'
#ftpCatalogPW = 'srbrodzik@gmail.com'
#catalogDestDir = 'incoming/brodzik/impacts'

text_base_dir = '/home/disk/bob/impacts/upperair'
max_ht = 7
secsPerDay = 86400
# set startFlag
#    0 -> start now
#    1 -> start at startDate
startFlag = 0
startDate = '20200229'
# set number of days to go back from startDate
num_days = 1
hourList = ['00','03','06','09','12','15','18','21']
siteList = {'72518':{'long_name':'Albany_NY','short_name':'ALB'},
            '72634':{'long_name':'Gaylord_MI','short_name':'APX'},
	    '72528':{'long_name':'Buffalo_NY','short_name':'BUF'},
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
            '72305':{'long_name':'Newport_NC','short_name':'MHX'},
            '72649':{'long_name':'Minneapolis_MN','short_name':'MPX'},
            '72501':{'long_name':'Upton_NY','short_name':'OKX'},
            '72520':{'long_name':'Pittsburgh_PA','short_name':'PIT'},
            '72318':{'long_name':'Blacksburg_VA','short_name':'RNK'},
            '72402':{'long_name':'Wallops_VA','short_name':'WAL'},
}
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
#if debug:
#    print('dateStrList = ',dateStrList)
   
# Go to data directory
#os.chdir(catalog_base_dir)
os.chdir(text_base_dir)

for idx,idate in enumerate(dateStrList,0):

    # define year, month and day
    year = yearStrList[idx]
    month = monthStrList[idx]
    day = dayStrList[idx]
    
    # define date dirs and create them if necessary
    #skewt_dir = skewt_base_dir+'/'+idate
    #if not os.path.exists(skewt_dir):
    #    os.makedirs(skewt_dir)
    #wetbulb_dir = wetbulb_base_dir+'/'+idate
    #if not os.path.exists(wetbulb_dir):
    #    os.makedirs(wetbulb_dir)
    text_dir = text_base_dir+'/'+idate
    if not os.path.exists(text_dir):
        os.makedirs(text_dir)
        #command = 'ln -s '+catalog_base_dir+'/text_sounding/index.php '+text_dir
        #os.system(command)

    # get list of files in text_dir
    text_dir_files = os.listdir(text_dir)
            
    # cd to text_dir
    os.chdir(text_dir)
            
    for site in siteList:

        #print >>sys.stderr, 'site = ', siteList[site]['short_name']

        for hour in hourList:

            #print >>sys.stderr, 'hour = ', hour

            # define output file names
            #outFile_skewt = skewt_dir+'/ops.skewt.'+idate+hour+'00.'+siteList[site]+'.png'
            #outFile_wetbulb = wetbulb_dir+'/ops.wet_bulb.'+idate+hour+'00.'+siteList[site]+'.png'
            #outFile_html = text_dir+'/ops.text_sounding.'+idate+hour+'00.'+siteList[site]+'.html'
            outFile_skewt = outfile_prefix+'.'+idate+hour+'00.'+siteList[site]['long_name']+'.png'
            outFile_wetbulb = outfile_prefix+'.'+idate+hour+'00.'+siteList[site]['long_name']+outfile_wb_suffix+'.png'
            outFile_html = outfile_prefix+'.'+idate+hour+'00.'+siteList[site]['short_name']+'.html'
            (base,ext) = os.path.splitext(outFile_html)
            #print >>sys.stderr, 'outFile_html = ',outFile_html

            # Check to make sure we don't already have data for this hour
            if not outFile_html in text_dir_files:
            
                # get ascii data
                try:
                    urlStr = 'http://weather.uwyo.edu/cgi-bin/sounding?region=naconf&TYPE=TEXT%3ALIST&YEAR='+year+'&MONTH='+month+'&FROM='+day+hour+'&TO='+day+hour+'&STNM='+site
                    command = "lwp-request '"+urlStr+"' > "+outFile_html
                    os.system(command)
                    #print >>sys.stderr, 'Done getting html file'
                except Exception as e:
                    #print sys.stderr, "lwp-request failed, exception: ", e
                    continue

                # check filesize of html file
                fileSize = os.path.getsize(outFile_html)
                if fileSize <= 3000:
                    #print >>sys.stderr, 'html file too small - go to next hour'
                    os.remove(outFile_html)
                else:
                    #print >>sys.stderr, 'html file okay - create skewt & wetbulb files'

                    # Remove html tags from file
                    command = bin_dir+'/removeHtmlTags.csh '+outFile_html+' '+base+'.txt'
	            os.system(command)
                
                    # Remove missing data records from file
	            command = bin_dir+'/removeLinesWithMissingData.py '+base+'.txt '+base+'.new'
	            os.system(command)

                    # Open ftp connection
                    #catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
                    catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser,ftpCatalogPW)
                    catalogFTP.cwd(catalogDestDir)
                    
                    # Create skewt (assumes png extension) and substitute long_name for short_name in fname
                    localSkewtPath = '/tmp/'+outFile_skewt
	            command = bin_dir+'/skewplot.py --file '+base+'.new --outpath /tmp --format UWYO --parcel False --hodograph False'
	            os.system(command)
                    shutil.move('/tmp/'+base+'.png','/tmp/'+outFile_skewt)
                    # Move to field catalog directory
	            #command = '/bin/mv /tmp/upperair.NWS_'+siteList[site]+'_sonde.'+idate+hour+'00.skewT.png '+outFile_skewt
	            #os.system(command)
                    # ftp to EOL
                    ftpFile = open(localSkewtPath,'rb')
                    catalogFTP.storbinary('STOR '+outFile_skewt,ftpFile)
                    ftpFile.close()

                    # Create wetbulb plot
                    # NOTE: Change code so figure header uses short_name instead of long_name
                    localWbPath = '/tmp/'+outFile_wetbulb
                    command = bin_dir+'/vertical_TvsTw_sean_rev_v2.py '+outFile_html+' '+localWbPath+' '+str(max_ht)
	            os.system(command)
                    # ftp to EOL
                    ftpFile = open(localWbPath,'rb')
                    catalogFTP.storbinary('STOR '+outFile_wetbulb,ftpFile)
                    ftpFile.close()

                    # Close ftp connection
                    catalogFTP.quit()
                
                    # Clean up
                    #command = '/bin/rm '+base+'.txt'+' '+base+'.new'
                    command = '/bin/rm '+base+'.txt '+base+'.new '+localSkewtPath+' '+localWbPath
	            os.system(command)

                    #print >>sys.stderr, 'Done making skewt & wetbulb files'



