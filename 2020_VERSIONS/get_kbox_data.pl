#!/usr/bin/perl

use File::Copy;

#define pathnames
$RAWPATH = "/home/disk/data/gempak/nexrad/craft/KBOX";
$WORKPATH = "/home/disk/bob/impacts/data.server/raw/kbox/sur";

while(1)  {

    # Get date and time information
    $yesterday = `date -u --date='1 day ago' "+%Y%m%d"`;
    chop $yesterday;
    $yesterdayDir = $WORKPATH."/".$yesterday;
    unless (-e $yesterdayDir) {mkdir $yesterdayDir;}

    $today = `date -u "+%Y%m%d"`;
    chop $today;
    $todayDir = $WORKPATH."/".$today;
    unless (-e $todayDir) {mkdir $todayDir;}

    $last_2hour = `date -u --date='2 hour ago' "+%H"`;
    chop $last_2hour;
    $last_hour = `date -u --date='1 hour ago' "+%H"`;
    chop $last_hour;
    $curr_hour = `date -u "+%H"`;
    chop $curr_hour;

    # Create find command
    if ($curr_hour eq "00") {
	$queryString1 = "KBOX_".$yesterday."_23??";
	$queryString2 = "KBOX_".$today."_00??";
    }
    else {
	$queryString1 = "KBOX_".$today."_".$last_hour."??";
	$queryString2 = "KBOX_".$today."_".$curr_hour."??";
    }
    $findcmd = "/usr/bin/find -type f -follow \\( -iname \"$queryString1\" -or -iname \"$queryString2\" \\) -print";
    print "findcmd = $findcmd\n";

    # Get new kbox level II data
    chdir($RAWPATH);
    open(FIND,"$findcmd |");
    while(<FIND>) {
	chop $_;
	print "top of while loop: $_\n";
	$date = substr($_,5,8);    
	unless (-e $WORKPATH."/".$date."/".$_) {
	    copy($_,$WORKPATH);
	}
    }

    # sleep for 20 minutes . . . .
    print "sleeping for 20 minutes . . .\n";
    system("sleep 1200");

} # end of while loop
