#!/usr/bin/perl

$DIFAX_N_AMER_PATH = "/home/disk/data/images/difax/difax_sfc";
$DIFAX_ATLANTIC_PATH = "/home/disk/data/images/difax/difax_atl";
$DIFAX_GOES_SFC_PATH = "/home/disk/data/images/sat_sfc";
$DIFAX_GOES_500MB_PATH = "/home/disk/data/images/sat_upr";

$ARCHIVE_PATH = "/home/disk/funnel/impacts/archive/ops/sfc_sat";

$today = `date "+%Y%m%d"`;
chop $today;
$todayDir = $ARCHIVE_PATH."/".$today;
unless (-e $todayDir) {
    mkdir $todayDir;
}
$today_yrmo = substr($today,0,6);

$tomorrow = `date --date='1 day ago' -u "+%Y%m%d"`;
chop $tomorrow;
$tomorrowDir = $ARCHIVE_PATH."/".$tomorrow;
unless (-e $tomorrowDir) {
    mkdir $tomorrowDir;
}
$tomorrow_yrmo = substr($tomorrow,0,6);

chdir($DIFAX_N_AMER_PATH);
foreach $file (<$today*00.gif>) {
  ($dateTime) = ($file =~ /(.*)\.gif/);
  $date = substr($dateTime,0,8);
  $outFile = $ARCHIVE_PATH."/".$date."/ops.sfc_sat.".$dateTime.".n_amer.gif";
  unless (-e $outFile) {
    system("/bin/cp $file $outFile");
  }
}
foreach $file (<$tomorrow*00.gif>) {
  ($dateTime) = ($file =~ /(.*)\.gif/);
  $date = substr($dateTime,0,8);
  $outFile = $ARCHIVE_PATH."/".$date."/ops.sfc_sat.".$dateTime.".n_amer.gif";
  unless (-e $outFile) {
    system("/bin/cp $file $outFile");
  }
}

#chdir($DIFAX_ATLANTIC_PATH);
#foreach $file (<$today*00.gif>) {
#  ($dateTime) = ($file =~ /(.*)\.gif/);
#  $date = substr($dateTime,0,8);
#  $outFile = $ARCHIVE_PATH."/".$date."/ops.sfc_sat.".$dateTime.".atlantic.gif";
#  unless (-e $outFile) {
#    system("/bin/cp $file $outFile");
#  }
#}
#foreach $file (<$tomorrow*00.gif>) {
#  ($dateTime) = ($file =~ /(.*)\.gif/);
#  $date = substr($dateTime,0,8);
#  $outFile = $ARCHIVE_PATH."/".$date."/ops.sfc_sat.".$dateTime.".atlantic.gif";
#  unless (-e $outFile) {
#    system("/bin/cp $file $outFile");
#  }
#}

chdir($DIFAX_GOES_SFC_PATH);
foreach $file (<$today*00.gif>) {
  ($dateTime) = ($file =~ /(.*)\.gif/);
  $date = substr($dateTime,0,8);
  $outFile = $ARCHIVE_PATH."/".$date."/ops.sfc_sat.".$dateTime.".goes_sfc.gif";
  unless (-e $outFile) {
    system("/bin/cp $file $outFile");
  }
}
foreach $file (<$tomorrow*00.gif>) {
  ($dateTime) = ($file =~ /(.*)\.gif/);
  $date = substr($dateTime,0,8);
  $outFile = $ARCHIVE_PATH."/".$date."/ops.sfc_sat.".$dateTime.".goes_sfc.gif";
  unless (-e $outFile) {
    system("/bin/cp $file $outFile");
  }
}

#chdir($DIFAX_GOES_500MB_PATH);
#foreach $file (<$today*00.gif>) {
#  ($dateTime) = ($file =~ /(.*)\.gif/);
#  $date = substr($dateTime,0,8);
#  $outFile = $ARCHIVE_PATH."/".$date."/ops.sfc_sat.".$dateTime.".goes_500mb.gif";
#  unless (-e $outFile) {
#    system("/bin/cp $file $outFile");
#  }
#}
#foreach $file (<$tomorrow*00.gif>) {
#  ($dateTime) = ($file =~ /(.*)\.gif/);
#  $date = substr($dateTime,0,8);
#  $outFile = $ARCHIVE_PATH."/".$date."/ops.sfc_sat.".$dateTime.".goes_500mb.gif";
#  unless (-e $outFile) {
#    system("/bin/cp $file $outFile");
#  }
#}

exit(0);
