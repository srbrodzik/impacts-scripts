#!/bin/csh

source /home/disk/meso-home/meso/.cshrc

set fltDate = "`date -u +'%Y%m%d'`"
echo $fltDate

exec /home/disk/bob/impacts/bin/kml_create/make_kml_p3_fltTrk_fill_v5_rt_seg.py $fltDate 60
#exec /home/disk/bob/impacts/bin/kml_create/make_kml_p3_fltTrk_fill_v5_rt_seg.py 20230214 60
