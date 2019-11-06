#!/usr/bin/perl

# This data also available here
#   /home/disk/data/pnw/upperair
# One file per day with all sites concatenated

use LWP::Simple;

$command = "umask 2";
system($command);

#define system env variables
$ENV{'PATH'} = "/usr/local/bin:/usr/ucb:".$ENV{'PATH'};
$ENV{'PYTHONPATH'} = "/home/disk/bob/impacts/bin:/home/disk/shear2/brodzik/python:/usr/local/lib/python2.7/dist-packages:/usr/local/lib/python2.7/lib-tk:".$ENV{'PYTHONPATH'};
$ENV{'LD_LIBRARY_PATH'} = "/opt/intel/compilers_and_libraries_2019.1.144/linux/compiler/lib/intel64_lin";
#$ENV{'DISPLAY'} = ":0";

#$binDir = "/home/disk/bob/impacts/bin";

# Set max height (in km) of plot
$max_ht = 7;

# Go to data directory
#$ARCHIVE_PATH = "/home/disk/user_www/brodzik/olympex/archive/ops";
$ARCHIVE_PATH = "/home/disk/funnel/impacts/archive/ops";
chdir($ARCHIVE_PATH);

# First, get time and make date subdirs if necessary
$yesterday = `date -u --date='1 day ago' "+%Y%m%d"`;
chop $yesterday;
#$yesterday = '20190731';
$yesterdaySkewtDir = $ARCHIVE_PATH."/skewt/".$yesterday;
unless (-e $yesterdaySkewtDir) {
    mkdir $yesterdaySkewtDir;
}
$yesterdayWetbulbDir = $ARCHIVE_PATH."/wet_bulb/".$yesterday;
unless (-e $yesterdayWetbulbDir) {
    mkdir $yesterdayWetbulbDir;
}
$yesterdayTextDir = $ARCHIVE_PATH."/text_sounding/".$yesterday;
unless (-e $yesterdayTextDir) {
    mkdir $yesterdayTextDir;
    $command = "ln -s ".$ARCHIVE_PATH."/text_sounding/index.php ".$yesterdayTextDir;
    system($command);
}
$yesterdayYear=substr($yesterday,0,4);
$yesterdayMonth=substr($yesterday,4,2);
$yesterdayDay=substr($yesterday,6,2);

$today = `date -u "+%Y%m%d"`;
chop $today;
#$today = '20190801';
$todaySkewtDir = $ARCHIVE_PATH."/skewt/".$today;
unless (-e $todaySkewtDir) {
    mkdir $todaySkewtDir;
}
$todayWetbulbDir = $ARCHIVE_PATH."/wet_bulb/".$today;
unless (-e $todayWetbulbDir) {
    mkdir $todayWetbulbDir;
}
$todayTextDir = $ARCHIVE_PATH."/text_sounding/".$today;
unless (-e $todayTextDir) {
    mkdir $todayTextDir;
    $command = "ln -s ".$ARCHIVE_PATH."/text_sounding/index.php ".$todayTextDir;
    system($command);
}

$todayYear=substr($today,0,4);
$todayMonth=substr($today,4,2);
$todayDay=substr($today,6,2);

# Define sites of interest
%siteID = (
    '72518', 'ALB',
    '72528', 'BUF',
    '74494', 'CHH',
    '72208', 'CHS',
    '72632', 'DTX',
    '74389', 'GYX',
    '72403', 'IAD',
    '72426', 'ILN',
    '74560', 'ILX',
    '72501', 'OKX',
    '72520', 'PIT',
    '72318', 'RNK',
    '72402', 'WAL',
    );
@siteNum = (keys %siteID);
$numSites = @siteNum;

# Define skewt times (hours)
#@times = ('00','06','12','18');
@times = ('00','12');
$numTimes = @times;

