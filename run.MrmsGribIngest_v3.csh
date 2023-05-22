#!/bin/csh

#source /home/disk/meso-home/meso/.cshrc
source /home/disk/meso-home/meso/.cshrc
setenv MDV_WRITE_FORMAT FORMAT_NCF 
exec /home/disk/bob/impacts/bin/run.MrmsGribIngest_v3.py
