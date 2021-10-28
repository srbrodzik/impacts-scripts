#!/usr/bin/perl

$gdrive_dir = "/home/disk/bob/impacts/gdrive";

chdir($gdrive_dir);
$command = "drive pull SBURadarObservatory";
system($command);

