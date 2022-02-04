#!/usr/bin/python3

import os
import sys
import shutil
from ftplib import FTP

test = True
debug = True
year = '2022'
months = ['01']
days = []
for day in range(1,25):
    if day < 10:
        day = '0'+str(day)
    else:
        day = str(day)
    days.append(day)
    
startMMDD = '0101'
tempDir = '/tmp'
baseDir = '/home/disk/meso-home/wolff/Ground_Instruments/Plots'
wff_instr = ['apu05','apu07','apu08','apu09',
             'apu10','apu11','apu15','apu17','apu20',
             'apu21','apu23','apu25','MRR2-02','MRR2-02',
             'MRRPRO-01','MRRPRO-02']
gail_instr = ['apu18','PIP003','MRR2-03']

# Field Catalog inputs
if test:
    ftpCatalogServer = 'ftp.atmos.washington.edu'
    ftpCatalogUser = 'anonymous'
    ftpCatalogPassword = 'brodzik@uw.edu'
    catalogDestDir = 'brodzik/incoming/impacts'
else:
    ftpCatalogServer = 'catalog.eol.ucar.edu'
    ftpCatalogUser = 'anonymous'
    catalogDestDir = '/pub/incoming/catalog/impacts'

# Open ftp connection
if test:
    catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser,ftpCatalogPassword)
    catalogFTP.cwd(catalogDestDir)
else:
    catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
    catalogFTP.cwd(catalogDestDir)

