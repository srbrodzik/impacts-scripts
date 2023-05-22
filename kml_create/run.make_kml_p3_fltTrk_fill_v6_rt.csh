#!/bin/csh

source /home/disk/meso-home/meso/.cshrc

set fltDate = "`date -u +'%Y%m%d'`"
echo $fltDate

exec /home/disk/bob/impacts/bin/kml_create/make_kml_p3_fltTrk_fill_v6_rt.py $fltDate
#exec /home/disk/bob/impacts/bin/kml_create/make_kml_p3_fltTrk_fill_v6_rt.py 20230214
