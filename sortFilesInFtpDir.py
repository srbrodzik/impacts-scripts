import os
import sys
import shutil

ftpDir = '/home/disk/ftp/brodzik/incoming'
webserverDir = '/home/disk/funnel/impacts/archive'

for file in os.listdir(ftpDir):
    if os.path.isfile(ftpDir+'/'+file):
        cmd = 'chmod a+rw '+ftpDir+'/'+file
        os.system(cmd)
        if file.endswith('pdf') or file.endswith('xlsx'):
            try:
                (prefix,product,date,category,suffix) = file.split('.')
                yyyymmdd = date[0:9]
                if not os.path.exists(webserverDir+'/'+prefix+'/'+product+'/'+yyyymmdd):
                    os.makedirs(webserverDir+'/'+prefix+'/'+product+'/'+yyyymmdd)
                    shutil.move(ftpDir+'/'+file,webserverDir+'/'+prefix+'/'+product+'/'+yyyymmdd+'/'+file)
            except ValueError:
                if not os.path.exists(ftpDir+'/junk'):
                    os.mkdir(ftpDir+'/junk')
                shutil.move(ftpDir+'/'+file,ftpDir+'/junk'+'/'+file)
                continue
        