for inst in wff_instr:
    print('{} {}'.format('Instrument =',inst))
    if 'apu' in inst:
        catCategory = 'surface'
        catPlatform = 'Parsivel'
        path = baseDir+'/'+inst+'/DSD/'+year
        os.chdir(path)
        for file in os.listdir(path):
            print('{} {} {}'.format(inst,'file =',file))
            if file.startswith('WFF') and file.endswith('dsd.png'):
                (base,ext) = os.path.splitext(file)
                (wff,abbr,yr,mmdd,dsd) = base.split('_')
                if mmdd >= startMMDD:
                    catProduct = 'WFF_'+abbr+'_DSD'
                    catName = catCategory+'.'+catPlatform+'.'+yr+mmdd+'0000.'+catProduct+ext
                    shutil.copy(path+'/'+file,
                                tempDir+'/'+catName)
                    #catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
                    #catalogFTP.cwd(catalogDestDir)
                    catalogFTP.set_pasv(False)
                    ftpFile = open(os.path.join(tempDir,catName),'rb')
                    catalogFTP.storbinary('STOR '+catName,ftpFile)
                    ftpFile.close()
                    os.remove(tempDir+'/'+catName)

        path = baseDir+'/'+inst+'/Rain/'+year
        os.chdir(path)
        for file in os.listdir(path):
            print('{} {} {}'.format(inst,'file =',file))
            if file.startswith('WFF') and file.endswith('rain.png'):
                (base,ext) = os.path.splitext(file)
                (wff,abbr,yr,mmdd,rain) = base.split('_')
                if mmdd >= startMMDD:
                    catProduct = 'WFF_'+abbr+'_Rain'
                    catName = catCategory+'.'+catPlatform+'.'+yr+mmdd+'0000.'+catProduct+ext
                    shutil.copy(path+'/'+file,
                                tempDir+'/'+catName)
                    #catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
                    #catalogFTP.cwd(catalogDestDir)
                    catalogFTP.set_pasv(False)
                    ftpFile = open(os.path.join(tempDir,catName),'rb')
                    catalogFTP.storbinary('STOR '+catName,ftpFile)
                    ftpFile.close()
                    os.remove(tempDir+'/'+catName)

    elif 'MRR2' in inst:
        catCategory = 'radar'
        catPlatform = 'MRR'
        for month in months:
            for day in days:
                path = baseDir+'/'+inst+'/'+year+'/'+month+'/'+day+'/ql'
                os.chdir(path)
                for file in os.listdir(path):
                    print('{} {} {}'.format(inst,'file =',file))
                    if file.startswith('WFF') and file.endswith('png'):
                        (base,ext) = os.path.splitext(file)
                        try:
                            (wff,abbr,yr,mmdd,hour,ql) = base.split('_')
                            if mmdd >= startMMDD:
                                catProduct = 'WFF_'+abbr+'_hourly'
                                catName = catCategory+'.'+catPlatform+'.'+yr+mmdd+hour+'00.'+catProduct+ext
                                shutil.copy(path+'/'+file,
                                            tempDir+'/'+catName)
                                catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
                                catalogFTP.cwd(catalogDestDir)
                                catalogFTP.set_pasv(False)
                                ftpFile = open(os.path.join(tempDir,catName),'rb')
                                catalogFTP.storbinary('STOR '+catName,ftpFile)
                                ftpFile.close()
                                os.remove(tempDir+'/'+catName)
                        except:
                            (wff,abbr,yr,mmdd,ql) = base.split('_')
                            if mmdd >= startMMDD:
                                catProduct = 'WFF_'+abbr
                                catName = catCategory+'.'+catPlatform+'.'+yr+mmdd+'0000.'+catProduct+ext
                                shutil.copy(path+'/'+file,
                                            tempDir+'/'+catName)
                                catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
                                catalogFTP.cwd(catalogDestDir)
                                catalogFTP.set_pasv(False)
                                ftpFile = open(os.path.join(tempDir,catName),'rb')
                                catalogFTP.storbinary('STOR '+catName,ftpFile)
                                ftpFile.close()
                                os.remove(tempDir+'/'+catName)
                                
    elif 'MRRPRO' in inst:
        catCategory = 'radar'
        catPlatform = 'MRR'
        for month in months:
            for day in days:
                path = baseDir+'/'+inst+'/'+year+'/'+month+'/'+day+'/ql'
                os.chdir(path)
                for file in os.listdir(path):
                    print('{} {} {}'.format(inst,'file =',file))
                    if file.startswith('WFF') and file.endswith('png'):
                        (base,ext) = os.path.splitext(file)
                        try:
                            (wff,abbr,yr,mmdd,hour,ql) = base.split('_')
                            if mmdd >= startMMDD:
                                catProduct = 'WFF_'+abbr+'_hourly'
                                catName = catCategory+'.'+catPlatform+'.'+yr+mmdd+hour+'00.'+catProduct+ext
                                shutil.copy(path+'/'+file,
                                            tempDir+'/'+catName)
                                catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
                                catalogFTP.cwd(catalogDestDir)
                                catalogFTP.set_pasv(False)
                                ftpFile = open(os.path.join(tempDir,catName),'rb')
                                catalogFTP.storbinary('STOR '+catName,ftpFile)
                                ftpFile.close()
                                os.remove(tempDir+'/'+catName)
                        except:
                            (wff,abbr,yr,mmdd,ql) = base.split('_')
                            if mmdd >= startMMDD:
                                catProduct = 'WFF_'+abbr
                                catName = catCategory+'.'+catPlatform+'.'+yr+mmdd+'0000.'+catProduct+ext
                                shutil.copy(path+'/'+file,
                                            tempDir+'/'+catName)
                                catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
                                catalogFTP.cwd(catalogDestDir)
                                catalogFTP.set_pasv(False)
                                ftpFile = open(os.path.join(tempDir,catName),'rb')
                                catalogFTP.storbinary('STOR '+catName,ftpFile)
                                ftpFile.close()
                                os.remove(tempDir+'/'+catName)
                            
    elif 'PIP' in inst:
        catCategory = 'surface'
        catPlatform = 'PIP'
        for month in months:
            path = baseDir+'/'+inst+'/'+year+'/'+month
            os.chdir(path)
            for file in os.listdir(path):
                print('{} {} {}'.format(inst,'file =',file))
                if file.startswith('003') and file.endswith('png'):
                    (base,ext) = os.path.splitext(file)
                    (dateStr,sum,fig) = base.split('_')
                    date = dateStr[3:]
                    mmdd = date[4:]
                    if mmdd >= startMMDD:
                        catProduct = 'WFF_'+inst
                        catName = catCategory+'.'+catPlatform+'.'+date+'0000.'+catProduct+ext
                        shutil.copy(path+'/'+file,
                                    tempDir+'/'+catName)
                        catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
                        catalogFTP.cwd(catalogDestDir)
                        catalogFTP.set_pasv(False)
                        ftpFile = open(os.path.join(tempDir,catName),'rb')
                        catalogFTP.storbinary('STOR '+catName,ftpFile)
                        ftpFile.close()
                        os.remove(tempDir+'/'+catName)
                        
