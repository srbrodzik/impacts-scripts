#!/usr/bin/perl

$DIFAX_N_AMER_PATH = "/home/disk/data/images/difax/difax_sfc";
$DIFAX_ATLANTIC_PATH = "/home/disk/data/images/difax/difax_atl";
$DIFAX_GOES_SFC_PATH = "/home/disk/data/images/sat_sfc";
$DIFAX_GOES_500MB_PATH = "/home/disk/data/images/sat_upr";

$ARCHIVE_PATH = "/home/disk/funnel/impacts/archive/ops/sfc_sat";

@dates = ("20190610","20190611");

for $idate (0..$#dates) {

    $today = $dates[$idate];
    $todayDir = $ARCHIVE_PATH."/".$today;
    unless (-e $todayDir) {
	mkdir $todayDir;
    }
    $today_yrmo = substr($today,0,6);
    #print "today = $today\n";
    #print "today_yrmo  = $today_yrmo\n";


    chdir($DIFAX_N_AMER_PATH);
    foreach $file (<$today*00.gif>) {
	($dateTime) = ($file =~ /(.*)\.gif/);
	$date = substr($dateTime,0,8);
	$outFile = $ARCHIVE_PATH."/".$date."/ops.sfc_sat.".$dateTime.".n_amer.gif";
	unless (-e $outFile) {
	    system("/bin/cp $file $outFile");
	}
    }

    chdir($DIFAX_ATLANTIC_PATH);
    foreach $file (<$today*00.gif>) {
	($dateTime) = ($file =~ /(.*)\.gif/);
	$date = substr($dateTime,0,8);
	$outFile = $ARCHIVE_PATH."/".$date."/ops.sfc_sat.".$dateTime.".atlantic.gif";
	unless (-e $outFile) {
	    system("/bin/cp $file $outFile");
	}
    }

    chdir($DIFAX_GOES_SFC_PATH);
    foreach $file (<$today*00.gif>) {
	($dateTime) = ($file =~ /(.*)\.gif/);
	$date = substr($dateTime,0,8);
	$outFile = $ARCHIVE_PATH."/".$date."/ops.sfc_sat.".$dateTime.".goes_sfc.gif";
	unless (-e $outFile) {
	    system("/bin/cp $file $outFile");
	}
    }

    chdir($DIFAX_GOES_500MB_PATH);
    foreach $file (<$today*00_500mb.gif>) {
	($dateTime) = ($file =~ /(.*)\_500mb\.gif/);
	$date = substr($dateTime,0,8);
	$outFile = $ARCHIVE_PATH."/".$date."/ops.sfc_sat.".$dateTime.".goes_500mb.gif";
	unless (-e $outFile) {
	    system("/bin/cp $file $outFile");
	}
    }

}

exit(0);
