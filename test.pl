#!/usr/bin/perl

# This data also available here
#   /home/disk/data/pnw/upperair
# One file per day with all sites concatenated

use LWP::Simple;

$command = "umask 2";
system($command);

#define system path variable
$ENV{'PATH'} = "/usr/local/bin:/usr/ucb:".$ENV{'PATH'};

$binDir = "/home/disk/bob/impacts/bin";

# Go to data directory
#$ARCHIVE_PATH = "/home/disk/user_www/brodzik/olympex/archive/ops";
$ARCHIVE_PATH = "/home/disk/funnel/impacts/archive/ops";
chdir($ARCHIVE_PATH);

# First, get time and make date subdirs if necessary
$yesterday = `date -u --date='1 day ago' "+%Y%m%d"`;
chop $yesterday;
$yesterdaySkewtDir = $ARCHIVE_PATH."/skewt/".$yesterday;
print "yesterdaySkewtDir = $yesterdaySkewtDir\n";
#unless (-e $yesterdaySkewtDir) {
#    mkdir $yesterdaySkewtDir;
#}
$yesterdayTextDir = $ARCHIVE_PATH."/text_sounding/".$yesterday;
print "yesterdayTextDir = $yesterdayTextDir\n";
#unless (-e $yesterdayTextDir) {
#    mkdir $yesterdayTextDir;
#    $command = "ln -s ".$ARCHIVE_PATH."/text_sounding/index.php ".$yesterdayTextDir;
#    system($command);
#}
$yesterdayYear=substr($yesterday,0,4);
$yesterdayMonth=substr($yesterday,4,2);
$yesterdayDay=substr($yesterday,6,2);

# Define sites of interest
%siteID = (
    '72402', 'WAL',
    );
@siteNum = (keys %siteID);
$numSites = @siteNum;

# Define skewt times (hours)
@times = ('00');
$numTimes = @times;

# Create yesterday's ascii data and download
for ($isite=0;$isite<$numSites;$isite++) {
    for ($itime=0;$itime<$numTimes;$itime++) {

	# skewt file name
	$outFile_skewt = $yesterdaySkewtDir."/ops.skewt.".$yesterday.$times[$itime]."00.".$siteID{$siteNum[$isite]}.".png";
	print "outFile_skewt = $outFile_skewt\n";

	# tables
	$outFile = $yesterdayTextDir."/ops.text_sounding.".$yesterday.$times[$itime]."00.".$siteID{$siteNum[$isite]}.".html";
	print "outFile_html = $outFile\n";
	
	$urlStr = 'http://weather.uwyo.edu/cgi-bin/sounding?region=naconf&TYPE=TEXT%3ALIST&YEAR='.$yesterdayYear.'&MONTH='.$yesterdayMonth.'&FROM='.$yesterdayDay.$times[$itime].'&TO='.$yesterdayDay.$times[$itime].'&STNM='.$siteNum[$isite];
	$command = "lwp-request '".$urlStr."' > ".$outFile;
	system("$command");
	$filesize = -s $outFile;
	if ($filesize < 1000) {
	    system("/bin/rm $outFile");
	}
	
	#Convert text data to skewt
	$command = $binDir.'/removeHtmlTags.csh '.$outFile.' '.$outFile.'.txt';
	print "$command\n";
	system("$command");
	$command = 'python '.$binDir.'/removeLinesWithMissingData.py '.$outFile.'.txt '.$outFile.'.new';
	print "$command\n";
	system("$command");
	$command = 'python '.$binDir.'/skewplot.py --file '.$outFile.'.new --outpath /tmp --format UWYO';
	print "$command\n";
	system("$command");
	$command = '/bin/rm '.$outFile.'.txt'.' '.$outFile.'.new';
	print "$command\n";
	system("$command");
	$command = "/bin/mv /tmp/upperair.NWS_".$siteID{$siteNum[$isite]}."_sonde.".$yesterday.$times[$itime]."00.skewT.png ".$outFile_skewt;
	print "$command\n";
	system("$command");
    }
}