# Download yesterday's ascii data and create associated skewt
for ($isite=0;$isite<$numSites;$isite++) {

    #print "site = $siteID{$siteNum[$isite]}\n";
    
    for ($itime=0;$itime<$numTimes;$itime++) {

	#print "time = $times[$itime]\n";

	$outFile_skewt = $yesterdaySkewtDir."/ops.skewt.".$yesterday.$times[$itime]."00.".$siteID{$siteNum[$isite]}.".png";
	$outFile_wetbulb = $yesterdayWetbulbDir."/ops.wet_bulb.".$yesterday.$times[$itime]."00.".$siteID{$siteNum[$isite]}.".png";
	$outFile_html = $yesterdayTextDir."/ops.text_sounding.".$yesterday.$times[$itime]."00.".$siteID{$siteNum[$isite]}.".html";
	#print "outFile_html = $outFile_html\n";
	
	# get ascii data
	$urlStr = 'http://weather.uwyo.edu/cgi-bin/sounding?region=naconf&TYPE=TEXT%3ALIST&YEAR='.$yesterdayYear.'&MONTH='.$yesterdayMonth.'&FROM='.$yesterdayDay.$times[$itime].'&TO='.$yesterdayDay.$times[$itime].'&STNM='.$siteNum[$isite];
	print "urlStr = $urlStr\n";
	$command = "lwp-request '".$urlStr."' > ".$outFile_html;
	system("$command");
	#print "   Done getting yesterdays html file\n'";
	$filesize = -s $outFile_html;
	if ($filesize <= 3000) {
	    print "file too small - go to next time\n";
	    system("/bin/rm $outFile_html");
	}
	else {
	    print "file okay - create skewt\n";
	    #Convert text data to skewt
	    $command = "/home/disk/bob/impacts/bin/removeHtmlTags.csh ".$outFile_html." ".$outFile_html.".txt";
	    system("$command");
	    $command = "/usr/bin/python /home/disk/bob/impacts/bin/removeLinesWithMissingData.py ".$outFile_html.".txt ".$outFile_html.".new";
	    system("$command");
	    $command = "/usr/bin/python /home/disk/bob/impacts/bin/skewplot.py --file ".$outFile_html.".new --outpath /tmp --format UWYO";
	    #print "command = $command\n";
	    system("$command");

	    print "file okay - create T vs Tw plot\n";
	    #Convert text data to T vs Tw plot
	    $command = "/usr/bin/python /home/disk/bob/impacts/bin/vertical_TvsTw_sean_rev_v2.py ".$outFile_html." ".$outFile_wetbulb." ".$max_ht;
	    #print "command = $command\n";
	    system($command);
	    
	    $command = "/bin/rm ".$outFile_html.".txt"." ".$outFile_html.".new";
	    system("$command");
	    $command = "/bin/mv /tmp/upperair.NWS_".$siteID{$siteNum[$isite]}."_sonde.".$yesterday.$times[$itime]."00.skewT.png ".$outFile_skewt;
	    #print "command = $command\n";
	    system("$command");
	    #print "   Done making yesterdays skewt file\n";
	}
    }
}

# Create today images and tables and download each one
for ($isite=0;$isite<$numSites;$isite++) {
    for ($itime=0;$itime<$numTimes;$itime++) {

	$outFile_skewt = $todaySkewtDir."/ops.skewt.".$today.$times[$itime]."00.".$siteID{$siteNum[$isite]}.".png";
	$outFile_wetbulb = $todayWetbulbDir."/ops.wet_bulb.".$today.$times[$itime]."00.".$siteID{$siteNum[$isite]}.".png";
	$outFile_html = $todayTextDir."/ops.text_sounding.".$today.$times[$itime]."00.".$siteID{$siteNum[$isite]}.".html";
	#print "outFile_html = $outFile_html\n";

	# get ascii data
	$urlStr = 'http://weather.uwyo.edu/cgi-bin/sounding?region=naconf&TYPE=TEXT%3ALIST&YEAR='.$todayYear.'&MONTH='.$todayMonth.'&FROM='.$todayDay.$times[$itime].'&TO='.$todayDay.$times[$itime].'&STNM='.$siteNum[$isite];
	print "urlStr = $urlStr\n";
	$command = "lwp-request '".$urlStr."' > ".$outFile_html;
	system("$command");
	#print "   Done getting todays html file\n";
	$filesize = -s $outFile_html;
	if ($filesize <= 3000) {
	    print "file too small - go to next time\n";
	    system("/bin/rm $outFile_html");
	}
	else {
	    print "file okay - create skewt\n";
	    #Convert text data to skewt
	    $command = "/home/disk/bob/impacts/bin/removeHtmlTags.csh ".$outFile_html." ".$outFile_html.".txt";
	    system("$command");
	    $command = "/usr/bin/python /home/disk/bob/impacts/bin/removeLinesWithMissingData.py ".$outFile_html.".txt ".$outFile_html.".new";
	    system("$command");
	    $command = "/usr/bin/python /home/disk/bob/impacts/bin/skewplot.py --file ".$outFile_html.".new --outpath /tmp --format UWYO";
	    #print "command = $command\n";
	    system("$command");

	    print "file okay - create T vs Tw plot\n";
	    #Convert text data to T vs Tw plot
	    $command = "/usr/bin/python /home/disk/bob/impacts/bin/vertical_TvsTw_sean_rev_v2.py ".$outFile_html." ".$outFile_wetbulb." ".$max_ht;
	    #print "command = $command\n";
	    system($command);
	    
	    $command = "/bin/rm ".$outFile_html.".txt"." ".$outFile_html.".new";
	    system("$command");
	    $command = "/bin/mv /tmp/upperair.NWS_".$siteID{$siteNum[$isite]}."_sonde.".$today.$times[$itime]."00.skewT.png ".$outFile_skewt;	
	    #print "command = $command\n";
	    system("$command");
	    #print "   Done making todays skewt file\n";
	}
    }
}

