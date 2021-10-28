#!/usr/bin/perl

$command = "umask 2";
system($command);

#define system env variables
$ENV{'PATH'} = "/usr/local/bin:/usr/ucb:".$ENV{'PATH'};
$ENV{'PYTHONPATH'} = "/home/disk/bob/impacts/bin:/home/disk/shear2/brodzik/python:/usr/lib/python2.7/dist-packages:".$ENV{'PYTHONPATH'};
$ENV{'LD_LIBRARY_PATH'} = "/opt/intel/compilers_and_libraries_2019.1.144/linux/compiler/lib/intel64_lin";

$binDir = "/home/disk/bob/impacts/bin";

$command = "python ".$binDir."/get_npol_images.py";
system($command);

