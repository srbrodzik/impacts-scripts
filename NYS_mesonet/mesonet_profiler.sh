#!/bin/bash
rm -f /home/disk/meso-home/jfinlon/impacts/mesonet/plot_profile_output.txt
cd /home/disk/meso-home/jfinlon/impacts/python_scripts/mesonet/
python NYS_mesonet_profiler.py > /home/disk/meso-home/jfinlon/impacts/mesonet/plot_profiler_output.txt 2>&1