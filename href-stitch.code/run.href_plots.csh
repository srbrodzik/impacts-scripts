#!/bin/csh

source /home/disk/meso-home/meso/.cshrc
#source /home/disk/shear2/brodzik/.cshrc

/bin/rm /home/disk/bob/impacts/bin/href_output.txt

#exec /home/disk/bob/impacts/bin/href-stitch_images.py latest ne,mw qpf_001h_mean_ptype /home/disk/meso-home/meso/impacts/plots/href/ > href_output.txt 2>&1
exec python3 /home/disk/bob/impacts/bin/href-stitch_images.py latest ne,mw qpf_001h_mean_ptype /home/disk/bob/impacts/model/href_03km_test/ 
