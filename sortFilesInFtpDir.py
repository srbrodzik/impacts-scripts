import os
import sys
import shutil

ftpDir = '/home/disk/ftp/brodzik/incoming'
webserverDir = '/home/disk/funnel/impacts/archive'

for file in os.listdir(ftpDir):
    if os.path.isfile(ftpDir+'/'+file):
        cmd = 'chmod a+rw '+ftpDir+'/'+file
        os.system(cmd)
        try:
            (prefix,date,junk,suffix) = file.split('.')
            if prefix == 'wxbriefing':
                if not os.path.exists(webserverDir+'/forecast/'+date):
                    os.mkdir(webserverDir+'/forecast/'+date)
                shutil.move(ftpDir+'/'+file,webserverDir+'/forecast/'+date+'/'+file)
            elif prefix == 'wxbriefing_update':
                if not os.path.exists(webserverDir+'/forecast/'+date):
                    os.mkdir(webserverDir+'/forecast/'+date)
                shutil.move(ftpDir+'/'+file,webserverDir+'/forecast/'+date+'/'+file)
            elif prefix == 'flt_plan':
                if not os.path.exists(webserverDir+'/forecast/'+date):
                    os.mkdir(webserverDir+'/forecast/'+date)
                shutil.move(ftpDir+'/'+file,webserverDir+'/forecast/'+date+'/'+file)
            elif prefix == 'summary':
                if not os.path.exists(webserverDir+'/forecast/'+date):
                    os.mkdir(webserverDir+'/forecast/'+date)
                shutil.move(ftpDir+'/'+file,webserverDir+'/forecast/'+date+'/'+file)
            else:
                print 'file = '+file+' has unexpected name -- move to junk'
                if not os.path.exists(ftpDir+'/junk'):
                    os.mkdir(ftpDir+'/junk')
                shutil.move(ftpDir+'/'+file,ftpDir+'/junk')
        except ValueError:
            if not os.path.exists(ftpDir+'/junk'):
                os.mkdir(ftpDir+'/junk')
            shutil.move(ftpDir+'/'+file,ftpDir+'/junk'+'/'+file)
            continue
        

# Check wx_briefing/update files
#for file in os.listdir(ftpDir+'/wx_briefing'):
#    try:
#        (prefix,date,junk,suffix) = file.split('.')
#        if prefix == 'wxbriefing':
#            if not os.path.exists(webserverDir+'/forecast/'+date):
#                os.mkdir(webserverDir+'/forecast/'+date)
#            shutil.move(ftpDir+'/wx_briefing/'+file,webserverDir+'/forecast/'+date)
#        elif prefix == 'wxbriefing_update':
#            if not os.path.exists(webserverDir+'/forecast/'+date):
#                os.mkdir(webserverDir+'/forecast/'+date)
#            shutil.move(ftpDir+'/wx_briefing/'+file,webserverDir+'/forecast/'+date)
#        else:
#            print 'file = '+file+' has unexpected name -- move to junk'
#            if not os.path.exists(ftpDir+'/wx_briefing/junk'):
#                os.mkdir(ftpDir+'/wx_briefing/junk')
#            shutil.move(ftpDir+'/wx_briefing/'+file,ftpDir+'/wx_briefing/junk')
#    except ValueError:
#        if not os.path.exists(ftpDir+'/wx_briefing/junk'):
#            os.mkdir(ftpDir+'/wx_briefing/junk')
#        shutil.move(ftpDir+'/wx_briefing/'+file,ftpDir+'/wx_briefing/junk')
#        continue

# Check flt_plan/summary files
#for file in os.listdir(ftpDir+'/flt_plan'):
#    try:
#        (prefix,date,junk,suffix) = file.split('.')
#        if prefix == 'flt_plan':
#            if not os.path.exists(webserverDir+'/forecast/'+date):
#                os.mkdir(webserverDir+'/forecast/'+date)
#            shutil.move(ftpDir+'/flt_plan/'+file,webserverDir+'/forecast/'+date)
#        elif prefix == 'summary':
#            if not os.path.exists(webserverDir+'/forecast/'+date):
#                os.mkdir(webserverDir+'/forecast/'+date)
#            shutil.move(ftpDir+'/flt_plan/'+file,webserverDir+'/forecast/'+date)
#        else:
#            print 'file = '+file+' has unexpected name -- move to junk'
#            if not os.path.exists(ftpDir+'/flt_plan/junk'):
#                os.mkdir(ftpDir+'/flt_plan/junk')
#            shutil.move(ftpDir+'/flt_plan/'+file,ftpDir+'/flt_plan/junk')
#    except ValueError:
#        if not os.path.exists(ftpDir+'/flt_plan/junk'):
#            os.mkdir(ftpDir+'/flt_plan/junk')
#        shutil.move(ftpDir+'/flt_plan/'+file,ftpDir+'/flt_plan/junk')
#        continue

