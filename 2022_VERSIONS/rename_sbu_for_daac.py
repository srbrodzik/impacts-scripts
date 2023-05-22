#!/usr/bin/python3

import os
import shutil

baseDir = '/home/disk/bob/impacts/radar/sbu'
RTbaseDir = baseDir+'/RadarTruck'
products = ['grawmetsounding','mrrpro2white','parsivel','pluvio','skyler1','vceilo15k']
RTproducts = ['airmarweather','grawmetsounding','parsivel2','skyler2']
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

    if product == 'grawmetsounding':
        # Data files: IMPACTS_sounding_YYYYMMDD_hhmmss_SBU_Mobile.nc
        # Needs new suffix for static soundings, maybe:
        # Data files: IMPACTS_sounding_YYYYMMDD_hhmmss_SBU.nc
        print('Renaming sounding files...')
        path = baseDir+'/'+product+'/netcdf'
        prefix_out = prefix_base_out+'_'+product
        for fname_in in os.listdir(path):
            if fname_in.endswith('nc'):
                print('fname_in = ',fname_in)
                (base, ext) = os.path.splitext(fname_in)
                (prefix1,prefix2,prefix2,date,time) = base.split('_')
                totalPrefix = prefix1+'_'+prefix2+'_'+prefix3
                if totalPrefix == 'GrawSonde_SBUSouthP_RTS':
                    suffix_out = 'vpt_BNL'
                    fname_out = prefix_out+'_'+date+'_'+suffix_out+'.nc'
                    shutil.move(path+'/'+fname_in,path+'/'+fname_out)
    
    elif product == 'mrrpro2white':
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

    elif product == 'skyler1':
        print('Renaming skyler1 files...')
        path = baseDir+'/'+product+'/netcdf'
        prefix_out = prefix_base_out+'_'+product
        for dir1 in os.listdir(path):
            if dir1.startswith('2022'):
                path_new = path+'/'+dir1
                for dir2 in os.listdir(path_new):
                    if dir2=='ppi':
                        path_newest = path_new+'/'+dir2
                        for fname_in in os.listdir(path_newest):
                            if fname_in.endswith('nc'):
                                print('fname_in =',fname_in)
                                (base, ext) = os.path.splitext(fname_in)
                                (pre,scan,date,time) = base.split('_')
                                fname_out = prefix_out+'_'+date+'_'+time+'_'+scan+'.nc'
                                print('fname_out =',fname_out)
                                shutil.move(path_newest+'/'+fname_in,path_newest+'/'+fname_out)
                    elif dir2=='rhi':
                        path_newest = path_new+'/'+dir2
                        for fname_in in os.listdir(path_newest):
                            if fname_in.endswith('nc'):
                                print('fname_in =',fname_in)
                                (base, ext) = os.path.splitext(fname_in)
                                if len(base.split('_')) == 4:
                                    (pre,scan,date,time) = base.split('_')
                                    fname_out = prefix_out+'_'+date+'_'+time+'_'+scan+'_mid.nc'
                                elif len(base.split('_')) == 5:
                                    (pre,scan,dir,date,time) = base.split('_')
                                    fname_out = prefix_out+'_'+date+'_'+time+'_'+scan+'_'+dir+'.nc'
                                print('fname_out =',fname_out)
                                shutil.move(path_newest+'/'+fname_in,path_newest+'/'+fname_out)
                         
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
        
    
   
