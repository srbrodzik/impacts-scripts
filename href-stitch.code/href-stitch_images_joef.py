'''
HREF Image Stitcher
Code by Joseph Finlon, Univ. of Washington, 2021

Combines basemap and product layer(s) from the SPC HREF site
(https://www.spc.noaa.gov/exper/href/).

Parameters
----------
run_cycles: 'latest' (for most recent 00, 12 UTC cycle) or comma-separated list
    of datetimes in YYYY-mm-ddTHH format
region_list: comma-separated list of region zooms (e.g., conus, ne, mw)
prod_list: comma-separated list of products
    (e.g., qpf_001h_mean_ptype; see SPC site for more)
root_dir: parent directory path to save raw and stitched images to
    (add trailing '/')

Execution
----------
python href-stitch_images.py latest ne,mw qpf_001h_mean_ptype /home/disk/meso-home/jfinlon/impacts/plots/href/ 

History
----------
11/16/21: Initial code commit. Tested on 1 hr QPF for northeast, midwest regions.
'''

import sys
import os

import urllib.request
from PIL import Image
from datetime import datetime, timedelta, timezone

# Import user arguments
run_cycles = sys.argv[1]
region_list = sys.argv[2].split(',')
prod_list = sys.argv[3].split(',')
root_dir = sys.argv[4]

# Build the datetime array
if run_cycles=='latest':
    curr_time = datetime.now(timezone.utc)
    run_cycle_list = [
        datetime(curr_time.year, curr_time.month, curr_time.day,
                 12 * (curr_time.hour // 12))] # fall back to nearest 00, 12 UTC cycle
else:
    run_cycles = run_cycles.split(',')
    run_cycle_list = [
        datetime.strptime(run_cycles[i], '%Y-%m-%dT%H')
        for i in range(len(run_cycles))]


# Create the necessary directories to save plots to
for run_cycle in run_cycle_list:
    model_dir = root_dir + datetime.strftime(run_cycle, '%Y%m%dT%H') + '/'

    # Create directories if they don't exist
    if os.path.isdir(model_dir) is not True:
        os.mkdir(model_dir)

    for prod in prod_list:
        if os.path.isdir(model_dir + prod + '/') is not True:
            os.mkdir(model_dir + prod + '/')
            os.mkdir(model_dir + prod + '/raw/')
            os.mkdir(model_dir + prod + '/combined/')
            
# Download the region basemap if it doesn't exist in the root dir
for region in region_list:
    localfile = root_dir + 'basemap_' + region + '.png'
    if os.path.exists(localfile) is not True:
        remotefile = (
            'https://www.spc.noaa.gov/exper/href/graphics/blank_maps/'
            + region + '.png')
        print(remotefile)
        try:
            urllib.request.urlretrieve(remotefile, localfile)
        except AttributeError:
            urllib.urlretrieve(remotefile, localfile)
            
# Download the individual component images
for run_cycle in run_cycle_list:
    print(
        'Downloading images for {} run cycle.'.format(
            datetime.strftime(run_cycle, '%H UTC %Y-%m-%d')))
    model_dir = root_dir + datetime.strftime(run_cycle, '%Y%m%dT%H') + '/'
    for region in region_list:
        for prod in prod_list:
            local_path = model_dir + prod + '/raw/'
            for fhr in range(1, 49):
                run_cycle_str = datetime.strftime(run_cycle, '%Y/%m/%d/%H%M/')
                remotefile = (
                    'https://www.spc.noaa.gov/exper/href/graphics/models/href/'
                    + run_cycle_str + 'f0' + str(fhr).zfill(2) + '00/' + prod
                    + '.' + region + '.f0' + str(fhr).zfill(2) + '00.png')
                localfile = local_path + remotefile.split('/')[-1]
                try:
                    urllib.request.urlretrieve(remotefile, localfile)
                except AttributeError:
                    print('{} not found. Skipping.'.format(remotefile))
                    #urllib.request.urlretrieve(remotefile, localfile)

                if prod=='qpf_001h_mean_ptype': # also save 2-m T
                    remotefile = (
                        'https://www.spc.noaa.gov/exper/href/graphics/models/href/'
                        + run_cycle_str + 'f0' + str(fhr).zfill(2)
                        + '00/sfct_32f_mean.' + region + '.f0'
                        + str(fhr).zfill(2) + '00.png')
                    localfile = local_path + remotefile.split('/')[-1]
                    try:
                        urllib.request.urlretrieve(remotefile, localfile)
                    except AttributeError:
                        print('{} not found. Skipping.'.format(remotefile))
                        #urllib.request.urlretrieve(remotefile, localfile)
                        
# Stitch together the component images
for run_cycle in run_cycle_list:
    model_dir = root_dir + datetime.strftime(run_cycle, '%Y%m%dT%H') + '/'
    print(
        'Stitching together images for {} run cycle.'.format(
            datetime.strftime(run_cycle, '%H UTC %Y-%m-%d')))
    for region in region_list:
        prod2_fname = ''
        basemap_fname = root_dir + 'basemap_' + region + '.png'
        if os.path.exists(basemap_fname):
            basemap = Image.open(basemap_fname) # load into memory
        for prod in prod_list:
            local_path = model_dir + prod + '/raw/'
            for fhr in range(1, 49):
                prod1_fname = (
                    model_dir + prod + '/raw/' + prod + '.' + region + '.f0'
                    + str(fhr).zfill(2) + '00.png')
                if prod=='qpf_001h_mean_ptype': # also grab 2-m T filename
                    prod2_fname = (
                        model_dir + prod + '/raw/sfct_32f_mean.' + region
                        + '.f0' + str(fhr).zfill(2) + '00.png')
                if os.path.exists(basemap_fname) and os.path.exists(prod1_fname):
                    # Load the product image into memory
                    prod1 = Image.open(prod1_fname)

                    # Paste the component images
                    new_img = Image.new('RGBA', basemap.size, 'WHITE')
                    new_img.paste(prod1, (0, 0), prod1)
                    new_img.paste(basemap, (0, 0), basemap)

                    if os.path.exists(prod2_fname): # paste second overlay if it exists
                        prod2 = Image.open(prod2_fname)
                        new_img.paste(prod2, (0, 0), prod2)
                        prod2.close()

                    # Save the image and close the opened components
#                     outfile = (
#                         model_dir + prod + '/combined/'
#                         + prod1_fname.split('/')[-1][:-4])
                    outfile = (
                        model_dir + prod + '/combined/' + 'model.HREF_03km_'
                        + region + '.' + datetime.strftime(run_cycle, '%Y%m%d%H%M')
                        + '.' + str(fhr).zfill(3) + '_' + prod)
                    new_img = new_img.convert('RGB')
                    new_img.save(outfile + '.jpg', 'JPEG', quality=70)
                    new_img.close()
                    prod1.close()
        basemap.close()
print('Done. Closing...')