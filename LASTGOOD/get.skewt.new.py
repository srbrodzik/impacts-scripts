#!/usr/bin/python

# For some reason skewplot.py has the year hardcoded into it for the NWS soundings
# so this will not run for other years unless that is changed

import os
import sys
import time
from datetime import timedelta
from datetime import datetime
import shutil

# user inputs
debug = 1
bin_dir = '/home/disk/bob/impacts/bin'
catalog_base_dir = "/home/disk/funnel/impacts/archive/ops"
skewt_base_dir = catalog_base_dir+'/skewt'
wetbulb_base_dir = catalog_base_dir+'/wet_bulb'
text_base_dir = catalog_base_dir+'/text_sounding'
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
siteList = {'72518':'ALB',
	    '72528':'BUF',
            '74494':'CHH',
            '72208':'CHS',
            '72632':'DTX',
            '74455':'DVN',
            '72317':'GSO',
            '74389':'GYX',
            '72403':'IAD',
            '72426':'ILN',
            '74560':'ILX',
            '72305':'MHX',
            '72649':'MPX',
            '72501':'OKX',
            '72520':'PIT',
            '72318':'RNK',
            '72402':'WAL'
}
numHours = len(hourList)
numSites = len(siteList)

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
print >>sys.stderr, 'dateStrList = ',dateStrList
   
# Go to data directory
os.chdir(catalog_base_dir)

for idx,idate in enumerate(dateStrList,0):

    # define year, month and day
    year = yearStrList[idx]
    month = monthStrList[idx]
    day = dayStrList[idx]
    
    # define date dirs and create them if necessary
    skewt_dir = skewt_base_dir+'/'+idate
    if not os.path.exists(skewt_dir):
        os.makedirs(skewt_dir)
    wetbulb_dir = wetbulb_base_dir+'/'+idate
    if not os.path.exists(wetbulb_dir):
        os.makedirs(wetbulb_dir)
    text_dir = text_base_dir+'/'+idate
    if not os.path.exists(text_dir):
        os.makedirs(text_dir)
        command = 'ln -s '+catalog_base_dir+'/text_sounding/index.php '+text_dir
        os.system(command)

    for site in siteList:

        print >>sys.stderr, 'site = ', siteList[site]

        for hour in hourList:

            print >>sys.stderr, 'hour = ', hour

            # define output file names
            outFile_skewt = skewt_dir+'/ops.skewt.'+idate+hour+'00.'+siteList[site]+'.png'
            outFile_wetbulb = wetbulb_dir+'/ops.wet_bulb.'+idate+hour+'00.'+siteList[site]+'.png'
            outFile_html = text_dir+'/ops.text_sounding.'+idate+hour+'00.'+siteList[site]+'.html'
            (base,ext) = os.path.splitext(outFile_html)
            print >>sys.stderr, 'outFile_html = ',outFile_html

            # get ascii data
            try:
                urlStr = 'http://weather.uwyo.edu/cgi-bin/sounding?region=naconf&TYPE=TEXT%3ALIST&YEAR='+year+'&MONTH='+month+'&FROM='+day+hour+'&TO='+day+hour+'&STNM='+site
                command = "lwp-request '"+urlStr+"' > "+outFile_html
                os.system(command)
                print >>sys.stderr, 'Done getting html file'
            except Exception as e:
                print sys.stderr, "lwp-request failed, exception: ", e
                continue

            # check filesize of html file
            fileSize = os.path.getsize(outFile_html)
            if fileSize <= 3000:
                print >>sys.stderr, 'html file too small - go to next hour'
                os.remove(outFile_html)
            else:
                print >>sys.stderr, 'html file okay - create skewt & wetbulb files'
                
                # Remove html tags from file
                command = bin_dir+'/removeHtmlTags.csh '+outFile_html+' '+base+'.txt'
	        os.system(command)
                
                # Remove missing data records from file
	        command = bin_dir+'/removeLinesWithMissingData.py '+base+'.txt '+base+'.new'
	        os.system(command)
                
                # Create skewt and move to field catalog directory
	        command = bin_dir+'/skewplot.py --file '+base+'.new --outpath /tmp --format UWYO --parcel False --hodograph False'
	        os.system(command)
	        command = '/bin/mv /tmp/upperair.NWS_'+siteList[site]+'_sonde.'+idate+hour+'00.skewT.png '+outFile_skewt
	        os.system(command)
                
                # Create wetbulb plot
                command = bin_dir+'/vertical_TvsTw_sean_rev_v2.py '+outFile_html+' '+outFile_wetbulb+' '+str(max_ht)
	        os.system(command)
                
                # Clean up
                command = '/bin/rm '+base+'.txt'+' '+base+'.new'
	        os.system(command)

                print >>sys.stderr, 'Done making skewt & wetbulb files'



