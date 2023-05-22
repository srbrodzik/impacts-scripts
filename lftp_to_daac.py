#!/usr/bin/python3

import os

inDirBase = '/home/disk/bob/impacts/netcdf/mrms/2DBaseRefl'

dates = ['20220114','20220115','20220116','20220117','20220118','20220119','20220120',
         '20220121','20220122','20220123','20220124','20220125',
         '20220126','20220127','20220128','20220129','20220130',
         '20220131',
         '20220201','20220202','20220203','20220204','20220205',
         '20220206','20220207','20220208','20220209','20220210',
         '20220211','20220212','20220213','20220214','20220215',
         '20220216','20220217','20220218','20220219','20220220',
         '20220221','20220222','20220223','20220224','20220225',
         '20220226']

#for date in os.listdir(inDirBase):
for date in dates:
    inDir = inDirBase+'/'+date
    if os.path.isdir(inDir):
        print(date)
        os.chdir(inDir)
        #command = 'lftp -c "open ftp://impacts:snowfallATLANTIC2020\!@ghrc.nsstc.nasa.gov; mirror -R"'
        command = 'lftp -c "open ftp://impacts:snowfallATLANTIC2020\!@ghrc.nsstc.nasa.gov; cd MRMS; cd BaseDBZ; mirror -R"'
        os.system(command)
