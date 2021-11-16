#!/usr/bin/python3

import netCDF4 as nc
import numpy as np
reflValPrefix = 'ConusMergedReflectivityQC'

def copyAttsDimsVarsToNewFile(inFile,outFile,nalts,reflName,altArr):
    with nc.Dataset(inFile) as src, nc.Dataset(outFile, "w") as dst:
        # copy global attributes
        for name in src.ncattrs():
            dst.setncattr(name, src.getncattr(name))

        # create new dimension 'altitude' and variable 'altitude'
        dst.createDimension('altitude',nalts)
        altVar = dst.createVariable('altitude','float32',('altitude'))
        altVar.units = 'km'
        altVar.long_name = 'altitude'
        dst['altitude'][:] = altArr

        # copy rest of dimensions from src
        for dimName, dimValue in src.dimensions.items():
            print(dimName, len(dimValue))
            dst.createDimension(dimName, len(dimValue) if not dimValue.isunlimited() else None)

        # copy all variables except reflectivity
        for varName, varIn in src.variables.items():
            if not varName.startswith(reflValPrefix):
                fill_value = None
                if hasattr(varIn,'_FillValue'):
                    fill_value = varIn._FillValue
                outVar = dst.createVariable(varName,varIn.datatype,
                                            varIn.dimensions,fill_value=fill_value)
                print(varIn.datatype)
                print(varIn.ncattrs())
                outVar.setncatts({k: varIn.getncattr(k) for k in varIn.ncattrs() if k not in ['_FillValue']})
                outVar[:] = varIn[:]
            else:
                #reflVarName = varName
                #[reflVarNameMerge,junk] = reflVarName.split('_')
                #reflVarNameMerge = 'DBZ_QC'
                reflVarIn = varIn

        # create new reflectivity variable
        # fill_value should be 9.999e+20f but it's actually -999
        #fill_value = None
        #if hasattr(reflVarIn,'_FillValue'):
        #    fill_value = reflVarIn._FillValue
        fill_value = -999.
        outVar = dst.createVariable(reflName,reflVarIn.datatype,
                                    ('time','altitude','latitude','longitude'),
                                    fill_value=fill_value,zlib=True)
        [short_name,junk] = (reflVarIn.short_name).split('_')
        outVar.short_name = short_name
        outVar.long_name = reflVarIn.long_name
        outVar.units = reflVarIn.units

        
        
        
