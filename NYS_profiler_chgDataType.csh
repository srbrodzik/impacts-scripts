#!/bin/csh

if ($#argv != 1) then
    echo Usage: $0 file
    exit 1
endif

ncap2 -h -s 'temperature_qc=ubyte(temperature_qc);relative_humidity_qc=ubyte(relative_humidity_qc);vapor_density_qc=ubyte(vapor_density_qc);liquid_qc=ubyte(liquid_qc);integrated_qc=ubyte(integrated_qc);surface_qc=ubyte(surface_qc)' $1 $1.new

/bin/mv $1.new $1
