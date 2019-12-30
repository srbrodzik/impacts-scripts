import time
import datetime
import os
import shutil

infile = '/home/disk/funnel/impacts-website/precip_map/IMPACTS_map.png'
outdir = '/home/disk/funnel/impacts-website/archive/ops/totals'
prefix = 'ops.totals'
suffix = 'precip24.png'

# Get current date
now = datetime.datetime.utcnow()
nowDateStr = now.strftime("%Y%m%d")

# Create new filename
outfile = prefix+'.'+nowDateStr+'0000.'+suffix

# Copy 24 hour accumulation map to outdir
if not os.path.exists(outdir+'/'+nowDateStr):
    os.mkdir(outdir+'/'+nowDateStr)
shutil.copy(infile,outdir+'/'+nowDateStr+'/'+outfile)
