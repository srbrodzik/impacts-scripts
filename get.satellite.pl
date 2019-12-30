#!/usr/bin/perl

$VIS4KM_PATH = "/home/disk/data/images/sat_east_common";
$IR4KM_PATH = "/home/disk/data/images/sat_east_common";
$WV4KM_PATH = "/home/disk/data/images/sat_east_common";
#$ARCHIVE_PATH = "/home/disk/user_www/brodzik/olympex/archive/ops/goes_west";
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

chdir($VIS4KM_PATH);
foreach $file (<$today*0_vis.gif $tomorrow*0_vis.gif>) {
  ($dateTime) = ($file =~ /(.*)_vis\.gif/);
  $date = substr($dateTime,0,8);
  $outFile = $ARCHIVE_PATH."/".$date."/ops.goes_east.".$dateTime.".vis_4km.gif";
  unless (-e $outFile) {
    system("/bin/cp $file $outFile");
  }
}

chdir($IR4KM_PATH);
foreach $file (<$today*0_ir.gif $tomorrow*0_ir.gif>) {
  ($dateTime) = ($file =~ /(.*)_ir\.gif/);
  $date = substr($dateTime,0,8);
  $outFile = $ARCHIVE_PATH."/".$date."/ops.goes_east.".$dateTime.".ir_4km.gif";
  unless (-e $outFile) {
    system("/bin/cp $file $outFile");
  }
}

chdir($WV4KM_PATH);
foreach $file (<$today*0_wv.gif $tomorrow*0_wv.gif>) {
  ($dateTime) = ($file =~ /(.*)_wv\.gif/);
  $date = substr($dateTime,0,8);
  $outFile = $ARCHIVE_PATH."/".$date."/ops.goes_east.".$dateTime.".wv_4km.gif";
  unless (-e $outFile) {
    system("/bin/cp $file $outFile");
  }
}

exit(0);
