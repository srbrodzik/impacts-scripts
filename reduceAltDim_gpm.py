import os
import sys

indir = '/home/disk/bob/gpm/nam_imp_ku/classify/ex_data_v06/2019/12'
outdir = '/home/disk/bob/impacts/raw/gpm_ku'

for file in os.listdir(indir):
    if file.endswith('.nc'):
        print file
        cmd = 'ncks -d alt,0,124 '+indir+'/'+file+' '+outdir+'/'+file
        os.system(cmd)
