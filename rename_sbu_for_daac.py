#!/usr/bin/python3

import os
import shutil

baseDir = '/home/disk/bob/impacts/gdrive/IMPACTS'
RTbaseDir = baseDir+'/RadarTruck'
#products = ['dopplerlidar','kaspr','mrr2','mrrpro2','parsivel','parsivel2','pluvio','vceilo15k','vceilo7.5k','weatherdhs']
products = []
RTproducts = ['airmarweather','chm15k','mrrpro2white','parsivel2']
prefix_base_out = 'IMPACTS_SBU'
monthDict = {'Jan':'01',
             'Feb':'02',
             'Mar':'03',
             'Apr':'04',
             'May':'05',
             'Jun':'06',
             'Jul':'07',
             'Aug':'08',
             'Sep':'09',
             'Oct':'10',
             'Nov':'11',
             'Dec':'12'}

for product in products:

    if product == 'dopplerlidar':
        print('Renaming dopplerlidar files...')
        path = baseDir+'/'+product+'/netcdf/2020'
        prefix_out = prefix_base_out+'_'+product
        for fname_in in os.listdir(path):
            if fname_in.endswith('nc'):
                print('fname_in = ',fname_in)
                (base, ext) = os.path.splitext(fname_in)
                (prefix1,prefix2,date) = base.split('_')
                if prefix1 == 'Stare':
                    suffix_out = 'vpt_BNL'
                elif prefix1 == 'User1':
                    suffix_out = 'rhi_BNL'
                elif prefix1 == 'VAD':
                    suffix_out = 'vel_az_BNL'
                fname_out = prefix_out+'_'+date+'_'+suffix_out+'.nc'
                shutil.move(path+'/'+fname_in,path+'/'+fname_out)
    
    elif product == 'kaspr':
        print('Renaming kaspr files...')
        path = baseDir+'/'+product+'/netcdf'
        prefix_out = prefix_base_out+'_'+product
        for dir in os.listdir(path):
            if dir.startswith('2020'):
                path_new = path+'/'+dir
                for fname_in in os.listdir(path_new):
                    if fname_in.endswith('nc'):
                        print('fname_in = ',fname_in)
                        (base, ext) = os.path.splitext(fname_in)
                        (main,suffix_out) = base.split('.')
                        if main.startswith('KASPR_MOMENTS_'):
                            datetime = main.replace('KASPR_MOMENTS_','')
                        elif main.startswith('KASPR_PP_MOMENTS_'):
                            datetime = main.replace('KASPR_PP_MOMENTS_','')
                        (date,time) = datetime.split('-')
                        fname_out = prefix_out+'_'+date+'_'+time+'_'+suffix_out+'.nc'
                        shutil.move(path_new+'/'+fname_in,path_new+'/'+fname_out)
                                            
    elif product == 'mrr2':
        print('Renaming mrr2 files...')
        path = baseDir+'/'+product+'/netcdf'
        prefix_out = prefix_base_out+'_'+product
        suffix_out = 'BNL'
        for dir in os.listdir(path):
            if dir.startswith('2020'):
                path_new = path+'/'+dir
                for fname_in in os.listdir(path_new):
                    if fname_in.endswith('nc'):
                        print('fname_in = ',fname_in)
                        (base, ext) = os.path.splitext(fname_in)
                        (prefix1,prefix2,date) = base.split('_')
                        fname_out = prefix_out+'_'+date+'_'+suffix_out+'.nc'
                        shutil.move(path_new+'/'+fname_in,path_new+'/'+fname_out)

    elif product == 'mrrpro2':
        print('Renaming mrrpro2 files...')
        path = baseDir+'/'+product+'/netcdf'
        prefix_out = prefix_base_out+'_'+product
        suffix_out = 'MAN'
        for dir in os.listdir(path):
            if dir.startswith('2020'):
                for dir2 in os.listdir(path+'/'+dir):
                    if dir2.startswith('2020'):
                        path_new = path+'/'+dir+'/'+dir2
                        for fname_in in os.listdir(path_new):
                            if fname_in.endswith('nc'):
                                print('fname_in = ',fname_in)
                                (datetime, ext) = os.path.splitext(fname_in)
                                fname_out = prefix_out+'_'+datetime+'_'+suffix_out+'.nc'
                                shutil.move(path_new+'/'+fname_in,path_new+'/'+fname_out)
        

    elif product == 'parsivel':
        print('Renaming parsivel files...')
        path = baseDir+'/'+product+'/netcdf/2020'
        prefix_out = prefix_base_out+'_'+product
        suffix_out = 'MAN'
        for fname_in in os.listdir(path):
            if fname_in.endswith('nc'):
                print('fname_in = ',fname_in)
                (base, ext) = os.path.splitext(fname_in)
                (prefix,date) = base.split('_')
                fname_out = prefix_out+'_'+date+'_'+suffix_out+'.nc'
                shutil.move(path+'/'+fname_in,path+'/'+fname_out)
        

    elif product == 'parsivel2':
        print('Renaming parsivel2 files...')
        path = baseDir+'/'+product+'/netcdf/2020'
        prefix_out = prefix_base_out+'_parsivel'
        for fname_in in os.listdir(path):
            if fname_in.endswith('nc'):
                print('fname_in = ',fname_in)
                (base, ext) = os.path.splitext(fname_in)
                (prefix,date) = base.split('_')
                fname_out = prefix_out+'_'+date+'.nc'
                shutil.move(path+'/'+fname_in,path+'/'+fname_out)
        
    elif product == 'pluvio':
        print('Renaming pluvio files...')
        path = baseDir+'/'+product
        prefix_out = prefix_base_out+'_'+product
        for fname_in in os.listdir(path):
            if fname_in.endswith('txt'):
                print('fname_in = ',fname_in)
                (base, ext) = os.path.splitext(fname_in)
                (prefix,date) = base.split('_')
                fname_out = prefix_out+'_'+date+'.csv'
                shutil.move(path+'/'+fname_in,path+'/'+fname_out)

    elif product == 'vceilo15k':
        print('Renaming vceilo15k files...')
        path = baseDir+'/'+product+'/netcdf'
        prefix_out = prefix_base_out+'_ceilo'
        suffix_out = 'cl15k_MAN'
        for fname_in in os.listdir(path):
            if fname_in.startswith('L3'):
                print('fname_in = ',fname_in)
                (base, ext) = os.path.splitext(fname_in)
                base = base.replace('L3_DEFAULT__','')
                parts = base.split('_')
                datetime = parts[0]
                date = datetime[0:8]
                time = datetime[8:]
                fname_out = prefix_out+'_'+date+'_'+time+'_'+suffix_out+'.nc'
                shutil.move(path+'/'+fname_in,path+'/'+fname_out)

    elif product == 'vceilo7.5k':
        print('Renaming vceilo7.5k files...')
        path = baseDir+'/'+product+'/netcdf/2020'
        prefix_out = prefix_base_out+'_ceilo'
        suffix_out = 'ct25k_BNL'
        for fname_in in os.listdir(path):
            if fname_in.endswith('nc'):
                print('fname_in = ',fname_in)
                (base, ext) = os.path.splitext(fname_in)
                (date,junk) = base.split('_')
                fname_out = prefix_out+'_'+date+'_'+suffix_out+'.nc'
                shutil.move(path+'/'+fname_in,path+'/'+fname_out)
                

    elif product == 'weatherdhs':
        print('Renaming weatherdhs files...')
        path = baseDir+'/'+product+'/csv'
        prefix_out = prefix_base_out+'_'+product
        suffix_out = 'MAN'
        for fname_in in os.listdir(path):
            if fname_in.endswith('txt'):
                print('fname_in = ',fname_in)
                date1 = fname_in.replace('Values.txt','')
                (year,month,day) = date1.split('-')
                date = year+month+day
                fname_out = prefix_out+'_'+date+'_'+suffix_out+'.csv'
                shutil.move(path+'/'+fname_in,path+'/'+fname_out)

