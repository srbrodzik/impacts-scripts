#!/usr/bin/perl

use LWP::Simple;

#define system path variable
$ENV{'PATH'} = "/usr/local/bin:/usr/ucb:".$ENV{'PATH'};

$BIN_PATH = "/home/disk/bob/impacts/bin";
#$ARCHIVE_PATH = "/home/disk/user_www/brodzik/olympex/archive/ops";
$ARCHIVE_PATH = "/home/disk/funnel/impacts/archive/ops";

# Go to data directory
chdir($ARCHIVE_PATH);

@dates = ("20190625");

for $idate (0..$#dates) {

    print "date = $dates[$idate]\n";

    $today = $dates[$idate];
    $todaySkewtDir = $ARCHIVE_PATH."/skewt/".$today;
    print "todaySkewtDir = $todaySkewtDir\n";
    unless (-e $todaySkewtDir) {
	mkdir $todaySkewtDir;
    }
    $todayTextDir = $ARCHIVE_PATH."/text_sounding/".$today;
    print "todayTextDir = $todayTextDir\n";
    unless (-e $todayTextDir) {
	mkdir $todayTextDir;
    }

    $todayYear=substr($today,0,4);
    $todayMonth=substr($today,4,2);
    $todayDay=substr($today,6,2);

    # Define sites of interest
    %siteID = (
	'72518', 'ALB',
	'72528', 'BUF',
	'74494', 'CHH',
	'74389', 'GYX',
	'72403', 'IAD',
	'72501', 'OKX',
	'72318', 'RNK',
	'72402', 'WAL',
	);
    @siteNum = (keys %siteID);
    $numSites = @siteNum;

    # Define skewt times (hours)
    @times = ('00','06','12','18');
    $numTimes = @times;

    # Create today images and tables and download each one
    for ($isite=0;$isite<$numSites;$isite++) {

	print "site = $siteNum[$isite]\n";
	
	for ($itime=0;$itime<$numTimes;$itime++) {
	    
	    # skewts
	    #print "SKEWTS\n";
	    $skewtFile = $todaySkewtDir."/ops.skewt.".$today.$times[$itime]."00.".$siteID{$siteNum[$isite]}.".png";
	    print "skewtFile = $skewtFile\n";
	    #$urlStr = 'http://weather.uwyo.edu/upperair/images/'.$todayYear.$todayMonth.$todayDay.$times[$itime].'.'.$siteNum[$isite].'.skewt.parc.gif';
	    #if (head($urlStr)) {
		#$command = "lwp-request '".$urlStr."' > ".$skewtFile;
		#print "command = $command\n";
		#system("$command");
	    #}
	    
	    # tables
	    print "TABLES\n";
	    $outFile = $todayTextDir."/ops.text_sounding.".$today.$times[$itime]."00.".$siteID{$siteNum[$isite]}.".html";
	    $urlStr = 'http://weather.uwyo.edu/cgi-bin/sounding?region=naconf&TYPE=TEXT%3ALIST&YEAR='.$todayYear.'&MONTH='.$todayMonth.'&FROM='.$todayDay.$times[$itime].'&TO='.$todayDay.$times[$itime].'&STNM='.$siteNum[$isite];
	    $command = "lwp-request '".$urlStr."' > ".$outFile;
	    print "command = $command\n";
	    system("$command");
	    $filesize = -s $outFile;
	    print "filesize = $filesize\n";
	    if ($filesize < 1000) {
		system("/bin/rm $outFile");
	    }
	    #else {
		# remove html tags
		#$outFile_noTags =  $todayTextDir."/ops.text_sounding.".$today.$times[$itime]."00.".$siteID{$siteNum[$isite]}.".txt";
		#$command = $BIN_PATH.'/removeHtmlTags.csh '.$outFile.' '.$outFile_noTags;
		#print "command = $command\n";
		#system("$command");
		# create skewt
		#$command = 'python '.$BIN_PATH.'/skewplot.py --file '.$outFile_noTags.' --outdir '.$todaySkewtDir.' --format UWYO';
		#print "command = $command\n";
		#system("$command");
		# rename skewt
		#chdir($todaySkewtDir);
		#$command = '/bin/mv '.$todaySkewtDir.'/upperair.NWS_'.$siteID{$siteNum[$isite]}.'_sonde.'.$today.$times[$itime].'00.skewT.png '.$skewtFile;
		#print "command = $command\n";
		#system($command);
		# remove outFile_noTags
		#$command = "/bin/rm ".$outFile_noTags;
		#print "command = $command\n";
		#system($command);
	    #}
	}
    }
}

#skewt
#http://weather.uwyo.edu/cgi-bin/sounding?region=naconf&TYPE=GIF%3ASKEWT&YEAR=2015&MONTH=08&FROM=1500&TO=1500&STNM=72797
#data
#http://weather.uwyo.edu/cgi-bin/sounding?region=naconf&TYPE=TEXT%3ALIST&YEAR=2015&MONTH=08&FROM=1500&TO=1500&STNM=72797
