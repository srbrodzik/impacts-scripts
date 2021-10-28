#!/usr/bin/perl

$DIFAX_MIN_PATH = "/home/disk/data/archive/images/difax/difax_min";

$ARCHIVE_PATH = "/home/disk/funnel/impacts/archive/ops/extrema";

# Look for yesterday's map

$month = `date --date='yesterday' "+%Y%m"`;
chop $month;
#print "month = $month\n";
$yesterday = `date --date='yesterday' "+%Y%m%d"`;
chop $yesterday;
#print "yesterday = $yesterday\n";
$yesterdayDir = $ARCHIVE_PATH."/".$yesterday;
unless (-e $yesterdayDir) {
    mkdir $yesterdayDir;
}

# note for 2021: new maps are in $DIFAX_MIN_PATH."/".$year.$month
# e.g. /home/disk/data/archive/images/difax/difax_min/202008
chdir($DIFAX_MIN_PATH."/".$month);
#print "changed to $DIFAX_MIN_PATH/$month\n";
foreach $file (<$yesterday*1200.gif>) {
  print "file = $file\n";
  ($dateTime) = ($file =~ /(.*)\.gif/);
  $date = substr($dateTime,0,8);
  #print "date = $date\n";
  $outFile = $ARCHIVE_PATH."/".$date."/ops.extrema.".$dateTime.".min_temp.gif";
  print "outFile = $outFile\n";
  unless (-e $outFile) {
    system("/bin/cp $file $outFile");
  }
}

# Look for today's map

$month = `date "+%Y%m"`;
chop $month;
#print "month = $month\n";
$today = `date "+%Y%m%d"`;
chop $today;
#print "today = $today\n";
$todayDir = $ARCHIVE_PATH."/".$today;
unless (-e $todayDir) {
    mkdir $todayDir;
}

chdir($DIFAX_MIN_PATH."/".$month);
#print "changed to $DIFAX_MIN_PATH/$month\n";
foreach $file (<$today*1200.gif>) {
  print "file = $file\n";
  ($dateTime) = ($file =~ /(.*)\.gif/);
  $date = substr($dateTime,0,8);
  #print "date = $date\n";
  $outFile = $ARCHIVE_PATH."/".$date."/ops.extrema.".$dateTime.".min_temp.gif";
  print "outFile = $outFile\n";
  unless (-e $outFile) {
    system("/bin/cp $file $outFile");
  }
}

exit(0);
