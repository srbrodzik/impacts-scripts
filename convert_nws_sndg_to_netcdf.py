#!/usr/bin/python

# File naming convention for NWS sounding netcdf files:
# IMPACTS_sounding_<start date>_<start time>_<site name>.nc

import os
import sys
from datetime import datetime
import pandas as pd
import xarray
from netCDF4 import Dataset

def is_number(str):
    try:
        float(str)
        return True
    except ValueError:
        return False

def read_var_vals(line,missing_value):
    try:
        pres = float(line[0:7])
    except:
        pres = missing_value
                            
    try:
        hght = float(line[7:14])
    except:
        hght = missing_value
                            
    try:
        temp = float(line[14:21])
    except:
        temp = missing_value
                            
    try:
        dwpt = float(line[21:28])
    except:
        dwpt = missing_value

    try:
        relh = float(line[28:35])
    except:
        relh = missing_value

    try:
        mixr = float(line[35:42])
    except:
        mixr = missing_value

    try:
        drct = float(line[42:49])
    except:
        drct = missing_value

    try:
        sknt = float(line[49:56])
    except:
        sknt = missing_value

    try:
        thta = float(line[56:63])
    except:
        thta = missing_value

    try:
        thte = float(line[63:70])
    except:
        thte = missing_value

    try:
        thtv = float(line[70:77])
    except:
        thtv = missing_value

    return pres,hght,temp,dwpt,relh,mixr,drct,sknt,thta,thte,thtv

#inDirBase = '/home/snowband/impacts/Downloads/sounding'
inDirBase = '/home/disk/funnel/impacts-website/archive/ops/text_sounding'
#outDirBase = inDirBase
outDirBase = '/home/disk/funnel/impacts-website/archive/ops/sounding'
#bindir = '/home/snowband/brodzik/bin'
bindir = '/home/disk/bob/impacts/bin'
missing_value = -999
nc_prefix = 'IMPACTS_sounding'

for date in os.listdir(inDirBase):
    if os.path.isdir(inDirBase+'/'+date):
        inDir = inDirBase+'/'+date
        outDir = outDirBase+'/'+date
        if not os.path.exists(outDir):
            os.makedirs(outDir)
        
        for file in os.listdir(inDir):
            if file.endswith('html'):

                print >>sys.stdout, 'Input file = ', file
        
                # Create textFile and ncFile names
                (base,ext) = os.path.splitext(file)
                (prefix1,prefix2,dtStr,site) = base.split('.')
                dtObj = datetime.strptime(dtStr,'%Y%m%d%H%M%S')
                date = dtObj.strftime('%Y%m%d')
                time = dtObj.strftime('%H%M%S')
                textFile = inDir+'/'+base+'.txt'
                ncFile = outDir+'/'+nc_prefix+'_'+date+'_'+time+'_'+site+'.nc'
        
                # Remove html tags from file
                command = bindir+'/removeHtmlTags.csh '+inDir+'/'+file+' '+textFile
                os.system(command)

                # Create empty attribute dict and dataFrame
                attributes = {}
                df = pd.DataFrame(columns=['pres','hght','temp','dwpt','relh','mixr',
                                           'drct','sknt','thta','thte','thtv'])
        
                # Read in textFile
                with open(textFile,'r') as f:

                    # Skip first 19 lines
                    for i in range(0,18):
                        header = f.readline()

                    # Read in remainder of file
                    for line in f:
                        #line = line.strip()
                        line_tmp = line.strip()
                        if len(line_tmp) > 0:
                    
                            if ':' in line and 'http' not in line:
                                # Read attr name and value
                                (attrName,attrVal) = line_tmp.split(':')
                                attrName = attrName.replace(' ','_')
                                attrName = attrName.replace('[','')
                                attrName = attrName.replace(']','')

                                # If possible, convert attrVal string to a float
                                try:
                                    attributes[attrName] = float(attrVal)
                                except:
                                    attributes[attrName] = attrVal
                            
                            elif is_number(line[0:7]):
                                # Read var vals
                                (pres,hght,temp,dwpt,relh,mixr,drct,sknt,thta,thte,thtv) = read_var_vals(line,missing_value)
                                
                                # Add vals to dataframe
                                df = df.append({'pres':pres,'hght':hght,'temp':temp,'dwpt':dwpt,
                                                'relh':relh,'mixr':mixr,'drct':drct,'sknt':sknt,
                                                'thta':thta,'thte':thte,'thtv':thtv}, ignore_index=True)
                
                # Remove textFile
                os.remove(textFile)
                        
                # Create xarray and assign var and global attributes
                xr = xarray.Dataset.from_dataframe(df)
                xr['pres'].attrs={'units':'hPa', 'long_name':'atmospheric_pressure'}
                xr['hght'].attrs={'units':'meter', 'long_name':'geopotential_height'}
                xr['temp'].attrs={'units':'degC', 'long_name':'temperature'}
                xr['dwpt'].attrs={'units':'degC', 'long_name':'dewpoint_temperature'}
                xr['relh'].attrs={'units':'%', 'long_name':'relative_humidity'}
                xr['mixr'].attrs={'units':'g/kg', 'long_name':'mixing_ratio'}
                xr['drct'].attrs={'units':'deg', 'long_name':'wind_direction'}
                xr['sknt'].attrs={'units':'knot', 'long_name':'wind_speed'}
                xr['thta'].attrs={'units':'degK', 'long_name':'potential_temperature'}
                xr['thte'].attrs={'units':'degK', 'long_name':'equivalent_potential_temperature'}
                xr['thtv'].attrs={'units':'degK', 'long_name':'virtual_potential_temperature'}
                xr.attrs = attributes

                # Convert xarray to netcdf
                encoding = {
                    'pres': {'_FillValue':missing_value},
                    'hght': {'_FillValue':missing_value},
                    'temp': {'_FillValue':missing_value},
                    'dwpt': {'_FillValue':missing_value},
                    'relh': {'_FillValue':missing_value},
                    'mixr': {'_FillValue':missing_value},
                    'drct': {'_FillValue':missing_value},
                    'sknt': {'_FillValue':missing_value},
                    'thta': {'_FillValue':missing_value},
                    'thte': {'_FillValue':missing_value},
                    'thtv': {'_FillValue':missing_value}
                }
                xr.to_netcdf(ncFile,encoding=encoding)
