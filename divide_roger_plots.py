#!/usr/bin/python

import os
import shutil

indir = '/home/disk/funnel/impacts-website/archive/research/stonybrook'
outdir = indir

dict = {'cropped_0':'time_ht',
        'cropped_1':'spectrum_refl'}

for date in os.listdir(indir):
    if date.startswith('20200'):
        os.chdir(indir+'/'+date)
        for file in os.listdir(indir+'/'+date):
            if file.endswith('roger.png'):
                cmd = 'convert -crop 510x815 '+file+' cropped_%d.png'
                os.system(cmd)
                (base,ext) = os.path.splitext(file)
                (category,platform,datetime,product_orig) = base.split('.')
                for base_tmp in dict.keys():
                    file_new = category+'.'+platform+'.'+datetime+'.'+product_orig+'_'+dict[base_tmp]+ext
                    shutil.move(indir+'/'+date+'/'+base_tmp+ext,
                                outdir+'/'+date+'/'+file_new)
