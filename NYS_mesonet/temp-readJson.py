#!/usr/bin/python

import os
import json
import pandas as pd
import xarray as xr
import glob

indir = '/home/disk/data/albany/profiler'
outdir = '/home/disk/bob/impacts/bin/NYS_mesonet/prof_output'
sites = ['ALBA','BELL','BRON','BUFF','CHAZ','CLYM','EHAM',
         'JORD','OWEG','QUEE','REDH','STAT','STON','SUFF',
         'TUPP','WANT','WEBS']

for site in sites:

    print('Site: {}'.format(site))

    outfile1 = outdir+'/nys_profiler_'+site+'_times'
    outfile2 = outdir+'/nys_profiler_'+site+'_missing_data'

    fout1 = open(outfile1,'w')
    fout2 = open(outfile2,'w')

    for date in sorted(os.listdir(indir)):
        if date.startswith('202001') or date.startswith('202002'):
            print('Date: {}'.format(date))
            sitefiles = sorted(glob.glob(indir+'/'+date+'/'+'*_'+site+'.json'))
            for file in sitefiles:
                fin = open(file,'r')
                data = json.load(fin)
                mwr = data['mwr']
                lidar = data['lidar']
                if not mwr and not lidar:
                    fout1.write('{}:\tNo data\n'.format(file))
                    fout2.write('{}:\tmissing mwr & lidar data\n'.format(file))
                    continue
                elif not mwr:
                    fout2.write('{}:\tmissing mwr data\n'.format(file))
                    lidar = xr.Dataset.from_dict(lidar)
                    lidar = xr.decode_cf(lidar)
                    lidar_df = lidar.to_dataframe()
                    times = lidar_df.index.get_level_values('time').drop_duplicates()
                    fout1.write('{}:\t{}\t{}\n'.format(file,times[0],times[-1]))
                elif not lidar:
                    fout2.write('{}:\tmissing lidar data\n'.format(file))
                    mwr = xr.Dataset.from_dict(mwr)
                    mwr = xr.decode_cf(mwr)
                    mwr_p = mwr['pressure_level'].to_dataframe()
                    times = mwr_p.index.get_level_values('time').drop_duplicates()
                    fout1.write('{}:\t{}\t{}\n'.format(file,times[0],times[-1]))
                else:
                    mwr = xr.Dataset.from_dict(mwr)
                    mwr = xr.decode_cf(mwr)
                    mwr_p = mwr['pressure_level'].to_dataframe()
                    times = mwr_p.index.get_level_values('time').drop_duplicates()
                    fout1.write('{}:\t{}\t{}\n'.format(file,times[0],times[-1]))
                fin.close()

    fout1.close()
    fout2.close()
