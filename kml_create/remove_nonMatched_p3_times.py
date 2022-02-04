#!/usr/bin/python3

import os
import shutil

longTrackDir = '/home/disk/funnel/impacts-website/archive_ncar/gis/aircraft/NASA_P3/20220114'
shortTrackDir = '/home/disk/funnel/impacts-website/archive_ncar/gis/aircraft_worms/NASA_P3/20220114'
extraDir = shortTrackDir+'/extra'

if not os.path.isdir(extraDir):
    os.makedirs(extraDir)

for file in os.listdir(shortTrackDir):
    if file.endswith('kml'):
        if not os.path.exists(longTrackDir+'/'+file):
            print(file)
            shutil.move(shortTrackDir+'/'+file,
                        extraDir+'/'+file)
            
