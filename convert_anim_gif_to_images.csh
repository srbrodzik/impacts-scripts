#!/bin/csh

if ($#argv != 2) then
  echo Usage: $0 infile outfile_prefix
  exit 1
endif

convert -coalesce $1 $2_%d.gif
