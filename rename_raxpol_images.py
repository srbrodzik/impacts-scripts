#!/usr/bin/python3

import os
import shutil

indir = '/home/disk/bob/impacts/radar/raxpol/20230125'
catPrefix = 'radar.RaXPOL'
catProds = {'D':'zdr',
            'P':'phidp',
            'R':'rhohv',
            'S':'6_panel',
            'V':'vel',
            'W':'sw',
            'Z':'refl'}

for file in os.listdir(indir):
    if file.startswith('RAXPOL') and file.endswith('png'):
        print('file = {}'.format(file))
        (base,ext) = os.path.splitext(file)
        (radar,date,time,angle,field) = base.split('-')
        if angle.startswith('E'):
            catSuffix = 'ppi_'+catProds[field]
        elif angle.startswith('A'):
            catSuffix = 'rhi_'+catProds[field]
        else:
            print('Angle {} not ppi or rhi'.format(angle))
            continue
        catName = catPrefix+'.'+date+time[:-2]+'.'+catSuffix+ext
        print('catName = {}\n'.format(catName))
        shutil.move(indir+'/'+file,
                    indir+'/'+catName)
        
        
