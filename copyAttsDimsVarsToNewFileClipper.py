#!/usr/bin/python3

import netCDF4 as nc
import numpy as np

def copyAttsDimsVarsToNewFileClipper(inFile,outFile,nalts,
                                     var_name_in,var_name_out,
                                     long_name,units,altArr,
                                     missing):

    with nc.Dataset(inFile) as src, nc.Dataset(outFile, "w") as dst:
        # copy global attributes
        for name in src.ncattrs():
            if name != 'Height' and name != 'SubType-value':
                dst.setncattr(name, src.getncattr(name))
            if name == 'MissingData':
                missing_data = src.getncattr(name)
            elif name == 'Time':
                timeArr = [src.getncattr(name)]
            elif name == 'Latitude':
                lat_ul = src.getncattr(name)
            elif name == 'Longitude':
                lon_ul = src.getncattr(name)
            elif name == 'LatGridSpacing':
                lat_res = src.getncattr(name)
            elif name == 'LonGridSpacing':
                lon_res = src.getncattr(name)

        # create new dimension 'time' and variable 'time'
        dst.createDimension('time',None)
        timeVar = dst.createVariable('time','float64',('time'))
        timeVar.units = 'seconds since 1970-01-01T00:00:00Z'
        timeVar.long_name = 'Data time'
        dst['time'][:] = timeArr

        # create new dimension 'altitude' and variable 'altitude'
        dst.createDimension('altitude',nalts)
        altVar = dst.createVariable('altitude','float32',('altitude'))
        altVar.units = 'km'
        altVar.long_name = 'altitude'
        dst['altitude'][:] = altArr

        # copy rest of dimensions from src
        for dimName, dimValue in src.dimensions.items():
            print(dimName, len(dimValue))
            if dimName == 'Lat':
                nlat = len(dimValue)
                dst.createDimension('latitude', len(dimValue) if not dimValue.isunlimited() else None)
            elif dimName == 'Lon':
                nlon = len(dimValue)
                dst.createDimension('longitude', len(dimValue) if not dimValue.isunlimited() else None)

        # copy all variables except var_name_in
        for varName, varIn in src.variables.items():
            if not varName.startswith(var_name_in):
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
                reflVarIn = varIn

        # create new latitude variable and fill
        lat_lr = lat_ul - (nlat * lat_res)
        #lat_vals = np.arange(lat_lr,lat_ul,lat_res)
        lat_vals = np.arange(lat_ul,lat_lr,-lat_res)
        outVar = dst.createVariable('latitude','float32',('latitude'))
        outVar.long_name = 'latitude'
        outVar.units = 'degrees_north'
        dst['latitude'][:] = lat_vals 

        # create new longitude variable and fill
        lon_lr = lon_ul + (nlon * lon_res)
        lon_vals = np.arange(lon_ul,lon_lr,lon_res)
        outVar = dst.createVariable('longitude','float32',('longitude'))
        outVar.long_name = 'longitude'
        outVar.units = 'degrees_east'
        dst['longitude'][:] = lon_vals 

        # create new reflectivity variable
        fill_value = missing
        outVar = dst.createVariable(var_name_out,reflVarIn.datatype,
                                    ('time','altitude','latitude','longitude'),
                                    fill_value=fill_value,zlib=True)
        outVar.short_name = var_name_out
        outVar.long_name = long_name
        outVar.units = units

        return missing_data
