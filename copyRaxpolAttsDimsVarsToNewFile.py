#!/usr/bin/python3

import netCDF4 as nc
import numpy as np

def copyRaxpolAttsDimsVarsToNewFile(inFile,outFile,excludedAttrs,fields,field,firstFile):
    if firstFile:
        with nc.Dataset(inFile) as src, nc.Dataset(outFile, "w") as dst:
            # copy global attributes
            for name in src.ncattrs():
                #print(name)
                if name == 'MissingData':
                    fillValue = src.getncattr(name)
                if name not in excludedAttrs:
                    dst.setncattr(name, src.getncattr(name))

            # copy dimensions from src
            for dimName, dimValue in src.dimensions.items():
                #print(dimName, len(dimValue))
                dst.createDimension(dimName, len(dimValue) if not dimValue.isunlimited() else None)

            # copy variables
            for varName, varIn in src.variables.items():
                #print(varName)
                #print(varIn)
                fill_value = fillValue
                if hasattr(varIn,'_FillValue'):
                    fill_value = varIn._FillValue
                if varName == fields[field]['inName']:
                    outVar = dst.createVariable(fields[field]['outName'],varIn.datatype,
                                                varIn.dimensions,fill_value=fill_value)
                else:
                    outVar = dst.createVariable(varName,varIn.datatype,
                                                varIn.dimensions,fill_value=fill_value)
                #print(varIn.datatype)
                #print(varIn.ncattrs())
                outVar.setncatts({k: varIn.getncattr(k) for k in varIn.ncattrs() if k not in ['_FillValue']})
                outVar[:] = varIn[:]

    else:
        with nc.Dataset(inFile) as src, nc.Dataset(outFile, "a") as dst:
            # get MissingData global attribute
            for name in src.ncattrs():
                #print(name)
                if name == 'MissingData':
                    fillValue = src.getncattr(name)
            # copy only polarimetric variable
            for varName, varIn in src.variables.items():
                #print(varName)
                #print(fields[field]['inName'])
                if varName == fields[field]['inName']:
                    fill_value = fillValue
                    if hasattr(varIn,'_FillValue'):
                        fill_value = varIn._FillValue
                    outVar = dst.createVariable(fields[field]['outName'],varIn.datatype,
                                            varIn.dimensions,fill_value=fill_value)
                    #print(varIn.datatype)
                    #print(varIn.ncattrs())
                    outVar.setncatts({k: varIn.getncattr(k) for k in varIn.ncattrs() if k not in ['_FillValue']})
                    outVar[:] = varIn[:]
            

        
        
        
