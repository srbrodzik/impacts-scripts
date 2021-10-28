import sys
import os
import datetime
import shutil

numargs = len(sys.argv) - 1
print("numargs = %d" % (numargs))
if numargs != 3:
    print("Useage: %s [start(YYYYMMDDHHMM)] [end(YYYYMMDDHHMM)] [sector(1 or 2)]" % (sys.argv[0]))
    exit()
else:
    print("You are good to go")
    
start = sys.argv[1]
startObj = datetime.datetime.strptime(start,'%Y%m%d%H%M%S')
startUnix = int(startObj.strftime("%s"))
startDate = startObj.strftime("%Y%m%d")
end = sys.argv[2]
endObj = datetime.datetime.strptime(end,'%Y%m%d%H%M%S')
endUnix = int(endObj.strftime("%s"))
endDate = endObj.strftime("%Y%m%d")
sector = sys.argv[3]    
print("startUnix = %s, endUnix = %s, sector = %s" % (startUnix,endUnix,sector))

base_in_dir = '/home/disk/data/satellite/GOES/GRB16/ABI/Mesoscale-'+sector
base_save_dir = '/home/disk/bob/impacts/goes-meso/Mesoscale-'+sector
channels = ['Channel01','Channel13']
prefix = 'OR_ABI-L1b-RadM'

for ichan in range(0,len(channels)):
    indir = base_in_dir+'/'+channels[ichan]
    outdir = base_save_dir+'/'+channels[ichan]
    print ("ichan = %d and indir = %s and outdir = %s" % (ichan,indir,outdir))
    dirlist = os.listdir(indir)
    for dir in dirlist:
        if dir.startswith('2019'):
            dirDate = dir
            dirDateObj = datetime.datetime.strptime(dir,'%Y%m%d')
            dirDateUnix = int(dirDateObj.strftime("%s"))
            if dirDate >= startDate and dirDate <= endDate:
                if not os.path.isdir(outdir+'/'+dirDate):
                    os.mkdir(outdir+'/'+dirDate)
                os.chdir(indir+'/'+dirDate)
                filelist = os.listdir('.')
                for file in filelist:
                    if file.startswith(prefix):
                        parts = file.split('_')
                        for part in parts:
                            if part.startswith('s'):
                                fileDateTime = part[1:-1]  # format sYYYYJJJHHMMSSs
                                fileDateTimeObj = datetime.datetime.strptime(fileDateTime,'%Y%j%H%M%S')
                                fileDateTimeUnix = int(fileDateTimeObj.strftime("%s"))
                                if fileDateTimeUnix >= startUnix and  fileDateTimeUnix <= endUnix:
                                    shutil.copy(file,outdir+'/'+dirDate)
                                
                        
    
