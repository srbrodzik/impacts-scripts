#!/usr/bin/python

import os
import shutil

inDirBase = '/home/disk/funnel/impacts-website/archive/model'
outDirBase = '/home/disk/funnel/impacts-website/archive_ncar/model'
category_new = 'model'
platforms = {'gfs_28km':'GFS_28km',
             'hrrr_01km':'HRRR_01km',
             'hrrr_03km':'HRRR_03km',
             'nam_12km':'NAM_12km',
             'wrf_gfs_04km':'WRF_GFS_SBU_04km',
             'wrf_gfs_12km':'WRF_GFS_SBU_12km',
             'wrf_gfs_36km':'WRF_GFS_SBU_36km'}
gfs_products = {'T2m_us':'T2m',
                'temp_adv_fgen_700_us':'700hPa_temp_adv_fgen_wind',
                'uv250_us':'250mb_wind_mslp',
                'z500_vort_us':'500mb_ht_vort_wind',
                'ir_us':'ir_Tb',
                'ref_frzn_us':'refl_mslp',
                'T850_us':'850hPa_temp_wind_mslp'}
hrrr01_products = {'ctop':'cloud_top_ht',
                   'cref_sfc':'refl',
                   'G114bt_sat':'ir_Tb',
                   'lcc_sfc':'low_level_cld_cvr',
                   'mcc_sfc':'mid_level_cld_cvr',
                   'hcc_sfc':'high_level_cld_cvr',
                   'wind_250':'250mb_ht_wind',
                   'temp_700':'700mb_temp_ht_wind',
                   'temp_850':'850mb_temp_ht_wind',
                   'temp_925':'925mb_temp_ht_wind'}
hrrr03_products = {'ref_frzn_us':'refl_mslp',
                   'ir_us':'ir_Tb',
                   'T2m_us':'T2m'}
nam_products = {'T2m_us':'T2m',
                'uv250_us':'250mb_wind_mslp',
                'z500_vort_us':'500mb_ht_vort_wind',
                'temp_adv_fgen_700_us':'700hPa_temp_adv_fgen_wind',
                'T850_us':'850hPa_temp_wind_mslp',
                'ref_frzn_us':'refl_mslp'}
wrf_products = {'500_avo':'500hPa_wind_ht_vort',
                '700_dBZfronto':'700hPa_ht_fronto_refl',
                '850_dBZfronto':'850hPa_ht_fronto_refl',
                'refl_10cm':'refl_preciptype_mslp_wind',
                'temps_sfc':'T2m_mslp_uv10m',
                'pcp3':'3hr_precip'}
             
for platform in platforms.keys():

    # get appropriate product dictionary
    if platform == 'gfs_28km':
        products = gfs_products
    elif platform == 'hrrr_01km':
        products = hrrr01_products
    elif platform == 'hrrr_03km':
        products = hrrr03_products
    elif platform == 'nam_12km':
        products = nam_products
    else:
        products = wrf_products

    # make output product dir
    if not os.path.isdir(outDirBase+'/'+platforms[platform]):
        os.mkdir(outDirBase+'/'+platforms[platform])

    # go through dates & files
    for date in os.listdir(inDirBase+'/'+platform):
        if not os.path.isdir(outDirBase+'/'+platforms[platform]+'/'+date):
            os.mkdir(outDirBase+'/'+platforms[platform]+'/'+date)
        for file in os.listdir(inDirBase+'/'+platform+'/'+date):
                print('file = '+file)
                basename = os.path.splitext(file)[0]
                ext = os.path.splitext(file)[1]
                (category_orig,platform_orig,datetime,product_orig) = basename.split('.')
                parts = product_orig.split('_')
                fcst_hr = '0'+parts[0]
                separator = '_'
                fcst_product = separator.join(parts[1:])                
                file_new = category_new+'.'+platforms[platform]+'.'+datetime+'.'+fcst_hr+'_'+products[fcst_product]+ext
                print('file_new = '+file_new)
                shutil.copy(inDirBase+'/'+platform+'/'+date+'/'+file,
                            outDirBase+'/'+platforms[platform]+'/'+date+'/'+file_new)
            
