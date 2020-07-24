#!/usr/bin/python

import os
import shutil

inDir = '/home/disk/funnel/impacts-website/archive/ops/nys_ground_qc'
outDir = '/home/disk/funnel/impacts-website/archive_ncar/surface/NYS_Mesonet'
category_new = 'surface'
platform_new = 'Meteogram'

nys_ground_sites = {'ande':'Andes_NY',
                    'bing':'Binghamton_NY',
                    'brew':'Brewster_NY',
                    'broc':'Brockport_NY',
                    'buff':'Buffalo_NY',
                    'elmi':'Elmira_NY',
                    'fred':'Fredonia_NY',
                    'gfal':'Glens_Falls_NY',
                    'gfld':'Glenfield_NY',
                    'ilak':'Indian_Lake_NY',
                    'malo':'Malone_NY',
                    'nhud':'North_Hudson_NY',
                    'oswe':'Oswego_NY',
                    'pots':'Potsdam_NY',
                    'redf':'Redfield_NY',
                    'sara':'Saranac_NY',
                    'stat':'Staten_Island_NY',
                    'ston':'Stony_Brook_NY',
                    'wate':'Waterloo_NY',
                    'west':'Westmoreland_NY'}

for date in os.listdir(inDir):
    if not os.path.isdir(outDir+'/'+date):
        os.mkdir(outDir+'/'+date)
    for file in os.listdir(inDir+'/'+date):
        if 'nys_ground' in file:
            print(file)
            basename = os.path.splitext(file)[0]
            ext = os.path.splitext(file)[1]
            (category,platform,datetime,site) = basename.split('.')
            file_new = category_new+'.'+platform_new+'.'+datetime+'.NYSM_'+nys_ground_sites[site]+ext
            print(file_new)
            shutil.copy(inDir+'/'+date+'/'+file,outDir+'/'+date+'/'+file_new)
            
