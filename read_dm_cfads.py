#!/usr/bin/python3

import os
import numpy as np
import netCDF4 as nc

indir = '/home/disk/bob/gpm/nam_ku/classify/class_data_v07/stats_class_v12s/Cfad_Dm/06'
type = 'Dm'
#indir = '/home/disk/bob/gpm/nam_ku/classify/class_data_v07/stats_class_v12s/Cfad/06'
#type = 'refl'

for file in os.listdir(indir):
    if file.endswith('nc'):
        if 'Stra' in file or 'Shallow' in file:
            print('file = {}'.format(file))
            with nc.Dataset(indir+'/'+file,'r') as ncid:
                numBad = 0
                #ncid.dimensions['Dm_CFAD']
                if type == 'Dm':
                    bin_vals = ncid['Dm'][:]
                elif type == 'refl':
                    bin_vals = ncid['refl'][:]
                nbin_vals = len(bin_vals)
                alt_vals = ncid['altitude'][:]
                nalt_vals = len(alt_vals)
                if type == 'Dm':
                    full = ncid['Dm_CFAD_Full'][:,:]
                    core = ncid['Dm_CFAD_Core'][:,:]
                elif type == 'refl':
                    full = ncid['CFAD_Full'][:,:]
                    core = ncid['CFAD_Core'][:,:]                    
                #np.amax(full[134:176,:])
                for ilevel in range(0,nalt_vals):
                    if np.amax(full[ilevel,:]) > 0:
                        #print('ilevel = {} and alt = {}'.format(ilevel,alt_vals[ilevel]))
                        full_list = list(full[ilevel,:])
                        core_list = list(core[ilevel,:])
                        for ibin in range(0,nbin_vals):
                            #if full_list[ibin] > 0:
                            #print('ibin = {} and Dm = {:.2f}'.format(ibin,bin_vals[ibin]))
                            diff = full_list[ibin] - core_list[ibin]
                            if diff < 0:
                                #print('higher core count than full count')
                                #print('   ilevel = {} and alt = {}'.format(ilevel,alt_vals[ilevel]))
                                #print('   ibin = {} and Dm = {:.2f}'.format(ibin,bin_vals[ibin]))
                                #print('   coreVal = {} and fullVal = {}'.format(core_list[ibin],full_list[ibin]))
                                numBad = numBad + 1
                print('   numBad = {}'.format(numBad))
                print('   total core count = {}'.format(np.sum(core)))
                print('   total full count = {}'.format(np.sum(full)))

        elif 'Conv' in file:
            print('file = {}'.format(file))
            with nc.Dataset(indir+'/'+file,'r') as ncid:
                #ncid.dimensions['Dm_CFAD']
                if type == 'Dm':
                    bin_vals = ncid['Dm'][:]
                elif type == 'refl':
                    bin_vals = ncid['refl'][:]
                nbin_vals = len(bin_vals)
                alt_vals = ncid['altitude'][:]
                nalt_vals = len(alt_vals)
                if type == 'Dm':
                    full = ncid['Dm_CFAD_Full'][:,:,:]
                    core = ncid['Dm_CFAD_Core'][:,:,:]
                elif type == 'refl':
                    full = ncid['CFAD_Full'][:,:,:]
                    core = ncid['CFAD_Core'][:,:,:]                    
                for iconv in range(0,3):
                    numBad = 0
                    if iconv == 0:
                        print('   Deep Convective')
                    elif iconv == 1:
                        print('   Wide Convective')
                    elif iconv == 2:
                        print('   Deep and Wide Convective')
                    for ilevel in range(0,nalt_vals):
                        if np.amax(full[iconv,ilevel,:]) > 0:
                            #print('ilevel = {} and alt = {}'.format(ilevel,alt_vals[ilevel]))
                            full_list = list(full[iconv,ilevel,:])
                            core_list = list(core[iconv,ilevel,:])
                            for ibin in range(0,nbin_vals):
                                #if full_list[ibin] > 0:
                                #print('ibin = {} and Dm = {:.2f}'.format(ibin,bin_vals[ibin]))
                                diff = full_list[ibin] - core_list[ibin]
                                if diff < 0:
                                    #print('higher core count than full count')
                                    #print('   ilevel = {} and alt = {}'.format(ilevel,alt_vals[ilevel]))
                                    #print('   ibin = {} and Dm = {:.2f}'.format(ibin,bin_vals[ibin]))
                                    #print('   coreVal = {} and fullVal = {}'.format(core_list[ibin],full_list[ibin]))
                                    numBad = numBad + 1
                    print('   numBad = {}'.format(numBad))
                    print('   total core count = {}'.format( sum(sum(core[iconv,:,:]))) )
                    print('   total full count = {}'.format( sum(sum(full[iconv,:,:]))) )
