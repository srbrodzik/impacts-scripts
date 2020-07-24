#!/bin/bash
rm -f /home/disk/meso-home/jfinlon/impacts/mesonet/csv_output.txt
rm -f /home/disk/meso-home/jfinlon/impacts/mesonet/plot_output.txt
cd /home/disk/meso-home/jfinlon/impacts/python_scripts/mesonet/
python NYS_mesonet_save.py > /home/disk/meso-home/jfinlon/impacts/mesonet/csv_output.txt 2>&1
python NYS_mesonet_plot.py > /home/disk/meso-home/jfinlon/impacts/mesonet/plot_output.txt 2>&1