#!/usr/bin/perl

$command = "umask 2";
system($command);

#define system env variables
$ENV{'PATH'} = "/usr/local/bin:/usr/ucb:".$ENV{'PATH'};
$ENV{'PYTHONPATH'} = "/home/disk/bob/impacts/bin:/home/disk/shear2/brodzik/python:/usr/lib/python3/dist-packages:".$ENV{'PYTHONPATH'};
$ENV{'LD_LIBRARY_PATH'} = "/opt/intel/compilers_and_libraries_2019.1.144/linux/compiler/lib/intel64_lin";

$binDir = "/home/disk/bob/impacts/bin";

$command = "python3 ".$binDir."/ASOS_save_and_plot_withPrecipAPI_v1.py";
system($command);

