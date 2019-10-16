#!/usr/bin/perl

$DIFAX_MIN_PATH = "/home/disk/data/images/difax/difax_min";

$ARCHIVE_PATH = "/home/disk/funnel/impacts/archive/ops/extrema";

$today = `date "+%Y%m%d"`;
chop $today;
$todayDir = $ARCHIVE_PATH."/".$today;
unless (-e $todayDir) {
    mkdir $todayDir;
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

exit(0);
