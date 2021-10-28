#!/bin/csh

if ($#argv != 2) then
    echo Usage: $0 inputFile outputFile
    exit 1
endif

awk 'NR == 1 || NR % 3 == 0' $1 > $2

