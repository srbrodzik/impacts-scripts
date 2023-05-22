#!/bin/csh

cd /home/disk/bob/impacts/daac/MRMS/ZDR

rsync -av /home/disk/bob/impacts/mdv/mrms/3DZdr/2023* .

foreach dir ( 2023* )
   echo $dir
   cd $dir
   mmv "*_*.mdv.cf.nc" "IMPACTS_mrms_#1_#2_ZDR.nc"
   cd ..
end
