#!/usr/bin/perl

$VIS_CH02_PATH = "/home/disk/data/images/sat_east_impacts";
$WV_CH08_PATH = "/home/disk/data/images/sat_east_impacts";
$IR_CH13_PATH = "/home/disk/data/images/sat_east_impacts";
$ARCHIVE_PATH = "/home/disk/funnel/impacts/archive/ops/goes_east";

$today = `date "+%Y%m%d"`;
chop $today;
$todayDir = $ARCHIVE_PATH."/".$today;
unless (-e $todayDir) {
    mkdir $todayDir;
}
$tomorrow = `date --date='tomorrow' "+%Y%m%d"`;
chop $tomorrow;
$tomorrowDir = $ARCHIVE_PATH."/".$tomorrow;
unless (-e $tomorrowDir) {
    mkdir $tomorrowDir;
}

chdir($VIS_CH02_PATH);
foreach $file (<$today*0.ch02.gif $tomorrow*0.ch02.gif>) {
  ($dateTime) = ($file =~ /(.*)\.ch02\.gif/);
  $date = substr($dateTime,0,8);
  $outFile = $ARCHIVE_PATH."/".$date."/ops.goes_east.".$dateTime.".vis_ch02.gif";
  unless (-e $outFile) {
    system("/bin/cp $file $outFile");
  }
}

chdir($WV_CH08_PATH);
foreach $file (<$today*0.ch08.gif $tomorrow*0.ch08.gif>) {
  ($dateTime) = ($file =~ /(.*)\.ch08\.gif/);
  $date = substr($dateTime,0,8);
  $outFile = $ARCHIVE_PATH."/".$date."/ops.goes_east.".$dateTime.".wv_ch08.gif";
  unless (-e $outFile) {
    system("/bin/cp $file $outFile");
  }
}

chdir($IR_CH13_PATH);
foreach $file (<$today*0.ch13.gif $tomorrow*0.ch13.gif>) {
  ($dateTime) = ($file =~ /(.*)\.ch13\.gif/);
  $date = substr($dateTime,0,8);
  $outFile = $ARCHIVE_PATH."/".$date."/ops.goes_east.".$dateTime.".ir_ch13.gif";
  unless (-e $outFile) {
    system("/bin/cp $file $outFile");
  }
}

exit(0);
