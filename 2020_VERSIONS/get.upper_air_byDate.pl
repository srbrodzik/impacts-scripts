#!/usr/bin/perl

$DIFAX_850_PATH = "/home/disk/archive/images/difax/difax_850";
$DIFAX_700_PATH = "/home/disk/archive/images/difax/difax_700";
$DIFAX_500_PATH = "/home/disk/archive/images/difax/difax_500";
$DIFAX_300_PATH = "/home/disk/archive/images/difax/difax_300";
$DIFAX_200_PATH = "/home/disk/archive/images/difax/difax_200";

$ARCHIVE_PATH = "/home/disk/funnel/impacts/archive/ops/upper_air";

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

    chdir($DIFAX_850_PATH."/".$yrmo);
    foreach $file (<$today*00.gif>) {
	($dateTime) = ($file =~ /(.*)\.gif/);
	$date = substr($dateTime,0,8);
	$outFile = $ARCHIVE_PATH."/".$date."/ops.upper_air.".$dateTime.".850mb.gif";
	unless (-e $outFile) {
	    system("/bin/cp $file $outFile");
	}
    }

    chdir($DIFAX_700_PATH."/".$yrmo);
    foreach $file (<$today*00.gif>) {
	($dateTime) = ($file =~ /(.*)\.gif/);
	$date = substr($dateTime,0,8);
	$outFile = $ARCHIVE_PATH."/".$date."/ops.upper_air.".$dateTime.".700mb.gif";
	unless (-e $outFile) {
	    system("/bin/cp $file $outFile");
	}
    }

    chdir($DIFAX_500_PATH."/".$yrmo);
    foreach $file (<$today*00.gif>) {
	($dateTime) = ($file =~ /(.*)\.gif/);
	$date = substr($dateTime,0,8);
	$outFile = $ARCHIVE_PATH."/".$date."/ops.upper_air.".$dateTime.".500mb.gif";
	unless (-e $outFile) {
	    system("/bin/cp $file $outFile");
	}
    }

    chdir($DIFAX_300_PATH."/".$yrmo);
    foreach $file (<$today*00.gif>) {
	($dateTime) = ($file =~ /(.*)\.gif/);
	$date = substr($dateTime,0,8);
	$outFile = $ARCHIVE_PATH."/".$date."/ops.upper_air.".$dateTime.".300mb.gif";
	unless (-e $outFile) {
	    system("/bin/cp $file $outFile");
	}
    }

    chdir($DIFAX_200_PATH."/".$yrmo);
    foreach $file (<$today*00.gif>) {
	($dateTime) = ($file =~ /(.*)\.gif/);
	$date = substr($dateTime,0,8);
	$outFile = $ARCHIVE_PATH."/".$date."/ops.upper_air.".$dateTime.".200mb.gif";
	unless (-e $outFile) {
	    system("/bin/cp $file $outFile");
	}
    }
}

exit(0);
