#!/usr/bin/env python3

import json
import xarray as xr

mwr = None
lidar = None
with open("PROF_ALBA.json", "r") as f:
    data = json.load(f)
    try:
        mwr = data['mwr']
        mwr = xr.Dataset.from_dict(mwr)
        mwr = xr.decode_cf(mwr)
    except:
        print("Problem reading microwave radiometer data")

    try:
        lidar = data['lidar']
        lidar = xr.Dataset.from_dict(lidar)
        lidar = xr.decode_cf(lidar)
    except:
        print("Problem reading lidar data")

# Select a particular time and convert to a pandas dataframe for display
print(lidar.sel(time='2019-06-19T14:40:00').to_dataframe())

for col in ['range', 'pressure_level', 'velocity', 'direction']:
  print("Units for {} are {}".format(col, lidar[col].attrs['units']))
