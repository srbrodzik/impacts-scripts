import os
import shutil

# Filenames
# YYYY-MM-DD-hh:mm-lidar_cnr.PROF_XXXX.png
# YYYY-MM-DD-hh:mm-lidar_horizontal_speed.PROF_XXXX.png
# YYYY-MM-DD-hh:mm-lidar_ts.PROF_XXXX.png
# YYYY-MM-DD-hh:mm-lidar_vertical_speed.PROF_XXXX.png
# YYYY-MM-DD-hh:mm-radiometer_integrations.PROF_XXXX.png
# YYYY-MM-DD-hh:mm-radiometer_ts.PROF_XXXX.png

in_dir = '/home/disk/funnel/impacts/raw/png'
catalog_root_dir = '/home/disk/funnel/impacts/archive/ops'

prods = {'lidar_cnr':'lidar_cnr','lidar_horizontal_speed':'lidar_horiz_ws','lidar_ts':'lidar_ts','lidar_vertical_speed':'lidar_vert_ws','radiometer_integrations':'mwr_integrations','radiometer_ts':'mwr_ts'}

for in_file in os.listdir(in_dir):
    if in_file.endswith('.png'):

        #print 'file = ',in_file

        (year,month,day,time,rest) = in_file.split('-')
        (hour,minute) = time.split(':')
        (p,site,ext) = rest.split('.')
        product = prods.get(p)
        site = site.lower()

        out_file = 'ops.'+site+'.'+year+month+day+hour+minute+'.'+product+'.'+ext
        out_dir = catalog_root_dir+'/'+site+'/'+year+month+day
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)
        shutil.move(in_dir+'/'+in_file,out_dir+'/'+out_file)
    
