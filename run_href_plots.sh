#!/bin/bash
cd /home/disk/meso-home/jfinlon/impacts/python_scripts/forecasting
rm -f href_output.txt
python href-stitch_images.py latest ne,mw qpf_001h_mean_ptype /home/disk/meso-home/jfinlon/impacts/plots/href/ > href_output.txt 2>&1
