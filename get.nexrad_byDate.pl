#!/usr/bin/perl

use File::Copy;

$BASE_PATH = "/home/disk/data/images/nexrad";
$BOX_BREF_PATH = $BASE_PATH."/BOX/BREF1";
$BOX_VEL_PATH = $BASE_PATH."/BOX/VEL1";
$DIX_BREF_PATH = $BASE_PATH."/DIX/BREF1";
$DIX_VEL_PATH = $BASE_PATH."/DIX/VEL1";
$ARCHIVE_PATH = "/home/disk/funnel/impacts/archive/ops/nexrad";

@dates = ("20190605","20190606");

for $idate (0..$#dates) {

    $today = $dates[$idate];
    $todayDir = $ARCHIVE_PATH."/".$today;
    unless (-e $todayDir) {mkdir $todayDir;}

    # Get BOX reflectivity data
    chdir($BOX_BREF_PATH);
    foreach $file (<$today*.gif>)  {
	($dateTime) = ($file =~ /(.*)\.gif/);
	$date = substr($dateTime,0,8);
	$new = $ARCHIVE_PATH."/".$date."/ops.nexrad.".$dateTime.".box_bref.gif";
	unless (-e $new) {copy($file,$new);}
    }

    # Get BOX velocity data
    chdir($BOX_VEL_PATH);
    foreach $file (<$today*.gif>)  {
	($dateTime) = ($file =~ /(.*)\.gif/);
	$date = substr($dateTime,0,8);
	$new = $ARCHIVE_PATH."/".$date."/ops.nexrad.".$dateTime.".box_vel.gif";
	unless (-e $new) {copy($file,$new);}
    }

    # Get DIX reflectivity data
    chdir($DIX_BREF_PATH);
    foreach $file (<$today*.gif>)  {
	($dateTime) = ($file =~ /(.*)\.gif/);
	$date = substr($dateTime,0,8);
	$new = $ARCHIVE_PATH."/".$date."/ops.nexrad.".$dateTime.".dix_bref.gif";
	unless (-e $new) {copy($file,$new);}
    }

    # Get DIX velocity data
    chdir($DIX_VEL_PATH);
    foreach $file (<$today*.gif>)  {
	($dateTime) = ($file =~ /(.*)\.gif/);
	$date = substr($dateTime,0,8);
	$new = $ARCHIVE_PATH."/".$date."/ops.nexrad.".$dateTime.".dix_vel.gif";
	unless (-e $new) {copy($file,$new);}
    }

}

exit(0);
