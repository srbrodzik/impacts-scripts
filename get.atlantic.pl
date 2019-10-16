#!/usr/bin/perl

# define system env variables
$ENV{'PATH'} = "/usr/local/bin:/usr/ucb:".$ENV{'PATH'};
$ENV{'PYTHONPATH'} = "/home/disk/bob/impacts/bin:/home/disk/shear2/brodzik/python:/usr/local/lib/python2.7/dist-packages:".$
ENV{'PYTHONPATH'};
$ENV{'LD_LIBRARY_PATH'} = "/opt/intel/compilers_and_libraries_2019.1.144/linux/compiler/lib/intel64_lin";

#$outdir = "/home/disk/bob/impacts/bin/atlantic_test";
$outdir = "/home/disk/funnel/impacts/archive/ops/sfc_anal";
$url = "https://ocean.weather.gov/UA/East_coast.gif";

# get date and time info
$date = `date -u "+%Y%m%d"`;
chop($date);
$hour = `date -u "+%H"`;
chop($hour);

# create outdir subdir if required
unless (-e $outdir.'/'.$date) {
    mkdir $outdir.'/'.$date;
}

# determine fileDateTime
if ($hour == '04') {
    $fileDateTime = $date.'0000';
}
elsif ($hour == '10') {
    $fileDateTime = $date.'0600';
}
elsif ($hour == '16') {
    $fileDateTime = $date.'1200';
}
elsif ($hour == '22') {
    $fileDateTime = $date.'1800';
}
else {
    print 'hour = $hour: Not one of 4 hours of interest';
    exit;
}

# download file and rename it
chdir($outdir.'/'.$date);
$cmd = 'wget '.$url;
system($cmd);
#$cmd = 'mv East_coast.gif '.$dtg.'_East_coast.gif';
$cmd = 'mv East_coast.gif '.$outdir.'/'.$date.'/ops.sfc_anal.'.$fileDateTime.'.atlantic.gif';
system($cmd);
