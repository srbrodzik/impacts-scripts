#!/bin/csh

if ($#argv != 1) then
    echo Usage: $0 site
    exit 1
endif

cd /home/disk/funnel/impacts-website/data_archive/nys_ground/sites/$1

foreach dir ( ../../2020???? )
   foreach file ($dir/*.$1.csv)
      ln -s $file
   end
end
