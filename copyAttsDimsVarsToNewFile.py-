#!/usr/bin/python3

import netCDF4 as nc
import numpy as np
refl_val_prefix = 'ConusMergedReflectivityQC'

def copyAttsDimsVarsToNewFile(inFile,outFile,nalts,refl_name):
    with nc.Dataset(inFile) as src, nc.Dataset(outFile, "w") as dst:
        # copy global attributes
        for name in src.ncattrs():
            dst.setncattr(name, src.getncattr(name))

        # create new dimension 'altitude'
        dst.createDimension('altitude',nalts)

        # copy rest of dimensions from src
        for dim_name, dim_value in src.dimensions.items():
            print(dim_name, len(dim_value))
            dst.createDimension(dim_name, len(dim_value) if not dim_value.isunlimited() else None)

        # copy all variables except reflectivity
        for var_name, varin in src.variables.items():
            if not var_name.startswith(refl_val_prefix):
                fill_value = None
                if hasattr(varin,'_FillValue'):
                    fill_value = varin._FillValue
                outVar = dst.createVariable(var_name,varin.datatype,
                                            varin.dimensions,fill_value=fill_value)
                print(varin.datatype)
                print(varin.ncattrs())
                outVar.setncatts({k: varin.getncattr(k) for k in varin.ncattrs() if k not in ['_FillValue']})
                outVar[:] = varin[:]
            else:
                #refl_var_name = var_name
                #[refl_var_name_merge,junk] = refl_var_name.split('_')
                #refl_var_name_merge = 'DBZ_QC'
                refl_varin = varin

        # create new reflectivity variable
        # fill value should be 9.999e+20f but it's actually -999
        #fill_value = None
        #if hasattr(refl_varin,'_FillValue'):
        #    fill_value = refl_varin._FillValue
        fill_value = -999.
        outVar = dst.createVariable(refl_name,refl_varin.datatype,
                                    ('time','altitude','latitude','longitude'),
                                    fill_value=fill_value,zlib=True)
        [shortname,junk] = (refl_varin.short_name).split('_')
        outVar.short_name = shortname
        outVar.long_name = refl_varin.long_name
        outVar.units = refl_varin.units

        
        
        
