#!/usr/bin/perl

$DIFAX_MAX_PATH = "/home/disk/data/images/difax/difax_max";
$DIFAX_MIN_PATH = "/home/disk/data/images/difax/difax_min";

$ARCHIVE_PATH = "/home/disk/funnel/impacts/archive/ops/extrema";

@dates = ("20190530","20190531");

for $idate (0..$#dates) {

    $today = $dates[$idate];
    $todayDir = $ARCHIVE_PATH."/".$today;
    unless (-e $todayDir) {
	mkdir $todayDir;
    }

    chdir($DIFAX_MAX_PATH);
    foreach $file (<$today*00.gif>) {
	($dateTime) = ($file =~ /(.*)\.gif/);
	$date = substr($dateTime,0,8);
	$outFile = $ARCHIVE_PATH."/".$date."/ops.extrema.".$dateTime.".max_temp.gif";
	unless (-e $outFile) {
	    system("/bin/cp $file $outFile");
	}
    }
    
    chdir($DIFAX_MIN_PATH);
    foreach $file (<$today*00.gif>) {
	($dateTime) = ($file =~ /(.*)\.gif/);
	$date = substr($dateTime,0,8);
	$outFile = $ARCHIVE_PATH."/".$date."/ops.extrema.".$dateTime.".min_temp.gif";
	unless (-e $outFile) {
	    system("/bin/cp $file $outFile");
	}
    }
}

exit(0);
