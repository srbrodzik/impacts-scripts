#!/usr/bin/perl

use File::Copy;

$BASE_PATH = "/home/disk/data/images/newnexrad";
$BOX_REF_PATH = $BASE_PATH."/BOX/N0R";
$BOX_VEL_PATH = $BASE_PATH."/BOX/N0V";
$DIX_REF_PATH = $BASE_PATH."/DIX/N0R";
$DIX_VEL_PATH = $BASE_PATH."/DIX/N0V";
$ARCHIVE_PATH = "/home/disk/funnel/impacts/archive/ops/nexrad";

# Get date and time information
$yesterday = `date -u --date='1 day ago' "+%Y%m%d"`;
chop $yesterday;
$yesterdayDir = $ARCHIVE_PATH."/".$yesterday;
unless (-e $yesterdayDir) {mkdir $yesterdayDir;}

$today = `date -u "+%Y%m%d"`;
chop $today;
$todayDir = $ARCHIVE_PATH."/".$today;
unless (-e $todayDir) {mkdir $todayDir;}

$last_hour = `date -u --date='1 hour ago' "+%H"`;
chop $last_hour;
$curr_hour = `date -u "+%H"`;
chop $curr_hour;

# Create find command
if ($curr_hour eq "00") {
    $queryString1 = $yesterday."23??.gif";
    $queryString2 = $today."00??.gif";
}
else {
    $queryString1 = $today.$last_hour."??.gif";
    $queryString2 = $today.$curr_hour."??.gif";
}
$findcmd = "/usr/bin/find -type f -follow \\( -iname \"$queryString1\" -or -iname \"$queryString2\" \\) -print";

# Get BOX reflectivity data
chdir($BOX_REF_PATH);
open(FIND,"$findcmd |");
while(<FIND>) {
    s/\s*$//;
    s/\.\///;
    ($dateTime) = ($_ =~ /(.*)\.gif/);
    $date = substr($dateTime,0,8);
    $new = $ARCHIVE_PATH."/".$date."/ops.nexrad.".$dateTime.".box_bref.gif";
    unless (-e $new) {copy($_,$new);}
}

# Get BOX velocity data
chdir($BOX_VEL_PATH);
open(FIND,"$findcmd |");
while(<FIND>) {
    s/\s*$//;
    s/\.\///;
    ($dateTime) = ($_ =~ /(.*)\.gif/);
    $date = substr($dateTime,0,8);
    $new = $ARCHIVE_PATH."/".$date."/ops.nexrad.".$dateTime.".box_vel.gif";
    unless (-e $new) {copy($_,$new);}
}

# Get DIX reflectivity data
chdir($DIX_REF_PATH);
open(FIND,"$findcmd |");
while(<FIND>) {
    s/\s*$//;
    s/\.\///;
    ($dateTime) = ($_ =~ /(.*)\.gif/);
    $date = substr($dateTime,0,8);
    $new = $ARCHIVE_PATH."/".$date."/ops.nexrad.".$dateTime.".dix_bref.gif";
    unless (-e $new) {copy($_,$new);}
}

# Get DIX velocity data
chdir($DIX_VEL_PATH);
open(FIND,"$findcmd |");
while(<FIND>) {
    s/\s*$//;
    s/\.\///;
    ($dateTime) = ($_ =~ /(.*)\.gif/);
    $date = substr($dateTime,0,8);
    $new = $ARCHIVE_PATH."/".$date."/ops.nexrad.".$dateTime.".dix_vel.gif";
    unless (-e $new) {copy($_,$new);}
}

exit(0);
