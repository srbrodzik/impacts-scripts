#!/bin/csh

if ($#argv != 1) then
    echo Usage: $0 site
    exit 1
endif

cd /home/disk/funnel/impacts-website/data_archive/nys_ground/2020/csv_QC/csv_by_site/$1

foreach dir ( ../../2020???? )
   foreach file ($dir/*.$1.csv)
      #ln -s $file
      /bin/cp $file .
   end
end
