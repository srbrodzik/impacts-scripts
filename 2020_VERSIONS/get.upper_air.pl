#!/usr/bin/perl

$DIFAX_850_PATH = "/home/disk/data/images/difax/difax_850";
$DIFAX_700_PATH = "/home/disk/data/images/difax/difax_700";
$DIFAX_500_PATH = "/home/disk/data/images/difax/difax_500";
$DIFAX_300_PATH = "/home/disk/data/images/difax/difax_300";
$DIFAX_200_PATH = "/home/disk/data/images/difax/difax_200";

$ARCHIVE_PATH = "/home/disk/funnel/impacts/archive/ops/upper_air";

#----------------------
# get today's 1200 data
#----------------------
$today = `date "+%Y%m%d"`;
chop $today;
$todayDir = $ARCHIVE_PATH."/".$today;
unless (-e $todayDir) {
    mkdir $todayDir;
}

chdir($DIFAX_850_PATH);
foreach $file (<$today*200.gif>) {
  ($dateTime) = ($file =~ /(.*)\.gif/);
  $date = substr($dateTime,0,8);
  $outFile = $ARCHIVE_PATH."/".$date."/ops.upper_air.".$dateTime.".850mb.gif";
  unless (-e $outFile) {
    system("/bin/cp $file $outFile");
  }
}

chdir($DIFAX_700_PATH);
foreach $file (<$today*200.gif>) {
  ($dateTime) = ($file =~ /(.*)\.gif/);
  $date = substr($dateTime,0,8);
  $outFile = $ARCHIVE_PATH."/".$date."/ops.upper_air.".$dateTime.".700mb.gif";
  unless (-e $outFile) {
    system("/bin/cp $file $outFile");
  }
}

chdir($DIFAX_500_PATH);
foreach $file (<$today*200.gif>) {
  ($dateTime) = ($file =~ /(.*)\.gif/);
  $date = substr($dateTime,0,8);
  $outFile = $ARCHIVE_PATH."/".$date."/ops.upper_air.".$dateTime.".500mb.gif";
  unless (-e $outFile) {
    system("/bin/cp $file $outFile");
  }
}

#chdir($DIFAX_300_PATH);
#foreach $file (<$today*200.gif>) {
#  ($dateTime) = ($file =~ /(.*)\.gif/);
#  $date = substr($dateTime,0,8);
#  $outFile = $ARCHIVE_PATH."/".$date."/ops.upper_air.".$dateTime.".300mb.gif";
#  unless (-e $outFile) {
#    system("/bin/cp $file $outFile");
#  }
#}

chdir($DIFAX_200_PATH);
foreach $file (<$today*200.gif>) {
  ($dateTime) = ($file =~ /(.*)\.gif/);
  $date = substr($dateTime,0,8);
  $outFile = $ARCHIVE_PATH."/".$date."/ops.upper_air.".$dateTime.".200mb.gif";
  unless (-e $outFile) {
    system("/bin/cp $file $outFile");
  }
}

#-------------------------
# get tomorrow's 0000 data
#-------------------------
$tomorrow = `date --date='tomorrow' "+%Y%m%d"`;
chop $tomorrow;
$tomorrowDir = $ARCHIVE_PATH."/".$tomorrow;
unless (-e $tomorrowDir) {
    mkdir $tomorrowDir;
}

chdir($DIFAX_850_PATH);
foreach $file (<$tomorrow*000.gif>) {
  ($dateTime) = ($file =~ /(.*)\.gif/);
  $date = substr($dateTime,0,8);
  $outFile = $ARCHIVE_PATH."/".$date."/ops.upper_air.".$dateTime.".850mb.gif";
  unless (-e $outFile) {
    system("/bin/cp $file $outFile");
  }
}

chdir($DIFAX_700_PATH);
foreach $file (<$tomorrow*000.gif>) {
  ($dateTime) = ($file =~ /(.*)\.gif/);
  $date = substr($dateTime,0,8);
  $outFile = $ARCHIVE_PATH."/".$date."/ops.upper_air.".$dateTime.".700mb.gif";
  unless (-e $outFile) {
    system("/bin/cp $file $outFile");
  }
}

chdir($DIFAX_500_PATH);
foreach $file (<$tomorrow*000.gif>) {
  ($dateTime) = ($file =~ /(.*)\.gif/);
  $date = substr($dateTime,0,8);
  $outFile = $ARCHIVE_PATH."/".$date."/ops.upper_air.".$dateTime.".500mb.gif";
  unless (-e $outFile) {
    system("/bin/cp $file $outFile");
  }
}

chdir($DIFAX_300_PATH);
foreach $file (<$tomorrow*000.gif>) {
  ($dateTime) = ($file =~ /(.*)\.gif/);
  $date = substr($dateTime,0,8);
  $outFile = $ARCHIVE_PATH."/".$date."/ops.upper_air.".$dateTime.".300mb.gif";
  unless (-e $outFile) {
    system("/bin/cp $file $outFile");
  }
}

chdir($DIFAX_200_PATH);
foreach $file (<$tomorrow*000.gif>) {
  ($dateTime) = ($file =~ /(.*)\.gif/);
  $date = substr($dateTime,0,8);
  $outFile = $ARCHIVE_PATH."/".$date."/ops.upper_air.".$dateTime.".200mb.gif";
  unless (-e $outFile) {
    system("/bin/cp $file $outFile");
  }
}

exit(0);
