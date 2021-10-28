#!/usr/bin/perl

$DIFAX_PRECIP_PATH = "/home/disk/archive/images/difax/difax_precip24";
#$DIFAX_PRECIP_PATH = "/home/disk/data/images/difax/difax_precip24";
$DIFAX_SNOW_PATH = "/home/disk/archive/images/difax/difax_snow";
#$DIFAX_SNOW_PATH = "/home/disk/data/images/difax/difax_snow";

$ARCHIVE_PATH = "/home/disk/funnel/impacts/archive/ops/totals";

@dates = ("20190530","20190531");

for $idate (0..$#dates) {

    $today = $dates[$idate];
    $todayDir = $ARCHIVE_PATH."/".$today;
    unless (-e $todayDir) {
	mkdir $todayDir;
    }
    $yrmo = substr($today,0,6);
    print "today = $today\n";
    print "yrmo  = $yrmo\n";

    chdir($DIFAX_PRECIP_PATH."/".$yrmo);
    foreach $file (<$today*00.gif>) {
	($dateTime) = ($file =~ /(.*)\.gif/);
	$date = substr($dateTime,0,8);
	$outFile = $ARCHIVE_PATH."/".$date."/ops.totals.".$dateTime.".precip24.gif";
	unless (-e $outFile) {
	    system("/bin/cp $file $outFile");
	}
    }

    chdir($DIFAX_SNOW_PATH."/".$yrmo);
    foreach $file (<$today*00.gif>) {
	($dateTime) = ($file =~ /(.*)\.gif/);
	$date = substr($dateTime,0,8);
	$outFile = $ARCHIVE_PATH."/".$date."/ops.totals.".$dateTime.".snow.gif";
	unless (-e $outFile) {
	    system("/bin/cp $file $outFile");
	}
    }
}

exit(0);
