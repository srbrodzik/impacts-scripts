#!/bin/csh

#source /home/disk/meso-home/meso/.cshrc

set modelInitTime = "`date +'%Y%m%d'`03"
echo $modelInitTime
exec /home/disk/bob/impacts/bin/get_hrrr_1km_plots_rev.py $modelInitTime

