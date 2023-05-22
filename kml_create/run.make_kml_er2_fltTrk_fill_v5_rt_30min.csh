#!/bin/csh

source /home/disk/meso-home/meso/.cshrc

set fltDate = "`date -u +'%Y%m%d'`"
echo $fltDate

exec /home/disk/bob/impacts/bin/kml_create/make_kml_er2_fltTrk_fill_v5_rt_seg.py $fltDate 30 10
#exec /home/disk/bob/impacts/bin/kml_create/make_kml_er2_fltTrk_fill_v5_rt_seg.py 20230214 30 10
