#!/usr/bin/python

import os
import sys

# Set time window
#start_time_str = '202201181900'
#end_time_str   = '202201181900'

if len(sys.argv) != 3:
    print('{} {} {}'.format('Useage: ',sys.argv[0],'<start_time_str(YYYYMMDDhhmm)> <end_time_str(YYYYMMDDhhmm)>'))
    sys.exit()
else:
    start_time_str = sys.argv[1]
    end_time_str = sys.argv[2]

print('{} {}'.format('StartTime = ',start_time_str))
print('{} {}'.format('  EndTime = ',end_time_str))
    
command = '/home/snowband/impacts/git/lrose-impacts/projDir/catalog/scripts/create_catMaps_goes_ch01.py '+start_time_str+' '+end_time_str
#command = '/home/disk/bob/impacts/bin/kml_create/create_catMaps_goes_ch01.py '+start_time_str+' '+end_time_str
os.system(command)

command = '/home/snowband/impacts/git/lrose-impacts/projDir/catalog/scripts/create_catMaps_goes_ch13.py '+start_time_str+' '+ end_time_str
#command = '/home/disk/bob/impacts/bin/kml_create/create_catMaps_goes_ch13.py '+start_time_str+' '+ end_time_str
os.system(command)

command = '/home/snowband/impacts/git/lrose-impacts/projDir/catalog/scripts/create_catMaps_mrms_refl_gis.py '+start_time_str+' '+end_time_str
#command = '/home/disk/bob/impacts/bin/kml_create/create_catMaps_mrms_refl_gis.py '+start_time_str+' '+end_time_str
os.system(command)

command = '/home/snowband/impacts/git/lrose-impacts/projDir/catalog/scripts/create_catMaps_mrms_refl_radar.py '+start_time_str+' '+ end_time_str
#command = '/home/disk/bob/impacts/bin/kml_create/create_catMaps_mrms_refl_radar.py '+start_time_str+' '+ end_time_str
os.system(command)

command = '/home/snowband/impacts/git/lrose-impacts/projDir/catalog/scripts/rename_cat_images_and_ftp.py'
#command = '/home/disk/bob/impacts/bin/kml_create/rename_cat_images_and_ftp.py'
os.system(command)