for inst in gail_instr:
    print('{} {}'.format('Instrument =',inst))
    if 'apu' in inst:
        catCategory = 'surface'
        catPlatform = 'Parsivel'
        path = baseDir+'/'+inst+'/DSD/'+year
        os.chdir(path)
        for file in os.listdir(path):
            print('{} {} {}'.format(inst,'file =',file))
            if file.startswith('WFF') and file.endswith('dsd.png'):
                (base,ext) = os.path.splitext(file)
                (wff,abbr,yr,mmdd,dsd) = base.split('_')
                if mmdd >= startMMDD:
                    catProduct = 'NASA_GAIL_UConn_DSD'
                    catName = catCategory+'.'+catPlatform+'.'+yr+mmdd+'0000.'+catProduct+ext
                    shutil.copy(path+'/'+file,
                                tempDir+'/'+catName)
                    #catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
                    #catalogFTP.cwd(catalogDestDir)
                    catalogFTP.set_pasv(False)
                    ftpFile = open(os.path.join(tempDir,catName),'rb')
                    catalogFTP.storbinary('STOR '+catName,ftpFile)
                    ftpFile.close()
                    os.remove(tempDir+'/'+catName)

        path = baseDir+'/'+inst+'/Rain/'+year
        os.chdir(path)
        for file in os.listdir(path):
            print('{} {} {}'.format(inst,'file =',file))
            if file.startswith('WFF') and file.endswith('rain.png'):
                (base,ext) = os.path.splitext(file)
                (wff,abbr,yr,mmdd,rain) = base.split('_')
                if mmdd >= startMMDD:
                    catProduct = 'NASA_GAIL_UConn_Rain'
                    catName = catCategory+'.'+catPlatform+'.'+yr+mmdd+'0000.'+catProduct+ext
                    shutil.copy(path+'/'+file,
                                tempDir+'/'+catName)
                    #catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
                    #catalogFTP.cwd(catalogDestDir)
                    catalogFTP.set_pasv(False)
                    ftpFile = open(os.path.join(tempDir,catName),'rb')
                    catalogFTP.storbinary('STOR '+catName,ftpFile)
                    ftpFile.close()
                    os.remove(tempDir+'/'+catName)

    elif 'MRR2' in inst:
        catCategory = 'radar'
        catPlatform = 'MRR'
        for month in months:
            for day in days:
                path = baseDir+'/'+inst+'/'+year+'/'+month+'/'+day+'/ql'
                os.chdir(path)
                for file in os.listdir(path):
                    print('{} {} {}'.format(inst,'file =',file))
                    if file.startswith('WFF') and file.endswith('png'):
                        (base,ext) = os.path.splitext(file)
                        try:
                            (wff,abbr,yr,mmdd,hour,ql) = base.split('_')
                            if mmdd >= startMMDD:
                                catProduct = 'NASA_GAIL_UConn_hourly'
                                catName = catCategory+'.'+catPlatform+'.'+yr+mmdd+hour+'00.'+catProduct+ext
                                shutil.copy(path+'/'+file,
                                            tempDir+'/'+catName)
                                catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
                                catalogFTP.cwd(catalogDestDir)
                                catalogFTP.set_pasv(False)
                                ftpFile = open(os.path.join(tempDir,catName),'rb')
                                catalogFTP.storbinary('STOR '+catName,ftpFile)
                                ftpFile.close()
                                os.remove(tempDir+'/'+catName)
                        except:
                            (wff,abbr,yr,mmdd,ql) = base.split('_')
                            if mmdd >= startMMDD:
                                catProduct = 'NASA_GAIL_UConn'
                                catName = catCategory+'.'+catPlatform+'.'+yr+mmdd+'0000.'+catProduct+ext
                                shutil.copy(path+'/'+file,
                                            tempDir+'/'+catName)
                                catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
                                catalogFTP.cwd(catalogDestDir)
                                catalogFTP.set_pasv(False)
                                ftpFile = open(os.path.join(tempDir,catName),'rb')
                                catalogFTP.storbinary('STOR '+catName,ftpFile)
                                ftpFile.close()
                                os.remove(tempDir+'/'+catName)
                                
    elif 'MRRPRO' in inst:
        catCategory = 'radar'
        catPlatform = 'MRR'
        for month in months:
            for day in days:
                path = baseDir+'/'+inst+'/'+year+'/'+month+'/'+day+'/ql'
                os.chdir(path)
                for file in os.listdir(path):
                    print('{} {} {}'.format(inst,'file =',file))
                    if file.startswith('WFF') and file.endswith('png'):
                        (base,ext) = os.path.splitext(file)
                        try:
                            (wff,abbr,yr,mmdd,hour,ql) = base.split('_')
                            if mmdd >= startMMDD:
                                catProduct = 'NASA_GAIL_UConn_hourly'
                                catName = catCategory+'.'+catPlatform+'.'+yr+mmdd+hour+'00.'+catProduct+ext
                                shutil.copy(path+'/'+file,
                                            tempDir+'/'+catName)
                                catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
                                catalogFTP.cwd(catalogDestDir)
                                catalogFTP.set_pasv(False)
                                ftpFile = open(os.path.join(tempDir,catName),'rb')
                                catalogFTP.storbinary('STOR '+catName,ftpFile)
                                ftpFile.close()
                                os.remove(tempDir+'/'+catName)
                        except:
                            (wff,abbr,yr,mmdd,ql) = base.split('_')
                            if mmdd >= startMMDD:
                                catProduct = 'NASA_GAIL_UConn_hourly'
                                catName = catCategory+'.'+catPlatform+'.'+yr+mmdd+'0000.'+catProduct+ext
                                shutil.copy(path+'/'+file,
                                            tempDir+'/'+catName)
                                catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
                                catalogFTP.cwd(catalogDestDir)
                                catalogFTP.set_pasv(False)
                                ftpFile = open(os.path.join(tempDir,catName),'rb')
                                catalogFTP.storbinary('STOR '+catName,ftpFile)
                                ftpFile.close()
                                os.remove(tempDir+'/'+catName)
                            
    elif 'PIP' in inst:
        catCategory = 'surface'
        catPlatform = 'PIP'
        for month in months:
            path = baseDir+'/'+inst+'/'+year+'/'+month
            os.chdir(path)
            for file in os.listdir(path):
                print('{} {} {}'.format(inst,'file =',file))
                if file.startswith('003') and file.endswith('png'):
                    (base,ext) = os.path.splitext(file)
                    (dateStr,sum,fig) = base.split('_')
                    date = dateStr[3:]
                    mmdd = date[4:]
                    if mmdd >= startMMDD:
                        catProduct = 'NASA_GAIL_UConn'
                        catName = catCategory+'.'+catPlatform+'.'+date+'0000.'+catProduct+ext
                        shutil.copy(path+'/'+file,
                                    tempDir+'/'+catName)
                        catalogFTP = FTP(ftpCatalogServer,ftpCatalogUser)
                        catalogFTP.cwd(catalogDestDir)
                        catalogFTP.set_pasv(False)
                        ftpFile = open(os.path.join(tempDir,catName),'rb')
                        catalogFTP.storbinary('STOR '+catName,ftpFile)
                        ftpFile.close()
                        os.remove(tempDir+'/'+catName)
                        
catalogFTP.quit()
