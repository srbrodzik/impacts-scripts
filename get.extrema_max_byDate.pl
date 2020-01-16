#!/usr/bin/perl

$DIFAX_MAX_PATH = "/home/disk/data/archive/images/difax/difax_max";

$ARCHIVE_PATH = "/home/disk/funnel/impacts/archive/ops/extrema";

# Look for map for specified date

$month = '202001';
#print "month = $month\n";
$dayOfInt = '20200108';
#print "dayOfInt = $dayOfInt\n";
$dayDir = $ARCHIVE_PATH."/".$dayOfInt;
unless (-e $dayDir) {
    mkdir $dayDir;
}

chdir($DIFAX_MAX_PATH."/".$month);
#print "changed to $DIFAX_MAX_PATH/$month\n";
foreach $file (<$dayOfInt*0000.gif>) {
  print "file = $file\n";
  ($dateTime) = ($file =~ /(.*)\.gif/);
  $date = substr($dateTime,0,8);
  #print "date = $date\n";
  $outFile = $ARCHIVE_PATH."/".$date."/ops.extrema.".$dateTime.".max_temp.gif";
  print "outFile = $outFile\n";
  unless (-e $outFile) {
    system("/bin/cp $file $outFile");
  }
}

exit(0);
