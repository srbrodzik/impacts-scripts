import os
import shutil

indir = '/home/disk/bob/impacts/sat'
outdir = '/home/disk/funnel/impacts-website/archive/ops/goes_east'
prefix = 'ops.goes_east'

for file in os.listdir(indir):

    if file.endswith('gif'):

        print 'file = ',file
    
        (base,ext) = file.split('.')
        (time,band) = base.split('_')
        ymd = time[0:8]

        if band == 'ir':
            suffix = 'ir_ch14'
        elif band == 'vis':
            suffix = 'vis_ch02'
        elif band == 'wv':
            suffix = 'wv_ch08'

        file_new = prefix+'.'+time+'.'+suffix+'.'+ext

        if not os.path.isdir(outdir+'/'+ymd):
            os.mkdir(outdir+'/'+ymd)
    
        shutil.copy(indir+'/'+file,outdir+'/'+ymd+'/'+file_new)
    

    
        
    
