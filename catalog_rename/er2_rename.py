#!/usr/bin/python

import os
import shutil

inDir = '/home/disk/funnel/impacts-website/archive/research/er2'
# These pair 'old product name':'new product name'
products = {'ampr':'AMPR',
            'cosmir_aft_conical':'CoSMIR_aft_conical',
            'cosmir_along_track':'CoSMIR_along_track',
            'cosmir_cross_track':'CoSMIR_cross_track',
            'cosmir_forward_conical':'CoSMIR_forward_conical',
            'cpl_1064nm':'CPL_1064nm',
            'cpl_355nm':'CPL_355nm',
            'cpl_532nm':'CPL_532nm',
            'cpl_aerosol_od':'CPL_aerosol_opt_depth',
            'cpl_cloud_od':'CPL_cloud_opt_depth',
            'cpl_column_od':'CPL_column_opt_depth',
            'cpl_combo':'CPL_combo',
            'cpl_depol_ratio':'CPL_depol_ratio',
            'cpl_extinction_coef':'CPL_extinction_coef',
            'cpl_feature_type':'CPL_feature_type',
            'cpl_map':'CPL_flight_track',
            'cpl_iwc':'CPL_iwc',
            'crs':'CRS_dBZ_quicklook',
            'crs_dbz':'CRS_dBZ',
            'crs_ldr':'CRS_ldr',
            'crs_sw':'CRS_sw',
            'crs_vel':'CRS_vel',
            'exrad':'EXRAD_dBZ_quicklook',
            'exrad_dbz':'EXRAD_dBZ',
            'exrad_sw':'EXRAD_sw',
            'exrad_vel':'EXRAD_vel',
            'flight_track':'flight_track_composite',
            'hiwrap_ka':'HIWRAP_Ka_dBZ_quicklook',
            'hiwrap_Ka_dbz':'HIWRAP_Ka_dBZ',
            'hiwrap_Ka_sw':'HIWRAP_Ka_sw',
            'hiwrap_Ka_vel':'HIWRAP_Ka_vel',
            'hiwrap_ku':'HIWRAP_Ku_dBZ_quicklook',
            'hiwrap_Ku_dbz':'HIWRAP_Ku_dBZ',
            'hiwrap_Ku_sw':'HIWRAP_Ku_sw',
            'hiwrap_Ku_vel':'HIWRAP_Ku_vel'}
outDir = '/home/disk/funnel/impacts-website/archive_ncar/aircraft/NASA_ER2'
category_new = 'aircraft'
platform_new = 'NASA_ER2'

for date in os.listdir(inDir):
    if os.path.isdir(inDir+'/'+date) and '2020' in date:
        if not os.path.isdir(outDir+'/'+date):
            os.mkdir(outDir+'/'+date)
        for file in os.listdir(inDir+'/'+date):
            if 'all' not in file and (file.endswith('png') or file.endswith('gif')):
                print('file = '+file)
                basename = os.path.splitext(file)[0]
                ext = os.path.splitext(file)[1]
                (category,plat,datetime,prod) = basename.split('.')
                file_new = category_new+'.'+platform_new+'.'+datetime+'.'+products[prod]+ext
                print('file_new = '+file_new)
                shutil.copy(inDir+'/'+date+'/'+file,
                            outDir+'/'+date+'/'+file_new)