for product in RTproducts:

    if product == 'airmarweather':
        print('Renaming airmarweather files...')
        path = RTbaseDir+'/'+product+'/netcdf'
        prefix_out = prefix_base_out+'_'+product
        suffix_out = 'RT'
        for fname_in in os.listdir(path):
            if fname_in.endswith('nc'):
                print('fname_in = ',fname_in)
                (base, ext) = os.path.splitext(fname_in)
                tmpDate = base.replace('_PORT_5_0183','')
                (strMonth,day,year) = tmpDate.split('_')
                month = monthDict[strMonth]
                date = year+month+day
                fname_out = prefix_out+'_'+date+'_'+suffix_out+'.nc'
                shutil.move(path+'/'+fname_in,path+'/'+fname_out)                    

    elif product == 'chm15k':
        print('Renaming chm15k files...')
        path = RTbaseDir+'/'+product+'/netcdf/2020'
        prefix_out = prefix_base_out+'_ceilo'
        suffix_out = 'chm15k_RT'
        for monthDir in os.listdir(path):
            if len(monthDir) == 2:
                for dayDir in os.listdir(path+'/'+monthDir):
                    if len(dayDir) == 2:
                        path_new = path+'/'+monthDir+'/'+dayDir
                        for fname_in in os.listdir(path_new):
                            if fname_in.endswith('nc'):
                                print('fname_in = ',fname_in)
                                (base, ext) = os.path.splitext(fname_in)
                                (date,junk1,junk2,time,junk3) = base.split('_')
                                fname_out = prefix_out+'_'+date+'_'+time+'_'+suffix_out+'.nc'
                                shutil.move(path_new+'/'+fname_in,path_new+'/'+fname_out)                    

    elif product == 'mrrpro2white':
        print('Renaming mrrpro2white files...')
        path = RTbaseDir+'/'+product+'/netcdf'
        prefix_out = prefix_base_out+'_mrrpro'
        suffix_out = 'RT'
        for monthDir in os.listdir(path):
            if len(monthDir) == 6:
                for dayDir in os.listdir(path+'/'+monthDir):
                    if len(dayDir) == 8:
                        path_new = path+'/'+monthDir+'/'+dayDir
                        for fname_in in os.listdir(path_new):
                            if fname_in.endswith('nc'):
                                print('fname_in = ',fname_in)
                                (base, ext) = os.path.splitext(fname_in)
                                (date,time) = base.split('_')
                                fname_out = prefix_out+'_'+date+'_'+time+'_'+suffix_out+'.nc'
                                shutil.move(path_new+'/'+fname_in,path_new+'/'+fname_out)

    elif product == 'parsivel2':
        print('Renaming parsivel2 files...')
        path = RTbaseDir+'/'+product+'/netcdf/2020'
        prefix_out = prefix_base_out+'_parsivel'
        suffix_out = 'RT'
        for fname_in in os.listdir(path):
            if fname_in.endswith('nc'):
                print('fname_in = ',fname_in)
                (base, ext) = os.path.splitext(fname_in)
                (junk,date) = base.split('_')
                fname_out = prefix_out+'_'+date+'_'+suffix_out+'.nc'
                shutil.move(path+'/'+fname_in,path+'/'+fname_out)
        
    
   
