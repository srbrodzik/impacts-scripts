#!/usr/bin/perl

$DIFAX_MAX_PATH = "/home/disk/data/images/difax/difax_max";

$ARCHIVE_PATH = "/home/disk/funnel/impacts/archive/ops/extrema";

$tomorrow = `date --date='tomorrow' "+%Y%m%d"`;
chop $tomorrow;
$tomorrowDir = $ARCHIVE_PATH."/".$tomorrow;
unless (-e $tomorrowDir) {
    mkdir $tomorrowDir;
}

chdir($DIFAX_MAX_PATH);
foreach $file (<$tomorrow*00.gif>) {
  ($dateTime) = ($file =~ /(.*)\.gif/);
  $date = substr($dateTime,0,8);
  $outFile = $ARCHIVE_PATH."/".$date."/ops.extrema.".$dateTime.".max_temp.gif";
  unless (-e $outFile) {
    system("/bin/cp $file $outFile");
  }
}

exit(0);
