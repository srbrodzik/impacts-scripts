#!/bin/csh

source /home/disk/meso-home/meso/.cshrc

#set modelInitTime = "`date +'%Y%m%d'`03"
set modelInitTime = "2023010703"
echo $modelInitTime
/home/disk/bob/impacts/bin/get_hrrr_1km_plots_rev.py $modelInitTime

