#!/bin/csh

if ($#argv != 1) then
    echo Usage: $0 file
    exit 1
endif

ncap2 -h -s 'vapor_density_qc=ubyte(vapor_density_qc)' $1 $1.new
ncks -x -v vapor_denstiy_qc $1.new $1.new2
ncatted -h -a history,global,d,, $1.new2 $1.new3
ncatted -h -a NCO,global,d,, $1.new3 $1.new4

/bin/mv $1.new4 $1
/bin/rm $1.new $1.new2 $1.new3
