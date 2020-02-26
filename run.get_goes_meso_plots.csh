#!/bin/csh

if ($#argv != 1) then
    echo Usage: $0 [sector: 1 or 2]
    exit 1
endif

source /home/disk/meso-home/meso/.cshrc
exec /home/disk/bob/impacts/bin/get_goes_meso_plots.py $1

