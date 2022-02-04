#!/usr/bin/python

import os
from datetime import datetime
from datetime import timedelta

# User inputs
start_time_str = '202201181900'
#end_time_str   = '202201161900'
end_time_str   = '202201181900'
minutes_between_images = 10

# Get some environment variables
PROJ_DIR = os.getenv('PROJ_DIR')
DATA_DIR = os.getenv('DATA_DIR')

# Set some environment variables
os.environ['CATEGORY'] = 'radar'
os.environ['PLATFORM_NAME'] = 'MRMS_MOSAIC'
os.environ['NUM_MENU_BAR_CELLS'] = '1'
os.environ['RENDER_LTG'] = 'TRUE'
os.environ['CIDD_LABEL'] = 'IMPACTS'
os.environ['CREATING_IMAGES'] = '1'
os.environ['TRANSPARENT_IMAGES'] = '0'
os.environ['IS_TRANS'] = ''
os.environ['PLOT_MAPS'] = '1'
os.environ['FOREGROUND_COLOR'] = 'white'
os.environ['BACKGROUND_COLOR'] = 'grey50'
os.environ['MISSING_DATA_COLOR'] = 'transparent'
os.environ['RANGE_RING_FLAG'] = '0'
os.environ['SHOW_HEIGHT_SEL'] = '0'
os.environ['TIME_INTERVAL'] = '10.0'
os.environ['IMAGE_DIR'] = DATA_DIR+'/raw/images'
os.environ['OUTPUT_GEO_XML'] = '0'
os.environ['MARGIN_WIDTH'] = '0'
os.environ['HORIZ_DEFAULT_HEIGHT'] = '1500'
os.environ['COLOR_SCALE_WIDTH'] = '0'
os.environ['PROJECTION'] = 'MERCATOR'
os.environ['ZOOM_LIMITS_IN_LATLON'] = '1'
os.environ['ORIGIN_LAT'] = '0.0'
os.environ['ORIGIN_LON'] = '-83.0'
os.environ['MINX'] = '-100.0'
os.environ['MAXX'] = '-66.0'
os.environ['MINY'] =  '32.0'
os.environ['MAXY'] =  '48.0'

# Run image every ten minutes starting at 20200101 00:00
# Time string must be in format 'hh:mm MM/DD/YYYY'

start_time_obj = datetime.strptime(start_time_str,'%Y%m%d%H%M')
end_time_obj = datetime.strptime(end_time_str,'%Y%m%d%H%M')
next_time_obj = start_time_obj
while next_time_obj < end_time_obj:
    next_time_str = next_time_obj.strftime("%H:%M %m/%d/%Y")
    print(next_time_str)
    os.environ['CIDD_DEMO_TIME'] = next_time_str
    os.chdir(PROJ_DIR+'/catalog/params')
    command = 'CIDD -p CIDD.catalog.mrms_refl_archive -i mosaic.web.transparent -fn fixed -v 2'
    os.system(command)
    next_time_obj = next_time_obj + timedelta(minutes=minutes_between_images)
