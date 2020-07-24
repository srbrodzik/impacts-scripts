#!/bin/bash
cd /home/disk/meso-home/jfinlon/impacts/briefings/
rm -f briefing_output.txt
python briefing.py namelist_morning.txt > briefing_output.txt 2>&1
