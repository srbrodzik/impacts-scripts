#!/usr/bin/python3

import os
import shutil

longTrackDir = '/home/disk/funnel/impacts-website/archive_ncar/gis/aircraft/NASA_ER2/20220119'
shortTrackDir = '/home/disk/funnel/impacts-website/archive_ncar/gis/aircraft_worms/NASA_ER2/20220119'
extraDir = shortTrackDir+'/extra'

for file in os.listdir(shortTrackDir):
    if file.endswith('kml'):
        if not os.path.exists(longTrackDir+'/'+file):
            print(file)
            shutil.move(shortTrackDir+'/'+file,
                        extraDir+'/'+file)
