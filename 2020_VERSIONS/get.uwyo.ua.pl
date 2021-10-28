#!/usr/bin/perl

# This data also available here
#   /home/disk/data/pnw/upperair
# One file per day with all sites concatenated

$command = "umask 2";
system($command);

#define system env variables
$ENV{'PATH'} = "/usr/local/bin:/usr/ucb:".$ENV{'PATH'};
$ENV{'PYTHONPATH'} = "/home/disk/bob/impacts/bin:/home/disk/shear2/brodzik/python:/usr/local/lib/python2.7/dist-packages:".$ENV{'PYTHONPATH'};
$ENV{'LD_LIBRARY_PATH'} = "/opt/intel/compilers_and_libraries_2019.1.144/linux/compiler/lib/intel64_lin";

chdir('/home/disk/shear2/brodzik/impacts/Data/test');

#1000hPa obs and analysis
#$urlStr = 'http://weather.uwyo.edu/upperair/maps/2019080912.1000oa.naconf.gif';
# same for 850, 700, 500, 400, 300, 250, 200, 150, 100, 70, 50, 30, 10 hPa

#850hPa obs only
#$urlStr = 'http://weather.uwyo.edu/upperair/maps/2019080912.850o.naconf.gif';
# same for 1000, 700, 500, 400, 300, 250, 200, 150, 100, 70, 50, 30, 10 hPa

#850hPa anal only
#$urlStr = 'http://weather.uwyo.edu/upperair/maps/2019080912.850a.naconf.gif';
# same for 1000, 700, 500, 400, 300, 250, 200, 150, 100, 70, 50, 30, 10 hPa

#precipitable water
#$urlStr = 'http://weather.uwyo.edu/upperair/maps/2019080912.Woa.naconf.gif';

# thickness
#$urlStr = 'http://weather.uwyo.edu/upperair/maps/2019080912.Toa.naconf.gif';

# 500 hPa Vorticity
#$urlStr = 'http://weather.uwyo.edu/upperair/maps/2019080912.Aoa.naconf.gif';

$outFile_gif = 'ua.gif';

$command = "lwp-request '".$urlStr."' > ".$outFile_gif;
system("$command");

